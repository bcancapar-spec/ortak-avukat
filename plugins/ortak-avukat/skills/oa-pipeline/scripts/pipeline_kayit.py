#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
pipeline_kayit.py — oa-pipeline DEFTERİ (append-only JSONL olay defteri)

Fiziksel işletim protokolünün garantörü: bir parçanın statüsü ancak KANITLA
yazılabilir. Model 'çalıştırdım' diyemez; defter kanıt ister. Boşluklu tur
teslim edilemez (--denetle hata koduyla döner).

EŞZAMANLI (PARALEL ALT-AJAN) GÜVENLİK
-------------------------------------
Gerçeğin kaynağı append-only bir olay defteridir: `_oa/defter/pipeline-olaylar.jsonl`.
Her --isle / --katman çağrısı bu dosyaya TEK satırlık bir olay EKLER (atomik
O_APPEND + en iyi çaba dosya kilidi). Hiçbir çağrı dosyayı oku-değiştir-yaz
yapmaz; yalnızca kendi satırını ekler. Böylece iki alt-ajan aynı anda FARKLI
adımı işlerse ikisinin de olayı diskte kalır — eski tasarımdaki "son yazan
kazanır / diğerinin statüsü sessizce silinir" veri kaybı yapısal olarak biter.

Durum (--goster / --denetle) bu olaylardan DERLENİR. `pipeline-durum.json`
yalnızca TÜREV / OKUNUR bir görünümdür (atomik replace ile tazelenir; jsonl'den
her an yeniden üretilebilir — oa_metrik.py bu görünümü okur). Eski (jsonl'den
önceki) `pipeline-durum.json` varsa ilk okumada olaylara MIGRATE edilir.

Kullanım:
  python pipeline_kayit.py --baslat "Dosya adı" [--ceza mudafii|musteki] [--kok KLASÖR]
  python pipeline_kayit.py --isle --adim 3 --parca oa-ictihat --durum UYGULANDI \
      --kanit "Skill çağrısı yapıldı; ictihat_ara 'istihkak muvazaa' 12.HD → 3 künye teyitli"
  python pipeline_kayit.py --isle --adim 5 --parca oa-kiyas --durum GEREKSIZ --gerekce "..."
  python pipeline_kayit.py --katman oa-gizlilik --durum UYGULANDI --kanit "gizlilik_tara.py 2 çağrıda ALLOW"
  python pipeline_kayit.py --goster [--kok KLASÖR]
  python pipeline_kayit.py --denetle [--kok KLASÖR]        # teslim öncesi; boşluk varsa exit 1

--kok: çalışma kökü (tam_tur.py / oa_metrik.py ile simetri). Verilirse defter
<KLASÖR>/_oa/defter altındadır; verilmezse mevcut davranış (CWD/_oa). Claude Code
alt-ajan thread'lerinde cwd sıfırlandığından, mutlak --kok ile çağrı yanlış yerde
hayalet _oa oluşmasını önler. (Geriye uyum için --yol da desteklenir.)

Statüler: UYGULANDI (kanıt zorunlu) · GEREKSIZ (gerekçe zorunlu) ·
          BILGI-EKSIK (eksik tanımı zorunlu) · YUKLENEMEDI (açıklama zorunlu)
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, json, os, sys, datetime

# Gerçeğin kaynağı (append-only) ve türev görünüm — aynı 'defter' klasöründe yaşar.
OLAYLAR_ADI = "pipeline-olaylar.jsonl"   # append-only olay defteri (SOURCE OF TRUTH)
DURUM_ADI   = "pipeline-durum.json"      # türev/okunur görünüm (oa_metrik.py bunu okur)

ADIMLAR = {
    0:  ("MANİFEST",   ["manifest"]),
    1:  ("ALIM",       ["oa-interview", "oa-illiyet", "oa-sure"]),
    2:  ("KONUMLAMA",  ["oa-alan"]),
    3:  ("ARAŞTIRMA",  ["oa-ictihat"]),
    4:  ("OLGU/DELİL", ["oa-vakia"]),
    5:  ("KIYAS",      ["oa-kiyas"]),
    6:  ("STRATEJİ",   ["oa-strateji"]),
    7:  ("ANTİTEZ",    ["oa-antitez"]),
    8:  ("YAZIM",      ["oa-dilekce"]),
    9:  ("KONTROL",    ["oa-kontrol"]),
    10: ("KAPANIŞ",    ["oa-usta"]),
}
KATMANLAR = ["oa-usul", "oa-illiyet", "oa-gizlilik"]
SCRIPTLI = {"oa-sure", "oa-usul", "oa-vakia", "oa-antitez", "oa-kiyas",
            "oa-illiyet", "oa-gizlilik", "oa-sozlesme", "manifest"}
STATULER = {"UYGULANDI", "GEREKSIZ", "BILGI-EKSIK", "YUKLENEMEDI"}
MIN_KANIT = 20  # karakter — "yaptım" tek kelimesi kanıt değildir


def simdi():
    return datetime.datetime.now().isoformat(timespec="seconds")


# --- yol çözümleme (--kok / --yol) -------------------------------------------
def _yollar(args):
    """(olaylar_jsonl, durum_json) döndür. Öncelik: açık --yol (geriye uyum:
    doğrudan durum.json yolu; jsonl aynı klasörde). Yoksa --kok/_oa/defter."""
    if getattr(args, "yol", None):
        durum_yol = args.yol
        defter = os.path.dirname(durum_yol) or "."
    else:
        defter = os.path.normpath(os.path.join(getattr(args, "kok", None) or ".",
                                               "_oa", "defter"))
        durum_yol = os.path.join(defter, DURUM_ADI)
    olaylar_yol = os.path.join(defter, OLAYLAR_ADI)
    return olaylar_yol, durum_yol


# --- append-only olay defteri (atomik) ---------------------------------------
def olay_ekle(olaylar_yol, olay):
    """Tek satırlık olayı jsonl'e ATOMİK ekle. Dosya asla oku-değiştir-yaz
    edilmez; yalnız kendi satırımız eklenir → eşzamanlı yazımlarda kimsenin
    kaydı silinemez. Tek os.write (POSIX'te PIPE_BUF altı atomik) + en iyi çaba
    kilit (POSIX fcntl / Windows msvcrt) ile yazımlar serileştirilir."""
    ust = os.path.dirname(olaylar_yol)
    if ust:
        os.makedirs(ust, exist_ok=True)
    ham = (json.dumps(olay, ensure_ascii=False) + "\n").encode("utf-8")
    fd = os.open(olaylar_yol, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    kilit = None
    try:
        try:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX); kilit = "fcntl"
        except Exception:
            try:
                import msvcrt
                msvcrt.locking(fd, msvcrt.LK_LOCK, 1); kilit = "msvcrt"
            except Exception:
                kilit = None  # kilit yoksa tek-write atomikliğine güven
        os.write(fd, ham)
    finally:
        try:
            if kilit == "fcntl":
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_UN)
            elif kilit == "msvcrt":
                import msvcrt
                os.lseek(fd, 0, os.SEEK_SET)  # kilit 0. bayttaydı; oraya dön
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        except Exception:
            pass  # her hâlde os.close tüm kilitleri bırakır
        os.close(fd)


def olaylari_oku(olaylar_yol):
    """jsonl'i satır satır oku. Bozuk/yarım satır (çok nadir eşzamanlı yazımda)
    atlanır; kalan olaylar yine derlenir (dayanıklılık)."""
    olaylar = []
    if not (os.path.exists(olaylar_yol) and os.path.getsize(olaylar_yol) > 0):
        return olaylar
    with open(olaylar_yol, encoding="utf-8") as f:
        for satir in f:
            satir = satir.strip()
            if not satir:
                continue
            try:
                olaylar.append(json.loads(satir))
            except json.JSONDecodeError:
                continue
    return olaylar


# --- durum derleme (olaylardan) ----------------------------------------------
def _iskelet(dosya, olusturma, ceza_dali):
    d = {"dosya": dosya, "olusturma": olusturma, "ceza_dali": ceza_dali,
         "adimlar": {}, "katmanlar": {}, "gunluk": []}
    for no, (ad, parcalar) in ADIMLAR.items():
        d["adimlar"][str(no)] = {
            "ad": ad,
            "parcalar": {p: {"durum": "BEKLIYOR", "kanit": None, "zaman": None}
                         for p in parcalar},
        }
    katmanlar = list(KATMANLAR)
    if ceza_dali:
        katmanlar.append("oa-mudafii" if ceza_dali == "mudafii" else "oa-musteki-vekili")
    for k in katmanlar:
        d["katmanlar"][k] = {"durum": "BEKLIYOR", "kanit": None, "zaman": None}
    return d


def _uygula_adim(d, o):
    no = str(o.get("adim"))
    a = d["adimlar"].get(no)
    if a is None:
        try:
            ad = ADIMLAR[int(no)][0]
        except Exception:
            ad = f"ADIM-{no}"
        a = d["adimlar"][no] = {"ad": ad, "parcalar": {}}
    parca = o.get("parca")
    if parca not in a["parcalar"]:
        a["parcalar"][parca] = {"durum": "BEKLIYOR", "kanit": None, "zaman": None}
    a["parcalar"][parca].update({"durum": o.get("durum"), "kanit": o.get("kanit"),
                                 "zaman": o.get("zaman")})
    d["gunluk"].append({"zaman": o.get("zaman"), "adim": o.get("adim"),
                        "parca": parca, "durum": o.get("durum")})


def _uygula_katman(d, o):
    k = o.get("katman")
    if k not in d["katmanlar"]:
        d["katmanlar"][k] = {"durum": "BEKLIYOR", "kanit": None, "zaman": None}
    d["katmanlar"][k].update({"durum": o.get("durum"), "kanit": o.get("kanit"),
                              "zaman": o.get("zaman")})
    d["gunluk"].append({"zaman": o.get("zaman"), "katman": k, "durum": o.get("durum")})


def _migrasyon(olaylar_yol, durum_yol):
    """jsonl yoksa/boşsa ama eski (türev-öncesi) pipeline-durum.json varsa,
    durumu olaylara BİR KEZ taşı. jsonl doluysa hiçbir şey yapmaz."""
    if os.path.exists(olaylar_yol) and os.path.getsize(olaylar_yol) > 0:
        return
    if not os.path.exists(durum_yol):
        return
    try:
        eski = json.load(open(durum_yol, encoding="utf-8"))
    except Exception:
        return
    if not isinstance(eski, dict) or "adimlar" not in eski:
        return
    olay_ekle(olaylar_yol, {"zaman": eski.get("olusturma") or simdi(), "tip": "baslat",
                            "dosya": eski.get("dosya"), "ceza_dali": eski.get("ceza_dali"),
                            "migrasyon": True})
    for no in sorted(eski.get("adimlar", {}),
                     key=lambda x: int(x) if str(x).lstrip("-").isdigit() else 0):
        a = eski["adimlar"][no]
        for parca, p in (a.get("parcalar") or {}).items():
            if isinstance(p, dict) and p.get("durum") and p["durum"] != "BEKLIYOR":
                olay_ekle(olaylar_yol, {
                    "zaman": p.get("zaman") or simdi(), "tip": "adim",
                    "adim": int(no) if str(no).lstrip("-").isdigit() else no,
                    "parca": parca, "durum": p["durum"], "kanit": p.get("kanit"),
                    "migrasyon": True})
    for k, p in (eski.get("katmanlar") or {}).items():
        if isinstance(p, dict) and p.get("durum") and p["durum"] != "BEKLIYOR":
            olay_ekle(olaylar_yol, {
                "zaman": p.get("zaman") or simdi(), "tip": "katman",
                "katman": k, "durum": p["durum"], "kanit": p.get("kanit"),
                "migrasyon": True})


def derle(olaylar_yol, durum_yol=None):
    """Olay defterinden durumu DERLE (gerçeğin kaynağı jsonl). durum_yol
    verilirse önce eski görünüm migrate edilir. Defter yoksa None döner."""
    if durum_yol is not None:
        _migrasyon(olaylar_yol, durum_yol)
    olaylar = olaylari_oku(olaylar_yol)
    if not olaylar:
        return None
    d = None
    for o in olaylar:
        tip = o.get("tip")
        if tip == "baslat":
            if d is None:
                d = _iskelet(o.get("dosya"), o.get("zaman"), o.get("ceza_dali"))
            elif o.get("dosya"):
                d["dosya"] = o["dosya"]  # sonraki baslat yalnız kimliği tazeler
        elif tip == "adim":
            if d is None:
                d = _iskelet(None, o.get("zaman"), None)
            _uygula_adim(d, o)
        elif tip == "katman":
            if d is None:
                d = _iskelet(None, o.get("zaman"), None)
            _uygula_katman(d, o)
    return d


def _durum_yaz(durum_yol, d):
    """Türev görünümü ATOMİK yaz (tmp + os.replace). jsonl'den yeniden
    üretilebilir olduğundan bu dosyanın racy olması veri kaybı yaratmaz."""
    ust = os.path.dirname(durum_yol)
    if ust:
        os.makedirs(ust, exist_ok=True)
    tmp = f"{durum_yol}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    os.replace(tmp, durum_yol)


# --- kanıt disiplini (değişmedi) ---------------------------------------------
def dogrula_statu(args):
    if args.durum not in STATULER:
        sys.exit(f"HATA: geçersiz durum '{args.durum}'. Geçerli: {sorted(STATULER)}")
    if args.durum == "UYGULANDI":
        if not args.kanit or len(args.kanit.strip()) < MIN_KANIT:
            sys.exit("RET: UYGULANDI kanıtsız yazılamaz. --kanit ile fiilî işlemi "
                     f"(çağrı/script/MCP: araç+sorgu+sonuç) en az {MIN_KANIT} karakterle belgele.")
        return args.kanit.strip()
    if args.durum == "GEREKSIZ":
        if not args.gerekce:
            sys.exit("RET: GEREKSIZ gerekçesiz yazılamaz (--gerekce).")
        return "GEREKÇE: " + args.gerekce.strip()
    if args.durum == "BILGI-EKSIK":
        if not args.eksik:
            sys.exit("RET: BILGI-EKSIK, eksik bilgi tanımlanmadan yazılamaz (--eksik).")
        return "EKSİK: " + args.eksik.strip()
    if args.durum == "YUKLENEMEDI":
        if not args.kanit:
            sys.exit("RET: YUKLENEMEDI açıklamasız yazılamaz (--kanit ile neden + elden nasıl yürütüldüğü).")
        return "YÜKLENEMEDİ: " + args.kanit.strip()


def _defter_var(olaylar_yol, durum_yol):
    """--baslat yapılmış mı? (migrasyon dahil) — --isle/--katman ön-koşulu."""
    _migrasyon(olaylar_yol, durum_yol)
    return os.path.exists(olaylar_yol) and os.path.getsize(olaylar_yol) > 0


# --- komutlar ----------------------------------------------------------------
def baslat(args):
    olaylar_yol, durum_yol = _yollar(args)
    ust = os.path.dirname(olaylar_yol)
    if ust:
        os.makedirs(ust, exist_ok=True)
    onceki = os.path.exists(olaylar_yol) and os.path.getsize(olaylar_yol) > 0
    olay = {"zaman": simdi(), "tip": "baslat", "dosya": args.baslat, "ceza_dali": args.ceza}
    # --baslat fan-out ÖNCESİ tek-aktörlü bir komuttur; defteri taze kurar.
    with open(olaylar_yol, "w", encoding="utf-8") as f:
        f.write(json.dumps(olay, ensure_ascii=False) + "\n")
    _durum_yaz(durum_yol, derle(olaylar_yol))
    print(f"Defter açıldı: {olaylar_yol} — dosya: {args.baslat}"
          + (f" (ceza dalı: {args.ceza})" if args.ceza else ""))
    if onceki:
        print("NOT: önceki olay defteri vardı; --baslat taze başlattı (eski kayıtlar sıfırlandı).")
    print("Gerçeğin kaynağı: append-only olay defteri (jsonl); türev görünüm: " + durum_yol)
    print("Hatırlatma: statü ancak KANITLA yazılır; kanıt = fiilî Skill çağrısı / "
          "gerçek script çıktısı / gerçek MCP çağrısı (araç+sorgu+sonuç).")


def isle(args):
    olaylar_yol, durum_yol = _yollar(args)
    kanit = dogrula_statu(args)
    if args.adim is None:
        sys.exit("HATA: --adim gerekli (0-10).")
    if str(args.adim) not in {str(k) for k in ADIMLAR}:
        sys.exit(f"HATA: adım {args.adim} yok (0-10).")
    if not _defter_var(olaylar_yol, durum_yol):
        sys.exit(f"HATA: defter bulunamadı: {olaylar_yol} — önce --baslat ile aç.")
    # ATOMİK APPEND — eşzamanlı --isle'ler (farklı adım) birbirini silemez.
    olay_ekle(olaylar_yol, {"zaman": simdi(), "tip": "adim", "adim": args.adim,
                            "parca": args.parca, "durum": args.durum, "kanit": kanit})
    _durum_yaz(durum_yol, derle(olaylar_yol))  # türev görünümü tazele
    uyari = ""
    if (args.durum == "UYGULANDI" and args.parca in SCRIPTLI
            and "script" not in kanit.lower() and ".py" not in kanit.lower()):
        uyari = ("\nUYARI: bu parça SCRIPT'lidir; kanıtta script çıktısına iz yok — "
                 "gerçek script koştuysa kanıta yaz, koşmadıysa statü sahte olur.")
    print(f"İşlendi: adım {args.adim} / {args.parca} → {args.durum}{uyari}")


def katman_isle(args):
    olaylar_yol, durum_yol = _yollar(args)
    kanit = dogrula_statu(args)
    if not _defter_var(olaylar_yol, durum_yol):
        sys.exit(f"HATA: defter bulunamadı: {olaylar_yol} — önce --baslat ile aç.")
    olay_ekle(olaylar_yol, {"zaman": simdi(), "tip": "katman", "katman": args.katman,
                            "durum": args.durum, "kanit": kanit})
    _durum_yaz(durum_yol, derle(olaylar_yol))
    print(f"İşlendi: katman {args.katman} → {args.durum}")


def goster(args):
    olaylar_yol, durum_yol = _yollar(args)
    d = derle(olaylar_yol, durum_yol)
    if d is None:
        sys.exit(f"HATA: defter bulunamadı: {olaylar_yol} — önce --baslat ile aç.")
    _durum_yaz(durum_yol, d)  # türev görünümü tazele
    print(f"# Pipeline Defteri — {d['dosya']}  (açılış: {d['olusturma']})")
    for no in sorted(d["adimlar"], key=lambda x: int(x) if str(x).lstrip("-").isdigit() else 0):
        a = d["adimlar"][no]
        for parca, p in a["parcalar"].items():
            isaret = {"UYGULANDI": "✓", "GEREKSIZ": "−", "BILGI-EKSIK": "?",
                      "YUKLENEMEDI": "!", "BEKLIYOR": "⬜"}.get(p["durum"], "?")
            print(f"{isaret} {no:>2}. {a['ad']:<11} {parca:<18} {p['durum']}"
                  + (f" — {p['kanit'][:90]}" if p["kanit"] else ""))
    print("— Katmanlar —")
    for k, p in d["katmanlar"].items():
        print(f"  {k:<18} {p['durum']}" + (f" — {p['kanit'][:90]}" if p["kanit"] else ""))


def denetle(args):
    olaylar_yol, durum_yol = _yollar(args)
    d = derle(olaylar_yol, durum_yol)
    if d is None:
        sys.exit(f"HATA: defter bulunamadı: {olaylar_yol} — önce --baslat ile aç.")
    _durum_yaz(durum_yol, d)
    sorunlar, uyarilar = [], []
    for no in sorted(d["adimlar"], key=lambda x: int(x) if str(x).lstrip("-").isdigit() else 0):
        a = d["adimlar"][no]
        for parca, p in a["parcalar"].items():
            if p["durum"] == "BEKLIYOR":
                sorunlar.append(f"adım {no} ({a['ad']}) / {parca}: statü YOK (sessiz atlama?)")
            elif p["durum"] == "UYGULANDI":
                if not p["kanit"] or len(p["kanit"]) < MIN_KANIT:
                    sorunlar.append(f"adım {no} / {parca}: UYGULANDI ama kanıt yetersiz")
                elif (parca in SCRIPTLI and "script" not in p["kanit"].lower()
                      and ".py" not in p["kanit"].lower()):
                    uyarilar.append(f"adım {no} / {parca}: script'li parça, kanıtta script izi yok")
            elif p["durum"] == "YUKLENEMEDI":
                uyarilar.append(f"adım {no} / {parca}: fiziken yüklenemedi — çıktıda açıkça belirtilmeli")
    for k, p in d["katmanlar"].items():
        if p["durum"] == "BEKLIYOR":
            sorunlar.append(f"katman {k}: statü YOK (kalıcı katman 'gereksiz' olamaz; somut çıktısı kaydedilmeli)")
    if uyarilar:
        print("UYARILAR:")
        for u in uyarilar:
            print("  ⚠ " + u)
    if sorunlar:
        print("TESLİM ENGELİ — boşluklu tur teslim edilemez:")
        for s in sorunlar:
            print("  ✗ " + s)
        sys.exit(1)
    print("DENETİM TEMİZ: tüm adımlar ve katmanlar kanıtlı statüde. "
          "(Bu, içeriğin doğruluğunu değil, işletimin eksiksizliğini garanti eder — "
          "içerik denetimi oa-kontrol'ündür.)")


def main():
    ap = argparse.ArgumentParser(description="oa-pipeline defteri — statü ancak kanıtla yazılır (append-only jsonl)")
    ap.add_argument("--kok", default=".",
                    help="çalışma kökü (tam_tur.py/oa_metrik.py simetrisi; varsayılan CWD → CWD/_oa)")
    ap.add_argument("--yol", help="(geriye uyum) doğrudan pipeline-durum.json yolu; jsonl aynı klasörde")
    ap.add_argument("--baslat", metavar="DOSYA_ADI")
    ap.add_argument("--ceza", choices=["mudafii", "musteki"])
    ap.add_argument("--isle", action="store_true")
    ap.add_argument("--adim", type=int)
    ap.add_argument("--parca")
    ap.add_argument("--katman")
    ap.add_argument("--durum")
    ap.add_argument("--kanit")
    ap.add_argument("--gerekce")
    ap.add_argument("--eksik")
    ap.add_argument("--goster", action="store_true")
    ap.add_argument("--denetle", action="store_true")
    args = ap.parse_args()

    if args.baslat:
        baslat(args)
    elif args.isle:
        if not (args.parca and args.durum):
            sys.exit("HATA: --isle için --adim, --parca ve --durum gerekli.")
        isle(args)
    elif args.katman and args.durum:
        katman_isle(args)
    elif args.goster:
        goster(args)
    elif args.denetle:
        denetle(args)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()

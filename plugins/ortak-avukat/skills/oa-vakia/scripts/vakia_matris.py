#!/usr/bin/env python3
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
vakia_matris.py — DETERMİNİSTİK vakıa/delil yönetim motoru.

Amaç: Dosyanın OLGU/DELİL yarısını disipline etmek. (1) Kronoloji kurar, (2) her
iddiayı dayandığı delile eşler, (3) ispat boşluklarını ve yetim delilleri yakalar.

Dürüst sınır (anayasa): Script hukuki değerlendirme yapmaz. Deterministik olarak
SIRALAR (kronoloji), EŞLER (iddia↔delil) ve BOŞLUK/YETİM tespiti yapar. İspatın
yeterli olup olmadığına, delilin caiz olup olmadığına muhakeme + oa-kontrol/oa-antitez
(ispat_delil cephesi) karar verir.

Kullanım:
  python vakia_matris.py --iskelet
  python vakia_matris.py --dogrula vakia.json
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, importlib.util, json, os, sys
from datetime import date

# ── v0.5.14 (B-10 / T5A) — İSPAT KÜMESİ ÜÇE BÖLÜNDÜ ────────────────────────
# Eski hesap NEGATİF listeye dayanıyordu (`ispat_durumu != "ispatsiz"`): kapalı
# kümede HİÇ olmayan bir etiket (ör. "video") dolu bir `belge` ile birleşince
# iddiayı "belgeli" sayıyor ve `ispat_bosluklari` boş çıkıyordu (fail-open).
# Artık POZİTİF BEYAZ LİSTE geçerlidir:
#   ISPAT_TAM   → tek başına iddiayı BELGELİ destekleyebilen ispat araçları
#   ISPAT_KISMI → beyan: kayda geçer, ama tek başına belgeli destek SAYILMAZ
#   ISPAT       → adı ve rolü DEĞİŞMEDİ (iskelet basımı + geçersiz-etiket denetimi
#                 tek küme üzerinden çalışmaya devam eder)
ISPAT_TAM = {"belgeli", "tanik", "bilirkisi", "karine", "ikrar", "yemin"}
ISPAT_KISMI = {"beyan"}
ISPAT = ISPAT_TAM | ISPAT_KISMI | {"ispatsiz"}


# ── v0.5.8.4 ÖZNE TETİĞİ (372 karnesi: ozne_eslestirici'yi HİÇBİR akış
# çağırmıyordu — kullanıcı kararı: tetik oa-vakia'ya bağlanır). vakia_matris
# matris kurarken taraf/özne yazım varyantlarını toplar ve kardeş motorun
# jaro_winkler + eşikleriyle (BAGLA >= 0.92 / AVUKATA-SOR 0.80-0.92) damgalar.
# ADVISORY — karar vermez, `saglikli` hesabına GİRMEZ; varyant yoksa sessiz.

def _ozne_eslestirici_modulu():
    """ozne_eslestirici.py'yi (aynı dizin) İN-PROCESS import eder — algoritma
    TEKRARLANMAZ (tek-yazar kuralı; ozne_eslestirici.py DEĞİŞTİRİLMEZ, yalnız
    kullanılır). Import çökerse None döner; çağıran taraf bunu GÖRÜNÜR uyarıya
    çevirir (sessiz atlama yasağı)."""
    yol = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "ozne_eslestirici.py")
    if not os.path.isfile(yol):
        return None
    try:
        spec = importlib.util.spec_from_file_location("_vakia_ozne_eslestirici", yol)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def _ozne_adlarini_topla(m):
    """Matris girdisindeki taraf/özne YAZIMLARINI deterministik sırayla toplar:
    üst-düzey `taraflar` listesi (dize veya {"ad": ...}) + her olayın opsiyonel
    `ozne` alanı. Birebir aynı dize TEK sayılır (aynı yazım varyant değildir)."""
    adlar, gorulen = [], set()

    def _ekle(ad):
        ad = str(ad or "").strip()
        if ad and ad not in gorulen:
            gorulen.add(ad); adlar.append(ad)

    for t in m.get("taraflar", []) or []:
        _ekle(t.get("ad") if isinstance(t, dict) else t)
    for o in m.get("olaylar", []) or []:
        _ekle(o.get("ozne") if isinstance(o, dict) else None)
    return adlar


def ozne_eslestirme_kur(m):
    """tr_normalize sonrası aynı özneye ait GÖRÜNEN birden çok yazım varsa
    ozne_eslestirici skorlarıyla `ozne_eslestirme` bölümünü kurar:
      [{"varyantlar": [...], "skor": f, "karar": "BAGLA"|"AVUKATA-SOR"}]
    Varyant yoksa boş liste (sessiz). Döner: (bulgular, uyari) — `uyari`
    yalnız kardeş modül import edilemezse dolar (görünür fail-open)."""
    adlar = _ozne_adlarini_topla(m)
    if len(adlar) < 2:
        return [], None
    oe = _ozne_eslestirici_modulu()
    if oe is None:
        return [], ("ozne_eslestirici.py import edilemedi — özne yazım-varyantı "
                    "taraması YAPILAMADI (advisory; varyant birleştirme kararı "
                    "avukatta kalır)")
    bulgular = [{"varyantlar": [e["a"]["ad"], e["b"]["ad"]],
                 "skor": e["skor"], "karar": e["karar"]}
                for e in oe.eslestir(adlar)]
    return bulgular, None

def iskelet():
    """v0.5.14 (B-26): STDOUT yalnız GEÇERLİ JSON taşır; banner ve açıklamalar
    STDERR'e gider. SKILL.md'nin kendi öğrettiği kullanım
    `--iskelet > _oa/cikti/04-vakia.json` idi ve bugüne kadar sessizce
    AYRIŞTIRILAMAZ bir dosya üretiyordu (hata bir sonraki adımda çıkıyordu)."""
    def _not(*a):
        print(*a, file=sys.stderr)

    _not("="*68); _not("  VAKIA/DELİL MATRİSİ — kronoloji + iddia↔delil eşleme"); _not("="*68)
    _not("ispat_durumu değerleri:", ", ".join(sorted(ISPAT)))
    _not("  · ISPAT_TAM   :", ", ".join(sorted(ISPAT_TAM)),
         "→ dolu `belge` ile iddiayı BELGELİ destekler")
    _not("  · ISPAT_KISMI :", ", ".join(sorted(ISPAT_KISMI)),
         "→ kayda geçer, tek başına belgeli destek SAYILMAZ")
    sablon = {
        "taraflar": ["Taraf/özne adı (opsiyonel — yazım varyantları otomatik taranır, v0.5.8.4)"],
        "iddialar": [{"id":"I1","metin":"İspatlanacak maddi iddia — bir cümle"}],
        "olaylar": [{
            "tarih":"YYYY-MM-DD","olgu":"Ne oldu (kısa)",
            "ozne":"Olayın öznesi/faili (opsiyonel — özne varyant taramasına girer)",
            "belge":"Dayanak belge/delil (sözleşme, ihtarname, tutanak, tanık...) veya boş",
            "destekler":["I1"],
            "ispat_durumu":"|".join(sorted(ISPAT))
        }]
    }
    _not("\n--- Doldurulacak şablon (JSON — STDOUT) ---")
    print(json.dumps(sablon, ensure_ascii=False, indent=2))
    _not("\nDoldurduktan sonra: python vakia_matris.py --dogrula vakia.json")

def _parse_tarih(s):
    try: return date.fromisoformat(s)
    except Exception: return None

def dogrula(path, json_yol=None):
    try:
        with open(path, encoding="utf-8") as f: m = json.load(f)
    except Exception as e:
        print(f"❌ JSON okunamadı: {e}"); sys.exit(1)
    # v0.5.14 (B-23): kök tipi denetimi. Girdiyi model üretir; kök sözlük
    # değilse (null / [] / "dize") eski kod ham AttributeError traceback'i
    # veriyordu ve asıl mesaj kayboluyordu ("araç bozuldu" izlenimi).
    if not isinstance(m, dict):
        print(f"❌ JSON kökü sözlük değil ({type(m).__name__}) — vakia_matris "
              '{"iddialar": [...], "olaylar": [...]} biçiminde bir nesne bekler '
              "(şablon: --iskelet).")
        sys.exit(1)
    _ham_iddia = m.get("iddialar") or []
    _ham_olay = m.get("olaylar") or []
    iddialar = {i.get("id"): i.get("metin","") for i in _ham_iddia if isinstance(i, dict)}
    olaylar = [o for o in _ham_olay if isinstance(o, dict)]
    # sessiz atlama yasağı: sözlük olmayan kayıtlar düşürüldüyse GÖRÜNÜR olsun
    bicimsiz = [("iddialar", sum(1 for i in _ham_iddia if not isinstance(i, dict))),
                ("olaylar", sum(1 for o in _ham_olay if not isinstance(o, dict)))]
    bicimsiz = [f"{ad}: {n} kayıt sözlük değil — denetime alınmadı"
                for ad, n in bicimsiz if n > 0]

    tarihli, tarihsiz = [], []
    for o in olaylar:
        d = _parse_tarih(o.get("tarih","") or "")
        (tarihli if d else tarihsiz).append((d,o))
    tarihli.sort(key=lambda x: x[0])

    print("="*68); print("  VAKIA/DELİL DENETİMİ — KARAR-MALZEMESİ"); print("="*68)

    # 1) Kronoloji
    kronoloji = []
    print("\n--- KRONOLOJİ ---")
    for d,o in tarihli:
        bel = o.get("belge","") or "—"
        print(f"  {d.isoformat()} | {o.get('olgu','')}  [delil: {bel}; {o.get('ispat_durumu','?')}]")
        kronoloji.append({"tarih": d.isoformat(), "olgu": o.get("olgu",""),
                          "belge": o.get("belge","") or "", "ispat_durumu": o.get("ispat_durumu","")})
    if tarihsiz:
        print("  (tarihsiz — sıralanamadı:)")
        for _,o in tarihsiz: print(f"   ? {o.get('olgu','')}")

    # 2) İddia↔delil matrisi + ispat boşlukları
    print("\n--- İDDİA ↔ DELİL MATRİSİ ---")
    bos_iddia = []
    matris = []
    # v0.5.14 (B-10 / T5A): POZİTİF BEYAZ LİSTE. `belgeli` yalnız ISPAT_TAM
    # etiketli VE dolu `belge` taşıyan destekten doğar; `beyan` (ISPAT_KISMI)
    # ayrı sayılır ve tek başına iddiayı belgeli YAPMAZ.
    _d = lambda o: (o.get("ispat_durumu") or "")
    for iid, metin in iddialar.items():
        destek = [o for o in olaylar if iid in (o.get("destekler") or [])]
        belgeli = [o for o in destek if _d(o) in ISPAT_TAM and (o.get("belge") or "")]
        kismi = [o for o in destek if _d(o) in ISPAT_KISMI and (o.get("belge") or "")]
        print(f"  [{iid}] {metin}")
        if destek:
            for o in destek:
                print(f"       ← {o.get('tarih','?')} {o.get('olgu','')} ({o.get('ispat_durumu','?')})")
        if not belgeli:
            bos_iddia.append(iid)
            print("       ⚠ İSPAT BOŞLUĞU: bu iddiayı destekleyen belgeli/somut delil yok")
            if kismi:
                print("       ↳ yalnız KISMİ destek (beyan) — tek başına belgeli sayılmaz")
        matris.append({
            "iddia_id": iid, "metin": metin,
            "destekler": [o.get("olgu","") for o in destek],
            "belgeli": bool(belgeli),
            "kismi_destek": bool(kismi),
        })

    # 3) Yetim / eşlenmemiş deliller + geçersiz referans
    yetim, gecersiz_ref, gecersiz_durum = [], [], []
    for o in olaylar:
        dest = o.get("destekler") or []
        if not dest:
            yetim.append(o.get("olgu",""))
        for r in dest:
            if r not in iddialar: gecersiz_ref.append(f"{o.get('olgu','')} → bilinmeyen iddia '{r}'")
        if (o.get("ispat_durumu") or "") not in ISPAT:
            gecersiz_durum.append(f"{o.get('olgu','')}: '{o.get('ispat_durumu')}'")

    def blok(b, items, mark="!"):
        if items:
            print(f"\n--- {b} ---")
            for it in items: print(f"  {mark} {it}")

    blok("İSPAT BOŞLUKLARI (delilsiz iddialar — ispat yükü riski)", bos_iddia, "✗")
    blok("YETİM DELİLLER (hiçbir iddiaya bağlanmamış olgu)", yetim, "!")
    blok("GEÇERSİZ İDDİA REFERANSI", gecersiz_ref, "!")
    blok("GEÇERSİZ ispat_durumu", gecersiz_durum, "!")
    blok("BİÇİMSİZ KAYIT (sözlük değil — v0.5.14/B-23)", bicimsiz, "!")

    # 4) Özne yazım-varyantı taraması (v0.5.8.4 ÖZNE TETİĞİ — advisory,
    # saglikli hesabına GİRMEZ; "öznenin tüm beyanları" sorgusu varyant
    # yüzünden kayıt kaçırmasın — kayıpsızlık invaryantı). Varyant yoksa
    # SESSİZ (blok basılmaz); kardeş modül çökerse görünür uyarı.
    ozne_bulgular, ozne_uyari = ozne_eslestirme_kur(m)
    if ozne_uyari:
        print(f"\n  ! {ozne_uyari}")
    if ozne_bulgular:
        print("\n--- ÖZNE EŞLEŞTİRME (yazım varyantları — advisory, karar avukatta) ---")
        for b in ozne_bulgular:
            isaret = "?" if b["karar"] == "AVUKATA-SOR" else "~"
            print(f"  {isaret} {b['karar']} [{b['skor']}] "
                  + " ↔ ".join(f"«{v}»" for v in b["varyantlar"]))

    # Özet
    n_id = len(iddialar); n_destekli = n_id - len(bos_iddia)
    print("\n--- ÖZET ---")
    print(f"  İddia: {n_id} | belgeli destekli: {n_destekli} | ispat boşluğu: {len(bos_iddia)}")
    print(f"  Olay: {len(olaylar)} | tarihsiz: {len(tarihsiz)} | yetim: {len(yetim)}")
    # v0.5.14 (B-12): BOŞ GİRDİ AYRI SONUÇ SINIFI. Eskiden `{}` girdisi hiçbir
    # tespit listesini doldurmadığı için ">>> ... TAMAM <<<" basıyordu:
    # "0 iddia = kusursuz dosya". Denetlenecek içerik yokluğu, denetimin
    # GEÇTİĞİ anlamına gelmez. (Exit kodu sözleşmesi DEĞİŞMEZ — dogrula()
    # içinde sys.exit yoktur; sağlık sinyali çıktıdan/JSON'dan okunur.)
    denetlenemez = not iddialar and not olaylar
    saglikli = (not denetlenemez) and not (
        bos_iddia or tarihsiz or gecersiz_ref or gecersiz_durum or bicimsiz)
    if denetlenemez:
        print(">>> Dosya olgu/delil bütünlüğü DENETLENEMEDİ — girdide ne iddia "
              "ne olay var; boş matris 'TAMAM' sayılmaz <<<")
    else:
        print(">>> Dosya olgu/delil bütünlüğü " + ("TAMAM <<<" if saglikli else "EKSİK — yukarıdakiler kapatılmalı <<<"))
    print("="*68)

    if json_yol:
        sonuc = {
            "arac": "vakia_matris", "girdi": path,
            "kronoloji": kronoloji,
            "tarihsiz": [o.get("olgu","") for _,o in tarihsiz],
            "iddia_delil_matrisi": matris,
            "ispat_bosluklari": bos_iddia,
            "yetim_deliller": yetim,
            "gecersiz_referans": gecersiz_ref,
            "gecersiz_ispat_durumu": gecersiz_durum,
            "ozne_eslestirme": ozne_bulgular,
            "ozet": {"iddia": n_id, "belgeli_destekli": n_destekli,
                     "ispat_boslugu": len(bos_iddia), "olay": len(olaylar),
                     "tarihsiz": len(tarihsiz), "yetim": len(yetim)},
            "saglikli": saglikli,
        }
        with open(json_yol, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"[JSON] Makine-okur sonuc yazildi: {json_yol}")

def main():
    p = argparse.ArgumentParser(description="Deterministik vakıa/delil motoru")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--iskelet", action="store_true")
    g.add_argument("--dogrula", metavar="JSON")
    p.add_argument("--json", dest="json_yol", metavar="YOL",
                   help="--dogrula ile: denetim sonucunu makine-okur JSON olarak bu yola yaz (opsiyonel)")
    a = p.parse_args()
    iskelet() if a.iskelet else dogrula(a.dogrula, json_yol=a.json_yol)

if __name__=="__main__":
    try: main()
    except BrokenPipeError: sys.stderr.close()

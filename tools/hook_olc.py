#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
hook_olc.py — HOOK GECİKMESİ ÖLÇER (performans kanıt aracı)

NEDEN VAR: "hızlandırdım" bir BEYAN değil, bir ÖLÇÜMdür. Bu araç hook
yolundaki gerçek gecikmeyi ölçer; bir iyileştirme ancak burada görülürse
gerçektir. Ortak Avukat'ın "kanıtla yazılır" ilkesinin performans tarafı.

═══════════════════════════════════════════════════════════════════════════
İKİ ÖLÇÜM TUZAĞI — bu araç ikisini de KAPATIR
═══════════════════════════════════════════════════════════════════════════

TUZAK 1 — DEDUP KISA DEVRESİ (v0.5.16.3'te yakalandı)
`_hook_dedup_kisa_devre` aynı olayı aynı saniye içinde ikinci kez YAN-ETKİSİZ
kısa devre yapar; `prompt` için ayırt edici None'dır (anahtar yalnız olay adı).
Bir döngüde hook'u hızlı hızlı çağıran bir ölçüm betiği bu yüzden ÇOĞUNLUKLA
NO-OP ölçer. Ölçüldü (gerçek dava kökü): aralıksız çağrılar 56 ms, 1.1 sn
arayla aynı çağrı 210-373 ms. Yani aralıksız döngü gerçeği ~%70 YALANLAR.
→ Bu araç her çağrı arasında `--bekle` (varsayılan 1.1 sn) bekler ve
  kısa devre yapılan çağrıları AYIKLAR (`kisa_devre` sayacı).

TUZAK 2 — BOŞ KLASÖR TABANI
Boş bir geçici kökte hook neredeyse hiç iş yapmaz: dosya sistemi işi yoktur,
`_oa/` yoktur, kapılar erken çıkar. Gerçek maliyeti belirleyen şey modül
yükleme DEĞİL, dava kökündeki dosya sistemi işidir.
→ `--gercekci` bayrağı temsilî bir dava kökü kurar (evrak + defter +
  `_oa/cikti` ürünleri, ikili ürünler dahil) ve orada ölçer.

TUZAK 3 — YANLIŞ HEDEF
Gerçek sıcak yol `run-hook.cmd` → `hook_giris.py`'dir. Doğrudan
`pipeline_kayit.py` ölçmek TERK EDİLMİŞ yolu ölçer.
→ Varsayılan hedef `hook_giris.py`. `--hedef` ile karşılaştırılabilir;
  `--sarmalayici` gerçek `run-hook.cmd` üzerinden ölçer (kabuk katmanı dahil).

═══════════════════════════════════════════════════════════════════════════

Ölçüm ortamı ASLA gizlenmez: çıktı Python sürümünü, işletim sistemini ve
çekirdek sayısını basar. Bir sayı, ortamı olmadan anlamsızdır.

VERİ GÜVENLİĞİ: ölçüm İZOLE geçici bir kökte yapılır; gerçek dava
klasörlerine ve `_oa/` defterine DOKUNULMAZ. Betik hiçbir şey silmez
(yalnızca kendi kurduğu geçici kökü kaldırır).

Kullanım:
  python tools/hook_olc.py                          # boş kök, hızlı bakış
  python tools/hook_olc.py --gercekci               # GERÇEKÇİ dava kökü ← esas
  python tools/hook_olc.py --gercekci --tekrar 10   # daha kararlı
  python tools/hook_olc.py --gercekci --karsilastir # giriş vs doğrudan yol
  python tools/hook_olc.py --sarmalayici            # run-hook.cmd üzerinden
  python tools/hook_olc.py --import-dokumu          # ağır import avı
  python tools/hook_olc.py --json                   # makine okunur

Önce/sonra karşılaştırması AYNI makinede, AYNI yorumlayıcıyla, ARKA ARKAYA
yapılmalıdır (mutlak sayılar yorumlayıcı sürümüne ve `.pyc` sıcaklığına
göre değişir).
"""
import sys as _sys

for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

MODLAR = ("hook-prompt", "hook-pretool", "hook-postwrite", "hook-denetle", "hook-acilis")

YUKLER = {
    "hook-pretool": '{"tool_name":"Write","tool_input":{"file_path":"%s"}}',
    "hook-postwrite": '{"tool_name":"Write","tool_input":{"file_path":"%s"}}',
}

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO, "plugins", "ortak-avukat", "skills", "oa-pipeline", "scripts")
GIRIS = os.path.join(SCRIPTS, "hook_giris.py")
KAYIT = os.path.join(SCRIPTS, "pipeline_kayit.py")
WRAP = os.path.join(REPO, "plugins", "ortak-avukat", "hooks", "run-hook.cmd")


def _gercekci_kok():
    """Temsilî bir dava kökü kurar. NEDEN: boş kökte hook neredeyse hiç iş
    yapmaz; gerçek maliyeti `_oa/cikti` ve defter üzerindeki dosya sistemi
    işi belirler. İkili ÜRÜNLER (pdf/udf) bilinçli olarak konur — v0.5.16.3
    ikili süzgecinin etkisi ancak onlar varken görünür."""
    kok = tempfile.mkdtemp(prefix="oa-olcum-dava-")
    for i in range(1, 41):
        with open(os.path.join(kok, f"{i:03d}_evrak.pdf"), "wb") as f:
            f.write(b"evrak icerik\n")
    subprocess.run([sys.executable, KAYIT, "--baslat", "Ölçüm Davası 2026/1",
                    "--kok", kok],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cikti = os.path.join(kok, "_oa", "cikti")
    os.makedirs(cikti, exist_ok=True)
    os.makedirs(os.path.join(kok, "_oa", "teslim"), exist_ok=True)
    for ad in ("01-vakia", "02-illiyet", "03-ictihat", "04-kiyas",
               "05-strateji", "06-antitez"):
        with open(os.path.join(cikti, ad + ".md"), "w", encoding="utf-8") as f:
            f.write(f"# {ad}\n" + ("lorem ipsum dolor sit amet " * 400))
    with open(os.path.join(cikti, "dilekce-taslak.md"), "w", encoding="utf-8") as f:
        f.write("DAVACI : X\nDAVALI : Y\n\nNETİCE-İ TALEP\n" + ("metin " * 2000))
    # ikili ÜRÜNLER — süzgeç olmadan bunlar utf-8'e çözülüp regex'e giriyordu
    with open(os.path.join(cikti, "ek-deliller.pdf"), "wb") as f:
        f.write(b"%PDF-1.4\n" + bytes(3 * 1024 * 1024))
    with open(os.path.join(cikti, "TASLAK.udf"), "wb") as f:
        f.write(bytes(400 * 1024))
    return kok


def _komut(hedef, mod, kok):
    if hedef == "sarmalayici":
        kabuk = shutil.which("bash")
        if kabuk:
            return [kabuk, WRAP, mod]
        return None                        # bash yok (saf Windows) — atla
    return [sys.executable, hedef, "--" + mod, "--kok", kok]


def _tek_cagri(komut, yuk, kok):
    t0 = time.perf_counter()
    p = subprocess.run(komut, cwd=kok, input=yuk.encode("utf-8"),
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    sure = (time.perf_counter() - t0) * 1000.0
    return sure, (p.stdout or b"")


def _ciplak_baslik(tekrar):
    sureler = []
    for _ in range(tekrar):
        t0 = time.perf_counter()
        subprocess.run([sys.executable, "-c", "pass"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sureler.append((time.perf_counter() - t0) * 1000.0)
    return statistics.median(sureler)


def _mod_olc(hedef, mod, kok, tekrar, bekle):
    """Dedup kısa devresini YENEREK ölçer: her çağrı arasında `bekle` saniye
    beklenir. Çıktısı BOŞ olan çağrılar ayrıca sayılır — dava kökünde boş
    çıktı çoğu modda kısa devre işaretidir."""
    komut = _komut(hedef, mod, kok)
    if komut is None:
        return None
    yuk = YUKLER.get(mod, "{}")
    if "%s" in yuk:
        yuk = yuk % os.path.join(kok, "olcum.md").replace("\\", "\\\\")
    sureler, bos = [], 0
    for i in range(tekrar):
        if i and bekle:
            time.sleep(bekle)              # ← dedup kısa devresini yener
        sure, cikti = _tek_cagri(komut, yuk, kok)
        sureler.append(sure)
        if not cikti.strip():
            bos += 1
    return {
        "ortanca_ms": round(statistics.median(sureler), 2),
        "en_hizli_ms": round(min(sureler), 2),
        "en_yavas_ms": round(max(sureler), 2),
        "cagri": tekrar,
        "bos_cikti": bos,
    }


def _import_dokumu(kok, hedef):
    """Sıcak yolda hangi ağır modüllerin çekildiğini gösterir. Bir hook,
    işiyle ilgisiz bir modülü (zipfile, multiprocessing, pymupdf…) import
    ediyorsa orada gizli bir maliyet vardır.

    `hedef` ÇAĞIRAN tarafından çözülmüş yoldur — sabit `hook_giris.py`
    KULLANILMAZ: o dosya olmayan bir sürümde (ör. eski bir dalda) alt süreç
    sessizce çöker, stderr boş gelir ve döküm yanlışlıkla 'ağır modül YOK'
    der. Bu araç dürüstlük iddia ediyor; sessiz yanlış negatif kabul edilemez."""
    AGIR = ("concurrent.futures", "multiprocessing", "zipfile", "xml.etree",
            "subprocess", "pathlib", "tempfile", "logging", "pymupdf", "fitz",
            "PIL", "PIL.Image")
    print("\n── SICAK YOL IMPORT DÖKÜMÜ (ağır modül avı) ──")
    print(f"  hedef: {os.path.basename(hedef)}")
    for mod in ("hook-prompt", "hook-denetle"):
        p = subprocess.run(
            [sys.executable, "-X", "importtime", hedef, "--" + mod, "--kok", kok],
            input=b"{}", cwd=kok,
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        ham = p.stderr.decode("utf-8", "replace")
        satirlar = [s for s in ham.splitlines() if "import time:" in s]
        if not satirlar:
            # Alt süreç hiç import dökümü üretmedi → ölçüm GEÇERSİZ.
            print(f"  --{mod}: DÖKÜM ALINAMADI (alt süreç çöktü mü?) — "
                  f"bu bir 'ağır modül yok' sonucu DEĞİLDİR")
            ilk = ham.strip().splitlines()[-1] if ham.strip() else "(stderr boş)"
            print(f"      son stderr satırı: {ilk[:120]}")
            continue
        bulunan = []
        for s in satirlar:
            ad = s.split("|")[-1].strip()
            if ad in AGIR:
                bulunan.append((ad, s.split("|")[1].strip()))
        if bulunan:
            print(f"  --{mod}: {len(bulunan)} ağır modül")
            for ad, us in bulunan:
                print(f"      {ad:<22} kümülatif {us} µs")
        else:
            print(f"  --{mod}: ağır modül YOK ✓ ({len(satirlar)} import izlendi)")


def main():
    ap = argparse.ArgumentParser(
        description="Ortak Avukat hook gecikmesi ölçer (dedup-güvenli)")
    ap.add_argument("--tekrar", type=int, default=5,
                    help="mod başına çağrı sayısı (varsayılan 5; her çağrı "
                         "arasında --bekle beklenir, o yüzden az tutuldu)")
    ap.add_argument("--bekle", type=float, default=1.1,
                    help="çağrılar arası bekleme sn (varsayılan 1.1 — dedup "
                         "kısa devresini yener). 0 = beklemeden ölç (TUZAK: "
                         "sonuçlar no-op'larla kirlenir)")
    ap.add_argument("--mod", action="append", choices=MODLAR,
                    help="sadece bu mod(lar); yoksa hepsi")
    ap.add_argument("--gercekci", action="store_true",
                    help="TEMSİLÎ DAVA KÖKÜ kur ve orada ölç (esas ölçüm)")
    ap.add_argument("--karsilastir", action="store_true",
                    help="hook_giris.py ile doğrudan pipeline_kayit.py'yi kıyasla")
    ap.add_argument("--sarmalayici", action="store_true",
                    help="gerçek run-hook.cmd üzerinden ölç (kabuk katmanı dahil)")
    ap.add_argument("--json", action="store_true", help="makine okunur çıktı")
    ap.add_argument("--import-dokumu", action="store_true", dest="import_dokumu",
                    help="sıcak yolda ağır import avı")
    args = ap.parse_args()

    if not os.path.isfile(KAYIT):
        sys.exit("HATA: pipeline_kayit.py bulunamadı (depo kökünden mi koşuyorsunuz?)")
    hedef_ana = GIRIS if os.path.isfile(GIRIS) else KAYIT

    modlar = tuple(args.mod) if args.mod else MODLAR
    ortam = {
        "python": platform.python_version(),
        "isletim_sistemi": f"{platform.system()} {platform.release()}",
        "makine": platform.machine(),
        "cekirdek": os.cpu_count(),
        "tekrar": args.tekrar,
        "bekle_sn": args.bekle,
        "kok_tipi": "gerçekçi dava kökü" if args.gercekci else "boş kök",
        "hedef": os.path.basename(hedef_ana),
    }

    kok = _gercekci_kok() if args.gercekci else tempfile.mkdtemp(prefix="oa-olcum-bos-")
    try:
        taban = _ciplak_baslik(max(5, args.tekrar))
        sonuc, kars = {}, {}
        for mod in modlar:
            o = _mod_olc(hedef_ana, mod, kok, args.tekrar, args.bekle)
            if o is None:
                continue
            o["net_eklenti_yuku_ms"] = round(o["ortanca_ms"] - taban, 2)
            sonuc[mod] = o
            if args.karsilastir:
                d = _mod_olc(KAYIT, mod, kok, args.tekrar, args.bekle)
                if d:
                    d["net_eklenti_yuku_ms"] = round(d["ortanca_ms"] - taban, 2)
                    kars[mod] = d
        sar = {}
        if args.sarmalayici:
            for mod in modlar:
                s = _mod_olc("sarmalayici", mod, kok, args.tekrar, args.bekle)
                if s:
                    s["net_eklenti_yuku_ms"] = round(s["ortanca_ms"] - taban, 2)
                    sar[mod] = s

        if args.json:
            print(json.dumps({"ortam": ortam, "ciplak_baslik_ms": round(taban, 2),
                              "modlar": sonuc, "dogrudan_yol": kars,
                              "sarmalayici": sar},
                             ensure_ascii=False, indent=2))
        else:
            print("── ORTAM ──")
            for k, v in ortam.items():
                print(f"  {k:<18} {v}")
            print(f"  {'çıplak başlık':<18} {taban:.2f} ms (ortanca)")
            if not args.gercekci:
                print("\n  ! BOŞ KÖK ölçümü — hook neredeyse hiç dosya sistemi işi")
                print("    yapmıyor. Gerçek maliyet için: --gercekci")
            if not args.bekle:
                print("\n  ! --bekle 0 — dedup kısa devresi sonuçları KİRLETİR.")

            print("\n── HOOK GECİKMESİ ──")
            print(f"  {'mod':<16} {'ortanca':>9} {'en hızlı':>9} {'en yavaş':>9} "
                  f"{'NET':>9}  boş çıktı")
            for mod, o in sonuc.items():
                print(f"  {mod:<16} {o['ortanca_ms']:>7.1f}ms {o['en_hizli_ms']:>7.1f}ms "
                      f"{o['en_yavas_ms']:>7.1f}ms {o['net_eklenti_yuku_ms']:>7.1f}ms"
                      f"   {o['bos_cikti']}/{o['cagri']}")
            if kars:
                print("\n── KARŞILAŞTIRMA: doğrudan pipeline_kayit.py (terk edilmiş yol) ──")
                for mod, d in kars.items():
                    fark = d["ortanca_ms"] - sonuc[mod]["ortanca_ms"]
                    print(f"  {mod:<16} {d['ortanca_ms']:>7.1f}ms  "
                          f"(giriş betiği {fark:+.1f} ms daha {'hızlı' if fark > 0 else 'YAVAŞ'})")
            if sar:
                print("\n── SARMALAYICI (run-hook.cmd — kabuk katmanı dahil) ──")
                for mod, s in sar.items():
                    print(f"  {mod:<16} {s['ortanca_ms']:>7.1f}ms")
            if "hook-pretool" in sonuc and "hook-postwrite" in sonuc:
                cift = sonuc["hook-pretool"]["ortanca_ms"] + sonuc["hook-postwrite"]["ortanca_ms"]
                print(f"\n  BİLEŞİK: bir Write, Pre+Post ateşler → {cift:.1f} ms bloklama")

        if args.import_dokumu:
            _import_dokumu(kok, hedef_ana)
    finally:
        shutil.rmtree(kok, ignore_errors=True)   # sadece KENDİ geçici kökünü siler


if __name__ == "__main__":
    main()

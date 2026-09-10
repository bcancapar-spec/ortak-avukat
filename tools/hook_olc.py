#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
hook_olc.py — HOOK GECİKMESİ ÖLÇER (performans kanıt aracı)

NEDEN VAR: "hızlandırdım" bir BEYAN değil, bir ÖLÇÜMdür. Bu araç hook
yolundaki gerçek gecikmeyi ölçer; bir iyileştirme ancak burada görülürse
gerçektir. Ortak Avukat'ın "kanıtla yazılır" ilkesinin performans tarafı.

NE ÖLÇER: her hook modu için `python pipeline_kayit.py --<mod>` çağrısının
uçtan uca süresi. Çıplak yorumlayıcı başlığı ayrıca ölçülüp ÇIKARILIR, böylece
raporlanan sayı EKLENTİNİN KENDİ ek yüküdür (yorumlayıcı maliyeti değil) —
farklı makineler/Python sürümleri arasında karşılaştırılabilir tek sayı budur.

Ölçüm ortamı ASLA gizlenmez: çıktı Python sürümünü, işletim sistemini ve
çekirdek sayısını basar. Bir sayı, ortamı olmadan anlamsızdır.

VERİ GÜVENLİĞİ: ölçüm İZOLE geçici bir kökte (`--kok`) yapılır; gerçek dava
klasörlerine ve `_oa/` defterine DOKUNULMAZ. Betik hiçbir şey silmez.

Kullanım:
  python tools/hook_olc.py                      # tüm modlar, 20 tekrar
  python tools/hook_olc.py --tekrar 50          # daha kararlı ölçüm
  python tools/hook_olc.py --mod hook-prompt    # tek mod
  python tools/hook_olc.py --json               # makine okunur çıktı
  python tools/hook_olc.py --import-dokumu      # ağır import avı (-X importtime)

Karşılaştırma (önce/sonra) için:
  git stash && python tools/hook_olc.py --json > /tmp/once.json && git stash pop
  python tools/hook_olc.py --json > /tmp/sonra.json
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

# Her mod için hook'un stdin'den beklediği temsilî yük. hook-pretool ve
# hook-postwrite tool_input okur; diğerleri boş nesneyle yetinir.
YUKLER = {
    "hook-pretool": '{"tool_name":"Write","tool_input":{"file_path":"%s"}}',
    "hook-postwrite": '{"tool_name":"Write","tool_input":{"file_path":"%s"}}',
}


def _betik_yolu():
    """pipeline_kayit.py'yi bu dosyaya GÖRELİ bulur (depo taşınsa da çalışır)."""
    kok = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yol = os.path.join(kok, "plugins", "ortak-avukat", "skills",
                       "oa-pipeline", "scripts", "pipeline_kayit.py")
    return yol if os.path.isfile(yol) else None


def _ciplak_baslik(tekrar):
    """Yorumlayıcının kendi başlığı — eklenti yükünden ÇIKARILACAK taban."""
    sureler = []
    for _ in range(tekrar):
        t0 = time.perf_counter()
        subprocess.run([sys.executable, "-c", "pass"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sureler.append((time.perf_counter() - t0) * 1000.0)
    return sureler


def _mod_olc(betik, mod, kok, tekrar):
    yuk = YUKLER.get(mod, "{}")
    if "%s" in yuk:
        yuk = yuk % os.path.join(kok, "olcum.md").replace("\\", "\\\\")
    sureler = []
    for _ in range(tekrar):
        t0 = time.perf_counter()
        subprocess.run([sys.executable, betik, "--" + mod, "--kok", kok],
                       input=yuk.encode("utf-8"),
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sureler.append((time.perf_counter() - t0) * 1000.0)
    return sureler


def _ozet(sureler):
    """Ortalama YERİNE ortanca (medyan) esas alınır: süreç başlığı ölçümleri
    sağa çarpıktır (nadiren çok yavaş çağrılar ortalamayı bozar)."""
    return {
        "ortanca_ms": round(statistics.median(sureler), 2),
        "en_hizli_ms": round(min(sureler), 2),
        "en_yavas_ms": round(max(sureler), 2),
        "ortalama_ms": round(statistics.fmean(sureler), 2),
    }


def _import_dokumu(betik, kok):
    """Sıcak yolda hangi ağır modüllerin çekildiğini gösterir. Bir hook,
    işiyle ilgisiz bir modülü (zipfile, multiprocessing…) import ediyorsa
    orada gizli bir maliyet vardır."""
    AGIR = ("concurrent.futures", "multiprocessing", "zipfile",
            "xml.etree", "subprocess", "pathlib", "tempfile", "logging")
    print("\n── SICAK YOL IMPORT DÖKÜMÜ (ağır modül avı) ──")
    for mod in ("hook-prompt", "hook-pretool"):
        p = subprocess.run(
            [sys.executable, "-X", "importtime", betik, "--" + mod, "--kok", kok],
            input=b"{}", stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        satirlar = p.stderr.decode("utf-8", "replace").splitlines()
        bulunan = []
        for s in satirlar:
            ad = s.split("|")[-1].strip() if "|" in s else ""
            if ad in AGIR:
                us = s.split("|")[1].strip() if s.count("|") >= 2 else "?"
                bulunan.append((ad, us))
        if bulunan:
            print(f"  --{mod}: {len(bulunan)} ağır modül")
            for ad, us in bulunan:
                print(f"      {ad:<24} kümülatif {us} µs")
        else:
            print(f"  --{mod}: ağır modül YOK ✓")


def main():
    ap = argparse.ArgumentParser(
        description="Ortak Avukat hook gecikmesi ölçer (eklenti net ek yükü)")
    ap.add_argument("--tekrar", type=int, default=20,
                    help="mod başına çağrı sayısı (varsayılan 20)")
    ap.add_argument("--mod", action="append", choices=MODLAR,
                    help="sadece bu mod(lar) (yinelenebilir); yoksa hepsi")
    ap.add_argument("--json", action="store_true", help="makine okunur çıktı")
    ap.add_argument("--import-dokumu", action="store_true", dest="import_dokumu",
                    help="sıcak yolda ağır import avı")
    args = ap.parse_args()

    betik = _betik_yolu()
    if betik is None:
        sys.exit("HATA: pipeline_kayit.py bulunamadı (depo kökünden mi koşuyorsunuz?)")

    modlar = tuple(args.mod) if args.mod else MODLAR
    ortam = {
        "python": platform.python_version(),
        "isletim_sistemi": f"{platform.system()} {platform.release()}",
        "makine": platform.machine(),
        "cekirdek": os.cpu_count(),
        "tekrar": args.tekrar,
    }

    # İZOLE ölçüm kökü: gerçek dava klasörlerine ve deftere ASLA dokunulmaz.
    kok = tempfile.mkdtemp(prefix="oa-hook-olcum-")
    try:
        taban = _ozet(_ciplak_baslik(args.tekrar))
        sonuc = {}
        for mod in modlar:
            o = _ozet(_mod_olc(betik, mod, kok, args.tekrar))
            o["net_eklenti_yuku_ms"] = round(o["ortanca_ms"] - taban["ortanca_ms"], 2)
            sonuc[mod] = o

        if args.json:
            print(json.dumps({"ortam": ortam, "ciplak_baslik": taban,
                              "modlar": sonuc}, ensure_ascii=False, indent=2))
        else:
            print("── ORTAM ──")
            for k, v in ortam.items():
                print(f"  {k:<18} {v}")
            print(f"\n  çıplak yorumlayıcı başlığı: {taban['ortanca_ms']} ms (ortanca)")
            print("\n── HOOK GECİKMESİ ──")
            print(f"  {'mod':<16} {'ortanca':>9} {'en hızlı':>9} {'en yavaş':>9} "
                  f"{'NET EKLENTİ':>12}")
            for mod, o in sonuc.items():
                print(f"  {mod:<16} {o['ortanca_ms']:>7.2f}ms {o['en_hizli_ms']:>7.2f}ms "
                      f"{o['en_yavas_ms']:>7.2f}ms {o['net_eklenti_yuku_ms']:>10.2f}ms")
            # Bileşik etki: bir Write, PreToolUse + PostToolUse ikisini ateşler.
            if "hook-pretool" in sonuc and "hook-postwrite" in sonuc:
                cift = sonuc["hook-pretool"]["ortanca_ms"] + sonuc["hook-postwrite"]["ortanca_ms"]
                print(f"\n  BİLEŞİK: bir Write çağrısı Pre+Post ateşler → {cift:.2f} ms bloklama")
                print(f"  30 araç çağrılı bir tur ≈ {cift * 15 / 1000:.2f} s saf hook bloklaması")

        if args.import_dokumu:
            _import_dokumu(betik, kok)
    finally:
        shutil.rmtree(kok, ignore_errors=True)   # sadece KENDİ geçici kökünü siler


if __name__ == "__main__":
    main()

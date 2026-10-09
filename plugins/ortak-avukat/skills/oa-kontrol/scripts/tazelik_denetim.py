#!/usr/bin/env python3
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa-kontrol — tazelik_denetim.py  (v0.5.8, P6+P7 — graft deseninin devşirmesi;
bkz. anayasa m.0 dış desen devşirme protokolü, Can kararı 2026-08-12)

ÜRÜN-TAZELİK ZİNCİRİ: `_oa/cikti` ürünleri başlarındaki KAYNAK-BLOĞU ile
hangi girdiden türediklerini içerik-hash'iyle beyan eder (graft'ın
"Sources@hash" düğüm-başlığı deseni):

    <!-- kaynaklar: metin/00-kunye.json@a1b2c3d4 · cikti/01-illiyet-graf.json@e5f6a7b8 -->
    <!-- besledigi: 08-CBS-dilekce -->
    <!-- uretim: 2026-08-12T10:00Z · oa-strateji -->

Bu denetçi her ürünün beyan ettiği kaynak hash'lerini dosyaların BUGÜNKÜ
hash'iyle karşılaştırır; uyuşmayan ürün BAYAT ilan edilir ("kaynağı
üretiminden sonra değişti — delta geçişi gerek").

FELSEFE (amaç çizgisi): ADVISORY — her zaman exit 0. Saha kanıtı (Çal 1079):
graflar külliyatın %20'sindeyken doğdu, külliyat 5 kat büyüdü, ürünler
sessizce eskidi; delta emri İNSAN gözcüden geldi. Bu denetçi o gözcünün
otomasyonudur — BLOK değil, görünürlük. LLM'siz, token'sız, saniyelik.

JSON ÜRÜNLERİ (v0.5.18 — B-1b, zincirleme tepki): dört motorun (vakıa /
illiyet grafı / kıyas / antitez) `--json` denetim çıktısı da bir ÜRÜNDÜR ve
S1 sözleşmesiyle kaynağını beyan eder:

    {"arac": "vakia_matris", ..., "kaynaklar": [
        {"rol": "girdi", "yol": "cikti/04-vakia.json", "sha8": "a1b2c3d4"},
        {"rol": "kunye", "yol": "metin/00-kunye.json", "sha8": "e5f6a7b8"}]}

`yol` `_oa` dizinine göre POSIX göreli yoldur; `sha8` bu dosyanın `sha8()`
fonksiyonuyla AYNI hesaptır. Üç ayrı hâl üç ayrı sözcükle anılır ki
belirsizlik gizlenmesin: `kaynaklar` alanı HİÇ YOKSA ürün «beyansız (eski)»dir
(kademeli benimseme — bayat DEĞİL, alarm yok); alan BOŞ LİSTE + `kaynaklar_
notu` ise motor `_oa` dışında bir girdiyle koşmuştur → «denetim DIŞI» (temiz
DENMEZ); JSON hiç çözülemiyorsa «OKUNAMADI» (yarım yazım / elle düzenleme —
temiz SAYILMAZ). Damgasız (`arac`sız) JSON model GİRDİSİDİR, türetilmiş ürün
değil — denetim konusu olmaz.

Kullanım:
    python tazelik_denetim.py --kok <dava_koku> [--json]
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import hashlib
import json
import os
import re
import sys

KAYNAK_BLOK_RE = re.compile(
    r"<!--\s*kaynaklar:\s*(.+?)\s*-->", re.IGNORECASE)
# Girdi biçimi: "yol@sha8" öğeleri "·" veya "," ile ayrılır.
KAYNAK_OGE_RE = re.compile(r"(\S+?)@([0-9a-fA-F]{8})")


def sha8(yol):
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 16), b""):
            h.update(parca)
    return h.hexdigest()[:8]


def _guvenli_yol(kok, goreli):
    """Kaynak yolu dava kökü İÇİNDE kalmalı (yol-kaçış koruması)."""
    tam = os.path.realpath(os.path.join(kok, "_oa", goreli))
    oa = os.path.realpath(os.path.join(kok, "_oa"))
    if not (tam == oa or tam.startswith(oa + os.sep)):
        return None
    return tam


def _beyan_karsilastir(kok, ciftler):
    """[(goreli, beyan_sha8)] → (bayatlar, eksikler). md-bloğu ve JSON
    `kaynaklar` beyanı AYNI karşılaştırmadan geçer (tek kaynak — iki ürün
    türü için iki ayrı kural kümesi İCAT EDİLMEZ)."""
    bayatlar, eksikler = [], []
    for goreli, beyan in ciftler:
        tam = _guvenli_yol(kok, goreli)
        if tam is None or not os.path.isfile(tam):
            eksikler.append(goreli)
            continue
        simdiki = sha8(tam)
        if simdiki.lower() != beyan.lower():
            bayatlar.append((goreli, beyan.lower(), simdiki.lower()))
    return bayatlar, eksikler


def _json_urun_cozumle(kok, urun_yolu):
    """v0.5.18 (B-1b) — damgalı denetim JSON'unun S1 kaynak beyanını çözer.
    Döner: (durum, bayatlar, eksikler, not). `durum` ∈
      "beyanli"      — `kaynaklar` dolu; bayat/eksik listeleri geçerli
      "beyansiz"     — damgalı ama `kaynaklar` alanı yok (eski sürüm ürünü;
                       kademeli benimseme — bayat DEĞİL)
      "denetim-disi" — `kaynaklar: []` (+ `kaynaklar_notu`): motor `_oa`
                       dışı girdiyle koştu — tazelik hükmü VERİLEMEZ
      "okunamadi"    — JSON çözülemedi / biçimsiz (temiz SAYILMAZ)
      "yabanci"      — damgasız (`arac`sız) JSON: model girdisi, ürün değil
    ASLA fırlatmaz."""
    try:
        with open(urun_yolu, encoding="utf-8") as f:
            veri = json.load(f)
    except Exception as e:  # noqa: BLE001 — okunamayan ürün GÖRÜNÜR kalır
        hata = " ".join(f"{type(e).__name__}: {e}".split())[:120]
        return "okunamadi", None, None, hata
    if not isinstance(veri, dict) or not veri.get("arac"):
        return "yabanci", None, None, None
    if "kaynaklar" not in veri:
        return "beyansiz", None, None, None
    kaynaklar = veri.get("kaynaklar")
    if not isinstance(kaynaklar, list):
        return "okunamadi", None, None, "`kaynaklar` alanı liste değil"
    if not kaynaklar:
        notu = veri.get("kaynaklar_notu")
        return ("denetim-disi", None, None,
                str(notu) if notu else "kaynak beyanı boş (not yok)")
    ciftler, bicimsiz = [], []
    for k in kaynaklar:
        if (isinstance(k, dict) and isinstance(k.get("yol"), str)
                and isinstance(k.get("sha8"), str)):
            ciftler.append((k["yol"], k["sha8"]))
        else:
            bicimsiz.append("<biçimsiz kaynak kaydı: %s>" % " ".join(repr(k).split())[:80])
    bayatlar, eksikler = _beyan_karsilastir(kok, ciftler)
    # Ö-1 (Görev 1 incelemesi): KISMİ beyan TAZE sayılmaz. Üretici okunamayan rolü listeden düşürüp
    # sebebini `kaynaklar_notu`na yazar; liste doluyken not okunmuyor ve `girdi` rolünün yokluğu fark
    # edilmiyordu — beyansız girdi sonradan değişse bayatlık hiç görünmez, CLI «TAZE» derdi.
    notu = veri.get("kaynaklar_notu")
    if notu:
        bicimsiz.append("<beyan notu: %s>" % " ".join(str(notu).split())[:160])
    if not any(isinstance(k, dict) and k.get("rol") == "girdi" for k in kaynaklar):
        bicimsiz.append("<girdi beyanı yok — girdi değişse bayatlık ölçülemez>")
    return "beyanli", bayatlar, eksikler + bicimsiz, None


def urun_denetle(kok, urun_yolu):
    """Tek ürünün kaynak beyanını okur; (bayatlar, eksikler) döndürür.
    Beyan yoksa (None, None) — kademeli benimseme: beyansız ürün denetim DIŞI.
    `.json` ürünlerde (v0.5.18) beyan S1 `kaynaklar` alanıdır; yalnız
    "beyanli" hâl liste döndürür — beyansız / denetim-dışı / okunamadı /
    yabancı hâllerinin ayrımı `_json_urun_cozumle` + `kok_denetle`'dedir
    (bu fonksiyonun dönüş sözleşmesi çağıranlar için DEĞİŞMEZ)."""
    if str(urun_yolu).lower().endswith(".json"):
        durum, bayatlar, eksikler, _notu = _json_urun_cozumle(kok, urun_yolu)
        if durum != "beyanli":
            return None, None
        return bayatlar, eksikler
    with open(urun_yolu, encoding="utf-8", errors="replace") as f:
        bas = f.read(2048)  # blok dosyanın başındadır — bütünü okumaya gerek yok
    m = KAYNAK_BLOK_RE.search(bas)
    if not m:
        return None, None
    return _beyan_karsilastir(kok, KAYNAK_OGE_RE.findall(m.group(1)))


def kok_denetle(kok):
    """Dava kökünün `_oa/cikti` ürünlerini (md/txt bloğu + json beyanı)
    denetler; `--json` çıktısının ve pipeline_kayit'in (DURUM.md «Bayat Zincir»
    hattı, in-process) ORTAK kaynağı. Deterministik (ad sırası). Anahtarlar:
      bloklu / bloksuz         — beyanlı / beyansız ürün sayısı (md+json)
      bayat   [{urun,kaynak,beyan,simdiki}]  ·  eksik [{urun,kaynak}]
      beyansiz_json [ad]       — damgalı ama `kaynaklar`sız (eski) JSON'lar
      denetim_disi  [{urun,not}] — `_oa` dışı girdiyle koşan motor çıktısı
      okunamayan    [{urun,hata}] — çözülemeyen JSON (temiz SAYILMAZ)
    `_oa/cikti` yoksa None."""
    cikti = os.path.join(kok, "_oa", "cikti")
    if not os.path.isdir(cikti):
        return None
    rapor = {"bloklu": 0, "bloksuz": 0, "bayat": [], "eksik": [],
             "beyansiz_json": [], "denetim_disi": [], "okunamayan": []}

    def _isle(ad, bayatlar, eksikler):
        rapor["bloklu"] += 1
        for goreli, beyan, simdiki in bayatlar:
            rapor["bayat"].append({"urun": ad, "kaynak": goreli,
                                   "beyan": beyan, "simdiki": simdiki})
        for goreli in eksikler:
            rapor["eksik"].append({"urun": ad, "kaynak": goreli})

    for ad in sorted(os.listdir(cikti)):
        yol = os.path.join(cikti, ad)
        if not os.path.isfile(yol):
            continue
        if ad.lower().endswith(".json"):
            durum, bayatlar, eksikler, notu = _json_urun_cozumle(kok, yol)
            if durum == "yabanci":
                continue                       # model girdisi — ürün değil
            if durum == "okunamadi":
                rapor["okunamayan"].append({"urun": ad, "hata": notu})
            elif durum == "beyansiz":
                rapor["bloksuz"] += 1
                rapor["beyansiz_json"].append(ad)
            elif durum == "denetim-disi":
                rapor["denetim_disi"].append({"urun": ad, "not": notu})
            else:
                _isle(ad, bayatlar, eksikler)
            continue
        if not ad.endswith((".md", ".txt")):
            continue
        bayatlar, eksikler = urun_denetle(kok, yol)
        if bayatlar is None:
            rapor["bloksuz"] += 1
            continue
        _isle(ad, bayatlar, eksikler)
    return rapor


def main():
    ap = argparse.ArgumentParser(
        description="Ürün-tazelik zinciri (v0.5.8 P6) — advisory, BLOKLAMAZ.")
    ap.add_argument("--kok", default=".", help="dava kökü (_oa'nın üstü)")
    ap.add_argument("--json", action="store_true",
                    help="DURUM.md advisory hattı için makine-okur çıktı")
    args = ap.parse_args()

    rapor = kok_denetle(args.kok)
    if rapor is None:
        if args.json:
            print(json.dumps({"durum": "cikti-yok", "bayat": [], "eksik": []},
                             ensure_ascii=False))
        else:
            print("tazelik: _oa/cikti yok — denetlenecek ürün bulunamadı.")
        sys.exit(0)

    if args.json:
        print(json.dumps(rapor, ensure_ascii=False))
        sys.exit(0)

    # Satır biçimi geriye uyumlu ("N bloklu … M bloksuz"); JSON ürünlerinde
    # "blok" = S1 `kaynaklar` beyanıdır, "beyansız (eski)" ayrıca sayılır.
    print(f"tazelik: {rapor['bloklu']} bloklu ürün denetlendi "
          f"({rapor['bloksuz']} bloksuz — kademeli benimseme"
          + (f"; {len(rapor['beyansiz_json'])} beyansız (eski) JSON"
             if rapor["beyansiz_json"] else "")
          + ").")
    for b in rapor["bayat"]:
        print(f"  ⚠ BAYAT: {b['urun']} — kaynağı {b['kaynak']} üretiminden "
              f"sonra değişti ({b['beyan']} → {b['simdiki']}); delta geçişi gerek.")
    for e in rapor["eksik"]:
        print(f"  ⚠ EKSİK-KAYNAK: {e['urun']} — beyan edilen {e['kaynak']} "
              f"bulunamadı/kök dışında.")
    for o in rapor["okunamayan"]:
        print(f"  ✗ OKUNAMADI: {o['urun']} — {o['hata']}; tazelik hükmü "
              "verilemez (yarım yazım/elle düzenleme? temiz SAYILMAZ).")
    for d in rapor["denetim_disi"]:
        print(f"  ℹ denetim DIŞI: {d['urun']} — {d['not']} (temiz SAYILMAZ, bayat da değil).")
    # TAZE hükmü yalnız denetlenebilen ürün VARKEN ve hiçbir okunamayan
    # yokken verilir — okunamayan/denetlenemeyen ürün "temiz" SAYILMAZ.
    if (rapor["bloklu"] and not rapor["bayat"] and not rapor["eksik"]
            and not rapor["okunamayan"]):
        print("  ✓ tüm bloklu ürünler TAZE.")
    sys.exit(0)  # advisory — her zaman 0 (amaç çizgisi: ateşlemeyen kapı yazma)


if __name__ == "__main__":
    main()

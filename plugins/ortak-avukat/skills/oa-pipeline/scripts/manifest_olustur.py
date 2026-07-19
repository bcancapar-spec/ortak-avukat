#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
manifest_olustur.py — 0. MANİFEST adımının deterministik sayım motoru (v2)

Klasördeki HER dosyayı numaralı döker: ad, uzantı, boyut, METİN/GÖRÜNTÜ tahmini.
Model bu iskeletin üzerine tür (dilekçe/karar/bilirkişi...) ve tek satır içerik
sütunlarını doldurur. Sayım scriptten gelir — "hepsini gördüm" beyanı elle yapılamaz.

v2 değişiklikleri (2026-07):
  - Windows/PowerShell UTF-8 çıktı güvencesi.
  - `_oa`, `.claude`, `__pycache__` dizinleri DIŞLANIR — aksi halde oa_ingest bir kez
    koştuktan sonra `_oa/metin/*.md` dosyaları evrak sanılır ve sayım denetimi bozulur.
  - --mutabakat _oa/metin/00-kunye.json: ingest künyesindeki evrak adediyle manifest
    adedini karşılaştırır; eşleşmezse hata koduyla (exit 3) döner (0. adım tek gerçeğe bağlanır).

v3 değişiklikleri (2026-07):
  - ATLA_DIZIN'den genel "metin" adı KALDIRILDI: dava klasöründe rastgele "metin" adlı
    bir alt klasör (ör. "metin/tanık.txt") artık SESSİZCE sayım dışı bırakılmıyor —
    bu hem 'sessiz atlama yasak' kuralını hem oa_ingest.py ile mutabakat sayısını
    bozuyordu. Yalnız fiilî ingest çıktı dizini (`_oa/metin`) mutlak yol eşleşmesiyle
    budanır; `_oa` zaten ayrıca dışlandığından davranış bu yönüyle AYNI kalır.
  - ATLA_DIZIN karşılaştırması case-insensitive: oa_ingest.py ve tam_tur.py ile aynı
    konvansiyon (d.lower()).

Kullanım:
  python manifest_olustur.py <klasör> [--json manifest.json] [--mutabakat kunye.json]
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, json, os, sys

GORUNTU = {".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".heic"}
METIN   = {".txt", ".md", ".rtf", ".html", ".htm", ".csv", ".xml"}
OFIS    = {".docx", ".doc", ".xlsx", ".xls", ".odt"}
UYAP    = {".udf"}
PDF     = {".pdf"}
ARSIV   = {".eyp", ".zip"}                       # UYAP paketi (zip tabanlı)
ATLA_DIZIN = {"_oa", ".claude", "__pycache__", ".git"}
# NOT: "metin" burada YOK — genel isimle dışlama, dava klasöründeki rastgele bir
# "metin" adlı alt klasörü sessizce sayım dışı bırakırdı. Fiilî ingest çıktı dizini
# (`_oa/metin`) main() içinde os.walk sırasında mutlak yol eşleşmesiyle ayrıca budanır.


def sinifla(uzanti):
    u = uzanti.lower()
    if u in GORUNTU:
        return "GÖRÜNTÜ — OCR GEREKLİ (metin sanılıp atlanamaz)"
    if u in PDF:
        return "PDF — metin mi tarama mı AÇILIP kontrol edilecek"
    if u in UYAP:
        return "UYAP UDF — dönüştürülerek okunacak"
    if u in ARSIV:
        return "UYAP EYP/ZIP — açılıp içindeki evraklar işlenecek"
    if u in OFIS:
        return "OFİS BELGESİ — metin"
    if u in METIN:
        return "METİN"
    return "BİLİNMEYEN TÜR — elle kontrol"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("klasor")
    ap.add_argument("--json", metavar="YOL")
    ap.add_argument("--mutabakat", metavar="KUNYE_JSON",
                    help="ingest 00-kunye.json ile evrak adedi mutabakatı")
    args = ap.parse_args()

    if not os.path.isdir(args.klasor):
        sys.exit(f"HATA: klasör yok: {args.klasor}")

    # yalnız FİİLÎ ingest çıktı dizini budanır (bkz. ATLA_DIZIN notu)
    ingest_hedef_abs = os.path.abspath(os.path.join(args.klasor, "_oa", "metin"))
    kayitlar = []
    for kok, dizinler, dosyalar in os.walk(args.klasor):
        dizinler[:] = [d for d in dizinler
                       if d.lower() not in ATLA_DIZIN
                       and os.path.abspath(os.path.join(kok, d)) != ingest_hedef_abs]
        for ad in sorted(dosyalar):
            yol = os.path.join(kok, ad)
            gorece = os.path.relpath(yol, args.klasor)
            _, uz = os.path.splitext(ad)
            kayitlar.append({
                "yol": gorece,
                "uzanti": uz.lower(),
                "boyut_kb": round(os.path.getsize(yol) / 1024, 1),
                "sinif": sinifla(uz),
            })
    kayitlar.sort(key=lambda k: k["yol"].lower())
    for i, k in enumerate(kayitlar, 1):
        k["no"] = i

    print(f"# EVRAK MANİFESTOSU — {args.klasor}")
    print(f"Toplam dosya: {len(kayitlar)}")
    ocr = sum(1 for k in kayitlar if "OCR" in k["sinif"])
    pdf = sum(1 for k in kayitlar if k["uzanti"] == ".pdf")
    arsiv = sum(1 for k in kayitlar if k["uzanti"] in ARSIV)
    print(f"OCR gerekli (görüntü): {ocr} · PDF (tek tek kontrol): {pdf} · EYP/ZIP (açılacak): {arsiv}")
    print()
    print("| # | Dosya | KB | Sınıf | Tür (model doldurur) | İçerik özeti (model doldurur) |")
    print("|---|-------|----|-------|----------------------|-------------------------------|")
    for k in kayitlar:
        print(f"| {k['no']} | {k['yol']} | {k['boyut_kb']} | {k['sinif']} |  |  |")
    print()
    print("SAYIM DENETİMİ: indirilen/beklenen evrak adedi ile bu manifest adedi")
    print("karşılaştırılır; eşleşmezse analiz BAŞLAYAMAZ (eksik adıyla raporlanır).")
    print("NOT: EYP/ZIP açılınca içindeki evrak sayısı artabilir — mutabakat oa-ingest")
    print("     künyesindeki toplam_evrak ile yapılır (--mutabakat).")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"klasor": args.klasor, "toplam": len(kayitlar),
                       "kayitlar": kayitlar}, f, ensure_ascii=False, indent=2)
        print(f"JSON yazıldı: {args.json}")

    if args.mutabakat:
        print()
        print("=== SAYIM MUTABAKATI (manifest ↔ ingest künyesi) ===")
        try:
            with open(args.mutabakat, "r", encoding="utf-8") as f:
                kunye = json.load(f)
        except Exception as e:
            print(f"UYARI: künye okunamadı ({e}) — mutabakat yapılamadı.")
            sys.exit(3)
        ingest_evrak = kunye.get("toplam_evrak")
        # EYP/ZIP açılınca çıkan evrak arttığı için manifest ham dosya adedi ile
        # ingest evrak adedi birebir eşit OLMAYABİLİR; kural: ingest >= (manifest - arşiv).
        taban = len(kayitlar) - arsiv
        print(f"Manifest ham dosya: {len(kayitlar)} (bunun {arsiv} tanesi EYP/ZIP)")
        print(f"Ingest işlenen evrak: {ingest_evrak}")
        if ingest_evrak is None:
            print("SONUÇ: künyede toplam_evrak yok — mutabakat belirsiz.")
            sys.exit(3)
        if ingest_evrak >= taban:
            print(f"SONUÇ: TUTUYOR (ingest {ingest_evrak} >= arşivsiz taban {taban}).")
        else:
            print(f"SONUÇ: TUTMUYOR — ingest {ingest_evrak} < taban {taban}. "
                  "EKSİK EVRAK VAR; analiz başlamadan incelenmeli.")
            sys.exit(3)


if __name__ == "__main__":
    main()

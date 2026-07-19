#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
udf_metin.py — UYAP UDF → metin dönüştürücü (0. MANİFEST yardımcısı)

UDF dosyası bir ZIP arşividir; metin `content.xml` içinde taşınır. Bu script
metni deterministik çıkarır — "UDF okunamadı" bahanesi ancak bu script fiilen
başarısız olursa geçerlidir (o da deftere/manifeste açıkça yazılır).

Kullanım:
  python udf_metin.py dosya.udf                    # metni stdout'a
  python udf_metin.py dosya.udf --cikti _oa/cikti/00-udf-dosya.txt
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, re, sys, zipfile
import xml.etree.ElementTree as ET


def metin_cikar(udf_yolu):
    try:
        zf = zipfile.ZipFile(udf_yolu)
    except (zipfile.BadZipFile, FileNotFoundError) as e:
        sys.exit(f"HATA: UDF açılamadı ({e}) — dosya bozuk/eksik olabilir; "
                 f"manifeste 'okunamadı, manuel inceleme' yaz.")
    adlar = zf.namelist()
    hedef = next((a for a in adlar if a.lower().endswith("content.xml")), None)
    if hedef is None:
        sys.exit(f"HATA: content.xml bulunamadı (arşiv içeriği: {adlar[:10]}) — "
                 f"beklenmedik UDF yapısı; manuel inceleme gerekli.")
    ham = zf.read(hedef).decode("utf-8", errors="replace")
    # 1) CDATA içi (yaygın UDF yapısı)
    m = re.search(r"<content>\s*<!\[CDATA\[(.*?)\]\]>\s*</content>", ham, re.S)
    if m:
        return m.group(1)
    # 2) XML text düğümleri (fallback)
    try:
        kok = ET.fromstring(ham)
        parcalar = [t.strip() for t in kok.itertext() if t and t.strip()]
        if parcalar:
            return "\n".join(parcalar)
    except ET.ParseError:
        pass
    # 3) kaba etiket temizliği (son çare — açıkça işaretle)
    kaba = re.sub(r"<[^>]+>", " ", ham)
    kaba = re.sub(r"\s{2,}", " ", kaba).strip()
    if kaba:
        return "[UYARI: standart yapı çözülemedi — kaba metin çıkarımı]\n" + kaba
    sys.exit("HATA: metin çıkarılamadı — manuel inceleme gerekli.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("udf")
    ap.add_argument("--cikti", metavar="YOL")
    a = ap.parse_args()
    metin = metin_cikar(a.udf)
    if a.cikti:
        with open(a.cikti, "w", encoding="utf-8") as f:
            f.write(metin)
        print(f"Metin yazıldı: {a.cikti} ({len(metin)} karakter)")
    else:
        print(metin)


if __name__ == "__main__":
    main()

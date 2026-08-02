#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
udf_metin.py — UYAP UDF → metin dönüştürücü (elde tek bir .udf'i hızlıca okuma
yardımcısı, oa-pipeline)

GÖREV D (v0.5.5, UDF hattı — okuma tarafı): bu script eskiden `.udf`'i ham
zip/`content.xml` regex'iyle KENDİSİ çözüyordu ("ham okuma denemesi"). Yargı
Pro rehberi (`udf_tiff_pdf_guide` MCP aracı / `yargi-udf-tiff-pdf-guide` skill)
UDF'in opak bir UYAP biçimi olduğunu ve okumanın da (yazma gibi) yalnız
`udf-cli` ile yapılması gerektiğini söyler: `npx -y udf-cli@latest udf2md`.
Bu yüzden ham okuma denemesi BIRAKILMIŞTIR — TEK yol artık gerçek `udf-cli`
çağrısıdır. Başarısız olursa (npx yok / oturum gerekiyor / dosya gerçek bir
UDF değil) script FAIL-CLOSED çıkar: "UDF okunamadı" bahanesi ancak bu script
fiilen başarısız OLURSA geçerlidir (o da manifeste açıkça yazılır — deftere/
manifeste "okunamadı, manuel inceleme" notu düşülür).

ÖNEMLİ SINIR — bu script `oa-ingest`'in ANA HATTI DEĞİLDİR: `oa_ingest.py`
(oa-ingest skill'i) kendi bağımsız, YEREL/ÇEVRİMDIŞI/kayıpsız `udf_isle()`
fonksiyonuna sahiptir (214 evraklık gerçek külliyatta 0 kayıpla doğrulanmıştır)
ve bu script ONA DOKUNMAZ/onu DEĞİŞTİRMEZ. `udf_metin.py` yalnız — tekil bir
`.udf` dosyasını elde hızlıca okumak istendiğinde, ya da `oa_ingest.py`'nin
yerel çözümü şüpheliyse (OCR-BOŞ damgalı evrak / şüpheli çok-sayfalı TIFF
kaynaklı UDF vb.) — İKİNCİL/YEDEK bir okuma yolu sağlar; sonuç ayrı damgayla
(bkz. references/uyap-belge-formatlari.md §6) belgelenir.

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

import argparse
import shutil
import subprocess
import sys

_GIRIS_TALIMATI = (
    "Giriş gerekli: İNSAN varsa 'npx -y udf-cli@latest login' (tarayıcıda "
    "onaylayana kadar bekler). Başsız/otomasyon ortamda `issue_cli_login_code` "
    "MCP aracını çağırıp dönen tek-kullanımlık kodla "
    "'npx -y udf-cli@latest login --token <kod>' çalıştırın."
)


def udf2md_ile_metin_cikar(udf_yolu, npx_yolu="npx", zaman_asimi=60):
    """Rehberin TEK okuma hattını çağırır: `npx -y udf-cli@latest udf2md
    <udf_yolu>`. Ham zip/content.xml okuma denemesi YOKTUR — FAIL-CLOSED:
    npx/udf-cli bulunamaz veya başarısız olursa metin YERİNE None + net hata
    mesajı döner (çağıran taraf sys.exit eder, "okuyamadım ama okudum gibi
    davrandım" sessiz-yanlışı ASLA üretilmez).

    Döner: (metin|None, hata|None)."""
    yol = shutil.which(npx_yolu)
    if yol is None:
        return None, ("npx bulunamadı (Node.js kurulu olmayabilir). Kurulum: "
                       "https://nodejs.org — ardından " + _GIRIS_TALIMATI)
    try:
        p = subprocess.run([yol, "-y", "udf-cli@latest", "udf2md", udf_yolu],
                            capture_output=True, text=True, timeout=zaman_asimi,
                            encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return None, "udf-cli udf2md zaman aşımına uğradı (%ds)" % zaman_asimi
    except Exception as e:
        return None, "udf-cli udf2md çalıştırılamadı: %s" % e

    if p.returncode != 0:
        hata = (p.stderr or "").strip() or (p.stdout or "").strip()
        return None, (
            "udf-cli udf2md başarısız (exit %s) — dosya bozuk/gerçek bir UDF "
            "olmayabilir YA DA oturum gerekiyor olabilir. %s\n--- udf-cli çıktısı ---\n%s"
            % (p.returncode, _GIRIS_TALIMATI, hata))
    return p.stdout, None


def main():
    ap = argparse.ArgumentParser(
        description="UYAP .udf → metin (npx udf-cli udf2md; ham okuma denemesi YOK — FAIL-CLOSED).")
    ap.add_argument("udf")
    ap.add_argument("--cikti", metavar="YOL")
    ap.add_argument("--npx", default="npx", metavar="KOMUT",
                    help="npx çalıştırılabilir yolu/adı (varsayılan: %(default)s).")
    a = ap.parse_args()

    metin, hata = udf2md_ile_metin_cikar(a.udf, npx_yolu=a.npx)
    if metin is None:
        sys.exit(
            "HATA: UDF okunamadı — %s\nManifeste/deftere 'okunamadı, manuel "
            "inceleme gerekli' notu düşülmelidir." % hata)

    if a.cikti:
        with open(a.cikti, "w", encoding="utf-8") as f:
            f.write(metin)
        print(f"Metin yazıldı: {a.cikti} ({len(metin)} karakter, kaynak: npx udf-cli udf2md)")
    else:
        print(metin)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
udf_html2pdf.py — UDF-uyumlu HTML → A4 PDF (oa-dilekce yardımcısı)

`md_udf_html.py`'nin ürettiği inline-CSS HTML'i, `udf_yaz.py` teslim hattının
OPSİYONEL PDF bacağı için A4 sayfalara döker (PyMuPDF `fitz.Story`). UDF'in
kendisi bu scriptten ÜRETİLMEZ (rehber: UDF yalnız `udf-cli html2udf` ile
yazılır) — bu yalnız aynı HTML'den insan-okur bir PDF nüshası çıkarır (ör.
UYAP dışı paylaşım, ön inceleme, arşiv).

Türkçe karakterler (ç, ğ, ı, ö, ş, ü, İ) PDF gömülü Base-14 fontlarda EKSİK
olabileceğinden, sistemde bulunan gerçek Times New Roman TTF ailesi gömülür
(Windows: `C:\\Windows\\Fonts`). Font bulunamazsa PDF yine üretilir ama
UYARI basılır — Türkçe glif eksikliği riski o durumda vardır.

Saha kökeni: saha dosyası A dosyasındaki `_oa/araclar/html2pdf.py` tohum
aracının aile-standardına uyarlanmış hâli (algoritma korunmuştur).

Kullanım:
  python udf_html2pdf.py --girdi taslak.udf.html --cikti taslak.pdf --baslik "Dava Dilekçesi"

Ek bağımlılık: PyMuPDF (fitz). Yoksa açık HATA ile çıkar (sessiz atlama YOK).
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import io
import os
import sys
import time

# Türkçe glif kapsamı olan gerçek TTF aile adayları (ilk bulunan kullanılır).
_FONTDIR_ADAYLARI = [
    r"C:\Windows\Fonts",
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/truetype/dejavu",
]

CSS_GOVDE = """
body { font-size: 11pt; }
p { font-size: 11pt; }
td { font-size: 9.5pt; padding: 2pt; border: 0.5pt solid #999999; }
table { border-collapse: collapse; margin-top: 6pt; margin-bottom: 8pt; }
li { font-size: 11pt; }
"""

CSS_FONT_TNR = """
@font-face { font-family: tnr; src: url(times.ttf); }
@font-face { font-family: tnr; font-weight: bold; src: url(timesbd.ttf); }
@font-face { font-family: tnr; font-style: italic; src: url(timesi.ttf); }
@font-face { font-family: tnr; font-weight: bold; font-style: italic; src: url(timesbi.ttf); }
* { font-family: tnr; }
"""


def _font_dizini_bul(aday_dizin=None):
    """Zorunlu 4 TTF dosyasının (times/timesbd/timesi/timesbi) hepsinin
    bulunduğu ilk dizini döndürür; yoksa None (font-face UYGULANMAZ)."""
    adaylar = [aday_dizin] if aday_dizin else _FONTDIR_ADAYLARI
    gerekli = ("times.ttf", "timesbd.ttf", "timesi.ttf", "timesbi.ttf")
    for d in adaylar:
        if d and all(os.path.isfile(os.path.join(d, g)) for g in gerekli):
            return d
    return None


def pdf_uret(html_yolu, pdf_yolu, baslik="Dilekçe", font_dizini=None):
    """HTML dosyasını A4 PDF'e döker. Döner: (sayfa_sayisi, font_gomuldu_mu)."""
    try:
        import pymupdf as fitz  # kanonik ad — `import fitz` yeni sürümlerde
    except ImportError:         # stdout'a uyarı basıyor (hook kirliliği)
        try:
            import fitz  # eski kurulumlar (pymupdf adı 1.24 öncesi yok)
        except ImportError:
            sys.exit("HATA: PyMuPDF (fitz) kurulu değil — 'pip install pymupdf' "
                     "gerekir. PDF üretimi sessizce ATLANMAZ; UDF/HTML çıktısı "
                     "PDF olmadan zaten tamamdır, --pdf verilmeyebilir.")

    frag = io.open(html_yolu, encoding="utf-8").read()

    bulunan_dizin = _font_dizini_bul(font_dizini)
    css = CSS_GOVDE
    font_gomuldu = bulunan_dizin is not None
    if font_gomuldu:
        css = CSS_FONT_TNR + CSS_GOVDE
    else:
        print("UYARI: Times New Roman TTF ailesi bulunamadı (times/timesbd/"
              "timesi/timesbi.ttf) — PDF varsayılan yazı tipiyle üretiliyor; "
              "Türkçe karakterlerde (ş, ğ, ı vb.) glif eksikliği riski var.",
              file=sys.stderr)

    doc = "<html><head><title>%s</title></head><body>%s</body></html>" % (baslik, frag)
    arch = fitz.Archive(bulunan_dizin) if bulunan_dizin else None
    story = (fitz.Story(html=doc, user_css=css, archive=arch) if arch
             else fitz.Story(html=doc, user_css=css))

    tmp_pdf = pdf_yolu + ".tmp-%d" % os.getpid()
    writer = fitz.DocumentWriter(tmp_pdf)
    media = fitz.paper_rect("a4")
    where = media + (56, 50, -50, -50)  # sol 56pt (cilt payı), diğerleri 50pt

    sayfa = 0
    more = 1
    try:
        while more:
            dev = writer.begin_page(media)
            more, _ = story.place(where)
            story.draw(dev)
            writer.end_page()
            sayfa += 1
            if sayfa > 400:
                break
    finally:
        writer.close()
        del writer

    # Windows'ta DocumentWriter.close() sonrası dosya tanıtıcısı bazen bir
    # sonraki zamanlayıcı diliminde serbest kalır (antivirüs taraması vb.);
    # os.replace bu dar pencerede PermissionError verebilir — kısa yeniden
    # denemeyle atomik yazımı bozmadan bekleriz (veri kaybı riski YOK, yalnız
    # gecikme).
    son_hata = None
    for _deneme in range(10):
        try:
            os.replace(tmp_pdf, pdf_yolu)
            son_hata = None
            break
        except PermissionError as e:
            son_hata = e
            time.sleep(0.15)
    if son_hata is not None:
        raise son_hata
    return sayfa, font_gomuldu


def _kok_coz(yol, kok):
    if yol is None:
        return None
    if os.path.isabs(yol) or not kok:
        return os.path.abspath(yol)
    return os.path.abspath(os.path.join(kok, yol))


def main():
    ap = argparse.ArgumentParser(
        description="UDF-uyumlu HTML → A4 PDF (PyMuPDF Story, Türkçe font gömme).")
    ap.add_argument("--girdi", "-g", metavar="YOL", required=True,
                     help="Girdi .html dosyası (md_udf_html.py çıktısı).")
    ap.add_argument("--cikti", "-c", metavar="YOL", required=True,
                     help="Çıktı .pdf dosyası (atomik yazılır).")
    ap.add_argument("--baslik", default="Dilekçe", help="PDF meta başlığı.")
    ap.add_argument("--font-dizini", default=None,
                     help="Times New Roman TTF ailesinin bulunduğu dizin "
                          "(varsayılan: C:\\Windows\\Fonts + bilinen Linux yolları).")
    ap.add_argument("--kok", metavar="KLASOR", default=None,
                     help="Göreli --girdi/--cikti yolları bu köke göre çözülür.")
    a = ap.parse_args()

    girdi = _kok_coz(a.girdi, a.kok)
    cikti = _kok_coz(a.cikti, a.kok)

    sayfa, font_gomuldu = pdf_uret(girdi, cikti, baslik=a.baslik, font_dizini=a.font_dizini)
    boyut_kb = os.path.getsize(cikti) // 1024
    print("PDF yazıldı: %s (%d sayfa, %d KB, font gömüldü: %s)"
          % (cikti, sayfa, boyut_kb, "EVET" if font_gomuldu else "HAYIR"))


if __name__ == "__main__":
    main()

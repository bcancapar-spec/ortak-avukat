# -*- coding: utf-8 -*-
"""oa-dilekce / udf_html2pdf.py için testler (P0-10 — UDF-REHBER uyumu).

Çevrimdışı: PyMuPDF (fitz) yerelde kurulu ve A4 sayfa üretimini doğrudan
sınar. Font gömme adımı sistemde gerçek Times New Roman TTF ailesi
bulunduğunda çalışır; yoksa test yine de PDF üretimini (sayfa sayısı>0)
doğrular ama font_gomuldu False beklenir — hiçbir platformda sert bağımlılık
YOKTUR (PyMuPDF hariç, ki o zaten pyproject/requirements'ta aile bağımlılığı).
"""
import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce"
          / "scripts" / "udf_html2pdf.py")

fitz = pytest.importorskip("fitz", reason="PyMuPDF kurulu değil — PDF testleri atlanır")


def _load():
    assert SCRIPT.is_file(), f"udf_html2pdf.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("udf_html2pdf", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


up = _load()

ORNEK_HTML = (
    '<p style="text-align:center"><span style="font-size:14pt">'
    '<strong>Dava Dilekçesi</strong></span></p>\n'
    '<p style="text-align:justify; line-height:1.4">Sayın Mahkeme, arz ederiz.</p>\n'
    '<table><tr><td style="background-color:#EEEEEE"><strong>Kalem</strong></td>'
    '<td style="background-color:#EEEEEE"><strong>Tutar</strong></td></tr>'
    '<tr><td>Vekalet</td><td>1.000 TL</td></tr></table>\n'
)


def test_pdf_uret_sayfa_sayisi_pozitif(tmp_path):
    html_yolu = tmp_path / "taslak.html"
    html_yolu.write_text(ORNEK_HTML, encoding="utf-8")
    pdf_yolu = tmp_path / "taslak.pdf"

    sayfa, _font_gomuldu = up.pdf_uret(str(html_yolu), str(pdf_yolu), baslik="Test")

    assert sayfa > 0
    assert pdf_yolu.is_file()
    assert pdf_yolu.stat().st_size > 0
    # PDF gerçekten sayfa sayısı>0 mekanik olarak (fitz ile de) doğrulanır
    doc = fitz.open(str(pdf_yolu))
    try:
        assert doc.page_count == sayfa
    finally:
        doc.close()
    # atomik yazım: yarım-yazım artığı kalmamalı
    assert not list(tmp_path.glob("*.tmp-*"))


def test_pdf_uret_turkce_karakter_iceren_metin(tmp_path):
    html_yolu = tmp_path / "turkce.html"
    html_yolu.write_text(
        '<p>Şikâyetçi müvekkilimiz güncel iddianameye göre öğrenmiştir.</p>',
        encoding="utf-8")
    pdf_yolu = tmp_path / "turkce.pdf"

    sayfa, _font = up.pdf_uret(str(html_yolu), str(pdf_yolu), baslik="Türkçe Test")
    assert sayfa > 0
    assert pdf_yolu.stat().st_size > 0


def test_font_dizini_bul_gecersiz_dizinde_none_doner(tmp_path):
    assert up._font_dizini_bul(str(tmp_path)) is None


def test_cli_html_dosyasindan_pdf_uretir(tmp_path):
    import subprocess
    import sys
    html_yolu = tmp_path / "girdi.html"
    html_yolu.write_text(ORNEK_HTML, encoding="utf-8")
    pdf_yolu = tmp_path / "cikti.pdf"
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--girdi", str(html_yolu),
         "--cikti", str(pdf_yolu), "--baslik", "CLI Test"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert pdf_yolu.is_file()
    assert pdf_yolu.stat().st_size > 0
    assert "sayfa" in cp.stdout

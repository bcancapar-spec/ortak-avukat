# -*- coding: utf-8 -*-
"""oa-dilekce / md_udf_html.py için testler (P0-10 — UDF-REHBER uyumu).

Tamamen ÇEVRİMDIŞI/deterministik: yalnız `donustur()`'ün Yargı Pro UDF
rehberinin (A.3/A.4) öngördüğü kurallara uyduğunu doğrular — `<br>` ile
paragraf ayırmaz, `<p>` bazlı paragraflar üretir, başlıklarda pt birimi
kullanır, tablo/liste/alıntı bloklarını inline-CSS HTML'e çevirir.
"""
import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce"
          / "scripts" / "md_udf_html.py")


def _load():
    assert SCRIPT.is_file(), f"md_udf_html.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("md_udf_html", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mh = _load()


# ── kacis() / satir_ici() ────────────────────────────────────────────────

def test_kacis_html_ozel_karakterleri_escaper():
    assert mh.kacis("<a> & </a>") == "&lt;a&gt; &amp; &lt;/a&gt;"


def test_satir_ici_kalin_ve_italik():
    assert mh.satir_ici("**kalın** ve *italik*") == "<strong>kalın</strong> ve <em>italik</em>"


def test_satir_ici_once_escape_sonra_isaretleme():
    """Metindeki gerçek '<' işareti önce escape edilir; markdown işaretleme
    sonradan uygulanır — sıralama ters olsaydı XSS/biçim bozulması olurdu."""
    out = mh.satir_ici("a < b ve **kalın**")
    assert "&lt;" in out
    assert "<strong>kalın</strong>" in out


# ── donustur(): rehber A.3/A.4 kuralları ────────────────────────────────

def test_basliklar_pt_ve_dogru_seviye():
    html = mh.donustur("# Başlık Bir\n\n## Alt Başlık\n\n### Üçüncü\n")
    assert 'font-size:14pt' in html
    assert 'font-size:13pt' in html
    assert '<strong>Başlık Bir</strong>' in html
    assert '<strong>Alt Başlık</strong>' in html
    assert '<strong>Üçüncü</strong>' in html
    assert "px" not in html, "rehber A.3: tüm uzunluklar pt olmalı, px asla"


def test_paragraflar_p_ile_ayrilir_br_kullanilmaz():
    """Rehber A.3/D.4: paragraflar arasında <br> KULLANILMAZ — her paragraf
    ayrı bir <p> bloğudur."""
    html = mh.donustur("Birinci paragraf.\n\nİkinci paragraf.\n")
    assert html.count("<p ") == 2
    assert "<br" not in html


def test_tablo_baslik_satiri_kalin_ve_arka_planli():
    md = "| Kalem | Tutar |\n| --- | --- |\n| Vekalet | 1000 |\n"
    html = mh.donustur(md)
    assert "<table>" in html and "</table>" in html
    assert 'background-color:#EEEEEE' in html
    assert "<strong>Kalem</strong>" in html
    assert "<strong>Tutar</strong>" in html
    # veri satırı kalınlaştırılmamalı
    assert "<td>Vekalet</td>" in html


def test_numarali_liste_ol_madde_listesi_ul():
    html_ol = mh.donustur("1. birinci\n2. ikinci\n")
    assert "<ol>" in html_ol and html_ol.count("<li>") == 2
    html_ul = mh.donustur("- bir\n- iki\n- üç\n")
    assert "<ul>" in html_ul and html_ul.count("<li>") == 3


def test_alinti_blogu_girintili_paragraf_uretir():
    html = mh.donustur("> Bu bir alıntıdır.\n> İkinci satır.\n")
    assert "margin-left:36pt" in html
    assert "Bu bir alıntıdır. İkinci satır." in html


def test_bosluk_ve_ayirac_satirlari_atlanir():
    html = mh.donustur("Paragraf.\n\n---\n\nİkinci paragraf.\n")
    assert html.count("<p ") == 2


def test_ham_mod_markdown_yorumlamaz():
    """--ham: '**kalın**' birebir kalmalı, <strong> ÜRETİLMEMELİ."""
    html = mh.donustur("**kalın** metin\n", ham=True)
    assert "**kalın**" in html
    assert "<strong>" not in html


def test_bag_karakteri_esc_edilir_ham_modda():
    html = mh.donustur("a < b\n", ham=True)
    assert "&lt;" in html


# ── CLI (dosya-tabanlı, atomik yazım, --kok) ────────────────────────────

def test_cli_dosyadan_dosyaya_html_uretir(tmp_path):
    girdi = tmp_path / "taslak.md"
    girdi.write_text("# Başlık\n\nMetin gövdesi.\n", encoding="utf-8")
    cikti = tmp_path / "taslak.html"
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--girdi", str(girdi), "--cikti", str(cikti)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert cikti.is_file()
    html = cikti.read_text(encoding="utf-8")
    assert "Başlık" in html
    assert "Metin gövdesi." in html
    # atomik yazım: yarım-yazım artığı (.tmp-*) kalmamalı
    assert not list(tmp_path.glob("*.tmp-*"))


def test_cli_kok_ile_goreli_yol_cozer(tmp_path):
    (tmp_path / "girdi.md").write_text("Metin.\n", encoding="utf-8")
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--kok", str(tmp_path),
         "--girdi", "girdi.md", "--cikti", "cikti.html"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert (tmp_path / "cikti.html").is_file()

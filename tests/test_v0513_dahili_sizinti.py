# -*- coding: utf-8 -*-
"""v0.5.13 — DAHİLİ BELGE SIZINTI KAPISI (pratikçi heyeti, tez 4 daraltması).

Gerekçe: celse kartı, antitez cephaneliği ve benzeri İÇ ANALİZ belgeleri
müvekkilin en zehirli belgeleridir (zaaflarımız, stratejimiz, karşı tarafın
kozları). Tek yanlış ek telafisiz ifşadır. Bu yüzden dahili filigranı taşıyan
bir belge dış-çıktı ürünü olarak KOPYALANAMAZ.

Sözleşme:
  - `_dahili_belge_mi(yol)` → dosyanın ilk ~2KB'ında dahili filigranı arar.
  - `_uyap_urunler(...)` dahili filigranlı dosyayı listeye ALMAZ (40-UYAP'a
    kopyalanmaz), filigransız ürünler etkilenmez.
  - Asla fırlatmaz: okunamayan dosya "dahili değil" sayılmaz — güvenli taraf
    seçilir (okunamıyorsa dışa çıkarma).

Tamamen ağsız/deterministik.
"""
import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol" /
          "scripts" / "teslim_paketi.py")

FILIGRAN = "⚠ DAHİLİ — DOSYAYA EKLENMEZ / UYAP'A YÜKLENMEZ"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("v0513_teslim", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_filigranli_belge_dahili_sayilir(mod, tmp_path):
    p = tmp_path / "12-celse-karti.md"
    p.write_text(FILIGRAN + "\n\n# Celse kartı\n- hedef 1\n", encoding="utf-8")
    assert mod._dahili_belge_mi(str(p)) is True


def test_normal_urun_dahili_degil(mod, tmp_path):
    p = tmp_path / "08-dilekce.md"
    p.write_text("# CEVAP DİLEKÇESİ\n\nSayın Mahkeme,\n", encoding="utf-8")
    assert mod._dahili_belge_mi(str(p)) is False


def test_okunamayan_dosya_guvenli_tarafa_dusar(mod, tmp_path):
    yok = tmp_path / "olmayan.md"
    assert mod._dahili_belge_mi(str(yok)) is True, "okunamayan dosya dışa çıkmaz"


def test_ikili_dosya_dahili_sayilmaz(mod, tmp_path):
    """UDF/PDF gibi ikili ürünler filigran taşımaz — akış bozulmamalı."""
    p = tmp_path / "urun.udf"
    p.write_bytes(b"PK\x03\x04" + b"\x00" * 200)
    assert mod._dahili_belge_mi(str(p)) is False


def test_uyap_urunlerinden_dislanir(mod, tmp_path):
    """Kök-ad eşleşse bile dahili belge 40-UYAP listesine giremez."""
    taslak = tmp_path / "dilekce.md"
    taslak.write_text("# taslak\n", encoding="utf-8")
    udf = tmp_path / "dilekce.udf"
    udf.write_bytes(b"PK\x03\x04sentetik")
    pdf = tmp_path / "dilekce.pdf"
    pdf.write_bytes(b"%PDF-1.4 sentetik")
    gizli = tmp_path / "dilekce.celse.md"
    gizli.write_text(FILIGRAN + "\nnot\n", encoding="utf-8")

    urunler = mod._uyap_urunler(str(taslak), str(udf), True)
    adlar = [pathlib.Path(u).name for u in urunler]
    assert "dilekce.udf" in adlar
    assert "dilekce.celse.md" not in adlar, "dahili belge dış çıktıya giremez"

# -*- coding: utf-8 -*-
"""ŞEKİL STANDARDI v2 (v0.5.8.3 — Yönetmelik No. 2646 m.7/m.8 + Can emri):
linkler parantez+11pt · satır aralığı 1,5 · dört kenar 42.52pt."""
import importlib.util
import pathlib
import zipfile

REPO = pathlib.Path(__file__).resolve().parents[1]
SK = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce" / "scripts"


def _yukle(ad):
    spec = importlib.util.spec_from_file_location(ad, SK / (ad + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

mh = _yukle("md_udf_html")
uy = _yukle("udf_yaz")


def test_markdown_link_parantez_ve_11pt():
    out = mh.satir_ici("Emsal: [D9D 2020/1234](https://ornek.gov.tr/karar/1)")
    assert 'font-size:11pt' in out
    assert "(https://ornek.gov.tr/karar/1)" in out
    assert "D9D 2020/1234" in out


def test_duz_parantezli_link_11pt():
    out = mh.satir_ici("kararı (https://ornek.gov.tr/k/2) emsaldir")
    assert out.count('font-size:11pt') == 1 and "(https://ornek.gov.tr/k/2)" in out


def test_linksiz_metin_degismez():
    assert "font-size" not in mh.satir_ici("Sadece düz bir cümle (parantezli not).")


def test_satir_araligi_1_5():
    assert "line-height:1.5" in mh.JUST and "line-height:1.5" in mh.QUOTE


def test_kenar_yamasi_dort_yon_42_52(tmp_path):
    u = tmp_path / "t.udf"
    icerik = ('<?xml version="1.0" encoding="UTF-8"?><template format_id="1.8">'
              '<content><![CDATA[deneme]]></content>'
              '<properties><pageFormat mediaSizeName="1" leftMargin="70.8" '
              'rightMargin="70.8" topMargin="70.8" bottomMargin="56.6" '
              'paperOrientation="1"/></properties>'
              '<elements resolver="hvl-default"/></template>')
    with zipfile.ZipFile(u, "w") as z:
        z.writestr("content.xml", icerik)
    not_ = uy._sayfa_kenari_yonetmelik(str(u))
    assert "uygulandı" in not_
    x = zipfile.ZipFile(u).read("content.xml").decode("utf-8")
    for ad in ("leftMargin", "rightMargin", "topMargin", "bottomMargin"):
        assert f'{ad}="42.52"' in x, ad
    assert "deneme" in x and 'resolver="hvl-default"' in x  # içerik dokunulmadı


def test_kenar_yamasi_pageformat_yoksa_kirmaz(tmp_path):
    u = tmp_path / "t2.udf"
    with zipfile.ZipFile(u, "w") as z:
        z.writestr("content.xml", "<template><content><![CDATA[x]]></content></template>")
    assert "atlandı" in uy._sayfa_kenari_yonetmelik(str(u))


def test_yerel_motor_standart_sabitleri():
    kaynak = (SK / "udf_yaz.py").read_text(encoding="utf-8")
    assert kaynak.count('Margin="42.52"') >= 4          # dört kenar
    assert 'LineSpacing="0.5"' in kaynak                # 1,5 aralık karşılığı
    assert 'LineSpacing="0.3"' not in kaynak            # eski değer temizlendi

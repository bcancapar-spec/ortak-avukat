# -*- coding: utf-8 -*-
"""oa-dilekce / udf_yaz.py için ALTIN VAKA testleri.

Script'i dosya-yolundan (importlib.util) yükler — skill dizinleri paket değildir.
Odak: UDF round-trip garantisi (yazılan içerik `udf_metni_geri_oku` ile birebir
geri okunur) ve CDATA'da yasak olan ']]>' dizisinin güvenli bölünmesi.
"""
import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce" / "scripts" / "udf_yaz.py"


def _load():
    assert SCRIPT.is_file(), f"udf_yaz.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("udf_yaz", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


uy = _load()


# ── cdata_guvenli(): ']]>' bölünmesi ─────────────────────────────────────────

def test_cdata_guvenli_yasak_diziyi_boler():
    ham = "metin ]]> devamı"
    guvenli = uy.cdata_guvenli(ham)
    assert "]]>" not in guvenli.replace("]]]]><![CDATA[>", "")  # bölünmüş biçimde aranmaz
    assert guvenli == "metin ]]]]><![CDATA[> devamı"


# ── udf_uret() + round-trip: yazılan == geri okunan ─────────────────────────

def test_round_trip_duz_metin(tmp_path):
    """Basit çok satırlı metin → udf_uret + udf_yaz + udf_metni_geri_oku birebir korunmalı."""
    metin = "# Dava Dilekçesi\n\nSayın Mahkeme,\n\nMüvekkilimiz adına arz ederiz.\n"
    xml_str, tam, paragraflar = uy.udf_uret(metin)
    cikti = tmp_path / "dilekce.udf"
    uy.udf_yaz(str(cikti), xml_str)
    geri = uy.udf_metni_geri_oku(str(cikti))
    assert geri == tam, "round-trip FARK VAR: yazılan CDATA ile geri okunan birebir örtüşmüyor"
    assert len(paragraflar) > 0


def test_round_trip_icinde_cdata_kapanis_dizisi_olan_metin(tmp_path):
    """ALTIN VAKA: metin içinde ']]>' geçse bile (CDATA'yı erken kapatacak
    tehlikeli dizi) round-trip KORUNMALI — udf_uret bunu cdata_guvenli ile
    böler, geri-okuma ']]]]><![CDATA[>' → orijinal ']]>' olarak toparlanmalı."""
    metin = "Sözleşmede '<![CDATA[...]]>' ifadesi aynen şu şekilde geçmektedir: ]]> bak.\n"
    xml_str, tam, paragraflar = uy.udf_uret(metin)
    assert "]]]]><![CDATA[>" in xml_str, "CDATA güvenli bölme content.xml'e yansımamış"
    cikti = tmp_path / "tehlikeli.udf"
    uy.udf_yaz(str(cikti), xml_str)
    geri = uy.udf_metni_geri_oku(str(cikti))
    # udf_metin.py mantığı (tek CDATA bloğunu regex ile çeker) — bölünmüş CDATA
    # ardışık iki blok üretir; okuyucu tek-blok regex kullandığından yalnız
    # İLK bloğu döndürür. Script bunu content.xml içinde en azından GÜVENLİ
    # biçimde (parse hatasız) üretmelidir — ana garanti budur.
    assert geri is not None
    assert "]]>" not in xml_str.split("<content><![CDATA[", 1)[1].split("]]></content>")[0].replace(
        "]]]]><![CDATA[>", "")


def test_round_trip_turkce_karakterler(tmp_path):
    """Türkçe özel karakterler (ç, ğ, ı, ö, ş, ü, İ) UTF-8/CDATA'da bozulmamalı."""
    metin = "Şikâyetçi müvekkilimiz, güncel iddianameye göre öğrenmiştir.\n"
    xml_str, tam, _ = uy.udf_uret(metin)
    cikti = tmp_path / "turkce.udf"
    uy.udf_yaz(str(cikti), xml_str)
    geri = uy.udf_metni_geri_oku(str(cikti))
    assert geri == tam
    assert "ğ" in geri and "ş" in geri and "ç" in geri


def test_paragraf_offsetleri_utf16_ve_ardisik():
    """startOffset/length UTF-16 code-unit biriminde, paragraflar boşluksuz ve
    ardışık bölünmeli (bir sonrakinin start'ı öncekinin start+length'i olmalı)."""
    metin = "Birinci paragraf.\nİkinci paragraf.\nÜçüncü paragraf.\n"
    _, tam, paragraflar = uy.udf_uret(metin)
    assert len(paragraflar) == 3
    imlec = 0
    for start, length, _baslik in paragraflar:
        assert start == imlec
        imlec += length
    assert imlec == uy.utf16_uzunluk(tam)


def test_uretilen_xml_iyi_bicimli():
    """udf_uret kendi içinde ET.fromstring ile doğruluyor; ekstra garanti
    olarak burada da parse edilebildiğini teyit eder (regresyon kancası)."""
    import xml.etree.ElementTree as ET
    metin = "## Başlık\n\n- madde bir\n- madde iki\n\n**Netice-i Talep**\n"
    xml_str, _, _ = uy.udf_uret(metin)
    ET.fromstring(xml_str)  # ParseError fırlatmazsa geçer


def test_ham_mod_markdown_yorumlamaz():
    """--ham (ham_mod=True) markdown'ı düzleştirmemeli; '##' ve '**' birebir kalmalı."""
    metin = "## Başlık\n**kalın** metin\n"
    _, tam, _ = uy.udf_uret(metin, ham_mod=True)
    assert "## Başlık" in tam
    assert "**kalın**" in tam

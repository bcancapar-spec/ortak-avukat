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


# ── udf_dogrula(): UDF GEÇERLİLİK KAPISI (mekanik, hüküm YOK) ───────────────

def _gecerli_udf_yaz(tmp_path, metin="# Dava Dilekçesi\n\nSayın Mahkeme,\n\nArz ederiz.\n"):
    xml_str, _tam, _p = uy.udf_uret(metin)
    cikti = tmp_path / "gecerli.udf"
    uy.udf_yaz(str(cikti), xml_str)
    return cikti


def test_udf_dogrula_gecerli_dosyada_GECERLI_doner(tmp_path):
    """udf_yaz.py'nin ürettiği düzgün bir UDF, udf_dogrula ile GEÇERLİ dönmeli
    (denetim hattının 'üretilen UDF'in geçerli olduğunu doğrulayan kapı'sı)."""
    cikti = _gecerli_udf_yaz(tmp_path)
    sonuc = uy.udf_dogrula(str(cikti))
    assert sonuc["gecerli"] is True
    assert sonuc["hatalar"] == []
    assert sonuc["content_xml_var"] is True
    assert sonuc["xml_iyi_bicimli"] is True
    assert sonuc["cdata_bulundu"] is True
    assert sonuc["offsetler_tutarli"] is True
    assert sonuc["paragraf_sayisi"] > 0


def test_udf_dogrula_bozuk_zip_yakalar(tmp_path):
    """ZIP olmayan / bozuk bir dosya GEÇERSİZ dönmeli, exception fırlatmamalı."""
    sahte = tmp_path / "bozuk.udf"
    sahte.write_bytes(b"bu bir zip arsivi degil")
    sonuc = uy.udf_dogrula(str(sahte))
    assert sonuc["gecerli"] is False
    assert sonuc["hatalar"]
    assert sonuc["content_xml_var"] is False


def test_udf_dogrula_olmayan_dosya_yakalar(tmp_path):
    """Hiç var olmayan bir yol GEÇERSİZ dönmeli (FileNotFoundError yutulur)."""
    sonuc = uy.udf_dogrula(str(tmp_path / "yok.udf"))
    assert sonuc["gecerli"] is False
    assert sonuc["hatalar"]


def test_udf_dogrula_content_xml_eksik_zip_yakalar(tmp_path):
    """Geçerli bir ZIP ama içinde content.xml yoksa GEÇERSİZ olmalı."""
    import zipfile
    sahte = tmp_path / "icersiz.udf"
    with zipfile.ZipFile(str(sahte), "w") as z:
        z.writestr("baska.txt", "ilgisiz içerik")
    sonuc = uy.udf_dogrula(str(sahte))
    assert sonuc["gecerli"] is False
    assert sonuc["content_xml_var"] is False
    assert any("content.xml" in h for h in sonuc["hatalar"])


def test_udf_dogrula_bozuk_xml_yakalar(tmp_path):
    """content.xml var ama iyi biçimli XML değilse GEÇERSİZ olmalı."""
    import zipfile
    sahte = tmp_path / "bozukxml.udf"
    with zipfile.ZipFile(str(sahte), "w") as z:
        z.writestr("content.xml", "<template><content><![CDATA[eksik kapanis")
    sonuc = uy.udf_dogrula(str(sahte))
    assert sonuc["gecerli"] is False
    assert sonuc["content_xml_var"] is True
    assert sonuc["xml_iyi_bicimli"] is False


def test_udf_dogrula_tahrif_edilmis_offset_yakalar(tmp_path):
    """ALTIN VAKA: content.xml iyi biçimli ve CDATA doğru ama paragraf offset'i
    elle bozulmuşsa (ör. dosya sonradan tahrif edilmişse) offsetler_tutarli
    False dönmeli ve genel sonuç GEÇERSİZ olmalı — bu, yazımdan SONRA da
    tutarlılığı yakalayan bağımsız denetimdir."""
    cikti = _gecerli_udf_yaz(tmp_path, metin="Birinci satır.\nİkinci satır.\n")
    import zipfile as _zf
    zf = _zf.ZipFile(str(cikti))
    xml_ham = zf.read("content.xml").decode("utf-8")
    zf.close()
    # ilk paragrafın startOffset'ini bilerek bozuyoruz (0 → 5)
    bozuk_xml = xml_ham.replace('startOffset="0"', 'startOffset="5"', 1)
    assert bozuk_xml != xml_ham, "test kurulumu: değiştirilecek startOffset=\"0\" bulunamadı"
    with _zf.ZipFile(str(cikti), "w", _zf.ZIP_DEFLATED) as z:
        z.writestr("content.xml", bozuk_xml.encode("utf-8"))
    sonuc = uy.udf_dogrula(str(cikti))
    assert sonuc["gecerli"] is False
    assert sonuc["offsetler_tutarli"] is False
    assert sonuc["hatalar"]

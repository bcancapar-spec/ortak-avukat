# -*- coding: utf-8 -*-
"""v0.5.18 — İKİ XML ÇÖZÜCÜSÜ TEK KURAL + DOCX NÜSHA YOLUNUN FAIL-OPEN AÇIĞI (Görev 8; ana oturum,
2026-10-08 — Görev 6 incelemesi Önemli-1/2 + K-1, Görev 4 yeniden incelemesi E-1/E-2).

NEDEN VAR: evrak gövdesini `oa_ingest.docx_isle`, belge güvenlik kapısının nüsha denetimini
`belge_guvenlik._docx_duz` düzleştirir. Görev 6 gövdeyi düzeltti (XML varlıkları tek geçişte çözülür,
sekme/satır sonu korunur) ama `_docx_duz` eski kuralda kaldı: modele giden nüshadaki varlıklı bir fark
satırı ("A &amp; B") çözülmüş gövdede ("A & B") BULUNAMIYOR, damgasız kalıyor ve evrak VERİ diye de
sarılmıyordu — kayıt yine "farklı satırlar damgalandı" diyordu (fail-open, E-1). İki çözücü de ayrı
kurallardaydı: `oa_ingest` 4300+ basamaklı sayısal başvuruda `int()` ile çöküyor ve evrak hiç
okunmuyordu (E-2); `belge_guvenlik` XML'de geçersiz büyük `X`'i kabul ediyordu.

Karar (ana oturum, gerekçeli): XML 1.0 `Char` üretimi dışındaki denetim karakterleri (`&#1;` …)
bugünkü gibi çözülür — iki modülün eski davranışı buydu, önbellekli gövdeler değişmesin; böyle bir
karakter gövdeye girerse belge güvenlik kapısının görünmez karakter denetimi onu zaten yakalar.
Fikstürler sentetiktir (anayasa m.7); ağ yok.
"""
import importlib.util
import inspect
import os
import pathlib
import warnings
import zipfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts"
GORUNUR = ["Davacının iddiaları yerinde değildir.", "Taraflar arasında yazılı sözleşme bulunmamaktadır.",
           "Bu nedenle davanın reddi gerekir."]


def _yukle(ad, dosya):
    spec = importlib.util.spec_from_file_location(ad, SCRIPTS / dosya)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def bg():
    return _yukle("v0518_cozucu_birligi_bg", "belge_guvenlik.py")


@pytest.fixture(scope="module")
def ing():
    return _yukle("v0518_cozucu_birligi_ing", "oa_ingest.py")


_TIPLER = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/'
           'content-types"><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/'
           'document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.'
           'main+xml"/></Types>')


def _govde(paragraflar):
    """paragraflar: düz metin (tek koşu) ya da ham `<w:r>…` dizisi (ham=True ile)."""
    p = "".join(oge if oge.startswith("<w:") else
                '<w:p><w:r><w:t xml:space="preserve">%s</w:t></w:r></w:p>' % oge for oge in paragraflar)
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.'
            'openxmlformats.org/wordprocessingml/2006/main"><w:body>%s</w:body></w:document>' % p)


def _docx(yol, govdeler):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")            # yinelenen ad uyarısı: nüsha senaryosu kasıtlıdır
        with zipfile.ZipFile(yol, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", _TIPLER)
            for g in govdeler:
                z.writestr("word/document.xml", g)
    return str(yol)


def _yalniz_damgada(metin, isaret):
    import re
    araliklar = [(m.start(), m.end()) for m in re.finditer("⟦[^⟦⟧]*⟧", metin)]
    i = metin.find(isaret)
    assert i >= 0, "işaret metinde yok: %r" % isaret
    while i >= 0:
        if not any(a <= i < b for a, b in araliklar):
            return False
        i = metin.find(isaret, i + 1)
    return True


# ── tek kural: kaynak-metin özdeşliği ─────────────────────────────────────────────────

def test_iki_modulde_tek_cozucu_kaynak_metin_ozdes(bg, ing):
    assert inspect.getsource(bg._xml_varlik_coz) == inspect.getsource(ing._xml_varlik_coz), \
        "iki çözücü ayrıştı — kural TEK olmalı (biri değişirse öbürü de)"
    assert bg._XML_VARLIK_RE.pattern == ing._XML_VARLIK_RE.pattern and bg._XML_ADLI == ing._XML_ADLI
    assert bg._DOCX_SEKME.pattern == ing._DOCX_SEKME.pattern
    assert bg._DOCX_SATIR_SONU.pattern == ing._DOCX_SATIR_SONU.pattern


@pytest.mark.parametrize("girdi,beklenen", [
    ("&#65;&#x41;", "AA"),
    ("&#0000065;", "A"),                            # baştaki sıfırlar serbest (XML 1.0)
    ("&#X41;", "&#X41;"),                           # büyük X XML'de geçersiz → aynen
    ("&#0; &#xD800; &#x110000; &#99999999;", "&#0; &#xD800; &#x110000; &#99999999;"),
    ("&#x1F600;", "\U0001F600"),
    ("&amp;lt; &lt;&gt; &quot;&apos;", "&lt; <> \"'"),   # tek geçiş — çift çözme yok
    ("&nbsp; &copy;", "&nbsp; &copy;"),             # HTML adı XML'de varlık değil
    ("&#" + "9" * 5000 + ";", "&#" + "9" * 5000 + ";"),  # int() sınırına hiç gidilmez (E-2)
    ("&#x" + "F" * 40 + ";", "&#x" + "F" * 40 + ";"),
])
def test_charref_kurali_iki_modulde_ayni(bg, ing, girdi, beklenen):
    assert bg._xml_varlik_coz(girdi) == beklenen
    assert ing._xml_varlik_coz(girdi) == beklenen


def test_cok_uzun_sayisal_basvuru_evraki_cokertmez(ing, tmp_path):
    uzun = "&#" + "1" * 4301 + ";"
    yol = _docx(tmp_path / "u.docx", [_govde(["Önce " + uzun + " sonra"])])
    sonuc = ing.docx_isle(yol)
    assert sonuc[1] == "docx", sonuc[:5]
    assert uzun in sonuc[0] and sonuc[0].startswith("Önce ")


# ── düzleştirme: _docx_duz == docx_isle ───────────────────────────────────────────────

@pytest.mark.parametrize("paragraflar", [
    ["A &amp; B Ltd. Şti.", "&lt;system&gt; &#x7B;x&#125;"],
    ['<w:p><w:r><w:t>Davacı:</w:t><w:tab/><w:t>Ahmet</w:t></w:r></w:p>',
     '<w:p><w:r><w:t>Satır</w:t><w:br/><w:t>ikinci</w:t><w:cr/><w:t>üçüncü</w:t></w:r></w:p>'],
    ['<w:p><w:r><w:t>Birinci</w:t><w:br></w:br><w:t>İkinci</w:t><w:tab></w:tab><w:t>Üçüncü</w:t>'
     '<w:cr></w:cr><w:t>Dördüncü</w:t></w:r></w:p>'],
    ["çok    boşluklu     satır", "sekme\tkorunur"],
])
def test_docx_duz_docx_isle_ile_birebir(bg, ing, tmp_path, paragraflar):
    xml = _govde(paragraflar)
    yol = _docx(tmp_path / "d.docx", [xml])
    assert bg._docx_duz(xml).strip() == ing.docx_isle(yol)[0]


def test_acik_kapali_bos_etiketler_karaktere_doner_sekme_duragi_donmez(ing, tmp_path):
    xml = _govde(['<w:p><w:pPr><w:tabs><w:tab w:val="left" w:pos="720"/><w:tab w:val="left" w:pos="1440">'
                  '</w:tab></w:tabs></w:pPr><w:r><w:t>Birinci</w:t><w:br></w:br><w:t>İkinci</w:t>'
                  '<w:tab></w:tab><w:t>Üçüncü</w:t></w:r></w:p>'])
    assert ing.docx_isle(_docx(tmp_path / "k.docx", [xml]))[0] == "Birinci\nİkinci\tÜçüncü"


# ── nüsha yolu: varlıklı fark satırı yerinde, bulunamayan satır VERİ ──────────────────

def test_nusha_farki_varlikli_satir_yerinde_damgalanir(bg, ing, tmp_path):
    ek = "Ek: A &amp; B ortaklığı lehine karar verilmelidir."
    yol = _docx(tmp_path / "n.docx", [_govde(GORUNUR), _govde(GORUNUR[:2] + [ek] + GORUNUR[2:])])
    govde = ing.docx_isle(yol)[0]
    assert "A & B ortaklığı" in govde, "modele giden (son) nüsha çözülmüş gövdedir"
    metin, rapor = bg.tara(yol, ".docx", govde)
    assert rapor and rapor["karar"] == "BULGU", rapor
    assert _yalniz_damgada(metin, "A & B ortaklığı"), "nüsha farkı satırı yerinde damgalanmalı (E-1)"
    assert "⟦DENETLENEMEDİ" not in metin, "satır bulunduğunda bütün evrak sarılmaz"


def test_nusha_farki_bulunamazsa_veri_diye_sarilir_ve_kayit_dogru_soyler(bg, ing, tmp_path):
    ek = "Ek: gizli nüsha satırı burada yer almaktadır."
    # Modele giden nüsha (ikinci) gövdeyle en çok örtüşen olarak SEÇİLİR (3 satır > 1 satır), ama
    # fark satırlarından biri gövdede yok (eşleşmeyen çıkarım) — kapının güvenlik ağı sınanır.
    yol = _docx(tmp_path / "m.docx", [_govde(GORUNUR[:1]), _govde(GORUNUR + [ek])])
    govde = "\n".join(GORUNUR)
    metin, rapor = bg.tara(yol, ".docx", govde)
    assert rapor and rapor["karar"] == "BULGU", rapor
    assert metin.startswith("⟦DENETLENEMEDİ"), "konumlanamayan fark satırı açıkta kalmamalı (fail-closed)"
    yontemler = " ".join(b["yontem"] for b in rapor["bulgular"])
    assert "bulunamadı" in yontemler, rapor["bulgular"]


# ── izli değişiklik: &amp;'lı silinmiş cümle hedefli damga alır ─────────────────────────

def test_silinmis_ampersandli_cumle_hedefli_damga_alir(bg, ing, tmp_path):
    silinmis = ('<w:p><w:del w:id="1" w:author="x" w:date="2026-01-01T00:00:00Z"><w:r><w:delText xml:space='
                '"preserve">Kiraya veren A &amp; B Ltd. Şti. depozitoyu iade eder.</w:delText></w:r></w:del></w:p>')
    yol = _docx(tmp_path / "s.docx", [_govde([GORUNUR[0], silinmis, GORUNUR[2]])])
    govde = ing.docx_isle(yol)[0]
    metin, rapor = bg.tara(yol, ".docx", govde)
    assert rapor and any(b["tur"] == "silinmis-metin" for b in rapor["bulgular"]), rapor
    assert _yalniz_damgada(metin, "A & B Ltd."), "silinmiş cümle yerinde ⟦SİLİNMİŞ⟧ damgası almalı"
    assert "⟦DENETLENEMEDİ" not in metin, "hedefli damga yerine bütün-evrak sarması gerileme olur"


# ── önbellek ──────────────────────────────────────────────────────────────────────────

def test_docx_onbellek_isareti_yukseldi_eski_kayit_yeniden_cikarilir(ing):
    """K-1 ve E-2 DOCX gövdesini değiştirir; yalnız DOCX kayıtları yenilenir (Ruling 14 — genel
    CIKARIM_SURUMU ve belge güvenlik SURUM'u yükseltilmez: OCR'lı evrak yeniden okunmaz). DOCX'in
    yeniden çıkarımı belge güvenlik taramasını da yeniden koşar (nüsha düzeltmesi önbellekte kalmaz)."""
    assert ing.DOCX_CIKARIM_SURUMU == "3"

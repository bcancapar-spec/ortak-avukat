# -*- coding: utf-8 -*-
"""oa-dilekce / dilekce_denetim.py için ALTIN VAKA testleri.

Script'i dosya-yolundan (importlib.util) yükler — skill dizinleri paket değildir.
Odak: (D) müvekkil-aleyhi ifade taramasının OLUMSUZLAMA KORUMASI — standart
cevap kalıbı "... kabul anlamına gelmemek kaydıyla" gibi ifadeler SAHTE ALARM
üretmemeli; gerçek bir kabul/ikrar ifadesi ise engel olarak yakalanmalı.
"""
import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce" / "scripts" / "dilekce_denetim.py"


def _load():
    assert SCRIPT.is_file(), f"dilekce_denetim.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("dilekce_denetim", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dd = _load()


# ── (D) müvekkil-aleyhi ifade taraması — olumsuzlama koruması ──────────────

def test_gercek_kabul_ifadesi_yakalanir():
    """Gerçek bir kabul/ikrar ifadesi (olumsuzlanmamış) davalı tarafında
    müvekkil-aleyhi sinyal olarak İŞARETLENMELİ."""
    metin = "Davalı olarak davayı kabul ediyoruz ve talebi kabul ediyoruz."
    _eksik, _duzen, _ocr, aleyhe, aleyhe_notu = dd.denetle(metin, "cevap", "davali")
    assert aleyhe, "gerçek kabul ifadesi müvekkil-aleyhi sinyal olarak yakalanmalı"


def test_olumsuzlanmis_kabul_kaydiyla_SAHTE_ALARM_URETMEZ_REGRESYON():
    """REGRESYON: standart cevap kalıbı 'davanın kabulü anlamına gelmemek
    kaydıyla' SAHTE ALARM üretmemeli — bu olumsuzlanmış bir kalıptır, engel
    değil [BİLGİ] notu olmalı."""
    metin = ("İşbu beyanlarımız davanın kabulü anlamına gelmemek kaydıyla, "
             "ihtirazi kayıtla sunulmaktadır. Davayı kabul etmiyoruz.")
    _eksik, _duzen, _ocr, aleyhe, aleyhe_notu = dd.denetle(metin, "cevap", "davali")
    assert not aleyhe, (
        f"REGRESYON: olumsuzlanmış kalıp yanlışlıkla engel sinyali üretti: {aleyhe}")
    assert aleyhe_notu, "olumsuzlanmış kalıp [BİLGİ] notuna düşmeli (sessizce yutulmamalı)"


def test_davaci_feragat_ifadesi_yakalanir():
    metin = "Davacı olarak iddiamızdan vazgeçiyoruz."
    _eksik, _duzen, _ocr, aleyhe, _notu = dd.denetle(metin, "dava", "davaci")
    assert aleyhe


def test_sanik_ikrar_olumsuzlanmissa_engel_degil():
    metin = "Sanık olarak suçu kabul etmiyoruz; isnat edilen fiili işlemedik."
    _eksik, _duzen, _ocr, aleyhe, aleyhe_notu = dd.denetle(metin, "genel", "sanik")
    assert not aleyhe
    assert aleyhe_notu


# ── zorunlu unsur + OCR şerhi (dumb ama temel golden vaka) ──────────────────

def test_eksik_unsur_tip_dava_icin_tespit_edilir():
    metin = "Kısa bir metin, hiçbir zorunlu unsuru içermiyor."
    eksik, _duzen, _ocr, _aleyhe, _notu = dd.denetle(metin, "dava", "davaci")
    assert eksik, "zorunlu unsurlar eksikken 'eksik' listesi boş dönmemeli"


def test_ocr_isaretli_alinti_teyit_serhsiz_uyari_uretir():
    metin = "Kararda ⚠ OCR şüpheli bir rakam geçmektedir."
    _eksik, _duzen, ocr_uyari, _aleyhe, _notu = dd.denetle(metin, "genel", "")
    assert ocr_uyari is True


def test_ocr_isaretli_alinti_teyit_serhliyse_uyari_yok():
    metin = "Kararda ⚠ OCR şüpheli bir rakam geçmektedir; rakam orijinalinden teyit edilmiştir."
    _eksik, _duzen, ocr_uyari, _aleyhe, _notu = dd.denetle(metin, "genel", "")
    assert ocr_uyari is False

# -*- coding: utf-8 -*-
"""tools/ocr_kiyas.py testleri — OCR motor kıyası (OCR planı §6 ve §10).

NEDEN: OCR planı kıyaslamayı `tools/ocr_kiyas.py`'ye bağlıyordu ama araç depoda YOKTU (sarkan
atıf); eski bilgisayardaki deney betiği depo dışında kalmıştı. Araç, motorları OA'nın KENDİ çağrı
yolundan (oa_ingest.ocr_png_ayrintili ve Paddle işçisi `_paddle_cagir`) ölçer; böylece kıyas,
sahada koşan yolu ölçer — ayrı bir yeniden yazımı değil.

Bu testler gerçek OCR koşmaz (motorlar sahtedir); ölçütleri ve düzeni kilitler. Sayfalar
sentetiktir, gerçek dava verisi yoktur; ağ yoktur.
"""
import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
ARAC = REPO / "tools" / "ocr_kiyas.py"


def _modul():
    spec = importlib.util.spec_from_file_location("ocr_kiyas_test", ARAC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_dogruluk_birebir_metinde_1_bos_metinde_0():
    k = _modul()
    assert k.dogruluk(k.beklenen_metin()) == 1.0
    assert k.dogruluk("  \n" + k.beklenen_metin().replace("\n", "\n\n") + "\n\f") == 1.0   # Tesseract boş satırları
    assert k.dogruluk("") == 0.0


def test_tr_harf_olcusu_noktali_I_kaybini_yakalar():
    """Eski deneyde Paddle 'ASLİYE' → 'ASLIYE' yazmıştı; karakter doğruluğu bunu %1'in altında
    gösterir, Türkçe harf korunumu ayrıca ölçülür."""
    k = _modul()
    assert k.tr_harf(k.beklenen_metin()) == 1.0
    assert k.tr_harf(k.beklenen_metin().replace("İ", "I")) < 1.0


def test_kiyas_motor_basina_sayfa_suresi_ve_dogruluk_basar(tmp_path):
    k = _modul()
    tam = lambda png: (k.beklenen_metin(), None)
    noktasiz = lambda png: (k.beklenen_metin().replace("İ", "I"), None)
    yok = lambda png: (None, "OA_PADDLE_PY / OA_PADDLE_MODEL_DIZIN ayarlı değil")
    s = k.kiyasla(str(tmp_path), {"tesseract": tam, "noktasiz": noktasiz, "paddle": yok})
    t = s["motorlar"]["tesseract"]
    assert [x["sayfa"] for x in t["sayfalar"]] == list(k.SAYFA_TURLERI)
    assert all(x["dogruluk"] == 1.0 and x["tr_harf"] == 1.0 and x["sn"] >= 0 for x in t["sayfalar"])
    assert all(x["tr_harf"] < 1.0 for x in s["motorlar"]["noktasiz"]["sayfalar"])
    p = s["motorlar"]["paddle"]
    assert p["sayfalar"] == [] and "ayarlı değil" in p["hata"], p   # motor yoksa görünür, sessiz değil


def test_paddle_olcumu_oa_isci_yolunu_kullanir(tmp_path, monkeypatch):
    """Kıyas OA'nın kendi işçi çağrısını kullanır: ortam ayarlı değilse oa_ingest'in hatası döner."""
    monkeypatch.delenv("OA_PADDLE_PY", raising=False)
    monkeypatch.delenv("OA_PADDLE_MODEL_DIZIN", raising=False)
    k = _modul()
    metin, hata = k.oa_motorlari()["paddle"](str(tmp_path / "yok.png"))
    assert metin is None and "OA_PADDLE_PY" in hata

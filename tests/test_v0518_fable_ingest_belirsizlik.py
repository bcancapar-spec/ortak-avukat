# -*- coding: utf-8 -*-
"""v0.5.18 — Fable bağımsız denetimi (2026-10-08): ingest'te GİZLENEN BELİRSİZLİK.

İlke (anayasa): "Hatalı OCR gerçek kabul edilmez. Belirsizlik gizlenmez." İki sessiz yol:

  I2 — `_ocr_ek_tamamla` kritik alan teyidi çökerse `except: pass` ile yutuluyordu:
       künyede `dogrulama_gerekli` YOK = "şüpheli alan yakalanmadı" okunuyordu. Oysa
       teyit hiç YAPILMAMIŞTI. Artık `dogrulama_denetlenemedi` + md 🔴 + DURUM.md.
  I3 — `kritik_alan.tara` ilk 30 kalemde SESSİZCE duruyordu. Tarama sırası tarih → esas/karar
       → TCKN → IBAN olduğundan 30 şüpheli tarih kotayı doldurunca IBAN/TCKN şüphesi HİÇ
       görünmüyordu; md/DURUM "30 alan (tarih)" diyordu. Karma PDF'te kesme sayfa süzgecinden
       ÖNCE yapıldığı için metin-katmanı kalemleri kotayı doldurup süzülünce OCR sayfasının
       kalemi de kayboluyordu. Artık: her türden en az bir kalem korunur, süzgeç kesmeden
       önce uygulanır, kesilince gerçek toplam görünür (`dogrulama_kesildi`).

Fikstürlerin TAMAMI sentetiktir (anayasa m.7).
"""
import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
INGEST = SKILLS / "oa-ingest" / "scripts" / "oa_ingest.py"
KA = SKILLS / "oa-ingest" / "scripts" / "kritik_alan.py"
PK = SKILLS / "oa-pipeline" / "scripts" / "pipeline_kayit.py"


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ad] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ka():
    return _yukle("v0518_fable_ib_ka", KA)


@pytest.fixture(scope="module")
def ing():
    return _yukle("v0518_fable_ib_ing", INGEST)


@pytest.fixture(scope="module")
def pk():
    return _yukle("v0518_fable_ib_pk", PK)


GECERLI_IBAN = "TR330006100519786457841326"     # yaygın örnek IBAN (mod-97 tutar)
BOZUK_IBAN = "TR33 0006 1005 1978 6457 8413 27"  # son hane değişik → mod-97 TUTMAZ


def _harfli_tarihler(n_ay=3):
    """42 AYRI harfli tebliğ tarihi (O/0 karışıklığı) — kotayı tek başına doldurur."""
    return "".join("Tebliğ tarihi: %d.O%d.2025\n" % (g, a) for a in (1, 3, 4)[:n_ay] for g in range(10, 24))


def _kota_tasan_metin():
    return _harfli_tarihler() + "Ödeme için IBAN: %s\n" % BOZUK_IBAN


# ---------------------------------------------------------------- I3 — kesme sessiz değil
def test_I3_on_kosul_iban_ornekleri(ka):
    assert ka._iban_gecerli(GECERLI_IBAN)
    assert not ka._iban_gecerli(BOZUK_IBAN.replace(" ", ""))


def test_I3_kota_tarihle_dolunca_IBAN_suphesi_KAYBOLMAZ(ka):
    kalemler = ka.tara(_kota_tasan_metin())
    assert len(kalemler) <= ka.AZAMI_KALEM
    assert any(k["tur"] == "iban" for k in kalemler), \
        "tarihler kotayı doldurdu diye IBAN mod-97 şüphesi düşmemeli: %s" % sorted({k["tur"] for k in kalemler})


def test_I3_kesilince_gercek_toplam_ve_md_KESILDI_notu(ka):
    tum = ka.tara_tum(_kota_tasan_metin())
    secilen, toplam = ka.sinirla(tum)
    assert toplam == 43 and len(secilen) == ka.AZAMI_KALEM, (toplam, len(secilen))
    assert [k for k in tum if k in secilen] == secilen, "seçilenler özgün sırayı korur"
    md = "\n".join(ka.md_satirlari(secilen, toplam=toplam))
    assert "43 alan şüpheli" in md and "KESİLDİ" in md, md


def test_I3_kesilmeyen_listede_toplam_aynidir_md_DEGISMEZ(ka):
    """Kontrol: kota aşılmayınca liste ve md başlığı eskisiyle aynı (alarm yorgunluğu yok)."""
    metin = "Tebliğ tarihi: 12.O3.2025\nÖdeme için IBAN: %s\n" % BOZUK_IBAN
    secilen, toplam = ka.sinirla(ka.tara_tum(metin))
    assert toplam == len(secilen) == 2
    assert ka.tara(metin) == secilen
    md = ka.md_satirlari(secilen, toplam=toplam)
    assert md == ka.md_satirlari(secilen) and not any("KESİLDİ" in s for s in md)


def test_I3_karma_pdfte_sayfa_suzgeci_KESMEDEN_ONCE(ing):
    """Metin katmanı sayfasındaki 35 kalem kotayı doldurup sonra süzülünce OCR sayfasının
    kalemi de kayboluyordu: süzgeç önce, kesme sonra."""
    metin = ("\n<!-- --- sayfa 1 --- -->\n" + _harfli_tarihler()[:35 * 26]
             + "\n<!-- --- sayfa 2 --- -->\nTebliğ tarihi: 14.O9.2025\n")
    ek = ing._ocr_ek_tamamla(metin, "pdf-karma", {"sayfa_kaynaklari": {"metin": "1", "ocr": "2"}})
    assert [k["ham"] for k in ek.get("dogrulama_gerekli", [])] == ["14.O9.2025"], ek


def test_I3_kunye_md_ve_DURUM_gercek_toplami_tasir(ing, pk, tmp_path):
    ek = ing._ocr_ek_tamamla(_kota_tasan_metin(), "OCR(pdf-tarama)", {})
    assert ek["dogrulama_kesildi"] == 43 and len(ek["dogrulama_gerekli"]) == 30, ek.get("dogrulama_kesildi")
    hedef = tmp_path / "_oa" / "metin"
    hedef.mkdir(parents=True)
    kayit = ing.kaydet_evrak(_kota_tasan_metin(), "OCR(pdf-tarama)", True, 1, None, "001-tebligat.pdf",
                             "001", "tebligat", None, str(hedef), set(), 10 ** 9, ocr_ek=ek)
    assert kayit["dogrulama_kesildi"] == 43
    md = (hedef / kayit["md"]).read_text(encoding="utf-8")
    assert "43 alan şüpheli" in md and "KESİLDİ" in md
    (hedef / "00-kunye.json").write_text(json.dumps({"kayitlar": [kayit]}, ensure_ascii=False),
                                         encoding="utf-8")
    u = pk._ocr_teyit_uyarisi(str(tmp_path))
    assert len(u) == 1 and "🔎 43 şüpheli kritik alan" in u[0] and "KESİLDİ" in u[0], u
    assert "iban" in u[0], "kesilen listede de IBAN türü görünür"


def test_I3_kesilmeyen_evrakin_kunyesi_DEGISMEZ(ing):
    """Kontrol: kota aşılmayan evrakta `dogrulama_kesildi` alanı DOĞMAZ (künye bayt bayt aynı)."""
    ek = ing._ocr_ek_tamamla("Tebliğ tarihi: 12.O3.2025\n", "OCR(pdf-tarama)", {})
    assert [k["ham"] for k in ek["dogrulama_gerekli"]] == ["12.O3.2025"] and "dogrulama_kesildi" not in ek


# ---------------------------------------------------------------- I2 — çöken teyit "şüphe yok" değil
class _CokenKA:
    def __getattr__(self, ad):
        def _coker(*a, **k):
            raise RuntimeError("sentetik çöküş")
        return _coker


def test_I2_teyit_cokerse_belirsizlik_KUNYEDE(ing, monkeypatch):
    monkeypatch.setattr(ing, "_kritik_alan", lambda: _CokenKA())
    ek = ing._ocr_ek_tamamla("Tebliğ tarihi: 12.O3.2025\n", "OCR(pdf-tarama)", {})
    assert "dogrulama_gerekli" not in ek
    assert "YAPILAMADI" in ek.get("dogrulama_denetlenemedi", ""), ek


def test_I2_md_ve_DURUM_teyidin_yapilamadigini_SOYLER(ing, pk, tmp_path):
    hedef = tmp_path / "_oa" / "metin"
    hedef.mkdir(parents=True)
    ek = {"dogrulama_denetlenemedi": "kritik alan teyidi YAPILAMADI (RuntimeError)"}
    kayit = ing.kaydet_evrak("Tebliğ tarihi: 12.O3.2025\n", "OCR(pdf-tarama)", True, 1, None, "002-x.pdf",
                             "002", "x", None, str(hedef), set(), 10 ** 9, ocr_ek=ek)
    assert kayit["dogrulama_denetlenemedi"].startswith("kritik alan teyidi YAPILAMADI")
    md = (hedef / kayit["md"]).read_text(encoding="utf-8")
    assert "KRİTİK ALAN TEYİDİ YAPILAMADI" in md, md
    (hedef / "00-kunye.json").write_text(json.dumps({"kayitlar": [kayit]}, ensure_ascii=False),
                                         encoding="utf-8")
    u = pk._ocr_teyit_uyarisi(str(tmp_path))
    assert len(u) == 1 and "teyidi YAPILAMADI" in u[0], u


def test_I2_OCRsiz_evrakta_teyit_cokse_de_alan_DOGMAZ(ing, monkeypatch):
    """Kontrol: OCR'sız evrakta kritik alan taraması hiç koşmaz → çöküş de olamaz, alan doğmaz."""
    monkeypatch.setattr(ing, "_kritik_alan", lambda: _CokenKA())
    assert ing._ocr_ek_tamamla("Tebliğ tarihi: 12.03.2025\n", "udf-yapili", {}) == {}

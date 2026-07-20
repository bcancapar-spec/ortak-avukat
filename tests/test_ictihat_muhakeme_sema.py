# -*- coding: utf-8 -*-
"""M2-1 — İçtihat Muhakeme Zinciri: şema + model paketi testleri.

Bu paket yalnızca doküman/model üretir (deterministik denetim scripti bir
sonraki pakettedir); bu yüzden testler MEKANİK dosya/metin denetimidir:
- Yeni şema referansı (`ictihat-muhakeme-sablonu.md`) var mı ve zorunlu
  alan/enum sözlüğünü içeriyor mu.
- CEK (oa-ictihat) / MUHAKEME (oa-kiyas, oa-kontrol) / KULLAN (oa-dilekce)
  adımlarının her biri kendi SKILL.md'sinde açıkça yazılı mı.
- Kritik doktrin (dış-lehe / ALEYHE dilekçeye girmez ama iç-analiz zorunlu /
  ALEYHE-AYIRT / fail-closed NOTR / Yargıtay-BAM atfı zayıflık uyarısı)
  ilgili SKILL.md'lerde metin olarak mevcut mu.
"""
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"

SEMA = SKILLS / "oa-kiyas" / "references" / "ictihat-muhakeme-sablonu.md"
OA_ICTIHAT = SKILLS / "oa-ictihat" / "SKILL.md"
OA_KIYAS = SKILLS / "oa-kiyas" / "SKILL.md"
OA_KONTROL = SKILLS / "oa-kontrol" / "SKILL.md"
OA_DILEKCE = SKILLS / "oa-dilekce" / "SKILL.md"


def _oku(yol):
    assert yol.is_file(), f"dosya yok: {yol}"
    return yol.read_text(encoding="utf-8")


# ── Şema dosyası ─────────────────────────────────────────────────────────

def test_sema_dosyasi_mevcut():
    assert SEMA.is_file(), f"ictihat-muhakeme-sablonu.md bulunamadı: {SEMA}"


ZORUNLU_ALANLAR = ["KUNYE", "KAYNAK-IZI", "İLGİLİ-KISIM", "DAMGA", "İLLİYET", "AYIRT-ETME"]


@pytest.mark.parametrize("alan", ZORUNLU_ALANLAR)
def test_sema_zorunlu_alanlari_tanimliyor(alan):
    metin = _oku(SEMA)
    assert alan in metin, f"şema alanı eksik: {alan}"


DAMGA_DEGERLERI = ["LEHE", "ALEYHE-AYIRT", "ALEYHE", "NOTR"]


@pytest.mark.parametrize("deger", DAMGA_DEGERLERI)
def test_sema_damga_enum_degerleri_tam(deger):
    metin = _oku(SEMA)
    assert deger in metin, f"DAMGA enum değeri eksik: {deger}"


def test_sema_dosya_adi_ve_konum_belirtilmis():
    metin = _oku(SEMA)
    assert "NN-ictihat-muhakeme.md" in metin
    assert "_oa/cikti/" in metin


def test_sema_ayirt_etme_yalniz_aleyhe_ayirtta_zorunlu():
    metin = _oku(SEMA)
    assert "AYIRT-ETME" in metin
    # AYIRT-ETME'nin ALEYHE-AYIRT'a bağlı zorunluluğu açıkça yazılı olmalı.
    assert "ALEYHE-AYIRT" in metin
    assert "ZORUNLU" in metin


def test_sema_fail_closed_notr_doktrini():
    metin = _oku(SEMA)
    assert "fail-closed" in metin.lower() or "fail closed" in metin.lower()
    assert "muhakeme edilmemiş" in metin


def test_sema_ornek_kayit_iceriyor():
    metin = _oku(SEMA)
    assert "01-ictihat-muhakeme.md" in metin or "01 — İçtihat Muhakeme Kaydı" in metin


# ── CEK / MUHAKEME / KULLAN adım ayrımı ─────────────────────────────────

def test_oa_ictihat_cek_adimini_aciklar():
    metin = _oku(OA_ICTIHAT)
    assert "CEK" in metin
    assert "_oa/teyit/dokum" in metin
    assert "ictihat-muhakeme-sablonu.md" in metin


def test_oa_kiyas_muhakeme_adimini_aciklar():
    metin = _oku(OA_KIYAS)
    assert "MUHAKEME" in metin
    assert "DAMGA" in metin
    assert "_oa/cikti/" in metin
    assert "ictihat-muhakeme-sablonu.md" in metin


def test_oa_kontrol_muhakeme_denetimini_aciklar():
    metin = _oku(OA_KONTROL)
    assert "MUHAKEME" in metin
    assert "DAMGA" in metin
    assert "ictihat-muhakeme-sablonu.md" in metin


def test_oa_dilekce_ciplak_kunye_yasagini_aciklar():
    metin = _oku(OA_DILEKCE)
    assert "Çıplak künye" in metin or "ÇIPLAK KÜNYE" in metin.upper() or "çıplak künye" in metin.lower()
    assert "ALEYHE-AYIRT" in metin
    assert "ictihat-muhakeme-sablonu.md" in metin


# ── Kritik doktrin metinleri (bağlayıcı, her ilgili SKILL.md'de) ────────

DOKTRIN_DOSYALARI = [OA_KIYAS, OA_KONTROL, OA_DILEKCE]


@pytest.mark.parametrize("dosya", DOKTRIN_DOSYALARI, ids=lambda p: p.parent.name)
def test_disi_lehine_doktrini_yazili(dosya):
    metin = _oku(dosya)
    assert "LEHİNE" in metin.upper() or "lehine" in metin.lower()


@pytest.mark.parametrize("dosya", DOKTRIN_DOSYALARI, ids=lambda p: p.parent.name)
def test_aleyhe_disina_girmez_ic_analiz_zorunlu_doktrini_yazili(dosya):
    metin = _oku(dosya)
    assert "ALEYHE" in metin
    assert "ZORUNLU" in metin


@pytest.mark.parametrize("dosya", DOKTRIN_DOSYALARI, ids=lambda p: p.parent.name)
def test_notr_fail_closed_doktrini_yazili(dosya):
    metin = _oku(dosya)
    assert "NOTR" in metin
    assert "muhakeme edilmemiş" in metin.lower()


@pytest.mark.parametrize("dosya", [OA_KIYAS, OA_KONTROL], ids=lambda p: p.parent.name)
def test_yargitay_bam_atfi_zayiflik_uyarisi_yazili(dosya):
    metin = _oku(dosya)
    assert "Yargıtay" in metin and "BAM" in metin
    assert "zayıf" in metin.lower() or "ZAYIF" in metin


# ── Hayalet parça / bozuk referans olmadığından emin ol ─────────────────

def test_sema_dosyasindaki_parca_referanslari_gercek():
    import re
    metin = _oku(SEMA)
    mevcut = {d.name for d in SKILLS.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()}
    for ref in set(re.findall(r"oa-[a-z]{3,}(?:-[a-z]+)*", metin)):
        assert ref in mevcut, f"var olmayan parçaya atıf: {ref}"

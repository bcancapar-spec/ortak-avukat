# -*- coding: utf-8 -*-
"""M3-1 — Dilekçe yazım playbook (kanun yolu mimarisi) testleri.

Saf metin paketi (script yok); testler MEKANİK dosya/içerik denetimidir:
- Yeni playbook (`kanun-yolu-mimari-playbook.md`) var mı ve B1-B7
  bölümlerinin hepsini taşıyor mu.
- `oa-dilekce/SKILL.md`'nin playbook'a kısa çapası var mı (dedup —
  içerik iki yerde şişirilmemiş).
- "İçtihat kullanımı" bölümü 5 adıma genişlemiş mi (damıtma cümlesi +
  somut tatbik/a fortiori + sınırlama/ayırt şerhi).
- GİRİŞ = özet değil + rütbelendirme kuralı SKILL.md'de açık mı.
- Anonimleştirme: playbook'ta isim/dava/kurum/dosya no izi yok (Av.
  Bayram Can Çapar istisnası hariç).
- Değişiklik günlüğü güncellenmiş mi.
- `aile_dogrula.py` (repo bakım denetçisi) bu paketle birlikte yeşil mi.
"""
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"

OA_DILEKCE = SKILLS / "oa-dilekce" / "SKILL.md"
PLAYBOOK = SKILLS / "oa-dilekce" / "references" / "kanun-yolu-mimari-playbook.md"
GUNLUK = SKILLS / "oa-dilekce" / "references" / "degisiklik-gunlugu.md"
AILE_DOGRULA = SKILLS / "oa-usta" / "scripts" / "aile_dogrula.py"


def _oku(yol):
    assert yol.is_file(), f"dosya yok: {yol}"
    return yol.read_text(encoding="utf-8")


# ── Playbook dosyası ─────────────────────────────────────────────────────

def test_playbook_dosyasi_mevcut():
    assert PLAYBOOK.is_file(), f"kanun-yolu-mimari-playbook.md bulunamadı: {PLAYBOOK}"


BOLUMLER = [
    "B1", "B2", "B3", "B4", "B5", "B6", "B7",
    "Künye disiplini",
    "GİRİŞ",
    "Vakıa",
    "İçtihat bloğu",
    "Çökertme protokolü",
    "Bölüm mimarisi",
    "Yardımcı desenler",
]


@pytest.mark.parametrize("baslik", BOLUMLER)
def test_playbook_tum_bolumleri_tasiyor(baslik):
    metin = _oku(PLAYBOOK)
    assert baslik in metin, f"playbook bölümü eksik: {baslik}"


def test_playbook_b1_tebligtarihini_ayri_satir_olarak_isaretliyor():
    metin = _oku(PLAYBOOK)
    assert "Tebliğ tarihi" in metin
    assert "ayrı satır" in metin.lower()


def test_playbook_b2_giris_ozet_degil_ve_muhakeme_onkosulu_var():
    metin = _oku(PLAYBOOK)
    assert "olay özeti" in metin.lower() or "olayların özeti" in metin.lower()
    assert "muhakeme edilmişse" in metin.lower() or "muhakeme edilmemiş" in metin.lower()


def test_playbook_b4_bes_adim_tam():
    metin = _oku(PLAYBOOK)
    for parca in ["Tam künye", "birebir blok-alıntı", "Damıtma cümlesi",
                  "Somut tatbik", "a fortiori", "sınırlama/ayırt şerhi"]:
        assert parca in metin, f"B4 adımı eksik: {parca}"


def test_playbook_b4_sunum_disiplini_yalniz_duyulmus_aleyhe():
    metin = _oku(PLAYBOOK)
    assert "DUYULMUŞ" in metin
    assert "preemptive" in metin.lower()


def test_playbook_b5_bes_tur_cokertme():
    metin = _oku(PLAYBOOK)
    for tur in ["Belge lafzı", "Takvim", "Yokluk tespiti",
                "İç-çelişki", "İtiraf-çıkarma"]:
        assert tur in metin, f"B5 çürütme türü eksik: {tur}"


def test_playbook_b6_rutbelendirme_ve_sira():
    metin = _oku(PLAYBOOK)
    assert "Rütbelendirme" in metin or "rütbelendirilir" in metin
    assert "asıl neden" in metin.lower()
    assert "destekleyici" in metin.lower()


def test_playbook_anonim_isim_dava_kurum_dosya_no_izi_yok():
    metin = _oku(PLAYBOOK)
    # Tasarımcı adı yalnız © telif satırında geçebilir; gövdede (telif
    # satırından önceki kısımda) hiç geçmemelidir — playbook yöntem/mimaridir,
    # somut vaka/isim taşımaz (B1 girişi bunu açıkça belirtir).
    govde = metin.split("© 2026")[0]
    assert "Bayram Can Çapar" not in govde
    # Esas/Karar numarası deseni (ör. "2023/1234") playbook'ta somut vaka
    # numarası olarak GEÇMEMELİ.
    import re
    assert not re.search(r"E\.\s*\d{4}/\d+", metin)
    assert not re.search(r"K\.\s*\d{4}/\d+", metin)


# ── SKILL.md çapası + genişleme ──────────────────────────────────────────

def test_skill_playbooka_kisa_capa_veriyor():
    metin = _oku(OA_DILEKCE)
    assert "kanun-yolu-mimari-playbook.md" in metin


def test_skill_ictihat_kullanimi_bes_adima_genisledi():
    metin = _oku(OA_DILEKCE)
    assert "5 adım" in metin
    assert "Damıtma cümlesi" in metin
    assert "Somut tatbik" in metin
    assert "a fortiori" in metin
    assert "sınırlama/ayırt şerhi" in metin.lower() or "Sınırlama" in metin


def test_skill_giris_ozet_degil_ve_rutbelendirme_capasi():
    metin = _oku(OA_DILEKCE)
    assert "GİRİŞ" in metin
    assert "olay özeti değildir" in metin.lower() or "özeti değildir" in metin.lower()
    assert "rütbelendir" in metin.lower()


def test_skill_sunum_disiplini_sinirinin_ictihat_bolumune_baglandigi():
    metin = _oku(OA_DILEKCE)
    assert "DUYULMUŞ" in metin


# ── Değişiklik günlüğü ────────────────────────────────────────────────────

def test_gunluk_yeni_kayit_iceriyor():
    metin = _oku(GUNLUK)
    assert "kanun-yolu-mimari-playbook.md" in metin
    assert "M3-1" in metin


# ── Hayalet parça / bozuk referans olmadığından emin ol ─────────────────

def test_playbook_dosyasindaki_parca_referanslari_gercek():
    import re
    metin = _oku(PLAYBOOK)
    mevcut = {d.name for d in SKILLS.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()}
    for ref in set(re.findall(r"oa-[a-z]{3,}(?:-[a-z]+)*", metin)):
        assert ref in mevcut, f"var olmayan parçaya atıf: {ref}"


# ── aile_dogrula.py (repo bakım denetçisi) bu paketle yeşil ─────────────

def test_aile_dogrula_yesil():
    assert AILE_DOGRULA.is_file(), f"aile_dogrula.py yok: {AILE_DOGRULA}"
    sonuc = subprocess.run(
        [sys.executable, str(AILE_DOGRULA), str(SKILLS)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert sonuc.returncode == 0, (
        f"aile_dogrula HATA verdi (exit {sonuc.returncode}):\n"
        f"{sonuc.stdout}\n{sonuc.stderr}"
    )

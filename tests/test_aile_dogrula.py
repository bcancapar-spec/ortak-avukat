# -*- coding: utf-8 -*-
"""oa-usta / aile_dogrula.py için testler.

Bu script Fable-tespitli TESTSİZ release-kapısı scriptlerinden biridir
(bkz. görev notu): "aile_dogrula + pytest" release kapısının mekanik
yarısını hiçbir test doğrulamıyordu — regresyonda sessizce körleşebilirdi.

Script'i subprocess ile GERÇEK repo skills kökü üzerinde çağırır (temiz
kök → exit 0) ve ayrıca skills ağacının tempfile KOPYASINDA kasıtlı bir
anayasa ihlali (eski 'Opus-sınıfı' model dayatması metni) enjekte ederek
mekanik kapının GERÇEKTEN bunu yakaladığını (exit 1) doğrular. Gerçek repo
ASLA değiştirilmez — yalnız tempfile.mkdtemp() kopyaları bozulur.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-usta" / "scripts" / "aile_dogrula.py"
SKILLS_KOKU = REPO / "plugins" / "ortak-avukat" / "skills"


def _cli(kok):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), str(kok)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


@pytest.fixture
def bozuk_kopya():
    """Gerçek skills ağacının tempfile KOPYASI — testler burada BOZAR,
    gerçek repo dokunulmaz. Test bitince otomatik temizlenir."""
    assert SCRIPT.is_file(), f"aile_dogrula.py bulunamadı: {SCRIPT}"
    assert SKILLS_KOKU.is_dir(), f"skills kökü bulunamadı: {SKILLS_KOKU}"
    tmp = pathlib.Path(tempfile.mkdtemp())
    hedef = tmp / "skills"
    shutil.copytree(SKILLS_KOKU, hedef)
    yield hedef
    shutil.rmtree(tmp, ignore_errors=True)


# ── temiz kök: gerçek repo (salt-okunur denetim, hiçbir şey yazılmaz) ───────

def test_gercek_repo_skills_koku_temiz_exit0():
    """Gerçek repo skills kökü şu an TEMİZ olmalı → exit 0.
    (Release kapısının GEÇEN hâlini doğrular; regresyonda bu test kırılır.)"""
    assert SCRIPT.is_file(), f"aile_dogrula.py bulunamadı: {SCRIPT}"
    kod, cikti = _cli(SKILLS_KOKU)
    assert kod == 0, f"gerçek skills kökü temiz olmalıydı; çıktı:\n{cikti}"
    assert "AİLE YAPI DENETİMİ TEMİZ" in cikti


def test_gercek_repo_bos_argumanla_kullanim_hatasi():
    """Kullanım hatası (dizin yok) mekanik olarak exit koduyla durdurur."""
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), str(REPO / "olmayan-dizin-xyz")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert cp.returncode != 0


# ── bozuk KOPYA: mekanik kapı GERÇEKTEN yakalıyor mu ────────────────────────

def test_opus_sinifi_enjeksiyonu_yakalanir_exit1(bozuk_kopya):
    """ANAYASA TEK-KAYNAK KAPISI: bir parçanın SKILL.md'sine eski model
    dayatması metni ('Opus-sınıfı') enjekte edilirse mekanik kapı bunu
    HATA olarak yakalayıp exit 1 vermeli. Kopyada bozulur, repo bozulmaz."""
    hedef_skill = bozuk_kopya / "oa-sure" / "SKILL.md"
    assert hedef_skill.is_file()
    with hedef_skill.open("a", encoding="utf-8") as f:
        f.write("\n\nBu iş için model Opus-sınıfı olmalıdır.\n")

    kod, cikti = _cli(bozuk_kopya)
    assert kod == 1, f"'Opus-sınıfı' enjeksiyonu exit 1 üretmeliydi; çıktı:\n{cikti}"
    assert "Opus-sınıfı" in cikti
    assert "oa-sure" in cikti


def test_hayalet_parca_atfi_yakalanir_exit1(bozuk_kopya):
    """HAYALET PARÇA DENETİMİ: var olmayan bir 'oa-xxx' parçasına atıf
    enjekte edilirse mekanik kapı bunu yakalayıp exit 1 vermeli."""
    hedef_skill = bozuk_kopya / "oa-kontrol" / "SKILL.md"
    assert hedef_skill.is_file()
    with hedef_skill.open("a", encoding="utf-8") as f:
        f.write("\n\nBu iş için ayrıca oa-hayalet-parca ile eşgüdüm kurulmalıdır.\n")

    kod, cikti = _cli(bozuk_kopya)
    assert kod == 1, f"hayalet parça atfı exit 1 üretmeliydi; çıktı:\n{cikti}"
    assert "hayalet" in cikti.lower()
    assert "oa-hayalet-parca" in cikti


def test_bozuk_kopya_enjeksiyonsuz_hala_temiz(bozuk_kopya):
    """Kontrast: hiçbir bozulma yapılmadan kopyanın kendisi hâlâ temiz
    olmalı (yani exit 1'in NEDENİ enjeksiyondur, kopyalama artefaktı değil)."""
    kod, cikti = _cli(bozuk_kopya)
    assert kod == 0, f"enjeksiyonsuz kopya da temiz olmalıydı; çıktı:\n{cikti}"

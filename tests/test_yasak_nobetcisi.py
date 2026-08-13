# -*- coding: utf-8 -*-
"""YASAK-NÖBETÇİSİ (v0.5.8 P5 — aile_dogrula ağ-import + vendor denetimi).

m.0 devşirme protokolünün icra aracı: çekirdek scriptler ağ kütüphanesi
import edemez (Layer 0 mekanik teminatı); '# VENDOR:' başlıklı dosya testsiz
olamaz. Semantica dersi: sınır salt konvansiyonla durmaz — sürüm kapısına bağlanır.
"""
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-usta"
          / "scripts" / "aile_dogrula.py")


def _aile_kur(script_icerik, tests_dizini=False):
    """Depo yapısını taklit eder: <root>/skills/<parça> + opsiyonel <root>/tests.
    VENDOR denetimi tests/ dizinini yakın köklerde arar — dizin YOKSA atlar
    (kural depoyu bağlar, depo-dışı kopyayı değil)."""
    root = pathlib.Path(tempfile.mkdtemp())
    kok = root / "skills"
    parca = kok / "oa-sentetik"
    (parca / "scripts").mkdir(parents=True)
    (parca / "SKILL.md").write_text("---\nname: oa-sentetik\n---\ntest",
                                    encoding="utf-8")
    (parca / "scripts" / "arac.py").write_text(script_icerik, encoding="utf-8")
    if tests_dizini:
        (root / "tests").mkdir()
    return kok


def _cli(kok):
    p = subprocess.run([sys.executable, str(SCRIPT), str(kok)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def test_ag_import_ihlali_yakalanir_exit1():
    kok = _aile_kur("import json\nimport requests\n")
    kod, out = _cli(kok)
    assert kod != 0
    assert "YASAK ağ-import" in out and "requests" in out


def test_lazy_import_da_yakalanir():
    kok = _aile_kur("def f():\n    import httpx\n    return httpx\n")
    kod, out = _cli(kok)
    assert "YASAK ağ-import" in out and "httpx" in out


def test_temiz_script_yasak_uretmez():
    kok = _aile_kur("import json, hashlib, os, sys\n")
    kod, out = _cli(kok)
    assert "YASAK ağ-import" not in out  # başka yapısal hatalar olabilir


def test_vendor_testsiz_yakalanir():
    kok = _aile_kur("# VENDOR: github.com/ornek/repo@abc123 (MIT)\nimport json\n",
                    tests_dizini=True)
    kod, out = _cli(kok)
    assert "vendor" in out.lower() and "test" in out.lower()


def test_vendor_depo_disi_kopyada_atlanir():
    """tests/ dizini bulunamayan kopyada VENDOR denetimi atlanır — temiz-kopya
    karakterizasyon testlerinin kırılmaması bu davranışa bağlıdır."""
    kok = _aile_kur("# VENDOR: github.com/ornek/repo@abc123 (MIT)\nimport json\n",
                    tests_dizini=False)
    kod, out = _cli(kok)
    assert "vendor dosyası ama" not in out.lower()


def test_gercek_aile_yasak_ihlalsiz():
    """Gerçek aile üzerinde nöbetçi sıfır ağ-import bulmalı (ölçülmüş taban)."""
    gercek = REPO / "plugins" / "ortak-avukat" / "skills"
    kod, out = _cli(gercek)
    assert "YASAK ağ-import" not in out
    assert kod == 0

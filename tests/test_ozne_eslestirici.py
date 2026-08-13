# -*- coding: utf-8 -*-
"""ozne_eslestirici.py (v0.5.8 P4 — M9 motoru; vendor: semantica JW/Lev
algoritma uyarlaması) testleri. Advisory sözleşmesi: her zaman exit 0,
BAGLA >= 0.92, AVUKATA-SOR 0.80-0.92, altı sessiz."""
import importlib.util
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-vakia"
          / "scripts" / "ozne_eslestirici.py")

spec = importlib.util.spec_from_file_location("ozne_eslestirici", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_tr_normalize_turkce_ve_ocr():
    assert m.tr_normalize("BALÇAL") == "balçal"          # İ/I kuralı + küçültme
    assert m.tr_normalize("Bal.al") == "balal"           # OCR nokta gürültüsü
    assert m.tr_normalize("İsmail  GÜMÜŞ") == "ismail gümüş"


def test_ayni_ozne_varyantlari_yakalanir():
    sonuc = m.eslestir(["Ahmet Balçal", "AHMET BALÇAL", "Ahmet Bal.al"])
    kararlar = {(e["a"]["ad"], e["b"]["ad"]): e["karar"] for e in sonuc}
    # birebir (büyük/küçük) → BAGLA
    assert kararlar[("Ahmet Balçal", "AHMET BALÇAL")] == "BAGLA"
    # OCR varyantı en az AVUKATA-SOR bandında YÜZEYE ÇIKMALI (sessiz kalamaz)
    assert ("Ahmet Balçal", "Ahmet Bal.al") in kararlar


def test_kardes_adi_bagla_DEGIL():
    """Aynı soyad + farklı ad (kardeşler) otomatik BAĞLAnamaz — en fazla
    AVUKATA-SOR; karar avukatta (sessiz çatışma çözümü YASAK)."""
    sonuc = m.eslestir(["Barış Öztürk", "Haldun Öztürk"])
    for e in sonuc:
        assert e["karar"] != "BAGLA"


def test_alakasiz_adlar_sessiz():
    assert m.eslestir(["Nihat Yılmaz", "Zeynep Kaya"]) == []


def test_determinizm_ve_cli_json():
    girdi = ["Mehmet Demir", "Mehmet Demır", "Ayşe Ak"]  # OCR ı/i varyantı
    a = m.eslestir(girdi)
    b = m.eslestir(girdi)
    assert a == b  # determinizm
    p = subprocess.run([sys.executable, str(SCRIPT), *girdi, "--json"],
                       capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0  # advisory — her zaman 0
    r = json.loads(p.stdout)
    assert r["esik_bagla"] == 0.92 and isinstance(r["eslesmeler"], list)
    assert any(e["skor"] >= 0.92 for e in r["eslesmeler"])  # Demir≈Demır

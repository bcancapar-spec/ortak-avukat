# -*- coding: utf-8 -*-
"""P2-14 (v0.5.5) — Override sayacı: --zorla/--serh/--serhle oranının
model-bağımsız mekanik ölçümü. Salt ölçer, exit kodunu ETKİLEMEZ; oran
BAŞARI ÖLÇÜTÜ değil İNCELEME TETİKLEYİCİSİDİR (görünmez-kaçış sayaçları
AYNI çıktıda birlikte taşınır).
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PK = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
METRIK = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "oa_metrik.py"

UZUN_KANIT = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."
UZUN_SERH = "Bilinçli olarak elden devam ediliyor, gerekçe >=30 karakter burada."


def _pk(args, cwd):
    cp = subprocess.run([sys.executable, str(PK)] + args, capture_output=True, text=True,
                         encoding="utf-8", errors="replace", cwd=str(cwd))
    return cp.returncode, cp.stdout + cp.stderr


def _metrik(cwd):
    cp = subprocess.run([sys.executable, str(METRIK), "--kok", "."], capture_output=True,
                         text=True, encoding="utf-8", errors="replace", cwd=str(cwd))
    return cp.returncode, cp.stdout + cp.stderr


def _kunye_kur(tmp_path):
    metin = tmp_path / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")


def test_serhli_ve_temiz_olaylar_orani_dogru_hesaplanir(tmp_path):
    kod, _ = _pk(["--baslat", "Test Dosyası", "--kok", "."], tmp_path)
    assert kod == 0
    _kunye_kur(tmp_path)

    # 2 şerhli (adım-5 önkoşul kapısını ŞERH ile geç) + 3 temiz UYGULANDI.
    kod, cikti = _pk(["--isle", "--adim", "5", "--parca", "oa-kiyas", "--durum", "UYGULANDI",
                      "--kanit", UZUN_KANIT, "--serh", UZUN_SERH, "--kok", "."], tmp_path)
    assert kod == 0, cikti
    kod, cikti = _pk(["--isle", "--adim", "9", "--parca", "oa-kontrol", "--durum", "UYGULANDI",
                      "--kanit", UZUN_KANIT, "--serh", UZUN_SERH, "--kok", "."], tmp_path)
    assert kod == 0, cikti
    for adim, parca in ((1, "oa-interview"), (2, "oa-alan"), (0, "manifest")):
        kod, cikti = _pk(["--isle", "--adim", str(adim), "--parca", parca, "--durum", "UYGULANDI",
                          "--kanit", UZUN_KANIT, "--kok", "."], tmp_path)
        assert kod == 0, cikti

    kod, cikti = _metrik(tmp_path)
    assert kod == 0, cikti
    metrik_yol = tmp_path / "_oa" / "defter" / "metrik.json"
    metrik = json.loads(metrik_yol.read_text(encoding="utf-8"))
    ov = metrik["override_sayaci"]
    assert ov["durum"] == "olculdu"
    assert ov["serhli_uygulandi_parca"] == 2
    assert ov["toplam_uygulandi_parca"] == 5
    assert abs(ov["override_orani"] - (2 / 5)) < 1e-9
    assert "OVERRIDE SAYACI" in cikti


def test_serhsiz_kokte_oran_sifir(tmp_path):
    kod, _ = _pk(["--baslat", "Test Dosyası", "--kok", "."], tmp_path)
    assert kod == 0
    _kunye_kur(tmp_path)
    kod, cikti = _pk(["--isle", "--adim", "1", "--parca", "oa-interview", "--durum", "UYGULANDI",
                      "--kanit", UZUN_KANIT, "--kok", "."], tmp_path)
    assert kod == 0, cikti

    kod, _ = _metrik(tmp_path)
    assert kod == 0
    metrik = json.loads((tmp_path / "_oa" / "defter" / "metrik.json").read_text(encoding="utf-8"))
    ov = metrik["override_sayaci"]
    assert ov["serhli_uygulandi_parca"] == 0
    assert ov["override_orani"] == 0


def test_makbuz_red_sayimi_dogru(tmp_path):
    kod, _ = _pk(["--baslat", "Test Dosyası", "--kok", "."], tmp_path)
    assert kod == 0
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True, exist_ok=True)
    (defter / "teslim-makbuz.json").write_text(
        json.dumps({"exit_kodu": 1, "taslak_yol": "x.md"}), encoding="utf-8")

    kod, _ = _metrik(tmp_path)
    assert kod == 0
    metrik = json.loads((tmp_path / "_oa" / "defter" / "metrik.json").read_text(encoding="utf-8"))
    assert metrik["override_sayaci"]["teslim_makbuz_red_sayisi"] == 1


def test_metrik_exit_kodunu_etkilemez(tmp_path):
    # defter/kunye hiç yokken bile oa_metrik her zaman exit 0 döner (ölçer, kapı değil).
    kod, cikti = _metrik(tmp_path)
    assert kod == 0, cikti
    metrik_yol = tmp_path / "_oa" / "defter" / "metrik.json"
    metrik = json.loads(metrik_yol.read_text(encoding="utf-8"))
    assert metrik["override_sayaci"]["durum"] == "yok"

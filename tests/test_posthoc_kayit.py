# -*- coding: utf-8 -*-
"""P2-13 (v0.5.5) — Post-hoc kayıt dedektörü: bir adımın UYGULANDI zaman
damgası *TESLIM*/*FINAL* desenli dosyanın mtime'ından SONRAYSA `--denetle`
GÖRÜNÜR (advisory) bir uyarı basar. mtime git-checkout/kopyalama/OneDrive ile
oynayabildiğinden bu ASLA exit kodunu değiştirmez (blokleyiciye YÜKSELMEZ).
"""
import os
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"

UZUN_KANIT = "Fiilen script/MCP çağrısı yapıldı ve sonucu belgelendi (>=20 karakter)."


def _cli(args, cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )


def _baslat(tmp_path):
    cp = _cli(["--baslat", "Test Dosyası", "--kok", "."], tmp_path)
    assert cp.returncode == 0, cp.stdout + cp.stderr


def _kunye_kur(tmp_path):
    import json
    metin = tmp_path / "_oa" / "metin"
    metin.mkdir(parents=True, exist_ok=True)
    (metin / "00-kunye.json").write_text(
        json.dumps({"toplam_evrak": 0, "kayitlar": []}), encoding="utf-8")


def _teslim_dosya_yaz(tmp_path, gecmis_offset=-100):
    cikti = tmp_path / "_oa" / "cikti"
    cikti.mkdir(parents=True, exist_ok=True)
    dosya = cikti / "08-dilekce-TESLIM.md"
    dosya.write_text("NETİCE-İ TALEP: ...", encoding="utf-8")
    hedef = time.time() + gecmis_offset
    os.utime(dosya, (hedef, hedef))
    return dosya


def test_teslim_sonrasi_dusulen_uygulandi_uyari_uretir(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    # TESLIM dosyası 100sn ÖNCE yazılmış gibi ayarlanır; adım kaydı ŞİMDİ
    # (yani TESLİM'den SONRA) düşülüyor.
    _teslim_dosya_yaz(tmp_path, gecmis_offset=-100)

    kod, cikti = _isle(tmp_path)
    assert kod == 0, cikti
    cp = _cli(["--denetle", "--kok", "."], tmp_path)
    assert "POST-HOC KAYIT" in cp.stdout
    assert "adım 4" in cp.stdout


def test_ters_sirada_uyari_uretilmez(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    kod, cikti = _isle(tmp_path)
    assert kod == 0, cikti
    # TESLIM dosyası adım kaydından SONRA yazılır (doğal sıra) → uyarı YOK.
    _teslim_dosya_yaz(tmp_path, gecmis_offset=100)

    cp = _cli(["--denetle", "--kok", "."], tmp_path)
    assert "POST-HOC KAYIT" not in cp.stdout


def test_uyari_exit_kodunu_degistirmez(tmp_path):
    _baslat(tmp_path)
    _kunye_kur(tmp_path)
    _teslim_dosya_yaz(tmp_path, gecmis_offset=-100)
    kod, _ = _isle(tmp_path)
    assert kod == 0

    cp_uyarili = _cli(["--denetle", "--kok", "."], tmp_path)
    assert "POST-HOC KAYIT" in cp_uyarili.stdout

    # aynı boşluklu-tur exit kodu — uyarı VARKEN de YOKKEN de aynı olmalı.
    import shutil
    shutil.rmtree(tmp_path / "_oa" / "cikti")
    cp_temiz = _cli(["--denetle", "--kok", "."], tmp_path)
    assert cp_temiz.returncode == cp_uyarili.returncode


def _isle(tmp_path):
    return (lambda cp: (cp.returncode, cp.stdout + cp.stderr))(_cli(
        ["--isle", "--adim", "4", "--parca", "oa-vakia", "--durum", "UYGULANDI",
         "--kanit", UZUN_KANIT, "--kok", "."], tmp_path))

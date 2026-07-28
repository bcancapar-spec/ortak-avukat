# -*- coding: utf-8 -*-
"""P1-12 (v0.5.5, yeniden çerçevelenmiş) — UTF-8 guard REGRESYON KİLİDİ.

Sinav-turu tespiti: guard zaten 25/25 script'te MEVCUT (bu maddenin kapatacağı
yüzey zaten kapalıydı) — bu dosya bunu KİLİTLER (yeni bir script guard'sız
eklenirse test kırmızı yanar). Ayrılan ikinci ağırlık: kapı-çökme = kapı-
atlanması sınıfını PYTHONIOENCODING=cp1254 altında fiilen doğrulamak (Windows/
PowerShell konsol gerçeği) — Türkçe+işaretli rapor basan kapılar traceback
vermeden tamamlanmalı (replace kabul, çökme RET).
"""
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"


def _tum_scriptler():
    return sorted(SKILLS.glob("*/scripts/*.py"))


def test_her_scriptte_utf8_guard_veya_utf8_konsol_var():
    eksik = []
    for s in _tum_scriptler():
        txt = s.read_text(encoding="utf-8", errors="replace")
        if "__OA_UTF8_GUARD__" not in txt and "utf8_konsol" not in txt:
            eksik.append(str(s.relative_to(REPO)))
    assert not eksik, f"guard'sız script(ler): {eksik}"


def test_en_az_yirmibes_script_taranir_regresyon_kilidi():
    # Bu sayı P1-12 yazıldığında 25 idi; azalırsa (dosya kaybı) veya yeni
    # scriptler eklenip guard kontrolü atlanırsa fark edilsin diye kilitlenir.
    assert len(_tum_scriptler()) >= 25


def _cp1254_ortam():
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp1254"
    env["PYTHONUTF8"] = "0"
    return env


def _turkce_rapor_basan_kapilar_cp1254_altinda_cokmez(script, args, cwd):
    env = _cp1254_ortam()
    cp = subprocess.run(
        [sys.executable, str(script)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(cwd), env=env,
    )
    hata = (cp.stderr or "")
    assert "UnicodeEncodeError" not in hata, f"{script.name} cp1254 altında çöktü:\n{hata}"
    assert "Traceback" not in hata, f"{script.name} cp1254 altında traceback verdi:\n{hata}"


def test_pipeline_kayit_cp1254_altinda_cokmez(tmp_path):
    script = SKILLS / "oa-pipeline" / "scripts" / "pipeline_kayit.py"
    subprocess.run([sys.executable, str(script), "--baslat", "Türkçe Şerh Dosyası",
                    "--kok", "."], cwd=str(tmp_path), capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
    _turkce_rapor_basan_kapilar_cp1254_altinda_cokmez(
        script, ["--denetle", "--kok", "."], tmp_path)


def test_oa_hafiza_cp1254_altinda_cokmez(tmp_path):
    script = SKILLS / "oa-pipeline" / "scripts" / "oa_hafiza.py"
    subprocess.run([sys.executable, str(script), "init", "--dosya", "Türkçe Dosya"],
                   cwd=str(tmp_path), capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
    _turkce_rapor_basan_kapilar_cp1254_altinda_cokmez(script, ["durum"], tmp_path)

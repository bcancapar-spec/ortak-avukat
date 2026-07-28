# -*- coding: utf-8 -*-
"""P1-8 (v0.5.5) — KAPANIŞ Gate: `oa_hafiza.py oturum-kapat`, `pipeline_kayit.py
--denetle` + `oa_metrik.py` özetini FİİLEN (İN-PROCESS) koşturur.

DÜZELTME (bağlayıcı plan, sinav çelişkisinin çözümü): --denetle'nin bulduğu
sorunlar/uyarılar kapanışı BLOKLAMAZ — çıktı KESMESİZ devir notuna yazılır.
RET yalnız dar hâlde: denetim FİİLEN koşulamadığında (script yok/çöktü) VE
--serhle (≥30 karakter) verilmediğinde.

Kapsam:
1. Defter var + --denetle sorun/uyarı bulur → kapanış YİNE DE exit 0, devir
   notunda denetim çıktısı KESMESİZ (tam metin) var.
2. pipeline_kayit.py bulunamıyor/çöküyor → RET (exit 1), --serhle YOKSA.
3. Deftersiz kök → eski davranış (yalnız --not + cikti-boş uyarısı).
4. pipeline_kayit yok + --serhle geçerli → kapanır, devir notunda hem şerh
   hem "koşulamadı" mesajı KESMESİZ görünür.
5. Kilit yalnız başarılı/şerhli kapanışta silinir (dar RET'te kilit KALIR).
"""
import importlib.util
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
OA_HAFIZA = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts"
             / "oa_hafiza.py")
PIPELINE_KAYIT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts"
                  / "pipeline_kayit.py")


def _load(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _cli(args, cwd):
    return subprocess.run(
        [sys.executable, str(OA_HAFIZA)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )


def _init(kok):
    cp = _cli(["init", "--dosya", "Test Dosyası"], kok)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    cp = _cli(["oturum-ac"], kok)
    assert cp.returncode == 0, cp.stdout + cp.stderr


def _pk_cli(args, cwd):
    return subprocess.run(
        [sys.executable, str(PIPELINE_KAYIT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )


def test_defter_var_denetim_sorun_bulur_ama_kapanis_blok_olmaz(tmp_path):
    _init(tmp_path)
    # Defter aç ama hiçbir adım işleme → --denetle kesin BEKLIYOR/sorun bulur.
    cp = _pk_cli(["--baslat", "Test Dosyası", "--kok", "."], tmp_path)
    assert cp.returncode == 0, cp.stdout + cp.stderr

    cp = _cli(["oturum-kapat", "--not", "yeterince uzun kapanış notu buradadır"], tmp_path)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert "KAPANIŞ GATE" in cp.stdout
    kilit = tmp_path / "_oa" / ".oturum-kilidi"
    assert not kilit.exists(), "başarılı kapanışta kilit kalkmalı"

    # Devir notunda denetim çıktısı KESMESİZ (tam metin) görünür olmalı.
    oturum_dizin = tmp_path / "_oa" / "oturum"
    notlar = sorted(oturum_dizin.glob("*.md"))
    assert notlar, "oturum notu yazılmamış"
    icerik = notlar[-1].read_text(encoding="utf-8")
    assert "KAPANIŞ GATE" in icerik
    assert "pipeline_kayit --denetle" in icerik


def test_deftersiz_kok_eski_davranis(tmp_path):
    _init(tmp_path)
    # cmd_init _oa/defter'i BOŞ dizin olarak da yaratır (pipeline_kayit --baslat
    # hiç koşulmamış olsa dahi) — gerçek "bu kök pipeline defteri KULLANMIYOR"
    # durumunu simüle etmek için dizini tamamen kaldırıyoruz.
    (tmp_path / "_oa" / "defter").rmdir()
    cp = _cli(["oturum-kapat", "--not", "yeterince uzun kapanış notu buradadır"], tmp_path)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert "KAPANIŞ GATE" not in cp.stdout
    kilit = tmp_path / "_oa" / ".oturum-kilidi"
    assert not kilit.exists()


def test_pipeline_kayit_bulunamazsa_serhsiz_ret(tmp_path):
    mod = _load(OA_HAFIZA, "oa_hafiza_gate_test_1")
    mod._kok_ayarla(str(tmp_path))
    os.makedirs(str(tmp_path), exist_ok=True)
    import argparse
    ns = argparse.Namespace(dosya="Test Dosyası", kok=str(tmp_path))
    mod.cmd_init(ns)
    # defter dizinini oluştur ki "deftersiz kök = eski davranış" yoluna düşmesin.
    os.makedirs(os.path.join(mod.KOK, "defter"), exist_ok=True)
    with open(mod.KILIT, "w", encoding="utf-8") as f:
        f.write("açılış: test")

    mod._pipeline_kayit_modulu = lambda: None  # script "bulunamadı" simülasyonu

    ns2 = argparse.Namespace(not_="yeterince uzun kapanış notu buradadır",
                              kok=str(tmp_path), serhle=None)
    try:
        mod.cmd_oturum_kapat(ns2)
        assert False, "RET beklenirdi (SystemExit)"
    except SystemExit as e:
        mesaj = str(e)
        assert "RET" in mesaj
        assert "koşulamadı" in mesaj
    kilit = pathlib.Path(mod.KILIT)
    assert kilit.exists(), "dar RET'te kilit KALMALI (başarısız kapanış)"

    # P1-8 DÜZELTME (BLOKER) — dar RET'te dahi KAPANIŞ artefaktı (devir notu)
    # KAYBOLMAMALI: exit kararından ÖNCE diske yazılır (kayıpsızlık invaryantı).
    oturum_dizin = pathlib.Path(mod.KOK) / "oturum"
    notlar = sorted(oturum_dizin.glob("*.md"))
    assert notlar, "dar RET'te devir notu diske YAZILMAMIŞ (P1-8 REGRESYONU)"
    icerik = notlar[-1].read_text(encoding="utf-8")
    assert "koşulamadı" in icerik
    assert "yeterince uzun kapanış notu buradadır" in icerik


def test_pipeline_kayit_bulunamazsa_serhle_gecerli_kapanir(tmp_path):
    mod = _load(OA_HAFIZA, "oa_hafiza_gate_test_2")
    mod._kok_ayarla(str(tmp_path))
    import argparse
    ns = argparse.Namespace(dosya="Test Dosyası", kok=str(tmp_path))
    mod.cmd_init(ns)
    os.makedirs(os.path.join(mod.KOK, "defter"), exist_ok=True)

    mod._pipeline_kayit_modulu = lambda: None

    serh = "pipeline_kayit.py bu ortamda erişilemiyor, elden kapanıyoruz"
    ns2 = argparse.Namespace(not_="yeterince uzun kapanış notu buradadır",
                              kok=str(tmp_path), serhle=serh)
    mod.cmd_oturum_kapat(ns2)  # exit etmemeli

    oturum_dizin = pathlib.Path(mod.KOK) / "oturum"
    notlar = sorted(oturum_dizin.glob("*.md"))
    assert notlar
    icerik = notlar[-1].read_text(encoding="utf-8")
    assert "ŞERH" in icerik
    assert "koşulamadı" in icerik
    kilit = pathlib.Path(mod.KILIT)
    assert not kilit.exists(), "şerhli kapanışta kilit kalkmalı"

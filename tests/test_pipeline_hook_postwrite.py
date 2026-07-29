# -*- coding: utf-8 -*-
"""oa-pipeline / pipeline_kayit.py — GÖREV B (P0-B, v0.5.5) İKİNCİ AYAK testleri:
`--hook-postwrite` (PostToolUse(Write|Edit) hook komutu).

Saha bulgusu (B3): teslim kapısının görünürlüğü Stop/SessionEnd'e kadar
GECİKİYORDU — bir taslak/UDF üretimi ile oturum kapanışı arasında model
hiçbir şey çağırmadan uzun süre çalışabiliyordu. `--hook-postwrite` bu
boşluğu HER Write/Edit çağrısından sonra tetiklenerek kapatır; ama HER
çağrıda tam (Gate-G/makbuz/oa_metrik dahil) ağır denetimi koşturmak pahalı
olacağından, önce `_hook_postwrite_tetikle_mi` UCUZ bir ön-denetimle yalnız
"_oa/cikti altında SON 60 saniyede dilekçe-şekilli yeni bir dosya düştü mü"
sorusuna bakar; HAYIR ise tam gövde HİÇ çağrılmaz.

Sözleşme (hook_denetle ile SİMETRİK): ASLA bloklamaz (her zaman exit 0);
hataya dayanıklıdır; sessiz başarısızlık yoktur (mümkünse DURUM.md'ye not
düşer).
"""
import importlib.util
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"


def _load():
    spec = importlib.util.spec_from_file_location("pipeline_kayit_hook_postwrite", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pk = _load()


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def test_script_bayragi_tanimli():
    metin = SCRIPT.read_text(encoding="utf-8")
    assert "--hook-postwrite" in metin
    assert "def hook_postwrite(" in metin
    assert "def _hook_postwrite_tetikle_mi(" in metin


# ── _hook_postwrite_tetikle_mi() — ucuz ön-denetim birim testleri ──────────

def test_defter_yoksa_false(tmp_path):
    assert pk._hook_postwrite_tetikle_mi(str(tmp_path)) is False


def test_defter_var_cikti_yok_false(tmp_path):
    (tmp_path / "_oa" / "defter").mkdir(parents=True)
    assert pk._hook_postwrite_tetikle_mi(str(tmp_path)) is False


def test_defter_var_cikti_bos_false(tmp_path):
    (tmp_path / "_oa" / "defter").mkdir(parents=True)
    (tmp_path / "_oa" / "cikti").mkdir(parents=True)
    assert pk._hook_postwrite_tetikle_mi(str(tmp_path)) is False


def test_defter_var_yeni_dilekce_sekilli_dosya_true(tmp_path):
    (tmp_path / "_oa" / "defter").mkdir(parents=True)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True)
    (cikti_dizin / "08-dilekce-son.md").write_text(
        "DAVACI: Ali Veli\nDAVALI: XYZ A.Ş.\nSONUÇ VE İSTEM: ...\n", encoding="utf-8")
    assert pk._hook_postwrite_tetikle_mi(str(tmp_path)) is True


def test_dilekce_sekilli_olmayan_dosya_false(tmp_path):
    (tmp_path / "_oa" / "defter").mkdir(parents=True)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True)
    (cikti_dizin / "notlar.md").write_text("Yalnızca bir çalışma notu.\n", encoding="utf-8")
    assert pk._hook_postwrite_tetikle_mi(str(tmp_path)) is False


def test_eski_dosya_pencere_disinda_false(tmp_path):
    (tmp_path / "_oa" / "defter").mkdir(parents=True)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True)
    dosya = cikti_dizin / "08-dilekce-son.md"
    dosya.write_text("DAVACI: Ali Veli\nSONUÇ VE İSTEM: ...\n", encoding="utf-8")
    eski = time.time() - 3600  # 1 saat önce
    import os
    os.utime(dosya, (eski, eski))
    assert pk._hook_postwrite_tetikle_mi(str(tmp_path), pencere_sn=60) is False


def test_hicbir_zaman_istisna_firlatmaz_var_olmayan_yol():
    assert pk._hook_postwrite_tetikle_mi("/kesinlikle/var/olmayan/bir/yol/xyz123") is False


# ── hook_postwrite() — CLI/fonksiyon uçtan uca ─────────────────────────────

def test_cikti_bos_iken_agir_govde_hic_calismaz_sessiz(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(["--hook-postwrite", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    assert cikti.strip() == "", (
        f"_oa/cikti'ya yeni dilekçe-şekilli dosya düşmeden ağır gövde SESSİZ kalmalı:\n{cikti}")


def test_yeni_dilekce_dusunce_tam_denetim_calisir_ve_uyarir(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "08-dilekce-son.md").write_text(
        "DAVACI: Ali Veli\nDAVALI: XYZ A.Ş.\nSONUÇ VE İSTEM: ...\n", encoding="utf-8")

    kod, cikti = _cli(["--hook-postwrite", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "OTOMATİK DENETİM" in cikti
    assert "makbuzsuz dilekçe adayı" in cikti


def test_defter_yokken_sessiz_exit0(tmp_path):
    kod, cikti = _cli(["--hook-postwrite", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    assert cikti.strip() == ""


def test_fonksiyon_dogrudan_cagrilinca_hep_0_doner():
    sonuc = pk.hook_postwrite(kok="/kesinlikle/var/olmayan/bir/yol/xyz123")
    assert sonuc == 0


def test_bozuk_defterde_bile_exit0_doner(tmp_path):
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True, exist_ok=True)
    (defter / "pipeline-olaylar.jsonl").write_text(
        "{bozuk-json-degil-ama-gecerli-de-degil\n", encoding="utf-8")
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "08-dilekce-son.md").write_text(
        "DAVACI: Ali Veli\nSONUÇ VE İSTEM: ...\n", encoding="utf-8")
    kod, cikti = _cli(["--hook-postwrite", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, f"bozuk defterde bile hook exit 0 dönmeli:\n{cikti}"


# ── hook_denetle ile ortak gövde regresyonu (refactor kilidi) ───────────────

def test_hook_denetle_hala_calisir_refactor_sonrasi(tmp_path):
    """`_hook_govde_calistir` ortak gövdeye çıkarılırken `hook_denetle`'nin
    DAVRANIŞI bit-düzeyinde BOZULMAMALI (bkz. tests/test_hook_denetle.py)."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(["--hook-denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    assert "OTOMATİK DENETİM" in cikti
    assert "Stop/SessionEnd hook" in cikti

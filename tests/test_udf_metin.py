# -*- coding: utf-8 -*-
"""oa-pipeline / udf_metin.py için testler.

GÖREV D (v0.5.5, UDF hattı — okuma tarafı): script artık ham zip/content.xml
okuma DENEMEZ (bu deneme BIRAKILDI) — TEK okuma yolu `npx -y udf-cli@latest
udf2md`. Bu yüzden testler:
  - FAIL-CLOSED (npx yok/başarısız → None + hata, CLI'de exit != 0, net mesaj)
    ağsız/deterministiktir, her zaman koşar.
  - Gerçek `udf-cli udf2md` uçtan-uca testi yalnız npx/oturum kullanılabilirse
    koşar (nazikçe skip — hiçbir makinede KIRILMAZ).

NOT: `oa_ingest.py`'nin kendi bağımsız `udf_isle()` (yerel/çevrimdışı ana
ingest hattı) BU DOSYADA test EDİLMEZ — o script'e Görev D kapsamında
DOKUNULMADI (bkz. udf_metin.py docstring'i, 'ÖNEMLİ SINIR').
"""
import importlib.util
import pathlib
import subprocess
import sys

import pytest

import oa_udf_ortam

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "udf_metin.py"
UDF_YAZ_SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce"
                  / "scripts" / "udf_yaz.py")


def _load():
    assert SCRIPT.is_file(), f"udf_metin.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("udf_metin", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


um = _load()


def test_ham_okuma_fonksiyonlari_artik_yok():
    """Eski ham zip/content.xml okuma denemesi (`metin_cikar`) TAMAMEN
    kaldırılmış olmalı — TEK yol artık `udf2md_ile_metin_cikar` (npx udf-cli)."""
    assert not hasattr(um, "metin_cikar")
    assert hasattr(um, "udf2md_ile_metin_cikar")


def test_zipfile_kodda_hic_gecmiyor():
    """Regresyon kilidi: script artık `zipfile`/`xml.etree` KULLANMAZ — okuma
    tamamen dış `udf-cli` sürecine devredilmiştir."""
    kaynak = SCRIPT.read_text(encoding="utf-8")
    assert "import zipfile" not in kaynak
    assert "xml.etree" not in kaynak


# ── FAIL-CLOSED: npx yokken/başarısızken ham okumaya SESSİZCE düşülmez ──────

def test_fonksiyon_npx_yokken_none_ve_hata_doner(tmp_path):
    sahte = tmp_path / "sahte.udf"
    sahte.write_bytes(b"herhangi bir icerik")
    metin, hata = um.udf2md_ile_metin_cikar(
        str(sahte), npx_yolu="oa-hic-boyle-bir-komut-yok-xyz")
    assert metin is None
    assert hata


def test_cli_npx_yokken_exit_farkli_sifir_ve_net_mesaj(tmp_path):
    sahte = tmp_path / "sahte.udf"
    sahte.write_bytes(b"herhangi bir icerik")
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), str(sahte), "--npx", "oa-hic-boyle-bir-komut-yok-xyz"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode != 0
    birlesik = cp.stdout + cp.stderr
    assert "HATA" in birlesik
    assert "manuel inceleme" in birlesik
    assert "login" in birlesik.lower()


def test_cli_npx_yokken_cikti_dosyasi_yazilmaz(tmp_path):
    sahte = tmp_path / "sahte.udf"
    sahte.write_bytes(b"herhangi bir icerik")
    cikti = tmp_path / "cikti.txt"
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), str(sahte), "--cikti", str(cikti),
         "--npx", "oa-hic-boyle-bir-komut-yok-xyz"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode != 0
    assert not cikti.exists(), "npx yokken --cikti dosyası YAZILMAMALIYDI (fail-closed)"


# ── gerçek udf-cli round-trip: npx/oturum kullanılabilirse ──────────────────

def _npx_hazir_mi():
    """TEK KAYNAK: bu yoklamanın KENDİ kopyası vardı (üretimdeki
    `udf_yaz.npx_kullanilabilir_mi()`nin ikizi — aynı komut, ayrı kod).
    İkiz kaldırıldı; soru artık `tests/oa_udf_ortam.py` üzerinden bir kez
    sorulur ve oturum boyunca önbelleklenir."""
    return oa_udf_ortam.gercek_udf_yazici_var()


@pytest.mark.skipif(not _npx_hazir_mi(), reason="npx/udf-cli oturumu bu makinede kullanılamıyor")
def test_gercek_udf_cli_ile_uretilen_udf_geri_okunur(tmp_path):
    """Uçtan uca: udf_yaz.py (gerçek npx html2udf) ile üret → udf_metin.py
    (gerçek npx udf2md) ile geri oku — içerik round-trip etmeli."""
    girdi = tmp_path / "taslak.md"
    girdi.write_text("# Dava Dilekcesi\n\nMuvekkilimiz adina arz ederiz.\n",
                      encoding="utf-8")
    udf = tmp_path / "dilekce.udf"
    cp_yaz = subprocess.run(
        [sys.executable, str(UDF_YAZ_SCRIPT), "--girdi", str(girdi), "--cikti", str(udf)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    assert cp_yaz.returncode == 0, cp_yaz.stdout + cp_yaz.stderr
    assert udf.is_file()

    cp_oku = subprocess.run([sys.executable, str(SCRIPT), str(udf)],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=60)
    assert cp_oku.returncode == 0, cp_oku.stdout + cp_oku.stderr
    assert "Muvekkilimiz" in cp_oku.stdout

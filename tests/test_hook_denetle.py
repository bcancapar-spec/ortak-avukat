# -*- coding: utf-8 -*-
"""P0-7 (v0.5.5) — pipeline_kayit.py --hook-denetle (model-bağımsız Stop/
SessionEnd hook komutu) için testler.

Sözleşme: _oa/defter bu kökte YOKSA sessizce exit 0 (çıktı yok); VARSA
denetim + oa_metrik özetini basar; NE OLURSA OLSUN her zaman exit 0 (ASLA
oturum kapanışını bloklamaz) — bozuk/eksik defterde bile.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline" / "scripts" / "pipeline_kayit.py"


def _load():
    spec = importlib.util.spec_from_file_location("pipeline_kayit_hook", SCRIPT)
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


def test_script_mevcut():
    assert SCRIPT.is_file()


def test_defter_yoksa_sessiz_exit0(tmp_path):
    kod, cikti = _cli(["--hook-denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0
    assert cikti.strip() == "", f"defter yokken hook SESSİZ olmalı, çıktı üretmemeli:\n{cikti}"


def test_defter_varsa_ozet_basar_ve_exit0(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod, cikti = _cli(["--hook-denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, f"hook ASLA bloklamamalı (exit 0 dönmeli):\n{cikti}"
    assert "OTOMATİK DENETİM" in cikti
    assert "TOKEN / VERİMLİLİK TELEMETRİSİ" in cikti or "oa_metrik" in cikti.lower()


def test_defter_varsa_durum_md_tazelenir(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    durum_md = tmp_path / "_oa" / "DURUM.md"
    assert durum_md.is_file(), "--baslat DURUM.md'yi zaten üretmeliydi (P0-8)"
    onceki = durum_md.read_text(encoding="utf-8")
    kod, _cikti = _cli(
        ["--isle", "--adim", "0", "--parca", "manifest", "--durum", "GEREKSIZ",
         "--gerekce", "test amaçlı — manifest adımı bu senaryoda gereksiz.",
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod == 0
    kod_h, cikti_h = _cli(["--hook-denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod_h == 0, cikti_h
    guncel = durum_md.read_text(encoding="utf-8")
    assert guncel != onceki, "DURUM.md hook-denetle sonrası tazelenmeliydi"


def test_hook_denetle_asla_exit_1_donmez_bozuk_defterde(tmp_path):
    """Bozuk/yarım bir defter olsa bile --hook-denetle ASLA exit != 0
    dönmemeli (hook sözleşmesi: ASLA bloklamaz)."""
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True, exist_ok=True)
    (defter / "pipeline-olaylar.jsonl").write_text(
        "{bozuk-json-degil-ama-gecerli-de-degil\n", encoding="utf-8")
    kod, cikti = _cli(["--hook-denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod == 0, f"bozuk defterde bile hook exit 0 dönmeli:\n{cikti}"


def test_hook_denetle_fonksiyonu_dogrudan_cagrilinca_hep_0_doner():
    """`hook_denetle()` fonksiyonunun kendisi de (CLI sarmalayıcısı dışında)
    her koşulda 0 döner — ASLA istisna fırlatıp çağıranı çökertmez."""
    sonuc = pk.hook_denetle(kok="/kesinlikle/var/olmayan/bir/yol/xyz123")
    assert sonuc == 0


# ── P0-7 KUCUK-düzeltme (sinav-turu): 'Stop' HER asistan turunda tetiklenir
# (yalnız oturum sonunda değil) — defter DEĞİŞMEDEN art arda hook çağrıları
# aynı (pahalı) denetimi tekrar basmamalı; defter DEĞİŞİNCE yeniden basmalı.

def test_hook_ikinci_kez_degismeden_cagrilinca_sessiz_kisa_devre(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod1, cikti1 = _cli(["--hook-denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod1 == 0
    assert "OTOMATİK DENETİM" in cikti1, "ilk hook koşusu her zaman tam denetimi basmalı"

    # Defter DEĞİŞMEDEN aynı hook ikinci kez tetiklenir (ör. bir sonraki tur).
    kod2, cikti2 = _cli(["--hook-denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod2 == 0, f"hook ASLA bloklamamalı:\n{cikti2}"
    assert cikti2.strip() == "", (
        f"defter DEĞİŞMEDEN ikinci hook koşusu SESSİZ kısa devre yapmalıydı:\n{cikti2}")


def test_hook_defter_degismeden_cikti_dilekce_yazilinca_yine_uyarir(tmp_path):
    """Paket-B sinav-turu BLOKER giderimi: model deftere HİÇ DOKUNMADAN
    (--isle/--katman/--baslat çağırmadan) `_oa/cikti`'ya dilekçe-şekilli bir
    dosya yazarsa (atlatma senaryosu — `--isle` çağrılmadan doğrudan yazım),
    hook'un eski (yalnız defter boyut/mtime'ına bakan) kısa devresi KÖRDÜ.
    Yeni sözleşme: `_dilekce_sekilli_makbuzsuz_uyarisi` denetim ÇIKTISINI
    değiştirdiği için (defter değişmese bile) hook YİNE basmalı."""
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod1, cikti1 = _cli(["--hook-denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod1 == 0
    assert "OTOMATİK DENETİM" in cikti1, "ilk hook koşusu her zaman tam denetimi basmalı"
    assert "makbuzsuz dilekçe adayı" not in cikti1

    # Defter HİÇ DEĞİŞMEDEN (--isle/--katman/--baslat YOK) _oa/cikti'ya elden
    # dilekçe-şekilli bir dosya yazılır — tam da atlatma senaryosu.
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / "08-dilekce-son.md").write_text(
        "DAVACI: Ali Veli\nDAVALI: XYZ A.Ş.\nSONUÇ VE İSTEM: ...\n", encoding="utf-8")

    kod2, cikti2 = _cli(["--hook-denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod2 == 0, f"hook ASLA bloklamamalı:\n{cikti2}"
    assert cikti2.strip() != "", (
        "defter değişmese bile _oa/cikti'ya yeni dilekçe yazılınca hook SESSİZ "
        "kalmamalı (eski kısa devre bu senaryoda kördü)")
    assert "OTOMATİK DENETİM" in cikti2
    assert "makbuzsuz dilekçe adayı" in cikti2


def test_hook_defter_degisince_yeniden_denetler(tmp_path):
    _cli(["--baslat", "Test Dosyası", "--kok", str(tmp_path)], cwd=tmp_path)
    kod1, _cikti1 = _cli(["--hook-denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod1 == 0

    kod_isle, _c = _cli(
        ["--isle", "--adim", "0", "--parca", "manifest", "--durum", "GEREKSIZ",
         "--gerekce", "test amaçlı — manifest adımı bu senaryoda gereksiz.",
         "--kok", str(tmp_path)],
        cwd=tmp_path,
    )
    assert kod_isle == 0

    kod2, cikti2 = _cli(["--hook-denetle", "--kok", str(tmp_path)], cwd=tmp_path)
    assert kod2 == 0
    assert "OTOMATİK DENETİM" in cikti2, (
        f"defter DEĞİŞTİKTEN sonra hook yeniden tam denetim basmalıydı:\n{cikti2}")

# -*- coding: utf-8 -*-
"""oa-pipeline / capraz_denetim.py için testler.

Bu script Fable-tespitli TESTSİZ release-kapısı scriptlerinden biridir:
illiyet grafı + vakıa matrisi + kıyas dosyalarının ORTAK KİMLİK UZAYINDA
tutarlı olup olmadığını denetleyen bu çapraz-referans denetçisi hiçbir
test doğrulamıyordu — kopukluk tespiti sessizce bozulabilirdi.

Üç senaryo: (1) kasıtlı KOPUK graf/vakıa/kıyas üçlüsü → kopukluk YAKALANIR,
exit 1; (2) aynı üçlünün TUTARLI hâli → exit 0; (3) dosyalardan biri/hepsi
eksikken çökme yok.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-pipeline"
          / "scripts" / "capraz_denetim.py")


def _cli(cikti_dizin, extra=()):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--cikti-dizin", str(cikti_dizin), *extra],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


@pytest.fixture
def cikti_dizin():
    tmp = pathlib.Path(tempfile.mkdtemp())
    d = tmp / "_oa" / "cikti"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _yaz(dizin, ad, veri):
    (dizin / ad).write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")


# Tutarlı (temiz) üçlü: delil aynı kimlikle graf+vakıada var, kıyas
# vakıası vakia.json'daki olgu/iddia metniyle birebir örtüşüyor, unsur
# ve dayanak_delil referansları tanımlı.
GRAF_TEMIZ = {
    "dugumler": [{"id": "delil-1", "tip": "delil", "ad": "Sözleşme örneği"}],
    "kenarlar": [{"dayanak_delil": ["delil-1"]}],
}
VAKIA_TEMIZ = {
    "iddialar": [{"id": "iddia-1", "metin": "Taraflar sözleşme imzaladı"}],
    "olaylar": [{"olgu": "Taraflar sözleşme imzaladı", "belge": "Sözleşme örneği",
                 "ispat_durumu": "belgeli"}],
}
KIYAS_TEMIZ = {
    "buyuk_onerme": {"unsurlar": [{"id": "unsur-1"}]},
    "kucuk_onerme": {"vakialar": [{"metin": "Taraflar sözleşme imzaladı",
                                    "karsilar": ["unsur-1"],
                                    "dayanak_delil": ["delil-1"]}]},
}

# Kasıtlı KOPUK üçlü: vakıanın delili grafta yok, kıyasın vakıası
# vakia.json'da yok, kıyasın dayanak_delili ne grafta ne vakıada tanınıyor,
# kıyasın 'karsilar'ı tanımsız bir unsura işaret ediyor.
GRAF_BOZUK = {
    "dugumler": [{"id": "delil-1", "tip": "delil", "ad": "Sözleşme örneği"}],
    "kenarlar": [{"dayanak_delil": ["delil-1"]}],
}
VAKIA_BOZUK = {
    "iddialar": [{"id": "iddia-1", "metin": "Ödeme yapılmadı"}],
    "olaylar": [{"olgu": "Ödeme yapılmadı", "belge": "Fatura no 123",
                 "ispat_durumu": "belgeli"}],
}
KIYAS_BOZUK = {
    "buyuk_onerme": {"unsurlar": [{"id": "unsur-1"}]},
    "kucuk_onerme": {"vakialar": [{"metin": "Taraflar hiç görüşmedi",
                                    "karsilar": ["unsur-99"],
                                    "dayanak_delil": ["delil-XYZ"]}]},
}


def test_script_mevcut():
    assert SCRIPT.is_file(), f"capraz_denetim.py bulunamadı: {SCRIPT}"


# ── (1) kasıtlı kopuk graf/vakıa/kıyas → kopukluk yakalanır, exit 1 ────────

def test_kasitli_kopuk_uclu_yakalanir_exit1(cikti_dizin):
    _yaz(cikti_dizin, "01-illiyet-graf.json", GRAF_BOZUK)
    _yaz(cikti_dizin, "04-vakia.json", VAKIA_BOZUK)
    _yaz(cikti_dizin, "05-kiyas.json", KIYAS_BOZUK)

    kod, cikti = _cli(cikti_dizin)

    assert kod == 1, f"kasıtlı kopukluk exit 1 üretmeliydi; çıktı:\n{cikti}"
    assert "KOPUK REFERANSLAR" in cikti
    assert "DELIL_GRAFTA_YOK" in cikti
    assert "KIYAS_VAKIA_VAKIADA_YOK" in cikti
    assert "KIYAS_DELIL_BILINMIYOR" in cikti
    assert "KIYAS_UNSUR_YOK" in cikti


def test_kopuk_json_ciktisinda_da_gorunur(cikti_dizin):
    _yaz(cikti_dizin, "01-illiyet-graf.json", GRAF_BOZUK)
    _yaz(cikti_dizin, "04-vakia.json", VAKIA_BOZUK)
    _yaz(cikti_dizin, "05-kiyas.json", KIYAS_BOZUK)
    json_yol = cikti_dizin.parent / "capraz-denetim.json"

    kod, _cikti = _cli(cikti_dizin, extra=["--json", str(json_yol)])

    assert kod == 1
    assert json_yol.is_file()
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert sonuc["tutarli"] is False
    assert sonuc["kopuk_sayisi"] >= 4
    tipler = {k["tip"] for k in sonuc["kopuk_referanslar"]}
    assert "DELIL_GRAFTA_YOK" in tipler


# ── (2) temiz (tutarlı) üçlü → exit 0 ───────────────────────────────────────

def test_temiz_uclu_kopukluk_yok_exit0(cikti_dizin):
    _yaz(cikti_dizin, "01-illiyet-graf.json", GRAF_TEMIZ)
    _yaz(cikti_dizin, "04-vakia.json", VAKIA_TEMIZ)
    _yaz(cikti_dizin, "05-kiyas.json", KIYAS_TEMIZ)

    kod, cikti = _cli(cikti_dizin)

    assert kod == 0, f"tutarlı üçlü exit 0 üretmeliydi; çıktı:\n{cikti}"
    assert "KOPUK REFERANS YOK" in cikti


def test_temiz_uclu_json_ciktisinda_tutarli_true(cikti_dizin):
    _yaz(cikti_dizin, "01-illiyet-graf.json", GRAF_TEMIZ)
    _yaz(cikti_dizin, "04-vakia.json", VAKIA_TEMIZ)
    _yaz(cikti_dizin, "05-kiyas.json", KIYAS_TEMIZ)
    json_yol = cikti_dizin.parent / "capraz-denetim.json"

    kod, _cikti = _cli(cikti_dizin, extra=["--json", str(json_yol)])
    assert kod == 0
    sonuc = json.loads(json_yol.read_text(encoding="utf-8"))
    assert sonuc["tutarli"] is True
    assert sonuc["kopuk_sayisi"] == 0
    assert sonuc["kopuk_referanslar"] == []


# ── (3) eksik dosya(lar) → çökme yok ────────────────────────────────────────

def test_hicbir_dosya_yokken_cokmez_exit0(cikti_dizin):
    """Boş bir cikti dizini (üç dosyadan hiçbiri üretilmemiş) — script
    çökmemeli; 'henüz üretilmemiş' deyip denetimi atlamalı."""
    kod, cikti = _cli(cikti_dizin)
    assert kod == 0, f"hiçbir dosya yokken çökme olmamalı; çıktı:\n{cikti}"
    assert "henüz üretilmemiş" in cikti
    assert "en az iki dosya gerekli" in cikti


def test_dizin_hic_yokken_cokmez_exit0():
    """--cikti-dizin hiç var olmayan bir yol olsa bile çökme yok."""
    tmp = pathlib.Path(tempfile.mkdtemp())
    olmayan = tmp / "hic-yok" / "cikti"
    kod, cikti = _cli(olmayan)
    assert kod == 0, f"olmayan dizin çökmemeli; çıktı:\n{cikti}"


def test_tek_dosya_varken_yetersiz_denetim_atlanir_cokmez(cikti_dizin):
    """Yalnız bir dosya (graf) mevcutken çapraz denetim için en az iki dosya
    gerektiğinden denetim atlanır; script yine de çökmeden exit 0 verir."""
    _yaz(cikti_dizin, "01-illiyet-graf.json", GRAF_TEMIZ)
    kod, cikti = _cli(cikti_dizin)
    assert kod == 0
    assert "en az iki dosya gerekli" in cikti


def test_bozuk_json_dosyasi_okunamadi_diye_atlanir_cokmez(cikti_dizin):
    """Bir dosya bozuk JSON içerse bile script çökmemeli; o dosyayı
    'okunamadı' diye işaretleyip devam etmeli."""
    (cikti_dizin / "01-illiyet-graf.json").write_text("{ gecersiz json", encoding="utf-8")
    _yaz(cikti_dizin, "04-vakia.json", VAKIA_TEMIZ)
    _yaz(cikti_dizin, "05-kiyas.json", KIYAS_TEMIZ)

    kod, cikti = _cli(cikti_dizin)
    assert kod in (0, 1)  # çökme yok; graf atlanır, vakia+kiyas ile denetim sürer
    assert "okunamadı" in cikti

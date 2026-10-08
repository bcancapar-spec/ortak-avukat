# -*- coding: utf-8 -*-
"""v0.5.18 — GİZLİ TALİMAT İFŞASI, Faz B (dilekçeye bağlama) testleri.

Görev 10 (2026-10-07). Bu dosya Faz B'nin kilit testlerini taşır; ilk kayıt
Y-2'dir (Görev 4 yeniden incelemesi): `gizli_talimat_ifsa._sira_anahtari`
künye `no` alanını `isdigit()` ile sınıyor, ardından `int()` çağırıyordu —
`"²".isdigit()` True iken `int("²")` ValueError fırlatır; K-1 ağı bunu
yakalayıp TÜM koşuyu DENETLENEMEDI/3'e düşürüyordu (tek bozuk `no` bütün
ifşayı susturuyordu). `isdecimal()` ile `int()` birebir uyumludur.
Fikstür sentetiktir (anayasa m.7).
"""
import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
MOTOR = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts" / "gizli_talimat_ifsa.py"


@pytest.fixture(scope="module")
def gti():
    spec = importlib.util.spec_from_file_location("v0518_ifsa_faz_b_gti", MOTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_y2_sira_anahtari_unicode_ust_simge_rakami_int_ile_uyumlu(gti):
    """Y-2: `no="²"` (üst simge iki) — `isdigit()` True ama `int()` çözmez.
    Beklenen: istisna YOK; sayı olmayan `no` gibi sona düşer ((1, 0) kolu).
    Gerçek ondalık rakamlar (ASCII ve Arap-Hint) eskisi gibi sayısal sıralanır."""
    anahtar = gti._sira_anahtari({"no": "²", "kaynak": "ek.udf"})
    assert anahtar[0] == (1, 0), anahtar
    assert gti._sira_anahtari({"no": "12", "kaynak": "a.udf"})[0] == (0, 12)
    assert gti._sira_anahtari({"no": "١٢", "kaynak": "b.udf"})[0] == (0, 12)
    assert gti._sira_anahtari({"no": None, "kaynak": "c.udf"})[0] == (1, 0)
    # kaynak kilidi: `isdigit(` motorda artık geçmez (sessiz geri dönüş olmasın)
    src = MOTOR.read_text(encoding="utf-8")
    assert ".isdigit(" not in src and ".isdecimal(" in src

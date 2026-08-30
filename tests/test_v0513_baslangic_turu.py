# -*- coding: utf-8 -*-
"""v0.5.13 — SÜRE BAŞLANGIÇ TÜRÜ ÇATALI (pratikçi hakem heyeti, tez 1).

Saha gerekçesi: bir kanun yolu süresinin tebliğden mi, tefhimden mi, öğrenmeden
mi işlediği dosyanın kaderidir. MCP teyidi (2026-08-27) iki farklı rejimin bir
arada yaşadığını gösterdi: CMK m.268 itiraz **öğrenme gününden**, m.273/291
istinaf-temyiz **gerekçeli kararın tebliğinden**. Aynı dosyada iki süreyi tek
formülle hesaplamak hata üretir.

Mühendis heyetinin şartları (bu testler onları kilitler):
  M2 — yeni parametre `hesapla()` imzasının SONUNA eklenir (mevcut testler
       altıncı argümanı POZİSYONEL geçiyor; araya girmek onları kırar).
  M1 — "belirsiz" değerinde tek kayda iki tarih sıkıştırılmaz; çağıran iki
       ayrı senaryo alır ve ERKEN tarihe göre plan yapar.
  M1 — enum aritmetiği DEĞİŞTİRMEZ: aynı tarih + aynı süre → aynı son gün.
       Kazanç görünürlükte (rapor satırı), hesapta değil.
  M3 — varsayılan davranış birebir korunur (parametre verilmezse hiçbir fark
       yoktur; eski çağrılar ve eski dava klasörleri etkilenmez).

Tamamen ağsız/deterministik.
"""
import importlib.util
import pathlib
from datetime import date

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-sure" /
          "scripts" / "hesapla_sure.py")


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("v0513_hesapla", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


TEBLIG = date(2026, 3, 2)


def test_varsayilan_davranis_degismedi(mod):
    """M3 kilidi: parametre verilmezse sonuç birebir eskisi gibi."""
    eski = mod.hesapla(TEBLIG, 2, "hafta", "hukuk", "usul", False)
    yeni = mod.hesapla(TEBLIG, 2, "hafta", "hukuk", "usul", False, None)
    assert eski[0] == yeni[0]


def test_imza_sonuna_eklendi(mod):
    """M2 kilidi: yeni parametre EN SONDA; altıncı argüman hâlâ istisna bayrağı."""
    import inspect
    adlar = list(inspect.signature(mod.hesapla).parameters)
    assert adlar[5] == "adli_tatil_istisna", "6. parametre yerini korumalı"
    assert adlar[-1] == "baslangic_turu", "yeni parametre imzanın SONUNDA olmalı"


@pytest.mark.parametrize("tur", ["teblig", "tefhim", "ogrenme", "olay"])
def test_aritmetigi_degistirmez(mod, tur):
    """M1 kilidi: başlangıç türü sonucu DEĞİŞTİRMEZ (görünürlük kazancı)."""
    temel = mod.hesapla(TEBLIG, 2, "hafta", "hukuk", "usul", False)[0]
    with_tur = mod.hesapla(TEBLIG, 2, "hafta", "hukuk", "usul", False, tur)[0]
    assert temel == with_tur


def test_rapora_gorunur_satir_duser(mod):
    _son, rapor, _uy = mod.hesapla(TEBLIG, 2, "hafta", "hukuk", "usul",
                                   False, "tefhim")
    metin = " ".join(rapor)
    assert "tefhim" in metin.lower()


def test_belirsiz_iki_senaryo_uyarisi(mod):
    """M1 kilidi: 'belirsiz' tek tarihe indirgenmez — çağıran uyarılır.

    NOT (Türkçe tuzağı): `"BELİRSİZ".lower()` → `"beli̇rsi̇z"` (İ, i + birleşik
    nokta olur) — bu yüzden karşılaştırma küçültmeden, yazıldığı gibi yapılır.
    """
    _son, rapor, uyarilar = mod.hesapla(TEBLIG, 2, "hafta", "hukuk", "usul",
                                        False, "belirsiz")
    hepsi = " ".join(list(rapor) + list(uyarilar))
    assert "BELİRSİZ" in hepsi
    assert "İKİ senaryo" in hepsi, "iki senaryo şartı yazılmalı"
    assert "ERKEN" in hepsi, "belirsizde ERKEN tarih esası yazılmalı"


def test_gecersiz_tur_sessizce_yutulmaz(mod):
    """Yanlış değer sessizce 'teblig' sayılmaz — görünür uyarı düşer."""
    _son, rapor, uyarilar = mod.hesapla(TEBLIG, 2, "hafta", "hukuk", "usul",
                                        False, "zart")
    assert any("zart" in s.lower() or "tanınmayan" in s.lower()
               for s in list(rapor) + list(uyarilar))


def test_cli_bayragi_var(mod):
    """CLI'da opsiyonel bayrak olarak sunulur (zorunlu DEĞİL — Fable daraltması)."""
    kaynak = SCRIPT.read_text(encoding="utf-8")
    assert "--baslangic-turu" in kaynak
    assert "tefhim" in kaynak

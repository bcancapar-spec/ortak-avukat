# -*- coding: utf-8 -*-
"""oa-gizlilik / gizlilik_tara.py için testler.

Script'i dosya-yolundan (importlib.util) yükler — skill dizinleri paket değildir,
farklı klasörlerde durur. Yol bağımsızlığı için pathlib + repo köküne göre göreli yol.
"""
import importlib.util
import pathlib

import pytest

# Bu dosya: <repo>/tests/test_gizlilik.py  →  repo kökü iki üst dizin.
REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-gizlilik" / "scripts" / "gizlilik_tara.py"


def _load():
    assert SCRIPT.is_file(), f"gizlilik_tara.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("gizlilik_tara", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


giz = _load()


# ── tara(): strict / balanced ────────────────────────────────────────────────

def test_strict_saglik_ceza_deny_dolu():
    """strict modda sağlık + ceza metni → deny listesi 'guclu' unsurlarla dolu."""
    metin = "Muvekkilin teshis raporu var; adli sicil kaydinda mahkumiyet gorunuyor."
    deny, ask = giz.tara(metin, "strict")
    assert deny, "strict modda güçlü hassas veri deny üretmeliydi"
    adlar = " ".join(ad for _s, ad in deny)
    assert "Sağlık" in adlar
    assert "Ceza" in adlar or "sabıka" in adlar.lower()


def test_balanced_saglik_ask_dolu_REGRESYON():
    """ESKİ BUG regresyonu: balanced modda sağlık verisi ASK üretmeliydi ama
    'and' kısa-devre bug'ı yüzünden hiç uyarı üretmiyordu. Bu test onu yakalar."""
    metin = "Muvekkilin psikiyatri teshis raporu dosyada mevcut."
    deny, ask = giz.tara(metin, "balanced")
    # balanced: güçlü hassas veri DENY değil, ASK olur.
    assert not deny, "balanced modda sağlık verisi DENY olmamalı (ASK olmalı)"
    assert ask, "REGRESYON: balanced modda sağlık verisi ASK üretmedi (eski bug geri geldi)"
    assert any("Sağlık" in ad for _s, ad in ask)


# ── tckn_gecerli() ───────────────────────────────────────────────────────────

def test_tckn_gecerli_dogru():
    assert giz.tckn_gecerli("10000000146") is True


def test_tckn_gecersiz():
    assert giz.tckn_gecerli("12345678901") is False
    assert giz.tckn_gecerli("00000000000") is False  # ilk hane 0
    assert giz.tckn_gecerli("123") is False           # 11 hane değil


# ── luhn_gecerli() ───────────────────────────────────────────────────────────

def test_luhn_gecerli_dogru():
    assert giz.luhn_gecerli("4111111111111111") is True


def test_luhn_gecersiz():
    assert giz.luhn_gecerli("1234567890123456") is False
    assert giz.luhn_gecerli("abc") is False


# ── maskele() ────────────────────────────────────────────────────────────────

def test_maskele_tckn_kart_parola():
    metin = "TCKN 10000000146 kart 4111 1111 1111 1111 parola: gizli123"
    cikti = giz.maskele(metin)
    # Ham hassas değerler artık görünmemeli.
    assert "10000000146" not in cikti
    assert "4111" not in cikti
    assert "gizli123" not in cikti
    # Maske etiketleri yerleşmiş olmalı.
    assert "[TCKN-MASKELİ]" in cikti
    assert "[KART/HESAP-MASKELİ]" in cikti
    assert "[MASKELİ]" in cikti

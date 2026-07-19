# -*- coding: utf-8 -*-
"""oa-sure / sure_nobetci.py için testler.

Bu script Fable-tespitli TESTSİZ release-kapısı scriptlerinden biridir:
`_oa/sureler.json` defterini BUGÜNE göre tarayıp geçmiş/yaklaşan/ileri
sınıflaması üreten ve exit koduyla "acil süre var mı" sinyalini veren bu
mekanizma hiçbir test doğrulamıyordu.

Script BUGÜNÜ `date.today()` ile okuduğu için (importlib ile sabit bir
tarihe enjekte edilmesi elverişsiz), testler tarihleri ÇALIŞMA ANINDAKİ
gerçek bugüne göre GÖRELİ üretir (dünkü/gelecek hafta/çok ileri tarih gibi)
— sabit takvim tarihine bağlı KIRILGAN olmaz.

Kanonik defter yolu `<kök>/_oa/sureler.json`dır; her test tempfile
tabanlı izole bir kök kullanır, gerçek repo hiç dokunulmaz.
"""
import json
import pathlib
import subprocess
import sys
import tempfile
from datetime import date, timedelta

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-sure"
          / "scripts" / "sure_nobetci.py")


def _cli(kok):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--kok", str(kok)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


@pytest.fixture
def izole_kok():
    return pathlib.Path(tempfile.mkdtemp())


def _defter_yaz(kok, kayitlar):
    oa = kok / "_oa"
    oa.mkdir(parents=True, exist_ok=True)
    (oa / "sureler.json").write_text(
        json.dumps(kayitlar, ensure_ascii=False), encoding="utf-8")


def test_script_mevcut():
    assert SCRIPT.is_file(), f"sure_nobetci.py bulunamadı: {SCRIPT}"


# ── geçmiş + yaklaşan + ileri kayıtlı örnek defter → doğru sınıflama ────────

def test_gecmis_yaklasan_ileri_dogru_siniflanir_exit3(izole_kok):
    bugun = date.today()
    gecmis = (bugun - timedelta(days=5)).isoformat()
    yaklasan = (bugun + timedelta(days=3)).isoformat()  # D-7 penceresi içinde
    ileri = (bugun + timedelta(days=120)).isoformat()   # D-7 penceresi dışında

    _defter_yaz(izole_kok, [
        {"son_gun": gecmis, "aciklama": "Gecmis sure - istinaf", "tur": "usul"},
        {"son_gun": yaklasan, "aciklama": "Yaklasan sure - temyiz", "tur": "usul"},
        {"son_gun": ileri, "aciklama": "Ileri sure - zamanasimi", "tur": "maddi"},
    ])

    kod, cikti = _cli(izole_kok)

    assert kod == 3, f"en az bir geçmiş+yaklaşan süre varken exit 3 beklenir; çıktı:\n{cikti}"
    assert "1 GEÇMİŞ" in cikti
    assert "1 YAKLAŞAN" in cikti
    assert "1 İLERİ" in cikti
    assert "GEÇMİŞ" in cikti and "Gecmis sure - istinaf" in cikti
    assert "yaklaşıyor" in cikti and "Yaklasan sure - temyiz" in cikti
    assert "Ileri sure - zamanasimi" in cikti
    # en yakın/geçmiş üste sıralanmalı: geçmiş kaydın satırı yaklaşandan önce basılmalı
    assert cikti.index("Gecmis sure - istinaf") < cikti.index("Yaklasan sure - temyiz")
    assert cikti.index("Yaklasan sure - temyiz") < cikti.index("Ileri sure - zamanasimi")


def test_bugun_son_gun_gecmis_gibi_acil_sayilir_exit3(izole_kok):
    bugun = date.today().isoformat()
    _defter_yaz(izole_kok, [{"son_gun": bugun, "aciklama": "Tam bugun dolan sure", "tur": "usul"}])

    kod, cikti = _cli(izole_kok)
    assert kod == 3
    assert "1 BUGÜN" in cikti
    assert "BUGÜN — SON GÜN" in cikti


def test_yalniz_ileri_tarihli_kayitlarda_acil_yok_exit0(izole_kok):
    ileri = (date.today() + timedelta(days=200)).isoformat()
    _defter_yaz(izole_kok, [{"son_gun": ileri, "aciklama": "Cok ileri sure", "tur": "maddi"}])

    kod, cikti = _cli(izole_kok)
    assert kod == 0, f"yalnız ileri tarihli kayıtta exit 0 beklenir; çıktı:\n{cikti}"
    assert "Acil süre yok" in cikti


# ── bozuk/tarihsiz kayıt → çökmeden raporlanır ──────────────────────────────

def test_bozuk_tarihli_kayit_cokmeden_raporlanir_exit3(izole_kok):
    _defter_yaz(izole_kok, [{"son_gun": "gecersiz-tarih", "aciklama": "Bozuk kayit", "tur": "usul"}])
    kod, cikti = _cli(izole_kok)
    assert kod == 3
    assert "BOZUK" in cikti
    assert "OKUNAMADI" in cikti


# ── sarmalayıcı şema ('flagler') da desteklenir ─────────────────────────────

def test_flagler_sarmalayici_semasi_da_okunur(izole_kok):
    yaklasan = (date.today() + timedelta(days=1)).isoformat()
    _defter_yaz(izole_kok, {"flagler": [
        {"tarih": yaklasan, "aciklama": "Sarmalayici semali kayit", "kural": "hmk_istinaf", "tur": "usul"},
    ]})
    kod, cikti = _cli(izole_kok)
    assert kod == 3
    assert "Sarmalayici semali kayit" in cikti


# ── defter yok → çökme yok, exit 0 ──────────────────────────────────────────

def test_defter_yok_cokmez_exit0(izole_kok):
    """izole_kok'ta _oa/sureler.json hiç yaratılmadı — script çökmemeli,
    kullanıcıyı oa-sure ile eklemeye yönlendirip exit 0 vermeli."""
    kod, cikti = _cli(izole_kok)
    assert kod == 0, f"defter yokken exit 0 beklenir (çökme yok); çıktı:\n{cikti}"
    assert "Süre kaydı yok" in cikti


def test_defter_bos_liste_cokmez_exit0(izole_kok):
    _defter_yaz(izole_kok, [])
    kod, cikti = _cli(izole_kok)
    assert kod == 0
    assert "boş" in cikti


def test_defter_bozuk_json_exit1(izole_kok):
    oa = izole_kok / "_oa"
    oa.mkdir(parents=True, exist_ok=True)
    (oa / "sureler.json").write_text("{ gecersiz json", encoding="utf-8")
    kod, cikti = _cli(izole_kok)
    assert kod == 1
    assert "HATA" in cikti

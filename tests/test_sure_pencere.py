# -*- coding: utf-8 -*-
"""M5 (Paket D, v0.5.5) — hesapla_sure.py SÜRE PENCERE BİNDİRME kontrolü
(--pencereler). Birden çok süre kaydının [teblig+1, son_gün] pencerelerinin
PAIRWISE çakışıp çakışmadığını deterministik olarak raporlar.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-sure" / "scripts" / "hesapla_sure.py"


def _load():
    spec = importlib.util.spec_from_file_location("hesapla_sure", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hs = _load()


def _cli(args, cwd):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _yaz(tmp_path, kayitlar, ad="pencereler.json"):
    yol = tmp_path / ad
    yol.write_text(json.dumps(kayitlar, ensure_ascii=False), encoding="utf-8")
    return yol


def test_cakisan_pencereler_bindirme_uretir(tmp_path):
    yol = _yaz(tmp_path, [
        {"ad": "İtiraz süresi", "teblig": "2026-05-20", "kural": "hmk_istinaf"},
        {"ad": "Cevap süresi", "teblig": "2026-05-25", "sure": 2, "birim": "hafta"},
    ])
    kod, cikti = _cli(["--pencereler", str(yol)], cwd=tmp_path)
    assert kod == 0
    assert "BİNDİRME" in cikti
    assert "İtiraz süresi" in cikti and "Cevap süresi" in cikti
    assert "ÇAKIŞIYOR" in cikti


def test_ayrik_pencereler_bindirme_uretmez(tmp_path):
    yol = _yaz(tmp_path, [
        {"ad": "Süre-1", "teblig": "2026-01-05", "kural": "hmk_istinaf"},
        {"ad": "Süre-2", "teblig": "2026-06-01", "kural": "hmk_istinaf"},
    ])
    kod, cikti = _cli(["--pencereler", str(yol)], cwd=tmp_path)
    assert kod == 0
    assert "Bindirme yok" in cikti
    assert "ÇAKIŞIYOR" not in cikti


def test_json_cikti_dosyasi_yazilir(tmp_path):
    yol = _yaz(tmp_path, [
        {"ad": "İtiraz süresi", "teblig": "2026-05-20", "kural": "hmk_istinaf"},
        {"ad": "Cevap süresi", "teblig": "2026-05-25", "sure": 2, "birim": "hafta"},
    ])
    cikti_yol = tmp_path / "sonuc.json"
    kod, _c = _cli(["--pencereler", str(yol), "--pencereler-json", str(cikti_yol)], cwd=tmp_path)
    assert kod == 0
    sonuc = json.loads(cikti_yol.read_text(encoding="utf-8"))
    assert len(sonuc["pencereler"]) == 2
    assert len(sonuc["bindirmeler"]) == 1
    assert sonuc["bindirmeler"][0]["a"] == "İtiraz süresi"
    assert sonuc["bindirmeler"][0]["b"] == "Cevap süresi"


def test_bilinmeyen_kural_atlanir_cokmez(tmp_path):
    yol = _yaz(tmp_path, [
        {"ad": "Geçersiz", "teblig": "2026-05-20", "kural": "olmayan_kural"},
        {"ad": "Geçerli", "teblig": "2026-05-20", "kural": "hmk_istinaf"},
    ])
    kod, cikti = _cli(["--pencereler", str(yol)], cwd=tmp_path)
    assert kod == 0
    assert "bilinmeyen kural" in cikti
    assert "Geçerli" in cikti


# ── M5 düzeltmesi (Paket D sınav bulgusu, KUCUK) — çöken kapı sınıfı: kök
# nesne liste DEĞİLSE veya liste öğeleri sözlük DEĞİLSE korumasız traceback
# yerine nazik HATA/⚠ mesajıyla durmalı ────────────────────────────────────

def test_sozluk_kok_nesne_korumasiz_traceback_vermez(tmp_path):
    """`{\"kayitlar\": [...]}` gibi makul bir kullanıcı hatası — kök nesne
    LİSTE değil SÖZLÜK — AttributeError traceback yerine nazik HATA ile durmalı."""
    yol = tmp_path / "pencereler.json"
    yol.write_text(json.dumps({"kayitlar": [
        {"ad": "A", "teblig": "2026-05-20", "kural": "hmk_istinaf"},
    ]}, ensure_ascii=False), encoding="utf-8")
    kod, cikti = _cli(["--pencereler", str(yol)], cwd=tmp_path)
    assert kod != 0
    assert "Traceback" not in cikti
    assert "HATA" in cikti and "LİSTE" in cikti


def test_liste_ogesi_sozluk_degilse_atlanir_cokmez(tmp_path):
    yol = _yaz(tmp_path, [
        "bu bir string, sözlük değil",
        {"ad": "Geçerli", "teblig": "2026-05-20", "kural": "hmk_istinaf"},
    ])
    kod, cikti = _cli(["--pencereler", str(yol)], cwd=tmp_path)
    assert kod == 0
    assert "Traceback" not in cikti
    assert "sözlük değil" in cikti
    assert "Geçerli" in cikti


# ═══════════════════════════════════════════════════════════════════════════
# DÜZELTME (v0.5.5 şerh turu — Ş13 ÖNEMLİ, BLOKER-sınıfı fail-open):
# `_pencere_kontrol` SIFIR kayıt çözülse bile (tüm kayıtlar bozuk/eksikse)
# HİÇBİR şey çözülmediğine bakmadan '>>> Bindirme yok — pencereler ayrık. <<<'
# OLGU BEYANI basıyordu — mekanik körlüğü olgu beyanına ÇEVİRME hatası.
# ═══════════════════════════════════════════════════════════════════════════

def test_tum_kayitlar_bozuk_denetlenemedi_exit_farkli_ayrik_basmaz(tmp_path):
    yol = _yaz(tmp_path, [
        {"ad": "Geçersiz kural", "teblig": "2026-05-20", "kural": "olmayan_kural"},
        {"ad": "Geçersiz birim", "teblig": "2026-05-20", "sure": 10, "birim": "yil-degil"},
        {"ad": "Bozuk tarih", "teblig": "tarih-degil", "kural": "hmk_istinaf"},
    ])
    kod, cikti = _cli(["--pencereler", str(yol)], cwd=tmp_path)
    assert kod != 0, cikti
    assert "ayrık" not in cikti.lower(), (
        f"hiçbir kayıt çözülmediği hâlde 'ayrık' (temiz) hükmü BASILMAMALIYDI:\n{cikti}")
    assert "DENETLENEMEDİ" in cikti


def test_bos_liste_girdisi_aynen_denetlenemedi_davranir(tmp_path):
    yol = _yaz(tmp_path, [])
    kod, cikti = _cli(["--pencereler", str(yol)], cwd=tmp_path)
    assert kod != 0, cikti
    assert "ayrık" not in cikti.lower()
    assert "DENETLENEMEDİ" in cikti


def test_iki_gecerli_bir_bozuk_kayit_json_atlanan_uzunlugu_bir(tmp_path):
    yol = _yaz(tmp_path, [
        {"ad": "A", "teblig": "2026-01-05", "kural": "hmk_istinaf"},
        {"ad": "B", "teblig": "2026-06-01", "kural": "hmk_istinaf"},
        {"ad": "Bozuk", "teblig": "2026-05-20", "kural": "olmayan_kural"},
    ])
    cikti_yol = tmp_path / "sonuc.json"
    kod, cikti = _cli(
        ["--pencereler", str(yol), "--pencereler-json", str(cikti_yol)], cwd=tmp_path)
    assert kod == 0, cikti
    sonuc = json.loads(cikti_yol.read_text(encoding="utf-8"))
    assert len(sonuc["atlanan"]) == 1
    assert sonuc["atlanan"][0]["ad"] == "Bozuk"
    assert sonuc["denetlenen_kayit"] == 2
    assert "DÜŞTÜ" in cikti  # ayrık hükmüne düşen-kayıt şerhi iliştirilir


def test_sure_sifir_alan_eksik_sayilmaz(tmp_path):
    """DÜZELTME (Ş13): eski `k.get("sure") and k.get("birim")` falsy
    kontrolü `sure: 0`ı 'alan eksik' sayıp SESSİZCE düşürüyordu."""
    yol = _yaz(tmp_path, [
        {"ad": "Sıfır süre", "teblig": "2026-05-20", "sure": 0, "birim": "gun"},
    ])
    kod, cikti = _cli(["--pencereler", str(yol)], cwd=tmp_path)
    assert "'kural' VEYA 'sure'+'birim' eksik" not in cikti, cikti


def test_tek_pencere_yapisal_olarak_denetlenemez_mesaji(tmp_path):
    yol = _yaz(tmp_path, [
        {"ad": "Tek", "teblig": "2026-05-20", "kural": "hmk_istinaf"},
    ])
    kod, cikti = _cli(["--pencereler", str(yol)], cwd=tmp_path)
    assert kod == 0, cikti
    assert "Tek pencere" in cikti
    assert "ayrık" not in cikti.lower()


def test_pencere_kontrol_fonksiyonu_dogrudan(tmp_path):
    yol = _yaz(tmp_path, [
        {"ad": "A", "teblig": "2026-05-20", "kural": "hmk_istinaf"},
        {"ad": "B", "teblig": "2026-05-25", "kural": "hmk_istinaf"},
    ])
    cikti_yol = tmp_path / "sonuc.json"
    hs._pencere_kontrol(str(yol), str(cikti_yol))
    sonuc = json.loads(cikti_yol.read_text(encoding="utf-8"))
    assert len(sonuc["pencereler"]) == 2

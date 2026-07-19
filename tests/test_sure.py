# -*- coding: utf-8 -*-
"""oa-sure / hesapla_sure.py için ALTIN VAKA testleri.

Strateji: modül import edilebiliyorsa hesapla() doğrudan çağrılır (birincil yol).
İmport başarısızsa CLI subprocess ile çağrılıp 'HESAPLANAN SON GÜN' satırı regex'le
çekilir (yedek yol). Beklenen tarihler scriptin GERÇEK çıktısından türetildi
(uydurma değil — golden değerler bu dosyada sabitlenmiştir).

Altın vakalar (hepsi HMK istinaf = 2 hafta, hukuk yargısı):
  (a) Hafta sonu kayması : teblig 2026-06-06 (Cmt) → ham 2026-06-20 (Cmt) → 2026-06-22 (Pzt)
  (b) Adli tatil (HMK m.104): teblig 2026-07-15 → ham 20 Tem–31 Ağu içinde → 2026-09-07 (Pzt)
  (c) Normal iş günü     : teblig 2026-05-20 (Çrş) → ham 2026-06-03 (Çrş), kayma yok
"""
import importlib.util
import pathlib
import re
import subprocess
import sys
from datetime import date

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-sure" / "scripts" / "hesapla_sure.py"

# HMK m.345 istinaf: 2 hafta.
HMK_ISTINAF = (2, "hafta")

# Golden vakalar: (teblig, beklenen_son_gun_ISO)
ALTIN = {
    "hafta_sonu_kaymasi": ("2026-06-06", "2026-06-22"),
    "adli_tatil":         ("2026-07-15", "2026-09-07"),
    "normal_is_gunu":     ("2026-05-20", "2026-06-03"),
}


def _load_module():
    """hesapla_sure'yi importlib ile yükle; başarısızsa None döndür (subprocess'e düş)."""
    try:
        spec = importlib.util.spec_from_file_location("hesapla_sure", SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


MOD = _load_module()

_SON_GUN_RE = re.compile(r"HESAPLANAN SON G[ÜU]N\s*:\s*(\d{4}-\d{2}-\d{2})")


def _cli_son_gun(teblig, kural="hmk_istinaf", yargi="hukuk"):
    """CLI'ı subprocess ile çağırır, stdout'tan son günü regex'le çeker (yedek yol)."""
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--teblig", teblig, "--kural", kural, "--yargi", yargi],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert cp.returncode == 0, f"CLI hata verdi: {cp.stderr}"
    m = _SON_GUN_RE.search(cp.stdout)
    assert m, f"'HESAPLANAN SON GÜN' satırı bulunamadı:\n{cp.stdout}"
    return m.group(1)


def _cli_run(*extra_args, teblig, kural="hmk_istinaf", yargi="hukuk"):
    """CLI'ı ek bayraklarla (ör. --adli-tatil-istisna, --uets) koşar, tüm stdout'u döndürür."""
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--teblig", teblig, "--kural", kural, "--yargi", yargi, *extra_args],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert cp.returncode == 0, f"CLI hata verdi: {cp.stderr}"
    return cp.stdout


def _son_gun(teblig, yargi="hukuk"):
    """Birincil: modül import → hesapla() doğrudan. Yedek: CLI subprocess."""
    if MOD is not None:
        miktar, birim = HMK_ISTINAF
        son, _rapor, _uy = MOD.hesapla(date.fromisoformat(teblig), miktar, birim, yargi, "usul")
        return son.isoformat()
    return _cli_son_gun(teblig, yargi=yargi)


def test_modul_import_edilebilir():
    """hesapla_sure importlib ile yüklenebilmeli (birincil test yolu)."""
    assert MOD is not None, "hesapla_sure importlib ile yüklenemedi"
    assert hasattr(MOD, "hesapla")


@pytest.mark.parametrize("ad", list(ALTIN.keys()))
def test_altin_vaka(ad):
    teblig, beklenen = ALTIN[ad]
    assert _son_gun(teblig) == beklenen, f"{ad}: teblig={teblig} beklenen={beklenen}"


def test_hafta_sonu_pazartesiye_kayar():
    """(a) Son gün Cumartesi'ye denk → ilk iş günü Pazartesi'ye kayar (HMK m.93)."""
    son = _son_gun("2026-06-06")
    assert son == "2026-06-22"
    if MOD is not None:
        assert MOD._gun_adi(date.fromisoformat(son)) == "Pazartesi"


def test_adli_tatil_07_eylule_uzar():
    """(b) HMK istinaf son günü adli tatile (20 Tem–31 Ağu) düşerse 07 Eylül'e uzar."""
    son = _son_gun("2026-07-15")
    assert son == "2026-09-07"
    if MOD is not None:
        assert MOD._gun_adi(date.fromisoformat(son)) == "Pazartesi"


def test_normal_is_gunu_kaymaz():
    """(c) Ham bitiş normal iş gününe denk → kayma yok."""
    assert _son_gun("2026-05-20") == "2026-06-03"


def test_cli_yolu_calisir():
    """Yedek yolun (CLI subprocess + regex) da fiilen çalıştığını doğrula."""
    assert _cli_son_gun("2026-07-15") == "2026-09-07"


# ── YENİ: HMK m.103 ADLİ TATİL İSTİSNASI ─────────────────────────────────────
# Golden (scriptin GERÇEK çıktısından türetildi): nafaka/iş davası istinafı
# (HMK istinaf = 2 hafta, hukuk yargısı), teblig 2026-08-01 (Cumartesi).
#   Ham bitiş 2026-08-15 (Cumartesi), adli tatil (20 Tem–31 Ağu) penceresinde.
#   Bayraksız (VARSAYILAN) → 31 Ağu + 1 hafta uzatması → 2026-09-07 (Pzt).
#   --adli-tatil-istisna (HMK m.103 işi) → UZAMAZ; ham bitiş yalnız hafta sonu
#   kaymasıyla 2026-08-15 (Cmt) → 2026-08-17 (Pzt).
ISTISNA_TEBLIG = "2026-08-01"
ISTISNA_BEKLENEN = "2026-08-17"   # uzatma YOK, yalnız Cmt→Pzt kayması
DEFAULT_BEKLENEN = "2026-09-07"   # bayraksız: adli tatil uzatması korunur
ISTISNA_NOTU = "HMK m.103 istisna işi — adli tatil uzatması uygulanmadı"


def test_adli_tatil_istisna_modul_uzatmaz():
    """(a) HMK m.103 istisna bayrağı ile son gün UZAMAZ; ham bitişin hafta sonu kayması kalır."""
    if MOD is None:
        pytest.skip("modül import edilemedi; istisna CLI testi ayrıca koşuyor")
    miktar, birim = HMK_ISTINAF
    t = date.fromisoformat(ISTISNA_TEBLIG)
    son_ist, rapor, _uy = MOD.hesapla(t, miktar, birim, "hukuk", "usul", True)
    assert son_ist.isoformat() == ISTISNA_BEKLENEN
    # Bayraksız (varsayılan) davranış AYNEN korunur → uzar
    son_def, _r, _u = MOD.hesapla(t, miktar, birim, "hukuk", "usul", False)
    assert son_def.isoformat() == DEFAULT_BEKLENEN
    assert son_ist != son_def, "istisna bayrağı varsayılandan farklı sonuç vermeli"
    assert any(ISTISNA_NOTU in s for s in rapor), "m.103 istisna notu rapora düşmeli"


def test_adli_tatil_istisna_cli_uzatmaz():
    """(a) CLI --adli-tatil-istisna: son gün 2026-08-17 (uzamaz) ve m.103 notu basılır."""
    out = _cli_run("--adli-tatil-istisna", teblig=ISTISNA_TEBLIG)
    m = _SON_GUN_RE.search(out)
    assert m and m.group(1) == ISTISNA_BEKLENEN, out
    assert ISTISNA_NOTU in out, out


def test_adli_tatil_istisna_varsayilan_bozulmadi():
    """(a) Aynı teblig için BAYRAKSIZ CLI eski davranışı (adli tatil uzatması) korur."""
    out = _cli_run(teblig=ISTISNA_TEBLIG)
    m = _SON_GUN_RE.search(out)
    assert m and m.group(1) == DEFAULT_BEKLENEN, out


# ── YENİ: --uets (7201 m.7/a e-tebligat) +5 gün karine ───────────────────────
# Golden: teblig (=ulaşma/okunma günü) 2026-05-20, HMK istinaf.
#   Senaryo-1 (okunma günü esas): son gün 2026-06-03.
#   Senaryo-2 (yasal karine, ulaşma+5. günün sonu → teblig 2026-05-25): son gün 2026-06-08.
_UETS_S1_RE = re.compile(r"UETS Senaryo-1.*?son g[üu]n\s+(\d{4}-\d{2}-\d{2})")
_UETS_S2_RE = re.compile(r"UETS Senaryo-2.*?son g[üu]n\s+(\d{4}-\d{2}-\d{2})")


def test_uets_karine_5_gun():
    """(b) --uets: iki senaryo basılır; karine senaryosu okunmadan tam 5 gün ileridedir."""
    out = _cli_run("--uets", teblig="2026-05-20")
    m1 = _UETS_S1_RE.search(out)
    m2 = _UETS_S2_RE.search(out)
    assert m1 and m1.group(1) == "2026-06-03", out
    assert m2 and m2.group(1) == "2026-06-08", out
    d1 = date.fromisoformat(m1.group(1))
    d2 = date.fromisoformat(m2.group(1))
    assert (d2 - d1).days == 5, "karine (+5 gün) senaryosu okunma senaryosundan 5 gün ileride olmalı"


def test_kural_tablosu_json_okunuyor():
    """sure_kurallari.json'a taşınan yeni kurallar (CMK/İİK/6183) CLI'da seçilebilir olmalı."""
    for kural, beklenen in (("cmk_itiraz", None), ("iik_sikayet", None), ("amme_6183_m58", None)):
        out = _cli_run(teblig="2026-05-20", kural=kural)
        assert _SON_GUN_RE.search(out), f"{kural}: son gün satırı üretilmedi:\n{out}"


# ── YENİ: İYUK m.8/3 idari yargı çalışmaya-ara uzaması (kritik regresyon) ────
# Golden (scriptin GERÇEK çıktısından türetildi): iyuk_istinaf (30 gün, idari
# yargı), teblig 2026-07-15 → ham bitiş 2026-08-14 (adli tatil/çalışmaya ara
# penceresinde, 20 Tem-31 Ağu) → ara bitimini (31 Ağu) İZLEYEN 1 Eylül'den
# itibaren 7 GÜN (1 Eylül dahil) → 07 Eylül (Pazartesi). ESKİ (hatalı) davranış
# 31 Ağu + 1 gün + 7 gün = 08 Eylül üretiyordu — bu, avukata bir gün GEÇ son gün
# verip süre kaçırma riski doğuran kritik bir hataydı.
IYUK_IDARI_TEBLIG = "2026-07-15"
IYUK_IDARI_BEKLENEN = "2026-09-07"


def test_iyuk_idari_calismaya_ara_dogru_uzuyor():
    """(kritik) İYUK m.8/3 idari dalı: 08 Eylül DEĞİL, 07 Eylül (Pazartesi) üretilmeli."""
    if MOD is None:
        pytest.skip("modül import edilemedi; CLI testi ayrıca koşuyor")
    son, rapor, _uy = MOD.hesapla(date.fromisoformat(IYUK_IDARI_TEBLIG), 30, "gun", "idari", "usul")
    assert son.isoformat() == IYUK_IDARI_BEKLENEN, (
        f"İYUK m.8/3 idari uzaması yanlış: {son.isoformat()} (beklenen {IYUK_IDARI_BEKLENEN}, "
        "eski hatalı davranış 2026-09-08 üretiyordu)"
    )
    assert MOD._gun_adi(son) == "Pazartesi"


def test_iyuk_idari_calismaya_ara_cli():
    """(kritik) Aynı vaka CLI (--kural iyuk_istinaf --yargi idari) üzerinden de 07 Eylül vermeli."""
    out = _cli_run(teblig=IYUK_IDARI_TEBLIG, kural="iyuk_istinaf", yargi="idari")
    m = _SON_GUN_RE.search(out)
    assert m and m.group(1) == IYUK_IDARI_BEKLENEN, out

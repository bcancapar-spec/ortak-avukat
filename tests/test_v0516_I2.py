# -*- coding: utf-8 -*-
"""v0.5.16 — GRUP I2: oa-antitez BİLİRKİŞİ/TEKNİK CEPHESİ + HÂKİM LENSİ +
HAT SIRASI HİZALAMASI.

Kapatılan bulgular (2026-09-06 denetimleri):

  P1-5 / A-20  `antitez_matris.py` STANDART_CEPHELER sekiz cepheyle bilirkişi
               raporunu (Türk hukuk yargılamasının fiilî karar mercii çoğu
               dosyada rapordur) GÖRMÜYORDU: rapor kırılma noktası, HMK m.281
               itiraz stratejisi, HMK m.293 uzman görüşü, HMK m.279/4 hukuki
               nitelendirme yasağı hiçbir cephede zorunlu değildi. 9. cephe
               `bilirkisi_teknik` eklendi. BİLİNÇLİ ETKİ: eski sekiz cepheli
               matrisler artık "AÇIK CEPHE: bilirkisi_teknik" alır — sessiz
               uyum YOK; kör nokta görünür kılınır.
  A-21         SKILL.md'ye HÂKİM LENSİ: çürütme brifine ikinci pas (cephe
               DEĞİL, lens) — oa-kontrol C2 brifiyle aynı cümle.
  P0-3         "Kompozisyon (iki konum)" pipeline sırasıyla hizalandı: erken
               konum = SABİT HAT ADIM 6 (STRATEJİ adım 7'den ÖNCE); oa-strateji
               antitez çıktısını girdi alır.
  (koruma)     `dilekce_denetim.py` [G] ANTİTEZ-CEVAP-ÇAPASI sözleşmesi
               (`_oa/cikti/*antitez*.json` + `duyulmus_curutmeler()`) DEĞİŞMEDİ
               — kanıt testleri aşağıda.

Girdiler tempfile tabanlı İZOLE dizinlerde üretilir; repo dosyalarına
dokunulmaz. Fikstürler sentetiktir (anayasa m.7).
"""
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
ANTITEZ_DIZIN = SKILLS / "oa-antitez"
ANTITEZ = ANTITEZ_DIZIN / "scripts" / "antitez_matris.py"
ANTITEZ_SKILL = ANTITEZ_DIZIN / "SKILL.md"
DILEKCE_DENETIM = SKILLS / "oa-dilekce" / "scripts" / "dilekce_denetim.py"

ESKI_SEKIZ = [
    "usul", "maddi_vakia", "ispat_delil", "hukuki_niteleme", "ictihat",
    "zamanasimi", "defi_karsi_talep", "muvekkil_zaaf",
]
YENI_CEPHE = "bilirkisi_teknik"


def _kos(script, *args):
    cp = subprocess.run(
        [sys.executable, str(script), *[str(a) for a in args]],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return cp.returncode, (cp.stdout or ""), (cp.stderr or "")


def _modul(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def izole_dizin():
    return pathlib.Path(tempfile.mkdtemp())


def _yaz(dizin, ad, veri):
    yol = dizin / ad
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return yol


def _cephe(ad, **ek):
    """Sentetik, ÇÖZÜLMÜŞ bir cephe kaydı (saldırı 'orta', çürütme + teyitli
    dayanak) — matrisi 'TAMAM' hükmüne taşıyacak biçimde."""
    kayit = {
        "cephe": ad,
        "antitez": "Karşı taraf bu cepheden saldırır (sentetik)",
        "guc": "orta",
        "curutme": "Çürütme metni (sentetik)",
        "curutme_dayanak": "HMK m.281 (sentetik teyit)",
        "dayanak_durum": "teyitli",
        "artik_risk": "",
        "duyulmus": False,
    }
    kayit.update(ek)
    return kayit


# ═══════════════════════════════════════════════════════════════════════════
# 1) P1-5 / A-20 — 9. cephe: bilirkisi_teknik
# ═══════════════════════════════════════════════════════════════════════════

def test_iskelet_dokuz_cephe_ve_bilirkisi_teknik_sonda():
    """`--iskelet` artık DOKUZ cephe üretir; `bilirkisi_teknik` 9. sıradadır
    (usul 1. cephe olarak korunur — anayasa m.2)."""
    kod, out, err = _kos(ANTITEZ, "--iskelet")
    assert kod == 0
    sablon = json.loads(out)
    adlar = [c["cephe"] for c in sablon["cepheler"]]
    assert len(adlar) == 9
    assert adlar[:8] == ESKI_SEKIZ, "eski sekizlinin sırası DEĞİŞMEMELİ"
    assert adlar[8] == YENI_CEPHE
    assert sablon["cepheler"][8]["duyulmus"] is False
    # STDERR cephe listesi ve açıklaması
    assert f"[{YENI_CEPHE}]" in err
    for norm in ("HMK m.281", "HMK m.293", "HMK m.279/4"):
        assert norm in err, f"{norm} cephe açıklamasında yok"


def test_standart_cepheler_aciklamasi_bilirkisi_unsurlarini_tasir():
    mod = _modul(ANTITEZ, "antitez_matris_i2")
    assert list(mod.STANDART_CEPHELER)[-1] == YENI_CEPHE
    aciklama = mod.STANDART_CEPHELER[YENI_CEPHE]
    for parca in ("kırılma nokta", "itiraz stratejisi", "HMK m.281",
                  "uzman görüşü", "HMK m.293", "hukuki nitelendirme yasağı",
                  "HMK m.279/4", "tek imza/heyet", "keşif dayanağı"):
        assert parca in aciklama, f"'{parca}' cephe açıklamasında yok"


def test_sekiz_cepheli_eski_matris_bilirkisi_teknik_acik_cephe_alir(izole_dizin):
    """BİLİNÇLİ karakterizasyon değişikliği (P1-5/A-20): v0.5.15'te 'TAMAM'
    hükmü alan sekiz cepheli tam matris artık 'EKSİK' + AÇIK CEPHE
    `bilirkisi_teknik` alır. Sessiz uyum YOKTUR — kör nokta görünür kılınır."""
    veri = {"tez": "Sentetik tez", "cepheler": [_cephe(ad) for ad in ESKI_SEKIZ]}
    yol = _yaz(izole_dizin, "07-antitez-matris.json", veri)
    kod, out, err = _kos(ANTITEZ, "--dogrula", yol)
    assert "Traceback" not in err
    assert "AÇIK CEPHELER" in out
    assert f"✗ {YENI_CEPHE}" in out
    assert "Cephe kapsamı     : 8/9" in out
    assert "Matris bütünlüğü EKSİK" in out
    assert "Matris bütünlüğü TAMAM" not in out


def test_dokuz_cepheli_tam_matris_tamam(izole_dizin):
    veri = {"tez": "Sentetik tez",
            "cepheler": [_cephe(ad) for ad in ESKI_SEKIZ + [YENI_CEPHE]]}
    yol = _yaz(izole_dizin, "07-antitez-matris.json", veri)
    kod, out, err = _kos(ANTITEZ, "--dogrula", yol)
    assert "Traceback" not in err
    assert "AÇIK CEPHELER" not in out
    assert "Cephe kapsamı     : 9/9" in out
    assert "Matris bütünlüğü TAMAM" in out


def test_bilirkisi_teknik_curutulmemis_antitez_yakalanir(izole_dizin):
    """Yeni cephe de eski denetim kurallarına tabidir: güçlü saldırı + ne
    çürütme ne artık risk → ÇÜRÜTÜLMEMİŞ ANTİTEZ."""
    cepheler = [_cephe(ad) for ad in ESKI_SEKIZ]
    cepheler.append(_cephe(YENI_CEPHE, guc="yuksek", curutme="",
                           curutme_dayanak="", dayanak_durum="yok"))
    yol = _yaz(izole_dizin, "07-antitez-matris.json",
               {"tez": "Sentetik tez", "cepheler": cepheler})
    kod, out, err = _kos(ANTITEZ, "--dogrula", yol)
    assert "ÇÜRÜTÜLMEMİŞ ANTİTEZLER" in out
    assert f"✗ {YENI_CEPHE}" in out
    assert "Matris bütünlüğü EKSİK" in out


# ═══════════════════════════════════════════════════════════════════════════
# 4) [G] kapısı sözleşmesi KORUNUR — duyulmus_curutmeler + *antitez*.json
# ═══════════════════════════════════════════════════════════════════════════

def test_duyulmus_curutmeler_sozlesmesi_eski_ve_yeni_matriste_ayni():
    mod = _modul(ANTITEZ, "antitez_matris_i2_g")
    # Eski sekiz cepheli matris — yeni cephe yok; fonksiyon ÇÖKMEZ, aynı döner
    eski = {"tez": "T", "cepheler": [
        _cephe("zamanasimi", duyulmus=True, curutme="zamanaşımı çürütmesi"),
        _cephe("usul", duyulmus=False),
    ]}
    assert mod.duyulmus_curutmeler(eski) == [
        {"cephe": "zamanasimi", "curutme": "zamanaşımı çürütmesi"}]
    # Yeni cephe de aynı sözleşmeyle akar
    yeni = {"tez": "T", "cepheler": [
        _cephe(YENI_CEPHE, duyulmus=True, curutme="rapor hukuki nitelendirme yapmış"),
        _cephe(YENI_CEPHE, duyulmus=True, curutme="   "),   # boş çürütme → dışarıda
    ]}
    assert mod.duyulmus_curutmeler(yeni) == [
        {"cephe": YENI_CEPHE, "curutme": "rapor hukuki nitelendirme yapmış"}]
    # Fail-safe korunur
    assert mod.duyulmus_curutmeler(None) == []
    assert mod.duyulmus_curutmeler({"cepheler": "bozuk"}) == []
    assert mod.duyulmus_curutmeler({"cepheler": [None, 3, "x"]}) == []


def test_dilekce_denetim_G_kapisi_bilirkisi_teknik_cephesini_gorur(izole_dizin):
    """[G] ANTİTEZ-CEVAP-ÇAPASI (oa-dilekce) `_oa/cikti/*antitez*.json` okur ve
    `duyulmus_curutmeler()`i çağırır — yeni cephe için de aynı sözleşme:
    DUYULMUŞ + çürütülmüş ama dilekçede çapasız → [UYARI] satırı."""
    kok = izole_dizin
    cikti = kok / "_oa" / "cikti"
    cikti.mkdir(parents=True)
    curutme = ("Bilirkişi raporu hukuki nitelendirme yaparak sınırını aşmıştır "
               "heyet raporunda görüş ayrılığı gerekçesi bulunmamaktadır")
    _yaz(cikti, "07-antitez-matris.json", {"tez": "T", "cepheler": [
        _cephe(YENI_CEPHE, duyulmus=True, curutme=curutme)]})
    dd = _modul(DILEKCE_DENETIM, "dilekce_denetim_i2")
    uyarilar = dd.antitez_cevap_capasi_uyarilari(
        "Davacı alacağın tahsilini talep eder.", str(kok))
    assert len(uyarilar) == 1
    assert YENI_CEPHE in uyarilar[0] and "DUYULMUŞ" in uyarilar[0]
    # Çapa varsa uyarı yok — sözleşmenin diğer yüzü
    assert dd.antitez_cevap_capasi_uyarilari(curutme, str(kok)) == []


def test_iskelet_ciktisi_dogrudan_G_kapisi_dosyasi_olarak_okunur(izole_dizin):
    """B-26 korunur: `--iskelet > _oa/cikti/07-antitez.json` [G] kapısı için
    geçerli girdidir (9 cepheli şablon dahil)."""
    kod, out, err = _kos(ANTITEZ, "--iskelet")
    cikti = izole_dizin / "_oa" / "cikti"
    cikti.mkdir(parents=True)
    (cikti / "07-antitez.json").write_text(out, encoding="utf-8")
    mod = _modul(ANTITEZ, "antitez_matris_i2_b26")
    m = json.loads((cikti / "07-antitez.json").read_text(encoding="utf-8"))
    assert mod.duyulmus_curutmeler(m) == []      # şablon: hiçbiri duyulmuş değil
    dd = _modul(DILEKCE_DENETIM, "dilekce_denetim_i2_b26")
    assert dd._antitez_matris_dosyalari(str(izole_dizin)) == [
        str(cikti / "07-antitez.json")]


# ═══════════════════════════════════════════════════════════════════════════
# 2) A-21 HÂKİM LENSİ + 3) P0-3 hizalama — SKILL.md metin sözleşmesi
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def skill_metni():
    return ANTITEZ_SKILL.read_text(encoding="utf-8")


def test_skill_dokuz_cephe_ve_mcp_teyit_notu(skill_metni):
    assert "Dokuz sabit **cephe**" in skill_metni
    assert "bilirkişi/teknik" in skill_metni
    assert "Sekiz sabit" not in skill_metni
    assert "sekiz cepheyi" not in skill_metni
    for norm in ("HMK m.279/4", "HMK m.281", "HMK m.293"):
        assert norm in skill_metni
    assert "Mevzuat MCP teyit 2026-09-06" in skill_metni


def test_skill_hakim_lensi_cephe_degil_lens(skill_metni):
    """A-21: oa-kontrol C2 brifiyle AYNI cümle; cephe DEĞİL lens."""
    assert "HÂKİM LENSİ" in skill_metni
    assert ("hâkim bu dosyayı nasıl kapatmak ister: iş yükü, gerekçe alışkanlığı, "
            "daire eğilimi; on dakikada okuyan hâkim tezi anlıyor mu") in skill_metni
    assert "cephe değil" in skill_metni.lower() or "cephe DEĞİL" in skill_metni


def test_skill_kompozisyon_pipeline_sirasiyla_hizali(skill_metni):
    """P0-3: erken konum = SABİT HAT ADIM 6 (STRATEJİ adım 7'den ÖNCE);
    geç konum = YAZIM sonrası / KONTROL öncesi; strateji antitezi girdi alır."""
    bolum = skill_metni.split("## Kompozisyon")[1].split("\n## ")[0]
    assert "ADIM 6" in bolum
    assert "STRATEJİ" in bolum and "adım 7" in bolum
    assert "oa-strateji` antitez çıktısını girdi alır" in bolum
    assert "YAZIM" in bolum and "KONTROL" in bolum
    # Eski, hatalı sıralama imâsı kalmadı ("teslimden önce oa-kontrol ile birlikte" → geç konum tanımı)
    assert "07-antitez" in skill_metni   # [G]/pipeline evrak adı korunur

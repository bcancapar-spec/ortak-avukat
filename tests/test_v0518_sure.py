# -*- coding: utf-8 -*-
"""v0.5.18 — SÜRE MOTORU: kural düzeyinde adli tatil rejimi, eksik kurallar,
AYM/AİHM, tatil takvimi kapısı ve başlangıç kapısı (oa-sure).

Kaynak: 2026-10-03 yetenek denetimi — Y-01…Y-05, Y-08 hukuki doğruluk
bulguları — ve Yargı PRO 12-1/12-2/12-3 skill'lerinin FİKRİ
(metin kopyalanmadı). Her beklenen tarih ya resmî metinden ya da aşağıda künyesi
yazılı gerçek bir Yargıtay/AYM/AİHM kararındaki tarihlerden türetildi — oracle
motorun kendi çıktısı DEĞİLDİR (test_sure.py:188-194 dersi: yanlış oracle hatayı
yeşile boyar). Mevzuat MCP teyidi 2026-10-05:
  İİK m.16, 18, 19, 62, 65, 67, 68, 68/a, 69, 89, 134, 168, 265, 347, 363, 364
  HMK m.20, 92, 93, 103, 104, 127, 139, 140, 317, 345, 361, 394, 397
  CMK m.39, 331 · 6216 m.47 · AYM İçtüzüğü m.64 · 7201 m.7/a, 11, 21, 31, 32, 35, 36
İçtihat (ictihat_getir ile tam metin, 2026-10-05):
  Y. 12. HD E.2025/7548 K.2025/7898; E.2024/7040 K.2024/10869; E.2022/11578
  K.2022/11538; E.2009/1886 K.2009/10134 · Y. 23. HD E.2013/8404 K.2013/7933 ·
  Y. 9. HD E.2016/1261 K.2016/22196 · YCGK E.2013/2-272 K.2013/524;
  E.2021/319 K.2022/846 · Y. 11. CD E.2017/14079 K.2018/2400 ·
  AYM Ramazan Seçen (B. No: 2021/37483, 6/1/2026) · AİHM Sabri Güneş/Türkiye [BD]
  (no. 27396/06, 29.06.2012).
Testler ağsızdır, depoya yazmaz (tmp_path), gerçek dosya/kişi/yol içermez (m.7).
"""
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
from datetime import date, timedelta

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-sure"
SCRIPT = SKILL / "scripts" / "hesapla_sure.py"
NOBETCI = SKILL / "scripts" / "sure_nobetci.py"
KURAL_JSON = SKILL / "scripts" / "sure_kurallari.json"
TATIL_JSON = SKILL / "scripts" / "tatiller.json"
SKILL_MD = SKILL / "SKILL.md"
CIZELGE = SKILL / "references" / "sure-cizelgesi.md"
KAPI_MD = SKILL / "references" / "baslangic-kapisi.md"
GUNLUK = SKILL / "references" / "degisiklik-gunlugu.md"

_SON_GUN_RE = re.compile(r"HESAPLANAN SON G[ÜU]N\s*:\s*(\d{4}-\d{2}-\d{2})")


def _yukle():
    spec = importlib.util.spec_from_file_location("v0518_hesapla_sure", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


H = _yukle()


def _cli(*args, cwd=None):
    """CLI koşar (deftere yazmaz); (rc, stdout+stderr) döndürür."""
    cp = subprocess.run([sys.executable, str(SCRIPT), *args, "--flagsiz"],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(cwd or REPO), timeout=120)
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _son(out):
    m = _SON_GUN_RE.search(out)
    assert m, "son gün satırı yok:\n" + out
    return m.group(1)


def _hesap(teblig, kural, yargi="hukuk", **kw):
    miktar, birim, _k = H.KURALLAR[kural]
    return H.hesapla(teblig, miktar, birim, yargi, "usul", kural=kural, **kw)


# ══════════════════════════════════════════════════════════════════════════
# Y-01 — İCRA SÜRELERİ ADLİ TATİLDE UZAMAZ (İİK m.18/1 + HMK m.103/1-h)
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("kural,beklenen", [
    ("iik_istinaf", date(2026, 8, 24)),   # İİK m.363: 2 hafta, tebliğden
    ("iik_temyiz", date(2026, 8, 24)),    # İİK m.364/2: 2 hafta, tebliğden
    ("iik_sikayet", date(2026, 8, 17)),   # İİK m.16/1: 7 gün
])
def test_Y01_icra_suresi_adli_tatilde_UZAMAZ(kural, beklenen):
    """Denetim örneği: 10.08.2026 tebliğde motor 07.09 veriyordu (HMK m.104 ile
    bir hafta uzatma). İcra mahkemesine arz edilen hususlar ivedidir (İİK m.18/1),
    HMK m.103/1-h gereği tatilde görülür; Y. 12. HD: 'bu sürenin adli tatilin
    bitiminden itibaren bir hafta daha uzatılmış sayılmasına imkan yoktur'."""
    son, rapor, _u = _hesap(date(2026, 8, 10), kural)
    assert son == beklenen
    assert son != date(2026, 9, 7), "eski HATALI davranış (HMK m.104 uzatması) geri geldi"
    metin = "\n".join(rapor)
    assert "İİK m.18/1" in metin and "12. HD" in metin, metin
    assert "Adli tatil (HMK m.104)" not in metin


def test_Y01_CLI_varsayilan_yargi_kolunda_da_dogru():
    """Kullanıcı --yargi vermese bile (varsayılan hukuk) kural kendi rejimini taşır."""
    rc, out = _cli("--teblig", "2026-08-10", "--kural", "iik_istinaf")
    assert rc == 0, out
    assert _son(out) == "2026-08-24"
    assert "UYGULANMAZ" in out


@pytest.mark.parametrize("teblig,beklenen,dilekce", [
    # Y. 12. HD E.2024/7040 K.2024/10869 (30.12.2024): tebliğ 16.07.2024,
    # temyiz 30.08.2024 → süre aşımı.
    (date(2024, 7, 16), date(2024, 7, 30), date(2024, 8, 30)),
    # Y. 12. HD E.2022/11578 K.2022/11538 (07.11.2022): tebliğ 02.08.2022,
    # temyiz 07.09.2022 → süre aşımı (icra dairelerinde ve mahkemelerinde
    # HMK m.102/104 uygulanmaz).
    (date(2022, 8, 2), date(2022, 8, 16), date(2022, 9, 7)),
    # Y. 12. HD E.2023/7838 K.2023/7423 (13.11.2023): tebliğ 23.07.2023 (TATİL
    # İÇİNDE) — icrada süre tatilde de işler; son gün Pazar → Pazartesi.
    (date(2023, 7, 23), date(2023, 8, 7), date(2023, 8, 21)),
    # Y. 12. HD E.2025/8109 K.2025/7958 (04.12.2025): tebliğ 04.08.2025,
    # temyiz 03.09.2025 → süre aşımı.
    (date(2025, 8, 4), date(2025, 8, 18), date(2025, 9, 3)),
])
def test_Y01_yargitay_12HD_vakalariyla_birebir(teblig, beklenen, dilekce):
    son, _r, _u = _hesap(teblig, "iik_temyiz")
    assert son == beklenen
    assert dilekce > son, "Yargıtay süre aşımı dedi; motor süresinde göstermemeli"


def test_Y01_odeme_emrine_itiraz_23HD_vakasi():
    """Y. 23. HD E.2013/8404 K.2013/7933 (11.12.2013): ödeme emri 26.08.2011'de
    tebliğ, yedi günlük itiraz süresi 02.09.2011'de doldu (idari tatil süreyi
    uzatmaz; HMK m.104 HMK dışındaki sürelere uygulanmaz) → 05.09.2011 itirazı
    süresinden sonra."""
    son, _r, _u = _hesap(date(2011, 8, 26), "iik_odeme_emrine_itiraz")
    assert son == date(2011, 9, 2)
    assert date(2011, 9, 5) > son


def test_Y01_kambiyo_itirazi_IIK_m19_kaymasi_12HD_vakasi():
    """Y. 12. HD E.2009/1886 K.2009/10134: 09.06.2008 tebliğ, beş günlük süre
    Cumartesiye rastladı → İİK m.19/3 uyarınca tatili izleyen gün; 16.06.2008
    itirazı SÜRESİNDE. Kayma dayanağı HMK m.93 değil İİK m.19 olmalı."""
    son, rapor, _u = _hesap(date(2008, 6, 9), "iik_kambiyo_itiraz")
    assert son == date(2008, 6, 16)
    assert "İİK m.19" in "\n".join(rapor)


def test_Y01_yargi_icra_serbest_sure_de_uzamaz():
    """Tabloda olmayan bir İİK süresi --sure ile hesaplanırken --yargi icra
    seçilirse adli tatil rejimi 'uygulanmaz' olur (bayraksız güvenli taraf)."""
    rc, out = _cli("--teblig", "2026-08-10", "--sure", "2", "--birim", "hafta",
                   "--yargi", "icra")
    assert rc == 0, out
    assert _son(out) == "2026-08-24"


def test_Y01_hukuk_serbest_suresi_DEGISMEDI_regresyon():
    rc, out = _cli("--teblig", "2026-08-10", "--sure", "2", "--birim", "hafta")
    assert rc == 0 and _son(out) == "2026-09-07", out


def test_Y01_icra_kurali_ceza_koluyla_DURUR():
    rc, out = _cli("--teblig", "2026-08-10", "--kural", "iik_istinaf", "--yargi", "ceza")
    assert rc != 0 and not _SON_GUN_RE.search(out), out


# ══════════════════════════════════════════════════════════════════════════
# Y-02 — CMK m.331/4: TATİL İÇİNDE TEBLİĞDE SÜRE TATİLDE İŞLEMEZ
# ══════════════════════════════════════════════════════════════════════════

def test_Y02_tatil_icinde_teblig_tam_sure_1_Eylulden_isler():
    """Denetim örneği: 25.08.2026 tebliğ → motor 08.09 veriyordu (süreyi tatilde
    işletiyordu). YCGK E.2021/319 K.2022/846 ve E.2013/2-272 K.2013/524:
    tatilde süre işlemez, süre tatilin bitiminden itibaren başlar → 14.09."""
    bilgi = {}
    son, rapor, uyarilar = _hesap(date(2026, 8, 25), "cmk_istinaf", "ceza", _bilgi=bilgi)
    assert son == date(2026, 9, 14)
    metin = "\n".join(rapor + uyarilar)
    assert "2022/846" in metin and "2013/2-272" in metin
    # İHTİYAT = eski daire okuması (süre tatilde de işler; bitiş tatil dışında → ham
    # bitiş 08.09). 31 Ağu + 3 (03.09) bu tebliğde HİÇBİR okumanın sonucu değildir.
    assert "2026-09-08" in "\n".join(uyarilar)
    assert bilgi["ihtiyat_son"] == date(2026, 9, 8) and bilgi["plan_son"] == date(2026, 9, 8)
    assert "331" in metin and "tutuklu" in metin.lower()


def test_Y02_tatilin_ilk_gunu_teblig_ihtiyat_uc_gun():
    """Tebliğ 20.07 → eski okumada ham bitiş (03.08) tatil içinde → 31 Ağu + üç gün
    (Y. 11. CD E.2017/14079 K.2018/2400 deseni: 07.08.2014 tebliğ, 01.09'dan üç gün)."""
    bilgi = {}
    son, _r, uyarilar = _hesap(date(2026, 7, 20), "cmk_istinaf", "ceza", _bilgi=bilgi)
    assert son == date(2026, 9, 14)
    assert bilgi["ihtiyat_son"] == date(2026, 9, 3)
    assert "2026-09-03" in "\n".join(uyarilar)


def test_Y02_tatilden_once_teblig_uc_gun_kurali_DEGISMEDI():
    """Tatilden önce başlayıp tatilde biten süre: tatil bitiminden itibaren üç gün."""
    bilgi = {}
    son2, _r, uyarilar2 = _hesap(date(2026, 7, 14), "cmk_istinaf", "ceza", _bilgi=bilgi)
    assert son2 == date(2026, 9, 3)
    assert bilgi["alt_son"] is None
    assert not any("SINIR HÂLİ" in u for u in uyarilar2)


def test_Y02_19_Temmuz_sinir_hali_erken_manset_ve_kesin_dil_kapisi():
    """Tebliğ 19.07 → süre tatilin İLK günü başlar, tatil öncesinde hiç işlemez.
    Doğrudan karar yok (TEYİT BEKLİYOR): manşet ERKEN tarih (03.09), YCGK okuması
    (14.09) karşı taraf kapısına girer — 10.09 başvurusuna kesin dil KURULMAZ."""
    bilgi = {}
    son, _r, uyarilar = _hesap(date(2026, 7, 19), "cmk_istinaf", "ceza", _bilgi=bilgi)
    assert son == date(2026, 9, 3)
    assert bilgi["alt_son"] == date(2026, 9, 14)
    assert any("SINIR HÂLİ" in u and "TEYİT BEKLİYOR" in u for u in uyarilar)
    rc, out = _cli("--teblig", "2026-07-19", "--kural", "cmk_istinaf", "--yargi", "ceza",
                   "--islem", "2026-09-10")
    assert rc == 0 and "ARA TESPİT" in out and "SÜRE KAÇIRILMIŞTIR" not in out, out


def test_Y02_YCGK_2013_524_vakasi_birebir():
    """YCGK E.2013/2-272 K.2013/524: gerekçeli karar 04.08.2012'de (tatil içinde)
    tebliğ; yedi günlük süre 1 Eylül'de başlayıp 7 Eylül Cuma mesai bitiminde
    sona erdi → 10.09.2012 başvurusu süreden sonra."""
    son, _r, _u = H.hesapla(date(2012, 8, 4), 7, "gun", "ceza", "usul")
    assert son == date(2012, 9, 7)
    assert date(2012, 9, 10) > son


@pytest.mark.parametrize("teblig,miktar,birim,dilekce,beklenen", [
    # YCGK E.2021/319 K.2022/846: tutuklu işte 21.07.2020 tebliğ, 15 günlük süre,
    # 02.09.2020 temyizi SÜRESİNDE (tutuklu işte de tatilde süre işlemez).
    (date(2020, 7, 21), 15, "gun", date(2020, 9, 2), date(2020, 9, 15)),
    # AYM Ramazan Seçen (2021/37483): 21.07.2020 tebliğ, 31.08.2020 temyizi süre
    # aşımı sayılmış → mahkemeye erişim hakkı İHLAL.
    (date(2020, 7, 21), 15, "gun", date(2020, 8, 31), date(2020, 9, 15)),
    # Y. 8. CD E.2024/24467 K.2025/6983: 24.07.2024 tebliğ, 04.09.2024 temyizi
    # süresinde; iki hafta 14.09.2024 Cumartesi → 16.09.2024.
    (date(2024, 7, 24), 2, "hafta", date(2024, 9, 4), date(2024, 9, 16)),
])
def test_Y02_tutuklu_dahil_kararlarla_birebir(teblig, miktar, birim, dilekce, beklenen):
    son, _r, _u = H.hesapla(teblig, miktar, birim, "ceza", "usul")
    assert son == beklenen
    assert dilekce <= son, "yüksek mahkeme süresinde dedi; motor kaçırılmış göstermemeli"


def test_Y02_CLI():
    rc, out = _cli("--teblig", "2026-08-25", "--kural", "cmk_istinaf", "--yargi", "ceza")
    assert rc == 0 and _son(out) == "2026-09-14", out


def test_Y02_json_plan_son_gun_ihtiyat_tarihidir():
    """Manşet hukuki son günü (YCGK) korur; makine-okur çıktı kendi işlemimiz için
    ERKEN plan tarihini ayrıca taşır (regex/JSON tüketicisi yalnız geç tarihi görmesin)."""
    rc, out = _cli("--teblig", "2026-08-25", "--kural", "cmk_istinaf", "--yargi", "ceza", "--json")
    assert rc == 0, out
    satir = [s for s in out.splitlines() if s.startswith("[JSON] ")][-1]
    js = json.loads(satir[len("[JSON] "):])
    assert js["son_gun"] == "2026-09-14" and js["ihtiyat_son_gun"] == "2026-09-08"
    assert js["plan_son_gun"] == "2026-09-08" and js["adli_tatil_rejimi"] == "cmk331"


def test_Y02_ihtiyat_plani_deftere_ayri_kayit_nobetci_celiski_saymaz(tmp_path):
    (tmp_path / "_oa").mkdir()
    cp = subprocess.run([sys.executable, str(SCRIPT), "--teblig", "2026-08-25", "--kural",
                         "cmk_istinaf", "--yargi", "ceza", "--kok", str(tmp_path)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        timeout=120)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    d = json.loads((tmp_path / "_oa" / "sureler.json").read_text(encoding="utf-8"))
    assert sorted(f["son_gun"] for f in d["flagler"]) == ["2026-09-08", "2026-09-14"]
    assert any("ihtiyat planı" in f["aciklama"] for f in d["flagler"])
    nb = subprocess.run([sys.executable, str(NOBETCI), "--kok", str(tmp_path)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        timeout=120)
    assert "ÇELİŞKİ ADAYI" not in nb.stdout, nb.stdout


# ══════════════════════════════════════════════════════════════════════════
# Y-03 — HMK m.345 / m.361 ve İİK m.363 / m.364 YALNIZ TEBLİĞDEN işler
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("kural", ["hmk_istinaf", "hmk_temyiz", "iik_istinaf", "iik_temyiz"])
def test_Y03_izinli_baslangic_yalniz_teblig(kural):
    assert H.KURAL_BASLANGIC[kural] == ["teblig"]
    assert H._GOMULU_BASLANGIC[kural] == ["teblig"]


def test_Y03_tefhim_secilirse_celiski_gorunur():
    rc, out = _cli("--teblig", "2026-03-02", "--kural", "hmk_istinaf",
                   "--baslangic-turu", "tefhim")
    assert rc == 0, out
    assert "BAŞLANGIÇ TÜRÜ ÇELİŞKİSİ" in out.split("UYARILAR", 1)[-1]


# ══════════════════════════════════════════════════════════════════════════
# Y-04 — HMK m.139/1-ç iki haftalık kesin süre TARİH ÜRETİR
# ══════════════════════════════════════════════════════════════════════════

def test_Y04_on_inceleme_belge_suresi_tarih_kurali():
    son, _r, _u = _hesap(date(2026, 3, 2), "hmk_on_inceleme_belge_sunma")
    assert son == date(2026, 3, 16)
    kaynak = H.KURALLAR["hmk_on_inceleme_belge_sunma"][2]
    assert "m.139/1-ç" in kaynak and "m.140/5" in kaynak and "KESİN" in kaynak


def test_Y04_asama_catali_tarih_kuralina_baglanir():
    """Aşama kuralı korunur (davetiye tebliğ edilene kadar tarih yok); açıklaması
    artık tarih kuralının adını verir."""
    assert "hmk_on_inceleme_belge" in H.ASAMA_KURALLAR
    assert "hmk_on_inceleme_belge_sunma" in H.ASAMA_KURALLAR["hmk_on_inceleme_belge"]["aciklama"]
    rc, out = _cli("--teblig", "2026-07-27", "--kural", "hmk_on_inceleme_belge_sunma")
    assert rc == 0 and _son(out) == "2026-09-07", out   # HMK süresi → m.104


# ══════════════════════════════════════════════════════════════════════════
# Y-05 — EKSİK SÜRE KURALLARI (her biri resmî metinden)
# ══════════════════════════════════════════════════════════════════════════

YENI_KURALLAR = {
    # ad: (miktar, birim, madde çıpası, rejim)
    "iik_temyiz": (2, "hafta", "m.364", "uygulanmaz"),
    "iik_odeme_emrine_itiraz": (7, "gun", "m.62", "uygulanmaz"),
    "iik_gecikmis_itiraz": (3, "gun", "m.65", "uygulanmaz"),
    "iik_itirazin_iptali": (1, "yil", "m.67", "uygulanmaz"),
    "iik_itirazin_kaldirilmasi": (6, "ay", "m.68", "uygulanmaz"),
    "iik_borctan_kurtulma": (7, "gun", "m.69", "uygulanmaz"),
    "iik_89_ihbarname_itiraz": (7, "gun", "m.89", "uygulanmaz"),
    "iik_89_menfi_tespit": (15, "gun", "m.89", "uygulanmaz"),
    "iik_ihalenin_feshi": (7, "gun", "m.134", "uygulanmaz"),
    "iik_ihalenin_feshi_azami": (1, "yil", "m.134", "uygulanmaz"),
    "iik_kambiyo_itiraz": (5, "gun", "m.168", "uygulanmaz"),
    "iik_ihtiyati_haciz_itiraz": (7, "gun", "m.265", "uygulanmaz"),
    "iik_icra_ceza_sikayet": (3, "ay", "m.347", "uygulanmaz"),
    "iik_icra_ceza_sikayet_azami": (1, "yil", "m.347", "uygulanmaz"),
    "hmk_dosya_gonderme": (2, "hafta", "m.20", "hmk104"),
    "hmk_cevap_basit": (2, "hafta", "m.317/2", "hmk104"),
    "hmk_on_inceleme_belge_sunma": (2, "hafta", "m.139", "hmk104"),
    "hmk_tedbir_itiraz": (1, "hafta", "m.394", "uygulanmaz"),
    "hmk_tedbir_esas_dava": (2, "hafta", "m.397", "uygulanmaz"),
    "aym_bireysel_mazeret": (15, "gun", "m.47/5", "uygulanmaz"),
    "aihm_basvuru": (4, "ay", "m.35/1", "uygulanmaz"),
}


@pytest.mark.parametrize("ad,beklenen", sorted(YENI_KURALLAR.items()))
def test_Y05_yeni_kural_tabloda_ve_teyitli(ad, beklenen):
    miktar, birim, capa, rejim = beklenen
    assert ad in H.KURALLAR, ad
    assert H.KURALLAR[ad][:2] == (miktar, birim)
    assert capa in H.KURALLAR[ad][2], H.KURALLAR[ad][2]
    assert H.KURAL_TEYIT[ad], "teyitsiz kural eklenemez: " + ad
    assert H.KURAL_REJIM[ad]["adli_tatil"] == rejim
    son, _r, _u = _hesap(date(2026, 3, 2), ad)
    assert son > date(2026, 3, 2)


def test_Y05_itirazin_kaldirilmasi_alti_ay_ve_sabit_tatil_kaymasi():
    """İİK m.68/1: altı ay. 15.01.2026 + 6 ay = 15.07.2026 (Demokrasi ve Millî
    Birlik Günü) → İİK m.19/3 uyarınca ertesi gün."""
    son, rapor, _u = _hesap(date(2026, 1, 15), "iik_itirazin_kaldirilmasi")
    assert son == date(2026, 7, 16)
    assert "İİK m.19" in "\n".join(rapor)


def test_Y05_tedbire_itiraz_HMK103_1a_ile_uzamaz():
    son, rapor, _u = _hesap(date(2026, 8, 10), "hmk_tedbir_itiraz")
    assert son == date(2026, 8, 17)
    assert "m.103/1-a" in "\n".join(rapor)


@pytest.mark.parametrize("kural,teblig,son_beklenen", [
    ("hmk_tedbir_esas_dava", date(2026, 8, 10), date(2026, 8, 24)),
    ("iik_itirazin_iptali", date(2025, 8, 20), date(2026, 8, 20)),
])
def test_Y05_teyitsiz_rejim_TEMKINLI_ve_gorunur(kural, teblig, son_beklenen):
    """Rejimi resmî kaynakla teyit edilemeyen kuralda motor ERKEN tarihi seçer ve
    bunu açıkça söyler (sessiz seçim yok)."""
    son, _r, uyarilar = _hesap(teblig, kural)
    assert son == son_beklenen
    assert any("TEMKİNLİ" in u for u in uyarilar), uyarilar


def test_Y05_teyitsiz_rejimde_karsi_tarafa_KESIN_DIL_kurulmaz():
    """Karşı taraf 31.08'de dava açtıysa: m.104 uygulanırsa son gün 07.09 olurdu.
    Rejim teyitsizken 'süre kaçırılmıştır' denemez — ARA TESPİT."""
    rc, out = _cli("--teblig", "2026-08-10", "--kural", "hmk_tedbir_esas_dava",
                   "--islem", "2026-08-31")
    assert rc == 0, out
    assert "SÜRE KAÇIRILMIŞTIR" not in out
    assert "ARA TESPİT" in out and "KESİN DİL KULLANMA" in out


def test_Y05_teyitli_icra_suresinde_kesin_dil_korunur():
    rc, out = _cli("--teblig", "2026-08-10", "--kural", "iik_istinaf",
                   "--islem", "2026-08-31")
    assert rc == 0 and "SÜRE KAÇIRILMIŞTIR" in out, out


def test_Y05_cevap_basit_ek_sure_siniri_metinde():
    k = H.KURALLAR["hmk_cevap_basit"][2]
    assert "m.317/2" in k and "İKİ HAFTA" in k and "7036 m.7/1" in k
    assert "hmk_cevap_basit" in H.KURALLAR["hmk_cevap"][2]


def test_Y05_icra_ceza_sikayeti_ogrenme_tatilde_CMK_okumasi_kesin_dili_keser():
    """İİK m.347 — öğrenme tatil içinde; rejim TEYİT BEKLİYOR. Diğer okuma (CMK m.331/4:
    süre tatilde işlemez) son günü 30.11'e taşır → 10.11 şikâyetine kesin dil kurulmaz.
    25.10.2026 Pazar → İİK m.19/3 ile 26.10.2026 Pazartesi."""
    bilgi = {}
    son, _r, uyarilar = _hesap(date(2026, 7, 25), "iik_icra_ceza_sikayet", _bilgi=bilgi)
    assert son == date(2026, 10, 26)
    assert bilgi["alt_son"] == date(2026, 11, 30)
    assert any("TEMKİNLİ" in u for u in uyarilar)
    rc, out = _cli("--teblig", "2026-07-25", "--kural", "iik_icra_ceza_sikayet", "--yargi", "ceza",
                   "--islem", "2026-11-10")
    assert rc == 0 and "ARA TESPİT" in out and "SÜRE KAÇIRILMIŞTIR" not in out, out


def test_tabloda_olmayan_kural_sessizce_kol_rejimine_dusmez():
    """Doğrudan API çağrısında tabloda olmayan kural: kol rejimine (hukuk → m.104)
    SESSİZCE düşülmez; ön ekten türetilir, teyitsiz ve görünür (fail-closed)."""
    bilgi = {}
    son, _r, uyarilar = H.hesapla(date(2026, 8, 10), 2, "hafta", "hukuk", "usul",
                                  kural="iik_tabloda_olmayan", _bilgi=bilgi)
    assert son == date(2026, 8, 24) and bilgi["rejim_turetildi"] == "ön ekten"
    assert any("REJİM TÜRETİLDİ" in u for u in uyarilar)


# ══════════════════════════════════════════════════════════════════════════
# AYM (6216 m.47/5) ve AİHM (AİHS m.35/1)
# ══════════════════════════════════════════════════════════════════════════

def test_AYM_otuz_gun_hafta_sonu_kaymasi_Ramazan_Secen_vakasi():
    """AYM Ramazan Seçen (2021/37483) § 2, 9: nihai karar 03.06.2021'de UYAP'tan
    öğrenildi, başvuru 05.07.2021 (otuzuncu gün Cumartesi → Pazartesi)."""
    son, _r, uyarilar = _hesap(date(2021, 6, 3), "aym_bireysel",
                               baslangic_turu="ogrenme")
    assert son == date(2021, 7, 5)
    assert any("Ramazan Seçen" in u for u in uyarilar)


def test_AYM_adli_tatil_UZATMASI_artik_uygulanmaz_temkinli():
    """6216 ve AYM İçtüzüğünde adli tatil hükmü yok; eski motor 20.07 + 30 gün
    için HMK m.104 ile 07.09 veriyordu (geç tarih). Temkinli: uzatma YOK."""
    son, _r, uyarilar = _hesap(date(2026, 7, 20), "aym_bireysel")
    assert son == date(2026, 8, 19)
    assert any("TEMKİNLİ" in u for u in uyarilar)
    assert any("TEYİT BEKLİYOR" in u for u in uyarilar)


def test_AYM_mazeret_on_bes_gun():
    son, _r, _u = _hesap(date(2026, 3, 2), "aym_bireysel_mazeret")
    assert son == date(2026, 3, 17)


def test_AIHM_dort_ay():
    son, _r, _u = _hesap(date(2026, 3, 2), "aihm_basvuru")
    assert son == date(2026, 7, 2)


def test_AIHM_son_gun_hafta_sonuna_rastlasa_da_KAYMAZ_Sabri_Gunes():
    """Sabri Güneş/Türkiye [BD] §§ 60-61: tebliğ 28.11.2005; süre 28.05.2006 Pazar
    gece yarısı doldu; 29.05.2006 başvurusu süre dışı (iç hukuktaki kayma
    kuralı AİHM süresine uygulanmaz)."""
    son, rapor, uyarilar = H.hesapla(date(2005, 11, 28), 6, "ay", "hukuk", "usul",
                                     kural="aihm_basvuru")
    assert son == date(2006, 5, 28)
    assert "Sabri Güneş" in "\n".join(rapor + uyarilar)
    son4, _r, _u = _hesap(date(2026, 6, 3), "aihm_basvuru")
    assert son4 == date(2026, 10, 3) and son4.weekday() == 5   # Cumartesi, kaymaz


def test_AIHM_gecis_kurali_uyarisi():
    _s, _r, uyarilar = _hesap(date(2021, 12, 1), "aihm_basvuru")
    assert any("15 No'lu Protokol" in u and "TEYİT BEKLİYOR" in u for u in uyarilar)


def test_AIHM_ceza_koluyla_da_hesaplanir_kural_kendi_rejimini_tasir():
    rc, out = _cli("--teblig", "2026-03-02", "--kural", "aihm_basvuru", "--yargi", "ceza")
    assert rc == 0 and _son(out) == "2026-07-02", out


# ══════════════════════════════════════════════════════════════════════════
# İş hukuku kuralları: 4857 süresi — HMK m.104 uzatması yok (9. HD)
# ══════════════════════════════════════════════════════════════════════════

def test_is_iade_davasi_suresi_tatilde_uzamaz_9HD():
    """Y. 9. HD E.2016/1261 K.2016/22196: işe iade süresinde m.104 uzatmasının
    uygulanması usul ve yasaya aykırı (HMK m.103/1-ç). Eski motor 07.09 veriyordu."""
    son, _r, uyarilar = _hesap(date(2026, 8, 10), "is_ise_iade_dava")
    assert son == date(2026, 8, 24)
    assert "m.103/1-ç" in " ".join(uyarilar)


# ══════════════════════════════════════════════════════════════════════════
# Kural düzeyinde rejim tablosu — ikiz kilit (B-21 deseni)
# ══════════════════════════════════════════════════════════════════════════

_REJIMLER = {"hmk104", "iyuk8", "cmk331", "uygulanmaz"}


def test_rejim_json_ve_gomulu_BIREBIR():
    j = json.loads(KURAL_JSON.read_text(encoding="utf-8"))["kurallar"]
    g = H._GOMULU_REJIM
    assert set(g) == set(j) == set(H._GOMULU_KURALLAR)
    ayrisan = []
    for k in sorted(g):
        for alan in ("adli_tatil", "adli_tatil_dayanak", "adli_tatil_teyitli", "son_gun_kaymasi"):
            if g[k][alan] != j[k].get(alan):
                ayrisan.append("%s.%s" % (k, alan))
    assert not ayrisan, "İKİZ REJİM TABLOSU AYRIŞMASI: " + ", ".join(ayrisan)


def test_rejim_degerleri_gecerli_ve_aileler_tutarli():
    for k, r in H.KURAL_REJIM.items():
        assert r["adli_tatil"] in _REJIMLER, k
        assert r["adli_tatil_dayanak"].strip(), k
        if k.startswith("iik_"):
            assert r["adli_tatil"] == "uygulanmaz", k
        if k.startswith("cmk_"):
            assert r["adli_tatil"] == "cmk331", k
        if k.startswith("iyuk_"):
            assert r["adli_tatil"] == "iyuk8", k
        if not r["adli_tatil_teyitli"]:
            assert "TEYİT" in r["adli_tatil_dayanak"] or "TARTIŞMALI" in r["adli_tatil_dayanak"], k
    yalniz_aihm = [k for k, r in H.KURAL_REJIM.items() if not r["son_gun_kaymasi"]]
    assert yalniz_aihm == ["aihm_basvuru"]


def test_json_bozuksa_gomulu_rejim_ile_icra_yine_uzamaz(tmp_path):
    (tmp_path / "sure_kurallari.json").write_text("{ bozuk", encoding="utf-8")
    kopya = tmp_path / "hesapla_sure.py"
    kopya.write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    cp = subprocess.run([sys.executable, str(kopya), "--teblig", "2026-08-10",
                         "--kural", "iik_istinaf", "--flagsiz"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        timeout=120)
    out = cp.stdout + cp.stderr
    assert cp.returncode == 0 and "gömülü" in out.lower(), out
    assert _son(out) == "2026-08-24"


def test_json_rejim_alani_yoksa_onekten_turetilir_ve_soylenir(tmp_path):
    veri = json.loads(KURAL_JSON.read_text(encoding="utf-8"))
    for v in veri["kurallar"].values():
        for alan in ("adli_tatil", "adli_tatil_dayanak", "adli_tatil_teyitli", "son_gun_kaymasi"):
            v.pop(alan, None)
    (tmp_path / "sure_kurallari.json").write_text(json.dumps(veri, ensure_ascii=False),
                                                 encoding="utf-8")
    kopya = tmp_path / "hesapla_sure.py"
    kopya.write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    cp = subprocess.run([sys.executable, str(kopya), "--teblig", "2026-08-10",
                         "--kural", "iik_istinaf", "--flagsiz"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        timeout=120)
    out = cp.stdout + cp.stderr
    assert cp.returncode == 0, out
    assert _son(out) == "2026-08-24", "ön ekten türetme icrayı 'uygulanmaz'a bağlamalı"
    assert "TÜRETİLDİ" in out


def test_hesapla_imzasi_geriye_uyumlu():
    import inspect
    adlar = list(inspect.signature(H.hesapla).parameters)
    assert adlar[:8] == ["teblig", "miktar", "birim", "yargi", "tur",
                         "adli_tatil_istisna", "baslangic_turu", "kural"]


# ══════════════════════════════════════════════════════════════════════════
# Y-08 — TATİL TAKVİMİ EKSİK: sessiz yanlış hesap yok
# Testler tatiller.json'un BUGÜNKÜ içeriğine kilitlenmez (bir yılın resmî tarihleri
# sonradan doğru şekilde işlendiğinde kırılmasınlar): eksik yıl in-process'te DINI
# tablosu monkeypatch'lenerek, CLI'da geçici kopya (tmp_path) ile kurulur.
# ══════════════════════════════════════════════════════════════════════════

_EKSIK_YIL = 2027


def _dini_yilsiz(monkeypatch, yil=_EKSIK_YIL, kismi=None):
    d = {k: set(v) for k, v in H.DINI.items() if k != str(yil)}
    if kismi:
        d[str(yil)] = set(kismi)
    monkeypatch.setattr(H, "DINI", d)


def _eksik_takvimli_kopya(tmp_path, yil=_EKSIK_YIL):
    """Script + kural tablosu + nöbetçinin geçici kopyası; tatiller.json'da `yil` BOŞ."""
    hedef = tmp_path / "scripts"
    hedef.mkdir()
    for ad in ("hesapla_sure.py", "sure_kurallari.json", "sure_nobetci.py"):
        (hedef / ad).write_text((SKILL / "scripts" / ad).read_text(encoding="utf-8"),
                                encoding="utf-8")
    t = json.loads(TATIL_JSON.read_text(encoding="utf-8"))
    t["dini"][str(yil)] = []
    (hedef / "tatiller.json").write_text(json.dumps(t, ensure_ascii=False), encoding="utf-8")
    return hedef / "hesapla_sure.py", hedef / "sure_nobetci.py"


def test_Y08_bos_birakilan_yil_gerekcesiz_kalmaz_ve_kayitlar_salt_ISO():
    """'dini' altında BOŞ bırakılan yılın nedeni `_<yıl>_durum` notunda yazılı olmalı
    (2027: resmî kaynakla teyit edilemedi — 2026-10-05); dolu yılda yalnız salt ISO tarih."""
    t = json.loads(TATIL_JSON.read_text(encoding="utf-8"))
    for yil, gunler in t["dini"].items():
        if not gunler:
            assert t.get("_%s_durum" % yil, "").strip(), "boş yıl gerekçesiz: " + yil
        for g in gunler:
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", g) and g.startswith(yil), g


def test_Y08_eksik_yil_hesabinda_TATIL_TAKVIMI_EKSIK_uyarisi(monkeypatch):
    _dini_yilsiz(monkeypatch)
    _son, rapor, uyarilar = _hesap(date(2027, 3, 1), "hmk_istinaf")
    assert any("TATİL TAKVİMİ EKSİK" in u and "2027" in u for u in uyarilar)
    assert any("TATİL TAKVİMİ EKSİK" in s for s in rapor)


def test_Y08_kismi_girilmis_yil_TAM_sayilmaz(monkeypatch):
    """Tek bir bayram günü girilmiş yıl takvim kapısını sessizce kapatamaz (fail-closed)."""
    _dini_yilsiz(monkeypatch, kismi={"2027-03-09"})
    assert H.dini_tanimli_mi(2027) and not H.dini_tam_mi(2027)
    _s, rapor, _u = _hesap(date(2027, 3, 1), "hmk_istinaf")
    assert any("TATİL TAKVİMİ EKSİK" in s and "KISMİ" in s for s in rapor)


def test_Y08_takvimi_tam_yilda_uyari_YOK():
    assert H.dini_tam_mi(2026)
    _s, rapor, uyarilar = _hesap(date(2026, 5, 20), "hmk_istinaf")
    assert not any("TATİL TAKVİMİ EKSİK" in s for s in rapor + uyarilar)


def test_Y08_is_gunu_sayiminda_eksik_takvim_ozellikle_uyarilir(monkeypatch):
    _dini_yilsiz(monkeypatch)
    _s, _r, uyarilar = H.hesapla(date(2027, 3, 1), 10, "isgunu", "hukuk", "usul",
                                 kural="is_ise_baslatma_basvuru")
    assert any("İŞ GÜNÜ" in u and "TAKVİM" in u for u in uyarilar), uyarilar


def test_Y08_eksik_takvimde_karsi_tarafa_kesin_dil_kurulmaz(tmp_path):
    betik, _n = _eksik_takvimli_kopya(tmp_path)
    cp = subprocess.run([sys.executable, str(betik), "--teblig", "2027-03-01", "--kural",
                         "hmk_istinaf", "--islem", "2027-03-17", "--flagsiz"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        cwd=str(tmp_path), timeout=120)
    out = cp.stdout + cp.stderr
    assert cp.returncode == 0, out
    assert "SÜRE KAÇIRILMIŞTIR" not in out and "ARA TESPİT" in out


def test_Y08_deftere_takvim_eksik_isareti_ve_nobetci_gosterir(tmp_path):
    betik, nobetci = _eksik_takvimli_kopya(tmp_path)
    kok = tmp_path / "dava"
    (kok / "_oa").mkdir(parents=True)
    cp = subprocess.run([sys.executable, str(betik), "--teblig", "2027-03-01",
                         "--kural", "hmk_istinaf", "--kok", str(kok)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        cwd=str(tmp_path), timeout=120)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    d = json.loads((kok / "_oa" / "sureler.json").read_text(encoding="utf-8"))
    assert d["flagler"][0]["takvim_eksik"] == [2027]
    nb = subprocess.run([sys.executable, str(nobetci), "--kok", str(kok)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        cwd=str(tmp_path), timeout=120)
    # Çıkış kodu bilinçli olarak denetlenmez: nöbetçi kaydı BUGÜNE göre sınıflar
    # (ileri/yaklaşan/geçmiş); işaret ise sınıftan bağımsız basılır → deterministik.
    assert "takvim eksik" in (nb.stdout + nb.stderr).lower()


# ══════════════════════════════════════════════════════════════════════════
# BAŞLANGIÇ KAPISI (Yargı PRO 12-2 / 12-3 fikrinin OA uyarlaması)
# ══════════════════════════════════════════════════════════════════════════

def test_kapi_supheli_teblig_tek_kesin_tarih_URETMEZ(tmp_path):
    (tmp_path / "_oa").mkdir()
    cp = subprocess.run([sys.executable, str(SCRIPT), "--teblig", "2026-03-02",
                         "--kural", "hmk_istinaf", "--teblig-durumu", "supheli",
                         "--kok", str(tmp_path)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        timeout=120)
    out = cp.stdout + cp.stderr
    assert cp.returncode == 0, out
    assert "İHTİYAT HEDEFİ" in out and "HESAPLANAN SON GÜN" not in out
    d = json.loads((tmp_path / "_oa" / "sureler.json").read_text(encoding="utf-8"))
    assert d["flagler"][0]["aciklama"].startswith("[İHTİYAT")


def test_kapi_usulsuz_teblig_TK32_ogrenme_ister():
    _s, _r, uyarilar = _hesap(date(2026, 3, 2), "hmk_istinaf", teblig_durumu="usulsuz")
    assert any("TK m.32" in u for u in uyarilar)
    _s, _r, uyarilar2 = _hesap(date(2026, 3, 2), "hmk_istinaf", teblig_durumu="usulsuz",
                               baslangic_turu="ogrenme")
    assert not any("--baslangic-turu ogrenme" in u for u in uyarilar2)


def test_kapi_kanitsiz_baslangic_gorunur_ve_kesin_dili_keser():
    _s, _r, uyarilar = _hesap(date(2026, 3, 2), "hmk_istinaf", baslangic_kaniti="beyan")
    assert any("KANITSIZ BAŞLANGIÇ" in u for u in uyarilar)
    rc, out = _cli("--teblig", "2026-03-02", "--kural", "hmk_istinaf",
                   "--baslangic-kaniti", "yok", "--islem", "2026-03-30")
    assert rc == 0, out
    assert "SÜRE KAÇIRILMIŞTIR" not in out and "ARA TESPİT" in out


def test_kapi_tefhim_tutanagi_teblige_bagli_kuralla_celisir():
    _s, _r, uyarilar = _hesap(date(2026, 3, 2), "hmk_istinaf",
                              baslangic_kaniti="tefhim-tutanagi")
    assert any("KANIT" in u and "ÇELİŞKİ" in u for u in uyarilar), uyarilar
    _s, _r, temiz = _hesap(date(2026, 3, 2), "hmk_istinaf", baslangic_kaniti="mazbata")
    assert not any("ÇELİŞKİ" in u for u in temiz)


def test_kapi_uets_kaydi_iki_senaryoyu_kendiliginden_acar():
    """7201 m.7/a: elektronik adrese ulaştığı tarihi izleyen beşinci günün sonunda
    tebliğ sayılır — UETS kanıtı verilince iki senaryo zorunlu."""
    rc, out = _cli("--teblig", "2026-05-20", "--kural", "hmk_istinaf",
                   "--baslangic-kaniti", "uets-kaydi")
    assert rc == 0, out
    assert "UETS Senaryo-1" in out and "UETS Senaryo-2" in out
    assert _son(out) == "2026-06-03"   # bizim süremizde plan ERKEN tarih


def test_kapi_aym_ve_aihm_ogrenme_notu():
    _s, _r, u1 = _hesap(date(2026, 3, 2), "aym_bireysel")
    _s, _r, u2 = _hesap(date(2026, 3, 2), "aihm_basvuru")
    assert any("UYAP" in u and "öğren" in u.lower() for u in u1)
    assert any("§ 53" in u for u in u2)


def test_kapi_kanit_secenekleri_cli_de():
    rc, out = _cli("--help")
    assert "--baslangic-kaniti" in out and "--teblig-durumu" in out


# ══════════════════════════════════════════════════════════════════════════
# Talimat katmanı
# ══════════════════════════════════════════════════════════════════════════

def test_skill_md_yeni_katmanlari_anlatir():
    md = SKILL_MD.read_text(encoding="utf-8")
    for anahtar in ("--baslangic-kaniti", "--teblig-durumu", "--yargi icra",
                    "baslangic-kapisi.md", "iik_odeme_emrine_itiraz", "aihm_basvuru",
                    "hmk_on_inceleme_belge_sunma", "TATİL TAKVİMİ EKSİK"):
        assert anahtar in md, anahtar


def test_cizelge_ve_kapi_belgesi_capalari():
    c = CIZELGE.read_text(encoding="utf-8")
    for capa in ("İİK m.18/1", "2025/7548", "2013/2-272", "Sabri Güneş", "m.89", "m.347"):
        assert capa in c, capa
    k = KAPI_MD.read_text(encoding="utf-8")
    for capa in ("m.7/a", "m.32", "m.11", "m.21", "m.31", "m.36", "TEYİT BEKLİYOR"):
        assert capa in k, capa


def test_degisiklik_gunlugu_v0518():
    g = GUNLUK.read_text(encoding="utf-8")
    assert "v0.5.18" in g
    for bid in ("Y-01", "Y-02", "Y-03", "Y-04", "Y-05", "Y-08"):
        assert bid in g, bid

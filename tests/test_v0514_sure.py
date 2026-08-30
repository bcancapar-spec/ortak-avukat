# -*- coding: utf-8 -*-
"""v0.5.14 — SÜRE MOTORU paketi (oa-sure) regresyon ve kilit testleri.

Kapsanan denetim bulguları:
  A-1  (P0) CMK sürelerine HMK m.104 adli tatili uygulanıyor; doğrusu CMK m.331/4 (üç gün)
  A-3        İYUK m.27 yürütmenin durdurulması — `iyuk_yd_itiraz` kuralı (7 gün, m.27/7)
  A-4        UETS "güvenli taraf" çelişkisi + bozuk cümle + vergide dayanak (VUK m.107/A)
  A-5        İYUK m.20/A (ivedi) ve m.20/B (merkezî sınav) kuralları + uyarı metni
  A-7        Adli tatil istisnası gerekçesi yargı koluna göre dallanmalı (idari → İYUK m.62)
  A-9        `_dikkat_cmk` notu yürürlükten kalkmış hukuku anlatıyor
  A-10       İdari/ceza yargıda HMK m.95 eski hâle getirme önerilmemeli
  A-17       İYUK m.48/3 (30 gün cevap) ve m.48/6 + m.45/2 (7 gün) kuralları
  A-20       6183 m.58 süresinin çalışmaya ara ile uzaması TARTIŞMALI — şerh düşmeli
  B-16       Negatif/sıfır süre sessizce kabul ediliyor; geçmişte "son gün" üretiyor
  B-20       `--baslangic-turu` seçilen kuralla çelişse de sessizce kabul ediliyor
  B-21       İkiz kural tablosu (JSON ↔ _GOMULU_KURALLAR) ayrışması — MEKANİK KİLİT
  B-22       Hatalı/uç tarihte ham traceback

Tüm hukuki iddialar Mevzuat MCP'den teyitlidir (2026-08-31):
CMK m.331/4, m.39, m.268, m.273, m.291, m.40 · İYUK m.8, m.20/A, m.20/B, m.27,
m.45, m.48, m.61, m.62 · HMK m.103 · 6183 m.58 · VUK m.107/A · 7201 m.7/a.
"""
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
from datetime import date

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-sure"
SCRIPT = SKILL / "scripts" / "hesapla_sure.py"
KURAL_JSON = SKILL / "scripts" / "sure_kurallari.json"
SKILL_MD = SKILL / "SKILL.md"
CIZELGE = SKILL / "references" / "sure-cizelgesi.md"
GUNLUK = SKILL / "references" / "degisiklik-gunlugu.md"

_SON_GUN_RE = re.compile(r"HESAPLANAN SON G[ÜU]N\s*:\s*(\d{4}-\d{2}-\d{2})")


def _load():
    spec = importlib.util.spec_from_file_location("hesapla_sure_v0514", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _load()


def _cli(*args):
    """CLI'ı koşar; (returncode, stdout, stderr) döndürür. --flagsiz: deftere yazmaz."""
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--flagsiz"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO),
    )
    return cp.returncode, cp.stdout, cp.stderr


# ══════════════════════════════════════════════════════════════════════════
# A-1 (P0) — CMK m.331/4: adli tatil sonrası ÜÇ GÜN
# ══════════════════════════════════════════════════════════════════════════

def test_A1_yargi_kolu_ceza_secenegi_var():
    """--yargi 'ceza' değerini kabul etmeli (denetimden önce: invalid choice)."""
    rc, out, err = _cli("--teblig", "2026-07-14", "--kural", "cmk_istinaf", "--yargi", "ceza")
    assert rc == 0, f"--yargi ceza reddedildi:\nSTDOUT:{out}\nSTDERR:{err}"
    assert "invalid choice" not in err


def test_A1_cmk_adli_tatil_uc_gun_uzar_2026_09_03():
    """CMK m.331/4: 'tatilin bittiği günden itibaren ÜÇ GÜN uzatılmış sayılır'.

    Golden vaka (denetim raporu A-1): tebliğ 2026-07-14, cmk_istinaf (2 hafta)
    → ham bitiş 2026-07-28 (20 Tem–31 Ağu penceresinde) → 31 Ağu + 3 gün =
    2026-09-03 (Perşembe). Denetimden önceki çıktı 2026-09-07 idi (HMK m.104
    hukuk rejimi) — dört gün GEÇ, telafisiz hak kaybı.
    """
    son, rapor, _uy = MOD.hesapla(date(2026, 7, 14), 2, "hafta", "ceza", "usul")
    assert son.isoformat() == "2026-09-03", (
        f"CMK m.331/4 üç günlük uzatma yanlış: {son.isoformat()} "
        "(beklenen 2026-09-03; eski hatalı davranış 2026-09-07)")
    metin = "\n".join(rapor)
    assert "331" in metin, f"Uzatma satırı m.331 çıpası taşımıyor:\n{metin}"
    assert "HMK m.104" not in metin, "Ceza kolunda HMK m.104 gerekçesi basılamaz"


def test_A1_cmk_adli_tatil_uc_gun_CLI():
    """Aynı vaka CLI üzerinden de 2026-09-03 vermeli."""
    rc, out, _err = _cli("--teblig", "2026-07-14", "--kural", "cmk_istinaf", "--yargi", "ceza")
    m = _SON_GUN_RE.search(out)
    assert rc == 0 and m and m.group(1) == "2026-09-03", out


def test_A1_cmk_kurali_ceza_kolu_disinda_HESABI_DURDURUR():
    """SESSİZ YANLIŞ VARSAYILAN YASAK: cmk_* kuralı hukuk/idari kolda seçilirse
    hesap DURUR (exit != 0), yanlış son gün ne ekrana ne deftere yazılır."""
    for kol in ("hukuk", "idari"):
        rc, out, err = _cli("--teblig", "2026-07-14", "--kural", "cmk_istinaf", "--yargi", kol)
        assert rc != 0, f"--yargi {kol} + cmk_istinaf DURMADI (rc=0):\n{out}"
        assert not _SON_GUN_RE.search(out), f"Durduruldu ama son gün yine basıldı:\n{out}"
        assert "ceza" in (out + err), "Hata mesajı doğru bayrağı (--yargi ceza) söylemiyor"


def test_A1_ceza_kolu_ceza_disi_kuralla_da_DURUR():
    """Ters yön aynı derecede tehlikelidir: hukuk/idari kuralına üç günlük ceza
    uzatması uygulamak süreyi YANLIŞ KISALTIR → hesap DURUR."""
    rc, out, err = _cli("--teblig", "2026-07-14", "--kural", "hmk_istinaf", "--yargi", "ceza")
    assert rc != 0, f"ceza kolu + hmk_istinaf DURMADI:\n{out}"
    assert not _SON_GUN_RE.search(out)


def test_A1_ceza_kuralsiz_serbest_sure_calisir():
    """--kural verilmeden --yargi ceza + --sure/--birim serbest hesap ÇALIŞIR
    (kural tablosunda olmayan ceza süreleri kapatılmamalı)."""
    rc, out, _err = _cli("--teblig", "2026-07-14", "--sure", "2", "--birim", "hafta",
                         "--yargi", "ceza")
    m = _SON_GUN_RE.search(out)
    assert rc == 0 and m and m.group(1) == "2026-09-03", out


def test_A1_m331_2_3_istisnasi_metinde_yazili():
    """m.331/2-3 (tatilde de yürütülen işler: soruşturma, tutuklu işlere ilişkin
    kovuşturma, ivedi işler; BAM/Yargıtay'da tutuklu hükümler) çıktıda görünür."""
    _son, _rapor, uyarilar = MOD.hesapla(date(2026, 7, 14), 2, "hafta", "ceza", "usul")
    metin = "\n".join(uyarilar)
    assert "331" in metin and "tutuklu" in metin.lower(), metin


def test_A1_ceza_tatil_kaymasinda_HMK_m93_gerekcesi_basilmaz():
    """Ceza kolunda son gün kayması CMK m.39/4 ile gerekçelendirilir, HMK m.93 ile değil."""
    # 2026-05-15 Cuma + 2 hafta = 2026-05-29 Cuma; tatil değil → 2026-05-30/31 hafta sonu değil.
    # Hafta sonuna denk gelen bir vaka seç: 2026-06-06 (Cmt) + 2 hafta = 2026-06-20 (Cmt)
    son, rapor, _uy = MOD.hesapla(date(2026, 6, 6), 2, "hafta", "ceza", "usul")
    metin = "\n".join(rapor)
    assert son.isoformat() == "2026-06-22", son.isoformat()
    assert "HMK m.93" not in metin, f"Ceza kolunda HMK m.93 gerekçesi:\n{metin}"
    assert "CMK m.39" in metin, f"CMK m.39/4 gerekçesi yok:\n{metin}"


# ══════════════════════════════════════════════════════════════════════════
# A-3 / A-5 / A-17 — yeni İYUK kuralları
# ══════════════════════════════════════════════════════════════════════════

_YENI_IYUK = {
    "iyuk_yd_itiraz":        (7, "gun", "27"),
    "iyuk_dava_ivedi":       (30, "gun", "20/A"),
    "iyuk_temyiz_ivedi":     (15, "gun", "20/A"),
    "iyuk_dava_sinav":       (10, "gun", "20/B"),
    "iyuk_temyiz_sinav":     (5, "gun", "20/B"),
    "iyuk_temyiz_cevap":     (30, "gun", "48"),
    "iyuk_temyiz_ozel_7gun": (7, "gun", "48"),
}


@pytest.mark.parametrize("ad,beklenen", sorted(_YENI_IYUK.items()))
def test_A3_A5_A17_yeni_iyuk_kurallari_tabloda(ad, beklenen):
    """MCP teyitli (2026-08-31) yeni İYUK kuralları hem tabloda hem CLI'da olmalı."""
    miktar, birim, capa = beklenen
    assert ad in MOD.KURALLAR, f"{ad} kural tablosunda yok"
    assert MOD.KURALLAR[ad][0] == miktar and MOD.KURALLAR[ad][1] == birim, MOD.KURALLAR[ad]
    assert capa in MOD.KURALLAR[ad][2], f"{ad} kaynak metni m.{capa} çıpası taşımıyor"
    rc, out, _err = _cli("--teblig", "2026-05-20", "--kural", ad, "--yargi", "idari")
    assert rc == 0 and _SON_GUN_RE.search(out), out


def test_A3_yd_itiraz_kurali_ivedi_ve_sinav_istisnasini_soyluyor():
    """İYUK m.20/A-2/e ve m.20/B-1/d: ivedi yargılama ve merkezî sınav davalarında
    YD kararlarına İTİRAZ EDİLEMEZ — kural metni bu istisnayı taşımalı."""
    kaynak = MOD.KURALLAR["iyuk_yd_itiraz"][2]
    assert "20/A" in kaynak and "20/B" in kaynak, kaynak
    # NOT: Türkçe "İ" ASCII "i"ye katlanmadığından .lower() ile karşılaştırılmaz.
    assert "İTİRAZ EDİLEMEZ" in kaynak, kaynak


def test_A3_yd_bloklari_cizelgede():
    """sure-cizelgesi.md yürütmenin durdurulması bloklarını taşımalı (aile grep=0'dı)."""
    m = CIZELGE.read_text(encoding="utf-8")
    for capa in ("m.27", "yürütmenin durdurulması", "tahsil işlemini durdurmaz", "m.27/7"):
        assert capa.lower() in m.lower(), f"çizelgede eksik: {capa}"


def test_A5_ivedi_ve_sinav_bloklari_cizelgede():
    """m.20/A, m.20/B ve m.45/8 (ivedide istinaf YOK) çizelgede yazılı olmalı."""
    m = CIZELGE.read_text(encoding="utf-8")
    for capa in ("m.20/A", "m.20/B", "ivedi yargılama", "m.45/8"):
        assert capa.lower() in m.lower(), f"çizelgede eksik: {capa}"


def test_A5_ozel_sure_uyarisi_iyuk_20A_20B_gosteriyor():
    """Eski uyarı ('özel kanun süreleri olabilir') avukatı YANLIŞ yöne bakıyordu;
    bu süreler İYUK'un kendisindedir."""
    _son, _rapor, uyarilar = MOD.hesapla(date(2026, 5, 20), 60, "gun", "idari", "usul")
    metin = "\n".join(uyarilar)
    assert "20/A" in metin and "20/B" in metin, metin


def test_A17_iyuk_m48_satirlari_cizelgede():
    """A-17: m.48/3 (30 gün cevap) ve m.48/6 + m.45/2 (7 gün) çizelgede."""
    m = CIZELGE.read_text(encoding="utf-8")
    assert "m.48/3" in m and "m.48/6" in m and "m.45/2" in m, "İYUK m.48 satırları eksik"


# ══════════════════════════════════════════════════════════════════════════
# A-4 — UETS: güvenli taraf tanımı + bozuk cümle + vergide dayanak
# ══════════════════════════════════════════════════════════════════════════

def test_A4_uets_guvenli_taraf_celiskisi_bitti():
    """Script ile SKILL.md aynı yönü söylemeli: BİZİM süremizde güvenli taraf
    ERKEN son gündür (Senaryo-1); karine (geç) senaryosu güvenli taraf DEĞİLDİR."""
    rc, out, _err = _cli("--teblig", "2026-08-10", "--kural", "iyuk_dava_vergi",
                         "--yargi", "idari", "--uets")
    assert rc == 0, out
    assert "güvenli taraf" in out.lower()
    # Eski (çelişkili) cümle bir daha basılmamalı:
    assert "güvenli taraf\n    KARİNE" not in out
    assert "güvenli taraf KARİNE" not in out.replace("\n    ", " ")


def test_A4_uets_vergi_dayanagi_VUK_107A():
    """Vergi kanadında e-tebliğ dayanağı VUK m.107/A'dır (7587 s.K. ile değişik),
    7201 m.7/a değil — çıktı kurala göre doğru dayanağı göstermeli."""
    rc, out, _err = _cli("--teblig", "2026-08-10", "--kural", "iyuk_dava_vergi",
                         "--yargi", "idari", "--uets")
    assert rc == 0 and "107/A" in out, out


def test_A4_uets_adli_dayanak_7201_kalir():
    """Adli tebligatta (HMK kolu) dayanak 7201 m.7/a olarak kalır."""
    rc, out, _err = _cli("--teblig", "2026-08-10", "--kural", "hmk_istinaf", "--uets")
    assert rc == 0 and "7201" in out, out


def test_A4_uets_iki_senaryo_hala_uretiliyor_regresyon():
    """Regresyon: --uets iki son gün üretmeye devam eder ve karine 5 gün ileridedir."""
    # Tebliğ öyle seçildi ki iki senaryoda da hafta sonu/tatil kayması YOK —
    # aksi hâlde fark 5 değil 6-7 çıkar (kayma senaryoyu değil takvimi izler).
    rc, out, _err = _cli("--teblig", "2026-05-20", "--kural", "hmk_istinaf", "--uets")
    tarihler = re.findall(r"→ son gün (\d{4}-\d{2}-\d{2})", out)
    assert rc == 0 and len(tarihler) >= 2, out
    assert (date.fromisoformat(tarihler[1]) - date.fromisoformat(tarihler[0])).days == 5


# ══════════════════════════════════════════════════════════════════════════
# A-7 — adli tatil istisnası gerekçesi yargı koluna göre
# ══════════════════════════════════════════════════════════════════════════

def test_A7_idari_istisna_IYUK_m62_ile_gerekcelendirilir():
    """İdari yargının nöbetçi mahkeme kataloğu İYUK m.62'dir; HMK m.103 DEĞİL."""
    _son, rapor, uyarilar = MOD.hesapla(date(2026, 7, 15), 30, "gun", "idari", "usul",
                                        adli_tatil_istisna=True)
    metin = "\n".join(rapor + uyarilar)
    assert "m.62" in metin, f"İYUK m.62 çıpası yok:\n{metin}"
    assert "delillerin tespiti" in metin, f"m.62/a kataloğu yok:\n{metin}"
    # Asıl kilit: HMK m.103 KATALOĞUNUN gerekçe olarak basılmaması. (m.103'ün adının
    # "bu katalog idari yargıda geçerli DEĞİLDİR" diye anılması istenen davranıştır.)
    for yanlis in ("nafaka", "çekişmesiz yargı", "iş mahkemesi"):
        assert yanlis not in metin, (
            f"İdari kolda HMK m.103 kataloğu kalemi basıldı ({yanlis}):\n{metin}")


def test_A7_hukuk_istisna_m103_bent_bent_ve_davaci_sifati():
    """HMK m.103/1-ç istisnası DAVACI SIFATINA bağlıdır ('işçilerin AÇTIKLARI davalar')."""
    _son, rapor, uyarilar = MOD.hesapla(date(2026, 7, 15), 2, "hafta", "hukuk", "usul",
                                        adli_tatil_istisna=True)
    metin = "\n".join(rapor + uyarilar)
    assert "m.103" in metin
    # NOT: Türkçe "İ" ASCII "i"ye katlanmadığı için .lower() ile karşılaştırılmaz.
    assert "AÇTIKLARI" in metin, f"m.103/1-ç davacı sıfatı şerhi yok:\n{metin}"
    assert "İŞVEREN" in metin, f"davacı sıfatı şerhi (işverenin açtığı dava) yok:\n{metin}"
    assert "soybağı" in metin or "velayet" in metin, f"m.103/1-b eksik:\n{metin}"


def test_A7_ceza_istisnasinda_m331_lafzi_uyarisi():
    """CMK m.331/4 lafzında istisna YOKTUR — ceza kolunda bayrak kullanılırsa
    bu açıkça uyarılmalı (sessiz kısaltma yasağı)."""
    _son, rapor, uyarilar = MOD.hesapla(date(2026, 7, 14), 2, "hafta", "ceza", "usul",
                                        adli_tatil_istisna=True)
    metin = "\n".join(rapor + uyarilar)
    assert "331" in metin, metin
    assert "İSTİSNA YOKTUR" in metin, (
        f"m.331/4 lafzında istisna olmadığı söylenmiyor:\n{metin}")
    # m.103 KATALOĞU ceza dosyasına gerekçe olarak basılamaz:
    for yanlis in ("nafaka", "çekişmesiz yargı", "dispeçci"):
        assert yanlis not in metin, (
            f"Ceza kolunda HMK m.103 kataloğu basıldı ({yanlis}):\n{metin}")


# ══════════════════════════════════════════════════════════════════════════
# A-9 — sure_kurallari.json `_dikkat_cmk` notu
# ══════════════════════════════════════════════════════════════════════════

def test_A9_dikkat_cmk_notu_yururlukteki_hukuku_anlatiyor():
    """Not, kendi teyitli kayıtlarını çürütmemeli: m.273/m.291/m.268 üçü de
    İKİ HAFTA (MCP 2026-08-31); f.2'ler 7499 s.K. ile MÜLGA."""
    d = json.loads(KURAL_JSON.read_text(encoding="utf-8"))
    not_ = d.get("_dikkat_cmk", "")
    assert "7 gün" not in not_ and "15 gün" not in not_, (
        "Not hâlâ mülga rejimi (7/15 gün) anlatıyor: " + not_)
    if not_:
        # NOT: Türkçe "İ" ASCII "i"ye katlanmadığı için .lower() kullanılmaz.
        assert ("İKİ HAFTA" in not_ or "iki hafta" in not_), not_
        assert "7499" in not_ and "MÜLGA" in not_, not_
        assert "331/4" in not_, "not, ceza adli tatil rejimini (m.331/4) anmıyor: " + not_


def test_A9_cmk_kayitlarinin_teyit_tarihi_dolu():
    d = json.loads(KURAL_JSON.read_text(encoding="utf-8"))["kurallar"]
    for k in ("cmk_itiraz", "cmk_istinaf", "cmk_temyiz"):
        assert d[k]["mcp_teyit_tarihi"], f"{k}: mcp_teyit_tarihi boş"


# ══════════════════════════════════════════════════════════════════════════
# A-10 — eski hâle getirme uyarısı yargı koluna duyarlı
# ══════════════════════════════════════════════════════════════════════════

def test_A10_idari_kolda_HMK_m95_onerilmez():
    """2577'de 'eski hale getirme/mazeret' = 0 eşleşme (MCP). İdari yargıda
    HMK m.95 var olmayan bir kurtarma kapısıdır."""
    tatiller = MOD.TATILLER.get("idari_izin", {})
    gunler = sorted(tatiller.get("2026", []))
    if not gunler:
        pytest.skip("tatiller.json'da 2026 idari izin kaydı yok")
    hedef = date.fromisoformat(gunler[0])
    _son, rapor, uyarilar = MOD.hesapla(hedef - MOD.timedelta(days=1), 1, "gun", "idari", "usul")
    metin = "\n".join(rapor + uyarilar)
    if "İDARİ İZİN" in metin:
        # HMK m.95 ancak "GÜVENME" bağlamında anılabilir; ÖNERİ olarak asla.
        assert "eski hâle getirme (HMK m.95" not in metin, (
            f"İdari kolda HMK m.95 kurtarma kapısı olarak önerildi:\n{metin}")
        assert "KURUMU YOKTUR" in metin, (
            f"İYUK'ta eski hâle getirme olmadığı yazılmamış:\n{metin}")
        assert "m.40/2" in metin and "düzeltme" in metin, metin


def test_A10_hukuk_kolunda_HMK_m95_korunur():
    """Hukuk kolunda mevcut davranış (HMK m.95 ihtiyat notu) aynen kalır."""
    src = SCRIPT.read_text(encoding="utf-8")
    assert "HMK m.95" in src, "hukuk kolu için m.95 notu tamamen silinmemeli"


# ══════════════════════════════════════════════════════════════════════════
# A-20 — 6183 m.58 + çalışmaya ara uzaması TARTIŞMALI
# ══════════════════════════════════════════════════════════════════════════

def test_A20_amme_58_uzamasi_tartismali_serhi_basiliyor():
    """Danıştay 7.D. E.2000/5685 K.2002/3522 (MCP tam metin, 13.11.2002):
    çoğunluk uzamadan yana ama karar OYÇOKLUĞU; tetkik hâkimi + savcı + ayrışık
    oy aksi yönde. Tarih kesin bilgi gibi sunulamaz."""
    rc, out, _err = _cli("--teblig", "2026-08-10", "--kural", "amme_6183_m58", "--yargi", "idari")
    assert rc == 0, out
    assert "TARTIŞMALI" in out, f"TARTIŞMALI şerhi yok:\n{out}"
    assert "2000/5685" in out or "oyçokluğu" in out.lower(), out


def test_A20_serh_yalniz_uzama_uygulandiginda_basilir():
    """Ham bitiş çalışmaya ara dışındaysa şerh basılmaz (gürültü disiplini)."""
    rc, out, _err = _cli("--teblig", "2026-01-10", "--kural", "amme_6183_m58", "--yargi", "idari")
    assert rc == 0 and "TARTIŞMALI" not in out, out


# ══════════════════════════════════════════════════════════════════════════
# B-16 — negatif / sıfır süre
# ══════════════════════════════════════════════════════════════════════════

def test_B16_negatif_sure_reddedilir():
    """`--sure -5` bugün 'son gün 2026-05-15' (tebliğden ÖNCE) verip exit 0 dönüyordu."""
    rc, out, err = _cli("--teblig", "2026-05-20", "--sure", "-5", "--birim", "gun")
    assert rc != 0, f"negatif süre kabul edildi:\n{out}"
    assert not _SON_GUN_RE.search(out), out
    assert "traceback" not in (out + err).lower()


def test_B16_sifir_sure_dogru_mesajla_reddedilir():
    """`--sure 0` 'alan eksik' YALANINI söylememeli — sıfır süre olarak reddedilmeli."""
    rc, out, err = _cli("--teblig", "2026-05-20", "--sure", "0", "--birim", "gun")
    assert rc != 0
    metin = (out + err).lower()
    assert "ya --kural ver" not in metin, "sıfır süre hâlâ 'alan eksik' sanılıyor: " + metin


def test_B16_son_gun_asla_tebligden_once_olamaz():
    """Sağlık kontrolü: hesapla() geçmişe düşen bir son gün üretemez."""
    with pytest.raises(ValueError):
        MOD.hesapla(date(2026, 5, 20), -5, "gun", "hukuk", "usul")


# ══════════════════════════════════════════════════════════════════════════
# B-22 — bozuk/uç tarih ve miktar: temiz hata, traceback YOK
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("teblig", ["2026-13-45", "2026-02-30", "abc", "20.05.2026", ""])
def test_B22_bozuk_tarih_temiz_hata(teblig):
    rc, out, err = _cli("--teblig", teblig, "--kural", "hmk_istinaf")
    metin = out + err
    assert rc != 0, metin
    assert "Traceback" not in metin, f"ham traceback:\n{metin}"
    assert "ValueError" not in metin


@pytest.mark.parametrize("miktar", ["999999999", "100000"])
def test_B22_asiri_miktar_temiz_hata(miktar):
    rc, out, err = _cli("--teblig", "2026-05-20", "--sure", miktar, "--birim", "yil")
    metin = out + err
    assert rc != 0, metin
    assert "Traceback" not in metin and "OverflowError" not in metin, metin


@pytest.mark.parametrize("teblig", ["9999-12-31", "0001-01-01"])
def test_B22_uc_tarihlerde_cokmez(teblig):
    """Uç ama GEÇERLİ tarihlerde ya temiz hesap ya temiz hata — traceback YOK."""
    rc, out, err = _cli("--teblig", teblig, "--kural", "hmk_istinaf")
    metin = out + err
    assert "Traceback" not in metin, metin


def test_B22_pencere_bozuk_tarihte_hala_nazik_atlar_regresyon():
    """Regresyon: --pencereler tarafındaki mevcut nazik 'atlandı' disiplini bozulmadı."""
    import tempfile, os
    kayitlar = [{"ad": "Bozuk", "teblig": "tarih-degil", "kural": "hmk_istinaf"},
                {"ad": "Geçerli", "teblig": "2026-05-20", "kural": "hmk_istinaf"}]
    fd, yol = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(kayitlar, f, ensure_ascii=False)
    try:
        cp = subprocess.run([sys.executable, str(SCRIPT), "--pencereler", yol],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
        assert "Traceback" not in (cp.stdout + cp.stderr)
        assert "atlandı" in cp.stdout
    finally:
        os.unlink(yol)


# ══════════════════════════════════════════════════════════════════════════
# B-20 — başlangıç türü ↔ kural uyuşmazlığı
# ══════════════════════════════════════════════════════════════════════════

def test_B20_kuralla_celisen_baslangic_turu_uyari_uretir():
    """cmk_istinaf'ın TEK başlangıcı gerekçeli karar tebliğidir (m.273 f.2 MÜLGA);
    'tefhim' seçilirse çelişki sessiz kalamaz."""
    rc, out, _err = _cli("--teblig", "2026-03-02", "--kural", "cmk_istinaf",
                         "--yargi", "ceza", "--baslangic-turu", "tefhim")
    assert rc == 0, out
    assert "BAŞLANGIÇ TÜRÜ" in out.upper()
    assert "tefhim" in out
    # uyarı bölümünde çelişki işaretlenmiş olmalı
    uyari_blogu = out.split("UYARILAR", 1)[-1]
    assert "tefhim" in uyari_blogu, f"çelişki uyarısı basılmadı:\n{out}"


def test_B20_uyumlu_baslangic_turunde_uyari_yok():
    """cmk_itiraz + ogrenme uyumludur (m.268: 'kararı öğrendiği günden') → uyarı yok."""
    rc, out, _err = _cli("--teblig", "2026-03-02", "--kural", "cmk_itiraz",
                         "--yargi", "ceza", "--baslangic-turu", "ogrenme")
    uyari_blogu = out.split("UYARILAR", 1)[-1]
    assert rc == 0 and "BAŞLANGIÇ TÜRÜ ÇELİŞKİSİ" not in uyari_blogu.upper(), out


def test_B20_baslangic_turu_verilmezse_davranis_degismez_regresyon():
    rc, out, _err = _cli("--teblig", "2026-05-20", "--kural", "hmk_istinaf")
    m = _SON_GUN_RE.search(out)
    assert rc == 0 and m and m.group(1) == "2026-06-03", out


# ══════════════════════════════════════════════════════════════════════════
# B-21 — İKİZ KURAL TABLOSU MEKANİK KİLİDİ (ailenin en tekrar eden kırılması)
# ══════════════════════════════════════════════════════════════════════════

def test_B21_gomulu_ve_json_kural_tablosu_BIREBIR_ayni():
    """`_GOMULU_KURALLAR` ↔ `sure_kurallari.json`: anahtar, miktar, birim VE
    kaynak metni birebir aynı olmalı. Bu, ailenin en tekrar eden kırılma
    desenidir (ikiz liste ayrışması) — gelecekteki ayrışmayı mekanik yakalar."""
    j = json.loads(KURAL_JSON.read_text(encoding="utf-8"))["kurallar"]
    g = MOD._GOMULU_KURALLAR
    assert set(g) == set(j), (
        f"anahtar kümesi ayrıştı — yalnız gömülüde: {sorted(set(g) - set(j))}; "
        f"yalnız JSON'da: {sorted(set(j) - set(g))}")
    ayrisan = []
    for k in sorted(g):
        miktar, birim, kaynak = g[k]
        if miktar != j[k]["miktar"]:
            ayrisan.append(f"{k}.miktar: {miktar} != {j[k]['miktar']}")
        if birim != j[k]["birim"]:
            ayrisan.append(f"{k}.birim: {birim} != {j[k]['birim']}")
        if kaynak != j[k].get("kaynak"):
            ayrisan.append(f"{k}.kaynak metni farklı")
    assert not ayrisan, "İKİZ TABLO AYRIŞMASI:\n  " + "\n  ".join(ayrisan)


def test_B21_teyit_tarihleri_de_birebir_ayni():
    """Fallback yolu 'teyit boş' derken gömülü metin '(MCP teyit ...)' diyordu —
    aynı ekranda iki zıt beyan. Teyit tarihi artık tek yerde, iki tabloda aynı."""
    j = json.loads(KURAL_JSON.read_text(encoding="utf-8"))["kurallar"]
    for k, v in sorted(MOD._GOMULU_TEYIT.items()):
        assert v == (j[k].get("mcp_teyit_tarihi") or ""), (
            f"{k}: teyit tarihi ayrıştı ({v!r} != {j[k].get('mcp_teyit_tarihi')!r})")
    assert set(MOD._GOMULU_TEYIT) == set(MOD._GOMULU_KURALLAR)


def test_B21_kaynak_metninde_gomulu_teyit_dizesi_YOK():
    """Teyit tarihi METİNDEN alana taşındı — kaynak metni artık '(MCP teyit ...)'
    içermemeli (aksi hâlde iki kaynak yeniden doğar)."""
    for k, (_m, _b, kaynak) in sorted(MOD._GOMULU_KURALLAR.items()):
        assert "MCP teyit 20" not in kaynak, f"{k} kaynak metni hâlâ teyit tarihi taşıyor"


def test_B21_json_bozuksa_SESSIZ_dusmez(tmp_path, monkeypatch):
    """JSON okunamazsa gömülüye düşülür AMA bu SESSİZ olmaz — görünür uyarı."""
    bozuk = tmp_path / "sure_kurallari.json"
    bozuk.write_text("{ bozuk json", encoding="utf-8")
    kopya = tmp_path / "hesapla_sure.py"
    kopya.write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    cp = subprocess.run(
        [sys.executable, str(kopya), "--teblig", "2026-05-20", "--kural", "hmk_istinaf",
         "--flagsiz"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    metin = cp.stdout + cp.stderr
    assert cp.returncode == 0, metin
    assert "gömülü" in metin.lower(), metin
    assert "bozuk" in metin.lower() or "okunamadı" in metin.lower(), (
        "JSON bozukluğu sessizce yutuldu:\n" + metin)


# ══════════════════════════════════════════════════════════════════════════
# B-19 — bayraklar talimat katmanında belgeli mi
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("bayrak", ["--adli-tatil-istisna", "--uets", "--baslangic-turu"])
def test_B19_bayraklar_SKILL_md_de_belgeli(bayrak):
    """Üç bayrak da SKILL.md'de tam-dize olarak geçmeli (denetimde 0 isabetti)."""
    assert bayrak in SKILL_MD.read_text(encoding="utf-8"), f"{bayrak} SKILL.md'de yok"


def test_B19_m103_istisnasi_talimat_katmaninda():
    """--adli-tatil-istisna'nın hangi işlerde kullanılacağı (HMK m.103) talimatta yazılı."""
    md = SKILL_MD.read_text(encoding="utf-8")
    assert "m.103" in md and "işçilerin açtıkları" in md, "m.103 kapsamı talimatta eksik"


# ══════════════════════════════════════════════════════════════════════════
# A-6 — AYM tarafından iptal edilmiş 6183 m.58/5
# ══════════════════════════════════════════════════════════════════════════

def test_A6_haksiz_cikma_zammi_iptal_serhi():
    """6183 m.58/5 AYM E.2021/119, K.2022/48 (21/4/2022) ile İPTAL edilmiştir;
    yürürlükteymiş gibi hatırlatılamaz."""
    m = CIZELGE.read_text(encoding="utf-8")
    assert "m.58/5 haksız itiraz zammı yönü hatırlanır" not in m, "eski ibare duruyor"
    assert "2021/119" in m and "2022/48" in m, "AYM iptal künyesi yazılmamış"
    idx = m.find("2021/119")
    assert "iptal" in m[max(0, idx - 300):idx + 300].lower()


# ══════════════════════════════════════════════════════════════════════════
# GENEL REGRESYON — mevcut altın vakalar bozulmadı
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("teblig,beklenen,yargi,miktar,birim", [
    ("2026-06-06", "2026-06-22", "hukuk", 2, "hafta"),   # hafta sonu kayması
    ("2026-07-15", "2026-09-07", "hukuk", 2, "hafta"),   # HMK m.104
    ("2026-05-20", "2026-06-03", "hukuk", 2, "hafta"),   # normal
    ("2026-07-15", "2026-09-07", "idari", 30, "gun"),    # İYUK m.8/3
])
def test_altin_vakalar_korundu(teblig, beklenen, yargi, miktar, birim):
    son, _r, _u = MOD.hesapla(date.fromisoformat(teblig), miktar, birim, yargi, "usul")
    assert son.isoformat() == beklenen


def test_maddi_sure_adli_tatil_uygulanmaz_regresyon():
    son, rapor, _u = MOD.hesapla(date(2026, 7, 15), 2, "hafta", "hukuk", "maddi")
    assert son.isoformat() == "2026-07-29"
    assert "Maddi hukuk süresi" in "\n".join(rapor)


def test_degisiklik_gunlugunde_v0514_kaydi_var():
    g = GUNLUK.read_text(encoding="utf-8")
    assert "v0.5.14" in g, "değişiklik günlüğüne v0.5.14 girişi yazılmamış"
    for bid in ("A-1", "A-3", "A-5", "B-16", "B-21", "B-22"):
        assert bid in g, f"günlükte {bid} bulgu kimliği anılmamış"


def test_utf8_guard_korundu():
    assert "__OA_UTF8_GUARD__" in SCRIPT.read_text(encoding="utf-8")

# -*- coding: utf-8 -*-
"""v0.5.18 — İŞ MAHKEMESİ SÜRELERİ: kural tabanı + İŞ GÜNÜ birimi.

2026-09-10 denetiminin **B7** bulgusu kapatıldı. O gün ölçülen durum şuydu:
kural tabanındaki 21 kuralın **hiçbiri iş hukuku değildi** ve motor `isgunu`
birimini **tanımıyordu** — oysa 4857 m.21/5 süresi takvim günü değil İŞ GÜNÜ
sayar. Kural yokken sistem fail-closed davranıyordu (argparse reddediyordu),
yani sessiz yanlış hesap yoktu; ama iş mahkemesi dosyasında avukat motoru
hiç kullanamıyordu.

Buradaki her sözleşme MCP'den teyitlidir (2026-09-10):
  4857 m.20/1  (7036/11) — arabulucuya başvuru 1 ay · dava 2 hafta (son tutanak)
  4857 m.21/1,5,6        — işe başlatma 1 ay · başvuru 10 İŞGÜNÜ · sonucu
  4857 Ek m.3  (7036/15) — zamanaşımı 5 yıl
  7036 m.3     (7445/41) — dava şartı olarak arabuluculuk
  6325 m.18/A-15         — arabuluculukta zamanaşımı durur, hak düşürücü işlemez
"""
import json
import pathlib
import subprocess
import sys
from datetime import date, timedelta

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-sure"
SCRIPT = SKILL / "scripts" / "hesapla_sure.py"
KURAL_JSON = SKILL / "scripts" / "sure_kurallari.json"

sys.path.insert(0, str(SCRIPT.parent))
import hesapla_sure as H  # noqa: E402

IS_KURALLARI = {
    "is_ise_iade_arabulucu":     (1, "ay",     ["teblig"]),
    "is_ise_iade_dava":          (2, "hafta",  ["olay"]),
    "is_ise_iade_arabulucu_ret": (2, "hafta",  ["teblig"]),
    "is_ise_baslatma_basvuru":   (10, "isgunu", ["teblig"]),
    "is_ise_baslatma_isveren":   (1, "ay",     ["olay"]),
    "is_zamanasimi_5yil":        (5, "yil",    ["olay", "ogrenme"]),
}


# ── KURAL TABANI ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("ad,beklenen", sorted(
    (a, (m, b)) for a, (m, b, _t) in IS_KURALLARI.items()))
def test_is_kurali_json_ve_gomulude_AYNI(ad, beklenen):
    """B7: kural tabanında iş hukuku YOKTU. Artık var — ve JSON ile gömülü
    fallback tablosu AYRIŞAMAZ (mevcut B-21 ikiz kilidinin iş hukuku ayağı)."""
    kurallar, _teyit, _gomuluye_dusuldu = H.kurallari_yukle()
    assert ad in kurallar, "kural JSON'da YOK: %s" % ad
    assert kurallar[ad][:2] == beklenen, "JSON miktar/birim ayrıştı: %s" % ad
    assert ad in H._GOMULU_KURALLAR, "kural gömülü fallback'te YOK: %s" % ad
    assert H._GOMULU_KURALLAR[ad][:2] == beklenen, "gömülü miktar/birim ayrıştı: %s" % ad


@pytest.mark.parametrize("ad", sorted(IS_KURALLARI))
def test_is_kurali_mcp_teyit_tarihi_ve_madde_capasi_tasir(ad):
    """Süre HUKUKİ kuraldır: çıpasız kural yazılamaz (ailenin teyit disiplini)."""
    veri = json.loads(KURAL_JSON.read_text(encoding="utf-8"))["kurallar"][ad]
    assert veri.get("mcp_teyit_tarihi"), "teyit tarihi yok: %s" % ad
    kaynak = veri.get("kaynak", "")
    assert "4857" in kaynak or "7036" in kaynak, "madde çıpası yok: %s → %r" % (ad, kaynak)
    assert len(kaynak) > 80, "kaynak metni yüzeysel: %s" % ad


@pytest.mark.parametrize("ad,izinli", sorted(
    (a, t) for a, (_m, _b, t) in IS_KURALLARI.items()))
def test_is_kurali_izinli_baslangic_turleri(ad, izinli):
    """'Yanlış olaya bağlanan doğru hesap, yanlış hesaptır' (B-20).

    İşe iade DAVASI süresi tebliğden değil son tutanağın DÜZENLENMESİNDEN
    (olay) işler; işverenin işe başlatma süresi ise işçinin BAŞVURUSUNDAN.
    Bu ayrım kapalı kümede tutulur ki çelişki sessiz kalmasın."""
    H.kurallari_yukle()
    assert sorted(H.KURAL_BASLANGIC[ad]) == sorted(izinli)


def test_is_kurallari_hukuk_koluna_bagli():
    """`is_` ön eki hukuk koluna çözülmeli; çözülmezse `kol_uyusmazligi`
    denetimi iş dosyasında kör kalır."""
    for ad in IS_KURALLARI:
        assert H.kural_kolu(ad) == "hukuk", ad


# ── İŞ GÜNÜ BİRİMİ ────────────────────────────────────────────────────────

def test_isgunu_hafta_sonu_ve_resmi_tatilleri_ATLAR():
    """4857 m.21/5 'on işgünü' — motor bu birimi HİÇ tanımıyordu."""
    teb = date(2026, 3, 6)                      # Cuma
    son = H._is_gunu_ekle(teb, 10)
    elde, sayac = teb, 0
    while sayac < 10:
        elde += timedelta(days=1)
        if H.is_gunu_mu(elde):
            sayac += 1
    assert son == elde
    assert H.is_gunu_mu(son), "son gün iş günü olmak zorunda"


def test_isgunu_takvim_gununden_FARKLI_ve_daha_GEC():
    """İş günü ile takvim günü karıştırılırsa hak erken kapatılmış sayılır.

    Aynı örnekte fark bir haftadır: takvim 16 Mart, iş günü 23 Mart. Takvim
    hesabına güvenen avukat, 20 Mart'ta yapılan geçerli bir başvuruyu
    'süresi geçmiş' sanar."""
    teb = date(2026, 3, 6)
    isgunu = H._is_gunu_ekle(teb, 10)
    takvim = teb + timedelta(days=10)
    assert isgunu > takvim
    assert (isgunu - takvim).days >= 5


def test_isgunu_baslangic_gunu_SAYILMAZ():
    """Tebliğ günü süreye dâhil değildir (HMK m.92 mantığı ile simetrik)."""
    pzt = date(2026, 3, 9)                       # Pazartesi, iş günü
    assert H.is_gunu_mu(pzt)
    assert H._is_gunu_ekle(pzt, 1) == date(2026, 3, 10)


def test_isgunu_MIKTAR_DOGRULAMASINA_tabi():
    """Yeni birim, mevcut B-16 girdi denetiminin dışında kalamaz."""
    assert "isgunu" in H.MIKTAR_UST_SINIR
    assert H.miktar_dogrula(0, "isgunu")
    assert H.miktar_dogrula(-5, "isgunu")
    assert H.miktar_dogrula(H.MIKTAR_UST_SINIR["isgunu"] + 1, "isgunu")
    assert H.miktar_dogrula(10, "isgunu") is None


def test_isgunu_adli_tatil_UZATMASI_uygulanmaz_ama_GORUNUR():
    """Sayım tatilleri zaten atlar; ayrıca 4857 m.21/5 süresi MAHKEMEYE değil
    İŞVERENE başvuru süresidir. Uzatma uygulamak GEÇ tarih üretirdi — geç
    tarih hak kaybettirir. Ama sessiz kalmaz: görünür uyarı basılır."""
    son, _rapor, uyarilar = H.hesapla(
        date(2026, 8, 10), 10, "isgunu", "hukuk", tur="usul",
        kural="is_ise_baslatma_basvuru")
    assert H.aralik_icinde_mi(son), "bu senaryo adli tatil aralığına düşmeli"
    assert son < date(2026, 9, 1), "uzatma UYGULANMAMALI (7 Eylül'e taşınmamalı)"
    assert any("İŞ GÜNÜ + ADLİ TATİL" in u for u in uyarilar), \
        "uzatmanın uygulanmadığı GÖRÜNÜR olmalı (sessiz atlama yasağı)"


# ── HESAP DOĞRULUĞU — GERÇEK YARGITAY VAKASI ──────────────────────────────

def test_ay_hesabi_YARGITAY_olcutuyle_ayni():
    """Y. 9. HD E.2016/10425 K.2017/8620 (23.05.2017): ikale 29.08.2015 ise
    bir aylık hak düşürücü süre **29.09.2015** mesai bitiminde dolar. İlk
    derece mahkemesi 'ertesi günden başlar, 30 Eylül' demiş; Yargıtay bunu
    *'yasanın düzenlemesine AÇIKÇA AYKIRI'* bulmuştur."""
    son, _r, _u = H.hesapla(date(2015, 8, 29), 1, "ay", "hukuk", tur="maddi",
                            kural="is_ise_iade_arabulucu")
    assert son == date(2015, 9, 29), "Yargıtay ölçütünden sapma: %s" % son


@pytest.mark.parametrize("tutanak,beklenen", [
    (date(2018, 11, 27), date(2018, 12, 11)),
    (date(2019, 1, 9),   date(2019, 1, 23)),
    (date(2018, 3, 7),   date(2018, 3, 21)),
])
def test_ise_iade_iki_hafta_mahkeme_kararlariyla_ayni(tutanak, beklenen):
    """Yargı Pro'dan çekilen üç gerçek BAM/Yargıtay vakasında mahkemenin
    kabul ettiği son gün ile motorun sonucu birebir."""
    son, _r, _u = H.hesapla(tutanak, 2, "hafta", "hukuk", tur="usul",
                            kural="is_ise_iade_dava")
    assert son == beklenen


# ── UYARI KATMANI — hesap dışı üç mekanizma görünür olmalı ────────────────

@pytest.mark.parametrize("ad", sorted(IS_KURALLARI))
def test_her_is_kuralinda_dava_sarti_ve_DURMA_uyarisi_basilir(ad):
    """Arabuluculuk (a) DAVA ŞARTIdır ve (b) süreyi DURDURUR; ikisi de tarih
    aritmetiğinin dışındadır ve script bunları hesaplayamaz. Görünür
    kılınmazlarsa doğru aritmetik yanlış tarihe götürür."""
    m, b, _ = H.KURALLAR[ad]
    _s, _r, uyarilar = H.hesapla(date(2026, 3, 2), m, b, "hukuk",
                                 tur="maddi" if b == "yil" else "usul", kural=ad)
    metin = " ".join(uyarilar)
    assert "DAVA ŞARTIDIR" in metin, "7036 m.3 dava şartı uyarısı yok: %s" % ad
    assert "6325" in metin and "DURUR" in metin, "durma uyarısı yok: %s" % ad
    assert "m.103/1-ç" in metin, "HMK m.103/1-ç (işçinin açtığı dava) uyarısı yok: %s" % ad


def test_ise_iade_davasinda_TARTISMALI_baslangic_uyarisi():
    """İki haftalık sürenin başlangıcı içtihatta ayrışıktır ve Yargıtay 9. HD
    (E.2024/10170, K.2024/14797, 18.11.2024) uyuşmazlığın giderilmesine YER
    OLMADIĞINA karar verdiği için ayrılık SÜRMEKTEDİR. Avukat bunu bilmeden
    geç senaryoya güvenirse hak düşer."""
    _s, _r, uyarilar = H.hesapla(date(2026, 4, 10), 2, "hafta", "hukuk",
                                 tur="usul", kural="is_ise_iade_dava")
    metin = " ".join(uyarilar)
    assert "BAŞLANGIÇ TARTIŞMALI" in metin
    assert "2024/14797" in metin, "güncel içtihat çıpası yok"
    assert "GÜVENLİ PLAN" in metin, "hangi senaryonun güvenli olduğu yazılmalı"


def test_ise_baslatma_basvurusunda_HAK_KAYBI_sonucu_yazilir():
    """4857 m.21/6 — süresinde başvurmayan işçi bakımından fesih GEÇERLİ
    sayılır; kazanılmış işe iade kararı işlevsizleşir."""
    _s, _r, uyarilar = H.hesapla(date(2026, 3, 6), 10, "isgunu", "hukuk",
                                 tur="usul", kural="is_ise_baslatma_basvuru")
    metin = " ".join(uyarilar)
    assert "m.21/6" in metin
    assert "GEÇERLİ BİR FESİH SAYILIR" in metin


def test_is_disi_kuralda_is_hukuku_uyarilari_BASILMAZ():
    """Uyarı katmanı yalnız `is_` kurallarına bağlıdır; her hesabı iş hukuku
    metniyle doldurmak gürültüdür (zero-fluff sınırı)."""
    _s, _r, uyarilar = H.hesapla(date(2026, 3, 2), 2, "hafta", "hukuk",
                                 tur="usul", kural="hmk_istinaf")
    metin = " ".join(uyarilar)
    assert "DAVA ŞARTIDIR" not in metin
    assert "6325" not in metin


# ── CLI ───────────────────────────────────────────────────────────────────

def test_cli_is_kurallarini_ve_isgunu_birimini_kabul_eder():
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--teblig", "2026-03-06",
         "--kural", "is_ise_baslatma_basvuru", "--flagsiz"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO), timeout=120)
    assert cp.returncode == 0, cp.stderr
    assert "2026-03-23" in cp.stdout, cp.stdout
    assert "İŞ GÜNÜ" in cp.stdout
    assert "4857 m.21/5" in cp.stdout


def test_cli_birim_secenekleri_isgunu_tasir():
    cp = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(REPO), timeout=120)
    assert "isgunu" in cp.stdout

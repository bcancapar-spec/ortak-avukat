# -*- coding: utf-8 -*-
"""v0.5.16 — GRUP F: oa-vakia İSPAT ONTOLOJİSİ düzeltmesi (P0-1 / A-13).

Bulgu (dış denetim A-13, ⚠ P0 «yeşil matris, dinlenmeyen delil»):
`vakia_matris.py` ISPAT_TAM kümesinde `tanik` ve `karine` "tek başına
belgeli destek" sayılıyordu. Oysa:
  * TANIK şartlı delildir — senetle ispat zorunluluğu (HMK m.200) ve senede
    karşı tanık yasağı (m.201) altında dinlenemeyebilir; delil başlangıcı
    (m.202) veya m.203 istisnaları gerekir. Caizliği belirsiz tanık iddiayı
    "belgeli" yapamaz.
  * KARİNE ispat etmez, ispat yükünü kaydırır (HMK m.190/2).
  * HUKUKİ iddia (hukuki nitelendirme) delille ispatlanmaz; bilirkişi de
    hukuki konuda delil değildir (HMK m.266 sınırı).
Sonuç: bugüne kadar YEŞİL görünen bazı matrisler KIRMIZIYA döner — istenen
etkidir.

(Tüm madde metinleri Mevzuat MCP'den 2026-09-06'da fiilen okunmuştur.)

Kapatılan beklentiler:
  1. iddialar[].tur ∈ {vakia, hukuki}; yoksa «vakia» + [BİLGİ].
  2. olaylar[].caizlik ∈ {caiz, sinirli, caiz_degil, bilinmiyor}; yoksa
     «bilinmiyor» (fail-closed). caiz → TAM; sinirli/bilinmiyor → kısmi;
     caiz_degil → sayılmaz.
  3. karine → yuk_kaydiran sınıfı; belgeli SAYILMAZ.
  4. ISPAT_TAM = {belgeli, ikrar, yemin, bilirkisi}; ISPAT_KISMI = {beyan,
     tanik}; ISPAT adı/rolü korunur (iskelet + geçersiz-etiket denetimi).
  5. JSON şeması genişler: satır `tur`/`yuk_kaydiran`/`tanik_caizlik_belirsiz`,
     `ozet.hukuki_iddia`/`ozet.yuk_kaydiran_karine`; ÜST-DÜZEY anahtar
     kümesi DEĞİŞMEZ; exit sözleşmesi (dogrula'da sys.exit yok) KORUNUR.
  6. Eski JSON (yeni alanlar yok) çökmeden çalışır.

Girdiler tempfile tabanlı İZOLE dizinlerde üretilir; kişi/dosya adları
sentetiktir; repo dosyalarına dokunulmaz.
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
VAKIA_DIR = SKILLS / "oa-vakia"
SCRIPT = VAKIA_DIR / "scripts" / "vakia_matris.py"
SKILL_MD = VAKIA_DIR / "SKILL.md"

UST_DUZEY_ANAHTARLAR = {
    "arac", "girdi", "kronoloji", "tarihsiz", "iddia_delil_matrisi",
    "ispat_bosluklari", "yetim_deliller", "gecersiz_referans",
    "gecersiz_ispat_durumu", "ozne_eslestirme", "ozet", "saglikli",
}
SATIR_ANAHTARLAR = {
    "iddia_id", "metin", "tur", "destekler", "belgeli", "kismi_destek",
    "yuk_kaydiran", "tanik_caizlik_belirsiz",
}
OZET_ANAHTARLAR = {
    "iddia", "belgeli_destekli", "ispat_boslugu", "olay", "tarihsiz",
    "yetim", "hukuki_iddia", "yuk_kaydiran_karine",
}


def _cli(*args):
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), *[str(a) for a in args]],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return cp.returncode, cp.stdout or "", cp.stderr or ""


@pytest.fixture
def izole_dizin():
    return pathlib.Path(tempfile.mkdtemp())


def _dogrula(dizin, veri):
    yol = dizin / "vakia.json"
    yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    hedef = dizin / "sonuc.json"
    kod, out, err = _cli("--dogrula", yol, "--json", hedef)
    assert kod == 0, f"exit sözleşmesi: dogrula içinde sys.exit yok\n{out}\n{err}"
    return out, json.loads(hedef.read_text(encoding="utf-8"))


def _modul():
    spec = importlib.util.spec_from_file_location("_vakia_matris_f", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _olay(olgu, durum, belge="tutanak", destekler=("I1",), **ek):
    o = {"tarih": "2025-01-10", "olgu": olgu, "belge": belge,
         "destekler": list(destekler), "ispat_durumu": durum}
    o.update(ek)
    return o


# ── 4) kapalı beyaz liste yeniden bölündü ───────────────────────────────────

def test_ispat_kumeleri_kapali_beyaz_liste():
    """A-13: tanık ve karine ISPAT_TAM'dan ÇIKAR; ISPAT (tam küme) adı ve
    üyeleri DEĞİŞMEZ (iskelet basımı + geçersiz-etiket denetimi aynı)."""
    m = _modul()
    assert m.ISPAT_TAM == {"belgeli", "ikrar", "yemin", "bilirkisi"}
    assert m.ISPAT_KISMI == {"beyan", "tanik"}
    assert m.ISPAT_YUK_KAYDIRIR == {"karine"}
    assert m.ISPAT == {"belgeli", "beyan", "bilirkisi", "ikrar", "ispatsiz",
                       "karine", "tanik", "yemin"}
    assert m.IDDIA_TUR == {"vakia", "hukuki"}
    assert m.TANIK_CAIZLIK == {"caiz", "sinirli", "caiz_degil", "bilinmiyor"}


def test_iskelet_sablonu_tur_ve_caizlik_tasir():
    """--iskelet: iddia şablonuna `tur`, olay şablonuna `caizlik` eklendi;
    stdout saf JSON kalır; stderr'deki ISPAT satırı (v0.5.14 kilidi)
    değişmez."""
    kod, out, err = _cli("--iskelet")
    assert kod == 0
    sablon = json.loads(out)
    assert set(sablon) == {"taraflar", "iddialar", "olaylar"}
    assert "tur" in sablon["iddialar"][0]
    assert "vakia" in sablon["iddialar"][0]["tur"] and "hukuki" in sablon["iddialar"][0]["tur"]
    assert "caizlik" in sablon["olaylar"][0]
    for c in ("caiz", "sinirli", "caiz_degil", "bilinmiyor"):
        assert c in sablon["olaylar"][0]["caizlik"]
    assert ("ispat_durumu değerleri: belgeli, beyan, bilirkisi, ikrar, "
            "ispatsiz, karine, tanik, yemin") in err
    assert "ISPAT_YUK_KAYDIRIR" in err
    assert "caizlik" in err
    assert "HMK m.266" in err and "HMK m.190" in err and "HMK m.200" in err


# ── 2) tanık şartlı delil ──────────────────────────────────────────────────

def test_tanik_tek_delil_caizlik_yok_ispat_boslugu(izole_dizin):
    """A-13 çekirdek vaka: yalnız tanıkla desteklenen VAKIA iddiası,
    caizlik alanı YOKKEN (→ bilinmiyor, fail-closed) belgeli SAYILMAZ ve
    `ispat_bosluklari`na düşer. Eski kodda bu dosya TAMAM basıyordu."""
    veri = {"iddialar": [{"id": "I1", "metin": "Bedel elden odendi"}],
            "olaylar": [_olay("Tanik Ayse Ornek beyani", "tanik", belge="tanik listesi")]}
    out, sonuc = _dogrula(izole_dizin, veri)
    assert sonuc["ispat_bosluklari"] == ["I1"]
    assert sonuc["saglikli"] is False
    satir = sonuc["iddia_delil_matrisi"][0]
    assert satir["belgeli"] is False
    assert satir["kismi_destek"] is True
    assert satir["tanik_caizlik_belirsiz"] is True
    assert satir["yuk_kaydiran"] is False
    assert satir["tur"] == "vakia"
    assert "tanık caizliği belirsiz" in out
    assert "HMK m.200-203" in out
    assert "EKSİK — yukarıdakiler kapatılmalı <<<" in out
    assert "[BİLGİ]" in out and "caizlik" in out  # varsayılan GÖRÜNÜR


def test_tanik_caiz_tam_ispat_bosluk_yok(izole_dizin):
    """caizlik: caiz → tanık TAM ispat aracı gibi sayılır (dolu belge ile)."""
    veri = {"iddialar": [{"id": "I1", "metin": "Kaza aninda fren yapilmadi", "tur": "vakia"}],
            "olaylar": [_olay("Gorgu tanigi beyani", "tanik", belge="tanik listesi", caizlik="caiz")]}
    out, sonuc = _dogrula(izole_dizin, veri)
    assert sonuc["ispat_bosluklari"] == []
    assert sonuc["saglikli"] is True
    satir = sonuc["iddia_delil_matrisi"][0]
    assert satir["belgeli"] is True
    assert satir["tanik_caizlik_belirsiz"] is False
    assert "tanık caizliği belirsiz" not in out
    assert ">>> Dosya olgu/delil bütünlüğü TAMAM <<<" in out


def test_tanik_sinirli_kismi_destek_bosluk(izole_dizin):
    """caizlik: sinirli → yalnız kısmi destek; iddia boşlukta kalır."""
    veri = {"iddialar": [{"id": "I1", "metin": "Kira bedeli 5 yil odendi"}],
            "olaylar": [_olay("Komsu tanik", "tanik", caizlik="sinirli")]}
    out, sonuc = _dogrula(izole_dizin, veri)
    assert sonuc["ispat_bosluklari"] == ["I1"]
    satir = sonuc["iddia_delil_matrisi"][0]
    assert satir["belgeli"] is False and satir["kismi_destek"] is True
    assert satir["tanik_caizlik_belirsiz"] is True


def test_tanik_caiz_degil_destek_sayilmaz(izole_dizin):
    """caizlik: caiz_degil → ne TAM ne KISMİ; matris satırında görünür ama
    kismi_destek bile False; 'destek sayılmadı' notu basılır."""
    veri = {"iddialar": [{"id": "I1", "metin": "Senede karsi sozlu anlasma"}],
            "olaylar": [_olay("Tanik beyani", "tanik", caizlik="caiz_degil")]}
    out, sonuc = _dogrula(izole_dizin, veri)
    assert sonuc["ispat_bosluklari"] == ["I1"]
    satir = sonuc["iddia_delil_matrisi"][0]
    assert satir["belgeli"] is False
    assert satir["kismi_destek"] is False
    assert satir["tanik_caizlik_belirsiz"] is False
    assert satir["destekler"] == ["Tanik beyani"]
    assert "tanık caiz değil" in out and "destek SAYILMADI" in out


def test_tanik_gecersiz_caizlik_etiketi_bilinmiyor_sayilir(izole_dizin):
    """Kapalı kümede olmayan caizlik etiketi (ör. 'evet') fail-closed →
    bilinmiyor; GÖRÜNÜR uyarı basılır (sessiz atlama yok)."""
    veri = {"iddialar": [{"id": "I1", "metin": "X"}],
            "olaylar": [_olay("Tanik", "tanik", caizlik="evet")]}
    out, sonuc = _dogrula(izole_dizin, veri)
    assert sonuc["ispat_bosluklari"] == ["I1"]
    assert sonuc["iddia_delil_matrisi"][0]["tanik_caizlik_belirsiz"] is True
    assert "'evet'" in out and "bilinmiyor" in out


def test_caizlik_alani_tanik_disi_olayda_etkisiz(izole_dizin):
    """caizlik yalnız `tanik` için anlamlıdır; belgeli olayda 'caiz_degil'
    yazılsa bile belgeli destek bozulmaz (alan yoksayılır)."""
    veri = {"iddialar": [{"id": "I1", "metin": "Sozlesme kuruldu"}],
            "olaylar": [_olay("Sozlesme", "belgeli", belge="yazili sozlesme", caizlik="caiz_degil")]}
    out, sonuc = _dogrula(izole_dizin, veri)
    assert sonuc["ispat_bosluklari"] == []
    assert sonuc["iddia_delil_matrisi"][0]["belgeli"] is True


# ── 1) vakıa iddiası ≠ hukuki iddia ────────────────────────────────────────

def test_hukuki_iddia_delilsiz_bosluk_uretmez(izole_dizin):
    """tur: hukuki → delil aranmaz; ispat boşluğu ÜRETMEZ; satırda tur
    notu + HMK m.266 sınırı basılır; özette hukuki_iddia sayılır."""
    veri = {"iddialar": [
                {"id": "I1", "metin": "Sozlesme kuruldu", "tur": "vakia"},
                {"id": "H1", "metin": "Sozlesme eser sozlesmesidir", "tur": "hukuki"}],
            "olaylar": [_olay("Sozlesme", "belgeli", belge="yazili sozlesme")]}
    out, sonuc = _dogrula(izole_dizin, veri)
    assert sonuc["ispat_bosluklari"] == []
    assert sonuc["saglikli"] is True
    h = [s for s in sonuc["iddia_delil_matrisi"] if s["iddia_id"] == "H1"][0]
    assert h["tur"] == "hukuki"
    assert h["belgeli"] is False
    assert "tur: hukuki — bilirkişi delil değildir (HMK m.266 sınırı" in out
    assert "hâkimlik mesleğinin gerektirdiği hukuki bilgiyle" in out
    assert sonuc["ozet"]["hukuki_iddia"] == 1
    assert sonuc["ozet"]["belgeli_destekli"] == 1   # hukuki iddia belgeli SAYILMAZ
    assert "hukuki iddia: 1" in out


def test_hukuki_iddiada_bilirkisi_destegi_sayilmaz(izole_dizin):
    """Hukuki iddiaya bağlanan `bilirkisi` olayı destek SAYILMAZ; görünür
    uyarı basılır. Yine boşluk üretmez (hukuki iddia sınıfı)."""
    veri = {"iddialar": [{"id": "H1", "metin": "Fiil haksiz fiildir", "tur": "hukuki"}],
            "olaylar": [_olay("Hukukcu bilirkisi raporu", "bilirkisi", belge="rapor", destekler=("H1",))]}
    out, sonuc = _dogrula(izole_dizin, veri)
    assert sonuc["ispat_bosluklari"] == []
    satir = sonuc["iddia_delil_matrisi"][0]
    assert satir["belgeli"] is False
    assert "bilirkişi desteği hukuki iddiada SAYILMAZ" in out


def test_vakia_iddiada_bilirkisi_dolu_belge_ile_tam(izole_dizin):
    """Vakıa iddiasında bilirkişi (dolu belge) TAM ispat aracıdır."""
    veri = {"iddialar": [{"id": "I1", "metin": "Hasar bedeli 100 birim", "tur": "vakia"}],
            "olaylar": [_olay("Teknik bilirkisi raporu", "bilirkisi", belge="rapor")]}
    out, sonuc = _dogrula(izole_dizin, veri)
    assert sonuc["ispat_bosluklari"] == []
    assert sonuc["iddia_delil_matrisi"][0]["belgeli"] is True


def test_tur_alani_yoksa_vakia_varsayilir_bilgi_basilir(izole_dizin):
    veri = {"iddialar": [{"id": "I1", "metin": "Tur alani yok"}],
            "olaylar": [_olay("Sozlesme", "belgeli")]}
    out, sonuc = _dogrula(izole_dizin, veri)
    assert sonuc["iddia_delil_matrisi"][0]["tur"] == "vakia"
    assert "[BİLGİ]" in out and "I1" in out and "'vakia' varsayıldı" in out


def test_gecersiz_tur_etiketi_vakia_sayilir_ve_sagligi_bozar(izole_dizin):
    """Kapalı küme dışı tur (ör. 'karma') fail-closed → vakıa sayılır
    (delil aranan sıkı sınıf) ve BİÇİMSİZ KAYIT bloğunda görünür → saglikli
    False (geçersiz enum = geçersiz ispat_durumu ile aynı ciddiyet)."""
    veri = {"iddialar": [{"id": "I1", "metin": "X", "tur": "karma"}],
            "olaylar": [_olay("Sozlesme", "belgeli")]}
    out, sonuc = _dogrula(izole_dizin, veri)
    assert sonuc["iddia_delil_matrisi"][0]["tur"] == "vakia"
    assert sonuc["saglikli"] is False
    assert "'karma'" in out


# ── 3) karine yük kaydırır ─────────────────────────────────────────────────

def test_karine_yuk_kaydirir_belgeli_sayilmaz(izole_dizin):
    """karine → yuk_kaydiran: true; belgeli SAYILMAZ; HMK m.190/2 notu;
    özette yuk_kaydiran_karine sayılır. Yalnız karineyle desteklenen vakıa
    iddiası boşluktadır (karinenin TEMEL vakıası ayrıca ispatlanmalı)."""
    veri = {"iddialar": [{"id": "I1", "metin": "Borc odenmedi"}],
            "olaylar": [_olay("Kanuni karine", "karine", belge="")]}
    out, sonuc = _dogrula(izole_dizin, veri)
    assert sonuc["ispat_bosluklari"] == ["I1"]
    satir = sonuc["iddia_delil_matrisi"][0]
    assert satir["yuk_kaydiran"] is True
    assert satir["belgeli"] is False
    assert "karine ispat etmez, ispat yükünü kaydırır (HMK m.190/2" in out
    assert sonuc["ozet"]["yuk_kaydiran_karine"] == 1
    assert "yük kaydıran karine: 1" in out


def test_karine_ve_belgeli_birlikte_bosluk_yok_yuk_kaydiran_true(izole_dizin):
    veri = {"iddialar": [{"id": "I1", "metin": "Borc odenmedi"}],
            "olaylar": [_olay("Kanuni karine", "karine", belge=""),
                        _olay("Ihtarname", "belgeli", belge="ihtarname")]}
    out, sonuc = _dogrula(izole_dizin, veri)
    assert sonuc["ispat_bosluklari"] == []
    satir = sonuc["iddia_delil_matrisi"][0]
    assert satir["yuk_kaydiran"] is True and satir["belgeli"] is True


# ── 5) JSON şeması / geriye uyum ────────────────────────────────────────────

def test_json_semasi_genisledi_ust_duzey_degismedi(izole_dizin):
    veri = {"iddialar": [{"id": "I1", "metin": "Sozlesme kuruldu"}],
            "olaylar": [_olay("Sozlesme", "belgeli", belge="yazili sozlesme")]}
    out, sonuc = _dogrula(izole_dizin, veri)
    assert set(sonuc) == UST_DUZEY_ANAHTARLAR
    assert set(sonuc["iddia_delil_matrisi"][0]) == SATIR_ANAHTARLAR
    assert set(sonuc["ozet"]) == OZET_ANAHTARLAR
    assert sonuc["ozet"] == {"iddia": 1, "belgeli_destekli": 1, "ispat_boslugu": 0,
                             "olay": 1, "tarihsiz": 0, "yetim": 0,
                             "hukuki_iddia": 0, "yuk_kaydiran_karine": 0}


def test_eski_json_yeni_alanlar_yok_cokmeden_calisir(izole_dizin):
    """Geriye uyum: v0.5.14 biçimli girdi (tur/caizlik yok) traceback
    vermeden koşar; eski TAM etiketli (belgeli/ikrar/yemin) dosya yine
    TAMAM; yalnız tanık/karine dayanaklı iddialar A-13 gereği kırmızıya
    döner (istenen etki)."""
    eski = {"iddialar": [{"id": "I1", "metin": "A"}, {"id": "I2", "metin": "B"},
                         {"id": "I3", "metin": "C"}],
            "olaylar": [
                {"tarih": "2025-01-01", "olgu": "Sozlesme", "belge": "sozlesme",
                 "destekler": ["I1"], "ispat_durumu": "belgeli"},
                {"tarih": "2025-01-02", "olgu": "Ikrar", "belge": "cevap dilekcesi",
                 "destekler": ["I2"], "ispat_durumu": "ikrar"},
                {"tarih": "2025-01-03", "olgu": "Tanik", "belge": "tanik listesi",
                 "destekler": ["I3"], "ispat_durumu": "tanik"}]}
    yol = izole_dizin / "eski.json"
    yol.write_text(json.dumps(eski), encoding="utf-8")
    hedef = izole_dizin / "sonuc.json"
    kod, out, err = _cli("--dogrula", yol, "--json", hedef)
    assert kod == 0 and "Traceback" not in err
    sonuc = json.loads(hedef.read_text(encoding="utf-8"))
    assert sonuc["ispat_bosluklari"] == ["I3"]
    assert sonuc["ozet"]["belgeli_destekli"] == 2
    assert all(s["tur"] == "vakia" for s in sonuc["iddia_delil_matrisi"])


def test_eski_json_bos_sozluk_ve_bicimsiz_kayit_hala_cokmez(izole_dizin):
    for veri in ({}, {"iddialar": ["dize"], "olaylar": [None]}):
        yol = izole_dizin / "v.json"
        yol.write_text(json.dumps(veri), encoding="utf-8")
        kod, out, err = _cli("--dogrula", yol)
        assert kod == 0 and "Traceback" not in err


def test_tum_siniflar_bir_arada_ozet_tutarli(izole_dizin):
    """iddia = belgeli_destekli + ispat_boslugu + hukuki_iddia (bölümleme)."""
    veri = {"iddialar": [
                {"id": "I1", "metin": "belgeli", "tur": "vakia"},
                {"id": "I2", "metin": "tanik belirsiz"},
                {"id": "I3", "metin": "karine"},
                {"id": "H1", "metin": "hukuki", "tur": "hukuki"}],
            "olaylar": [
                _olay("Sozlesme", "belgeli", destekler=("I1",)),
                _olay("Tanik", "tanik", destekler=("I2",)),
                _olay("Karine", "karine", belge="", destekler=("I3",)),
                _olay("Karine2", "karine", belge="", destekler=("I1",))]}
    out, sonuc = _dogrula(izole_dizin, veri)
    oz = sonuc["ozet"]
    assert oz["iddia"] == 4
    assert oz["belgeli_destekli"] + oz["ispat_boslugu"] + oz["hukuki_iddia"] == 4
    assert oz["hukuki_iddia"] == 1 and oz["ispat_boslugu"] == 2
    assert oz["yuk_kaydiran_karine"] == 2  # yük kaydıran karine OLAYI sayısı
    assert sonuc["ispat_bosluklari"] == ["I2", "I3"]


# ── SKILL.md — İSPAT ONTOLOJİSİ bölümü + teyit damgası ─────────────────────

def test_skill_md_ispat_ontolojisi_bolumu():
    txt = SKILL_MD.read_text(encoding="utf-8")
    assert "İSPAT ONTOLOJİSİ" in txt
    for norm in ("HMK m.190", "HMK m.200", "m.201", "m.202", "m.203", "HMK m.266"):
        assert norm in txt, norm
    assert "Mevzuat MCP teyit 2026-09-06" in txt
    for anahtar in ("tur", "caizlik", "yuk_kaydiran", "tanik_caizlik_belirsiz",
                    "hukuki_iddia", "yuk_kaydiran_karine", "ispat_bosluklari"):
        assert anahtar in txt, anahtar
    # eski yanlış öğreti kaldırıldı: tanık/karine artık TAM listede anılmaz
    assert "`belgeli · tanik · bilirkisi · karine · ikrar · yemin`" not in txt

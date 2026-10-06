# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — oa-usul [G10] AYM / [G11] AİHM bireysel başvuru yolu kontrol listesi.

NEDEN (yetenek denetimi, 2026-10-03/05): OA'da AYM yolu kısmen (yalnız süre
kuralı ve dilekçe tipi), AİHM yolu HİÇ yoktu; Yargı PRO 5-1/5-3/5-4/5-5 ve
6-1…6-5 skill'lerinin fikri (eşik → ölçüt → giderim) OA yöntemiyle kuruldu:
model değerlendirir, `usul_matris.py` değerlendirmenin EKSİKSİZ ve KANITLI
olduğunu denetler; hukuki sonuç avukatındır.

Dayanaklar resmî metinden teyit edildi (Yargı PRO, 2026-10-05): 6216 m.45-50,
geçici m.1/8; AYM İçtüzüğü m.59/63/66; HMK m.375/377; CMK m.311; İYUK m.53;
AİHS m.35/1 (Orhan/Türkiye (k.k.), no. 38358/22, § 44 — 01.02.2022 geçişi).
Bu dosyadaki bütün dosya/kişi verileri KURGUDUR (anayasa m.7).
"""
import copy
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
USUL = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-usul"
SCRIPT = USUL / "scripts" / "usul_matris.py"

spec = importlib.util.spec_from_file_location("v0518_usul_um", SCRIPT)
um = importlib.util.module_from_spec(spec)
spec.loader.exec_module(um)


def _calistir(*args, cwd=None):
    return subprocess.run([sys.executable, str(SCRIPT)] + [str(a) for a in args],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", cwd=str(cwd) if cwd else None)


def _cli(*args, cwd=None):
    cp = _calistir(*args, cwd=cwd)
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _bb():
    return copy.deepcopy(um.ORNEK_BB)


def _denetle(v):
    bulgular, bosluklar = um.denetle(v)
    return "\n".join(bulgular), bosluklar


# ── şablon ve geriye uyum ───────────────────────────────────────────────────

def test_ornek_bb_kendi_denetiminden_temiz_gecer(tmp_path):
    cp = _calistir("--ornek-bb")
    assert cp.returncode == 0, cp.stdout + cp.stderr
    yol = tmp_path / "bb.json"
    yol.write_text(cp.stdout, encoding="utf-8")   # yalnız stdout: JSON'a uyarı karışmasın
    kod, rapor = _cli("--girdi", yol)
    assert kod == 0, rapor
    assert "[G10]" in rapor and "[G11]" in rapor and "Boşluk yok" in rapor


def test_eski_ornek_degismedi_ve_bireysel_basvuru_tasimaz():
    assert "bireysel_basvuru" not in um.ORNEK
    assert len(um.ORNEK["islemler"]) == 3


def test_alan_yoksa_G10_G11_satiri_basilmaz():
    bulgular, bosluklar = _denetle(copy.deepcopy(um.ORNEK))
    assert "[G10]" not in bulgular and "[G11]" not in bulgular and not bosluklar


# ── [G10] AYM ölçütleri ─────────────────────────────────────────────────────

def test_degerlendirilmemis_olcut_bosluktur():
    v = _bb()
    del v["bireysel_basvuru"][0]["kriterler"]["zaman_bakimindan"]
    _, bosluklar = _denetle(v)
    assert any("zaman_bakimindan" in b and "DEĞERLENDİRİLMEMİŞ" in b
               and "geçici m.1/8" in b for b in bosluklar), bosluklar


def test_kanitsiz_tamam_bosluktur():
    v = _bb()
    v["bireysel_basvuru"][0]["kriterler"]["kisi_bakimindan"] = {"durum": "tamam", "kanit": ""}
    _, bosluklar = _denetle(v)
    assert any("kisi_bakimindan" in b and "kanıtsız" in b for b in bosluklar)


def test_eksik_durum_bosluktur():
    v = _bb()
    v["bireysel_basvuru"][0]["kriterler"]["yollarin_tuketilmesi"] = {
        "durum": "eksik", "not": "temyiz dilekçesi dosyada yok"}
    _, bosluklar = _denetle(v)
    assert any("yollarin_tuketilmesi" in b and "EKSİK" in b and "6216 m.45/2" in b
               for b in bosluklar)


def test_supheli_gerekceliyse_avukat_karari_bulgusu_bosluk_degil():
    bulgular, bosluklar = _denetle(_bb())
    assert not bosluklar
    assert "ŞÜPHELİ" in bulgular and "AVUKAT KARARI" in bulgular


@pytest.mark.parametrize("durum", ["supheli", "karsilanmiyor"])
def test_supheli_karsilanmiyor_gerekcesiz_bosluktur(durum):
    v = _bb()
    v["bireysel_basvuru"][0]["kriterler"]["acik_dayanaktan_yoksunluk"] = {"durum": durum}
    _, bosluklar = _denetle(v)
    assert any("gerekçe" in b and "acik_dayanaktan_yoksunluk" in b for b in bosluklar)


def test_karsilanmiyor_kabul_edilemezlik_riski_olarak_gorunur_ama_yasaklamaz():
    v = _bb()
    v["bireysel_basvuru"][0]["kriterler"]["yollarin_tuketilmesi"] = {
        "durum": "karsilanmiyor", "not": "istinaf yoluna gidilmemiş"}
    bulgular, bosluklar = _denetle(v)
    assert "KABUL EDİLEMEZLİK RİSKİ" in bulgular
    # avukat kararı kayda geçmeden boşluk kapanmaz (G3 simetrisi)
    assert any("avukat_karari" in b and "yollarin_tuketilmesi" in b for b in bosluklar)
    for karar in ("devam", "vazgec"):
        v["bireysel_basvuru"][0]["kriterler"]["yollarin_tuketilmesi"]["avukat_karari"] = karar
        bulgular, bosluklar = _denetle(v)
        assert not bosluklar and f"avukat kararı → {karar}" in bulgular


def test_temel_olcut_uygulanmaz_olamaz():
    v = _bb()
    v["bireysel_basvuru"][0]["kriterler"]["konu_bakimindan"] = {"durum": "uygulanmaz"}
    _, bosluklar = _denetle(v)
    assert any("konu_bakimindan" in b and "OLAMAZ" in b for b in bosluklar)


@pytest.mark.parametrize("anahtar,dayanak", [
    ("anayasal_onem_onemli_zarar", "6216 m.48/2"),
    ("acik_dayanaktan_yoksunluk", "6216 m.48/2, m.49/6"),
    ("kotuye_kullanmama", "6216 m.51"),
])
def test_aym_m48_iki_esigi_ve_m51_ayri_olcuttur(anahtar, dayanak):
    v = _bb()
    del v["bireysel_basvuru"][0]["kriterler"][anahtar]
    _, bosluklar = _denetle(v)
    assert any(anahtar in b and "DEĞERLENDİRİLMEMİŞ" in b and dayanak in b
               for b in bosluklar), bosluklar


# ── [G10] İçtüzük m.59 form ve zorunlu ekler ────────────────────────────────

def test_form_kalemi_degerlendirilmemisse_bosluk():
    v = _bb()
    del v["bireysel_basvuru"][0]["form"]["59/3-b"]
    _, bosluklar = _denetle(v)
    assert any("59/3-b" in b and "harcın ödendiğine" in b for b in bosluklar)


def test_form_eksik_kalemi_bosluk_kosullu_kalem_uygulanmaz_olabilir():
    v = _bb()
    form = v["bireysel_basvuru"][0]["form"]
    form["59/2-k"] = "eksik"          # imza
    form["59/2-b"] = "uygulanmaz"     # tüzel kişi değil — koşullu
    _, bosluklar = _denetle(v)
    assert any("59/2-k" in b and "EKSİK" in b for b in bosluklar)
    assert not any("59/2-b" in b for b in bosluklar)


def test_zorunlu_form_kalemi_uygulanmaz_olamaz():
    v = _bb()
    v["bireysel_basvuru"][0]["form"]["59/2-h"] = "uygulanmaz"   # talepler
    _, bosluklar = _denetle(v)
    assert any("59/2-h" in b and "OLAMAZ" in b for b in bosluklar)


def test_harc_belgesi_yalniz_adli_yardimda_uygulanmaz_olabilir():
    v = _bb()
    form = v["bireysel_basvuru"][0]["form"]
    form["59/3-b"] = "uygulanmaz"
    _, bosluklar = _denetle(v)
    assert any("59/3-b" in b and "OLAMAZ" in b and "adli yardım" in b for b in bosluklar)
    form["59/3-h"] = "tamam"                       # adli yardım talebi + mali belgeler
    _, bosluklar = _denetle(v)
    assert not bosluklar


def test_basvuru_yolu_ongorulmemisse_tuketme_kalemleri_uygulanmaz_olabilir():
    v = _bb()
    form = v["bireysel_basvuru"][0]["form"]
    form["59/2-f"] = form["59/3-g"] = "uygulanmaz"
    _, bosluklar = _denetle(v)
    assert any("59/2-f" in b and "OLAMAZ" in b for b in bosluklar)
    assert any("59/3-g" in b and "OLAMAZ" in b for b in bosluklar)
    v["bireysel_basvuru"][0]["basvuru_yolu_ongorulmemis"] = True
    _, bosluklar = _denetle(v)
    assert not bosluklar


def test_sunulamayan_ek_icin_m59_4_hatirlatilir():
    v = _bb()
    v["bireysel_basvuru"][0]["form"]["59/3-d"] = "supheli"
    bulgular, _ = _denetle(v)
    assert "59/3-d" in bulgular and "m.59/4" in bulgular


def test_form_listesi_icuzuk_m59_kalemlerinin_tamamini_tasir():
    anahtarlar = [k for k, _o, _u in um.AYM_FORM]
    for harf in ("a", "b", "c", "ç", "d", "e", "f", "g", "ğ", "h", "ı", "i", "j", "k", "l"):
        assert f"59/2-{harf}" in anahtarlar, harf
    for harf in ("a", "b", "c", "ç", "d", "e", "f", "g", "ğ", "h"):
        assert f"59/3-{harf}" in anahtarlar, harf
    assert "60/2" in anahtarlar


# ── süre bağı (hesap oa-sure'nin) ───────────────────────────────────────────

def test_son_gun_yoksa_bosluk():
    v = _bb()
    del v["bireysel_basvuru"][0]["sure"]["son_gun"]
    _, bosluklar = _denetle(v)
    assert any("son_gun YOK" in b for b in bosluklar)


def test_baslangic_kanitsiz_ise_bosluk():
    v = _bb()
    v["bireysel_basvuru"][0]["sure"]["baslangic_kaniti"] = ""
    _, bosluklar = _denetle(v)
    assert any("baslangic_kaniti" in b for b in bosluklar)


def test_kural_oneki_yolu_yalanliyorsa_bosluk():
    v = _bb()
    v["bireysel_basvuru"][0]["sure"]["kural"] = "hmk_istinaf"
    _, bosluklar = _denetle(v)
    assert any("birbirini yalanlıyor" in b for b in bosluklar)


def test_suresi_gecmis_basvuru_bulgu_ve_mazeret_yolu_avukat_karari():
    v = _bb()
    sure = v["bireysel_basvuru"][0]["sure"]
    sure["basvuru_tarihi"] = "2026-10-05"   # son gün 2026-10-01
    bulgular, bosluklar = _denetle(v)
    assert "SÜRE GEÇMİŞ (+4 gün)" in bulgular and "m.47/5" in bulgular
    assert any("avukat_karari" in b for b in bosluklar)          # karar kaydı zorunlu
    sure["avukat_karari"] = "devam"
    _, bosluklar = _denetle(v)
    assert any("mazeret_kaniti" in b for b in bosluklar)         # 6216 m.47/5 belge ister
    sure["mazeret_kaniti"] = "hastane raporu (kurgu)"
    bulgular, bosluklar = _denetle(v)
    assert not bosluklar and "avukat kararı → devam" in bulgular
    del sure["mazeret_kaniti"]
    sure["avukat_karari"] = "vazgec"
    _, bosluklar = _denetle(v)
    assert not bosluklar


# ── [G11] AİHM ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("nihai", ["2022-01-31", "2022-02-01", "2026-08-20"])
def test_aihm_suresi_her_zaman_dort_ay(nihai):
    """R7 (avukat kararı 2026-10-06): AİHM başvuru süresi dört aydır; 1.2.2022 öncesi
    altı ay geçişi kapsam dışıdır. oa-sure ile aynı: iki modül de yalnız dört ay der."""
    v = _bb()
    v["bireysel_basvuru"][1]["sure"]["nihai_karar_tarihi"] = nihai
    bulgular, _ = _denetle(v)
    assert "süresi 4 ay" in bulgular
    assert "6 ay" not in bulgular


def test_aihm_nihai_karar_tarihi_yoksa_bosluk():
    v = _bb()
    del v["bireysel_basvuru"][1]["sure"]["nihai_karar_tarihi"]
    _, bosluklar = _denetle(v)
    assert any("nihai_karar_tarihi" in b for b in bosluklar)


def test_aihm_olcutleri_degerlendirilmemisse_bosluk():
    v = _bb()
    v["bireysel_basvuru"][1]["kriterler"] = {}
    _, bosluklar = _denetle(v)
    for anahtar in ("magdur_sifati", "yollarin_tuketilmesi", "onemli_zarar",
                    "eksiksiz_basvuru", "ayni_konu_baska_merci", "kotuye_kullanmama"):
        assert any(anahtar in b for b in bosluklar), anahtar
    assert any("AİHS m.34" in b for b in bosluklar)
    assert any("AİHS m.35/2-b" in b for b in bosluklar)
    assert any("kotuye_kullanmama" in b and "AİHS m.35/3-a" in b for b in bosluklar)
    assert any("TEYİT BEKLİYOR" in b for b in bosluklar)   # İçtüzük m.47 etiketi


# ── karar sonrası ───────────────────────────────────────────────────────────

def test_aym_ihlalinde_hmk_375_dayanagi_yanlis_bosluk():
    v = _bb()
    v["bireysel_basvuru"][0]["karar_sonrasi"] = {
        "karar_turu": "ihlal", "ihlal_kaynagi": "mahkeme_karari", "dayanak": "HMK m.375/1-i"}
    bulgular, bosluklar = _denetle(v)
    assert "6216 m.50/2" in bulgular
    assert any("YANLIŞ" in b and "AİHM kararına özgüdür" in b for b in bosluklar)


def test_aym_ihlalinde_dogru_dayanak_bosluksuz():
    v = _bb()
    v["bireysel_basvuru"][0]["karar_sonrasi"] = {
        "karar_turu": "ihlal", "ihlal_kaynagi": "mahkeme_karari", "dayanak": "6216 m.50/2"}
    _, bosluklar = _denetle(v)
    assert not bosluklar


def test_aym_ihlal_kararinda_ihlal_kaynagi_zorunlu():
    v = _bb()
    v["bireysel_basvuru"][0]["karar_sonrasi"] = {"karar_turu": "ihlal"}
    _, bosluklar = _denetle(v)
    assert any("ihlal_kaynagi" in b and "m.50/2" in b and "m.50/1" in b for b in bosluklar)
    v["bireysel_basvuru"][0]["karar_sonrasi"]["ihlal_kaynagi"] = "diger"
    bulgular, bosluklar = _denetle(v)
    assert not bosluklar and "6216 m.50/1" in bulgular


def test_aihm_ozgu_dayanak_deseni_rakam_sinirli():
    assert um._AIHM_OZGU_DAYANAK_RE.search("HMK m.353/1") is None
    assert um._AIHM_OZGU_DAYANAK_RE.search("İYUK m.53/1-ı") is not None
    assert um._AIHM_OZGU_DAYANAK_RE.search("CMK m.311/1-f") is not None


@pytest.mark.parametrize("tur", ["kabul_edilemezlik", "ihlal_yok", "kismi"])
def test_aym_ret_kararinda_aihm_degerlendirmesi_zorunlu(tur):
    v = _bb()
    # «kismi» bir ihlal içerir → ihlal kaynağı da yazılır (bu test AİHM kolunu sınar)
    v["bireysel_basvuru"][0]["karar_sonrasi"] = {"karar_turu": tur, "ihlal_kaynagi": "diger"}
    _, bosluklar = _denetle(v)
    assert any("dosya bitti" in b for b in bosluklar)
    v["bireysel_basvuru"][0]["karar_sonrasi"]["aihm_degerlendirmesi"] = (
        "AİHS m.6 şikâyeti için 4 ay içinde başvuru — avukat kararı")
    _, bosluklar = _denetle(v)
    assert not bosluklar


@pytest.mark.parametrize("kol,dayanak", [
    ("hmk", "HMK m.375/1-i + m.377/1-e"), ("cmk", "CMK m.311/1-f"),
    ("iyuk", "İYUK m.53/1-ı + m.53/3")])
def test_aihm_ihlalinde_yeniden_yargilama_kola_gore(kol, dayanak):
    v = _bb()
    ks = v["bireysel_basvuru"][1]["karar_sonrasi"]
    ks["inis_kolu"] = kol
    bulgular, bosluklar = _denetle(v)
    assert dayanak in bulgular and not bosluklar


def test_aihm_hmk_yolunda_on_yil_siniri_iptali_aninir():
    v = _bb()
    v["bireysel_basvuru"][1]["karar_sonrasi"]["inis_kolu"] = "hmk"
    bulgular, _ = _denetle(v)
    assert "E.2022/7" in bulgular and "üç ay" in bulgular


def test_aihm_ihlalinde_inis_kolu_ve_sure_zorunlu():
    v = _bb()
    v["bireysel_basvuru"][1]["karar_sonrasi"] = {"karar_turu": "dostane_cozum"}
    _, bosluklar = _denetle(v)
    assert any("inis_kolu" in b for b in bosluklar)
    v["bireysel_basvuru"][1]["karar_sonrasi"] = {"karar_turu": "ihlal", "inis_kolu": "cmk"}
    _, bosluklar = _denetle(v)
    assert any("süresi hesaplanmamış" in b for b in bosluklar)


def test_aihm_ihlal_yok_kararinda_yeniden_yargilama_aranmaz():
    v = _bb()
    v["bireysel_basvuru"][1]["karar_sonrasi"] = {"karar_turu": "ihlal_yok"}
    bulgular, bosluklar = _denetle(v)
    assert "yeniden yargılama bendi aranmaz" in bulgular and not bosluklar


def test_json_ciktisi_G10_bosluklarini_tasir(tmp_path):
    v = _bb()
    del v["bireysel_basvuru"][0]["kriterler"]["konu_bakimindan"]
    girdi = tmp_path / "g.json"
    girdi.write_text(json.dumps(v, ensure_ascii=False), encoding="utf-8")
    cikti = tmp_path / "s.json"
    kod, out = _cli("--girdi", girdi, "--json", cikti)
    assert kod == 1, out
    sonuc = json.loads(cikti.read_text(encoding="utf-8"))
    assert sonuc["saglikli"] is False
    assert any("[G10]" in b and "konu_bakimindan" in b for b in sonuc["bosluklar"])


# ── sağlamlık: bozuk girdi çökme değil BOŞLUK üretir ────────────────────────

@pytest.mark.parametrize("bozuk", [
    {"bireysel_basvuru": {"yol": "aym"}},                    # liste değil
    {"bireysel_basvuru": ["metin"]},                         # öğe sözlük değil
    {"bireysel_basvuru": [{"id": "X", "yol": "uzay"}]},      # geçersiz yol
])
def test_bozuk_ust_yapi_bosluk_uretir_cokmez(bozuk):
    _, bosluklar = _denetle(bozuk)
    assert any("[G10/G11]" in b for b in bosluklar), bosluklar


def test_bozuk_tipli_alanlar_cokmez_bosluk_uretir():
    v = _bb()
    aym, aihm = v["bireysel_basvuru"]
    aym["kriterler"] = ["konu_bakimindan"]
    aym["form"] = "tamam"
    aym["sure"]["son_gun"] = 20261001
    aym["karar_sonrasi"] = {"karar_turu": ["ihlal"]}
    aihm["sure"]["nihai_karar_tarihi"] = 2022
    aihm["karar_sonrasi"] = ["ihlal"]
    _, bosluklar = _denetle(v)
    metin = "\n".join(bosluklar)
    for parca in ("'kriterler' sözlük olmalı", "'form' sözlük olmalı",
                  "son_gun ISO tarih değil", "karar_turu geçersiz",
                  "nihai_karar_tarihi ISO tarih değil", "'karar_sonrasi' sözlük olmalı"):
        assert parca in metin, parca


# ── [G9] önek→kol tablosu oa-sure'den (ikiz liste yok) ──────────────────────

SURE_HESAP = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-sure" / "scripts" / "hesapla_sure.py"


def _g9(sure_kurali, yargi_kolu):
    i = {"id": "I1", "taraf": "karsi", "islem": "itiraz", "sure_kurali": sure_kurali,
         "yargi_kolu": yargi_kolu, "kesin_dil": False}
    bulgular, bosluklar = [], []
    um._g9_denetle(i, "I1", None, bulgular, bosluklar)
    return "\n".join(bulgular), bosluklar


def test_g9_tablosu_oa_sure_kaynagindan_okunur():
    """Tablo oa-sure'nin KENDİ tanımına eşittir (değerler testte kopyalanmaz)."""
    import ast as _ast
    agac = _ast.parse(SURE_HESAP.read_text(encoding="utf-8"))
    kaynak = {}
    for d in agac.body:
        if isinstance(d, _ast.Assign) and isinstance(d.targets[0], _ast.Name) and \
                d.targets[0].id == "KURAL_KOLU":
            kaynak = _ast.literal_eval(d.value)
    assert kaynak, "oa-sure KURAL_KOLU bulunamadı"
    assert um.KURAL_ONEK_KOL == {k: (None if v is None else {v}) for k, v in kaynak.items()}
    # A'nın raporundaki iki yeni sınıf artık TANINIR (bilinmiyor değil)
    assert "iik" in um.KURAL_ONEK_KOL and "aihm" in um.KURAL_ONEK_KOL


def test_g9_icra_kolu_ve_aihm_oneki_taninir():
    kol = um.KURAL_ONEK_KOL["iik"]
    beyan = next(iter(kol))                       # oa-sure'nin iik kolu (bugün «icra»)
    bulgular, bosluklar = _g9("iik_sikayet", beyan)
    assert not bosluklar and "tutarlı" in bulgular and "bilinmiyor" not in bulgular
    assert um._kol_normalize("icra")[0] == "icra"
    for k in ("hukuk", "ceza", "idari", "icra"):  # AİHM kol-bağımsız
        bulgular, bosluklar = _g9("aihm_basvuru", k)
        assert not bosluklar and "bilinmiyor" not in bulgular, k


def test_g9_kurala_ozgu_ek_izin_oa_sureden():
    for kural, kollar in um.KURAL_EK_IZIN.items():
        for k in kollar:
            _b, bosluklar = _g9(kural, k)
            assert not bosluklar, (kural, k)


def test_g9_kaynak_okunamazsa_tablo_bos_ve_gorunur_bilinmiyor(tmp_path):
    assert um._oa_sure_kol_kaynagi(str(tmp_path / "yok.py")) == ({}, {})
    eski, eski_ek = um.KURAL_ONEK_KOL, um.KURAL_EK_IZIN
    try:
        um.KURAL_ONEK_KOL, um.KURAL_EK_IZIN = {}, {}
        bulgular, bosluklar = _g9("hmk_istinaf", "hukuk")
        assert not bosluklar and "tablosu okunamadı" in bulgular
    finally:
        um.KURAL_ONEK_KOL, um.KURAL_EK_IZIN = eski, eski_ek


def test_bb_sure_kurali_katalogda_yoksa_bulgu_adaylarla():
    v = _bb()
    v["bireysel_basvuru"][1]["sure"]["kural"] = "aihm_uydurma_kural"
    bulgular, bosluklar = _denetle(v)
    assert "oa-sure kataloğunda yok" in bulgular and "aihm_basvuru" in bulgular
    assert not bosluklar                          # önek doğru → yalnız görünür bulgu
    katalog = um._sure_kural_katalogu()
    assert katalog and {"aym_bireysel", "aihm_basvuru"} <= katalog


# ── belgeler ────────────────────────────────────────────────────────────────

def test_referans_dogrulanmis_dayanaklari_ve_teyit_bekleyenleri_tasir():
    ref = (USUL / "references" / "bireysel-basvuru-yolu.md").read_text(encoding="utf-8")
    for parca in ("6216 m.47/5", "İçtüzük", "m.59", "m.66", "Orhan/Türkiye", "38358/22",
                  "6216 m.50/2", "HMK m.375/1-i", "CMK m.311/1-f", "İYUK m.53/1-ı",
                  "E.2022/7", "aihm_ictihat_ara", "ictihat_getir", "CMK m.141-142",
                  "TEYİT BEKLİYOR", "6216 m.51", "AİHS m.35/2-b", "m.59/4", "m.62/2",
                  "avukat_karari", "ihlal_kaynagi", "basvuru_yolu_ongorulmemis"):
        assert parca in ref, parca


def test_skill_ve_cetvel_yeni_listeye_bagli():
    skill = (USUL / "SKILL.md").read_text(encoding="utf-8")
    cetvel = (USUL / "references" / "usul-cetveli.md").read_text(encoding="utf-8")
    gunluk = (USUL / "references" / "degisiklik-gunlugu.md").read_text(encoding="utf-8")
    assert "[G10]" in skill and "[G11]" in skill and "bireysel-basvuru-yolu.md" in skill
    assert "bireysel-basvuru-yolu.md" in cetvel and "en çok 15 gün" in cetvel
    assert "v0.5.18 (aday)" in gunluk

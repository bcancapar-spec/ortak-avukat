# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — ATIF KAPISI: kapsam (Y-09), derinlik (B-21/B-03), dava geçmişi
(B-17) ve AİHM künyesinin Türkçe yazımı.

SAHA KANITI (derlem testi + yetenek denetimi, 2026-10-03; ayrıntı derlem bulgular
kaydındadır — burada gerçek dosya/kişi YOK):
- Y-09: `kunye_teyit.py` «Anayasa m.36», «Anayasa'nın 36. maddesi», «Av.K. m.36»
  ve ek/geçici madde atıflarını kendi regex'iyle HİÇ çıkarmıyordu; derlem
  taslaklarında 29 Anayasa atfı denetimsiz teslim edilmişti. İMK/TK/HUAK/KMK
  numara eşlemesinde yoktu (kütükte «7201 sayılı Tebligat Kanunu m.21» teyidi
  varken taslaktaki «TK m.21» TEYİTSİZ kalıyordu).
- B-03/B-21: kapı, bir kanun maddesini ya da bir BAM kararını yalnız BAŞKA bir
  kararın dökümünde/kaydında anıldığı için «TEYİTLİ» sayıyordu (iz ≠ teyit);
  kütüğün yazdığı DOKUM-SINIFI derinlik izini okumuyordu.
- B-17: kanun yolu dilekçesinin başlığındaki DAVANIN KENDİ GEÇMİŞİ (istinaf/
  temyiz edilen karar, ilk derece kararı — HMK m.342/2-c'nin ZORUNLU kıldığı
  bilgi) iki kapıda da teslim engeli üretiyordu.
- AİHM yolu: Türkçe yazılmış doğru AİHM künyesi («no. 12345/18») EKSİK KÜNYE
  engeline düşüyordu.

Kanun numaraları ve resmî adlar Yargı PRO `mevzuat_ara` ile mevzuat.gov.tr'den
teyit edildi (2026-10-05). Tüm veriler KURGUDUR (anayasa m.7).
"""
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol" / "scripts"
KT_YOL = SCRIPTS / "kunye_teyit.py"
IMD_YOL = SCRIPTS / "ictihat_muhakeme_denetim.py"
KO_YOL = SCRIPTS / "kunye_ortak.py"


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kt = _yukle("v0518_atif_kt", KT_YOL)
ko = _yukle("v0518_atif_ko", KO_YOL)

KUTUK_BASLIK = ("# Künye Teyit Kütüğü\n| Zaman | Araç | Sorgu | Sonuç | Döküm |\n"
                "|---|---|---|---|---|\n")


def _cli(script, args, cwd):
    cp = subprocess.run([sys.executable, str(script)] + [str(a) for a in args],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(cwd))
    return cp.returncode, (cp.stdout or "") + (cp.stderr or "")


def _iskele(kok, taslak, kutuk_satirlari=(), dokumler=None, dosya_md=None):
    teyit = kok / "_oa" / "teyit"
    (teyit / "dokum").mkdir(parents=True, exist_ok=True)
    (kok / "_oa" / "cikti").mkdir(parents=True, exist_ok=True)
    (teyit / "kunye-teyit.md").write_text(
        KUTUK_BASLIK + "".join(s + "\n" for s in kutuk_satirlari), encoding="utf-8")
    for ad, icerik in (dokumler or {}).items():
        (teyit / "dokum" / ad).write_text(icerik, encoding="utf-8")
    if dosya_md is not None:
        (kok / "_oa" / "dosya.md").write_text(dosya_md, encoding="utf-8")
    (kok / "taslak.md").write_text(taslak, encoding="utf-8")


def _mevzuat(metin):
    return kt.mevzuat_cikar(metin)


# ── Y-09: kapsam ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("metin", [
    "Anayasa m.36 uyarınca",
    "Anayasa'nın 36. maddesi güvence altına alır",
    "Anayasa’nın 36’ncı maddesi",
    "Türkiye Cumhuriyeti Anayasası'nın 36 ncı maddesi",
    "Anayasa md. 36",
])
def test_anayasa_atfi_artik_cikarilir_ve_2709a_baglanir(metin):
    atiflar = _mevzuat(metin)
    assert len(atiflar) == 1, metin
    assert "2709" in atiflar[0].kanun_anahtar and atiflar[0].madde == "36"


@pytest.mark.parametrize("metin", [
    "Anayasa Mahkemesi 2022/7 E. sayılı kararında",
    "Anayasa Mahkemesinin 36 sayfalık kararı",
    "Anayasaya aykırılık iddiası 36. madde",
    "Anayasal düzen bakımından",
])
def test_anayasa_mahkemesi_ve_turevler_mevzuat_atfi_sayilmaz(metin):
    assert not [a for a in _mevzuat(metin) if "2709" in a.kanun_anahtar], metin


@pytest.mark.parametrize("metin", [
    "Av.K. m.36 sır saklama", "Av. K. m.36", "AvK m.36",
    "Avukatlık Kanunu m.36", "1136 sayılı Avukatlık Kanunu'nun 36. maddesi",
])
def test_avukatlik_kanunu_yazimlari_1136(metin):
    atiflar = _mevzuat(metin)
    assert len(atiflar) == 1 and "1136" in atiflar[0].kanun_anahtar, metin


@pytest.mark.parametrize("metin,no", [
    ("TK m.21", "7201"), ("TK 32", "7201"), ("HUAK'ın 18. maddesi", "6325"),
    ("KMK m.18", "634"), ("İMK m.3", "7036"), ("Tebligat Kanunu'nun 21. maddesi", "7201"),
    ("Kat Mülkiyeti Kanunu m.18", "634"), ("İş Mahkemeleri Kanunu m.7", "7036"),
    ("Hukuk Uyuşmazlıklarında Arabuluculuk Kanunu m.18", "6325"),
])
def test_yeni_kisaltma_ve_adlar_resmi_numaraya_eslenir(metin, no):
    atiflar = _mevzuat(metin)
    assert len(atiflar) == 1 and no in atiflar[0].kanun_anahtar, (metin, atiflar)


def test_kanun_no_eslemesi_resmi_numaralarla():
    assert kt.KANUN_NO["İMK"] == "7036" and kt.KANUN_NO["TK"] == "7201"
    assert kt.KANUN_NO["HUAK"] == "6325" and kt.KANUN_NO["KMK"] == "634"
    assert kt.KANUN_NO["AVK"] == "1136"
    # eski eşleme değişmedi
    assert kt.KANUN_NO["TBK"] == "6098" and kt.KANUN_NO["AY"] == "2709"


@pytest.mark.parametrize("metin,tur,madde", [
    ("4857 sayılı Kanun geçici m. 8 uyarınca", "gecici", "8"),
    ("4857 sayılı Kanun'un geçici 8. maddesi", "gecici", "8"),
    ("4857 s.K. ek m.3", "ek", "3"),
    ("375 s. KHK geçici m.24/1-c", "gecici", "24/1-c"),
    ("6102 sayılı TTK'nın geçici 7. maddesinin", "gecici", "7"),
    ("4857 sayılı Kanun EK MADDE 3", "ek", "3"),
])
def test_ek_gecici_madde_turuyle_cikarilir(metin, tur, madde):
    atiflar = _mevzuat(metin)
    assert len(atiflar) == 1, (metin, [a.metin for a in atiflar])
    assert atiflar[0].madde_turu == tur and atiflar[0].madde == madde


def test_olagan_ve_gecici_madde_ayri_atiftir():
    atiflar = kt.atiflari_cikar("İK m.8 ile İK geçici m.8 farklı hükümlerdir.")
    turler = sorted((a.madde_turu or "") for a in atiflar if a.tur == "mevzuat")
    assert turler == ["", "gecici"]


def test_numarali_eski_kanun_yeni_kanun_numarasini_almaz():
    a = _mevzuat("765 sayılı Türk Ceza Kanunu m.5")[0]
    assert a.kanun_anahtar == {"765"}, a.kanun_anahtar


def test_basin_is_kanunu_is_kanunu_sanilmaz():
    assert _mevzuat("Basın İş Kanunu m.6") == []
    assert "4857" in _mevzuat("İş Kanunu'nun 17. maddesi")[0].kanun_anahtar


def test_s_kisaltmasi_sayfa_numarasini_kanun_sanmaz():
    atiflar = _mevzuat("Yazar, Kitap, Ankara 2019, s. 45 vd.")
    assert atiflar == []


def test_ciplak_bicimde_yil_madde_sayilmaz():
    """Eşlemeye giren kısaltmalar «HUAK 2012 yılında» gibi cümleyi sahte
    «m.2012» atfına çevirmesin; madde numarası korunur."""
    assert _mevzuat("6325 sayılı HUAK 2012 yılında yürürlüğe girdi.") == []
    assert [a.madde for a in _mevzuat("HUAK 18 uyarınca")] == ["18"]


# ── Fable karşı-tez turu: çıkarım tarafı ────────────────────────────────────

@pytest.mark.parametrize("metin,beklenen", [
    ("ANAYASASI MADDE 36 uyarınca", {"2709", "AY"}),          # eskiden sahte «AYASASI»
    ("Anayasasının 36. maddesi", {"2709", "AY"}),
    ("TÜRK BORÇLAR KANUNU MADDE 49", {"6098", "TBK"}),
    ("İŞ KANUNU MADDE 17", {"4857", "IK"}),
    ("6098 sayılı TBK m.49", {"6098", "TBK"}),
    ("765 sayılı TCK m.5", {"765"}),                           # TCK→5237 EKLENMEZ
    ("375 s. KHK m.28", {"375"}),                              # «KHK» kimlik değil
])
def test_kanun_anahtari_buyuk_harf_ve_numara_kimligi(metin, beklenen):
    atiflar = _mevzuat(metin)
    assert len(atiflar) == 1, (metin, [a.metin for a in atiflar])
    assert atiflar[0].kanun_anahtar == beklenen, atiflar[0].kanun_anahtar


@pytest.mark.parametrize("metin", [
    "anayasal düzen m.36 bakımından", "Basın-İş Kanunu m.6", "basın iş kanunu m.6",
    "4857 sayılı Kanuna ek 2 maddeyle değişiklik yapıldı",
])
def test_yanlis_atif_uretilmez(metin):
    assert _mevzuat(metin) == [], metin


def test_ek_gecici_ters_bicimde_sira_eki_kabul():
    a = _mevzuat("4857 sayılı Kanun'un geçici 8'inci maddesi")
    assert [(x.madde_turu, x.madde) for x in a] == [("gecici", "8")]


# ── Fable karşı-tez #1: madde izi yalnız MADDE BAĞLAMINDA ───────────────────

@pytest.mark.parametrize("segment,madde,var", [
    ("mevzuatgov:kanun:5:6100:m222", "222", True),
    ("6102 s.K. m.411 (madde_no=411)", "411", True),
    ("mevzuat_getir mevzuatgov:kanun:5:2577 madde_no 49", "49", True),
    ('{"madde_no": 51}', "51", True),
    ("HMK 222 uyarınca", "222", True),
    ("HMK'nın 222. maddesi", "222", True),
    ("**MADDE 51**- (1) Bireysel başvuru", "51", True),
    ("(m216)", "216", True),
    ("HMK m.353/1-a-6", "353/1", True),
    ("| 2026-10-05T10:35:47 | mevzuat_getir | HMK m.119 |", "35", False),
    ("(Ek:16/7/2026-7589/13 md.)", "13", False),
    ("Hüküm 35 gün içinde", "35", False),
    ("4857 m.32; ek m.3", "3", False),
    ("geçici   madde    8", "8", False),
])
def test_madde_izi_baglam_kurali(segment, madde, var):
    seg = kt._segmentler(segment)[0]
    assert kt._madde_var(seg, madde, None, ("HMK", "6100")) is var, (segment, madde)


def _kutuk_satiri_mevzuat(sorgu, sonuc, zaman="2026-10-05T10:35:47"):
    return f"| {zaman} | mevzuat_getir | {sorgu} | {sonuc} | — |"


def test_zaman_damgasi_madde_teyidi_saymaz(tmp_path):
    """YANLIŞ-TEYİT KAPATILDI: kütükte yalnız HMK m.119 teyidi varken «HMK
    m.35» damganın «:35:» parçasıyla TEYİTLİ geçiyordu."""
    satir = _kutuk_satiri_mevzuat("HMK m.119", "6100 sayılı HMK m.119 metni")
    _iskele(tmp_path, "Dilekçe HMK m.35 uyarınca verildi.\n", [satir])
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 1 and "TEYİTSİZ" in out, out
    _iskele(tmp_path, "Dilekçe HMK m.119 uyarınca verildi.\n", [satir])
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, out


def test_degisiklik_notu_ve_tarih_yili_iz_degildir():
    satir = _kutuk_satiri_mevzuat("5237 madde 158",
                                  "5237 s. TCK m.158/4 (Ek:16/7/2026-7589/13 md.)")
    a = _mevzuat("TCK m.13")[0]
    assert not any(kt.segment_eslesir(a, s) for s in kt._segmentler(satir))
    satir2 = _kutuk_satiri_mevzuat("TBK m.68", "TBK m.68 metni (RG 12.05.2004)")
    b = _mevzuat("İİK m.68")[0]                     # 2004 sayılı Kanun
    assert not any(kt.segment_eslesir(b, s) for s in kt._segmentler(satir2))
    c = _mevzuat("TCK m.158")[0]
    assert any(kt.segment_eslesir(c, s) for s in kt._segmentler(satir))


def test_tk_eslemesi_raporda_gorunur(tmp_path):
    _iskele(tmp_path, "Tebliğ TK m.21 uyarınca usulsüzdür.\n",
            [_kutuk_satiri_mevzuat("tebligat m21", "7201 sayılı Tebligat Kanunu m.21 metni")])
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0 and "kısaltma eşlemesi" in out and "7201 sayılı Tebligat Kanunu" in out, out
    _iskele(tmp_path, "Tebliğ 7201 sayılı TK m.21 uyarınca usulsüzdür.\n",
            [_kutuk_satiri_mevzuat("tebligat m21", "7201 sayılı Tebligat Kanunu m.21 metni")])
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0 and "kısaltma eşlemesi" not in out, out


# ── güvenlik: felaket geri izleme (ReDoS) yok ───────────────────────────────
# Zaman ÖLÇÜLMEZ (deterministik): eski art arda isteğe bağlı `\s*` yapısıyla bu
# girdiler pratikte bitmezdi (polinom geri izleme); düzeltilmiş desenle çağrı
# hemen döner. Maskelenmiş kaynakça bloğu gerçekte binlerce boşluk üretir.
UZUN_BOSLUK = " " * 50000


def test_ters_bicim_uzun_bosluk_dizisinde_kilitlenmez():
    assert _mevzuat("4857 sayılı Kanun'un 8" + UZUN_BOSLUK + "son") == []
    assert _mevzuat("Anayasa'nın 36" + UZUN_BOSLUK + "." + UZUN_BOSLUK + "x") == []


def test_kanunsuz_ekgec_uzun_bosluk_dizisinde_kilitlenmez():
    assert kt.kanunsuz_ekgec_anislari("ek 3" + UZUN_BOSLUK + "x", []) == []


def test_aihm_deseni_uzun_bosluk_dizisinde_kilitlenmez():
    assert ko.esas_karar_atiflari("AİHM kararı B. No" + UZUN_BOSLUK + "x") == []
    assert ko.esas_karar_atiflari("AİHM kararı no." + UZUN_BOSLUK + "x") == []


def test_esas_karar_etiketi_uzun_bosluk_dizisinde_kilitlenmez():
    """Eski `_KUYRUK` («E»/«K» + art arda isteğe bağlı boşluk) aynı girdide
    kilitlenirdi; dil değişmedi — olağan künye aynen ayrışır."""
    assert ko.esas_karar_atiflari("Yargıtay E" + UZUN_BOSLUK + "x") == []
    assert ko.ayristirilamayan_atiflar("Yargıtay K" + UZUN_BOSLUK + "x") == []
    a = ko.esas_karar_atiflari("Yargıtay 9. HD, E. 2020/1111, K. 2021/2222")
    assert [(x["esas"], x["karar"]) for x in a] == [("2020/1111", "2021/2222")]
    b = ko.esas_karar_atiflari("Yargıtay 9. HD E: 2020/1 K. No: 2021/2 sayılı kararı")
    assert [(x["esas"], x["karar"]) for x in b] == [("2020/1", "2021/2")]


def test_kanunsuz_gecici_madde_teyitsiz_uretmez_bilgi_basar(tmp_path):
    """«GEÇİCİ MADDE 8» kanunsuz yazıldığında eskiden «GEÇİCİ» adlı hayalî
    kanunun maddesi sayılıp sahte TEYİTSİZ çıkıyordu; artık [BİLGİ]."""
    _iskele(tmp_path, "Somut olayda GEÇİCİ MADDE 8 uygulanmalıdır.\n")
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, out
    assert "KANUNU BELİRSİZ EK/GEÇİCİ" in out and "TEYİTSİZ" not in out


def test_Y09_anayasa_atfi_artik_denetlenir_teyitsizse_engel(tmp_path):
    """Eskiden exit 0 ile denetimsiz geçen Anayasa atfı artık kapıdadır."""
    _iskele(tmp_path, "Anayasa'nın 36. maddesi hak arama hürriyetini korur.\n")
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 1, out
    assert "TEYİTSİZ" in out and "2709" in out


def test_Y09_anayasa_atfi_mevzuat_kaydiyla_teyitli(tmp_path):
    _iskele(tmp_path, "Anayasa'nın 36. maddesi hak arama hürriyetini korur.\n",
            ["| 2026-10-05T10:00:00 | mevzuat_getir | anayasa m36 | Anayasa m.36 "
             "(mevzuatgov:kanun:5:2709) okundu | — |"])
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, out
    assert "[TEYİTLİ]" in out and "İKİNCİ EL" not in out


def test_tk_kisaltmasi_kutukteki_tebligat_kanunu_numarasiyla_eslesir(tmp_path):
    _iskele(tmp_path, "Tebliğ TK m.21 uyarınca usulsüzdür.\n",
            ["| 2026-10-05T10:00:00 | mevzuat_getir | tebligat m21 | 7201 sayılı "
             "Tebligat Kanunu m.21 metni | — |"])
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, out


def test_kayan_pencere_sayiyi_kesmez_sahte_esas_izi_yok():
    """Pencere sonu «2023/1234»ü «2023/1» diye kesiyordu → esas 2023/1 sahte
    izle eşleşebiliyordu. Pencereler artık boşluğa hizalanır (yalnız genişler)."""
    metin = "a " * 125 + "abc " + "2023/1234 sonraki metin"
    segs = kt._segmentler(metin)
    assert not any(kt._sayi_var(s, "2023/1") for s in segs)
    assert any(kt._sayi_var(s, "2023/1234") for s in segs)


def test_gecici_madde_teyidi_olagan_maddeyi_karsilamaz(tmp_path):
    satir = ("| 2026-10-05T10:00:00 | mevzuat_getir | is k gecici 8 | 4857 sayılı "
             "Kanun geçici m.8 metni | — |")
    _iskele(tmp_path, "4857 sayılı Kanun geçici m. 8 uygulanır.\n", [satir])
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, out
    _iskele(tmp_path, "4857 sayılı Kanun m.8 uygulanır.\n", [satir])
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 1 and "TEYİTSİZ" in out, out


# ── B-21 / B-03: teyit derinliği (advisory) ─────────────────────────────────

DOKUM_X = ("T.C. YARGITAY 9. HUKUK DAİRESİ E. 2020/1111 K. 2021/2222\n"
           "... bölge adliye mahkemesinin 2019/77 E. 2019/88 K. sayılı kararı ...\n"
           "... 1475 sayılı Kanun m.14 uyarınca ...\n")
SATIR_X = ("| 2026-10-05T10:00:00 | ictihat_getir | kurgu | Yargıtay 9. HD, E. 2020/1111, "
           "K. 2021/2222 DAMGA=LEHE DOKUM-SINIFI=tam-metin | [d](_oa/teyit/dokum/"
           "001-ictihat_getir-x.md) |")


def test_tam_metin_derinligi_gorunur(tmp_path):
    _iskele(tmp_path, "Yargıtay 9. HD, E. 2020/1111, K. 2021/2222 kararı.\n",
            [SATIR_X], {"001-ictihat_getir-x.md": DOKUM_X})
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, out
    assert "TAM METNİ" in out and "İKİNCİ EL" not in out


def test_ikinci_el_ictihat_teyitli_ama_uyarili_exit0(tmp_path):
    _iskele(tmp_path, "BAM 2019/77 E. 2019/88 K. sayılı kararı emsaldir.\n",
            [SATIR_X], {"001-ictihat_getir-x.md": DOKUM_X})
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, out                       # iz gerçek → statü TEYİTLİ
    assert "[TEYİTLİ]" in out and "İKİNCİ EL" in out
    assert "⚠ İKİNCİ EL 1" in out              # ÖZET sayacı


def test_icinde_alintili_isaretli_kutuk_satiri_ikinci_el(tmp_path):
    _iskele(tmp_path, "Örnek BAM 3. HD 2024/500 E. 2025/600 K. kararı.\n",
            ["| 2026-10-05T10:00:00 | ictihat_getir | kurgu | Örnek BAM 3. HD "
             "2024/500 E. 2025/600 K. TEYİTLİ (belge 999 içinde alıntılı) | — |"])
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0 and "İKİNCİ EL" in out, out


def test_yalniz_arama_kaydi_derinligi(tmp_path):
    _iskele(tmp_path, "Yargıtay 3. HD, E. 2021/10, K. 2021/20 kararı.\n",
            ["| 2026-10-05T10:00:00 | ictihat_ara | kurgu | Yargıtay 3. HD, E. 2021/10, "
             "K. 2021/20 [ARAMA — tam metin çekilmedi] | — |"])
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, out
    assert "ARAMA" in out and "yalnız-ARAMA 1" in out


def test_mevzuat_maddesi_yalniz_ictihat_dokumunde_ikinci_el(tmp_path):
    """B-03: 1475 m.14 bir içtihat dökümünde anıldı diye mevzuat teyidi sayılmaz."""
    _iskele(tmp_path, "1475 sayılı Kanun m.14 yürürlüktedir.\n",
            [SATIR_X], {"001-ictihat_getir-x.md": DOKUM_X})
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0 and "İKİNCİ EL" in out and "mevzuat sorgusu" in out, out


def test_mevzuat_maddesi_mevzuat_kaydiyla_birinci_el(tmp_path):
    _iskele(tmp_path, "1475 sayılı Kanun m.14 yürürlüktedir.\n",
            [SATIR_X, "| 2026-10-05T10:01:00 | mevzuat_getir | 1475 m14 | 1475 sayılı "
                      "Kanun m.14 yürürlükte | — |"],
            {"001-ictihat_getir-x.md": DOKUM_X})
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0 and "İKİNCİ EL" not in out, out


def test_merci_uyusmazligi_ikinci_bir_ikinci_el_uyarisi_uretmez(tmp_path):
    """Fable #5(b): daire farkı ayrı bir bulgudur — sahte «İKİNCİ EL» eklenmez.

    v0.5.18 (Fable bağımsız denetimi K3, 2026-10-08): izde aynı E/K FARKLI daireye (9. HD) ait,
    taslak 3. HD diyor → artık TEYİTSİZ (exit 1) ve «MERCİ ÇELİŞKİSİ». Eski «⚠ MERCİ DOĞRULANAMADI»
    + exit 0, yanlış daireli künyeyi mahkemeye «teyitli» gönderiyordu (E/K her dairede yılda
    sıfırdan başlar). Derinlik satırı yalnız teyitli künyede basıldığından burada beklenmez."""
    _iskele(tmp_path, "Yargıtay 3. HD, E. 2020/1111, K. 2021/2222 kararı.\n", [SATIR_X])
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 1 and "MERCİ ÇELİŞKİSİ" in out and "9. HD" in out, out
    assert "İKİNCİ EL" not in out, out


def test_arama_isabet_listesindeki_kunye_ikinci_el_degil_yalniz_arama(tmp_path):
    """Fable #5(a): ARAMA kaydının sonuç listesindeki ikinci isabet «başka
    kararın içinde» değildir — varlığı arama sonucunda görülmüştür."""
    _iskele(tmp_path, "Yargıtay 9. HD, E. 2021/30, K. 2021/40 kararı.\n",
            ["| 2026-10-05T10:00:00 | ictihat_ara | kurgu | 1) Yargıtay 9. HD, E. 2021/10, "
             "K. 2021/20; 2) Yargıtay 9. HD, E. 2021/30, K. 2021/40 [ARAMA — tam metin "
             "çekilmedi] | — |"])
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0 and "İKİNCİ EL" not in out and "yalnız-ARAMA 1" in out, out


def test_damgasiz_satirda_sonraki_hucredeki_ilk_kunye_kendi_kunyedir():
    satir = ("| 2026-10-05T10:00:00 | ictihat_getir | ilgili: Yargıtay 1. HD E. 2019/1 "
             "K. 2019/2 | Yargıtay 9. HD E. 2020/1111 K. 2021/2222 okundu | — |")
    assert kt._satirin_kendi_kunyesi_mi(satir, "2020/1111", "2021/2222")
    # DAMGA'lı satırda kimlik script'in doğruladığı (DAMGA hücresindeki) künyedir
    damgali = ("| 2026-10-05T10:00:00 | ictihat_getir | Yargıtay 1. HD E. 2019/1 K. 2019/2 "
               "DAMGA=LEHE | Yargıtay 9. HD E. 2020/1111 K. 2021/2222 | — |")
    assert not kt._satirin_kendi_kunyesi_mi(damgali, "2020/1111", "2021/2222")


@pytest.mark.parametrize("metin,aile", [
    ("search_mevzuat_detail", "mevzuat"), ("get_yargitay_document", "ictihat"),
    ("001-mevzuat_getir-x.md", "mevzuat"), ("aihm_ictihat_ara", "ictihat"),
    ("düz metinde mevzuat ve anayasa sözcükleri", None),
])
def test_arac_ailesi_alt_cizgili_ad_okur(metin, aile):
    assert kt._arac_ailesi(metin) == aile


# ── B-17: davanın kendi geçmişi ─────────────────────────────────────────────

DOSYA_MD = ("# Dosya Kimliği — kurgu\n"
            "- Aşama + merci + esas no: Temyiz — Danıştay 10. Daire E. 2024/123; "
            "temyiz edilen: Örnek BİM 3. İDD E. 2023/45 K. 2023/67; ilk derece: "
            "Örnek 1. İdare Mah. E. 2022/8 K. 2023/9\n")
BASLIK = ("DANIŞTAY 10. DAİRESİNE\n"
          "TEMYİZ EDİLEN KARAR: Örnek BİM 3. İDD E. 2023/45 K. 2023/67\n"
          "İLK DERECE KARARI: Örnek 1. İdare Mah. E. 2022/8 K. 2023/9\n")


def test_dava_gecmisi_kunyeleri_noktali_virgulle_ayrisir(tmp_path):
    (tmp_path / "_oa").mkdir()
    (tmp_path / "_oa" / "dosya.md").write_text(DOSYA_MD, encoding="utf-8")
    kunyeler = ko.dava_gecmisi_kunyeleri(kok=str(tmp_path))
    ciftler = {(k["esas"], k["karar"]) for k in kunyeler}
    assert ("2023/45", "2023/67") in ciftler and ("2022/8", "2023/9") in ciftler
    assert ("2024/123", None) in ciftler      # esas-only kendi numara karara yapışmadı


def test_B17_kunye_teyit_kendi_gecmisi_muaf_ve_iz_birakir(tmp_path):
    _iskele(tmp_path, BASLIK + "\nAçıklama: başka atıf yok.\n", dosya_md=DOSYA_MD)
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, out
    assert "davanın KENDİ geçmişi" in out and "TEYİTSİZ" not in out
    kayit = [json.loads(s) for s in (tmp_path / "_oa" / "defter" /
             "istisna-kayitlari.jsonl").read_text(encoding="utf-8").splitlines() if s.strip()]
    assert {k["tur"] for k in kayit} == {"kunye-istisna-dava-gecmisi"} and len(kayit) == 2


def test_B17_ictihat_muhakeme_kapisi_kendi_gecmisini_bloklamaz(tmp_path):
    _iskele(tmp_path, BASLIK + "\nAçıklama: başka atıf yok.\n", dosya_md=DOSYA_MD)
    kod, out = _cli(IMD_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, out
    assert "[G2-İSTİSNA]" in out and "[BLOK]" not in out


def test_B17_beyansiz_ayni_baslik_eskisi_gibi_engel(tmp_path):
    """Beyan yoksa muafiyet yok — davranış eskisiyle aynı (fail-closed)."""
    _iskele(tmp_path, BASLIK)
    assert _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)[0] == 1
    assert _cli(IMD_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)[0] == 1


def test_B17_karar_no_uyusmazsa_muafiyet_yok(tmp_path):
    _iskele(tmp_path, "TEMYİZ EDİLEN KARAR: Örnek BİM 3. İDD E. 2023/45 K. 2023/68\n",
            dosya_md=DOSYA_MD)
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 1 and "TEYİTSİZ" in out, out


def test_B17_daire_uyusmazsa_muafiyet_yok():
    kunyeler = [{"esas": "2023/45", "karar": "2023/67", "daire_key": ("3", "HD"),
                 "kaynak": "t", "metin": ""}]
    atif = {"esas": "2023/45", "karar": "2023/67", "daire_key": ("4", "HD"),
            "kunye_turu": "esas_karar"}
    assert ko.dava_gecmisi_eslesmesi(atif, kunyeler) is None
    atif["daire_key"] = ("3", "HD")
    assert ko.dava_gecmisi_eslesmesi(atif, kunyeler) is not None


def test_B17_kendi_kunye_bayragi(tmp_path):
    _iskele(tmp_path, "İSTİNAF EDİLEN KARAR: Örnek 5. Asliye Hukuk E. 2025/11 K. 2026/22\n")
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path, "--kendi-kunye",
                             "Örnek 5. Asliye Hukuk E. 2025/11 K. 2026/22"], tmp_path)
    assert kod == 0 and "davanın KENDİ geçmişi" in out, out


def test_B17_esas_only_kendi_dosya_no_eksik_kunye_sayilmaz(tmp_path):
    _iskele(tmp_path, "Danıştay 10. Daire E. 2024/123 sayılı dosya\n", dosya_md=DOSYA_MD)
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, out
    assert "EKSİK KÜNYE" not in out.split("ATIF/KÜNYE DOĞRULAMA KAPISI")[-1]


# ── B-17 sertleştirme (Fable karşı-tez #3/#4) ───────────────────────────────

def test_B17_etiket_satir_basina_capali_emsal_esas_no_beyan_degil(tmp_path):
    (tmp_path / "_oa").mkdir()
    (tmp_path / "_oa" / "dosya.md").write_text(
        "- Emsal esas no: Yargıtay 9. HD E. 2020/1111 K. 2021/2222\n"
        "- Karşı taraf esas no: Örnek Mah. E. 2021/5 K. 2021/6\n"
        "- **Dava geçmişi:** Örnek 2. Asliye Hukuk E. 2023/9 K. 2024/1\n", encoding="utf-8")
    kunyeler = ko.dava_gecmisi_kunyeleri(kok=str(tmp_path))
    assert [(k["esas"], k["karar"]) for k in kunyeler] == [("2023/9", "2024/1")]


def test_B17_beyan_siniri_asilirsa_muafiyet_hic_uygulanmaz(tmp_path):
    fazla = "".join(f"- Dava geçmişi: Örnek Mah. E. 2020/{i} K. 2021/{i}\n"
                    for i in range(1, ko.DAVA_GECMISI_AZAMI + 2))
    _iskele(tmp_path, BASLIK, dosya_md=DOSYA_MD + fazla)
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 1 and "UYGULANMADI" in out and "TEYİTSİZ" in out, out


def test_B17_esas_only_atifta_yuksek_mahkeme_izi_beyanda_olmali():
    kunyeler = ko.dava_gecmisi_kunyeleri(
        ek_metinler=["İlk derece: Örnek 1. Asliye Hukuk E. 2023/9 K. 2024/1"])
    hgk = {"esas": "2023/9", "karar": None, "daire_key": None,
           "kunye_turu": "esas_karar", "metin": "Yargıtay HGK E. 2023/9"}
    kendi = dict(hgk, metin="Mahkemenin E. 2023/9")
    assert ko.dava_gecmisi_eslesmesi(hgk, kunyeler) is None
    assert ko.dava_gecmisi_eslesmesi(kendi, kunyeler) is not None


def test_B17_eksik_kunye_satiri_merci_izine_bakar():
    kunyeler = ko.dava_gecmisi_kunyeleri(
        ek_metinler=["İlk derece: Örnek 1. Asliye Hukuk E. 2023/9 K. 2024/1"])
    assert not ko.dava_gecmisi_satiri_mi("Yargıtay HGK'nın 2023/9 sayılı kararı", kunyeler)
    assert ko.dava_gecmisi_satiri_mi(
        "Mahkemenin 2023/9 sayılı kararı Yargıtay içtihadına aykırıdır", kunyeler)


def test_B17_etiket_deseni_uzun_bosluk_dizisinde_kilitlenmez(tmp_path):
    (tmp_path / "_oa").mkdir()
    (tmp_path / "_oa" / "dosya.md").write_text(
        UZUN_BOSLUK + "x\n-" + UZUN_BOSLUK + "esas\n", encoding="utf-8")
    assert ko.dava_gecmisi_kunyeleri(kok=str(tmp_path)) == []


# ── AİHM künyesinin Türkçe yazımı ───────────────────────────────────────────

@pytest.mark.parametrize("metin,no", [
    ("AİHM, Örnek/Türkiye, no. 12345/18, 10.12.2019 kararı", "12345/18"),
    ("Avrupa İnsan Hakları Mahkemesinin Örnek/Türkiye (Başvuru no. 54321/20) kararı", "54321/20"),
    ("AİHM'in kararında B. No: 98765/19 ile", "98765/19"),
])
def test_turkce_aihm_kunyesi_taninir_eksik_kunye_degil(metin, no):
    atiflar = ko.esas_karar_atiflari(metin)
    assert [(a["kunye_turu"], a["esas"]) for a in atiflar] == [("aihm_basvuru", no)]
    assert ko.ayristirilamayan_atiflar(metin) == []


def test_aym_bb_numarasi_aihm_sayilmaz_ve_karar_no_yakalanmaz():
    a = ko.esas_karar_atiflari("AYM, Örnek başvurusu, B. No: 2018/12345, 1.1.2020")
    assert [x["kunye_turu"] for x in a] == ["aym_bb"]
    b = ko.esas_karar_atiflari("Yargıtay 9. HD Karar no: 2021/18 ile ilgili AİHM kararı")
    assert not [x for x in b if x["kunye_turu"] == "aihm_basvuru"]


@pytest.mark.parametrize("metin,no", [
    ("AİHM, Örnek/Türkiye, No. 12345/18", "12345/18"),           # büyük harf «No.»
    ("AİHM, Örnek/Türkiye, no. 12345/2018", "12345/18"),        # dört haneli yıl
])
def test_aihm_turkce_kunye_genisletilmis_yazim(metin, no):
    assert [(a["kunye_turu"], a["esas"]) for a in ko.esas_karar_atiflari(metin)] == [
        ("aihm_basvuru", no)]


def test_aihm_baglamli_satirdaki_turk_karar_numarasi_aihm_sayilmaz():
    atiflar = ko.esas_karar_atiflari("AİHM kararına aykırı; Karar no. 2021/18")
    assert not [a for a in atiflar if a["kunye_turu"] == "aihm_basvuru"]


def test_aihm_kunyesi_kutukte_varsa_teyitli(tmp_path):
    _iskele(tmp_path, "AİHM, Örnek/Türkiye, no. 12345/18, 10.12.2019, § 45.\n",
            ["| 2026-10-05T10:00:00 | aihm_ictihat_ara | kurgu | Örnek/Türkiye, "
             "no. 12345/18 [ARAMA — tam metin çekilmedi] | — |"])
    kod, out = _cli(KT_YOL, ["taslak.md", "--kok", tmp_path], tmp_path)
    assert kod == 0, out
    assert "EKSİK KÜNYE" not in out and "[TEYİTLİ]" in out


# ── belgeler ────────────────────────────────────────────────────────────────

def test_skill_ve_gunluk_v0518_kurallarini_anlatir():
    skill = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol" /
             "SKILL.md").read_text(encoding="utf-8")
    gunluk = (REPO / "plugins" / "ortak-avukat" / "skills" / "oa-kontrol" / "references" /
              "degisiklik-gunlugu.md").read_text(encoding="utf-8")
    for parca in ("İKİNCİ EL", "dava geçmişi", "Anayasa'nın 36. maddesi", "AİHM künyesi",
                  "MADDE BAĞLAMINDA", "SATIR BAŞINDA"):
        assert parca in skill, parca
    assert "v0.5.18 (aday)" in gunluk and "B-17" in gunluk and "Y-09" in gunluk
    assert "Fable 5.1 karşı-tez turu" in gunluk and "REDDEDİLEN" in gunluk

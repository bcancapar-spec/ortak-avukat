# -*- coding: utf-8 -*-
"""v0.5.14 — TESLİM + KÜNYE + KAYNAKÇA paketi (B-2, B-3, B-13, B-14, B-18,
B-24, B-29, B-30, B-33).

Bu paket sistemin VARLIK SEBEBİNE dokunur: uydurma içtihadın avukatın
imzasını taşıyacak metne girmesini engellemek. Denetim raporunun (2026-08-31)
kanıtları burada REGRESYON TESTİNE çevrilir.

Kapsanan bulgular
-----------------
B-2  Künye/atıf kapısı yaygın künye biçimlerini görmüyordu (`E:2020/1111`,
     küçük harf `esas/karar`, AYM `B. No:`, AİHM `Application no.`), üstelik
     merci anılıp künye ayrıştırılamadığında kapı "atıf yok" diyerek AÇILIYORDU
     (fail-OPEN). Artık: desen kümesi genişledi + ayrıştırılamayan atıf iddiası
     fail-CLOSED.
B-3  `kaynakca_uret.py`, kütüğün hiç görmediği künye için dilekçeye "tamamı tam
     metinleriyle okunup kütüğe damgalanmıştır" yazıyordu — belgeye yalan.
     Artık beyan KOŞULLU; teyitsiz künye "⚠ TEYİT EDİLMEDİ" satırı alır.
B-13 `artifact_sha256` alanı OLMAYAN mühür sessizce "bayat" sayılıyordu; ayrı
     `shasiz` sınıfı + açık RED gerekçesi.
B-14 `.docx`/`.pdf` teslim sınıfı sayılıyor ama mühür-tazelik taraması yalnız
     `.udf`e bakıyordu — makbuz sonrası değişiklik penceresi açıktı.
B-18 `teslim_paketi.py` girdisini mutasyona uğratıyordu: kaynakça bloğunun
     yazdığı `⚠`, ikinci koşuda dilekçe denetiminin [C] OCR şerhi kapısını
     kapatıyordu (1. koşu yeşil, 2. koşu kırmızı).
B-24 argparse hatasında bile `_oa/defter/` açıp RED makbuzu yazılıyordu —
     yazım hatası dosya sistemini kirletiyor ve sahte dava kökü işareti
     yaratıyordu.
B-29 Ölü sarmalayıcı `_t_beyan_var_mi` (0 çağrı).
B-30 `[K] m.6 CEPHANELİK BEKÇİSİ` regex'i gerçek dilekçe cümlesinde
     ateşlemiyordu (madde atfındaki nokta, satır kırığı, fiil listesi).
B-33 Makbuz şeması belgede 11 alan, üretici 17 alan yazıyordu.

Tamamen ağsız/deterministik; tüm veriler sentetiktir.
"""
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SK = REPO / "plugins" / "ortak-avukat" / "skills"
KONTROL = SK / "oa-kontrol" / "scripts"
DILEKCE = SK / "oa-dilekce" / "scripts"


def _yukle(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ko():
    return _yukle(KONTROL / "kunye_ortak.py", "v0514_kunye_ortak")


@pytest.fixture(scope="module")
def ka():
    return _yukle(KONTROL / "kaynakca_uret.py", "v0514_kaynakca")


@pytest.fixture(scope="module")
def tp():
    return _yukle(KONTROL / "teslim_paketi.py", "v0514_teslim_paketi")


@pytest.fixture(scope="module")
def dd():
    return _yukle(DILEKCE / "dilekce_denetim.py", "v0514_dilekce_denetim")


# ═══════════════════ B-2 — künye kapısı körlüğü ═══════════════════════════
# Denetim kanıtı (her satır ayrı koşuldu): 'E. 2020/1111, K. 2021/2222' BLOK
# ederken 'E:2020/1111', 'E: 2020/1111', küçük harf 'esas … karar …',
# 'AYM B. No: 2019/12345', 'AİHM Application no. 1234/05' ve
# 'Yargıtay 22. HD, 12.03.2019 tarihli kararı' kapıyı AÇIK bırakıyordu (exit 0).

B2_ESAS_KARAR_VAKALARI = [
    ("nokta_bosluk", "Yargıtay 9. HD, E. 2020/1111, K. 2021/2222 sayılı kararı"),
    ("iki_nokta_bitisik", "Yargıtay 9. HD, E:2020/1111, K:2021/2222 sayılı kararı"),
    ("iki_nokta_bosluklu", "Yargıtay 9. HD, E: 2020/1111, K: 2021/2222"),
    ("kucuk_harf_uzun", "Yargıtay 9. hd esas 2020/1111 karar 2021/2222"),
    ("noktasiz_harf", "Yargıtay 9. HD E 2020/1111 K 2021/2222"),
    ("ters_sira", "Yargıtay 9. HD 2020/1111 E. 2021/2222 K."),
    ("ters_sira_noktasiz", "Yargıtay 9. HD 2020/1111 E, 2021/2222 K sayılı"),
    ("bitisik_nokta", "Danıştay 8. Daire E.2020/1111 K.2021/2222"),
    ("esas_no_karar_no", "Yargıtay 9. HD Esas No: 2020/1111 Karar No: 2021/2222"),
]


@pytest.mark.parametrize("ad,metin", B2_ESAS_KARAR_VAKALARI,
                         ids=[t[0] for t in B2_ESAS_KARAR_VAKALARI])
def test_b2_yaygin_kunye_bicimleri_ayristirilir(ko, ad, metin):
    """B-2: her yaygın künye biçimi esas+karar olarak ÇIKARILMALI — biri bile
    görülmezse uydurma içtihat mekanik kapıdan geçer."""
    atiflar = ko.esas_karar_atiflari(metin)
    assert atiflar, f"{ad}: künye hiç görülmedi — kapı AÇIK kalır"
    assert atiflar[0]["esas"] == "2020/1111", f"{ad}: esas yanlış → {atiflar}"
    assert atiflar[0]["karar"] == "2021/2222", f"{ad}: karar yanlış → {atiflar}"


B2_AYM_VAKALARI = [
    ("bb_no", "AYM, B. No: 2019/12345, 12/03/2021 tarihli kararı"),
    ("basvuru_numarasi", "Anayasa Mahkemesi Başvuru Numarası: 2019/12345"),
    ("basvuru_no", "AYM Başvuru No 2019/12345 sayılı kararı"),
]


@pytest.mark.parametrize("ad,metin", B2_AYM_VAKALARI, ids=[t[0] for t in B2_AYM_VAKALARI])
def test_b2_aym_bireysel_basvuru_kunyesi_gorulur(ko, ad, metin):
    """B-2 (yapısal körlük): AYM bireysel başvuruda E./K. YOKTUR — künye
    `Başvuru Numarası: YYYY/N` biçimindedir (6216 s. K. m.45-49 usulü; canlı
    AYM verisinde 'BB 2015/53' biçimi teyit edildi). Eski desen kümesi bu
    künyeyi HİÇ göremiyordu; oa-dilekce `aym_bireysel` tipini desteklerken
    kapı o tip için tamamen kördü."""
    atiflar = ko.esas_karar_atiflari(metin)
    assert atiflar, f"{ad}: AYM başvuru künyesi görülmedi"
    assert atiflar[0]["esas"] == "2019/12345"
    assert atiflar[0].get("kunye_turu") == "aym_bb"


def test_b2_aihm_basvuru_kunyesi_gorulur(ko):
    """B-2: AİHM künyesi (`Application no. 1234/05`) de görülmeli."""
    atiflar = ko.esas_karar_atiflari("AİHM, Kaya/Türkiye, Application no. 1234/05")
    assert atiflar, "AİHM başvuru künyesi görülmedi"
    assert atiflar[0].get("kunye_turu") == "aihm_basvuru"


B2_AYRISTIRILAMAYAN = [
    ("tarihli_karar", "Yargıtay 22. HD, 12.03.2019 tarihli kararı bu yöndedir."),
    ("sayili_karar", "Danıştay 8. Daire'nin 2019/4444 sayılı kararı emsaldir."),
    ("gunlu_karar", "Yargıtay HGK'nın 05.06.2018 günlü kararı uygulanmalıdır."),
]


@pytest.mark.parametrize("ad,metin", B2_AYRISTIRILAMAYAN,
                         ids=[t[0] for t in B2_AYRISTIRILAMAYAN])
def test_b2_ayristirilamayan_atif_fail_closed(ko, ad, metin):
    """B-2 çekirdeği — VARSAYILAN TERSİNE ÇEVRİLDİ: merci anılıyor ve bir karar
    iması var ama künye ayrıştırılamıyorsa sonuç 'atıf yok' DEĞİL,
    'mekanik teyit YAPILAMADI' olmalıdır (fail-closed)."""
    izler = ko.ayristirilamayan_atiflar(metin)
    assert izler, f"{ad}: ayrıştırılamayan atıf iddiası görülmedi (fail-OPEN)"
    assert izler[0]["satir_no"] == 1


B2_TEMIZ = [
    ("merci_var_atif_yok", "Yargıtay'ın yerleşik içtihadı bu yöndedir."),
    ("daire_var_iddia_yok", "Yargıtay 9. HD uygulaması istikrarlıdır."),
    ("tam_kunye", "Yargıtay 9. HD, E. 2020/1111, K. 2021/2222 sayılı kararı"),
    ("kendi_dosya_no", "MERCİ: Ankara BAM 10. HD\nDOSYA NO: 2024/123"),
    ("kendi_esas_no", "ESAS NO: 2025/354 — Denizli 3. İş Mahkemesi"),
]


@pytest.mark.parametrize("ad,metin", B2_TEMIZ, ids=[t[0] for t in B2_TEMIZ])
def test_b2_yanlis_pozitif_uretmez(ko, ad, metin):
    """B-2 yan etki denetimi: fail-closed varsayılan MUHAKEMEYİ ENGELLEMEMELİ.
    Merci anılan ama atıf iddiası olmayan cümle, tam künye ve dilekçenin KENDİ
    künye bloğu (Denizli 346 karnesindeki tek parser yanlış-pozitifi) asla
    'ayrıştırılamayan atıf' sayılmaz."""
    assert ko.ayristirilamayan_atiflar(metin) == [], f"{ad}: yanlış-pozitif"


def test_b2_kunye_teyit_ayristirilamayan_atifta_bloklar(tmp_path):
    """B-2 uçtan uca: kütükte hiçbir iz yokken 'tarihli kararı' biçimli çıplak
    atıf taşıyan taslak kunye_teyit.py kapısını KAPATMALI (eski davranış:
    'Doğrulanacak künye yok — kapı AÇIK', exit 0)."""
    taslak = tmp_path / "taslak.md"
    taslak.write_text("Yargıtay 22. HD, 12.03.2019 tarihli kararı bu yöndedir.\n",
                      encoding="utf-8")
    cp = subprocess.run([sys.executable, str(KONTROL / "kunye_teyit.py"), str(taslak)],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(tmp_path))
    assert cp.returncode != 0, "kapı AÇIK kaldı:\n" + (cp.stdout or "")


# ═══════════════════ B-3 — gerçeğe aykırı "okundu" beyanı ═════════════════

_MUHAKEME_TEYITLI = """# İÇTİHAT MUHAKEME ZİNCİRİ — sentetik

**KUNYE:** Yargıtay 12. Hukuk Dairesi E. 2020/1111 K. 2021/2222 T. 01.02.2021
**KAYNAK-URL:** https://ornek.adalet.gov.tr/ictihat/333
**DAMGA:** LEHE
"""

_TASLAK_ATIF = ("Yargıtay 12. Hukuk Dairesi E. 2020/1111 K. 2021/2222 sayılı "
                "kararı uyarınca talebimiz yerindedir.\n")


def _kok_kur(tmp_path, muhakeme=None, taslak_metni=_TASLAK_ATIF):
    kok = tmp_path / "dava"
    (kok / "_oa" / "cikti").mkdir(parents=True)
    if muhakeme is not None:
        (kok / "_oa" / "cikti" / "03-ictihat-muhakeme.md").write_text(
            muhakeme, encoding="utf-8")
    taslak = kok / "taslak.md"
    taslak.write_text(taslak_metni, encoding="utf-8")
    return kok, taslak


def test_b3_teyitsiz_kunyeye_okundu_beyani_yazilmaz(ka, tmp_path):
    """B-3 (P0) — kütükte HİÇ kaydı olmayan künye için dilekçeye 'tam
    metinleriyle okunup kütüğe damgalanmıştır' yazılamaz. Bu, avukatın
    imzasını taşıyacak belgeye mekanik olarak yalan yazmaktır."""
    kok, taslak = _kok_kur(tmp_path)          # muhakeme kaydı YOK
    ka.taslaga_isle(str(taslak), str(kok))
    yeni = taslak.read_text(encoding="utf-8")
    assert "tam metinleriyle okunup" not in yeni, (
        "teyitsiz künye için gerçeğe aykırı okundu beyanı yazıldı:\n" + yeni)
    assert "TEYİT EDİLMEDİ" in yeni, "teyitsizlik görünür kılınmadı:\n" + yeni


def test_b3_teyitli_kunyede_beyan_korunur(ka, tmp_path):
    """B-3 karşı-denetimi: teyitli künyede beyan KAYBOLMAMALI (v0.5.12
    sözleşmesi korunur — düzeltme beyanı sessizce silmez)."""
    kok, taslak = _kok_kur(tmp_path, muhakeme=_MUHAKEME_TEYITLI)
    ka.taslaga_isle(str(taslak), str(kok))
    yeni = taslak.read_text(encoding="utf-8")
    assert "tam metinleriyle okunup" in yeni
    assert "TEYİT EDİLMEDİ" not in yeni


def test_b3_karisik_listede_beyan_tamami_demez(ka, tmp_path):
    """B-3: bir teyitli + bir teyitsiz künye varsa beyan 'tamamı' diyemez;
    teyitsiz satır ayrıca işaretlenir."""
    kok, taslak = _kok_kur(
        tmp_path, muhakeme=_MUHAKEME_TEYITLI,
        taslak_metni=_TASLAK_ATIF + "Ayrıca Yargıtay 4. HD E. 2099/9999 "
                     "K. 2099/8888 sayılı kararı da bu yöndedir.\n")
    ka.taslaga_isle(str(taslak), str(kok))
    yeni = taslak.read_text(encoding="utf-8")
    assert "TEYİT EDİLMEDİ" in yeni
    assert "kararların tamamı tam metinleriyle" not in yeni, (
        "karışık listede 'tamamı' beyanı sürdü:\n" + yeni)


def test_b3_kaynakca_kunye_ortaktan_okur(ka, ko, tmp_path):
    """B-3 kök nedeni: kaynakça üreteci kendi gevşek desenini kullanıyordu
    ('kunye_ortak ile aynı ruh' diyen yorum, farklı desen). Tek kaynak
    kuralı: kaynakça artık kunye_ortak'ın çıkarımını kullanır — kapı neyi
    görüyorsa kaynakça da onu görür."""
    kok, taslak = _kok_kur(tmp_path, taslak_metni="Yargıtay 9. HD E:2020/1111 K:2021/2222\n")
    ka.taslaga_isle(str(taslak), str(kok))
    yeni = taslak.read_text(encoding="utf-8")
    assert "2020/1111" in yeni.split("<!-- kaynakca:v1 -->")[1], (
        "kapının gördüğü künyeyi kaynakça görmedi:\n" + yeni)


# ═══════════════════ B-13 / B-14 — mühür taraması ═════════════════════════

def _muhurlu(kok, ad, icerik=b"veri", sha=None, bozuk=False):
    """Sentetik teslim ürünü + yanındaki .prov.json mührü."""
    yol = kok / ad
    yol.parent.mkdir(parents=True, exist_ok=True)
    yol.write_bytes(icerik)
    prov = kok / (ad + ".prov.json")
    if bozuk:
        prov.write_text("{ bozuk json", encoding="utf-8")
    elif sha == "__yok__":
        prov.write_text(json.dumps({"arac": "udf_yaz"}), encoding="utf-8")
    else:
        prov.write_text(json.dumps({"artifact_sha256": sha or "0" * 64}),
                        encoding="utf-8")
    return yol


def test_b13_shasiz_muhur_ayri_sinif_ve_red(tp, tmp_path):
    """B-13: `artifact_sha256` alanı OLMAYAN mühür 'bayat' etiketiyle
    yutuluyordu — mührün içini silmek, hiç mühür yazmamaktan temiz
    görünüyordu. Ayrı `shasiz` sınıfı + açık RED gerekçesi gerekir."""
    kok = tmp_path / "dava"
    kok.mkdir()
    _muhurlu(kok, "urun.udf", sha="__yok__")
    sorunlar, _uyarilar, kayitlar = tp._filo_tazelik_denetimi(str(kok))
    assert any(k["muhur"] == "shasiz" for k in kayitlar), kayitlar
    assert any("SHA" in s.upper() for s in sorunlar), sorunlar


def test_b13_bozuk_muhur_okunamadi_regresyon(tp, tmp_path):
    """B-13 karşı-denetimi: okunamayan mühür zaten fail-closed'dı, öyle
    kalmalı."""
    kok = tmp_path / "dava"
    kok.mkdir()
    _muhurlu(kok, "urun.udf", bozuk=True)
    sorunlar, _u, kayitlar = tp._filo_tazelik_denetimi(str(kok))
    assert any(k["muhur"] == "okunamadi" for k in kayitlar)
    assert sorunlar


def test_b14_muhurlu_docx_bayat_yakalanir(tp, tmp_path):
    """B-14: `.docx` teslim sınıfı sayılıyor (40-UYAP'a kopyalanıyor) ama
    hiçbir mühür/tazelik taraması ona bakmıyordu → makbuz sonrası değişiklik
    penceresi bir uzantı için tamamen açıktı. sha karşılaştırması uzantıdan
    BAĞIMSIZDIR."""
    kok = tmp_path / "dava"
    kok.mkdir()
    _muhurlu(kok, "dilekce.docx", sha="beklenmeyen" + "0" * 53)
    sorunlar, _u, kayitlar = tp._filo_tazelik_denetimi(str(kok))
    assert any(k["dosya"].endswith(".docx") for k in kayitlar), kayitlar
    assert any("dilekce.docx" in s for s in sorunlar), sorunlar


def test_b14_muhurlu_pdf_taze_temiz(tp, tmp_path):
    """B-14: mührü GÜNCEL olan .pdf sorun ÜRETMEZ (yanlış-BLOK yasağı)."""
    kok = tmp_path / "dava"
    kok.mkdir()
    yol = kok / "dilekce.pdf"
    yol.write_bytes(b"pdf-veri")
    sha = tp._sha256_dosya(str(yol))
    (kok / "dilekce.pdf.prov.json").write_text(
        json.dumps({"artifact_sha256": sha}), encoding="utf-8")
    sorunlar, _u, kayitlar = tp._filo_tazelik_denetimi(str(kok))
    assert sorunlar == [], sorunlar
    assert any(k["muhur"] == "taze" for k in kayitlar), kayitlar


def test_b14_uyaptaki_muhursuz_docx_red_uretmez(tp, tmp_path):
    """B-14 REGRESYON KORUMASI: 40-UYAP'a kopyalanan .pdf/.docx yoldaşları
    tanım gereği mühürsüzdür (yalnız UDF mühürlenir). Bunları RED saymak her
    yeşil teslimi bir sonraki koşuda kırardı — mühürsüz .pdf/.docx yalnız
    GÖRÜNÜR UYARI üretir."""
    kok = tmp_path / "dava"
    (kok / "40-UYAP").mkdir(parents=True)
    (kok / "40-UYAP" / "dilekce.docx").write_bytes(b"docx")
    sorunlar, uyarilar, _k = tp._filo_tazelik_denetimi(str(kok))
    assert sorunlar == [], sorunlar
    assert any("dilekce.docx" in u for u in uyarilar), uyarilar


def test_b14_uyaptaki_muhursuz_udf_hala_red(tp, tmp_path):
    """B-14 karşı-denetimi: 40-UYAP'ta mühürsüz .udf v0.5.10'dan beri RED —
    genişletme bu sözleşmeyi BOZMAMALI."""
    kok = tmp_path / "dava"
    (kok / "40-UYAP").mkdir(parents=True)
    (kok / "40-UYAP" / "urun.udf").write_bytes(b"udf")
    sorunlar, _u, _k = tp._filo_tazelik_denetimi(str(kok))
    assert any("urun.udf" in s for s in sorunlar), sorunlar


# ═══════════════════ B-18 — idempotans (girdi mutasyonu) ═══════════════════

def test_b18_kaynakca_blogu_ocr_serh_kapisini_kapatmaz(dd):
    """B-18 kök nedeni: kaynakça bloğunun yazdığı `⚠` işaretini ikinci koşuda
    dilekçe denetiminin [C] OCR/⚠ alıntı teyidi yakalıyordu → aynı komut aynı
    dosyada 1. koşuda yeşil, 2. koşuda kırmızı. Makine üretimi kaynakça bloğu
    avukatın gövde metni DEĞİLDİR; denetim onu görmemelidir."""
    govde = "Bu bir dilekçe gövdesidir.\n\n"
    blok = ("<!-- kaynakca:v1 -->\n\n## İÇTİHAT KAYNAKÇASI\n\n"
            "- E. 2020/1111 K. 2021/2222 — ⚠ erişim linki kütüğe işlenmedi\n\n"
            "<!-- /kaynakca -->\n")
    _e, _d, ocr_uyari, _a, _n = dd.denetle(govde + blok, "genel", "")
    assert ocr_uyari is False, "kaynakça bloğunun ⚠'si kapıyı kapattı (B-18)"


def test_b18_govdedeki_ocr_isareti_hala_yakalanir(dd):
    """B-18 karşı-denetimi: gövdedeki ⚠ hâlâ [C] uyarısı üretmeli — maskeleme
    yalnız makine bloğunu kapsar, kapıyı topyekûn körleştirmez."""
    metin = "Bilirkişi raporundan ⚠ alıntı: tazminat 12.345 TL'dir.\n"
    _e, _d, ocr_uyari, _a, _n = dd.denetle(metin, "genel", "")
    assert ocr_uyari is True


def test_b18_makine_blogu_disinda_prose_maskelenmez(ko):
    """B-18 kötüye kullanım koruması: işaretler arasına elle sokuşturulan DÜZ
    METİN maskelenmez (yalnız üretecin kendi ürettiği başlık/önsöz/madde
    satırları maskelenir) — kapı işaret yazarak atlatılamaz."""
    metin = ("<!-- kaynakca:v1 -->\n## İÇTİHAT KAYNAKÇASI\n"
             "- E. 2020/1111 K. 2021/2222 — ⚠ link yok\n"
             "Müvekkil borcu kabul etmektedir ⚠\n"
             "<!-- /kaynakca -->\n")
    maskeli = ko.makine_blogu_maskele(metin)
    assert "Müvekkil borcu kabul etmektedir ⚠" in maskeli
    assert "link yok" not in maskeli
    assert len(maskeli) == len(metin), "maskeleme ofsetleri/satır sayısını bozdu"


def test_b18_kaynakca_uret_idempotent(ka, tmp_path):
    """B-18: aynı komut aynı dosyada arka arkaya koşturulduğunda dosya içeriği
    DEĞİŞMEMELİ (kapı deterministik olmak zorundadır)."""
    kok, taslak = _kok_kur(tmp_path, muhakeme=_MUHAKEME_TEYITLI)
    ka.taslaga_isle(str(taslak), str(kok))
    birinci = taslak.read_text(encoding="utf-8")
    ka.taslaga_isle(str(taslak), str(kok))
    ikinci = taslak.read_text(encoding="utf-8")
    ka.taslaga_isle(str(taslak), str(kok))
    ucuncu = taslak.read_text(encoding="utf-8")
    assert birinci == ikinci == ucuncu


def test_b18_dilekce_denetim_ardisik_kosuda_ayni_exit(tmp_path):
    """B-18 uçtan uca: kaynakça işlendikten SONRA dilekçe denetiminin exit
    kodu değişmemeli (denetim raporundaki `rc=0 → rc=1 → rc=1` dizisi)."""
    kok, taslak = _kok_kur(tmp_path, muhakeme=_MUHAKEME_TEYITLI,
                           taslak_metni=_TASLAK_ATIF)

    def _dd():
        cp = subprocess.run(
            [sys.executable, str(DILEKCE / "dilekce_denetim.py"), str(taslak),
             "--tip", "genel", "--kok", str(kok), "--ictihat-muhakeme-yok"],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        return cp.returncode

    once = _dd()
    ka_mod = _yukle(KONTROL / "kaynakca_uret.py", "v0514_kaynakca_e2e")
    ka_mod.taslaga_isle(str(taslak), str(kok))
    assert _dd() == once, "kaynakça işlendikten sonra kapı hükmü değişti (B-18)"


# ═══════════════════ B-24 — kullanıcı hatası dosya kirletmemeli ═══════════

def test_b24_argparse_hatasi_dosya_sistemine_dokunmaz(tmp_path):
    """B-24: argümansız/yanlış çağrı `./_oa/defter/teslim-makbuz-RED.json`
    yazıyordu — yazım hatası dosya sistemini değiştiriyor ve SAHTE bir dava
    kökü işareti yaratıyordu (diğer scriptler orayı dava kökü sanar).
    'Makbuz garantisi' argümanlar AYRIŞTIKTAN sonra başlar."""
    cp = subprocess.run([sys.executable, str(KONTROL / "teslim_paketi.py")],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(tmp_path))
    assert cp.returncode != 0
    assert not (tmp_path / "_oa").exists(), (
        "argparse hatası dosya sistemini kirletti: " +
        str(list(tmp_path.rglob("*"))))


def test_b24_gecersiz_secim_de_dosya_yazmaz(tmp_path):
    """B-24: geçersiz `--taraf` seçimi de argparse hatasıdır — aynı kural."""
    taslak = tmp_path / "t.md"
    taslak.write_text("x\n", encoding="utf-8")
    cp = subprocess.run(
        [sys.executable, str(KONTROL / "teslim_paketi.py"), str(taslak),
         "--taraf", "olmayan-taraf", "--kok", str(tmp_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(tmp_path))
    assert cp.returncode != 0
    assert not (tmp_path / "_oa").exists()


def test_b24_gercek_red_hala_damgali_makbuz_keser(tmp_path):
    """B-24 karşı-denetimi: mevcut makbuz sözleşmesi ('RED bile damgalı makbuz
    keser') KASITLIYDI ve KORUNUR — argümanlar ayrıştıktan sonraki her
    başarısız yol RED makbuzu düşürmeye devam eder."""
    kok = tmp_path / "dava"
    kok.mkdir()
    cp = subprocess.run(
        [sys.executable, str(KONTROL / "teslim_paketi.py"),
         str(kok / "olmayan.md"), "--kok", str(kok)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(tmp_path))
    assert cp.returncode != 0
    makbuz = kok / "_oa" / "defter" / "teslim-makbuz-RED.json"
    assert makbuz.is_file(), (cp.stdout or "") + (cp.stderr or "")
    veri = json.loads(makbuz.read_text(encoding="utf-8"))
    assert veri.get("erken_cikis") is True


# ═══════════════════ B-29 — ölü sarmalayıcı ═══════════════════════════════

def test_b29_olu_sarmalayici_silindi(dd):
    """B-29: `_t_beyan_var_mi` depo genelinde 0 çağrıydı (tek satır: tanımın
    kendisi); gerçek kapı `_beyan_var_mi`'yı doğrudan çağırıyor. Ölü kod
    'bu kapı var' yanılsaması üretir — ailenin en pahalı deseninin sahte
    kopyası."""
    assert not hasattr(dd, "_t_beyan_var_mi")
    assert hasattr(dd, "_beyan_var_mi"), "gerçek yardımcı yanlışlıkla silindi"


# ═══════════════════ B-30 — [K] cephanelik bekçisi kör ════════════════════

B30_ATESLEMELI = [
    ("duz", "Davalı, alacağın zamanaşımına uğradığını ileri sürebilecektir."),
    ("madde_atifli", "Davalı, TBK m. 146 uyarınca alacağın zamanaşımına "
                     "uğradığını ileri sürebilir."),
    ("satir_kirikli", "Davalı, alacağın zamanaşımına uğradığını\n"
                      "ileri sürebilecektir."),
    ("defi_bulunabilir", "Davalı, zamanaşımı def'inde bulunabilir."),
    ("uzun_ara", "Karşı taraf, dosyaya sunulan bilirkişi raporundaki hesaplama "
                 "yöntemine ve gün sayısına dayanarak itiraz edebilir."),
    ("idare", "İdarenin, başvurunun süresinde yapılmadığını savunması "
              "muhtemeldir."),
]


@pytest.mark.parametrize("ad,metin", B30_ATESLEMELI, ids=[t[0] for t in B30_ATESLEMELI])
def test_b30_cephanelik_bekcisi_ateslenir(dd, ad, metin):
    """B-30: `[^.\\n]{0,80}` penceresi hem NOKTAYI (madde atfı: 'm. 146') hem
    SATIR SONUNU dışlıyordu; fiil listesi de dardı. Uçtan uca koşuda taslakta
    ihlal varken '[OK] … bulunamadı' basıldı — advisory'nin TEK işlevi
    görünürlüktür, o da üretilmiyordu."""
    assert dd.cephanelik_ifsa_uyarilari(metin), f"{ad}: bekçi ateşlemedi"


B30_ATESLEMESIZ = [
    ("norm_cumle", "Davalı, dava dilekçesine cevap vermiştir."),
    ("kendi_talebimiz", "Müvekkilin alacağının tahsiline karar verilmesini talep ederiz."),
    ("durusma", "Davalı vekili duruşmada hazır bulunmuştur."),
    ("uzak_baglam", "Davalı şirket 2019 yılında kurulmuştur. Bilirkişi raporunda "
                    "yer alan hesaplama yöntemine dayanabilir."),
]


@pytest.mark.parametrize("ad,metin", B30_ATESLEMESIZ, ids=[t[0] for t in B30_ATESLEMESIZ])
def test_b30_cephanelik_yanlis_pozitif_uretmez(dd, ad, metin):
    """B-30 yan etki denetimi: genişletme advisory'yi gürültüye boğmamalı."""
    assert dd.cephanelik_ifsa_uyarilari(metin) == [], f"{ad}: yanlış-pozitif"


# ═══════════════════ B-33 — makbuz şeması sürüklenmesi ════════════════════

def test_b33_makbuz_semasi_belgede_tek_kaynak(tp):
    """B-33: makbuz şeması belgede 11 alan, üretici 17 alan yazıyordu. Makbuz,
    'teslim oldu' sözleşmesinin TEK ölçütüdür ve en az beş yer onu okur; yeni
    bir okuyucu 'belgede yok = yok' varsayabilir. Şema tek kaynağa
    (references/cikti-semasi.md) bağlanır ve bu test sürüklenmeyi kilitler."""
    sema = (SK / "oa-kontrol" / "references" / "cikti-semasi.md").read_text(
        encoding="utf-8")
    import re as _re
    blok = _re.search(r"<!-- makbuz-alanlari:bas -->(.*?)<!-- makbuz-alanlari:son -->",
                      sema, _re.S)
    assert blok, "cikti-semasi.md makbuz alan listesi işaretlerini taşımıyor"
    belgelenen = set(_re.findall(r"^\s*[-*]\s*`([a-z0-9_]+)`", blok.group(1), _re.M))

    class _A:
        tip, taraf, udf_yok = "genel", "", False

    veri = tp._makbuz_taban(_A(), __file__, os.path.dirname(__file__), [], 0,
                            None, "test", sebep="test")
    uretilen = set(veri)
    assert uretilen - belgelenen == set(), (
        "üretici belgede olmayan alan yazıyor: %s" % sorted(uretilen - belgelenen))
    assert belgelenen - uretilen == set(), (
        "belgede olup üreticide olmayan alan: %s" % sorted(belgelenen - uretilen))


def test_b33_yola_ozgu_ek_alanlar_da_belgeli():
    """B-33 (ikinci katman): `ekstra={...}` ile makbuza giren yola-özgü
    alanlar da belgede yaşamalı — sürüklenmenin asıl kaynağı bunlardı."""
    import re as _re
    kaynak = (KONTROL / "teslim_paketi.py").read_text(encoding="utf-8")
    sema = (SK / "oa-kontrol" / "references" / "cikti-semasi.md").read_text(
        encoding="utf-8")
    blok = _re.search(r"<!-- makbuz-ekstra:bas -->(.*?)<!-- makbuz-ekstra:son -->",
                      sema, _re.S)
    assert blok, "cikti-semasi.md ek-alan işaretlerini taşımıyor"
    belgelenen = set(_re.findall(r"^\s*[-*]\s*`([a-z0-9_]+)`", blok.group(1), _re.M))
    uretilen = set()
    for m in _re.finditer(r"ekstra=\{(.*?)\}\)", kaynak, _re.S):
        uretilen |= set(_re.findall(r'"([a-z0-9_]+)":', m.group(1)))
    uretilen.add("erken_cikis")
    assert uretilen - belgelenen == set(), (
        "belgesiz ek alan: %s" % sorted(uretilen - belgelenen))

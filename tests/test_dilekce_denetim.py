# -*- coding: utf-8 -*-
"""oa-dilekce / dilekce_denetim.py için ALTIN VAKA testleri.

Script'i dosya-yolundan (importlib.util) yükler — skill dizinleri paket değildir.
Odak: (D) müvekkil-aleyhi ifade taramasının OLUMSUZLAMA KORUMASI — standart
cevap kalıbı "... kabul anlamına gelmemek kaydıyla" gibi ifadeler SAHTE ALARM
üretmemeli; gerçek bir kabul/ikrar ifadesi ise engel olarak yakalanmalı.
"""
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce" / "scripts" / "dilekce_denetim.py"


def _load():
    assert SCRIPT.is_file(), f"dilekce_denetim.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("dilekce_denetim", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dd = _load()


def _load_udf_yaz():
    yol = SCRIPT.parent / "udf_yaz.py"
    assert yol.is_file(), f"udf_yaz.py bulunamadı: {yol}"
    spec = importlib.util.spec_from_file_location("udf_yaz", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── (D) müvekkil-aleyhi ifade taraması — olumsuzlama koruması ──────────────

def test_gercek_kabul_ifadesi_yakalanir():
    """Gerçek bir kabul/ikrar ifadesi (olumsuzlanmamış) davalı tarafında
    müvekkil-aleyhi sinyal olarak İŞARETLENMELİ."""
    metin = "Davalı olarak davayı kabul ediyoruz ve talebi kabul ediyoruz."
    _eksik, _duzen, _ocr, aleyhe, aleyhe_notu = dd.denetle(metin, "cevap", "davali")
    assert aleyhe, "gerçek kabul ifadesi müvekkil-aleyhi sinyal olarak yakalanmalı"


def test_olumsuzlanmis_kabul_kaydiyla_SAHTE_ALARM_URETMEZ_REGRESYON():
    """REGRESYON: standart cevap kalıbı 'davanın kabulü anlamına gelmemek
    kaydıyla' SAHTE ALARM üretmemeli — bu olumsuzlanmış bir kalıptır, engel
    değil [BİLGİ] notu olmalı."""
    metin = ("İşbu beyanlarımız davanın kabulü anlamına gelmemek kaydıyla, "
             "ihtirazi kayıtla sunulmaktadır. Davayı kabul etmiyoruz.")
    _eksik, _duzen, _ocr, aleyhe, aleyhe_notu = dd.denetle(metin, "cevap", "davali")
    assert not aleyhe, (
        f"REGRESYON: olumsuzlanmış kalıp yanlışlıkla engel sinyali üretti: {aleyhe}")
    assert aleyhe_notu, "olumsuzlanmış kalıp [BİLGİ] notuna düşmeli (sessizce yutulmamalı)"


def test_davaci_feragat_ifadesi_yakalanir():
    metin = "Davacı olarak iddiamızdan vazgeçiyoruz."
    _eksik, _duzen, _ocr, aleyhe, _notu = dd.denetle(metin, "dava", "davaci")
    assert aleyhe


def test_sanik_ikrar_olumsuzlanmissa_engel_degil():
    metin = "Sanık olarak suçu kabul etmiyoruz; isnat edilen fiili işlemedik."
    _eksik, _duzen, _ocr, aleyhe, aleyhe_notu = dd.denetle(metin, "genel", "sanik")
    assert not aleyhe
    assert aleyhe_notu


def test_davali_dogrudur_ifadesi_yakalanir():
    """Davalı için 'doğrudur' kabul ekseni — olumsuzlanmamışsa engel sinyali olmalı."""
    metin = "Bu husus doğrudur, davayı kabul ediyoruz."
    _eksik, _duzen, _ocr, aleyhe, _notu = dd.denetle(metin, "cevap", "davali")
    assert aleyhe, "davalı 'doğrudur' kabul ekseni yakalanmalı"


def test_davali_dogrudur_olumsuzlanmissa_engel_degil():
    metin = "Doğrudur, ancak davayı kabul etmiyoruz."
    _eksik, _duzen, _ocr, aleyhe, aleyhe_notu = dd.denetle(metin, "cevap", "davali")
    assert not aleyhe
    assert aleyhe_notu


def test_musteki_sikayetten_vazgecme_yakalanir():
    """Müşteki/katılan için şikayetten vazgeçme-uzlaşma ekseni yakalanmalı."""
    metin = "Müşteki olarak şikayetimizi geri alıyoruz."
    _eksik, _duzen, _ocr, aleyhe, _notu = dd.denetle(metin, "genel", "musteki")
    assert aleyhe, "müşteki şikayetten vazgeçme ifadesi yakalanmalı"


def test_katilan_musteki_ile_ayni_kalip_setini_kullanir():
    """Katılan usulen müştekinin devamıdır — aynı riskli eksenle taranmalı."""
    metin = "Katılan olarak şikayetimizi geri alıyoruz."
    _eksik, _duzen, _ocr, aleyhe, _notu = dd.denetle(metin, "genel", "katilan")
    assert aleyhe


def test_musteki_sikayetten_vazgecme_olumsuzlanmissa_engel_degil():
    metin = ("Müşteki olarak şikayetimizi geri almış değiliz; şikayetçiyiz, "
             "kovuşturmaya devam edilmesini talep ediyoruz.")
    _eksik, _duzen, _ocr, aleyhe, aleyhe_notu = dd.denetle(metin, "genel", "musteki")
    assert not aleyhe
    assert aleyhe_notu


def test_davaci_talebimizden_vazgecme_yakalanir():
    """Görev tanımında açıkça istenen davacı kalıbı: 'talebimizden vazgeçiyoruz'."""
    metin = "Davacı olarak talebimizden vazgeçiyoruz."
    _eksik, _duzen, _ocr, aleyhe, _notu = dd.denetle(metin, "dava", "davaci")
    assert aleyhe


# ── EK-FİX (risk#2): kalıbın KENDİ 'değil' gövdesi sahte-olumsuzlama sayılmamalı ──

def test_sikayetci_degil_duz_cumlede_ARTIK_BLOKLAR_REGRESYON():
    """REGRESYON: eski kod, aleyhe eşleşmesinin (m.start()..m.end()) KENDİSİNİ de
    NEG penceresine dahil ediyordu. 'şikayetçi değil' kalıbının gövdesi 'değil'
    kelimesini TAŞIDIĞI için NEG deseni eşleşmenin İÇİNDE hep bulunuyor, bu kalıp
    düz bir cümlede bile ASLA bloklamıyor, hep [BİLGİ]'ye düşüyordu. Artık pencere
    yalnız eşleşmenin ÖNCESİ/SONRASI olduğundan, gerçek bir olumsuzlama-eki
    olmayan düz kullanım BLOKLAMALI (engel sinyali)."""
    metin = "Müvekkilimiz şikayetçi değil, dosyaya yeni delil sunmaktadır."
    _eksik, _duzen, _ocr, aleyhe, aleyhe_notu = dd.denetle(metin, "genel", "musteki")
    assert aleyhe, (
        f"REGRESYON: 'şikayetçi değil' düz cümlede BLOKLAMADI (eski hata geri geldi): "
        f"aleyhe={aleyhe} notu={aleyhe_notu}")


def test_hakli_degiliz_duz_cumlede_ARTIK_BLOKLAR_REGRESYON():
    """Aynı regresyon sınıfı: 'haklı değiliz' kalıbı da 'değil' gövdesini taşır;
    düz bir cümlede gerçek olumsuzlama-ekiyle çevrelenmediği sürece BLOKLAMALI."""
    metin = "Bu davada haklı değiliz, ancak kısmi taleplerimiz mevcuttur."
    _eksik, _duzen, _ocr, aleyhe, aleyhe_notu = dd.denetle(metin, "dava", "davaci")
    assert aleyhe, (
        f"REGRESYON: 'haklı değiliz' düz cümlede BLOKLAMADI (eski hata geri geldi): "
        f"aleyhe={aleyhe} notu={aleyhe_notu}")


def test_sikayetci_degil_gercek_olumsuzlama_ile_cevriliyse_hala_bilgiye_duser():
    """Kontrast: kalıbın KENDİSİ dışında, penceresinde GERÇEK bir olumsuzlama-eki
    varsa (ör. 'demek/anlamına gelmemek kaydıyla') sinyal hâlâ [BİLGİ]'ye düşmeli
    — fix yalnız kalıbın KENDİ 'değil'ini pencereden çıkardı, dış olumsuzlamayı
    yakalama yeteneğini bozmadı."""
    metin = "Müvekkilimiz şikayetçi değil demek anlamına gelmemek kaydıyla beyanda bulunmaktadır."
    _eksik, _duzen, _ocr, aleyhe, aleyhe_notu = dd.denetle(metin, "genel", "musteki")
    assert not aleyhe, f"gerçek olumsuzlama varken engel sinyali üretilmemeli: {aleyhe}"
    assert aleyhe_notu


# ── [B] TERTİP/DÜZEN — zorunlu unsurların tip'ten BAĞIMSIZ mekanik varlık denetimi ──

def test_duzen_tip_ozel_listede_olmayan_unsur_ayrica_yakalanir():
    """İstinaf tipinin kendi özel listesi 'Konu'/'Deliller' aramaz; [B] katmanı bunları
    tip'ten bağımsız olarak ayrıca yakalamalı (mekanik VARLIK denetimi, hüküm değil)."""
    metin = (
        "# Bölge Adliye Mahkemesi Başkanlığına\n\n"
        "İstinaf eden: Ahmet ...\n\n"
        "İlk derece esas no: 2024/1 karar no: 2024/2\n\n"
        "İstinaf sebepleri: hukuka aykırı karar verilmiştir.\n\n"
        "Netice-i talep: kaldırılmasını talep ederiz.\n\n"
        "Tebliğ tarihi ... iki hafta içinde ...\n\n"
        "01.01.2026\nimza\nAv. Vekil\n"
    )
    eksik, duzen_eksik, _ocr, _aleyhe, _notu = dd.denetle(metin, "istinaf", "davaci")
    assert not eksik, f"istinaf tip-özel liste için eksik olmamalı: {eksik}"
    assert "Konu" in duzen_eksik
    assert "Deliller" in duzen_eksik


def test_duzen_tam_dilekcede_temiz_gecis():
    """Sekiz zorunlu unsurun tamamı mevcutsa [B] TERTİP-DÜZEN temiz geçmeli."""
    metin = (
        "# Denizli 3. İş Mahkemesi Başkanlığına\n\n"
        "## Taraflar\n"
        "Davacı: Ahmet Yılmaz, Adres: ...\n"
        "Davalı: XYZ A.Ş., Adres: ...\n"
        "Vekil: Av. Test Vekil\n\n"
        "## Konu\n"
        "İşçilik alacaklarına ilişkindir.\n\n"
        "## Açıklamalar\n"
        "1. Davacının işe giriş vakıası.\n"
        "2. İkinci vakıa.\n\n"
        "## Hukuki Sebepler\n"
        "4857 sayılı Kanun ve ilgili hukuki dayanaklar.\n\n"
        "## Deliller\n"
        "Tanık, bilirkişi incelemesi, bordro.\n\n"
        "## Netice-i Talep\n"
        "Yukarıda açıklanan nedenlerle davanın kabulüne karar verilmesini saygıyla talep ederiz.\n\n"
        "01.01.2026\nAv. Test Vekil\nimza\n"
    )
    eksik, duzen_eksik, _ocr, aleyhe, _notu = dd.denetle(metin, "dava", "davaci")
    assert not eksik, f"beklenmedik eksik: {eksik}"
    assert not duzen_eksik, f"tam dilekçede tertip-düzen eksiği olmamalı: {duzen_eksik}"
    assert not aleyhe, f"temiz dilekçede aleyhe sinyal çıkmamalı: {aleyhe}"


# ── [B2] KANUN-YOLU (istinaf/temyiz) YAPISAL KALEMLERİ — M3-2 ──────────────

KANUN_YOLU_TAM = (
    "# Bölge Adliye Mahkemesi 3. Hukuk Dairesi Başkanlığına\n\n"
    "## GİRİŞ\n"
    "İlk derece mahkemesi kararı iki taşıyıcı dayanağa indirgenmektedir.\n\n"
    "## Taraflar\n"
    "Davacı: Ahmet Yılmaz\nDavalı: XYZ A.Ş.\nVekil: Av. Test Vekil\n\n"
    "İlk derece esas no: 2024/10 karar no: 2024/20 sayılı ilk derece "
    "kararında davanın reddine karar verilmiştir.\n\n"
    "Dava konusu işlemin dayanağı 4857 sayılı Kanun m. 20'dir.\n\n"
    "Tebliğ tarihi: 01.01.2026\n\n"
    "## Konu\nİşçilik alacaklarına ilişkindir.\n\n"
    "## Açıklamalar\n1. Birinci vakıa.\n\n"
    "## İstinaf Sebepleri\nHukuka aykırı karar verilmiştir.\n\n"
    "## Hukuki Sebepler\nHMK ve ilgili mevzuat.\n\n"
    "## Deliller\nTanık, bilirkişi.\n\n"
    "## Netice-i Talep\n"
    "1. Kararın kaldırılmasına,\n"
    "2. Yargılama giderlerinin karşı tarafa yükletilmesine karar verilmesini "
    "saygıyla talep ederiz.\n\n"
    "01.01.2026\nAv. Test Vekil\nimza\n"
)

KANUN_YOLU_EKSIK = (
    "# Bölge Adliye Mahkemesi Başkanlığına\n\n"
    "İstinaf eden: Ahmet ...\n\n"
    "İlk derece esas no: 2024/1 karar no: 2024/2\n\n"
    "İstinaf sebepleri: hukuka aykırı karar verilmiştir.\n\n"
    "Netice-i talep: kaldırılmasını talep ederiz.\n\n"
    "01.01.2026\nimza\nAv. Vekil\n"
)


def test_kanun_yolu_kalemleri_istinaf_tipinde_eksikse_yakalanir():
    """--tip istinaf iken B1/B2/B4/B6 mekanik kalemleri (künye alan seti,
    TEBLİĞ TARİHİ ayrı satır, GİRİŞ, numaralı SONUÇ) eksikse [B]'ye eklenmeli."""
    _eksik, duzen_eksik, _ocr, _aleyhe, _notu = dd.denetle(KANUN_YOLU_EKSIK, "istinaf", "davaci")
    birlesik = " | ".join(duzen_eksik)
    assert "TEBLİĞ TARİHİ" in birlesik
    assert "GİRİŞ" in birlesik
    assert "Numaralı SONUÇ/İSTEM" in birlesik


def test_kanun_yolu_kalemleri_temyiz_tipinde_de_uygulanir():
    """Kapsam yalnız istinaf'a değil, temyiz tipine de uygulanır."""
    _eksik, duzen_eksik, _ocr, _aleyhe, _notu = dd.denetle(KANUN_YOLU_EKSIK, "temyiz", "davaci")
    birlesik = " | ".join(duzen_eksik)
    assert "GİRİŞ" in birlesik


def test_kanun_yolu_kalemleri_dava_tipinde_UYGULANMAZ():
    """G1 gibi tip-koşullu: --tip dava/cevap/genel/aym_bireysel gibi kanun-yolu
    OLMAYAN tiplerde B1/B2/B4/B6 kalemleri hiç eklenmemeli (aynı eksik metin,
    tip='dava' olunca kanun-yolu etiketli kalemler duzen_eksik'te GÖRÜNMEMELİ)."""
    _eksik, duzen_eksik, _ocr, _aleyhe, _notu = dd.denetle(KANUN_YOLU_EKSIK, "dava", "davaci")
    birlesik = " | ".join(duzen_eksik)
    assert "GİRİŞ" not in birlesik
    assert "TEBLİĞ TARİHİ" not in birlesik
    assert "Numaralı SONUÇ/İSTEM" not in birlesik


def test_kanun_yolu_kalemleri_tam_dilekcede_eksik_cikmiyor():
    """Tüm B1/B2/B4/B6 kalemleri mevcut kanun-yolu dilekçesinde [B2] eksik
    listesine hiçbir yeni kalem eklenmemeli."""
    _eksik, duzen_eksik, _ocr, _aleyhe, _notu = dd.denetle(KANUN_YOLU_TAM, "istinaf", "davaci")
    birlesik = " | ".join(duzen_eksik)
    assert "B1 Künye" not in birlesik
    assert "GİRİŞ" not in birlesik
    assert "Numaralı SONUÇ/İSTEM" not in birlesik
    assert "B4" not in birlesik


def test_tebligi_tarihi_gomulu_cumle_icinde_ayri_satir_sayilmaz():
    """B1 sık atlanan hata: tebliğ tarihinin bir cümlenin ORTASINA gömülmesi
    'ayrı satır' zorunluluğunu KARŞILAMAZ — mekanik kapı bunu yakalamalı."""
    metin = (
        "# BAM Başkanlığına\n\n## GİRİŞ\nKarar indirgenmektedir.\n\n"
        "İlk derece esas no: 2024/1 karar no: 2024/2 sayılı kararında davanın "
        "reddine karar verilmiş olup bu karar tarafımıza tebliğ tarihi olan "
        "01.01.2026'da tebliğ edilmiştir, dayanak 4857 sayılı Kanun m.20'dir.\n\n"
        "## Netice-i Talep\n1. Kaldırılmasına karar verilmesini talep ederiz.\n\n"
        "01.01.2026\nimza\nAv. Vekil\n"
    )
    _eksik, duzen_eksik, _ocr, _aleyhe, _notu = dd.denetle(metin, "istinaf", "davaci")
    assert any("TEBLİĞ TARİHİ" in u for u in duzen_eksik)


def test_giris_bolumu_var_mi_baslik_taniyor():
    assert dd._giris_bolumu_var_mi("# BAM\n\n## GİRİŞ\nİçerik.\n") is True
    assert dd._giris_bolumu_var_mi("# BAM\n\nGiriş niteliğinde bir cümle.\n") is False


def test_sonuc_numarali_mi_numarasiz_ise_false():
    assert dd._sonuc_numarali_mi("Netice-i Talep\nKabulüne karar verilmesini talep ederiz.\n") is False
    assert dd._sonuc_numarali_mi("Netice-i Talep\n1. Kabulüne karar verilmesini talep ederiz.\n") is True


def test_alinti_aciklama_denetle_aciklamasiz_alinti_yakalanir():
    metin = "## İçtihat\n> Karardan birebir alıntı.\n\n## Sonraki Bölüm\nBaşka içerik.\n"
    toplam, eksik = dd._alinti_aciklama_denetle(metin)
    assert toplam == 1
    assert eksik == 1


def test_alinti_aciklama_denetle_aciklamali_alinti_temiz():
    metin = ("## İçtihat\n> Karardan birebir alıntı.\n\n"
             "Bu karar, somut olaya uygulandığında ... sonucunu ortaya koymaktadır.\n")
    toplam, eksik = dd._alinti_aciklama_denetle(metin)
    assert toplam == 1
    assert eksik == 0


def test_alinti_aciklama_denetle_alinti_yoksa_sifir_sifir():
    metin = "Bu metinde hiç blok alıntı yok, düz metin var.\n"
    toplam, eksik = dd._alinti_aciklama_denetle(metin)
    assert (toplam, eksik) == (0, 0)


def test_kanun_yolu_alinti_aciklamasiz_ise_duzen_eksige_eklenir():
    """KANUN_YOLU_TAM'ın diğer tüm kalemleri temiz kalırken, yalnız İstinaf
    Sebepleri bölümüne açıklamasız bırakılan bir blok-alıntı eklenir — [B2]
    yalnız bu YENİ eksiği yakalamalı, diğerlerini bozmamalı."""
    metin = KANUN_YOLU_TAM.replace(
        "## İstinaf Sebepleri\nHukuka aykırı karar verilmiştir.\n\n",
        "## İstinaf Sebepleri\n> Karardan birebir alıntı.\n\n## Hukuki Sebepler\n",
    )
    _eksik, duzen_eksik, _ocr, _aleyhe, _notu = dd.denetle(metin, "istinaf", "davaci")
    assert any("B4" in u and "açıklama" in u for u in duzen_eksik), duzen_eksik


# ── [F] --tip pass-through — G1 esaslı-dilekçe tip listesi (M3-2/R6) ────────

def test_ictihat_muhakeme_kapisi_tip_ile_esasli_olmayanda_uyari_bilgiye_duser(tmp_path):
    """dilekce_denetim ictihat_muhakeme_kapisi()'nin --tip'i kardeş scripte
    aktardığının uçtan-uca kanıtı: tip='yemin' iken hiç atıf yoksa G1
    [UYARI] değil [BİLGİ] olarak basılmalı (yine bloklamaz, exit 0)."""
    dokum_dizin = tmp_path / "_oa" / "teyit" / "dokum"
    dokum_dizin.mkdir(parents=True)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True)
    taslak = tmp_path / "taslak.md"
    taslak.write_text("Bu dilekçe hiçbir içtihat atfı içermemektedir.\n", encoding="utf-8")

    kod_esasli, cikti_esasli = dd.ictihat_muhakeme_kapisi(
        str(taslak), kok=str(tmp_path), tip="dava")
    kod_hafif, cikti_hafif = dd.ictihat_muhakeme_kapisi(
        str(taslak), kok=str(tmp_path), tip="yemin")

    assert kod_esasli == 0 and kod_hafif == 0
    assert "[UYARI]" in cikti_esasli
    assert "[BİLGİ]" in cikti_hafif
    assert "[UYARI] Dilekçede esas/karar" not in cikti_hafif


# ── zorunlu unsur + OCR şerhi (dumb ama temel golden vaka) ──────────────────

def test_eksik_unsur_tip_dava_icin_tespit_edilir():
    metin = "Kısa bir metin, hiçbir zorunlu unsuru içermiyor."
    eksik, _duzen, _ocr, _aleyhe, _notu = dd.denetle(metin, "dava", "davaci")
    assert eksik, "zorunlu unsurlar eksikken 'eksik' listesi boş dönmemeli"


def test_ocr_isaretli_alinti_teyit_serhsiz_uyari_uretir():
    metin = "Kararda ⚠ OCR şüpheli bir rakam geçmektedir."
    _eksik, _duzen, ocr_uyari, _aleyhe, _notu = dd.denetle(metin, "genel", "")
    assert ocr_uyari is True


def test_ocr_isaretli_alinti_teyit_serhliyse_uyari_yok():
    metin = "Kararda ⚠ OCR şüpheli bir rakam geçmektedir; rakam orijinalinden teyit edilmiştir."
    _eksik, _duzen, ocr_uyari, _aleyhe, _notu = dd.denetle(metin, "genel", "")
    assert ocr_uyari is False


# ── [E] UDF GEÇERLİLİK KAPISI — udf_kapisi() / udf_yaz.py entegrasyonu ──────

def test_udf_kapisi_gecerli_udf_icin_gecerli_doner(tmp_path):
    """udf_kapisi, kardeş script udf_yaz.py'yi yükleyip udf_dogrula'yı çağırır;
    düzgün üretilmiş bir UDF için GEÇERLİ dönmeli (denetim hattı bağlantısı)."""
    uy = _load_udf_yaz()
    xml_str, _tam, _p = uy.udf_uret("# Dava Dilekçesi\n\nArz ederiz.\n")
    cikti = tmp_path / "gecerli.udf"
    uy.udf_yaz(str(cikti), xml_str)

    sonuc = dd.udf_kapisi(str(cikti))
    assert sonuc["gecerli"] is True
    assert sonuc["hatalar"] == []


def test_udf_kapisi_bozuk_udf_icin_gecersiz_doner(tmp_path):
    sahte = tmp_path / "bozuk.udf"
    sahte.write_bytes(b"zip degil")
    sonuc = dd.udf_kapisi(str(sahte))
    assert sonuc["gecerli"] is False
    assert sonuc["hatalar"]


def test_main_udf_bayragi_gecersiz_udf_ile_engel_uretir(tmp_path, capsys):
    """CLI ucu: --udf ile geçersiz bir UDF verilirse [E] bölümü basılmalı ve
    genel SONUÇ engellenmeli (exit 1) — UDF-VARSAYILAN doktrininin mekanik kapısı."""
    taslak = tmp_path / "taslak.md"
    taslak.write_text(
        "# Mahkeme Başkanlığına\n\nDavacı: Ahmet ...\nDavalı: Mehmet ...\n\n"
        "## Açıklamalar\n1. Vak'a bir.\n\n## Hukuki Sebepler\nHMK.\n\n"
        "## Deliller\nTanık.\n\n## Netice-i Talep\nKabulünü talep ederiz.\n\n"
        "01.01.2026\nAv. Test Vekil\nimza\n",
        encoding="utf-8",
    )
    sahte_udf = tmp_path / "gecersiz.udf"
    sahte_udf.write_bytes(b"zip degil")

    argv_yedek = sys.argv
    sys.argv = ["dilekce_denetim.py", str(taslak), "--tip", "dava", "--taraf", "davaci",
                "--udf", str(sahte_udf)]
    try:
        with pytest.raises(SystemExit) as exc:
            dd.main()
    finally:
        sys.argv = argv_yedek

    assert exc.value.code == 1
    cikti = capsys.readouterr().out
    assert "[E] UDF GEÇERLİLİK KAPISI" in cikti
    assert "GEÇERSİZ" in cikti


# ── [F] İÇTİHAT MUHAKEME ZİNCİRİ KAPISI — dilekce_denetim ↔ oa-kontrol bağlantısı (M2-3) ──

KUNYE_F = "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023"
TASLAK_ICTIHATLI = (
    "# Mahkeme Başkanlığına\n\nDavacı: Ahmet ...\nDavalı: Mehmet ...\n\n"
    "## Konu\nİşçilik alacakları.\n\n"
    "## Açıklamalar\n1. Somut olayda Yargıtay 4. HD'nin E. 2023/1234 K. 2023/5678 "
    "sayılı kararı emsal teşkil etmektedir.\n\n## Hukuki Sebepler\nHMK.\n\n"
    "## Deliller\nTanık.\n\n## Netice-i Talep\nKabulünü talep ederiz.\n\n"
    "01.01.2026\nAv. Test Vekil\nimza\n"
)


def _f_kur(tmp_path, damga="LEHE", ayirt_etme=""):
    """[F] için _oa/teyit/dokum + _oa/cikti/*ictihat-muhakeme*.md iskeleti kurar;
    taslak dosya yolunu döndürür."""
    dokum_dizin = tmp_path / "_oa" / "teyit" / "dokum"
    dokum_dizin.mkdir(parents=True)
    cikti_dizin = tmp_path / "_oa" / "cikti"
    cikti_dizin.mkdir(parents=True)
    (dokum_dizin / "kaynak.md").write_text(
        "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678 sayılı kararın tam metni "
        "burada yer almaktadır...\n",
        encoding="utf-8",
    )
    satirlar = [
        "# 01 — İçtihat Muhakeme Kaydı", "",
        f"**KUNYE:** {KUNYE_F}",
        "**KAYNAK-IZI:** _oa/teyit/dokum/kaynak.md",
        f"**DAMGA:** {damga}", "",
        "## İLGİLİ-KISIM", "...ilgili kısım metni...", "",
        "## DAVAYA-BAĞ", "...davaya bağ açıklaması...", "",
        "## AYIRT-ETME", ayirt_etme, "",
    ]
    (cikti_dizin / "01-ictihat-muhakeme.md").write_text("\n".join(satirlar), encoding="utf-8")

    taslak = tmp_path / "taslak.md"
    taslak.write_text(TASLAK_ICTIHATLI, encoding="utf-8")
    return taslak


def test_ictihat_muhakeme_kapisi_lehe_temiz_engel_uretmez(tmp_path):
    """[F] fonksiyon-seviyesi: DAMGA=LEHE + tam alanlı kayıt → exit 0, [BLOK] yok."""
    taslak = _f_kur(tmp_path, damga="LEHE")
    kod, cikti = dd.ictihat_muhakeme_kapisi(str(taslak), kok=str(tmp_path))
    assert kod == 0, cikti
    assert "[BLOK]" not in cikti


def test_ictihat_muhakeme_kapisi_aleyhe_engel_uretir(tmp_path):
    """[F] fonksiyon-seviyesi: DAMGA=ALEYHE → exit 1 (anayasa m.6)."""
    taslak = _f_kur(tmp_path, damga="ALEYHE")
    kod, cikti = dd.ictihat_muhakeme_kapisi(str(taslak), kok=str(tmp_path))
    assert kod == 1, cikti
    assert "ALEYHE" in cikti


def test_main_ictihat_muhakeme_bayragi_kapali_ise_f_bolumu_hic_calismaz(tmp_path):
    """Bayrak verilmezse [F] hiç çalışmaz — mevcut A-E davranışı bozulmaz (geriye uyum)."""
    taslak = _f_kur(tmp_path, damga="ALEYHE")  # ALEYHE olsa bile --ictihat-muhakeme YOK

    argv_yedek = sys.argv
    sys.argv = ["dilekce_denetim.py", str(taslak), "--tip", "dava", "--taraf", "davaci"]
    try:
        with pytest.raises(SystemExit) as exc:
            dd.main()
    finally:
        sys.argv = argv_yedek

    assert exc.value.code == 0, "flag verilmezse [F] hiç tetiklenmemeli; ALEYHE kaydı bloklamamalı"


def test_main_ictihat_muhakeme_bayragi_ile_aleyhe_teslim_engeli_uretir(tmp_path, capsys):
    """CLI ucu: --ictihat-muhakeme --kok ile ALEYHE damgalı kayıt genel SONUCU engellemeli
    (exit 1) — mekanik kapılar zincirine YENİ yeşil ışık [F] eklendiğinin uçtan uca kanıtı."""
    taslak = _f_kur(tmp_path, damga="ALEYHE")

    argv_yedek = sys.argv
    sys.argv = ["dilekce_denetim.py", str(taslak), "--tip", "dava", "--taraf", "davaci",
                "--ictihat-muhakeme", "--kok", str(tmp_path)]
    try:
        with pytest.raises(SystemExit) as exc:
            dd.main()
    finally:
        sys.argv = argv_yedek

    assert exc.value.code == 1
    cikti = capsys.readouterr().out
    assert "[F] İÇTİHAT MUHAKEME ZİNCİRİ KAPISI" in cikti
    assert "ALEYHE" in cikti


def test_main_ictihat_muhakeme_bayragi_ile_lehe_temiz_gecer(tmp_path, capsys):
    """Kontrast: LEHE + tam alanlı kayıtta [F] engel üretmemeli; diğer bölümler
    (A-E) zaten temizse genel sonuç da temiz olmalı."""
    taslak_yolu = _f_kur(tmp_path, damga="LEHE")

    argv_yedek = sys.argv
    sys.argv = ["dilekce_denetim.py", str(taslak_yolu), "--tip", "dava", "--taraf", "davaci",
                "--ictihat-muhakeme", "--kok", str(tmp_path)]
    try:
        with pytest.raises(SystemExit) as exc:
            dd.main()
    finally:
        sys.argv = argv_yedek

    cikti = capsys.readouterr().out
    assert "[F] İÇTİHAT MUHAKEME ZİNCİRİ KAPISI" in cikti
    assert exc.value.code == 0, cikti

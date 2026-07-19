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

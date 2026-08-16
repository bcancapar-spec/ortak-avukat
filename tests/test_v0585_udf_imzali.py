# -*- coding: utf-8 -*-
"""v0.5.8.5 B6+B7 — İMZALI-NÜSHA PROFİLİ + MAKBUZ GARANTİSİ (udf_yaz.py).

B6 (İMZALI-NÜSHA PROFİLİ): `udf_dogrula` zip'te `sign.sgn` girdisi görünce
sonuçta `imzali_nusha=True` döner ve YALNIZ bu profilde editör-kaynaklı dört
sapma sınıfı GEÇERSİZLİK sebebi SAYILMAZ:
  (a) float kenar değerleri (14.170000000000032 gibi),
  (b) prolog öncesi fazla boşluk/satır,
  (c) zip data-descriptor bayrağı,
  (d) offset döşemesinde 1-boşluk sınıfı sapma (TEK küçük boşluk toleransı).
Gerekçe (v0.5.5.2 dersinin devamı — resmî gerçeklik > bizim varsayım): gerçek
e-imzalı, mahkemece KABUL edilmiş bir dosyada 1 boşluk sapması ÖLÇÜLDÜ; katı
kural o gerçek-geçerli dosyayı yanlış-BLOK'lardı. İMZASIZ dosyada tolerans
YOK — katı invaryant aynen sürer (katılık kanıtı testleri aşağıda).

B7 (MAKBUZ GARANTİSİ): `_uretim_makbuzu_yaz` artık "defter yoksa sessiz atla"
değil — `_oa` dizini VARSA `_oa/defter`i makedirs ile KURAR ve yazar; `_oa`
da yoksa sessiz atlama sürer. Hiçbir hata üretimi kırmaz (asla-fırlatmaz
sözleşmesi korunur).

Ek: istisna defteri ortak şeması — tolerans uygulanınca
`_oa/defter/istisna-kayitlari.jsonl`e `tur="dogrulama-toleransi"` satırı düşer.

Tamamen ağsız/deterministik: resmî okuyucu bacağı ya `resmi_okuyucu=False`
ile kapalı ya monkeypatch ile yalıtılmış; tüm veriler sentetiktir (tmp_path —
gerçek dava numarası/kişi adı/klasör yolu YOK; "2024/123 Esas" uydurmadır).
"""
import importlib.util
import json
import pathlib
import sys
import zipfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SK = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce" / "scripts"


def _yukle(ad, modul_adi):
    yol = SK / (ad + ".py")
    assert yol.is_file(), f"{ad}.py bulunamadı: {yol}"
    spec = importlib.util.spec_from_file_location(modul_adi, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


uy = _yukle("udf_yaz", "_v0585_udf_yaz")

HVL_STIL = '<style name="hvl-default" family="Times New Roman" size="12"/>'


def _veri_tanimlayici_bayragi_koy(yol):
    """Zip genel-amaç bayrağının 3. bitini (data descriptor) hem yerel
    başlıklarda hem merkez dizin girdilerinde işaretler — UYAP editörünün
    akış (streaming) zip yazıcısının bıraktığı izi taklit eder. Girdiler
    ZIP_STORED yazıldığından gövde içinde sahte 'PK' imzası yoktur."""
    veri = bytearray(pathlib.Path(yol).read_bytes())
    for imza, bayrak_ofseti in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
        i = 0
        while True:
            i = veri.find(imza, i)
            if i < 0:
                break
            veri[i + bayrak_ofseti] |= 0x08
            i += len(imza)
    pathlib.Path(yol).write_bytes(bytes(veri))


def _sentetik_udf(yol, imzali=False, prolog_bosluklu=False, float_kenar=False,
                  veri_tanimlayici=False, kuyruk=""):
    """Sentetik UDF üretir (tmp_path — hepsi uydurma). `kuyruk` CDATA sonuna
    HİÇBİR offset elemanının kaplamadığı ek karakter(ler) koyar: " " tek
    boşluk (ölçülen gerçek editör sapması), "X" metin kaybı, "  " çift boşluk."""
    satirlar = ["Sentetik başlık satırı.", "2024/123 Esas — arz ederiz."]
    parcalar = [s + "\n" for s in satirlar]
    tam = "".join(parcalar) + kuyruk
    kenar = "14.170000000000032" if float_kenar else "42.52"
    x = []
    if prolog_bosluklu:
        # prolog ÖNCESİ fazla satır/boşluk — katı XML parser'da ParseError
        x.append("")
        x.append("   ")
    x.append('<?xml version="1.0" encoding="UTF-8"?>')
    x.append('<template format_id="1.8">')
    x.append('<content><![CDATA[' + tam + ']]></content>')
    x.append('<properties><pageFormat mediaSizeName="1" leftMargin="%s" '
             'rightMargin="%s" topMargin="%s" bottomMargin="%s" '
             'paperOrientation="1"/></properties>' % (kenar, kenar, kenar, kenar))
    x.append('<elements resolver="hvl-default">')
    imlec = 0
    for parca in parcalar:
        u16 = uy.utf16_uzunluk(parca)
        x.append('<paragraph Alignment="3"><content startOffset="%d" '
                 'length="%d"/></paragraph>' % (imlec, u16))
        imlec += u16
    x.append('</elements>')
    x.append('<styles>%s</styles>' % HVL_STIL)
    x.append('</template>')
    xml_str = "\n".join(x) + "\n"
    with zipfile.ZipFile(str(yol), "w", zipfile.ZIP_STORED) as z:
        z.writestr("content.xml", xml_str.encode("utf-8"))
        if imzali:
            z.writestr("sign.sgn", b"\x30\x82sentetik-imza-baytlari")
    if veri_tanimlayici:
        _veri_tanimlayici_bayragi_koy(str(yol))
    return str(yol)


# ── B6.1 — imzalı-nüsha TANIMA ──────────────────────────────────────────────

def test_imzali_nusha_tespit_edilir(tmp_path):
    """sign.sgn'li zip → imzali_nusha=True; imzasız → False. Temiz dosyada
    her iki profil de GEÇERLİ (profil, geçerli dosyayı değiştirmez)."""
    imzali = _sentetik_udf(tmp_path / "imzali.udf", imzali=True)
    imzasiz = _sentetik_udf(tmp_path / "imzasiz.udf", imzali=False)
    s1 = uy.udf_dogrula(imzali, resmi_okuyucu=False)
    s2 = uy.udf_dogrula(imzasiz, resmi_okuyucu=False)
    assert s1["imzali_nusha"] is True
    assert s1["imza_dosyasi"] == "sign.sgn"
    assert s1["gecerli"] is True
    assert s2["imzali_nusha"] is False
    assert s2["gecerli"] is True


# ── B6.2 — imzalı profilde editör sapmaları GEÇERLİLİĞİ BOZMAZ ──────────────

def test_imzali_editor_sapmalari_gecerliligi_bozmaz(tmp_path):
    """Dört sapma sınıfı BİRDEN (float kenar + prolog boşluğu + data-descriptor
    bayrağı + 1-boşluk döşeme sapması) imzalı nüshada GEÇERLİ kalır — gerçek
    e-imzalı, mahkemece kabul edilmiş dosya sınıfı yanlış-BLOK'lanmaz."""
    yol = _sentetik_udf(tmp_path / "imzali-sapmali.udf", imzali=True,
                        prolog_bosluklu=True, float_kenar=True,
                        veri_tanimlayici=True, kuyruk=" ")
    s = uy.udf_dogrula(yol, resmi_okuyucu=False)
    assert s["imzali_nusha"] is True
    assert s["hatalar"] == [], "imzalı profilde editör sapmaları hata OLMAMALI"
    assert s["gecerli"] is True
    assert s["xml_iyi_bicimli"] is True
    assert s["offsetler_tutarli"] is True
    # toleranslar SESSİZ değil: sonuçta görünür iz bırakır
    assert s["imzali_tolerans"], "uygulanan tolerans sonuçta görünür olmalı"


def test_ayni_sapmalar_imzasizda_GECERSIZ(tmp_path):
    """KATILIK KANITI: birebir aynı sapmalar imzasız dosyada GEÇERSİZ —
    tolerans yalnız imzalı-nüsha profiline aittir, genel gevşeme değildir."""
    yol = _sentetik_udf(tmp_path / "imzasiz-sapmali.udf", imzali=False,
                        prolog_bosluklu=True, float_kenar=True,
                        veri_tanimlayici=True, kuyruk=" ")
    s = uy.udf_dogrula(yol, resmi_okuyucu=False)
    assert s["imzali_nusha"] is False
    assert s["gecerli"] is False
    assert s["hatalar"]
    # ilk düşen kapı: prolog boşluğu katı parser'da iyi-biçimliliği bozar
    assert s["xml_iyi_bicimli"] is False


# ── B6.3 — 1-boşluk döşeme sapması: imzalıda tolere, imzasızda RED ──────────

def test_tek_bosluk_sapmasi_imzalida_tolere_imzasizda_red(tmp_path):
    """Ölçülen gerçek saha sapması tek başına: CDATA sonunda hiçbir elemanın
    kaplamadığı TEK boşluk. İmzalıda tolere (görünür notla), imzasızda RED."""
    imzali = _sentetik_udf(tmp_path / "i1.udf", imzali=True, kuyruk=" ")
    imzasiz = _sentetik_udf(tmp_path / "i2.udf", imzali=False, kuyruk=" ")
    s1 = uy.udf_dogrula(imzali, resmi_okuyucu=False)
    s2 = uy.udf_dogrula(imzasiz, resmi_okuyucu=False)
    assert s1["gecerli"] is True
    assert s1["offsetler_tutarli"] is True
    assert any("boşluk" in t for t in s1["imzali_tolerans"])
    assert s2["gecerli"] is False
    assert s2["offsetler_tutarli"] is False
    assert any("uyuşmuyor" in h for h in s2["hatalar"])


def test_prolog_boslugu_imzalida_tolere_imzasizda_red(tmp_path):
    """Prolog öncesi fazla boşluk/satır tek başına: imzalıda parse kurtarılır
    ve GEÇERLİ; imzasızda iyi-biçimlilik hatası olarak kalır."""
    imzali = _sentetik_udf(tmp_path / "p1.udf", imzali=True, prolog_bosluklu=True)
    imzasiz = _sentetik_udf(tmp_path / "p2.udf", imzali=False, prolog_bosluklu=True)
    s1 = uy.udf_dogrula(imzali, resmi_okuyucu=False)
    s2 = uy.udf_dogrula(imzasiz, resmi_okuyucu=False)
    assert s1["xml_iyi_bicimli"] is True and s1["gecerli"] is True
    assert s2["xml_iyi_bicimli"] is False and s2["gecerli"] is False


def test_tolerans_bosluk_sinifiyla_sinirli_metin_kaybi_imzalida_da_RED(tmp_path):
    """Tolerans '1-boşluk SINIFI' ile sınırlıdır: kaplanmayan kuyruk METİN
    ('X') ise imzalı nüshada BİLE GEÇERSİZ — metin kaybı hiçbir profilde
    tolere edilmez."""
    yol = _sentetik_udf(tmp_path / "kayip.udf", imzali=True, kuyruk="X")
    s = uy.udf_dogrula(yol, resmi_okuyucu=False)
    assert s["gecerli"] is False
    assert s["offsetler_tutarli"] is False


def test_tolerans_tek_boslukla_sinirli_cift_bosluk_imzalida_da_RED(tmp_path):
    """'TEK küçük boşluk' toleransı: iki boşlukluk sapma imzalı nüshada bile
    RED — tolerans ölçülen gerçek sapmanın (1 boşluk) ötesine genişletilmez."""
    yol = _sentetik_udf(tmp_path / "cift.udf", imzali=True, kuyruk="  ")
    s = uy.udf_dogrula(yol, resmi_okuyucu=False)
    assert s["gecerli"] is False
    assert s["offsetler_tutarli"] is False


# ── B7 — MAKBUZ GARANTİSİ (_oa varsa defter kurulur) ────────────────────────

def test_makbuz_oa_varken_defteri_kurar_ve_yazar(tmp_path):
    """B7: `_oa` VAR ama `_oa/defter` YOK → makbuz fonksiyonu defteri
    makedirs ile KURAR ve satırı yazar (eski davranış sessiz atlamaydı)."""
    (tmp_path / "_oa").mkdir()
    cikti = tmp_path / "dilekce.udf"
    cikti.write_bytes(b"ornek udf baytlari")
    yol = uy._uretim_makbuzu_yaz(str(tmp_path), "taslak.md", str(cikti),
                                 "html2udf", {"gecerli": True,
                                              "resmi_okuyucu": "OK"})
    assert yol is not None, "_oa varken makbuz yazılmalıydı (defter kurularak)"
    assert (tmp_path / "_oa" / "defter").is_dir()
    kayit = json.loads(pathlib.Path(yol).read_text(encoding="utf-8")
                       .strip().splitlines()[-1])
    assert kayit["motor"] == "html2udf"
    assert kayit["cikti"] == str(cikti)


def test_makbuz_oa_da_defter_de_yoksa_sessiz_atlanir(tmp_path):
    """B7 sınırı: `_oa` da yoksa sessiz atlama SÜRER — defter/`_oa` açmak
    pipeline'ın işidir, bu script dayatmaz."""
    cikti = tmp_path / "d.udf"
    cikti.write_bytes(b"x")
    yol = uy._uretim_makbuzu_yaz(str(tmp_path), "t.md", str(cikti),
                                 "html2udf", {"gecerli": True})
    assert yol is None
    assert not (tmp_path / "_oa").exists(), "_oa yokken OLUŞTURULMAMALI"


# ── istisna defteri (ortak şema, append-only) ───────────────────────────────

def test_istisna_kaydi_oa_varken_yazilir(tmp_path):
    (tmp_path / "_oa").mkdir()
    yol = uy._istisna_kaydi_yaz(str(tmp_path), "dogrulama-toleransi",
                                "ornek.udf", "test gerekçesi")
    assert yol is not None
    satirlar = pathlib.Path(yol).read_text(encoding="utf-8").strip().splitlines()
    kayit = json.loads(satirlar[-1])
    assert kayit["tur"] == "dogrulama-toleransi"
    assert kayit["ilgili"] == "ornek.udf"
    assert kayit["gerekce"] == "test gerekçesi"
    assert kayit["onay"] == "otomatik-kural"
    assert kayit["imza"] == "udf_yaz.py"
    assert kayit["zaman"]
    # append-only: ikinci çağrı üzerine yazmaz
    uy._istisna_kaydi_yaz(str(tmp_path), "dogrulama-toleransi", "o2.udf", "g2")
    assert len(pathlib.Path(yol).read_text(encoding="utf-8")
               .strip().splitlines()) == 2


def test_istisna_kaydi_oa_yoksa_sessiz(tmp_path):
    yol = uy._istisna_kaydi_yaz(str(tmp_path), "dogrulama-toleransi", "o", "g")
    assert yol is None
    assert not (tmp_path / "_oa").exists()


def test_dogrula_cli_imzali_toleransta_istisna_kaydi_duser(tmp_path, monkeypatch):
    """--dogrula hattı: imzalı nüshada tolerans uygulanınca `--kok` altındaki
    `_oa/defter/istisna-kayitlari.jsonl`e dogrulama-toleransi satırı düşer ve
    çıkış kodu 0'dır (dosya GEÇERLİ). Resmî okuyucu bacağı ağsız yalıtılır."""
    (tmp_path / "_oa").mkdir()
    udf = _sentetik_udf(tmp_path / "imzali.udf", imzali=True,
                        prolog_bosluklu=True, kuyruk=" ")
    monkeypatch.setattr(uy, "npx_ile_udf_oku", lambda *a, **k: {
        "calisti": False, "basarili": False, "metin": "", "hata": "test ortamı"})
    monkeypatch.setattr(sys, "argv", [
        "udf_yaz.py", "--dogrula", udf, "--kok", str(tmp_path)])
    with pytest.raises(SystemExit) as e:
        uy.main()
    assert e.value.code == 0, "imzalı-tolerans profilinde dosya GEÇERLİ çıkmalı"
    kutuk = tmp_path / "_oa" / "defter" / "istisna-kayitlari.jsonl"
    assert kutuk.is_file(), "tolerans istisna defterine iz düşmeliydi"
    kayit = json.loads(kutuk.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert kayit["tur"] == "dogrulama-toleransi"
    assert kayit["ilgili"] == udf

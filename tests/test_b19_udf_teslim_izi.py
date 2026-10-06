# -*- coding: utf-8 -*-
"""B-19 / B-18 kilidi — mahkemeye giden UDF'ye İÇ İZ sızmaz.

Saha bulgusu (derlem, 08-09.09.2026): taslaktaki iç izleme yorumları
(`<!-- kaynaklar: _oa/... -->`) ve makine kaynakça bloğu (`<!-- kaynakca:v1 -->`
… önsözünde `kaynakca_uret.py` adı) UDF'ye GÖRÜNÜR METİN olarak geçti.
16.09'da kurulu eklenti önbelleğinde yerinde yamalandı (v0.5.16.2/16.3) ama
depoya işlenmedi (B-19): eklentiyi GitHub'dan kuran herkeste sızıntı geri
geliyordu. v0.5.17.1 yamayı depoya alır; B-20 avukat kararı (2026-10-06):
kaynakça mahkemeye giden nüshaya GİRMEZ, iç taslakta kalır.

Tamamen çevrimdışı ve deterministik: yalnız `md_udf_html.donustur()` ve
`kunye_ortak.kendi_dosya_no_mu()` çıktıları denetlenir. Fikstürler kurgudur.
"""
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mh = _yukle("md_udf_html_b19", SKILLS / "oa-dilekce" / "scripts" / "md_udf_html.py")
sys.path.insert(0, str(SKILLS / "oa-kontrol" / "scripts"))
import kunye_ortak as ko  # noqa: E402

KAYNAKCA_BLOGU = (
    "<!-- kaynakca:v1 -->\n\n"
    "## İÇTİHAT KAYNAKÇASI\n\n"
    "Aşağıdaki kararların tamamı tam metinleriyle okunup kütüğe\n"
    "damgalanmıştır; erişim linkleri teyit kaydından gelir (bu blok\n"
    "`kaynakca_uret.py` tarafından mekanik üretilir — elle yazılmaz).\n\n"
    "- Yargıtay 9. HD 2024/123 E., 2024/456 K. — https://ornek.invalid/karar\n\n"
    "<!-- /kaynakca -->\n"
)


# ------------------------------------------------------------ iç iz ayıklama
def test_html_yorumu_teslim_htmline_gecmez():
    html = mh.donustur("<!-- kaynaklar: _oa/metin/00-kunye.json@ab12 -->\n\n"
                       "Gövde cümlesi.\n")
    assert "<!--" not in html and "&lt;!--" not in html
    assert "_oa/" not in html and "kaynaklar:" not in html
    assert "Gövde cümlesi." in html


def test_makine_kaynakca_blogu_teslim_htmline_gecmez():
    html = mh.donustur("Talebimizin kabulüne karar verilmesini saygıyla arz ederiz.\n\n"
                       + KAYNAKCA_BLOGU)
    assert "İÇTİHAT KAYNAKÇASI" not in html
    assert "kaynakca_uret" not in html and "mekanik üretilir" not in html
    assert "ornek.invalid" not in html
    assert "saygıyla arz ederiz." in html


def test_cok_satirli_yorum_ayiklanir():
    html = mh.donustur("Birinci.\n\n<!-- iç not\nikinci satır -->\n\nİkinci.\n")
    assert "iç not" not in html and "ikinci satır" not in html
    assert "Birinci." in html and "İkinci." in html


def test_kapanmamis_yorum_gorunur_kalir():
    """Fail-visible: kapanmamış '<!--' sessizce yutulmaz; avukat görür."""
    html = mh.donustur("Metin <!-- kapanmadı\n")
    assert "&lt;!-- kapanmadı" in html


def test_ham_yol_da_ayiklar():
    html = mh.donustur("<!-- iz -->\nMetin satırı\n", ham=True)
    assert "iz" not in html.replace("Metin satırı", "")
    assert "Metin satırı" in html


def test_cok_sayida_kapanmamis_yorum_dokunulmadan_kalir():
    """Kapanış hiç yoksa girdi aynen döner (kapanmamış yorum avukata görünür
    kalır); uygulama tek geçişli olduğundan uzun girdide de kilitlenmez."""
    md = "<!-- x " * 20000
    assert mh.yorumlari_ayikla(md) == md


def test_kapanmamis_kaynakca_isareti_metni_yutmaz():
    md = "<!-- kaynakca:v1 -->\nAvukatın metni.\n"
    assert "Avukatın metni." in mh.yorumlari_ayikla(md)


# ------------------------------------------------------------ künye biçimi
def test_arti_isaretli_basliklar_alti_cizili_olur():
    html = mh.donustur("++DOSYA NO++\t: 2024/123 Esas\n")
    assert "<u>DOSYA NO</u>" in html and "++" not in html


def test_kunye_blogu_girintisiz_ve_satir_sonu_korunur():
    html = mh.donustur("MAHKEME\t: Örnek Asliye Hukuk Mahkemesi\n"
                       "DOSYA NO\t: 2024/123 Esas\n")
    assert html.count("<p ") == 1
    assert "text-indent" not in html
    assert "Mahkemesi<br/>DOSYA NO" in html


def test_duz_paragraf_girintili_ve_tek_satira_birlesmez():
    html = mh.donustur("Birinci satır\nikinci satır\n")
    assert "text-indent:24pt" in html
    assert "Birinci satır<br/>ikinci satır" in html


# ------------------------------------------------------------ B8 muafiyeti (kunye_ortak)
def test_arti_isaretli_dosya_no_satiri_kendi_kunyedir():
    atif = {"esas": "2024/123", "karar": None, "daire_key": None,
            "kunye_turu": None, "satir_no": 1}
    assert ko.kendi_dosya_no_mu(atif, "++DOSYA NO++ : 2024/123 Esas") is True


def test_arti_isareti_daireli_kunyeyi_muaf_tutmaz():
    atif = {"esas": "2024/123", "karar": None, "daire_key": 9,
            "kunye_turu": None, "satir_no": 1}
    assert ko.kendi_dosya_no_mu(atif, "++DOSYA NO++ : 2024/123 Esas") is False


# ------------------------------------------------------------ bağımsız inceleme (Fable 5.1, 2026-10-06)
# A1 — VERİ KAYBI: kapanmamış '<!--' ileride HERHANGİ bir '-->' ile (ör. dosya sonundaki
# kaynakça işareti) yorum sanılırsa aradaki dilekçe metni UDF'den SESSİZCE silinirdi.
def test_kapanmamis_yorum_sonraki_isarete_kadar_metni_yutmaz():
    md = ("<!-- kaynaklar: _oa/metin/00-kunye.json@ab12 -->\n# DİLEKÇE\n\nGövde 1.\n\n"
          "<!-- TODO teyit et\n\n## AÇIKLAMALAR\n\nAçıklama metni.\n\n"
          "## NETİCE-İ TALEP\n\nKabulü.\n\n" + KAYNAKCA_BLOGU)
    html = mh.donustur(md)
    for parca in ("Gövde 1.", "AÇIKLAMALAR", "Açıklama metni.", "NETİCE-İ TALEP", "Kabulü."):
        assert parca in html, parca
    assert "&lt;!-- TODO teyit et" in html          # kapanmamış not görünür kalır
    assert "İÇTİHAT KAYNAKÇASI" not in html and "kaynakca_uret" not in html
    assert "_oa/" not in html


def test_kapanmamis_yorum_metindeki_ok_isaretine_kadar_metni_yutmaz():
    html = mh.donustur("Giriş.\n\n<!-- not\n\nÖnemli paragraf.\n\nSonuç --> devam.\n")
    assert "Önemli paragraf." in html and "Sonuç" in html


# A2 — kapanışı silinmiş eski blok + yeni blok: ilk açılıştan son kapanışa sıçranırsa aradaki
# EKLER/imza silinirdi. Kapanışsız açılış yalnız kendi işaretini kaybeder.
def test_cift_kaynakca_acilisi_tek_kapanista_metni_yutmaz():
    md = ("Gövde.\n\n<!-- kaynakca:v1 -->\n## İÇTİHAT KAYNAKÇASI\n- eski\n\n"
          "EKLER: 1- vekaletname\n\nAv. Örnek İmza\n\n"
          "<!-- kaynakca:v1 -->\n## İÇTİHAT KAYNAKÇASI\n- yeni künye\n<!-- /kaynakca -->\n")
    html = mh.donustur(md)
    assert "EKLER: 1- vekaletname" in html and "Av. Örnek İmza" in html
    assert "yeni künye" not in html


def test_kaynakca_ureticisi_kapanissiz_blokta_ikinci_blok_eklemez(tmp_path):
    ku = _yukle("kaynakca_uret_b19", SKILLS / "oa-kontrol" / "scripts" / "kaynakca_uret.py")
    taslak = tmp_path / "taslak.md"
    icerik = ("Gövde.\n\n<!-- kaynakca:v1 -->\n## İÇTİHAT KAYNAKÇASI\n- eski\n\n"
              "EKLER: 1- vekaletname\n")
    taslak.write_text(icerik, encoding="utf-8")
    with pytest.raises(ValueError):
        ku.taslaga_isle(str(taslak), str(tmp_path))
    assert taslak.read_text(encoding="utf-8") == icerik


# A3 — çevrimdışı yerel motor yolu (--yerel-motor-riskli) da aynı ayıklamadan geçer.
def test_yerel_motor_icerigine_ic_iz_gecmez():
    uy = _yukle("udf_yaz_b19", SKILLS / "oa-dilekce" / "scripts" / "udf_yaz.py")
    _, tam, _ = uy._ym_icerik_xml("<!-- kaynaklar: _oa/x -->\nGövde cümlesi.\n\n" + KAYNAKCA_BLOGU)
    assert "Gövde cümlesi." in tam
    assert "_oa/" not in tam and "kaynakca_uret" not in tam and "İÇTİHAT KAYNAKÇASI" not in tam


# A4 — HTML5 boş yorumları ('<!-->', '<!--->') kapanmış sayılır; gövde yutulmaz.
def test_bos_html5_yorumlari_metni_yutmaz():
    html = mh.donustur("A <!--> B gövde cümlesi C <!-- iz --> D <!---> E\n")
    assert "B gövde cümlesi C" in html and " D " in html and "E" in html
    assert " iz " not in html


# A5 — makine bloğu işaretleri üreticinin (kunye_ortak) işaretleriyle aynı kalmalı.
def test_kaynakca_isaretleri_kunye_ortak_ile_ayni():
    assert ko.KAYNAKCA_BLOK_BAS == "<!-- %s -->" % mh._KAYNAKCA_BAS_ICERIK
    assert ko.KAYNAKCA_BLOK_SON == "<!-- %s -->" % mh._KAYNAKCA_SON_ICERIK


# B — satıra yayılan vurgu, satır sonu korunurken de işlenir.
def test_satira_yayilan_kalin_yazi_islenir():
    html = mh.donustur("**Davacının iddiası\nyerinde değildir.**\n")
    assert "<strong>Davacının iddiası<br/>yerinde değildir.</strong>" in html
    assert "**" not in html


# C — '++' yalnız sözcük sınırında altı çizer; 'C++' gibi metin bozulmaz.
def test_cpp_arti_isaretleri_alti_cizili_olmaz():
    html = mh.donustur("C++ ve C++14 dilleri arasında fark yoktur.\n")
    assert "<u>" not in html and "C++ ve C++14" in html


# ------------------------------------------------------------ bağımsız inceleme 2. tur (Fable 5.1)
def test_crlf_metinde_bos_satir_korumasi_calisir():
    """Windows satır sonlu (CRLF) taslakta boş satır deseni (LF + boşluk + LF) boş satırı
    görmüyordu: kapanmamış yorum ile metindeki '-->' arasındaki paragraf yine sessizce yutuluyordu."""
    html = mh.donustur("Giriş.\r\n\r\n<!-- not\r\n\r\nÖnemli paragraf.\r\n\r\nSonuç --> devam.\r\n")
    assert "Önemli paragraf." in html and "Sonuç" in html


def test_uzun_tek_satirlik_ic_iz_yorumu_ayiklanir():
    """Uzunluk tavanı yalnız ÇOK SATIRLI adaya uygulanır: tek satırlık yorum paragraf sınırı
    yutamaz; kaynak_blogu'nun çok girdili meşru '<!-- kaynaklar: … -->' satırı ayıklanmalı."""
    yorum = "<!-- kaynaklar: " + " · ".join("metin/%03d-evrak.md@abcdef12" % i for i in range(120)) + " -->"
    assert len(yorum) > 2000
    html = mh.donustur(yorum + "\n\nGövde cümlesi.\n")
    assert "kaynaklar:" not in html and "metin/000" not in html
    assert "Gövde cümlesi." in html

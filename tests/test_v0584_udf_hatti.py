# -*- coding: utf-8 -*-
"""v0.5.8.4 UDF hattı — 372 saha provası ölçümlerinin devşirilmesi.

Kanıt tabanı (A/B saha hükmü): elle kurulan content.xml'li UDF'ler UYAP'ta
AÇILMIYOR (7 dosya karantina); html2udf ürünleri açılıyor. Python re-zip'i ve
pageFormat kenar yaması AKLANDI — fark yalnız content.xml içeriği: yerel motor
`<elements resolver="hvl-default">` yazıyor ama `<styles>` bloğunda
`name="hvl-default"` STİL TANIMI YOK. Ayrıca makbuz hiç üretilmedi çünkü tek
üretici `teslim_paketi._makbuz_yaz` idi ve model o zinciri atladı.

Bu dosya dört sözleşmeyi kilitler:
  1) `--yerel-motor` EMEKLİ: hata + yönlendirme (`--yerel-motor-riskli`).
  2) Riskli yol `udf_dogrula(resmi_okuyucu=True)` kullanır; okuyucu OK
     vermezse `<ad>.DOGRULANMADI` işareti bırakır ama üretimi KIRMAZ.
  3) `udf_dogrula` hvl-default STİL TANIMI denetimi (elle-üretim imzası).
  4) Üretim makbuzu (best-effort): `_oa/defter/udf-uretim-makbuz.jsonl`.
  5) md_udf_html şekil düzeltmeleri: link 11pt, başlık/tablo/liste 1,5
     satır aralığı, `<li><p>` hayalet-paragraf deseni yok.

Tamamen ağsız/deterministik: dış süreç ya sahte npx adıyla ya monkeypatch ile
yalıtılır; tüm veriler sentetiktir (tmp_path — gerçek dava yolu/adı YOK).
"""
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import zipfile

REPO = pathlib.Path(__file__).resolve().parents[1]
SK = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce" / "scripts"
SCRIPT = SK / "udf_yaz.py"
MD_HTML_SCRIPT = SK / "md_udf_html.py"


def _yukle(ad, modul_adi):
    yol = SK / (ad + ".py")
    assert yol.is_file(), f"{ad}.py bulunamadı: {yol}"
    spec = importlib.util.spec_from_file_location(modul_adi, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


uy = _yukle("udf_yaz", "_v0584_udf_yaz")
mh = _yukle("md_udf_html", "_v0584_md_udf_html")


def _sentetik_udf(yol, stil_etiketi):
    """Sentetik minimal UDF: CDATA 'Metin\\n' (6 karakter) + tek paragraf.
    `stil_etiketi` styles bloğunun içeriğidir — hvl-default stil tanımının
    VARLIĞI/YOKLUĞU testin değişkenidir."""
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<template format_id="1.8">'
        '<content><![CDATA[Metin\n]]></content>'
        '<properties><pageFormat mediaSizeName="1"/></properties>'
        '<elements resolver="hvl-default" name="hvl-default">'
        '<paragraph><content startOffset="0" length="6"/></paragraph>'
        '</elements>'
        '<styles>%s</styles>'
        '</template>' % stil_etiketi
    )
    with zipfile.ZipFile(str(yol), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.xml", xml.encode("utf-8"))
    return yol


HVL_STIL = '<style name="hvl-default" family="Times New Roman" size="12"/>'
DUZ_STIL = '<style name="default" family="Times New Roman" size="12"/>'


# ── (1) --yerel-motor EMEKLİ: hata + yönlendirme ────────────────────────────

def test_eski_yerel_motor_bayragi_hata_verir_ve_yonlendirir(tmp_path):
    """372 hükmü: eski bayrak artık ÜRETMEZ — hata verir, karantina kanıtını
    söyler ve bilinçli-risk bayrağına yönlendirir. Hiçbir .udf yazılmaz."""
    girdi = tmp_path / "taslak.md"
    girdi.write_text("# BAŞLIK\n\nSayın Mahkeme, arz ederiz.\n", encoding="utf-8")
    cikti = tmp_path / "taslak.udf"
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--girdi", str(girdi),
         "--cikti", str(cikti), "--yerel-motor"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode != 0
    assert not cikti.exists(), "emekli bayrak .udf ÜRETMEMELİYDİ"
    birlesik = cp.stderr + cp.stdout
    assert "372" in birlesik and "karantina" in birlesik
    assert "html2udf" in birlesik
    assert "--yerel-motor-riskli" in birlesik


# ── (2) --yerel-motor-riskli: resmi_okuyucu=True + DOGRULANMADI işareti ─────

def test_riskli_yol_udf_dogrulayi_resmi_okuyucu_ile_cagirir(tmp_path, monkeypatch):
    """Riskli yolun doğrulaması artık resmî okuyucu bacağını (5. denetim)
    İÇERMEK zorundadır — monkeypatch ile çağrı parametresi gözlenir."""
    yakalanan = {}

    def _sahte_dogrula(yol, resmi_okuyucu=False, okuyucu_fn=None):
        yakalanan["resmi_okuyucu"] = resmi_okuyucu
        yakalanan["okuyucu_fn_verildi"] = okuyucu_fn is not None
        return {"gecerli": True, "hatalar": [], "resmi_okuyucu": "OK"}

    monkeypatch.setattr(uy, "udf_dogrula", _sahte_dogrula)
    cikti = tmp_path / "riskli.udf"
    sonuc = uy.yerel_motor_ile_uret("Sayın Mahkeme.\n", str(cikti))
    assert yakalanan["resmi_okuyucu"] is True, (
        "riskli yol udf_dogrula'yı resmi_okuyucu=True ile çağırmalı")
    assert sonuc["basarili"] is True
    assert cikti.is_file()
    # okuyucu OK dediyse işaret dosyası BIRAKILMAZ
    assert sonuc["isaret_dosyasi"] is None
    assert not pathlib.Path(str(cikti) + ".DOGRULANMADI").exists()


def test_riskli_okuyucu_ok_vermezse_DOGRULANMADI_isareti_birakilir(tmp_path, monkeypatch):
    """Okuyucu OK vermezse (YAPILAMADI/RET): üretim yine TAMAMLANIR (fırlatmaz)
    ama çıktının yanına '<ad>.DOGRULANMADI' işaret dosyası düşer — 372 dersi:
    üretildi != geçerli; doğrulanmamışlık diskte GÖRÜNÜR kalmalı."""
    monkeypatch.setattr(uy, "udf_dogrula", lambda *a, **k: {
        "gecerli": False,
        "hatalar": ["hvl-default stil tanımı yok (elle-üretim imzası)"],
        "resmi_okuyucu": "YAPILAMADI"})
    cikti = tmp_path / "riskli2.udf"
    sonuc = uy.yerel_motor_ile_uret("Metin.\n", str(cikti))
    assert sonuc["basarili"] is True, "üretim kırılmamalı (fırlatmaz)"
    assert cikti.is_file()
    isaret = pathlib.Path(str(cikti) + ".DOGRULANMADI")
    assert isaret.is_file(), "işaret dosyası çıktının yanına düşmeliydi"
    assert sonuc["isaret_dosyasi"] == str(isaret)
    icerik = isaret.read_text(encoding="utf-8")
    assert "UYAP" in icerik  # işaret dosyası gerekçeyi taşır


def test_cli_riskli_bayrak_uretir_isaretler_ve_uyarir(tmp_path):
    """Uçtan uca (AĞSIZ — npx bilerek bozuk): riskli bayrak dosyayı üretir
    (exit 0), görünür uyarı basar; okuyucu YAPILAMADI kaldığından
    DOGRULANMADI işareti diskte olmalı."""
    girdi = tmp_path / "taslak.md"
    girdi.write_text("# BAŞLIK\n\nSayın Mahkeme, arz ederiz.\n", encoding="utf-8")
    cikti = tmp_path / "taslak.udf"
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--girdi", str(girdi), "--cikti", str(cikti),
         "--yerel-motor-riskli", "--npx", "oa-boyle-bir-komut-yok-xyz"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert cikti.is_file() and cikti.stat().st_size > 0
    assert "GARANTİ DEĞİL" in cp.stderr
    assert pathlib.Path(str(cikti) + ".DOGRULANMADI").is_file()
    assert "DOGRULANMADI" in cp.stderr  # blok uyarı işareti anons eder


# ── (3) udf_dogrula: hvl-default STİL TANIMI denetimi ───────────────────────

def test_udf_dogrula_hvl_stil_tanimli_dosyayi_GECERLI_sayar(tmp_path):
    yol = _sentetik_udf(tmp_path / "stilli.udf", HVL_STIL)
    sonuc = uy.udf_dogrula(str(yol), resmi_okuyucu=False)
    assert sonuc["hvl_stil_tanimi"] is True
    assert sonuc["gecerli"] is True, sonuc["hatalar"]


def test_udf_dogrula_yalniz_elements_te_hvl_olani_GECERSIZ_sayar(tmp_path):
    """AYIRT EDİCİ İMZA (372 A/B): `<elements ... name="hvl-default">` VAR ama
    styles bloğunda `<style name="hvl-default">` TANIMI YOK — açılmayan elle
    üretimlerin imzası tam olarak budur. elements'teki name denetimi
    SAĞLAMAMALI."""
    yol = _sentetik_udf(tmp_path / "imzali.udf", DUZ_STIL)
    sonuc = uy.udf_dogrula(str(yol), resmi_okuyucu=False)
    assert sonuc["hvl_stil_tanimi"] is False
    assert sonuc["gecerli"] is False
    assert any("hvl-default stil tanımı yok (elle-üretim imzası)" in h
               for h in sonuc["hatalar"])


# ── (4) ÜRETİM MAKBUZU (best-effort, _oa/defter) ────────────────────────────

def test_makbuz_defter_varken_yazilir_ve_append_eder(tmp_path):
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True)
    cikti = tmp_path / "dilekce.udf"
    cikti.write_bytes(b"ornek udf baytlari")

    yol = uy._uretim_makbuzu_yaz(
        str(tmp_path), "taslak.md", str(cikti), "html2udf",
        {"gecerli": True, "resmi_okuyucu": "OK"}, kenar_notu="kenar: uygulandı")

    assert yol is not None and os.path.isfile(yol)
    assert os.path.basename(yol) == "udf-uretim-makbuz.jsonl"
    satirlar = pathlib.Path(yol).read_text(encoding="utf-8").strip().splitlines()
    assert len(satirlar) == 1
    kayit = json.loads(satirlar[0])
    assert kayit["motor"] == "html2udf"
    assert kayit["dogrulama"] is True
    assert kayit["resmi_okuyucu"] == "OK"
    assert kayit["girdi"] == "taslak.md"
    assert kayit["cikti"] == str(cikti)
    assert kayit["kenar_notu"] == "kenar: uygulandı"
    assert kayit["sha256"] == hashlib.sha256(b"ornek udf baytlari").hexdigest()
    assert kayit["zaman"]  # ISO zaman damgası dolu

    # ikinci koşu APPEND etmeli (üzerine yazmamalı)
    uy._uretim_makbuzu_yaz(str(tmp_path), "taslak.md", str(cikti),
                           "yerel-riskli", {"gecerli": False,
                                            "resmi_okuyucu": "YAPILAMADI"})
    satirlar = pathlib.Path(yol).read_text(encoding="utf-8").strip().splitlines()
    assert len(satirlar) == 2
    kayit2 = json.loads(satirlar[1])
    assert kayit2["motor"] == "yerel-riskli"
    assert kayit2["dogrulama"] is False


def test_makbuz_defter_yoksa_sessiz_atlanir(tmp_path):
    cikti = tmp_path / "d.udf"
    cikti.write_bytes(b"x")
    yol = uy._uretim_makbuzu_yaz(str(tmp_path), "t.md", str(cikti),
                                 "html2udf", {"gecerli": True})
    assert yol is None
    assert not (tmp_path / "_oa").exists(), "defter yokken _oa OLUŞTURULMAMALI"


def test_makbuz_bozuk_defter_yolunda_firlatmaz(tmp_path):
    """Makbuz dosyasının yerinde bir DİZİN dursa bile (open başarısız) makbuz
    fonksiyonu fırlatmamalı — üretim akışı ASLA kırılmaz."""
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True)
    (defter / "udf-uretim-makbuz.jsonl").mkdir()  # dosya yerine dizin: engel
    cikti = tmp_path / "d.udf"
    cikti.write_bytes(b"x")
    yol = uy._uretim_makbuzu_yaz(str(tmp_path), "t.md", str(cikti),
                                 "html2udf", {"gecerli": True})
    assert yol is None  # sessizce atlandı, istisna sızmadı


def test_cli_html2udf_basarisinda_makbuz_duser(tmp_path, monkeypatch):
    """Uçtan uca (in-process, npx sahte): html2udf hattı başarıyla bitince
    defter varsa makbuz düşer — 372'de makbuzun hiç üretilmeme sebebi tek
    üreticinin (teslim_paketi) atlanabilmesiydi; artık .udf'i fiilen yazan
    script kendi makbuzunu düşer."""
    defter = tmp_path / "_oa" / "defter"
    defter.mkdir(parents=True)
    girdi = tmp_path / "taslak.md"
    girdi.write_text("Sayın Mahkeme, arz ederiz.\n", encoding="utf-8")
    cikti = tmp_path / "dilekce.udf"

    def _sahte_uret(html_yolu, cikti_yolu, npx_yolu="npx", zaman_asimi=180):
        _sentetik_udf(cikti_yolu, HVL_STIL)
        return {"basarili": True, "exit_kod": 0, "stdout": "", "stderr": "",
                "hata": None, "kenar_notu": "kenar: test"}

    monkeypatch.setattr(uy, "npx_ile_udf_uret", _sahte_uret)
    monkeypatch.setattr(uy, "npx_ile_udf_oku", lambda *a, **k: {
        "calisti": False, "basarili": False, "metin": "", "hata": "test ortamı"})
    monkeypatch.setattr(sys, "argv", [
        "udf_yaz.py", "--girdi", str(girdi), "--cikti", str(cikti),
        "--kok", str(tmp_path)])
    uy.main()  # başarı yolunda sys.exit çağırmaz

    makbuz = defter / "udf-uretim-makbuz.jsonl"
    assert makbuz.is_file(), "html2udf başarısında makbuz düşmeliydi"
    kayit = json.loads(makbuz.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert kayit["motor"] == "html2udf"
    assert kayit["kenar_notu"] == "kenar: test"
    assert kayit["cikti"] == str(cikti)


# ── (5) md_udf_html şekil düzeltmeleri ──────────────────────────────────────

def test_kaynak_blogu_linkleri_11pt_9pt_yok():
    """KULLANICI KARARI: tüm link puntoları 11pt'de birleşti — kaynak
    bloğundaki linkler de gövde linkleriyle aynı 11pt span'i alır; 9pt
    hiçbir yerde kalmaz."""
    md = ("## KAYNAKLAR\n\n"
          "- [Yargıtay 9. HD 2020/1 E.](https://karararama.yargitay.gov.tr/x)\n"
          "- [AYM B. No: 2020/1](https://kararlarbilgibankasi.anayasa.gov.tr/y)\n")
    html = mh.donustur(md)
    assert html.count("font-size:11pt") == 2
    assert "9pt" not in html
    kaynak = MD_HTML_SCRIPT.read_text(encoding="utf-8")
    assert "9pt" not in kaynak, "9pt punto kodda da kalmamalı"


def test_baslik_stillerinde_satir_araligi_1_5():
    html = mh.donustur("# Bir\n\n## İki\n\n### Üç\n")
    basliklar = [s for s in html.splitlines() if s.startswith("<p ")]
    assert len(basliklar) == 3
    for b in basliklar:
        assert "line-height:1.5" in b, b


def test_tablo_hucrelerinde_satir_araligi_1_5():
    html = mh.donustur("| Kalem | Tutar |\n| --- | --- |\n| Vekalet | 1000 |\n")
    assert '<td style="background-color:#EEEEEE; line-height:1.5">' in html
    assert '<td style="line-height:1.5">Vekalet</td>' in html
    assert "<td>" not in html, "stilsiz hücre kalmamalı"


def test_liste_maddesinde_blok_p_yok_hayalet_paragraf_onlenir():
    """CANLI ÖLÇÜM (372): `<li><p style=...>` deseni html2udf'te her maddeden
    sonra HAYALET boş Numbered paragraf üretiyor — li içine doğrudan stillenmiş
    span/metin verilir, blok <p> KULLANILMAZ."""
    html_ol = mh.donustur("1. birinci madde\n2. ikinci madde\n")
    assert "<ol>" in html_ol and html_ol.count("<li>") == 2
    assert "<li><p" not in html_ol
    assert '<li><span style="line-height:1.5">' in html_ol
    assert "birinci madde" in html_ol

    html_ul = mh.donustur("- bir\n- iki\n- üç\n")
    assert "<ul>" in html_ul and html_ul.count("<li>") == 3
    assert "<li><p" not in html_ul


def test_kod_yorumu_1_3_degil_1_5_der():
    """(e) kod-yorum sapması: JUST sabiti 1.5 üretirken yorum '1.3 satır
    aralığı' diyordu — yorum da 1,5 demeli."""
    kaynak = MD_HTML_SCRIPT.read_text(encoding="utf-8")
    assert "1.3 satır aralığı" not in kaynak
    assert ("1,5 satır aralığı" in kaynak) or ("1.5 satır aralığı" in kaynak)

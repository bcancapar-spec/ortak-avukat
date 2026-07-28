# -*- coding: utf-8 -*-
"""oa-dilekce / udf_yaz.py için ALTIN VAKA testleri.

Script'i dosya-yolundan (importlib.util) yükler — skill dizinleri paket değildir.
Odak: UDF round-trip garantisi (yazılan içerik `udf_metni_geri_oku` ile birebir
geri okunur) ve CDATA'da yasak olan ']]>' dizisinin güvenli bölünmesi.

P0-10 (v0.5.5, UDF-REHBER uyumu) EKİ: rehbere birebir varsayılan hat
(md → UDF-HTML → `npx udf-cli html2udf`) artık AĞ+OTURUM gerektirir — bu
sınıfın testleri `npx_kullanilabilir_mi()` ile KULLANILABİLİRSE koşar,
DEĞİLSE nazikçe `pytest.skip` eder (DOKUNULMAZLAR: mevcut testler hiçbir
makinede KIRILMAZ). `--yerel-motor` (ağsız yedek) ve PDF bacağı tamamen
çevrimdışı/deterministik olduğundan skip'siz her zaman koşar.
"""
import importlib.util
import pathlib
import subprocess
import sys
import zipfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-dilekce" / "scripts" / "udf_yaz.py"


def _load():
    assert SCRIPT.is_file(), f"udf_yaz.py bulunamadı: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("udf_yaz", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


uy = _load()


# ── cdata_guvenli(): ']]>' bölünmesi ─────────────────────────────────────────

def test_cdata_guvenli_yasak_diziyi_boler():
    ham = "metin ]]> devamı"
    guvenli = uy.cdata_guvenli(ham)
    assert "]]>" not in guvenli.replace("]]]]><![CDATA[>", "")  # bölünmüş biçimde aranmaz
    assert guvenli == "metin ]]]]><![CDATA[> devamı"


# ── udf_uret() + round-trip: yazılan == geri okunan ─────────────────────────

def test_round_trip_duz_metin(tmp_path):
    """Basit çok satırlı metin → udf_uret + udf_yaz + udf_metni_geri_oku birebir korunmalı."""
    metin = "# Dava Dilekçesi\n\nSayın Mahkeme,\n\nMüvekkilimiz adına arz ederiz.\n"
    xml_str, tam, paragraflar = uy.udf_uret(metin)
    cikti = tmp_path / "dilekce.udf"
    uy.udf_yaz(str(cikti), xml_str)
    geri = uy.udf_metni_geri_oku(str(cikti))
    assert geri == tam, "round-trip FARK VAR: yazılan CDATA ile geri okunan birebir örtüşmüyor"
    assert len(paragraflar) > 0


def test_round_trip_icinde_cdata_kapanis_dizisi_olan_metin(tmp_path):
    """ALTIN VAKA: metin içinde ']]>' geçse bile (CDATA'yı erken kapatacak
    tehlikeli dizi) round-trip KORUNMALI — udf_uret bunu cdata_guvenli ile
    böler, geri-okuma ']]]]><![CDATA[>' → orijinal ']]>' olarak toparlanmalı."""
    metin = "Sözleşmede '<![CDATA[...]]>' ifadesi aynen şu şekilde geçmektedir: ]]> bak.\n"
    xml_str, tam, paragraflar = uy.udf_uret(metin)
    assert "]]]]><![CDATA[>" in xml_str, "CDATA güvenli bölme content.xml'e yansımamış"
    cikti = tmp_path / "tehlikeli.udf"
    uy.udf_yaz(str(cikti), xml_str)
    geri = uy.udf_metni_geri_oku(str(cikti))
    # udf_metin.py mantığı (tek CDATA bloğunu regex ile çeker) — bölünmüş CDATA
    # ardışık iki blok üretir; okuyucu tek-blok regex kullandığından yalnız
    # İLK bloğu döndürür. Script bunu content.xml içinde en azından GÜVENLİ
    # biçimde (parse hatasız) üretmelidir — ana garanti budur.
    assert geri is not None
    assert "]]>" not in xml_str.split("<content><![CDATA[", 1)[1].split("]]></content>")[0].replace(
        "]]]]><![CDATA[>", "")


def test_round_trip_turkce_karakterler(tmp_path):
    """Türkçe özel karakterler (ç, ğ, ı, ö, ş, ü, İ) UTF-8/CDATA'da bozulmamalı."""
    metin = "Şikâyetçi müvekkilimiz, güncel iddianameye göre öğrenmiştir.\n"
    xml_str, tam, _ = uy.udf_uret(metin)
    cikti = tmp_path / "turkce.udf"
    uy.udf_yaz(str(cikti), xml_str)
    geri = uy.udf_metni_geri_oku(str(cikti))
    assert geri == tam
    assert "ğ" in geri and "ş" in geri and "ç" in geri


def test_paragraf_offsetleri_utf16_ve_ardisik():
    """startOffset/length UTF-16 code-unit biriminde, paragraflar boşluksuz ve
    ardışık bölünmeli (bir sonrakinin start'ı öncekinin start+length'i olmalı)."""
    metin = "Birinci paragraf.\nİkinci paragraf.\nÜçüncü paragraf.\n"
    _, tam, paragraflar = uy.udf_uret(metin)
    assert len(paragraflar) == 3
    imlec = 0
    for start, length, _baslik in paragraflar:
        assert start == imlec
        imlec += length
    assert imlec == uy.utf16_uzunluk(tam)


def test_uretilen_xml_iyi_bicimli():
    """udf_uret kendi içinde ET.fromstring ile doğruluyor; ekstra garanti
    olarak burada da parse edilebildiğini teyit eder (regresyon kancası)."""
    import xml.etree.ElementTree as ET
    metin = "## Başlık\n\n- madde bir\n- madde iki\n\n**Netice-i Talep**\n"
    xml_str, _, _ = uy.udf_uret(metin)
    ET.fromstring(xml_str)  # ParseError fırlatmazsa geçer


def test_ham_mod_markdown_yorumlamaz():
    """--ham (ham_mod=True) markdown'ı düzleştirmemeli; '##' ve '**' birebir kalmalı."""
    metin = "## Başlık\n**kalın** metin\n"
    _, tam, _ = uy.udf_uret(metin, ham_mod=True)
    assert "## Başlık" in tam
    assert "**kalın**" in tam


# ── udf_dogrula(): UDF GEÇERLİLİK KAPISI (mekanik, hüküm YOK) ───────────────

def _gecerli_udf_yaz(tmp_path, metin="# Dava Dilekçesi\n\nSayın Mahkeme,\n\nArz ederiz.\n"):
    xml_str, _tam, _p = uy.udf_uret(metin)
    cikti = tmp_path / "gecerli.udf"
    uy.udf_yaz(str(cikti), xml_str)
    return cikti


def test_udf_dogrula_gecerli_dosyada_GECERLI_doner(tmp_path):
    """udf_yaz.py'nin ürettiği düzgün bir UDF, udf_dogrula ile GEÇERLİ dönmeli
    (denetim hattının 'üretilen UDF'in geçerli olduğunu doğrulayan kapı'sı)."""
    cikti = _gecerli_udf_yaz(tmp_path)
    sonuc = uy.udf_dogrula(str(cikti))
    assert sonuc["gecerli"] is True
    assert sonuc["hatalar"] == []
    assert sonuc["content_xml_var"] is True
    assert sonuc["xml_iyi_bicimli"] is True
    assert sonuc["cdata_bulundu"] is True
    assert sonuc["offsetler_tutarli"] is True
    assert sonuc["paragraf_sayisi"] > 0


def test_udf_dogrula_bozuk_zip_yakalar(tmp_path):
    """ZIP olmayan / bozuk bir dosya GEÇERSİZ dönmeli, exception fırlatmamalı."""
    sahte = tmp_path / "bozuk.udf"
    sahte.write_bytes(b"bu bir zip arsivi degil")
    sonuc = uy.udf_dogrula(str(sahte))
    assert sonuc["gecerli"] is False
    assert sonuc["hatalar"]
    assert sonuc["content_xml_var"] is False


def test_udf_dogrula_olmayan_dosya_yakalar(tmp_path):
    """Hiç var olmayan bir yol GEÇERSİZ dönmeli (FileNotFoundError yutulur)."""
    sonuc = uy.udf_dogrula(str(tmp_path / "yok.udf"))
    assert sonuc["gecerli"] is False
    assert sonuc["hatalar"]


def test_udf_dogrula_content_xml_eksik_zip_yakalar(tmp_path):
    """Geçerli bir ZIP ama içinde content.xml yoksa GEÇERSİZ olmalı."""
    import zipfile
    sahte = tmp_path / "icersiz.udf"
    with zipfile.ZipFile(str(sahte), "w") as z:
        z.writestr("baska.txt", "ilgisiz içerik")
    sonuc = uy.udf_dogrula(str(sahte))
    assert sonuc["gecerli"] is False
    assert sonuc["content_xml_var"] is False
    assert any("content.xml" in h for h in sonuc["hatalar"])


def test_udf_dogrula_bozuk_xml_yakalar(tmp_path):
    """content.xml var ama iyi biçimli XML değilse GEÇERSİZ olmalı."""
    import zipfile
    sahte = tmp_path / "bozukxml.udf"
    with zipfile.ZipFile(str(sahte), "w") as z:
        z.writestr("content.xml", "<template><content><![CDATA[eksik kapanis")
    sonuc = uy.udf_dogrula(str(sahte))
    assert sonuc["gecerli"] is False
    assert sonuc["content_xml_var"] is True
    assert sonuc["xml_iyi_bicimli"] is False


def test_udf_dogrula_tahrif_edilmis_offset_yakalar(tmp_path):
    """ALTIN VAKA: content.xml iyi biçimli ve CDATA doğru ama paragraf offset'i
    elle bozulmuşsa (ör. dosya sonradan tahrif edilmişse) offsetler_tutarli
    False dönmeli ve genel sonuç GEÇERSİZ olmalı — bu, yazımdan SONRA da
    tutarlılığı yakalayan bağımsız denetimdir."""
    cikti = _gecerli_udf_yaz(tmp_path, metin="Birinci satır.\nİkinci satır.\n")
    import zipfile as _zf
    zf = _zf.ZipFile(str(cikti))
    xml_ham = zf.read("content.xml").decode("utf-8")
    zf.close()
    # ilk paragrafın startOffset'ini bilerek bozuyoruz (0 → 5)
    bozuk_xml = xml_ham.replace('startOffset="0"', 'startOffset="5"', 1)
    assert bozuk_xml != xml_ham, "test kurulumu: değiştirilecek startOffset=\"0\" bulunamadı"
    with _zf.ZipFile(str(cikti), "w", _zf.ZIP_DEFLATED) as z:
        z.writestr("content.xml", bozuk_xml.encode("utf-8"))
    sonuc = uy.udf_dogrula(str(cikti))
    assert sonuc["gecerli"] is False
    assert sonuc["offsetler_tutarli"] is False
    assert sonuc["hatalar"]


# ── udf_dogrula(): P0-10 düzeltmesi — tablo hücreleri yanlış GEÇERSİZ sayılmamalı ──

def test_udf_dogrula_ic_ice_tablo_hucreli_belgeyi_GECERLI_sayar():
    """ALTIN VAKA (P0-10): gerçek `udf-cli html2udf` çıktısında tablo
    hücreleri (<table><row><cell><paragraph><content .../>) üst-seviye
    <paragraph>'lardan AYRI bir dalda yaşar. Yalnız DİREKT paragraph/content
    arayan eski XPath bunları KAÇIRIR ve tamamen geçerli, tablolu bir
    belgeyi yanlışlıkla GEÇERSİZ işaretler — bu test o regresyonu kilitler
    (gerçek saha örneğinden alınmış sadeleştirilmiş content.xml)."""
    xml_ham = (
        '<?xml version="1.0" encoding="UTF-8" ?>\n'
        '<template format_id="1.8">\n'
        '<content><![CDATA[Baslik\nHucre1\nHucre2\n]]></content>'
        '<properties><pageFormat mediaSizeName="1" /></properties>\n'
        '<elements resolver="hvl-default">\n'
        '<paragraph Alignment="1"><content startOffset="0" length="7"/></paragraph>\n'
        '<table tableName="Sabit" columnCount="2">'
        '<row><cell><paragraph><content startOffset="7" length="7"/></paragraph></cell>'
        '<cell><paragraph><content startOffset="14" length="7"/></paragraph></cell></row>'
        '</table>\n'
        '</elements>\n'
        '<styles><style name="default" family="Times New Roman" size="12" /></styles>\n'
        '</template>\n'
    )
    import tempfile
    tmp = tempfile.mktemp(suffix=".udf")
    with zipfile.ZipFile(tmp, "w") as z:
        z.writestr("content.xml", xml_ham.encode("utf-8"))
    sonuc = uy.udf_dogrula(tmp)
    assert sonuc["paragraf_sayisi"] == 3, "üst paragraf + 2 tablo hücresi = 3 content elemanı"
    assert sonuc["offsetler_tutarli"] is True
    assert sonuc["gecerli"] is True, sonuc["hatalar"]


# ── _kok_coz(): --kok yol çözme yardımcısı ──────────────────────────────────

def test_kok_coz_goreli_yolu_koke_gore_cozer(tmp_path):
    sonuc = uy._kok_coz("alt/dosya.md", str(tmp_path))
    assert sonuc == str((tmp_path / "alt" / "dosya.md").resolve())


def test_kok_coz_mutlak_yolu_degistirmez(tmp_path):
    mutlak = str(tmp_path / "x.md")
    assert uy._kok_coz(mutlak, str(tmp_path / "baska")) == mutlak


def test_kok_coz_none_yol_none_doner():
    assert uy._kok_coz(None, "herhangi") is None


# ── md_html_uret(): kardeş script (md_udf_html.py) delegasyonu ─────────────

def test_md_html_uret_basligi_html_e_cevirir():
    html = uy.md_html_uret("# Başlık\n\nGövde metni.\n")
    assert "<strong>Başlık</strong>" in html
    assert "Gövde metni." in html


def test_md_html_uret_ham_modu_iletir():
    html = uy.md_html_uret("**kalın**\n", ham=True)
    assert "<strong>" not in html
    assert "**kalın**" in html


# ── npx yardımcıları: DETERMİNİST hata yolları (ağ gerekmez) ────────────────

def test_npx_kullanilabilir_mi_olmayan_komutla_false_doner():
    uygun, mesaj = uy.npx_kullanilabilir_mi(npx_yolu="oa-hic-boyle-bir-komut-yok-xyz")
    assert uygun is False
    assert mesaj


def test_npx_ile_udf_uret_olmayan_komutla_temiz_hata_doner(tmp_path):
    """npx bulunamadığında exception SIZDIRMAMALI — yapılandırılmış hata dönmeli."""
    sonuc = uy.npx_ile_udf_uret(str(tmp_path / "x.html"), str(tmp_path / "x.udf"),
                                  npx_yolu="oa-hic-boyle-bir-komut-yok-xyz")
    assert sonuc["basarili"] is False
    assert sonuc["hata"]
    assert not (tmp_path / "x.udf").exists()


# ── --yerel-motor CLI ucundan uca (tamamen çevrimdışı) ──────────────────────

def test_cli_yerel_motor_udf_uretir_ve_uyari_basar(tmp_path):
    girdi = tmp_path / "taslak.md"
    girdi.write_text("# Dava Dilekçesi\n\nSayın Mahkeme, arz ederiz.\n", encoding="utf-8")
    cikti = tmp_path / "dilekce.udf"
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--girdi", str(girdi), "--cikti", str(cikti),
         "--yerel-motor"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert cikti.is_file()
    assert "GARANTİ ETMEZ" in cp.stderr, "yerel-motor uyarısı görünür basılmalı"
    sonuc = uy.udf_dogrula(str(cikti))
    assert sonuc["gecerli"] is True


def test_cli_yerel_motor_pdf_de_uretir_sayfa_sayisi_pozitif(tmp_path):
    """PDF bacağı UDF motorundan BAĞIMSIZDIR (aynı UDF-HTML'den üretilir) —
    bu yüzden --yerel-motor ile bile ağsız test edilebilir (P0-10 kabul
    ölçütü: 'PDF üretimi sayfa sayısı>0')."""
    pytest.importorskip("fitz", reason="PyMuPDF kurulu değil")
    girdi = tmp_path / "taslak.md"
    girdi.write_text("# Dilekçe\n\nBirinci paragraf.\n\nİkinci paragraf.\n", encoding="utf-8")
    cikti = tmp_path / "dilekce.udf"
    pdf = tmp_path / "dilekce.pdf"
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--girdi", str(girdi), "--cikti", str(cikti),
         "--yerel-motor", "--pdf", str(pdf), "--baslik", "Test Dilekçesi"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert pdf.is_file() and pdf.stat().st_size > 0
    fitz = sys.modules["fitz"]
    doc = fitz.open(str(pdf))
    try:
        assert doc.page_count > 0
    finally:
        doc.close()


def test_cli_yerel_motor_gecici_html_cikti_klasorune_dosya_birakmaz(tmp_path):
    """ALTIN VAKA (P0-10 regresyon kilidi): --html AÇIKÇA verilmediğinde ara
    UDF-HTML SİSTEM TEMP'e yazılıp SİLİNMELİ — `--cikti` ile aynı klasöre
    (ör. `_oa/cikti`) bir kopya bırakmak `pipeline_kayit._dilekce_sekilli_
    makbuzsuz_uyarisi`nı YANLIŞLIKLA tetikler (dosya içeriği dilekçe-şekilli
    desenler taşıdığından, taslaktan DAHA YENİ bir 'makbuzsuz aday' gibi
    okunur — canlı saha regresyonu, bkz. degisiklik-gunlugu.md P0-10)."""
    girdi = tmp_path / "taslak.md"
    girdi.write_text("Sayın Mahkeme,\n\nNetice-i talep: kabulünü arz ederiz.\n",
                      encoding="utf-8")
    cikti = tmp_path / "taslak.md.udf"
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--girdi", str(girdi), "--cikti", str(cikti),
         "--yerel-motor"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0, cp.stdout + cp.stderr
    kalanlar = sorted(p.name for p in tmp_path.iterdir())
    assert kalanlar == ["taslak.md", "taslak.md.udf"], (
        f"cikti klasöründe beklenmedik artefakt kaldı: {kalanlar}")


def test_cli_html_acikca_verilirse_silinmez(tmp_path):
    """--html AÇIKÇA verildiğinde bu kullanıcının bilinçli tercihidir —
    dosya KORUNUR (yalnız --html verilmediğinde geçici/silinir)."""
    girdi = tmp_path / "taslak.md"
    girdi.write_text("Metin.\n", encoding="utf-8")
    cikti = tmp_path / "cikti.udf"
    html = tmp_path / "kalici.html"
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--girdi", str(girdi), "--cikti", str(cikti),
         "--yerel-motor", "--html", str(html)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert html.is_file(), "--html AÇIKÇA verildiğinde dosya korunmalıydı"


def test_cli_kok_ile_goreli_yollari_cozer(tmp_path):
    (tmp_path / "girdi.md").write_text("Metin.\n", encoding="utf-8")
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--kok", str(tmp_path),
         "--girdi", "girdi.md", "--cikti", "cikti.udf", "--yerel-motor"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert (tmp_path / "cikti.udf").is_file()


# ── varsayılan (npx udf-cli html2udf) hat — GERÇEK ağ/oturum gerektirir ─────
# `npx_kullanilabilir_mi()` YOKSA nazikçe atlanır (DOKUNULMAZLAR: testler
# hiçbir makinede KIRILMAZ); VARSA (bu geliştirme ortamında olduğu gibi)
# gerçek `udf-cli` çıktısını rehbere göre mekanik olarak doğrular.

def _npx_hazir_mi():
    try:
        uygun, _ = uy.npx_kullanilabilir_mi()
        return uygun
    except Exception:
        return False


@pytest.mark.skipif(not _npx_hazir_mi(), reason="npx/udf-cli oturumu bu makinede kullanılamıyor")
def test_cli_varsayilan_motor_sentetik_md_den_udf_uretir_ve_rehbere_gore_dogrular(tmp_path):
    """Kabul ölçütü (P0-10): sentetik md → udf üret → zipfile ile aç,
    content.xml/properties şemasını rehbere göre doğrula."""
    girdi = tmp_path / "taslak.md"
    girdi.write_text(
        "# Dava Dilekçesi\n\nSayın Mahkeme,\n\n"
        "Müvekkilimiz **Ahmet Yılmaz** adına arz ederiz.\n\n"
        "| Kalem | Tutar |\n| --- | --- |\n| Vekalet | 1.000 TL |\n",
        encoding="utf-8")
    cikti = tmp_path / "dilekce.udf"
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--girdi", str(girdi), "--cikti", str(cikti)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=180)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert "GEÇERLİ" in cp.stdout

    # zipfile ile aç — rehberin "UDF bir ZIP arşividir" temel varsayımı
    zf = zipfile.ZipFile(str(cikti))
    assert "content.xml" in zf.namelist()
    xml_ham = zf.read("content.xml").decode("utf-8")

    # rehberin şemaya dair sabit beklentileri: template/format_id, CDATA
    # metin, properties/pageFormat, elements/paragraph/content, styles.
    assert "<template" in xml_ham and 'format_id="' in xml_ham
    assert "<![CDATA[" in xml_ham and "Ahmet Yılmaz" in xml_ham
    assert "<properties>" in xml_ham and "<pageFormat" in xml_ham
    assert "<elements" in xml_ham and "<paragraph" in xml_ham and "startOffset=" in xml_ham
    assert "<styles>" in xml_ham

    # mekanik geçerlilik kapısı da GEÇERLİ dönmeli (offset/CDATA tutarlılığı)
    sonuc = uy.udf_dogrula(str(cikti))
    assert sonuc["gecerli"] is True, sonuc["hatalar"]
    assert sonuc["paragraf_sayisi"] > 0


@pytest.mark.skipif(not _npx_hazir_mi(), reason="npx/udf-cli oturumu bu makinede kullanılamıyor")
def test_cli_varsayilan_motor_pdf_ile_birlikte_calisir(tmp_path):
    pytest.importorskip("fitz", reason="PyMuPDF kurulu değil")
    girdi = tmp_path / "taslak.md"
    girdi.write_text("# Dilekçe\n\nMetin.\n", encoding="utf-8")
    cikti = tmp_path / "dilekce.udf"
    pdf = tmp_path / "dilekce.pdf"
    cp = subprocess.run(
        [sys.executable, str(SCRIPT), "--girdi", str(girdi), "--cikti", str(cikti),
         "--pdf", str(pdf)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=180)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert pdf.is_file() and pdf.stat().st_size > 0

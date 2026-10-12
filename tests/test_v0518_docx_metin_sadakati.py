# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — DOCX METİN SADAKATİ (XML varlıkları, sekme, satır sonu).

NEDEN VAR: `oa_ingest.docx_isle` word/document.xml'den etiketleri siliyor ama
XML varlıklarını ÇÖZMÜYORDU: belgede "A & B Ltd." yazan unvan modele
"A &amp; B Ltd." diye gidiyordu; `<w:tab/>` ve `<w:br/>`/`<w:cr/>` iz
bırakmadan siliniyor, kelimeler ve satırlar birleşiyordu ("Davacı:Ahmet").
Modelin okuduğu evrak metni bozuksa hukuki analiz de bozuktur (şirket unvanı,
tablo hücresi, tarih). Bu dosya düzeltmenin sözleşmesini kilitler:

  (1) beş adlandırılmış XML varlığı (&amp; &lt; &gt; &quot; &apos;) ve sayısal
      karakter başvuruları (&#…; &#x…;) TEK GEÇİŞTE çözülür — çift çözme YOK:
      belgede yazılı "&lt;" dizgesi XML'de `&amp;lt;` durur, metne "&lt;" girer;
  (2) HTML'e özgü adlar (&nbsp; &copy; …) XML'de varlık DEĞİLDİR, çözülmez;
  (3) XML'de geçersiz sayısal başvuru (0, vekil kod noktası, aralık dışı)
      çökertmez ve yutulmaz — olduğu gibi kalır;
  (4) `<w:tab/>` → sekme, `<w:br/>`/`<w:cr/>` → satır sonu; `</w:p>` ve `</w:tr>`
      satır sonu davranışı korunur; sekme DURAĞI tanımı (`<w:tab w:val=… w:pos=…/>`)
      sekme üretmez; yalnız BOŞLUK dizileri katlanır, sekme katlanmaz;
  (5) önbellek: yalnız DOCX kaydı taşıyan girdiler BİR KEZ yeniden çıkarılır —
      küresel `CIKARIM_SURUMU` artırılmaz (bütün evrakı, taranmış PDF OCR'ı
      dahil, yeniden okuturdu); PDF/UDF/düz metin girdileri HIT kalır;
  (6) determinizm: aynı DOCX → bayt-özdeş metin;
  (7) yeni desenler kapanmayan etiket selinde doğrusal kalır (ReDoS yok);
  (8) hook'un ucuz yolu (`ONBAKIS_DIZIN` satır okuması, CLAUDE.md değişmez #1)
      bozulmadı.

Fikstürlerin tamamı tmp_path'te zipfile ile üretilen sentetik DOCX'tir
(anayasa m.7: gerçek evrak, gerçek kişi, gerçek dosya numarası YOK).
"""
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys
import zipfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
INGEST = SKILLS / "oa-ingest" / "scripts" / "oa_ingest.py"
KAYIT = SKILLS / "oa-pipeline" / "scripts" / "pipeline_kayit.py"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ad] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ing():
    return _yukle("v0518_dms_ing", INGEST)


# ── sentetik DOCX üreticileri ────────────────────────────────────────────────

def _t(metin):
    """Tek koşu (run): Word'ün yazdığı gibi `xml:space="preserve"` ile."""
    return '<w:r><w:t xml:space="preserve">%s</w:t></w:r>' % metin


def _p(*icerik):
    return "<w:p>" + "".join(icerik) + "</w:p>"


def _docx(yol, govde):
    xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="%s"><w:body>%s</w:body></w:document>' % (W_NS, govde))
    with zipfile.ZipFile(yol, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("word/document.xml", xml)
    return str(yol)


def _metin(ing, yol):
    metin, yontem, teyit, _sayfa, hata, _gorsel = ing.docx_isle(yol)
    assert (yontem, hata) == ("docx", None), (yontem, hata)
    return metin


# ── (1) varlıklar tek geçişte ────────────────────────────────────────────────

def test_docx_xml_varliklari_tek_gecis_cozulur(ing, tmp_path):
    """Belgede görünen karakterler: "A & B Ltd." — modele "&amp;" DEĞİL '&' gitmeli.
    Şirket unvanı, tırnaklı alıntı ve açılı ayraç hukuki metnin olağan parçasıdır."""
    yol = _docx(tmp_path / "unvan.docx",
                _p(_t("A &amp; B Ltd. &lt;Şti.&gt; &quot;Alacaklı&quot; &apos;Borçlu&apos;")))
    assert _metin(ing, yol) == 'A & B Ltd. <Şti.> "Alacaklı" \'Borçlu\''


def test_docx_cift_kacisli_metin_cift_cozulmez(ing, tmp_path):
    """Belgede YAZILI "&lt;" dizgesi XML'de `&amp;lt;` durur. Tek geçiş onu "&lt;"
    yapar; ikinci bir geçiş '<' yapardı — belgede olmayan bir karakter üretmek
    metni UYDURMAKTIR (model, avukatın yazmadığı bir işareti okur)."""
    yol = _docx(tmp_path / "cift.docx",
                _p(_t("Belgede yazılı: &amp;lt; ve &amp;amp; ve &amp;#60; ve &amp;quot;")))
    assert _metin(ing, yol) == "Belgede yazılı: &lt; ve &amp; ve &#60; ve &quot;"


def test_docx_sayisal_karakter_basvurulari_cozulur(ing, tmp_path):
    """Ondalık (&#214;) ve onaltılık (&#x15E;, büyük/küçük rakam) başvurular Türkçe
    harfler dahil çözülür; '&' ve '<' sayısal biçimde de düz karaktere döner."""
    yol = _docx(tmp_path / "sayisal.docx",
                _p(_t("&#123;&#214;rnek&#125; &#x15E;irket &#x15e;ube &#231;&#x131; "
                      "&#38;&#x3C; a&#x1F;b")))
    assert _metin(ing, yol) == "{Örnek} Şirket Şube çı &< a\x1fb"


def test_docx_gecersiz_sayisal_basvuru_oldugu_gibi_kalir_cokmez(ing, tmp_path):
    """XML 1.0'da geçersiz kod noktaları (0, vekil D800-DFFF, 10FFFF üstü) Word'den
    çıkmaz; düşmanca/bozuk dosyada gelirse `chr()` ile ÇÖKMEK (evrak hiç okunmaz)
    ya da YUTMAK (metin sessizce eksilir) yerine başvuru aynen kalır. Aynı metindeki
    geçerli başvuru etkilenmez."""
    yol = _docx(tmp_path / "gecersiz.docx",
                _p(_t("&#214; &#0; &#xD800; &#xDFFF; &#1114112; &#x110000; sonu")))
    assert _metin(ing, yol) == "Ö &#0; &#xD800; &#xDFFF; &#1114112; &#x110000; sonu"


def test_docx_html_adlari_cozulmez(ing, tmp_path):
    """`&nbsp;`, `&copy;`, `&ouml;`, `&euro;`, `&hellip;` HTML adlarıdır; XML'de varlık
    değildir (Word onları hiç yazmaz; belgede yazılıysa `&amp;nbsp;` durur). `html.unescape`
    benzeri bir çözücü hem bunları çözer hem `&#128;` gibi başvuruları Windows-1252'ye
    eşler — ikisi de XML'e aykırıdır. Aynı metindeki `&amp;` çözülmeli."""
    yol = _docx(tmp_path / "html.docx",
                _p(_t("&nbsp;&copy; 2026 &ouml;rnek &euro; &hellip; &amp;")))
    assert _metin(ing, yol) == "&nbsp;&copy; 2026 &ouml;rnek &euro; &hellip; &"


# ── (4) sekme ve satır sonu ──────────────────────────────────────────────────

def test_docx_sekme_ve_satir_sonu_korunur(ing, tmp_path):
    """`<w:tab/>` sekme, `<w:br/>` / `<w:cr/>` / `<w:br w:type="page"/>` satır sonu
    üretir; paragraf (`</w:p>`) ve tablo satırı (`</w:tr>`) satır sonu davranışı
    aynen kalır. `<w:pPr><w:tabs><w:tab w:val=… w:pos=…/>` bir sekme DURAĞI
    tanımıdır, içerik değildir — sekme üretmez (metinde tam BİR sekme olmalı)."""
    govde = ('<w:p><w:pPr><w:tabs><w:tab w:val="left" w:pos="720"/></w:tabs></w:pPr>'
             + _t("Davacı:") + "<w:r><w:tab/></w:r>" + _t("Ahmet")
             + "<w:r><w:br/></w:r>" + _t("İkinci satır")
             + "<w:r><w:cr/></w:r>" + _t("Üçüncü satır")
             + '<w:r><w:br w:type="page"/></w:r>' + _t("Yeni sayfa")
             + "</w:p>"
             + "<w:tbl><w:tr><w:tc>" + _p(_t("Hücre 1")) + "</w:tc>"
             + "<w:tc>" + _p(_t("Hücre 2")) + "</w:tc></w:tr></w:tbl>")
    metin = _metin(ing, _docx(tmp_path / "sekme.docx", govde))
    assert metin == "Davacı:\tAhmet\nİkinci satır\nÜçüncü satır\nYeni sayfa\nHücre 1\nHücre 2"


def test_docx_ardisik_sekmeler_ve_bosluklu_sekme_katlanmaz(ing, tmp_path):
    """Boşluk katlama (`  ` → ` `) eski davranıştır ve kalır; ama sekme YAPISALDIR:
    `<w:tab/><w:tab/>` ve sekme+boşluk katlanıp tek boşluğa dönüşmez — eski-usul
    hizalamalı dilekçelerde ("Alacak\\t\\t1.000 TL") sütun bilgisi korunur."""
    govde = (_p(_t("Alacak") + "<w:r><w:tab/></w:r><w:r><w:tab/></w:r>" + _t("1.000 TL"))
             + _p(_t("Ad") + "<w:r><w:tab/></w:r>" + _t(" Soyad"))
             + _p(_t("çift  boşluk")))
    metin = _metin(ing, _docx(tmp_path / "ardisik.docx", govde))
    assert metin == "Alacak\t\t1.000 TL\nAd\t Soyad\nçift boşluk"


# ── (5) önbellek: dar işaret ─────────────────────────────────────────────────

def _imza(yol):
    return f"{os.path.getmtime(yol):.0f}-{os.path.getsize(yol)}"


def _eski_girdi(ing, yol, kayitlar):
    """v0.5.17 ve öncesinin yazdığı girdi: küresel işaret ve güvenlik sürümü GÜNCEL,
    DOCX'e özgü işaret YOK (o zaman böyle bir işaret yoktu)."""
    g = {"imza": _imza(yol), "cikarim": ing.CIKARIM_SURUMU, "guvenlik": ing._belge_guvenlik().SURUM}
    if len(kayitlar) == 1 and not str(yol).lower().endswith((".eyp", ".zip")):
        g["kayit"] = kayitlar[0]
    else:
        g["kayitlar"] = kayitlar
    return g


def _kayit(yontem, md):
    return {"yontem": yontem, "md": md, "karakter": 12, "sha": "0" * 16}


def test_docx_onbellek_yalniz_docx_kaydini_gecersiz_kilar(ing, tmp_path):
    """Eski DOCX girdisi MISS (metni bozuk çıkarılmıştı; bayat md adı geri alınır),
    aynı önbellekteki PDF girdisi HIT (küresel işaret artırılmadı — saatlerce OCR
    yeniden koşmaz). Yeni işaretli DOCX girdisi HIT: yeniden çıkarım BİR KEZ olur."""
    kok = tmp_path / "dava"; kok.mkdir()
    docx = kok / "001-sozlesme.docx"; docx.write_bytes(b"PK-sentetik")      # _tara yalnız stat okur
    pdf = kok / "002-karar.pdf"; pdf.write_bytes(b"%PDF-sentetik")
    hedef = str(kok / "_oa" / "metin")
    onbellek = {"001-sozlesme.docx": _eski_girdi(ing, docx, [_kayit("docx", "001-sozlesme.md")]),
                "002-karar.pdf": _eski_girdi(ing, pdf, [_kayit("pdf-metin(PyMuPDF)", "002-karar.md")])}

    items = {it["gorece"]: it for it in ing._tara(str(kok), hedef, onbellek, False)}
    assert items["002-karar.pdf"]["hit"] is True, "PDF girdisi HIT kalmalı (küresel işaret dokunulmadı)"
    assert items["001-sozlesme.docx"]["hit"] is False, (
        "eski DOCX girdisi MISS olmalı: metni varlık çözümsüz (bozuk) çıkarılmıştı")
    assert items["001-sozlesme.docx"]["eski_md"] == ["001-sozlesme.md"]

    isaret = getattr(ing, "DOCX_CIKARIM_SURUMU", None)
    assert isaret, "biçime özgü işaret (DOCX_CIKARIM_SURUMU) tanımlı olmalı"
    onbellek["001-sozlesme.docx"]["docx_cikarim"] = isaret
    items2 = {it["gorece"]: it for it in ing._tara(str(kok), hedef, onbellek, False)}
    assert items2["001-sozlesme.docx"]["hit"] is True, "yeni işaretli DOCX girdisi her koşuda yeniden çıkarılmamalı"
    assert items2["002-karar.pdf"]["hit"] is True


def test_docx_onbellek_arsiv_ici_docx_kaydi_da_gecersiz_kilinir(ing, tmp_path):
    """EYP/ZIP girdisi arşiv bütünüyle önbelleklenir; içinde DOCX kaydı varsa girdi
    MISS (arşiv yeniden açılır), yalnız PDF/UDF taşıyan arşiv HIT kalır."""
    kok = tmp_path / "dava"; kok.mkdir()
    eyp = kok / "003-paket.eyp"; eyp.write_bytes(b"PK-sentetik-arsiv")
    zip_ = kok / "004-ekler.zip"; zip_.write_bytes(b"PK-sentetik-arsiv-2")
    hedef = str(kok / "_oa" / "metin")
    onbellek = {
        "003-paket.eyp": _eski_girdi(ing, eyp, [_kayit("udf-yapili", "003a-paket.md"),
                                                 _kayit("docx", "003b-paket.md")]),
        "004-ekler.zip": _eski_girdi(ing, zip_, [_kayit("pdf-metin(PyMuPDF)", "004a-ekler.md"),
                                                  _kayit("duz-metin", "004b-ekler.md")]),
    }
    items = {it["gorece"]: it for it in ing._tara(str(kok), hedef, onbellek, False)}
    assert items["004-ekler.zip"]["hit"] is True, "DOCX taşımayan arşiv HIT kalmalı"
    assert items["003-paket.eyp"]["hit"] is False, "içinde DOCX kaydı olan eski arşiv girdisi MISS olmalı"
    assert items["003-paket.eyp"]["eski_md"] == ["003a-paket.md", "003b-paket.md"]


def _ingest(klasor):
    """Gerçek alt-süreç: önbellek dosyaya yazılıp sonraki sürecin onu okuması ancak
    böyle uçtan uca sınanır (bkz. test_oa_ingest.py). --ocr kapali: Tesseract gerekmez;
    --isci 1: seri yol (Windows'ta süreç havuzu kurulmaz)."""
    cp = subprocess.run([sys.executable, str(INGEST), str(klasor), "--ocr", "kapali", "--isci", "1"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    assert cp.returncode == 0, f"oa_ingest.py hata ile bitti:\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    return cp


def _ozet(cp):
    m = re.search(r"yeni: (\d+), önbellekten: (\d+)", cp.stdout)
    assert m, cp.stdout[-800:]
    return int(m.group(1)), int(m.group(2))


def test_docx_onbellek_isareti_yazilir_ve_ikinci_kosu_hit(ing, tmp_path):
    """Yazma tarafı okuma tarafıyla UYUMLU olmalı: ilk koşu işareti yalnız DOCX
    girdisine yazar (düz metin girdisi işaretsiz), küresel işaret değişmez; ikinci
    koşu ikisini de önbellekten basar. v0.5.17 önbelleği taklit edilince (işaret
    silinmiş, md bayat "&amp;" metniyle) üçüncü koşu YALNIZ DOCX'i yeniden çıkarır
    ve md'ye çözülmüş metni yazar."""
    kok = tmp_path / "dava"; kok.mkdir()
    _docx(kok / "001-sozlesme.docx", _p(_t("A &amp; B Ltd.")))
    (kok / "002-not.txt").write_text("düz metin notu", encoding="utf-8")
    hedef = kok / "_oa" / "metin"

    assert _ozet(_ingest(kok)) == (2, 0)
    onb_yol = hedef / ".ingest-onbellek.json"
    onb = json.loads(onb_yol.read_text(encoding="utf-8"))
    isaret = getattr(ing, "DOCX_CIKARIM_SURUMU", None)
    assert isaret and onb["001-sozlesme.docx"].get("docx_cikarim") == isaret
    assert "docx_cikarim" not in onb["002-not.txt"], "işaret yalnız DOCX girdisine yazılır"
    assert onb["001-sozlesme.docx"]["cikarim"] == ing.CIKARIM_SURUMU, "küresel işaret artırılmaz"
    md = hedef / onb["001-sozlesme.docx"]["kayit"]["md"]
    assert "A & B Ltd." in md.read_text(encoding="utf-8")

    assert _ozet(_ingest(kok)) == (0, 2), "ikinci koşu: DOCX da düz metin de önbellekten"

    del onb["001-sozlesme.docx"]["docx_cikarim"]                      # v0.5.17 önbelleği taklidi
    onb_yol.write_text(json.dumps(onb, ensure_ascii=False), encoding="utf-8")
    md.write_text("# bayat\n\nA &amp; B Ltd.\n", encoding="utf-8")
    assert _ozet(_ingest(kok)) == (1, 1), "üçüncü koşu: yalnız DOCX yeniden, düz metin önbellekten"
    onb3 = json.loads(onb_yol.read_text(encoding="utf-8"))
    md3 = hedef / onb3["001-sozlesme.docx"]["kayit"]["md"]
    assert "A & B Ltd." in md3.read_text(encoding="utf-8") and "&amp;" not in md3.read_text(encoding="utf-8")
    assert onb3["001-sozlesme.docx"].get("docx_cikarim") == isaret


# ── (6) determinizm ──────────────────────────────────────────────────────────

def test_docx_ayni_belge_bayt_ozdes_metin(ing, tmp_path):
    """Aynı DOCX (aynı yol iki kez; bayt-özdeş kopya başka yolda) → bayt-özdeş metin.
    Gövde yeni yolların hepsini (varlık, sayısal başvuru, sekme, satır sonu, tablo) gezer."""
    govde = (_p(_t("A &amp; B &#214;rnek") + "<w:r><w:tab/></w:r>" + _t("&quot;x&quot;")
                + "<w:r><w:br/></w:r>" + _t("&amp;lt; &nbsp;"))
             + "<w:tbl><w:tr><w:tc>" + _p(_t("H1")) + "</w:tc><w:tc>" + _p(_t("H2")) + "</w:tc></w:tr></w:tbl>")
    a = _docx(tmp_path / "a.docx", govde)
    b = _docx(tmp_path / "b.docx", govde)
    m1, m2, m3 = _metin(ing, a), _metin(ing, a), _metin(ing, b)
    assert m1.encode("utf-8") == m2.encode("utf-8") == m3.encode("utf-8")
    assert m1 == 'A & B Örnek\t"x"\n&lt; &nbsp;\nH1\nH2'


# ── (7) doğrusallık: yeni desenler etiket selinde kilitlenmez ────────────────

_SEL_BETIGI = r'''
import importlib.util, os, sys, tempfile, zipfile
spec = importlib.util.spec_from_file_location("v0518_dms_sel_ing", sys.argv[1])
ing = importlib.util.module_from_spec(spec); spec.loader.exec_module(ing)
N = 300_000
d = tempfile.mkdtemp()
for i, birim in enumerate(("<w:br ", "<w:br w:type=\"page\" ", "<w:tab ", "<w:cr ", "&#1", "&#x1", "&amp", "&")):
    yol = os.path.join(d, "sel%d.docx" % i)
    with zipfile.ZipFile(yol, "w") as z:
        z.writestr("word/document.xml", birim * (N // len(birim)))
    ing.docx_isle(yol)
    with zipfile.ZipFile(yol, "w") as z:          # tek kapanış: her açılış son '>'e kadar tarar
        z.writestr("word/document.xml", birim * (N // len(birim)) + ">")
    ing.docx_isle(yol)
print("TAMAM")
'''


def test_docx_sekme_satir_sonu_varlik_desenleri_etiket_selinde_kilitlenmez():
    """`<w:br …/>`, `<w:tab/>`, `<w:cr/>` ve `&…;` desenleri kapanmayan etiket/varlık
    selinde (300 KB, `>`siz ve tek `>`li) doğrusal kalmalı. Karesel sürüm ("[^>]*" ile
    komşu etikete taşan desen) aynı girdide saatler sürer; zaman aşımı yalnız kilitlenme
    sigortasıdır, süre iddiası değil (bkz. test_v0518_kaynak_sinirlari)."""
    p = subprocess.run([sys.executable, "-c", _SEL_BETIGI, str(INGEST)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=120)
    assert p.returncode == 0, p.stderr[-2000:]
    assert p.stdout.strip().endswith("TAMAM"), p.stdout[-500:]


# ── (8) hook'un ucuz yolu bozulmadı (CLAUDE.md değişmez #1) ──────────────────

def test_onbaks_dizin_literal_okunabilir_kaldi(ing):
    """`ONBAKIS_DIZIN` oa_ingest.py'de BASİT dize literali kalmalı: kancalar onu modülü
    yürütmeden SATIR okuyarak alır; literal bozulursa `_oa_ingest_sabit_oku` None döner
    ve her kullanıcı turunda pymupdf+PIL yükleyen tam import yedeğine düşülür."""
    pk = _yukle("v0518_dms_pk", KAYIT)
    ucuz = pk._oa_ingest_sabit_oku("ONBAKIS_DIZIN")
    assert ucuz is not None, "ONBAKIS_DIZIN artık satır okumasıyla bulunamıyor (literal bozuldu)"
    assert ucuz == ing.ONBAKIS_DIZIN == "metin-onbakis"

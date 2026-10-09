# -*- coding: utf-8 -*-
"""v0.5.18 (aday) — OCR planı (docs/OCR-IMPLEMENTATION-PLAN.md): sayfa düzeyi yönlendirme,
gerçek güven, kritik alan teyidi, sayfa başına zaman aşımı.

Bulgular (kod üzerinden ölçüldü, 2026-10-05; Fable 5.1 karşı-tez incelemesiyle):
  O-1  pdf_isle OCR kararını BELGE ORTALAMASIYLA veriyordu: 9 metin + 1 taranmış sayfa
       (ör. araya eklenmiş tebliğ mazbatası) ortalamayı geçer, taranmış sayfa UYARISIZ
       boş kalırdı — süre o sayfadan başlayabilir.
  O-2  OCR güveni hiç ölçülmüyordu; hangi sayfanın güvensiz olduğu bilinmiyordu.
  O-3  O/0, I/1, B/8, S/5 karışıklığı tebliğ tarihini/esas no'yu/TCKN'yi/IBAN'ı değiştirir;
       katı rakam deseni harfli tarihi HİÇ görmediği için süre adayı da kayboluyordu.
  O-6  Sayfa kaynağı (metin katmanı / OCR / harici OCR katmanı) künyede yoktu; tarayıcının
       görünmez OCR katmanı KESİN metin gibi (teyitsiz) sunuluyordu.
  Ayrıca: tek sayfanın OCR zaman aşımı evrakı BÜTÜNÜYLE boş döndürüyordu.
Fikstürler tmp_path'te üretilen sentetik evraktır; gerçek Tesseract gerektiren testler
paket yoksa GÖRÜNÜR biçimde atlanır.
"""
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import zipfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "ortak-avukat" / "skills"
INGEST = SKILLS / "oa-ingest" / "scripts" / "oa_ingest.py"
KA = SKILLS / "oa-ingest" / "scripts" / "kritik_alan.py"
KAPI = SKILLS / "oa-pipeline" / "scripts" / "okuma_kapisi.py"

fitz = pytest.importorskip("pymupdf")
PIL_Image = pytest.importorskip("PIL.Image")
from PIL import ImageDraw, ImageFont  # noqa: E402


def _yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ad] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def ing():
    """Her test kendi örneğini alır (monkeypatch modül global'lerini değiştiriyor)."""
    return _yukle("v0518_ocr_ing", INGEST)


@pytest.fixture(scope="module")
def ka():
    return _yukle("v0518_ocr_ka", KA)


@pytest.fixture(scope="module")
def ok():
    return _yukle("v0518_ocr_ok", KAPI)


def _tesseract_tur():
    t = shutil.which("tesseract")
    if not t and os.name == "nt":
        aday = os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Tesseract-OCR", "tesseract.exe")
        t = aday if os.path.isfile(aday) else None
    if not t:
        return None
    try:
        r = subprocess.run([t, "--list-langs"], capture_output=True, text=True, timeout=60)
    except Exception:
        return None
    return t if "tur" in (r.stdout + r.stderr).split() else None


TESSERACT = _tesseract_tur()
GERCEK_OCR = pytest.mark.skipif(TESSERACT is None, reason="Tesseract + 'tur' paketi yok — gerçek OCR testi atlandı")

METIN_SAYFASI = ("Davacı vekilinin iddiaları yerinde değildir ve reddi gerekir. Müvekkil şirket ile "
                 "davacı arasında yazılı bir sözleşme bulunmamaktadır.")
OPTS = {"ocr": "auto", "sayfa_limit": 0, "dpi": 200, "dil": "tur"}


def _taranmis_png(yol, satirlar, boyut=(1240, 1754)):
    im = PIL_Image.new("L", boyut, 255)
    c = ImageDraw.Draw(im)
    try:
        font = ImageFont.load_default(size=34)
    except TypeError:   # eski Pillow
        font = ImageFont.load_default()
    y = 120
    for s in satirlar:
        c.text((90, y), s, fill=0, font=font)
        y += 60
    im.save(yol)
    return yol


def _pdf(yol, sayfalar, tmp):
    """sayfalar: ('metin', str) | ('tarama', [satırlar]) | ('kisa', str) | ('harici', str) |
    ('bozuk', str) | ('vektor', None)"""
    doc = fitz.open()
    for i, (tur, icerik) in enumerate(sayfalar):
        s = doc.new_page()
        if tur in ("metin", "kisa"):
            y = 80
            for parca in [icerik[k:k + 70] for k in range(0, len(icerik), 70)]:
                s.insert_text((60, y), parca, fontsize=11, fontname="helv")
                y += 16
        elif tur in ("tarama", "harici"):
            png = _taranmis_png(str(pathlib.Path(tmp) / ("t%d.png" % i)), icerik if tur == "tarama" else ["x"])
            s.insert_image(s.rect, filename=png)
            if tur == "harici":   # tarayıcının görünmez OCR katmanı (Tr 3) görselin üstünde
                y = 80
                for parca in [METIN_SAYFASI[k:k + 70] for k in range(0, len(METIN_SAYFASI), 70)]:
                    s.insert_text((60, y), parca, fontsize=11, fontname="helv", render_mode=3)
                    y += 16
        elif tur == "bozuk":
            s.insert_text((60, 80), icerik, fontsize=11, fontname="helv")
        elif tur == "vektor":
            for k in range(260):
                x, y = 40 + (k % 26) * 20, 60 + (k // 26) * 30
                s.draw_rect(fitz.Rect(x, y, x + 8, y + 12), color=(0, 0, 0), fill=(0, 0, 0))
    doc.save(str(yol))
    doc.close()
    return str(yol)


def _sahte_ocr(ing, monkeypatch, cevap="SAHTE OCR METNİ " * 6, zaman_asimi_sayfa=None, guven=None):
    """ocr_png_ayrintili'yi sahteyle değiştirir; PNG adından sayfa no çıkarır (p{i:03d}_d{n})."""
    cagrilar = []

    def sahte(png, dil, psm="3"):
        ad = os.path.basename(png)
        sayfa = int(ad[1:4]) + 1
        cagrilar.append((sayfa, psm))
        if zaman_asimi_sayfa == sayfa:
            raise subprocess.TimeoutExpired(cmd="tesseract", timeout=600)
        return "%s sayfa %d" % (cevap, sayfa), None, guven

    monkeypatch.setattr(ing, "ocr_png_ayrintili", sahte)
    monkeypatch.setattr(ing, "TESSERACT", "sahte-tesseract")
    return cagrilar


# ---------------------------------------------------------------- O-1 / O-6 sayfa yönlendirme
def test_karma_pdf_taranmis_sayfa_artik_OCRlanir(ing, tmp_path, monkeypatch):
    yol = _pdf(tmp_path / "karma.pdf", [("metin", METIN_SAYFASI), ("metin", METIN_SAYFASI),
                                         ("tarama", ["TEBLIG MAZBATASI"])], tmp_path)
    cagrilar = _sahte_ocr(ing, monkeypatch)
    ek = {}
    metin, yontem, teyit, n, hata, bos = ing.pdf_isle(yol, OPTS, str(tmp_path), ek)
    assert yontem == "pdf-karma" and teyit is True and n == 3
    assert ek["sayfa_kaynaklari"] == {"metin": "1-2", "ocr": "3"}
    assert {s for s, _ in cagrilar} == {3}, "yalnız taranmış sayfa OCR'lanmalı"
    assert "SAHTE OCR METNİ" in metin.split("<!-- --- sayfa 3 --- -->")[1]
    assert "Davacı vekilinin" in metin.split("<!-- --- sayfa 3 --- -->")[0].replace("\n", " ") or \
        "Davac" in metin.split("<!-- --- sayfa 3 --- -->")[0]
    assert "KARMA PDF" in hata


def test_kisa_imza_sayfasi_karma_sayilmaz_cikti_BAYT_BAYT_eski(ing, tmp_path, monkeypatch):
    """Görselsiz kısa sayfa (imza/kapak) OCR'a gitmez; tamamı metin PDF'in çıktısı eskisiyle
    aynıdır — her UYAP kararının son sayfası 'karma' sayılıp alarm yorgunluğu doğmasın."""
    yol = _pdf(tmp_path / "imza.pdf", [("metin", METIN_SAYFASI), ("kisa", "Hakim e-imzalidir")], tmp_path)
    cagrilar = _sahte_ocr(ing, monkeypatch)
    ek = {}
    sonuc = ing.pdf_isle(yol, OPTS, str(tmp_path), ek)
    doc = fitz.open(yol)
    beklenen = "".join("\n<!-- --- sayfa %d --- -->\n" % (i + 1) + p.get_text("text") for i, p in enumerate(doc))
    doc.close()
    assert sonuc == (beklenen, "pdf-metin(PyMuPDF)", False, 2, None, [])
    assert cagrilar == [] and ek == {}


def test_karma_pdf_ocr_kapaliyken_sessiz_kalmaz(ing, tmp_path, monkeypatch):
    yol = _pdf(tmp_path / "k.pdf", [("metin", METIN_SAYFASI), ("metin", METIN_SAYFASI),
                                     ("tarama", ["EK"])], tmp_path)
    cagrilar = _sahte_ocr(ing, monkeypatch)
    _, yontem, teyit, _, hata, _ = ing.pdf_isle(yol, dict(OPTS, ocr="kapali"), str(tmp_path), {})
    assert yontem == "pdf-karma" and teyit is True
    assert "METİNSİZ" in hata and "sayfa 3" in hata
    assert cagrilar == []


def test_harici_ocr_katmani_kesin_metin_gibi_sunulmaz(ing, tmp_path, monkeypatch):
    yol = _pdf(tmp_path / "h.pdf", [("harici", None), ("metin", METIN_SAYFASI)], tmp_path)
    cagrilar = _sahte_ocr(ing, monkeypatch)
    ek = {}
    metin, yontem, teyit, _, hata, _ = ing.pdf_isle(yol, OPTS, str(tmp_path), ek)
    assert yontem == "pdf-metin(PyMuPDF)" and teyit is True
    assert "HARİCİ OCR KATMANI" in hata
    assert ek["sayfa_kaynaklari"] == {"metin": "2", "harici-ocr": "1"}
    assert cagrilar == [], "harici katman yeniden OCR'lanmaz; teyit damgası alır"


def test_arsiv_icindeki_evrakin_ocr_ust_verisi_kunyeye_ulasir(ing, tmp_path, monkeypatch):
    """Regresyon (2026-10-05): `_cikar_arsiv`, OCR üst verisi sözlüğünü (`ek`) arşivdeki
    mükerrer ad bulgusu listesiyle EZİYORDU → EYP/ZIP içindeki evrakın sayfa kaynakları,
    güveni ve kritik alan uyarıları künyeye SESSİZCE ulaşmıyor; kanonik adı aynı iki
    girdili arşivde çıkarım ÇÖKÜYORDU (kaydet_evrak: 'list' object has no attribute 'get')."""
    pdf = _pdf(tmp_path / "h.pdf", [("harici", None), ("metin", METIN_SAYFASI)], tmp_path)
    cagrilar = _sahte_ocr(ing, monkeypatch)
    for ad, girdiler in (("tek.zip", ["evrak/h.pdf"]), ("mukerrer.zip", ["evrak/h.pdf", "EVRAK/H.PDF"])):
        arsiv = tmp_path / ad
        with zipfile.ZipFile(arsiv, "w") as z:
            for g in girdiler:
                z.write(pdf, g)
        ret = ing._cikar_arsiv(str(arsiv), OPTS)
        assert ret["hata"] is None and ret["icler"], ret
        for ic in ret["icler"]:
            assert isinstance(ic["ocr_ek"], dict), (ad, ic["ocr_ek"])
            assert ic["ocr_ek"]["sayfa_kaynaklari"] == {"metin": "2", "harici-ocr": "1"}
        if len(girdiler) > 1:   # mükerrer nüsha bulgusu güvenlik raporunda KALIR
            assert any(b["tur"] == "arsiv-nushasi" for ic in ret["icler"]
                       for b in (ic["guvenlik"] or {}).get("bulgular", []))
    assert cagrilar == []


def test_sayfa_sinifi_bozuk_katman_ve_vektor_sayfa(ing, tmp_path):
    yol = _pdf(tmp_path / "s.pdf", [("vektor", None), ("metin", METIN_SAYFASI)], tmp_path)
    doc = fitz.open(yol)
    try:
        assert ing._pdf_sayfa_sinifi(doc[0], doc[0].get_text("text")) == "ocr", "vektöre dönmüş yazı OCR ister"
        assert ing._pdf_sayfa_sinifi(doc[1], doc[1].get_text("text")) == "metin"
    finally:
        doc.close()
    assert ing._metin_katmani_bozuk_mu("\ue001\ue002\ue003 " * 20) is True
    assert ing._metin_katmani_bozuk_mu(METIN_SAYFASI) is False


def test_aralik_ve_kaynak_ozeti(ing):
    assert ing._aralik([0, 1, 2, 5, 7, 8]) == "1-3, 6, 8-9"
    assert ing._sayfa_kaynak_ozeti(["metin", "metin", "ocr", "kisa"]) == {"metin": "1-2", "ocr": "3", "kisa": "4"}


# ---------------------------------------------------------------- zaman aşımı: okunan sayfalar korunur
def test_tek_sayfanin_zaman_asimi_evraki_bosaltmaz(ing, tmp_path, monkeypatch):
    yol = _pdf(tmp_path / "z.pdf", [("tarama", ["A"]), ("tarama", ["B"]), ("tarama", ["C"])], tmp_path)
    cagrilar = _sahte_ocr(ing, monkeypatch, zaman_asimi_sayfa=2)
    ek = {}
    metin, yontem, teyit, n, hata, bos = ing.pdf_isle(yol, OPTS, str(tmp_path), ek)
    assert yontem == "OCR-BOS" and [s for s, _ in bos] == [2]
    govdeler = metin.split("<!-- --- sayfa ")
    assert "SAHTE OCR METNİ" in govdeler[1] and "SAHTE OCR METNİ" in govdeler[3], "okunan sayfalar KORUNMALI"
    assert "SAHTE OCR METNİ" not in govdeler[2]
    assert ek["zaman_asimi_sayfalar"] == [2] and "zaman aşımı" in hata
    assert [s for s, _ in cagrilar].count(2) == 1, "zaman aşımına uğrayan sayfada retry YOK"
    assert bos[0][1], "görsel inceleme PNG'si taşınmalı"


# ---------------------------------------------------------------- O-2 güven
def test_tsv_guven_ayristirma(ing, tmp_path):
    tsv = tmp_path / "x.tsv"
    tsv.write_text(
        "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
        "1\t1\t0\t0\t0\t0\t0\t0\t1000\t2000\t-1\t\n"
        "5\t1\t1\t1\t1\t1\t100\t200\t50\t20\t95.0\tTebliğ\n"
        "5\t1\t1\t1\t1\t2\t200\t200\t50\t20\t35.0\tt@rih\n"
        "5\t1\t1\t1\t1\t3\t300\t200\t50\t20\t-1\t\n"
        "5\t1\t1\t1\t1\t4\t400\t200\t50\t20\t90.0\t \n", encoding="utf-8")
    g = ing._tsv_guven(str(tsv))
    assert g["kelime"] == 2 and g["ortalama"] == 65.0 and g["dusuk_oran"] == 0.5
    assert g["dusuk_bolgeler"] == [[20.0, 10.0, 5.0, 1.0]], "bölge sayfa yüzdesi olmalı"
    assert ing._tsv_guven(str(tmp_path / "yok.tsv")) is None, "güven UYDURULMAZ"
    bos = tmp_path / "b.tsv"
    bos.write_text("level\n", encoding="utf-8")
    assert ing._tsv_guven(str(bos))["ortalama"] is None


def test_guven_ozeti_bant_ve_dusuk_oran(ing):
    oz = ing._guven_ozeti({1: {"ortalama": 92.0, "dusuk_oran": 0.02}, 2: {"ortalama": 92.0, "dusuk_oran": 0.3,
                                                                       "dusuk_bolgeler": [[1, 2, 3, 4]]},
                           3: {"ortalama": 55.0, "dusuk_oran": 0.6}, 4: {"ortalama": None}})
    assert oz["1"]["bant"] == "yüksek"
    assert oz["2"]["bant"] == "orta" and oz["2"]["dusuk_bolgeler"] == [[1, 2, 3, 4]], \
        "ortalama yüksek ama düşük güvenli kelime oranı yüksek → bant düşer"
    assert oz["3"]["bant"] == "düşük" and oz["4"]["bant"] == "ölçülemedi"


@GERCEK_OCR
def test_gercek_tesseract_txt_tsv_metni_eski_stdout_ile_ayni(ing, tmp_path):
    """Tek geçiş txt+tsv'ye geçiş metni DEĞİŞTİRMEMELİ (evrensel satır sonuyla)."""
    png = _taranmis_png(str(tmp_path / "p000_d0.png"), ["ESAS NO: 2024/1234", "Teblig tarihi: 12.03.2025",
                                                         "Davacinin talebinin reddine."])
    eski = subprocess.run([TESSERACT, png, "-", "-l", "tur", "--psm", "3"], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout
    ing.TESSERACT = TESSERACT
    metin, hata, guven = ing.ocr_png_ayrintili(png, "tur", "3")
    assert hata is None and metin == eski
    assert guven and guven["kelime"] > 3 and guven["ortalama"] is not None
    m2, h2 = ing.ocr_png(png, "tur")
    assert (m2, h2) == (metin, None), "ocr_png (metin, hata) sözleşmesi korunur"


# ---------------------------------------------------------------- O-3 kritik alan
def test_kritik_alan_supheli_alanlari_isaretler_ASLA_duzeltmez(ka):
    metin = ("<!-- --- sayfa 1 --- -->\nESAS NO: 2O24/1234 KARAR NO: 2025/567\n"
             "Tebliğ tarihi: 12.O3.2025 olup düzenleme tarihi 31.02.2025.\n"
             "<!-- --- sayfa 2 --- -->\nT.C. Kimlik No: 12345678901\n"
             "IBAN: TR33 0006 1005 1978 6457 8413 27\nIBAN: TR33 OOO6 1005 1978 6457 8413 26\n")
    kalemler = ka.tara(metin)
    ozet = {(k["sayfa"], k["tur"], k["ham"]) for k in kalemler}
    assert (1, "tarih", "12.O3.2025") in ozet and (1, "tarih", "31.02.2025") in ozet
    assert (1, "esas_no", "2O24/1234") in ozet
    assert (2, "tckn", "12345678901") in ozet
    assert (2, "iban", "TR330006100519786457841327") in ozet and (2, "iban", "TR33OOO6100519786457841326") in ozet
    satir = "\n".join(ka.md_satirlari(kalemler))
    assert "DÜZELTİLMEDİ" in satir and "doğrulandı" in satir


def test_kritik_alan_gecerli_ve_maskeli_degerleri_isaretlemez(ka):
    metin = ("Tebliğ tarihi: 12.03.2025. ESAS NO: 2024/1234 KARAR NO: 2025/567. "
             "T.C. Kimlik No: 10000000146. Kimlik No: 123*****456. IBAN: TR33 0006 1005 1978 6457 8413 26. "
             "Tribünde trafik vardı; Trabzon yolu. Serbest TR330006100519786457841326 hesabı.")
    assert ka.tara(metin) == []


def test_kritik_alan_yil_araligi_sabit_deterministik(ka):
    assert (ka.YIL_ALT, ka.YIL_UST) == (1950, 2099)
    assert ka.tara("Tebliğ tarihi 01.01.2095") == []
    assert ka.tara("Tebliğ tarihi 01.01.2925")[0]["neden"].startswith("mantıksız yıl")


def test_ocr_ek_tamamla_karma_pdfte_yalniz_ocr_sayfalarini_tarar(ing):
    metin = ("\n<!-- --- sayfa 1 --- -->\nTebliğ tarihi: 12.O3.2025\n"
             "\n<!-- --- sayfa 2 --- -->\nTebliğ tarihi: 14.O3.2025\n")
    ek = ing._ocr_ek_tamamla(metin, "pdf-karma", {"sayfa_kaynaklari": {"metin": "1", "ocr": "2"}})
    assert [k["ham"] for k in ek["dogrulama_gerekli"]] == ["14.O3.2025"], "metin katmanı sayfası taranmaz"
    assert ing._ocr_ek_tamamla(metin, "udf-yapili", {}) == {}, "OCR'sız evrakta kritik alan taraması yok"


# ---------------------------------------------------------------- süre adayı: harfli tarih kaybolmaz
def test_ocr_bos_sayfa_esiginin_iki_yani(ing):
    """Eşik kenarı (bağımsız güvenlik incelemesi önerisi): nöbetçi uçtan uca testinin fikstürü
    eşiğin belirgin üstüne taşındığı için kenar AYRICA kilitlenir — sayfa başına TAM 49 anlamlı
    karakter YETERSİZ, TAM 50 YETERLİ (kelimelerden oluşan, çöp-skoru temiz metin)."""
    esik = ing.OCR_BOS_ESIK_KARAKTER_SAYFA
    assert esik == 50

    def tam_anlamli(n):
        s, say = " ".join(["Sentetik"] * 10), 0
        for i, c in enumerate(s):
            say += not c.isspace()
            if say == n:
                return s[: i + 1]

    alti, tam = tam_anlamli(esik - 1), tam_anlamli(esik)
    assert (ing.anlamli(alti), ing.anlamli(tam)) == (esik - 1, esik)
    assert ing._cop_skor(alti) < 1.0          # YETERSİZ kararı çöp-skorundan DEĞİL, eşikten gelir
    assert ing._ocr_kalite_yeterli_mi(alti, 1) is False
    assert ing._ocr_kalite_yeterli_mi(tam, 1) is True
    assert ing._ocr_kalite_yeterli_mi(tam, 2) is False      # eşik SAYFA BAŞINA ölçülür


def test_sure_adayi_onerileri_EN_TEMKINLIDEN_siralanir(ok):
    """v0.5.18: önerilen komut adayların İLKİNİ kullanır — belgenin yargı kolu belli değilken
    geç tarih hak kaybettirir. Sıra katalogdan (oa-sure TEK kaynak) doğrulanır: en kısa süre
    önce; eşit sürede adli tatilde UZAMAYAN kural önce. Her aday katalogda VAR olmalı."""
    katalog = json.loads((SKILLS / "oa-sure" / "scripts" / "sure_kurallari.json")
                         .read_text(encoding="utf-8"))["kurallar"]

    def anahtar(k):
        kural = katalog[k]
        assert kural["birim"] in ("gun", "hafta"), (k, kural["birim"])
        return (kural["miktar"] * (7 if kural["birim"] == "hafta" else 1), kural["adli_tatil"] != "uygulanmaz")

    for sinif, oneri in ok.SURE_ADAYI_ONERI.items():
        assert all(k in katalog for k in oneri["kural"]), (sinif, oneri["kural"])
        assert oneri["kural"] == sorted(oneri["kural"], key=anahtar), (sinif, oneri["kural"])
    assert "iik_odeme_emrine_itiraz" in ok.SURE_ADAYI_ONERI["odeme_emri"]["kural"]
    assert ok.SURE_ADAYI_ONERI["karar"]["kural"][0] == "iik_istinaf"   # tatilde uzamaz → en erken


def test_sure_adayi_harfli_ocr_tarihini_SUPHELI_olarak_tasir(ok, tmp_path):
    hedef = tmp_path / "_oa" / "metin"
    hedef.mkdir(parents=True)
    (hedef / "001-tebligat.md").write_text("# 001\n\n---\nTebliğ tarihi: 12.O3.2025\n", encoding="utf-8")
    kunye = {"kayitlar": [{"no": "001", "ad": "tebligat", "kaynak": "001-tebligat.pdf", "md": "001-tebligat.md",
                           "tur_tahmini": "tebligat", "teyit_gerek": True}]}
    adaylar = ok.sure_adaylari(kunye, str(tmp_path))
    assert len(adaylar) == 1
    t = adaylar[0]["tarih_adaylari"]
    assert t and t[0]["tarih"] == "12.O3.2025" and t[0]["supheli"] is True and t[0]["iso"] is None, \
        "katı desen bu tarihi görmez; eskiden 'süre adayı yok' denirdi"


# ---------------------------------------------------------------- O-4 motor yönlendiricisi (sahte Paddle)
PADDLE = SKILLS / "oa-ingest" / "scripts" / "paddle_isci.py"
_SAHTE_PADDLE = '''# SAHTE PADDLE İŞÇİSİ — yalnız test (gerçek paddle_isci.py ile aynı JSON sözleşmesi)
import json, os, sys
if "--kontrol" in sys.argv:
    print(json.dumps({"hazir": True, "motor": {"ad": "sahte"}})); sys.exit(0)
mod = os.environ.get("OA_PADDLE_SAHTE_MOD", "iyi")
if mod == "iyi":
    m = "Davacı vekili tarafından dava dilekçesi ile mahkeme kararı ve tebliğ tarihi hakkında itiraz edilmiştir."
    print(json.dumps({"metin": m, "satirlar": [{"metin": m, "skor": 0.97, "kutu": [0, 0, 9, 9]}]}))
elif mod == "cop":
    m = "8 8 8 1 1 1 0 0 0 Xq Zw Vb Kj " * 6
    print(json.dumps({"metin": m, "satirlar": [{"metin": m, "skor": 0.99, "kutu": [0, 0, 9, 9]}]}))
else:
    print(json.dumps({"hata": "sahte işçi hatası"})); sys.exit(2)
'''


@pytest.fixture()
def sahte_paddle(tmp_path, monkeypatch):
    isci = tmp_path / "sahte_paddle.py"
    isci.write_text(_SAHTE_PADDLE, encoding="utf-8")
    (tmp_path / "modeller").mkdir()
    monkeypatch.setenv("OA_PADDLE_PY", sys.executable)
    monkeypatch.setenv("OA_PADDLE_ISCI", str(isci))
    monkeypatch.setenv("OA_PADDLE_MODEL_DIZIN", str(tmp_path / "modeller"))
    return isci


def test_paddle_motoru_istenince_kullanilir_ve_kaydedilir(ing, tmp_path, monkeypatch, sahte_paddle):
    yol = _pdf(tmp_path / "p.pdf", [("tarama", ["A"])], tmp_path)
    cagrilar = _sahte_ocr(ing, monkeypatch)
    ek = {}
    metin, yontem, *_ = ing.pdf_isle(yol, dict(OPTS, ocr_motor="paddle"), str(tmp_path), ek)
    ing._ocr_ek_tamamla(metin, yontem, ek)
    assert "Davacı vekili" in metin and cagrilar == [], "Tesseract çağrılmamalı"
    assert ek["ocr_motor"] == {"istenen": "paddle", "kullanilan": {"paddle": "1"}, "yedek": []}
    assert ek["sayfa_guven"][1]["motor"] == "paddle"


def test_paddle_hazir_degilse_tesseracta_duser_ve_NEDENI_yazilir(ing, tmp_path, monkeypatch):
    yol = _pdf(tmp_path / "p.pdf", [("tarama", ["A"])], tmp_path)
    cagrilar = _sahte_ocr(ing, monkeypatch)
    ek = {}
    metin, yontem, *_ = ing.pdf_isle(yol, dict(OPTS, ocr_motor="paddle", paddle_hata="model dizini yok"),
                                     str(tmp_path), ek)
    ing._ocr_ek_tamamla(metin, yontem, ek)
    assert "SAHTE OCR METNİ" in metin and cagrilar
    assert ek["ocr_motor"]["kullanilan"] == {"tesseract": "1"}
    assert "model dizini yok" in ek["ocr_motor"]["yedek"][0]["neden"], "sessiz yedek YOK"


def test_auto_paddle_yalniz_basarisiz_sayfada_ve_olcutle_kabul(ing, tmp_path, monkeypatch, sahte_paddle):
    """Tesseract sayfayı okuyamadı (boş): auto, Paddle'ı dener; Türkçe ve kaliteli çıktı kabul edilir.
    Tesseract'ın okuduğu sayfaya Paddle HİÇ dokunmaz."""
    yol = _pdf(tmp_path / "a.pdf", [("tarama", ["A"]), ("tarama", ["B"])], tmp_path)

    def sahte(png, dil, psm="3"):
        sayfa = int(os.path.basename(png)[1:4]) + 1
        return ("", None, None) if sayfa == 1 else ("Tesseract okudu " * 8, None, None)

    monkeypatch.setattr(ing, "ocr_png_ayrintili", sahte)
    monkeypatch.setattr(ing, "TESSERACT", "sahte")
    ek = {}
    metin, yontem, teyit, n, hata, bos = ing.pdf_isle(yol, dict(OPTS, ocr_motor="auto"), str(tmp_path), ek)
    ing._ocr_ek_tamamla(metin, yontem, ek)
    assert yontem == "OCR(pdf-tarama)" and bos == []
    assert "Davacı vekili" in metin.split("<!-- --- sayfa 2 --- -->")[0]
    assert "Tesseract okudu" in metin.split("<!-- --- sayfa 2 --- -->")[1]
    assert ek["ocr_motor"]["kullanilan"] == {"paddle": "1", "tesseract": "2"}


def test_auto_paddle_cop_ciktisi_REDDEDILIR(ing, tmp_path, monkeypatch, sahte_paddle):
    """Yüksek güvenli ama Türkçe olmayan çöp (rakam halüsinasyonu) kabul edilmez; sayfa OCR-BOŞ kalır."""
    monkeypatch.setenv("OA_PADDLE_SAHTE_MOD", "cop")
    yol = _pdf(tmp_path / "c.pdf", [("tarama", ["A"])], tmp_path)
    monkeypatch.setattr(ing, "ocr_png_ayrintili", lambda png, dil, psm="3": ("", None, None))
    monkeypatch.setattr(ing, "TESSERACT", "sahte")
    ek = {}
    metin, yontem, teyit, n, hata, bos = ing.pdf_isle(yol, dict(OPTS, ocr_motor="auto"), str(tmp_path), ek)
    ing._ocr_ek_tamamla(metin, yontem, ek)
    assert yontem == "OCR-BOS" and [s for s, _ in bos] == [1]
    assert "8 8 8" not in metin
    assert "Türkçe isabet" in ek["ocr_motor"]["yedek"][0]["neden"]


def test_paddle_iscisi_model_yoksa_AGA_CIKMADAN_reddeder(tmp_path):
    cp = subprocess.run([sys.executable, str(PADDLE), "--kontrol", "--model-dizin", str(tmp_path / "yok")],
                        capture_output=True, text=True, encoding="utf-8",
                        env=dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1"))
    assert cp.returncode == 2
    assert "indirme YAPILMAZ" in json.loads(cp.stdout.strip())["hata"]


def test_ocr_motoru_onbellek_anahtarinda(ing, tmp_path):
    """Başka motorla (ya da Paddle hazır değilken Tesseract'a düşerek) OCR'lanmış kayıt istenen motorla
    yeniden okunur; varsayılan (tesseract) koşuda eski önbellek AYNEN geçerlidir."""
    kaynak = tmp_path / "dava"
    kaynak.mkdir()
    png = kaynak / "001-tarama.png"
    PIL_Image.new("L", (20, 20), 255).save(png)
    hedef = kaynak / "_oa" / "metin"
    hedef.mkdir(parents=True)
    (hedef / "001-tarama.md").write_text("# 001\n\n---\nmetin\n", encoding="utf-8")
    imza = "%.0f-%d" % (os.path.getmtime(png), os.path.getsize(png))
    bg = ing._belge_guvenlik()
    onb = {"001-tarama.png": {"imza": imza, "guvenlik": bg.SURUM, "cikarim": ing.CIKARIM_SURUMU,
                              "kayit": {"yontem": "OCR(goruntu)", "md": "001-tarama.md"}}}
    it = ing._tara(str(kaynak), str(hedef), onb, False, "tesseract")[0]
    assert it["hit"] is True
    it = ing._tara(str(kaynak), str(hedef), onb, False, "paddle")[0]
    assert it["hit"] is False and it["eski_md"] == ["001-tarama.md"]


def test_durum_md_ocr_teyit_bolumu(tmp_path):
    """Akışın _oa/DURUM.md halkası: OCR'a özgü teyit işaretleri durum panosuna ulaşır."""
    pk = _yukle("v0518_ocr_pk", SKILLS / "oa-pipeline" / "scripts" / "pipeline_kayit.py")
    hedef = tmp_path / "_oa" / "metin"
    hedef.mkdir(parents=True)
    kunye = {"kayitlar": [
        {"kaynak": "001-karar.pdf", "md": "001-karar.md", "yontem": "pdf-karma",
         "sayfa_kaynaklari": {"metin": "1-2", "ocr": "3"},
         "dogrulama_gerekli": [{"sayfa": 3, "tur": "tarih", "ham": "12.O3.2025", "neden": "x"}],
         "ocr_guven": {"3": {"ortalama": 55.0, "bant": "düşük"}}},
        {"kaynak": "002-temiz.udf", "md": "002-temiz.md", "yontem": "udf-yapili"}]}
    (hedef / "00-kunye.json").write_text(json.dumps(kunye, ensure_ascii=False), encoding="utf-8")
    u = pk._ocr_teyit_uyarisi(str(tmp_path))
    assert len(u) == 1 and "karma PDF — OCR sayfa 3" in u[0] and "🔎 1 şüpheli kritik alan (tarih)" in u[0]
    assert "düşük/ölçülemeyen OCR güveni: sayfa 3" in u[0]


# ---------------------------------------------------------------- uçtan uca (gerçek Tesseract)
@GERCEK_OCR
def test_uctan_uca_karma_pdf_kunye_md_ve_onbellek(tmp_path):
    d = tmp_path / "dava"
    d.mkdir()
    _pdf(d / "001-karar.pdf", [("metin", METIN_SAYFASI), ("metin", METIN_SAYFASI),
                               ("tarama", ["TEBLIG MAZBATASI", "Teblig tarihi: 12.03.2025",
                                           "Esas No: 2024/1234"])], tmp_path)
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1",
               OA_TESSERACT_YOL=TESSERACT)
    cp = subprocess.run([sys.executable, str(INGEST), str(d), "--isci", "1"], capture_output=True, text=True,
                        encoding="utf-8", errors="replace", env=env)
    assert cp.returncode == 0, cp.stderr[-2000:]
    hedef = d / "_oa" / "metin"
    k = json.loads((hedef / "00-kunye.json").read_text(encoding="utf-8"))["kayitlar"][0]
    assert k["yontem"] == "pdf-karma" and k["teyit_gerek"] is True
    assert k["sayfa_kaynaklari"] == {"metin": "1-2", "ocr": "3"}
    assert "3" in k["ocr_guven"] and k["ocr_guven"]["3"]["ortalama"] is not None
    md = (hedef / k["md"]).read_text(encoding="utf-8")
    assert "- Sayfa kaynakları: metin katmanı 1-2 · OCR 3" in md
    onb = json.loads((hedef / ".ingest-onbellek.json").read_text(encoding="utf-8"))
    assert all(v.get("cikarim") == "1.9" for v in onb.values())

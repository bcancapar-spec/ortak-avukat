# -*- coding: utf-8 -*-
"""oa-ingest — P0-9 OCR-NÖBETÇİSİ testleri.

Saha kanıtı (Denizli 307, _oa/metin — okuma amaçlı referans, DEĞİŞTİRİLMEDİ):
60 OCR evrağının 5'i sessizce boş/çöp kalmıştı (008, 000a, 000c, 143, 144 —
ikisi müvekkil delili). Zincir: ① OCR çıktısı kalite denetimi (boş-eşik:
sayfa başına < OCR_BOS_ESIK_KARAKTER_SAYFA anlamlı karakter + çöp-skor:
alfasayısal oran/tek-karakter kelime oranı) → ② deterministik retry
(DPI yükselt / PSM değişimi / yönelim) → ③ hâlâ çökükse PyMuPDF/Pillow ile
sayfa görselleri `_oa/metin/gorsel/<evrak>/pNN.png` + künyede "OCR-BOŞ →
GÖRSEL İNCELEME GEREK" damgası (YÜKLENEMEDİ DEĞİL, işlendi de DEĞİL) +
00-INDEX.md'de görünür 🔴 işaret. Görsel YALNIZ çöken sayfalar için üretilir
(hedefli — dünkü 228-PNG israfı tekrarlanmaz); sağlıklı evrakta HİÇ üretilmez.

Bu dosya iki katman test eder:
  (A) Birim testleri (Tesseract/PyMuPDF GEREKMEZ) — saf kalite-kapısı
      fonksiyonları (_cop_skor, _ocr_kalite_yeterli_mi) doğrudan içe
      aktarılıp denetlenir; ayrıca saha referansındaki GERÇEK OCR çıktısı
      (008/143/000a) üzerinde kapının doğru sayfaları yakaladığı kanıtlanır.
  (B) Uçtan uca testler (gerçek Tesseract + PyMuPDF GEREKİR — bu makinede
      kuruludur; yoksa skip edilir): sentetik BOŞ taranan PDF → damga+görsel
      üretilir; sentetik SAĞLIKLI taranan PDF → hiçbir görsel/damga üretilmez;
      künye sayaçları (`ocr_bos_evrak`) tutarlı kalır.
"""
import importlib.util
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins" / "ortak-avukat" / "skills" / "oa-ingest" / "scripts" / "oa_ingest.py"
SAHA_REFERANS = pathlib.Path(
    r"C:\Users\pc\Downloads\uyap-evraklar\2026_307_Denizli_8._Asliye_Hukuk_Mahkemesi\_oa\metin"
)

TESSERACT_YOK = shutil.which("tesseract") is None


def _oi():
    """oa_ingest.py'yi doğrudan içe aktarır (birim testleri için — Tesseract/
    subprocess gerektirmez, yalnız saf Python fonksiyonlarını çağırır)."""
    spec = importlib.util.spec_from_file_location("oa_ingest_ocr_nobetci_birim", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _kos(klasor):
    assert SCRIPT.is_file(), f"oa_ingest.py bulunamadı: {SCRIPT}"
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(klasor), "--ocr", "auto", "--isci", "1"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def _kunye(klasor):
    yol = pathlib.Path(klasor) / "_oa" / "metin" / "00-kunye.json"
    return json.loads(yol.read_text(encoding="utf-8"))


def _index(klasor):
    return (pathlib.Path(klasor) / "_oa" / "metin" / "00-INDEX.md").read_text(encoding="utf-8")


def _sayfalari_ayikla(md_metni):
    """md gövdesindeki '<!-- --- sayfa N --- -->' ayraçlarına göre sayfa
    metinlerini döndürür — saha referans .md dosyalarını test girdisi yapmak için."""
    ayrac = re.compile(r"<!-- --- sayfa (\d+) --- -->\n?")
    eslesmeler = list(ayrac.finditer(md_metni))
    sayfalar = []
    for i, m in enumerate(eslesmeler):
        s = m.end()
        e = eslesmeler[i + 1].start() if i + 1 < len(eslesmeler) else len(md_metni)
        sayfalar.append(md_metni[s:e])
    return sayfalar


# ═════════════════════════════════════════════════════════════════════════
# (A) BİRİM TESTLERİ — Tesseract/PyMuPDF GEREKMEZ
# ═════════════════════════════════════════════════════════════════════════

def test_cop_skor_bos_metin_tavan_dokunur():
    oi = _oi()
    assert oi._cop_skor("") == 1.0
    assert oi._cop_skor("   \n\n  ") == 1.0


def test_cop_skor_temiz_metin_sifir():
    oi = _oi()
    temiz = "Bu makul uzunlukta gerçek bir cümledir ve gayet okunaklıdır."
    assert oi._cop_skor(temiz) == 0.0


def test_ocr_kalite_yeterli_mi_bos_esik_yakalar():
    oi = _oi()
    # sayfa başına OCR_BOS_ESIK_KARAKTER_SAYFA'nın (50) altı → yetersiz
    assert oi._ocr_kalite_yeterli_mi("kisa", 1) is False
    assert oi._ocr_kalite_yeterli_mi("", 1) is False


def test_ocr_kalite_yeterli_mi_yeterli_metinde_gecer():
    oi = _oi()
    yeterli = "Bu makul uzunlukta gerçek bir cümledir ve elli karakterin üstündedir gayet."
    assert len(yeterli) > oi.OCR_BOS_ESIK_KARAKTER_SAYFA
    assert oi._ocr_kalite_yeterli_mi(yeterli, 1) is True


def test_ocr_kalite_yeterli_mi_cop_skor_yakalar():
    oi = _oi()
    # uzun (boş-eşiği aşar) AMA alfasayısal oranı düşük + tek-karakter kelime oranı yüksek → çöp
    cop_metin = " ".join(["â", "î", "ş", "%", "&", "#"] * 20)
    assert len(cop_metin) > oi.OCR_BOS_ESIK_KARAKTER_SAYFA
    assert oi._ocr_kalite_yeterli_mi(cop_metin, 1) is False


@pytest.mark.skipif(not SAHA_REFERANS.is_dir(), reason="saha referans klasörü bu makinede yok")
@pytest.mark.parametrize("dosya, boyle_sayfalar", [
    ("000a-nilfratgrhandelilleri_henuz_sunulmayan_EYP_ici_CamScanner_07.07.2026_12.26.pdf.md",
     {1, 2, 3}),
    ("143-Dosyaya_Eklenecek_Evrak.md", {53, 54, 55, 56, 57, 58, 59, 60}),
])
def test_kalite_kapisi_saha_referansindaki_bos_sayfalari_yakalar(dosya, boyle_sayfalar):
    """P0-9 kalite kapısı, saha referansındaki (Denizli 307, salt-okunur) GERÇEK
    OCR çıktısında elle tespit edilmiş boş sayfaları YAKALAR — kapının kendisi
    bu dosyayı DEĞİŞTİRMEZ, yalnız içeriğini okur."""
    oi = _oi()
    md_yol = SAHA_REFERANS / dosya
    if not md_yol.is_file():
        pytest.skip(f"saha referans dosyası yok: {dosya}")
    sayfalar = _sayfalari_ayikla(md_yol.read_text(encoding="utf-8"))
    yetersiz = {i + 1 for i, s in enumerate(sayfalar) if not oi._ocr_kalite_yeterli_mi(s, 1)}
    assert boyle_sayfalar.issubset(yetersiz), (
        f"{dosya}: beklenen boş sayfalar {boyle_sayfalar} yetersiz kümesinde değil ({yetersiz})"
    )


# ═════════════════════════════════════════════════════════════════════════
# (B) UÇTAN UCA — gerçek Tesseract + PyMuPDF/Pillow gerekir
# ═════════════════════════════════════════════════════════════════════════

@pytest.mark.skipif(TESSERACT_YOK, reason="Tesseract PATH'te değil")
def test_bos_taranan_pdf_ocr_bos_damgalanir_ve_gorsel_uretilir(tmp_path):
    fitz = pytest.importorskip("fitz")
    doc = fitz.open()
    doc.new_page()   # embedded metin YOK → OCR tetiklenir; tamamen boş sayfa → tesseract "" döner
    doc.new_page()
    doc.save(str(tmp_path / "005-bos-tarama.pdf"))
    doc.close()

    cp = _kos(tmp_path)
    assert cp.returncode == 0, f"STDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"

    kunye = _kunye(tmp_path)
    assert kunye["ocr_bos_evrak"] == 1, kunye
    kayit = kunye["kayitlar"][0]
    assert kayit["ocr_durum"] == "OCR-BOŞ → GÖRSEL İNCELEME GEREK"
    assert kayit["ocr_bos_sayfalar"] == [1, 2]
    assert kayit["gorsel_klasor"] == "gorsel/005-bos-tarama"
    assert kayit["teyit_gerek"] is True   # OCR-BOŞ da 'teyit gerek' hattında kalır — kayıp yok

    gklasor = tmp_path / "_oa" / "metin" / kayit["gorsel_klasor"]
    assert gklasor.is_dir()
    pngler = sorted(p.name for p in gklasor.glob("p*.png"))
    assert pngler == ["p001.png", "p002.png"]
    for p in gklasor.glob("p*.png"):
        assert p.stat().st_size > 0

    idx = _index(tmp_path)
    assert "🔴 OCR-BOŞ (görsel inceleme gerek): **1**" in idx
    assert "gorsel/005-bos-tarama" in idx
    assert "## 🔴 OCR-BOŞ — GÖRSEL İNCELEME GEREK" in idx


@pytest.mark.skipif(TESSERACT_YOK, reason="Tesseract PATH'te değil")
def test_saglikli_taranan_pdf_gorsel_uretilmez(tmp_path):
    fitz = pytest.importorskip("fitz")
    PIL = pytest.importorskip("PIL")
    from PIL import Image, ImageDraw, ImageFont

    with tempfile.TemporaryDirectory() as kaynak_dizin:   # tmp_path DIŞINDA — yanlışlıkla ingest edilmesin
        img = Image.new("L", (1600, 300), color=255)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except Exception:
            font = ImageFont.load_default()
        metin = "SAGLIKLI TARANMIS ORNEK BELGE METNI BURADA YAZILIDIR VE OKUNABILIR OLMALIDIR"
        draw.text((20, 20), metin, fill=0, font=font)
        png_yol = pathlib.Path(kaynak_dizin) / "kaynak.png"
        img.save(png_yol)

        doc = fitz.open()
        page = doc.new_page(width=1600, height=300)
        page.insert_image(fitz.Rect(0, 0, 1600, 300), filename=str(png_yol))
        doc.save(str(tmp_path / "006-saglikli-tarama.pdf"))
        doc.close()

    cp = _kos(tmp_path)
    assert cp.returncode == 0, f"STDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"

    kunye = _kunye(tmp_path)
    assert kunye["ocr_bos_evrak"] == 0, kunye
    assert len(kunye["kayitlar"]) == 1
    kayit = kunye["kayitlar"][0]
    assert kayit["ocr_durum"] is None
    assert kayit["ocr_bos_sayfalar"] == []
    assert kayit["gorsel_klasor"] == ""
    assert kayit["yontem"] == "OCR(pdf-tarama)"
    assert kayit["karakter"] > 0

    assert not (tmp_path / "_oa" / "metin" / "gorsel").exists(), (
        "sağlıklı evrakta görsel klasörü HİÇ üretilmemeli (hedefli — israf yok)"
    )

    idx = _index(tmp_path)
    assert "🔴 OCR-BOŞ (görsel inceleme gerek): **0**" in idx
    assert "## 🔴 OCR-BOŞ" not in idx


@pytest.mark.skipif(TESSERACT_YOK, reason="Tesseract PATH'te değil")
def test_karisik_evrakta_yalniz_bos_sayfa_gorsele_girer_saglikli_sayfa_girmez(tmp_path):
    """Aynı evrak içinde bir sayfa boş bir sayfa sağlıklıysa: yalnız boş sayfa
    görsele girer (hedefli — 'tüm evrak' değil, 'çöken sayfa')."""
    fitz = pytest.importorskip("fitz")
    PIL = pytest.importorskip("PIL")
    from PIL import Image, ImageDraw, ImageFont

    with tempfile.TemporaryDirectory() as kaynak_dizin:
        img = Image.new("L", (1600, 300), color=255)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except Exception:
            font = ImageFont.load_default()
        draw.text((20, 20), "IKINCI SAYFA SAGLIKLI OKUNABILIR METIN ICERIR BURADA", fill=0, font=font)
        png_yol = pathlib.Path(kaynak_dizin) / "kaynak2.png"
        img.save(png_yol)

        doc = fitz.open()
        doc.new_page()   # sayfa 1: tamamen boş
        p2 = doc.new_page(width=1600, height=300)   # sayfa 2: sağlıklı
        p2.insert_image(fitz.Rect(0, 0, 1600, 300), filename=str(png_yol))
        doc.save(str(tmp_path / "007-karisik.pdf"))
        doc.close()

    cp = _kos(tmp_path)
    assert cp.returncode == 0, f"STDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"

    kunye = _kunye(tmp_path)
    kayit = kunye["kayitlar"][0]
    assert kayit["ocr_durum"] == "OCR-BOŞ → GÖRSEL İNCELEME GEREK"
    assert kayit["ocr_bos_sayfalar"] == [1], (
        "yalnız sayfa 1 (boş) görsele girmeli; sağlıklı sayfa 2 GİRMEMELİ"
    )
    gklasor = tmp_path / "_oa" / "metin" / kayit["gorsel_klasor"]
    pngler = sorted(p.name for p in gklasor.glob("p*.png"))
    assert pngler == ["p001.png"]

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa_ingest.py — 0. MANİFEST'in AI KATMANI: deterministik metin çıkarım motoru (v1.1)

AMAÇ (illiyet): Model artık ham PDF/TIFF/JPG'yi GÖRÜNTÜ olarak açmasın.
Her evraktan metni EN UCUZ doğru yoldan bir kez çıkar, _oa/metin/ altına
belge-başına Markdown + tek kunye.json + 00-INDEX.md yaz. Bütün oa- adımları
bundan sonra bu ucuz metni ve indeksi okur → milyonlarca token yerine yüz binler.
Bağlam KOPMAZ: her .md kaynağına (dosya+sayfa+yöntem) bağlıdır; OCR çıktısı
"⚠ teyit gerek" damgalıdır; orijinal salt-okunur arşivde durur.

v1.1 değişiklikleri (2026-07):
  - Windows/PowerShell UTF-8 çıktı güvencesi (cp1254 çökmesini önler).
  - .eyp (UYAP paketi) DESTEKLENİR — eskiden sessizce atlanıyordu (ailenin en temel
    yasağının ihlali). EYP/ZIP içinden yalnız PDF değil UDF/TIFF/DOCX de çıkarılır.
  - Önbellek ve .md anahtarı GÖRELİ YOL bazlı + kısa hash: farklı alt klasörlerdeki
    aynı adlı iki evrak birbirini artık EZMEZ.
  - Metin PDF'lerde sayfa ayracı (<!-- --- sayfa N --- -->) — 'her metin sayfaya bağlı'
    vaadi metin PDF'lerde de tutar.
  - Tesseract subprocess çıktısı UTF-8 çözülür (Türkçe OCR metni Windows'ta bozulmaz).
  - Bilinmeyen uzantı SESSİZCE ATLANMAZ; künyeye 'elle kontrol' satırıyla girer.

v1.2 değişiklikleri (2026-07):
  - Her künye kaydına içerik imzası: "sha" = sha256(metin)[:16]. Delta motoru artık
    karakter+yöntem yerine gerçek içerik hash'ine bakar (aynı karakter sayılı değişikliği
    yakalar; aynı sha farklı ad = yeniden adlandırma ipucu).
  - EYP/ZIP dalı ÖNBELLEĞE bağlandı: arşiv imzası (mtime+size) tutuyorsa içerik yeniden
    açılmaz/OCR'lanmaz; önbellekteki çoklu kayıt (onbellek[gorece]={"imza","kayitlar":[...]})
    doğrudan künyeye basılır. Tekil dosya önbelleği eski {"imza","kayit"} biçimiyle uyumludur.

v1.3 değişiklikleri (2026-07):
  - ATLA_DIZIN'den genel "metin" adı KALDIRILDI: dava klasöründe rastgele "metin" adlı
    bir alt klasör (ör. tanık beyanlarının durduğu "metin/tanık.txt") artık SESSİZCE
    atlanmıyordu — hem ailenin 'sessiz atlama yasak' kuralını hem tam_tur.py ile
    tutarlılığı bozan bir kördü (tam_tur diskte görüp künyede bulamayınca sürekli
    "KÜNYE BAYAT" diyor, oa_ingest'i tekrar koşmak DÜZELTMİYORDU). Artık yalnız fiilî
    çıktı dizini (--hedef, varsayılan `_oa/metin`) mutlak yol eşleşmesiyle budanıyor;
    `_oa` zaten ayrıca dışlandığı için varsayılan kullanımda davranış AYNI kalır.
  - ATLA_DIZIN karşılaştırması case-insensitive: artık oa-pipeline/manifest_olustur.py
    ve tam_tur.py ile aynı konvansiyonu (d.lower()) kullanır.

v1.4 değişiklikleri (2026-07):
  - KRİTİK — SESSİZ KÜLLİYAT BOZULMASI düzeltildi: `kullanilan` (md dosya-adı
    çakışma) kümesi eskiden yalnız döngü İLERLEDİKÇE doluyordu; önbellekten
    doğrudan basılan kayıtların md adları döngü BAŞINDA rezerve edilmiyordu.
    Delta iş akışında, sıralamada önbellekli kayıttan ÖNCE gelen aynı taban-adlı
    YENİ bir evrak (ör. a/001-dilekce.txt), henüz sırası gelmemiş b/001-dilekce.txt
    önbellek kaydının "001-dilekce.md" dosyasını ele geçirip SESSİZCE ÜZERİNE
    YAZIYORDU: künyede iki kayıt aynı md'ye işaret ediyor, md içeriği yalnız
    sonradan yazanınki oluyor, önbellekli kaydın çıkarılmış metni okuma
    katmanından kayboluyordu (künyedeki karakter/sha ise eski içeriği göstermeye
    devam edip md ile ÇELİŞİYORDU) — hiçbir uyarı üretilmeden. Artık önbellek
    yüklendikten hemen sonra tüm önbellekli kayıtların md adları `kullanilan`a
    baştan eklenir; yeni işlenen dosya md_yaz'da çakışmayı görür ve kisa_hash
    sonekiyle FARKLI ad alır — önbellekli md dosyaları asla ezilmez.

ÇIKARIM YOLLARI (model kurmaz, script çıkarır):
  PDF (metin katmanlı)  → PyMuPDF text            [BEDAVA, kayıpsız]
  PDF (taranmış/fontsuz) → PyMuPDF render + OCR    [OCR — ⚠ teyit]
  UDF                    → zip/content.xml         [BEDAVA]
  EYP / .zip             → aç → içindeki evrakları (PDF/UDF/TIFF/DOCX) aynı hatta ver
  TIFF/JPG/PNG/BMP       → Pillow + OCR (çok sayfa) [OCR — ⚠ teyit]
  DOCX                   → word/document.xml        [BEDAVA]

Bir PDF'in "metin mi tarama mı" olduğu ELLE değil ÖLÇÜMLE belirlenir:
çıkarılan metnin sayfa başına anlamlı karakteri eşiğin altındaysa → taranmış → OCR.

BAĞIMLILIKLAR (Windows-dostu, binary gerektirmez):
  pip install pymupdf pillow          # PDF + görüntü (saf wheel)
  OCR için (yalnız taranmış evrakta):  Tesseract kurulumu + PATH + 'tur' dil paketi
    Windows: UB-Mannheim tesseract kurucusu (kurulumda Turkish + 'Add to PATH')
    Linux:   apt-get install tesseract-ocr tesseract-ocr-tur
  Tesseract yoksa metin PDF/UDF/DOCX yine BEDAVA işlenir; yalnız taranmış
  evraklar "YÜKLENEMEDİ (OCR yok)" damgasıyla künyeye yazılır (sessiz atlama yok).

Kullanım:
  python oa_ingest.py "<dava_klasoru>"
  python oa_ingest.py "<klasor>" --ocr auto|zorla|kapali
  python oa_ingest.py "<klasor>" --ocr-sayfa-limit 2      # demo/hızlı (0 = sınırsız)
  python oa_ingest.py "<klasor>" --yeniden                # önbelleği yok say
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile, zipfile
import xml.etree.ElementTree as ET

GORUNTU = {".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp", ".gif"}
PDF, UDF, DOCX = {".pdf"}, {".udf"}, {".docx"}
ARSIV = {".zip", ".eyp"}                     # EYP = UYAP paketi (zip tabanlı)
DUZ = {".txt", ".md", ".rtf", ".html", ".htm", ".csv", ".xml"}
IC_BILINEN = PDF | UDF | DOCX | GORUNTU | DUZ  # arşiv içinde işlenecek tipler
ATLA_DIZIN = {"_oa", ".claude", "__pycache__", ".git"}
# NOT: "metin" burada YOK — genel isimle dışlama, dava klasöründeki rastgele bir
# "metin" adlı alt klasörü sessizce yutardı. Fiilî çıktı dizini (hedef) main()
# içinde os.walk sırasında mutlak yol eşleşmesiyle ayrıca budanır (bkz. main()).
ATLA_DOSYA = {"thumbs.db", "desktop.ini", ".ds_store", ".ingest-onbellek.json"}
METIN_ESIK_KARAKTER_SAYFA = 40   # sayfa başına bu kadar anlamlı karakterin altı → OCR
KAR_PER_TOKEN = 3                 # Türkçe için kaba token tahmini (~3 karakter/token)
TESSERACT = shutil.which("tesseract")
BOS_SHA = hashlib.sha256(b"").hexdigest()[:16]   # metinsiz kayıtlar için sabit içerik imzası

try:
    import fitz  # PyMuPDF
    FITZ = True
except ImportError:
    FITZ = False
try:
    from PIL import Image
    PIL = True
except ImportError:
    PIL = False


def anlamli(s):
    return len(re.sub(r"\s+", "", s or ""))


def slug(ad):
    tr = {"ç": "c", "Ç": "C", "ğ": "g", "Ğ": "G", "ı": "i", "İ": "I",
          "ö": "o", "Ö": "O", "ş": "s", "Ş": "S", "ü": "u", "Ü": "U"}
    ad = "".join(tr.get(c, c) for c in ad)
    return (re.sub(r"[^A-Za-z0-9._-]+", "_", ad).strip("_")[:80]) or "evrak"


def kisa_hash(s):
    return hashlib.sha1(s.encode("utf-8", "replace")).hexdigest()[:6]


def evrak_no_ad(dosya_adi):
    kok = os.path.splitext(dosya_adi)[0]
    m = re.match(r"^(\d{1,4})[_\-\s]+(.*)$", kok)
    no = m.group(1).zfill(3) if m else None
    geri = m.group(2) if m else kok
    tarih = None
    dm = re.search(r"(\d{2})[_.\-](\d{2})[_.\-](\d{4})", geri)
    if dm:
        tarih = f"{dm.group(1)}.{dm.group(2)}.{dm.group(3)}"
        geri = geri[:dm.start()].strip("_-. ")
    return no, geri.replace("_", " ").strip(), tarih


def ocr_png(png_yol, dil):
    """Tek PNG'yi OCR'la (Tesseract subprocess). Yoksa None."""
    if not TESSERACT:
        return None
    r = subprocess.run([TESSERACT, png_yol, "-", "-l", dil, "--psm", "3"],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600)
    return r.stdout or ""


# ---------------- çıkarım ----------------
def pdf_isle(yol, opts, tmp):
    """PyMuPDF ile metin; zayıfsa render+OCR. (metin, yontem, teyit, sayfa, hata)."""
    if not FITZ:
        return "", "hata", True, None, "PyMuPDF yok (pip install pymupdf)"
    try:
        doc = fitz.open(yol)
    except Exception as e:
        return "", "hata", True, None, f"PDF açılamadı ({e})"
    n = doc.page_count or 1
    sayfalar = [p.get_text("text") for p in doc]
    ham = "\n".join(sayfalar)
    oran = anlamli(ham) / n
    if opts["ocr"] != "zorla" and oran >= METIN_ESIK_KARAKTER_SAYFA:
        doc.close()
        metin = "".join(f"\n<!-- --- sayfa {i+1} --- -->\n" + s for i, s in enumerate(sayfalar))
        return metin, "pdf-metin(PyMuPDF)", False, n, None
    if opts["ocr"] == "kapali":
        doc.close()
        return ham, "pdf-metin(zayıf)", True, n, f"taranmış görünüyor ({oran:.0f} kar/sayfa), OCR kapalı"
    if not TESSERACT:
        doc.close()
        return ham, "pdf-metin(zayıf)", True, n, f"taranmış ({oran:.0f} kar/sayfa) ama Tesseract yok — YÜKLENEMEDİ"
    limit = opts["sayfa_limit"] or n
    parcalar = []
    for i in range(min(n, limit)):
        pix = doc[i].get_pixmap(dpi=opts["dpi"])
        p = os.path.join(tmp, f"p{i:03d}.png")
        pix.save(p)
        parcalar.append(f"\n<!-- --- sayfa {i+1} --- -->\n" + (ocr_png(p, opts["dil"]) or ""))
    doc.close()
    return "".join(parcalar), "OCR(pdf-tarama)", True, n, None


def goruntu_isle(yol, opts, tmp):
    if opts["ocr"] == "kapali":
        return "", "atlandı", True, None, "görüntü ama OCR kapalı"
    if not PIL:
        return "", "hata", True, None, "Pillow yok (pip install pillow)"
    if not TESSERACT:
        return "", "atlandı", True, None, "Tesseract yok — YÜKLENEMEDİ"
    im = Image.open(yol)
    n = getattr(im, "n_frames", 1)
    limit = opts["sayfa_limit"] or n
    parcalar = []
    for i in range(min(n, limit)):
        try:
            im.seek(i)
        except EOFError:
            break
        p = os.path.join(tmp, f"f{i:03d}.png")
        im.convert("L").save(p)
        parcalar.append(f"\n<!-- --- sayfa {i+1} --- -->\n" + (ocr_png(p, opts["dil"]) or ""))
    return "".join(parcalar), "OCR(goruntu)", True, n, None


def udf_isle(yol):
    try:
        zf = zipfile.ZipFile(yol)
    except Exception as e:
        return "", "hata", True, None, f"UDF açılamadı ({e})"
    hedef = next((a for a in zf.namelist() if a.lower().endswith("content.xml")), None)
    if not hedef:
        return "", "hata", True, None, "content.xml yok"
    ham = zf.read(hedef).decode("utf-8", "replace")
    m = re.search(r"<content>\s*<!\[CDATA\[(.*?)\]\]>\s*</content>", ham, re.S)
    if m:
        return m.group(1), "udf", False, None, None
    try:
        kok = ET.fromstring(ham)
        p = [t.strip() for t in kok.itertext() if t and t.strip()]
        if p:
            return "\n".join(p), "udf", False, None, None
    except ET.ParseError:
        pass
    kaba = re.sub(r"\s{2,}", " ", re.sub(r"<[^>]+>", " ", ham)).strip()
    if kaba:
        return "[UYARI: standart UDF çözülemedi — kaba metin]\n" + kaba, "udf(kaba)", True, None, None
    return "", "hata", True, None, "metin yok"


def docx_isle(yol):
    try:
        ham = zipfile.ZipFile(yol).read("word/document.xml").decode("utf-8", "replace")
    except Exception as e:
        return "", "hata", True, None, f"DOCX açılamadı ({e})"
    ham = ham.replace("</w:p>", "\n").replace("</w:tr>", "\n")
    return re.sub(r"[ \t]{2,}", " ", re.sub(r"<[^>]+>", "", ham)).strip(), "docx", False, None, None


def evrak_isle(yol, uz, opts, tmp_kok):
    with tempfile.TemporaryDirectory(dir=tmp_kok) as t:
        try:
            if uz in PDF:      return pdf_isle(yol, opts, t)
            if uz in UDF:      return udf_isle(yol)
            if uz in DOCX:     return docx_isle(yol)
            if uz in GORUNTU:  return goruntu_isle(yol, opts, t)
            if uz in DUZ:
                return open(yol, encoding="utf-8", errors="replace").read(), "duz-metin", False, None, None
        except subprocess.TimeoutExpired:
            return "", "zaman-asimi", True, None, "OCR 600 sn aştı"
        except Exception as e:
            return "", "hata", True, None, str(e)
    return "", "bilinmeyen", True, None, "desteklenmeyen tür"


def md_yaz(hedef, no, ad, tarih, metin, kayit, kullanilan):
    taban = f"{no or '000'}-{slug(ad)}"
    dosya = f"{taban}.md"
    if dosya in kullanilan:                       # çakışma → göreli-yol hash'i ekle
        dosya = f"{taban}-{kisa_hash(kayit['kaynak'])}.md"
    n = 2
    while dosya in kullanilan:                     # yine çakışırsa sayaç
        dosya = f"{taban}-{kisa_hash(kayit['kaynak'])}-{n}.md"
        n += 1
    kullanilan.add(dosya)
    bas = [f"# {no or '—'} · {ad}", ""]
    bas.append(f"- Kaynak evrak: `{kayit['kaynak']}`")
    if tarih:
        bas.append(f"- Tarih: {tarih}")
    bas.append(f"- Çıkarım yöntemi: **{kayit['yontem']}**"
               + (f" · sayfa: {kayit['sayfa']}" if kayit.get("sayfa") else ""))
    bas.append(f"- Karakter: {kayit['karakter']}")
    if kayit["teyit_gerek"]:
        bas.append("- ⚠ **OCR/zayıf çıkarım — künye ve sayısal veri için orijinalden TEYİT gerekir.**")
    if kayit.get("hata"):
        bas.append(f"- Not: {kayit['hata']}")
    bas.append("\n---\n")
    with open(os.path.join(hedef, dosya), "w", encoding="utf-8") as f:
        f.write("\n".join(bas) + (metin or "*(metin çıkarılamadı)*") + "\n")
    return dosya


def kaydet_evrak(metin, yontem, teyit, sayfa, hata, kaynak, no, ad, tarih, hedef, kullanilan):
    kayit = {"no": no, "ad": ad, "tarih": tarih, "kaynak": kaynak, "yontem": yontem,
             "teyit_gerek": teyit, "karakter": anlamli(metin),
             "sha": hashlib.sha256((metin or "").encode("utf-8", "replace")).hexdigest()[:16],
             "sayfa": sayfa, "hata": hata}
    kayit["md"] = md_yaz(hedef, no, ad, tarih, metin, kayit, kullanilan)
    return kayit


def main():
    ap = argparse.ArgumentParser(description="oa-ingest — deterministik metin çıkarım motoru (PyMuPDF)")
    ap.add_argument("klasor", nargs="?", default=".",
                    help="dava klasörü (verilmezse BULUNDUĞUN klasör işlenir)")
    ap.add_argument("--hedef")
    ap.add_argument("--ocr", choices=["auto", "zorla", "kapali"], default="auto")
    ap.add_argument("--dil", default="tur")
    ap.add_argument("--ocr-dpi", type=int, default=300, dest="dpi")
    ap.add_argument("--ocr-sayfa-limit", type=int, default=0, dest="sayfa_limit")
    ap.add_argument("--yeniden", action="store_true")
    a = ap.parse_args()

    if not os.path.isdir(a.klasor):
        sys.exit(f"HATA: klasör yok: {a.klasor}")
    print(f"İşlenen klasör: {os.path.abspath(a.klasor)}")
    if not FITZ:
        print("UYARI: PyMuPDF yok → PDF'ler işlenemez. Kur:  pip install pymupdf", file=sys.stderr)
    if a.ocr != "kapali" and not TESSERACT:
        print("BİLGİ: Tesseract PATH'te yok → taranmış evraklar OCR'lanamayacak "
              "(metin PDF/UDF/DOCX yine işlenir). Kur: UB-Mannheim (Win) / apt tesseract-ocr-tur (Linux).",
              file=sys.stderr)

    hedef = a.hedef or os.path.join(a.klasor, "_oa", "metin")
    os.makedirs(hedef, exist_ok=True)
    tmp_kok = tempfile.mkdtemp(prefix="oaing_")
    opts = {"ocr": a.ocr, "dil": a.dil, "dpi": a.dpi, "sayfa_limit": a.sayfa_limit}

    onbellek_yol = os.path.join(hedef, ".ingest-onbellek.json")
    onbellek = {}
    if os.path.exists(onbellek_yol) and not a.yeniden:
        try:
            onbellek = json.load(open(onbellek_yol, encoding="utf-8"))
        except Exception:
            onbellek = {}

    hedef_abs = os.path.abspath(hedef)  # yalnız FİİLÎ çıktı dizini budanır (bkz. ATLA_DIZIN notu)
    dosyalar = []
    for kok, dizinler, adlar in os.walk(a.klasor):
        dizinler[:] = [d for d in dizinler
                       if d.lower() not in ATLA_DIZIN
                       and os.path.abspath(os.path.join(kok, d)) != hedef_abs]
        for ad in adlar:
            if ad.lower() in ATLA_DOSYA:
                continue
            dosyalar.append((kok, ad))
    dosyalar.sort(key=lambda x: os.path.relpath(os.path.join(x[0], x[1]), a.klasor).lower())

    kunye, yeni, atlanan, ocr_sayisi, bilinmeyen = [], 0, 0, 0, 0
    kullanilan = set()
    # ÖNBELLEKLİ md ADLARI DÖNGÜ BAŞINDA REZERVE EDİLİR (v1.4 düzeltmesi):
    # aksi halde döngüde önbellekli kayıttan ÖNCE sırası gelen aynı taban-adlı
    # YENİ bir evrak, henüz kullanilan'a eklenmemiş bu md adını ele geçirip
    # SESSİZCE ÜZERİNE YAZAR — bkz. modül docstring'i v1.4 notu.
    if not a.yeniden:
        for onb in onbellek.values():
            kayitlar = [onb["kayit"]] if onb.get("kayit") else (onb.get("kayitlar") or [])
            for k in kayitlar:
                if k and k.get("md"):
                    kullanilan.add(k["md"])
    for kok, ad in dosyalar:
        yol = os.path.join(kok, ad)
        gorece = os.path.relpath(yol, a.klasor)
        uz = os.path.splitext(ad)[1].lower()
        no, temiz, tarih = evrak_no_ad(ad)

        if uz not in (PDF | UDF | ARSIV | DOCX | GORUNTU | DUZ):
            # SESSİZ ATLAMA YASAK — bilinmeyen uzantı künyeye 'elle kontrol' ile girer
            kunye.append({"no": no, "ad": temiz, "tarih": tarih, "kaynak": gorece,
                          "yontem": "bilinmeyen", "teyit_gerek": True, "karakter": 0,
                          "sha": BOS_SHA,
                          "sayfa": None, "hata": f"desteklenmeyen uzantı ({uz}) — elle kontrol",
                          "md": ""})
            bilinmeyen += 1
            continue

        imza = f"{os.path.getmtime(yol):.0f}-{os.path.getsize(yol)}"

        if uz in ARSIV:  # EYP / ZIP → içindeki tüm desteklenen evraklar
            # ÖNBELLEK: arşiv imzası (mtime+size) tutuyorsa içeriği yeniden AÇMA/OCR ETME;
            # önbellekteki çoklu kaydı doğrudan künyeye bas (arşiv her koşuda tekrar açılmasın).
            onb = onbellek.get(gorece)
            if (onb and onb.get("imza") == imza and isinstance(onb.get("kayitlar"), list)
                    and not a.yeniden):
                for k in onb["kayitlar"]:
                    kunye.append(k)
                    if k.get("md"):
                        kullanilan.add(k["md"])
                    ocr_sayisi += bool(k.get("teyit_gerek"))
                    if k.get("yontem") == "arşiv-boş":
                        bilinmeyen += 1
                    else:
                        atlanan += 1
                continue
            arsiv_kayitlari = []
            try:
                with tempfile.TemporaryDirectory(dir=tmp_kok) as t:
                    zipfile.ZipFile(yol).extractall(t)
                    icler = []
                    for dp, _, fs in os.walk(t):
                        for f in fs:
                            ie = os.path.splitext(f)[1].lower()
                            if ie in IC_BILINEN:
                                icler.append((os.path.join(dp, f), ie, f))
                    icler.sort(key=lambda x: x[2].lower())
                    if not icler:
                        rec = {"no": no, "ad": temiz, "tarih": tarih, "kaynak": gorece,
                               "yontem": "arşiv-boş", "teyit_gerek": True, "karakter": 0,
                               "sha": BOS_SHA, "sayfa": None,
                               "hata": "EYP/ZIP içinde desteklenen evrak yok — elle kontrol",
                               "md": ""}
                        kunye.append(rec); arsiv_kayitlari.append(rec); bilinmeyen += 1
                    for j, (ic, ie, icad) in enumerate(icler):
                        metin, y, teyit, sf, hata = evrak_isle(ic, ie, opts, tmp_kok)
                        son = "" if len(icler) == 1 else (chr(97 + j) if j < 26 else str(j))
                        ic_no = f"{no or '000'}{son}"
                        k = kaydet_evrak(metin, y, teyit, sf, hata,
                                         f"{gorece}::{icad}", ic_no,
                                         f"{temiz} (EYP içi: {icad})", tarih, hedef, kullanilan)
                        kunye.append(k); arsiv_kayitlari.append(k)
                        yeni += 1; ocr_sayisi += bool(teyit)
                # başarıyla açıldı → çoklu kaydı önbelleğe bağla (sonraki koşuda tekrar açılmaz)
                onbellek[gorece] = {"imza": imza, "kayitlar": arsiv_kayitlari}
            except Exception as e:
                # açılamadı → önbelleğe YAZMA (sonraki koşuda yeniden denensin)
                kunye.append({"no": no, "ad": temiz, "tarih": tarih, "kaynak": gorece,
                              "yontem": "hata", "teyit_gerek": True, "karakter": 0,
                              "sha": BOS_SHA, "sayfa": None,
                              "hata": f"EYP/ZIP açılamadı: {e}", "md": ""})
            continue

        # Geriye uyum: tekil dosya önbelleği eski biçimde {"imza":..., "kayit":{...}}
        onb = onbellek.get(gorece, {})
        if onb.get("imza") == imza and "kayit" in onb and not a.yeniden:
            k = onb["kayit"]
            kunye.append(k); atlanan += 1
            if k.get("md"):
                kullanilan.add(k["md"])
            ocr_sayisi += bool(k.get("teyit_gerek"))
            continue

        metin, y, teyit, sf, hata = evrak_isle(yol, uz, opts, tmp_kok)
        k = kaydet_evrak(metin, y, teyit, sf, hata, gorece, no, temiz, tarih, hedef, kullanilan)
        kunye.append(k); yeni += 1; ocr_sayisi += bool(teyit)
        onbellek[gorece] = {"imza": imza, "kayit": k}

    kunye.sort(key=lambda k: (k.get("no") or "999", k.get("kaynak", "")))
    toplam = sum(k.get("karakter") or 0 for k in kunye)
    tahmini_token = toplam // KAR_PER_TOKEN

    with open(os.path.join(hedef, "00-kunye.json"), "w", encoding="utf-8") as f:
        json.dump({"klasor": os.path.abspath(a.klasor), "toplam_evrak": len(kunye),
                   "ocr_teyit_gerek": ocr_sayisi, "bilinmeyen": bilinmeyen,
                   "toplam_karakter": toplam, "tahmini_token": tahmini_token,
                   "kayitlar": kunye}, f, ensure_ascii=False, indent=2)
    with open(os.path.join(hedef, "00-INDEX.md"), "w", encoding="utf-8") as f:
        f.write(f"# Evrak Metin İndeksi — {os.path.basename(os.path.abspath(a.klasor))}\n\n")
        f.write(f"Toplam evrak: **{len(kunye)}** · OCR/teyit gerek: **{ocr_sayisi}** · "
                f"bilinmeyen/elle: **{bilinmeyen}** · "
                f"toplam metin: ~{toplam:,} karakter (~{tahmini_token:,} token)\n\n")
        f.write("| # | Evrak | Tarih | Yöntem | ⚠ | Karakter | Dosya |\n")
        f.write("|---|-------|-------|--------|---|----------|-------|\n")
        for k in kunye:
            f.write(f"| {k.get('no') or '—'} | {k.get('ad','')} | {k.get('tarih') or ''} "
                    f"| {k.get('yontem','')} | {'⚠' if k.get('teyit_gerek') else ''} "
                    f"| {k.get('karakter') or 0} | `{k.get('md','')}` |\n")
        f.write("\n> ⚠ = OCR/zayıf çıkarım; künye ve sayısal veriyi orijinalden teyit et. "
                "Orijinal evrak salt-okunur arşivde durur.\n")
    json.dump(onbellek, open(onbellek_yol, "w", encoding="utf-8"), ensure_ascii=False)
    shutil.rmtree(tmp_kok, ignore_errors=True)

    print(f"BİTTİ · evrak: {len(kunye)} (yeni: {yeni}, önbellekten: {atlanan}, bilinmeyen: {bilinmeyen}) · "
          f"OCR/teyit: {ocr_sayisi} · ~{toplam:,} karakter (~{tahmini_token:,} token)")
    print(f"Çıktı: {hedef}  → 00-INDEX.md, 00-kunye.json, NNN-*.md")


if __name__ == "__main__":
    main()

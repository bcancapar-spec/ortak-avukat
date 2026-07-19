#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa_ingest.py — 0. MANİFEST'in AI KATMANI: deterministik metin çıkarım motoru (v1.5.1)

AMAÇ (illiyet): Model artık ham PDF/TIFF/JPG'yi GÖRÜNTÜ olarak açmasın.
Her evraktan metni EN UCUZ doğru yoldan bir kez çıkar, _oa/metin/ altına
belge-başına Markdown + tek kunye.json + 00-INDEX.md yaz. Bütün oa- adımları
bundan sonra bu ucuz metni ve indeksi okur → milyonlarca token yerine yüz binler.
Bağlam KOPMAZ: her .md kaynağına (dosya+sayfa+yöntem) bağlıdır; OCR çıktısı
"⚠ teyit gerek" damgalıdır; orijinal salt-okunur arşivde durur.

GENELLİK (kurucu ilke): Bu motor BELİRLİ bir dava/korpusa göre değil, SINIRSIZ ve
genel hukuki içeriğe/kelimeye göre çalışır. Çıkarım İÇERİK-AGNOSTİKtir: hangi evrak,
hangi hukuk dalı, hangi kelime olursa olsun aynı deterministik yolu (ölçümle tarama/
metin ayrımı, OCR eşiği, XML çözümü) izler. Hız için içerik/korpus varsayımı YAPMAZ.

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

v1.5 değişiklikleri (2026-07) — PARALEL ÇIKARIM, VERİ KAYBI KANITLI:
  Amaç: büyük külliyatta (yüzlerce evrak) çıkarımı çok-çekirdekle hızlandır; ama
  HİÇBİR veri kaybı/bozulma/determinizm kaybı olmadan. Mimari (Fable K reçetesi):
    • SAF İŞÇİ / TEK-YAZAR EBEVEYN: işçiler yalnız metin ÇIKARIR (evrak_isle),
      hiçbir paylaşılan durumu değiştirmez. md yazımı, künye, önbellek ve md-ad
      ataması TAMAMEN ebeveynde, SIRALI-İNDEKS düzeninde, tek yazarda kalır. Böylece
      v1.4'te kapatılan sessiz md-ezme paralelde HORTLAMAZ (tamamlanma sırası çıktıyı
      DEĞİŞTİRMEZ — sonuçlar özgün sıralı indekse göre birleştirilir).
    • DETERMİNİZM: çıktı çekirdek sayısından BAĞIMSIZDIR. `--isci 1` (seri) ile
      `--isci N` (paralel) BYTE-AYNI 00-kunye.json, AYNI md ad kümesi, AYNI md sha256
      üretir (tests/test_oa_ingest_paralel.py bunu kanıtlar).
    • ATOMİK YAZIM: 00-kunye.json / 00-INDEX.md / önbellek `tmp + os.replace` ile
      yazılır — çökmede yarım/kesik künye İMKANSIZ (eski tam sürüm kalır); künye EN SON
      yazılır = commit işareti. (Bu, seri kodda da açık bir felaket moduydu.)
    • MEKANİK KAPI (sessiz-atlama yasağı): üretilen kayıt sayısı beklenenle eşit
      değilse künye YAZILMAZ, hata ile çıkılır. İşçi çökerse (BrokenProcessPool) o
      evrak "işçi çöktü — elle kontrol" damgasıyla künyeye girer (asla sessiz düşmez).
    • Tesseract aşırı-aboneliği önlenir (işçi ortamında OMP_THREAD_LIMIT=1); seri
      yolda da aynı kısıt uygulanır ki OCR koşulları seri==paralel özdeş kalsın.
    • try/finally temp: her işçi kendi geçici dizinini `with` ile açar → çökmede
      müvekkil evrakının render'ları %TEMP%'te SIZMAZ (Layer 0 hijyeni).
    • KIRMIZI ÇİZGİ: hız ASLA kayıplı parametreden gelmez — dpi ve sayfa-limit
      varsayılanları düşürülmez; kazanç yalnız eşzamanlılık + önbellekten gelir.

v1.5.1 değişiklikleri (2026-07) — FABLE BACKLOG SAĞLAMLAŞTIRMA:
  (a) ARIZA SONUCU ÖNBELLEĞE YAZILMAZ: yöntem {hata, atlandı} olan kayıtlar önbelleğe
      YAZILMAZ — Tesseract/araç sonradan kurulunca "imza aynı → önbellekten bas" yolu
      bayat 'YÜKLENEMEDİ' damgasını SONSUZA dek tekrarlamasın; her koşuda yeniden
      denenirler. 'zaman-aşımı' İSTİSNA: OCR 600 sn'lik zaman-aşımı PAHALI olduğu için
      önbellekte TUTULABİLİR (aynı devasa evrakta koşu başına 10 dk tekrar beklenmesin);
      avukat gerekirse `--yeniden` ile açıkça atlar.
  (b) main() başında hedeften önceki çökmüş koşulardan kalan `.tmp-oaing-*.part`
      atomik-yazım artıkları süpürülür (_atomik_yaz zaten çökmede eski TAM sürümü
      korur; bu yalnız diskte kalan .part çöpünü temizler).
  (c) ÖNBELLEK BUDAMA: FAZ A/C sonrası, önbellekte olup diskte artık OLMAYAN (silinmiş
      kaynak) anahtarlar atılır — önbellek tek-yönlü BÜYÜMESİN, yetim md-adı rezervasyonu
      kalmasın. FAZ A HER koşuda TÜM klasörü tarar (kısmi değil) → önbellekte olup o
      koşunun `items` kümesinde OLMAYAN anahtar YALNIZ silinmiş kaynak olabilir; hâlâ
      diskte duran ama bu koşuda sırası gelmemiş bir kaynak asla bu kümenin dışında kalmaz.
  (d) POISON-EVRAK İZOLE YENİDEN DENEME: havuzda çöken (BrokenProcessPool) kalemler FAZ
      C'den ÖNCE tek-işçi (max_workers=1) izole bir havuzda BİRER BİRER yeniden denenir —
      bir "zehirli" evrak tüm havuzu düşürüp aynı batch'teki MASUM evrakları da 'işçi
      çöktü' damgasıyla sürüklemesin. Yalnız izole halde de çöken evrak nihai 'işçi çöktü'
      damgasını alır (canlı-kilit önlenir: tekrar tekrar tüm havuzu düşürmeye çalışmaz).
  (e) _ADMIN kovasına 'atlandı' ve 'zaman-aşımı' EKLENDİ: OCR hiç YAPILMAMIŞ (atlanmış/
      zaman-aşımına uğramış) kayıtlar artık `ocr_teyit_gerek` sayacına GİRMEZ — o sayaç
      yalnız GERÇEKTEN OCR/zayıf-çıkarım yapılmış (teyit gerektiren) kayıtları yansıtır;
      idari/işlenmemiş kayıtlar 'bilinmeyen' kovasına sayılır. (Bu, 00-kunye.json'daki
      `ocr_teyit_gerek`/`bilinmeyen` BYTE-çıktısını etkiler — bkz. tests/test_oa_ingest*.py.)

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
  python oa_ingest.py "<klasor>" --isci 8                 # 8 paralel işçi (0=oto, 1=seri)
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, glob, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time, zipfile
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor, as_completed

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
# v1.5.1 (a): bu yöntemlerle biten kayıtlar önbelleğe YAZILMAZ — araç (Tesseract vb.)
# sonradan kurulunca "imza aynı → önbellekten bas" yolu bayat 'YÜKLENEMEDİ' damgasını
# tekrarlamasın. 'zaman-aşımı' kasıtlı olarak DIŞARIDA: OCR zaman-aşımı pahalıdır,
# önbellekte kalması (--yeniden ile açıkça atlanabilir) kabul edilebilir bir ödünleşimdir.
_ARIZA_ONBELLEKSIZ = {"hata", "atlandı"}

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


# ---------------- çıkarım (İÇERİK-AGNOSTİK, saf; işçide de ebeveynde de aynı) ----------------
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


# ---------------- v1.5: paralel çıkarım altyapısı (SAF İŞÇİ — durum değiştirmez) ----------------
# NOT: Bu fonksiyonlar üst-düzeydir ve picklable'dır (Windows spawn zorunluluğu).
# Yalnız METİN çıkarırlar; md/künye/önbellek yazımı EBEVEYNE aittir (tek-yazar doktrini).

def _isci_init():
    """Havuz işçisi başlatıcı: Tesseract'ın kendi çok-iş-parçacığını KIS (N işçi ×
    çok-thread aşırı-abonelik olmasın). OCR metni thread sayısından bağımsızdır → çıktı DEĞİŞMEZ."""
    os.environ["OMP_THREAD_LIMIT"] = "1"


def _cikar_tekil(yol, uz, opts):
    """SAF çıkarım (tek dosya). İçerik-agnostik: herhangi bir evrak/kelime aynı yolu izler."""
    # TEST KANCASI (yalnız pytest, v1.5.1 d): OA_INGEST_TEST_KILL ortam değişkeni bir
    # dosya taban-adına eşitse işçi süreci GERÇEKTEN öldürülür (os._exit) — bu, poison-
    # evrak izole yeniden denemesini (tests/test_oa_ingest_paralel.py) gerçek bir
    # BrokenProcessPool ile test etmeyi sağlar. Normal koşuda bu değişken HİÇ ayarlı
    # DEĞİLDİR → üretim davranışı hiçbir şekilde etkilenmez.
    _oa_kill = os.environ.get("OA_INGEST_TEST_KILL")
    if _oa_kill and os.path.basename(yol) == _oa_kill:
        os._exit(137)
    t0 = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="oaing_w_") as t:   # with: çökmede %TEMP% sızmaz
        metin, y, teyit, sf, hata = evrak_isle(yol, uz, opts, t)
    return {"metin": metin, "yontem": y, "teyit": teyit, "sayfa": sf, "hata": hata,
            "sure_ms": (time.perf_counter() - t0) * 1000.0}


def _cikar_arsiv(yol, opts):
    """SAF çıkarım (EYP/ZIP) — arşivin TAMAMI tek iş birimi; içini ARŞİV-GÖRELİ YOLA göre
    SIRALI açar, her evrağı çıkarır. a/b/c ek-harflemesi EBEVEYNDE atanır (burada yalnız sıralı metin).
    KİMLİK = arşiv-göreli yol (yalnız taban ad DEĞİL): EYP içinde farklı alt klasörde aynı adlı
    iki evrak (UYAP paketlerinde gerçekçi) hem DETERMİNİSTİK sıra alır hem `kaynak`'ı BENZERSİZ
    kalır ('her md kaynağına bağlıdır' vaadi + geri-izleme korunur)."""
    try:
        with tempfile.TemporaryDirectory(prefix="oaing_a_") as t:
            zipfile.ZipFile(yol).extractall(t)
            icler = []
            for dp, _, fs in os.walk(t):
                for f in fs:
                    ie = os.path.splitext(f)[1].lower()
                    if ie in IC_BILINEN:
                        tam = os.path.join(dp, f)
                        gor = os.path.relpath(tam, t).replace(os.sep, "/")   # arşiv-göreli, benzersiz
                        icler.append((tam, ie, gor))
            icler.sort(key=lambda x: (x[2].lower(), x[2]))   # göreli yol; ikincil anahtar = kararlılık
            if not icler:
                return {"bos": True, "icler": [], "hata": None}
            cikti = []
            for ic, ie, icad in icler:
                t0 = time.perf_counter()
                metin, y, teyit, sf, hata = evrak_isle(ic, ie, opts, t)
                cikti.append({"icad": icad, "ie": ie, "metin": metin, "yontem": y,
                              "teyit": teyit, "sayfa": sf, "hata": hata,
                              "sure_ms": (time.perf_counter() - t0) * 1000.0})
            return {"bos": False, "icler": cikti, "hata": None}
    except Exception as e:
        return {"bos": False, "icler": None, "hata": f"EYP/ZIP açılamadı: {e}"}


def _cikar_is(item, opts):
    """Havuz/seri ORTAK giriş noktası: bir iş kalemini SAF çıkarır (picklable, üst-düzey)."""
    if item["sinif"] == "arsiv":
        return _cikar_arsiv(item["yol"], opts)
    return _cikar_tekil(item["yol"], item["uz"], opts)


# ---------------- yazım (yalnız EBEVEYN; tek-yazar) ----------------
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


def _atomik_yaz(yol, veri):
    """tmp'ye yaz + os.replace: yarım/kesik dosya İMKANSIZ (çökmede eski tam sürüm kalır).
    os.replace aynı dizinde atomiktir; sonraki oa- adımları asla truncate künye görmez."""
    d = os.path.dirname(os.path.abspath(yol)) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-oaing-", suffix=".part")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(veri)
        os.replace(tmp, yol)
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


# ---------------- yardımcılar: FAZ A tarama, FAZ C birleştirme ----------------
def _tara(klasor, hedef_abs, onbellek, yeniden):
    """FAZ A — diski DETERMİNİSTİK (göreli-yol) sırada tara; sıralı iş kalemleri döndür.
    Her kaleme sınıf (tekil/arsiv/bilinmeyen), imza ve önbellek-isabeti damgalanır."""
    ham = []
    for kok, dizinler, adlar in os.walk(klasor):
        dizinler[:] = [d for d in dizinler
                       if d.lower() not in ATLA_DIZIN
                       and os.path.abspath(os.path.join(kok, d)) != hedef_abs]
        for ad in adlar:
            if ad.lower() in ATLA_DOSYA:
                continue
            ham.append((kok, ad))
    ham.sort(key=lambda x: os.path.relpath(os.path.join(x[0], x[1]), klasor).lower())

    items = []
    for i, (kok, ad) in enumerate(ham):
        yol = os.path.join(kok, ad)
        gorece = os.path.relpath(yol, klasor)
        uz = os.path.splitext(ad)[1].lower()
        no, temiz, tarih = evrak_no_ad(ad)
        it = {"index": i, "yol": yol, "gorece": gorece, "uz": uz, "no": no,
              "temiz": temiz, "tarih": tarih, "hit": False, "cached": None, "imza": None}
        if uz not in (PDF | UDF | ARSIV | DOCX | GORUNTU | DUZ):
            it["sinif"] = "bilinmeyen"
        else:
            it["sinif"] = "arsiv" if uz in ARSIV else "tekil"
            it["imza"] = f"{os.path.getmtime(yol):.0f}-{os.path.getsize(yol)}"
            onb = onbellek.get(gorece)
            if onb and not yeniden and onb.get("imza") == it["imza"]:
                if it["sinif"] == "arsiv" and isinstance(onb.get("kayitlar"), list):
                    it["hit"] = True; it["cached"] = onb
                elif it["sinif"] == "tekil" and "kayit" in onb:
                    it["hit"] = True; it["cached"] = onb
        items.append(it)
    return items


def _hata_kaydi(no, ad, tarih, kaynak, yontem, hata):
    return {"no": no, "ad": ad, "tarih": tarih, "kaynak": kaynak, "yontem": yontem,
            "teyit_gerek": True, "karakter": 0, "sha": BOS_SHA, "sayfa": None,
            "hata": hata, "md": ""}


def main():
    ap = argparse.ArgumentParser(description="oa-ingest — deterministik metin çıkarım motoru v1.5.1 (PyMuPDF, paralel)")
    ap.add_argument("klasor", nargs="?", default=".",
                    help="dava klasörü (verilmezse BULUNDUĞUN klasör işlenir)")
    ap.add_argument("--hedef")
    ap.add_argument("--ocr", choices=["auto", "zorla", "kapali"], default="auto")
    ap.add_argument("--dil", default="tur")
    ap.add_argument("--ocr-dpi", type=int, default=300, dest="dpi")
    ap.add_argument("--ocr-sayfa-limit", type=int, default=0, dest="sayfa_limit")
    ap.add_argument("--yeniden", action="store_true")
    ap.add_argument("--isci", type=int, default=0,
                    help="paralel işçi sayısı (0=otomatik=min(çekirdek,8); 1=seri/tek-süreç)")
    a = ap.parse_args()

    if not os.path.isdir(a.klasor):
        sys.exit(f"HATA: klasör yok: {a.klasor}")
    # Seri yolda da OCR thread'ini kıs → OCR koşulları seri==paralel özdeş (determinizm sigortası).
    os.environ.setdefault("OMP_THREAD_LIMIT", "1")
    t_bas = time.perf_counter()
    print(f"İşlenen klasör: {os.path.abspath(a.klasor)}")
    if not FITZ:
        print("UYARI: PyMuPDF yok → PDF'ler işlenemez. Kur:  pip install pymupdf", file=sys.stderr)
    if a.ocr != "kapali" and not TESSERACT:
        print("BİLGİ: Tesseract PATH'te yok → taranmış evraklar OCR'lanamayacak "
              "(metin PDF/UDF/DOCX yine işlenir). Kur: UB-Mannheim (Win) / apt tesseract-ocr-tur (Linux).",
              file=sys.stderr)

    hedef = a.hedef or os.path.join(a.klasor, "_oa", "metin")
    os.makedirs(hedef, exist_ok=True)
    # v1.5.1 (b): önceki çökmüş bir koşudan kalan atomik-yazım artıklarını süpür.
    # _atomik_yaz zaten çökmede eski TAM sürümü korur (yarım künye İMKANSIZ); bu yalnız
    # os.replace'e hiç ulaşamamış .part çöp dosyalarını temizler — sessizce YIĞILMASINLAR.
    for _art in glob.glob(os.path.join(hedef, ".tmp-oaing-*.part")):
        try:
            os.remove(_art)
        except OSError:
            pass
    opts = {"ocr": a.ocr, "dil": a.dil, "dpi": a.dpi, "sayfa_limit": a.sayfa_limit}

    onbellek_yol = os.path.join(hedef, ".ingest-onbellek.json")
    onbellek = {}
    if os.path.exists(onbellek_yol) and not a.yeniden:
        try:
            onbellek = json.load(open(onbellek_yol, encoding="utf-8"))
        except Exception:
            onbellek = {}

    # ---- FAZ A: tarama → sıralı iş listesi (deterministik: göreli-yol) ----
    items = _tara(a.klasor, os.path.abspath(hedef), onbellek, a.yeniden)

    # ---- FAZ B: SAF ÇIKARIM (seri veya havuz) — yalnız cache-MISS tekil/arşiv ----
    is_kalemleri = [it for it in items if it["sinif"] in ("tekil", "arsiv") and not it["hit"]]
    isci = a.isci if a.isci > 0 else max(1, min((os.cpu_count() or 1), 8))
    sonuclar = {}   # index -> payload (None = işçi çöktü)
    profil = {}     # yontem -> toplam_ms

    def _profille(p):
        if p is None:
            return
        if p.get("icler"):
            for ic in p["icler"]:
                profil[ic["yontem"]] = profil.get(ic["yontem"], 0.0) + ic.get("sure_ms", 0.0)
        elif "sure_ms" in p:
            profil[p["yontem"]] = profil.get(p["yontem"], 0.0) + p["sure_ms"]

    t_cik = time.perf_counter()
    if is_kalemleri and isci <= 1:
        for it in is_kalemleri:
            p = _cikar_is(it, opts)
            sonuclar[it["index"]] = p
            _profille(p)
    elif is_kalemleri:
        toplam = len(is_kalemleri); tamam = 0
        with ProcessPoolExecutor(max_workers=isci, initializer=_isci_init) as ex:
            gel = {ex.submit(_cikar_is, it, opts): it for it in is_kalemleri}
            for fut in as_completed(gel):
                it = gel[fut]
                try:
                    p = fut.result()
                except Exception as e:   # BrokenProcessPool / işçi çöktü → FAZ C damgalar (sessiz atlama YOK)
                    p = None
                    print(f"  ⚠ işçi çöktü: {it['gorece']} ({e})", file=sys.stderr)
                sonuclar[it["index"]] = p
                _profille(p)
                tamam += 1
                if tamam % 25 == 0 or tamam == toplam:
                    print(f"  … çıkarım {tamam}/{toplam}", file=sys.stderr)
    cik_sn = time.perf_counter() - t_cik

    # ---- v1.5.1 (d): POISON-EVRAK İZOLE YENİDEN DENEME (FAZ C'den ÖNCE) ----
    # Havuzda çöken (BrokenProcessPool → sonuclar[idx] = None) kalemler tek-işçi
    # (max_workers=1) İZOLE bir havuzda BİRER BİRER yeniden denenir. Amaç: bir "zehirli"
    # evrak (ör. bozuk font tablolu PDF) tüm havuzu düşürüp AYNI BATCH'teki masum
    # evrakları da 'işçi çöktü' damgasıyla sürüklemesin. İzole halde de çöken evrak
    # nihai 'işçi çöktü' damgasını FAZ C'de alır (canlı-kilit önlenir: tekrar tekrar
    # tüm havuzu düşürmeye çalışmaz — her zehirli evrak yalnız KENDİ izole denemesini yakar).
    coken = [it for it in is_kalemleri if sonuclar.get(it["index"]) is None]
    if coken:
        print(f"  … {len(coken)} kalem havuzda çöktü, izole (tek-işçi) yeniden deneniyor",
              file=sys.stderr)
        for it in coken:
            try:
                with ProcessPoolExecutor(max_workers=1, initializer=_isci_init) as ex:
                    p = ex.submit(_cikar_is, it, opts).result()
            except Exception as e:
                p = None
                print(f"  ⚠ izole yeniden denemede de çöktü: {it['gorece']} ({e})", file=sys.stderr)
            else:
                if p is not None:
                    print(f"  ✓ izole yeniden deneme kurtardı: {it['gorece']}", file=sys.stderr)
            sonuclar[it["index"]] = p
            _profille(p)

    # ---- FAZ C: BİRLEŞTİRME (tek-yazar ebeveyn, SIRALI-İNDEKS) — md/künye/önbellek ----
    # NOT: yeni/atlanan yalnız stdout özeti içindir. ocr_sayisi/bilinmeyen künyeye GİRER;
    # onlar döngüde artırılmaz, FİNAL künyeden TÜRETİLİR (aşağıda) — yol-bağımsız olsun ki
    # soğuk==sıcak (idempotens) ve seri==paralel byte-eşitliği bir özet sayacında kırılmasın.
    kunye, yeni, atlanan = [], 0, 0
    kullanilan = set()
    # ÖNBELLEKLİ md ADLARI DÖNGÜ BAŞINDA REZERVE (v1.4 düzeltmesi — bkz. docstring).
    if not a.yeniden:
        for onb in onbellek.values():
            for k in ([onb["kayit"]] if onb.get("kayit") else (onb.get("kayitlar") or [])):
                if k and k.get("md"):
                    kullanilan.add(k["md"])

    temsil = set()   # MEKANİK KAPI (GERÇEK invaryant): HER kaynak ≥1 kayıtla temsil edilmeli
    for it in items:      # items zaten SIRALI → md adlandırma seri koşuyla BİREBİR aynı
        gorece, no, temiz, tarih = it["gorece"], it["no"], it["temiz"], it["tarih"]

        if it["sinif"] == "bilinmeyen":
            kunye.append(_hata_kaydi(no, temiz, tarih, gorece, "bilinmeyen",
                                     f"desteklenmeyen uzantı ({it['uz']}) — elle kontrol"))
            temsil.add(it["index"])
            continue

        if it["hit"]:      # önbellekten — yeniden açma/OCR YOK
            onb = it["cached"]
            if it["sinif"] == "arsiv":
                for k in onb["kayitlar"]:      # BOŞ kayitlar (bozuk önbellek) → temsil EDİLMEZ → kapı yakalar
                    kunye.append(k)
                    if k.get("md"):
                        kullanilan.add(k["md"])
                    atlanan += 1; temsil.add(it["index"])
            else:
                k = onb["kayit"]; kunye.append(k); atlanan += 1
                if k.get("md"):
                    kullanilan.add(k["md"])
                temsil.add(it["index"])
            continue

        p = sonuclar.get(it["index"])
        if p is None:      # işçi çöktü → HATA damgası (sessiz atlama YASAK), önbelleğe YAZMA
            kunye.append(_hata_kaydi(no, temiz, tarih, gorece, "hata",
                                     "çıkarım işçisi çöktü — elle kontrol"))
            temsil.add(it["index"])
            continue

        if it["sinif"] == "tekil":
            k = kaydet_evrak(p["metin"], p["yontem"], p["teyit"], p["sayfa"], p["hata"],
                             gorece, no, temiz, tarih, hedef, kullanilan)
            kunye.append(k); yeni += 1; temsil.add(it["index"])
            # v1.5.1 (a): arıza {hata, atlandı} önbelleğe YAZILMAZ — sonraki koşuda
            # yeniden denensin (araç sonradan kurulunca bayat 'YÜKLENEMEDİ' tuzağı olmasın).
            if p["yontem"] not in _ARIZA_ONBELLEKSIZ:
                onbellek[gorece] = {"imza": it["imza"], "kayit": k}
            continue

        # ---- arşiv (miss) ----
        if p.get("icler") is None:     # açılamadı → önbelleğe YAZMA (sonraki koşuda tekrar denensin)
            kunye.append(_hata_kaydi(no, temiz, tarih, gorece, "hata",
                                     p.get("hata") or "EYP/ZIP açılamadı"))
            temsil.add(it["index"])
            continue
        arsiv_kayitlari = []
        if p.get("bos"):
            rec = _hata_kaydi(no, temiz, tarih, gorece, "arşiv-boş",
                              "EYP/ZIP içinde desteklenen evrak yok — elle kontrol")
            kunye.append(rec); arsiv_kayitlari.append(rec); temsil.add(it["index"])
        icler = p.get("icler") or []
        for j, ic in enumerate(icler):
            son = "" if len(icler) == 1 else (chr(97 + j) if j < 26 else str(j))
            ic_no = f"{no or '000'}{son}"
            k = kaydet_evrak(ic["metin"], ic["yontem"], ic["teyit"], ic["sayfa"], ic["hata"],
                             f"{gorece}::{ic['icad']}", ic_no,
                             f"{temiz} (EYP içi: {ic['icad']})", tarih, hedef, kullanilan)
            kunye.append(k); arsiv_kayitlari.append(k); yeni += 1; temsil.add(it["index"])
        # v1.5.1 (a): arşiv içinde arıza {hata, atlandı} taşıyan EN AZ BİR iç kayıt varsa
        # bu arşiv de önbelleğe YAZILMAZ (imza aynı kalır → araç sonradan kurulunca
        # bütün arşiv sessizce bayat kalır; önbellek olmadan bir sonraki koşuda yeniden açılır).
        if not any(k.get("yontem") in _ARIZA_ONBELLEKSIZ for k in arsiv_kayitlari):
            onbellek[gorece] = {"imza": it["imza"], "kayitlar": arsiv_kayitlari}

    # ---- v1.5.1 (c): ÖNBELLEK BUDAMA — diskte artık OLMAYAN (silinmiş) kaynakların
    # önbellek kaydını at (önbellek tek-yönlü BÜYÜMESİN + yetim md-adı rezervasyonu kalmasın).
    # DİKKAT: FAZ A (`_tara`) HER koşuda TÜM klasörü tarar (kısmi/delta DEĞİL) → bu koşuda
    # diskte var olan HER kaynak `items` içindedir; onbellekte olup `items`'ta OLMAYAN
    # anahtar YALNIZ silinmiş bir kaynak olabilir — hâlâ diskte duran ama bu koşuda sırası
    # gelmemiş bir kaynak asla bu kümenin dışında kalmaz, YANLIŞLIKLA BUDANMAZ.
    _mevcut_gorece = {it["gorece"] for it in items}
    for _stale in [g for g in onbellek if g not in _mevcut_gorece]:
        del onbellek[_stale]

    # ---- ÖZET SAYAÇLARI: final künyeden TÜRET (yol-bağımsız → idempotent + seri==paralel) ----
    # ocr_sayisi = gerçek OCR/zayıf çıkarım (teyit gerekli, idari-olmayan); idari kayıtlar
    # (bilinmeyen uzantı / arşiv-boş / açılamayan / OCR hiç YAPILMAMIŞ) 'bilinmeyen/elle'
    # kovasında toplanır. v1.5.1 (e): 'atlandı' (OCR kapalı/araç yok → hiç denenmedi) ve
    # 'zaman-asimi' (OCR başladı ama bitmedi) da BURAYA eklendi — bunlar GERÇEK OCR/zayıf-
    # çıkarım DEĞİL, ocr_teyit_gerek sayacını (asıl 'yapıldı ama teyit gerekir' kovası) şişirip
    # yanlış izlenim vermesin.
    _ADMIN = {"bilinmeyen", "arşiv-boş", "hata", "atlandı", "zaman-asimi"}
    ocr_sayisi = sum(1 for k in kunye if k.get("teyit_gerek") and k.get("yontem") not in _ADMIN)
    bilinmeyen = sum(1 for k in kunye if k.get("yontem") in _ADMIN)

    # ---- MEKANİK KAPI (sessiz-atlama yasağı): HER kaynak ≥1 kayıtla temsil edilmeli ----
    # GERÇEK invaryant — 'append başına say' totolojisi DEĞİL: bozuk önbellekte "kayitlar":[]
    # olan bir arşiv-hit SIFIR kayıt üretir; o kalem temsil'e girmez → burada YAKALANIR.
    eksik = [it for it in items if it["index"] not in temsil]
    if eksik:
        ilk = ", ".join(e["gorece"] for e in eksik[:3])
        sys.exit(f"HATA (mekanik kapı): {len(eksik)} kaynak HİÇ kayıt üretmedi (ilk: {ilk}) — "
                 f"sessiz kayıp; künye YAZILMADI. Önbelleği atlamak için '--yeniden' ile tekrar koş.")

    kunye.sort(key=lambda k: (k.get("no") or "999", k.get("kaynak", "")))
    toplam = sum(k.get("karakter") or 0 for k in kunye)
    tahmini_token = toplam // KAR_PER_TOKEN

    # ---- FAZ D: ATOMİK YAZIM (tmp+os.replace → yarım künye İMKANSIZ); künye EN SON = commit ----
    idx = [f"# Evrak Metin İndeksi — {os.path.basename(os.path.abspath(a.klasor))}\n\n",
           f"Toplam evrak: **{len(kunye)}** · OCR/teyit gerek: **{ocr_sayisi}** · "
           f"bilinmeyen/elle: **{bilinmeyen}** · "
           f"toplam metin: ~{toplam:,} karakter (~{tahmini_token:,} token)\n\n",
           "| # | Evrak | Tarih | Yöntem | ⚠ | Karakter | Dosya |\n",
           "|---|-------|-------|--------|---|----------|-------|\n"]
    for k in kunye:
        idx.append(f"| {k.get('no') or '—'} | {k.get('ad','')} | {k.get('tarih') or ''} "
                   f"| {k.get('yontem','')} | {'⚠' if k.get('teyit_gerek') else ''} "
                   f"| {k.get('karakter') or 0} | `{k.get('md','')}` |\n")
    idx.append("\n> ⚠ = OCR/zayıf çıkarım; künye ve sayısal veriyi orijinalden teyit et. "
               "Orijinal evrak salt-okunur arşivde durur.\n")

    _atomik_yaz(os.path.join(hedef, "00-INDEX.md"), "".join(idx))
    # Önbellek sort_keys → tamamlanma/ekleme sırasından BAĞIMSIZ, byte-deterministik.
    _atomik_yaz(onbellek_yol, json.dumps(onbellek, ensure_ascii=False, sort_keys=True))
    kunye_str = json.dumps({"klasor": os.path.abspath(a.klasor), "toplam_evrak": len(kunye),
                            "ocr_teyit_gerek": ocr_sayisi, "bilinmeyen": bilinmeyen,
                            "toplam_karakter": toplam, "tahmini_token": tahmini_token,
                            "kayitlar": kunye}, ensure_ascii=False, indent=2)
    _atomik_yaz(os.path.join(hedef, "00-kunye.json"), kunye_str)   # EN SON = commit işareti

    # ---- özet + profil (künye'ye YAZILMAZ → seri==paralel byte-eşitliği korunur) ----
    top_sn = time.perf_counter() - t_bas
    print(f"BİTTİ · evrak: {len(kunye)} (yeni: {yeni}, önbellekten: {atlanan}, bilinmeyen: {bilinmeyen}) · "
          f"OCR/teyit: {ocr_sayisi} · ~{toplam:,} karakter (~{tahmini_token:,} token)")
    print(f"Süre: {top_sn:.1f} sn (çıkarım {cik_sn:.1f} sn · işçi={isci}) · Çıktı: {hedef}")
    if profil:
        sirali = sorted(profil.items(), key=lambda x: -x[1])
        print("Çıkarım profili (yöntem→sn): " + " · ".join(f"{y}={ms/1000:.1f}" for y, ms in sirali[:6]))


if __name__ == "__main__":
    main()

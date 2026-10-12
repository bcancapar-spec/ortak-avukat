#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
ocr_kiyas.py — OCR MOTOR KIYASI (OCR planı §6 ve §10; kanıt aracı)

NEDEN VAR: "Paddle daha iyi okur" ya da "bu makinede hızlıdır" bir BEYAN değil, ölçümdür.
Araç motorları OA'nın KENDİ çağrı yolundan ölçer — Tesseract için `oa_ingest.ocr_png_ayrintili`,
PaddleOCR için `oa_ingest._paddle_cagir` (ayrı yorumlayıcıdaki `paddle_isci.py`). Yani sahada
koşan yol ölçülür; Paddle'da sayfa süresi işçinin model yüklemesini de içerir, çünkü OA her
sayfada işçiyi yeniden başlatır (gerçek maliyet budur; yükleme ayrıca `--kontrol` ile ölçülür).

NE ÖLÇER: beş SENTETİK sayfa (temiz, bulanık, gürültülü, eğik, düşük DPI; Türkçe karakterli altı
satır — eski bilgisayardaki 2026-10-06 deneyiyle aynı üretim). Sayfa başına duvar saati süresi,
karakter doğruluğu (difflib; boş satırlar ve satır başı/sonu boşlukları ölçülmez) ve Türkçe
harf korunumu (İ/ı, ş, ğ… — karakter doğruluğunun gizlediği "ASLİYE → ASLIYE" hatası).
Gerçek dava verisi KULLANILMAZ; sayfalar geçici dizinde üretilir.

PADDLE ÖN KOŞULU (OA ile aynı ortam değişkenleri): `OA_PADDLE_PY` (Paddle kurulu ayrı yorumlayıcı)
ve `OA_PADDLE_MODEL_DIZIN`. Modeller AĞSIZ kullanılır; bu araç hiçbir şey İNDİRMEZ. Dizindeki
model dosyaları `--model-dogrula <dizin>` ile aşağıdaki sabit manifeste karşı doğrulanır (boyut +
SHA-256 ya da git-blob özeti; kaynak: Hugging Face PaddlePaddle depolarında sabit commit).

Kullanım:
  python tools/ocr_kiyas.py                         # tesseract + (ayarlıysa) paddle
  python tools/ocr_kiyas.py --motor tesseract --tekrar 3
  python tools/ocr_kiyas.py --json sonuc.json
  python tools/ocr_kiyas.py --model-dogrula <OA_PADDLE_MODEL_DIZIN>
Ölçüm ortamı (Python, işletim sistemi, çekirdek sayısı, yazı tipi) çıktıda ASLA gizlenmez.
"""
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, difflib, hashlib, importlib.util, json, os, platform, statistics, tempfile, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OA_INGEST = os.path.join(REPO, "plugins", "ortak-avukat", "skills", "oa-ingest", "scripts", "oa_ingest.py")

BEKLENEN = [
    "T.C. ANKARA 3. ASLİYE HUKUK MAHKEMESİ",
    "ESAS NO: 2024/1234   KARAR NO: 2025/567",
    "Tebliğ tarihi: 12.03.2025 — Şişli, İğdır, Çığ, Öğün, Ünlü",
    "Davacı vekilinin itirazının reddine karar verilmiştir.",
    "IBAN: TR33 0006 1005 1978 6457 8413 26",
    "Hüküm, taraflara tefhim edilmiş olup kesinleşmemiştir.",
]
SAYFA_TURLERI = ("temiz", "bulanik", "gurultulu", "egik", "dusuk_dpi")
TR_HARFLER = "çğışöüÇĞİŞÖÜ"
_YAZI_TIPLERI = (r"C:\Windows\Fonts\arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/Library/Fonts/Arial.ttf")

# Sabit model manifesti (2026-10-06 eski bilgisayar deneyinde 6/6 doğrulandı): dosya → (bayt, tür, özet)
PADDLE_MODELLER = {
    "PP-OCRv6_medium_det": {
        "commit": "8e0f56fb2ef86b461d99cfc7ac5c137738985f61",
        "dosyalar": {
            "inference.json": (312150, "git-blob", "548f60c00e9303a0323feceeae460256576671a6"),
            "inference.pdiparams": (61960476, "sha256",
                                    "85218d2e3d98f5a21c58b4220627be923a97aee5db3cc71f39536ab31ac53960"),
            "inference.yml": (886, "git-blob", "1c5c05809877e4c7385f899019fff0ac9017ca80"),
        }},
    "PP-OCRv6_medium_rec": {
        "commit": "e5a92bcbc5cc1b494628e458d267778f0704fd7c",
        "dosyalar": {
            "inference.json": (221814, "git-blob", "9e0192344de3b69dacdb19dd735efbd06bd852f9"),
            "inference.pdiparams": (76465087, "sha256",
                                    "1b01c79a914587933f615569e75de54f2e638ebb5d3f3b3c1b38c24ede8c7319"),
            "inference.yml": (150580, "git-blob", "c53a96fcd315a86cb4748d2746f3d90941e1c6d8"),
        }},
}


def beklenen_metin():
    return "\n".join(BEKLENEN)


def normal(metin):
    """Satır başı/sonu boşlukları ve boş satırlar ölçülmez (Tesseract paragraf arası boş satır basar)."""
    return "\n".join(s.strip() for s in (metin or "").splitlines() if s.strip())


def dogruluk(okunan):
    return round(difflib.SequenceMatcher(None, beklenen_metin(), normal(okunan)).ratio(), 3)


def tr_harf(okunan):
    """Beklenen metindeki Türkçe harflerin okunan metinde korunma oranı (harf başına sayım)."""
    b, o = beklenen_metin(), okunan or ""
    toplam = sum(b.count(h) for h in TR_HARFLER)
    return round(sum(min(o.count(h), b.count(h)) for h in TR_HARFLER) / toplam, 3) if toplam else 1.0


def _yazi_tipi():
    from PIL import ImageFont
    for yol in [os.environ.get("OA_KIYAS_FONT") or ""] + list(_YAZI_TIPLERI):
        if yol and os.path.isfile(yol):
            return ImageFont.truetype(yol, 34), yol
    try:
        return ImageFont.load_default(size=34), "Pillow varsayılanı (sonuçlar KIYASLANAMAZ)"
    except TypeError:
        return ImageFont.load_default(), "Pillow varsayılanı (sonuçlar KIYASLANAMAZ)"


def sayfalar(dizin):
    """Beş sentetik sayfa → {tür: png yolu}. Üretim deterministiktir (sabit tohum)."""
    import random
    from PIL import Image, ImageDraw, ImageFilter
    font, _ = _yazi_tipi()
    temel = Image.new("L", (1240, 700), 255)
    c = ImageDraw.Draw(temel)
    for i, s in enumerate(BEKLENEN):
        c.text((60, 60 + i * 95), s, fill=0, font=font)
    rnd = random.Random(7)
    gurultulu = temel.copy()
    px = gurultulu.load()
    for _ in range(40000):
        px[rnd.randrange(1240), rnd.randrange(700)] = rnd.choice((0, 255))
    uret = {"temiz": temel, "bulanik": temel.filter(ImageFilter.GaussianBlur(1.6)), "gurultulu": gurultulu,
            "egik": temel.rotate(2.5, expand=True, fillcolor=255),
            "dusuk_dpi": temel.resize((620, 350)).resize((1240, 700))}
    yollar = {}
    for ad in SAYFA_TURLERI:
        yollar[ad] = os.path.join(dizin, ad + ".png")
        uret[ad].save(yollar[ad])
    return yollar


def _oa_ingest():
    spec = importlib.util.spec_from_file_location("_ocr_kiyas_oa_ingest", OA_INGEST)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def oa_motorlari():
    """OA'nın kendi çağrı yolları: {ad: png → (metin|None, hata|None)}."""
    ing = _oa_ingest()

    def tesseract(png):
        metin, hata, _guven = ing.ocr_png_ayrintili(png, "tur")
        return metin, hata

    def paddle(png):
        d, hata = ing._paddle_cagir(png)
        return (d or {}).get("metin"), hata

    def paddle_yukleme():
        t0 = time.perf_counter()
        _d, hata = ing._paddle_cagir("", kontrol=True)
        return (None if hata else round(time.perf_counter() - t0, 2)), hata

    return {"tesseract": tesseract, "paddle": paddle, "_paddle_yukleme": paddle_yukleme}


def kiyasla(dizin, motorlar, tekrar=1):
    """Her motoru her sayfada `tekrar` kez koşar (süre: medyan). İlk hatada o motor durur ve
    hata GÖRÜNÜR yazılır — motor yoksa sessizce atlanmaz."""
    yollar = sayfalar(dizin)
    sonuc = {"sayfa_turleri": list(SAYFA_TURLERI), "tekrar": tekrar, "motorlar": {}}
    for ad, oku in motorlar.items():
        if ad.startswith("_"):
            continue
        kayit = {"sayfalar": [], "hata": None}
        for sayfa in SAYFA_TURLERI:
            sureler, metin = [], None
            for _ in range(max(1, tekrar)):
                t0 = time.perf_counter()
                metin, hata = oku(yollar[sayfa])
                sureler.append(time.perf_counter() - t0)
                if hata:
                    break
            if hata:
                kayit["hata"] = "%s sayfasında: %s" % (sayfa, hata)
                break
            kayit["sayfalar"].append({"sayfa": sayfa, "sn": round(statistics.median(sureler), 2),
                                      "dogruluk": dogruluk(metin), "tr_harf": tr_harf(metin),
                                      "ornek": normal(metin)[:120]})
        sonuc["motorlar"][ad] = kayit
    return sonuc


def _git_blob(veri):
    return hashlib.sha1(b"blob %d\0" % len(veri) + veri).hexdigest()


def model_dogrula(dizin):
    """Model dosyalarını sabit manifeste karşı doğrular → (tamam: bool, satırlar)."""
    satirlar, tamam = [], True
    for model, m in PADDLE_MODELLER.items():
        for ad, (bayt, tur, ozet) in m["dosyalar"].items():
            yol = os.path.join(dizin, model, ad)
            if not os.path.isfile(yol):
                satirlar.append("YOK    %s/%s" % (model, ad))
                tamam = False
                continue
            with open(yol, "rb") as f:
                veri = f.read()
            gercek = hashlib.sha256(veri).hexdigest() if tur == "sha256" else _git_blob(veri)
            dogru = len(veri) == bayt and gercek == ozet
            tamam = tamam and dogru
            satirlar.append("%s %s/%s (%d bayt, %s)" % ("TAMAM " if dogru else "FARKLI", model, ad, len(veri), tur))
    return tamam, satirlar


def _ortam(yazi_tipi):
    return {"python": platform.python_version(), "isletim": platform.platform(), "cekirdek": os.cpu_count(),
            "islemci": platform.processor(), "yazi_tipi": yazi_tipi}


def main(argv=None):
    ap = argparse.ArgumentParser(description="OCR motor kıyası (sentetik sayfalar, OA çağrı yolu)")
    ap.add_argument("--motor", choices=("tesseract", "paddle", "hepsi"), default="hepsi")
    ap.add_argument("--tekrar", type=int, default=1)
    ap.add_argument("--json", dest="json_yol")
    ap.add_argument("--model-dogrula", dest="model_dizin")
    a = ap.parse_args(argv)
    if a.model_dizin:
        tamam, satirlar = model_dogrula(a.model_dizin)
        print("\n".join(satirlar))
        print("MODEL DOĞRULAMA: " + ("TAMAM (6/6)" if tamam else "BAŞARISIZ"))
        return 0 if tamam else 1
    motorlar = oa_motorlari()
    secili = {k: v for k, v in motorlar.items() if a.motor == "hepsi" or k in (a.motor,)}
    with tempfile.TemporaryDirectory(prefix="ocr_kiyas_") as d:
        sonuc = kiyasla(d, secili, a.tekrar)
    sonuc["ortam"] = _ortam(_yazi_tipi()[1])
    if "paddle" in sonuc["motorlar"] and not sonuc["motorlar"]["paddle"]["hata"]:
        sonuc["motorlar"]["paddle"]["yukleme_sn"] = motorlar["_paddle_yukleme"]()[0]
    for ad, k in sonuc["motorlar"].items():
        if k["hata"]:
            print("%-10s HATA: %s" % (ad, k["hata"]))
            continue
        print("%-10s medyan %.2f sn/sayfa%s" % (ad, statistics.median(x["sn"] for x in k["sayfalar"]),
                                              ("  (işçi yükleme %.1f sn)" % k["yukleme_sn"]) if k.get("yukleme_sn") else ""))
        for x in k["sayfalar"]:
            print("  %-10s %6.2f sn  doğruluk %.3f  Türkçe harf %.3f" % (x["sayfa"], x["sn"], x["dogruluk"], x["tr_harf"]))
    print("ortam: %(python)s · %(isletim)s · %(cekirdek)s çekirdek · yazı tipi: %(yazi_tipi)s" % sonuc["ortam"])
    if a.json_yol:
        with open(a.json_yol, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    _sys.exit(main())

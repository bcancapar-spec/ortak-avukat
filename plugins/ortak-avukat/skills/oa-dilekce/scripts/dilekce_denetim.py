#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
dilekce_denetim.py — oa-dilekce/oa-kontrol TESLİM ÖNCESİ ŞABLON + ZAAF KAPISI

Deterministik denetim: taslak dilekçede (a) tip başına ZORUNLU UNSURLAR var mı,
(b) "avukata yakışan tertip-düzen" — hem biçim (başlık/numaralı vakıa) hem de sekiz
zorunlu unsurun (mahkeme başlığı, taraflar/vekil, konu, açıklamalar, hukuki sebepler,
deliller, sonuç-istem, tarih-imza) mekanik VARLIK denetimi, tip'ten BAĞIMSIZ olarak
her dilekçede — kuruldu mu, (c) OCR ⚠ kaynaklı alıntı teyit şerhi taşıyor mu,
(d) MÜVEKKİL-ALEYHİ ifade sinyali, TARAF-BİLİNÇLİ (anayasal TEK KATI SINIR — davalıda
kabul/ikrar/doğrudur, davacıda vazgeçme/haksızlık, müşteki/katılanda şikayetten
vazgeçme/uzlaşma, sanıkta suç ikrarı) var mı. Script hukuki karar VERMEZ;
eksik/riski işaretler, nihai göz avukatındır — ama eksik/sinyal varsa exit 1 ile
teslim öncesi durdurur.

Tip/unsur listeleri numerus clausus DEĞİL — düşünce metodunu gösteren ÖRNEKLEMDİR;
bilinmeyen tip 'genel dilekçe unsurları' ile denetlenir (anayasa: örnekleme ilkesi).

Kullanım:
  python dilekce_denetim.py <taslak.md> --tip dava|cevap|istinaf|temyiz|aym_bireysel|genel
                            [--taraf davaci|davali|sanik|katilan|mudahil|musteki]
Çıkış kodu: 0 = temiz; 1 = eksik unsur / müvekkil-aleyhi sinyal / OCR-teyit şerhi eksik.
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import importlib.util
import pathlib
import re
import sys

# Tip → [(unsur adı, [anahtar desen/kelime])] — herhangi biri geçerse unsur VAR sayılır.
GENEL = [
    ("Mahkeme/merci başlığı", [r"mahkeme", r"başkanlığı", r"hakimliği", r"\bmerci"]),
    ("Taraf + kimlik (TC/adres)", [r"davac[ıi]", r"daval[ıi]", r"başvurucu", r"\bT\.?C\.?\b", r"kimlik\s*no", r"adres"]),
    ("Konu", [r"\bkonu\b"]),
    ("Açıklamalar / vakıalar", [r"açıklama", r"vak[ıi]a", r"olay"]),
    ("Hukuki sebepler", [r"hukuki\s*sebep", r"hukuki\s*neden", r"dayanak"]),
    ("Deliller", [r"delil", r"ispat", r"tanık", r"bilirkişi"]),
    ("Netice-i talep", [r"netice-?i?\s*talep", r"sonuç\s*ve\s*istem", r"talep\s*(ederiz|ederim|olunur)"]),
    ("Tarih", [r"\d{1,2}[./]\d{1,2}[./]\d{4}", r"tarih"]),
    ("İmza / vekil", [r"imza", r"\bvekil", r"av\.\s", r"avukat"]),
]
TIPLER = {
    "dava": GENEL,
    "cevap": GENEL + [("Cevap/ilk itiraz (varsa)", [r"cevap", r"ilk\s*itiraz", r"karşı\s*dava", r"itiraz"])],
    "istinaf": [
        ("Başvurulan BAM + ilk derece karar", [r"bölge\s*adliye", r"\bBAM\b", r"ilk\s*derece", r"esas\s*no", r"karar\s*no"]),
        ("Taraflar", [r"davac[ıi]", r"daval[ıi]", r"istinaf\s*eden"]),
        ("İstinaf sebepleri", [r"istinaf\s*sebep", r"istinaf\s*neden", r"kaldır", r"hukuka\s*aykırı"]),
        ("Talep (kaldırma/yeniden)", [r"netice-?i?\s*talep", r"kaldırıl", r"talep\s*(ederiz|ederim)"]),
        ("Tebliğ tarihi + süre satırı", [r"tebliğ", r"süre", r"iki\s*hafta", r"\b2\s*hafta"]),
        ("Tarih + imza", [r"\d{1,2}[./]\d{1,2}[./]\d{4}", r"imza", r"\bvekil"]),
    ],
    "temyiz": [
        ("Yargıtay ilgili dairesi", [r"yargıtay", r"\bdaire", r"hukuk\s*dairesi", r"ceza\s*dairesi"]),
        ("BAM kararı bilgisi", [r"bölge\s*adliye", r"\bBAM\b", r"esas\s*no", r"karar\s*no"]),
        ("Temyiz sebepleri", [r"temyiz\s*sebep", r"temyiz\s*neden", r"bozma", r"hukuka\s*aykırı"]),
        ("Talep", [r"netice-?i?\s*talep", r"boz", r"talep\s*(ederiz|ederim)"]),
        ("Süre satırı", [r"tebliğ", r"süre", r"iki\s*hafta"]),
        ("Tarih + imza", [r"\d{1,2}[./]\d{1,2}[./]\d{4}", r"imza"]),
    ],
    "aym_bireysel": [
        ("Başvurucu bilgileri", [r"başvurucu", r"\bT\.?C\.?\b", r"kimlik"]),
        ("İhlal edilen hak + Anayasa maddesi", [r"ihlal", r"anayasa[’']?n[ıi]n?\s*\d+", r"\bAY\s*m\.?\s*\d+", r"hak\b"]),
        ("Başvuru yollarının tüketilmesi", [r"yol.*tüket", r"tüketil", r"kesinleş"]),
        ("Süre (30 gün)", [r"süre", r"otuz\s*gün", r"\b30\s*gün", r"tebliğ", r"öğrenme"]),
        ("Talep", [r"talep", r"ihlalin\s*tespit", r"yeniden\s*yargılama"]),
    ],
    "genel": GENEL,
}

# Tertip-düzen: hem BİÇİM (başlık/numaralandırma) hem de "avukata yakışan" dilekçenin
# ZORUNLU UNSURLARININ VARLIĞI — tip ne olursa olsun (dava/cevap/istinaf/temyiz/aym_bireysel/
# genel) her dilekçede bulunması beklenen sekiz kalem: mahkeme başlığı, taraflar/vekil, konu,
# açıklamalar, hukuki sebepler, deliller, sonuç-istem, tarih-imza. Bu katman [A]'daki tip-özel
# listeden BAĞIMSIZ ve TÜM tiplere UYGULANIR — istinaf/temyiz/aym_bireysel gibi tip-özel
# listeler "Konu"/"Deliller"/"Hukuki sebepler" gibi jenerik kalemleri her zaman içermeyebilir;
# bu katman onu tamamlar. Script yalnız "unsur var/yok" der — "dilekçe iyi/kötü/kabule
# elverişli" hükmü VERMEZ (sahte kesinlik yok); eksik olanı UYAR, nihai göz avukatındır.
DUZEN = [
    ("Belirgin başlık bloğu", [r"^#", r"mahkeme", r"başkanlığı"]),
    ("Numaralı/bölümlü açıklama düzeni", [r"^\s*\d+[.)]", r"^\s*[-*]\s", r"##"]),
    ("Mahkeme/merci başlığı", [r"mahkeme", r"başkanlığı", r"hakimliği", r"\bmerci", r"dairesi", r"kurulu"]),
    ("Taraflar / vekil bilgisi", [r"davac[ıi]", r"daval[ıi]", r"başvurucu", r"müşteki", r"sanık",
                                   r"katılan", r"müdahil", r"\bvekil", r"av\.\s"]),
    ("Konu", [r"\bkonu\b"]),
    ("Açıklamalar / vakıalar", [r"açıklama", r"vak[ıi]a", r"olay"]),
    ("Hukuki sebepler", [r"hukuki\s*sebep", r"hukuki\s*neden", r"dayanak", r"hukuka\s*aykır"]),
    ("Deliller", [r"delil", r"ispat", r"tanık", r"bilirkişi"]),
    ("Sonuç ve istem (netice-i talep)", [r"netice-?i?\s*talep", r"sonuç\s*ve\s*istem", r"talep\s*(ederiz|ederim|olunur)"]),
    ("Tarih + imza bloğu", [r"\d{1,2}[./]\d{1,2}[./]\d{4}", r"imza", r"\bvekil", r"saygı"]),
]

# Müvekkil-aleyhi tehlike desenleri (TARAF-BİLİNÇLİ) — HEURİSTİK; avukat teyit etmeli.
# Her taraf tipi kendi riskli kalıp setiyle taranır: davalı için kabul/ikrar/doğrudur ekseni,
# davacı için vazgeçme/haksızlık ekseni, müşteki/katılan için şikayetten vazgeçme/uzlaşma
# ekseni, sanık için suç ikrarı ekseni. "genel" seti her taraf için ek olarak taranır.
_ALEYHE_DAVALI = [
    r"davay[ıi]\s*kabul", r"kabul\s*ed(iyoruz|iyorum|eriz)", r"haklı\s*olduğunu\s*kabul",
    r"borcu(muzu)?\s*kabul", r"\bikrar\s*ed", r"talebi(ni)?\s*kabul", r"davanın\s*kabul",
    r"\bdoğrudur\b", r"iddia\s*doğrudur", r"kusurlu(yuz|yum)", r"sorumlu\s*olduğu(muzu|mu)",
]
_ALEYHE_DAVACI = [
    r"iddiam[ıi]zdan\s*vazgeç", r"haksız\s*olduğumuz", r"talebimizi\s*geri",
    r"talebimizden\s*vazgeç", r"davadan\s*feragat", r"iddiam[ıi]zdan\s*feragat",
    r"haklı\s*değiliz", r"davamız\s*yersiz",
]
_ALEYHE_MUSTEKI = [
    r"şikayet(im|imiz)i\s*geri", r"şikayetten\s*vazgeç", r"affediyor",
    r"barıştık", r"şikayetçi\s*değil", r"davacı\s*olmak\s*istemiyor",
]
_ALEYHE_SANIK = [
    r"suçu\s*kabul", r"işlediğim(i)?\s*kabul", r"\bikrar\s*ed", r"pişman.*kabul",
    r"suçlu\s*olduğumu",
]
ALEYHE = {
    "davali": _ALEYHE_DAVALI,
    "davaci": _ALEYHE_DAVACI,
    "musteki": _ALEYHE_MUSTEKI,
    # katılan usulen müştekinin kamu davası açıldıktan sonraki devamıdır — aynı riskli eksen.
    "katilan": _ALEYHE_MUSTEKI,
    "sanik": _ALEYHE_SANIK,
    "genel": [r"karşı\s*taraf(ın)?\s*haklı", r"aleyhimize\s*kabul"],
}


def _bul(metin, desenler):
    return any(re.search(d, metin, re.I | re.M) for d in desenler)


def _udf_yaz_yukle():
    """udf_yaz.py'yi (kardeş script) dosya-yolundan yükler — paket değildir."""
    yol = pathlib.Path(__file__).resolve().parent / "udf_yaz.py"
    if not yol.is_file():
        return None
    spec = importlib.util.spec_from_file_location("udf_yaz", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def udf_kapisi(udf_yolu):
    """Üretilen UDF'in GEÇERLİ olup olmadığını udf_yaz.udf_dogrula ile denetler.

    Bu, denetim hattının UDF-VARSAYILAN doktrinine bağlı mekanik kapısıdır:
    dilekçe UDF olarak teslim edilecekse, önce bu kapı GEÇERLİ dönmelidir.
    Sahte kesinlik yok — yalnız 'geçerli/geçersiz' + somut hata listesi döner,
    'iyi dilekçe' hükmü vermez.
    """
    mod = _udf_yaz_yukle()
    if mod is None:
        return {"gecerli": False, "hatalar": ["udf_yaz.py yüklenemedi (kardeş script bulunamadı)"]}
    return mod.udf_dogrula(udf_yolu)


def denetle(metin, tip, taraf):
    eksik, uyari = [], []
    unsurlar = TIPLER.get(tip, TIPLER["genel"])

    # A) zorunlu unsurlar
    for ad, des in unsurlar:
        if not _bul(metin, des):
            eksik.append(ad)

    # B) tertip-düzen
    duzen_eksik = [ad for ad, des in DUZEN if not _bul(metin, des)]

    # C) OCR ⚠ alıntı → teyit şerhi
    ocr_var = ("⚠" in metin) or re.search(r"\bOCR\b", metin, re.I)
    ocr_serh = re.search(r"orijinal.*teyit|teyit\s*(edil|gerek)|RG.*teyit", metin, re.I)
    ocr_uyari = bool(ocr_var and not ocr_serh)

    # D) müvekkil-aleyhi ifade (tek katı sınır) — OLUMSUZLAMA KORUMALI
    # Standart cevap kalıbı "davanın kabulü anlamına gelmemek kaydıyla" / "kabul etmediğimiz"
    # sahte alarm üretmesin: ±70 karakter penceresinde olumsuzlama varsa sinyal düşürülür.
    NEG = re.compile(r"anlamına\s*gelme|kaydıyla|etmedi[ğg]|etmiyor|etmemek|etmez|\bkabul\s*etme"
                     r"|redd|aksi|\bdeğil|olmaks[ıi]z[ıi]n|olmamak", re.I)
    aleyhe, aleyhe_notu = [], []
    for anahtar in ([taraf] if taraf in ALEYHE else []) + ["genel"]:
        for d in ALEYHE.get(anahtar, []):
            for m in re.finditer(d, metin, re.I):
                pencere = metin[max(0, m.start() - 70): m.end() + 70]
                if NEG.search(pencere):
                    aleyhe_notu.append(m.group(0))   # olumsuzlanmış → bilgi, engel değil
                else:
                    aleyhe.append(m.group(0))

    return eksik, duzen_eksik, ocr_uyari, aleyhe, aleyhe_notu


def main():
    ap = argparse.ArgumentParser(description="dilekce_denetim.py — teslim öncesi şablon + zaaf kapısı")
    ap.add_argument("taslak")
    ap.add_argument("--tip", default="genel",
                    choices=["dava", "cevap", "istinaf", "temyiz", "aym_bireysel", "genel"])
    ap.add_argument("--taraf", default="",
                    choices=["", "davaci", "davali", "sanik", "katilan", "mudahil", "musteki"])
    ap.add_argument("--udf", metavar="YOL", default="",
                    help="(opsiyonel) Üretilmiş .udf dosyasını da GEÇERLİLİK KAPISI ile "
                         "denetler — UDF-VARSAYILAN doktrini burada mekanik olarak kapanır.")
    a = ap.parse_args()

    try:
        metin = open(a.taslak, encoding="utf-8", errors="replace").read()
    except Exception as e:
        print(f"HATA: taslak okunamadı ({e})", file=sys.stderr)
        sys.exit(1)

    eksik, duzen_eksik, ocr_uyari, aleyhe, aleyhe_notu = denetle(metin, a.tip, a.taraf)
    cizgi = "=" * 62
    print(cizgi)
    print(f"DİLEKÇE DENETİMİ — tip: {a.tip} · taraf: {a.taraf or '—'}")
    print(cizgi)

    print("\n[A] ZORUNLU UNSURLAR")
    if eksik:
        for u in eksik:
            print(f"   [EKSİK] {u}")
    else:
        print("   [OK] tip için beklenen unsurlar mevcut görünüyor")

    print("\n[B] TERTİP-DÜZEN (avukata yakışan biçim)")
    if duzen_eksik:
        for u in duzen_eksik:
            print(f"   [UYARI] {u} — zayıf/görünmüyor")
    else:
        print("   [OK] başlık/bölüm/netice/imza düzeni kurulu")

    print("\n[C] OCR/⚠ ALINTI TEYİDİ")
    if ocr_uyari:
        print("   [UYARI] OCR/⚠ işareti var ama 'orijinalden teyit' şerhi görünmüyor — "
              "künye/sayısal veriyi orijinalden doğrula.")
    else:
        print("   [OK] OCR-teyit şerhi sorunu görünmüyor")

    print("\n[D] MÜVEKKİL-ALEYHİ İFADE TARAMASI (anayasal — tek katı sınır)")
    if aleyhe:
        for s in sorted(set(aleyhe)):
            print(f"   [UYARI] olası müvekkil-aleyhi ifade: \"{s}\" — avukat TEYİT ETMELİ; "
                  "dış çıktı müvekkil lehine kurgulanır (davalıda kabul/ikrar YOK).")
    else:
        print("   [OK] belirgin müvekkil-aleyhi ifade sinyali bulunamadı (heuristik)")
    if aleyhe_notu:
        print(f"   [BİLGİ] olumsuzlanmış kalıp(lar) sinyal sayılmadı (ör. 'kabul anlamına "
              f"gelmemek kaydıyla'): {', '.join(sorted(set(aleyhe_notu)))}")

    udf_gecersiz = False
    if a.udf:
        print("\n[E] UDF GEÇERLİLİK KAPISI (UDF-VARSAYILAN doktrini)")
        udf_sonuc = udf_kapisi(a.udf)
        if udf_sonuc["gecerli"]:
            print(f"   [OK] {a.udf} geçerli UDF (zip + content.xml + XML + offset/round-trip tutarlı)")
        else:
            udf_gecersiz = True
            print(f"   [EKSİK] {a.udf} GEÇERSİZ UDF:")
            for h in udf_sonuc["hatalar"]:
                print(f"      - {h}")

    print("\n" + cizgi)
    engel = bool(eksik or ocr_uyari or aleyhe or udf_gecersiz)
    if engel:
        print("SONUÇ: TESLİM ÖNCESİ AVUKAT GÖZÜ ŞART (eksik unsur / aleyhe sinyal / teyit şerhi).")
        print(cizgi)
        sys.exit(1)
    print("SONUÇ: temel şablon denetimi temiz (nihai sorumluluk avukatındır).")
    print(cizgi)
    sys.exit(0)


if __name__ == "__main__":
    main()

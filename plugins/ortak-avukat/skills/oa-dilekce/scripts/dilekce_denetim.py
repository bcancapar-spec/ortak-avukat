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

── [F] İÇTİHAT MUHAKEME ZİNCİRİ KAPISI (M2-3 — oa-kontrol'e BAĞLANDI; P1-7: VARSAYILAN AÇIK) ──
[F], kardeş skill oa-kontrol'ün `ictihat_muhakeme_denetim.py`'sini (çıplak/
ALEYHE/eksik-alanlı içtihat atfı mekanik kapısı — bkz. o scriptin docstring'i)
AYRI SÜREÇTE çalıştırır ve raporu + exit kodu bu denetime [F] bölümü olarak
ekler. Tek tanım oa-kontrol'de yaşar, burada TEKRARLANMAZ — teslim öncesi
MEKANİK KAPILAR zinciri BEŞ değil ALTI yeşil ışıktan oluşur (A-F).

P1-7 (v0.5.5): `--ictihat-muhakeme` artık VARSAYILAN AÇIKTIR (v0.5.4 kanıtı:
kapı opt-in olduğu için gerçek koşumda bayrak hiç verilmedi, [F] hiç koşmadı).
Kapatmak için `--ictihat-muhakeme-yok` kullanılır (teslim_paketi.py bunu
tekilleştirme amacıyla BİLİNÇLİ geçirir — bkz. aşağı). AKILLI FAIL-OPEN (yanlış-
blok supabı, DAR): (a) `--kok` altında `_oa/` yoksa VEYA (b) taslakta hiçbir
içtihat künye-deseni (esas/karar no) VE hiçbir "Yargıtay/Danıştay/AYM/AİHM/
yerleşik içtihat/emsal karar" ANLATIM deseni yoksa [F] `[BİLGİ] atlandı` der,
BLOKLAMAZ — içtihatsız dilekçeler ve `_oa`'sız eski akışlar kırılmaz. AMA künye
YOK iken anlatım deseni VARSA (künyesiz emsal anlatımı) [F] ATLANMAZ — kapı
normal çalışır (G1 zaten bunu "emsal içtihat yok" uyarısına çevirir, bloklamaz)
ve rapora GÖRÜNÜR ek bir satır düşer: "künyesiz içtihat anlatımı — muhakeme
zinciri denetlenemedi" (invaryant m.4: künyesiz parafrazın sessizce sızması
engellenir). `--ictihat-muhakeme-yok` KULLANILDIYSA bu da raporda AÇIKÇA
görünür (sessiz opt-out yok).

Kullanım:
  python dilekce_denetim.py <taslak.md>
                            --tip dava|cevap|istinaf|temyiz|aym_bireysel|yemin|idari-kanal|genel
                            [--taraf davaci|davali|sanik|katilan|mudahil|musteki]
                            [--udf YOL]
                            [--ictihat-muhakeme --kok KLASÖR]
Çıkış kodu: 0 = temiz; 1 = eksik unsur / müvekkil-aleyhi sinyal / OCR-teyit şerhi
eksik / GEÇERSİZ UDF / [F] içtihat muhakeme kapısı engeli.

── [B2] KANUN-YOLU YAPISAL KALEMLERİ (M3-2 — kanun-yolu-mimari-playbook.md B1/B2/B4/B6) ──
`--tip istinaf|temyiz` verildiğinde [B] TERTİP-DÜZEN kapısı, kanun yolu
dilekçesinin fiziksel mimarisine özgü YAPISAL kalemleri de mekanik olarak
denetler: künye blok alan seti (kanun yoluna konu kararın kimliği/sonucu +
dava konusu işlem/dayanak norm), TEBLİĞ TARİHİ'nin AYRI SATIRDA olması, GİRİŞ
bölümünün varlığı, SONUÇ/İSTEM'in numaralı olması ve her içtihat blok-
alıntısının (markdown '>' satırı) ardından bir açıklama paragrafı bulunması
(B4'ün "çıplak alıntı kabul edilmez" kuralının tertip-düzen izdüşümü). Bu da
[A]/[B] gibi YALNIZ var/yok der — "iyi dilekçe" hükmü VERMEZ; `denetle()`'nin
imzası/dönüş arity'si DEĞİŞMEZ (mevcut çağıranlar bozulmaz), yeni kalemler tip
koşuluyla mevcut `duzen_eksik` listesine eklenir.

── G1 "ESASLI DİLEKÇE" TİP LİSTESİ (M3-2/R6) ──
`--ictihat-muhakeme` ile birlikte `--tip` değeri de [F] kapısına
(`ictihat_muhakeme_denetim.py`) aktarılır: o scriptin G1 "emsal içtihat yok"
UYARISI yalnız "esaslı" dilekçe tiplerinde (dava/cevap/istinaf/temyiz/
aym_bireysel) basılır; `yemin`/`idari-kanal` gibi hafif tiplerde bu uyarı
[BİLGİ]'ye düşer (G1 zaten hiçbir zaman bloklamaz — bu yalnız gürültüyü
azaltır). Tek kaynak liste `ictihat_muhakeme_denetim.ESASLI_OLMAYAN_TIPLER`'dir
(burada TEKRARLANMAZ).

── [H] GÖRÜNMEZ İSKELET TARAMASI (P1-11 ek kural, advisory — ASLA bloklamaz) ──
İDDİA→NORM→İÇTİHAT→ÖRTÜŞME→SONUÇ zinciri paragrafın İÇ MANTIĞIDIR, yüzey
metnine ETİKET olarak sızmaz (saha dersi: model iskeleti görünür kalıba
çevirdi, akıcılık bozuldu). [H] satır başında 'İddiamız:', 'Norm:', 'Somut
örtüşme:' kalıplarını ararsa bir AKICILIK uyarısı basar — hukuki içerik
denetimi DEĞİLDİR, yalnız biçim sinyalidir; exit koduna ASLA dokunmaz.

── [I] KUSUR→SONUÇ→TALEP ASİMETRİSİ TARAMASI (P1-11 ek kural, advisory) ──
Karşı tarafın kusuru TESPİT edilir, SONUÇ yazılır, ama GİDERİLMESİNE yönelik
ara karar talebi KURULMAZ (rakibin dosyasını onarmaya yardım = müvekkil-
aleyhi talep inşası). [I] karşı-taraf-kusuru bağlamında 'süre verilsin/
tamamlan-/gideril-' kalıplarını ararsa bir uyarı basar — advisory, ASLA
bloklamaz.
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import glob
import importlib.util
import json
import os
import pathlib
import re
import subprocess
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

# ── [B2] KANUN-YOLU (istinaf/temyiz) YAPISAL KALEMLERİ — M3-2 ──────────────
# kanun-yolu-mimari-playbook.md B1 (künye disiplini) / B2 (GİRİŞ) / B4 (içtihat
# bloğu 5-adım) / B6 (bölüm mimarisi) 'nin dilekçe-içi mekanik izdüşümü. [B]
# TERTİP-DÜZEN kapısının tip-koşullu UZANTISIDIR — yalnız --tip istinaf|temyiz
# iken devreye girer; DUZEN listesinden BAĞIMSIZ yeni bir alan çifti EKLER,
# denetle()'nin dönüş imzasını DEĞİŞTİRMEZ. Sahte kesinlik yok: yalnız
# var/yok listesi döner, "iyi dilekçe" hükmü VERMEZ.
KANUN_YOLU_TIPLERI = {"istinaf", "temyiz"}

# B1 künye blok alan seti — DUZEN'de zaten denetlenen merci/taraflar/tarih
# kalemleriyle ÇAKIŞMAYAN, kanun yoluna özgü iki alan.
KANUN_YOLU_KUNYE_EK = [
    ("B1 Künye — kanun yoluna konu kararın kimliği/operatif sonucu",
     [r"ilk\s*derece.{0,40}karar", r"karar\s*ver(ilmiş|di)", r"hükm",
      r"reddine|kabulüne|karar\s*verilmiştir"]),
    ("B1 Künye — dava konusu işlem + dayanak norm",
     [r"dayanak", r"\bm\.\s*\d", r"madde\s*\d+", r"kanun(?:'?un|\s+m\.)"]),
]


def _satir_basi(metin, desen):
    """Bir satırın (markdown başlık/liste işaretleri temizlendikten sonra)
    BAŞI verilen desenle eşleşiyor mu — 'ayrı satır' zorunluluğunun mekanik
    karşılığı. Metnin ortasına/başka bir cümlenin içine gömülü geçiş bu
    denetim için YETERSİZ sayılır (B1: 'tebliğ tarihinin künye metnine
    gömülmesi' sık atlanan hatadır — süre denetimi bu satırı ayrıca arar)."""
    for satir in metin.splitlines():
        temiz = re.sub(r"^[\s#>*\-\d.)]+", "", satir).strip()
        if re.match(desen, temiz, re.I):
            return True
    return False


def _giris_bolumu_var_mi(metin):
    """B2 — 'GİRİŞ' başlıklı bir markdown bölümü var mı (yalnız VARLIK;
    içeriğin gerçekten 'çatı indirgeme' yapıp yapmadığı script'in işi
    DEĞİLDİR — bkz. playbook B2 ön koşulu)."""
    return bool(re.search(r"^\s*#{1,3}\s*[Gg][İIiı][Rr][İIiı][Şş]\b", metin, re.M))


def _sonuc_numarali_mi(metin):
    """B6 — netice-i talep/sonuç-istem bölümünden SONRAKİ metinde numaralı
    ('1. ...'/'1) ...') bir liste var mı. Rakam sayısı 1-2 hane + noktalama +
    ARDINDAN BOŞLUK ile sınırlanır ki '01.01.2026' gibi bir TARİH satırı
    (tarih-imza bloğu her dilekçenin sonunda bulunur) numaralı liste maddesi
    sanılıp YANLIŞ pozitif üretmesin."""
    m = re.search(r"netice-?i?\s*talep|sonuç\s*ve\s*istem", metin, re.I)
    if not m:
        return False
    return bool(re.search(r"^\s*\d{1,2}[.)]\s+\S", metin[m.end():], re.M))


def _alinti_aciklama_denetle(metin):
    """B4 — markdown blok-alıntı ('>' ile başlayan ardışık satır grupları)
    gruplarının HER BİRİ için, grup bittikten sonraki birkaç satır içinde
    boş-olmayan/alıntı-olmayan/BAŞLIK-OLMAYAN bir açıklama paragrafı var mı.
    (toplam_alinti, aciklamasiz_sayisi) döndürür — alıntı hiç yoksa (0, 0):
    bu denetim yalnız VAR OLAN alıntıların ardışıklığını denetler, alıntı
    yokluğunu YAKALAMAZ (o [F]/G1'in — oa-kontrol'ün — işidir). Bir sonraki
    markdown başlığı ('#...') açıklama SAYILMAZ — bölüm bittiği anlamına
    gelir, alıntı çıplak kalmış demektir (B4: 'çıplak alıntı kabul edilmez')."""
    satirlar = metin.splitlines()
    n = len(satirlar)
    toplam, eksik = 0, 0
    i = 0
    while i < n:
        if satirlar[i].lstrip().startswith(">"):
            toplam += 1
            j = i
            while j < n and satirlar[j].lstrip().startswith(">"):
                j += 1
            aciklama_var = False
            for k in range(j, min(j + 8, n)):
                s = satirlar[k].strip()
                if not s:
                    continue
                aciklama_var = not (s.startswith(">") or s.startswith("#"))
                break
            if not aciklama_var:
                eksik += 1
            i = j
        else:
            i += 1
    return toplam, eksik


def _kanun_yolu_yapisal_eksik(metin):
    """Kanun-yolu (istinaf/temyiz) tipleri için B1/B2/B4/B6 mekanik
    izdüşümünün eksik kalemlerini döndürür (yalnız VAR/YOK; hüküm YOK)."""
    eksik = [ad for ad, des in KANUN_YOLU_KUNYE_EK if not _bul(metin, des)]
    if not _satir_basi(metin, r"tebliğ\s*tarih"):
        eksik.append("B1 Künye — TEBLİĞ TARİHİ (ayrı satırda)")
    if not _giris_bolumu_var_mi(metin):
        eksik.append("B2 — GİRİŞ bölümü")
    if not _sonuc_numarali_mi(metin):
        eksik.append("B6 — Numaralı SONUÇ/İSTEM")
    toplam_alinti, eksik_aciklama = _alinti_aciklama_denetle(metin)
    if toplam_alinti and eksik_aciklama:
        eksik.append(
            f"B4 — İçtihat blok-alıntısı sonrası açıklama paragrafı "
            f"({eksik_aciklama}/{toplam_alinti} alıntıda eksik görünüyor)")
    return eksik


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


def _ictihat_muhakeme_yolu():
    """Kardeş skill oa-kontrol'ün `ictihat_muhakeme_denetim.py` yolunu döndürür
    (…/skills/oa-dilekce/scripts/ → …/skills/oa-kontrol/scripts/); yoksa None."""
    yol = (pathlib.Path(__file__).resolve().parent.parent.parent
           / "oa-kontrol" / "scripts" / "ictihat_muhakeme_denetim.py")
    return yol if yol.is_file() else None


_KUNYE_ORTAK_MOD = None


def _kunye_ortak_modulu():
    """kunye_ortak.py'yi (…/oa-kontrol/scripts/) İN-PROCESS import eder — P1-7
    akıllı fail-open ön-denetiminde 'taslakta içtihat künye-deseni var mı'
    sorgusu TEK KAYNAKTAN (`kunye_ortak.esas_karar_atiflari`) yanıtlanır,
    regex burada TEKRARLANMAZ. Kardeş skill kurulu değilse/import çökerse
    None döner — çağıran taraf bunu FAIL-SAFE sayıp [F]'i ATLAMAZ (belirsizlik
    içtihat kapısını sessizce kapatmanın gerekçesi olamaz)."""
    global _KUNYE_ORTAK_MOD
    if _KUNYE_ORTAK_MOD is not None:
        return _KUNYE_ORTAK_MOD
    yol = (pathlib.Path(__file__).resolve().parent.parent.parent
           / "oa-kontrol" / "scripts" / "kunye_ortak.py")
    if not yol.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            "_oa_dilekce_kunye_ortak_inproc", str(yol))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return None
    _KUNYE_ORTAK_MOD = mod
    return _KUNYE_ORTAK_MOD


# P1-7 DÜZELTME — "künye yok" fail-open'ının içtihat ANLATIMI ile delinmesini
# önleyen desen: Yargıtay/Danıştay/AYM/AİHM/içtihadı birleştirme/yerleşik
# içtihat/emsal karar sözcükleri esas/karar no'suz da geçebilir (invaryant
# m.4'ün korumak istediği tam da bu yüzey — künyesiz parafraz).
ICTIHAT_ANLATIM_DESENI = re.compile(
    r"Yarg[ıi]tay|Dan[ıi]ştay\b|\bAYM\b|Anayasa\s+Mahkemesi|\bA[İi]HM\b|"
    r"içtihad[ıi]\s*birleştirme|yerleşik\s+içtihat|emsal\s+karar", re.I)


def _f_kapisi_fail_open_durumu(metin, a):
    """P1-7 — AKILLI FAIL-OPEN ön-denetimi (DAR). Döner:
      None                    → [F] normal çalışır (varsayılan/çoğunluk hâli).
      'no_oa'                 → _oa/ bulunamadı, [F] `[BİLGİ]` ile atlanır.
      'no_signal'              → taslakta ne künye ne içtihat anlatımı var,
                                  [F] `[BİLGİ]` ile atlanır.
      'desen_var_kunye_yok'    → künye YOK ama içtihat ANLATIMI var — [F]
                                  ATLANMAZ (normal çalışır), rapora ek GÖRÜNÜR
                                  uyarı düşer (künyesiz parafraz sızmasın)."""
    taban = a.kok if a.kok else "."
    if not os.path.isdir(os.path.join(taban, "_oa")):
        return "no_oa"
    ko = _kunye_ortak_modulu()
    kunye_var = None
    if ko is not None:
        try:
            atiflar = ko.esas_karar_atiflari(metin)
            kunye_var = any((x.get("esas") or x.get("karar")) for x in atiflar)
        except Exception:
            kunye_var = None
    if kunye_var:
        return None
    if kunye_var is None:
        # kunye_ortak yüklenemedi — belirsizlik atlamayı GEREKÇELENDİRMEZ,
        # fail-safe: [F] normal çalışsın (sessiz kapatma yok).
        return None
    if ICTIHAT_ANLATIM_DESENI.search(metin):
        return "desen_var_kunye_yok"
    return "no_signal"


def ictihat_muhakeme_kapisi(taslak_yolu, kok=None, muhakeme_dizin=None, dokum_dizin=None,
                             tip=None):
    """[F] İçtihat Muhakeme Zinciri mekanik kapısını (oa-kontrol'ün
    `ictihat_muhakeme_denetim.py`'si) AYRI SÜREÇTE çalıştırır ve (exit_kodu,
    rapor_metni) döndürür. Tek tanım oa-kontrol'de yaşar — burada
    TEKRARLANMAZ (M2-3: dilekce_denetim'in teslim-öncesi mekanik kapılar
    zincirine bu adımı BAĞLAR, yeni yeşil ışık). `tip` verilirse (M3-2/R6)
    kardeş scripte `--tip` olarak aktarılır — G1 "esaslı dilekçe" tip
    listesinin tek kaynağı orada yaşar, burada TEKRARLANMAZ."""
    yol = _ictihat_muhakeme_yolu()
    if yol is None:
        return 1, ("[EKSİK] ictihat_muhakeme_denetim.py bulunamadı "
                    "(oa-kontrol/scripts/ — kardeş skill kurulu mu?)")
    args = [sys.executable, str(yol), taslak_yolu]
    if kok:
        args += ["--kok", kok]
    if muhakeme_dizin:
        args += ["--muhakeme-dizin", muhakeme_dizin]
    if dokum_dizin:
        args += ["--dokum-dizin", dokum_dizin]
    if tip:
        args += ["--tip", tip]
    cp = subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return cp.returncode, ((cp.stdout or "") + (cp.stderr or "")).rstrip()


_ANTITEZ_MATRIS_MOD = None


def _antitez_matris_modulu():
    """Kardeş skill oa-antitez'in `antitez_matris.py`sini (…/oa-antitez/scripts/)
    İN-PROCES import eder — [G] advisory kapısının `duyulmus_curutmeler()`
    çağrısı için TEK KAYNAK (mantık burada TEKRARLANMAZ). Kardeş skill kurulu
    değilse/import çökerse None döner — [G] SESSİZCE atlanır (advisory,
    bloklamaz; bkz. `_kunye_ortak_modulu` ile aynı fail-safe desen)."""
    global _ANTITEZ_MATRIS_MOD
    if _ANTITEZ_MATRIS_MOD is not None:
        return _ANTITEZ_MATRIS_MOD
    yol = (pathlib.Path(__file__).resolve().parent.parent.parent
           / "oa-antitez" / "scripts" / "antitez_matris.py")
    if not yol.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("antitez_matris", yol)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return None
    _ANTITEZ_MATRIS_MOD = mod
    return mod


_ANTITEZ_DURAK_KELIME = {
    "ve", "veya", "ile", "için", "gibi", "ama", "fakat", "ancak", "değil",
    "olan", "olarak", "üzere", "göre", "kadar", "daha", "her", "hiç", "ise",
    "yani", "dolayı", "çünkü", "birlikte", "sonra", "önce", "sırasında",
}


def _antitez_anahtar_kelimeler(metin):
    kelimeler = re.findall(r"[a-zçğıöşüA-ZÇĞİÖŞÜ]{5,}", (metin or "").lower())
    return [k for k in kelimeler if k not in _ANTITEZ_DURAK_KELIME]


def _antitez_matris_dosyalari(kok):
    """M3 düzeltmesi (Paket D sınav bulgusu) — `_oa/cikti/*antitez*.json`
    ADAYLARINI TEK YERDEN bulur; hem `antitez_cevap_capasi_uyarilari` hem de
    [G] kapısının CLI çıktısı AYNI listeyi kullanır — böylece 'matris hiç
    yok' ile 'matris var ve tam örtüşüyor' durumları AYRI etiketlenebilir
    (ikisi de eskiden aynı boş-liste dönüşüyle [OK] altında birleşiyordu).

    YENİ-2 (Paket D DÜZELTME) — `kok` verilmediğinde artık SERT `[]` DÖNMEZ;
    `_ictihat_muhakeme_atlama_sebebi`:375 ile SİMETRİK olarak CWD'ye
    (`"."`) düşer. Kanonik teslim hattı (`teslim_paketi.py`) CWD'yi zaten
    `kok`a eşitleyip çalıştırır (`_kos(..., cwd=kok)`) — dolayısıyla
    `--kok` argümanı unutulsa bile [G] kapısı gerçek matrisi görür."""
    taban = kok if kok else "."
    cikti_dizin = os.path.join(taban, "_oa", "cikti")
    if not os.path.isdir(cikti_dizin):
        return []
    return sorted(glob.glob(os.path.join(cikti_dizin, "*antitez*.json")))


def antitez_cevap_capasi_uyarilari(metin, kok):
    """M3 (Paket D, v0.5.5) — [G] ADVISORY: `_oa/cikti/*antitez*.json`
    matrisindeki DUYULMUŞ+çürütülmüş her cephe için dilekçede bir 'çapa'
    (anahtar-kelime örtüşmesi, ≥%25 VEYA hiç yoksa) var mı? Bu bir DOĞRULUK
    denetimi DEĞİLDİR — yalnız 'çürütme dış çıktıya hiç yansımamış olabilir'
    sinyalidir; matris/kok yoksa veya kardeş skill yüklenemezse SESSİZCE boş
    liste döner (bloklamaz, ASLA çökmez — advisory girdisidir)."""
    adaylar = _antitez_matris_dosyalari(kok)
    if not adaylar:
        return []
    mod = _antitez_matris_modulu()
    if mod is None:
        return []
    uyarilar = []
    metin_kelimeleri = set(_antitez_anahtar_kelimeler(metin))
    for yol in adaylar:
        try:
            with open(yol, encoding="utf-8") as f:
                m = json.load(f)
        except Exception:
            continue
        try:
            duyulmuslar = mod.duyulmus_curutmeler(m)
        except Exception:
            continue
        for kayit in duyulmuslar:
            curutme = kayit.get("curutme") or ""
            anahtarlar = _antitez_anahtar_kelimeler(curutme)
            if not anahtarlar:
                continue
            ortusen = sum(1 for k in anahtarlar if k in metin_kelimeleri)
            oran = ortusen / len(anahtarlar)
            if ortusen < 1 or oran < 0.25:
                uyarilar.append(
                    f"cephe '{kayit.get('cephe')}' DUYULMUŞ (karşı taraf fiilen ileri "
                    "sürmüş) ve çürütülmüş ama dilekçede buna karşılık gelen bir çapa "
                    f"bulunamadı ({os.path.relpath(yol, kok)}) — çürütme dış çıktıya "
                    "İŞLENMEMİŞ olabilir; avukat gözden geçirmeli."
                )
    return uyarilar


# ── [H] GÖRÜNMEZ İSKELET TARAMASI (P1-11 ek kural, advisory) ───────────────
# İDDİA→NORM→İÇTİHAT→ÖRTÜŞME→SONUÇ zinciri paragrafın İÇ MANTIĞIDIR; saha
# dersi modelin bu zinciri görünür ETİKETLERE çevirdiğini gösterdi (akıcılık
# bozuldu). Bu tarama yalnız BİÇİM sinyalidir — hukuki içerik denetimi
# DEĞİLDİR, exit koduna ASLA dokunmaz (advisory).
_ISKELET_KALIPLARI = [
    (r"İddia(?:m[ıi]z)?\s*:", "İddiamız:"),
    (r"Norm\s*:", "Norm:"),
    (r"Somut\s*örtüşme\s*:", "Somut örtüşme:"),
]


def _gorunmez_iskelet_uyarilari(metin):
    """Satır başında (markdown başlık/liste işaretleri temizlendikten sonra)
    'İddiamız:', 'Norm:', 'Somut örtüşme:' kalıp-etiketlerini arar. Bulunan
    HER FARKLI etiket için bir uyarı döner — paragraf başına tekrar tekrar
    aynı uyarıyı basıp gürültü üretmemek için etiket başına TEKİLLEŞTİRİLİR."""
    uyarilar = []
    bulunanlar = set()
    for satir in (metin or "").splitlines():
        temiz = re.sub(r"^[\s#>*\-\d.)]+", "", satir).strip()
        for desen, etiket in _ISKELET_KALIPLARI:
            if etiket in bulunanlar:
                continue
            if re.match(desen, temiz, re.I):
                bulunanlar.add(etiket)
                uyarilar.append(
                    f"paragraf başında görünür kalıp-etiket '{etiket}' tespit edildi — "
                    "İDDİA→NORM→İÇTİHAT→ÖRTÜŞME→SONUÇ zinciri paragrafın İÇ MANTIĞI olmalı, "
                    "yüzeye ETİKET olarak sızmamalı (geçiş cümleleriyle örülmeli); akıcılık "
                    "bozulmuş olabilir — biçim sinyalidir, hukuki içerik hükmü değildir."
                )
    return uyarilar


# ── [I] KUSUR→SONUÇ→TALEP ASİMETRİSİ TARAMASI (P1-11 ek kural, advisory) ───
# Karşı tarafın kusuru TESPİT edilir, SONUÇ yazılır, ama GİDERİLMESİNE yönelik
# ara karar talebi KURULMAZ — rakibin dosyasını onarmaya yardım etmek
# müvekkil-aleyhi talep inşasıdır. Bu tarama yalnız BİÇİM/BAĞLAM sinyalidir,
# hukuki içerik hükmü DEĞİLDİR, exit koduna ASLA dokunmaz (advisory).
_KUSUR_BAGLAM_RE = re.compile(
    r"karşı\s*taraf(ın)?|davalı(n[ıi]n)?|daval[ıi]\s*taraf|davac[ıi](n[ıi]n)?|"
    r"kusur(u|lu|lar[ıi])?|eksik(lik|liği)?|dava\s*şart[ıi]\s*eksik", re.I)
_TALEP_ONARMA_RE = re.compile(
    r"süre\s*veril(sin|mesi|melidir)|tamamlan(mas[ıi]|mas[ıi]n[ıi]|d[ıi]r[ıi]lmas[ıi])|"
    r"gideril(sin|mesi|melidir)", re.I)


def _kusur_sonuc_talep_asimetri_uyarilari(metin):
    """Karşı-taraf-kusuru bağlamında ('karşı taraf', 'davalının', 'kusur',
    'eksiklik', 'dava şartı eksik' vb.) bir 'süre verilsin/tamamlan-/
    gideril-' onarma-talebi kalıbı geçiyor mu — ÖNCESİNDEKİ ~150 karakterlik
    pencerede bağlam kelimesi arar (aleyhe-ifade taramasındaki pencere
    deseniyle aynı yöntem). Bulunursa müvekkil-aleyhi talep inşası riski
    uyarısı döner; tekrarları TEKİLLEŞTİRİR."""
    uyarilar = []
    gorulen = set()
    for m in _TALEP_ONARMA_RE.finditer(metin or ""):
        once = metin[max(0, m.start() - 150): m.start()]
        if _KUSUR_BAGLAM_RE.search(once):
            ifade = m.group(0)
            if ifade in gorulen:
                continue
            gorulen.add(ifade)
            uyarilar.append(
                f"karşı-taraf-kusuru bağlamında onarma-talebi kalıbı: \"{ifade}\" — "
                "kusur TESPİT edilir, SONUÇ yazılır, ama GİDERİLMESİNE yönelik ara "
                "karar talebi KURULMAZ (rakibin dosyasını onarmasına yardım = "
                "müvekkil-aleyhi talep inşası); avukat gözden geçirmeli."
            )
    return uyarilar


def denetle(metin, tip, taraf):
    eksik, uyari = [], []
    unsurlar = TIPLER.get(tip, TIPLER["genel"])

    # A) zorunlu unsurlar
    for ad, des in unsurlar:
        if not _bul(metin, des):
            eksik.append(ad)

    # B) tertip-düzen (+ [B2] kanun-yolu tip-koşullu yapısal kalemler — M3-2)
    duzen_eksik = [ad for ad, des in DUZEN if not _bul(metin, des)]
    if tip in KANUN_YOLU_TIPLERI:
        duzen_eksik += _kanun_yolu_yapisal_eksik(metin)

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
                # EK-FİX (risk#2): pencere eşleşen kalıbın KENDİ aralığını İÇERMEZ.
                # Bazı aleyhe kalıpları ('şikayetçi değil', 'haklı değiliz') 'değil'i
                # kalıbın GÖVDESİ olarak taşır; eski kod pencereyi m.start()-70..m.end()+70
                # (eşleşmenin kendisi dahil) alıyordu → NEG deseni ('değil') eşleşmenin
                # içinde HER ZAMAN bulunuyor, bu kalıplar asla BLOKLAMIYOR, hep [BİLGİ]'ye
                # düşüyordu. Artık pencere yalnız eşleşmenin ÖNCESİ ve SONRASIdır — gerçek
                # bir olumsuzlama (eşleşmenin dışında) hâlâ doğru şekilde sinyali düşürür.
                once = metin[max(0, m.start() - 70): m.start()]
                sonra = metin[m.end(): m.end() + 70]
                if NEG.search(once) or NEG.search(sonra):
                    aleyhe_notu.append(m.group(0))   # olumsuzlanmış → bilgi, engel değil
                else:
                    aleyhe.append(m.group(0))

    return eksik, duzen_eksik, ocr_uyari, aleyhe, aleyhe_notu


def main():
    ap = argparse.ArgumentParser(description="dilekce_denetim.py — teslim öncesi şablon + zaaf kapısı")
    ap.add_argument("taslak")
    ap.add_argument("--tip", default="genel",
                    choices=["dava", "cevap", "istinaf", "temyiz", "aym_bireysel",
                             "yemin", "idari-kanal", "genel"])
    ap.add_argument("--taraf", default="",
                    choices=["", "davaci", "davali", "sanik", "katilan", "mudahil", "musteki"])
    ap.add_argument("--udf", metavar="YOL", default="",
                    help="(opsiyonel) Üretilmiş .udf dosyasını da GEÇERLİLİK KAPISI ile "
                         "denetler — UDF-VARSAYILAN doktrini burada mekanik olarak kapanır.")
    ap.add_argument("--ictihat-muhakeme", action="store_true", default=True,
                    help="(P1-7: VARSAYILAN AÇIK) [F] İçtihat Muhakeme Zinciri mekanik "
                         "kapısını (oa-kontrol/ictihat_muhakeme_denetim.py) da bu tek çağrıda "
                         "çalıştırır — çıplak/ALEYHE/eksik-alanlı içtihat atfı teslim engelidir. "
                         "Bayrak zaten varsayılan True olduğundan verilmesi davranışı DEĞİŞTİRMEZ "
                         "(geriye uyum için tutulur); kapatmak için --ictihat-muhakeme-yok kullan.")
    ap.add_argument("--ictihat-muhakeme-yok", action="store_true",
                    dest="ictihat_muhakeme_yok",
                    help="(opsiyonel) P0-5 DÜZELTME(c) çift-[F] tekilleştirme: [F] kapısını "
                         "HER KOŞULDA (ileride --ictihat-muhakeme VARSAYILANI değişse dahi) "
                         "kapalı tutan AÇIK override — teslim_paketi.py bunu (a) çağrısına "
                         "BİLİNÇLİ geçirir çünkü İçtihat Muhakeme Zinciri'ni kendi (b2) "
                         "adımında AYRICA çalıştırır (tek yetkili yol (b2)); bu bayrak "
                         "--ictihat-muhakeme'den ÖNCELİKLİDİR.")
    ap.add_argument("--kok", default=None,
                    help="(opsiyonel) --ictihat-muhakeme ile birlikte; çalışma kökü "
                         "(kunye_teyit.py/ictihat_muhakeme_denetim.py --kok simetrisi) — "
                         "verilmezse --muhakeme-dizin/--ictihat-dokum-dizin CWD-göreli "
                         "_oa/cikti, _oa/teyit/dokum'a düşer")
    ap.add_argument("--muhakeme-dizin", default=None,
                    help="(opsiyonel) --ictihat-muhakeme ile birlikte; verilmezse "
                         "--kok/_oa/cikti (--kok yoksa CWD-göreli _oa/cikti)")
    ap.add_argument("--ictihat-dokum-dizin", default=None,
                    help="(opsiyonel) --ictihat-muhakeme ile birlikte; verilmezse "
                         "--kok/_oa/teyit/dokum (--kok yoksa CWD-göreli _oa/teyit/dokum)")
    a = ap.parse_args()
    if a.ictihat_muhakeme_yok:
        a.ictihat_muhakeme = False  # AÇIK override — --ictihat-muhakeme VARSAYILANından bağımsız

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

    ictihat_muhakeme_engel = False
    if a.ictihat_muhakeme_yok:
        print("\n[F] İÇTİHAT MUHAKEME ZİNCİRİ KAPISI — --ictihat-muhakeme-yok ile AÇIKÇA "
              "ATLANDI (sessiz opt-out DEĞİL; genelde teslim_paketi.py'nin (b2) kapısıyla "
              "tekilleştirme tercihidir).")
    elif a.ictihat_muhakeme:
        fail_open = _f_kapisi_fail_open_durumu(metin, a)
        if fail_open == "no_oa":
            print("\n[F] İÇTİHAT MUHAKEME ZİNCİRİ KAPISI — [BİLGİ] atlandı: _oa/ bulunamadı "
                  "(bu kök pipeline/teyit altyapısını henüz kullanmıyor) — bloklamaz.")
        elif fail_open == "no_signal":
            print("\n[F] İÇTİHAT MUHAKEME ZİNCİRİ KAPISI — [BİLGİ] atlandı: taslakta esas/karar "
                  "no'lu içtihat künyesi VE 'Yargıtay/emsal karar' benzeri anlatım hiç yok "
                  "— bloklamaz.")
        else:
            print("\n[F] İÇTİHAT MUHAKEME ZİNCİRİ KAPISI (ictihat_muhakeme_denetim.py — oa-kontrol)")
            if fail_open == "desen_var_kunye_yok":
                print("   [UYARI] künyesiz içtihat anlatımı — muhakeme zinciri denetlenemedi "
                      "('Yargıtay/Danıştay/AYM/AİHM/yerleşik içtihat/emsal karar' benzeri "
                      "anlatım var ama esas/karar no'lu bir künye yok; fail-open bunu "
                      "ATLAMAZ — G1 aşağıda ayrıca 'emsal içtihat yok' uyarısı basacaktır.)")
            muhakeme_dizin = a.muhakeme_dizin if a.muhakeme_dizin is not None else (
                os.path.join(a.kok, "_oa", "cikti") if a.kok else None)
            dokum_dizin = a.ictihat_dokum_dizin if a.ictihat_dokum_dizin is not None else (
                os.path.join(a.kok, "_oa", "teyit", "dokum") if a.kok else None)
            kod_f, cikti_f = ictihat_muhakeme_kapisi(a.taslak, a.kok, muhakeme_dizin, dokum_dizin,
                                                      tip=a.tip)
            for satir in cikti_f.splitlines():
                print(f"   {satir}")
            ictihat_muhakeme_engel = (kod_f != 0)

    print("\n[G] ANTİTEZ-CEVAP-ÇAPASI (advisory — M3, Paket D, ASLA bloklamaz)")
    g_uyarilar = antitez_cevap_capasi_uyarilari(metin, a.kok)
    if g_uyarilar:
        for u in g_uyarilar:
            print(f"   [UYARI] {u}")
    elif not _antitez_matris_dosyalari(a.kok):
        # M3 düzeltmesi (Paket D sınav bulgusu, KUCUK) — matrisin TAMAMEN
        # YOKLUĞU ile 'matris var ve tam örtüşüyor' hâli artık AYNI [OK]
        # etiketiyle raporlanmıyor: zorunlu pas girdisinin hiç koşulmamış
        # olabileceği ayrıca [BİLGİ] ile işaretlenir.
        # YENİ-2 (Paket D DÜZELTME) — `--kok` verilmemişse mekanik körlüğü
        # olgu beyanına ÇEVİRME: 'koşulmamış olabilir' yalnız kök BİLİNİYORKEN
        # (ve orada gerçekten yoksa) söylenir; kök belirsizse yalnız arama
        # yapılamadığı söylenir.
        if a.kok:
            print("   [BİLGİ] _oa/cikti/*antitez*.json bulunamadı — ANTİTEZ PASI "
                  "koşulmamış olabilir (M3: zorunlu pas girdisi)")
        else:
            print("   [BİLGİ] _oa/cikti/*antitez*.json ARANAMADI (kök belirsiz — "
                  "--kok verilmedi, CWD'ye göre arandı) — sonuç kanıt sayılmaz")
    else:
        print("   [OK] karşılıksız DUYULMUŞ antitez sinyali bulunamadı (matris tam örtüşüyor)")

    print("\n[H] GÖRÜNMEZ İSKELET TARAMASI (advisory — P1-11 ek kural, ASLA bloklamaz)")
    h_uyarilar = _gorunmez_iskelet_uyarilari(metin)
    if h_uyarilar:
        for u in h_uyarilar:
            print(f"   [UYARI] {u}")
    else:
        print("   [OK] görünür kalıp-etiket sinyali bulunamadı (heuristik)")

    print("\n[I] KUSUR→SONUÇ→TALEP ASİMETRİSİ TARAMASI (advisory — P1-11 ek kural, ASLA bloklamaz)")
    i_uyarilar = _kusur_sonuc_talep_asimetri_uyarilari(metin)
    if i_uyarilar:
        for u in i_uyarilar:
            print(f"   [UYARI] {u}")
    else:
        print("   [OK] karşı-taraf-kusuru bağlamında onarma-talebi sinyali bulunamadı (heuristik)")

    print("\n" + cizgi)
    engel = bool(eksik or ocr_uyari or aleyhe or udf_gecersiz or ictihat_muhakeme_engel)
    if engel:
        print("SONUÇ: TESLİM ÖNCESİ AVUKAT GÖZÜ ŞART (eksik unsur / aleyhe sinyal / teyit şerhi "
              "/ ictihat muhakeme kapısı).")
        print(cizgi)
        sys.exit(1)
    print("SONUÇ: temel şablon denetimi temiz (nihai sorumluluk avukatındır).")
    print(cizgi)
    sys.exit(0)


if __name__ == "__main__":
    main()

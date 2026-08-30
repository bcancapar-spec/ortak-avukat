#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
kunye_ortak.py — İçtihat KÜNYE (esas/karar) ÇIKARIM + NORMALİZASYON ortak yardımcı.

PAYLAŞIM AMACI (M2-2 → M2-3 — TAMAMLANDI): Bu modül `ictihat_muhakeme_denetim.py`
(oa-kontrol) VE `kunye_teyit.py` (oa-kontrol) tarafından ORTAK kullanılır —
esas/karar/daire normalizasyon mantığı artık TEK yerde yaşar; iki script
arasında sürüklenip ayrışmaz (iki-yazar riski kapalı, çünkü tek tanım tek
dosyada). `kunye_teyit.py` kendi ESAS_RE/KARAR_RE/_norm_no/_daire_key/
_daire_kumesi tanımlarını KALDIRDI, bu modülün `esas_karar_atiflari`/
`norm_no`/`daire_key`/`daire_kumesi` fonksiyonlarını çağırır (yalnız mevzuat
madde-çıkarımı, ki bu modülün kapsamı dışıdır, `kunye_teyit.py`'de yerel kaldı).

Fonksiyonlar bir künyeyi "TEMİZLEMEZ" — yalnız METİNDE ZATEN VAR OLAN esas/karar
sayılarını kanonik (YIL/SIRA) biçime getirir ve döndürür. Metinde yoksa None.

Dışa açılan API:
  norm_no(s)                    → "2021 / 1234" → "2021/1234"
  esas_karar_atiflari(metin)    → belge-geneli çıkarım (nearest-pairing);
                                   [{"esas":.., "karar":.., "daire_key":.., ...}, ...]
  kunye_normalize(kunye_metin)  → TEK bir künye pasajı için (esas, karar) çifti
                                   (ilk bulunan çift; belge-geneli eşleştirme
                                   GEREKMEZ çünkü künye zaten tek bir atıftır)
  daire_key(metin)              → metindeki İLK numaralı daireyi (no, aile) olarak
  sayi_var(segment, sayi)       → sayıyı komşu rakamdan izole ederek arar (149≠49)
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os
import re

_YN = r"\d{4}\s*/\s*\d{1,6}"

# ── B-2 DÜZELTMESİ (v0.5.14) — DESEN KÖRLÜĞÜ ───────────────────────────────
# Denetim kanıtı (2026-08-31, her satır ayrı koşturuldu): `E. 2020/1111,
# K. 2021/2222` BLOK ederken `E:2020/1111` · `E: 2020/1111` · küçük harf
# `esas … karar …` kapıyı AÇIK bırakıyordu (exit 0) — yani halüsinasyonun EN
# SIK aldığı biçimlerde koruma yoktu. Eski desende (a) `E`den sonra NOKTA
# ZORUNLUYDU, (b) `re.IGNORECASE` yoktu.
# Şimdi: nokta OPSİYONEL, `:` ayracı tanınır, uzun biçim (`esas`/`karar`/`no`)
# BÜYÜK-KÜÇÜK HARF DUYARSIZ. Tek harflik `E`/`K` etiketi BİLİNÇLİ olarak
# BÜYÜK HARF kalır: `(?i)` verilseydi düz metindeki bağımsız "e"/"k"
# kelimeleri sayı komşuluğunda gürültü üretirdi (yanlış-BLOK yasağı).
_KUYRUK = r"\s*\.?\s*(?:(?i:no)\s*\.?)?\s*[:.]?\s*"   # '.', ':', ' ', 'No:' …
_E_ONEK = r"(?:\bE" + _KUYRUK + r"|(?i:\besas\b)" + _KUYRUK + r")"
_K_ONEK = r"(?:\bK" + _KUYRUK + r"|(?i:\bkarar\b)" + _KUYRUK + r")"
_E_SONEK = r"(?:\bE\.|\bE\b|(?i:\besas\b))"           # '2020/1111 E.' | '… E,'
_K_SONEK = r"(?:\bK\.|\bK\b|(?i:\bkarar\b))"

ESAS_RE = re.compile(_E_ONEK + r"(" + _YN + r")|(" + _YN + r")\s*" + _E_SONEK)
KARAR_RE = re.compile(_K_ONEK + r"(" + _YN + r")|(" + _YN + r")\s*" + _K_SONEK)
ESAS_TAG_RE = re.compile(_E_ONEK + r"(" + _YN + r")")
KARAR_TAG_RE = re.compile(_K_ONEK + r"(" + _YN + r")")

# ── B-2 (v0.5.14) — AYM / AİHM KÜNYELERİ (yapısal körlük) ──────────────────
# AYM BİREYSEL BAŞVURUDA E./K. YOKTUR: künye `Başvuru Numarası: YYYY/N`
# biçimindedir (usul: 6216 s. Kanun m.45-49 — MCP `mevzuat_icinde_ara` ile
# teyit edildi; canlı AYM verisinde künyeler `BB 2015/53` biçiminde döner —
# MCP `aym_ictihat_ara` ile teyit edildi). `MERCI_RE` "AYM"/"AİHM"i merci
# olarak TANIYOR ama künyesini asla ayrıştıramıyordu; `oa-dilekce` ise
# `aym_bireysel` tipini destekliyor — kapı o tipte tamamen kördü.
AYM_BB_RE = re.compile(
    r"(?:\bB\s*\.?\s*(?i:no)\s*\.?\s*[:.]?\s*"
    r"|(?i:\bbaşvuru\s+(?:numarası|no))\s*\.?\s*[:.]?\s*)(" + _YN + r")")
# AİHM başvuru numarası ters biçimlidir (sıra/yıl — ör. 1234/05). Yalnız
# İngilizce `Application no.` kalıbı kullanılır; Türkçe "Başvuru No" AYM'ye
# aittir (yukarıda) — iki desen çakışmaz.
AIHM_BASVURU_RE = re.compile(
    r"(?i:\bapplication\s+no)\s*\.?\s*[:.]?\s*(\d{1,6}\s*/\s*\d{2,4})")

# Dilekçenin KENDİ künye bloğu (Denizli 346 karnesinin tek parser
# yanlış-pozitifi: scriptin kendi `DOSYA NO:` satırını karşı-atıf sanması).
# TEK KAYNAK burasıdır; `kunye_teyit.py` bu tanımı kullanır.
KENDI_DOSYA_SATIR_RE = re.compile(
    r"^\s*[>*\-•\s]*(?:DOSYA\s*(?:ESAS\s*)?NO|ESAS\s*NO|MERC[İIiı])\b", re.I)

MERCI_RE = re.compile(
    r"(?:Yargıtay|Danıştay|Anayasa\s+Mahkemesi|AYM|Sayıştay|Uyuşmazlık\s+Mahkemesi|"
    r"A[İI]HM|(?:[A-ZÇĞİÖŞÜ][a-zçğıöşü]+\s+)?(?:BAM|B[İI]M|Bölge\s+Adliye\s+Mahkemesi|"
    r"Bölge\s+İdare\s+Mahkemesi)|HGK|CGK|[İI]BK|[İI]DDK|VDDK|"
    r"\d{1,2}\.\s*(?:HD|CD|D\b|Daire|Hukuk\s+Dairesi|Ceza\s+Dairesi|"
    r"İdari\s+Dava\s+Dairesi|Vergi\s+Dava\s+Dairesi))"
)

DAIRE_RE = re.compile(
    r"(\d{1,2})\s*\.\s*"
    r"(HD|CD|Hukuk\s+Dairesi|Ceza\s+Dairesi|İdari\s+Dava\s+Dairesi|"
    r"Vergi\s+Dava\s+Dairesi|Daire|D)(?![A-Za-zÇĞİÖŞÜçğıöşü])"
)


def _daire_aile(tur):
    u = tur.upper()
    if u.startswith("HD") or "HUKUK" in u:
        return "HD"
    if u.startswith("CD") or "CEZA" in u:
        return "CD"
    if "VERG" in u:
        return "VDD"
    if "DAR" in u:
        return "İDD"
    if u.startswith("DAIRE") or u == "D":
        return "D"
    return u


def daire_key(metin):
    """Metindeki İLK numaralı daireyi (no, aile) olarak döndürür; yoksa None."""
    m = DAIRE_RE.search(metin)
    if not m:
        return None
    return (m.group(1), _daire_aile(m.group(2)))


def daire_kumesi(segment):
    """Segmentteki TÜM numaralı daireleri {(no, aile), ...} olarak toplar
    (merci katmanı — 'izde FARKLI daire var mı' denetimi için; M2-3'te
    kunye_teyit.py ile paylaşıldı)."""
    return {(no, _daire_aile(tur)) for (no, tur) in DAIRE_RE.findall(segment)}


def norm_no(s):
    """'2021 / 1234' → '2021/1234' ; iç boşlukları temizle."""
    return re.sub(r"\s*/\s*", "/", s.strip())


def _sikistir(s, n=140):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def _cakisir(span, spanlar):
    s, e = span
    return any(s < b and a < e for (a, b) in spanlar)


def _esas_karar_ham_cikar(metin):
    """Esas/karar (başlangıç, bitiş, no) listelerini İKİ GEÇİŞLİ çıkarır.
    Bkz. modül docstring'i — kunye_teyit.py'deki aynı-isimli fonksiyonla
    KASITLI OLARAK aynı iki-geçişli yutma-kurtarma mantığını izler."""
    esas_ham = [(m.start(), m.end(), norm_no(m.group(1) or m.group(2)),
                 m.group(1) is not None)
                for m in ESAS_RE.finditer(metin)]
    karar_ham = [(m.start(), m.end(), norm_no(m.group(1) or m.group(2)),
                  m.group(1) is not None)
                 for m in KARAR_RE.finditer(metin)]

    esas_span_tum = [(s, e) for (s, e, _no, _t) in esas_ham]
    karar_span_tum = [(s, e) for (s, e, _no, _t) in karar_ham]

    esaslar = [(s, e, no) for (s, e, no, tag_once) in esas_ham
               if tag_once or not _cakisir((s, e), karar_span_tum)]
    kararlar = [(s, e, no) for (s, e, no, tag_once) in karar_ham
                if tag_once or not _cakisir((s, e), esas_span_tum)]

    for m in ESAS_TAG_RE.finditer(metin):
        span = (m.start(), m.end())
        if _cakisir(span, [(s, e) for (s, e, _no) in esaslar]):
            continue
        esaslar.append((span[0], span[1], norm_no(m.group(1))))
    for m in KARAR_TAG_RE.finditer(metin):
        span = (m.start(), m.end())
        if _cakisir(span, [(s, e) for (s, e, _no) in kararlar]):
            continue
        kararlar.append((span[0], span[1], norm_no(m.group(1))))

    esaslar.sort(key=lambda t: t[0])
    kararlar.sort(key=lambda t: t[0])
    return esaslar, kararlar


def _satir_no(metin, konum):
    return metin.count("\n", 0, konum) + 1


def _ozel_kunye_atiflari(metin, dolu_spanlar):
    """B-2 (v0.5.14) — AYM bireysel başvuru + AİHM künyeleri. Esas/karar
    çiftiyle ÖRTÜŞMEYEN eşleşmeler atıf olarak döner; `karar` alanı None'dır
    (bu künye türlerinde karar numarası YOKTUR — 6216 s. K. m.45-49 usulü)."""
    ekler = []
    for rx, tur in ((AYM_BB_RE, "aym_bb"), (AIHM_BASVURU_RE, "aihm_basvuru")):
        for m in rx.finditer(metin):
            if _cakisir((m.start(), m.end()), dolu_spanlar):
                continue
            ekler.append({
                "esas": norm_no(m.group(1)),
                "karar": None,
                "daire_key": None,
                "kunye_turu": tur,
                "satir_no": _satir_no(metin, m.start()),
                "metin": _sikistir(m.group(0)),
                "bas": m.start(), "son": m.end(),
            })
    return ekler


def esas_karar_atiflari(metin):
    """Belge-geneli çıkarım: her esas'ı en yakın kararla eşler (nearest-pairing);
    her atıf için {esas, karar, merci, daire_key, satir_no, metin} sözlüğü döner.

    v0.5.14 (B-2): sözlüğe İKİ EK ALAN girdi — `kunye_turu`
    ('esas_karar' | 'aym_bb' | 'aihm_basvuru') ve ham `bas`/`son` ofsetleri.
    Alanlar EKLEMELİDİR (eski okuyucular etkilenmez); AYM/AİHM künyeleri de
    artık bu listeye girer."""
    esaslar, kararlar = _esas_karar_ham_cikar(metin)

    kullanilan_k = set()
    atiflar = []
    dolu_spanlar = []
    for (es, ee, eno) in esaslar:
        en_iyi, en_mesafe = None, 61
        for idx, (ks, ke, kno) in enumerate(kararlar):
            if idx in kullanilan_k:
                continue
            mesafe = ks - ee if ks >= ee else es - ke
            if 0 <= mesafe < en_mesafe:
                en_iyi, en_mesafe = idx, mesafe
        bas, son = es, ee
        karar_no = None
        if en_iyi is not None:
            kullanilan_k.add(en_iyi)
            ks, ke, kno = kararlar[en_iyi]
            karar_no = kno
            bas, son = min(bas, ks), max(son, ke)
        pencere = metin[max(0, bas - 70):bas]
        merci_bulunan = list(MERCI_RE.finditer(pencere))
        if merci_bulunan:
            bas = max(0, bas - 70) + merci_bulunan[0].start()
        ham_kunye = metin[bas:son]
        dkey = daire_key(ham_kunye)
        dolu_spanlar.append((bas, son))
        atiflar.append({
            "esas": eno,
            "karar": karar_no,
            "daire_key": dkey,
            "kunye_turu": "esas_karar",
            "satir_no": _satir_no(metin, es),
            "metin": _sikistir(ham_kunye),
            "bas": bas, "son": son,
        })
    atiflar.extend(_ozel_kunye_atiflari(metin, dolu_spanlar))
    atiflar.sort(key=lambda a: a["bas"])
    return atiflar


# ── B-2 (v0.5.14) — VARSAYILAN TERS ÇEVRİLDİ: AYRIŞTIRILAMAYAN ATIF BLOKTUR ─
# Denetim kanıtı: iki uydurma künye taşıyan istinaf taslağı uçtan uca
# "TESLİME HAZIR" (rc=0) aldı, çünkü kapı künyeyi ayrıştıramayınca "atıf yok"
# diyor ve AÇILIYORDU (fail-OPEN). Bu ailenin varlık sebebi tam tersidir:
# mekanik teyit YAPILAMADIYSA kapı KAPANIR. Kapsam DAR tutulur — yanlış-BLOK
# muhakemeyi engeller (AMAÇ ÇİZGİSİ): tetik, merci anılan bir SATIRDA bir
# karar iması bulunup o satırdan HİÇ künye çıkarılamamasıdır.
_KARAR_IMASI_RE = re.compile(
    r"\d{4}\s*/\s*\d{1,6}"
    r"|(?i:say[ıi]l[ıi]\s+karar)"
    r"|(?i:tarih(?:li|inde)?\s+karar)"
    r"|(?i:g[üu]nl[üu]\s+karar)")


def ayristirilamayan_atiflar(metin, dolu_satirlar=None):
    """Merci anılan ve karar iması taşıyan ama künyesi ÇIKARILAMAYAN satırlar.
    Döner: [{"satir_no", "metin", "sebep"}, ...] — çağıran bunları TEYİTSİZ
    sınıfında değerlendirip kapıyı KAPATIR.

    `dolu_satirlar`: üzerinde ZATEN bir atıf ayrıştırılmış satır numaraları
    (1-index). Verilmezse bu modülün kendi çıkarımından hesaplanır; çağıran
    (ör. `kunye_teyit.py`) mevzuat atıflarını da kapsayan kendi kümesini
    geçebilir.

    YANLIŞ-POZİTİF KORUMALARI (üçü birden):
      1. Satırda ZATEN bir künye ayrıştırıldıysa satır atlanır (tam künyeli
         '… E. 2020/1111 K. 2021/2222 sayılı kararı' cümlesi tetiklemez).
      2. Satır dilekçenin KENDİ künye bloğuysa (`DOSYA NO`/`ESAS NO`/`MERCİ`)
         atlanır — Denizli 346 karnesinin tek parser yanlış-pozitifi.
      3. Merci VE karar iması AYNI SATIRDA olmalıdır; yalnız merci anmak
         ('Yargıtay'ın yerleşik içtihadı') hiçbir zaman tetiklemez."""
    if dolu_satirlar is None:
        dolu_satirlar = {a["satir_no"] for a in esas_karar_atiflari(metin)}
    else:
        dolu_satirlar = set(dolu_satirlar)
    izler, gorulen = [], set()
    for satir_no, satir in enumerate(metin.split("\n"), start=1):
        if satir_no in dolu_satirlar or satir_no in gorulen:
            continue
        if not MERCI_RE.search(satir):
            continue
        ima = _KARAR_IMASI_RE.search(satir)
        if not ima:
            continue
        if KENDI_DOSYA_SATIR_RE.match(satir):
            continue
        gorulen.add(satir_no)
        izler.append({
            "satir_no": satir_no,
            "metin": _sikistir(satir),
            "sebep": ("merci anılıyor ve karar iması var (%r) ama künye "
                      "(esas/karar ya da başvuru numarası) ÇIKARILAMADI — "
                      "mekanik teyit YAPILAMADI" % _sikistir(ima.group(0), 40)),
        })
    return izler


# ── B-18 (v0.5.14) — MAKİNE ÜRETİMİ KAYNAKÇA BLOĞU: TEK KAYNAK ─────────────
# `kaynakca_uret.py` taslağın SONUNA işaretli bir blok yazar. O blok avukatın
# GÖVDE METNİ DEĞİLDİR; denetim kapıları onu kendi girdileri sanınca zincir
# İDEMPOTANSINI kaybediyordu (denetim kanıtı: aynı komut aynı dosyada
# `rc=0 → rc=1 → rc=1`; blok içindeki "⚠" işaretini dilekçe denetiminin [C]
# OCR/alıntı teyidi yakalıyordu). İşaretler ve üretecin kendi önsöz satırları
# BURADA tanımlanır — üretici de maskeleyici de aynı kaynaktan okur.
KAYNAKCA_BLOK_BAS = "<!-- kaynakca:v1 -->"
KAYNAKCA_BLOK_SON = "<!-- /kaynakca -->"
KAYNAKCA_BASLIK = "## İÇTİHAT KAYNAKÇASI"
KAYNAKCA_ONSOZ_SATIRLARI = (
    "Aşağıdaki kararların tamamı tam metinleriyle okunup kütüğe",
    "damgalanmıştır; erişim linkleri teyit kaydından gelir (bu blok",
    "Aşağıdaki listede her kararın TEYİT DURUMU ayrıca gösterilmiştir:",
    "\"⚠ TEYİT EDİLMEDİ\" işaretli künyeler için tam metin teyidi",
    "YAPILMAMIŞTIR; erişim linkleri yalnız teyit kaydından gelir (bu blok",
    "`kaynakca_uret.py` tarafından mekanik üretilir — elle yazılmaz).",
)

_KAYNAKCA_BLOK_RE = re.compile(
    re.escape(KAYNAKCA_BLOK_BAS) + r".*?" + re.escape(KAYNAKCA_BLOK_SON), re.S)


def makine_blogu_maskele(metin):
    """Makine üretimi kaynakça bloğunun ÜRETECE AİT satırlarını aynı uzunlukta
    boşlukla değiştirir (ofsetler ve satır numaraları KORUNUR).

    KÖTÜYE KULLANIM KORUMASI: yalnız işaret satırları, blok başlığı, üretecin
    kendi önsöz satırları ve `- ` ile başlayan künye maddeleri maskelenir.
    İşaretler arasına elle sokuşturulan DÜZ METİN maskelenmez — kapı, metne
    yorum işareti yazarak atlatılamaz."""
    if KAYNAKCA_BLOK_BAS not in metin:
        return metin
    parcalar = []
    son = 0
    for m in _KAYNAKCA_BLOK_RE.finditer(metin):
        parcalar.append(metin[son:m.start()])
        yeni = []
        for satir in m.group(0).split("\n"):
            s = satir.strip()
            uretece_ait = (
                not s
                or s in (KAYNAKCA_BLOK_BAS, KAYNAKCA_BLOK_SON, KAYNAKCA_BASLIK)
                or s.startswith("- ")
                or s in KAYNAKCA_ONSOZ_SATIRLARI)
            yeni.append(" " * len(satir) if uretece_ait else satir)
        parcalar.append("\n".join(yeni))
        son = m.end()
    parcalar.append(metin[son:])
    return "".join(parcalar)


def kunye_normalize(kunye_metin):
    """TEK bir künye pasajı (ör. '**KUNYE:** Yargıtay 4. HD, E. 2023/1234, K.
    2023/5678, T. 12.09.2023' satırının değeri) için (esas, karar) çiftini
    döndürür. Pasajda birden çok esas/karar geçse bile İLK çifti alır — bir
    KUNYE alanı tanım gereği TEK bir kararı tanımlar. Esas ve/veya karar
    bulunamazsa ilgili öğe None olur. 'Temizleme' yapmaz — yalnız metinde
    zaten var olan sayıları kanonikleştirir."""
    if not kunye_metin:
        return (None, None)
    atiflar = esas_karar_atiflari(kunye_metin)
    if not atiflar:
        return (None, None)
    a = atiflar[0]
    return (a["esas"], a["karar"])


def sayi_var(segment, sayi):
    """Sayıyı komşu rakamdan izole ederek arar (149 ≠ 49)."""
    if not sayi:
        return False
    return re.search(r"(?<!\d)" + re.escape(sayi) + r"(?!\d)", segment) is not None


# ── P0-3 (v0.5.5) — çok-bölümlü muhakeme dosyası ayrıştırıcı ────────────────
# `oa_hafiza.py teyit --damga` artık `_oa/cikti/03-ictihat-muhakeme.md`'ye
# bölüm APPEND eder (bir dosya = N kayıt); eski "bir dosya = bir karar"
# varsayımı (`ictihat_muhakeme_denetim.py`) buna göre genişler. Ayraç, ALANIN
# KENDİSİDİR (`**KUNYE:**` satır-başı bold alan) — parser'a YENİ bir sözdizimi
# (ör. `## KUNYE:` başlığı) EKLENMEZ (tek-yazar kuralı: ikinci regex evreni
# doğmaz). Eski tek-karar dosyaları (tek `**KUNYE:**`) DEĞİŞMEDEN, tek bölüm
# olarak okunur (geriye uyum — bit düzeyinde davranış aynı).
_KUNYE_BOLUM_RE = re.compile(r"^\*\*KUNYE:\*\*", re.M)


def bolum_araliklari(metin):
    """`bolumlere_ayir` ile AYNI ayracı (satır-başı `**KUNYE:**`) kullanarak
    bölümlerin (başlangıç, bitiş) OFSET çiftlerini döndürür — 0/1 eşleşmede
    TEK bölüm `[(0, len(metin))]` olarak döner.

    P0-2 DÜZELTME (d, v0.5.5): bir bölümü SURGICAL olarak düzenlemek isteyen
    çağıranlar (ör. `oa_hafiza.py`'nin DAMGA değişince eski bölüme
    `**GEÇERSİZ-KILINDI:**` satırı eklemesi) tam metin yerine ofset ister —
    içerik SİLİNMEZ/YENİDEN YAZILMAZ, yalnız doğru konuma satır eklenir. Ayraç
    mantığı burada TEK yerde yaşar (tek-yazar kuralı); `bolumlere_ayir` bu
    fonksiyonun üzerine kurulur, ikinci bir regex evreni açılmaz."""
    eslesmeler = list(_KUNYE_BOLUM_RE.finditer(metin))
    if len(eslesmeler) <= 1:
        return [(0, len(metin))]
    sinirlar = [m.start() for m in eslesmeler] + [len(metin)]
    return [(sinirlar[i], sinirlar[i + 1]) for i in range(len(eslesmeler))]


def bolumlere_ayir(metin):
    """Metni (dosya içeriği) `**KUNYE:**` satır-başlarından bağımsız bölümlere
    ayırır. 0 veya 1 eşleşme varsa TÜM metni TEK bölüm olarak döner (eski
    tek-karar dosyaları ve gövde metninde geçen serbest 'KUNYE' kelimesi bölüm
    başlatmaz — regex yalnız satır-başı `**KUNYE:**` ile eşleşir)."""
    return [metin[a:b] for (a, b) in bolum_araliklari(metin)]


_DAMGA_TOKEN_RE = re.compile(r"DAMGA=([A-ZÇĞİÖŞÜa-zçğıöşü-]+)")


def kutukten_son_damga(kutuk_yolu, esas, karar, daire=None):
    """Künye teyit kütüğündeki (append-only, `| Zaman | Araç | Sorgu | Sonuç |
    Döküm |` satırları) bir esas/karar (+ opsiyonel `daire`) için SON `DAMGA=`
    tokenını döndürür; kütük yoksa/okunamazsa/eşleşme yoksa None.

    PAYLAŞIMLI (P0-2 DÜZELTME d, v0.5.5): hem `ictihat_muhakeme_denetim.py`
    (okuma-zamanı çapraz kontrol — muhakeme bölümü elle değiştirilmiş mi) HEM
    `oa_hafiza.py` (YAZMA-ÖNCESİ çapraz kontrol — aynı künyeye ikinci bir
    `teyit --damga` ile SESSİZCE farklı damga vurulması engellenir) bu
    fonksiyonu çağırır; kütük satır biçimi tek yerde ayrıştırılır (tek-yazar
    kuralı — iki script arasında sürüklenip ayrışmaz).

    DÜZELTME (v0.5.5 düzeltme turu — DAİRE-KÖR + fail-open bug'ları):
    - `daire` verilirse VE kütük satırının sonuç hücresinden bir daire
      çıkarılabiliyorsa (`daire_key`), İKİSİ DE tanınıyorken FARKLIYSA satır
      eşleşme SAYILMAZ — esas/karar no'ları her dairede yılda sıfırdan
      başladığından, GERÇEKTEN FARKLI bir dairenin aynı numaralı kararı bu
      künyenin 'son damgası' sanılmaz (eski daire-kör davranış, MuhakemeKaydi.
      eslesir'in aynı ilkesiyle simetrik hâle getirilir).
    - Satırın hücre sayısı beklenen 5-sütun biçimine (tam 6 `|`, split→7
      eleman) uymuyorsa satır BOZUK sayılıp GÖRÜNÜR bir uyarıyla fail-CLOSED
      atlanır (eski `len(hucreler) < 5` gevşekliği, kaçmamış bir `|` ile
      kolon kaymasını SESSİZCE yutuyordu — sessiz atlama yasağı).
    - `esas` VE `karar` her ikisi de biliniyorsa satırda İKİSİNİN DE dize
      olarak geçmesi şart koşulur (`esas_var OR karar_var` gevşekliği, yalnız
      TEK bir sayısı çakışan alakasız bir satırın damgasını 'son damga'
      sanabiliyordu — fail-open bug)."""
    if not (esas or karar) or not kutuk_yolu or not os.path.isfile(kutuk_yolu):
        return None
    try:
        with open(kutuk_yolu, encoding="utf-8", errors="replace") as f:
            satirlar = f.readlines()
    except OSError:
        return None
    son_damga = None
    for satir in satirlar:
        if not satir.startswith("|"):
            continue
        hucreler = satir.split("|")
        if len(hucreler) != 7:
            _sys.stderr.write(
                "UYARI (kunye_ortak.kutukten_son_damga): kütük satırı beklenen "
                f"5-sütun biçiminde değil ({len(hucreler)} hücre, 7 beklenirdi) — "
                "BOZUK sayılıp fail-CLOSED atlandı: " + satir.strip()[:160] + "\n")
            continue
        sonuc_hucresi = hucreler[4]
        esas_var = bool(esas) and sayi_var(sonuc_hucresi, esas)
        karar_var = bool(karar) and sayi_var(sonuc_hucresi, karar)
        if esas and karar:
            if not (esas_var and karar_var):
                continue
        elif esas:
            if not esas_var:
                continue
        elif karar:
            if not karar_var:
                continue
        else:
            continue
        if daire is not None:
            satir_daire = daire_key(sonuc_hucresi)
            if satir_daire is not None and satir_daire != daire:
                continue
        m = _DAMGA_TOKEN_RE.search(sonuc_hucresi)
        if m:
            son_damga = m.group(1).upper()
    return son_damga


def _kutuk_satirlarini_oku(kutuk_yolu):
    """Ortak yardımcı — künye teyit kütüğünü satır satır okur; dosya yoksa/
    okunamazsa boş liste döner (çağıranlar bunu fail-open/fail-closed olarak
    kendileri yorumlar)."""
    if not kutuk_yolu or not os.path.isfile(kutuk_yolu):
        return []
    try:
        with open(kutuk_yolu, encoding="utf-8", errors="replace") as f:
            return f.readlines()
    except OSError:
        return []


def kutuk_gercek_veri_var_mi(kutuk_yolu):
    """DÜZELTME (v0.5.5 şerh turu — Ş2, HAYALET MUHAKEME ikinci katman):
    kütük dosyasının fiilen EN AZ BİR gerçek (7 hücreli, `kutukten_son_damga`
    ile AYNI biçim şartı) veri satırı taşıyıp taşımadığını söyler. Dosya hiç
    yoksa, boşsa ya da yalnız başlık/ayraç satırları içeriyorsa 'kütük fiilen
    kullanılmıyor' sayılır — bu durumda `kutuk_son_damga_engeli` (mevcut,
    DOKUNULMAZ) ve `kutukte_esas_karar_satiri_var_mi` (yeni) SESSİZCE
    atlanır: elle kurulmuş test iskeletleri / 'derin yol' (doğrudan dosya
    yazımıyla muhakeme kaydı oluşturma — P1-11 playbook'u) davranışı BOZULMAZ
    (bkz. `test_kutuk_yoksa_denetim_sessizce_atlanir_geriye_uyum` — bit
    düzeyinde korunan geriye-uyum invaryantı). Kütük FİİLEN kullanılıyorsa
    (≥1 gerçek satır — yani bu kökte gerçek `teyit` çağrıları YAPILMIŞ),
    'bu künyenin kütükte hiç izi yok' denetimi anlamlı ve fail-closed hâle
    gelir.

    DİKKAT: `oa_hafiza.py init`'in yazdığı BOŞ kütük şablonu da (başlık +
    `|---|---|---|---|---|` ayraç satırı) tesadüfen 7-hücreye böler — bu
    İKİ satır 'gerçek veri' SAYILMAZ (aksi hâlde hiç `teyit` çağrısı
    yapılmamış TAZE bir `_oa` kökünde bile derin-yol/elle-yazım BLOKLANIRDI).
    Ayırt edici: gerçek bir satırın ZAMAN hücresi `ts()`'ten gelir (ISO
    tarih-saat), başlık hücresi 'Zaman' sabit metnidir, ayraç hücresi yalnız
    `-` karakterlerinden oluşur."""
    for satir in _kutuk_satirlarini_oku(kutuk_yolu):
        if not satir.startswith("|"):
            continue
        hucreler = satir.split("|")
        if len(hucreler) != 7:
            continue
        ilk_hucre = hucreler[1].strip()
        if not ilk_hucre or ilk_hucre.casefold() == "zaman":
            continue  # başlık satırı
        if set(ilk_hucre) <= {"-"}:
            continue  # markdown ayraç satırı (|---|---|...|)
        return True
    return False


def kutukte_esas_karar_satiri_var_mi(kutuk_yolu, esas, karar, daire=None):
    """DÜZELTME (v0.5.5 şerh turu — Ş2, t3 HAYALET MUHAKEME BLOKERİ): künye
    teyit kütüğünde bu esas/karar (+ opsiyonel daire) için EN AZ BİR gerçek
    satır (DAMGA'lı olsun olmasın) bulunup bulunmadığını söyler.
    `kutukten_son_damga` ile AYNI 7-hücre/esas-karar-daire eşleşme mantığını
    kullanır (tek-yazar kuralı) ama yalnız 'satır var mı' sorusuna cevap
    verir — DAMGA tokenı ARANMAZ; bu fonksiyonun amacı damga çapraz kontrolü
    DEĞİL, kaydın FİİLEN bir `teyit` çağrısına dayandığının doğrulanmasıdır.
    Yalnız `kutuk_gercek_veri_var_mi` True dönerken (kütük fiilen
    kullanılıyorken) çağrılması amaçlanır (bkz. `ictihat_muhakeme_denetim.
    kutuk_dayanagi_denetle`)."""
    if not (esas or karar):
        return False
    for satir in _kutuk_satirlarini_oku(kutuk_yolu):
        if not satir.startswith("|"):
            continue
        hucreler = satir.split("|")
        if len(hucreler) != 7:
            continue
        sonuc_hucresi = hucreler[4]
        esas_var = bool(esas) and sayi_var(sonuc_hucresi, esas)
        karar_var = bool(karar) and sayi_var(sonuc_hucresi, karar)
        if esas and karar:
            if not (esas_var and karar_var):
                continue
        elif esas:
            if not esas_var:
                continue
        elif karar:
            if not karar_var:
                continue
        else:
            continue
        if daire is not None:
            satir_daire = daire_key(sonuc_hucresi)
            if satir_daire is not None and satir_daire != daire:
                continue
        return True
    return False


def kutukte_damgali_dayanak_satiri_var_mi(kutuk_yolu, esas, karar, damga, kaynak_izi=None, daire=None):
    """DÜZELTME (v0.5.5 düzeltme turu — Ş2/t3-B, HAYALET MUHAKEME İKİNCİ
    KATMAN): `kutukte_esas_karar_satiri_var_mi` yalnız 'bu esas/karar no
    kütükte HERHANGİ bir satırda geçiyor mu' sorusuna cevap verir — DAMGA
    tokenı ARANMAZ. Bu, damgasız/tam-metinsiz UCUZ bir ARAMA teyidinin
    (`teyit --arac ictihat_ara --sonuc "<uydurma künye>"`, döküm-icerik'siz,
    --damga'sız, kod=0) bir HAYALET muhakeme bölümünü meşrulaştırmasına izin
    veriyordu (canlı kanıt: sb6 — sıfır elle dosya düzenlemesi, yalnız 3 CLI
    çağrısıyla uydurma bir karar `[OK]`/`DAMGA: LEHE` ile G2/G3'ten geçti).

    Bu fonksiyon DAHA SIKI bir dayanak arar: kütükte bu esas/karar (+daire)
    için (a) muhakeme bölümündeki DAMGA ile AYNI `DAMGA=` tokenını taşıyan
    VE (b) `kaynak_izi` verildiyse döküm hücresinin bu KAYNAK-IZI dosyasını
    (dize olarak) işaret ettiği EN AZ BİR satır bulunmalıdır. Damgasız bir
    ARAMA satırı hiçbir zaman bu denetimi geçemez (ARAMA sınıfına `--damga`
    zaten YASAK olduğundan `DAMGA=` tokenı hiç taşımaz) — damgalı bir
    muhakeme bölümünün dayanağı da damgasız bir ARAMA satırı OLAMAZ (mevcut
    ARAMA/GETİR ayrımıyla simetrik). `damga` None/boşsa (DAMGA alanı zaten
    başka bir denetimde eksik sayılıp engellenir) False döner — çağıran
    taraf bu durumda çağırmayı atlayabilir."""
    if not (esas or karar) or not damga:
        return False
    damga_u = damga.strip().upper()
    if not damga_u:
        return False
    for satir in _kutuk_satirlarini_oku(kutuk_yolu):
        if not satir.startswith("|"):
            continue
        hucreler = satir.split("|")
        if len(hucreler) != 7:
            continue
        sonuc_hucresi = hucreler[4]
        dokum_hucresi = hucreler[5]
        esas_var = bool(esas) and sayi_var(sonuc_hucresi, esas)
        karar_var = bool(karar) and sayi_var(sonuc_hucresi, karar)
        if esas and karar:
            if not (esas_var and karar_var):
                continue
        elif esas:
            if not esas_var:
                continue
        elif karar:
            if not karar_var:
                continue
        else:
            continue
        if daire is not None:
            satir_daire = daire_key(sonuc_hucresi)
            if satir_daire is not None and satir_daire != daire:
                continue
        m = _DAMGA_TOKEN_RE.search(sonuc_hucresi)
        if not m or m.group(1).upper() != damga_u:
            continue
        if kaynak_izi and kaynak_izi.strip() and kaynak_izi.strip() not in dokum_hucresi:
            continue
        return True
    return False

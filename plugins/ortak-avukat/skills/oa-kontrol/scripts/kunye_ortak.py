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

import re

_YN = r"\d{4}\s*/\s*\d{1,6}"

ESAS_RE = re.compile(
    r"(?:\bE\.\s*(?:No\.?)?\s*[:.]?\s*|\bEsas\b\s*(?:No\.?)?\s*[:.]?\s*)(" + _YN + r")"
    r"|(" + _YN + r")\s*(?:\bE\.|\bEsas\b)"
)
KARAR_RE = re.compile(
    r"(?:\bK\.\s*(?:No\.?)?\s*[:.]?\s*|\bKarar\b\s*(?:No\.?)?\s*[:.]?\s*)(" + _YN + r")"
    r"|(" + _YN + r")\s*(?:\bK\.|\bKarar\b)"
)
ESAS_TAG_RE = re.compile(
    r"(?:\bE\.\s*(?:No\.?)?\s*[:.]?\s*|\bEsas\b\s*(?:No\.?)?\s*[:.]?\s*)(" + _YN + r")"
)
KARAR_TAG_RE = re.compile(
    r"(?:\bK\.\s*(?:No\.?)?\s*[:.]?\s*|\bKarar\b\s*(?:No\.?)?\s*[:.]?\s*)(" + _YN + r")"
)

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


def esas_karar_atiflari(metin):
    """Belge-geneli çıkarım: her esas'ı en yakın kararla eşler (nearest-pairing);
    her atıf için {esas, karar, merci, daire_key, satir_no, metin} sözlüğü döner."""
    esaslar, kararlar = _esas_karar_ham_cikar(metin)

    kullanilan_k = set()
    atiflar = []
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
        atiflar.append({
            "esas": eno,
            "karar": karar_no,
            "daire_key": dkey,
            "satir_no": _satir_no(metin, es),
            "metin": _sikistir(ham_kunye),
        })
    return atiflar


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

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

# ── K4 (v0.5.16, Hamle 3) — KURUL ESAS BİÇİMİ ────────────────────────────
# Yargıtay HGK/CGK (ve İBK) esas numarası «YYYY/<daire>-<sıra>» biçimlidir
# (ör. «E. 2020/9-111»). Eski `_YN` bunu «2020/9» diye KESİYORDU — künye
# yanlış kanonikleşince kütük/döküm eşleşmesi de yanlış oluyordu. Tire
# soneki artık sayının parçasıdır; ama «-YYYY/N» (E-K birleşik ikinci
# yarısı) yutulmasın diye tire sonrasının «/» ile devam etmemesi şart.
# ONARIM (hakem, 2026-09-07 — K4 REGRESYON): «(?!\s*/)» tek başına YETMEZ —
# regex motoru «-2021» reddedilince GERİ İZLEYİP «-202»de durur ve
# «E. 2020/1111-2021/2222» girdisinde esas «2020/1111-202» (bozuk), karar
# kaybı, sahte EKSİK KÜNYE üretirdi (taban aynı girdide TAM künye veriyordu).
# «\b» kelime sınırı geri izlemeyi keser: tire soneki ya TAM sayı olarak
# eşleşir (kurul: «2020/9-111») ya da hiç eşleşmez (birleşik: «2020/1111»).
_YN = r"\d{4}\s*/\s*\d{1,6}(?:-\d{1,6}\b(?!\s*/))?"

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


# ── K4 (v0.5.16, Hamle 3 / Karar #4) — BİRLEŞİK E-K BİÇİMİ ─────────────────
# Yargıtay künyesi sahada sık «2020/1111-2021/2222» ya da aynı yılda
# «2019/4444-5555» (esas-karar tireyle birleşik, etiketsiz) yazılır. Eski
# tanıyıcı bu biçimi ne ayrıştırıyor ne de EKSİK sayıyordu — «sayılı» iması
# yüzünden yalnız 'ayrıştırılamadı' bloğuna düşüyordu. Şimdi TAM künyeye
# (esas+karar) AYRIŞTIRILIR. İki koruma: (1) merci anılan satırla sınırlı
# (mercisiz sayı çifti tarih/telefon/tutar olabilir — yanlış-teyit yasağı);
# (2) KURUL mercilerinde (HGK/CGK/İBK/İDDK/VDDK) «YYYY/N-N» daire-sıra
# biçimli TEK esas numarasıdır (bkz. `_YN`), E-K diye BÖLÜNMEZ — o satır
# etiketsizse EKSİK KÜNYE sınıfına düşer (fail-closed).
_KURUL_MERCI_RE = re.compile(
    r"\b(?:HGK|CGK|[İI]BK|[İI]DDK|VDDK|Hukuk\s+Genel\s+Kurulu|Ceza\s+Genel\s+Kurulu|"
    r"[İI]çtihad[ıi]\s+Birle[şs]tirme)\b")
BIRLESIK_EK_RE = re.compile(
    r"(?<![\d/.-])(\d{4})\s*/\s*(\d{1,6})\s*[-–]\s*(?:(\d{4})\s*/\s*)?(\d{1,6})(?![\d/.-])")
# ONARIM (hakem, 2026-09-07) — ETİKETLİ birleşik biçim «E. 2020/1111-2021/2222
# [K.] sayılı»: `_YN` tire sonekini «-YYYY/N» önünde bırakınca esas «2020/1111»
# olarak ayrışır (tabanla aynı); K. etiketi yoksa tirenin ardındaki «YYYY/N»
# bu kuyruk deseniyle KARAR olarak tamamlanır (kurul dışı satırda). Aynı-yıl
# «E. 2019/4444-5555» ise `_YN` tarafından bütün olarak yakalanır; satırda
# kurul anılmıyor VE numaralı daire varsa (kurul esasında daire olmaz) E-K
# diye bölünür; ne kurul ne daire varsa belirsizdir → bütün kalır (E-only →
# EKSİK KÜNYE, fail-closed).
_ETIKETLI_BIRLESIK_KUYRUK_RE = re.compile(r"\s*[-–]\s*(\d{4})\s*/\s*(\d{1,6})(?![\d/.-])")


def _satir_metni(metin, konum):
    bas = metin.rfind("\n", 0, konum) + 1
    son = metin.find("\n", konum)
    return metin[bas:(son if son != -1 else len(metin))]


def _pencere_basi(metin, bas, genislik=70):
    """K4 — merci geri-bakış penceresinin başlangıcı: en fazla `genislik`
    karakter geriye, ama SATIR BAŞINI aşmadan (bir önceki satırın mercisi bu
    künyeye yapışmasın — künye ile mercisi aynı satırda anılır)."""
    return max(0, bas - genislik, metin.rfind("\n", 0, bas) + 1)


def _birlesik_ek_atiflari(metin, dolu_spanlar):
    """K4 — etiketsiz birleşik «YYYY/N-N» / «YYYY/N-YYYY/N» çiftlerini esas+karar
    olarak döndürür (merci anılan, kurul olmayan satırlarda; dolu spanlarla
    örtüşmeyen eşleşmeler)."""
    ekler = []
    for m in BIRLESIK_EK_RE.finditer(metin):
        if _cakisir((m.start(), m.end()), dolu_spanlar):
            continue
        satir = _satir_metni(metin, m.start())
        if not MERCI_RE.search(satir) or _KURUL_MERCI_RE.search(satir):
            continue
        esas = f"{m.group(1)}/{m.group(2)}"
        karar = f"{m.group(3) or m.group(1)}/{m.group(4)}"
        bas, son = m.start(), m.end()
        pencere_bas = _pencere_basi(metin, bas)
        pencere = metin[pencere_bas:bas]
        merci_bulunan = list(MERCI_RE.finditer(pencere))
        if merci_bulunan:
            bas = pencere_bas + merci_bulunan[0].start()
        ham_kunye = metin[bas:son]
        ekler.append({
            "esas": esas,
            "karar": karar,
            "daire_key": daire_key(ham_kunye),
            "kunye_turu": "esas_karar",
            "bicim": "birlesik",
            "satir_no": _satir_no(metin, m.start()),
            "metin": _sikistir(ham_kunye),
            "bas": bas, "son": son,
        })
    return ekler


def esas_karar_atiflari(metin):
    """Belge-geneli çıkarım: her esas'ı en yakın kararla eşler (nearest-pairing);
    her atıf için {esas, karar, merci, daire_key, satir_no, metin} sözlüğü döner.

    v0.5.14 (B-2): sözlüğe İKİ EK ALAN girdi — `kunye_turu`
    ('esas_karar' | 'aym_bb' | 'aihm_basvuru') ve ham `bas`/`son` ofsetleri.
    Alanlar EKLEMELİDİR (eski okuyucular etkilenmez); AYM/AİHM künyeleri de
    artık bu listeye girer.

    v0.5.16 (K4): etiketsiz BİRLEŞİK «YYYY/N-N sayılı» biçimi de esas+karar
    olarak girer (`_birlesik_ek_atiflari`; `bicim='birlesik'` ek alanı);
    kurul (HGK/CGK) «YYYY/N-N» esas numarası tek sayı olarak korunur."""
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
        bicim = None
        if en_iyi is not None:
            kullanilan_k.add(en_iyi)
            ks, ke, kno = kararlar[en_iyi]
            karar_no = kno
            bas, son = min(bas, ks), max(son, ke)
        elif not _KURUL_MERCI_RE.search(_satir_metni(metin, es)):
            # ONARIM (hakem, 2026-09-07) — etiketli birleşik yükseltmesi
            # (bkz. `_ETIKETLI_BIRLESIK_KUYRUK_RE` açıklaması).
            m_kuyruk = _ETIKETLI_BIRLESIK_KUYRUK_RE.match(metin, ee)
            if m_kuyruk:
                karar_no = f"{m_kuyruk.group(1)}/{m_kuyruk.group(2)}"
                son, bicim = m_kuyruk.end(), "birlesik"
            elif "-" in eno and daire_key(_satir_metni(metin, es)):
                e_parca, k_parca = eno.split("-", 1)
                eno, karar_no = e_parca, f"{e_parca.split('/')[0]}/{k_parca}"
                bicim = "birlesik"
        # K4 (v0.5.16) — merci geri-bakış penceresi SATIRLA sınırlı: eskiden
        # 70 karakterlik pencere satır sonunu aşıyor, bir önceki satırdaki
        # başka bir künyenin mercisini («9. HD») bu künyeye yapıştırıyordu —
        # hem daire_key yanlış oluyor hem de `dolu_spanlar` önceki satırın
        # (birleşik) künyesini örtüp onu sahte «EKSİK KÜNYE» yapıyordu.
        pencere_bas = _pencere_basi(metin, bas)
        pencere = metin[pencere_bas:bas]
        merci_bulunan = list(MERCI_RE.finditer(pencere))
        if merci_bulunan:
            bas = pencere_bas + merci_bulunan[0].start()
        ham_kunye = metin[bas:son]
        dkey = daire_key(ham_kunye)
        dolu_spanlar.append((bas, son))
        atif = {
            "esas": eno,
            "karar": karar_no,
            "daire_key": dkey,
            "kunye_turu": "esas_karar",
            "satir_no": _satir_no(metin, es),
            "metin": _sikistir(ham_kunye),
            "bas": bas, "son": son,
        }
        if bicim:
            atif["bicim"] = bicim
        atiflar.append(atif)
    birlesik = _birlesik_ek_atiflari(metin, dolu_spanlar)
    dolu_spanlar.extend((a["bas"], a["son"]) for a in birlesik)
    atiflar.extend(birlesik)
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
    r"|(?i:say[ıi]l[ıi]\s+(?:karar|ilam))"
    r"|(?i:tarih(?:li|inde)?\s+(?:karar|ilam))"
    r"|(?i:g[üu]nl[üu]\s+(?:karar|ilam))")

# ── K4 (v0.5.16, Hamle 3 / Karar #3) — «EKSİK KÜNYE» SINIFI ───────────────
# İki alt biçim: (a) TARİH-ONLY «<merci> … dd.mm.yyyy tarihli kararı/ilamı»
# (tarih tek başına künye DEĞİLDİR — aynı gün aynı daire onlarca karar verir);
# (b) K-ONLY / E-ONLY «<merci>'nin YYYY/N sayılı kararı» (tek sayı; etiketli
# «K. 2021/2222» ya da «E. 2020/1111» dahil). Bunlar 'ayrıştırılamadı' değil,
# 'EKSİK' künyedir: yazar hangi kararı kastettiğini biliyor ama esas+karar
# çiftini yazmamış — mesaj tamamlatmaya yöneltir (Yargıtay birleşik biçimi
# «YYYY/N-YYYY/N» artık tanınır, bkz. `_birlesik_ek_atiflari`).
# «tarihli» kelimesi mevzuat tarihiyle («28.02.2018 tarihli Resmî Gazete»)
# karışmasın: tetik MERCİ ANILAN SATIRLA sınırlıdır ve «tarihli/günlü» ancak
# «karar/ilam» ile bitişikse imadır (yanlış-BLOK yasağı).
SINIF_EKSIK_KUNYE = "EKSİK KÜNYE"
SINIF_AYRISTIRILAMAYAN = "AYRIŞTIRILAMAYAN"
_TARIH_ONLY_RE = re.compile(
    r"\d{1,2}[./]\d{1,2}[./]\d{4}\s*(?i:tarih(?:li|inde)?|g[üu]nl[üu])\s+(?i:karar|ilam)")
_YN_SADE_RE = re.compile(r"\d{4}\s*/\s*\d{1,6}")

# ONARIM (hakem, 2026-09-07 — yanlış-BLOK adayı): «Yerel mahkemenin 05.06.2024
# tarihli kararı Yargıtay'ın yerleşik içtihadına aykırıdır.» istinaf/temyiz
# dilekçesinde ÇOK sık cümledir; tarih KENDİ dosyasının kararına aittir, merci
# yalnız genel içtihat anımıdır. Tarih-only iması ancak tarih MERCİYE AİTSE
# geçerlidir (yapısal ölçüt, hukuki yorum değil): merci tarihten ÖNCE aynı
# satırda anılmış VE aradaki metinde başka bir mahkeme iyeliği («yerel
# mahkemenin», «ilk derece mahkemesinin», «… hâkimliğinin») yok. «Bölge
# Adliye Mahkemesinin 05.06.2024 tarihli kararı» yine imadır (merci sözcüğü
# mahkeme adının kendisidir; arada iyelik yoktur).
_ARA_MAHKEME_IYELIGI_RE = re.compile(
    r"(?i)\bmahkeme(?:si)?n[iı]n\b|\bilk\s+derece\b|\byerel\b|\bh[âa]kimli[ğg]i(?:nin)?\b")
_TARIH_IMASI_BAS_RE = re.compile(r"(?i)^(?:tarih|g[üu]nl[üu])")


def _tarih_merciye_ait(satir):
    """K4 onarım — satırdaki «dd.mm.yyyy tarihli/günlü karar/ilam» tarihlerinden
    en az biri anılan merciye ait mi (merci tarihten önce, arada mahkeme
    iyeliği yok)?"""
    for m in _TARIH_ONLY_RE.finditer(satir):
        onceki = list(MERCI_RE.finditer(satir, 0, m.start()))
        if not onceki:
            continue
        ara = satir[onceki[-1].end():m.start()]
        if _ARA_MAHKEME_IYELIGI_RE.search(ara):
            continue
        return True
    return False


def _gecerli_karar_imasi(satir):
    """K4 onarım — satırdaki İLK geçerli karar iması (re.Match) ya da None.
    Sayı («2020/1111») ve «sayılı karar» imaları daima geçerlidir; «tarihli/
    günlü karar» iması, satırda tarihli-karar kalıbı varsa ancak tarih
    merciye aitse geçerlidir (tarih kalıbı hiç yoksa eski davranış korunur —
    fail-closed)."""
    ilk_tarih_imasi = None
    for m in _KARAR_IMASI_RE.finditer(satir):
        if not _TARIH_IMASI_BAS_RE.match(m.group(0)):
            return m
        if ilk_tarih_imasi is None:
            ilk_tarih_imasi = m
    if ilk_tarih_imasi is None:
        return None
    if _TARIH_ONLY_RE.search(satir) and not _tarih_merciye_ait(satir):
        return None
    return ilk_tarih_imasi


def _satir_tamlik(metin):
    """K4 — satır başına künye TAMLIĞI: (tam_satirlar, eksik_satirlar).
    'Tam' = esas+karar çifti ya da AYM/AİHM başvuru numarası ayrışmış satır;
    'eksik' = yalnız esas-only/karar-only atıf ayrışmış (tam künyesiz) satır."""
    tam, eksik = set(), set()
    for a in esas_karar_atiflari(metin):
        if a.get("kunye_turu") != "esas_karar" or (a["esas"] and a["karar"]):
            tam.add(a["satir_no"])
        else:
            eksik.add(a["satir_no"])
    return tam, eksik - tam


def _eksik_alt_bicim(satir):
    """K4 — EKSİK KÜNYE alt biçimi: 'K-only' | 'E-only' | 'E/K belirsiz' |
    'tarih-only' | None (eksik-künye kalıbı yok → genel ayrıştırılamayan)."""
    if _YN_SADE_RE.search(satir):
        k_var = bool(KARAR_RE.search(satir))
        e_var = bool(ESAS_RE.search(satir))
        if k_var and not e_var:
            return "K-only"
        if e_var and not k_var:
            return "E-only"
        return "E/K belirsiz"
    if _TARIH_ONLY_RE.search(satir):
        return "tarih-only"
    return None


def ayristirilamayan_atiflar(metin, dolu_satirlar=None):
    """Merci anılan ve karar iması taşıyan ama künyesi ÇIKARILAMAYAN ya da
    EKSİK kalan satırlar. Döner: [{"satir_no", "metin", "sebep", "sinif"},
    ...] — çağıran bunları TEYİTSİZ sınıfında değerlendirip kapıyı KAPATIR.

    `sinif` (v0.5.16/K4, EKLEMELİ alan): `SINIF_EKSIK_KUNYE` (tarih-only /
    K-only / E-only / etiketsiz tek sayı — künye eksik, tamamlanmalı) ya da
    `SINIF_AYRISTIRILAMAYAN` (karar iması var, hiçbir kalıp tanınmadı).

    `dolu_satirlar`: üzerinde ZATEN bir atıf ayrıştırılmış satır numaraları
    (1-index). Verilmezse bu modülün kendi çıkarımından hesaplanır; çağıran
    (ör. `kunye_teyit.py`) mevzuat atıflarını da kapsayan kendi kümesini
    geçebilir. K4: yalnız esas-only/karar-only atıf ayrışmış (tam künyesiz)
    satırlar 'dolu' SAYILMAZ — merci anılan bir satırdaki «E. 2020/1111
    sayılı kararı» artık EKSİK KÜNYE'dir (eskiden esas-only atıf kütükte
    tek sayı eşleşmesiyle TEYİTLİ geçebiliyordu — fail-open).

    YANLIŞ-POZİTİF KORUMALARI (üçü birden):
      1. Satırda ZATEN TAM bir künye ayrıştırıldıysa satır atlanır (tam künyeli
         '… E. 2020/1111 K. 2021/2222 sayılı kararı' cümlesi tetiklemez).
      2. Satır dilekçenin KENDİ künye bloğuysa (`DOSYA NO`/`ESAS NO`/`MERCİ`)
         atlanır — Denizli 346 karnesinin tek parser yanlış-pozitifi.
      3. Merci VE karar iması AYNI SATIRDA olmalıdır; yalnız merci anmak
         ('Yargıtay'ın yerleşik içtihadı') hiçbir zaman tetiklemez; «tarihli»
         ancak «karar/ilam» ile bitişikse imadır (RG/ihtarname tarihi değil).
      4. (onarım, 2026-09-07) Tarih-only iması ancak tarih MERCİYE AİTSE
         geçerlidir — «Yerel mahkemenin 05.06.2024 tarihli kararı Yargıtay'ın
         yerleşik içtihadına aykırıdır» tetiklemez (bkz. `_tarih_merciye_ait`)."""
    tam_satirlar, eksik_satirlar = _satir_tamlik(metin)
    if dolu_satirlar is None:
        dolu_satirlar = set(tam_satirlar)
    else:
        dolu_satirlar = set(dolu_satirlar) - eksik_satirlar
    izler, gorulen = [], set()
    for satir_no, satir in enumerate(metin.split("\n"), start=1):
        if satir_no in dolu_satirlar or satir_no in gorulen:
            continue
        if not MERCI_RE.search(satir):
            continue
        ima = _gecerli_karar_imasi(satir)   # onarım: tarih merciye ait değilse ima yok
        if not ima:
            continue
        if KENDI_DOSYA_SATIR_RE.match(satir):
            continue
        gorulen.add(satir_no)
        alt = _eksik_alt_bicim(satir)
        if alt:
            sinif = SINIF_EKSIK_KUNYE
            sebep = (f"EKSİK KÜNYE — {alt} atıf (%r); esas+karar çifti tamamlanmalı "
                     "(Yargıtay birleşik biçimi «YYYY/N-YYYY/N» de tanınır) — "
                     "tek tarih/tek sayı ile mekanik teyit YAPILAMAZ"
                     % _sikistir(ima.group(0), 40))
        else:
            sinif = SINIF_AYRISTIRILAMAYAN
            sebep = ("merci anılıyor ve karar iması var (%r) ama künye "
                     "(esas/karar ya da başvuru numarası) ÇIKARILAMADI — "
                     "mekanik teyit YAPILAMADI" % _sikistir(ima.group(0), 40))
        izler.append({
            "satir_no": satir_no,
            "metin": _sikistir(satir),
            "sebep": sebep,
            "sinif": sinif,
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
    return _kutukten_son_token(kutuk_yolu, esas, karar, daire, _DAMGA_TOKEN_RE,
                               "kutukten_son_damga")


# ── K5 (v0.5.16, Hamle 4) — AKIBET TOKENI ────────────────────────────────────
# D grubu (`oa_hafiza.py teyit --akibet`) kütük sonuç hücresine, DAMGA=
# hücresi gibi, «AKIBET=<enum>» yazar (enum: kesinlesti | kesinlesmedi |
# bozuldu | kaldirildi | geri_cevrildi). Okuyucu burada; yazıcı D grubunda.
_AKIBET_TOKEN_RE = re.compile(r"AKIBET=([A-Za-zçğıöşüÇĞİÖŞÜ_-]+)")


def kutukten_son_akibet(kutuk_yolu, esas, karar, daire=None):
    """K5 — kütükteki bir esas/karar (+ opsiyonel daire) için SON `AKIBET=`
    tokenını döndürür (küçük harf); yoksa None. Satır eşleşme kuralı
    `kutukten_son_damga` ile BİREBİR aynıdır (tek-yazar kuralı — ortak
    `_kutukten_son_token`)."""
    sonuc = _kutukten_son_token(kutuk_yolu, esas, karar, daire, _AKIBET_TOKEN_RE,
                                "kutukten_son_akibet")
    return sonuc.lower() if sonuc else None


def _kutukten_son_token(kutuk_yolu, esas, karar, daire, token_re, etiket):
    """`kutukten_son_damga` / `kutukten_son_akibet` ortak gövdesi (v0.5.16 —
    davranış bit düzeyinde aynı; yalnız token deseni parametreleşti)."""
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
                f"UYARI (kunye_ortak.{etiket}): kütük satırı beklenen "
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
        m = token_re.search(sonuc_hucresi)
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

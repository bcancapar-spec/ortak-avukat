# -*- coding: utf-8 -*-
"""udf_md.py — UYAP `.udf` → Markdown, YAPI KORUYARAK (yerel, ağsız).

SÖZLEŞME
--------
    udf_markdown_cikar(yol) -> (markdown: str, kunye: dict)

    * ASLA istisna fırlatmaz. Hata hâlinde markdown="" ve kunye["hata"] DOLU
      döner. GEREKÇE: ingest sözleşmesinde "sessiz atlama" yasaktır — çağıran
      bir evrağın işlenemediğini künyeden GÖRMEK zorundadır; istisna fırlatan
      bir modül, üst katmanda `except: pass` ile sessizce yutulabilir.
    * Yalnız Python standart kütüphanesi. Ağ yok, alt süreç yok, npx/oturum yok.
    * Girdi dosyası SALT OKUNUR açılır (K9).

BELGE MODELİ (798 gerçek dosyada ölçülerek doğrulandı)
------------------------------------------------------
    template[@format_id]
      ├── content                → CDATA: GÖRÜNÜR METNİN TAMAMI (tek blok)
      ├── properties / styles    → biçim tanımları (metin taşımaz)
      ├── elements
      │     ├── paragraph  > (content|field|space|tab|image)*
      │     ├── table[@columnCount] > row > cell[@align] > (paragraph|table)*
      │     ├── header|footer > paragraph*
      │     └── page-break > paragraph > content
      ├── webID / data / tabLength → CDATA DIŞI UYAP alan verisi
      └── (arşivde .sgn/.p7s varsa e-imzalı nüsha)

Metin ile biçim AYRI yaşar: `elements` ağacındaki her düğüm CDATA'ya
`startOffset`/`length` ile işaret eder. Bu yüzden ham okuma metni kaybetmez
ama YAPIYI kaybeder; doğru çevirim, ağacı gezip her düğümün gösterdiği CDATA
dilimini o düğümün ANLAMIYLA (paragraf/hücre/satır) birleştirmektir.

ŞARTNAME KURALLARI (UDF-SARTNAME.md K1–K10) — bu dosyadaki karşılıkları
----------------------------------------------------------------------
    K1  offset birimi     -> sınıf Metin (çift sayım + ayrışma uyarısı)
    K2  boşluksuz döşeme  -> _kapsam_denetle (gap/overlap → uyarilar[])
    K3  ZWS ayıklama      -> _gorunur_temizle (unicodedata kategori 'Cf')
    K4  satır sonu kırpma -> _blok_birlestir
    K5  sayfa sonu        -> Cevirici.blok (page-break görünür içerik üretmez)
    K6  sekme ayracı      -> Cevirici._tabset_denetle (noktalı virgül = uyarı)
    K7  tablo             -> Cevirici.tablo (columnCount + birleşik hücre damgası)
    K8  uzantı yalanı     -> _gercek_tur (PDF/DOCX/OLE2 → gercek_tur, md üretilmez)
    K9  imzalı dokunulmaz -> yalnız "rb"; arşive HİÇBİR yazma yok
    K10 biçim işaretleri  -> _vurgu (kalın/italik/ALTI ÇİZİLİ) + sütun hizası
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler.
# GEREKÇE: bu gerçek bir arızadır, temkin değil — cp1254 U+FFFC (görsel yer
# tutucusu) ve U+200B karakterlerini kodlayamaz; guard olmadan modül sahada
# UnicodeEncodeError ile ÖLÜR.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import base64
import binascii
import hashlib
import io
import json
import os
import re
import struct
import time
import unicodedata
import zipfile
import zlib
import xml.etree.ElementTree as ET

__all__ = ["udf_markdown_cikar", "SURUM"]

SURUM = "1.0"

# ---------------------------------------------------------------------------
# Sabitler — hepsi 798 gerçek dosya üzerinde ÖLÇÜLEREK saptandı, varsayım yok.
# ---------------------------------------------------------------------------

# CDATA tek bir bloktur ve belgenin İLK CDATA'sıdır (kök `content` çocuğu).
# Ham baytlardan regex ile alınır; ET ile alınmaz, çünkü XML ayrıştırıcısı
# satır sonlarını normalize eder (\r\n → \n) ve bu, offsetleri KAYDIRIR.
CDATA_RE = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.S)
FORMAT_RE = re.compile(r'format_id="([^"]*)"')

# CDATA'ya offset ile işaret eden BEŞ etiket (ölçüm: content/field/space/tab/image).
SPAN_ETIKET = ("content", "field", "space", "tab", "image")
SPAN_KUME = frozenset(SPAN_ETIKET)

# Yapı taşıyan bloklar.
BLOK_KUME = frozenset(("paragraph", "table", "row", "cell", "header", "footer",
                       "page-break"))

# Metin taşımayan, künyeye de girmemesi gereken dallar.
ATLA_KUME = frozenset(("styles", "style", "properties", "pageFormat", "webID"))

# Swing StyleConstants hizalama kodları (ölçüm: 0/1/2/3 değerleri görüldü).
HIZA_NOTU = {"1": "<!--hiza:orta-->", "2": "<!--hiza:sag-->"}

# GFM sütun hizası. UDF'te hiza HÜCRE özniteliğidir (`cell/@align`), GFM'de
# SÜTUN özelliğidir; sütunun hizası, o sütunda hiza bildiren İLK hücreden alınır.
GFM_HIZA = {"left": ":---", "center": ":---:", "right": "---:"}

# Birleşik hücre yer tutucusu. GFM'de görünmez (HTML yorumu) ama ham Markdown'ı
# okuyan dil modeli için AÇIK bir işarettir: burası "boş hücre" değil,
# "yeri bilinmeyen birleşik hücre artığı"dır. Sessiz düzleştirme K7'de YASAK.
BIRLESIK_IM = "<!--bh-->"

# Görsel verisi: ölçüm 548/548 görselin base64 PNG olduğunu gösterdi (satır
# kaydırma boşlukları içerir).
PNG_SIHIR = b"\x89PNG\r\n\x1a\n"


# ---------------------------------------------------------------------------
# 1. KABUK — bayt düzeyi: gerçek tür tespiti (K8) ve content.xml çıkarımı
# ---------------------------------------------------------------------------

def _gercek_tur(ham):
    """İlk baytlardan GERÇEK dosya türünü söyle (K8 — uzantı yalanı).

    GEREKÇE: sahada `.udf` uzantılı ama gerçekte başka biçim olan dosyalar var.
    Bunlar bugün "hata" damgasıyla külliyat dışında kalıyor; oysa doğru
    davranış, çağıranı DOĞRU işleyiciye yönlendirmektir (ingest'te pdf_isle /
    docx_isle mevcut). Sözü olguya bağlıyoruz: karar uzantıya değil, BAYTA.
    """
    if not ham:
        return "bos", ""
    if ham[:4] == b"%PDF":
        return "pdf", "%PDF imzası"
    # OLE2 bileşik belge (eski .doc/.xls/.ppt).
    if ham[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return "ole2", "OLE2 bileşik belge imzası"
    if ham[:5] == b"{\\rtf":
        return "rtf", "RTF imzası"
    if ham[:2] == b"PK":
        # ZIP ailesi: içerik listesine bakmadan karar verilemez.
        adlar = _zip_adlari(ham)
        dus = [a.lower() for a in adlar]
        if any(a.endswith("content.xml") for a in dus):
            # UDF de OpenDocument de content.xml taşır; ODF'i mimetype ayırır.
            if any(a == "mimetype" for a in dus) and \
               any(a.startswith("meta-inf/") for a in dus):
                return "odf", "ODF (mimetype + META-INF)"
            return "udf", ""
        if any(a.startswith("word/") for a in dus):
            return "docx", "word/ dizini"
        if any(a.startswith("xl/") for a in dus):
            return "xlsx", "xl/ dizini"
        if any(a.startswith("ppt/") for a in dus):
            return "pptx", "ppt/ dizini"
        if not adlar:
            # ZIP başlıyor ama dizin okunamıyor: bozuk arşiv olabilir; ham
            # kurtarma denemesi ileride yapılır, burada "udf" varsayılır.
            return "udf", "ZIP dizini okunamadı"
        return "zip", ",".join(adlar[:4])
    bas = ham.lstrip()[:200]
    if bas[:5] == b"<?xml" or bas[:9] == b"<template":
        return "udf", "çıplak XML"
    return "bilinmeyen", repr(ham[:4])


def _zip_adlari(ham):
    """ZIP dizinindeki adlar; bozuk arşivde ham tarama ile isim toplar."""
    try:
        with zipfile.ZipFile(io.BytesIO(ham)) as z:
            return z.namelist()
    except Exception:
        return [a for a, _ in _zip_ham_tara(ham, yalniz_ad=True)]


def _zip_ham_tara(ham, yalniz_ad=False, hedef_son=None):
    """ZIP yerel başlıklarını ELDEN tarayıp girdileri çöz (CRC DOĞRULAMADAN).

    GEREKÇE (ölçüm): külliyatta CRC'si bozuk 1 arşiv var; `zipfile` onu tümden
    reddediyor, oysa sıkıştırılmış akış SAĞLAM (42.895/42.895 bayt kurtarıldı).
    Bir evrağın CRC alanı bozuk diye külliyat dışında kalması, avukatın dosyanın
    bir parçasını hiç görmemesi demektir. Kurtarılan içerik künyeye AÇIK
    uyarıyla damgalanır — "kurtarıldı" ile "doğrulandı" aynı şey değildir.

    ZIP yerel başlığı (biçim kuralı; olgu):
        0..3  PK\\x03\\x04 | 4..5 sürüm | 6..7 bayrak | 8..9 yöntem
        10..13 zaman/tarih | 14..17 CRC | 18..21 sıkışık boy
        22..25 açık boy | 26..27 ad boyu | 28..29 ek alan boyu | 30.. ad
    """
    out = []
    i = 0
    n = len(ham)
    while True:
        i = ham.find(b"PK\x03\x04", i)
        if i < 0 or i + 30 > n:
            break
        try:
            bayrak, yontem = struct.unpack_from("<HH", ham, i + 6)
            sikisik, _acik, ad_boy, ek_boy = struct.unpack_from("<IIHH", ham, i + 18)
        except struct.error:
            break
        bas = i + 30
        ad_b = ham[bas:bas + ad_boy]
        try:
            ad = ad_b.decode("utf-8" if (bayrak & 0x800) else "cp437", "replace")
        except Exception:
            ad = repr(ad_b)
        veri_bas = bas + ad_boy + ek_boy
        if yalniz_ad:
            out.append((ad, b""))
            i = veri_bas or (i + 4)
            continue
        if hedef_son and not ad.lower().endswith(hedef_son):
            i = veri_bas + (sikisik or 1)
            continue
        blok = ham[veri_bas:veri_bas + sikisik] if sikisik else ham[veri_bas:]
        try:
            if yontem == 0:
                icerik = blok
            elif yontem == 8:
                d = zlib.decompressobj(-15)  # ham deflate (ZIP gövdesi)
                icerik = d.decompress(blok) + d.flush()
            else:
                i = veri_bas + (sikisik or 1)
                continue
        except zlib.error:
            i = veri_bas + (sikisik or 1)
            continue
        out.append((ad, icerik))
        i = veri_bas + (sikisik or max(len(blok), 1))
    return out


def _kabuk_ac(ham):
    """`.udf` baytları → (content_xml_baytlari, imzali, kabuk_adi, uyarilar).

    K9: dosya yalnız OKUNUR; arşiv hiçbir koşulda yeniden paketlenmez.
    """
    uyarilar = []
    if ham[:2] == b"PK":
        try:
            with zipfile.ZipFile(io.BytesIO(ham)) as z:
                adlar = z.namelist()
                hedef = next((a for a in adlar
                              if a.lower().endswith("content.xml")), None)
                if hedef is None:
                    raise _Cikamadi("content_xml_yok", ",".join(adlar[:5]))
                imzali = any(a.lower().endswith((".sgn", ".p7s")) for a in adlar)
                return z.read(hedef), imzali, "zip", uyarilar
        except _Cikamadi:
            raise
        except Exception as e:
            # BadZipFile / CRC hatası: ham kurtarmayı DENE, ama damgala.
            kurtarilan = _zip_ham_tara(ham, hedef_son="content.xml")
            if kurtarilan:
                adlar = [a for a, _ in _zip_ham_tara(ham, yalniz_ad=True)]
                imzali = any(a.lower().endswith((".sgn", ".p7s")) for a in adlar)
                uyarilar.append(
                    "K8/arşiv: ZIP dizini bozuk (%s) — içerik ham deflate ile "
                    "KURTARILDI, CRC DOĞRULANMADI" % str(e)[:60])
                return kurtarilan[0][1], imzali, "zip(crc-atlandi)", uyarilar
            raise _Cikamadi("bozuk_zip", str(e)[:80])
    bas = ham.lstrip()[:200]
    if bas[:5] == b"<?xml" or bas[:9] == b"<template":
        # Ölçüm: 8 dosya ZIP değil, ÇIPLAK XML. Bunlar geçerli UDF içeriğidir.
        return ham, False, "ciplak_xml", uyarilar
    raise _Cikamadi("zip_degil", repr(ham[:4]))


class _Cikamadi(Exception):
    """İç sinyal — DIŞARI SIZMAZ; udf_markdown_cikar bunu künyeye çevirir."""

    def __init__(self, tur, ayrinti=""):
        super().__init__(tur)
        self.tur = tur
        self.ayrinti = ayrinti


def _xml_ayristir(xml_baytlari):
    """content.xml baytları → (kok, cdata, format_id, xml_hatasi).

    XML bozuk AMA CDATA okunabiliyorsa `kok=None` döner ve çağıran DÜZ METİN
    kurtarmasına geçer. GEREKÇE (ölçüm): külliyatta 1 dosyanın XML'i gerçekten
    bozuk (satır 632) — ama görünür metni sapasağlam. Mevcut ham ingest hattı
    bu dosyadan metin ÇIKARIYOR; yapı kuramadık diye dosyayı tümden reddetmek
    avukat açısından bir GERİLEME olurdu. Bozulma açıkça damgalanır.
    """
    # İmzalı nüshalarda prolog öncesi BOM/boşluk görülür — ET bunu reddeder.
    b = xml_baytlari.lstrip(b"\xef\xbb\xbf").lstrip()
    metin = b.decode("utf-8", errors="replace")
    m = CDATA_RE.search(metin)
    mf = FORMAT_RE.search(metin[:4000])
    fmt_regex = mf.group(1) if mf else "?"
    try:
        kok = ET.fromstring(b)
    except ET.ParseError as e:
        if m and m.group(1).strip():
            return None, m.group(1), fmt_regex, str(e)[:80]
        raise _Cikamadi("xml_bozuk", str(e)[:80])
    if m:
        cdata = m.group(1)
    else:
        # CDATA'sız yazılmış nüsha: kök `content` düğümünün düz metnini kullan.
        dugum = kok.find("content")
        cdata = (dugum.text or "") if dugum is not None else ""
    return kok, cdata, kok.attrib.get("format_id") or fmt_regex, ""


# ---------------------------------------------------------------------------
# 2. METİN — offset birimi (K1) ve dilimleme
# ---------------------------------------------------------------------------

class Metin:
    """CDATA üzerinde offset dilimleyici; K1'in ÇİFT SAYIMINI yapar.

    K1'de bir ÇELİŞKİ vardır: kendi belgemiz offsetlerin UTF-16 kod birimi
    olduğunu söyler, incelenen başka bir uygulama codepoint sayar. Türkçe hukuk
    metni tamamen BMP içinde kaldığı için ikisi AYNI sonucu verir; fark yalnız
    BMP-dışı karakterde (emoji) doğar. Bu sınıf iki sayımı da yapar, ayrışırsa
    UTF-16'yı seçer (kendi belgemiz esastır) ve ayrışmayı UYARIYA bağlar.

    DÜRÜST KAYIT: 798 gerçek dosyada BMP-dışı karakter SIFIRDIR; yani hangi
    sayımın doğru olduğu bu külliyatla KANITLANAMAZ — yalnız "fark yok"
    kanıtlanmıştır. Uyarı, ayırt edici bir dosya geldiği gün susmasın diye var.
    """

    def __init__(self, cdata):
        self.s = cdata
        self.bmp_disi = sum(1 for ch in cdata if ord(ch) > 0xFFFF)
        self.ayrisma = 0   # UTF-16 ve codepoint dilimlerinin farklı çıktığı span
        self.tasma = 0     # CDATA sınırını aşan offset
        if self.bmp_disi:
            # UTF-16 kod birimi indeksi -> Python kod noktası indeksi haritası.
            h = []
            for i, ch in enumerate(cdata):
                h.append(i)
                if ord(ch) > 0xFFFF:
                    h.append(i)  # vekil çifti iki kod birimi, tek kod noktası
            h.append(len(cdata))
            self.harita = h
            self.birim = len(h) - 1
        else:
            self.harita = None
            self.birim = len(cdata)

    def dilim(self, bas, boy):
        """[bas, bas+boy) aralığındaki metni döndür; taşmayı sayaca yaz."""
        if bas < 0 or boy < 0 or bas + boy > self.birim:
            # SESSİZ KIRPMA YASAK: kırpıyoruz ama sayaca yazıyoruz, çünkü
            # sessiz kırpma bozuk dosyada görünmez metin kaybı üretir (P2/12).
            self.tasma += 1
        if self.harita is None:
            return self.s[max(bas, 0):max(bas, 0) + max(boy, 0)]
        a = self.harita[min(max(bas, 0), self.birim)]
        b = self.harita[min(max(bas + boy, 0), self.birim)]
        u16 = self.s[a:b]
        kp = self.s[max(bas, 0):max(bas, 0) + max(boy, 0)]  # codepoint sayımı
        if u16 != kp:
            self.ayrisma += 1
        return u16


# ---------------------------------------------------------------------------
# 3. GÖRÜNÜRLÜK — K3 (ZWS ve diğer görünmez biçim karakterleri)
# ---------------------------------------------------------------------------

def _gorunmez_mi(ch):
    """Unicode 'Cf' (format) kategorisi = glif üretmeyen karakter.

    Ölçüm: CDATA'da U+200B (ZWS, 325 kez) ve U+FEFF (1 kez) bulundu. Kuralı
    tek karaktere değil KATEGORİYE bağlamak, ileride ZWNJ/ZWJ/LRM gibi
    akrabaların sızmasını da kapatır. U+F040 gibi ÖZEL KULLANIM (Co) karakteri
    silinmez — o, sembol yazı tipinde GÖRÜNÜR bir gliftir.
    """
    return unicodedata.category(ch) == "Cf"


# Unicode 'Cf' kategorisinin TAM aralık listesi. Karakter karakter
# `unicodedata.category` çağırmak 6,4 milyon karakterde ölçülebilir yavaşlıktır;
# bu regex aynı kümeyi C hızında tarar. ÖLÇÜT hâlâ `unicodedata`dır: süitteki
# `test_cf_regexi_unicodedata_ile_birebir` bu iki tanımın tüm kod noktası
# uzayında AYNI kümeyi verdiğini doğrular — uyuşmazsa test kırılır.
_CF_RE = re.compile(
    "[­؀-؅؜۝܏࢐-࢑࣢᠎"
    "​-‏‪-‮⁠-⁤⁦-⁯﻿￹-￻"
    "\U000110bd\U000110cd\U00013430-\U0001343f\U0001bca0-\U0001bca3"
    "\U0001d173-\U0001d17a\U000e0001\U000e0020-\U000e007f]")


def _gorunur_temizle(s):
    """K3 — görünmez biçim karakterlerini çıktıdan ayıkla."""
    if not s or s.isascii():
        # Sık yol: ASCII metinde U+00AD dışında Cf yoktur, U+00AD de ASCII
        # değildir — yani ASCII dizide temizlenecek hiçbir şey yoktur.
        return s
    return _CF_RE.sub("", s)


_BOSLUK_RE = re.compile(r"\s+")


def _olcum_metni(s):
    """Kayıp ölçümü için normalleştirilmiş 'görünür metin'.

    Boşluk ATILIR: hücre içi `\\n` → boşluk/`<br>` dönüşümü tasarım gereğidir,
    bu yüzden karakteri karakterine boşluk sadakati YOKTUR ve olamaz. Dürüst
    ifade: "görünür metnin tamamı, sırası bozulmadan korunur".
    """
    return _BOSLUK_RE.sub("", _CF_RE.sub("", s))


# ---------------------------------------------------------------------------
# 4. ÇEVİRİCİ
# ---------------------------------------------------------------------------

class Cevirici:
    """`elements` ağacını gezip Markdown üretir; bütün sayaç ve uyarıları tutar."""

    def __init__(self, kok, T, secenek):
        self.kok = kok
        self.T = T
        self.sec = secenek
        self.uyarilar = []
        self.sayac = dict(paragraf=0, tablo=0, satir=0, hucre=0, gorsel=0,
                          alan=0, tab=0, ic_ice_tablo=0, ustbilgi_altbilgi=0,
                          liste_ogesi=0, birlesik_hucre_satiri=0,
                          sayfa_sonu=0, veri_dugumu=0)
        self.alanlar = []          # (fieldName, değer)
        self.tablo_bicimi = []     # GFM tablosu olarak basılanlar (satır, sütun)
        self.ic_ice_bicimi = []    # satır içi sıkıştırılan iç tablolar
        self.kapsam = bytearray(len(T.s))
        self.cakisma = 0
        self.gorseller = []        # (sıra, png_baytları)
        self._ic_tablolar = []     # ertelenmiş iç içe tablolar
        self._ic_sira = 0
        self._liste_sayac = {}
        self._tabset_uyarildi = False

    # -- span düzeyi ------------------------------------------------------

    def _isaretle(self, bas, boy):
        """K2 kapsam defteri: hangi CDATA karakteri hangi yapıya bağlandı.

        Dilim üzerinden çalışır (C hızında): karakter karakter dönmek 6,4 milyon
        karakterlik külliyatta ölçülebilir yavaşlıktır. Çakışma önce ucuz bir
        `count` ile aranır; ancak varsa ayrıntılı sayıma inilir.
        """
        a = max(bas, 0)
        b = min(bas + boy, len(self.kapsam))
        if b <= a:
            return
        parca = self.kapsam[a:b]
        n = parca.count(1)
        if n:
            self.cakisma += n
        self.kapsam[a:b] = b"\x01" * (b - a)

    def _tabset_denetle(self, e):
        """K6 — sekme durağı ayracı VİRGÜL olmalıdır.

        Okuma tarafını bağlamaz ama noktalı virgül, dosyanın bozuk bir yazıcıdan
        çıktığının işaretidir (UYAP editörü böyle dosyayı SESSİZCE açmaz).
        Ölçüm: 3.135 virgüllü TabSet, 0 noktalı virgül — kural sahada doğrulandı.
        """
        if self._tabset_uyarildi:
            return
        v = e.attrib.get("TabSet")
        if v and ";" in v:
            self._tabset_uyarildi = True
            self.uyarilar.append(
                "K6/sekme: TabSet ayracı NOKTALI VİRGÜL — dosya bozuk bir "
                "yazıcıdan çıkmış olabilir (beklenen ayraç: virgül)")

    def _spanlar(self, dugum):
        """Düğümün altındaki tüm offsetli span'ler, offset sırasında."""
        out = []
        for e in dugum.iter():
            if e.tag in SPAN_KUME and "startOffset" in e.attrib:
                try:
                    bas = int(e.attrib["startOffset"])
                    boy = int(e.attrib.get("length", "0"))
                except ValueError:
                    continue
                out.append((bas, boy, e))
        out.sort(key=lambda t: (t[0], t[1]))
        return out

    def _vurgu(self, govde, kalin, italik, alti):
        """K10 — kalın/italik/ALTI ÇİZİLİ işaretleri Markdown'a çevir.

        Altı çizili, hukuk metninde VURGUDUR (ölçüm: 1.487 örnek / 270 dosya);
        atılması anlam kaybıdır. GFM'de altı çizme imi yoktur; sadık taşıyıcı
        HTML `<u>` etiketidir (Markdown içinde geçerlidir ve geri döndürülebilir).
        Baştaki/sondaki boşluk imin DIŞINDA bırakılır — aksi hâlde `** metin **`
        gibi işlemeyen im üretilir.
        """
        if not govde.strip():
            return govde
        on = govde[:len(govde) - len(govde.lstrip())]
        arka = govde[len(govde.rstrip()):]
        orta = govde.strip()
        if kalin:
            orta = "**" + orta + "**"
        if italik:
            orta = "*" + orta + "*"
        if alti:
            orta = "<u>" + orta + "</u>"
        return on + orta + arka

    def _span_metni(self, spanlar):
        """Bitişik ve AYNI biçimli span'leri birleştirerek işaretli metin üret.

        Birleştirme şart: aksi hâlde her karakter ayrı `**` ile sarılır ve
        Markdown hem şişer hem bozulur.
        """
        parcalar = []
        tampon, mevcut = "", None
        for bas, boy, e in spanlar:
            self._tabset_denetle(e)
            ham = self.T.dilim(bas, boy)
            self._isaretle(bas, boy)
            if e.tag == "image":
                if tampon:
                    parcalar.append(self._vurgu(tampon, *mevcut))
                    tampon, mevcut = "", None
                parcalar.append(self._gorsel(e, ham))
                continue
            metin = _gorunur_temizle(ham)   # K3
            if not metin:
                continue
            if e.tag == "tab":
                self.sayac["tab"] += 1
            if e.tag == "field":
                self.sayac["alan"] += 1
                ad = e.attrib.get("fieldName")
                if ad:
                    self.alanlar.append((ad, metin.strip()))
            anahtar = (e.attrib.get("bold") == "true",
                       e.attrib.get("italic") == "true",
                       e.attrib.get("underline") == "true")
            if mevcut is None or anahtar == mevcut:
                tampon += metin
                mevcut = anahtar
            else:
                parcalar.append(self._vurgu(tampon, *mevcut))
                tampon, mevcut = metin, anahtar
        if tampon:
            parcalar.append(self._vurgu(tampon, *mevcut))
        return "".join(parcalar)

    def _gorsel(self, e, ham_dilim):
        """Görsel yer tutucusu; istenirse PNG diske çıkarılır.

        Mühür, ıslak imza ve ekran görüntüsü DELİLDİR. Ölçüm: 548 görselin
        548'i base64 PNG. Varsayılan davranış yalnız yer tutucudur (ingest'in
        metin sözleşmesi bozulmasın); `gorsel_dizin` verilirse dosyaya yazılır.
        CDATA'daki yer tutucu karakter (ölçüm: 543× U+00B8, 5× U+FFFC) çıktıya
        AYNEN eklenir — aksi hâlde kayıpsızlık ölçümü haklı olarak kayıp sayar.
        """
        self.sayac["gorsel"] += 1
        sira = self.sayac["gorsel"]
        en = e.attrib.get("width", "?")
        boy = e.attrib.get("height", "?")
        veri = e.attrib.get("imageData")
        bag = "#gorsel"
        if veri and self.sec.get("gorsel_dizin"):
            png = self._png_coz(veri)
            if png:
                self.gorseller.append((sira, png))
                bag = "gorsel-%03d.png" % sira
        return "![gorsel-%d %sx%s](%s)%s" % (sira, en, boy, bag, ham_dilim)

    @staticmethod
    def _png_coz(veri):
        try:
            ham = base64.b64decode(re.sub(r"\s+", "", veri), validate=False)
        except (binascii.Error, ValueError):
            return None
        return ham if ham[:8] == PNG_SIHIR else ham or None

    # -- paragraf ---------------------------------------------------------

    def _liste_oneki(self, p):
        """K10 komşusu — madde/numara imlerini geri kur (P1).

        Ölçüm: `Bulleted=true` 260 paragraf, `Numbered=true` 787 paragraf,
        `ListLevel` 0/1. Dilekçede "1., 2., 3." talep sırası HUKUKEN anlamlıdır;
        düz paragrafa çökerse model talepleri sayamaz.
        """
        try:
            duzey = int(p.attrib.get("ListLevel", "0"))
        except ValueError:
            duzey = 0
        duzey = max(0, min(duzey, 6))
        girinti = "  " * duzey
        if p.attrib.get("Bulleted") == "true":
            self.sayac["liste_ogesi"] += 1
            return girinti + "- "
        if p.attrib.get("Numbered") == "true":
            self.sayac["liste_ogesi"] += 1
            kimlik = p.attrib.get("ListId", "")
            anahtar = (kimlik, duzey)
            n = self._liste_sayac.get(anahtar, 0) + 1
            self._liste_sayac[anahtar] = n
            # Alt düzeyler yeniden başlar (yeni bir üst madde açıldı).
            for k in list(self._liste_sayac):
                if k[0] == kimlik and k[1] > duzey:
                    del self._liste_sayac[k]
            return "%s%d. " % (girinti, n)
        return None

    def paragraf(self, p, hiza_notu=True):
        self.sayac["paragraf"] += 1
        govde = self._span_metni(self._spanlar(p))
        onek = self._liste_oneki(p)
        if not govde.strip():
            # K3/K4: boş paragraf (ZWS + \n) çıktıya SAHTE boş satır bırakmaz.
            return ""
        if onek is None:
            # Liste dışı dolu paragraf listeyi kırar → sayaçları sıfırla.
            self._liste_sayac.clear()
        govde = govde.strip()
        if hiza_notu:
            not_ = HIZA_NOTU.get(p.attrib.get("Alignment"))
            if not_:
                govde = not_ + govde
        return (onek + govde) if onek else govde

    # -- tablo ------------------------------------------------------------

    def hucre(self, c):
        """Bir hücrenin Markdown metni; iç içe tablolar ERTELENİR."""
        parcalar = []
        for ch in c:
            if ch.tag == "paragraph":
                t = self.paragraf(ch, hiza_notu=False)
                if t:
                    parcalar.append(t)
            elif ch.tag == "table":
                # K7 — İÇ İÇE TABLO. Ölçüm: 424 iç içe tablo, derinlik 4'e kadar.
                # GFM'de tablo İÇ İÇE GEÇMEZ; iki seçenek vardır ve ikisi de
                # bir şey feda eder:
                #   satir-ici (VARSAYILAN): tablo hücrenin İÇİNDE, geometrisi
                #     BİLDİRİLEREK sıkıştırılır. Okuma SIRASI korunur.
                #   ayri: iç tablo ayrı GFM tablosu olur, hücrede atıf kalır.
                #     Yapı tam korunur ama metin ebeveyninden SONRAYA kayar.
                # Varsayılan "satir-ici"dir; çünkü şartnamenin başarı ölçütü
                # (madde 1 ve 5) SIRALI kayıpsızlıktır ve ölçüm gösterdi ki
                # "ayri" kipi 169 dosyada 50.678 karakteri YERİNDEN OYNATIYOR
                # (hiçbiri yok olmuyor — ama sıra bozuluyor).
                self.sayac["ic_ice_tablo"] += 1
                if self.sec.get("ic_ice") == "ayri":
                    self._ic_sira += 1
                    etiket = "iç-tablo-%d" % self._ic_sira
                    # Kuyrukta YER AYIR, sonra doldur: iç-içe-içe tablolarda
                    # tamamlanma sırası BELGE sırasının TERSİDİR.
                    sira = len(self._ic_tablolar)
                    self._ic_tablolar.append((etiket, ""))
                    self._ic_tablolar[sira] = (etiket,
                                               self.tablo(ch, etiket=etiket))
                    parcalar.append("[%s]" % etiket)
                else:
                    parcalar.append(self._ic_tablo_satirici(ch))
            elif ch.tag == "page-break":
                self.sayfa_sonu(ch)          # K5 — hücre içinde de görülebilir
            else:
                sp = self._spanlar(ch)
                if sp:
                    t = self._span_metni(sp)
                    if t.strip():
                        parcalar.append(t)
        metin = "<br>".join(x for x in parcalar if x)
        # GFM hücre kaçışları: boru işareti sütunu böler, satır sonu satırı.
        return metin.replace("|", "\\|").replace("\n", " ").strip()

    def _tablo_izgarasi(self, t):
        """Tablonun hücre ızgarasını kur; (veri, sutun, eksik_satir, fazla_satir).

        Sütun sayısı: BİLDİRİLEN `columnCount` ile GÖRÜLEN hücre sayısının
        BÜYÜĞÜ. GEREKÇE (ölçüm): 40 tabloda MD genişliği columnCount'tan
        DARDI — yalnız görülen hücreye bakmak sütun DÜŞÜRÜR.
        """
        veri = []
        for rw in t.findall("row"):
            hucreler = rw.findall("cell")
            if not hucreler:
                continue
            veri.append([self.hucre(c) for c in hucreler])
        if not veri:
            return None, 0, 0, 0
        try:
            bildirilen = int(t.attrib.get("columnCount", "0"))
        except ValueError:
            bildirilen = 0
        sutun = max(bildirilen, max(len(r) for r in veri))
        eksik = sum(1 for r in veri if len(r) < sutun)
        fazla = sum(1 for r in veri if len(r) > sutun)
        if eksik:
            self.sayac["birlesik_hucre_satiri"] += eksik
            self.uyarilar.append(
                "K7/birleşik-hücre: %d satırda hücre sayısı bildirilen sütun "
                "sayısından (%d) az — konum bilinmiyor, damgalandı"
                % (eksik, sutun))
        if fazla:
            self.uyarilar.append(
                "K7/tablo: %d satırda hücre sayısı columnCount'u AŞIYOR" % fazla)
        veri = [r[:sutun] + [BIRLESIK_IM] * (sutun - len(r)) for r in veri]
        self.sayac["satir"] += len(veri)
        self.sayac["hucre"] += sum(len(r) for r in veri)
        return veri, sutun, eksik, fazla

    def _ic_tablo_satirici(self, t):
        """İç içe tabloyu SIRA BOZMADAN, geometrisi BİLDİRİLEREK sıkıştır.

        Biçim: `{tablo RxC: [h1 / h2] [h3 / h4]}`. Satır/sütun sayısı AÇIKÇA
        yazılır — prototipin `{ a / b ; c / d }` biçiminde geometri kayıptı ve
        aşağı akış tablonun kaç sütunlu olduğunu bilemiyordu.
        """
        veri, sutun, _e, _f = self._tablo_izgarasi(t)
        if veri is None:
            sp = self._spanlar(t)
            return self._span_metni(sp) if sp else ""
        self.ic_ice_bicimi.append((len(veri), sutun))
        govde = " ".join("[" + " / ".join(r) + "]" for r in veri)
        return "{tablo %dx%d: %s}" % (len(veri), sutun, govde)

    def _sutun_hizalari(self, satirlar_xml, sutun):
        """K10 — sütun hizası: o sütunda hiza bildiren İLK hücreden alınır."""
        hiza = ["---"] * sutun
        for rw in satirlar_xml:
            for i, c in enumerate(rw.findall("cell")):
                if i >= sutun:
                    break
                a = c.attrib.get("align")
                if a and hiza[i] == "---":
                    hiza[i] = GFM_HIZA.get(a.lower(), "---")
        return hiza

    def tablo(self, t, etiket=None):
        """K7 — tablonun kalbi. Sessiz düzleştirme YASAK."""
        satirlar_xml = t.findall("row")
        # Biçim defterinde YER AYIR: iç içe tablolar hücre çizilirken kurulur ve
        # ebeveynden ÖNCE biterdi; yer ayırmadan defterin sırası MD'nin sırasına
        # uymaz, kıyas ölçümü de sahte uyuşmazlık üretirdi.
        yer = len(self.tablo_bicimi)
        self.tablo_bicimi.append(None)
        veri, sutun, eksik_satir, fazla_satir = self._tablo_izgarasi(t)
        if veri is None:
            # Satırsız tablo: metni varsa düz akış olarak kurtarılır.
            del self.tablo_bicimi[yer]
            sp = self._spanlar(t)
            return self._span_metni(sp) if sp else ""

        notlar = []
        if eksik_satir:
            # K7'nin AÇIK yasağı: birleşik hücreyi sessizce sağa doldurma.
            # Birleşmenin YERİ XML'de yazmıyor (row/@columnSpans ölçüldü:
            # birleşme haritası DEĞİL, sütun GENİŞLİĞİ). Bu yüzden hücreler
            # soldan yazılır, eksik yerler AÇIK damgayla doldurulur ve tablonun
            # üstüne uyarı konur — değer yanlış sütuna kaymış OLABİLİR.
            notlar.append(
                "<!--tablo-uyari: %d sütun bildirildi; %d satırda hücre EKSİK "
                "(birleşik hücre). Birleşmenin YERİ dosyada yazmıyor; hücreler "
                "SOLDAN yazıldı, eksik yerlere %s kondu — değer yanlış sütunda "
                "olabilir.-->" % (sutun, eksik_satir, BIRLESIK_IM))
        if fazla_satir:
            notlar.append("<!--tablo-uyari: %d satırda bildirilen sütundan FAZLA "
                          "hücre var-->" % fazla_satir)
        if t.attrib.get("rowSpans"):
            # Ölçüm: 3 tabloda görüldü, değerleri tekil sayı (457/485) —
            # satır birleştirme haritası DEĞİL. Yorumlamıyoruz; söylüyoruz.
            notlar.append("<!--tablo-uyari: rowSpans özniteliği var ama "
                          "yorumlanamadı (satır birleşmesi kaybolmuş olabilir)-->")
            self.uyarilar.append("K7/rowSpans: yorumlanamayan satır birleşme bilgisi")

        self.sayac["tablo"] += 1
        self.tablo_bicimi[yer] = (len(veri), sutun)

        hiza = self._sutun_hizalari(satirlar_xml, sutun)
        if len(veri) == 1:
            # UDF'te "başlık satırı" kavramı YOKTUR; GFM bir başlık satırı
            # DAYATIR. Tek satırlı tabloda o satır aslında VERİDİR — aşağı
            # akışta başlık sanılmasın diye açıkça işaretlenir.
            notlar.append("<!--tablo:tek-satir (1. satır başlık DEĞİL, veridir)-->")
        if etiket:
            notlar.insert(0, "<!--%s-->" % etiket)

        satirlar = ["| " + " | ".join(veri[0]) + " |",
                    "|" + "|".join(" %s " % h for h in hiza) + "|"]
        for r in veri[1:]:
            satirlar.append("| " + " | ".join(r) + " |")
        return "\n".join(notlar + satirlar)

    # -- sayfa sonu / üst-alt bilgi ---------------------------------------

    def sayfa_sonu(self, e):
        """K5 — sayfa sonu GÖRÜNÜR içerik üretmez.

        İçindeki tek boş paragraf (ZWS + `\\n`) çıktıya SIZMAMALIDIR. Ama
        span'leri kapsam defterine işlenir; aksi hâlde K2 denetimi bu
        karakterleri haksız yere "hiçbir yapıya bağlı değil" sayar.
        """
        self.sayac["sayfa_sonu"] += 1
        for bas, boy, _ in self._spanlar(e):
            self.T.dilim(bas, boy)
            self._isaretle(bas, boy)
        return "<!--sayfa-sonu-->"

    def ust_alt(self, e):
        self.sayac["ustbilgi_altbilgi"] += 1
        ic = []
        for ch in e:
            if ch.tag == "paragraph":
                t = self.paragraf(ch, hiza_notu=False)
                if t:
                    ic.append(t)
            else:
                sp = self._spanlar(ch)
                if sp:
                    t = self._span_metni(sp)
                    if t.strip():
                        ic.append(t.strip())
        if not ic:
            return ""
        etiket = "ÜSTBİLGİ" if e.tag == "header" else "ALTBİLGİ"
        return "> **[%s]** %s" % (etiket, " ".join(ic))

    # -- gövde ------------------------------------------------------------

    def govde(self):
        bloklar = []
        gorulen = set()
        for el in self.kok.findall("elements"):
            bloklar.extend(self._kap(el))
            for _, _, e in self._spanlar(el):
                gorulen.add(id(e))
        # `elements` dışında kalmış offsetli span (yetim): metni kaybolmasın.
        yetim = [(a, b, e) for a, b, e in self._spanlar(self.kok)
                 if id(e) not in gorulen]
        if yetim:
            self.uyarilar.append(
                "yapı: %d span `elements` ağacı DIŞINDA — metni kurtarıldı ama "
                "yapısı bilinmiyor" % len(yetim))
            bloklar.append(self._span_metni(yetim))
        return bloklar

    def _kap(self, kap):
        out = []
        for ch in kap:
            if ch.tag == "paragraph":
                out.append(self.paragraf(ch, self.sec.get("hiza_notu", True)))
            elif ch.tag == "table":
                self._ic_tablolar = []
                out.append(self.tablo(ch))
                # Ertelenmiş iç içe tablolar üst tablonun HEMEN ardına gelir.
                for _, govde in self._ic_tablolar:
                    if govde.strip():
                        out.append(govde)
                self._ic_tablolar = []
            elif ch.tag in ("header", "footer"):
                out.append(self.ust_alt(ch))
            elif ch.tag == "page-break":
                out.append(self.sayfa_sonu(ch))
            elif ch.tag in ATLA_KUME:
                continue
            elif ch.tag in SPAN_KUME and "startOffset" in ch.attrib:
                try:
                    out.append(self._span_metni(
                        [(int(ch.attrib["startOffset"]),
                          int(ch.attrib.get("length", "0")), ch)]))
                except ValueError:
                    continue
            else:
                sp = self._spanlar(ch)
                if sp:
                    out.append(self._span_metni(sp))
        return out

    # -- CDATA dışı UYAP verisi ------------------------------------------

    def veri_hasadi(self):
        """CDATA'da GÖRÜNMEYEN UYAP alan verisi (`data`, `Sabit`, ...).

        Ham okumada bu bilgi %100 kaybolur; oysa dosya no, taraf, tutar gibi
        künye bilgileri burada durur.
        """
        kayitlar = []

        def gez(e, yol):
            offsetli = "startOffset" in e.attrib
            metin = (e.text or "").strip()
            if not offsetli and metin and e.tag not in ATLA_KUME:
                kayitlar.append((".".join(yol + [e.tag]), " ".join(metin.split())))
            for c in e:
                gez(c, yol + [e.tag])

        for ch in self.kok:
            if ch.tag in ("content", "elements", "styles", "properties"):
                continue
            gez(ch, [])
        for el in self.kok.findall("elements"):
            for c in el:
                if c.tag not in BLOK_KUME and c.tag not in SPAN_KUME:
                    gez(c, ["elements"])
        self.sayac["veri_dugumu"] = len(kayitlar)
        return kayitlar

    # -- K2 denetimi ------------------------------------------------------

    def kapsam_denetle(self):
        """K2 — gap/overlap denetimi. Sessiz geçmek YASAK.

        Boşluk (gap), metnin bir kısmının HİÇBİR yapıya bağlanmadığı demektir.
        Ölçüm: 604 dosyada 1.151 karakter boşluk çıktı, 1.150'si `\\n` — yani
        satır sonu. Görünür bir karakter boşlukta kalıyorsa bu GERÇEK bir
        kayıptır ve künyeye damgalanır.
        """
        bosluk_sonu = 0
        bosluk_gorunur = 0
        s = self.T.s
        # YALNIZ kapsanmayan konumları gez (ölçüm: külliyat genelinde 1.151
        # karakter) — tüm CDATA'yı Python döngüsüyle taramak gereksizdir.
        i = self.kapsam.find(0)
        while i >= 0:
            ch = s[i] if i < len(s) else " "
            if ch.isspace() or _gorunmez_mi(ch):
                bosluk_sonu += 1
            else:
                bosluk_gorunur += 1
            i = self.kapsam.find(0, i + 1)
        if self.cakisma:
            self.uyarilar.append(
                "K2/çakışma: %d karakter BİRDEN FAZLA yapıya bağlı — metin "
                "tekrarlanmış olabilir" % self.cakisma)
        if bosluk_gorunur:
            self.uyarilar.append(
                "K2/boşluk: %d GÖRÜNÜR karakter hiçbir yapıya bağlı değil "
                "(offset döşemesi boşluksuz değil)" % bosluk_gorunur)
        if self.T.tasma:
            self.uyarilar.append(
                "offset/taşma: %d span CDATA sınırını aşıyor — kırpıldı, "
                "dosya bozuk olabilir" % self.T.tasma)
        if self.T.bmp_disi:
            self.uyarilar.append(
                "K1/BMP-dışı: %d karakter BMP dışında — offset biriminin "
                "(UTF-16 mi codepoint mi) AYRIMI bu dosyada ANLAMLI"
                % self.T.bmp_disi)
        if self.T.ayrisma:
            self.uyarilar.append(
                "K1/ayrışma: %d span'de UTF-16 ve codepoint sayımları FARKLI "
                "sonuç verdi; UTF-16 seçildi — bu span'ler şüphelidir"
                % self.T.ayrisma)
        return bosluk_sonu, bosluk_gorunur


# ---------------------------------------------------------------------------
# 5. K4 — blok birleştirme (sahte boş satır birikmesin)
# ---------------------------------------------------------------------------

_UC_SATIR_RE = re.compile(r"\n{3,}")
_SATIR_SONU_BOSLUK_RE = re.compile(r"[ \t]+\n")


def _blok_birlestir(bloklar):
    """K4 — blok sonu boşlukları kırp, boş blokları ele, 3+ boş satırı ez."""
    temiz = []
    for b in bloklar:
        if not b:
            continue
        b = b.rstrip()
        if not b.strip():
            continue
        temiz.append(b)
    md = "\n\n".join(temiz)
    md = _SATIR_SONU_BOSLUK_RE.sub("\n", md)
    return _UC_SATIR_RE.sub("\n\n", md).strip()


def _kayip_olc(cdata, govde_md):
    """Kayıpsızlık öz-denetimi — İKİ AYRI ÖLÇÜ, çünkü ikisi farklı şey söyler.

    1) SIRALI kayıp: CDATA'nın görünür metni, çıktının ALT DİZİSİ mi?
       Şartnamenin başarı ölçütü budur (madde 1 ve 5). Metin YERİNDEN
       oynamışsa da bu ölçü kayıp sayar — sıra, hukuk metninde anlamdır.
    2) EKSİK karakter (çoklu küme farkı): karakter GERÇEKTEN yok mu?
       Bu ikisini ayırmak şart: "yerinden oynadı" ile "yok oldu" aynı ağırlıkta
       değildir ve tek sayıyla raporlamak yanıltıcı olurdu.

    Ek bloklar (UYAP alanları/veri) ölçüme KATILMAZ; aksi hâlde gövdedeki bir
    kayıp, ekteki tekrar sayesinde maskelenebilirdi.
    """
    ihtiyac = _olcum_metni(cdata)
    saman = _olcum_metni(govde_md)
    i = 0
    sirali = 0
    for ch in ihtiyac:
        j = saman.find(ch, i)
        if j < 0:
            sirali += 1
        else:
            i = j + 1
    eksik = 0
    if sirali:
        sayim = {}
        for ch in saman:
            sayim[ch] = sayim.get(ch, 0) + 1
        for ch in ihtiyac:
            n = sayim.get(ch, 0)
            if n:
                sayim[ch] = n - 1
            else:
                eksik += 1
    return len(ihtiyac), sirali, eksik


# ---------------------------------------------------------------------------
# 6. ANA GİRİŞ
# ---------------------------------------------------------------------------

def _bos_kunye():
    return {
        "surum": SURUM,
        "format_id": "?",
        "gercek_tur": "?",
        "kabuk": "?",
        "imzali": False,
        "paragraf": 0, "tablo": 0, "satir": 0, "hucre": 0,
        "ic_ice_tablo": 0, "gorsel": 0, "alan": 0, "tab": 0,
        "liste_ogesi": 0, "ustbilgi_altbilgi": 0, "sayfa_sonu": 0,
        "veri_dugumu": 0, "birlesik_hucre_satiri": 0,
        "tablo_bicimi": [],
        "ic_ice_bicimi": [],
        "cdata_uzunluk": 0,
        "md_uzunluk": 0,
        "gorunur_karakter": 0,
        # A paketi (v0.5.15): alan etiketleri ÇAĞIRANA açılır (künye çekirdeği
        # oradan süzülür) ve içerik-akışı parmak izi ayrıca damgalanır.
        "alan_degerleri": {},
        "icerik_sha256": "",
        "kayip_karakter": 0,
        "eksik_karakter": 0,
        "cakisma_karakter": 0,
        "bosluk_satir_sonu": 0,
        "bosluk_gorunur": 0,
        "bmp_disi_karakter": 0,
        "offset_tasma": 0,
        "gorsel_yazildi": 0,
        "yapi_kuruldu": True,
        "uyarilar": [],
        "hata": "",
        "yonlendir": "",
        "sure_ms": 0.0,
    }


# Uzantı yalanı hâlinde çağıranın gideceği ingest işleyicisi (K8).
_YONLENDIRME = {"pdf": "pdf_isle", "docx": "docx_isle", "xlsx": "",
                "pptx": "", "ole2": "", "rtf": "", "odf": "", "zip": ""}


def udf_markdown_cikar(yol, gorsel_dizin=None, alanlar=True, veri=True,
                       hiza_notu=True, ic_ice="satir-ici"):
    """`.udf` dosyasını yapısı korunmuş Markdown'a çevir.

    Parametreler
    ------------
    yol           : okunacak `.udf` dosyasının yolu (SALT OKUNUR — K9).
    gorsel_dizin  : verilirse gömülü PNG'ler bu dizine yazılır ve Markdown
                    göreli bağ verir. None ise yalnız yer tutucu üretilir.
                    (Arşive ASLA yazılmaz; yazım YALNIZ bu dizinedir.)
    alanlar       : `fieldName` → değer eki üretilsin mi.
    veri          : CDATA dışı UYAP veri bloğu eki üretilsin mi.
    hiza_notu     : paragraf hizası için görünmez not bırakılsın mı.
    ic_ice        : "satir-ici" (VARSAYILAN — okuma sırası korunur) veya
                    "ayri" (iç tablo ayrı GFM tablosu; yapı tam korunur ama
                    metin ebeveyninden SONRAYA kayar, künyeye damgalanır).

    Dönüş
    -----
    (markdown, kunye). ASLA istisna fırlatmaz.
    """
    t0 = time.perf_counter()
    kunye = _bos_kunye()

    def bitir(md=""):
        kunye["sure_ms"] = round((time.perf_counter() - t0) * 1000, 3)
        kunye["md_uzunluk"] = len(md)
        return md, kunye

    def icerik_muhurle(cdata):
        """İÇERİK-AKIŞI parmak izi (σ-sha) — renderer'dan BAĞIMSIZ.

        Çıktı sha'sı sunum geliştikçe değişir; bu sha SÜRÜMLER ARASI SABİT
        kalmalıdır — asıl delil parmak izi budur. Değiştiği gün "kayıpsızlık
        tanımımız değişti" demektir ve ayrıca gerekçe ister.
        """
        kunye["icerik_sha256"] = hashlib.sha256(
            _olcum_metni(cdata or "").encode("utf-8")).hexdigest()

    # --- 1) baytları oku (salt okunur) ---------------------------------
    try:
        with open(yol, "rb") as fh:
            ham = fh.read()
    except OSError as e:
        kunye["hata"] = "okunamadi: %s" % (str(e)[:120],)
        return bitir()
    except Exception as e:                                   # beklenmedik
        kunye["hata"] = "okunamadi/%s: %s" % (type(e).__name__, str(e)[:100])
        return bitir()

    if not ham:
        kunye["gercek_tur"] = "bos"
        kunye["hata"] = "bos_dosya"
        return bitir()

    # --- 2) K8: gerçek tür ---------------------------------------------
    try:
        tur, ayrinti = _gercek_tur(ham)
    except Exception as e:
        tur, ayrinti = "bilinmeyen", type(e).__name__
    kunye["gercek_tur"] = tur
    if tur != "udf":
        # Uzantı yalanı: MARKDOWN ÜRETMEYE ÇALIŞMA. Çağıran doğru işleyiciye
        # yönlendirsin; sessizce atlamak YASAK olduğu için `hata` DOLDURULUR.
        kunye["yonlendir"] = _YONLENDIRME.get(tur, "")
        kunye["hata"] = "uzanti_yalani: gerçek tür '%s' (%s)" % (tur, ayrinti)
        kunye["uyarilar"].append(
            "K8/uzantı: dosya `.udf` değil, '%s' — %s" %
            (tur, ("ingest'te %s ile işlenmeli" % kunye["yonlendir"])
             if kunye["yonlendir"] else "bu hat bu türü işleyemez"))
        return bitir()

    # --- 3) kabuk + XML -------------------------------------------------
    try:
        xml_baytlari, imzali, kabuk, kabuk_uyari = _kabuk_ac(ham)
        kunye["imzali"] = bool(imzali)
        kunye["kabuk"] = kabuk
        kunye["uyarilar"].extend(kabuk_uyari)
        kok, cdata, fmt, xml_hatasi = _xml_ayristir(xml_baytlari)
        # İçerik-akışı mührü: CDATA elde edilir edilmez, RENDERER'DAN ÖNCE
        # basılır — sunum yolunda ne olursa olsun bu parmak izi kaynağın
        # kendisini damgalar.
        icerik_muhurle(cdata)
    except _Cikamadi as e:
        kunye["hata"] = e.tur + ((": " + e.ayrinti) if e.ayrinti else "")
        return bitir()
    except Exception as e:
        kunye["hata"] = "kabuk/%s: %s" % (type(e).__name__, str(e)[:100])
        return bitir()

    kunye["format_id"] = fmt
    kunye["cdata_uzunluk"] = len(cdata)
    if not cdata:
        kunye["hata"] = "cdata_yok: belgede görünür metin bloğu bulunamadı"
        return bitir()

    # --- 3b) XML bozuk ama metin sağlam: DÜZ METİN kurtarması -----------
    if kok is None:
        kunye["yapi_kuruldu"] = False
        kunye["uyarilar"].append(
            "XML/bozuk: belge ağacı ayrıştırılamadı (%s) — YALNIZ düz metin "
            "kurtarıldı; tablo/başlık/alan YAPISI YOK" % xml_hatasi)
        govde = _blok_birlestir(
            [_gorunur_temizle(s) for s in cdata.split("\n")])
        md = ("> **[UYARI] Bu evrağın XML yapısı BOZUK — yalnız düz metin "
              "kurtarıldı; tablo ve başlık yapısı YOKTUR.**\n\n" + govde)
        gorunur, kayip, eksik = _kayip_olc(cdata, govde)
        kunye["gorunur_karakter"] = gorunur
        kunye["kayip_karakter"] = kayip
        kunye["eksik_karakter"] = eksik
        return bitir(md)

    # --- 4) çevirim -----------------------------------------------------
    try:
        T = Metin(cdata)
        cev = Cevirici(kok, T, {"gorsel_dizin": gorsel_dizin,
                                "hiza_notu": hiza_notu,
                                "ic_ice": ic_ice})
        govde_md = _blok_birlestir(cev.govde())

        ekler = []
        # A paketi: ham alanlar ÇAĞIRANA da açılır (künye çekirdeği süzmesi için).
        # Sıra KORUNUR (dict 3.7+ ekleme sıralı) — determinizm şartı.
        if cev.alanlar:
            _ad_map = {}
            for _ad, _dg in cev.alanlar:
                _ad_map.setdefault(_ad, []).append(_dg)
            kunye["alan_degerleri"] = _ad_map
        if alanlar and cev.alanlar:
            gorulen, satirlar = set(), []
            for ad, deger in cev.alanlar:
                if not deger or (ad, deger) in gorulen:
                    continue
                gorulen.add((ad, deger))
                satirlar.append("- **%s**: %s" % (ad, deger))
            if satirlar:
                ekler.append("## UYAP ALANLARI (fieldName → değer)\n"
                             + "\n".join(satirlar))
        if veri:
            kayitlar = cev.veri_hasadi()
            if kayitlar:
                ekler.append("## UYAP VERİ BLOĞU (CDATA'da GÖRÜNMEZ)\n"
                             + "\n".join("- **%s**: %s" % (k, v)
                                         for k, v in kayitlar))
        md = govde_md + ("\n\n" + "\n\n".join(ekler) if ekler else "")

        bosluk_sonu, bosluk_gorunur = cev.kapsam_denetle()
        gorunur, kayip, eksik = _kayip_olc(cdata, govde_md)

        kunye.update({k: cev.sayac[k] for k in
                      ("paragraf", "tablo", "satir", "hucre", "ic_ice_tablo",
                       "gorsel", "alan", "tab", "liste_ogesi",
                       "ustbilgi_altbilgi", "sayfa_sonu", "veri_dugumu",
                       "birlesik_hucre_satiri")})
        kunye["tablo_bicimi"] = cev.tablo_bicimi
        kunye["ic_ice_bicimi"] = cev.ic_ice_bicimi
        kunye["gorunur_karakter"] = gorunur
        kunye["kayip_karakter"] = kayip
        kunye["eksik_karakter"] = eksik
        kunye["cakisma_karakter"] = cev.cakisma
        kunye["bosluk_satir_sonu"] = bosluk_sonu
        kunye["bosluk_gorunur"] = bosluk_gorunur
        kunye["bmp_disi_karakter"] = T.bmp_disi
        kunye["offset_tasma"] = T.tasma
        kunye["uyarilar"].extend(cev.uyarilar)
        if eksik:
            kunye["uyarilar"].append(
                "kayıpsızlık/EKSİK: %d görünür karakter çıktıda HİÇ YOK "
                "(%d karakterde) — GERÇEK KAYIP" % (eksik, gorunur))
        elif kayip:
            kunye["uyarilar"].append(
                "kayıpsızlık/SIRA: %d görünür karakter yerinden oynadı "
                "(%d karakterde); hiçbiri yok olmadı" % (kayip, gorunur))

        # Görselleri YALNIZCA istenen dizine yaz (K9: arşive asla).
        if gorsel_dizin and cev.gorseller:
            try:
                os.makedirs(gorsel_dizin, exist_ok=True)
                for sira, png in cev.gorseller:
                    hedef = os.path.join(gorsel_dizin, "gorsel-%03d.png" % sira)
                    with open(hedef, "wb") as fh:
                        fh.write(png)
                    kunye["gorsel_yazildi"] += 1
            except OSError as e:
                kunye["uyarilar"].append(
                    "görsel: dizine yazılamadı (%s)" % str(e)[:80])

        return bitir(md)
    except Exception as e:
        # Buraya düşmek bir HATADIR ama çağıranı çökertmez: künye konuşur.
        kunye["hata"] = "cevirim/%s: %s" % (type(e).__name__, str(e)[:120])
        return bitir()


# ---------------------------------------------------------------------------
# 7. CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="udf_md_uretim.py",
        description="UYAP .udf dosyasını yapısı korunmuş Markdown'a çevirir "
                    "(yalnız stdlib; ağ/oturum yok; girdi salt okunur).")
    ap.add_argument("girdi", help="okunacak .udf dosyası")
    ap.add_argument("-o", "--cikti", help="Markdown çıktı dosyası "
                                          "(verilmezse stdout)")
    ap.add_argument("--gorsel-dizin", default=None,
                    help="gömülü PNG'lerin yazılacağı dizin (varsayılan: yazma)")
    ap.add_argument("--kunye", action="store_true",
                    help="künyeyi JSON olarak stderr'e bas")
    ap.add_argument("--no-alanlar", action="store_true",
                    help="UYAP alan ekini üretme")
    ap.add_argument("--no-veri", action="store_true",
                    help="CDATA dışı UYAP veri ekini üretme")
    ap.add_argument("--no-hiza", action="store_true",
                    help="paragraf hiza notlarını üretme")
    ap.add_argument("--ic-ice", choices=("satir-ici", "ayri"),
                    default="satir-ici",
                    help="iç içe tablo kipi: satir-ici (okuma sırasını korur, "
                         "varsayılan) | ayri (yapıyı korur, metin kayar)")
    a = ap.parse_args(argv)

    md, kunye = udf_markdown_cikar(a.girdi,
                                   gorsel_dizin=a.gorsel_dizin,
                                   alanlar=not a.no_alanlar,
                                   veri=not a.no_veri,
                                   hiza_notu=not a.no_hiza,
                                   ic_ice=a.ic_ice)
    if a.kunye:
        _sys.stderr.write(json.dumps(kunye, ensure_ascii=False) + "\n")
    if kunye["hata"]:
        _sys.stderr.write("HATA: %s\n" % kunye["hata"])
        if kunye["yonlendir"]:
            _sys.stderr.write("YÖNLENDİR: %s\n" % kunye["yonlendir"])
        return 1
    if a.cikti:
        with open(a.cikti, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(md)
    else:
        _sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    _sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
kritik_alan.py — OCR KRİTİK ALAN TEYİDİ (v0.5.18 · OCR planı O-3)

NEDEN: OCR'ın O/0, I/l/1, B/8, S/5, Z/2, G/6 karışıklığı tebliğ tarihini, esas/karar
numarasını, TCKN'yi, IBAN'ı DEĞİŞTİRİR. Yanlış tebliğ tarihi = yanlış son gün =
süre kaçırma; yanlış esas no = yanlış dosyaya atıf. Bu modül OCR'lı metinde bu
alanları bulur ve ŞÜPHELİ olanları işaretler.

İLKELER:
  1. Metin ASLA düzeltilmez: "12.O3.2025" olduğu gibi kalır; yalnız işaret düşülür.
     Doğru değeri seçmek orijinal evrakla teyittir (avukat).
  2. "Doğrulandı" diye bir durum YOKTUR. Boş liste "şüphe yakalanmadı" demektir;
     rakam→rakam hatası (3↔8, 1↔7, 5↔6) sağlamasız alanlarda TESPİT EDİLEMEZ.
  3. Asgari ve gürültüsüz küme (alarm yorgunluğu da avukata zarardır): çıpalı
     tarih (tebliğ/tebellüğ/karar/düzenleme tarihi), esas/karar no, bağlamlı TCKN
     (sağlama), IBAN (mod-97). Tutar/telefon/kanun no bilinçli olarak YOK.
  4. Maskeli değer (123*****456) işaretlenmez; IBAN 26 karaktere tamamlanamıyorsa
     "geçersiz" değil "okunamadı" denir.

Kullanım (modül): tara(metin) → [{sayfa, tur, ham, neden}]
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import datetime, re

SURUM = "1.0"
__all__ = ["tara", "md_satirlari", "tarih_adaylari_supheli", "SURUM"]
AZAMI_KALEM = 30
CIPA_KOMSULUK = 80
YIL_ALT, YIL_UST = 1950, 2099   # SABİT aralık: sonuç bugünün tarihine bağlı olmasın (determinizm)
# OCR'ın rakam yuvasına koyabildiği harfler (ölçü: Tesseract tur çıktısında görülen karışıklıklar).
# Desenler BÜYÜK/KÜÇÜK HARF DUYARLIDIR: IGNORECASE sınıfı genişletir ('tribün' → 'TR'+'ib').
_R = "[0-9OoIlİı|SsBbZzGgD]"
_HARF = re.compile(r"[^0-9]")
_CIPALAR = ("tebliğ", "teblig", "tebellüğ", "tebellug", "karar tarihi", "düzenleme tarihi",
            "duzenleme tarihi", "tefhim", "ödeme emri", "odeme emri")
_TARIH_RE = re.compile(r"(?<![0-9A-Za-z])(%s{1,2})([./-])(%s{1,2})\2(%s{4})(?![0-9A-Za-z])" % (_R, _R, _R))
# Her isteğe bağlı parça KENDİ boşluğunu taşır (yan yana `\s*` YOK): yan yana iki `\s*`
# uzun boşluk dizisinde üstel geri izleme (ReDoS) doğurur — karşı tarafın evrakı ingest'i
# kilitleyebilirdi (2026-10-05 güvenlik incelemesi).
_ESAS_RE = re.compile(r"\b(ESAS|Esas|esas|KARAR|Karar|karar|E|K)(?:\s*\.)?"
                      r"(?:\s*(?:[Nn][Oo]|[Nn]umaras[ıi]|[Ss]ay[ıi]s[ıi]|NUMARASI|SAYISI))?(?:\s*[:.])?\s*"
                      r"(%s{4})\s*/\s*(%s{1,7})(?![0-9A-Za-z])" % (_R, _R))
_TCKN_BAGLAM = re.compile(r"(?i)(t\.?\s*c\.?\s*kimlik|kimlik\s*no|tckn|t\.?c\.?\s*no)")
_TCKN_RE = re.compile(r"(?<![0-9A-Za-z])(%s{11})(?![0-9A-Za-z*])" % _R)
_IBAN_ANAHTAR = re.compile(r"(?i)\biban\b")
_IBAN_GOVDE = re.compile(r"T\s*R\s*((?:%s\s*){2,30})" % _R)                 # anahtar sözcükten SONRA
_IBAN_SERBEST = re.compile(r"(?<![0-9A-Za-z])TR\s*\d{2}(?:\s*\d){22}(?![0-9A-Za-z])")   # anahtarsız: katı


def _sayfa_haritasi(metin):
    """'<!-- --- sayfa N --- -->' işaretlerinden (konum, sayfa) listesi."""
    return [(m.start(), int(m.group(1))) for m in re.finditer(r"<!-- --- sayfa (\d+) --- -->", metin or "")]


def _sayfa(harita, konum):
    s = None
    for k, n in harita:
        if k > konum:
            break
        s = n
    return s


def _kucuk(s):
    """Türkçe küçültme; UZUNLUK KORUNUR (dizinler özgün metne eşlenir)."""
    s = s.replace("İ", "i").replace("I", "ı")
    k = s.lower()
    return k if len(k) == len(s) else "".join(c.lower() if len(c.lower()) == 1 else c for c in s)


def _harfli(*parcalar):
    return any(_HARF.search(p) for p in parcalar)


def _tckn_gecerli(t):
    if len(t) != 11 or not t.isdigit() or t[0] == "0":
        return False
    d = [int(c) for c in t]
    if (sum(d[0:9:2]) * 7 - sum(d[1:8:2])) % 10 != d[9]:
        return False
    return sum(d[:10]) % 10 == d[10]


def _iban_gecerli(iban):
    """ISO 13616 mod-97 (TR: 26 karakter)."""
    s = iban[4:] + iban[:4]
    try:
        return int("".join(str(int(c, 36)) for c in s)) % 97 == 1
    except ValueError:
        return False


def tara(metin):
    """OCR'lı metinde şüpheli kritik alanlar: [{sayfa, tur, ham, neden}]. ASLA düzeltmez."""
    if not metin:
        return []
    harita = _sayfa_haritasi(metin)
    kucuk = _kucuk(metin)
    out, gorulen = [], set()

    def ekle(konum, tur, ham, neden):
        anahtar = (tur, ham, neden)
        if anahtar in gorulen or len(out) >= AZAMI_KALEM:
            return
        gorulen.add(anahtar)
        out.append({"sayfa": _sayfa(harita, konum), "tur": tur, "ham": ham, "neden": neden})

    # 1) çıpalı tarih — süre bu tarihten işler
    for m in _TARIH_RE.finditer(metin):
        pencere = kucuk[max(0, m.start() - CIPA_KOMSULUK): m.end() + CIPA_KOMSULUK]
        if not any(c in pencere for c in _CIPALAR):
            continue
        g, a, y = m.group(1), m.group(3), m.group(4)
        if _harfli(g, a, y):
            ekle(m.start(), "tarih", m.group(0), "rakam yuvasında harf (OCR karışıklığı: O/0, I/1, S/5, B/8…)")
            continue
        try:
            datetime.date(int(y), int(a), int(g))
        except ValueError:
            ekle(m.start(), "tarih", m.group(0), "takvimde olmayan tarih (gün/ay okunuşu şüpheli)")
            continue
        if not YIL_ALT <= int(y) <= YIL_UST:
            ekle(m.start(), "tarih", m.group(0), "mantıksız yıl (OCR okuma hatası olabilir)")
    # 2) esas / karar no
    for m in _ESAS_RE.finditer(metin):
        yil, sira = m.group(2), m.group(3)
        tur = "esas_no" if m.group(1).lower() in ("esas", "e") else "karar_no"
        if _harfli(yil, sira):
            ekle(m.start(2), tur, "%s/%s" % (yil, sira), "numarada harf (OCR karışıklığı)")
        elif not YIL_ALT <= int(yil) <= YIL_UST:
            ekle(m.start(2), tur, "%s/%s" % (yil, sira), "mantıksız yıl")
    # 3) bağlamlı TCKN (maskeli değer işaretlenmez)
    for b in _TCKN_BAGLAM.finditer(metin):
        m = _TCKN_RE.search(metin, b.end(), b.end() + 40)
        if not m:
            continue
        t = m.group(1)
        if _harfli(t):
            ekle(m.start(), "tckn", t, "rakam yuvasında harf (OCR karışıklığı)")
        elif not _tckn_gecerli(t):
            ekle(m.start(), "tckn", t, "TCKN sağlaması tutmuyor (OCR okuma hatası olabilir)")
    # 4) IBAN (mod-97): "IBAN" sözcüğünden sonra izinli sınıfla; anahtarsız yalnız katı rakam biçimi
    adaylar = []
    for a in _IBAN_ANAHTAR.finditer(metin):
        m = _IBAN_GOVDE.search(metin, a.end(), a.end() + 40)
        if m:
            adaylar.append((m.start(), re.sub(r"\s+", "", m.group(1))))
    for m in _IBAN_SERBEST.finditer(metin):
        if not any(abs(m.start() - k) < 5 for k, _ in adaylar):
            adaylar.append((m.start(), re.sub(r"\s+", "", m.group(0))[2:]))
    for konum, govde in adaylar:
        if len(govde) < 24:
            ekle(konum, "iban", ("TR" + govde)[:34], "IBAN tamamlanamadı (okunamadı) — orijinalden teyit")
            continue
        govde = govde[:24]
        if _harfli(govde):
            ekle(konum, "iban", "TR" + govde, "rakam yuvasında harf (OCR karışıklığı)")
        elif not _iban_gecerli("TR" + govde):
            ekle(konum, "iban", "TR" + govde, "IBAN mod-97 sağlaması tutmuyor")
    return out


def tarih_adaylari_supheli(metin):
    """Süre adayı taraması (okuma_kapisi) için TEK KAYNAK: çıpa komşuluğunda rakam
    yuvasında HARF taşıyan tarih biçimli dizgiler. Katı rakam deseni bunları HİÇ
    görmez → OCR '12.O3.2025' okuduğunda 'süre adayı yok' sanılırdı (sessiz kayıp).
    Dönüş: [(konum, ham)] — değer DÜZELTİLMEZ."""
    out = []
    kucuk = _kucuk(metin or "")
    for m in _TARIH_RE.finditer(metin or ""):
        if not _harfli(m.group(1), m.group(3), m.group(4)):
            continue
        pencere = kucuk[max(0, m.start() - CIPA_KOMSULUK): m.end() + CIPA_KOMSULUK]
        if any(c in pencere for c in _CIPALAR):
            out.append((m.start(), m.group(0)))
    return out


def md_satirlari(kalemler):
    """md başlığı için satırlar (yalnız şüphe varsa)."""
    if not kalemler:
        return []
    satirlar = ["- 🔎 **KRİTİK ALAN TEYİDİ: %d alan şüpheli** — OCR metni DÜZELTİLMEDİ; değerleri "
                "orijinal evraktan teyit et (liste 'doğrulandı' anlamına gelmez; rakam→rakam "
                "hatası bu taramayla yakalanamaz)." % len(kalemler)]
    for k in kalemler[:8]:
        satirlar.append("  - sayfa %s · %s · «%s» — %s" % (k.get("sayfa") or "?", k["tur"], k["ham"], k["neden"]))
    if len(kalemler) > 8:
        satirlar.append("  - … +%d alan daha (künye: dogrulama_gerekli)" % (len(kalemler) - 8))
    return satirlar

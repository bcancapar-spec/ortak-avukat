#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
kunye_teyit.py — oa-kontrol ATIF/KÜNYE DOĞRULAMA KAPISI (deterministik)

Sistemin iddiası "halüsinasyonu yapısal dışlarım"dır. Bu script o iddiayı model
disiplininden MEKANİK kapıya çevirir: bir taslak dilekçe/mütalaadaki HER hukuki
atfı (içtihat künyesi + mevzuat maddesi) regex ile çıkarır ve TEYİT EDİCİ kaynak
evreniyle çaprazlar. İzi OLMAYAN atıf "TEYİTSİZ"tir ve TESLİM ENGELİdir (exit 1).

Kural (pipeline künye tutarlılık kuralının fiziksel karşılığı): teyit edici
kaynakta esas/karar no veya kanun+madde eşleşmesi bulunmayan künye çıktıya
"teyitli" giremez. "Teyitli" etiketi ancak fiilen yapılmış bir MCP çağrısının
izine konur; bu script o izi arar, üretmez.

── PAYLAŞIMLI YARDIMCI (M2-3 — `kunye_ortak.py`) ──
İçtihat esas/karar/daire çıkarım+normalizasyon mantığı artık `kunye_ortak.py`
(oa-kontrol) modülünde TEK yerde yaşar; bu script kendi ESAS_RE/KARAR_RE/
_norm_no/_daire_key/_daire_kumesi tanımlarını TUTMAZ, `ictihat_muhakeme_denetim.py`
ile AYNI ortak modülü çağırır (iki-yazar riski kapalı — tek tanım, iki kullanan).
Mevzuat madde-çıkarımı (kanun+madde regex'leri) bu modülün kapsamı dışıdır,
burada yerel kalır.

── F) KÜNYE TEYİT ÖNCE-BAK (`--once-bak`) ──
Bir künye kütükte (+ ham MCP dökümünde) ZATEN varsa AYNI künye için tekrar bir
MCP teyit turu koşmak gereksizdir. `--once-bak "<künye metni>"` bu durumu
MEKANİK olarak denetler (advisory — teslim engeli DEĞİL, her hâlde exit 0):
künyeyi kütük/döküm evreninde arar, VAR/YOK der. VARSA ajan aynı künye için
yeni bir MCP çağrısını atlayabilir; YOKSA MCP teyidi hâlâ gereklidir. Bu mod
`taslak` pozisyonel argümanını GEREKTİRMEZ.

── KAYNAK EVRENİ (kendi-kendini-teyit deliğinin kapatılması) ──
Teyit EDİCİ kaynak evreni SADECE ikisidir:
  (1) künye teyit kütüğü      → `_oa/teyit/kunye-teyit.md`
  (2) ham MCP döküm dizini    → `_oa/teyit/dokum/`  (yalnız ham MCP çıktıları)
`_oa/cikti/` teyit kaynağı DEĞİLDİR. Orası MCP dökümü değil, MODELİN yazdığı
çalışma evraklarıdır (taslak, antitez, kıyas...). Model 3. adımda bir çalışma
evrakına halüsinasyon künye yazarsa, eski sürümde o künye 9. adımda "döküm izli →
TEYİTLİ" çıkıyordu — kapının varlık sebebi kaynak tanımıyla deliniyordu. Artık
`_oa/cikti/` en çok "[BİLGİ] iz var ama TEYİT SAYILMAZ (model çıktısı)" notu
üretir; statüyü TEYİTLİ YAPMAZ (kütük/ham döküm izi şarttır).

── MERCİ KATMANI (aynı esas/karar farklı dairede eşleşmesin) ──
"2023/1234" her dairede vardır; mercisiz eşleşmede farklı daire aynı esas/karar
üstünden TEYİTLİ geçebiliyordu. Artık taslak atfında bir daire/merci (ör.
"12. HD") yakalandıysa, eşleşen kütük/döküm segmentinde de o daire aranır.
Segmentte bizim daire bulunamazsa "TEYİTLİ (⚠ MERCİ DOĞRULANAMADI — farklı daire
olabilir)" ARA STATÜSÜ üretilir. Bu ara statü künye izi GERÇEK olduğu için exit'i
1 YAPMAZ; GÖRÜNÜR uyarı + ayrı sayaçtır. Hangi dairenin baktığı esas eşleşmesi
oa-kontrol A-listesi muhakemesine bırakılır (mekanik iz ≠ daire doğruluğu).

Kullanım:
  python kunye_teyit.py <taslak.md> [--kutuk _oa/teyit/kunye-teyit.md] \
      [--dokum-dizin _oa/teyit/dokum] [--cikti-dizin _oa/cikti]
  python kunye_teyit.py <taslak.md> --kok "<klasör>"   # oa_hafiza.py/tam_tur.py simetrisi
  python kunye_teyit.py --once-bak "Yargıtay 4. HD, E. 2023/1234, K. 2023/5678" \
      [--kutuk ... | --kok "<klasör>"]                 # F — önce-bak (advisory)

--kok: verilirse --kutuk/--dokum-dizin/--cikti-dizin'in VARSAYILANLARI
<KLASÖR>/_oa/teyit/kunye-teyit.md, <KLASÖR>/_oa/teyit/dokum, <KLASÖR>/_oa/cikti olur
(cwd'den BAĞIMSIZ, mutlak --kok verilebilir). Açıkça verilen --kutuk/--dokum-dizin/
--cikti-dizin her zaman --kok'u EZER. --kok verilmezse davranış eskisiyle AYNIDIR
(CWD-göreli VARSAYILAN_*). Gerekçe: Claude Code alt-ajan thread'lerinde cwd
sıfırlandığından, --kok eksikliği "Failed to run citation gate" ile sonuçlanıyordu
(gerçek Denizli testinde görüldü) — bu, oa_hafiza.py/tam_tur.py/pipeline_kayit.py'deki
--kok simetrisinin oa-kontrol tarafındaki eksik parçasıydı.

Çıkış kodları:
  0 = tüm atıflar teyitli (veya atıf yok) — kapı AÇIK
      (⚠ MERCİ DOĞRULANAMADI ara statüsü TEK BAŞINA exit'i 1 YAPMAZ — künye izlidir)
  1 = en az bir TEYİTSİZ atıf VAR ya da kütük dosyası yok — TESLİM ENGELİ
      (yalnız `_oa/cikti/` izi olan künye TEYİTSİZ'dir → exit 1)

Not: Bu kapı künyenin TEYİT EDİCİ KAYNAKTA İZİNİ dener; kararın hükmünün iddiayı
gerçekten karşılayıp karşılamadığı (esas/savunma ayrımı) ve doğru dairenin hangisi
olduğu hâlâ oa-kontrol A-listesinin muhakeme işidir. Mekanik iz ≠ içerik doğruluğu.
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import os
import re
import sys

BURA = os.path.dirname(os.path.abspath(__file__))
if BURA not in sys.path:
    sys.path.insert(0, BURA)

import kunye_ortak as ko  # noqa: E402 — paylaşımlı esas/karar/daire yardımcısı (M2-3)

VARSAYILAN_KUTUK = os.path.join("_oa", "teyit", "kunye-teyit.md")
# Ham MCP dökümleri — TEYİT EDİCİ ikinci kaynak (Fikir-1: MCP döküm diski).
VARSAYILAN_DOKUM = os.path.join("_oa", "teyit", "dokum")
# Çalışma evrakları — BİLGİ AMAÇLI, teyit EDİCİ DEĞİL (model çıktısı; kendi-kendini
# teyit deliğinin kaynağı). Geriye uyum için `--cikti-dizin` kabul edilir.
VARSAYILAN_CIKTI = os.path.join("_oa", "cikti")

# ── Bilinen kanun kısaltması ↔ numara eşlemesi (atıf çapraz-eşlemesi için) ──
# "TBK m.49" taslakta, "6098 ... m.49" kütükte olsa bile eşleşsin diye.
KANUN_NO = {
    "TBK": "6098", "TMK": "4721", "TTK": "6102", "HMK": "6100", "HUMK": "1086",
    "CMK": "5271", "TCK": "5237", "İYUK": "2577", "IYUK": "2577",
    "İİK": "2004", "IIK": "2004", "KVKK": "6698", "VUK": "213", "GVK": "193",
    "AATUHK": "6183", "İK": "4857", "IK": "4857", "AY": "2709",
    "İSGK": "6331", "ISGK": "6331", "TKHK": "6502", "HSK": "6087",
    "SGK": "5510", "BK": "818", "MK": "743", "KDV": "3065",
}
NO_KANUN = {v: k for k, v in KANUN_NO.items()}

# Bare biçim ("HMK 119") yalnızca BİLİNEN kısaltmalarla çıkarılır — aksi hâlde
# mahkeme markerları (AYM, BAM, HGK) yanlışlıkla "kanun" sanılır.
BILINEN_BARE = set(KANUN_NO.keys()) | {"MÜLGA", "HUMK"}

# Mahkeme/kurul markerları — kanun sanılmamaları için dışlanır.
MERCILER = {
    "YARGITAY", "DANIŞTAY", "DANISTAY", "AYM", "BAM", "BİM", "BIM", "HGK",
    "CGK", "İBK", "IBK", "AİHM", "AIHM", "SAYIŞTAY", "HD", "CD", "İDDK",
    "IDDK", "VDDK", "KANUN", "SAYILI", "MADDE", "ESAS", "KARAR",
}

# ── İçtihat: esas/karar/daire çıkarımı — PAYLAŞIMLI (M2-3) ──
# Bu script artık kendi ESAS_RE/KARAR_RE/_daire_key/_daire_kumesi tanımlarını
# TUTMAZ; iki-geçişli etiket-önce/ters-alternatif çakışma çözümü ve daire
# ayırt edici mantığı TEK yerde (`kunye_ortak.py`) yaşar — bkz. `ko.esas_karar_atiflari`,
# `ko.norm_no`, `ko.daire_key`, `ko.daire_kumesi`, `ko.DAIRE_RE`.

# ── Mevzuat: kanun tanıtıcısı + madde ──
_KANUN = (
    r"(?:\d{3,5}\s*[Ss]ayılı\s+[^\n]{0,50}?(?:[Kk]anun\w*|KHK)"   # 6098 sayılı ... Kanun
    r"|\d{3,5}\s*[Ss]ayılı\s+[A-ZÇĞİÖŞÜ]{2,7}"                    # 6098 sayılı TBK
    r"|[A-ZÇĞİÖŞÜ]{2,7})"                                         # TBK, HMK, İYUK
)
_MADDE = r"\d+(?:\s*/\s*\d+)?(?:\s*[-–]\s*[a-zçğıöşü]\b)?"

# "TBK m.49" / "6098 sayılı Kanun m.49" / "TCK md. 5" / "HMK madde 119"
MEVZUAT_M_RE = re.compile(
    r"(?P<kanun>" + _KANUN + r")\s*"
    r"(?:m\.\s*|md\.\s*|mad\.\s*|[Mm]adde\s*|MADDE\s*)(?P<madde>" + _MADDE + r")"
)
# Ters biçim: "TBK'nın 49. maddesi" / "HMK 119. madde"
MEVZUAT_REV_RE = re.compile(
    r"(?P<kanun>" + _KANUN + r")['’]?(?:[nN][ıiuü]n|[dt][ae])?\s*"
    r"(?P<madde>\d+(?:\s*/\s*\d+)?)\s*\.?\s*"
    r"(?:uncu|üncü|inci|ıncı|nci|ncı)?\s*[Mm]adde(?:si|sinde|sine|sindeki)?"
)
# Bare biçim: "HMK 119" (yalnız bilinen kısaltma + çıplak sayı)
MEVZUAT_BARE_RE = re.compile(
    r"\b(?P<kanun>[A-ZÇĞİÖŞÜ]{2,7})\s+(?P<madde>\d{1,4}(?:\s*/\s*\d{1,3})?)\b(?!\s*(?:E\.|K\.|Esas|Karar|sayılı))"
)

OCR_RE = re.compile(r"OCR|⚠")


def _sikistir(s, n=140):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


# ───────────────────────── ATIF ÇIKARIMI ─────────────────────────
class Atif:
    __slots__ = ("tur", "metin", "esas", "karar", "kanun_anahtar", "madde",
                 "ocr_taslak", "satir_no", "durum", "kaynak", "kaynak_seg",
                 "merci", "daire_key", "merci_uyari", "merci_celiski",
                 "cikti_izi", "cikti_seg")

    def __init__(self, tur, metin):
        self.tur = tur          # 'ictihat' | 'mevzuat'
        self.metin = metin
        self.esas = None
        self.karar = None
        self.kanun_anahtar = set()
        self.madde = None
        self.ocr_taslak = False
        self.satir_no = None
        self.durum = "TEYİTSİZ"
        self.kaynak = None
        self.kaynak_seg = None
        self.merci = None            # taslakta yakalanan daire metni (ör. "12. HD")
        self.daire_key = None        # (no, aile) — merci ayırt edicisi; yoksa None
        self.merci_uyari = False     # TEYİTLİ ama izde merci doğrulanamadı
        self.merci_celiski = False   # izde FARKLI bir daire fiilen görüldü
        self.cikti_izi = None        # SADECE çalışma evrakı (BİLGİ) izi etiketi
        self.cikti_seg = None

    def anahtar(self):
        """Tekilleştirme anahtarı."""
        if self.tur == "ictihat":
            return ("ictihat", self.esas, self.karar)
        return ("mevzuat", tuple(sorted(self.kanun_anahtar)), self.madde)


def _kanun_anahtarlari(kanun_str):
    """Kanun metninden eşleşme anahtarları (kısaltma + numara + eşlenik)."""
    al = set()
    for num in re.findall(r"\d{3,5}", kanun_str):
        al.add(num)
        if num in NO_KANUN:
            al.add(NO_KANUN[num])
    for ab in re.findall(r"[A-ZÇĞİÖŞÜ]{2,7}", kanun_str):
        if ab in MERCILER:
            continue
        al.add(ab)
        if ab in KANUN_NO:
            al.add(KANUN_NO[ab])
    return al


def _satir_no(metin, konum):
    return metin.count("\n", 0, konum) + 1


def _satir_metni(metin, konum):
    bas = metin.rfind("\n", 0, konum) + 1
    son = metin.find("\n", konum)
    if son == -1:
        son = len(metin)
    return metin[bas:son]


def _satir_metni_no(metin, no):
    """satir_no (1-index, `ko._satir_no` ile aynı sayaç) numaralı satırın
    metnini döndürür — `ko.esas_karar_atiflari` yalnız satir_no verir, ham
    karakter konumu vermez (bkz. ictihat_cikar)."""
    satirlar = metin.split("\n")
    idx = no - 1
    return satirlar[idx] if 0 <= idx < len(satirlar) else ""


def ictihat_cikar(metin):
    """Esas/karar numaralarını bulup künyelere eşle. Çıkarım + nearest-pairing
    + merci-penceresi mantığı PAYLAŞIMLI `kunye_ortak.esas_karar_atiflari()`
    iledir (M2-3) — burada TEKRARLANMAZ; yalnız OCR/merci-metni gibi bu
    scripte özel alanlar üstüne eklenir."""
    atiflar = []
    for ham in ko.esas_karar_atiflari(metin):
        atif = Atif("ictihat", ham["metin"])
        atif.esas = ham["esas"]
        atif.karar = ham["karar"]
        atif.satir_no = ham["satir_no"]
        if ham.get("daire_key"):
            atif.daire_key = ham["daire_key"]
            dm = ko.DAIRE_RE.search(ham["metin"])
            if dm:
                atif.merci = _sikistir(dm.group(0), 40)
        atif.ocr_taslak = bool(OCR_RE.search(_satir_metni_no(metin, ham["satir_no"])))
        atiflar.append(atif)
    return atiflar


def mevzuat_cikar(metin):
    atiflar = []
    goruldu_span = []

    def cakisma(s, e):
        for (a, b) in goruldu_span:
            if s < b and a < e:
                return True
        return False

    for rx in (MEVZUAT_M_RE, MEVZUAT_REV_RE, MEVZUAT_BARE_RE):
        for m in rx.finditer(metin):
            s, e = m.start(), m.end()
            if cakisma(s, e):
                continue
            kanun_ham = m.group("kanun")
            # Bare biçimde mahkeme/kurul markerlerini dışla
            if rx is MEVZUAT_BARE_RE and kanun_ham.upper() not in BILINEN_BARE:
                continue
            anahtarlar = _kanun_anahtarlari(kanun_ham)
            if not anahtarlar:
                continue
            madde = ko.norm_no(m.group("madde"))
            goruldu_span.append((s, e))
            atif = Atif("mevzuat", _sikistir(m.group(0)))
            atif.kanun_anahtar = anahtarlar
            atif.madde = madde
            atif.satir_no = _satir_no(metin, s)
            atif.ocr_taslak = bool(OCR_RE.search(_satir_metni(metin, s)))
            atiflar.append(atif)
    return atiflar


def atiflari_cikar(metin):
    hepsi = ictihat_cikar(metin) + mevzuat_cikar(metin)
    # Tekilleştir (aynı künye birden çok geçebilir) — sırayı koru
    gorulen, tekil = set(), []
    for a in hepsi:
        k = a.anahtar()
        if k in gorulen:
            continue
        gorulen.add(k)
        tekil.append(a)
    return tekil


# ───────────────────────── KAYNAK / EŞLEŞME ─────────────────────────
def _segmentler(ham):
    """Kaynak metninden eşleşme segmentleri: satırlar + kayan pencereler.
    (E/K bitişik satırlara bölünmüş olsa da yakalanabilsin diye pencere.)"""
    norm = re.sub(r"\s*/\s*", "/", ham)
    segs = [s.strip() for s in norm.splitlines() if s.strip()]
    duz = re.sub(r"[ \t]+", " ", norm)
    duz = re.sub(r"\n+", " \n ", duz)
    duz = re.sub(r"\s+", " ", duz)
    W, step = 260, 130
    if duz:
        for i in range(0, len(duz), step):
            segs.append(duz[i:i + W])
    return segs


def _dizin_kaynaklari(dizin, etiket_on):
    """Dizindeki .md/.txt/.json dosyalarını [(etiket, [segment,...]), ...] yükler."""
    cikan = []
    if dizin and os.path.isdir(dizin):
        for ad in sorted(os.listdir(dizin)):
            if ad.lower().endswith((".md", ".txt", ".json")):
                yol = os.path.join(dizin, ad)
                if os.path.isfile(yol):
                    try:
                        with open(yol, encoding="utf-8", errors="replace") as f:
                            cikan.append((etiket_on + ad, _segmentler(f.read())))
                    except OSError:
                        pass
    return cikan


def kaynaklari_yukle(kutuk_yolu, dokum_dizin, cikti_dizin):
    """Teyit edici ve bilgi amaçlı kaynakları AYRI döndürür.

    Döner: (teyit_kaynaklar, bilgi_kaynaklar, kutuk_var)
      teyit_kaynaklar : kütük (`_oa/teyit/kunye-teyit.md`) + ham MCP dökümleri
                        (`_oa/teyit/dokum/`) — statüyü TEYİTLİ yapabilen tek evren.
      bilgi_kaynaklar : `_oa/cikti/` çalışma evrakları — MODEL çıktısı; TEYİT
                        SAYILMAZ, yalnız "[BİLGİ] iz var" notu üretir (delik kapalı).
    """
    teyit_kaynaklar = []
    kutuk_var = os.path.isfile(kutuk_yolu)
    if kutuk_var:
        with open(kutuk_yolu, encoding="utf-8", errors="replace") as f:
            teyit_kaynaklar.append(("kütük:" + kutuk_yolu, _segmentler(f.read())))
    teyit_kaynaklar += _dizin_kaynaklari(dokum_dizin, "döküm:")
    # `_oa/cikti/` teyit EDİCİ değildir → yalnız bilgi kaynağı olarak yüklenir.
    bilgi_kaynaklar = _dizin_kaynaklari(cikti_dizin, "çıktı(BİLGİ):")
    return teyit_kaynaklar, bilgi_kaynaklar, kutuk_var


def _sayi_var(segment, sayi):
    """Sayıyı komşu rakamdan izole ederek arar (149 ≠ 49)."""
    return re.search(r"(?<!\d)" + re.escape(sayi) + r"(?!\d)", segment) is not None


def _anahtar_var(segment, alias):
    if alias.isdigit():
        return _sayi_var(segment, alias)
    return re.search(r"(?<![A-ZÇĞİÖŞÜ0-9])" + re.escape(alias) + r"(?![A-ZÇĞİÖŞÜ0-9])",
                     segment) is not None


def segment_eslesir(atif, segment):
    if atif.tur == "ictihat":
        if atif.esas and not _sayi_var(segment, atif.esas):
            return False
        if atif.karar and not _sayi_var(segment, atif.karar):
            return False
        return bool(atif.esas or atif.karar)
    # mevzuat: madde numarası + en az bir kanun anahtarı aynı segmentte
    if not atif.madde or not _sayi_var(segment, atif.madde):
        return False
    return any(_anahtar_var(segment, al) for al in atif.kanun_anahtar)


def _merci_durumu(atif, seg):
    """Eşleşen segmentin, atfın dairesiyle merci ilişkisi.
       'eslesti' : atıfta daire yok (denetim gerekmez) veya izde AYNI daire var.
       'celiski' : izde başka daire(ler) var ama bizimki yok (farklı daire olabilir).
       'yok'     : izde hiç numaralı daire yok — merci doğrulanamadı."""
    if not atif.daire_key:
        return "eslesti"
    seg_daireler = ko.daire_kumesi(seg)
    if not seg_daireler:
        return "yok"
    return "eslesti" if atif.daire_key in seg_daireler else "celiski"


def teyit_et(atif, teyit_kaynaklar, bilgi_kaynaklar):
    """Statüyü belirle. Teyit EDİCİ kaynakta iz varsa TEYİTLİ (gerekirse merci
    uyarısıyla). Yoksa TEYİTSİZ; sadece çalışma evrakında (BİLGİ) iz varsa şerh."""
    ilk = None            # ilk eşleşen (etiket, seg) — iz gösterimi
    merci_ok = False      # eşleşen bir segmentte atfın dairesi doğrulandı
    merci_celiski = False # eşleşen bir segmentte FARKLI daire fiilen görüldü
    for etiket, segler in teyit_kaynaklar:
        for seg in segler:
            if not segment_eslesir(atif, seg):
                continue
            if ilk is None:
                ilk = (etiket, seg)
            md = _merci_durumu(atif, seg)
            if md == "eslesti":
                merci_ok = True
                ilk = (etiket, seg)   # merci-temiz izi tercih et
                break
            if md == "celiski":
                merci_celiski = True
        if merci_ok:
            break

    if ilk is not None:
        atif.durum = "TEYİTLİ"
        atif.kaynak, seg = ilk
        atif.kaynak_seg = _sikistir(seg, 160)
        if atif.daire_key and not merci_ok:
            atif.merci_uyari = True
            atif.merci_celiski = merci_celiski
        return

    # Teyit edici kaynakta iz YOK → TEYİTSİZ. Sadece çalışma evrakında iz var mı?
    for etiket, segler in bilgi_kaynaklar:
        for seg in segler:
            if segment_eslesir(atif, seg):
                atif.cikti_izi = etiket
                atif.cikti_seg = _sikistir(seg, 160)
                break
        if atif.cikti_izi:
            break
    atif.durum = "TEYİTSİZ"


# ───────────────────────── RAPOR ─────────────────────────
def rapor_yaz(atiflar, kutuk_var, kutuk_yolu):
    print("=" * 72)
    print("ATIF/KÜNYE DOĞRULAMA KAPISI — oa-kontrol (deterministik)")
    print("=" * 72)

    if not kutuk_var:
        print("[BLOK] KÜTÜK YOK — hiçbir atıf teyit edilemez.")
        print("       Beklenen kütük: " + kutuk_yolu)
        print("       (oa_hafiza.py init ile açılır; her MCP teyidi araç+sorgu+sonuç"
              " satırıyla işlenir.)")
        print("-" * 72)

    if not atiflar:
        print("Taslakta hukuki atıf (içtihat künyesi / mevzuat maddesi) BULUNAMADI.")
        print("Doğrulanacak künye yok — kapı AÇIK.")
        return

    ictihatlar = [a for a in atiflar if a.tur == "ictihat"]
    mevzuatlar = [a for a in atiflar if a.tur == "mevzuat"]

    def blok(baslik, grup):
        if not grup:
            return
        print(f"\n## {baslik} ({len(grup)})")
        for a in grup:
            isaret = "[TEYİTLİ] " if a.durum == "TEYİTLİ" else "[TEYİTSİZ]"
            merci_ek = "  (⚠ MERCİ DOĞRULANAMADI)" if a.merci_uyari else ""
            print(f"{isaret} (satır {a.satir_no})  {a.metin}{merci_ek}")
            if a.durum == "TEYİTLİ":
                print(f"           ↳ kaynak: {a.kaynak}")
                print(f"           ↳ iz    : {a.kaynak_seg}")
                if OCR_RE.search(a.kaynak_seg or ""):
                    print("           ⚠ OCR damgalı kaynaktan teyit — künyeyi ORİJİNALİNDEN "
                          "(RG/UYAP/Kazancı-Lexpera) ayrıca doğrula.")
                if a.merci_uyari:
                    neden = ("izde FARKLI daire var" if a.merci_celiski
                             else "izde numaralı daire yok")
                    print(f"           ⚠ MERCİ DOĞRULANAMADI — taslak mercisi "
                          f"'{a.merci}' eşleşen izde teyit edilmedi ({neden}; farklı "
                          "daire olabilir).")
                    print("             Ara statü: TEYİTLİ (⚠ MERCİ DOĞRULANAMADI — farklı "
                          "daire olabilir). Bu uyarı exit'i 1 YAPMAZ (künye izi gerçek); "
                          "doğru daire eşleşmesi oa-kontrol A-listesi muhakemesidir.")
            else:
                if a.tur == "ictihat":
                    ip = "esas/karar no"
                    ayr = f"E. {a.esas or '—'} / K. {a.karar or '—'}"
                else:
                    ip = "kanun+madde"
                    ayr = f"{'/'.join(sorted(a.kanun_anahtar))} m.{a.madde}"
                print(f"           ↳ teyit edici kaynakta (kütük/ham döküm) {ip} izi YOK "
                      f"({ayr}) — çıktıya 'teyitli' giremez.")
                if a.cikti_izi:
                    print(f"[BİLGİ]    ↳ SADECE çalışma evrakında iz var ({a.cikti_izi}) — "
                          "TEYİT SAYILMAZ (model çıktısı; halüsinasyon olabilir). Künye "
                          "kütük/ham MCP dökümüyle teyit edilmeden çıktıya giremez.")
                    print(f"             iz: {a.cikti_seg}")
            if a.ocr_taslak:
                print("           ⚠ Taslakta OCR şüphesi işareti — kaynak orijinalinden teyit şerhi.")

    blok("İÇTİHAT KÜNYELERİ", ictihatlar)
    blok("MEVZUAT ATIFLARI", mevzuatlar)

    teyitli = sum(1 for a in atiflar if a.durum == "TEYİTLİ")
    teyitsiz = len(atiflar) - teyitli
    merci_uyari = sum(1 for a in atiflar if a.merci_uyari)
    cikti_izli = sum(1 for a in atiflar if a.cikti_izi)
    print("\n" + "-" * 72)
    ozet = f"ÖZET: {len(atiflar)} atıf  |  TEYİTLİ {teyitli}  |  TEYİTSİZ {teyitsiz}"
    if merci_uyari:
        ozet += f"  |  ⚠ MERCİ DOĞRULANAMADI {merci_uyari}"
    print(ozet)
    if cikti_izli:
        print(f"NOT: {cikti_izli} teyitsiz künyenin izi YALNIZ çalışma evrakında "
              "(_oa/cikti) — model çıktısı, TEYİT SAYILMAZ (kendi-kendini-teyit deliği kapalı).")
    if teyitsiz:
        print("SONUÇ: TESLİM ENGELİ — teyitsiz atıf giderilecek ya da müvekkile 'açık uç'"
              " olarak raporlanacak (gömülmez).")
    else:
        print("SONUÇ: Tüm atıflar kütük/ham döküm izli — mekanik kapı AÇIK. "
              "(İçerik/esas-savunma + doğru daire denetimi oa-kontrol A-listesinindir.)")
        if merci_uyari:
            print("       ⚠ Ancak MERCİ DOĞRULANAMADI uyarılı künye(ler) var — daireyi "
                  "orijinal kaynaktan teyit et (exit 0'ı bloklamaz).")


# ───────────────────────── F) KÜNYE TEYİT ÖNCE-BAK ─────────────────────────
def once_bak_calistir(kunye_metni, kutuk_yolu, dokum_dizin):
    """F — bir künyenin kütükte (+ ham MCP dökümünde) ZATEN VAR olup olmadığını
    MEKANİK olarak bakar. Advisory'dir (teslim engeli DEĞİL, her hâlde exit 0):
    amaç AYNI künye için gereksiz bir tekrar MCP teyit turunu ÖNLEMEKTİR — VAR
    ise ajan yeniden MCP çağrısı yapmadan geçebilir; YOK ise MCP teyidi hâlâ
    gereklidir (bu fonksiyon teyidin YERİNE geçmez, yalnız tekrarı önler)."""
    print("=" * 72)
    print("KÜNYE TEYİT ÖNCE-BAK — oa-kontrol (advisory, teslim engeli DEĞİL)")
    print("=" * 72)

    esas, karar = ko.kunye_normalize(kunye_metni)
    daire_key = ko.daire_key(kunye_metni)
    if esas is None and karar is None:
        print(f"[HATA] Verilen metinden esas/karar no çıkarılamadı: {kunye_metni!r}")
        print("       Önce-bak yapılamıyor — künye biçimini (E./K. veya Esas/Karar) kontrol edin.")
        sys.exit(1)

    atif = Atif("ictihat", _sikistir(kunye_metni))
    atif.esas, atif.karar = esas, karar
    if daire_key:
        atif.daire_key = daire_key
        dm = ko.DAIRE_RE.search(kunye_metni)
        if dm:
            atif.merci = _sikistir(dm.group(0), 40)

    kunye_goster = f"E. {esas or '—'} / K. {karar or '—'}"
    if atif.merci:
        kunye_goster += f" / {atif.merci}"

    teyit_kaynaklar, _bilgi_kaynaklar, kutuk_var = kaynaklari_yukle(
        kutuk_yolu, dokum_dizin, None)
    if not kutuk_var:
        print(f"[YOK] Kütük dosyası yok ({kutuk_yolu}) — {kunye_goster} için önce-bak "
              "yapılamaz; MCP teyidi gerekli.")
        sys.exit(0)

    teyit_et(atif, teyit_kaynaklar, [])
    if atif.durum == "TEYİTLİ":
        print(f"[VAR] {kunye_goster} kütükte/ham dökümde ZATEN mevcut.")
        print(f"      ↳ kaynak: {atif.kaynak}")
        print(f"      ↳ iz    : {atif.kaynak_seg}")
        if atif.merci_uyari:
            print("      ⚠ MERCİ DOĞRULANAMADI — daireyi ayrıca orijinalinden teyit edin.")
        print("SONUÇ: Bu künye için AYNI MCP teyit turu GEREKSİZDİR — tekrarlanmayabilir.")
    else:
        print(f"[YOK] {kunye_goster} kütükte/ham dökümde bulunamadı.")
        print("SONUÇ: MCP teyidi gerekli — bu künye kütüğe/ham döküme HENÜZ girmemiş.")
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser(
        description="oa-kontrol atıf/künye doğrulama kapısı — teyitsiz atıf teslim engelidir.")
    ap.add_argument("taslak", nargs="?", default=None,
                    help="Taslak dilekçe/mütalaa (.md/.txt) — --once-bak modunda gerekmez")
    ap.add_argument("--once-bak", metavar="KUNYE_METNI", default=None,
                    help="F — tek bir künyenin kütükte/ham dökümde ZATEN var olup olmadığını "
                         "MEKANİK denetler (advisory, her hâlde exit 0); VARSA aynı künye için "
                         "tekrar MCP teyit turu ATLANABİLİR. `taslak` argümanı bu modda gerekmez.")
    ap.add_argument("--kok",
                    help="çalışma kökü (oa_hafiza.py/tam_tur.py/pipeline_kayit.py simetrisi); "
                         "verilirse --kutuk/--dokum-dizin/--cikti-dizin varsayılanları "
                         "<KOK>/_oa/teyit/kunye-teyit.md, <KOK>/_oa/teyit/dokum, <KOK>/_oa/cikti "
                         "olur (açıkça verilen --kutuk/--dokum-dizin/--cikti-dizin bunu ezer)")
    ap.add_argument("--kutuk", default=None,
                    help="Künye teyit kütüğü — TEYİT EDİCİ "
                         f"(varsayılan: --kok yoksa {VARSAYILAN_KUTUK}, varsa <KOK>/{VARSAYILAN_KUTUK})")
    ap.add_argument("--dokum-dizin", default=None,
                    help="Ham MCP döküm dizini — TEYİT EDİCİ ikinci kaynak "
                         f"(varsayılan: --kok yoksa {VARSAYILAN_DOKUM}, varsa <KOK>/{VARSAYILAN_DOKUM})")
    ap.add_argument("--cikti-dizin", default=None,
                    help="Çalışma evrakı dizini — BİLGİ AMAÇLI, TEYİT EDİCİ DEĞİL "
                         "(model çıktısı; geriye uyum için kabul edilir, statüyü TEYİTLİ "
                         f"YAPMAZ). (varsayılan: --kok yoksa {VARSAYILAN_CIKTI}, varsa <KOK>/{VARSAYILAN_CIKTI})")
    args = ap.parse_args()

    # --kok verilirse ve ilgili --X açıkça verilmemişse, <KOK>/_oa/... varsayılanına düş.
    # --kok verilmezse davranış ESKİSİYLE AYNI (CWD-göreli VARSAYILAN_*).
    kutuk = args.kutuk if args.kutuk is not None else (
        os.path.join(args.kok, VARSAYILAN_KUTUK) if args.kok else VARSAYILAN_KUTUK)
    dokum_dizin = args.dokum_dizin if args.dokum_dizin is not None else (
        os.path.join(args.kok, VARSAYILAN_DOKUM) if args.kok else VARSAYILAN_DOKUM)
    cikti_dizin = args.cikti_dizin if args.cikti_dizin is not None else (
        os.path.join(args.kok, VARSAYILAN_CIKTI) if args.kok else VARSAYILAN_CIKTI)

    if args.once_bak is not None:
        once_bak_calistir(args.once_bak, kutuk, dokum_dizin)
        return  # once_bak_calistir sys.exit() çağırır; buraya normalde ulaşılmaz

    if not args.taslak:
        sys.exit("HATA: taslak pozisyonel argümanı gerekli (ya da --once-bak KUNYE_METNI kullanın)")
    if not os.path.isfile(args.taslak):
        sys.exit(f"HATA: taslak bulunamadı: {args.taslak}")
    with open(args.taslak, encoding="utf-8", errors="replace") as f:
        metin = f.read()

    atiflar = atiflari_cikar(metin)
    teyit_kaynaklar, bilgi_kaynaklar, kutuk_var = kaynaklari_yukle(
        kutuk, dokum_dizin, cikti_dizin)

    if kutuk_var:
        for a in atiflar:
            teyit_et(a, teyit_kaynaklar, bilgi_kaynaklar)
    # kütük yoksa: hepsi TEYİTSİZ kalır (yapısal blok)

    rapor_yaz(atiflar, kutuk_var, kutuk)

    if not atiflar:
        sys.exit(0)  # doğrulanacak künye yok
    if not kutuk_var:
        sys.exit(1)  # kütük yok — hiçbir atıf teyit edilemez
    sys.exit(1 if any(a.durum == "TEYİTSİZ" for a in atiflar) else 0)


if __name__ == "__main__":
    main()

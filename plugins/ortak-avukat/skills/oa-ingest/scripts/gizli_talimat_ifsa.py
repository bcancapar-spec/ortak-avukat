#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
gizli_talimat_ifsa.py — GİZLİ TALİMAT İFŞASI, Faz A (v0.5.18)

NEDEN VAR: Avukat talimatı (2026-10-07): karşı tarafın evrakında insan gözünün görmediği
ama yapay zekânın okuduğu bir gizli talimat bulunduğunda, hazırlanacak dilekçeye
mahkemeye sunulabilir, olgusal bir İFŞA bölümü girsin — siber hukuk güvenliği için.
B-22 BELGE GÜVENLİK KAPISI (belge_guvenlik.py) gizli katmanı bulur ve damgalar; bu
motor o KESİN bulguları (karar BULGU) dilekçe diline çevirir. İki tehlikeyi birden
önler: (1) yanlış suçlama müvekkile zarar verir (anayasa m.6) → UYARI ve
DENETLENEMEZ düzeyindeki şüphe dilekçeye GİRMEZ, görünür ya da içeriksiz yapısal
tespitler (özel parantez, sayfa ayracı satırı, özdeş ikinci nüsha) de GİRMEZ,
niyet/suç iddiası ÜRETİLMEZ; (2) gizli talimat dilekçeyi okuyacak başka yapay zekâ
araçlarını zehirleyebilir → alıntı etiketli bir blokta, görünmez karakterleri kaçışlı,
Markdown/HTML biçimlendirmesi ve bağlantıları etkisiz biçimde aktarılır. Anayasa m.11
korunur: gizli metin UYGULANMAZ, yalnız DELİL olarak aktarılır.

KALICI KAYNAK: `_oa/metin/00-kunye.json` → `kayitlar[].belge_guvenlik`
(karar BULGU | UYARI | DENETLENEMEZ; `bulgular[]`: tur, yontem, konum, ornek,
uzunluk, alinti — kapı sürümü 1.1). Bu script kendi başına tarama YAPMAZ, ikinci bir
denetim İCAT ETMEZ: yalnız kapının kalıcı kaydını okur. `_oa`'ya YAZMAZ; yalnız
`--md` / `--json` ile verilen hedeflere atomik yazar (tmp + os.replace).

NE YAPMAZ: hukuki nitelendirme (kötü niyet, dürüstlük kuralına aykırılık, suç) —
bunlar avukatın ve Mahkemenin takdiridir; bölümü dilekçeye koyma kararı avukatındır.

Kullanım:
  python gizli_talimat_ifsa.py --kok <dava kökü> [--md <yol>] [--json <yol>]
Çıkış kodu: 0 = ifşa edilecek BULGU yok · 1 = BULGU var, bölüm üretildi ·
            3 = bulgular okunamadı/denetlenemedi (fail-closed; "bulgu yok" DENMEZ) —
            beklenmedik iç hata da 3'tür (1 "BULGU var" demektir, hata değil).
JSON (sort_keys): {"arac", "surum", "karar": IFSA_VAR|IFSA_YOK|DENETLENEMEDI,
  "kaynaklar": [{"rol","yol","sha8"}], "bulgular": [...], "dilekce_bolumu_md",
  "ic_not": [...], "yer_tutucular": [...], "dayanak": [...]}
Python API: ifsa_uret(kok) -> dict (JSON ile aynı içerik).

Determinizm: aynı `_oa` → bayt-özdeş çıktı; zaman damgası, rastgelelik, sıra
bağımlılığı yok (kayıtlar künye sırasıyla — no sayısal, kaynak — dizilir).
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import hashlib
import importlib.util
import json
import os
import re
import unicodedata

ARAC = "gizli_talimat_ifsa"
SURUM = "1.1"
KARAR_VAR, KARAR_YOK, KARAR_DENETLENEMEDI = "IFSA_VAR", "IFSA_YOK", "DENETLENEMEDI"
CIKIS = {KARAR_YOK: 0, KARAR_VAR: 1, KARAR_DENETLENEMEDI: 3}
KUNYE_GORECE = "metin/00-kunye.json"          # `_oa`'ya göre, POSIX
AZAMI_KUNYE_BAYT = 256 * 1024 * 1024          # künye büyük külliyatta büyür; sınır yalnız kaza/bomba sigortası
ALINTI_SINIRI = 1500                          # dilekçeye giren alıntı (karakter) — aşan kısım kırpılır, TOPLAM yazılır
ORNEK_SINIRI = 160                            # belge_guvenlik._kirp varsayılanı: 1.0 kaydının kırpma eşiği
YER_TUTUCU_SUNAN = "[SUNAN TARAF — avukat teyidi]"
SUNAN_KARSI = "karsi-taraf"                   # künye kaydında `sunan_taraf` alanının tek tanınan değeri
KAHIN_TUR = "kahin-devre-disi"
# Kâhin kapalıyken yalnız SEZGİSEL kalan PDF gerekçeleri (bkz. Ruling, references/gizli-talimat-ifsasi.md)
SEZGISEL_ISARETLER = ("kontrast", "alfa", "örtü", "zemin")
# Ö-1: AGIR ama GÖRÜNÜR ya da İÇERİKSİZ yapısal tespitler — gizli metin göstermez, dilekçeye girmez
GORUNUR_YAPISAL = ("damga-taklidi", "isaret-taklidi")
TUTULMA_KAHIN, TUTULMA_YAPISAL = KAHIN_TUR, "gorunur-yapisal"

# Resmî metinden okunan dayanaklar — Yargı PRO `mevzuat_getir`, 2026-10-07 (mevzuat.gov.tr).
# Bölümde ANILAN her madde burada kayıtlı olmalıdır; okunmamış madde anılmaz (testle kilitli).
DAYANAK = [
    {"kanun": "6100 sayılı Hukuk Muhakemeleri Kanunu", "madde": "29",
     "baslik": "Dürüst davranma ve doğruyu söyleme yükümlülüğü",
     "metin": "(1) Taraflar, dürüstlük kuralına uygun davranmak zorundadırlar. (2) Taraflar, davanın "
              "dayanağı olan vakıalara ilişkin açıklamalarını gerçeğe uygun bir biçimde yapmakla yükümlüdürler.",
     "kaynak": "mevzuat.gov.tr — mevzuatgov:kanun:5:6100:m29",
     "teyit": "Yargı PRO mevzuat_getir, 2026-10-07"},
    {"kanun": "6100 sayılı Hukuk Muhakemeleri Kanunu", "madde": "199", "baslik": "Belge",
     "metin": "(1) Uyuşmazlık konusu vakıaları ispata elverişli yazılı veya basılı metin, senet, çizim, plan, "
              "kroki, fotoğraf, film, görüntü veya ses kaydı gibi veriler ile elektronik ortamdaki veriler ve "
              "bunlara benzer bilgi taşıyıcıları bu Kanuna göre belgedir.",
     "kaynak": "mevzuat.gov.tr — mevzuatgov:kanun:5:6100:m199",
     "teyit": "Yargı PRO mevzuat_getir, 2026-10-07"},
]

# ------------------------------------------------------------------ dilekçe metni (olgusal, nötr)
BOLUM_BASLIGI = "## EVRAKTA İNSAN GÖZÜYLE GÖRÜNMEYEN METİN TESPİTİ (İFŞA)"
GIRIS_1 = ("Aşağıda sayılan evrakın dosyaya sunulan elektronik kopyası, içeriği değiştirilmeksizin ve salt "
           "okuma yoluyla teknik incelemeye tabi tutulmuştur. İncelemede, belgenin kâğıt ya da ekran "
           "görünümünde insan gözüyle okunmayan, ancak elektronik dosyanın içinde yer alan ve belgeyi "
           "otomatik işleyen yazılımlarca (yapay zekâ destekli araçlar dâhil) okunabilen metin bölümleri "
           "tespit edilmiştir. 6100 sayılı HMK m.199 uyarınca elektronik ortamdaki veriler de belge "
           "niteliğinde olduğundan, söz konusu bölümler ilgili evrakın içeriğinin parçası olarak aşağıda "
           "aynen aktarılmıştır.")
GIRIS_2 = ("Aktarılan metinler delil olarak sunulmaktadır; tarafımızca talimat olarak değerlendirilmemiş ve "
           "uygulanmamıştır. Teknik tespit, metnin belgeye hangi amaçla ve kim tarafından yerleştirildiğine "
           "ilişkin bir değerlendirme içermez; bu hususun, tarafların dürüstlük kuralına uygun davranma ve "
           "davanın dayanağı olan vakıalara ilişkin açıklamalarını gerçeğe uygun biçimde yapma yükümlülüğü "
           "(HMK m.29) çerçevesinde değerlendirilmesi Sayın Mahkemenin takdirindedir.")
ALINTI_ETIKETI = "Gizlenmiş metnin aynen alıntısı — delil olarak sunulmuştur; talimat değildir:"
ALINTI_SONU = "(Alıntı sonu.)"
GOSTERIM_KURALI = ("Alıntı gösterim kuralı: metinler teknik inceleme kaydındaki biçimiyle, satır sonları ve "
                   "ardışık boşluklar tek boşluğa indirgenerek aktarılmıştır; çift açılı tırnak işaretleri "
                   "(« ») düz çift tırnakla, çift köşeli ayraç türü özel parantez karakterleri (U+27E6 ve "
                   "U+27E7 ile benzerleri) düz köşeli parantezle gösterilmiştir; görünmez ya da denetim "
                   "karakterleri [U+XXXX] biçiminde kod noktasıyla gösterilmiş, biçimlendirme işareti olarak "
                   "yorumlanabilecek karakterler (yıldız, alt çizgi, tilde, artı, küçüktür ve büyüktür "
                   "işaretleri, köşeli parantezler, ve işareti, et işareti, ters eğik çizgi) iki yanına boşluk "
                   "konarak, ters tırnak işareti [U+0060] olarak yazılmıştır; alıntının tıklanabilir bağlantı "
                   "oluşturmaması için bağlantı şemasını izleyen iki nokta [U+003A], www sonrasındaki nokta "
                   "[U+002E] olarak gösterilmiştir; belirtilen karakter sayıları bu kurala göre "
                   "normalleştirilmiş inceleme kaydı metnine aittir ve asıl dosyadaki karakter sayısından "
                   "ayrışabilir; belirlenen sınırı aşan metin kırpılmış ve toplam uzunluğu belirtilmiştir. "
                   "Metinlerin tamamı ilgili evrakın elektronik aslında mevcuttur.")

# ------------------------------------------------------------------ kardeş kapı modülü
_BG = []


def _bg():
    """Kardeş `belge_guvenlik.py` (B-22) — AGIR tür kümesi ve damga nötrleyici TEK KAYNAKTAN okunur
    (ikinci bir kopya iki kaynak demektir). Yüklenemezse çağıran DENETLENEMEDİ der."""
    if _BG:
        return _BG[0]
    yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), "belge_guvenlik.py")
    spec = importlib.util.spec_from_file_location("oa_belge_guvenlik_ifsa", yol)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    _BG.append(m)
    return m


class IfsaHatasi(Exception):
    """Bulgu kaydı okunamadı/denetlenemedi — fail-closed (çıkış 3)."""


# ------------------------------------------------------------------ künye
def kunye_oku(kok):
    """`<kok>/_oa/metin/00-kunye.json` → (künye, kaynaklar). Yoksa/bozuksa/şema dışıysa IfsaHatasi:
    ingest koşmamış ya da kayıt okunamıyorsa 'bulgu yok' DENMEZ."""
    if not os.path.isdir(kok):
        raise IfsaHatasi("dava kökü dizin değil: %s" % kok)
    oa = os.path.join(kok, "_oa")
    if not os.path.isdir(oa):
        raise IfsaHatasi("_oa dizini yok — oa_ingest.py koşmamış; belge güvenlik kaydı okunamadı")
    yol = os.path.join(oa, *KUNYE_GORECE.split("/"))
    if not os.path.isfile(yol):
        raise IfsaHatasi("künye yok (_oa/%s) — oa_ingest.py TAM koşusu yapılmamış; "
                         "belge güvenlik kaydı okunamadı" % KUNYE_GORECE)
    try:
        if os.path.getsize(yol) > AZAMI_KUNYE_BAYT:
            raise IfsaHatasi("künye %d MB sınırını aşıyor — okunmadı" % (AZAMI_KUNYE_BAYT // 2**20))
        with open(yol, "rb") as f:
            ham = f.read()
    except OSError as e:
        raise IfsaHatasi("künye okunamadı: %s" % e)
    try:
        kunye = json.loads(ham.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        raise IfsaHatasi("künye bozuk (JSON/UTF-8): %s" % str(e)[:120])
    if not isinstance(kunye, dict) or not isinstance(kunye.get("kayitlar"), list):
        raise IfsaHatasi("künye şema dışı — {\"kayitlar\": [...]} bekleniyor")
    kaynaklar = [{"rol": "kunye", "yol": KUNYE_GORECE, "sha8": hashlib.sha256(ham).hexdigest()[:8]}]
    return kunye, kaynaklar


def _sunan_taraf(kayit):
    """Kalıcı kayıttan sunan taraf. Bugün künyeyi yazan hiçbir adım bu alanı DOLDURMAZ (Faz B bağlama
    noktası: `kayit["sunan_taraf"] = "karsi-taraf"`); tanınmayan/eksik değer → None → yer tutucu
    (fail-closed: tahminle 'karşı taraf' yazılmaz)."""
    return SUNAN_KARSI if kayit.get("sunan_taraf") == SUNAN_KARSI else None


def _sira_anahtari(k):
    """Künye sırası: `no` SAYISAL (dizgi sıralaması '1000' < '999' yapardı), sayı olmayan/boş `no` sona;
    eşitlikte kaynak adı. Deterministik. `isdecimal()` KULLANILIR (Y-2): `isdigit()` üst simge
    rakamları ('²') da kabul eder ama `int()` onları çözmez — tek bozuk `no` K-1 ağına düşüp
    TÜM ifşayı DENETLENEMEDİ'ye çeviriyordu; `isdecimal()` ile `int()` birebir uyumludur."""
    no = str(k.get("no") or "")
    return ((0, int(no)) if no.isdecimal() else (1, 0)), no, str(k.get("kaynak") or "")


def _bulgu_normalize(b):
    """Künye bulgusunu dizge alanlara indirger. Şema dışı (tür dizge değil; metin alanları dizge/None
    değil; uzunluk tam sayı değil) → None: istisna yerine GÖRÜNÜR dışlama (K-1 — beklenmedik istisna
    çıkış kodu 1 = 'BULGU var' ile çakışıyordu)."""
    if not isinstance(b, dict) or not isinstance(b.get("tur"), str) or not b["tur"]:
        return None
    for alan in ("yontem", "konum", "ornek", "alinti"):
        v = b.get(alan)
        if v is not None and not isinstance(v, str):
            return None
    uz = b.get("uzunluk")
    if uz is not None and (isinstance(uz, bool) or not isinstance(uz, int)):
        return None
    return {"tur": b["tur"], "yontem": b.get("yontem") or "", "konum": b.get("konum") or "",
            "ornek": b.get("ornek") or "", "alinti": b.get("alinti"), "uzunluk": uz}


# ------------------------------------------------------------------ metin güvenliği
_KACIS_KATEGORI = frozenset({"Cc", "Cf", "Co", "Cn", "Cs", "Zl", "Zp", "Zs"})
# Kategorisi harf/işaret olduğu için kaçmayan ama görünmeyen kod noktaları
_GORUNMEZ_EK = frozenset({0x034F, 0x115F, 0x1160, 0x17B4, 0x17B5, 0x180E, 0x2800, 0x3164, 0xFFA0})
_BICIM_ALINTI = frozenset("*_~+<>[]&@\\")    # alıntıda iki yanına boşluk konan biçim/bağlantı karakterleri
_BICIM_AD = frozenset("*<>[]&\\")           # evrak adında her zaman aralanan (alt çizgi/tilde koşullu)
_ASCII_BOSLUK = re.compile(r"[ \t\r\n\f\v]+")
# K-3: GFM önizleme (GitHub/VS Code) çıplak URL'yi ve www.'yi tıklanabilir yapar — saldırganın adresi
# dilekçeden tıklanamaz: şema sonrası ':' ve www sonrası '.' kod noktasıyla yazılır (karakter silinmez).
_BAGLANTI_SEMA_RE = re.compile(r"(?i)\b(https?|ftps?|mailto|xmpp):")
_WWW_RE = re.compile(r"(?i)\bwww\.")


def _gorunur_kacis(s):
    """Görünmez/denetim karakterleri `[U+XXXX]` olur — ham kopyalanmaz (dilekçeyi okuyan araç da görmez,
    mahkeme de). Olağan boşluk (U+0020) dokunulmaz."""
    out = []
    for c in s:
        o = ord(c)
        if c == " ":
            out.append(c)
        elif (unicodedata.category(c) in _KACIS_KATEGORI or o in _GORUNMEZ_EK
              or 0xFE00 <= o <= 0xFE0F or 0xE0100 <= o <= 0xE01EF):
            out.append("[U+%04X]" % o)
        else:
            out.append(c)
    return "".join(out)


def _bicim_notr(s, kume):
    """Markdown/HTML biçimlendirmesini ETKİSİZ kılar — karakter silinmez, görünür kalır: biçim karakteri
    iki yanına boşluk alır (ne CommonMark ne oa-dilekce dönüştürücüsü boşlukla çevrili işareti vurgu/etiket/
    bağlantı sayar); ters tırnak `[U+0060]` olur (dönüştürücü ters tırnak çiftini SİLER — delil kaybı olurdu).
    Tek satır + «» içinde başladığı için satır başı yapıları (başlık, liste, tablo, alıntı) tetiklenemez."""
    out = []
    for c in s:
        if c == "`":
            out.append("[U+0060]")
        elif c in kume:
            out.append(" %s " % c)
        else:
            out.append(c)
    return re.sub(r" {2,}", " ", "".join(out)).strip()


def _ad_bicim_notr(s):
    """Evrak adı için nötrleme (K-4): `*<>[]&\\` her zaman aralanır; alt çizgi yalnız sözcük sınırında
    (sözcük içi `cevap_dilekcesi` CommonMark'ta vurgu değildir — ad bozulmaz, `__ad__` kalın olmaz);
    tilde yalnız koşu hâlinde (`~~ad~~` üstü çizili olmaz); ters tırnak `[U+0060]`."""
    out, n = [], len(s)
    for i, c in enumerate(s):
        onceki = s[i - 1] if i else ""
        sonraki = s[i + 1] if i + 1 < n else ""
        if c == "`":
            out.append("[U+0060]")
        elif c in _BICIM_AD:
            out.append(" %s " % c)
        elif c == "_" and not (onceki.isalnum() and sonraki.isalnum()):
            out.append(" _ ")
        elif c == "~" and (onceki == "~" or sonraki == "~"):
            out.append(" ~ ")
        else:
            out.append(c)
    return re.sub(r" {2,}", " ", "".join(out)).strip()


def _baglanti_notr(s):
    return _WWW_RE.sub("www[U+002E]", _BAGLANTI_SEMA_RE.sub(r"\1[U+003A]", s))


def _duzlestir(s):
    """Künyeden gelen metni dilekçeye taşımadan önce: damga benzeri parantezler nötr (⟦⟧ → []), «» → ",
    ASCII boşluk koşuları tek boşluk. (Kapı bunu zaten yapar; burada yeniden yapmak eski/yabancı kayda
    karşı sigortadır.) Bu ikameler mahkemeye gösterim kuralında açıkça söylenir (K-2)."""
    s = _bg()._notrle(str(s or "")).replace("«", "\"").replace("»", "\"")
    return _ASCII_BOSLUK.sub(" ", s).strip()


def _alinti_metni(ham):
    return _gorunur_kacis(_baglanti_notr(_bicim_notr(_duzlestir(ham), _BICIM_ALINTI)))


def _ad_metni(ham):
    return _gorunur_kacis(_ad_bicim_notr(_duzlestir(ham)))


def _sayi(n):
    """Türkçe binlik ayraç: 1500 → '1.500'."""
    return "{:,}".format(int(n)).replace(",", ".")


def _evrak_adi_goster(kaynak):
    """Dilekçede evrak DOSYADAKİ adıyla anılır; arşiv üyesi `paket.eyp::a/ek.txt` okunur biçimde."""
    k = str(kaynak or "")
    if "::" in k:
        dis, ic = k.split("::", 1)
        return "«%s» arşivi içindeki «%s»" % (_ad_metni(dis), _ad_metni(ic))
    return "«%s»" % _ad_metni(k)


# ------------------------------------------------------------------ avukat dili
def _sayi_tr(v):
    return str(v).replace(".", ",")


def _yontem_aciklama(tur, yontem):
    """Kapının teknik gerekçesini (kontrast=1.00;punto=1 · görünmez kip · gizli(vanish) …) avukat diline çevirir.
    Ham gerekçe dilekçeye GEÇMEZ (iç iz taşıyabilir); yalnız tanınan kalıplar ve sayıları."""
    tur = str(tur or "")
    y = str(yontem or "")
    yk = y.lower()
    p = []
    if tur == "silinmis-metin" or "silinmiş metin" in yk:
        p.append("silinmiş izli değişiklik (Word'de silinmiş görünen, ancak dosyada duran metin)")
    if tur == "unicode-tag":
        m = re.search(r"TAG karakteri=(\d+)", y)
        p.append("görünmez Unicode TAG karakterleriyle kodlanmış metin%s (ekranda ve kâğıtta hiçbir iz bırakmaz; "
                 "çözümü aşağıdadır)" % ((" — %s karakter" % m.group(1)) if m else ""))
    if tur == "bidi":
        p.append("yazı yönünü değiştiren görünmez denetim karakteri (ekranda görünen sıra ile dosyada okunan "
                 "sıra farklı)")
    if tur == "arsiv-nushasi":
        if "özdeş" in yk:
            p.append("dosya arşivinde aynı içeriğin ikinci nüshası (içerikleri özdeş)")
        elif "farklı" in yk:
            p.append("dosya arşivinde aynı içeriğin ikinci, farklı nüshası (ekranda gösterilen nüsha ile dosyada "
                     "duran nüsha ayrışıyor; yalnız bir nüshada bulunan satırlar aşağıdadır)")
        elif "beklenen yerde değil" in yk:
            p.append("dosya arşivinde içerik beklenen yerde değil (ikinci bir içerik nüshası)")
        else:
            p.append("dosya arşivinde birden çok içerik nüshası")
    if tur == "ust-veri-talimat":
        p.append("belge üst verisinde (belge özellikleri/yorum alanı) yazı — belgenin görünür gövdesinde yer almaz")
    if tur == "ocr-katmani-talimat":
        p.append("taranmış görüntünün üstündeki görünmez metin katmanında yazı")
    if tur == "damga-taklidi":   # Ö-1: görünür yapısal tespit — dilekçeye girmez; iç not/JSON için nötr ad
        p.append("görünür metinde çift köşeli ayraç türü özel parantez karakterleri (yapısal tespit; gizli metin "
                 "değildir)")
    if tur == "isaret-taklidi":
        p.append("görünür metinde sayfa ayracı biçiminde satır (yapısal tespit; gizli metin değildir)")
    if "vanish" in yk:
        p.append("Word gizli metin biçimi (ekranda ve çıktıda görünmez)")
    m = re.search(r"kontrast(?:=([\d.]+))?", yk)
    if m:
        deger = (" — kontrast oranı %s" % _sayi_tr(m.group(1))) if m.group(1) else ""
        zemin = "çizilmiş zemin" if "(zemin)" in yk else "zemin"
        p.append("%s rengiyle ayrışmayan yazı rengi%s (ör. beyaz zemine beyaz yazı)" % (zemin, deger))
    m = re.search(r"punto(?:=([\d.]+))?", yk)
    if m:
        p.append("okunamayacak kadar küçük yazı%s" % ((" (%s punto)" % _sayi_tr(m.group(1))) if m.group(1) else ""))
    m = re.search(r"\balfa(?:=(\d+))?", yk)
    if m:
        p.append("saydam ya da neredeyse saydam yazı%s" % ((" (opaklık %s/255)" % m.group(1)) if m.group(1) else ""))
    if "görünmez kip" in yk:
        p.append("PDF görünmez yazı kipi (metin sayfaya gömülü, ancak çizilmiyor)")
    if "örtü altında farklı yazı" in yk:
        p.append("yazının üstüne opak kutu çizilip kutunun üstüne farklı bir yazı basılmış (ekranda görünen metin "
                 "ile altta duran metin farklı)")
    elif "örtülü" in yk:
        p.append("yazının üstüne sonradan opak kutu çizilmiş (karartma/örtü)")
    if "görsel zemin üstünde seçilemeyen yazı" in yk:
        p.append("görsel zemin üstünde seçilemeyen yazı")
    if "sayfa dışı" in yk:
        p.append("sayfa sınırının dışına yerleştirilmiş yazı")
    m = re.search(r"yatay ölçek=%(\d+)", y)
    if m:
        p.append("yatay ölçeği okunamayacak düzeye daraltılmış yazı (%%%s)" % m.group(1))
    m = re.search(r"harf aralığı=(-?\d+)", y)
    if m:
        p.append("harfleri üst üste bindirilmiş yazı (harf aralığı %s twip)" % m.group(1))
    if "alan kodu" in yk:
        p.append("Word alan kodu içine yerleştirilmiş yazı (belgede görünmez)")
    if "veri bloğunda" in yk:
        p.append("UYAP UDF veri bloğunda yazı (editörde görünmez alan)")
    if "html yorumunda" in yk:
        p.append("HTML yorumunda yazı (sayfada görünmez)")
    if "bloğunda talimat dili" in yk:
        p.append("HTML betik/stil bloğunda yazı (sayfada görünmez)")
    if "gizli biçimli öğe" in yk:
        p.append("gizli biçimli HTML öğesi içinde yazı")
    if "küçük/soluk/görsel altındaki" in yk:
        p.append("küçük, soluk ya da görsel altında kalan yazı")
    if "açık renkli yazı" in yk:
        p.append("açık renkli yazı")
    if "küçük görsel üstünde" in yk:
        p.append("küçük bir görselin üstünde")
    if "konumu gövdede bulunamadı" in yk:
        p.append("metin dosya yapısından tespit edildi (görünür gövdede konumlandırılamadı)")
    if tur in ("gizli-talimat", "ocr-katmani-talimat", "ust-veri-talimat"):
        p.append("metin, belgeyi otomatik işleyen yazılımlara yönelik yönerge kalıbı içermektedir "
                 "(otomatik kalıp eşleşmesi)")
    tekil = []
    for x in p:
        if x not in tekil:
            tekil.append(x)
    return "; ".join(tekil) if tekil else "biçimsel gizleme (teknik ayrıntı inceleme kaydında)"


_KONUM_SABIT = {"veri bloğu": "UYAP veri bloğu (editörde görünmez alan)",
                "EXIF/XMP": "görüntü üst verisi (EXIF/XMP)", "metin": "metin gövdesi", "yorum": "HTML yorumu",
                "öğe": "gizli HTML öğesi", "görünür metin": "görünür metin",
                "content.xml": "belge içeriği (content.xml)", "word/document.xml": "belge gövdesi (word/document.xml)",
                "script": "HTML betik bloğu", "style": "HTML stil bloğu", "noscript": "HTML noscript bloğu",
                "template": "HTML template bloğu"}


def _konum_aciklama(konum, tur=None):
    """Kapının konum dizgesini avukat diline çevirir — TÜR duyarlı (Ö-1): 'belge' yalnız üst-veri
    tespitinde üst veridir; gövdedeki yapısal tespitte belgenin bütünüdür."""
    k = str(konum or "").strip()
    tur = str(tur or "")
    m = re.fullmatch(r"sayfa (\d+)", k)
    if m:
        return "sayfa %s" % m.group(1)
    m = re.fullmatch(r"content\.xml ofset (\d+)-(\d+)", k)
    if m:
        return "belge içeriği (content.xml), %s–%s. karakterler" % (m.group(1), m.group(2))
    m = re.fullmatch(r"paragraf (\d+)", k)
    if m:
        return "%s. paragraf (word/document.xml)" % m.group(1)
    if k == "belge":
        return "belge özellikleri (üst veri)" if tur == "ust-veri-talimat" else "belgenin bütünü"
    if k in _KONUM_SABIT:
        return _KONUM_SABIT[k]
    if not k:
        return "konum kayıtta belirtilmemiş"
    # Tanınmayan konum evraktan gelen ad olabilir (arşiv girdisi, üst veri parçası): tam nötrlenir.
    if tur == "ust-veri-talimat":
        return "üst veri alanı «%s»" % _alinti_metni(k)
    return "«%s»" % _alinti_metni(k)


def _dogrulama_adimlari(tur, yontem, kaynak):
    """İç not: avukat tespiti ASIL evrakta kendi gözüyle doğrular (dilekçeye GİRMEZ)."""
    yk = str(yontem or "").lower()
    uz = os.path.splitext(str(kaynak or "").split("::")[-1])[1].lower()
    if tur in ("unicode-tag", "bidi"):
        return ("metni bir Unicode kod noktası görüntüleyicisine yapıştırın (TAG: U+E0000–U+E007F; yön "
                "karakterleri: U+202D/U+202E)")
    if tur == "arsiv-nushasi":
        return "dosyanın uzantısını .zip yapıp açın; aynı adlı ikinci girdiyi (content.xml/document.xml) karşılaştırın"
    if tur == "ust-veri-talimat":
        return "Dosya → Özellikler (PDF: Belge Özellikleri; görüntü: EXIF/XMP) alanlarını okuyun"
    if tur == "silinmis-metin" or "silinmiş" in yk:
        return "Word → Gözden Geçir → İzleme → 'Tüm İşaretler' görünümünü seçin; silinen metin üstü çizili görünür"
    if "vanish" in yk:
        return ("Word → Dosya → Seçenekler → Görüntü → 'Gizli metin' kutusunu işaretleyin ve ¶ (tüm biçimlendirme "
                "işaretlerini göster) ile bakın")
    if "veri bloğ" in yk:
        return "UDF'yi .zip olarak açıp content.xml içinde CDATA dışındaki alanları okuyun"
    if "html" in yk or uz in (".html", ".htm"):
        return "sayfa kaynağını (Ctrl+U) görüntüleyin"
    if uz == ".pdf":
        return ("PDF okuyucuda Ctrl+A ile tümünü seçin ya da metni kopyalayıp düz metin editörüne yapıştırın; "
                "görünmez/beyaz yazı seçimde ve yapıştırmada belirir")
    return ("UYAP Editörü/Word'de Ctrl+A ile tümünü seçin (seçim vurgusu zeminle aynı renkteki ya da çok küçük "
            "yazıyı gösterir); zemin rengini değiştirin ya da metni düz metin editörüne yapıştırın")


def _sezgisel_mi(yontem):
    yk = str(yontem or "").lower()
    return any(i in yk for i in SEZGISEL_ISARETLER)


# ------------------------------------------------------------------ bulgu → dilekçe satırları
def _alinti_hazirla(b):
    """Künye bulgusundan dilekçe alıntısı: (gösterilen_metin, uzunluk|None, gösterilen_karakter, kırpıldı,
    uzunluk_kayıtlı). 1.0 kaydında (`uzunluk` yok) kırpılmış örneğin üç noktası yük DEĞİLDİR, atılır."""
    ornek = str(b.get("ornek") or "")
    ham = str(b.get("alinti") or ornek)
    uzunluk = b.get("uzunluk")
    kayitli = isinstance(uzunluk, int) and not isinstance(uzunluk, bool) and uzunluk >= 0
    kapi_kirpmasi = len(ornek) == ORNEK_SINIRI and ornek.endswith("…") and not b.get("alinti")
    if not kayitli:
        uzunluk = None
        kirpildi = kapi_kirpmasi
        if kapi_kirpmasi:
            ham = ornek[:-1]            # kapının kırpma işareti yük değildir
    else:
        if kapi_kirpmasi and uzunluk > ORNEK_SINIRI - 1:
            ham = ornek[:-1]            # uzunluk var ama uzun alıntı yok (elle düzenlenmiş kayıt): işaret atılır
        kirpildi = uzunluk > len(ham)
    ham = _duzlestir(ham)
    if len(ham) > ALINTI_SINIRI:
        ham = ham[:ALINTI_SINIRI]
        kirpildi = True
    return _alinti_metni(ham), uzunluk, len(ham), kirpildi, kayitli


def _uzunluk_satiri(uzunluk, gosterilen, kirpildi, kayitli):
    if not kayitli:
        if kirpildi:
            return ("- Tespit edilen metnin toplam uzunluğu inceleme kaydında bulunmamaktadır; aşağıda kayıttaki ilk "
                    "%s karakteri aktarılmıştır (kalan kısım kırpılmıştır; metnin tamamı evrakın elektronik "
                    "aslındadır)." % _sayi(gosterilen))
        return "- Tespit edilen metnin uzunluğu: %s karakter; tamamı aşağıda aktarılmıştır." % _sayi(gosterilen)
    if kirpildi:
        return ("- Tespit edilen metnin toplam uzunluğu: %s karakter; aşağıda ilk %s karakteri aktarılmıştır "
                "(kalan kısım kırpılmıştır; metnin tamamı evrakın elektronik aslındadır)."
                % (_sayi(uzunluk), _sayi(gosterilen)))
    return "- Tespit edilen metnin uzunluğu: %s karakter; tamamı aşağıda aktarılmıştır." % _sayi(uzunluk)


def _tespit_bloku(no_evrak, no_tespit, b, alinti, uzunluk, gosterilen, kirpildi, kayitli):
    satirlar = ["#### %d.%d Tespit" % (no_evrak, no_tespit),
                "- Tespit yeri: %s" % _konum_aciklama(b["konum"], b["tur"]),
                "- Gizleme biçimi: %s" % _yontem_aciklama(b["tur"], b["yontem"])]
    if alinti:
        satirlar.append(_uzunluk_satiri(uzunluk, gosterilen, kirpildi, kayitli))
        satirlar += ["", ALINTI_ETIKETI, "", "> «%s»" % alinti, "", ALINTI_SONU]
    else:
        satirlar.append("- Bu tespitte alıntılanacak ayrı bir metin bulunmamaktadır; tespit, dosyanın yapısına "
                        "ilişkindir.")
    return satirlar


def _json_bulgu(k, kaynak, sunan, b, girdi, neden):
    alinti, uzunluk, gosterilen, kirpildi, kayitli = _alinti_hazirla(b)
    return {"evrak": kaynak, "evrak_adi": str(k.get("ad") or ""), "no": k.get("no"), "sunan_taraf": sunan,
            "tur": b["tur"], "yontem": b["yontem"], "konum": b["konum"],
            "yontem_aciklama": _yontem_aciklama(b["tur"], b["yontem"]),
            "konum_aciklama": _konum_aciklama(b["konum"], b["tur"]), "alinti": alinti, "uzunluk": uzunluk,
            "gosterilen": gosterilen, "kirpildi": kirpildi, "uzunluk_kayitli": kayitli,
            "dilekceye_girdi": girdi, "tutulma_nedeni": neden}


def _bos_sonuc():
    return {"arac": "gizli_talimat_ifsa", "surum": SURUM, "karar": KARAR_YOK, "kaynaklar": [], "bulgular": [],
            "dilekce_bolumu_md": "", "ic_not": [], "yer_tutucular": [], "dayanak": [dict(d) for d in DAYANAK]}


def _denetlenemedi(sonuc, neden, kaynaklar=None):
    """Kısmi sonuç YAYILMAZ: bulgular/md/yer tutucular sıfırlanır; neden iç notta."""
    sonuc.update(karar=KARAR_DENETLENEMEDI, bulgular=[], dilekce_bolumu_md="", yer_tutucular=[],
                 kaynaklar=list(kaynaklar or []), ic_not=["DENETLENEMEDİ: %s — 'bulgu yok' DENMEZ." % neden])
    return sonuc


# ------------------------------------------------------------------ ana üretim
def _isle(sonuc, kunye, kaynaklar):
    sonuc["kaynaklar"] = kaynaklar
    agir = _bg().AGIR
    kayitlar = [k for k in kunye["kayitlar"] if isinstance(k, dict)]
    atlanan = len(kunye["kayitlar"]) - len(kayitlar)
    kayitlar.sort(key=_sira_anahtari)
    ic_not, bulgular, bloklar, yer_tutucular = [], [], [], set()
    if atlanan:
        ic_not.append("%d künye kaydı şema dışı (nesne değil) — değerlendirilemedi, dilekçeye GİRMEDİ." % atlanan)
    for k in kayitlar:
        r = k.get("belge_guvenlik")
        if not r:
            continue
        kaynak = str(k.get("kaynak") or k.get("ad") or "?")
        ad = _evrak_adi_goster(kaynak)
        if not isinstance(r, dict):
            ic_not.append("%s: belge güvenlik kaydı şema dışı — dilekçeye GİRMEDİ; evrakı yeniden tarayın." % ad)
            continue
        karar = r.get("karar")
        ham_bulgular = r.get("bulgular") if isinstance(r.get("bulgular"), list) else []
        if karar != "BULGU":
            ilk = next((nb for nb in (_bulgu_normalize(b) for b in ham_bulgular) if nb), None)
            if karar == "UYARI":
                ic_not.append("%s: karar UYARI — dilekçeye GİRMEDİ (görünür metinde yapay zekâya hitap eden dil ya da "
                              "görünmez karakter; gizli katman kesinleşmedi).%s"
                              % (ad, (" İlk işaret: %s — %s%s" % (ilk["tur"], _konum_aciklama(ilk["konum"], ilk["tur"]),
                                                                  (" · «%s»" % _alinti_metni(ilk["ornek"]))
                                                                  if ilk["ornek"] else "")) if ilk else ""))
            else:
                ic_not.append("%s: karar %s — dilekçeye GİRMEDİ; temiz SAYILMAZ: %s. Evrakı orijinalden kontrol "
                              "edin ya da yeniden tarayın." % (ad, karar or "?", r.get("denetlenemedi") or
                                                                  "tarama tamamlanamadı"))
            continue
        kahin_kapali = any(isinstance(b, dict) and b.get("tur") == KAHIN_TUR for b in ham_bulgular)
        sunan = _sunan_taraf(k)
        girenler, tutulanlar, yapisal, disi, sema_disi = [], [], [], [], 0
        for b in ham_bulgular:
            nb = _bulgu_normalize(b)
            if nb is None:
                sema_disi += 1
                continue
            tur = nb["tur"]
            if tur not in agir:
                if tur != KAHIN_TUR:
                    disi.append(nb)
                continue
            if tur in GORUNUR_YAPISAL or (tur == "arsiv-nushasi" and not nb["ornek"].strip()):
                yapisal.append(nb)          # Ö-1: görünür ya da içeriksiz — gizli metin göstermez
            elif kahin_kapali and _sezgisel_mi(nb["yontem"]):
                tutulanlar.append(nb)       # Ruling: kâhinsiz sezgisel gerekçe
            else:
                girenler.append(nb)
        if girenler:
            no_evrak = len(bloklar) + 1
            satirlar = ["### %d. Evrak: %s" % (no_evrak, ad),
                        "- Sunan taraf: %s" % ("karşı tarafça sunulan evrak" if sunan == SUNAN_KARSI
                                               else YER_TUTUCU_SUNAN)]
            if sunan != SUNAN_KARSI:
                yer_tutucular.add(YER_TUTUCU_SUNAN)
            if len(girenler) > 1:
                satirlar.append("- Tespit sayısı: %d" % len(girenler))
            for i, nb in enumerate(girenler, 1):
                alinti, uzunluk, gosterilen, kirpildi, kayitli = _alinti_hazirla(nb)
                satirlar.append("")
                satirlar += _tespit_bloku(no_evrak, i, nb, alinti, uzunluk, gosterilen, kirpildi, kayitli)
                bulgular.append(_json_bulgu(k, kaynak, sunan, nb, True, None))
                if not kayitli and nb["ornek"]:
                    ic_not.append("%s: tespit %d.%d — toplam uzunluk kayıtta yok (eski kapı sürümü 1.0); alıntı "
                                  "kayıttaki örnekle sınırlı. Evrakı güncel kapıyla yeniden tarayın "
                                  "(`oa_ingest.py <klasor> --yeniden`)." % (ad, no_evrak, i))
            bloklar.append(satirlar)
            if sunan != SUNAN_KARSI:
                ic_not.append("%s: evrakı hangi tarafın sunduğu kalıcı kayıtta yok → dilekçede '%s' yer tutucusu "
                              "duruyor; dilekçeye girmeden önce doldurulmalı." % (ad, YER_TUTUCU_SUNAN))
            adimlar = []
            for nb in girenler:
                a = _dogrulama_adimlari(nb["tur"], nb["yontem"], kaynak)
                if a not in adimlar:
                    adimlar.append(a)
            ic_not.append("%s: ASIL evrakta doğrulama — %s." % (ad, "; ".join(adimlar)))
        for nb in yapisal:
            bulgular.append(_json_bulgu(k, kaynak, sunan, nb, False, TUTULMA_YAPISAL))
            ic_not.append("%s: yapısal tespit dilekçeye ALINMADI — görünür ya da içeriksiz tespit, gizli metin "
                          "göstermez (yanlış suçlama riski): %s (%s). Avukat gerekli görürse ayrıca değerlendirir."
                          % (ad, _yontem_aciklama(nb["tur"], nb["yontem"]), _konum_aciklama(nb["konum"], nb["tur"])))
        for nb in tutulanlar:
            kayit = _json_bulgu(k, kaynak, sunan, nb, False, TUTULMA_KAHIN)
            bulgular.append(kayit)
            ic_not.append("%s: tespit dilekçeye ALINMADI — görünürlük kâhini bu evrakta çalışmadı (%s); %s "
                          "gerekçesi yalnız sezgiseldir, görünür yazı gizli sayılabilir. Orijinalde elle "
                          "doğrulayın ya da PyMuPDF ≥ 1.24.2 ile yeniden tarayın (`oa_ingest.py <klasor> "
                          "--yeniden`). Tutulan metin (%s): «%s»"
                          % (ad, KAHIN_TUR, kayit["yontem_aciklama"], kayit["konum_aciklama"], kayit["alinti"]))
        if disi:
            turler = ", ".join(sorted({nb["tur"] for nb in disi}))
            ornekler = [_alinti_metni(nb["ornek"]) for nb in disi if nb["ornek"]]
            ic_not.append("%s: ayrıca %d görünür/ikincil işaret (%s) var — gizli katman değil, ifşa bölümüne "
                          "alınmadı.%s" % (ad, len(disi), turler,
                                           (" Örnek: «%s»" % ornekler[0]) if ornekler else ""))
        if sema_disi:
            ic_not.append("%s: %d bulgu kaydı şema dışı (tür/metin alanları beklenen biçimde değil) — dilekçeye "
                          "GİRMEDİ; evrakı güncel kapıyla yeniden tarayın." % (ad, sema_disi))
        if not (girenler or tutulanlar or yapisal or disi or sema_disi):
            ic_not.append("%s: kayıt BULGU ama bulgu listesi boş — dilekçeye GİRMEDİ; evrakı yeniden tarayın." % ad)
    if bloklar:
        md = [BOLUM_BASLIGI, "", GIRIS_1, "", GIRIS_2, ""]
        for satirlar in bloklar:
            md += satirlar + [""]
        md += [GOSTERIM_KURALI]
        sonuc["karar"] = KARAR_VAR
        sonuc["dilekce_bolumu_md"] = "\n".join(md) + "\n"
        ic_not.insert(0, "Bölümü dilekçeye koyma kararı avukatındır; bölüm teknik tespiti aktarır, hukuki "
                         "nitelendirme (dürüstlük kuralı, niyet) yapmaz — bunlar avukatın ve Mahkemenin takdiridir.")
    else:
        ic_not.insert(0, "İfşa edilecek kesin bulgu (karar BULGU) yok — dilekçe bölümü üretilmedi. Bu bir "
                         "güvenlik beyanı değildir; aşağıdaki notlar varsa okuyun.")
    sonuc["bulgular"] = bulgular
    sonuc["ic_not"] = ic_not
    sonuc["yer_tutucular"] = sorted(yer_tutucular)
    return sonuc


def ifsa_uret(kok):
    """Dava kökünden (yalnız okuyarak) ifşa sonucunu üretir — JSON ile aynı içerik. Asla `_oa`'ya yazmaz;
    asla fırlatmaz: her beklenmedik hata DENETLENEMEDİ'dir (K-1)."""
    sonuc = _bos_sonuc()
    try:
        _bg()
        kunye, kaynaklar = kunye_oku(kok)
    except IfsaHatasi as e:
        return _denetlenemedi(sonuc, "%s — bulgu kaydı okunamadığı için ifşa kararı verilemez" % e)
    except Exception as e:   # kardeş modül yüklenemedi vb.: temiz SAYILMAZ
        return _denetlenemedi(sonuc, "kapı modülü/kayıt işlenemedi (%s: %s)" % (type(e).__name__, str(e)[:120]))
    try:
        return _isle(sonuc, kunye, kaynaklar)
    except Exception as e:
        return _denetlenemedi(_bos_sonuc(), "bulgular işlenirken beklenmedik hata (%s: %s); kısmi sonuç yayılmadı"
                              % (type(e).__name__, str(e)[:160]), kaynaklar)


# ------------------------------------------------------------------ CLI
def _atomik_yaz(yol, metin):
    """tmp + os.replace: yarım dosya nihai adda görünmez. Ebeveyn dizin yoksa açılır (ör. _oa/cikti)."""
    yol = os.path.abspath(yol)
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    tmp = "%s.tmp-%d" % (yol, os.getpid())
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(metin)
    os.replace(tmp, yol)


def _ciktilar(a, sonuc):
    karar = sonuc["karar"]
    if a.json_yol:
        _atomik_yaz(a.json_yol, json.dumps(sonuc, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
        print("JSON yazıldı: %s" % a.json_yol)
    if karar == KARAR_VAR:
        evraklar = len({b["evrak"] for b in sonuc["bulgular"] if b["dilekceye_girdi"]})
        tespit = sum(1 for b in sonuc["bulgular"] if b["dilekceye_girdi"])
        print("İFŞA: %d evrakta %d tespit — dilekçe bölümü üretildi%s"
              % (evraklar, tespit, (" · yer tutucu: %d (avukat teyidi gerekir)" % len(sonuc["yer_tutucular"]))
                 if sonuc["yer_tutucular"] else ""))
        if a.md:
            _atomik_yaz(a.md, sonuc["dilekce_bolumu_md"])
            print("Dilekçe bölümü yazıldı: %s" % a.md)
    else:
        if karar == KARAR_DENETLENEMEDI:
            print("DENETLENEMEDİ — bulgu kaydı okunamadı ya da işlenemedi; ifşa kararı verilemez ('bulgu yok' DENMEZ).")
        else:
            print("İfşa edilecek kesin bulgu (BULGU) yok — dilekçe bölümü üretilmedi ('bulgu yok' bir güvenlik "
                  "beyanı değildir).")
        if a.md and os.path.exists(a.md):
            print("UYARI: %s mevcut ama bu koşuda bölüm üretilmedi — dosya BAYAT olabilir; dilekçeye almayın." % a.md)
    if sonuc["ic_not"]:
        print("İÇ NOT (dilekçeye girmez):")
        for n in sonuc["ic_not"]:
            print("  - " + n)
    return CIKIS[karar]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gizli talimat İFŞASI — B-22 kesin bulgularından dilekçe bölümü "
                                             "(salt okur; yalnız --md/--json hedeflerine yazar)")
    ap.add_argument("--kok", required=True, help="dava kökü (içinde _oa/metin/00-kunye.json)")
    ap.add_argument("--md", help="dilekçe bölümü Markdown çıktısı (yalnız BULGU varsa yazılır)")
    ap.add_argument("--json", dest="json_yol", help="makine-okur sonuç (her kararda yazılır)")
    a = ap.parse_args(argv)
    try:
        sonuc = ifsa_uret(a.kok)
    except Exception as e:   # ifsa_uret kendi yakalar; çift sigorta — 1 ('BULGU var') ile çakışma olmasın
        sonuc = _denetlenemedi(_bos_sonuc(), "beklenmedik hata (%s: %s)" % (type(e).__name__, str(e)[:160]))
    try:
        return _ciktilar(a, sonuc)
    except Exception as e:
        print("DENETLENEMEDİ: çıktı yazılamadı (%s: %s) — ifşa kararı verilemez ('bulgu yok' DENMEZ)."
              % (type(e).__name__, str(e)[:160]))
        return CIKIS[KARAR_DENETLENEMEDI]


if __name__ == "__main__":
    _sys.exit(main())

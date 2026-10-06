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
  (3) kütük Döküm sütununun bağladığı `_oa/teyit/ham/` dosyaları (K1,
      v0.5.8.6 — dokum/ ile eşdeğer; kök dışına çıkan bağ RET)
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

── v0.5.18 (aday) — ATIF KAPSAMI + DERİNLİK + DAVA GEÇMİŞİ ──
(1) Y-09: «Anayasa m.36», «Anayasa'nın 36. maddesi», «Av.K. m.36», ek/geçici
    madde («4857 sayılı Kanun geçici m.8», «Kanun'un ek 3. maddesi»), «4857
    s.K.» kısaltması ve adıyla anılan kanunlar artık çıkarılır; İMK/TK/HUAK/
    KMK/AvK numara eşlemesine girdi (numaralar resmî kaynaktan teyitli).
    «Anayasa Mahkemesi» atıf değildir. Kanunsuz ek/geçici anış [BİLGİ]'dir.
(2) B-21/B-03: TEYİTLİ atfın DERİNLİĞİ okunur (DOKUM-SINIFI, ARAMA izi,
    ikinci el: künye/madde yalnız başka bir kararın kaydında/dökümünde) —
    ADVISORY (⚠ + sayaç; exit'i değiştirmez).
(3) B-17: `_oa/dosya.md`de (ya da `--kendi-kunye` ile) beyan edilen davanın
    KENDİ geçmişi künyeleri muaf (birebir eşleşme; [BİLGİ] + istisna defteri).
(4) Fable karşı-tez turu: mevzuat madde izi yalnız MADDE BAĞLAMINDA sayılır
    (kütük satırının zaman damgası «:35:» artık «m.35» izi değildir; kanun
    numarası tarih parçasından okunmaz); numaralı atıfta kimlik numaradır
    («765 sayılı TCK» yeni TCK kaydıyla teyit edilmez); «TK»/«İMK» eşlemesi
    raporda görünür.

Kullanım:
  python kunye_teyit.py <taslak.md> [--kutuk _oa/teyit/kunye-teyit.md] \
      [--dokum-dizin _oa/teyit/dokum] [--cikti-dizin _oa/cikti] [--kendi-kunye "..."]
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
import datetime
import functools
import json
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
    # v0.5.18 (Y-09) — eşlemede OLMAYAN kısaltmalar. Numara + resmî ad
    # mevzuat.gov.tr'den Yargı PRO `mevzuat_ara` ile teyit edildi (2026-10-05):
    # 7036 İŞ MAHKEMELERİ KANUNU (RG 25.10.2017) · 7201 TEBLİGAT KANUNU
    # (RG 19.02.1959) · 6325 HUKUK UYUŞMAZLIKLARINDA ARABULUCULUK KANUNU
    # (RG 22.06.2012) · 634 KAT MÜLKİYETİ KANUNU (RG 02.07.1965) · 1136
    # AVUKATLIK KANUNU (RG 07.04.1969). NEDEN: eşlemede olmayan kısaltma
    # yalnız harfiyle aranıyordu — kütükte «7201 sayılı Tebligat Kanunu m.21»
    # teyidi varken taslaktaki «TK m.21» TEYİTSİZ kalıyor, çıplak «TK 21»
    # hiç çıkarılmıyordu (derlemde tebligat dersleri bu yazımla dolu).
    # NOT: «İMK» iş hukuku yazınında İş Mahkemeleri Kanunu'dur; İmar Kanunu
    # (3194) için bu kısaltma KULLANILMAZ — «3194 sayılı Kanun» yazılır.
    "İMK": "7036", "IMK": "7036", "TK": "7201", "HUAK": "6325", "KMK": "634",
    "AVK": "1136",
}
NO_KANUN = {v: k for k, v in KANUN_NO.items()}

# Bare biçim ("HMK 119") yalnızca BİLİNEN kısaltmalarla çıkarılır — aksi hâlde
# mahkeme markerları (AYM, BAM, HGK) yanlışlıkla "kanun" sanılır.
BILINEN_BARE = set(KANUN_NO.keys()) | {"MÜLGA", "HUMK"}

# Mahkeme/kurul markerları — kanun sanılmamaları için dışlanır.
# v0.5.18: «EK»/«GEÇİCİ» madde türüdür, kanun DEĞİLDİR — kanunsuz yazılmış
# «GEÇİCİ MADDE 8» eskiden «GEÇİCİ» adlı hayalî bir kanunun maddesi sanılıp
# sahte TEYİTSİZ üretiyordu; artık kanun anahtarı sayılmaz (kanunsuz ek/geçici
# atıf ayrı [BİLGİ] bloğunda görünür kalır).
MERCILER = {
    "YARGITAY", "DANIŞTAY", "DANISTAY", "AYM", "BAM", "BİM", "BIM", "HGK",
    "CGK", "İBK", "IBK", "AİHM", "AIHM", "SAYIŞTAY", "HD", "CD", "İDDK",
    "IDDK", "VDDK", "KANUN", "SAYILI", "MADDE", "ESAS", "KARAR",
    "EK", "GEÇİCİ", "GECICI",
}
# NOT (v0.5.18): «375 s. KHK m.28» gibi NUMARALI atıfta kimlik numaradır —
# `_kanun_anahtarlari` numarayla tutarsız kısaltmayı («KHK», «765 sayılı TCK»
# içindeki «TCK») anahtar yapmaz; «399 sayılı KHK m.28» teyidi o atfı
# karşılamaz. Numarasız yalın «KHK m.28» / büyük harfli tablo-dışı kanun adı
# («GÜMRÜK KANUNU MADDE 5» → «KANUNU») eski davranışını korur: çıkarılır ve
# teyit ister (denetimsiz bırakılmaz; fail-closed).
# v0.5.18 — iki anlamlı kısaltmalar: eşleme tek anlama bağlanır ve RAPORDA
# görünür kılınır (avukat başka kanun kastetmişse fark etsin). «TK» uygulamada
# Tebligat Kanunu'dur; eski ticaret yazınında Ticaret Kanunu için de görülür.
# «İMK» iş hukukunda İş Mahkemeleri Kanunu'dur (İmar Kanunu 3194 için
# kullanılmaz). Başka kanun kastediliyorsa atıf NUMARASIYLA yazılır.
BELIRSIZ_KISALTMA = {
    "TK": "7201 sayılı Tebligat Kanunu",
    "İMK": "7036 sayılı İş Mahkemeleri Kanunu",
    "IMK": "7036 sayılı İş Mahkemeleri Kanunu",
}

# ── v0.5.18 (Y-09) — ADIYLA ANILAN KANUNLAR (numarasız yazım) ──────────────
# «Anayasa m.36», «Anayasa'nın 36. maddesi», «Av.K. m.36», «Türk Borçlar
# Kanunu'nun 49. maddesi»... Eski `_KANUN` yalnız BÜYÜK HARF kısaltmayı ya da
# «N sayılı» biçimini tanıyordu: bu yazımlar HİÇ çıkarılmıyor, denetimsiz
# teslim ediliyordu (Y-09 — kapının kendi regex'iyle sınandı; derlem
# taslaklarında 29 Anayasa atfı denetim dışı). Tablo KANUN NUMARASINA bağlıdır
# (kimlik numaradır; ad ve kısaltma takma addır) ve İKİ YÖNDE aynı desenle
# kullanılır (tek-yazar): taslaktan çıkarımda ve kütük/döküm eşleşmesinde.
# Resmî adlar mevzuat.gov.tr'den Yargı PRO `mevzuat_ara` ile teyit edildi
# (2026-10-05). YANLIŞ-POZİTİF KORUMALARI: «Anayasa Mahkemesi» bir atıf
# değildir (negatif bakış); «Basın İş Kanunu»/«Deniz İş Kanunu» İş Kanunu
# değildir; numara taşıyan yazımda («765 sayılı Türk Ceza Kanunu») kimlik
# NUMARADIR — ad deseni o atfa başka numara EKLEMEZ (eski kanun yenisiyle
# teyit edilmiş sayılmasın). Tablo örneklemdir (anayasa m.3): listede olmayan
# kanun adıyla anılırsa çıkarılmaz; «N sayılı» ya da kısaltma yazımı kapıya
# girer — tablo kullanıldıkça genişletilir.
# Adlar BÜYÜK-KÜÇÜK HARF DUYARSIZDIR (`(?i:…)`; Python'un Unicode eşlemesi
# i/İ/ı/I'yı birbirine bağlar): büyük harfli başlıktaki «ANAYASASI MADDE 36»
# eskiden «AYASASI» adlı hayalî bir kanun sanılıp sahte TEYİTSİZ üretiyordu.
# Anayasa deseni sağdan da sınırlıdır: «anayasal», «Anayasacı» ad sayılmaz
# (eşleşme tarafında yanlış-teyit yüzeyi olurdu).
KANUN_AD_DESENLERI = {
    "2709": (r"(?i:Anayasa(?:s[ıi])?(?:n[ıi]n|n[ıi]|nda|na|da|ya)?"
             r"(?![a-zçğıöşü])(?!\s*Mahkeme))",),
    "1136": (r"(?i:Avukatl[ıi]k\s+Kanunu)", r"Av\.\s*K\b\.?", r"AvK\b"),
    "7201": (r"(?i:Tebligat\s+Kanunu)",),
    "7036": (r"(?i:İş\s+Mahkemeleri\s+Kanunu)",),
    "634": (r"(?i:Kat\s+Mülkiyeti\s+Kanunu)",),
    "6325": (r"(?i:Hukuk\s+Uyuşmazlıklarında\s+Arabuluculuk\s+Kanunu)",),
    "6098": (r"(?i:Türk\s+Borçlar\s+Kanunu)",),
    "4721": (r"(?i:Türk\s+Medeni\s+Kanunu)",),
    "6102": (r"(?i:Türk\s+Ticaret\s+Kanunu)",),
    "6100": (r"(?i:Hukuk\s+Muhakemeleri\s+Kanunu)",),
    "5271": (r"(?i:Ceza\s+Muhakemesi\s+Kanunu)",),
    "5237": (r"(?i:Türk\s+Ceza\s+Kanunu)",),
    "2577": (r"(?i:İdari\s+Yargılama\s+Usulü\s+Kanunu)",),
    "2004": (r"(?i:İcra\s+ve\s+İflas\s+Kanunu)",),
    # «Basın İş», «Basın-İş», «Deniz İş Kanunu» İş Kanunu (4857) DEĞİLDİR.
    "4857": (r"(?<!(?i:basın)[\s-])(?<!(?i:deniz)[\s-])(?i:İş\s+Kanunu)",),
}
_HARF_ONCESI_DEGIL = r"(?<![A-Za-zÇĞİÖŞÜçğıöşü])"
_KANUN_AD_RX = {no: re.compile(_HARF_ONCESI_DEGIL + "(?:" + "|".join(ds) + ")")
                for no, ds in KANUN_AD_DESENLERI.items()}
_KANUN_ADLI = "(?:" + "|".join(_HARF_ONCESI_DEGIL + d
                               for ds in KANUN_AD_DESENLERI.values() for d in ds) + ")"
# Ad deseninin hemen önünde FARKLI bir «N sayılı» numarası varsa o geçiş bu
# kanunun adı sayılmaz (eşleşme tarafında da kimlik numaradır).
_AD_ONCESI_NO_RE = re.compile(r"(\d{3,5})\s*(?:[Ss]ayılı|[Ss]\.)\s*$")

# ── İçtihat: esas/karar/daire çıkarımı — PAYLAŞIMLI (M2-3) ──
# Bu script artık kendi ESAS_RE/KARAR_RE/_daire_key/_daire_kumesi tanımlarını
# TUTMAZ; iki-geçişli etiket-önce/ters-alternatif çakışma çözümü ve daire
# ayırt edici mantığı TEK yerde (`kunye_ortak.py`) yaşar — bkz. `ko.esas_karar_atiflari`,
# `ko.norm_no`, `ko.daire_key`, `ko.daire_kumesi`, `ko.DAIRE_RE`.

# ── Mevzuat: kanun tanıtıcısı + madde ──
_KANUN = (
    r"(?:\d{3,5}\s*[Ss]ayılı\s+[^\n]{0,50}?(?:[Kk]anun\w*|KHK)"   # 6098 sayılı ... Kanun
    r"|\d{3,5}\s*[Ss]ayılı\s+[A-ZÇĞİÖŞÜ]{2,7}"                    # 6098 sayılı TBK
    # v0.5.18 (Y-09) — «s.» kısaltmalı numara: «4857 s.K.», «4857 s. Kanun»,
    # «375 s. KHK». Hukuk yazımında yaygın (derlemde «4857 s.K. ek m.3»,
    # «375 s. KHK geçici m.24» denetimsiz geçiyordu). Kanun sözcüğü «s.»nin
    # HEMEN ardında aranır (pencere yok): «2019 s. 45» (sayfa) eşleşmez.
    r"|\d{3,5}\s*[Ss]\.\s*K\b\.?"
    r"|\d{3,5}\s*[Ss]\.\s*(?:[Kk]anun\w*|KHK|[A-ZÇĞİÖŞÜ]{2,7})"
    r"|" + _KANUN_ADLI +                                           # v0.5.18: Anayasa / Av.K. / ad
    # TBK, HMK, İYUK — v0.5.18: SOLDAN sözcük sınırlı (büyük harfli sözcüğün
    # ortasından «AYASASI»/«KANUNU» gibi parça kanun anahtarı koparılmaz)
    r"|" + _HARF_ONCESI_DEGIL + r"[A-ZÇĞİÖŞÜ]{2,7})"
)
# Kanun metninden kısaltma çıkarımı — TAM sözcük (2-7 büyük harf).
_KISALTMA_RE = re.compile(_HARF_ONCESI_DEGIL + r"[A-ZÇĞİÖŞÜ]{2,7}(?![A-Za-zÇĞİÖŞÜçğıöşü])")
_MADDE = r"\d+(?:\s*/\s*\d+)?(?:\s*[-–]\s*[a-zçğıöşü]\b)?"
# v0.5.18 — iyelik/hâl eki: «TBK'nın», «HUAK'ın» (ünlüyle başlayan ek de),
# «AİHS'in», «Anayasa'da». Eski desen yalnız n'li biçimi tanıyordu.
_IYELIK = r"['’]?(?:[nN]?[ıiuü]n|[dt][ae])?"
# v0.5.18 (Y-09/B-03) — EK / GEÇİCİ MADDE: kanun ile madde arasına giren tür
# sözcüğü eski regex'i kırıyordu («4857 sayılı Kanun geçici m. 8», «ek m. 3»
# listede yoktu). Zamanaşımı/geçiş hükümleri gibi SONUÇ BELİRLEYİCİ maddeler
# bu sınıftadır — yanlış numaralı bir geçiş hükmü süre savunmasını çökertir.
_TUR = r"(?:(?P<tur>[Gg]e[çc]ici|GE[ÇC][İI]C[İI]|[Ee]k|EK)\s*)"

# "TBK m.49" / "6098 sayılı Kanun m.49" / "TCK md. 5" / "HMK madde 119"
# v0.5.18: "4857 sayılı Kanun geçici m. 8" / "Anayasa m.36" / "Av.K. m.36"
MEVZUAT_M_RE = re.compile(
    r"(?P<kanun>" + _KANUN + r")" + _IYELIK + r"\s*" + _TUR + r"?"
    r"(?:m\.\s*|md\.\s*|mad\.\s*|[Mm]adde\s*|MADDE\s*)(?P<madde>" + _MADDE + r")"
)
# Ters biçim: "TBK'nın 49. maddesi" / "HMK 119. madde"
# v0.5.18: "Anayasa'nın 36. maddesi" / "4857 sayılı Kanun'un geçici 8. maddesi"
# / "Anayasa'nın 36'ncı maddesi" (kesme işaretli sıra eki)
# ReDoS KORUMASI (v0.5.18): madde ile «madde» sözcüğü arasında YALNIZ BİR
# serbest `\s*` vardır; isteğe bağlı her parça (nokta, kesme, sıra eki) kendi
# boşluğunu kendisi tüketir. Art arda isteğe bağlı `\s*` grupları uzun boşluk
# dizisinde (maskelenmiş kaynakça bloğu binlerce boşluk üretir) polinom geri
# izlemeye yol açardı — kapı büyük taslakta kilitlenmemeli.
# Ek/geçici türde SIRA İŞARETİ (nokta ya da -inci eki) ZORUNLUDUR: «Kanuna ek
# 2 maddeyle» (iki EK madde) bir «ek m.2» atfı değildir; «geçici 8. maddesi»,
# «ek 3'üncü madde» atıftır (koşullu grup `(?(tur)…)`).
_SIRA_EKI = r"(?:inci|nci|ıncı|ncı|uncu|ncu|üncü|ncü)"
MEVZUAT_REV_RE = re.compile(
    r"(?P<kanun>" + _KANUN + r")" + _IYELIK + r"\s*" + _TUR + r"?"
    r"(?P<madde>\d+(?:\s*/\s*\d+)?)\s*"
    r"(?(tur)(?:\.\s*(?:['’]\s*)?|(?:['’]\s*)?" + _SIRA_EKI + r"\s*)"
    r"|(?:\.\s*)?(?:['’]\s*)?(?:" + _SIRA_EKI + r"\s*)?)"
    r"(?:[Mm]adde|MADDE)"
    r"(?:si|sinde|sine|sindeki|sinin|siyle|leri)?"
)
# Bare biçim: "HMK 119" (yalnız bilinen kısaltma + çıplak sayı)
MEVZUAT_BARE_RE = re.compile(
    r"\b(?P<kanun>[A-ZÇĞİÖŞÜ]{2,7})\s+(?P<madde>\d{1,4}(?:\s*/\s*\d{1,3})?)\b(?!\s*(?:E\.|K\.|Esas|Karar|sayılı))"
)

OCR_RE = re.compile(r"OCR|⚠")

# v0.5.18 — KANUNSUZ ek/geçici madde anışı («geçici m.8», «Ek Madde 3»):
# kanunu aynı ibarede yazılmadığı için mekanik teyit YAPILAMAZ. Engel
# DEĞİLDİR (kanun önceki cümlede anılmış olabilir — alarm yorgunluğu da
# zarardır) ama SESSİZ de geçmez: [BİLGİ] bloğunda listelenir.
_TUR_DESEN = {"gecici": r"(?:[Gg]e[çc]ici|GE[ÇC][İI]C[İI])", "ek": r"(?:[Ee]k|EK)"}
KANUNSUZ_EKGEC_RE = re.compile(
    _HARF_ONCESI_DEGIL + r"(?:[Gg]e[çc]ici|GE[ÇC][İI]C[İI]|[Ee]k|EK)\s*"
    r"(?:(?:[Mm]adde|MADDE|md\.|m\.)\s*\d+"
    r"|\d+\s*(?:\.\s*)?(?:['’]\s*)?(?:(?:inci|nci|ıncı|ncı|uncu|ncu|üncü|ncü)\s*)?"
    r"(?:[Mm]adde|MADDE))")
_EKGEC_ONCESI_RE = re.compile(
    r"(?:[Gg]e[çc]ici|GE[ÇC][İI]C[İI]|\b[Ee]k|\bEK)\s*(?:(?:[Mm]adde\w*|MADDE|md\.|m\.)\s*)?$")

# ── v0.5.18 (Fable karşı-tez #1) — MADDE İZİ YALNIZ MADDE BAĞLAMINDA ─────────
# YANLIŞ-TEYİT KAPATILDI: madde numarası kaynak segmentin HERHANGİ bir yerinde
# aranıyordu. Her kütük satırı bir zaman damgası taşır («2026-10-05T10:35:47»)
# ve tek segmenttir; damganın «10/35/47» parçaları 1-59 arası her maddenin
# «izi» sayılıyordu: kütükte yalnız «HMK m.119» teyidi varken taslaktaki
# «HMK m.35» TEYİTLİ geçebiliyordu. Aynı şekilde değişiklik notlarındaki
# «(Ek:16/7/2026-7589/13 md.)» parçaları da sahte madde iziydi. Artık sayı
# ancak MADDE BAĞLAMINDA iz sayılır: (a) önünde madde işareti («m.», «md.»,
# «madde», «MADDE», «madde_no=», mevzuat kimliğindeki «:m51»), (b) ardında
# «. madde(si)» / «'nci madde», (c) atfın kendi kısaltmasının hemen ardında
# çıplak biçim («HMK 119»). Fail-closed: bağlamsız sayı iz DEĞİLDİR.
_MADDE_ONCESI_RE = re.compile(
    r"(?:" + _HARF_ONCESI_DEGIL
    + r"(?:[Mm]\.|[Mm][Dd]\.|[Mm]ad\.|[Mm]adde|MADDE)(?:[\s_]?(?:no|NO))?[\"']?\s*(?:[:=]\s*)?"
    r"|" + _HARF_ONCESI_DEGIL + r"m)$")
_MADDE_SONRASI_RE = re.compile(
    r"(?:\s*/\s*\d+)?(?:\s*[-–]\s*[a-zçğıöşü](?![a-zçğıöşü]))?\s*(?:\.\s*)?(?:['’]\s*)?"
    r"(?:" + _SIRA_EKI + r"\s*)?(?:[Mm]adde|MADDE)")
# Kanun NUMARASI aranırken tarih/saat parçaları maskelenir: «12.05.2004»
# tarihindeki yıl 2004 (İİK) numarası sayılmasın; ISO damga, «16/7/2026».
_TARIH_SAAT_RE = re.compile(
    r"(?<!\d)(?:\d{4}-\d{1,2}-\d{1,2}(?:[T ]\d{1,2}[:\-]\d{2}(?:[:\-]\d{2})?)?"
    r"|\d{1,2}[./]\d{1,2}[./]\d{4}"
    r"|\d{8}T\d{4,6}"
    r"|\d{1,2}:\d{2}(?::\d{2})?)(?!\d)")

# ── v0.5.18 (B-21 / B-03) — TEYİT DERİNLİĞİ ────────────────────────────────
# Kütük (oa_hafiza `teyit`) GETİR satırına DOKUM-SINIFI=tam-metin|ilgili-kisim,
# ARAMA satırına «[ARAMA — tam metin çekilmedi]» yazıyor; bu kapı onları HİÇ
# okumuyordu. Ayrıca bir künyenin izi yalnız BAŞKA bir kararın kaydında ya da
# dökümünde (o karar içinde alıntı) bulunduğunda «TEYİTLİ» geçiyordu (B-21:
# kaldırma kararı olan, kendisi hiç getirilmemiş BAM kararı) ve bir mevzuat
# maddesi yalnız bir içtihat dökümünde anıldığı için «teyitli» sayılıyordu
# (B-03: mevzuat sorgusu yok; iz ≠ teyit). Derinlik ADVISORY'dir: statüyü
# ve exit kodunu DEĞİŞTİRMEZ (künye izi gerçektir), görünür ⚠ ve sayaç basar.
# Araç ailesi ad ÖRÜNTÜSÜNDEN okunur (ad listesi kopyalanmaz — tek-yazar:
# kanonik adlar oa_hafiza'dadır). Yalnız ALT ÇİZGİLİ araç adı biçimindeki
# sözcükler sınıflanır (düz «mevzuat»/«anayasa» sözcüğü araç adı değildir);
# aileler: *mevzuat* / resmi_gazete_* → mevzuat; *ictihat* / kurum_karari_* /
# *bedesten* / *anayasa* / *yargitay* / *danistay* / *emsal* / *aihm* / aym_*
# → içtihat. Tanınmayan ad → belirsiz (uyarı ÜRETMEZ — alarm yorgunluğu).
_ARAC_ADI_RE = re.compile(r"[A-Za-z0-9]+(?:_[A-Za-z0-9]+)+")
_ARAC_MEVZUAT_PARCA = ("mevzuat", "resmi_gazete")
_ARAC_ICTIHAT_PARCA = ("ictihat", "kurum_karari", "bedesten", "anayasa", "yargitay",
                       "danistay", "emsal", "aihm", "aym_", "uyusmazlik")
_IKINCI_EL_ISARET_RE = re.compile(
    r"içinde\s+(?:alıntı|anıl|geç|atıf)|alıntıla\w*|alıntılı\b|alıntı\s+yap\w*"
    r"|atıf\s+yapılan|atfen\b|naklen\b|ikinci\s+el")
# Arama aracı satırı: «[ARAMA — tam metin çekilmedi]» işareti ya da *_ara /
# search_* araç adı. Arama isabet listesinde görülen künye ikinci el DEĞİL,
# «yalnız arama» düzeyidir (varlığı görüldü, içeriği çekilmedi).
_ARAMA_ARAC_RE = re.compile(r"\b[a-z0-9_]*_ara\b|\bsearch_\w+", re.I)

# ── B1 (v0.5.8.5) — KENDİ-DOSYA-NO İSTİSNASI ────────────────────────────────
# Saha bulgusu: taslağın başlık/künye bloğundaki KENDİ dosya numarası satırı
# ("DOSYA NO : 2024/123 Esas") içtihat künyesi sanılıp TEYİTSİZ/teslim engeli
# üretiyordu. Muafiyet DARALTILMIŞTIR (fail-closed): yalnız DOSYA NO/ESAS NO/
# MERCİ etiketiyle BAŞLAYAN satırdaki, daire ANMAYAN ve E.+K. ÇİFTİ taşımayan
# (esas-only / karar-only) desen muaf olur; daire adı ya da tam E./K. çifti
# taşıyan metin gerçek içtihat künyesi olabilir → aynen yakalanmaya devam eder.
# Muafiyet SESSİZ DEĞİLDİR: `_oa/defter/istisna-kayitlari.jsonl` ortak şemasına
# (zaman/tur/ilgili/gerekce/onay/imza) kayıt düşülür + rapora [BİLGİ] basılır.
# v0.5.14 (B-2): tanım `kunye_ortak`a taşındı (tek-yazar kuralı) — hem bu
# muafiyet hem `ayristirilamayan_atiflar`ın yanlış-pozitif koruması AYNI
# satır desenine bakar; iki yerde sürüklenip ayrışamaz.
KENDI_DOSYA_SATIR_RE = ko.KENDI_DOSYA_SATIR_RE


def _istisna_kaydi_yaz(kok, tur, ilgili, gerekce, onay="otomatik-kural"):
    """İstisna defteri ortak şeması (append-only JSONL, birden çok araç yazar):
    `_oa/defter/istisna-kayitlari.jsonl` satırı = {"zaman": ISO, "tur": ...,
    "ilgili": str, "gerekce": str, "onay": "avukat"|"otomatik-kural",
    "imza": araç-imzası}. Küçük YEREL yardımcı — ortak modül bağımlılığı
    yaratılmaz (şema sözleşmesi satır biçimidir, kod değil). Yazılamazsa
    görünür uyarı basılır, akış bloklanmaz (defter kaydı advisory izdir)."""
    defter_dizin = os.path.join(kok or ".", "_oa", "defter")
    kayit = {"zaman": datetime.datetime.now().isoformat(timespec="seconds"),
             "tur": tur, "ilgili": ilgili, "gerekce": gerekce,
             "onay": onay, "imza": "kunye_teyit.py"}
    try:
        os.makedirs(defter_dizin, exist_ok=True)
        with open(os.path.join(defter_dizin, "istisna-kayitlari.jsonl"),
                  "a", encoding="utf-8") as f:
            f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"UYARI: istisna defterine yazılamadı ({e}) — muafiyet yine de "
              "uygulandı, iz eksik kaldı.", file=sys.stderr)


def kendi_dosya_no_ayikla(atiflar, metin):
    """B1 — atıf listesinden başlık/künye bloğundaki KENDİ dosya no satırlarını
    ayıklar. Döner: (kalanlar, muaflar). Muafiyet şartları (hepsi birden):
    (1) içtihat türü atıf, (2) E.+K. çifti TAM DEĞİL (esas-only/karar-only),
    (3) daire/merci anılmıyor, (4) satır DOSYA NO/ESAS NO/MERCİ etiketiyle
    başlıyor. Gerçek içtihat künyeleri (daire adı ve/veya E.+K. çifti) bu
    süzgeçten GEÇMEZ — yakalanmaya devam eder (testle kanıtlı)."""
    kalanlar, muaflar = [], []
    for a in atiflar:
        muaf = (a.tur == "ictihat"
                and not (a.esas and a.karar)
                and a.daire_key is None
                and bool(KENDI_DOSYA_SATIR_RE.match(
                    _satir_metni_no(metin, a.satir_no or 0))))
        (muaflar if muaf else kalanlar).append(a)
    return kalanlar, muaflar


def dava_gecmisi_ayikla(atiflar, kendi_kunyeler):
    """v0.5.18 (B-17) — davanın beyan edilmiş KENDİ geçmişine birebir uyan
    içtihat atıflarını ayıklar. Döner: (kalanlar, [(atif, beyan), ...]).
    Eşleşme kuralı tek kaynaktadır (`ko.dava_gecmisi_eslesmesi`)."""
    if not kendi_kunyeler:
        return atiflar, []
    kalanlar, muaflar = [], []
    for a in atiflar:
        kn = None
        if a.tur == "ictihat":
            kn = ko.dava_gecmisi_eslesmesi(
                {"esas": a.esas, "karar": a.karar, "daire_key": a.daire_key,
                 "kunye_turu": a.kunye_turu, "metin": a.metin}, kendi_kunyeler)
        if kn:
            muaflar.append((a, kn))
        else:
            kalanlar.append(a)
    return kalanlar, muaflar


def _sikistir(s, n=140):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


# ───────────────────────── ATIF ÇIKARIMI ─────────────────────────
class Atif:
    __slots__ = ("tur", "metin", "esas", "karar", "kanun_anahtar", "madde",
                 "ocr_taslak", "satir_no", "durum", "kaynak", "kaynak_seg",
                 "merci", "daire_key", "merci_uyari", "merci_celiski",
                 "cikti_izi", "cikti_seg",
                 # v0.5.18
                 "madde_turu", "kunye_turu", "derinlik", "derinlik_not",
                 "bas", "son")

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
        self.madde_turu = None       # v0.5.18: None | 'gecici' | 'ek'
        self.kunye_turu = None       # v0.5.18: içtihatta 'esas_karar'|'aym_bb'|'aihm_basvuru'
        self.derinlik = None         # v0.5.18 (B-21): teyit derinliği sınıfı
        self.derinlik_not = None
        self.bas = None
        self.son = None

    def anahtar(self):
        """Tekilleştirme anahtarı. v0.5.18: madde TÜRÜ de anahtardadır —
        «İK m.8» ile «İK geçici m.8» ayrı maddelerdir, birleştirilemez."""
        if self.tur == "ictihat":
            return ("ictihat", self.esas, self.karar)
        return ("mevzuat", tuple(sorted(self.kanun_anahtar)), self.madde_turu,
                self.madde)

    def madde_goster(self):
        """Rapor için madde yazımı («m.8» / «geçici m.8» / «ek m.3»)."""
        on = {"gecici": "geçici ", "ek": "ek "}.get(self.madde_turu, "")
        return f"{on}m.{self.madde}"


def _kanun_anahtarlari(kanun_str):
    """Kanun metninden eşleşme anahtarları (kısaltma + numara + eşlenik).
    v0.5.18: numara TAŞIMAYAN yazımda kanun ADI tablosu (`KANUN_AD_DESENLERI`)
    numarayı verir («Anayasa» → 2709, «Av.K.» → 1136). Numara taşıyan yazımda
    KİMLİK NUMARADIR: ad deseni başka numara eklemez («765 sayılı Türk Ceza
    Kanunu» 5237 sayılmaz) ve yalnız o numarayla TUTARLI bilinen kısaltma
    anahtar olur («6098 sayılı TBK» → TBK; «765 sayılı TCK» → TCK EKLENMEZ —
    eski kanun atfı yeni TCK kaydıyla teyit edilmiş sayılmasın). Kısaltmalar
    TAM sözcüktür ve ad tablosu eşleştiyse ad metnindeki büyük harfli
    sözcükler anahtar olmaz («TÜRK BORÇLAR KANUNU» → 6098/TBK; «TÜRK»,
    «KANUNU» gibi kimliksiz sözcük başka kanunun iziyle eşleşmesin)."""
    al = set()
    sayilar = re.findall(r"\d{3,5}", kanun_str)
    for num in sayilar:
        al.add(num)
        if num in NO_KANUN:
            al.add(NO_KANUN[num])
    kisaltmalar = [ab for ab in _KISALTMA_RE.findall(kanun_str) if ab not in MERCILER]
    if sayilar:
        for ab in kisaltmalar:
            if KANUN_NO.get(ab) in sayilar:
                al.add(ab)
        return al
    ad_eslesti = False
    for no, rx in _KANUN_AD_RX.items():
        if rx.search(kanun_str):
            ad_eslesti = True
            al.add(no)
            if no in NO_KANUN:
                al.add(NO_KANUN[no])
    if not ad_eslesti:
        for ab in kisaltmalar:
            al.add(ab)
            if ab in KANUN_NO:
                al.add(KANUN_NO[ab])
    return al


def _tur_normalize(ham):
    """'geçici'/'GEÇİCİ'/'gecici' → 'gecici'; 'ek'/'EK' → 'ek'; yoksa None."""
    if not ham:
        return None
    return "ek" if ham.strip().lower() == "ek" else "gecici"


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
        atif.kunye_turu = ham.get("kunye_turu")
        atif.bas, atif.son = ham.get("bas"), ham.get("son")
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
            # v0.5.18 — çıplak biçimde (madde işareti yok) YIL gibi duran dört
            # haneli sayı («HUAK 2012 yılında», «HMK 2011'de») madde sayılmaz:
            # 1900–2099 aralığında madde numarası taşıyan bir kanun bilinmiyor;
            # eşlemeye giren yeni kısaltmalar bu yanlış-pozitifi büyütmesin.
            if rx is MEVZUAT_BARE_RE and re.fullmatch(r"(?:19|20)\d\d", m.group("madde").strip()):
                continue
            anahtarlar = _kanun_anahtarlari(kanun_ham)
            if not anahtarlar:
                continue
            madde = ko.norm_no(m.group("madde"))
            goruldu_span.append((s, e))
            atif = Atif("mevzuat", _sikistir(m.group(0)))
            atif.kanun_anahtar = anahtarlar
            atif.madde = madde
            atif.madde_turu = _tur_normalize(
                m.groupdict().get("tur") if rx is not MEVZUAT_BARE_RE else None)
            atif.satir_no = _satir_no(metin, s)
            atif.ocr_taslak = bool(OCR_RE.search(_satir_metni(metin, s)))
            atif.bas, atif.son = s, e
            atiflar.append(atif)
    return atiflar


def kanunsuz_ekgec_anislari(metin, atiflar):
    """v0.5.18 — kanunu aynı ibarede yazılmamış ek/geçici madde anışları
    (çıkarılmış hiçbir mevzuat atfıyla örtüşmeyen). Döner: [{satir_no, metin}].
    ADVISORY: teyit edilemediği görünür kılınır; teslim engeli değildir."""
    spanlar = [(a.bas, a.son) for a in atiflar
               if a.tur == "mevzuat" and a.bas is not None]
    cikan = []
    for m in KANUNSUZ_EKGEC_RE.finditer(metin):
        if any(m.start() < b and a < m.end() for (a, b) in spanlar):
            continue
        cikan.append({"satir_no": _satir_no(metin, m.start()),
                      "metin": _sikistir(m.group(0), 60)})
    return cikan


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
    # v0.5.18 — satır segmentinde iç boşluk da tekleştirilir: «geçici   madde
    # 8» gibi geniş boşluklu yazım, ek/geçici geri-bakış penceresini aşıp
    # olağan m.8 izi sayılmasın (pencereler zaten tekleştirilmişti).
    segs = [re.sub(r"\s+", " ", s).strip() for s in norm.splitlines() if s.strip()]
    duz = re.sub(r"[ \t]+", " ", norm)
    duz = re.sub(r"\n+", " \n ", duz)
    duz = re.sub(r"\s+", " ", duz)
    W, step = 260, 130
    if duz:
        n = len(duz)
        for i in range(0, n, step):
            bas, son = i, min(n, i + W)
            # v0.5.18 — pencere SÖZCÜK/SAYI ORTASINDA başlamaz ve bitmez.
            # Neden: kesik pencere «gecici 8»i «ecici 8» (olağan m.8 izi) ve
            # «2023/1234»ü «2023/12» (sahte esas izi) gösterebiliyordu — ikisi
            # de yanlış-teyit yüzeyidir. Başlangıç, kesik sözcüğün BAŞINA
            # (en çok 40 karakter geri) çekilir — madde türü bağlamı korunur;
            # bitiş ise kesik sözcük/sayı DIŞARIDA kalacak şekilde GERİ çekilir
            # (pencereye yeni metin eklenmez; o parça sonraki pencerededir).
            if bas > 0:
                k = duz.rfind(" ", max(0, bas - 40), bas)
                if k != -1:
                    bas = k + 1
            if son < n and duz[son] != " ":
                k = duz.rfind(" ", max(bas + 1, son - 40), son)
                if k != -1:
                    son = k
            segs.append(duz[bas:son])
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


# ── K1 (v0.5.8.6) — KÜTÜK DÖKÜM SÜTUNU ham/ BAĞLARI ────────────────────────
# 777 saha dersi: model gerçek triyaj emeğini (ham dökümler + LEHE/ALEYHE)
# teyit-script formatı dışında `_oa/teyit/ham/` altına yazmıştı; kütük Döküm
# sütunu o dosyaları gösterdiği hâlde kapı onları GÖREMİYORDU. Kütük Döküm
# sütunundaki bağlar `_oa/teyit/ham/` altını gösteriyorsa artık GEÇERLİ döküm
# sayılır (dokum/ ile eşdeğer). YOL GÜVENLİĞİ korunur: bağ çözüldüğünde ham
# dizininin (dolayısıyla kökün) dışına çıkıyorsa RET — yüklenmez, görünür
# uyarı basılır (fail-closed; ham/ dizini TOPTAN yüklenmez, yalnız bağlılar).
_HAM_BAG_TOKEN_RE = re.compile(r"[^\s|`'\"()\[\]<>]+")
_HAM_SEGMENT_RE = re.compile(r"ham[/\\]")


def kutuk_ham_baglari(kutuk_yolu):
    """Kütük tablosunun Döküm bağlarını (satırın herhangi bir hücresinde —
    v0.5.16.1: sütun sayısı/konumu sorulmaz, `kunye_ortak.kutuk_veri_satirlari`
    ile aynı satır sözleşmesi) `_oa/teyit/ham/` altını gösteriyorsa teyit
    kaynağı olarak yükler.
    Göreli bağlar KÖKE göre çözülür (oa_hafiza `--dokum` yazım sözleşmesi);
    kök dışına çıkan bağ RET edilir (stderr'e görünür uyarı)."""
    cikan = []
    if not (kutuk_yolu and os.path.isfile(kutuk_yolu)):
        return cikan
    teyit_dizin = os.path.dirname(os.path.abspath(kutuk_yolu))
    ham_dizin = os.path.join(teyit_dizin, "ham")
    kok = os.path.dirname(os.path.dirname(teyit_dizin))
    ham_n = os.path.normcase(os.path.normpath(ham_dizin))
    gorulen = set()
    # v0.5.16.1 — sütun sayısından bağımsız: bağ tokenları satırın tamamında
    # aranır (`ham/` segmenti süzer); veri satırı tanımı `kunye_ortak.
    # kutuk_veri_satirlari` (tek-yazar kuralı; saha kütükleri 17 hücreli).
    for satir in ko.kutuk_veri_satirlari(kutuk_yolu, "kutuk_ham_baglari"):
        for tok in _HAM_BAG_TOKEN_RE.findall(satir):
            if not _HAM_SEGMENT_RE.search(tok):
                continue  # ham/ altını göstermeyen hücre içeriği — ilgisiz
            yol = tok if os.path.isabs(tok) else os.path.join(kok, tok)
            yol = os.path.normpath(os.path.abspath(yol))
            yol_n = os.path.normcase(yol)
            if yol_n in gorulen:
                continue
            gorulen.add(yol_n)
            if not (yol_n == ham_n or yol_n.startswith(ham_n + os.sep)):
                print("UYARI: kütük Döküm bağı `_oa/teyit/ham/` (kök) dışına "
                      f"çıkıyor — RET, teyit kaynağı SAYILMADI: {tok}",
                      file=sys.stderr)
                continue
            if not (os.path.isfile(yol)
                    and yol.lower().endswith((".md", ".txt", ".json"))):
                continue  # bağ var ama dosya yok/tanınmayan tür — teyit üretmez
            try:
                with open(yol, encoding="utf-8", errors="replace") as f:
                    cikan.append(("döküm(ham):" + os.path.basename(yol),
                                  _segmentler(f.read())))
            except OSError:
                pass
    return cikan


def kaynaklari_yukle(kutuk_yolu, dokum_dizin, cikti_dizin):
    """Teyit edici ve bilgi amaçlı kaynakları AYRI döndürür.

    Döner: (teyit_kaynaklar, bilgi_kaynaklar, kutuk_var)
      teyit_kaynaklar : kütük (`_oa/teyit/kunye-teyit.md`) + ham MCP dökümleri
                        (`_oa/teyit/dokum/` + kütük Döküm sütununun bağladığı
                        `_oa/teyit/ham/` dosyaları — K1) — statüyü TEYİTLİ
                        yapabilen tek evren.
      bilgi_kaynaklar : `_oa/cikti/` çalışma evrakları — MODEL çıktısı; TEYİT
                        SAYILMAZ, yalnız "[BİLGİ] iz var" notu üretir (delik kapalı).
    """
    teyit_kaynaklar = []
    kutuk_var = os.path.isfile(kutuk_yolu)
    if kutuk_var:
        with open(kutuk_yolu, encoding="utf-8", errors="replace") as f:
            teyit_kaynaklar.append(("kütük:" + kutuk_yolu, _segmentler(f.read())))
    teyit_kaynaklar += _dizin_kaynaklari(dokum_dizin, "döküm:")
    # K1: kütük Döküm sütununun `_oa/teyit/ham/` bağları — dokum/ ile eşdeğer.
    teyit_kaynaklar += kutuk_ham_baglari(kutuk_yolu)
    # `_oa/cikti/` teyit EDİCİ değildir → yalnız bilgi kaynağı olarak yüklenir.
    bilgi_kaynaklar = _dizin_kaynaklari(cikti_dizin, "çıktı(BİLGİ):")
    return teyit_kaynaklar, bilgi_kaynaklar, kutuk_var


def _sayi_var(segment, sayi):
    """Sayıyı komşu rakamdan izole ederek arar (149 ≠ 49)."""
    return re.search(r"(?<!\d)" + re.escape(sayi) + r"(?!\d)", segment) is not None


def _ad_var(segment, no):
    """v0.5.18 — kanun numarası `no`nun ADI segmentte geçiyor mu? Ad geçişinin
    hemen önünde FARKLI bir «N sayılı» numarası varsa o geçiş sayılmaz
    («765 sayılı Türk Ceza Kanunu» 5237'nin teyidi değildir)."""
    rx = _KANUN_AD_RX.get(no)
    if rx is None:
        return False
    for m in rx.finditer(segment):
        once = _AD_ONCESI_NO_RE.search(segment[max(0, m.start() - 30):m.start()])
        if once and once.group(1) != no:
            continue
        return True
    return False


def _anahtar_var(segment, alias):
    if alias.isdigit():
        return _sayi_var(segment, alias) or _ad_var(segment, alias)
    return re.search(r"(?<![A-ZÇĞİÖŞÜ0-9])" + re.escape(alias) + r"(?![A-ZÇĞİÖŞÜ0-9])",
                     segment) is not None


def _madde_baglaminda(segment, bas, son, aliaslar=()):
    """v0.5.18 — `segment[bas:son]`deki sayı MADDE BAĞLAMINDA mı? (bkz.
    `_MADDE_ONCESI_RE` açıklaması). Tarih/saat/değişiklik notu parçası değil."""
    if _MADDE_ONCESI_RE.search(segment[max(0, bas - 24):bas]):
        return True
    if _MADDE_SONRASI_RE.match(segment, son):
        return True
    once = segment[max(0, bas - 24):bas]
    for al in aliaslar:
        if al.isdigit():
            continue
        if re.search(r"(?<![A-Za-zÇĞİÖŞÜçğıöşü0-9])" + re.escape(al)
                     + r"(?:['’][a-zçğıöşü]{1,4})?\s+$", once):
            return True
    return False


def _madde_var(segment, madde, tur=None, aliaslar=()):
    """v0.5.18 — madde izi. Ek/geçici maddede sayının önünde AYNI TÜR sözcüğü
    aranır («geçici m.8», «GEÇİCİ MADDE 8», mevzuat kimliğindeki «gecici8»;
    fıkra/bent ayrıntısı aranmaz — teyit maddenin kendisinin çekilmesidir).
    Olağan maddede ise önünde ek/geçici sözcüğü OLMAYAN ve MADDE BAĞLAMINDA
    duran en az bir geçiş gerekir: «İK m.8» atfı kütükteki «geçici m.8»
    teyidiyle, «HMK m.35» atfı satırın zaman damgasındaki «:35:» ile
    karşılanmaz (Fable karşı-tez #1)."""
    if tur in _TUR_DESEN:
        taban = re.match(r"\d+", madde)
        if not taban:
            return False
        return re.search(
            _HARF_ONCESI_DEGIL + _TUR_DESEN[tur]
            + r"\s*(?:(?:[Mm]adde\w*|MADDE|md\.|m\.)\s*)?(?:no\s*(?:[:.]\s*)?)?"
            + re.escape(taban.group(0)) + r"(?!\d)", segment) is not None
    for m in re.finditer(r"(?<!\d)" + re.escape(madde) + r"(?!\d)", segment):
        if _EKGEC_ONCESI_RE.search(segment[max(0, m.start() - 24):m.start()]):
            continue
        if _madde_baglaminda(segment, m.start(), m.end(), aliaslar):
            return True
    return False


@functools.lru_cache(maxsize=65536)
def _tarih_maskele(segment):
    """Kanun NUMARASI aramasından önce tarih/saat parçalarını boşlukla örter
    (bkz. `_TARIH_SAAT_RE`). Saf fonksiyon — önbellek yalnız hız içindir."""
    return _TARIH_SAAT_RE.sub(" ", segment)


def segment_eslesir(atif, segment):
    if atif.tur == "ictihat":
        if atif.esas and not _sayi_var(segment, atif.esas):
            return False
        if atif.karar and not _sayi_var(segment, atif.karar):
            return False
        return bool(atif.esas or atif.karar)
    # mevzuat: madde numarası (MADDE BAĞLAMINDA) + en az bir kanun anahtarı
    # aynı segmentte; kanun numarası tarih/saat parçasından okunmaz.
    if not atif.madde or not _madde_var(segment, atif.madde, atif.madde_turu,
                                        atif.kanun_anahtar):
        return False
    maskeli = _tarih_maskele(segment)
    return any(_anahtar_var(maskeli, al) for al in atif.kanun_anahtar)


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


# ───────────────── v0.5.18 (B-21 / B-03) — TEYİT DERİNLİĞİ ─────────────────
def _arac_ailesi(metin):
    """'mevzuat' | 'ictihat' | None — metindeki araç adı ailesi."""
    aileler = set()
    for ad in _ARAC_ADI_RE.findall(metin or ""):
        k = ad.lower()
        if any(p in k for p in _ARAC_MEVZUAT_PARCA):
            aileler.add("mevzuat")
        elif any(p in k for p in _ARAC_ICTIHAT_PARCA):
            aileler.add("ictihat")
    if "mevzuat" in aileler:
        return "mevzuat"
    return "ictihat" if aileler else None


def _ikinci_el_isareti(satir):
    return bool(_IKINCI_EL_ISARET_RE.search(ko._tr_kucuk(satir)))


def _arama_satiri_mi(satir):
    """Satır bir ARAMA kaydı mı? İşaret «[ARAMA» ya da YALNIZ arama aracı adı
    taşıyan bir hücre (serbest metindeki «ictihat_ara sonrası» sayılmaz)."""
    return "[ARAMA" in satir or any(
        _ARAMA_ARAC_RE.fullmatch(h) for h in ko.kutuk_satir_hucreleri(satir) if h)


def _satirin_kendi_kunyesi_mi(satir, esas, karar):
    """Kütük satırının KENDİ künyesi (esas, karar) mı? DAMGA/AKIBET taşıyan
    satırda kimlik script'in doğruladığı künyedir (`kutuk_satiri_kunyesi`);
    taşımayan satırda herhangi bir hücrenin İLK tam künyesi (17 hücreli saha
    düzeninde künye sütunu ilk sırada olmayabilir — Fable karşı-tez #5)."""
    hedef = (esas, karar)
    if "DAMGA=" in satir or "AKIBET=" in satir:
        e, k, _d = ko.kutuk_satiri_kunyesi(satir)
        return (e, k) == hedef
    if any(ko.kunye_normalize(h) == hedef for h in ko.kutuk_satir_hucreleri(satir)):
        return True
    e, k, _d = ko.kutuk_satiri_kunyesi(satir)
    return (e, k) == hedef


def _dokum_kaynaklari(teyit_kaynaklar):
    """`kaynaklari_yukle`nin zaten yüklediği döküm/ham kaynakları
    [(dosya_adı, segmentler)] — dosyalar İKİNCİ KEZ okunmaz."""
    return [(etiket.split(":", 1)[-1], segler) for etiket, segler in teyit_kaynaklar
            if etiket.startswith("döküm")]


def _ilk_kunye(segler):
    """Dökümün başındaki İLK esas/karar künyesi (kararın kendi başlığı).
    `_segmentler` önce satırları sırayla verir; ilk satırlar yeter."""
    bas = "\n".join(segler[:80])[:4000]
    for a in ko.esas_karar_atiflari(bas):
        if a.get("esas") and a.get("karar"):
            return a["esas"], a["karar"]
    return None, None


def teyit_derinligi(atif, kutuk_yolu, teyit_kaynaklar):
    """TEYİTLİ bir atfın teyit DERİNLİĞİNİ sınıflar (advisory; statüyü
    değiştirmez). Döner: (sinif, not) — sinif:
      içtihat: 'tam-metin' | 'ilgili-kisim' | 'arama' | 'kendi-dokum' |
               'ikinci-el' | None (belirsiz/eski kayıt — sessiz)
      mevzuat: 'ikinci-el' (yalnız içtihat kaynaklarında anılıyor) | None
    Kural MEKANİKTİR: kütük satırının KENDİ künyesi (`kutuk_satiri_kunyesi`)
    atfın künyesiyse ve satırda «… içinde alıntılı» gibi ikinci el işareti
    yoksa birinci el; aksi hâlde künye yalnız başka bir kararın kaydında ya da
    dökümünde anılıyordur."""
    dokumler = _dokum_kaynaklari(teyit_kaynaklar)
    if atif.tur == "ictihat":
        if not (atif.esas and atif.karar) or atif.kunye_turu not in (None, "esas_karar"):
            return None, None
        kendi, arama_izi = [], False
        for satir in ko.kutuk_veri_satirlari(kutuk_yolu, "kunye_teyit.derinlik"):
            # daire=None: merci uyuşmazlığı AYRI uyarıdır (⚠ MERCİ); derinlik
            # sınıfı ona ikinci, yanlış bir «ikinci el» uyarısı eklemez.
            if not ko.kutuk_satiri_kunyeyle_eslesir(satir, atif.esas, atif.karar, None):
                continue
            if "DAMGA=" in satir or "AKIBET=" in satir:
                if _satirin_kendi_kunyesi_mi(satir, atif.esas, atif.karar):
                    kendi.append(satir)
                continue
            if _ikinci_el_isareti(satir):
                continue
            if _satirin_kendi_kunyesi_mi(satir, atif.esas, atif.karar):
                kendi.append(satir)
            elif _arama_satiri_mi(satir):
                arama_izi = True
        if kendi:
            if any("DOKUM-SINIFI=tam-metin" in s for s in kendi):
                return "tam-metin", "kararın TAM METNİ okunup kütüğe işlenmiş (DOKUM-SINIFI=tam-metin)"
            if any(("DOKUM-SINIFI=ilgili-kisim" in s) or ("DAMGA=" in s) for s in kendi):
                return "ilgili-kisim", ("kararın yalnız İLGİLİ KISMI okunmuş "
                                        "(tam-metin beyanı yok)")
            if any(_arama_satiri_mi(s) for s in kendi):
                return "arama", ("yalnız ARAMA sonucu — kararın tam metni çekilmemiş "
                                 "(içerik/sonuç teyit edilmedi)")
            return None, None
        if arama_izi:
            return "arama", ("künye yalnız bir ARAMA sonuç listesinde görüldü — kararın "
                             "kendisi çekilmemiş (içerik/sonuç teyit edilmedi)")
        for _ad, segler in dokumler:
            if not any(segment_eslesir(atif, seg) for seg in segler):
                continue
            if _ilk_kunye(segler) == (atif.esas, atif.karar):
                return "kendi-dokum", "kararın kendi dökümü var (kütükte kendi satırı yok)"
        return "ikinci-el", ("kütükte bu künyenin KENDİ satırı ve kendi dökümü yok; "
                             "iz yalnız BAŞKA bir kararın kaydında/dökümünde — kararın "
                             "kendisi getirilmedi (kaldırma/geri gönderme gibi zayıf "
                             "otorite olabilir). Kararı ictihat_getir ile çekip kütüğe "
                             "işleyin ya da ikinci el olduğunu metinde açıkça belirtin (B-21)")
    # mevzuat — önce içtihat-DIŞI (mevzuat/belirsiz) kaynaklar: biri eşleşirse
    # ikinci el iddiası kurulamaz (erken çıkış; büyük döküm evreninde ucuz yol).
    ictihat_kaynaklari = []
    for satir in ko.kutuk_veri_satirlari(kutuk_yolu, "kunye_teyit.derinlik"):
        if _arac_ailesi(satir) == "ictihat":
            ictihat_kaynaklari.append([satir])
        elif segment_eslesir(atif, satir):
            return None, None
    for ad, segler in dokumler:
        if _arac_ailesi(ad) == "ictihat":
            ictihat_kaynaklari.append(segler)
        elif any(segment_eslesir(atif, seg) for seg in segler):
            return None, None
    if any(segment_eslesir(atif, seg) for segler in ictihat_kaynaklari for seg in segler):
        return "ikinci-el", ("madde yalnız İÇTİHAT kaynaklarında anılıyor — "
                             "mevzuat sorgusu (mevzuat_getir) kaydı yok; yürürlük "
                             "ve güncel lafız teyit edilmedi (B-03)")
    return None, None


# ───────────────────────── RAPOR ─────────────────────────
def _belirsiz_kisaltma_notu(atif):
    """v0.5.18 — iki anlamlı kısaltma («TK», «İMK») NUMARASIZ yazıldıysa hangi
    kanuna eşlendiğini döndürür (rapor notu); değilse None."""
    if atif.tur != "mevzuat":
        return None
    for ab, ad in BELIRSIZ_KISALTMA.items():
        if not re.search(_HARF_ONCESI_DEGIL + re.escape(ab) + r"(?![A-Za-zÇĞİÖŞÜçğıöşü])",
                         atif.metin or ""):
            continue
        if KANUN_NO.get(ab) in re.findall(r"\d{3,5}", atif.metin or ""):
            return None
        return f"«{ab}» → {ad} olarak eşlendi"
    return None


def _ayristirilamayan_yazdir(izler):
    """B-2 (v0.5.14) — ayrıştırılamayan atıf iddialarını GÖRÜNÜR kılar."""
    if not izler:
        return
    print(f"\n## AYRIŞTIRILAMAYAN / EKSİK ATIF İDDİASI ({len(izler)}) — MEKANİK TEYİT YAPILAMADI")
    for iz in izler:
        # K4 (v0.5.16): EKSİK KÜNYE (tarih-only / K-only / E-only) sınıfı
        # TEYİTSİZ etiketiyle görünür — tek tarih/tek sayı ile teyit yapılamaz.
        sinif = iz.get("sinif") or ko.SINIF_AYRISTIRILAMAYAN
        etiket = "[TEYİTSİZ]" if sinif == ko.SINIF_EKSIK_KUNYE else "[BLOK]    "
        print(f"{etiket} (satır {iz['satir_no']})  {iz['metin']}  [{sinif}]")
        print(f"           ↳ {iz['sebep']}")
    print("           ↳ Künyeyi TAM biçimde yaz (ör. 'Yargıtay 9. HD, E. 2020/1111, "
          "K. 2021/2222', birleşik 'Yargıtay 9. HD 2020/1111-2021/2222' ya da AYM "
          "için 'B. No: 2019/12345') ve MCP teyidini kütüğe işle; eksik/"
          "ayrıştırılamayan atıf teyit edilemez, teyit edilemeyen atıf çıktıya "
          "GİREMEZ (fail-closed).")


def rapor_yaz(atiflar, kutuk_var, kutuk_yolu, ayristirilamayan=()):
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
        if ayristirilamayan:
            # B-2: "künye yok" ile "künye AYRIŞTIRILAMADI" artık AYRI şeylerdir.
            print("ANCAK ayrıştırılamayan atıf iddiası var — kapı KAPALI.")
            _ayristirilamayan_yazdir(ayristirilamayan)
        else:
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
                # v0.5.18 (B-21/B-03) — teyit derinliği (advisory)
                if a.derinlik == "ikinci-el":
                    print(f"           ⚠ İKİNCİ EL TEYİT — {a.derinlik_not}. Bu uyarı "
                          "exit'i 1 YAPMAZ (iz gerçek); karar avukatındır.")
                elif a.derinlik in ("tam-metin", "ilgili-kisim", "arama", "kendi-dokum"):
                    print(f"           ⓘ teyit derinliği: {a.derinlik_not}")
            else:
                if a.tur == "ictihat":
                    ip = "esas/karar no"
                    ayr = f"E. {a.esas or '—'} / K. {a.karar or '—'}"
                else:
                    ip = "kanun+madde"
                    ayr = f"{'/'.join(sorted(a.kanun_anahtar))} {a.madde_goster()}"
                print(f"           ↳ teyit edici kaynakta (kütük/ham döküm) {ip} izi YOK "
                      f"({ayr}) — çıktıya 'teyitli' giremez.")
                if a.cikti_izi:
                    print(f"[BİLGİ]    ↳ SADECE çalışma evrakında iz var ({a.cikti_izi}) — "
                          "TEYİT SAYILMAZ (model çıktısı; halüsinasyon olabilir). Künye "
                          "kütük/ham MCP dökümüyle teyit edilmeden çıktıya giremez.")
                    print(f"             iz: {a.cikti_seg}")
            if a.ocr_taslak:
                print("           ⚠ Taslakta OCR şüphesi işareti — kaynak orijinalinden teyit şerhi.")
            kis_notu = _belirsiz_kisaltma_notu(a)
            if kis_notu:
                print(f"           ⓘ kısaltma eşlemesi: {kis_notu} — başka kanun "
                      "kastedildiyse atfı NUMARASIYLA yazın.")

    blok("İÇTİHAT KÜNYELERİ", ictihatlar)
    blok("MEVZUAT ATIFLARI", mevzuatlar)
    _ayristirilamayan_yazdir(ayristirilamayan)

    teyitli = sum(1 for a in atiflar if a.durum == "TEYİTLİ")
    teyitsiz = len(atiflar) - teyitli
    merci_uyari = sum(1 for a in atiflar if a.merci_uyari)
    cikti_izli = sum(1 for a in atiflar if a.cikti_izi)
    ikinci_el = sum(1 for a in atiflar if a.durum == "TEYİTLİ" and a.derinlik == "ikinci-el")
    yalniz_arama = sum(1 for a in atiflar if a.durum == "TEYİTLİ" and a.derinlik == "arama")
    print("\n" + "-" * 72)
    ozet = f"ÖZET: {len(atiflar)} atıf  |  TEYİTLİ {teyitli}  |  TEYİTSİZ {teyitsiz}"
    if merci_uyari:
        ozet += f"  |  ⚠ MERCİ DOĞRULANAMADI {merci_uyari}"
    if ikinci_el:
        ozet += f"  |  ⚠ İKİNCİ EL {ikinci_el}"
    if yalniz_arama:
        ozet += f"  |  ⓘ yalnız-ARAMA {yalniz_arama}"
    print(ozet)
    if cikti_izli:
        print(f"NOT: {cikti_izli} teyitsiz künyenin izi YALNIZ çalışma evrakında "
              "(_oa/cikti) — model çıktısı, TEYİT SAYILMAZ (kendi-kendini-teyit deliği kapalı).")
    if teyitsiz or ayristirilamayan:
        print("SONUÇ: TESLİM ENGELİ — teyitsiz/ayrıştırılamayan atıf giderilecek ya da "
              "müvekkile 'açık uç' olarak raporlanacak (gömülmez).")
    else:
        print("SONUÇ: Tüm atıflar kütük/ham döküm izli — mekanik kapı AÇIK. "
              "(İçerik/esas-savunma + doğru daire denetimi oa-kontrol A-listesinindir.)")
        if merci_uyari:
            print("       ⚠ Ancak MERCİ DOĞRULANAMADI uyarılı künye(ler) var — daireyi "
                  "orijinal kaynaktan teyit et (exit 0'ı bloklamaz).")
        if ikinci_el:
            print("       ⚠ Ancak İKİNCİ EL teyitli atıf(lar) var — izi yalnız başka bir "
                  "kaynağın içinde; kendisini resmî kaynaktan çekin (exit 0'ı bloklamaz).")


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
    ap.add_argument("--kendi-kunye", action="append", default=None, metavar="KUNYE",
                    help="v0.5.18 (B-17) — davanın KENDİ geçmişine ait künye (temyiz/istinaf "
                         "edilen karar, ilk derece kararı); birden çok kez verilebilir. "
                         "`_oa/dosya.md`deki «esas no / dava geçmişi / kendi künye» etiketli "
                         "satırlar da OKUNUR. Yalnız BİREBİR eşleşen atıf muaf olur; muafiyet "
                         "[BİLGİ] + istisna defteriyle görünür.")
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

    # B-18 (v0.5.14) — makine üretimi kaynakça bloğu taslağın GÖVDESİ değildir:
    # kapılar onu kendi girdileri sayınca zincir idempotansını kaybediyordu.
    metin = ko.makine_blogu_maskele(metin)

    atiflar = atiflari_cikar(metin)

    # B-2 (v0.5.14) — AYRIŞTIRILAMAYAN ATIF = FAIL-CLOSED. Merci anılan bir
    # satırda karar iması var ama künye çıkarılamıyorsa sonuç "atıf yok"
    # DEĞİLDİR: "mekanik teyit YAPILAMADI"dır. Eski davranışta uydurma
    # içtihatlı taslak "Doğrulanacak künye yok — kapı AÇIK" ile geçiyordu.
    ayristirilamayan = ko.ayristirilamayan_atiflar(
        metin, {a.satir_no for a in atiflar if a.satir_no})

    # B1 (v0.5.8.5) — KENDİ-DOSYA-NO İSTİSNASI: başlık/künye bloğundaki kendi
    # dosya numarası satırları içtihat taramasından muaf; muafiyet istisna
    # defterine yazılır ve rapora [BİLGİ] basılır (sessiz atlama yasağı).
    atiflar, muaf_atiflar = kendi_dosya_no_ayikla(atiflar, metin)
    for a in muaf_atiflar:
        print(f"[BİLGİ] (satır {a.satir_no}) '{a.metin}' — başlık/künye "
              "bloğundaki KENDİ dosya numarası satırı (DOSYA NO/ESAS NO/MERCİ): "
              "içtihat künyesi taramasından MUAF tutuldu (B1); istisna defterine "
              "kaydedildi (_oa/defter/istisna-kayitlari.jsonl).")
        _istisna_kaydi_yaz(
            args.kok, "kunye-istisna",
            ilgili=f"satır {a.satir_no}: {a.metin} (E. {a.esas or '—'} / K. {a.karar or '—'})",
            gerekce="başlık/künye bloğundaki kendi dosya numarası satırı — "
                    "içtihat künyesi değil, taslağın kendi kimliği (B1 muafiyeti; "
                    "daire ve E./K. çifti taşımayan etiketli satır)")

    # v0.5.18 (B-17) — DAVANIN KENDİ GEÇMİŞİ: `_oa/dosya.md`de (ya da
    # --kendi-kunye ile) beyan edilen kendi künyeler içtihat taramasından muaf;
    # her muafiyet [BİLGİ] + istisna defteri (sessiz atlama yasağı). Kök:
    # --kok, yoksa kütük yolunun kökü (teslim_paketi cwd=kök ile çağırır).
    dosya_koku = args.kok or os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(kutuk))))
    kendi_kunyeler = ko.dava_gecmisi_kunyeleri(kok=dosya_koku,
                                               ek_metinler=args.kendi_kunye or ())
    atiflar, gecmis_muaflar = dava_gecmisi_ayikla(atiflar, kendi_kunyeler)
    for a, kn in gecmis_muaflar:
        print(f"[BİLGİ] (satır {a.satir_no}) '{a.metin}' — davanın KENDİ geçmişi "
              f"(beyan: {kn['kaynak']}): içtihat künyesi taramasından MUAF tutuldu "
              "(B-17; HMK m.342/2-c kararın mahkemesi/tarihi/sayısını zorunlu kılar); "
              "istisna defterine kaydedildi.")
        _istisna_kaydi_yaz(
            args.kok, "kunye-istisna-dava-gecmisi",
            ilgili=f"satır {a.satir_no}: {a.metin} (E. {a.esas or '—'} / K. {a.karar or '—'})",
            gerekce=f"davanın kendi geçmişi — {kn['kaynak']} beyanıyla birebir eşleşti "
                    "(B-17 muafiyeti; emsal atfı değildir)")
    if kendi_kunyeler and ayristirilamayan:
        kalan = []
        for iz in ayristirilamayan:
            if ko.dava_gecmisi_satiri_mi(_satir_metni_no(metin, iz["satir_no"]),
                                        kendi_kunyeler):
                print(f"[BİLGİ] (satır {iz['satir_no']}) '{iz['metin']}' — yalnız "
                      "davanın kendi geçmişini anıyor (B-17): EKSİK KÜNYE taramasından "
                      "muaf.")
                continue
            kalan.append(iz)
        ayristirilamayan = kalan

    # v0.5.18 — kanunu aynı ibarede yazılmamış ek/geçici madde (advisory)
    kanunsuz = kanunsuz_ekgec_anislari(metin, atiflar)
    if kanunsuz:
        print(f"[BİLGİ] KANUNU BELİRSİZ EK/GEÇİCİ MADDE ANIŞI ({len(kanunsuz)}) — "
              "mekanik teyit YAPILAMADI (teslim engeli değil):")
        for iz in kanunsuz[:12]:
            print(f"         (satır {iz['satir_no']}) {iz['metin']}")
        print("         ↳ Atfı kanunuyla aynı ibarede yazın (ör. «4857 sayılı Kanun "
              "geçici m.8») ki kapı denetleyebilsin.")

    teyit_kaynaklar, bilgi_kaynaklar, kutuk_var = kaynaklari_yukle(
        kutuk, dokum_dizin, cikti_dizin)

    if kutuk_var:
        for a in atiflar:
            teyit_et(a, teyit_kaynaklar, bilgi_kaynaklar)
            if a.durum == "TEYİTLİ":
                a.derinlik, a.derinlik_not = teyit_derinligi(a, kutuk, teyit_kaynaklar)
    # kütük yoksa: hepsi TEYİTSİZ kalır (yapısal blok)

    rapor_yaz(atiflar, kutuk_var, kutuk, ayristirilamayan)

    if ayristirilamayan:
        sys.exit(1)  # B-2 — mekanik teyit YAPILAMADI (fail-closed)
    if not atiflar:
        sys.exit(0)  # doğrulanacak künye yok
    if not kutuk_var:
        sys.exit(1)  # kütük yok — hiçbir atıf teyit edilemez
    sys.exit(1 if any(a.durum == "TEYİTSİZ" for a in atiflar) else 0)


if __name__ == "__main__":
    main()

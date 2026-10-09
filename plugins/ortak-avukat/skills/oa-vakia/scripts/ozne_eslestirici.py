#!/usr/bin/env python3
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
# KAYNAK ATFI — kavramsal devşirme (anayasa m.0 dört-yol kıyasının "kavramsal
#   devşirme" yolu). v0.5.18: eski "VENDOR" öz-etiketi düzeltildi — dosya
#   dondurulmuş bir vendor kopyası DEĞİLDİR; düzeltmeler bu dosyanın içinde
#   yapılır ve tests/test_ozne_eslestirici.py + tests/test_v0518_ozne.py ile
#   kilitlenir. Algoritma fikri: github.com/semantica-agi/semantica@v0.6.5
#   deduplication/similarity_calculator.py:529-615 (Jaro-Winkler + iki-satır DP
#   Levenshtein). Upstream lisansı MIT — "Copyright (c) 2026 Hawksight AI"
#   (v0.6.5 LICENSE). Kod kopyalanmadı: ders kitabı algoritmaları stdlib ile
#   yeniden yazıldı, paket bağımlılığı YOK. "Farklı türdeki iki varlık asla tek
#   özneye birleşmez" yapısal koruma fikri: semantica v0.6.7 #1149 (kod alınmadı).
"""
oa-vakia — ozne_eslestirici.py  (v0.5.8 P4 — M9 ÖZNE/BEYAN ANATOMİSİ motoru;
v0.5.18 kural seti — kullanıcı kararı 2026-10-05)

OCR'lı UYAP külliyatında aynı öznenin yazım varyantlarını ("Tekçin / TEKCIN /
Tek.in" sınıfı — kurgu örnek) deterministik kurallarla damgalar: "öznenin tüm
beyanları" sorgusu yazım varyantı yüzünden kayıt kaçırmasın (kayıpsızlık).

NEDEN DEĞİŞTİ (v0.5.18): eski motor adın tamamını tek dize olarak
Jaro-Winkler'le skorluyordu. Ortak ilk ad önek bonusu aldığı için iki AYRI
kişi BAGLA damgası alıyordu ("Ahmet Kaya"~"Ahmet Kara" 0,96); sırası değişmiş
ya da ASCII yazılmış aynı kişi ise kaçıyordu ("Mehmet Yılmaz"~"YILMAZ Mehmet"
0,49). Yanlış BAGLA bir tanığın beyanını sanığa akıtabilir (m.4 olgu hatası,
doğrudan müvekkil aleyhine). Kullanıcı kararı: YANLIŞ BİRLEŞTİRME, FAZLADAN
SORUDAN DAHA KÖTÜDÜR — belirsizlik avukata SORU olarak çıkar.

KARAR VERMEZ, DAMGA BASAR (advisory; geçerli girdide CLI her zaman exit 0):
  1. Türkçe katlama (ı→i ç→c ş→s ğ→g ö→o ü→u) ASCII yazımı tanımak içindir:
     "ISMAIL GUNES" = "İsmail Güneş". İki taraf da Türkçe harfle yazılmış ve
     harfleri farklıysa ("Gülşen"/"Gülsen") ayrı ad olabilir → AVUKATA-SOR.
  2. BAGLA yalnız YAZIM eşdeğerliğinde verilir (harfler aynı; fark yalnız
     büyük-küçük harf, ASCII yazımı, boşluk, kurum eki kısaltması ya da sıra):
     a) parçalar aynı; sıra farkı (döndürme) ancak SOYAD tutarlıysa —
        "YILMAZ Mehmet" (büyük harfli parça soyaddır) ya da "Yılmaz, Mehmet"
        = "Mehmet Yılmaz"; "Şahin Yıldız" ~ "Yıldız Şahin" → SOR (iki parça da
        ad ya da soyad olabilir); döndürme dışı sıra (Ali Mehmet ↔ Mehmet Ali)
        → SOR;
     b) boşluksuz birleşik biçim HARFİ HARFİNE aynı ("Ayşegül" = "Ayşe Gül");
        yalnız katlamayla aynıysa ("Can Kaya" ~ "Çankaya") → SOR.
     Sayısal yakınlık ve OCR jokeri TEK BAŞINA BAGLA ettirmez: kardeş adları
     ("Serkan"/"Serhan") yüksek skor alır, joker birden çok ada uyabilir
     ("Ha.an" → Hasan mı Hakan mı?). Bunlar AVUKATA-SOR'dur.
  3. Parça sayısı eşitse en iyi döndürmede parça-bazlı EN DÜŞÜK skor (her
     parça çifti max(Jaro-Winkler, Levenshtein)); ≥ SOR_ESIK → AVUKATA-SOR.
     Önek-uzantısı (Demir/Demirci, Seda/Sedat) gerekçeye yazılır.
  4. Parça sayısı farklıysa en fazla AVUKATA-SOR: kısa adın parçaları uzun
     adda varsa (ikinci ad, çift soyad "Kaya-Demir", şirket eki) ya da
     tam-dize skoru ≥ SOR_ESIK ise.
  5. `tur` (gercek_kisi / tuzel_kisi / kamu) iki tarafta da var ve farklıysa
     BAGLA ASLA. Türsüz bir yazım farklı türden kayıtlara (BAGLA ya da SOR
     ile) bağlanıyorsa onun BAGLA'ları da SOR'a iner — tür koruması dolaylı
     yoldan delinemez. Alan yoksa davranış değişmez.
  + Sessiz kaçak koruması: baş harf ("M. Yılmaz", "M.Yılmaz", "M.A."), OCR
    jokeri, OCR harf karışıklığı (rn↔m, cl↔d, l↔i, 1↔i, 0↔o) ve kurum eki
    ("Ltd. Şti." = "Limited Şirketi" yazım eşdeğeridir; aynı unvanda "A.Ş." ile
    "Ltd. Şti." ise ayrı şirket olabilir → AVUKATA-SOR) yakalanır.
  Bilinen bedel: OCR bozulması ("Y.lmaz", "Yılrnaz") ve "Ahmed/Ahmet",
  "Muhammed/Muhammet" gibi yazım farkları BAGLA değil AVUKATA-SOR'dur.
Semantica'dan BİLİNÇLİ ALINMAYANLAR: Soundex (İngilizce ses sınıfları Ç/Ş/Ğ
düşürür), embedding (Yargı Pro'da var), sessiz çatışma çözümü (çelişki
avukata ÇIKAR — K3 ilkesi).

Kullanım:
  python ozne_eslestirici.py --girdi ozneler.json [--json]
  python ozne_eslestirici.py "Ahmet Tekçin" "TEKCIN Ahmet" "Tek.in"
Girdi JSON: ["ad1", "ad2", ...]  veya
            [{"id": "V1", "ad": "...", "tur": "gercek_kisi"}, ...]  (tur opsiyonel)
Çıkış: 0 = tarama yapıldı (advisory) · 2 = girdi okunamadı/sınır aşıldı.
"""
# __OA_UTF8_GUARD__
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import json
import os
import re
import sys
import unicodedata

# Eşikler. v0.5.18'den beri BAGLA bir eşikle değil YAZIM EŞDEĞERLİĞİYLE
# verilir; BAGLA_ESIK yalnız "yüksek benzerlik ama yapısal kanıt yok"
# gerekçesini işaretler (JSON'daki "esik_bagla" anahtarı geriye uyum için).
BAGLA_ESIK = 0.92
SOR_ESIK = 0.80
TURLER = ("gercek_kisi", "tuzel_kisi", "kamu")

# Kilitlenme sınırları (sınır aşımı sessiz kırpma değil, görünür uyarı/hatadır):
AZAMI_AD = 160          # katlanmış ad uzunluğu; üstü yalnız yazım eşdeğerliğiyle karşılaştırılır
AZAMI_DIZE = 64         # tam-dize skoru (karesel) yalnız bu uzunluğa kadar hesaplanır
AZAMI_PARCA = 8         # döndürme hizalamasında parça sınırı
AZAMI_OZNE = 300        # ≈45 bin çift
AZAMI_BAYT = 8 * 1024 * 1024
IS_BUTCESI = 20_000_000  # sayısal karşılaştırma iş birimi (karakter çifti); aşılınca kalan çiftler
                         # yalnız yazım eşdeğerliğiyle karşılaştırılır ve bu GÖRÜNÜR yazılır

_TR_KUCUK = str.maketrans({"İ": "i", "I": "ı"})
_SAPKA = str.maketrans({"â": "a", "î": "i", "û": "u"})      # Kâmil, Nâzım, Hâkim
_TR_HARFLER = frozenset("abcçdefgğhıijklmnoöprsştuüvyzqwx")
_TR_OZEL = frozenset("çğıöşüÇĞİÖŞÜ")                         # ASCII yazım tespiti
_YABANCI = {"ł": "l", "ø": "o", "đ": "d", "ß": "ss", "æ": "ae", "œ": "oe", "þ": "th", "ð": "d"}
_KATLA = str.maketrans("ıçşğöü", "icsgou")
_OCR_KANON = (("rn", "m"), ("cl", "d"), ("1", "i"), ("l", "i"), ("0", "o"))
_JOKER = "?"
_JOKER_GECICI = "\x01"
_HARF = "a-zçğıöşü"
_BUYUK = "A-ZÇĞİÖŞÜÂÎÛ"
_KUCUK = "a-zçğıöşüâîû"

# Kurum ekleri: katlanmış kısaltma → kanonik yazım parçaları. Yalnız adda bir
# şirket işareti varsa uygulanır ("San" bir soyad da olabilir). Hukuki biçim
# korunur: "A.Ş." ile "Ltd. Şti." ayrı kalır (ayrı şirketler olabilir).
_KURUM_ISARETI = frozenset({"ltd", "limited", "sti", "sirketi", "as", "anonim", "koop", "kooperatifi"})
_KURUM_KISALTMA = {
    "ltd": ["limited"], "limited": ["limited"],
    "sti": ["şirketi"], "sirketi": ["şirketi"],
    "as": ["anonim", "şirketi"], "anonim": ["anonim"],
    "ins": ["inşaat"], "insaat": ["inşaat"],
    "san": ["sanayi"], "sanayi": ["sanayi"],
    "tic": ["ticaret"], "ticaret": ["ticaret"],
    "koop": ["kooperatifi"], "kooperatifi": ["kooperatifi"],
}
# Hukuki biçim parçaları (katlanmış): unvan aynı, biçim farklıysa ("A.Ş." / "Ltd. Şti.")
# ayrı ya da ilişkili şirketler olabilir → sessiz kalmaz, AVUKATA-SOR.
_HUKUKI_BICIM = frozenset({"limited", "sirketi", "anonim", "kooperatifi"})


def _harf_sadele(c):
    """Türk alfabesi dışındaki harfi tabanına indirir (é→e, ä→a, ł→l, ß→ss);
    Türkçe harfler (ç ğ ı ö ş ü) bu yola hiç girmez."""
    if c in _YABANCI:
        return _YABANCI[c]
    d = unicodedata.normalize("NFKD", c)
    return "".join(x for x in d if not unicodedata.combining(x))


def _kucult(ad):
    """NFC + Türkçe-doğru küçültme + şapkalı ünlü + yabancı harf sadeleştirme.
    NFC: ayrışık yazılmış "u + ¨" gibi girdiler tek harfe birleşir; aksi hâlde
    birleşik işaret boşluğa dönüp adı ikiye bölüyordu."""
    s = unicodedata.normalize("NFC", str(ad)).translate(_TR_KUCUK).lower()
    s = s.translate(_SAPKA)
    return "".join(c if (c in _TR_HARFLER or not c.isalpha()) else _harf_sadele(c)
                   for c in s)


def tr_normalize(ad):
    """Türkçe-doğru küçültme + OCR gürültü temizliği (nokta/kesme/tire) +
    boşluk sadeleştirme. Türkçe harfler KORUNUR (Soundex'in aksine).
    v0.5.18: NFC birleştirme, şapkalı ünlü (â î û) ve yabancı harf
    sadeleştirme eklendi — "Kâmil" artık "k mil" diye bölünmez."""
    s = _kucult(ad)
    s = re.sub(r"[.'’`\-_]", "", s)          # OCR nokta/kesme gürültüsü
    s = re.sub(r"[^0-9a-zçğıöşü ]", " ", s)  # kalan yabancı işaretler → boşluk
    return re.sub(r"\s+", " ", s).strip()


def tr_katla(s):
    """Kural 1 — Türkçe katlama (ı→i ç→c ş→s ğ→g ö→o ü→u). tr_normalize
    "I"yı doğru olarak "ı" yapar; ASCII büyük harfli metinde "ISMAIL" böylece
    "ısmaıl" olur ve "İsmail" ile eşleşmezdi. Katlama bu belirsizliği kapatır."""
    return str(s).translate(_KATLA)


def _on_isle(ad):
    """Ham (büyük-küçük harfi korunan) metinde yapısal düzeltmeler:
    sondaki "A.Ş." tek parça olur; "M.Yılmaz" / "M.A." baş harfleri ayrılır
    (noktadan sonra büyük harf + küçük harf ya da yeni baş harf); harf
    arasındaki tire boşluk olur (çift soyad "Kaya-Demir", OCR heceleme)."""
    s = unicodedata.normalize("NFC", str(ad))
    s = re.sub(r"(?i)(?<![^\W\d_])a\s?\.\s?[şs]\s?\.?\s*$", " AŞ", s)
    s = re.sub(r"(?<![%s%s])([%s])\.(?=[%s](?:[%s]|\.))" % (_BUYUK, _KUCUK, _BUYUK, _BUYUK, _KUCUK),
               r"\1. ", s)
    return re.sub(r"(?<=[^\W\d_])-(?=[^\W\d_])", " ", s)


def _parcalar(on, kurum=True):
    """Ön-işlenmiş adı [(k, kj, h, hj)] parçalarına ayırır. h: küçültülmüş
    (Türkçe harfler korunur) parça, k: katlanmış hâli; hj/kj: harf arasındaki
    okunamayan OCR işaretinin '?' jokeri olarak korunduğu biçim (yoksa None).
    Adda şirket işareti varsa kurum eki kısaltmaları kanonik yazıma açılır."""
    s = _kucult(on)
    s = re.sub(r"(?<=[%s])[.?*_•·�](?=[%s])" % (_HARF, _HARF), _JOKER_GECICI, s)
    s = re.sub(r"[.'’`\-_]", "", s)
    s = re.sub(r"[^0-9a-zçğıöşü%s ]" % _JOKER_GECICI, " ", s)
    sonuc = []
    for p in s.split():
        hj = p.replace(_JOKER_GECICI, _JOKER) if _JOKER_GECICI in p else None
        h = p.replace(_JOKER_GECICI, "")
        if h:
            sonuc.append((tr_katla(h), tr_katla(hj) if hj else None, h, hj))
    if kurum and any(p[0] in _KURUM_ISARETI for p in sonuc):
        acik = []
        for p in sonuc:
            if p[1] is None and p[0] in _KURUM_KISALTMA:
                acik.extend((tr_katla(h), None, h, None) for h in _KURUM_KISALTMA[p[0]])
            else:
                acik.append(p)
        sonuc = acik
    return sonuc


def _soyad_kumesi(on):
    """Soyad işareti: virgülden önceki kısım ("Yılmaz, Mehmet"); büyük-küçük
    karışık yazılmış adda TAMAMI büyük harf olan parça(lar) ("YILMAZ Mehmet",
    "Mehmet YILMAZ"); işaret yoksa son parça (Türkçe "Ad Soyad" düzeni)."""
    if "," in on:
        once = _parcalar(on.split(",", 1)[0])
        if once:
            return frozenset(p[0] for p in once)
    hamlar = [re.sub(r"[^\w]", "", t) for t in on.split()]
    hamlar = [t for t in hamlar if any(c.isalpha() for c in t)]
    if any(any(c.islower() for c in t) for t in hamlar):
        buyuk = [t for t in hamlar if sum(c.isalpha() for c in t) >= 2 and not any(c.islower() for c in t)]
        if buyuk:
            return frozenset(tr_katla(tr_normalize(t)) for t in buyuk)
    son = _parcalar(on)
    return frozenset(p[0] for p in son[-1:])


def _yorumlar(ad):
    """Ad için okuma(lar). Tamamı büyük harfli "M.YILMAZ" hem baş harf + soyad
    hem OCR bozulması olabilir → iki okuma; diğer adlarda tek okuma."""
    on = _on_isle(ad)
    ornekler = [on]
    alt = re.sub(r"(?<![^\W\d_])([%s])\.(?=[%s]{2,}(?![%s]))" % (_BUYUK, _BUYUK, _KUCUK), r"\1. ", on)
    if alt != on:
        ornekler.append(alt)
    ascii_mi = not any(c in _TR_OZEL for c in on)
    return [{"parcalar": _parcalar(o), "dize": [p[0] for p in _parcalar(o, kurum=False)],
             "ascii": ascii_mi, "soyad": _soyad_kumesi(o)} for o in ornekler]


def levenshtein_benzerlik(a, b):
    """İki-satır DP — semantica :529-547 deseninin uyarlaması. Kısa dize iç
    döngüye alınır (bellek O(min(|a|,|b|)))."""
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    if len(b) > len(a):
        a, b = b, a
    onceki = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        simdiki = [i]
        for j, cb in enumerate(b, 1):
            simdiki.append(min(onceki[j] + 1, simdiki[j - 1] + 1,
                               onceki[j - 1] + (ca != cb)))
        onceki = simdiki
    return 1.0 - onceki[-1] / max(len(a), len(b))


def jaro(a, b):
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    pencere = max(len(a), len(b)) // 2 - 1
    pencere = max(pencere, 0)
    a_es = [False] * len(a)
    b_es = [False] * len(b)
    eslesme = 0
    for i, ca in enumerate(a):
        lo, hi = max(0, i - pencere), min(len(b), i + pencere + 1)
        for j in range(lo, hi):
            if not b_es[j] and b[j] == ca:
                a_es[i] = b_es[j] = True
                eslesme += 1
                break
    if not eslesme:
        return 0.0
    t = 0
    j = 0
    for i in range(len(a)):
        if a_es[i]:
            while not b_es[j]:
                j += 1
            if a[i] != b[j]:
                t += 1
            j += 1
    t /= 2
    return (eslesme / len(a) + eslesme / len(b)
            + (eslesme - t) / eslesme) / 3


def jaro_winkler(a, b, p=0.1, max_onek=4):
    j = jaro(a, b)
    onek = 0
    for ca, cb in zip(a, b):
        if ca != cb or onek == max_onek:
            break
        onek += 1
    return j + onek * p * (1 - j)


def parca_skoru(a, b):
    """Tek ad parçası çifti: max(JW, Levenshtein). JW önek-ağırlıklıdır,
    kelime ortası OCR bozulmasını ıskalayabilir — Levenshtein o açığı kapatır.
    Önek bonusu artık yalnız parça İÇİNDE işler; ortak ilk ad tüm adı
    şişiremez (kök neden (i))."""
    return max(jaro_winkler(a, b), levenshtein_benzerlik(a, b))


_TUR_ESANLAM = {
    "gercekkisi": "gercek_kisi", "gercek": "gercek_kisi", "kisi": "gercek_kisi", "sahis": "gercek_kisi",
    "tuzelkisi": "tuzel_kisi", "tuzel": "tuzel_kisi", "ozelhukuktuzelkisisi": "tuzel_kisi",
    "sirket": "tuzel_kisi", "anonimsirket": "tuzel_kisi", "anonimsirketi": "tuzel_kisi",
    "limitedsirket": "tuzel_kisi", "limitedsirketi": "tuzel_kisi", "dernek": "tuzel_kisi",
    "vakif": "tuzel_kisi", "kooperatif": "tuzel_kisi",
    "kamu": "kamu", "kamukurumu": "kamu", "kamutuzelkisisi": "kamu", "kamuidaresi": "kamu",
    "idare": "kamu", "belediye": "kamu", "bakanlik": "kamu", "valilik": "kamu", "kaymakamlik": "kamu",
}


def tur_normalize(tur):
    """`tur` alanını kapalı kümeye indirir. Döner: (deger | None, uyari | None).
    Yalnız açık eş anlamlılar kabul edilir ("Gerçek Kişi", "şahıs", "tüzel",
    "anonim şirket", "belediye"); tanınmayan değer ("davacı" gibi usul rolü
    dahil) YOK SAYILIR — BAGLA'yı ne açar ne kapatır — ama görünür not düşer."""
    if tur is None or str(tur).strip() == "":
        return None, None
    s = tr_katla(tr_normalize(tur)).replace(" ", "")
    if s in _TUR_ESANLAM:
        return _TUR_ESANLAM[s], None
    return None, f"tur_taninmadi={str(tur)[:40]}"


def _esitlik(xa, xb):
    """Parça dizileri aynı mı? None | 'ayni-sira' | 'dondurme' | 'permutasyon'."""
    if sorted(xa) != sorted(xb):
        return None
    if xa == xb:
        return "ayni-sira"
    if any(xb[r:] + xb[:r] == xa for r in range(1, len(xb))):
        return "dondurme"
    return "permutasyon"


def _birlesik(xa, xb):
    """Kural 2b — boşluksuz birleşik biçim: None | 'ayni' | 'dondurme'."""
    if "".join(xa) == "".join(xb):
        return "ayni"
    a_bic = {"".join(xa[r:] + xa[:r]) for r in range(min(len(xa), AZAMI_PARCA))}
    if any("".join(xb[r:] + xb[:r]) in a_bic for r in range(min(len(xb), AZAMI_PARCA))):
        return "dondurme"
    return None


def _ocr_kanonik(p):
    for eski, yeni in _OCR_KANON:
        p = p.replace(eski, yeni)
    return p


def _joker_esit(jokerli, duz):
    """Tek '?' taşıyan jokerli parça, aynı uzunluktaki jokersiz parçaya o
    konum dışında birebir uyuyor mu? (Yalnız AVUKATA-SOR doğurur.)"""
    if (jokerli is None or jokerli.count(_JOKER) != 1 or len(jokerli) != len(duz)
            or len(duz) < 2):
        return False
    return all(x == _JOKER or x == y for x, y in zip(jokerli, duz))


def _bas_harf_mi(a, b):
    k, u = (a, b) if len(a) <= len(b) else (b, a)
    return len(k) == 1 and len(u) >= 2 and u[0] == k and k.isalpha()


def _onek_uzantisi_mi(a, b):
    k, u = (a, b) if len(a) <= len(b) else (b, a)
    return len(k) >= 2 and len(u) > len(k) and u.startswith(k)


def _cift(p, q):
    """İki parçayı sınıflar: (tur, skor). tur ∈ esit | joker | basharf | sayisal.
    joker ve basharf uyum gösterir ama kanıt zayıftır — yalnız AVUKATA-SOR."""
    if p[0] == q[0]:
        return "esit", 1.0
    skor = parca_skoru(p[0], q[0])
    if (p[1] is not None and q[1] is None and _joker_esit(p[1], q[0])) or \
            (q[1] is not None and p[1] is None and _joker_esit(q[1], p[0])):
        return "joker", skor
    if _bas_harf_mi(p[0], q[0]):
        return "basharf", skor
    return "sayisal", skor


def _hizala(pa, pb):
    """Eşit sayıda parça için pb'nin döndürmeleri arasında en iyi hizalamayı
    seçer. Ölçüt (sözlük sırası): uyumlu çift sayısı, en düşük skor, toplam
    skor; eşitlikte ilk döndürme (deterministik). Döndürme dışı permütasyon
    denenmez: "Ali Mehmet" ile "Mehmet Ali" ayrı kişiler olabilir."""
    en_iyi = None
    n = len(pa)
    for r in range(n):
        rb = pb[r:] + pb[:r]
        ciftler = [(pa[i][0], rb[i][0]) + _cift(pa[i], rb[i]) for i in range(n)]
        skorlar = [c[3] for c in ciftler]
        uyum = sum(1 for c in ciftler if c[2] != "sayisal")
        anahtar = (uyum, min(skorlar), sum(skorlar))
        if en_iyi is None or anahtar > en_iyi[0]:
            en_iyi = (anahtar, ciftler)
    return en_iyi[1]


def _dize_skoru(sa, sb):
    """Tam-dize skoru (eski yöntemin katlanmış hâli); kısa tarafın döndürmeleri
    içinde en iyisi. AZAMI_DIZE'yi aşan dizede HESAPLANMAZ (None) — karesel
    maliyet sınırı."""
    kisa, uzun = (sa, sb) if len(sa) <= len(sb) else (sb, sa)
    u = " ".join(uzun)
    if len(u) > AZAMI_DIZE or len(" ".join(kisa)) > AZAMI_DIZE:
        return None
    return max(parca_skoru(" ".join(kisa[r:] + kisa[:r]), u)
               for r in range(max(1, min(len(kisa), AZAMI_PARCA))))


def _parca_uyar(p, q):
    t, _ = _cift(p, q)
    return t != "sayisal" or _ocr_kanonik(p[0]) == _ocr_kanonik(q[0])


def _alt_kume(pa, pb):
    """Kural 4 — kısa adın her parçası uzun adda ayrı bir parçaya uyuyor mu
    (birebir, joker, baş harf ya da OCR karışıklığı)? Açgözlü, deterministik."""
    kisa, uzun = (pa, pb) if len(pa) <= len(pb) else (pb, pa)
    kullanildi = [False] * len(uzun)
    for p in kisa:
        for i, q in enumerate(uzun):
            if not kullanildi[i] and _parca_uyar(p, q):
                kullanildi[i] = True
                break
        else:
            return False
    return True


GEREKCE = {
    "katlanmis-esit": "aynı ad: yalnız büyük-küçük harf, ASCII yazımı, kurum eki ya da (soyad tutarlı) sıra farkı",
    "birlesik-esit": "boşluksuz birleşik biçim harfi harfine aynı (ör. Ayşegül = Ayşe Gül)",
    "diakritik-farki": "iki yazım da Türkçe harfli ve harfleri farklı (ör. Gülşen/Gülsen) — ayrı ad olabilir; avukata sor",
    "birlesik-katlama": "birleşik biçim yalnız Türkçe harf katlamasıyla aynı (ör. Can Kaya/Çankaya) — avukata sor",
    "sira-farki": "aynı parçalar farklı sırada; hangisinin soyad olduğu belli değil — avukata sor",
    "kurum-turu-farki": "aynı unvan, farklı şirket türü (ör. A.Ş. / Ltd. Şti.) — ayrı ya da ilişkili şirketler olabilir; avukata sor",
    "ocr-joker": "OCR'ın okunamayan işareti bir harfe denk (ör. Y.lmaz ~ Yılmaz) — muhtemelen aynı; avukata sor",
    "bas-harf": "baş harf eşleşmesi (ör. M. ↔ Mehmet) — aynı kişi de olabilir başka kişi de; avukata sor",
    "ocr-karisikligi": "OCR harf karışıklığı (rn↔m, cl↔d, l↔i) giderilince aynı — muhtemelen aynı özne; avukata sor",
    "parca-benzerligi": "ad parçaları yakın ama birebir değil (yazım varyantı ya da kardeş/akraba adı) — avukata sor",
    "alt-kume": "kısa ad uzun adın parçası (ikinci ad, çift soyad, şirket eki, kısaltma) — avukata sor",
    "dize-benzerligi": "parça sayısı farklı, tam dize yakın — avukata sor",
    "tur-farkli": "tür farklı (gerçek kişi / tüzel kişi / kamu) — BAGLA YASAK; avukata sor",
    "tur-belirsiz": "bu yazım farklı türden kayıtlara bağlanıyor (kişi mi şirket mi?) — hangi özneye ait olduğu avukata sorulmalı",
}


def _karar_tek(A, B, sayisal=True):
    """Tek okuma çifti için (skor, karar, kural, nedenler)."""
    pa, pb = A["parcalar"], B["parcalar"]
    if not pa or not pb:
        return 0.0, None, "bos-ad", ["bos-ad"]
    ha, hb = [p[2] for p in pa], [p[2] for p in pb]
    ka, kb = [p[0] for p in pa], [p[0] for p in pb]
    soyad_tutarli = A["soyad"] == B["soyad"]

    eh = _esitlik(ha, hb)
    ek = eh or _esitlik(ka, kb)
    if ek:
        if eh is None and not (A["ascii"] or B["ascii"]):
            return 1.0, "AVUKATA-SOR", "diakritik-farki", ["diakritik=" + "/".join(
                f"{x}~{y}" for x, y in zip(sorted(ha), sorted(hb)) if x != y)]
        if ek == "ayni-sira":
            return 1.0, "BAGLA", "katlanmis-esit", []
        if ek == "dondurme" and soyad_tutarli:
            return 1.0, "BAGLA", "katlanmis-esit", ["sira=soyad-tutarli"]
        return 1.0, "AVUKATA-SOR", "sira-farki", ["sira=" + ek]
    bh = _birlesik(ha, hb)
    if bh == "ayni" or (bh == "dondurme" and soyad_tutarli):
        return 1.0, "BAGLA", "birlesik-esit", []
    if bh == "dondurme":
        return 1.0, "AVUKATA-SOR", "sira-farki", ["sira=birlesik-dondurme"]
    if _birlesik(ka, kb):
        return 1.0, "AVUKATA-SOR", "birlesik-katlama", []
    ca = [x for x in ka if x not in _HUKUKI_BICIM]
    cb = [x for x in kb if x not in _HUKUKI_BICIM]
    if ca and len(ca) < len(ka) and len(cb) < len(kb) and sorted(ca) == sorted(cb):
        return 1.0, "AVUKATA-SOR", "kurum-turu-farki", ["hukuki_bicim=" + "/".join(
            " ".join(x for x in s if x in _HUKUKI_BICIM) for s in (ka, kb))]
    if not sayisal:
        return 0.0, None, "butce-asildi", ["sayisal_karsilastirma_atlandi"]
    if len(" ".join(ka)) > AZAMI_AD or len(" ".join(kb)) > AZAMI_AD:
        return 0.0, None, "cok-uzun", [f"cok_uzun>{AZAMI_AD}"]

    nedenler = []
    karar = kural = None
    if len(ka) == len(kb) and len(ka) <= AZAMI_PARCA:
        ciftler = _hizala(pa, pb)
        skor = min(c[3] for c in ciftler)
        turler = [c[2] for c in ciftler]
        nedenler.append(f"parca_min={skor:.3f}")
        for a, b, t, s in ciftler:
            if t == "joker":
                nedenler.append(f"joker={a}~{b}")
            elif t == "basharf":
                nedenler.append(f"bas_harf={a}~{b}")
            elif t == "sayisal" and _onek_uzantisi_mi(a, b):
                nedenler.append(f"onek_uzantisi={a}/{b}")
        sayisal_ok = all(t != "sayisal" or s >= SOR_ESIK for _, _, t, s in ciftler)
        if "basharf" in turler and sayisal_ok:
            karar, kural = "AVUKATA-SOR", "bas-harf"
        elif "joker" in turler and sayisal_ok:
            karar, kural = "AVUKATA-SOR", "ocr-joker"
        elif sorted(_ocr_kanonik(x) for x in ka) == sorted(_ocr_kanonik(x) for x in kb):
            karar, kural = "AVUKATA-SOR", "ocr-karisikligi"
        elif skor >= SOR_ESIK:
            karar, kural = "AVUKATA-SOR", "parca-benzerligi"
            if skor >= BAGLA_ESIK:
                nedenler.append("yuksek_benzerlik_ama_yapisal_kanit_yok")
        if karar:   # eski yöntemin (tam dize) skoru yalnız raporlanan çiftte: bilgi + maliyet
            d = _dize_skoru(A["dize"], B["dize"])
            nedenler.insert(1, f"dize={d:.3f}" if d is not None else "dize=hesaplanmadi(uzun)")
    else:
        d = _dize_skoru(A["dize"], B["dize"])   # kurum eki açılımı ÖNCESİ parçalar (eski yöntemle karşılaştırılabilir)
        skor = d if d is not None else 0.0
        nedenler.append(f"dize={d:.3f}" if d is not None else "dize=hesaplanmadi(uzun)")
        nedenler.append(f"parca_sayisi={len(ka)}/{len(kb)}")
        if _alt_kume(pa, pb):
            karar, kural = "AVUKATA-SOR", "alt-kume"
        elif d is not None and d >= SOR_ESIK:
            karar, kural = "AVUKATA-SOR", "dize-benzerligi"
    return skor, karar, kural or "esik-alti", nedenler


def _hazirla(ad, tur=None):
    """Ad başına bir kez: (okumalar, tur, tur_uyarisi). eslestir() listeyi
    çift başına yeniden ayrıştırmasın diye ayrı tutulur."""
    t, u = tur_normalize(tur)
    return _yorumlar(ad), t, u


def _karar(h1, h2, sayisal=True):
    (ya, t1, u1), (yb, t2, u2) = h1, h2
    sonuclar = [_karar_tek(a, b, sayisal) for a in ya for b in yb]
    # Birden çok okuma (yalnız "M.YILMAZ" sınıfı): yazım eşdeğerliği veren
    # okuma, yoksa soru doğuran okuma, yoksa ilki — sessiz okuma soruyu ezemez.
    secim = (next((s for s in sonuclar if s[1] == "BAGLA"), None)
             or next((s for s in sonuclar if s[1] == "AVUKATA-SOR"), None) or sonuclar[0])
    skor, karar, kural, nedenler = secim
    nedenler = [u for u in (u1, u2) if u] + list(nedenler)
    tur_catisma = bool(t1 and t2 and t1 != t2)
    if tur_catisma:
        nedenler.append(f"tur_farkli={t1}/{t2}")
    gerekce = GEREKCE.get(kural, "eşik altı — ayrı özne")
    if karar == "BAGLA" and tur_catisma:
        karar = "AVUKATA-SOR"
        gerekce = GEREKCE["tur-farkli"] + " (" + GEREKCE[kural] + ")"
        kural = kural + "+tur-farkli"
    elif karar and tur_catisma:
        gerekce += "; tür de farklı"
    return {"skor": skor, "karar": karar, "kural": kural, "nedenler": nedenler, "gerekce": gerekce}


def ozne_karari(ad1, ad2, tur1=None, tur2=None):
    """İki ad için kural setini uygular. Döner: {"skor", "karar", "kural",
    "nedenler", "gerekce"}; karar ∈ "BAGLA" | "AVUKATA-SOR" | None (sessiz —
    ayrı özne). `skor` bilgi amaçlıdır: karar KURALDAN çıkar."""
    return _karar(_hazirla(ad1, tur1), _hazirla(ad2, tur2))


def ozne_skoru(ad1, ad2):
    """Geriye uyum (v0.5.8 arayüzü): (skor, nedenler)."""
    k = ozne_karari(ad1, ad2)
    return k["skor"], k["nedenler"]


def _kayit(x, sira):
    """Girdi öğesi: ad dizesi ya da {"id", "ad", "tur"} sözlüğü. Başka tür
    (None, sayı, liste) sessizce str() ile ad yapılmaz — "None"~"None" BAGLA'sı
    gibi uydurma eşleşme doğardı."""
    if isinstance(x, dict):
        ad = x.get("ad")
        if ad is not None and not isinstance(ad, str):
            raise ValueError(f"özne #{sira}: 'ad' dize olmalı (gelen: {type(ad).__name__})")
        return (x.get("id") or f"V{sira}", ad or "", x.get("tur"))
    if isinstance(x, str):
        return (f"V{sira}", x, None)
    raise ValueError(f"özne #{sira}: ad dizesi ya da {{\"ad\": ...}} sözlüğü olmalı "
                     f"(gelen: {type(x).__name__})")


def _liste_denetimi(ham, turler):
    """BAGLA geçişlidir (model A~B ve B~C'yi görünce A ile C'yi de birleştirir).
    BAGLA zinciriyle bağlanan yazımların türleri ile türsüz üyelerin SOR
    komşularının türleri birden fazlaysa (ör. türsüz "AHMET YILMAZ" hem gerçek
    kişi "Ahmet Yılmaz"a BAGLA hem tüzel "Ahmet Yılmaz İnşaat Ltd. Şti."ne SOR
    ile bağlı), türsüz uçlu BAGLA'lar SOR'a iner: yazımın kişi mi şirket mi
    olduğu avukata sorulur. İki türlü uç ya aynı türdedir (güvenli) ya da
    çift düzeyinde zaten SOR'dur."""
    ata = list(range(len(turler)))

    def _kok(x):
        while ata[x] != x:
            ata[x] = ata[ata[x]]
            x = ata[x]
        return x

    for e in ham:
        if e["karar"] == "BAGLA":
            a, b = _kok(e["_i"]), _kok(e["_j"])
            if a != b:
                ata[max(a, b)] = min(a, b)
    sor_komsu = {}
    for e in ham:
        if e["karar"] == "AVUKATA-SOR":
            for x, y in ((e["_i"], e["_j"]), (e["_j"], e["_i"])):
                if turler[x] is None and turler[y]:
                    sor_komsu.setdefault(x, set()).add(turler[y])
    bilesen = {}
    for i, t in enumerate(turler):
        tset = bilesen.setdefault(_kok(i), set())
        if t:
            tset.add(t)
        else:
            tset.update(sor_komsu.get(i, ()))
    for e in ham:
        tset = bilesen.get(_kok(e["_i"]), set())
        kopru = turler[e["_i"]] is None or turler[e["_j"]] is None
        if e["karar"] == "BAGLA" and len(tset) > 1 and kopru:
            e["karar"] = "AVUKATA-SOR"
            e["kural"] = e["kural"] + "+tur-belirsiz"
            e["nedenler"] = e["nedenler"] + ["tur_belirsiz=" + "/".join(sorted(tset))]
            e["gerekce"] = GEREKCE["tur-belirsiz"]
    return [{k: v for k, v in e.items() if not k.startswith("_")} for e in ham if e["karar"]]


def eslestir(ozneler, uyarilar=None):
    """Tüm çiftleri kural setinden geçirir; BAGLA ve AVUKATA-SOR damgalı
    çiftleri döndürür (deterministik sıra: girdi sırası korunur). Sessiz
    (ayrı özne) çiftler listelenmez. AZAMI_OZNE aşılırsa ya da öğe biçimsizse
    ValueError — kırpıp sessizce eksik tarama YAPILMAZ. İş bütçesi aşılırsa
    kalan çiftler yalnız yazım eşdeğerliğiyle karşılaştırılır ve `uyarilar`a
    (verildiyse) yazılır."""
    ozneler = list(ozneler or [])
    if len(ozneler) > AZAMI_OZNE:
        raise ValueError(f"özne sayısı {len(ozneler)} > {AZAMI_OZNE} — tarama "
                         "yapılmadı (listeyi böl ya da tekrarlı yazımları ayıkla)")
    kayitlar = [_kayit(x, i + 1) for i, x in enumerate(ozneler)]
    hazir = [_hazirla(ad, tur) for _, ad, tur in kayitlar]
    uzunluk = [len(" ".join(p[0] for p in h[0][0]["parcalar"])) for h in hazir]
    harcanan, atlanan = 0, 0
    ham = []
    for i in range(len(kayitlar)):
        for j in range(i + 1, len(kayitlar)):
            maliyet = max(1, uzunluk[i] * uzunluk[j])
            sayisal = harcanan + maliyet <= IS_BUTCESI
            if sayisal:
                harcanan += maliyet
            else:
                atlanan += 1
            k = _karar(hazir[i], hazir[j], sayisal)
            if not k["karar"]:
                continue
            id1, ad1, tur1 = kayitlar[i]
            id2, ad2, tur2 = kayitlar[j]
            a = {"id": id1, "ad": ad1}
            b = {"id": id2, "ad": ad2}
            if tur1 is not None:
                a["tur"] = tur1
            if tur2 is not None:
                b["tur"] = tur2
            ham.append({"_i": i, "_j": j, "a": a, "b": b, "skor": round(k["skor"], 3),
                        "karar": k["karar"], "kural": k["kural"],
                        "nedenler": k["nedenler"], "gerekce": k["gerekce"]})
    if atlanan and uyarilar is not None:
        uyarilar.append(f"iş bütçesi aşıldı: {atlanan} çift yalnız yazım eşdeğerliğiyle karşılaştırıldı "
                        "(sayısal benzerlik bakılmadı) — listeyi bölüp yeniden tarayın")
    return _liste_denetimi(ham, [h[1] for h in hazir])


def asiri_uzun_adlar(ozneler):
    """AZAMI_AD'ı aşan adlar (yalnız yazım eşdeğerliğiyle karşılaştırılır) —
    çağıran bunu görünür uyarıya çevirir."""
    out = []
    for i, x in enumerate(ozneler or []):
        ad = _kayit(x, i + 1)[1]
        if len(" ".join(p[0] for p in _parcalar(_on_isle(ad)))) > AZAMI_AD:
            out.append(ad[:40] + "…")
    return out


def _girdi_oku(yol):
    if not os.path.isfile(yol):
        raise ValueError(f"girdi dosyası yok: {yol}")
    if os.path.getsize(yol) > AZAMI_BAYT:
        raise ValueError(f"girdi {AZAMI_BAYT} bayttan büyük — okunmadı")
    with open(yol, encoding="utf-8-sig") as f:
        veri = json.load(f)
    if not isinstance(veri, list):
        raise ValueError("girdi JSON bir liste olmalı: [\"ad\", ...] ya da [{\"ad\": ...}, ...]")
    return veri


def main():
    ap = argparse.ArgumentParser(
        description="M9 özne-varyant eşleştirici (advisory — karar avukatta)")
    ap.add_argument("adlar", nargs="*", help="doğrudan ad listesi")
    ap.add_argument("--girdi", default=None, help="JSON dosyası")
    ap.add_argument("--json", action="store_true", help="makine-okur çıktı")
    args = ap.parse_args()

    uyarilar = []
    try:
        ozneler = _girdi_oku(args.girdi) if args.girdi else list(args.adlar)
        sonuc = eslestir(ozneler, uyarilar)
        uyarilar += [f"çok uzun ad yalnız yazım eşdeğerliğiyle karşılaştırıldı: «{a}»"
                     for a in asiri_uzun_adlar(ozneler)]
    except (ValueError, OSError, json.JSONDecodeError) as e:
        print(f"özne-eşleştirici: GİRDİ HATASI — {e}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        print(json.dumps({"esik_bagla": BAGLA_ESIK, "esik_sor": SOR_ESIK,
                          "kural_seti": "v0.5.18",
                          "bagla_kosulu": "yazim-esdegerligi: katlanmis-esit | birlesik-esit",
                          "eslesmeler": sonuc, "uyarilar": uyarilar},
                         ensure_ascii=False))
        sys.exit(0)
    for u in uyarilar:
        print(f"  ! {u}")
    if not sonuc:
        print("özne-eşleştirici: BAGLA/AVUKATA-SOR çifti yok (tüm özneler AYRI).")
    for e in sonuc:
        isaret = "✓" if e["karar"] == "BAGLA" else "?"
        print(f"  {isaret} {e['karar']} [{e['skor']}] «{e['a']['ad']}» ↔ "
              f"«{e['b']['ad']}» — {e['gerekce']}  ({', '.join(e['nedenler'])})")
    sys.exit(0)  # advisory — karar vermez, damga basar


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
ictihat_muhakeme_denetim.py — oa-kontrol İÇTİHAT MUHAKEME ZİNCİRİ MEKANİK KAPISI
(MODÜL 2 — bkz. `oa-kiyas/references/ictihat-muhakeme-sablonu.md`)

Bu script bir dilekçe taslağındaki (dış çıktı) HER içtihat künyesinin gerçekten
"muhakeme edilmiş" sayılabilmesi için gereken YAPISAL izleri deterministik
denetler. "Çıplak künye" (yalnız daire+esas+karar, arkasında bir NN-ictihat-
muhakeme.md kaydı olmadan) dilekçede kalamaz — bu script o yasağın mekanik
karşılığıdır.

NOT (R4 — terim netliği): şemanın "İLLİYET" alanı `oa-illiyet`'in modellediği
fiil→netice NEDENSELLİK grafıyla karışmasın diye **DAVAYA-BAĞ** olarak
adlandırılmıştır (bkz. `oa-kiyas/references/ictihat-muhakeme-sablonu.md`);
bu bir analoji/emsal-uygunluk bağıdır, nedensellik değildir.

── SCRIPT NE YAPAR / NE YAPMAZ (bağlayıcı sınır) ──
Script "bu içtihat GERÇEKTEN ilgili mi" MUHAKEMESİNE GİRMEZ. Yalnız üç şeyi
mekanik olarak denetler: (1) VARLIK — dilekçedeki her künye için bir muhakeme
kaydı var mı; (2) BAĞ — o kaydın KAYNAK-İZİ dosyası gerçekten diskte var mı ve
künye o dosyada bir dize olarak geçiyor mu; (3) ALAN BÜTÜNLÜĞÜ — İLGİLİ-KISIM/
DAVAYA-BAĞ/DAMGA alanları dolu mu, DAMGA=ALEYHE-AYIRT ise AYIRT-ETME dolu mu.
"İlgili kısım gerçekten ilgili mi", "illiyet muhakemesi isabetli mi", "hangi
dairenin baktığı doğru mu" gibi İÇERİK/MUHAKEME soruları bu scriptin işi
DEĞİLDİR — onlar oa-kontrol A listesi + avukatın nihai gözüdür (model kurar,
script yalnız YAPISAL/MEKANİK denetler; "sahte kesinlik" üretmez).

Script muhakeme kayıtlarını ASLA "temizlemez"/düzeltmez — yalnız okur ve
raporlar. Kayıt eksikse/bozuksa avukat (veya oa-kiyas/oa-kontrol muhakemesi)
kaydı tamamlar; script bunun YERİNE geçmez.

── ÜÇ KAPI ──
G1 (UYARI — BLOKLAMAZ): Dilekçede hiç doğrulanabilir içtihat atfı (esas/karar
   no'lu künye) yoksa "emsal içtihat yok — muhakeme zayıf" uyarısı basılır.
   Bu, "esaslı mı" hükmü DEĞİLDİR; yalnız bir eksiklik bulgusudur.
   **`--tip` ile bağlanır (M3-2/R6):** bu uyarı yalnız "esaslı" dilekçe
   tiplerinde (dava/cevap/istinaf/temyiz/aym_bireysel) anlamlıdır; yemin
   teklif/idari kanal başvurusu gibi hafif tiplerde içtihat atfı yapısal
   olarak beklenmez — bu tiplerde uyarı [BİLGİ]'ye düşer (yine bloklamaz).
   `--tip` verilmezse veya tanınmayan bir değerse FAIL-SAFE: esaslı sayılır
   (uyarı bastırılmaz) — yalnız açıkça "esaslı değil" listesindeki tipler
   bastırır.

G2 (ENGEL — yalnız yapısal): Dilekçedeki HER içtihat künyesi için:
   - `_oa/cikti/*ictihat-muhakeme*.md` kayıtları arasında künyesi
     (`kunye_normalize` ile) eşleşen bir kayıt VAR mı? Eşleşme yalnız
     ESAS+KARAR no'suyla değil, (biliniyorsa) DAİRE ile de aranır —
     Türk yargı sisteminde esas/karar no'ları HER dairede yılda sıfırdan
     başladığından aynı numaralar onlarca farklı dairede aynı anda var
     olabilir; taraflardan biri esas/karar aynı ama farklı bir daireye
     aitse EŞLEŞMEZ. Dilekçe atfı hangi daireye ait olduğunu belirtmiyorsa
     VE aynı esas/karar no'suna sahip birden fazla FARKLI daireye ait kayıt
     varsa bu durum belirsiz sayılır → fail-closed ENGEL (`daire_key` —
     `kunye_ortak.daire_key`).
   - O kaydın KAYNAK-İZİ alanındaki dosya `--dokum-dizin` içinde GERÇEKTEN
     var mı ve künye (esas/karar sayıları) o dosyada bir dize olarak geçiyor mu?
   - İLGİLİ-KISIM / DAVAYA-BAĞ / DAMGA alanları DOLU mu?
   Yoksa → "çıplak/muhakeme edilmemiş atıf" → ENGEL.

G3 (ENGEL): Eşleşen kaydın DAMGA değerine göre:
   - DAMGA=ALEYHE            → dilekçeye GİREMEZ (TESLİM ENGELİ, anayasa m.6 —
                                 müvekkil-aleyhi dış çıktı yasağı).
   - DAMGA=ALEYHE-AYIRT      → AYIRT-ETME alanı DOLU olmalı; boşsa ENGEL
                                 (fail-closed: boş AYIRT-ETME = ALEYHE gibi işlem görür).
   - DAMGA=NOTR              → UYARI ("nötr içtihat neden dilekçede?"); BLOKLAMAZ.
   - DAMGA yok/geçersiz enum → FAIL-CLOSED ENGEL ("muhakeme edilmemiş" sayılır;
                                 hiçbir hâlde varsayılan-nötr/geçerli sayılmaz).
   - DAMGA=LEHE              → sorun yok.

G-EK (UYARI — BLOKLAMAZ, YENİ-2 backlog): Aynı esas+karar+daireye ait BİRDEN
   FAZLA muhakeme kaydı varsa VE bu kayıtların DAMGA değerleri birbirinden
   FARKLIYSA (ör. biri LEHE biri ALEYHE), "ÇELİŞEN DAMGA" UYARISI basılır —
   script "temiz" (engelsiz) adayı bulup kullanabilir (mekanik kapı yine
   açık kalabilir) ama bu yapısal tutarsızlığı SESSİZCE gizlemez.

Paylaşımlı `kunye_normalize()` — bkz. `kunye_ortak.py` (M2-3'te `kunye_teyit.py`
ile PAYLAŞILMASI planlanan ortak yardımcı; esas/karar normalizasyon mantığı).

Kullanım:
  python ictihat_muhakeme_denetim.py <taslak.md> \
      [--muhakeme-dizin _oa/cikti] [--dokum-dizin _oa/teyit/dokum] [--kok <klasör>]

--kok verilirse --muhakeme-dizin/--dokum-dizin varsayılanları
<KOK>/_oa/cikti ve <KOK>/_oa/teyit/dokum olur (oa_hafiza.py/tam_tur.py/
kunye_teyit.py --kok simetrisi; cwd'den BAĞIMSIZ). Açıkça verilen bayraklar
her zaman --kok'u ezer.

Çıkış kodları:
  0 = G2/G3 engeli YOK (G1/NOTR uyarıları olsa bile) — mekanik kapı AÇIK
  1 = en az bir G2 (çıplak atıf / eksik alan / kaynak-izi kırık) ya da G3
      (ALEYHE / eksik AYIRT-ETME / damgasız-geçersiz) engeli VAR — TESLİM ENGELİ
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
import os
import re
import sys

BURA = os.path.dirname(os.path.abspath(__file__))
if BURA not in sys.path:
    sys.path.insert(0, BURA)

import kunye_ortak as ko  # noqa: E402

VARSAYILAN_MUHAKEME = os.path.join("_oa", "cikti")
VARSAYILAN_DOKUM = os.path.join("_oa", "teyit", "dokum")

DAMGA_ENUM = {"LEHE", "ALEYHE", "ALEYHE-AYIRT", "NOTR"}

# G1 — "esaslı dilekçe" tip listesi (M3-2/R6): dilekce_denetim.py --tip
# taksonomisine bağlı. Yalnız bu listede AÇIKÇA "esaslı değil" sayılan tipler
# G1 uyarısını [BİLGİ]'ye düşürür; her başka değer (tanınmayan tip dahil)
# fail-safe olarak esaslı sayılır.
ESASLI_OLMAYAN_TIPLER = {"yemin", "idari-kanal"}


def esasli_mi(tip):
    """R6: G1 (emsal içtihat yokluğu) uyarısı yalnız 'esaslı' dilekçe
    tiplerinde (dava/cevap/istinaf/temyiz/aym_bireysel) UYARI olarak basılır;
    yemin teklif/idari kanal başvurusu gibi hafif tiplerde içtihat atfı
    yapısal olarak beklenmez. `tip` boş/None/tanınmayansa FAIL-SAFE: True
    (esaslı) — yalnız ESASLI_OLMAYAN_TIPLER'de AÇIKÇA sayılan tipler False
    döner."""
    if not tip:
        return True
    return tip not in ESASLI_OLMAYAN_TIPLER

KUNYE_LINE_RE = re.compile(r"^\*\*KUNYE:\*\*\s*(.+)$", re.M)
KAYNAK_IZI_LINE_RE = re.compile(r"^\*\*KAYNAK-IZI:\*\*\s*(.+)$", re.M)
DAMGA_LINE_RE = re.compile(r"^\*\*DAMGA:\*\*\s*(.+)$", re.M)


def _bolum_al(metin, baslik):
    """'## <baslik>' bölümünün içeriğini (bir sonraki '## ' başlığa veya metin
    sonuna kadar) döndürür; bölüm yoksa None."""
    m = re.search(r"^##\s*" + re.escape(baslik) + r"\s*$", metin, re.M)
    if not m:
        return None
    bas = m.end()
    sonraki = re.search(r"^##\s+", metin[bas:], re.M)
    son = bas + sonraki.start() if sonraki else len(metin)
    return metin[bas:son].strip()


class MuhakemeKaydi:
    __slots__ = ("dosya", "kunye_ham", "esas", "karar", "daire", "kaynak_izi",
                 "damga_ham", "damga", "ilgili_kisim", "davaya_bag", "ayirt_etme")

    def __init__(self, dosya, metin):
        self.dosya = dosya
        m = KUNYE_LINE_RE.search(metin)
        self.kunye_ham = m.group(1).strip() if m else None
        self.esas, self.karar = ko.kunye_normalize(self.kunye_ham or "")
        self.daire = ko.daire_key(self.kunye_ham or "")

        m = KAYNAK_IZI_LINE_RE.search(metin)
        self.kaynak_izi = m.group(1).strip() if m else None

        m = DAMGA_LINE_RE.search(metin)
        self.damga_ham = m.group(1).strip() if m else None
        self.damga = self.damga_ham.upper() if self.damga_ham else None

        self.ilgili_kisim = _bolum_al(metin, "İLGİLİ-KISIM")
        # R4: eski "İLLİYET" alanı DAVAYA-BAĞ oldu (oa-illiyet nedensellik
        # grafıyla karışmasın diye); geriye dönük uyumluluk için eski "##
        # İLLİYET" başlığı da hâlâ okunur (henüz göçürülmemiş eski kayıtlar).
        self.davaya_bag = _bolum_al(metin, "DAVAYA-BAĞ") or _bolum_al(metin, "İLLİYET")
        self.ayirt_etme = _bolum_al(metin, "AYIRT-ETME")

    def kunye_var_mi(self):
        return self.esas is not None or self.karar is not None

    def eslesir(self, esas, karar, daire_key=None):
        """Esas+karar EŞLEŞMESİ tek başına YETERSİZDİR — Türk yargı sisteminde
        esas/karar no'ları HER dairede yılda sıfırdan başlar, aynı numaralar
        onlarca farklı dairede aynı anda var olabilir. Her iki tarafta da
        (bu kayıt + dilekçe atfı) tanınabilir bir daire varsa DAİRE de
        eşleşmelidir; taraflardan biri daire içermiyorsa (biçim/format
        sınırı) geriye dönük uyumluluk için yalnız esas/karar ile eşleşir —
        bu durum çağıran tarafta (_atif_denetle) ayrıca çok-daireli çakışma
        belirsizliği olarak denetlenir (fail-closed)."""
        if self.esas != esas or self.karar != karar:
            return False
        if daire_key is not None and self.daire is not None:
            return self.daire == daire_key
        return True


def muhakeme_kayitlarini_yukle(muhakeme_dizin):
    """`_oa/cikti/*ictihat-muhakeme*.md` desenindeki dosyaları MuhakemeKaydi
    listesine çevirir (dosya-sırasıyla, sabit sıralı)."""
    kayitlar = []
    if not muhakeme_dizin or not os.path.isdir(muhakeme_dizin):
        return kayitlar
    desen = os.path.join(muhakeme_dizin, "*ictihat-muhakeme*.md")
    for yol in sorted(glob.glob(desen)):
        if not os.path.isfile(yol):
            continue
        try:
            with open(yol, encoding="utf-8", errors="replace") as f:
                metin = f.read()
        except OSError:
            continue
        kayitlar.append(MuhakemeKaydi(yol, metin))
    return kayitlar


def _yol_coz(deger, kok):
    if not deger:
        return None
    if os.path.isabs(deger):
        return deger
    return os.path.join(kok, deger)


def _dizin_icinde_mi(yol, dizin):
    try:
        yol_n = os.path.normcase(os.path.normpath(os.path.abspath(yol)))
        dizin_n = os.path.normcase(os.path.normpath(os.path.abspath(dizin)))
    except OSError:
        return False
    return yol_n == dizin_n or yol_n.startswith(dizin_n + os.sep)


def kaynak_izi_denetle(kayit, kok, dokum_dizin):
    """KAYNAK-İZİ alanının işaret ettiği dosyanın (a) dökum dizini İÇİNDE
    gerçekten var olduğunu ve (b) künyenin (esas/karar) o dosyada BİR DİZE
    OLARAK geçtiğini denetler. Sorun listesini döndürür (boşsa temiz)."""
    sorunlar = []
    if not kayit.kaynak_izi:
        sorunlar.append("KAYNAK-IZI alanı boş/yok")
        return sorunlar

    yol = _yol_coz(kayit.kaynak_izi, kok)
    if not _dizin_icinde_mi(yol, dokum_dizin):
        sorunlar.append(
            "KAYNAK-IZI dökum dizini dışında bir yola işaret ediyor "
            f"('{kayit.kaynak_izi}' → {dokum_dizin} içinde değil)"
        )
        return sorunlar
    if not os.path.isfile(yol):
        sorunlar.append(f"KAYNAK-IZI dosyası dökum dizininde bulunamadı: {kayit.kaynak_izi}")
        return sorunlar

    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            icerik = f.read()
    except OSError as e:
        sorunlar.append(f"KAYNAK-IZI dosyası okunamadı: {kayit.kaynak_izi} ({e})")
        return sorunlar

    if not (kayit.esas or kayit.karar):
        sorunlar.append("KUNYE alanından esas/karar no çıkarılamadı — dize denetimi yapılamaz")
        return sorunlar
    if kayit.esas and not ko.sayi_var(icerik, kayit.esas):
        sorunlar.append(f"künyenin esas no'su ({kayit.esas}) KAYNAK-IZI dosyasında dize olarak geçmiyor")
    if kayit.karar and not ko.sayi_var(icerik, kayit.karar):
        sorunlar.append(f"künyenin karar no'su ({kayit.karar}) KAYNAK-IZI dosyasında dize olarak geçmiyor")
    return sorunlar


def alan_butunlugu_denetle(kayit):
    """G2 — İLGİLİ-KISIM / DAVAYA-BAĞ / DAMGA alanları DOLU mu (yalnız varlık;
    içerik isabeti muhakeme işidir, bu fonksiyon YARGILAMAZ)."""
    sorunlar = []
    if not kayit.ilgili_kisim:
        sorunlar.append("İLGİLİ-KISIM alanı boş/yok")
    if not kayit.davaya_bag:
        sorunlar.append("DAVAYA-BAĞ alanı boş/yok")
    if not kayit.damga_ham:
        sorunlar.append("DAMGA alanı boş/yok")
    return sorunlar


def damga_denetle(kayit):
    """G3 — DAMGA değerinin anlamına göre engel/uyarı üretir.
    Döndürür: (engeller: [str,...], uyarilar: [str,...])."""
    engeller, uyarilar = [], []
    if not kayit.damga_ham:
        engeller.append(
            "DAMGA yok — fail-closed: 'muhakeme edilmemiş' sayılır "
            "(varsayılan-nötr/geçerli VARSAYILMAZ)"
        )
        return engeller, uyarilar
    if kayit.damga not in DAMGA_ENUM:
        engeller.append(
            f"DAMGA geçersiz enum değeri ('{kayit.damga_ham}') — fail-closed: "
            "'muhakeme edilmemiş' sayılır"
        )
        return engeller, uyarilar

    if kayit.damga == "ALEYHE":
        engeller.append(
            "DAMGA=ALEYHE — bu içtihat dilekçeye GİREMEZ (TESLİM ENGELİ, "
            "anayasa m.6 — müvekkil-aleyhi dış çıktı yasağı). İç analizde/"
            "oa-antitez cephaneliğinde tutulur, dış çıktıya sızmaz."
        )
    elif kayit.damga == "ALEYHE-AYIRT":
        if not kayit.ayirt_etme:
            engeller.append(
                "DAMGA=ALEYHE-AYIRT ama AYIRT-ETME alanı boş — fail-closed: "
                "boş AYIRT-ETME ile ALEYHE-AYIRT geçersizdir, kayıt ALEYHE gibi "
                "işlem görür ve dilekçeye GİREMEZ"
            )
    elif kayit.damga == "NOTR":
        uyarilar.append(
            "DAMGA=NOTR — nötr içtihat neden dilekçede kullanılıyor? "
            "(bloklamaz; ama nötr kararın dilekçedeki varlığı gözden geçirilmeli)"
        )
    # LEHE → sorun yok
    return engeller, uyarilar


def taslaktaki_atiflari_bul(metin):
    """Dilekçedeki esas/karar no'lu içtihat atıflarını (esas, karar, daire_key)
    üçlüsüyle tekilleştirip döndürür; sırayı korur. DAİRE de anahtara dahildir
    çünkü aynı esas/karar no'suyla FARKLI dairelere ait iki ayrı atıf aynı
    dilekçede geçebilir (ör. 4. HD'nin ve 11. HD'nin aynı numaralı kararları) —
    bunlar tek bir atıfmış gibi birleştirilip biri sessizce kaybedilemez."""
    ham = ko.esas_karar_atiflari(metin)
    gorulen, tekil = set(), []
    for a in ham:
        anahtar = (a["esas"], a["karar"], a.get("daire_key"))
        if anahtar in gorulen:
            continue
        if a["esas"] is None and a["karar"] is None:
            continue
        gorulen.add(anahtar)
        tekil.append(a)
    return tekil


def _daire_goster(daire_key):
    if not daire_key:
        return "belirtilmemiş"
    no, aile = daire_key
    return f"{no}. {aile}"


def _esas_karar_eslesenler(atif, kayitlar):
    """Yalnız esas/karar no'su eşleşen TÜM kayıtlar (daire bakılmaksızın) —
    çok-daireli çakışma/belirsizlik tespiti için kullanılır."""
    return [k for k in kayitlar if k.esas == atif["esas"] and k.karar == atif["karar"]]


def _atif_icin_kayit_bul(atif, kayitlar):
    """Esas/karar VE (biliniyorsa) DAİRE eşleşen kayıtları döndürür — bkz.
    MuhakemeKaydi.eslesir(). Daire eşleşmesi olmadan yalnız esas/karar
    eşleşmesi ARTIK YETERLİ SAYILMAZ (bkz. anayasa m.6 — çok-daireli çakışma)."""
    return [k for k in kayitlar
            if k.eslesir(atif["esas"], atif["karar"], atif.get("daire_key"))]


def _celisen_damga_uyarisi(adaylar):
    """YENİ-2 (backlog): AYNI esas+karar+daireye ait BİRDEN FAZLA muhakeme
    kaydı varsa ve bunların DAMGA değerleri birbirinden FARKLIYSA (ör. biri
    LEHE biri ALEYHE), bu yapısal bir tutarsızlıktır — script "temiz" adayı
    sessizce seçip ALEYHE ikizini gölgelememelidir. UYARI döndürür (None =
    çelişki yok); bu bir ENGEL değildir, yalnız görünürlük sağlar — hangi
    kaydın isabetli olduğu avukat/model muhakemesidir."""
    if len(adaylar) < 2:
        return None
    damgalar = {k.damga for k in adaylar if k.damga}
    if len(damgalar) < 2:
        return None
    dosyalar = ", ".join(f"{k.dosya} ({k.damga_ham})" for k in adaylar if k.damga_ham)
    return (
        "ÇELİŞEN DAMGA (YENİ-2): aynı esas/karar/daireye ait BİRDEN FAZLA "
        f"muhakeme kaydı var ve DAMGA değerleri farklı — {dosyalar}. Bu "
        "yapısal bir tutarsızlıktır (aynı karar iki farklı damga taşıyamaz); "
        "hangi kaydın isabetli olduğu avukat/model muhakemesiyle çözülmeli, "
        "temiz olan sessizce seçilip diğeri gölgelenmemeli."
    )


def _atif_denetle(atif, kayitlar, kok, dokum_dizin):
    """Bir dilekçe atfı için tüm denetimi yürütür.
    Döndürür: (durum: 'OK'|'BLOK', engeller: [str], uyarilar: [str], kayit veya None)."""
    esas_karar_eslesen = _esas_karar_eslesenler(atif, kayitlar)
    farkli_daireler = {k.daire for k in esas_karar_eslesen if k.daire is not None}

    # Dilekçe atfı hangi daireye ait olduğunu belirtmiyor (merci taranamadı)
    # AMA aynı esas/karar no'suna sahip BİRDEN FAZLA FARKLI daireye ait kayıt
    # varsa: hangisinin geçerli olduğu belirlenemez — fail-closed ENGEL
    # (sessizce "ilk temiz aday"a kayıp ALEYHE kaydı arkasına saklanmasın).
    if atif.get("daire_key") is None and len(farkli_daireler) > 1:
        daire_listesi = ", ".join(sorted(_daire_goster(d) for d in farkli_daireler))
        return ("BLOK",
                [f"Aynı esas/karar no'suna (E. {atif['esas'] or '—'} / K. {atif['karar'] or '—'}) "
                 f"sahip BİRDEN FAZLA FARKLI DAİREYE ait muhakeme kaydı bulundu "
                 f"({daire_listesi}); dilekçe atfında merci/daire belirtilmediğinden hangi "
                 "kaydın geçerli olduğu belirlenemiyor — fail-closed ENGEL (esas/karar no'ları "
                 "her dairede yılda sıfırdan başladığından çakışma olağandır; anayasa m.6 ihtiyatı)"],
                [], None)

    adaylar = _atif_icin_kayit_bul(atif, kayitlar)
    if not adaylar:
        if esas_karar_eslesen:
            eslesen_daireler = ", ".join(sorted(_daire_goster(k.daire) for k in esas_karar_eslesen))
            return ("BLOK",
                    [f"Bu esas/karar no'suna ait muhakeme kaydı/kayıtları var ({eslesen_daireler}) "
                     f"ama HİÇBİRİ dilekçe atfındaki daireyle ({_daire_goster(atif.get('daire_key'))}) "
                     "eşleşmiyor — farklı bir daireye ait kayıt bu atıf için KULLANILAMAZ "
                     "(esas/karar no'ları her dairede yılda sıfırdan başlar, çakışma olağandır)"],
                    [], None)
        return ("BLOK",
                ["Bu künye için hiçbir _oa/cikti/*ictihat-muhakeme*.md kaydı yok "
                 "(çıplak/muhakeme edilmemiş atıf) — dilekçede çıplak künye kalamaz"],
                [], None)

    # YENİ-2: aynı esas/karar/daireye ait birden çok aday ÇELİŞEN damga
    # taşıyorsa, hangi sonuç dönerse dönsün (OK ya da BLOK) bu tutarsızlık
    # UYARI olarak görünür kalır — temiz aday sessizce seçilip ALEYHE ikizi
    # gölgelenmez.
    celisen_uyari = _celisen_damga_uyarisi(adaylar)

    # Birden çok aday varsa: TAM temiz (engelsiz) olan varsa onu kullan;
    # yoksa raporlama için İLK adayı esas al (deterministik).
    en_iyi = None
    en_iyi_engeller, en_iyi_uyarilar = None, None
    for kayit in adaylar:
        engeller = list(alan_butunlugu_denetle(kayit))
        engeller += kaynak_izi_denetle(kayit, kok, dokum_dizin)
        damga_engel, damga_uyari = damga_denetle(kayit)
        engeller += damga_engel
        if not engeller:
            uyarilar = list(damga_uyari)
            if celisen_uyari:
                uyarilar.append(celisen_uyari)
            return ("OK", [], uyarilar, kayit)
        if en_iyi is None:
            en_iyi, en_iyi_engeller, en_iyi_uyarilar = kayit, engeller, damga_uyari

    en_iyi_uyarilar = list(en_iyi_uyarilar or [])
    if celisen_uyari:
        en_iyi_uyarilar.append(celisen_uyari)
    return ("BLOK", en_iyi_engeller, en_iyi_uyarilar, en_iyi)


def rapor_yaz(taslak_yolu, atiflar, sonuclar, muhakeme_dizin, dokum_dizin, kutuk_bos_mu,
              tip=None):
    print("=" * 72)
    print("İÇTİHAT MUHAKEME DENETİMİ — oa-kontrol (deterministik, YAPISAL)")
    print("=" * 72)
    print(f"Taslak            : {taslak_yolu}")
    print(f"Muhakeme kayıtları: {muhakeme_dizin}")
    print(f"Dökum dizini      : {dokum_dizin}")
    if kutuk_bos_mu:
        print(f"[BİLGİ] Muhakeme kayıtları dizini boş/yok ({muhakeme_dizin}) — "
              "hiçbir *ictihat-muhakeme*.md kaydı yüklenemedi; aşağıdaki atıflar "
              "bu yüzden 'çıplak' görünüyor olabilir.")

    print("\n" + "-" * 72)
    print("[G1] EMSAL İÇTİHAT TARAMASI" + (f" (tip: {tip})" if tip else ""))
    print("-" * 72)
    if not atiflar:
        if esasli_mi(tip):
            print("[UYARI] Dilekçede esas/karar no'lu hiçbir içtihat atfı bulunamadı — "
                  "emsal içtihat yok, muhakeme zayıf. (Bu bir 'esaslı mı' hükmü DEĞİLDİR; "
                  "yalnız bir eksiklik bulgusudur — bloklamaz.)")
        else:
            print(f"[BİLGİ] Dilekçede içtihat atfı yok; tip='{tip}' esaslı-dilekçe "
                  "listesinde değil (R6: yemin/idari-kanal) — bu tipte içtihat atfı "
                  "yapısal olarak beklenmez, emsal-yokluğu uyarısı bu yüzden atlandı "
                  "(zaten bloklamıyordu).")
    else:
        print(f"Dilekçede {len(atiflar)} tekil içtihat atfı bulundu.")

    genel_engel = False
    if atiflar:
        print("\n" + "-" * 72)
        print(f"[G2/G3] ATIF BAŞINA MUHAKEME KAYDI DENETİMİ ({len(atiflar)} atıf)")
        print("-" * 72)
        for atif, (durum, engeller, uyarilar, kayit) in zip(atiflar, sonuclar):
            kunye_goster = (f"E. {atif['esas'] or '—'} / K. {atif['karar'] or '—'} / "
                             f"Daire: {_daire_goster(atif.get('daire_key'))}")
            etiket = "[OK]  " if durum == "OK" else "[BLOK]"
            print(f"\n{etiket} (satır {atif['satir_no']}) {atif['metin']}  ({kunye_goster})")
            if kayit is not None:
                print(f"       ↳ eşleşen kayıt: {kayit.dosya}")
                if kayit.damga_ham:
                    print(f"       ↳ DAMGA        : {kayit.damga_ham}")
            for e in engeller:
                print(f"       ✗ {e}")
                genel_engel = True
            for u in uyarilar:
                print(f"       ⚠ {u}")

    print("\n" + "-" * 72)
    blok_sayisi = sum(1 for (d, *_r) in sonuclar if d == "BLOK")
    ok_sayisi = len(sonuclar) - blok_sayisi
    print(f"ÖZET: {len(atiflar)} atıf  |  OK {ok_sayisi}  |  BLOK {blok_sayisi}")
    if genel_engel:
        print("SONUÇ: TESLİM ENGELİ — çıplak/eksik/ALEYHE atıf(lar) giderilmeden dilekçe "
              "teslime hazır sayılamaz.")
    else:
        print("SONUÇ: G2/G3 engeli YOK — mekanik kapı AÇIK. (İçerik/muhakeme isabeti hâlâ "
              "oa-kontrol A listesi + avukatın nihai gözü işidir; bu script yalnız yapısal "
              "varlık+bağ denetler.)")
    return genel_engel


def main():
    ap = argparse.ArgumentParser(
        description="oa-kontrol içtihat muhakeme zinciri mekanik kapısı — "
                     "çıplak/ALEYHE/eksik-alanlı içtihat atfı teslim engelidir.")
    ap.add_argument("taslak", help="Taslak dilekçe/mütalaa (.md/.txt)")
    ap.add_argument("--kok", default=None,
                     help="çalışma kökü (kunye_teyit.py/oa_hafiza.py/tam_tur.py simetrisi); "
                          "verilirse --muhakeme-dizin/--dokum-dizin varsayılanları "
                          "<KOK>/_oa/cikti, <KOK>/_oa/teyit/dokum olur")
    ap.add_argument("--muhakeme-dizin", default=None,
                     help="İçtihat muhakeme kayıtlarının dizini "
                          f"(varsayılan: --kok yoksa {VARSAYILAN_MUHAKEME}, "
                          f"varsa <KOK>/{VARSAYILAN_MUHAKEME})")
    ap.add_argument("--dokum-dizin", default=None,
                     help="Ham MCP döküm dizini — KAYNAK-IZI'nin doğrulandığı yer "
                          f"(varsayılan: --kok yoksa {VARSAYILAN_DOKUM}, "
                          f"varsa <KOK>/{VARSAYILAN_DOKUM})")
    ap.add_argument("--tip", default=None,
                     help="(opsiyonel, M3-2/R6) dilekce_denetim.py --tip değeri; "
                          "yalnız G1 (emsal içtihat yokluğu) uyarısının 'esaslı' "
                          "dilekçe tiplerinde mi UYARI yoksa [BİLGİ] olarak mı "
                          "basılacağını belirler (dava/cevap/istinaf/temyiz/"
                          "aym_bireysel=esaslı; yemin/idari-kanal=değil). G2/G3 "
                          "engellerini ETKİLEMEZ.")
    args = ap.parse_args()

    if not os.path.isfile(args.taslak):
        sys.exit(f"HATA: taslak bulunamadı: {args.taslak}")

    kok = args.kok if args.kok is not None else "."
    muhakeme_dizin = args.muhakeme_dizin if args.muhakeme_dizin is not None else (
        os.path.join(args.kok, VARSAYILAN_MUHAKEME) if args.kok else VARSAYILAN_MUHAKEME)
    dokum_dizin = args.dokum_dizin if args.dokum_dizin is not None else (
        os.path.join(args.kok, VARSAYILAN_DOKUM) if args.kok else VARSAYILAN_DOKUM)

    with open(args.taslak, encoding="utf-8", errors="replace") as f:
        metin = f.read()

    atiflar = taslaktaki_atiflari_bul(metin)
    kayitlar = muhakeme_kayitlarini_yukle(muhakeme_dizin)

    sonuclar = [_atif_denetle(a, kayitlar, kok, dokum_dizin) for a in atiflar]

    engel_var = rapor_yaz(args.taslak, atiflar, sonuclar, muhakeme_dizin, dokum_dizin,
                           kutuk_bos_mu=not kayitlar, tip=args.tip)

    sys.exit(1 if engel_var else 0)


if __name__ == "__main__":
    main()

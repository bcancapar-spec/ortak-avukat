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
VARSAYILAN_KUTUK = os.path.join("_oa", "teyit", "kunye-teyit.md")

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
# v0.5.7 — teyit anında kaydedilen resmî bağlantı (bkz. oa-ictihat v0.5.5.3:
# `oa_hafiza.py teyit --kaynak-url`). Dilekçe-link tutarlılığı [G4] bunu okur.
KAYNAK_URL_LINE_RE = re.compile(r"^\*\*KAYNAK-URL:\*\*\s*(\S+)\s*$", re.M)
# Dilekçe metnindeki http(s) bağlantıları — [G4] uydurma-link taraması.
HTTP_URL_RE = re.compile(r"https?://[^\s\)\]\>»\"']+")
# v0.5.8 [G5] AŞILMIŞ-İÇTİHAT (semantica superseded deseninin devşirmesi —
# bkz. anayasa m.0 dış desen devşirme protokolü): bir içtihadın sonradan
# İBK / kanun değişikliği / daire kaymasıyla AŞILDIĞI kütüğe işlenirse,
# o karar LEHE dayanak olarak dilekçeye GİREMEZ. Alanlar teyit/damga anında
# elle doldurulur (otomatik aşan-kaynak taraması bilinçli olarak v2'ye
# ertelendi — kaş-göz ilkesi).
ASAN_KAYNAK_LINE_RE = re.compile(r"^\*\*AŞAN-KAYNAK:\*\*\s*(.+)$", re.M)
ASILMA_TARIHI_LINE_RE = re.compile(r"^\*\*AŞILMA-TARİHİ:\*\*\s*(.+)$", re.M)
GECERLILIK_BITIS_LINE_RE = re.compile(r"^\*\*GEÇERLİLİK-BİTİŞ:\*\*\s*(.+)$", re.M)


def _bolum_al(metin, baslik):
    """'## <baslik>' bölümünün içeriğini (bir sonraki markdown başlığına —
    HER seviyeden `#` — veya metin sonuna kadar) döndürür; bölüm yoksa None.

    P0-3 DÜZELTME (v0.5.5): durdurucu ESKİDEN yalnız `^##\\s+` arıyordu; ama
    çok-bölümlü dosyalarda her kayıt `# İçtihat Muhakeme Kaydı — <ts>` (TEK
    `#`) başlığıyla başlar (bkz. `oa-kiyas/references/ictihat-muhakeme-
    sablonu.md` örnek kayıtları: `# 01 — ...`). Tek-`#` durdurucu SAYILMAYINCA
    bir SONRAKİ kaydın başlık satırı bu bölümün (ör. AYIRT-ETME) içeriğine
    SIZIYORDU — boş AYIRT-ETME dolu görünüp G3'ün fail-closed ALEYHE-AYIRT
    denetimini deliyordu. Artık HER `#`..`######` başlığı (satır başı) durdurucu
    sayılır — `kunye_ortak.bolumlere_ayir`'ın `**KUNYE:**` ayracıyla ayrıştırdığı
    her bölüm kendi alanlarını KENDİ içinde tutar, komşu kayda taşmaz."""
    m = re.search(r"^##\s*" + re.escape(baslik) + r"\s*$", metin, re.M)
    if not m:
        return None
    bas = m.end()
    sonraki = re.search(r"^#{1,6}\s+", metin[bas:], re.M)
    son = bas + sonraki.start() if sonraki else len(metin)
    return metin[bas:son].strip()


GECERSIZ_KILINDI_RE = re.compile(r"^\*\*GEÇERSİZ-KILINDI:\*\*", re.M)


class MuhakemeKaydi:
    __slots__ = ("dosya", "kunye_ham", "esas", "karar", "daire", "kaynak_izi",
                 "damga_ham", "damga", "ilgili_kisim", "davaya_bag", "ayirt_etme",
                 "gecersiz", "kaynak_url", "asan_kaynak", "asilma_tarihi",
                 "gecerlilik_bitis")

    def __init__(self, dosya, metin):
        self.dosya = dosya
        m = KUNYE_LINE_RE.search(metin)
        self.kunye_ham = m.group(1).strip() if m else None
        self.esas, self.karar = ko.kunye_normalize(self.kunye_ham or "")
        self.daire = ko.daire_key(self.kunye_ham or "")
        # DÜZELTME (v0.5.5 düzeltme turu — GEÇERSİZ-KILINDI artık TÜKETİLİR):
        # `oa_hafiza.py --damga-degistir` bu satırı eski bölüme SURGICAL olarak
        # ekler (bkz. `_eski_bolumleri_gecersiz_kil`); eskiden hiçbir tüketici
        # yoktu — hükümsüz kılınan bölüm tam yetkili bir aday olarak yaşamaya
        # devam edip sahte ÇELİŞEN DAMGA / DAMGA-elle-değiştirilmiş engeli
        # üretiyordu. Bu bayrak `muhakeme_kayitlarini_yukle`'de aday havuzundan
        # DÜŞÜRMEK için kullanılır (sessizce değil — rapora sayaç basılır).
        self.gecersiz = bool(GECERSIZ_KILINDI_RE.search(metin))

        m = KAYNAK_IZI_LINE_RE.search(metin)
        self.kaynak_izi = m.group(1).strip() if m else None

        m = DAMGA_LINE_RE.search(metin)
        self.damga_ham = m.group(1).strip() if m else None
        self.damga = self.damga_ham.upper() if self.damga_ham else None

        m = KAYNAK_URL_LINE_RE.search(metin)
        self.kaynak_url = m.group(1).strip() if m else None

        # v0.5.8 [G5] — aşılmışlık alanları (üçü de opsiyonel; herhangi biri
        # doluysa karar AŞILMIŞ sayılır).
        m = ASAN_KAYNAK_LINE_RE.search(metin)
        self.asan_kaynak = m.group(1).strip() if m else None
        m = ASILMA_TARIHI_LINE_RE.search(metin)
        self.asilma_tarihi = m.group(1).strip() if m else None
        m = GECERLILIK_BITIS_LINE_RE.search(metin)
        self.gecerlilik_bitis = m.group(1).strip() if m else None

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
    listesine çevirir (dosya-sırasıyla, sabit sıralı).

    P0-3 (v0.5.5): bir dosya artık BİRDEN ÇOK karar barındırabilir (P0-2'nin
    tek-komut `teyit --damga` ritüelinin bölüm-APPEND biçimi). Ayrıştırma
    `kunye_ortak.bolumlere_ayir` ile yapılır (ayraç: satır-başı `**KUNYE:**`);
    tek bölümlü (eski) dosyalarda `dosya` etiketi DEĞİŞMEDEN kalır (geriye
    uyum — mevcut testler/raporlar bit-özdeş).

    DÜZELTME (v0.5.5 düzeltme turu): `**GEÇERSİZ-KILINDI:**` işaretli bölümler
    aday havuzuna GİRMEZ (döner: (kayitlar, gecersiz_sayisi) — sessiz atlama
    yasağı gereği çağıran taraf bu sayıyı rapora basar)."""
    kayitlar = []
    gecersiz_sayisi = 0
    if not muhakeme_dizin or not os.path.isdir(muhakeme_dizin):
        return kayitlar, gecersiz_sayisi
    desen = os.path.join(muhakeme_dizin, "*ictihat-muhakeme*.md")
    for yol in sorted(glob.glob(desen)):
        if not os.path.isfile(yol):
            continue
        try:
            with open(yol, encoding="utf-8", errors="replace") as f:
                metin = f.read()
        except OSError:
            continue
        bolumler = ko.bolumlere_ayir(metin)
        for i, bolum in enumerate(bolumler):
            etiket = yol if len(bolumler) == 1 else f"{yol}#{i + 1}"
            kayit = MuhakemeKaydi(etiket, bolum)
            if kayit.gecersiz:
                gecersiz_sayisi += 1
                continue
            kayitlar.append(kayit)
    return kayitlar, gecersiz_sayisi


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


def kutuk_son_damga_engeli(kayit, kutuk_yolu):
    """P0-2 DÜZELTME (d) — DAMGA çapraz kontrolü: aynı künye için kütükteki
    (append-only) SON teyit satırının `DAMGA=` tokenı ile muhakeme bölümündeki
    DAMGA değeri FARKLIYSA ENGEL üretir — salt-ALEYHE'nin muhakeme dosyası elle
    düzenlenerek LEHE'ye çevrilme yolu kapanır (bölüm-append tek dosyada
    olduğundan bu düzenleme tek satırlık olabilir; kütük ise append-only'dir).

    Kütük dosyası yoksa VEYA bu künye için kütükte hiç `DAMGA=` etiketli satır
    yoksa denetim SESSİZCE ATLANIR (fail-OPEN) — kütüksüz/elle kurulmuş eski
    kayıtları BOZMAZ (geriye uyum); kütük izi VARSA ve ÇELİŞİYORSA fail-CLOSED.

    Kütük ayrıştırma mantığı `kunye_ortak.kutukten_son_damga`'da PAYLAŞIMLIDIR
    (P0-2 DÜZELTME d) — `oa_hafiza.py` aynı fonksiyonu YAZMA-ÖNCESİ çapraz
    kontrol için çağırır (tek-yazar kuralı)."""
    son_damga = ko.kutukten_son_damga(kutuk_yolu, kayit.esas, kayit.karar, kayit.daire)
    if son_damga is not None and kayit.damga is not None and son_damga != kayit.damga:
        return [f"DAMGA elle değiştirilmiş — kütükteki (append-only) son teyit DAMGA'sı "
                f"('{son_damga}') ile muhakeme kaydındaki DAMGA ('{kayit.damga}') "
                "uyuşmuyor; damga değişimi ancak yeni bir `teyit --damga` satırıyla olur."]
    return []


def kutuk_dayanagi_denetle(kayit, kutuk_yolu):
    """DÜZELTME (v0.5.5 şerh turu — Ş2, BLOKER, HAYALET MUHAKEME t3): bir
    muhakeme kaydının KAYNAK-IZI dosyası diskte var olsa bile
    (`kaynak_izi_denetle` yalnız BUNU denetler), bu dosyayı GERÇEKTEN üreten
    bir `teyit` çağrısının künye teyit kütüğünde hiçbir izi yoksa kayıt
    HAYALETTİR — künye/döküm ile hiçbir fiilî MCP çağrısı arasında bağ
    kanıtlanmamıştır (`--arac` enjeksiyonuyla `oa_hafiza.py`'ye YAZDIRILAN bir
    bölüm tam da bu izi bırakmaz).

    Denetim yalnız kütük FİİLEN KULLANILIYORSA (`kutuk_gercek_veri_var_mi` —
    en az bir gerçek 7-hücreli satır) etkindir; kütük hiç yoksa/hiç
    kullanılmamışsa (elle kurulmuş test iskeleti / 'derin yol' — doğrudan
    dosya yazımıyla muhakeme kaydı oluşturma, P1-11 playbook'u) mevcut SESSİZ
    ATLAMA (geriye uyum, `kutuk_son_damga_engeli` ile SİMETRİK) KORUNUR — bu
    invaryant `test_kutuk_yoksa_denetim_sessizce_atlanir_geriye_uyum` ile
    kilitlidir, bit düzeyinde bozulmaz (bu atlamanın GÖRÜNÜRLÜĞÜ artık
    `main()`/`rapor_yaz` seviyesinde ayrı bir [BİLGİ] satırıyla sağlanır —
    bkz. `kutuk_gercek_veri_var_mi` çağrısının main()'deki kopyası).

    DÜZELTME (v0.5.5 düzeltme turu — Ş2/t3-B, İKİNCİ KATMAN): 'esas/karar
    kütükte HERHANGİ bir satırda geçiyor mu' (`kutukte_esas_karar_satiri_
    var_mi`) tek başına YETERSİZDİR — damgasız/tam-metinsiz ucuz bir ARAMA
    teyidi bu denetimi bedavaya geçiyordu (t3-B). Satır fiilen VARSA ama
    bölümün DAMGA'sıyla eşleşen VE aynı KAYNAK-IZI dosyasını gösteren bir
    satır YOKSA (`kutukte_damgali_dayanak_satiri_var_mi`), kayıt yine HAYALET
    sayılır — farklı, daha isabetli bir gerekçeyle."""
    if not ko.kutuk_gercek_veri_var_mi(kutuk_yolu):
        return []
    if not (kayit.esas or kayit.karar):
        return []
    if not ko.kutukte_esas_karar_satiri_var_mi(kutuk_yolu, kayit.esas, kayit.karar, kayit.daire):
        return [
            f"Bu muhakeme kaydının künyesi (E. {kayit.esas or '—'} / K. {kayit.karar or '—'}) "
            "künye teyit kütüğünde HİÇ BİR SATIRDA geçmiyor — kütük bu kökte fiilen "
            "kullanılıyor (başka teyit satırları var) ama BU kayda karşılık gelen bir "
            "`teyit` çağrısı YOK (HAYALET MUHAKEME — fail-closed, anayasa m.6 ihtiyatı)"
        ]
    if kayit.damga and not ko.kutukte_damgali_dayanak_satiri_var_mi(
            kutuk_yolu, kayit.esas, kayit.karar, kayit.damga,
            kaynak_izi=kayit.kaynak_izi, daire=kayit.daire):
        return [
            f"Bu muhakeme kaydının künyesi (E. {kayit.esas or '—'} / K. {kayit.karar or '—'}) "
            "kütükte GEÇİYOR ama bu bölümün DAMGA'sıyla "
            f"('{kayit.damga_ham}') eşleşen VE aynı KAYNAK-IZI dosyasını ('{kayit.kaynak_izi}') "
            "gösteren bir `teyit` satırı YOK — damgasız/tam-metinsiz bir ARAMA satırı (ya da "
            "başka bir künyeye/dosyaya ait bir döküm) bir muhakeme bölümünü MEŞRULAŞTIRMAZ "
            "(HAYALET MUHAKEME — fail-closed, anayasa m.6 ihtiyatı)"
        ]
    return []


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


ORTUSME_MIN_NOKTA = 3  # M2 (Paket D, v0.5.5) — advisory eşik, BLOKLAMAZ


def ortusme_zenginligi_uyarisi(kayit):
    """M2 (Paket D, v0.5.5) — KIYAS ŞEMASI: DAVAYA-BAĞ (ÖRTÜŞME) metni en az
    ORTUSME_MIN_NOKTA somut ortak-unsur noktası içeriyor mu? Yalnız ADVISORY
    (G2'nin 'alan dolu mu' semantiği DEĞİŞMEZ — bkz. `alan_butunlugu_denetle`,
    DOKUNULMAZ) — tek cümlelik yüzeysel bir örtüşme beyanını GÖRÜNÜR kılar,
    bloklamaz (pahalı muhakemeyi ucuz bir kapıyla zorunlu kılmak v0.3.20/
    v0.5.3'teki 61→0 çöküşünü tekrarlardı). Nokta sayımı madde-imli satırlar
    (-, *, 1.) VEYA cümle sayısı (hangisi büyükse) üzerinden yapılır — bu bir
    doğruluk/isabet denetimi DEĞİLDİR, yalnız yapısal zenginlik göstergesidir."""
    metin = (kayit.davaya_bag or "").strip()
    if not metin:
        return None
    madde_sayisi = len(re.findall(r"(?m)^\s*(?:[-*•]|\d+[.)])\s+\S", metin))
    cumle_sayisi = len([s for s in re.split(r"(?<=[.!?])\s+", metin) if s.strip()])
    nokta = max(madde_sayisi, cumle_sayisi)
    if nokta < ORTUSME_MIN_NOKTA:
        return (f"DAVAYA-BAĞ (ÖRTÜŞME) yalnız ~{nokta} somut nokta içeriyor gibi görünüyor "
                f"(önerilen ≥{ORTUSME_MIN_NOKTA}) — yüzeysel/tek-cümlelik örtüşme beyanı "
                "hukuken zayıf sayılabilir (bloklamaz; avukat gözü karar verir).")
    return None


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


def _atif_denetle(atif, kayitlar, kok, dokum_dizin, kutuk_yolu=None):
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

    # v0.5.5 SON SINAV DÜZELTMESİ (m.6 kaçağı): çelişki, damganın "girebilir"
    # (LEHE / ALEYHE-AYIRT) ve "giremez" (ALEYHE / NOTR) SINIFLARI ARASINDAYSA
    # yalnız UYARI yetmez — script aşağıdaki döngüde temiz olan (lehe) adayı
    # seçip [OK] verir ve ALEYHE ikizi sessizce gölgelenir; salt-ALEYHE bir
    # karar dilekçeye lehe kılığında girer. Bu, m.6'nın doğrudan ihlalidir →
    # ENGEL. Çözüm yolu kapalı değil: yanlış kayıt --damga-degistir ile
    # GEÇERSİZ-KILINDI damgası alınca aday havuzundan düşer ve engel kalkar.
    # (Aynı sınıf içi çelişki — ör. LEHE ↔ ALEYHE-AYIRT — engel DEĞİL, uyarı
    # kalır: ikisi de dış çıktıya girebilen damgalardır.)
    _GIREMEZ = {"ALEYHE", "NOTR"}
    _GIREBILIR = {"LEHE", "ALEYHE-AYIRT"}
    _damgalar = {k.damga for k in adaylar if k.damga}
    if celisen_uyari and (_damgalar & _GIREMEZ) and (_damgalar & _GIREBILIR):
        return ("BLOK",
                ["ÇELİŞEN DAMGA — aynı karara ait kayıtlardan biri dış çıktıya "
                 "GİREMEZ sınıfında (" + ", ".join(sorted(_damgalar & _GIREMEZ)) +
                 "), diğeri girebilir sınıfında (" +
                 ", ".join(sorted(_damgalar & _GIREBILIR)) + "). Lehe olan "
                 "sessizce seçilemez (anayasa m.6). Çelişkiyi çözün: isabetsiz "
                 "kaydı `oa_hafiza.py teyit --damga-degistir <gerekçe>` ile "
                 "GEÇERSİZ-KILINDI hâline getirin."],
                [celisen_uyari], adaylar[0])

    # Birden çok aday varsa: TAM temiz (engelsiz) olan varsa onu kullan;
    # yoksa raporlama için İLK adayı esas al (deterministik).
    en_iyi = None
    en_iyi_engeller, en_iyi_uyarilar = None, None
    for kayit in adaylar:
        engeller = list(alan_butunlugu_denetle(kayit))
        engeller += kaynak_izi_denetle(kayit, kok, dokum_dizin)
        damga_engel, damga_uyari = damga_denetle(kayit)
        engeller += damga_engel
        engeller += kutuk_son_damga_engeli(kayit, kutuk_yolu)
        engeller += kutuk_dayanagi_denetle(kayit, kutuk_yolu)
        ortusme_uyari = ortusme_zenginligi_uyarisi(kayit)
        if not engeller:
            uyarilar = list(damga_uyari)
            if celisen_uyari:
                uyarilar.append(celisen_uyari)
            if ortusme_uyari:
                uyarilar.append(ortusme_uyari)
            return ("OK", [], uyarilar, kayit)
        if en_iyi is None:
            en_iyi_uyarilar_ilk = list(damga_uyari)
            if ortusme_uyari:
                en_iyi_uyarilar_ilk.append(ortusme_uyari)
            en_iyi, en_iyi_engeller, en_iyi_uyarilar = kayit, engeller, en_iyi_uyarilar_ilk

    en_iyi_uyarilar = list(en_iyi_uyarilar or [])
    if celisen_uyari:
        en_iyi_uyarilar.append(celisen_uyari)
    return ("BLOK", en_iyi_engeller, en_iyi_uyarilar, en_iyi)


def rapor_yaz(taslak_yolu, atiflar, sonuclar, muhakeme_dizin, dokum_dizin, kutuk_bos_mu,
              tip=None, gecersiz_sayisi=0, kutuk_kullanimda_mi=True):
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
    # DÜZELTME (v0.5.5 düzeltme turu — Ş2, ÖNEMLİ, SESSİZ FAIL-OPEN
    # GÖRÜNÜRLÜĞÜ): `kutuk_dayanagi_denetle` (HAYALET MUHAKEME kütük dayanağı
    # denetimi) kütük bu kökte fiilen kullanılmıyorsa (`kutuk_gercek_veri_
    # var_mi` False — taze kök / kütüksüz 'derin yol') SESSİZCE atlanır
    # (geriye uyum, bit düzeyinde korunur). Ama bu atlama artık GÖRÜNMEZ
    # DEĞİL — 'sessiz atlama yasağı' invaryantı gereği avukat, bu koşuda en
    # kritik hayalet-muhakeme denetiminin HİÇ ÇALIŞMADIĞINI burada görür
    # (bloklamaz — yalnız görünürlük).
    if not kutuk_kullanimda_mi:
        print("[BİLGİ] Künye teyit kütüğü bu kökte fiilen kullanılmıyor — HAYALET "
              "MUHAKEME denetimi (kütük dayanağı) bu koşuda ÇALIŞMADI; muhakeme "
              "kayıtlarının teyit dayanağı MEKANİK olarak doğrulanmamıştır.")
    if gecersiz_sayisi:
        print(f"[BİLGİ] {gecersiz_sayisi} hükümsüz kılınmış (**GEÇERSİZ-KILINDI:**) "
              "muhakeme kaydı aday havuzundan ATLANDI (gerekçe: `--damga-degistir` ile "
              "bilinçli DAMGA değişiminde eski bölüm hükümsüz kılınmıştır — dosyada "
              "SİLİNMEDEN durur ama artık bir atfı 'muhakeme edilmiş' saymaz).")

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


# ── [G4] KAYNAK-URL TUTARLILIĞI (v0.5.7 — Denizli 754 saha bulgusu) ─────────
# Kural zinciri v0.5.5.3'ten beri var: bağlantı YALNIZ teyit anında yakalanır
# (`--kaynak-url`), yazım aşamasında model URL HATIRLAYAMAZ ama UYDURABİLİR;
# bu yüzden "kayıt yoksa parantez HİÇ AÇILMAZ". Bu kapı zincirin dilekçe
# ucunu mekanikleştirir:
#   (a) UYDURMA-LINK → BLOK: künye satırının ±1 satır penceresinde görünen
#       bir http(s) bağlantısı HİÇBİR muhakeme kaydının KAYNAK-URL'iyle
#       örtüşmüyorsa teslim ENGELİDİR — sahte bağlantı "teyit edildi" der,
#       çıplak künyeden DAHA KÖTÜDÜR.
#   (b) KAYITLI-LINK-KULLANILMAMIŞ → UYARI (bloklamaz): teyit anında
#       kaydedilmiş bağlantı dilekçeye işlenmemişse görünür kılınır
#       (kullanıcı kuralı: karardan bahsedilince linki de dilekçede olmalı).
def kaynak_url_denetimi(metin, atiflar, sonuclar, kayitlar):
    """Döndürür: (bloklar, uyarilar) — her ikisi de [str]."""
    bloklar, uyarilar = [], []
    kayitli_urller = [k.kaynak_url for k in kayitlar if getattr(k, "kaynak_url", None)]

    def _kayitli_mi(url):
        u = url.rstrip(".,;")
        for ku in kayitli_urller:
            if u == ku or u.startswith(ku) or ku.startswith(u):
                return True
        return False

    satirlar = metin.splitlines()
    atif_satirlari = {a.get("satir_no") for a in atiflar if a.get("satir_no")}
    for sno in sorted(atif_satirlari):
        pencere = "\n".join(satirlar[max(0, sno - 2): sno + 1])
        for url in HTTP_URL_RE.findall(pencere):
            if not _kayitli_mi(url):
                bloklar.append(
                    f"(satır ~{sno}) künye yanındaki bağlantı HİÇBİR muhakeme "
                    f"kaydının KAYNAK-URL'inde yok: {url[:90]} — UYDURMA BAĞLANTI "
                    "riski (sahte bağlantı 'teyit edildi' der; çıplak künyeden "
                    "DAHA KÖTÜDÜR). Ya teyit anında `--kaynak-url` ile kaydedin "
                    "ya da bağlantıyı dilekçeden çıkarın.")

    for atif, (durum, _e, _u, kayit) in zip(atiflar, sonuclar):
        if durum != "OK" or kayit is None:
            continue
        ku = getattr(kayit, "kaynak_url", None)
        if ku and ku not in metin:
            uyarilar.append(
                f"E. {atif['esas'] or '—'} / K. {atif['karar'] or '—'}: teyit "
                f"anında kaydedilen bağlantı dilekçeye İŞLENMEMİŞ ({ku[:90]}) — "
                "5-adım/1 kuralı: künyenin ardından parantez içinde verilmeli.")
    return bloklar, uyarilar


def asilmis_ictihat_denetimi(atiflar, kayitlar):
    """v0.5.8 [G5] AŞILMIŞ-İÇTİHAT kapısı (semantica superseded deseni).

    Kural (Can kararı 2026-08-12): DAMGA=LEHE ∧ aşılmışlık alanı dolu ∧ künye
    dilekçede atıf olarak GEÇİYORSA → TESLİM ENGELİ (aşılmış içtihat lehte
    dayanak olamaz — İBK/kanun değişikliği/daire kayması onu öldürmüştür).
    LEHE ama dilekçede geçmiyorsa → UYARI (kütük hijyeni: damga güncellenmeli).
    ALEYHE/ALEYHE-AYIRT/NOTR + aşılmış → UYARI (bilgi — aşılmış ALEYHE karar
    cephanelikte İŞE YARAR: karşı taraf ileri sürerse aşan kaynak koz olur).
    Alanlar boşsa kayıt bu kapıya hiç girmez (geriye dönük uyum, fail-open)."""
    bloklar, uyarilar = [], []
    for k in kayitlar:
        asilmis = k.asan_kaynak or k.asilma_tarihi or k.gecerlilik_bitis
        if not asilmis:
            continue
        asan = k.asan_kaynak or "aşan kaynak belirtilmemiş"
        tarih = k.asilma_tarihi or k.gecerlilik_bitis or "?"
        atifta_var = any(k.eslesir(a["esas"], a["karar"], a.get("daire_key"))
                         for a in atiflar)
        if k.damga == "LEHE":
            if atifta_var:
                bloklar.append(
                    f"{k.kunye_ham or k.dosya}: DAMGA=LEHE ama içtihat AŞILMIŞ "
                    f"(aşan: {asan}; tarih: {tarih}) — aşılmış karar lehte "
                    f"dayanak olarak dilekçede KALAMAZ.")
            else:
                uyarilar.append(
                    f"{k.kunye_ham or k.dosya}: kütükte LEHE damgalı ama AŞILMIŞ "
                    f"(aşan: {asan}) — dilekçede kullanılmamış; damga gözden "
                    f"geçirilmeli (--damga-degistir).")
        else:
            uyarilar.append(
                f"{k.kunye_ham or k.dosya}: AŞILMIŞ içtihat (damga: "
                f"{k.damga or 'yok'}; aşan: {asan}) — bilgi: karşı tarafça "
                f"ileri sürülürse aşan kaynak cephanelik kozudur.")
    return bloklar, uyarilar


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
    ap.add_argument("--kutuk-yol", default=None,
                     help="Künye teyit kütüğü — P0-2 DAMGA çapraz kontrolü için "
                          f"(varsayılan: --kok yoksa {VARSAYILAN_KUTUK}, "
                          f"varsa <KOK>/{VARSAYILAN_KUTUK}); kütük yoksa/künye kütükte "
                          "yoksa denetim SESSİZCE atlanır (fail-open — geriye uyum)")
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
    kutuk_yolu = args.kutuk_yol if args.kutuk_yol is not None else (
        os.path.join(args.kok, VARSAYILAN_KUTUK) if args.kok else VARSAYILAN_KUTUK)

    with open(args.taslak, encoding="utf-8", errors="replace") as f:
        metin = f.read()

    atiflar = taslaktaki_atiflari_bul(metin)
    kayitlar, gecersiz_sayisi = muhakeme_kayitlarini_yukle(muhakeme_dizin)

    sonuclar = [_atif_denetle(a, kayitlar, kok, dokum_dizin, kutuk_yolu) for a in atiflar]

    engel_var = rapor_yaz(args.taslak, atiflar, sonuclar, muhakeme_dizin, dokum_dizin,
                           kutuk_bos_mu=not kayitlar and not gecersiz_sayisi, tip=args.tip,
                           gecersiz_sayisi=gecersiz_sayisi,
                           kutuk_kullanimda_mi=ko.kutuk_gercek_veri_var_mi(kutuk_yolu))

    url_bloklar, url_uyarilar = kaynak_url_denetimi(metin, atiflar, sonuclar, kayitlar)
    if url_bloklar or url_uyarilar:
        print("\n" + "-" * 72)
        print("[G4] KAYNAK-URL TUTARLILIĞI (v0.5.7 — bağlantı, teyit anının izidir)")
        print("-" * 72)
        for b in url_bloklar:
            print(f"  ✗ {b}")
        for u in url_uyarilar:
            print(f"  ⚠ {u}")
        if url_bloklar:
            engel_var = True
            print("SONUÇ-EK: TESLİM ENGELİ — kütükte izi olmayan bağlantı dilekçede "
                  "kalamaz (uydurma-bağlantı yasağı).")

    g5_bloklar, g5_uyarilar = asilmis_ictihat_denetimi(atiflar, kayitlar)
    if g5_bloklar or g5_uyarilar:
        print("\n" + "-" * 72)
        print("[G5] AŞILMIŞ-İÇTİHAT (v0.5.8 — aşılmış karar lehte dayanak olamaz)")
        print("-" * 72)
        for b in g5_bloklar:
            print(f"  ✗ {b}")
        for u in g5_uyarilar:
            print(f"  ⚠ {u}")
        if g5_bloklar:
            engel_var = True
            print("SONUÇ-EK: TESLİM ENGELİ — İBK/kanun değişikliği/daire "
                  "kaymasıyla aşılmış içtihat LEHE dayanak olarak kullanılamaz.")

    sys.exit(1 if engel_var else 0)


if __name__ == "__main__":
    main()

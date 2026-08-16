#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa-gizlilik — gizlilik_tara.py (v2)
Dış araca gidecek içerikte hassas veri / UYAP-eimza deseni DETERMİNİSTİK tarama.

Felsefe: Privacy Layer 0 garantörü. Karar içeriğe bağlıdır, modelin iradesine değil.
Güçlü desen = DENY, zayıf desen = ASK, temiz = ALLOW. UYAP login / e-imza / PIN ve
finansal kimlik desenleri her mod'da MUTLAK DENY (anayasa KATI KURAL).

v2 değişiklikleri (2026-07):
  - Windows/PowerShell UTF-8 çıktı güvencesi (cp1254 UnicodeEncodeError'ı önler).
  - FAIL-CLOSED: beklenmeyen her hata → exit 2 (DENY); "gönderme"yi asla "sorulabilir"e
    indirmez. Eski kod DENY'i basarken çöküp exit 1 dönüyordu (güvenlik açığı).
  - balanced modu artık gerçekten çalışıyor (eski `and` kısa-devre bug'ı: KVKK m.6
    özel nitelikli veri sessizce ALLOW alıyordu — düzeltildi).
  - TCKN checksum (algoritmik doğrulama) + kart no Luhn: yanlış pozitif azalır,
    gerçek kimlik verisinde YANLIŞ NEGATİF ÜRETMEDEN (checksum tutmayan dizi yine
    'olası' düzeyinde işaretlenir — fail-closed).
  - Esas/Karar no deseni 'YYYY/N Esas' biçimini de yakalar.
  - --maskele: hassas alanları etiketle değiştirilmiş kopya üretir (yerel işleme).
  - tara()/maskele() import edilebilir kütüphane API'si (oa-usta ders damıtma anonimleştirmesi
    bunları yeniden kullanır).

v3 değişiklikleri (2026-07):
  - balanced politika deliği kapatıldı: zayıf desen (esas/karar no) artık sessizce
    ALLOW almıyor. balanced'da zayıf desen "yok say" yerine "raporla-ama-engelleme":
    çıktıya [BİLGİ] satırı basılır ama exit 0 KALIR (anayasa §10 "esas no taranır"
    ile uyum). strict davranışı AYNEN korunur (zayıf → ASK). tara() geriye-uyumlu:
    dönüş yine (deny, ask); opsiyonel `bilgi` listesiyle BİLGİ kanalı yüzeye çıkar.

Kullanım:
    python gizlilik_tara.py <dosya> [--mod strict|balanced] [--maskele cikti.txt]
Çıkış kodu: 2=DENY, 1=ASK, 0=ALLOW (otomasyonda kullanılabilir). Hata/okunamama = 2.
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
import json
import os
import re
import sys

# --- MUTLAK DENY desenleri (her mod) ---
# (Kart no ve IBAN ayrıca algoritmik doğrulanır; aşağıya bakınız.)
MUTLAK_DENY = [
    ("UYAP login / oturum akışı", re.compile(r"\buyap\b.{0,40}(giri[sş]|login|oturum|parola|[sş]ifre|kullan[ıi]c[ıi])", re.I)),
    ("e-imza / e-mühür / mobil imza", re.compile(r"\b(e[-\s]?imza|e[-\s]?m[üu]h[üu]r|mobil\s?imza|elektronik\s?imza)\b", re.I)),
    ("PIN / parola", re.compile(r"\b(pin\s?kodu?|parola|[sş]ifre|password|passwd)\b\s*[:=]?\s*\S+", re.I)),
    ("API anahtarı / token", re.compile(r"\b(api[_\s-]?key|token|secret|bearer)\b\s*[:=]?\s*[A-Za-z0-9_\-]{8,}", re.I)),
    ("IBAN", re.compile(r"\bTR\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b")),
]

# Algoritmik doğrulanan güçlü kimlik desenleri (checksum tutarsa güçlü, tutmazsa 'olası')
KART = re.compile(r"\b(?:\d[ -]?){15,16}\b")
TCKN = re.compile(r"(?<!\d)[1-9]\d{10}(?!\d)")

# ── E2 BAĞLAM İSTİSNALARI (v0.5.8.5, saha karnesi — yanlış pozitif onarımı) ──
# (a) SAĞLIK: "rapor" TEK BAŞINA sağlık verisi DEĞİLDİR (hukuk metninin en sık
#     kelimelerinden biri: bilirkişi raporu / ek rapor / kök rapor). Sağlık
#     çekirdek deseni "rapor"suz tanımlanır; "rapor" YALNIZ sağlık-bağlam
#     komşuluğunda (± _RAPOR_PENCERE karakter içinde hastane/teşhis/tedavi
#     sınıfı bir kelime ya da doktor/hekim/heyet) sağlık sinyali sayılır.
#     Gerçek sağlık verisinde YANLIŞ NEGATİF ÜRETMEZ: çekirdek kelimelerin
#     herhangi biri metinde geçiyorsa desen zaten bağımsız tetiklenir.
SAGLIK_CEKIRDEK = re.compile(
    r"\b(te[sş]his|tan[ıi]\b|hastal[ıi][kğ]|hastane|klinik|poliklinik|psikiyatr|psikoloj|"
    r"engel(li|\s?oran)|sa[gğ]l[ıi]k|t[ıi]bb[iî]|tedavi|ameliyat|operasyon|kanser|t[üu]m[öo]r|hiv|aids|"
    r"hepatit|ila[çc]\b|re[çc]ete|tahlil|biyopsi|gebe|hamile|ruh\s?sa[gğ]l[ıi]|ba[gğ][ıi]ml[ıi]l[ıi]k)\b", re.I)
RAPOR = re.compile(r"\brapor\w*", re.I)
# "rapor"u sağlıklaştıran EK komşu kelimeler (çekirdekte olmayanlar):
RAPOR_SAGLIK_KOMSU = re.compile(r"\b(doktor|hekim|heyet|sa[gğ]l[ıi]k\s?kurulu)\b", re.I)
_RAPOR_PENCERE = 60


class _BaglamliSaglikDeseni:
    """re.Pattern gibi .search sunar (HASSAS listesi API'si değişmez):
    çekirdek kelime → doğrudan eşleşme; 'rapor' → yalnız pencere içinde
    sağlık-bağlam komşusu varsa eşleşme (yoksa None — tetiklenmez)."""

    def search(self, metin):
        m = SAGLIK_CEKIRDEK.search(metin)
        if m:
            return m
        for r in RAPOR.finditer(metin):
            pencere = metin[max(0, r.start() - _RAPOR_PENCERE): r.end() + _RAPOR_PENCERE]
            if SAGLIK_CEKIRDEK.search(pencere) or RAPOR_SAGLIK_KOMSU.search(pencere):
                return r
        return None


# (c) TELEFON: 05XX/+90 biçimli kişisel telefon YAKALANIR; ama 10 haneli
#     belge/doküman-id dizileri (documentId / evrak no / belge no / doğrulama
#     kodu / barkod komşuluğu) telefon uyarısından AYRIŞIR — UYAP evrak
#     kimlikleri telefonla aynı hane genişliğindedir, etiket komşuluğu ayırır.
TELEFON = re.compile(
    r"(?<!\d)(?:\+?\s?90[\s.\-]?)?(?:\(0?\d{3}\)|0\d{3}|\d{3})"
    r"[\s.\-]?\d{3}[\s.\-]?\d{2}[\s.\-]?\d{2}(?!\d)")
DOKUMAN_ID_KOMSU = re.compile(
    r"(documentid|dok[uü]man\s*(?:no|id)|evrak\s*(?:no|numaras[ıi])|"
    r"belge\s*(?:no|numaras[ıi])|do[gğ]rulama\s*kodu|barkod)", re.I)
_DOKUMAN_PENCERE = 40


class _DokumanIdAyrikTelefonDeseni:
    """re.Pattern gibi .search sunar: telefon-biçimli her dizi, ± pencere
    içinde belge/doküman-id etiketi TAŞIMIYORSA eşleşme sayılır (fail-closed
    yön: etiketi olmayan her telefon-biçimli dizi yine yakalanır)."""

    def search(self, metin):
        for m in TELEFON.finditer(metin):
            cevre = metin[max(0, m.start() - _DOKUMAN_PENCERE): m.end() + _DOKUMAN_PENCERE]
            if not DOKUMAN_ID_KOMSU.search(cevre):
                return m
        return None


def _mersis_gibi(ham):
    """(b) MERSİS AYRIMI: Mersis no 16 hanedir ve 0 ile başlar; kart IIN'i
    (ilk hane) hiçbir ödeme ağında 0 DEĞİLDİR. 16 hane + '0' başlangıcı →
    kart değil işletme kaydı biçimi (Mersis, Luhn'dan bağımsızdır — tesadüfen
    Luhn tutturan bir Mersis no kart DENY'i üretmesin)."""
    hane = "".join(c for c in ham if c.isdigit())
    return len(hane) == 16 and hane.startswith("0")


# --- Hassas veri desenleri (mod'a göre deny/ask) ---
HASSAS = [
    ("Esas/Karar no (taraf bağlamı olabilir)", "zayif",
     re.compile(r"\b(?:19|20)\d{2}\s?/\s?\d{1,6}(?:\s*(?:E|K|Esas|Karar)\.?)?\b", re.I)),
    ("Sağlık verisi (KVKK m.6 özel nitelikli)", "guclu",
     _BaglamliSaglikDeseni()),
    ("Telefon numarası (kişisel veri — belge-id bağlamı hariç)", "zayif",
     _DokumanIdAyrikTelefonDeseni()),
    ("Ceza/sabıka verisi (KVKK m.6)", "guclu",
     re.compile(r"\b(sab[ıi]ka|adli\s?sicil|mahk[uû]miyet|ceza\s?kayd|h[üu]k[üu]ml[üu]|tutuklu|g[öo]zalt[ıi]|"
                r"uyu[şs]turucu|denetimli\s?serbest|infaz\s?kurumu|su[çc]\s?kayd)\b", re.I)),
    ("Biyometrik/din/köken (KVKK m.6)", "guclu",
     re.compile(r"\b(biyometri|parmak\s?izi|din[iî]\b|etnik|sendika)\b", re.I)),
]

# Maskeleme için desen → etiket (algoritmik olanlar ayrıca ele alınır)
_MASKE = [
    (MUTLAK_DENY[4][1], "[IBAN-MASKELİ]"),
    (TCKN, "[TCKN-MASKELİ]"),
    (KART, "[KART/HESAP-MASKELİ]"),
]


def tckn_gecerli(s):
    """Standart T.C. Kimlik No algoritması (11 hane, checksum)."""
    d = [int(c) for c in s if c.isdigit()]
    if len(d) != 11 or d[0] == 0:
        return False
    if ((sum(d[0:9:2]) * 7) - sum(d[1:8:2])) % 10 != d[9]:
        return False
    return sum(d[0:10]) % 10 == d[10]


def luhn_gecerli(s):
    """Kart no Luhn (mod-10) doğrulaması."""
    d = [int(c) for c in s if c.isdigit()]
    if not (13 <= len(d) <= 19):
        return False
    toplam, ikinci = 0, False
    for x in reversed(d):
        if ikinci:
            x *= 2
            if x > 9:
                x -= 9
        toplam += x
        ikinci = not ikinci
    return toplam % 10 == 0


def tara(metin, mod, bilgi=None):
    """(deny, ask) döndürür; her biri (şiddet, ad) çiftlerinden liste.

    fail-closed tasarım: algoritmik doğrulama TUTMAYAN kimlik dizileri de düşürülmez,
    'olası' düzeyde işaretlenir — böylece OCR ile bozulmuş gerçek TCKN/kart kaçmaz.

    Geriye-uyumlu imza: dönüş DAİMA (deny, ask) 2'lisidir; mevcut çağıranlar/testler
    `deny, ask = tara(...)` kalıbını sürdürür. İsteğe bağlı `bilgi` bir liste olarak
    verilirse, balanced modda ENGELLEMEYEN ama raporlanan zayıf desenler (esas/karar
    no) oraya (şiddet, ad) olarak eklenir; exit kodunu ETKİLEMEZ (bkz. _yaz_ve_cik).
    """
    deny, ask = [], []

    for ad, pat in MUTLAK_DENY:
        if pat.search(metin):
            deny.append(("MUTLAK", ad))

    # TCKN: checksum tutan → MUTLAK; tutmayan 11 hane → 'olası' (fail-closed)
    tckn_hit = TCKN.findall(metin)
    if any(tckn_gecerli(x) for x in tckn_hit):
        deny.append(("MUTLAK", "TC Kimlik No (checksum geçerli)"))
    elif tckn_hit:
        ask.append(("guclu", "Olası 11 haneli kimlik/hesap (checksum tutmadı — teyit)"))

    # Kart no: Luhn tutan → MUTLAK; tutmayan uzun dizi → 'olası'.
    # E2(b) v0.5.8.5: Mersis biçimli diziler (16 hane + 0 başlangıcı — kart
    # IIN'i 0 ile başlamaz) kart uyarısından AYRIŞIR; Luhn tesadüfen tutsa
    # bile kart sayılmaz. Raporsuz da yutulmaz: bilgi kanalına düşer.
    kart_hit = [x for x in KART.findall(metin) if not _mersis_gibi(x)]
    mersis_hit = [x for x in KART.findall(metin) if _mersis_gibi(x)]
    if mersis_hit and bilgi is not None:
        bilgi.append(("zayif", "Mersis biçimli 16 haneli dizi (0 ile başlar — kart sayılmadı)"))
    if any(luhn_gecerli(x) for x in kart_hit):
        deny.append(("MUTLAK", "Kart numarası (Luhn geçerli)"))
    elif kart_hit:
        ask.append(("zayif", "Uzun sayı dizisi (olası hesap/kart — teyit)"))

    for ad, siddet, pat in HASSAS:
        if pat.search(metin):
            if mod == "strict":
                (deny if siddet == "guclu" else ask).append((siddet, ad))
            else:  # balanced: güçlü → ASK; zayıf → raporla-ama-engelleme (BİLGİ)
                if siddet == "guclu":
                    ask.append((siddet, ad))
                elif bilgi is not None:
                    bilgi.append((siddet, ad))
    return deny, ask


def maskele(metin):
    """Hassas alanları etiketle değiştirilmiş kopya üretir (yerel işleme için)."""
    for pat, etiket in _MASKE:
        metin = pat.sub(etiket, metin)
    # PIN/parola/token gibi 'anahtar: değer' desenlerinde değeri maskele
    metin = re.sub(r"(\b(?:pin\s?kodu?|parola|[sş]ifre|password|passwd|api[_\s-]?key|token|secret|bearer)\b\s*[:=]?\s*)\S+",
                   r"\1[MASKELİ]", metin, flags=re.I)
    return metin


def _yaz_ve_cik(deny, ask, mod, bilgi=None):
    cizgi = "=" * 60
    print(cizgi)
    print(f"OA-GİZLİLİK — TARAMA RAPORU (mod: {mod})")
    print(cizgi)
    if bilgi:
        # Engellemez, exit kodunu değiştirmez; ama sessiz ALLOW da bırakmaz.
        print("\n[BİLGİ] engellemeyen desen(ler) var — dış araca gidiyorsa bilinçli karar olsun")
        for siddet, ad in bilgi:
            print(f"   - {ad}  [{siddet}]")
        print("   (bu satırlar engellemez; anayasa §10 gereği esas no ve benzeri desenler taranır.)")
    if deny:
        print("\n[DENY] bu içerik dış araca GÖNDERİLMEMELİ:")
        for siddet, ad in deny:
            print(f"   - {ad}  [{siddet}]")
        print("\n   UYAP/e-imza/PIN/finansal kimlik varsa: bu adım münhasıran avukata aittir.")
        print("   Claude kod yazmaz/çalıştırmaz/göndermez. Manuel adım öner, yerel işle.")
        print(cizgi)
        return 2
    if ask:
        print("\n[ASK] göndermeden ÖNCE avukattan açık onay al:")
        for siddet, ad in ask:
            print(f"   - {ad}  [{siddet}]")
        print("\n   Onay alınmadan dış araca aktarma. Mümkünse --maskele ile maskele/yerel işle.")
        print(cizgi)
        return 1
    print("\n[ALLOW] belirgin hassas desen bulunamadı.")
    print("   (Tarama desenlere dayanır; emin değilsen yine de avukata danış.)")
    print(cizgi)
    return 0


OVERRIDE_GEREKCE_ASGARI = 30  # şerh konvansiyonuyla aynı alt sınır (>=30 karakter)


def _istisna_defterine_yaz(kok, tur, ilgili, gerekce, onay):
    """E2(d) v0.5.8.5 — İSTİSNA DEFTERİ ortak şeması (append-only JSONL):
    `_oa/defter/istisna-kayitlari.jsonl` satırı = {zaman, tur, ilgili, gerekce,
    onay, imza}. Birden çok araç aynı deftere YALNIZ satır ekleyerek yazar;
    bu yardımcı bilinçli olarak YEREL tutulur (ortak modül bağımlılığı
    yaratılmaz — her araç kendi küçük yazıcısını taşır)."""
    dizin = os.path.join(kok, "_oa", "defter")
    os.makedirs(dizin, exist_ok=True)
    satir = {
        "zaman": datetime.datetime.now().isoformat(timespec="seconds"),
        "tur": tur,
        "ilgili": ilgili,
        "gerekce": gerekce,
        "onay": onay,
        "imza": "gizlilik_tara.py",
    }
    yol = os.path.join(dizin, "istisna-kayitlari.jsonl")
    with open(yol, "a", encoding="utf-8") as f:
        f.write(json.dumps(satir, ensure_ascii=False) + "\n")
    return yol


def main():
    ap = argparse.ArgumentParser(description="oa-gizlilik — deterministik hassas veri / Layer 0 tarayıcı")
    ap.add_argument("dosya")
    ap.add_argument("--mod", choices=["strict", "balanced"], default="strict")
    ap.add_argument("--maskele", metavar="CIKTI", help="maskelenmiş kopyayı bu dosyaya yaz")
    # E2(d) DENY-OVERRIDE PROTOKOLÜ (v0.5.8.5): DENY sonucu YALNIZ bu
    # parametreyle aşılabilir — model tek başına aşamaz; parametre avukatın
    # bilinçli kararını temsil eder ve istisna defterine İZ bırakır.
    ap.add_argument("--override-onay", dest="override_onay", choices=["avukat"],
                    default=None,
                    help="DENY sonucunu bilinçli olarak aşar (yalnız 'avukat'); "
                         "--override-gerekce (>=30 karakter) ZORUNLU; kullanım "
                         "_oa/defter/istisna-kayitlari.jsonl'e kaydedilir")
    ap.add_argument("--override-gerekce", dest="override_gerekce", default=None,
                    help="override gerekçesi (>=30 karakter) — istisna defterine yazılır")
    ap.add_argument("--kok", default=".",
                    help="istisna defterinin yazılacağı çalışma kökü "
                         "(<kok>/_oa/defter/istisna-kayitlari.jsonl; varsayılan: .)")
    args = ap.parse_args()

    # FAIL-CLOSED: override parametresi eksik/yanlış kullanılmışsa hiç taramadan
    # DENY — 'yarım onay' hiçbir sonucu aşamaz.
    if args.override_onay and not (args.override_gerekce
                                   and len(args.override_gerekce.strip()) >= OVERRIDE_GEREKCE_ASGARI):
        print(f"[DENY] --override-onay için --override-gerekce (>= {OVERRIDE_GEREKCE_ASGARI} "
              "karakter) ZORUNLU — gerekçesiz override yok (fail-closed).", file=sys.stderr)
        sys.exit(2)

    # FAIL-CLOSED: taramanın herhangi bir aşaması çökerse DENY (exit 2) — asla sessiz geçme.
    try:
        with open(args.dosya, "r", encoding="utf-8", errors="replace") as f:
            metin = f.read()
    except Exception as e:
        print(f"[DENY] dosya okunamadı ({e}) — tarama yapılamadı, GÖNDERME. (fail-closed)", file=sys.stderr)
        sys.exit(2)

    try:
        bilgi = []
        deny, ask = tara(metin, args.mod, bilgi)
        if args.maskele:
            with open(args.maskele, "w", encoding="utf-8") as f:
                f.write(maskele(metin))
            print(f"Maskelenmiş kopya yazıldı: {args.maskele}")
        kod = _yaz_ve_cik(deny, ask, args.mod, bilgi)
        if kod == 2 and args.override_onay == "avukat":
            # DENY aşımı: rapor AYNEN basıldı (görünürlük); iz istisna defterine.
            yol = _istisna_defterine_yaz(args.kok, "gizlilik-deny-override",
                                         args.dosya, args.override_gerekce.strip(),
                                         "avukat")
            print("\n[OVERRIDE] DENY, avukat onayıyla AŞILDI — sorumluluk bilinçli "
                  "karara aittir; istisna defterine kaydedildi:")
            print(f"   {yol}")
            sys.exit(0)
        sys.exit(kod)
    except SystemExit:
        raise
    except Exception as e:
        print(f"[DENY] tarama sırasında beklenmeyen hata ({e}) — fail-closed, GÖNDERME.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

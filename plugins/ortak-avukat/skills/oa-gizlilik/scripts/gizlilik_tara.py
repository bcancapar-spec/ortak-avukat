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

import re
import sys
import argparse

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

# --- Hassas veri desenleri (mod'a göre deny/ask) ---
HASSAS = [
    ("Esas/Karar no (taraf bağlamı olabilir)", "zayif",
     re.compile(r"\b(?:19|20)\d{2}\s?/\s?\d{1,6}(?:\s*(?:E|K|Esas|Karar)\.?)?\b", re.I)),
    ("Sağlık verisi (KVKK m.6 özel nitelikli)", "guclu",
     re.compile(r"\b(te[sş]his|tan[ıi]\b|rapor|hastal[ıi][kğ]|hastane|klinik|poliklinik|psikiyatr|psikoloj|"
                r"engel(li|\s?oran)|sa[gğ]l[ıi]k|t[ıi]bb[iî]|tedavi|ameliyat|operasyon|kanser|t[üu]m[öo]r|hiv|aids|"
                r"hepatit|ila[çc]\b|re[çc]ete|tahlil|biyopsi|gebe|hamile|ruh\s?sa[gğ]l[ıi]|ba[gğ][ıi]ml[ıi]l[ıi]k)\b", re.I)),
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

    # Kart no: Luhn tutan → MUTLAK; tutmayan uzun dizi → 'olası'
    kart_hit = KART.findall(metin)
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
        print("\n[BİLGİ] esas/karar no var — dış araca gidiyorsa bilinçli karar olsun")
        for siddet, ad in bilgi:
            print(f"   - {ad}  [{siddet}]")
        print("   (balanced modda engellenmez; anayasa §10 gereği esas no taranır.)")
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


def main():
    ap = argparse.ArgumentParser(description="oa-gizlilik — deterministik hassas veri / Layer 0 tarayıcı")
    ap.add_argument("dosya")
    ap.add_argument("--mod", choices=["strict", "balanced"], default="strict")
    ap.add_argument("--maskele", metavar="CIKTI", help="maskelenmiş kopyayı bu dosyaya yaz")
    args = ap.parse_args()

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
        sys.exit(_yaz_ve_cik(deny, ask, args.mod, bilgi))
    except SystemExit:
        raise
    except Exception as e:
        print(f"[DENY] tarama sırasında beklenmeyen hata ({e}) — fail-closed, GÖNDERME.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

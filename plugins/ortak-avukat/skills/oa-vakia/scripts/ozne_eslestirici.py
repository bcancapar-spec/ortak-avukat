#!/usr/bin/env python3
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
# VENDOR: github.com/semantica-agi/semantica@v0.6.5
#         deduplication/similarity_calculator.py:529-615 ALGORİTMA uyarlaması
#         (Jaro-Winkler + iki-satır DP Levenshtein; kod stdlib'de yeniden
#         yazıldı, paket bağımlılığı YOK — m.0 devşirme protokolü, vendor
#         kuralı: dondurulmuş, testli [tests/test_ozne_eslestirici.py]).
"""
oa-vakia — ozne_eslestirici.py  (v0.5.8 P4 — M9 ÖZNE/BEYAN ANATOMİSİ motoru)

OCR'lı UYAP külliyatında aynı öznenin yazım varyantlarını ("Balçal / BALCAL /
Bal.al" sınıfı) deterministik benzerlikle eşler. Saha kanıtı (Çal 1079,
3.968 sayfa OCR): model varyantları sezgiyle birleştirdi — doğruydu ama
DENETİMSİZDİ; "öznenin tüm beyanları" sorgusu varyant yüzünden kayıt
kaçırabilir (kayıpsızlık invaryantının sessiz ihlali).

FELSEFE: KARAR VERMEZ, DAMGA BASAR (advisory; her zaman exit 0):
  skor >= 0.92  → BAGLA        (aynı özne — advisory bağ)
  0.80 - 0.92   → AVUKATA-SOR  (kardeş/akraba adı olabilir — karar avukatta)
  < 0.80        → sessiz (ayrı özne)
Semantica'dan BİLİNÇLİ ALINMAYANLAR: Soundex (İngilizce ses sınıfları Ç/Ş/Ğ
düşürür), embedding (Yargı Pro'da var), sessiz çatışma çözümü (çelişki
avukata ÇIKAR — K3 ilkesi).

Kullanım:
  python ozne_eslestirici.py --girdi ozneler.json [--json]
  python ozne_eslestirici.py "Ahmet Balçal" "BALCAL Ahmet" "Bal.al"
Girdi JSON: ["ad1", "ad2", ...]  veya  [{"id": "V1", "ad": "..."}, ...]
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
import re
import sys

BAGLA_ESIK = 0.92
SOR_ESIK = 0.80

_TR_KUCUK = str.maketrans({"İ": "i", "I": "ı"})


def tr_normalize(ad):
    """Türkçe-doğru küçültme + OCR gürültü temizliği (nokta/kesme/tire) +
    boşluk sadeleştirme. Türkçe harfler KORUNUR (Soundex'in aksine)."""
    s = str(ad).translate(_TR_KUCUK).lower()
    s = re.sub(r"[.'’`\-_]", "", s)          # OCR nokta/kesme gürültüsü
    s = re.sub(r"[^0-9a-zçğıöşü ]", " ", s)  # kalan yabancı işaretler → boşluk
    return re.sub(r"\s+", " ", s).strip()


def levenshtein_benzerlik(a, b):
    """İki-satır DP (O(min) bellek) — semantica :529-547 deseninin uyarlaması."""
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
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


def ozne_skoru(ad1, ad2):
    """max(JW, Levenshtein) + gerekçe listesi. JW önek-ağırlıklıdır, kelime
    ortası OCR bozulmasını ıskalayabilir — Levenshtein o açığı kapatır."""
    n1, n2 = tr_normalize(ad1), tr_normalize(ad2)
    if not n1 or not n2:
        return 0.0, ["bos-ad"]
    nedenler = []
    if n1 == n2:
        return 1.0, ["normalize-sonrasi-birebir"]
    jw = jaro_winkler(n1, n2)
    lev = levenshtein_benzerlik(n1, n2)
    skor = max(jw, lev)
    nedenler.append(f"jaro_winkler={jw:.3f}")
    nedenler.append(f"levenshtein={lev:.3f}")
    t1, t2 = set(n1.split()), set(n2.split())
    ortak = t1 & t2
    if ortak:
        nedenler.append(f"ortak_token={len(ortak)}")
    return skor, nedenler


def eslestir(ozneler):
    """Tüm çiftleri skorlar; SOR_ESIK üstünü karar damgasıyla döndürür
    (deterministik sıra: girdi sırası korunur)."""
    kayitlar = []
    for x in ozneler:
        if isinstance(x, dict):
            kayitlar.append((x.get("id") or f"V{len(kayitlar)+1}",
                             x.get("ad", "")))
        else:
            kayitlar.append((f"V{len(kayitlar)+1}", str(x)))
    sonuc = []
    for i in range(len(kayitlar)):
        for j in range(i + 1, len(kayitlar)):
            id1, ad1 = kayitlar[i]
            id2, ad2 = kayitlar[j]
            skor, nedenler = ozne_skoru(ad1, ad2)
            if skor >= SOR_ESIK:
                karar = "BAGLA" if skor >= BAGLA_ESIK else "AVUKATA-SOR"
                sonuc.append({"a": {"id": id1, "ad": ad1},
                              "b": {"id": id2, "ad": ad2},
                              "skor": round(skor, 3), "karar": karar,
                              "nedenler": nedenler})
    return sonuc


def main():
    ap = argparse.ArgumentParser(
        description="M9 özne-varyant eşleştirici (advisory — karar avukatta)")
    ap.add_argument("adlar", nargs="*", help="doğrudan ad listesi")
    ap.add_argument("--girdi", default=None, help="JSON dosyası")
    ap.add_argument("--json", action="store_true", help="makine-okur çıktı")
    args = ap.parse_args()

    if args.girdi:
        with open(args.girdi, encoding="utf-8") as f:
            ozneler = json.load(f)
    else:
        ozneler = args.adlar
    sonuc = eslestir(ozneler or [])

    if args.json:
        print(json.dumps({"esik_bagla": BAGLA_ESIK, "esik_sor": SOR_ESIK,
                          "eslesmeler": sonuc}, ensure_ascii=False))
        sys.exit(0)
    if not sonuc:
        print("özne-eşleştirici: eşik üstü çift yok (tüm özneler AYRI).")
    for e in sonuc:
        isaret = "✓" if e["karar"] == "BAGLA" else "?"
        print(f"  {isaret} {e['karar']} [{e['skor']}] «{e['a']['ad']}» ↔ "
              f"«{e['b']['ad']}»  ({', '.join(e['nedenler'])})")
    sys.exit(0)  # advisory — karar vermez, damga basar


if __name__ == "__main__":
    main()

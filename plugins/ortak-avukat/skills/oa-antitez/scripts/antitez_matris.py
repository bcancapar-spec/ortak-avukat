#!/usr/bin/env python3
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
antitez_matris.py — DETERMİNİSTİK antitez/çürütme motoru.

Amaç (Can): Antitez DURUM FARKINDALIĞI içindir. Karşı tarafın bizi kapatacak
savunma/iddialarını işin ilk etabında görür, sonra her birini ÇÖKERTİRİZ.
Çıktı: çürütülmüş ve güçlenmiş konumumuz + dürüstçe işaretlenmiş artık riskler.

Dürüst sınır (anayasa gereği): Bu script hukuki içeriği ÜRETMEZ. İki deterministik
iş yapar:
  1. İSKELET: sabit, eksiksiz "saldırı cepheleri" listesini ve doldurulacak matris
     şablonunu üretir (protokol her seferinde aynı sırada çalışır).
  2. DENETİM: doldurulmuş matrisi eksiksizlik + bütünlük açısından denetler —
     hiçbir cephe atlanmadı mı, her antitezin çürütmesi YA DA işaretli artık riski
     var mı, her çürütme dayanağı teyitli mi. Eksikleri/kör noktaları raporlar.
Hukuki muhakemeyi sen yaparsın; künyeyi oa-ictihat (Yargı/Mevzuat MCP) doğrular.

Kullanım:
  python antitez_matris.py --iskelet                 # cepheler + boş şablon
  python antitez_matris.py --dogrula matris.json      # doldurulmuş matrisi denetle
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


import argparse
import json
import sys

# --- Sabit saldırı cepheleri (deterministik omurga — eksiksiz değerlendirilir) ---
STANDART_CEPHELER = {
    "usul":            "Usul/şekil: görev, yetki, derdestlik, kesin hüküm, husumet, dava şartı, süre/hak düşürücü",
    "maddi_vakia":     "Maddi vakıa: olgu doğru/ispatlanabilir mi, iç çelişki var mı",
    "ispat_delil":     "İspat ve delil: ispat yükü kimde, delil caiz mi (HMK m.189/2), yeterli mi",
    "hukuki_niteleme": "Hukuki niteleme: olguya uygulanan norm doğru mu, alternatif norm/sonuç",
    "ictihat":         "İçtihat: dayanılan karar esastan mı, güncel mi, aleyhe içtihat/daire kayması var mı",
    "zamanasimi":      "Zamanaşımı / hak düşürücü süre",
    "defi_karsi_talep":"Def'i / karşı talep / takas (ödeme, ifa, zamanaşımı def'i)",
    "muvekkil_zaaf":   "Müvekkilin kendi belgelerindeki zaaf (oa-kontrol C protokolü ile)",
}

GUC_DEGERLERI = {"yuksek", "orta", "dusuk", "yok"}
DAYANAK_DURUMLARI = {"teyitli", "teyitsiz", "yok"}


def iskelet():
    print("=" * 70)
    print("  ANTİTEZ CEPHELERİ — durum farkındalığı için EKSİKSİZ değerlendirilir")
    print("=" * 70)
    for k, v in STANDART_CEPHELER.items():
        print(f"  [{k}]\n      {v}")
    print("\n--- Doldurulacak matris şablonu (JSON) ---")
    sablon = {
        "tez": "Müvekkilin ana tezi — bir cümle",
        "cepheler": [
            {
                "cephe": k,
                "antitez": "Karşı tarafın bu cepheden saldırısı (saldırı yoksa kısaca 'değerlendirildi: saldırı zayıf/yok')",
                "guc": "yuksek|orta|dusuk|yok",
                "curutme": "Bizim çürütmemiz (antitezi nasıl çökertiyoruz)",
                "curutme_dayanak": "Çürütmenin içtihat/mevzuat künyesi veya boş",
                "dayanak_durum": "teyitli|teyitsiz|yok",
                "artik_risk": "Çürütülemeyen kalıntı risk (varsa) — dürüstçe yaz",
            }
            for k in STANDART_CEPHELER
        ],
    }
    print(json.dumps(sablon, ensure_ascii=False, indent=2))
    print("\nDoldurduktan sonra: python antitez_matris.py --dogrula matris.json")


def dogrula(path):
    try:
        with open(path, encoding="utf-8") as f:
            m = json.load(f)
    except Exception as e:
        print(f"❌ JSON okunamadı: {e}")
        sys.exit(1)

    tez = m.get("tez", "(tez belirtilmemiş)")
    cepheler = m.get("cepheler", [])
    verilen = {c.get("cephe") for c in cepheler}

    eksik_cepheler = [k for k in STANDART_CEPHELER if k not in verilen]
    curutulmemis = []      # saldırı var ama ne çürütme ne artık risk
    teyitsiz_dayanak = []  # çürütme bir künyeye dayanıyor ama teyitsiz
    dayanaksiz_guclu = []  # güçlü antiteze dayanaksız çürütme
    artik_riskler = []     # dürüst kalıntı riskler
    gecersiz = []          # şema hatası

    saldiri_sayisi = 0
    cozulen = 0

    for c in cepheler:
        ad = c.get("cephe", "(adsız)")
        guc = (c.get("guc") or "").lower()
        curutme = (c.get("curutme") or "").strip()
        dayanak = (c.get("curutme_dayanak") or "").strip()
        durum = (c.get("dayanak_durum") or "").lower()
        risk = (c.get("artik_risk") or "").strip()

        if guc and guc not in GUC_DEGERLERI:
            gecersiz.append(f"{ad}: geçersiz 'guc' = {guc}")
        if durum and durum not in DAYANAK_DURUMLARI:
            gecersiz.append(f"{ad}: geçersiz 'dayanak_durum' = {durum}")

        if guc in {"yuksek", "orta", "dusuk"}:
            saldiri_sayisi += 1
            if not curutme and not risk:
                curutulmemis.append(ad)
            elif curutme or risk:
                cozulen += 1
            if curutme and dayanak and durum == "teyitsiz":
                teyitsiz_dayanak.append(f"{ad}: '{dayanak}'")
            if guc == "yuksek" and curutme and not dayanak:
                dayanaksiz_guclu.append(ad)
            if risk:
                artik_riskler.append(f"{ad}: {risk}")

    # --- Rapor ---
    print("=" * 70)
    print("  ANTİTEZ DENETİMİ — KARAR-MALZEMESİ, NİHAİ TEYİT KULLANICININDIR")
    print("=" * 70)
    print(f"Tez: {tez}\n")

    kapsam = (len(STANDART_CEPHELER) - len(eksik_cepheler)) / len(STANDART_CEPHELER)
    print(f"Cephe kapsamı     : {len(STANDART_CEPHELER)-len(eksik_cepheler)}/{len(STANDART_CEPHELER)} (%{kapsam*100:.0f})")
    if saldiri_sayisi:
        print(f"Çürütme kapsamı   : {cozulen}/{saldiri_sayisi} saldırı çürütüldü/işaretlendi")
    print()

    def blok(baslik, items, isaret="!"):
        if items:
            print(f"--- {baslik} ---")
            for it in items:
                print(f"  {isaret} {it}")
            print()

    blok("AÇIK CEPHELER (değerlendirilmemiş — KÖR NOKTA)", eksik_cepheler, "✗")
    blok("ÇÜRÜTÜLMEMİŞ ANTİTEZLER (ne çürütme ne risk işareti)", curutulmemis, "✗")
    blok("TEYİTSİZ DAYANAK (atıf denetimi — oa-kontrol A)", teyitsiz_dayanak, "!")
    blok("GÜÇLÜ ANTİTEZE DAYANAKSIZ ÇÜRÜTME (zayıf)", dayanaksiz_guclu, "!")
    blok("ŞEMA HATASI", gecersiz, "!")
    blok("ARTIK RİSKLER (çürütülemeyen — dürüst rapor; müvekkile sun)", artik_riskler, "→")

    saglikli = not (eksik_cepheler or curutulmemis or teyitsiz_dayanak or gecersiz)
    if saglikli:
        print(">>> Matris bütünlüğü TAMAM: tüm cepheler değerlendirildi, her saldırı")
        print("    çürütüldü ya da artık risk olarak işaretlendi, dayanaklar teyitli. <<<")
    else:
        print(">>> Matris bütünlüğü EKSİK: yukarıdaki kör noktalar/eksikler kapatılmadan")
        print("    dosya 'durum farkındalığı tam' sayılmaz. <<<")
    print("=" * 70)


def main():
    p = argparse.ArgumentParser(description="Deterministik antitez/çürütme motoru")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--iskelet", action="store_true", help="Cephe listesi + boş şablon üret")
    g.add_argument("--dogrula", metavar="JSON", help="Doldurulmuş matrisi denetle")
    a = p.parse_args()
    if a.iskelet:
        iskelet()
    else:
        dogrula(a.dogrula)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # head/less gibi araçlara borulanınca sessizce çık
        sys.stderr.close()

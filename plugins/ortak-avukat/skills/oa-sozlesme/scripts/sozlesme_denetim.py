#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
sozlesme_denetim.py — oa-sozlesme deterministik KAPSAM denetimi

Script hukuki değerlendirme YAPMAZ; kapsam eksiksizliğini garanti eder:
- zorunlu kloz kategorilerinden sessizce atlanan var mı,
- yüksek/kritik riskli kloza önlem (redline/alternatif/fallback) yazılmış mı,
- şekil şartı ve imza yetkisi DEĞERLENDİRİLMİŞ mi (içeriği model kurar),
- kırmızı çizgiler tanımlı mı (İNCELEME modunda müzakere planının ön şartı).

Kullanım:
  python sozlesme_denetim.py --iskelet > _oa/cikti/sozlesme.json
  python sozlesme_denetim.py --dogrula _oa/cikti/sozlesme.json
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, json, sys

ZORUNLU_KATEGORILER = [
    "taraflar_temsil_imza_yetkisi", "konu_edimler", "bedel_odeme_ifa",
    "sure_uzama", "temerrut_cezai_sart_faiz", "fesih_tasfiye", "gizlilik",
    "kvkk_veri", "rekabet_yasagi_munhasirlik", "devir_temlik", "mucbir_sebep",
    "bildirim_tebligat", "uyusmazlik_cozumu", "delil_sozlesmesi",
    "butunluk_merger", "sekil_sarti",
]
RISK_BANTLARI = {"kritik", "yuksek", "orta", "dusuk", "yok"}
DURUMLAR = {"VAR", "YOK-GEREKSIZ", "YOK-EKSIK"}


def iskelet():
    d = {
        "mod": "TAHRIR | INCELEME",
        "tip": "ör. hizmet, NDA, bayilik...",
        "kategoriler": {
            k: {"durum": "YOK-EKSIK", "risk": "yok",
                "not": "", "onlem": ""}
            for k in ZORUNLU_KATEGORILER
        },
        "kirmizi_cizgiler": [],
        "acik_uclar": [],
    }
    print(json.dumps(d, ensure_ascii=False, indent=2))


def dogrula(yol):
    with open(yol, encoding="utf-8") as f:
        d = json.load(f)
    sorunlar, uyarilar = [], []
    kats = d.get("kategoriler", {})

    for k in ZORUNLU_KATEGORILER:
        if k not in kats:
            sorunlar.append(f"kategori tamamen atlanmış: {k} (sessiz atlama)")
            continue
        v = kats[k]
        durum = v.get("durum")
        if durum not in DURUMLAR:
            sorunlar.append(f"{k}: geçersiz durum '{durum}' ({sorted(DURUMLAR)})")
            continue
        if durum == "YOK-GEREKSIZ" and len(v.get("not", "").strip()) < 10:
            sorunlar.append(f"{k}: YOK-GEREKSIZ gerekçesiz olamaz ('not' alanı)")
        if durum == "YOK-EKSIK":
            uyarilar.append(f"{k}: EKSİK — ya kloz yaz(dır) ya gerekçeyle GEREKSIZ işaretle "
                            f"(karşı taslakta eksiklik çoğu kez KASITLIDIR)")
        risk = v.get("risk", "yok")
        if risk not in RISK_BANTLARI:
            sorunlar.append(f"{k}: geçersiz risk bandı '{risk}' (nitel bantlar: {sorted(RISK_BANTLARI)})")
        elif risk in ("kritik", "yuksek") and len(v.get("onlem", "").strip()) < 15:
            sorunlar.append(f"{k}: risk={risk} ama 'onlem' boş — yüksek risk önlemsiz "
                            f"(redline/alternatif kloz/fallback) bırakılamaz")

    ozel = kats.get("sekil_sarti", {})
    if ozel.get("durum") == "VAR" and "teyit" not in (ozel.get("not", "") + ozel.get("onlem", "")).lower():
        uyarilar.append("sekil_sarti: nota Mevzuat MCP teyidinin izi yazılmamış "
                        "(hangi madde, hangi sorgu) — ezber şekil şartı kabul edilmez")

    if d.get("mod", "").upper().startswith("INCELEME") and not d.get("kirmizi_cizgiler"):
        sorunlar.append("İNCELEME modunda kırmızı çizgi listesi boş — müzakere planı "
                        "kırmızı çizgi/pazarlık payı ayrımı olmadan kurulamaz (oa-strateji)")

    if uyarilar:
        print("UYARILAR:")
        for u in uyarilar:
            print("  ⚠ " + u)
    if sorunlar:
        print("KAPSAM BOŞLUĞU — bu denetim kapanmadan taslak/redline teslim edilemez:")
        for s in sorunlar:
            print("  ✗ " + s)
        sys.exit(1)
    print("KAPSAM DENETİMİ TEMİZ. (Bu, klozların hukuken YETERLİ olduğunu değil, "
          "hiçbir kategorinin sessizce atlanmadığını garanti eder — içerik yargısı "
          "modelin ve nihai karar avukatındır.)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iskelet", action="store_true")
    ap.add_argument("--dogrula", metavar="JSON")
    a = ap.parse_args()
    if a.iskelet:
        iskelet()
    elif a.dogrula:
        dogrula(a.dogrula)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()

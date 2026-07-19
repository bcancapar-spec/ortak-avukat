#!/usr/bin/env python3
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa-kiyas — kiyas_denetim.py
Hukuki silojizmin (açık kıyas) DETERMİNİSTİK yapı denetimi.

Felsefe: script normun YORUMUNA karar vermez ("unsur oluşmuştur" demez). Yalnızca
yapısal eksikliği yakalar: üç bileşen dolu mu, normun her unsuru bir vakıaya eşlenmiş
mi, küçük önerme delile bağlı mı, büyük önerme içtihatla somutlaştırılmış mı.
Unsurun hukuken gerçekten oluşup oluşmadığı avukatın muhakemesidir.

Girdi:  kiyas.json  (şema references/kiyas-rehberi.md)
Kullanım: python kiyas_denetim.py kiyas.json
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json
import sys


def yukle(yol):
    with open(yol, "r", encoding="utf-8") as f:
        return json.load(f)


def denetle(k):
    rapor = []
    eksik_kritik = False

    buyuk = k.get("buyuk_onerme", {})
    kucuk = k.get("kucuk_onerme", {})
    sonuc = k.get("sonuc")

    veri = {
        "arac": "kiyas_denetim",
        "buyuk_onerme": {
            "norm": buyuk.get("norm"),
            "ictihat": buyuk.get("ictihat", []),
            "unsurlar": buyuk.get("unsurlar", []),
        },
        "kucuk_onerme": {"vakialar": kucuk.get("vakialar", [])},
        "sonuc": sonuc,
        "teyitsiz_ictihat": [],
        "unsur_vakia_eslesme": [],
        "yetim_vakialar": [],
    }

    # 1. Üç bileşen var mı
    rapor.append("### 1. ÜÇLÜ YAPI BÜTÜNLÜĞÜ")
    if not buyuk.get("norm"):
        rapor.append("  ✗ Büyük önerme: norm eksik"); eksik_kritik = True
    else:
        rapor.append(f"  ✓ Norm: {buyuk['norm']}")
    if not kucuk.get("vakialar"):
        rapor.append("  ✗ Küçük önerme: vakıa eksik"); eksik_kritik = True
    else:
        rapor.append(f"  ✓ Küçük önerme: {len(kucuk['vakialar'])} vakıa")
    if not sonuc:
        rapor.append("  ⚠ Sonuç henüz yazılmamış")
    else:
        rapor.append("  ✓ Sonuç var")
    rapor.append("")

    # 2. Büyük önerme içtihatla somutlaştırılmış mı + teyitli mi
    rapor.append("### 2. BÜYÜK ÖNERME — İÇTİHAT VE TEYİT")
    ictihat = buyuk.get("ictihat", [])
    if not ictihat:
        rapor.append("  ⚠ Normu somutlaştıran içtihat yok → oa-ictihat ile emsal ara")
    else:
        for ic in ictihat:
            d = ic.get("dogrulama", "?")
            isaret = "✓" if d == "teyitli" else "⚠"
            rapor.append(f"  {isaret} {ic.get('kunye','(künye yok)')} [{d}]")
            if d != "teyitli":
                rapor.append("     → resmî kaynaktan (Yargı/Mevzuat MCP) teyit et")
                veri["teyitsiz_ictihat"].append(ic.get("kunye", "(künye yok)"))
    rapor.append("")

    # 3. Unsur ↔ vakıa eşleşmesi (kıyasın kalbi)
    rapor.append("### 3. UNSUR ↔ VAKIA EŞLEŞMESİ (subsumtion boşluğu)")
    unsurlar = buyuk.get("unsurlar", [])
    if not unsurlar:
        rapor.append("  ⚠ Norm unsurlarına ayrılmamış — eşleşme denetimi yapılamıyor.")
        rapor.append("     Normu unsurlara böl (örn. fiil/hukuka aykırılık/kusur/zarar/illiyet).")
    else:
        vakialar = kucuk.get("vakialar", [])
        # her unsur en az bir vakıaya 'karsilar' alanıyla bağlanmış olmalı
        karsilanan = {}
        for v in vakialar:
            for u in v.get("karsilar", []):
                karsilanan.setdefault(u, []).append(v)
        for u in unsurlar:
            uid = u.get("id", u) if isinstance(u, dict) else u
            uad = u.get("ad", uid) if isinstance(u, dict) else u
            if uid in karsilanan:
                deliller = [d for v in karsilanan[uid] for d in v.get("dayanak_delil", [])]
                if deliller:
                    rapor.append(f"  ✓ [{uad}] ← vakıa var, delil var")
                    durum = "karsilanan_delilli"
                else:
                    rapor.append(f"  ⚠ [{uad}] ← vakıa var ama DELİLSİZ → oa-vakia")
                    durum = "karsilanan_delilsiz"
            else:
                rapor.append(f"  ✗ [{uad}] ← KARŞILANMAMIŞ unsur (boşluk: ispat veya hukuki dayanak)")
                eksik_kritik = True
                durum = "karsilanmamis"
            veri["unsur_vakia_eslesme"].append(
                {"unsur_id": uid, "unsur_ad": uad, "durum": durum})
    rapor.append("")

    # 4. Yetim vakıa (hiçbir unsuru karşılamayan)
    rapor.append("### 4. YETİM VAKIA (hiçbir norm unsurunu karşılamıyor)")
    yetim = [v for v in kucuk.get("vakialar", []) if not v.get("karsilar")]
    if yetim:
        for v in yetim:
            rapor.append(f"  ⚠ '{v.get('metin','(metin yok)')}' — hangi unsuru karşılıyor? bağla veya çıkar")
            veri["yetim_vakialar"].append(v.get("metin", "(metin yok)"))
    else:
        rapor.append("  ✓ Her vakıa bir unsura bağlı.")
    rapor.append("")

    veri["kritik_bosluk"] = eksik_kritik
    return rapor, eksik_kritik, veri


def main(yol, json_yol=None):
    k = yukle(yol)
    cizgi = "=" * 60
    print(cizgi)
    print("OA-KIYAS — DETERMİNİSTİK SİLOJİZM DENETİM RAPORU")
    print(cizgi)
    rapor, kritik, veri = denetle(k)
    print("\n".join(rapor))
    print(cizgi)
    if kritik:
        print("SONUÇ: Kıyasta KRİTİK BOŞLUK var (karşılanmamış unsur / eksik bileşen).")
        print("Bu boşluk kapanmadan sonuç güvenilir değildir.")
    else:
        print("SONUÇ: Yapı bütün. Unsurların hukuken oluşup oluşmadığı AVUKAT muhakemesidir.")
    print(cizgi)

    if json_yol:
        veri["girdi"] = yol
        with open(json_yol, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"[JSON] Makine-okur sonuc yazildi: {json_yol}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="OA-kiyas deterministik silojizm denetimi")
    p.add_argument("kiyas", nargs="?", help="kiyas.json yolu")
    p.add_argument("--json", dest="json_yol", metavar="YOL",
                   help="denetim sonucunu makine-okur JSON olarak bu yola yaz (opsiyonel)")
    a = p.parse_args()
    if not a.kiyas:
        print("Kullanım: python kiyas_denetim.py kiyas.json [--json out.json]")
        sys.exit(1)
    main(a.kiyas, json_yol=a.json_yol)

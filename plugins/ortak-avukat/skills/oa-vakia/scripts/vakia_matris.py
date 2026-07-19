#!/usr/bin/env python3
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
vakia_matris.py — DETERMİNİSTİK vakıa/delil yönetim motoru.

Amaç: Dosyanın OLGU/DELİL yarısını disipline etmek. (1) Kronoloji kurar, (2) her
iddiayı dayandığı delile eşler, (3) ispat boşluklarını ve yetim delilleri yakalar.

Dürüst sınır (anayasa): Script hukuki değerlendirme yapmaz. Deterministik olarak
SIRALAR (kronoloji), EŞLER (iddia↔delil) ve BOŞLUK/YETİM tespiti yapar. İspatın
yeterli olup olmadığına, delilin caiz olup olmadığına muhakeme + oa-kontrol/oa-antitez
(ispat_delil cephesi) karar verir.

Kullanım:
  python vakia_matris.py --iskelet
  python vakia_matris.py --dogrula vakia.json
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, json, sys
from datetime import date

ISPAT = {"belgeli","tanik","bilirkisi","karine","ikrar","yemin","ispatsiz"}

def iskelet():
    print("="*68); print("  VAKIA/DELİL MATRİSİ — kronoloji + iddia↔delil eşleme"); print("="*68)
    print("ispat_durumu değerleri:", ", ".join(sorted(ISPAT)))
    sablon = {
        "iddialar": [{"id":"I1","metin":"İspatlanacak maddi iddia — bir cümle"}],
        "olaylar": [{
            "tarih":"YYYY-MM-DD","olgu":"Ne oldu (kısa)",
            "belge":"Dayanak belge/delil (sözleşme, ihtarname, tutanak, tanık...) veya boş",
            "destekler":["I1"],
            "ispat_durumu":"belgeli|tanik|bilirkisi|karine|ikrar|yemin|ispatsiz"
        }]
    }
    print("\n--- Doldurulacak şablon (JSON) ---")
    print(json.dumps(sablon, ensure_ascii=False, indent=2))
    print("\nDoldurduktan sonra: python vakia_matris.py --dogrula vakia.json")

def _parse_tarih(s):
    try: return date.fromisoformat(s)
    except Exception: return None

def dogrula(path, json_yol=None):
    try:
        with open(path, encoding="utf-8") as f: m = json.load(f)
    except Exception as e:
        print(f"❌ JSON okunamadı: {e}"); sys.exit(1)
    iddialar = {i.get("id"): i.get("metin","") for i in m.get("iddialar",[])}
    olaylar = m.get("olaylar",[])

    tarihli, tarihsiz = [], []
    for o in olaylar:
        d = _parse_tarih(o.get("tarih","") or "")
        (tarihli if d else tarihsiz).append((d,o))
    tarihli.sort(key=lambda x: x[0])

    print("="*68); print("  VAKIA/DELİL DENETİMİ — KARAR-MALZEMESİ"); print("="*68)

    # 1) Kronoloji
    kronoloji = []
    print("\n--- KRONOLOJİ ---")
    for d,o in tarihli:
        bel = o.get("belge","") or "—"
        print(f"  {d.isoformat()} | {o.get('olgu','')}  [delil: {bel}; {o.get('ispat_durumu','?')}]")
        kronoloji.append({"tarih": d.isoformat(), "olgu": o.get("olgu",""),
                          "belge": o.get("belge","") or "", "ispat_durumu": o.get("ispat_durumu","")})
    if tarihsiz:
        print("  (tarihsiz — sıralanamadı:)")
        for _,o in tarihsiz: print(f"   ? {o.get('olgu','')}")

    # 2) İddia↔delil matrisi + ispat boşlukları
    print("\n--- İDDİA ↔ DELİL MATRİSİ ---")
    bos_iddia = []
    matris = []
    for iid, metin in iddialar.items():
        destek = [o for o in olaylar if iid in (o.get("destekler") or [])]
        belgeli = [o for o in destek if (o.get("ispat_durumu") or "")!="ispatsiz" and (o.get("belge") or "")]
        print(f"  [{iid}] {metin}")
        if destek:
            for o in destek:
                print(f"       ← {o.get('tarih','?')} {o.get('olgu','')} ({o.get('ispat_durumu','?')})")
        if not belgeli:
            bos_iddia.append(iid)
            print("       ⚠ İSPAT BOŞLUĞU: bu iddiayı destekleyen belgeli/somut delil yok")
        matris.append({
            "iddia_id": iid, "metin": metin,
            "destekler": [o.get("olgu","") for o in destek],
            "belgeli": bool(belgeli),
        })

    # 3) Yetim / eşlenmemiş deliller + geçersiz referans
    yetim, gecersiz_ref, gecersiz_durum = [], [], []
    for o in olaylar:
        dest = o.get("destekler") or []
        if not dest:
            yetim.append(o.get("olgu",""))
        for r in dest:
            if r not in iddialar: gecersiz_ref.append(f"{o.get('olgu','')} → bilinmeyen iddia '{r}'")
        if (o.get("ispat_durumu") or "") not in ISPAT:
            gecersiz_durum.append(f"{o.get('olgu','')}: '{o.get('ispat_durumu')}'")

    def blok(b, items, mark="!"):
        if items:
            print(f"\n--- {b} ---")
            for it in items: print(f"  {mark} {it}")

    blok("İSPAT BOŞLUKLARI (delilsiz iddialar — ispat yükü riski)", bos_iddia, "✗")
    blok("YETİM DELİLLER (hiçbir iddiaya bağlanmamış olgu)", yetim, "!")
    blok("GEÇERSİZ İDDİA REFERANSI", gecersiz_ref, "!")
    blok("GEÇERSİZ ispat_durumu", gecersiz_durum, "!")

    # Özet
    n_id = len(iddialar); n_destekli = n_id - len(bos_iddia)
    print("\n--- ÖZET ---")
    print(f"  İddia: {n_id} | belgeli destekli: {n_destekli} | ispat boşluğu: {len(bos_iddia)}")
    print(f"  Olay: {len(olaylar)} | tarihsiz: {len(tarihsiz)} | yetim: {len(yetim)}")
    saglikli = not (bos_iddia or tarihsiz or gecersiz_ref or gecersiz_durum)
    print(">>> Dosya olgu/delil bütünlüğü " + ("TAMAM <<<" if saglikli else "EKSİK — yukarıdakiler kapatılmalı <<<"))
    print("="*68)

    if json_yol:
        sonuc = {
            "arac": "vakia_matris", "girdi": path,
            "kronoloji": kronoloji,
            "tarihsiz": [o.get("olgu","") for _,o in tarihsiz],
            "iddia_delil_matrisi": matris,
            "ispat_bosluklari": bos_iddia,
            "yetim_deliller": yetim,
            "gecersiz_referans": gecersiz_ref,
            "gecersiz_ispat_durumu": gecersiz_durum,
            "ozet": {"iddia": n_id, "belgeli_destekli": n_destekli,
                     "ispat_boslugu": len(bos_iddia), "olay": len(olaylar),
                     "tarihsiz": len(tarihsiz), "yetim": len(yetim)},
            "saglikli": saglikli,
        }
        with open(json_yol, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"[JSON] Makine-okur sonuc yazildi: {json_yol}")

def main():
    p = argparse.ArgumentParser(description="Deterministik vakıa/delil motoru")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--iskelet", action="store_true")
    g.add_argument("--dogrula", metavar="JSON")
    p.add_argument("--json", dest="json_yol", metavar="YOL",
                   help="--dogrula ile: denetim sonucunu makine-okur JSON olarak bu yola yaz (opsiyonel)")
    a = p.parse_args()
    iskelet() if a.iskelet else dogrula(a.dogrula, json_yol=a.json_yol)

if __name__=="__main__":
    try: main()
    except BrokenPipeError: sys.stderr.close()

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

import argparse, importlib.util, json, os, sys
from datetime import date

ISPAT = {"belgeli","tanik","bilirkisi","karine","ikrar","yemin","ispatsiz"}


# ── v0.5.8.4 ÖZNE TETİĞİ (372 karnesi: ozne_eslestirici'yi HİÇBİR akış
# çağırmıyordu — kullanıcı kararı: tetik oa-vakia'ya bağlanır). vakia_matris
# matris kurarken taraf/özne yazım varyantlarını toplar ve kardeş motorun
# jaro_winkler + eşikleriyle (BAGLA >= 0.92 / AVUKATA-SOR 0.80-0.92) damgalar.
# ADVISORY — karar vermez, `saglikli` hesabına GİRMEZ; varyant yoksa sessiz.

def _ozne_eslestirici_modulu():
    """ozne_eslestirici.py'yi (aynı dizin) İN-PROCESS import eder — algoritma
    TEKRARLANMAZ (tek-yazar kuralı; ozne_eslestirici.py DEĞİŞTİRİLMEZ, yalnız
    kullanılır). Import çökerse None döner; çağıran taraf bunu GÖRÜNÜR uyarıya
    çevirir (sessiz atlama yasağı)."""
    yol = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "ozne_eslestirici.py")
    if not os.path.isfile(yol):
        return None
    try:
        spec = importlib.util.spec_from_file_location("_vakia_ozne_eslestirici", yol)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def _ozne_adlarini_topla(m):
    """Matris girdisindeki taraf/özne YAZIMLARINI deterministik sırayla toplar:
    üst-düzey `taraflar` listesi (dize veya {"ad": ...}) + her olayın opsiyonel
    `ozne` alanı. Birebir aynı dize TEK sayılır (aynı yazım varyant değildir)."""
    adlar, gorulen = [], set()

    def _ekle(ad):
        ad = str(ad or "").strip()
        if ad and ad not in gorulen:
            gorulen.add(ad); adlar.append(ad)

    for t in m.get("taraflar", []) or []:
        _ekle(t.get("ad") if isinstance(t, dict) else t)
    for o in m.get("olaylar", []) or []:
        _ekle(o.get("ozne") if isinstance(o, dict) else None)
    return adlar


def ozne_eslestirme_kur(m):
    """tr_normalize sonrası aynı özneye ait GÖRÜNEN birden çok yazım varsa
    ozne_eslestirici skorlarıyla `ozne_eslestirme` bölümünü kurar:
      [{"varyantlar": [...], "skor": f, "karar": "BAGLA"|"AVUKATA-SOR"}]
    Varyant yoksa boş liste (sessiz). Döner: (bulgular, uyari) — `uyari`
    yalnız kardeş modül import edilemezse dolar (görünür fail-open)."""
    adlar = _ozne_adlarini_topla(m)
    if len(adlar) < 2:
        return [], None
    oe = _ozne_eslestirici_modulu()
    if oe is None:
        return [], ("ozne_eslestirici.py import edilemedi — özne yazım-varyantı "
                    "taraması YAPILAMADI (advisory; varyant birleştirme kararı "
                    "avukatta kalır)")
    bulgular = [{"varyantlar": [e["a"]["ad"], e["b"]["ad"]],
                 "skor": e["skor"], "karar": e["karar"]}
                for e in oe.eslestir(adlar)]
    return bulgular, None

def iskelet():
    print("="*68); print("  VAKIA/DELİL MATRİSİ — kronoloji + iddia↔delil eşleme"); print("="*68)
    print("ispat_durumu değerleri:", ", ".join(sorted(ISPAT)))
    sablon = {
        "taraflar": ["Taraf/özne adı (opsiyonel — yazım varyantları otomatik taranır, v0.5.8.4)"],
        "iddialar": [{"id":"I1","metin":"İspatlanacak maddi iddia — bir cümle"}],
        "olaylar": [{
            "tarih":"YYYY-MM-DD","olgu":"Ne oldu (kısa)",
            "ozne":"Olayın öznesi/faili (opsiyonel — özne varyant taramasına girer)",
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

    # 4) Özne yazım-varyantı taraması (v0.5.8.4 ÖZNE TETİĞİ — advisory,
    # saglikli hesabına GİRMEZ; "öznenin tüm beyanları" sorgusu varyant
    # yüzünden kayıt kaçırmasın — kayıpsızlık invaryantı). Varyant yoksa
    # SESSİZ (blok basılmaz); kardeş modül çökerse görünür uyarı.
    ozne_bulgular, ozne_uyari = ozne_eslestirme_kur(m)
    if ozne_uyari:
        print(f"\n  ! {ozne_uyari}")
    if ozne_bulgular:
        print("\n--- ÖZNE EŞLEŞTİRME (yazım varyantları — advisory, karar avukatta) ---")
        for b in ozne_bulgular:
            isaret = "?" if b["karar"] == "AVUKATA-SOR" else "~"
            print(f"  {isaret} {b['karar']} [{b['skor']}] "
                  + " ↔ ".join(f"«{v}»" for v in b["varyantlar"]))

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
            "ozne_eslestirme": ozne_bulgular,
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

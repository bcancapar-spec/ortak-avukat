#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
delil_plani.py — DELİL TEDARİK PLANI DENETİMİ (oa-vakia · v0.5.18 adayı).

NEDEN VAR: vakia_matris ispat boşluğunu (delilsiz vakıa iddiasını) BULUR ama
boşluğun nasıl kapatılacağını izlemez. Sahadaki desen: analizde "eksik delil"
yazılır, dilekçede "sair deliller / bilahare bildirilecek deliller" denir ve
delil ancak duruşmada aranır — kamera kaydı, log, HTS gibi kaybolabilir delil o
tarihte artık yoktur; süresinde gösterilmeyen delil ise ancak izinle
gösterilebilir (HMK m.145). Bu script her ispat boşluğunun somut bir TEDARİK
satırına (kaynak · yöntem · kim · aciliyet · son gün · dayanak · durum)
bağlandığını MEKANİK olarak denetler.
Fikir kaynağı: Yargı PRO 16-4 (delil toplama planı) — kod/metin ALINMADI.

Girdi:
  --matris : vakia_matris.py --dogrula … --json <yol> çıktısı (ispat_bosluklari,
             iddia_delil_matrisi)
  --plan   : model/avukatın yazdığı plan JSON'u:
     {"satirlar": [{"iddia_id": "I1", "hedef_delil": "…", "kaynak": "…",
       "yontem": "…", "kim": "MUVEKKIL|AVUKAT|MAHKEME|KURUM|KARSI_TARAF",
       "aciliyet": "KAYBOLUYOR|SURELI|NORMAL", "son_gun": "YYYY-MM-DD|BELIRLENEMEDI",
       "dayanak": "<kanun+madde> | TEYIDE MUHTAC",
       "durum": "PLANLANDI|TALEP_EDILDI|GELDI|GELMEDI"}]}
  --iskelet: --matris ile birlikte; her ispat boşluğu için doldurulacak satır
             iskeletini STDOUT'a basar (iskelet DOLDURULMADAN denetimden GEÇMEZ).

Ne yapmaz: ispat kuralını koymaz (yük kimde, delil caiz mi — model + HMK
m.190, 200-203), dilekçe/müzekkere metni yazmaz, gelen delili değerlendirmez,
SÜRE HESAPLAMAZ (son gün oa-sure'dedir), dosya YAZMAZ (JSON stdout'a).

Dayanaklar (Yargı PRO MCP mevzuat_getir, teyit 2026-10-05): HMK m.145 (sonradan
delil — izne bağlı), m.190 (ispat yükü), m.240/2 (tanık listesi; ikinci liste
verilemez), m.324 (delil avansı — kesin süre; yatırılmazsa delilden vazgeçilmiş
sayılır), m.400 (delil tespiti — kaybolma/zorlaşma ihtimalinde hukuki yarar).

Çıkış: 0 PLAN TAM · 1 PLAN EKSİK/HATALI (tedariksiz boşluk, muğlak ya da geçersiz
satır) · 2 girdi okunamadı/şema dışı.

Kullanım:
  python delil_plani.py --matris _oa/cikti/04-vakia-denetim.json --iskelet > _oa/cikti/04-delil-plani.json
  python delil_plani.py --matris _oa/cikti/04-vakia-denetim.json --plan _oa/cikti/04-delil-plani.json [--json]
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import datetime as _dt
import json
import os
import re
import sys

ARAC = "delil_plani"
AZAMI_BAYT = 8 * 1024 * 1024
KIM = ("MUVEKKIL", "AVUKAT", "MAHKEME", "KURUM", "KARSI_TARAF")
ACILIYET = ("KAYBOLUYOR", "SURELI", "NORMAL")
DURUM = ("PLANLANDI", "TALEP_EDILDI", "GELDI", "GELMEDI")
ZORUNLU_METIN = ("hedef_delil", "kaynak", "yontem", "dayanak")
DOLDUR = "DOLDUR"
# "Sair deliller" sınıfı muğlak ifade: doldurulmamış hücre sayılır (16-4 fikri;
# OA yöntemiyle): delili duruşmada aramak demektir. "Gerekirse/gerektiğinde"
# gibi KOŞUL ifadeleri bilerek listede YOK — meşru planda da geçer (alarm
# yorgunluğu da zarardır).
MUGLAK = re.compile(r"SAİR\s+DELİL|SAIR\s+DELIL|HER\s+TÜRLÜ|İLGİLİ\s+YER|BİLAHARE|SONRADAN\s+BİLDİRİLECEK|"
                    r"\bVB\.?$|\bVS\.?$|" + DOLDUR)
TANIK = re.compile(r"TANIK")
AVANS_GEREKTIRIR = re.compile(r"TANIK|BİLİRKİŞİ|KEŞİF|MÜZEKKERE|CELP|TESPİT")


def _tr_ust(s):
    return str(s or "").replace("i", "İ").replace("ı", "I").upper()


class GirdiHatasi(Exception):
    pass


def _json_oku(yol, ad):
    # kaynak koruması: plan/matris küçük dosyalardır; aşırı büyük girdi okunmaz
    try:
        if os.path.getsize(yol) > AZAMI_BAYT:
            raise GirdiHatasi(f"{ad} çok büyük (> {AZAMI_BAYT} bayt): {yol}")
    except OSError as e:
        raise GirdiHatasi(f"{ad} okunamadı: {yol}: {e}")
    try:
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise GirdiHatasi(f"{ad} okunamadı/bozuk JSON: {yol}: {e}")


def matris_oku(yol):
    m = _json_oku(yol, "matris")
    if not isinstance(m, dict) or m.get("arac") != "vakia_matris" \
            or not isinstance(m.get("iddia_delil_matrisi"), list):
        raise GirdiHatasi("matris şema dışı — vakia_matris.py --dogrula … --json <yol> çıktısı bekleniyor "
                          "(arac=vakia_matris, iddia_delil_matrisi)")
    iddialar = {}
    for s in m["iddia_delil_matrisi"]:
        if isinstance(s, dict) and s.get("iddia_id") is not None:
            iddialar[str(s["iddia_id"])] = s
    bosluklar = [str(x) for x in (m.get("ispat_bosluklari") or [])]
    return iddialar, bosluklar


def iskelet(iddialar, bosluklar):
    """Her ispat boşluğu için doldurulacak satır. Değerler bilerek 'DOLDUR':
    doldurulmamış iskelet denetimden GEÇMEZ (sessiz kabul yok)."""
    satirlar = []
    for iid in bosluklar:
        satirlar.append({"iddia_id": iid, "iddia_metni": (iddialar.get(iid) or {}).get("metin", ""),
                         "hedef_delil": DOLDUR, "kaynak": DOLDUR, "yontem": DOLDUR,
                         "kim": "|".join(KIM), "aciliyet": "|".join(ACILIYET),
                         "son_gun": "YYYY-MM-DD|BELIRLENEMEDI", "dayanak": DOLDUR + " (kanun+madde ya da TEYIDE MUHTAC)",
                         "durum": "PLANLANDI"})
    return {"arac": ARAC, "iskelet": True, "satirlar": satirlar}


def denetle(iddialar, bosluklar, plan):
    if not isinstance(plan, dict) or not isinstance(plan.get("satirlar"), list):
        raise GirdiHatasi("plan şema dışı — {\"satirlar\": [...]} bekleniyor (iskelet: --iskelet)")
    hatalar, uyarilar, kaybolan, hatirlatma = [], [], [], []
    kapsanan = set()
    avans_gerekli = tanik_var = False
    for n, s in enumerate(plan["satirlar"], 1):
        if not isinstance(s, dict):
            hatalar.append(f"satır {n}: nesne değil")
            continue
        iid = str(s.get("iddia_id", ""))
        etiket = f"satır {n} [{iid or '?'}]"
        if iid not in iddialar:
            hatalar.append(f"{etiket}: BİLİNMEYEN İDDİA — matriste '{iid}' yok")
        else:
            kapsanan.add(iid)
        kim, aciliyet, durum = s.get("kim"), s.get("aciliyet"), s.get("durum")
        for alan, deger, kume in (("kim", kim, KIM), ("aciliyet", aciliyet, ACILIYET), ("durum", durum, DURUM)):
            if deger not in kume:
                hatalar.append(f"{etiket}: GEÇERSİZ {alan}='{deger}' (geçerli: {', '.join(kume)})")
        karsi = kim == "KARSI_TARAF"
        for alan in ZORUNLU_METIN:
            v = str(s.get(alan) or "").strip()
            if karsi and alan in ("kaynak", "yontem") and not v:
                continue
            if not v:
                hatalar.append(f"{etiket}: BOŞ {alan}")
            elif MUGLAK.search(_tr_ust(v)):
                hatalar.append(f"{etiket}: MUĞLAK {alan} «{v[:80]}» — 'sair deliller' sınıfı ifade doldurulmamış "
                               "hücre sayılır; somut delil, kaynak ve yöntem yazın")
        sg = str(s.get("son_gun") or "").strip()
        if sg == "BELIRLENEMEDI":
            uyarilar.append(f"{etiket}: son gün BELİRLENEMEDİ — süre kalemi oa-sure'ye (hesapla_sure.py) satır "
                            "olarak açılmalı; tahminle gün yazılmaz")
        else:
            try:
                _dt.date.fromisoformat(sg)
            except ValueError:
                hatalar.append(f"{etiket}: GEÇERSİZ son_gun='{sg}' (YYYY-MM-DD ya da BELIRLENEMEDI)")
        if aciliyet == "KAYBOLUYOR":
            kaybolan.append(f"{etiket}: {s.get('hedef_delil', '')} — kaynak: {s.get('kaynak', '')}")
        if karsi:
            uyarilar.append(f"{etiket}: ispat yükü KARŞI TARAFTA işaretli — tedarik planlanmaz (HMK m.190/1); "
                            "gereksiz delil sunmak karşı tarafa veri verir, avukat teyit etsin")
        if durum == "GELMEDI":
            uyarilar.append(f"{etiket}: delil GELMEDİ — tekit/mahkemeye bildirim; süresinden sonra delil "
                            "gösterme izne bağlıdır (HMK m.145)")
        metin = _tr_ust(" ".join(str(s.get(a) or "") for a in ("hedef_delil", "yontem", "kaynak")))
        if TANIK.search(metin):
            tanik_var = True
            if (iddialar.get(iid) or {}).get("tanik_caizlik_belirsiz"):
                uyarilar.append(f"{etiket}: tanık planlanmış ama matriste tanık caizliği BELİRSİZ — önce senetle "
                                "ispat denetimi (HMK m.200-203; oa-vakia İSPAT ONTOLOJİSİ)")
            if (iddialar.get(iid) or {}).get("tur") == "hukuki":
                uyarilar.append(f"{etiket}: hukuki iddiaya tanık planlanmış — hukuki nitelendirme delille "
                                "ispatlanmaz (oa-vakia İSPAT ONTOLOJİSİ)")
        if kim == "MAHKEME" or AVANS_GEREKTIRIR.search(metin):
            avans_gerekli = True
    tedariksiz = [b for b in bosluklar if b not in kapsanan]
    for b in tedariksiz:
        hatalar.append(f"TEDARİKSİZ BOŞLUK [{b}] «{(iddialar.get(b) or {}).get('metin', '')[:80]}» — ispat boşluğu "
                       "bir tedarik satırına bağlanmadan kapanmaz")
    if kaybolan:
        hatirlatma.append("KAYBOLABİLİR DELİL: aynı gün aksiyon; delilin hemen tespit edilmemesi hâlinde "
                          "kaybolacağı ya da ileri sürülmesinin önemli ölçüde zorlaşacağı ihtimalinde delil "
                          "tespiti için hukuki yarar var sayılır (HMK m.400/2) — talep avukatın kararı.")
    if avans_gerekli:
        hatirlatma.append("AVANS: delil ikamesi için mahkemenin belirlediği avans verilen KESİN sürede yatırılır; "
                          "taraf yatırmaz ve diğer taraf da yatırmazsa delilden vazgeçilmiş sayılır (HMK m.324) — "
                          "süre oa-sure'ye işlenir.")
    if tanik_var:
        hatirlatma.append("TANIK LİSTESİ: dinletilmek istenen vakıa + tanığın adı soyadı + tebliğe elverişli adresi "
                          "listede gösterilir; listede olmayan dinlenemez, ikinci liste verilemez (HMK m.240/2) — "
                          "soru planı için tanik_plani.py.")
    return {"arac": ARAC, "satir": len(plan["satirlar"]), "ispat_boslugu": len(bosluklar),
            "tedariksiz": tedariksiz, "kaybolan": kaybolan, "hatalar": hatalar, "uyarilar": uyarilar,
            "hatirlatmalar": hatirlatma, "plan_tam": not hatalar}


def rapor(r):
    L = ["DELİL TEDARİK PLANI DENETİMİ — mekanik (oa-vakia · delil_plani.py; ispat kuralını model koyar)"]
    if r["kaybolan"]:
        L.append("")
        L.append("--- 🔴 KAYBOLABİLİR DELİL — AYNI GÜN AKSİYON ---")
        L.extend(f"  🔴 {k}" for k in r["kaybolan"])
    if r["hatalar"]:
        L.append("")
        L.append("--- HATALAR (plan kapanmaz) ---")
        L.extend(f"  ✗ {h}" for h in r["hatalar"])
    if r["uyarilar"]:
        L.append("")
        L.append("--- UYARILAR ---")
        L.extend(f"  ! {u}" for u in r["uyarilar"])
    if r["hatirlatmalar"]:
        L.append("")
        L.append("--- HATIRLATMALAR (kanun metni — Mevzuat MCP teyit 2026-10-05) ---")
        L.extend(f"  → {h}" for h in r["hatirlatmalar"])
    L.append("")
    L.append(f"Plan: {r['satir']} satır · ispat boşluğu: {r['ispat_boslugu']} · tedariksiz: {len(r['tedariksiz'])} · "
             f"🔴 kaybolan: {len(r['kaybolan'])}")
    L.append(">>> PLAN " + ("TAM <<<" if r["plan_tam"] else "EKSİK — yukarıdaki hatalar kapatılmalı <<<"))
    return "\n".join(L)


def main(argv=None):
    p = argparse.ArgumentParser(description="Delil tedarik planı denetimi (ispat boşluğu → tedarik satırı; "
                                            "çıkış 0 tam / 1 eksik / 2 girdi hatası; dosya yazmaz)")
    p.add_argument("--matris", required=True, help="vakia_matris --json çıktısı")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--plan", help="delil tedarik planı JSON")
    g.add_argument("--iskelet", action="store_true", help="boşluklar için doldurulacak plan iskeletini bas")
    p.add_argument("--json", action="store_true", help="denetim sonucunu JSON olarak stdout'a bas")
    a = p.parse_args(argv)
    try:
        iddialar, bosluklar = matris_oku(a.matris)
        if a.iskelet:
            print(json.dumps(iskelet(iddialar, bosluklar), ensure_ascii=False, indent=2))
            return 0
        r = denetle(iddialar, bosluklar, _json_oku(a.plan, "plan"))
    except GirdiHatasi as e:
        print(f"GİRDİ HATASI: {e}")
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=2) if a.json else rapor(r))
    return 0 if r["plan_tam"] else 1


if __name__ == "__main__":
    sys.exit(main())

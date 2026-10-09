#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
tanik_plani.py — TANIK SORU PLANI DENETİMİ (oa-vakia · v0.5.18 adayı).

NEDEN VAR: tanık duruşmada kazanılır ya da kaybedilir; vakıaya bağlanmamış
"genel" sorular hem süre harcar hem karşı tarafa yol gösterir. İkinci ve daha
ağır risk: yapay zekâ "tanık ne diyecek" metnini yazarsa bu, görülmekte olan
davada tanığı hukuka aykırı etkilemeye teşebbüs (TCK m.277) ve yalan tanıklık
(TCK m.272) riskini doğrudan büroya taşır. Bu script soru planını MEKANİK
olarak denetler: her soru matristeki bir vakıaya bağlı mı, plan tanığın
CEVABINI içeriyor mu, tanık listede mi, vakıa tanıkla ispata elverişli mi.
Fikir kaynağı: Yargı PRO 16-3 (tanık soruları) — kod/metin ALINMADI.

Girdi:
  --matris : vakia_matris.py --dogrula … --json <yol> çıktısı (iddia kimlikleri)
  --plan   : soru planı JSON'u:
     {"rejim": "hmk|cmk",
      "taniklar": [{"tanik": "T1 (rol — kurgu ad)", "yan": "biz|karsi",
                    "listede": "evet|hayir|bilinmiyor",
                    "dinleme": "durusma|istinabe|segbis|kesif",   (isteğe bağlı)
                    "sorular": [{"soru": "…", "vakia_id": "I1",
                                 "ispat_yonu": "ispat|curutme|guvenilirlik",
                                 "risk": "dusuk|orta|yuksek"}]}]}

KESİN YASAKLAR (çıkış 1):
  * VAKIASIZ SORU — vakia_id yok ya da matriste bulunmuyor.
  * TANIK CEVABI — planda cevap/beklenen cevap/ifade taslağı alanı ya da
    "şöyle söyleyin" türü yönlendirme. Soru üretilir, CEVAP ÜRETİLMEZ.
  * Şema/enum hatası.
Ne yapmaz: soruyu yazmaz (model yazar), tanıkla görüşmez, süre hesaplamaz,
dosya yazmaz (JSON stdout'a).

Dayanaklar (Yargı PRO MCP mevzuat_getir, teyit 2026-10-05): HMK m.152 (vekil
tanığa doğrudan soru yöneltebilir; taraf hâkim aracılığıyla), m.240/2 (tanık
listesi; listede olmayan dinlenemez, ikinci liste verilemez), m.243/1 (hazır
bulundurulan tanık), m.255 (tanıklığın doğruluğunda kuşku — iddia ve ispat),
m.259/4 (istinabede tanığın hangi hususlardan dinleneceğini hâkim belirler),
m.261/2 (tanık dinlenirken yazılı not kullanamaz); CMK m.201 (doğrudan soru
yöneltme); TCK m.272, m.277.

Çıkış: 0 PLAN GEÇERLİ (uyarı olabilir) · 1 PLAN GEÇERSİZ · 2 girdi okunamadı.

Kullanım:
  python tanik_plani.py --matris _oa/cikti/04-vakia-denetim.json --plan _oa/cikti/04-tanik-soru-plani.json [--json]
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
import os
import re
import sys

ARAC = "tanik_plani"
AZAMI_BAYT = 8 * 1024 * 1024
REJIM = ("hmk", "cmk")
YAN = ("biz", "karsi")
LISTEDE = ("evet", "hayir", "bilinmiyor")
DINLEME = ("durusma", "istinabe", "segbis", "kesif")
ISPAT_YONU = ("ispat", "curutme", "guvenilirlik")
RISK = ("dusuk", "orta", "yuksek")
# Tanığın cevabını/ifade metnini taşıyan alan adları — plan bunları TAŞIYAMAZ.
CEVAP_ALANLARI = {"cevap", "beklenen_cevap", "beklenen", "yanit", "yanıt", "beyan_metni", "ifade",
                  "ifade_taslagi", "ifade_taslağı", "senaryo", "soylenecek", "söylenecek"}
# Soru metninde tanığa ne söyleyeceğini dikte eden kalıplar (Türkçe büyük harf).
# Kelime sınırı bilinçli: "şöyle söylemiş miydi?" gibi geçmiş zamanlı MEŞRU soru
# yakalanmaz; yalnız emir/gelecek kipiyle tanığa ne diyeceğini söyleyen kalıp.
YONLENDIRME = re.compile(r"ŞÖYLE\s+(?:SÖYLE|DE|DEYİN|SÖYLEYİN|ANLAT|ANLATIN)\b|\b(?:SÖYLEYİN|DEYİN|"
                         r"SÖYLEYECEKSİN(?:İZ)?|DİYECEKSİN(?:İZ)?)\b|CEVABIN(?:IZ)?\s+.{0,40}OLMALI|"
                         r"DİYE\s+CEVAP\s+VER")


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
        raise GirdiHatasi("matris şema dışı — vakia_matris.py --dogrula … --json <yol> çıktısı bekleniyor")
    return {str(s["iddia_id"]): s for s in m["iddia_delil_matrisi"]
            if isinstance(s, dict) and s.get("iddia_id") is not None}


def _cevap_alani(d):
    return sorted(k for k in d if str(k).strip().lower() in CEVAP_ALANLARI)


def denetle(iddialar, plan):
    if not isinstance(plan, dict) or not isinstance(plan.get("taniklar"), list):
        raise GirdiHatasi("plan şema dışı — {\"rejim\": \"hmk|cmk\", \"taniklar\": [...]} bekleniyor")
    hatalar, uyarilar, bilgi = [], [], []
    rejim = plan.get("rejim")
    if rejim not in REJIM:
        hatalar.append(f"GEÇERSİZ rejim='{rejim}' (hmk|cmk) — tanık kuralları rejime göre değişir; HMK m.240/2 "
                       "tek liste kilidi ceza yargılamasına taşınmaz")
    soru_sayisi, kapsanan = 0, set()
    for t_no, t in enumerate(plan["taniklar"], 1):
        if not isinstance(t, dict):
            hatalar.append(f"tanık {t_no}: nesne değil")
            continue
        ad = str(t.get("tanik") or f"tanık {t_no}")
        for alan in _cevap_alani(t):
            hatalar.append(f"{ad}: TANIK CEVABI ÜRETİLEMEZ — '{alan}' alanı planda olamaz (TCK m.272, m.277)")
        for alan, deger, kume in (("yan", t.get("yan"), YAN), ("listede", t.get("listede"), LISTEDE)):
            if deger not in kume:
                hatalar.append(f"{ad}: GEÇERSİZ {alan}='{deger}' ({'|'.join(kume)})")
        dinleme = t.get("dinleme")
        if dinleme is not None and dinleme not in DINLEME:
            hatalar.append(f"{ad}: GEÇERSİZ dinleme='{dinleme}' ({'|'.join(DINLEME)})")
        if rejim == "hmk" and t.get("listede") == "hayir":
            uyarilar.append(f"{ad}: tanık listesinde YOK — listede gösterilmeyen kimse tanık olarak dinlenemez ve "
                            "ikinci liste verilemez (HMK m.240/2); hazır bulundurma istisnasını (HMK m.243/1) "
                            "avukat değerlendirir")
        if rejim == "hmk" and t.get("listede") == "bilinmiyor":
            uyarilar.append(f"{ad}: liste durumu bilinmiyor — HMK m.240/2 bakımından teyit edilmeli")
        # HMK'ya özgü notlar YALNIZ hmk rejiminde basılır: ceza yargılamasına HMK
        # atfı taşımak yanlış künye üretmektir (CMK karşılıkları burada teyitli değil).
        if dinleme == "istinabe" and rejim == "hmk":
            bilgi.append(f"{ad}: istinabe — tanığın hangi hususlardan dinleneceğini hâkim belirler (HMK m.259/4); "
                         "soru seti önceden ve eksiksiz verilmeli")
        sorular = t.get("sorular")
        if not isinstance(sorular, list) or not sorular:
            hatalar.append(f"{ad}: soru listesi boş")
            continue
        yonler = set()
        for s_no, s in enumerate(sorular, 1):
            etiket = f"{ad} / soru {s_no}"
            if not isinstance(s, dict):
                hatalar.append(f"{etiket}: nesne değil")
                continue
            soru_sayisi += 1
            for alan in _cevap_alani(s):
                hatalar.append(f"{etiket}: TANIK CEVABI ÜRETİLEMEZ — '{alan}' alanı (TCK m.272, m.277)")
            metin = str(s.get("soru") or "").strip()
            if not metin:
                hatalar.append(f"{etiket}: soru metni boş")
            elif YONLENDIRME.search(_tr_ust(metin)):
                hatalar.append(f"{etiket}: TANIĞA CEVAP DİKTE EDEN İFADE «{metin[:80]}» — soru üretilir, cevap "
                               "üretilmez (TCK m.277)")
            vid = str(s.get("vakia_id") or "").strip()
            if not vid:
                hatalar.append(f"{etiket}: VAKIASIZ SORU — vakia_id yok")
            elif vid not in iddialar:
                hatalar.append(f"{etiket}: VAKIASIZ SORU — matriste '{vid}' yok")
            else:
                kapsanan.add(vid)
                satir = iddialar[vid]
                if satir.get("tur") == "hukuki":
                    uyarilar.append(f"{etiket}: '{vid}' hukuki iddia — hukuki nitelendirme tanıkla ispatlanmaz "
                                    "(oa-vakia İSPAT ONTOLOJİSİ); soruyu bir vakıaya bağlayın")
                if satir.get("tanik_caizlik_belirsiz") and rejim == "hmk":
                    uyarilar.append(f"{etiket}: '{vid}' için tanık caizliği BELİRSİZ — önce senetle ispat denetimi "
                                    "(HMK m.200-203)")
            if s.get("ispat_yonu") not in ISPAT_YONU:
                hatalar.append(f"{etiket}: GEÇERSİZ ispat_yonu='{s.get('ispat_yonu')}' ({'|'.join(ISPAT_YONU)})")
            else:
                yonler.add(s["ispat_yonu"])
            if s.get("risk") not in RISK:
                hatalar.append(f"{etiket}: GEÇERSİZ risk='{s.get('risk')}' ({'|'.join(RISK)})")
        if t.get("yan") == "karsi" and "guvenilirlik" not in yonler and rejim == "hmk":
            bilgi.append(f"{ad}: karşı tanıkta güvenilirlik ekseni yok — tanıklığın doğruluğunda kuşku sebebi "
                         "(ör. davada yararı) iddia ve ispat edilebilir (HMK m.255)")
    if rejim == "hmk":
        bilgi.append("HMK: duruşmaya katılan vekil tanığa doğrudan soru yöneltebilir; taraf hâkim aracılığıyla sorar; "
                     "itiraz edilen sorunun yöneltilmesine hâkim karar verir (HMK m.152).")
    elif rejim == "cmk":
        bilgi.append("CMK: müdafi/vekil duruşmada tanığa doğrudan soru yöneltebilir; sanık ve katılan mahkeme "
                     "başkanı ya da hâkim aracılığıyla sorar (CMK m.201).")
    bilgi.append("Plan DAHİLİDİR: tanığa verilmez, tanıkla cevap provası yapılmaz"
                 + ("; tanık dinlenirken yazılı not kullanamaz (HMK m.261/2)" if rejim == "hmk" else "")
                 + "; görülmekte olan davada tanığı hukuka aykırı etkilemeye teşebbüs suçtur (TCK m.277).")
    return {"arac": ARAC, "rejim": rejim, "tanik": len(plan["taniklar"]), "soru": soru_sayisi,
            "kapsanan_vakialar": sorted(kapsanan), "hatalar": hatalar, "uyarilar": uyarilar, "bilgi": bilgi,
            "gecerli": not hatalar}


def rapor(r):
    L = ["TANIK SORU PLANI DENETİMİ — mekanik (oa-vakia · tanik_plani.py; soruyu model yazar, karar avukatın)"]
    if r["hatalar"]:
        L.append("")
        L.append("--- HATALAR (plan geçersiz) ---")
        L.extend(f"  ✗ {h}" for h in r["hatalar"])
    if r["uyarilar"]:
        L.append("")
        L.append("--- UYARILAR ---")
        L.extend(f"  ! {u}" for u in r["uyarilar"])
    L.append("")
    L.append("--- BİLGİ (kanun metni — Mevzuat MCP teyit 2026-10-05) ---")
    L.extend(f"  → {b}" for b in r["bilgi"])
    L.append("")
    L.append(f"Tanık: {r['tanik']} · soru: {r['soru']} · soruyla kapsanan vakıa: {', '.join(r['kapsanan_vakialar']) or '—'}")
    L.append(">>> SORU PLANI " + ("GEÇERLİ <<<" if r["gecerli"] else "GEÇERSİZ — hatalar kapatılmadan kullanılamaz <<<"))
    return "\n".join(L)


def main(argv=None):
    p = argparse.ArgumentParser(description="Tanık soru planı denetimi (vakıasız soru ve tanık cevabı YASAK; "
                                            "çıkış 0 geçerli / 1 geçersiz / 2 girdi hatası; dosya yazmaz)")
    p.add_argument("--matris", required=True, help="vakia_matris --json çıktısı")
    p.add_argument("--plan", required=True, help="tanık soru planı JSON")
    p.add_argument("--json", action="store_true", help="denetim sonucunu JSON olarak stdout'a bas")
    a = p.parse_args(argv)
    try:
        r = denetle(matris_oku(a.matris), _json_oku(a.plan, "plan"))
    except GirdiHatasi as e:
        print(f"GİRDİ HATASI: {e}")
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=2) if a.json else rapor(r))
    return 0 if r["gecerli"] else 1


if __name__ == "__main__":
    sys.exit(main())

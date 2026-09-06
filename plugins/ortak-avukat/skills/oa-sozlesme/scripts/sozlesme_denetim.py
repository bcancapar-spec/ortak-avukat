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
- kırmızı çizgiler tanımlı mı (İNCELEME modunda müzakere planının ön şartı),
- geçerlilik katmanı (ehliyet/temsil + genel işlem koşulları) açık kalmış mı,
- v0.5.16 (P2-6/A-23): her yazılmış kloz ÜÇ İFA SENARYOSUNDA (normal ifa /
  gecikme / fesih) sınanmış mı — `senaryo_testi` alanı; sınanmamış senaryo
  GÖRÜNÜR boşluk satırıdır, ASLA bloklamaz (exit sözleşmesi korunur).

Alanın DOLU/BOŞ/BİÇİM denetimi scriptin; NİTELENDİRME modelin işidir.
"Kloz gecikmede çalışır mı" sorusunun cevabı (calisir/calismaz) modelin ve
avukatın hukuki yargısıdır; script yalnız cevabın VERİLİP verilmediğine bakar.

Kullanım:
  python sozlesme_denetim.py --iskelet > _oa/cikti/sozlesme.json
  python sozlesme_denetim.py --dogrula _oa/cikti/sozlesme.json [--json cikti.json]

Çıkış kodu: 0 = kapsam boşluğu YOK · 1 = kapsam boşluğu VAR (teslim edilemez).
`--json` verilirse denetim sonucu (sorunlar/uyarılar/senaryo matrisi/
senaryo_bosluklari) makine-okur olarak yazılır — exit 1'de de yazılır.
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, json, re, sys

ZORUNLU_KATEGORILER = [
    "taraflar_temsil_imza_yetkisi", "konu_edimler", "bedel_odeme_ifa",
    "sure_uzama", "temerrut_cezai_sart_faiz", "fesih_tasfiye", "gizlilik",
    "kvkk_veri", "rekabet_yasagi_munhasirlik", "devir_temlik", "mucbir_sebep",
    "bildirim_tebligat", "uyusmazlik_cozumu", "delil_sozlesmesi",
    "butunluk_merger", "sekil_sarti",
]
# RİSK bantları oa-sozlesme'nin KENDİ eksenidir (B-31): oa-strateji'nin
# güçlü/dengeli/zayıf/belirsiz bantları OLASILIK bandıdır, risk bandı değil —
# ikisi ayrı eksendir ve birbirine atıfla tanımlanamaz.
# "yok" = değerlendirildi, kloz düzeyinde taşınan risk bulunmadı. İskelet
# varsayılanı da "yok" olduğundan, hiç doldurulmamış şablonu bu banda bakarak
# ayırt etmek MÜMKÜN DEĞİLDİR; o iş `_dokunulmamis_iskelet_mi` kapısınındır.
RISK_BANTLARI = {"kritik", "yuksek", "orta", "dusuk", "yok"}
DURUMLAR = {"VAR", "YOK-GEREKSIZ", "YOK-EKSIK"}

# `--iskelet` yer tutucuları — doldurulmamışlığın parmak izi (B-6).
ISKELET_MOD = "TAHRIR | INCELEME"
ISKELET_TIP = "ör. hizmet, NDA, bayilik..."

# Kabul edilen mod adları (B-8). SKILL.md gövdesi "İNCELEME / REDLINE" diye
# öğretiyor; her iki yazım da tanınır.
MOD_INCELEME_ADLARI = {"INCELEME", "REDLINE"}
MOD_TAHRIR_ADLARI = {"TAHRIR"}

# Şekil şartı beyanının MCP teyit izi: 'teyit/teyidi' + madde numarası (B-7).
_TEYIT_RE = re.compile(r"teyi[td]")
_MADDE_RE = re.compile(r"\bm\.?\s*\d+|\bmadde\s*\d+", re.IGNORECASE)

# B-32 — ehliyet ve genel işlem koşulları ZORUNLU_KATEGORILER'e anahtar olarak
# EKLENMEZ: yeni zorunlu anahtar sahadaki tüm mevcut sozlesme.json'ları exit 1
# ile düşürürdü. `sekil_sarti` emsali: döngüden SONRA, yalnız UYARI.
GECERLILIK_ALANLARI = ("ehliyet_temsil", "genel_islem_kosullari")
GECERLILIK_ADLARI = {
    "ehliyet_temsil": "ehliyet/temsil (TMK m.9, m.15 çıpası)",
    "genel_islem_kosullari": "genel işlem koşulları (TBK m.20-25 çıpası)",
}

# v0.5.16 (P2-6/A-23) — İFA SENARYO TESTİ. Sözleşme uyuşmazlık çıkana kadar
# test edilmez; bir kloz "var" olabilir ama gecikme ya da fesih anında hiç
# işlemeyebilir (ör. fesih bildirimi için kanal yazılmamışsa fesih klozu
# kâğıt üstünde kalır — TBK m.117: temerrüt ihtarla; m.125-126: seçimlik
# haklar/fesih — Mevzuat MCP teyit 2026-09-06). Alan OPSİYONELDİR: eski
# sozlesme.json'lar düşmez, yalnız görünür uyarı alır. Değer kümesi kapalıdır;
# tanınmayan değer sessizce 'calisir'e DÜŞMEZ, 'belirsiz' sayılır ve uyarılır.
SENARYOLAR = ("normal", "gecikme", "fesih")
SENARYO_SONUCLARI = {"calisir", "calismaz", "belirsiz"}
SENARYO_ADLARI = {"normal": "normal ifa", "gecikme": "gecikme", "fesih": "fesih"}
# Matris yalnız YAZILMIŞ kloz için anlamlıdır; yazılmamış kloz (YOK-*) '—'.
SENARYO_UYGULANIR_DURUMLAR = {"VAR"}

# Türkçe-duyarlı büyütme: 'İ'.upper() ASCII 'I'ya KATLANMAZ, 'ı' da öyle.
_TR_BUYUK = str.maketrans({
    "ı": "I", "İ": "I", "i": "I", "ş": "S", "Ş": "S", "ğ": "G", "Ğ": "G",
    "ü": "U", "Ü": "U", "ö": "O", "Ö": "O", "ç": "C", "Ç": "C",
})


def _tr_upper(s):
    return str(s or "").translate(_TR_BUYUK).upper()


def _metin(v):
    return str(v or "").strip()


def iskelet():
    d = {
        "mod": ISKELET_MOD,
        "tip": ISKELET_TIP,
        "kategoriler": {
            k: {"durum": "YOK-EKSIK", "risk": "yok",
                "not": "", "onlem": "",
                # v0.5.16 — varsayılan 'belirsiz': sınanmamışlık görünür
                # kalsın; 'calisir' varsayılanı sahte kesinlik olurdu.
                "senaryo_testi": {sn: "belirsiz" for sn in SENARYOLAR}}
            for k in ZORUNLU_KATEGORILER
        },
        "kirmizi_cizgiler": [],
        "acik_uclar": [],
        # Zorunlu DEĞİL, advisory: boş bırakılırsa tek satır uyarı doğurur.
        "gecerlilik_katmani": {a: "" for a in GECERLILIK_ALANLARI},
    }
    print(json.dumps(d, ensure_ascii=False, indent=2))


def _mod_coz(ham):
    """Ham `mod` değerini 'TAHRIR' / 'INCELEME' / None (tanınmayan) yapar.

    'TAHRIR | INCELEME' gibi iskelet yer tutucusu SEÇİM SAYILMAZ (None):
    mod belirsizken kırmızı çizgi kapısı yapısal olarak ölü kalır.
    """
    parcalar = set(re.findall(r"[A-Z]+", _tr_upper(ham)))
    if not parcalar:
        return None
    tahrir = bool(parcalar & MOD_TAHRIR_ADLARI)
    inceleme = bool(parcalar & MOD_INCELEME_ADLARI)
    if tahrir and inceleme:
        return None
    yabanci = parcalar - MOD_TAHRIR_ADLARI - MOD_INCELEME_ADLARI - {"MOD", "MODU"}
    if yabanci:
        return None
    if inceleme:
        return "INCELEME"
    if tahrir:
        return "TAHRIR"
    return None


def _dokunulmamis_iskelet_mi(d, kats):
    """B-6 — `--iskelet` çıktısının hiç doldurulmadan doğrulanması.

    Dar tutulur (yanlış pozitif yasağı): yer tutucu mod/tip DURUYOR **ve**
    16 kategorinin tamamı boş `YOK-EKSIK`. Tek kategori bile doldurulmuşsa
    bu kapı ateşlemez.
    """
    if not (_metin(d.get("mod")) == ISKELET_MOD
            or _metin(d.get("tip")) == ISKELET_TIP):
        return False
    for k in ZORUNLU_KATEGORILER:
        v = kats.get(k)
        if not isinstance(v, dict) or v.get("durum") != "YOK-EKSIK":
            return False
        if _metin(v.get("not")) or _metin(v.get("onlem")):
            return False
    return True


def _sekil_sarti_sorunu(kats):
    """B-7 — teyit izi şartı kategorinin TAMAMINA bağlıdır ve SORUNDUR.

    Eski kapı yalnız `durum == "VAR"` derken ve yalnız uyarı olarak teyit
    istiyordu; asıl pahalı cevap olan "YOK-GEREKSIZ" hiçbir kanıt yükü
    taşımadan geçiyordu. `YOK-EKSIK` muaftır (zaten eksiklik raporlanır).
    """
    v = kats.get("sekil_sarti")
    if not isinstance(v, dict):
        return None
    durum = v.get("durum")
    if durum not in ("VAR", "YOK-GEREKSIZ"):
        return None
    iz = _metin(v.get("not")) + " " + _metin(v.get("onlem"))
    duz = _tr_upper(iz).lower()
    if _TEYIT_RE.search(duz) and _MADDE_RE.search(duz):
        return None
    return (f"sekil_sarti: durum='{durum}' beyanı Mevzuat MCP teyit izi "
            f"taşımıyor (hangi madde + hangi sorgu) — ezber şekil şartı kabul "
            f"edilmez; en pahalı yanlış cevap 'gereksiz' demektir, şekil "
            f"ihlali tipe göre geçersizlik doğurur")


def _gecerlilik_katmani_uyarisi(d):
    """B-32 — tek satır advisory; alan adları DÖKÜLMEZ (gürültü disiplini)."""
    blok = d.get("gecerlilik_katmani")
    if isinstance(blok, dict):
        acik = [a for a in GECERLILIK_ALANLARI if not _metin(blok.get(a))]
    else:
        acik = list(GECERLILIK_ALANLARI)
    if not acik:
        return []
    return ["geçerlilik katmanı değerlendirilmemiş — açık eksen: "
            + " · ".join(GECERLILIK_ADLARI[a] for a in acik)
            + " (script yalnız alanın dolu olup olmadığına bakar; "
              "nitelendirme ve hukuki sonuç modelin/avukatın işidir)"]


def _senaryo_denetimi(kats):
    """v0.5.16 (P2-6/A-23) — kloz × 3 senaryo matrisi ve boşlukları.

    Döner: (matris, bosluklar, calismaz, uyarilar, alan_var_mi)
      matris   : {kloz: {senaryo: calisir|calismaz|belirsiz|"—"}}
      bosluklar: [{"kloz","senaryo","neden": alan_yok|belirsiz|gecersiz_deger}]
      calismaz : [{"kloz","senaryo"}]
      uyarilar : görünür satırlar (ASLA sorun değil — exit sözleşmesi korunur)
      alan_var_mi: en az bir klozda alan var mı (geriye uyum kapısı)

    Script nitelendirme YAPMAZ: 'calisir/calismaz' yargısı modelin/avukatın;
    script yalnız yargının verilip verilmediğine ve biçimine bakar.
    """
    matris, bosluklar, calismaz, uyarilar = {}, [], [], []
    alan_var_mi = False
    for k in ZORUNLU_KATEGORILER:
        v = kats.get(k)
        if not isinstance(v, dict) or v.get("durum") not in SENARYO_UYGULANIR_DURUMLAR:
            # Yazılmamış/atlanmış kloz senaryoda sınanamaz; eksiklik zaten
            # kapsam kapısında raporlanır (çift kırmızı yasağı).
            matris[k] = {sn: "—" for sn in SENARYOLAR}
            continue
        alan_var = "senaryo_testi" in v
        st = v.get("senaryo_testi")
        if alan_var:
            alan_var_mi = True
        if not isinstance(st, dict):
            # alan yok / bozuk tip → üç senaryo da sınanmamış; çökme YOK.
            matris[k] = {sn: "belirsiz" for sn in SENARYOLAR}
            neden = "belirsiz" if alan_var else "alan_yok"
            if alan_var and st is not None:
                uyarilar.append(f"kloz {k}: senaryo_testi alanı sözlük değil "
                                f"({type(st).__name__}) — üç senaryo belirsiz sayıldı")
            for sn in SENARYOLAR:
                bosluklar.append({"kloz": k, "senaryo": sn, "neden": neden})
            continue
        satir = {}
        for sn in SENARYOLAR:
            ham = st.get(sn)
            deger = _tr_upper(ham).lower()
            if sn not in st or not deger:
                satir[sn] = "belirsiz"
                bosluklar.append({"kloz": k, "senaryo": sn, "neden": "belirsiz"})
            elif deger not in SENARYO_SONUCLARI:
                satir[sn] = "belirsiz"
                uyarilar.append(f"kloz {k}: {sn} senaryosu değeri "
                                f"{ham!r} tanınmıyor "
                                f"({' / '.join(sorted(SENARYO_SONUCLARI))}) — belirsiz sayıldı")
                bosluklar.append({"kloz": k, "senaryo": sn, "neden": "gecersiz_deger"})
            else:
                satir[sn] = deger
                if deger == "belirsiz":
                    bosluklar.append({"kloz": k, "senaryo": sn, "neden": "belirsiz"})
                elif deger == "calismaz":
                    calismaz.append({"kloz": k, "senaryo": sn})
        matris[k] = satir
    return matris, bosluklar, calismaz, uyarilar, alan_var_mi


def _senaryo_matrisi_yazdir(matris, mod):
    """Kloz × senaryo tablosu. Okuma yönü moda bağlıdır:
    TAHRİR → 'calismaz' = kloz o senaryoda işlemez, YENİDEN YAZ;
    İNCELEME → 'calismaz' = kloz o senaryoda MÜVEKKİL ALEYHİNE TETİKLENİR
    (karşı vekilin tuzağı — redline gerekçesi)."""
    if mod == "INCELEME":
        etiket_calismaz = "RİSK"
        okuma = ("okuma: RİSK yönü — 'calismaz' = kloz o senaryoda müvekkil "
                 "aleyhine tetiklenir (redline gerekçesi)")
    elif mod == "TAHRIR":
        etiket_calismaz = "ÇALIŞMAZ"
        okuma = ("okuma: TAHRİR yönü — 'calismaz' = kloz o senaryoda işlemez, "
                 "yeniden yaz")
    else:
        etiket_calismaz = "ÇALIŞMAZ"
        okuma = "okuma: mod belirsiz — yön seçilmedi"
    etiket = {"calisir": "çalışır", "calismaz": etiket_calismaz,
              "belirsiz": "belirsiz", "—": "—"}
    print("İFA SENARYO MATRİSİ (kloz × normal ifa / gecikme / fesih; "
          "'—' = kloz yazılmamış, senaryo uygulanmaz):")
    print("  " + okuma)
    genis = max(len(k) for k in matris) if matris else 10
    print("  " + "kloz".ljust(genis) + " | " + " | ".join(
        SENARYO_ADLARI[sn].ljust(10) for sn in SENARYOLAR))
    for k, satir in matris.items():
        print("  " + k.ljust(genis) + " | " + " | ".join(
            etiket[satir[sn]].ljust(10) for sn in SENARYOLAR))


def dogrula(yol, json_yol=None):
    with open(yol, encoding="utf-8") as f:
        d = json.load(f)
    sorunlar, uyarilar, eksikler = [], [], []
    kats = d.get("kategoriler", {})

    if _dokunulmamis_iskelet_mi(d, kats):
        sorunlar.append("iskelet hiç doldurulmamış: mod/tip yer tutucu ve 16 "
                        "kategorinin tamamı boş 'YOK-EKSIK' — boş şablon "
                        "'temiz' sayılamaz, denetim hiç yapılmamıştır")

    for k in ZORUNLU_KATEGORILER:
        if k not in kats:
            sorunlar.append(f"kategori tamamen atlanmış: {k} (sessiz atlama)")
            continue
        v = kats[k]
        durum = v.get("durum")
        if durum not in DURUMLAR:
            sorunlar.append(f"{k}: geçersiz durum '{durum}' ({sorted(DURUMLAR)})")
            continue
        if durum == "YOK-GEREKSIZ" and len(_metin(v.get("not"))) < 10:
            sorunlar.append(f"{k}: YOK-GEREKSIZ gerekçesiz olamaz ('not' alanı)")
        if durum == "YOK-EKSIK":
            eksikler.append(k)
            uyarilar.append(f"{k}: EKSİK — ya kloz yaz(dır) ya gerekçeyle GEREKSIZ işaretle "
                            f"(karşı taslakta eksiklik çoğu kez KASITLIDIR)")
        risk = v.get("risk", "yok")
        if risk not in RISK_BANTLARI:
            sorunlar.append(f"{k}: geçersiz risk bandı '{risk}' (nitel bantlar: {sorted(RISK_BANTLARI)})")
        elif risk in ("kritik", "yuksek") and len(_metin(v.get("onlem"))) < 15:
            sorunlar.append(f"{k}: risk={risk} ama 'onlem' boş — yüksek risk önlemsiz "
                            f"(redline/alternatif kloz/fallback) bırakılamaz")

    sekil = _sekil_sarti_sorunu(kats)
    if sekil:
        sorunlar.append(sekil)

    mod = _mod_coz(d.get("mod"))
    if mod is None:
        sorunlar.append(f"tanınmayan mod: {d.get('mod')!r} — kabul edilen adlar: "
                        f"TAHRIR · İNCELEME · REDLINE. Mod seçilmeden kırmızı "
                        f"çizgi kapısı yapısal olarak ölüdür")
    elif mod == "INCELEME" and not d.get("kirmizi_cizgiler"):
        sorunlar.append("İNCELEME modunda kırmızı çizgi listesi boş — müzakere planı "
                        "kırmızı çizgi/pazarlık payı ayrımı olmadan kurulamaz (oa-strateji)")

    uyarilar.extend(_gecerlilik_katmani_uyarisi(d))

    # v0.5.16 (P2-6/A-23) — ifa senaryo testi. Kapsam kapısından SONRA ve
    # yalnız UYARI: senaryo boşluğu exit kodunu ASLA değiştirmez (saha
    # dosyaları toptan düşmez), ama TEMİZ damgasını da vermez.
    if isinstance(kats, dict):
        (matris, bosluklar, calismaz,
         sn_uyari, alan_var_mi) = _senaryo_denetimi(kats)
    else:
        matris, bosluklar, calismaz, sn_uyari, alan_var_mi = {}, [], [], [], False
    yazili = sum(1 for r in matris.values() if r.get("normal") != "—")
    if matris and not alan_var_mi and yazili:
        # Eski (v0.5.15) dosya: tek toplu satır — 48 satır dökülmez.
        uyarilar.append(f"ifa senaryo testi hiç yapılmamış — {yazili} kloz × "
                        f"{len(SENARYOLAR)} senaryo (normal ifa / gecikme / fesih) "
                        f"sınanmamış; `senaryo_testi` alanı yok (v0.5.16 alanı; "
                        f"`--iskelet` şablonuna bakın)")
    else:
        uyarilar.extend(sn_uyari)
        for b in bosluklar:
            uyarilar.append(f"kloz {b['kloz']}: {b['senaryo']} senaryosu sınanmamış")
    senaryo_okuma = {"TAHRIR": "tahrir", "INCELEME": "risk"}.get(mod, "belirsiz")

    if matris:
        _senaryo_matrisi_yazdir(matris, mod)
    if uyarilar:
        print("UYARILAR:")
        for u in uyarilar:
            print("  ⚠ " + u)

    exit_kodu = 1 if sorunlar else 0
    if sorunlar:
        print("KAPSAM BOŞLUĞU — bu denetim kapanmadan taslak/redline teslim edilemez:")
        for s in sorunlar:
            print("  ✗ " + s)
        hukum = "KAPSAM BOŞLUĞU"
    elif eksikler:
        # B-6 — en az bir EKSİK varken "TEMİZ" hükmü BASILMAZ. Exit kodu
        # (advisory) 0 kalır: eksiklik bilinçli raporlanmış olabilir, ama
        # "temiz" damgası hak edilmemiştir.
        print(f"KAPSAM DENETİMİ KAPANMADI — {len(eksikler)} kategori EKSİK "
              f"işaretli; boşluk raporu kapatılmadan taslak/redline teslim "
              f"edilemez (karşı taslakta eksiklik çoğu kez KASITLIDIR).")
        hukum = "KAPSAM DENETİMİ KAPANMADI"
    elif bosluklar or calismaz:
        # v0.5.16 — kapsam tam ama senaryo denetimi açık: TEMİZ basılmaz,
        # exit 0 kalır (advisory). 'calismaz' klozu da temiz sayılmaz —
        # tahrirde yeniden yazılacak, incelemede redline gerekçesidir.
        parcalar = []
        if bosluklar:
            parcalar.append(f"{len(bosluklar)} senaryo boşluğu")
        if calismaz:
            parcalar.append(f"{len(calismaz)} kloz 'calismaz'")
        print("SENARYO DENETİMİ AÇIK — " + " · ".join(parcalar) + "; kapsam tam "
              "ama üç senaryo (normal ifa / gecikme / fesih) kapatılmadan "
              "taslak/redline teslim edilemez (hukuki yargı modelin/avukatın; "
              "script yalnız cevabın verilip verilmediğine bakar).")
        hukum = "SENARYO DENETİMİ AÇIK"
    else:
        print("KAPSAM DENETİMİ TEMİZ. (Bu, klozların hukuken YETERLİ olduğunu değil, "
              "hiçbir kategorinin sessizce atlanmadığını ve her yazılmış klozun üç "
              "ifa senaryosunda sınandığını garanti eder — içerik yargısı "
              "modelin ve nihai karar avukatındır.)")
        hukum = "KAPSAM DENETİMİ TEMİZ"

    if json_yol:
        cikti = {
            "girdi": str(yol), "mod": mod, "exit": exit_kodu, "hukum": hukum,
            "sorunlar": sorunlar, "uyarilar": uyarilar, "eksikler": eksikler,
            "senaryo_okuma": senaryo_okuma, "senaryo_matrisi": matris,
            "senaryo_bosluklari": bosluklar, "senaryo_calismaz": calismaz,
        }
        with open(json_yol, "w", encoding="utf-8") as f:
            json.dump(cikti, f, ensure_ascii=False, indent=2)
        print(f"[JSON] Makine-okur sonuc yazildi: {json_yol}")
    if exit_kodu:
        sys.exit(exit_kodu)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iskelet", action="store_true")
    ap.add_argument("--dogrula", metavar="JSON")
    ap.add_argument("--json", dest="json_yol", metavar="YOL",
                    help="(--dogrula ile) denetim sonucunu makine-okur JSON "
                         "olarak bu yola yaz — senaryo_bosluklari dahil")
    a = ap.parse_args()
    if a.iskelet:
        iskelet()
    elif a.dogrula:
        dogrula(a.dogrula, json_yol=a.json_yol)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()

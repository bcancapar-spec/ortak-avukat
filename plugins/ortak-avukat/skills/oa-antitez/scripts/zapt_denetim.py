#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
zapt_denetim.py — CELSE KARTI ↔ DURUŞMA ZABTI KARŞILAŞTIRMASI (oa-antitez ·
v0.5.18 adayı).

NEDEN VAR: dosya tutanakta kazanılır. Ön inceleme, tahkikat ve yargılama
işlemleri ancak tutanakla ispat olunur (HMK m.156); tarafların soruşturmaya
ilişkin istekleri ve ara kararlar MUTLAK olarak tutanağa yazılır (HMK m.154/3-g,
ğ). Sözlü yapılıp zapta geçmeyen bir delil talebi ya da itiraz, istinafta
"ileri sürülmüş" sayılmayabilir. Celse kartı (oa-antitez Protokol 7) tutanağa
geçirilmesi şart kalemleri listeler; bu script her kalemi zabıtta ARAR ve
sonucu ADAY olarak işaretler (GEÇMİŞ GÖRÜNÜYOR / KISMEN / GEÇMEMİŞ GÖRÜNÜYOR).
Ayrıca ara karar kalemlerini, süre doğurabilecek ifadeleri ve RET kararlarında
gerekçe ibaresinin bulunup bulunmadığını gösterir.
Fikir kaynağı: Yargı PRO 16-2 (duruşma zaptı denetimi) — kod/metin ALINMADI.

SINIR (oa-antitez SKILL: "celse sonrası karşılaştırma model-denetimli bir
checklisttir, mekanik denetim değildir ve yalnız öneri üretir"): eşleştirme
kelime kökü düzeyindedir; hâkim tutanağa ÖZETLE geçirebilir (HMK m.154/1) —
"GEÇMEMİŞ GÖRÜNÜYOR" bir ihtimaldir, kesin hüküm değildir. Model ilgili zabıt
paragrafını OKUR; düzeltme talebi verilip verilmeyeceği AVUKATIN takdiridir.
Script SÜRE HESAPLAMAZ (süre doğuran ara karar → oa-sure) ve dosya YAZMAZ.

Tutanağın düzeltilmesi için HMK'da ayrı bir süre maddesi BULUNAMADI (m.154-158
okundu, Yargı PRO MCP 2026-10-05): düzeltme yolu ve zamanı TEYİT BEKLİYOR;
pratik ihtiyat olarak fark celseyi izleyen ilk iş günü avukata raporlanır (bu
bir kanuni süre değildir).

Girdi:
  --kart : celse kartı (.md: başlığında "TUTANAĞA" geçen bölümün madde işaretli
           listesi okunur) ya da .json: {"kalemler": [{"id": "K1", "tur":
           "talep|itiraz|beyan|ara_karar_talebi", "metin": "…", "anahtar":
           ["tanık", "dinlen"]}]}  — 'anahtar' verilirse eşleşme bu köklerle yapılır.
  --zapt : duruşma zabtının metni (.md/.txt — tercihen oa-ingest çıktısı).

Çıkış: 0 rapor üretildi (bulgular ADAYDIR) · 2 girdi okunamadı/ikili/şema dışı.

Kullanım:
  python zapt_denetim.py --kart _oa/cikti/NN-celse-karti.md --zapt _oa/metin/NNN-durusma-zapti.md [--json]
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
import unicodedata

ARAC = "zapt_denetim"
TURLER = ("talep", "itiraz", "beyan", "ara_karar_talebi")
IKILI_UZANTILAR = {".udf", ".docx", ".doc", ".pdf", ".zip", ".eyp", ".tif", ".tiff", ".jpg", ".jpeg", ".png"}
ESIK_GECTI, ESIK_KISMEN = 0.75, 0.4
AZAMI_BAYT = 8 * 1024 * 1024

SAYFA_AYRACI = re.compile(r"<!--\s*-{2,}\s*sayfa\s+\d+\s*-{2,}\s*-->", re.I)
# Eşleştirmede anlam taşımayan sık sözcükler (Türkçe büyük harf).
DURAK = {"İÇİN", "OLAN", "OLARAK", "GİBİ", "DAHA", "KADAR", "SONRA", "ÖNCE", "DAVACI", "DAVALI", "VEKİLİ",
         "VEKİL", "VEKİLİNİN", "MAHKEME", "MAHKEMEMİZ", "SAYIN", "EDİLMESİ", "EDİLMESİNE", "EDİLMESİNİ",
         "OLUNMASI", "OLUNMASINA", "YAPILMASI", "HUSUSU", "HUSUSUNUN", "TUTANAĞA", "TUTANAK", "GEÇİRİLMESİ",
         "GEÇİRİLMESİNİ", "BEYAN", "BEYANI", "BEYANININ", "TALEP", "TALEBİ", "TALEBİNİN", "KAYIT", "KAYDI",
         "BİZİM", "TARAFIMIZ", "TARAFIMIZDAN", "DOSYA", "DOSYAYA", "DURUŞMA", "DURUŞMADA", "CELSE", "ŞART"}
ARA_KARAR_BAS = re.compile(r"GEREĞİ\s+DÜŞÜNÜLDÜ|\bG\.\s?D\.?\s*:?|ARA\s+KARAR")
MADDE_NO = re.compile(r"(?:(?<=\s)|^)(\d{1,2})\s?[-)]\s?(?=\S)")
SURE_IFADE = re.compile(r"SÜRE|GÜN\s+İÇİNDE|HAFTA|AY\s+İÇİNDE|KESİN")
RET = re.compile(r"REDDİNE|REDDEDİLMESİNE")
RET_KONU = re.compile(r"TANIK|DELİL|BİLİRKİŞİ|KEŞİF|TALEB|TALEP|İSTİNABE|MÜZEKKERE")
# Gerekçe ibaresi: bağlaçlar + Türkçe "-DIĞINDAN/-DİĞİNDEN/-DUĞUNDAN/-DÜĞÜNDEN" (T'li biçimler dahil)
# gerekçe kipi (ör. "ispatı mümkün olmadığından", "gerekmediğinden", "görüldüğünden").
GEREKCE = re.compile(r"ZİRA|ÇÜNKÜ|NEDENİYLE|SEBEBİYLE|GEREKÇE|DOLAYISIYLA|[DT][IİUÜ]Ğ[IİUÜ]ND[AE]N\b")
UNSUR_IPUCU = (  # HMK m.154/3 — mutlak tutanağa yazılacakların İPUÇLARI (bilgi düzeyi)
    ("a) mahkemenin adı", re.compile(r"MAHKEMESİ|HAKİMLİĞİ|HÂKİMLİĞİ")),
    ("a) duruşma tarihi", re.compile(r"\b\d{1,2}[./]\d{1,2}[./]\d{4}\b")),
    ("b) hâkim", re.compile(r"HÂKİM|HAKİM|BAŞKAN|ÜYE")),
    ("b) zabıt kâtibi", re.compile(r"KÂTİP|KATİP|ZABIT")),
    ("c) aleni/gizli", re.compile(r"ALENİ|AÇIK\s+(?:YARGILAMA|DURUŞMA)|GİZLİ")),
)


def _tr_ust(s):
    return str(s or "").replace("i", "İ").replace("ı", "I").upper()


class GirdiHatasi(Exception):
    pass


def _metin_oku(yol, ad):
    if not os.path.isfile(yol):
        raise GirdiHatasi(f"{ad} dosyası yok: {yol}")
    if os.path.splitext(yol)[1].lower() in IKILI_UZANTILAR:
        raise GirdiHatasi(f"{ad} ikili evrak — önce oa-ingest ile metne çevirin: {yol}")
    if os.path.getsize(yol) > AZAMI_BAYT:    # kaynak koruması: tek zabıt/kart beklenir
        raise GirdiHatasi(f"{ad} çok büyük (> {AZAMI_BAYT} bayt): {yol}")
    with open(yol, "rb") as f:
        ham = f.read()
    if ham.startswith(b"PK\x03\x04") or ham.startswith(b"%PDF") or b"\x00" in ham[:4096]:
        raise GirdiHatasi(f"{ad} metin değil (ikili imza): {yol}")
    try:
        metin = ham.decode("utf-8-sig")
    except UnicodeDecodeError:
        metin = ham.decode("cp1254", errors="replace")
    return unicodedata.normalize("NFC", metin.replace("\r\n", "\n").replace("\r", "\n"))


def _ingest_basligi_at(metin):
    satirlar = metin.split("\n")
    if satirlar and satirlar[0].startswith("# "):
        for i, s in enumerate(satirlar[:120]):
            if i > 0 and s.strip() == "---":
                if any(b.startswith("- Kaynak evrak:") for b in satirlar[:i]):
                    return "\n".join(satirlar[i + 1:])
                break
    return metin


def _kokler(metin):
    """Kalem metninden eşleştirme kökleri: 4+ harfli, durak dışı sözcüklerin ilk 5
    (6+ harfte) ya da ilk 4 harfi. Türkçe ek/ses değişimi yüzünden kaba bir
    yaklaşımdır — sonuç ADAYDIR."""
    kokler = []
    for w in re.findall(r"[A-ZÇĞİÖŞÜÂÎÛ]+", _tr_ust(metin)):
        if len(w) < 4 or w in DURAK:
            continue
        k = w[:5] if len(w) >= 6 else w[:4]
        if k not in kokler:
            kokler.append(k)
    return kokler


def kart_oku(yol):
    if yol.lower().endswith(".json"):
        try:
            veri = json.loads(_metin_oku(yol, "kart"))
        except ValueError as e:
            raise GirdiHatasi(f"kart bozuk JSON: {e}")
        if not isinstance(veri, dict) or not isinstance(veri.get("kalemler"), list):
            raise GirdiHatasi("kart şema dışı — {\"kalemler\": [...]} bekleniyor")
        kalemler = []
        for n, k in enumerate(veri["kalemler"], 1):
            if not isinstance(k, dict) or not str(k.get("metin") or "").strip():
                raise GirdiHatasi(f"kart kalemi {n}: 'metin' yok")
            tur = k.get("tur") if k.get("tur") in TURLER else "beyan"
            anahtar = [str(x) for x in (k.get("anahtar") or []) if str(x).strip()]
            kalemler.append({"id": str(k.get("id") or f"K{n}"), "tur": tur, "metin": str(k["metin"]).strip(),
                             "anahtar": anahtar})
        return kalemler
    metin = _metin_oku(yol, "kart")
    kalemler, icinde = [], False
    for satir in metin.split("\n"):
        s = satir.strip()
        baslik = s.startswith("#") or (s.startswith("**") and s.endswith("**")) or s.endswith(":")
        if baslik and not re.match(r"^[-*•]\s|^\d+[.)]\s", s):
            icinde = "TUTANA" in _tr_ust(s)
            continue
        if icinde:
            m = re.match(r"^(?:[-*•]|\d+[.)])\s+(.+)$", s)
            if m:
                kalemler.append({"id": f"K{len(kalemler) + 1}", "tur": "beyan", "metin": m.group(1).strip(),
                                 "anahtar": []})
    if not kalemler:
        raise GirdiHatasi("kartta 'TUTANAĞA …' başlıklı madde işaretli liste bulunamadı (oa-antitez Protokol 7-c)")
    return kalemler


def zapt_paragraflari(metin):
    metin = SAYFA_AYRACI.sub("\n", _ingest_basligi_at(metin))
    metin = metin.replace("**", "").replace("__", "")
    paragraflar, tampon = [], []
    for satir in metin.split("\n"):
        if satir.strip():
            tampon.append(satir.strip())
        elif tampon:
            paragraflar.append(" ".join(tampon))
            tampon = []
    if tampon:
        paragraflar.append(" ".join(tampon))
    return paragraflar


def _paragraf_kelimeleri(p):
    return re.findall(r"[A-ZÇĞİÖŞÜÂÎÛ0-9]+", _tr_ust(p))


# Türkçe ünsüz yumuşaması (talep→talebi, ağaç→ağacı, kanat→kanadı, renk→rengi)
# YALNIZ kökün son harfinde denk sayılır. Daha geniş bir gevşetme bilerek
# yapılmaz: bu araçta en tehlikeli hata, zapta GEÇMEMİŞ bir talebi "geçmiş"
# göstermektir (avukat düzeltme istemez, istinaf sebebi kaybolabilir).
_YUMUSAMA = {"B": "P", "C": "Ç", "D": "T", "Ğ": "K", "G": "K"}


def _kok_eslesir(kelime, kok):
    if kelime.startswith(kok):
        return True
    if len(kelime) < len(kok) or kelime[:len(kok) - 1] != kok[:-1]:
        return False
    son_k, son_w = kok[-1], kelime[len(kok) - 1]
    return _YUMUSAMA.get(son_k, son_k) == _YUMUSAMA.get(son_w, son_w)


def kalem_ara(kalem, paragraflar):
    if kalem["anahtar"]:
        aranan = [_tr_ust(a).split() for a in kalem["anahtar"]]
    else:
        aranan = [[k] for k in _kokler(kalem["metin"])]
    if not aranan:
        return {"durum": "DENETLENEMEDİ", "skor": None, "paragraf": None, "alinti": "",
                "not": "kalem metninde aranabilir kök yok — 'anahtar' verin"}
    en_iyi = (-1.0, None)
    for i, p in enumerate(paragraflar):
        kelimeler = _paragraf_kelimeleri(p)
        bulunan = sum(1 for grup in aranan if all(any(_kok_eslesir(w, g) for w in kelimeler) for g in grup))
        skor = bulunan / len(aranan)
        if skor > en_iyi[0]:
            en_iyi = (skor, i)
    skor, i = en_iyi
    durum = ("GEÇMİŞ GÖRÜNÜYOR" if skor >= ESIK_GECTI else "KISMEN — özü değişmiş olabilir" if skor >= ESIK_KISMEN
             else "GEÇMEMİŞ GÖRÜNÜYOR")
    alinti = paragraflar[i][:220] if (i is not None and skor > 0) else ""
    return {"durum": durum, "skor": round(skor, 2), "paragraf": (i + 1) if skor > 0 else None, "alinti": alinti,
            "not": ""}


def ara_kararlar(paragraflar):
    """'Gereği düşünüldü' / 'G.D.' / 'ara karar' sonrasındaki numaralı kalemler."""
    tam = "\n".join(paragraflar)
    u = _tr_ust(tam)
    m = ARA_KARAR_BAS.search(u)
    if not m:
        return [], False
    bolge = tam[m.end():]
    bolge_u = _tr_ust(bolge)
    noktalar = list(MADDE_NO.finditer(bolge_u))
    kalemler = []
    for j, n in enumerate(noktalar):
        son = noktalar[j + 1].start() if j + 1 < len(noktalar) else len(bolge)
        parca = bolge[n.end():son].strip()
        pu = bolge_u[n.end():son]
        ret = bool(RET.search(pu))
        kalemler.append({"no": n.group(1), "metin": parca[:300],
                         "sure_dogurabilir": bool(SURE_IFADE.search(pu)),
                         "ret": ret, "ret_konusu_delil_talep": ret and bool(RET_KONU.search(pu)),
                         "gerekce_ibaresi": bool(GEREKCE.search(pu)) if ret else None})
    return kalemler, True


def denetle(kalemler, zapt_metni):
    paragraflar = zapt_paragraflari(zapt_metni)
    if not paragraflar:
        raise GirdiHatasi("zabıt boş — karşılaştırılacak metin yok (boş zabıt 'geçti' kanıtı değildir)")
    sonuc = []
    for k in kalemler:
        s = kalem_ara(k, paragraflar)
        s.update({"id": k["id"], "tur": k["tur"], "metin": k["metin"]})
        sonuc.append(s)
    ak, bolge_var = ara_kararlar(paragraflar)
    tam_u = _tr_ust("\n".join(paragraflar))
    eksik_ipucu = [ad for ad, d in UNSUR_IPUCU if not d.search(tam_u)]
    if not bolge_var:
        eksik_ipucu.append("ğ) ara kararlar ('Gereği düşünüldü' / 'G.D.' / 'ara karar' bölümü)")
    return {"arac": ARAC, "kalem": len(sonuc), "paragraf": len(paragraflar), "kalemler": sonuc,
            "ara_kararlar": ak, "unsur_ipucu_bulunamadi": eksik_ipucu,
            "ozet": {"gecmis_gorunuyor": sum(1 for s in sonuc if s["durum"] == "GEÇMİŞ GÖRÜNÜYOR"),
                     "kismen": sum(1 for s in sonuc if s["durum"].startswith("KISMEN")),
                     "gecmemis_gorunuyor": sum(1 for s in sonuc if s["durum"] == "GEÇMEMİŞ GÖRÜNÜYOR"),
                     "denetlenemedi": sum(1 for s in sonuc if s["durum"] == "DENETLENEMEDİ"),
                     "sure_dogurabilir_ara_karar": sum(1 for a in ak if a["sure_dogurabilir"]),
                     "gerekce_ibaresiz_ret": sum(1 for a in ak if a["ret_konusu_delil_talep"]
                                                  and not a["gerekce_ibaresi"])}}


def rapor(r):
    L = ["ZABIT DENETİMİ — celse kartı ↔ duruşma zabtı (oa-antitez · zapt_denetim.py; sonuçlar ADAYDIR,",
         "ilgili zabıt paragrafı okunur; düzeltme talebi avukatın takdiridir)"]
    L.append("")
    L.append("--- TUTANAĞA GEÇİRİLECEK KALEMLER ---")
    for s in r["kalemler"]:
        yer = f" · zabıt ¶{s['paragraf']} (skor {s['skor']})" if s["paragraf"] else ""
        isaret = "✓" if s["durum"] == "GEÇMİŞ GÖRÜNÜYOR" else ("~" if s["durum"].startswith("KISMEN") else "✗")
        L.append(f"  {isaret} [{s['id']}] {s['durum']}{yer}: {s['metin'][:120]}")
        if s["alinti"] and s["durum"] != "GEÇMİŞ GÖRÜNÜYOR":
            L.append(f"        en yakın: «{s['alinti']}»")
        if s["not"]:
            L.append(f"        ! {s['not']}")
    if r["ara_kararlar"]:
        L.append("")
        L.append("--- ARA KARARLAR (HMK m.154/3-ğ: mutlak olarak tutanağa yazılır) ---")
        for a in r["ara_kararlar"]:
            etiket = []
            if a["sure_dogurabilir"]:
                etiket.append("SÜRE DOĞURABİLİR → oa-sure (gün burada sayılmaz)")
            if a["ret_konusu_delil_talep"]:
                etiket.append("RET — gerekçe ibaresi " + ("VAR" if a["gerekce_ibaresi"] else "GÖRÜLMEDİ: reddin "
                              "gerekçesinin zapta geçtiğini kontrol edin (HMK m.156: tutanakla ispat)"))
            L.append(f"  {a['no']}- {a['metin'][:160]}" + (f"  [{' · '.join(etiket)}]" if etiket else ""))
    if r["unsur_ipucu_bulunamadi"]:
        L.append("")
        L.append("--- BİLGİ: HMK m.154/3 unsur ipucu bulunamadı (OCR/biçim kaynaklı olabilir; hata değildir) ---")
        L.extend(f"  · {u}" for u in r["unsur_ipucu_bulunamadi"])
    o = r["ozet"]
    L.append("")
    L.append(f"Kalem {r['kalem']}: geçmiş görünüyor {o['gecmis_gorunuyor']} · kısmen {o['kismen']} · geçmemiş "
             f"görünüyor {o['gecmemis_gorunuyor']} · denetlenemedi {o['denetlenemedi']} | süre doğurabilir ara karar "
             f"{o['sure_dogurabilir_ara_karar']} · gerekçe ibaresiz ret {o['gerekce_ibaresiz_ret']}")
    L.append("NOT: Tutanağın düzeltilmesi için HMK'da ayrı bir süre maddesi bulunamadı (m.154-158) — yol ve zaman "
             "TEYİT BEKLİYOR; fark celseyi izleyen ilk iş günü avukata raporlanır (pratik ihtiyat, kanuni süre değil).")
    return "\n".join(L)


def main(argv=None):
    p = argparse.ArgumentParser(description="Celse kartı kalemlerini duruşma zabtında arar (aday düzeyinde; "
                                            "çıkış 0 rapor / 2 girdi hatası; süre hesaplamaz; dosya yazmaz)")
    p.add_argument("--kart", required=True, help="celse kartı (.md ya da .json)")
    p.add_argument("--zapt", required=True, help="duruşma zabtı metni (.md/.txt)")
    p.add_argument("--json", action="store_true", help="sonucu JSON olarak stdout'a bas")
    a = p.parse_args(argv)
    try:
        r = denetle(kart_oku(a.kart), _metin_oku(a.zapt, "zabıt"))
    except GirdiHatasi as e:
        print(f"GİRDİ HATASI: {e}")
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=2) if a.json else rapor(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())

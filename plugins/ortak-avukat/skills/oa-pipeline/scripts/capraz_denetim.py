#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa-pipeline — capraz_denetim.py
ORTAK KİMLİK UZAYI çapraz-referans denetçisi (DETERMİNİSTİK).

Üç ayrı motorun (`_oa/cikti/` altındaki illiyet grafı + vakıa matrisi + kıyas)
çıktıları TEK bir kimlik uzayında tutarlı mı? Her motor kendi dosyasını denetler;
bu script motorlar ARASINDAKİ kopuk referansları yakalar:

  1. Bir delil vakıa matrisinde var ama illiyet grafında düğümü yok.
  2. Kıyasın küçük önermesindeki vakıa vakia.json'da yok.
  3. Bir olgu hiçbir evrak/belgeye bağlı değil (yetim olgu).
  4. Kıyasta anılan delil ne grafta ne vakıada tanınıyor.
  5. Graf kenarındaki dayanak_delil, karşılığı olan delil düğümüne bağlı değil.
  6. Kıyas vakıasının 'karsilar' alanı tanımsız bir norm unsuruna işaret ediyor.

Felsefe (Ortak Avukat anayasası): script HUKUKİ karar VERMEZ. Yalnızca üç dosyanın
birbirini tuttuğunu YAPISAL olarak denetler. Yorum ve nihai karar avukata aittir.

Dosyalardan biri henüz üretilmemişse çökmez; "henüz üretilmemiş" der ve o dosyaya
bağlı denetimleri atlar. Kopuk referans bulunursa exit 1.

Kullanım:
    python capraz_denetim.py                       # varsayılan _oa/cikti
    python capraz_denetim.py --cikti-dizin _oa/cikti
    python capraz_denetim.py --graf g.json --vakia v.json --kiyas k.json
    python capraz_denetim.py --json _oa/cikti/capraz-denetim.json
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
import sys

VARSAYILAN_CIKTI = os.path.join("_oa", "cikti")

# Dosya adı anahtarları (numaralı konvansiyon: 01-illiyet-graf / 04-vakia / 05-kiyas)
ANAHTAR = {
    "graf": ("illiyet-graf", "graf"),
    "vakia": ("vakia", "vakıa"),
    "kiyas": ("kiyas", "kıyas"),
}

# belgesiz kalması meşru olan (ispat yükünü kaydıran) ispat türleri
BELGESIZ_MESRU = {"karine", "ikrar", "yemin"}

_TR_LOWER = str.maketrans({
    "İ": "i", "I": "ı", "Ş": "ş", "Ğ": "ğ", "Ü": "ü", "Ö": "ö", "Ç": "ç",
})


def _norm(s):
    """Türkçe-duyarlı normalize: küçült, boşluk sıkıştır, tırnak/nokta kırp."""
    if s is None:
        return ""
    t = str(s).translate(_TR_LOWER).lower().strip()
    t = " ".join(t.split())
    return t.strip("\"'“”‘’.,;:()[]{}")


def _eslesir(token, kume):
    """token (norm) kümede eşit VEYA (len>=4) tek yönlü kapsama ile var mı."""
    if not token:
        return False
    if token in kume:
        return True
    if len(token) >= 4:
        for s in kume:
            if s and (token in s or s in token):
                return True
    return False


def _dosya_bul(cikti_dizin, override, anahtarlar):
    """override verilmişse onu; yoksa dizinde anahtar içeren ilk .json'u döndür."""
    if override:
        return override if os.path.isfile(override) else False  # False = verildi ama yok
    if not cikti_dizin or not os.path.isdir(cikti_dizin):
        return None
    for ad in sorted(os.listdir(cikti_dizin)):
        low = ad.lower()
        if low.endswith(".json") and any(a in low for a in anahtarlar):
            yol = os.path.join(cikti_dizin, ad)
            if os.path.isfile(yol):
                return yol
    return None


def _yukle(yol):
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------- #
#  Kimlik uzayı çıkarımı
# --------------------------------------------------------------------------- #
def graf_kimlik(g):
    delil_ad = set()          # tip=delil düğümlerinin id + ad (norm)
    kenar_delil_ref = set()   # kenar dayanak_delil token'ları (norm)
    tum_dugum_id = set()      # ham (norm) tüm düğüm id
    delil_dugum_id = set()    # ham (norm) tip=delil düğüm id
    askida = []               # (kenar_index, token) düğümü olmayan dayanak_delil
    for d in g.get("dugumler", []):
        did = d.get("id")
        tum_dugum_id.add(_norm(did))
        if d.get("tip") == "delil":
            delil_dugum_id.add(_norm(did))
            delil_ad.add(_norm(did))
            if d.get("ad"):
                delil_ad.add(_norm(d.get("ad")))
    for i, k in enumerate(g.get("kenarlar", [])):
        for t in (k.get("dayanak_delil") or []):
            kenar_delil_ref.add(_norm(t))
            if _norm(t) not in tum_dugum_id:
                askida.append((i, t))
    return {
        "delil_bilinen": delil_ad | kenar_delil_ref,  # grafın tanıdığı tüm delil
        "delil_dugum_id": delil_dugum_id,
        "tum_dugum_id": tum_dugum_id,
        "askida_dayanak_delil": askida,
    }


def vakia_kimlik(v):
    iddia_id = set()
    metin_havuz = set()   # olgu + iddia metinleri (norm) — kıyas vakıası buraya eşlenir
    belge_norm = set()    # dolu belge (norm)
    yetim_olgu = []       # (olgu, ispat_durumu, mesru_mu) belgesiz olaylar
    for it in v.get("iddialar", []):
        iddia_id.add(it.get("id"))
        metin_havuz.add(_norm(it.get("metin")))
    for o in v.get("olaylar", []):
        olgu = o.get("olgu", "")
        metin_havuz.add(_norm(olgu))
        belge = (o.get("belge") or "").strip()
        ispat = o.get("ispat_durumu", "")
        if belge:
            belge_norm.add(_norm(belge))
        else:
            yetim_olgu.append((olgu, ispat, ispat in BELGESIZ_MESRU))
    metin_havuz.discard("")
    return {
        "iddia_id": iddia_id,
        "metin_havuz": metin_havuz,
        "belge_norm": belge_norm,
        "yetim_olgu": yetim_olgu,
    }


def kiyas_kimlik(k):
    buyuk = k.get("buyuk_onerme", {})
    unsur_id = set()
    for u in buyuk.get("unsurlar", []):
        unsur_id.add(u.get("id") if isinstance(u, dict) else u)
    vakialar = []
    for v in k.get("kucuk_onerme", {}).get("vakialar", []):
        vakialar.append({
            "metin": v.get("metin", ""),
            "karsilar": v.get("karsilar", []) or [],
            "dayanak_delil": v.get("dayanak_delil", []) or [],
        })
    return {"unsur_id": unsur_id, "vakialar": vakialar}


# --------------------------------------------------------------------------- #
#  Çapraz denetimler  (her biri kopukluk listesine ekler)
# --------------------------------------------------------------------------- #
def caprazla(graf, vakia, kiyas):
    kopuk = []

    def ekle(tip, mesaj):
        kopuk.append({"tip": tip, "mesaj": mesaj})

    gk = graf_kimlik(graf) if graf is not None else None
    vk = vakia_kimlik(vakia) if vakia is not None else None
    kk = kiyas_kimlik(kiyas) if kiyas is not None else None

    # 1. DELİL: vakıada var, illiyet grafında düğümü yok
    if gk and vk:
        for belge in sorted(vk["belge_norm"]):
            if not _eslesir(belge, gk["delil_bilinen"]):
                ekle("DELIL_GRAFTA_YOK",
                     f"Vakıa delili '{belge}' illiyet grafında düğüm/dayanak olarak yok")

    # 2. KIYAS küçük önerme vakıası vakia.json'da yok
    if kk and vk:
        for v in kk["vakialar"]:
            if not _eslesir(_norm(v["metin"]), vk["metin_havuz"]):
                ekle("KIYAS_VAKIA_VAKIADA_YOK",
                     f"Kıyas vakıası '{v['metin']}' vakia.json'da (olgu/iddia) yok")

    # 3. YETİM OLGU: hiçbir evrak/belgeye bağlı değil
    if vk:
        for olgu, ispat, mesru in vk["yetim_olgu"]:
            if mesru:
                # karine/ikrar/yemin belgesiz olabilir — kopukluk saymıyoruz, not düşüyoruz
                continue
            ekle("OLGU_EVRAKSIZ",
                 f"Olgu '{olgu}' hiçbir evrak/belgeye bağlı değil (yetim; ispat={ispat or '?'})")

    # 4. KIYAS delili ne grafta ne vakıada tanınıyor
    if kk and (gk or vk):
        graf_delil = gk["delil_bilinen"] if gk else set()
        vakia_delil = vk["belge_norm"] if vk else set()
        for v in kk["vakialar"]:
            for t in v["dayanak_delil"]:
                tn = _norm(t)
                if not (_eslesir(tn, graf_delil) or _eslesir(tn, vakia_delil)):
                    ekle("KIYAS_DELIL_BILINMIYOR",
                         f"Kıyas delili '{t}' ne grafta ne vakıada tanınıyor")

    # 5. GRAF dayanak_delil askıda (delil düğümü yok)
    if gk:
        for i, t in gk["askida_dayanak_delil"]:
            ekle("GRAF_DELIL_DUGUMU_YOK",
                 f"Graf kenar #{i}: dayanak_delil '{t}' düğümü tanımsız")

    # 6. KIYAS karsilar askıda unsur
    if kk and kk["unsur_id"]:
        for v in kk["vakialar"]:
            for u in v["karsilar"]:
                if u not in kk["unsur_id"]:
                    ekle("KIYAS_UNSUR_YOK",
                         f"Kıyas vakıası '{v['metin']}' tanımsız unsur '{u}'a bağlanmış")

    kopuk.sort(key=lambda x: (x["tip"], x["mesaj"]))
    return kopuk


# --------------------------------------------------------------------------- #
def main():
    p = argparse.ArgumentParser(description="OA ortak kimlik uzayı çapraz-referans denetçisi")
    p.add_argument("--cikti-dizin", default=VARSAYILAN_CIKTI,
                   help=f"çıktı dizini (varsayılan: {VARSAYILAN_CIKTI})")
    p.add_argument("--graf", help="illiyet graf.json (dizin taramasını ezer)")
    p.add_argument("--vakia", help="vakia.json (dizin taramasını ezer)")
    p.add_argument("--kiyas", help="kiyas.json (dizin taramasını ezer)")
    p.add_argument("--json", dest="json_yol", metavar="YOL",
                   help="çapraz-denetim sonucunu makine-okur JSON olarak bu yola yaz")
    a = p.parse_args()

    cizgi = "=" * 60
    print(cizgi)
    print("OA-PIPELINE — ORTAK KİMLİK UZAYI ÇAPRAZ DENETİMİ")
    print(cizgi)

    dosyalar = {}
    durum = {}   # ad -> "yuklendi" | "yok" | "okunamadi"
    for ad, ov in (("graf", a.graf), ("vakia", a.vakia), ("kiyas", a.kiyas)):
        yol = _dosya_bul(a.cikti_dizin, ov, ANAHTAR[ad])
        if yol is None or yol is False:
            dosyalar[ad] = None
            durum[ad] = "yok"
            neden = "belirtilen yolda yok" if yol is False else "henüz üretilmemiş"
            print(f"  [-] {ad:6s}: {neden} — bu dosyaya bağlı denetimler atlanıyor")
            continue
        try:
            dosyalar[ad] = _yukle(yol)
            durum[ad] = "yuklendi"
            print(f"  [OK] {ad:6s}: {yol}")
        except Exception as e:
            dosyalar[ad] = None
            durum[ad] = "okunamadi"
            print(f"  [!] {ad:6s}: okunamadı ({e}) — atlanıyor")
    print()

    var = [ad for ad, s in durum.items() if s == "yuklendi"]
    if len(var) < 2:
        print("  Çapraz denetim için en az iki dosya gerekli. "
              f"Mevcut: {', '.join(var) if var else 'yok'}.")
        print(cizgi)
        if a.json_yol:
            _json_yaz(a.json_yol, durum, [])
        sys.exit(0)

    kopuk = caprazla(dosyalar["graf"], dosyalar["vakia"], dosyalar["kiyas"])

    if kopuk:
        print(f"### KOPUK REFERANSLAR ({len(kopuk)})")
        for k in kopuk:
            print(f"  [KOPUK] ({k['tip']}) {k['mesaj']}")
    else:
        print("### KOPUK REFERANS YOK")
        print("  Üç dosya ortak kimlik uzayında tutarlı (mevcut dosyalar arası).")
    print()

    print(cizgi)
    print("NOT: Bu rapor YAPISAL çapraz-tutarlılığı gösterir. Referansın hukuki "
          "yeterliliği ve nihai karar avukata aittir.")
    print(cizgi)

    if a.json_yol:
        _json_yaz(a.json_yol, durum, kopuk)
        print(f"[JSON] Makine-okur sonuc yazildi: {a.json_yol}")

    sys.exit(1 if kopuk else 0)


def _json_yaz(yol, durum, kopuk):
    sonuc = {
        "arac": "capraz_denetim",
        "dosya_durum": durum,
        "kopuk_referanslar": kopuk,
        "kopuk_sayisi": len(kopuk),
        "tutarli": not kopuk,
    }
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2, sort_keys=True)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        try:
            _sys.stderr.close()
        except Exception:
            pass

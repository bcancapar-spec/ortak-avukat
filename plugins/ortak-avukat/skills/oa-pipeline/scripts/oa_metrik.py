#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa_metrik.py — TOKEN / VERİMLİLİK TELEMETRİSİ (deterministik ölçer)

NEDEN (illiyet): "2026-07 token hedefi" bir İDDİA idi; ölçülmeden doğrulanamaz.
Aile üç yerde iz bırakıyor — külliyat künyesi (_oa/metin/00-kunye.json), tam tur
kaydı (_oa/analiz/dosya-analiz.json) ve pipeline defteri
(_oa/defter/pipeline-durum.json). Bu script o üç izi OKUR ve tasarrufu ÖLÇÜLEBİLİR
sayıya çevirir: ham okuma maliyeti, seçiciliğin geri kazandırdığı token, tam turun
DELTA modunda kurtardığı tekrar-analiz maliyeti ve defterin işletim eksiksizliği.

Bu motor YORUMLAMAZ, yalnız ÖLÇER. Hiçbir sayıyı uydurmaz: kaynak dosya yoksa ya da
okunamıyorsa ilgili metrik "yok" / "ölçülemedi" olarak damgalanır, ASLA sıfır veya
tahmini bir rakamla doldurulmaz. Kanıt yoksa metrik yoktur.

ÖLÇÜLEN METRİKLER:
  1) Külliyat   : toplam evrak, toplam karakter, tahmini token (ham okuma maliyeti).
  2) Seçicilik  : üretilen NNN-md sayısı vs defter/analiz kanıtında ATIFLI md sayısı
                  (okunanın alt sınırı) → okunmayan md'lerin ham token'ı (tasarruf üst
                  sınırı). Kanıtta hiç md atfı yoksa "ölçülemedi" (yokluk, kanıt değildir).
  3) Tam tur    : yapıldı mı, snapshot evrak, bekleyen delta (yeni+değişen). İmza,
                  tam_tur.py._evrak_imzalari ile BİREBİR AYNI mantıkla kurulur (künyede
                  `sha` varsa "sha:<hex>" gerçek içerik hash'i; yoksa geri-uyumlu
                  "karakter-yöntem"). Karşılaştırma da tam_tur._delta_hesapla gibi
                  yalnız AYNI şema içindeki kayıtlarda yapılır; şema (sha<->karakter-
                  yöntem) değişmiş kayıtlar sahte "değişen" SAYILMAZ, ayrı bir
                  "karşılaştırılamadı" damgasıyla raporlanır (yok sayılmaz, uydurulmaz).
                  Delta varsa: tam tur TEKRAR edilmez → tam analiz token'ı tasarruf edilir.
  4) Defter     : parçaların statü dağılımı (UYGULANDI / GEREKSIZ / BILGI-EKSIK /
                  YUKLENEMEDI / BEKLIYOR) — işletimin eksiksizlik telemetrisi.

ÇIKTI:
  _oa/defter/metrik.json  (makine-okur, deterministik)
  + insan-okur özet (stdout, ASCII işaretçi).

Kullanım:
  python oa_metrik.py --kok "<çalışma_klasörü>"      # varsayılan: bulunulan klasör
  python oa_metrik.py --kok "<klasör>" --cikti "<metrik.json yolu>"

Çıkış kodu: her zaman 0 (bu bir GEÇİT değil, ÖLÇERdir; boşluğu raporlar, engellemez).
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import datetime
import json
import os
import sys

KAR_PER_TOKEN = 3   # oa_ingest ile tutarlı kaba token tahmini (~3 karakter/token)
YOK = "yok"
OLCULEMEDI = "olculemedi"


# ---------------- yollar (tam_tur / pipeline_kayit ile hizalı) ----------------
def _oa_kok(kok):
    return os.path.join(kok, "_oa")


def _kunye_yolu(kok):
    return os.path.join(_oa_kok(kok), "metin", "00-kunye.json")


def _analiz_yolu(kok):
    return os.path.join(_oa_kok(kok), "analiz", "dosya-analiz.json")


def _defter_yolu(kok):
    return os.path.join(_oa_kok(kok), "defter", "pipeline-durum.json")


def _metrik_yolu(kok):
    return os.path.join(_oa_kok(kok), "defter", "metrik.json")


def _simdi():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def _oku_json(yol):
    """(veri, ham_metin, hata) — dosya yoksa/bozuksa çökmeden None döner."""
    if not os.path.exists(yol):
        return None, None, "dosya yok"
    try:
        with open(yol, encoding="utf-8") as f:
            ham = f.read()
    except Exception as e:
        return None, None, f"okunamadı ({e})"
    try:
        return json.loads(ham), ham, None
    except Exception as e:
        return None, ham, f"JSON bozuk ({e})"


def _token(karakter):
    try:
        return int(karakter) // KAR_PER_TOKEN
    except Exception:
        return 0


# ---------------- 1) Külliyat ----------------
def olc_kulliyat(kunye, hata):
    if kunye is None:
        return {"durum": YOK, "not": f"00-kunye.json {hata or 'okunamadı'}"}
    try:
        toplam_evrak = int(kunye.get("toplam_evrak") or 0)
        toplam_karakter = int(kunye.get("toplam_karakter") or 0)
        tahmini_token = kunye.get("tahmini_token")
        tahmini_token = int(tahmini_token) if tahmini_token is not None else _token(toplam_karakter)
        return {
            "durum": "olculdu",
            "toplam_evrak": toplam_evrak,
            "toplam_karakter": toplam_karakter,
            "tahmini_token": tahmini_token,
            "not": "ham okuma maliyeti: tüm evrak metnini bir kez okumanın kaba token'ı.",
        }
    except Exception as e:
        return {"durum": OLCULEMEDI, "not": f"künye alanları çözülemedi ({e})"}


# ---------------- 2) Seçicilik ----------------
def olc_secicilik(kunye, defter_ham, analiz_ham):
    if kunye is None:
        return {"durum": YOK, "not": "00-kunye.json yok — üretilen md sayısı bilinmiyor."}
    kayitlar = kunye.get("kayitlar")
    if not isinstance(kayitlar, list):
        return {"durum": OLCULEMEDI, "not": "künye 'kayitlar' listesi yok/bozuk."}

    # md -> karakter (aynı md adı tekrarsa toplanır; boş md = evrak metne dönüşmedi)
    md_karakter = {}
    for k in kayitlar:
        if not isinstance(k, dict):
            continue
        md = k.get("md")
        if not md:
            continue
        try:
            md_karakter[md] = md_karakter.get(md, 0) + int(k.get("karakter") or 0)
        except Exception:
            md_karakter.setdefault(md, 0)

    uretilen = len(md_karakter)
    toplam_md_karakter = sum(md_karakter.values())
    if uretilen == 0:
        return {"durum": OLCULEMEDI, "uretilen_md": 0,
                "not": "hiç NNN-md üretilmemiş (metne dönüşen evrak yok)."}

    # Kanıt = defter + analiz HAM metni (künye taranmaz → dairesel sayım olmaz).
    kanit_metin = (defter_ham or "") + "\n" + (analiz_ham or "")
    if not kanit_metin.strip():
        return {"durum": OLCULEMEDI, "uretilen_md": uretilen,
                "toplam_md_token": _token(toplam_md_karakter),
                "not": "defter/analiz kanıtı yok — kaç md okundu ölçülemez (UYDURMA yok)."}

    atifli = sorted(md for md in md_karakter if md in kanit_metin)
    if not atifli:
        return {"durum": OLCULEMEDI, "uretilen_md": uretilen,
                "toplam_md_token": _token(toplam_md_karakter),
                "not": ("kanıtta hiçbir md adı geçmiyor — okunan sayısı ölçülemez "
                        "(yokluk kanıt değildir; sıfır varsayılmaz).")}

    okunan = len(atifli)
    okunan_karakter = sum(md_karakter[m] for m in atifli)
    okunmayan_karakter = toplam_md_karakter - okunan_karakter
    return {
        "durum": "olculdu",
        "uretilen_md": uretilen,
        "okunan_md_tahmini": okunan,
        "okunan_kaynak": "defter+analiz kanıtında adı geçen md (alt sınır)",
        "secim_orani": round(okunan / uretilen, 3) if uretilen else None,
        "toplam_md_token": _token(toplam_md_karakter),
        "okunan_md_token": _token(okunan_karakter),
        "okunmayan_md_token_ust_sinir": _token(okunmayan_karakter),
        "not": ("okunan = kanıtta ATIFLI md (gerçek okunanın ALT sınırı); "
                "okunmayan token = seçiciliğin kazandırdığı tasarrufun ÜST sınırı."),
    }


# ---------------- 3) Tam tur + delta ----------------
def _imzalar(kunye):
    """kaynak -> içerik imzası. tam_tur.py._evrak_imzalari ile BİREBİR AYNI mantık:
    künyede `sha` varsa ondan kur ('sha:<hex>', gerçek içerik hash'i — v1.2+ oa_ingest);
    yoksa eski karakter+yöntem (geri uyum). Aynı künyede iki şema karışık olabilir;
    karşılaştırma yalnız AYNI şemalı çiftlerde yapılmalı — bkz. _sema()."""
    d = {}
    for k in (kunye.get("kayitlar", []) if kunye else []):
        if not isinstance(k, dict):
            continue
        kaynak = k.get("kaynak") or k.get("ad") or ""
        if k.get("sha"):
            d[kaynak] = "sha:" + k["sha"]
        else:
            d[kaynak] = f"{k.get('karakter', 0)}-{k.get('yontem', '')}"
    return d


def _sema(imza):
    """imza 'sha:...' ise 'sha', değilse 'kar' (karakter-yöntem) — tam_tur.py._delta_hesapla
    içindeki yerel _sema() ile AYNI ayrım. Şema farklıysa iki imza karşılaştırılamaz
    (künye v1.2 öncesi 'karakter-yöntem' -> sonrası 'sha' geçişi, her kaydı yanlışça
    "değişmiş" göstermesin diye)."""
    return "sha" if isinstance(imza, str) and imza.startswith("sha:") else "kar"


def olc_tam_tur(analiz, analiz_hata, kunye):
    if analiz is None:
        return {"durum": YOK, "not": f"dosya-analiz.json {analiz_hata or 'okunamadı'} — tam tur hiç yapılmamış olabilir."}
    durumu = analiz.get("tam_tur_durumu")
    snap = analiz.get("kunye_snapshot") or {}
    snapshot_evrak = snap.get("toplam_evrak")
    gelisme_sayisi = len(analiz.get("gelismeler") or [])

    if durumu != "TAMAM":
        return {"durum": "eksik", "tam_tur_durumu": durumu or YOK,
                "snapshot_evrak": snapshot_evrak, "gelisme_sayisi": gelisme_sayisi,
                "not": "tam tur --kaydet ile kapatılmamış; delta tabanı yok."}

    sonuc = {"durum": "yapildi", "tam_tur_durumu": "TAMAM",
             "snapshot_evrak": snapshot_evrak,
             "tam_tur_tarihi": analiz.get("tam_tur_tarihi"),
             "gelisme_sayisi": gelisme_sayisi}

    if kunye is None:
        sonuc["bekleyen_delta"] = OLCULEMEDI
        sonuc["not"] = "güncel künye yok → delta ölçülemez."
        return sonuc

    guncel = _imzalar(kunye)
    snap_imza = snap.get("imzalar") or {}
    ortak = [k for k in guncel if k in snap_imza]
    yeni = sorted(k for k in guncel if k not in snap_imza)
    # DEĞİŞEN yalnız AYNI şema içinde ölçülür (tam_tur._delta_hesapla ile birebir aynı
    # kural): eski (karakter-yöntem) snapshot'tan yeni (sha) künyeye geçiş, her evrakı
    # yanlışça "değişmiş" göstermesin (geri uyum; sahte bekleyen-delta üretilmez).
    degisen = sorted(k for k in ortak
                      if guncel[k] != snap_imza[k] and _sema(guncel[k]) == _sema(snap_imza[k]))
    karsilastirilamadi = sorted(k for k in ortak
                                 if guncel[k] != snap_imza[k] and _sema(guncel[k]) != _sema(snap_imza[k]))
    toplam = len(yeni) + len(degisen)
    sonuc["bekleyen_delta"] = {"yeni": len(yeni), "degisen": len(degisen), "toplam": toplam}
    if karsilastirilamadi:
        sonuc["karsilastirilamadi"] = {
            "sayi": len(karsilastirilamadi),
            "kaynaklar": karsilastirilamadi,
            "not": ("künye imza şeması (sha vs karakter-yöntem) snapshot alındığından beri "
                    "değişmiş; bu kayıtlarda içerik değişikliği GÜVENİLİR ölçülemez — "
                    "'değişen'e SAYILMAZ ama yokluk da varsayılmaz (sayı uydurulmaz)."),
        }
    if toplam > 0:
        sonuc["not"] = ("bekleyen delta var → tam tur TEKRAR edilmez; yalnız yeni/değişen "
                        "evrak işlenir. DELTA MODUNDA TAM TUR ANALİZ TOKEN'I TASARRUF EDİLDİ.")
    else:
        sonuc["not"] = ("delta yok → tam tur güncel; sonraki turlarda tam analiz "
                        "tekrarlanmaz (tam tur token'ı tasarruf edilir).")
        if karsilastirilamadi:
            sonuc["not"] += (" NOT: bazı kayıtlar şema farkı nedeniyle KARŞILAŞTIRILAMADI "
                             "(yukarı bkz.) — 'delta yok' yalnız aynı şemalı kayıtlar içindir.")
    return sonuc


# ---------------- 4) Defter ----------------
def olc_defter(defter, defter_hata):
    if defter is None:
        return {"durum": YOK, "not": f"pipeline-durum.json {defter_hata or 'okunamadı'} — defter yok."}
    statuler = ["UYGULANDI", "GEREKSIZ", "BILGI-EKSIK", "YUKLENEMEDI", "BEKLIYOR"]
    parca_say = {s: 0 for s in statuler}
    diger = 0
    toplam_parca = 0
    adimlar = defter.get("adimlar") or {}
    try:
        for _no, a in adimlar.items():
            for _p, p in (a.get("parcalar") or {}).items():
                toplam_parca += 1
                d = p.get("durum")
                if d in parca_say:
                    parca_say[d] += 1
                else:
                    diger += 1
    except Exception as e:
        return {"durum": OLCULEMEDI, "not": f"defter 'adimlar' çözülemedi ({e})"}

    katman_say = {s: 0 for s in statuler}
    for _k, p in (defter.get("katmanlar") or {}).items():
        d = p.get("durum") if isinstance(p, dict) else None
        if d in katman_say:
            katman_say[d] += 1
    return {
        "durum": "olculdu",
        "dosya": defter.get("dosya"),
        "toplam_parca": toplam_parca,
        "parca_statuleri": parca_say,
        "parca_diger_statu": diger,
        "katman_statuleri": katman_say,
        "not": "işletim eksiksizliği telemetrisi (içerik doğruluğu değil).",
    }


# ---------------- insan-okur özet (ASCII işaretçi) ----------------
def _s(v, birim=""):
    if v is None:
        return "-"
    if isinstance(v, int):
        return f"{v:,}{birim}"
    return f"{v}{birim}"


def ozet_yaz(metrik):
    o = []
    o.append("=" * 66)
    o.append("  ORTAK AVUKAT — TOKEN / VERİMLİLİK TELEMETRİSİ")
    o.append(f"  kok: {metrik['kok']}")
    o.append(f"  olcum: {metrik['olcum_zamani']}")
    o.append("=" * 66)

    k = metrik["kulliyat"]
    o.append("[1] KÜLLİYAT (ham okuma maliyeti)")
    if k["durum"] == "olculdu":
        o.append(f"    -> evrak        : {_s(k['toplam_evrak'])}")
        o.append(f"    -> karakter     : {_s(k['toplam_karakter'])}")
        o.append(f"    -> tahmini token: {_s(k['tahmini_token'])}  (~{KAR_PER_TOKEN} kar/token)")
    else:
        o.append(f"    -> {k['durum'].upper()}: {k.get('not','')}")

    s = metrik["secicilik"]
    o.append("[2] SEÇİCİLİK (üretilen vs okunan md)")
    if s["durum"] == "olculdu":
        o.append(f"    -> üretilen md  : {_s(s['uretilen_md'])}")
        o.append(f"    -> okunan (atıflı, alt sınır): {_s(s['okunan_md_tahmini'])}"
                 f"  (oran {s.get('secim_orani')})")
        o.append(f"    -> okunmayan md token (tasarruf ÜST sınırı): {_s(s['okunmayan_md_token_ust_sinir'])}")
    else:
        o.append(f"    -> {s['durum'].upper()}: {s.get('not','')}")
        if s.get("uretilen_md") is not None:
            o.append(f"       (üretilen md: {_s(s['uretilen_md'])})")

    t = metrik["tam_tur"]
    o.append("[3] TAM TUR (snapshot + delta)")
    if t["durum"] in ("yapildi", "eksik"):
        o.append(f"    -> durum        : {t.get('tam_tur_durumu')}")
        o.append(f"    -> snapshot evrak: {_s(t.get('snapshot_evrak'))}")
        bd = t.get("bekleyen_delta")
        if isinstance(bd, dict):
            o.append(f"    -> bekleyen delta: {bd['toplam']} (yeni {bd['yeni']}, değişen {bd['degisen']})")
        elif bd is not None:
            o.append(f"    -> bekleyen delta: {str(bd).upper()}")
        kk = t.get("karsilastirilamadi")
        if isinstance(kk, dict):
            o.append(f"    -> karsilastirilamadi: {kk['sayi']} (imza semasi degismis — bkz. metrik.json)")
        o.append(f"    -> not          : {t.get('not','')}")
    else:
        o.append(f"    -> {t['durum'].upper()}: {t.get('not','')}")

    d = metrik["defter"]
    o.append("[4] DEFTER (işletim eksiksizliği)")
    if d["durum"] == "olculdu":
        ps = d["parca_statuleri"]
        o.append(f"    -> toplam parça : {_s(d['toplam_parca'])}")
        o.append(f"    -> UYGULANDI {ps['UYGULANDI']} | GEREKSIZ {ps['GEREKSIZ']} | "
                 f"BILGI-EKSIK {ps['BILGI-EKSIK']} | YUKLENEMEDI {ps['YUKLENEMEDI']} | "
                 f"BEKLIYOR {ps['BEKLIYOR']}")
    else:
        o.append(f"    -> {d['durum'].upper()}: {d.get('not','')}")

    o.append("-" * 66)
    o.append(f"  metrik.json -> {metrik['cikti']}")
    o.append("  NOT: ölçer, yorumlamaz. 'yok/ölçülemedi' = kanıt yok; sayı UYDURULMADI.")
    o.append("=" * 66)
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser(
        description="oa_metrik.py — token/verimlilik telemetrisi (deterministik ölçer)")
    ap.add_argument("--kok", default=".", help="çalışma kökü (varsayılan: bulunulan klasör)")
    ap.add_argument("--cikti", help="metrik.json yolu (varsayılan: <kok>/_oa/defter/metrik.json)")
    a = ap.parse_args()

    kok = a.kok
    if not os.path.isdir(kok):
        sys.exit(f"HATA: klasör yok: {kok}")

    kunye, _kunye_ham, kunye_hata = _oku_json(_kunye_yolu(kok))
    analiz, _analiz_ham, analiz_hata = _oku_json(_analiz_yolu(kok))
    defter, defter_ham, defter_hata = _oku_json(_defter_yolu(kok))

    metrik = {
        "arac": "oa_metrik",
        "surum": "1.1",
        "olcum_zamani": _simdi(),
        "kok": os.path.abspath(kok),
        "kaynaklar": {
            "kunye": {"yol": os.path.relpath(_kunye_yolu(kok), kok),
                      "durum": "var" if kunye is not None else (kunye_hata or YOK)},
            "analiz": {"yol": os.path.relpath(_analiz_yolu(kok), kok),
                       "durum": "var" if analiz is not None else (analiz_hata or YOK)},
            "defter": {"yol": os.path.relpath(_defter_yolu(kok), kok),
                       "durum": "var" if defter is not None else (defter_hata or YOK)},
        },
        "kulliyat": olc_kulliyat(kunye, kunye_hata),
        "secicilik": olc_secicilik(kunye, defter_ham, _analiz_ham),
        "tam_tur": olc_tam_tur(analiz, analiz_hata, kunye),
        "defter": olc_defter(defter, defter_hata),
    }

    cikti = a.cikti or _metrik_yolu(kok)
    metrik["cikti"] = os.path.abspath(cikti)
    ust = os.path.dirname(cikti)
    if ust:
        os.makedirs(ust, exist_ok=True)
    try:
        with open(cikti, "w", encoding="utf-8") as f:
            json.dump(metrik, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"UYARI: metrik.json yazılamadı ({e}) — özet yine de basılıyor.", file=sys.stderr)

    print(ozet_yaz(metrik))
    return 0


if __name__ == "__main__":
    sys.exit(main())

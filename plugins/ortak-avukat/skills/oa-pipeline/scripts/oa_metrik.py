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
  5) ANALİZ TOKEN RAPORU (M1-4, Gate D): `_oa/defter/tam-yukleme.jsonl` (Gate B —
                  okuma_kapisi.py'nin TAM-YÜKLEME DEDUP DEFTERİ; her satır bir alt-
                  ajanın büyük bir evrağı TAM yüklediği olayı: kaynak+ajan+zaman) okunur;
                  her olayın `kaynak`ı 00-kunye.json'daki `karakter` alanıyla eşlenir ve
                  ajan bazında + toplamda tahmini token'a çevrilir. Bu, "hangi alt-ajan
                  ne kadar evrak-token okudu" sorusunun deterministik ÖLÇÜMÜdür (defter/
                  okuma-log'dan derlenir, tahmin/varsayım YOK). Eşik (varsayılan: külliyat
                  toplam tahmini token'ı — kunye yoksa sabit `ANALIZ_ESIK_VARSAYILAN`;
                  `--analiz-esik-token` ile elle de verilebilir) aşılırsa "SEÇİCİ OKU"
                  UYARISI basılır — bu bir ÖLÇÜM UYARISIDIR, engel/kapı değildir; derinlik
                  kısılmaz, yalnız haritadan seçici okumaya dikkat çekilir. Defter yoksa
                  (hiç tam-yükleme olayı) "yok" damgalanır (yokluk kanıt değildir, sıfır
                  UYDURULMAZ).

ÇIKTI:
  _oa/defter/metrik.json  (makine-okur, deterministik)
  + insan-okur özet (stdout, ASCII işaretçi).

Kullanım:
  python oa_metrik.py --kok "<çalışma_klasörü>"      # varsayılan: bulunulan klasör
  python oa_metrik.py --kok "<klasör>" --cikti "<metrik.json yolu>"
  python oa_metrik.py --kok "<klasör>" --analiz-esik-token 200000   # eşiği elle ver

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
import importlib.util
import json
import os
import sys

KAR_PER_TOKEN = 3   # oa_ingest ile tutarlı kaba token tahmini (~3 karakter/token)
YOK = "yok"
OLCULEMEDI = "olculemedi"
# Kunye okunamıyorsa (külliyat tahmini token'ı bilinmiyorsa) ANALİZ TOKEN RAPORU
# eşiği için kullanılan sabit varsayılan (--analiz-esik-token ile ezilebilir).
ANALIZ_ESIK_VARSAYILAN = 150_000


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


def _tam_yukleme_yolu(kok):
    # okuma_kapisi.py (Gate B) ile AYNI yol — TAM-YÜKLEME DEDUP DEFTERİ.
    return os.path.join(_oa_kok(kok), "defter", "tam-yukleme.jsonl")


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


# ---------------- 6) OVERRIDE SAYACI (P2-14, v0.5.5) ----------------
_PIPELINE_KAYIT_MOD = None


def _pipeline_kayit_modulu():
    """pipeline_kayit.py'yi (aynı dizin) İN-PROCESS import eder — sözleşme-dışı
    dizin bekçisi/makbuzsuz-dilekçe uyarısı TEK KAYNAKTAN okunur (ikiz-liste
    yasağı); bulunamaz/çökerse None (çağıran taraf bu alt-sayaçları 'olculemedi'
    sayar, ANA override_orani hesabını ETKİLEMEZ)."""
    global _PIPELINE_KAYIT_MOD
    if _PIPELINE_KAYIT_MOD is not None:
        return _PIPELINE_KAYIT_MOD
    betik = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline_kayit.py")
    if not os.path.isfile(betik):
        return None
    try:
        spec = importlib.util.spec_from_file_location("_oa_metrik_pipeline_kayit_inproc", betik)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return None
    _PIPELINE_KAYIT_MOD = mod
    return _PIPELINE_KAYIT_MOD


# ---------------- 7) REGRESYON SAYAÇLARI (P1-13, v0.5.5) ----------------
_OA_HAFIZA_MOD = None


def _oa_hafiza_modulu():
    """oa_hafiza.py'yi (aynı dizin) İN-PROCESS import eder — ARAMA_ARACLARI/
    GETIR_ARACLARI (araç sınıflandırması) TEK KAYNAKTAN okunur (ikiz-liste
    yasağı). Bulunamaz/çökerse None (çağıran taraf sınıflandırmayı 'diğer'e
    düşürür, çökmez)."""
    global _OA_HAFIZA_MOD
    if _OA_HAFIZA_MOD is not None:
        return _OA_HAFIZA_MOD
    betik = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oa_hafiza.py")
    if not os.path.isfile(betik):
        return None
    try:
        spec = importlib.util.spec_from_file_location("_oa_metrik_hafiza_inproc", betik)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return None
    _OA_HAFIZA_MOD = mod
    return _OA_HAFIZA_MOD


def olc_regresyon(kok, analiz_token_raporu, override_sayaci):
    """P1-13 (P2'den YÜKSELTİLDİ, sinav DÜZELTMESİ) — v0.5.5'in KENDİ
    geçerlilik/regresyon aracı: bir canlı koşunun 'regresyon kapandı' iddiası
    BEYANLA değil bu sayaçlarla doğrulanır. Salt ÖLÇER (aynı doktrin: kanıt
    yoksa 0/None, UYDURMA yok). Kapsar: (b) adım-artefakt varlık matrisi
    (04/05/06/07), (c) teyit kütüğü satırlarının araç-sınıfına göre dağılımı
    (ictihat-arama/ictihat-getir/mevzuat/diğer — oa_hafiza'dan TEK KAYNAK),
    (d) _oa/teyit/dokum/ dosya sayısı, (e) tam-yukleme.jsonl satır sayısı
    (analiz_token_raporu'ndan devralınır — iki kez ayrıştırılmaz)."""
    cikti_dizin = os.path.join(_oa_kok(kok), "cikti")
    import glob as _glob
    desen_map = {"04-vakia": "04-vakia*", "05-kiyas": "05-kiyas*",
                 "06-strateji": "06-strateji*", "07-antitez": "07-antitez*"}
    artefakt_matrisi = {}
    for ad, desen in desen_map.items():
        eslesen = _glob.glob(os.path.join(cikti_dizin, desen)) if os.path.isdir(cikti_dizin) else []
        artefakt_matrisi[ad] = bool(eslesen)

    # Muhakeme kaydı sayısı — P0-2 tek-komutunun bölüm-append ürettiği
    # *ictihat-muhakeme* dosyalarındaki '**KUNYE:**' bölüm başlığı sayısı
    # (her bölüm = bir muhakeme kaydı; parser'a bağlı KALMADAN ucuz sayım).
    muhakeme_kayit_sayisi = 0
    if os.path.isdir(cikti_dizin):
        for yol_m in _glob.glob(os.path.join(cikti_dizin, "*ictihat-muhakeme*")):
            try:
                with open(yol_m, encoding="utf-8", errors="replace") as f:
                    muhakeme_kayit_sayisi += f.read().count("**KUNYE:**")
            except OSError:
                pass

    hafiza = _oa_hafiza_modulu()
    arama_set = getattr(hafiza, "ARAMA_ARACLARI", set()) if hafiza is not None else set()
    getir_set = getattr(hafiza, "GETIR_ARACLARI", set()) if hafiza is not None else set()
    kutuk_yol = os.path.join(_oa_kok(kok), "teyit", "kunye-teyit.md")
    sinif_dagilim = {"ictihat-arama": 0, "ictihat-getir": 0, "mevzuat": 0, "diger": 0}
    if os.path.isfile(kutuk_yol):
        try:
            with open(kutuk_yol, encoding="utf-8", errors="replace") as f:
                for satir in f:
                    s = satir.strip()
                    if not s.startswith("|"):
                        continue
                    hucreler = [h.strip() for h in s.strip("|").split("|")]
                    if len(hucreler) < 2 or hucreler[0].lower() in ("zaman", "---"):
                        continue
                    arac = hucreler[1]
                    if not arac or arac.strip("-") == "" or arac == "Araç":
                        continue
                    if arac in arama_set:
                        sinif_dagilim["ictihat-arama"] += 1
                    elif arac in getir_set:
                        sinif_dagilim["ictihat-getir"] += 1
                    elif arac.lower().startswith("mevzuat"):
                        sinif_dagilim["mevzuat"] += 1
                    else:
                        sinif_dagilim["diger"] += 1
        except OSError:
            pass

    dokum_dizin = os.path.join(_oa_kok(kok), "teyit", "dokum")
    dokum_dosya_sayisi = 0
    if os.path.isdir(dokum_dizin):
        try:
            dokum_dosya_sayisi = sum(1 for e in os.scandir(dokum_dizin) if e.is_file())
        except OSError:
            pass

    tam_yukleme_satir_sayisi = 0
    if isinstance(analiz_token_raporu, dict) and analiz_token_raporu.get("durum") == "olculdu":
        tam_yukleme_satir_sayisi = analiz_token_raporu.get("olay_sayisi") or 0

    golge_dizin_sayisi = None
    if isinstance(override_sayaci, dict):
        gk = override_sayaci.get("gorunmez_kacis_sayaclari") or {}
        gd = gk.get("sozlesme_disi_dizin")
        golge_dizin_sayisi = gd if isinstance(gd, int) else None

    pk = _pipeline_kayit_modulu()
    kutuk_n, dilekce_n = None, None
    if pk is not None:
        try:
            kutuk_n, dilekce_n = pk._kutuk_dilekce_sayaci(kok)
        except Exception:
            pass

    return {
        "durum": "olculdu",
        "artefakt_matrisi": artefakt_matrisi,
        "muhakeme_kayit_sayisi": muhakeme_kayit_sayisi,
        "teyit_kutuk_arac_sinif_dagilimi": sinif_dagilim,
        "dokum_dosya_sayisi": dokum_dosya_sayisi,
        "tam_yukleme_satir_sayisi": tam_yukleme_satir_sayisi,
        "golge_dizin_sayisi": golge_dizin_sayisi,
        "kutuk_dilekce_sayaci": {"kutuk": kutuk_n, "dilekce": dilekce_n},
        "not": ("v0.5.5'in KENDİ regresyon/geçerlilik sayaçları — bir canlı koşunun "
                "'regresyon kapandı' iddiası bunlarla ÖLÇÜLÜR, beyanla değil "
                "(bkz. --baz-yaz/--baz için token/sayaç kıyas raporu)."),
    }


# ---------------- 7b) BAZ ÇİZGİSİ KIYASI (--baz-yaz / --baz) ----------------
_BAZ_ALANLAR = [
    ("kulliyat_tahmini_token",
     lambda m: (m.get("kulliyat") or {}).get("tahmini_token")
     if (m.get("kulliyat") or {}).get("durum") == "olculdu" else None),
    ("analiz_toplam_token",
     lambda m: (m.get("analiz_token_raporu") or {}).get("toplam_token")
     if (m.get("analiz_token_raporu") or {}).get("durum") == "olculdu" else None),
    ("muhakeme_kayit_sayisi",
     lambda m: (m.get("regresyon_sayaclari") or {}).get("muhakeme_kayit_sayisi")),
    ("dokum_dosya_sayisi",
     lambda m: (m.get("regresyon_sayaclari") or {}).get("dokum_dosya_sayisi")),
    ("tam_yukleme_satir_sayisi",
     lambda m: (m.get("regresyon_sayaclari") or {}).get("tam_yukleme_satir_sayisi")),
    ("golge_dizin_sayisi",
     lambda m: (m.get("regresyon_sayaclari") or {}).get("golge_dizin_sayisi")),
    ("override_orani",
     lambda m: (m.get("override_sayaci") or {}).get("override_orani")),
]
BAZ_ESIK_YUZDE = 30  # yalnız GÖZLEM eşiği — GEÇİT değil (Goodhart notu, P1-13)


def baz_kiyasla(guncel, baz):
    """(guncel, baz) iki `hesapla()` çıktısı (ya da `--baz-yaz` ile dondurulmuş
    aynı şekilli bir dosya) arasında EŞİKSİZ bir token/sayaç kıyas raporu
    üretir. Hiçbir alan zorunlu/engel DEĞİLDİR — yalnız GÖZLENİR; `BAZ_ESIK_
    YUZDE` aşan alan(lar) yalnız 'v0.5.6 gündemine girer' notuyla işaretlenir."""
    alanlar = {}
    esik_asan = []
    for ad, alici in _BAZ_ALANLAR:
        try:
            b = alici(baz) if isinstance(baz, dict) else None
        except Exception:
            b = None
        try:
            g = alici(guncel) if isinstance(guncel, dict) else None
        except Exception:
            g = None
        satir = {"baz": b, "guncel": g, "fark_yuzde": None}
        if isinstance(b, (int, float)) and isinstance(g, (int, float)) and b:
            fark = (g - b) / b
            satir["fark_yuzde"] = round(fark * 100, 1)
            if abs(fark) * 100 >= BAZ_ESIK_YUZDE:
                esik_asan.append(ad)
        alanlar[ad] = satir
    return {
        "alanlar": alanlar,
        "esik_asan_alanlar": esik_asan,
        "esik_yuzde": BAZ_ESIK_YUZDE,
        "not": ("EŞİKSİZ ölçüm — bu bir GEÇİT/ENGEL değildir, yalnız GÖZLENİR "
                f"(Goodhart notu). ±%{BAZ_ESIK_YUZDE}+ değişen alan(lar) v0.5.6 "
                "gündemine (backlog) girer notu düşülür, teslim engellenmez."),
    }


def olc_override(kok, defter, analiz):
    """P2-14 — --zorla/--serh/--serhle oranının model-bağımsız MEKANİK ölçümü.
    SALT ÖLÇER, ENGELLEMEZ (mevcut ADVISORY doktrini aynen). Bu oran BAŞARI
    ÖLÇÜTÜ DEĞİL, İNCELEME TETİKLEYİCİSİDİR (Goodhart notu — sinav DÜZELTME):
    hedef ilan edilirse görünür kaçış (şerh) görünmez kaçışa (ad değiştirme/
    hiç loglamama/gölge dizine yazma) iter; sağlık ölçüsü ikisinin BİRLİKTE
    okunmasıdır. Bu yüzden 'gorunmez_kacis_sayaclari' AYNI çıktıda taşınır."""
    if defter is None:
        return {"durum": YOK, "not": "defter yok — override ölçülemedi."}
    serhli_parca, toplam_uygulandi = 0, 0
    try:
        for _no, a in (defter.get("adimlar") or {}).items():
            for _p, p in (a.get("parcalar") or {}).items():
                if p.get("durum") == "UYGULANDI":
                    toplam_uygulandi += 1
                    if p.get("serh"):
                        serhli_parca += 1
    except Exception as e:
        return {"durum": OLCULEMEDI, "not": f"defter 'adimlar' çözülemedi ({e})"}

    serh_tarihcesi_n = len((analiz or {}).get("serh_tarihcesi") or [])

    serhli_kapanis = 0
    oturum_dizin = os.path.join(_oa_kok(kok), "oturum")
    if os.path.isdir(oturum_dizin):
        try:
            for ad in os.listdir(oturum_dizin):
                yol = os.path.join(oturum_dizin, ad)
                if os.path.isfile(yol):
                    with open(yol, encoding="utf-8", errors="replace") as f:
                        serhli_kapanis += f.read().count("ŞERH (--serhle):")
        except OSError:
            pass

    makbuz_red = 0
    makbuz_yol = os.path.join(_oa_kok(kok), "defter", "teslim-makbuz.json")
    if os.path.isfile(makbuz_yol):
        try:
            with open(makbuz_yol, encoding="utf-8") as f:
                m = json.load(f)
            if isinstance(m, dict) and m.get("exit_kodu") not in (0, None):
                makbuz_red = 1
        except Exception:
            pass

    oran = round(serhli_parca / toplam_uygulandi, 4) if toplam_uygulandi else None

    # Görünmez-kaçış sayaçları — pipeline_kayit'in TEK KAYNAKLI (ikiz-liste
    # yasağı) bekçi fonksiyonlarından okunur; modül yüklenemezse "olculemedi".
    golge_dizin_n, makbuzsuz_dilekce_n = OLCULEMEDI, OLCULEMEDI
    pk = _pipeline_kayit_modulu()
    if pk is not None:
        try:
            golge_dizin_n = len(pk._sozlesme_disi_dizinler(kok))
        except Exception:
            golge_dizin_n = OLCULEMEDI
        try:
            makbuzsuz_dilekce_n = 1 if pk._dilekce_sekilli_makbuzsuz_uyarisi(kok) else 0
        except Exception:
            makbuzsuz_dilekce_n = OLCULEMEDI

    return {
        "durum": "olculdu",
        "serhli_uygulandi_parca": serhli_parca,
        "toplam_uygulandi_parca": toplam_uygulandi,
        "override_orani": oran,
        "serh_tarihcesi_uzunluk": serh_tarihcesi_n,
        "serhli_kapanis_sayisi": serhli_kapanis,
        "teslim_makbuz_red_sayisi": makbuz_red,
        "gorunmez_kacis_sayaclari": {
            "sozlesme_disi_dizin": golge_dizin_n,
            "makbuzsuz_dilekce_adayi": makbuzsuz_dilekce_n,
        },
        "not": ("override_orani BAŞARI ÖLÇÜTÜ DEĞİL, İNCELEME TETİKLEYİCİSİDİR — "
                "şerh GÖRÜNÜR bir kaçıştır, sağlık ölçüsü bu oranla "
                "gorunmez_kacis_sayaclari'nın BİRLİKTE okunmasıdır (Goodhart notu)."),
    }


# ---------------- 5) ANALİZ TOKEN RAPORU (M1-4, Gate D) ----------------
def _tam_yukleme_oku(yol):
    """(olaylar, hata) — tam-yukleme.jsonl'i satır satır oku. Bozuk satır
    atlanır (dayanıklılık); dosya okunamazsa hata metni döner (uydurma yok)."""
    if not os.path.exists(yol):
        return [], None
    olaylar = []
    try:
        with open(yol, encoding="utf-8") as f:
            for satir in f:
                satir = satir.strip()
                if not satir:
                    continue
                try:
                    olaylar.append(json.loads(satir))
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        return [], f"okunamadı ({e})"
    return olaylar, None


def olc_analiz_token(kunye, kok, esik_override=None):
    """`_oa/defter/tam-yukleme.jsonl` (Gate B'nin TAM-YÜKLEME DEDUP DEFTERİ) her
    alt-ajanın (`ajan`) TAM yüklediği evrak (`kaynak`) olaylarını tutar. Bu
    fonksiyon her olayı 00-kunye.json'daki `karakter` alanıyla eşleyip ajan
    bazında + toplamda tahmini token'a çevirir — SADECE ÖLÇER, yargı vermez.
    Kaynak künyede bulunamazsa (elle girilmiş/silinmiş kayıt) o olay toplama
    KATILMAZ ama sessizce de yok sayılmaz (`kaynak_bulunamadi` sayaçlı)."""
    yol = _tam_yukleme_yolu(kok)
    if not os.path.exists(yol):
        return {"durum": YOK, "not": f"tam-yukleme.jsonl yok — hiç TAM yükleme olayı yok "
                                      f"({os.path.relpath(yol, kok)})."}
    olaylar, hata = _tam_yukleme_oku(yol)
    if hata:
        return {"durum": OLCULEMEDI, "not": f"tam-yukleme.jsonl {hata}"}
    if not olaylar:
        return {"durum": YOK, "not": "tam-yukleme.jsonl boş — hiç TAM yükleme olayı yok."}

    kaynak_karakter = {}
    if kunye:
        for k in kunye.get("kayitlar", []):
            if isinstance(k, dict) and k.get("kaynak"):
                try:
                    kaynak_karakter[k["kaynak"]] = int(k.get("karakter") or 0)
                except Exception:
                    pass

    ajan_toplam = {}
    toplam_karakter = 0
    bilinmeyen_olay = 0
    for o in olaylar:
        if not isinstance(o, dict):
            continue
        ajan = o.get("ajan") or "bilinmeyen"
        rec = ajan_toplam.setdefault(ajan, {"olay_sayisi": 0, "toplam_karakter": 0,
                                            "kaynak_bulunamadi": 0})
        rec["olay_sayisi"] += 1
        kar = kaynak_karakter.get(o.get("kaynak"))
        if kar is None:
            rec["kaynak_bulunamadi"] += 1
            bilinmeyen_olay += 1
            continue
        rec["toplam_karakter"] += kar
        toplam_karakter += kar

    ajanlar = []
    for ajan, rec in sorted(ajan_toplam.items(), key=lambda kv: -kv[1]["toplam_karakter"]):
        ajanlar.append({
            "ajan": ajan,
            "olay_sayisi": rec["olay_sayisi"],
            "toplam_karakter": rec["toplam_karakter"],
            "toplam_token": _token(rec["toplam_karakter"]),
            "kaynak_bulunamadi": rec["kaynak_bulunamadi"],
        })

    toplam_token = _token(toplam_karakter)
    kulliyat_token = None
    if kunye is not None:
        try:
            tt = kunye.get("tahmini_token")
            kulliyat_token = int(tt) if tt is not None else _token(int(kunye.get("toplam_karakter") or 0))
        except Exception:
            kulliyat_token = None

    if esik_override is not None:
        esik, esik_kaynak = esik_override, "elle (--analiz-esik-token)"
    elif kulliyat_token:
        esik, esik_kaynak = kulliyat_token, "kunye (kulliyat tahmini_token)"
    else:
        esik, esik_kaynak = ANALIZ_ESIK_VARSAYILAN, "sabit varsayilan (kunye yok)"

    esik_asimi = bool(esik) and toplam_token > esik
    sonuc = {
        "durum": "olculdu",
        "kaynak_dosya": os.path.relpath(yol, kok),
        "olay_sayisi": len(olaylar),
        "ajan_bazinda": ajanlar,
        "toplam_karakter": toplam_karakter,
        "toplam_token": toplam_token,
        "esik_token": esik,
        "esik_kaynak": esik_kaynak,
        "esik_asimi": esik_asimi,
    }
    if bilinmeyen_olay:
        sonuc["not_kaynak_bulunamadi"] = (f"{bilinmeyen_olay} olayda kaynak künyede bulunamadı "
                                          "(elle girilmiş/silinmiş olabilir) — bu olaylar token "
                                          "toplamına KATILMADI (uydurulmadı).")
    if esik_asimi:
        sonuc["uyari"] = ("SEÇİCİ OKU UYARISI: alt-ajanların TAM YÜKLEME token toplamı eşiği aştı "
                          f"({toplam_token:,} > {esik:,} token) — büyük evrak(lar) haritadan "
                          "(<evrak>.harita.json, Gate A) seçici okunmalı. Bu bir ÖLÇÜM UYARISIDIR; "
                          "derinlik kısılmaz, teslim engellenmez.")
    else:
        sonuc["not"] = "eşik aşılmadı."
    return sonuc


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

    r = metrik["analiz_token_raporu"]
    o.append("[5] ANALİZ TOKEN RAPORU (alt-ajan bazında TAM YÜKLEME — Gate D)")
    if r["durum"] == "olculdu":
        o.append(f"    -> olay sayısı   : {_s(r['olay_sayisi'])}")
        for a in r["ajan_bazinda"]:
            eksik = f" (kaynak bulunamadı: {a['kaynak_bulunamadi']})" if a["kaynak_bulunamadi"] else ""
            o.append(f"       - {a['ajan']:<20} {_s(a['toplam_token'])} token "
                     f"({_s(a['olay_sayisi'])} olay){eksik}")
        o.append(f"    -> TOPLAM token  : {_s(r['toplam_token'])}  "
                 f"(eşik {_s(r['esik_token'])}, kaynak: {r['esik_kaynak']})")
        if r.get("uyari"):
            o.append(f"    -> ⚠ {r['uyari']}")
        else:
            o.append(f"    -> {r.get('not','')}")
        if r.get("not_kaynak_bulunamadi"):
            o.append(f"    -> NOT: {r['not_kaynak_bulunamadi']}")
    else:
        o.append(f"    -> {r['durum'].upper()}: {r.get('not','')}")

    ov = metrik.get("override_sayaci") or {}
    o.append("[6] OVERRIDE SAYACI (--zorla/--serh/--serhle — İNCELEME TETİKLEYİCİSİ, HEDEF DEĞİL)")
    if ov.get("durum") == "olculdu":
        oran_str = f"%{ov['override_orani']*100:.1f}" if ov.get("override_orani") is not None else "-"
        o.append(f"    -> şerhli UYGULANDI: {_s(ov['serhli_uygulandi_parca'])} / "
                 f"{_s(ov['toplam_uygulandi_parca'])} (oran: {oran_str})")
        o.append(f"    -> serh_tarihcesi (tam_tur --zorla): {_s(ov['serh_tarihcesi_uzunluk'])}")
        o.append(f"    -> şerhli kapanış (oturum-kapat --serhle): {_s(ov['serhli_kapanis_sayisi'])}")
        o.append(f"    -> teslim-makbuz RED: {_s(ov['teslim_makbuz_red_sayisi'])}")
        gk = ov.get("gorunmez_kacis_sayaclari") or {}
        o.append(f"    -> GÖRÜNMEZ-KAÇIŞ: sözleşme-dışı dizin {_s(gk.get('sozlesme_disi_dizin'))} · "
                 f"makbuzsuz-taslak sayacı {_s(gk.get('makbuzsuz_dilekce_adayi'))}")
        o.append(f"    -> {ov.get('not','')}")
    else:
        o.append(f"    -> {ov.get('durum', OLCULEMEDI).upper()}: {ov.get('not','')}")

    reg = metrik.get("regresyon_sayaclari") or {}
    o.append("[7] REGRESYON SAYAÇLARI (P1-13 — v0.5.5'in KENDİ geçerlilik aracı)")
    if reg.get("durum") == "olculdu":
        am = reg.get("artefakt_matrisi") or {}
        am_str = " · ".join(f"{ad}:{'VAR' if v else 'YOK'}" for ad, v in am.items())
        o.append(f"    -> adım-artefakt matrisi : {am_str}")
        o.append(f"    -> muhakeme kaydı sayısı : {_s(reg.get('muhakeme_kayit_sayisi'))}")
        sd = reg.get("teyit_kutuk_arac_sinif_dagilimi") or {}
        sd_str = " · ".join(f"{k}:{v}" for k, v in sd.items())
        o.append(f"    -> teyit kütük araç sınıfı: {sd_str}")
        o.append(f"    -> döküm dosya sayısı    : {_s(reg.get('dokum_dosya_sayisi'))}")
        o.append(f"    -> tam-yükleme satır sayısı: {_s(reg.get('tam_yukleme_satir_sayisi'))}")
        o.append(f"    -> gölge-dizin sayısı    : {_s(reg.get('golge_dizin_sayisi'))}")
        kd = reg.get("kutuk_dilekce_sayaci") or {}
        o.append(f"    -> kütük/dilekçe künye   : {_s(kd.get('kutuk'))} / {_s(kd.get('dilekce'))}")
    else:
        o.append(f"    -> {reg.get('durum', OLCULEMEDI).upper()}: {reg.get('not','')}")

    if metrik.get("baz_kiyas"):
        bk = metrik["baz_kiyas"]
        o.append("[BAZ KIYAS] önceki bir baz çizgisine karşı EŞİKSİZ gözlem (--baz)")
        for ad, satir in (bk.get("alanlar") or {}).items():
            fark = satir.get("fark_yuzde")
            fark_str = f"%{fark:+.1f}" if fark is not None else "-"
            isaret = " ⚠" if ad in (bk.get("esik_asan_alanlar") or []) else ""
            o.append(f"    -> {ad:<26}: baz={_s(satir.get('baz'))}  güncel={_s(satir.get('guncel'))}"
                     f"  fark={fark_str}{isaret}")
        if bk.get("esik_asan_alanlar"):
            o.append(f"    -> ⚠ %{bk.get('esik_yuzde')}+ değişen: "
                     + ", ".join(bk["esik_asan_alanlar"]) + " (gözlem — v0.5.6 gündemine girer, ENGEL DEĞİL).")
        else:
            o.append(f"    -> %{bk.get('esik_yuzde')}+ değişen alan yok.")

    o.append("-" * 66)
    o.append(f"  metrik.json -> {metrik['cikti']}")
    o.append("  NOT: ölçer, yorumlamaz. 'yok/ölçülemedi' = kanıt yok; sayı UYDURULMADI.")
    o.append("=" * 66)
    return "\n".join(o)


def hesapla(kok, analiz_esik_token=None):
    """P0-7/P0-8 (v0.5.5) — `main()`'in ÖLÇÜM mantığını (dosya yazımından AYRI)
    İN-PROCESS yeniden-kullanılabilir hâle getirir: `pipeline_kayit.py --hook-
    denetle` (model-bağımsız Stop/SessionEnd hook'u) subprocess AÇMADAN aynı
    metrik sözlüğünü üretebilsin diye (P0-4/P0-5'teki 'kapı başka kapıyı
    subprocess ile çağırmaz' tasarım kuralıyla simetrik). CLI davranışı
    (main()) DEĞİŞMEDİ — yalnız gövdesi bu fonksiyona taşındı."""
    kunye, _kunye_ham, kunye_hata = _oku_json(_kunye_yolu(kok))
    analiz, _analiz_ham, analiz_hata = _oku_json(_analiz_yolu(kok))
    defter, defter_ham, defter_hata = _oku_json(_defter_yolu(kok))

    override_sayaci = olc_override(kok, defter, analiz)
    analiz_token_raporu = olc_analiz_token(kunye, kok, analiz_esik_token)

    return {
        "arac": "oa_metrik",
        "surum": "1.3",
        "olcum_zamani": _simdi(),
        "kok": os.path.abspath(kok),
        "kaynaklar": {
            "kunye": {"yol": os.path.relpath(_kunye_yolu(kok), kok),
                      "durum": "var" if kunye is not None else (kunye_hata or YOK)},
            "analiz": {"yol": os.path.relpath(_analiz_yolu(kok), kok),
                       "durum": "var" if analiz is not None else (analiz_hata or YOK)},
            "defter": {"yol": os.path.relpath(_defter_yolu(kok), kok),
                       "durum": "var" if defter is not None else (defter_hata or YOK)},
            "tam_yukleme": {"yol": os.path.relpath(_tam_yukleme_yolu(kok), kok),
                            "durum": "var" if os.path.exists(_tam_yukleme_yolu(kok)) else YOK},
        },
        "kulliyat": olc_kulliyat(kunye, kunye_hata),
        "secicilik": olc_secicilik(kunye, defter_ham, _analiz_ham),
        "tam_tur": olc_tam_tur(analiz, analiz_hata, kunye),
        "defter": olc_defter(defter, defter_hata),
        "override_sayaci": override_sayaci,
        "analiz_token_raporu": analiz_token_raporu,
        "regresyon_sayaclari": olc_regresyon(kok, analiz_token_raporu, override_sayaci),
    }


def main():
    ap = argparse.ArgumentParser(
        description="oa_metrik.py — token/verimlilik telemetrisi (deterministik ölçer)")
    ap.add_argument("--kok", default=".", help="çalışma kökü (varsayılan: bulunulan klasör)")
    ap.add_argument("--cikti", help="metrik.json yolu (varsayılan: <kok>/_oa/defter/metrik.json)")
    ap.add_argument("--analiz-esik-token", type=int, default=None, dest="analiz_esik_token",
                    help="ANALİZ TOKEN RAPORU eşiği (token); verilmezse külliyat tahmini "
                         "token'ı (kunye yoksa sabit varsayılan) kullanılır")
    ap.add_argument("--baz-yaz", dest="baz_yaz", default=None, metavar="YOL",
                    help="P1-13 — bu ölçümü BAZ ÇİZGİSİ olarak <YOL>'a da dondurur "
                         "(ör. metrik-baz-v054.json); --cikti'den BAĞIMSIZ, ayrıca yazılır")
    ap.add_argument("--baz", dest="baz", default=None, metavar="YOL",
                    help="P1-13 — önceki bir baz dosyasına (<YOL>, --baz-yaz ile üretilmiş ya "
                         "da eski bir metrik.json) karşı EŞİKSİZ token/sayaç kıyas raporu üretir "
                         "(yalnız GÖZLEM — bir GEÇİT değildir, teslimi engellemez)")
    a = ap.parse_args()

    kok = a.kok
    if not os.path.isdir(kok):
        sys.exit(f"HATA: klasör yok: {kok}")

    metrik = hesapla(kok, a.analiz_esik_token)

    if a.baz:
        baz_veri, _baz_ham, baz_hata = _oku_json(a.baz)
        if baz_veri is None:
            print(f"UYARI: baz dosyası okunamadı ({baz_hata}) — --baz kıyası ATLANDI: {a.baz}",
                  file=sys.stderr)
        else:
            metrik["baz_kiyas"] = baz_kiyasla(metrik, baz_veri)
            metrik["baz_kiyas"]["kaynak_dosya"] = os.path.abspath(a.baz)

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

    if a.baz_yaz:
        try:
            ust_baz = os.path.dirname(a.baz_yaz)
            if ust_baz:
                os.makedirs(ust_baz, exist_ok=True)
            with open(a.baz_yaz, "w", encoding="utf-8") as f:
                json.dump(metrik, f, ensure_ascii=False, indent=2)
            print(f"BAZ ÇİZGİSİ donduruldu: {os.path.abspath(a.baz_yaz)}")
        except Exception as e:
            print(f"UYARI: baz dosyası yazılamadı ({e})", file=sys.stderr)

    print(ozet_yaz(metrik))
    return 0


if __name__ == "__main__":
    sys.exit(main())

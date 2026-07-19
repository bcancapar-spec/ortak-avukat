#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
sure_nobetci.py — oa-sure SÜRE NÖBETÇİSİ (oturum açılışı deterministik özet)

hesapla_sure.py ile hesaplanıp `_oa/sureler.json`'a MEKANİK yazılan (halüsinasyon
çıpası — `oa_hafiza.py sure-flag` ile) son günleri BUGÜNE göre okur ve tek
bakışta durum çıkarır: geçmiş (kaçmış), yaklaşan (D-1/D-3/D-7 penceresi) ve
ileri süreleri işaretler, en yakın/geçmiş olanları üste alır. Amaç: her oturum
açılışında "hangi süre yanıyor" sorusunu tek komutla, sessiz kaçış olmadan
yanıtlamak.

Bu script HUKUKİ hesap YAPMAZ; son günler zaten hesapla_sure.py çıktısıdır.
Nöbetçi yalnızca defteri BUGÜNE göre tarar ve sıralar (deterministik). Adli
tatil/başlangıç anı gibi kurallar buraya değil hesapla_sure.py'ye aittir.

KANONİK DEFTER: `_oa/sureler.json` — `oa_hafiza.py sure-flag` ile aynı dosya
(mimari tekil kaynak; oa-pipeline/scripts/oa_hafiza.py'nin `init`/`sure-flag`
komutlarıyla PAYLAŞILIR — ayrı bir `_oa/defter/sureler.json` YOKTUR/kullanılmaz).
Şema TOLERANSLIDIR — ikisi de kabul edilir:
  (a) üst düzey LİSTE   : [ {"son_gun": "YYYY-MM-DD", "aciklama": "...", "tur": "usul|maddi"}, ... ]
  (b) sarmalayıcı (oa_hafiza.py'nin ürettiği biçim):
      {"flagler": [ {"son_gun"|"tarih": "YYYY-MM-DD", "aciklama": "...", "kural": "...", "tur": "..."} , ... ]}
Tarih alanı önce "son_gun", yoksa geriye-uyumlu "tarih" olarak okunur (iki alan
adı da desteklenir — oa_hafiza.py her iki alanı birlikte yazar). Defter yoksa
çökmez; "süre kaydı yok, oa-sure ile ekleyin" der.

Kullanım (Windows/PowerShell — 'python'):
  python sure_nobetci.py [--kok <klasör>]
    --kok : çalışma kökü; defter <kök>/_oa/sureler.json (varsayılan: .)

İşaretçiler (ASCII):
  [!!!] GEÇMİŞ veya BUGÜN (son gün) · [!] yaklaşan (D-1..D-7) · [ ] ileri
Çıkış kodu:
  0 = defter yok / boş ya da hiçbir süre acil değil
  3 = en az bir GEÇMİŞ/BUGÜN/yaklaşan süre VAR ya da okunamayan (bozuk) kayıt var — DİKKAT
  1 = defter var ama okunamıyor / biçim bozuk (JSON hatası)
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
from datetime import date

CIZGI = "=" * 66
ALT = "-" * 66
YAKIN_ESIK = 7  # gün — D-1..D-7 "yaklaşan" penceresi


def _defter_yolu(kok):
    # KANONİK yol — oa_hafiza.py init/sure-flag ile AYNI dosya (mimari tekil kaynak).
    return os.path.join(kok, "_oa", "sureler.json")


def _kayitlari_al(veri):
    """Üst düzey liste beklenir; toleranslı olarak yaygın sarmalayıcıları da açar.
    'flagler' — oa_hafiza.py sure-flag'in ürettiği kanonik sarmalayıcı anahtarıdır."""
    if isinstance(veri, list):
        return veri
    if isinstance(veri, dict):
        for anahtar in ("flagler", "sureler", "kayitlar", "records", "items"):
            if isinstance(veri.get(anahtar), list):
                return veri[anahtar]
    return None


def _tur_etiketi(kayit):
    tur = ""
    if isinstance(kayit, dict):
        tur = str(kayit.get("tur") or "").strip().lower()
    if tur in ("usul", "maddi"):
        return "[%s]" % tur
    return "[—]"


def _aciklama(kayit):
    if isinstance(kayit, dict):
        a = str(kayit.get("aciklama") or "").strip()
        if a:
            return a
    return "(açıklama yok)"


def _son_gun(kayit):
    """(date|None, ham_metin) — bozuk/eksik son_gun None döner (çökme yok).
    Alan adı önce 'son_gun' (kanonik), yoksa 'tarih' (oa_hafiza.py sure-flag
    geriye-uyumluluk alanı) olarak okunur."""
    ham = ""
    if isinstance(kayit, dict):
        ham = str(kayit.get("son_gun") or kayit.get("tarih") or "").strip()
    if not ham:
        return None, ham
    try:
        return date.fromisoformat(ham), ham
    except ValueError:
        return None, ham


def _kategori(gun, bugun):
    """(anahtar, isaret, etiket) — bugüne göre sınıf."""
    fark = (gun - bugun).days
    if fark < 0:
        return "GECMIS", "[!!!]", "GEÇMİŞ (%d gün önce doldu)" % (-fark)
    if fark == 0:
        return "BUGUN", "[!!!]", "BUGÜN — SON GÜN"
    if fark <= YAKIN_ESIK:
        return "YAKLASAN", "[!]", "D-%d (yaklaşıyor)" % fark
    return "ILERI", "[ ]", "D-%d" % fark


def _yaz_kayit(isaret, ham_gun, etiket, tur_tag, aciklama):
    print("%-6s%-12s%-27s%-8s%s" % (isaret, ham_gun, etiket, tur_tag, aciklama))


def main():
    ap = argparse.ArgumentParser(
        description="oa-sure süre nöbetçisi — sureler.json'u bugüne göre tarar ve sıralar.")
    ap.add_argument("--kok", default=".",
                    help="çalışma kökü; defter <kök>/_oa/sureler.json (varsayılan: .)")
    a = ap.parse_args()

    kok = os.path.abspath(a.kok)
    bugun = date.today()
    yol = _defter_yolu(kok)

    print(CIZGI)
    print("SÜRE NÖBETÇİSİ — bugün: %s" % bugun.isoformat())
    print("Defter: %s" % yol)
    print(CIZGI)

    # ── defter yok → çökme yok, yönlendir ──────────────────────────────────
    if not os.path.isfile(yol):
        print("Süre kaydı yok, oa-sure ile ekleyin.")
        print("(hesapla_sure.py ile son gün hesaplayıp `oa_hafiza.py sure-flag --tarih ... "
              "--aciklama \"...\" --kural ...` ile bu deftere işleyin — halüsinasyon çıpası.)")
        sys.exit(0)

    # ── defter oku → JSON bozuksa çökme yok, exit 1 ────────────────────────
    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            veri = json.load(f)
    except (OSError, ValueError) as e:
        print("HATA: defter okunamadı / biçim bozuk (%s)." % e, file=sys.stderr)
        print("Beklenen şema: [ {\"son_gun\":\"YYYY-MM-DD\",\"aciklama\":\"...\",\"tur\":\"usul|maddi\"}, ... ]",
              file=sys.stderr)
        sys.exit(1)

    kayitlar = _kayitlari_al(veri)
    if kayitlar is None:
        print("HATA: beklenen üst düzey LİSTE ya da {\"flagler\":[...]} sarmalayıcısı değil (şema uyumsuz).",
              file=sys.stderr)
        print("Beklenen: [ {\"son_gun\":\"YYYY-MM-DD\",\"aciklama\":\"...\",\"tur\":\"usul|maddi\"}, ... ] "
              "VEYA {\"flagler\": [...]}", file=sys.stderr)
        sys.exit(1)

    if not kayitlar:
        print("Süre kaydı yok (defter boş), oa-sure ile ekleyin.")
        sys.exit(0)

    # ── ayrıştır: geçerli tarihliler + bozuk/tarihsizler ───────────────────
    gecerli, bozuk = [], []
    for kayit in kayitlar:
        gun, ham = _son_gun(kayit)
        if gun is None:
            bozuk.append((ham, _tur_etiketi(kayit), _aciklama(kayit)))
        else:
            anahtar, isaret, etiket = _kategori(gun, bugun)
            gecerli.append((gun, anahtar, isaret, etiket, _tur_etiketi(kayit), _aciklama(kayit)))

    # en yakın/geçmiş üste: son güne göre artan (en geçmiş → en ileri)
    gecerli.sort(key=lambda x: (x[0], x[5]))

    sayac = {"GECMIS": 0, "BUGUN": 0, "YAKLASAN": 0, "ILERI": 0}
    for g in gecerli:
        sayac[g[1]] += 1

    # ── kısa özet (oturum açılışı) ─────────────────────────────────────────
    print("Özet: %d GEÇMİŞ · %d BUGÜN · %d YAKLAŞAN · %d İLERİ  (toplam %d kayıt%s)"
          % (sayac["GECMIS"], sayac["BUGUN"], sayac["YAKLASAN"], sayac["ILERI"],
             len(kayitlar), (", %d bozuk" % len(bozuk)) if bozuk else ""))
    print()

    # ── liste ──────────────────────────────────────────────────────────────
    for gun, anahtar, isaret, etiket, tur_tag, aciklama in gecerli:
        _yaz_kayit(isaret, gun.isoformat(), etiket, tur_tag, aciklama)

    if bozuk:
        print()
        print("BOZUK / TARİHSİZ kayıt(lar) — son_gun okunamadı (elle düzelt):")
        for ham, tur_tag, aciklama in bozuk:
            _yaz_kayit("[?]", (ham or "—"), "OKUNAMADI", tur_tag, aciklama)

    # ── sonuç + çıkış kodu ─────────────────────────────────────────────────
    acil = sayac["GECMIS"] + sayac["BUGUN"] + sayac["YAKLASAN"]
    print()
    print(ALT)
    if acil or bozuk:
        parcalar = []
        if sayac["GECMIS"]:
            parcalar.append("%d geçmiş" % sayac["GECMIS"])
        if sayac["BUGUN"]:
            parcalar.append("%d bugün" % sayac["BUGUN"])
        if sayac["YAKLASAN"]:
            parcalar.append("%d yaklaşan" % sayac["YAKLASAN"])
        if bozuk:
            parcalar.append("%d bozuk kayıt" % len(bozuk))
        print("DİKKAT: " + ", ".join(parcalar) + " — derhâl kontrol et; dış takvimle eşgüdümü doğrula.")
        print(CIZGI)
        sys.exit(3)
    print("Acil süre yok — tüm kayıtlar ileri tarihli. (Yine de dış takvimle eşgüdümü koru.)")
    print(CIZGI)
    sys.exit(0)


if __name__ == "__main__":
    main()

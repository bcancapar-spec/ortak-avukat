#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""İÇTİHAT KAYNAKÇASI üretici (v0.5.12 — link zinciri tamamlayıcısı).

Avukat kuralı (2026-08-27): "dilekçeye veya herhangi bir çalışmaya giren TÜM
yargı kararlarının linkleri TÜM çıktılarda olsun."

Ne yapar: taslakta atıf yapılan karar künyelerini (esas/karar numarası
çifti üzerinden) muhakeme kaydındaki (`*ictihat-muhakeme*.md`) kayıtlarla
eşler ve taslağın SONUNA işaretli bir `## İÇTİHAT KAYNAKÇASI` bloğu işler.
Blok İDEMPOTENTTİR: kendi işaretleri (`<!-- kaynakca:v1 -->`) arasındaki
bölgeyi tazeler, ikinci koşuda ikinci blok üretmez.

İlkeler:
- URL YALNIZ muhakeme kaydındaki `**KAYNAK-URL:**` satırından gelir —
  bu script link ÜRETMEZ/uydurmaz (v0.5.5.3: uydurma link, çıplak künyeden
  kötüdür; sahte "teyit edildi" görüntüsü verir).
- URL'siz künye GİZLENMEZ: "erişim linki kütüğe işlenmedi" notuyla
  listelenir — yokluk görünür kalır, teslim notunda uyarıya dönüşür.
- Taslakta geçmeyen muhakeme künyesi kaynakçaya GİRMEZ (kaynakça, taslağın
  fiilî atıflarının aynasıdır; şişirme yasak).
- Taslağa işlendiği için ürün zinciri (UDF → PDF → 40-UYAP kopyaları)
  kaynakçayı kendiliğinden taşır — "tüm çıktılarda" şartının mekanik yolu.

Kullanım:
  python kaynakca_uret.py --taslak <yol.md> --kok <dava kökü>
  python kaynakca_uret.py --taslak <yol.md> --kok <kök> --kuru   # yazmadan rapor
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
# (v0.5.5.5 saha dersi: dış süreç kodlaması teslim hattını kırmıştı).
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import glob
import importlib.util
import io
import os
import re
import sys

# ── B-3 DÜZELTMESİ (v0.5.14) — TEK KAYNAK ──────────────────────────────────
# Eski hâlde bu dosyanın kendi ESAS_RE/KARAR_RE'si vardı; yorumu "kunye_ortak
# ile aynı ruh" diyordu ama DESEN FARKLIYDI. Sonuç: kapının GÖREMEDİĞİ bir
# künyeyi kaynakça GÖRÜYOR ve o künye hakkında dilekçeye "tam metniyle okundu"
# beyanı yazıyordu. Artık çıkarım TEK yerde (`kunye_ortak`) yaşar — kapı neyi
# görüyorsa kaynakça da onu görür.
_KO_YOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kunye_ortak.py")
_spec = importlib.util.spec_from_file_location("_kaynakca_kunye_ortak", _KO_YOL)
ko = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ko)

KUNYE_SATIR_RE = re.compile(r"^\*\*KUNYE:\*\*\s*(.+)$", re.M)
KAYNAK_URL_RE = re.compile(r"^\*\*KAYNAK-URL:\*\*\s*(\S+)\s*$", re.M)

# İşaretler/başlık/önsöz `kunye_ortak`ta tanımlıdır (B-18: aynı tanımı
# `makine_blogu_maskele` de okur — üretici ile maskeleyici ayrışamaz).
BLOK_BAS = ko.KAYNAKCA_BLOK_BAS
BLOK_SON = ko.KAYNAKCA_BLOK_SON


def _ciftler(metin):
    """Metindeki (esas, karar) numara çiftleri — sıralı, tekil.
    Çıkarım `kunye_ortak.esas_karar_atiflari` iledir (tek-yazar kuralı);
    AYM/AİHM künyelerinde `karar` None'dır."""
    tekil = []
    for a in ko.esas_karar_atiflari(metin):
        c = (a["esas"], a["karar"])
        if c not in tekil:
            tekil.append(c)
    return tekil


def muhakeme_haritasi(kok):
    """Muhakeme kayıtlarından {(esas,karar) → {kunye, url}} haritası.
    Birden çok muhakeme dosyası varsa hepsi okunur; asla fırlatmaz."""
    harita = {}
    try:
        desen = os.path.join(kok, "_oa", "cikti", "*ictihat-muhakeme*.md")
        for yol in sorted(glob.glob(desen)):
            metin = io.open(yol, encoding="utf-8", errors="replace").read()
            # kayıtlar '**KUNYE:**' ayracıyla bölünür
            parcalar = re.split(r"(?=^\*\*KUNYE:\*\*)", metin, flags=re.M)
            for p in parcalar:
                mk = KUNYE_SATIR_RE.search(p)
                if not mk:
                    continue
                kunye = mk.group(1).strip()
                cf = _ciftler(kunye)
                if not cf:
                    continue
                mu = KAYNAK_URL_RE.search(p)
                harita[cf[0]] = {"kunye": kunye,
                                 "url": mu.group(1).strip() if mu else None}
    except Exception:
        pass
    return harita


def _kaynakca_blogu(satirlar, teyitsiz=0):
    """B-3 (P0, v0.5.14) — BEYAN KOŞULLUDUR.

    Eski hâlde blok, listedeki künyelerin TEYİT DURUMUNA BAKMADAN
    "Aşağıdaki kararların tamamı tam metinleriyle okunup kütüğe
    damgalanmıştır" diyordu. Denetim kanıtı (2026-08-31): muhakeme kaydı HİÇ
    olmayan uydurma bir künye için bu cümle taslağa YAZILDI ve diske işlendi
    (taslak md5 değişti). Bu, avukatın imzasını taşıyacak belgeye mekanik
    olarak YALAN yazmaktır — kütüğün hiç görmediği bir karar hakkında
    doğrulama beyanı üretilmesidir.

    Yeni kural: kütükte teyitli olmayan tek bir künye varsa "tam metniyle
    okundu" cümlesi HİÇ yazılmaz; onun yerine her satırın teyit durumunu
    gösteren dürüst bir önsöz kurulur."""
    govde = "\n".join(satirlar) if satirlar else "- (taslakta karar atfı bulunamadı)"
    if teyitsiz:
        onsoz = ("Aşağıdaki listede her kararın TEYİT DURUMU ayrıca gösterilmiştir:\n"
                 "\"⚠ TEYİT EDİLMEDİ\" işaretli künyeler için tam metin teyidi\n"
                 "YAPILMAMIŞTIR; erişim linkleri yalnız teyit kaydından gelir (bu blok\n"
                 "`kaynakca_uret.py` tarafından mekanik üretilir — elle yazılmaz).")
    else:
        onsoz = ("Aşağıdaki kararların tamamı tam metinleriyle okunup kütüğe\n"
                 "damgalanmıştır; erişim linkleri teyit kaydından gelir (bu blok\n"
                 "`kaynakca_uret.py` tarafından mekanik üretilir — elle yazılmaz).")
    return (f"{BLOK_BAS}\n\n{ko.KAYNAKCA_BASLIK}\n\n{onsoz}\n\n"
            f"{govde}\n\n{BLOK_SON}")


def taslaga_isle(taslak_yolu, kok, kuru=False):
    """Taslağa kaynakça bloğunu işler/tazeler. Döner:
    {linkli, linksiz, degisti, satirlar}."""
    metin = io.open(taslak_yolu, encoding="utf-8", errors="replace").read()
    # kendi bloğumuzu ayıklayarak taslağın ASIL gövdesindeki atıfları say
    govde = metin
    if BLOK_BAS in govde and BLOK_SON in govde:
        govde = govde[:govde.index(BLOK_BAS)] + govde[govde.index(BLOK_SON) + len(BLOK_SON):]
    harita = muhakeme_haritasi(kok)
    satirlar, linkli, linksiz, teyitsiz = [], 0, 0, 0
    for cift in _ciftler(govde):
        kayit = harita.get(cift)
        if kayit is None:
            # B-3: künye muhakeme kaydında HİÇ YOK — teyit edilmemiştir.
            # "link yok" ile "teyit yok" AYRI şeylerdir; eski şerh yalnız
            # LİNK yokluğuna dairdi ve teyitsizliği görünmez bırakıyordu.
            kunye = f"E. {cift[0]}" + (f" K. {cift[1]}" if cift[1] else "")
            satirlar.append(
                f"- {kunye} — ⚠ TEYİT EDİLMEDİ: bu künye teyit kütüğünde "
                "bulunamadı; tam metin teyidi YAPILMAMIŞTIR (oa_hafiza.py "
                "teyit --damga ile kütüğe işlenmelidir)")
            teyitsiz += 1
            linksiz += 1
        elif kayit.get("url"):
            satirlar.append(f"- {kayit['kunye']} — erişim: {kayit['url']}")
            linkli += 1
        else:
            satirlar.append(
                f"- {kayit['kunye']} — ⚠ erişim linki kütüğe işlenmedi "
                "(teyit kaydına --kaynak-url ile tamamlanmalı)")
            linksiz += 1
    blok = _kaynakca_blogu(satirlar, teyitsiz)
    if BLOK_BAS in metin and BLOK_SON in metin:
        yeni = (metin[:metin.index(BLOK_BAS)].rstrip()
                + "\n\n" + blok
                + metin[metin.index(BLOK_SON) + len(BLOK_SON):])
    else:
        yeni = metin.rstrip() + "\n\n" + blok + "\n"
    degisti = (yeni != metin)
    if degisti and not kuru:
        tmp = f"{taslak_yolu}.tmp.{os.getpid()}"
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(yeni)
        os.replace(tmp, taslak_yolu)
    return {"linkli": linkli, "linksiz": linksiz, "teyitsiz": teyitsiz,
            "degisti": degisti, "satirlar": satirlar}


def main():
    ap = argparse.ArgumentParser(description="İçtihat kaynakçası üretici (v0.5.12)")
    ap.add_argument("--taslak", required=True)
    ap.add_argument("--kok", required=True)
    ap.add_argument("--kuru", action="store_true", help="yazmadan raporla")
    a = ap.parse_args()
    r = taslaga_isle(a.taslak, a.kok, kuru=a.kuru)
    print(f"KAYNAKÇA: linkli={r['linkli']} linksiz={r['linksiz']} "
          f"teyitsiz={r['teyitsiz']} "
          f"{'(kuru koşu)' if a.kuru else ('işlendi' if r['degisti'] else 'değişiklik yok')}")
    for satir in r["satirlar"]:
        print("  " + satir)
    if r["teyitsiz"]:
        print("UYARI (B-3): TEYİT EDİLMEMİŞ künye var — kaynakçaya 'tam metniyle "
              "okundu' beyanı YAZILMADI. Bu künyeler teyit kütüğünde yok; "
              "teyit edilmeden çıktıya giremez (kapı: kunye_teyit.py).")
    if r["linksiz"]:
        print("UYARI: linksiz künye var — teyit kaydına --kaynak-url eklenmeli "
              "(bu araç link UYDURMAZ; yokluk görünür bırakılır).")
    sys.exit(0)


if __name__ == "__main__":
    main()

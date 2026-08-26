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
import io
import os
import re
import sys

# kunye_ortak ile aynı ruh: yıl/no çifti — geniş ama karar-özgü desen.
ESAS_RE = re.compile(r"\bE\.?\s*[:\s]?\s*(\d{4})\s*/\s*(\d{1,6})")
KARAR_RE = re.compile(r"\bK\.?\s*[:\s]?\s*(\d{4})\s*/\s*(\d{1,6})")
KUNYE_SATIR_RE = re.compile(r"^\*\*KUNYE:\*\*\s*(.+)$", re.M)
KAYNAK_URL_RE = re.compile(r"^\*\*KAYNAK-URL:\*\*\s*(\S+)\s*$", re.M)

BLOK_BAS = "<!-- kaynakca:v1 -->"
BLOK_SON = "<!-- /kaynakca -->"


def _ciftler(metin):
    """Metindeki (esas, karar) numara çiftleri — sıralı, tekil.
    Esas ve karar aynı cümle penceresinde aranmaz; belge ölçeğinde
    eşleşen sıradaki çiftler alınır (muhakeme kaydı künye-satırı tek
    satır olduğu için orada birebir; taslakta ise atıf kalıbı gereği
    E./K. yan yana geçer)."""
    esaslar = [(m.start(), f"{m.group(1)}/{m.group(2)}") for m in ESAS_RE.finditer(metin)]
    kararlar = [(m.start(), f"{m.group(1)}/{m.group(2)}") for m in KARAR_RE.finditer(metin)]
    ciftler = []
    for pos_e, e in esaslar:
        # en yakın (aynı atıf içindeki) karar no: e'den sonra 120 karakter içinde
        aday = [k for pos_k, k in kararlar if 0 <= pos_k - pos_e <= 160]
        ciftler.append((e, aday[0] if aday else None))
    tekil = []
    for c in ciftler:
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


def _kaynakca_blogu(satirlar):
    govde = "\n".join(satirlar) if satirlar else "- (taslakta karar atfı bulunamadı)"
    return (f"{BLOK_BAS}\n\n## İÇTİHAT KAYNAKÇASI\n\n"
            "Aşağıdaki kararların tamamı tam metinleriyle okunup kütüğe\n"
            "damgalanmıştır; erişim linkleri teyit kaydından gelir (bu blok\n"
            "`kaynakca_uret.py` tarafından mekanik üretilir — elle yazılmaz).\n\n"
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
    satirlar, linkli, linksiz = [], 0, 0
    for cift in _ciftler(govde):
        kayit = harita.get(cift)
        if kayit and kayit.get("url"):
            satirlar.append(f"- {kayit['kunye']} — erişim: {kayit['url']}")
            linkli += 1
        else:
            kunye = (kayit or {}).get("kunye") or f"E. {cift[0]}" + (f" K. {cift[1]}" if cift[1] else "")
            satirlar.append(
                f"- {kunye} — ⚠ erişim linki kütüğe işlenmedi "
                "(teyit kaydına --kaynak-url ile tamamlanmalı)")
            linksiz += 1
    blok = _kaynakca_blogu(satirlar)
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
    return {"linkli": linkli, "linksiz": linksiz,
            "degisti": degisti, "satirlar": satirlar}


def main():
    ap = argparse.ArgumentParser(description="İçtihat kaynakçası üretici (v0.5.12)")
    ap.add_argument("--taslak", required=True)
    ap.add_argument("--kok", required=True)
    ap.add_argument("--kuru", action="store_true", help="yazmadan raporla")
    a = ap.parse_args()
    r = taslaga_isle(a.taslak, a.kok, kuru=a.kuru)
    print(f"KAYNAKÇA: linkli={r['linkli']} linksiz={r['linksiz']} "
          f"{'(kuru koşu)' if a.kuru else ('işlendi' if r['degisti'] else 'değişiklik yok')}")
    for satir in r["satirlar"]:
        print("  " + satir)
    if r["linksiz"]:
        print("UYARI: linksiz künye var — teyit kaydına --kaynak-url eklenmeli "
              "(bu araç link UYDURMAZ; yokluk görünür bırakılır).")
    sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
aile_dogrula.py — oa-usta AİLE YAPI DENETİMİ (bakım garantörü)

Ailenin yapısal sağlığını deterministik denetler; her yeniden paketlemeden
ÖNCE koşulur, hata varken paketleme yapılmaz. Denetlenenler:
- SKILL.md var + frontmatter geçerli + name ↔ klasör adı eşleşiyor
- description uzunluğu: >1024 = HATA (paketleme sınırı), >850 = HATA (Fable tıraş sınırı)
  (bakım kuralı: YENİ İÇERİK GÖVDEYE EKLENİR, description'a DEĞİL)
- Fiziksel aktivasyon bloğu mevcut (çekirdek/pipeline'da özel bölüm)
- Değişiklik günlüğü işaretçisi + references/degisiklik-gunlugu.md mevcut
- SKILL.md'de anılan scripts/*.py dosyaları gerçekten var
- Sürüm işaretçisi ("Güncel sürüm") aile genelinde tutarlı
- ANAYASA TEK-KAYNAK KAPISI: eski model dayatması metni yok ('Opus-sınıfı'/'High altı');
  yaprak parçalar anayasa.md'ye referans veriyor; ortak-avukat/references/anayasa.md mevcut

Kullanım: python aile_dogrula.py <aile-kök-dizini>
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os, re, sys

CEKIRDEK = {"ortak-avukat", "oa-pipeline"}
PLACEHOLDER = {"oa-par", "oa-parca", "oa-x", "oa-skill-iskeleti"}  # gerçek parça değil (örnek/dosya;
# 'oa-par' = 'oa-parça' yer tutucusunun ASCII kırpımı)


def frontmatter(metin):
    m = re.match(r"^---\n(.*?)\n---\n", metin, re.S)
    if not m:
        return None, None
    blok = m.group(1)
    ad = re.search(r"^name:\s*(\S+)", blok, re.M)
    dm = re.search(r"^description:\s*>-?\n((?:[ \t]+.*\n?)+)", blok, re.M)
    desc = ""
    if dm:
        desc = " ".join(s.strip() for s in dm.group(1).splitlines() if s.strip())
    return (ad.group(1) if ad else None), desc


def main():
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        sys.exit("Kullanım: python aile_dogrula.py <aile-kök-dizini>")
    kok = sys.argv[1]
    hatalar, uyarilar, surumler = [], [], {}
    parcalar = sorted(d for d in os.listdir(kok)
                      if os.path.isdir(os.path.join(kok, d))
                      and os.path.isfile(os.path.join(kok, d, "SKILL.md")))
    if not parcalar:
        sys.exit("HATA: kök dizinde SKILL.md içeren parça bulunamadı.")

    for p in parcalar:
        yol = os.path.join(kok, p, "SKILL.md")
        try:
            metin = open(yol, encoding="utf-8").read()
        except UnicodeDecodeError as e:
            hatalar.append(f"{p}: SKILL.md UTF-8 okunamıyor ({e})")
            continue

        ad, desc = frontmatter(metin)
        if ad is None:
            hatalar.append(f"{p}: frontmatter yok/bozuk")
        elif ad != p:
            hatalar.append(f"{p}: frontmatter name='{ad}' klasör adıyla eşleşmiyor")
        if desc:
            n = len(desc)
            if n > 1024:
                hatalar.append(f"{p}: description {n} karakter (>1024 paketleme sınırı) "
                               f"— içerik GÖVDEYE taşınmalı")
            elif n > 850:
                hatalar.append(f"{p}: description {n} karakter (>850 Fable tıraş sınırı) "
                               f"— içerik GÖVDEYE taşınmalı, description'a değil")

        if p in CEKIRDEK:
            if "FİZİKSEL" not in metin:
                hatalar.append(f"{p}: fiziksel aktivasyon/işletim bölümü yok")
        elif "Fiziksel aktivasyon — simülasyon yasağı" not in metin:
            hatalar.append(f"{p}: 'Fiziksel aktivasyon — simülasyon yasağı' bloğu yok")

        # ANAYASA TEKİLLEŞTİRME KAPISI (2026-07) — tek kaynak enforcement
        if "Opus-sınıfı" in metin or "High altı" in metin:
            hatalar.append(f"{p}: ESKİ model dayatması metni ('Opus-sınıfı'/'High altı') var — "
                           "model/efor kullanıcı tercihidir; bu metin anayasa.md'ye taşınmış olmalı")
        if p not in CEKIRDEK and "references/anayasa.md" not in metin:
            hatalar.append(f"{p}: anayasa TEK-KAYNAK işaretçisi yok "
                           "('ortak-avukat/references/anayasa.md' referansı zorunlu — dedup sonrası)")

        if "degisiklik-gunlugu.md" not in metin:
            hatalar.append(f"{p}: günlük işaretçisi yok")
        if not os.path.isfile(os.path.join(kok, p, "references", "degisiklik-gunlugu.md")):
            hatalar.append(f"{p}: references/degisiklik-gunlugu.md yok")

        sm = re.search(r"Güncel sürüm:\s*\*\*(v[\d.]+)\*\*", metin)
        if sm:
            surumler.setdefault(sm.group(1), []).append(p)

        # script referans bütünlüğü
        for ref in set(re.findall(r"`?([\w\-]+/)?scripts/([\w]+\.py)`?", metin)):
            sahip, dosya = ref
            if sahip and sahip.rstrip("/") != p:
                hedef = os.path.join(kok, sahip.rstrip("/"), "scripts", dosya)
            else:
                hedef = os.path.join(kok, p, "scripts", dosya)
            if not os.path.isfile(hedef):
                hatalar.append(f"{p}: SKILL.md '{(sahip or '') + 'scripts/' + dosya}' anıyor "
                               f"ama dosya yok ({hedef})")

        # HAYALET PARÇA DENETİMİ — SKILL.md var olmayan bir oa- parçasına atıf yapmasın
        # (kaldırılan/yanlış yazılmış skill adı: oa-arsiv sınıfı bir daha doğmasın)
        # ASCII + min 3 harf: gerçek parça/klasör adları ASCII'dir; Türkçe-yazımlı
        # prose ("oa-müşteki-vekili") çağrı değildir, eşleşmez — sahte pozitif önlenir.
        for ref in set(re.findall(r"oa-[a-z]{3,}(?:-[a-z]+)*", metin)):
            if ref != p and ref not in parcalar and ref not in PLACEHOLDER:
                hatalar.append(f"{p}: var olmayan parçaya atıf '{ref}' "
                               "(hayalet — kaldırılmış/yanlış yazılmış skill adı)")

    # Tek kaynak anayasa dosyası mevcut olmalı (dedup'ın hedefi)
    if not os.path.isfile(os.path.join(kok, "ortak-avukat", "references", "anayasa.md")):
        hatalar.append("ortak-avukat/references/anayasa.md (TEK KAYNAK anayasa) yok — "
                       "dedup işaretçileri kırık kalır")

    # Plugin/marketplace manifest sürüm tutarlılığı (vitrin bayatlığı mekanik yakalansın)
    try:
        import json as _json
        pj = os.path.join(kok, "..", ".claude-plugin", "plugin.json")
        mj = os.path.join(kok, "..", "..", "..", ".claude-plugin", "marketplace.json")
        if os.path.isfile(pj) and os.path.isfile(mj):
            pv = _json.load(open(pj, encoding="utf-8")).get("version")
            mv = (_json.load(open(mj, encoding="utf-8")).get("plugins") or [{}])[0].get("version")
            if pv and mv and pv != mv:
                hatalar.append(f"manifest sürüm tutarsız: plugin.json={pv} ↔ marketplace.json={mv}")
    except Exception as e:
        uyarilar.append(f"manifest sürüm denetimi yapılamadı ({e})")

    if len(surumler) > 1:
        detay = "; ".join(f"{s}: {', '.join(pl[:4])}{'...' if len(pl) > 4 else ''}"
                          for s, pl in sorted(surumler.items()))
        uyarilar.append(f"sürüm işaretçileri tutarsız → {detay}")

    print(f"Denetlenen parça: {len(parcalar)}")
    if uyarilar:
        print("UYARILAR:")
        for u in uyarilar:
            print("  ⚠ " + u)
    if hatalar:
        print("HATALAR — bu hatalar kapanmadan aile paketlenemez:")
        for h in hatalar:
            print("  ✗ " + h)
        sys.exit(1)
    print("AİLE YAPI DENETİMİ TEMİZ.")


if __name__ == "__main__":
    main()

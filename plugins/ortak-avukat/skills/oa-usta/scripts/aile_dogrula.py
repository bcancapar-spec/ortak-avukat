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

        # YASAK-NÖBETÇİSİ (v0.5.8 P5 — anayasa m.0 devşirme protokolünün icra
        # aracı; Can kararı 2026-08-12): çekirdek scriptler AĞ kütüphanesi
        # import EDEMEZ (Layer 0'ın mekanik teminatı — müvekkil verisi python
        # katmanından dışarı çıkamaz; npx/subprocess hattına dokunmaz, o ayrı
        # ve bilinçli bir kanaldır). Semantica'da bu sınırın SALT KONVANSİYONLA
        # durduğunu ölçtük — bizde sürüm kapısına bağlıdır. Satır-başı desen:
        # fonksiyon-içi lazy importlar da yakalanır; docstring prose'u eşleşmez.
        script_dizin = os.path.join(kok, p, "scripts")
        if os.path.isdir(script_dizin):
            yasak_re = re.compile(
                r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|urllib3|socket|"
                r"openai|anthropic|groq|litellm|http\.client|urllib\.request)\b")
            for sad in sorted(os.listdir(script_dizin)):
                if not sad.endswith(".py"):
                    continue
                syol = os.path.join(script_dizin, sad)
                with open(syol, encoding="utf-8", errors="replace") as sf:
                    siçerik = sf.read()
                for i, satir in enumerate(siçerik.splitlines(), 1):
                    m2 = yasak_re.match(satir)
                    if m2:
                        hatalar.append(
                            f"{p}/scripts/{sad}:{i}: YASAK ağ-import "
                            f"'{m2.group(1)}' (m.0 devşirme protokolü / Layer 0 "
                            "— çekirdek script ağ kütüphanesi taşıyamaz)")
                # VENDOR denetimi (m.0: "vendor dosyası testsiz olamaz"):
                # '# VENDOR:' başlık satırı taşıyan scriptin tests/test_<ad>.py
                # eşi depoda bulunmalı. tests/ dizini yakın köklerde ARANIR;
                # hiç yoksa (aile depo DIŞINA kopyalanmış — test fixture'ları
                # gibi) denetim ATLANIR: kural depoyu bağlar, kopyayı değil.
                if re.search(r"^#\s*VENDOR:", siçerik, re.M):
                    tests_dizin = None
                    for yukari in ("..", os.path.join("..", ".."),
                                   os.path.join("..", "..", "..")):
                        aday = os.path.normpath(
                            os.path.join(kok, yukari, "tests"))
                        if os.path.isdir(aday):
                            tests_dizin = aday
                            break
                    if tests_dizin and not os.path.isfile(
                            os.path.join(tests_dizin, f"test_{sad[:-3]}.py")):
                        hatalar.append(
                            f"{p}/scripts/{sad}: VENDOR dosyası ama "
                            f"tests/test_{sad[:-3]}.py yok (m.0: vendor "
                            "testsiz olamaz)")

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
            pj_veri = _json.load(open(pj, encoding="utf-8"))
            mj_veri = _json.load(open(mj, encoding="utf-8"))
            pv = pj_veri.get("version")
            mv = (mj_veri.get("plugins") or [{}])[0].get("version")
            if pv and mv and pv != mv:
                hatalar.append(f"manifest sürüm tutarsız: plugin.json={pv} ↔ marketplace.json={mv}")

            # KAPI-A (v0.5.9): MANİFEST SAYI — description'daki "N skill"
            # iddiası skills/ altındaki GERÇEK parça sayısıyla eşleşmeli.
            # (Saha: vitrin "22 skill" derken repoda 20 vardı — vitrin
            # bayatlığı göz taramasına değil mekanik kapıya emanet.)
            desc_metinler = [pj_veri.get("description") or "",
                             mj_veri.get("description") or ""]
            desc_metinler += [(e.get("description") or "")
                              for e in (mj_veri.get("plugins") or [])]
            for metin_ in desc_metinler:
                for m_ in re.finditer(r"(\d+)\s+skill", metin_):
                    iddia = int(m_.group(1))
                    if iddia != len(parcalar):
                        hatalar.append(
                            f"manifest sayı iddiası: description '{iddia} skill' diyor "
                            f"ama skills/ altında {len(parcalar)} gerçek parça var "
                            "(vitrin bayat — sayı güncellenmeli)")
    except Exception as e:
        uyarilar.append(f"manifest sürüm denetimi yapılamadı ({e})")

    # KAPI-B (v0.5.9): HOOK KAPSAM — hooks.json'daki her run-hook.cmd modu
    # pipeline_kayit.py'de --<mod> bayrağı olarak tanımlı olmalı; ayrıca
    # hook_doktor'un DİNAMİK envanteri (hooks_olaylari) hooks.json olay
    # kümesiyle eşit olmalı. Depo-dışı kopyada (hooks.json / pipeline_kayit /
    # tools yok) SESSİZCE atlanır — kural depoyu bağlar, kopyayı değil
    # (VENDOR deseni).
    try:
        import json as _json
        hooks_json = os.path.normpath(os.path.join(kok, "..", "hooks", "hooks.json"))
        pk_yol = os.path.join(kok, "oa-pipeline", "scripts", "pipeline_kayit.py")
        if os.path.isfile(hooks_json) and os.path.isfile(pk_yol):
            hveri = _json.load(open(hooks_json, encoding="utf-8"))
            olaylar_js = set((hveri.get("hooks") or {}).keys())
            modlar = set()
            for girdiler in (hveri.get("hooks") or {}).values():
                for g in girdiler:
                    for h in g.get("hooks", []):
                        m_ = re.search(r'run-hook\.cmd"?\s+([\w-]+)',
                                       h.get("command") or "")
                        if m_:
                            modlar.add(m_.group(1))
            pk_metin = open(pk_yol, encoding="utf-8").read()
            for mod_ in sorted(modlar):
                if not re.search(r'add_argument\(\s*"--%s"' % re.escape(mod_), pk_metin):
                    hatalar.append(
                        f"hook kapsamı: hooks.json '{mod_}' modunu çağırıyor ama "
                        f"pipeline_kayit.py'de --{mod_} bayrağı tanımlı değil "
                        "(sessiz ölü hook — 447 dersi)")
            # hook_doktor dinamik envanter eşitliği (yakın-kök araması;
            # tools/ yoksa depo-dışı kopyadır → sessiz atla)
            doktor_yol = None
            for yukari in ("..", os.path.join("..", ".."),
                           os.path.join("..", "..", "..")):
                aday = os.path.normpath(os.path.join(kok, yukari, "tools", "hook_doktor.py"))
                if os.path.isfile(aday):
                    doktor_yol = aday
                    break
            if doktor_yol:
                import importlib.util as _ilu
                spec = _ilu.spec_from_file_location("_oa_hook_doktor", doktor_yol)
                hd = _ilu.module_from_spec(spec)
                spec.loader.exec_module(hd)
                doktor_olaylar = set(hd.hooks_olaylari(hooks_json))
                if doktor_olaylar != olaylar_js:
                    hatalar.append(
                        "hook kapsamı: hook_doktor.hooks_olaylari() "
                        f"({', '.join(sorted(doktor_olaylar))}) hooks.json olaylarıyla "
                        f"({', '.join(sorted(olaylar_js))}) eşit değil")
    except Exception as e:
        uyarilar.append(f"hook kapsam denetimi yapılamadı ({e})")

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

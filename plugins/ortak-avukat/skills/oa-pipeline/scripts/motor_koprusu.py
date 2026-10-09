#!/usr/bin/env python3
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa-pipeline — motor_koprusu.py
Dört halüsinasyon motorunu (illiyet, vakıa, kıyas, antitez) ve çapraz denetimi
TEK komutla koşturan köprü.

NEDEN VAR (v0.5.18 saha testi — Fable 5.1 teşhisi): grafik_denetim, vakia_matris,
kiyas_denetim, antitez_matris ve capraz_denetim kurulu ve sağlamdı (duman testi:
beşi de exit 0, damgalı çıktı) ama gerçek dosyada SIFIR kez koştu. Zincirde motoru
ÇAĞIRAN deterministik bir halka yoktu: her motorun kendi komutu kendi SKILL.md
gövdesindeydi ve o gövdeler hiç yüklenmedi. pipeline_kayit artık motor parçasında
UYGULANDI'yı, adım-8'i ve teslim (c2) kapısını motorun KENDİ damgasına bağlar; bu
köprü o kapıların RET/ELDEN mesajında gösterilen tek komuttur.

Sınır (anayasa — model kurar, script denetler): köprü motorları yalnız ÇAĞIRIR.
  * Damgayı motorun kendisi yazar; köprü hiçbir dosyaya `arac` alanı koymaz —
    sahte damga yapısal olarak imkânsızdır.
  * Girdi yoksa motoru koşturmaz (exit 2). Şablonu olan motorda (vakıa, antitez)
    motorun KENDİ `--iskelet` çıktısını belgelenmiş girdi adına UTF-8 yazar —
    yalnız o adda HİÇBİR dosya yoksa (var olan dosyanın üzerine asla yazmaz).
    Neden köprü yazar: Windows PowerShell 5.1'de `--iskelet > dosya` yönlendirmesi
    UTF-16 üretir ve motor o dosyayı okuyamaz (JSON okunamadı, exit 1).
    Şablonu olmayan motorda (graf, kıyas) şema belgesini gösterir.
  * Motorun kendi `--iskelet` şablonuyla AYNI kalmış (doldurulmamış) girdiyi
    doğrulatmaz — boş şablonun denetimi "motor koştu" sayılmaz.
  * Motorun bulgusu (ispat boşluğu, açık cephe, kritik kıyas boşluğu) köprünün
    çıkışını DEĞİŞTİRMEZ: rapor aynen basılır, hüküm avukatındır.
  * Hook yolunda DEĞİLDİR (performans değişmezleri etkilenmez); alt süreç
    kullanır çünkü motorlar kendi CLI sözleşmeleriyle (`sys.exit`) yaşar.

Kullanım:
    python motor_koprusu.py --kok <dava kökü>

Girdi adları (SKILL.md sözleşmesi; yoksa adında anahtar geçen DAMGASIZ ilk .json):
    _oa/cikti/01-illiyet-graf.json   → grafik_denetim → 01-illiyet-denetim.json
    _oa/cikti/04-vakia.json          → vakia_matris   → 04-vakia-denetim.json
    _oa/cikti/05-kiyas.json          → kiyas_denetim  → 05-kiyas-denetim.json
    _oa/cikti/06-antitez-matris.json → antitez_matris → 06-antitez-denetim.json
    (ardından) capraz_denetim        → capraz-denetim.json

Çıkış: 0 dört motor koştu (bulgular olabilir — raporu oku) · 2 en az bir motor
koşamadı (girdi yok / şablon doldurulmamış / çöktü / damga yazılmadı)
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
import subprocess
import sys

CIZGI = "=" * 70
RAPOR_SATIR_TAVANI = 60     # motor başına basılan rapor satırı; fazlası JSON'da — kesinti söylenir
MOTOR_ZAMAN_ASIMI = 900     # sn — 5.000 düğümlük graf bile bunun çok altında koşar

# (parça, skill, betik, girdi adı, yedek ad anahtarları, çıktı adı, damga, mod, şablon kaynağı)
# mod: "dogrula" → `--dogrula GİRDİ --json ÇIKTI` · "konumsal" → `GİRDİ --json ÇIKTI`
MOTORLAR = (
    ("oa-illiyet", "oa-illiyet", "grafik_denetim.py", "01-illiyet-graf.json",
     ("illiyet-graf", "graf"), "01-illiyet-denetim.json", "grafik_denetim", "konumsal",
     "oa-illiyet/references/illiyet-doktrini.md (şema dosyanın sonunda)"),
    ("oa-vakia", "oa-vakia", "vakia_matris.py", "04-vakia.json",
     ("vakia", "vakıa"), "04-vakia-denetim.json", "vakia_matris", "dogrula", None),
    ("oa-kiyas", "oa-kiyas", "kiyas_denetim.py", "05-kiyas.json",
     ("kiyas", "kıyas"), "05-kiyas-denetim.json", "kiyas_denetim", "konumsal",
     "oa-kiyas/references/kiyas-rehberi.md"),
    ("oa-antitez", "oa-antitez", "antitez_matris.py", "06-antitez-matris.json",
     ("antitez",), "06-antitez-denetim.json", "antitez_matris", "dogrula", None),
)
CAPRAZ = ("oa-pipeline", "capraz_denetim.py", "capraz-denetim.json", "capraz_denetim")


def motor_betigi(skill, betik):
    """Motorun yolu: önce eklenti düzeni (`skills/<skill>/scripts/`), yoksa bu
    dosyanın kendi dizini — model araç çantasını `_oa/araclar/`a DÜZ kopyalar
    (saha gerçeği). Bulunamazsa None."""
    burasi = os.path.dirname(os.path.abspath(__file__))
    skills = os.path.dirname(os.path.dirname(burasi))
    for aday in (os.path.join(skills, skill, "scripts", betik), os.path.join(burasi, betik)):
        if os.path.isfile(aday):
            return aday
    return None


def _json_oku(yol):
    try:
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _damgali_mi(yol):
    veri = _json_oku(yol)
    return isinstance(veri, dict) and bool(veri.get("arac"))


def _girdi_bul(cikti_dizin, ad, anahtarlar, cikti_adi):
    """Belgelenmiş ad önce; yoksa adında anahtar geçen, damgasız ilk .json
    (capraz_denetim._dosya_bul ile aynı kural: damgalı denetim çıktısı girdi değildir)."""
    tam = os.path.join(cikti_dizin, ad)
    if os.path.isfile(tam) and not _damgali_mi(tam):
        return tam
    if not os.path.isdir(cikti_dizin):
        return None
    for aday in sorted(os.listdir(cikti_dizin)):
        low = aday.lower()
        if (low.endswith(".json") and aday != cikti_adi and any(a in low for a in anahtarlar)):
            yol = os.path.join(cikti_dizin, aday)
            if os.path.isfile(yol) and not _damgali_mi(yol):
                return yol
    return None


def _kos(komut, kok):
    ortam = dict(os.environ)
    ortam["PYTHONIOENCODING"] = "utf-8"
    try:
        cp = subprocess.run(komut, capture_output=True, text=True, encoding="utf-8",
                            errors="replace", cwd=kok, env=ortam, timeout=MOTOR_ZAMAN_ASIMI)
    except subprocess.TimeoutExpired:
        return None, "", "zaman aşımı (%d sn)" % MOTOR_ZAMAN_ASIMI
    return cp.returncode, cp.stdout or "", cp.stderr or ""


def _sablon(betik, kok):
    """Motorun kendi `--iskelet` şablonu (STDOUT yalnız JSON — B-26); alınamazsa None."""
    kod, out, _err = _kos([sys.executable, betik, "--iskelet"], kok)
    if kod != 0:
        return None
    try:
        veri = json.loads(out)
    except ValueError:
        return None
    return veri if isinstance(veri, dict) and not veri.get("arac") else None


def _sablon_mu(betik, girdi_yolu, kok):
    """Girdi, motorun kendi `--iskelet` şablonuyla AYNI mı (doldurulmamış)?"""
    sablon = _sablon(betik, kok)
    return sablon is not None and sablon == _json_oku(girdi_yolu)


def _sablon_yaz(betik, hedef, kok):
    """Şablonu `hedef`e UTF-8 ve atomik yazar — YALNIZ hedefte hiçbir dosya yoksa.
    Döner: True (yazıldı) | False."""
    if os.path.exists(hedef):
        return False
    sablon = _sablon(betik, kok)
    if sablon is None:
        return False
    gecici = "%s.%d.oa-tmp" % (hedef, os.getpid())
    try:
        with open(gecici, "w", encoding="utf-8") as f:
            json.dump(sablon, f, ensure_ascii=False, indent=2)
        if os.path.exists(hedef):          # yarış: arada biri yazdıysa dokunma
            os.remove(gecici)
            return False
        os.replace(gecici, hedef)
    except OSError:
        try:
            os.remove(gecici)
        except OSError:
            pass
        return False
    return True


def _sema_belgesi(sema):
    """Şema belgesinin eklenti düzenindeki tam yolu; düz kitte göreli tarif."""
    if not sema:
        return None
    burasi = os.path.dirname(os.path.abspath(__file__))
    skills = os.path.dirname(os.path.dirname(burasi))
    goreli = sema.split(" ", 1)[0]
    tam = os.path.join(skills, *goreli.split("/"))
    return sema.replace(goreli, tam, 1) if os.path.isfile(tam) else sema


def _rapor_bas(metin):
    satirlar = metin.rstrip().splitlines()
    for s in satirlar[:RAPOR_SATIR_TAVANI]:
        print("    " + s)
    if len(satirlar) > RAPOR_SATIR_TAVANI:
        print("    … (%d satır daha — tam sonuç denetim JSON'undadır)"
              % (len(satirlar) - RAPOR_SATIR_TAVANI))


def _damga_tazelendi_mi(yol, damga, once_mtime):
    """Çıktı bu koşuda motorun kendisince yazıldı mı (damga + yeni mtime)?"""
    veri = _json_oku(yol)
    if not (isinstance(veri, dict) and veri.get("arac") == damga):
        return False
    try:
        return os.stat(yol).st_mtime_ns != once_mtime
    except OSError:
        return False


def _motor_kos(motor, kok, cikti_dizin):
    """Tek motor. Döner: (koştu mu, satır, kullanılan girdi yolu)."""
    _parca, skill, betik_adi, girdi_adi, anahtarlar, cikti_adi, damga, mod, sema = motor
    betik = motor_betigi(skill, betik_adi)
    if betik is None:
        return False, "%s: betik bulunamadı (%s/scripts/%s) — eklentiyi/araç çantasını tazeleyin" % (
            damga, skill, betik_adi), None
    girdi = _girdi_bul(cikti_dizin, girdi_adi, anahtarlar, cikti_adi)
    hedef_girdi = os.path.join(cikti_dizin, girdi_adi)
    if girdi is None:
        if mod != "dogrula":
            yol_tarifi = ("şema: %s — grafı/kıyası bu adla yaz, köprüyü yeniden koş"
                          % _sema_belgesi(sema))
        elif os.path.exists(hedef_girdi):
            yol_tarifi = ("bu adda bir dosya VAR ama damgalı bir denetim ÇIKTISI — girdi "
                          "değildir; matrisi bu adla yaz (dosyaya dokunulmadı)")
        elif _sablon_yaz(betik, hedef_girdi, kok):
            yol_tarifi = ("motorun kendi --iskelet şablonu bu adla YAZILDI (UTF-8) — evraka "
                          "dayanarak doldur, köprüyü yeniden koş")
        else:
            yol_tarifi = ('şablon yazılamadı; elle: python "%s" --iskelet — çıktıyı UTF-8 '
                          "olarak bu adla kaydet, doldur, köprüyü yeniden koş" % betik)
        return False, "%s: girdi yok — %s (%s)" % (damga, hedef_girdi, yol_tarifi), None
    if mod == "dogrula" and _sablon_mu(betik, girdi, kok):
        return False, ("%s: girdi motorun şablonuyla AYNI — iskelet doldurulmamış (%s); "
                       "boş şablonun denetimi 'motor koştu' sayılmaz" % (damga, girdi)), girdi
    cikti = os.path.join(cikti_dizin, cikti_adi)
    try:
        once = os.stat(cikti).st_mtime_ns
    except OSError:
        once = None
    if mod == "dogrula":
        komut = [sys.executable, betik, "--dogrula", girdi, "--json", cikti]
    else:
        komut = [sys.executable, betik, girdi, "--json", cikti]
        if damga == "grafik_denetim":
            komut += ["--kok", kok]
    print()
    print("── %s  (%s)" % (damga, os.path.relpath(girdi, kok)))
    kod, out, err = _kos(komut, kok)
    _rapor_bas(out)
    if kod is None:
        return False, "%s: %s" % (damga, err), girdi
    if not _damga_tazelendi_mi(cikti, damga, once):
        hata = (err.strip().splitlines() or [""])[-1][:200]
        return False, "%s: motor exit %s ile döndü, damgalı çıktı YAZILMADI%s" % (
            damga, kod, (" — " + hata) if hata else ""), girdi
    veri = _json_oku(cikti) or {}
    if veri.get("denetim_coktu"):
        return False, "%s: DENETİM ÇÖKTÜ (exit %s) — %s" % (damga, kod, veri.get("hata") or "?"), girdi
    return True, "%s → %s (exit %s)" % (damga, os.path.relpath(cikti, kok), kod), girdi


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Dört halüsinasyon motorunu (illiyet/vakıa/kıyas/antitez) ve çapraz "
                    "denetimi tek komutla koşturur; damgayı motorlar yazar.")
    ap.add_argument("--kok", default=".", help="dava kökü (_oa/ burada)")
    a = ap.parse_args(argv)
    kok = os.path.abspath(a.kok)
    cikti_dizin = os.path.join(kok, "_oa", "cikti")

    print(CIZGI)
    print("MOTOR KÖPRÜSÜ — halüsinasyon motorları (oa-pipeline)")
    print(CIZGI)
    print("Kök: %s" % kok)
    if not os.path.isdir(cikti_dizin):
        print("HATA: %s yok — önce ingest ve motor girdileri." % cikti_dizin)
        return 2

    sonuclar, girdiler = [], {}
    for motor in MOTORLAR:
        kostu, satir, girdi = _motor_kos(motor, kok, cikti_dizin)
        sonuclar.append((kostu, satir))
        if kostu and girdi:
            girdiler[motor[6]] = girdi

    # Çapraz denetim — motorların KULLANDIĞI girdilerle (dizin taramasına bırakılmaz).
    # En az iki girdi şarttır: tek dosyalı/girdisiz çapraz denetim "tutarlı" der ama
    # hiçbir şeyi kıyaslamamıştır — o JSON'u üretmek yanıltıcı olurdu.
    capraz_satir = None
    capraz = motor_betigi(CAPRAZ[0], CAPRAZ[1])
    capraz_girdi = [d for d in ("grafik_denetim", "vakia_matris", "kiyas_denetim") if d in girdiler]
    if capraz is None:
        capraz_satir = "capraz_denetim: betik bulunamadı — çapraz denetim KOŞMADI"
    elif len(capraz_girdi) < 2:
        capraz_satir = ("capraz_denetim: KOŞMADI — en az iki motor girdisi gerekli "
                        "(graf/vakıa/kıyas; koşan: %s)" % (", ".join(capraz_girdi) or "yok"))
    else:
        komut = [sys.executable, capraz, "--cikti-dizin", cikti_dizin,
                 "--json", os.path.join(cikti_dizin, CAPRAZ[2])]
        for bayrak, damga in (("--graf", "grafik_denetim"), ("--vakia", "vakia_matris"),
                              ("--kiyas", "kiyas_denetim")):
            if damga in girdiler:
                komut += [bayrak, girdiler[damga]]
        print()
        print("── capraz_denetim")
        kod, out, err = _kos(komut, kok)
        _rapor_bas(out)
        hedef = os.path.join("_oa", "cikti", CAPRAZ[2])
        if kod == 0:
            capraz_satir = "capraz_denetim → %s (exit 0)" % hedef
        elif kod == 1:
            capraz_satir = "capraz_denetim → %s (exit 1 — kopuk referans var, rapora bak)" % hedef
        else:
            capraz_satir = "capraz_denetim: exit %s — %s" % (kod, err.strip()[-200:])

    kosan = sum(1 for k, _ in sonuclar if k)
    print()
    print(CIZGI)
    print("KÖPRÜ SONUCU: %d/%d motor koştu (damgaları motorların kendisi yazdı)." % (kosan, len(sonuclar)))
    for kostu, satir in sonuclar:
        print("  %s %s" % ("✓" if kostu else "✗", satir))
    if capraz_satir:
        print("  · " + capraz_satir)
    if kosan == len(sonuclar):
        print("Sonraki adım: bulguları oku — dilekçe yalnız bu denetimlerden geçen olgu, "
              "illiyet, kıyas ve karşı-tez değerlendirmesine dayanır; hüküm avukatındır.")
        print(CIZGI)
        return 0
    print("Eksik motorlar koşmadan dilekçe adımı (adım-8) ve teslim (c2) kapısı RET verir; "
          "bilinçli geçiş yalnız gerekçeli avukat şerhiyle: --serh \"...\" --serh-kapi halusinasyon")
    print(CIZGI)
    return 2


if __name__ == "__main__":
    sys.exit(main())

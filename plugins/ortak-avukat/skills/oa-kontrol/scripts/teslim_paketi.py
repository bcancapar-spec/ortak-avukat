#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
teslim_paketi.py — oa-kontrol TEK KOMUT TESLİM ZİNCİRİ (deterministik orkestra)

Bir taslağı teslime hazırlarken oa- ailesinin teslim öncesi kapılarını TEK
komutla, SABİT sırada ve İLK ENGELDE DURARAK koşar; hangi kapının kapandığını
tek raporda basar. Amaç: teslim öncesi denetimi "hatırlanan bir liste" olmaktan
çıkarıp MEKANİK bir zincire çevirmek. Script hukuki karar VERMEZ; yalnız alt
scriptleri çağırır, çıkış kodlarını okur ve raporlar. Nihai göz avukatındır.

Zincir (ilk exit != 0'da DURUR — kalan kapılar çalıştırılmaz):
  (a)  dilekce_denetim.py <taslak> --tip --taraf  → zorunlu unsur + müvekkil-aleyhi
  (b)  kunye_teyit.py <taslak>                     → atıf/künye izi (teyitsiz = engel)
  (b2) ictihat_muhakeme_denetim.py <taslak> --kok <kök>  → İçtihat Muhakeme Zinciri
       (MODÜL 2, M2-3'te zincire BAĞLANDI — yeni yeşil ışık): çıplak içtihat atfı /
       DAMGA=ALEYHE / eksik AYIRT-ETME / damgasız-geçersiz DAMGA → engel; NOTR/emsal-yok
       yalnız uyarı (bloklamaz). (b)'nin künye-izi denetiminden AYRI ve TAMAMLAYICIDIR —
       (b) künyenin kaynakta İZİNİ, (b2) o künyenin GERÇEKTEN MUHAKEME EDİLİP EDİLMEDİĞİNİ
       ve DAMGA'sına göre dış-çıktıya girip giremeyeceğini denetler.
  (c)  gizlilik_tara.py <taslak>   [yalnız --dis-arac ise]  → Privacy Layer 0
  (d)  pipeline_kayit.py --denetle --kok <kök> [yalnız defter varsa]  → defter boşluğu
       ("defter var" kuralı tam_tur.py._defter_var_mi ile AYNI: pipeline-olaylar.jsonl
       boş-değil VEYA pipeline-durum.json mevcut — kapılar arası tutarlılık için)
  (e)  tam_tur.py --durum          → tam tur / delta durumu (BİLGİ; engel SAYILMAZ)
Hepsi geçerse:
  udf_yaz.py --girdi <taslak> --cikti <taslak>.udf  → UDF üret, "TESLİME HAZIR".

Alt scriptler bu scriptin __file__ konumundan GÖRELİ keşfedilir
(../../<skill>/scripts/...). Bulunamayan kapı "script yok — atlandı" diye AÇIKÇA
raporlanır (sessiz geçilmez) ve teslimde uyarı olarak listelenir.

Not: alt scriptler başka ajanlarca güncelleniyor olabilir; bu zincir yalnız
DOSYA-YOLU + TEMEL argümanlarla çağırır, opsiyonel yeni bayraklara güvenmez.

Kullanım (Windows/PowerShell — 'python'):
  python teslim_paketi.py <taslak.md> --tip <tip> --taraf <taraf> [--dis-arac] [--kok <klasör>]
    --tip   : dava|cevap|istinaf|temyiz|aym_bireysel|genel  (dilekce_denetim'e geçer)
    --taraf : davaci|davali|sanik|katilan|mudahil            (boş bırakılabilir)
    --dis-arac : çıktı dış araca (web/bulut/e-posta) gidecekse Layer 0 taramasını ekler
    --kok   : çalışma kökü; _oa/... göreli yolları buradan çözülür (varsayılan: bulunulan klasör)

Çıkış kodu:
  0 = tüm engelleyici kapılar açık, UDF üretildi (TESLİME HAZIR)
  1 = bir kapı kapandı (teslim durduruldu) ya da UDF üretilemedi / kullanım hatası
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import os
import subprocess
import sys

# ── Alt script keşfi: __file__ (.../skills/oa-kontrol/scripts/) → .../skills ──
BURA = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.abspath(os.path.join(BURA, "..", ".."))


def _script(skill, ad):
    return os.path.join(SKILLS, skill, "scripts", ad)


S_DILEKCE = _script("oa-dilekce", "dilekce_denetim.py")   # (a)
S_KUNYE = _script("oa-kontrol", "kunye_teyit.py")          # (b)
S_ICTIHAT_MUHAKEME = _script("oa-kontrol", "ictihat_muhakeme_denetim.py")  # (b2)
S_GIZLILIK = _script("oa-gizlilik", "gizlilik_tara.py")    # (c)
S_PIPELINE = _script("oa-pipeline", "pipeline_kayit.py")   # (d)
S_TAMTUR = _script("oa-pipeline", "tam_tur.py")            # (e)
S_UDF = _script("oa-dilekce", "udf_yaz.py")                # (+)

CIZGI = "=" * 66
ALT = "-" * 66


def _kos(script_yolu, arglar, kok):
    """Scripti çalıştıran interpreter ile (sys.executable = 'python') koşar.
    (bulundu, returncode, birlesik_cikti) döndürür. cwd=kok: alt scriptlerin
    _oa/... göreli varsayılanları çalışma kökünden çözülsün diye."""
    if not os.path.isfile(script_yolu):
        return False, None, ""
    komut = [sys.executable, script_yolu] + list(arglar)
    try:
        p = subprocess.run(komut, cwd=kok, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    except Exception as e:  # alt süreç hiç başlatılamadı → engel say
        return True, 1, "[teslim_paketi] alt süreç başlatılamadı: %s" % e
    return True, p.returncode, (p.stdout or "") + (p.stderr or "")


def _alt_cikti_yaz(cikti):
    """Alt script çıktısını tek raporun içine girintili gömer."""
    icerik = (cikti or "").rstrip("\n")
    if not icerik.strip():
        print("    | (çıktı yok)")
        return
    for satir in icerik.split("\n"):
        print("    | " + satir)


def _bolum(baslik):
    print()
    print(ALT)
    print(baslik)
    print(ALT)


def _defter_var_mi(kok):
    """oa-pipeline'ın pipeline_kayit.py --baslat ile açtığı olay defteri bu kökte
    var mı? tam_tur.py'deki _defter_var_mi ile AYNI kural (v-jsonl mimarisinde
    gerçeğin kaynağı pipeline-olaylar.jsonl, durum.json türev/eski görünüm):
    jsonl mevcut ve boş DEĞİLSE VEYA (jsonl'den önceki eski görünüm olarak)
    durum.json varsa defter var sayılır. İki kapı arasında bu kural tutarlı
    olmazsa 'defter yok — atlandı' denip fiilen doğrulanmamış bir tur teslime
    çıkabilir."""
    olaylar = os.path.join(kok, "_oa", "defter", "pipeline-olaylar.jsonl")
    if os.path.isfile(olaylar) and os.path.getsize(olaylar) > 0:
        return True
    durum = os.path.join(kok, "_oa", "defter", "pipeline-durum.json")
    return os.path.isfile(durum)


def _kapi(script_yolu, arglar, kok, engelleyici=True):
    """Bir kapıyı çalıştırıp raporlar. Döndürür: 'ATLA' | 'OK' | 'BLOK' | 'BILGI', rc."""
    bulundu, rc, cikti = _kos(script_yolu, arglar, kok)
    if not bulundu:
        print("    [ATLA] script yok — atlandı: %s" % script_yolu)
        return "ATLA", rc
    _alt_cikti_yaz(cikti)
    if not engelleyici:
        print("    [BILGI] bilgi kapısı — teslim engeli SAYILMAZ (exit %s)." % rc)
        return "BILGI", rc
    if rc != 0:
        print("    [BLOK] KAPI KAPALI (exit %s)." % rc)
        return "BLOK", rc
    print("    [OK] kapı açık (exit 0).")
    return "OK", rc


def main():
    ap = argparse.ArgumentParser(
        description="oa-kontrol tek komut teslim zinciri — ilk engelde durur, tek rapor basar.")
    ap.add_argument("taslak", help="Teslim edilecek taslak (.md/.txt)")
    ap.add_argument("--tip", default="genel",
                    help="dilekçe tipi (dava|cevap|istinaf|temyiz|aym_bireysel|genel); "
                         "dilekce_denetim.py'ye geçer (varsayılan: genel)")
    ap.add_argument("--taraf", default="",
                    choices=["", "davaci", "davali", "sanik", "katilan", "mudahil"],
                    help="taraf sıfatı (müvekkil-aleyhi taraması için); boş bırakılabilir")
    ap.add_argument("--dis-arac", action="store_true",
                    help="çıktı dış araca gidecekse Privacy Layer 0 (gizlilik_tara) kapısını ekle")
    ap.add_argument("--kok", default=".",
                    help="çalışma kökü; _oa/... göreli yolları buradan çözülür (varsayılan: .)")
    a = ap.parse_args()

    taslak = os.path.abspath(a.taslak)
    kok = os.path.abspath(a.kok)

    if not os.path.isfile(taslak):
        print("HATA: taslak bulunamadı: %s" % taslak, file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(kok):
        print("HATA: kök klasör yok: %s" % kok, file=sys.stderr)
        sys.exit(1)

    print(CIZGI)
    print("TESLİM PAKETİ — tek komut teslim zinciri (oa-kontrol)")
    print(CIZGI)
    print("Taslak    : %s" % taslak)
    print("tip/taraf : %s / %s" % (a.tip, a.taraf or "—"))
    print("Dış araç  : %s" % ("EVET (Layer 0 taraması dahil)" if a.dis_arac else "hayır"))
    print("Kök (_oa) : %s" % kok)

    gecen = []       # açılan (OK) kapılar
    atlanan = []     # script bulunamadığı için atlanan kapılar
    kapanan = None   # ilk kapanan kapı: (ad, rc)

    # ── (a) dilekçe denetimi — zorunlu unsur + müvekkil-aleyhi ──────────────
    _bolum("[a] DİLEKÇE DENETİMİ — zorunlu unsur + müvekkil-aleyhi  (dilekce_denetim.py)")
    arglar_a = [taslak, "--tip", a.tip] + (["--taraf", a.taraf] if a.taraf else [])
    sonuc, rc = _kapi(S_DILEKCE, arglar_a, kok)
    if sonuc == "ATLA":
        atlanan.append("(a) dilekce_denetim.py")
    elif sonuc == "BLOK":
        kapanan = ("(a) DİLEKÇE DENETİMİ", rc)
    elif sonuc == "OK":
        gecen.append("(a) dilekçe denetimi")

    # ── (b) atıf/künye izi ─────────────────────────────────────────────────
    if kapanan is None:
        _bolum("[b] ATIF/KÜNYE DOĞRULAMA — teyitsiz atıf teslim engeli  (kunye_teyit.py)")
        sonuc, rc = _kapi(S_KUNYE, [taslak], kok)
        if sonuc == "ATLA":
            atlanan.append("(b) kunye_teyit.py")
        elif sonuc == "BLOK":
            kapanan = ("(b) ATIF/KÜNYE DOĞRULAMA", rc)
        elif sonuc == "OK":
            gecen.append("(b) atıf/künye")

    # ── (b2) İçtihat Muhakeme Zinciri — çıplak/ALEYHE/eksik-alanlı atıf ─────
    if kapanan is None:
        _bolum("[b2] İÇTİHAT MUHAKEME ZİNCİRİ — çıplak/ALEYHE/eksik-alanlı atıf "
               "(ictihat_muhakeme_denetim.py)")
        sonuc, rc = _kapi(S_ICTIHAT_MUHAKEME, [taslak, "--kok", kok], kok)
        if sonuc == "ATLA":
            atlanan.append("(b2) ictihat_muhakeme_denetim.py")
        elif sonuc == "BLOK":
            kapanan = ("(b2) İÇTİHAT MUHAKEME ZİNCİRİ", rc)
        elif sonuc == "OK":
            gecen.append("(b2) içtihat muhakeme zinciri")

    # ── (c) gizlilik / Privacy Layer 0 — yalnız --dis-arac ise ─────────────
    if kapanan is None:
        _bolum("[c] GİZLİLİK / PRIVACY LAYER 0  (gizlilik_tara.py)")
        if not a.dis_arac:
            print("    [BILGI] --dis-arac verilmedi; içerik dışarı çıkmıyor sayıldı — "
                  "Layer 0 taraması ATLANDI.")
        else:
            sonuc, rc = _kapi(S_GIZLILIK, [taslak], kok)
            if sonuc == "ATLA":
                atlanan.append("(c) gizlilik_tara.py")
            elif sonuc == "BLOK":
                kapanan = ("(c) GİZLİLİK / LAYER 0", rc)
            elif sonuc == "OK":
                gecen.append("(c) gizlilik/Layer 0")

    # ── (d) pipeline defter boşluğu — yalnız defter varsa ──────────────────
    if kapanan is None:
        _bolum("[d] PİPELİNE DEFTER BOŞLUĞU  (pipeline_kayit.py --denetle)")
        if not _defter_var_mi(kok):
            print("    [BILGI] pipeline defteri yok (%s)" %
                  os.path.join(kok, "_oa", "defter", "pipeline-olaylar.jsonl"))
            print("            → bu dosya pipeline defteri kullanmıyor; defter denetimi ATLANDI.")
        else:
            sonuc, rc = _kapi(S_PIPELINE, ["--denetle", "--kok", kok], kok)
            if sonuc == "ATLA":
                atlanan.append("(d) pipeline_kayit.py")
            elif sonuc == "BLOK":
                kapanan = ("(d) PİPELİNE DEFTER BOŞLUĞU", rc)
            elif sonuc == "OK":
                gecen.append("(d) pipeline defteri")

    # ── (e) tam tur / delta durumu — BİLGİ (engel değil, exit 3 dahil) ──────
    if kapanan is None:
        _bolum("[e] TAM TUR / DELTA DURUMU — BİLGİ (teslim engeli değil)  (tam_tur.py --durum)")
        sonuc, rc = _kapi(S_TAMTUR, ["--durum"], kok, engelleyici=False)
        if sonuc == "ATLA":
            atlanan.append("(e) tam_tur.py")
        # BILGI / diğer: hiçbir zaman engel değil (exit 3 = tam tur yok/delta bekliyor — sadece bilgi)

    # ── ilk engelde durduysa: rapor + çık ──────────────────────────────────
    print()
    print(CIZGI)
    if kapanan is not None:
        ad, rc = kapanan
        print("SONUÇ: TESLİM DURDURULDU — İLK KAPANAN KAPI: %s (exit %s)." % (ad, rc))
        print("Zincir bu noktada durdu; SONRAKİ KAPILAR ÇALIŞTIRILMADI (ilk engelde dur ilkesi).")
        if gecen:
            print("Bu kapıya kadar açılan: " + ", ".join(gecen) + ".")
        if atlanan:
            print("Not — script bulunamadığı için ATLANAN kapı(lar): " + ", ".join(atlanan) + ".")
        print("UDF ÜRETİLMEDİ. Kapanan kapıyı gider ve teslim_paketi'ni yeniden koş.")
        print(CIZGI)
        sys.exit(1)

    # ── tüm engelleyici kapılar açık → UDF üret ────────────────────────────
    _bolum("[+] UDF ÜRETİMİ — udf_yaz.py --girdi <taslak> --cikti <taslak>.udf")
    udf_cikti = taslak + ".udf"
    bulundu, rc, cikti = _kos(S_UDF, ["--girdi", taslak, "--cikti", udf_cikti], kok)
    udf_uretildi = False
    if not bulundu:
        print("    [ATLA] script yok — atlandı: %s" % S_UDF)
        atlanan.append("(+) udf_yaz.py")
    else:
        _alt_cikti_yaz(cikti)
        if rc != 0:
            print("    [BLOK] UDF üretimi başarısız (exit %s)." % rc)
            print()
            print(CIZGI)
            print("SONUÇ: TÜM KAPILAR AÇIK ama UDF ÜRETİLEMEDİ — udf_yaz.py çıktısına bak.")
            if atlanan:
                print("Not — atlanan kapı(lar): " + ", ".join(atlanan) + ".")
            print(CIZGI)
            sys.exit(1)
        udf_uretildi = os.path.isfile(udf_cikti)
        print("    [OK] UDF üretildi.")

    print()
    print(CIZGI)
    print("SONUÇ: TESLİME HAZIR")
    print(CIZGI)
    print("Açılan engelleyici kapı(lar): " + (", ".join(gecen) if gecen else "—") + ".")
    print("Üretilen / ilgili dosyalar:")
    print("   - Taslak : %s" % taslak)
    if udf_uretildi:
        print("   - UDF    : %s" % udf_cikti)
    else:
        print("   - UDF    : (üretilemedi — udf_yaz.py yok/atlandı)")
    if atlanan:
        print("UYARI — script bulunamadığı için ATLANAN kapı(lar): " + ", ".join(atlanan) + ".")
        print("        Bu kapılar DENETLENMEDİ; teslimden önce elle doğrula (sessiz geçilmedi).")
    print("Not: bu zincir mekanik kapıların açık olduğunu gösterir; içerik/esas doğruluğu ve")
    print("     nihai göz AVUKATINDIR (oa-kontrol A-listesi muhakeme işidir).")
    sys.exit(0)


if __name__ == "__main__":
    main()

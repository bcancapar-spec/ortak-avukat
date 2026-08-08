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
  (b2) ictihat_muhakeme_denetim.py <taslak> --kok <kök> --tip <tip>  → İçtihat
       Muhakeme Zinciri (MODÜL 2, M2-3'te zincire BAĞLANDI — yeni yeşil ışık):
       çıplak içtihat atfı / DAMGA=ALEYHE / eksik AYIRT-ETME / damgasız-geçersiz
       DAMGA → engel; NOTR/emsal-yok yalnız uyarı (bloklamaz). `--tip` (M3-2/R6)
       emsal-yok uyarısını yalnız "esaslı" tiplerde basar (dava/cevap/istinaf/
       temyiz/aym_bireysel); yemin/idari-kanal gibi hafif tiplerde bu uyarı
       [BİLGİ]'ye düşer (yine bloklamaz). (b)'nin künye-izi denetiminden AYRI ve
       TAMAMLAYICIDIR — (b) künyenin kaynakta İZİNİ, (b2) o künyenin GERÇEKTEN
       MUHAKEME EDİLİP EDİLMEDİĞİNİ ve DAMGA'sına göre dış-çıktıya girip
       giremeyeceğini denetler.
  (c)  gizlilik_tara.py <taslak>   [yalnız --dis-arac ise]  → Privacy Layer 0
  (d)  pipeline_kayit.denetle_calistir(kok, makbuz_kontrolu=False) [yalnız defter
       varsa] → defter boşluğu — P0-5 (v0.5.5): artık İN-PROCESS import (subprocess
       DEĞİL — 'kapı başka kapıyı subprocess ile çağırmaz' ilkesi); makbuz bütünlüğü
       BU kapının amacı DEĞİLDİR (dairesel bağımlılık kırıcı — bkz. modül içi not)
       ("defter var" kuralı tam_tur.py._defter_var_mi ile AYNI: pipeline-olaylar.jsonl
       boş-değil VEYA pipeline-durum.json mevcut — kapılar arası tutarlılık için)
  (e)  tam_tur.py --durum          → tam tur / delta durumu (BİLGİ; engel SAYILMAZ)
Hepsi geçerse:
  udf_yaz.py --girdi <taslak> --cikti <taslak>.udf  → UDF üret (GERÇEK ve TEK
  yazıcı: npx udf-cli html2udf; rehbere birebir — bkz. GÖREV D, v0.5.5 saha
  bulgusu B5). (--udf-yok ile BİLİNÇLİ atlanabilir — kurucu kural 'varsayılan
  çıktı UDF' bu bayraksız her zaman geçerlidir), "TESLİME HAZIR".

  DÜZELTME (GÖREV D, B5 — KRİTİK): eski `--yerel-motor` (ağsız, hand-rolled
  zip/content.xml) "hızlı yapısal ön-kapı" TAMAMEN KALDIRILDI — saha dosyası A
  sahasında bu motorun ürettiği .udf UYAP editöründe AÇILMADI, ama zincir
  yine de "TESLİME HAZIR" basıyordu (sessiz-yanlış). udf_yaz.py artık BAŞKA
  bir yazma motoru TAŞIMIYOR; bu adım ağ+oturum (`npx -y udf-cli@latest
  login`) GEREKTİRİR. npx/udf-cli yoksa veya oturum gerekiyorsa udf_yaz.py
  FAIL-CLOSED döner (hiçbir .udf yazılmaz) ve bu adım mevcut (rc != 0 → BLOK)
  dalından TESLİMİ DURDURUR — bu KASITLIDIR: bozuk-ama-"üretildi" görünen bir
  UDF, dürüst bir "ağ/oturum eksik" engelinden DAHA KÖTÜDÜR. Avukat
  `--udf-yok` ile bilinçli atlayabilir ya da login yapıp yeniden koşar.

TESLİM MAKBUZU (P0-5, v0.5.5): her koşu `_oa/defter/teslim-makbuz.json` (başarı)
ya da `teslim-makbuz-RED.json` (başarısız deneme — İZLİDİR, kaybolmaz) ATOMİK
yazar: {zaman, taslak_yol, taslak_sha256, tip, taraf, kapilar:[{ad,durum,exit}],
exit_kodu, udf_yolu, udf_atlandi_istekle, ictihat_muhakeme_kanali, surum,
kismi_ingest:{n,m}|None (P1-9 KUCUK-düzeltme — kök yalnız --onbakis'tan geçmişse
GÖRÜNÜR kalır, ad ne olursa olsun)}. Kapı
başına durum ENUM'u {OK, BLOK, ATLA, BILGI} — pipeline_kayit.py'nin adım-9
önkoşul kapısı VE --denetle'nin makbuz denetimi bu dosyayı okur.

Alt scriptler bu scriptin __file__ konumundan GÖRELİ keşfedilir
(../../<skill>/scripts/...); bulunamazsa `OA_SKILLS_KOK` ortam değişkeni
fallback denenir (P0-5(b) path-fix). "Script bulunamadı/çalıştırılamadı" artık
FAIL-CLOSED'dır (P0-5 DÜZELTME d): bir ENGELLEYİCİ kapı için bu, BLOK ile
EŞDEĞERDİR (sessizce atlanıp zincire devam EDİLMEZ) — yalnız (e) (BİLGİ kapısı)
bu kuraldan muaftır.

Not: alt scriptler başka ajanlarca güncelleniyor olabilir; bu zincir yalnız
DOSYA-YOLU + TEMEL argümanlarla çağırır, opsiyonel yeni bayraklara güvenmez.

Kullanım (Windows/PowerShell — 'python'):
  python teslim_paketi.py <taslak.md> --tip <tip> --taraf <taraf> [--dis-arac] [--kok <klasör>] [--udf-yok]
    --tip   : dava|cevap|istinaf|temyiz|aym_bireysel|yemin|idari-kanal|genel
              (dilekce_denetim'e VE ictihat_muhakeme_denetim'e geçer)
    --taraf : davaci|davali|sanik|katilan|mudahil            (boş bırakılabilir)
    --dis-arac : çıktı dış araca (web/bulut/e-posta) gidecekse Layer 0 taramasını ekler
    --kok   : çalışma kökü; _oa/... göreli yolları buradan çözülür (varsayılan: bulunulan klasör)
    --udf-yok : kurucu kural 'varsayılan çıktı UDF'yi BİLİNÇLİ atla (makbuza yazılır)

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
import datetime
import hashlib
import importlib.util
import json
import os
import subprocess
import sys

# ── Alt script keşfi: __file__ (.../skills/oa-kontrol/scripts/) → .../skills ──
BURA = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.abspath(os.path.join(BURA, "..", ".."))


def _script(skill, ad):
    """Alt script yolunu döndürür: ÖNCE __file__-göreli konumu dener, o
    yoksa `OA_SKILLS_KOK` ortam değişkeni fallback'ini kullanır (P0-5(b)
    path-fix — v0.5.1'in 'path sorunuyla atlandı, alt-kapılar elden
    koşturuldu' nüksünü kapatır). Hiçbiri yoksa __file__-göreli yol (bulunamadı
    hâliyle) döner; `_script_denenen` HATA mesajı için TÜM denenen yolları
    verir."""
    goreli = os.path.join(SKILLS, skill, "scripts", ad)
    if os.path.isfile(goreli):
        return goreli
    kok_env = os.environ.get("OA_SKILLS_KOK")
    if kok_env:
        alt = os.path.join(kok_env, skill, "scripts", ad)
        if os.path.isfile(alt):
            return alt
    return goreli


def _script_denenen(skill, ad):
    """Hata mesajında TAM YOLLARI göstermek için — bulunamayan bir scriptin
    hangi konumlarda arandığı asla belirsiz kalmasın."""
    yollar = [os.path.join(SKILLS, skill, "scripts", ad)]
    kok_env = os.environ.get("OA_SKILLS_KOK")
    if kok_env:
        yollar.append(os.path.join(kok_env, skill, "scripts", ad))
    return yollar


S_DILEKCE = ("oa-dilekce", "dilekce_denetim.py")            # (a)
S_KUNYE = ("oa-kontrol", "kunye_teyit.py")                  # (b)
S_ICTIHAT_MUHAKEME = ("oa-kontrol", "ictihat_muhakeme_denetim.py")  # (b2)
S_GIZLILIK = ("oa-gizlilik", "gizlilik_tara.py")            # (c)
S_TAMTUR = ("oa-pipeline", "tam_tur.py")                    # (e)
S_UDF = ("oa-dilekce", "udf_yaz.py")                        # (+)

CIZGI = "=" * 66
ALT = "-" * 66


def _kos(skill_ad, arglar, kok):
    """`(skill, ad)` çiftini `_script()` ile çözüp çalıştıran interpreter ile
    ('python' = sys.executable) koşar. (bulundu, returncode, birlesik_cikti)
    döndürür. cwd=kok: alt scriptlerin _oa/... göreli varsayılanları çalışma
    kökünden çözülsün diye. Bulunamazsa TÜM denenen TAM YOLLARI çıktıya yazar
    (P0-5(b) — 'script bulunamadı' asla belirsiz kalmaz)."""
    skill, ad = skill_ad
    script_yolu = _script(skill, ad)
    if not os.path.isfile(script_yolu):
        denenen = _script_denenen(skill, ad)
        return False, None, "denenen yollar:\n" + "\n".join(f"      - {y}" for y in denenen)
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


def _sha256_dosya(yol):
    h = hashlib.sha256()
    try:
        with open(yol, "rb") as f:
            for blok in iter(lambda: f.read(65536), b""):
                h.update(blok)
    except OSError:
        return None
    return h.hexdigest()


# ── P0-5 (v0.5.5) — pipeline_kayit.py İN-PROCESS import (dairesel bağımlılık
# kırıcı, P0-4'ün tasarım kuralıyla simetrik: 'kapı başka kapıyı subprocess
# ile çağırmaz'). (d) adımı artık `sys.executable pipeline_kayit.py --denetle`
# subprocess'i KOŞTURMAK YERİNE `denetle_calistir(kok, makbuz_kontrolu=False)`
# çağırır — makbuz bütünlüğü kontrolü (d)'nin AMACI DEĞİLDİR (defter boşluğu
# amacı), zaten teslim_paketi'nin KENDİSİ zincirin SONUNDA makbuzu üretir;
# aksi hâlde kendi üreteceği makbuzun YOKLUĞU yüzünden kendine engel koyan
# bir döngü doğar (yaz→denetle→yaz — fiziksel olarak imkânsız önkoşul).
_PIPELINE_KAYIT_MOD = None


def _pipeline_kayit_modulu():
    global _PIPELINE_KAYIT_MOD
    if _PIPELINE_KAYIT_MOD is not None:
        return _PIPELINE_KAYIT_MOD
    betik = _script("oa-pipeline", "pipeline_kayit.py")
    if not os.path.isfile(betik):
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            "_oa_teslim_paketi_pipeline_kayit_inproc", betik)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"UYARI: pipeline_kayit.py import edilemedi ({e}) — tam yol: {betik}")
        return None
    _PIPELINE_KAYIT_MOD = mod
    return _PIPELINE_KAYIT_MOD


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


def _kapi(skill_ad, arglar, kok, engelleyici=True):
    """Bir kapıyı çalıştırıp raporlar. Döndürür: 'ATLA' | 'OK' | 'BLOK' | 'BILGI', rc.

    P0-5 DÜZELTME (d) — "script bulunamadı" = KAPI KAPALI (fail-closed): bir
    ENGELLEYİCİ kapının scripti bulunamaz/çalıştırılamazsa artık sessizce
    devam EDİLMEZ — ATLA, BLOK ile EŞDEĞER muamele görür (rc=None, çağıran
    tarafta zincir orada durur). Yalnız BİLGİ kapıları (`engelleyici=False`)
    bu kuraldan MUAFTIR (zaten hiçbir zaman teslimi durdurmuyorlardı)."""
    bulundu, rc, cikti = _kos(skill_ad, arglar, kok)
    if not bulundu:
        _alt_cikti_yaz(cikti)
        if not engelleyici:
            print("    [ATLA] script yok — bilgi kapısı olduğundan teslim engeli SAYILMAZ.")
            return "ATLA", rc
        print("    [ATLA→BLOK] script bulunamadı — FAIL-CLOSED: kapı KAPALI sayılır "
              "(sessiz atlama yok).")
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


def _kismi_ingest_alani(kok):
    """P1-9 KUCUK-DÜZELTME (sinav bulgusu) — makbuza `kismi_ingest` alanını
    pipeline_kayit._kismi_ingest_durumu (TEK KAYNAK) üzerinden ekler: kısmi
    (--onbakis) bir taramadan geçilmiş bir kökte teslim denemesi/başarısı,
    ad ne olursa olsun makbuzda GÖRÜNÜR kalır. pk yüklenemezse `None` (sessiz
    varsayım YOK, alan makbuzda yok/None kalır)."""
    pk = _pipeline_kayit_modulu()
    if pk is None or not hasattr(pk, "_kismi_ingest_durumu"):
        return None
    try:
        kismi, n, m = pk._kismi_ingest_durumu(kok)
    except Exception:
        return None
    if not kismi:
        return None
    return {"n": n, "m": m}


OA_SURUM = "0.5.7.4"  # P0-5 — makbuz şemasındaki olay-bazlı sürüm damgası


def _makbuz_yaz(kok, veri, basarili):
    """P0-5(a) — _oa/defter/teslim-makbuz.json (başarı) ya da teslim-makbuz-
    RED.json (başarısız deneme) ATOMİK yazılır. Başarısız denemeler de İZLİDİR
    (T2) — sessizce kaybolmaz, bir SONRAKİ denetim ('adım-9 UYGULANDI ama
    makbuz RED') bunu görür."""
    defter = os.path.join(kok, "_oa", "defter")
    os.makedirs(defter, exist_ok=True)
    ad = "teslim-makbuz.json" if basarili else "teslim-makbuz-RED.json"
    hedef = os.path.join(defter, ad)
    tmp = f"{hedef}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)
    os.replace(tmp, hedef)
    # Görev A (B2 kapanışı, v0.5.5 devamı) — DURUM.md üretimi artık YALNIZ
    # pipeline_kayit.py'nin --isle/--katman çağrısına bağlı DEĞİLDİR:
    # teslim_paketi.py de HER makbuz (başarılı/RED) yazımından sonra TEK
    # KAYNAKTAN (pipeline_kayit._durum_md_yaz) DURUM.md'yi tazeler. Defter bu
    # kökte hiç açılmamışsa sessizce no-op — best-effort, ASLA çökmez/bloklamaz.
    pk = _pipeline_kayit_modulu()
    if pk is not None and hasattr(pk, "_durum_md_yaz"):
        try:
            pk._durum_md_yaz(kok)
        except Exception:
            pass
    return hedef


def main():
    ap = argparse.ArgumentParser(
        description="oa-kontrol tek komut teslim zinciri — ilk engelde durur, tek rapor basar.")
    ap.add_argument("taslak", help="Teslim edilecek taslak (.md/.txt)")
    ap.add_argument("--tip", default="genel",
                    help="dilekçe tipi (dava|cevap|istinaf|temyiz|aym_bireysel|yemin|"
                         "idari-kanal|genel); dilekce_denetim.py'ye VE "
                         "ictihat_muhakeme_denetim.py'ye geçer (varsayılan: genel)")
    ap.add_argument("--taraf", default="",
                    choices=["", "davaci", "davali", "sanik", "katilan", "mudahil"],
                    help="taraf sıfatı (müvekkil-aleyhi taraması için); boş bırakılabilir")
    ap.add_argument("--dis-arac", action="store_true",
                    help="çıktı dış araca gidecekse Privacy Layer 0 (gizlilik_tara) kapısını ekle")
    ap.add_argument("--kok", default=".",
                    help="çalışma kökü; _oa/... göreli yolları buradan çözülür (varsayılan: .)")
    ap.add_argument("--udf-yok", action="store_true", dest="udf_yok",
                    help="P0-5(c): kurucu kural 'varsayılan çıktı UDF'yi BİLİNÇLİ olarak "
                         "atla — bu tercih makbuza yazılır (varsayılan: UDF ÜRETİLİR).")
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

    gecen = []           # açılan (OK) kapılar
    atlanan = []         # script bulunamadığı için atlanan (fail-closed) kapılar
    kapanan = None       # ilk kapanan kapı: (ad, rc)
    kapilar_makbuz = []  # P0-5(a) — makbuz şeması: [{"ad","durum","exit"}, ...]

    # ── (a) dilekçe denetimi — zorunlu unsur + müvekkil-aleyhi ──────────────
    # P1-7 çift-[F] tekilleştirme (P0-5 DÜZELTME c, sinav-turu ile SIKILAŞTIRILDI):
    # bu çağrıya BİLİNÇLİ olarak `--ictihat-muhakeme` GEÇİLMEZ VE ayrıca AÇIKÇA
    # `--ictihat-muhakeme-yok` geçilir — İçtihat Muhakeme Zinciri kapısı YALNIZ
    # (b2)'de (aşağıda) çalışır; tek yetkili yol (b2)'dir, bu tercih makbuza
    # `ictihat_muhakeme_kanali` alanıyla yazılır. `--ictihat-muhakeme-yok` AÇIK
    # override'dır: dilekce_denetim.py'nin `--ictihat-muhakeme` VARSAYILANI
    # ileride (P1-7 ile) AÇIK'a çevrilse dahi bu çağrı [F]'yi HER KOŞULDA kapalı
    # tutar — yalnız "bayrağı geçmemek" örtük varsayılana güvenmek, o varsayılan
    # değiştiğinde çift-[F] koşumunu SESSİZCE geri getirirdi.
    # YENİ-2 (Paket D DÜZELTME) — `--kok` AÇIKÇA geçilir: [G] kapısının
    # `_antitez_matris_dosyalari` (dilekce_denetim.py) çağrısı `a.kok`a bakar;
    # bu argüman eksikse kapı CWD'ye örtük güvenmek ZORUNDA kalırdı — `_kos`
    # zaten `cwd=kok` veriyor olsa da, kök AÇIK parametreye dayanmalı (tek
    # başına CWD'ye güvenmek doğrudan-CLI kullanımını açıkta bırakırdı).
    _bolum("[a] DİLEKÇE DENETİMİ — zorunlu unsur + müvekkil-aleyhi  (dilekce_denetim.py)")
    arglar_a = ([taslak, "--tip", a.tip, "--kok", kok]
                + (["--taraf", a.taraf] if a.taraf else [])
                + ["--ictihat-muhakeme-yok"])
    sonuc, rc = _kapi(S_DILEKCE, arglar_a, kok)
    kapilar_makbuz.append({"ad": "(a) DİLEKÇE DENETİMİ", "durum": sonuc, "exit": rc})
    if sonuc == "ATLA":
        atlanan.append("(a) dilekce_denetim.py")
        kapanan = ("(a) DİLEKÇE DENETİMİ", rc)
    elif sonuc == "BLOK":
        kapanan = ("(a) DİLEKÇE DENETİMİ", rc)
    elif sonuc == "OK":
        gecen.append("(a) dilekçe denetimi")

    # ── (b) atıf/künye izi ─────────────────────────────────────────────────
    if kapanan is None:
        _bolum("[b] ATIF/KÜNYE DOĞRULAMA — teyitsiz atıf teslim engeli  (kunye_teyit.py)")
        sonuc, rc = _kapi(S_KUNYE, [taslak], kok)
        kapilar_makbuz.append({"ad": "(b) ATIF/KÜNYE DOĞRULAMA", "durum": sonuc, "exit": rc})
        if sonuc == "ATLA":
            atlanan.append("(b) kunye_teyit.py")
            kapanan = ("(b) ATIF/KÜNYE DOĞRULAMA", rc)
        elif sonuc == "BLOK":
            kapanan = ("(b) ATIF/KÜNYE DOĞRULAMA", rc)
        elif sonuc == "OK":
            gecen.append("(b) atıf/künye")

    # ── (b2) İçtihat Muhakeme Zinciri — çıplak/ALEYHE/eksik-alanlı atıf ─────
    if kapanan is None:
        _bolum("[b2] İÇTİHAT MUHAKEME ZİNCİRİ — çıplak/ALEYHE/eksik-alanlı atıf "
               "(ictihat_muhakeme_denetim.py)")
        sonuc, rc = _kapi(S_ICTIHAT_MUHAKEME, [taslak, "--kok", kok, "--tip", a.tip], kok)
        kapilar_makbuz.append({"ad": "(b2) İÇTİHAT MUHAKEME ZİNCİRİ", "durum": sonuc, "exit": rc})
        if sonuc == "ATLA":
            atlanan.append("(b2) ictihat_muhakeme_denetim.py")
            kapanan = ("(b2) İÇTİHAT MUHAKEME ZİNCİRİ", rc)
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
            kapilar_makbuz.append({"ad": "(c) GİZLİLİK / LAYER 0", "durum": "BILGI", "exit": None})
        else:
            sonuc, rc = _kapi(S_GIZLILIK, [taslak], kok)
            kapilar_makbuz.append({"ad": "(c) GİZLİLİK / LAYER 0", "durum": sonuc, "exit": rc})
            if sonuc == "ATLA":
                atlanan.append("(c) gizlilik_tara.py")
                kapanan = ("(c) GİZLİLİK / LAYER 0", rc)
            elif sonuc == "BLOK":
                kapanan = ("(c) GİZLİLİK / LAYER 0", rc)
            elif sonuc == "OK":
                gecen.append("(c) gizlilik/Layer 0")

    # ── (d) pipeline defter boşluğu — yalnız defter varsa ──────────────────
    # P0-5 dairesel-bağımlılık kırıcı: İN-PROCESS `denetle_calistir(kok,
    # makbuz_kontrolu=False)` — subprocess YOK; makbuz bütünlüğü kontrolü BU
    # kapının amacı DEĞİLDİR (bkz. _pipeline_kayit_modulu üstü not).
    if kapanan is None:
        _bolum("[d] PİPELİNE DEFTER BOŞLUĞU  (pipeline_kayit.py --denetle, in-process)")
        if not _defter_var_mi(kok):
            print("    [BILGI] pipeline defteri yok (%s)" %
                  os.path.join(kok, "_oa", "defter", "pipeline-olaylar.jsonl"))
            print("            → bu dosya pipeline defteri kullanmıyor; defter denetimi ATLANDI.")
            kapilar_makbuz.append({"ad": "(d) PİPELİNE DEFTER BOŞLUĞU", "durum": "BILGI", "exit": None})
        else:
            pk = _pipeline_kayit_modulu()
            if pk is None:
                print("    [ATLA→BLOK] pipeline_kayit.py import edilemedi — FAIL-CLOSED: "
                      "kapı KAPALI sayılır (sessiz atlama yok).")
                atlanan.append("(d) pipeline_kayit.py")
                kapanan = ("(d) PİPELİNE DEFTER BOŞLUĞU", None)
                kapilar_makbuz.append({"ad": "(d) PİPELİNE DEFTER BOŞLUĞU", "durum": "ATLA", "exit": None})
            else:
                # P0-5×P0-6 dairesel-KİLİT sinav-turu düzeltmesi (BLOKER): (d)
                # kapısı `teslim_oncesi=True` ile de çağrılır — adım-9 (KONTROL) /
                # adım-10 (KAPANIŞ) BEKLIYOR durumu bu kapıda sorun SAYILMAZ
                # (bunlar tanım gereği TAM DA bu kapının üreteceği makbuzla
                # teslimden SONRA kapanır — aksi hâlde (d) hiçbir zaman UYGULANDI
                # adım-9'dan önce açılamaz, adım-9 de makbuzsuz UYGULANDI
                # yazılamayacağından döngü --serh dışında kapanmazdı).
                temiz, cikti = pk.denetle_calistir(kok, makbuz_kontrolu=False,
                                                    teslim_oncesi=True)
                _alt_cikti_yaz(cikti)
                if temiz:
                    print("    [OK] kapı açık (defter boşluksuz).")
                    gecen.append("(d) pipeline defteri")
                    kapilar_makbuz.append({"ad": "(d) PİPELİNE DEFTER BOŞLUĞU", "durum": "OK", "exit": 0})
                else:
                    print("    [BLOK] KAPI KAPALI (defter boşluklu).")
                    kapanan = ("(d) PİPELİNE DEFTER BOŞLUĞU", 1)
                    kapilar_makbuz.append({"ad": "(d) PİPELİNE DEFTER BOŞLUĞU", "durum": "BLOK", "exit": 1})

    # ── (e) tam tur / delta durumu — BİLGİ (engel değil, exit 3 dahil) ──────
    if kapanan is None:
        _bolum("[e] TAM TUR / DELTA DURUMU — BİLGİ (teslim engeli değil)  (tam_tur.py --durum)")
        sonuc, rc = _kapi(S_TAMTUR, ["--durum"], kok, engelleyici=False)
        kapilar_makbuz.append({"ad": "(e) TAM TUR / DELTA DURUMU", "durum": sonuc, "exit": rc})
        if sonuc == "ATLA":
            atlanan.append("(e) tam_tur.py")
        # BILGI / diğer: hiçbir zaman engel değil (exit 3 = tam tur yok/delta bekliyor — sadece bilgi)

    # ── ilk engelde durduysa: RED makbuzu + rapor + çık ─────────────────────
    if kapanan is not None:
        ad, rc = kapanan
        print()
        print(CIZGI)
        print("SONUÇ: TESLİM DURDURULDU — İLK KAPANAN KAPI: %s (exit %s)." % (ad, rc))
        print("Zincir bu noktada durdu; SONRAKİ KAPILAR ÇALIŞTIRILMADI (ilk engelde dur ilkesi).")
        if gecen:
            print("Bu kapıya kadar açılan: " + ", ".join(gecen) + ".")
        if atlanan:
            print("Not — script bulunamadığı/çalıştırılamadığı için (FAIL-CLOSED) BLOK sayılan "
                  "kapı(lar): " + ", ".join(atlanan) + ".")
        print("UDF ÜRETİLMEDİ. Kapanan kapıyı gider ve teslim_paketi'ni yeniden koş.")
        print(CIZGI)
        makbuz_veri = {
            "zaman": datetime.datetime.now().isoformat(timespec="seconds"),
            "taslak_yol": taslak, "taslak_sha256": _sha256_dosya(taslak),
            "tip": a.tip, "taraf": a.taraf or None,
            "kapilar": kapilar_makbuz, "exit_kodu": 1, "udf_yolu": None,
            "udf_atlandi_istekle": bool(a.udf_yok),
            "ictihat_muhakeme_kanali": "b2-tekil", "surum": OA_SURUM,
            "kismi_ingest": _kismi_ingest_alani(kok),
            "durdu": ad,
        }
        _makbuz_yaz(kok, makbuz_veri, basarili=False)
        sys.exit(1)

    # ── tüm engelleyici kapılar açık → UDF üret (--udf-yok verilmedikçe) ────
    udf_cikti = taslak + ".udf"
    udf_uretildi = False
    if a.udf_yok:
        _bolum("[+] UDF ÜRETİMİ — ATLANDI (--udf-yok BİLİNÇLİ istekle)")
        print("    [BILGI] --udf-yok verildi; UDF üretimi kullanıcı isteğiyle atlandı "
              "(kurucu kural 'varsayılan çıktı UDF' bilinçli olarak devre dışı — makbuza yazıldı).")
        kapilar_makbuz.append({"ad": "(+) UDF ÜRETİMİ", "durum": "BILGI", "exit": None})
    else:
        _bolum("[+] UDF ÜRETİMİ — udf_yaz.py --girdi <taslak> --cikti <taslak>.udf")
        print("    [BILGI] GERÇEK UYAP yazıcısı çağrılıyor (npx udf-cli html2udf, "
              "rehbere birebir) — ağ + oturum gerektirir. `--yerel-motor` KALDIRILDI "
              "(B5 saha bulgusu: o motorun ürettiği .udf UYAP'ta açılmıyordu); "
              "npx/oturum yoksa bu adım FAIL-CLOSED BLOK olur (bkz. oa-dilekce/"
              "scripts/udf_yaz.py, 'npx -y udf-cli@latest login').")
        bulundu, rc, cikti = _kos(
            S_UDF, ["--girdi", taslak, "--cikti", udf_cikti], kok)
        if not bulundu:
            _alt_cikti_yaz(cikti)
            print("    [ATLA→BLOK] script bulunamadı — FAIL-CLOSED: UDF üretilemedi "
                  "(kurucu kural: varsayılan çıktı UDF; atlamak için --udf-yok kullan).")
            atlanan.append("(+) udf_yaz.py")
            kapilar_makbuz.append({"ad": "(+) UDF ÜRETİMİ", "durum": "ATLA", "exit": None})
            print()
            print(CIZGI)
            print("SONUÇ: TÜM KAPILAR AÇIK ama UDF ÜRETİLEMEDİ (script bulunamadı) — "
                  "kurucu kural gereği bu bir TESLİM ENGELİDİR.")
            if atlanan:
                print("Not — atlanan kapı(lar): " + ", ".join(atlanan) + ".")
            print(CIZGI)
            makbuz_veri = {
                "zaman": datetime.datetime.now().isoformat(timespec="seconds"),
                "taslak_yol": taslak, "taslak_sha256": _sha256_dosya(taslak),
                "tip": a.tip, "taraf": a.taraf or None,
                "kapilar": kapilar_makbuz, "exit_kodu": 1, "udf_yolu": None,
                "udf_atlandi_istekle": False,
                "ictihat_muhakeme_kanali": "b2-tekil", "surum": OA_SURUM,
                "kismi_ingest": _kismi_ingest_alani(kok),
                "durdu": "(+) UDF ÜRETİMİ",
            }
            _makbuz_yaz(kok, makbuz_veri, basarili=False)
            sys.exit(1)
        _alt_cikti_yaz(cikti)
        if rc != 0:
            print("    [BLOK] UDF üretimi başarısız (exit %s)." % rc)
            kapilar_makbuz.append({"ad": "(+) UDF ÜRETİMİ", "durum": "BLOK", "exit": rc})
            print()
            print(CIZGI)
            print("SONUÇ: TÜM KAPILAR AÇIK ama UDF ÜRETİLEMEDİ — udf_yaz.py çıktısına bak.")
            if atlanan:
                print("Not — atlanan kapı(lar): " + ", ".join(atlanan) + ".")
            print(CIZGI)
            makbuz_veri = {
                "zaman": datetime.datetime.now().isoformat(timespec="seconds"),
                "taslak_yol": taslak, "taslak_sha256": _sha256_dosya(taslak),
                "tip": a.tip, "taraf": a.taraf or None,
                "kapilar": kapilar_makbuz, "exit_kodu": 1, "udf_yolu": None,
                "udf_atlandi_istekle": False,
                "ictihat_muhakeme_kanali": "b2-tekil", "surum": OA_SURUM,
                "kismi_ingest": _kismi_ingest_alani(kok),
                "durdu": "(+) UDF ÜRETİMİ",
            }
            _makbuz_yaz(kok, makbuz_veri, basarili=False)
            sys.exit(1)
        udf_uretildi = os.path.isfile(udf_cikti)
        kapilar_makbuz.append({"ad": "(+) UDF ÜRETİMİ", "durum": "OK", "exit": rc})
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
    elif a.udf_yok:
        print("   - UDF    : (üretilmedi — --udf-yok istekle)")
    else:
        print("   - UDF    : (üretilemedi — udf_yaz.py yok/atlandı)")
    if atlanan:
        print("UYARI — script bulunamadığı için ATLANAN kapı(lar): " + ", ".join(atlanan) + ".")
        print("        Bu kapılar DENETLENMEDİ; teslimden önce elle doğrula (sessiz geçilmedi).")
    print("Not: bu zincir mekanik kapıların açık olduğunu gösterir; içerik/esas doğruluğu ve")
    print("     nihai göz AVUKATINDIR (oa-kontrol A-listesi muhakeme işidir).")

    makbuz_veri = {
        "zaman": datetime.datetime.now().isoformat(timespec="seconds"),
        "taslak_yol": taslak, "taslak_sha256": _sha256_dosya(taslak),
        "tip": a.tip, "taraf": a.taraf or None,
        "kapilar": kapilar_makbuz, "exit_kodu": 0,
        "udf_yolu": (udf_cikti if udf_uretildi else None),
        "udf_atlandi_istekle": bool(a.udf_yok),
        "ictihat_muhakeme_kanali": "b2-tekil", "surum": OA_SURUM,
        "kismi_ingest": _kismi_ingest_alani(kok),
        "durdu": None,
    }
    makbuz_yolu = _makbuz_yaz(kok, makbuz_veri, basarili=True)
    print("TESLİM MAKBUZU  : %s" % makbuz_yolu)
    sys.exit(0)


if __name__ == "__main__":
    main()

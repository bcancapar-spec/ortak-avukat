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

v0.5.8.4 (372 Torbalı saha devşirmesi): (1) UDF üretiminden ÖNCE mevcut aday
.udf DEVRALINIR (hafif geçerlilik süzgeciyle; geçersiz elle-üretim adayı
karantinaya taşınır) — çift-UDF tuzağı kapandı; (2) makbuz try/finally
GARANTİSİNDE — erken çıkışlar dahil her başarısız yol RED makbuzu düşürür;
(3) teslim edilecek UDF için PROV-TAZELİK + YEREL-DAMGA + ŞEKİL (kenar 42.52)
kapıları ve OTOMATİK mühürleme (mühürsüz teslim fiziksel imkânsız);
(4) tazelik_denetim.py advisory olarak zincire bağlı (makbuzda
`tazelik_uyarilari`). Ayrıntı: aşağıda GÖREV 1-6 blok yorumu.

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
import re
import shutil
import subprocess
import sys
import zipfile

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


# ════════════════════════════════════════════════════════════════════════════
# v0.5.8.4 — 372 Torbalı saha derslerinin mekanik karşılığı (GÖREV 1-6):
#   1) MEVCUT-UDF DEVRALMA: üretimden ÖNCE aday .udf aranır — çift-UDF tuzağı
#      (372: koşu kendi ürettiği ikinci .udf'i kendisi karantinaya almıştı).
#   2) MAKBUZ GARANTİSİ: try/finally — erken çıkışlar dahil HER başarısız yol
#      RED makbuzu düşürür (372: makbuz hiç üretilmedi, model zinciri atladı).
#   3) PROV-TAZELİK + otomatik mühür: mühürsüz teslim fiziksel imkânsız
#      (372: Stop hook 23 kez MÜHÜRSÜZ uyardı, model 0 kez uyguladı).
#   4) YEREL-DAMGA KAPISI: yerel-motor ürünü teslime giremez (A/B hükmü:
#      suçlu yerel motorun content.xml'i — stil tanımsız hvl-default).
#   5) ŞEKİL KAPISI: pageFormat 4 kenar 42.52 pt değilse udf_yaz'ın GERÇEK
#      yamasıyla düzeltilir (AB3 tanığı: yamalı dosya UYAP'ta açıldı) ve
#      mühür sha'sı GÜNCELLENİR; LineSpacing/11pt yalnız İSTİŞARİ.
#   6) TAZELİK BİLGİ KAPISI: tazelik_denetim.py advisory — BAYAT satırları
#      makbuza `tazelik_uyarilari` olarak geçer, kapı KAPATMAZ.
# ════════════════════════════════════════════════════════════════════════════

# GÖREV 2 — makbuz garantisi durum kaydı: _makbuz_yaz her yazımda işaretler;
# main()'in finally kolu, başarısız çıkışta hiç makbuz yazılmamışsa erken-RED
# makbuzu düşürür (zaman + sebep + argv).
_MAKBUZ_DURUM = {"yazildi": False, "kok": None, "sebep": None}

# 372 A/B hükmünün imzası: yerel motor <elements resolver="hvl-default"> yazar
# ama styles bloğunda name="hvl-default" STİL TANIMI yoktur → UYAP'ta açılmaz.
# (`<style\b` — `<styles>` etiketine YANLIŞ eşleşmez.)
_HVL_STIL_RE = re.compile(r'<style\b[^>]*name="hvl-default"')

# udf_yaz._KENAR_PT yüklenemezse yedek (tek kaynak udf_yaz'dır; bu yalnız
# fail-durumu yedeğidir — Yönetmelik No. 2646 m.8, 1,5 cm).
_KENAR_PT_YEDEK = "42.52"


def _argv_kok_tahmini(argv=None):
    """Erken-RED makbuzu için kök tahmini: argparse'a hiç ulaşılamamış olsa
    bile sys.argv'den `--kok` değerini söker; bulunamazsa '.' döner."""
    argv = list(sys.argv[1:] if argv is None else argv)
    for i, s in enumerate(argv):
        if s == "--kok" and i + 1 < len(argv):
            return argv[i + 1]
        if s.startswith("--kok="):
            return s.split("=", 1)[1]
    return "."


def _modul_yukle(skill, ad, takma):
    """Kardeş scripti importlib ile İN-PROCESS yükler (P0-4 ilkesi: kapı
    kapıyı subprocess ile çağırmaz). Yüklenemezse None (çağıran fail-closed
    karar verir)."""
    betik = _script(skill, ad)
    if not os.path.isfile(betik):
        return None
    try:
        spec = importlib.util.spec_from_file_location(takma, betik)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        print("UYARI: %s import edilemedi (%s) — tam yol: %s" % (ad, e, betik))
        return None


def _muhur_modulu():
    return _modul_yukle("oa-kontrol", "muhur_yaz.py", "_oa_tp_muhur_yaz_inproc")


def _udf_yaz_modulu():
    return _modul_yukle("oa-dilekce", "udf_yaz.py", "_oa_tp_udf_yaz_inproc")


def _udf_content_xml(yol):
    """UDF zip'inden content.xml metnini döndürür; açılamazsa/yoksa None."""
    try:
        with zipfile.ZipFile(yol) as z:
            if "content.xml" not in z.namelist():
                return None
            return z.read("content.xml").decode("utf-8", "replace")
    except Exception:
        return None


def _udf_hafif_gecerli_mi(yol):
    """GÖREV 1 — hafif geçerlilik süzgeci: (gecerli, sebep).
    zip açılıyor + content.xml var + styles içinde name="hvl-default" STİL
    TANIMI var. Stil tanımı yoksa bu, 372 A/B testinin akladığı zip/yama
    değil, SUÇLU bulunan yerel-motor content.xml imzasıdır."""
    xml = _udf_content_xml(yol)
    if xml is None:
        return False, "zip açılamadı ya da content.xml yok"
    if not _HVL_STIL_RE.search(xml):
        return False, ('styles içinde name="hvl-default" stil tanımı YOK — '
                       "elle-üretim imzası (372: bu dosyalar UYAP'ta açılmıyor)")
    return True, "hafif geçerlilik geçti"


def _udf_adaylari(taslak, kok):
    """GÖREV 1 — üretimden ÖNCE devralınabilir .udf adayları, SABİT sırayla:
      (1) <taslak-kök>.udf   (2) <taslak>.udf
      (3) _oa/cikti altında taslakla aynı kök-adlı .udf'ler (alt klasörler
          dahil — Ş9 alt-klasör körlüğü dersi burada da geçerli)."""
    adaylar = []
    for y in (os.path.splitext(taslak)[0] + ".udf", taslak + ".udf"):
        y = os.path.abspath(y)
        if os.path.isfile(y) and y not in adaylar:
            adaylar.append(y)
    kok_ad = os.path.basename(taslak).split(".")[0]
    cikti_dizin = os.path.join(kok, "_oa", "cikti")
    if os.path.isdir(cikti_dizin):
        for dizin, _altlar, adlar in os.walk(cikti_dizin):
            for ad in sorted(adlar):
                if not ad.lower().endswith(".udf"):
                    continue
                if ad.split(".")[0] != kok_ad:
                    continue
                y = os.path.abspath(os.path.join(dizin, ad))
                if os.path.isfile(y) and y not in adaylar:
                    adaylar.append(y)
    return adaylar


def _karantinaya_tasi(kok, yol):
    """GÖREV 1 — geçersiz adayı _oa/arsiv-yerel/gecersiz-elle-udf/ altına
    zaman damgalı adla taşır (SİLMEZ — kayıpsızlık invaryantı); yanındaki
    .prov.json varsa çifti ayırmadan birlikte taşır. Hedef yolu döndürür."""
    hedef_dizin = os.path.join(kok, "_oa", "arsiv-yerel", "gecersiz-elle-udf")
    os.makedirs(hedef_dizin, exist_ok=True)
    damga = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    hedef = os.path.join(hedef_dizin, "%s-%s" % (damga, os.path.basename(yol)))
    shutil.move(yol, hedef)
    prov = yol + ".prov.json"
    if os.path.isfile(prov):
        shutil.move(prov, hedef + ".prov.json")
    return hedef


def _kenarlar_uygun_mu(xml, kenar_pt):
    """GÖREV 5 — content.xml pageFormat'ında DÖRT kenar da kenar_pt mi?"""
    m = re.search(r"<pageFormat[^>]*>", xml or "")
    if not m:
        return False
    etiket = m.group(0)
    for ad in ("leftMargin", "rightMargin", "topMargin", "bottomMargin"):
        deger = re.search(ad + r'="([0-9.]+)"', etiket)
        if not deger or deger.group(1) != kenar_pt:
            return False
    return True


def _sekil_istisari_uyarilar(xml):
    """GÖREV 5 (istişari kol) — KAPI KAPATMAZ, yalnız satır basılır:
    gövdede LineSpacing="0.50" (1,5 satır) yaygınlığı + link için 11pt imzası
    (372 saha standardı). Sert ölçüt DEĞİLDİR — v0.5.5 dersi: yanlış katmanı
    sertleştirme."""
    uyarilar = []
    p_toplam = xml.count("<paragraph")
    p_15 = xml.count('LineSpacing="0.50"')
    if p_toplam and p_15 * 2 < p_toplam:
        uyarilar.append('gövdede LineSpacing="0.50" (1,5 satır) yaygın değil '
                        "(%d/%d paragraf) — şekil standardı v2 önerisi"
                        % (p_15, p_toplam))
    if "http" in xml and 'size="11"' not in xml:
        uyarilar.append('bağlantı (link) metni için 11pt (size="11") imzası '
                        "görünmüyor — saha standardı önerisi")
    return uyarilar


def _tazelik_uyarilari_topla(kok):
    """GÖREV 6 — tazelik_denetim.py --json advisory koşusu: BAYAT/EKSİK
    satırları liste olarak döner (makbuza `tazelik_uyarilari` girer), HİÇBİR
    koşulda bloklamaz. Script yok / çıktı çözülemedi → None (sessiz varsayım
    yok; alan makbuzda None kalır)."""
    bulundu, rc, cikti = _kos(("oa-kontrol", "tazelik_denetim.py"),
                              ["--kok", kok, "--json"], kok)
    if not bulundu or rc is None:
        return None
    try:
        satir = next(s for s in (cikti or "").splitlines()
                     if s.strip().startswith("{"))
        rapor = json.loads(satir)
    except Exception:
        return None
    uyarilar = []
    for b in rapor.get("bayat") or []:
        uyarilar.append("BAYAT: %s — kaynağı %s üretiminden sonra değişti "
                        "(%s → %s); delta geçişi gerek"
                        % (b.get("urun"), b.get("kaynak"),
                           b.get("beyan"), b.get("simdiki")))
    for e in rapor.get("eksik") or []:
        uyarilar.append("EKSİK-KAYNAK: %s — beyan edilen %s bulunamadı/kök dışında"
                        % (e.get("urun"), e.get("kaynak")))
    return uyarilar


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


OA_SURUM = "0.5.8.4"  # P0-5 — makbuz şemasındaki olay-bazlı sürüm damgası


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
    _MAKBUZ_DURUM["yazildi"] = True  # GÖREV 2 — garanti kolu ikinci kez yazmasın
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


def _makbuz_taban(a, taslak, kok, kapilar, exit_kodu, udf_yolu, durdu,
                  sebep=None, ekstra=None):
    """Makbuz gövdesinin TEK üreticisi (v0.5.8.4 — beş ayrı el-yazımı dict'in
    tekilleştirilmesi): şema alanları her yolda aynı kalır; `sebep` ve `argv`
    GÖREV 2 gereği eklenir, `ekstra` başarı yoluna özgü alanları taşır."""
    veri = {
        "zaman": datetime.datetime.now().isoformat(timespec="seconds"),
        "taslak_yol": taslak, "taslak_sha256": _sha256_dosya(taslak),
        "tip": a.tip, "taraf": a.taraf or None,
        "kapilar": kapilar, "exit_kodu": exit_kodu, "udf_yolu": udf_yolu,
        "udf_atlandi_istekle": bool(a.udf_yok),
        "ictihat_muhakeme_kanali": "b2-tekil", "surum": OA_SURUM,
        "kismi_ingest": _kismi_ingest_alani(kok),
        "durdu": durdu,
        "argv": sys.argv[1:],
    }
    if sebep is not None:
        veri["sebep"] = sebep
    if ekstra:
        veri.update(ekstra)
    return veri


def _erken_red_makbuz(exit_kodu):
    """GÖREV 2 — MAKBUZ GARANTİSİ emniyet kolu: zincir makbuz yazamadan ölen
    HER başarısız çıkış (taslak yok, kök yok, argparse hatası, beklenmeyen
    çökme) için RED makbuzu düşer (zaman + sebep + argv). Bu emniyet yazımı
    KENDİSİ asla yeni bir çöküş üretmez (best-effort; hook felsefesiyle
    simetrik: emniyet katmanı akışı bloklamaz)."""
    try:
        kok = _MAKBUZ_DURUM.get("kok") or os.path.abspath(_argv_kok_tahmini())
        veri = {
            "zaman": datetime.datetime.now().isoformat(timespec="seconds"),
            "sebep": (_MAKBUZ_DURUM.get("sebep")
                      or "erken çıkış — zincir kapılara ulaşamadan sonlandı"),
            "argv": sys.argv[1:],
            "erken_cikis": True,
            "taslak_yol": None, "taslak_sha256": None, "tip": None, "taraf": None,
            "kapilar": [], "exit_kodu": exit_kodu if isinstance(exit_kodu, int) else 1,
            "udf_yolu": None, "udf_atlandi_istekle": False,
            "ictihat_muhakeme_kanali": "b2-tekil", "surum": OA_SURUM,
            "kismi_ingest": None, "durdu": "(erken çıkış)",
        }
        _makbuz_yaz(kok, veri, basarili=False)
        print("RED MAKBUZU (erken çıkış — makbuz garantisi): "
              "_oa/defter/teslim-makbuz-RED.json", file=sys.stderr)
    except Exception:
        pass


def main():
    """GÖREV 2 — try/finally MAKBUZ GARANTİSİ sarmalayıcısı: `_zincir()` hangi
    yoldan çıkarsa çıksın, başarısız (exit != 0) VE henüz makbuz yazılmamış
    her durumda RED makbuzu düşer. 372 kanıtı: makbuz hiç üretilmedi çünkü
    tek üretici zincirin SONUNDAYDI ve erken çıkışlar makbuzsuz ölüyordu."""
    _MAKBUZ_DURUM["yazildi"] = False
    _MAKBUZ_DURUM["kok"] = None
    _MAKBUZ_DURUM["sebep"] = None
    kod = 0
    try:
        _zincir()
    except SystemExit as e:
        kod = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        raise
    except BaseException as e:
        kod = 1
        if not _MAKBUZ_DURUM.get("sebep"):
            _MAKBUZ_DURUM["sebep"] = "beklenmeyen hata: %r" % (e,)
        raise
    finally:
        if kod != 0 and not _MAKBUZ_DURUM.get("yazildi"):
            _erken_red_makbuz(kod)


def _zincir():
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
    _MAKBUZ_DURUM["kok"] = kok  # GÖREV 2 — erken-RED makbuzunun düşeceği kök

    if not os.path.isfile(taslak):
        _MAKBUZ_DURUM["sebep"] = "taslak bulunamadı: %s" % taslak
        print("HATA: taslak bulunamadı: %s" % taslak, file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(kok):
        _MAKBUZ_DURUM["sebep"] = "kök klasör yok: %s" % kok
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
        _makbuz_yaz(kok, _makbuz_taban(
            a, taslak, kok, kapilar_makbuz, 1, None, ad,
            sebep="kapı kapandı: %s (exit %s)" % (ad, rc)), basarili=False)
        sys.exit(1)

    # ── tüm engelleyici kapılar açık → UDF devralma/üretim (--udf-yok yoksa) ─
    udf_cikti = taslak + ".udf"
    udf_uretildi = False
    udf_devralindi = None    # GÖREV 1 — {"yol","sha256"} | None (makbuza girer)
    kenar_duzeltildi = False  # GÖREV 5 — kenar yaması uygulandı mı (makbuza girer)
    if a.udf_yok:
        _bolum("[+] UDF ÜRETİMİ — ATLANDI (--udf-yok BİLİNÇLİ istekle)")
        print("    [BILGI] --udf-yok verildi; UDF üretimi kullanıcı isteğiyle atlandı "
              "(kurucu kural 'varsayılan çıktı UDF' bilinçli olarak devre dışı — makbuza yazıldı).")
        kapilar_makbuz.append({"ad": "(+) UDF ÜRETİMİ", "durum": "BILGI", "exit": None})
    else:
        # ── GÖREV 1 — MEVCUT-UDF DEVRALMA: üretimden ÖNCE aday ara (372'nin
        # çift-UDF tuzağı: mevcut geçerli .udf dururken koşulsuz ikinci üretim) ──
        _bolum("[+] UDF DEVRALMA — mevcut aday arama (üretimden ÖNCE)")
        for aday in _udf_adaylari(taslak, kok):
            gecerli, aday_sebep = _udf_hafif_gecerli_mi(aday)
            if gecerli:
                udf_cikti = aday
                udf_uretildi = True
                udf_devralindi = {"yol": aday, "sha256": _sha256_dosya(aday)}
                print("    [OK] mevcut UDF DEVRALINDI — yeniden üretim YOK: %s" % aday)
                kapilar_makbuz.append({"ad": "(+) UDF DEVRALMA", "durum": "OK", "exit": 0})
                break
            hedef = _karantinaya_tasi(kok, aday)
            print("    [UYARI] geçersiz aday (%s)" % aday_sebep)
            print("            → karantinaya taşındı (silinmedi): %s" % hedef)
        if udf_devralindi is None:
            print("    [BILGI] devralınabilir geçerli aday yok — taze üretime geçiliyor.")
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
                _makbuz_yaz(kok, _makbuz_taban(
                    a, taslak, kok, kapilar_makbuz, 1, None, "(+) UDF ÜRETİMİ",
                    sebep="udf_yaz.py bulunamadı (FAIL-CLOSED)"), basarili=False)
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
                _makbuz_yaz(kok, _makbuz_taban(
                    a, taslak, kok, kapilar_makbuz, 1, None, "(+) UDF ÜRETİMİ",
                    sebep="udf_yaz.py üretimi başarısız (exit %s)" % rc), basarili=False)
                sys.exit(1)
            udf_uretildi = os.path.isfile(udf_cikti)
            kapilar_makbuz.append({"ad": "(+) UDF ÜRETİMİ", "durum": "OK", "exit": rc})
            print("    [OK] UDF üretildi.")

        # ── GÖREV 3/4/5 — UDF TESLİM KAPILARI: mühür-tazelik → yerel-damga →
        # şekil (kenar 42.52) → mühür üret/güncelle + doğrula. "Üretilen .udf
        # doğrulanmadan YÜKLENMEZ" kuralının mekanik karşılığı. ───────────────
        _bolum("[++] UDF TESLİM KAPILARI — PROV tazelik / yerel-damga / şekil / mühür")

        def _udf_red(durdu_ad, sebep_metni):
            print("    [BLOK] %s" % sebep_metni)
            kapilar_makbuz.append({"ad": durdu_ad, "durum": "BLOK", "exit": 1})
            print()
            print(CIZGI)
            print("SONUÇ: TESLİM DURDURULDU — %s" % sebep_metni)
            print(CIZGI)
            _makbuz_yaz(kok, _makbuz_taban(
                a, taslak, kok, kapilar_makbuz, 1, None, durdu_ad,
                sebep=sebep_metni,
                ekstra={"udf_devralindi": udf_devralindi,
                        "kenar_duzeltildi": kenar_duzeltildi}), basarili=False)
            sys.exit(1)

        # (i) mevcut mühür okunur; YEREL-DAMGA (GÖREV 4) yeniden mühürlemeden
        # ÖNCE denetlenir — aksi hâlde suç delili kendi elimizle silinirdi.
        prov_yolu = udf_cikti + ".prov.json"
        muhur_kaydi = None
        if os.path.isfile(prov_yolu):
            try:
                with open(prov_yolu, encoding="utf-8") as f:
                    muhur_kaydi = json.load(f)
            except Exception as e:
                _udf_red("(+) PROV-TAZELİK",
                         "mühür (.prov.json) OKUNAMADI (%s) — güvenilmez mühürle "
                         "teslim YOK (fail-closed)" % e)
            uretici = str(muhur_kaydi.get("was_generated_by") or "")
            if "yerel" in uretici.lower():
                _udf_red("(+) YEREL-DAMGA",
                         "YEREL-MOTOR ÜRÜNÜ TESLİME GİREMEZ — üretilen .udf "
                         "doğrulanmadan yüklenmez kuralı (372 A/B hükmü: suçlu "
                         "yerel-motor content.xml; was_generated_by=%r)" % uretici)
            # (ii) GÖREV 3 — PROV-TAZELİK: mühürdeki sha güncel sha ile uyuşmalı
            guncel_sha = _sha256_dosya(udf_cikti)
            if muhur_kaydi.get("artifact_sha256") != guncel_sha:
                _udf_red("(+) PROV-TAZELİK",
                         "PROV-BAYAT: mühürdeki sha güncel dosyayla uyuşmuyor "
                         "(mühür %s… ≠ şimdiki %s…) — 372 kanıtı: cikti/10 mührü "
                         "bayat kalmıştı; bayat mühürle teslim YOK"
                         % (str(muhur_kaydi.get("artifact_sha256", "?"))[:12],
                            str(guncel_sha or "?")[:12]))
            print("    [OK] mühür taze (sha uyumlu) ve yerel-damgasız.")
        else:
            print("    [BILGI] mühür yok — şekil kapısından sonra OTOMATİK "
                  "mühürlenecek (mühürsüz teslim fiziksel olarak imkânsız).")

        # (iii) GÖREV 5 — ŞEKİL KAPISI: pageFormat 4 kenar 42.52 pt (Yönetmelik
        # 2646 m.8); değilse udf_yaz'ın GERÇEK yamasıyla düzeltilir (AB3 tanığı:
        # bu yama UYAP'ta açılan dosya üretir), düzeltilemezse RED.
        uy_mod = _udf_yaz_modulu()
        kenar_pt = getattr(uy_mod, "_KENAR_PT", _KENAR_PT_YEDEK) if uy_mod else _KENAR_PT_YEDEK
        xml = _udf_content_xml(udf_cikti)
        if xml is None:
            _udf_red("(+) ŞEKİL", "content.xml okunamadı — şekil denetimi "
                     "yapılamadı (fail-closed)")
        if not _kenarlar_uygun_mu(xml, kenar_pt):
            kenar_fn = getattr(uy_mod, "_sayfa_kenari_yonetmelik", None) if uy_mod else None
            if kenar_fn is None:
                _udf_red("(+) ŞEKİL", "pageFormat kenarları %s pt değil ve "
                         "udf_yaz._sayfa_kenari_yonetmelik yüklenemedi — "
                         "DÜZELTİLEMEDİ" % kenar_pt)
            print("    [BILGI] %s" % kenar_fn(udf_cikti))
            xml = _udf_content_xml(udf_cikti)
            if xml is None or not _kenarlar_uygun_mu(xml, kenar_pt):
                _udf_red("(+) ŞEKİL", "pageFormat 4 kenar %s pt'ye DÜZELTİLEMEDİ "
                         "— düzeltilemeyen şekil teslime giremez" % kenar_pt)
            kenar_duzeltildi = True
            print("    [OK] kenarlar düzeltildi (4x%s pt) — makbuza yazıldı." % kenar_pt)
        else:
            print("    [OK] pageFormat 4 kenar %s pt (Yönetmelik 2646 m.8)." % kenar_pt)
        for istisari in _sekil_istisari_uyarilar(xml):
            print("    [İSTİŞARİ] %s (kapı KAPATMAZ)" % istisari)

        # (iv) GÖREV 3 devamı — MÜHÜR: hiç yoksa teslim_paketi KENDİSİ üretir;
        # kenar yaması sha'yı değiştirdiyse GÜNCELLER (bayat mühür bırakma).
        mm = _muhur_modulu()
        if mm is None:
            _udf_red("(+) MÜHÜR", "muhur_yaz.py yüklenemedi — mühürsüz teslim "
                     "YOK (fail-closed)")
        if muhur_kaydi is None or kenar_duzeltildi:
            onceki = (muhur_kaydi.get("artifact_sha256")
                      if (muhur_kaydi and kenar_duzeltildi) else None)
            try:
                yeni_kayit = mm.muhur_uret(
                    kok, udf_cikti, "dilekce_udf",
                    "dilekce:%s" % os.path.basename(udf_cikti),
                    [taslak], onceki=onceki,
                    arac="teslim_paketi (html2udf zinciri)")
                prov_dosya, muhur_hata = mm.muhur_yaz(kok, udf_cikti, yeni_kayit)
            except Exception as e:
                prov_dosya, muhur_hata = None, str(e)
            if muhur_hata:
                _udf_red("(+) MÜHÜR", "mühür YAZILAMADI (%s) — mühürsüz teslim "
                         "fiziksel olarak imkânsız" % muhur_hata)
            print("    [OK] mühür %s: %s" % (
                "GÜNCELLENDİ (kenar yaması sonrası)" if muhur_kaydi else "üretildi",
                os.path.basename(prov_dosya)))
        if mm.dogrula(udf_cikti) != 0:
            _udf_red("(+) MÜHÜR", "mühür doğrulaması BAŞARISIZ — mühür↔dosya "
                     "uyuşmazlığıyla teslim YOK")
        kapilar_makbuz.append({"ad": "(++) UDF TESLİM KAPILARI", "durum": "OK", "exit": 0})

    # ── GÖREV 6 — TAZELİK BİLGİ KAPISI (advisory; kapı KAPATMAZ) ────────────
    tazelik_uyarilari = _tazelik_uyarilari_topla(kok)
    if tazelik_uyarilari:
        _bolum("[i] TAZELİK BİLGİ KAPISI — advisory (tazelik_denetim.py; BLOK DEĞİL)")
        for uyari in tazelik_uyarilari:
            print("    [UYARI-BİLGİ] %s" % uyari)
        print("    [BILGI] bu satırlar makbuza `tazelik_uyarilari` olarak geçti; "
              "kapı kapatmaz (amaç çizgisi: görünürlük).")

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

    makbuz_veri = _makbuz_taban(
        a, taslak, kok, kapilar_makbuz, 0,
        (udf_cikti if udf_uretildi else None), None,
        ekstra={"udf_devralindi": udf_devralindi,        # GÖREV 1
                "kenar_duzeltildi": kenar_duzeltildi,    # GÖREV 5
                "tazelik_uyarilari": tazelik_uyarilari})  # GÖREV 6
    makbuz_yolu = _makbuz_yaz(kok, makbuz_veri, basarili=True)
    print("TESLİM MAKBUZU  : %s" % makbuz_yolu)
    sys.exit(0)


if __name__ == "__main__":
    main()

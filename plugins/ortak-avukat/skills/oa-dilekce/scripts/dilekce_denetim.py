#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
dilekce_denetim.py — oa-dilekce/oa-kontrol TESLİM ÖNCESİ ŞABLON + ZAAF KAPISI

Deterministik denetim: taslak dilekçede (a) tip başına ZORUNLU UNSURLAR var mı,
(b) "avukata yakışan tertip-düzen" — hem biçim (başlık/numaralı vakıa) hem de sekiz
zorunlu unsurun (mahkeme başlığı, taraflar/vekil, konu, açıklamalar, hukuki sebepler,
deliller, sonuç-istem, tarih-imza) mekanik VARLIK denetimi, tip'ten BAĞIMSIZ olarak
her dilekçede — kuruldu mu, (c) OCR ⚠ kaynaklı alıntı teyit şerhi taşıyor mu,
(d) MÜVEKKİL-ALEYHİ ifade sinyali, TARAF-BİLİNÇLİ (anayasal TEK KATI SINIR — davalıda
kabul/ikrar/doğrudur, davacıda vazgeçme/haksızlık, müşteki/katılanda şikayetten
vazgeçme/uzlaşma, sanıkta suç ikrarı) var mı. Script hukuki karar VERMEZ;
eksik/riski işaretler, nihai göz avukatındır — ama eksik/sinyal varsa exit 1 ile
teslim öncesi durdurur.

Tip/unsur listeleri numerus clausus DEĞİL — düşünce metodunu gösteren ÖRNEKLEMDİR;
bilinmeyen tip 'genel dilekçe unsurları' ile denetlenir (anayasa: örnekleme ilkesi).

── [F] İÇTİHAT MUHAKEME ZİNCİRİ KAPISI (M2-3 — oa-kontrol'e BAĞLANDI; P1-7: VARSAYILAN AÇIK) ──
[F], kardeş skill oa-kontrol'ün `ictihat_muhakeme_denetim.py`'sini (çıplak/
ALEYHE/eksik-alanlı içtihat atfı mekanik kapısı — bkz. o scriptin docstring'i)
AYRI SÜREÇTE çalıştırır ve raporu + exit kodu bu denetime [F] bölümü olarak
ekler. Tek tanım oa-kontrol'de yaşar, burada TEKRARLANMAZ — teslim öncesi
MEKANİK KAPILAR zinciri BEŞ değil ALTI yeşil ışıktan oluşur (A-F).

P1-7 (v0.5.5): `--ictihat-muhakeme` artık VARSAYILAN AÇIKTIR (v0.5.4 kanıtı:
kapı opt-in olduğu için gerçek koşumda bayrak hiç verilmedi, [F] hiç koşmadı).
Kapatmak için `--ictihat-muhakeme-yok` kullanılır (teslim_paketi.py bunu
tekilleştirme amacıyla BİLİNÇLİ geçirir — bkz. aşağı). AKILLI FAIL-OPEN (yanlış-
blok supabı, DAR): (a) `--kok` altında `_oa/` yoksa VEYA (b) taslakta hiçbir
içtihat künye-deseni (esas/karar no) VE hiçbir "Yargıtay/Danıştay/AYM/AİHM/
yerleşik içtihat/emsal karar" ANLATIM deseni yoksa [F] `[BİLGİ] atlandı` der,
BLOKLAMAZ — içtihatsız dilekçeler ve `_oa`'sız eski akışlar kırılmaz. AMA künye
YOK iken anlatım deseni VARSA (künyesiz emsal anlatımı) [F] ATLANMAZ — kapı
normal çalışır (G1 zaten bunu "emsal içtihat yok" uyarısına çevirir, bloklamaz)
ve rapora GÖRÜNÜR ek bir satır düşer: "künyesiz içtihat anlatımı — muhakeme
zinciri denetlenemedi" (invaryant m.4: künyesiz parafrazın sessizce sızması
engellenir). `--ictihat-muhakeme-yok` KULLANILDIYSA bu da raporda AÇIKÇA
görünür (sessiz opt-out yok).

Kullanım:
  python dilekce_denetim.py <taslak.md>
                            --tip dava|cevap|istinaf|temyiz|aym_bireysel|yemin|idari-kanal|genel
                            [--taraf davaci|davali|sanik|katilan|mudahil|musteki]
                            [--udf YOL]
                            [--ictihat-muhakeme --kok KLASÖR]
Çıkış kodu: 0 = temiz; 1 = eksik unsur / müvekkil-aleyhi sinyal / OCR-teyit şerhi
eksik / GEÇERSİZ UDF / [F] içtihat muhakeme kapısı engeli.

── [B2] KANUN-YOLU YAPISAL KALEMLERİ (M3-2 — kanun-yolu-mimari-playbook.md B1/B2/B4/B6) ──
`--tip istinaf|temyiz` verildiğinde [B] TERTİP-DÜZEN kapısı, kanun yolu
dilekçesinin fiziksel mimarisine özgü YAPISAL kalemleri de mekanik olarak
denetler: künye blok alan seti (kanun yoluna konu kararın kimliği/sonucu +
dava konusu işlem/dayanak norm), TEBLİĞ TARİHİ'nin AYRI SATIRDA olması, GİRİŞ
bölümünün varlığı, SONUÇ/İSTEM'in numaralı olması ve her içtihat blok-
alıntısının (markdown '>' satırı) ardından bir açıklama paragrafı bulunması
(B4'ün "çıplak alıntı kabul edilmez" kuralının tertip-düzen izdüşümü). Bu da
[A]/[B] gibi YALNIZ var/yok der — "iyi dilekçe" hükmü VERMEZ; `denetle()`'nin
imzası/dönüş arity'si DEĞİŞMEZ (mevcut çağıranlar bozulmaz), yeni kalemler tip
koşuluyla mevcut `duzen_eksik` listesine eklenir.

── G1 "ESASLI DİLEKÇE" TİP LİSTESİ (M3-2/R6) ──
`--ictihat-muhakeme` ile birlikte `--tip` değeri de [F] kapısına
(`ictihat_muhakeme_denetim.py`) aktarılır: o scriptin G1 "emsal içtihat yok"
UYARISI yalnız "esaslı" dilekçe tiplerinde (dava/cevap/istinaf/temyiz/
aym_bireysel) basılır; `yemin`/`idari-kanal` gibi hafif tiplerde bu uyarı
[BİLGİ]'ye düşer (G1 zaten hiçbir zaman bloklamaz — bu yalnız gürültüyü
azaltır). Tek kaynak liste `ictihat_muhakeme_denetim.ESASLI_OLMAYAN_TIPLER`'dir
(burada TEKRARLANMAZ).

── [H] GÖRÜNMEZ İSKELET TARAMASI (P1-11 ek kural, advisory — ASLA bloklamaz) ──
İDDİA→NORM→İÇTİHAT→ÖRTÜŞME→SONUÇ zinciri paragrafın İÇ MANTIĞIDIR, yüzey
metnine ETİKET olarak sızmaz (saha dersi: model iskeleti görünür kalıba
çevirdi, akıcılık bozuldu). [H] satır başında 'İddiamız:', 'Norm:', 'Somut
örtüşme:' kalıplarını ararsa bir AKICILIK uyarısı basar — hukuki içerik
denetimi DEĞİLDİR, yalnız biçim sinyalidir; exit koduna ASLA dokunmaz.

── [I] KUSUR→SONUÇ→TALEP ASİMETRİSİ TARAMASI (P1-11 ek kural, advisory) ──
Karşı tarafın kusuru TESPİT edilir, SONUÇ yazılır, ama GİDERİLMESİNE yönelik
ara karar talebi KURULMAZ (rakibin dosyasını onarmaya yardım = müvekkil-
aleyhi talep inşası). [I] karşı-taraf-kusuru bağlamında 'süre verilsin/
tamamlan-/gideril-' kalıplarını ararsa bir uyarı basar — advisory, ASLA
bloklamaz.

── [K] İZ SATIRI (v0.5.8.4 — 372 karnesi dersi) ──
Cephanelik denetimi 0 bulgu verdiğinde de '[K] cephanelik: 0 bulgu' satırı
basılır — sessiz yeşil ÖLÇÜLEBİLİR olur (372 saha karnesi bunu isteyerek
kanıtlayamadı: iz yoksa "denetim koştu ve temizdi" ile "denetim hiç koşmadı"
ayırt edilemez).

── [L] KAYNAK-BLOĞU İSTİŞARİ DENETİMİ (v0.5.8.4, advisory — ASLA bloklamaz) ──
372 Torbalı bulgusu: KAYNAK-BLOĞU deseni sahada YARIM kaldı — bloklar var ama
@sha8'siz; oa-kontrol/tazelik_denetim.py'nin KAYNAK_OGE_RE'si hash'siz öğeyi
yakalamadığından ürün-tazelik denetimi fiilen işlevsizdi. [L] girdi md'nin
İLK 3 SATIRINDA bloğu arar; yoksa ya da öğeler @sha8'sizse üreticiyi
(oa-kontrol/scripts/kaynak_blogu.py) işaret eden İSTİŞARİ uyarı basar — exit
kodu DEĞİŞMEZ. Regexler TEK KAYNAKTAN (tazelik_denetim) import edilir,
burada TEKRARLANMAZ.

── [Ş] ŞEKİL STANDARDI (v0.5.8.4, advisory — SERT kapı teslim_paketi'nde) ──
Girdi .udf ise content.xml'den üç istişari kalem: pageFormat DÖRT kenar
42.52 pt mi (1,5 cm — Resmî Yazışma Yönetmeliği No. 2646 m.8), gövdede
LineSpacing="0.50" (~1,5 satır) yaygın mı, '(https://…)' bağlantıları 11pt
kapsamında mı (md_udf_html standardı: bağlantı gövdeden 1 punto küçük).
Burada yalnız GÖRÜNÜRLÜK — exit koduna ASLA dokunmaz.

── [Y] HAVADA-KALAN ALINTI KAPISI (346 saha dersi) ────────────────────────
Dört sınıf AYRILIR — sınıflandırma önce gelir, kural körlemesine uygulanamaz
(saha dersi: akış-içi alıntıya kapanış eklemek metni BOZAR):
  (a) akış-bağlı alıntı — cümle tırnaktan sonra gramerce devam ediyor
      ('… şeklinde', '… ifadesiyle', 'denilmiş; devamında', 'sonucuna
      varılmıştır' vb.) → DOKUNULMAZ/temiz;
  (b) havada-kalan — tırnak içinde açılıp '...' ile kesilen ve kapanış kalıbı
      (denilmiştir/şeklindedir/ifade edilmiştir/belirtilmiştir/vurgulanmıştır)
      taşımadan paragraf biten alıntı → BLOK sınıfı bulgu;
  (c) açılan tırnak paragraf sonunda kapanmıyor → BLOK;
  (d) alıntı-dışı serbest '...' → yalnız uyarı.
'>' satırları birebir blok-alıntı gövdesidir ([B4]'ün alanı) — [Y] taramaz.
BLOK bulgular exit 1 üretir; avukat onaylı istisna için `--istisna-gerekce`
(aşağıda) BLOK'u görünür uyarıya düşürür ve istisna defterine yazar.

── [M] MADDE NUMARASI SÜREKLİLİĞİ (346 saha dersi, uyarı sınıfı) ───────────
Numaralı madde/paragraf dizisinde ATLAMA ve MÜKERRERLİK denetimi (saha:
ekleme sırasında 1-5 ve 28-31 blokları mükerrer doğmuştu) → görünür bulgu.
Bölüm başlığından (#) sonra 1'den yeniden başlamak meşru yazım tarzıdır,
uyarı üretmez; sıra bozukluğu BLOK DEĞİLDİR — yazım tarzları değişkendir.

── [N] ÇIPLAK KISALTMA (346 saha dersi, uyarı sınıfı) ──────────────────────
2+ büyük harfli kısaltma metinde geçiyor ama hiçbir yerde tam açılımı
('Açılım (KIS)' ya da 'KIS (Açılım)') verilmemişse uyarı. BİREBİR ALINTI
içindeki kısaltma MUAF (tırnak içi + '>' blok-alıntı tespiti). Yaygın hukuki
kısaltmalar beyaz listesi (HMK, TTK, TBK, TMK, CMK, İYUK, AYM, BAM, E., K.,
md. — örneklemdir, numerus clausus değil) uyarı üretmez.

── [T] TESLİME-HAZIR MAKBUZ KAPISI (346 saha dersi — makbuz garantisi) ─────
Denetlenen taslakta ya da kökün `_oa/` belgelerinde 'TESLİME HAZIR' ibaresi
var ama `_oa/defter/teslim-makbuz.json` (exit_kodu=0) yok/geçersiz →
'makbuzsuz hazır-beyanı' görünür ihlali, BLOK (R2: tek ölçüt teslim_paketi.py
exit 0 + makbuzdur; sözle/ibare ile 'hazır' İLAN EDİLEMEZ). Olumsuzlanmış
geçişler ('hiç TESLİME HAZIR olmamış' — pipeline_kayit uyarı metni) beyan
DEĞİLDİR, sayılmaz. H3b (v0.5.8.6, 777 saha dersi): aynı kapı 'YEŞİL MAKBUZ'
iddiasını da arar — _oa yaşayan belgelerinde iddia VAR ama kanonik makbuz
YOK ise 'kanonik olmayan makbuz beyanı' (BLOK); tarihçe muafiyeti
(oturum/devir/dersler/arsiv-yerel) AYNEN geçerli. H3c: her [T] bulgusu
tek-cümle kanonik tanımı taşır: yeşil makbuz = YALNIZ
_oa/defter/teslim-makbuz.json (exit_kodu=0); stdout dökümü/txt makbuz
DEĞİLDİR.

── İSTİSNA DEFTERİ (ortak şema, append-only) ───────────────────────────────
`--istisna-gerekce METİN` verilirse [Y]/[T] BLOK bulguları avukat onayıyla
görünür UYARIYA düşer (exit'e yansımaz) ve `_oa/defter/istisna-kayitlari.jsonl`
dosyasına {"zaman","tur":"yanlis-pozitif-ilani","ilgili","gerekce","onay":
"avukat","imza"} satırı APPEND-ONLY yazılır — kapı muhakemeyi ENGELLEMEZ,
kaydını tutarak yol verir (sessiz opt-out yok).
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
import glob
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys
import zipfile

# Tip → [(unsur adı, [anahtar desen/kelime])] — herhangi biri geçerse unsur VAR sayılır.
GENEL = [
    ("Mahkeme/merci başlığı", [r"mahkeme", r"başkanlığı", r"hakimliği", r"\bmerci"]),
    ("Taraf + kimlik (TC/adres)", [r"davac[ıi]", r"daval[ıi]", r"başvurucu", r"\bT\.?C\.?\b", r"kimlik\s*no", r"adres"]),
    ("Konu", [r"\bkonu\b"]),
    ("Açıklamalar / vakıalar", [r"açıklama", r"vak[ıi]a", r"olay"]),
    ("Hukuki sebepler", [r"hukuki\s*sebep", r"hukuki\s*neden", r"dayanak"]),
    ("Deliller", [r"delil", r"ispat", r"tanık", r"bilirkişi"]),
    ("Netice-i talep", [r"netice-?i?\s*talep", r"sonuç\s*ve\s*istem", r"talep\s*(ederiz|ederim|olunur)"]),
    ("Tarih", [r"\d{1,2}[./]\d{1,2}[./]\d{4}", r"tarih"]),
    ("İmza / vekil", [r"imza", r"\bvekil", r"av\.\s", r"avukat"]),
]
TIPLER = {
    "dava": GENEL,
    "cevap": GENEL + [("Cevap/ilk itiraz (varsa)", [r"cevap", r"ilk\s*itiraz", r"karşı\s*dava", r"itiraz"])],
    "istinaf": [
        ("Başvurulan BAM + ilk derece karar", [r"bölge\s*adliye", r"\bBAM\b", r"ilk\s*derece", r"esas\s*no", r"karar\s*no"]),
        ("Taraflar", [r"davac[ıi]", r"daval[ıi]", r"istinaf\s*eden"]),
        ("İstinaf sebepleri", [r"istinaf\s*sebep", r"istinaf\s*neden", r"kaldır", r"hukuka\s*aykırı"]),
        ("Talep (kaldırma/yeniden)", [r"netice-?i?\s*talep", r"kaldırıl", r"talep\s*(ederiz|ederim)"]),
        ("Tebliğ tarihi + süre satırı", [r"tebliğ", r"süre", r"iki\s*hafta", r"\b2\s*hafta"]),
        ("Tarih + imza", [r"\d{1,2}[./]\d{1,2}[./]\d{4}", r"imza", r"\bvekil"]),
    ],
    "temyiz": [
        ("Yargıtay ilgili dairesi", [r"yargıtay", r"\bdaire", r"hukuk\s*dairesi", r"ceza\s*dairesi"]),
        ("BAM kararı bilgisi", [r"bölge\s*adliye", r"\bBAM\b", r"esas\s*no", r"karar\s*no"]),
        ("Temyiz sebepleri", [r"temyiz\s*sebep", r"temyiz\s*neden", r"bozma", r"hukuka\s*aykırı"]),
        ("Talep", [r"netice-?i?\s*talep", r"boz", r"talep\s*(ederiz|ederim)"]),
        ("Süre satırı", [r"tebliğ", r"süre", r"iki\s*hafta"]),
        ("Tarih + imza", [r"\d{1,2}[./]\d{1,2}[./]\d{4}", r"imza"]),
    ],
    "aym_bireysel": [
        ("Başvurucu bilgileri", [r"başvurucu", r"\bT\.?C\.?\b", r"kimlik"]),
        ("İhlal edilen hak + Anayasa maddesi", [r"ihlal", r"anayasa[’']?n[ıi]n?\s*\d+", r"\bAY\s*m\.?\s*\d+", r"hak\b"]),
        ("Başvuru yollarının tüketilmesi", [r"yol.*tüket", r"tüketil", r"kesinleş"]),
        ("Süre (30 gün)", [r"süre", r"otuz\s*gün", r"\b30\s*gün", r"tebliğ", r"öğrenme"]),
        ("Talep", [r"talep", r"ihlalin\s*tespit", r"yeniden\s*yargılama"]),
    ],
    "genel": GENEL,
}

# Tertip-düzen: hem BİÇİM (başlık/numaralandırma) hem de "avukata yakışan" dilekçenin
# ZORUNLU UNSURLARININ VARLIĞI — tip ne olursa olsun (dava/cevap/istinaf/temyiz/aym_bireysel/
# genel) her dilekçede bulunması beklenen sekiz kalem: mahkeme başlığı, taraflar/vekil, konu,
# açıklamalar, hukuki sebepler, deliller, sonuç-istem, tarih-imza. Bu katman [A]'daki tip-özel
# listeden BAĞIMSIZ ve TÜM tiplere UYGULANIR — istinaf/temyiz/aym_bireysel gibi tip-özel
# listeler "Konu"/"Deliller"/"Hukuki sebepler" gibi jenerik kalemleri her zaman içermeyebilir;
# bu katman onu tamamlar. Script yalnız "unsur var/yok" der — "dilekçe iyi/kötü/kabule
# elverişli" hükmü VERMEZ (sahte kesinlik yok); eksik olanı UYAR, nihai göz avukatındır.
DUZEN = [
    ("Belirgin başlık bloğu", [r"^#", r"mahkeme", r"başkanlığı"]),
    ("Numaralı/bölümlü açıklama düzeni", [r"^\s*\d+[.)]", r"^\s*[-*]\s", r"##"]),
    ("Mahkeme/merci başlığı", [r"mahkeme", r"başkanlığı", r"hakimliği", r"\bmerci", r"dairesi", r"kurulu"]),
    ("Taraflar / vekil bilgisi", [r"davac[ıi]", r"daval[ıi]", r"başvurucu", r"müşteki", r"sanık",
                                   r"katılan", r"müdahil", r"\bvekil", r"av\.\s"]),
    ("Konu", [r"\bkonu\b"]),
    ("Açıklamalar / vakıalar", [r"açıklama", r"vak[ıi]a", r"olay"]),
    ("Hukuki sebepler", [r"hukuki\s*sebep", r"hukuki\s*neden", r"dayanak", r"hukuka\s*aykır"]),
    ("Deliller", [r"delil", r"ispat", r"tanık", r"bilirkişi"]),
    ("Sonuç ve istem (netice-i talep)", [r"netice-?i?\s*talep", r"sonuç\s*ve\s*istem", r"talep\s*(ederiz|ederim|olunur)"]),
    ("Tarih + imza bloğu", [r"\d{1,2}[./]\d{1,2}[./]\d{4}", r"imza", r"\bvekil", r"saygı"]),
]

# ── [B2] KANUN-YOLU (istinaf/temyiz) YAPISAL KALEMLERİ — M3-2 ──────────────
# kanun-yolu-mimari-playbook.md B1 (künye disiplini) / B2 (GİRİŞ) / B4 (içtihat
# bloğu 5-adım) / B6 (bölüm mimarisi) 'nin dilekçe-içi mekanik izdüşümü. [B]
# TERTİP-DÜZEN kapısının tip-koşullu UZANTISIDIR — yalnız --tip istinaf|temyiz
# iken devreye girer; DUZEN listesinden BAĞIMSIZ yeni bir alan çifti EKLER,
# denetle()'nin dönüş imzasını DEĞİŞTİRMEZ. Sahte kesinlik yok: yalnız
# var/yok listesi döner, "iyi dilekçe" hükmü VERMEZ.
KANUN_YOLU_TIPLERI = {"istinaf", "temyiz"}

# B1 künye blok alan seti — DUZEN'de zaten denetlenen merci/taraflar/tarih
# kalemleriyle ÇAKIŞMAYAN, kanun yoluna özgü iki alan.
KANUN_YOLU_KUNYE_EK = [
    ("B1 Künye — kanun yoluna konu kararın kimliği/operatif sonucu",
     [r"ilk\s*derece.{0,40}karar", r"karar\s*ver(ilmiş|di)", r"hükm",
      r"reddine|kabulüne|karar\s*verilmiştir"]),
    ("B1 Künye — dava konusu işlem + dayanak norm",
     [r"dayanak", r"\bm\.\s*\d", r"madde\s*\d+", r"kanun(?:'?un|\s+m\.)"]),
]


def _satir_basi(metin, desen):
    """Bir satırın (markdown başlık/liste işaretleri temizlendikten sonra)
    BAŞI verilen desenle eşleşiyor mu — 'ayrı satır' zorunluluğunun mekanik
    karşılığı. Metnin ortasına/başka bir cümlenin içine gömülü geçiş bu
    denetim için YETERSİZ sayılır (B1: 'tebliğ tarihinin künye metnine
    gömülmesi' sık atlanan hatadır — süre denetimi bu satırı ayrıca arar)."""
    for satir in metin.splitlines():
        temiz = re.sub(r"^[\s#>*\-\d.)]+", "", satir).strip()
        if re.match(desen, temiz, re.I):
            return True
    return False


def _giris_bolumu_var_mi(metin):
    """B2 — 'GİRİŞ' başlıklı bir markdown bölümü var mı (yalnız VARLIK;
    içeriğin gerçekten 'çatı indirgeme' yapıp yapmadığı script'in işi
    DEĞİLDİR — bkz. playbook B2 ön koşulu)."""
    return bool(re.search(r"^\s*#{1,3}\s*[Gg][İIiı][Rr][İIiı][Şş]\b", metin, re.M))


def _sonuc_numarali_mi(metin):
    """B6 — netice-i talep/sonuç-istem bölümünden SONRAKİ metinde numaralı
    ('1. ...'/'1) ...') bir liste var mı. Rakam sayısı 1-2 hane + noktalama +
    ARDINDAN BOŞLUK ile sınırlanır ki '01.01.2026' gibi bir TARİH satırı
    (tarih-imza bloğu her dilekçenin sonunda bulunur) numaralı liste maddesi
    sanılıp YANLIŞ pozitif üretmesin."""
    m = re.search(r"netice-?i?\s*talep|sonuç\s*ve\s*istem", metin, re.I)
    if not m:
        return False
    return bool(re.search(r"^\s*\d{1,2}[.)]\s+\S", metin[m.end():], re.M))


def _alinti_aciklama_denetle(metin):
    """B4 — markdown blok-alıntı ('>' ile başlayan ardışık satır grupları)
    gruplarının HER BİRİ için, grup bittikten sonraki birkaç satır içinde
    boş-olmayan/alıntı-olmayan/BAŞLIK-OLMAYAN bir açıklama paragrafı var mı.
    (toplam_alinti, aciklamasiz_sayisi) döndürür — alıntı hiç yoksa (0, 0):
    bu denetim yalnız VAR OLAN alıntıların ardışıklığını denetler, alıntı
    yokluğunu YAKALAMAZ (o [F]/G1'in — oa-kontrol'ün — işidir). Bir sonraki
    markdown başlığı ('#...') açıklama SAYILMAZ — bölüm bittiği anlamına
    gelir, alıntı çıplak kalmış demektir (B4: 'çıplak alıntı kabul edilmez')."""
    satirlar = metin.splitlines()
    n = len(satirlar)
    toplam, eksik = 0, 0
    i = 0
    while i < n:
        if satirlar[i].lstrip().startswith(">"):
            toplam += 1
            j = i
            while j < n and satirlar[j].lstrip().startswith(">"):
                j += 1
            aciklama_var = False
            for k in range(j, min(j + 8, n)):
                s = satirlar[k].strip()
                if not s:
                    continue
                aciklama_var = not (s.startswith(">") or s.startswith("#"))
                break
            if not aciklama_var:
                eksik += 1
            i = j
        else:
            i += 1
    return toplam, eksik


def _kanun_yolu_yapisal_eksik(metin):
    """Kanun-yolu (istinaf/temyiz) tipleri için B1/B2/B4/B6 mekanik
    izdüşümünün eksik kalemlerini döndürür (yalnız VAR/YOK; hüküm YOK)."""
    eksik = [ad for ad, des in KANUN_YOLU_KUNYE_EK if not _bul(metin, des)]
    if not _satir_basi(metin, r"tebliğ\s*tarih"):
        eksik.append("B1 Künye — TEBLİĞ TARİHİ (ayrı satırda)")
    if not _giris_bolumu_var_mi(metin):
        eksik.append("B2 — GİRİŞ bölümü")
    if not _sonuc_numarali_mi(metin):
        eksik.append("B6 — Numaralı SONUÇ/İSTEM")
    toplam_alinti, eksik_aciklama = _alinti_aciklama_denetle(metin)
    if toplam_alinti and eksik_aciklama:
        eksik.append(
            f"B4 — İçtihat blok-alıntısı sonrası açıklama paragrafı "
            f"({eksik_aciklama}/{toplam_alinti} alıntıda eksik görünüyor)")
    return eksik


# Müvekkil-aleyhi tehlike desenleri (TARAF-BİLİNÇLİ) — HEURİSTİK; avukat teyit etmeli.
# Her taraf tipi kendi riskli kalıp setiyle taranır: davalı için kabul/ikrar/doğrudur ekseni,
# davacı için vazgeçme/haksızlık ekseni, müşteki/katılan için şikayetten vazgeçme/uzlaşma
# ekseni, sanık için suç ikrarı ekseni. "genel" seti her taraf için ek olarak taranır.
_ALEYHE_DAVALI = [
    r"davay[ıi]\s*kabul", r"kabul\s*ed(iyoruz|iyorum|eriz)", r"haklı\s*olduğunu\s*kabul",
    r"borcu(muzu)?\s*kabul", r"\bikrar\s*ed", r"talebi(ni)?\s*kabul", r"davanın\s*kabul",
    r"\bdoğrudur\b", r"iddia\s*doğrudur", r"kusurlu(yuz|yum)", r"sorumlu\s*olduğu(muzu|mu)",
]
_ALEYHE_DAVACI = [
    r"iddiam[ıi]zdan\s*vazgeç", r"haksız\s*olduğumuz", r"talebimizi\s*geri",
    r"talebimizden\s*vazgeç", r"davadan\s*feragat", r"iddiam[ıi]zdan\s*feragat",
    r"haklı\s*değiliz", r"davamız\s*yersiz",
]
_ALEYHE_MUSTEKI = [
    r"şikayet(im|imiz)i\s*geri", r"şikayetten\s*vazgeç", r"affediyor",
    r"barıştık", r"şikayetçi\s*değil", r"davacı\s*olmak\s*istemiyor",
]
_ALEYHE_SANIK = [
    r"suçu\s*kabul", r"işlediğim(i)?\s*kabul", r"\bikrar\s*ed", r"pişman.*kabul",
    r"suçlu\s*olduğumu",
]
ALEYHE = {
    "davali": _ALEYHE_DAVALI,
    "davaci": _ALEYHE_DAVACI,
    "musteki": _ALEYHE_MUSTEKI,
    # katılan usulen müştekinin kamu davası açıldıktan sonraki devamıdır — aynı riskli eksen.
    "katilan": _ALEYHE_MUSTEKI,
    "sanik": _ALEYHE_SANIK,
    "genel": [r"karşı\s*taraf(ın)?\s*haklı", r"aleyhimize\s*kabul"],
}


def _bul(metin, desenler):
    return any(re.search(d, metin, re.I | re.M) for d in desenler)


def _udf_yaz_yukle():
    """udf_yaz.py'yi (kardeş script) dosya-yolundan yükler — paket değildir."""
    yol = pathlib.Path(__file__).resolve().parent / "udf_yaz.py"
    if not yol.is_file():
        return None
    spec = importlib.util.spec_from_file_location("udf_yaz", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def udf_kapisi(udf_yolu):
    """Üretilen UDF'in GEÇERLİ olup olmadığını udf_yaz.udf_dogrula ile denetler.

    Bu, denetim hattının UDF-VARSAYILAN doktrinine bağlı mekanik kapısıdır:
    dilekçe UDF olarak teslim edilecekse, önce bu kapı GEÇERLİ dönmelidir.
    Sahte kesinlik yok — yalnız 'geçerli/geçersiz' + somut hata listesi döner,
    'iyi dilekçe' hükmü vermez.
    """
    mod = _udf_yaz_yukle()
    if mod is None:
        return {"gecerli": False, "hatalar": ["udf_yaz.py yüklenemedi (kardeş script bulunamadı)"]}
    return mod.udf_dogrula(udf_yolu)


def _ictihat_muhakeme_yolu():
    """Kardeş skill oa-kontrol'ün `ictihat_muhakeme_denetim.py` yolunu döndürür
    (…/skills/oa-dilekce/scripts/ → …/skills/oa-kontrol/scripts/); yoksa None."""
    yol = (pathlib.Path(__file__).resolve().parent.parent.parent
           / "oa-kontrol" / "scripts" / "ictihat_muhakeme_denetim.py")
    return yol if yol.is_file() else None


_KUNYE_ORTAK_MOD = None


def _kunye_ortak_modulu():
    """kunye_ortak.py'yi (…/oa-kontrol/scripts/) İN-PROCESS import eder — P1-7
    akıllı fail-open ön-denetiminde 'taslakta içtihat künye-deseni var mı'
    sorgusu TEK KAYNAKTAN (`kunye_ortak.esas_karar_atiflari`) yanıtlanır,
    regex burada TEKRARLANMAZ. Kardeş skill kurulu değilse/import çökerse
    None döner — çağıran taraf bunu FAIL-SAFE sayıp [F]'i ATLAMAZ (belirsizlik
    içtihat kapısını sessizce kapatmanın gerekçesi olamaz)."""
    global _KUNYE_ORTAK_MOD
    if _KUNYE_ORTAK_MOD is not None:
        return _KUNYE_ORTAK_MOD
    yol = (pathlib.Path(__file__).resolve().parent.parent.parent
           / "oa-kontrol" / "scripts" / "kunye_ortak.py")
    if not yol.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            "_oa_dilekce_kunye_ortak_inproc", str(yol))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return None
    _KUNYE_ORTAK_MOD = mod
    return _KUNYE_ORTAK_MOD


# P1-7 DÜZELTME — "künye yok" fail-open'ının içtihat ANLATIMI ile delinmesini
# önleyen desen: Yargıtay/Danıştay/AYM/AİHM/içtihadı birleştirme/yerleşik
# içtihat/emsal karar sözcükleri esas/karar no'suz da geçebilir (invaryant
# m.4'ün korumak istediği tam da bu yüzey — künyesiz parafraz).
ICTIHAT_ANLATIM_DESENI = re.compile(
    r"Yarg[ıi]tay|Dan[ıi]ştay\b|\bAYM\b|Anayasa\s+Mahkemesi|\bA[İi]HM\b|"
    r"içtihad[ıi]\s*birleştirme|yerleşik\s+içtihat|emsal\s+karar", re.I)


def _f_kapisi_fail_open_durumu(metin, a):
    """P1-7 — AKILLI FAIL-OPEN ön-denetimi (DAR). Döner:
      None                    → [F] normal çalışır (varsayılan/çoğunluk hâli).
      'no_oa'                 → _oa/ bulunamadı, [F] `[BİLGİ]` ile atlanır.
      'no_signal'              → taslakta ne künye ne içtihat anlatımı var,
                                  [F] `[BİLGİ]` ile atlanır.
      'desen_var_kunye_yok'    → künye YOK ama içtihat ANLATIMI var — [F]
                                  ATLANMAZ (normal çalışır), rapora ek GÖRÜNÜR
                                  uyarı düşer (künyesiz parafraz sızmasın)."""
    taban = a.kok if a.kok else "."
    if not os.path.isdir(os.path.join(taban, "_oa")):
        return "no_oa"
    ko = _kunye_ortak_modulu()
    kunye_var = None
    if ko is not None:
        try:
            atiflar = ko.esas_karar_atiflari(metin)
            kunye_var = any((x.get("esas") or x.get("karar")) for x in atiflar)
        except Exception:
            kunye_var = None
    if kunye_var:
        return None
    if kunye_var is None:
        # kunye_ortak yüklenemedi — belirsizlik atlamayı GEREKÇELENDİRMEZ,
        # fail-safe: [F] normal çalışsın (sessiz kapatma yok).
        return None
    if ICTIHAT_ANLATIM_DESENI.search(metin):
        return "desen_var_kunye_yok"
    return "no_signal"


def ictihat_muhakeme_kapisi(taslak_yolu, kok=None, muhakeme_dizin=None, dokum_dizin=None,
                             tip=None):
    """[F] İçtihat Muhakeme Zinciri mekanik kapısını (oa-kontrol'ün
    `ictihat_muhakeme_denetim.py`'si) AYRI SÜREÇTE çalıştırır ve (exit_kodu,
    rapor_metni) döndürür. Tek tanım oa-kontrol'de yaşar — burada
    TEKRARLANMAZ (M2-3: dilekce_denetim'in teslim-öncesi mekanik kapılar
    zincirine bu adımı BAĞLAR, yeni yeşil ışık). `tip` verilirse (M3-2/R6)
    kardeş scripte `--tip` olarak aktarılır — G1 "esaslı dilekçe" tip
    listesinin tek kaynağı orada yaşar, burada TEKRARLANMAZ."""
    yol = _ictihat_muhakeme_yolu()
    if yol is None:
        return 1, ("[EKSİK] ictihat_muhakeme_denetim.py bulunamadı "
                    "(oa-kontrol/scripts/ — kardeş skill kurulu mu?)")
    args = [sys.executable, str(yol), taslak_yolu]
    if kok:
        args += ["--kok", kok]
    if muhakeme_dizin:
        args += ["--muhakeme-dizin", muhakeme_dizin]
    if dokum_dizin:
        args += ["--dokum-dizin", dokum_dizin]
    if tip:
        args += ["--tip", tip]
    cp = subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return cp.returncode, ((cp.stdout or "") + (cp.stderr or "")).rstrip()


_ANTITEZ_MATRIS_MOD = None


def _antitez_matris_modulu():
    """Kardeş skill oa-antitez'in `antitez_matris.py`sini (…/oa-antitez/scripts/)
    İN-PROCES import eder — [G] advisory kapısının `duyulmus_curutmeler()`
    çağrısı için TEK KAYNAK (mantık burada TEKRARLANMAZ). Kardeş skill kurulu
    değilse/import çökerse None döner — [G] SESSİZCE atlanır (advisory,
    bloklamaz; bkz. `_kunye_ortak_modulu` ile aynı fail-safe desen)."""
    global _ANTITEZ_MATRIS_MOD
    if _ANTITEZ_MATRIS_MOD is not None:
        return _ANTITEZ_MATRIS_MOD
    yol = (pathlib.Path(__file__).resolve().parent.parent.parent
           / "oa-antitez" / "scripts" / "antitez_matris.py")
    if not yol.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("antitez_matris", yol)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return None
    _ANTITEZ_MATRIS_MOD = mod
    return mod


_ANTITEZ_DURAK_KELIME = {
    "ve", "veya", "ile", "için", "gibi", "ama", "fakat", "ancak", "değil",
    "olan", "olarak", "üzere", "göre", "kadar", "daha", "her", "hiç", "ise",
    "yani", "dolayı", "çünkü", "birlikte", "sonra", "önce", "sırasında",
}


def _antitez_anahtar_kelimeler(metin):
    kelimeler = re.findall(r"[a-zçğıöşüA-ZÇĞİÖŞÜ]{5,}", (metin or "").lower())
    return [k for k in kelimeler if k not in _ANTITEZ_DURAK_KELIME]


def _antitez_matris_dosyalari(kok):
    """M3 düzeltmesi (Paket D sınav bulgusu) — `_oa/cikti/*antitez*.json`
    ADAYLARINI TEK YERDEN bulur; hem `antitez_cevap_capasi_uyarilari` hem de
    [G] kapısının CLI çıktısı AYNI listeyi kullanır — böylece 'matris hiç
    yok' ile 'matris var ve tam örtüşüyor' durumları AYRI etiketlenebilir
    (ikisi de eskiden aynı boş-liste dönüşüyle [OK] altında birleşiyordu).

    YENİ-2 (Paket D DÜZELTME) — `kok` verilmediğinde artık SERT `[]` DÖNMEZ;
    `_ictihat_muhakeme_atlama_sebebi`:375 ile SİMETRİK olarak CWD'ye
    (`"."`) düşer. Kanonik teslim hattı (`teslim_paketi.py`) CWD'yi zaten
    `kok`a eşitleyip çalıştırır (`_kos(..., cwd=kok)`) — dolayısıyla
    `--kok` argümanı unutulsa bile [G] kapısı gerçek matrisi görür."""
    taban = kok if kok else "."
    cikti_dizin = os.path.join(taban, "_oa", "cikti")
    if not os.path.isdir(cikti_dizin):
        return []
    return sorted(glob.glob(os.path.join(cikti_dizin, "*antitez*.json")))


def antitez_cevap_capasi_uyarilari(metin, kok):
    """M3 (Paket D, v0.5.5) — [G] ADVISORY: `_oa/cikti/*antitez*.json`
    matrisindeki DUYULMUŞ+çürütülmüş her cephe için dilekçede bir 'çapa'
    (anahtar-kelime örtüşmesi, ≥%25 VEYA hiç yoksa) var mı? Bu bir DOĞRULUK
    denetimi DEĞİLDİR — yalnız 'çürütme dış çıktıya hiç yansımamış olabilir'
    sinyalidir; matris/kok yoksa veya kardeş skill yüklenemezse SESSİZCE boş
    liste döner (bloklamaz, ASLA çökmez — advisory girdisidir)."""
    adaylar = _antitez_matris_dosyalari(kok)
    if not adaylar:
        return []
    mod = _antitez_matris_modulu()
    if mod is None:
        return []
    uyarilar = []
    metin_kelimeleri = set(_antitez_anahtar_kelimeler(metin))
    for yol in adaylar:
        try:
            with open(yol, encoding="utf-8") as f:
                m = json.load(f)
        except Exception:
            continue
        try:
            duyulmuslar = mod.duyulmus_curutmeler(m)
        except Exception:
            continue
        for kayit in duyulmuslar:
            curutme = kayit.get("curutme") or ""
            anahtarlar = _antitez_anahtar_kelimeler(curutme)
            if not anahtarlar:
                continue
            ortusen = sum(1 for k in anahtarlar if k in metin_kelimeleri)
            oran = ortusen / len(anahtarlar)
            if ortusen < 1 or oran < 0.25:
                uyarilar.append(
                    f"cephe '{kayit.get('cephe')}' DUYULMUŞ (karşı taraf fiilen ileri "
                    "sürmüş) ve çürütülmüş ama dilekçede buna karşılık gelen bir çapa "
                    f"bulunamadı ({os.path.relpath(yol, kok)}) — çürütme dış çıktıya "
                    "İŞLENMEMİŞ olabilir; avukat gözden geçirmeli."
                )
    return uyarilar


# ── [H] GÖRÜNMEZ İSKELET TARAMASI (P1-11 ek kural, advisory) ───────────────
# İDDİA→NORM→İÇTİHAT→ÖRTÜŞME→SONUÇ zinciri paragrafın İÇ MANTIĞIDIR; saha
# dersi modelin bu zinciri görünür ETİKETLERE çevirdiğini gösterdi (akıcılık
# bozuldu). Bu tarama yalnız BİÇİM sinyalidir — hukuki içerik denetimi
# DEĞİLDİR, exit koduna ASLA dokunmaz (advisory).
_ISKELET_KALIPLARI = [
    (r"İddia(?:m[ıi]z)?\s*:", "İddiamız:"),
    (r"Norm\s*:", "Norm:"),
    (r"Somut\s*örtüşme\s*:", "Somut örtüşme:"),
]


def _gorunmez_iskelet_uyarilari(metin):
    """Satır başında (markdown başlık/liste işaretleri temizlendikten sonra)
    'İddiamız:', 'Norm:', 'Somut örtüşme:' kalıp-etiketlerini arar. Bulunan
    HER FARKLI etiket için bir uyarı döner — paragraf başına tekrar tekrar
    aynı uyarıyı basıp gürültü üretmemek için etiket başına TEKİLLEŞTİRİLİR."""
    uyarilar = []
    bulunanlar = set()
    for satir in (metin or "").splitlines():
        temiz = re.sub(r"^[\s#>*\-\d.)]+", "", satir).strip()
        for desen, etiket in _ISKELET_KALIPLARI:
            if etiket in bulunanlar:
                continue
            if re.match(desen, temiz, re.I):
                bulunanlar.add(etiket)
                uyarilar.append(
                    f"paragraf başında görünür kalıp-etiket '{etiket}' tespit edildi — "
                    "İDDİA→NORM→İÇTİHAT→ÖRTÜŞME→SONUÇ zinciri paragrafın İÇ MANTIĞI olmalı, "
                    "yüzeye ETİKET olarak sızmamalı (geçiş cümleleriyle örülmeli); akıcılık "
                    "bozulmuş olabilir — biçim sinyalidir, hukuki içerik hükmü değildir."
                )
    return uyarilar


# ── [I] KUSUR→SONUÇ→TALEP ASİMETRİSİ TARAMASI (P1-11 ek kural, advisory) ───
# Karşı tarafın kusuru TESPİT edilir, SONUÇ yazılır, ama GİDERİLMESİNE yönelik
# ara karar talebi KURULMAZ — rakibin dosyasını onarmaya yardım etmek
# müvekkil-aleyhi talep inşasıdır. Bu tarama yalnız BİÇİM/BAĞLAM sinyalidir,
# hukuki içerik hükmü DEĞİLDİR, exit koduna ASLA dokunmaz (advisory).
_KUSUR_BAGLAM_RE = re.compile(
    r"karşı\s*taraf(ın)?|davalı(n[ıi]n)?|daval[ıi]\s*taraf|davac[ıi](n[ıi]n)?|"
    r"kusur(u|lu|lar[ıi])?|eksik(lik|liği)?|dava\s*şart[ıi]\s*eksik", re.I)
_TALEP_ONARMA_RE = re.compile(
    r"süre\s*veril(sin|mesi|melidir)|tamamlan(mas[ıi]|mas[ıi]n[ıi]|d[ıi]r[ıi]lmas[ıi])|"
    r"gideril(sin|mesi|melidir)", re.I)


# ── B-30 DÜZELTMESİ (v0.5.14) — [K] BEKÇİSİ GERÇEK CÜMLEDE ATEŞLEMİYORDU ───
# Eski desen tek parçaydı: `(hasım)[^.\n]{0,80}(fiil)`. In-process vaka seti
# (2026-08-31) beş ayrı körlük gösterdi: (a) `[^.]` MADDE ATFINDAKİ noktayı
# ('TBK m. 146') pencere dışına atıyor, (b) `[^\n]` SATIR KIRIĞINI kesiyor,
# (c) 80 karakter gerçek cümle için dar, (d) fiil listesi eksik
# ('def'inde bulunabilir', 'savunması muhtemeldir'). Uçtan uca koşuda taslakta
# ihlal varken "[OK] … bulunamadı" basıldı — advisory'nin TEK işlevi
# GÖRÜNÜRLÜKTÜR, o da üretilmiyordu.
#
# Yeni yapı: tek dev regex yerine PENCERE MANTIĞI — metin cümlelere bölünür,
# her cümlede "muhtemel savunma fiili" aranır, fiilden ÖNCE aynı cümlede bir
# hasım sözcüğü olması şartı konur. Cümle sınırı, RAKAMDAN SONRA GELEN noktayı
# (madde atfı 'm. 146', künye '9. HD') sınır SAYMAZ; tek satır kırığı sınır
# değildir, BOŞ SATIR sınırdır.
CEPHANELIK_HASIM_RE = re.compile(
    r"davalı|karşı\s*taraf|idare(?:nin|ye|yi|si)?|hasım", re.IGNORECASE)

CEPHANELIK_FIIL_RE = re.compile(
    r"savunabil"
    r"|savunma(?:s[ıi]|lar[ıi])?\s+(?:muhtemel|olas[ıi]|beklen)"
    r"|(?:muhtemel|olas[ıi])\s+savunma"
    r"|savunmas[ıi](?:na|nda)?\s*karşı"
    r"|ileri\s*sürebil"
    r"|itiraz\s*edebil"
    r"|iddia\s*edebil"
    r"|karşı\s*çıkabil"
    r"|dayanabil"
    r"|(?:def['’]?\w*|itiraz\w*|talep\w*|talebin\w*|savunma\w*)\s+bulunabil",
    re.IGNORECASE)

# Cümle sınırı: nokta/ünlem/soru + boşluk + BÜYÜK harf — ama noktadan ÖNCE
# RAKAM varsa sınır DEĞİLDİR ('m. 146', 'Yargıtay 9. HD', 'E. 2020/1111').
# Boş satır her hâlde sınırdır (paragraf değişimi).
_CEPHANELIK_CUMLE_SINIRI_RE = re.compile(
    r"\n\s*\n|(?<![0-9])(?<=[.!?])\s+(?=[A-ZÇĞİÖŞÜ])")

# v0.5.14: eski tek-parça desen SİLİNDİ (tek yazar kuralı — iki desen evreni
# doğmasın). Dışa açık ad olarak `CEPHANELIK_HASIM_RE`/`CEPHANELIK_FIIL_RE`
# kullanılır.


def _cephanelik_cumleler(metin):
    """(başlangıç_ofseti, cümle_metni) çiftleri — bkz. sınır kuralı."""
    parcalar, son = [], 0
    for m in _CEPHANELIK_CUMLE_SINIRI_RE.finditer(metin or ""):
        parcalar.append((son, metin[son:m.start()]))
        son = m.end()
    parcalar.append((son, (metin or "")[son:]))
    return parcalar


def cephanelik_ifsa_uyarilari(metin):
    """v0.5.8.1 [K] — m.6 CEPHANELİK BEKÇİSİ (447 provası bulgusu-A):
    karşı tarafın MUHTEMEL savunmalarının analizi dilekçeye yazılmışsa yakala.
    Bu analiz İÇ CEPHANELİKTİR (_oa/cikti/07-antitez-cephanelik.md) — dilekçede
    kurulması, karşı tarafa savunma hattını HEDİYE etmek ve kendi zayıf
    noktalarını İFŞA etmektir. ADVISORY: bilinçli ön-karşılama (praeoccupatio)
    nadiren meşru bir retorik tercihtir — karar avukatta, script BLOKLAMAZ."""
    uyarilar = []
    for bas, cumle in _cephanelik_cumleler(metin or ""):
        for m in CEPHANELIK_FIIL_RE.finditer(cumle):
            if not CEPHANELIK_HASIM_RE.search(cumle[:m.start()]):
                continue
            parca = " ".join(cumle[:m.end() + 50].split())
            uyarilar.append(
                f"muhtemel-savunma analizi dilekçede: \"…{parca[:140]}…\" — m.6: "
                "bu analiz CEPHANELİĞE yazılır (07-antitez), dilekçeye DEĞİL; "
                "bilinçli ön-karşılama ise avukat onayıyla kalabilir")
            break          # aynı cümleden tek uyarı (gürültü yasağı)
        if len(uyarilar) >= 6:
            break
    return uyarilar


def _kusur_sonuc_talep_asimetri_uyarilari(metin):
    """Karşı-taraf-kusuru bağlamında ('karşı taraf', 'davalının', 'kusur',
    'eksiklik', 'dava şartı eksik' vb.) bir 'süre verilsin/tamamlan-/
    gideril-' onarma-talebi kalıbı geçiyor mu — ÖNCESİNDEKİ ~150 karakterlik
    pencerede bağlam kelimesi arar (aleyhe-ifade taramasındaki pencere
    deseniyle aynı yöntem). Bulunursa müvekkil-aleyhi talep inşası riski
    uyarısı döner; tekrarları TEKİLLEŞTİRİR."""
    uyarilar = []
    gorulen = set()
    for m in _TALEP_ONARMA_RE.finditer(metin or ""):
        once = metin[max(0, m.start() - 150): m.start()]
        if _KUSUR_BAGLAM_RE.search(once):
            ifade = m.group(0)
            if ifade in gorulen:
                continue
            gorulen.add(ifade)
            uyarilar.append(
                f"karşı-taraf-kusuru bağlamında onarma-talebi kalıbı: \"{ifade}\" — "
                "kusur TESPİT edilir, SONUÇ yazılır, ama GİDERİLMESİNE yönelik ara "
                "karar talebi KURULMAZ (rakibin dosyasını onarmasına yardım = "
                "müvekkil-aleyhi talep inşası); avukat gözden geçirmeli."
            )
    return uyarilar


# ── [L] KAYNAK-BLOĞU İSTİŞARİ DENETİMİ (v0.5.8.4, advisory) ────────────────
# 372 Torbalı bulgusu: bloklar var ama @sha8'siz → tazelik_denetim'in
# KAYNAK_OGE_RE'si öğeyi yakalamıyor, ürün-tazelik denetimi fiilen işlevsiz.
# Regexler TEK KAYNAKTAN (oa-kontrol/tazelik_denetim.py) okunur — kopya regex
# üretici/denetçi simetrisini sessizce DELERDİ; burada TEKRARLANMAZ.

_TAZELIK_MOD = None


def _tazelik_modulu():
    """tazelik_denetim.py'yi (…/oa-kontrol/scripts/) İN-PROCESS import eder —
    KAYNAK_BLOK_RE/KAYNAK_OGE_RE tek kaynaktan gelir. Kardeş skill kurulu
    değilse/import çökerse None döner — [L] advisory olduğundan çağıran taraf
    bunu '[BİLGİ] denetlenemedi' olarak GÖRÜNÜR kılar, sessizce yeşil demez
    (bkz. `_kunye_ortak_modulu` ile aynı fail-safe desen)."""
    global _TAZELIK_MOD
    if _TAZELIK_MOD is not None:
        return _TAZELIK_MOD
    yol = (pathlib.Path(__file__).resolve().parent.parent.parent
           / "oa-kontrol" / "scripts" / "tazelik_denetim.py")
    if not yol.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            "_oa_dilekce_tazelik_inproc", str(yol))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        return None
    _TAZELIK_MOD = mod
    return _TAZELIK_MOD


def kaynak_blogu_uyarilari(metin):
    """İlk 3 satırda '<!-- kaynaklar: yol@sha8 ... -->' bloğu var mı ve TÜM
    öğeler @sha8'li mi. Döner: [] = temiz · [uyarı] = eksik/hashsiz · None =
    tazelik_denetim yüklenemedi (denetlenemedi — çağıran [BİLGİ] basar).
    Modelden elle sha yazması BEKLENMEZ — uyarı üreticiyi işaret eder."""
    tz = _tazelik_modulu()
    if tz is None:
        return None
    ilk3 = "\n".join((metin or "").splitlines()[:3])
    m = tz.KAYNAK_BLOK_RE.search(ilk3)
    if not m:
        return ["KAYNAK-BLOĞU EKSİK/HASHSİZ — kaynak_blogu.py kullan "
                "(ilk 3 satırda '<!-- kaynaklar: yol@sha8 ... -->' bloğu yok; "
                "tazelik_denetim.py bu ürünün bayatlığını izleyemez)"]
    # tek-satır biçiminde 'besledigi:'/'uretim:' segmentleri öğe DEĞİLDİR
    ogeler_ham = m.group(1).split("|")[0]
    tokenlar = [t.strip() for t in re.split(r"[·,]", ogeler_ham) if t.strip()]
    hashsiz = [t for t in tokenlar if not tz.KAYNAK_OGE_RE.fullmatch(t)]
    if not tokenlar or hashsiz:
        return ["KAYNAK-BLOĞU EKSİK/HASHSİZ — kaynak_blogu.py kullan "
                "(@sha8'siz öğe: %s; KAYNAK_OGE_RE hash'siz öğeyi yakalayamaz, "
                "tazelik denetimi fiilen işlevsiz kalır)"
                % (", ".join(hashsiz[:4]) if hashsiz else "öğe yok")]
    return []


# ── [Ş] ŞEKİL STANDARDI İSTİŞARİ DENETİMİ (v0.5.8.4, advisory) ─────────────
# 372 Torbalı A/B hükmü: zip + kenar yaması MASUM; şekil standardının SERT
# kapısı teslim_paketi'nde yaşar — burada yalnız GÖRÜNÜRLÜK. Üç kalem:
# pageFormat dört kenar 42.52 pt (1,5 cm — Resmî Yazışma Yönetmeliği No. 2646
# m.8), gövdede LineSpacing 0.50 (~1,5 satır) yaygınlığı, '(https://…)'
# bağlantılarının 11pt kapsamı (md_udf_html standardı).
_SEKIL_KENARLAR = ("leftMargin", "rightMargin", "topMargin", "bottomMargin")
_SEKIL_KENAR_PT = 42.52
_SEKIL_LINK_RE = re.compile(r"\(https?://")


def _sekil_utf16(s):
    """UYAP offset'leri UTF-16 code-unit sayar (bkz. udf_yaz._ym_utf16_uzunluk)."""
    return len(s.encode("utf-16-le")) // 2


def _sekil_deger_esit(deger, hedef):
    try:
        return deger is not None and abs(float(deger) - hedef) < 0.01
    except (TypeError, ValueError):
        return False


def sekil_uyarilari(udf_yolu):
    """.udf içindeki content.xml üzerinde üç İSTİŞARİ şekil kalemini denetler;
    uyarı listesi döner (boş = uyumlu görünüyor). Yalnız var/yok-uyum söyler,
    'iyi dilekçe' hükmü VERMEZ ve exit koduna ASLA dokunmaz — okunamayan
    dosyada da çökmez, GÖRÜNÜR 'denetlenemedi' uyarısı döner."""
    try:
        with zipfile.ZipFile(udf_yolu) as z:
            ad = next((n for n in z.namelist()
                       if n.lower().endswith("content.xml")), None)
            if ad is None:
                return ["şekil denetlenemedi: arşivde content.xml yok"]
            xml = z.read(ad).decode("utf-8", errors="replace")
    except Exception as e:
        return ["şekil denetlenemedi: %s açılamadı (%s)" % (udf_yolu, e)]

    uyarilar = []

    # 1) pageFormat DÖRT kenar 42.52 pt (1,5 cm)
    m = re.search(r"<pageFormat\b([^>]*)>", xml)
    if not m:
        uyarilar.append("pageFormat bulunamadı — dört kenarın 42.52 pt "
                        "(1,5 cm) olduğu doğrulanamadı")
    else:
        attrs = dict(re.findall(r'([\w:-]+)\s*=\s*"([^"]*)"', m.group(1)))
        sapan = ["%s=%s" % (k, attrs.get(k, "YOK")) for k in _SEKIL_KENARLAR
                 if not _sekil_deger_esit(attrs.get(k), _SEKIL_KENAR_PT)]
        if sapan:
            uyarilar.append("pageFormat kenarları 42.52 pt (1,5 cm — Yön. 2646 "
                            "m.8) değil: " + ", ".join(sapan))

    # 2) gövdede LineSpacing="0.50" (~1,5 satır) yaygınlığı — '0.5' de aynı değerdir
    paragraflar = re.findall(r"<paragraph\b[^>]*>", xml)
    if not paragraflar:
        uyarilar.append('paragraph öğesi bulunamadı — LineSpacing="0.50" '
                        "yaygınlığı doğrulanamadı")
    else:
        uygun = 0
        for p in paragraflar:
            mm = re.search(r'LineSpacing\s*=\s*"([^"]+)"', p)
            if mm and _sekil_deger_esit(mm.group(1), 0.5):
                uygun += 1
        if uygun * 2 < len(paragraflar):
            uyarilar.append('gövdede LineSpacing="0.50" (~1,5 satır aralığı) '
                            "yaygın değil (%d/%d paragraf)" % (uygun, len(paragraflar)))

    # 3) '(https://…)' bağlantıları 11pt kapsamında mı (md_udf_html standardı)
    cdata = "".join(re.findall(r"<!\[CDATA\[(.*?)\]\]>", xml, re.S))
    spanlar = []
    for sm in re.finditer(r"<content\b([^>]*?)/?>", xml):
        at = dict(re.findall(r'([\w:-]+)\s*=\s*"([^"]*)"', sm.group(1)))
        if "startOffset" not in at:
            continue  # CDATA taşıyıcısı <content> özniteliksizdir — span değildir
        try:
            bas = int(at["startOffset"])
            son = bas + int(at.get("length", "0"))
        except (TypeError, ValueError):
            continue
        spanlar.append((bas, son, at.get("size")))
    toplam, kapsam_disi = 0, 0
    for lm in _SEKIL_LINK_RE.finditer(cdata):
        toplam += 1
        off = _sekil_utf16(cdata[:lm.start()])
        if not any(b <= off < s and _sekil_deger_esit(sz, 11.0)
                   for b, s, sz in spanlar):
            kapsam_disi += 1
    if kapsam_disi:
        uyarilar.append("'(https://…)' bağlantılarının %d/%d tanesi 11pt "
                        "kapsamında görünmüyor (bağlantı gövdeden 1 punto "
                        "küçük yazılır — md_udf_html standardı)"
                        % (kapsam_disi, toplam))
    return uyarilar


# ── [J] SAYI/TARİH HARİTASI (v0.5.5.2 — BAĞIMSIZ İÇERİK HAKEMİ'nin mekanik gözü)
# 2026/307 saha vakası: mekanik kapıların TÜMÜ yeşilken, dilekçenin nakden tazmin
# savunması KENDİ başka bölümüyle aritmetik olarak çelişiyordu (karşı tarafın 836
# rakamı zaten 1100−264 idi; taslak "264, 836'nın içinde" diyordu). Böyle bir
# çelişkiyi bir script "yanlış" diye ADLANDIRAMAZ — bunun için davanın anlamını
# bilmek gerekir ve sahte kesinlik yasağı bunu men eder. Ama script çelişkinin
# GÖRÜNMESİNİ sağlayabilir: aynı sayının geçtiği tüm yerleri yan yana koyar.
# Kapı hüküm VERMEZ, GÖRÜNÜR KILAR — muhakeme hakemin/avukatındır. Advisory.
_SAYI_RE = re.compile(r"(?<![\w./,-])(\d{1,3}(?:\.\d{3})+|\d{2,})(?![\w/.,-])")
# Künye/mevzuat/tarih gürültüsü haritayı boğmasın: bu bağlamlardaki sayı atlanır.
_SAYI_GURULTU_RE = re.compile(
    r"(?:\bE\.|\bK\.|\bEsas\b|\bKarar\b|\bm\.|\bmadde\b|\bMADDE\b|\bsayılı\b|"
    r"\bTL\b|\byevmiye\b|\bsicil\b)", re.I)
_SAYI_ASGARI_TEKRAR = 2      # yalnız BİRDEN ÇOK yerde geçen sayılar haritaya girer
_SAYI_AZAMI_KALEM = 12       # rapor şişmesin — aşan sayı GÖRÜNÜR biçimde bildirilir


def _sayi_haritasi(metin):
    """Metinde ≥2 basamaklı ve BİRDEN ÇOK yerde geçen sayıları, satır no +
    kısa bağlamlarıyla gruplayarak döndürür. Döner: (kalemler, atlanan_sayi).
    Sıralama: geçiş sayısı ÇOK olandan aza, eşitlikte sayısal değere göre —
    deterministik (aynı metin → aynı rapor)."""
    metin = metin or ""
    satir_baslari = [0]
    for i, ch in enumerate(metin):
        if ch == "\n":
            satir_baslari.append(i + 1)

    def _satir(k):
        alt, ust = 0, len(satir_baslari) - 1
        while alt < ust:
            orta = (alt + ust + 1) // 2
            if satir_baslari[orta] <= k:
                alt = orta
            else:
                ust = orta - 1
        return alt + 1

    gruplar = {}
    for m in _SAYI_RE.finditer(metin):
        ham = m.group(1)
        once = metin[max(0, m.start() - 30): m.start()]
        sonra = metin[m.end(): m.end() + 12]
        if _SAYI_GURULTU_RE.search(once) or _SAYI_GURULTU_RE.search(sonra):
            continue
        deger = ham.replace(".", "")
        bag = metin[max(0, m.start() - 45): m.end() + 45].replace("\n", " ")
        bag = re.sub(r"\s{2,}", " ", bag).strip()
        gruplar.setdefault(deger, []).append((_satir(m.start()), bag))

    kalemler = [(d, yerler) for d, yerler in gruplar.items()
                if len(yerler) >= _SAYI_ASGARI_TEKRAR]
    kalemler.sort(key=lambda t: (-len(t[1]), int(t[0])))
    atlanan = max(0, len(kalemler) - _SAYI_AZAMI_KALEM)
    return kalemler[:_SAYI_AZAMI_KALEM], atlanan


# ── [Y] HAVADA-KALAN ALINTI KAPISI (346 saha dersi) ────────────────────────
# Sınıflandırma ÖNCE gelir (saha dersi: akış-içi alıntıya kapanış eklemek
# metni bozar): (a) akış-bağlı temiz · (b) '...' ile kesik + kapanışsız BLOK ·
# (c) kapanmayan tırnak BLOK · (d) alıntı-dışı serbest '...' yalnız uyarı.
_Y_TIRNAK_KAPANIS = {'"': '"', "“": "”", "«": "»"}
_Y_ELIPS_SON_RE = re.compile(r"(\.{3}|…)\s*$")
_Y_ELIPS_RE = re.compile(r"\.{3}|…")
# (a)+(b) ortak kuyruk deseni: tırnaktan SONRA gelen akış/kapanış kalıpları —
# 'şeklinde(dir)', 'biçiminde', 'ifadesiyle/ifadesine/ifade edilmiştir',
# 'denilmiş(tir)', 'belirtilmiştir', 'vurgulanmıştır', 'sonucuna varılmıştır',
# 'yer verilmiştir', 'yönünde', 'gerekçesiyle', 'değerlendirmesi'.
_Y_AKIS_KAPANIS_RE = re.compile(
    r"\bşeklinde|\bbiçiminde|\bifadesi\w*|\bifade\s+edil\w*|\bdenil\w*|"
    r"\bden(?:mek|miş)\w*|\bbelirtil\w*|\bvurgulan\w*|\bsonucuna\s+var\w*|"
    r"\byer\s+veril\w*|\byönünde|\bgerekçesiyle|\bdeğerlendirme")


def _y_tirnak_boluntule(parca):
    """Bir paragraftaki tırnak segmentlerini ayırır. Döner:
    (kapali_segmentler, acik_baslangic) — kapali: (icerik, bas, son_dahil_degil);
    acik_baslangic: kapanmamış tırnağın indeksi ya da None. Düz `\"` için
    açılış/kapanış sıralı eşlenir; kıvrık “” ve «» çifti açıkça eşlenir."""
    segmentler, acik = [], None
    for i, ch in enumerate(parca):
        if acik is None:
            if ch in _Y_TIRNAK_KAPANIS:
                acik = (i, _Y_TIRNAK_KAPANIS[ch])
        elif ch == acik[1]:
            segmentler.append((parca[acik[0] + 1:i], acik[0], i + 1))
            acik = None
    return segmentler, (acik[0] if acik else None)


def _y_kirp(parca, bas, uzunluk=60):
    return " ".join(parca[bas:bas + uzunluk].split())


def havada_kalan_alinti_denetle(metin):
    """(bloklar, uyarilar) döndürür — bloklar (b)/(c) sınıfı (teslim engeli),
    uyarilar (d) sınıfı (serbest '...'). (a) akış-bağlı alıntı hiçbir listeye
    GİRMEZ (DOKUNULMAZ). '>' satırları birebir blok-alıntıdır, taranmaz."""
    bloklar, uyarilar = [], []
    for ham in re.split(r"\n\s*\n", metin or ""):
        satirlar = [s for s in ham.splitlines() if not s.lstrip().startswith(">")]
        parca = "\n".join(satirlar).strip()
        if not parca:
            continue
        segmentler, acik = _y_tirnak_boluntule(parca)
        if acik is not None:
            bloklar.append(
                "(c) açılan tırnak paragraf sonunda KAPANMIYOR: "
                f"„…{_y_kirp(parca, acik)}…” — alıntı ya kapatılmalı ya da "
                "tırnak kaldırılmalı (avukat gözü şart)")
        for icerik, bas, son in segmentler:
            if not _Y_ELIPS_SON_RE.search(icerik.rstrip()):
                continue  # '...' ile kesilmemiş alıntı bu kapının konusu değil
            kuyruk = parca[son:]
            if _Y_AKIS_KAPANIS_RE.search(kuyruk):
                continue  # (a) akış-bağlı / kapanış kalıplı — DOKUNULMAZ
            bloklar.append(
                "(b) havada-kalan alıntı: „…" + _y_kirp(parca, bas) + "…” — "
                "'...' ile kesilmiş ve kapanış kalıbı (denilmiştir/şeklindedir/"
                "ifade edilmiştir/belirtilmiştir/vurgulanmıştır) taşımadan "
                "paragraf bitiyor; alıntı cümleye bağlanmalı")
        # (d) alıntı-dışı serbest '...': tırnak içleri maskelenir, kalan taranır
        maske = list(parca)
        for _icerik, bas, son in segmentler:
            maske[bas:son] = " " * (son - bas)
        if acik is not None:
            maske[acik:] = " " * (len(parca) - acik)
        disari = "".join(maske)
        m = _Y_ELIPS_RE.search(disari)
        if m:  # (d) her paragraf için EN FAZLA bir uyarı — gürültü kontrolü
            uyarilar.append(
                "(d) alıntı-dışı serbest '...': „…"
                + _y_kirp(disari, max(0, m.start() - 30)) + "…” — kesik anlatım "
                "sinyali; bilinçli üslupsa dokunulmaz (uyarı, engel değil)")
    return bloklar, uyarilar


# ── [M] MADDE NUMARASI SÜREKLİLİĞİ (346 saha dersi, uyarı sınıfı) ──────────
_M_MADDE_RE = re.compile(r"^\s{0,3}(\d{1,3})[.)]\s+\S")
_M_BASLIK_RE = re.compile(r"^\s{0,3}#{1,6}\s")


def madde_numara_uyarilari(metin):
    """Numaralı madde dizilerinde ATLAMA ve MÜKERRERLİK uyarıları (uyarı
    sınıfı — BLOK değil, yazım tarzları değişkendir). Bölüm başlığı (#) yeni
    sayaç başlatır: bölüm başına 1'den yeniden başlamak MEŞRUDUR. Tarih
    satırları ('01.01.2026') madde numarası desenine girmez (rakam + [.)] +
    BOŞLUK zorunlu)."""
    uyarilar = []
    bolum, bolumler = [], []
    bolumler.append(bolum)
    for satir in (metin or "").splitlines():
        if _M_BASLIK_RE.match(satir):
            bolum = []
            bolumler.append(bolum)
            continue
        m = _M_MADDE_RE.match(satir)
        if m:
            bolum.append(int(m.group(1)))
    for numaralar in bolumler:
        if not numaralar:
            continue
        sayim = {}
        for n in numaralar:
            sayim[n] = sayim.get(n, 0) + 1
        for n in sorted(k for k, c in sayim.items() if c > 1):
            uyarilar.append(
                f"mükerrer madde numarası: {n} ({sayim[n]} kez) — ekleme "
                "sırasında bir blok İKİNCİ KEZ doğmuş olabilir (saha: 1-5 ve "
                "28-31 mükerrerliği); avukat gözden geçirmeli")
        onceki = None
        for n in numaralar:
            if onceki is not None and n > onceki + 1:
                uyarilar.append(
                    f"madde numarası atlaması: {onceki} → {n} (aradaki "
                    f"{onceki + 1}..{n - 1} görünmüyor) — bilinçli değilse dizi onarılmalı")
            onceki = n
    return uyarilar


# ── [N] ÇIPLAK KISALTMA (346 saha dersi, uyarı sınıfı) ─────────────────────
# Beyaz liste ÖRNEKLEMDİR (numerus clausus değil): görev listesi (HMK, TTK,
# TBK, TMK, CMK, İYUK, AYM, BAM, E., K., md.) + aynı sınıftan yaygın hukuki
# daire/kanun kısaltmaları + sistem damgaları (TC/UYAP/OCR/UDF/RG). 'E.', 'K.',
# 'md.' tek harfli/noktalı biçimler {2,} desenine zaten girmez — belge amaçlı.
_N_BEYAZ_LISTE = {
    "HMK", "TTK", "TBK", "TMK", "CMK", "İYUK", "IYUK", "AYM", "BAM",
    "HD", "CD", "HGK", "CGK", "TCK", "İİK", "IIK", "AİHM", "AIHM", "KVKK",
    "TC", "UYAP", "OCR", "UDF", "RG",
}
_N_KISALTMA_RE = re.compile(r"(?<!\w)[A-ZÇĞİÖŞÜ]{2,5}(?!\w)")
_N_ROMEN_RE = re.compile(r"[IVXLCDM]+")
_N_KUCUK_HARF_RE = re.compile(r"[a-zçğıöşü]")
_N_AZAMI_UYARI = 8


def ciplak_kisaltma_uyarilari(metin):
    """Tam açılımı hiçbir yerde verilmemiş 2+ büyük harfli kısaltmalar için
    uyarı listesi (uyarı sınıfı — BLOK değil). MUAFİYETLER: tırnak/'>' birebir
    alıntı içi (alıntı metnine müdahale edilemez), beyaz liste, romen rakamı,
    tamamı-büyük başlık satırı ve tamamı-büyük ibarenin parçası olan sözcük."""
    metin = metin or ""
    # tırnak spanları (kapanmamış tırnak paragraf/metin sonuna kadar alıntıdır)
    spanlar, acik = [], None
    for i, ch in enumerate(metin):
        if acik is None:
            if ch in _Y_TIRNAK_KAPANIS:
                acik = (i, _Y_TIRNAK_KAPANIS[ch])
        elif ch == acik[1]:
            spanlar.append((acik[0], i + 1))
            acik = None
    if acik is not None:
        spanlar.append((acik[0], len(metin)))

    def _tirnak_icinde(k):
        return any(b <= k < s for b, s in spanlar)

    adaylar = []
    gorulen = set()
    for sm in re.finditer(r"[^\n]+", metin):
        satir = sm.group(0)
        if satir.lstrip().startswith(">"):
            continue  # birebir blok-alıntı — MUAF
        if not _N_KUCUK_HARF_RE.search(satir):
            continue  # tamamı-büyük başlık/damga satırı — kısaltma bağlamı değil
        for m in _N_KISALTMA_RE.finditer(satir):
            tok = m.group(0)
            if tok in gorulen or tok in _N_BEYAZ_LISTE or _N_ROMEN_RE.fullmatch(tok):
                continue
            if _tirnak_icinde(sm.start() + m.start()):
                continue  # birebir alıntı içi — MUAF
            once, sonra = satir[:m.start()], satir[m.end():]
            if (re.search(r"[A-ZÇĞİÖŞÜ]{2,}[\s:;,.\-]*$", once)
                    or re.search(r"^[\s:;,.\-]*[A-ZÇĞİÖŞÜ]{2,}", sonra)):
                continue  # tamamı-büyük ibarenin parçası ('TESLİME HAZIR' gibi)
            gorulen.add(tok)
            adaylar.append(tok)
    uyarilar = []
    for tok in adaylar:
        if (re.search(r"\(\s*%s\s*\)" % re.escape(tok), metin)
                or re.search(r"(?<!\w)%s\s*\(" % re.escape(tok), metin)):
            continue  # 'Açılım (KIS)' ya da 'KIS (Açılım)' — açılım verilmiş
        uyarilar.append(
            f"çıplak kısaltma '{tok}' — metinde tam açılımı görünmüyor; ilk "
            "geçtiği yerde 'Açılım (KISALTMA)' biçiminde açılmalı (mahkeme "
            "metni okuyucuya kısaltma sözlüğü borçlu bırakmaz)")
    if len(uyarilar) > _N_AZAMI_UYARI:
        kirpilan = len(uyarilar) - _N_AZAMI_UYARI
        uyarilar = uyarilar[:_N_AZAMI_UYARI]
        uyarilar.append(f"(+{kirpilan} çıplak kısaltma adayı daha — rapor "
                        f"{_N_AZAMI_UYARI} kalemle sınırlı, taslağı elle tarayın)")
    return uyarilar


# ── [T] TESLİME-HAZIR MAKBUZ KAPISI (346 saha dersi — makbuz garantisi) ────
# İbare BÜYÜK HARFLİ damga biçiminde aranır ('TESLİME HAZIR' — teslim_paketi
# çıktı damgasıyla aynı yüzey); olumsuzlanmış geçişler ('hiç TESLİME HAZIR
# olmamış' — pipeline_kayit uyarı metni) hazır-BEYANI değildir, sayılmaz.
_T_HAZIR_RE = re.compile(r"TESL[İI]ME\s+HAZ[İI]R")
# H3b (v0.5.8.6, 777 saha dersi): 'YEŞİL MAKBUZ' iddiası da aynı damga
# yüzeyinden aranır — bayat teslim_paketi stdout'u bir .txt'ye yönlendirilip
# kanonik defter/teslim-makbuz.json HİÇ YOKKEN 'yeşil makbuz' beyan edilmişti.
_T_YESIL_MAKBUZ_RE = re.compile(r"YE[ŞS][İI]L\s+MAKBUZ")
_T_OLUMSUZ_SONRA_RE = re.compile(
    r"^\s*(olmam[ıi]ş|olmad[ıi]|de[ğg]il|DE[ĞG][İI]L|yok|YOK|üretilmedi|ÜRET[İI]LMED[İI])")
_T_OLUMSUZ_ONCE_RE = re.compile(r"hi[çc]\s*$|henüz\s*$", re.I)

# H3c (v0.5.8.6) — KANONİK TANIM: her [T] bulgusuna eklenen tek-cümle tanım.
_T_KANONIK_TANIM = ("yeşil makbuz = YALNIZ _oa/defter/teslim-makbuz.json "
                    "(exit_kodu=0); stdout dökümü/txt makbuz DEĞİLDİR")


def _teslim_makbuzu_gecerli_mi(taban):
    """_oa/defter/teslim-makbuz.json var + JSON okunuyor + exit_kodu==0 mu.
    (teslim_paketi.py makbuzu yalnız başarıda bu adla yazar; RED denemesi
    teslim-makbuz-RED.json'dur — o makbuz DEĞİLDİR.)"""
    yol = os.path.join(taban, "_oa", "defter", "teslim-makbuz.json")
    if not os.path.isfile(yol):
        return False
    try:
        with open(yol, encoding="utf-8") as f:
            veri = json.load(f)
        return int(veri.get("exit_kodu", 0)) == 0
    except Exception:
        return False


def _beyan_var_mi(icerik, desen):
    """`desen` ile yakalanan damga-ibare, olumsuzlanmamış EN AZ BİR geçişte
    varsa True ('hiç ... olmamış' / '... yok' beyan DEĞİLDİR)."""
    for m in desen.finditer(icerik or ""):
        if _T_OLUMSUZ_SONRA_RE.search(icerik[m.end():m.end() + 20]):
            continue
        if _T_OLUMSUZ_ONCE_RE.search(icerik[max(0, m.start() - 10):m.start()]):
            continue
        return True
    return False


# B-29 (v0.5.14): `_t_beyan_var_mi` sarmalayıcısı SİLİNDİ — depo genelinde 0
# çağrıydı (tek satır: tanımın kendisi); gerçek kapı `_beyan_var_mi`'yı
# doğrudan çağırıyor. Ölü sarmalayıcı zararsız görünür ama "bu kapı var"
# yanılsaması üretir — ailenin en pahalı deseninin sahte kopyasıdır.


def teslime_hazir_ihlalleri(metin, kok):
    """'TESLİME HAZIR' ibaresi (makbuzsuz hazır-beyanı) YA DA 'YEŞİL MAKBUZ'
    iddiası (H3b — kanonik olmayan makbuz beyanı) taslakta ya da kökün _oa/
    *.md YAŞAYAN belgelerinde geçiyor ama geçerli teslim makbuzu yoksa BLOK
    sınıfı ihlal listesi döner. Kök verilmemişse CWD'ye düşer
    (`_antitez_matris_dosyalari` ile simetrik — kanonik hat CWD=kok koşar)."""
    taban = kok if kok else "."
    hazir_yerler, yesil_yerler = [], []
    if _beyan_var_mi(metin, _T_HAZIR_RE):
        hazir_yerler.append("denetlenen taslak")
    if _beyan_var_mi(metin, _T_YESIL_MAKBUZ_RE):
        yesil_yerler.append("denetlenen taslak")
    oa = os.path.join(taban, "_oa")
    if os.path.isdir(oa):
        # TARİHÇE MUAFİYETİ (v0.5.8.5, 346 prova bulgusu): oturum/ ve devir/
        # dizinleri GEÇMİŞ koşuların kayıtlarıdır — tarih kaydı beyan değildir;
        # taransaydı eski bir koşunun hatası kökü KALICI bloğa çevirirdi.
        # [T] yalnız YAŞAYAN belgeleri denetler (00-TESLIM, DURUM, kök notlar).
        # H3b: aynı muafiyet 'YEŞİL MAKBUZ' iddiası için de AYNEN geçerlidir.
        _TARIHCE_DIZINLER = {"oturum", "devir", "dersler", "arsiv-yerel"}
        for yol in sorted(glob.glob(os.path.join(oa, "**", "*.md"), recursive=True)):
            gorel = os.path.relpath(yol, oa)
            if gorel.split(os.sep)[0] in _TARIHCE_DIZINLER:
                continue
            try:
                with open(yol, encoding="utf-8", errors="replace") as f:
                    icerik = f.read()
            except Exception:
                continue
            if _beyan_var_mi(icerik, _T_HAZIR_RE):
                hazir_yerler.append(os.path.relpath(yol, taban))
            if _beyan_var_mi(icerik, _T_YESIL_MAKBUZ_RE):
                yesil_yerler.append(os.path.relpath(yol, taban))
    if (not hazir_yerler and not yesil_yerler) or _teslim_makbuzu_gecerli_mi(taban):
        return []
    ihlaller = [
        f"makbuzsuz hazır-beyanı: 'TESLİME HAZIR' ibaresi «{yer}» içinde ama "
        "_oa/defter/teslim-makbuz.json (exit_kodu=0) yok/geçersiz — R2: tek "
        "ölçüt teslim_paketi.py exit 0 + makbuzdur; makbuz üretilmeden 'hazır' "
        "İLAN EDİLEMEZ (üretildi≠teslime hazır) · " + _T_KANONIK_TANIM
        for yer in hazir_yerler]
    # H3b (777 saha dersi): stdout'un .txt'ye yönlendirilmesiyle 'yeşil makbuz'
    # BEYAN edilebiliyordu — kanonik dosya yokken bu iddia BLOK'tur.
    ihlaller += [
        f"kanonik olmayan makbuz beyanı: 'YEŞİL MAKBUZ' iddiası «{yer}» içinde "
        "ama _oa/defter/teslim-makbuz.json (exit_kodu=0) yok/geçersiz — "
        + _T_KANONIK_TANIM
        for yer in yesil_yerler]
    return ihlaller


# ── İSTİSNA DEFTERİ YAZICISI (ortak şema, append-only) ─────────────────────

def istisna_kaydi_yaz(kok, tur, ilgili, gerekce, onay="avukat"):
    """_oa/defter/istisna-kayitlari.jsonl'a ORTAK ŞEMA ile bir satır APPEND
    eder ve dosya yolunu döndürür. Şema (birden çok ajan yazar, append-only):
    {"zaman": ISO, "tur": "gizlilik-deny-override"|"kunye-istisna"|
    "yanlis-pozitif-ilani"|"dogrulama-toleransi", "ilgili": str, "gerekce":
    str, "onay": "avukat"|"otomatik-kural", "imza": arac-imzasi}. Bu yardımcı
    BİLEREK yereldir — ortak modül bağımlılığı yaratılmaz."""
    taban = kok if kok else "."
    defter = os.path.join(taban, "_oa", "defter")
    os.makedirs(defter, exist_ok=True)
    yol = os.path.join(defter, "istisna-kayitlari.jsonl")
    kayit = {
        "zaman": datetime.datetime.now().isoformat(timespec="seconds"),
        "tur": tur, "ilgili": ilgili, "gerekce": gerekce, "onay": onay,
        "imza": "dilekce_denetim.py",
    }
    with open(yol, "a", encoding="utf-8") as f:
        f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
    return yol


# ── HIZLI KİP (v0.5.9 — inline zincirin giriş noktası, İÇ API) ─────────────
# YALNIZ metin-tabanlı hızlı denetimler koşar: [Y] havada-kalan alıntı,
# [M] madde sürekliliği/mükerrerlik, [N] çıplak kısaltma, [K] cephanelik-
# ifşa, [T] teslime-hazır/yeşil-makbuz beyanı (YALNIZ kok verilmişse) ve
# [L] kaynak-bloğu ilk-satır yokluğu. .udf/zip/npx/resmî-okuyucu bacaklarına
# ASLA girmez (hız şartı: tipik 50KB taslakta < 1 sn). CLI davranışı
# DEĞİŞMEZ — main() bu fonksiyonu KULLANMAZ; dört ilke izdüşümü:
# DETERMİNİSTİK (aynı metin → aynı bulgu listesi) · TAMAMLAYICI (denetler,
# muhakeme üretmez) · KESİNTİSİZ (bulgular tek listede akar) · SÜRTÜNMESİZ
# (sessiz ret yok — koşamayan sınıf GÖRÜNÜR "[!]" bulgusudur, hata
# ne-yapmalıyı söyler).

_HIZLI_KOSAMADI = object()  # sentinel: alt denetim kendi içinde çöktü


def hizli_denetim(metin, kok=None):
    """Metin-tabanlı HIZLI denetimlerin tek-çağrılık iç API'si.

    list[str] döndürür; her bulgu "[X] kısa metin" biçimindedir ve EN KRİTİK
    ÖNCE sıralanır: BLOK sınıfı ([T] makbuz kapısı, [Y] b/c havada-kalan/
    kapanmayan alıntı) uyarı sınıfından ([Y] d, [K], [M], [N], [L]) önce
    gelir. `kok` verilmemişse [T] HİÇ koşulmaz (hızlı kip dosya sistemine
    CWD üzerinden tırmanmaz). Hiçbir koşulda exception sızdırmaz: bozuk
    girdide boş bulgu yerine TEK görünür "[!]" uyarısı döner (boş liste
    'temiz' demektir, 'denetlenemedi' demek DEĞİLDİR — ikisi karışmaz)."""
    try:
        if not isinstance(metin, str):
            return ["[!] hızlı denetim koşamadı: metin str değil "
                    f"({type(metin).__name__}) — taslağı düz metin (str) olarak "
                    "ver; boş liste dönmüyor ki 'temiz' sanılmasın"]
        meta = []

        def _kos(etiket, fn):
            try:
                return fn()
            except Exception as e:
                meta.append(f"[!] {etiket} denetimi koşamadı "
                            f"({type(e).__name__}) — bu sınıf DENETLENMEDİ; "
                            "tam denetim için dilekce_denetim.py CLI'ını koş")
                return _HIZLI_KOSAMADI

        y = _kos("[Y]", lambda: havada_kalan_alinti_denetle(metin))
        y_blok, y_uyari = ([], []) if y is _HIZLI_KOSAMADI else y
        t_ihlal = []
        if kok:
            t = _kos("[T]", lambda: teslime_hazir_ihlalleri(metin, kok))
            t_ihlal = [] if t is _HIZLI_KOSAMADI else t
        k_uyari = _kos("[K]", lambda: cephanelik_ifsa_uyarilari(metin))
        m_uyari = _kos("[M]", lambda: madde_numara_uyarilari(metin))
        n_uyari = _kos("[N]", lambda: ciplak_kisaltma_uyarilari(metin))
        l_uyari = _kos("[L]", lambda: kaynak_blogu_uyarilari(metin))

        def _liste(x):
            return [] if x is _HIZLI_KOSAMADI else list(x)

        # BLOK sınıfı önce ([T] teslim yalanı, [Y] b/c alıntı), sonra uyarılar.
        bulgular = ["[T] " + b for b in t_ihlal]
        bulgular += ["[Y] " + b for b in y_blok]
        bulgular += ["[Y] " + b for b in y_uyari]
        bulgular += ["[K] " + b for b in _liste(k_uyari)]
        bulgular += ["[M] " + b for b in _liste(m_uyari)]
        bulgular += ["[N] " + b for b in _liste(n_uyari)]
        if l_uyari is None:
            # kaynak_blogu_uyarilari sözleşmesi: None = tazelik_denetim
            # yüklenemedi → 'denetlenemedi' GÖRÜNÜR kılınır (yeşil değildir).
            bulgular.append("[L] kaynak-bloğu DENETLENEMEDİ: tazelik_denetim.py "
                            "yüklenemedi (oa-kontrol kurulu mu?) — bu bir yeşil "
                            "ışık DEĞİLDİR; kurulumu onarıp yeniden dene")
        elif l_uyari is not _HIZLI_KOSAMADI:
            bulgular += ["[L] " + b for b in l_uyari]
        return bulgular + meta
    except Exception as e:  # savunma hattı — iç API asla exception sızdırmaz
        return [f"[!] hızlı denetim koşamadı ({type(e).__name__}) — bulgular "
                "üretilemedi; tam denetim için dilekce_denetim.py CLI'ını koş"]


def makine_bloklarini_maskele(metin):
    """B-18 (v0.5.14) — `kaynakca_uret.py`'nin taslağa işlediği makine üretimi
    `## İÇTİHAT KAYNAKÇASI` bloğu avukatın GÖVDE METNİ DEĞİLDİR; denetim
    kapıları onu kendi girdileri sayınca zincir İDEMPOTANSINI kaybediyordu.

    Denetim kanıtı (2026-08-31, üç ardışık özdeş koşu, md5 izli):
    `rc=0 | hash değişti | TESLİME HAZIR` → `rc=1 | TESLİM DURDURULDU` →
    `rc=1`. Kök neden: bloğun yazdığı `⚠` işaretini ikinci koşuda [C] OCR/
    alıntı teyidi yakalıyordu. Kapı deterministik olmak ZORUNDADIR — burada
    cevap koşu sayısına bağlıydı; avukat emin olmak için tekrar koşunca
    hiçbir şey değiştirmediği hâlde kırmızı görüyor ve kapıya güven çöküyordu.

    Maskeleme mantığı TEK YERDE (`oa-kontrol/scripts/kunye_ortak.py`) yaşar —
    üretici (kaynakca_uret) ile maskeleyici ayrışamaz. Modül yüklenemezse
    metin DEĞİŞMEDEN döner (fail-safe: eski, daha SIKI davranış sürer)."""
    ko = _kunye_ortak_modulu()
    if ko is None or not hasattr(ko, "makine_blogu_maskele"):
        return metin
    try:
        return ko.makine_blogu_maskele(metin)
    except Exception:
        return metin


def denetle(metin, tip, taraf):
    # B-18: makine üretimi kaynakça bloğu denetim girdisi DEĞİLDİR.
    metin = makine_bloklarini_maskele(metin)
    eksik, uyari = [], []
    unsurlar = TIPLER.get(tip, TIPLER["genel"])

    # A) zorunlu unsurlar
    for ad, des in unsurlar:
        if not _bul(metin, des):
            eksik.append(ad)

    # B) tertip-düzen (+ [B2] kanun-yolu tip-koşullu yapısal kalemler — M3-2)
    duzen_eksik = [ad for ad, des in DUZEN if not _bul(metin, des)]
    if tip in KANUN_YOLU_TIPLERI:
        duzen_eksik += _kanun_yolu_yapisal_eksik(metin)

    # C) OCR ⚠ alıntı → teyit şerhi
    ocr_var = ("⚠" in metin) or re.search(r"\bOCR\b", metin, re.I)
    ocr_serh = re.search(r"orijinal.*teyit|teyit\s*(edil|gerek)|RG.*teyit", metin, re.I)
    ocr_uyari = bool(ocr_var and not ocr_serh)

    # D) müvekkil-aleyhi ifade (tek katı sınır) — OLUMSUZLAMA KORUMALI
    # Standart cevap kalıbı "davanın kabulü anlamına gelmemek kaydıyla" / "kabul etmediğimiz"
    # sahte alarm üretmesin: ±70 karakter penceresinde olumsuzlama varsa sinyal düşürülür.
    NEG = re.compile(r"anlamına\s*gelme|kaydıyla|etmedi[ğg]|etmiyor|etmemek|etmez|\bkabul\s*etme"
                     r"|redd|aksi|\bdeğil|olmaks[ıi]z[ıi]n|olmamak", re.I)
    aleyhe, aleyhe_notu = [], []
    for anahtar in ([taraf] if taraf in ALEYHE else []) + ["genel"]:
        for d in ALEYHE.get(anahtar, []):
            for m in re.finditer(d, metin, re.I):
                # EK-FİX (risk#2): pencere eşleşen kalıbın KENDİ aralığını İÇERMEZ.
                # Bazı aleyhe kalıpları ('şikayetçi değil', 'haklı değiliz') 'değil'i
                # kalıbın GÖVDESİ olarak taşır; eski kod pencereyi m.start()-70..m.end()+70
                # (eşleşmenin kendisi dahil) alıyordu → NEG deseni ('değil') eşleşmenin
                # içinde HER ZAMAN bulunuyor, bu kalıplar asla BLOKLAMIYOR, hep [BİLGİ]'ye
                # düşüyordu. Artık pencere yalnız eşleşmenin ÖNCESİ ve SONRASIdır — gerçek
                # bir olumsuzlama (eşleşmenin dışında) hâlâ doğru şekilde sinyali düşürür.
                once = metin[max(0, m.start() - 70): m.start()]
                sonra = metin[m.end(): m.end() + 70]
                if NEG.search(once) or NEG.search(sonra):
                    aleyhe_notu.append(m.group(0))   # olumsuzlanmış → bilgi, engel değil
                else:
                    aleyhe.append(m.group(0))

    return eksik, duzen_eksik, ocr_uyari, aleyhe, aleyhe_notu


def main():
    ap = argparse.ArgumentParser(description="dilekce_denetim.py — teslim öncesi şablon + zaaf kapısı")
    ap.add_argument("taslak")
    ap.add_argument("--tip", default="genel",
                    choices=["dava", "cevap", "istinaf", "temyiz", "aym_bireysel",
                             "yemin", "idari-kanal", "genel"])
    ap.add_argument("--taraf", default="",
                    choices=["", "davaci", "davali", "sanik", "katilan", "mudahil", "musteki"])
    ap.add_argument("--udf", metavar="YOL", default="",
                    help="(opsiyonel) Üretilmiş .udf dosyasını da GEÇERLİLİK KAPISI ile "
                         "denetler — UDF-VARSAYILAN doktrini burada mekanik olarak kapanır.")
    ap.add_argument("--ictihat-muhakeme", action="store_true", default=True,
                    help="(P1-7: VARSAYILAN AÇIK) [F] İçtihat Muhakeme Zinciri mekanik "
                         "kapısını (oa-kontrol/ictihat_muhakeme_denetim.py) da bu tek çağrıda "
                         "çalıştırır — çıplak/ALEYHE/eksik-alanlı içtihat atfı teslim engelidir. "
                         "Bayrak zaten varsayılan True olduğundan verilmesi davranışı DEĞİŞTİRMEZ "
                         "(geriye uyum için tutulur); kapatmak için --ictihat-muhakeme-yok kullan.")
    ap.add_argument("--ictihat-muhakeme-yok", action="store_true",
                    dest="ictihat_muhakeme_yok",
                    help="(opsiyonel) P0-5 DÜZELTME(c) çift-[F] tekilleştirme: [F] kapısını "
                         "HER KOŞULDA (ileride --ictihat-muhakeme VARSAYILANI değişse dahi) "
                         "kapalı tutan AÇIK override — teslim_paketi.py bunu (a) çağrısına "
                         "BİLİNÇLİ geçirir çünkü İçtihat Muhakeme Zinciri'ni kendi (b2) "
                         "adımında AYRICA çalıştırır (tek yetkili yol (b2)); bu bayrak "
                         "--ictihat-muhakeme'den ÖNCELİKLİDİR.")
    ap.add_argument("--kok", default=None,
                    help="(opsiyonel) --ictihat-muhakeme ile birlikte; çalışma kökü "
                         "(kunye_teyit.py/ictihat_muhakeme_denetim.py --kok simetrisi) — "
                         "verilmezse --muhakeme-dizin/--ictihat-dokum-dizin CWD-göreli "
                         "_oa/cikti, _oa/teyit/dokum'a düşer")
    ap.add_argument("--muhakeme-dizin", default=None,
                    help="(opsiyonel) --ictihat-muhakeme ile birlikte; verilmezse "
                         "--kok/_oa/cikti (--kok yoksa CWD-göreli _oa/cikti)")
    ap.add_argument("--istisna-gerekce", default="",
                    help="(opsiyonel) AVUKAT ONAYLI istisna: [Y] havada-kalan alıntı / "
                         "[T] makbuzsuz hazır-beyanı BLOK bulgularını görünür UYARIYA "
                         "düşürür ve gerekçeyi _oa/defter/istisna-kayitlari.jsonl'a "
                         "(ortak şema, append-only, tur=yanlis-pozitif-ilani) yazar — "
                         "sessiz opt-out yok, kapı kaydını tutarak yol verir.")
    ap.add_argument("--ictihat-dokum-dizin", default=None,
                    help="(opsiyonel) --ictihat-muhakeme ile birlikte; verilmezse "
                         "--kok/_oa/teyit/dokum (--kok yoksa CWD-göreli _oa/teyit/dokum)")
    a = ap.parse_args()
    if a.ictihat_muhakeme_yok:
        a.ictihat_muhakeme = False  # AÇIK override — --ictihat-muhakeme VARSAYILANından bağımsız

    try:
        metin = open(a.taslak, encoding="utf-8", errors="replace").read()
    except Exception as e:
        print(f"HATA: taslak okunamadı ({e})", file=sys.stderr)
        sys.exit(1)

    # B-18 (v0.5.14) — İDEMPOTANS: makine üretimi kaynakça bloğu TÜM kapılar
    # için denetim dışıdır (sessiz atlama YASAĞI: görünür not basılır).
    ham_metin = metin
    metin = makine_bloklarini_maskele(metin)
    if metin != ham_metin:
        print("[BİLGİ] Makine üretimi '## İÇTİHAT KAYNAKÇASI' bloğu denetim "
              "girdisi SAYILMADI (kaynakca_uret.py ürünü; blok içine elle "
              "yazılmış düz metin maskelenmez ve denetlenmeye devam eder) — "
              "B-18: zincirin idempotansı bu maskeleme ile korunur.")

    eksik, duzen_eksik, ocr_uyari, aleyhe, aleyhe_notu = denetle(metin, a.tip, a.taraf)
    cizgi = "=" * 62
    print(cizgi)
    print(f"DİLEKÇE DENETİMİ — tip: {a.tip} · taraf: {a.taraf or '—'}")
    print(cizgi)

    print("\n[A] ZORUNLU UNSURLAR")
    if eksik:
        for u in eksik:
            print(f"   [EKSİK] {u}")
    else:
        print("   [OK] tip için beklenen unsurlar mevcut görünüyor")

    print("\n[B] TERTİP-DÜZEN (avukata yakışan biçim)")
    if duzen_eksik:
        for u in duzen_eksik:
            print(f"   [UYARI] {u} — zayıf/görünmüyor")
    else:
        print("   [OK] başlık/bölüm/netice/imza düzeni kurulu")

    print("\n[C] OCR/⚠ ALINTI TEYİDİ")
    if ocr_uyari:
        print("   [UYARI] OCR/⚠ işareti var ama 'orijinalden teyit' şerhi görünmüyor — "
              "künye/sayısal veriyi orijinalden doğrula.")
    else:
        print("   [OK] OCR-teyit şerhi sorunu görünmüyor")

    print("\n[D] MÜVEKKİL-ALEYHİ İFADE TARAMASI (anayasal — tek katı sınır)")
    if aleyhe:
        for s in sorted(set(aleyhe)):
            print(f"   [UYARI] olası müvekkil-aleyhi ifade: \"{s}\" — avukat TEYİT ETMELİ; "
                  "dış çıktı müvekkil lehine kurgulanır (davalıda kabul/ikrar YOK).")
    else:
        print("   [OK] belirgin müvekkil-aleyhi ifade sinyali bulunamadı (heuristik)")
    if aleyhe_notu:
        print(f"   [BİLGİ] olumsuzlanmış kalıp(lar) sinyal sayılmadı (ör. 'kabul anlamına "
              f"gelmemek kaydıyla'): {', '.join(sorted(set(aleyhe_notu)))}")

    print("\n[Y] HAVADA-KALAN ALINTI KAPISI (a: akış-bağlı DOKUNULMAZ · b/c: BLOK · d: uyarı)")
    y_blok, y_uyari = havada_kalan_alinti_denetle(metin)
    for u in y_blok:
        print(f"   [BLOK] {u}")
    for u in y_uyari:
        print(f"   [UYARI] {u}")
    if not y_blok and not y_uyari:
        print("   [OK] havada-kalan/kapanmayan alıntı ve serbest '...' sinyali yok")

    print("\n[M] MADDE NUMARASI SÜREKLİLİĞİ (uyarı sınıfı — sıra tarzı değişkendir, "
          "ASLA bloklamaz)")
    m_uyarilar = madde_numara_uyarilari(metin)
    if m_uyarilar:
        for u in m_uyarilar:
            print(f"   [UYARI] {u}")
    else:
        print("   [OK] numaralı dizilerde atlama/mükerrerlik sinyali yok")

    print("\n[N] ÇIPLAK KISALTMA (uyarı sınıfı — birebir alıntı içi MUAF, ASLA bloklamaz)")
    n_uyarilar = ciplak_kisaltma_uyarilari(metin)
    if n_uyarilar:
        for u in n_uyarilar:
            print(f"   [UYARI] {u}")
    else:
        print("   [OK] açılımsız kısaltma sinyali yok (beyaz liste + alıntı muafiyeti sonrası)")

    udf_gecersiz = False
    if a.udf:
        print("\n[E] UDF GEÇERLİLİK KAPISI (UDF-VARSAYILAN doktrini)")
        udf_sonuc = udf_kapisi(a.udf)
        if udf_sonuc["gecerli"]:
            print(f"   [OK] {a.udf} geçerli UDF (zip + content.xml + XML + offset/round-trip tutarlı)")
        else:
            udf_gecersiz = True
            print(f"   [EKSİK] {a.udf} GEÇERSİZ UDF:")
            for h in udf_sonuc["hatalar"]:
                print(f"      - {h}")
        # RESMİ OKUYUCU TANIĞI — bu satır GEÇERLİ hâlde de basılır: "YAPILAMADI"
        # durumu susturulursa avukat, yalnız kendi ayrıştırıcımızın onayladığı
        # bir dosyayı UYAP'ta açılacak sanır (sahada bizi yakan hata sınıfı).
        _ro = udf_sonuc.get("resmi_okuyucu")
        if _ro == "OK":
            print("   [OK] resmî okuyucu (udf-cli udf2md) dosyayı geri okudu — "
                  f"{udf_sonuc.get('resmi_okuyucu_karakter') or 0} karakter")
        elif _ro == "YAPILAMADI":
            print("   [UYARI] resmî okuyucu doğrulaması YAPILAMADI — "
                  f"{udf_sonuc.get('resmi_okuyucu_not')}. Bu dosyanın UYAP'ta AÇILDIĞI "
                  "DOĞRULANMADI (yalnız kendi ayrıştırıcımız onayladı); teslimden önce "
                  "UYAP Doküman Editöründe elle açıp teyit edin.")

    ictihat_muhakeme_engel = False
    if a.ictihat_muhakeme_yok:
        print("\n[F] İÇTİHAT MUHAKEME ZİNCİRİ KAPISI — --ictihat-muhakeme-yok ile AÇIKÇA "
              "ATLANDI (sessiz opt-out DEĞİL; genelde teslim_paketi.py'nin (b2) kapısıyla "
              "tekilleştirme tercihidir).")
    elif a.ictihat_muhakeme:
        fail_open = _f_kapisi_fail_open_durumu(metin, a)
        if fail_open == "no_oa":
            print("\n[F] İÇTİHAT MUHAKEME ZİNCİRİ KAPISI — [BİLGİ] atlandı: _oa/ bulunamadı "
                  "(bu kök pipeline/teyit altyapısını henüz kullanmıyor) — bloklamaz.")
        elif fail_open == "no_signal":
            print("\n[F] İÇTİHAT MUHAKEME ZİNCİRİ KAPISI — [BİLGİ] atlandı: taslakta esas/karar "
                  "no'lu içtihat künyesi VE 'Yargıtay/emsal karar' benzeri anlatım hiç yok "
                  "— bloklamaz.")
        else:
            print("\n[F] İÇTİHAT MUHAKEME ZİNCİRİ KAPISI (ictihat_muhakeme_denetim.py — oa-kontrol)")
            if fail_open == "desen_var_kunye_yok":
                print("   [UYARI] künyesiz içtihat anlatımı — muhakeme zinciri denetlenemedi "
                      "('Yargıtay/Danıştay/AYM/AİHM/yerleşik içtihat/emsal karar' benzeri "
                      "anlatım var ama esas/karar no'lu bir künye yok; fail-open bunu "
                      "ATLAMAZ — G1 aşağıda ayrıca 'emsal içtihat yok' uyarısı basacaktır.)")
            muhakeme_dizin = a.muhakeme_dizin if a.muhakeme_dizin is not None else (
                os.path.join(a.kok, "_oa", "cikti") if a.kok else None)
            dokum_dizin = a.ictihat_dokum_dizin if a.ictihat_dokum_dizin is not None else (
                os.path.join(a.kok, "_oa", "teyit", "dokum") if a.kok else None)
            kod_f, cikti_f = ictihat_muhakeme_kapisi(a.taslak, a.kok, muhakeme_dizin, dokum_dizin,
                                                      tip=a.tip)
            for satir in cikti_f.splitlines():
                print(f"   {satir}")
            ictihat_muhakeme_engel = (kod_f != 0)

    print("\n[G] ANTİTEZ-CEVAP-ÇAPASI (advisory — M3, Paket D, ASLA bloklamaz)")
    g_uyarilar = antitez_cevap_capasi_uyarilari(metin, a.kok)
    if g_uyarilar:
        for u in g_uyarilar:
            print(f"   [UYARI] {u}")
    elif not _antitez_matris_dosyalari(a.kok):
        # M3 düzeltmesi (Paket D sınav bulgusu, KUCUK) — matrisin TAMAMEN
        # YOKLUĞU ile 'matris var ve tam örtüşüyor' hâli artık AYNI [OK]
        # etiketiyle raporlanmıyor: zorunlu pas girdisinin hiç koşulmamış
        # olabileceği ayrıca [BİLGİ] ile işaretlenir.
        # YENİ-2 (Paket D DÜZELTME) — `--kok` verilmemişse mekanik körlüğü
        # olgu beyanına ÇEVİRME: 'koşulmamış olabilir' yalnız kök BİLİNİYORKEN
        # (ve orada gerçekten yoksa) söylenir; kök belirsizse yalnız arama
        # yapılamadığı söylenir.
        if a.kok:
            print("   [BİLGİ] _oa/cikti/*antitez*.json bulunamadı — ANTİTEZ PASI "
                  "koşulmamış olabilir (M3: zorunlu pas girdisi)")
        else:
            print("   [BİLGİ] _oa/cikti/*antitez*.json ARANAMADI (kök belirsiz — "
                  "--kok verilmedi, CWD'ye göre arandı) — sonuç kanıt sayılmaz")
    else:
        print("   [OK] karşılıksız DUYULMUŞ antitez sinyali bulunamadı (matris tam örtüşüyor)")

    print("\n[H] GÖRÜNMEZ İSKELET TARAMASI (advisory — P1-11 ek kural, ASLA bloklamaz)")
    h_uyarilar = _gorunmez_iskelet_uyarilari(metin)
    if h_uyarilar:
        for u in h_uyarilar:
            print(f"   [UYARI] {u}")
    else:
        print("   [OK] görünür kalıp-etiket sinyali bulunamadı (heuristik)")

    print("\n[K] m.6 CEPHANELİK BEKÇİSİ (v0.5.8.1 — advisory, ASLA bloklamaz)")
    k_uyarilar = cephanelik_ifsa_uyarilari(metin)
    # v0.5.8.4 İZ SATIRI — 372 karnesi 0-bulgu hâlini KANITLAYAMADI (iz yoksa
    # 'koştu ve temizdi' ile 'hiç koşmadı' ayrılamaz); sayı HER koşuda basılır.
    print(f"   [K] cephanelik: {len(k_uyarilar)} bulgu")
    if k_uyarilar:
        for u in k_uyarilar:
            print(f"   [UYARI] {u}")
    else:
        print("   [OK] dilekçede muhtemel-savunma analizi kalıbı bulunamadı (heuristik)")

    print("\n[I] KUSUR→SONUÇ→TALEP ASİMETRİSİ TARAMASI (advisory — P1-11 ek kural, ASLA bloklamaz)")
    i_uyarilar = _kusur_sonuc_talep_asimetri_uyarilari(metin)
    if i_uyarilar:
        for u in i_uyarilar:
            print(f"   [UYARI] {u}")
    else:
        print("   [OK] karşı-taraf-kusuru bağlamında onarma-talebi sinyali bulunamadı (heuristik)")

    print("\n[J] SAYI/TARİH HARİTASI (advisory — BAĞIMSIZ İÇERİK HAKEMİ'nin gözü, ASLA bloklamaz)")
    j_kalemler, j_atlanan = _sayi_haritasi(metin)
    if j_kalemler:
        print("   Aynı sayının geçtiği yerler yan yana — script çelişkiyi SÖYLEMEZ, GÖRÜNÜR KILAR;")
        print("   her rakamın taslağın KENDİ diğer bölümüyle aynı hesabı verdiğini AVUKAT doğrular.")
        for deger, yerler in j_kalemler:
            print(f"   • {deger} ({len(yerler)} yerde)")
            for satir, bag in yerler[:4]:
                print(f"       satır {satir}: …{bag}…")
            if len(yerler) > 4:
                print(f"       (+{len(yerler) - 4} geçiş daha)")
        if j_atlanan:
            # Sessiz kırpma yasağı: kırpıldıysa KAÇ TANE olduğu söylenir.
            print(f"   NOT: {j_atlanan} sayı daha birden çok yerde geçiyor (rapor {_SAYI_AZAMI_KALEM} "
                  f"kalemle sınırlı) — tamamı için taslağı elle tarayın.")
    else:
        print("   [OK] birden çok yerde geçen sayı bulunmadı (çapraz-hesap riski düşük)")

    print("\n[L] KAYNAK-BLOĞU (advisory — v0.5.8.4, ASLA bloklamaz)")
    if a.taslak.lower().endswith(".udf"):
        print("   [BİLGİ] taslak .udf — kaynak-bloğu denetimi md ürünlere özgüdür, atlandı")
    else:
        l_uyarilar = kaynak_blogu_uyarilari(metin)
        if l_uyarilar is None:
            print("   [BİLGİ] tazelik_denetim.py yüklenemedi (oa-kontrol kurulu mu?) — "
                  "kaynak-bloğu DENETLENEMEDİ (bu bir yeşil ışık DEĞİLDİR)")
        elif l_uyarilar:
            for u in l_uyarilar:
                print(f"   [UYARI] {u}")
        else:
            print("   [OK] kaynaklar bloğu ilk 3 satırda ve tüm öğeler @sha8'li")

    print("\n[T] TESLİME-HAZIR MAKBUZ KAPISI (makbuzsuz hazır-beyanı = görünür ihlal, BLOK)")
    t_ihlaller = teslime_hazir_ihlalleri(metin, a.kok)
    if t_ihlaller:
        for u in t_ihlaller:
            print(f"   [BLOK] {u}")
    else:
        print("   [OK] makbuzsuz 'TESLİME HAZIR' / kanonik olmayan 'YEŞİL MAKBUZ' "
              "beyanı yok (ibare yok ya da makbuz geçerli)")

    sekil_yolu = a.udf or (a.taslak if a.taslak.lower().endswith(".udf") else "")
    if sekil_yolu:
        print("\n[Ş] ŞEKİL STANDARDI (advisory — v0.5.8.4, ASLA bloklamaz; "
              "SERT kapı teslim_paketi'nde)")
        s_uyarilar = sekil_uyarilari(sekil_yolu)
        if s_uyarilar:
            for u in s_uyarilar:
                print(f"   [UYARI] {u}")
        else:
            print("   [OK] kenar 42.52 · LineSpacing 0.50 · bağlantılar 11pt — "
                  "şekil standardı uyumlu görünüyor")

    # AVUKAT ONAYLI İSTİSNA — [Y]/[T] BLOK bulguları --istisna-gerekce ile görünür
    # uyarıya düşer; gerekçe istisna defterine (append-only, ortak şema) yazılır.
    # Kayıt YALNIZ fiilen düşürülen bir bulgu varken atılır (defter kirletilmez).
    yeni_blok_istisnali = False
    if (y_blok or t_ihlaller) and a.istisna_gerekce:
        ilgili = a.taslak + " [" + "/".join(
            e for e, var in (("Y", y_blok), ("T", t_ihlaller)) if var) + "]"
        defter_yolu = istisna_kaydi_yaz(a.kok, "yanlis-pozitif-ilani",
                                        ilgili, a.istisna_gerekce)
        print(f"\n[Y/T] avukat onaylı istisna: BLOK bulguları UYARIYA düşürüldü; "
              f"gerekçe istisna defterine yazıldı: {defter_yolu}")
        yeni_blok_istisnali = True

    print("\n" + cizgi)
    engel = bool(eksik or ocr_uyari or aleyhe or udf_gecersiz or ictihat_muhakeme_engel
                 or ((y_blok or t_ihlaller) and not yeni_blok_istisnali))
    if engel:
        print("SONUÇ: TESLİM ÖNCESİ AVUKAT GÖZÜ ŞART (eksik unsur / aleyhe sinyal / teyit şerhi "
              "/ ictihat muhakeme kapısı / havada-kalan alıntı / makbuzsuz hazır-beyanı).")
        print(cizgi)
        sys.exit(1)
    print("SONUÇ: temel şablon denetimi temiz (nihai sorumluluk avukatındır).")
    print(cizgi)
    sys.exit(0)


if __name__ == "__main__":
    main()

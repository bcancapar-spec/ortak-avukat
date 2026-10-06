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
                                  (v0.5.18: + icra ailesi, idari-dava, yd-talebi,
                                   ceza-istinaf — tam liste `--help`)
                            [--taraf davaci|davali|sanik|katilan|mudahil|musteki|
                                     alacakli|borclu|ucuncu-kisi]
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

── [F] HAFİF KİP (v0.5.16 — K3, Hamle 1; yalnız `hizli_denetim`) ─────────
Tam [F] kapısı ayrı süreçte kalır (teslimde yetkili). Hızlı kip (inline
PostToolUse zinciri, 2 sn) in-process ve yalnız yerel kütükle koşar:
`kunye_ortak.esas_karar_atiflari` ile künyeleri çıkarır, `_oa/teyit/
kunye-teyit.md`'de SON DAMGA'yı `kunye_ortak.kutukten_son_damga` ile okur.
ALEYHE → "m.6 teslim engeli adayı", NOTR → "dilekçeye giremez", kütükte
satır yok → "çıplak künye adayı", damgasız satır → "muhakeme edilmemiş";
LEHE/ALEYHE-AYIRT sessiz. kunye_ortak/kütük yoksa GÖRÜNÜR bilgi satırı
(yalnız künye varken). [F] satırları bulgu listesinin EN BAŞINDA gelir.

── [P] NETİCE-İ TALEP (v0.5.16 — P0-4/A-22, advisory — ASLA bloklamaz) ────
Talep bloğunu (NETİCE-İ TALEP / SONUÇ VE İSTEM / NETİCE VE TALEP / TALEP
başlığından metnin sonuna) bulur; para ifadesi varken faiz türü VE
başlangıcı, 'kısmi dava/belirsiz alacak/şimdilik' varken 'fazlaya ilişkin',
'yargılama gideri/vekâlet ücreti' yokluğunu uyarır; blok yoksa 'bulunamadı'
(CLI'da; hızlı kip yarım taslakta bu satırı basmaz). Hukuki yorum YOK —
faiz türü seçimi avukat kararı (SKILL.md NETİCE-İ TALEP PLAYBOOK'U).

── [N] TARAF/ROL BEYAZ LİSTESİ (v0.5.16 — H2, Hamle 11) ────────────────────
SANIK/ŞÜPHELİ/HÜKÜMLÜ/MAĞDUR/MÜŞTEKİ/KATILAN/MÜDAHİL/DAVACI/DAVALI/ALACAKLI/
BORÇLU/VEKİL(İ)/MÜVEKKİL/TANIK/İDARE/DAVA/KARAR/ESAS/MADDE (+KONU/MÜDAFİ(İ)/
TARİH) etiketleri kısaltma DEĞİLDİR — [N] üretmez (örneklem, m.3).

── v0.5.18 (aday) — İCRA AİLESİ + Y-06 KAPI SIKILAŞTIRMASI ────────────────
NEDEN VAR: kapı icra dilekçelerini tanımıyordu (takip talebi, ödeme emrine/
kambiyo itirazı, şikâyet, haciz/satış, ihalenin feshi, itirazın iptali/
kaldırılması, menfi tespit, istihkak, icra ceza, usul işlemleri `--tip genel`
ile denetleniyor, İİK'nın kendine özgü zorunlu içeriği hiç aranmıyordu) ve
3 Ekim 2026 yetenek denetiminin Y-06 bulgusu dört açık saydı: dava değeri
ayrı unsur değil; bileşik unsurda tek desen yetiyor; idari dava ve ceza
istinafı tipi yok. Fikir kaynağı Yargı PRO 3-1…3-9, 2-6, 4-4 (yalnız fikir;
metin/kod alınmadı); her madde Yargı PRO MCP ile resmî metinden 2026-10-05'te
okundu — insan-okur cetvel: `references/icra-dilekce-ailesi.md`,
`references/idari-ceza-tipleri.md`.
  * UNSUR MODELİ: tekil unsur (desenlerden biri yeter — eski davranış) ·
    `Bilesik` (her PARÇA ayrı ayrı karşılanmalı; eksik parça adıyla raporlanır)
    · `Yakin` (çapanın ardındaki/önündeki pencerede arama — alacaklının adresi
    borçlunun adres eksiğini, imza tarihi tebliğ tarihi eksiğini örtmez) ·
    `Kosullu` (yalnız koşul metinde varsa zorunlu; istisna deseni koşulu
    kaldırır). `denetle()`'nin imzası ve 5'li dönüşü DEĞİŞMEDİ; bileşik eksik
    "ad — eksik parça: …" biçiminde [A] listesine düşer.
  * SÜRE ↔ [A]: süre başlangıcının TARİHİ (tebliğ/öğrenme/ödeme/maninin
    kalkması) olayın yanında aranır; "yedi gün içinde" gibi süre İFADESİ yasal
    içerik değildir, aranmaz — süre [S] ile oa-sure'ye bağlanır. "Tebliğ
    edilmemiştir/edilmeden" beyanı tarih unsurunu kaldırır (tebliğden önce
    başvuru hakkı).
  * YENİ TİPLER: takip-talebi, odeme-emrine-itiraz, kambiyo-itiraz,
    gecikmis-itiraz, itirazin-kaldirilmasi, itirazin-iptali, menfi-tespit,
    haciz-talebi, satis-talebi, haciz-ihbarnamesi-itiraz, kiymet-takdiri-sikayet,
    ihalenin-feshi, icra-sikayet, istihkak-davasi, icra-ceza-sikayet, icra-usul,
    idari-dava, yd-talebi, ceza-istinaf.
  * SIKILAŞAN ESKİ TİPLER: istinaf (tebliğ tarihi HMK m.342/2-ç ayrı; mahkeme +
    sayı ve tarih + imza birlikte), temyiz (HMK m.364/2-d tebliğ tarihi ayrı),
    aym_bireysel (hak + Anayasa hükmü, kimlik + adres ayrı parçalar; ekler ve
    vekâletname — 6216 m.47/3-4). Eski `dava` tipinde dava değeri (HMK
    m.119/1-d) ve taraf adres/TCKN'si BLOKLAYICI DEĞİL, [A] altında görünür
    uyarıdır (mevcut kilit testler değer satırsız para talepli taslağın temiz
    geçmesini bekliyor — karar avukatın/ana ajanın).
  * TİPE ÖZEL İSTİŞARİ UYARILAR (`tip_ozel_uyarilari` — exit koduna ASLA
    dokunmaz): faizsiz takip, TCKN/VKN ("varsa" — m.58/2), imza/kira akdi
    reddi (m.62 imza fıkrası, m.269/2), kötü niyet/inkâr tazminatı ve tedbir
    istemleri, kambiyoda geçici durdurma (risk notuyla — m.169/a-6, m.170/3),
    üçüncü kişinin dürüst borç beyanı (m.89/4, m.338/1), yanlış merci, istinafta
    karar tarihi (HMK m.342/2-c), teminat ve ikinci YD istemi yasağı (İYUK
    m.27/6, 27/10) gibi kalemler.
  * [S] SÜRE BAĞLANTISI (bilgi, ASLA bloklamaz): tipin bağlı olduğu madde ve
    `oa-sure/scripts/sure_kurallari.json` içinde o maddeyi taşıyan kural
    kimliği ÇALIŞMA ANINDA aranır; bulunamazsa "TEYİT BEKLİYOR" yazılır. Süre
    HESABI oa-sure'ündür — burada hesap YOKTUR.
  * YENİ TARAF SIFATLARI: alacakli, borclu, ucuncu-kisi (icra kalıp setleri +
    davacı/davalı eksenleri). `menfi-tespit` tipinde borçlu DAVACI, alacaklı
    DAVALI konumundadır; `kambiyo-itiraz` tipinde borcun kısmen kabulü ayrıca
    taranır (m.170/a-3); `haciz-ihbarnamesi-itiraz` tipinde üçüncü kişinin borç
    beyanı BLOK değil uyarıdır — tarama ekseni tipe göre çevrilir
    (`aleyhe_kapsami(taraf, tip)`; tek argümanlı eski çağrı aynen çalışır).
  * `(?#kesin)` KALIPLAR: çekimli olumlu yüklemle biten ikrar kalıpları
    ('itirazımızdan vazgeçiyoruz', 'borcun tamamını kabul ediyoruz') ±70 NEG
    penceresinden muaftır — komşu 'aksi/değil/redd' sözcüğü gerçek ikrarı
    BİLGİ'ye düşüremez. Olumsuz çekim ('vazgeçmiyoruz', 'vazgeçmeyeceğiz')
    kalıp gövdesinde dışlanır; olumlu '-mek/-mekte' biçimleri yakalanır.

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

# ── v0.5.18 — UNSUR MODELİ: tekil · bileşik · yakınlık · koşullu (Y-06) ──────
# NEDEN VAR: unsurlar düz desen listesiyle tanımlıydı ve listedeki HERHANGİ bir
# desen unsuru "var" saydırıyordu. Kanunun iki ayrı şart koyduğu yerde (6216
# m.47/3 "ihlal edildiği ileri sürülen hak VE dayanılan Anayasa hükümleri";
# HMK m.342/2-ç tebliğ tarihi) kapı tek şartı görüp geçiyordu — 'hak' kelimesi
# tek başına AYM unsurunu, 'süre' kelimesi tek başına tebliğ tarihini
# karşılıyordu. Eski düz-liste biçimi AYNEN geçerlidir (geri uyum); yeni
# biçimler yalnız gerektiği yerde kullanılır.

class Bilesik(tuple):
    """BİLEŞİK unsur: (('parça etiketi', desenler), ...) — HER parça ayrı ayrı
    karşılanmalı (parçalar arası VE, parça içi VEYA). Eksik parça adıyla
    raporlanır ki avukat neyin eksik olduğunu aramak zorunda kalmasın.
    Parça deseni düz liste ya da `Yakin` olabilir."""
    __slots__ = ()


class Yakin:
    """YAKINLIK parçası: `capa` desenlerinden birinin geçtiği her yerin
    ARDINDAKİ `pencere` (ve istenirse ÖNCESİNDEKİ `geri`) karakter içinde
    `hedef` desenlerinden biri aranır.

    NEDEN VAR: bileşik denetim belgenin tamamında arar; takip talebinde
    alacaklının adresi borçlunun adres eksiğini örterdi (İİK m.58/2-1 ve 2-2
    adresi TARAF BAŞINA ister; m.62 borçlunun yurt içi adresini ayrıca ister).
    Aynı kör nokta tebliğ tarihinde vardı: 'tebliğ' kelimesi ile imza
    tarihinin belgede AYRI AYRI geçmesi "tebliğ tarihi var" saydırıyordu
    (Fable 5.1 salt okunur incelemesi, 2026-10-05); HMK m.342/2-ç ve
    m.364/2-d zorunlu içeriği TARİHİN kendisidir. Türkçede tarih çoğu kez
    fiilden ÖNCE gelir ("10.01.2026 tarihinde tebliğ edilen") — bu yüzden
    `geri` penceresi vardır. Taraf penceresi bilinçli olarak geniştir (UYAP
    başlık bloğunda etiket ile adres arasında TCKN/VKN, unvan satırı bulunur)."""
    __slots__ = ("capa", "hedef", "pencere", "geri")

    def __init__(self, capa, hedef, pencere=400, geri=0):
        self.capa = list(capa)
        self.hedef = list(hedef)
        self.pencere = pencere
        self.geri = geri


class Kosullu:
    """KOŞULLU unsur: `kosul` desenlerinden biri metinde geçerse (ve `istisna`
    desenlerinden hiçbiri geçmezse) `desen` (düz liste / Bilesik / Yakin)
    zorunlu olur. `kosul=None` → koşul her zaman doğmuş sayılır (yalnız
    istisna işler — ör. İİK m.16/2 süresiz şikâyet hâlinde süre unsuru
    aranmaz)."""
    __slots__ = ("kosul", "desen", "istisna")

    def __init__(self, kosul, desen, istisna=None):
        self.kosul = list(kosul) if kosul else None
        self.desen = desen
        self.istisna = list(istisna) if istisna else []


# Ortak desen yapı taşları — yeni tiplerde tekrar tekrar kullanılır. OCR'dan
# geçmiş ya da Türkçe karaktersiz yazılmış metne dayanıklılık için kritik
# sözcüklerde [cç]/[sş]/[gğ]/[oö]/[uü] sınıfları kullanılır (ailenin B6
# konvansiyonu); ı/i/İ/I eşdeğerliğini Python'un re.I'si zaten sağlar.
# Tarih: gg.aa.yyyy, gg/aa/yyyy, gg-aa-yyyy ve "10 Ocak 2026". Gruplanmıştır
# çünkü başka desenlere eklenerek kullanılır (alternation önceliği bozulmasın).
_TARIH = (r"(?:\d{1,2}[./-]\d{1,2}[./-]\d{4}|\d{1,2}\s+(?:ocak|[sş]ubat|mart|nisan|"
          r"may[ıi]s|haziran|temmuz|a[gğ]ustos|eyl[üu]l|ekim|kas[ıi]m|aral[ıi]k)\s+\d{4})")
_IMZA_D = [r"imza", r"\bvekil", r"\bav\.\s", r"avukat"]
_TARIH_IMZA = Bilesik((("tarih", [_TARIH]), ("imza/vekil", _IMZA_D)))
_ICRA_DAIRESI_D = [r"icra\s*daire", r"icra\s*m[üu]d[üu]rl[üu][gğ]"]
_ICRA_MAHKEMESI_D = [r"icra\s*(?:hukuk\s*)?mahkeme", r"icra\s*h[âa]kimli"]
_DOSYA_NO_D = [r"dosya\s*(?:no|numara|say[ıi])", r"esas\s*(?:no|numara|say[ıi])",
               r"\b\d{4}\s*/\s*\d+\s*(?:E\b|Esas\b|Tal\b|Talimat\b)",
               r"takip\s*(?:dosya|no\b|numara)"]
_DOSYA_TAKIP = Bilesik((("icra dairesi", _ICRA_DAIRESI_D), ("esas/dosya no", _DOSYA_NO_D)))
_ALACAKLI_D = [r"alacakl[ıi]"]
_BORCLU_D = [r"bor[cç]lu"]
_ADRES_D = [r"adres", r"yerle[sş]im\s*yeri", r"ikametg[âa]h"]
_KIMLIK_D = [r"\bT\.?\s*C\.?\s*(?:kimlik\s*)?(?:no\b|numaras)", r"\bTCKN\b",
             r"kimlik\s*(?:no\b|numaras)", r"\bVKN\b",
             r"vergi\s*(?:kimlik\s*)?(?:no\b|numaras)", r"mersis",
             r"\bT\.?\s*C\.?\s*:\s*\d"]
_IBAN_D = [r"\bIBAN\b", r"\bTR\s?\d{2}[\s\d]{10,}", r"banka\s*(?:ad[ıi]|hesab)",
           r"hesap\s*(?:no\b|numaras|bilgi)"]
# Para tutarı — sınırlı tekrar (uzun rakam/nokta dizisinde felaket geri izleme
# yok); "10.000,00 TL", "10.000,00-TL", "10.000.-TL", "10.000 Türk Lirası".
_TL_TUTAR = r"\d[\d.]{0,24}(?:,\d{1,4})?[ \t]{0,3}-?[ \t]{0,2}(?:TL\b|₺|T[üu]rk\s*liras)"
# 'tebligat' (ör. "tebligat gideri") tebliğ OLAYI değildir — dışlanır.
_TEBLIG_D = [r"tebli[gğ](?!at)", r"tebell[üu][gğ]"]
# Usulsüz tebliğde muhatabın tebliğe muttali olduğunu beyan ettiği tarih
# tebliğ tarihi sayılır (Tebligat K. m.32); icra şikâyetinde süre öğrenmeden
# işler (İİK m.16/1) — Yargı PRO MCP, 2026-10-05.
_OGRENME_D = [r"[öo][gğ]ren", r"[ıi]tt[ıi]la", r"muttali"]
# Tebliğ HENÜZ YAPILMAMIŞSA tarih yazılamaz; tebliğden önce başvurmak
# müvekkilin hakkıdır (ör. gerekçeli karar tebliğ edilmeden istinaf). Açık
# "tebliğ edilmemiştir / edilmeden" beyanı tarih unsurunu kaldırır. YALNIZ
# olumsuz çekimler: 'tebliğ edilmesi' (ad-fiil) olumludur, istisna DEĞİLDİR.
_TEBLIG_YOK_D = [r"tebli[gğ]\s*(?:edil|yap[ıi]l|olun)m(?:e(?:mi[sş]|di|den)|a(?:m[ıi][sş]|d[ıi]|dan))"]
# Süre başlangıcının belgesi: tebliğ TARİHİ, tebliğ olayının YANINDA (Yakin;
# Türkçede tarih çoğu kez fiilden önce gelir → `geri`). Süre İFADESİ ("yedi
# gün içinde") dilekçenin yasal içeriği değildir — süreyi [S] satırı oa-sure'ye
# bağlar (Fable 5.1 salt okunur incelemesi benimsendi, 2026-10-05).
_TEBLIG_TARIHI = Kosullu(None, Yakin(_TEBLIG_D, [_TARIH], pencere=80, geri=100),
                         istisna=_TEBLIG_YOK_D)
_TEBLIG_OGRENME_TARIHI = Kosullu(None, Yakin(_TEBLIG_D + _OGRENME_D, [_TARIH], pencere=80,
                                             geri=100),
                                 istisna=_TEBLIG_YOK_D)
_DEGER_D = [r"dava\s*de[gğ]eri", r"harca\s*esas\s*de[gğ]er", r"m[üu]ddeabih",
            r"^[ \t]*(?:\*\*[ \t]*)?de[gğ]er[iİı]?[ \t]*(?:\*\*[ \t]*)?:", r"de[gğ]eri\s*:",
            r"uyu[sş]mazl[ıi]k\s*konusu\s*miktar"]
_INKAR_D = [r"ink[âa]r\s*tazminat"]
_KOTU_NIYET_D = [r"k[öo]t[üu]\s*niyet\w*\s*tazminat", r"k[öo]t[üu]niyet\w*\s*tazminat"]
# Kambiyo senedi adları Türkçe çekimiyle: 'bonoya/bononun/bonolar', 'çeke/çekin/
# çekler'. Sözcük sınırı korunur — 'çekişme', 'çekilmiş', 'çekince' çek DEĞİLDİR.
_BONO = r"\bbono\w*"
_CEK = r"\b[çc]ek(?:ler\w*|in|e|i|te|ten|le)?\b"
# 'senet' ünsüz yumuşamasıyla 'senedi/senedin/senede' olur; 'seneden/seneyi'
# (yıl) alınmaz.
_SENET = r"\bsenet|\bsened(?:i|e\b)"
# TTK m.5/A-1 dava şartı arabuluculuk sinyali. Bilinçli olarak DAR: tek bir
# 'A.Ş.' unvanı ya da 'fatura' kelimesi davayı ticari yapmaz (nispi ticari dava
# iki tarafın ticari işletmesini ister — TTK m.4/1 ilk cümle); kambiyo senedi
# ise TTK'da düzenlendiği için tarafların tacir olup olmadığına bakılmaksızın
# ticari davadır (TTK m.4/1-a; bono TTK m.776 — Yargı PRO MCP, 2026-10-05).
_TICARI_D = [r"ticari\s*(?:dava|i[sş]|alaca|ili[sş]ki|defter|i[sş]letme)", r"\btacir",
             r"cari\s*hesap", r"kambiyo", _BONO, _CEK, r"poli[çc]e"]
_TICARI_ISTISNA_D = [r"ticari\s*dava\s*(?:niteli[gğ]inde\s*)?(?:de[gğ]il|say[ıi]lmaz)",
                     r"t[üu]ketici", r"arabuluculu[gğ]a\s*tabi\s*de[gğ]il",
                     r"dava\s*[sş]art[ıi]\s*(?:arabuluculu[gğ]u\s*)?(?:kapsam[ıi]nda\s*)?de[gğ]il"]
_DELIL_BELGE_D = [r"delil", r"belge", r"makbuz", r"dekont", r"\bekte\b",
                  r"\bekler\w*", r"bilirki[sş]i"]
_EKLER_D = [r"^[ \t]*(?:#+[ \t]*)?(?:\*\*[ \t]*)?ekler?\b", r"\bek\s*[-:.)]\s*\d",
            r"\bekte\b", r"\bekli(?:dir)?\b", r"\bekler\w*"]
_HUKUKI_SEBEP_D = [r"hukuki\s*sebep", r"hukuki\s*neden", r"dayanak"]
_VAKIA_DELIL = Bilesik((("vakıalar", [r"a[çc][ıi]klama", r"vak[ıi]a", r"olay"]),
                        ("deliller", [r"delil"])))
_DAVACI_DAVALI = Bilesik((("davacı", [r"davac[ıi]"]), ("davalı", [r"daval[ıi]"])))
_ADRES_KIMLIK = Bilesik((("adres", _ADRES_D), ("TCKN/VKN", _KIMLIK_D)))
_TALEP_D = [r"talep\s*ed(?:erim|eriz|iyoruz|iyorum)", r"arz\s*(?:ve|ile)\s*talep",
            r"karar\s*verilmesini"]


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
    # v0.5.18 (Y-06 / Yargı PRO 2-6 fikri): HMK m.342/2 — kararın mahkemesi
    # ile SAYISI birlikte (c), kararın tebliğ tarihi AYRI (ç), imza (g).
    # Eskiden 'süre' ya da 'iki hafta' kelimesi tebliğ tarihi unsurunu tek
    # başına karşılıyordu; tebliğ tarihi yasal zorunlu içeriktir, süre ifadesi
    # değildir (yedi kural #3: savunulmayan usulî noktayı savunma).
    "istinaf": [
        ("Kararın mahkemesi + sayısı (HMK m.342/2-c)",
         Bilesik((("kararı veren mahkeme", [r"b[öo]lge\s*adliye", r"\bBAM\b", r"ilk\s*derece",
                                            r"mahkemesi"]),
                  ("sayı (esas/karar no)", [r"esas\s*no", r"karar\s*no", r"\bE\.\s*\d{4}",
                                            r"\bK\.\s*\d{4}",
                                            r"\d{4}\s*/\s*\d+\s*(?:E|K|Esas|Karar)\b"])))),
        ("Taraflar", [r"davac[ıi]", r"daval[ıi]", r"istinaf\s*eden"]),
        ("İstinaf sebepleri", [r"istinaf\s*sebep", r"istinaf\s*neden", r"kaldır", r"hukuka\s*aykırı"]),
        ("Talep (kaldırma/yeniden)", [r"netice-?i?\s*talep", r"kaldırıl", r"talep\s*(ederiz|ederim)"]),
        ("Kararın tebliğ tarihi (HMK m.342/2-ç)", _TEBLIG_TARIHI),
        ("Tarih + imza (HMK m.342/2-g)", _TARIH_IMZA),
    ],
    # v0.5.18 (Y-06): HMK m.364/2-d — ilamın temyiz edene tebliğ edildiği
    # tarih AYRI unsur; m.364/2-ğ imza.
    "temyiz": [
        ("Yargıtay ilgili dairesi", [r"yargıtay", r"\bdaire", r"hukuk\s*dairesi", r"ceza\s*dairesi"]),
        ("BAM kararı bilgisi", [r"bölge\s*adliye", r"\bBAM\b", r"esas\s*no", r"karar\s*no"]),
        ("Temyiz sebepleri", [r"temyiz\s*sebep", r"temyiz\s*neden", r"bozma", r"hukuka\s*aykırı"]),
        ("Talep", [r"netice-?i?\s*talep", r"boz", r"talep\s*(ederiz|ederim)"]),
        ("İlamın tebliğ tarihi (HMK m.364/2-d)", _TEBLIG_TARIHI),
        ("Tarih + imza (HMK m.364/2-ğ)", _TARIH_IMZA),
    ],
    # v0.5.18 (Y-06): 6216 m.47/3 "kimlik VE adres", "ihlal edildiği ileri
    # sürülen hak VE dayanılan Anayasa hükümleri" — iki parçalı unsurlar.
    # Eskiden tek başına 'hak' kelimesi Anayasa maddesi unsurunu karşılıyordu.
    # m.47/3 son cümle: deliller + işlem/karar aslı ya da örneği + harç belgesi
    # eklenmesi ŞART; m.47/4: avukatla temsilde vekâletname.
    "aym_bireysel": [
        ("Başvurucu kimlik + adres bilgileri (6216 m.47/3)",
         Bilesik((("başvurucu/kimlik", [r"başvurucu", r"\bT\.?C\.?\b", r"kimlik"]),
                  ("adres", _ADRES_D)))),
        ("İhlal edilen hak + dayanılan Anayasa hükümleri (6216 m.47/3)",
         Bilesik((("ihlal edilen hak", [r"ihlal"]),
                  ("Anayasa maddesi", [r"anayasa[’']?n[ıi]n?\s*\d+", r"\bAY\s*m\.?\s*\d+",
                                       r"anayasa\s*m\.?\s*\d+",
                                       r"anayasa\w*\s+\d+\s*\.?\s*(?:ve\s+\d+\s*\.?\s*)?madde"])))),
        ("Başvuru yollarının tüketilmesi", [r"yol.*tüket", r"tüketil", r"kesinleş"]),
        ("Süre (30 gün)", [r"süre", r"otuz\s*gün", r"\b30\s*gün", r"tebliğ", r"öğrenme"]),
        ("Talep", [r"talep", r"ihlalin\s*tespit", r"yeniden\s*yargılama"]),
        ("Ekler — işlem/karar örneği + harç belgesi ya da adli yardım (6216 m.47/3 son cümle)",
         Bilesik((("işlem/karar örneği", [r"karar\w*\s*(?:örne|suret|asl)",
                                         r"(?:örne[gğ]|suret)\w*", r"\bekler\w*", r"\bekte\b"]),
                  ("harç belgesi / adli yardım", [r"harç", r"adli\s*yardım"])))),
        ("Vekâletname — avukatla temsilde (6216 m.47/4)",
         Kosullu([r"\bvekil", r"\bav\.\s", r"avukat"], [r"vek[âa]letname"])),
    ],
    "genel": GENEL,
}

# ── v0.5.18 — İCRA AİLESİ TİPLERİ (İİK; fikir: Yargı PRO 3-1…3-9) ────────────
# İnsan-okur cetvel + resmî metin künyeleri: references/icra-dilekce-ailesi.md.
# Her unsur adı dayanak maddeyi taşır ki [A] EKSİK satırı avukata neyin NEDEN
# zorunlu olduğunu da söylesin. Desenler yalnız VAR/YOK sinyalidir — hangi
# yolun isabetli olduğu (ilamsız/kambiyo, kesin/geçici kaldırma, 67/68) avukat
# kararıdır; script hukuki karar VERMEZ.
_FAIZ_TUR_D = [r"(?:yasal|kanuni|kanun[îi]|avans|ticari|ticar[îi]|temerr[üu]t|reeskont|"
               r"akdi|akd[îi]|s[öo]zle[sş]me(?:sel)?|mevduat)\s*faiz",
               r"%\s*\d", r"y[üu]zde\s*\d", r"faiz\s*oran"]
_FAIZ_BAS_D = [r"tarihinden\s*itibaren", r"takip\s*tarihinden", r"temerr[üu]t\s*tarih",
               r"vade\s*tarihinden", r"i[sş]lemeye\s*ba[sş]la", r"itibaren\s*i[sş]le"]
_SENET_SEBEP_D = [_SENET, _BONO, _CEK, r"poli[çc]e", r"\bfatura",
                  r"s[öo]zle[sş]me", r"borcun\s*sebebi", r"\bilam", r"cari\s*hesap",
                  r"[öo]d[üu]n[çc]", r"kira\s*(?:s[öo]zle[sş]me|bedel|alaca)", r"hizmet\s*bedel",
                  r"sat[ıi][sş]\s*bedel"]
_TAKIP_YOLU_D = [r"takip\s*yolu", r"takibin\s*yolu", r"ilams[ıi]z", r"ilaml[ıi]", r"kambiyo",
                 r"rehnin\s*paraya", r"tahliye", r"genel\s*haciz", r"iflas\s*yolu",
                 r"haciz\s*yolu"]
_KAMBIYO_D = [r"kambiyo", _BONO, _CEK, r"poli[çc]e", r"emre\s*muharrer"]
_BELGE_KOSUL_D = [_SENET, _BONO, _CEK, r"poli[çc]e", r"\bfatura",
                  r"s[öo]zle[sş]me", r"\bilam"]
_ITIRAZ_BEYAN_D = [r"itiraz\s*ed(?:iyoruz|iyorum|eriz|erim|ilmi[sş]tir)",
                   r"itiraz(?:[ıi]m[ıi]z|[ıi]m)\s*(?:vard[ıi]r|bulunmaktad[ıi]r|mevcut)",
                   r"(?:borca|borcun\s*tamam[ıi]na|faize|ferilerine|as[ıi]l\s*alaca[gğ]a|"
                   r"yetkiye|imzaya)\s*(?:ve\s*\w+\s*)?itiraz"]
_KISMI_D = [r"k[ıi]smen\s*itiraz", r"k[ıi]smi\s*itiraz", r"k[ıi]sm[ıi]na\s*itiraz"]
_CIHET_D = [r"as[ıi]l\s*alaca", r"i[sş]lemi[sş]\s*faiz", r"\bfaiz", r"ferileri", r"masraf",
            r"kalem", r"cihet", r"vek[âa]let\s*[üu]cret"]
_KAMBIYO_TUR_D = [r"borca\s*itiraz", r"imzaya\s*itiraz",
                  r"imza\w*\s*(?:m[üu]vekkil\w*\s*)?(?:ait\s*olmad|ink[âa]r|reddi)",
                  r"kambiyo\s*senedi\s*(?:niteli|vasf)", r"vasf\w*\s*(?:y[öo]n[üu]nden|ili[sş]kin|"
                  r"dair)?\s*[sş]ik[âa]yet", r"vas[ıi]f\s*[sş]ik[âa]yet",
                  r"yetki(?:ye)?\s*itiraz", r"zamana[sş][ıi]m[ıi]\s*itiraz"]
_KAMBIYO_SEBEP_D = [r"itfa", r"[öo]dendi|[öo]denmi[sş]|[öo]deme\s*yap[ıi]l", r"mehil",
                    r"zamana[sş][ıi]m", r"bor[cç]lu\s*(?:olmad|de[gğ]il|bulunmad)",
                    r"bedelsiz", r"hat[ıi]r\s*senedi", r"yetkisiz", r"vasf",
                    r"imza\w*\s*(?:ait\s*olmad|sahte)", r"kar[sş][ıi]l[ıi]ks[ıi]z"]
# İİK m.169/a-1: borcun olmadığı, itfa ya da imhal RESMÎ veya imzası ikrar
# edilmiş belgeyle ispatlanır — belge YALNIZ bu sebeplerde zorunludur
# (zamanaşımı senedin metninden, yetki dosyadan anlaşılır; imza itirazı m.68/a
# usulüyle incelenir — m.170/3). 'Deliller' başlığı belge DEĞİLDİR.
_BELGE_GEREKEN_SEBEP_D = [r"itfa", r"imhal", r"mehil", r"[öo]dendi|[öo]denmi[sş]|[öo]deme\s*yap[ıi]l",
                          r"bor[cç]lu\s*(?:olmad|de[gğ]il|bulunmad)"]
_ODEME_BELGE_D = [r"belge", r"makbuz", r"dekont", r"ibraname", r"ibra\s*senedi", r"noter",
                  r"resm[îi]", r"imzas[ıi]\s*ikrar", r"\bekte\b", r"\bek\s*[-:.)]\s*\d",
                  r"havale", r"\bEFT\b", r"banka\s*kayd"]
_DURDURMA_D = [r"durdurul", r"\bdur(?:ma|mas[ıi])\b"]
_KALDIRMA_BELGE_D = [r"68\s*/\s*a", r"68-a", r"(?:m\.?|madde)\s*68\b", r"68\s*\.?\s*madde",
                     r"noter", r"resm[îi]\s*belge", r"imzas[ıi]\s*ikrar", r"bor[cç]\s*ikrar",
                     r"imza\s*(?:inceleme|tatbik)"]
_BORCLU_OLMAMA_D = [r"bor[cç]lu\s*(?:olmad|de[gğ]il|bulunmad|olunmad)",
                    r"borcu\w*\s*(?:yok|bulunmad|bulunmamakta)",
                    r"bor[cç]\w*\s*(?:sona\s*er|itfa|[öo]denmi[sş]|bulunmamakta)",
                    r"bedelsiz", r"sahte", r"zamana[sş][ıi]m"]
_MAL_D = [r"ta[sş][ıi]nmaz", r"ta[sş][ıi]n[ıi]r", r"\bara[çc]", r"plaka", r"banka",
          r"maa[sş]", r"[üu]cret", r"hak\s*ve\s*alacak", r"\b89\b", r"tapu", r"menkul",
          r"mal\w*\s*varl[ıi]", r"hesap", r"mahcuz", r"hacizli"]
_HACIZ_TARIHI_D = [r"haciz\s*(?:tarih|tutana)", r"ha(?:ciz|cz)\w*\s*.{0,40}" + _TARIH,
                   _TARIH + r".{0,40}ha(?:ciz|cz)"]
_SURESIZ_SIKAYET_D = [r"s[üu]resiz", r"her\s*zaman\s*[sş]ik[âa]yet", r"s[üu]r[üu]ncemede",
                      r"yerine\s*getirilmeme", r"16\s*/\s*2"]

_ICRA_TIPLERI = {
    # İİK m.58 (+ m.167 kambiyo, m.269 kira tahliyesi) — takip talebi.
    "takip-talebi": [
        ("Merci — icra dairesi (İİK m.58/1)", _ICRA_DAIRESI_D),
        # m.58/2-1 TCKN/VKN'yi "varsa", m.58/2-2 borçlununkini "alacaklı
        # tarafından biliniyorsa" ister — zorunlu parça DEĞİL; yokluğu istişari
        # uyarıdır (TIP_UYARILARI; Fable 5.1 incelemesi benimsendi, MCP teyitli).
        ("Alacaklı kimliği — ad/unvan + yerleşim yeri (İİK m.58/2-1)",
         Bilesik((("alacaklı", _ALACAKLI_D),
                  ("alacaklı adresi", Yakin(_ALACAKLI_D, _ADRES_D))))),
        ("Ödeme hesabı — banka + hesap/IBAN bilgisi (İİK m.58/2-1)", _IBAN_D),
        ("Borçlu kimliği — ad/unvan + adres (İİK m.58/2-2)",
         Bilesik((("borçlu", _BORCLU_D), ("borçlu adresi", Yakin(_BORCLU_D, _ADRES_D))))),
        ("Alacağın Türk parasıyla tutarı (İİK m.58/2-3)", [_TL_TUTAR]),
        ("Faiz — oran/tür + işlemeye başladığı gün (İİK m.58/2-3)",
         Kosullu([r"faiz"], Bilesik((("oran/tür", _FAIZ_TUR_D),
                                     ("işlemeye başladığı gün", _FAIZ_BAS_D))))),
        ("Senet ya da borcun sebebi (İİK m.58/2-4)", _SENET_SEBEP_D),
        ("Takip yolu (İİK m.58/2-5)", _TAKIP_YOLU_D),
        ("Belge eki — aslı ya da onaylı örnekleri (İİK m.58/3)",
         Kosullu(_BELGE_KOSUL_D, _EKLER_D)),
        # Vade parçası yok: vadesi gösterilmemiş bono görüldüğünde ödenecek
        # sayılır (TTK m.777/2) — vadenin denetimi icra dairesinindir (İİK
        # m.168/1); vadesiz senette 'vade' kelimesini aramak sahte BLOK üretirdi.
        ("Kambiyo — senet aslı + borçlu adedince onaylı örnek (İİK m.167/2)",
         Kosullu(_KAMBIYO_D, Bilesik((("senet aslı", [r"asl[ıi]"]),
                                      ("onaylı örnek", [r"[öo]rne[gğk]", r"suret"]))))),
        ("Kira tahliyesi — ihtar + tahliye istemi (İİK m.269/1)",
         Kosullu([r"tahliye"], [r"ihtar"])),
        ("Tarih + imza", _TARIH_IMZA),
    ],
    # İİK m.62 (+ m.269/2 kira) — ilamsız takipte ödeme emrine itiraz, icra dairesine.
    # m.62'nin fıkra sırası mülga fıkra notu yüzünden belirsizdir — fıkralar
    # KONUSUYLA anılır (Fable 5.1 incelemesi; metin MCP ile okundu).
    "odeme-emrine-itiraz": [
        ("Merci — takibi yapan icra dairesi (İİK m.62/1)", _ICRA_DAIRESI_D),
        ("Takip dosyası (esas no)", _DOSYA_NO_D),
        ("Borçlu + yurt içi adresi (İİK m.62, adres fıkrası — itirazla birlikte bildirilir)",
         Bilesik((("borçlu", _BORCLU_D), ("borçlu adresi", Yakin(_BORCLU_D, _ADRES_D))))),
        ("Ödeme emrinin tebliğ (ya da öğrenme) tarihi (süre başlangıcı — İİK m.62/1: 7 gün; "
         "bkz. [S])", _TEBLIG_OGRENME_TARIHI),
        ("Açık itiraz beyanı — borca/faize/ferilere (İİK m.62)", _ITIRAZ_BEYAN_D),
        ("Kısmi itirazda cihet + miktar (İİK m.62, kısmi itiraz fıkrası — yoksa itiraz "
         "edilmemiş sayılır)",
         Kosullu(_KISMI_D, Bilesik((("miktar (TL)", [_TL_TUTAR]), ("cihet (kalem)", _CIHET_D))))),
        ("Talep — takibin durdurulması (İİK m.66/1)", _DURDURMA_D),
        ("Tarih + imza", _TARIH_IMZA),
    ],
    # İİK m.168/1-3,4,5; m.169, 169/a, 170 — kambiyo takibinde itiraz/şikâyet, icra mahkemesine.
    # Geçici durdurma İSTEMİ [A] DEĞİLDİR: m.169/a-2 ve m.170/2 mahkemeye takdir
    # verir ("karar verebilir") ve istem RİSK taşır — takip durdurulup itiraz
    # reddedilirse borçlu tazminata (m.169/a-6; imzada ayrıca para cezası —
    # m.170/3) mahkûm edilir. Karar avukatındır; yokluğu istişari uyarıdır
    # (TIP_UYARILARI; Fable 5.1 incelemesi benimsendi, MCP teyitli).
    "kambiyo-itiraz": [
        ("Merci — icra mahkemesi (İİK m.168/1-3, 4, 5)", _ICRA_MAHKEMESI_D),
        ("Takip dosyası — icra dairesi + esas no", _DOSYA_TAKIP),
        ("Taraflar — borçlu (itiraz eden) + alacaklı",
         Bilesik((("borçlu", _BORCLU_D), ("alacaklı", _ALACAKLI_D)))),
        ("Ödeme emrinin tebliğ (ya da öğrenme) tarihi (süre başlangıcı — İİK m.168/1: 5 gün; "
         "bkz. [S])", _TEBLIG_OGRENME_TARIHI),
        ("İtirazın türü açıkça — borca / imzaya / vasıf şikâyeti / yetki (İİK m.168/1-3, 4, 5)",
         _KAMBIYO_TUR_D),
        ("İtiraz sebebi (İİK m.168/1-5; m.169/a)", _KAMBIYO_SEBEP_D),
        ("Dayanak belge — borçlu olmama / itfa / imhal iddiasında resmî ya da imzası ikrar "
         "edilmiş belge (İİK m.169/a-1)",
         Kosullu(_BELGE_GEREKEN_SEBEP_D, _ODEME_BELGE_D)),
        ("Talep — itirazın kabulü / takibin iptali",
         [r"itiraz(?:[ıi]m[ıi]z|[ıi]n)\w*\s*kabul", r"takibin\s*iptal"] + _TALEP_D),
        ("Tarih + imza", _TARIH_IMZA),
    ],
    # İİK m.65 — gecikmiş itiraz, icra mahkemesine.
    "gecikmis-itiraz": [
        ("Merci — icra mahkemesi (İİK m.65/3 — itirazı icra mahkemesi inceler)",
         _ICRA_MAHKEMESI_D),
        ("Takip dosyası — icra dairesi + esas no", _DOSYA_TAKIP),
        ("Mani (mazeret) + borçlunun kusursuzluğu (İİK m.65/1)",
         Bilesik((("mani/mazeret", [r"mazeret", r"\bmani\b", r"m[âa]ni\b", r"engel"]),
                  ("kusursuzluk", [r"kusur\w*\s*(?:olmaks|bulunmaks|yok|bulunmamakta)",
                                   r"kusursuz", r"elinde\s*olmayan", r"iradesi\s*d[ıi][sş][ıi]nda"])))),
        # m.65/2'nin üç günü maninin kalktığı GÜNDEN işler; o günün TARİHİ,
        # süresinde başvurulduğunun dilekçedeki tek belgesidir.
        ("Maninin kalktığı gün — tarihiyle (süre başlangıcı — İİK m.65/2: 3 gün; bkz. [S])",
         Yakin([r"kalk(?:t|m)", r"sona\s*er", r"son\s*bul", r"taburcu"], [_TARIH],
               pencere=80, geri=100)),
        ("Mazereti gösterir deliller (İİK m.65/2)", _DELIL_BELGE_D + [r"rapor"]),
        ("İtiraz + sebepleri (İİK m.65/2)", _ITIRAZ_BEYAN_D + [r"itiraz\s*sebep"]),
        ("Harç ve masraf (İİK m.65/2 — itirazla birlikte ödenir)",
         [r"har[çc]", r"masraf", r"gider\s*avans"]),
        ("Talep — takibin tatili/durdurulması", _DURDURMA_D + [r"\btatil"]),
        ("Tarih + imza", _TARIH_IMZA),
    ],
    # İİK m.68, m.68/a — itirazın kesin/geçici kaldırılması, icra mahkemesine (alacaklı).
    # İnkâr tazminatı istemi [A] DEĞİLDİR: "diğer tarafın talebi üzerine" (m.68
    # ve m.68/a son fıkraları) talebi stratejik kılar, dilekçenin yasal içeriği
    # yapmaz — yokluğu istişari uyarıdır, aynı nitelikteki kötü niyet
    # tazminatıyla tutarlı (Fable 5.1 incelemesi benimsendi, MCP teyitli).
    "itirazin-kaldirilmasi": [
        ("Merci — icra mahkemesi (İİK m.68, m.68/a)", _ICRA_MAHKEMESI_D),
        ("Takip dosyası — icra dairesi + esas no", _DOSYA_TAKIP),
        ("Taraflar — alacaklı + borçlu",
         Bilesik((("alacaklı", _ALACAKLI_D), ("borçlu", _BORCLU_D)))),
        ("İtirazın tebliğ tarihi (süre başlangıcı — İİK m.68/1, m.68/a-1: 6 ay; bkz. [S])",
         _TEBLIG_OGRENME_TARIHI),
        ("Dayanak belgenin niteliği — m.68/1 belgesi ya da m.68/a imza incelemesi",
         _KALDIRMA_BELGE_D),
        ("Talep — itirazın (kesin/geçici) kaldırılması",
         [r"itiraz\w*\s*(?:kesin(?:\s*olarak)?\s*|ge[çc]ici(?:\s*olarak)?\s*|muvakkaten\s*)?kald[ıi]r[ıi]l"]),
        ("Deliller / belge ekleri", _DELIL_BELGE_D),
        ("Tarih + imza", _TARIH_IMZA),
    ],
    # İİK m.67 — itirazın iptali davası (genel mahkeme; HMK m.119 unsurları).
    "itirazin-iptali": [
        ("Mahkeme — genel mahkeme (HMK m.119/1-a)", [r"mahkemesi", r"h[âa]kimli[gğ]i"]),
        ("Davacı + davalı (HMK m.119/1-b)", _DAVACI_DAVALI),
        ("Adres + davacının TCKN/VKN'si (HMK m.119/1-b, c)", _ADRES_KIMLIK),
        ("Dava değeri (HMK m.119/1-d)", _DEGER_D),
        ("Takip dosyası — icra dairesi + esas no", _DOSYA_TAKIP),
        ("İtirazın tebliğ tarihi (süre başlangıcı — İİK m.67/1: 1 yıl; bkz. [S])",
         _TEBLIG_OGRENME_TARIHI),
        ("Vakıalar + deliller (HMK m.119/1-e, f)", _VAKIA_DELIL),
        ("Hukuki sebepler (HMK m.119/1-g)", _HUKUKI_SEBEP_D),
        ("Talep — itirazın iptali + takibin devamı (HMK m.119/1-ğ)",
         Bilesik((("itirazın iptali", [r"itiraz\w*\s*iptal"]),
                  ("takibin devamı", [r"takibin\s*devam"])))),
        # Dava şartı yokluğu usulden ret demektir — kalem BLOK kalır, ama koşulu
        # dardır (bkz. _TICARI_D) ve 'ticari dava değil / tüketici' beyanı
        # koşulu kaldırır. İnkâr tazminatı istemi istişaridir (TIP_UYARILARI).
        ("Dava şartı arabuluculuk — ticari alacakta son tutanak (TTK m.5/A-1)",
         Kosullu(_TICARI_D, [r"arabulucu"], istisna=_TICARI_ISTISNA_D)),
        ("Tarih + imza (HMK m.119/1-h)", _TARIH_IMZA),
    ],
    # İİK m.72 — menfi tespit (istirdat dahil); borçlu DAVACI konumunda.
    "menfi-tespit": [
        ("Mahkeme (HMK m.119/1-a)", [r"mahkemesi", r"h[âa]kimli[gğ]i"]),
        ("Davacı + davalı (HMK m.119/1-b)", _DAVACI_DAVALI),
        ("Adres + davacının TCKN/VKN'si (HMK m.119/1-b, c)", _ADRES_KIMLIK),
        ("Dava değeri (HMK m.119/1-d)", _DEGER_D),
        ("İcra takibiyle bağlantı — takip dosyası ya da 'takipten önce' beyanı (İİK m.72/1)",
         [r"takip(?:ten)?\s*[öo]nce", r"icra\s*daire", r"\d{4}\s*/\s*\d+\s*(?:E\b|Esas\b)",
          r"dosya\s*(?:no\b|numara)", r"esas\s*(?:no\b|numara)"]),
        ("Borçlu olmama vakıası + deliller (İİK m.72/1)",
         Bilesik((("borçlu olmama", _BORCLU_OLMAMA_D), ("deliller", [r"delil"])))),
        ("Hukuki sebepler (HMK m.119/1-g)", _HUKUKI_SEBEP_D),
        ("Talep — borçlu olunmadığının tespiti (istirdatta iade)",
         [r"bor[cç]lu\s*ol(?:un)?mad\w*(?:\s+\w+)?\s+tespit", r"menfi\s*tespit", r"tespitine",
          r"istirda[td]", r"iadesine", r"geri\s*veril"]),
        # 'ödeme emri' ödeme OLAYI değildir — çapadan dışlanır (ödeme emrinin
        # tebliğ tarihi istirdat süresinin başlangıcı değildir).
        ("İstirdatta ödeme tarihi (süre başlangıcı — İİK m.72/7: ödemeden 1 yıl; bkz. [S])",
         Kosullu([r"istirda[td]", r"geri\s*veril", r"iadesine"],
                 Yakin([r"[öo]deme(?!\s*emr)", r"[öo]dendi", r"[öo]denmi[sş]", r"[öo]dedi",
                        r"[öo]demi[sş]", r"[öo]deyerek", r"tahsil\s*edil"],
                       [_TARIH], pencere=80, geri=100))),
        ("Dava şartı arabuluculuk — ticari uyuşmazlıkta (TTK m.5/A-1: menfi tespit/istirdat)",
         Kosullu(_TICARI_D, [r"arabulucu"], istisna=_TICARI_ISTISNA_D)),
        ("Tarih + imza (HMK m.119/1-h)", _TARIH_IMZA),
    ],
    # İİK m.78 — haciz talebi, icra dairesine.
    "haciz-talebi": [
        ("Merci — icra dairesi (İİK m.78/1)", _ICRA_DAIRESI_D),
        ("Takip dosyası (esas no)", _DOSYA_NO_D),
        ("Haczi istenen mal, hak ya da alacak (somut)", _MAL_D),
        ("Takibin kesinleştiği — ödeme emri süresi geçti / itiraz kaldırıldı (İİK m.78/1)",
         [r"kesinle[sş]"]),
        ("Talep — haciz konulması", [r"haciz\s*(?:konul|uygula|i[sş]lem)", r"hacz(?:ine|inin)",
                                     r"haczedil"]),
        ("Tarih + imza", _TARIH_IMZA),
    ],
    # İİK m.106, m.110 — satış talebi, icra dairesine.
    "satis-talebi": [
        ("Merci — icra dairesi", _ICRA_DAIRESI_D),
        ("Takip dosyası (esas no)", _DOSYA_NO_D),
        ("Haczedilen mal + haciz tarihi (İİK m.106/1 — hacizden 1 yıl)",
         Bilesik((("mal", _MAL_D), ("haciz tarihi", _HACIZ_TARIHI_D)))),
        ("Kıymet takdiri + satış giderlerinin peşin yatırılması (İİK m.106/3; yatırılmazsa "
         "talep vaki olmamış sayılır — m.106/5)",
         [r"gider\w*\s*(?:avans|pe[sş]in|yat[ıi]r)", r"masraf\w*\s*(?:pe[sş]in|yat[ıi]r)",
          r"pe[sş]in(?:en)?\s*(?:olarak\s*)?yat[ıi]r", r"avans\w*\s*yat[ıi]r"]),
        ("Motorlu araçta muhafaza + kıymet takdiri + satış birlikte (İİK m.106/4)",
         Kosullu([r"\bara[çc]", r"plaka", r"motorlu", r"otomobil", r"kamyon"],
                 Bilesik((("muhafaza", [r"muhafaza"]), ("kıymet takdiri", [r"k[ıi]ymet\s*takdir"]))))),
        ("Talep — satış", [r"sat[ıi][sş](?:[ıi]n[ıi]n|[ıi]na)?\s*(?:yap[ıi]l|istenmesi|talep)",
                           r"sat[ıi]lmas[ıi]", r"sat[ıi][sş]a\s*[çc][ıi]kar[ıi]l",
                           r"sat[ıi][sş]\s*talep"]),
        ("Tarih + imza", _TARIH_IMZA),
    ],
    # İİK m.89 — üçüncü kişinin haciz ihbarnamesine itirazı, icra dairesine.
    "haciz-ihbarnamesi-itiraz": [
        ("Merci — icra dairesi (İİK m.89/2)", _ICRA_DAIRESI_D),
        ("Takip dosyası (esas no)", _DOSYA_NO_D),
        ("İhbarname + tebliğ tarihi (süre başlangıcı — İİK m.89/2-3: 7 gün; bkz. [S])",
         Bilesik((("ihbarname (1/2/3)", [r"ihbarname", r"89\s*/\s*[123]"]),
                  ("tebliğ tarihi", _TEBLIG_OGRENME_TARIHI)))),
        ("İtiraz sebebi — borç yok / mal yedinde değil / ödendi … (İİK m.89/2)",
         [r"borcu(?:muz)?\s*(?:bulunma|yok)", r"bor[cç]\w*\s*(?:bulunmamakta|yoktur)",
          r"(?:yedimizde|yedinde|elimizde)\s*(?:bulunmamakta|bulunmuyor|yok|de[gğ]il)",
          r"[öo]denmi[sş]", r"alaca[gğ][ıi]\s*(?:bulunmamakta|yoktur)", r"rehin", r"telef",
          r"istihlak"]),
        ("Talep — itirazın kabulü/kayda alınması", [r"itiraz\w*\s*(?:kabul|kayda)"] + _TALEP_D),
        ("Tarih + imza", _TARIH_IMZA),
    ],
    # İİK m.128/a — kıymet takdirine şikâyet, icra mahkemesine.
    "kiymet-takdiri-sikayet": [
        ("Merci — raporu düzenleten icra dairesinin bulunduğu yer icra mahkemesi (İİK m.128/a-1)",
         _ICRA_MAHKEMESI_D),
        ("Takip dosyası — icra dairesi + esas no", _DOSYA_TAKIP),
        ("Kıymet takdiri raporu + tebliğ tarihi (süre başlangıcı — İİK m.128/a-1: 7 gün; "
         "bkz. [S])",
         Bilesik((("rapor", [r"k[ıi]ymet\s*takdir", r"bilirki[sş]i\s*rapor"]),
                  ("tebliğ tarihi", _TEBLIG_OGRENME_TARIHI)))),
        ("Somut değer itirazı — gerekçe/emsal",
         [r"d[üu][sş][üu]k", r"y[üu]ksek", r"emsal", r"ger[çc]ek\s*de[gğ]er", r"piyasa\s*de[gğ]er",
          r"rayi[çc]"]),
        ("Yeniden bilirkişi incelemesi + masraf/ücretin şikâyetten itibaren 7 gün içinde "
         "yatırılması (İİK m.128/a-1 — yatırılmazsa kesin ret)",
         Bilesik((("bilirkişi incelemesi", [r"bilirki[sş]i"]),
                  ("masraf/ücret", [r"masraf", r"[üu]cret", r"gider\s*avans"])))),
        ("Talep — kıymet takdirinin düzeltilmesi / yeniden takdir",
         [r"yeniden\s*(?:k[ıi]ymet\s*)?takdir", r"k[ıi]ymet\s*takdirinin\s*(?:iptal|d[üu]zeltil|"
          r"kald[ıi]r[ıi]l)"] + _TALEP_D),
        ("Tarih + imza", _TARIH_IMZA),
    ],
    # İİK m.134/2 — ihalenin feshi şikâyeti, icra mahkemesine.
    "ihalenin-feshi": [
        ("Merci — icra mahkemesi (İİK m.134/2 — şikâyet yolu)", _ICRA_MAHKEMESI_D),
        ("Takip dosyası + ihale tarihi",
         Bilesik((("dosya", _DOSYA_NO_D + _ICRA_DAIRESI_D),
                  ("ihale tarihi", [r"ihale\s*tarih", _TARIH + r".{0,40}ihale",
                                    r"ihale\w*\s*.{0,40}" + _TARIH])))),
        ("Talep edenin İİK m.134/2'de sayılan sıfatı (satış isteyen alacaklı, borçlu, sicilde "
         "kayıtlı ilgili, sınırlı ayni hak sahibi, pey süren)",
         [r"sat[ıi][sş]\s*isteyen", r"bor[cç]lu", r"alacakl[ıi]", r"tapu\s*sicil",
          r"sicilde\s*kay[ıi]tl[ıi]", r"ipotek", r"s[ıi]n[ıi]rl[ıi]\s*ayn[îi]\s*hak",
          r"pey\s*s[üu]r", r"ihaleye\s*(?:kat[ıi]l|i[sş]tirak)"]),
        ("Yurt içinde adres (İİK m.134/2 — feshin koşulu)", _ADRES_D),
        # Süre (ihaleden 7 gün; ıttıla hâlinde ıttıladan) [S] satırındadır;
        # ihale tarihi yukarıdaki künye unsurunda zaten aranır.
        ("Yolsuzluk sebepleri (ilan/tebliğ, kıymet, fesat, esaslı hata …)",
         [r"usuls[üu]z", r"yolsuzluk", r"tebli[gğ]\s*edilmed", r"\bilan", r"fesa[td]",
          r"esasl[ıi]\s*(?:vas[ıi]f|hata)", r"k[ıi]ymet\s*takdir", r"muhammen"]),
        ("Menfaat ihlali — feshi isteyen kendi menfaatinin zarar gördüğünü ispatla yükümlü (İİK m.134)",
         [r"menfaat", r"zarar(?:a\s*u[gğ]ra|[ıi]m[ıi]z|[ıi]\s*do[gğ])", r"daha\s*(?:y[üu]ksek|fazla)\s*bedel",
          r"muhtel"]),
        ("Talep — ihalenin feshi", [r"ihalenin\s*feshi"]),
        ("Tarih + imza", _TARIH_IMZA),
    ],
    # İİK m.16 — icra dairesi işlemine şikâyet, icra mahkemesine.
    "icra-sikayet": [
        ("Merci — icra mahkemesi (İİK m.16/1)", _ICRA_MAHKEMESI_D),
        ("Takip dosyası — icra dairesi + esas no", _DOSYA_TAKIP),
        ("Şikâyet olunan icra dairesi işlemi",
         [r"i[sş]lem", r"muamele", r"m[üu]d[üu]rl[üu]k\s*karar", r"memur\w*\s*(?:karar|i[sş]lem)",
          r"tutanak", r"talebimiz\w*\s*(?:red|ret)", r"\bkarar"]),
        # Süre öğrenmeden işler (m.16/1) — tebliğ edilmemiş işlemde de öğrenme
        # tarihi gerekir; bu yüzden 'tebliğ edilmemiştir' istisnası burada YOK.
        ("Öğrenme/tebliğ tarihi (süre başlangıcı — İİK m.16/1: 7 gün; süresiz hâllerde "
         "aranmaz: m.16/2; bkz. [S])",
         Kosullu(None, Yakin(_TEBLIG_D + _OGRENME_D, [_TARIH], pencere=80, geri=100),
                 istisna=_SURESIZ_SIKAYET_D)),
        ("Şikâyet sebebi — kanuna aykırılık / olaya uygunsuzluk (İİK m.16/1)",
         [r"kanuna\s*ayk[ıi]r[ıi]", r"yasaya\s*ayk[ıi]r[ıi]", r"usuls[üu]z", r"olaya\s*uygun",
          r"hadiseye\s*uygun", r"hukuka\s*ayk[ıi]r[ıi]"]),
        ("Talep — işlemin iptali / düzeltilmesi", [r"iptal", r"d[üu]zeltil", r"kald[ıi]r[ıi]l"]),
        ("Tarih + imza", _TARIH_IMZA),
    ],
    # İİK m.96-97, 97/a — üçüncü kişinin istihkak davası, icra mahkemesinde.
    "istihkak-davasi": [
        ("Merci — icra mahkemesi (İİK m.97/6, 97/9)", _ICRA_MAHKEMESI_D),
        ("Davacı (üçüncü kişi) + davalı(lar)", _DAVACI_DAVALI),
        ("Adres + davacının TCKN/VKN'si (HMK m.119/1-b, c)", _ADRES_KIMLIK),
        ("Dava değeri — haczedilen malın değeri (HMK m.119/1-d)", _DEGER_D),
        ("Takip dosyası + haciz (tarih/tutanak)",
         Bilesik((("dosya", _DOSYA_NO_D), ("haciz", _HACIZ_TARIHI_D)))),
        ("Başlangıç olayının tarihi — tefhim/tebliğ ya da hacze ıttıla (süre başlangıcı — "
         "İİK m.97/6, m.97/9: 7 gün; bkz. [S])",
         Yakin([r"tefhim"] + _TEBLIG_D + _OGRENME_D, [_TARIH], pencere=80, geri=100)),
        ("Mülkiyet karinesine karşı — iktisap sebebi + malın borçlu yanında bulunma sebebi (İİK m.97/a)",
         Bilesik((("iktisap sebebi", [r"iktisap", r"sat[ıi]n\s*al", r"\bfatura", r"\bedin",
                                      r"m[üu]lkiyet", r"miras"]),
                  ("bulunma sebebi", [r"emanet", r"\bkira", r"ariyet", r"[öo]d[üu]n[çc]", r"yedinde",
                                      r"elinde", r"zilyet", r"bulunma\w*\s*sebeb", r"ayn[ıi]\s*adres",
                                      r"i[sş]yeri", r"depo"])))),
        ("Deliller", [r"delil"]),
        ("Talep — istihkakın kabulü + haczin kaldırılması",
         [r"istihkak\w*\s*(?:iddia\w*\s*)?kabul", r"haczin\s*kald[ıi]r[ıi]l",
          r"m[üu]lkiyet\w*\s*tespit"]),
        ("Tarih + imza", _TARIH_IMZA),
    ],
    # İİK m.76, 337/a, 338, 340, 344 + usul m.347-351 — icra ceza şikâyeti.
    "icra-ceza-sikayet": [
        ("Merci — icra (ceza) mahkemesi (İİK m.349)", [r"icra\s*ceza"] + _ICRA_MAHKEMESI_D),
        ("Şikâyetçi alacaklı + borçlu + adres",
         Bilesik((("şikâyetçi/alacaklı", [r"[sş]ik[âa]yet[çc]i", r"m[üu][sş]teki", r"alacakl[ıi]"]),
                  ("borçlu (sanık/şüpheli)", [r"bor[cç]lu", r"san[ıi]k", r"[sş][üu]pheli", r"maznun"]),
                  ("adres", _ADRES_D)))),
        ("Takip dosyası — icra dairesi + esas no", _DOSYA_TAKIP),
        ("Fiil + dayanak madde (İİK m.76/337-a/338/340/344)",
         Bilesik((("fiil", [r"taahh[üu][dt]\w*\s*(?:\S+\s+){0,3}ihlal", r"[öo]deme\s*[sş]art[ıi]n[ıi]\s*ihlal",
                            r"mal\s*beyan", r"nafaka", r"hakikate\s*ayk[ıi]r[ıi]",
                            r"ger[çc]e[gğ]e\s*ayk[ıi]r[ıi]", r"ticareti\s*terk", r"tazyik"]),
                  ("dayanak madde", [r"\b(?:İİK|IIK|İcra\s*ve\s*İflas\s*Kanunu)\w*\s*(?:m\.?|madde)?\s*"
                                     r"(?:76|337|338|340|344)\b",
                                     r"\b(?:76|337/a|338|340|344)\s*(?:\.|['’]?\s*(?:nc[ıi]|nci|[üu]nc[üu]))?\s*madde"])))),
        ("Öğrenme tarihi + fiil tarihi (İİK m.347 — öğrenmeden 3 ay, her hâlde fiilden 1 yıl; "
         "hak düşürücü)",
         Bilesik((("öğrenme tarihi", Yakin(_OGRENME_D, [_TARIH], pencere=80, geri=100)),
                  ("fiil/ihlal tarihi", [r"(?:ihlal|fiil|taksit|vade|[öo]deme)\w*\s*(?:tarih|.{0,40}" + _TARIH + ")",
                                         _TARIH + r".{0,60}(?:ihlal|[öo]denmed|[öo]demed|taksit)"])))),
        ("Deliller — şikâyetçi dilekçesinde gösterdiği delillerle bağlıdır (İİK m.351/1)", [r"delil"]),
        ("Talep — tazyik hapsi / cezalandırma",
         [r"tazyik\s*hapsi", r"cezaland[ıi]r[ıi]l", r"hapis"] + _TALEP_D),
        ("Tarih + imza", _TARIH_IMZA),
    ],
    # İİK m.33, 36, 71, 78, 96/2, 111 … — icra usul işlemleri (Yargı PRO 3-9 fikri).
    "icra-usul": [
        ("Merci — icra dairesi ya da icra mahkemesi", _ICRA_DAIRESI_D + _ICRA_MAHKEMESI_D),
        ("Takip dosyası (esas no)", _DOSYA_NO_D),
        ("Talep konusu + dayanak madde",
         Bilesik((("talep konusu", [r"\bkonu\b", r"talep\w*\s*konusu"]),
                  ("dayanak madde", [r"\b(?:İİK|IIK)\b", r"İcra\s*ve\s*İflas", r"\bmadde",
                                     r"\bm\.\s*\d"])))),
        ("Tehir-i icra — kanun yolu başvurusu + depo/teminat (İİK m.36/1)",
         Kosullu([r"tehir[\s-]*i?\s*icra", r"icran[ıi]n\s*geri\s*b[ıi]rak[ıi]lmas[ıi]\s*i[çc]in\s*s[üu]re"],
                 Bilesik((("kanun yolu başvurusu", [r"istinaf", r"temyiz"]),
                          ("depo/teminat", [r"teminat", r"depo", r"kefalet", r"mahcuz"]))))),
        # m.33/1: itfa/imhal iddiası resmî ya da usulüne göre onaylı/ikrar
        # olunmuş senetle tevsik edilir — belge YALNIZ itfa/imhalde aranır
        # (zamanaşımı itirazında belge koşulu yoktur; MCP teyitli).
        ("İcranın geri bırakılması — icra emrinin tebliğ tarihi + itfa/imhal/zamanaşımı + "
         "itfa/imhalde belge (İİK m.33/1: 7 gün; bkz. [S])",
         Kosullu([r"icra\s*emri"],
                 Bilesik((("tebliğ tarihi", _TEBLIG_OGRENME_TARIHI),
                          ("itfa/imhal/zamanaşımı", [r"itfa", r"imhal", r"zamana[sş][ıi]m"]),
                          ("belge (itfa/imhalde)",
                           Kosullu([r"itfa", r"imhal"], [r"belge", r"makbuz", r"noter",
                                                         r"resm[îi]", _SENET])))))),
        # m.96/2: icra dairesi bildirimle ÜÇ GÜNLÜK mühlet verir; susma istihkak
        # iddiasının kabulü sayılır (MCP teyitli).
        ("İstihkak iddiasına itiraz — icra dairesi bildiriminin tarihi (İİK m.96/2: 3 gün; "
         "susma kabul sayılır; bkz. [S])",
         Kosullu([r"istihkak\s*iddia\w*\s*(?:na|s[ıi]na)\s*itiraz"],
                 Kosullu(None, Yakin(_TEBLIG_D + _OGRENME_D + [r"bildiri"], [_TARIH],
                                     pencere=80, geri=100),
                         istisna=_TEBLIG_YOK_D))),
        ("Talep", _TALEP_D),
        ("Tarih + imza", _TARIH_IMZA),
    ],
}

# ── v0.5.18 — İDARİ DAVA, YD TALEBİ, CEZA İSTİNAFI (Y-06; fikir: Yargı PRO 4-4) ──
# İnsan-okur not + künyeler: references/idari-ceza-tipleri.md.
_YD_IKI_KOSUL = Bilesik((
    ("telafisi güç veya imkânsız zarar", [r"telafisi\s*(?:g[üu][çc]|imk[âa]ns[ıi]z)"]),
    ("açıkça hukuka aykırılık", [r"a[çc][ıi]k(?:[çc]a)?\s*hukuka\s*ayk[ıi]r[ıi]"]),
))
_IDARI_CEZA_TIPLERI = {
    # İYUK m.3 — idari dava dilekçesi.
    "idari-dava": [
        ("Merci — Danıştay / idare mahkemesi / vergi mahkemesi başkanlığına hitap (İYUK m.3/1)",
         [r"idare\s*mahkemesi", r"vergi\s*mahkemesi", r"dan[ıi][sş]tay"]),
        ("Taraflar + adres + gerçek kişi TCKN (İYUK m.3/2-a)",
         Bilesik((("davacı", [r"davac[ıi]"]),
                  ("davalı idare", [r"daval[ıi]", r"\bidare", r"bakanl[ıi][gğ]", r"belediye",
                                    r"ba[sş]kanl[ıi][gğ]", r"m[üu]d[üu]rl[üu][gğ]", r"valili[gğ]",
                                    r"kaymakaml[ıi][gğ]"]),
                  ("adres", _ADRES_D), ("TCKN", _KIMLIK_D)))),
        ("Davanın konusu + sebepleri (İYUK m.3/2-b)",
         Bilesik((("konu", [r"\bkonu\b", r"dava\s*konusu"]),
                  ("sebepler", [r"hukuka\s*ayk[ıi]r[ıi]", r"sebep", r"yetki", r"[sş]ekil", r"maksat",
                                r"neden"])))),
        ("Dayanılan deliller (İYUK m.3/2-b)", [r"delil"]),
        # Tarih bildirim olayının YANINDA aranır (Yakin). Zımni retde yazılı
        # bildirim yoktur; süre başvurudan otuz gün sonra işler (İYUK m.10/2 —
        # MCP teyitli) → başvuru tarihi de bu unsuru karşılar.
        ("Dava konusu işlemin yazılı bildirim tarihi (İYUK m.3/2-c; zımni retde başvuru "
         "tarihi — m.10/2)",
         Kosullu(None, Yakin(_TEBLIG_D + _OGRENME_D + [r"bildiri", r"ba[sş]vur"], [_TARIH],
                             pencere=80, geri=100),
                 istisna=_TEBLIG_YOK_D)),
        ("Uyuşmazlık konusu miktar — mali yükümlerde ve tam yargıda (İYUK m.3/2-d)",
         Kosullu([r"tam\s*yarg[ıi]", r"tazminat", r"vergi\s*mahkemesi", r"vergi\s*ziya[ıi]",
                  r"tarhiyat", r"ihbarname", r"mali\s*y[üu]k[üu]ml[üu]"],
                 [_TL_TUTAR, r"miktar"])),
        ("Vergi davasında nevi + yıl + ihbarname tarih/no (İYUK m.3/2-e)",
         Kosullu([r"vergi\s*mahkemesi", r"vergi\s*ziya[ıi]", r"tarhiyat", r"ihbarname"],
                 Bilesik((("vergi/ceza nevi", [r"verg", r"ceza"]),
                          ("yıl/dönem", [r"\b(?:19|20)\d{2}\b.{0,25}(?:y[ıi]l|d[öo]nem)",
                                         r"(?:y[ıi]l|d[öo]nem)\w*\s*:?\s*(?:19|20)\d{2}"]),
                          ("ihbarname tarih/no", [r"ihbarname\w*\s*.{0,60}(?:tarih|say[ıi]|no\b)"]))))),
        ("Ekler — dava konusu işlem/belge aslı ya da örneği (İYUK m.3/3)", _EKLER_D),
        ("Talep — iptal / yürütmenin durdurulması / tazminat",
         [r"iptal", r"y[üu]r[üu]tmenin\s*durdurul", r"tazminat"] + _TALEP_D),
        ("YD istendiyse iki koşul ayrı ayrı — zarar + açık hukuka aykırılık (İYUK m.27/2)",
         Kosullu([r"y[üu]r[üu]tmenin\s*durdurul"], _YD_IKI_KOSUL)),
        ("İmzalı dilekçe + tarih (İYUK m.3/1)", _TARIH_IMZA),
    ],
    # İYUK m.27 — yürütmenin durdurulması talebi (Yargı PRO 4-4 fikri).
    "yd-talebi": [
        ("Merci — Danıştay / idare / vergi mahkemesi ya da bölge idare mahkemesi",
         [r"idare\s*mahkemesi", r"vergi\s*mahkemesi", r"dan[ıi][sş]tay", r"b[öo]lge\s*idare"]),
        ("Dava dosyası ya da birlikte açılan dava", _DOSYA_NO_D + [r"dava\s*dilek[çc]e"]),
        ("Dava konusu idari işlem", [r"i[sş]lem", r"\bkarar"]),
        ("İki koşul ayrı ayrı — telafisi güç/imkânsız zarar + açıkça hukuka aykırılık (İYUK m.27/2)",
         _YD_IKI_KOSUL),
        ("YD kararına itirazda kararın tebliğ tarihi (süre başlangıcı — İYUK m.27/7: 7 gün, "
         "bir defaya mahsus; bkz. [S])",
         Kosullu([r"karar\w*\s*(?:kar[sş][ıi]\s*)?itiraz", r"YD\s*(?:karar\w*\s*)?itiraz",
                  r"27\s*/\s*7"],
                 _TEBLIG_TARIHI)),
        ("Talep — yürütmenin durdurulması", [r"y[üu]r[üu]tmenin\s*durdurul"]),
        ("Tarih + imza", _TARIH_IMZA),
    ],
    # CMK m.273 — ceza istinafı (CMK m.294 temyizde sebep zorunluluğu: `temyiz`).
    "ceza-istinaf": [
        ("Merci — hükmü veren ceza mahkemesi (CMK m.273/1) + bölge adliye mahkemesi",
         Bilesik((("hükmü veren ceza mahkemesi", [r"(?:a[gğ][ıi]r|asliye|sulh)\s*ceza",
                                                  r"[çc]ocuk\s*(?:a[gğ][ıi]r\s*)?ceza",
                                                  r"ceza\s*mahkeme"]),
                  ("bölge adliye mahkemesi", [r"b[öo]lge\s*adliye", r"\bBAM\b", r"ceza\s*daire",
                                              r"g[öo]nderilmek\s*[üu]zere"])))),
        ("Hükmün künyesi — esas/karar no + hüküm",
         Bilesik((("esas/karar no", [r"esas\s*(?:no\b|numara|say[ıi])", r"karar\s*(?:no\b|numara|say[ıi])",
                                     r"\d{4}\s*/\s*\d+\s*(?:E|K|Esas|Karar)\b"]),
                  ("hüküm", [r"h[üu]k[üu]m", r"h[üu]km[üu]", r"karar\s*tarih",
                             r"tarihli\s*(?:karar|h[üu]k[üu]m)"])))),
        ("Başvuranın sıfatı — sanık/müdafi, katılan/vekili, suçtan zarar gören (CMK m.273/4)",
         [r"san[ıi]k", r"m[üu]dafi", r"kat[ıi]lan", r"su[çc]tan\s*zarar\s*g[öo]ren", r"m[üu][sş]teki"]),
        # Gerekçeli hüküm henüz tebliğ edilmeden verilen (süre tutum) istinaf
        # dilekçesinde tarih yazılamaz — 'tebliğ edilmemiştir' beyanı tarih
        # parçasını kaldırır (bkz. _TEBLIG_YOK_D).
        ("Gerekçeli hükmün tebliğ tarihi (süre başlangıcı — CMK m.273/1: 2 hafta; bkz. [S])",
         Bilesik((("tebliğ tarihi", _TEBLIG_TARIHI),
                  ("gerekçeli hüküm", [r"gerek[çc]eli", r"h[üu]km[üu]n\s*gerek[çc]e"])))),
        ("İstinaf sebepleri (OA standardı — CMK m.273/4 yokluğu engel saymaz)",
         [r"istinaf\s*sebep", r"istinaf\s*neden", r"hukuka\s*ayk[ıi]r[ıi]",
          r"delil\w*\s*(?:de[gğ]erlendir|takdir)", r"eksik\s*(?:inceleme|ara[sş]t[ıi]rma)",
          r"usul\w*\s*ayk[ıi]r[ıi]"]),
        ("Talep — hükmün kaldırılması / beraat / yeniden hüküm",
         [r"kald[ıi]r[ıi]l", r"beraat", r"bozul", r"yeniden\s*(?:h[üu]k[üu]m|yarg[ıi]la)"] + _TALEP_D),
        ("Tarih + imza", _TARIH_IMZA),
    ],
}
TIPLER.update(_ICRA_TIPLERI)
TIPLER.update(_IDARI_CEZA_TIPLERI)

# Tertip-düzen: hem BİÇİM (başlık/numaralandırma) hem de "avukata yakışan" dilekçenin
# ZORUNLU UNSURLARININ VARLIĞI — tip ne olursa olsun (dava/cevap/istinaf/temyiz/aym_bireysel/
# genel) her dilekçede bulunması beklenen sekiz kalem: mahkeme başlığı, taraflar/vekil, konu,
# açıklamalar, hukuki sebepler, deliller, sonuç-istem, tarih-imza. Bu katman [A]'daki tip-özel
# listeden BAĞIMSIZ ve TÜM tiplere UYGULANIR — istinaf/temyiz/aym_bireysel gibi tip-özel
# listeler "Konu"/"Deliller"/"Hukuki sebepler" gibi jenerik kalemleri her zaman içermeyebilir;
# bu katman onu tamamlar. Script yalnız "unsur var/yok" der — "dilekçe iyi/kötü/kabule
# elverişli" hükmü VERMEZ (sahte kesinlik yok); eksik olanı UYAR, nihai göz avukatındır.
DUZEN = [
    # v0.5.18: icra dairesine hitap ('… İCRA DAİRESİNE' / '… İcra Müdürlüğüne')
    # da belirgin başlıktır — eskiden yalnız mahkeme/başkanlık arandığından her
    # icra talebi sahte [B] uyarısı alıyordu (istişari kapıda gürültü de zarardır).
    ("Belirgin başlık bloğu", [r"^#", r"mahkeme", r"başkanlığı", r"icra\s*daire",
                               r"m[üu]d[üu]rl[üu][gğ]"]),
    ("Numaralı/bölümlü açıklama düzeni", [r"^\s*\d+[.)]", r"^\s*[-*]\s", r"##"]),
    ("Mahkeme/merci başlığı", [r"mahkeme", r"başkanlığı", r"hakimliği", r"\bmerci", r"dairesi", r"kurulu",
                               r"m[üu]d[üu]rl[üu][gğ]"]),
    ("Taraflar / vekil bilgisi", [r"davac[ıi]", r"daval[ıi]", r"başvurucu", r"müşteki", r"sanık",
                                   r"katılan", r"müdahil", r"\bvekil", r"av\.\s",
                                   # v0.5.18 — icra/idari taraf etiketleri
                                   r"alacakl[ıi]", r"bor[cç]lu", r"[üu][çc][üu]nc[üu]\s*ki[sş]i",
                                   r"[sş]ik[âa]yet[çc]i"]),
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
KANUN_YOLU_TIPLERI = {"istinaf", "temyiz", "ceza-istinaf"}  # v0.5.18: + ceza-istinaf

# v0.5.18 — [B] TERTİP-DÜZEN muafiyetleri. NEDEN VAR: takip talebi, haciz ve
# satış talebi gibi icra dairesine verilen FORM NİTELİKLİ talepler (İİK m.58,
# m.78, m.106) delil/açıklama/hukuki sebep bölümü taşımaz; bu kalemlerin
# yokluğunu her seferinde [B] UYARI olarak basmak istişari kapıyı gürültüye
# boğar ve gerçek uyarıyı gömer (alarm yorgunluğu da zarardır). Muafiyet
# YALNIZ [B]'dir; [A] zorunlu unsurları bundan etkilenmez.
DUZEN_MUAF = {
    "takip-talebi": {"Deliller", "Açıklamalar / vakıalar", "Hukuki sebepler"},
    "haciz-talebi": {"Deliller", "Açıklamalar / vakıalar", "Hukuki sebepler"},
    "satis-talebi": {"Deliller", "Açıklamalar / vakıalar", "Hukuki sebepler"},
    "haciz-ihbarnamesi-itiraz": {"Deliller", "Hukuki sebepler"},
    "icra-usul": {"Deliller"},
}

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

# v0.5.18 — Türkçe çekim yardımcıları (Fable 5.1 salt okunur incelemesi
# benimsendi, 2026-10-05). '-me/-ma' Türkçede hem OLUMSUZLUK hem AD-FİİL
# ekidir: 'vazgeçmiyoruz / vazgeçmedik / vazgeçmeyeceğiz' olumsuzdur ama
# 'vazgeçmek istiyoruz / vazgeçmekteyiz / vazgeçmeyi' OLUMLUDUR. Kaba bir
# `(?!me)` olumlu '-mek/-mekte' biçimlerini de düşürür (sessiz yanlış-negatif);
# bu yüzden YALNIZ gerçek olumsuz devamlar dışlanır.
_VAZGEC = r"vazge[çc](?!(?:il)?me(?:d|z|yece|yiz|me|mi[sş]|ksizin)|(?:il)?miyor)"
_GERI_AL = r"geri\s*al(?!(?:[ıi]n)?ma(?:d|z|yaca|y[ıi]z|ma|m[ıi][sş]|ks[ıi]z)|(?:[ıi]n)?m[ıi]yor)"
_UGRA = r"u[gğ]ra(?!ma(?:d|z|yaca|y[ıi]z|ma|m[ıi][sş]|ks[ıi]z)|m[ıi]yor)"
# `(?#kesin)` ile başlayan kalıp ±70 NEG penceresinden MUAFTIR (bkz. denetle).
# Ön şartı: kalıp ÇEKİMLİ (bitmiş) OLUMLU yüklemle biter — olumsuzluk ve ortaç
# ('kabul ettiğimiz anlamına gelmez') kalıbın kendi gövdesinde dışarıda kalır.
# NEDEN: NEG listesindeki 'aksi', 'redd', 'değil' hukuk metninde çok sık geçer;
# "Borcun tamamını kabul ediyoruz; aksi düşünülemez" gibi gerçek bir ikrar
# komşu sözcük yüzünden BİLGİ'ye düşüp teslimden geçebiliyordu (anayasa m.6).
_KESIN = "(?#kesin)"
_OLUMLU_ET = (r"(?:ed(?:iyoruz|iyorum|iyor\b|eriz|erim|er\b|ece[gğ]iz|ece[gğ]im|"
              r"ilmi[sş]tir|ildi\b|ilmektedir)|et(?:tik|tim|ti|mi[sş]tir|mi[sş]tik|"
              r"mekteyiz|mekteyim|mektedir)\b)")
_KABUL_K = r"(?:kabul|ikrar)(?:\s*ve\s*(?:ikrar|kabul|beyan))?\s*" + _OLUMLU_ET
_VAZGEC_K = (r"vazge[çc](?:iyoruz|iyorum|iyor\b|eriz|erim|er\b|tik\b|tim\b|ti\b|mi[sş]tir|"
             r"mi[sş]tik|mekteyiz|mekteyim|mektedir|ece[gğ]iz|ece[gğ]im|ilmi[sş]tir|ildi\b)")
_GERI_AL_K = (r"geri\s*al(?:[ıi]yoruz|[ıi]yorum|[ıi]yor\b|[ıi]r[ıi]z|[ıi]r[ıi]m|d[ıi]k\b|"
              r"d[ıi]m\b|d[ıi]\b|m[ıi][sş]t[ıi]r|m[ıi][sş]t[ıi]k|makta(?:y[ıi]z|y[ıi]m|d[ıi]r)|"
              r"aca[gğ][ıi]z|aca[gğ][ıi]m|[ıi]nm[ıi][sş]t[ıi]r|[ıi]nd[ıi]\b)")
# itiraz + iyelik/çoğul ekleri — birinci ağız ('itirazımızdan') ve müvekkil
# anlatımı ('müvekkil itirazından vazgeçmiştir') birlikte.
_ITIRAZ_EK = r"itiraz(?:[ıi]m[ıi]z|[ıi]m|[ıi]n|lar[ıi]m[ıi]z|lar[ıi]n)?"

_ALEYHE_DAVALI = [
    r"davay[ıi]\s*kabul", r"kabul\s*ed(iyoruz|iyorum|eriz)", r"haklı\s*olduğunu\s*kabul",
    r"borcu(muzu)?\s*kabul", r"\bikrar\s*ed", r"talebi(ni)?\s*kabul", r"davanın\s*kabul",
    r"\bdoğrudur\b", r"iddia\s*doğrudur", r"kusurlu(yuz|yum)", r"sorumlu\s*olduğu(muzu|mu)",
]
_ALEYHE_DAVACI = [
    r"iddiam[ıi]zdan\s*" + _VAZGEC, r"haksız\s*olduğumuz", r"talebimizi\s*geri",
    r"talebimizden\s*" + _VAZGEC, r"davadan\s*feragat", r"iddiam[ıi]zdan\s*feragat",
    r"haklı\s*değiliz", r"davamız\s*yersiz",
]
_ALEYHE_MUSTEKI = [
    r"şikayet(im|imiz)i\s*geri", r"şikayetten\s*" + _VAZGEC, r"affediyor",
    r"barıştık", r"şikayetçi\s*değil", r"davacı\s*olmak\s*istemiyor",
]
# ── İŞ HUKUKU EKSENİ (2026-09-10 saha testi — iş mahkemeleri yönünden) ─────
# Genel medeni usul kalıpları (feragat/vazgeçme/kabul) iş davasında YETMEZ:
# müvekkili bitiren ikrar burada BAŞKA bir dille gelir. Ölçüm (aynı tarih):
# aşağıdaki yedi işçi-yanı ve beş işveren-yanı ifadenin HİÇBİRİ yakalanmıyordu
# (0/7 ve 0/5) — oysa her biri davayı tek başına bitirebilir.
#
# NEDEN OPSİYONEL BİR `--alan is` BAYRAĞINA BAĞLANMADI: aynı denetimin B2
# bulgusu, taramayı isteğe bağlı bir bayrağa bağlamanın onu SESSİZCE kör
# bıraktığını gösterdi. Bu yüzden kalıplar taraf setlerine doğrudan eklendi;
# yanlış-pozitifi avukat gözü eler ([UYARI] sınıfı, BLOK değil), yanlış-negatif
# müvekkili batırır.
#
# TARAF ASİMETRİSİ KASITLIDIR: "istifa etti" bir İŞVEREN vekili dilekçesinde
# müvekkil LEHİNEdir ve orada taranmaz; "haksız fesih" bir İŞÇİ vekili
# dilekçesinde LEHEdir ve orada taranmaz. Bu yüzden iki liste ayrı tutulur.
_ALEYHE_IS_ISCI_YANI = [
    # Fesih işçiye ait sayılırsa kıdem+ihbar düşer (4857 m.17, m.120 / 1475 m.14)
    r"istifa\s*et(?:ti|mi[sş]|erek|mek|mesi|mekle)", r"istifa\s*dilek[çc]e",
    r"kendi\s*(?:iste[gğ]|r[ıi]za|arzu)\w*\s*(?:ile\s*)?(?:i[sş]ten\s*)?ayr[ıi]l",
    # İbraname: TBK m.420 — alacakların ibrası
    r"ibraname\w*\s*(?:n[ıi]|y[ıi])?\s*imzala", r"ibra\s*et(?:ti|mi[sş])",
    # İkale: işe iade hakkını ve tazminatları ortadan kaldırır
    r"ikale\s*(?:s[öo]zle[sş]me|protokol)", r"ikale\s*ile\s*sona\s*er",
    r"ikale\s*(?:s[öo]zle[sş]mesi\s*)?imzalan",
    # Alacak kalmadı ikrarı — dava konusuz kalır
    r"alaca[gğ][ıi]\s*kalma(?:m[ıi][sş]|d[ıi])", r"alaca[gğ][ıi]m[ıi]z\s*kalma",
    r"t[üu]m\s*(?:yasal\s*)?alacaklar[ıi]\s*[öo]denmi[sş]",
    # İşverenin haklı fesih sebebini teyit eden ikrarlar (4857 m.25)
    r"devams[ıi]zl[ıi]k\s*yap", r"i[sş]e\s*gelme(?:di|mi[sş])",
    r"(?:fesih|fesh?in?)\s*hakl[ıi]\s*(?:sebe[bp]|neden|oldu[gğ])",
    r"hakl[ıi]\s*(?:sebe[bp]|neden)e?\s*dayan",
]
_ALEYHE_IS_ISVEREN_YANI = [
    r"haks[ıi]z\s*(?:olarak\s*)?(?:fesh|fesih|i[sş]ten)",
    r"(?:fesih|fesh?in?)\s*haks[ıi]z",
    r"ge[çc]erli\s*(?:bir\s*)?(?:sebep|neden)\s*(?:bulunma|yok|olmad[ıi][gğ])",
    r"k[ıi]dem\s*tazminat[ıi]na\s*hak\s*kazan", r"ihbar\s*tazminat[ıi]na\s*hak\s*kazan",
    r"fazla\s*mesai\w*(?:\s+\S+){0,4}\s*[öo]denme(?:di|mi[sş])",
    r"sigortas[ıi]z\s*[çc]al[ıi][sş]", r"sigorta\s*primleri(?:\s+\S+){0,3}\s*yat[ıi]r[ıi]lma",
    r"ihbar\s*[öo]ne?l\w*(?:\s+\S+){0,3}\s*uyulma",
    r"[üu]cretleri(?:\s+\S+){0,3}\s*[öo]denme(?:di|mi[sş])",
]

_ALEYHE_SANIK = [
    r"suçu\s*kabul", r"işlediğim(i)?\s*kabul", r"\bikrar\s*ed", r"pişman.*kabul",
    r"suçlu\s*olduğumu",
]

# ── v0.5.18 — İCRA EKSENİ (İİK) — taraf-asimetrik, BİRİNCİ AĞIZDAN ikrarlar ──
# NEDEN VAR: icra dilekçesinde müvekkili bitiren beyan genel medeni usul
# dilinden farklı gelir: borçlu vekilinin "itirazımızdan vazgeçiyoruz" demesi
# takibi kesinleştirir; alacaklı vekilinin istihkak iddiasını kabulü haczi
# düşürür (m.96/2'de susma bile kabul sayılır). Kalıplar bilinçli olarak
# BİRİNCİ AĞIZ ya da müvekkil anlatımı biçimindedir ('alacağımız',
# 'itirazımız', 'müvekkil itirazından') — karşı tarafın iddiasını aktaran cümle
# ('borçlunun borcun ödendiği iddiası') sinyal üretmesin diye. Olumsuz çekimi
# kalıbın kendisi dışarıda bırakır (_VAZGEC/_GERI_AL/_UGRA); '-miş' evidential
# olumludur ve yakalanır. Her eksen iki katmanlıdır: GENİŞ kalıp (NEG
# korumalı) + `(?#kesin)` kalıp (çekimli olumlu yüklem — NEG'den muaf).
# OCR'a dayanıklı sınıflar ([sş] [gğ] [cç] [oö] [uü]) ailenin B6 konvansiyonudur.
_ALEYHE_ICRA_BORCLU = [
    r"[öo]deme\s*emrine\s*itiraz\s*etmiyor",
    _ITIRAZ_EK + r"dan\s*" + _VAZGEC,
    _ITIRAZ_EK + r"[ıi]\s*" + _GERI_AL,
    r"takibin\s*kesinle[sş]ti[gğ]ini\s*kabul",
    r"bor[cç]lu\s*oldu[gğ]umuzu\s*(?:kabul|ikrar)",
    r"borcun\s*(?:tamam[ıi]n[ıi]|t[üu]m[üu]n[üu])\s*kabul",
    r"imza\s*(?:ink[âa]r[ıi]\s*)?" + _ITIRAZ_EK + r"(?:dan\s*" + _VAZGEC + r"|[ıi]\s*" + _GERI_AL + r")",
    r"taahh[üu]d[üu](?:m[üu]z[üu])?\s*ihlal\s*etti(?:k|[gğ]imizi)",
    # Davalı ekseninin 'kabul ed(iyoruz|iyorum|eriz)' kalıbının kaçırdığı
    # birinci ağız çekimleri ('-mekte', geçmiş zaman) — NEG korumalı.
    r"\bkabul\s*(?:et(?:tik|tim|mekteyiz|mekteyim)\b|ederim\b)",
    _KESIN + _ITIRAZ_EK + r"dan\s*" + _VAZGEC_K,
    _KESIN + _ITIRAZ_EK + r"[ıi]\s*" + _GERI_AL_K,
    _KESIN + r"takibin\s*kesinle[sş]ti[gğ]ini\s*" + _KABUL_K,
    _KESIN + r"bor[cç]lu\s*oldu[gğ]u(?:muzu|mu|nu)\s*" + _KABUL_K,
    _KESIN + r"borcun\s*(?:tamam[ıi]n[ıi]|t[üu]m[üu]n[üu])\s*" + _KABUL_K,
]
# Kambiyo takibine ÖZGÜ: borcun kısmen ya da tamamen kabulü (ve imza inkârı
# itirazının geri alınması) mahkemenin senedin kambiyo vasfını re'sen
# gözetmesini kapatır (İİK m.170/a-3 — Yargı PRO MCP, 2026-10-05). İlamsız
# takipte ise kısmi kabul + kısmi itiraz meşru ve sık bir stratejidir (m.62
# kısmi itiraz fıkrası) — bu yüzden kalıp YALNIZ kambiyo-itiraz tipinde taranır
# (Fable 5.1 incelemesi benimsendi).
_ALEYHE_ICRA_BORCLU_KAMBIYO = [
    r"borcun\s*(?:\S+\s+){0,3}?k[ıi]sm[ıi]n[ıi]\s*kabul", r"borcu\s*k[ıi]smen\s*kabul",
    _KESIN + r"borcun\s*(?:\S+\s+){0,3}?k[ıi]sm[ıi]n[ıi]\s*" + _KABUL_K,
    _KESIN + r"borcu\s*k[ıi]smen\s*" + _KABUL_K,
]
_ALEYHE_ICRA_ALACAKLI = [
    # Yalnız TAMAMLANMIŞ çekim: 'alacağımızın tahsil EDİLMESİ için' (takip
    # talebinin olağan amaç cümlesi) sinyal DEĞİLDİR; 'tahsil edilmiştir' ikrardır.
    _KESIN + r"alaca[gğ][ıi]m[ıi]z(?:[ıi]n)?\s*(?:tamamen\s*|tamam[ıi]\s*)?"
    r"(?:tahsil\s*edil(?:mi[sş]tir|di)|[öo]denmi[sş]tir|[öo]dendi)\b",
    r"borcun\s*(?:tamamen\s*)?[öo]dendi[gğ]ini\s*kabul",
    _KESIN + r"borcun\s*(?:tamamen\s*)?[öo]dendi[gğ]ini\s*" + _KABUL_K,
    r"tak(?:ipten|ibimizden|ibinden)\s*feragat", r"tak(?:ipten|ibimizden|ibinden)\s*" + _VAZGEC,
    _KESIN + r"tak(?:ipten|ibimizden|ibinden)\s*feragat\s*" + _OLUMLU_ET,
    _KESIN + r"tak(?:ipten|ibimizden|ibinden)\s*" + _VAZGEC_K,
    _KESIN + r"haczin\s*kald[ıi]r[ıi]lmas[ıi]na\s*muvafakat\s*" + _OLUMLU_ET,
    r"alaca[gğ][ıi]m[ıi]z(?:[ıi]n)?\s*zamana[sş][ıi]m[ıi]na\s*" + _UGRA,
    _KESIN + r"alaca[gğ][ıi]m[ıi]z\s*zamana[sş][ıi]m[ıi]na\s*u[gğ]ra(?:m[ıi][sş]t[ıi]r|d[ıi]\b|"
    r"makta(?:d[ıi]r)?\b)",
    r"itiraz(?:[ıi]n|[ıi])\s*hakl[ıi]\s*oldu[gğ]unu\s*kabul",
    _KESIN + r"itiraz(?:[ıi]n|[ıi])\s*hakl[ıi]\s*oldu[gğ]unu\s*" + _KABUL_K,
    r"istihkak\s*iddias[ıi]n[ıi]\s*kabul",
    _KESIN + r"istihkak\s*iddias[ıi]n[ıi]\s*" + _KABUL_K,
    r"[sş]ik[âa]yet(?:imiz)?den\s*" + _VAZGEC,
    _KESIN + r"[sş]ik[âa]yet(?:imiz)?den\s*" + _VAZGEC_K,
]
# Üçüncü kişinin borçluya borcunu / yedindeki malın borçluya aitliğini kabul
# eden cümleler. İstihkak davası gibi KENDİ hakkını ileri sürdüğü yerde
# müvekkili bitirir → BLOK. Haciz ihbarnamesine itirazda (m.89) ise üçüncü kişi
# gerçeği söylemek zorundadır — hakikate aykırı beyan hapis ve tazminat
# doğurur (İİK m.89/4, m.338/1 — MCP teyitli); orada aynı cümle dürüst beyandır
# ve BLOK DEĞİL istişari uyarıdır (TIP_UYARILARI; Fable 5.1 incelemesi).
_UCUNCU_BORC_IKRAR_D = [
    r"bor[cç]luya\s*(?:olan\s*)?borcumuz(?:un)?\s*(?:bulunmaktad[ıi]r|vard[ıi]r|mevcuttur)",
    r"m[üu]vekkil\w*\s*bor[cç]luya\s*(?:olan\s*)?borcu\s*(?:bulunmaktad[ıi]r|vard[ıi]r|mevcuttur)",
    r"bor[cç]luya\s*(?:olan\s*)?borcu(?:muzu)?\s*" + _KABUL_K,
    r"mal(?:lar)?[ıi]n\s*bor[cç]luya\s*ait\s*oldu[gğ]unu\s*" + _KABUL_K,
]
_ALEYHE_ICRA_UCUNCU_KISI = [
    r"bor[cç]luya\s*(?:olan\s*)?borcumuz(?:un)?\s*(?:bulunmaktad[ıi]r|vard[ıi]r|mevcuttur)",
    r"m[üu]vekkil\w*\s*bor[cç]luya\s*(?:olan\s*)?borcu\s*(?:bulunmaktad[ıi]r|vard[ıi]r|mevcuttur)",
    r"bor[cç]luya\s*(?:olan\s*)?borcu(?:muzu)?\s*kabul",
    r"mal(?:lar)?[ıi]n\s*bor[cç]luya\s*ait\s*oldu[gğ]unu\s*kabul",
    _KESIN + r"mal(?:lar)?[ıi]n\s*bor[cç]luya\s*ait\s*oldu[gğ]unu\s*" + _KABUL_K,
    r"istihkak\s*iddiam[ıi]zdan\s*" + _VAZGEC,
    _KESIN + r"istihkak\s*iddiam[ıi]zdan\s*" + _VAZGEC_K,
]
# Haciz ihbarnamesine itiraz eden üçüncü kişi: itirazından vazgeçmesi borcu
# zimmetinde / malı yedinde saydırır (İİK m.89/3 — MCP teyitli).
_ALEYHE_ICRA_UCUNCU_KISI_89 = [
    _ITIRAZ_EK + r"dan\s*" + _VAZGEC,
    _ITIRAZ_EK + r"[ıi]\s*" + _GERI_AL,
    _KESIN + _ITIRAZ_EK + r"dan\s*" + _VAZGEC_K,
    _KESIN + _ITIRAZ_EK + r"[ıi]\s*" + _GERI_AL_K,
]
# Borçlu setlerinde davalı ekseninin '\bikrar\s*ed' kalıbı edilgen 'imzası
# ikrar EDİLMİŞ belge' (İİK m.68/1, m.169/a-1 — kanunun kendi terimi) ibaresini
# ikrar sanıyordu: icra dilekçesinde sık geçen bu terim sahte BLOK üretirdi.
_ALEYHE_DAVALI_ICRA = [r"\bikrar\s*ed(?!il)" if p == r"\bikrar\s*ed" else p
                       for p in _ALEYHE_DAVALI]
# Menfi tespitte borçlu DAVACIdır: davalı ekseninin usul kalıpları ('davanın
# kabul') onun KENDİ talep cümlesidir — alınmaz; ama esasa ilişkin ikrar
# kalıpları (borcu kabul, ikrar) aynen tehlikelidir → alınır.
_ALEYHE_DAVALI_ESASA = [r"borcu(muzu)?\s*kabul", r"haklı\s*olduğunu\s*kabul",
                        r"\bikrar\s*ed(?!il)", r"iddia\s*doğrudur", r"kusurlu(yuz|yum)",
                        r"sorumlu\s*olduğu(muzu|mu)"]

ALEYHE = {
    # İş davalarının ezici çoğunluğunda işçi DAVACI, işveren DAVALIdır — HMK
    # m.103/1-ç'nin lafzı da ("işçilerin AÇTIKLARI davalar") bu kabuldedir.
    "davali": _ALEYHE_DAVALI + _ALEYHE_IS_ISVEREN_YANI,
    "davaci": _ALEYHE_DAVACI + _ALEYHE_IS_ISCI_YANI,
    "musteki": _ALEYHE_MUSTEKI,
    # katılan usulen müştekinin kamu davası açıldıktan sonraki devamıdır — aynı riskli eksen.
    "katilan": _ALEYHE_MUSTEKI,
    "sanik": _ALEYHE_SANIK,
    "genel": [r"karşı\s*taraf(ın)?\s*haklı", r"aleyhimize\s*kabul"],
    # v0.5.18 — icra sıfatları. Varsayılan konum: alacaklı talep eden (davacı
    # ekseni), borçlu karşı koyan (davalı ekseni), üçüncü kişi kendi hakkını
    # ileri süren (istihkak davasında davacı — davacı ekseni). İş hukuku
    # eksenleri aynı asimetriyle taşınır: alacaklı çoğunlukla işçi, borçlu
    # çoğunlukla işverendir.
    "alacakli": _ALEYHE_DAVACI + _ALEYHE_IS_ISCI_YANI + _ALEYHE_ICRA_ALACAKLI,
    "borclu": _ALEYHE_DAVALI_ICRA + _ALEYHE_IS_ISVEREN_YANI + _ALEYHE_ICRA_BORCLU,
    "ucuncu-kisi": _ALEYHE_DAVACI + _ALEYHE_ICRA_UCUNCU_KISI,
    # Konum çevrimi (bkz. TARAF_KONUM_CEVRIMI): menfi tespitte borçlu DAVACI,
    # alacaklı DAVALI'dır. Davalı kalıbı 'davanın kabul' borçlunun KENDİ talep
    # cümlesidir ('davanın kabulüne') — eksen çevrilmezse sahte BLOK üretirdi;
    # esasa ilişkin ikrar kalıpları ise korunur (_ALEYHE_DAVALI_ESASA).
    "borclu@davaci": (_ALEYHE_DAVACI + _ALEYHE_DAVALI_ESASA + _ALEYHE_IS_ISVEREN_YANI
                      + _ALEYHE_ICRA_BORCLU),
    "alacakli@davali": _ALEYHE_DAVALI_ICRA + _ALEYHE_IS_ISCI_YANI + _ALEYHE_ICRA_ALACAKLI,
    "borclu@kambiyo": (_ALEYHE_DAVALI_ICRA + _ALEYHE_IS_ISVEREN_YANI + _ALEYHE_ICRA_BORCLU
                       + _ALEYHE_ICRA_BORCLU_KAMBIYO),
    "ucuncu-kisi@89": _ALEYHE_DAVACI + _ALEYHE_ICRA_UCUNCU_KISI_89,
}

# v0.5.18 — tipe göre usul konumu çevrimi: (tip → {taraf: ALEYHE anahtarı}).
# Yalnız konumun ya da riskin VARSAYILANDAN farklı olduğu tipler yazılır.
TARAF_KONUM_CEVRIMI = {
    "menfi-tespit": {"borclu": "borclu@davaci", "alacakli": "alacakli@davali"},
    "kambiyo-itiraz": {"borclu": "borclu@kambiyo"},
    "haciz-ihbarnamesi-itiraz": {"ucuncu-kisi": "ucuncu-kisi@89"},
}

# CLI'nin kabul ettiği ama ALEYHE'de KENDİ anahtarı olmayan taraf sıfatlarının
# hangi eksen(ler)le taranacağı. Fer'î müdahil, yanında katıldığı tarafın
# yardımcısıdır (HMK m.66-69); asli müdahilse kendi hakkını ileri sürer. Script
# müdahilin HANGİ tarafta olduğunu BİLEMEZ → fail-closed: HER İKİ eksen de
# taranır (yanlış-pozitif avukat gözüyle elenir; yanlış-negatif müvekkili batırır).
TARAF_ESLEME = {
    "mudahil": ("davaci", "davali"),
}


def aleyhe_kapsami(taraf, tip=None):
    """(setler, kismi_mi, sebep) — bu taraf sıfatı için HANGİ kalıp setlerinin
    taranacağı ve taramanın TAM mı KISMİ mi olduğu.

    Ailenin SESSİZ ATLAMA YASAĞI'nın bu kapıdaki karşılığıdır: taraf sıfatı
    verilmemiş ya da sözlükte karşılığı yoksa yalnız iki desenli 'genel' seti
    taranır — bu bir tarama DEĞİL, tarama YOKLUĞUdur ve çıktıda "bulunamadı"
    diye görünemez ("bakmadım" ile "bakıp bulamadım" aynı şey değildir).

    v0.5.18: `tip` verilirse (ör. 'menfi-tespit') usul konumu tipe göre
    çevrilir (TARAF_KONUM_CEVRIMI); tek argümanlı eski çağrı aynen çalışır.
    """
    t = (taraf or "").strip().lower()
    if not t:
        return ["genel"], True, "taraf sıfatı VERİLMEDİ"
    if t in ALEYHE:
        anahtar = TARAF_KONUM_CEVRIMI.get((tip or "").strip().lower(), {}).get(t, t)
        return [anahtar, "genel"], False, ""
    if t in TARAF_ESLEME:
        return list(TARAF_ESLEME[t]) + ["genel"], False, ""
    return ["genel"], True, "taraf sıfatı %r kalıp sözlüğünde YOK" % t


def _bul(metin, desenler):
    return any(re.search(d, metin, re.I | re.M) for d in desenler)


def _yakin_var(metin, y):
    """`Yakin` parçası: çapanın geçtiği HER yerin ardındaki `pencere` (ve
    önündeki `geri`) karakter içinde hedef desenlerden biri var mı (en az bir
    çapa için yeterli). Pencere sınırlıdır — büyük girdide maliyet çapa
    sayısıyla doğrusal kalır."""
    for d in y.capa:
        for m in re.finditer(d, metin, re.I | re.M):
            pencere = metin[max(0, m.start() - y.geri): m.end() + y.pencere]
            if _bul(pencere, y.hedef):
                return True
    return False


def _parca_var(metin, des):
    """Bileşik unsurun tek parçası — düz liste, `Yakin` ya da `Kosullu`
    (koşulu doğmamış/istisnası geçen koşullu parça VAR sayılır)."""
    if isinstance(des, Kosullu):
        return not _unsur_degerlendir(metin, des)[0]
    if isinstance(des, Yakin):
        return _yakin_var(metin, des)
    return _bul(metin, des)


def _unsur_degerlendir(metin, des):
    """(eksik_mi, eksik_parcalar, parca_sayisi) — v0.5.18 unsur modeli.

    Düz liste → eski davranış (desenlerden biri yeter). `Kosullu` → koşul
    doğmamışsa ya da istisna geçiyorsa unsur ARANMAZ (eksik sayılmaz).
    `Bilesik` → her parça ayrı denetlenir; eksik parçaların etiketleri döner
    (hepsi eksikse unsur bütünüyle eksiktir). Desen tanımları modül içinde
    sabittir; her tipin derlenebilirliği testle kilitlidir."""
    if isinstance(des, Kosullu):
        if des.kosul is not None and not _bul(metin, des.kosul):
            return False, [], 0
        if des.istisna and _bul(metin, des.istisna):
            return False, [], 0
        return _unsur_degerlendir(metin, des.desen)
    if isinstance(des, Bilesik):
        eksikler = [etiket for etiket, d in des if not _parca_var(metin, d)]
        return bool(eksikler), eksikler, len(des)
    if isinstance(des, Yakin):
        return (not _yakin_var(metin, des)), [], 1
    return (not _bul(metin, des)), [], 1


def zorunlu_unsur_eksikleri(metin, tip):
    """[A] ZORUNLU UNSURLAR — tipin unsur listesini değerlendirir; eksik
    unsurların adlarını döndürür. Bileşik unsurda parça eksikse ad
    "unsur — eksik parça: a, b" biçimindedir (hepsi eksikse yalnız ad)."""
    eksik = []
    for ad, des in TIPLER.get(tip, TIPLER["genel"]):
        eksik_mi, parcalar, toplam = _unsur_degerlendir(metin, des)
        if not eksik_mi:
            continue
        if parcalar and len(parcalar) < toplam:
            eksik.append("%s — eksik parça: %s" % (ad, ", ".join(parcalar)))
        else:
            eksik.append(ad)
    return eksik


# ── v0.5.18 — TİPE ÖZEL İSTİŞARİ UYARILAR ([A] altında, ASLA bloklamaz) ──────
# NEDEN AYRI (zorunlu unsur değil): bu kalemlerin yokluğu ya bilinçli bir avukat
# tercihi olabilir (imzayı kabul etmek, tazminat istememek) ya da eski bir tipte
# kilit testleri bozmadan görünürlük gerekir (eski `dava` tipinde dava değeri —
# Y-06). Kural biçimi:
#   kosul : desenlerden biri YOKSA kural işlemez (None → her zaman işler)
#   yoksa : desenlerin HİÇBİRİ yoksa uyarı (None → yokluk aranmaz)
#   varsa : desenlerden biri VARSA uyarı; `bas` verilirse yalnız metnin ilk
#           `bas` karakterinde (başlık bloğu) aranır
# Mesajlar yalnız Yargı PRO MCP ile 2026-10-05'te okunan maddelere dayanır.
_MALVARLIGI_D = [_TL_TUTAR, r"alaca[gğk]", r"tazminat", r"tahsil", r"\bbedel"]
TIP_UYARILARI = {
    "dava": [
        {"kosul": _MALVARLIGI_D, "yoksa": _DEGER_D,
         "mesaj": "dava değeri satırı görünmüyor (HMK m.119/1-d — malvarlığı davasında zorunlu "
                  "içerik; harç ve kanun yolu parasal sınırı buna bağlanır). Y-06: eski 'dava' "
                  "tipinde istişaridir; itirazın iptali / menfi tespit / istihkak tiplerinde [A] "
                  "zorunlu unsurdur"},
        {"kosul": [r"davac[ıi]"], "yoksa": _ADRES_D,
         "mesaj": "tarafların adresi görünmüyor (HMK m.119/1-b) — eksiklikte hâkim bir haftalık "
                  "kesin süre verir, tamamlanmazsa dava açılmamış sayılır (HMK m.119/2)"},
        {"kosul": [r"davac[ıi]"], "yoksa": _KIMLIK_D,
         "mesaj": "davacının TCKN'si görünmüyor (HMK m.119/1-c) — eksiklikte bir haftalık kesin "
                  "süre, tamamlanmazsa dava açılmamış sayılır (HMK m.119/2)"},
    ],
    "takip-talebi": [
        {"kosul": None, "yoksa": [r"faiz"],
         "mesaj": "faiz istemi görünmüyor — faizli alacakta faizin miktarı/oranı ve işlemeye "
                  "başladığı gün gösterilir (İİK m.58/2-3); faizsiz takip çoğu zaman müvekkil "
                  "kaybıdır (karar avukatın)"},
        {"kosul": None, "yoksa": _KIMLIK_D,
         "mesaj": "TCKN/VKN görünmüyor — alacaklınınki 'varsa' (İİK m.58/2-1), borçlununki "
                  "'alacaklı tarafından biliniyorsa' (m.58/2-2) gösterilir: gerçek kişide "
                  "TCKN, tüzel kişide VKN yazın ya da bilinmediğini not edin"},
    ],
    "odeme-emrine-itiraz": [
        {"kosul": [_SENET, _BONO, r"s[öo]zle[sş]me", r"\bfatura", _CEK],
         "yoksa": [r"imza"],
         "mesaj": "takip senede/sözleşmeye dayanıyor ama imza beyanı yok — imza reddedilecekse "
                  "AYRICA VE AÇIKÇA yazılmalı, aksi hâlde icra takibi yönünden imza kabul "
                  "edilmiş sayılır (İİK m.62, imza fıkrası); imzanın kabulü bilinçli tercih "
                  "olabilir"},
        {"kosul": [r"\bkira", r"tahliye"],
         "yoksa": [r"kira\s*(?:akdi|s[öo]zle[sş]me|ili[sş]ki)\w*.{0,80}(?:red|ret|ink[âa]r|kabul\s*etm|"
                   r"bulunmad|yoktur|mevcut\s*de[gğ]il)"],
         "mesaj": "kira tahliye takibinde kira akdi ve sözleşmedeki imza AÇIK VE KESİN "
                  "reddedilmezse akit kabul edilmiş sayılır (İİK m.269/2); akdin kabulü bilinçli "
                  "tercih olabilir"},
    ],
    "kambiyo-itiraz": [
        {"kosul": None, "yoksa": _KOTU_NIYET_D,
         "mesaj": "kötü niyet tazminatı istemi görünmüyor — itirazın esasa ilişkin nedenlerle "
                  "kabulünde kötü niyetli/ağır kusurlu alacaklı aleyhine (İİK m.169/a-6; imza "
                  "itirazında m.170/4); koşulları varsa istemi kurun"},
        {"kosul": None, "yoksa": [r"durdurul", r"\btatil", r"tehir", r"tedbir"],
         "mesaj": "takibin geçici olarak durdurulması istemi görünmüyor — itiraz satış dışında "
                  "takibi kendiliğinden durdurmaz (İİK m.169, m.170/1); mahkeme durdurmaya "
                  "karar VEREBİLİR (m.169/a-2; imzada m.170/2). DİKKAT: takip durdurulur ve "
                  "itiraz reddedilirse borçlu yüzde yirmiden az olmamak üzere tazminata "
                  "(m.169/a-6), imza itirazında ayrıca yüzde on para cezasına (m.170/3) "
                  "mahkûm edilir — istem bilinçli bir risk kararıdır (avukat)"},
    ],
    "itirazin-kaldirilmasi": [
        {"kosul": None, "yoksa": _INKAR_D,
         "mesaj": "icra inkâr tazminatı istemi görünmüyor — itirazın kaldırılması esasa ilişkin "
                  "nedenlerle kabul edilirse borçlu, 'diğer tarafın talebi üzerine' yüzde "
                  "yirmiden aşağı olmamak üzere tazminata mahkûm edilir (İİK m.68 ve m.68/a son "
                  "fıkraları): talep yoksa hükmedilmez — istemi kurun ya da bilinçli tercih "
                  "olduğunu not edin"},
    ],
    "itirazin-iptali": [
        {"kosul": None, "varsa": [r"icra\s*(?:hukuk\s*)?mahkemesi"], "bas": 400,
         "mesaj": "başlık bloğunda icra mahkemesi görünüyor — itirazın iptali genel mahkemede, "
                  "genel hükümler dairesinde açılır (İİK m.67/1); icra mahkemesi yolu itirazın "
                  "kaldırılmasıdır (İİK m.68, m.68/a): merciyi denetleyin"},
        {"kosul": None, "yoksa": _INKAR_D,
         "mesaj": "icra inkâr tazminatı istemi görünmüyor — borçlunun itirazının haksızlığına "
                  "karar verilirse 'diğer tarafın talebi üzerine' hükmolunan meblağın yüzde "
                  "yirmisinden aşağı olmamak üzere tazminata hükmedilir (İİK m.67/2): talep "
                  "yoksa hükmedilmez — istemi kurun ya da bilinçli tercih olduğunu not edin"},
    ],
    "haciz-ihbarnamesi-itiraz": [
        {"kosul": _UCUNCU_BORC_IKRAR_D,
         "mesaj": "üçüncü kişinin borçluya borcu olduğunu / yedindeki malın borçluya ait "
                  "olduğunu kabul eden cümle var — itiraz yalnız gerçeğe uygun kapsamda "
                  "yapılabilir: alacaklı cevabın aksini ispatlarsa üçüncü kişi İİK m.338/1'e "
                  "göre cezalandırılır ve tazminata mahkûm edilebilir (m.89/4). Bu yüzden "
                  "cümle BLOK değildir; kabul edilen kısmın tutarını/kapsamını müvekkille "
                  "yazılı teyit edin"},
    ],
    "istinaf": [
        {"kosul": None,
         "yoksa": [r"karar\s*tarih", r"tarihli\s*(?:karar|h[üu]k[üu]m|ilam)",
                   _TARIH + r"\s*tarihli", r"\bT\.\s*" + _TARIH],
         "mesaj": "kararın TARİHİ görünmüyor — HMK m.342/2-c kararın hangi mahkemeden "
                  "verildiğini 'tarihi ile sayısı'yla birlikte ister; künyeye karar tarihini "
                  "ekleyin (eski tipte istişari)"},
    ],
    "menfi-tespit": [
        {"kosul": None, "yoksa": [r"tedbir"],
         "mesaj": "ihtiyati tedbir istemi görünmüyor — takipten önce açılan davada yüzde on "
                  "beşten az olmayan teminatla takibin durdurulması istenebilir (İİK m.72/2); "
                  "takipten sonra takip durdurulamaz, aynı teminatla paranın alacaklıya "
                  "ödenmemesi istenir (m.72/3)"},
        {"kosul": None, "yoksa": _KOTU_NIYET_D,
         "mesaj": "kötü niyet tazminatı istemi görünmüyor — takip haksız ve kötü niyetliyse "
                  "TALEP ÜZERİNE, yüzde yirmiden az olmamak üzere (İİK m.72/5)"},
    ],
    "istihkak-davasi": [
        {"kosul": None, "yoksa": [r"talik", r"tedbir", r"durdurul"],
         "mesaj": "takibin talikı (tedbir) istemi görünmüyor — davacının talebi üzerine "
                  "(İİK m.97/1, m.97/9); talik kararında teminat alınır (m.97/3)"},
    ],
    "ihalenin-feshi": [
        {"kosul": [r"pey\s*s[üu]r", r"ihaleye\s*(?:kat[ıi]l|i[sş]tirak)"], "yoksa": [r"teminat"],
         "mesaj": "pey süren gibi m.134/2 listesindeki alacaklı/borçlu/sicilde kayıtlı ilgili/"
                  "sınırlı ayni hak sahibi DIŞINDAKİ ilgili için ihale bedelinin yüzde beşi "
                  "teminat ve nispi harcın yarısı peşin (İİK m.134/3-4); eksikse iki haftalık "
                  "kesin süre, sonra ret"},
    ],
    "icra-usul": [
        {"kosul": [r"taahh[üu]t", r"taksit"],
         "mesaj": "taahhüt/taksit metni var — İİK m.111 uyarınca ya da alacaklının muvafakatiyle "
                  "kararlaştırılan ödeme şartını makbul sebep olmadan ihlal eden borçlu hakkında, "
                  "alacaklının şikâyeti üzerine üç aya kadar tazyik hapsi (İİK m.340); borçlu "
                  "vekiliyseniz müvekkili yazılı bilgilendirin"},
    ],
    "yd-talebi": [
        {"kosul": None, "yoksa": [r"teminat"],
         "mesaj": "teminat konusu görünmüyor — YD teminat karşılığı verilir; durumun "
                  "gereklerine göre teminat aranmayabilir, idareden ve adli yardımdan "
                  "yararlanandan alınmaz (İYUK m.27/6): teminatsız YD istemini açıkça kurun"},
        {"kosul": [r"ikinci\s*kez", r"yeniden\s*(?:y[üu]r[üu]tmenin|YD)",
                   r"daha\s*[öo]nce\w*\s*(?:y[üu]r[üu]tmenin|YD)", r"[öo]nceki\s*(?:YD|y[üu]r[üu]tmenin)"],
         "yoksa": [r"farkl[ıi]\s*(?:sebep|gerek[çc]e|neden)", r"yeni\s*(?:sebep|olgu|delil|neden)"],
         "mesaj": "önceki YD istemi anılıyor — aynı sebeplere dayanılarak ikinci kez YD "
                  "istenemez (İYUK m.27/10); yeni/farklı sebebi açıkça kurun"},
    ],
    "idari-dava": [
        {"kosul": [r"y[üu]r[üu]tmenin\s*durdurul"], "yoksa": [r"teminat"],
         "mesaj": "YD isteniyor ama teminat konusu görünmüyor — teminat aranmayabilir, idareden "
                  "ve adli yardımdan yararlanandan alınmaz (İYUK m.27/6): teminatsız YD istemini "
                  "açıkça kurun"},
    ],
}


def tip_ozel_uyarilari(metin, tip):
    """Tipe özel İSTİŞARİ uyarılar — liste döner, exit koduna ASLA dokunmaz.
    Asla istisna fırlatmaz; ama koşamadığında SESSİZ boş liste de dönmez
    (boş liste 'uyarı yok' demektir, 'bakılamadı' DEĞİL — ailenin sessiz
    atlama yasağı): tek görünür 'KOŞAMADI' satırı döner."""
    try:
        if metin is not None and not isinstance(metin, str):
            raise TypeError("metin str değil (%s)" % type(metin).__name__)
        metin = metin or ""
        uyarilar = []
        for kural in TIP_UYARILARI.get(tip, []):
            kosul = kural.get("kosul")
            if kosul is not None and not _bul(metin, kosul):
                continue
            yoksa = kural.get("yoksa")
            varsa = kural.get("varsa")
            if yoksa is not None and _bul(metin, yoksa):
                continue
            if varsa is not None:
                alan = metin[:kural["bas"]] if kural.get("bas") else metin
                if not _bul(alan, varsa):
                    continue
            uyarilar.append(kural["mesaj"])
        return uyarilar
    except Exception as e:
        return ["tipe özel istişari uyarılar KOŞAMADI (%s) — bu bir temizlik beyanı "
                "DEĞİLDİR; taslağı düz metin olarak verip yeniden koşun" % type(e).__name__]


# ── v0.5.18 — [S] SÜRE BAĞLANTISI (bilgi; süre HESABI oa-sure'ündür) ──────────
# NEDEN VAR: dilekçe kapısı süre hesaplamaz (tek yetkili: oa-sure); ama hangi
# dilekçenin HANGİ süre kuralına bağlandığı yazılmazsa süre satırı boş kalır ya
# da elle hesaplanır (Y-01: icra süresinin adli tatilde yanlış uzatılması tam
# bu sınıftandır). Kural kimliği koda GÖMÜLMEZ: oa-sure tablosu ÇALIŞMA ANINDA
# madde deseniyle aranır — kardeş ajan yeni kural eklediğinde bağ kendiliğinden
# kurulur; kural yoksa "TEYİT BEKLİYOR" görünür (sessiz boşluk yok).
# Biçim: tip → [(oa-sure 'kaynak' alanında aranacak madde deseni | None, açıklama)]
def _md(kanun, no):
    """oa-sure 'kaynak' metninde madde atfını yazım biçiminden bağımsız arar:
    'İİK m.62', 'İİK md. 62', 'İİK madde 62', 'İİK 62/1' hepsi tutar (kardeş
    ajanın yazım tercihi bağı sessizce koparmasın). `no` regex parçasıdır."""
    return kanun + r"\s*(?:m(?:d|adde)?\.?\s*)?(?:" + no + r")\b"


TIP_SURE = {
    "takip-talebi": [
        (_md("İİK", "62"), "İİK m.62/1 — borçlunun ödeme emrine itirazı: tebliğden 7 gün "
                           "(karşı taraf süresi; kesinleşme izlenir)"),
        (_md("İİK", "168"), "İİK m.168/1 — kambiyoda borçlunun itiraz/şikâyeti: tebliğden 5 gün"),
        (_md("İİK", "78"), "İİK m.78/2 — haciz isteme hakkı: ödeme emrinin tebliğinden 1 yıl"),
        (None, "alacağın zamanaşımı maddi süredir — oa-sure --tur maddi (kural alacağın türüne bağlı)"),
    ],
    "odeme-emrine-itiraz": [
        (_md("İİK", "62"), "İİK m.62/1 — ödeme emrinin tebliğinden 7 gün"),
        (_md("İİK", "269"), "İİK m.269/2 — kira tahliye takibinde 7 gün (eski BK m.260'taki "
                            "6 günlük mühlet hâlinde 3 gün — m.269 son fıkra)"),
    ],
    "kambiyo-itiraz": [
        (_md("İİK", "168"), "İİK m.168/1-3, 4, 5 — ödeme emrinin tebliğinden 5 gün"),
    ],
    "gecikmis-itiraz": [
        (_md("İİK", "65"), "İİK m.65/2 — maninin kalktığı günden 3 gün (m.65/1: paraya "
                           "çevirme bitinceye kadar)"),
    ],
    "itirazin-kaldirilmasi": [
        (_md("İİK", "68"), "İİK m.68/1, m.68/a-1 — itirazın tebliğinden 6 ay (geçerse aynı "
                           "alacak için yeniden ilamsız takip yapılamaz)"),
    ],
    "itirazin-iptali": [
        (_md("İİK", "67"), "İİK m.67/1 — itirazın tebliğinden 1 yıl"),
    ],
    "menfi-tespit": [
        (_md("İİK", "72"), "İİK m.72/7 — istirdat: ödemeden 1 yıl (menfi tespitin kendine "
                           "özgü dava süresi yok)"),
    ],
    "haciz-talebi": [
        (_md("İİK", "78"), "İİK m.78/2 — ödeme emrinin tebliğinden 1 yıl (itiraz/dava ve "
                           "taksit sözleşmesi süresi sayılmaz)"),
    ],
    "satis-talebi": [
        (_md("İİK", "106"), "İİK m.106/1 — hacizden itibaren 1 yıl; istenmezse haciz kalkar "
                            "(m.110/1)"),
    ],
    "haciz-ihbarnamesi-itiraz": [
        (_md("İİK", "89"), "İİK m.89/2-3 — ihbarnamenin tebliğinden 7 gün; 2. ihbarname 7 gün; "
                           "3. bildirimde 15 gün + dava belgesi 20 gün"),
    ],
    "kiymet-takdiri-sikayet": [
        (_md("İİK", "128"), "İİK m.128/a-1 — raporun tebliğinden 7 gün; masraf/ücret "
                            "şikâyetten itibaren 7 gün"),
    ],
    "ihalenin-feshi": [
        (_md("İİK", "134"), "İİK m.134/2 — ihale tarihinden 7 gün; ıttıla hâlinde ıttıladan, "
                            "her hâlde e-satış ilanından 1 yıl"),
    ],
    "icra-sikayet": [
        (_md("İİK", "16"), "İİK m.16/1 — öğrenmeden 7 gün (m.16/2 süresiz hâller)"),
    ],
    "istihkak-davasi": [
        (_md("İİK", "9[67]"), "İİK m.97/6 — kararın tefhim/tebliğinden 7 gün; m.97/9 — hacze "
                              "ıttıladan 7 gün; m.96/3 — iddia ıttıladan 7 gün"),
    ],
    "icra-ceza-sikayet": [
        (_md("İİK", "347"), "İİK m.347 — fiilin öğrenilmesinden 3 ay, her hâlde fiilden 1 yıl "
                            "(hak düşürücü)"),
    ],
    "icra-usul": [
        (_md("İİK", "33"), "İİK m.33/1 — icranın geri bırakılması: icra emrinin tebliğinden 7 gün"),
        (_md("İİK", "96"), "İİK m.96/2 — istihkak iddiasına itiraz: 3 gün (susma kabul sayılır)"),
        (_md("İİK", "363"), "İİK m.363 — icra mahkemesi kararına istinaf: tebliğden 2 hafta"),
    ],
    "idari-dava": [
        (_md("İYUK", "7"), "İYUK m.7 — dava açma süresi (idari 60 gün / vergi 30 gün; özel "
                           "usuller ayrı)"),
    ],
    "yd-talebi": [
        (_md("İYUK", "27"), "İYUK m.27/7 — YD kararına itiraz: tebliği izleyen günden 7 gün, "
                            "bir defaya mahsus"),
    ],
    "ceza-istinaf": [
        (_md("CMK", "273"), "CMK m.273/1 — gerekçeli hükmün tebliğinden 2 hafta"),
    ],
    "istinaf": [
        (_md("HMK", "345"), "HMK m.345 — ilamın tebliğinden 2 hafta"),
    ],
    "temyiz": [
        (_md("HMK", "361"), "HMK m.361 — tebliğden 2 hafta (hukuk)"),
        (_md("CMK", "291"), "CMK m.291/1 — gerekçeli hükmün tebliğinden 2 hafta (ceza)"),
    ],
    # HMK m.127 ve m.317/2 — Yargı PRO MCP, 2026-10-05 (yazılı yargılamada ek süre
    # en çok bir ay, basit yargılamada en çok iki hafta; ikisi de bir defaya mahsus).
    "cevap": [
        (_md("HMK", "127"), "HMK m.127 — yazılı yargılamada cevap: tebliğden 2 hafta (+ bir "
                            "defaya mahsus, en çok 1 ay ek süre)"),
        (_md("HMK", "317"), "HMK m.317/2 — basit yargılamada cevap: tebliğden 2 hafta (+ bir "
                            "defaya mahsus, en çok 2 hafta ek süre)"),
    ],
    "aym_bireysel": [
        (_md("6216", "47"), "6216 m.47/5 — yolların tüketilmesinden (yol yoksa öğrenmeden) 30 gün"),
    ],
}

_SURE_TABLO_ONBELLEK = {}


def _sure_kurallari_kaynaklari():
    """oa-sure kural tablosunu (…/oa-sure/scripts/sure_kurallari.json) YALNIZ
    OKUR ve {kural_kimliği: kaynak_metni} döndürür; okunamazsa None.
    Modül seviyesinde OKUNMAZ (hook sıcak yolu yüklenmesin — CLAUDE.md
    performans değişmezi); ilk çağrıda okunur, süreç içinde önbelleklenir."""
    if "v" in _SURE_TABLO_ONBELLEK:
        return _SURE_TABLO_ONBELLEK["v"]
    yol = (pathlib.Path(__file__).resolve().parent.parent.parent
           / "oa-sure" / "scripts" / "sure_kurallari.json")
    sonuc = None
    try:
        with open(yol, encoding="utf-8") as f:
            veri = json.load(f)
        sonuc = {}
        for blok in ("kurallar", "asama_kurallari"):
            b = veri.get(blok) if isinstance(veri, dict) else None
            if isinstance(b, dict):
                for kimlik, kural in b.items():
                    if isinstance(kural, dict):
                        sonuc[kimlik] = str(kural.get("kaynak") or "")
    except Exception:
        sonuc = None
    _SURE_TABLO_ONBELLEK["v"] = sonuc
    return sonuc


def sure_baglantisi(tip):
    """[S] satırları — tipin bağlı olduğu süre maddesi + oa-sure kural
    kimliği (çalışma anında aranır). Süre HESAPLAMAZ, ASLA bloklamaz."""
    kalemler = TIP_SURE.get(tip)
    if not kalemler:
        return []
    kaynaklar = _sure_kurallari_kaynaklari()
    satirlar = []
    for desen, aciklama in kalemler:
        if desen is None:
            satirlar.append(aciklama)
        elif kaynaklar is None:
            satirlar.append(f"{aciklama} → oa-sure kural tablosu OKUNAMADI (oa-sure kurulu mu?) — "
                            "süreyi elle hesaplama; avukat teyidi")
        else:
            bulunan = sorted(k for k, kaynak in kaynaklar.items()
                             if re.search(desen, kaynak, re.I))
            if bulunan:
                satirlar.append(f"{aciklama} → oa-sure kuralı: {', '.join(bulunan)}")
            else:
                satirlar.append(f"{aciklama} → TEYİT BEKLİYOR: oa-sure'de bu madde için kural "
                                "yok — süreyi elle hesaplama; kural eklenene dek avukat teyidi "
                                "ve en erken son gün")
    return satirlar


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
    Bu analiz İÇ CEPHANELİKTİR (_oa/cikti/06-antitez-cephanelik.md; ≤v0.5.15: 07-antitez-*) — dilekçede
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
                "bu analiz CEPHANELİĞE yazılır (06-antitez), dilekçeye DEĞİL; "
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
    # v0.5.18 — icra/idari dilekçelerin olağan kimlik/merci kısaltmaları
    # (takip talebinde IBAN/VKN zorunlu içeriktir — İİK m.58/2-1; her icra
    # talebinde [N] gürültüsü üretmesin). Örneklem, numerus clausus değil.
    "IBAN", "VKN", "TCKN", "BİM", "BIM", "YD",
}
# H2 (v0.5.16, Hamle 11): TARAF/ROL ETİKETLERİ — dilekçe başlık bloğunda
# 'SANIK : Ayşe Örnek', 'İDARE : …', 'KONU : …' biçiminde büyük harfle yazılan
# taraf/rol/alan etiketleri KISALTMA DEĞİL, sözcüğün kendisidir; [N] bunları
# "açılımsız kısaltma" diye uyarıyordu (saha: her ceza dilekçesinde 'SANIK'/
# 'TANIK' gürültüsü). Liste ÖRNEKLEMDİR (anayasa m.3) — aynı sınıftan
# (rol/alan etiketi) sözcük aynı muameleyi görür.
_N_TARAF_ROL_ETIKETLERI = {
    "SANIK", "ŞÜPHELİ", "HÜKÜMLÜ", "MAĞDUR", "MÜŞTEKİ", "KATILAN", "MÜDAHİL",
    "DAVACI", "DAVALI", "ALACAKLI", "BORÇLU", "VEKİLİ", "VEKİL", "MÜVEKKİL",
    "TANIK", "İDARE", "DAVA", "KARAR", "ESAS", "MADDE",
    # aynı sınıftan başlık-bloğu alan etiketleri (örneklem uzantısı)
    "KONU", "MÜDAFİ", "MÜDAFİİ", "TARİH",
    # para birimi simgesi — açılım beklenmez; her para talepli taslakta [N]
    # gürültüsü üretip gerçek kısaltmayı gömüyordu (v0.5.16 smoke bulgusu)
    "TL",
}
_N_BEYAZ_LISTE |= _N_TARAF_ROL_ETIKETLERI
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


# ── [F] HAFİF KİP (v0.5.16 — K3, Hamle 1) ──────────────────────────────────
# Tam [F] kapısı (`ictihat_muhakeme_denetim.py`) AYRI SÜREÇTE koşar ve
# teslimde (teslim_paketi (b2) / CLI) yetkili kalır. Hızlı kip (PostToolUse
# inline zincir, 2 sn sınırı) bu süreci açamaz — 777/372 karneleri: taslak
# yazılırken ALEYHE künye inline bulgu listesine HİÇ düşmüyordu, model bunu
# ancak teslim anında görüyordu. Hafif kip in-process, yalnız YEREL dosya
# (kütük) okur, MCP/ağ/alt-süreç YOK: künyeleri `kunye_ortak.
# esas_karar_atiflari` ile çıkarır, `<kok>/_oa/teyit/kunye-teyit.md`'de SON
# DAMGA'yı `kunye_ortak.kutukten_son_damga` ile okur (kütük satır biçimi TEK
# YERDE ayrıştırılır — burada regex TEKRARLANMAZ; son damga geçerlidir,
# oa_hafiza `--damga-degistir` ritüeliyle simetrik). Muhakeme kaydı
# (`_oa/cikti/*ictihat-muhakeme*`) alan denetimi, KAYNAK-URL/[G4], G6 tam-
# metin sınıfı vb. hafif kipin KONUSU DEĞİLDİR — o tam kapının işidir.
# Sessiz atlama yasağı: kunye_ortak yüklenemedi / kütük yok → GÖRÜNÜR bilgi
# satırı (yalnız taslakta künye VARKEN — künyesiz yarım taslak gürültü
# üretmez). `kok` yoksa hiç koşmaz ([T] ile aynı ilke).
_F_HAFIF_AZAMI = 8


def _f_hafif_kunye_metni(atif):
    """Bulgu satırında künyeyi kısa ve okunur göster (satır no ile)."""
    return f"{atif.get('metin') or ''} (satır {atif.get('satir_no')})".strip()


def ictihat_hafif_kip_bulgulari(metin, kok):
    """[F] HAFİF KİP — list[str] döner ("[F] " öneki ÇAĞIRAN tarafından
    eklenir). Sınıflar: ALEYHE → 'anayasa m.6 teslim engeli adayı';
    NOTR → 'dilekçeye giremez'; kütükte satır yok → 'çıplak künye adayı';
    satır var ama damgasız (ARAMA sınıfı) → 'muhakeme edilmemiş';
    LEHE / ALEYHE-AYIRT → satır YOK. Aynı esas/karar TEKİLLEŞTİRİLİR.
    Bu bir hüküm DEĞİLDİR — tam kapı ([F] ayrı süreç) teslimde yetkilidir;
    hafif kip yalnız GÖRÜNÜRLÜK üretir (sahte kesinlik yok)."""
    if not kok:
        return []
    # B-18 simetrisi: makine üretimi kaynakça bloğu gövde metni DEĞİLDİR.
    metin = makine_bloklarini_maskele(metin or "")
    ko = _kunye_ortak_modulu()
    if ko is None:
        return ["hafif kip: kunye_ortak yüklenemedi (oa-kontrol/scripts/ — "
                "kardeş skill kurulu mu?) — künyeler DENETLENMEDİ; tam kapı "
                "teslimde koşar"]
    try:
        atiflar = ko.esas_karar_atiflari(metin)
    except Exception as e:
        return [f"hafif kip: künye çıkarımı koşamadı ({type(e).__name__}) — "
                "tam kapı teslimde koşar"]
    atiflar = [a for a in atiflar if a.get("esas") or a.get("karar")]
    if not atiflar:
        return []
    kutuk = os.path.join(kok, "_oa", "teyit", "kunye-teyit.md")
    if not os.path.isfile(kutuk):
        return [f"hafif kip: künye teyit kütük dosyası bulunamadı ({os.path.relpath(kutuk, kok)}) — "
                f"taslaktaki {len(atiflar)} künyenin DAMGA'sı okunamadı (çıplak künye "
                "adayı); tam kapı teslimde koşar"]
    bulgular, gorulen = [], set()
    for a in atiflar:
        anahtar = (a.get("esas"), a.get("karar"), a.get("daire_key"))
        if anahtar in gorulen:
            continue
        gorulen.add(anahtar)
        kunye = _f_hafif_kunye_metni(a)
        daire = a.get("daire_key")
        damga = ko.kutukten_son_damga(kutuk, a.get("esas"), a.get("karar"), daire)
        if damga is None:
            satir_var = ko.kutukte_esas_karar_satiri_var_mi(
                kutuk, a.get("esas"), a.get("karar"), daire)
            if satir_var:
                bulgular.append(
                    f"damgasız künye (kütükte satır var, DAMGA yok — ARAMA sınıfı?): "
                    f"{kunye} — muhakeme edilmemiş, çıplak künye adayı; tam kapı "
                    "teslimde karar verir")
            else:
                bulgular.append(
                    f"kütükte izi yok: {kunye} — çıplak künye adayı (teyit --damga "
                    "ile kütüğe işlenmemiş); tam kapı teslimde karar verir")
        elif damga == "ALEYHE":
            bulgular.append(
                f"ALEYHE künye taslakta: {kunye} — anayasa m.6 teslim engeli adayı "
                "(salt-ALEYHE dış çıktıya GİREMEZ; cephanelikte işlenir)")
        elif damga == "NOTR":
            bulgular.append(
                f"NÖTR künye: {kunye} — dilekçeye giremez (muhakeme edilmemiş; "
                "damga LEHE/ALEYHE-AYIRT olmadan dış çıktıya girmez)")
        elif damga in ("LEHE", "ALEYHE-AYIRT"):
            continue
        else:
            bulgular.append(
                f"tanınmayan damga '{damga}': {kunye} — enum dışı (fail-closed: "
                "geçerli sayılmaz); tam kapı teslimde karar verir")
        if len(bulgular) >= _F_HAFIF_AZAMI:
            bulgular.append(f"(+ daha fazla künye var — hafif kip {_F_HAFIF_AZAMI} "
                            "kalemle sınırlı; tam kapı teslimde hepsini denetler)")
            break
    return bulgular


# ── [P] NETİCE-İ TALEP (v0.5.16 — P0-4 / A-22, advisory — ASLA bloklamaz) ──
# Talep bloğu, dilekçenin hükme dönüşen tek parçasıdır (taleple bağlılık —
# hâkim istenmeyeni veremez). Saha: para talebi var ama faiz türü/başlangıcı
# yok (faizsiz hüküm), 'kısmi dava/şimdilik' var ama 'fazlaya ilişkin haklar
# saklı' yok, yargılama gideri + vekâlet ücreti istenmemiş. Script HUKUKİ
# YORUM YAPMAZ — yalnız blok içinde MEKANİK var/yok söyler; hangi faiz
# türünün doğru olduğu (3095 s.K. m.1 kanuni / m.2 avans) avukat kararıdır
# (SKILL.md "NETİCE-İ TALEP PLAYBOOK'U"). Blok = başlık satırından METNİN
# SONUNA kadar (imza bloğu dahil — zararsız).
_P_BASLIK_RE = re.compile(
    r"^(?:NET[İIi]CE[-\s]*[İIi]?\s*TALEP|NET[İIi]CE\s+VE\s+TALEP|"
    r"SONU[ÇC]\s+VE\s+[İIi]STEM|SONU[ÇC]\s+VE\s+TALEP|TALEP)\s*:?\s*$", re.I)
_P_PARA_RE = re.compile(r"\bTL\b|₺|\d[\d.]*,\d{2}")
_P_FAIZ_TURU_RE = re.compile(
    r"(?:yasal|kanuni|kanunî|avans|ticari|ticarî|temerrüt|reeskont|akdi|akdî|sözleşme)\s*faiz", re.I)
_P_FAIZ_BASLANGIC_RE = re.compile(
    r"\d{1,2}[./]\d{1,2}[./]\d{4}|tarihinden|tarihinden\s+itibaren|"
    r"temerrüt\s+tarih|dava\s+tarih|ıslah\s+tarih|ihtar\s+tarih", re.I)
_P_FAZLAYA_RE = re.compile(r"fazlaya\s+(?:ilişkin|dair)", re.I)
_P_KISMI_RE = re.compile(r"kısmi\s+dava|kısmî\s+dava|belirsiz\s+alacak|\bşimdilik\b", re.I)
_P_BELIRSIZ_RE = re.compile(r"belirsiz\s+alacak", re.I)
_P_GIDER_RE = re.compile(r"yargılama\s+gider|vek[âa]let\s+ücret", re.I)


def _p_talep_blogu(metin):
    """Talep başlığı satırını (markdown/bold/numara işaretleri temizlenmiş)
    arar; SON eşleşmeden metnin sonuna kadar olan bloğu döner, yoksa None."""
    satirlar = (metin or "").splitlines()
    bas = None
    for i, satir in enumerate(satirlar):
        temiz = re.sub(r"^[\s#>*\-\d.)_]+", "", satir)
        temiz = re.sub(r"[*_]+", "", temiz).strip()
        if temiz and _P_BASLIK_RE.match(temiz):
            bas = i
    if bas is None:
        return None
    return "\n".join(satirlar[bas:])


def netice_talep_uyarilari(metin):
    """[P] NETİCE-İ TALEP advisory — uyarı listesi (boş = sinyal yok).
    Blok yoksa TEK satır 'bulunamadı' döner (CLI bunu basar; hızlı kip
    yarım taslakta bu satırı ATLAR — bkz. `hizli_denetim`)."""
    blok = _p_talep_blogu(metin)
    if blok is None:
        return ["netice-i talep bloğu bulunamadı (NETİCE-İ TALEP / SONUÇ VE İSTEM / "
                "NETİCE VE TALEP / TALEP başlığı yok) — talep bölümü başlıksız ya da "
                "eksik olabilir; hâkim istenmeyeni veremez (taleple bağlılık)"]
    uyarilar = []
    if _P_PARA_RE.search(blok):
        eksik = []
        if not _P_FAIZ_TURU_RE.search(blok):
            eksik.append("faiz türü (yasal/kanuni · avans · ticari · temerrüt · reeskont)")
        if not _P_FAIZ_BASLANGIC_RE.search(blok):
            eksik.append("faiz başlangıcı (temerrüt/dava tarihi ya da gg.aa.yyyy)")
        if eksik:
            uyarilar.append(
                "para talebi var ama " + " ve ".join(eksik) + " görünmüyor — faizsiz/"
                "başlangıçsız talep faizsiz hükme yol açar; 3095 s.K. m.1 (kanuni) / m.2 "
                "(temerrüt·avans) seçimi avukat kararıdır (playbook: NETİCE-İ TALEP)")
    tum = metin or ""
    if _P_KISMI_RE.search(tum) and not _P_FAZLAYA_RE.search(tum):
        ek = ""
        if _P_BELIRSIZ_RE.search(tum):
            ek = (" · NOT: HMK m.107 belirsiz alacak davası 7589/19 ile mülga (RG "
                  "31.07.2026); önce açılan davalarda uygulanmaya devam (7589 geçici "
                  "m.1/10) — Mevzuat MCP teyit 2026-09-06")
        uyarilar.append(
            "'kısmi dava / belirsiz alacak / şimdilik' geçiyor ama 'fazlaya ilişkin "
            "haklar saklı' kaydı yok — HMK m.109/3 feragat karinesini dışlar ama açık "
            "kayıt sahada standarttır; m.109/4 (7589/20) bir defalık talep artırımı "
            "playbook'ta" + ek)
    if not _P_GIDER_RE.search(blok):
        uyarilar.append(
            "talep bloğunda 'yargılama gideri' / 'vekâlet ücreti' istemi görünmüyor — "
            "yargılama giderine re'sen hükmedilir (HMK m.332/1; vekâlet ücreti "
            "gider kalemidir m.323/1-ğ, yükletilme m.326 — Mevzuat MCP teyit "
            "2026-09-07); açık istem sahada standarttır (playbook: NETİCE-İ TALEP 5)")
    return uyarilar


# ── HIZLI KİP (v0.5.9 — inline zincirin giriş noktası, İÇ API) ─────────────
# YALNIZ metin-tabanlı hızlı denetimler koşar: [Y] havada-kalan alıntı,
# [M] madde sürekliliği/mükerrerlik, [N] çıplak kısaltma, [K] cephanelik-
# ifşa, [T] teslime-hazır/yeşil-makbuz beyanı (YALNIZ kok verilmişse),
# [F] HAFİF KİP künye/damga taraması (v0.5.16 — YALNIZ kok verilmişse, yerel
# kütük), [P] netice-i talep (v0.5.16 — blok varsa) ve [L] kaynak-bloğu
# ilk-satır yokluğu. .udf/zip/npx/resmî-okuyucu bacaklarına
# ASLA girmez (hız şartı: tipik 50KB taslakta < 1 sn; [F] hafif kiple < 2 sn
# — pipeline_kayit INLINE_DENETIM_ZAMAN_SINIRI_SN). CLI davranışı
# DEĞİŞMEZ — main() bu fonksiyonu KULLANMAZ; dört ilke izdüşümü:
# DETERMİNİSTİK (aynı metin → aynı bulgu listesi) · TAMAMLAYICI (denetler,
# muhakeme üretmez) · KESİNTİSİZ (bulgular tek listede akar) · SÜRTÜNMESİZ
# (sessiz ret yok — koşamayan sınıf GÖRÜNÜR "[!]" bulgusudur, hata
# ne-yapmalıyı söyler).

_HIZLI_KOSAMADI = object()  # sentinel: alt denetim kendi içinde çöktü


def hizli_denetim(metin, kok=None):
    """Metin-tabanlı HIZLI denetimlerin tek-çağrılık iç API'si.

    list[str] döndürür; her bulgu "[X] kısa metin" biçimindedir ve EN KRİTİK
    ÖNCE sıralanır: [F] hafif kip (ALEYHE/NÖTR/kütükte-izi-yok künye — K3,
    v0.5.16) EN BAŞTA, sonra BLOK sınıfı ([T] makbuz kapısı, [Y] b/c havada-
    kalan/kapanmayan alıntı), sonra uyarı sınıfı ([Y] d, [K], [M], [N], [P],
    [L]). `kok` verilmemişse [T] ve [F] HİÇ koşulmaz (hızlı kip dosya sistemine
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
        t_ihlal, f_hafif = [], []
        if kok:
            t = _kos("[T]", lambda: teslime_hazir_ihlalleri(metin, kok))
            t_ihlal = [] if t is _HIZLI_KOSAMADI else t
            # v0.5.16 K3: [F] HAFİF KİP — yalnız kok verilmişse (yerel kütük).
            f = _kos("[F]", lambda: ictihat_hafif_kip_bulgulari(metin, kok))
            f_hafif = [] if f is _HIZLI_KOSAMADI else f
        k_uyari = _kos("[K]", lambda: cephanelik_ifsa_uyarilari(metin))
        m_uyari = _kos("[M]", lambda: madde_numara_uyarilari(metin))
        n_uyari = _kos("[N]", lambda: ciplak_kisaltma_uyarilari(metin))
        # v0.5.16 P0-4: [P] — hızlı kipte 'blok bulunamadı' satırı BASILMAZ
        # (taslak yazılırken talep bölümü henüz doğmamış olabilir; her Write'ta
        # gürültü üretmek advisory'yi kör eder) — o satır CLI'nın işidir.
        p_uyari = _kos("[P]", lambda: (
            [] if _p_talep_blogu(metin) is None else netice_talep_uyarilari(metin)))
        l_uyari = _kos("[L]", lambda: kaynak_blogu_uyarilari(metin))

        def _liste(x):
            return [] if x is _HIZLI_KOSAMADI else list(x)

        # [F] hafif kip EN BAŞA (K3: inline hook ilk 5 bulguyu gösterir —
        # ALEYHE künye asla 6. sıraya düşüp görünmez kalmasın), sonra BLOK
        # sınıfı ([T] teslim yalanı, [Y] b/c alıntı), sonra uyarılar.
        bulgular = ["[F] " + b for b in f_hafif]
        bulgular += ["[T] " + b for b in t_ihlal]
        bulgular += ["[Y] " + b for b in y_blok]
        bulgular += ["[Y] " + b for b in y_uyari]
        bulgular += ["[K] " + b for b in _liste(k_uyari)]
        bulgular += ["[M] " + b for b in _liste(m_uyari)]
        bulgular += ["[N] " + b for b in _liste(n_uyari)]
        bulgular += ["[P] " + b for b in _liste(p_uyari)]
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

    # A) zorunlu unsurlar — v0.5.18: tekil/bileşik/yakınlık/koşullu modeli
    # (Y-06). Düz-liste unsurlar eskisi gibi değerlendirilir; dönüş imzası
    # ve 5'li arity DEĞİŞMEDİ.
    eksik = zorunlu_unsur_eksikleri(metin, tip)

    # B) tertip-düzen (+ [B2] kanun-yolu tip-koşullu yapısal kalemler — M3-2;
    # v0.5.18: form nitelikli icra taleplerinde DUZEN_MUAF kalemleri aranmaz)
    muaf = DUZEN_MUAF.get(tip, set())
    duzen_eksik = [ad for ad, des in DUZEN if ad not in muaf and not _bul(metin, des)]
    if tip in KANUN_YOLU_TIPLERI:
        duzen_eksik += _kanun_yolu_yapisal_eksik(metin)

    # C) OCR ⚠ alıntı → teyit şerhi
    ocr_var = ("⚠" in metin) or re.search(r"\bOCR\b", metin, re.I)
    ocr_serh = re.search(r"orijinal.*teyit|teyit\s*(edil|gerek)|RG.*teyit", metin, re.I)
    ocr_uyari = bool(ocr_var and not ocr_serh)

    # D) müvekkil-aleyhi ifade (tek katı sınır) — OLUMSUZLAMA KORUMALI
    # Standart cevap kalıbı "davanın kabulü anlamına gelmemek kaydıyla" / "kabul etmediğimiz"
    # sahte alarm üretmesin: ±70 karakter penceresinde olumsuzlama varsa sinyal düşürülür.
    # DİKKAT (B3) — `\bkabul\s*etme` KELİME SINIRI OLMADAN yazılamaz: Türkçede
    # `-me` hem OLUMSUZLUK eki (`kabul etmemek`) hem MASTAR/çekim ekidir
    # (`kabul etmektedir`, `kabul etmekteyiz`, `kabul etmesi` — bunlar OLUMLU
    # İKRARDIR). Sınırsız desen, en yaygın ikrar kalıbını "olumsuzlanmış" sayıp
    # BLOK'tan BİLGİ'ye düşürüyordu (müvekkil ikrarı sessizce onaylanmış olur;
    # HMK m.188 — ikrar kesin delildir, geri alınamaz). Gerçek olumsuz çekimler
    # zaten ayrı ayrı listelidir: etmedi/etmiyor/etmemek/etmez.
    NEG = re.compile(r"anlamına\s*gelme|kaydıyla|etmedi[ğg]|etmiyor|etmemek|etmez|\bkabul\s*etme\b"
                     r"|redd|aksi|\bdeğil|olmaks[ıi]z[ıi]n|olmamak", re.I)
    aleyhe, aleyhe_notu = [], []
    _setler, _kismi, _sebep = aleyhe_kapsami(taraf, tip)
    # v0.5.18 — `(?#kesin)` kalıplar (çekimli olumlu yüklem; bkz. _KESIN) NEG
    # penceresine bakılmadan sinyal verir. Aynı ifadeyi kapsayan GENİŞ kalıbın
    # eşleşmesi ayrıca raporlanmaz — aynı cümle hem [UYARI] hem 'olumsuzlanmış'
    # [BİLGİ] olarak çelişkili görünmesin. Kesin kalıp yoksa davranış aynen eskisidir.
    kesin_araliklar = []
    for anahtar in _setler:
        for d in ALEYHE.get(anahtar, []):
            if d.startswith(_KESIN):
                for m in re.finditer(d, metin, re.I):
                    aleyhe.append(m.group(0))
                    kesin_araliklar.append((m.start(), m.end()))
    for anahtar in _setler:
        for d in ALEYHE.get(anahtar, []):
            if d.startswith(_KESIN):
                continue
            for m in re.finditer(d, metin, re.I):
                if any(m.start() < b and a < m.end() for a, b in kesin_araliklar):
                    continue
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
                             "yemin", "idari-kanal", "genel"]
                    # v0.5.18 — icra ailesi + idari dava, YD talebi, ceza istinafı
                    + sorted(set(_ICRA_TIPLERI) | set(_IDARI_CEZA_TIPLERI)))
    ap.add_argument("--taraf", default="",
                    choices=["", "davaci", "davali", "sanik", "katilan", "mudahil", "musteki",
                             "alacakli", "borclu", "ucuncu-kisi"])
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
    # v0.5.18 — tipe özel İSTİŞARİ uyarılar (exit koduna dokunmaz; bilinçli
    # avukat tercihi olabilecek ya da eski tipte kilit testleri bozmadan
    # görünür kılınan kalemler — bkz. TIP_UYARILARI).
    for u in tip_ozel_uyarilari(metin, a.tip):
        print(f"   [UYARI] {u}")

    print("\n[B] TERTİP-DÜZEN (avukata yakışan biçim)")
    if duzen_eksik:
        for u in duzen_eksik:
            print(f"   [UYARI] {u} — zayıf/görünmüyor")
    else:
        print("   [OK] başlık/bölüm/netice/imza düzeni kurulu")

    print("\n[S] SÜRE BAĞLANTISI (bilgi — süre HESABI oa-sure'ündür, ASLA bloklamaz)")
    s_satirlar = sure_baglantisi(a.tip)
    if s_satirlar:
        for s in s_satirlar:
            print(f"   • {s}")
        print("   (son gün: oa-sure/scripts/hesapla_sure.py ile, belgeli başlangıç tarihinden "
              "hesaplanır — kapı tarih ÜRETMEZ)")
    else:
        # Etiketsiz madde işareti BİLİNÇLİDİR: '[BİLGİ]' etiketi zincirde
        # (teslim_paketi.py (a) bölümü) "bir kapı atlandı/koşulmadı" anlamında
        # okunur; süre bağlantısı tanımsız bir tip ise atlama değildir.
        print("   • bu tip için tanımlı süre bağlantısı yok — süre doğuran bir işlem "
              "varsa oa-sure ile ayrıca hesaplayın")

    print("\n[C] OCR/⚠ ALINTI TEYİDİ")
    if ocr_uyari:
        print("   [UYARI] OCR/⚠ işareti var ama 'orijinalden teyit' şerhi görünmüyor — "
              "künye/sayısal veriyi orijinalden doğrula.")
    else:
        print("   [OK] OCR-teyit şerhi sorunu görünmüyor")

    print("\n[D] MÜVEKKİL-ALEYHİ İFADE TARAMASI (anayasal — tek katı sınır)")
    # B2/B4 — KAPSAM ÖNCE YAZILIR: bu kapı "bakmadım"ı "bulamadım" diye
    # gösteremez. Taraf sıfatı yoksa/sözlükte karşılığı yoksa yalnız iki desenli
    # 'genel' seti taranır; taraf-özel eksenler (kabul/ikrar, feragat, şikayetten
    # vazgeçme, suç ikrarı) HİÇ taranmaz — ve eski çıktı buna rağmen
    # "[OK] ... bulunamadı" basıp YANLIŞ GÜVENCE veriyordu.
    _setler, _kismi, _sebep = aleyhe_kapsami(a.taraf, a.tip)
    if _kismi:
        print(f"   [UYARI] TARAMA KISMİ — {_sebep}. Yalnız 'genel' kalıp seti tarandı; "
              "taraf-özel eksenler (kabul/ikrar · feragat · şikayetten vazgeçme · "
              "suç ikrarı · icra itirazından vazgeçme) TARANMADI.")
        print("           → --taraf davaci|davali|sanik|katilan|mudahil|musteki|alacakli|"
              "borclu|ucuncu-kisi VERİP YENİDEN KOŞ; aksi hâlde aşağıdaki sonuç bir "
              "TEMİZLİK BEYANI DEĞİLDİR.")
    else:
        print("   [KAPSAM] taranan kalıp setleri: %s" % ", ".join(_setler))
    if aleyhe:
        for s in sorted(set(aleyhe)):
            print(f"   [UYARI] olası müvekkil-aleyhi ifade: \"{s}\" — avukat TEYİT ETMELİ; "
                  "dış çıktı müvekkil lehine kurgulanır (davalıda kabul/ikrar YOK).")
    elif _kismi:
        print("   [—] taranan DAR kapsamda sinyal yok — bu 'temiz' DEMEK DEĞİLDİR (bkz. yukarıdaki UYARI).")
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

    print("\n[P] NETİCE-İ TALEP (advisory — v0.5.16 P0-4/A-22, ASLA bloklamaz; "
          "faiz türü/başlangıcı · fazlaya ilişkin · gider+vekâlet ücreti)")
    p_uyarilar = netice_talep_uyarilari(metin)
    if p_uyarilar:
        for u in p_uyarilar:
            print(f"   [UYARI] {u}")
    else:
        print("   [OK] talep bloğunda mekanik eksik sinyali yok (faiz türü seçimi ve "
              "talep dizilişi avukat kararıdır — playbook: NETİCE-İ TALEP)")

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

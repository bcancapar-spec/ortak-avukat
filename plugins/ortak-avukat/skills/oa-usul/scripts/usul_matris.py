#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa-usul deterministik EKSİKSİZLİK motoru (v2 — kamu cephesi dahil).

Model hukuku düşünür; bu script analizin BOŞLUKSUZ olduğunu mekanik garanti eder:
  G1  Tarihli her işlem süre denetiminden geçmiş mi (son_gun + fiili_tarih karşılaştırılmış mı)?
  G2  KARŞI tarafın her kaçırması (a) usuli sonuca bağlanmış ve (b) kapıları KAPATILMIŞ mı?
  G3  MÜVEKKİLİN her hatası için ÜÇ KANALLI kapı araştırması yapılmış mı (içtihat+doktrin+web)?
  G4  Tebliğ tarihi BELGESİZ iken kesin dil kullanımı engellenmiş mi (kesin_dil=true yasak)?
  G5  Açılan her kapının KENDİ süresi hesaplanmış mı (kapi_suresi_hesaplandi)?
  G6  Her KAMU işlemi unsur denetiminden geçmiş mi (yetki + şekil + AY m.40/2 başvuru-yolu sorusu)?
  G7  Tespit edilen kamu aykırılığı NİTELENMİŞ (iptal/yokluk/süre-işlemez/delil-yasağı),
      içtihatla teyitli ve bir KAPIYA dönüştürülmüş mü?
  G8  Kasıt deseni iddiası BELGESİZ iken metinde "kasıt" dili engellenmiş mi (ihtiyat kilidi)?
  G9  Kesin dil izni verilen işlemde son_gun'ün DAYANAĞI yazılmış mı ve kendi
      içinde tutarlı mı (`sure_kurali` + `yargi_kolu` dolu; kural adının öneki
      beyan edilen yargı kolunu yalanlamıyor)?
  Z   (v0.5.16 — P2-3/A-8, ADVISORY) Karşı taraf kusurunda opsiyonel
      `tamamlanabilir: true|false` + `zamanlama: simdi|sonra|avukat_karari`:
      tamamlanabilir kusurda (harç, vekâletname, dilekçe eksiği — HMK m.119/2,
      m.115/2, m.77) "ne zaman ileri sür" AVUKAT KARARIDIR — erken ileri
      sürülürse karşı taraf kesin sürede tamamlar. Zamanlama yazılmamışsa
      bulgu satırı «tamamlanabilir kusurda zamanlama kararı yok» basılır;
      BOŞLUK DEĞİLDİR (exit sözleşmesi korunur). Tamamlanamaz kusurda (süre)
      "derhâl" kuralı (anayasa m.2) işler; zamanlama sorusu sorulmaz.
  G10 (v0.5.18) AYM BİREYSEL BAŞVURU kabul edilebilirlik kontrol listesi (6216
      m.45-48, m.51, geçici m.1/8; İçtüzük m.59/60 form + ekler) + karar
      sonrası (m.50/1-2: ihlal kaynağı zorunlu).
  G11 (v0.5.18) AİHM BAŞVURU kabul edilebilirlik kontrol listesi (AİHS m.34,
      m.35/1, m.35/2-b, m.35/3-a/b; eksiksiz başvuru) + 4/6 ay rejimi + karar
      sonrası (yeniden yargılama HMK m.375/1-i, CMK m.311/1-f, İYUK m.53/1-ı;
      adil tazmin m.41). Girdi: üst düzey `bireysel_basvuru` listesi (şablon:
      `--ornek-bb`; şema: references/bireysel-basvuru-yolu.md §8).
      Script KARAR VERMEZ: değerlendirilmemiş ölçüt / kanıtsız «tamam» /
      «eksik» BOŞLUKTUR; «supheli» ve «karsilanmiyor» avukat kararına giden
      görünür bulgudur (gerekçe zorunlu); «karsilanmiyor» ve SÜRE GEÇMİŞ
      hâlinde avukat kararı (devam|vazgec) KAYDA geçmeden boşluk kapanmaz.
Boşluk varsa adıyla raporlar ve exit(1) — boşluklu usul analizi teslim edilemez.

Süre HESABI bu scriptin işi değildir → oa-sure/hesapla_sure.py (son_gun oradan gelir).
[G9] de süre HESAPLAMAZ ve HUKUKİ NİTELENDİRME YAPMAZ (hangi kuralın uygulanacağına
karar vermez): yalnız alanların DOLU ve BİRBİRİYLE TUTARLI olduğuna bakar. Tanınmayan
kural öneki / yargı kolu değeri "bilinmiyor" sayılır ve boşluk üretmez.

Kullanım:
  python usul_matris.py --ornek > dosya_usul.json     # girdi şablonu
  python usul_matris.py --ornek-bb > bb.json          # v0.5.18: AYM/AİHM şablonu
  python usul_matris.py --girdi dosya_usul.json       # denetim raporu
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, ast, json, os, re, sys
from datetime import date

BURA = os.path.dirname(os.path.abspath(__file__))
# oa-sure — süre kuralı kataloğunun ve kural→kol konvansiyonunun TEK kaynağı.
SURE_SCRIPTLERI = os.path.normpath(os.path.join(BURA, "..", "..", "oa-sure", "scripts"))

ORNEK = {
  "dosya": "Örnek 2026/000",
  "yargi_kolu": "hukuk",
  "islemler": [
    {"id": "I1", "taraf": "karsi", "islem": "istinaf", "sure_kurali": "hmk_istinaf",
     "teblig": "2026-04-01", "teblig_belgeli": True,
     "son_gun": "2026-04-15", "fiili_tarih": "2026-04-20",
     "sonuc_norm": "HMK m.346/352 — süreden ret", "sonuc_ictihat_teyit": True,
     "kapi_kapatma": [{"kapi": "K-1 eski hâle getirme", "kapatma": "mazeret iddiası yok; 2 hafta da geçti"},
                        {"kapi": "K-2 usulsüz tebliğ", "kapatma": "e-tebligat UETS kaydı belgeli (7201 m.7/a)"}],
     "kesin_dil": True,
     "tamamlanabilir": False, "zamanlama": "simdi"},
    {"id": "I2", "taraf": "biz", "islem": "cevap", "sure_kurali": "hmk_cevap",
     "teblig": "2026-03-02", "teblig_belgeli": False,
     "son_gun": "2026-03-16", "fiili_tarih": "2026-03-20",
     "kapi_arastirmasi": {"ictihat": True, "doktrin": True, "web": True,
        "kapilar": [{"kapi": "K-2 usulsüz tebliğ (7201 m.32)", "norm_teyit": True,
                      "kapi_suresi_hesaplandi": True, "uygulanabilirlik": "güçlü — tebliğ m.21 prosedürü sakat"}]},
     "kesin_dil": False},
    {"id": "K1", "taraf": "kamu", "aktor": "idare", "islem": "disiplin cezası tebliği",
     "unsur_denetimi": {"yetki": True, "sekil": True, "ay40_basvuru_yolu_gosterildi": False},
     "aykiriliklar": [{"aykirilik": "işlemde başvuru mercii ve süresi gösterilmemiş",
        "niteleme": "AY m.40/2 — süre işlemez", "ictihat_teyit": True,
        "kapiya_donusturuldu": "K-12"}],
     "kasit_deseni": {"var": True, "belgeli": False, "metinde_kasit_dili": False}}
  ]
}

def _d(s): return date.fromisoformat(s) if s else None


# ── [G9] süre dayanağı tutarlılık tablosu (v0.5.14 — denetim bulgusu B-9) ────
# Bu tablo HUKUKİ NİTELENDİRME DEĞİLDİR: `oa-sure` kural anahtarlarının ÖNEK
# KONVANSİYONUDUR. Script hangi kuralın uygulanacağına karar vermez; yalnız
# "kural adı ile beyan edilen yargı kolu birbirini yalanlıyor mu" sorusunu sorar.
# Önek tabloda YOKSA hüküm verilmez ("bilinmiyor") — eski/özel kanun kuralları
# kapıda düşmez (CLAUDE.md: eski dosyada alan yoksa script çökmez, "bilinmiyor" der).
#
# v0.5.18 — İKİZ LİSTE KALDIRILDI: tablo artık oa-sure'nin KENDİ tanımından
# (`hesapla_sure.py` → `KURAL_KOLU` + kurala özgü `_KOL_EK_IZIN`) IMPORT
# EDİLMEDEN, AST ile okunur. NEDEN: oa-sure v0.5.18'de «iik» kolu «icra» oldu
# (İİK süreleri adli tatille uzamaz — eski «hukuk» eşlemesi HMK m.104 uzatmasıyla
# GEÇ son gün üretiyordu) ve «aihm» kol-bağımsız önek olarak geldi; bu scriptteki
# elle kopya tablo ikisini de «bilinmiyor» sayıyordu (sınıflama kördü). Kaynak
# okunamazsa tablo BOŞ kalır ve her satır görünür «bilinmiyor» bulgusu üretir
# (sessiz varsayım yok; süre HESABINA dokunulmaz — o oa-sure'nindir).
def _oa_sure_kol_kaynagi(yol=None):
    """(önek→kol|None, kural→ek izinli kollar) — oa-sure `hesapla_sure.py`deki
    `KURAL_KOLU` ve `_KOL_EK_IZIN` sözlük literallerinden. Okunamaz/çözülemezse
    ({}, {}) döner."""
    yol = yol or os.path.join(SURE_SCRIPTLERI, "hesapla_sure.py")
    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            agac = ast.parse(f.read())
    except (OSError, SyntaxError, ValueError):
        return {}, {}
    bulunan = {}
    for dugum in agac.body:
        if isinstance(dugum, ast.Assign) and len(dugum.targets) == 1 and \
                isinstance(dugum.targets[0], ast.Name) and \
                dugum.targets[0].id in ("KURAL_KOLU", "_KOL_EK_IZIN"):
            try:
                bulunan[dugum.targets[0].id] = ast.literal_eval(dugum.value)
            except (ValueError, TypeError, SyntaxError):
                pass
    kol = bulunan.get("KURAL_KOLU")
    ek = bulunan.get("_KOL_EK_IZIN")
    kol = {str(k): (v if v is None else str(v)) for k, v in kol.items()} \
        if isinstance(kol, dict) else {}
    ek = {str(k): {str(x) for x in v} for k, v in ek.items()
          if isinstance(v, (set, list, tuple))} if isinstance(ek, dict) else {}
    return kol, ek


_SURE_KURAL_KOLU, KURAL_EK_IZIN = _oa_sure_kol_kaynagi()
KURAL_ONEK_KOL = {onek: (None if kol is None else {kol})
                  for onek, kol in _SURE_KURAL_KOLU.items()}
# Yargı kolu için kabul edilen yazımlar (eş anlamlı normalizasyon; kapalı küme).
# v0.5.18: «icra» oa-sure'nin icra koludur (iik_* kuralları).
KOL_ESANLAM = {"hukuk": "hukuk", "adli": "hukuk", "ozel": "hukuk",
               "ceza": "ceza",
               "idari": "idari", "idare": "idari", "vergi": "idari",
               "icra": "icra"}


def _kol_normalize(ham):
    """(normalize|None, ham) — kapalı küme dışı değer NİTELENDİRİLMEZ."""
    h = str(ham or "").strip().lower()
    return KOL_ESANLAM.get(h), h


def _kural_kolu(kural):
    """(izinli_kol_kumesi|None, onek) — önek tanınmıyorsa (None, onek).
    Kurala özgü ek izin (oa-sure `_KOL_EK_IZIN`, ör. icra ceza şikâyeti ceza
    koluyla da çelişmez) izinli kümeye eklenir."""
    k = str(kural or "").strip().lower()
    onek = k.split("_", 1)[0] if k else ""
    if onek in KURAL_ONEK_KOL:
        izinli = KURAL_ONEK_KOL[onek]
        if izinli is not None and k in KURAL_EK_IZIN:
            izinli = izinli | KURAL_EK_IZIN[k]
        return izinli, onek
    return None, onek


def _g9_denetle(i, iid, ust_kol, bulgular, bosluklar):
    """[G9] — kesin dil izninin süre DAYANAĞI denetimi (B-9).

    İki dal:
      (a) `kesin_dil` TALEP EDİLMİŞSE dayanak alanları DOLU olmalıdır;
      (b) alanlar dolu ama BİRBİRİNİ YALANLIYORSA (kural öneki ↔ yargı kolu)
          kesin dil talep edilmese de boşluktur — çelişki gerçek çelişkidir.
    Alanları hiç taşımayan eski artefakt (b) dalını tetikleyemez → kapıda düşmez.
    """
    kesin = bool(i.get("kesin_dil"))
    kural = str(i.get("sure_kurali") or "").strip()
    kol_ham = i.get("yargi_kolu") if i.get("yargi_kolu") is not None else ust_kol
    kol, kol_yazim = _kol_normalize(kol_ham)

    if kesin:
        if not kural:
            bosluklar.append(
                f"[G9] {iid}: kesin_dil=true ama 'sure_kurali' BOŞ — son_gun'ün hangi "
                f"kurala dayandığı belirsiz; kesin dil izni verilemez (oa-sure ile "
                f"hesapla ve kural adını yaz).")
        if not kol_yazim:
            bosluklar.append(
                f"[G9] {iid}: kesin_dil=true ama 'yargi_kolu' BOŞ (ne işlemde ne üst "
                f"düzeyde) — süre rejimi belirsizken kesin dil izni verilemez.")

    if not kural or not kol_yazim:
        return

    izinli, onek = _kural_kolu(kural)
    if izinli is None:
        if not KURAL_ONEK_KOL:
            bulgular.append(
                f"  {iid}: süre dayanağı '{kural}' — kural/kol tablosu okunamadı "
                f"(oa-sure/scripts/hesapla_sure.py KURAL_KOLU); yargı kolu uyumu "
                f"bilinmiyor (script nitelendirme yapmaz).")
        elif onek not in KURAL_ONEK_KOL:
            bulgular.append(
                f"  {iid}: süre dayanağı '{kural}' — kural öneki tabloda yok, yargı kolu "
                f"uyumu bilinmiyor (script nitelendirme yapmaz; teyit avukattadır).")
        return
    if kol is None:
        bulgular.append(
            f"  {iid}: yargı kolu '{kol_yazim}' kapalı küme dışı — kural/kol uyumu "
            f"bilinmiyor (script nitelendirme yapmaz).")
        return
    if kol not in izinli:
        bosluklar.append(
            f"[G9] {iid}: süre dayanağı ÇELİŞKİLİ — '{kural}' kuralı ile beyan edilen "
            f"yargı kolu '{kol_yazim}' birbirini yalanlıyor; script nitelendirme yapmaz, "
            f"hangisinin doğru olduğunu oa-sure ile teyit edip düzelt "
            f"(yanlış rejimde hesaplanmış son_gun kesin dille sunulamaz).")
    else:
        bulgular.append(
            f"  {iid}: süre dayanağı '{kural}' ↔ yargı kolu '{kol}' tutarlı "
            f"(hesap oa-sure'nindir; script yalnız tutarlılığa bakar).")


# ── [Z] tamamlanabilir kusur × zamanlama (v0.5.16 — P2-3/A-8, ADVISORY) ──────
# Karşı tarafın usul kusuru iki sınıftır:
#   TAMAMLANAMAZ (süre kaçırma): sonucu kesindir → "derhâl" ileri sürülür
#     (anayasa m.2: kaçırılmış süre en ucuz kazanımdır, gizli tutulmaz).
#   TAMAMLANABİLİR (harç ikmali 492; vekâletname HMK m.77; dilekçe eksiği HMK
#     m.119/2; giderilebilir dava şartı m.115/2 — Mevzuat MCP teyit 2026-09-06):
#     erken ileri sürülürse mahkeme kesin süre verir ve karşı taraf TAMAMLAR;
#     "ne zaman ileri sür" bu yüzden AVUKAT KARARIDIR. Script karar vermez,
#     yalnız kararın YAZILIP YAZILMADIĞINA bakar (advisory; boşluk üretmez —
#     exit sözleşmesi korunur). Saha dersi: karşı tarafın vekâletname eksiğini
#     ilk celsede ileri süren, ona ikinci celseye kadar tamamlama süresi
#     kazandırır; sessiz kalıp kesin sürenin kaçmasını izleyen, dosyayı kapatır.
ZAMANLAMA_ENUM = {"simdi", "sonra", "avukat_karari"}


def _zamanlama_denetle(i, iid, kim, bulgular):
    """[Z] — advisory; hiçbir dalı `bosluklar`a yazmaz."""
    if "tamamlanabilir" not in i and "zamanlama" not in i:
        return                      # eski artefakt: alan yok → satır yok
    if kim != "karsi":
        bulgular.append(
            f"  {iid}: 'tamamlanabilir/zamanlama' alanı yalnız karşı taraf kusurunda "
            f"(A-cephesi) anlamlıdır — '{kim}' kaydında yok sayıldı.")
        return
    t = i.get("tamamlanabilir")
    if not isinstance(t, bool):
        bulgular.append(
            f"  {iid}: 'tamamlanabilir' değeri bool değil ({t!r}) — script "
            f"nitelendirme yapmaz; alan yok sayıldı (true/false yaz).")
        return
    if t is False:
        bulgular.append(
            f"  {iid}: TAMAMLANAMAZ kusur (süre) → 'derhâl' kuralı: sonuç kesin, "
            f"zamanlama sorusu yok (anayasa m.2).")
        return
    z_ham = i.get("zamanlama")
    z = str(z_ham).strip() if isinstance(z_ham, str) else ""
    if z and z not in ZAMANLAMA_ENUM:
        bulgular.append(
            f"  {iid}: 'zamanlama' değeri kapalı enum dışı ('{z_ham}') — script "
            f"nitelendirme yapmaz; 'bilinmiyor' sayıldı "
            f"(simdi|sonra|avukat_karari).")
        z = ""
    if not z:
        bulgular.append(
            f"  {iid}: TAMAMLANABİLİR kusur — tamamlanabilir kusurda zamanlama kararı "
            f"yok: erken ileri sürülürse karşı taraf kesin sürede tamamlar; "
            f"'ne zaman' AVUKAT KARARIDIR (zamanlama=simdi|sonra|avukat_karari yaz).")
        return
    bulgular.append(
        f"  {iid}: TAMAMLANABİLİR kusur — zamanlama={z} (kayıtlı; karar avukatındır, "
        f"script yalnız kararın yazıldığına bakar).")


def _kamu_denetle(i, iid, bulgular, bosluklar):
    aktor = i.get("aktor", "?")
    # G6 — unsur denetimi (her kamu işleminde standart üçlü soru)
    ud = i.get("unsur_denetimi")
    if not ud:
        bosluklar.append(f"[G6] {iid} (kamu/{aktor}): unsur denetimi HİÇ yapılmamış "
                         f"(yetki + şekil + AY m.40/2 başvuru-yolu üçlüsü zorunlu).")
    else:
        for alan, ad in (("yetki","yetki"),("sekil","şekil"),("ay40_basvuru_yolu_gosterildi","AY m.40/2 başvuru yolu")):
            if alan not in ud:
                bosluklar.append(f"[G6] {iid}: '{ad}' sorusu sorulmamış (unsur_denetimi.{alan} eksik).")
        if ud.get("ay40_basvuru_yolu_gosterildi") is False:
            bulgular.append(f"{iid} (kamu/{aktor}) {i.get('islem')}: AY m.40/2 İHLALİ adayı — "
                            f"başvuru yolu gösterilmemiş → süre-işlemez kapısı (K-12).")
    # G7 — aykırılıklar nitelenmiş + teyitli + kapıya dönüştürülmüş
    ayk = i.get("aykiriliklar") or []
    if ud and any(ud.get(a) is False for a in ud) and not ayk:
        bosluklar.append(f"[G7] {iid}: unsur denetimi aykırılık gösteriyor ama 'aykiriliklar' kaydı yok.")
    for a in ayk:
        ne = a.get("aykirilik","?")
        if not a.get("niteleme"):
            bosluklar.append(f"[G7] {iid}/'{ne}': NİTELEME yok (iptal/yokluk/süre-işlemez/delil-yasağı merdiveni).")
        if not a.get("ictihat_teyit"):
            bosluklar.append(f"[G7] {iid}/'{ne}': içtihat teyidi yok (oa-ictihat).")
        if not a.get("kapiya_donusturuldu"):
            bosluklar.append(f"[G7] {iid}/'{ne}': bir KAPIYA dönüştürülmemiş (Kapı Kataloğu eşlemesi).")
        else:
            bulgular.append(f"  {iid}: '{ne}' → {a.get('niteleme')} → kapı {a.get('kapiya_donusturuldu')}")
    # G8 — kasıt ihtiyat kilidi
    kd = i.get("kasit_deseni") or {}
    if kd.get("var"):
        if kd.get("metinde_kasit_dili") and not kd.get("belgeli"):
            bosluklar.append(f"[G8] {iid}: kasıt deseni BELGESİZ iken metinde kasıt dili kullanılmış — yasak; "
                             f"sonucu objektif aykırılıktan al, deseni dahili raporda tut.")
        else:
            bulgular.append(f"  {iid}: kasıt deseni kaydı — belgeli={kd.get('belgeli')}, "
                            f"metin dili={'kasıt' if kd.get('metinde_kasit_dili') else 'objektif aykırılık'} (kural uyumlu).")


# ── [G10]/[G11] BİREYSEL BAŞVURU YOLU — AYM / AİHM (v0.5.18) ────────────────
# NEDEN VAR: AYM bireysel başvuru ve AİHM yolu çoğu dosyanın SON çıkış kapısıdır
# ve hatası telafisizdir: süresi kaçmış, yolu tüketilmemiş, formu eksik ya da
# «dördüncü derece» şikâyetine dönmüş başvuru esasa hiç girmeden reddedilir;
# AYM'nin kabul edilemezlik kararı «dosya bitti» sanılırsa AİHM penceresi
# sessizce kapanır. Bu blok, Yargı PRO 5-1/5-3/5-4/5-5 ve 6-1…6-5 skill'lerinin
# FİKRİNİ (eşik → ölçüt → giderim zinciri) OA yöntemiyle kurar: model her ölçütü
# değerlendirir, script yalnız DEĞERLENDİRMENİN EKSİKSİZ ve kanıtlı olduğunu
# denetler. Hukuki sonuç (gidilir/gidilmez) AVUKATINDIR — script «karşılanmıyor»
# diye işaretlenen ölçütü görünür kılar, başvuruyu yasaklamaz.
# Dayanak satırlarının tamamı resmî metinden teyit edildi (2026-10-05, Yargı
# PRO): 6216 m.45-50 ve geçici m.1/8, AYM İçtüzüğü m.59/m.63/m.66 (mevzuat.gov.tr
# `mevzuat_getir`); AİHS m.35/1 güncel metni ve 01.02.2022 geçişi Orhan/Türkiye
# (k.k.), no. 38358/22, §§ 25-26, 44; m.35/3-b Ağcakaya/Türkiye (k.k.), no.
# 39365/18, § 10 (HUDOC `ictihat_getir`). AİHM İçtüzüğü m.47 metni MCP'de yok
# → TEYİT BEKLİYOR (etiket raporda görünür).
# Fable karşı-tez turu (2026-10-05): 6216 m.48/2'nin iki eşiği ayrıldı, 6216
# m.51 (kötüye kullanma) ve AİHS m.35/2-b, m.35/3-a (kötüye kullanma) ölçüt
# oldu; harç belgesi (59/3-b) adli yardımda, kanun yolu dilekçeleri (59/3-g)
# ve tüketme aşamaları (59/2-f) başvuru yolu öngörülmemişse «uygulanmaz»
# olabilir (6216 m.47/3-5, İçtüzük m.59/4, m.62/2 — mevzuat.gov.tr metinleri).
DURUM_ENUM = ("tamam", "eksik", "supheli", "karsilanmiyor", "uygulanmaz")

# (anahtar, ölçüt, dayanak, «uygulanmaz» olabilir mi)
AYM_KRITERLER = (
    ("konu_bakimindan", "Konu bakımından yetki: hak Anayasa VE AİHS (+ Türkiye'nin "
     "taraf olduğu ek protokoller) ortak alanında; yasama işlemi/düzenleyici işlem "
     "aleyhine doğrudan başvuru yok", "6216 m.45/1, m.45/3", False),
    ("kisi_bakimindan", "Kişi bakımından yetki / MAĞDUR SIFATI: güncel, kişisel ve "
     "DOĞRUDAN etkilenme; kamu tüzel kişisi başvuramaz; özel hukuk tüzel kişisi yalnız "
     "kendi hakları; yabancı, yalnız Türk vatandaşlarına tanınan haklarda başvuramaz",
     "6216 m.46", False),
    ("zaman_bakimindan", "Zaman bakımından yetki: 23.09.2012'den sonra kesinleşen nihai "
     "işlem/karar", "6216 geçici m.1/8", False),
    ("yollarin_tuketilmesi", "Kanunda öngörülen idari ve yargısal başvuru yollarının "
     "TAMAMI tüketildi (şikâyetin özü derece yargısında ileri sürüldü)",
     "6216 m.45/2", False),
    # m.48/2'nin İKİ AYRI eşiği ayrı değerlendirilir (Fable karşı-tez turu):
    # birincisi BİRLİKTE aranan iki koşuldur (önem taşımama VE önemli zarar
    # olmaması), ikincisi açıkça dayanaktan yoksunluktur.
    ("anayasal_onem_onemli_zarar", "Başvuru Anayasanın uygulanması/yorumlanması ya da "
     "temel hakların kapsamı/sınırları bakımından önem taşıyor YA DA başvurucu önemli "
     "bir zarara uğradı (ikisi birden yoksa kabul edilemezlik)", "6216 m.48/2", False),
    ("acik_dayanaktan_yoksunluk", "Açıkça dayanaktan yoksun değil; kanun yolunda "
     "gözetilecek husus («dördüncü derece» şikâyeti) değil",
     "6216 m.48/2, m.49/6", False),
    ("kotuye_kullanmama", "Bireysel başvuru hakkı açıkça kötüye kullanılmıyor (aksi "
     "hâlde yargılama giderleri dışında 2.000 TL'ye kadar disiplin para cezası)",
     "6216 m.51", False),
)
# AYM başvuru formu (İçtüzük m.59/2) ve zorunlu ekler (m.59/3) + m.60/2 özet.
# Üçüncü öğe «uygulanmaz» olabilir mi: True | False | KOŞULLU etiket —
#   "adli_yardim": yalnız adli yardım talebi (59/3-h) 'tamam' ise (harç
#                  belgesi bu durumda sunulamaz; İçtüzük m.62/2: talebi
#                  Bölüm/Komisyon karara bağlar; m.59/4: sunulamayan belgenin
#                  gerekçesi forma eklenir),
#   "yol_yok"    : yalnız kayıtta "basvuru_yolu_ongorulmemis": true ise (6216
#                  m.47/3 ve 47/5 «başvuru yolu öngörülmemişse» hâlini ayrıca
#                  düzenler — tüketilecek kanun yolu ve dilekçesi yoktur).
AYM_FORM = (
    ("59/2-a", "başvurucunun kimlik ve adres bilgileri", False),
    ("59/2-b", "tüzel kişi bilgileri (MERSİS, unvan, temsile yetkili)", True),
    ("59/2-c", "avukat ya da kanuni temsilci bilgileri", True),
    ("59/2-ç", "kamu gücünün işlem/eylem/ihmaline dair olayların TARİH SIRALI özeti", False),
    ("59/2-d", "hangi hakkın hangi nedenle ihlal edildiği, gerekçe ve delillerin özlü açıklaması", False),
    ("59/2-e", "her hakkın açıklamasının birbiriyle ilişkilendirilerek AYRI AYRI yapılması", False),
    ("59/2-f", "başvuru yollarının tüketilmesi aşamaları (tarih sırasıyla)", "yol_yok"),
    ("59/2-g", "yolların tüketildiği / (yol yoksa) ihlalin öğrenildiği tarih", False),
    ("59/2-ğ", "süresinde yapılamadıysa mazeret açıklaması", True),
    ("59/2-h", "başvurucunun talepleri", False),
    ("59/2-ı", "devam eden başka başvurunun numarası", True),
    ("59/2-i", "kimliğin gizli tutulması talebi ve gerekçesi", True),
    ("59/2-j", "SMS / e-posta ile bilgilendirme tercihi", False),
    ("59/2-k", "başvurucu, avukat ya da kanuni temsilcinin imzası", False),
    ("59/2-l", "İçtüzük m.73 tedbir talebi ve gerekçesi", True),
    ("59/3-a", "EK: temsile yetkili olunduğuna dair belge (vekâletname — 6216 m.47/4)", True),
    ("59/3-b", "EK: harcın ödendiğine dair belge (6216 m.47/2-3)", "adli_yardim"),
    ("59/3-c", "EK: bizzat başvuruda kimliği tespite yarar resmî belgenin onaylı örneği", True),
    ("59/3-ç", "EK: tüzel kişi adına başvuruda temsil yetkisini gösteren belge", True),
    ("59/3-d", "EK: nihai karar/işlemi ÖĞRENME tarihini gösteren belge", False),
    ("59/3-e", "EK: ihlal iddialarını temellendiren belgelerin onaylı örnekleri", False),
    ("59/3-f", "EK: tazminat talebi varsa zarar ve belgeleri", True),
    ("59/3-g", "EK: olağan ve olağanüstü kanun yolu başvuru dilekçelerinin onaylı örnekleri", "yol_yok"),
    ("59/3-ğ", "EK: süresinde yapılamadıysa mazereti ispatlayan belgeler", True),
    ("59/3-h", "EK: adli yardım talebi varsa mali durum belgeleri", True),
    ("60/2", "form (ekler hariç) on sayfayı geçiyorsa olayların özeti", True),
)
AIHM_KRITERLER = (
    ("magdur_sifati", "MAĞDUR SIFATI: başvurucu iddia edilen ihlalden kişisel olarak "
     "etkilenen mağdur", "AİHS m.34", False),
    ("yollarin_tuketilmesi", "İç hukuk yollarının tüketilmesi (Türkiye yönünden AYM "
     "bireysel başvurusu etkili iç hukuk yoludur — Uzun/Türkiye (k.k.), no. 10755/13; "
     "şikâyetin özü AYM'de ileri sürüldü)", "AİHS m.35/1", False),
    ("konu_bakimindan_bagdasma", "Sözleşme hükümleriyle konu bakımından bağdaşma "
     "(şikâyet edilen hak Sözleşme/Protokol kapsamında)", "AİHS m.35/3-a", False),
    ("acik_dayanaktan_yoksunluk", "Açıkça dayanaktan yoksun değil («dördüncü derece» "
     "şikâyeti değil)", "AİHS m.35/3-a", False),
    ("onemli_zarar", "Önemli zarar: başvurucu önemli bir zarar görmüş ya da insan "
     "haklarına saygı esas incelemeyi gerektiriyor", "AİHS m.35/3-b (15 No.lu Protokol)", False),
    # Fable karşı-tez turu — eksik iki ölçüt (HUDOC künye üst verisiyle teyitli:
    # Varnava ve Diğerleri/Türkiye [BD], no. 16064/90 vd., 18.09.2009 — ilgili
    # madde «35-2-b», «substantially the same»; Akdivar ve Diğerleri/Türkiye
    # [BD], no. 21893/93, 16.09.1996 — «(Art. 35-3-a) Abuse of the right of
    # application»).
    ("ayni_konu_baska_merci", "Esasen aynı başvuru daha önce AİHM'ce incelenmemiş ve "
     "başka bir uluslararası soruşturma/çözüm merciine sunulmamış (sunulduysa ilgili "
     "yeni bilgi var)", "AİHS m.35/2-b", False),
    ("kotuye_kullanmama", "Bireysel başvuru hakkı kötüye kullanılmıyor (yanıltıcı "
     "bilgi, saygısız dil vb. — değerlendirme avukatın)", "AİHS m.35/3-a", False),
    ("eksiksiz_basvuru", "Resmî başvuru formu ve zorunlu ekler EKSİKSİZ (eksik form "
     "süreyi korumayabilir)", "AİHM İçtüzüğü m.47 — TEYİT BEKLİYOR", False),
)
# AİHS m.35/1 süresinin 6 aydan 4 aya inişi: iç hukukta kesinleşmiş (nihai)
# karar 01.02.2022'den ÖNCE verildiyse 6 ay, 31.01.2022'den SONRA verildiyse 4
# ay — Orhan/Türkiye (k.k.) § 44. Tarih karşılaştırmasıdır, nitelendirme değil.
AIHM_4AY_GECIS = date(2022, 2, 1)
# Karar sonrası — yanlış yeniden yargılama dayanağı (AYM ihlal kararı için):
# HMK m.375/1-i, CMK m.311/1-f ve İYUK m.53/1-ı AİHM kararına özgüdür
# (mevzuat.gov.tr metinleri); AYM ihlal kararında dayanak 6216 m.50/2'dir.
# Sayılar komşu rakamdan yalıtılır: «HMK m.353/1» bir «53/1» DEĞİLDİR.
_AIHM_OZGU_DAYANAK_RE = re.compile(r"(?<!\d)(?:375|311|53)\s*/\s*1(?!\d)")
# Avukat kararı (karşılanmayan ölçüt / süresi geçmiş başvuru): risk bilinçli
# üstlenilir ya da yoldan vazgeçilir — ikisi de KAYIT altına alınır (G3 simetrisi:
# sahte umut da, sessizlik de yasak).
AVUKAT_KARARLARI = ("devam", "vazgec")
# AYM ihlal kararının kaynağı: mahkeme kararı → 6216 m.50/2 (yeniden
# yargılama); diğer (idari işlem/eylem/ihmal) → 6216 m.50/1 (ihlalin ve
# sonuçlarının ortadan kaldırılması için yapılması gerekenler).
AYM_IHLAL_KAYNAKLARI = ("mahkeme_karari", "diger")
AIHM_YENIDEN_YARGILAMA = {
    "hmk": ("HMK m.375/1-i + m.377/1-e", "kesinleşmiş AİHM kararının TEBLİĞİNDEN üç ay "
            "(on yıllık azami süre (e) bendi yönünden AYM E.2022/7, K.2022/79 ile iptal)"),
    "cmk": ("CMK m.311/1-f", "AİHM kararının KESİNLEŞTİĞİ tarihten bir yıl"),
    "iyuk": ("İYUK m.53/1-ı + m.53/3", "AİHM kararının KESİNLEŞTİĞİ tarihten bir yıl"),
}
AIHM_YY_ACAN = {"ihlal", "dostane_cozum", "tek_tarafli_deklarasyon"}
AYM_KARAR_TURLERI = {"ihlal", "ihlal_yok", "kabul_edilemezlik", "kismi", "dusme"}
AIHM_KARAR_TURLERI = {"ihlal", "ihlal_yok", "kabul_edilemezlik", "dostane_cozum",
                      "tek_tarafli_deklarasyon", "dusme"}


def _kriter_denetle(etiket, bid, anahtar, olcut, dayanak, uyg_olabilir, kayit,
                    bulgular, bosluklar):
    """Tek bir kabul edilebilirlik ölçütü: değerlendirilmiş mi, kanıtlı mı,
    şüpheli/karşılanmıyor ise gerekçeli mi? (Hukuki karar VERMEZ.)"""
    if not isinstance(kayit, dict) or kayit.get("durum") not in DURUM_ENUM:
        bosluklar.append(
            f"[{etiket}] {bid}: '{anahtar}' DEĞERLENDİRİLMEMİŞ ({dayanak}: {olcut}) — "
            f"durum={'|'.join(DURUM_ENUM)} + kanıt/gerekçe yaz.")
        return
    durum = kayit["durum"]
    kanit = str(kayit.get("kanit") or "").strip()
    gerekce = str(kayit.get("not") or "").strip()
    if durum == "tamam":
        if not kanit:
            bosluklar.append(
                f"[{etiket}] {bid}: '{anahtar}' kanıtsız 'tamam' ({dayanak}) — hangi belge/karar "
                f"bunu gösteriyor? (kanıtsız beyan kesin dil sayılmaz)")
        else:
            bulgular.append(f"  [{etiket}] {bid}: {anahtar}: tamam — {kanit} ({dayanak})")
    elif durum == "eksik":
        bosluklar.append(
            f"[{etiket}] {bid}: '{anahtar}' EKSİK bilgi/belge ({dayanak}) — tamamlanmadan "
            f"başvuru hazır sayılamaz" + (f" [{gerekce}]" if gerekce else ""))
    elif durum == "uygulanmaz":
        if not uyg_olabilir:
            bosluklar.append(
                f"[{etiket}] {bid}: '{anahtar}' 'uygulanmaz' OLAMAZ ({dayanak}) — bu ölçüt her "
                f"başvuruda değerlendirilir.")
        else:
            bulgular.append(f"  [{etiket}] {bid}: {anahtar}: uygulanmaz ({dayanak})")
    else:   # supheli | karsilanmiyor
        if not gerekce:
            bosluklar.append(
                f"[{etiket}] {bid}: '{anahtar}' {durum} ama gerekçe ('not') yok ({dayanak}) — "
                f"avukat kararı gerekçesiz verilemez.")
        isaret = ("⚠ ŞÜPHELİ" if durum == "supheli"
                  else "✗ KARŞILANMIYOR — KABUL EDİLEMEZLİK RİSKİ")
        bulgular.append(f"  [{etiket}] {bid}: {anahtar}: {isaret} ({dayanak}) — {gerekce or '—'} "
                        f"→ AVUKAT KARARI (script başvuruyu yasaklamaz).")
        if durum == "karsilanmiyor":
            karar = kayit.get("avukat_karari")
            if karar not in AVUKAT_KARARLARI:
                bosluklar.append(
                    f"[{etiket}] {bid}: '{anahtar}' KARŞILANMIYOR ama avukat_karari "
                    f"({'|'.join(AVUKAT_KARARLARI)}) yazılmamış — risk bilinçli üstlenilir "
                    f"ya da yoldan vazgeçilir; ikisi de kayda geçer.")
            else:
                bulgular.append(f"  [{etiket}] {bid}: {anahtar}: avukat kararı → {karar}")


def _sure_kural_katalogu(yol=None):
    """oa-sure `sure_kurallari.json` kural ANAHTARLARI (kurallar + aşama
    kuralları) — kural adlarının TEK kaynağı. Okunamazsa None (denetim
    atlanır, hüküm verilmez)."""
    yol = yol or os.path.join(SURE_SCRIPTLERI, "sure_kurallari.json")
    try:
        with open(yol, encoding="utf-8") as f:
            veri = json.load(f)
    except (OSError, ValueError):
        return None
    anahtarlar = set()
    for bolum in ("kurallar", "asama_kurallari"):
        if isinstance(veri, dict) and isinstance(veri.get(bolum), dict):
            anahtarlar |= set(veri[bolum])
    return anahtarlar or None


def _bb_sure_denetle(etiket, bid, yol, sure, bulgular, bosluklar):
    """Süre bağı: HESAP oa-sure'nindir; burada yalnız dolu/tutarlı mı ve
    başlangıç belgeli mi bakılır (G4/G9 ile aynı ihtiyat). v0.5.18: kural
    adı oa-sure kataloğunda yoksa GÖRÜNÜR bulgu (adın tek kaynağı oa-sure)."""
    if not isinstance(sure, dict):
        bosluklar.append(f"[{etiket}] {bid}: 'sure' bloğu yok — başvuru süresi oa-sure ile "
                         f"hesaplanmamış (son gün yazılmadan başvuru planlanamaz).")
        return
    kural = str(sure.get("kural") or "").strip().lower()
    onekler = ("aym",) if yol == "aym" else ("aihm", "aihs")
    if not kural:
        bosluklar.append(f"[{etiket}] {bid}: sure.kural BOŞ — son gün hangi kurala dayanıyor? "
                         f"(oa-sure kural adı)")
    elif not kural.startswith(onekler):
        bosluklar.append(f"[{etiket}] {bid}: sure.kural '{kural}' ile başvuru yolu '{yol}' "
                         f"birbirini yalanlıyor — kural adı '{yol}' önekiyle başlamalı "
                         f"(script nitelendirme yapmaz; oa-sure ile düzelt).")
    else:
        katalog = _sure_kural_katalogu()
        if katalog is not None and kural not in katalog:
            adaylar = ", ".join(sorted(k for k in katalog if k.startswith(onekler))) or "—"
            bulgular.append(f"  [{etiket}] {bid}: sure.kural '{kural}' oa-sure kataloğunda "
                            f"yok (sure_kurallari.json) — son gün hangi kurala dayanıyor? "
                            f"Kural adını oa-sure'den al (katalogdaki '{yol}' kuralları: "
                            f"{adaylar}).")
    if not str(sure.get("baslangic_kaniti") or "").strip():
        bosluklar.append(f"[{etiket}] {bid}: sure.baslangic_kaniti BOŞ — tüketme/öğrenme/"
                         f"tebliğ tarihi belgelenmeden kesin son gün yazılamaz.")
    son = sure.get("son_gun")
    if not son:
        bosluklar.append(f"[{etiket}] {bid}: sure.son_gun YOK — oa-sure ile hesapla "
                         f"(hesap bu scriptin işi değildir).")
        return
    try:
        son_d = _d(son)
    except (TypeError, ValueError):
        bosluklar.append(f"[{etiket}] {bid}: sure.son_gun ISO tarih değil ({son!r}).")
        return
    bas = sure.get("basvuru_tarihi")
    if bas:
        try:
            fark = (_d(bas) - son_d).days
        except (TypeError, ValueError):
            bosluklar.append(f"[{etiket}] {bid}: sure.basvuru_tarihi ISO tarih değil ({bas!r}).")
            return
        if fark > 0:
            mazeret = ("6216 m.47/5: mazeretin kalktığı tarihten 15 gün + belge — "
                       "AVUKAT KARARI" if yol == "aym" else "AVUKAT KARARI")
            bulgular.append(f"  [{etiket}] {bid}: başvuru {bas} > son gün {son} → "
                            f"SÜRE GEÇMİŞ (+{fark} gün) — {mazeret}.")
            karar = sure.get("avukat_karari")
            if karar not in AVUKAT_KARARLARI:
                bosluklar.append(
                    f"[{etiket}] {bid}: SÜRE GEÇMİŞ ama sure.avukat_karari "
                    f"({'|'.join(AVUKAT_KARARLARI)}) yazılmamış — mazeretle devam mı, "
                    f"vazgeçme mi; karar kayda geçer.")
            elif karar == "devam" and yol == "aym" and \
                    not str(sure.get("mazeret_kaniti") or "").strip():
                bosluklar.append(
                    f"[{etiket}] {bid}: süresi geçmiş başvuruda devam kararı var ama "
                    f"sure.mazeret_kaniti BOŞ — 6216 m.47/5 mazereti BELGELEYEN delillerle "
                    f"birlikte başvuruyu ister (form 59/2-ğ, ek 59/3-ğ).")
            else:
                bulgular.append(f"  [{etiket}] {bid}: süre aşımı — avukat kararı → {karar}")
        else:
            bulgular.append(f"  [{etiket}] {bid}: başvuru {bas} ≤ son gün {son} → SÜRESİNDE.")
    else:
        bulgular.append(f"  [{etiket}] {bid}: son gün {son} (kural {kural or '—'}; hesap "
                        f"oa-sure'nin) — başvuru tarihi henüz yok.")


def _aym_karar_sonrasi(bid, ks, bulgular, bosluklar):
    tur = ks.get("karar_turu")
    if not isinstance(tur, str) or tur not in AYM_KARAR_TURLERI:
        bosluklar.append(f"[G10] {bid}: karar_sonrasi.karar_turu geçersiz ({tur!r}) — "
                         f"{'|'.join(sorted(AYM_KARAR_TURLERI))}.")
        return
    dayanak = str(ks.get("dayanak") or "")
    kaynak = ks.get("ihlal_kaynagi")
    if tur in ("ihlal", "kismi") and kaynak not in AYM_IHLAL_KAYNAKLARI:
        bosluklar.append(
            f"[G10] {bid}: AYM ihlal kararında ihlal_kaynagi belirtilmemiş ({kaynak!r}) — "
            f"mahkeme_karari (6216 m.50/2: yeniden yargılama) | diger (6216 m.50/1: "
            f"ihlalin ve sonuçlarının ortadan kaldırılması); giderim yolu buna göre ayrılır.")
    elif tur in ("ihlal", "kismi") and kaynak == "diger":
        bulgular.append(
            f"  [G10] {bid}: AYM ihlal kararı mahkeme kararı dışı bir işlem/eylemden "
            f"kaynaklanıyor → 6216 m.50/1: ihlalin ve sonuçlarının ortadan kaldırılması "
            f"için hükmedilenlerin takibi (yeniden yargılama bendi aranmaz).")
    if tur in ("ihlal", "kismi") and kaynak == "mahkeme_karari":
        bulgular.append(
            f"  [G10] {bid}: AYM ihlal kararı mahkeme kararından kaynaklanıyor → "
            f"YENİDEN YARGILAMA dayanağı 6216 m.50/2 (dosya ilgili mahkemeye gönderilir; "
            f"hukuki yarar yoksa tazminat ya da genel mahkemede dava yolu).")
        if _AIHM_OZGU_DAYANAK_RE.search(dayanak):
            bosluklar.append(
                f"[G10] {bid}: yeniden yargılama dayanağı '{dayanak}' YANLIŞ — HMK "
                f"m.375/1-i, CMK m.311/1-f ve İYUK m.53/1-ı AİHM kararına özgüdür; AYM "
                f"ihlal kararında dayanak 6216 m.50/2'dir.")
    if tur in ("ihlal_yok", "kabul_edilemezlik", "kismi"):
        if not str(ks.get("aihm_degerlendirmesi") or "").strip():
            bosluklar.append(
                f"[G10] {bid}: AYM kararı ({tur}) 'dosya bitti' DEĞİLDİR — AİHM yolu "
                f"(AİHS m.35/1; süre oa-sure) değerlendirilmemiş (aihm_degerlendirmesi boş). "
                f"Gidilmeyecekse bu da avukat kararı olarak yazılır.")
        else:
            bulgular.append(f"  [G10] {bid}: AİHM değerlendirmesi: {ks['aihm_degerlendirmesi']}")


def _aihm_karar_sonrasi(bid, ks, bulgular, bosluklar):
    tur = ks.get("karar_turu")
    if not isinstance(tur, str) or tur not in AIHM_KARAR_TURLERI:
        bosluklar.append(f"[G11] {bid}: karar_sonrasi.karar_turu geçersiz ({tur!r}) — "
                         f"{'|'.join(sorted(AIHM_KARAR_TURLERI))}.")
        return
    if tur in AIHM_YY_ACAN:
        kol = str(ks.get("inis_kolu") or "").strip().lower()
        if kol not in AIHM_YENIDEN_YARGILAMA:
            bosluklar.append(
                f"[G11] {bid}: yeniden yargılama yolu açık ({tur}) ama inis_kolu belirsiz "
                f"({kol or '—'}) — hmk|cmk|iyuk (süre rejimi kola göre AYRIDIR).")
        else:
            dayanak, sure_metni = AIHM_YENIDEN_YARGILAMA[kol]
            bulgular.append(f"  [G11] {bid}: yeniden yargılama — {dayanak}: {sure_metni} "
                            f"(hesap oa-sure'nin).")
            if not (str(ks.get("sure_kurali") or "").strip() and ks.get("son_gun")):
                bosluklar.append(
                    f"[G11] {bid}: yeniden yargılama süresi hesaplanmamış (sure_kurali/"
                    f"son_gun boş) — {sure_metni}; oa-sure ile hesapla.")
    else:
        bulgular.append(f"  [G11] {bid}: karar türü '{tur}' — yeniden yargılama bendi "
                        f"aranmaz (bent: ihlal tespiti ya da dostane çözüm/tek taraflı "
                        f"deklarasyonla düşme).")
    at = ks.get("adil_tazmin")
    if at is not None:
        bulgular.append(f"  [G11] {bid}: adil tazmin (AİHS m.41): {at}")


def _bb_denetle(bb, bulgular, bosluklar):
    """[G10] AYM / [G11] AİHM — tek bir başvuru yolu kaydı."""
    bid = bb.get("id", "?")
    yol = str(bb.get("yol") or "").strip().lower()
    if yol not in ("aym", "aihm"):
        bosluklar.append(f"[G10/G11] {bid}: 'yol' aym|aihm olmalı ({yol or '—'}).")
        return
    etiket = "G10" if yol == "aym" else "G11"
    kriterler = bb.get("kriterler")
    if not isinstance(kriterler, dict):
        if kriterler is not None:
            bosluklar.append(f"[{etiket}] {bid}: 'kriterler' sözlük olmalı "
                             f"({type(kriterler).__name__}) — ölçütler okunamadı.")
        kriterler = {}
    tablo = AYM_KRITERLER if yol == "aym" else AIHM_KRITERLER
    for anahtar, olcut, dayanak, uyg in tablo:
        _kriter_denetle(etiket, bid, anahtar, olcut, dayanak, uyg, kriterler.get(anahtar),
                        bulgular, bosluklar)
    if yol == "aym":
        form = bb.get("form")
        if not isinstance(form, dict):
            if form is not None:
                bosluklar.append(f"[G10] {bid}: 'form' sözlük olmalı "
                                 f"({type(form).__name__}) — form kalemleri okunamadı.")
            form = {}
        yol_yok = bb.get("basvuru_yolu_ongorulmemis") is True
        adli_yardim = form.get("59/3-h") == "tamam"
        for anahtar, olcut, uyg in AYM_FORM:
            durum = form.get(anahtar)
            if uyg == "adli_yardim":
                uyg, kosul = adli_yardim, ("yalnız adli yardım talebinde (59/3-h 'tamam'); "
                                           "sunulamayan belgenin gerekçesi forma eklenir "
                                           "(İçtüzük m.59/4)")
            elif uyg == "yol_yok":
                uyg, kosul = yol_yok, ("yalnız başvuru yolu öngörülmemişse "
                                       "('basvuru_yolu_ongorulmemis': true — 6216 m.47/3, 47/5)")
            else:
                kosul = None
            if durum not in DURUM_ENUM:
                bosluklar.append(f"[G10] {bid}: form '{anahtar}' değerlendirilmemiş — "
                                 f"{olcut} (AYM İçtüzüğü m.{anahtar}).")
            elif durum == "eksik":
                bosluklar.append(f"[G10] {bid}: form '{anahtar}' EKSİK — {olcut}.")
            elif durum == "uygulanmaz" and not uyg:
                bosluklar.append(f"[G10] {bid}: form '{anahtar}' 'uygulanmaz' OLAMAZ — "
                                 f"{olcut}" + (f" ({kosul})" if kosul else "") + ".")
            elif durum in ("supheli", "karsilanmiyor"):
                ek = (" Sunulamıyorsa gerekçesi ve varsa bilgi/belgesi forma eklenir "
                      "(İçtüzük m.59/4)." if anahtar.startswith("59/3") else "")
                bulgular.append(f"  [G10] {bid}: form '{anahtar}' {durum.upper()} — {olcut} "
                                f"→ eksiklik bildirimi riski (6216 m.47/6; İçtüzük m.66: en "
                                f"çok 15 günlük kesin süre).{ek}")
    sure = bb.get("sure")
    if yol == "aihm":
        nk = (sure or {}).get("nihai_karar_tarihi") if isinstance(sure, dict) else None
        if not nk:
            bosluklar.append(f"[G11] {bid}: sure.nihai_karar_tarihi YOK — AİHS m.35/1 "
                             f"rejimi (4/6 ay) belirlenemez.")
        else:
            try:
                rejim = "6 ay (eski rejim)" if _d(nk) < AIHM_4AY_GECIS else "4 ay"
                bulgular.append(f"  [G11] {bid}: nihai karar {nk} → AİHS m.35/1 süre "
                                f"rejimi {rejim} (Orhan/Türkiye (k.k.) § 44); süre "
                                f"tebliğden işler — hesap oa-sure'nin.")
            except (TypeError, ValueError):
                bosluklar.append(f"[G11] {bid}: sure.nihai_karar_tarihi ISO tarih değil "
                                 f"({nk!r}).")
    _bb_sure_denetle(etiket, bid, yol, sure, bulgular, bosluklar)
    ks = bb.get("karar_sonrasi")
    if ks is not None and not isinstance(ks, dict):
        bosluklar.append(f"[{etiket}] {bid}: 'karar_sonrasi' sözlük olmalı "
                         f"({type(ks).__name__}) — karar sonrası okunamadı.")
    elif isinstance(ks, dict) and ks:
        (_aym_karar_sonrasi if yol == "aym" else _aihm_karar_sonrasi)(
            bid, ks, bulgular, bosluklar)


ORNEK_BB = {
  "dosya": "Örnek 2026/000 (kurgu)",
  "islemler": [],
  "bireysel_basvuru": [
    {"id": "BB1", "yol": "aym",
     "kriterler": {
       "konu_bakimindan": {"durum": "tamam", "kanit": "adil yargılanma hakkı (AY m.36) — AİHS m.6 ortak alanı"},
       "kisi_bakimindan": {"durum": "tamam", "kanit": "başvurucu davanın tarafı; kişisel ve doğrudan etkilenme"},
       "zaman_bakimindan": {"durum": "tamam", "kanit": "nihai karar 2026'da kesinleşti"},
       "yollarin_tuketilmesi": {"durum": "tamam", "kanit": "istinaf + temyiz tüketildi; şikâyet temyiz dilekçesinde ileri sürüldü"},
       "anayasal_onem_onemli_zarar": {"durum": "tamam", "kanit": "mahkûmiyet hükmü — başvurucu yönünden önemli zarar"},
       "acik_dayanaktan_yoksunluk": {"durum": "supheli", "kanit": "",
                                     "not": "delil takdiri itirazı ağır basıyor — usul güvencesi diline çevrilmeli (dördüncü derece riski)"},
       "kotuye_kullanmama": {"durum": "tamam", "kanit": "olaylar belgeye dayalı, dil ölçülü (taslak gözden geçirildi)"}},
     "form": {"59/2-a": "tamam", "59/2-b": "uygulanmaz", "59/2-c": "tamam", "59/2-ç": "tamam",
              "59/2-d": "tamam", "59/2-e": "tamam", "59/2-f": "tamam", "59/2-g": "tamam",
              "59/2-ğ": "uygulanmaz", "59/2-h": "tamam", "59/2-ı": "uygulanmaz",
              "59/2-i": "uygulanmaz", "59/2-j": "tamam", "59/2-k": "tamam", "59/2-l": "uygulanmaz",
              "59/3-a": "tamam", "59/3-b": "tamam", "59/3-c": "uygulanmaz", "59/3-ç": "uygulanmaz",
              "59/3-d": "tamam", "59/3-e": "tamam", "59/3-f": "uygulanmaz", "59/3-g": "tamam",
              "59/3-ğ": "uygulanmaz", "59/3-h": "uygulanmaz", "60/2": "uygulanmaz"},
     "sure": {"kural": "aym_bireysel", "baslangic": "2026-09-01",
              "baslangic_kaniti": "nihai kararın vekile UYAP tebliğ kaydı (kurgu)",
              "son_gun": "2026-10-01"}},
    {"id": "BB2", "yol": "aihm",
     "kriterler": {
       "magdur_sifati": {"durum": "tamam", "kanit": "başvurucu ihlalden kişisel olarak etkilendi"},
       "yollarin_tuketilmesi": {"durum": "tamam", "kanit": "AYM bireysel başvurusu yapıldı; şikâyetin özü orada ileri sürüldü"},
       "konu_bakimindan_bagdasma": {"durum": "tamam", "kanit": "AİHS m.6 kapsamı"},
       "acik_dayanaktan_yoksunluk": {"durum": "tamam", "kanit": "usul güvencesi ihlali — delil takdiri değil"},
       "onemli_zarar": {"durum": "tamam", "kanit": "hapis cezası; zarar önemli"},
       "ayni_konu_baska_merci": {"durum": "tamam", "kanit": "başka uluslararası merciye başvuru yok (müvekkil beyanı + dosya)"},
       "kotuye_kullanmama": {"durum": "tamam", "kanit": "olaylar belgeye dayalı, AYM kararı eksiksiz eklendi"},
       "eksiksiz_basvuru": {"durum": "supheli", "kanit": "", "not": "resmî formun güncel sürümü ve ek listesi avukatça teyit edilecek (İçtüzük m.47 TEYİT BEKLİYOR)"}},
     "sure": {"kural": "aihm_basvuru", "nihai_karar_tarihi": "2026-08-20", "baslangic": "2026-09-01",
              "baslangic_kaniti": "AYM kararının vekile tebliği (kurgu)", "son_gun": "2027-01-01"},
     "karar_sonrasi": {"karar_turu": "ihlal", "inis_kolu": "cmk",
                       "sure_kurali": "<oa-sure kural adı — CMK m.311/1-f>",
                       "son_gun": "2028-01-01", "adil_tazmin": "talep edildi"}}
  ]
}

def denetle(v):
    bulgular, bosluklar = [], []
    ust_kol = v.get("yargi_kolu")
    for i in v.get("islemler", []):
        kim = i.get("taraf"); iid = i.get("id", "?")
        if kim == "kamu":
            _kamu_denetle(i, iid, bulgular, bosluklar); continue
        son, fiili = _d(i.get("son_gun")), _d(i.get("fiili_tarih"))
        # G1 — süre denetimi tamam mı
        if i.get("teblig") and not son:
            bosluklar.append(f"[G1] {iid}: tebliğ var ama son_gun yok — oa-sure ile hesapla.")
            continue
        if son and fiili is None and kim == "karsi":
            bulgular.append(f"{iid} ({kim}): işlem HİÇ yapılmamış görünüyor — son gün {son}: "
                            f"dolduysa kaçırma; teyit et.")
        durum = None
        if son and fiili:
            fark = (fiili - son).days
            durum = "SÜRESİNDE" if fark <= 0 else f"KAÇIRILMIŞ (+{fark} gün)"
            bulgular.append(f"{iid} ({kim}) {i.get('islem')}: son gün {son} / fiilî {fiili} → {durum}")
        # G4 — kesin dil kilidi
        if i.get("kesin_dil") and not i.get("teblig_belgeli"):
            bosluklar.append(f"[G4] {iid}: tebliğ BELGESİZ iken kesin_dil=true — yasak; "
                             f"'teyidi kaydıyla' formülüne dön.")
        # G9 — kesin dilin süre DAYANAĞI: alanlar dolu mu ve tutarlı mı (B-9)
        _g9_denetle(i, iid, ust_kol, bulgular, bosluklar)
        # [Z] — tamamlanabilir kusur × zamanlama (advisory; süre durumundan
        # bağımsız: vekâletname/harç eksiği süresinde de "kusur"dur)
        _zamanlama_denetle(i, iid, kim, bulgular)
        if durum and durum.startswith("KAÇIRILMIŞ"):
            if kim == "karsi":
                # G2 — sonuç + kapı kapatma
                if not i.get("sonuc_norm"):
                    bosluklar.append(f"[G2a] {iid}: karşı kaçırma usuli SONUCA bağlanmamış (sonuc_norm yok).")
                if not i.get("sonuc_ictihat_teyit"):
                    bosluklar.append(f"[G2a] {iid}: sonucun içtihat teyidi yok (oa-ictihat).")
                kk = i.get("kapi_kapatma") or []
                if not kk:
                    bosluklar.append(f"[G2b] {iid}: karşı tarafın kurtuluş KAPILARI KAPATILMAMIŞ "
                                     f"(en az K-1 eski hâle getirme + K-2 usulsüz tebliğ öngörülmeli).")
                else:
                    bulgular.append(f"  {iid}: kapatılan kapılar → " + "; ".join(k['kapi'] for k in kk))
            elif kim == "biz":
                # G3 — üç kanallı kapı araştırması
                ka = i.get("kapi_arastirmasi") or {}
                for kanal in ("ictihat", "doktrin", "web"):
                    if not ka.get(kanal):
                        bosluklar.append(f"[G3] {iid}: müvekkil hatasında '{kanal}' kanalı araştırılmamış.")
                kapilar = ka.get("kapilar") or []
                if not kapilar:
                    bosluklar.append(f"[G3] {iid}: hiç kapı kaydı yok — kapı bulunamadıysa "
                                     f"uygulanabilirlik='YOK' kaydıyla açıkça yazılır (sahte umut da, sessizlik de yasak).")
                for k in kapilar:
                    if not k.get("norm_teyit"):
                        bosluklar.append(f"[G3] {iid}/{k.get('kapi')}: norm Mevzuat MCP teyidi yok.")
                    if not k.get("kapi_suresi_hesaplandi"):
                        bosluklar.append(f"[G5] {iid}/{k.get('kapi')}: kapının KENDİ süresi hesaplanmamış (oa-sure).")
                    if not k.get("uygulanabilirlik"):
                        bosluklar.append(f"[G3] {iid}/{k.get('kapi')}: dürüst uygulanabilirlik değerlendirmesi yok.")
    # [G10]/[G11] (v0.5.18) — bireysel başvuru yolu kontrol listesi. Alan yoksa
    # (eski artefakt) hiçbir satır basılmaz; exit sözleşmesi aynen korunur.
    bbler = v.get("bireysel_basvuru")
    if bbler is not None and not isinstance(bbler, list):
        bosluklar.append("[G10/G11] 'bireysel_basvuru' liste olmalı "
                         f"({type(bbler).__name__}) — başvuru yolu kayıtları okunamadı.")
        bbler = []
    for sira, bb in enumerate(bbler or [], start=1):
        if isinstance(bb, dict):
            _bb_denetle(bb, bulgular, bosluklar)
        else:
            bosluklar.append(f"[G10/G11] bireysel_basvuru #{sira} sözlük değil "
                             f"({type(bb).__name__}) — kayıt okunamadı.")
    return bulgular, bosluklar

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--girdi"); p.add_argument("--ornek", action="store_true")
    p.add_argument("--ornek-bb", action="store_true",
                   help="v0.5.18: AYM/AİHM bireysel başvuru yolu ([G10]/[G11]) girdi "
                        "şablonu (kurgu veri; şema references/bireysel-basvuru-yolu.md)")
    p.add_argument("--json", dest="json_yol", metavar="YOL",
                   help="denetim sonucunu makine-okur JSON olarak bu yola yaz "
                        "(opsiyonel; graf/vakia/kiyas motorlarıyla simetri — "
                        "YOL-HARITASI P2 '--json' maddesinin oa-usul ayağı)")
    a = p.parse_args()
    if a.ornek:
        print(json.dumps(ORNEK, ensure_ascii=False, indent=2)); return
    if a.ornek_bb:
        print(json.dumps(ORNEK_BB, ensure_ascii=False, indent=2)); return
    if not a.girdi:
        p.error("--girdi dosya.json (şablon için --ornek)")
    v = json.load(open(a.girdi, encoding="utf-8"))
    bulgular, bosluklar = denetle(v)
    print("=" * 70)
    print(f"  oa-usul EKSİKSİZLİK DENETİMİ — {v.get('dosya','?')}  (karar materyali)")
    print("=" * 70)
    for b in bulgular: print("  " + b)
    print("-" * 70)
    if a.json_yol:
        # exit'ten ÖNCE yazılır: boşluklu denetimin sonucu da makine-okur kalmalı
        # (DURUM.md advisory bekçisi boşlukları ancak buradan görebilir).
        sonuc = {"arac": "usul_matris", "girdi": a.girdi,
                 "dosya": v.get("dosya"), "bulgular": bulgular,
                 "bosluklar": bosluklar, "saglikli": not bosluklar}
        with open(a.json_yol, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"[JSON] Makine-okur sonuc yazildi: {a.json_yol}")
    if bosluklar:
        print("  BOŞLUKLAR — kapatılmadan analiz TESLİM EDİLEMEZ:")
        for b in bosluklar: print("  ! " + b)
        sys.exit(1)
    print("  ✓ Boşluk yok: süre denetimi, sonuç bağlama, kapı kapatma/araştırma ve")
    print("    kesin-dil kilidi tamam. Nihai hukuki değerlendirme avukatındır.")

if __name__ == "__main__":
    main()

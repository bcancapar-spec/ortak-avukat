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
Boşluk varsa adıyla raporlar ve exit(1) — boşluklu usul analizi teslim edilemez.

Süre HESABI bu scriptin işi değildir → oa-sure/hesapla_sure.py (son_gun oradan gelir).
[G9] de süre HESAPLAMAZ ve HUKUKİ NİTELENDİRME YAPMAZ (hangi kuralın uygulanacağına
karar vermez): yalnız alanların DOLU ve BİRBİRİYLE TUTARLI olduğuna bakar. Tanınmayan
kural öneki / yargı kolu değeri "bilinmiyor" sayılır ve boşluk üretmez.

Kullanım:
  python usul_matris.py --ornek > dosya_usul.json     # girdi şablonu
  python usul_matris.py --girdi dosya_usul.json       # denetim raporu
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, json, sys
from datetime import date

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
     "kesin_dil": True},
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
# Bu tablo HUKUKİ NİTELENDİRME DEĞİLDİR: `oa-sure/scripts/sure_kurallari.json`
# anahtarlarının ÖNEK KONVANSİYONUDUR (hmk_*, iik_*, cmk_*, iyuk_*, amme_*,
# aym_*). Script hangi kuralın uygulanacağına karar vermez; yalnız "kural adı
# ile beyan edilen yargı kolu birbirini yalanlıyor mu" sorusunu sorar.
# Önek tabloda YOKSA hüküm verilmez ("bilinmiyor") — eski/özel kanun kuralları
# kapıda düşmez (CLAUDE.md: eski dosyada alan yoksa script çökmez, "bilinmiyor" der).
KURAL_ONEK_KOL = {
    "hmk": {"hukuk"},
    "iik": {"hukuk"},
    "cmk": {"ceza"},
    "iyuk": {"idari"},
    "amme": {"idari"},
    "aym": None,   # AYM bireysel başvuru bir yargı KOLU değildir → kol-bağımsız
}
# Yargı kolu için kabul edilen yazımlar (eş anlamlı normalizasyon; kapalı küme).
KOL_ESANLAM = {"hukuk": "hukuk", "adli": "hukuk", "ozel": "hukuk",
               "ceza": "ceza",
               "idari": "idari", "idare": "idari", "vergi": "idari"}


def _kol_normalize(ham):
    """(normalize|None, ham) — kapalı küme dışı değer NİTELENDİRİLMEZ."""
    h = str(ham or "").strip().lower()
    return KOL_ESANLAM.get(h), h


def _kural_kolu(kural):
    """(izinli_kol_kumesi|None, onek) — önek tanınmıyorsa (None, onek)."""
    k = str(kural or "").strip().lower()
    onek = k.split("_", 1)[0] if k else ""
    if onek in KURAL_ONEK_KOL:
        return KURAL_ONEK_KOL[onek], onek
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
        if onek not in KURAL_ONEK_KOL:
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
    return bulgular, bosluklar

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--girdi"); p.add_argument("--ornek", action="store_true")
    p.add_argument("--json", dest="json_yol", metavar="YOL",
                   help="denetim sonucunu makine-okur JSON olarak bu yola yaz "
                        "(opsiyonel; graf/vakia/kiyas motorlarıyla simetri — "
                        "YOL-HARITASI P2 '--json' maddesinin oa-usul ayağı)")
    a = p.parse_args()
    if a.ornek:
        print(json.dumps(ORNEK, ensure_ascii=False, indent=2)); return
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

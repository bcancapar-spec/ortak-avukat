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
Boşluk varsa adıyla raporlar ve exit(1) — boşluklu usul analizi teslim edilemez.

Süre HESABI bu scriptin işi değildir → oa-sure/hesapla_sure.py (son_gun oradan gelir).

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
    if bosluklar:
        print("  BOŞLUKLAR — kapatılmadan analiz TESLİM EDİLEMEZ:")
        for b in bosluklar: print("  ! " + b)
        sys.exit(1)
    print("  ✓ Boşluk yok: süre denetimi, sonuç bağlama, kapı kapatma/araştırma ve")
    print("    kesin-dil kilidi tamam. Nihai hukuki değerlendirme avukatındır.")

if __name__ == "__main__":
    main()

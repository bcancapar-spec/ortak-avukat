#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
hesapla_sure.py — Türk usul hukuku için DETERMİNİSTİK süre hesaplayıcı (v2).

Felsefe (Ortak Avukat anayasası): Script yalnızca DATE ARİTMETİĞİNİ deterministik
yapar. Hukuki KURALI (sürenin kaç gün/hafta olduğunu) kullanıcı/Claude resmî
kaynaktan (Mevzuat MCP) teyit edip GİRER.

Deterministik: tebliğ+1, gün/hafta ekleme, hafta sonu, resmî tatiller
(scripts/tatiller.json — güncellenebilir), adli tatil/çalışmaya ara
(HMK m.102/104 ve İYUK m.61/m.8-3).
İŞARETLENEN (deterministik DEĞİL): tabloda tanımsız dini bayramlar, özel kanun
süreleri (7036/CMK vb.), parasal kesinlik. Çıktı bunları "ELLE TEYİT" uyarır.

v2: (1) Tatiller scripts/tatiller.json'dan okunur — yıllık güncellenebilir.
(2) İdari yargı çalışmaya ara mekaniği ayrı işlenir: süre araya rastlarsa, ara
bitişini (31 Ağu) İZLEYEN tarihten (1 Eylül) İTİBAREN 7 GÜN (1 Eylül dahil) → 7
Eylül (İYUK m.8/3; Danıştay'ın yerleşik uygulaması ve scriptin kendi gün-sayma
konvansiyonu — başlangıç günü 1. gün sayılır). Matematik olarak 31 Ağu + 7 gün
ile AYNI sonucu verir; HMK m.104 (hukuk: 31 Ağu + 1 hafta) ile de örtüşür.

Kullanım:
  python hesapla_sure.py --teblig 2026-05-20 --kural hmk_istinaf
  python hesapla_sure.py --teblig 2026-07-15 --kural iyuk_istinaf --yargi idari
  python hesapla_sure.py --teblig 2026-05-20 --sure 2 --birim hafta
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, json, os, sys
from datetime import date, timedelta

ARA_BASLANGIC = (7, 20)   # HMK m.102 / İYUK m.61: 20 Temmuz
ARA_BITIS = (8, 31)       # 31 Ağustos

# GÖMÜLÜ (fallback) kural tablosu — sure_kurallari.json yoksa/bozuksa devreye girer.
# Süreler HUKUKİ kuraldır; resmî kaynaktan (Mevzuat MCP) teyit edilmelidir.
_GOMULU_KURALLAR = {
    "hmk_istinaf":     (2, "hafta", "HMK m.345 — istinaf, ilamın tebliğinden"),
    "hmk_temyiz":      (2, "hafta", "HMK m.361 — temyiz, BAM kararının tebliğinden"),
    "hmk_cevap":       (2, "hafta", "HMK m.127 — cevap (kural; uzatma ayrı)"),
    "iik_istinaf":     (2, "hafta", "İİK m.363 — icra mah. istinaf (ESKİ 10 GÜN DEĞİL)"),
    "iik_sikayet":     (7, "gun", "İİK m.16 — icra mah. şikâyet; kural 7 gün (süresiz haller ayrık)"),
    "cmk_itiraz":      (7, "gun", "CMK m.268 — itiraz; karar tebliğ/öğrenilmesinden 7 gün"),
    "cmk_istinaf":     (2, "hafta", "CMK m.273 — istinaf; DİKKAT '7 GÜN' olabilir — TEYİT ET"),
    "cmk_temyiz":      (2, "hafta", "CMK m.291 — temyiz; DİKKAT '15 GÜN' olabilir — TEYİT ET"),
    "iyuk_dava_idare": (60, "gun", "İYUK m.7 — idare mah./Danıştay dava açma"),
    "iyuk_dava_vergi": (30, "gun", "İYUK m.7 — vergi mah. dava açma"),
    "iyuk_istinaf":    (30, "gun", "İYUK m.45 — BİM istinaf"),
    "iyuk_temyiz":     (30, "gun", "İYUK m.46 — Danıştay temyiz"),
    "amme_6183_m58":   (15, "gun", "6183 m.58 — ödeme emrine karşı dava; 15 gün (7061 s.K. — TEYİT ET)"),
    "aym_bireysel":    (30, "gun", "6216 m.47/5 — AYM bireysel başvuru"),
}

def kurallari_yukle():
    """sure_kurallari.json varsa oradan (kural, teyit) oku; yoksa/bozuksa gömülüye düş."""
    yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sure_kurallari.json")
    try:
        with open(yol, encoding="utf-8") as f:
            data = json.load(f)
        kurallar, teyit = {}, {}
        for k, v in data.get("kurallar", {}).items():
            kurallar[k] = (v["miktar"], v["birim"], v.get("kaynak", ""))
            teyit[k] = v.get("mcp_teyit_tarihi", "") or ""
        if kurallar:
            return kurallar, teyit, False
    except Exception:
        pass
    return dict(_GOMULU_KURALLAR), {k: "" for k in _GOMULU_KURALLAR}, True

KURALLAR, KURAL_TEYIT, _KURAL_TABLO_YOK = kurallari_yukle()
_GUNLER = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
def _gun_adi(g): return _GUNLER[g.weekday()]

def _ay_ekle(d, ay):
    """Tarihe ay ekler; hedef ayda gün yoksa ayın son gününe sabitler (TBK m.92 mantığı)."""
    y = d.year + (d.month - 1 + ay) // 12
    m = (d.month - 1 + ay) % 12 + 1
    # ayın son günü
    if m == 12:
        son_gun = 31
    else:
        son_gun = (date(y, m+1, 1) - timedelta(days=1)).day
    return date(y, m, min(d.day, son_gun))

def tatilleri_yukle():
    yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tatiller.json")
    try:
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"sabit":[{"ay":1,"gun":1,"ad":"Yılbaşı"},{"ay":4,"gun":23,"ad":"23 Nisan"},
            {"ay":5,"gun":1,"ad":"1 Mayıs"},{"ay":5,"gun":19,"ad":"19 Mayıs"},
            {"ay":7,"gun":15,"ad":"15 Temmuz"},{"ay":8,"gun":30,"ad":"30 Ağustos"},
            {"ay":10,"gun":29,"ad":"29 Ekim"}],"dini":{},"_tablo_yok":True}

TATILLER = tatilleri_yukle()
SABIT = {(t["ay"],t["gun"]): t["ad"] for t in TATILLER.get("sabit",[])}
DINI = {y: set(g for g in gs if isinstance(g,str) and g[:4].isdigit())
        for y,gs in TATILLER.get("dini",{}).items() if y.isdigit()}
# İDARİ İZİN — CB tasarrufu (Cumhurbaşkanlığı Kararnamesi / CB Kararı / CB Genelgesi):
# hangi formda ilan edilirse edilsin 2429 anlamında resmî tatil DEĞİLDİR.
# Süreyi UZATMAZ, süreden sayılır → yalnızca UYARI üretir, son günü asla kaydırmaz.
IDARI = {y: set(g for g in gs if isinstance(g,str) and g[:4].isdigit())
         for y,gs in TATILLER.get("idari_izin",{}).items() if y.isdigit()}
def idari_izin_mi(g): return g.isoformat() in IDARI.get(str(g.year),set())
def idari_tanimli_mi(y): return str(y) in IDARI and len(IDARI[str(y)])>0
def dini_yakin_mi(g, esik=4):
    return any(abs((date.fromisoformat(d)-g).days) <= esik for d in DINI.get(str(g.year), set()))

# ── ARİTMETİK HİCRİ TAKVİM (tabular/civil — gelecek yıllar için TAHMİN) ─────
# Diyanet'in rüyet-esaslı resmî takviminden ±1-2 gün SAPABİLİR. Bu hesap yalnızca
# UYARI üretmek ve hangi tarihlerin teyit edileceğini göstermek içindir; tahmine
# dayanarak son gün ASLA kaydırılmaz/kaydırılmamazlık edilmez — teyit + tablo şarttır.
def _g2jdn(y, m, d):
    a = (14 - m) // 12; yy = y + 4800 - a; mm = m + 12 * a - 3
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045
def _jdn2g(j):
    a = j + 32044; b = (4 * a + 3) // 146097; c = a - 146097 * b // 4
    dd = (4 * c + 3) // 1461; e = c - 1461 * dd // 4; mm = (5 * e + 2) // 153
    gun = e - (153 * mm + 2) // 5 + 1; ay = mm + 3 - 12 * (mm // 10)
    return date(100 * b + dd - 4800 + mm // 10, ay, gun)
def _hicri2jdn(hy, hm, hd):
    onceki = ((hm - 1) // 2) * 59 + ((hm - 1) % 2) * 30
    return hd + onceki + (hy - 1) * 354 + (3 + 11 * hy) // 30 + 1948439
def tahmini_bayramlar(gy):
    """Verilen miladi yıl için TAHMİNİ bayram günleri: {ad: [date, ...]}."""
    sonuc = {}
    hy0 = int((gy - 622) * 33 / 32)
    for hy in range(hy0 - 1, hy0 + 3):
        for ad, hm, hd0, n in (("Ramazan Bayramı", 10, 1, 3), ("Kurban Bayramı", 12, 10, 4)):
            gunler = [_jdn2g(_hicri2jdn(hy, hm, hd0) + i) for i in range(n)]
            gunler = [g for g in gunler if g.year == gy]
            if gunler:
                sonuc.setdefault(f"{ad} ~{hy}H (TAHMİNİ ±1-2 gün)", []).extend(gunler)
    return sonuc

def resmi_tatil_mi(g):
    if (g.month,g.day) in SABIT: return SABIT[(g.month,g.day)]
    if g.isoformat() in DINI.get(str(g.year),set()): return "Dini bayram (tabloda tanımlı)"
    return None
def hafta_sonu_mu(g): return g.weekday()>=5
def is_gunu_mu(g): return not hafta_sonu_mu(g) and resmi_tatil_mi(g) is None
def sonraki_is_gunu(g):
    while not is_gunu_mu(g): g += timedelta(days=1)
    return g
def aralik_icinde_mi(g):
    return date(g.year,*ARA_BASLANGIC) <= g <= date(g.year,*ARA_BITIS)
def dini_tanimli_mi(y): return str(y) in DINI and len(DINI[str(y)])>0

def hesapla(teblig, miktar, birim, yargi, tur="usul", adli_tatil_istisna=False):
    rapor, uyarilar = [], []
    bas = teblig + timedelta(days=1)
    rapor.append(f"Tebliğ/öğrenme tarihi : {teblig.isoformat()} ({_gun_adi(teblig)})")
    rapor.append(f"Süre başlangıcı       : {bas.isoformat()} (tebliğ günü sayılmaz)")
    if birim=="hafta":
        ham = teblig + timedelta(weeks=miktar); rapor.append(f"Süre                  : {miktar} hafta")
    elif birim=="gun":
        ham = teblig + timedelta(days=miktar); rapor.append(f"Süre                  : {miktar} gün")
    elif birim=="ay":
        ham = _ay_ekle(teblig, miktar); rapor.append(f"Süre                  : {miktar} ay (TBK m.92 tarzı: sayılı güne denk gelen gün)")
    elif birim=="yil":
        ham = _ay_ekle(teblig, miktar*12); rapor.append(f"Süre                  : {miktar} yıl")
    else:
        raise ValueError("birim 'gun', 'hafta', 'ay' veya 'yil' olmalı")
    rapor.append(f"Ham bitiş             : {ham.isoformat()} ({_gun_adi(ham)})")
    son = ham
    # Adli tatil/çalışmaya ara YALNIZCA USUL sürelerine uygulanır.
    # Maddi hukuk süreleri (zamanaşımı, hak düşürücü) usul süresi DEĞİLDİR → uzamaz.
    if tur=="usul" and aralik_icinde_mi(son) and not adli_tatil_istisna:
        if yargi=="hukuk":
            son = date(son.year,*ARA_BITIS) + timedelta(weeks=1)
            rapor.append(f"Adli tatil (HMK m.104): ham bitiş 20 Tem–31 Ağu arasında; 31 Ağu + 1 hafta → {son.isoformat()}")
        else:
            son = date(son.year,*ARA_BITIS) + timedelta(days=7)
            rapor.append(f"Çalışmaya ara (İYUK m.8/3): ham bitiş 20 Tem–31 Ağu arasında; ara bitimini izleyen "
                         f"1 Eylül'den itibaren 7 gün (1 Eylül dahil) → {son.isoformat()}")
    elif tur=="usul" and aralik_icinde_mi(son) and adli_tatil_istisna:
        # HMK m.103'te SAYILAN işler adli tatilde GÖRÜLÜR → süre UZAMAZ. Ham bitiş korunur;
        # yalnız aşağıdaki hafta sonu/resmî tatil kayması (HMK m.93) uygulanır.
        rapor.append(f"HMK m.103 istisna işi — adli tatil uzatması uygulanmadı: ham bitiş {son.isoformat()} "
                     f"({_gun_adi(son)}) 20 Tem–31 Ağu arasında olsa da UZATILMADI "
                     f"(nafaka, ihtiyati tedbir/haciz, delil tespiti, çekişmesiz yargı, iş mahkemesi/iş hukuku "
                     f"uyuşmazlıkları vb. adli tatilde görülür — HMK m.103). Yalnız hafta sonu/tatil kayması yapılır.")
        uyarilar.append("HMK m.103 ADLİ TATİL İSTİSNASI seçildi: Bu işin gerçekten m.103 kapsamında (adli tatilde "
            "görülen iş) olduğunu TEYİT ET — kapsam dışı bir işte istisnayı uygulamak süreyi YANLIŞ KISALTIR ve "
            "hak kaybına yol açar. Tereddütte istisnayı KALDIR (bayraksız hesap güvenli taraftır).")
    elif tur=="maddi" and aralik_icinde_mi(son):
        rapor.append("ⓘ Maddi hukuk süresi (zamanaşımı/hak düşürücü) — adli tatil UZATMASI UYGULANMADI "
                     "(usul süresi değildir). Yalnız son gün tatile rastlarsa kayar (aşağıda).")
    if not is_gunu_mu(son):
        eski = son; son = sonraki_is_gunu(son)
        if hafta_sonu_mu(eski):
            sebep = ("hafta sonu — Pazar 2429 s.K. genel tatil; Cumartesi yerleşik kabul/içtihatla tatil sayılır"
                     if eski.weekday()==5 else "hafta sonu — Pazar (2429 s.K. genel tatil)")
        else:
            sebep = f"resmî tatil ({resmi_tatil_mi(eski)}, 2429 s.K.)"
        rapor.append(f"Tatil günü düzeltmesi : {eski.isoformat()} {sebep} → ilk iş günü {son.isoformat()} (HMK m.93: yalnız SON GÜN tatile rastlarsa uzar; aradaki tatil günleri süreye DAHİLDİR)")
    # ── İDARİ İZİN KATMANI (uyarı — KAYDIRMA YAPILMAZ) ─────────────────────
    # Hukuki kural: idari izin (CB tasarrufu — Kararname/Karar/Genelge) 2429 anlamında resmî tatil
    # değildir; süreyi UZATMAZ, SÜREDEN SAYILIR. Riski görünür kılar, son günü değiştirmez.
    if idari_izin_mi(son):
        rapor.append(f"ⓘ Son gün {son.isoformat()} İDARİ İZİN gününe denk geliyor — son gün KAYDIRILMADI (idari izin süreden sayılır).")
        uyarilar.append("İDARİ İZİN: Son gün, Cumhurbaşkanlığı tasarrufuyla (Kararname/Karar/Genelge) ilan edilmiş idari izin gününe denk. "
            "İdari izin 2429 s.K. anlamında resmî tatil DEĞİLDİR — SÜREYİ UZATMAZ, SÜREDEN SAYILIR. "
            "Kamu birimleri (vergi dairesi, tapu, kalem, vezne) fiilen kapalı/eksik çalışıyor olabilir: "
            "fiziki işlem veya harç/vezne gerektiren adımı ÖNCEDEN tamamla; UYAP elektronik kanalı 23:59'a kadar açıktır. "
            "İşlem o gün fiilen imkânsızlaştıysa eski hâle getirme (HMK m.95 vd.) ayrıca ve ihtiyatla değerlendirilir — buna güvenerek bekleme.")
    elif not idari_tanimli_mi(son.year) and dini_yakin_mi(son):
        uyarilar.append(f"İDARİ İZİN TARAMASI: Son gün bir dini bayrama bitişik ve {son.year} için tabloda idari izin kaydı yok. "
            "O yıl köprü günü idari izni ilan edilmiş olabilir — Mevzuat MCP'den ÜÇ enstrümanı birden "
            "(search_cbk + search_cbbaskankarar + search_cbgenelge, yıl + 'idari izin') tara; ilan edilmişse tatiller.json'a işle. "
            "NOT: idari izin süreyi UZATMAZ; bu tarama yalnızca fiilî erişim riskini görmek içindir.")
    if TATILLER.get("_tablo_yok"):
        uyarilar.append("tatiller.json bulunamadı; yalnızca sabit ulusal tatiller kullanıldı.")
    if not dini_tanimli_mi(son.year) or not dini_tanimli_mi(ham.year):
        yakin = []
        for yy in {son.year, ham.year}:
            if not dini_tanimli_mi(yy):
                for ad, gunler in tahmini_bayramlar(yy).items():
                    for g in gunler:
                        if abs((g - son).days) <= 3 or abs((g - ham).days) <= 3:
                            yakin.append(f"{g.isoformat()} [{ad}]")
        if yakin:
            uyarilar.append("TAHMİNİ DİNİ BAYRAM PENCERESİ: Bu yıl için tabloda resmî dini bayram yok; aritmetik hicri "
                "hesap, son günün şu TAHMİNİ bayram günlerine bitişik/denk olduğunu gösteriyor: "
                + "; ".join(sorted(set(yakin))) +
                ". Tahmin Diyanet'in rüyet-esaslı takviminden ±1-2 gün sapabilir. Kesin tarihleri Diyanet/Resmî Gazete'den "
                "teyit edip tatiller.json'a işle ve YENİDEN HESAPLA — tahmine dayanarak son günü kaydırma/sabitleme kararı VERME.")
        else:
            uyarilar.append(f"DİNİ BAYRAM: {ham.year}/{son.year} için tabloda resmî dini bayram tanımlı değil. "
                "Aritmetik hicri tahmin, son güne ±3 gün içinde bayram GÖSTERMİYOR (tahmin ±1-2 gün sapabilir). "
                "Yıl yaklaşınca Diyanet/RG tarihlerini tatiller.json'a yine de işle; o yılın tüm tahminleri için: --bayram YYYY.")
    if tur=="maddi":
        uyarilar.append("MADDİ HUKUK SÜRESİ: Bu bir zamanaşımı/hak düşürücü süre olabilir. (a) Hangisi olduğunu "
            "ve başlangıç anını (muacceliyet/öğrenme/fiil tarihi) Mevzuat MCP'den teyit et — başlangıç çoğu kez "
            "tebliğ değildir. (b) Zamanaşımı KESİLİR/DURUR (TBK m.153-158), hak düşürücü süre kural olarak durmaz/kesilmez. "
            "(c) Bu durum/kesilme olaylarını script HESAPLAMAZ — elle değerlendir.")
    else:
        uyarilar.append("PARASAL KESİNLİK: Süre işlese de karar parasal sınırın altındaysa kanun yolu KAPALI "
            "olabilir. Sınırı o yıl için Mevzuat MCP'den teyit et.")
    if yargi=="idari" and tur=="usul":
        uyarilar.append("ÖZEL SÜRE: İdari yargıda bazı işlerin (memur disiplin, ihale vb.) özel kanun "
            "süreleri olabilir; uygulanan kuralı teyit et.")
    rapor.append("")
    rapor.append(f">>> HESAPLANAN SON GÜN  : {son.isoformat()} ({_gun_adi(son)}) — mesai bitimi <<<")
    return son, rapor, uyarilar

def main():
    p = argparse.ArgumentParser(description="Deterministik Türk usul/maddi süre hesaplayıcı (v3)")
    p.add_argument("--teblig", help="Başlangıç tarihi: usulde tebliğ/öğrenme; maddi hukukta muacceliyet/öğrenme/fiil (YYYY-MM-DD)")
    p.add_argument("--sure", type=int); p.add_argument("--birim", choices=["gun","hafta","ay","yil"])
    p.add_argument("--kural", choices=list(KURALLAR.keys()))
    p.add_argument("--yargi", choices=["hukuk","idari"], default="hukuk")
    p.add_argument("--tur", choices=["usul","maddi"], default="usul",
                   help="usul = kanun yolu/başvuru süresi (adli tatil uygulanır); "
                        "maddi = zamanaşımı/hak düşürücü (TBK/TMK/TTK/6183 vb. — adli tatil uygulanmaz)")
    p.add_argument("--islem", metavar="YYYY-MM-DD",
                   help="Fiilî işlem/başvuru tarihi (özellikle KARŞI TARAF denetimi): hesaplanan son günle "
                        "karşılaştırılır; süre kaçırılmışsa NET ve KESİN tespit üretilir (çalışmaya eklenecek dille)")
    p.add_argument("--bayram", type=int, metavar="YYYY",
                   help="Süre hesabı yerine: verilen miladi yıl için TAHMİNİ dini bayram günlerini yazdır "
                        "(aritmetik hicri hesap, ±1-2 gün; Diyanet/RG teyidi ŞART — teyitliyi tatiller.json'a işle)")
    p.add_argument("--adli-tatil-istisna", action="store_true",
                   help="HMK m.103 istisna işi (nafaka, ihtiyati tedbir/haciz, delil tespiti, çekişmesiz yargı, "
                        "iş mahkemesi/iş hukuku uyuşmazlıkları vb.): adli tatil UZATMASI UYGULANMAZ — ham bitiş korunur, "
                        "yalnız hafta sonu/tatil kayması yapılır. Bayraksız (varsayılan) davranış aynen kalır.")
    p.add_argument("--uets", action="store_true",
                   help="E-tebligat (UETS): 7201 m.7/a — elektronik adrese ulaştığı tarihi izleyen 5. günün sonunda "
                        "tebliğ edilmiş sayılır. İki senaryoyu (ulaşma/okunma günü esas VE ulaşma+5. gün karinesi) "
                        "çift hesaplar ve gösterir. --teblig = elektronik adrese ULAŞMA/okunma günüdür.")
    a = p.parse_args()
    if a.bayram:
        print(f"TAHMİNİ dini bayram günleri — {a.bayram} (aritmetik hicri hesap; Diyanet rüyet takviminden ±1-2 gün sapabilir):")
        th = tahmini_bayramlar(a.bayram)
        if not th: print("  (bu yıl için tahmin üretilemedi)")
        for ad, gunler in sorted(th.items()):
            print(f"  {ad}: {gunler[0].isoformat()} .. {gunler[-1].isoformat()} ({len(gunler)} gün)")
        if str(a.bayram) in DINI and DINI[str(a.bayram)]:
            print(f"  ⓘ Tabloda {a.bayram} için RESMÎ kayıt zaten var: {sorted(DINI[str(a.bayram)])}")
        print("UYARI: Bunlar TAHMİNDİR — süre hesabında kullanılmaz. Diyanet/Resmî Gazete'den teyit edip")
        print("tatiller.json 'dini' bölümüne salt-ISO işle; idari izin (CBK/Karar/Genelge) ilanlarını da ayrıca tara.")
        return
    if not a.teblig:
        p.error("--teblig zorunlu (ya da --bayram YYYY kullan)")
    teblig = date.fromisoformat(a.teblig); kaynak=None
    if a.kural:
        miktar,birim,kaynak = KURALLAR[a.kural]
        if a.kural.startswith("iyuk") and a.yargi!="idari":
            print("ⓘ Not: İYUK kuralı; --yargi idari önerilir (çalışmaya ara mekaniği).")
    elif a.sure and a.birim:
        miktar,birim = a.sure,a.birim
    else:
        p.error("Ya --kural ver ya da --sure + --birim birlikte ver.")
    son,rapor,uyarilar = hesapla(teblig,miktar,birim,a.yargi,a.tur,a.adli_tatil_istisna)
    # ── E-TEBLİGAT / UETS (7201 m.7/a): ulaşma+5. gün karine senaryosunu çift hesapla ─
    son_karine = None
    if a.uets:
        karine_teblig = teblig + timedelta(days=5)
        son_karine, _rk, uyarilar_karine = hesapla(karine_teblig, miktar, birim, a.yargi, a.tur, a.adli_tatil_istisna)
        rapor.append("")
        rapor.append("── 7201 m.7/a E-TEBLİGAT (UETS) — İKİ SENARYO (çift hesap) ─────────")
        rapor.append(f"UETS Senaryo-1 (okunma/ulaşma günü esas)  : teblig={teblig.isoformat()} "
                     f"→ son gün {son.isoformat()} ({_gun_adi(son)})")
        rapor.append(f"UETS Senaryo-2 (karine: ulaşma+5. gün sonu): teblig={karine_teblig.isoformat()} "
                     f"→ son gün {son_karine.isoformat()} ({_gun_adi(son_karine)})")
        rapor.append("    NOT: 7201 m.7/a — e-tebligat, muhatabın elektronik adresine ULAŞTIĞI tarihi İZLEYEN")
        rapor.append("    5. günün sonunda yapılmış SAYILIR. Muhatap erken okusa dahi uygulamada güvenli taraf")
        rapor.append("    KARİNE (Senaryo-2) tarihidir; okunma günü esas alınacaksa (Senaryo-1) dayanağını teyit et.")
        uyarilar.append("UETS/E-TEBLİGAT (7201 m.7/a): İki son gün üretildi. Kanun yolu/başvuru süresini kaçırmamak "
            "için GÜVENLİ taraf, KARİNE (ulaşma+5. gün) senaryosunun DAHA ERKEN olanı ise onu; ama süre işlemeye "
            "başlama anını (ulaşma tarihi UYAP/UETS kaydından) BELGELİ olarak teyit et — ulaşma günü ile 5. gün "
            "karinesini karıştırma.")
        # Senaryo-2 (karine) hesabının KENDİ uyarılarından Senaryo-1'den farklı olanları da rapora taşı
        # (ör. karine tebliğ tarihi farklı bir idari izin/bayram penceresine düşebilir — sessizce atılmaz).
        _farkli_uk = [u for u in uyarilar_karine if u not in uyarilar]
        if _farkli_uk:
            rapor.append("    Senaryo-2 (karine) hesabına özgü ek uyarı(lar) — aşağıya işlendi.")
            for _u in _farkli_uk:
                uyarilar.append(f"[UETS Senaryo-2/karine] {_u}")
    # ── SÜRE DENETİMİ (--islem): süresinde mi, kaçırıldı mı (özellikle KARŞI TARAF) ──
    if a.islem:
        islem = date.fromisoformat(a.islem)
        fark = (islem - son).days
        rapor.append("")
        rapor.append("── SÜRE DENETİMİ (fiilî işlem tarihi karşılaştırması) ──────────────")
        rapor.append(f"Fiilî işlem tarihi    : {islem.isoformat()} ({_gun_adi(islem)})")
        if a.uets and son_karine is not None:
            # --uets ile birlikte: 7201 m.7/a karine senaryosu hukuken GEÇERLİ tebliğ
            # tarihidir (ulaşma+5. gün). Yalnız Senaryo-1'e (okunma günü) karşı denetim
            # kesin/net dil için YETERSİZDİR — iki senaryoyu da ayrı ayrı denetle.
            fark_karine = (islem - son_karine).days
            gecti_s1 = fark > 0
            gecti_s2 = fark_karine > 0
            rapor.append(f"    Senaryo-1 (okunma esas) son gün  : {son.isoformat()} → fark {fark:+d} gün")
            rapor.append(f"    Senaryo-2 (karine, ulaşma+5) son gün: {son_karine.isoformat()} → fark {fark_karine:+d} gün")
            if gecti_s1 and gecti_s2:
                rapor.append(f">>> TESPİT — SÜRE KAÇIRILMIŞTIR (HER İKİ SENARYODA DA): İşlem, Senaryo-1 son gününden "
                             f"{fark} gün, Senaryo-2 (karine) son gününden {fark_karine} gün SONRA yapılmıştır.")
                rapor.append("    Süresinden sonra yapılan işlem usul hukuku bakımından sonuç doğurmaz; süreye")
                rapor.append("    ilişkin itiraz/ret talebi DERHÂL ileri sürülür.")
                uyarilar.append("SÜRE KAÇIRMA TESPİTİ (UETS — İKİ SENARYO DA AŞILMIŞ) — ÇALIŞMAYA EKLE (net/kesin dil): "
                    "Karşı tarafa ait süre kaçırması GİZLİ CEPHANELİKTE SAKLANMAZ — bu bir savunma değil AKTİF usul "
                    "itirazıdır, derhâl ve açıkça ileri sürülür. Tebliğ-sayılma tarihini (ulaşma tarihi) UETS kaydından BELGELE.")
            elif gecti_s1 or gecti_s2:
                gec = "Senaryo-1 (okunma günü esas)" if gecti_s1 else "Senaryo-2 (karine, ulaşma+5. gün)"
                sureli = "Senaryo-2 (karine, ulaşma+5. gün)" if gecti_s1 else "Senaryo-1 (okunma günü esas)"
                rapor.append(f">>> ARA TESPİT — SENARYOYA GÖRE DEĞİŞİYOR: {gec} son gününü geçmiştir; ANCAK "
                             f"{sureli} esas alınırsa işlem SÜRESİ İÇİNDEDİR.")
                uyarilar.append(f"KESİN DİL KULLANMA — SENARYOLAR ÇELİŞİYOR (UETS): İşlem yalnız {gec} göre süre "
                    f"kaçırmış görünüyor; {sureli} göre süresindedir (7201 m.7/a — ulaşma+5. gün karinesi hukuken "
                    "GEÇERLİ tebliğ tarihidir). Kesin/net 'süre kaçırılmıştır' dili YALNIZ her iki senaryo da aşıldığında "
                    "kullanılır; aksi hâlde 'tebliğ-sayılma tarihini (ulaşma tarihini) UETS kaydından teyit et' şerhiyle "
                    "ara tespit yazılır — teyide göre kesinleşir.")
            else:
                rapor.append(">>> TESPİT: İşlem SÜRESİ İÇİNDE yapılmıştır (her iki UETS senaryosunda da).")
        elif fark <= 0:
            rapor.append(f">>> TESPİT: İşlem SÜRESİ İÇİNDE yapılmıştır ({'son günde' if fark==0 else f'son günden {-fark} gün önce'}).")
        else:
            rapor.append(f">>> TESPİT — SÜRE KAÇIRILMIŞTIR: İşlem, sürenin dolduğu {son.isoformat()} tarihinden")
            rapor.append(f"    {fark} GÜN SONRA yapılmıştır. Süresinden sonra yapılan işlem usul hukuku")
            rapor.append(f"    bakımından sonuç doğurmaz; süreye ilişkin itiraz/ret talebi DERHÂL ileri sürülür.")
            uyarilar.append("SÜRE KAÇIRMA TESPİTİ — ÇALIŞMAYA EKLE (net/kesin dil): Karşı tarafa ait süre kaçırması "
                "GİZLİ CEPHANELİKTE SAKLANMAZ — bu bir savunma değil AKTİF usul itirazıdır, derhâl ve açıkça ileri "
                "sürülür (ör. istinaf/temyizin SÜREDEN REDDİ; süresinde verilmeyen cevapta HMK m.128 inkâr sonucu; "
                "süresinde sürülmeyen ilk itirazın m.117/2 dinlenmemesi; itiraz edilmeyen bilirkişi raporu m.281). "
                "KESİNLİK ŞARTI: net/kesin dil ancak tebliğ tarihi BELGELİ (tebliğ şerhi/UYAP kaydı/mazbata) ise "
                "kullanılır; teyitsizse tespit 'tebliğ şerhinin teyidi kaydıyla' yazılır. Hesap dayanağı rapor "
                "satırlarındadır (HMK m.92/93/104) — bu satırlar dilekçedeki süre paragrafının iskeletidir (oa-dilekce).")
    print("="*66); print("  SÜRE HESABI — KARAR-MALZEMESİ, NİHAİ TEYİT KULLANICININDIR"); print("="*66)
    if kaynak:
        print(f"Kural                 : {a.kural}  →  {kaynak}")
        teyit = KURAL_TEYIT.get(a.kural, "")
        _kaynak_adi = "gömülü tablo" if _KURAL_TABLO_YOK else "sure_kurallari.json"
        print(f"Kural kaynağı/teyit   : {_kaynak_adi}; mcp_teyit_tarihi = "
              f"{teyit or 'BOŞ → kuralı resmî kaynaktan/Mevzuat MCP ile TEYİT ET (süreler değişebilir)'}")
    print(f"Süre türü             : {a.tur}  ({'usul — adli tatil uygulanır' if a.tur=='usul' else 'maddi hukuk — zamanaşımı/hak düşürücü, adli tatil uygulanmaz'})")
    print(f"Yargı kolu            : {a.yargi}")
    for s in rapor: print(s)
    print("\n--- UYARILAR (deterministik DEĞİL — elle teyit) ---")
    for u in uyarilar: print(f"  ! {u}")
    print("="*66)
    print("Sonraki adım: bu son gün 'python oa_hafiza.py sure-flag --tarih ... --aciklama \"...\" --kural ...'")
    print("ile _oa/sureler.json'a MEKANİK olarak yazılır (halüsinasyon çıpası). event_create/")
    print("reminder_create ÇAĞRILMAZ; dış takvim/hatırlatıcı eşgüdümü AVUKAT tarafından ELLE")
    print("yapılır — araç yoksa/kurulamıyorsa bu açıkça raporlanır (disk pasiftir, kimseyi dürtmez).")

if __name__=="__main__":
    try: main()
    except BrokenPipeError: sys.stderr.close()

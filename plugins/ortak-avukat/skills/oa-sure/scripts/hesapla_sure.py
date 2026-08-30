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

import argparse, datetime as _datetime, json, os, sys
from datetime import date, timedelta

ARA_BASLANGIC = (7, 20)   # HMK m.102 / İYUK m.61: 20 Temmuz
ARA_BITIS = (8, 31)       # 31 Ağustos

# GÖMÜLÜ (fallback) kural tablosu — sure_kurallari.json yoksa/bozuksa devreye girer.
# Süreler HUKUKİ kuraldır; resmî kaynaktan (Mevzuat MCP) teyit edilmelidir.
_GOMULU_KURALLAR = {
    "hmk_istinaf":         (2, "hafta",
                        "HMK m.345 — istinaf, ilamın tebliğinden"),
    "hmk_temyiz":          (2, "hafta",
                        "HMK m.361 — temyiz, BAM kararının tebliğinden"),
    "hmk_cevap":           (2, "hafta",
                        "HMK m.127 — cevap (kural; uzatma ayrı)"),
    "iik_istinaf":         (2, "hafta",
                        "İİK m.363 — icra mah. istinaf (ESKİ 10 GÜN DEĞİL) · 7499 s.K. (yür. 1/6/2024) süreyi iki haftaya çıkardı VE \"tefhim veya\" ibaresini metinden ÇIKARDI — süre artık YALNIZ tebliğden işler."),
    "iik_sikayet":         (7, "gun",
                        "İİK m.16 — icra mahkemesine şikâyet; kural 7 gün (SÜRESİZ şikâyet halleri ayrıktır — m.16/2)"),
    "cmk_itiraz":          (2, "hafta",
                        "CMK m.268 — itiraz; ilgililerin kararı ÖĞRENDİĞİ günden itibaren iki hafta (m.35: yüze karşı açıklama; hazır bulunamayana tebliğ). Eski '7 gün' YÜRÜRLÜKTE DEĞİL. CMK m.263 (tutuklunun kurum müdürüne başvurusu — süreyi KESER) saklıdır."),
    "cmk_istinaf":         (2, "hafta",
                        "CMK m.273/1 — istinaf; hükmün GEREKÇESİYLE BİRLİKTE TEBLİĞ edildiği tarihten iki hafta. (Hazır bulunmayanlara ilişkin f.2, 7499 s.K. ile MÜLGA — tek başlangıç: gerekçeli karar tebliği. Savcı yönünden f.3: kararın başsavcılığa geliş tarihi. m.263 saklıdır.)"),
    "cmk_temyiz":          (2, "hafta",
                        "CMK m.291/1 — temyiz; hükmün GEREKÇESİYLE BİRLİKTE TEBLİĞ edildiği tarihten iki hafta (f.2 7499 ile MÜLGA; m.273 ile simetrik; m.263 saklıdır)."),
    "iyuk_dava_idare":     (60, "gun",
                        "İYUK m.7 — idare mah./Danıştay dava açma · 7331 s.K.'nın \"altmış→otuz\" değişikliği m.10/11/13 içindir; m.7 dava açma süresine DOKUNULMAMIŞTIR (sık karıştırılır)."),
    "iyuk_dava_vergi":     (30, "gun",
                        "İYUK m.7 — vergi mah. dava açma"),
    "iyuk_istinaf":        (30, "gun",
                        "İYUK m.45 — BİM istinaf"),
    "iyuk_temyiz":         (30, "gun",
                        "İYUK m.46 — Danıştay temyiz · Süre değişmedi; ANCAK 7589 s.K. (31/7/2026) kapsamı genişletti (yeni f.2; (c) bendi mülga) — geçici m.1/3: 31/7/2026 SONRASI BİM kararlarına uygulanır."),
    "iyuk_yd_itiraz":      (7, "gun",
                        "İYUK m.27/7 — yürütmenin durdurulması istemi hakkında verilen karara İTİRAZ; kararın tebliğini İZLEYEN günden itibaren yedi gün, BİR DEFAYA MAHSUS (itiraz üzerine verilen karar kesindir). İSTİSNA: m.20/A-2/e (ivedi yargılama) ve m.20/B-1/d (merkezî ve ortak sınav) davalarında YD kararlarına İTİRAZ EDİLEMEZ."),
    "iyuk_dava_ivedi":     (30, "gun",
                        "İYUK m.20/A-2/a — İVEDİ YARGILAMA usulünde dava açma; otuz gün. Katalog m.20/A-1: ihale işlemleri (yasaklama hariç), acele kamulaştırma, ÖYK kararları, 2634 turizm satış/tahsis/kiralama, ÇED kararları, 6306 CB kararları. m.20/A-2/b: m.11 UYGULANMAZ. m.45/8: istinaf yolu KAPALI."),
    "iyuk_temyiz_ivedi":   (15, "gun",
                        "İYUK m.20/A-2/g — ivedi yargılamada nihai karara karşı TEMYİZ; tebliğ tarihinden on beş gün (istinaf YOK — m.45/8; temyize cevap süresi m.20/A-2/ı on beş gün)."),
    "iyuk_dava_sinav":     (10, "gun",
                        "İYUK m.20/B-1/a — MEB ve ÖSYM'nin MERKEZÎ VE ORTAK SINAVLARINA ilişkin davalarda dava açma; on gün. m.20/B-1/b: m.11 UYGULANMAZ."),
    "iyuk_temyiz_sinav":   (5, "gun",
                        "İYUK m.20/B-1/f — merkezî ve ortak sınav davalarında nihai karara karşı TEMYİZ; tebliğ tarihinden beş gün (temyize cevap süresi m.20/B-1/ğ beş gün)."),
    "iyuk_temyiz_cevap":   (30, "gun",
                        "İYUK m.48/3 — temyiz dilekçesine CEVAP; tebliğ tarihini izleyen otuz gün. Cevap veren, kararı süresinde temyiz etmemiş olsa bile dilekçesinde temyiz isteminde bulunabilir (bu dilekçe temyiz dilekçesi yerine geçer)."),
    "iyuk_temyiz_ozel_7gun": (7, "gun",
                        "İYUK m.48/6 son cümle — temyiz isteminde bulunulmamış sayılmasına (m.48/2) ve temyiz isteminin reddine ilişkin kararlara karşı tebliğ tarihini İZLEYEN günden itibaren yedi gün; İYUK m.45/2 ek cümle (7524 s.K.) — BİM'in m.48/7 uyarınca verdiği kararlara karşı da yedi gün."),
    "amme_6183_m58":       (15, "gun",
                        "6183 m.58 — ödeme emrine karşı dava; tebliğ tarihinden itibaren 15 gün (7061 s.K. ile 7→15). Ödeme emri bir TAHSİLAT işlemidir: dava açılması tahsili KENDİLİĞİNDEN durdurmaz (İYUK m.27/4) — ayrıca yürütmenin durdurulması istenir."),
    "aym_bireysel":        (30, "gun",
                        "6216 m.47/5 — AYM bireysel başvuru"),
}

# B-21 (v0.5.14) — teyit tarihi kaynak METNİNDEN AYRI alanda tutulur; böylece
# aynı bilginin iki kaynağı (metin içi şerh + JSON alanı) doğup ayrışamaz.
_GOMULU_TEYIT = {
    "hmk_istinaf":         "2026-08-31",
    "hmk_temyiz":          "2026-08-31",
    "hmk_cevap":           "2026-08-31",
    "iik_istinaf":         "2026-08-31",
    "iik_sikayet":         "2026-08-31",
    "cmk_itiraz":          "2026-08-31",
    "cmk_istinaf":         "2026-08-31",
    "cmk_temyiz":          "2026-08-31",
    "iyuk_dava_idare":     "2026-08-31",
    "iyuk_dava_vergi":     "2026-08-31",
    "iyuk_istinaf":        "2026-08-31",
    "iyuk_temyiz":         "2026-08-31",
    "iyuk_yd_itiraz":      "2026-08-31",
    "iyuk_dava_ivedi":     "2026-08-31",
    "iyuk_temyiz_ivedi":   "2026-08-31",
    "iyuk_dava_sinav":     "2026-08-31",
    "iyuk_temyiz_sinav":   "2026-08-31",
    "iyuk_temyiz_cevap":   "2026-08-31",
    "iyuk_temyiz_ozel_7gun": "2026-08-31",
    "amme_6183_m58":       "2026-08-31",
    "aym_bireysel":        "2026-08-31",
}

# B-20 (v0.5.14) — kuralın hukuken İZİN VERDİĞİ başlangıç türleri. Script
# NİTELENDİRME YAPMAZ: yalnız seçilen türün bu kümede olup olmadığına bakar.
_GOMULU_BASLANGIC = {
    "hmk_istinaf":            ["teblig", "tefhim"],
    "hmk_temyiz":             ["teblig", "tefhim"],
    "hmk_cevap":              ["teblig"],
    "iik_istinaf":            ["teblig", "tefhim"],
    "iik_sikayet":            ["ogrenme", "teblig"],
    "cmk_itiraz":             ["ogrenme", "teblig", "tefhim"],
    "cmk_istinaf":            ["teblig"],
    "cmk_temyiz":             ["teblig"],
    "iyuk_dava_idare":        ["teblig", "ogrenme"],
    "iyuk_dava_vergi":        ["teblig", "ogrenme"],
    "iyuk_istinaf":           ["teblig"],
    "iyuk_temyiz":            ["teblig"],
    "iyuk_yd_itiraz":         ["teblig"],
    "iyuk_dava_ivedi":        ["teblig", "ogrenme"],
    "iyuk_temyiz_ivedi":      ["teblig"],
    "iyuk_dava_sinav":        ["teblig", "ogrenme"],
    "iyuk_temyiz_sinav":      ["teblig"],
    "iyuk_temyiz_cevap":      ["teblig"],
    "iyuk_temyiz_ozel_7gun":  ["teblig"],
    "amme_6183_m58":          ["teblig"],
    "aym_bireysel":           ["teblig", "ogrenme"],
}

# B-21 (v0.5.14) — JSON okunamazsa artık SESSİZ düşülmez: sebep burada saklanır
# ve hesabın BAŞINDA görünür şekilde raporlanır ("gömülüye düşüldü, çünkü ...").
_KURAL_TABLO_SEBEP = ""
# Kuralın izin verdiği başlangıç türleri (JSON'dan okunur; yoksa gömülüden).
KURAL_BASLANGIC = {}


def kurallari_yukle():
    """sure_kurallari.json varsa oradan (kural, teyit, başlangıç) oku; yoksa/bozuksa
    gömülüye düş — ve DÜŞME SEBEBİNİ `_KURAL_TABLO_SEBEP`e yaz (B-21: sessiz
    fallback, kullanıcıya birbirini yalanlayan iki satır gösteriyordu)."""
    global _KURAL_TABLO_SEBEP, KURAL_BASLANGIC
    yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sure_kurallari.json")
    if not os.path.exists(yol):
        _KURAL_TABLO_SEBEP = "sure_kurallari.json BULUNAMADI"
    else:
        try:
            with open(yol, encoding="utf-8") as f:
                data = json.load(f)
            kurallar, teyit, baslangic = {}, {}, {}
            for k, v in data.get("kurallar", {}).items():
                kurallar[k] = (v["miktar"], v["birim"], v.get("kaynak", ""))
                teyit[k] = v.get("mcp_teyit_tarihi", "") or ""
                bt = v.get("izinli_baslangic_turleri") or []
                baslangic[k] = [str(x) for x in bt] if isinstance(bt, list) else []
            if kurallar:
                KURAL_BASLANGIC = baslangic
                return kurallar, teyit, False
            _KURAL_TABLO_SEBEP = "sure_kurallari.json 'kurallar' bölümü BOŞ"
        except Exception as e:
            _KURAL_TABLO_SEBEP = ("sure_kurallari.json OKUNAMADI/BOZUK "
                                  "(%s: %s)" % (type(e).__name__, e))
    KURAL_BASLANGIC = {k: list(v) for k, v in _GOMULU_BASLANGIC.items()}
    return dict(_GOMULU_KURALLAR), dict(_GOMULU_TEYIT), True

KURALLAR, KURAL_TEYIT, _KURAL_TABLO_YOK = kurallari_yukle()

# ── A-1 (P0, v0.5.14) — KURAL ↔ YARGI KOLU MUTABAKATI ─────────────────────
# Ceza sürelerinde adli tatil rejimi HMK m.104 (bir hafta) DEĞİL, CMK m.331/4
# (ÜÇ GÜN) uyarınca işler. Kural ile kol uyuşmazsa hesap SESSİZCE yanlış bir
# son gün üretiyordu (denetim A-1: dört gün GEÇ → süreden ret → kesinleşme).
# Sessiz yanlış varsayılan YASAK: uyuşmazlıkta hesap DURUR (aşağıda main/
# _pencere_kontrol), çünkü uyarı basılsa dahi ">>> HESAPLANAN SON GÜN" satırı
# ve otomatik `_oa/sureler.json` flag'i yanlış tarihi kalıcılaştırırdı.
KURAL_KOLU = {"cmk": "ceza", "hmk": "hukuk", "iik": "hukuk",
              "iyuk": "idari", "amme": "idari", "aym": None}


def kural_kolu(kural):
    """Kuralın ait olduğu yargı kolunu ön ekinden döndürür; bilinmiyorsa None."""
    if not kural:
        return None
    return KURAL_KOLU.get(str(kural).split("_", 1)[0])


def kol_uyusmazligi(kural, yargi):
    """(A-1) Kural ↔ yargı kolu uyuşmazlığında insan-okur gerekçe döndürür; yoksa None.

    Yalnız ADLİ TATİL REJİMİNİN FARKLI olduğu hâller bloklanır:
      · ceza kolu ile ceza-dışı kural (üç günlük uzatma hukuk/idari süreyi KISALTIR)
      · ceza kuralı ile ceza-dışı kol (bir haftalık uzatma ceza süresini UZATIR)
    İYUK ↔ HMK arasında uzatma aritmetiği aynı sonucu verdiği için (31 Ağu + 1
    hafta ≡ 1 Eylül'den 7 gün) orası bilgi notu olarak kalır, bloklanmaz.
    """
    beklenen = kural_kolu(kural)
    if beklenen is None:
        if yargi == "ceza":
            return ("'%s' kuralı ceza yargısına ait değil; --yargi ceza ile "
                    "koşulursa CMK m.331/4 (üç gün) uzatması uygulanır ve süre "
                    "YANLIŞ KISALIR." % kural)
        return None
    if beklenen == "ceza" and yargi != "ceza":
        return ("'%s' bir CEZA kanun yolu kuralıdır; --yargi %s ile koşulduğunda "
                "adli tatil uzatması HMK m.104/İYUK m.8-3 rejimine göre yapılır ve "
                "son gün CMK m.331/4'e göre olması gerekenden GEÇ çıkar (denetim "
                "A-1: dört gün). Doğru kullanım: --yargi ceza" % (kural, yargi))
    if beklenen != "ceza" and yargi == "ceza":
        return ("'%s' ceza yargısına ait bir kural DEĞİLDİR; --yargi ceza ile "
                "koşulduğunda CMK m.331/4 (üç gün) uzatması uygulanır ve süre "
                "YANLIŞ KISALIR. Doğru kullanım: --yargi %s" % (kural, beklenen))
    return None


# B-16 / B-22 (v0.5.14) — miktar için akla uygun üst sınır: bunun ötesi
# hesaplanabilir bir usul/maddi süre değil, girdi hatasıdır (yıl biriminde
# date aritmetiği 9999'u aşınca ham OverflowError/ValueError veriyordu).
MIKTAR_UST_SINIR = {"gun": 36525, "hafta": 5217, "ay": 1200, "yil": 100}


def miktar_dogrula(miktar, birim):
    """Geçersiz miktarda insan-okur gerekçe döndürür; geçerliyse None."""
    if not isinstance(miktar, int) or isinstance(miktar, bool):
        return "süre miktarı tam sayı olmalı (verilen: %r)" % (miktar,)
    if miktar < 0:
        return ("süre NEGATİF olamaz (verilen: %d). Negatif süre, tebliğden ÖNCEKİ "
                "bir tarihi 'son gün' diye üretir — bu bir hesap değil, girdi hatasıdır."
                % miktar)
    if miktar == 0:
        return ("süre SIFIR olamaz (verilen: 0). Sıfır uzunlukta bir usul süresi yoktur; "
                "başlangıç tarihini mi kastettiniz?")
    ust = MIKTAR_UST_SINIR.get(birim)
    if ust is not None and miktar > ust:
        return ("süre miktarı akla uygun üst sınırı aşıyor (%d %s > %d %s). "
                "Girdi hatası olmadığından emin olun." % (miktar, birim, ust, birim))
    return None
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

# v0.5.13 — BAŞLANGIÇ TÜRÜ (pratikçi hakem heyeti tez 1; MCP teyitli gerekçe):
# aynı dosyada iki farklı başlangıç rejimi yaşayabilir — CMK m.268 itiraz
# *öğrenme gününden*, m.273/291 istinaf-temyiz *gerekçeli kararın tebliğinden*
# işler. Bu alan ARİTMETİĞİ DEĞİŞTİRMEZ; hangi olayın süreyi başlattığını
# çıktıda GÖRÜNÜR kılar (yanlış olaya bağlanan doğru hesap, yanlış hesaptır).
# Opsiyoneldir: verilmezse davranış birebir eskisi gibidir.
BASLANGIC_TURLERI = {
    "teblig": "tebliğ (evrakın usulüne uygun tebliği)",
    "tefhim": "tefhim (duruşmada yüze karşı açıklama)",
    "ogrenme": "öğrenme (fiilen öğrenildiği gün)",
    "olay": "olay/fiil tarihi (maddi hukuk süreleri)",
    "belirsiz": "BELİRSİZ — iki senaryo hesaplanmalı",
}


def _kurtarma_kapisi_notu(yargi):
    """A-10 (v0.5.14) — kaçırılan süre için gösterilecek kurtarma kapısı YARGI
    KOLUNA GÖRE değişir. Eski kod idari dosyada da HMK m.95'i öneriyordu; oysa
    2577'de 'eski hale getirme'/'mazeret' geçmiyor (MCP içinde-ara 2026-08-31 →
    0 eşleşme) ve ailenin kendi kuralı 'bu satır idari dosyaya ASLA basılmaz'
    diyordu. Var olmayan bir kapı, gerçek kapıların aranmasını engeller."""
    if yargi == "idari":
        return ("İşlem o gün fiilen imkânsızlaştıysa: İYUK'ta ESKİ HÂLE GETİRME KURUMU YOKTUR "
                "(2577'de 'eski hale getirme'/'mazeret' hükmü bulunmaz) — HMK m.95'e GÜVENME. "
                "Bakılacak gerçek yerler: AY m.40/2 (başvuru yolu, mercii ve süresinin işlemde "
                "bildirilmemesi), İYUK m.10 (idari makama başvuru) ve vergide düzeltme-şikâyet "
                "(YALNIZ vergi hatası varsa — VUK m.116-126). Hangisinin açık olduğunu teyit et.")
    if yargi == "ceza":
        return ("İşlem o gün fiilen imkânsızlaştıysa CMK m.40 (eski hâle getirme) değerlendirilir: "
                "'Kusuru olmaksızın bir süreyi geçirmiş olan kişi, eski hale getirme isteminde "
                "bulunabilir'; kanun yoluna başvuru hakkı bildirilmemişse kişi KUSURSUZ sayılır "
                "(m.40/2). Ayrıca tutukluda CMK m.263 kanalı ayrıca kontrol edilir — buna güvenerek "
                "bekleme, süresinde işlem yap.")
    return ("İşlem o gün fiilen imkânsızlaştıysa eski hâle getirme (HMK m.95 vd.; süre m.96 — "
            "engelin kalkmasından iki hafta) ayrıca ve ihtiyatla değerlendirilir — buna güvenerek bekleme.")


def hesapla(teblig, miktar, birim, yargi, tur="usul", adli_tatil_istisna=False,
            baslangic_turu=None, kural=None):
    rapor, uyarilar = [], []
    # B-16 (v0.5.14) — negatif/sıfır/aşırı miktar SESSİZCE kabul edilemez:
    # eskiden `--sure -5` tebliğden ÖNCEKİ bir tarihi ">>> HESAPLANAN SON GÜN"
    # diye basıp exit 0 dönüyordu (ve --kok verilirse deftere de yazıyordu).
    _mh = miktar_dogrula(miktar, birim)
    if _mh:
        raise ValueError(_mh)
    bas = teblig + timedelta(days=1)
    if baslangic_turu is not None:
        anahtar = str(baslangic_turu).strip().lower()
        if anahtar in BASLANGIC_TURLERI:
            rapor.append("Başlangıç türü        : %s" % BASLANGIC_TURLERI[anahtar])
            if anahtar == "belirsiz":
                uyarilar.append(
                    "BAŞLANGIÇ BELİRSİZ: süre hangi olaydan işlediği kesin değil "
                    "— İKİ senaryo ayrı ayrı hesaplanmalı ve plan ERKEN tarihe "
                    "göre yapılmalıdır (geç senaryoya güvenmek hak kaybettirir).")
            # B-20 (v0.5.14) — seçilen başlangıç türü kuralın hukuken izin
            # verdiği türlerden değilse çelişki SESSİZ kalamaz. Script
            # NİTELENDİRME yapmaz: yalnız alanın kapalı kümede olup olmadığına
            # bakar; hukuki hüküm avukata aittir (kural metni ekrandadır).
            _izinli = [str(x).strip().lower()
                       for x in (KURAL_BASLANGIC.get(kural) or [])] if kural else []
            if _izinli and anahtar not in _izinli and anahtar != "belirsiz":
                uyarilar.append(
                    "BAŞLANGIÇ TÜRÜ ÇELİŞKİSİ: '%s' kuralının kayıtlı başlangıç türleri "
                    "(%s) arasında '%s' YOK. Kural satırındaki dayanağı oku ve hangi "
                    "olayın süreyi başlattığını Mevzuat MCP'den teyit et — yanlış olaya "
                    "bağlanan doğru hesap, yanlış hesaptır." % (
                        kural, ", ".join(_izinli), anahtar))
        else:
            uyarilar.append(
                "TANINMAYAN BAŞLANGIÇ TÜRÜ: %r — sessizce 'tebliğ' sayılmadı; "
                "geçerli değerler: %s" % (baslangic_turu,
                                          ", ".join(sorted(BASLANGIC_TURLERI))))
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
        if yargi=="ceza":
            # A-1 (P0, v0.5.14 — MCP teyitli 2026-08-31, CMK m.331/4):
            # "Adlî tatile rastlayan süreler işlemez. Bu süreler tatilin bittiği
            # günden itibaren ÜÇ GÜN uzatılmış sayılır." Bu, hukuk yargısının
            # bir haftalık uzatmasından (HMK m.104) DÖRT GÜN kısadır; eski kod
            # ceza dosyasına hukuk rejimini uyguluyor ve dört gün GEÇ tarih
            # veriyordu (süreden ret → hüküm kesinleşir).
            son = date(son.year,*ARA_BITIS) + timedelta(days=3)
            rapor.append(f"Adli tatil (CMK m.331/4): ham bitiş 20 Tem–31 Ağu arasında; süre İŞLEMEZ ve "
                         f"tatilin bittiği günden (31 Ağu) itibaren ÜÇ GÜN uzatılmış sayılır → {son.isoformat()}")
            uyarilar.append(
                "CEZA ADLİ TATİLİ (CMK m.331): (1) f.4 uyarınca uzatma ÜÇ GÜNDÜR — hukuk yargısının "
                "HMK m.104 bir haftalık uzatmasıyla KARIŞTIRMA. (2) f.2: soruşturma ile TUTUKLU işlere "
                "ilişkin kovuşturmaların ve ivedi sayılacak diğer hususların tatil süresi içinde ne "
                "suretle yerine getirileceğini HSK belirler. (3) f.3: tatil süresince BAM ve Yargıtay "
                "yalnız TUTUKLU hükümlere ilişkin veya Meşhud Suçların Muhakeme Usulü Kanunu gereğince "
                "görülen işlerin incelemelerini yapar. f.2-3 hangi İŞLERİN görüleceğine dairdir; süre "
                "uzaması her hâlde f.4'e tabidir — tutuklu dosyada işin fiilen yürüyecek olması sürenin "
                "uzamadığı anlamına GELMEZ. Tutuklu sanıkta ayrıca CMK m.263 (ceza infaz kurumu "
                "müdürüne başvuru süreyi KESER) değerlendirilir.")
        elif yargi=="hukuk":
            son = date(son.year,*ARA_BITIS) + timedelta(weeks=1)
            rapor.append(f"Adli tatil (HMK m.104): ham bitiş 20 Tem–31 Ağu arasında; 31 Ağu + 1 hafta → {son.isoformat()}")
        else:
            son = date(son.year,*ARA_BITIS) + timedelta(days=7)
            rapor.append(f"Çalışmaya ara (İYUK m.8/3): ham bitiş 20 Tem–31 Ağu arasında; ara bitimini izleyen "
                         f"1 Eylül'den itibaren 7 gün (1 Eylül dahil) → {son.isoformat()}")
            # A-20 (v0.5.14) — İYUK m.8/3 uzatmasının ÖZEL KANUN sürelerine
            # (ör. 6183 m.58) uygulanması TARTIŞMALIDIR. Danıştay 7.D.
            # E.2000/5685 K.2002/3522 (13.11.2002, MCP tam metin) çoğunluğu
            # uzamadan yana — script bu tarafta — ANCAK karar OYÇOKLUĞU ile
            # verilmiştir; tetkik hâkimi, Danıştay savcısı ve ayrışık oy aksi
            # yöndedir. Tarih kesin bilgi gibi sunulamaz.
            if kural and kural_kolu(kural) == "idari" and not str(kural).startswith("iyuk"):
                uyarilar.append(
                    "TARTIŞMALI UZATMA (A-20): Son gün, İYUK m.8/3 çalışmaya ara uzatmasının ÖZEL "
                    "KANUNDAKİ ('%s') süreye de uygulanmasıyla bulundu. Danıştay 7. Daire "
                    "E.2000/5685 K.2002/3522 (13.11.2002) çoğunluğu bu yönde ('bu düzenleme özel bir "
                    "düzenlemedir… özel kanunlarda öngörülen dava açma süresi olması hâlinde de "
                    "uzayacağı açıktır') — ancak karar OYÇOKLUĞU ile verilmiştir; tetkik hâkimi, "
                    "Danıştay savcısı ve AYRIŞIK OY aksi yöndedir (özel süre 2577'de yazılı olmadığı "
                    "için uzamaz). Karşı taraf ayrışık oya dayanarak süre aşımı def'i ileri sürebilir: "
                    "GÜVENLİ PLAN HAM BİTİŞ tarihidir (%s) — işlemi ona göre yap, uzamış süreyi yalnız "
                    "ikincil savunma olarak tut." % (kural, ham.isoformat()))
    elif tur=="usul" and aralik_icinde_mi(son) and adli_tatil_istisna:
        # A-7 (v0.5.14) — İSTİSNA GEREKÇESİ YARGI KOLUNA GÖRE DALLANIR.
        # Eski kod idari yargı istinafında da HMK m.103 kataloğunu basıyordu;
        # oysa idari yargının nöbetçi mahkeme kataloğu İYUK m.62'dir ve içeriği
        # tamamen farklıdır (MCP teyitli 2026-08-31). Sayılan işler adli tatilde
        # GÖRÜLÜR → süre UZAMAZ; ham bitiş korunur, yalnız son gün kayması yapılır.
        if yargi == "idari":
            rapor.append(f"İYUK m.62 nöbetçi mahkeme işi — çalışmaya ara uzatması uygulanmadı: ham bitiş "
                         f"{son.isoformat()} ({_gun_adi(son)}) 20 Tem–31 Ağu arasında olsa da UZATILMADI. "
                         f"İYUK m.62: nöbetçi mahkeme ara verme süresi içinde (a) yürütmenin durdurulmasına "
                         f"ve delillerin tespitine ait işleri, (b) kanunen belli süre içinde karara "
                         f"bağlanması gereken işleri görür. Yalnız hafta sonu/tatil kayması yapılır.")
            uyarilar.append(
                "İYUK m.62 İSTİSNASI seçildi: İdari yargının ara verme kataloğu HMK m.103 DEĞİL, "
                "İYUK m.62'dir (iki katalog birbirinden tamamen farklıdır). Bu işin gerçekten m.62 "
                "kapsamında olduğunu TEYİT ET — kapsam dışı bir işte istisnayı uygulamak süreyi 14 GÜN "
                "YANLIŞ KISALTIR. Ayrıca İYUK m.61/1 c.2: yargı çevresine dâhil olduğu BİM'in bulunduğu "
                "il merkezi dışında kalan ve SADECE BİR idare veya bir vergi mahkemesi bulunan yerlerdeki "
                "idari yargı mercileri çalışmaya ara vermeden YARARLANAMAZ — dosyanın mahkemesi buysa "
                "m.8/3 uzamasının işleyip işlemediği ayrıca değerlendirilir. Tereddütte istisnayı KALDIR "
                "(bayraksız hesap güvenli taraftır).")
        elif yargi == "ceza":
            rapor.append(f"CEZA KOLUNDA İSTİSNA BAYRAĞI — uzatma uygulanmadı: ham bitiş {son.isoformat()} "
                         f"({_gun_adi(son)}) 20 Tem–31 Ağu arasında olsa da UZATILMADI. Yalnız hafta "
                         f"sonu/tatil kayması yapılır.")
            uyarilar.append(
                "DİKKAT — CMK m.331/4 LAFZINDA İSTİSNA YOKTUR: 'Adlî tatile rastlayan süreler işlemez. "
                "Bu süreler tatilin bittiği günden itibaren üç gün uzatılmış sayılır.' Madde, sürenin "
                "uzamayacağı bir iş kategorisi saymaz; m.331/2-3 hangi İŞLERİN tatilde görüleceğini "
                "belirler (soruşturma, tutuklu işlere ilişkin kovuşturma, ivedi işler; BAM/Yargıtay'da "
                "tutuklu hükümler) — bu, sürenin uzamadığı anlamına GELMEZ. `--adli-tatil-istisna` "
                "bayrağı HMK m.103 için tasarlanmıştır; ceza dosyasında kullanmak süreyi ÜÇ GÜN "
                "KISALTIR ve dayanağı YOKTUR. Aksi bir dayanak teyit edilmedikçe bayrağı KALDIR.")
        else:
            rapor.append(f"HMK m.103 istisna işi — adli tatil uzatması uygulanmadı: ham bitiş {son.isoformat()} "
                         f"({_gun_adi(son)}) 20 Tem–31 Ağu arasında olsa da UZATILMADI. HMK m.103/1 bentleri: "
                         f"(a) ihtiyati tedbir/ihtiyati haciz/delil tespiti gibi geçici hukuki koruma, deniz "
                         f"raporu ve dispeçci atanması talepleri ile bunlara karşı itiraz ve başvurular; "
                         f"(b) her çeşit nafaka davaları ile soybağı, velayet ve vesayete ilişkin dava/işler; "
                         f"(c) nüfus kayıtlarının düzeltilmesi; (ç) hizmet akdi veya iş sözleşmesi sebebiyle "
                         f"İŞÇİLERİN AÇTIKLARI davalar; (d) ticari defter kaybı/kıymetli evrak iptali; "
                         f"(e) iflas, konkordato ve yeniden yapılandırma; (f) adli tatilde yapılmasına karar "
                         f"verilen keşifler; (g) tahkim; (ğ) çekişmesiz yargı işleri; (h) kanunen ivedi olan "
                         f"veya mahkemece ivedi görülmesine karar verilen dava/işler. Yalnız hafta sonu/tatil "
                         f"kayması yapılır.")
            uyarilar.append("HMK m.103 ADLİ TATİL İSTİSNASI seçildi: Bu işin gerçekten m.103 kapsamında (adli tatilde "
                "görülen iş) olduğunu TEYİT ET — kapsam dışı bir işte istisnayı uygulamak süreyi YANLIŞ KISALTIR ve "
                "hak kaybına yol açar. DAVACI SIFATINI TEYİT ET: m.103/1-ç istisnası 'işçilerin AÇTIKLARI davalar' "
                "lafzıyla davacı sıfatına bağlıdır — İŞVERENİN açtığı iş davası bu bende girmez. Aynı şekilde "
                "m.103/1-b nafakanın yanında soybağı, velayet ve vesayeti sayar; m.103/2 uyarınca tarafların "
                "anlaşmasıyla bu işlerin görülmesi tatil sonrasına bırakılabilir. Tereddütte istisnayı KALDIR "
                "(bayraksız hesap güvenli taraftır).")
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
        # A-7/A-1 (v0.5.14) — kayma dayanağı da yargı koluna göre yazılır:
        # hukuk HMK m.93, idari İYUK m.8/2, ceza CMK m.39/4 (MCP teyitli 2026-08-31).
        _kayma_capa = {"ceza": "CMK m.39/4", "idari": "İYUK m.8/2"}.get(yargi, "HMK m.93")
        rapor.append(f"Tatil günü düzeltmesi : {eski.isoformat()} {sebep} → ilk iş günü {son.isoformat()} "
                     f"({_kayma_capa}: yalnız SON GÜN tatile rastlarsa uzar; aradaki tatil günleri süreye DAHİLDİR)")
    # ── İDARİ İZİN KATMANI (uyarı — KAYDIRMA YAPILMAZ) ─────────────────────
    # Hukuki kural: idari izin (CB tasarrufu — Kararname/Karar/Genelge) 2429 anlamında resmî tatil
    # değildir; süreyi UZATMAZ, SÜREDEN SAYILIR. Riski görünür kılar, son günü değiştirmez.
    if idari_izin_mi(son):
        rapor.append(f"ⓘ Son gün {son.isoformat()} İDARİ İZİN gününe denk geliyor — son gün KAYDIRILMADI (idari izin süreden sayılır).")
        uyarilar.append("İDARİ İZİN: Son gün, Cumhurbaşkanlığı tasarrufuyla (Kararname/Karar/Genelge) ilan edilmiş idari izin gününe denk. "
            "İdari izin 2429 s.K. anlamında resmî tatil DEĞİLDİR — SÜREYİ UZATMAZ, SÜREDEN SAYILIR. "
            "Kamu birimleri (vergi dairesi, tapu, kalem, vezne) fiilen kapalı/eksik çalışıyor olabilir: "
            "fiziki işlem veya harç/vezne gerektiren adımı ÖNCEDEN tamamla; UYAP elektronik kanalı 23:59'a kadar açıktır. "
            + _kurtarma_kapisi_notu(yargi))
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
        # A-5 (v0.5.14) — eski uyarı ("özel kanun süreleri olabilir") avukatı
        # YANLIŞ yöne bakmaya sevk ediyordu: en sık ıskalanan kısa süreler özel
        # kanunlarda değil, İYUK'un KENDİSİNDEDİR (m.20/A, m.20/B — MCP teyitli
        # 2026-08-31). Bir dosyada 60 gün sanılan süre gerçekte 30 veya 10 olabilir.
        uyarilar.append(
            "ÖZEL YARGILAMA USULÜ (İYUK'UN KENDİSİNDE): Dava İYUK m.20/A (İVEDİ YARGILAMA) veya "
            "m.20/B (MERKEZÎ VE ORTAK SINAV) kapsamındaysa süreler bu hesabın varsayılanından çok "
            "daha KISADIR. m.20/A-1 katalog: ihale işlemleri (yasaklama hariç), ACELE KAMULAŞTIRMA, "
            "ÖYK kararları, 2634 turizm satış/tahsis/kiralama, ÇED kararları, 6306 CB kararları → "
            "dava 30 gün (m.20/A-2/a), temyiz 15 gün (/g), İSTİNAF YOLU KAPALI (m.45/8), m.11 "
            "UYGULANMAZ (/b), YD kararına İTİRAZ EDİLEMEZ (/e). m.20/B (MEB-ÖSYM merkezî ve ortak "
            "sınavlar) → dava 10 gün (/a), temyiz 5 gün (/f), m.11 UYGULANMAZ (/b), YD kararına "
            "itiraz edilemez (/d). İlgili kural adları: iyuk_dava_ivedi, iyuk_temyiz_ivedi, "
            "iyuk_dava_sinav, iyuk_temyiz_sinav. Ayrıca özel kanunlarda (memur disiplin, ihale vb.) "
            "başka süreler de olabilir — uygulanan kuralı Mevzuat MCP'den teyit et.")
    if yargi=="ceza" and tur=="usul":
        uyarilar.append(
            "CEZA KANUN YOLU KAPILARI: Başvuru süresi işlese de yol KAPALI olabilir — istinafta "
            "CMK m.272/3 (parasal sınır ve kesin hükümler), temyizde m.286 sınırlamaları kullanım "
            "anında Mevzuat MCP'den teyit edilir. Tutuklu sanıkta CMK m.263 (ceza infaz kurumu "
            "müdürüne başvuru) süreyi KESER — müvekkile bu kanal ayrıca söylenir.")
    # B-16 (v0.5.14) — SON SAĞLIK KONTROLÜ: son gün hiçbir koşulda başlangıç
    # tarihinden önce olamaz. Bu satır bir daha ASLA geçmeyecek olsa bile durur:
    # bu motorun tek işi tarih aritmetiğidir ve geçmişe düşen bir "son gün"
    # deftere yazılıp nöbetçi tarafından "GEÇMİŞ süre" diye alarma dönüşür.
    if son < teblig:
        raise ValueError(
            "İÇ TUTARSIZLIK: hesaplanan son gün (%s) başlangıç tarihinden (%s) ÖNCE — "
            "sonuç kullanılamaz." % (son.isoformat(), teblig.isoformat()))
    rapor.append("")
    rapor.append(f">>> HESAPLANAN SON GÜN  : {son.isoformat()} ({_gun_adi(son)}) — mesai bitimi <<<")
    return son, rapor, uyarilar

def _pencere_kontrol(json_yol, cikti_yol=None):
    """M5 (Paket D, v0.5.5) — SÜRE PENCERE BİNDİRME KONTROLÜ: birden çok süre
    kaydını (`{ad, teblig, kural | (sure+birim), [yargi, tur, adli_tatil_istisna]}`)
    OKUYUP her birini `hesapla()` ile (TEK mantık — kod tekrarı yok) çözer, her
    kaydın [teblig+1, son_gün] PENCERESİNİ çıkarır ve pencerelerin PAIRWISE
    ÇAKIŞIP çakışmadığını (bindirme) raporlar. Amaç: illiyet/kronoloji
    katmanındaki (oa-illiyet zaman katmanı) birden fazla süre AYNI ANDA
    işlerken biri gözden kaçabilir — bu kontrol o körlüğü kapatır. Hukuki
    öncelik/hangi sürenin daha kritik olduğu MUHAKEMEDİR; script yalnız
    ÇAKIŞMAYI (tarih aritmetiği) tespit eder."""
    try:
        with open(json_yol, encoding="utf-8") as f:
            kayitlar = json.load(f)
    except Exception as e:
        print(f"HATA: pencereler JSON okunamadı: {e}")
        sys.exit(1)

    # M5 düzeltmesi (Paket D sınav bulgusu, KUCUK) — kök nesne bir LİSTE
    # olmalı (ör. {"kayitlar": [...]} gibi makul bir kullanıcı hatası
    # KORUMASIZ TRACEBACK yerine nazik bir HATA mesajıyla durmalı; diğer tüm
    # hata dalları zaten '⚠ … atlandı' ile nazikçe geçiyor — şema hatası da
    # aynı disipline tabi olmalı).
    if not isinstance(kayitlar, list):
        print("HATA: --pencereler JSON kök nesnesi bir LİSTE olmalı "
              '([{ad,teblig,...}, ...]) — bulunan: ' + type(kayitlar).__name__)
        sys.exit(1)

    pencereler = []
    atlanan = []  # DÜZELTME (Ş13, v0.5.5 şerh turu): düşen HER kayıt burada iz bırakır
    for k in kayitlar:
        if not isinstance(k, dict):
            sebep = f"liste öğesi sözlük değil ({type(k).__name__})"
            print(f"  ⚠ {sebep} — atlandı")
            atlanan.append({"ad": "(bilinmiyor)", "sebep": sebep})
            continue
        ad = k.get("ad") or "(adsız)"
        teblig_str = k.get("teblig")
        if not teblig_str:
            sebep = "'teblig' alanı eksik"
            print(f"  ⚠ '{ad}': {sebep} — atlandı")
            atlanan.append({"ad": ad, "sebep": sebep})
            continue
        try:
            teblig = date.fromisoformat(teblig_str)
        except Exception:
            sebep = f"geçersiz teblig tarihi '{teblig_str}'"
            print(f"  ⚠ '{ad}': {sebep} — atlandı")
            atlanan.append({"ad": ad, "sebep": sebep})
            continue
        yargi = k.get("yargi", "hukuk")
        tur = k.get("tur", "usul")
        adli_tatil_istisna = bool(k.get("adli_tatil_istisna"))
        if k.get("kural"):
            if k["kural"] not in KURALLAR:
                sebep = f"bilinmeyen kural '{k['kural']}'"
                print(f"  ⚠ '{ad}': {sebep} — atlandı")
                atlanan.append({"ad": ad, "sebep": sebep})
                continue
            # A-1 (v0.5.14) — kural ↔ yargı kolu uyuşmazlığı burada da SESSİZ
            # geçemez: pencere defteri de son gün üretir ve bindirme hükmü verir.
            _ku = kol_uyusmazligi(k["kural"], yargi)
            if _ku:
                sebep = "kural/yargı kolu uyuşmazlığı — %s" % _ku
                print(f"  ⚠ '{ad}': {sebep} — atlandı")
                atlanan.append({"ad": ad, "sebep": sebep})
                continue
            miktar, birim, _kaynak = KURALLAR[k["kural"]]
        # DÜZELTME (Ş13, v0.5.5 şerh turu): eski `k.get("sure") and k.get("birim")`
        # falsy kontrolü `sure: 0`ı 'alan eksik' sayıp SESSİZCE düşürüyordu (0
        # sayısal olarak geçerli bir süre DEĞİLSE bile — ör. yanlışlıkla girilen
        # bir 0 — en azından 'alan eksik' YALANINI SÖYLEMEMELİ). `is not None`
        # ile yalnız GERÇEKTEN eksik/None alan 'eksik' sayılır.
        elif k.get("sure") is not None and k.get("birim"):
            miktar, birim = k["sure"], k["birim"]
        else:
            sebep = "'kural' VEYA 'sure'+'birim' eksik"
            print(f"  ⚠ '{ad}': {sebep} — atlandı")
            atlanan.append({"ad": ad, "sebep": sebep})
            continue
        try:
            son, _rapor, _uyarilar = hesapla(teblig, miktar, birim, yargi, tur,
                                             adli_tatil_istisna, None, k.get("kural"))
        except Exception as e:
            sebep = f"hesaplama hatası ({e})"
            print(f"  ⚠ '{ad}': {sebep} — atlandı")
            atlanan.append({"ad": ad, "sebep": sebep})
            continue
        bas = teblig + timedelta(days=1)
        pencereler.append({"ad": ad, "bas": bas.isoformat(), "son": son.isoformat()})

    print("=" * 68)
    print("  SÜRE PENCERE BİNDİRME KONTROLÜ (M5, Paket D — v0.5.5)")
    print("=" * 68)
    for pe in pencereler:
        print(f"  {pe['ad']}: {pe['bas']} .. {pe['son']}")

    bindirmeler = []
    for i in range(len(pencereler)):
        for j in range(i + 1, len(pencereler)):
            a_, b_ = pencereler[i], pencereler[j]
            bas_a, son_a = date.fromisoformat(a_["bas"]), date.fromisoformat(a_["son"])
            bas_b, son_b = date.fromisoformat(b_["bas"]), date.fromisoformat(b_["son"])
            if bas_a <= son_b and bas_b <= son_a:
                bindirmeler.append((a_["ad"], b_["ad"]))

    # DÜZELTME (Ş13, v0.5.5 şerh turu BLOKER — fail-open yanlış temiz-ışık):
    # eskiden hayatta kalan pencere sayısına HİÇ BAKILMADAN `bindirmeler`
    # boşsa '>>> Bindirme yok — pencereler ayrık. <<<' basılıyordu — bu,
    # SIFIR kayıt çözülse (ör. tüm kayıtlar bozuk/eksikse) ya da yalnız TEK
    # kayıt hayatta kalsa (bindirme yapısal olarak İMKÂNSIZ) bile AYNI 'temiz'
    # OLGU BEYANINI üretiyordu — 'mekanik körlüğü olgu beyanına ÇEVİRME'
    # doktrininin (bkz. dilekce_denetim.py) bu sürümdeki ihlaliydi. Üç ayrı
    # hüküm: (a) 0 pencere → DENETLENEMEDİ + exit != 0 (girdi verilmişken
    # sessiz 'başarı' YOK); (b) 1 pencere → yapısal olarak denetlenemez
    # (bindirme TANIM GEREĞİ yoktur, ama bu bir 'ayrık' KANITI DEĞİLDİR);
    # (c) ≥2 pencere → mevcut hükme (varsa) düşen-kayıt şerhi eklenir.
    print()
    if not pencereler:
        print(f">>> BİNDİRME DENETLENEMEDİ — hiçbir kayıt çözülemedi "
              f"({len(atlanan)} kayıt düştü); bu sonuç KANIT SAYILMAZ. <<<")
        denetlenemedi = True
    elif len(pencereler) == 1:
        print(f">>> Tek pencere ('{pencereler[0]['ad']}') — bindirme yapısal olarak "
              "denetlenemez (karşılaştırılacak ikinci bir pencere yok). <<<")
        denetlenemedi = False
    else:
        denetlenemedi = False
        if bindirmeler:
            print("--- BİNDİRME (üst üste binen pencereler) ---")
            for x, y in bindirmeler:
                print(f"  ⚠ '{x}' ile '{y}' PENCERELERİ ÇAKIŞIYOR — aynı dönemde iki ayrı "
                      "süre birden işliyor; önceliklendirme/çakışan iş yükü avukat "
                      "gözüyle değerlendirilmeli.")
        else:
            ek = f" (NOT: {len(atlanan)} kayıt DÜŞTÜ — kapsam eksik, bu hüküm yalnız " \
                 "hayatta kalan pencerelere dayanır.)" if atlanan else ""
            print(">>> Bindirme yok — pencereler ayrık. <<<" + ek)
    print("=" * 68)

    if cikti_yol:
        with open(cikti_yol, "w", encoding="utf-8") as f:
            json.dump({"pencereler": pencereler,
                      "bindirmeler": [{"a": x, "b": y} for x, y in bindirmeler],
                      "atlanan": atlanan,
                      "denetlenen_kayit": len(pencereler)},
                     f, ensure_ascii=False, indent=2)
        print(f"[JSON] {cikti_yol}")

    if denetlenemedi:
        sys.exit(1)


def _sure_flagini_yaz(kok, son_gunler, aciklama_taban, kural, tur):
    """E4a (v0.5.8.5) — SÜRE BAĞI: hesaplanan son gün(ler) <kok>/_oa varsa
    `_oa/sureler.json`a OTOMATİK flag olarak işlenir (halüsinasyon çıpası —
    hesap yapıldı ama deftere hiç yazılmadı boşluğu kapanır). Kayıt biçimi
    oa_hafiza.py `cmd_sure_flag` ŞEMASIYLA BİREBİR aynıdır (son_gun kanonik +
    geriye-uyumlu tarih alanı; sure_nobetci.py aynı defteri okur) — subprocess
    AÇILMAZ, doğrudan İN-PROCESS json yazımı yapılır (kapı-kapıyı-subprocess'le-
    çağırmaz kuralıyla simetrik). <kok>/_oa YOKSA hiçbir şey yazılmaz (dava
    kökü değildir; defter İCAT EDİLMEZ) — dönüş (None, sebep). Aynı
    (son_gun, aciklama) çifti defterde zaten varsa TEKRAR eklenmez (tekrar
    koşu defteri şişirmez). Dönüş: (yeni_eklenen_listesi, defter_yolu|sebep)."""
    oa = os.path.join(kok, "_oa")
    if not os.path.isdir(oa):
        return None, f"{oa} yok — otomatik flag yazılmadı (dava kökü değil)"
    syol = os.path.join(oa, "sureler.json")
    try:
        with open(syol, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        d = {"flagler": []}
    if not isinstance(d, dict):
        d = {"flagler": []}
    if not isinstance(d.get("flagler"), list):
        d["flagler"] = []
    yeni = []
    for tarih_iso, acik in son_gunler:
        acik = acik or aciklama_taban
        if any((f.get("son_gun") or f.get("tarih")) == tarih_iso
               and f.get("aciklama") == acik
               for f in d["flagler"] if isinstance(f, dict)):
            continue   # aynı hesap ikinci koşuda çoğalmaz
        kayit = {"son_gun": tarih_iso, "tarih": tarih_iso, "aciklama": acik,
                 "kural": kural,
                 "kayit": _datetime.datetime.now().isoformat(timespec="seconds"),
                 "tur": tur}
        d["flagler"].append(kayit)
        yeni.append(tarih_iso)
    if yeni:
        d["flagler"].sort(key=lambda x: (x.get("son_gun") or x.get("tarih") or "")
                          if isinstance(x, dict) else "")
        with open(syol, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
    return yeni, syol


def main():
    p = argparse.ArgumentParser(description="Deterministik Türk usul/maddi süre hesaplayıcı (v3)")
    p.add_argument("--teblig", help="Başlangıç tarihi: usulde tebliğ/öğrenme; maddi hukukta muacceliyet/öğrenme/fiil (YYYY-MM-DD)")
    p.add_argument("--sure", type=int); p.add_argument("--birim", choices=["gun","hafta","ay","yil"])
    p.add_argument("--kural", choices=list(KURALLAR.keys()))
    p.add_argument("--yargi", choices=["hukuk","idari","ceza"], default="hukuk",
                   help="Yargı kolu — ADLİ TATİL REJİMİNİ belirler: hukuk = HMK m.104 "
                        "(31 Ağu + 1 hafta); idari = İYUK m.8/3 (1 Eylül'den 7 gün); "
                        "ceza = CMK m.331/4 (tatilin bittiği günden ÜÇ GÜN). cmk_* kuralları "
                        "YALNIZ --yargi ceza ile koşulur (aksi hâlde hesap DURUR).")
    p.add_argument("--tur", choices=["usul","maddi"], default="usul",
                   help="usul = kanun yolu/başvuru süresi (adli tatil uygulanır); "
                        "maddi = zamanaşımı/hak düşürücü (TBK/TMK/TTK/6183 vb. — adli tatil uygulanmaz)")
    p.add_argument("--baslangic-turu", dest="baslangic_turu",
                   choices=["teblig", "tefhim", "ogrenme", "olay", "belirsiz"],
                   default=None,
                   help="v0.5.13 — süreyi başlatan OLAYIN türü (opsiyonel; aritmetiği "
                        "DEĞİŞTİRMEZ, çıktıda görünür kılar). Aynı dosyada iki rejim "
                        "yaşayabilir: CMK m.268 itiraz ÖĞRENME gününden, m.273/291 "
                        "istinaf-temyiz GEREKÇELİ KARARIN TEBLİĞİNDEN işler. "
                        "'belirsiz' verilirse iki senaryo uyarısı düşer ve plan ERKEN "
                        "tarihe göre yapılır.")
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
    p.add_argument("--pencereler", metavar="JSON",
                   help="M5 (Paket D): SÜRE PENCERE BİNDİRME kontrolü — birden çok "
                        "{ad,teblig,(kural|sure+birim),[yargi,tur,adli_tatil_istisna]} kaydı "
                        "taşıyan bir JSON dosyasını okur, her birini hesapla() ile çözer ve "
                        "[teblig+1, son_gün] pencerelerinin PAIRWISE çakışıp çakışmadığını raporlar.")
    p.add_argument("--pencereler-json", dest="pencereler_json_cikti", metavar="YOL",
                   help="--pencereler ile: sonucu makine-okur JSON olarak bu yola da yaz")
    p.add_argument("--kok", default=".",
                   help="E4a SÜRE BAĞI: çalışma kökü — <kok>/_oa VARSA hesaplanan son gün "
                        "_oa/sureler.json'a OTOMATİK flag olarak işlenir (oa_hafiza sure-flag "
                        "şeması; sure_nobetci.py aynı defteri okur). _oa yoksa yazılmaz.")
    p.add_argument("--aciklama", default=None,
                   help="otomatik süre flag'i açıklaması (verilmezse kural/süre metninden türetilir)")
    p.add_argument("--flagsiz", action="store_true",
                   help="otomatik sureler.json flag yazımını kapat (yalnız hesap yap)")
    a = p.parse_args()
    if a.pencereler:
        _pencere_kontrol(a.pencereler, a.pencereler_json_cikti)
        return
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
    # B-22 (v0.5.14) — gg.aa.yyyy alışkanlığı ve tipografik hatalar ham
    # ValueError/traceback üretiyordu; avukat hatanın kendisinde mi araçta mı
    # olduğunu ayırt edemiyordu. Artık argparse'ın kendi temiz hata yolu.
    try:
        teblig = date.fromisoformat(a.teblig)
    except ValueError as e:
        p.error("--teblig geçersiz tarih: %r (%s). Beklenen biçim YYYY-AA-GG "
                "(ör. 2026-05-20) — gg.aa.yyyy KABUL EDİLMEZ." % (a.teblig, e))
    kaynak=None
    if a.kural:
        # A-1 (P0) — SESSİZ YANLIŞ VARSAYILAN YASAK: kural ile yargı kolu
        # uyuşmuyorsa hesap hiç yapılmaz. Uyarı basıp devam etmek yetmez;
        # ">>> HESAPLANAN SON GÜN" satırı ve otomatik defter flag'i yanlış
        # tarihi kalıcılaştırır (ve sure_nobetci onu otorite sayar).
        _uyusmazlik = kol_uyusmazligi(a.kural, a.yargi)
        if _uyusmazlik:
            p.error("KURAL ↔ YARGI KOLU UYUŞMAZLIĞI — hesap DURDURULDU (yanlış son gün "
                    "üretilmedi, deftere hiçbir şey yazılmadı).\n  %s" % _uyusmazlik)
        miktar,birim,kaynak = KURALLAR[a.kural]
        if a.kural.startswith("iyuk") and a.yargi!="idari":
            print("ⓘ Not: İYUK kuralı; --yargi idari önerilir (çalışmaya ara mekaniği). "
                  "Uzatma aritmetiği hukuk koluyla aynı sonucu verdiği için hesap DURDURULMADI.")
    elif a.sure is not None and a.birim:
        # B-16 — eski `a.sure and a.birim` kontrolü `--sure 0`ı falsy görüp
        # "alan eksik" YALANINI söylüyordu (kullanıcı alanı VERMİŞTİ).
        miktar,birim = a.sure,a.birim
        _mh = miktar_dogrula(miktar, birim)
        if _mh:
            p.error("--sure geçersiz: %s" % _mh)
    else:
        p.error("Ya --kural ver ya da --sure + --birim birlikte ver.")
    try:
        son,rapor,uyarilar = hesapla(teblig,miktar,birim,a.yargi,a.tur,a.adli_tatil_istisna,
                                     getattr(a, "baslangic_turu", None), a.kural)
    except (ValueError, OverflowError) as e:
        # B-22 — uç tarih/miktarda ham traceback yerine temiz mesaj.
        p.error("hesap yapılamadı: %s" % e)
    # ── E-TEBLİGAT / UETS (7201 m.7/a): ulaşma+5. gün karine senaryosunu çift hesapla ─
    son_karine = None
    if a.uets:
        # A-4 (v0.5.14) — E-TEBLİĞ DAYANAĞI KURALA GÖRE SEÇİLİR. Aritmetik her iki
        # rejimde de aynıdır (beşinci günün sonu), bu yüzden dayanak hatası sessiz
        # kalıyordu — ama dilekçeye yanlış norm giriyordu. MCP teyitli 2026-08-31:
        #   7201 m.7/a  : "...elektronik adresine ULAŞTIĞI tarihi izleyen beşinci günün sonunda..."
        #   VUK m.107/A : "...bu sistem ile muhatabına İLETİLDİĞİ tarihi izleyen beşinci günün
        #                  sonunda..." (Değişik: 24/6/2026-7587/9 md.)
        _vergi_kanadi = a.kural in ("iyuk_dava_vergi", "amme_6183_m58")
        if _vergi_kanadi:
            _dayanak = ("VUK m.107/A (vergi idaresinin elektronik tebligatı; Değişik: 24/6/2026-7587 s.K.) "
                        "— tebliğ, sistemle muhatabına İLETİLDİĞİ tarihi izleyen 5. günün sonunda yapılmış sayılır")
            _dayanak_kisa = "VUK m.107/A"
        else:
            _dayanak = ("7201 s.K. m.7/a (UETS üzerinden adli/idari tebligat) — tebligat, muhatabın "
                        "elektronik adresine ULAŞTIĞI tarihi izleyen 5. günün sonunda yapılmış sayılır")
            _dayanak_kisa = "7201 m.7/a"
        karine_teblig = teblig + timedelta(days=5)
        son_karine, _rk, uyarilar_karine = hesapla(karine_teblig, miktar, birim, a.yargi,
                                                   a.tur, a.adli_tatil_istisna, None, a.kural)
        rapor.append("")
        rapor.append("── E-TEBLİGAT (UETS/e-tebligat) — İKİ SENARYO (çift hesap) ─────────")
        rapor.append(f"Dayanak               : {_dayanak}.")
        if _vergi_kanadi:
            rapor.append("    (Adli tebligat 7201 m.7/a'ya tabidir; burada VERGİ kanadı kuralı seçildiği için")
            rapor.append("     VUK m.107/A gösterildi — dosyada fiilen hangi rejimin uygulandığını TEYİT ET.)")
        rapor.append(f"UETS Senaryo-1 (ulaşma/iletilme günü esas): teblig={teblig.isoformat()} "
                     f"→ son gün {son.isoformat()} ({_gun_adi(son)})")
        rapor.append(f"UETS Senaryo-2 (karine: ulaşma+5. gün sonu): teblig={karine_teblig.isoformat()} "
                     f"→ son gün {son_karine.isoformat()} ({_gun_adi(son_karine)})")
        rapor.append("    GÜVENLİ TARAF — AMACA GÖRE AYRILIR (tek tanım):")
        rapor.append(f"    · BİZİM süremizde (kanun yolu/başvuru): güvenli taraf ERKEN son gündür — {son.isoformat()}")
        rapor.append("      (Senaryo-1). Karine senaryosu tanım gereği 5 gün DAHA GEÇtir; ona güvenip beklemek,")
        rapor.append(f"      girilen tarih zaten TEBLİĞ-SAYILMA tarihiyse süreyi 5 gün AŞMAK demektir. İşlemi")
        rapor.append(f"      {son.isoformat()} tarihine göre planla.")
        rapor.append("    · KARŞI TARAFA kesin dil kurarken: 'süre kaçırılmıştır' YALNIZ her iki senaryo da")
        rapor.append("      aşılmışsa yazılır (karine hukuken geçerli tebliğ tarihidir) — bkz. --islem denetimi.")
        rapor.append(f"    Ayrım: ULAŞMA/İLETİLME tarihi ≠ TEBLİĞ-SAYILMA tarihi. Hangisinin girildiğini")
        rapor.append(f"    UYAP/UETS kaydından BELGELİ teyit et; {_dayanak_kisa} metnini kullanım anında MCP'den doğrula.")
        uyarilar.append(
            "UETS/E-TEBLİGAT (%s): İki son gün üretildi. BİZİM süremizde güvenli taraf ERKEN "
            "olan son gündür (%s) — geç senaryoya (karine, %s) güvenmek hak kaybettirir. Karşı tarafa "
            "yönelik KESİN dil ise ancak HER İKİ senaryo da aşılmışsa kurulur. Süre başlangıç anını "
            "(ulaşma/iletilme tarihini) UYAP/UETS kaydından BELGELİ teyit et; ulaşma günü ile 5. gün "
            "karinesini karıştırma." % (_dayanak_kisa, min(son, son_karine).isoformat(),
                                        max(son, son_karine).isoformat()))
        # Senaryo-2 (karine) hesabının KENDİ uyarılarından Senaryo-1'den farklı olanları da rapora taşı
        # (ör. karine tebliğ tarihi farklı bir idari izin/bayram penceresine düşebilir — sessizce atılmaz).
        _farkli_uk = [u for u in uyarilar_karine if u not in uyarilar]
        if _farkli_uk:
            rapor.append("    Senaryo-2 (karine) hesabına özgü ek uyarı(lar) — aşağıya işlendi.")
            for _u in _farkli_uk:
                uyarilar.append(f"[UETS Senaryo-2/karine] {_u}")
    # ── SÜRE DENETİMİ (--islem): süresinde mi, kaçırıldı mı (özellikle KARŞI TARAF) ──
    if a.islem:
        try:   # B-22 — --islem de temiz hata versin
            islem = date.fromisoformat(a.islem)
        except ValueError as e:
            p.error("--islem geçersiz tarih: %r (%s). Beklenen biçim YYYY-AA-GG."
                    % (a.islem, e))
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
    if _KURAL_TABLO_YOK:
        # B-21 (v0.5.14) — eskiden bu düşüş SESSİZDİ: kullanıcı "teyit BOŞ" satırı
        # ile kaynak metnindeki "(MCP teyit ...)" şerhini aynı ekranda görüp hangisine
        # inanacağını bilemiyordu. Artık düşüşün SEBEBİ ilk satırda yazılı.
        print("⚠ KURAL TABLOSU: gömülü (fallback) tabloya düşüldü — sebep: %s"
              % (_KURAL_TABLO_SEBEP or "bilinmiyor"))
        print("  Gömülü tablo ile sure_kurallari.json BİREBİR aynı tutulur (test kilidi:")
        print("  test_v0514_sure.py::test_B21_gomulu_ve_json_kural_tablosu_BIREBIR_ayni),")
        print("  ancak JSON güncellemeleri bu koşuda GÖRÜLMEMİŞTİR — dosyayı onar.")
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
    # ── E4a SÜRE BAĞI (v0.5.8.5): hesap çıktısı üretilirken flag OTOMATİK yazılır ──
    # Boşluk sahada ölçüldü: hesap yapılıyor ama sureler.json'a işleme adımı (elle
    # oa_hafiza sure-flag) atlanıyordu → nöbetçi hiç görmüyordu. Artık <kok>/_oa
    # varsa son gün deftere İN-PROCESS işlenir; --uets'te karine senaryosu da ayrı
    # kayıt olur (kayıpsızlık: iki son gün de görünür). Yazım BLOKLAMAZ: defter
    # hatası hesabı düşürmez, açıkça raporlanır.
    if a.flagsiz:
        print("ⓘ --flagsiz: otomatik sureler.json flag yazımı istekle KAPALI.")
    else:
        _acik_taban = a.aciklama or ((kaynak or f"{miktar} {birim} süre") + " — son gün")
        _adaylar = [(son.isoformat(), a.aciklama)]
        if son_karine is not None:
            _adaylar.append((son_karine.isoformat(),
                             (a.aciklama or _acik_taban) + " [UETS karine: ulaşma+5. gün]"))
        try:
            _yeni, _bilgi = _sure_flagini_yaz(a.kok, _adaylar, _acik_taban, a.kural, a.tur)
        except Exception as _e:   # yazım hesabı ASLA düşürmez — açık rapor, sessiz değil
            print(f"UYARI: süre flag'i yazılamadı ({_e}) — oa_hafiza.py sure-flag ile ELLE işle.")
        else:
            if _yeni is None:
                print(f"ⓘ SÜRE BAĞI: {_bilgi}; dava kökünde `--kok <klasör>` ile koş "
                      "ya da oa_hafiza.py sure-flag ile elle işle.")
            elif _yeni:
                print(f"SÜRE FLAG'İ OTOMATİK İŞLENDİ ({', '.join(_yeni)}): {_bilgi}")
                print("(sure_nobetci.py --kok . bu deftere göre GEÇMİŞ/YAKLAŞAN son günü tarar.)")
            else:
                print(f"ⓘ SÜRE BAĞI: aynı son gün + açıklama defterde ZATEN kayıtlı — tekrar eklenmedi ({_bilgi}).")
    print("NOT: event_create/reminder_create ÇAĞRILMAZ; dış takvim/hatırlatıcı eşgüdümü AVUKAT")
    print("tarafından ELLE yapılır — araç yoksa/kurulamıyorsa bu açıkça raporlanır (disk pasiftir,")
    print("kimseyi dürtmez). _oa/dosya.md süre özetini de güncelle.")

if __name__=="__main__":
    try: main()
    except BrokenPipeError: sys.stderr.close()

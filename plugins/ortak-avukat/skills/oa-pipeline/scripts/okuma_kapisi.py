#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
okuma_kapisi.py — GATE B: OKUMA KAPISI (M1-3, Denizli canlı testinden çıktı)

AMAÇ: `oa_ingest.py`'nin ürettiği `_oa/metin/00-INDEX.md` + `00-kunye.json`
(+ Gate A `<taban>.harita.json` sayfa/bölüm haritaları) üzerinden bir alt-ajana
"öncelikli evrak listesi + büyük-evrak uyarısı" üretir. SADECE MEKANİK: künyedeki
alanları (tür~ tahmini, karakter, buyuk, harita) okuyup SABİT bir kurala göre
dizer; içerik OKUMAZ, içerik hakkında "iyi/kötü/ilgili/olmuştur" YARGISI VERMEZ
(model kurar, script denetler ayrımı — bkz. anayasa.md). Öncelik sırası, usulün
esasa takaddüm ettiği anayasal düsturun sabit bir tablo hâlidir (tebligat/süre
önce); bu bir MUHAKEME değil, dosya adından türeyen `tur_tahmini` (Gate C)
alanına uygulanan SABİT sıra numarasıdır.

GATE B — İKİ İŞLEV:
  (1) ÖNCELİKLİ OKUMA LİSTESİ: künyeyi tur_tahmini sırasına göre diz, OCR/⚠
      ve BÜYÜK (>eşik anlamlı karakter) damgalarını taşı; büyük evrak için
      "haritadan oku, tam yükleme" uyarısı ver.
  (2) TAM-YÜKLEME DEDUP DEFTERİ (`_oa/defter/tam-yukleme.jsonl`, append-only):
      bir alt-ajan büyük bir evrağı GERÇEKTEN tam yüklediğinde
      `--tam-yukle-kaydet` ile deftere loglar; AYNI büyük evrak İKİNCİ kez tam
      yüklenmek istenirse script yalnız UYARIR — BLOKLAMAZ (advisory). Konu
      gerçekten gerektiriyorsa alt-ajan fazlasını/tamamını okuyabilir; derinlik
      hiçbir zaman kısılmaz — bu yalnız "önce haritaya bak, sonra bilinçli seç"
      disiplinidir.

  (3) KRİTİK EVRAK → SÜRE ADAYI (v0.5.16/E — P1-10/A-4): künyedeki evraklar
      arasında tür/ad sınıfı tebligat | tebliğ mazbatası | ara karar | tensip |
      bilirkişi raporu | gerekçeli karar | ödeme emri | ihbarname olanlar
      "SÜRE ADAYI" işaretlenir; evrağın .md metninden dd.mm.yyyy / dd/mm/yyyy
      tarihleri, "tebliğ | tebellüğ | karar tarihi | düzenleme tarihi" komşuluğu
      (±80 karakter) ile ADVISORY tarih adayı olarak çıkarılır. `--sure-adaylari`
      → stdout tablo + `_oa/cikti/00-sure-adaylari.json`. Script `sure-flag`
      YAZMAZ: yalnız `oa_hafiza.py sure-flag … (avukat onayıyla)` komutunu
      ÖNERİR — süre kuralını ve son günü seçmek muhakemedir (oa-sure + Mevzuat
      MCP teyidi + avukat), mekanik tarama değil. Künyede `tur_tahmini` yoksa
      dosya adı + md'nin ilk 600 karakterinden `tur_tahmin` (advisory) üretilir.

Kullanım:
  python okuma_kapisi.py [--kok KLASÖR] [--esik N]
  python okuma_kapisi.py [--kok KLASÖR] --json CIKTI.json
  python okuma_kapisi.py [--kok KLASÖR] --sure-adaylari
  python okuma_kapisi.py [--kok KLASÖR] --tam-yukle-kaydet "<kaynak>" [--ajan "oa-x"]
  python okuma_kapisi.py [--kok KLASÖR] --tam-yukle-defter

--kok: çalışma kökü (oa_hafiza.py/tam_tur.py/pipeline_kayit.py simetrisi;
verilmezse CWD). `_oa/metin/00-kunye.json` buradan aranır — Claude Code
alt-ajan thread'lerinde cwd sıfırlandığından mutlak --kok önerilir.

Çıkış kodu: 0 = normal; 1 = künye bulunamadı (önce oa-ingest koşulmalı) veya
kullanım hatası. `--tam-yukle-kaydet`/`--tam-yukle-defter` her hâlde 0 döner
(advisory — teslim engeli DEĞİL).
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse, datetime, json, os, re, sys

BUYUK_ESIK_VARSAYILAN = 40000  # oa_ingest.py BUYUK_ESIK_KARAKTER ile aynı varsayılan

# ═════════════════════════════════════════════════════════════════════════
# (3) KRİTİK EVRAK → SÜRE ADAYI (v0.5.16/E — P1-10 / A-4)
# MEKANİK: ad/tür/ilk-600-karakter üzerinde anahtar eşlemesi + tarih regex'i.
# Hangi sürenin işlediği, başlangıcın tebliğ mi tefhim mi olduğu, adli tatil,
# UETS — hepsi MUHAKEMEDİR (oa-sure + Mevzuat MCP + avukat). Bu script yalnız
# "şu evrak süre başlatabilir, şu tarihler tebliğ/karar sözcüğünün yanında
# geçiyor" der; kesinlik iddia etmez, sure-flag YAZMAZ.
# ═════════════════════════════════════════════════════════════════════════
_TR_KATLA = {"ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g", "ı": "i", "İ": "i",
             "ö": "o", "Ö": "o", "ş": "s", "Ş": "s", "ü": "u", "Ü": "u"}


def _katla(s):
    """Türkçe harfleri ASCII'ye katla + küçült (oa_ingest._ascii_kucuk ile aynı sözleşme)."""
    return "".join(_TR_KATLA.get(c, c) for c in (s or "")).lower()


# Sıralı liste — İLK eşleşen kazanır (deterministik). Anahtarlar KATLANMIŞ
# (ASCII-küçük) metne uygulanır; boşluk/tire/alt çizgi farkı için birkaç varyant.
SURE_ADAYI_SINIFLARI = [
    ("tebligat",        ("teblig mazbata", "tebligat", "teblig")),
    ("gerekceli_karar", ("gerekceli karar", "gerekceli_karar", "gerekceli-karar", "gerekceli")),
    ("ara_karar",       ("ara karar", "ara_karar", "ara-karar", "arakarar")),
    ("tensip",          ("tensip",)),
    ("bilirkisi_raporu", ("bilirkisi rapor", "bilirkisi", "bilirkis")),
    ("odeme_emri",      ("odeme emri", "odeme_emri", "odeme-emri", "odemeemri")),
    ("ihbarname",       ("ihbarname",)),
    # Gate C 'karar' tahmini (karar/ilam/hukum) — gerekçeli olduğu belli değil; yine
    # de süre adayıdır (kanun yolu süresi tebliğle işleyebilir) → en düşük özgüllük.
    ("karar",           ("ilam", "hukum", "karar")),
]
# Gate C `tur_tahmini` → süre adayı sınıfı (künye zaten tahmin etmişse ad taranmaz).
_TUR_TAHMINI_ESLEME = {"tebligat": "tebligat", "bilirkisi": "bilirkisi_raporu", "karar": "karar"}

# Sınıf → oa-sure kataloğu (`sure_kurallari.json`) anahtar ÖNERİSİ + kısa not.
# Normlar Mevzuat MCP teyitlidir (2026-09-06): HMK m.345/1 (istinaf iki hafta,
# ilamın tebliğinden), HMK m.281/1 (bilirkişi raporuna tebliğden iki hafta),
# CMK m.273/1 (istinaf, hükmün gerekçesiyle tebliğinden iki hafta), İYUK m.45/1
# (BİM istinaf 30 gün), İYUK m.7/1 (dava: idare 60 / vergi 30 gün), İİK m.62/1
# (ödeme emrine itiraz tebliğden 7 gün), 6183 m.58/1 (amme ödeme emrine itiraz
# 15 gün). Anahtar listesi "aday"dır — yargı kolunu ve somut kuralı AVUKAT seçer;
# katalogda karşılığı olmayan süre için hesapla_sure.py --sure/--birim ile elle.
SURE_ADAYI_ONERI = {
    "tebligat":        {"kural": [], "not": "tebliğ mazbatası süreyi BAŞLATIR; hangi sürenin "
                                            "işlediği tebliğ edilen belgeye bağlıdır (o evrağa bak)"},
    "gerekceli_karar": {"kural": ["hmk_istinaf", "cmk_istinaf", "iyuk_istinaf"],
                        "not": "kanun yolu süresi tebliğle işler — yargı koluna göre HMK m.345 / "
                               "CMK m.273 / İYUK m.45 (Mevzuat MCP teyit 2026-09-06)"},
    "karar":           {"kural": ["hmk_istinaf", "cmk_istinaf", "iyuk_istinaf"],
                        "not": "karar/ilam — gerekçeli mi, tebliğ edildi mi belgeden doğrula; "
                               "kanun yolu süresi adayı"},
    "ara_karar":       {"kural": [], "not": "ara karar — kesin süre/duruşma günü içerebilir; "
                                            "belgeden okunur (avukat)"},
    "tensip":          {"kural": [], "not": "tensip — kesin süre/duruşma günü/delil ibraz süresi "
                                            "içerebilir; belgeden okunur (avukat)"},
    "bilirkisi_raporu": {"kural": [], "not": "HMK m.281/1: rapora itiraz tebliğden iki hafta "
                                             "(Mevzuat MCP teyit 2026-09-06) — katalogda anahtar "
                                             "yok: hesapla_sure.py --sure 2 --birim hafta"},
    "odeme_emri":      {"kural": ["amme_6183_m58"],
                        "not": "İİK m.62/1: genel haciz ödeme emrine itiraz tebliğden 7 gün "
                               "(katalogda anahtar yok, elle); 6183 m.58/1: amme alacağında "
                               "15 gün (Mevzuat MCP teyit 2026-09-06) — hangisi olduğu belgeden"},
    "ihbarname":       {"kural": ["iyuk_dava_vergi", "iyuk_dava_idare"],
                        "not": "İYUK m.7/1: vergi mahkemesinde 30, idare mahkemesinde 60 gün "
                               "(Mevzuat MCP teyit 2026-09-06); uzlaşma/düzeltme yolları ayrıca"},
}

_TARIH_RE = re.compile(r"(?<!\d)(\d{1,2})[./](\d{1,2})[./](\d{4})(?!\d)")
# Tarih komşuluğunda aranan çıpalar (katlanmış metne uygulanır). Sıra = raporlanan etiket.
_TARIH_CIPALARI = [
    ("tebellüğ", "tebellug"),
    ("tebliğ", "teblig"),
    ("karar tarihi", "karar tarihi"),
    ("düzenleme tarihi", "duzenleme tarihi"),
]
TARIH_KOMSULUK = 80          # ± karakter
TUR_TAHMIN_ILK_KARAKTER = 600


def _sure_adayi_sinifi(k, md_ilk=None):
    """Bir künye kaydı için (sinif, tur_tahmin, tur_tahmin_kaynak) döndürür.
    Öncelik: (1) künyedeki `tur_tahmini` (Gate C) eşlemesi; (2) ad + kaynak taraması;
    (3) tur_tahmini YOKSA ad + md'nin ilk 600 karakteri → `tur_tahmin` (advisory,
    kaynak "ad+md600"). Eşleşme yoksa (None, None, None) — 'diğer' UYDURULMAZ."""
    tt = k.get("tur_tahmini")
    if tt and tt in _TUR_TAHMINI_ESLEME:
        return _TUR_TAHMINI_ESLEME[tt], None, None
    ad_metin = _katla(f"{k.get('ad') or ''} {k.get('kaynak') or ''}")
    for sinif, anahtarlar in SURE_ADAYI_SINIFLARI:
        if any(a in ad_metin for a in anahtarlar):
            return sinif, None, None
    if tt is None and md_ilk:
        govde = _katla(md_ilk[:TUR_TAHMIN_ILK_KARAKTER])
        for sinif, anahtarlar in SURE_ADAYI_SINIFLARI:
            if any(a in govde for a in anahtarlar):
                return sinif, sinif, "ad+md600"
    return None, None, None


def _md_govde_oku(kok, md):
    """`_oa/metin/<md>` gövdesini (başlık bloğundan sonrasını) okur; yoksa ''."""
    if not md:
        return ""
    yol = os.path.join(_oa_kok(kok), "metin", md)
    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            icerik = f.read()
    except OSError:
        return ""
    _bas, ayrac, kuyruk = icerik.partition("\n---\n")
    return kuyruk if ayrac else icerik


def _tarih_gecerli(g, a, y):
    try:
        datetime.date(int(y), int(a), int(g))
        return True
    except ValueError:
        return False


def _tarih_adaylari(metin, en_fazla=12):
    """md metninden ÇIPALI tarih adayları: dd.mm.yyyy / dd/mm/yyyy biçimindeki her
    tarih için ±TARIH_KOMSULUK karakterlik pencere katlanır ve _TARIH_CIPALARI
    aranır; çıpasız tarihler ADAY DEĞİLDİR (yalnız sayılır → `cipasiz_tarih`).
    Aynı tarih+çıpa çifti bir kez raporlanır. Advisory: tarih 'tebliğ' sözcüğünün
    yanında geçiyor diye tebliğ tarihi OLMAYABİLİR — orijinalden teyit."""
    adaylar, gorulen, cipasiz = [], set(), 0
    for m in _TARIH_RE.finditer(metin or ""):
        g, a, y = m.group(1), m.group(2), m.group(3)
        if not _tarih_gecerli(g, a, y):
            continue
        bas = max(0, m.start() - TARIH_KOMSULUK)
        pencere = _katla(metin[bas:m.end() + TARIH_KOMSULUK])
        etiket = next((e for e, k in _TARIH_CIPALARI if k in pencere), None)
        if etiket is None:
            cipasiz += 1
            continue
        anahtar = (m.group(0), etiket)
        if anahtar in gorulen:
            continue
        gorulen.add(anahtar)
        adaylar.append({"tarih": m.group(0), "iso": f"{y}-{int(a):02d}-{int(g):02d}",
                        "baglam": etiket, "offset": m.start()})
        if len(adaylar) >= en_fazla:
            break
    return adaylar, cipasiz


def sure_adaylari(kunye, kok):
    """Künyeden SÜRE ADAYI listesi üretir (saf: künye + md gövdeleri → liste)."""
    cikti = []
    for k in kunye.get("kayitlar", []) if kunye else []:
        if not isinstance(k, dict):
            continue
        govde = _md_govde_oku(kok, k.get("md"))
        sinif, tur_tahmin, tt_kaynak = _sure_adayi_sinifi(k, govde)
        if not sinif:
            continue
        tarihler, cipasiz = _tarih_adaylari(govde)
        if k.get("tarih"):
            tarihler.insert(0, {"tarih": k["tarih"], "iso": None, "baglam": "dosya-adi", "offset": None})
        oneri = SURE_ADAYI_ONERI.get(sinif, {"kural": [], "not": ""})
        aday = {"evrak": k.get("kaynak"), "no": k.get("no"), "ad": k.get("ad"), "md": k.get("md") or "",
                "sinif": sinif, "tur_tahmini": k.get("tur_tahmini"),
                "teyit_gerek": bool(k.get("teyit_gerek")),
                "tarih_adaylari": tarihler, "cipasiz_tarih": cipasiz,
                "oneri_kural": list(oneri["kural"]), "not": oneri["not"]}
        if tur_tahmin:
            aday["tur_tahmin"] = tur_tahmin
            aday["tur_tahmin_kaynak"] = tt_kaynak
        cikti.append(aday)
    return cikti


def _sure_adaylari_json_yolu(kok):
    return os.path.join(_oa_kok(kok), "cikti", "00-sure-adaylari.json")


def cmd_sure_adaylari(args):
    kok = args.kok
    kunye = _kunye_oku(kok)
    if kunye is None:
        print(f"HATA: künye bulunamadı: {_kunye_yolu(kok)} — önce oa-ingest "
              "(0. MANİFEST'in AI katmanı) koşulmalı.", file=sys.stderr)
        return 1
    adaylar = sure_adaylari(kunye, kok)
    print(f"# SÜRE ADAYI TARAMASI — mekanik/advisory ({_kunye_yolu(kok)})")
    print("Kaynak: künye tür~ + dosya adı + md ilk 600 kar.; tarih = dd.mm.yyyy|dd/mm/yyyy, "
          f"±{TARIH_KOMSULUK} kar. içinde tebliğ/tebellüğ/karar tarihi/düzenleme tarihi çıpası. "
          "Bu bir MUHAKEME değildir: süre kuralı, başlangıç ve son gün oa-sure (hesapla_sure.py) "
          "+ Mevzuat MCP teyidi + AVUKAT kararıyla belirlenir. Script sure-flag YAZMAZ.")
    print()
    if not adaylar:
        print("SÜRE ADAYI: süre adayı YOK (tebligat/karar/tensip/bilirkişi/ödeme emri/ihbarname "
              "sınıfında evrak bulunamadı — bu 'süre yok' demek DEĞİLDİR; künyeye ve orijinale bak).")
    else:
        print(f"SÜRE ADAYI: {len(adaylar)} evrak")
        print("| # | Evrak | Sınıf | Tarih adayları (bağlam) | Öneri kural | Not |")
        print("|---|-------|-------|--------------------------|-------------|-----|")
        for a in adaylar:
            tarih_s = "; ".join(f"{t['tarih']} ({t['baglam']})" for t in a["tarih_adaylari"]) or "—"
            if a["cipasiz_tarih"]:
                tarih_s += f" · +{a['cipasiz_tarih']} çıpasız"
            sinif_s = a["sinif"] + (" (md600~)" if a.get("tur_tahmin") else "")
            if a["teyit_gerek"]:
                sinif_s += " ⚠OCR"
            print(f"| {a['no'] or '—'} | {a['evrak']} | {sinif_s} | {tarih_s} | "
                  f"{', '.join(a['oneri_kural']) or '—'} | {a['not']} |")
        print()
        print("ÖNERİLEN ADIMLAR (avukat onayıyla — script YAZMAZ):")
        for a in adaylar:
            ilk_iso = next((t["iso"] for t in a["tarih_adaylari"] if t.get("iso")), "YYYY-MM-DD")
            kural = a["oneri_kural"][0] if a["oneri_kural"] else "<kural|--sure N --birim gun|hafta>"
            print(f"  - {a['evrak']} [{a['sinif']}]: python oa-sure/scripts/hesapla_sure.py "
                  f"--kural {kural} --teblig {ilk_iso}  →  HESAPLANAN SON GÜN ile: "
                  f"python oa_hafiza.py sure-flag --tarih <SON GÜN> --aciklama \"{a['sinif']}: "
                  f"{a['evrak']}\" --kural {kural} (avukat onayıyla)")
    yol = _sure_adaylari_json_yolu(kok)
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    veri = {"kok": os.path.abspath(kok), "uretim": _simdi(), "kaynak_kunye": _kunye_yolu(kok),
            "advisory": True, "sure_flag_yazildi": False,
            "aciklama": ("mekanik tarama — süre kuralı/son gün oa-sure + Mevzuat MCP + avukat; "
                         "sure-flag yalnız avukat onayıyla oa_hafiza.py ile yazılır"),
            "adaylar": adaylar}
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)
    print(f"\nJSON yazıldı: {yol} (sure-flag YAZILMADI — `oa_hafiza.py sure-flag` avukat onayıyla)")
    return 0

# Mekanik öncelik sırası — oa_ingest.py Gate C'nin `tur_tahmini` alanına uygulanan
# SABİT tablo (usul/süre önce doktrini). İçerik okumaz; yalnız zaten hesaplanmış
# advisory alana bir sıra numarası verir. Listede olmayan/tahmin edilemeyen tür
# en SONA gider (varsayılan-önemli/varsayılan-önemsiz YOK — yalnız sıra kuralı).
ONCELIK_SIRASI = [
    "tebligat", "karar", "durusma_tutanagi", "bilirkisi", "dilekce",
    "istinabe", "sicil", "vekaletname", "harc_makbuz", "bilanco",
]


def _oa_kok(kok):
    return os.path.join(kok, "_oa")


def _kunye_yolu(kok):
    return os.path.join(_oa_kok(kok), "metin", "00-kunye.json")


def _index_yolu(kok):
    return os.path.join(_oa_kok(kok), "metin", "00-INDEX.md")


def _defter_dizin(kok):
    return os.path.join(_oa_kok(kok), "defter")


def _tam_yukleme_yolu(kok):
    return os.path.join(_defter_dizin(kok), "tam-yukleme.jsonl")


def _simdi():
    return datetime.datetime.now().isoformat(timespec="seconds")


def _kunye_oku(kok):
    y = _kunye_yolu(kok)
    if not os.path.exists(y):
        return None
    try:
        return json.load(open(y, encoding="utf-8"))
    except Exception:
        return None


def _oncelik_no(tur):
    try:
        return ONCELIK_SIRASI.index(tur)
    except ValueError:
        return len(ONCELIK_SIRASI)  # tahmin yok/bilinmeyen → sona (yargı değil, sıra kuralı)


def _oncelik_listesi(kunye, esik):
    """Künye kayıtlarını mekanik öncelik sırasına göre diz; büyük/OCR damgalarını
    taşı. Muhakeme YOK — yalnız kayıttaki alanları okur, sabit anahtarla sıralar."""
    kayitlar = kunye.get("kayitlar", []) if kunye else []
    sirali = sorted(
        enumerate(kayitlar),
        key=lambda t: (_oncelik_no(t[1].get("tur_tahmini")), str(t[1].get("no") or "999"), t[0]),
    )
    liste = []
    for _, k in sirali:
        buyuk = bool(k.get("buyuk")) or (k.get("karakter") or 0) > esik
        # v0.5.16/E: SÜRE ADAYI etiketi (ad/tür üzerinden — md okunmaz, ucuz; tam
        # tarama için --sure-adaylari). Eşleşme yoksa None (uydurma yok).
        sure_adayi, _tt, _ttk = _sure_adayi_sinifi(k)
        liste.append({
            "no": k.get("no"), "ad": k.get("ad"), "kaynak": k.get("kaynak"),
            "tur_tahmini": k.get("tur_tahmini"), "karakter": k.get("karakter") or 0,
            "teyit_gerek": bool(k.get("teyit_gerek")), "buyuk": buyuk,
            "harita": k.get("harita") or "", "md": k.get("md") or "",
            "sure_adayi": sure_adayi,
        })
    return liste


# ---------------- TAM-YÜKLEME DEDUP DEFTERİ (append-only jsonl) ----------------
def _tam_yukle_ekle(kok, olay):
    """Tek satırlık olayı jsonl'e ATOMİK ekle (pipeline_kayit.py olay_ekle ile
    aynı desen): dosya asla oku-değiştir-yaz edilmez, yalnız kendi satırı eklenir."""
    yol = _tam_yukleme_yolu(kok)
    ust = os.path.dirname(yol)
    if ust:
        os.makedirs(ust, exist_ok=True)
    ham = (json.dumps(olay, ensure_ascii=False) + "\n").encode("utf-8")
    fd = os.open(yol, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    kilit = None
    try:
        try:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX); kilit = "fcntl"
        except Exception:
            try:
                import msvcrt
                msvcrt.locking(fd, msvcrt.LK_LOCK, 1); kilit = "msvcrt"
            except Exception:
                kilit = None
        os.write(fd, ham)
    finally:
        try:
            if kilit == "fcntl":
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_UN)
            elif kilit == "msvcrt":
                import msvcrt
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        except Exception:
            pass
        os.close(fd)


def _tam_yukle_oku(kok):
    yol = _tam_yukleme_yolu(kok)
    olaylar = []
    if not os.path.exists(yol):
        return olaylar
    with open(yol, encoding="utf-8") as f:
        for satir in f:
            satir = satir.strip()
            if not satir:
                continue
            try:
                olaylar.append(json.loads(satir))
            except json.JSONDecodeError:
                continue
    return olaylar


def cmd_tam_yukle_kaydet(args):
    kok = args.kok
    kaynak = (args.tam_yukle_kaydet or "").strip()
    if not kaynak:
        sys.exit("HATA: --tam-yukle-kaydet için kaynak evrak adı/yolu gerekli.")
    onceki = [o for o in _tam_yukle_oku(kok) if o.get("kaynak") == kaynak]
    kunye = _kunye_oku(kok)
    buyuk_mu = None
    if kunye:
        for k in kunye.get("kayitlar", []):
            if k.get("kaynak") == kaynak:
                buyuk_mu = bool(k.get("buyuk"))
                break
    olay = {"zaman": _simdi(), "kaynak": kaynak, "ajan": args.ajan or None,
            "buyuk_kunyede": buyuk_mu}
    _tam_yukle_ekle(kok, olay)
    sayi = len(onceki) + 1
    print(f"TAM YÜKLEME KAYDEDİLDİ: {kaynak} ({sayi}. kez) — defter: {_tam_yukleme_yolu(kok)}")
    if buyuk_mu is False:
        print("NOT: bu kaynak künyede 'büyük' işaretli DEĞİL (eşik altı) — dedup uyarısı "
              "asıl büyük evrakta anlamlıdır; kayıt yine de tutuldu.")
    elif buyuk_mu is None:
        print("NOT: bu kaynak 00-kunye.json'da bulunamadı (elle girilmiş olabilir) — "
              "künye ile eşleşmedi, kayıt yine de tutuldu.")
    if sayi > 1:
        print(f"UYARI: bu evrak DAHA ÖNCE de TAM yüklenmiş ({sayi - 1} kez) — mümkünse "
              "haritadan (`<evrak>.harita.json`) ilgili sayfa/bölümü oku. Bu BLOKLAMAZ: "
              "konu gerçekten gerektiriyorsa tekrar tam yükleme MEŞRUDUR, derinlik kısılmaz; "
              "bu yalnız görünürlük için bir mekanik uyarıdır.")
    return 0


def cmd_tam_yukle_defter(args):
    kok = args.kok
    olaylar = _tam_yukle_oku(kok)
    if not olaylar:
        print(f"TAM YÜKLEME DEFTERİ boş: {_tam_yukleme_yolu(kok)}")
        return 0
    gruplar = {}
    for o in olaylar:
        gruplar.setdefault(o.get("kaynak"), []).append(o)
    print(f"# TAM YÜKLEME DEFTERİ — {_tam_yukleme_yolu(kok)}")
    for kaynak, kayitlar in sorted(gruplar.items(), key=lambda x: (-len(x[1]), x[0] or "")):
        son = kayitlar[-1]
        etiket = " ⚠ mükerrer (haritadan okumayı düşün)" if len(kayitlar) > 1 else ""
        print(f"  - {kaynak}: {len(kayitlar)} kez (son: {son.get('zaman')}, "
              f"ajan: {son.get('ajan') or '—'}){etiket}")
    return 0


# ---------------- ÖNCELİKLİ OKUMA LİSTESİ ----------------
def cmd_liste(args):
    kok = args.kok
    kunye = _kunye_oku(kok)
    if kunye is None:
        print(f"HATA: künye bulunamadı: {_kunye_yolu(kok)} — önce oa-ingest "
              "(0. MANİFEST'in AI katmanı) koşulmalı.", file=sys.stderr)
        return 1

    esik = args.esik if args.esik is not None else kunye.get("buyuk_esik", BUYUK_ESIK_VARSAYILAN)
    liste = _oncelik_listesi(kunye, esik)
    tam_yukle_sayim = {}
    for o in _tam_yukle_oku(kok):
        k = o.get("kaynak")
        tam_yukle_sayim[k] = tam_yukle_sayim.get(k, 0) + 1

    print(f"# OKUMA KAPISI — öncelikli evrak listesi (mekanik, {_kunye_yolu(kok)})")
    buyuk_toplam = kunye.get("buyuk_evrak")
    if buyuk_toplam is None:
        buyuk_toplam = sum(1 for k in liste if k["buyuk"])
    print(f"Toplam evrak: {kunye.get('toplam_evrak', len(liste))} · "
          f"büyük evrak (>{esik:,} kar.): {buyuk_toplam}")
    print()
    print("ÖNCELİK SIRASI (mekanik tür~ tahminine göre SABİT sıralama — tebligat/süre "
          "önce; bu bir MUHAKEME değil sıralama kuralıdır — içerik ajan tarafından "
          "gerekirse farklı önceliklendirilebilir, DERİNLİK KISILMAZ):")
    for i, k in enumerate(liste, 1):
        etiketler = []
        if k["teyit_gerek"]:
            etiketler.append("⚠OCR")
        if k["buyuk"]:
            etiketler.append("BÜYÜK")
        if k.get("sure_adayi"):
            etiketler.append(f"SÜRE ADAYI:{k['sure_adayi']}")
        etiket_s = (" [" + ", ".join(etiketler) + "]") if etiketler else ""
        print(f" {i:>3}. [{k['tur_tahmini'] or '—'}] {k['no'] or '—'} · {k['ad'] or ''} · "
              f"{k['karakter']} kar.{etiket_s} · {k['md']}")

    buyukler = [k for k in liste if k["buyuk"]]
    if buyukler:
        print()
        print("BÜYÜK EVRAK UYARISI — haritadan oku (harita = deterministik sayfa/bölüm "
              "bölmesi, ÖZET DEĞİL); yalnız gerçekten gerekliyse TAM yükle, TAM yükleme "
              "deftere loglanır (`--tam-yukle-kaydet \"<kaynak>\"`):")
        for k in buyukler:
            onceki = tam_yukle_sayim.get(k["kaynak"], 0)
            damga = f" — DAHA ÖNCE {onceki} kez TAM yüklenmiş (mükerrer olabilir)" if onceki else ""
            print(f"  - {k['kaynak']} (~{k['karakter']:,} kar.) · harita: "
                  f"{k['harita'] or '—'}{damga}")

    sure_adaylari_l = [k for k in liste if k.get("sure_adayi")]
    if sure_adaylari_l:
        print()
        print(f"SÜRE ADAYI: {len(sure_adaylari_l)} evrak (tebligat/karar/tensip/bilirkişi/ödeme "
              "emri/ihbarname sınıfı — süre BAŞLATABİLİR). Tarih çıkarımı + öneri için: "
              "`okuma_kapisi.py --sure-adaylari` (advisory; sure-flag avukat onayıyla yazılır).")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"kok": os.path.abspath(kok), "esik": esik, "liste": liste},
                      f, ensure_ascii=False, indent=2)
        print(f"\nJSON yazıldı: {args.json}")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="okuma_kapisi.py — GATE B: OKUMA KAPISI (00-INDEX/kunye/haritadan "
                    "mekanik öncelikli okuma listesi + tam-yükleme dedup defteri)")
    ap.add_argument("--kok", default=".", help="çalışma kökü (oa_hafiza.py/tam_tur.py "
                    "simetrisi; _oa buradan aranır; varsayılan CWD)")
    ap.add_argument("--esik", type=int, default=None,
                    help="büyük evrak eşiği (anlamlı karakter); verilmezse künyedeki "
                         "buyuk_esik (yoksa 40000)")
    ap.add_argument("--json", help="öncelik listesini ayrıca JSON olarak yaz")
    ap.add_argument("--tam-yukle-kaydet", dest="tam_yukle_kaydet", metavar="KAYNAK",
                    help="bir evrağın TAM yüklendiğini deftere logla (dedup uyarısı — "
                         "asla bloklamaz)")
    ap.add_argument("--ajan", help="--tam-yukle-kaydet: kaydı bırakan alt-ajan/parça adı "
                    "(opsiyonel, ör. oa-vakia)")
    ap.add_argument("--tam-yukle-defter", dest="tam_yukle_defter", action="store_true",
                    help="tam-yükleme dedup defterini göster")
    ap.add_argument("--sure-adaylari", dest="sure_adaylari", action="store_true",
                    help="(v0.5.16/E P1-10) kritik evrak → SÜRE ADAYI taraması: stdout tablo + "
                         "_oa/cikti/00-sure-adaylari.json; advisory — sure-flag YAZMAZ")
    args = ap.parse_args()

    if not os.path.isdir(args.kok):
        sys.exit(f"HATA: klasör yok: {args.kok}")

    if args.sure_adaylari:
        sys.exit(cmd_sure_adaylari(args))
    if args.tam_yukle_kaydet:
        sys.exit(cmd_tam_yukle_kaydet(args))
    if args.tam_yukle_defter:
        sys.exit(cmd_tam_yukle_defter(args))
    sys.exit(cmd_liste(args))


if __name__ == "__main__":
    main()

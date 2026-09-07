#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
kanun_yolu_zinciri.py — KANUN YOLU ZİNCİRİ ÇIKARICI (v0.5.16 — Hamle 8, karar #10).

Amaç: Bir ÜST mahkeme kararının (Yargıtay / Danıştay / BAM) tam metninden
ALT kat künyelerini (BAM dairesi → ilk derece mahkemesi) MEKANİK olarak
çıkarır ve «iniş mümkün mü» sorusunu yapısal ölçütle cevaplar. Zincir:
ilk derece → istinaf (HMK m.341 / CMK m.272) → temyiz (HMK m.361 / CMK m.286)
[Mevzuat MCP teyit 2026-09-06]. Üst karar bu zinciri yukarıdan aşağı
tarif eder; script o tarifi okur.

Dürüst sınır (anayasa m.4/5 — model kurar, script denetler): Script hukuki
yorum yapmaz, «karar lehe mi» demez, indekste arama YAPMAZ (ağ yok). Yalnız
metinde ZATEN VAR OLAN esas/karar/tarih/mahkeme dizgelerini kanonikleştirir.
Metinde olmayan hiçbir künye üretilmez; künye redakteyse (D1) bunu
GÖRÜNÜR yazar — "bulundu" demez (sahte kesinlik yasağı).

İNİŞ KARARI (mekanik): alt katta esas VE karar dolu VE redakte değil →
o kata iniş mümkün. Aksi hâlde gerekçeyle HAYIR:
  • «BAM redakte — iniş kör (D1)»: BAM, KENDİ dosyasının ilk derece
    künyesini «... Esas, ... Karar» biçiminde redakte eder (emsal atıfları
    korunur). Redakte künyeden ilk derece kararına inilemez.
  • «ilçe adı redakte»: ceza yeni biçimde ilk derece mahkemesinin yer adı
    «... 1. Asliye Ceza Mahkemesi» gibi kesilmiş olabilir; esas/karar dolu
    olsa bile mahkeme kimliği yoktur → o kat kör, iniş BAM'a kadar.

Saha dersi (D3): esas_no BAM'lar arası TEKİL DEĞİLDİR (her BAM kendi
sırasını tutar) ve MCP `ictihat_ara` BAM/daire filtresi sunmaz → arama
sonuçları istemci tarafında süzülmelidir (`--suzgec`). Süzgeç sessiz kırpmaz:
elenen her kayıt NEDENİYLE listelenir, sayılar basılır.

Tek yazar kuralı: bu script KÜTÜĞE (`_oa/teyit/kunye-teyit.md`) YAZMAZ —
tek yazar `oa_hafiza.py teyit`tir. `--kok` verildiğinde yalnız
`_oa/cikti/03-kanun-yolu-zinciri.json` (pipeline adım-3 ARAŞTIRMA kanıtı)
yazılır ve kat başına ÖNERİLEN teyit komut satırı STDERR'e basılır.

Kullanım:
  python kanun_yolu_zinciri.py _oa/teyit/dokum/<dosya>.md [--json] [--kok <KOK>]
  python kanun_yolu_zinciri.py --suzgec arama_sonuclari.json [--bam "<BAM adı>"]
         [--daire "11. HD"] [--yil-min 2020] [--json]

Çıktı (JSON): {"arac":"kanun_yolu_zinciri","girdi":…,"ust":{merci,daire,esas,
karar,tarih},"alt":[{seviye:"BAM"|"ilk_derece",mahkeme,esas,karar,tarih,
redakte:bool,inis:bool,gerekce}],"inis_mumkun":bool,"inis_kati":
"BAM"|"ilk_derece"|null,"gerekce":str,"zincir_ozeti":str,"uyarilar":[…]}
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import importlib.util
import json
import os
import re
import sys

ARAC = "kanun_yolu_zinciri"
CIKTI_ADI = "03-kanun-yolu-zinciri.json"   # pipeline adım-3 (ARAŞTIRMA) kanıtı

# ── kunye_ortak (oa-kontrol) — TEK KAYNAK künye çıkarımı ────────────────────
# Esas/karar/daire normalizasyonu ailede tek yerde yaşar (`kunye_ortak.py`);
# bu script onu GÖRELİ yoldan importlib ile yükler. Yüklenemezse (aile dışına
# kopyalanmış tek dosya) yerel MİNİMAL regex devreye girer ve bu durum
# çıktıda görünür UYARI olarak taşınır — sessiz düşme yok (fail-closed:
# minimal regex daha az biçim tanır; tanımadığını "yok" saymaz, uyarır).
_KO_VARSAYILAN = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "oa-kontrol", "scripts", "kunye_ortak.py"))


def kunye_ortak_yukle(yol=None):
    """(modül | None, uyarı | None) döndürür. Yol yoksa/yüklenemezse None + uyarı."""
    yol = str(yol or _KO_VARSAYILAN)
    if not os.path.isfile(yol):
        return None, (f"UYARI: kunye_ortak.py bulunamadı ({yol}) — yerel MİNİMAL "
                      "künye regex'i kullanıldı; nadir biçimler atlanmış olabilir "
                      "(fail-closed: atlanan künye 'yok' sayılmaz, elle bak).")
    try:
        spec = importlib.util.spec_from_file_location("_kyz_kunye_ortak", yol)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if not hasattr(mod, "esas_karar_atiflari") or not hasattr(mod, "daire_key"):
            return None, ("UYARI: kunye_ortak.py yüklendi ama beklenen API "
                          "(esas_karar_atiflari/daire_key) yok — yerel minimal regex.")
        return mod, None
    except Exception as e:  # pragma: no cover — bozuk modül
        return None, f"UYARI: kunye_ortak.py yüklenemedi ({e.__class__.__name__}: {e}) — yerel minimal regex."


KO, KO_UYARI = kunye_ortak_yukle()

# ── Yerel minimal desenler (yedek; kunye_ortak varken KULLANILMAZ) ──────────
_YN = r"\d{4}\s*/\s*\d{1,6}"
_MIN_ESAS_RE = re.compile(
    r"(?:\bE(?:sas)?\s*\.?\s*(?:No\s*\.?)?\s*[:.]?\s*(" + _YN + r"))|(" + _YN + r")\s*(?:E\.|E\b|Esas\b)",
    re.I)
_MIN_KARAR_RE = re.compile(
    r"(?:\bK(?:arar)?\s*\.?\s*(?:No\s*\.?)?\s*[:.]?\s*(" + _YN + r"))|(" + _YN + r")\s*(?:K\.|K\b|Karar\b)",
    re.I)
_MIN_DAIRE_RE = re.compile(
    r"(\d{1,2})\s*\.\s*(HD|CD|Hukuk\s+Dairesi|Ceza\s+Dairesi|İdari\s+Dava\s+Dairesi|"
    r"Vergi\s+Dava\s+Dairesi|Daire|D)(?![A-Za-zÇĞİÖŞÜçğıöşü])", re.I)

# ── Genel desenler ──────────────────────────────────────────────────────────
TARIH_RE = re.compile(r"\b(\d{1,2})[./](\d{1,2})[./](\d{4})\b")
# (iv) D1 — BAM kendi dosyasının alt künyesini redakte eder: «... Esas, ... Karar»
# / «… Esas» / «…/… E.» — üç nokta VE elips karakteri; tam künye eşleşmez.
REDAKTE_RE = re.compile(
    r"(?:\.{3}|…)(?:\s*/\s*(?:\.{3}|…))?\s*(?:Esas\b|E\s*\.|E\b|Karar\b|K\s*\.|K\b)", re.I)
# mahkeme ADI redakte (ilçe/il adı kesilmiş): değer üç nokta/elips ile başlar
AD_REDAKTE_RE = re.compile(r"^\s*(?:\.{3}|…)")

# Yeni biçim etiket satırları (i)/(iii): «MAHKEMESİ : …», «İLK DERECE MAHKEMESİ : …»,
# «TARİHİ : …», «SAYISI : …», «NUMARASI : …»
_ETIKET_RE = re.compile(
    r"^\s*[*_ ]*(?P<etiket>İLK\s+DERECE\s+MAHKEMES[İIiı]|MAHKEMES[İIiı]|MAHKEME|"
    r"KARAR\s+TAR[İIiı]H[İIiı]?|TAR[İIiı]H[İIiı]?|SAYISI|NUMARASI|ESAS\s*NO|KARAR\s*NO|"
    r"DOSYA\s*NO)[*_ ]*\s*:\s*(?P<deger>.*?)\s*$", re.I)

# (ii) Eski biçim gövde cümlesi: «… Mahkemesince verilen dd.mm.yyyy tarih ve
# YYYY/N E., YYYY/N K. sayılı» (Dairesince: BAM eski biçim)
ESKI_RE = re.compile(
    r"(?P<mahkeme>[^\n;]{3,160}?(?:Mahkemesi|Dairesi))(?:'|’)?nce\s+verilen\s+"
    r"(?P<tarih>\d{1,2}[./]\d{1,2}[./]\d{4})\s+(?:tarih|gün)(?:li)?\s+ve\s+"
    r"(?P<esas>" + _YN + r")\s*(?:E\.?|Esas)\s*,?\s*(?P<karar>" + _YN + r")\s*(?:K\.?|Karar)",
    re.I)
_ESKI_KIRP_RE = re.compile(
    r"\b(?:sonunda|dolayı|dolayısıyla|arasındaki|arasında|tarafından|üzerine|ile|"
    r"nedeniyle|hakkında)\b", re.I)

UST_MERCI_RE = re.compile(
    r"YARGITAY|DANIŞTAY|BÖLGE\s+ADL[İI]YE\s+MAHKEMES[İI]|BÖLGE\s+[İI]DARE\s+MAHKEMES[İI]"
    r"|\bBAM\b|\bB[İI]M\b", re.I)
BAM_AD_RE = re.compile(r"Bölge\s+Adliye|Bölge\s+İdare|\bBAM\b|\bB[İI]M\b", re.I)


def _tr_kucuk(s):
    return s.replace("İ", "i").replace("I", "ı").lower()


def norm_no(s):
    return re.sub(r"\s*/\s*", "/", s.strip()) if s else None


def redakte_mi(deger):
    """Künye/değer dizgesi redakte mi («... Esas, ... Karar» sınıfı)?"""
    return bool(deger) and REDAKTE_RE.search(deger) is not None


def _tarih(deger):
    m = TARIH_RE.search(deger or "")
    if not m:
        return None
    g, a, y = m.groups()
    return f"{int(g):02d}.{int(a):02d}.{y}"


def _esas_karar(metin, ko):
    """Pasajdan (esas, karar) — kunye_ortak varsa onunla, yoksa minimal regex."""
    if not metin:
        return None, None
    if ko is not None:
        at = ko.esas_karar_atiflari(metin)
        at = [a for a in at if a.get("kunye_turu", "esas_karar") == "esas_karar"]
        if at:
            return at[0]["esas"], at[0]["karar"]
        return None, None
    me = _MIN_ESAS_RE.search(metin)
    mk = _MIN_KARAR_RE.search(metin)
    esas = norm_no(me.group(1) or me.group(2)) if me else None
    karar = norm_no(mk.group(1) or mk.group(2)) if mk else None
    return esas, karar


_BUYUK_DAIRE_RE = re.compile(
    r"\b(HUKUK|CEZA|İDARİ\s+DAVA|VERGİ\s+DAVA)\s+DA[İI]RES[İI]\b")
_BUYUK_DAIRE_ESLEM = {"HUKUK": "Hukuk Dairesi", "CEZA": "Ceza Dairesi",
                      "İDARİ DAVA": "İdari Dava Dairesi", "VERGİ DAVA": "Vergi Dava Dairesi"}


def _daire_normalize(metin):
    """BAM/Yargıtay başlıkları TAMAMEN BÜYÜK HARF gelebilir («3. HUKUK DAİRESİ»);
    `kunye_ortak.DAIRE_RE` büyük-küçük harf duyarlıdır (gövde gürültüsüne karşı
    bilinçli) — başlık için yalnız «… DAİRESİ» kalıbı kanonik yazıma çevrilir."""
    return _BUYUK_DAIRE_RE.sub(
        lambda m: _BUYUK_DAIRE_ESLEM[re.sub(r"\s+", " ", m.group(1))], metin)


def _daire(metin, ko):
    """«11. HD» / «2. CD» / «3. D» kanonik daire etiketi; yoksa None."""
    if not metin:
        return None
    metin = _daire_normalize(metin)
    if ko is not None:
        dk = ko.daire_key(metin)
    else:
        m = _MIN_DAIRE_RE.search(metin)
        if not m:
            dk = None
        else:
            u = m.group(2).upper()
            aile = ("HD" if u.startswith("HD") or "HUKUK" in u else
                    "CD" if u.startswith("CD") or "CEZA" in u else
                    "VDD" if "VERG" in u else "İDD" if "DAR" in u else "D")
            dk = (m.group(1), aile)
    return f"{dk[0]}. {dk[1]}" if dk else None


def _ust_merci(bas_metin):
    m = UST_MERCI_RE.search(bas_metin)
    if not m:
        return None
    t = _tr_kucuk(m.group(0))
    if "yargıtay" in t:
        return "Yargıtay"
    if "danıştay" in t:
        return "Danıştay"
    if "idare" in t or t == "bim":
        return "BİM"
    return "BAM"


def _alt_seviye(etiket, mahkeme, ust_merci):
    if etiket.upper().startswith("İLK") or etiket.upper().startswith("ILK"):
        return "ilk_derece"
    if ust_merci in ("BAM", "BİM"):
        return "ilk_derece"
    return "BAM" if BAM_AD_RE.search(mahkeme or "") else "ilk_derece"


def _bloklar(metin):
    """Yeni biçim etiket bloklarını ayırır.
    Döner: (ust_alanlar: dict, alt_bloklar: [ {etiket, mahkeme, tarih, sayi} ], ust_bas_metin)"""
    ust = {}
    bloklar = []
    aktif = None
    ust_bas = []
    for satir in metin.split("\n"):
        m = _ETIKET_RE.match(satir)
        if not m:
            if aktif is None:
                ust_bas.append(satir)
            continue
        etiket = re.sub(r"\s+", " ", m.group("etiket")).upper()
        deger = m.group("deger").strip()
        if etiket in ("MAHKEMESİ", "MAHKEMESI", "MAHKEME") or etiket.startswith(("İLK", "ILK")):
            aktif = {"etiket": etiket, "mahkeme": deger, "tarih": None, "sayi": ""}
            bloklar.append(aktif)
            continue
        if aktif is None:
            ust_bas.append(satir)
            if etiket.startswith("KARAR TAR") or etiket.startswith("TAR"):
                ust.setdefault("tarih", _tarih(deger))
            else:
                ust["kunye"] = (ust.get("kunye", "") + " " + etiket + ": " + deger).strip()
            continue
        if etiket.startswith("TAR"):
            aktif["tarih"] = _tarih(deger)
        else:  # SAYISI / NUMARASI / ESAS NO / KARAR NO / DOSYA NO
            aktif["sayi"] = (aktif["sayi"] + " " + deger).strip()
    return ust, bloklar, "\n".join(ust_bas)


def _eski_bicim(metin, ust_merci, ko):
    """(ii) gövde cümlesi biçimi — birden çok atıf olabilir (ilk derece + BAM)."""
    alt = []
    for m in ESKI_RE.finditer(metin):
        ham = m.group("mahkeme")
        parcalar = _ESKI_KIRP_RE.split(ham)
        mahkeme = re.sub(r"\s+", " ", parcalar[-1]).strip(" ,.:;'’")
        esas, karar = _esas_karar(
            f"{m.group('esas')} E., {m.group('karar')} K.", ko)
        alt.append({
            "seviye": _alt_seviye("MAHKEMESİ", mahkeme, ust_merci),
            "mahkeme": mahkeme,
            "esas": esas, "karar": karar,
            "tarih": _tarih(m.group("tarih")),
            "redakte": False,
        })
    return alt


def _kat_degerlendir(a):
    """Her alt kat için MEKANİK iniş kararı + gerekçe (yorum yok)."""
    if a["redakte"] and a.get("ad_redakte"):
        a["inis"] = False
        a["gerekce"] = ("ilçe/mahkeme adı redakte — künye numarası olsa bile "
                        "mahkeme kimliği yok; bu kat kör")
    elif a["redakte"]:
        a["inis"] = False
        a["gerekce"] = "künye redakte («... Esas, ... Karar») — iniş kör (D1)"
    elif a["esas"] and a["karar"]:
        a["inis"] = True
        a["gerekce"] = "esas + karar dolu, redakte değil — iniş mümkün (mekanik)"
    else:
        a["inis"] = False
        eksik = [k for k in ("esas", "karar") if not a[k]]
        a["gerekce"] = f"künye eksik ({', '.join(eksik)} yok) — iniş yapılamaz"
    return a


def zincir_cikar(metin, girdi="-", ko=KO):
    """Ana çıkarım. `ko`: kunye_ortak modülü (None → yerel minimal regex + uyarı)."""
    uyarilar = []
    if ko is None:
        uyarilar.append(KO_UYARI or "UYARI: kunye_ortak.py yüklenmedi — yerel minimal regex.")

    ust_alan, bloklar, ust_bas = _bloklar(metin)
    bas = metin[:2500]
    ust_merci = _ust_merci(ust_bas) or _ust_merci(bas)
    ust_kunye_pasaj = ust_alan.get("kunye") or ust_bas
    ust_esas, ust_karar = _esas_karar(ust_kunye_pasaj, ko)
    if ust_esas is None and ust_karar is None:
        ust_esas, ust_karar = _esas_karar(ust_bas, ko)
    ust_tarih = ust_alan.get("tarih") or _tarih(ust_bas)
    ust = {
        "merci": ust_merci,
        "daire": _daire(ust_bas, ko),
        "esas": ust_esas, "karar": ust_karar, "tarih": ust_tarih,
    }
    if ust_merci is None:
        uyarilar.append("UYARI: üst merci (Yargıtay/Danıştay/BAM/BİM) başlıkta tanınmadı.")

    alt = []
    for b in bloklar:
        mahkeme = re.sub(r"\s+", " ", b["mahkeme"]).strip()
        ad_redakte = bool(AD_REDAKTE_RE.match(mahkeme)) or not mahkeme
        sayi_redakte = redakte_mi(b["sayi"])
        esas, karar = (None, None) if sayi_redakte else _esas_karar(b["sayi"], ko)
        alt.append({
            "seviye": _alt_seviye(b["etiket"], mahkeme, ust_merci),
            "mahkeme": mahkeme or None,
            "esas": esas, "karar": karar,
            "tarih": b["tarih"],
            "redakte": bool(sayi_redakte or ad_redakte),
            "ad_redakte": ad_redakte,
        })
    if not alt:
        alt = _eski_bicim(metin, ust_merci, ko)
        for a in alt:
            a["ad_redakte"] = False

    for a in alt:
        _kat_degerlendir(a)

    # Kat sırası: BAM önce, ilk derece sonra (üstten aşağı iniş)
    sira = {"BAM": 0, "ilk_derece": 1}
    alt.sort(key=lambda a: sira.get(a["seviye"], 9))

    # İniş: kat kat; bir kat kör olunca daha aşağısı da körlenir (zincir kopar)
    inis_kati = None
    gerekce = None
    for a in alt:
        if a["inis"]:
            inis_kati = a["seviye"]
        else:
            gerekce = f"{a['seviye']} ({a['mahkeme'] or '?'}): {a['gerekce']}"
            break
    if not alt:
        gerekce = ("alt künye bulunamadı — metinde ne yeni biçim etiketi "
                   "(MAHKEMESİ/SAYISI) ne eski biçim cümlesi (… Mahkemesince "
                   "verilen … tarih ve … E., … K.) tanındı; iniş yapılamaz "
                   "(fail-closed — elle bak, 'yok' sayma)")
    inis_mumkun = inis_kati is not None
    if inis_mumkun and gerekce is None:
        gerekce = f"tüm katlar inilebilir — en derin kat: {inis_kati}"
    elif inis_mumkun:
        gerekce = f"iniş {inis_kati} katına kadar; sonrası kör → {gerekce}"

    def _k(x):
        if x.get("redakte"):
            return "künye redakte"
        return f"E. {x.get('esas') or '?'} / K. {x.get('karar') or '?'}"

    parcalar = [f"{ust['merci'] or '?'} {ust['daire'] or ''}".strip() + f" ({_k(ust)}, {ust['tarih'] or 'tarih ?'})"]
    for a in alt:
        parcalar.append(f"{a['seviye']}: {a['mahkeme'] or '?'} ({_k(a)}, {a['tarih'] or 'tarih ?'})")
    zincir_ozeti = " ← ".join(parcalar)

    for a in alt:
        a.pop("ad_redakte", None)

    return {
        "arac": ARAC,
        "girdi": girdi,
        "ust": ust,
        "alt": alt,
        "inis_mumkun": inis_mumkun,
        "inis_kati": inis_kati,
        "gerekce": gerekce,
        "zincir_ozeti": zincir_ozeti,
        "uyarilar": uyarilar,
    }


def teyit_onerileri(sonuc):
    """Kat başına ÖNERİLEN `oa_hafiza.py teyit` komutu (kütüğe YAZMAZ — tek yazar
    oa_hafiza). Layer 0: `--sorgu` ilk derece mahkeme adı + esas no birlikte
    TAŞIMAZ (oa_hafiza fail-closed reddeder); künye `--sonuc`'a gider. Emsal
    (kamu) kararı için serbesttir; iniş hedefi MÜVEKKİLİN KENDİ dosyasıysa
    MCP'ye hiç gönderilmez (UYAP'ta iniş avukata aittir)."""
    satirlar = []
    for a in sonuc["alt"]:
        kunye = "redakte" if a["redakte"] else "tam"
        kunye_metni = (f"{a['mahkeme'] or '?'} E. {a['esas'] or '?'} K. {a['karar'] or '?'} "
                       f"T. {a['tarih'] or '?'}")
        # esas/karar NO sorguya GİRMEZ (Layer 0: mahkeme adı + esas no eş-geçişi RET)
        sorgu = f"{a['mahkeme'] or '?'} {a['tarih'] or ''}".strip()
        onek = ""
        if a["redakte"]:
            # D1: redakte katta ARAMA YAPILMAZ (aranacak künye yok); satır yalnız
            # kütükte "bu kat kör" izini bırakmak içindir — "bulunamadı" demek de yanlış.
            onek = "[REDAKTE KAT — arama yapılmaz, yalnız iz kaydı] "
        satirlar.append(
            f"{onek}python oa-pipeline/scripts/oa_hafiza.py teyit --arac ictihat_ara "
            f"--sorgu \"{sorgu}\" "
            f"--sonuc \"SEVİYE={a['seviye']} KÜNYE={kunye} METİN=<indekste-var|bulunamadı> "
            f"| {kunye_metni}\"")
    return satirlar


# ── --suzgec (D3) ───────────────────────────────────────────────────────────
_LISTE_ANAHTARLARI = ("results", "sonuclar", "kararlar", "items", "data", "decisions")


def _sonuc_listesi(veri):
    if isinstance(veri, list):
        return veri
    if isinstance(veri, dict):
        for k in _LISTE_ANAHTARLARI:
            if isinstance(veri.get(k), list):
                return veri[k]
    return None


def _kayit_metni(kayit):
    if isinstance(kayit, dict):
        return " ".join(str(v) for v in kayit.values() if isinstance(v, (str, int, float)))
    return str(kayit)


def _kayit_birim(kayit):
    if not isinstance(kayit, dict):
        return _kayit_metni(kayit)
    for k in ("birimAdi", "birim", "daire", "mahkeme", "court", "unit", "birim_adi"):
        v = kayit.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return _kayit_metni(kayit)


def _kayit_yil(kayit):
    """Karar yılı: tarih alanından (dd.mm.yyyy | yyyy-mm-dd); yoksa karar no'dan;
    yoksa None (belirsiz → fail-closed elenir)."""
    if not isinstance(kayit, dict):
        return None
    for k, v in kayit.items():
        if "tarih" in _tr_kucuk(k) or "date" in k.lower():
            m = re.search(r"(\d{4})-\d{2}-\d{2}", str(v)) or re.search(r"\d{1,2}[./]\d{1,2}[./](\d{4})", str(v))
            if m:
                return int(m.group(1))
    for k, v in kayit.items():
        if "karar" in _tr_kucuk(k):
            m = re.match(r"\s*(\d{4})\s*/", str(v))
            if m:
                return int(m.group(1))
    return None


def suzgec(veri, girdi, bam=None, daire=None, yil_min=None, ko=KO):
    liste = _sonuc_listesi(veri)
    if liste is None:
        sys.exit("RET: --suzgec girdisi bir sonuç LİSTESİ ya da {'results': [...]} "
                 "sözlüğü olmalı (ictihat_ara sonuçlarının JSON dökümü).")
    hedef_daire = None
    if daire:
        hedef_daire = _daire(daire, ko)
        if not hedef_daire:
            sys.exit(f"RET: --daire '{daire}' ayrıştırılamadı — '11. HD' / '2. CD' / "
                     "'11. Hukuk Dairesi' biçiminde verin (fail-closed).")
    bam_k = _tr_kucuk(bam) if bam else None

    suzulen, elenen = [], []
    for kayit in liste:
        birim = _kayit_birim(kayit)
        nedenler = []
        if bam_k and bam_k not in _tr_kucuk(birim):
            nedenler.append(f"BAM eşleşmedi ('{birim}' ≠ '{bam}') — esas_no BAM'lar arası tekil değil (D3)")
        if hedef_daire:
            kd = _daire(birim, ko)
            if kd != hedef_daire:
                nedenler.append(f"daire eşleşmedi ({kd or '?'} ≠ {hedef_daire})")
        if yil_min is not None:
            y = _kayit_yil(kayit)
            if y is None:
                nedenler.append("yıl belirsiz (tarih/karar no alanı yok) — fail-closed elendi; elle bak")
            elif y < yil_min:
                nedenler.append(f"yıl {y} < --yil-min {yil_min}")
        if nedenler:
            elenen.append({"neden": "; ".join(nedenler), "kayit": kayit})
        else:
            suzulen.append(kayit)
    return {
        "arac": ARAC, "mod": "suzgec", "girdi": girdi,
        "filtre": {"bam": bam, "daire": hedef_daire, "yil_min": yil_min},
        "sayilar": {"toplam": len(liste), "suzulen": len(suzulen), "elenen": len(elenen)},
        "suzulen": suzulen, "elenen": elenen,
    }


# ── CLI ─────────────────────────────────────────────────────────────────────

def _oku(yol):
    if not os.path.isfile(yol):
        sys.exit(f"RET: girdi dosyası yok: {yol}")
    with open(yol, encoding="utf-8", errors="replace") as f:
        return f.read()


def _insan_ozet(r):
    print(f"KANUN YOLU ZİNCİRİ — {r['girdi']}")
    print(f"  ÜST : {r['ust']['merci'] or '?'} {r['ust']['daire'] or ''} "
          f"E. {r['ust']['esas'] or '?'} K. {r['ust']['karar'] or '?'} T. {r['ust']['tarih'] or '?'}")
    for a in r["alt"]:
        print(f"  {a['seviye']:<11}: {a['mahkeme'] or '?'} | E. {a['esas'] or '?'} K. {a['karar'] or '?'} "
              f"T. {a['tarih'] or '?'} | redakte={'EVET' if a['redakte'] else 'hayır'} | "
              f"iniş={'EVET' if a['inis'] else 'HAYIR'} — {a['gerekce']}")
    print(f"  İNİŞ MÜMKÜN: {'EVET' if r['inis_mumkun'] else 'HAYIR'} "
          f"(kat: {r['inis_kati'] or '-'}) — {r['gerekce']}")
    print(f"  ZİNCİR: {r['zincir_ozeti']}")
    for u in r["uyarilar"]:
        print(f"  {u}")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Üst mahkeme kararından kanun yolu zinciri (alt künyeler) çıkarır; "
                    "iniş kararı MEKANİKTİR. --suzgec: ictihat_ara sonuçlarını istemci "
                    "tarafında BAM/daire/yıl ile süzer (D3).")
    ap.add_argument("girdi", nargs="?", help="üst karar tam metni (md/txt; tipik: _oa/teyit/dokum/*.md)")
    ap.add_argument("--json", action="store_true", help="çıktıyı JSON olarak STDOUT'a bas")
    ap.add_argument("--kok", help="çalışma kökü: <KOK>/_oa/cikti/%s yazılır + önerilen teyit "
                                  "komutları STDERR'e basılır (kütüğe YAZMAZ)" % CIKTI_ADI)
    ap.add_argument("--suzgec", help="ictihat_ara sonuç JSON dosyası (istemci tarafı süzgeç)")
    ap.add_argument("--bam", help="süzgeç: BAM adı alt dizgesi (ör. 'Örnek Bölge Adliye')")
    ap.add_argument("--daire", help="süzgeç: daire ('11. HD' / '2. CD')")
    ap.add_argument("--yil-min", dest="yil_min", type=int, help="süzgeç: en küçük karar yılı")
    args = ap.parse_args(argv)

    if KO_UYARI:
        print(KO_UYARI, file=sys.stderr)

    if args.suzgec:
        ham = _oku(args.suzgec)
        try:
            veri = json.loads(ham)
        except json.JSONDecodeError as e:
            sys.exit(f"RET: --suzgec JSON ayrıştırılamadı ({e}).")
        if not (args.bam or args.daire or args.yil_min is not None):
            print("UYARI: --suzgec için hiçbir filtre (--bam/--daire/--yil-min) verilmedi — "
                  "tüm kayıtlar geçti; süzgeç anlamsız (D3: BAM+daire+tarih ile doğrula).",
                  file=sys.stderr)
        r = suzgec(veri, args.suzgec, bam=args.bam, daire=args.daire, yil_min=args.yil_min)
        s = r["sayilar"]
        print(f"SÜZGEÇ: toplam {s['toplam']} · süzülen {s['suzulen']} · elenen {s['elenen']} "
              f"(sessiz kırpma yok — elenenler nedenleriyle listede)", file=sys.stderr)
        if args.json:
            print(json.dumps(r, ensure_ascii=False, indent=2))
        else:
            for k in r["suzulen"]:
                print("GEÇTİ :", _kayit_metni(k)[:160])
            for e in r["elenen"]:
                print("ELENDİ:", _kayit_metni(e["kayit"])[:100], "→", e["neden"])
        return 0

    if not args.girdi:
        ap.print_usage(file=sys.stderr)
        sys.exit("RET: girdi dosyası ya da --suzgec verin.")
    metin = _oku(args.girdi)
    r = zincir_cikar(metin, girdi=args.girdi)

    if args.kok:
        cikti_dizin = os.path.join(args.kok, "_oa", "cikti")
        os.makedirs(cikti_dizin, exist_ok=True)
        cikti = os.path.join(cikti_dizin, CIKTI_ADI)
        with open(cikti, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2)
        print(f"YAZILDI: {cikti}", file=sys.stderr)
        print("ÖNERİLEN kütük satırları (kütüğe bu script YAZMAZ — tek yazar oa_hafiza; "
              "METİN=<…> alanını MCP sonucuna göre DOLDUR):", file=sys.stderr)
        for s in teyit_onerileri(r):
            print("  " + s, file=sys.stderr)

    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        _insan_ozet(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
maliyet_cetveli.py — DETERMİNİSTİK MALİYET CETVELİ (oa-strateji · P1-11 / A-18,
v0.5.16).

Felsefe (anayasa m.4/m.5 — olguda sıfır halüsinasyon): bu script HİÇBİR
parasal veriyi KENDİ İÇİNDE TAŞIMAZ. Tüm harç/tarife rakamları yanındaki
`tarife.json`'dan okunur; o dosya yıl damgalı ve MCP-teyit tarihlidir. Script
yalnız ARİTMETİK yapar (nispi harç, peşin harç, karşı vekâlet, gider bandı);
hukuki yorum, olasılık, "kazanma şansı" ÜRETMEZ (oa-strateji dürüst sınır:
olasılık nitel banttır, sayı değildir — o bant modelin işidir, scriptin değil).

FAIL-CLOSED (A-18 saha dersi — bayat tarifeyle "kesin" rakam üretmek, sayı
uydurmanın mekanik biçimidir):
  * `mcp_teyit_tarihi` BOŞ  → «TARİFE TEYİTSİZ/BAYAT — hesap yapılmadı», exit 2
  * `yil` ≠ hesap yılı      → aynı mesaj, exit 2
  * hesap için gereken bir tarife alanı `null` → o kalem «TEYİTSİZ — hesaplanmadı»
    olarak basılır, hesaplanabilen kalemler gösterilir, exit yine 2 (KISMİ).
Yalnız TÜM kalemler teyitli tarifeden hesaplandıysa exit 0.

Kullanılan kurallar (metinleri Mevzuat MCP'den okundu, 2026-09-06):
  * 492 s. Harçlar K. m.15/16 (nispi–maktu ölçü; değer esası), m.28/a (karar ve
    ilam harcının DÖRTTE BİRİ peşin), (1) sayılı tarife III-1-a (hüküm altına
    alınan değer üzerinden nispi karar harcı; nispi harç asgari haddi).
  * HMK m.323 (yargılama giderlerinin kapsamı), m.326/2 (kısmen haklı çıkmada
    giderlerin haklılık oranına göre paylaştırılması — ORAN mahkeme takdiridir;
    script yalnız kabul oranını yansıtır, "çıpa").
  * AAÜT (RG 04.11.2025/33067; değ. 08.01.2026/33131, 28.03.2026/33207) m.3/1
    (karşı tarafa yükletilen ücret tarife miktarından az, üç katından çok olamaz),
    m.13/1 (konusu para olan işte üçüncü kısım; maktu altına inemez), m.13/2
    (hükmedilen ücret kabul/reddedilen miktarı geçemez), m.13/3 (maddi tazminatta
    kısmi ret: karşı vekâlet davacı vekili lehine belirlenen ücreti geçemez),
    m.13/4 (maddi tazminatın TAMAMININ reddinde maktu).

Kullanım:
  python maliyet_cetveli.py --deger 250000 --kismi-kabul 0.6
  python maliyet_cetveli.py --deger 250000 --kismi-kabul 0.6 --tarife test.json --yil 2026
  python maliyet_cetveli.py --deger 250000 --bilirkisi 15000 --diger-gider 3000 --json
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import datetime as _dt
import json
import os
import sys

VARSAYILAN_TARIFE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tarife.json")
BAYAT_MESAJ = "TARİFE TEYİTSİZ/BAYAT — hesap yapılmadı"
EKSIK_MESAJ = "TEYİTSİZ (tarife alanı null) — hesaplanmadı"

# Şema: tarife.json'da bulunması ZORUNLU üst anahtarlar (eksikse fail-closed)
ZORUNLU_ANAHTARLAR = ("yil", "mcp_teyit_tarihi", "kaynak", "harc", "aaut")


class TarifeHatasi(Exception):
    """Tarife dosyası okunamıyor / şema dışı / teyitsiz / bayat."""


# ───────────────────────────── yardımcılar ──────────────────────────────

def tl(x):
    """1234567.891 → '1.234.567,89 TL' (Türkçe biçim; yüzde işareti KULLANILMAZ —
    çıktıda '%' görünmesi 'olasılık' yanılsaması yaratır, test bunu kilitler)."""
    if x is None:
        return EKSIK_MESAJ
    s = f"{float(x):,.2f}"                       # 1,234,567.89
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s + " TL"


def _sayi_mi(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def tarife_yukle(yol):
    """tarife.json'u oku; şema ve tip denetimi. Bozuk/eksik → TarifeHatasi."""
    if not os.path.isfile(yol):
        raise TarifeHatasi(f"tarife dosyası yok: {yol}")
    try:
        with open(yol, encoding="utf-8") as f:
            veri = json.load(f)
    except (OSError, ValueError) as e:
        raise TarifeHatasi(f"tarife dosyası okunamadı/bozuk JSON: {e}")
    if not isinstance(veri, dict):
        raise TarifeHatasi("tarife kökü bir nesne (dict) olmalı")
    for k in ZORUNLU_ANAHTARLAR:
        if k not in veri:
            raise TarifeHatasi(f"tarife şema dışı — '{k}' anahtarı yok")
    if not isinstance(veri.get("harc"), dict) or not isinstance(veri.get("aaut"), dict):
        raise TarifeHatasi("tarife şema dışı — 'harc' ve 'aaut' nesne olmalı")
    return veri


def tarife_teyit_kontrol(veri, hesap_yili):
    """FAIL-CLOSED kapısı: teyit tarihi boş VEYA yıl ≠ hesap yılı → TarifeHatasi."""
    teyit = veri.get("mcp_teyit_tarihi")
    if not isinstance(teyit, str) or not teyit.strip():
        raise TarifeHatasi(f"{BAYAT_MESAJ} (mcp_teyit_tarihi boş)")
    try:
        _dt.date.fromisoformat(teyit.strip())
    except ValueError:
        raise TarifeHatasi(f"{BAYAT_MESAJ} (mcp_teyit_tarihi ISO tarih değil: {teyit!r})")
    yil = veri.get("yil")
    if not isinstance(yil, int) or isinstance(yil, bool):
        raise TarifeHatasi(f"{BAYAT_MESAJ} (yil tam sayı değil: {yil!r})")
    if yil != hesap_yili:
        raise TarifeHatasi(f"{BAYAT_MESAJ} (tarife yılı {yil} ≠ hesap yılı {hesap_yili})")


# ───────────────────────────── aritmetik ────────────────────────────────

def nispi_ucret(miktar, dilimler):
    """AAÜT üçüncü kısım (kademeli/artan dilim) hesabı. dilimler:
    [{"ust": 50000, "yuzde": 16}, {"ust": null, "yuzde": 15}, ...] — 'ust' o
    dilimin ÜST sınırı (kümülatif), null = son dilim. Boş liste → None."""
    if not dilimler:
        return None
    kalan = float(miktar)
    onceki_ust = 0.0
    toplam = 0.0
    for d in dilimler:
        ust = d.get("ust")
        yuzde = d.get("yuzde")
        if not _sayi_mi(yuzde):
            return None
        if ust is None:
            dilim_genislik = kalan
        else:
            dilim_genislik = max(0.0, min(kalan, float(ust) - onceki_ust))
            onceki_ust = float(ust)
        toplam += dilim_genislik * float(yuzde) / 100.0
        kalan -= dilim_genislik
        if kalan <= 0:
            break
    return round(toplam, 2)


def hesapla(deger, kismi_kabul, tarife, bilirkisi=0.0, diger_gider=0.0):
    """Saf hesap: dict döndürür; eksik tarife alanı olan kalemler None kalır
    ve 'eksik' listesine adı yazılır. Olasılık/yorum ÜRETMEZ."""
    harc = tarife["harc"]
    aaut = tarife["aaut"]
    eksik = []
    deger = float(deger)
    kabul = round(deger * kismi_kabul, 2)
    ret = round(deger - kabul, 2)

    basvuru = harc.get("basvuru_maktu")
    binde = harc.get("karar_ilam_nispi_binde")
    pesin_oran = harc.get("pesin_oran")
    nispi_asgari = harc.get("nispi_asgari")          # opsiyonel had
    kesif = harc.get("kesif")                         # opsiyonel
    istinaf_h = harc.get("istinaf_basvuru_maktu")     # opsiyonel
    temyiz_h = harc.get("temyiz_basvuru_maktu")       # opsiyonel

    # — HARÇ —
    if not _sayi_mi(basvuru):
        eksik.append("harc.basvuru_maktu")
        basvuru = None
    if _sayi_mi(binde):
        karar_dava = round(deger * binde / 1000.0, 2)
        karar_hukum = round(kabul * binde / 1000.0, 2)
        if _sayi_mi(nispi_asgari):
            karar_dava = max(karar_dava, float(nispi_asgari))
            karar_hukum = max(karar_hukum, float(nispi_asgari)) if kabul > 0 else karar_hukum
    else:
        eksik.append("harc.karar_ilam_nispi_binde")
        karar_dava = karar_hukum = None
    if _sayi_mi(pesin_oran) and karar_dava is not None:
        pesin = round(karar_dava * pesin_oran, 2)
    else:
        if not _sayi_mi(pesin_oran):
            eksik.append("harc.pesin_oran")
        pesin = None
    acilis = None
    if basvuru is not None and pesin is not None:
        acilis = round(basvuru + pesin, 2)

    # — KARŞI VEKÂLET (AAÜT m.13) —
    maktu = aaut.get("maktu_asliye")
    dilimler = aaut.get("nispi_dilimler") or []
    lehe = aleyhe = None
    if not _sayi_mi(maktu):
        eksik.append("aaut.maktu_asliye")
    elif not dilimler:
        eksik.append("aaut.nispi_dilimler")
    else:
        n_kabul = nispi_ucret(kabul, dilimler)
        n_ret = nispi_ucret(ret, dilimler)
        if n_kabul is None or n_ret is None:
            eksik.append("aaut.nispi_dilimler")
        else:
            maktu = float(maktu)
            # lehe (kabul edilen kısım): m.13/1 maktu altına inmez; m.13/2 kabul miktarını geçemez
            lehe = 0.0 if kabul <= 0 else min(max(n_kabul, maktu), kabul)
            if ret <= 0:
                aleyhe = 0.0
            elif kabul <= 0:
                aleyhe = maktu                      # m.13/4 — tamamının reddi: maktu
            else:
                aleyhe = min(max(n_ret, maktu), ret)   # m.13/1 + m.13/2
                aleyhe = min(aleyhe, lehe)             # m.13/3 — davacı vekili ücretini geçemez
            lehe, aleyhe = round(lehe, 2), round(aleyhe, 2)

    # — YARGILAMA GİDERİ BANDI (HMK m.323 kalemleri; oran m.326/2 — çıpa) —
    ret_orani = round(1.0 - kismi_kabul, 4)
    ek = float(bilirkisi or 0.0) + float(diger_gider or 0.0)
    band_alt = band_ust = None
    if acilis is not None:
        band_alt = round(acilis + ek, 2)
    if basvuru is not None and karar_dava is not None:
        ust = basvuru + karar_dava + ek
        for opsiyonel in (kesif, istinaf_h, temyiz_h):
            if _sayi_mi(opsiyonel):
                ust += float(opsiyonel)
        if aleyhe is not None:
            ust += aleyhe
        band_ust = round(ust, 2)

    return {
        "girdi": {"deger": deger, "kismi_kabul": kismi_kabul, "kabul": kabul, "ret": ret,
                  "ret_orani": ret_orani, "bilirkisi": float(bilirkisi or 0.0),
                  "diger_gider": float(diger_gider or 0.0)},
        "harc": {"basvuru_maktu": basvuru, "karar_ilam_dava_degeri": karar_dava,
                 "karar_ilam_pesin": pesin, "karar_ilam_hukum_degeri": karar_hukum,
                 "dava_acilis_toplam": acilis},
        "karsi_vekalet": {"lehe_kabul_kismi": lehe, "aleyhe_ret_kismi": aleyhe},
        "gider_bandi": {"alt": band_alt, "ust": band_ust},
        "eksik_alanlar": eksik,
    }


# ───────────────────────────── rapor ────────────────────────────────────

def rapor(sonuc, tarife, tarife_yolu):
    g, h, kv, b = sonuc["girdi"], sonuc["harc"], sonuc["karsi_vekalet"], sonuc["gider_bandi"]
    L = []
    L.append("MALİYET CETVELİ — deterministik aritmetik (oa-strateji · P1-11)")
    L.append(f"Tarife: {tarife_yolu} · yıl {tarife['yil']} · MCP teyit {tarife['mcp_teyit_tarihi']}")
    L.append(f"Kaynak: {tarife.get('kaynak') or '—'}")
    L.append("")
    L.append(f"Dava değeri            : {tl(g['deger'])}")
    L.append(f"Kısmi kabul (oran)     : {g['kismi_kabul']:.2f} → kabul {tl(g['kabul'])} · ret {tl(g['ret'])}")
    L.append("")
    L.append("HARÇ (492 s.K. (1) sayılı tarife; m.28/a peşin oran)")
    L.append(f"  Başvurma harcı (maktu)                    : {tl(h['basvuru_maktu'])}")
    L.append(f"  Karar ve ilam harcı — dava değeri üzerinden: {tl(h['karar_ilam_dava_degeri'])}")
    L.append(f"  Peşin karar harcı (açılışta)               : {tl(h['karar_ilam_pesin'])}")
    L.append(f"  Karar harcı — hüküm altına alınan değer    : {tl(h['karar_ilam_hukum_degeri'])}")
    L.append(f"  DAVA AÇILIŞ TOPLAMI (başvuru + peşin)      : {tl(h['dava_acilis_toplam'])}")
    L.append("")
    L.append("KARŞI VEKÂLET (AAÜT m.13 — üçüncü kısım; maktu taban; kabul/ret tavanı)")
    L.append(f"  Lehe (kabul edilen kısım)                  : {tl(kv['lehe_kabul_kismi'])}")
    L.append(f"  ALEYHE (reddedilen kısım — müvekkil öder)  : {tl(kv['aleyhe_ret_kismi'])}")
    L.append("")
    L.append("YARGILAMA GİDERİ BANDI (HMK m.323 kalemleri; paylaştırma m.326/2 — mahkeme takdiri, çıpa)")
    L.append(f"  ALT (açılış zorunlu + elle girilen gider)  : {tl(b['alt'])}")
    L.append(f"  ÜST (tam harç + keşif/kanun yolu harçları + aleyhe vekâlet + elle gider): {tl(b['ust'])}")
    L.append(f"  Elle girilen: bilirkişi {tl(g['bilirkisi'])} · diğer {tl(g['diger_gider'])} "
             "(tarifesiz kalemler — avukat girer, script uydurmaz)")
    L.append("")
    if sonuc["eksik_alanlar"]:
        L.append("KISMİ CETVEL — şu tarife alanları null (MCP'den teyit edilemedi), ilgili kalemler "
                 "HESAPLANMADI: " + ", ".join(sonuc["eksik_alanlar"]))
        L.append("→ tarife.json'u resmî kaynaktan (Mevzuat MCP / Resmî Gazete) doldur, teyit tarihini yaz.")
    L.append("NOT: Bu cetvel olasılık/kazanma şansı ÜRETMEZ; başarı bandı (güçlü/dengeli/zayıf/belirsiz) "
             "modelin gerekçeli işidir. Rakamlar tarife aritmetiğidir, hukuki yorum değildir.")
    return "\n".join(L)


# ───────────────────────────── CLI ──────────────────────────────────────

def main(argv=None):
    p = argparse.ArgumentParser(
        description="Deterministik maliyet cetveli — tarife.json'dan harç/karşı vekâlet/gider bandı "
                    "(olasılık üretmez; teyitsiz/bayat tarifede FAIL-CLOSED exit 2).")
    p.add_argument("--deger", type=float, required=True, help="dava/talep değeri (TL)")
    p.add_argument("--kismi-kabul", type=float, default=1.0,
                   help="kabul oranı 0..1 (ör. 0.6 = değerin yüzde altmışı kabul, kalanı ret); varsayılan 1.0")
    p.add_argument("--tarife", default=VARSAYILAN_TARIFE, help="tarife.json yolu (varsayılan: script yanı)")
    p.add_argument("--yil", type=int, default=None, help="hesap yılı (varsayılan: bugünün yılı)")
    p.add_argument("--bilirkisi", type=float, default=0.0, help="bilirkişi ücreti (elle, TL)")
    p.add_argument("--diger-gider", type=float, default=0.0, help="tebligat/posta/keşif dışı diğer gider (elle, TL)")
    p.add_argument("--json", action="store_true", help="sonucu JSON olarak da bas")
    a = p.parse_args(argv)

    if a.deger <= 0:
        print("HATA: --deger pozitif olmalı.", file=sys.stderr)
        return 1
    if not (0.0 <= a.kismi_kabul <= 1.0):
        print("HATA: --kismi-kabul 0 ile 1 arasında olmalı.", file=sys.stderr)
        return 1
    hesap_yili = a.yil if a.yil is not None else _dt.date.today().year

    try:
        tarife = tarife_yukle(a.tarife)
        tarife_teyit_kontrol(tarife, hesap_yili)
    except TarifeHatasi as e:
        print(f"FAIL-CLOSED: {e}")
        print(f"Tarife: {a.tarife}")
        print("Hiçbir rakam üretilmedi — tarife.json'u Mevzuat MCP / Resmî Gazete teyidiyle "
              "yıl damgalı doldurup 'mcp_teyit_tarihi' yazın.")
        return 2

    sonuc = hesapla(a.deger, a.kismi_kabul, tarife, a.bilirkisi, a.diger_gider)
    print(rapor(sonuc, tarife, a.tarife))
    if a.json:
        print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    return 2 if sonuc["eksik_alanlar"] else 0


if __name__ == "__main__":
    sys.exit(main())

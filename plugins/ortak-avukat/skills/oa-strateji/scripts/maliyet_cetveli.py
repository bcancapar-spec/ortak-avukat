#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
maliyet_cetveli.py — DETERMİNİSTİK MALİYET CETVELİ (oa-strateji · P1-11 / A-18,
v0.5.16; v0.5.18 adayı: merci kalemleri, ölüm/cismani zarar peşin oranı, dilimli
faiz + güncel oran teyidi protokolü).

Felsefe (anayasa m.4/m.5 — olguda sıfır halüsinasyon): bu script HİÇBİR
parasal veriyi ve HİÇBİR oranı KENDİ İÇİNDE TAŞIMAZ. Tüm harç/tarife rakamları
yanındaki `tarife.json`'dan okunur; o dosya yıl damgalı ve MCP-teyit tarihlidir.
Faiz oranı ise hiç saklanmaz: her hesapta dönemiyle, resmî kaynağıyla ve teyit
tarihiyle ayrıca verilir (--oranlar ya da --faiz-orani). Script yalnız
ARİTMETİK yapar (nispi harç, peşin harç, karşı vekâlet, gider bandı, basit
faiz); hukuki yorum, "kazanma şansı" ÜRETMEZ (oa-strateji dürüst sınır: başarı
nitel banttır, sayı değildir — o bant modelin işidir, scriptin değil).

FAIL-CLOSED (A-18 saha dersi — bayat tarifeyle "kesin" rakam üretmek, sayı
uydurmanın mekanik biçimidir):
  * `mcp_teyit_tarihi` BOŞ  → «TARİFE TEYİTSİZ/BAYAT — hesap yapılmadı», exit 2
  * `yil` ≠ hesap yılı      → aynı mesaj, exit 2
  * hesap için gereken bir tarife alanı `null` → o kalem «TEYİTSİZ — hesaplanmadı»
    olarak basılır, hesaplanabilen kalemler gösterilir, exit yine 2 (KISMİ).
  * (v0.5.18) faiz istenip oran KAYNAKSIZ/TARİHSİZ verilirse, dönem oran
    dilimleriyle tam KAPSANMIYORSA, dilimler ÇAKIŞIYORSA ya da teyit
    tarihinden SONRASI (projeksiyon) hesaplanıyorsa → faiz kalemi ÇIPA olarak
    görünür uyarıyla basılır, exit 2. Oran hiç verilmezse faiz hesaplanmaz
    (exit 1 — script oran ÜRETMEZ).
Yalnız TÜM kalemler teyitli tarifeden/orandan hesaplandıysa exit 0.

Kullanılan kurallar (metinleri Mevzuat MCP'den okundu, 2026-09-06; v0.5.18
eklemeleri 2026-10-05):
  * 492 s. Harçlar K. m.15/16 (nispi–maktu ölçü; değer esası), m.28/a (karar ve
    ilam harcının DÖRTTE BİRİ peşin; ölüm ve cismani zarar sebebiyle açılan
    maddi ve manevi tazminat davalarında YİRMİDE BİRİ), (1) sayılı tarife III-1-a
    (hüküm altına alınan değer üzerinden nispi karar harcı; nispi harç asgari
    haddi), (1) sayılı tarife A-I-1 (sulh/icra tetkik mercii başvurma harcı),
    (3) sayılı tarife (vergi yargısı harçları). m.28 yalnız (1) sayılı tarifenin
    nispi harçlarını düzenler; vergi yargısı nispi harcının peşin kısmı bu
    script'te HESAPLANMAZ (TEYİT BEKLİYOR — görünür not).
  * HMK m.323 (yargılama giderlerinin kapsamı), m.326/2 (kısmen haklı çıkmada
    giderlerin haklılık oranına göre paylaştırılması — ORAN mahkeme takdiridir;
    script yalnız kabul oranını yansıtır, "çıpa").
  * AAÜT (RG 04.11.2025/33067; değ. 08.01.2026/33131, 28.03.2026/33207) m.3/1,
    m.13/1-4; m.21 (ücret takdirinde hükmün verildiği tarihteki tarife esas —
    bugünkü tarife gelecekteki hüküm için ÇIPA). Maktu ücret MERCİYE göredir:
    script başka merci için asliye maktuunu KULLANMAZ ('aaut.maktu_<merci>').
  * (v0.5.18 K2 — 2026-10-07) Av.K. m.168/2 (Ek cümle: 16/6/2009-5904/35): vergi,
    resim, harç ve benzeri mali yükümlülükler, bunların zam ve cezaları ile
    tarifelere ilişkin davalar ve 6183 s.K. uygulamasından doğan her türlü davada
    avukatlık ücreti MAKTU belirlenir → `AVK168_MAKTU_MERCILER` mercilerinde nispi
    dilim (AAÜT üçüncü kısım, m.13) UYGULANMAZ; tam kabul/ret → `aaut.maktu_<merci>`
    (AAÜT m.15/1 "diğer durumlarda tamamına"); KISMİ kabul/ret dağılımı ve m.13/2
    tavanının maktu ücrete uygulanması genel hükümlerden OKUNAMADI → o kalem
    "HESAPLANAMAYAN" olarak görünür yazılır, rakam ÜRETİLMEZ (exit 2).
  * 3095 s.K. m.1 (Değişik: 7589/10; yürürlük RG 31.07.2026) ve m.2: kanuni
    faiz ve temerrüt faizi oranı TCMB oranına bağlıdır, yıllık belirlenir ve
    30 Haziran'da beş puan veya daha çok farkta yılın ikinci yarısı için değişir
    — oran DÖNEMSELDİR; bu yüzden faiz dilimli ve kaynaklı verilir, script yıl/
    yarıyıl/rejim sınırını kesen dilimde hatırlatma basar (`oran_kurallari`).

Kullanım:
  python maliyet_cetveli.py --deger 250000 --kismi-kabul 0.6
  python maliyet_cetveli.py --deger 250000 --merci sulh --tarife test.json --yil 2026
  python maliyet_cetveli.py --deger 250000 --olum-cismani --json
  python maliyet_cetveli.py --deger 250000 --faiz-baslangic 2026-01-15 --faiz-bitis 2026-09-30 --oranlar oranlar.json
  python maliyet_cetveli.py --deger 250000 --faiz-baslangic 2026-01-15 --faiz-bitis 2026-09-30 \\
      --faiz-orani 24 --faiz-turu kanuni --faiz-kaynak "<RG/TCMB künyesi>" --faiz-teyit 2026-10-05
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

# Merci → (başvurma harcı kaynağı, istinaf, temyiz). "harc:" önekli olanlar
# (1) sayılı tarifenin asliye satırından (geriye uyum), "merci:" önekliler
# `harc_merci.kalemler`den okunur. Tutar burada YOK — yalnız anahtar adı.
MERCILER = {
    "asliye":      ("harc:basvuru_maktu", "harc:istinaf_basvuru_maktu", "harc:temyiz_basvuru_maktu"),
    "idare":       ("harc:basvuru_maktu", "merci:bim_istinaf", "merci:danistay_temyiz"),
    "sulh":        ("merci:sulh_icra_tetkik_basvuru", "harc:istinaf_basvuru_maktu", "harc:temyiz_basvuru_maktu"),
    "icra_tetkik": ("merci:sulh_icra_tetkik_basvuru", "harc:istinaf_basvuru_maktu", "harc:temyiz_basvuru_maktu"),
    "vergi":       ("merci:vergi_basvuru_vm_bim", "merci:vergi_istinaf_bim", "merci:vergi_temyiz_danistay"),
}
MERCI_ADI = {"asliye": "asliye mahkemesi", "idare": "idare mahkemesi (vergi dışı)",
             "sulh": "sulh mahkemesi", "icra_tetkik": "icra tetkik mercii (icra mahkemesi)",
             "vergi": "vergi mahkemesi ((3) sayılı tarife)"}
# v0.5.18 K2 (T5-4 GİZLİ KUSUR) — Av.K. m.168/2 (Ek cümle: 16/6/2009-5904/35 md., Yargı PRO
# mevzuat_getir 2026-10-07): "… genel bütçeye, il özel idareleri, belediye ve köylere ait
# vergi, resim, harç ve benzeri mali yükümlülükler ve bunların zam ve cezaları ile
# tarifelere ilişkin davalar ve 6183 sayılı Amme Alacaklarının Tahsil Usulü Hakkında
# Kanunun uygulanmasından doğan her türlü davalar için avukatlık ücreti tutarı maktu
# olarak belirlenir." NEDEN VAR: karşı vekâlet kolunda bu mercilerde AAÜT üçüncü kısım
# nispi dilimi (m.13) UYGULANMAZ; `aaut.maktu_<merci>` esastır. Eski kod merci=vergi'de de
# nispi dilim uyguluyordu — tablolar null olduğu için rakam üretmiyor, kusur görünmüyordu.
# Aynı rejimdeki (harç/6183) başka bir merci eklenirse TEK genişleme noktası budur.
AVK168_MAKTU_MERCILER = ("vergi",)
FAIZ_TURLERI = ("kanuni", "temerrut", "avans", "sozlesme", "diger")


class TarifeHatasi(Exception):
    """Tarife dosyası okunamıyor / şema dışı / teyitsiz / bayat."""


class OranHatasi(Exception):
    """Oran dosyası okunamıyor / şema dışı — faiz hesaplanamaz (exit 1)."""


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


def _iso(s):
    """'YYYY-MM-DD' → date; değilse None (istisna fırlatmaz)."""
    if not isinstance(s, str):
        return None
    try:
        return _dt.date.fromisoformat(s.strip())
    except ValueError:
        return None


def _oran_yazi(x):
    """Yıllık oranı '%' işareti KULLANMADAN yazar (bkz. tl() notu)."""
    return "yıllık yüzde " + (f"{float(x):.4f}".rstrip("0").rstrip(".").replace(".", ","))


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
        teyit_t = _dt.date.fromisoformat(teyit.strip())
    except ValueError:
        raise TarifeHatasi(f"{BAYAT_MESAJ} (mcp_teyit_tarihi ISO tarih değil: {teyit!r})")
    yil = veri.get("yil")
    if not isinstance(yil, int) or isinstance(yil, bool):
        raise TarifeHatasi(f"{BAYAT_MESAJ} (yil tam sayı değil: {yil!r})")
    if yil != hesap_yili:
        raise TarifeHatasi(f"{BAYAT_MESAJ} (tarife yılı {yil} ≠ hesap yılı {hesap_yili})")
    # Yıl damgası elle ileri alınıp eski teyitle bırakılmasın: bir yılın tarifesi
    # en erken önceki yıl sonunda yayımlanır (bugünün tarihine BAKILMAZ — determinizm).
    if teyit_t.year < yil - 1:
        raise TarifeHatasi(f"{BAYAT_MESAJ} (mcp_teyit_tarihi {teyit_t.isoformat()} tarife yılı {yil} için çok eski)")


def merci_blogu_gecerli(tarife):
    """`harc_merci` bloğu kaynaklı ve tarife yılıyla tutarlı mı? Değilse neden
    döner (kalemleri TEYİTSİZ sayılır — fail-closed; sessiz kullanım yok)."""
    b = tarife.get("harc_merci")
    if not isinstance(b, dict):
        return False, "harc_merci bloğu yok"
    if not (isinstance(b.get("rg"), str) and b["rg"].strip()):
        return False, "harc_merci.rg (Resmî Gazete künyesi) boş"
    yur, tey = _iso(b.get("yururluk")), _iso(b.get("teyit_tarihi"))
    if yur is None or tey is None:
        return False, "harc_merci.yururluk/teyit_tarihi ISO tarih değil"
    if yur.year != tarife.get("yil"):
        return False, f"harc_merci yürürlük yılı {yur.year} ≠ tarife yılı {tarife.get('yil')}"
    if tey < yur - _dt.timedelta(days=45):
        return False, (f"harc_merci.teyit_tarihi {tey.isoformat()} yürürlükten ({yur.isoformat()}) çok önce — "
                       "o yılın tebliği yayımlanmadan teyit edilmiş olamaz")
    if not isinstance(b.get("kalemler"), dict):
        return False, "harc_merci.kalemler nesne değil"
    return True, ""


def kalem_oku(tarife, anahtar):
    """'harc:ad' ya da 'merci:ad' → (tutar|None, eksik_alan_adı|None, kalem_sözlüğü|None)."""
    kaynak, ad = anahtar.split(":", 1)
    if kaynak == "harc":
        v = tarife["harc"].get(ad)
        return (float(v), None, None) if _sayi_mi(v) else (None, f"harc.{ad}", None)
    gecerli, _ = merci_blogu_gecerli(tarife)
    if not gecerli:
        return None, f"harc_merci.{ad}", None
    k = tarife["harc_merci"]["kalemler"].get(ad)
    if isinstance(k, dict) and _sayi_mi(k.get("tutar")) and k["tutar"] > 0:
        return float(k["tutar"]), None, k
    return None, f"harc_merci.{ad}", None


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


def hesapla(deger, kismi_kabul, tarife, bilirkisi=0.0, diger_gider=0.0, merci="asliye",
            olum_cismani=False):
    """Saf hesap: dict döndürür; eksik tarife alanı olan kalemler None kalır
    ve 'eksik' listesine adı yazılır. Olasılık/yorum ÜRETMEZ."""
    if merci not in MERCILER:
        raise ValueError(f"bilinmeyen merci: {merci}")
    harc = tarife["harc"]
    aaut = tarife["aaut"]
    # v0.5.18 K2 (KÜÇÜK-8): karşı vekâlete ait notlar HARÇ bölümüne değil, KARŞI VEKÂLET
    # bölümüne basılır — okur dayanağı ilgili satırın yanında görür.
    eksik, notlar, vekalet_notlari = [], [], []
    deger = float(deger)
    kabul = round(deger * kismi_kabul, 2)
    ret = round(deger - kabul, 2)
    vergi = merci == "vergi"
    bas_anahtar, ist_anahtar, tem_anahtar = MERCILER[merci]

    basvuru, e, bas_kalem = kalem_oku(tarife, bas_anahtar)
    if e:
        eksik.append(e)
    # Tarife içi tutarlılık: asliye başvurma harcı iki blokta da varsa AYNI olmalı
    # (biri güncellenip diğeri unutulursa hangisinin doğru olduğu bilinemez).
    asl_merci, _, _ = kalem_oku(tarife, "merci:asliye_idare_basvuru")
    asl_harc = harc.get("basvuru_maktu")
    if asl_merci is not None and _sayi_mi(asl_harc) and abs(float(asl_harc) - asl_merci) > 0.005:
        eksik.append("tarife tutarsız: harc.basvuru_maktu ≠ harc_merci.asliye_idare_basvuru")
    istinaf_h, _, _ = kalem_oku(tarife, ist_anahtar)     # opsiyonel (üst bant)
    temyiz_h, _, _ = kalem_oku(tarife, tem_anahtar)       # opsiyonel (üst bant)
    kesif = harc.get("kesif")                             # opsiyonel

    # — KARAR VE İLAM HARCI —
    if vergi:
        nispi, e, nispi_kalem = kalem_oku(tarife, "merci:vergi_nispi_vm_bim_binde")
        binde = nispi
        nispi_asgari = nispi_kalem.get("asgari") if nispi_kalem else None
        if e:
            eksik.append(e)
        notlar.append("(3) sayılı tarife — vergi yargısı: nispi karar harcı hüküm altına alınan uyuşmazlık "
                      "değeri üzerinden; peşin kısmı ve ödeme zamanı TEYİT BEKLİYOR (492 s.K. m.28 yalnız (1) "
                      "sayılı tarifenin nispi harçlarını düzenler) — açılış toplamına yalnız başvurma harcı girer.")
    else:
        binde = harc.get("karar_ilam_nispi_binde")
        nispi_asgari = harc.get("nispi_asgari")          # opsiyonel had
        if not _sayi_mi(binde):
            eksik.append("harc.karar_ilam_nispi_binde")
    if _sayi_mi(binde):
        karar_dava = round(deger * binde / 1000.0, 2)
        karar_hukum = round(kabul * binde / 1000.0, 2)
        if _sayi_mi(nispi_asgari):
            karar_dava = max(karar_dava, float(nispi_asgari))
            karar_hukum = max(karar_hukum, float(nispi_asgari)) if kabul > 0 else karar_hukum
    else:
        karar_dava = karar_hukum = None
    if vergi:
        # Vergi yargısında kabul edilen kısım üzerinden harcın kime ve nasıl
        # yükleneceği (3) sayılı tarifeden teyit edilmedi — rakam ÜRETİLMEZ.
        karar_hukum = None

    # — PEŞİN HARÇ (492 m.28/a) —
    pesin = None
    if vergi:
        if olum_cismani:
            notlar.append("--olum-cismani vergi yargısında UYGULANMADI (492 m.28/a (1) sayılı tarifeye ilişkindir).")
    else:
        oran_ad = "pesin_oran_olum_cismani" if olum_cismani else "pesin_oran"
        pesin_oran = harc.get(oran_ad)
        if _sayi_mi(pesin_oran) and karar_dava is not None:
            pesin = round(karar_dava * pesin_oran, 2)
        elif not _sayi_mi(pesin_oran):
            eksik.append(f"harc.{oran_ad}")
        if olum_cismani:
            notlar.append("Peşin harç oranı: yirmide bir (492 s.K. m.28/a — ölüm ve cismani zarar sebebiyle "
                          "açılan maddi ve manevi tazminat davası; nitelendirme avukatındır).")
    if vergi:
        acilis = basvuru
    else:
        acilis = round(basvuru + pesin, 2) if (basvuru is not None and pesin is not None) else None

    # — KARŞI VEKÂLET (AAÜT m.13; maktu MERCİYE göre — m.13/1) —
    maktu_ad = f"maktu_{merci}"
    maktu = aaut.get(maktu_ad)
    dilimler = aaut.get("nispi_dilimler") or []
    lehe = aleyhe = None
    hesaplanamayan = []
    if merci == "idare":
        # v0.5.18 K2 (KÜÇÜK-9 — görünürlük, kapsam GENİŞLETİLMEDİ): idare mahkemesinde görülen
        # 6183/harç kaynaklı dava (ecrimisil, idari para cezası ödeme emri…) Av.K. m.168/2
        # "her türlü dava" lafzıyla maktu rejimdedir; bu cetvel idare merciinde nispi uygular.
        # Nitelendirme avukatındır — script davanın kaynağını bilemez, yalnız uyarır.
        vekalet_notlari.append(
            "DİKKAT — Av.K. m.168/2 kapsamı: dava 6183 s.K. uygulamasından ya da vergi, resim, harç ve "
            "benzeri mali yükümlülükten kaynaklanıyorsa (ör. ecrimisil, idari para cezası ödeme emri) "
            "avukatlık ücreti MAKTU belirlenir ('her türlü dava'); bu cetvel `--merci idare`de nispi dilimi "
            "(AAÜT m.13) uyguladı. Davanın kaynağını AVUKAT nitelendirir ve teyit eder; maktu rejimi "
            "gerekiyorsa aşağıdaki karşı vekâlet satırları KULLANILMAZ (idare için maktu kol eklenmedi — "
            "kapsam genişletilmedi).")
    if merci in AVK168_MAKTU_MERCILER:
        # v0.5.18 K2 — Av.K. m.168/2: ücret MAKTU; nispi dilim bu mercide UYGULANMAZ ve
        # `aaut.nispi_dilimler` istenmez. Okunan genel hükümler (AAÜT m.3/1, m.13, m.15/1,
        # m.21) kısmi kabul/ret hâlinde maktu ücretin taraflar arasında dağılımını ve
        # m.13/2 tavanının maktu ücrete uygulanmasını SÖYLEMEZ → o hâlde rakam üretilmez.
        vekalet_notlari.append(
            "Av.K. m.168/2 (Ek cümle: 16/6/2009-5904/35): vergi, resim, harç ve benzeri mali yükümlülükler, "
            "bunların zam ve cezaları ile tarifelere ilişkin davalar ve 6183 s.K. uygulamasından doğan her "
            "türlü davada avukatlık ücreti MAKTU olarak belirlenir — nispi dilim (AAÜT üçüncü kısım, m.13) "
            f"UYGULANMADI; esas `aaut.{maktu_ad}`. AAÜT m.15/1: birinci savunma dilekçesi süresinin bitimine "
            "kadar feragat, kabul, konusuz kalma ya da bu nedenlerle ret → ücretin yarısı, diğer durumlarda "
            "tamamı (aşamayı script bilmez; cetvel tamamını yazar, avukat değerlendirir). AAÜT m.3/1: "
            "tarifede yazılı miktardan az ve üç katından çok olamaz — maktu tutar TABANDIR, üç katına kadar "
            "takdir (ÇIPA). m.13/2 kabul/ret tavanının maktu vergi ücretine uygulanıp uygulanmayacağı genel "
            "hükümlerden okunamadı — tavan uygulanmadı.")
        if not _sayi_mi(maktu):
            eksik.append(f"aaut.{maktu_ad}")
        else:
            maktu = float(maktu)
            if ret <= 0:
                lehe, aleyhe = maktu, 0.0            # tam kabul → davacı vekili lehine maktu
            elif kabul <= 0:
                lehe, aleyhe = 0.0, maktu            # tam ret → davalı (idare) vekili lehine maktu
            else:
                hesaplanamayan.append(
                    "karşı vekâlet (vergi — kısmi kabul/ret): Av.K. m.168/2 maktu ücretin taraflar arasında "
                    "kısmi kabul/ret dağılımı AAÜT genel hükümlerinden (m.3, m.13, m.15, m.21) okunamadı — "
                    "rakam ÜRETİLMEDİ; Danıştay uygulaması bu turda teyit edilmedi, avukat değerlendirir.")
    elif not _sayi_mi(maktu):
        eksik.append(f"aaut.{maktu_ad}")
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
    ust_vekalet = None     # dahil | maktu_ust_sinir | haric — ÜST satırı bunu AÇIKÇA yazar
    if acilis is not None:
        band_alt = round(acilis + ek, 2)
    if basvuru is not None and karar_dava is not None:
        ust = basvuru + karar_dava + ek
        for opsiyonel in (kesif, istinaf_h, temyiz_h):
            if _sayi_mi(opsiyonel):
                ust += float(opsiyonel)
        # v0.5.18 K2 (ÖNEMLİ-1, inceleme): aleyhe vekâlet HESAPLANAMADI iken ÜST bandı onu
        # sessizce dışlıyor, etiket "aleyhe vekâlet dahil" diyordu → müvekkilin azami maruziyeti
        # maktu kadar DÜŞÜK görünüyordu (hak kaybı yönü). Bilinen maktu ÜST SINIR olarak eklenir
        # (müvekkil için güvenli yön); maktu da bilinmiyorsa band "haric" diye işaretlenir.
        if aleyhe is not None:
            ust += aleyhe
            ust_vekalet = "dahil"
        elif hesaplanamayan and _sayi_mi(maktu):
            ust += float(maktu)
            ust_vekalet = "maktu_ust_sinir"
        else:
            ust_vekalet = "haric"
        band_ust = round(ust, 2)

    return {
        "girdi": {"deger": deger, "kismi_kabul": kismi_kabul, "kabul": kabul, "ret": ret,
                  "ret_orani": ret_orani, "bilirkisi": float(bilirkisi or 0.0),
                  "diger_gider": float(diger_gider or 0.0), "merci": merci,
                  "olum_cismani": bool(olum_cismani)},
        "harc": {"basvuru_maktu": basvuru, "karar_ilam_dava_degeri": karar_dava,
                 "karar_ilam_pesin": pesin, "karar_ilam_hukum_degeri": karar_hukum,
                 "dava_acilis_toplam": acilis, "basvuru_satiri": (bas_kalem or {}).get("satir")},
        "karsi_vekalet": {"lehe_kabul_kismi": lehe, "aleyhe_ret_kismi": aleyhe},
        "gider_bandi": {"alt": band_alt, "ust": band_ust, "ust_vekalet": ust_vekalet},
        "vekalet_notlari": vekalet_notlari,
        "eksik_alanlar": eksik,
        # v0.5.18 K2 — tarife alanı dolu olsa da KURALI okunamayan kalem (ör. vergide kısmi
        # kabul/ret dağılımı): rakam yok, görünür not var; exit 2 (eksik_alanlar'dan ayrı —
        # bu bir "tarife.json'u doldur" eksiği DEĞİLDİR).
        "hesaplanamayan": hesaplanamayan,
        "notlar": notlar,
    }


# ───────────────────────── faiz + güncel oran teyidi ─────────────────────

def oranlar_yukle(yol):
    """Oran dosyası: {"oranlar": [{"tur","baslangic","bitis","yillik_yuzde",
    "kaynak","teyit_tarihi"}, ...]} ya da doğrudan liste. Şema dışı → OranHatasi."""
    if not os.path.isfile(yol):
        raise OranHatasi(f"oran dosyası yok: {yol}")
    try:
        with open(yol, encoding="utf-8") as f:
            veri = json.load(f)
    except (OSError, ValueError) as e:
        raise OranHatasi(f"oran dosyası okunamadı/bozuk JSON: {e}")
    liste = veri.get("oranlar") if isinstance(veri, dict) else veri
    if not isinstance(liste, list) or not liste:
        raise OranHatasi("oran dosyası şema dışı — boş olmayan 'oranlar' listesi gerekir")
    return liste


def _dilim_dogrula(ham, sira):
    """Dilimi denetler. Döner: (dilim, kaynak_eksik_mi). Biçim hatası → OranHatasi."""
    if not isinstance(ham, dict):
        raise OranHatasi(f"oran dilimi #{sira} nesne değil")
    bas, bit = _iso(ham.get("baslangic")), _iso(ham.get("bitis"))
    if bas is None or bit is None or bit < bas:
        raise OranHatasi(f"oran dilimi #{sira}: baslangic/bitis ISO tarih değil ya da bitis < baslangic")
    oran = ham.get("yillik_yuzde")
    if not _sayi_mi(oran) or oran < 0:
        raise OranHatasi(f"oran dilimi #{sira}: yillik_yuzde sayı değil")
    # Tür sessizce 'diger'e düşürülmez: türü bilinmeyen oranın hangi rejime
    # (yarıyıl kuralı, 7589 sınırı) tabi olduğu denetlenemez.
    tur = ham.get("tur")
    if tur not in FAIZ_TURLERI:
        raise OranHatasi(f"oran dilimi #{sira}: tur {tur!r} — {', '.join(FAIZ_TURLERI)} değerlerinden biri olmalı")
    kaynak = ham.get("kaynak") if isinstance(ham.get("kaynak"), str) else ""
    teyit = _iso(ham.get("teyit_tarihi"))
    dilim = {"sira": sira, "tur": tur, "baslangic": bas, "bitis": bit, "yillik_yuzde": float(oran),
             "kaynak": kaynak.strip(), "teyit_tarihi": teyit}
    return dilim, (not dilim["kaynak"] or teyit is None)


AZAMI_FAIZ_GUN = 36600      # ~100 yıl: bunun üstü veri hatasıdır (kaynak koruması), hesap yapılmaz
AZAMI_DILIM = 1000


def _araliklar(parcalar):
    """[(başlangıç, bitiş_hariç), …] → bitişik olanları birleştirip
    'YYYY-MM-DD..YYYY-MM-DD' (bitiş DAHİL) dizelerine çevirir."""
    sonuc = []
    for a, b in parcalar:
        if sonuc and sonuc[-1][1] == a:
            sonuc[-1][1] = b
        else:
            sonuc.append([a, b])
    return [f"{a.isoformat()}..{(b - _dt.timedelta(days=1)).isoformat()}" for a, b in sonuc]


def _yariyil_sonu(t):
    """t'nin içinde bulunduğu yarıyılın bittiği günün ertesi (1 Temmuz / 1 Ocak)."""
    return _dt.date(t.year, 7, 1) if t.month < 7 else _dt.date(t.year + 1, 1, 1)


def _yariyil_kurali(kurallar, tur, gun):
    """`gun` için `tur`a uygulanan yarıyıl kuralı (yoksa None)."""
    for kural in (kurallar or {}).get("yariyil_kurallari") or []:
        if tur in (kural.get("turler") or []):
            gecerli_bas = _iso(kural.get("gecerlilik_baslangici") or "")
            if gecerli_bas is None or gun >= gecerli_bas:
                return kural
    return None


def faiz_hesapla(anapara, baslangic, bitis, ham_dilimler, kurallar=None):
    """Basit faiz: her gün, o günü kapsayan dilimin yıllık oranıyla gün/365
    işler (artık yılda da 365 — mahkemenin hesabı farklıysa avukat düzeltir).
    Dönem [baslangic, bitis) — başlangıç günü dahil, bitiş günü hariç.
    Oran ÜRETMEZ; kapsanmayan/çakışan gün HESAPLANMAZ ve görünür yazılır.
    Hesap gün gün değil, sınırlarla bölünmüş ARALIKLAR üzerinden yapılır
    (maliyet dönem uzunluğundan bağımsız — kilitlenme koruması).

    PROJEKSİYON (oranın bilinmediği günler): sözleşme faizi oranı sözleşmeden
    gelir — projeksiyon sayılmaz. Yarıyıl kuralına tabi oran (3095 m.1-2)
    teyit edildiği yarıyılın sonuna kadar bilinir; sonrası projeksiyondur.
    Diğer türlerde teyit gününden sonrası projeksiyondur."""
    if bitis <= baslangic:
        raise OranHatasi("faiz bitiş tarihi başlangıçtan sonra olmalı")
    if (bitis - baslangic).days > AZAMI_FAIZ_GUN:
        raise OranHatasi(f"faiz dönemi {AZAMI_FAIZ_GUN} günü aşıyor — tarihleri kontrol edin (veri hatası)")
    if len(ham_dilimler) > AZAMI_DILIM:
        raise OranHatasi(f"oran dilimi sayısı {AZAMI_DILIM}'i aşıyor")
    kurallar = kurallar or {}
    dilimler, kaynaksiz, uyarilar = [], [], []
    for i, h in enumerate(ham_dilimler, 1):
        d, eksik = _dilim_dogrula(h, i)
        dilimler.append(d)
        if eksik:
            kaynaksiz.append(i)
        if 0 < d["yillik_yuzde"] < 1:
            uyarilar.append(f"dilim #{i}: {_oran_yazi(d['yillik_yuzde'])} — oran YÜZDE olarak mı (ör. 24) yoksa "
                            "kesir olarak mı (0,24) girildi? Kesirse faiz yüz kat küçük çıkar; girdiyi kontrol edin.")
    artik = [f"{y}-02-29" for y in range(baslangic.year, bitis.year + 1)
             if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) and baslangic <= _dt.date(y, 2, 29) < bitis]
    if artik:
        uyarilar.append("dönem artık yıl gününü içeriyor (" + ", ".join(artik) + ") — hesap gün/365 esasıyla "
                        "yapıldı; mahkemenin hesap esası farklıysa (366 gün) sonuç küçük farkla değişir.")
    gun1 = _dt.timedelta(days=1)
    sinirlar = {baslangic, bitis}

    def _ekle(t):
        if baslangic < t < bitis:
            sinirlar.add(t)

    for d in dilimler:
        _ekle(d["baslangic"])
        _ekle(d["bitis"] + gun1)
        if d["teyit_tarihi"] is not None:
            _ekle(d["teyit_tarihi"] + gun1)
            _ekle(_yariyil_sonu(d["teyit_tarihi"]))
    for kural in kurallar.get("yariyil_kurallari") or []:
        g = _iso(kural.get("gecerlilik_baslangici") or "")
        if g:
            _ekle(g)
    sinirlar = sorted(sinirlar)
    kapsanmayan, cakisan = [], []
    projeksiyon = 0
    birikim = {d["sira"]: {"gun": 0, "tutar": 0.0} for d in dilimler}
    for a, b in zip(sinirlar, sinirlar[1:]):
        gun = (b - a).days                      # [a, b) içinde kapsama ve kural sabittir
        kapsayan = [d for d in dilimler if d["baslangic"] <= a <= d["bitis"]]
        oranlar = {d["yillik_yuzde"] for d in kapsayan}
        if not kapsayan:
            kapsanmayan.append((a, b))
        elif len(oranlar) > 1:
            cakisan.append((a, b))
        else:
            d = kapsayan[0]
            birikim[d["sira"]]["gun"] += gun
            birikim[d["sira"]]["tutar"] += float(anapara) * d["yillik_yuzde"] / 100.0 / 365.0 * gun
            t = d["teyit_tarihi"]               # yoksa dilim zaten KAYNAKSIZ/TARİHSİZ sayıldı
            if t is not None and d["tur"] != "sozlesme":
                if _yariyil_kurali(kurallar, d["tur"], a):
                    if a >= _yariyil_sonu(t):
                        projeksiyon += gun
                elif a > t:
                    projeksiyon += gun

    hatirlatma = []
    if not kurallar and any(d["tur"] in ("kanuni", "temerrut", "avans") for d in dilimler):
        hatirlatma.append("tarife.json'da 'oran_kurallari' yok — kanuni/temerrüt/avans faizinin yarıyıl ve "
                          "rejim sınırları (3095 m.1-2; 7589) DENETLENEMEDİ")
    for d in dilimler:
        # Yarıyıl kuralı (3095 m.1-2): oran yıllık belirlenir, 30 Haziran'da
        # değişebilir → 1 Ocak / 1 Temmuz sınırını kesen TEK dilim doğrulanmış
        # sayılmaz. Kural türe ve geçerlilik başlangıcına göre veriden okunur.
        for kural in kurallar.get("yariyil_kurallari") or []:
            if d["tur"] not in (kural.get("turler") or []):
                continue
            gecerli_bas = _iso(kural.get("gecerlilik_baslangici") or "")
            for yil in range(d["baslangic"].year, d["bitis"].year + 1):
                for sinir in (_dt.date(yil, 1, 1), _dt.date(yil, 7, 1)):
                    if d["baslangic"] < sinir <= d["bitis"] and (gecerli_bas is None or sinir >= gecerli_bas):
                        hatirlatma.append(
                            f"dilim #{d['sira']} ({d['tur']}) {sinir.isoformat()} sınırını kesiyor — oran yıllık "
                            "belirlenir ve yarıyılda değişebilir; aynı oran sürse bile sınırın iki yanını ayrı "
                            f"dilim ve ayrı teyitle girin [{kural.get('kaynak', 'oran_kurallari')}]")
        for r in kurallar.get("rejim_sinirlari") or []:
            t = _iso(r.get("tarih"))
            if t and d["tur"] in (r.get("turler") or []) and d["baslangic"] < t <= d["bitis"]:
                hatirlatma.append(f"dilim #{d['sira']} ({d['tur']}) REJİM SINIRI {t.isoformat()} kesiyor — tek "
                                  f"oranla hesaplanamaz [{r.get('kaynak', '')}]")
    satirlar = []
    for d in dilimler:
        b = birikim[d["sira"]]
        satirlar.append({"sira": d["sira"], "tur": d["tur"], "baslangic": d["baslangic"].isoformat(),
                         "bitis": d["bitis"].isoformat(), "yillik_yuzde": d["yillik_yuzde"],
                         "kaynak": d["kaynak"] or None,
                         "teyit_tarihi": d["teyit_tarihi"].isoformat() if d["teyit_tarihi"] else None,
                         "gun": b["gun"], "tutar": round(b["tutar"], 2)})
    toplam = round(sum(s["tutar"] for s in satirlar), 2)
    teyitli = not (kaynaksiz or kapsanmayan or cakisan or projeksiyon or hatirlatma)
    return {"anapara": float(anapara), "baslangic": baslangic.isoformat(), "bitis": bitis.isoformat(),
            "gun": (bitis - baslangic).days, "hesaplanan_gun": sum(s["gun"] for s in satirlar),
            "tutar": toplam, "dilimler": satirlar, "kaynaksiz_dilim": kaynaksiz,
            "kapsanmayan": _araliklar(kapsanmayan), "cakisan": _araliklar(cakisan),
            "projeksiyon_gun": projeksiyon, "hatirlatmalar": hatirlatma, "uyarilar": uyarilar,
            "teyitli": teyitli}


# ───────────────────────────── rapor ────────────────────────────────────

def _faiz_raporu(fz):
    L = ["FAİZ (basit faiz aritmetiği; gün/365, artık yılda da 365 — script oran ÜRETMEZ, oran dönemi ve "
         "kaynağıyla verilir; faiz harç matrahına EKLENMEZ, ekleneceğini avukat değerlendirir)"]
    L.append(f"  Anapara {tl(fz['anapara'])} · dönem {fz['baslangic']} → {fz['bitis']} "
             f"({fz['gun']} gün; hesaplanan {fz['hesaplanan_gun']} gün)")
    for s in fz["dilimler"]:
        L.append(f"  dilim #{s['sira']} {s['tur']}: {s['baslangic']}..{s['bitis']} · {_oran_yazi(s['yillik_yuzde'])}"
                 f" · {s['gun']} gün · {tl(s['tutar'])}")
        L.append(f"      kaynak: {s['kaynak'] or 'YOK'} · teyit: {s['teyit_tarihi'] or 'YOK'}")
    L.append(f"  FAİZ TOPLAMI (hesaplanan günler)           : {tl(fz['tutar'])}")
    if fz["kaynaksiz_dilim"]:
        L.append("  ⚠ KAYNAKSIZ/TARİHSİZ ORAN — dilim " + ", ".join(f"#{i}" for i in fz["kaynaksiz_dilim"])
                 + ": oranın resmî kaynağı (RG/TCMB künyesi) ve teyit tarihi yok; faiz kalemi ÇIPA, "
                 "dilekçeye/müvekkile kesin rakam olarak verilemez.")
    if fz["kapsanmayan"]:
        L.append("  ⚠ KAPSANMAYAN GÜNLER (oran verilmedi — faiz HESAPLANMADI): " + ", ".join(fz["kapsanmayan"]))
    if fz["cakisan"]:
        L.append("  ⚠ ÇAKIŞAN ORAN DİLİMLERİ (farklı oranlar — faiz HESAPLANMADI): " + ", ".join(fz["cakisan"]))
    if fz["projeksiyon_gun"]:
        L.append(f"  ⚠ PROJEKSİYON: {fz['projeksiyon_gun']} gün oranın teyit tarihinden SONRASINA düşüyor — "
                 "gelecek oran bilinmez, bu kısım bugünkü oranla ÇIPADIR.")
    for h in fz["hatirlatmalar"]:
        L.append(f"  ⚠ {h}")
    for u in fz.get("uyarilar") or []:
        L.append(f"  ! {u}")
    L.append("  FAİZ KALEMİ: " + ("TEYİTLİ (tüm günler kaynaklı ve teyit tarihli oranla hesaplandı)"
                               if fz["teyitli"] else "ÇIPA — yukarıdaki uyarılar kapanmadan kesin rakam değildir"))
    return L


def rapor(sonuc, tarife, tarife_yolu, faiz=None):
    g, h, kv, b = sonuc["girdi"], sonuc["harc"], sonuc["karsi_vekalet"], sonuc["gider_bandi"]
    L = []
    L.append("MALİYET CETVELİ — deterministik aritmetik (oa-strateji · P1-11)")
    L.append(f"Tarife: {tarife_yolu} · yıl {tarife['yil']} · MCP teyit {tarife['mcp_teyit_tarihi']}")
    L.append(f"Kaynak: {tarife.get('kaynak') or '—'}")
    if g["merci"] != "asliye" or h.get("basvuru_satiri"):
        L.append(f"Merci: {MERCI_ADI[g['merci']]}" + (f" — başvurma: {h['basvuru_satiri']}" if h.get("basvuru_satiri") else ""))
        hm = tarife.get("harc_merci") or {}
        gecerli, neden = merci_blogu_gecerli(tarife)
        L.append("Merci kalemleri: " + (f"RG {hm.get('rg')} · yürürlük {hm.get('yururluk')} · teyit {hm.get('teyit_tarihi')}"
                                        if gecerli else f"TEYİTSİZ ({neden})"))
    L.append("")
    L.append(f"Dava değeri            : {tl(g['deger'])}")
    L.append(f"Kısmi kabul (oran)     : {g['kismi_kabul']:.2f} → kabul {tl(g['kabul'])} · ret {tl(g['ret'])}")
    L.append("")
    L.append("HARÇ (492 s.K. (1) sayılı tarife; m.28/a peşin oran)" if g["merci"] != "vergi"
             else "HARÇ (492 s.K. (3) sayılı tarife — vergi yargısı harçları)")
    L.append(f"  Başvurma harcı (maktu)                    : {tl(h['basvuru_maktu'])}")
    L.append(f"  Karar ve ilam harcı — dava değeri üzerinden: {tl(h['karar_ilam_dava_degeri'])}")
    if g["merci"] == "vergi":
        L.append("  Peşin karar harcı (açılışta)               : TEYİT BEKLİYOR — hesaplanmadı")
    else:
        L.append(f"  Peşin karar harcı (açılışta)               : {tl(h['karar_ilam_pesin'])}")
    if g["merci"] == "vergi":
        L.append("  Karar harcı — hüküm altına alınan değer    : TEYİT BEKLİYOR — hesaplanmadı")
    else:
        L.append(f"  Karar harcı — hüküm altına alınan değer    : {tl(h['karar_ilam_hukum_degeri'])}")
    L.append(f"  DAVA AÇILIŞ TOPLAMI (başvuru + peşin)      : {tl(h['dava_acilis_toplam'])}")
    for n in sonuc.get("notlar") or []:
        L.append(f"  NOT: {n}")
    L.append("")
    if g["merci"] in AVK168_MAKTU_MERCILER:
        L.append("KARŞI VEKÂLET (Av.K. m.168/2 — MAKTU; nispi dilim uygulanmaz; AAÜT m.15/1 tamamı/yarısı, "
                 "m.3/1 taban)")
    else:
        L.append("KARŞI VEKÂLET (AAÜT m.13 — üçüncü kısım; maktu taban; kabul/ret tavanı)")

    def _kv_yaz(x):
        # v0.5.18 K2 — None iki ayrı sebeple doğar: tarife alanı null (EKSIK_MESAJ) ya da
        # KURAL okunamadı (`hesaplanamayan`; tarife doludur). İkincisine "tarife alanı null"
        # demek yanlış teşhistir — avukatı tarife.json doldurmaya yönlendirir, o da kapatmaz.
        if x is None and sonuc.get("hesaplanamayan"):
            return "HESAPLANAMADI — kural resmî metinden okunamadı (aşağıdaki HESAPLANAMAYAN satırı)"
        return tl(x)

    L.append(f"  Lehe (kabul edilen kısım)                  : {_kv_yaz(kv['lehe_kabul_kismi'])}")
    L.append(f"  ALEYHE (reddedilen kısım — müvekkil öder)  : {_kv_yaz(kv['aleyhe_ret_kismi'])}")
    for hk in sonuc.get("hesaplanamayan") or []:
        L.append(f"  HESAPLANAMAYAN — kural resmî metinden okunamadı, rakam ÜRETİLMEDİ: {hk}")
    for n in sonuc.get("vekalet_notlari") or []:
        L.append(f"  NOT: {n}")
    L.append("")
    L.append("YARGILAMA GİDERİ BANDI (HMK m.323 kalemleri; paylaştırma m.326/2 — mahkeme takdiri, çıpa)")
    L.append(f"  ALT (açılış zorunlu + elle girilen gider)  : {tl(b['alt'])}")
    _ust_ek = {
        "maktu_ust_sinir": (" — aleyhe vekâlet: kısmi dağılım hesaplanamadı, bilinen MAKTU ÜST SINIR olarak "
                            "eklendi (müvekkil için güvenli yön; gerçek tutar bundan düşük olabilir)"),
        "haric": " — aleyhe vekâlet DAHİL DEĞİL (hesaplanamadı/teyitsiz): gerçek azami maruziyet bu rakamdan YÜKSEK",
    }.get(b.get("ust_vekalet"), "")
    L.append(f"  ÜST (tam harç + keşif/kanun yolu harçları + aleyhe vekâlet + elle gider): {tl(b['ust'])}{_ust_ek}")
    L.append(f"  Elle girilen: bilirkişi {tl(g['bilirkisi'])} · diğer {tl(g['diger_gider'])} "
             "(tarifesiz kalemler — avukat girer, script uydurmaz)")
    L.append("")
    if faiz is not None:
        L.extend(_faiz_raporu(faiz))
        L.append("")
    if sonuc["eksik_alanlar"]:
        L.append("KISMİ CETVEL — şu tarife alanları null (MCP'den teyit edilemedi), ilgili kalemler "
                 "HESAPLANMADI: " + ", ".join(sonuc["eksik_alanlar"]))
        L.append("→ tarife.json'u resmî kaynaktan (Mevzuat MCP / Resmî Gazete) doldur, teyit tarihini yaz.")
    if sonuc.get("hesaplanamayan"):
        L.append("KISMİ CETVEL — HESAPLANAMAYAN KALEMLER (tarife dolu olsa da kural resmî metinden okunamadı; "
                 "rakam ÜRETİLMEDİ, tarife.json doldurmak bunu kapatmaz): "
                 + " | ".join(sonuc["hesaplanamayan"]))
    L.append("ZAMAN NOTU: kanun yolu harçları, bakiye karar harcı ve karşı vekâlet gelecekte doğar; bugünkü yıl "
             "tarifesiyle hesaplanan tutar ÇIPADIR (AAÜT m.21: ücret takdirinde hükmün verildiği tarihteki tarife).")
    L.append("NOT: Bu cetvel olasılık/kazanma şansı ÜRETMEZ; başarı bandı (güçlü/dengeli/zayıf/belirsiz) "
             "modelin gerekçeli işidir. Rakamlar tarife aritmetiğidir, hukuki yorum değildir.")
    return "\n".join(L)


# ───────────────────────────── CLI ──────────────────────────────────────

def _faiz_dilimleri(a):
    """CLI → oran dilimleri listesi. Oran hiç verilmediyse OranHatasi (exit 1)."""
    if a.oranlar and a.faiz_orani is not None:
        raise OranHatasi("--oranlar ile --faiz-orani birlikte verilemez")
    if a.oranlar:
        return oranlar_yukle(a.oranlar)
    if a.faiz_orani is None:
        raise OranHatasi("faiz istendi ama oran verilmedi — script oran ÜRETMEZ: --oranlar <json> ya da "
                         "--faiz-orani (+ --faiz-kaynak, --faiz-teyit) verin")
    if a.faiz_turu is None:
        raise OranHatasi("--faiz-orani ile --faiz-turu zorunlu (kanuni/temerrut/avans/sozlesme/diger) — türü "
                         "bilinmeyen oranın yarıyıl/rejim kuralı denetlenemez")
    return [{"tur": a.faiz_turu, "baslangic": a.faiz_baslangic, "bitis": a.faiz_bitis,
             "yillik_yuzde": a.faiz_orani, "kaynak": a.faiz_kaynak or "",
             "teyit_tarihi": a.faiz_teyit or ""}]


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Deterministik maliyet cetveli — tarife.json'dan harç/karşı vekâlet/gider bandı "
                    "(olasılık üretmez; teyitsiz/bayat tarifede FAIL-CLOSED exit 2; oran uydurmaz).")
    p.add_argument("--deger", type=float, required=True, help="dava/talep değeri (TL)")
    p.add_argument("--kismi-kabul", type=float, default=1.0,
                   help="kabul oranı 0..1 (ör. 0.6 = değerin yüzde altmışı kabul, kalanı ret); varsayılan 1.0")
    p.add_argument("--tarife", default=VARSAYILAN_TARIFE, help="tarife.json yolu (varsayılan: script yanı)")
    p.add_argument("--yil", type=int, default=None, help="hesap yılı (varsayılan: bugünün yılı)")
    p.add_argument("--bilirkisi", type=float, default=0.0, help="bilirkişi ücreti (elle, TL)")
    p.add_argument("--diger-gider", type=float, default=0.0, help="tebligat/posta/keşif dışı diğer gider (elle, TL)")
    p.add_argument("--merci", choices=sorted(MERCILER), default="asliye",
                   help="davanın görüldüğü merci (başvurma harcı ve kanun yolu satırını seçer; varsayılan asliye)")
    p.add_argument("--olum-cismani", action="store_true",
                   help="ölüm/cismani zarar sebebiyle maddi-manevi tazminat davası: peşin harç yirmide bir (492 m.28/a)")
    p.add_argument("--faiz-baslangic", help="faiz başlangıcı YYYY-MM-DD (dahil)")
    p.add_argument("--faiz-bitis", help="faiz bitişi YYYY-MM-DD (hariç)")
    p.add_argument("--faiz-anapara", type=float, default=None, help="faiz anaparası (varsayılan: --deger)")
    p.add_argument("--oranlar", help="dilimli oran dosyası (JSON; her dilim kaynak + teyit tarihi taşır)")
    p.add_argument("--faiz-orani", type=float, default=None, help="tek dilim kısayolu: yıllık oran (yüzde)")
    p.add_argument("--faiz-turu", choices=FAIZ_TURLERI, default=None,
                   help="tek dilim kısayolu: oran türü (--faiz-orani ile ZORUNLU)")
    p.add_argument("--faiz-kaynak", default="", help="tek dilim kısayolu: oranın resmî kaynağı (RG/TCMB künyesi)")
    p.add_argument("--faiz-teyit", default="", help="tek dilim kısayolu: oranın teyit tarihi YYYY-MM-DD")
    p.add_argument("--json", action="store_true", help="sonucu JSON olarak da bas")
    a = p.parse_args(argv)

    if a.deger <= 0:
        print("HATA: --deger pozitif olmalı.", file=sys.stderr)
        return 1
    if not (0.0 <= a.kismi_kabul <= 1.0):
        print("HATA: --kismi-kabul 0 ile 1 arasında olmalı.", file=sys.stderr)
        return 1
    faiz_istendi = any(x is not None and x != "" for x in (a.faiz_baslangic, a.faiz_bitis, a.oranlar, a.faiz_orani))
    faiz_bas = faiz_bit = None
    if faiz_istendi:
        faiz_bas, faiz_bit = _iso(a.faiz_baslangic), _iso(a.faiz_bitis)
        if faiz_bas is None or faiz_bit is None:
            print("HATA: faiz için --faiz-baslangic ve --faiz-bitis (YYYY-MM-DD) birlikte gerekir.", file=sys.stderr)
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
        if a.json:   # makine tüketicisi de sessiz kalmasın: hata da JSON olarak gelir
            print(json.dumps({"durum": "FAIL-CLOSED", "neden": str(e), "cikis_kodu": 2}, ensure_ascii=False))
        return 2

    faiz = None
    if faiz_istendi:
        try:
            dilimler = _faiz_dilimleri(a)
            faiz = faiz_hesapla(a.faiz_anapara if a.faiz_anapara is not None else a.deger,
                                faiz_bas, faiz_bit, dilimler, tarife.get("oran_kurallari"))
        except OranHatasi as e:
            print(f"HATA (faiz): {e}", file=sys.stderr)
            print("Faiz HESAPLANMADI — oran resmî kaynağıyla verilmeden faiz rakamı üretilmez.", file=sys.stderr)
            if a.json:
                print(json.dumps({"durum": "FAİZ HESAPLANMADI", "neden": str(e), "cikis_kodu": 1},
                                 ensure_ascii=False))
            return 1

    sonuc = hesapla(a.deger, a.kismi_kabul, tarife, a.bilirkisi, a.diger_gider, a.merci, a.olum_cismani)
    if faiz is not None:
        sonuc["faiz"] = faiz
    print(rapor(sonuc, tarife, a.tarife, faiz))
    if a.json:
        print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    teyitsiz_faiz = faiz is not None and not faiz["teyitli"]
    return 2 if (sonuc["eksik_alanlar"] or sonuc.get("hesaplanamayan") or teyitsiz_faiz) else 0


if __name__ == "__main__":
    sys.exit(main())

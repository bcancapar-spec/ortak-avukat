#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
sure_nobetci.py — oa-sure SÜRE NÖBETÇİSİ (oturum açılışı deterministik özet)

hesapla_sure.py ile hesaplanıp `_oa/sureler.json`'a MEKANİK yazılan (halüsinasyon
çıpası — `oa_hafiza.py sure-flag` ile) son günleri BUGÜNE göre okur ve tek
bakışta durum çıkarır: geçmiş (kaçmış), yaklaşan (D-1/D-3/D-7 penceresi) ve
ileri süreleri işaretler, en yakın/geçmiş olanları üste alır. Amaç: her oturum
açılışında "hangi süre yanıyor" sorusunu tek komutla, sessiz kaçış olmadan
yanıtlamak.

Bu script HUKUKİ hesap YAPMAZ; son günler zaten hesapla_sure.py çıktısıdır.
Nöbetçi yalnızca defteri BUGÜNE göre tarar ve sıralar (deterministik). Adli
tatil/başlangıç anı gibi kurallar buraya değil hesapla_sure.py'ye aittir.

KANONİK DEFTER: `_oa/sureler.json` — `oa_hafiza.py sure-flag` ile aynı dosya
(mimari tekil kaynak; oa-pipeline/scripts/oa_hafiza.py'nin `init`/`sure-flag`
komutlarıyla PAYLAŞILIR — ayrı bir `_oa/defter/sureler.json` YOKTUR/kullanılmaz).
Şema TOLERANSLIDIR — ikisi de kabul edilir:
  (a) üst düzey LİSTE   : [ {"son_gun": "YYYY-MM-DD", "aciklama": "...", "tur": "usul|maddi"}, ... ]
  (b) sarmalayıcı (oa_hafiza.py'nin ürettiği biçim):
      {"flagler": [ {"son_gun"|"tarih": "YYYY-MM-DD", "aciklama": "...", "kural": "...", "tur": "..."} , ... ]}
Tarih alanı önce "son_gun", yoksa geriye-uyumlu "tarih" olarak okunur (iki alan
adı da desteklenir — oa_hafiza.py her iki alanı birlikte yazar). Defter yoksa
çökmez; "süre kaydı yok, oa-sure ile ekleyin" der.

DÜZELTME REJİMİ — APPEND-ONLY (v0.5.14; denetim bulgusu B-17)
En sık kullanıcı hareketi yanlış girilmiş bir tebliğ tarihini DÜZELTMEKtir.
Defterden kayıt SİLİNMEZ (denetim izi kayıpsızlığı anayasal): düzeltme, deftere
eklenen bir İPTAL KAYDIdır. Nöbetçi kapatılmış kaydı listede DENETİM İZİ olarak
gösterir ama SAYMAZ ve acil sayımına katmaz — hayalet alarm gerçek alarmı
boğmaz. Kapatma iki yoldan okunur:
  (a) kaydın kendi alanı  : {"durum": "iptal"|"duzeltildi"} ya da {"iptal": true}
  (b) ayrı bir düzeltme kaydı: {"iptal_eder": "<kimlik>", "gerekce": "..."}
      (eş anlamlı alan adı: "duzeltir"; değer tek kimlik ya da kimlik listesi)
Her kaydın KİMLİĞİ deterministiktir (son_gun + kural + açıklama üzerinden
üretilen 8 haneli parmak izi) ve her satırda `#xxxxxxxx` olarak basılır; kaydın
kendi "id" alanı varsa o kullanılır.

ÇELİŞKİ UYARISI: aynı `kural` için birden çok AKTİF ve FARKLI son gün varsa en
az biri hayalettir — nöbetçi bunu adıyla raporlar ve DİKKAT (exit 3) sınıfına
alır (bozuk kayıt ile aynı sınıf; ayrı bir çıkış kodu İCAT EDİLMEZ).

Kullanım (Windows/PowerShell — 'python'):
  python sure_nobetci.py [--kok <klasör>]
    --kok : çalışma kökü; defter <kök>/_oa/sureler.json (varsayılan: .)
  python sure_nobetci.py --kok <klasör> --iptal <kimlik> --gerekce "<neden>"
    deftere APPEND-ONLY iptal/düzeltme kaydı ekler (silme YOK). Kimlik nöbet
    listesindeki `#xxxxxxxx` değeridir; gerekçe zorunludur (denetim izi).

İşaretçiler (ASCII):
  [!!!] GEÇMİŞ veya BUGÜN (son gün) · [!] yaklaşan (D-1..D-7) · [ ] ileri
  [×] iptal edilmiş / düzeltilmiş (nöbet dışı — sayılmaz) · [?] okunamayan
Çıkış kodu:
  0 = defter yok / boş ya da hiçbir süre acil değil (ve --iptal başarılı)
  3 = en az bir GEÇMİŞ/BUGÜN/yaklaşan süre VAR ya da okunamayan (bozuk) kayıt
      var ya da aynı kuralda çelişik aktif son gün var — DİKKAT
  1 = defter var ama okunamıyor / biçim bozuk (JSON hatası) ya da --iptal
      hedefi bulunamadı
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import hashlib
import json
import os
import sys
from datetime import date, datetime

CIZGI = "=" * 66
ALT = "-" * 66
YAKIN_ESIK = 7  # gün — D-1..D-7 "yaklaşan" penceresi

# Kaydın kendi alanıyla kapatıldığını gösteren değerler (append-only rejim).
KAPALI_DURUMLAR = {"iptal", "iptal_edildi", "duzeltildi", "düzeltildi",
                   "superseded", "gecersiz", "geçersiz"}
# Bir kaydın BAŞKA kaydı kapattığını gösteren alan adları.
IPTAL_ALANLARI = ("iptal_eder", "duzeltir", "düzeltir")


def _defter_yolu(kok):
    # KANONİK yol — oa_hafiza.py init/sure-flag ile AYNI dosya (mimari tekil kaynak).
    return os.path.join(kok, "_oa", "sureler.json")


def _kayitlari_al(veri):
    """Üst düzey liste beklenir; toleranslı olarak yaygın sarmalayıcıları da açar.
    'flagler' — oa_hafiza.py sure-flag'in ürettiği kanonik sarmalayıcı anahtarıdır."""
    if isinstance(veri, list):
        return veri
    if isinstance(veri, dict):
        for anahtar in ("flagler", "sureler", "kayitlar", "records", "items"):
            if isinstance(veri.get(anahtar), list):
                return veri[anahtar]
    return None


def _tur_etiketi(kayit):
    tur = ""
    if isinstance(kayit, dict):
        tur = str(kayit.get("tur") or "").strip().lower()
    if tur in ("usul", "maddi"):
        return "[%s]" % tur
    return "[—]"


def _aciklama(kayit):
    if isinstance(kayit, dict):
        a = str(kayit.get("aciklama") or "").strip()
        if a:
            return a
    return "(açıklama yok)"


def _son_gun(kayit):
    """(date|None, ham_metin) — bozuk/eksik son_gun None döner (çökme yok).
    Alan adı önce 'son_gun' (kanonik), yoksa 'tarih' (oa_hafiza.py sure-flag
    geriye-uyumluluk alanı) olarak okunur."""
    ham = ""
    if isinstance(kayit, dict):
        ham = str(kayit.get("son_gun") or kayit.get("tarih") or "").strip()
    if not ham:
        return None, ham
    try:
        return date.fromisoformat(ham), ham
    except ValueError:
        return None, ham


def _kural(kayit):
    if isinstance(kayit, dict):
        return str(kayit.get("kural") or "").strip().lower()
    return ""


def _kayit_kimligi(kayit):
    """8 haneli deterministik parmak izi — kaydı ADRESLENEBİLİR yapar.

    Düzeltme ancak adreslenebilir kayıtla mümkündür. Kaydın kendi "id" alanı
    varsa o esas alınır; yoksa (son_gun|kural|aciklama) üçlüsünden türetilir.
    Kimlik İÇERİKTEN türediği için defter yeniden sıralansa da değişmez.
    Not: aynı üçlüyü taşıyan iki kayıt AYNI kimliği alır (ayırt edilemez
    kopyalardır) — biri iptal edilirse ikisi de nöbetten düşer; ayrı tutulmaları
    gerekiyorsa açıklamaları ayrıştırılır.
    """
    if isinstance(kayit, dict) and str(kayit.get("id") or "").strip():
        return str(kayit["id"]).strip()[:32]
    _, ham = _son_gun(kayit)
    cekirdek = "|".join([ham, _kural(kayit), _aciklama(kayit)])
    return hashlib.sha1(cekirdek.encode("utf-8")).hexdigest()[:8]


def _iptal_hedefleri(kayit):
    """Bu kaydın KAPATTIĞI kimliklerin listesi (tek değer ya da liste)."""
    if not isinstance(kayit, dict):
        return []
    hedefler = []
    for alan in IPTAL_ALANLARI:
        ham = kayit.get(alan)
        if isinstance(ham, str) and ham.strip():
            hedefler.append(ham.strip())
        elif isinstance(ham, (list, tuple)):
            hedefler.extend(str(h).strip() for h in ham if str(h).strip())
    return hedefler


def _kendi_kapali_mi(kayit):
    """Kayıt KENDİ alanıyla kapatılmış mı ({"durum": ...} / {"iptal": true})."""
    if not isinstance(kayit, dict):
        return False
    if kayit.get("iptal") is True:
        return True
    durum = str(kayit.get("durum") or "").strip().lower()
    return durum in KAPALI_DURUMLAR


def _kategori(gun, bugun):
    """(anahtar, isaret, etiket) — bugüne göre sınıf."""
    fark = (gun - bugun).days
    if fark < 0:
        return "GECMIS", "[!!!]", "GEÇMİŞ (%d gün önce doldu)" % (-fark)
    if fark == 0:
        return "BUGUN", "[!!!]", "BUGÜN — SON GÜN"
    if fark <= YAKIN_ESIK:
        return "YAKLASAN", "[!]", "D-%d (yaklaşıyor)" % fark
    return "ILERI", "[ ]", "D-%d" % fark


def _yaz_kayit(isaret, ham_gun, etiket, tur_tag, aciklama, kimlik=""):
    kim = ("#%s " % kimlik) if kimlik else ""
    print("%-6s%-12s%-27s%-8s%s%s" % (isaret, ham_gun, etiket, tur_tag, kim, aciklama))


# Aynı kural altında BİLİNÇLİ olarak iki son gün üreten tek üretici:
# `hesapla_sure.py --uets` 7201 m.7/a karine senaryosunu AYRI kayıt olarak
# yazar (kayıpsızlık — iki son gün de görünür). Bu bir çelişki DEĞİLDİR;
# çelişki taramasının dışında tutulur, listede normal şekilde görünmeye devam eder.
CELISKI_DISI_IZLER = ("uets karine",)


def _celiski_disi(aciklama):
    dusuk = (aciklama or "").lower()
    return any(iz in dusuk for iz in CELISKI_DISI_IZLER)


def _celiskiler(gecerli):
    """Aynı `kural` için birden çok AKTİF ve FARKLI son gün → hayalet süre.

    Script hukuki hüküm VERMEZ; hangisinin doğru olduğunu söylemez — yalnız
    defterin kendi içinde çeliştiğini gösterir ve düzeltme yolunu işaret eder.
    """
    gruplar = {}
    for kayit in gecerli:
        kural = kayit["kural"]
        if kural and not _celiski_disi(kayit["aciklama"]):
            gruplar.setdefault(kural, []).append(kayit)
    cikan = []
    for kural, uyeler in sorted(gruplar.items()):
        gunler = sorted({u["gun"].isoformat() for u in uyeler})
        if len(gunler) > 1:
            cikan.append((kural, gunler,
                          [u["kimlik"] for u in sorted(uyeler, key=lambda x: x["gun"])]))
    return cikan


def _defteri_kaydet(yol, veri, kayitlar):
    """Kayıt listesini defterin KENDİ şemasını (liste / sarmalayıcı) koruyarak yazar."""
    if isinstance(veri, dict):
        for anahtar in ("flagler", "sureler", "kayitlar", "records", "items"):
            if isinstance(veri.get(anahtar), list):
                veri[anahtar] = kayitlar
                govde = veri
                break
        else:
            govde = {"flagler": kayitlar}
    else:
        govde = kayitlar
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(govde, f, ensure_ascii=False, indent=2)


def _iptal_uygula(yol, veri, kayitlar, kimlik, gerekce):
    """APPEND-ONLY iptal: hiçbir kayıt silinmez/değiştirilmez, kayıt EKLENİR."""
    hedef = None
    for kayit in kayitlar:
        if _kayit_kimligi(kayit) == kimlik:
            hedef = kayit
            break
    if hedef is None:
        print("HATA: '%s' kimlikli kayıt defterde bulunamadı — hiçbir şey yazılmadı.\n"
              "(Kimlik, nöbet listesindeki `#xxxxxxxx` değeridir; önce bayraksız koşup "
              "listeyi görün.)" % kimlik, file=sys.stderr)
        return 1
    kayit_ts = datetime.now().astimezone().isoformat(timespec="seconds")
    kayitlar.append({
        "kayit_turu": "iptal",
        "iptal_eder": kimlik,
        "gerekce": gerekce,
        "iptal_edilen_son_gun": _son_gun(hedef)[1],
        "iptal_edilen_aciklama": _aciklama(hedef),
        "kayit": kayit_ts,
    })
    _defteri_kaydet(yol, veri, kayitlar)
    print("İPTAL KAYDI EKLENDİ (append-only — hiçbir kayıt silinmedi):")
    print("  hedef #%s · %s · %s" % (kimlik, _son_gun(hedef)[1] or "—", _aciklama(hedef)))
    print("  gerekçe: %s" % gerekce)
    print("Yazıldı: %s" % yol)
    print("NOT: doğru son günü ayrıca deftere işleyin "
          "(`oa_hafiza.py sure-flag --tarih ... --aciklama \"...\" --kural ...`); "
          "iptal kaydı yalnız HAYALET süreyi nöbetten düşürür, yenisini KURMAZ.")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="oa-sure süre nöbetçisi — sureler.json'u bugüne göre tarar ve sıralar.")
    ap.add_argument("--kok", default=".",
                    help="çalışma kökü; defter <kök>/_oa/sureler.json (varsayılan: .)")
    ap.add_argument("--iptal", metavar="KIMLIK",
                    help="APPEND-ONLY düzeltme: verilen `#xxxxxxxx` kimlikli kaydı "
                         "iptal/düzeltildi olarak İŞARETLEYEN yeni bir kayıt ekler "
                         "(silme YOK — denetim izi korunur). --gerekce zorunludur.")
    ap.add_argument("--gerekce", metavar="METIN",
                    help="--iptal ile zorunlu: kaydın neden düzeltildiği (denetim izi).")
    a = ap.parse_args()

    kok = os.path.abspath(a.kok)
    bugun = date.today()
    yol = _defter_yolu(kok)

    if a.iptal and not (a.gerekce or "").strip():
        print("HATA: --iptal, --gerekce ister (denetim izi zorunludur; "
              "silme değil işaretleme yapıyoruz).", file=sys.stderr)
        sys.exit(2)
    if a.gerekce and not a.iptal:
        print("HATA: --gerekce yalnız --iptal ile birlikte kullanılır.", file=sys.stderr)
        sys.exit(2)

    print(CIZGI)
    print("SÜRE NÖBETÇİSİ — bugün: %s" % bugun.isoformat())
    print("Defter: %s" % yol)
    print(CIZGI)

    # ── defter yok → çökme yok, yönlendir ──────────────────────────────────
    if not os.path.isfile(yol):
        if a.iptal:
            print("HATA: defter yok — iptal edilecek kayıt yok (%s)." % yol,
                  file=sys.stderr)
            sys.exit(1)
        print("Süre kaydı yok, oa-sure ile ekleyin.")
        print("(hesapla_sure.py ile son gün hesaplayıp `oa_hafiza.py sure-flag --tarih ... "
              "--aciklama \"...\" --kural ...` ile bu deftere işleyin — halüsinasyon çıpası.)")
        sys.exit(0)

    # ── defter oku → JSON bozuksa çökme yok, exit 1 ────────────────────────
    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            veri = json.load(f)
    except (OSError, ValueError) as e:
        print("HATA: defter okunamadı / biçim bozuk (%s)." % e, file=sys.stderr)
        print("Beklenen şema: [ {\"son_gun\":\"YYYY-MM-DD\",\"aciklama\":\"...\",\"tur\":\"usul|maddi\"}, ... ]",
              file=sys.stderr)
        sys.exit(1)

    kayitlar = _kayitlari_al(veri)
    if kayitlar is None:
        print("HATA: beklenen üst düzey LİSTE ya da {\"flagler\":[...]} sarmalayıcısı değil (şema uyumsuz).",
              file=sys.stderr)
        print("Beklenen: [ {\"son_gun\":\"YYYY-MM-DD\",\"aciklama\":\"...\",\"tur\":\"usul|maddi\"}, ... ] "
              "VEYA {\"flagler\": [...]}", file=sys.stderr)
        sys.exit(1)

    if not kayitlar:
        if a.iptal:
            print("HATA: defter boş — iptal edilecek kayıt yok.", file=sys.stderr)
            sys.exit(1)
        print("Süre kaydı yok (defter boş), oa-sure ile ekleyin.")
        sys.exit(0)

    # ── APPEND-ONLY düzeltme kipi (B-17) ───────────────────────────────────
    if a.iptal:
        sys.exit(_iptal_uygula(yol, veri, kayitlar, a.iptal.lstrip("#").strip(),
                               a.gerekce.strip()))

    # ── kapatma haritası: hangi kimlikler iptal/düzeltilmiş (append-only) ──
    kapatilan = set()
    for kayit in kayitlar:
        kapatilan.update(_iptal_hedefleri(kayit))

    # ── ayrıştır: aktif / kapatılmış / bozuk-tarihsiz / saf düzeltme ───────
    gecerli, bozuk, kapali, duzeltme = [], [], [], []
    for kayit in kayitlar:
        kimlik = _kayit_kimligi(kayit)
        gun, ham = _son_gun(kayit)
        hedefler = _iptal_hedefleri(kayit)
        if hedefler:
            duzeltme.append((kimlik, hedefler, _aciklama(kayit),
                             str(kayit.get("gerekce") or "").strip()
                             if isinstance(kayit, dict) else ""))
            if gun is None and not ham:
                # saf düzeltme kaydı — bir SÜRE değildir; bozuk sayılmaz
                continue
        if kimlik in kapatilan or _kendi_kapali_mi(kayit):
            kapali.append((kimlik, ham, _tur_etiketi(kayit), _aciklama(kayit)))
            continue
        if gun is None:
            bozuk.append((kimlik, ham, _tur_etiketi(kayit), _aciklama(kayit)))
        else:
            anahtar, isaret, etiket = _kategori(gun, bugun)
            gecerli.append({"gun": gun, "anahtar": anahtar, "isaret": isaret,
                            "etiket": etiket, "tur": _tur_etiketi(kayit),
                            "aciklama": _aciklama(kayit), "kimlik": kimlik,
                            "kural": _kural(kayit)})

    # en yakın/geçmiş üste: son güne göre artan (en geçmiş → en ileri)
    gecerli.sort(key=lambda x: (x["gun"], x["aciklama"]))

    sayac = {"GECMIS": 0, "BUGUN": 0, "YAKLASAN": 0, "ILERI": 0}
    for g in gecerli:
        sayac[g["anahtar"]] += 1

    celiskiler = _celiskiler(gecerli)

    # ── kısa özet (oturum açılışı) ─────────────────────────────────────────
    ekler = []
    if bozuk:
        ekler.append("%d bozuk" % len(bozuk))
    if kapali:
        ekler.append("%d iptal/düzeltildi" % len(kapali))
    print("Özet: %d GEÇMİŞ · %d BUGÜN · %d YAKLAŞAN · %d İLERİ  (toplam %d kayıt%s)"
          % (sayac["GECMIS"], sayac["BUGUN"], sayac["YAKLASAN"], sayac["ILERI"],
             len(kayitlar), (", " + ", ".join(ekler)) if ekler else ""))
    print()

    # ── liste ──────────────────────────────────────────────────────────────
    for g in gecerli:
        _yaz_kayit(g["isaret"], g["gun"].isoformat(), g["etiket"], g["tur"],
                   g["aciklama"], g["kimlik"])

    if kapali:
        print()
        print("İPTAL / DÜZELTİLDİ — nöbet dışı, SAYILMAZ (denetim izi olarak durur):")
        for kimlik, ham, tur_tag, aciklama in kapali:
            _yaz_kayit("[×]", (ham or "—"), "İPTAL/DÜZELTİLDİ", tur_tag, aciklama, kimlik)

    if bozuk:
        print()
        print("BOZUK / TARİHSİZ kayıt(lar) — son_gun okunamadı (elle düzelt):")
        for kimlik, ham, tur_tag, aciklama in bozuk:
            _yaz_kayit("[?]", (ham or "—"), "OKUNAMADI", tur_tag, aciklama, kimlik)

    if celiskiler:
        print()
        print("ÇELİŞKİ ADAYI — aynı kural için birden çok AKTİF ve FARKLI son gün:")
        for kural, gunler, kimlikler in celiskiler:
            print("  ! %s → %s  (kayıtlar: %s)"
                  % (kural, " / ".join(gunler), ", ".join("#" + k for k in kimlikler)))
        print("  Biri HAYALET olabilir (ör. yanlış tebliğ tarihi düzeltilmiş ama eski "
              "kayıt defterde kalmış). Dosyada gerçekten iki ayrı işlem varsa "
              "açıklamaları ayrıştırın; değilse hatalı kaydı kapatın — düzeltme "
              "APPEND-ONLY'dir (silme yok):")
        print("  `sure_nobetci.py --kok . --iptal <kimlik> --gerekce \"...\"`")

    # ── sonuç + çıkış kodu ─────────────────────────────────────────────────
    acil = sayac["GECMIS"] + sayac["BUGUN"] + sayac["YAKLASAN"]
    print()
    print(ALT)
    # v0.5.13 — "SÜRE KAÇTI" NİHAİ RAPOR DEĞİLDİR (pratikçi heyeti, tez 2):
    # geçmiş süre görülürse tek satırlık işaretçi basılır. Katalog BURADA
    # DEĞİLDİR (ikiz-liste yasağı): kurtarma kapıları tek kaynakta —
    # `usul_matris.py` üç kanallı kapı araştırması (G3/G5) + oa-usul
    # referansında — yaşar; nöbetçi yalnız oraya işaret eder. `GEÇMİŞ`
    # alt dizesi ve exit-3 sözleşmesi AYNEN korunur.
    if sayac["GECMIS"]:
        print("NOT: geçmiş süre HUKUKEN KESİN DEĞİLDİR — süre hiç işlememiş "
              "olabilir (usulsüz tebliğ; kanun yolu bildiriminin yapılmaması; "
              "vekil varken asile tebliğ). Kurtarma kapıları yargı koluna göre "
              "ayrışır ve İSTİSNAİDİR: `usul_matris.py` kapı araştırmasını "
              "koştur (oa-usul). Araştırma olumsuzsa sonuç kesin dille kapatılır.")
        print()
    if acil or bozuk or celiskiler:
        parcalar = []
        if sayac["GECMIS"]:
            parcalar.append("%d geçmiş" % sayac["GECMIS"])
        if sayac["BUGUN"]:
            parcalar.append("%d bugün" % sayac["BUGUN"])
        if sayac["YAKLASAN"]:
            parcalar.append("%d yaklaşan" % sayac["YAKLASAN"])
        if bozuk:
            parcalar.append("%d bozuk kayıt" % len(bozuk))
        if celiskiler:
            parcalar.append("%d çelişkili kural" % len(celiskiler))
        print("DİKKAT: " + ", ".join(parcalar) + " — derhâl kontrol et; dış takvimle eşgüdümü doğrula.")
        print(CIZGI)
        sys.exit(3)
    print("Acil süre yok — tüm kayıtlar ileri tarihli. (Yine de dış takvimle eşgüdümü koru.)")
    print(CIZGI)
    sys.exit(0)


if __name__ == "__main__":
    main()

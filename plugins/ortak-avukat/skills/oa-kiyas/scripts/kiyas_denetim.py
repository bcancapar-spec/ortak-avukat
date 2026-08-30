#!/usr/bin/env python3
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa-kiyas — kiyas_denetim.py
Hukuki silojizmin (açık kıyas) DETERMİNİSTİK yapı denetimi.

Felsefe: script normun YORUMUNA karar vermez ("unsur oluşmuştur" demez). Yalnızca
yapısal eksikliği yakalar: üç bileşen dolu mu, normun her unsuru bir vakıaya eşlenmiş
mi, küçük önerme delile bağlı mı, büyük önerme içtihatla somutlaştırılmış mı.
Unsurun hukuken gerçekten oluşup oluşmadığı avukatın muhakemesidir.

Girdi:  kiyas.json  (şema references/kiyas-rehberi.md)
Kullanım: python kiyas_denetim.py kiyas.json

ÇIKIŞ KODU KARARI (2026-08-12, Av. Bayram Can Çapar — semantica-uyarlama karar
sorusu #1): kritik boşlukta dahi exit 0 BİLİNÇLİ TASARIMDIR ve öyle kalır.
Gerekçe: kıyas boşluğu bazen stratejik tercihtir (terditli/alternatif savunma
meşru avukat taktiğidir); bu script İÇERİK muhakemesi denetler, kütük disiplini
değil — kapılar yalnız kütük/olgu disiplinini bloklar (yanlış-BLOK yasağı,
v0.5.5 "yanlış katmanı sertleştirdik" dersi). Görünürlük DURUM.md advisory
hattıyla sağlanır; bu kararı değiştirmek yeni bir Can kararı gerektirir.
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json
import sys


# ── v0.5.14 (T7/T8) — İSPAT YÜKÜ KAPALI ENUM'LARI ──────────────────────────
# Boşluk her zaman BİZİM eksiğimiz değildir: ispat yükü, kanunda özel bir
# düzenleme bulunmadıkça, iddia edilen vakıaya bağlanan hukuki sonuçtan kendi
# lehine hak çıkaran tarafa aittir (HMK m.190/1; aynı yönde TMK m.6 —
# Mevzuat MCP'den teyitli, 2026-08-31). Bu yüzden karşılanmamış her unsur
# otomatik olarak bizim subsumtion boşluğumuz sayılamaz. AMA carve-out
# fail-CLOSED'dır: script hukuki NİTELENDİRME yapmaz, yalnız ÜÇ ŞARTIN
# birlikte yazılı olup olmadığına bakar (aşağıda, denetle() 3. bölüm).
YUK_ENUM = {"bizde", "karsi_taraf", "resen", "bilinmiyor"}
DURUM_ENUM = {"karsilanan_delilli", "karsilanan_delilsiz", "karsilanmamis",
              "ispat_yuku_karsida"}


def _unsur_alan(u, ad, varsayilan=None):
    """Unsur kaydından opsiyonel alan okur. Unsur düz string olabilir
    (karakterizasyon: `unsurlar: ["fiil", "zarar"]` desteklenir) — o hâlde
    varsayılan döner. `vars` builtin'i GÖLGELENMEZ."""
    return u.get(ad, varsayilan) if isinstance(u, dict) else varsayilan


def _kimlik(x):
    """Eşleştirmede kullanılacak hashable kimlik. Bozuk girdide (unsur id'si
    sözlük/liste olarak yazılmışsa) `in` operatörü TypeError ile çökerdi."""
    try:
        hash(x)
        return x
    except TypeError:
        return str(x)


def yukle(yol):
    """v0.5.14 (B-23): girdiyi MODEL üretir; okuma/ayrıştırma/kök-tipi
    hatasında ham traceback yerine temiz mesaj + exit 1 (aile standardı —
    traceback 'araç bozuldu' izlenimi verip asıl mesajı kaybediyordu)."""
    try:
        with open(yol, "r", encoding="utf-8") as f:
            veri = json.load(f)
    except FileNotFoundError:
        print(f"❌ JSON okunamadı: dosya yok — {yol}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ JSON okunamadı: {e}")
        sys.exit(1)
    if not isinstance(veri, dict):
        print(f"❌ JSON kökü sözlük değil ({type(veri).__name__}) — kiyas_denetim "
              '{"buyuk_onerme": {...}, "kucuk_onerme": {...}, "sonuc": "..."} '
              "biçiminde bir nesne bekler (şema: references/kiyas-rehberi.md).")
        sys.exit(1)
    return veri


def _sozluk(x):
    return x if isinstance(x, dict) else {}


def _liste(x):
    return x if isinstance(x, list) else []


def denetle(k):
    rapor = []
    eksik_kritik = False

    buyuk = _sozluk(k.get("buyuk_onerme"))
    kucuk = _sozluk(k.get("kucuk_onerme"))
    sonuc = k.get("sonuc")

    veri = {
        "arac": "kiyas_denetim",
        "buyuk_onerme": {
            "norm": buyuk.get("norm"),
            "ictihat": _liste(buyuk.get("ictihat")),
            "unsurlar": _liste(buyuk.get("unsurlar")),
        },
        "kucuk_onerme": {"vakialar": _liste(kucuk.get("vakialar"))},
        "sonuc": sonuc,
        "teyitsiz_ictihat": [],
        "unsur_vakia_eslesme": [],
        "yetim_vakialar": [],
    }

    # 1. Üç bileşen var mı
    rapor.append("### 1. ÜÇLÜ YAPI BÜTÜNLÜĞÜ")
    if not buyuk.get("norm"):
        rapor.append("  ✗ Büyük önerme: norm eksik"); eksik_kritik = True
    else:
        rapor.append(f"  ✓ Norm: {buyuk['norm']}")
    if not kucuk.get("vakialar"):
        rapor.append("  ✗ Küçük önerme: vakıa eksik"); eksik_kritik = True
    else:
        rapor.append(f"  ✓ Küçük önerme: {len(kucuk['vakialar'])} vakıa")
    if not sonuc:
        rapor.append("  ⚠ Sonuç henüz yazılmamış")
    else:
        rapor.append("  ✓ Sonuç var")
    rapor.append("")

    # 2. Büyük önerme içtihatla somutlaştırılmış mı + teyitli mi
    rapor.append("### 2. BÜYÜK ÖNERME — İÇTİHAT VE TEYİT")
    ictihat = _liste(buyuk.get("ictihat"))
    if not ictihat:
        rapor.append("  ⚠ Normu somutlaştıran içtihat yok → oa-ictihat ile emsal ara")
    else:
        for ic in ictihat:
            if not isinstance(ic, dict):
                rapor.append(f"  ⚠ İçtihat kaydı sözlük değil ({type(ic).__name__}) — "
                             "denetime alınamadı; şemaya göre yaz")
                continue
            d = ic.get("dogrulama", "?")
            isaret = "✓" if d == "teyitli" else "⚠"
            rapor.append(f"  {isaret} {ic.get('kunye','(künye yok)')} [{d}]")
            if d != "teyitli":
                rapor.append("     → resmî kaynaktan (Yargı/Mevzuat MCP) teyit et")
                veri["teyitsiz_ictihat"].append(ic.get("kunye", "(künye yok)"))
    rapor.append("")

    # 3. Unsur ↔ vakıa eşleşmesi (kıyasın kalbi)
    rapor.append("### 3. UNSUR ↔ VAKIA EŞLEŞMESİ (subsumtion boşluğu)")
    unsurlar = _liste(buyuk.get("unsurlar"))
    tanimli_unsurlar = set()
    yuk_karsida = []   # rapor §5 için (unsur adı, kaynak, çürütme hazırlığı)
    if not unsurlar:
        # v0.5.14 (B-11): SESSİZ YANLIŞ-YEŞİL KAPATILDI. Norm unsurlara hiç
        # ayrılmamışsa kıyasın kalbi HİÇ atmamıştır; "denetim yapılamadı" ile
        # "denetim geçti" aynı hükmü üretemez. Eskiden yalnız ⚠ basılıyor,
        # ardından "SONUÇ: Yapı bütün." + kritik_bosluk=False geliyordu.
        rapor.append("  ✗ Norm unsurlarına ayrılmamış — subsumtion denetimi YAPILAMADI.")
        rapor.append("     Normu unsurlara böl (örn. fiil/hukuka aykırılık/kusur/zarar/illiyet).")
        rapor.append("     Denetimin YAPILAMAMASI 'yapı bütün' demek DEĞİLDİR.")
        eksik_kritik = True
    else:
        vakialar = _liste(kucuk.get("vakialar"))
        # her unsur en az bir vakıaya 'karsilar' alanıyla bağlanmış olmalı
        karsilanan = {}
        for v in vakialar:
            if not isinstance(v, dict):
                continue
            for u in _liste(v.get("karsilar")):
                karsilanan.setdefault(_kimlik(u), []).append(v)
        for u in unsurlar:
            uid = _unsur_alan(u, "id", u)
            uad = _unsur_alan(u, "ad", uid)
            tanimli_unsurlar.add(_kimlik(uid))
            if _kimlik(uid) in karsilanan:
                deliller = [d for v in karsilanan[_kimlik(uid)]
                            for d in _liste(v.get("dayanak_delil"))]
                if deliller:
                    rapor.append(f"  ✓ [{uad}] ← vakıa var, delil var")
                    durum = "karsilanan_delilli"
                else:
                    rapor.append(f"  ⚠ [{uad}] ← vakıa var ama DELİLSİZ → oa-vakia")
                    durum = "karsilanan_delilsiz"
            else:
                # ── v0.5.14 (T7/T8) İSPAT YÜKÜ CARVE-OUT — TEK dışlama noktası.
                # Fail-CLOSED: carve-out ancak ÜÇ ŞART BİRLİKTE varsa verilir.
                # Aksi hâlde eski yol (KARŞILANMAMIŞ + kritik) aynen işler —
                # model tek token yazarak yeşil satın ALAMAZ.
                ham = _unsur_alan(u, "ispat_yuku", "bilinmiyor")
                yuk = ham if isinstance(ham, str) else (
                    "bilinmiyor" if ham is None else str(ham))
                _kay = _unsur_alan(u, "ispat_yuku_kaynak", "")
                kaynak = _kay.strip() if isinstance(_kay, str) else ""
                hz = _unsur_alan(u, "curutme_hazirligi", None)
                hz_var = isinstance(hz, list) and any(str(x).strip() for x in hz)

                if yuk not in YUK_ENUM:
                    rapor.append(f"  ⚠ [{uad}] ispat_yuku değeri kapalı enum dışında "
                                 f"('{ham}') — script nitelendirme yapmaz, "
                                 "'bilinmiyor' sayıldı")
                    rapor.append(f"  ✗ [{uad}] ← KARŞILANMAMIŞ unsur (boşluk: ispat veya hukuki dayanak)")
                    eksik_kritik = True
                    durum = "karsilanmamis"
                elif yuk == "karsi_taraf" and kaynak and hz_var:
                    rapor.append(f"  ⇄ [{uad}] ← vakıa yok — İSPAT YÜKÜ KARŞI TARAFTA "
                                 f"({kaynak}); kapatma zorunlu değil, ÇÜRÜTME "
                                 "HAZIRLIĞI kayıtlı")
                    durum = "ispat_yuku_karsida"
                    yuk_karsida.append((uad, kaynak,
                                        [str(x).strip() for x in hz if str(x).strip()]))
                elif yuk == "karsi_taraf":
                    rapor.append(f"  ✗ [{uad}] ← KARŞILANMAMIŞ unsur (boşluk: ispat veya hukuki dayanak)")
                    rapor.append("     ⚠ carve-out VERİLMEDİ: kaynak gösterilmemiş / "
                                 "çürütme hazırlığı boş (üç şart birlikte aranır)")
                    eksik_kritik = True
                    durum = "karsilanmamis"
                else:
                    rapor.append(f"  ✗ [{uad}] ← KARŞILANMAMIŞ unsur (boşluk: ispat veya hukuki dayanak)")
                    eksik_kritik = True
                    durum = "karsilanmamis"
            veri["unsur_vakia_eslesme"].append(
                {"unsur_id": uid, "unsur_ad": uad, "durum": durum})
    rapor.append("")

    # 4. Yetim vakıa (hiçbir unsuru karşılamayan)
    rapor.append("### 4. YETİM VAKIA (hiçbir norm unsurunu karşılamıyor)")
    bulundu_yetim = False
    for v in _liste(kucuk.get("vakialar")):
        if not isinstance(v, dict):
            rapor.append(f"  ⚠ Vakıa kaydı sözlük değil ({type(v).__name__}) — "
                         "denetime alınamadı; şemaya göre yaz")
            bulundu_yetim = True
            continue
        metin = v.get("metin", "(metin yok)")
        ks = _liste(v.get("karsilar"))
        if not ks:
            rapor.append(f"  ⚠ '{metin}' — hangi unsuru karşılıyor? bağla veya çıkar")
            veri["yetim_vakialar"].append(metin)
            bulundu_yetim = True
        elif tanimli_unsurlar and not any(_kimlik(x) in tanimli_unsurlar for x in ks):
            # v0.5.14 (B-11 ikinci ayak): `karsilar` TANIMSIZ bir unsura işaret
            # ediyorsa vakıa ne eşleşiyor ne yetim sayılıyordu — tamamen
            # görünmezdi. Tanımlı hiçbir unsuru karşılamayan vakıa yetimdir.
            rapor.append(f"  ⚠ '{metin}' — 'karsilar' TANIMSIZ unsur(lar)a işaret "
                         f"ediyor ({', '.join(str(x) for x in ks)}); tanımlı hiçbir "
                         "norm unsurunu karşılamıyor")
            veri["yetim_vakialar"].append(metin)
            bulundu_yetim = True
    if not bulundu_yetim:
        rapor.append("  ✓ Her vakıa bir unsura bağlı.")
    rapor.append("")

    # 5. İspat yükü (yalnız carve-out verilen unsur varsa basılır)
    if yuk_karsida:
        rapor.append("### 5. İSPAT YÜKÜ — carve-out verilen unsurlar")
        rapor.append("  ⚠ DAHİLİ — DOSYAYA EKLENMEZ / UYAP'A YÜKLENMEZ")
        for uad, kaynak, hazirlik in yuk_karsida:
            rapor.append(f"  ⇄ [{uad}] yük karşı tarafta — dayanak: {kaynak}")
            for h in hazirlik:
                rapor.append(f"      · çürütme hazırlığı: {h}")
        rapor.append("")

    veri["kritik_bosluk"] = eksik_kritik
    return rapor, eksik_kritik, veri


def main(yol, json_yol=None):
    k = yukle(yol)
    cizgi = "=" * 60
    print(cizgi)
    print("OA-KIYAS — DETERMİNİSTİK SİLOJİZM DENETİM RAPORU")
    print(cizgi)
    rapor, kritik, veri = denetle(k)
    print("\n".join(rapor))
    print(cizgi)
    if kritik:
        print("SONUÇ: Kıyasta KRİTİK BOŞLUK var (karşılanmamış unsur / eksik bileşen).")
        print("Bu boşluk kapanmadan sonuç güvenilir değildir.")
    else:
        print("SONUÇ: Yapı bütün. Unsurların hukuken oluşup oluşmadığı AVUKAT muhakemesidir.")
    # v0.5.14 (T7/T8): carve-out uygulanmışsa görünür tek satır. "KRİTİK
    # BOŞLUK" literali BİLİNÇLİ olarak geçmez (mevcut metin kilitleri).
    n_yuk = sum(1 for u in veri["unsur_vakia_eslesme"]
                if u.get("durum") == "ispat_yuku_karsida")
    if n_yuk:
        print(f"NOT: {n_yuk} unsur 'ispat yükü KARŞI TARAFTA' gerekçesiyle boşluk "
              "sayılmadı (kaynak + çürütme hazırlığı şartlı). Yükün gerçekten "
              "karşıda olup olmadığı AVUKAT muhakemesidir.")
    print(cizgi)

    if json_yol:
        veri["girdi"] = yol
        with open(json_yol, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"[JSON] Makine-okur sonuc yazildi: {json_yol}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="OA-kiyas deterministik silojizm denetimi")
    p.add_argument("kiyas", nargs="?", help="kiyas.json yolu")
    p.add_argument("--json", dest="json_yol", metavar="YOL",
                   help="denetim sonucunu makine-okur JSON olarak bu yola yaz (opsiyonel)")
    a = p.parse_args()
    if not a.kiyas:
        print("Kullanım: python kiyas_denetim.py kiyas.json [--json out.json]")
        sys.exit(1)
    main(a.kiyas, json_yol=a.json_yol)

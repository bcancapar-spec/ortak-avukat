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

Kullanım:
  python okuma_kapisi.py [--kok KLASÖR] [--esik N]
  python okuma_kapisi.py [--kok KLASÖR] --json CIKTI.json
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

import argparse, datetime, json, os, sys

BUYUK_ESIK_VARSAYILAN = 40000  # oa_ingest.py BUYUK_ESIK_KARAKTER ile aynı varsayılan

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
        liste.append({
            "no": k.get("no"), "ad": k.get("ad"), "kaynak": k.get("kaynak"),
            "tur_tahmini": k.get("tur_tahmini"), "karakter": k.get("karakter") or 0,
            "teyit_gerek": bool(k.get("teyit_gerek")), "buyuk": buyuk,
            "harita": k.get("harita") or "", "md": k.get("md") or "",
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
    args = ap.parse_args()

    if not os.path.isdir(args.kok):
        sys.exit(f"HATA: klasör yok: {args.kok}")

    if args.tam_yukle_kaydet:
        sys.exit(cmd_tam_yukle_kaydet(args))
    if args.tam_yukle_defter:
        sys.exit(cmd_tam_yukle_defter(args))
    sys.exit(cmd_liste(args))


if __name__ == "__main__":
    main()

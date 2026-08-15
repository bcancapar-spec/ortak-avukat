#!/usr/bin/env python3
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
oa-kontrol — muhur_yaz.py  (v0.5.8, P1 — semantica PROV-O deseninin devşirmesi;
bkz. anayasa m.0 dış desen devşirme protokolü, Can kararı 2026-08-12)

PROVENANCE MÜHRÜ: her teslim ürününe PROV-O adlarıyla hizalı doğum belgesi.
Ürünün yanına `<urun>.prov.json` yazar + dava kökünde append-only
`_oa/provenance.jsonl` defterine bir satır ekler.

Şema `oa-muhur/1.0` (~11 alan):
  prov_schema        : "oa-muhur/1.0"
  entity_id          : mantıksal kimlik (ör. "dilekce:cbs-2023-1079:v2")
  entity_type        : dilekce_udf | dilekce_pdf | graf_json | analiz_md | diger
  artifact_file      : ürünün DAVA KÖKÜNE GÖRELİ yolu (sabit-yol sızıntı dersi)
  artifact_sha256    : ürünün HAM BAYTLARININ tam SHA-256'ı — semantica'nın
                       compute_checksum'unda OLMAYAN, bizde ŞART olan alan
                       ("üretildi ≠ geçerli" dersi: mühür DOSYAYA bağlanır)
  generated_at_time  : UTC ISO-8601 (prov:generatedAtTime)
  was_generated_by   : üreten araç + sürüm (prov:wasGeneratedBy)
  used               : girdi listesi [{file, sha256}] (prov:used)
  was_derived_from   : önceki sürümün artifact_sha256'ı | null (prov:wasDerivedFrom)
  llm_kullanimi      : serbest tanıklık metni (Layer 0 beyanı). v0.5.8.4: çağrıda
                       verilmezse 'beyan edilmedi' DEĞİL, otomatik olarak
                       'mekanik üretim; içerik oturum LLM koşusundan' yazılır
                       (mühür hep script'ten üretilir; içerik oturumdan gelir —
                       dürüst varsayılan budur, boş beyan değil).

--tasi ESKI YENI (v0.5.8.4): ürün dosyası arşive taşınınca mührü de taşır —
dosya YENI konumda değilse önce dosyayı taşır, `artifact_file` yolunu günceller,
sha'nın AYNI kaldığını ŞART koşar (değiştiyse exit 1 — taşıma içerik değiştirmez),
defter satırı düşer ve eski `.prov.json`u kaldırır.

FELSEFE (amaç çizgisi + semantica'nın zarif-bozulma deseni): mühür yazımı
teslim akışını ASLA kırmaz — hata görünür uyarıyla raporlanır, üretim sürer.
Doğrulama tarafı ise serttir: `--dogrula` mevcut mühürle dosyayı karşılaştırır,
uyuşmazlıkta exit 1 (UYAP-öncesi kontrol için).

teslim_paketi.py entegrasyonu (otomatik çağrı) BİLİNÇLİ olarak saha provası
sonrasına bırakıldı (kaş-göz ilkesi: tek-ölçüt kapıya bu turda cerrahi yok);
kapanış adımında SKILL talimatıyla ürün başına koşturulur.

Kullanım:
  python muhur_yaz.py --kok <kok> --urun _oa/teslim/x.udf --tip dilekce_udf \
      --kimlik "dilekce:cbs:v2" --girdi _oa/cikti/08.md [--onceki <sha256>] \
      [--arac "udf_yaz v0.5.8"] [--llm "YOK — mekanik üretim"]
  python muhur_yaz.py --kok <kok> --dogrula _oa/teslim/x.udf
"""
# __OA_UTF8_GUARD__
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys

# v0.5.8.4 — llm_kullanimi verilmediğinde 'beyan edilmedi' yerine dürüst
# otomatik beyan (üretim mekaniği script, içerik oturumun LLM koşusudur).
LLM_VARSAYILAN = "mekanik üretim; içerik oturum LLM koşusundan"


def sha256_dosya(yol):
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 16), b""):
            h.update(parca)
    return h.hexdigest()


def _goreli(kok, yol):
    try:
        return os.path.relpath(os.path.realpath(yol),
                               os.path.realpath(kok)).replace("\\", "/")
    except ValueError:  # farklı sürücü — göreli yazılamaz, ad yazılır
        return os.path.basename(yol)


def muhur_uret(kok, urun, tip, kimlik, girdiler, onceki=None,
               arac=None, llm=None):
    kayit = {
        "prov_schema": "oa-muhur/1.0",
        "entity_id": kimlik,
        "entity_type": tip,
        "artifact_file": _goreli(kok, urun),
        "artifact_sha256": sha256_dosya(urun),
        "generated_at_time": datetime.datetime.now(
            datetime.timezone.utc).isoformat(timespec="seconds"),
        "was_generated_by": arac or "ortak-avukat v0.5.8 (fork-prova)",
        "used": [{"file": _goreli(kok, g), "sha256": sha256_dosya(g)}
                 for g in girdiler if os.path.isfile(g)],
        "was_derived_from": onceki,
        "llm_kullanimi": llm or LLM_VARSAYILAN,
    }
    return kayit


def muhur_yaz(kok, urun, kayit):
    """Ürün yanına .prov.json + köke append-only jsonl. Hata FIRLATMAZ —
    (yol|None, hata|None) döndürür (zarif bozulma)."""
    try:
        prov_yolu = urun + ".prov.json"
        with open(prov_yolu, "w", encoding="utf-8") as f:
            json.dump(kayit, f, ensure_ascii=False, indent=1, sort_keys=True)
        defter = os.path.join(kok, "_oa", "provenance.jsonl")
        os.makedirs(os.path.dirname(defter), exist_ok=True)
        with open(defter, "a", encoding="utf-8") as f:
            f.write(json.dumps(kayit, ensure_ascii=False, sort_keys=True) + "\n")
        return prov_yolu, None
    except OSError as e:
        return None, str(e)


def tasi(kok, eski, yeni):
    """v0.5.8.4 — `--tasi ESKI YENI`: ürün arşive taşınınca mührü taşır.
    Kurallar: (1) ESKI yanında mühür ŞART; (2) YENI konumda dosya yoksa ve
    ESKI duruyorsa dosyayı da taşır (mühür-dosya çifti ayrılmaz); (3) sha
    AYNI kalmalı — YENI dosyanın sha'sı mühürdekiyle uyuşmazsa exit 1
    (taşıma içerik değiştirmez; değiştiyse bu taşıma değil tahriftir);
    (4) `artifact_file` yeni göreli yola güncellenir, eski `.prov.json`
    kaldırılır, defterde iz satırı düşer. exit-kodu döndürür."""
    eski_prov = eski + ".prov.json"
    if not os.path.isfile(eski_prov):
        print(f"✗ taşınacak mühür yok: {eski_prov}")
        return 1
    with open(eski_prov, encoding="utf-8") as f:
        kayit = json.load(f)
    if not os.path.isfile(yeni):
        if not os.path.isfile(eski):
            print(f"✗ ürün ne eski ({eski}) ne yeni ({yeni}) konumda mevcut — "
                  "taşınacak dosya yok.")
            return 1
        hedef_dizin = os.path.dirname(os.path.abspath(yeni))
        if hedef_dizin:
            os.makedirs(hedef_dizin, exist_ok=True)
        shutil.move(eski, yeni)
    simdiki = sha256_dosya(yeni)
    if simdiki != kayit.get("artifact_sha256"):
        print(f"✗ TAŞIMA REDDEDİLDİ: sha AYNI kalmalı — mühür "
              f"{str(kayit.get('artifact_sha256', '?'))[:12]}… ≠ şimdiki "
              f"{simdiki[:12]}… (taşıma içerik değiştirmez).")
        return 1
    kayit["artifact_file"] = _goreli(kok, yeni)
    yeni_prov = yeni + ".prov.json"
    with open(yeni_prov, "w", encoding="utf-8") as f:
        json.dump(kayit, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.remove(eski_prov)
    defter = os.path.join(kok, "_oa", "provenance.jsonl")
    os.makedirs(os.path.dirname(defter), exist_ok=True)
    with open(defter, "a", encoding="utf-8") as f:
        f.write(json.dumps(kayit, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"✓ mühür taşındı: {os.path.basename(eski)} → {kayit['artifact_file']} "
          f"(sha aynı: {simdiki[:12]}…)")
    return 0


def dogrula(urun):
    """Mühür ↔ dosya karşılaştırması. exit-kodu döndürür (0 uyumlu / 1 değil)."""
    prov_yolu = urun + ".prov.json"
    if not os.path.isfile(prov_yolu):
        print(f"✗ mühür yok: {prov_yolu}")
        return 1
    with open(prov_yolu, encoding="utf-8") as f:
        kayit = json.load(f)
    simdiki = sha256_dosya(urun)
    if simdiki != kayit.get("artifact_sha256"):
        print(f"✗ MÜHÜR UYUŞMAZLIĞI: {os.path.basename(urun)} — dosya mühürden "
              f"SONRA değişmiş (beyan {kayit.get('artifact_sha256','?')[:12]}… "
              f"≠ şimdiki {simdiki[:12]}…). UYAP'a YÜKLEME.")
        return 1
    print(f"✓ mühür uyumlu: {os.path.basename(urun)} "
          f"({simdiki[:12]}…, {kayit.get('generated_at_time')})")
    return 0


def main():
    ap = argparse.ArgumentParser(description="oa-mühür (v0.5.8 P1, PROV-O hizalı)")
    ap.add_argument("--kok", default=".")
    ap.add_argument("--urun", help="mühürlenecek ürün yolu")
    ap.add_argument("--tip", default="diger")
    ap.add_argument("--kimlik", default=None)
    ap.add_argument("--girdi", action="append", default=[],
                    help="üretimde kullanılan girdi (tekrarlanabilir)")
    ap.add_argument("--onceki", default=None,
                    help="önceki sürümün artifact_sha256'ı")
    ap.add_argument("--arac", default=None)
    ap.add_argument("--llm", default=None)
    ap.add_argument("--dogrula", default=None,
                    help="mevcut mührü doğrula (sert: uyuşmazlık=exit 1)")
    ap.add_argument("--tasi", nargs=2, metavar=("ESKI", "YENI"), default=None,
                    help="v0.5.8.4: ürün arşive taşınınca mührü taşı — "
                         "artifact_file güncellenir, sha AYNI kalmalı (sert)")
    args = ap.parse_args()

    if args.tasi:
        sys.exit(tasi(args.kok, args.tasi[0], args.tasi[1]))

    if args.dogrula:
        sys.exit(dogrula(args.dogrula))

    if not args.urun or not os.path.isfile(args.urun):
        sys.exit(f"HATA: ürün bulunamadı: {args.urun}")

    kimlik = args.kimlik or f"urun:{os.path.basename(args.urun)}"
    kayit = muhur_uret(args.kok, args.urun, args.tip, kimlik,
                       args.girdi, args.onceki, args.arac, args.llm)
    yol, hata = muhur_yaz(args.kok, args.urun, kayit)
    if hata:
        # zarif bozulma: üretimi KIRMAZ — görünür uyarı basar, exit 0
        print(f"⚠ MÜHÜR YAZILAMADI ({hata}) — teslim akışı sürdü; mühürsüz "
              f"ürün UYAP öncesi elle doğrulanmalı.")
        sys.exit(0)
    print(f"✓ mühür: {os.path.basename(yol)} "
          f"(sha {kayit['artifact_sha256'][:12]}…, girdi: {len(kayit['used'])})")
    sys.exit(0)


if __name__ == "__main__":
    main()

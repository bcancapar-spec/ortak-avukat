#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).
# 'Ortak Avukat' metodoloji sistemi. İzinsiz çoğaltma/dağıtma/türev yasaktır.
"""
tam_tur.py — TAM TUR yaşam döngüsü motoru (bir kez tam analiz, sonra DELTA).

KONSEPT (kurucu talep): Tam tur bir davanın YAPISINI çıkarır; model tümünü inceler,
muhakemeyi doğru kurar. Bu PAHALI analiz dosya başına BİR KEZ yapılır ve modelin
okuyabileceği yapılandırılmış bir KAYIT BELGESİ olarak diske yazılır
(_oa/analiz/dosya-analiz.md + .json + evrak anlık görüntüsü). Dosyaya sonradan yeni
evrak/gelişme/delil eklenince tam tur TEKRAR TÜKETİLMEZ: yalnız yeni gelişmeyi kapsayan
ARTIMLI (delta) kayıt eklenir. Böylece her promptta tüm aile baştan koşmaz.

Bu script HUKUKİ değerlendirme yapmaz; yalnız (a) evrak anlık görüntüsünü tutar,
(b) yeni evrakı (delta) deterministik saptar, (c) parça çıktılarını (_oa/cikti/*) tek
belgede toplar, (d) artımlı gelişme günlüğünü yönetir. Analizin İÇERİĞİ modele + aile
parçalarına aittir; bu motor onun ÇERÇEVESİNİ ve TAZELİĞİNİ garanti eder.

DELTA MOTORU (körlük kapama): Delta yalnız "son ingest künyesi"ni değil, ÖNCE diski
tarar: çalışma kökünde künyede olmayan (ya da künyede olup diskte kalmayan) ham evrak
varsa "KÜNYE BAYAT — önce oa_ingest koş" der (avukat 3 PDF atıp ingest'i koşmazsa artık
"DELTA YOK" diyerek kör kalmaz). İmza karakter+yöntem değil künyedeki `sha` (gerçek içerik
hash'i) üzerinden kurulur (aynı karakter sayılı içerik değişikliği yakalanır; aynı sha
farklı ad = yeniden adlandırma ipucu). Silinen/kaldırılan evrak da raporlanır.

BAYAT-KÜNYE KAPISI (`--kaydet` başında, körlük kapama): `--durum`/`--delta` yalnız
KÜNYE-bilinen deltayı görür — künyede HİÇ anılmayan (diske atılmış ama ingest edilmemiş)
ham evrak onlara görünmez. Bu yüzden `--kaydet`, künye okunur okunmaz `_bayat_kunye` ile
diski künyeyle karşılaştırır: eklenen/kaldırılan varsa TAMAM damgalanamaz ve snapshot
alınmaz ("boşluklu tur teslim edilemez" doktrini tam damgalama anında delinmesin diye) —
--zorla ile geçilirse dosya-analiz.md ŞERH bloğuna işlenir (sessiz geçiş yok).

DEFTER KAPISI (§6-B(iv), boşluklu tur teslim edilemez): `--kaydet`, bayat-künye kapısı,
_oa/cikti boşluğu ve işlenmemiş-delta yutmasının yanına DÖRDÜNCÜ bir denetim ekler — bu
kökte oa-pipeline'ın pipeline_kayit.py --baslat ile açtığı bir olay defteri
(_oa/defter/pipeline-olaylar.jsonl) varsa, aynı dizindeki pipeline_kayit.py --denetle
mantığı alt süreçte koşturulur; BEKLIYOR veya kanıtsız adım varsa TAMAM damgalanamaz
(--zorla ile ŞERH düşülerek geçilebilir). Defter hiç açılmamışsa (defter kullanmayan akış)
bu kapı sessizce atlanır — mevcut davranış korunur.

Kullanım:
  python tam_tur.py --durum                         # tam tur var mı, delta var mı, künye bayat mı
  python tam_tur.py --baslat --dosya "<ad>"         # tam tur başlat (snapshot planla)
  python tam_tur.py --kaydet                         # _oa/cikti/* → dosya-analiz + snapshot al (tam tur BİTTİ)
  python tam_tur.py --kaydet --zorla                 # boş-çıktı / bayat-künye / işlenmemiş-delta / defter-engeli ŞERH düşerek geç
  python tam_tur.py --delta                          # snapshot'tan bu yana YENİ/DEĞİŞEN/SİLİNEN evrak
  python tam_tur.py --ekle "<gelişme özeti>"         # artımlı gelişme kaydı (tam tur tekrar YOK)
  python tam_tur.py --kok "<klasör>"                 # çalışma kökü (varsayılan: bulunulan klasör)

Çıkış kodu: 0 = tam tur güncel / iş tamam; 3 = tam tur yok VEYA bekleyen delta var VEYA
künye bayat (`--durum`/`--delta`de; pipeline bunu okuyup "artımlı mod"a / "önce ingest"e geçer);
1 = kullanım/erişim hatası VEYA `--kaydet` başında künye bayat (--zorla yoksa) VEYA
_oa/cikti boş (--zorla yoksa) VEYA işlenmemiş evrak snapshot'a yutulacak (--zorla yoksa)
VEYA pipeline defteri TESLİM ENGELİ bildiriyor (--zorla yoksa; defter hiç açılmamışsa bu
koşul devre dışıdır).
"""
# __OA_UTF8_GUARD__ — Windows/PowerShell cp1254 konsolunda çökmeyi önler
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
import subprocess
import sys

# Diskte "ham evrak" sayılan uzantılar (oa_ingest'in işlediği tipler). `_oa` taranmaz.
HAM_UZANTILAR = {".pdf", ".udf", ".docx", ".eyp", ".zip",
                 ".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp", ".gif",
                 ".txt", ".md", ".rtf", ".html", ".htm", ".csv", ".xml"}
ATLA_DIZIN = {"_oa", ".claude", "__pycache__", ".git"}
BOS_SHA = hashlib.sha256(b"").hexdigest()[:16]   # metinsiz kayıtların sabit imzası


def _oa_kok(kok):
    return os.path.join(kok, "_oa")


def _analiz_dizin(kok):
    return os.path.join(_oa_kok(kok), "analiz")


def _analiz_json(kok):
    return os.path.join(_analiz_dizin(kok), "dosya-analiz.json")


def _analiz_md(kok):
    return os.path.join(_analiz_dizin(kok), "dosya-analiz.md")


def _kunye_yolu(kok):
    return os.path.join(_oa_kok(kok), "metin", "00-kunye.json")


def _defter_dizin(kok):
    return os.path.join(_oa_kok(kok), "defter")


def _defter_olaylar_yolu(kok):
    return os.path.join(_defter_dizin(kok), "pipeline-olaylar.jsonl")


def _defter_durum_yolu(kok):
    return os.path.join(_defter_dizin(kok), "pipeline-durum.json")


def _defter_var_mi(kok):
    """oa-pipeline'ın pipeline_kayit.py --baslat ile açtığı olay defteri bu kökte
    var mı? Yoksa defter kapısı devre dışı kalır — defter KULLANMAYAN akış (yalnız
    oa-ingest + tam_tur ile çalışan dosyalar) bloklanmaz."""
    olaylar = _defter_olaylar_yolu(kok)
    if os.path.exists(olaylar) and os.path.getsize(olaylar) > 0:
        return True
    return os.path.exists(_defter_durum_yolu(kok))  # jsonl'den önceki eski görünüm


def _defter_denetle(kok):
    """Pipeline defteri (§6-B(iv) kapısı): varsa aynı dizindeki pipeline_kayit.py'yi
    `--denetle --kok <kok>` ile alt süreçte koştur — BEKLIYOR/kanıtsız adım varsa
    boşluklu tur teslim edilemez. Döner: (temiz, çıktı).
      - Defter yoksa: (True, "") — kapı atlanır, mevcut davranış korunur.
      - Betik bulunamaz/çalıştırılamazsa: (True, uyarı) — defter kapısındaki bir
        arıza defterden ÖNCEKİ davranışı kilitli bir çıkmaza sokmasın; yine de
        uyarı metni çağırana döner (sessiz geçilmez)."""
    if not _defter_var_mi(kok):
        return True, ""
    betik = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline_kayit.py")
    if not os.path.isfile(betik):
        return True, "UYARI: pipeline_kayit.py bulunamadı — defter kapısı atlandı."
    try:
        r = subprocess.run([sys.executable, betik, "--denetle", "--kok", kok],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
    except Exception as e:
        return True, f"UYARI: defter denetimi çalıştırılamadı ({e}) — kapı atlandı."
    cikti = ((r.stdout or "") + (r.stderr or "")).strip()
    return (r.returncode == 0), cikti


def _simdi():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def _kunye_oku(kok):
    y = _kunye_yolu(kok)
    if not os.path.exists(y):
        return None
    try:
        return json.load(open(y, encoding="utf-8"))
    except Exception:
        return None


def _evrak_imzalari(kunye):
    """kaynak → içerik imzası. Künyede `sha` varsa ondan kur (gerçek içerik hash'i,
    aynı karakter sayılı değişikliği yakalar); yoksa eski karakter+yöntem (geri uyum)."""
    d = {}
    for k in kunye.get("kayitlar", []):
        kaynak = k.get("kaynak") or k.get("ad") or ""
        if k.get("sha"):
            d[kaynak] = "sha:" + k["sha"]
        else:
            d[kaynak] = f"{k.get('karakter', 0)}-{k.get('yontem', '')}"
    return d


def _sha_of(imza):
    """imza 'sha:<hex>' ise <hex> döner; boş-içerik sha'sı yanıltmasın diye elenir."""
    if isinstance(imza, str) and imza.startswith("sha:"):
        h = imza[4:]
        if h and h != BOS_SHA:
            return h
    return None


def _yeniden_adlandirma(guncel_imza, snap_imza, yeni, silinen):
    """Aynı sha + farklı ad → yeniden adlandırma çiftleri (eski_ad, yeni_ad)."""
    silinen_sha = {}
    for k in silinen:
        h = _sha_of(snap_imza.get(k))
        if h:
            silinen_sha.setdefault(h, []).append(k)
    ciftler = []
    for k in yeni:
        h = _sha_of(guncel_imza.get(k))
        if h and h in silinen_sha:
            for eski in silinen_sha[h]:
                ciftler.append((eski, k))
    return sorted(ciftler)


def _disk_ham_evraklar(kok):
    """Çalışma kökündeki ham evrakları (HAM_UZANTILAR, `_oa` hariç) göreli yolla tara."""
    bulunan = set()
    for dk, dizinler, adlar in os.walk(kok):
        dizinler[:] = [d for d in dizinler if d.lower() not in ATLA_DIZIN]
        for ad in adlar:
            if os.path.splitext(ad)[1].lower() in HAM_UZANTILAR:
                rel = os.path.relpath(os.path.join(dk, ad), kok).replace("\\", "/")
                bulunan.add(rel)
    return bulunan


def _kunye_kaynaklar(kunye):
    """Künye kayıtlarının diskteki taban dosyası (arşiv içi 'x.eyp::ic' → 'x.eyp')."""
    s = set()
    for k in kunye.get("kayitlar", []):
        kaynak = k.get("kaynak") or ""
        taban = kaynak.split("::", 1)[0].replace("\\", "/")
        if taban:
            s.add(taban)
    return s


def _bayat_kunye(kok):
    """Künye diskle örtüşüyor mu? (eklenen: diskte var künyede yok;
    kaldirilan: künyede var diskte yok). Künye yoksa None."""
    kunye = _kunye_oku(kok)
    if kunye is None:
        return None
    disk = _disk_ham_evraklar(kok)
    kaynaklar = _kunye_kaynaklar(kunye)
    eklenen = sorted(d for d in disk if d not in kaynaklar)
    kaldirilan = sorted(
        b for b in kaynaklar
        if not os.path.exists(os.path.join(kok, b.replace("/", os.sep)))
    )
    return eklenen, kaldirilan


def _bayat_kontrol_yaz(kok):
    """Bayat künye varsa uyarı basıp exit 3 döndürür; yoksa 0."""
    sonuc = _bayat_kunye(kok)
    if sonuc is None:
        return 0
    eklenen, kaldirilan = sonuc
    if not eklenen and not kaldirilan:
        return 0
    print("KUNYE BAYAT — once oa_ingest kos (kunye diskle ortusmuyor; delta korlesir).",
          file=sys.stderr)
    if eklenen:
        print(f"  Kunyede OLMAYAN {len(eklenen)} dosya (ingest edilmemis):", file=sys.stderr)
        for e in eklenen[:20]:
            print(f"   + {e}", file=sys.stderr)
        if len(eklenen) > 20:
            print(f"   ... (+{len(eklenen) - 20} daha)", file=sys.stderr)
    if kaldirilan:
        print(f"  Kunyede olup diskte OLMAYAN {len(kaldirilan)} dosya (silinmis/tasinmis):",
              file=sys.stderr)
        for e in kaldirilan[:20]:
            print(f"   - {e}", file=sys.stderr)
        if len(kaldirilan) > 20:
            print(f"   ... (+{len(kaldirilan) - 20} daha)", file=sys.stderr)
    return 3


def _durum_oku(kok):
    y = _analiz_json(kok)
    if not os.path.exists(y):
        return None
    try:
        return json.load(open(y, encoding="utf-8"))
    except Exception:
        return None


def _durum_yaz(kok, durum):
    os.makedirs(_analiz_dizin(kok), exist_ok=True)
    with open(_analiz_json(kok), "w", encoding="utf-8") as f:
        json.dump(durum, f, ensure_ascii=False, indent=2)


def _delta_hesapla(kok, durum):
    """(yeni, degisen, silinen) — snapshot'a göre eklenen, içeriği değişen ve
    snapshot'ta olup güncelde bulunmayan evrak. Künye okunamazsa (None, None, None)."""
    kunye = _kunye_oku(kok)
    if kunye is None:
        return None, None, None
    guncel = _evrak_imzalari(kunye)
    snap = durum.get("kunye_snapshot", {}).get("imzalar", {}) if durum else {}

    def _sema(v):  # 'sha' (yeni) mi 'karakter' (eski) mi
        return "sha" if isinstance(v, str) and v.startswith("sha:") else "kar"

    yeni = [k for k in guncel if k not in snap]
    # DEĞİŞEN yalnız AYNI şema içinde ölçülür: eski (karakter) snapshot'tan yeni (sha)
    # künyeye geçiş, her evrakı yanlışça "değişmiş" göstermesin (geri uyum).
    degisen = [k for k in guncel if k in snap and guncel[k] != snap[k]
               and _sema(guncel[k]) == _sema(snap[k])]
    silinen = [k for k in snap if k not in guncel]
    return sorted(yeni), sorted(degisen), sorted(silinen)


def _anilan_evraklar(durum, since_index=0):
    """GELİŞMELER günlüğünde anılan evrak kaynaklarının kümesi (yutma denetimi için).
    `since_index` verilirse yalnız o INDEX'ten İTİBAREN eklenmiş gelişmeler sayılır
    (varsayılan 0 = tüm geçmiş, geri uyum). Bu, tam turun ÖNCEKİ snapshot döngüsünde
    anılmış bir evrakın, snapshot tazelendikten SONRA aynı evrak tekrar değişip hiç
    işlenmeden geçmiş (bayat) bir anmayla sahte-doğrulanmasını engeller. Gelişmeler
    listesi yalnız `--ekle` ile sona eklendiği ve `--kaydet` onu değiştirmediği için
    liste KONUMU, dakika çözünürlüklü tarih damgasından farklı olarak, aynı dakika
    içindeki ardışık ekle+kaydet çağrılarında bile KESİN bir sınır verir."""
    s = set()
    for g in durum.get("gelismeler", [])[since_index:]:
        for k in (g.get("yeni_evrak") or []):
            s.add(k)
        for k in (g.get("degisen_evrak") or []):
            s.add(k)
    return s


def cmd_baslat(kok, dosya):
    durum = _durum_oku(kok) or {}
    durum.setdefault("dosya", dosya or durum.get("dosya") or os.path.basename(os.path.abspath(kok)))
    durum["tam_tur_durumu"] = "DEVAM"
    durum.setdefault("gelismeler", [])
    durum["baslatildi"] = _simdi()
    _durum_yaz(kok, durum)
    print(f"TAM TUR başlatıldı: {durum['dosya']} ({durum['baslatildi']})")
    print("Aile tüm parçaları işletsin; her adım _oa/cikti/ altına çalışma evrakı bıraksın.")
    print("Tur bitince: python tam_tur.py --kaydet")
    return 0


def _cikti_topla(kok):
    """_oa/cikti/ altındaki adım çıktılarını (NN-parca-*.md/.json) toplar."""
    cdiz = os.path.join(_oa_kok(kok), "cikti")
    kalemler = []
    if os.path.isdir(cdiz):
        for ad in sorted(os.listdir(cdiz)):
            yol = os.path.join(cdiz, ad)
            if not os.path.isfile(yol):
                continue
            try:
                boyut = os.path.getsize(yol)
            except OSError:
                boyut = 0
            kalemler.append({"dosya": ad, "boyut": boyut,
                             "yol": os.path.relpath(yol, kok)})
    return kalemler


def cmd_kaydet(kok, zorla=False):
    durum = _durum_oku(kok) or {"gelismeler": []}
    kunye = _kunye_oku(kok)
    if kunye is None:
        print("HATA: _oa/metin/00-kunye.json yok — önce oa-ingest koşmalı (0. adım).",
              file=sys.stderr)
        return 1

    # (iv-0) Bayat-künye kapısı: diske atılmış ama HİÇ ingest edilmemiş (ya da
    # künyede olup diskten silinmiş) ham evrak varken TAMAM damgalanamaz — yutma
    # denetimi (iv-b) yalnız KÜNYE-bilinen deltayı görür; künyede hiç olmayan
    # disk dosyası ona ve snapshot'a görünmez kalırdı. --zorla ile geçilirse
    # dosya-analiz.md ŞERH bloğuna işlenir (sessiz geçiş yok).
    serh_bayat = []
    bayat = _bayat_kunye(kok)
    if bayat is not None:
        eklenen_b, kaldirilan_b = bayat
        if eklenen_b or kaldirilan_b:
            if not zorla:
                print("HATA: KUNYE BAYAT — once oa_ingest kos; islenmemis disk evraki "
                      "TAMAM damgasina yutulamaz.", file=sys.stderr)
                if eklenen_b:
                    print(f"  Kunyede OLMAYAN {len(eklenen_b)} dosya (ingest edilmemis):",
                          file=sys.stderr)
                    for e in eklenen_b[:20]:
                        print(f"   + {e}", file=sys.stderr)
                    if len(eklenen_b) > 20:
                        print(f"   ... (+{len(eklenen_b) - 20} daha)", file=sys.stderr)
                if kaldirilan_b:
                    print(f"  Kunyede olup diskte OLMAYAN {len(kaldirilan_b)} dosya "
                          "(silinmis/tasinmis):", file=sys.stderr)
                    for e in kaldirilan_b[:20]:
                        print(f"   - {e}", file=sys.stderr)
                    if len(kaldirilan_b) > 20:
                        print(f"   ... (+{len(kaldirilan_b) - 20} daha)", file=sys.stderr)
                print("Cozum: once oa_ingest kos (kunye diski yakalasin), sonra --kaydet. "
                      "(Bilerek gecmek icin: --zorla)", file=sys.stderr)
                return 1
            serh_bayat = sorted(list(eklenen_b) + list(kaldirilan_b))

    kalemler = _cikti_topla(kok)
    # (iv-a) _oa/cikti boşsa TAMAM damgalanamaz — ⚠ notu yetmez, snapshot kilitlenir.
    if not kalemler and not zorla:
        print("HATA: _oa/cikti bos — tam tur adimlari calisma evraki birakmamis "
              "(FIZIKSEL ISLETIM PROTOKOLU). TAMAM damgalanmadi; snapshot alinmadi. "
              "Once adim ciktilari uret. (Bilerek gecmek icin: --zorla)", file=sys.stderr)
        return 1

    # (iv-b) Yutma denetimi: ÖNCEKİ snapshot varsa, ona göre bekleyen delta (yeni+değişen)
    # her evrak GELİŞMELER'de anılmış mı? Anılmayan varsa işlenmemiş evrak snapshot'a yutulamaz.
    onceki_snapshot = durum.get("kunye_snapshot")
    serh_yutma = []
    if onceki_snapshot is not None:
        y0, d0, _s0 = _delta_hesapla(kok, durum)
        bekleyen = list(y0 or []) + list(d0 or [])
        if bekleyen:
            # Yalnız SON snapshot'tan SONRA eklenmiş gelişme kayıtları sayılır (bayatlık
            # kapatma): önceki döngüde anılmış bir evrak, snapshot tazelendikten sonra
            # tekrar değişip hiç işlenmeden geçmiş bir anmayla yutulamasın. Sınır, snapshot
            # alınırken kaydedilen gelişme LİSTE UZUNLUĞUdur (`gelisme_sayisi`) — dakika
            # çözünürlüklü tarihe değil kesin konuma dayanır. Eski (bu alanı içermeyen)
            # snapshot'larda 0'a düşer: geri uyumlu, bir sonraki --kaydet kendini onarır.
            since_index = onceki_snapshot.get("gelisme_sayisi")
            if not isinstance(since_index, int) or since_index < 0:
                since_index = 0
            gelisme_gecerli = durum.get("gelismeler", [])[since_index:]
            anilan = _anilan_evraklar(durum, since_index=since_index)
            ozet_blob = " ".join(g.get("ozet", "") for g in gelisme_gecerli)
            anilmayan = [e for e in bekleyen if e not in anilan and e not in ozet_blob]
            if anilmayan and not zorla:
                print("HATA: islenmemis evrak snapshot'a yutulamaz — su evrak(lar) hicbir "
                      "GELISME kaydinda anilmamis:", file=sys.stderr)
                for e in anilmayan:
                    print(f"   ! {e}", file=sys.stderr)
                print("Cozum: her biri icin `--ekle \"...\"` ile gelisme yaz, sonra --kaydet. "
                      "(Bilerek gecmek icin: --zorla)", file=sys.stderr)
                return 1
            if anilmayan and zorla:
                serh_yutma = anilmayan

    # (iv-c) Defter kapısı: pipeline defteri (_oa/defter/pipeline-olaylar.jsonl) bu
    # kökte AÇILMIŞSA, pipeline_kayit.py --denetle mantığı BEKLIYOR/kanıtsız adım
    # bulursa TAMAM damgalanamaz (boşluklu tur teslim edilemez, delta çağında da
    # geçerli). Defter hiç açılmamışsa (defter kullanmayan akış) kapı atlanır.
    defter_temiz, defter_cikti = _defter_denetle(kok)
    serh_defter = None
    if not defter_temiz:
        if not zorla:
            print("HATA: pipeline defteri TESLIM ENGELI bildiriyor — BEKLIYOR/kanitsiz "
                  "adim(lar) var; TAMAM damgalanamadi. (Bilerek gecmek icin: --zorla)",
                  file=sys.stderr)
            if defter_cikti:
                print(defter_cikti, file=sys.stderr)
            return 1
        serh_defter = defter_cikti or "pipeline defteri TESLIM ENGELI bildirdi (ayrinti yok)"
    elif defter_cikti:
        # temiz ama bilgilendirici bir mesaj var (ör. betik bulunamadı) — sessiz geçme.
        print(defter_cikti, file=sys.stderr)

    bos_cikti_zorla = (not kalemler and zorla)

    durum["dosya"] = durum.get("dosya") or os.path.basename(os.path.abspath(kok))
    durum["tam_tur_durumu"] = "TAMAM"
    durum["tam_tur_tarihi"] = _simdi()
    durum["kunye_snapshot"] = {
        "toplam_evrak": kunye.get("toplam_evrak"),
        "alindi": _simdi(),
        "imzalar": _evrak_imzalari(kunye),
        # Bu snapshot anındaki gelişme sayısı — bir SONRAKİ kaydet'te (iv-b) yalnız
        # BU İNDEXTEN SONRA eklenen gelişmelerin sayılması için (bkz. _anilan_evraklar).
        "gelisme_sayisi": len(durum.get("gelismeler", [])),
    }
    durum["adim_ciktilari"] = kalemler
    durum.setdefault("gelismeler", [])
    _durum_yaz(kok, durum)

    # Model-okur kayıt belgesi
    os.makedirs(_analiz_dizin(kok), exist_ok=True)
    with open(_analiz_md(kok), "w", encoding="utf-8") as f:
        f.write(f"# DOSYA ANALİZ KAYDI (TAM TUR) — {durum['dosya']}\n\n")
        f.write(f"- Tam tur tarihi: **{durum['tam_tur_tarihi']}**\n")
        f.write(f"- Snapshot evrak sayısı: **{durum['kunye_snapshot']['toplam_evrak']}**\n")
        if bos_cikti_zorla or serh_yutma or serh_bayat or serh_defter:
            f.write("- ⚠ **ŞERH (--zorla ile kaydedildi):**\n")
            if bos_cikti_zorla:
                f.write("  - _oa/cikti boş olmasına rağmen zorla damgalandı "
                        "(adımlar çalışma evrakı bırakmamış).\n")
            if serh_yutma:
                f.write("  - GELİŞMELER'de anılmadan snapshot'a yutulan işlenmemiş evrak: "
                        + ", ".join(f"`{e}`" for e in serh_yutma) + "\n")
            if serh_bayat:
                f.write("  - bayat künye üzerinden zorla damgalandı: "
                        + ", ".join(f"`{e}`" for e in serh_bayat) + "\n")
            if serh_defter:
                tek_satir = " ".join(serh_defter.split())[:400]
                f.write("  - Pipeline defteri TESLİM ENGELİ bildirmesine rağmen zorla "
                        f"damgalandı: {tek_satir}\n")
        f.write("- Bu belge, tam turun MODEL-OKUR çıktısıdır. Sonraki oturumlar TAM TURU\n")
        f.write("  TEKRAR YAPMAZ; yeni evrak/gelişme geldiğinde `--delta` ile yalnız yeni\n")
        f.write("  kısım işlenir ve `--ekle` ile aşağıdaki GELİŞMELER günlüğüne yazılır.\n\n")
        f.write("## Adım çıktıları (tam turun kanıtı — _oa/cikti/)\n\n")
        if kalemler:
            f.write("| Çalışma evrakı | Boyut (bayt) |\n|---|---|\n")
            for k in kalemler:
                f.write(f"| `{k['yol']}` | {k['boyut']} |\n")
        else:
            f.write("> ⚠ _oa/cikti/ boş — tam tur adımları çalışma evrakı bırakmamış "
                    "(FİZİKSEL İŞLETİM PROTOKOLÜ ihlali; adımlar evraksız 'UYGULANDI' sayılmaz).\n")
        f.write("\n## GELİŞMELER GÜNLÜĞÜ (artımlı — tam tur tekrar edilmez)\n\n")
        f.write("_(yeni evrak/delil/gelişme buraya `--ekle` ile eklenir)_\n")
    print(f"TAM TUR kaydedildi: {durum['dosya']} · {durum['kunye_snapshot']['toplam_evrak']} evrak "
          f"snapshot · {len(kalemler)} adım çıktısı"
          + ("  [--zorla ile ŞERHLİ]" if (bos_cikti_zorla or serh_yutma or serh_bayat or serh_defter) else ""))
    print(f"Kayıt belgesi: {_analiz_md(kok)}")
    print("Bundan sonra yeni evrakta: python tam_tur.py --delta  (tam tur TEKRAR YOK)")
    return 0


def cmd_delta(kok):
    # (i) Diski hızlı tara: künye diskle örtüşmüyorsa delta körleşir → önce ingest.
    b = _bayat_kontrol_yaz(kok)
    if b:
        return b
    durum = _durum_oku(kok)
    if not durum or durum.get("tam_tur_durumu") != "TAMAM":
        print("TAM TUR YOK/EKSİK → önce tam tur yapılıp `--kaydet` ile kapatılmalı.")
        return 3
    yeni, degisen, silinen = _delta_hesapla(kok, durum)
    if yeni is None:
        print("HATA: güncel künye okunamadı (oa-ingest yeniden koşmalı).", file=sys.stderr)
        return 1
    kunye = _kunye_oku(kok)
    guncel_imza = _evrak_imzalari(kunye) if kunye else {}
    snap_imza = durum.get("kunye_snapshot", {}).get("imzalar", {})
    rename = _yeniden_adlandirma(guncel_imza, snap_imza, yeni, silinen)
    if not yeni and not degisen and not silinen:
        print(f"DELTA YOK — tam tur güncel ({durum.get('tam_tur_tarihi')}). "
              "Tüm evrak snapshot'ta; yeniden analiz gereksiz.")
        return 0
    print(f"ARTIMLI MOD — tam tur ({durum.get('tam_tur_tarihi')}) KORUNUR, TEKRAR YAPILMAZ.")
    if yeni:
        print(f"\nYENİ evrak ({len(yeni)}) — yalnız bunlar işlenip GELİŞMELER'e eklenecek:")
        for k in yeni:
            print(f"   + {k}")
    if degisen:
        print(f"\nDEĞİŞEN evrak ({len(degisen)}) — içerik (sha) değişmiş, gözden geçir:")
        for k in degisen:
            print(f"   ~ {k}")
    if silinen:
        print(f"\nSİLİNEN/KALDIRILAN evrak ({len(silinen)}) — snapshot'ta vardı, artık yok:")
        for k in silinen:
            print(f"   - {k}")
    if rename:
        print(f"\nYENİDEN ADLANDIRMA ipucu ({len(rename)}) — aynı içerik (sha), farklı ad:")
        for eski, yeni_ad in rename:
            print(f"   {eski}  ->  {yeni_ad}")
    print("\nİşlem: yalnız yeni/değişen/silinen evrakı ilgili parçalara ver, sonucu\n"
          "  python tam_tur.py --ekle \"...\"  ile kayda geçir; ardından --kaydet ile snapshot tazele.")
    return 3


def cmd_ekle(kok, ozet):
    durum = _durum_oku(kok)
    if not durum:
        print("HATA: tam tur kaydı yok — önce --baslat/--kaydet.", file=sys.stderr)
        return 1
    yeni, degisen, silinen = _delta_hesapla(kok, durum)
    kayit = {"tarih": _simdi(), "ozet": ozet,
             "yeni_evrak": yeni or [], "degisen_evrak": degisen or [],
             "silinen_evrak": silinen or []}
    durum.setdefault("gelismeler", []).append(kayit)
    _durum_yaz(kok, durum)
    # md günlüğüne işle
    md = _analiz_md(kok)
    satir = (f"\n### {kayit['tarih']} — gelişme\n"
             f"- Özet: {ozet}\n"
             + (f"- Yeni evrak: {', '.join(yeni)}\n" if yeni else "")
             + (f"- Değişen evrak: {', '.join(degisen)}\n" if degisen else "")
             + (f"- Silinen evrak: {', '.join(silinen)}\n" if silinen else ""))
    if os.path.exists(md):
        with open(md, "a", encoding="utf-8") as f:
            f.write(satir)
    print(f"GELİŞME kaydedildi ({kayit['tarih']}): {ozet}")
    print("Not: snapshot'ı tazelemek için `--kaydet` (yeni evrak artık tam turun parçası sayılır).")
    return 0


def cmd_durum(kok):
    # (i) Diski hızlı tara: künye bayatsa uyarıyı basar (körlük kapanır).
    bayat = _bayat_kontrol_yaz(kok)
    durum = _durum_oku(kok)
    if not durum:
        print("TAM TUR: hiç yapılmamış. İlk iş: tam tur (manifest→ingest→...→kontrol) + `--kaydet`.")
        return 3
    print(f"Dosya           : {durum.get('dosya')}")
    print(f"Tam tur durumu  : {durum.get('tam_tur_durumu')}  ({durum.get('tam_tur_tarihi') or '—'})")
    snap = durum.get("kunye_snapshot", {})
    print(f"Snapshot evrak  : {snap.get('toplam_evrak', '—')}  (alındı: {snap.get('alindi', '—')})")
    print(f"Gelişme kaydı   : {len(durum.get('gelismeler', []))}")
    if durum.get("tam_tur_durumu") == "TAMAM":
        yeni, degisen, silinen = _delta_hesapla(kok, durum)
        if yeni is None:
            print("Delta           : güncel künye okunamadı (oa-ingest?).")
            return 1
        if yeni or degisen or silinen:
            print(f"Delta           : BEKLİYOR → {len(yeni)} yeni, {len(degisen)} değişen, "
                  f"{len(silinen)} silinen (artımlı mod: `--delta`).")
            return 3
        if bayat:
            # künye diskle örtüşmüyor → "güncel" demek KÖRLÜK olurdu; ingest'e yönlendir.
            print("Delta           : KUNYE BAYAT (yukaridaki uyari) — once oa_ingest kos.")
            return 3
        print("Delta           : yok — tam tur güncel.")
        return 0
    return 3


def main():
    ap = argparse.ArgumentParser(description="tam_tur.py — TAM TUR yaşam döngüsü (bir kez + delta)")
    ap.add_argument("--kok", default=".", help="çalışma kökü (varsayılan: bulunulan klasör)")
    ap.add_argument("--durum", action="store_true")
    ap.add_argument("--baslat", action="store_true")
    ap.add_argument("--dosya")
    ap.add_argument("--kaydet", action="store_true")
    ap.add_argument("--delta", action="store_true")
    ap.add_argument("--ekle", metavar="OZET")
    ap.add_argument("--zorla", action="store_true",
                    help="kaydet: boş-çıktı / işlenmemiş-delta engelini şerh düşerek geç")
    a = ap.parse_args()

    kok = a.kok
    if not os.path.isdir(kok):
        sys.exit(f"HATA: klasör yok: {kok}")

    if a.baslat:
        sys.exit(cmd_baslat(kok, a.dosya))
    if a.kaydet:
        sys.exit(cmd_kaydet(kok, a.zorla))
    if a.delta:
        sys.exit(cmd_delta(kok))
    if a.ekle is not None:
        sys.exit(cmd_ekle(kok, a.ekle))
    # varsayılan: durum
    sys.exit(cmd_durum(kok))


if __name__ == "__main__":
    main()

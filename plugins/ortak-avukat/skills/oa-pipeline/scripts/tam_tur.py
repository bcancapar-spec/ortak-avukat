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

DOĞUM-ANI KALICILIK (M3-0 — Gate G+): dosya-analiz.md her incelenen dosyada BAŞTAN
kurulur ve DAİMA MEVCUTTUR — DEVİR (handoff) için ucuz giriş noktası; bir parça devir
aldığında ham evrakı baştan okumaz, bu kaydı okur. TEK SAHİP bu script'tir (oa_ingest/
oa_hafiza dosya-analiz.md'ye YAZMAZ). Üç komut, TEK render motoru üzerine kurulu:
  - `--baslat`  : iskelet YOKSA doğurur (atomik+idempotent); VARSA içeriğe DOKUNMAZ,
                  yalnız başlık satırındaki dosya adını gerekirse tazeler.
  - `--senkron` : dosya-analiz.md'yi İSKELET + `_oa/cikti/*` + `00-kunye.json` +
                  `dosya-analiz.json`dan DETERMİNİSTİK olarak YENİDEN TÜRETİR (atomik,
                  idempotent, TAMAM işaretçisi ASLA üretmez). Md hiçbir bilginin TEK
                  nüshasını TAŞIMAZ — her bölüm birincil kaynaktan türetilir; OKUNABİLİR
                  (metin) her `_oa/cikti/*` dosyası BOYUTTAN BAĞIMSIZ TAM gömülür (M3-0
                  düzeltmesi — muhakeme kaybı yok: bir İçtihat Muhakeme/Kıyas/Strateji/
                  Antitez/Yazım çıktısı binlerce karakter olsa da özetlenmez), yalnız
                  gerçekten İKİLİ/okunamayan içerik öz+yol+sha16 ile temsil edilir (bu
                  da muhakeme metni DEĞİLDİR — ikili veri zaten özetlenebilir metin
                  taşımaz).
  - `--kaydet`  : son `--senkron` + evrak snapshot'ı + TAMAM damgası (tek birleştirici).
Bölümler `<!-- oa:bolum:NN-ad -->` ayraçlarıyla 0(Künye)…14(CATCH-ALL — haritaya
eşleşmeyen HER `_oa/cikti` dosyası; hiçbir şey düşmez) arası sabittir. Parçalar bu
belgeye ASLA doğrudan yazmaz — yalnız `_oa/cikti/*`'a yazar, senkron/kaydet toplar.

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
--zorla ile geçilirse dosya-analiz.md ŞERH bölümüne (13) kalıcı olarak işlenir (durum.json
`serh_tarihcesi`'nde — sessiz geçiş yok, senkron sonrası da kaybolmaz).

DEFTER KAPISI (§6-B(iv), boşluklu tur teslim edilemez): `--kaydet`, bayat-künye kapısı,
_oa/cikti boşluğu ve işlenmemiş-delta yutmasının yanına DÖRDÜNCÜ bir denetim ekler — bu
kökte oa-pipeline'ın pipeline_kayit.py --baslat ile açtığı bir olay defteri
(_oa/defter/pipeline-olaylar.jsonl) varsa, aynı dizindeki pipeline_kayit.py --denetle
mantığı alt süreçte koşturulur; BEKLIYOR veya kanıtsız adım varsa TAMAM damgalanamaz
(--zorla ile ŞERH düşülerek geçilebilir). Defter hiç açılmamışsa (defter kullanmayan akış)
bu kapı sessizce atlanır — mevcut davranış korunur.

GATE G+ — KALICILIK KAPISI (`--durum`, mekanik, M3-0 ile genişledi): "tamamlandi" durum
.json'daki öz-beyandan (`tam_tur_durumu: TAMAM`) BAĞIMSIZ olarak, diskteki fiziksel
kanıtla yeniden doğrulanır — DÖRT koşul: (1) dosya-analiz.md VAR, (2) BOŞ DEĞİL,
(3) mtime tam-tur başlangıcından (`--baslat` zamanı) ESKİ DEĞİL, (4) [M3-0] md İÇİNDE
yalnız `--kaydet`in yazdığı `<!-- oa:tam-tur:TAMAM <tarih> -->` işaretçisi VAR. İlk üçü
tek başına YETMEZ — İSKELET (--baslat/--senkron) da VAR+dolu+taze olabilir ama TAMAM
işaretçisi taşımaz; işaretçisiz iskelet HER ZAMAN "tamamlanmadi" sayılır (exit 3,
fail-closed). Kendini-onarma: `--durum`/`--senkron` md YOKSA/BOZUKSA (bölüm ayraçları
eksikse) iskeleti birincil kaynaklardan YENİDEN KURAR + GÖRÜNÜR bir uyarı basar; bu
onarım TAMAM ÜRETMEZ (yalnız gerçek `--kaydet` işaretçiyi kazandırır). Kalıcı kayıt
(dosya-analiz.md ve dosya-analiz.json) her zaman ATOMİK (tmp + os.replace) yazılır.

Kullanım:
  python tam_tur.py --durum                         # tam tur var mı, delta var mı, künye bayat mı
  python tam_tur.py --baslat --dosya "<ad>"         # tam tur başlat (iskelet doğar, snapshot planlanır)
  python tam_tur.py --senkron                        # dosya-analiz.md'yi birincil kaynaklardan YENİDEN TÜRET (TAMAM YOK)
  python tam_tur.py --kaydet                         # son --senkron + snapshot al (tam tur BİTTİ, TAMAM damgalanır)
  python tam_tur.py --kaydet --zorla                 # boş-çıktı / bayat-künye / işlenmemiş-delta / defter-engeli ŞERH düşerek geç
  python tam_tur.py --delta                          # snapshot'tan bu yana YENİ/DEĞİŞEN/SİLİNEN evrak
  python tam_tur.py --ekle "<gelişme özeti>"         # artımlı gelişme kaydı (durum.json'a; md sonraki senkron/kaydet'te yansır)
  python tam_tur.py --brif                            # M1-4 Gate E: ARTIMLI MOD BRİFİ (--durum'un aynı
                                                        # mekanik sinyaline dayanır; ARAŞTIRMA/analiz
                                                        # adımının "ham evrağı toplu yeniden okuma /
                                                        # tam turu tekrar koşma" kararını verirken okuduğu
                                                        # tek komut)
  python tam_tur.py --kok "<klasör>"                 # çalışma kökü (varsayılan: bulunulan klasör)

Çıkış kodu: 0 = tam tur güncel / iş tamam (--senkron her zaman 0 döner — bir onarım
DEĞİL, rutin türetimdir); 3 = tam tur yok VEYA bekleyen delta var VEYA künye bayat
(`--durum`/`--delta`de; pipeline bunu okuyup "artımlı mod"a / "önce ingest"e geçer);
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
import re
import subprocess
import sys

# Diskte "ham evrak" sayılan uzantılar (oa_ingest'in işlediği tipler). `_oa` taranmaz.
HAM_UZANTILAR = {".pdf", ".udf", ".docx", ".eyp", ".zip",
                 ".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp", ".gif",
                 ".txt", ".md", ".rtf", ".html", ".htm", ".csv", ".xml"}
ATLA_DIZIN = {"_oa", ".claude", "__pycache__", ".git"}
BOS_SHA = hashlib.sha256(b"").hexdigest()[:16]   # metinsiz kayıtların sabit imzası

# ── M3-0 — DOĞUM-ANI KALICILIK: bölüm iskeleti (0-14, sabit sıra) ───────────────
# (bölüm_no, slug, başlık) — slug marker'da kullanılır (<!-- oa:bolum:NN-slug -->).
# 1-10 arası, oa-pipeline SKILL.md'nin 0-9 numaralı ÇALIŞMA EVRAKI adlandırmasına
# (`_oa/cikti/NN-parca-*`) +1 kaydırmayla eşlenir (bölüm 0 = Künye, cikti'den değil
# `00-kunye.json`dan türer). Bölüm 14 CATCH-ALL: 00-09 dışı/eşlenmeyen HER cikti
# dosyası buraya düşer — hiçbir çalışma evrakı sessizce kaybolmaz.
BOLUM_TANIMLARI = [
    (0, "Kunye", "Künye"),
    (1, "Manifest", "Manifest"),
    (2, "Taraf-talep-sure", "Taraf / Talep / Süre"),
    (3, "Konumlama", "Konumlama"),
    (4, "Arastirma-ictihat-muhakeme", "Araştırma + İçtihat Muhakeme"),
    (5, "Olgu-delil", "Olgu / Delil"),
    (6, "Kiyas", "Kıyas"),
    (7, "Strateji", "Strateji"),
    (8, "Antitez", "Antitez"),
    (9, "Yazim", "Yazım"),
    (10, "Kontrol", "Kontrol"),
    (11, "Acik-uclar", "Açık Uçlar"),
    (12, "Gelismeler", "Gelişmeler"),
    (13, "Serh", "Şerh"),
    (14, "Diger-calisma-evraklari", "Diğer Çalışma Evrakları (CATCH-ALL)"),
]
TAMAM_DESEN = re.compile(r"<!--\s*oa:tam-tur:TAMAM\b[^>]*-->")


def _bolum_marker(no):
    for n, slug, _ in BOLUM_TANIMLARI:
        if n == no:
            return f"<!-- oa:bolum:{n:02d}-{slug} -->"
    raise ValueError(f"tanımsız bölüm: {no}")


def _tamam_marker(tarih):
    return f"<!-- oa:tam-tur:TAMAM {tarih} -->"


def _tamam_isaretci_var_mi(icerik):
    """Gate G+ (M3-0 delinme kapatma — Fable K CONFIRMED): TAMAM işaretçisi YALNIZ md'nin
    SON boş-olmayan satırında TAM SATIR olarak sayılır. `_md_render` işaretçiyi (yalnız
    `--kaydet`te) daima belgenin EN SONUNA yazar; cikti gövdesine tam gömülen bir dosyanın
    İÇİNDE (örnek/backtick) geçen marker metni artık sahte-TAMAM üretemez. Ek savunma:
    `_marker_etkisizlestir` gömülü tam-marker satırlarını da nötrler."""
    for satir in reversed((icerik or "").splitlines()):
        s = satir.strip()
        if not s:
            continue
        return bool(TAMAM_DESEN.fullmatch(s))
    return False


def _marker_etkisizlestir(metin):
    """Gömülen cikti gövdesindeki TAM-SATIR TAMAM marker'ını görünür şekilde nötrler
    (Gate G+ delinmesine ikinci savunma katmanı). Orijinal dosyaya dokunulmaz + sha16 ile
    korunur → kayıpsızlıkla ÇELİŞMEZ (yalnız render annotasyonu; muhakeme metni silinmez)."""
    ciktilar = []
    for satir in metin.split("\n"):
        if TAMAM_DESEN.fullmatch(satir.strip()):
            ciktilar.append("⟨gömülü örnek — Gate G+ marker nötrlendi⟩ " + satir)
        else:
            ciktilar.append(satir)
    return "\n".join(ciktilar)


def _iskelet_saglam_mi(icerik):
    """Her 15 bölüm ayracı sırasıyla İÇERİKTE VAR mı? (kaba ama yeterli bütünlük
    denetimi — kendi biçimimizden SAPMIŞ/elle bozulmuş/eski-format bir dosyayı
    'bozuk' sayıp kendini-onarmayı tetikler)."""
    if not icerik:
        return False
    for n, slug, _ in BOLUM_TANIMLARI:
        if _bolum_marker(n) not in icerik:
            return False
    return True


def _cikti_bolum_no(dosya_adi):
    """`_oa/cikti/NN-...` adlandırmasındaki NN (00-09) → bölüm (1-10). Eşleşmeyen
    her şey (NN 00-09 dışında, ya da hiç NN yoksa) CATCH-ALL bölüm 14'e düşer."""
    m = re.match(r"^(\d{2})-", dosya_adi or "")
    if not m:
        return 14
    n = int(m.group(1))
    if 0 <= n <= 9:
        return n + 1
    return 14


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
    """kaynak → içerik imzası. Künyede `sha` varsa ondan kur (gerçek içerik imzası,
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
    """dosya-analiz.json'u ATOMİK yaz (tmp + os.replace) — kalıcı kayıt yarım
    yazımda asla bozuk/yarım görünmesin (Gate G — KALICILIK KAPISI)."""
    dizin = _analiz_dizin(kok)
    os.makedirs(dizin, exist_ok=True)
    hedef = _analiz_json(kok)
    tmp = f"{hedef}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(durum, f, ensure_ascii=False, indent=2)
    os.replace(tmp, hedef)


def _md_yaz_atomik(kok, icerik):
    """dosya-analiz.md'yi ATOMİK yaz (tmp + os.replace) — Gate G+'nin fiziksel
    kanıt denetimi (VAR+dolu+taze) yarım yazımda asla yanlış sinyal vermesin."""
    os.makedirs(_analiz_dizin(kok), exist_ok=True)
    hedef = _analiz_md(kok)
    tmp = f"{hedef}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(icerik)
    os.replace(tmp, hedef)


def _tam_tur_baslangic_epoch(durum):
    """durum['baslatildi'] (varsa, `--baslat` ile _simdi() biçiminde yazılır)
    epoch'a çevrilir. Ayrıştırılamazsa/yoksa None (kapı atlanır — --baslat hiç
    kullanılmadan doğrudan --kaydet ile çalışan geriye-uyum akışları için)."""
    s = durum.get("baslatildi") if durum else None
    if not s:
        return None
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M").timestamp()
    except Exception:
        return None


def _analiz_kaydi_fiziksel_tamam(kok, durum):
    """Gate G+ — KALICILIK KAPISI (mekanik, model beyanına DEĞİL diske dayanır):
    dosya-analiz.md VAR + BOŞ DEĞİL + mtime >= tam-tur başlangıcı (varsa) + İÇİNDE
    yalnız `--kaydet`in yazdığı TAMAM işaretçisi VAR (M3-0 — 4. koşul). İlk üçü
    tek başına YETMEZ: `--baslat`/`--senkron` ürettiği İSKELET de VAR+dolu+taze
    olabilir ama işaretçisiz KALIR — Gate G+'nin asıl kapattığı boşluk budur.
    Bu denetim durum.json'daki `tam_tur_durumu: TAMAM` öz-beyanından BAĞIMSIZDIR
    — o alan elle/başka araçla bozulsa, ya da dosya sonradan silinse/boşaltılsa
    ya da `--baslat` ile tur yeniden açılıp `--kaydet` ile TAZELENMEDEN bırakılsa
    bile bu fonksiyon fiziksel kanıtı yeniden doğrular. Döner: (tamam:bool, sebep:str).
    Yan etkisiz (SALT-OKUR) — kendini-onarma bu fonksiyonun DIŞINDA, yalnız
    `cmd_durum`/`cmd_senkron` içinde açıkça tetiklenir."""
    yol = _analiz_md(kok)
    if not os.path.exists(yol):
        return False, "dosya-analiz.md yok"
    try:
        boyut = os.path.getsize(yol)
    except OSError:
        boyut = 0
    if boyut == 0:
        return False, "dosya-analiz.md boş"
    baslangic = _tam_tur_baslangic_epoch(durum)
    if baslangic is not None:
        try:
            mtime = os.path.getmtime(yol)
        except OSError:
            mtime = None
        if mtime is not None and mtime < baslangic:
            return False, ("dosya-analiz.md tam-tur başlangıcından ESKİ (bayat kayıt — "
                            "--baslat sonrası --kaydet koşulmamış)")
    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            icerik = f.read()
    except OSError:
        return False, "dosya-analiz.md okunamadı"
    if not _tamam_isaretci_var_mi(icerik):
        return False, ("TAMAM işaretçisi yok (Gate G+ — iskelet/senkron VAR ama "
                        "`--kaydet` ile KAPATILMAMIŞ)")
    return True, ""


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


# ── M3-0 — TEK RENDER MOTORU (--baslat/--senkron/--kaydet hepsi bunu kullanır) ──

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


def _cikti_govde(kok, kalem):
    """Bir `_oa/cikti/*` dosyasının md gövdesi: OKUNABİLİR (metin, utf-8 çözülebilir)
    ise BOYUTTAN BAĞIMSIZ HER ZAMAN TAM gömülür — M3-0 düzeltmesi (Gate G+): eşiğe
    dayalı 'küçükse tam, büyükse öz' ayrımı KALDIRILDI, çünkü bu ayrım muhakeme
    ağırlıklı bölümlere (4-Araştırma+İçtihat Muhakeme, 6-Kıyas, 7-Strateji, 8-Antitez,
    9-Yazım) da ayrımsız uygulanıyor ve birkaç bin karakterlik gerçek bir gerekçelendirme
    dosya-analiz.md'ye yalnız ~300 karakterlik bir 'öz' olarak giriyordu — sonraki
    oturum ARTIMLI MOD'da (yalnız dosya-analiz.md + GELİŞMELER okunur, ham cikti
    TEKRAR AÇILMAZ) o muhakemeyi hiç görmüyordu. Bu, anayasanın 'muhakemede tasarruf
    ASLA yapılmaz' ilkesini ve hard invaryantı ('MUHAKEME KAYBI YOK', 'ÖZETLEME/digest
    YASAK') ihlal ederdi. Yalnız GERÇEKTEN İKİLİ/okunamayan (utf-8 çözülemeyen) içerik
    öz+yol+sha16 ile temsil edilir — bu bir özetleme DEĞİLDİR, çünkü ikili veri zaten
    özetlenebilir düzyazı/muhakeme taşımaz (metne çevrilebilir olsaydı oa-ingest onu
    zaten markdown/metin olarak üretirdi). Her iki durumda da TAM içerik diskte
    (`kalem['yol']`) kalır ve sha ile doğrulanabilir (veri kaybı yok)."""
    tam_yol = os.path.join(kok, kalem["yol"])
    try:
        with open(tam_yol, "rb") as f:
            veri = f.read()
    except OSError:
        return f"> ⚠ okunamadı: `{kalem['yol']}`\n\n"
    sha = hashlib.sha256(veri).hexdigest()[:16]
    baslik = f"### `{kalem['yol']}` ({kalem['boyut']} bayt, sha:{sha})\n\n"
    try:
        metin = _marker_etkisizlestir(veri.decode("utf-8"))
        okunabilir = True
    except UnicodeDecodeError:
        metin = None
        okunabilir = False
    if okunabilir:
        ext = os.path.splitext(kalem["dosya"])[1].lstrip(".").lower()
        if ext == "json":
            govde = f"```json\n{metin}\n```\n\n"
        elif ext in ("md", "txt", ""):
            govde = metin.rstrip("\n") + "\n\n"
        else:
            govde = f"```\n{metin}\n```\n\n"
    else:
        govde = ("> (ikili/okunamayan içerik — metin temsili yok)\n"
                 f"> Tam içerik dosyada (sha ile doğrulanır): `{kalem['yol']}`\n\n")
    return baslik + govde


def _md_render(kok, durum, tamam_tarih=None):
    """dosya-analiz.md'nin TAM İÇERİĞİNİ birincil kaynaklardan (iskelet + `_oa/cikti/*`
    + `00-kunye.json` + `dosya-analiz.json`/durum) DETERMİNİSTİK olarak üretir. Md
    hiçbir bilginin TEK nüshasını taşımaz. `tamam_tarih` verilmezse (None) TAMAM
    işaretçisi YAZILMAZ — bu, `--baslat`/`--senkron`'un asla TAMAM üretmemesinin
    (Gate G+'yi kasıtlı geçmemesinin) tek mekanizmasıdır; yalnız `cmd_kaydet` bu
    parametreyi doldurarak marker'ı ekler."""
    durum = durum or {}
    dosya_adi = durum.get("dosya") or os.path.basename(os.path.abspath(kok))
    kunye = _kunye_oku(kok)
    kalemler = _cikti_topla(kok)
    by_bolum = {i: [] for i in range(15)}
    for k in kalemler:
        by_bolum[_cikti_bolum_no(k["dosya"])].append(k)

    p = []
    p.append(f"# DOSYA ANALİZ KAYDI (TAM TUR) — {dosya_adi}\n\n")
    p.append("_Bu belge `tam_tur.py --senkron`/`--kaydet` ile birincil kaynaklardan "
              "(iskelet + `_oa/cikti/*` + `00-kunye.json` + `dosya-analiz.json`) "
              "DETERMİNİSTİK olarak yeniden türetilir; hiçbir bölüm burada TEK nüsha "
              "taşımaz — kaynağı diskte kalır. Parçalar bu belgeye ASLA doğrudan "
              "yazmaz, yalnız `_oa/cikti/*`'a yazar._\n\n"
              "- Sonraki oturumlar TAM TURU TEKRAR YAPMAZ; yeni evrak/gelişme geldiğinde "
              "`--delta` ile yalnız yeni kısım işlenir ve `--ekle` ile GELİŞMELER'e "
              "(bölüm 12) yazılır.\n\n")
    if durum.get("tam_tur_tarihi"):
        p.append(f"- Son `--kaydet`      : **{durum['tam_tur_tarihi']}**\n")
    if durum.get("baslatildi"):
        p.append(f"- Son `--baslat`      : **{durum['baslatildi']}**\n")
    if kunye is not None:
        p.append(f"- Künye toplam evrak  : **{kunye.get('toplam_evrak', '—')}**\n")
    p.append("\n")

    # bölüm 0 — Künye
    p.append(_bolum_marker(0) + "\n")
    p.append("## 0. Künye\n\n")
    if kunye is None:
        p.append("> `_oa/metin/00-kunye.json` henüz yok — oa-ingest koşulmadı.\n\n")
    else:
        p.append(f"- Toplam evrak     : **{kunye.get('toplam_evrak', '—')}**\n")
        p.append(f"- Künye kayıt sayısı: **{len(kunye.get('kayitlar', []))}**\n")
        p.append("- Künye dosyası     : `_oa/metin/00-kunye.json`\n\n")

    # bölüm 1-10 — _oa/cikti/NN-* eşlemesi (NN=00-09 → bölüm NN+1)
    for i in range(1, 11):
        baslik = next(b for n, _s, b in BOLUM_TANIMLARI if n == i)
        p.append(_bolum_marker(i) + "\n")
        p.append(f"## {i}. {baslik}\n\n")
        kalem = sorted(by_bolum.get(i, []), key=lambda x: x["dosya"])
        if not kalem:
            p.append("_(henüz çalışma evrakı yok)_\n\n")
        else:
            for k in kalem:
                p.append(_cikti_govde(kok, k))

    # bölüm 11 — Açık Uçlar
    p.append(_bolum_marker(11) + "\n")
    p.append("## 11. Açık Uçlar\n\n")
    acik = durum.get("acik_uclar") or []
    if not acik:
        p.append("_(henüz kayıt yok)_\n\n")
    else:
        for a in acik:
            p.append(f"- {a}\n")
        p.append("\n")

    # bölüm 12 — Gelişmeler (GELİŞMELER GÜNLÜĞÜ — durum.json'dan türer)
    p.append(_bolum_marker(12) + "\n")
    p.append("## 12. Gelişmeler\n\n")
    gelismeler = durum.get("gelismeler") or []
    if not gelismeler:
        p.append("_(yeni evrak/delil/gelişme buraya `--ekle` ile eklenir)_\n\n")
    else:
        for g in gelismeler:
            p.append(f"### {g.get('tarih')} — gelişme\n")
            p.append(f"- Özet: {g.get('ozet')}\n")
            if g.get("yeni_evrak"):
                p.append(f"- Yeni evrak: {', '.join(g['yeni_evrak'])}\n")
            if g.get("degisen_evrak"):
                p.append(f"- Değişen evrak: {', '.join(g['degisen_evrak'])}\n")
            if g.get("silinen_evrak"):
                p.append(f"- Silinen evrak: {', '.join(g['silinen_evrak'])}\n")
            p.append("\n")

    # bölüm 13 — Şerh (durum.json `serh_tarihcesi` — kalıcı, senkron'da kaybolmaz)
    p.append(_bolum_marker(13) + "\n")
    p.append("## 13. Şerh\n\n")
    serhler = durum.get("serh_tarihcesi") or []
    if not serhler:
        p.append("_(şerh yok)_\n\n")
    else:
        for s in serhler:
            p.append(f"### ⚠ ŞERH — {s.get('tarih')} (--zorla ile kaydedildi)\n")
            for satir in s.get("aciklamalar", []):
                p.append(f"- {satir}\n")
            p.append("\n")

    # bölüm 14 — Diğer Çalışma Evrakları (CATCH-ALL)
    p.append(_bolum_marker(14) + "\n")
    p.append("## 14. Diğer Çalışma Evrakları (CATCH-ALL)\n\n")
    kalem14 = sorted(by_bolum.get(14, []), key=lambda x: x["dosya"])
    if not kalem14:
        p.append("_(haritaya eşlenmeyen çalışma evrakı yok)_\n\n")
    else:
        for k in kalem14:
            p.append(_cikti_govde(kok, k))

    if tamam_tarih:
        p.append(_tamam_marker(tamam_tarih) + "\n")

    return "".join(p)


_ONARIM_UYARISI = (
    "UYARI: dosya-analiz.md eksik/bozuktu — İSKELET birincil kaynaklardan "
    "(_oa/cikti + 00-kunye.json + dosya-analiz.json) yeniden kuruldu; TAMAM "
    "işaretçisi ÜRETİLMEDİ (gerçek `--kaydet` ile yeniden kapatılmalı)."
)


def _bozuk_mu(kok):
    """dosya-analiz.md YOK mu veya BOZUK mu (bölüm iskeleti eksik/bütün değil)?
    Kendini-onarmanın (cmd_durum/cmd_senkron) tetikleyicisi — salt-okur."""
    yol = _analiz_md(kok)
    if not os.path.exists(yol):
        return True
    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            mevcut = f.read()
    except OSError:
        return True
    return (not mevcut.strip()) or (not _iskelet_saglam_mi(mevcut))


def _baslik_tazele(kok, dosya_adi):
    """`--baslat` idempotent yol: md zaten VARSA gövdeye DOKUNMAZ, yalnız ilk satırdaki
    başlığı (dosya adı) güncel değilse ATOMİK olarak tazeler. Tanınmayan/bozuk ilk
    satır varsa dokunmaz — o onarım `--durum`/`--senkron`'un işidir."""
    yol = _analiz_md(kok)
    try:
        with open(yol, encoding="utf-8") as f:
            icerik = f.read()
    except OSError:
        return
    satir_sonu = icerik.find("\n")
    if satir_sonu == -1:
        return
    ilk_satir = icerik[:satir_sonu]
    beklenen = f"# DOSYA ANALİZ KAYDI (TAM TUR) — {dosya_adi}"
    if ilk_satir == beklenen or not ilk_satir.startswith("# DOSYA ANALİZ KAYDI"):
        return
    yeni_icerik = beklenen + icerik[satir_sonu:]
    tmp = f"{yol}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(yeni_icerik)
    os.replace(tmp, yol)


def cmd_baslat(kok, dosya):
    durum = _durum_oku(kok) or {}
    durum.setdefault("dosya", dosya or durum.get("dosya") or os.path.basename(os.path.abspath(kok)))
    if dosya:
        durum["dosya"] = dosya
    durum["tam_tur_durumu"] = "DEVAM"
    durum.setdefault("gelismeler", [])
    durum["baslatildi"] = _simdi()
    _durum_yaz(kok, durum)

    # DOĞUM: dosya-analiz.md YOKSA iskelet ATOMİK doğar (0.adım atlanamaz —
    # "DAİMA MEVCUT" garantisinin başlangıç noktası). VARSA idempotent: gövdeye
    # DOKUNULMAZ, yalnız başlık (dosya adı) gerekirse tazelenir.
    yol = _analiz_md(kok)
    if not os.path.exists(yol):
        icerik = _md_render(kok, durum, tamam_tarih=None)
        _md_yaz_atomik(kok, icerik)
        print(f"İskelet kuruldu: {yol}")
    else:
        _baslik_tazele(kok, durum["dosya"])

    print(f"TAM TUR başlatıldı: {durum['dosya']} ({durum['baslatildi']})")
    print("Aile tüm parçaları işletsin; her adım _oa/cikti/ altına çalışma evrakı bıraksın.")
    print("Tur bitince: python tam_tur.py --kaydet  (ara güncelleme için: --senkron — "
          "DİKKAT: --senkron TAMAM damgası YAZMAZ; --kaydet sonrası çağrılırsa damga "
          "düşer, geri kazanmak için tekrar --kaydet gerekir).")
    return 0


def cmd_senkron(kok):
    """dosya-analiz.md'yi birincil kaynaklardan (iskelet + cikti + kunye + durum)
    DETERMİNİSTİK olarak YENİDEN TÜRETİR. Atomik + idempotent. TAMAM işaretçisi
    ASLA yazmaz (yalnız `--kaydet`in işidir) — md yok/bozuksa GÖRÜNÜR uyarıyla
    kendini onarır ama bu onarım tamamlanmış saymaz (Gate G+ fail-closed kalır).
    Yan bulgu düzeltmesi: `--kaydet` sonrası (TAMAM işaretli) bir md üzerinde
    `--senkron` çağrılırsa TAMAM işaretçisi bu render'da YOK sayılır (yalnız
    `--kaydet` onu yeniden yazar) — veri kaybı yoktur (durum.json'daki gerçek
    kaynaklar bozulmaz, bir sonraki `--kaydet` işaretçiyi geri kazandırır) ama
    sessizce olursa şaşırtıcıdır; bu yüzden burada AÇIKÇA bildirilir."""
    durum = _durum_oku(kok) or {}
    onarim_gerekti = _bozuk_mu(kok)
    # TAMAM işaretçisi bu senkronla düşecek mi? (önceki --kaydet'in izini taşıyordu mu)
    tamam_dusuyor = False
    yol = _analiz_md(kok)
    if os.path.exists(yol):
        try:
            with open(yol, encoding="utf-8", errors="replace") as f:
                onceki_icerik = f.read()
            tamam_dusuyor = _tamam_isaretci_var_mi(onceki_icerik)
        except OSError:
            pass
    icerik = _md_render(kok, durum, tamam_tarih=None)
    _md_yaz_atomik(kok, icerik)
    if onarim_gerekti:
        print(_ONARIM_UYARISI, file=sys.stderr)
    print(f"SENKRON: dosya-analiz.md _oa/cikti + 00-kunye.json + dosya-analiz.json'dan "
          f"deterministik yeniden türetildi ({_simdi()}).")
    print(f"Kayıt belgesi: {_analiz_md(kok)}")
    if tamam_dusuyor:
        print("NOT: bu dosya-analiz.md daha önce `--kaydet` ile TAMAM damgalanmıştı — "
              "`--senkron` TAMAM işaretçisini ASLA yazmaz, bu yüzden damga bu render'da "
              "DÜŞTÜ (veri kaybı yok: durum.json'daki gerçek kayıtlar korunur, Gate G+ "
              "şimdi 'tamamlanmadi' der). Damgayı geri kazanmak için: `python tam_tur.py "
              "--kaydet`.", file=sys.stderr)
    return 0


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
    # dosya-analiz.md ŞERH bölümüne (13, durum.json'da KALICI) işlenir.
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

    # ŞERH — durum.json'da KALICI tarihçe (M3-0): md hiçbir bilginin TEK nüshasını
    # taşımaz; --zorla ile geçilen her uyarı burada kalır, senkron/kendi-onarma
    # sırasında da (md yeniden türetilse bile) bölüm 13'te GÖRÜNÜR kalmaya devam eder.
    aciklamalar = []
    if bos_cikti_zorla:
        aciklamalar.append("_oa/cikti boş olmasına rağmen zorla damgalandı "
                            "(adımlar çalışma evrakı bırakmamış).")
    if serh_yutma:
        aciklamalar.append("GELİŞMELER'de anılmadan snapshot'a yutulan işlenmemiş evrak: "
                            + ", ".join(f"`{e}`" for e in serh_yutma))
    if serh_bayat:
        aciklamalar.append("bayat künye üzerinden zorla damgalandı: "
                            + ", ".join(f"`{e}`" for e in serh_bayat))
    if serh_defter:
        tek_satir = " ".join(serh_defter.split())[:400]
        aciklamalar.append("Pipeline defteri TESLİM ENGELİ bildirmesine rağmen zorla "
                            f"damgalandı: {tek_satir}")
    if aciklamalar:
        durum.setdefault("serh_tarihcesi", []).append(
            {"tarih": _simdi(), "aciklamalar": aciklamalar})

    durum.setdefault("gelismeler", [])
    _durum_yaz(kok, durum)

    # --kaydet = son --senkron + snapshot (yukarıda) + TAMAM damgası — TEK render
    # motoru (_md_render) üzerinden, ATOMİK yazım (Gate G+'nin fiziksel kanıt
    # denetimi yarım yazımda asla yanlış sinyal vermesin).
    icerik = _md_render(kok, durum, tamam_tarih=durum["tam_tur_tarihi"])
    _md_yaz_atomik(kok, icerik)

    serhli = bool(aciklamalar)
    print(f"TAM TUR kaydedildi: {durum['dosya']} · {durum['kunye_snapshot']['toplam_evrak']} evrak "
          f"snapshot · {len(kalemler)} adım çıktısı"
          + ("  [--zorla ile ŞERHLİ]" if serhli else ""))
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
    """Artımlı gelişme kaydı — YALNIZ durum.json'a yazar (M3-0: `--ekle` md-append
    KALKTI). dosya-analiz.md bölüm 12'ye bu kayıt bir SONRAKİ `--senkron`/`--kaydet`
    çağrısında yansır — md hiçbir bilginin tek nüshasını taşımadığı için bu gecikme
    veri kaybı DEĞİLDİR (kaynak durum.json'da kalıcıdır)."""
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
    print(f"GELİŞME kaydedildi ({kayit['tarih']}): {ozet}")
    print("Not: dosya-analiz.md'ye yansıtmak için `--senkron` (ya da snapshot'ı da "
          "tazelemek için `--kaydet`) — yeni evrak artık tam turun parçası sayılır.")
    return 0


def cmd_durum(kok):
    # (i) Diski hızlı tara: künye bayatsa uyarıyı basar (körlük kapanır).
    bayat = _bayat_kontrol_yaz(kok)
    durum = _durum_oku(kok)
    if not durum:
        print("TAM TUR: hiç yapılmamış. İlk iş: tam tur (manifest→ingest→...→kontrol) + `--kaydet`.")
        print("Analiz kaydı    : tamamlanmadi (tam tur hiç başlatılmamış)")
        return 3
    # Kendini-onarma (M3-0): dosya-analiz.md YOKSA/BOZUKSA burada, --durum'un
    # kendisi içinde, birincil kaynaklardan YENİDEN KURULUR + GÖRÜNÜR uyarı basılır.
    # Bu onarım TAMAM ÜRETMEZ — aşağıdaki Gate G+ denetimi yine "tamamlanmadi" der
    # (gerçek --kaydet gerekir); "DAİMA MEVCUT" garantisi böyle sağlanır.
    if _bozuk_mu(kok):
        icerik = _md_render(kok, durum, tamam_tarih=None)
        _md_yaz_atomik(kok, icerik)
        print(_ONARIM_UYARISI, file=sys.stderr)
    print(f"Dosya           : {durum.get('dosya')}")
    print(f"Tam tur durumu  : {durum.get('tam_tur_durumu')}  ({durum.get('tam_tur_tarihi') or '—'})")
    snap = durum.get("kunye_snapshot", {})
    print(f"Snapshot evrak  : {snap.get('toplam_evrak', '—')}  (alındı: {snap.get('alindi', '—')})")
    print(f"Gelişme kaydı   : {len(durum.get('gelismeler', []))}")
    # Gate G+ — KALICILIK KAPISI (mekanik): dosya-analiz.md fiziksel kanıtı +
    # TAMAM işaretçisi, durum.json'daki öz-beyandan BAĞIMSIZ doğrulanır. "tamamlandi"
    # = SCRIPT ÇIKTISI, model beyanı değil (bkz. _analiz_kaydi_fiziksel_tamam).
    fiziksel_tamam, fiziksel_sebep = _analiz_kaydi_fiziksel_tamam(kok, durum)
    print(f"Analiz kaydı    : {'tamamlandi' if fiziksel_tamam else 'tamamlanmadi'}"
          + (f"  ({fiziksel_sebep})" if not fiziksel_tamam else ""))
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
        if not fiziksel_tamam:
            # json "TAMAM" + delta temiz görünse de fiziksel kanıt yoksa/bayatsa
            # "güncel" denemez — Gate G+ kalıcılık kapısı önceliklidir.
            print("Delta           : yok ama fiziksel kalıcılık kapısı GEÇMEDİ (yukarı bkz).")
            return 3
        print("Delta           : yok — tam tur güncel.")
        return 0
    return 3


def cmd_brif(kok):
    """M1-4 GATE E — ARTIMLI MOD BRİFİ (TAM TUR DELTA ZORLAMA).

    --durum ile AYNI mekanik sinyale dayanır (tek gerçek kaynak — ayrı bir
    mantık icat edilmedi): Gate G+ (kalıcılık kapısı, M3-0 ile TAMAM işaretçisi
    dahil) + delta hesabı. Amaç, ARAŞTIRMA/analiz adımının önüne doğrudan
    tüketilebilir bir TALİMAT metni koymaktır — "tam tur TAMAM + delta yok" ise
    hat HAM evrağı toplu yeniden OKUMAZ / tam turu TEKRAR KOŞMAZ, yalnız
    dosya-analiz.md + GELİŞMELER günlüğü okunur; bekleyen delta varsa yalnız o
    evrak(lar) tek tek işlenir.

    Dönüş kodları --durum ile birebir aynı sözleşmeyi taşır: 0 = artımlı mod
    TAM AÇIK (tam tur güncel, toplu yeniden okuma GEREKSİZ); 3 = ZORUNLU TAM
    TUR gerekli VEYA yalnız bekleyen delta işlenmeli (KISMİ); 1 = ölçülemedi
    (künye okunamadı)."""
    bayat = _bayat_kontrol_yaz(kok)
    durum = _durum_oku(kok)
    if not durum or durum.get("tam_tur_durumu") != "TAMAM":
        print("ARTIMLI MOD: KAPALI — tam tur hiç yapılmamış/TAMAM değil.")
        print("TALİMAT: ZORUNLU TAM TUR işletilmeli (MANİFEST → ... → KONTROL), sonra --kaydet.")
        return 3
    fiziksel_tamam, fiziksel_sebep = _analiz_kaydi_fiziksel_tamam(kok, durum)
    if not fiziksel_tamam:
        print(f"ARTIMLI MOD: KAPALI — Gate G+ (kalıcılık kapısı) geçmedi ({fiziksel_sebep}).")
        print("TALİMAT: tam tur yeniden kapatılmalı (--kaydet), sonra tekrar --brif.")
        return 3
    yeni, degisen, silinen = _delta_hesapla(kok, durum)
    if yeni is None:
        print("ARTIMLI MOD: ÖLÇÜLEMEDİ — güncel künye okunamadı (oa-ingest yeniden koşmalı).")
        return 1
    if bayat:
        print("ARTIMLI MOD: KAPALI — künye diskle örtüşmüyor (yukarıdaki KÜNYE BAYAT uyarısı).")
        print("TALİMAT: önce oa_ingest koş, sonra tekrar --brif.")
        return 3
    if yeni or degisen or silinen:
        print(f"ARTIMLI MOD: KISMİ — tam tur ({durum.get('tam_tur_tarihi')}) KORUNUR, TEKRAR YAPILMAZ; "
              f"{len(yeni)} yeni, {len(degisen)} değişen, {len(silinen)} silinen evrak bekliyor.")
        print("TALİMAT: HAM evrağı TOPLU yeniden OKUMA — yalnız aşağıdaki evrak(lar) tek tek işlenir; "
              "kalan evrak dosya-analiz.md'den (GELİŞMELER günlüğü) devralınır.")
        for k in yeni:
            print(f"   + YENİ: {k}")
        for k in degisen:
            print(f"   ~ DEĞİŞEN: {k}")
        for k in silinen:
            print(f"   - SİLİNEN: {k}")
        print(f"Kayıt belgesi: {_analiz_md(kok)}")
        print("İşlem sonrası: `--ekle \"...\"` ile GELİŞME yaz, sonra `--kaydet` ile snapshot tazele.")
        return 3
    print(f"ARTIMLI MOD: TAM AÇIK — tam tur ({durum.get('tam_tur_tarihi')}) güncel, bekleyen delta yok.")
    print(f"Kayıt belgesi: {_analiz_md(kok)}")
    print("TALİMAT: ARAŞTIRMA/analiz adımı HAM evrağı TOPLU yeniden OKUMASIN, tam tur TEKRAR "
          "KOŞULMASIN — yalnız dosya-analiz.md + GELİŞMELER günlüğü okunur; avukatın somut yeni "
          "sorusu belirli bir evrakı gerektiriyorsa yalnız O evrak (tek tek, haritadan/seçici) açılır.")
    gelismeler = durum.get("gelismeler") or []
    if gelismeler:
        son = gelismeler[-3:]
        print(f"Son gelişme(ler) ({len(son)}/{len(gelismeler)}):")
        for g in son:
            print(f"   - {g.get('tarih')}: {g.get('ozet')}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="tam_tur.py — TAM TUR yaşam döngüsü (bir kez + delta)")
    ap.add_argument("--kok", default=".", help="çalışma kökü (varsayılan: bulunulan klasör)")
    ap.add_argument("--durum", action="store_true")
    ap.add_argument("--baslat", action="store_true")
    ap.add_argument("--dosya")
    ap.add_argument("--senkron", action="store_true",
                    help="M3-0: dosya-analiz.md'yi iskelet+cikti+kunye+durum'dan "
                         "deterministik yeniden türetir (TAMAM işaretçisi YAZMAZ; "
                         "md yok/bozuksa kendini onarır + GÖRÜNÜR uyarı basar)")
    ap.add_argument("--kaydet", action="store_true")
    ap.add_argument("--delta", action="store_true")
    ap.add_argument("--ekle", metavar="OZET")
    ap.add_argument("--zorla", action="store_true",
                    help="kaydet: boş-çıktı / işlenmemiş-delta engelini şerh düşerek geç")
    ap.add_argument("--brif", action="store_true",
                    help="M1-4 Gate E: ARTIMLI MOD BRİFİ (--durum sinyaline dayanır; "
                         "ARAŞTIRMA/analiz adımının toplu-yeniden-okuma kararı için)")
    a = ap.parse_args()

    kok = a.kok
    if not os.path.isdir(kok):
        sys.exit(f"HATA: klasör yok: {kok}")

    if a.baslat:
        sys.exit(cmd_baslat(kok, a.dosya))
    if a.senkron:
        sys.exit(cmd_senkron(kok))
    if a.kaydet:
        sys.exit(cmd_kaydet(kok, a.zorla))
    if a.delta:
        sys.exit(cmd_delta(kok))
    if a.ekle is not None:
        sys.exit(cmd_ekle(kok, a.ekle))
    if a.brif:
        sys.exit(cmd_brif(kok))
    # varsayılan: durum
    sys.exit(cmd_durum(kok))


if __name__ == "__main__":
    main()

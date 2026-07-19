---
name: oa-ingest
description: >-
  Ortak Avukat sisteminin ÇIKARIM / AI KATMANI parçası ve 0. MANİFEST adımının metin
  motoru. Bir dava/icra klasöründeki UYAP evrakları (PDF/TIFF/JPG/EYP/UDF/DOCX) ilk
  kez ele alınırken — herhangi bir oa- parçası ham evrağı GÖRÜNTÜ olarak açmadan ÖNCE
  — her evrağın metnini en ucuz doğru yoldan (metin PDF→PyMuPDF, taranmış→OCR,
  UDF/EYP/DOCX→aç) bir kez çıkar; belge-başına Markdown + kunye.json + 00-INDEX.md üret
  ki sonraki parçalar külliyatı görüntü değil ucuz metin+indeks üzerinden seçici okusun
  (OCR çıktısı "⚠ teyit" damgalı, orijinal salt-okunur). "Dosyayı işle / evrakları oku
  / metne çevir / taranmış evrak / OCR / neden bu kadar token" türü her işte — ve
  kapsamlı dava ilk kez ele alınırken, kullanıcı istemese bile — tetikle.
---

# oa-ingest — Çıkarım / AI Katmanı (0. MANİFEST'in metin motoru)

Sök-tak parça. UYAP evrak indiricisi klasörü "insan gözü" için üretir (PDF/TIFF/JPG/EYP); bu parça onu **yapay zekânın ucuza ve kesintisiz okuyabileceği metne** çevirir. Görevi: **her evrağın metnini en ucuz doğru yoldan bir kez çıkar · belge-başına `.md` + `kunye.json` + `00-INDEX.md` üret · her metni kaynağına bağla · OCR'ı ⚠ teyit damgala.** `manifest_olustur`'un sayımını tamamlayan çıkarım yarısıdır.

## Deterministik motor
Script hukuki değerlendirme yapmaz; **metni çıkarır, sınıflar, indeksler.** Neyin esaslı olduğu, hangi delilin neyi ispatladığı muhakemeye ve `oa-vakia`/`oa-ictihat`'e aittir.

```bash
python scripts/oa_ingest.py "<dava_klasoru>"           # _oa/metin/ üretir (INDEX + kunye.json + NNN-*.md)
python scripts/oa_ingest.py                            # argümansız = BULUNDUĞUN klasör
python scripts/oa_ingest.py "<klasor>" --ocr auto|zorla|kapali
python scripts/oa_ingest.py "<klasor>" --yeniden       # önbelleği yok say, hepsini yeniden çıkar
python scripts/oa_ingest.py "<klasor>" --isci 8        # açık paralellik (0=oto varsayılan, 1=seri)
```

Çıkarım yolları (model kurmaz, script çıkarır): metin PDF→**PyMuPDF** (bedava, kayıpsız) · taranmış PDF→render+**OCR** (⚠) · UDF→content.xml (bedava) · EYP/.zip→aç→içindeki PDF'i aynı hatta ver · TIFF/JPG/PNG→OCR (çok sayfa, ⚠) · DOCX→document.xml (bedava). Bir PDF'in "metin mi tarama mı" olduğu ELLE değil ÖLÇÜMLE (sayfa başına anlamlı karakter eşiği) belirlenir — "gördüm" beyanı değil, ölçüm.

Bağımlılık (Windows-dostu, binary'siz): `pip install pymupdf pillow`. OCR için ayrıca Tesseract + `tur` dil paketi; yoksa metin PDF/UDF/DOCX yine işlenir, taranmışlar "YÜKLENEMEDİ ⚠" damgasıyla künyeye yazılır (sessiz atlama yok).

## Çıktı sözleşmesi (`_oa/metin/`)
```
00-INDEX.md    → parça ÖNCE bunu okur: evrak tablosu (no, ad, tarih, yöntem, ⚠, karakter, dosya)
00-kunye.json  → makine-okur künye: her evrak için yöntem + teyit_gerek + karakter + kaynak
NNN-<slug>.md  → belge-başına metin; başlıkta kaynak+sayfa+yöntem, gövdede içerik
```
Sonraki parçalar ham evrağı DEĞİL `00-INDEX.md`'yi okur, sonra yalnız gereken `NNN-*.md`'ye iner; tam pasaj için o `.md` içinde grep'lenir. Orijinal PDF yalnızca imza/mühür/kroki gibi görüntünün esas olduğu ya da ⚠ künye teyidi gereken durumda açılır.

## İş akışı (pipeline adım 0)
1. `manifest_olustur.py <klasor>` → sayım + sınıflandırma (kaç evrak, kaç OCR).
2. `oa_ingest.py <klasor>` → çıkarım + `_oa/metin/` — **v1.5 PARALEL**: `--isci`
   verilmezse otomatik `min(çekirdek,8)` işçiyle koşar; büyük külliyatta (~50+
   evrak veya ağır OCR yükü) bu varsayılan duvar-saatini kısaltır ve elle
   müdahale GEREKTİRMEZ. Determinizm garantisi: `--isci 1` (seri) ile
   `--isci N` (paralel) çıktısı (00-kunye.json, her md'nin sha256'sı)
   BYTE-ÖZDEŞTİR — bkz. `tests/test_oa_ingest_paralel.py`. Hata ayıklarken veya
   tek-çekirdek ortamda `--isci 1` açıkça verilebilir.
3. Kanıtı deftere işle: `pipeline_kayit.py --isle --adim 0 --parca manifest --durum UYGULANDI --kanit "oa_ingest.py koştu: N evrak, M OCR, işçi=K, _oa/metin üretildi"`.
4. **Sayım denetimi:** indirilen evrak adedi = `kunye.json.toplam_evrak` değilse analiz BAŞLAMAZ (eksik adıyla raporlanır); `manifest_olustur.py <klasor> --mutabakat _oa/metin/00-kunye.json` bunu paralel koşu sonrasında da aynen denetler (paralellik mutabakat mantığını değiştirmez).

## Anayasal bloklar — tek kaynak (anayasa.md)
Bu parça, ailenin ortak anayasal ilkelerine tabidir — **Çaba/token standardı** (model/efor kullanıcının tercihi; muhakemede/doğrulamada/çıktı kalitesinde tasarruf YOK, yalnız mekanik katmanda kayıpsız verimlilik), **Örnekleme ilkesi** (konu sınırlaması yok — kapsam TÜM Türk hukuku), **Doğaçlama meşruiyeti** (yöntem serbest, olgu MCP-teyitli), ayrıca Doğrulama mimarisi, Anonimleştirme ve Layer 0 gizlilik. **Tek ve yetkili kaynak: `ortak-avukat/references/anayasa.md`.** (Bu parça alt-ajan olarak koşarken bu ilkeler `oa-pipeline/scripts/oa_hafiza.py ajan-brif` ile taşınır.)

## Bağlam kopmaz — atıf bütünlüğü (anayasal)
Üretilen her `.md` başlığında kaynağını (evrak no, dosya adı, sayfa, çıkarım yöntemi) taşır. OCR/zayıf çıkarım açıkça **⚠ teyit gerek** damgalıdır: karar/esas no, tarih, taraf gibi künye verisi OCR metninden "teyitli" alınamaz, orijinalden doğrulanır (bu, `oa-kontrol` atıf denetiminin ön şartıdır). Orijinal evrak **salt-okunurdur**; motor onu asla değiştirmez, tüm üretim `_oa/metin/` altına gider.

## Başbakan denetimi (anayasal)
Bu parça ailenin Başbakanı `oa-pipeline`'ın icra+denetimine tabidir: çağrıldığında disiplini istisnasız işletilir; "çıkardım" deyip script'i koşmamak YASAK.

## Fiziksel aktivasyon — simülasyon yasağı (anayasal)
Bu parça yalnızca ÜÇ kanıttan en az biriyle "çalıştı" sayılır: (1) Skill aracıyla FİİLEN çağrıldı ve bu gövde bağlama yüklendi; (2) `oa_ingest.py` gerçekten koştu ve `_oa/metin/` çıktısı görünür (BİTTİ satırı + INDEX); (3) çıkarım script'e bağlıdır — koşmamış script "koştu", çıkarılmamış metin "çıkarıldı" gösterilemez, bu halüsinasyonun ta kendisidir. Her kalıcı çıktı çalışılan klasörün `_oa/` yerel hafıza kökünde yaşar; statü `oa-pipeline` defterine kanıtla işlenir.

## Gizlilik (Layer 0 dostu)
Çıkarım (PyMuPDF/Tesseract/unzip) TAMAMEN YERELDİR; hiçbir müvekkil verisi dış araca gitmez. Bu parça `oa-gizlilik` Layer 0 ile çelişmez, onu KOLAYLAŞTIRIR — dışarıya gidecek olan artık ham dosya değil, süzülebilir metindir.

## Kompozisyon
`manifest_olustur` (sayım) → **oa-ingest** (çıkarım + INDEX) → `oa-vakia`/`oa-ictihat`/`oa-antitez`/`oa-dilekce` (hepsi INDEX'ten seçici okur, ham evrağı değil) · `oa-gizlilik` (yerel çıkarım, Layer 0 dostu) · `oa-pipeline` (defter/kanıt).

## Öğrenme günlüğü
Yeni bir evrak biçimi, çıkarım tuzağı (ör. sınır PDF, çok-katmanlı EYP) veya eşik ayarı öğrenildiğinde script/şablona ekle, aşağıya işle, yeniden paketle.

## Değişiklik Günlüğü
Tam günlük `references/degisiklik-gunlugu.md`'dedir. Güncel sürüm: **v3.20** (parça girişi v1.0; aile metodoloji sürümüne hizalandı).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

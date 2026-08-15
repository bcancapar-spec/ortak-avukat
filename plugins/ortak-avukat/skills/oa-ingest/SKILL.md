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
python scripts/oa_ingest.py "<klasor>" --onbakis 5      # P1-9(a): MEŞRU HIZLI KANAL, bkz. aşağı
```

**`--onbakis N` (P1-9a — meşru hızlı kanal, AYRI artefakt):** yalnız ilk N evrağı (`--onbakis-secim REGEX` ile önceliklendirilebilir) işler ve **ana hatta HİÇ karışmayan** `_oa/metin-onbakis/` dizinine yazar (`00-kunye.onbakis.json` + `00-INDEX.onbakis.md`); ana `_oa/metin/00-kunye.json`/`00-INDEX.md`/önbelleğe **tek bayt dokunmaz** — bayraksız TAM koşu byte-özdeş kalır. Çıkış kodu **4** (kısmi-tamam — "ONBAKIS: N/M — TAM DEĞİL"). Bu artefakt pipeline'ı **hiçbir adımda** yetkilendirmez: `pipeline_kayit.py`'nin İNGEST-ÖNCE kapısı yalnız `_oa/metin/00-kunye.json`'a (TAM koşu) bakar, `--onbakis` çıktısı bu dosyayı üretmediği için adım 1+ hâlâ blokludur — "TAM DEĞİL" damgası ayrı dosya adının kendisinde içkindir. `--onbakis` yalnız hızlı bir ilk-bakış/triyaj aracıdır; gerçek analiz için **--onbakis'siz tam koşu şarttır**.

Çıkarım yolları (model kurmaz, script çıkarır): metin PDF→**PyMuPDF** (bedava, kayıpsız) · taranmış PDF→render+**OCR** (⚠) · UDF→content.xml (bedava) · EYP/.zip→aç→içindeki PDF'i aynı hatta ver · TIFF/JPG/PNG→OCR (çok sayfa, ⚠) · DOCX→document.xml (bedava). Bir PDF'in "metin mi tarama mı" olduğu ELLE değil ÖLÇÜMLE (sayfa başına anlamlı karakter eşiği) belirlenir — "gördüm" beyanı değil, ölçüm.

**UDF OKUMA — bu ANA HAT ile ELLE YAZMA'yı KARIŞTIRMA:** yukarıdaki "UDF→content.xml" yalnız **OKUMA**dır — `oa_ingest.py`'nin kendi yerel/çevrimdışı/kayıpsız `udf_isle()` fonksiyonu (214 evraklık gerçek külliyatta 0 kayıpla doğrulanmıştır); bu ana hatta Görev D kapsamında DOKUNULMADI. **ALTIN KURAL (bağlayıcı, tüm aile için): UDF ELLE YAZILMAZ** — `.udf` üretimi yalnız `udf-cli` (`npx -y udf-cli@latest html2udf`) ile yapılır, zip/`content.xml` elle kurulmaz, `md2udf` ASLA kullanılmaz (bkz. `oa-dilekce/references/uyap-belge-formatlari.md` — Yargı Pro `udf_tiff_pdf_guide` rehberinin ailedeki operasyonel klonu). Bu ana hattın yerel okuması şüpheliyse (OCR-BOŞ damgalı evrak, şüpheli çok-sayfalı TIFF kaynaklı UDF) rehberin `udf2md` hattı (`oa-pipeline/scripts/udf_metin.py`) İKİNCİL/YEDEK bir doğrulama olarak kullanılabilir — sessiz atlama yasağı burada da geçerlidir.

Bağımlılık (Windows-dostu, binary'siz): `pip install pymupdf pillow`. OCR için ayrıca Tesseract + `tur` dil paketi; yoksa metin PDF/UDF/DOCX yine işlenir, taranmışlar "YÜKLENEMEDİ ⚠" damgasıyla künyeye yazılır (sessiz atlama yok).

## Çıktı sözleşmesi (`_oa/metin/`)
```
00-INDEX.md          → parça ÖNCE bunu okur: evrak tablosu (no, ad, tarih, yöntem, ⚠, 🔴, tür~, karakter, harita, dosya)
00-kunye.json        → makine-okur künye: her evrak için yöntem + teyit_gerek + karakter + kaynak + buyuk + harita + tur_tahmini + ocr_durum
NNN-<slug>.md        → belge-başına metin; başlıkta kaynak+sayfa+yöntem+tür~, gövdede içerik
NNN-<slug>.harita.json → yalnız BÜYÜK evrakta (>--buyuk-esik, varsayılan 40.000 kar.): sayfa/bölüm haritası (Gate A)
gorsel/<evrak>/pNN.png → yalnız OCR-BOŞ kalan sayfa(lar) için (Gate P0-9): görsel-inceleme
```
Sonraki parçalar ham evrağı DEĞİL `00-INDEX.md`'yi okur, sonra yalnız gereken `NNN-*.md`'ye iner; tam pasaj için o `.md` içinde grep'lenir. Büyük evrakta önce `.harita.json`'a bakılır (offset+başlık+karakter/token ile hangi sayfa/bölümün arandığı bulunur), sonra `.md`'ye o offset'ten girilir — tüm gövdeyi baştan okumak GEREKMEZ. Orijinal PDF yalnızca imza/mühür/kroki gibi görüntünün esas olduğu ya da ⚠ künye teyidi gereken durumda açılır.

**Gate A (sayfa/bölüm haritası):** karakter (anlamlı) eşiği aşan her evrak için md YANINA deterministik, KAYIPSIZ bir harita üretilir — özetleme DEĞİL, mevcut `<!-- --- sayfa N --- -->` ayracından (varsa) türetilen saf yapısal bölme (offset + ilk-satır-başlık + karakter/token). Ayraç yoksa (udf/docx/duz-metin gibi) tüm gövde tek 'bölüm' sayılır. `00-INDEX.md`'de 'büyük' özet sayacı + harita linki. **v1.7.1 (Gate A dirilişi):** önbellek-HIT kayıtları da bu geçitten geçer — `buyuk`/`buyuk_esik` her künyede, eksik `.harita.json` üretilmiş md'den byte-özdeş geri üretilir; eski (v1.6 öncesi) korpus kendini onarır.

**Gate C (mekanik tür~ tahmini):** dosya adından (İÇERİK OKUMADAN) tebligat/karar/dilekce/bilirkişi/sicil/bilanço vb. bir tür TAHMİN edilir; künyede `tur_tahmini`, INDEX'te daima "<tür> (tahmini)" damgasıyla — advisory, kesinlik DEĞİLDİR; eşleşme yoksa `null` (uydurulmuş varsayılan yasak).

**OCR-NÖBETÇİSİ (P0-9 — saha kanıtı: sessizce boş kalan OCR evrakları, ikisi müvekkil delili):** her OCR sayfası ① boş-eşik (sayfa başına <50 anlamlı karakter) + çöp-skor (alfasayısal oran/tek-karakter kelime oranı) ile denetlenir → ② yetersizse DPI yükselt/PSM değiştir/yönelim çevir sırasıyla DETERMİNİSTİK yeniden denenir → ③ hâlâ çökükse **yalnız o sayfa(lar) için** (hedefli — tüm evrak/tüm evraklar DEĞİL) `_oa/metin/gorsel/<evrak>/pNN.png` görselleri yazılır; künyede `ocr_durum` "OCR-BOŞ → GÖRSEL İNCELEME GEREK" (YÜKLENEMEDİ DEĞİL, işlendi de DEĞİL — üçüncü bir sınıf), `ocr_bos_sayfalar`, `gorsel_klasor`. `00-INDEX.md`'de 🔴 sütunu + özet sayacı (`ocr_bos_evrak`) + ayrı bir "OCR-BOŞ" bölümü; `_oa/DURUM.md` de aynı kayıtları görünür kılar. Sağlıklı evrakta HİÇ görsel üretilmez (dünkü israfın tekrarı yasak).

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
5. **M3-0 — DOĞUM-ANI KALICILIK:** bu adımdan sonra `oa-pipeline/scripts/tam_tur.py --senkron --kok .` çalıştırılır — `_oa/analiz/dosya-analiz.md`'nin MANİFEST bölümü (0. Künye) az önce üretilen `00-kunye.json`'dan deterministik doldurulur (tek sahip `tam_tur.py`dir; bu script dosya-analiz.md'ye yazmaz).

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
Tam günlük `references/degisiklik-gunlugu.md`'dedir. Güncel sürüm: **v3.26** (parça girişi v1.0; aile metodoloji sürümüne hizalandı).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

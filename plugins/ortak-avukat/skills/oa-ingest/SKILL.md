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
python scripts/oa_ingest.py .                          # bulunduğun klasör AÇIKÇA '.' (B-25: argümansız koşu REDDEDİLİR)
python scripts/oa_ingest.py "<klasor>" --ocr auto|zorla|kapali
python scripts/oa_ingest.py "<klasor>" --dil tur       # OCR dil paketi; yoksa 'OCR YAPILAMADI' damgası (aşağıda)
python scripts/oa_ingest.py "<klasor>" --yeniden       # önbelleği yok say, hepsini yeniden çıkar
python scripts/oa_ingest.py "<klasor>" --isci 8        # açık paralellik (0=oto varsayılan, 1=seri)
python scripts/oa_ingest.py "<klasor>" --onbakis 5      # P1-9(a): MEŞRU HIZLI KANAL, bkz. aşağı
```

**`--onbakis N` (P1-9a — meşru hızlı kanal, AYRI artefakt):** yalnız ilk N evrağı (`--onbakis-secim REGEX` ile önceliklendirilebilir) işler ve **ana hatta HİÇ karışmayan** `_oa/metin-onbakis/` dizinine yazar (`00-kunye.onbakis.json` + `00-INDEX.onbakis.md`); ana `_oa/metin/00-kunye.json`/`00-INDEX.md`/önbelleğe **tek bayt dokunmaz** — bayraksız TAM koşu byte-özdeş kalır. Çıkış kodu **4** (kısmi-tamam — "ONBAKIS: N/M — TAM DEĞİL"). Bu artefakt pipeline'ı **hiçbir adımda** yetkilendirmez: `pipeline_kayit.py`'nin İNGEST-ÖNCE kapısı yalnız `_oa/metin/00-kunye.json`'a (TAM koşu) bakar, `--onbakis` çıktısı bu dosyayı üretmediği için adım 1+ hâlâ blokludur — "TAM DEĞİL" damgası ayrı dosya adının kendisinde içkindir. `--onbakis` yalnız hızlı bir ilk-bakış/triyaj aracıdır; gerçek analiz için **--onbakis'siz tam koşu şarttır**.

Çıkarım yolları (model kurmaz, script çıkarır): metin PDF→**PyMuPDF** (bedava, kayıpsız) · taranmış PDF→render+**OCR** (⚠) · UDF→content.xml (bedava) · EYP/.zip→aç→içindeki PDF'i aynı hatta ver · TIFF/JPG/PNG→OCR (çok sayfa, ⚠) · DOCX→document.xml (bedava). Bir PDF'in "metin mi tarama mı" olduğu ELLE değil ÖLÇÜMLE (sayfa başına anlamlı karakter eşiği) belirlenir — "gördüm" beyanı değil, ölçüm.

**UDF OKUMA — YAPISI KORUNARAK (v0.5.15).** `.udf` artık düz metne indirgenmez: `scripts/udf_md.py` tabloları **tablo**, listeleri **liste**, üst/alt bilgiyi ayrı blok, gömülü görselleri ayrı dosya olarak çıkarır; CDATA'nın TAMAMEN DIŞINDA duran UYAP veri kayıtlarını (makbuz/reddiyat) `## EK` bölümüne taşır ve UYAP'ın kendi etiketlediği künye alanlarını (`mahkemeAdi`, `dosyaNo`, `kararNo`…) künyeye **`kunye_kaynak: udf-alan`** provenansıyla yazar — bunlar regex tahmini DEĞİL kaynak beyanıdır. Tamamen **yerel**: ağ, `npx`, oturum GEREKMEZ (stdlib). Ölçüm (798 gerçek evrak): görünür karakter kaybı **0/6.403.940**, tablo geometrisi XML gerçeğine karşı **739/739**, ~4 ms/dosya, salt-okuma ihlali **0/798**. *Dürüst sınır:* kayıpsızlık **görünür metin** içindir; birebir boşluk sadakati yoktur (hücre içi satır sonu → hücre ayracı). Bu ANA HAT **OKUMA**dır — UDF **YAZMA** yalnız `html2udf` ile yapılır ve o kural DEĞİŞMEDİ. Sessiz geçiş yok: gap/örtüşme, birleşik hücre ve uzantı yalanı künyede **damgalanır**. Determinizm: aynı girdi + aynı sürüm → bayt-özdeş; `icerik_sha256` renderer'dan bağımsızdır ve sürümler arası sabit kalmalıdır (künye/kapsam denetimi `--kunye` ile stderr'e basılır; `icerik_sha256` testlerle kilitlidir — `--denetle` diye bir alt komut YOKTUR).

Bağımlılık (Windows-dostu, binary'siz): `pip install pymupdf pillow`. OCR için ayrıca Tesseract + `tur` dil paketi; ikili yoksa metin PDF/UDF/DOCX yine işlenir, taranmışlar "YÜKLENEMEDİ ⚠" damgasıyla künyeye yazılır (sessiz atlama yok). PATH dışı kurulum: `OA_TESSERACT_YOL=<tesseract yolu>`.

**OCR ARAÇ HATASI DAMGASI (v0.5.16/E — P0-2/B-1/B-8; saha dersi: Linux'ta tesseract kurulu ama `tur.traineddata` yokken bütün taramalar "OCR-BOŞ → görsel incele" diye damgalanıp yüzlerce PNG yazılıyordu — ortam hatası evrak özelliği sanılıyordu):** Tesseract `rc != 0` döner ya da stderr'de `Error opening data file` / `Failed loading language` / `Tesseract couldn't load any languages` görülürse bu **boş sayfa DEĞİL, araç hatasıdır**. Evrak `OCR-BOŞ` almaz; ayrı damga alır: **"OCR YAPILAMADI — dil paketi/araç hatası (ortam hatası, evrak özelliği DEĞİL)"**, künyede `ocr_durum: "arac-hatasi"`, `yontem: OCR-ARAC-HATA`, üst düzeyde `ocr_arac_hatasi` sayacı (`ocr_bos_evrak` bunları SAYMAZ). Retry zinciri (DPI/PSM/yönelim) ÇALIŞMAZ, sonraki sayfa denenmez, `gorsel/` altına PNG YAZILMAZ; `00-INDEX.md`'de ayrı **"🔴 OCR YAPILAMADI (ortam hatası)"** bölümü + kurulum önerisi (`tur.traineddata`: UB-Mannheim / `apt tesseract-ocr-tur`). `main` başında `tesseract --list-langs` ile `--dil` paketi ÖN-KONTROL edilir: paket yoksa **tek seferlik görünür UYARI** ve OCR gerektiren tüm evraklar tesseract hiç çağrılmadan bu damgayı alır (sayfa başına deneme israfı yok; paralel işçi yolunda da aynı — karar `opts` ile taşınır); metin PDF/UDF/DOCX yine işlenir. Araç hatası önbelleğe yazılmaz: paket kurulup script yeniden koşunca aynı evraklar yeniden denenir. Okuyan parça için kural: `arac-hatasi` damgalı evrak **okunmamıştır** — "görsel incele" değil, "ortamı düzelt, yeniden koş" demektir; bu damgayla analiz "evrak eksik" sayılır (sayım denetimi gibi).

## Çıktı sözleşmesi (`_oa/metin/`)
```
00-INDEX.md          → parça ÖNCE bunu okur: evrak tablosu (no, ad, tarih, yöntem, ⚠, 🔴, tür~, karakter, harita, dosya)
00-kunye.json        → makine-okur künye: her evrak için yöntem + teyit_gerek + karakter + kaynak + buyuk + harita + tur_tahmini + ocr_durum (null | "OCR-BOŞ → …" | "arac-hatasi"); üst düzeyde ocr_bos_evrak + ocr_arac_hatasi sayaçları
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
6. **KRİTİK EVRAK → SÜRE ADAYI (v0.5.16/E — P1-10/A-4; usul esasa üstündür, süre telafisiz tek hatadır):** ingest biter bitmez `python oa-pipeline/scripts/okuma_kapisi.py --kok . --sure-adaylari` koşulur. Script künye/INDEX'teki evraklar arasında **tebligat / tebliğ mazbatası / ara karar / tensip / bilirkişi raporu / gerekçeli karar / ödeme emri / ihbarname** sınıfındakileri "SÜRE ADAYI" işaretler (künyede `tur_tahmini` yoksa dosya adı + md'nin ilk 600 karakterinden advisory `tur_tahmin` üretir), her adayın `.md` metninden `dd.mm.yyyy`/`dd/mm/yyyy` tarihleri **tebliğ | tebellüğ | karar tarihi | düzenleme tarihi** komşuluğu (±80 karakter) ile tarih adayı olarak çıkarır, stdout tablo + `_oa/cikti/00-sure-adaylari.json` (`{evrak, sinif, tarih_adaylari[], oneri_kural, not}`) yazar ve oa-sure kataloğundan aday kural anahtarı önerir (normlar Mevzuat MCP teyitli, 2026-09-06: HMK m.345, m.281; CMK m.273; İYUK m.7, m.45; İİK m.62; 6183 m.58). **Script `sure-flag` YAZMAZ** — yalnız `hesapla_sure.py --kural … --teblig … --flagsiz` (hesap advisory; `--flagsiz` olmadan hesapla_sure `_oa` varsa son günü sureler.json'a OTOMATİK yazar — E4a — ve onay kapısı aşılır) → `oa_hafiza.py sure-flag --tarih <SON GÜN> … (avukat onayıyla)` komut satırını ÖNERİR; kuralı, başlangıcı (tebliğ/tefhim), adli tatili ve son günü seçmek muhakemedir (`oa-sure` + avukat). OCR'lı (⚠) evrakta tarih orijinalden teyit edilmeden flag'e yazılmaz. Aday listesi boşsa bu "süre yok" demek DEĞİLDİR.

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

# OCR Uygulama Planı — oa-ingest (v0.5.18 adayı)

> Durum: **UYGULAMA AŞAMASINDA** · dal `guncelleme/0.5.18` · yayın/commit/push avukat
> onayına bağlıdır. Ölçüt tek cümle: **OCR hatası süre, künye ve tutar hatasıdır; hiçbir
> taranmış sayfa sessizce kaybolmamalı, hiçbir OCR çıktısı kesinmiş gibi sunulmamalı.**
> Bulut OCR KULLANILMAZ (Av.K. m.36, KVKK); her şey yerel CPU'da koşar.

## 1. Mevcut mimari (kod üzerinden ölçüldü, 2026-10-05)

| Parça | Davranış | Konum |
|---|---|---|
| `pdf_isle` | Metin katmanı `get_text("text")`; **belge ortalaması** sayfa başına < 40 anlamlı karakterse TÜM sayfalar render + OCR | `oa_ingest.py` |
| `goruntu_isle` | TIFF/JPG/PNG (çok kare) → Tesseract | `oa_ingest.py` |
| `ocr_png` | Tesseract alt süreci, **düz metin** (stdout); güven skoru YOK; `--psm` parametrik | `oa_ingest.py` |
| P0-9 OCR-NÖBETÇİSİ | sayfa başına boş-eşik (50) + çöp-skor; 4 adımlı deterministik retry (DPI/PSM/180°); kalmazsa `OCR-BOŞ → GÖRSEL İNCELEME GEREK` + PNG | `_ocr_sayfalari_isle` |
| v1.8 araç hatası | rc≠0 / stderr imzası → `OCR-ARAC-HATA` (ortam hatası, evrak özelliği değil) | `ocr_png`, `_tesseract_dil_var_mi` |
| Sözleşme | md başlığı (⚠ teyit, 🔴), künye (`yontem`, `teyit_gerek`, `ocr_durum`, `ocr_bos_sayfalar`, `gorsel_klasor`), INDEX, DURUM.md, `okuma_kapisi` süre adayı | — |

## 2. Bulgular

- **O-1 (YÜKSEK) — karma PDF'te sessiz kayıp.** Karar belge ortalamasıyla verildiği için 9
  metin sayfası + 1 taranmış sayfa (ör. araya eklenmiş tebliğ mazbatası) ortalamayı geçer, OCR
  hiç yapılmaz; taranmış sayfa UYARISIZ boş kalır. Süre o sayfadan başlayabilir.
- **O-2 (ORTA) — güven yok.** OCR metni bütün olarak "⚠ teyit" damgalı; hangi sayfanın
  güvensiz olduğu bilinmez, avukat teyidi önceliklendiremez.
- **O-3 (YÜKSEK) — kritik alan karışıklığı.** O/0, I/l/1, B/8, S/5, Z/2, G/6 karışıklığı
  tarih, esas/karar no, tutar, IBAN, TCKN'de sonucu değiştirir; hiçbir işaretleme yok.
- **O-4 (ORTA) — tek motor.** Zor taramada (düşük çözünürlük, eğik, tablo) ikinci motor yok.
- **O-5 (ORTA) — el yazısı.** Türkçe el yazısını okuyan doğrulanmış yerel motor yok; el
  yazısı ya çöp ya OCR-BOŞ olur, "el yazısı" diye sınıflanmaz.
- **O-6 (ORTA) — sayfa izlenebilirliği.** Hangi sayfanın metin katmanından, hangisinin OCR'dan
  geldiği künyede yok.

## 3. Tasarım kararları

1. **Sayfa düzeyi yönlendirme (O-1, O-6).** Her sayfa ayrı karar alır: metin katmanı anlamlı
   (≥ 40) → `metin` (bozuk katman → `ocr`; görsel üstündeki görünmez OCR katmanı → `harici-ocr`,
   teyit); değilse OCR için KANIT aranır: raster görsel/maske kapsaması ≥ %30 (`get_bboxlog`) ya da
   ≥ 200 çizim yolu → `ocr`; kanıt yoksa `kisa` (imza/kapak — metniyle kalır, OCR yok). Tümü metin →
   `pdf-metin(PyMuPDF)` (çıktı **BAYT BAYT aynı**); tümü taranmış → `OCR(pdf-tarama)` (mevcut);
   karışık → yeni `pdf-karma` (⚠ teyit). Künyeye `sayfa_kaynaklari` YALNIZ OCR'lı/harici sayfa
   varken eklenir. `--ocr kapali` iken karma sayfa sessiz kalmaz: not + teyit.
2. **Güven (O-2).** Tesseract tek geçişte `txt` + `tsv` yapılandırmasıyla koşar: metin
   değişmez (aynı motor, aynı ayar — deneyle doğrulanır), kelime güvenleri TSV'den okunur;
   sayfa güveni = geçerli kelime güvenlerinin ortalaması. Güven ölçülemezse **null** (uydurma
   yok). Künye `ocr_guven` (sayfa → değer), md başlığında en düşük sayfa.
3. **Kritik alan teyidi (O-3).** OCR'lı metinde tarih, esas/karar/dosya no, kanun no, TCKN,
   IBAN, tutar, telefon desenleri; sayısal bağlamda karışık harf ya da sağlama (TCKN algoritması,
   IBAN mod-97) tutmazsa `dogrulama_gerekli` listesi (sayfa, tür, ham değer, neden).
   **Metin ASLA düzeltilmez.** md başlığında 🔎 satırı; süre adayı tablosunda not.
4. **Motor yönlendirici (O-4).** `--ocr-motor tesseract|auto|paddle` (+ `OA_OCR_MOTOR`).
   Varsayılan `tesseract` (geri uyum). PaddleOCR OA'ya bağımlılık olarak GİRMEZ: ayrı
   yorumlayıcıda (`OA_PADDLE_PY`) alt süreç işçisi koşar; ağsız çalışır, model yoksa araç
   hatası → Tesseract'a düşer. `auto` (asimetrik, deterministik): Tesseract önce; yalnız P0-9
   kapısını geçemeyen sayfada Paddle İLK denemenin görüntüsüyle denenir; çıktısı yalnız aynı kapıyı
   ve Türkçe sık sözcük isabetini (≥ %5) geçerse alınır. Motorlar arası güven KIYASLANMAZ; kabul
   edilmiş Tesseract sayfası değiştirilmez. Künye `ocr_motor`: istenen motor, kullanılan motor
   başına sayfa aralığı, yedek nedenleri. Motor seçimi önbellek anahtarındadır.
5. **El yazısı (O-5).** Doğrulanmış Türkçe el yazısı motoru YOK → okuma iddiası yok.
   Sayfada mürekkep var ama OCR güveni çok düşük ya da OCR-BOŞ → `el_yazisi_inceleme: true`
   + sayfa listesi; görsel PNG (P0-9) zaten yazılır.
6. **Korunan sözleşmeler.** YÜKLENEMEDİ / OCR-BOŞ / OCR-ARAC-HATA damgaları, INDEX, DURUM.md,
   md başlıkları, `_oa` dizin sözleşmesi, seri == paralel bayt eşitliği, önbellek doktrini.
   Yeni alanlar yalnız ilgili durumda eklenir (temiz metin PDF/UDF/DOCX künyesi değişmez).

## 4. Değerlendirilen alternatifler

| Seçenek | Karar | Gerekçe |
|---|---|---|
| Bulut OCR (Google/Azure/Adobe) | **REDDEDİLDİ** | Meslek sırrı + KVKK; kullanıcı yasağı |
| EasyOCR | Reddedildi | PyTorch (~1 GB), CPU'da yavaş, ek kazanç doğrulanmadı |
| PaddleOCR 3.x (PP-OCRv5) | **Opsiyonel motor** | Yerel, CPU, Latin/Türkçe modeli; ağır → ayrı yorumlayıcı |
| OCRmyPDF | Reddedildi | Tesseract'ın üstüne ek katman; mevcut hat zaten render+OCR yapıyor |
| Kraken / Calamari / TrOCR (el yazısı) | Kapsam dışı | Türkçe el yazısı modeli doğrulanmadı → görsel inceleme |

## 5. Deney (önce deney, sonra iddia)

- Resmî belge (paddlepaddle.org.cn, Windows pip): Python 3.9–3.13, 64-bit, MKL; **noavx
  paketi yok** (AVX şart). Bu makine: AMD A8-4500M — AVX VAR, AVX2 YOK, 7,4 GB RAM.
- Deney sonucu: §8'e yazılır (kurulum, model indirme, örnek sayfada doğruluk/süre). Hedef
  makine (Core Ultra 7 255H) bu oturumda erişilebilir değil → **orada doğrulanmadı**.

## 6. Test planı (önce test)

Sentetik evrak testte üretilir (gerçek dava verisi yok): karma PDF (metin + taranmış sayfa),
boş kapak sayfası, düşük güvenli sayfa, kritik alan karışıklığı (O/0, I/1, B/8, S/5; geçersiz
TCKN/IBAN), sahte Paddle işçisi (`OA_PADDLE_PY` ile stub — tesseract sahtesiyle aynı desen),
yedeğe düşme, el yazısı şüphesi, regresyon (metin PDF/UDF/DOCX bayt-özdeş, seri == paralel).
Kıyaslama: `tools/ocr_kiyas.py` (sentetik sayfalarda motor başına süre + karakter doğruluğu).

## 7. Kalite kapısı

Hedefli testler yeşil → tam süit (sayı tek kaynakta: `tests/README.md` OA-SUIT-SAYISI) yeşil →
`aile_dogrula` temiz → kanca süresi ölçümü
(PERFORMANS-STATUS kuralı) → avukata rapor. FAIL/BLOCKED varken commit/push YOK.

## 8. Bağımsız karşı-tez incelemesi (Fable 5.1, 2026-10-05) ve sonuç

İnceleme, planı ve `oa_ingest.py`'yi salt okuyarak yapıldı. Kabul edilen düzeltmeler:

- **`bos` sınıfı yeni sessiz kayıp kapısı olabilirdi** (vektöre dönmüş yazı, Form XObject'teki
  JBIG2 maskesi `get_image_info`'da görünmeyebilir). → Görsel kapsaması `get_bboxlog` ile
  (görsel + görsel maskesi) ölçülür; ayrıca çizim yolu sayısı kanıt sayılır; kanıtsız kısa sayfa
  `kisa` adıyla METNİYLE kalır (boş sayılmaz).
- **Harici OCR katmanı kesin metin gibi sunuluyordu.** → `harici-ocr` + teyit (tek kaynak ölçüt).
- **Bozuk CID/ToUnicode katmanı ≥ 40 karakter "metin" sayılıyordu.** → bozuk oranı > %20 ise OCR.
- **`pdf-karma` yalnız fiilen OCR'lanan sayfa varken**; kısa ama kanıtsız sayfa karmaya kaydırmaz
  (her UYAP kararının imza sayfası alarm üretmesin).
- **Önbellek**: yönlendirme sürümü işaretsiz kayıt yeniden taranır (`cikarim`); motor seçimi anahtarda.
- **txt+tsv**: çıktı tabanı DOSYA (stdout'ta iki çıktı karışır); `stdout == txt` eşitliği testle kilitli.
- **Güven**: yalnız ortalama yetmez → düşük güvenli kelime ORANI + BÖLGELER; md'de bant.
- **Kritik alan**: izinli rakam sınıfı (sıkı desen harfli değeri hiç yakalamaz); rakam→rakam hatası
  yakalanamaz → "doğrulandı" durumu YOK; asgari küme (çıpalı tarih, esas/karar no, TCKN, IBAN);
  tutar/telefon/kanun no ERTELENDİ (alarm yorgunluğu).
- **Paddle**: ayrı yorumlayıcı doğru; ağsızlık KANITLANMALI (model yoksa ret); `auto` kuralı
  asimetrik (motorlar arası güven kıyası REDDEDİLDİ); cpu_threads=1, MKL-DNN kapalı.
- **El yazısı**: "el yazısı" etiketi dürüst değil (mühür/imza/faks aynı sinyali verir) → düşük
  güvenli bölge listesi + görsel inceleme.
- **Zaman aşımı**: tek sayfanın aşımı evrakı boşaltıyordu → sayfa başına.

Reddedilen: motorlar arası güven/karakter sayısı kıyasıyla seçim; görsel kapsamasının tek başına
`bos` ölçütü olması; herhangi bir "doğrulandı" durumu; yalnız ortalama güven.

## 9. Deney ve uygulama kayıtları

- **Tesseract txt+tsv (2026-10-05, Tesseract 5.4.0 + tur, Windows):** sentetik sayfada dosya `txt`
  ile stdout arasında tek fark satır sonu (CRLF/LF); evrensel satır sonuyla metin AYNI. TSV kelime
  güvenleri gerçek ve ayırt edici (bozuk glifli kelimeler %23–57, temiz kelimeler %90+).
- **PaddleOCR kurulumu (2026-10-05, bu makine: AMD A8-4500M, AVX var/AVX2 yok, 7,4 GB):** yalıtılmış
  `paddle-deney` sanal ortamına PyPI'den paddlepaddle 3.3.0 + paddleocr 3.7.0 (paddlex 3.7.2)
  KURULDU (714 MB). PaddleOCR 3.7 Türkçeyi (Latin ailesi) varsayılan PP-OCRv6 medium det/rec
  modelleriyle işler. Çıkarım (model indirme + örnek sayfa) deneyi: §10.
- **Uygulama:** sayfa yönlendirme, harici OCR katmanı, bozuk katman, txt+tsv güveni, kritik alan,
  sayfa başına zaman aşımı, motor yönlendiricisi (`paddle_isci.py`, sahte işçiyle sınandı) —
  `tests/test_v0518_ocr.py`.

## 10. PaddleOCR çıkarım deneyi

**Koşu (2026-10-06, eski ve ısınma sorunlu bir dizüstü bilgisayar — yalnız CPU, ısı korumalı başlangıç):** PaddleOCR 3.7 / paddlepaddle 3.3.0 ayrı sanal ortamda; modeller `PP-OCRv6_medium_det` ve `PP-OCRv6_medium_rec` resmî Hugging Face deposundan SABİT bir commit'ten indirildi (avukat onayıyla) ve SHA-256 / git-blob özetleri yayımlanan değerlerle doğrulandı (6/6). Çıkarım AĞSIZ (yerel model dizini), `cpu_threads=1`, MKL-DNN kapalı (determinizm). Girdi: 5 sentetik sayfa (Türkçe karakterli 6 satır: temiz, bulanık, gürültülü, eğik, düşük DPI); gerçek dava verisi YOK. Doğruluk = beklenen metinle karakter dizisi benzerliği (difflib).

- Tesseract (`tur`, psm 3): sayfa başına 1,4-1,7 sn · doğruluk temiz 0,989 · bulanık 0,986 · gürültülü 0,826 · eğik 0,986 · düşük DPI 0,986.
- PaddleOCR: model yükleme 30,2 sn · tepe bellek 1.213 MB · sayfa başına 104-128 sn · doğruluk temiz 0,989 · bulanık 0,989 · gürültülü **0,687** · eğik 0,989 · düşük DPI 0,989. Türkçe İ/ı ayrımında hata gözlendi ("ASLİYE" → "ASLIYE", "MAHKEMESİ" → "MAHKEMESi").

**Sonuç:** bu donanımda Paddle'ı varsayılan motor yapmak için gerekçe YOK — temiz/bulanık/eğik/düşük DPI'da Tesseract ile aynı, gürültülüde daha kötü, ~70 kat yavaş. Varsayılan `tesseract` kalır; `--ocr-motor auto` Paddle'ı yalnız P0-9 kapısını geçemeyen sayfada dener ve ölçütle (P0-9 + Türkçe isabet) kabul eder; `paddle` isteğe bağlıdır. Sınır: sentetik ve az sayıda sayfa; gerçek taranmış evrakta, el yazısında ve yeni donanımda (çok çekirdek, MKL-DNN) sonuç farklı olabilir — yeni cihazda yeniden ölçülmeli.

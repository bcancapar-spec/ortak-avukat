# Testler ve saha deneyleri — laboratuvar ve saha, tek belgede

> Bu belge iki okuyucu için yazıldı: vitrine bakan hukukçu ("bu sistem nasıl
> sınanıyor, kırmızı ne demek?") ve depoyu okuyan dil modeli ("süit nerede, kural
> ne?"). Sayı ve hüküm içermez: saha deneyleri ad, numara, süre ve token sayısı
> olmadan anlatılır (avukat kararı, 2026-10-17; anayasa m.7). Tarihli karneler
> `docs/arsiv/` altında olduğu gibi durur; oradaki etiketler o günün kaydıdır.

## 1. Neden bu belge

Bu deponun en ağır kusurlarının hiçbirini yazılım testi bulmadı; hepsini saha
buldu. Sonra her saha dersi bir teste dönüştü ve bir daha geri gelemedi. Bu
belge o döngüyü anlatır: önce laboratuvar (mekanik süit), sonra saha (gerçek
dosyada müdahalesiz koşu), sonra karne, sonra reçete. Süitin güncel büyüklüğü
burada yazmaz; tek kaynağı [tests/README.md](../tests/README.md)'deki
`OA-SUIT-SAYISI` işaretçisidir ve bir test onu her koşuda gerçek toplamayla
karşılaştırır.

## 2. Mekanik test altyapısı

Her sürüm, sahada bulunan her kusuru önce bir teste çevirir. Süit saf `pytest`
ile koşar, ağsızdır ve her test kendi geçici klasöründe kurgu bir dava kökü
kurar. Tematik anatomi:

| Tema | Neyi güvence altına alır |
|---|---|
| Sürüm-reçetesi paketleri (`test_vXYZ_*.py`) | Bir saha karnesinden doğan onarım paketinin kendi testleri; sahada bulunan her kusur burada nöbettedir |
| UDF hattı | Üretilen .udf UYAP'ta açılır mı: stil iskeleti, kenar ölçüleri, round-trip okuma, elle-üretim yasağı, atomik mühür |
| Kanca katmanı | Altı kanalın ateşleme koşulları, kök çözümü, dedup, nabız, enjeksiyon içerikleri, sunum kilidi |
| Künye / içtihat | Atıf resmî kaynağa çözülüyor mu, tam-metin ve damga şartı, muhakeme kaydı, kaynak adresi beyaz listede mi, yetim alıntı |
| Pipeline / defter | Adım zinciri, kanıt şartı, append-only defter bütünlüğü, oturum damgası |
| Teslim zinciri / makbuz | Kapıların sırası, RED ve yeşil makbuz garantisi, filo tazeliği, 40-UYAP kopyaları |
| Hafıza / devir | `_oa` iskeleti, oturum devri, çalışma hafızasının senkronu |
| Vakıa / antitez / kıyas | Kronoloji-delil eşlemesi, cephe bütünlüğü, unsur eşleşme denetimi |
| Süre hesabı | Usul ve maddi süreler, adli tatil ayrımı, son-gün hesabı, başlangıç kapısı |
| Evrak alımı / OCR / belge güvenliği | Evrak sayımı, metin çıkarımı, OCR damgası, gizli katman damgası, Excel gizli katmanı |
| Aile / sürüm bütünlüğü | Manifest-sürüm-kanca tutarlılığı, parmak izi, "N skill" sayımı, vitrin sürüm damgaları |
| Usul / kontrol · graf · kit güvenliği · gizlilik · şekil · sözleşme | Usul matrisi, illiyet grafının yapısal sağlığı, kilitli çekirdek, Layer 0 desenleri, şekil standardı, kloz kapsamı |
| Vitrin / depo hijyeni | Motor kapsam defteri, mutlak yerel yol yasağı, CI etiket tetiği ve OCR bacağı, bağlantı kapısı, kaynak hijyeni, kanal-bağımsız metin |

### Sentetik veri

Avukatın tanımı: **"Sentetik veri, gerçek verinin kişisel verilerden arındırılmış
hâlidir."** Depoda iki katman vardır:

- **Test fikstürleri tamamen kurgudur.** Dosya numaraları, kişi adları ve yollar
  uydurmadır ("2024/123 Esas" gibi). Gerçek bir dava verisi, kişi adı ya da yerel
  yol test koduna giremez; bu yasak mekaniktir (`tests/test_v0514_vitrin.py`
  mutlak yol kapısı) ve anayasa m.7'nin test kodundaki karşılığıdır.
- **Saha dersleri anonimleştirilmiş örüntülerdir.** Gerçek dosyadan öğrenilen her
  şey, kişi ve dosya kimliğinden arındırılıp "olay tipi + norm + örüntü" olarak
  skill metnine ve bu belgeye girer. Ders kalır, kimlik kalmaz.

Üretim kodu ile test kodu arasındaki sınır da kesindir: test altyapısı eklentinin
hiçbir kapısını gevşetmez; ağ gerektiren bir aracın yokluğu testi atlatır ama
atlama her koşuda gerekçesiyle görünür.

## 3. Kırmızı test ne demektir

"Kırmızı" bir testin düşmesidir. Bu depoda üç ayrı anlamı vardır ve üçü
karıştırılmaz:

1. **TDD'de önce kırmızı — kanıt.** Bir kusur onarılmadan önce, kusuru yeniden
   üreten test yazılır ve düşerken görülür. Düşmeyen bir test kusuru yakalayamıyor
   demektir; o yüzden "koşmadan geçti demek" yasaktır. Onarım yazılınca aynı test
   yeşile döner ve süitte kalır: o kusur bir daha sessizce geri gelemez.
2. **CI'da kırmızı — kapı kapalı.** Her push, GitHub Actions üzerinde Windows ve
   Ubuntu'da üç Python sürümüyle tam süiti, ayrı işlerde aile yapı denetimini,
   OCR bacağını ve kaynak hijyeni kapısını koşar. Kural serttir: CI yeşermeden
   sürüm etiketi atılamaz. Kırmızı CI, "bu sürüm yayınlanamaz" demektir; bir
   dönem uzun süre kırmızı kalan ve kimsenin fark etmediği CI, bu kuralın
   dersidir.
3. **Görünür atlama kırmızı DEĞİLDİR.** Ağ ya da oturum gerektiren bir araç (ör.
   resmî UDF yazıcısının oturumu) o makinede yoksa, ona bağlı testler gerekçesiyle
   atlanır ve pytest özetinde adıyla listelenir. Sessiz atlama yasaktır: bir
   testin "var ama hiç koşmuyor" hâlde durması kırmızıdan kötüdür, çünkü kapı
   varmış gibi görünür.

**Çözüm nasıl yapılır.** Kırmızı bir testte düzeltilen şey koddur, test değil.
Test susturulmaz, karantinaya alınmaz, `skip` ile geçiştirilmez. İki istisna
vardır ve ikisi de yazılı iz bırakır: (a) davranış bilinçli olarak değiştiyse
(ör. teyit kanalının resmî kaynak adresini zorunlu kılması) eski test yeni
sözleşmeye taşınır, gerekçesi testin docstring'ine ve değişiklik günlüğüne
yazılır; (b) kırmızının sebebi ortamsa (eksik araç, eksik kütüphane) test
"görünür atlama" sözleşmesine alınır, kapı gevşetilmez.

**Kırmızıyı nerede görürsünüz.** Yerelde `python -m pytest tests -q -n auto -rsfE`
çıktısının sonunda: düşen her test adıyla, atlanan her test gerekçesiyle
listelenir. GitHub'da depo sayfasının üstündeki CI rozeti ve Actions sekmesi.
Kırmızı görürseniz dosyayı değil, çıktıdaki ilk kırmızının gerekçesini okuyun;
çoğu zaman ya ortam eksiği ya da bilinçli bir sözleşme değişikliğidir ve ikisi de
metinde yazar.

## 4. Saha deneyleri — gerçek dosyada müdahalesiz koşu

Saha, son sınavdır. Protokol her koşuda aynıdır:

1. **Müdahalesiz gözlem.** Avukat gerçek bir derdest dosyanın klasöründe tek bir
   doğal prompt verir ve müdahale etmez. Ölçülen şey sistemin ne yaptığı değil,
   ne yapamadığıdır; koşu içinde onarım yasaktır, çökme bulgudur.
2. **Transkript adli analizi.** Koşu bitince oturumun tam dökümü satır satır
   okunur: hangi parça çağrıldı, hangisi çağrılmadı, model nerede beyanla yetindi.
3. **Artefakt denetimi.** Diskteki eserler (defter, kütük, makbuz, UDF) zaman
   damgalarıyla çaprazlanır. Kural: bir kapı ancak koşu penceresi içinde zaman
   damgalı bir eser bırakmış ve o eser aşağı akışta tüketilmişse ateşlemiştir;
   gerisi beyandır.
4. **Karne.** Her koşu için desen başına karne yazılır: ateşledi, ateşlemedi,
   yanlış ateşledi. Başarısızlıklar da yazılır.
5. **Karne → reçete.** Her karne bir sonraki sürümün reçetesidir. Sürüm zinciri
   birebir bu döngünün ürünüdür.

Üç deney sınıfı ayrı tutulur ve karıştırılmaz: **müdahalesiz** (tek prompt, sıfır
müdahale), **müdahaleli** (avukat koşu sırasında yönlendirme ya da mekanik
hatırlatma yazmak zorunda kaldı; karneye böyle yazılır), **çok oturumlu** (aynı
klasörde birden çok paralel oturum). Mekanik tamlık ("zincir fiziksel koştu mu")
ile içerik kabulü ("dilekçe avukatı tatmin etti mi") iki ayrı hükümdür.

### Belgeli koşular — anonim özet

Geliştirme zinciri gerçek derdest dosyalarda sınandı; bir kısmı sensörlü izleme
ve adli analizle uçtan uca belgelendi. Aşağıda dosya tipi ve çıkan ders anlatılır;
kimlik, etiket ve sayı yoktur.

- **Derdest istinaf dosyasında ek beyan (ilk tam koşu).** Tek doğal prompt'la
  teslim edilebilir bir dilekçe ve geçerli UDF çıktı; bayat araç kopyası ve
  bağlantı zinciri dersleri doğdu. Evrakı görüntü yerine metin olarak okumanın
  verimi burada ölçüldü.
- **Bakir klasörde müdahalesiz test.** Mekanizmalar sağlamdı ama çağrılmıyordu:
  "kapının gücü kodunda değil tetiğindedir" dersi; aktivasyon zinciri buradan
  çıktı.
- **Vergi davası.** Tetik boşlukları ve kanca katmanının sessiz ölümü (masaüstü
  uygulaması kancayı kabuksuz koşturuyordu) ölçüldü; sarmalayıcı deseni buradan
  doğdu.
- **Aile / mal rejimi dosyası.** Kanca katmanı ilk kez uçtan uca canlı ateşledi;
  çok kollu adli analizle elle-UDF engeli, makbuz garantisi ve mühür otomasyonu
  reçete oldu.
- **Bilirkişi raporuna itiraz.** Künye kapısı gerçek bir açığı yakaladı ve model
  dürüst davrandı; tek bir ayrıştırıcı yanlış-pozitifi yeşil makbuzu imkânsız
  kıldı. Mutlak triyaj (her karar baştan sona okunur) ve e-imza halkası buradan.
- **Banka / kefalet ikinci cevabı, çok klasörlü çapraz tarama.** Bayat araç kiti
  kök nedeni; ilk gerçek lehe/aleyhe triyajı; resmî araçla üretilen, yönetmelik
  ölçülerinde ilk tam-standart UDF.
- **Tasarrufun iptalinde ikinci cevap (devralmalı).** Uçtan uca zincir ve triyaj
  stratejiyi fiilen şekillendirdi; makbuz sonrası mühür dışı değişiklik ölçüldü ve
  atomik mühür ile filo tazeliği doğdu. Koşu müdahaleliydi ve karneye öyle yazıldı:
  karnenin ilk düzelttiği şey koşu sırasında yapılan kendi raporumuzdu.
- **Vergi / gümrük: ödeme emri ve ek tahakkuk, dilekçe ret sonrası yenileme.**
  Tek cümlelik prompt, sıfır müdahale, iki ayrı ürün; tam-metin kapısı dökümsüz
  atıfları reddetti ve model kararları çekip damgaladıktan sonra yeşil makbuz
  kesebildi. Zincir kendi düzeltmesiyle kırmızıdan yeşile döndü.
- **İdari yüksek yargıda soruşturma-izni itirazı, çok oturumlu, birden çok
  müvekkil.** Uygulamanın anlık-görüntü yolundan bulaşan bayat araç nesli
  adlandırıldı; tek seferlik onarımın yetmediği ölçüldü. Karantina, kilitli
  çekirdek, yönlü tazelik ve oturum damgası buradan.
- **İcra ve ceza dosyaları (son sürüm çizgisi).** Halüsinasyon kapısı (dört motor
  dilekçeden önce fiilen koşar), avukat onayının uydurulmaması, okunamayan evrak ve
  Excel tablolarının kaybolmaması, Layer 0 süzgecinin çağrı yerinde olması bu
  koşulardan çıktı.

Tam kayıtlar, ölçüm yöntemleri ve dakika dakika çizelgeler tarihli karnelerde
durur: [docs/arsiv/](arsiv/README.md). Oradaki saha etiketleri o günün kaydıdır
ve geriye dönük yazılmaz.

## 5. Dürüstlük — başarısızlıklar da yazılır

- Hiçbir kapı "bu dilekçe hukuken isabetli" demez; kapılar unsur, künye, biçim ve
  iz denetler. Hukuki isabet hükmü avukata aittir.
- Müdahaleli koşu müdahalesiz diye yazılmaz; her koşunun makbuzu kendi sınıfını
  taşır.
- Ham dersler saklanmaz: teslim hattının avukatın kendi makinesinde çökmesi, uzun
  süre kırmızı kalan CI, elle yazılmış defter, geçerli dilekçeyi kesen kapı —
  hepsi tarihiyle [STATUS.md](../STATUS.md) ve [CHANGELOG.md](../CHANGELOG.md)'de
  durur.
- Bir güvence "bir kez ölçüldü" ise öyle yazılır; tekrar ölçümü açık iş olarak
  listelenir.

## 6. Kayıtlar nerede

| Ne | Nerede |
|---|---|
| Süit büyüklüğü (tek kaynak) ve koşum tarifleri | [tests/README.md](../tests/README.md) |
| Sürüm başına ne değişti, hangi saha kanıtıyla | [CHANGELOG.md](../CHANGELOG.md) |
| Tarihli saha karneleri, ölçümler, denetim infazları | [docs/arsiv/](arsiv/README.md) |
| Kanca gecikmesi ölçüm defteri | [docs/PERFORMANS-STATUS.md](PERFORMANS-STATUS.md) |
| Bağımsız denetimler ve heyet koşumları | [docs/DENETIM-2026-10-15.md](DENETIM-2026-10-15.md) · [docs/heyet/](heyet/README.md) |
| Terimlerin avukat diliyle karşılığı | [SOZLUK.md](../SOZLUK.md) |

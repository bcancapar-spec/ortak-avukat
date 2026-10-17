# Saha bölümü — CHANGELOG üstünden taşınan metin (2026-10-12 → 2026-10-17)

> Bu dosya, 2026-10-12'de vitrinden (README) CHANGELOG'un üstüne taşınan "Saha sonuçları" ve
> "Saha deneyleri — testler nasıl yapıldı" bölümlerinin 2026-10-17'deki hâlini kelimesi kelimesine
> taşır (yalnız dosya bağlantıları bu dizine göre yeniden yazıldı). Avukat kararı (2026-10-17):
> canlı metin sayı, hüküm ve saha etiketi içermez; anonim anlatım
> [docs/TESTLER-VE-SAHA-DENEYLERI.md](../TESTLER-VE-SAHA-DENEYLERI.md)'dedir. Buradaki sayılar ve
> etiketler o günün kaydıdır ve geriye dönük yazılmaz.

---

## Saha sonuçları

*(2026-10-12'de vitrinden (README) kelimesi kelimesine taşındı. Avukat kararı: saha sonucu
ve benzeri ayrıntılar sürüm defterinde durur; vitrinde hukukçular için sözlük kalır.)*

> ⚖️ **Gerçek davalarda test edildi.Geliştirilmeye devam ediliyor.** Bu sistem sentetik örneklerle değil,
> derdest gerçek dosyalarla sahada sınanıyor: v0.0.1'den v0.5.16'ya gelen
> geliştirme zinciri **149 gerçek davada** test edildi (v0.5.17–0.5.18 denetim,
> güvenlik ve evrak-okuma sürümleridir; belgeli saha koşusu sayısı değişmedi —
> bkz. [Güncelleme notları](../../README.md#güncelleme-notları)); bunların **dokuzu**,
> sensörlü izleme + karne + adli analizle BELGELİ büyük saha koşusudur:
> (1) ~200 evraklık istinaf dosyasında ek beyan (ilk tam koşu), (2) 214
> evraklık bakir klasörde müdahalesiz test, (3) 447 sahası — vergi davası,
> (4) 372 sahası — aile/mal rejimi, (5) 346 sahası — bilirkişi ek raporuna
> itiraz, (6) 777 sahası — banka/kefalet ikinci cevap + 24 kök çapraz
> taraması, (7) 307 sahası — tasarrufun iptalinde ikinci cevap (devralmalı),
> (8) 923 sahası — vergi/gümrük, ödeme emri + ek tahakkuk (ilk organik yeşil
> makbuz), (9) 1865 sahası — idari yüksek yargıda soruşturma-izni itirazı
> (çok oturumlu, birden çok müvekkil). Ayrıntılar aşağıdaki tabloda ve karnelerdedir. Belgeli koşu sayımına yalnız sensörlü izlenen dosyalar alındı; ilk denemede sonuca ulaşan ama izlenmeyen dosyalar sayıma girmedi.
> İlk ölçüm: ~200 evraklık gerçek bir istinaf dosyası, **tek bir doğal-dil
> prompt'la**, 49 dakikada ve 45,6k token'la teslim edilebilir bir istinafa cevap
> dilekçesine ve geçerli UDF'e dönüştü. Aynı sınıf iş, eklenti öncesi aynı model ve
> eforla (Fable 5, max) yaklaşık 1,2M token tüketiyordu; fark ölçülmüştür, iddia
> değildir (ölçüm ve kayıp listesi: [SAHA-SONUCU.md](SAHA-SONUCU.md)). Evraklar
> [avukat-dosya-indirici](https://github.com/bcancapar-spec/avukat-dosya-indirici) ile PDF olarak indirilmiş, bu eklentiyle `.md`/`.json` biçimine otonom çevrilmiştir.
> Sayılar ve dürüst kayıp listesi: **[SAHA-SONUCU.md](SAHA-SONUCU.md)** · **[BASARI.md](BASARI.md)**. Dosya kimlikleri projenin anayasası m.7 gereği daima
> anonimdir. Hukuk erişilebilir olmalıdır — su ve nefes gibi.

## Saha deneyleri — testler nasıl yapıldı

Bu deponun en ağır kusurlarının **hiçbirini yazılım testi bulmadı — hepsini
saha buldu.** Bu yüzden test metodolojisinin merkezinde gerçek, derdest dosyalar
vardır. Protokol beş adımdır ve her koşuda aynıdır:

1. **Müdahalesiz gözlem ("stalker" protokolü):** avukat gerçek bir dava
   klasöründe tek prompt verir ve **müdahale etmez**; sistemin ne yaptığı değil
   ne yapamadığı ölçülür. Koşu-içi onarım yasaktır — çökme, bulgudur.
2. **Transkript adli analizi:** koşu bittikten sonra oturumun tam dökümü satır
   satır incelenir: hangi parça çağrıldı, hangisi çağrılmadı, model nerede
   beyanla yetindi.
3. **Artefakt denetimi:** diskteki eserler (`_oa/` altındaki defter, kütük,
   makbuz, UDF) zaman damgalarıyla çaprazlanır. Kural: bir kapı ancak koşu
   penceresi içinde zaman damgalı bir **eser** bırakmış ve o eser aşağı akışta
   **tüketilmişse** ateşlemiştir; gerisi beyandır.
4. **Karne çıkarımı:** her koşu için desen-başına karne yazılır: ateşledi /
   ateşlemedi / yanlış ateşledi. Başarısızlıklar da yazılır.
5. **Karne → reçete:** her karne bir sonraki sürümün reçetesidir. Aşağıdaki
   sürüm zinciri birebir bu döngünün ürünüdür.

### Mekanik test altyapısı — kod sahaya çıkmadan nasıl sınanır

Saha, son sınavdır; ama hiçbir kod sahaya test görmeden çıkmaz. Laboratuvar
tarafının kuralları:

- **Otomatik regresyon süiti** (ilk paket 57 sınamayla çıkmıştı — her sürüm,
  sahada bulunan her kusuru önce bir teste çevirir). Süitin güncel büyüklüğü
  tek kaynaktan okunur ve mekanik kapıyla doğrulanır:
  [tests/README.md](../../tests/README.md) `OA-SUIT-SAYISI` işaretçisi
  (`tests/test_v0514_vitrin.py` bu sayıyı her koşuda gerçek toplamayla
  karşılaştırır — belgede duran sayı artık BEYAN değil ÖLÇÜMDÜR). Testlerin
  tamamı **sentetik veriyle** koşar: anayasa m.7 gereği hiçbir gerçek dava
  verisi, kişi adı veya dosya yolu test koduna giremez.
- **Önce kırmızı, sonra yeşil (TDD):** her düzeltme, önce kusuru yeniden
  üreten bir testle "kırmızı" görülür; kod ancak o testi yeşile çevirerek
  girer. "Koşmadan geçti demek" yasaktır — test çıktıları karneye fiilî
  koşu sonucuyla yazılır.
- **Kanıt zinciri:** bir onarım, arızanın onarım *öncesi* fiilen
  gösterilmesiyle belgelenir (ör. bozuk teşhis aracının sahte "ARIZA VAR"
  bastığı önce koşuyla kanıtlandı, sonra onarıldı, sonra aynı koşu temiz
  görüldü).
- **CI matrisi:** her push, GitHub Actions üzerinde **Windows + Ubuntu ×
  Python 3.12/3.13/3.14** altı ortamında tam süiti ve ayrıca **aile yapı
  denetimini** (20 parçanın manifest/sürüm/hook tutarlılığı) koşar. Kural
  serttir: **CI yeşermeden sürüm etiketi atılamaz** — bu kural, 11 koşu
  kırmızı kalan CI'ın kimsenin fark etmediği bir dönemin dersidir. Platform
  farkları da burada yakalanır (örnek: Windows'ta görünmeyen bir çalıştırma-izni
  eksiği Ubuntu'da yakalandı ve kapatıldı).
- **Denetçinin denetimi:** teşhis ve denetim araçlarının kendileri de kendi
  testleriyle yaşar; manifest sayı iddiaları ve hook envanteri mekanik
  kapılarla (aile_dogrula Kapı-A/B) doğrulanır — "denetleyen kim denetliyor"
  sorusu açık bırakılmaz.

#### Süit tam olarak nedir — ne, nasıl, neden

**Ne:** her tam koşuda parametreli varyantlarıyla birlikte toplanan sınama
kümesi. Sayı burada TEKRARLANMAZ — tek kaynağı ve mekanik kapısı
[tests/README.md](../../tests/README.md)'dedir (v0.5.14/B-35: sayı üç ayrı yerde
üç ayrı ve üçü de yanlış yazılıydı; sayıyı denetleyen kapı yoktu). Tematik
anatomi (hangi tema, neyi güvence altına alır):

| Tema | Neyi güvence altına alır |
|---|---|
| Sürüm-reçetesi paketleri (`test_vXYZ_*.py`) | Her saha karnesinden doğan onarım paketinin kendi testleri — sahada bulunan her kusur burada sonsuza dek nöbettedir |
| UDF hattı | Üretilen .udf UYAP'ta açılır mı: stil iskeleti, kenar ölçüleri (4×42,52 pt), round-trip okuma, elle-üretim yasağı, atomik mühür |
| Hook katmanı | Altı kanalın ateşleme koşulları, kök çözümü, dedup, nabız, enjeksiyon içerikleri, sunum kilidi kararları |
| Künye / içtihat | Atıf resmî kaynağa çözülüyor mu, [G6] tam-metin/damga şartı, muhakeme kaydı, yetim alıntı |
| Pipeline / defter | Adım zinciri, kanıt şartı, append-only defter bütünlüğü, oturum damgası |
| Teslim zinciri / makbuz | Dokuz kapının sırası, RED/yeşil makbuz garantisi, filo tazeliği, 40-UYAP kopyaları |
| Hafıza / devir | `_oa` iskeleti, oturum devri, çalışma hafızasının senkronu |
| Vakıa / antitez / kıyas | Kronoloji-delil eşlemesi, dokuz cephe bütünlüğü, unsur eşleşme denetimi |
| Süre hesabı | Usul ve maddi süreler, adli tatil ayrımı, son-gün hesabı |
| Ingest / OCR | Evrak sayımı, metin çıkarımı, OCR damgası, künye/indeks üretimi |
| Aile / sürüm bütünlüğü | Manifest-sürüm-hook tutarlılığı, parmak izi, "N skill" sayımı, vitrin sürüm damgaları |
| Usul / kontrol · graf · kit güvenliği · gizlilik · şekil · sözleşme | Usul matrisi, illiyet grafının yapısal sağlığı, rpm karantinası + kilitli çekirdek, Layer 0 desenleri, şekil standardı, kloz kapsamı |
| Vitrin / test altyapısı | Motor kapsam defteri (testsiz motor kalamaz), mutlak yerel yol yasağı, CI etiket tetiği ve OCR bacağı |

**Nasıl doğar:** hiçbir test "aklımıza geldi" diye yazılmadı. Döngü sabittir:
saha karnesi bir kusur ölçer → kusur, **geçici klasörde kurulan sentetik bir
dava senaryosuyla** yeniden üretilir ve test önce KIRMIZI görülür → onarım
yazılır, test yeşile döner → test süitte kalır ve o kusur bir daha asla
sessizce geri gelemez (regresyon kilidi). Somut örnek: bir koşuda teslim
ürününün makbuzdan 68 dakika sonra mührün dışında değiştiği ölçüldü; bugün
süitte "dosya değişti → mühür tazelenmek zorunda" senaryosunu birebir kuran
ve bozulursa sürümü durduran testler var.

**Ne şekilde koşar:** her test kendi geçici klasöründe uydurma bir dosya
kurar ("2024/123 Esas" gibi kurgu kimliklerle) — anayasa m.7 gereği hiçbir
gerçek dava verisi, kişi adı veya yerel yol test koduna giremez. Testler
ağsızdır; ağ/oturum gerektiren gerçek UDF yazıcısı gibi araçlara bağımlı
testler, araç yoksa kendini **görünür şekilde** atlar (sessiz geçiş yok).
Süitin tamamı her push'ta altı ortamda (Windows + Ubuntu × üç Python)
baştan koşar.

**Mühendisler için ayrıntı:** test mimarisinin geliştirici-dili anlatımı
(desenler, sözleşme sınıfları, koşum tarifleri, yeni test ekleme disiplini)
ayrı belgededir: [tests/README.md](../../tests/README.md).

**Neden ve ne amaçla:** bu sistemin avukata verdiği güvenceler ("makbuzsuz
teslim olmaz", "aleyhe karar dilekçeye giremez", "elle UDF yazılamaz") birer
cümle değil, birer KAPIDIR — ve kapının kendisi de bozulabilir. Süit,
o kapıların her sürümde hâlâ kapandığının makine kanıtıdır: bir güncelleme
eski bir güvenceyi bozarsa süit kırmızıya döner ve **CI yeşermeden sürüm
etiketi atılamadığı için** o sürüm yayınlanamaz. Amaç tektir: sahada
avukatın karşısına, laboratuvarda bir kez bile kanıtlanmamış hiçbir
davranışın çıkmaması.

### Belgeli dokuz büyük saha koşusu (149 gerçek dava testi içinden)

Sistem 149 gerçek davada test edilerek bugüne geldi; her koşu karneye
bağlanmadı. Aşağıdaki dokuzu, **v0.5.x geliştirme döngüsünde** koşulan ve
sensörlü izleme + adli analizle uçtan uca BELGELENEN dava testleridir —
v0.5 sürüm zincirini fiilen bu dokuz dava yönlendirdi.
**Dokuz koşunun tam kaydı — yöntem, ölçümler, dersler:**
[SAHA-DENEYLERI.md](SAHA-DENEYLERI.md).

| Saha | Dosya tipi | Ne öğretti → hangi sürüm |
|---|---|---|
| **İlk tam koşu** | ~200 evraklık derdest istinaf dosyası | 49 dk · 45,6k token · teslim edilebilir ek beyan + geçerli UDF ([SAHA-SONUCU.md](SAHA-SONUCU.md)); bayat araç kopyası ve link zinciri dersleri → v0.5.7 · **45,6k token** |
| **Müdahalesiz test** | 214 evraklık bakir klasör | "Kapının gücü kodunda değil **tetiğindedir**" — mekanizmalar sağlamdı, çağrılmıyorlardı → v0.5.5.1–v0.5.5.3 · *(token ölçümü yok — izleme 307'yle başladı)* |
| **447 sahası** | vergi davası | Tetik boşlukları + hook katmanının sessiz ölümü (masaüstü uygulaması hook'u kabuksuz koşturuyordu) → v0.5.8.1 / v0.5.8.2 · **~604k token** |
| **372 sahası** | aile / mal rejimi | Hook katmanı ilk kez uçtan uca canlı ateşledi; koşunun **5 kollu adli analizi** (transkript + artefakt + kod yolu + şekil zinciri + desen karnesi) → v0.5.8.4: elle-UDF engeli, makbuz garantisi, mühür otomasyonu · **~1,24M token** |
| **346 sahası** | bilirkişi raporuna itiraz | Künye kapısı **gerçek bir açığı** yakaladı ve model dürüst davrandı; tek bir ayrıştırıcı yanlış-pozitifi yeşil makbuzu imkânsız kıldı → v0.5.8.5: mutlak triyaj [G6], hook dirilişi, e-imza halkası · **~1,17M token** |
| **777 sahası** | banka/kefalet ikinci cevap + **24 kök çapraz taraması** | Bayat araç kiti kök nedeni; ilk gerçek LEHE/ALEYHE triyajı; resmî araçla üretilen UDF, dört kenarı yönetmelik ölçüsünde (42,52 pt) ilk **tam-standart ürün** olarak UYAP editöründe açıldı → v0.5.8.6 + v0.5.9 · **~1,50M token** |
| **307 sahası** | tasarrufun iptali, ikinci cevap (devralmalı + taze tam indirme) | Uçtan uca zincir + LEHE/ALEYHE triyajı stratejiyi fiilen şekillendirdi; makbuz-sonrası mühür-dışı değişiklik (K1/K2) ölçüldü → v0.5.10: atomik mühür + filo-tazelik ([KARNE-307.md](KARNE-307.md)) · **~822k token / 161 dk** |
| **923 sahası** | vergi/gümrük — ödeme emri + ek tahakkuk, dilekçe ret sonrası yenileme | Tek cümlelik tek prompt, sıfır müdahale, çift ürün (2 dilekçe + 2 UDF); [G6] kapısı dökümsüz atıfları RED'ledi ve model tam-metin damgayla yeşile döndü → v0.5.10 çift-kanıt · **~360k token / 57 dk** |
| **1865 sahası** | idari yüksek yargı, soruşturma-izni itirazı — **çok oturumlu** (5-6 paralel), birden çok müvekkil | rpm bayat-kit nüksü adlandırıldı; söz-müdahalesi ezildi, dosya-düzeyi koruma tuttu → v0.5.11: rpm karantinası + kilitli çekirdek + yönlü tazelik + oturum damgası ([KARNE-1865.md](KARNE-1865.md)) · **toplam ~4,3M token** |

### Gerçek dava testleri — derdest dosyalarda canlı ölçüm

Bu sistem sentetik örneklerle değil, **avukatın kendi derdest dosyalarıyla**
test edilir. Bir gerçek dava testi şöyle koşar:

1. **Dosya gerçektir:** UYAP'tan indirilen ham evrak klasörü (50–210 evrak),
   yürüyen bir davanın güncel hali. Dosya kimliği kayıtlarda yalnız saha
   etiketiyle anılır; isimler ve numaralar hiçbir zaman depoya girmez.
2. **Prompt tektir ve doğaldır:** avukat işi tek paragrafla tarif eder
   ("ikinci cevap dilekçemizi hazırlayacağız, süreleri kontrol et...").
   Mekanik talimat, kapanış promptu, düzeltme zinciri **verilmez**.
3. **Müdahale yasaktır:** koşu boyunca oturuma dokunulmaz; gözlem dosya
   sistemi deltası ve defter kayıtları üzerinden salt-okunur yapılır.
4. **Ölçüm yazılıdır:** hook nabzı, damga oranları, makbuz sınıfı, token
   eğrisi — karne koşudan sonra transkript + artefakt + mekanizma olmak
   üzere üç koldan adli analizle çıkarılır.
5. **İki hüküm ayrı verilir:** mekanik tamlık (zincir fiziksel koştu mu)
   ve içerik kabulü (dilekçe avukatı tatmin etti mi) birbirine karışmaz.

**307 sahası (22.08.2026, v0.5.9.1, tamamlandı — deney sınıfı: MÜDAHALELİ):** tasarrufun
iptali davasında ikinci cevap (beyan) dilekçesi; 209 evraklık taze UYAP
indirimi + bir önceki sürümden devralınan eski çalışma alanı. Ara karne:

| Ölçüm | Sonuç |
|---|---|
| Hook nabzı | 6 kanal ateşledi; bayat araç kiti **3 kez yakalandı**, uyarı modelin bağlamına enjekte edildi ve araçlar 6 dakikada tazelendi |
| İçtihat triyajı | **45 damga, 45'i tam-metin sınıfı** (44 LEHE + 1 ALEYHE-AYIRT); 30 döküm dosyası |
| Muhakeme zinciri | teslim metnindeki her künye için ilgili-kısım + davaya-bağ kaydı mevcut (27 kayıt); uydurma künye yok |
| Aleyhe farkındalığı | Cephanelikteki aleyhe karar dilekçeye alınmadı ve **ana savunma ekseni ona göre kaydırıldı** |
| Gizlilik Layer 0 | Kimlik verisi DENY — içerik hiçbir dış araca gönderilmedi |
| Ürün | Resmî hatla üretilmiş, geçerlilik kapısından geçmiş UDF + PDF |
| Dürüstlük | Yeşil makbuz kesilmeden "hazır" denmedi; sistem **karar-kavşağında durup** 5 kalemi avukatın önüne koydu (fail-closed). Ama makbuz sonrası ürün mühür dışında değişti — bkz. karne K1/K2 |

**Koşu kapandı; nihai karne ayrı belgededir: [KARNE-307.md](KARNE-307.md).**
161 dakika sürdü. Karnenin ilk düzelttiği şey koşu sırasında yapılan kendi
raporumuzdur: bu koşu "tek doğal prompt / sıfır mekanik-hijyen promptu" ile
geçmedi — ölçüm 11 kullanıcı turu ve 7 mekanik-hijyen promptu gösterdi. Deney
sınıfı **müdahalelidir**. Karne ayrıca üç ağır kusur saptadı: teslim ürünü
makbuzdan sonra mührün dışında değişti, makbuz resmî adlı ürünü kapsamıyordu
ve parçalar kendiliğinden çağrılmadı (kök sebep kodda bulundu). Bu kusurlar
v0.5.10 onarım listesini oluşturur.

**923 sahası (24.08.2026, v0.5.9.1, TAMAMLANDI — tek doğal prompt, sıfır müdahale):** vergi/gümrük
dosyası; ödeme emri + ek tahakkuka karşı, dilekçe ret sonrası yenileme; 38
evraklık ham UYAP klasörü; **tek cümlelik tek prompt**. İlk 56 dakikanın
ölçümü (nihai karne kapanışta işlenecek — bunlar ara sayılardır):

| Ölçüm | Ara sonuç |
|---|---|
| Prompt disiplini | 1 kullanıcı turu; **0 mekanik-hijyen promptu** (307 dersinden sonra bu kez transkript sayılarak) |
| Üretim | ~366k token / 56 dk; 25 adım kaydı; alt-ajan 0 |
| İki ayrı iş ürünü | A: ödeme emrine karşı · B: ek tahakkuka karşı — iki ayrı dilekçe + 2 UDF üretildi |
| Künye teyidi | A **15/15** · B **18/18** teyitli, teyitsiz 0; çapraz denetimde kopuk referans yok |
| Antitez / usul | 8/8 cephe (o sürümün sekiz cepheli matrisi; v0.5.16'da dokuz) + çürütme; usul matrisi süre hesabını bağladı (son gün tespiti) |
| Bayat araç nöbetçisi | Bu sahada da ateşledi (1 uyarı) |
| Dürüst altyapı notu | Model, canlı içtihat ucuna erişemeyince yedek arşivle çalıştığını ve arşiv-sonrası kararların eksik olabileceğini kütüğün başına **kendisi yazdı** ("AŞAN-KAYNAK" riski) |
| [G6] sınavının SONUCU | Kapı ÇALIŞTI: teslim zinciri dökümsüz atıflarla RED verdi; model 7 kararın tam metnini döküp damgaladıktan sonra yeşil makbuz kesebildi (04:53). Ayrıca bu koşu, v0.5.10'u doğuran iki kusuru bağımsız tekrarladı: 40-UYAP kopyalarında çift-uzantı ve mühürsüz kopya |

**1865 sahası (25-26.08.2026, v0.5.10→v0.5.11, TAMAMLANDI — sınıf:
MÜDAHALELİ-YETKİLİ · ÇOK OTURUMLU):** idari yüksek yargıda soruşturma-izni
itirazı; birden çok müvekkil, iki dilekçe + çelişki raporu; aynı klasörde 5-6 paralel
oturum. Nihai karne: [KARNE-1865.md](KARNE-1865.md). Özet: v0.5.10'un üç
onarımı ilk gerçek sınavında doğrulandı (filo kapısı yeşilin içinde koştu,
mühür-kırık penceresi dakikasında yakalandı); 777'den beri üçüncü kez nükseden
kök düşman adlandırıldı — uygulamanın rpm anlık-görüntüsünden bulaşan bayat
araç nesli — ve tek seferlik onarımın yetmediği ölçüldü (onarım 9 dk'da geri
ezildi; dosya-düzeyi koruma tuttu). Bu ölçümler v0.5.11'i doğurdu: rpm
karantinası, kilitli çekirdek, yönlü tazelik, oturum damgası.

**Gözcü notları (koşu sırasında, salt-okunur izlemeden):**

- **Teslim zinciri koştu — ama kendiliğinden değil.** Zincir birden çok kez
  çalıştı ve her seferinde bir kapı fail-closed kesti; model bulguları
  düzeltmeye döndü. Ancak karne, kontrol parçasının modelce kendiliğinden
  çağrılmadığını, avukatın onu adıyla çağırmak zorunda kaldığını ölçtü
  (karne K3). Koşu sırasında bunun tersi raporlanmıştı; düzeltilmiştir.
- **Kırmızı makbuz bile damgalı kesildi.** Blok durumunda dahi makbuz
  garantisi çalıştı; dış-çıktı dizini yeşil makbuz olmadan **doğmadı** —
  tasarlandığı gibi.
- **Devir + taze indirme birlikte sınandı.** Dosya baştan indirildiği için
  eski çalışma alanının önbelleği yeni evrak adlarıyla hiç örtüşmüyordu
  (209 dosyada 0 ad kesişimi); sistem eski kütüğün 16 damgasını koruyup
  üstüne yeni triyajı ekledi, çökmedi.
- **Üretim temposu:** ~8 bin token/dk sabit; ilk 20 dk keşif+devralma
  (yüksek önbellek okuma), sonra tam-metin içtihat triyajı, sonra yazım.
  13 karar tam metniyle tek tek çekildi — künyeden damga basma hiç görülmedi.
- **Kalan sınır dürüstçe raporlandı:** müvekkil-aleyhi tarayıcısı, birebir
  Yargıtay alıntısının *içindeki* "davanın kabulüne" ibaresini kendi
  cümlemizden ayıramıyor; model bunu aşmaya çalışmak yerine kararı gerekçesiyle
  avukata taşıdı. Bu ayrıştırıcı sınıfı sonraki sürümün onarım listesindedir.

### Ölçülen örnekler — beyan değil sayı

Tüm koşuların token/süre/verim kayıtları ve ölçüm yöntemi ayrı
belgededir: **[OLCUMLER.md](OLCUMLER.md)**.

- **49 dakika / 45,6k token:** ~200 evraklık istinaf dosyasından teslim
  edilebilir ek beyan + geçerli UDF. Aynı sınıf iş, evrakı modele görüntü olarak
  yükleyen eski usulde **1M+ token** yiyordu — fark **~26×**, muhakemeden tek
  satır kısılmadan (dakika dakika çizelge: [SAHA-SONUCU.md](SAHA-SONUCU.md)).
- **Elle-UDF krizinin çözümü:** sahada model UDF dosyasını elle kurmaya
  yeltendi; elle kurulan dosya UYAP Doküman Editöründe **açılmıyordu**. Çözüm
  A/B testiyle bulundu: açılan ve açılmayan dosyaların iç imzaları
  karşılaştırıldı (editör `hvl-default` stil iskeletini arıyor). Sonuç üç
  katmanlı engel: elle üretim girişimi anında yakalanır, dosya imzası
  denetlenir, üretim yalnız resmî araçla yapılır.
- **İlk LEHE/ALEYHE triyajı:** 777 sahasında MCP'den çekilen kararlar tek tek
  **tam metniyle** okundu ve damgalandı — 23 LEHE / 11 ALEYHE. ALEYHE olanlar
  dilekçeye değil iç cephaneliğe gitti (anayasa m.6).
- **Yeşil makbuz zinciri:** teslim, ancak tüm kapılar fiilen koşup makbuz
  kestiğinde "hazır" sayılır; makbuzsuz "TESLİME HAZIR" beyanı v0.5.8.5'ten
  beri **bloktur**.
- **İki bağımsız hakem denetimi:** sürüm zinciri, iki ayrı bağımsız Claude
  Fable 5 oturumunca hakem olarak denetlendi; konsolide **T1–T26 raporu**nun
  tamamı v0.5.9'da yerli olarak uygulandı — denetim araçlarının kendileri de
  artık kendi testleriyle yaşıyor ("denetçinin denetimi").

### Dürüstlük — başarısızlıklar da yazılır

- **İlk organik yeşil makbuz: 923 sahası.** Tek cümlelik tek prompt, sıfır
  müdahale, sıfır mekanik-hijyen promptu — ve zincir RED'den kendi düzeltmesiyle
  yeşile döndü. 307 ise müdahaleliydi (7 hijyen promptu ölçüldü) ve karnesine
  öyle yazıldı; 1865 "müdahaleli-yetkili" sınıfındaydı. Sınıflar karıştırılmaz:
  her koşunun makbuzu kendi damgasını taşır.
- **İçerik kabulü avukat yargısıdır:** hiçbir kapı "bu dilekçe hukuken
  isabetli" demez; kapılar unsur, künye, biçim ve iz denetler. Hukuki isabet
  hükmü size aittir.
- Geçmiş sürümlerin ham dersleri saklanmaz: teslim hattının avukatın kendi
  makinesinde çökmesi, 11 koşu kırmızı kalan CI, elle yazılmış defter, geçerli
  dilekçeyi kesen kapı — hepsi tarihiyle [STATUS.md](../../STATUS.md)'de durur.

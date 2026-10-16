# GELİŞİM DEFTERİ (CHANGELOG)

Bu depo "gerçek testlerle optimum" yöntemiyle gelişir: **gerçek derdest dava
koşusu → karne → karnede ölçülen kusurun onarımı → yeni sürüm.** Bu defter,
sürüm zincirinin kök özetidir. Üç kademe birbirini tamamlar:

- **Bu dosya** — sürüm başına tek kayıt (ne, neden, hangi saha kanıtıyla).
- **Parça günlükleri** — her skill'in kendi `references/degisiklik-gunlugu.md`
  dosyası (dosya/fonksiyon düzeyinde ayrıntı).
- **Karneler ve Release'ler** — saha koşularının adli analizi
  ([KARNE-307.md](docs/arsiv/KARNE-307.md), [KARNE-1865.md](docs/arsiv/KARNE-1865.md),
  [SAHA-SONUCU.md](docs/arsiv/SAHA-SONUCU.md)) ve GitHub Release notları.

Kural: **CI yeşermeden sürüm etiketi atılamaz**; sürüm damgaları (plugin,
marketplace, iki script) daima birlikte artar. Dosya kimlikleri anayasa m.7
gereği yalnız saha etiketiyle anılır.

---

## Saha sonuçları

*(2026-10-12'de vitrinden (README) kelimesi kelimesine taşındı. Avukat kararı: saha sonucu
ve benzeri ayrıntılar sürüm defterinde durur; vitrinde hukukçular için sözlük kalır.)*

> ⚖️ **Gerçek davalarda test edildi.Geliştirilmeye devam ediliyor.** Bu sistem sentetik örneklerle değil,
> derdest gerçek dosyalarla sahada sınanıyor: v0.0.1'den v0.5.16'ya gelen
> geliştirme zinciri **149 gerçek davada** test edildi (v0.5.17–0.5.18 denetim,
> güvenlik ve evrak-okuma sürümleridir; belgeli saha koşusu sayısı değişmedi —
> bkz. [Güncelleme notları](README.md#güncelleme-notları)); bunların **dokuzu**,
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
> değildir (ölçüm ve kayıp listesi: [SAHA-SONUCU.md](docs/arsiv/SAHA-SONUCU.md)). Evraklar
> [avukat-dosya-indirici](https://github.com/bcancapar-spec/avukat-dosya-indirici) ile PDF olarak indirilmiş, bu eklentiyle `.md`/`.json` biçimine otonom çevrilmiştir.
> Sayılar ve dürüst kayıp listesi: **[SAHA-SONUCU.md](docs/arsiv/SAHA-SONUCU.md)** · **[BASARI.md](docs/arsiv/BASARI.md)**. Dosya kimlikleri projenin anayasası m.7 gereği daima
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
  [tests/README.md](tests/README.md) `OA-SUIT-SAYISI` işaretçisi
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
[tests/README.md](tests/README.md)'dedir (v0.5.14/B-35: sayı üç ayrı yerde
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
ayrı belgededir: [tests/README.md](tests/README.md).

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
[SAHA-DENEYLERI.md](docs/arsiv/SAHA-DENEYLERI.md).

| Saha | Dosya tipi | Ne öğretti → hangi sürüm |
|---|---|---|
| **İlk tam koşu** | ~200 evraklık derdest istinaf dosyası | 49 dk · 45,6k token · teslim edilebilir ek beyan + geçerli UDF ([SAHA-SONUCU.md](docs/arsiv/SAHA-SONUCU.md)); bayat araç kopyası ve link zinciri dersleri → v0.5.7 · **45,6k token** |
| **Müdahalesiz test** | 214 evraklık bakir klasör | "Kapının gücü kodunda değil **tetiğindedir**" — mekanizmalar sağlamdı, çağrılmıyorlardı → v0.5.5.1–v0.5.5.3 · *(token ölçümü yok — izleme 307'yle başladı)* |
| **447 sahası** | vergi davası | Tetik boşlukları + hook katmanının sessiz ölümü (masaüstü uygulaması hook'u kabuksuz koşturuyordu) → v0.5.8.1 / v0.5.8.2 · **~604k token** |
| **372 sahası** | aile / mal rejimi | Hook katmanı ilk kez uçtan uca canlı ateşledi; koşunun **5 kollu adli analizi** (transkript + artefakt + kod yolu + şekil zinciri + desen karnesi) → v0.5.8.4: elle-UDF engeli, makbuz garantisi, mühür otomasyonu · **~1,24M token** |
| **346 sahası** | bilirkişi raporuna itiraz | Künye kapısı **gerçek bir açığı** yakaladı ve model dürüst davrandı; tek bir ayrıştırıcı yanlış-pozitifi yeşil makbuzu imkânsız kıldı → v0.5.8.5: mutlak triyaj [G6], hook dirilişi, e-imza halkası · **~1,17M token** |
| **777 sahası** | banka/kefalet ikinci cevap + **24 kök çapraz taraması** | Bayat araç kiti kök nedeni; ilk gerçek LEHE/ALEYHE triyajı; resmî araçla üretilen UDF, dört kenarı yönetmelik ölçüsünde (42,52 pt) ilk **tam-standart ürün** olarak UYAP editöründe açıldı → v0.5.8.6 + v0.5.9 · **~1,50M token** |
| **307 sahası** | tasarrufun iptali, ikinci cevap (devralmalı + taze tam indirme) | Uçtan uca zincir + LEHE/ALEYHE triyajı stratejiyi fiilen şekillendirdi; makbuz-sonrası mühür-dışı değişiklik (K1/K2) ölçüldü → v0.5.10: atomik mühür + filo-tazelik ([KARNE-307.md](docs/arsiv/KARNE-307.md)) · **~822k token / 161 dk** |
| **923 sahası** | vergi/gümrük — ödeme emri + ek tahakkuk, dilekçe ret sonrası yenileme | Tek cümlelik tek prompt, sıfır müdahale, çift ürün (2 dilekçe + 2 UDF); [G6] kapısı dökümsüz atıfları RED'ledi ve model tam-metin damgayla yeşile döndü → v0.5.10 çift-kanıt · **~360k token / 57 dk** |
| **1865 sahası** | idari yüksek yargı, soruşturma-izni itirazı — **çok oturumlu** (5-6 paralel), birden çok müvekkil | rpm bayat-kit nüksü adlandırıldı; söz-müdahalesi ezildi, dosya-düzeyi koruma tuttu → v0.5.11: rpm karantinası + kilitli çekirdek + yönlü tazelik + oturum damgası ([KARNE-1865.md](docs/arsiv/KARNE-1865.md)) · **toplam ~4,3M token** |

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

**Koşu kapandı; nihai karne ayrı belgededir: [KARNE-307.md](docs/arsiv/KARNE-307.md).**
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
oturum. Nihai karne: [KARNE-1865.md](docs/arsiv/KARNE-1865.md). Özet: v0.5.10'un üç
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
belgededir: **[OLCUMLER.md](docs/arsiv/OLCUMLER.md)**.

- **49 dakika / 45,6k token:** ~200 evraklık istinaf dosyasından teslim
  edilebilir ek beyan + geçerli UDF. Aynı sınıf iş, evrakı modele görüntü olarak
  yükleyen eski usulde **1M+ token** yiyordu — fark **~26×**, muhakemeden tek
  satır kısılmadan (dakika dakika çizelge: [SAHA-SONUCU.md](docs/arsiv/SAHA-SONUCU.md)).
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
  dilekçeyi kesen kapı — hepsi tarihiyle [STATUS.md](STATUS.md)'de durur.

---

---

## Sürümsüz — BAĞIMSIZ KOD VE VİTRİN DENETİMİ (2026-10-15, dal `denetim/fable-2026-10-15`)

**Sürüm numarası değişmedi (0.6.0); sürüm, birleştirme ve yayın kararı avukatındır.** Depo
v0.6.0 hâliyle ölçümle denetlendi (tam süit, aile yapısı, statik analiz, kurulu eklentinin
kanca sağlığı, kurulum motoru); bulgular, karar ve plan [docs/DENETIM-2026-10-15.md](docs/DENETIM-2026-10-15.md)'de. Her onarım önce
kırmızı testle; dal GitHub'a push edilmedi.

- **Numaralı liste kaynak numarasını korur (B-1):** `md_udf_html.py` ilk madde 1 değilse
  `<ol start="N">` yazar; "A. USUL / B. ESAS" alt başlığıyla bölünen talep bentlerinde 9. bent
  artık "1." basılmıyor. Açık PR #6'nın (2026-09-14, main ile çakışmış) saha bulgusu; kod bu
  dalda yeniden yazıldı. 1'den başlayan listede çıktı eskisiyle bayt-özdeş.
- **Kaynak hijyeni kapısı (B-2…B-5):** `ruff.toml` yalnız hata sınıfı kurallarla (sözdizimi,
  tanımsız ad, yeniden tanım, kullanılmayan import, yinelenen küme öğesi, ham görünmez /
  çift-yönlü karakter); CI'da bağımsız `lint` işi, ruff sürümü sabit. Cf-sınıfı regex ve üç
  testteki ham karakterler kaçış yazımına çevrildi (desen özdeş; `test_v0518_metin_hijyeni`
  istisnasız kaldı); 35 kullanılmayan import, bir ölü dal, bir yinelenen küme öğesi temizlendi.
  Kapı kendini de sınar: `tests/test_kaynak_hijyeni.py`.
- **Sürüm damgası (B-6):** `pyproject.toml` `version` 0.1.0'da kalmıştı → 0.6.0;
  `aile_dogrula.surum_isaretcileri` artık pyproject'i de denetler (UYARI sınıfı).
- **Kök dizin ve bağlantı kapısı (B-7, B-11):** 11 tarihî kayıt `docs/arsiv/`'e
  ([dizin notu](docs/arsiv/README.md)), yaşayan iki defter (`PERFORMANS-STATUS`,
  `SICRAMA-NOTU`) `docs/`'a taşındı; 69 bağlantı yeniden yazıldı;
  `tests/test_belge_baglantilari.py` her belge bağlantısının hedefini denetler (taşımayla 29
  kırık gösterdi, yeniden yazımla yeşil). Kayıt notu (heyet 2026-10-16 USUL U-1): 13 dosyalık
  taşıma fiilen `47bba4d` ile girdi; `45a6d2e` bağlantıları yeniden yazdı ve kapıyı ekledi.
- **Excel'de gizli katman (YOL-HARITASI v0.5.19 kalemi; anayasa m.11):** belge güvenlik kapısı
  tabloyu artık "DENETLENEMEZ" diye sarmıyor; çalışma kitabını yeniden açıp gizli satır/sütun,
  sıfır yükseklik/genişlik, zeminle aynı renkteki yazı (tema/dizin/tint çözülür), `;;;` biçimi ve
  minik puntoyu ölçüyor (.xlsx openpyxl tam kip; .xls xlrd `formatting_info`). Gizli parça
  okuyucunun yazdığı satırla eşlenip yerinde `⟦GİZLİ KATMAN⟧` alıyor; değer silinmiyor. Gizli
  sayfa/satır/sütun/biçim UYARI, zeminle aynı renk ve minik yazı BULGU, gizli katmandaki talimat
  BULGU. Kitap açılamaz, boyut sınırı aşılır ya da okuyucu metniyle eşleşmezse tablo yine
  DENETLENEMEZ kalır. Önce kırmızı: `tests/test_v0519_excel_gizli_katman.py` (.xls fikstürü ham
  BIFF8, yeni bağımlılık yok). Gerçek evrak ölçümü küçük (eldeki tek .xls temiz); kalibrasyon
  sahadan.
- **Vitrin:** README katmanlı düzene geçti: rozetler, "Kim için, ne okumalı", "Bir bakışta:
  yapar / yapmaz", "Hâkim ve savcı gözüyle", özet parça tablosu; master prompt, tam katalog ve
  sürüm notları katlanır bloklarda aynen korundu; DÜSTUR m.6 satırı ve dizgi hataları
  düzeltildi. Avukatın commit'lenmemiş README düzeltmeleri (Excel okuyucuları, Mağaza
  kısayolu, prompt satırları) dala alındı.
  Eklenti README'si (ikinci vitrin) de aynı düzene geçti (`8a1c882`): kısa giriş ve okuyucu
  yönlendirmesi, "Bir bakışta: yapar / yapmaz", hatta yeri ve script sayısı taşıyan özet parça
  tablosu, katlanır tam katalog, v0.6.0 ve bu denetime bağlantı; kilitli bloklar aynen.
  Tablodaki üç script sayısı elle yazılmıştı ve bayattı (oa-pipeline 10 → 11, oa-ingest 5 → 6,
  çekirdek "—" → 1, kurulum motoru); kök kataloğun başlıkları da aynı sayıları taşıyordu,
  düzeltildi. `tests/test_eklenti_vitrini.py` iki vitrindeki sayıları
  `skills/<parça>/scripts/*.py` sayımına, katmanlı düzeni ve belge bağlantılarını kilitler
  (OA-SUIT-SAYISI 3781 → 3785).
- **Depo hijyeni:** `.github/SECURITY.md` (güvenlik bildirimi: müvekkil verisi içeren bulgu
  herkese açık issue'ya yazılmaz) ve `.github/PULL_REQUEST_TEMPLATE.md` (depo sözleşmesi).
- **Ölçüm (avukatın makinesi, Python 3.14.8, Windows):** tam süit 3800 geçti · 12 ortam gerekçesiyle atlandı (udf-cli oturumu, saha referansı) · 0 kırmızı (87,0 s, paralel); zamanlama testi 1 geçti; aile yapı denetimi TEMİZ; ruff kapısı temiz; kurulu eklentide 6/6 kanca olayı sağlıklı; toplanan test 3813, OA-SUIT-SAYISI ile birebir.
- **Dokunulmayan (avukat kararı):** sürüm numarası; GitHub depo açıklaması ve konu etiketleri
  (B-8, öneri belgede); hukuki içerik ve playbook'lar (m.4, m.9); `_gorus/`; `revizyon_farki.py`
  iç fonksiyonunun geç bağlanması (B-10, bugün hata değil).
- **Heyet (2026-10-16):** push öncesi kıdemli avukat denetim kurulu kuruldu (`c5f739f`, `8be918f`:
  üç Fable ajanı — usul, esas, güvenlik; protokol [docs/heyet/README.md](docs/heyet/README.md)) ve
  dalın bütünü (`origin/main..HEAD`, 14 commit) için ilk kez koşuldu: üç üye de ŞARTLI PUSH,
  BLOKLAYICI 0 · UYARI 8 · NOT 18; tam süit temiz kopyada 3800 geçti · 12 atlandı · 0 kırmızı
  (93,99 s). Push'tan önce istenen iki kalem Excel gizli katman kapısında (ızgara tavanı, tablo
  stili zemini). Üç rapor, birleşik bulgu listesi ve onarım kalemleri:
  [docs/heyet/2026-10-16/KARAR.md](docs/heyet/2026-10-16/KARAR.md). Push yapılmadı; karar avukatın.
  **Onarım (aynı gün; avukat kararı: push yok, önce K-1 ve K-2):** Excel kapısı var olan hücreleri gezer,
  ızgarayı değil (`_xlsx_var_olan_hucreler`; tek uzak stilli hücreli 5 KB kitapta 6,29 s / 400 MB →
  0,01 s / 0,3 MB); boyut sınırı `xl/` bütününe uygulanır; tablo stili aralığı koşullu biçimle aynı ZAYIF
  kural (koyu başlıkta beyaz yazı yanlış BULGU üretmez). Önce kırmızı: `tests/test_v0519_excel_gizli_katman.py`
  +3 (OA-SUIT-SAYISI 3813 → 3816). İkinci heyet koşumu bu onarımdan sonra.
  **İkinci koşum (aynı gün, HEAD `ca37539`):** usul ŞARTLI PUSH (BLOKLAYICI 0 · UYARI 2 · NOT 6), esas
  ŞARTLI PUSH (0 · 2 · 11), güvenlik PUSH (0 · 0 · 5); tam süit temiz kopyada 3803 geçti · 12 atlandı ·
  0 kırmızı; K-1 ve K-2 üç üyenin ölçümüyle kapandı; usulün push öncesi kayıt şartları (taşıma atfı notu,
  `.gitignore` `.claude/`, STATUS tarihi, DENETIM ölçüm satırı) bu kayıtla kapatıldı; kalan kalemler aynı
  dalda ayrı commit ya da açık kalem (ZAYIF aralık kaydı, 128 MB tavanının bellek karşılığı, `docProps`
  toplamı, süre denetimi, UYARI etiketi, `<ol start>` UDF ölçümü):
  [docs/heyet/2026-10-16-2/KARAR.md](docs/heyet/2026-10-16-2/KARAR.md). Push yapılmadı; karar avukatın.

---

## v0.6.0 — ANAYASANIN SAHADA İCRASI · TÜM SİSTEMİ ANLATAN VİTRİN (2026-10-12)

**Sürüm numarası avukat kararıdır (Av. Bayram Can Çapar, 2026-10-12).** 0.6.0, aşağıdaki
v0.5.18 çizgisinin (A–R) yayınıdır. Yürürlükteki anayasa maddeleri sahada icra edilir hâle
geldi; vitrin de sistemin tamamını kurucu fikrinden kopmadan anlatan bir düzene kavuştu. Yeni
ilke ya da yeni parça yoktur; kod davranışı v0.5.18 çizgisinin son hâliyle aynıdır.

- **Vitrin:** kök README'nin başına "Sistem bir bakışta" haritası eklendi. Kurucu fikir
  (model kurar → script denetler → model muhakeme eder; kişilere değil yönteme bağlılık;
  anayasa m.0) ve mevcut bölümler yerinde kaldı. Harita bölümleri müvekkilin menfaati
  ölçüsüyle birbirine bağlar; metin sökülüp yeniden yazılmadı.
- **Sürüm damgaları birlikte arttı:** plugin.json, marketplace.json, `pipeline_kayit.py`
  ve `teslim_paketi.py` `OA_SURUM`, iki README, STATUS ve YOL-HARITASI.
- **SICRAMA-NOTU ile ilişki:** not, 0.6.0'ı "aletin ne olduğunu değiştiren" yapısal sıçramaya
  ayırmıştı (dava-başına alet mi, hafızalı büro mu). O soru açık kalır. Bu numara avukatın
  yayın kararıdır, yapısal sıçrama iddiası değildir.
- **Güncelleyenin yapacakları:** v0.5.18'inkilerle aynıdır (README → Güncelleme notları).
  Eklenti yeni sürüm klasörüne (`0.6.0`) açılır; `compileall` o klasörde koşar.
- **Her yetenekte ne yapıldı:** [docs/SURUM-0.6.0-YETENEKLER.md](docs/SURUM-0.6.0-YETENEKLER.md) — yirmi
  parçanın her biri için avukat dilinde özet, değişiklik ölçüsü ve parça günlüğünden kayıtlar.
- **Büyüklük:** main'e göre ölçüm PR #8 açıklamasındadır (sayı her commit'le değiştiği için
  deftere yazılmaz).

---

## v0.5.18 — BELGE GÜVENLİĞİ (B-22) + OCR v1.9 + YARGI PRO UYARLAMALARI + HALÜSİNASYON KAPISI (2026-10-06 → 10-12)

**Ne:** karşı tarafın evrakındaki gizli talimatlara karşı belge güvenlik kapısı, sayfa düzeyinde izlenebilir OCR, gerçek evrak taramasıyla bulunan okuma kayıplarının kapatılması, Yargı PRO hukuk skill kütüphanesinden fikir düzeyinde uyarlamalar (kod/metin alınmadı), 2026-10-06 kod denetiminin ve Fable bağımsız denetiminin düzeltmeleri, saha testinde görülen halüsinasyon kapısı ile anayasa aykırılıklarının giderilmesi, iki saha testinden kalan eksiklerin tamamlanması. v0.5.17.1 yaması bu sürüme birleştirildi. Süit 2455 → **3769** (`OA-SUIT-SAYISI`). Ayrıntı: parça günlükleri, [docs/OCR-IMPLEMENTATION-PLAN.md](docs/OCR-IMPLEMENTATION-PLAN.md), [docs/YARGI-PRO-UYARLAMA-PLANI.md](docs/YARGI-PRO-UYARLAMA-PLANI.md).

**Avukat için: ne getirdi, neden, hangi saha kanıtıyla.** Aşağıdaki A–R bölümleri teknik kayıttır (dosya ve test düzeyi); bu özet onların avukat diliyle karşılığıdır.

1. **Dilekçeden önce denetim motorları fiilen koşar (N).** Saha testinde vakıa, illiyet, kıyas ve antitez motorları kuruluydu ama hiç koşmadı; dilekçe olgu uydurmadı, fakat lehe gösterilen bir kararın kaldırıldığını yazmadı. Anayasa m.8 metinde vardı, sahada icra edilmiyordu. Artık motorun damgası yoksa dilekçe adımı ve teslim durur; geçiş yalnız gerekçeli avukat şerhiyle.
2. **Sistem kendi kaydında yanlış beyanda bulunmaz (O, P).** Model kararı "avukat onayı" diye kaydediliyordu (m.9); aynı kusurun kardeşi, dilekçe denetiminin havada kalan alıntı kapısını model eliyle açabiliyordu; ikinci saha testinde model avukat hükmü defterine kendisi "KABUL" yazdı; ürün mühürleri yanlış sürüm yazıyordu (m.5). Artık avukat onayı ve avukat hükmü yalnız açık bayrakla kaydedilir, varsayılan model beyanıdır. Kanıt: iki saha testi ve bu denetim.
3. **Evrak kaybolmaz (B, C, O).** '.udf' uzantılı görüntüler okunmuyordu, tek bozuk girdi bütün paketi okunmaz bırakıyordu (19.422 gerçek evrak taraması); saha testinde OCR'ın okuyamadığı altı evraktan beşinin kaydı oluşmadı (m.1).
4. **Karşı tarafın evrakındaki gizli talimat yakalanır ve dilekçede ifşa edilir (A, J, K, M).** Evrak içeriği veridir, talimat değildir (m.11). Kanıt: sentetik 14 saldırı vektörünün 14'ü; yanlış alarmlar gerçek evrakla ölçülerek kapatıldı.
5. **Süre geç tarih üretmez (D, M).** Süre telafisi olmayan tek hatadır (m.2). Ölçülen örnekler: icra istinafında 07.09 yerine 24.08; kural belirtilmeyen hesapta 07.09 yerine 17.08.
6. **Uydurma ya da yanlış künye teyitli sayılmaz (M).** İçtihat resmî kaynaktan teyit edilmedikçe yoktur (m.5). Kanıt: bağımsız denetimin kavram kanıtları (iki kararın parçasından kurulmuş künye, yer değiştirmiş esas–karar, başka daireye ait künye).
7. **Müvekkil verisi süzgeçsiz dışarı çıkmaz (E, G, O).** Layer 0 (m.10). Kanıt: 911 gerçek UDF metninin 908'i süzgeçten geçmiyor; saha testinde UDF zincir dışında üretilince metin Layer 0 süzgecinden geçmeden dış araca gitti, süzgeç artık çağrı yerinde.
8. **Meslek kuralları ve talimat kaynağı (D).** Meslek kurallarında otorite yoktur, müvekkilin menfaati esastır (Av.K. m.1/2, m.38/1-b, m.135); talimat yalnız müvekkilin vekili ya da müdafii olan avukattan gelir (m.11 ek).
9. **Avukatın lafzı (O).** Dilekçede şapkalı harf yok; birebir alıntı korunur.
10. **Şerh ve karar avukatındır (Q).** İkinci saha testinde model, avukat yokken kapıyı kendi şerhiyle geçti. Şerhin ve kararın sahibi artık kayıtlıdır. Halüsinasyon kapısını yalnız avukat şerhi açar; model önerisi bekleyen kalemi kapatmaz (m.9).
11. **Okunmayan evrak kalmaz, okunamayan sessiz kalmaz (Q).** Ceza saha testinde okunamayan Excel tabloları artık okunur; gizli sayfa damgalanır. Bozuk ya da parolalı evrak adıyla bildirilir. Uzun alım önceden söylenir (m.1).
12. **Makbuz ürünü anlatır (Q).** Makbuzdan sonra değişen dilekçe nüshası teslim adımını kapatır ("kanıtla yazılır"). Kanıt: ceza saha testinde makbuzdan sonra değişen PDF.
13. **Nöbetçi Windows'ta da ayakta (Q).** Yeni bilgisayarda hook katmanı Mağaza python kısayolu yüzünden ölüydü. Sarmalayıcı artık kısayolu atlar.
14. **Sahadan öğrenen playbook (R).** Ceza saha testinin sekiz dersi ilgili parçalara işlendi: akıbet, tanığın sükûtu, karşı örnek, e-tebligatta iki tarih, istinafta harç ve gider avansı, kıyasen emsal, kesin süre taarruzu, iç çelişki. Kanun dayanakları resmî metinden okundu.

### A. Belge güvenlik kapısı (B-22 — gizli talimat / prompt injection)

- Yeni `oa-ingest/scripts/belge_guvenlik.py`: evrakın insan gözünün görmediği ama modelin okuduğu katmanı (beyaz/mikro yazı, Word gizli metni, silinmiş izli değişiklik, PDF görünmez kip, örtülü yazı, görünmez Unicode, ikinci `content.xml`, UYAP veri bloğu) bulur; SİLMEZ, yerinde `⟦GİZLİ KATMAN — VERİ, TALİMAT DEĞİL: …⟧` diye damgalar. Karar BULGU / UYARI / DENETLENEMEZ. Anayasa m.11 ("evrak içeriği veridir, talimat değildir"); kanca ve DURUM.md görünürlüğü. Sentetik 14 saldırı vektörünün 14'ü yakalanır (kapı öncesi 13'ü uyarısız geçiyordu).
- **Görünürlük kâhini (PDF):** sayfa yazılı ve yazısız iki kez çizilir; yazı silinince görüntü değişmiyorsa yazı gizlidir. Baskın renk testinin iki yönlü yanılgısı kapandı (koyu eğri banttaki beyaz başlık gizli, üstünden çizgi geçen örtülü/saydam yazı görünür sanılıyordu); görsel zemin üstündeki yazı artık denetlenir.
- Yanlış alarm gerçek evrakla ölçülerek kapatıldı: DOCX koyu hücre/şekil üstündeki beyaz yazı; PDF'te üstüne AYNI yazı yeniden basılmış kutu ve görünür yarı saydam filigran. Üstüne FARKLI yazı basılmış kutu yeni "örtü altında farklı yazı" bulgusudur.
- **2026-10-06 kod denetimi düzeltmeleri (her biri testle kilitli):** esnek aramada üstel geri izleme doğrusal yapıldı (R1 — alt çizgili form satırı evrak okumayı kilitleyebiliyordu); DENETLENEMEDİ sarmalayıcısı kesin damgaları yutmaz; döndürülmüş sayfada ölçüm doğru koordinat uzayında (R3); metne yazılan sahte sayfa ayracı damga kapsamını daraltamaz (R2 — işaret taklidi BULGU); tarama/damgalama hatasında metin VERİ diye sarılır (R6); DURUM.md'de evrak adı nötrlenir (R5); damgalı bölgedeki tarihler ayrı sayılır (R4); kâhin eski PyMuPDF'te ya da hata verdiğinde sessizce kapanmaz, raporda "kahin-devre-disi" notu çıkar (R9).
- **Son bağımsız güvenlik incelemesi (Fable 5.1, salt okunur, PoC'lerle; 2026-10-06):** hüküm "push için engel yok". Bir ORTA bulgu yayından önce kapatıldı (F-1): UDF/DOCX'te 300 karakteri aşan gizli parça gövdede birebir dururken bulunamıyor ve damgasız kalıyordu; artık yerinde damgalanır, konumlanamayan parçada evrak PDF'teki gibi VERİ diye sarılır (fail-closed). Hijyen (F-2): yerel OCR model ağırlıkları `.gitignore`'a alındı. Denenen ve geçen saldırılar: esnek arama ReDoS, DENETLENEMEDİ birleştirmesi, sahte sayfa ayracı, DURUM.md ad enjeksiyonu, zip-slip, künye desenleri, UDF iç iz ayıklaması, tedarik zinciri sabitleri, açık depo sızıntısı.

### B. OCR v1.9

- Sayfa düzeyi yönlendirme: karma PDF'te taranmış sayfa artık sessizce boş kalmaz; tarayıcının harici OCR katmanı KESİN metin sayılmaz (teyit damgası).
- Tesseract'tan gerçek güven değeri; kritik alan teyidi (tarih, esas/karar no, TCKN, IBAN — değer düzeltilmez, şüpheli işaretlenir); sayfa başına zaman aşımı.
- Yalnız yerel PaddleOCR yönlendiricisi (`--ocr-motor`). Yeni `tools/ocr_kiyas.py` motorları OA'nın kendi çağrı yolundan ölçer. Yeni donanımda (2026-10-06, 16 çekirdek): Tesseract 0,15 sn/sayfa; Paddle en iyi ayarda 7,8-10,3 sn/sayfa, temiz sayfalarda eşit doğruluk, yalnız gürültülü sayfada Türkçe harfleri daha iyi koruyor → varsayılan Tesseract kalır. MKL-DNN bu Paddle sürümünde çalışmıyor (ölçüldü). Bulut OCR yok.

### C. Gerçek evrak taraması (eski bilgisayarda; yerel, salt okunur; evrak metni kayda geçirilmedi)

- 1. geçiş: 19.422 evrak (arşiv içiyle 20.261 kayıt), çöküş 0. Bulunan ve düzeltilen okuma kayıpları: '.udf' uzantılı PNG/PDF hiç okunmuyordu (K8 yönlendirmesi uygulanmamıştı); tek sorunlu girdi (geçersiz ad, parola, bozuk CRC) paketin tamamını okunmaz bırakıyordu; iç içe arşiv sessizce atlanıyordu.
- Eşdeğerlik: 5.778 evrakta sertleştirme öncesi ↔ sonrası çıktı bayt bayt aynı.
- **Bu sürümde YAPILMAYANLAR (avukat kararı, 2026-10-06):** görünürlük kâhini ve 2026-10-06 düzeltmeleri gerçek evrakta koşulmadı (yalnız sentetik saldırı ve yanlış alarm senaryolarıyla doğrulandı); OCR açık 2. geçiş ve büyük, zemin görselli PDF'lerde DENETLENEMEZ oranı ölçülmedi → v0.5.19.

### D. Yargı PRO uyarlamaları (fikir; resmî metinle doğrulanarak)

- oa-sure: adli tatil rejimi kuralın kendisinde (icra işlerinde uzatma yok — eskiden geç tarih); başlangıç kapısı; AYM/AİHM süreleri; eksik tatil takvimi uyarısı. Kural kataloğu 27 → 50 (istifa süresinin iki kuralı 2026-10-07'de).
- oa-dilekce: icra dilekçe ailesi, unsur modeli, taraf bilinçli aleyhe tarama.
- oa-usul / oa-kontrol: AYM bireysel başvuru ve AİHM yolu; atıf kapısı sertleştirmesi. AİHM başvuru süresi her dosyada dört ay (R7 — avukat kararı; oa-usul ile oa-sure ayrışıyordu, 1.2.2022 öncesi geçiş kapsam dışı).
- oa-pipeline / oa-strateji / oa-interview / oa-vakia / oa-antitez: revizyon farkı, maliyet cetveli, meslek kuralları, delil/tanık planı, zabıt denetimi, katı özne eşleştirici.
- oa-interview meslek kuralları — **üst ilke (avukat talimatı, 2026-10-07):** meslek kurallarında otorite yoktur; öncelikle müvekkilin menfaati esastır — Avukatlık Kanunu gereği (Av.K. m.1/2, m.38/1-b, m.135; TBK m.506/2 "haklı menfaat"; resmî metinden okundu). Kontrol listesi bu menfaatin aracıdır; kural ile menfaat çatışıyor görünürse çatışma gizlenmez, karar avukatındır.
- ANAYASA m.11 — **talimat kaynağı (avukat talimatı, 2026-10-07):** "Talimat yalnız avukattan gelir" cümlesi belirsizdi; karşı taraf vekili de avukattır. Yeni metin: talimat yalnızca müvekkilin vekili ya da müdafii olan avukattan gelir — promptu ve talimatı veren avukat esastır; karşı taraf avukatı ve asil (karşı taraf da, müvekkil de) talimat kaynağı değildir. Ekleme m.11'in içindedir; vitrin nüshası, README, eklenti README ve SOZLUK aynı ilkeyi taşır (kilit: `tests/test_v0518_anayasa_m11.py`).

### E. Dış araç zinciri, bağımlılıklar ve Layer 0

- `udf-cli` 0.5.6 ve `docx2udf` 1.0.6 tek kaynak sabite bağlandı; `@latest` kalmadı.
- UDF teslimde Layer 0 zorunlu ve KATI ENGEL (avukat kararı, ölçüm sonrası: 911 gerçek UDF metninin 908'i taramadan geçmiyor) — bulgu varsa `--udf-yok` + UYAP editörü.
- `requirements.txt`: `pymupdf>=1.24.2` (görünürlük kâhininin gerektirdiği alt sürüm; testle kilitli).

### F. Kaynak tüketimi sınırları ve metin hijyeni

- Zip bombası (açılmış boyut beyanı), girdi seli, karesel düzenli ifade (40 KB'ta 3-16 sn → doğrusal) kapatıldı. Eklenti metinlerinde ham görünmez karakter yasak (testli).

### G. Sahipsiz yedek MCP ilanı kaldırıldı (B-23) ve UDF iç iz sızıntısı (B-19)

- v0.5.17.1 acil yamasıyla yayımlandı (aşağıdaki kayıt); bu sürüme birleştirildi.

### H. CI

- **CI bulgusu 2 (PR #8, üç bacak):** npm'in KENDİ önbellek hatası (eşzamanlı `npx -y`, ENOTEMPTY) da resmî okuyucunun dosya reddi sanılıyordu. Artık errno biçimli npm sistem çağrısı hatası ve olağan dışı çıkış kodu ve aracın kendi bağımlılığının bulunamaması (ERR_MODULE_NOT_FOUND) ortam hâlidir ("YAPILAMADI"); çalıştırılan aracın kendi başarısızlığı RET kalır (dar imler, kontrol testi + mutasyon kanıtı).
- **CI'nın yakaladığı iki üretim hatası (PR #8, yalnız 3.14 bacaklarında dönüşümlü kırmızı):** (1) `oa_ingest` — zehirli evrak işçiyi havuza gönderim sürerken öldürünce `submit` BrokenProcessPool fırlatıyor, gönderim korumasız olduğu için ana süreç TÜMDEN çöküyordu (tek evrak bütün klasörü okunmaz kılıyordu). Gönderilemeyen kalem artık çökmüş sayılır ve izole yeniden denemede kurtarılır. (2) `udf_yaz` resmî okuyucu — npx ya da kabuk udf-cli'yi hiç koşturamadığında (eşzamanlı `npx -y` önbellek yarışı, bozuk npx önbelleği, eksik Node; Türkçe Windows iletisi dahil) bu durum "resmî okuyucu REDDETTİ" sayılıp geçerli UDF GEÇERSİZ ilan ediliyordu. Artık başlatıcı hatası ortam hâlidir: "YAPILAMADI" görünür, dosya hakkında hüküm verilmez. Testler: `tests/test_oa_ingest_paralel.py::test_havuz_gonderimde_kirilirsa_ana_surec_cokmez_kalanlar_izole_kurtarilir`, `tests/test_udf_resmi_okuyucu.py::test_baslatici_hatasi_RET_degil_YAPILAMADI` (5 durum).
- Test matrisine Python 3.14 bacağı eklendi (avukatın makinesinde kancalar 3.14 ile çalışıyor); OCR işi `test_v0518_ocr.py`'yi de koşar (gerçek Tesseract testleri hiçbir işte koşmuyordu).
- **Yük altında titreyen GATE G testi (ürün değişmedi):** soru, CANLI-SENKRON kapısının 2 sn toleransının yavaş makinede sahte BAYAT üretip üretmediğiydi. Cevap: üretmez.
  - Kapı iki disk damgasını karşılaştırır: dosya-analiz.md ile `_oa/cikti`'daki en yeni çalışma evrakı. Bayatlığı geçen süre değil yazım sırası belirler.
  - `tam_tur --kaydet` kaydı en son yazar. Hiçbir tam_tur/pipeline komutu `_oa/cikti`'ya yazmaz; artık testle kilitli.
  - Kırmızının kaynağı testin kendisiydi: fikstür `--kaydet`ten SONRA `_oa/cikti`'ya yeni evrak yazıyordu. O anda kayıt gerçekten bayattı ve test ancak iki yazım 2 sn içinde kaldıkça geçiyordu.
  - Gerçek 2,5 sn gecikmeyle kanıtlandı: eski sıra CANLI-SENKRON ile RET, yeni sıra temiz.
  - Toleransı yükseltmek "onarım" değildir, gerçek bayatlığı gizler. Testle kilitli: beş mutasyonun beşi de yakalandı.
- **Testler deponun ortak `.pyc` önbelleğine dokunmaz (ürün değişmedi).** Yerel tam süitte (Python 3.14) sözdizimi kapısı, sağlam `tazelik_denetim.py`'yi "derlenmiyor" diye raporladı (`WinError 5`).
  - Kapı her betiği deponun `__pycache__`'ine derliyordu. Paralel işçilerdeki kanca alt süreçleri aynı `.pyc`'yi okurken Windows üzerine yazmayı reddetti.
  - Aynı sınıftan iki test daha vardı. Biri `hook_giris`'i oraya derliyordu. Öteki `pipeline_kayit`'in `.pyc`'sini siliyordu; `PYTHONDONTWRITEBYTECODE=1` ortamında (masaüstü uygulaması) kanca onu yeniden yazamadığı için hiçbir şey denetlemeden dönüyordu.
  - Üçü de artık kendi dizininde çalışır. Bayt kodu testi değişkeni alt süreçten çıkarır ve her ortamda gerçekten denetler. Yeni kilit testi kırmızıdan yeşile geçti; mutasyonla doğrulandı.

### I. Vitrin künyesi, kurulum prompt'u ve kapanış küçükleri (2026-10-08)

- **Künye ve ölçülmüş emek (avukat talimatı):** README ve eklenti README'sinin başında "Fikir ve dizayn babası: Av. Bayram Can ÇAPAR · Kâtip: Claude (Anthropic — Claude Code)" ve birlikte yazılan kodun satır sayıları. Sayılar elle yazılmaz: `tools/satir_sayaci.py` git'te izlenen dosyalardan sayar, aşağı yuvarlanmış alt sınır yazar (abartı yapısal olarak imkânsız); test sayısı OA-SUIT-SAYISI'ndan tam. `tests/test_v0518_satir_sayaci.py` künyenin biçimini, abartıyı ve bayatlığı kilitler; sayılar eskiyince `python tools/satir_sayaci.py --yaz`.
- **Kurulum motoru — tek prompt'luk zincirin proje içindeki kanıt halkası (avukat talimatı: "projenin içerisinde mutlaka zincirleme şekilde, Yargı Pro hariç kalan tüm gereksinimleri tek prompt'ta indirecek kısmı oluştur"):** `skills/ortak-avukat/scripts/oa_kurulum.py` Python'u, Python paketlerini (PyMuPDF alt sınırı `belge_guvenlik.PYMUPDF_ASGARI`'dan), Tesseract + `tur` dil verisini (PATH'te yoksa Windows standart yolunda), Node.js/npx'i, udf-cli girişini (ELİMDE — sürüm `udf_yaz.UDF_CLI_SURUM`'dan; motor ağa çıkmaz), eklenti bütünlüğünü (sürüm klasörü = plugin.json, 20 parça, dolu hooks.json, yetim `.orphaned_at` klasörü uyarısı), ilk çağrı derlemesini (`.pyc` tazeliği Python'un kendi başlık doğrulamasıyla; karma tabanlı pyc dahil) ve aile yapısını denetler; her gereksinimi tek satırda TAMAM / EKSİK / ELİMDE / BİLGİ diye yazar ve eksiğin resmî komutunu basar. `--uygula` yalnız koşan yorumlayıcıya pip paketlerini kurar ve compileall koşar; pip "externally-managed-environment" derse DURUR (sistem paketlerini zorlayan bayrak yok). Sistem yazılımını kurmaz; Yargı Pro KAPSAM DIŞI (ücretli üyelik — yalnız bildirilir). Çıkış: 0 tamam · 1 eksik · 2 kullanım. README prompt'unun 6. adımı motoru koşturur, eksiği onayla tamamlatır, motoru yeniden koşturur. Testler: `tests/test_v0518_kurulum.py` (30), `tests/test_v0518_master_prompt.py` +1.
- **Kurulum prompt'u (Görev 5 yeniden incelemesi Y-1, Y-2):** eski yedek bağlantı adı `claude mcp get` ile ağdan yoklanmaz (sahipsiz uç noktaya dokunulmaz) — önce öneri, onaydan sonra doğrudan `claude mcp remove`; tam yollu Tesseract doğrulaması kabuğunu söyler (`&` yalnız PowerShell'dedir, Git Bash karşılığı verildi).
- **Maliyet cetveli ifadesi (Görev 3 yeniden incelemesi KÜÇÜK-1):** vergi davasında kısmi kabulde ÜST banda eklenen bilinen maktu artık "ÜST SINIR" diye değil ÇIPA diye yazılır: maktu tarife TABANIDIR (AAÜT m.3/1 — üç katına kadar takdir); satır iki yönü de söyler (kısmi dağılımla düşük, takdirle yüksek olabilir). JSON anahtarı `maktu_ust_sinir` sözleşme olarak korundu.
- **Belge düzeltmeleri (Görev 2 yeniden incelemesi):** oa-antitez SKILL.md'de pipeline bekçisinin yalnız dosya adına baktığı (`cepheler` kuralı yalnız [G] kapısınındır), eski test docstring'i (Ruling 16: `--iskelet` şablonu damga taşımaz) ve dört motorun ortak atomik yazım docstring'i (kilitli geçici `.oa-tmp` kalabilir, `*.json` tüketicileri görmez).

### J. Gizli talimat ifşası Faz B — dilekçeye bağlama (2026-10-08)

- **Avukat talimatı:** "karşı tarafın gizli talimatı da ifşa edilsin, oluşacak dilekçeye girsin — siber hukuk güvenliği için". Kesin bulgu (karar BULGU) varsa ifşa bölümü dilekçeye VARSAYILAN olarak girer (oa-dilekce "İFŞA BÖLÜMÜ" pası). Bölüm olgusaldır; niyet/suç iddiası taşımaz, değerlendirme Mahkemenindir.
- **Dilekçe denetimi [İ] İFŞA** (advisory, çıkış kodu değişmez): bölüm yoksa, bayatsa, yer tutucu doldurulmadıysa, BULGU yokken bölüm varsa (yanlış ifşa riski) ya da denetlenemediyse görünür uyarı.
- **Bilinçli atlama:** `gizli_talimat_ifsa.py --kok <kök> --atla --gerekce "<gerekçe>"` — gerekçe zorunlu; kayıt ortak istisna defterine güncel bulgu parmak iziyle yazılır, bulgular değişince bayatlar ve uyarı geri gelir.
- **Teslim makbuzu:** `ifsa_durumu` alanı (bölüm dilekçede / bilinçli atlandı / bulgu yok / denetlenemedi …, künye sha8'iyle); teslimi durdurmaz.
- Ayrıntı: `plugins/ortak-avukat/skills/oa-ingest/references/gizli-talimat-ifsasi.md` §10. Test: `tests/test_v0518_ifsa_faz_b.py` (16).

### K. Belge güvenlik kapısı: iki XML çözücüsü tek kural, nüsha açığı kapandı (2026-10-08)

- **E-1 (fail-open kapandı):** Word evrakında birden çok `word/document.xml` nüshası varsa modele giden nüshadaki fark satırı damgalanır. Satır `A &amp; B` gibi XML varlığı taşıdığında çözülmüş gövdede bulunamıyor ve damgasız kalıyordu; kayıt yine "damgalandı" diyordu. Artık yerinde damgalanır; konumlanamayan satır evrakı VERİ diye sarar ve kayıt bunu açıkça söyler.
- **E-2:** iki modülde tek, kaynak-metin özdeş XML çözücüsü (XML 1.0 §4.1); çok uzun sayısal başvuru evrakı okunmaz kılmıyor. Açık-kapalı boş etiketler karaktere döner.
- **Önbellek:** yalnız DOCX kayıtları bir kez yeniden çıkarılır ve yeniden taranır (`DOCX_CIKARIM_SURUMU` 3); OCR'lı evrak yeniden okunmaz.
- Test: `tests/test_v0518_cozucu_birligi.py` (20).

### L. Zincir tüketicileri sıkılaştı (2026-10-08)

- **Kısmi kaynak beyanı "taze" sayılmaz:** bir halkanın denetim JSON'u girdisini beyan edemediyse (dosya okunamadı) bu DURUM.md'de ve makbuzda EKSİK-KAYNAK olarak görünür; eskiden "TAZE" deniyordu.
- **Graf kapısı gerçek çevrimi gizlemez:** okunamayan bir denetim dosyası ile gerçek bir dairesel illiyet aynı anda varsa RET mesajı ikisini de söyler; şerhle geçişte şerh metni de ikisini taşır.
- **Tek satır disiplini:** bayat zincir ve makbuz tazelik satırlarına satır sonu ya da damga taklidi sızamaz (R5).
- **Zincir uçtan uca sınandı:** gerçek motorlar sentetik bir dava kökünde birlikte koşar (`tests/test_v0518_zincir_butunlesme.py`; yedi mutasyonla kanıtlı):
  - künye değişince üç denetim (vakıa, graf, kıyas) BAYAT olur; bu DURUM.md'de ve makbuzda görünür, teslim durmaz;
  - antitez damgası yalnız denetim çıktısında bulunur, sahte "sağlıksız" satırı çıkmaz;
  - yarım kalmış graf denetimi adım 1'i RET eder; atomik yazımın geçici dosyası yanlış RET üretmez.

### M. Fable bağımsız denetimi — doğrulanan bulgular kapandı (2026-10-08)

Avukat talimatı: "Fable denetçi olarak incelesin." Yedi salt okunur Fable 5.1 denetçisi (her biri en çok 4 dakika) dalın en riskli alanlarını inceledi. Her bulgu ana oturumda yeniden üretildi ya da çürütüldü; düzeltmeler önce kırmızı testle yazıldı.

**Teslim ve güvenlik:**
- **Dava kökündeki program çalıştırılmaz (güvenlik):** Windows'ta `shutil.which` aramaya çalışma dizinini öne koyuyordu. Araçlar dava kökünde koştuğundan karşı tarafın evrakıyla gelen bir `npx.cmd`, `tesseract.bat` ya da `node.bat` çalıştırılabilirdi; denetçi kanıtladı. Dört betik (udf_yaz, udf_metin, oa_ingest, oa_kurulum) programı tek, özdeş bir yardımcıyla çözer.
- **UDF resmî okuyucu — bu dalın gerilemesi kapandı:** CI düzeltmesi 2'deki `npm warn cleanup` imi yalnız bir UYARI satırıydı ama gerçek reddi "YAPILAMADI"ya çevirip geçersiz UDF'yi teslime açabiliyordu. İm kaldırıldı; o CI vakası çıkış kodu kuralıyla zaten yakalanır. İmler artık yalnız stderr'de aranır ve "ağ" sözcük sınırlıdır ("aşağıdaki" ortam hatası sayılmaz).
- **Doğrulanamayan UDF görünür:** html2udf yolu da `.DOGRULANMADI` işareti bırakır (okuyucu OK deyince bayat işaret kalkar). Teslim makbuzu işareti taşır ve sonuç satırı "TESLİME HAZIR — ⚠ UDF resmî okuyucuyla DOĞRULANAMADI" diye nitelenir; teslim durmaz, karar avukatın.
- **Tazelik denetimi koşamazsa** teslim çıktısında "DENETLENEMEDİ" satırı görünür (eskiden "temiz" ile ayırt edilemiyordu).
- **Kurulum motoru** `markitdown[all]` ekinin Office dönüştürücülerini (mammoth, openpyxl, python-pptx) de denetler.
- Test: `tests/test_v0518_fable_teslim_guvenlik.py`; kurulum: `tests/test_v0518_kurulum.py`.

**Süre hesabı:**
- **Kuralsız hesap artık GEÇ tarih üretmez:** `--kural` verilmeden hukuk/idari usul süresi hesaplanınca HMK m.104 / İYUK m.8/3 uzatması TEYİTLİ sayılıyordu. İki hüküm yalnız kendi kanunlarının sürelerine uygulanır; süre İİK, İş Kanunu, TBK ya da Av.K. kaynaklıysa ya da hâkimin verdiği süreyse uzamaz. Örnek: 01.08 tebliğ, 15 gün → doğrusu 17.08 olabilirken motor 07.09 diyordu. Manşet artık erken tarih; uzamış okuma ayrıca görünür. Ceza kolu bilerek dışarıda (CMK m.331/4 sınırsız; tatil içi tebliğde ihtiyat planı zaten var).
- **Sınır hâli:** ham bitiş tatilden önceyken son gün kaymasıyla 20 Temmuz'a düşerse uzatma okuması gösterilir; manşet erken kalır.
- **Arife:** son gün bayram arifesiyse "fiziki işlemi öğleden önce tamamla" uyarısı basılır (2429 s.K.; arifeler tablodaki bayramlardan türetilir, tahmin yapılmaz).
- **Parasal kesinlik** uyarısı yalnız istinaf ve temyiz kurallarında basılır (alarm yorgunluğu).

**Künye teyidi (dördü v0.5.17.1'de de vardı; kapının "teyitsiz atıf → exit 1" sözleşmesini çiğniyordu):**
- **İki kararın parçası** (bir kararın esası + ötekinin kararı) ve **esas–karar yer değiştirmiş** künye artık TEYİTLİ sayılmaz: iz, taslakla aynı ayrıştırıcıdan geçirilir ve çift karşılaştırılır. Ayrıştırıcının tanımadığı döküm biçimlerinde (ör. markdown kalın başlık) bugünkü sayı eşleşmesi korunur.
- **Farklı daire:** izde aynı esas/karar başka bir daireye aitken künye artık TEYİTSİZ ve rapor "MERCİ ÇELİŞKİSİ" der (E/K her dairede yılda sıfırdan başlar). İzde hiç daire yoksa eski uyarı sürer.
- **AYM başvuru numarası** yalnız AYM bağlamı olan izle eşleşir (Yargı PRO'nun "BB 2015/53" biçimi dahil); bir Yargıtay esas numarası AYM kararını teyit etmez.
- Test: `tests/test_v0518_fable_sure_kunye.py`; iki kontrol testinin değeri mutasyonla kanıtlandı.

**Belge güvenlik kapısı (kapı sürümü 1.2; önbellekteki 1.1 kayıtları bir kez yeniden taranır):**
- **Öznitelik sırası:** DOCX desenleri `w:val`'ı ilk öznitelik sanıyordu. `<w:color w:themeColor="background1" w:val="FFFFFF"/>` gibi şema-geçerli bir yazımla beyaz, 1 punto, gizli, %5 ölçekli ya da sıkıştırılmış yazı damgasız geçiyordu. Artık öznitelikler sıradan bağımsız okunur; tema rengi varken Word'ün yaptığı gibi o esas alınır. Aynı kural stil başvurularında da geçerli.
- **Alternatif içerik:** Word 2010+ `mc:Choice`'u çizer, `mc:Fallback`'i göstermez; çıkarıcı ise ikisini de modele verir. Choice'ta olmayan Fallback metni artık gizli katman sayılır. Meşru yedek (aynı metin) alarm üretmez.
- **Açılamayan evrak "temiz" sayılmaz:** ZIP olarak açılamayan ya da ana belgesi olmayan DOCX'te, açılamayan ya da parolalı PDF'te, dizini bozuk ya da ne ZIP ne XML olan UDF'te tarama sessizce dönüyordu. En somut hâli: merkez dizini bozuk UDF'te çıkarıcı içeriği ham deflate ile kurtarıp modele veriyor, kapı ise arşivi açamayınca hiçbir şey demiyordu; beyaz, 1 puntoluk yük damgasız geçiyordu. Artık karar DENETLENEMEZ, gerekçe görünür ve denetlenmemiş metin VERİ diye sarılır. Sınır aşımında da metin artık sarılır.
- **İmzalı nüsha (bu doğrulamada bulundu):** imzalı UDF nüshalarında prolog öncesi BOM ya da boşluk görülür. Çıkarıcı bunu silip okurken kapı silmeden ayrıştırıyor ve gizli katman taramasını sessizce atlıyordu. Kapı artık çıkarıcıyla aynı toleransı taşır; gerçekten bozuk XML DENETLENEMEZ olur.
- Test: `tests/test_v0518_belge_guvenlik.py` (+20).

**OCR kritik alan teyidi (belirsizlik gizlenmez):**
- **Kesme görünür, tür kaybolmaz:** liste ilk 30 kalemde sessizce duruyordu. Tarama sırası tarih → esas/karar → TCKN → IBAN olduğundan 30 şüpheli tarih kotayı doldurunca IBAN ve TCKN şüphesi hiç görünmüyordu. Karma PDF'te kesme sayfa süzgecinden önce yapıldığı için OCR sayfasının kalemi de kaybolabiliyordu. Artık her türden en az bir kalem korunur, süzgeç kesmeden önce gelir; kesilince md, künye (`dogrulama_kesildi`) ve DURUM.md gerçek toplamı ve "KESİLDİ" notunu gösterir.
- **Çöken teyit "şüphe yok" değildir:** teyit çökünce hata yutuluyor, künyede alanın olmaması "şüpheli alan yakalanmadı" diye okunuyordu. Artık künyede `dogrulama_denetlenemedi`, md'de 🔴 satırı, DURUM.md'de "teyidi YAPILAMADI" görünür.
- Test: `tests/test_v0518_fable_ingest_belirsizlik.py` (10); iki kontrol testinin değeri mutasyonla kanıtlandı.

### N. Halüsinasyon kapısı — dört motor artık koşmak zorunda (saha testi, 2026-10-09)

Saha testi (gerçek bir icra hukuk dosyası, istinaf dilekçesi; kimlik bilgisi kayda geçirilmedi): eklenti GitHub'daki sürümle dosya dosya özdeş kuruldu, oturum yerel sensörlerle izlendi. Vakıa, illiyet, antitez ve kıyas motorları (ve çapraz denetim) kurulu ve sağlamdı — duman testinde beşi de exit 0 ve damgalı çıktı verdi — ama oturumda **hiç koşmadı**. Dilekçe uydurmadı ama seçici anlattı: lehe gösterilen bir kararın üst mahkemece kaldırıldığı yazılmadı; antitez matrisinin "aleyhe akıbet" cephesinin yakalayacağı türden bir eksik. Yazılım mühendisi + hukukçu kimliğiyle danışılan Fable 5.1'in teşhisi: zincirde motoru çağıran deterministik bir halka yok; kapılar "çıktı var mı" sorar, "motor koştu mu" sormaz. Modelin kendi yazdığı .md dosyası, kanıtta "script" kelimesi ya da BILGI-EKSIK statüsü kapıları açıyordu.

- **Kanıt metin değil, disk:** `oa-vakia`, `oa-illiyet`, `oa-antitez` ve `oa-kiyas` için UYGULANDI artık yalnız motorun KENDİ yazdığı `arac` damgalı, çökmemiş ve taze (tazelik denetiminin BAYAT hükmü) denetim JSON'u varken kalır; yoksa ELDEN'e düşer ve mesaj çalıştırılacak tek komutu gösterir.
- **Dilekçe adımı (adım-8):** dört motorun damgası yokken RET. Yalnız gerekçeli avukat şerhiyle geçilir: `--serh "…" --serh-kapi halusinasyon` (ya da `tumu`).
- **Teslim (c2) kapısı:** (c)'den sonra, (d)'den önce. Statüye değil diske bakar; BILGI-EKSIK ya da GEREKSIZ yazmak onu açmaz (sahada bu desen beş kez görüldü). Şerhli geçiş istisna defterine gerekçesiyle yazılır; makbuzda yeni `halusinasyon_kapisi` alanı. Defter yoksa (d) gibi bilgi verir, sormaz.
- **Motor köprüsü (yeni `oa-pipeline/scripts/motor_koprusu.py`):** dört motoru ve çapraz denetimi tek komutla koşturur. Damgayı motor yazar, köprü hiçbir dosyaya damga koymaz. Girdi yoksa motoru koşturmaz; vakıa ve antitez için motorun kendi şablonunu UTF-8 yazar (Windows PowerShell 5.1'de `>` yönlendirmesi UTF-16 yazıp dosyayı motora okunmaz kılıyor), var olan dosyanın üzerine asla yazmaz, doldurulmamış şablonu doğrulatmaz. Çapraz denetim en az iki girdiyle koşar (tek girdiyle "tutarlı" demek yanıltıcıdır). Model araç çantasını `_oa/araclar`'a düz kopyalasa da motorları bulur.
- **Şerh gerekçesi kayda girer:** `--serh` metni eskiden deftere yazılmıyordu, yalnız kapının kendi mesajı yazılıyordu. Artık olayda `serh_gerekce` alanı var.
- Motorun **bulgusu** (ispat boşluğu, açık cephe, kritik kıyas boşluğu) kapıyı kapatmaz; yalnız "motor koştu mu" sorulur, hüküm avukatındır (kıyas çıkış kodu kararı, 2026-08-12, korunur).
- Hook sıcak yoluna yeni import ya da hesap girmedi.
- Test: `tests/test_v0518_halusinasyon_kapisi.py` (24; sonradan eklenen dört davranış mutasyonla kanıtlandı). Zincirin başka halkasını sınayan eski testler motorların koştuğu dünyayı `tests/oa_motor_damga.py` fikstürüyle kurar; amaçları değişmedi.

### O. Sahada görülen anayasa aykırılıkları giderildi; avukatın lafız kuralı (2026-10-09)

Avukat talimatı: "anayasa aykırılıklarını da gider", "sisteme uy". Saha testinde gözcü heyeti, model davranışından bağımsız olarak sistemin kendisinin anayasaya aykırı işlediği dört yer buldu. Teşhisler Fable 5.1'in koddan çıkardığı kanıtla örtüştü. Her onarım önce kırmızı testle yazıldı.

- **Avukat onayı uydurulmaz (anayasa m.9, m.8):** karşı tarafın gizli talimatını dilekçeye almama kararı her durumda "avukat onayladı" diye kaydediliyordu; sahada bu kararı model vermişti. Artık kayıt kararın gerçek sahibini yazar: avukat açıkça karar verdiyse `--onay avukat`, aksi hâlde "model beyanı" — dilekçe denetimindeki uyarı açık kalır. Onarım ilk hâlinde ileriye dönüktü: bayraktan önce yazılmış kaydın "avukat" etiketi (saha dosyasındaki dahil) uyarıyı susturmaya devam ediyordu. O etiket artık kanıt sayılmaz (yazıcı sürümü 1.2); kayıt silinmez, uyarı geri gelir ve nedenini söyler.
- **Kapıyı model açamaz — dilekçe denetiminde yanlış pozitif ilanı (anayasa m.9, m.8; G-5'in kardeşi, bu denetimde bulundu):** [Y] (havada kalan alıntı) ve [T] (makbuzsuz hazır beyanı) kapısını düşüren ilan, kimin yaptığına bakmadan "avukat onayı" diye kaydediliyordu; kapıyı model de açabiliyordu. Artık yalnız `--istisna-onay avukat` düşürür; onaysız ilan model beyanı olarak kayda geçer, BLOK sürer. Desen depoda zaten vardı (`gizlilik_tara.py --override-onay avukat`).
- **Okunamayan evrak kaybolmaz (anayasa m.1 — veri kayıpsızlık):** OCR'ın okuyamadığı altı ayrı evrak ortak yer tutucu yüzünden "aynı içerik" sayıldı; beşinin kaydı ve avukatın sayfayı gözle okuyabileceği görselleri hiç oluşmadı. Artık okunamayan evrak tekrar-elemeye girmez; eski kusurla kaydedilmiş evrak bir kez yeniden okunur.
- **Gizlilik süzgeci dış aracı çağıran yerde koşar (anayasa m.10):** UDF'e çeviren araç (udf-cli) dış araçtır. Süzgeç yalnız teslim zincirinin içinde soruluyordu; sahada teslim UDF'siz alındıktan sonra UDF doğrudan üretildi ve metin süzgeçten geçmeden dışarı gitti. Artık süzgeç, içeriği dışarı gönderen betiğin içinde, dışarı fiilen giden metne uygulanır (iç kaynakça bloğu B-20 gereği dışarı gitmediği için taranmaz). Kişisel veri varsa UDF üretilmez ve avukatın 2026-10-05 kararındaki yol gösterilir: UDF yerelde UYAP editöründe üretilir. Resmî okuyucu da aynı kurala tabidir.
- **Mühür doğru sürümü yazar (anayasa m.5):** ürün mühürleri her ürünü "v0.5.8 (fork-prova)" üretmiş gibi damgalıyordu. Sürüm artık tek kaynaktan okunur; okunamazsa yanlış sürüm değil "sürümü okunamadı" yazılır.
- **Avukatın lafzı — şapkalı harf yok:** dilekçede â yerine a, î yerine i (hâkim → hakim, resmî → resmi). Birebir alıntıya dokunulmaz; alıntıyı değiştirmek tahriftir. Kural oa-dilekce'nin "Yazar sistemi ve lafzı" bölümüne işlendi; dilekçe denetiminde [Ş] uyarısı (bloklamaz).
- Açık kalan (v0.5.19): teslim makbuzunun nihai UDF'in özetini taşıması ve UDF'siz makbuzun "ara" sayılması (G-11'in makbuz yüzü); karar dökümünün araç çağrısına bağlanması.
- Test: `tests/test_v0518_anayasa_onarimlari.py` (19; G-6 bağı mutasyonla kanıtlı), `tests/test_v0518_sapka_kurali.py` (8), `tests/test_v0585_dilekce_kurallari.py` (yanlış pozitif ilanı: +1, iki test bilinçli sözleşme değişikliğiyle güncellendi).

### P. İkinci saha testi: ceza dosyası; avukat hükmü uydurulmaz (2026-10-09)

Avukat talimatı: ikinci bir gerçek dosyada (ceza) sistem başsız bir Sonnet oturumuyla sınansın. Gerçek bir ceza dosyasının asıl evrakı (binden fazla evrak; kimlik bilgisi kayda geçirilmedi) bulut dışı bir test köküne kopyalandı; başsız bir Sonnet oturumu kısa bir avukat talimatıyla, dış bağlayıcılar ve web kapalıyken koştu (69 dakika).

- Bu sürümün onarımları sahada çalıştı: dört motor ve çapraz denetim koştu, damgaları motorlar yazdı, teslim (c2) "OK"; ifşa atlaması "model beyanı" diye kaydedildi ve uyarı açık kaldı (G-5); UDF'i doğrudan üretme denemesini Layer 0 çağrı yerinde durdurdu (çıkış 6); dilekçede şapkalı harf yok; okunamayan sayfalı sekiz evrak ayrı ayrı görünür kaldı (G-8); künye kapısı teslimi durdurdu, dosyanın kendi geçmişine ait numaralar otomatik kuralla muaf tutuldu.
- **Avukat hükmü uydurulmaz (anayasa m.9, m.8):** model teslimden sonra avukat hükmü defterine kendisi "KABUL" yazdı; kayıt avukat hükmü sayıldı ve A-28 sensörünü (SICRAMA-NOTU §5'in tek başarı ölçütü) zehirledi. Artık kayıt sahibini yazar: varsayılan model beyanıdır, sayaca girmez; avukat hükmü yalnız `--hukum-onay avukat` ile sayılır. Onay alanı olmayan eski kayıt da varsayılmaz; ikisi de DURUM.md'de ayrı satırda görünür, hiçbir satır silinmez.
- **Okunmayan evrak sessiz kalmaz (anayasa m.1):** sistem yüzlerce Excel tablosunu metne çeviremedi ve bunu yalnız "bilinmeyen/elle" sayısında gösterdi. Alım özeti artık okunmayan türleri adı ve sayısıyla uyarı satırına yazar ("içerikleri analize GİRMEDİ; elle incelenmeli").
- Kapatılmayan, karar bekleyen bulgular (testten sonra; yöntem gereği test sürerken özellik eklenmedi): Excel'i metne çeviren okuyucu (belge güvenlik kapısıyla birlikte tasarlanmalı: gizli sayfa ve satır, beyaz yazı); teslim makbuzunun kapsadığı PDF ile diskteki PDF'in farkı hiçbir kapıda yakalanmıyor (dosya makbuzdan sonra değişti); kesilen evrak alımı kaldığı yerden sürmüyor; avukat şerhinin sahibi kayıtta ayrılmıyor (model şerhi avukat şerhi gibi duruyor); atıf olmayan dilekçede kıyas adımı yine içtihat muhakeme kaydı isteyip modeli şerhe itiyor; modelin kendi yazdığı yardımcı analizler kanıt zincirinin dışında kalıyor. Q'da kapatılanlar: Excel okuyucu (kapıyla birlikte), makbuz–ürün farkı, şerhin sahibi, atıfsız kıyas. v0.5.19'a kalanlar: kesilen alımın kaldığı yerden sürmesi, yardımcı analizlerin kanıt zincirine bağlanması.
- Test: `tests/test_v0516_B.py` (yeni `test_a28_model_beyani_hukum_avukat_hukmu_sayilmaz_ve_gorunur`; avukat yolunu sınayan testler `--hukum-onay avukat` alır), `tests/test_v0518_anayasa_onarimlari.py` (okunmayan tür uyarısı).

### Q. Saha testlerinden kalan eksikler tamamlandı (2026-10-11 → 10-12)

Avukat talimatı: "bir avukat olarak eksikleri tamamla". P'de karar bekleyen bulgular ve Fable 5.1 denetiminin açık bıraktıkları. Her onarım önce kırmızı testle yazıldı; test verisinin tamamı kurgudur.

- **Şerhin sahibi kaydedilir (anayasa m.9, m.8):** avukat yokken model kıyas kapısını kendi şerhiyle geçti; defter şerhin kimden geldiğini yazmıyordu. `--serh-onay` artık şerhin sahibini kaydeder. Varsayılan model beyanıdır ve kalem DURUM.md «Avukat Kararı Bekleyen» bölümünde "model şerhi; avukat onayı yok" diye kalır. Halüsinasyon kapısını (vakıa, illiyet, kıyas ve antitez motorları) yalnız avukat şerhi açar. Teslim (c2) kapısı model şerhini de sahibi kayıtsız eski şerhi de kabul etmez.
- **Avukat kararını model veremez (anayasa m.9):** «Avukat Kararı Bekleyen» kalemi modelin yazdığı kararla da kapanabiliyordu. `--karar-onay avukat` olmadan yazılan karar artık "model önerisi" olarak kaydedilir ve kalemi kapatmaz. Onay alanı olmayan eski kayıtlar kalemi kapatmaya devam eder; geriye dönük kayıp yoktur.
- **Kıyas yalnız norma dayanıyorsa muhakeme kaydı aranmaz:** atıfsız dilekçede kıyas adımı içtihat muhakeme kaydı isteyip modeli şerhe itiyordu. Büyük önermede içtihat yoksa kayıt aranmaz; içtihat varsa aranmaya devam eder.
- **Makbuz ile ürün ayrışmaz ("kanıtla yazılır"):** sahada teslim makbuzundan sonra değişen PDF'i hiçbir kapı yakalamadı. Teslim adımı artık makbuzdaki her teslim ürününün özetini diskteki dosyayla karşılaştırır. Makbuzdan sonra değişen ürün varsa adım kapanır ve `teslim_paketi.py` yeniden istenir. E-imzalı UDF türevdir; imza eklemek kapıyı kapatmaz.
- **Graf kapısı açık kalmaz (Fable P4):** graf sorgusu çöktüğünde kapı açık dönüyordu. Artık "graf DENETLENEMEDİ" diyerek kapalı kalır.
- **Teslim, bekleyen avukat kararını söyler:** teslim çıktısında yeni bir [ak] bölümü var. "TESLİME HAZIR" satırı bekleyen kalem sayısıyla nitelenir; makbuz `avukat_karari_bekleyen` alanını taşır. Liste okunamazsa sonuç satırı "DENETLENEMEDİ" der. Teslim durmaz; karar avukatındır.
- **Excel evrakı okunur (anayasa m.1, m.11):** ceza saha testinde Excel tabloları hiç okunmamıştı.
  - Tablo sayfa sayfa, satır satır metne çevrilir. Tarih ISO biçimine çevrilir; değer düzeltilmez, kırpılmaz.
  - Gizli sayfa okunur ve damgalanır.
  - Belge güvenlik kapısı tabloyu DENETLENEMEZ diye sarar, çünkü gizli satır/sütun ve yazı rengi bu sürümde ölçülmüyor. Gizli sayfadaki talimat dili BULGU'dur.
  - Okuyucu kurulu değilse evrak "OKUNMADI" diye işaretlenir. Kurulum betiği openpyxl ve xlrd'yi kurar.
  - Boyut beyanı (`<dimension>`) bayat tabloda satır kaybolmaz (bu makinede 6 satırın 2'si okunuyordu); arşiv (EYP/ZIP) içindeki Excel de okunur; Excel desteğinden önce önbelleğe alınmış arşiv bir kez yeniden açılır. Üçünü bağımsız antitez turu (Fable 5.1) buldu; kırmızı testle kapatıldı.
  - Bağımlılık anayasa m.0'ın devşirme süzgecinden geçti: openpyxl (MIT, tek bağımlılığı et_xmlfile) ve xlrd (BSD, bağımlılıksız) saf Python, ikili dosya yok, eksikse fail-closed. Dört yol tartıldı: kendi ayrıştırıcı (.xls ikili biçiminde sessiz yanlış okuma riski), vendor (ağır), almama (tablolar okunmaz, m.1), kütüphane. Kütüphane seçildi.
- **Açılamayan evrak adıyla söylenir (m.1):** bozuk, parolalı ya da uzantısı türüyle uyuşmayan evrak yalnız 00-INDEX'te ⚠ satırı olarak kalıyordu; konsolu okuyan model onu görmüyordu. Alım artık "UYARI (AÇILAMAYAN EVRAK)" satırını türü ve sayısıyla basar. Excel desteklenince bozuk tablolar «desteklenmeyen tür» uyarısından çıkıp bu sessizliğe düşmüştü; onarım o gerilemeyi de kapatır.
- **Uzun alım önceden söylenir (m.1):** yaklaşık 1.100 evraklık alım yaklaşık 27 dakika sürdü. Ön planda koşan alım kesilirse baştan başlar, çünkü önbellek koşu sonunda yazılır. 200'den fazla evrak çıkarılacaksa alım, çıkarımdan önce süre tahminini ("tahmin:") basar. Uyarı, alımın arka planda ve en az iki kat zaman aşımıyla koşturulmasını söyler. Kaldığı yerden süren alım v0.5.19 işidir.
- **Kaynakça, künye kapısıyla aynı gözle bakar (B-3 tek kaynak):** iç kaynakça bloğu, dosyayla ilgili bir hukuk davasının esas numarasını "teyit edilmemiş içtihat" sandı. Aynı körlük taslağın kendi "DOSYA NO" satırında da vardı. Kaynakça artık künye kapısının iki muafiyetini aynı kaynaktan uygular:
  - davanın beyan edilmiş geçmişi ayrı alt başlıkla, teyit beyanının dışında görünür;
  - taslağın kendi dosya numarası listelenmez;
  - aynı numara bir yüksek mahkeme kararı olarak da anılıyorsa muafiyet uygulanmaz.
- **Hook katmanı Windows Mağaza kısayolunda ölmez:** yeni bilgisayarda PATH'teki ilk `python`, Microsoft Store'un yer tutucusuydu (çıkış 49). Kurulu eklentinin altı hook olayının altısı da sessizce ölüydü. Sarmalayıcı (`run-hook.cmd`, cmd ve bash kolu) artık WindowsApps kısayolunu atlar; başka yorumlayıcı yoksa kısayolu son çare olarak dener; bash kolunda PATH genelinde önce python3 aranır (eski dağıtımda önceki dizindeki Python 2 seçilmesin). `||` yasağına uyuldu. Sarmalayıcı artık saf ASCII'dir: konsol kod sayfası UTF-8 (65001) iken cmd, LF satır sonlu dosyadaki çok baytlı karakterin (REM satırındaki uzun tire) ofsetini yanlış sayıyor ve REM yorumunun parçalarını komut diye çalıştırıyordu. Bu makinede ölçüldü; sistem genelinde UTF-8 kullanan Windows'ta kanca ölürdü.
- Testler:
  - yeni: `tests/test_v0518_eksikler.py` (27), `tests/test_hook_sarmalayici.py` (+5), `tests/test_v0518_kurulum.py` (+1);
  - bilinçli sözleşme değişikliğiyle güncellenenler:
    - `test_durum_md.py`: `--karar-onay avukat`;
    - `test_pipeline_kayit_onkosul.py` ve `test_v0518_halusinasyon_kapisi.py`: `--serh-onay avukat`;
    - `test_v0518_anayasa_onarimlari.py`: G-8 eki artık gerçekten desteklenmeyen türlerle koşar.

### R. Çırak dersleri: ceza saha testinden sekiz ders playbook'lara (2026-10-12; avukat onayıyla)

oa-usta'nın hata tetikli damıtma kuralı gereği aday kurallar saha raporunda ilk görünüşte yazılmıştı; kurala dönüşmeleri avukat onayına bağlıydı. Dayanak gösterilen hükümler resmî metinden okundu (Yargı PRO `mevzuat_getir`, 2026-10-12): Teb.K. m.7/a 4. fıkra, HMK m.344/1, HMK m.94/2-3.

1. **Akıbet olgunun parçasıdır** (oa-vakia, oa-antitez, oa-kontrol): lehe gösterilen her karar ve evrakın akıbeti aranır. Mekanik bayrak v0.5.19 adayıdır.
2. **Tanık iki sütunla çıkarılır** (oa-vakia, oa-dilekce): ne dedi, ne demedi. Tanıkla sabit kısım müvekkil beyanından ayrı yazılır.
3. **Mutlak ifadeye karşı örnek aranır** (oa-vakia, oa-kontrol): "hiç / tek / hiçbiri" için evrakta karşı örnek aranır, görsel evrak dahil.
4. **Elektronik tebligatta iki tarih yazılır** (oa-sure, oa-usul, oa-dilekce): ulaşma tarihi ve tebliğ sayılma tarihi, ardından "süresindedir" cümlesi.
5. **İstinafta harç ve gider avansı satırı yazılır** (oa-dilekce, oa-usul): eksiklikte bir haftalık kesin süre verilir, tamamlanmazsa başvuru yapılmamış sayılır.
6. **Farklı türde emsal "kıyasen" kullanılır** (oa-kiyas, oa-ictihat): fark açıkça söylenir.
7. **Karşı vekilin kesin süreden sonraki beyanı usul taarruzudur** (oa-usul). Taarruz önce hâkimin ihtarını denetler; ihtar yoksa süre kesin değildir.
8. **Aynı kaynağın iç çelişkisi iki yönlü not edilir** (oa-vakia, oa-antitez).

- Dokuzuncu aday (dilekçede bağlantı olmasın) avukatın v0.5.7.5 bağlantı kuralıyla çeliştiği için işlenmedi; kural yürürlükte. Onuncu aday (motor koşmadan dilekçe yok) N'de uygulanmıştı.
- SICRAMA-NOTU §1'e düzeltme dipnotu eklendi: "mekanik iskelet tamamlanmıştı" cümlesi model tarafı için erken söylenmişti; iskelet vardı, çağıran halka yoktu.

### Davranış değişiklikleri (güncelleyenler için)

- **B-23:** v0.5.7.4'teki yedek MCP kararı tersine çevrildi — tek içtihat bağlayıcısı Yargı PRO; yoksa otomatik geçiş yok, "teyit YAPILAMADI".
- **Görünürlük kâhini:** PDF'te gizli yazı kararı artık sayfa görüntüsüne dayanır; önceden gizli sayılan bazı görünür başlıklar artık temiz, önceden kaçan çizgili örtü ve saydam yazı artık BULGU.
- **UDF teslimde Layer 0 katı engel** (yukarıda E).
- **Özne eşleştirici:** yalnız yazım eşdeğerliğinde birleştirir; aynı soyadlı farklı ön adlar ayrı kişidir; OCR varyantları ve yazım farkları avukata soru olarak gelir.
- **AİHM süresi:** her dosyada dört ay (D).
- **Kuralsız süre hesabı (M):** `--kural` verilmeyen hukuk/idari usul süresinde adli tatil uzatması artık manşete konmaz; manşet erken tarih, uzamış okuma ayrıca görünür. HMK ya da İYUK'un kendi süresi için `--kural` ile hesaplayın.
- **Künye teyidi (M):** izde aynı esas/karar FARKLI daireye aitse künye TEYİTSİZ olur (eskiden yalnız uyarı + exit 0). İki kararın parçasından oluşan ya da esas–karar yer değiştirmiş künye teyitli sayılmaz.
- **Teslim sonuç satırı (M):** UDF resmî okuyucuyla doğrulanamadıysa "TESLİME HAZIR — ⚠ … DOĞRULANAMADI" diye nitelenir; teslim durmaz.
- **Belge güvenlik kapısı 1.2 (M):** önbellekte 1.1 ile işaretli evrak bir kez yeniden taranır (OCR'lı kayıtta yalnız md metni; bulgu ya da şüpheli alan varsa tam yeniden çıkarım). Açılamayan, parolalı ya da yapısı bozuk evrak artık "temiz" değil DENETLENEMEZ görünür.
- **Kritik alan listesi (M):** 30'dan fazla şüpheli alanda liste her türü korur; md ve DURUM.md gerçek toplamı ve "KESİLDİ" notunu gösterir.
- **Halüsinasyon kapısı (N):** vakıa, illiyet, antitez ve kıyas için UYGULANDI ile dilekçe adımı artık motorun kendi damgasını ister; teslimde yeni (c2) kapısı var. Motorlar koşmadıysa RET; tek komut `python <eklenti>/skills/oa-pipeline/scripts/motor_koprusu.py --kok <dava kökü>`; bilinçli geçiş yalnız gerekçeli avukat şerhiyle (`--serh-kapi halusinasyon`). Adımları BILGI-EKSIK ya da GEREKSIZ yazmak teslim (c2) kapısını açmaz.
- **İfşa atlama (O):** `gizli_talimat_ifsa.py --atla` kaydı varsayılan olarak "model beyanı"dır ve uyarıyı susturmaz; avukat kararı `--onay avukat` ile kaydedilir. 1.1 imzalı eski kayıttaki "avukat" etiketi model beyanı sayılır.
- **Yanlış pozitif ilanı (O):** `dilekce_denetim.py --istisna-gerekce` artık tek başına [Y]/[T] BLOK'unu düşürmez; avukat onayı `--istisna-onay avukat` ile verilir. Onaysız ilan kayda geçer, BLOK sürer.
- **Avukat hükmü (P):** `pipeline_kayit.py --avukat-hukmu` kaydı avukat hükmü sayılmak için `--hukum-onay avukat` ister; onaysız kayıt model beyanıdır. Önceki sürümlerde onay alanı olmadan yazılmış hüküm kayıtları sayaçta ayrı satıra geçer; avukat hükmüyse `--hukum-onay avukat` ile yeniden işlenir.
- **UDF üretimi (O):** kişisel veri (gizlilik süzgeci strict: DENY ya da ASK) taşıyan metin udf-cli/docx2udf'e gönderilmez — `udf_yaz.py` çıkış 6 verir; UDF yerelde UYAP editöründe üretilir. Resmî okuyucu böyle bir UDF için "YAPILAMADI (Layer 0)" der.
- **Dilekçe yazımı (O):** şapkalı â ve î kullanılmaz (a, i); dilekçe denetimi [Ş] uyarısı basar.
- **Şerh (Q):** `pipeline_kayit.py --serh` kaydı varsayılan olarak model şerhidir. Halüsinasyon kapısını ve teslim (c2) kapısını açmak için `--serh-onay avukat` gerekir. Diğer kapılarda model şerhi geçer, kalem «Avukat Kararı Bekleyen»de kalır.
- **Avukat kararı (Q):** `--avukat-karari` kaydı `--karar-onay avukat` olmadan model önerisidir ve bekleyen kalemi kapatmaz.
- **Teslim adımı (Q):** makbuzdan sonra değişen teslim ürünü varsa adım-9 kapanır; `teslim_paketi.py` yeniden koşulur.
- **Excel (Q):** `.xlsx`, `.xlsm` ve `.xls` artık metne çevrilir. Yeni bağımlılıklar `openpyxl>=3.1` ve `xlrd>=2.0` (`requirements.txt`). Bunlar kurulu değilse evrak "OKUNMADI" olur.
- **Alım uyarıları (Q):** 200'den fazla evrak çıkarılacaksa "UYARI (UZUN ALIM)" basılır. Açılamayan evrak "UYARI (AÇILAMAYAN EVRAK)" ile türü ve sayısıyla bildirilir.
- **Kaynakça (Q):** davanın beyan edilmiş geçmişi teyitsiz içtihat sayılmaz, ayrı alt başlıkta görünür. Taslağın kendi DOSYA NO'su listelenmez.
- **Hook sarmalayıcı (Q):** Windows'ta WindowsApps (Mağaza) python kısayolu atlanır; dosya saf ASCII'dir (UTF-8 kod sayfasında da ayrıştırılır). Kurulu sürümü güncelleyene kadar geçici çare: Ayarlar > Uygulamalar > Gelişmiş uygulama ayarları > Uygulama yürütme diğer adları > "python.exe" ve "python3.exe" kapalı.

### Yapılamayanlar / sınırlar

- Gerçek evrak ölçümleri (yukarıda C).
- TEYİT BEKLİYOR hukuki noktalar: [docs/YARGI-PRO-UYARLAMA-PLANI.md](docs/YARGI-PRO-UYARLAMA-PLANI.md) §6.3.
- Gerçek udf-cli ile UDF üretimi ağsız koşuda uçtan uca denenmedi.
- Avukat onay bayrakları (`--onay`, `--istisna-onay`, `--hukum-onay`, `--serh-onay`, `--karar-onay`) bir beyandır: sistem bayrağı kimin verdiğini doğrulayamaz; defter imzası sahiplik alanını kapsamaz. Avukatın kendi mesajına bağlanması v0.5.19 adayıdır.
- Kanca ölçümü (sürüm defteri): [PERFORMANS-STATUS.md](docs/PERFORMANS-STATUS.md) §12. Karşılaştırma v0.5.17.1 ile, aynı makinede, A/B/A/B.
  - Standart kökte ölçülebilir fark yok: Python 3.14'te en çok +2,4 ms, 3.12'de +1,6 ms. Giriş betiği kazancı 31–40 ms; ağır modül yok.
  - Zincir ürünleri olan büyük dosyada (3000 evrak temsili) Stop kancası +79 ms (~%20). Kaynağı çapraz denetim; v0.5.19'da girdi özetine bağlı önbellek önerilir.
  - Önceki ölçüm §11'de (2026-10-06).

## v0.5.17.1 — ACİL GÜVENLİK YAMASI: SAHİPSİZ YEDEK MCP (B-23) + UDF İÇ İZ SIZINTISI (B-19) (2026-10-06)

**Ne:** v0.5.18 adayından ayrılan ve yalnız iki güvenlik düzeltmesini taşıyan küçük sürüm. Süit 2426 → **2455** (`OA-SUIT-SAYISI`).

- **B-23 — sahipsiz yedek MCP ilanı kaldırıldı.** v0.5.7.4'ten beri `plugin.json`'da ilan edilen `yargi-mcp-yedek` uç noktası 2026-10-06'da ölçüldü: alan adı ilgisiz bir sunucuya çözülüyor ve başka bir alan adına verilmiş sertifika sunuyor; kaynak depo artık herkese açık değil. Claude Code bağlantıyı TLS ad uyuşmazlığıyla reddettiği için veri gitmedi. Ama adı ele geçiren taraf geçerli sertifika alırsa, eklentinin kendiliğinden güvendiği bu sunucu avukatın sorgularını okuyup "içtihat" diye sahte metin (gizli talimat dahil) döndürebilirdi. İlan kaldırıldı; oa-ictihat bağlantı katmanı güvenli kapanışa çevrildi (Pro yoksa otomatik geçiş YOK → "teyit YAPILAMADI", künye iddia kalır). Bu, v0.5.7.4'teki yedek kararını bilinçli olarak tersine çevirir. Eski sürümü kurulu olanlar `yargi-mcp-yedek` bağlantısını connectors bölümünden kaldırmalıdır. Kilit: `tests/test_v0518_mcp_ilan.py`.
- **B-19 / B-18 — mahkemeye giden UDF'ye iç iz sızıntısı.** Kurulu eklenti önbelleğinde 16-21.09'da yerinde yapılan `md_udf_html.py` ve `kunye_ortak.py` yamaları depoya işlenmemişti; eklentiyi GitHub'dan kuranlarda taslaktaki iç izleme yorumları ve makine kaynakça bloğunun aracın adını anan önsözü UDF'de görünür metin oluyordu. Yamalar depoya alındı; yorum ayıklama tek geçişli taramaya çevrildi (kapanmayan çok sayıda `<!--` içeren taslakta eski desen karesel çalışıyordu). Avukat kararı (B-20, 2026-10-06): içtihat kaynakçası mahkemeye giden nüshaya girmez, iç taslakta kalır. Kilit: `tests/test_b19_udf_teslim_izi.py`.
- **Bağımsız güvenlik incelemesi (Fable 5.1) düzeltmeleri:** yayından önce yapılan incelemede saha yamasının ayıklayıcısında bir VERİ KAYBI yolu bulundu ve kapatıldı: taslakta kapanmamış bir `<!--` (yarım kalmış not) ileride herhangi bir `-->` ile yorum sanılıp aradaki dilekçe metni UDF'den sessizce siliniyordu. Artık dilekçe metni taşıyabilecek aday yorum ayıklanmaz, görünür kalır ve uyarı basılır. Aynı turda: kapanışı silinmiş kaynakça bloğunda metin kaybı (ayıklayıcı + üretici fail-closed), yerel motor yolunda ayıklama, HTML5 boş yorumları, satıra yayılan vurgu, "C++" gibi metnin bozulması ve belgelerde sahipsiz yedek projenin "alternatif" diye önerilmesi düzeltildi. Kilitler: `tests/test_b19_udf_teslim_izi.py`, `tests/test_v0518_mcp_ilan.py`.
- **Güncelleyenler için:** eski sürümle üretilmiş `.udf` dosyaları iç iz taşıyabilir ve teslim hattı aynı adlı mevcut `.udf`'yi devralabilir (üretici sürümü devralma ölçütü değil — v0.5.19 İP-1). Güncellemeden sonra açık dosyalardaki eski `.udf`'leri kaldırıp teslimi yeniden koşun. 2. tur incelemeyle ayrıca: CRLF satır sonlu taslakta boş satır koruması ve tek satırlık uzun iç iz yorumlarının ayıklanması düzeltildi.
- **Test fikstürü:** `test_oa_ingest_ocr_nobetci` karışık evrak fikstürü boş-sayfa eşiğinin belirgin üstüne taşındı (Windows'ta Tesseract 5.x sağlıklı sayfayı eşiğin altında okuyordu; doğrulanan davranış aynı).
- **Doğrulama (2026-10-06, Windows 11, ağsız — udf-cli ve Node test sürecinin dışında):** tam süit Python 3.12.15'te 2442 geçti / 12 atlandı / 0 kaldı, Python 3.14.8'de 2442 / 12 / 0; zamanlama (perf) testi iki sürümde de geçti; `aile_dogrula` 20 parça TEMİZ. Atlananlar ortam kaynaklıdır (udf-cli oturumu ve saha referansı yok), main 0.5.17 tabanıyla aynıdır.

## v0.5.17 — BACKEND DENETİMİ + HOOK PERFORMANSI (2026-09-12)

**Ne:** İki bağımsız denetim dalının birleşimi (`claude/ortak-avukat-backend-check`
+ `claude/pc-optimization-performance`) ve manifest onarımı. Süit 2318 → **2426**;
`aile_dogrula` 20 parça TEMİZ.

### A. Müvekkil lehine sonucu bozan sistemsel kırıklar (2026-09-10 backend denetimi)

- **B5 — hook katmanı manifest çakışması (H0; eklentiyi tümden düşürüyordu):**
  `plugin.json`'daki `"hooks": "./hooks/hooks.json"` satırı, standart yol olduğu
  için zaten yüklenen dosyayı ikinci kez bildiriyordu → kurulumda «Duplicate
  hooks file detected» ve eklentinin **20 skill'i birlikte** yüklenemiyordu.
  Teşhis aracı (`tools/hook_doktor.py`) ise «hooks ✗ YOK» diyerek avukatı
  sistemi kırmaya yönlendiriyordu. Sözleşme tersine çevrildi ve **güçlendirildi**:
  standart yolun manifestte yeniden bildirimi artık ARIZA; buna karşılık
  `hooks/hooks.json` standart konumda VAR olmalı VE tetik sözlüğü DOLU olmalı
  (diskte durup boş kalırsa katman ölüdür — o da artık testli); standart yol
  DIŞI özel bildirim hâlâ meşru. Kapı sayısı azalmadı, arttı.
- **B1–B4 — müvekkil-aleyhi taramasının kör noktaları:** `tam_tur.py` Python 3.12
  öncesinde import edilemiyordu (SyntaxError); `--taraf` verilmediğinde tarama kör
  kalıyor ama çıktı «[OK] bulunamadı» diyordu (sessiz-yanlış); olumsuzlama deseni
  Türkçe `-me` ekini ayırt etmediğinden gerçek ikrar susturuluyordu; `mudahil`
  CLI'de varken kalıp sözlüğünde yoktu.
- **B6 — İŞ MAHKEMELERİ EKSENİ:** teslim kapısı iş hukukunu hiç tanımıyordu;
  müvekkili bitiren ikrarların HİÇBİRİ yakalanmıyordu.
- **B7 — iş hukuku süreleri + İŞ GÜNÜ birimi:** kural tabanındaki 21 kuralın
  hiçbiri iş hukuku değildi ve motor `isgunu` birimini TANIMIYORDU — oysa 4857
  m.21/5 süresi takvim günü değil **iş günü** sayar. Sistem fail-closed
  davranıyordu (sessiz yanlış hesap YOK) ama avukat motoru iş mahkemesi
  dosyasında hiç kullanamıyordu. `BASLANGIC_TURLERI["olay"]` açıklaması da
  düzeltildi: olaya bağlanan **usul** süreleri de vardır (4857 m.20/1 iki
  haftalık süre arabuluculuk son tutanağının DÜZENLENDİĞİ tarihten; m.21/1 bir
  aylık süre işçinin BAŞVURUSU ile) — «yanlış olaya bağlanan doğru hesap, yanlış
  hesaptır» (B-20).
- **B8 — [F] kapısı (H0):** dilekçenin KENDİ dosya numarasını çıplak künye
  sayıyordu.

### B. Hook performansı ve CI (pc-optimization dalı)

Ölçüm koşulu (PERFORMANS-STATUS.md §2 — elmayla-elma): `main` vs dal, aynı ölçüm
aracı, gerçekçi dava kökü, dedup yenilmiş, Python 3.12.3, 4 vCPU, ortanca değerler.

| Hook modu | ÖNCE (`main`) | SONRA | kazanç |
|---|---|---|---|
| `hook-prompt` (her kullanıcı turu) | 239.4 ms | **46.4 ms** | −80.6% |
| `hook-pretool` (her Write/Edit/Bash) | 232.7 ms | **40.4 ms** | −82.6% |
| `hook-denetle` (Stop + SessionEnd) | 935.3 ms | **77.1 ms** | −91.8% |
| **bir `Write` (Pre+Post birlikte)** | **1164.2 ms** | **118.1 ms** | **−89.9% · 9.86×** |
| sıcak yolda ağır modül | 11 (pymupdf dahil) | **0** | — |
| soğuk `.pyc` (taze kurulum) uçtan uca | 397 ms | **95–135 ms** | — |

- **Kök nedenler:** tek bir string sabiti için `pymupdf` yükleniyordu (sıcak yolda
  11 ağır modül); ayrıca aynı modül tek çağrıda 3 kez yürütülüyordu. `hooks.json`
  Stop ve SessionEnd'i aynı `hook-denetle` moduna bağladığından oturum
  kapanışında bu bedel iki kez ödeniyordu: ~1.87 s → ~0.15 s.
- Yeni tek giriş noktası `oa-pipeline/scripts/hook_giris.py` — **performans
  katmanı; hukuki iş akışını asla durdurmaz**: çıktısı doğrudan çağrıyla birebir
  aynı, `--denetle` exit 1 aktarımı, yedek yol ve `sys.path` temizliği testli.
  Ölçüm aracı `tools/hook_olc.py`; makine hızlandırma `tools/pc_hizlandir.ps1`.
- **CI:** paralel test (`-n auto`) + pip önbelleği ile süit 94.8 s → **43.0 s**
  (seri 259.1 s'ye göre 6.0×); Windows `-n auto` dört bacakta doğrulandı.
  `CLAUDE.md` mükerrer bölümü ve bayat sayılar düzeltildi.

**Düzeltme kaydı (B-20 düsturu gereği):** PR #5'in ilk gövdesindeki «189.7 →
26.9 ms · 7.05×» rakamı **boş klasörde, dedup'a yakalanmış sıkı bir döngüyle**
alınmıştı; hem yöntemi geçersizdi hem de gerçek kazancı OLDUĞUNDAN KÜÇÜK
gösteriyordu. Geçerli olan yukarıdaki tablodur (PERFORMANS-STATUS.md §2).

### C. Zamanlama testi yeniden tasarımı — kırılgan kapı kaldırıldı

`test_giris_betigi_dogrudan_cagridan_HIZLI`'nin oran eşiği (`giris <
dogrudan * 0.75`) **kaldırıldı**; yerine mekanizmayı zamanlamasız kilitleyen
deterministik kapı geldi. Gerekçe ölçümle kuruldu (tam kalibrasyon tablosu:
PERFORMANS-STATUS.md §10):

- Kazanç sabit bir DERLEME maliyetidir (mutlak); oranın paydası platforma
  bağlıdır. Windows'ta çıplak yorumlayıcı başlığı 53.49 ms ve süreç doğurma
  bedeli paydayı büyütür → aynı ~40–80 ms kazanç Linux'ta ~%45, Windows'ta
  ~%23 oran verir; eşik (%25) tam bandın ortasına düşüyordu. Test YÜKSÜZ
  makinede 3 koşuda 1 kırmızı yandı; tam süit yükü altında ölçüm TERSİNE
  döndü (203.3 vs 194.6 ms — eski AAAAA-BBBBB blok düzeninin artefaktı).
- Kendinden kalibre mutlak ölçüt (`fark >= 0.5 × C`) de denendi ve ÖLÇÜMLE
  ÇÜRÜTÜLDÜ: öngörü fark ≈ 0.85–0.95·C, gerçek **fark/C = 0.24–0.62**
  (unmarshal 6300 satırlık modülde 0.3–0.4·C — ihmal edilemez). Tahminci
  karşılaştırması da kayda geçti: `min−min` 25.9–80.8 ms arası zıplarken
  eşleştirilmiş ABBA fark ortancası 61.5–100.2 ms (ortanca 78.8 ms) ve
  bağımsız araç `hook_olc`'un +79.0 ms'iyle birebir uyumlu.
- **Kırılgan kapı, kırmızı kapıdan kötüdür:** «tekrar koştur» refleksi
  öğretir — ki bu, testin önlemek için yazıldığı şeyin (kazancın bir gün
  sessizce kaybolması) tam mekanizmasıdır.

Yerine gelen üçlü: **KAPI** `test_pipeline_kayit_KOD_NESNESI_PYC_DEN_YUKLENIR`
(`python -v` import izinde `code object from …pipeline_kayit.cpython-3xx.pyc`;
kırmızı bütçesi sıfır — zaman ölçmez; `runpy` yedeğine sessiz düşüşü, bayat/
yazılamayan önbelleği ve loader değişikliğini yakalar) · **KANARYA**
`test_giris_kazanci_KANARYA` (`@pytest.mark.perf`, assert YOK — eşleştirilmiş
ABBA ortancası 20 ms altına düşerse uyarı) · **DEFTER** (CLAUDE.md: her
sürümden önce `hook_olc.py --gercekci --tekrar 5 --karsilastir`, tablo
PERFORMANS-STATUS'a; hook-prompt farkı 30 ms altındaysa sürüm notunda
gerekçelendirilir). CI ana koşu `-m "not perf"`, ayrı **seri** adım `-m perf
-p no:xdist` — karantina değil yalıtım, kanarya her bacakta koşar. Ürün
koduna DOKUNULMADI.

**Ölçüm gözlemi — `hook-postwrite` farkı düşük (borç, kusur değil).** Diğer
dört modda giriş betiği +53…79 ms hızlıyken `hook-postwrite` yalnız +6.4 ms
(365.6 vs 372.0 ms). Regresyon DEĞİL — giriş yolu hâlâ hızlı taraf ve kapı
kararı aynı. **tahmin:** `hook_olc.py` giriş×5'i doğrudan×5'ten ÖNCE ve aynı
kökte koşuyor; postwrite, ağır gövdenin (Gate-G + makbuz + metrik) fiilen
ateşlendiği ilk mod olduğundan ilk-kez durum üretimini giriş bloğu ödüyor,
doğrudan blok hazır buluyor. Aynı yöne bakan iki anomali: postwrite-giriş
(365.6) > denetle-giriş (350.9) iken Linux'ta ikisi eşit (77.8/77.1).
Deneyle doğrulanmadı. **v0.5.17.1 borçları:** (i) ölçüm aracına yol başına
ısıtma turu + serpiştirme; (ii) çıktı birebir-eşitlik testi şu an yalnız
`hook-prompt` için kilitli — beş moda genişletilecek (zaman damgası
normalize ederek).

**Çakışma notu:** iki dal da `tests/README.md` OA-SUIT-SAYISI satırına dokunuyordu
(2403 ↔ 2341); kod çakışmadı, yalnız SAYI çakıştı. Bu satır elle uzlaştırılmaz —
`test_v0514_vitrin.py::test_b35_suit_sayisi_isaretcisi_gercek_toplama_ile_ayni`
beyanı `pytest --collect-only` ile karşılaştırır; birleşim sonrası gerçek toplama
**2426**.

---

## v0.5.16.1 — Saha Yan-Bulguları (2026-09-07)

**Ne:** v0.5.16'nın gerçek dava kopyalarında yapılan saha ölçümünün bulduğu iki
kusur onarıldı (dal `v0516/yan-bulgular`; test `tests/test_v0516_yan_bulgular.py`,
17 sınama; süit 2318).

- **Kütük ayrıştırıcısı sütun toleransı (oa-kontrol `kunye_ortak.py` + `ictihat_
  muhakeme_denetim.py` + `kunye_teyit.py`):** kütük okuyucuları satırı `len != 7`
  ise «BOZUK» sayıyordu; saha kütüklerinde satırlar 17 hücreli → 26/33 taslakta
  her künye «damgasız» göründü, [F] hafif kip ve kütük teyidi kör kaldı. Okuyucu
  artık sütun sayısından bağımsız: esas+karar ve `DAMGA=`/`AKIBET=` tokenları
  satırın tamamında (sonuncusu geçerli), daire künyeyi taşıyan hücreden; BOZUK
  yalnız gerçekten ayrıştırılamayan satıra. Yazıcı simetrisi (oa-pipeline
  `oa_hafiza.py`): `--sorgu` hücresi de DAMGA=/künye-izi kaçışından geçer.
- **Şerh zinciri kapı atlatması (oa-pipeline `pipeline_kayit.py`):** 00-kunye.json
  yokken `--serh --serh-kapi ingest-once` erken dönüp K2 GRAF KAPISI'nı hiç
  sormuyordu → çevrimli graf şerhsiz geçiyordu. Şerhli geçiş artık biriktirilir,
  kalan kapılar (senkron/çapraz-adım/graf/kiyas/kontrol) da sorulur; kapsanmayan
  bloklu kapı RET (hangi kapı, hangi ad; iki kapı için `tumu`); şerh mesajı
  geçilen kapıların hepsini listeler.

**Neden/kanıt:** saha ölçümü (gerçek dosyalar, anonim); ayrıntı parça
günlüklerinde (`oa-kontrol`, `oa-pipeline` `references/degisiklik-gunlugu.md`).
Plugin sürüm damgası 0.5.16'da kalır (yama, ayrı etiket entegratörün kararı).

## v0.5.16 — İki Denetimin İnfazı (2026-09-07)
**Kanıt türü:** iki bağımsız dış denetim raporu (6 Eylül 2026): (1) *bütünleşik
analiz* — döngü/graf/hook mimarisi + üç dalda saha sınaması + Yargıtay→BAM→ilk
derece dikey inişi; **22 bulgu** (K1–K5 kesişim, G1–G12 graf, H/P hook-pipeline,
D1–D4 kaynak) ve **12 hamle**; (2) *dış denetim* — 20 parçanın hukuki metodolojisi
ve müvekkil menfaati; **A-1..A-28 + B-1..B-8**, P0/P1/P2 reçetesi. Kaynak belgeler
`_gorus/denetim-2026-09-06-*.md`; her grubun Yargı Pro/Mevzuat teyit izleri
`_gorus/denetim-v0516-yargipro-teyit-<grup>.md` (49 MCP çağrısı, ~45 (kanun, madde)
çifti; kritik 0, küçük 10 — onarıldı). Saha "önce" ölçümü (11 gerçek dosya kopyası,
anonim kod) `oa-v0516-calisma/saha-once/`; **"sonra" ölçümü bu sürümde YAPILMADI**
(açık iş — STATUS §0).

**Yöntem:** reçete 15 sahiplik grubuna bölündü; her grup kendi git dalında
(`v0516/<grup>`) uygula → adversarial hakem → onarım → Yargı Pro hakem/onarım;
her norm Mevzuat/Yargı Pro MCP'den madde metniyle teyit (m.4), fikstürler
sentetik (m.7), önce-kırmızı TDD. Ana ajan hiçbir grubun dosyasına dokunmadı;
birleştirme tek entegratörde (`--no-ff`, sırayla A B C1 C2 D E F G H I1..I6;
çakışma yalnız `tests/README.md` OA-SUIT-SAYISI satırında — E/H/I3/I6, nihai
sayı `pytest --collect-only` ile tek seferde yazıldı; `tests/test_v0514_muhakeme.py`
F+I2 otomatik birleşti, iki beklenti de duruyor).

**Grup → parça:** **A** → oa-illiyet; **B** → oa-pipeline; **C1** → oa-dilekce; **C2** → oa-kontrol; **D** → oa-gizlilik, oa-pipeline; **E** → oa-ingest, oa-pipeline; **F** → oa-vakia; **G** → oa-usta; **H** → oa-ictihat; **I1** → oa-interview, oa-strateji; **I2** → oa-antitez; **I3** → oa-mudafii, oa-musteki-vekili; **I4** → oa-alan, oa-kiyas, oa-usul; **I5** → oa-sure; **I6** → oa-sozlesme.

**Kapanan bulgular (ölçüm: grup raporlarındaki `changelog_notu` metinlerinde anılan
kodlar):**

| Bulgu | Grup(lar) |
|---|---|
| A-1 | A, I5 |
| A-2 | B |
| A-3 | B |
| A-4 | E |
| A-5 | I1 |
| A-6 | I1 |
| A-7 | I4 |
| A-8 | I1, I4 |
| A-9 | I1 |
| A-10 | I5 |
| A-11 | D |
| A-13 | F |
| A-14 | H |
| A-15 | I4 |
| A-16 | I1 |
| A-17 | I1 |
| A-18 | I1 |
| A-19 | I1 |
| A-20 | I2 |
| A-21 | C2, I2 |
| A-22 | C1 |
| A-23 | I6 |
| A-24 | C2 |
| A-25 | I3 |
| A-26 | I3 |
| A-27 | G |
| A-28 | B, G |
| B-1 | B, E |
| B-2 | B, C2 |
| B-3 | G |
| B-5 | D |
| B-6 | C1 |
| B-8 | E |
| D1 | H |
| D2 | H |
| D3 | H |
| G1 | A |
| G2 | A, C2 |
| G3 | A |
| G4 | A |
| G5 | A, C2, D |
| G6 | A |
| G7 | A |
| G8 | A |
| G9 | A |
| G10 | A |
| G11 | C2 |
| G12 | A |
| H1 | B |
| H2 | C1 |
| K1 | B, G, I4 |
| K2 | A, B |
| K3 | C1 |
| K4 | C2 |
| K5 | C2, D |
| P0-1 | F |
| P0-2 | E |
| P0-3 | B, I2 |
| P0-4 | C1 |
| P0-9 | E |
| P1-1 | I1 |
| P1-2 | I1 |
| P1-3 | I5 |
| P1-4 | I4 |
| P1-5 | C2, I2 |
| P1-6 | I3 |
| P1-7 | I3 |
| P1-8 | D |
| P1-9 | B |
| P1-10 | E |
| P1-11 | I1 |
| P2-2 | I4 |
| P2-3 | I1, I4 |
| P2-5 | H |
| P2-6 | I6 |
| P2-7 | C2 |
| P2-8 | G |
| P2-10 | G |
| P2-12 | C1 |

Tabloda görünmeyen kodlar ya hazırlık commit'inde (fcae8d8: A-1/P2-1 anayasa m.1
triyaj, B-7/P2-13 README ölçüm dili) kapanmıştır ya da bir grubun notunda kod
adıyla anılmadan uygulanmıştır — parça günlükleri (`references/degisiklik-gunlugu.md`,
"v0.5.16" bölümü) ayrıntıyı taşır. Kapanan ana başlıklar: graf kapısı SERT + exit
sözleşmesi + bağlanmamış delil/köprü/güç sınıfları + dal-ayrımlı `kesme_flag` +
taraf yönü + karar/mahkeme tipi (A); bekçi DAMGAYA bağlandı (K1), graf kapısı (K2),
`--serh-kapi`, inline sayaç (M7), ANTİTEZ↔STRATEJİ sırası (P0-3), müvekkil kararı
düğümü (P1-9), avukat hükmü sensörü (A-28) (B); [F] hafif kip + [P] netice-i talep
+ [N] beyaz liste + udf-cli kesinti planı (C1); tarih-only/K-only atıf → EKSİK KÜNYE
BLOK, [G5-AKIBET], örtüşme sayacı, hâkim lensi (C2); `teyit --akibet` + senkron
klasör uyarısı (D); OCR araç-hatası teşhisi + süre adayı (E); ispat ontolojisi —
tanık caizliği, hukuki iddia, karine yük kaydırır (F); aile_dogrula yapısal kilitler
+ sürüm işaretçisi (G); `kanun_yolu_zinciri.py` + iniş ritüeli + içtihat haritası (H);
koruma tedbiri, zaman ekseni, risk toleransı, maliyet cetveli — fail-closed tarife (I1);
bilirkişi/teknik cephesi (dokuz cephe) + hâkim lensi (I2); müzakereli çıkışlar +
beyan protokolü, ceza↔hukuk köprüsü (I3); merci tayini, usul zamanlama, forum
seçimi, yarışan norm (I4); aşama tetikli süre sınıfı (I5); ifa senaryo testi (I6).

**Entegrasyon hizalamaları (birleşim sonrası, H1–H5 — `tests/test_v0516_entegrasyon.py`,
18 test):** H1 `oa_hafiza.py sure-flag --asama <ad> --pipeline-adimi N` (tarihsiz
`tur: asama` kaydı; `sure_nobetci` ile uçtan uca) · H2 eski «6 STRATEJİ / 7 ANTİTEZ»
sırası ortak-avukat/oa-mudafii/oa-musteki-vekili SKILL'lerinde düzeltildi; çalışma-
evrakı önekleri `06-antitez*`/`07-strateji*` (oa-antitez/oa-dilekce/oa-usul/oa-kiyas
şablonu, `oa_metrik.py`, `dilekce_denetim.py`, `ictihat_muhakeme_denetim.py`; eski
adlar geriye uyumla kabul) · H3 OA-SUIT-SAYISI tek seferde · H4 AKIBET yazar↔okur
uçtan uca (LEHE+bozuldu+atıf → BLOK) · H5 `*vakia*.json` bekçisi damgaya çekildi;
aile_dogrula KİLİT-A damga sözleşmesini (bekçi damgası ↔ üretici script) dört bekçide
denetler — gerçek depoda TEMİZ, kör kilit yok. «Sekiz cephe» kalıntıları «dokuz cephe».

**Sürüm damgaları:** plugin.json · marketplace.json · iki README · `pipeline_kayit.py`
ve `teslim_paketi.py` OA_SURUM → 0.5.16 (birlikte). `tests/README.md`
OA-SUIT-SAYISI = **2301** (`pytest --collect-only`). Tam süit sonucu STATUS §0'da.

**Yapılamayanlar / açık kalanlar (sessiz atlama yasağı):**
- Saha "SONRA" ölçümü (aynı 11 kopya, v0.5.16 araçları) ve önce/sonra tablosu — yapılmadı.
- `git push` — yapılmadı (kimlik engeli; `gh auth login -h github.com` sonrası kullanıcı).
- Avukat kararı bekleyen: B-4 `git filter-repo` (geçmişte dosya kimliği) · udf-cli pin
  (A5/B-6) · `maliyet_cetveli` tarife.json değerleri (AAÜT 2026 ek tabloları MCP'den
  alınamadı; nispi harç asgari haddi kaynak çelişkisi «çıpa» etiketli).
- MCP'den teyit edilemeyip «çıpa / teyit edilmedi» etiketiyle bırakılanlar: 7589 s.K. RG
  sayısı (C1); dava dilekçesi-temerrüt/faiz içtihadı ve HMK m.392 vd. (C1); HAGB «sanığın
  kabulü» AYM/7499 geçiş rejimi (I3); TBK m.74 içtihadı yalnız künye düzeyinde, TCK m.52 /
  CMK m.153 / TCK m.267 (I3); 492 s.K. m.30-32, HMK m.17-18/114/116-117/390 ve İİK tedbir
  çıpaları (I4); TBB Meslek Kuralları bilgilendirme hükmü (B-2); `ceza:hukuka_uygunluk`
  TCK m.24 vd. ve 12. CD künyesi (A-2).
- Devirler: `pipeline_kayit.py`'nin `senaryo_bosluklari` (I6 --json) okuması; `md_yaz`
  araç-hatası önerisinde dil adı sabiti (E); G11 parantez sayacının «m.353/(1)» sayması
  (C2, advisory); Linux'ta tur paketi yokken OCR yolu yalnız sahte ikiliyle sınandı (E).
- Belge bayatlık taraması (DEVAM-PLANI §9) bu sürümde H2 kalemi + sürüm/tarih damgaları
  ile SINIRLI yapıldı; satır satır tam tarama açık iş.
- **Belge bayatlık taraması — infaz (2026-09-07, ayrı commit):** 83 bulgu koda karşı
  doğrulandı, 82'si düzeltildi (1'i «bayatlık yok» bilgi notu). Sınıflar: script sayıları
  diskle eşitlendi (ingest 2 / kontrol 8 / ictihat 1 / strateji 1 / vakia 2); «sekiz cephe»
  → dokuz; 19 README damgası v3.20 → v3.26; «18 oa- parçası» → 19; eski MCP araç adları
  (`search_mevzuat*`, `search_cb*`, `search_anayasa_unified` birincil) → `mevzuat_ara` /
  `mevzuat_icinde_ara` / `mevzuat_getir` / `aym_ictihat_ara`; CLI enum/bayrak bayatlıkları
  (`--tip yemin|idari-kanal`, `--taraf` 6 değer, `--sebep` 7 değer, `--json` ZORUNLU
  kıyas, `sure-flag --asama`, `--muvekkil-karari`); DAMGA=NOTR G6'da BLOK; anayasa m.7
  kimlik soyutlamaları (yer adı + dosya no → «saha bulgusu»); Yönetmelik 2646 m.8 kenar
  notu (MCP teyit: üst/sol/sağ 1,5 cm — alt kenar maddede yok); 6 changelog'daki literal
  `
` yapıştırmaları gerçek satırlara açıldı ve yabancı parça blokları ayıklandı;
  KURULUM-SENKRON / TEST-KULLANIM «TARİHÎ» damgalandı; çekirdek günlüğündeki kesik satır
  (v3.14–v3.16 kayıp — git geçmişinde de yok) şerhlendi. Dokunulmayan: referans
  günlüklerindeki tarihî saha kimlikleri (ayrı karar), B-4 `git filter-repo`.

---

## v0.5.15 — UDF Yapılı Okuma (2026-08-31)
**Soru avukattan geldi:** *"ingest sistemimiz udf2md yapıyor muydu?"* Cevap:
yapıyordu ama **ham** — ZIP → CDATA → düz metin. Metin kaybolmuyordu, **yapı**
kayboluyordu. 798 gerçek evrakta ölçüldü: 739 tablo ızgarası · 424 iç içe tablo
· 548 görsel (20,8 MB mühür/imza — **delil**) · 32.593 alan etiketi · **7.316
veri düğümü** (düz metnin tamamen dışında; %100 kayıp) · 1.004 liste ögesi ·
1.487 altı çizili · 461 üst/alt bilgi. Bilirkişi hesap tablosunda tutar
kaleminden kopuyor, dilekçedeki "1., 2., 3." talep sırası düzleşiyordu.

**Çözüm — temiz oda.** Ticari bir üründe aynı işin çözümü olduğu görüldü;
avukat "yöntemlerinden faydalanalım" dedi. Sınır çizildi: **formatın kuralları
olgudur, öğrenilebilir; başkasının kodu ifadedir, kopyalanamaz.** Ajanın
referans olsun diye çıkardığı üçüncü taraf kaynakları karantinaya alındı;
üretim modülü yalnız avukatın kendi dosyalarındaki ölçümden ve kendi
sözlerimizle yazılmış şartnameden türedi. Açık kaynak taraması da kararı
destekledi: en yakın çözüm **lisanssız** bir depoda (= tüm hakları saklı).

**Ölçülen sonuç:** 796/798 dosya (eski hat 787) · görünür karakter kaybı
**0 / 6.403.940** — CDATA ham baytlardan **bağımsız** yeniden çıkarılarak
ölçüldü (modülün kendi beyanına güvenilmedi; ilk ölçümün **döngüsel** olduğu
sınavda yakalanmıştı) · tablo geometrisi **XML gerçeğine karşı 739/739** ·
regresyon 0 · salt-okuma ihlali 0/798 · ~4 ms/dosya · 75 yeni test.

**İki katmanlı invaryant (avukat kararı).** Önce "hiçbir karakter değişmeyecek"
dendi; ölçüm gösterdi ki katı okumada bu **796/796 dosyayı bloklar** ve yeni
hattı öldürür — çünkü hücre içi satır sonunun hücre ayracına dönüşmesi
tasarımın kendisidir. Avukat "kuralı esnet, önemli olan sonuca en yüksek
kesinlikle ulaşmak" dedi. Sonuç bir esneme değil, **doğru tanım** oldu:
**Katman 1 İÇERİK** katı, eşik 0 (bugün 0/6.403.940 ile tutuyor) ·
**Katman 2 KAP** tanımlı-esnek (belgeli, deterministik, sürüm damgalı).
*Katılık kaybolmadı, doğru katmana çekildi.*

**Kapıların huyu maliyet asimetrisinden:** üretim kapısı **işaretle-ve-taşı**
(bloklamak kayıplı hatta düşürür, değer kaybettirir; eksik karakterler
*kendileriyle* sapma kaydına yazılır — işaretlemek kaybetmek değildir);
bütünlük kapısı **blokla-ve-onar** (sha uyuşmazlığı güven iddiasını çökertir,
onarım ise 3,37 sn'de bedava).

**Künye artık makine-teyitli:** UYAP evrağın içinde mahkeme adını, dosya/karar
numarasını, tarafı **kendisi etiketliyor**; bugüne kadar bunları düz metinden
regex'le geri buluyorduk — hata payı bizimdi. Beyaz liste **dosya kapsamına**
göre seçildi (span sayısına göre değil: `makbuzBilgisi` 3.449 span taşır ama
yalnız 40 dosyada — o bir makbuz tablosudur). `kunye_kaynak: udf-alan`
provenansı, değerin tahmin değil kaynak beyanı olduğunu söyler.

**INDEX'e `Yapı` sütunu:** `T:n×m` · `V:n` · `G:n` · `İ` — yalnız ayırt edici
sinyal. İmzalayan personel sicili künyede kalır, **INDEX'e çıkmaz** (INDEX
dışa en çok sızan artefakttır).

**Determinizm:** aynı girdi + aynı sürüm → bayt-özdeş (hash-seed, ayrı süreç,
yol bağımsızlığı, CRLF testleriyle kilitli). `icerik_sha256` renderer'dan
**bağımsızdır** ve sürümler arası sabit kalmalıdır — değiştiği gün
"kayıpsızlık tanımımız değişti" demektir ve ayrıca gerekçe ister.

**Belge düzeltmesi:** `udf-ic-yapi.md` "ZIP içinde TEK content.xml" diyordu;
ölçüm 464 dosyada `documentproperties.xml` buldu (UYAP doğrulama kodu +
imzalayan sicili) — henüz okunmuyor, ayrı kalem olarak sırada.

**Sözleşme korundu:** `evrak_isle` 6'lı demeti bozulmadı; zenginlik 7. kanaldan
gider — PDF/OCR/DOCX hatlarına hiç dokunulmadı. Süit **1763** (1688'den).

## v0.5.14 — Denetimin İnfazı: 62 bulgu (2026-08-31)
**Kanıt türü:** iki bağımsız denetim turu. (1) Ertelenen dört tez kod üzerinde
planlandı ve planlar adversarial çürütmeden geçirildi; (2) eklentiyi **fiilen
çalıştıran** 5 hukukçu + scriptleri **fiilen koşturan** 4 mühendis avcı,
her biri ayrı bir şüpheci tarafından çürütülmeye tabi tutuldu. Toplam **62
bulgu** (A-1…A-22 hukuki, B-1…B-40 mühendislik). Hukuki iddiaların tamamı
Mevzuat MCP'den madde metniyle doğrulandı.

**Telafisiz üç hata düzeltildi:**
- **CMK m.331/4** — ceza kanun yolu sürelerine hukuk yargısının adli tatil
  rejimi (HMK m.104, bir hafta) uygulanıyordu; doğrusu **üç gündür**. Sistem
  dört gün geç tarih veriyordu; 4-7 Eylül'de verilen istinaf/temyiz süreden
  reddedilirdi. `--yargi ceza` kolu açıldı; kural↔kol uyuşmazlığı artık
  **hesabı durduruyor** (yanlış tarih deftere yazılamıyor).
- **CMK m.268** — referans dosyasında süre hâlâ "yedi gün"dü (v0.5.13'te
  SKILL.md düzeltilmiş, referans atlanmıştı: ikiz liste kayması).
- **IBAN deseni** — Layer 0'ın MUTLAK_DENY kuralı hane sayısı yanlış olduğu
  için **geçerli hiçbir Türk IBAN'ında ateşlemiyordu**.

**Halüsinasyon panzehirinin onarımı (P0):** künye kapısı yaygın künye
biçimlerini görmüyordu ve uydurma içtihatlı taslak uçtan uca "TESLİME HAZIR"
alabiliyordu; kaynakça üreteci ise kapının göremediği künye için dilekçeye
**gerçeğe aykırı "tam metniyle okundu" beyanı** yazıyordu. Kapı artık
ayrıştıramadığı atıfta **fail-closed**; teyitsiz künye varsa okundu beyanı
**hiç yazılmıyor**.

**Diğer P0'lar:** yürütmenin durdurulması (İYUK m.27) ailenin tamamında yoktu —
ödeme emrine karşı dava açmanın tahsilatı durdurmadığı hiçbir yerde yazılı
değildi; sunum kilidi dava klasörü dışında sessizce ölüydü; bayat-araç
nöbetçisi negatif parmak izine dayandığı için gerçekten bayat bir kiti
"kanaldan yeni" ilan ediyordu; mühürsüz-teslim taraması fail-open'dı;
`teslim_paketi` girdisini mutasyona uğratıyordu (aynı komut 1. koşuda yeşil,
2. koşuda kırmızı).

**Yapısal onarımlar:** kural tablosu artık **tek kaynak** (JSON) — gömülü
fallback ondan türetiliyor ve ayrışmayı bir test mekanik olarak yakalıyor
(bu tur entegratörün kendi kaymasını da yakaladı). Süit sayısı iddiası tek
işaretçiye indirildi. `unsur-sablonlari/` altına **amme ödeme emri** şablonu
eklendi (İİK ödeme emriyle karıştırma uyarısıyla). 21 süre kuralının
tamamı MCP teyit tarihli — teyitsiz kural **sıfır**.

**Entegratör hükmü (çatışma çözümü):** yeni sunum-kilidi uyarısı ile v0.5.9'un
"dava dışı klasörde sessiz kal" sözleşmesi çarpışıyordu. Ayrım: *diskte
olmayan bir yol için denetlenecek şey yoktur* (susmak gürültü disiplinidir);
uyarı yalnız **var olan** teslim ürününün kökü bulunamadığında çıkar.

Süit **1688** (v0.5.13'te 1406). Ayrıntı: [DENETIM-v0514.md](docs/arsiv/DENETIM-v0514.md).

## v0.5.13 — Heyet Kararlarının İnfazı (2026-08-27)
**Kanıt türü farklı:** bu sürüm bir saha karnesinden değil, **denetimden**
doğdu — 20 skill dört turdan geçti (7 mesleki denetçi + puanlama · 5 disiplinli
hukukçu hakem heyeti · 4 pratikçi avukatın tez/antitez düellosu · 3 yazılım
mühendisinin kod hükmü). Her hukuki iddia Mevzuat MCP'den madde metniyle
doğrulandı; ajan transkriptleri SHA-256 manifestli arşive mühürlendi.
**İki gerçek hata düzeltildi:** katılma anı (CMK m.237 — kanun yolunda
istenemez; ilk derecede hüküm verilinceye kadar) ve itiraz süresi (m.268:
"7 gün" → **iki hafta**, öğrenme gününden; JSON + gömülü fallback birlikte).
**Bir hakem tezi teyitte ÇÜRÜDÜ** ve bu da kayda geçti: "istinaf tefhimden
işler" iddiası m.273/1'in güncel metniyle yıkıldı (f.2, 7499 ile mülga) —
dosya doğruydu, değiştirilmedi. Ders: düzeltmenin kendisi de teyide tabidir.
**Yeni:** süre başlangıç türü çatalı (`--baslangic-turu`; belirsizde iki
senaryo + erken tarih) · "süre kaçtı" mutlak dilinin kırılması + kurtarma
kapıları kataloğu (yargı koluna göre; İYUK'ta eski hâle getirme YOK) ·
tutuklu dosya kipi · celse kartı + **dahili sızıntı kapısı** (iç analiz
belgesi dış çıktıya kopyalanamaz) · zorunlu arabuluculuk dava şartı dört
adreste · İİK m.67/68/72 + İYUK m.10/11 + VUK m.107/A çıpaları · mal kaçırma
kavşağı (iki tarih ekseni). Gerekçeli daraltmalar
[HEYET-KARARLARI-v0513.md](docs/arsiv/HEYET-KARARLARI-v0513.md)'de. Süit o gün **1406** toplandı (v0.5.14/B-35 düzeltmesi: kayıt 1405 yazıyordu, yeniden ölçüldü).

## v0.5.12 — İçtihat Kaynakçası (2026-08-27)
**Avukat kuralı:** dilekçeye giren her Yargıtay/Danıştay kararının **kaynak
linki** tüm çıktılarda görünsün. Taslağın sonuna idempotent kaynakça bloğu
üretildi; URL **yalnız** muhakeme kaydının teyitli satırından alınır —
uydurma yasak, linki olmayan künye görünür notla işaretlenir. UDF üretiminden
önce işlenir, makbuza kaydı düşer. Ayrıca 40-UYAP adının gerekçesi sözlüğe
(bant başı = giden evrak) ve tüm token ölçümleri repoya girdi. Süit 1394.

## v0.5.11 — Kit Güvenlik Katmanı (2026-08-26)
**Saha kanıtı:** 1865 (çok-oturumlu, müdahaleli-yetkili · [KARNE-1865.md](docs/arsiv/KARNE-1865.md)).
Kök düşman adlandırıldı: uygulamanın rpm anlık-görüntüsünden bulaşan bayat
araç nesli (777'den beri 3. nüks); tek seferlik onarımın yetmediği ölçüldü.
**Onarım:** rpm karantinası ('ask') · kilitli çekirdek (salt-okunur + 'ask') ·
yönlü tazelik (bayat / kanaldan-yeni / özdeş) · oturum damgası (defter+makbuz
`session_id`) · çok-oturum görünürlüğü · sözleşme-dışı dizin ve MANİFEST-önce
bekçileri. Süit 1385. Saha koşusu maliyeti: ~4,3M token (çok oturumlu).

## v0.5.10 — Kusursuz UDF Dönüşümü (2026-08-25)
**Saha kanıtı:** 307 (K1: ürün makbuzdan 68 dk sonra mühür dışında değişti;
K2: makbuz resmî ürünü kapsamıyordu · [KARNE-307.md](docs/arsiv/KARNE-307.md)) + 923
(çift-uzantı ve mühürsüz-kopya bağımsız tekrarı).
**Onarım:** atomik mühür (üretim=mühür, üç yolda) · filo-tazelik kapısı
(kök + 40-UYAP tüm teslim-sınıfı UDF'ler makbuza) · çift-uzantı kaynağında
öldü · kopyalar mühürleriyle gider · sunum kilidi makbuz-sonrası değişiklik
penceresini kapattı. Süit 1371. Saha maliyetleri: 307 ~822k · 923 ~360k token.

## v0.5.9 / v0.5.9.1 — Deterministik Tamamlayıcı Zincir (2026-08-22)
**Saha kanıtı:** 777 karnesi + 24-kök çapraz taraması + iki bağımsız hakem
turu (T1-T26 konsolide raporun yerli uygulaması). 777 koşusu ~1,50M token.
Sunum kilidi (makbuzsuz teslim-sınıfı gönderim → 'ask') · inline dilekçe
denetimi · zincir-durumu enjeksiyonu · 40-UYAP dış-çıktı şeması · vitrinin
avukat diliyle sıfırdan inşası. 0.5.9.1: kurulum damgası (sürüm-cache kuralı).

## v0.5.8.4 – v0.5.8.6 — Saha Karnelerinin İnfazı (2026-08-15 → 08-18)
**Saha kanıtı:** 372 (elle-UDF krizi; A/B testiyle hvl-default imzası bulundu),
346 (künye kapısı gerçek açık yakaladı; [G6] mutlak triyaj doğdu), 777 (bayat
kit kök nedeni).
0.5.8.4: elle-UDF engeli + makbuz garantisi (RED bile damgalı) + mühür
otomasyonu + şekil kapısı (4×42,52 pt). 0.5.8.5: [G6] mutlak triyaj (tam metin
okunmadan karar dilekçeye giremez; ALEYHE → iç cephanelik) + hook dirilişi +
e-imza halkası. 0.5.8.6: sürüm kilidi/parmak izi + VERSION.json + devralma
köprüleri. Koşu maliyetleri: 372 ~1,24M · 346 ~1,17M token.

## v0.5.7.x — Saha Donanımı (2026-08-07 → 08-08)
Bayat-tohum aşısı (komşu klasörden kopya yasağı — 754 bulgusu) · G4 bağlantı
kapısı · Yargı Pro birincil + otomatik yedek zincir · davadan gelen atıflar da
link zincirine tabi (kullanıcı kuralı) · CI stdout kirliliği onarımı.

## v0.5.6.1 — Hook Kaydı + Devir Zorlayıcı (2026-08-06)
Hook katmanının kayıt altyapısı; oturumlar arası devir disiplini; rehber
sadeleştirmesi ("ateşlemeyen kapı silinir" ilkesine ilk büyük uygulama).

## v0.5.5 – v0.5.5.5 — Aktivasyon Zinciri + Müdahalesiz Test Dersleri (2026-07-28 → 08-02)
**Saha kanıtı:** 214 evraklık bakir klasörde müdahalesiz test — "kapının gücü
kodunda değil tetiğindedir." Aktivasyon zinciri, OCR nöbetçisi, UDF hattının
resmî araca kilitlenmesi, geçerlilik kapısı, içerik hakemi; 0.5.5.5: cp1254
kodlama çökmesi onarımı (P0).

## v0.5.0 – v0.5.4 — Temel Atma (2026-07-19 → 07-20)
Temiz kurulum (tek kaynak: GitHub) · oa-ingest v1.5 paralel çıkarım · Okuma
Ekonomisi (Gate A-G) · İçtihat Muhakeme Zinciri (G1-G3) · working memory
(`dosya-analiz.md` doğum anı) · dilekçe playbook · anayasa dedup. İlk paket
57 testle çıktı; süitin GÜNCEL büyüklüğü tek kaynaktan okunur: [tests/README.md](tests/README.md) `OA-SUIT-SAYISI` işaretçisi.

---
*Daha eski tarih öncesi (v0.4.0 ve öncesi) tek-skill dönemidir; bugünkü
20-parça mimarisi v0.5.0 temiz kurulumuyla başlar.*

# Ortak Avukat · Türk Hukuku Co-Counsel Sistemi

> Kıdemli bir **Ortak Avukat (Co-Counsel)** kimliğiyle çalışan, İlk İlkeler ve **illiyet bağı** odaklı derin muhakeme yürüten Türk hukuku metodoloji sistemi. Bir Claude Code / Cowork **plugin marketplace** deposu.

**Sürüm:** 0.5.7.2 · **Yazar:** Av. Bayram Can Çapar · **20 skill** (çekirdek + 19 `oa-*` parça)

> ⚖️ **Gerçek davalarda test edildi.** Bu sistem sentetik örneklerle değil,
> derdest gerçek dosyalarla sahada sınanıyor. Son ölçüm: ~200 evraklık gerçek
> bir istinaf dosyası, **tek bir doğal-dil prompt'la**, 49 dakikada ve 45,6k
> token'la teslim edilebilir ek beyana + geçerli UDF'e dönüştü (Claude Fable 5,
> max efor; evrak [avukat-dosya-indirici](https://github.com/bcancapar-spec/avukat-dosya-indirici)
> ile UYAP'tan indirildi). Sayılar, dürüst kayıp listesiyle birlikte:
> **[SAHA-SONUCU.md](SAHA-SONUCU.md)**. Dosya kimlikleri anayasa m.7 gereği
> daima anonimdir.

> **© 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır.** Bu eserin fikri mülkiyeti ile tüm mali ve manevi hakları münhasıran Av. Bayram Can Çapar'a aittir.Ticari amaçla klonlanıp kullanılmadığı müddetçe ücretsizdir.  (5846 sayılı FSEK). Depo kamuya açıktır; izinsiz kopyalama/dağıtma/türev yasaktır.Yalnızca Yargı Pro MCP  geliştiren ekibin münhasıran kullanımı ve geliştirmesi serbesttir ve tam yetkiyle ticari iş kapsamı olmaksızın geliştirmeye yetkilidir.  Bkz. [LICENSE](LICENSE) ve [NOTICE](NOTICE).

---

## Ne işe yarar

**Bu bir "dilekçe yazan yapay zekâ" değildir; bir METODOLOJİ SİSTEMİDİR.**
Kıdemli bir avukatın çalışma metodunu — dosyayı ele alış sırasını, usulü esastan
önce denetleme refleksini, künyeyi resmî kaynaktan doğrulama disiplinini, zaafı
müvekkile karşı değil müvekkil için kullanma ayrımını — yazıya döker ve **her
adımını makineyle denetler.**

Ayırt edici yanı şudur: bir işin yapıldığını **modelin beyanına bırakmaz.**
"İçtihadı doğruladım" demek yetmez — kararın tam metni diske inmiş, davaya bağı
yazılmış ve lehe/aleyhe olarak damgalanmış olmalıdır. "Dilekçe hazır" demek
yetmez — teslim öncesi kapılar fiilen koşmuş olmalıdır. Bu yüzden aile, muhakemeyi
yapan katman ile onu denetleyen katmanı bilinçli olarak ayırır: **model kurar,
script denetler.**

Kullanım alanı Türk hukukunun **herhangi bir dalıdır**: dilekçe (dava, cevap,
istinaf, temyiz), dava-dosya-uyuşmazlık analizi, hukuki mütalaa, içtihat ve mevzuat
araştırması, AYM bireysel başvuru, sözleşme inceleme ve tahriri. Sistem kişilere
değil **yönteme** bağlıdır; her olgusal unsuru (künye, madde, tarih, içtihat) resmî
kaynaktan doğrular ve halüsinasyonu yapısal olarak dışlar.

Aile, 20 ayrı araç değil **yetenek sahibi tek bir eş-avukat** gibi çalışır: dosyanın
analizini kalıcı bir çalışma hafızasına yazar; sonraki her oturumda ham evrakı
baştan okumak yerine bu kaydı kullanır — token-verimli ve kayıpsız.

### DÜSTUR — ailenin anayasası

Ailenin yirmi parçasının tamamı tek bir anayasaya tabidir
([`anayasa.md`](plugins/ortak-avukat/skills/ortak-avukat/references/anayasa.md)).
Bir ilke değiştiğinde önce orası güncellenir; parçalar oraya işaret eder — yani
bir kural yirmi yerde farklı sürümlerle yaşayamaz. Kurucu ilke (m.0) + on madde:

| # | İlke | Meslektaş için ne demek |
|---|---|---|
| **0** | **Kurucu ilke — metodoloji tanım değil, DONANIMDIR** | Bu sistemi kullanan yapay zekâ, Türk hukukunda doğru çıktı için tanımlardan/özetlerden değil kurulu METODOLOJİDEN — tüm yeteneklerle fiilen donatılmış olarak — hareket eder. Bu yetenekler, modelin en verimli ve en başarılı işlem hacmini yaratan, kullanıcı ile yapay zekâ arasındaki KÖPRÜDÜR. |
| **1** | **Çaba ve kalite standardı** | Tasarruf yalnız **israftan** kesilir: aynı evrağı her adımda yeniden okumak, metni görüntü olarak açmak, bütünü yükleyip parçayı kullanmak. Muhakemeden, araştırmadan, unsur denetiminden **asla** kısılmaz. |
| **2** | **Usul esasa üstündür** | Usul denetimi esastan **önce** ve en az onun kadar ciddi yapılır. Süre, dosyadaki telafisi olmayan tek hatadır. Düstur çift yönlüdür: kendi usul zaafınız sıfırlanır, karşı tarafın kaçırdığı süre gizlenmez — derhâl ileri sürülür. |
| **3** | **Örnekleme ilkesi** | Metinlerdeki kanun/dava tipi listeleri kapsamı **daraltmaz**, yalnız metodu gösterir. Listede olmayan konu aynı metotla, kıyasen işlenir. Kapsam istisnasız tüm Türk hukukudur. |
| **4** | **Doğaçlama meşruiyeti** | Yöntemde serbestlik: muhakeme kurgusu, argüman dizilimi, üslup, strateji özgürce doğaçlanır. Sınır tek ve keskindir — **olguda asla**: künye, madde, tarih, tutar üretilemez. |
| **5** | **Doğrulama mimarisi** | **Teyit ≠ muhakeme.** Künyenin var olduğunu doğrulamak yetmez; tam metin çekilmiş, davaya bağı kurulmuş ve damgalanmış olmalıdır. Damgasız atıf, çıplak künyeden farksızdır. İki modelin hemfikir olması doğrulama **değildir**. |
| **6** | **Müvekkil-aleyhi çıktı yasağı** | Zaaf dış belgeye yazılmaz, ama iç analizde **saklanmaz**. Salt aleyhe içtihat dilekçeye giremez; cephanelikte durur ve ancak karşı taraf onu fiilen ileri sürerse çıkar. |
| **7** | **Anonimleştirme** | Sistem metinlerinde hiçbir müvekkil, karşı taraf veya dosya **ismen anılamaz**; tecrübe yalnız soyut örüntü olarak işlenir (Av.K. m.36 · KVKK). |
| **8** | **Simülasyon yasağı** | Bir parça, tarifinden taklit edilerek "çalıştırılmış" sayılmaz; fiilen çağrılmış olmalıdır. Yüklenemiyorsa çıktıya "fiziken yüklenemedi" diye **açıkça yazılır**. |
| **9** | **Başbakan denetimi** | `oa-pipeline` anayasayı icra ve denetim organıdır. Parça atlayarak, muhakeme kısarak maliyet düşürmek yasaktır. Karar materyali üretir; kararı avukat verir. |
| **10** | **Layer 0 — gizlilik** | Dış araca çıkan her içerik önce süzgeçten geçer. **UYAP girişi ve e-imza/PIN münhasıran avukata aittir**; sistem bunlar için kod yazmaz, yalnızca engeller. |

---

## Maliyet ekonomisi — dakika dakika ölçülmüş gerçek koşu

Aşağıdaki zaman çizelgesi tahmin değildir: gerçek, derdest bir istinaf
dosyasının (~200 evrak, 45 MB, 17'si OCR) **Claude Fable 5 (max efor)**
üzerinde tek prompt'la işlendiği koşuda, dakika dakika canlı kaydedilmiştir
(tam rapor: [SAHA-SONUCU.md](SAHA-SONUCU.md)):

| Dakika | Token | O anda ne oluyordu |
|---|---|---|
| 0 | 0 | Tek doğal-dil prompt girildi; başka hiçbir talimat verilmedi |
| ~1 | ~0 | Sistem kendiliğinden devraldı, `_oa/` çalışma kökü doğdu |
| 8 | 5,7k | **İngest çalışıyor** — 200+ evrak Python scriptiyle metne iniyor; model beklemede |
| 15 | 12,5k | İngest bitti: 202 birim, künye + indeks üretildi |
| 22 | 18k | İçtihat araştırması: Yargı Pro MCP'de isabetli sorgular |
| 30 | 25k | 11 karar + 3 norm teyitli; kütük ve ham döküm diskte |
| 35 | 29,1k | Analiz tamam, dilekçe taslağı yazılıyor |
| **49** | **45,6k** | **36 KB'lık ek beyan + geçerli .udf teslim edildi** |

Aynı sınıf iş, evrakı modele görüntü olarak yükleyen eski usulde **1M+ token**
yiyordu; yalnız analiz aşaması için 1,2M+ gözlenmişti. Fark **~26×** — ve
muhakemeden tek satır kısılmadan (dilekçe 11 bölümlü çıktı, her olgusal çapa
kaynağa izlendi, iki aleyhe içtihat iç cephanelikte tutuldu).

### Bu ucuzluk nereden geliyor — kodlama yapısı

Sır, anayasanın 1. maddesindedir: **tasarruf yalnız israftan kesilir,
muhakemeden asla.** Bunu mümkün kılan, ailenin iki katmanlı mimarisidir —
**model kurar, Python denetler:**

1. **Deterministik çıkarım (`oa_ingest.py`):** PDF/TIFF/UDF/EYP/DOCX evrak,
   modele hiç gösterilmeden Python'la metne iner (metin PDF → doğrudan,
   taranmış → OCR + kalite merdiveni). Token maliyeti: **sıfır** — bu iş
   CPU'da olur, bağlamda değil.
2. **Künye + indeks (`00-kunye.json`, `00-INDEX.md`):** model külliyatı
   toptan yüklemez; ucuz indeksten **seçici okur**. 45 MB görüntü yerine
   birkaç yüz KB hedefli metin.
3. **Denetim kapıları (script):** zorunlu unsur denetimi, künye teyidi,
   damga zinciri, teslim makbuzu, UDF geçerlilik kapısı — hepsi Python
   scriptidir; model "yaptım" der, script **kanıtlar**. Beyan token'ı yerine
   exit kodu.
4. **Muhakeme katmanı (model):** kıyas, strateji, antitez, kaleme alma —
   token buraya harcanır, yalnız buraya. 45,6k'nın büyük kısmı fiilen
   düşünmeye gitti; taşımaya değil.

Sonuç: pahalı olan katman (model muhakemesi) korunur, ucuzlatılabilen her
şey (okuma, doğrulama, biçim) koda iner. **Verim kaybı ve muhakeme kaybı
ölçülebilir düzeyde küçüktür; çıktı profesyonel sayılır düzeydedir** — dürüst
kayıp listesi dâhil tüm ölçüm SAHA-SONUCU.md'dedir.

---

## Bir dosya önünüze geldiğinde ne oluyor

1. **Evrak metne iner.** UYAP'tan indirdiğiniz PDF/TIFF/UDF/EYP/DOCX yığını bir kez
   ve en ucuz doğru yoldan metne çevrilir; taranmış olanlar OCR'dan geçer ve
   "⚠ teyit gerek" damgası alır. Sayım tutmuyorsa analiz **başlamaz**.
2. **Sorular sorulur.** Uzun analize girmeden önce talep, roller, aşama, **tebliğ
   tarihi**, eldeki ve eksik belgeler, karşı tarafın en güçlü kozu toplanır.
3. **Usul ve süre nöbete girer.** Bunlar bir "adım" değil, her aşamayı saran
   katmandır: dolan bir süre varsa diğer her işin önüne geçer.
4. **Olgu ve hukuk ayrı ayrı kurulur.** Kronoloji ve iddia↔delil matrisi bir yanda;
   norm, teyitli içtihat ve açık kıyas öbür yanda.
5. **Karşı taraf simüle edilir.** Sekiz cephede size gelebilecek her saldırı
   çıkarılır ve çürütülür; çürütülemeyen dürüstçe "artık risk" diye işaretlenir.
   Bu çıktı **size** gelir, dilekçeye girmez.
6. **Taslak yazılır, kapılardan geçer, UDF üretilir.** Zorunlu unsurlar, künye izi,
   içtihat muhakeme zinciri ve gizlilik denetlenir; sonuç tek bir "teslime hazır /
   değil" hükmüne bağlanır.
7. **Karar sizindir.** Sistem karar *materyali* üretir; nihai kararı avukat verir.

Tüm üretim, çalıştığınız klasörün içindeki `_oa/` yerel hafıza kökünde kalır.
**Müvekkil evrakı salt-okunurdur, değiştirilmez.**

---

## Aile — yirmi parça, tek tek

Parçaların bir kısmı **saf muhakeme parçasıdır** (yöntem disiplini), bir kısmı ise
yanında **deterministik denetim motoru** taşır. Bu ayrımı bilerek okuyun: makineyle
denetlenen yerde ölçüm vardır, saf muhakeme parçasında ise disiplinli yöntem.

### Çekirdek ve orkestra

#### [`ortak-avukat`](plugins/ortak-avukat/skills/ortak-avukat/) — çekirdek kimlik
Türk hukuku işi geldiğinde devreye giren varsayılan çalışma kimliğidir; kıdemli bir
eş-avukat duruşunu ve on maddelik anayasayı bağlama yükler. Tetiklenir tetiklenmez
işi `oa-pipeline`'a devreder — sizin elle parça çağırmanız beklenmez. Ailenin
anayasası fiziken bu parçanın altında durur ve diğer 19 parça oraya işaret eder;
yani bir ilke tek yerden değişir, yirmi yerde çelişmez. Ayırt edici kuralı şudur:
**devir sözle değil çağrıyla olur** — bir parçaya "devrettim" demek onu çalıştırmak
değildir, ve tarifinden taklit etmek halüsinasyonun ana kapısıdır.

#### [`oa-pipeline`](plugins/ortak-avukat/skills/oa-pipeline/) — Başbakan · 8 denetim scripti
Dosyayı 0. MANİFEST'ten 10. KAPANIŞ'a kadar sırayla yürüten ve her adımı denetleyen
icra organıdır. Bir adımın "yapıldı" iddiası yalnız beyanla kaydedilemez: kanıt
alanı boş bırakılamaz, gereksiz sayılan adım gerekçesiz geçilemez, ve o adımın
fiziksel çıktısı diskte yoksa kayıt yazılamaz. Analiz, evrak dökümü tamamlanmadan
başlayamaz; kıyas adımı içtihat muhakeme kaydı olmadan, kontrol adımı teslim
makbuzu olmadan kapanamaz. Turun sonunda tek bir soru sorulur — "boşluk var mı" —
ve boşluklu tur teslim edilemez; dosyanın canlı durumu (`_oa/DURUM.md`) defterden
**türetilir**, elle yazılmaz.

### Dosyayı ele alma

#### [`oa-ingest`](plugins/ortak-avukat/skills/oa-ingest/) — evrak metne iner · 1 script
UYAP klasöründeki her evrağın metnini **bir kez** ve en ucuz doğru yoldan çıkarır:
metin PDF'ten doğrudan, taranmış olandan OCR ile, UDF/EYP/DOCX'ten açarak. Her
belge için ayrı bir metin dosyası, bir künye kaydı ve bir indeks üretir; böylece
sonraki parçalar külliyatı görüntü olarak değil, ucuz metin ve indeks üzerinden
seçici okur. İndirilen evrak adedi künyedeki sayımla tutmuyorsa **analiz başlamaz**
— eksik evrak sessizce yok sayılamaz. OCR boş dönerse pes etmez: farklı çözünürlük
ve yönelimlerle yeniden dener, hâlâ boşsa o sayfanın görselini üretip "görsel
inceleme gerek" damgası basar.

#### [`oa-interview`](plugins/ortak-avukat/skills/oa-interview/) — ilk inceleme
Akışın en başındadır ve tek bir yönetici ilkesi vardır: önce sor, sonra analiz et.
Talep, roller, aşama ve merci, **tebliğ tarihi**, eldeki ve eksik belgeler, karşı
tarafın en güçlü kozu — bunlar toplanmadan uzun analize girilmez. Usul soruları
esas anlatımından önce sorulur, çünkü esasın en güçlü hâli bile dolan bir süreyi
kurtarmaz. Sorular tek tek değil, numaralı bir liste hâlinde toplu sorulur; böylece
yirmi mesajlık bir soru-cevap trafiği yerine tek turda tamamlanır. Toplananla
müvekkil lehine bir **ön dava teorisi** kurar ve size geri anlatır. Bu geri anlatım
bilinçlidir: yanlış bir varsayım varsa daha ilk dakikada düzeltilir, saatlerce
yanlış eksende çalışılmaz.

#### [`oa-alan`](plugins/ortak-avukat/skills/oa-alan/) — konumlama
Uyuşmazlığın hangi norma bağlandığını ve hangi yargı kolunda, HSK iş bölümü
ışığında hangi ihtisas dairesinin baktığını belirler. Bunu araştırma başlamadan
yapar; doğru daireye kilitlenmiş bir arama, geniş taramadan hem daha ucuz hem daha
isabetlidir. Dava türü başına unsur şablonları taşır (tasarrufun iptali, işe iade,
itirazın iptali, kıdem-ihbar gibi) ve bu unsurlar olgu matrisine taşınarak delilsiz
kalan unsur görünür kılınır. Ayırt edici kuralı bir **yasak bölgeler** listesidir:
geçmişte halüsinasyona yol açmış alanlarda künye, daire numarası veya parasal sınır
**ezberden yazılamaz** — doğrulanana kadar iddiadır.

### Her işi saran katmanlar

#### [`oa-usul`](plugins/ortak-avukat/skills/oa-usul/) — usulün esasa takaddümü · 1 script
"Usul esasa üstündür" düsturunun aile çapındaki uygulayıcısıdır ve bir adım değil,
her aşamayı saran katmandır. Dava şartı, görev/yetki, tebligat, harç, ehliyet ve
temsil, ıslah, eski hâle getirme ve kanun yolu şartlarını **üç ayrı cepheden**
denetler: karşı tarafın hatası (taarruz), müvekkilin hatası (savunma) ve kamu
gücünün hatası. Denetimde boşluk kalırsa analiz teslim edilemez. En sert kuralı bir
dil kilididir: tebliğ tarihi belgeli değilken "süresinden sonradır, usulden reddi
gerekir" gibi **kesin dil kurulamaz** — teyit kaydıyla yazılır ve açık uç bırakılır.

#### [`oa-sure`](plugins/ortak-avukat/skills/oa-sure/) — nöbetçi · 2 script
Dosyanın telafisi olmayan tek hatasını hesaplar: süre. Hem usul süreleri hem maddi
hukuk süreleri (zamanaşımı, hak düşürücü) aynı disipline tabidir. Hesap kara kutu
değildir; tebliğ gününün sayılmaması, araya giren tatilin süreyi uzatmaması ama son
gün tatile denk gelirse kayması gibi kurallar gerekçesiyle birlikte gösterilir.
Karşı tarafın fiilî işlem tarihi hesaplanan son güne karşı denenerek "kaçırılmış mı,
süresinde mi" sorusu da yanıtlanır. Geçmiş, bugün veya yaklaşan bir süre bulunursa
**diğer her işin önüne geçer** — sessiz kaçış yoktur.

#### [`oa-gizlilik`](plugins/ortak-avukat/skills/oa-gizlilik/) — Layer 0 · 1 script
Dış araca (bulut MCP, web, e-posta, üçüncü parti bağlayıcı) çıkacak her içeriği,
gönderilmeden **önce** tarar ve üç karardan birini verir: geçir, sor, engelle.
Müvekkil verisi, TC kimlik, dosya/esas no, sağlık ve ceza verisi, hesap/kart
bilgisi taranır; kimlik numarası ve kart numarası algoritmik olarak da sınanır.
Mutlak yasak listesi her modda geçerlidir: **UYAP giriş akışı, e-imza/e-mühür, PIN
ve parola, API anahtarı, IBAN** — bunlar için sistem kod yazmaz, doldurmaz,
göndermez. Tarama çökerse veya dosya okunamazsa karar otomatik olarak **engelle**
olur; şüphede daima daha kısıtlayıcı olan seçilir.

#### [`oa-illiyet`](plugins/ortak-avukat/skills/oa-illiyet/) — nedensellik grafı · 1 script
Dosyadaki kişileri, şirketleri, kamu kurumlarını, nesneleri ve delilleri düğüm;
aralarındaki ilişkileri ve neden-sonuç bağlarını kenar sayarak yönlü bir graf kurar.
İki kenar türünü bilinçli ayırır: durağan ilişki (ortaklık, temsil, işçi-işveren,
alacaklı-borçlu) ile dinamik illiyet (fiil → netice → zarar). Gözün kaçıracağı
yapısal boşlukları mekanik olarak açığa çıkarır: hiçbir yere bağlanmamış düğüm,
kopuk zincir, iki grubu tek başına bağlayan **köprü düğüm** (muvazaa sinyali) ve
illiyeti kesme adayları (mücbir sebep, mağdur veya üçüncü kişi kusuru). Her kenar
"teyitli / iddia / karine" olarak etiketlenir; **doğrulanmamış illiyet yok
sayılır** ve uydurma bir karar üzerine zincir kurulamaz.

### Olgu ve hukuk

#### [`oa-vakia`](plugins/ortak-avukat/skills/oa-vakia/) — olgu ve delil · 1 script
Dosyanın olgu yarısını disipline eder: olayları kronolojiye dizer, her iddiayı
dayandığı delile eşler. İki tür boşluğu mekanik olarak yakalar — **delilsiz iddia**
(ispat boşluğu) ve hiçbir iddiaya bağlanmamış **yetim delil**. İspat durumu kapalı
bir kümedir (belgeli, tanık, bilirkişi, karine, ikrar, yemin, ispatsız); "ispatsız"
işaretlenen olgu otomatik boşluk sinyali üretir. Görüntü veya taranmış evrak
"okudum" diye varsayılamaz: ya OCR'dan geçer ya da "okunamadı, elle inceleme
gerekli" denir.

#### [`oa-ictihat`](plugins/ortak-avukat/skills/oa-ictihat/) — teyit
Her argümanın normunu ve künyesini resmî kaynaktan (Yargı Pro, AYM, Mevzuat MCP)
**fiilen** çeker. Kararın tam metnini diske ham döküm olarak yazar; böylece daha
sonra dilekçeye giren her alıntı, hafızadan değil o dosyadan gelir. İki araç
sınıfını ayırır: arama araçları tam metin döndürmediği için onlardan damga çıkmaz,
tam metin çeken araçlarda ise damga, davaya bağ ve döküm zorunludur. Bu parça
**teyit eder, damgayı atamaz** — muhakeme başka parçanın işidir ve bu ayrım
sistemin belkemiğidir. "Teyitli" etiketi yalnız fiilen yapılmış bir çağrıya konur;
kararın kaynak bağlantısı da tam o anda kaydedilir. Gerekçesi basittir: yazım
aşamasında bir bağlantı *hatırlanamaz*, ancak uydurulabilir — bu yüzden kayıt
yoksa dilekçede parantez hiç açılmaz.

#### [`oa-kiyas`](plugins/ortak-avukat/skills/oa-kiyas/) — açık kıyas · 1 script
Hukuki sonucu örtük sezgiden çıkarıp denetlenebilir üçlüye oturtur: büyük önerme
(norm + teyitli içtihat) → küçük önerme (vakıa ve illiyet grafı) → sonuç. Normun
her unsurunun bir vakıaya eşlenip eşlenmediği tek tek denetlenir; eşleşmeyen unsur
ispat boşluğu veya hukuk boşluğu olarak görünür kalır. Teyitli bir kararı
"muhakeme edilmiş" hâle getiren yer burasıdır: kararın taşıyıcı ilkesi verbatim
alınır, dosyayla örtüşen somut noktalar kurulur, farklar yazılır ve damga
**bunlardan türetilir** — beyan edilmez. Damga dört değerlidir (lehe, aleyhe,
aleyhe-ayırt, nötr) ve **damga atanmazsa kayıt nötr sayılır**, yani kullanılamaz.

### Karar ve savunma

#### [`oa-strateji`](plugins/ortak-avukat/skills/oa-strateji/) — yol seçimi
Analizi bir karara dönüştürür: en az iki gerçek alternatif kurar (dava, sulh, icra,
idari başvuru, bekleme) ve her birini maliyet, fayda, aşağı yön ve **tahsil
edilebilirlik** boyutuyla tartar. "Haklı olmak ≠ tahsil etmek" kuralı gereği, karşı
tarafta malvarlığı yoksa bu tespit kararın önüne konur — kazanılan ama tahsil
edilemeyen bir karar müvekkile fayda değil masraf getirir. Başarı olasılığı **sayı
değildir**: "%72 kazanırsınız" denmez, çünkü böyle bir sayının arkasında hiçbir
ölçüm yoktur. Onun yerine nitel bir bant (güçlü, dengeli, zayıf, belirsiz) ve o
bandın gerekçesi verilir: hangi delil, hangi içtihat eğilimi, hangi usul riski.
Ayrıca "şu olursa şu yola geç" tetikleri kurulur, böylece karar tek seferlik değil
izlenebilir olur.

#### [`oa-antitez`](plugins/ortak-avukat/skills/oa-antitez/) — gizli cephanelik · 1 script
Müvekkilin tezine gelebilecek saldırıları sekiz sabit cephede eksiksiz çıkarır ve
her birini çürütür; çürütülemeyeni dürüstçe **artık risk** diye işaretler. Cephe
gücü ve dayanak durumu serbest metin olarak yazılamaz, kapalı değerlerle
işaretlenir; değerlendirilmemiş bir cephe "kör nokta" olarak yakalanır. Bu parçanın
çıktısı **karşı tarafa değil yalnız size** gelir. En sert kuralı sunum
disiplinidir: karşı taraf bir tezi fiilen ileri sürmeden ona karşı dilekçeye
önleyici çürütme konmaz — konursa karşı tarafı silahlandırırsınız. Hazırlanan
çürütme cephaneliktir; mühimmat ateş değildir.

### Üretim

#### [`oa-dilekce`](plugins/ortak-avukat/skills/oa-dilekce/) — yazım ve teslim biçimi · 4 script
Dava, cevap, istinaf, temyiz, AYM bireysel başvuru, yemin teklifi ve idari kanal
dilekçelerinin zorunlu unsurlarını playbook olarak uygular ve taslağı yazar.
Paragrafın iç mantığı (iddia → norm → içtihat → örtüşme → sonuç) **görünmez
iskelettir**: yüzeye etiket olarak sızmaz, metin akıcı ve tez-omurgalı örülür.
Çıplak künye yasağı burada fiilen kapanır: dilekçeye yalnız lehe veya ayırt edilmiş
aleyhe damgalı, künyesi, kaynak izi, ilgili kısmı ve davaya bağı tam olan kararlar
girer. Nihai teslim biçimi olan UDF dosyasını üretir ve bunu **elle kurmaz** —
resmî araçla üretir; araç yoksa veya oturum gerekiyorsa bozuk dosya yazmak yerine
durur ve size ne yapmanız gerektiğini söyler.

#### [`oa-sozlesme`](plugins/ortak-avukat/skills/oa-sozlesme/) — akdî metin · 1 script
Sözleşmeyi iki modda ele alır: **tahrir**de müvekkil lehine ama geçerlilik
sınırının içinde kloz kurar, **inceleme**de karşı taslaktaki tuzağı imzadan önce
yakalar. Sıralama bilinçlidir — şekil şartı, imza yetkisi ve temsil, ehliyet ve
emredici hukuk denetimi kloz içeriği tartışmasından **önce** gelir, çünkü şekli
sakat bir sözleşme en parlak klozu bile taşıyamaz. Zorunlu kloz kategorileri
sayılıdır ve bir kategorinin sessizce atlanması engellenir; "gereksiz" denen
kategori gerekçesiz bırakılamaz. Risk nitel bantlarla verilir; uydurma bir sayısal
skor üretmek mümkün değildir.

### Teslim

#### [`oa-kontrol`](plugins/ortak-avukat/skills/oa-kontrol/) — son kapı · 4 script
Doğrulama mimarisinin son halkasıdır: teslim öncesi künye izini, zorunlu unsurları,
içtihat muhakeme zincirini, gizliliği ve defter bütünlüğünü sabit sırada koşturur.
Ayırt edici kuralı bir **tek ölçüt** kuralıdır: kapıları teker teker sayıp "kaçı
yeşil" diye elle toplamak yasaktır; teslime hazır olup olmadığını yalnız orkestra
script'inin çıkış kodu söyler. Her koşuda bir **teslim makbuzu** yazılır — başarılı
da olsa başarısız da olsa iz kalır, taslağın özeti kaydedilir, sonradan değişirse
fark edilir. Bir engelleyici kapının script'i çalıştırılamıyorsa bu "atlandı"
sayılmaz, engellenmiş sayılır: belirsizlik teslimin lehine yorumlanmaz.

### Ceza dalı — aynanın iki yüzü

#### [`oa-mudafii`](plugins/ortak-avukat/skills/oa-mudafii/) — sanık/şüpheli savunması
Ceza dosyasında müdafilik üstlenildiğinde omurgaya savunma merceğini takar.
Aksiyomu nettir: **suçsuzluğu biz ispatlamayız** — iddia makamının ispatındaki
boşluğu, kuşkuyu ve hukuka aykırılığı gösteririz. Suçun maddi ve manevi unsurlarını
tek tek vakıaya eşler; eşleşmeyen unsur beraat sebebidir. Delil cephesini madde
adresleriyle tarar (doğrudan doğruyalık, hukuka aykırı delil yasağı, eksik
inceleme, atfı cürüm beyanı, dijital ve ses kaydı aidiyeti) ve kanun yolu
sürelerini ayrı bir nöbet tablosunda tutar. Sunum disiplini burada da geçerlidir:
iddia makamının henüz ileri sürmediği bir teze önleyici cevap vermek, kendi zayıf
noktanızı işaret etmektir.

#### [`oa-musteki-vekili`](plugins/ortak-avukat/skills/oa-musteki-vekili/) — müşteki/mağdur vekilliği
Müdafiliğin ayna kutbudur ve tam tersini yapar: unsur yokluğunu aramak yerine her
unsuru **kurar** ve delile eşler. İspat boşluğunu somut delille kapatır, eksik
soruşturmayı tamamlatır, delil karartma veya kaçış riski somutsa koruma
tedbirlerini gündeme getirir. Şikâyet süresi ve zamanaşımı burada da nöbettedir.
Anayasal süzgeci şudur: kuşkulu bir atfa dayanan güçlü görünümlü iddia, zayıf ama
sağlam olandan **daha tehlikelidir** — desteksiz her isnat açıkça etiketlenir ve
şüphelinin masumiyet karinesini ihlal eden aşırı dil kullanılmaz.

### Öğrenme

#### [`oa-usta`](plugins/ortak-avukat/skills/oa-usta/) — çırak · 1 script
Ailenin öğrenen ucudur: işlenen dosyalardan ders damıtır ve tekrar eden bir işi
yeni bir parça taslağına çevirir. Aynı iş üçüncü kez elle yapıldığında, siz
istemeseniz de "bunu kalıba dökelim mi" sorusunu gündeme getirir. İkinci ve daha
sert görevi ailenin yapısal sağlığını denetlemektir: her parçanın tanımı, adı,
klasörüyle uyumu, anılan scriptlerin gerçekten var olup olmadığı ve sürüm
işaretlerinin tutarlılığı makineyle sınanır. Bu denetim her paketlemeden önce
koşar ve **hata varken paketleme yapılmaz** — yani bozuk bir aile dağıtıma çıkamaz.
Damıtılan her ders anonimleştirme süzgecinden geçer: hiçbir dosya, müvekkil veya
karşı taraf ismen anılamaz, geriye yalnız soyut örüntü kalır.

---

## Sistemin **yapmadıkları** (dürüst sınırlar)

Bir meslektaş için, sistemin ne yaptığı kadar ne yapmadığı da önemlidir:

- **Hukuki sonucu garanti etmez.** Karar materyali üretir; kararı avukat verir.
- **"İyi dilekçe" demez.** Yalnız "unsur var/yok", "künye teyitli/teyitsiz",
  "biçim geçerli/geçersiz" der. Hukuki isabet hükmü avukata aittir.
- **Sayı uydurmaz.** Başarı olasılığı yüzde olarak verilmez; risk skoru
  üretilmez — nitel bantlar ve gerekçeleri verilir.
- **Çelişkiyi "yanlış" diye adlandırmaz.** Dilekçedeki rakamların birbiriyle
  tutarlılığını *görünür kılar*; hükmü siz verirsiniz.
- **E-imzanın geçerliliğini doğrulamaz.** İmzalı bir nüshayı tanır ve bildirir,
  ama kriptografik doğrulama UYAP'ın işidir.
- **UYAP'a girmez, e-imza atmaz.** Bu adımlar münhasıran avukata aittir; sistem
  onlar için kod dahi yazmaz.
- **Resmî kaynak bağlı değilse künye doğrulayamaz** — ve bunu gizlemez, "teyit
  edilemedi" damgası basar.

---

## Gereksinimler ve Kurulum

Sistem dört katmandır: **(1) Claude Code** · **(2) Python + Tesseract** (evrak çıkarımı, deterministik denetim) · **(3) Node.js/npx** (UDF üretimi — UYAP dilekçe formatı) · **(4) Yargı Pro MCP** (içtihat/mevzuat doğrulaması).

### A) Claude Code
Claude Code (CLI, Desktop veya web) kurulu ve oturum açık olmalı. Eklenti/skill ve MCP desteği bu ortamdan gelir.

### B) Python 3.10+ — evrak çıkarımı & denetim scriptleri
`oa-ingest` (0. adım: evrak → ucuz metin) ve tüm deterministik denetim scriptleri Python ile çalışır.

```bash
python --version
```

```bash
pip install pymupdf pillow
```

`pymupdf` PDF metin/görüntü çıkarımı, `pillow` TIFF/JPG/PNG işleme içindir. Bunlar olmadan PDF/görüntü evrak (metin PDF dahil) işlenemez.

### C) Tesseract OCR — taranmış evrak (önerilir)
Taranmış/fontsuz PDF ve görüntü (TIFF/JPG) evrakların OCR'ı için:

- **Windows:** [UB-Mannheim kurucusu](https://github.com/UB-Mannheim/tesseract/wiki) — kurulumda **Turkish (`tur`)** dil paketini seç **ve** "Add Tesseract to PATH" işaretle
- **Linux:** `sudo apt-get install tesseract-ocr tesseract-ocr-tur`
- **macOS:** `brew install tesseract tesseract-lang`

Doğrula:

```bash
tesseract --version
```

Tesseract yoksa metin PDF/UDF/DOCX yine işlenir; taranmış evraklar **"YÜKLENEMEDİ (OCR yok)"** damgasıyla künyeye girer — sessiz atlama yoktur.

### D) Node.js + `udf-cli` — UDF üretimi (dilekçe teslimi için ZORUNLU)
UYAP'a sunulacak `.udf` dosyası **yalnız** Yargı Pro'nun `udf-cli` paketiyle üretilebilir. **UDF elle yazılamaz** — elle üretilen zip/XML dosyaları UYAP Doküman Editöründe açılmaz (sahada doğrulandı: editör `resolver="hvl-default"` iskeletini arar, bulamazsa belgeyi açmaz).

```bash
node --version
```

```bash
npx -y udf-cli@latest login
```

```bash
npx -y udf-cli@latest whoami
```

- Giriş **tek seferlik**tir; token `~/.config/yargi/token.json`'da tutulur ve `udf-cli`, `uyap-tiff-cli`, `uyap-pdf-cli` arasında **paylaşılır**.
- Başsız/otomasyon ortamında tarayıcı akışı beklemede kalır: `issue_cli_login_code` MCP aracıyla tek kullanımlık kod alıp `udf-cli login --token <kod>` kullanılır.
- Giriş yapılmamışsa sistem **fail-closed** davranır: bozuk UDF üretmez, size giriş talimatı verir.
- Ayrıntı: [`skills/oa-dilekce/references/uyap-belge-formatlari.md`](plugins/ortak-avukat/skills/oa-dilekce/references/uyap-belge-formatlari.md)

### E) Yargı Pro MCP — içtihat/mevzuat doğrulaması (ZORUNLU)
İçtihat/mevzuat/kurum-kararı doğrulaması Yargı Pro MCP sunucusuna dayanır (Yargıtay, Danıştay, AYM, AİHM, Bedesten, Mevzuat, Resmî Gazete, YÖK Tez). Claude Code **connectors** bölümünden şu adresi ekleyin:

```
https://yargi.betaspacestudio.com/mcp
```

veya komut satırından:

```bash
claude mcp add --transport http yargipro https://yargi.betaspacestudio.com/mcp
```

OAuth akışını tamamlayın. **Bu bağlantı olmadan** künye doğrulaması yapılamaz; anayasa gereği içtihat "teyit edilemedi" damgasıyla işlenir ve dış çıktıya "teyitli" giremez.

### F) Eklentiyi kurun

```
/plugin marketplace add bcancapar-spec/ortak-avukat
```

```
/plugin install ortak-avukat@ortak-avukat
```

Kurulumdan sonra Claude Code'u **yeniden başlatın**. Skill listesinde tek bir `ortak-avukat` ailesi (22 skill) görünmeli.

> **Güncelleme takılırsa:** eklentiyi ve marketplace'i kaldırın, Claude Code'u kapatın,
> `~/.claude/plugins/cache/ortak-avukat` ile `~/.claude/plugins/marketplaces/ortak-avukat` dizinlerini silin,
> yeniden ekleyip kurun. Sürüm etiketi değil **dosya kanıtı** ile doğrulayın (aşağıdaki "Doğrulama").

### G) Kontrol listesi
- ✅ **Plugins / Skills** etkin, 22 skill yüklü
- ✅ **Yargı Pro MCP** bağlı (OAuth tamam)
- ✅ **Python + pymupdf + pillow** PATH'te
- ✅ **Tesseract** (`tur` dil paketiyle) PATH'te
- ✅ **Node.js/npx + `udf-cli login`** yapılmış (UDF üretimi için)
- ℹ️ **Çok çekirdekli CPU** — `oa-ingest` paralel çalışır (`--isci` otomatik = `min(çekirdek, 8)`)

---

## v0.5.5 — Bu sürümde ne var

v0.5.5'in tek cümlelik tezi: **"advisory kapı = olmayan kapı"** — talimat modeli bağlamaz, mekanik zincir bağlar. Aşağıdakiler bu tezin uygulamasıdır.

### Aktivasyon çekirdeği
| Madde | Ne yapar |
|---|---|
| **Brif restorasyonu** | Alt-ajan brifinde sert kurallar en görünür sıraya alındı; "advisory/serbesttir" tonu kaldırıldı |
| **Tek-komut muhakeme ritüeli** | `oa_hafiza.py teyit --damga --bag --ayirt --ilgili-kisim --dokum-icerik` → **tek çağrı** ile ham dökümü diske yazar, kütüğe işler, muhakeme kaydını üretir. (v0.5.3'ün "bir karar = bir dosya" pahalı ritüeli terk edildi — pahalı ritüel yapılmaz, ucuz ritüel yapılır) |
| **ARAMA / GETİR ayrımı** | Arama araçları damgasız serbest kütüklenir; tam metin çeken araçlarda damga + davaya-bağ + döküm **zorunlu** |
| **DAMGA çapraz kontrolü** | Kütükteki (append-only) son damga ile muhakeme kaydındaki damga farklıysa **engel** — aleyhe kararın sessizce lehe gösterilmesi kapanır |
| **Çok-bölümlü muhakeme kaydı** | Tek dosyada birden çok karar bölümü desteklenir (G1/G2/G3 semantiği değişmeden) |
| **Gate G döngü kırıcı** | `pipeline_kayit` ↔ `tam_tur` karşılıklı çağrısı in-process import ile çözüldü |

### Zorlama zinciri
| Madde | Ne yapar |
|---|---|
| **Teslim makbuzu** | `teslim_paketi.py` her koşuda `_oa/defter/teslim-makbuz.json` yazar (taslak sha256 + kapı-başına exit); makbuzsuz teslim koşan kapılarca kesilir |
| **Önkoşul-artefakt kapısı** | Adım kaydı, o adımın fiziksel artefaktı diskte yoksa yazılamaz (adım 5 kıyas ve adım 9 kontrol blokleyici; 3/4/6/7 uyarı) |
| **İngest-önce kapısı** | `00-kunye.json` mutabakatı diskte yokken adım 1+ "UYGULANDI" yazılamaz — **analiz, ingest bitmeden başlayamaz** |
| **Model-bağımsız tetik** | Plugin `Stop`/`SessionEnd`/`PostToolUse` hook'ları: oturum kapanırken ve dilekçe-şekilli çıktı yazıldığında defter denetimi + metrik otomatik koşar |
| **`_oa/DURUM.md`** | Pipeline defterinden **türetilen** canlı durum raporu: adım tablosu, kapı çıkışları, künye sayaçları, uyarılar, "avukat kararı bekleyen", "sıradaki" |

### Denetim ve ekonomi
| Madde | Ne yapar |
|---|---|
| **[F] içtihat-muhakeme kapısı varsayılan AÇIK** | `dilekce_denetim.py` artık her koşuda içtihat zincirini denetler |
| **Kapanış denetimi** | `oturum-kapat` defter denetimini fiilen koşar; çıktı kesmesiz devir notuna yazılır |
| **`oa_ingest --onbakis N`** | Meşru "hızlı ön bakış" kanalı — ayrı artefakta yazar, ana ingest hattına dokunmaz (gölge/uydurma çıkarım hattı ihtiyacını ortadan kaldırır) |
| **Sözleşme-dışı dizin bekçisi** | `_oa/` altında tanımsız dizin = görünür uyarı (tek-yazar tablosu) |
| **Canlı senkron kapısı** | Bayat working memory üstüne "UYGULANDI" yazılamaz |
| **Ölçüm** | `oa_metrik.py`: analiz token raporu, override/şerh oranı, görünmez-kaçış sayaçları |

### Muhakeme katmanı
| Madde | Ne yapar |
|---|---|
| **Dava tezi (M1)** | Tek paragraflık tez working memory'nin başında; her pas ve brifin ilk satırında |
| **Kıyas şeması (M2)** | Muhakeme kaydı: RATIO (taşıyıcı ilke, verbatim) + ÖRTÜŞME (en az 3 somut nokta) + FARKLAR → **damga bunlardan türetilir**, beyan edilmez |
| **Antitez pası (M3)** | `oa-antitez` çıktısı `oa-dilekce`'nin girdisi; aleyhe tarama iç dosyaya, dilekçeye yalnız duyulmuşsa |
| **Unsur şablonları (M4)** | Dava türü başına unsur listesi (tasarrufun iptali, işe iade, itirazın iptali, kıdem-ihbar); delilsiz unsur görünür |
| **Kronoloji + süre penceresi (M5)** | İlliyet grafına zaman katmanı; `hesapla_sure` pencereleri bindirilir |
| **İçtihat portföyü (M6)** | Dilekçe gövdesine en güçlü 3-5 karar (HGK/İBK > ihtisas dairesi > diğer; yeni > eski); kalanı kütükte yedek |
| **Avukat kararı bekleyen (M7)** | Stratejik çatallar `DURUM.md`'de ayrı bölüm — model sessizce karar vermez |

### Evrak ve teslim
| Madde | Ne yapar |
|---|---|
| **OCR nöbetçisi** | OCR boş/çöp dönerse deterministik yeniden deneme (DPI/yönelim/psm), hâlâ boşsa **sayfa görselleri** üretilir + `OCR-BOŞ → GÖRSEL İNCELEME GEREK` damgası (sessiz körlük biter) |
| **Gate A — sayfa haritası** | 40.000 karakteri aşan evrak için md yanında `<dosya>.harita.json`: deterministik, **kayıpsız** yapısal bölme (özet DEĞİL) — büyük evrak tam yüklenmeden ilgili sayfası okunur |
| **UDF hattı** | `md → inline-CSS HTML → udf-cli html2udf → .udf`. Elle zip/XML üretimi **kaldırıldı**; araç yoksa fail-closed |
| **UYAP format referansı** | UDF/TIFF/PDF okuma-yazma kuralları, HTML yazım şeması, dilekçe kalıpları eklentiye klonlandı |

### Yazım doktrini
- **"Künyeyi bulmak yetmez; kararın müvekkilin işine yarayıp yaramadığının muhakemesi güç çarpanıdır — çıplak künye sıfırdır."**
- **Görünmez iskelet:** İDDİA→NORM→İÇTİHAT→ÖRTÜŞME→SONUÇ paragrafın **iç mantığıdır**, yüzeye etiket olarak sızmaz
- **Üslup:** kanun-yolu playbook'una bağlı, tez-omurgalı, akıcı
- **Kusur→Sonuç→Talep asimetrisi:** karşı tarafın kusuru tespit edilir, sonucu yazılır, **giderilmesine yönelik talep kurulmaz**

---

## v0.5.5.1 — Saha testi düzeltmeleri

v0.5.5 gerçek bir dosyada (214 evrak, bakir klasör, metodoloji talimatı verilmeden) test edildi. Ekonomi hedefleri tuttu; ama üç **tetik** boşluğu görüldü: mekanizmalar sağlamdı, **çağrılmıyorlardı**. Bu sürümün dersi tek cümle: *kapının gücü kodunda değil tetiğindedir.*

| Düzeltme | Ne yapar |
|---|---|
| **Working memory tetiği** | `dosya-analiz.md` bizim biçimimizde değilse (elle yazılmış/bozulmuş), hook gövdesi `--senkron`'u **kendiliğinden** koşturur ve çalışma evraklarını kayıpsız geri gömer. Ritüelin çağrılmasını beklemez. Onarım **görünürdür** ve TAMAM üretmez — Gate G+ fail-closed kalır |
| **Defter-muhakeme denge uyarısı** | Kütükteki DAMGA'lı satır sayısı muhakeme kaydındaki bölüm sayısından fazlaysa uyarır. `teyit --damga` ikisini birlikte yazar; fark, satırın script dışında (elle) eklendiğini ve o künyelerin muhakemesinin hiç yapılmadığını gösterir |
| **Kök dosya bekçisi** | Sözleşme-dışı bekçisi yalnız `_oa/` altındaki **dizinlere** bakıyordu; kökteki serbest **dosyalar** kör noktadaydı. Artık görünür uyarı üretir (bloklamaz) |

### v0.5.5.2 — UDF geçerlilik kapısının iki kör noktası

Saha oturumundan gelen çevrim reçetesi üzerine kapı gerçek bir dilekçede sınandı ve **iki kusur** çıktı:

| Kusur | Düzeltme |
|---|---|
| **Yanlış-BLOK (ağır):** süreklilik denetimi yalnız `<content>` elemanlarına bakıyordu; gerçek `udf-cli` çıktısında `<tab/>` de offset taşır. Avukatın UYAP'ta **açıldığını teyit ettiği** 46.336 karakterlik dilekçe "offset süreksiz: beklenen 61, bulunan 62" ile **GEÇERSİZ** işaretleniyordu — kapı, korumaya çalıştığı teslimi kesiyordu | Denetlenen invaryant "paragraflar ardışık" değil **"offset taşıyan TÜM elemanlar CDATA'yı boşluksuz/örtüşmesiz döşer"** oldu. Etiket adı beyaz-listelenmedi (yarın `<space/>` gelirse yine yanlış-BLOK olurdu): ölçüt attribute'un **varlığı** |
| **Kör nokta:** kapı dosyayı yalnız **kendi ayrıştırıcımızın** varsayımına göre sınıyordu — sahada bizi yakan hata sınıfı tam olarak "bizim round-trip'imizi geçen ama UYAP'ın açmadığı dosya"ydı | **5. bacak: resmî okuyucu tanığı** — dosya, onu üreten aracın kendi okuyucusuyla (`udf-cli udf2md`) geri okunur. Üç durum ayrı tutulur: **OK** / **RET** (blokleyici) / **YAPILAMADI** (ağ-oturum yok → görünür uyarı, bloklamaz; "doğrulandı" sayılmaz) |

> Sahada şüphelenilen dört kusur (Gate A haritası, muhakeme dosyası yazımı, dava tezi, kayıpsız senkron) sentetik yeniden üretimle sınandı ve **dördü de sağlam çıktı** — bu yüzden kod değil tetik düzeltildi. Yeniden üretim testleri `tests/test_v0551_saha_tetikleri.py` içindedir.

---

### v0.5.5.3 — içerik hakemi, sicil desenleri, içtihat bağlantıları

| Ekleme | Ne yapar |
|---|---|
| **Bağımsız içerik hakemi (zorunlu adım)** | Mekanik kapıların hepsi yeşilken bile içerik yanlış olabilir: sahada, dilekçenin nakden tazmin savunması **kendi başka bölümüyle aritmetik olarak çelişiyordu**. Teslimden önce ayrı bir denetçi "çürütmeye çalış" brifiyle koşar — aritmetik tutarlılık, alıntı sadakati, dayanaksız olgu, niteleme doğruluğu, genelleme denetimi |
| **[J] Sayı/tarih haritası** (advisory) | Aynı sayının geçtiği tüm yerleri satır no + bağlamıyla yan yana koyar. Kapı çelişkiyi **söylemez, görünür kılar** — hüküm hakemin. Künye/madde numaraları haritaya girmez (gürültü), binlik ayracı normalize edilir (`1.100` = `1100`), kırpma yapılırsa kaç kalemin dışarıda kaldığı **sayıyla** bildirilir |
| **Ticaret sicili desenleri** | TTSG'yi delil olarak okuma rehberi: noter künyesi madeni, ardışık yevmiye = tek karşılıklı anlaşma göstergesi, TTK m.36/3 aleniyet bağı, takas/ivaz savunma kalıbı — ve kalıbın **dürüst sınırı** (birebir emsal bulunamadı; kalıp norm üzerinde durur). **Kritik niteleme:** TTSG'deki yevmiye genel kurul kararının TASDİK yevmiyesidir, pay devir sözleşmesinin yevmiyesi değildir |
| **İçtihat kaynak bağlantısı** | Dilekçede künyenin ardından **parantez içinde** kararın resmî bağlantısı yayımlanır. Bağlantı yalnız teyit anında `teyit --kaynak-url` ile kaydedilmiş olandır; **kayıt yoksa parantez hiç açılmaz** — uydurma bağlantı çıplak künyeden daha kötüdür (çıplak künye "teyit edilmedi" der, sahte bağlantı "teyit edildi" der) |

## Kullanım / iş akışı

1. **Evrakı indir:** UYAP dosyasındaki evrakları (PDF/TIFF/UDF/EYP/DOCX) bir klasöre indir
2. **O klasörde Claude Code başlat**
3. **Prompt ver:** *"Bu davada davalı X vekiliyim, dosyayı analiz et ve cevap dilekçesi hazırla"* gibi — metodoloji talimatı vermene gerek yok, sistem kendi disiplinini işletir
4. **Sistem ne yapar:** evrakı en ucuz doğru yoldan metne çevirir → working memory kurar → içtihat/mevzuatı Yargı Pro'dan doğrular ve **damgalar** → kıyas/antitez/strateji üretir → dilekçeyi yazar → teslim öncesi mekanik kapılardan geçirir → UDF üretir
5. **Sen ne yaparsın:** `_oa/DURUM.md`'ye bak (nerede kalındı, ne bekliyor), üretilen UDF'i UYAP editöründe **aç ve teyit et**, hukuki isabeti değerlendir

Tüm üretim çalışılan klasörün `_oa/` yerel hafıza kökünde kalır. **Müvekkil evrakı salt-okunurdur, değiştirilmez.**

### `_oa/` yapısı
```
_oa/
├── metin/          # ingest çıktısı: 00-INDEX.md, 00-kunye.json, NNN-*.md, *.harita.json
├── analiz/         # dosya-analiz.md (working memory) + .json
├── cikti/          # çalışma evrakları: NN-parça-içerik.md, dilekçe, UDF
├── teyit/          # kunye-teyit.md (künye kütüğü) + dokum/ (ham MCP dökümleri)
├── defter/         # pipeline-olaylar.jsonl, pipeline-durum.json, teslim-makbuz.json
├── devir/          # oturumlar arası devir paketleri
├── araclar/        # eklentiden kopyalanan deterministik scriptler
└── DURUM.md        # türetilmiş canlı durum raporu
```

---

## Doğrulama

### Kurulumun doğru olduğunu **dosya kanıtıyla** teyit et
Sürüm etiketi yetmez — kurulu cache'te sürümün kodunun fiilen bulunduğunu doğrula:

```bash
ls ~/.claude/plugins/cache/ortak-avukat/ortak-avukat/
```

```bash
grep -l teslim-makbuz ~/.claude/plugins/cache/ortak-avukat/ortak-avukat/*/skills/oa-kontrol/scripts/teslim_paketi.py
```

İlk komut yalnız güncel sürüm klasörünü göstermeli — eski sürüm klasörleri silinmiş olmalı, yoksa hangi kodun koştuğu belirsizdir.

### Geliştirici doğrulaması
Depo kökünde:

```bash
python -m pytest tests -q
```

```bash
python plugins/ortak-avukat/skills/oa-usta/scripts/aile_dogrula.py plugins/ortak-avukat/skills
```

İlki deterministik denetçilerin regresyonunu (**806 test**), ikincisi ailenin yapısal sağlığını (frontmatter, name↔klasör, sürüm tutarlılığı, anılan scriptlerin varlığı) denetler.

---

## Depo yapısı

```
ortak-avukat/
├── .claude-plugin/marketplace.json
├── plugins/ortak-avukat/
│   ├── .claude-plugin/plugin.json
│   ├── hooks/hooks.json              # model-bağımsız tetik
│   └── skills/                       # 22 skill
│       ├── ortak-avukat/             #   çekirdek kimlik + references/anayasa.md
│       ├── oa-pipeline/              #   orkestrasyon + tam_tur + pipeline_kayit + oa_hafiza + oa_metrik
│       ├── oa-ingest/                #   0. adım evrak çıkarımı (paralel, OCR nöbetçili)
│       ├── oa-kontrol/               #   teslim kapıları + içtihat muhakeme denetimi
│       ├── oa-dilekce/               #   dilekçe yazımı + UDF hattı + UYAP format referansı
│       └── …                         #   oa-alan, oa-vakia, oa-kiyas, oa-antitez, oa-usul, oa-sure, …
├── tests/                            # 806 pytest
├── README.md · LICENSE · NOTICE
```

Parçaların tam kataloğu ve anayasal ilkeler: **[plugins/ortak-avukat/README.md](plugins/ortak-avukat/README.md)**

---

## Gizlilik

Bu depo **hiçbir müvekkil verisi veya MCP kimlik bilgisi içermez**. Çalışma evrakı (`_oa/`) `.gitignore` ile dışlanmıştır. Dış araca (bulut MCP/web) veri çıkışı `oa-gizlilik` **Layer 0** süzgecine tabidir (müvekkil verisi, TCKN, IBAN, telefon, e-posta, plaka, sağlık/ceza verisi taranır; fail-closed). UYAP login ve e-imza/PIN adımları münhasıran avukata aittir; sistem bunlar için kod yazmaz.

---

## Fikri Mülkiyet ve Lisans

Bu depodaki tüm içerik — "Ortak Avukat" metodolojisi, skill metinleri, scriptler ve dokümantasyon dâhil — özgün bir eserdir ve **5846 sayılı Fikir ve Sanat Eserleri Kanunu (FSEK)** kapsamında korunur. Eserin sahibi ve tüm **mali ve manevi hakların** münhasır hak sahibi **Av. Bayram Can Çapar**'dır (b.cancapar@gmail.com).

Depo kamuya açık (public) olarak yayımlanmıştır;   Kopyalama, çoğaltma, dağıtma, değiştirme, çeviri, türev çalışma oluşturma ve ticari kullanım **önceden yazılı izne tabidir**. Telif/atıf bildirimleri ve hak sahibinin adı kaldırılamaz. Yalnızca Yargı Pro MCP oluşturan ekibin fikri değişimine ve gerektiğinde ticari amaçla kullanımına izin verilmiştir. 

Tam koşullar: [LICENSE](LICENSE) · Özet bildirim: [NOTICE](NOTICE).

# Ortak Avukat — Türk Hukuku Co-Counsel Sistemi

**Sürüm:** 0.5.7.5 · **Yazar:** Av. Bayram Can Çapar · **Kapsam:** Türk hukukunun tamamı · **20 parça** (çekirdek + 19 `oa-*`)

> **© 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).** Fikri mülkiyet ile mali/manevi haklar münhasıran hak sahibine aittir; izinsiz çoğaltma/dağıtma/türev yasaktır. Bkz. depo kökündeki [LICENSE](../../LICENSE) ve [NOTICE](../../NOTICE).

---

## Bu nedir

Bu bir "dilekçe yazan yapay zekâ" değildir. Bir **avukatın çalışma metodunu** —
dosyayı ele alış sırasını, usulü esastan önce denetleme refleksini, künyeyi resmî
kaynaktan doğrulama disiplinini, zaafı müvekkile karşı değil müvekkil için
kullanma ayrımını — yazıya döken ve **her adımını makineyle denetleyen** bir
metodoloji sistemidir.

Sistemin ayırt edici yanı şudur: bir işin yapıldığını **modelin beyanına**
bırakmaz. "İçtihadı doğruladım" demek yetmez; kararın tam metni diske inmiş,
davaya bağı yazılmış ve lehe/aleyhe olarak damgalanmış olmalıdır. "Dilekçe hazır"
demek yetmez; teslim öncesi kapılar fiilen koşmuş ve tek bir çıkış koduyla
"hazır" demiş olmalıdır. Bu yüzden aile, muhakemeyi yapan katman ile onu
denetleyen katmanı bilinçli olarak ayırır: **model kurar, script denetler.**

Aile **20 parçadan** oluşur: bir çekirdek (`ortak-avukat`) ve 19 `oa-*` parça.
Mimari kasıtlı olarak *Lego*'dur — her parça tek başına da çalışır, `oa-pipeline`
ise onları uçtan uca bir hatta dizer. Parçaların bir kısmı **muhakeme parçasıdır**
(saf yöntem: `oa-alan`, `oa-ictihat`, `oa-strateji`, `oa-mudafii`,
`oa-musteki-vekili`, `oa-interview`), bir kısmı ise yanında **deterministik
denetim motoru** taşır (süre aritmetiği, illiyet grafı, antitez matrisi, usul
matrisi, kloz cetveli, teslim kapıları). Bu ayrımı bilerek okuyun: makineyle
denetlenen yerde ölçüm vardır, saf muhakeme parçasında ise disiplinli yöntem.

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

## DÜSTUR — ailenin anayasası

Ailenin tüm parçaları tek bir anayasaya tabidir
([`skills/ortak-avukat/references/anayasa.md`](skills/ortak-avukat/references/anayasa.md)).
Bir ilke değiştiğinde önce orası güncellenir; parçalar oraya işaret eder. Kurucu ilke (m.0) + on madde:

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

## Yirmi parça

### Çekirdek ve orkestra

#### `ortak-avukat` — çekirdek kimlik
Türk hukuku işi geldiğinde devreye giren varsayılan çalışma kimliğidir; kıdemli bir
eş-avukat duruşunu ve on maddelik anayasayı bağlama yükler. Tetiklenir tetiklenmez
işi `oa-pipeline`'a devreder — sizin elle parça çağırmanız beklenmez. Ailenin
anayasası fiziken bu parçanın altında durur ve diğer 19 parça oraya işaret eder;
yani bir ilke tek yerden değişir, yirmi yerde çelişmez. Ayırt edici kuralı şudur:
**devir sözle değil çağrıyla olur** — bir parçaya "devrettim" demek onu çalıştırmak
değildir, ve tarifinden taklit etmek halüsinasyonun ana kapısıdır.

#### `oa-pipeline` — Başbakan
Dosyayı 0. MANİFEST'ten 10. KAPANIŞ'a kadar sırayla yürüten ve her adımı denetleyen
icra organıdır. Bir adımın "yapıldı" iddiası yalnız beyanla kaydedilemez: kanıt
alanı boş bırakılamaz, gereksiz sayılan adım gerekçesiz geçilemez, ve o adımın
fiziksel çıktısı diskte yoksa kayıt yazılamaz. Analiz, evrak dökümü tamamlanmadan
başlayamaz; kıyas adımı içtihat muhakeme kaydı olmadan, kontrol adımı teslim
makbuzu olmadan kapanamaz. Turun sonunda tek bir soru sorulur — "boşluk var mı" —
ve boşluklu tur teslim edilemez; ayrıca dosyanın canlı durumu (`_oa/DURUM.md`)
defterden **türetilir**, elle yazılmaz.

### Dosyayı ele alma

#### `oa-ingest` — evrak metne iner
UYAP klasöründeki her evrağın metnini **bir kez** ve en ucuz doğru yoldan çıkarır:
metin PDF'ten doğrudan, taranmış olandan OCR ile, UDF/EYP/DOCX'ten açarak. Her
belge için ayrı bir metin dosyası, bir künye kaydı ve bir indeks üretir; böylece
sonraki parçalar külliyatı görüntü olarak değil, ucuz metin ve indeks üzerinden
seçici okur. İndirilen evrak adedi künyedeki sayımla tutmuyorsa **analiz başlamaz**
— eksik evrak sessizce yok sayılamaz. OCR boş dönerse pes etmez: farklı çözünürlük
ve yönelimlerle yeniden dener, hâlâ boşsa o sayfanın görselini üretip
"görsel inceleme gerek" damgası basar.

#### `oa-interview` — ilk inceleme
Akışın en başındadır ve tek bir yönetici ilkesi vardır: **önce sor, sonra analiz
et.** Talep, roller, aşama ve merci, **tebliğ tarihi**, eldeki ve eksik belgeler,
karşı tarafın en güçlü kozu — bunlar toplanmadan uzun analize girilmez. Usul
soruları esas anlatımından önce sorulur, çünkü esasın en güçlü hâli bile dolan bir
süreyi kurtarmaz. Toplananla müvekkil lehine bir **ön dava teorisi** kurar ve size
geri anlatır; böylece yanlış bir varsayım üzerine saatlerce çalışılmaz.

#### `oa-alan` — konumlama
Uyuşmazlığın hangi norma bağlandığını ve hangi yargı kolunda, HSK iş bölümü
ışığında hangi ihtisas dairesinin baktığını belirler. Bunu araştırma başlamadan
yapar; doğru daireye kilitlenmiş bir arama, geniş taramadan hem daha ucuz hem daha
isabetlidir. Dava türü başına unsur şablonları taşır (tasarrufun iptali, işe iade,
itirazın iptali, kıdem-ihbar gibi) ve bu unsurlar olgu matrisine taşınarak delilsiz
kalan unsur görünür kılınır. Ayırt edici kuralı bir **yasak bölgeler** listesidir:
geçmişte halüsinasyona yol açmış alanlarda künye, daire numarası veya parasal sınır
**ezberden yazılamaz** — doğrulanana kadar iddiadır.

### Her işi saran katmanlar

#### `oa-usul` — usulün esasa takaddümü
"Usul esasa üstündür" düsturunun aile çapındaki uygulayıcısıdır ve bir adım değil,
her aşamayı saran katmandır. Dava şartı, görev/yetki, tebligat, harç, ehliyet ve
temsil, ıslah, eski hâle getirme ve kanun yolu şartlarını **üç ayrı cepheden**
denetler: karşı tarafın hatası (taarruz), müvekkilin hatası (savunma) ve kamu
gücünün hatası. Denetimde boşluk kalırsa analiz teslim edilemez. En sert kuralı bir
dil kilididir: tebliğ tarihi belgeli değilken "süresinden sonradır, usulden reddi
gerekir" gibi **kesin dil kurulamaz** — teyit kaydıyla yazılır ve açık uç bırakılır.

#### `oa-sure` — nöbetçi
Dosyanın telafisi olmayan tek hatasını hesaplar: süre. Hem usul süreleri hem maddi
hukuk süreleri (zamanaşımı, hak düşürücü) aynı disipline tabidir. Hesap kara kutu
değildir; tebliğ gününün sayılmaması, araya giren tatilin süreyi uzatmaması ama son
gün tatile denk gelirse kayması gibi kurallar gerekçesiyle birlikte gösterilir.
Karşı tarafın fiilî işlem tarihi hesaplanan son güne karşı denenerek "kaçırılmış mı,
süresinde mi" sorusu da yanıtlanır. Geçmiş, bugün veya yaklaşan bir süre bulunursa
**diğer her işin önüne geçer** — sessiz kaçış yoktur.

#### `oa-gizlilik` — Layer 0
Dış araca (bulut MCP, web, e-posta, üçüncü parti bağlayıcı) çıkacak her içeriği,
gönderilmeden **önce** tarar ve üç karardan birini verir: geçir, sor, engelle.
Müvekkil verisi, TC kimlik, dosya/esas no, sağlık ve ceza verisi, hesap/kart
bilgisi taranır; kimlik numarası ve kart numarası algoritmik olarak da sınanır.
Mutlak yasak listesi her modda geçerlidir: **UYAP giriş akışı, e-imza/e-mühür, PIN
ve parola, API anahtarı, IBAN** — bunlar için sistem kod yazmaz, doldurmaz,
göndermez. Tarama çökerse veya dosya okunamazsa karar otomatik olarak **engelle**
olur; şüphede daima daha kısıtlayıcı olan seçilir.

#### `oa-illiyet` — nedensellik grafı
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

#### `oa-vakia` — olgu ve delil
Dosyanın olgu yarısını disipline eder: olayları kronolojiye dizer, her iddiayı
dayandığı delile eşler. İki tür boşluğu mekanik olarak yakalar — **delilsiz iddia**
(ispat boşluğu) ve hiçbir iddiaya bağlanmamış **yetim delil**. İspat durumu kapalı
bir kümedir (belgeli, tanık, bilirkişi, karine, ikrar, yemin, ispatsız); "ispatsız"
işaretlenen olgu otomatik boşluk sinyali üretir. Görüntü veya taranmış evrak
"okudum" diye varsayılamaz: ya OCR'dan geçer ya da "okunamadı, elle inceleme
gerekli" denir.

#### `oa-ictihat` — teyit
Her argümanın normunu ve künyesini resmî kaynaktan (Yargı Pro, AYM, Mevzuat MCP)
**fiilen** çeker ve kararın tam metnini diske ham döküm olarak yazar. İki araç
sınıfını ayırır: arama araçları tam metin döndürmez, dolayısıyla onlardan damga
çıkmaz; tam metin çeken araçlarda ise damga, davaya bağ ve döküm zorunludur. Bu
parça **teyit eder, damgayı atamaz** — muhakeme başka parçanın işidir ve bu ayrım
sistemin belkemiğidir. "Teyitli" etiketi yalnız fiilen yapılmış bir çağrıya konur;
kaynak bağlantısı da tam o anda kaydedilir, çünkü yazım aşamasında bir bağlantı
*hatırlanamaz*, ancak uydurulabilir — **kayıt yoksa dilekçede parantez hiç
açılmaz.**

#### `oa-kiyas` — açık kıyas
Hukuki sonucu örtük sezgiden çıkarıp denetlenebilir üçlüye oturtur: büyük önerme
(norm + teyitli içtihat) → küçük önerme (vakıa ve illiyet grafı) → sonuç. Normun
her unsurunun bir vakıaya eşlenip eşlenmediği tek tek denetlenir; eşleşmeyen unsur
ispat boşluğu veya hukuk boşluğu olarak görünür kalır. Teyitli bir kararı
"muhakeme edilmiş" hâle getiren yer burasıdır: kararın taşıyıcı ilkesi verbatim
alınır, dosyayla örtüşen somut noktalar kurulur, farklar yazılır ve damga
**bunlardan türetilir** — beyan edilmez. Damga dört değerlidir (lehe, aleyhe,
aleyhe-ayırt, nötr) ve **damga atanmazsa kayıt nötr sayılır**, yani kullanılamaz.

### Karar ve savunma

#### `oa-strateji` — yol seçimi
Analizi bir karara dönüştürür: en az iki gerçek alternatif kurar (dava, sulh,
icra, idari başvuru, bekleme) ve her birini maliyet, fayda, aşağı yön ve
**tahsil edilebilirlik** boyutuyla tartar. "Haklı olmak ≠ tahsil etmek" kuralı
gereği, karşı tarafta malvarlığı yoksa bu tespit kararın önüne konur. Başarı
olasılığı **sayı değildir**: "%72 kazanırsınız" denmez; nitel bir bant (güçlü,
dengeli, zayıf, belirsiz) ve o bandın gerekçesi verilir. Ayrıca "şu olursa şu yola
geç" tetikleri kurulur, böylece karar tek seferlik değil izlenebilir olur.

#### `oa-antitez` — gizli cephanelik
Müvekkilin tezine gelebilecek saldırıları sekiz sabit cephede eksiksiz çıkarır ve
her birini çürütür; çürütülemeyeni dürüstçe **artık risk** diye işaretler. Cephe
gücü ve dayanak durumu serbest metin olarak yazılamaz, kapalı değerlerle
işaretlenir; değerlendirilmemiş bir cephe "kör nokta" olarak yakalanır. Bu parçanın
çıktısı **karşı tarafa değil yalnız size** gelir. En sert kuralı sunum
disiplinidir: karşı taraf bir tezi fiilen ileri sürmeden ona karşı dilekçeye
önleyici çürütme konmaz — konursa karşı tarafı silahlandırırsınız. Hazırlanan
çürütme cephaneliktir; mühimmat ateş değildir.

### Üretim

#### `oa-dilekce` — yazım ve teslim biçimi
Dava, cevap, istinaf, temyiz, AYM bireysel başvuru, yemin teklifi ve idari kanal
dilekçelerinin zorunlu unsurlarını playbook olarak uygular ve taslağı yazar.
Paragrafın iç mantığı (iddia → norm → içtihat → örtüşme → sonuç) **görünmez
iskelettir**: yüzeye etiket olarak sızmaz, metin akıcı ve tez-omurgalı örülür.
Çıplak künye yasağı burada fiilen kapanır: dilekçeye yalnız lehe veya ayırt edilmiş
aleyhe damgalı, künyesi, kaynak izi, ilgili kısmı ve davaya bağı tam olan kararlar
girer. Nihai teslim biçimi olan UDF dosyasını üretir ve bunu **elle kurmaz** —
resmî araçla üretir; araç yoksa veya oturum gerekiyorsa bozuk dosya yazmak yerine
durur ve size ne yapmanız gerektiğini söyler.

#### `oa-sozlesme` — akdî metin
Sözleşmeyi iki modda ele alır: **tahrir**de müvekkil lehine ama geçerlilik
sınırının içinde kloz kurar, **inceleme**de karşı taslaktaki tuzağı imzadan önce
yakalar. Sıralama bilinçlidir — şekil şartı, imza yetkisi ve temsil, ehliyet ve
emredici hukuk denetimi kloz içeriği tartışmasından **önce** gelir, çünkü şekli
sakat bir sözleşme en parlak klozu bile taşıyamaz. Zorunlu kloz kategorileri
sayılıdır ve bir kategorinin sessizce atlanması engellenir; "gereksiz" denen
kategori gerekçesiz bırakılamaz. Risk nitel bantlarla verilir; uydurma bir sayısal
skor üretmek mümkün değildir.

### Teslim

#### `oa-kontrol` — son kapı
Doğrulama mimarisinin son halkasıdır: teslim öncesi künye izini, zorunlu unsurları,
içtihat muhakeme zincirini, gizliliği ve defter bütünlüğünü sabit sırada koşturur.
Ayırt edici kuralı bir **tek ölçüt** kuralıdır: kapıları teker teker sayıp "kaçı
yeşil" diye elle toplamak yasaktır; teslime hazır olup olmadığını yalnız orkestra
script'inin çıkış kodu söyler. Her koşuda bir **teslim makbuzu** yazılır — başarılı
da olsa başarısız da olsa iz kalır, taslağın özeti kaydedilir, sonradan değişirse
fark edilir. Bir engelleyici kapının script'i çalıştırılamıyorsa bu "atlandı"
sayılmaz, engellenmiş sayılır: belirsizlik teslimin lehine yorumlanmaz.

### Ceza dalı — aynanın iki yüzü

#### `oa-mudafii` — sanık/şüpheli savunması
Ceza dosyasında müdafilik üstlenildiğinde omurgaya savunma merceğini takar.
Aksiyomu nettir: **suçsuzluğu biz ispatlamayız** — iddia makamının ispatındaki
boşluğu, kuşkuyu ve hukuka aykırılığı gösteririz. Suçun maddi ve manevi unsurlarını
tek tek vakıaya eşler; eşleşmeyen unsur beraat sebebidir. Delil cephesini madde
adresleriyle tarar (doğrudan doğruyalık, hukuka aykırı delil yasağı, eksik
inceleme, atfı cürüm beyanı, dijital ve ses kaydı aidiyeti) ve kanun yolu
sürelerini ayrı bir nöbet tablosunda tutar. Sunum disiplini burada da geçerlidir:
iddia makamının henüz ileri sürmediği bir teze önleyici cevap vermek, kendi zayıf
noktanızı işaret etmektir.

#### `oa-musteki-vekili` — müşteki/mağdur vekilliği
Müdafiliğin ayna kutbudur ve tam tersini yapar: unsur yokluğunu aramak yerine her
unsuru **kurar** ve delile eşler. İspat boşluğunu somut delille kapatır, eksik
soruşturmayı tamamlatır, delil karartma veya kaçış riski somutsa koruma tedbirlerini
gündeme getirir. Şikâyet süresi ve zamanaşımı burada da nöbettedir. Anayasal
süzgeci şudur: kuşkulu bir atfa dayanan güçlü görünümlü iddia, zayıf ama sağlam
olandan **daha tehlikelidir** — desteksiz her isnat açıkça etiketlenir ve
şüphelinin masumiyet karinesini ihlal eden aşırı dil kullanılmaz.

### Öğrenme

#### `oa-usta` — çırak
Ailenin öğrenen ucudur: işlenen dosyalardan ders damıtır ve tekrar eden bir işi yeni
bir parça taslağına çevirir. Aynı iş üçüncü kez elle yapıldığında, siz istemeseniz
de "bunu kalıba dökelim mi" sorusunu gündeme getirir. İkinci ve daha sert görevi
ailenin yapısal sağlığını denetlemektir: her parçanın tanımı, adı, klasörüyle
uyumu, anılan scriptlerin gerçekten var olup olmadığı ve sürüm işaretlerinin
tutarlılığı makineyle sınanır — **hata varken paketleme yapılmaz.** Damıtılan her
ders anonimleştirme süzgecinden geçer: hiçbir dosya veya kişi ismen anılamaz, yalnız
soyut örüntü kalır.

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

## Kurulum

### 1) Yargı Pro bağlantısı — önce bunu yapın
İçtihat, mevzuat ve kurum kararı doğrulaması **Yargı Pro** MCP sunucusuna dayanır.

> **v0.5.7.4'ten itibaren eklenti iki sunucuyu KENDİSİ ilan eder** — kurulumda
> `yargi-pro` (birincil) ve `yargi-mcp-yedek` (MIT, hesapsız) bağlantıları
> otomatik teklif edilir; onaylamanız yeterlidir. Katman kuralı tek yönlüdür:
> Pro çalışıyorsa yedek hiç kullanılmaz; Pro düşerse içtihat araması yedekten
> sürer (yedekte **mevzuat/AİHM yoktur** — aile bunu çıktıya dürüstçe yazar).
> Aşağıdaki elle kurulum yalnız otomatik teklifi atlamışsanız gereklidir.

Claude Code → **connectors** bölümünden yeni bir MCP sunucusu ekleyin ve adres
olarak şunu girin:

```
https://yargi.betaspacestudio.com/mcp
```

Komut satırını tercih ederseniz:

```bash
claude mcp add --transport http yargipro https://yargi.betaspacestudio.com/mcp
```

OAuth akışını tamamlayın. Bu bağlantı olmadan künye doğrulaması yapılamaz; aile
"teyit edilemedi" damgasıyla çalışır ve hiçbir atıf dış çıktıya teyitli giremez.

> **Mevzuat MCP** (norm) ile **Literatür/DergiPark** ve **YÖK Tez** (doktrin) de
> bağlıysa doğrulama zinciri tamdır. Bu paket hiçbir MCP kimlik bilgisi içermez;
> sunucular kendi ortamınızda bağlanır.

### 2) Eklentiyi kurun

```
/plugin marketplace add bcancapar-spec/ortak-avukat
```

```
/plugin install ortak-avukat@ortak-avukat
```

Kurulumdan sonra Claude Code'u yeniden başlatın; skill listesinde tek bir
`ortak-avukat` ailesi (20 parça) görünmeli.

### 3) Yardımcı programlar
Python (evrak çıkarımı ve denetim scriptleri), Tesseract (`tur` dil paketiyle —
taranmış evrak) ve Node.js + `udf-cli` (UDF üretimi) gerekir. Ayrıntılı kurulum
adımları için depo kökündeki [README](../../README.md) dosyasına bakın.

---

## Parça dizini

| Parça | Rol | Denetim motoru |
|---|---|---|
| [`ortak-avukat`](skills/ortak-avukat/) | Çekirdek kimlik + anayasa | — |
| [`oa-pipeline`](skills/oa-pipeline/) | Başbakan: uçtan uca hat + defter | 8 script |
| [`oa-ingest`](skills/oa-ingest/) | Evrak → metin (OCR nöbetçili) | 1 script |
| [`oa-interview`](skills/oa-interview/) | İlk inceleme / mülakat | — |
| [`oa-alan`](skills/oa-alan/) | Norm + ihtisas dairesi konumlama | — |
| [`oa-usul`](skills/oa-usul/) | Usul denetimi (kesişen katman) | 1 script |
| [`oa-sure`](skills/oa-sure/) | Süre / zamanaşımı nöbetçisi | 2 script |
| [`oa-gizlilik`](skills/oa-gizlilik/) | Layer 0 gizlilik süzgeci | 1 script |
| [`oa-illiyet`](skills/oa-illiyet/) | Nedensellik / ilişki grafı | 1 script |
| [`oa-vakia`](skills/oa-vakia/) | Kronoloji + iddia↔delil matrisi | 1 script |
| [`oa-ictihat`](skills/oa-ictihat/) | İçtihat/mevzuat teyidi | — |
| [`oa-kiyas`](skills/oa-kiyas/) | Açık kıyas + içtihat muhakemesi | 1 script |
| [`oa-strateji`](skills/oa-strateji/) | Yol seçimi + maliyet-fayda | — |
| [`oa-antitez`](skills/oa-antitez/) | Sekiz cephe + gizli cephanelik | 1 script |
| [`oa-dilekce`](skills/oa-dilekce/) | Dilekçe yazımı + UDF üretimi | 4 script |
| [`oa-sozlesme`](skills/oa-sozlesme/) | Sözleşme tahrir / redline | 1 script |
| [`oa-kontrol`](skills/oa-kontrol/) | Teslim kapıları + makbuz | 4 script |
| [`oa-mudafii`](skills/oa-mudafii/) | Ceza müdafiliği (savunma) | — |
| [`oa-musteki-vekili`](skills/oa-musteki-vekili/) | Müşteki/mağdur vekilliği (iddia) | — |
| [`oa-usta`](skills/oa-usta/) | Ders damıtma + aile yapı denetimi | 1 script |

---

## Sürüm

Tam değişiklik günlüğü her parçanın `references/degisiklik-gunlugu.md` dosyasındadır;
ailenin anayasası [`skills/ortak-avukat/references/anayasa.md`](skills/ortak-avukat/references/anayasa.md)
dosyasında tek kaynak olarak durur.

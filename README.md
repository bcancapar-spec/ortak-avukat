# Ortak Avukat · Türk Hukuku Co-Counsel Sistemi

> Yanınızda çalışan **kıdemli bir ortak avukat (co-counsel)** gibi davranan bir
> hukuk metodolojisi sistemi: UYAP'tan indirdiğiniz dosya klasörünü okur, süreleri
> hesaplar, içtihadı resmî kaynaktan tam metniyle doğrular, dilekçeyi yazar,
> teslimden önce kendi işini makineyle denetler — ve son kararı **daima size**
> bırakır. Bir Claude Code / Cowork **plugin marketplace** deposudur.

**Sürüm:** 0.5.9 · **Yazar:** Av. Bayram Can Çapar · **20 skill** (çekirdek + 19 `oa-*` parça)

> ⚖️ **Gerçek davalarda test edildi.Geliştirilmeye devam ediliyor.** Bu sistem sentetik örneklerle değil,
> derdest gerçek dosyalarla sahada sınanıyor: bugüne dek **altı büyük saha
> koşusu** (istinaf, vergi, aile/mal rejimi, bilirkişi itirazı, dava analizi, banka/kefalet vd. ). yapılmış teste alınmayanşekilde sistemin ilk çalışmasında sonuca ulaşıldığı davalar görmezden gelinmiş ve teste yansıtılmamıştır. Test için ayrılan davalarda ise başarı sağlanmıştır. 
> İlk ölçüm: ~200 evraklık gerçek bir istinaf dosyası, **tek bir doğal-dil
> prompt'la**, 49 dakikada ve 45,6k token'la teslim edilebilir ek beyana +
> geçerli UDF'e dönüştü (dünyadaki şimdilik en güçlü kabul edilen en pahalı token tüketen modelde plug in sayesinde en ucuz token tüketimi ve en yüksek çıktı kalitesi yakalanmıştır. Claude Fable 5, max efor ile) ; evraklar
> [avukat-dosya-indirici](https://github.com/bcancapar-spec/avukat-dosya-indirici) ile pdf olarak indirilmiş ve buplug in ile .md .json formatlarına otonom olarak çevrilmiştir. 
> ile UYAP'tan indirildi). Sayılar, dürüst kayıp listesiyle birlikte:
> **[SAHA-SONUCU.md](SAHA-SONUCU.md)** · o gecenin hikâyesi:
> **[BASARI.md](BASARI.md)**. Dosya kimlikleri projenin anayasası m.7 gereği daima
> anonimdir.

> **© 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır.** Bu eserin fikri mülkiyeti ile tüm mali ve manevi hakları münhasıran Av. Bayram Can Çapar'a aittir.Ticari amaçla klonlanıp/tersine mühendislik kullanılmadığı müddetçe ücretsizdir.Ticari ürün olarak kullanılamaz.   (5846 sayılı FSEK). Depo kamuya açıktır; izinsiz kopyalama/dağıtma/türev/maddi amaç yasaktır. Beta sürümleri tamamlanana kadar avukatlar ve geliştiriciler geliştirmeye ve kullanmaya yetkilidir.  Bkz. [LICENSE](LICENSE) ve [NOTICE](NOTICE).

---

## Bu nedir 

**Bu bir "dilekçe yazan yapay zekâ" değildir; bir METODOLOJİ SİSTEMİDİR.**
Kıdemli bir avukatın çalışma metodunu — dosyayı ele alış sırasını, usulü esastan
önce denetleme refleksini, künyeyi resmî kaynaktan doğrulama disiplinini, zaafı
müvekkile karşı değil müvekkil için kullanma ayrımını — yazıya döker ve **her
adımını makineyle denetler.** Dil modeli kurar makine deterministik olarak denetler prensibi ile çalışır. 

Ayırt edici yanı şudur: bir işin yapıldığını **modelin beyanına bırakmaz.**
"İçtihadı doğruladım" "uyuşmazlığı doğruladım" demek yetmez — kararın tam metni diske inmiş, davaya bağı
yazılmış ve lehe/aleyhe olarak damgalanmış olmalıdır. "Dilekçe hazır" demek
yetmez — teslim öncesi kapılar fiilen koşmuş ve dijital determinizm ile makbuz(yani kontrol)  kesilmiş olmalıdır.
Bu yüzden sistem, muhakemeyi yapan katman ile onu denetleyen katmanı bilinçli
olarak ayırır. Kuram üç kelimeyle özetlenir:

> **Model kurar → script denetler → model muhakeme eder.**
>
> Pahalı olan katman (hukuki muhakeme) yapay zekâya, ucuzlatılabilen her şey
> (evrak okuma, künye doğrulama, biçim, sayım, makbuz) deterministik Python
> scriptlerine verilir. Model "yaptım" der; script **kanıtlar**. Bu iki-katman
> mimari hem maliyeti ~26 kata kadar düşürür hem de halüsinasyonu yapısal
> olarak dışlar: script yalan söyleyemez.

Kullanım alanı Türk hukukunun **herhangi bir dalıdır**: dilekçe (dava, cevap,
istinaf, temyiz), dava-dosya-uyuşmazlık analizi, hukuki mütalaa, içtihat ve mevzuat
araştırması, AYM bireysel başvuru, sözleşme inceleme ve tahriri, ceza müdafiliği
ve müşteki vekilliği. Sistem kişilere değil **yönteme** bağlıdır; her olgusal
unsuru (künye, madde, tarih, içtihat) resmî kaynaktan doğrular.

Yirmi parça, 20 ayrı araç gibi değil **yetenek sahibi tek bir eş-avukat** gibi
çalışır: dosyanın analizini kalıcı bir çalışma hafızasına yazar; sonraki her
oturumda ham evrakı baştan okumak yerine bu kaydı kullanır — token-verimli ve
kayıpsız.

---

## Nasıl çalışır — dosyanızın başına oturduğunuzda

Sizin tarafınızdan görünen akış üç adımdır: **klasörü açarsınız, tek bir doğal
cümle yazarsınız, kararları siz verirsiniz.** Aradaki her şeyi sistem yürütür:

1. **Evrak metne iner.** UYAP'tan https://github.com/bcancapar-spec/avukat-dosya-indirici eklentisi ile indirdiğiniz PDF/TIFF/UDF/EYP/DOCX yığını bir
   kez ve en ucuz doğru yoldan metne çevrilir; taranmış olanlar OCR'dan geçer ve
   "⚠ teyit gerek" damgası alır. Evrak sayımı tutmuyorsa analiz **başlamaz**.
2. **Sorular sorulur.** Uzun analize girmeden önce talep, roller, aşama, **tebliğ
   tarihi**, eldeki ve eksik belgeler, karşı tarafın en güçlü kozu toplanır.
3. **Usul ve süre nöbete girer.** Dolan bir süre varsa diğer her işin önüne geçer;
   süre, dosyadaki telafisi olmayan tek hatadır.
4. **Olgu ve hukuk ayrı ayrı kurulur.** Kronoloji ve iddia↔delil matrisi bir yanda;
   norm, tam metniyle doğrulanmış içtihat ve açık kıyas öbür yanda.
5. **Karşı taraf simüle edilir.** Sekiz cephede size gelebilecek her saldırı
   çıkarılır ve çürütülür; çürütülemeyen dürüstçe "artık risk" diye işaretlenir.
   Bu çıktı **size** gelir, dilekçeye girmez.
6. **Taslak yazılır, kapılardan geçer, UDF üretilir.** Zorunlu unsurlar, künye izi,
   içtihat muhakeme zinciri ve gizlilik denetlenir; teslim makbuzu kesilir; UDF
   resmî araçla üretilir ve UYAP'ta açılabilirliği sınanır.
7. **Karar sizindir.** Sistem karar *materyali* üretir; nihai kararı avukat verir.
   Stratejik kavşaklarda sistem durur ve size sorar — sessizce karar vermez.

**Temsilî bir oturum** (kısaltılmış; kimlikler kurgudur):

```text
Siz   : Bu klasör [Mahkeme] 2099/123 esas sayılı dosyamız. Davalı vekiliyiz.
        Cevap dilekçesi hazırlanacak. Dosyanın tamamını işle, sürelere dikkat et,
        kullandığın her kararı tam metniyle doğrula, davacının iddialarını ve elimizdeki delileri analiz et. Karşı tarafın zayıf karnını yargıtay kararları ve mevzuat ile bul. Karar gereken kavşaklarda bana sor.

Sistem: 212 evrak metne indirildi (17'si taranmıştı → OCR; sayım tutuyor).
Sistem: Başlamadan 6 sorum var: (1) dava dilekçesi hangi tarihte tebliğ edildi?
        (2) ... (6) karşı tarafın en güçlü kozu sizce nedir?
Siz   : [cevaplarınız]
Sistem: Cevap süreniz [tarih] günü doluyor — 9 gün var. Usul taraması: yetki
        itirazı mümkün görünüyor. Devam ediyorum.
Sistem: 14 karar tam metniyle çekildi ve okundu: 9 LEHE → dilekçeye,
        3 ALEYHE → iç cephaneliğe, 2 ilgisiz → elendi.
Sistem: [AVUKAT KARARI BEKLENİYOR] Zamanaşımı def'i iki türlü kurulabilir:
        (a) ... (b) ... Hangisini tercih edersiniz?
Siz   : [kararınız]
Sistem: Taslak hazır; teslim kapıları koştu, makbuz kesildi, UDF üretildi:
        _oa/cikti/40-UYAP/ — UYAP editöründe açıp e-imzanızla siz yüklersiniz.
```

Tüm üretim, çalıştığınız klasörün içindeki `_oa/` yerel hafıza kökünde kalır.
**Müvekkil evrakı salt-okunurdur, değiştirilmez.**

---

## DÜSTUR — sistemin anayasası

Yirmi parçanın tamamı hooklar ile birbirine bağlanmış Av.Bayram Can ÇAPAR tarafından oluşturulan tek bir fiktif anayasaya tabidir
([`anayasa.md`](plugins/ortak-avukat/skills/ortak-avukat/references/anayasa.md)).
Bir ilke değiştiğinde önce orası güncellenir; parçalar oraya işaret eder — yani
bir kural yirmi yerde farklı sürümlerle yaşayamaz. Kurucu ilke (m.0) + on madde:

| # | İlke | Meslektaş için ne demek |
|---|---|---|
| **0** | **Kurucu ilke — metodoloji tanım değil, DONANIMDIR** | Bu sistemi kullanan yapay zekâ, Türk hukukunda doğru çıktı için tanımlardan/özetlerden değil kurulu METODOLOJİDEN — tüm yeteneklerle fiilen donatılmış olarak — hareket eder. Bu yetenekler, modelin en verimli ve en başarılı işlem hacmini yaratan, kullanıcı ile yapay zekâ arasındaki KÖPRÜDÜR. |
| **1** | **Çaba ve kalite standardı** | Tasarruf yalnız **israftan** kesilir: aynı evrağı her adımda yeniden okumak, metni görüntü olarak açmak, bütünü yükleyip parçayı kullanmak. Muhakemeden, araştırmadan, unsur denetiminden **asla** kısılmaz. |
| **2** | **Usul esasa üstündür** | Usul denetimi esastan **önce** ve en az onun kadar ciddi yapılır. Süre, dosyadaki telafisi olmayan tek hatadır. Düstur çift yönlüdür: kendi usul zaafınız sıfırlanır, karşı tarafın kaçırdığı süre , dava şartları veya hak düşürücü süreler vb. gizlenmez — derhâl ileri sürülür. |
| **3** | **Örnekleme ilkesi** | Metinlerdeki kanun/dava tipi listeleri kapsamı **daraltmaz**, yalnız metodu gösterir. Listede olmayan konu aynı metotla, kıyasen işlenir. Kapsam istisnasız tüm Türk hukukudur. |
| **4** | **Doğaçlama meşruiyeti** | Yöntemde serbestlik: muhakeme kurgusu, argüman dizilimi, üslup, strateji özgürce doğaçlanır. Sınır tek ve keskindir — **olguda asla**: **illiyet ve vakıa denetiminde asla**  künye, madde, tarih, tutar üretilemez. |
| **5** | **Doğrulama mimarisi** | **Teyit ≠ muhakeme.** Bir içtihat mevzuat.gov.tr den çekildiğinde MCP ile  Künyenin var olduğunu doğrulamak yetmez; tam metin çekilmiş, davaya bağı kurulmuş ve damgalanmış olmalıdır. Damgasız atıf, çıplak künyeden, perdesiz bir evden farksızdır. İki modelin hemfikir olması doğrulama **değildir**. |
| **6** | **Müvekkil-aleyhi çıktı yasağı** | Zaaf dış belgeye yazılmaz, ama iç analizde **saklanmaz**. Salt aleyhe içtihat dilekçeye giremez; cephanelikte durur ve ancak karşı taraf onu fiilen ileri sürerse çıkar. | bu hususta çalışma klasörüne ayrı dosya açılır ve durum farkındalığı verilir. 
| **7** | **Anonimleştirme** | Sistem metinlerinde hiçbir müvekkil, karşı taraf veya dosya **ismen anılamaz**; tecrübe yalnız soyut örüntü olarak işlenir (Av.K. m.36 · KVKK). |
| **8** | **Simülasyon yasağı** | plug in içerisinde olan yetenek kitlerinden Bir parça, tarifinden taklit edilerek "çalıştırılmış" sayılmaz; fiilen çağrılmış olmalıdır. Yüklenemiyorsa çıktıya "fiziken yüklenemedi" diye **açıkça yazılır**. |
| **9** | **Başbakan denetimi** | `oa-pipeline` anayasayı icra ve denetim organıdır. Parça atlayarak, muhakeme kısarak maliyet düşürmek yasaktır. Karar materyali üretir; kararı avukat verir. |
| **10** | **Layer 0 — gizlilik** | Dış araca çıkan her içerik önce süzgeçten geçer. **UYAP girişi ve e-imza/PIN münhasıran avukata aittir**; sistem bunlar için kod yazmaz, yalnızca engeller. |

---

## Claude Code'a vereceğiniz prompt — kopyala-yapıştır

Dava klasörünüzde açtığınız oturuma yazacağınız **tek doğal prompt** yeterlidir.
Metodoloji talimatı vermenize gerek yoktur — sistem kendi disiplinini işletir.İster  https://github.com/bcancapar-spec/avukat-dosya-indirici Chrome eklentisi ile dava dosyanızı indirin isterseniz de size verilen evrakları tarayıp lokal olarak bilgisayarınıza kaydedin
Köşeli parantezleri kendi dosyanıza göre doldurun:

```text
Bu klasör [Mahkeme] [Esas No] sayılı dosyamız. [Davacı/Davalı/Sanık müdafii/
Müşteki vekili] tarafız. Yapılacak iş: [cevap dilekçesi / bilirkişi raporuna
itiraz / istinaf başvurusu/ Dava Analizi / Bilirkişi raporu hazırlanması hazırlanması]. Dosyanın tamamını işle, sürelere
dikkat et, kullandığın her kararı tam metniyle doğrula, stratejik kavşaklarda
bana sor. Nihai teslim: UYAP'a yüklenmeye hazır UDF + kısa strateji notu hazırla. Verdiğin sistem promptu gerçekleştirilince kontrol için benden "kontrol et" şeklindesistem promptu iste.  
```

İş tipine göre hazır varyantlar (aynı gövdeye şu cümleyi ekleyin/değiştirin):

| İş | Prompt'a eklenecek satır |
|---|---|
| **Cevap dilekçesi** | "Dava dilekçesi [tarih] günü tebliğ edildi; cevap süremizin son gününü hesapla ve cevap dilekçesini hazırla." |
| **Bilirkişi itirazı** | "Bilirkişi raporu [tarih] günü tebliğ edildi; itiraz süresi içinde rapora itiraz dilekçesi hazırla; raporun hesabını kendi hesabınla çaprazla." |
| **İstinaf / temyiz** | "Gerekçeli karar [tarih] günü tebliğ edildi; kanun yolu süresini hesapla ve istinaf/temyiz dilekçesini hazırla." |
| **Yalnız analiz** | "Henüz dilekçe istemiyorum; dosyayı işle, güçlü/zayıf yanlarımızı ve yol seçeneklerini içeren bir strateji notu çıkar." |

> **Kapanış promptu gerekmez (v0.5.9).** Oturum kapanırken defter denetimi,
> mühür ve makbuz kontrolleri hook'larla **kendiliğinden** koşar; "işi kapat,
> denetle" diye ayrıca yazmanız gerekmez. Aynı şekilde her taslak yazımında
> hızlı denetim kendiliğinden çalışır ve bulgusunu modele anında geri verir —
> sizden hiçbir "mekanik hijyen" cümlesi beklenmez.

---

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

- **1.357 otomatik test** (bu sürüm itibarıyla; ilk paket 57 testle çıkmıştı —
  her sürüm, sahada bulunan her kusuru önce bir teste çevirir). Testlerin
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
  Python 3.12/3.13** dört ortamında tam süiti ve ayrıca **aile yapı
  denetimini** (20 parçanın manifest/sürüm/hook tutarlılığı) koşar. Kural
  serttir: **CI yeşermeden sürüm etiketi atılamaz** — bu kural, 11 koşu
  kırmızı kalan CI'ın kimsenin fark etmediği bir dönemin dersidir. Platform
  farkları da burada yakalanır (örnek: Windows'ta görünmeyen bir çalıştırma-izni
  eksiği Ubuntu'da yakalandı ve kapatıldı).
- **Denetçinin denetimi:** teşhis ve denetim araçlarının kendileri de kendi
  testleriyle yaşar; manifest sayı iddiaları ve hook envanteri mekanik
  kapılarla (aile_dogrula Kapı-A/B) doğrulanır — "denetleyen kim denetliyor"
  sorusu açık bırakılmaz.

### Altı büyük saha koşusu

| Saha | Dosya tipi | Ne öğretti → hangi sürüm |
|---|---|---|
| **İlk tam koşu** | ~200 evraklık derdest istinaf dosyası | 49 dk · 45,6k token · teslim edilebilir ek beyan + geçerli UDF ([SAHA-SONUCU.md](SAHA-SONUCU.md)); bayat araç kopyası ve link zinciri dersleri → v0.5.7 |
| **Müdahalesiz test** | 214 evraklık bakir klasör | "Kapının gücü kodunda değil **tetiğindedir**" — mekanizmalar sağlamdı, çağrılmıyorlardı → v0.5.5.1–v0.5.5.3 |
| **447 sahası** | vergi davası | Tetik boşlukları + hook katmanının sessiz ölümü (masaüstü uygulaması hook'u kabuksuz koşturuyordu) → v0.5.8.1 / v0.5.8.2 |
| **372 sahası** | aile / mal rejimi | Hook katmanı ilk kez uçtan uca canlı ateşledi; koşunun **5 kollu adli analizi** (transkript + artefakt + kod yolu + şekil zinciri + desen karnesi) → v0.5.8.4: elle-UDF engeli, makbuz garantisi, mühür otomasyonu |
| **346 sahası** | bilirkişi raporuna itiraz | Künye kapısı **gerçek bir açığı** yakaladı ve model dürüst davrandı; tek bir ayrıştırıcı yanlış-pozitifi yeşil makbuzu imkânsız kıldı → v0.5.8.5: mutlak triyaj [G6], hook dirilişi, e-imza halkası |
| **777 sahası** | banka/kefalet ikinci cevap + **24 kök çapraz taraması** | Bayat araç kiti kök nedeni; ilk gerçek LEHE/ALEYHE triyajı; resmî araçla üretilen UDF, dört kenarı yönetmelik ölçüsünde (42,52 pt) ilk **tam-standart ürün** olarak UYAP editöründe açıldı → v0.5.8.6 + v0.5.9 |

### Ölçülen örnekler — beyan değil sayı

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

- **Organik yeşil makbuz henüz 0:** bugüne dek sahada üretilen yeşil makbuzlar
  hep insan yardımı/onarımı sonrası geldi; sistemin hiç dokunulmadan uçtan uca
  yeşil makbuz kestiği bir koşu **henüz ölçülmedi**. v0.5.9'un varlık sebebi
  tam olarak budur.
- **İçerik kabulü avukat yargısıdır:** hiçbir kapı "bu dilekçe hukuken
  isabetli" demez; kapılar unsur, künye, biçim ve iz denetler. Hukuki isabet
  hükmü size aittir.
- Geçmiş sürümlerin ham dersleri saklanmaz: teslim hattının avukatın kendi
  makinesinde çökmesi, 11 koşu kırmızı kalan CI, elle yazılmış defter, geçerli
  dilekçeyi kesen kapı — hepsi tarihiyle [STATUS.md](STATUS.md)'de durur.

---

## Skill seti — yirmi parça, tek tek

Parçaların bir kısmı **saf muhakeme parçasıdır** (yöntem disiplini), bir kısmı
yanında **deterministik denetim scripti** taşır. Script sayısı her başlıkta
yazılıdır: makineyle denetlenen yerde ölçüm vardır.

### Çekirdek ve orkestra

#### [`ortak-avukat`](plugins/ortak-avukat/skills/ortak-avukat/) — çekirdek kimlik
Türk hukuku işi geldiğinde devreye giren varsayılan çalışma kimliğidir; kıdemli
bir eş-avukat duruşunu ve anayasayı bağlama yükler, işi hemen `oa-pipeline`'a
devreder — sizin elle parça çağırmanız beklenmez. Anayasa fiziken bu parçanın
altında durur; diğer 19 parça oraya işaret eder. Ayırt edici kuralı: **devir
sözle değil çağrıyla olur** — bir parçayı tarifinden taklit etmek, çalıştırmak
değildir.

#### [`oa-pipeline`](plugins/ortak-avukat/skills/oa-pipeline/) — Başbakan · 8 script
Dosyayı 0. MANİFEST'ten 10. KAPANIŞ'a kadar sırayla yürüten icra organıdır. Bir
adımın "yapıldı" iddiası beyanla kaydedilemez: o adımın fiziksel çıktısı diskte
yoksa kayıt yazılamaz; analiz, evrak dökümü tamamlanmadan başlayamaz. Dosyanın
canlı durumu (`_oa/DURUM.md`) defterden **türetilir**, elle yazılmaz. v0.5.9 ile
**kesintisiz akış** geldi: her mesajınıza görünmez bir "zincir durumu" eklenir —
model her turda zincirde nerede olduğunu, neyin beklediğini ve hangi avukat
kararının açık olduğunu bilir.

### Dosyayı ele alma

#### [`oa-ingest`](plugins/ortak-avukat/skills/oa-ingest/) — evrak metne iner · 1 script
UYAP klasöründeki her evrağın metnini **bir kez** ve en ucuz doğru yoldan
çıkarır: metin PDF'ten doğrudan, taranmış olandan OCR ile, UDF/EYP/DOCX'ten
açarak; belge başına metin dosyası + künye + indeks üretir. İndirilen evrak
adedi künyedeki sayımla tutmuyorsa **analiz başlamaz** — eksik evrak sessizce
yok sayılamaz. OCR boş dönerse pes etmez: farklı çözünürlük ve yönelimlerle
yeniden dener, hâlâ boşsa sayfa görselini üretip "görsel inceleme gerek"
damgası basar.

#### [`oa-interview`](plugins/ortak-avukat/skills/oa-interview/) — ilk inceleme
Tek yönetici ilkesi vardır: **önce sor, sonra analiz et.** Talep, roller, aşama,
tebliğ tarihi, eldeki ve eksik belgeler, karşı tarafın en güçlü kozu toplanmadan
uzun analize girilmez; usul soruları esastan önce sorulur. Sorular tek turda,
numaralı liste hâlinde gelir. Toplananla müvekkil lehine bir **ön dava teorisi**
kurar ve size geri anlatır — yanlış varsayım ilk dakikada düzelir.

#### [`oa-alan`](plugins/ortak-avukat/skills/oa-alan/) — konumlama
Uyuşmazlığın hangi norma bağlandığını ve HSK iş bölümü ışığında hangi ihtisas
dairesinin baktığını, araştırma başlamadan belirler — doğru daireye kilitli
arama hem ucuz hem isabetlidir. Dava türü başına zorunlu-unsur şablonları taşır;
delilsiz kalan unsur görünür kılınır. Ayırt edici kuralı **yasak bölgeler**
listesidir: geçmişte halüsinasyona yol açmış alanlarda künye, daire numarası
veya parasal sınır ezberden yazılamaz.

### Her işi saran katmanlar

#### [`oa-usul`](plugins/ortak-avukat/skills/oa-usul/) — usulün önceliği · 1 script
"Usul esasa üstündür" düsturunun uygulayıcısıdır; bir adım değil, her aşamayı
saran katmandır. Dava şartı, görev/yetki, tebligat, harç, ehliyet, ıslah ve
kanun yolu şartlarını **üç cepheden** denetler: karşı tarafın hatası, müvekkilin
hatası, kamu gücünün hatası. En sert kuralı bir dil kilididir: tebliğ tarihi
belgeli değilken "süresinden sonradır" gibi kesin dil kurulamaz — teyit kaydıyla
yazılır.

#### [`oa-sure`](plugins/ortak-avukat/skills/oa-sure/) — süre nöbetçisi · 2 script
Dosyanın telafisi olmayan tek hatasını hesaplar: süre. Usul süreleri de maddi
hukuk süreleri de (zamanaşımı, hak düşürücü) aynı disipline tabidir; kural önce
Mevzuat MCP'den teyit edilir, son gün deterministik scriptle hesaplanır. Hesap
kara kutu değildir: tebliğ gününün sayılmaması, son günün tatile kayması gibi
kurallar gerekçesiyle gösterilir. Dolan veya yaklaşan süre bulunursa **diğer her
işin önüne geçer**.

#### [`oa-gizlilik`](plugins/ortak-avukat/skills/oa-gizlilik/) — Layer 0 · 1 script
Dış araca (bulut MCP, web, e-posta) çıkacak her içeriği gönderilmeden **önce**
tarar ve üç karardan birini verir: geçir, sor, engelle. Müvekkil verisi, TC
kimlik, dosya/esas no, sağlık ve ceza verisi, hesap/kart bilgisi taranır.
Mutlak yasak her modda geçerlidir: **UYAP girişi, e-imza/PIN, parola, API
anahtarı, IBAN** — sistem bunlar için kod yazmaz, doldurmaz, göndermez. Tarama
çökerse karar otomatik **engelle** olur.

#### [`oa-illiyet`](plugins/ortak-avukat/skills/oa-illiyet/) — nedensellik grafı · 1 script
Dosyadaki kişileri, şirketleri, kurumları ve delilleri düğüm; ilişkileri ve
neden-sonuç bağlarını kenar sayarak yönlü bir graf kurar. Gözün kaçıracağı
yapısal boşlukları mekanik olarak çıkarır: bağlanmamış düğüm, kopuk zincir, iki
grubu tek başına bağlayan köprü düğüm (muvazaa sinyali), illiyeti kesme adayları
(mücbir sebep, üçüncü kişi kusuru). Zincir boyu **güven çürümesi** hesabı
varsayılan açıktır: en zayıf halka raporlanır; doğrulanmamış illiyet üzerine
zincir kurulamaz.

### Olgu ve hukuk

#### [`oa-vakia`](plugins/ortak-avukat/skills/oa-vakia/) — olgu ve delil · 2 script
Dosyanın olgu yarısını disipline eder: olayları kronolojiye dizer, her iddiayı
dayandığı delile eşler. İki tür boşluğu mekanik yakalar: **delilsiz iddia**
(ispat boşluğu) ve hiçbir iddiaya bağlanmamış **yetim delil**. Yanındaki özne
eşleştirici, farklı evraklarda farklı yazılmış aynı kişiyi/şirketi benzerlik
ölçüsüyle eşler — kesin değilse karar vermez, "avukata sor" damgası basar.

#### [`oa-ictihat`](plugins/ortak-avukat/skills/oa-ictihat/) — teyit ve mutlak triyaj
Her argümanın normunu ve künyesini resmî kaynaktan (Yargı Pro, AYM, Mevzuat MCP)
**fiilen** çeker; kararın tam metnini diske ham döküm olarak yazar — dilekçeye
giren her alıntı hafızadan değil o dosyadan gelir. v0.5.8.5'ten beri **mutlak
triyaj [G6]** geçerlidir: MCP'den çekilen **her karar istisnasız baştan sona
okunur**; LEHE ise dilekçeye, ALEYHE ise cephaneliğe gider; okunmamış veya
damgasız künye dilekçede **kalamaz**. Kaynak bağlantısı yalnız teyit anında
kaydedilir: kayıt yoksa dilekçede parantez hiç açılmaz — uydurma bağlantı,
çıplak künyeden daha kötüdür.

#### [`oa-kiyas`](plugins/ortak-avukat/skills/oa-kiyas/) — açık kıyas · 1 script
Hukuki sonucu örtük sezgiden çıkarıp denetlenebilir üçlüye oturtur: büyük önerme
(norm + teyitli içtihat) → küçük önerme (vakıa) → sonuç. Normun her unsurunun
bir vakıaya eşlenip eşlenmediği tek tek denetlenir; eşleşmeyen unsur boşluk
olarak görünür kalır. Kararın taşıyıcı ilkesi verbatim alınır, dosyayla örtüşen
somut noktalar kurulur, farklar yazılır — LEHE/ALEYHE damgası **bunlardan
türetilir**, beyan edilmez.

### Karar ve savunma

#### [`oa-strateji`](plugins/ortak-avukat/skills/oa-strateji/) — yol seçimi
Analizi karara dönüştürür: en az iki gerçek alternatif kurar (dava, sulh, icra,
idari başvuru, bekleme) ve her birini maliyet, fayda ve **tahsil edilebilirlik**
boyutuyla tartar — kazanılan ama tahsil edilemeyen karar müvekkile masraftır.
Başarı olasılığı **sayı değildir**: "%72 kazanırsınız" denmez; nitel bant
(güçlü/dengeli/zayıf/belirsiz) ve gerekçesi verilir. "Şu olursa şu yola geç"
tetikleri kurulur.

#### [`oa-antitez`](plugins/ortak-avukat/skills/oa-antitez/) — gizli cephanelik · 1 script
Müvekkilin tezine gelebilecek saldırıları sekiz sabit cephede eksiksiz çıkarır
ve çürütür; çürütülemeyeni dürüstçe **artık risk** diye işaretler. Çıktısı
**yalnız size** gelir, dilekçeye girmez. En sert kuralı sunum disiplinidir:
karşı taraf bir tezi fiilen ileri sürmeden ona dilekçede önleyici çürütme
yazılmaz — yazarsanız karşı tarafı silahlandırırsınız. Cephanelik mühimmattır;
mühimmat ateş değildir.

### Üretim

#### [`oa-dilekce`](plugins/ortak-avukat/skills/oa-dilekce/) — yazım ve teslim · 4 script
Dava, cevap, istinaf, temyiz, AYM başvurusu ve idari kanal dilekçelerinin
zorunlu unsurlarını playbook olarak uygular ve taslağı yazar; paragrafın iç
mantığı (iddia → norm → içtihat → örtüşme → sonuç) görünmez iskelettir, yüzeye
etiket olarak sızmaz. UDF'i **elle kurmaz** — resmî araçla üretir; biçim, Resmî
Yazışma Yönetmeliği ölçülerine (dört kenar 42,52 pt, 1,5 satır aralığı)
otomatik uyar. v0.5.9 ile **inline denetim** geldi: her taslak yazımında hızlı
denetim kendiliğinden koşar ve bulgusunu modele anında geri verir. E-imzalı
nüsha ayrıca korunur: imzalı dosyaya sistem **asla** dokunmaz.

#### [`oa-sozlesme`](plugins/ortak-avukat/skills/oa-sozlesme/) — akdî metin · 1 script
Sözleşmeyi iki modda ele alır: **tahrir**de müvekkil lehine ama geçerlilik
sınırı içinde kloz kurar, **inceleme**de karşı taslaktaki tuzağı imzadan önce
yakalar. Şekil şartı, imza yetkisi ve emredici hukuk denetimi kloz
tartışmasından **önce** gelir — şekli sakat sözleşme en parlak klozu taşıyamaz.
Zorunlu kloz kategorileri sayılıdır; sessiz atlama engellenir.

### Teslim

#### [`oa-kontrol`](plugins/ortak-avukat/skills/oa-kontrol/) — son kapı · 7 script
Doğrulama mimarisinin son halkasıdır: künye izi, zorunlu unsurlar, içtihat
muhakeme zinciri, kaynak tazeliği, gizlilik ve defter bütünlüğü sabit sırada
koşar; teslime hazır olup olmadığını **tek ölçüt** söyler — kapıları elle sayıp
toplamak yasaktır. Her koşuda **teslim makbuzu** kesilir (başarısız koşuda bile
RED makbuzu düşer) ve ürüne kalıcı bir **mühür** (kaynak izi + parmak izi)
basılır. v0.5.9'un **sunum kilidi** buraya bağlıdır: yeşil makbuz yokken
teslim-sınıfı bir dosya size gönderilmek istenirse sistem durup sorar — "yine
de gönder" demek sizin kararınızdır, ama artık **görmeden olmaz**.

### Ceza dalı — aynanın iki yüzü

#### [`oa-mudafii`](plugins/ortak-avukat/skills/oa-mudafii/) — sanık/şüpheli savunması
Ceza dosyasında müdafilik üstlenildiğinde omurgaya savunma merceğini takar.
Aksiyomu nettir: **suçsuzluğu biz ispatlamayız** — iddia makamının ispatındaki
boşluğu, kuşkuyu ve hukuka aykırılığı gösteririz. Suçun maddi ve manevi
unsurlarını tek tek vakıaya eşler; eşleşmeyen unsur beraat sebebidir. Delil
cephesi madde adresleriyle taranır; kanun yolu süreleri ayrı nöbet tablosunda
tutulur.

#### [`oa-musteki-vekili`](plugins/ortak-avukat/skills/oa-musteki-vekili/) — müşteki/mağdur vekilliği
Müdafiliğin ayna kutbudur: unsur yokluğunu aramak yerine her unsuru **kurar** ve
delile eşler; ispat boşluğunu somut delille kapatır, eksik soruşturmayı
tamamlatır, delil karartma riski somutsa koruma tedbirlerini gündeme getirir.
Anayasal süzgeci: kuşkulu atfa dayanan güçlü görünümlü iddia, zayıf ama sağlam
olandan **daha tehlikelidir** — desteksiz isnat açıkça etiketlenir.

### Öğrenme ve öz-denetim

#### [`oa-usta`](plugins/ortak-avukat/skills/oa-usta/) — çırak ve aile denetçisi · 1 script
Ailenin öğrenen ucudur: işlenen dosyalardan ders damıtır (anonimleştirme
süzgecinden geçirerek) ve tekrar eden işi yeni parça taslağına çevirir. İkinci
görevi ailenin yapısal sağlığını denetlemektir: her parçanın tanımı, adı,
anılan scriptlerin varlığı, sürüm tutarlılığı — ve v0.5.9'dan beri manifestteki
"N skill" iddiasının gerçek parça sayısıyla eşleşmesi ile hook kapsamının
bütünlüğü — makineyle sınanır. **Hata varken paketleme yapılmaz**: bozuk aile
dağıtıma çıkamaz.

Parçaların ayrıntılı kataloğu: **[plugins/ortak-avukat/README.md](plugins/ortak-avukat/README.md)**

---

## Kurulum — kolay yol

Sistem dört ayağa basar: **(1) Claude Code** · **(2) Python + Tesseract** (evrak
çıkarımı ve denetim scriptleri) · **(3) Node.js + udf-cli** (UDF üretimi) ·
**(4) Yargı Pro MCP** (içtihat/mevzuat doğrulaması). Adım adım:

### 1. Claude Code'u kurun
Claude Code (CLI veya Desktop) kurulu ve oturum açık olmalı: <https://claude.com/claude-code>

### 2. Python 3.10+ ve iki paket

```bash
python --version
pip install pymupdf pillow
```

`pymupdf` PDF metin çıkarımı, `pillow` TIFF/JPG işleme içindir — bunlar olmadan
evrak işlenemez.

### 3. Tesseract OCR (Türkçe dil paketiyle — taranmış evrak için önerilir)

- **Windows:** [UB-Mannheim kurucusu](https://github.com/UB-Mannheim/tesseract/wiki) — kurulumda **Turkish (`tur`)** dil paketini seçin **ve** "Add Tesseract to PATH" işaretleyin
- **Linux:** `sudo apt-get install tesseract-ocr tesseract-ocr-tur`
- **macOS:** `brew install tesseract tesseract-lang`

```bash
tesseract --version
```

Tesseract yoksa metin evraklar yine işlenir; taranmış evraklar "YÜKLENEMEDİ
(OCR yok)" damgasıyla künyeye girer — sessiz atlama yoktur.

### 4. Node.js + `udf-cli` girişi (UDF üretimi için ZORUNLU)
UYAP'a sunulacak `.udf` dosyası **yalnız** resmî `udf-cli` aracıyla üretilebilir
(elle üretilen dosyalar UYAP editöründe **açılmaz** — sahada doğrulandı):

```bash
node --version
npx -y udf-cli@latest login
npx -y udf-cli@latest whoami
```

Giriş tek seferliktir; token `~/.config/yargi/token.json`'da tutulur. Giriş
yapılmamışsa sistem bozuk UDF üretmez — durur ve size giriş talimatı verir.

### 5. Yargı Pro MCP'yi ekleyin (içtihat doğrulaması için ZORUNLU)

```bash
claude mcp add --transport http yargipro https://yargi.betaspacestudio.com/mcp
```

(veya Claude Code **connectors** bölümünden aynı adresi ekleyin) ve OAuth
akışını tamamlayın. Bu bağlantı olmadan künye doğrulaması yapılamaz; içtihat
"teyit edilemedi" damgasıyla işlenir ve dış çıktıya "teyitli" giremez.

### 6. Eklentiyi kurun

```
/plugin marketplace add bcancapar-spec/ortak-avukat
/plugin install ortak-avukat@ortak-avukat
```

### 7. Claude Code'u TAM kapatıp açın
Bayat süreç eski hook setini taşımaya devam eder — pencereyi kapatmak yetmez,
uygulamayı tamamen kapatıp açın. yada yüklemeleri tamamlayınca bilgisayarı yeniden başlatın.  (saha dersi: "sıfır ateşleme"nin köklerinden
biri buydu).

### 8. Doğrulayın
Skill listesinde tek bir `ortak-avukat` ailesi (**20 skill**) görünmeli. Sürüm
etiketi yetmez — **dosya kanıtıyla** doğrulayın:

```bash
ls ~/.claude/plugins/cache/ortak-avukat/ortak-avukat/
```

Yalnız güncel sürüm klasörü görünmeli; eski sürüm klasörleri kalmışsa hangi
kodun koştuğu belirsizdir (bkz. sorun giderme).

> **5 dakikada ilk kullanım**
> 1. UYAP'tan dosyanızın evrakını bir klasöre indirin
>    ([avukat-dosya-indirici](https://github.com/bcancapar-spec/avukat-dosya-indirici) işinizi görür).
> 2. O klasörde Claude Code oturumu açın.
> 3. Yukarıdaki **prompt şablonunu** doldurup gönderin.
> 4. Sistemin sorularını cevaplayın; stratejik kavşaklarda size dönecektir.
> 5. Bitince `_oa/DURUM.md`'ye bakın; üretilen UDF'i UYAP editöründe **açıp
>    teyit edin**, e-imzayı **siz** atın.

### Güncelleme

```bash
claude plugin marketplace update ortak-avukat && claude plugin update ortak-avukat@ortak-avukat
```

Ardından Claude Code'u yine **TAM kapatıp açın**.

### Sorun giderme — temiz kurulum
Güncelleme takılırsa: eklentiyi ve marketplace'i kaldırın, Claude Code'u
kapatın, `~/.claude/plugins/cache/ortak-avukat` ile
`~/.claude/plugins/marketplaces/ortak-avukat` dizinlerini silin, yeniden
ekleyip kurun ve dosya kanıtıyla doğrulayın (8. adım).

---

## Avukatın göreceği dosyalar — `_oa/` yapısı(_oa/ yapısı Ortak Avukat kısaltmasıdır)

Tüm üretim, çalıştığınız klasörün içindeki `_oa/` yerel hafıza kökünde kalır;
müvekkil evrakına dokunulmaz. Sizin düzenli bakacağınız üç yer işaretlidir:

```
_oa/
├── DURUM.md        # ◄ SİZİN EKRANINIZ: nerede kalındı, ne bekliyor, hangi
│                   #   karar sizde — defterden türetilir, elle yazılmaz
├── metin/          # ingest çıktısı: 00-INDEX.md, künye, belge başına metin
├── analiz/         # dosya-analiz.md (çalışma hafızası)
├── cikti/          # çalışma evrakları: taslaklar, kıyas/antitez kayıtları
│   └── 40-UYAP/    # ◄ TESLİM KAPISI: UYAP'a yüklenecek nihai ürünler
│                   #   (UDF + mühür kaydı) tek klasörde toplanır (v0.5.9)
├── teyit/          # künye kütüğü + ham MCP dökümleri (kararların tam metni)
├── defter/         # olay defteri + TESLİM MAKBUZU ◄ (kapı çıkışlarının kanıtı)
├── devir/          # oturumlar arası devir paketleri
└── araclar/        # eklentiden kopyalanan denetim scriptleri (sürüm kilitli)
```

- **`DURUM.md`** — her oturumun başında ve sonunda bakacağınız canlı rapor:
  adım tablosu, süre nöbeti, "avukat kararı bekleyen" listesi, sıradaki iş.
- **Teslim makbuzu** (`defter/teslim-makbuz.json`) — teslim kapılarının
  çıkış kanıtı: hangi kapı geçti, hangisi engelledi, taslağın parmak izi ne.
  Yeşil makbuz yoksa ürün "teslime hazır" **değildir** ve sistem bunu sizden
  saklayamaz.
- **`cikti/40-UYAP/`** — UYAP'a girecek her şeyin tek adresi: aramanız gereken
  dosya hangi klasördeydi derdi biter.

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
- **E-imzanın geçerliliğini doğrulamaz.** İmzalı bir nüshayı tanır, korur ve
  bildirir; kriptografik doğrulama UYAP'ın işidir.
- **UYAP'a girmez, e-imza atmaz.** Bu adımlar münhasıran avukata aittir; sistem
  onlar için kod dahi yazmaz.
- **Resmî kaynak bağlı değilse künye doğrulayamaz** — ve bunu gizlemez, "teyit
  edilemedi" damgası basar.
- **Organik yeşil makbuz henüz ölçülmedi.** Sahada uçtan uca insan
  müdahalesiz yeşil makbuz hâlâ açık hedeftir; bu satır o gün ölçümle
  güncellenecektir.

---

## Gizlilik

Bu depo **hiçbir müvekkil verisi veya MCP kimlik bilgisi içermez**. Çalışma
evrakı (`_oa/`) `.gitignore` ile dışlanmıştır. Dış araca (bulut MCP/web) veri
çıkışı `oa-gizlilik` **Layer 0** süzgecine tabidir (müvekkil verisi, TCKN, IBAN,
telefon, e-posta, plaka, sağlık/ceza verisi taranır; şüphede engellenir). UYAP
login ve e-imza/PIN adımları münhasıran avukata aittir; sistem bunlar için kod
yazmaz. Saha kayıtlarında dosya kimlikleri anayasa m.7 gereği daima anonimdir
(Av.K. m.36 · KVKK).

---

## Geliştirici doğrulaması

Depo kökünde:

```bash
python -m pytest tests -q
python plugins/ortak-avukat/skills/oa-usta/scripts/aile_dogrula.py plugins/ortak-avukat/skills
```

İlki deterministik denetçilerin regresyonunu (depoda **1.350+ test**; son tam
koşu ölçümü 1317 yeşil / 1 tasarımsal atlama + sonrasında eklenen testler),
ikincisi ailenin yapısal sağlığını (frontmatter, name↔klasör, sürüm
tutarlılığı, manifest "N skill" sayımı, hook kapsamı) denetler. Güncel ölçüm
ve açık bulgular: [STATUS.md](STATUS.md) · yol haritası:
[YOL-HARITASI.md](YOL-HARITASI.md).

```
ortak-avukat/
├── .claude-plugin/marketplace.json
├── plugins/ortak-avukat/
│   ├── .claude-plugin/plugin.json
│   ├── hooks/hooks.json              # 6 olaylı model-bağımsız tetik katmanı
│   └── skills/                       # 20 skill (çekirdek + 19 oa-*)
├── tests/                            # pytest süiti
├── README.md · STATUS.md · LICENSE · NOTICE
```

---

## Fikri Mülkiyet ve Lisans

Bu depodaki tüm içerik — "Ortak Avukat" metodolojisi, skill metinleri, scriptler ve dokümantasyon dâhil — özgün bir eserdir ve **5846 sayılı Fikir ve Sanat Eserleri Kanunu (FSEK)** kapsamında korunur. Eserin sahibi ve tüm **mali ve manevi hakların** münhasır hak sahibi **Av. Bayram Can Çapar**'dır (b.cancapar@gmail.com).

Depo kamuya açık (public) olarak yayımlanmıştır;   Kopyalama, çoğaltma, dağıtma, değiştirme, çeviri, türev çalışma oluşturma ve ticari kullanım **önceden yazılı izne tabidir**. Telif/atıf bildirimleri ve hak sahibinin adı kaldırılamaz. Yalnızca Yargı Pro MCP oluşturan ekibin fikri değişimine ve gerektiğinde ticari amaçla kullanımına izin verilmiştir. 

Tam koşullar: [LICENSE](LICENSE) · Özet bildirim: [NOTICE](NOTICE).


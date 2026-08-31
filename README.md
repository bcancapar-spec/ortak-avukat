# Ortak Avukat · Türk Hukuku Co-Counsel Sistemi

> Yanınızda çalışan **kıdemli bir ortak avukat (co-counsel)** gibi davranan bir
> hukuk metodolojisi sistemi: UYAP'tan indirdiğiniz dosya klasörünü okur, süreleri
> hesaplar, içtihadı resmî kaynaktan tam metniyle doğrular, dilekçeyi yazar,
> teslimden önce kendi işini makineyle denetler — ve son kararı **daima size**
> bırakır. Bir Claude Code / Cowork **plugin marketplace** deposudur.
>
> Bir avukatın Türk hukuku metodoloji sistemidir. Dil modelleri şimdilik
> zekâ sahibi değildir; AGI henüz oluşmamıştır. Bu yüzden modelin
> yetenekleri, deterministik olması için Python kodlarıyla — plugin kodlama
> yönünden olan kısmında deneme/yanılma ile — kurulmuştur ve geliştirilmeye
> devam edilmektedir. Unutmayınız: dil modelleri OLASILIK ile çalışır, akıl
> ve zekâ ile değil. (Gerçek davalarda test edilmektedir.)

**Sürüm:** 0.5.15 · **Yazar:** Av. Bayram Can Çapar · **20 skill** (çekirdek + 19 `oa-*` parça)

> ⚖️ **Gerçek davalarda test edildi.Geliştirilmeye devam ediliyor.** Bu sistem sentetik örneklerle değil,
> derdest gerçek dosyalarla sahada sınanıyor: v0.0.1'den v0.5.15'e gelen
> geliştirme zinciri **149 gerçek davada** test edildi; bunların **dokuzu**,
> sensörlü izleme + karne + adli analizle BELGELİ büyük saha koşusudur:
> (1) ~200 evraklık istinaf dosyasında ek beyan (ilk tam koşu), (2) 214
> evraklık bakir klasörde müdahalesiz test, (3) 447 sahası — vergi davası,
> (4) 372 sahası — aile/mal rejimi, (5) 346 sahası — bilirkişi ek raporuna
> itiraz, (6) 777 sahası — banka/kefalet ikinci cevap + 24 kök çapraz
> taraması, (7) 307 sahası — tasarrufun iptalinde ikinci cevap (devralmalı),
> (8) 923 sahası — vergi/gümrük, ödeme emri + ek tahakkuk (ilk organik yeşil
> makbuz), (9) 1865 sahası — idari yüksek yargıda soruşturma-izni itirazı
> (çok oturumlu, iki müvekkil). Ayrıntılar aşağıdaki tabloda ve karnelerdedir. yapılmış teste alınmayanşekilde sistemin ilk çalışmasında sonuca ulaşıldığı davalar görmezden gelinmiş ve teste yansıtılmamıştır. Test için ayrılan davalarda ise başarı sağlanmıştır. 
> İlk ölçüm: ~200 evraklık gerçek bir istinaf dosyası, **tek bir doğal-dil
> prompt'la**, 49 dakikada ve 45,6k token'la teslim edilebilir  davalının istinaf dilekçesine
> geçerli UDF'e dönüştü (dünyadaki şimdilik en güçlü kabul edilen en pahalı token tüketen modelde plug in sayesinde en ucuz token tüketimi ve en yüksek çıktı kalitesi yakalanmıştır. ( Plug in öncesi Claude Fable 5, max efor ile önceden yaklaşık 1,2m+ token tüketiliyordu 1m token 50$ test için özellikle en pahalımodel seçildi ve test edildi tasarruf maddiyatla görülerek gerçekleşti. ) ; evraklar
> [avukat-dosya-indirici](https://github.com/bcancapar-spec/avukat-dosya-indirici) ile pdf olarak indirilmiş ve bu plug in ile .md .json formatlarına otonom olarak çevrilmiştir. 
 Sayılar, dürüst kayıp listesiyle birlikte:
> **[SAHA-SONUCU.md](SAHA-SONUCU.md)** ·  > **[BASARI.md](BASARI.md)**. dosyalarında raporla sunulmuştur. Dosya kimlikleri projenin anayasası m.7 gereği daima
> anonimdir. Hukuk erişilebilir olmalıdır. su ve nefes gibi..

> **© 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır.** Bu eserin fikri mülkiyeti ile tüm mali ve manevi hakları münhasıran Av. Bayram Can Çapar'a aittir.Ticari amaçla klonlanıp/tersine mühendislik kullanılmadığı müddetçe ücretsizdir.Ticari ürün olarak kullanılamaz.   (5846 sayılı FSEK). Depo kamuya açıktır; izinsiz kopyalama/dağıtma/türev/maddi amaç yasaktır. Beta sürümleri tamamlanana kadar avukatlar ve geliştiriciler geliştirmeye ve kullanmaya yetkilidir.  Bkz. [LICENSE](LICENSE) ve [NOTICE](NOTICE).

---

## Bu nedir 
hukuk ve hak arama hürriyeti su ve nefes gibi erişilebilir olmalıdır.Eşit ve adelet gözetilmelidir.
**Büyük dil modellerini Türk Hukuku alanlarında deterministik çalıştırmak üzere hazırlanmış bir METODOLOJİ SİSTEMİDİR.**
Kıdemli bir avukatın çalışma metodunu — dosyayı ele alış sırasını, usulü esastan
önce denetleme refleksini, künyeyi resmî kaynaktan doğrulama disiplinini, zaafı
müvekkile karşı değil müvekkil için kullanma ayrımını — yazıya döker ve **her
adımını makineyle denetler.** Dil modeli kurar makine deterministik olarak denetler prensibi ile çalışır. 

Ayırt edici yanı şudur: bir işin yapıldığını **modelin beyanına bırakmaz.**
"İçtihadı doğruladım" "uyuşmazlığı doğruladım" "hukuki ihtilafı çözdüm veya buldum" demek yetmez. Tüm uyuşmazlık deterministik olarak kodlanır ve yerel diske kaydedilir.  — kararın tam metni diske inmiş, davaya bağı
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

Yirmi parça, 20 ayrı araç gibi değil **yetenek sahibi tek bir ortak-avukat** gibi
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


Tüm üretim, çalıştığınız klasörün içindeki `_oa/` yerel hafıza kökünde kalır.
**Müvekkil evrakı salt-okunurdur, değiştirilmez.**

---

## Kurulum — kolay yol

### 0. Tek yapıştırmayla kurulum — sistemi Claude Code kendisi kursun

Aşağıdaki bloğu OLDUĞU GİBİ kopyalayıp Claude Code'un sohbet kutusuna
yapıştırın; kurulumu sizin yerinize Claude yürütür, yalnız insan eli gereken
yerlerde (tarayıcı onayı gibi) durup size söyler:

```text
Bu bilgisayara "Ortak Avukat" sistemini uçtan uca kur. Sırayla ve her adımın
sonucunu tek satır göstererek ilerle:

1) Python 3.10+ kurulu mu denetle (python --version). Yoksa kurulum linkini
   ver ve bekle. Varsa: pip install pymupdf pillow markitdown[all] (kuruluysa geç).
2) Tesseract OCR + Türkçe paketi denetle (tesseract --list-langs içinde
   "tur"). Eksikse Windows için UB-Mannheim kurulum sayfası linkini ver,
   kurulumda "Turkish" dilini seçmemi söyle ve ben kurana kadar bekle.
3) Node.js/npx denetle (node --version). Yoksa nodejs.org LTS linkini ver ve
   bekle. Varsa `npx -y udf-cli@latest login` başlat; tarayıcı onayı
   gerektiğinde adresi ve kodu bana göster, ben onaylayınca
   `npx -y udf-cli@latest whoami` ile doğrula.
4) Yargı Pro MCP bağlantısını kur (uç nokta:
   https://yargi.betaspacestudio.com/mcp). Bağlayıcı onayı benden isteniyorsa
   dur ve ne yapacağımı söyle. (Alternatif kanal kullanacaksam ben söylerim.)
5) Eklentiyi kur: önce `claude plugin marketplace add
   bcancapar-spec/ortak-avukat`, sonra `claude plugin install
   ortak-avukat@ortak-avukat`. CLI yoksa bana sohbete yazmam için
   /plugin komutlarını ver.
6) DOSYA KANITIYLA doğrula: eklenti önbelleğinde ortak-avukat klasörünün ve
   20 skill'in indiğini listele; sürüm damgasını göster.
7) Özet tablo ver: hangi adım TAMAM, hangisi benim elimi bekliyor. En sonda
   Claude Code'u TAM kapatıp açmam gerektiğini hatırlat.

Kurallar: benden hiçbir şifre/PIN/kart bilgisi isteme ve hiçbirini bir yere
yazma; e-imza ve UYAP girişi kurulumun parçası DEĞİLDİR; var olan kurulumları
bozma (önce denetle, eksikse kur).
```

Kurulum bittikten sonra Claude Code'u **tamamen kapatıp açın** (7. adım bunu
zaten hatırlatır). Elle, adım adım kurmayı tercih ederseniz aşağıdaki tablo
ve 1-8 numaralı adımlar aynı işin açılımıdır.

Sistem dört ayağa basar. Önce ne gerektiğini ve **neden** gerektiğini görün,
sonra adım adım kurun. Bu tablodaki ve repodaki teknik terimler yabancıysa:
**[Hukukçular için sözlük → SOZLUK.md](SOZLUK.md)**.

| Yazılım | Nereden | Neden gerekli |
|---|---|---|
| **Claude Code** (veya Claude masaüstü/Cowork) | [claude.com/claude-code](https://claude.com/claude-code) | Sistemin koştuğu ajan ortamı: skill'ler, hook ağı ve MCP bağlantıları burada yaşar. Eklenti bu ortama kurulur. |
| **Python 3.10+** | [python.org/downloads](https://www.python.org/downloads/) | Bütün deterministik denetim scriptleri (defter, makbuz, künye teyidi, süre hesabı, teslim zinciri) Python'dur — "script denetler" ayağının motoru. |
| **PyMuPDF** (pip paketi) | [pypi.org/project/PyMuPDF](https://pypi.org/project/PyMuPDF/) | Metin-katmanlı PDF'lerden evrak çıkarımı ve PDF önizleme üretimi — evrakı görüntü olarak modele yüklememenin (26× tasarrufun) temeli. |
| **Pillow** (pip paketi) | [pypi.org/project/pillow](https://pypi.org/project/pillow/) | TIFF/görüntü evrakların sayfalara ayrılıp OCR'a hazırlanması. |
| **MarkItDown** (Microsoft, pip paketi) | [github.com/microsoft/markitdown](https://github.com/microsoft/markitdown) | Office ve karışık formatlı evrakı (**.docx, .xlsx, .pptx**, HTML, e-posta, CSV/JSON, hatta bazı PDF'ler) tek elden **Markdown'a** çevirir. UYAP klasörü yalnız PDF/TIFF değildir: bilirkişi raporu Excel, ekler PowerPoint, yazışma Word olarak gelir. Bu araç olmadan o evraklar ya modele görüntü olarak yüklenir (token patlaması) ya da hiç okunmaz. Metne bir kez indirip her adımda o metni seçici okuma ekonomisinin Office ayağıdır. |
| **Tesseract OCR + Türkçe dil paketi** | [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki) | UYAP klasörlerindeki taranmış evrak (mazbata, eski dilekçe, TIFF) metne ancak OCR ile iner; çıktı "⚠ teyit gerek" damgası alır. Türkçe paket (`tur`) olmadan Türkçe evrak doğru okunmaz. |
| **Node.js (LTS)** | [nodejs.org](https://nodejs.org/) | UDF üretim araçları npm ekosisteminde yaşar ve `npx` ile koşar. |
| **udf-cli** (npx, giriş gerekli) | [npmjs.com/package/udf-cli](https://www.npmjs.com/package/udf-cli) | UYAP'ın fiilen AÇABİLDİĞİ .udf dosyasını üreten resmî araç (`html2udf`). Sahada kanıtlandı: elle kurulan UDF editörde açılmıyor — tek geçerli yol budur. Bir kez `npx -y udf-cli@latest login` gerekir. |
| **uyap-tiff-cli / uyap-pdf-cli** (npx, aynı giriş) | [npmjs.com/package/uyap-tiff-cli](https://www.npmjs.com/package/uyap-tiff-cli) · [npmjs.com/package/uyap-pdf-cli](https://www.npmjs.com/package/uyap-pdf-cli) | Çok sayfalı TIFF'i kayıpsız PDF'e çevirme ve taranmış PDF'te otomatik OCR — ham UYAP klasörünün iki tuzağını kapatır. Giriş `udf-cli` ile ortaktır. |
| **Yargı Pro MCP** (geliştirici: [@saidsurucu](https://github.com/saidsurucu)) | [yargi.betaspacestudio.com/mcp](https://yargi.betaspacestudio.com/mcp) | İçtihat/mevzuat resmî doğrulama kanalı: mutlak triyaj [G6] kararların TAM METNİNİ bu kanaldan çeker; künye teyidi ve semantik arama buradan beslenir. Bu olmadan sistem "doğrulanmamış atıf iddiadır" kuralı gereği içtihatlı dilekçe teslim etmez. Alternatif: açık kaynak [yargi-mcp](https://github.com/saidsurucu/yargi-mcp) (semantik arama için ayrıca AI API anahtarı gerekir). |

Adım adım:

### 1. Claude Code'u kurun
Claude Code (CLI veya Desktop) kurulu ve oturum açık olmalı: <https://claude.com/claude-code>

### 2. Python 3.10+ ve iki paket

```bash
python --version
pip install pymupdf pillow markitdown[all]
```

`pymupdf` PDF metin çıkarımı, `pillow` TIFF/JPG işleme içindir — bunlar olmadan
evrak işlenemez. **`markitdown`** (Microsoft) Office ve karışık formatlı evrakı
Markdown'a çevirir: `.docx` yazışma, `.xlsx` bilirkişi hesap tablosu, `.pptx`
sunum eki, HTML/e-posta çıktısı. `[all]` eki tüm format eklentilerini kurar;
dar kurulum isterseniz `pip install markitdown` da çalışır ama bazı formatlar
kapsam dışı kalır.

```bash
markitdown --help
```

Depo ve ayrıntılı kullanım: [github.com/microsoft/markitdown](https://github.com/microsoft/markitdown).
Bu araç **yerelde** çalışır; evrak dışarı gönderilmez (Layer 0 gizliliğiyle uyumlu).

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

**Yargı Pro kullanmayanlar için alternatif:** açık kaynak
[yargi-mcp](https://github.com/saidsurucu/yargi-mcp) sunucusu da içtihat
arama kanalı olarak bağlanabilir — dikkat: **semantik arama özelliği için
ayrıca bir AI API anahtarı gerekir** ve kanal yetenekleri Yargı Pro ile
birebir değildir; sistemin "resmî kaynaktan teyit" kuralı hangi kanal
bağlıysa onun üzerinden işler.

> 🙏 **Emek etiketi:** Türk hukuku içtihat/mevzuat erişimini modele açan her
> iki köprü de — **Yargı Pro MCP** ve açık kaynak **yargi-mcp** —
> [Said Sürücü](https://github.com/saidsurucu)'nün eseridir. Bu sistemin
> "resmî kaynaktan tam metin" disiplini, onun kurduğu gişeler üzerinde çalışır.

### 6. Eklentiyi (plugin) kurun — hukukçu için adım adım

Eklenti kurulumu iki satırdır ve programcılık bilgisi GEREKTİRMEZ. Yeriniz:
Claude Code'un **sohbet kutusu** — yani normalde soru yazdığınız yer. Baştaki
`/` işareti dahil, satırı aynen yazıp Enter'a basacaksınız.

**Adım 6a — mağaza rafını tanıtın** (bir kez yapılır):

```
/plugin marketplace add bcancapar-spec/ortak-avukat
```

Bu komut, Ortak Avukat'ın yayımlandığı GitHub rafını Claude Code'a tanıtır.
"added/eklendi" sınıfı bir onay mesajı görürsünüz.

**Adım 6b — eklentiyi o raftan kurun:**

```
/plugin install ortak-avukat@ortak-avukat
```

Claude Code onay isterse onaylayın; kurulum birkaç saniye sürer ve 20
skill'lik aile makinenize iner. (`@` işaretinin iki yanı aynıdır: eklenti
adı @ raf adı.)

**Takılırsanız:** komutlar terminale değil SOHBET kutusuna yazılır ve `/`
ile başlar; `/plugin` yazdığınızda menü açılıyorsa oradan da
Marketplace → Add ve Install adımlarını tıklayarak ilerleyebilirsiniz.
Terminalden kurmayı bilenler için eşdeğeri: `claude plugin marketplace add
bcancapar-spec/ortak-avukat` ve `claude plugin install
ortak-avukat@ortak-avukat`.

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

## DÜSTUR — sistemin anayasası

Yirmi parçanın tamamı hooklar ile birbirine bağlanmış Av.Bayram Can ÇAPAR tarafından oluşturulan tek bir fiktif anayasaya tabidir
([`anayasa.md`](plugins/ortak-avukat/skills/ortak-avukat/references/anayasa.md);
tam metin kök dizinde: [ANAYASA.md](ANAYASA.md)).
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
| **Dava dilekçesi** | "Davayı biz açıyoruz: [talep — ör. alacak/tazminat/tahliye/iptal]. Görevli-yetkili mahkemeyi ve harca esas değeri değerlendir; zamanaşımı/hak düşürücü süreyi kontrol et; dava dilekçesini delil listesiyle birlikte hazırla." |
| **Savunma dilekçesi (ceza)** | "[Sanık müdafii / şüpheli müdafii] olarak savunma yapacağız; [iddianame/ifade çağrısı] [tarih] günü tebliğ edildi. Suçun unsurlarını tek tek denetle, delil yasaklarını tara, lehe delilleri topla ve savunma dilekçesini hazırla." |
| **Suç duyurusu / şikâyet** | "Müşteki vekiliyiz; şikâyet süresini kontrol et, suçun unsurlarını delillere eşleyerek suç duyurusu dilekçesi hazırla; celbi gereken delilleri ayrıca listele." |
| **İdari başvuru** | "Dava öncesi idari başvuru aşamasındayız: [işlem/eylem] [tarih] günü tebliğ edildi/öğrenildi. Başvuru ve dava sürelerini birlikte hesapla; [ilgili idareye] itiraz/başvuru dilekçesini hazırla ve zımni ret ihtimaline göre takvimi çıkar." |
| **Kuruma dilekçe** | "[Kurum — ör. SGK/vergi dairesi/tapu/belediye/KVKK] nezdinde [talep/itiraz] için kurum dilekçesi hazırla; dayanak mevzuatı tam künyesiyle doğrula ve varsa başvuru süresini nöbete al." |
| **Yalnız analiz** | "Henüz dilekçe istemiyorum; dosyayı işle, güçlü/zayıf yanlarımızı ve yol seçeneklerini içeren bir strateji notu çıkar." |

> **Kapanış promptu gerekmez (v0.5.9).** Oturum kapanırken defter denetimi,
> mühür ve makbuz kontrolleri hook'larla **kendiliğinden** koşar; "işi kapat,
> denetle" diye ayrıca yazmanız gerekmez. Aynı şekilde her taslak yazımında
> hızlı denetim kendiliğinden çalışır ve bulgusunu modele anında geri verir —
> sizden hiçbir "mekanik hijyen" cümlesi beklenmez.

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
 v0.5.11 ile **kit güvenlik katmanı** geldi: araç kopyaları yalnız güvenilir kaynaktan doğar (uygulamanın rpm anlık-görüntü yolu karantinada), tam-nesil çekirdek scriptler salt-okunur kilitlenir, tazelik uyarısı yön bilir (bayat / kanaldan-yeni / özdeş) ve her defter olayı ile makbuz, hangi oturumun ürünü olduğunu söyleyen **oturum damgası** taşır — çok oturumlu çalışmada (aynı dosyada 5-6 paralel oturum sahada ölçüldü) kim-ne-yaptı sorusu artık cevaplıdır.

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
denetim kendiliğinden koşar ve bulgusunu modele anında geri verir. v0.5.10
ile **üretim ve mühür tek atomik işlemdir**: her başarılı UDF üretimi kendi
mührünü (.prov.json) kendisi basar/tazeler — mühürsüz ya da bayat-mühürlü
ürün akışta yaşayamaz. E-imzalı
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
de gönder" demek sizin kararınızdır, ama artık **görmeden olmaz**. v0.5.10'un
**filo-tazelik kapısı** denetimi seçili üründen filoya genişletti: dava kökü +
40-UYAP'taki TÜM teslim-sınıfı UDF'ler mühür-tazelik hükmünden geçer ve
tamamı makbuza yazılır — "makbuz yeşil ama yüklenecek dosya başka" penceresi
(307 karnesi) yapısal olarak kapandı; sunum kilidi de yeşil makbuz varken bile
bayat-mühürlü ürünü yakalar.

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
| Vakıa / antitez / kıyas | Kronoloji-delil eşlemesi, sekiz cephe bütünlüğü, unsur eşleşme denetimi |
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
Süitin tamamı her push'ta dört ortamda (Windows + Ubuntu × iki Python)
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
| **1865 sahası** | idari yüksek yargı, soruşturma-izni itirazı — **çok oturumlu** (5-6 paralel), iki müvekkil | rpm bayat-kit nüksü adlandırıldı; söz-müdahalesi ezildi, dosya-düzeyi koruma tuttu → v0.5.11: rpm karantinası + kilitli çekirdek + yönlü tazelik + oturum damgası ([KARNE-1865.md](KARNE-1865.md)) · **toplam ~4,3M token** |

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
| Antitez / usul | 8/8 cephe + çürütme; usul matrisi süre hesabını bağladı (son gün tespiti) |
| Bayat araç nöbetçisi | Bu sahada da ateşledi (1 uyarı) |
| Dürüst altyapı notu | Model, canlı içtihat ucuna erişemeyince yedek arşivle çalıştığını ve arşiv-sonrası kararların eksik olabileceğini kütüğün başına **kendisi yazdı** ("AŞAN-KAYNAK" riski) |
| [G6] sınavının SONUCU | Kapı ÇALIŞTI: teslim zinciri dökümsüz atıflarla RED verdi; model 7 kararın tam metnini döküp damgaladıktan sonra yeşil makbuz kesebildi (04:53). Ayrıca bu koşu, v0.5.10'u doğuran iki kusuru bağımsız tekrarladı: 40-UYAP kopyalarında çift-uzantı ve mühürsüz kopya |

**1865 sahası (25-26.08.2026, v0.5.10→v0.5.11, TAMAMLANDI — sınıf:
MÜDAHALELİ-YETKİLİ · ÇOK OTURUMLU):** idari yüksek yargıda soruşturma-izni
itirazı; iki müvekkil, iki dilekçe + çelişki raporu; aynı klasörde 5-6 paralel
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
  dilekçeyi kesen kapı — hepsi tarihiyle [STATUS.md](STATUS.md)'de durur.

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

İlki deterministik denetçilerin regresyonunu (süitin güncel büyüklüğü ve son
tam koşu ölçümü [tests/README.md](tests/README.md)'de — depoda tek kaynak
orasıdır), ikincisi ailenin yapısal sağlığını (frontmatter, name↔klasör, sürüm
tutarlılığı, manifest "N skill" sayımı, hook kapsamı) denetler. Güncel ölçüm
ve açık bulgular: [STATUS.md](STATUS.md) · yol haritası:
[YOL-HARITASI.md](YOL-HARITASI.md) · sürüm zincirinin kök defteri:
[CHANGELOG.md](CHANGELOG.md) (parça ayrıntısı her skill'in kendi
`references/degisiklik-gunlugu.md` dosyasındadır).

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

Depo kamuya açık (public) olarak yayımlanmıştır;   Kopyalama, çoğaltma, dağıtma, değiştirme, çeviri, türev çalışma oluşturma ve ticari kullanım **önceden yazılı izne tabidir**. Telif/atıf bildirimleri ve hak sahibinin adı kaldırılamaz. 

Tam koşullar: [LICENSE](LICENSE) · Özet bildirim: [NOTICE](NOTICE).


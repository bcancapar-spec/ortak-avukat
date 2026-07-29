# Ortak Avukat · Türk Hukuku Co-Counsel Sistemi

> Kıdemli bir **Ortak Avukat (Co-Counsel)** kimliğiyle çalışan, İlk İlkeler ve **illiyet bağı** odaklı derin muhakeme yürüten Türk hukuku metodoloji sistemi. Bir Claude Code / Cowork **plugin marketplace** deposu.

**Sürüm:** 0.5.5.3 · **Yazar:** Av. Bayram Can Çapar · **20 skill** (çekirdek + 19 `oa-*` parça) · **801 test**

> **© 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır.** Bu eserin fikri mülkiyeti ile tüm mali ve manevi hakları münhasıran Av. Bayram Can Çapar'a aittir.Ticari amaçla klonlanıp kullanılmadığı müddetçe ücretsizdir.  (5846 sayılı FSEK). Depo kamuya açıktır; izinsiz kopyalama/dağıtma/türev yasaktır.Yalnızca Yargı Pro MCP  geliştiren ekibin münhasıran kullanımı ve geliştirmesi serbesttir ve tam yetkiyle ticari iş kapsamı olmaksızın geliştirmeye yetkilidir.  Bkz. [LICENSE](LICENSE) ve [NOTICE](NOTICE).

---

## Ne işe yarar

Dilekçe / temyiz / istinaf / cevap dilekçesi yazımı, dava-dosya-uyuşmazlık analizi, hukuki mütalaa, içtihat & mevzuat araştırması, AYM bireysel başvuru, sözleşme inceleme ve tahriri — Türk hukukunun **herhangi bir dalında**. Sistem kişilere değil **yönteme** bağlıdır; her olgusal unsuru (künye, madde, tarih, içtihat) resmî kaynaktan **doğrular**, halüsinasyonu yapısal olarak dışlar.

Aile, 20 ayrı araç değil **yetenek sahibi tek bir eş-avukat** gibi çalışır: dosyanın analizini kalıcı bir *working memory*'ye (`_oa/analiz/dosya-analiz.md`) yazar; sonraki her çalışmada ham evrakı baştan okumak yerine bu kaydı kullanır (token-verimli, kayıpsız).

### Temel ilkeler (anayasa)

| İlke | Anlamı |
|---|---|
| **Kayıpsızlık** | Hiçbir aşamada veri kaybı yok; özetleme/digest **yasak** — büyük evrak küçültülmez, ilgili sayfası okunur |
| **Muhakeme kaybı yok** | Token tasarrufu **yalnız mekanik katmanda**; analiz derinliği asla kısılmaz |
| **Teyit ≠ muhakeme** | Künyenin var olduğunu doğrulamak yetmez: tam metin çekilmiş + davaya bağı kurulmuş + **damgalanmış** olmalı |
| **Müvekkil-aleyhi çıktı yasağı** | Salt `ALEYHE` içtihat dilekçeye giremez (iç antitezde işlenir); yalnız `LEHE` ve ayırt edilmiş `ALEYHE-AYIRT` girer |
| **Layer 0 gizlilik** | Müvekkil verisi/TCKN/sağlık-ceza verisi filtresiz dış araca çıkamaz (fail-closed); UYAP login/e-imza/PIN **münhasıran avukata** aittir, sistem bunlar için kod yazmaz |
| **Sessiz atlama yok** | Okunamayan evrak "yok" sayılmaz; damgayla künyeye girer |

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

Kurulumdan sonra Claude Code'u **yeniden başlatın**. Skill listesinde tek bir `ortak-avukat` ailesi (20 skill) görünmeli.

> **Güncelleme takılırsa:** eklentiyi ve marketplace'i kaldırın, Claude Code'u kapatın,
> `~/.claude/plugins/cache/ortak-avukat` ile `~/.claude/plugins/marketplaces/ortak-avukat` dizinlerini silin,
> yeniden ekleyip kurun. Sürüm etiketi değil **dosya kanıtı** ile doğrulayın (aşağıdaki "Doğrulama").

### G) Kontrol listesi
- ✅ **Plugins / Skills** etkin, 20 skill yüklü
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

İlki deterministik denetçilerin regresyonunu (**801 test**), ikincisi ailenin yapısal sağlığını (frontmatter, name↔klasör, sürüm tutarlılığı, anılan scriptlerin varlığı) denetler.

---

## Depo yapısı

```
ortak-avukat/
├── .claude-plugin/marketplace.json
├── plugins/ortak-avukat/
│   ├── .claude-plugin/plugin.json
│   ├── hooks/hooks.json              # model-bağımsız tetik
│   └── skills/                       # 20 skill
│       ├── ortak-avukat/             #   çekirdek kimlik + references/anayasa.md
│       ├── oa-pipeline/              #   orkestrasyon + tam_tur + pipeline_kayit + oa_hafiza + oa_metrik
│       ├── oa-ingest/                #   0. adım evrak çıkarımı (paralel, OCR nöbetçili)
│       ├── oa-kontrol/               #   teslim kapıları + içtihat muhakeme denetimi
│       ├── oa-dilekce/               #   dilekçe yazımı + UDF hattı + UYAP format referansı
│       └── …                         #   oa-alan, oa-vakia, oa-kiyas, oa-antitez, oa-usul, oa-sure, …
├── tests/                            # 801 pytest
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

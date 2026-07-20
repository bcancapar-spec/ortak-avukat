# Ortak Avukat · Türk Hukuku Co-Counsel Sistemi

> Kıdemli bir **Ortak Avukat (Co-Counsel)** kimliğiyle çalışan, İlk İlkeler ve **illiyet bağı** odaklı derin muhakeme yürüten Türk hukuku metodoloji sistemi. Bir Claude Code / Cowork **plugin marketplace** deposu.

**Sürüm:** 0.5.4 · **Yazar:** Av. Bayram Can Çapar · **20 skill** (çekirdek + 19 `oa-*` parça)

> **© 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır.** Bu eserin fikri mülkiyeti ile tüm mali ve manevi hakları münhasıran Av. Bayram Can Çapar'a aittir.Ticari amaçla klonlanıp kullanılmadığı müddetçe ücretsizdir.  (5846 sayılı FSEK). Depo kamuya açıktır; izinsiz kopyalama/dağıtma/türev yasaktır.Yalnızca Yargı Pro MCP  geliştiren ekibin münhasıran kullanımı ve geliştirmesi serbesttir ve tam yetkiyle ticari iş kapsamı olmaksızın geliştirmeye yetkilidir.  Bkz. [LICENSE](LICENSE) ve [NOTICE](NOTICE).

---

## Ne işe yarar

Dilekçe / temyiz / istinaf / cevap dilekçesi yazımı, dava-dosya-uyuşmazlık analizi, hukuki mütalaa, içtihat & mevzuat araştırması, AYM bireysel başvuru, sözleşme inceleme ve tahriri — Türk hukukunun **herhangi bir dalında**. Sistem kişilere değil **yönteme** bağlıdır; her olgusal unsuru (künye, madde, tarih, içtihat) resmî kaynaktan **doğrular**, halüsinasyonu yapısal olarak dışlar.

Aile, 20 ayrı araç değil **yetenek sahibi tek bir eş-avukat** gibi çalışır: dosyanın analizini kalıcı bir *working memory*'ye (`_oa/analiz/dosya-analiz.md`) yazar; sonraki her çalışmada ham evrakı baştan okumak yerine bu kaydı kullanır (token-verimli, kayıpsız).

---

## Gereksinimler ve Kurulum

Sistem üç katmandır: **(1) Claude Code** (ana ortam) · **(2) yerel programlar** (evrak metin çıkarımı + deterministik denetim scriptleri için Python + Tesseract) · **(3) Yargı Pro MCP** (içtihat/mevzuat doğrulaması). Hepsi aşağıda.

### A) Claude Code
Claude Code (CLI, Desktop veya web) kurulu ve oturum açık olmalı. Eklenti/skill ve MCP desteği bu ortamdan gelir.

### B) Python + kütüphaneler — evrak çıkarımı & denetim scriptleri
`oa-ingest` (0. adım: evrak → ucuz metin) ve tüm deterministik denetim scriptleri **Python** ile çalışır.
- **Python 3.10+** kurulu; `python` komutu PATH'te erişilebilir olmalı — doğrula: `python --version`
- Gerekli kütüphaneler (saf wheel, ek binary gerektirmez):
  ```bash
  pip install pymupdf pillow
  ```
  `pymupdf` → PDF metin/görüntü çıkarımı · `pillow` → TIFF/JPG/PNG işleme.
- Bunlar olmadan PDF/görüntü evrak (metin PDF dahil) işlenemez.

### C) Tesseract OCR — taranmış evrak için (önerilir)
Taranmış/fontsuz PDF ve görüntü (TIFF/JPG) evrakların OCR'ı için **Tesseract** gerekir.
- **Windows:** [UB-Mannheim Tesseract kurucusu](https://github.com/UB-Mannheim/tesseract/wiki) — kurulumda **Turkish (`tur`)** dil paketini seç **ve** "Add Tesseract to PATH" işaretle.
- **Linux:** `sudo apt-get install tesseract-ocr tesseract-ocr-tur`
- **macOS:** `brew install tesseract tesseract-lang`
- Doğrula: `tesseract --version`
- Tesseract yoksa metin PDF/UDF/DOCX yine **bedava** işlenir; yalnız taranmış evraklar "YÜKLENEMEDİ (OCR yok)" damgasıyla künyeye girer — **sessiz atlama yoktur** (kayıpsızlık korunur).

### D) Yargı Pro MCP — içtihat/mevzuat doğrulaması (**zorunlu**)
Ailenin içtihat/mevzuat/kurum-kararı doğrulaması **Yargı Pro** MCP sunucusuna dayanır (Yargıtay, Danıştay, AYM, Bedesten, Mevzuat, YÖK Tez). Claude Code **connectors** bölümünden ekleyin:
```
https://yargi.betaspacestudio.com/mcp
```
veya komut satırından:
```bash
claude mcp add --transport http "yargipro" https://yargi.betaspacestudio.com/mcp
```
OAuth akışını tamamlayın. **Bu bağlantı olmadan** yetenekler künye doğrulaması yapamaz; anayasa gereği içtihat "teyit edilemedi" damgasıyla işlenir ve dış çıktıya "teyitli" olarak giremez (halüsinasyon yapısal olarak dışlanır).

### E) Eklentiyi kurun
```
/plugin marketplace add bcancapar-spec/ortak-avukat
/plugin install ortak-avukat@ortak-avukat
```
Kurulumdan sonra Claude Code'u **yeniden başlatın**. Skill listesinde tek bir `ortak-avukat` ailesi (20 skill) görünmeli; mükerrer/eski kopya olmamalı. (Alternatif: `releases` altındaki `.plugin` dosyasını sohbete bırakıp onaylayın.)

### F) Claude Code'da açık/etkin olması gerekenler — özet kontrol listesi
- ✅ **Plugins / Skills** etkin (eklenti kurulu + skill'ler yüklü)
- ✅ **Yargı Pro MCP** bağlı, OAuth tamam (içtihat/mevzuat için varsayılan kaynak)
- ✅ **Python + `pymupdf` + `pillow`** PATH'te (evrak çıkarımı)
- ✅ **Tesseract** (`tur` dil paketiyle) PATH'te (taranmış evrak OCR'ı — önerilir)
- ℹ️ **Çok çekirdekli CPU** — `oa-ingest` paralel çalışır (`--isci` otomatik = `min(çekirdek, 8)`); çok çekirdek = daha hızlı ingest (yüzlerce evraklık dosyada belirgin hızlanma)

---

## Kullanım / iş akışı

1. **Evrakı indir:** UYAP dava/icra dosyasındaki evrakları (PDF/TIFF/UDF/EYP/DOCX) bir klasöre indir (ör. bir "UYAP evrak indirici" tarayıcı eklentisiyle).
2. **O klasörde Claude Code başlat.**
3. **Prompt ver:** "davayı analiz et", "temyiz/istinaf/cevap dilekçesi yaz", "içtihat ara", "süreyi hesapla", "bu olaya hangi madde nasıl uygulanır" gibi.
4. **Sistem ne yapar:** önce evrakı en ucuz doğru yoldan metne çevirir (`oa-ingest`), dosya analizini working memory'ye yazar, içtihat/mevzuatı Yargı Pro'dan doğrular, teslim öncesi mekanik kapılardan (süre, usul, atıf teyidi, müvekkil-aleyhi tarama, tertip/düzen) geçirir.
5. **Çıktı:** aksi istenmedikçe **UDF** (UYAP'a uygun) formatında; istenirse `md`/`docx`.

Tüm üretim çalışılan klasörün `_oa/` yerel hafıza kökünde kalır. **Müvekkil evrakı salt-okunurdur, değiştirilmez.**

---

## Öne çıkanlar

- **Tek eş-avukat / working memory** — aile 20 organlı tek bir kıdemli eş-avukat gibi; dosya anlayışı `dosya-analiz.md`'de kalıcı, devirde ham evrak baştan okunmaz.
- **Lego mimarisi** — 20 bağımsız parça; `oa-pipeline` uçtan uca orkestrasyon (MANİFEST → … → KAPANIŞ).
- **Kesişen katmanlar** — `oa-usul` (usulün esasa takaddümü), `oa-illiyet` (nedensellik grafı), `oa-gizlilik` (meslek sırrı / Privacy Layer 0).
- **Deterministik denetim** — Python scriptleri model muhakemesini denetler: süre/zamanaşımı, illiyet grafı, açık kıyas, antitez, usul, **atıf/künye teyidi**, **içtihat muhakeme zinciri** (çekilir + davaya bağı kurulur + lehe/aleyhe damgalanır), **okuma ekonomisi** (token-verimli seçici okuma), **kalıcılık kapısı** (analiz kaydı daima üretilir).
- **Kayıpsızlık + muhakeme invaryantı** — her aşamada veri kaybı yok, muhakeme kaybı yok; token tasarrufu yalnız mekanik katmanda (özetleme yasak).
- **Ceza dalı** — `oa-mudafii` (savunma) ve `oa-musteki-vekili` (iddia) aynı unsur-inşasının iki yüzü.
- **Doğrulanmış kaynak** — içtihat/mevzuat daima Yargı Pro + Mevzuat MCP'den; doktrin Literatür/YÖK Tez'den.

---

## Depo yapısı

```
ortak-avukat/
├── .claude-plugin/
│   └── marketplace.json          # marketplace kataloğu
├── plugins/
│   └── ortak-avukat/             # eklentinin kendisi
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── skills/               # 20 skill (çekirdek + 19 oa-*)
│       │   ├── ortak-avukat/     #   çekirdek kimlik + references/anayasa.md
│       │   ├── oa-pipeline/      #   orkestrasyon + tam_tur (working memory) + scriptler
│       │   └── …
│       └── README.md             # eklenti dokümanı + parça kataloğu
├── tests/                        # 300+ pytest (script denetçilerinin regresyonu)
├── README.md                     # bu dosya
├── LICENSE
└── .gitignore
```

Parçaların tam kataloğu, mimari ve anayasal ilkeler için: **[plugins/ortak-avukat/README.md](plugins/ortak-avukat/README.md)**.

---

## Doğrulama (geliştirici)

Depo kökünde:
```bash
python -m pytest tests -q
python plugins/ortak-avukat/skills/oa-usta/scripts/aile_dogrula.py plugins/ortak-avukat/skills
```
İlki script denetçilerinin (300+ test) regresyonunu, ikincisi ailenin yapısal sağlığını (frontmatter, name↔klasör, sürüm tutarlılığı, anılan scriptlerin varlığı) denetler.

---

## Gizlilik

Bu depo **hiçbir müvekkil verisi veya MCP kimlik bilgisi içermez**. Çalışma evrakı (`_oa/`) `.gitignore` ile dışlanmıştır ve asla depoya girmez. Dış araca (bulut MCP/web/e-posta) veri çıkışı, `oa-gizlilik` **Layer 0** süzgecine tabidir (müvekkil verisi, TCKN, sağlık/ceza verisi, UYAP login/e-imza/PIN taranır; fail-closed). UYAP login ve e-imza/PIN adımları münhasıran avukata aittir; sistem bunlar için kod yazmaz.

---

## Fikri Mülkiyet ve Lisans

Bu depodaki tüm içerik — "Ortak Avukat" metodolojisi, skill metinleri, scriptler ve dokümantasyon dâhil — özgün bir eserdir ve **5846 sayılı Fikir ve Sanat Eserleri Kanunu (FSEK)** kapsamında korunur. Eserin sahibi ve tüm **mali ve manevi hakların** münhasır hak sahibi **Av. Bayram Can Çapar**'dır (b.cancapar@gmail.com).

Depo kamuya açık (public) olarak yayımlanmıştır;   Kopyalama, çoğaltma, dağıtma, değiştirme, çeviri, türev çalışma oluşturma ve ticari kullanım **önceden yazılı izne tabidir**. Telif/atıf bildirimleri ve hak sahibinin adı kaldırılamaz. Yalnızca Yargı Pro MCP oluşturan ekibin fikri değişimine ve gerektiğinde ticari amaçla kullanımına izin verilmiştir. 

Tam koşullar: [LICENSE](LICENSE) · Özet bildirim: [NOTICE](NOTICE).

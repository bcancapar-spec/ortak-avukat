# UYAP BELGE FORMATLARI — UDF · TIFF · PDF (operasyonel referans)

> **Kaynak:** Yargı Pro `udf_tiff_pdf_guide` / `yargi-udf-tiff-pdf-guide` skill (rehber sürümü 2026-06-22).
> Bu dosya, o rehberin **operasyonel içeriğini** ailenin kendi diliyle ve kendi konvansiyonlarıyla yeniden
> düzenler; rehberin kendisi Yargı Pro ekibine aittir. Güncel sürüm için daima kaynağa bakılır.
> Aile kuralı: **UDF üretimi bu dosyadaki hatta göre yapılır — başka yol denenmez.**

---

## 0. ALTIN KURAL — UDF ELLE YAZILMAZ

**UDF, yalnız `udf-cli` paketinin üretebildiği/okuyabildiği kapalı bir UYAP formatıdır.**
İçyapısı hakkında varsayımda bulunulmaz; zip + `content.xml` elle kurulmaz; `.udf` elle düzenlenmez.

> **v0.5.5 SAHA KANITI (2026-07-29):** `udf_yaz.py`'nin elle ürettiği `.udf` (yalnız `content.xml` içeren
> zip) **UYAP editöründe açılmadı**. Zip bütünlüğü "OK" görünmesi yanıltıcıdır — format geçerliliği
> demek değildir. Tek geçerli üretim yolu aşağıdaki `html2udf` hattıdır.

---

## 1. HANGİ FORMAT → HANGİ ARAÇ

| Elimizde | Tuzak | Yapılacak |
|---|---|---|
| `.udf` | Ham okuma ikili çöp verir; elle düzenlenmez | `npx -y udf-cli@latest udf2md dosya.udf` |
| `.tiff` / `.tif` | Çok sayfalı TIFF ham okunursa **yalnız İLK sayfa** görünür | `npx -y uyap-tiff-cli@latest tiff2pdf dosya.tiff` → PDF'i oku |
| `.pdf` | Taranmış PDF'te gömülü metin YOKTUR | `npx -y uyap-pdf-cli@latest pdf2md dosya.pdf` (metin + otomatik OCR) |

**Uzantı yalanı:** `.udf` uzantılı ama aslında PDF/DOCX olan dosya `udf2md`'de hata verir — gerçek türüne
göre işlenir.

**Tebligat mazbatası uyarısı:** tebellüğ tarihi çok sayfalı TIFF'in İLK ya da SON sayfasında olabilir;
sayfa kaybı = süre kaybı. (`oa-sure` ile doğrudan ilgili.)

---

## 2. GİRİŞ (login) — bir kez, üçü birden

`udf-cli`, `uyap-tiff-cli`, `uyap-pdf-cli` **giriş kapılıdır**; token `~/.config/yargi/token.json`'da
tutulur, kendini yeniler ve **üç CLI arasında paylaşılır** — bir kez giriş yeter.

- **İnsan varsa (tarayıcılı):** `npx -y udf-cli@latest login` → doğrulama URL'si + kod basar, insan
  onaylayana kadar bekler. Ajan tarayıcı açamıyorsa URL ve kodu **avukata iletir**.
- **Başsız/otomasyon:** tarayıcı akışı sonsuza kadar bekler. Yerine `issue_cli_login_code` MCP aracı
  çağrılır (tek kullanımlık, ~2 dk geçerli kod), sonra `udf-cli login --token <kod>`.
- Durum: `<cli> whoami` · çıkış: `<cli> logout`.

> **AİLE SINIRI (anayasa):** UYAP'ın kendi login/e-imza/PIN adımları **münhasıran avukata aittir**;
> aile bunlar için kod yazmaz. Buradaki giriş, Yargı Pro CLI hesabıdır — UYAP oturumu değildir.

---

## 3. UDF YAZMA — TEK GEÇERLİ HAT

```
İçerik (md/plan) → inline-CSS HTML → npx -y udf-cli@latest html2udf taslak.html cikti.udf
```

- **`md2udf` KULLANILMAZ.** Markdown, UDF'in ihtiyaç duyduğu font/hizalama/girinti/tab/tablo/renk
  denetimlerini taşımaz ve sessizce düşürür. Taslakta bile kullanılmaz.
- Girdi olarak dosya yolu, ham dize veya `-` (stdin) kabul edilir.
- Elde hazır `.docx`/`.pdf` varsa (avukat Word'de yazdıysa): `npx -y docx2udf@latest -input dilekce.docx
  -output dilekce.udf` (giriş kapılı; §5).

### 3.1 UDF-uyumlu HTML yazım şeması

**Tüm uzunluklar `pt`.** Varsayılan (font belirtilmezse): **Times New Roman 12pt**, siyah/beyaz.

| Öge | Kalıp |
|---|---|
| Satır içi | `<strong>`, `<em>`, `<u>`, `<span style="font-family:Arial; font-size:12pt; color:#FF0000; background-color:#FFFF00">` |
| Paragraf | `<p style="text-align:justify; line-height:1.5; margin-top:12pt; margin-bottom:6pt; margin-left:36pt; text-indent:24pt">` |
| Başlık | `<h1>`–`<h6>` → kalın paragraf, 24/20/16/14/12/10pt |
| Tab durakları | `<p style="tab-stops:36pt 72pt 108pt">Kalem<tab/>Değer<tab/>Not</p>` |
| Sayfa sonu | `<page-break/>` — **yalnız avukat açıkça isterse** (editörde "sayfa sonudur" işareti görünür, okur onu metin sanır) |
| Tablo | Standart `<table><tr><td>`; `colspan`/`rowspan`; hücre stili inline CSS; `border-style:none` ile gizli çerçeve |
| Liste | `<ul>`, `<ol>`, `<li>` (iç içe listelerle) |
| Görsel | `<img src="data:image/png;base64,..." width="200" height="100">` (pt) |
| Renk | `#RGB`, `#RRGGBB`, `rgb(r,g,b)`, adlandırılmış CSS renkleri |

### 3.2 Sık hata tablosu

| YANLIŞ | DOĞRU | Neden |
|---|---|---|
| `font-size:14px` | `font-size:14pt` | UDF punto kullanır |
| `&lt;tab/&gt;` | `<tab/>` | Kaçışlanan özel öge düz metne döner |
| `<br><br>` ile paragraf ayırma | İki ayrı `<p>` | UDF blok tabanlıdır; `<br>` paragraf-içi yumuşak satırdır |
| İçerik için `<div>` | `<p>` | `<div>` blok grubu, `<p>` paragraftır |
| `md2udf` | `html2udf` | md, biçimi sessizce düşürür |

### 3.3 Dilekçe kalıpları (hazır reçeteler)

Ortalanmış renkli başlık:
```html
<p style="text-align:center"><span style="font-family:Arial; font-size:18pt; color:#003366"><strong>BAŞLIK</strong></span></p>
```

İki yana yaslı, ilk satır girintili paragraf (dilekçe gövdesi):
```html
<p style="text-align:justify; text-indent:24pt; line-height:1.5">Somut olayda ...</p>
```

Asılı girinti (taraf/vekil künye satırı):
```html
<p style="margin-left:36pt; text-indent:-36pt">DAVALI<tab/>: Ad Soyad, T.C. …, adres</p>
```

Tab duraklı imza bloğu:
```html
<p style="tab-stops:200pt 400pt"><strong>Davacı</strong><tab/><strong>Davalı</strong><tab/><strong>Hâkim</strong></p>
```

Kalın başlıklı çerçeveli tablo, birleşik hücre (`colspan`/`rowspan`) ve çerçevesiz yerleşim tablosu
(`border-style:none`) rehberdeki kalıplarla aynıdır.

---

## 4. UDF OKUMA

```bash
npx -y udf-cli@latest udf2md dosya.udf     # ajan-dostu: doğrudan stdout'tan oku
npx -y udf-cli@latest udf2html dosya.udf   # karmaşık biçim incelemesi için
```

Kurallar: ham `.udf`'i `.md`/`.html` olarak diske yazma — dönüştürülmüş içeriği oku. Çok belgede
`00-INDEX.md` sırasını izle, dosya başına bir çağrı. Hata verirse dosya gerçek UDF olmayabilir.

---

## 5. MEVCUT DOCX/PDF → UDF (`docx2udf`)

```bash
npx -y docx2udf@latest -input dilekce.docx -output dilekce.udf
npx -y docx2udf@latest -input karar.pdf          # -output verilmezse .udf uzantısıyla aynı yola yazar
```

- Daima `-y` (npx'in etkileşimli sorusu bloklamasın).
- Başarı ölçütü: **çıkış kodu + `-output` dosyasının varlığı** — stdout/stderr metni ayrıştırılmaz.
- Çıktıdaki `---Sayfa Sonu---` satırları **belge metni değildir**, sayfa kesme işaretidir; özetlerken
  ve alıntılarken yok sayılır.

| Çıkış | Anlam | Yapılacak |
|---|---|---|
| 0 | Başarı | `-output` dosyasını kullan |
| 1 | Dönüştürme/girdi hatası | stderr'i oku, girdiyi düzelt |
| 2 | Giriş gerekli | login akışı, sonra tekrar |
| 3 | Hesap yasaklı | Dur, avukata bildir |
| 4 | Sunucuya erişilemiyor | Geçici, sonra dene |
| 5 | Aylık kota bitti | Avukata bildir |

---

## 6. TIFF VE PDF OKUMA (aile notu)

Rehberin önerdiği hat: `uyap-tiff-cli tiff2pdf` ve `uyap-pdf-cli pdf2md` (giriş kapılı, ağ gerektirir,
yerel Türkçe OCR'a otomatik düşer).

**Ailenin varsayılanı `oa-ingest`'tir** (PyMuPDF + yerel Tesseract, çevrimdışı, paralel, önbellekli,
kayıpsızlık damgalı) — 214 evraklık külliyatta 0 kayıpla doğrulanmıştır. Rehber hattı **yedek**tir:
- `oa-ingest` bir evrağı çözemez / OCR boş dönerse (OCR-BOŞ damgası),
- ya da çok sayfalı TIFF'te sayfa kaybı şüphesi varsa,
`tiff2pdf` / `pdf2md` ile ikinci bir okuma denenir ve sonuç **ayrı damgayla** künyeye işlenir.
Sessiz atlama yasağı burada da geçerlidir.

---

## 7. TESLİM HATTI (aile sözleşmesi)

```
08-dilekce-*.md  →  (inline-CSS HTML)  →  html2udf  →  <ad>.udf
                                                   └→  (istenirse) PDF önizleme
```
- UDF üretimi **teslim olayıdır**: üretilmeden önce içtihat-muhakeme ve künye-teyit denetimleri koşar,
  sonuç `<udf-adı>.denetim.txt` olarak yanına yazılır ve `_oa/DURUM.md`'ye işlenir (bkz. teslim makbuzu).
- Üretilen `.udf` **avukat tarafından UYAP editöründe açılarak** teyit edilir — makine bu adımı
  doğrulayamaz; "üretildi" ≠ "açılıyor".
- Temizlik: ara HTML/PNG/PDF gibi çalışma dosyaları `_oa/cikti/` kökünü kirletmez.

---

## 8. TUZAK ÖZETİ

1. **UDF elle yazılmaz/düzenlenmez** — yalnız `udf-cli`. (Zip "OK" görünmesi geçerlilik değildir.)
2. **Çok sayfalı TIFF ilk sayfa dışında her şeyi gizler** — tebellüğ tarihi son sayfada olabilir.
3. **Taranmış PDF'te metin yoktur** — OCR'sız okuma boş döner.
4. **Yazarken:** hep `pt`; `<tab/>` ve `<page-break/>` kaçışlanmaz; paragraf `<p>` ile; sayfa sonu yalnız
   istenirse; **her zaman `html2udf`, asla `md2udf`**.
5. **Çalışma dosyalarını temizle.**

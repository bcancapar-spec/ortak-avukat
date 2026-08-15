# UDF İÇ YAPISI — XML tabanı, kanonik yazım ve yerel motor sınırı (v0.5.7)

> © 2026 Av. Bayram Can Çapar — FSEK. Kaynaklar: Yargı UDF/TIFF/PDF rehberi
> (2026-06-22 sürümü, `udf_tiff_pdf_guide`) + Denizli 754 sahasında gerçek
> `.udf` dosyalarının bayt-düzeyi incelemesi (her iki üretim yolunun çıktısı
> mekanik kapı + resmî okuyucu round-trip'iyle doğrulandı).

## 1. Dosya anatomisi — UDF bir ZIP içinde tek XML'dir

```
dilekce.udf  (ZIP arşivi)
└── content.xml          ← belgenin tamamı; UTF-8 XML
    ├── <template format_id="1.8">        kök (bilinen: 1.6/1.7/1.8)
    ├── <content><![CDATA[ TÜM METİN ]]>  düz metin TEK blokta
    ├── <properties><pageFormat …/>       kenar boşlukları/kâğıt (70.866 = 2,5cm)
    ├── <elements resolver="hvl-default" name="hvl-default">
    │     <paragraph Alignment="N">       0=sol 1=orta 2=sağ 3=iki-yana
    │       <content startOffset="S" length="L" [bold="true"]/>
    │     …                               offset'ler CDATA'yı BOŞLUKSUZ döşer
    └── <styles><style name="default" family="Times New Roman" size="12"…/>
```

- **Biçim, metinden AYRI yaşar:** görünür metin CDATA'da; hiza/kalınlık,
  `elements` altında offset aralıklarıyla metne İŞARET eder. Bu, UYAP
  editörünün (Java/Swing) belge modelidir.
- **Offset birimi UTF-16 code unit'tir** (Swing). Python'un code-point
  sayımı BMP-dışı karakterde (emoji) kayar → tek emoji, sonraki TÜM
  hizaları bozar. Dilekçede emoji zaten kullanılmaz; motorlar yine de
  UTF-16 sayar.
- E-imza, arşive `sign.sgn`/`.p7s` (PKCS#7) olarak eklenir; içerik XML'i
  değişmez. İmzalı nüshaya DOKUNULMAZ.

## 2. Kanonik yazım yolu (VARSAYILAN — değişmedi)

`md → UDF-HTML (md_udf_html.py) → npx -y udf-cli@latest html2udf → GEÇERLİLİK KAPISI`

Rehber kuralları (birebir): uzunluklar **pt** (px asla); `<tab/>` ve
`<page-break/>` kaçırılmaz (escape edilirse düz metin olur); paragraf ayrımı
`<br>` değil YENİ `<p>`; sayfa sonu yalnız açık istekle. `html2udf` ağ +
oturum ister (`npx -y udf-cli@latest login`, jeton `~/.config/yargi/token.json`,
üç yargı CLI'ı paylaşır); yoksa hat FAIL-CLOSED durur — bozuk-ama-üretildi,
dürüst engelden kötüdür (B5).

## 3. Yerel motor — EMEKLİ (v0.5.8.4; riskli bayrak istisnası)

**372 sahası A/B hükmü (ders 10-D):** yerel motorun ürettiği UDF'ler UYAP
editöründe AÇILMADI (7 dosya karantina). A/B testi python re-zip'ini ve
pageFormat kenar yamasını AKLADI — suçlu `content.xml`'in kendisidir: yerel
motor `<elements resolver="hvl-default">` yazar ama `<styles>` bloğunda
`name="hvl-default"` STİL TANIMI vermez (açılan gerçek üretici çıktısında
tanım VAR). Bu imza artık `udf_dogrula`'da GEÇERSİZLİK sebebidir.

Sonuç: `--yerel-motor` **HATA verir** (emekli). Çevrimdışı üretim yalnız
`--yerel-motor-riskli` (bilinçli risk) ile koşar; çıktı resmî okuyucu
(`udf2md`) ile doğrulanamazsa yanına `<ad>.DOGRULANMADI` işaret dosyası düşer
— işaretli dosya YÜKLENMEZ. Sınırlar dürüstçe:

| | html2udf (kanonik) | yerel motor (`--yerel-motor-riskli`) |
|---|---|---|
| Ağ/oturum | gerekir | gerekmez (resmî okuyucu bacağı denenir) |
| Zengin biçim (tablo, renk, tab-stop) | tam | YOK — paragraf + başlık kalın/orta |
| UYAP editör uyumu | resmî yazıcı | **372'de AÇILMADI — garanti YOK** |
| Doğrulanamazsa | FAIL-CLOSED | `<ad>.DOGRULANMADI` işareti (yükleme yasağı) |
| Son söz | yine avukat | **UYAP editöründe görsel teyit ZORUNLU** |

## 4. Geçerlilik kapısının bacakları (`udf_dogrula`)

1. ZIP açılır + `content.xml` var; 2. XML iyi biçimli; 3. CDATA bulunur;
3.5. **`hvl-default` STİL TANIMI** (v0.5.8.4): `<styles>` bloğunda
`name="hvl-default"` taşıyan bir `<style>` etiketi yoksa dosya GEÇERSİZDİR
(elle-üretim imzası — `<elements ... name="hvl-default">` bu denetimi
SAĞLAMAZ, ölçüt tam olarak `<style>` etiketidir);
4. offset/length aralıkları CDATA'yı boşluksuz ve taşmasız döşer (tüm
`startOffset` taşıyan elementler — yalnız `<content>` değil; `<tab/>` da
sayılır); 5. resmî okuyucu tanığı (`npx udf2md` exit 0 + metin döner).
Beşinci bacak ağ ister; öncekiler çevrimdışıdır. Mekanik GEÇERLİ ≠ görsel
kusursuz — nihai göz avukatındır.

**Üretim makbuzu (v0.5.8.4):** her `.udf` üretimi, dava klasöründe defter
varsa `_oa/defter/udf-uretim-makbuz.jsonl`'e tek satır iz düşer (motor,
sha256, doğrulama durumu) — üretim noktasında yazılır, kapı değildir.

## 5. Okuma yönü (hatırlatma)

`.udf` ASLA ham okunmaz: `npx -y udf-cli@latest udf2md`. Ağsız iç hat için
`udf_metin.py` yalnız CDATA metnini çeker (biçim bilgisi vermez). Çok
sayfalı TIFF ve taranmış PDF tuzakları için rehberin B/C bölümleri geçerlidir.

## 6. SAHA STANDARDI — e-imzalı gerçek nüshadan ölçülen yazım metrikleri (v0.5.7.2)

Avukatın UYAP editöründe hazırlayıp e-imzalayarak FİİLEN SUNDUĞU bir dilekçe
nüshası bayt düzeyinde ölçüldü (kimlik m.7 gereği anonim; `sign.sgn` mevcuttu
ve mekanik kapımız dosyayı GEÇERLİ saydı — gerçek-dünya çapraz doğrulaması).
Ölçülen standart, iki motorun da varsayılanıdır:

| Öğe | Değer |
|---|---|
| Kenar boşlukları (pt) | sol **42.52** (1,5cm) · sağ **28.35** (1cm) · üst/alt **14.17** (0,5cm) |
| Gövde paragrafı | iki yana yaslı · `FirstLineIndent=24` · `SpaceBelow=6` · `LineSpacing=0.3` |
| Yazı | Times New Roman 12 — her content span'ında AÇIKÇA (yalnız styles'a bırakılmaz) |
| Etiket blokları (DAVACI/VEKİLİ…) | asılı girinti: `LeftIndent=110 + FirstLineIndent=-110 + TabSet=110` + gerçek TAB |
| Başlık | ortalı + bold; alt listeler `LeftIndent=24/36` |
| Footer | sayfa numarası (Arial 11) — editör ekler; motorlarımız üretmez |
| Vurgu | bold ~%35 span, italik alıntılarda |

Kanonik HTML karşılığı (md_udf_html `JUST`):
`text-align:justify; text-indent:24pt; line-height:1.3; margin-bottom:6pt`.
Etiket blokları için HTML deseni: `tab-stops:110pt` + `<tab/>` (rehber A.3).

## §6-v2 — ŞEKİL STANDARDI v2 (v0.5.8.3; Can emri + Yönetmelik No. 2646)

Dayanak: **Resmî Yazışmalarda Uygulanacak Usul ve Esaslar Hakkında Yönetmelik**
(CB Yönetmeliği No. 2646, RG 10.06.2020) — m.7 (TNR 12 punto esas; gerekli
hâllerde küçültme) ve m.8 (yazı alanı: kenarlardan 1,5 cm boşluk).

| Öğe | Değer | Kaynak |
|---|---|---|
| Sayfa kenarları (4 yön) | **42.52 pt = 1,5 cm** | Yönetmelik m.8 (alt kenar simetriyle) |
| Gövde | Times New Roman **12 pt**, yaslı, FirstLineIndent 24 | Yönetmelik m.7 + saha nüshası |
| **Satır aralığı** | **1,5** (HTML `line-height:1.5`; yerel motor `LineSpacing="0.5"`) | Can emri (dilekçe geleneği) |
| **Karar/emsal linkleri** | Parantez içinde, **11 pt** (gövdeden 1 punto küçük) | Can emri; m.7 küçültme cevazı |
| Üretim yolu | md → md_udf_html → html2udf → `_sayfa_kenari_yonetmelik` yaması → çift kapı | — |

Not: html2udf importer'ının varsayılan kenarları dardır; kenar yaması içerik
değil BİÇİM düzeltmesidir ve ardından udf_dogrula + resmî okuyucu yeniden koşar.
Eski §6 ölçümü (sol 42.52 / sağ 28.35 / üst-alt 14.17 / LineSpacing 0.3) tarihi
kayıt olarak durur; üretim standardı artık §6-v2'dir.

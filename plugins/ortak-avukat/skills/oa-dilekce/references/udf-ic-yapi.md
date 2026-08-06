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

## 3. Yerel motor v2 (`--yerel-motor`) — çevrimdışı yedek, sınırı net

Barındırılan oturuma erişilemeyen durum için (v0.5.7): §1'deki yapıyı
doğrudan üretir; çıktı mekanik kapıdan GEÇMEK ZORUNDADIR (geçmezse dosya
silinir). Sınırlar dürüstçe:

| | html2udf (kanonik) | yerel motor v2 |
|---|---|---|
| Ağ/oturum | gerekir | gerekmez |
| Zengin biçim (tablo, renk, tab-stop) | tam | YOK — paragraf + başlık kalın/orta |
| UYAP editör uyumu | resmî yazıcı | saha-kanıtlı ama GARANTİSİZ |
| Son söz | yine avukat | **UYAP editöründe görsel teyit ZORUNLU** |

## 4. Geçerlilik kapısının beş bacağı (`udf_dogrula`)

1. ZIP açılır + `content.xml` var; 2. XML iyi biçimli; 3. CDATA bulunur;
4. offset/length aralıkları CDATA'yı boşluksuz ve taşmasız döşer (tüm
`startOffset` taşıyan elementler — yalnız `<content>` değil; `<tab/>` da
sayılır); 5. resmî okuyucu tanığı (`npx udf2md` exit 0 + metin döner).
Beşinci bacak ağ ister; ilk dördü çevrimdışıdır. Mekanik GEÇERLİ ≠ görsel
kusursuz — nihai göz avukatındır.

## 5. Okuma yönü (hatırlatma)

`.udf` ASLA ham okunmaz: `npx -y udf-cli@latest udf2md`. Ağsız iç hat için
`udf_metin.py` yalnız CDATA metnini çeker (biçim bilgisi vermez). Çok
sayfalı TIFF ve taranmış PDF tuzakları için rehberin B/C bölümleri geçerlidir.

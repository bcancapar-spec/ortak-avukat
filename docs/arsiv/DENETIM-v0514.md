# DENETİMİN İNFAZI — v0.5.14

> Bu belge, 30-31 Ağustos 2026 denetimlerinde bulunan **62 kusurun** nasıl
> kapatıldığını kayda geçirir. Denetim ve infaz ayrı ellerde yürüdü: bulguları
> uzman ajanlar üretti, **tek bir entegratör** (ana ajan) hepsini satır satır
> denetleyip birleştirdi ve yayına aldı. Hiçbir alt ajan depoya commit atmadı.

## Yöntem

**Tur 1 — şema planı (30 Ağustos).** v0.5.13'te ertelenen dört tez kod üzerinde
planlandı; her plan bir **adversarial çürütücüye** verildi. Çürütücüler
planların kendi ölümcül kusurlarını buldu: kıyas için önerilen muafiyet
**fail-open** çıktı (model tek kelime yazarak yeşil hüküm satın alabilirdi);
önerilen bir testin dayandığı iddia doğduğu gün kırmızı olacaktı.

**Tur 2 — çelişki ve kırık avı (31 Ağustos).** Eklentiyi **fiilen çağıran**
5 hukukçu ve scriptleri **fiilen koşturan** 4 mühendis avcı. Her avcının
bulguları bağımsız bir şüpheciye verildi; şüphecinin varsayılanı *"bu bulgu
yanlıştır"* idi ve dosyayı kendisi açıp komutu kendisi koşturdu. Şişirilmiş
ciddiyetler düşürüldü, çürüyen bulgular rapordan çıkarıldı.

**Norm teyidi.** Hiçbir hukuki düzeltme hafızadan yazılmadı. Ayrıca 21 süre
kuralının tamamı ayrı bir teyit ajanına madde metniyle doğrulatıldı —
27 Ağustos'ta bir hakem heyeti bu adım atlandığı için eski hukuka dayanıp
doğru bir metni "hata" sanmıştı.

## Telafisiz üçlü

| # | Kusur | Neden telafisiz |
|---|---|---|
| **A-1** | Ceza kanun yolu sürelerine **HMK m.104** adli tatil rejimi uygulanıyordu (bir hafta); doğrusu **CMK m.331/4** (üç gün) | Sistem **dört gün geç** tarih veriyordu. 4-7 Eylül'de verilen istinaf/temyiz/itiraz süreden reddedilir, hüküm kesinleşir. Tutuklu dosyada özgürlük kaybı |
| **A-2** | Savunma kontrol listesinde CMK m.268 itiraz süresi hâlâ "yedi gün" | Süre **olduğundan kısa** görünüyordu: müdafi fiilen açık bir kanun yolundan vazgeçebilirdi. v0.5.13'te SKILL.md düzeltilmiş, **referans dosyası atlanmıştı** — ikiz liste kayması |
| **B-15** | Layer 0'daki IBAN deseninin hane sayısı yanlış | MUTLAK_DENY kuralı **geçerli hiçbir Türk IBAN'ında ateşleyemiyordu** — müvekkil hesap bilgisi dış araca sızabilirdi |

## Halüsinasyon panzehirinin onarımı

Sistemin varlık sebebi, kaynağı doğrulanmamış içtihadın dilekçeye girmesini
engellemektir. Denetim bu hattın iki yerinden delik olduğunu gösterdi:

- **B-2 —** künye/atıf kapısı yaygın künye biçimlerini görmüyordu; uydurma
  içtihat taşıyan bir taslak uçtan uca **"TESLİME HAZIR"** alabiliyordu.
  Artık ayrıştırılamayan atıfta kapı **fail-closed**; AYM ve AİHM künye
  biçimleri dahil regresyon vaka seti kilitlendi.
- **B-3 —** kaynakça üreteci, kapının göremediği künye için dilekçenin içine
  **"tam metniyle okundu"** diye gerçeğe aykırı beyan yazıyordu. Bir belgeye
  yalan yazmaktır. Teyitsiz tek künye varsa bu cümle **hiç yazılmıyor**;
  yerine teyidin yapılmadığı açıkça belirtiliyor. Künye çıkarımı tek kaynağa
  indirildi (iki ayrı ayrıştırıcı ayrışamaz artık).

## Diğer P0'lar

- **A-3 —** *yürütmenin durdurulması* (İYUK m.27) ailenin **tamamında yoktu**
  (aile geneli arama: sıfır satır). Ödeme emri bir **tahsilat** işlemidir ve
  dava açmak tahsilatı durdurmaz; sistem bunu hiçbir yerde söylemiyordu.
  Kural (`iyuk_yd_itiraz`, m.27/7), çizelge blokları, Kapı Kataloğu satırı ve
  ödeme emri şablonundaki YD kavşağı eklendi.
- **B-1 —** servis edilen araç nesli ile denetlenen nesil ayrıydı; `hook_doktor`
  iki kipte de yeşil basıyordu. Üç kez nükseden bayat-araç arızasının denetim
  körlüğü buydu.
- **B-4 —** sunum kilidi, oturum dava klasörü dışındayken sessizce ölüydü
  (kök keşfi `file_path` okuyordu, gönderim ise `files` listesi veriyordu).
- **B-5 —** bayat-araç nöbetçisi **negatif** parmak izine dayanıyordu: gerçekten
  bayat bir kit "kanaldan YENİ, tazeleme gerekmez" ilan ediliyordu.
- **B-13/B-14 —** mühürsüz-teslim taraması fail-open'dı; `.docx` teslim sınıfı
  sayılıyor ama hiçbir mühür taramasına girmiyordu.
- **B-18 —** `teslim_paketi` girdisini mutasyona uğratıyordu: aynı komut
  birinci koşuda yeşil, ikincisinde kırmızı veriyordu.

## Yapısal onarımlar

- **Kural tablosu tek kaynağa indi.** JSON asıldır; gömülü fallback ondan
  **türetilir** ve ayrışmayı bir test mekanik olarak yakalar. Bu tur, testin
  ilk avı **entegratörün kendi kayması** oldu: JSON'u güncelleyip fallback'i
  unutmuştum, kapı beni durdurdu.
- **21/21 süre kuralı MCP teyitli** — teyitsiz kural sıfır. Teyit sırasında üç
  kritik şerh çıktı ve çizelgeye işlendi: İİK m.363'te 7499 s.K. **"tefhim"
  ibaresini kaldırmış** (süre artık yalnız tebliğle işler); İYUK m.46 temyiz
  **kapsamı 31/7/2026'da genişlemiş**; İYUK m.7'nin 60 günü ise **değişmemiş**
  (7331'in "60→30" değişikliği m.10/11/13'tedir — sık karıştırılan bir tuzak).
- **Süit sayısı iddiası tek işaretçiye indi**; üç ayrı belgede üç ayrı yanlış
  sayı yazıyordu.
- **Amme ödeme emri şablonu** eklendi — "sebepler sınırlıdır" mutlaklığını
  kıran dört hat (tebliğ, yokluk, şekil, tahakkuk) ve İİK ödeme emriyle
  karıştırma uyarısıyla.

## Entegratör hükümleri (çatışma çözümleri)

**Sunum kilidi ↔ gürültü disiplini.** Yeni "doğrulayamadım" uyarısı, v0.5.9'un
*"dava dışı klasörde sessiz kal"* sözleşmesiyle çarpıştı. İkisi de meşru
ilkedir. Ayrım şöyle konuldu: **diskte olmayan** bir yol için denetlenecek bir
şey yoktur — orada susmak gürültü disiplinidir, sessiz ölüm değil. Uyarı
yalnız **var olan** bir teslim ürününün kökü bulunamadığında çıkar.

**Kural ↔ yargı kolu uyuşmazlığında durdurma.** Ceza kuralı hukuk koluyla
koşulduğunda uyarıp devam etmek yerine **hesap durdurulur**. Gerekçe: uyarı
basıp devam etmek yanlış son günü ekranda bırakır ve `--kok` verildiğinde onu
deftere **otomatik** yazar; defterde düzeltme yolu yoktur, yani sessiz yanlış
kalıcılaşırdı.

## Kapsam dışı kalan, kayda geçen

- **HMK m.107 (belirsiz alacak davası) 7589 s.K. ile ilga edildi** (31/7/2026);
  derdest davalar için geçici madde saklı. Ailede bu kuruma hiç atıf olmadığı
  doğrulandı — bayat atıf riski yok, ama iş hukuku tarafında ayrıca ele alınacak.
- Parasal kesinlik eşikleri kanun metnindeki **taban** değerlerdir ve her yıl
  yeniden değerlemeyle artar; ayrıca bir kısmı AYM kararlarıyla kısmen iptal
  edilmiştir. Bu yüzden hiçbir eşik rakamı sisteme sabit yazılmadı.

## Sayılar

62 bulgu · 8 uzman ajan + 9 avcı + 9 şüpheci + 1 teyit ajanı · süit
**1406 → 1688** · dört sürüm damgası birlikte arttı · CI yeşermeden etiket yok.

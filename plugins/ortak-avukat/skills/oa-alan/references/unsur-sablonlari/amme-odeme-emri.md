# Unsur Şablonu — Ödeme Emrine Karşı Dava (6183 m.58) · T10, v0.5.14

Norm çıpası: 6183 sayılı Amme Alacaklarının Tahsil Usulü Hakkında Kanun m.55 vd.
(ödeme emri) ve m.58 (ödeme emrine karşı dava); usul rejimi 2577 sayılı İYUK.
**Kullanım anında** güncel metin/yürürlük Mevzuat MCP'den, ilgili içtihat
`oa-ictihat`'tan teyit edilir — aşağıdaki madde numaraları başlangıç
ÇIPASIDIR, hafızadan kesinlenmez. **Süre ve oran rakamı bu şablona yazılmaz**;
süre `oa-sure` ile hesaplanır (kural adı: `amme_6183_m58`).

> **AD KARIŞIKLIĞI UYARISI (kritik).** Bu şablon **amme (kamu) alacağının**
> ödeme emrine ilişkindir. Aynı klasördeki `itirazin-iptali.md` şablonunun U1
> kalemi de "ödeme emri" der ama o **İİK** m.58-60 anlamında, **özel hukuk**
> takibinin ödeme emridir. İki kurum aynı adı taşır, rejimleri ayrıdır:
> biri idari yargıda dava, diğeri icra dairesine itiraz. Dosya tipini
> karıştırmak yanlış merci ve telafisiz süre kaybı üretir.

## Unsur tablosu

| Unsur (id önerisi) | Norm çıpası | Delil türü | İspat yükü |
|---|---|---|---|
| U1 — Ortada usulüne uygun **tebliğ** edilmiş bir ödeme emri var mı; tebliğ tarihi nedir | 6183 m.55; tebliğ rejimi (vergi alacaklarında VUK, diğerlerinde ilgili tebligat rejimi — kullanım anında teyit) | Ödeme emri aslı, tebliğ alındısı/mazbatası, e-tebliğ kaydı | İdare (tebliğin usulüne uygunluğu) |
| U2 — Ödeme emrinin **şekil** unsurları tam mı (alacağın nev'i, miktarı, dayanağı, ödeme yeri ve süresi, itiraz yolu ve mercii bildirimi) | 6183 m.55; yasa yolu bildirimi yönünden AY m.40/2 | Ödeme emri metninin kendisi | Davacı ileri sürer; belge dosyada |
| U3 — Dayanak amme alacağı **tahakkuk** etmiş ve kesinleşmiş mi (tahakkuk etmemiş alacak için ödeme emri düzenlenemez) | 6183 m.37, m.54-55; tarhiyat rejimi ilgili vergi kanunu | Tahakkuk fişi, ihbarname, kesinleşme yazısı, dava/kanun yolu kayıtları | İdare (tahakkukun varlığı) |
| U4 — **Borcum yoktur** — alacak hiç doğmamış, ödenmiş, terkin edilmiş, mahsup edilmiş ya da başka sebeple sona ermiş mi | 6183 m.58 (dava sebepleri) | Ödeme makbuzu, mahsup dilekçesi ve kabulü, terkin kararı, banka kaydı | Davacı |
| U5 — **Kısmen borçluyum** — miktarın hangi kısmına, hangi kalem yönünden itiraz edildiği açıkça gösterilmiş mi | 6183 m.58 | Hesap dökümü, kalem bazlı karşılaştırma tablosu, bilirkişi | Davacı (itiraz ettiği kısım yönünden) |
| U6 — **Zamanaşımı** — tahsil zamanaşımı dolmuş mu; kesen/durduran sebepler var mı | 6183 m.102-104 (tahsil zamanaşımı; kesen ve durduran hâller) | Takip dosyası safahatı, ödeme/haciz/aciz kayıtları, zamanaşımını kesen işlem tarihleri | Davacı ileri sürer; kesen işlemi idare ispatlar |
| U7 — İşlem **yok hükmünde** sayılacak ağırlıkta bir sakatlık taşıyor mu (borçlu olmayan kişiye, ölü kişiye, hiç var olmayan alacağa dayanan ödeme emri) | İdari işlemin yokluğu teorisi; 6183 m.55 | Nüfus/ticaret sicil kaydı, ilişik kesme belgesi, kimlik/unvan uyuşmazlığı | Davacı |
| U8 — Muhatap doğru mu — asıl borçlu, mirasçı, kanuni temsilci veya ortak sıfatı doğru kurulmuş mu | 6183 m.35 (limited şirket ortağı), mük. m.35 (kanuni temsilci); TMK mirasçılık hükümleri | Ticaret sicil kaydı, imza sirküleri, görev/atama kararları, mirasçılık belgesi | İdare (sıfatın kuruluşu) |
| U9 — Davanın **süresinde** açılmış olması | 6183 m.58; süre `oa-sure` ile hesaplanır (`--kural amme_6183_m58`) | Tebliğ tarihi ile dava tarihinin karşılaştırılması | Mahkemece resen gözetilir |
| U10 — Görevli ve yetkili yargı yeri doğru mu (alacağın türüne göre vergi mahkemesi / idare mahkemesi ayrımı) | 2577 İYUK; 2576 sayılı Kanun görev hükümleri | Ödeme emrindeki alacak nev'i, tahsil dairesi | Mahkemece resen gözetilir |

## Budanmayacak dört hat — "sebepler sınırlıdır" MUTLAK DEĞİLDİR

6183 m.58'in saydığı üç sebep (borcum yoktur · kısmen borçluyum · zamanaşımı)
dilekçenin **çekirdeğidir**, ama bu sınırlılık aşağıdaki dört hattı kesmez.
Bu hatlar dosyayı kazandıran savunmalardır ve şablon eliyle budanmaz:

1. **Tebliğ hattı (U1):** usulsüz tebliğ, tebliğin hiç yapılmamış olması,
   yanlış adrese/kişiye tebliğ. Tebliğ yoksa süre de işlemez.
2. **Yok hükmünde işlem hattı (U7):** işlemin yokluğu her zaman ileri
   sürülebilir; sebep sınırlaması bir yokluk iddiasını kapatmaz.
3. **Şekil hattı (U2):** ödeme emrinin zorunlu unsurları eksikse işlem
   sakattır; yasa yolu/mercii bildirilmemişse AY m.40/2 ayrıca gündeme gelir.
4. **Tahakkuk hattı (U3):** tahakkuk etmemiş, kesinleşmemiş ya da dava
   nedeniyle tahsili durmuş bir alacak için ödeme emri düzenlenemez.

**Yanlış cephede savaş uyarısı.** Ödeme emrine karşı davada **tarhiyatın
esası** kural olarak tartışılmaz — o tartışmanın yeri tarhiyata karşı açılan
davadır. Esasa girip kaybetmek, hem doğru hattı harcar hem sonucu ağırlaştırır.
İstisnalar (tahakkuk etmemiş alacak, yokluk hâli) yukarıdaki dört hatta
düşer; hangi cephede olduğun dilekçenin ilk paragrafında kararlaştırılır.

## Yürütmenin durdurulması kavşağı — "dava açtım, tahsilat durdu" YANILGISI

**Dava açıldı diye tahsilat kendiliğinden durmaz.** İYUK m.27/1 dava
açılmasının yürütmeyi durdurmayacağını söyler; **İYUK m.27/4** ise tahsilat
işlemlerinden dolayı açılan davaların tahsil işlemini durdurmadığını, bunlar
hakkında ayrıca **yürütmenin durdurulması** istenebileceğini söyler.
Ödeme emri bir **tahsilat** işlemidir — dolayısıyla YD talep edilmezse dava
sürerken **e-haciz**, banka bloke ve satış işlemleri yürür. Müvekkile
"dava açtık, rahat olun" denmesi bu yüzden yanlıştır; bilgilendirme dosyanın
gerçek durumunu yansıtmalıdır (bu bir tavsiyedir, mekanik denetim değildir).

**Nöbet kalemi — YD isteminin reddi.** YD istemi hakkındaki karara karşı
itiraz süresi **İYUK m.27/7**'de düzenlenmiştir ve bir defaya mahsustur.
Ret kararı **tebliğ edildiği anda**, tarihi bilinen bir süre başlar; o an
süre nöbetine yazılır (olay gerçekleşmeden pencere açılmaz):

```bash
python hesapla_sure.py --teblig <YYYY-AA-GG> --kural iyuk_yd_itiraz \
  --yargi idari --kok . --aciklama "YD isteminin reddine itiraz (İYUK m.27/7)"
```

Şerh: ivedi yargılama (İYUK m.20/A) ve merkezî sınav (m.20/B) usullerinde
YD kararına **itiraz edilemez** — bu dosyalarda nöbet satırı açılmaz.
Aynı sebeplere dayanarak ikinci kez YD istenemez (m.27/10).

## TEYİT LİSTESİ — kullanım anında Mevzuat MCP'den doğrulanacaklar

- **6183 m.55** — ödeme emrinin içeriği ve zorunlu unsurları.
- **6183 m.58** — dava sebepleri, süre, mercii ve ret hâlindeki sonuçlar.
  *Şerh:* bu maddenin **haksız çıkma zammına** ilişkin fıkrası **Anayasa
  Mahkemesince iptal edilmiştir** ve yerine hüküm konmamıştır — yürürlükte
  olmayan bir yaptırım müvekkile caydırıcı olarak anlatılamaz, karşı tarafa
  tehdit olarak yazılırsa dilekçe çürütülür.
- **6183 m.35 ve mük. m.35** — ortak ve kanuni temsilci sorumluluğu (sık değişen).
- **6183 m.102-104** — tahsil zamanaşımı, kesen ve durduran hâller.
- **2577 (İYUK) m.27** — özellikle f.1, f.4, f.7 ve f.10.
- **2577 m.7** — dava açma süresi rejimi (özel kanun süresi saklı).
- Görev/yetki: 2576 sayılı Kanun ve İYUK hükümleri.

## Antitez çapası (M3 köprüsü)

İdarenin en olası savunmaları: (a) davanın süresinde açılmadığı, (b) ileri
sürülen sebebin m.58 kapsamı dışında kaldığı (esasa girildiği), (c) tebliğin
usulüne uygun olduğu, (d) zamanaşımının kesildiği. `oa-antitez` matrisinde
"usul" (süre, kapsam) ve "ispat_delil" (tebliğ, kesen işlem) cepheleri bu
unsurlarla eşlenir; her cephe ya çürütülür ya işaretli artık risk olarak kalır.

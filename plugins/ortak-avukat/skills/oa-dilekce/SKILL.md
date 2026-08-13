---
name: oa-dilekce
description: >-
  Ortak Avukat sisteminin DİLEKÇE/SÖZLEŞME YAZIM parçası. Türk hukukunda dava,
  cevap, istinaf, temyiz dilekçesi; AYM bireysel başvuru; yemin teklif dilekçesi;
  idari kanal başvuru dilekçesi; sözleşme tahriri (boşanma protokolü, adi ortaklık);
  hukuki mütalaa yazımında DEVREYE GİR. Her tip için zorunlu unsurları ve sık atlanan
  alanları (tebliğ tarihi, ihtirazi kayıt, harç, ihlal eksenleri) playbook olarak
  uygula. Kullanıcı bir dilekçe/sözleşme/mütalaa istediğinde — tip adını anmasa bile —
  tetikle. Bağımsız çalışır; `oa-sure` (süre satırı), `oa-ictihat` (teyitli atıf) ve
  `oa-kontrol` (teslim öncesi denetim) ile takım oynar.
---

# oa-dilekce — Dilekçe ve Sözleşme Playbook'ları

Sök-tak parça. Her tip için **zorunlu unsurlar** (eksikse usulden ret/iade) ve **sık atlanan alanlar** (en çok hata yapılan yer). Madde numaraları başlangıç çıpasıdır; usul kuralı kullanım anında `oa-ictihat` üzerinden teyit edilir. **Bu, zincirin son/çıktı aşamasıdır:** interview → alan → içtihat → antitez halkalarının ürünü burada belgeye dönüşür.

## Yazar sistemi ve lafzı — esas kural
Bu parça `ortak-avukat` ailesinin yazım çıktısıdır ve ailenin tasarımcısı **Av. Bayram Can Çapar**'ın dilekçe sistemine bağlıdır. **Çapar tarafından yazılan/yazılacak dilekçelerde onun kendi sistemine ve lafzına (üslup, dizilim, ifade tarzı, başlıklandırma, terim tercihi) uymak ESAS kuraldır** — jenerik bir şablon dayatılmaz, mevcut üslubu korunur ve sürdürülür. Eldeki bir Çapar dilekçesi örnek/şablon olarak verildiğinde: önce onun yapısal düzeni ve lafzı çıkarılır, sonra yeni dilekçe **o lafza sadık** üretilir. Aşağıdaki ortak omurga ve tip playbook'ları bu lafzın *üzerine oturduğu iskelettir* — onun yerini almaz; çatışma hâlinde Çapar'ın yerleşik üslubu önceliklidir (zorunlu usul unsurları hariç — onlar her hâlde bulunur). Bu kural anonimleştirme anayasasının istisnasıdır: Çapar sistemin tasarımcısıdır ve söz konusu olan müvekkil/dava izi değil, tasarımcının kendi yazım metodudur.

## Ortak omurga (her dilekçede)
Doğru merci + hitap → taraflar (ad/unvan, TCKN/VKN, adres, vekil + baro/sicil) → esas no → konu → açıklamalar (vakıa → illiyet → norm/içtihat) → hukuki sebepler → deliller → **netice-i talep** → tarih + imza + sıfat. Talep gerekçeyle birebir örtüşür; her iddia bir delile bağlanır.

## GİRİŞ ve rütbelendirme — kanun yolu mimarisi (kısa çapa)
Kanun yolu dilekçelerinde (istinaf/temyiz/itiraz tipi) GİRİŞ bölümü **olay
özeti değildir**: karşı/aleyhe kararı 2-3 taşıyıcı dayanağa indirger ve her
dayanak için yıkım silahını önden ilan eder; ancak karşı kararın gerekçesi
**gerçekten muhakeme edilmişse** yazılabilir (muhakeme edilmemiş kararı
"indirgiyormuş gibi" özetlemek halüsinasyondur). Bölüm mimarisinde her
sebep **rütbelendirilir** (asıl neden / destekleyici) ve sıra usul → esas →
ölçülülük/belirlilik → gerekçe eksikliğidir (bkz. aşağıdaki "Anayasal
düstur"); SONUÇ/İSTEM numaralı ve önceliklidir. Tam mimari (B1 künye, B2
GİRİŞ, B3 argüman-yüklü vakıa, B5 5-turlu çökertme protokolü, B6 bölüm
mimarisi/rütbelendirme, B7 yardımcı desenler): `references/kanun-yolu-mimari-playbook.md`.

## Çıplak künye yasağı — yalnız MUHAKEME EDİLMİŞ içtihat girer (kritik, fail-closed)
Dilekçeye giren her içtihat, önce İçtihat Muhakeme Zinciri'nden geçmiş
olmalıdır: `oa-ictihat` künyeyi CEK eder → `oa-kiyas`/`oa-kontrol` MUHAKEME
eder ve `_oa/cikti/NN-ictihat-muhakeme.md` kaydını üretir (alan şeması:
`oa-kiyas/references/ictihat-muhakeme-sablonu.md`). Dilekçeye **yalnız**:
- DAMGA `LEHE` **veya** `ALEYHE-AYIRT` (AYIRT-ETME alanı dolu) olan,
- muhakeme kaydı KUNYE/KAYNAK-IZI/İLGİLİ-KISIM/DAVAYA-BAĞ (R4 — eski adı "İLLİYET") alanları tam olan

kararlar girer. **Çıplak künye** (yalnız daire+esas+karar, muhakeme kaydı
olmadan veya kaydı `NOTR`/damgasız olan) dilekçeye **YASAKTIR** — bu,
"muhakeme edilmemiş" demektir (fail-closed: damga yoksa/`NOTR` ise geçerli
sayılmaz). `ALEYHE` (ayırt edilmemiş) damgalı karar dilekçeye **hiçbir
zaman girmez**; iç analizde (muhakeme kaydı + `oa-antitez` cephaneliği)
işlenmesi **ZORUNLU**dur ama dış çıktıya yazılmaz — dış çıktı daima müvekkil
LEHİNEdir. Esaslı bir sonuç Yargıtay/BAM atfı içermiyorsa muhakeme "zayıf"
sayılır; bu açık uç olarak `oa-kontrol` çıktısında görünür kalır.

**DAVADAN GELEN ATIFLAR DA ZİNCİRE TABİDİR (v0.5.7.5 — kullanıcı kuralı).**
Dilekçede tartışılan bir yargı kararının kaynağı KİM olursa olsun — bizim
araştırmamız, KARŞI TARAFIN dilekçesi, GEREKÇELİ KARAR ya da bilirkişi
raporu — aynı zincir işler: karar `oa-ictihat`'tan fiilen ÇEKİLİR, teyit
edilir, damgalanır ve **erişim linki dilekçede künyenin yanında parantez
içinde verilir** (5-adım/1 + [G4] kapısı; link yalnız teyit anındaki
`**KAYNAK-URL:**` kaydından gelir — davadan gelen atıf için de uydurma
bağlantı yazılamaz, kayıt yoksa parantez açılmaz). İkili kazanç: (a) mahkeme,
tartışılan HER kararın kaynağına tek tıkla ulaşır; (b) karşı tarafın künyesi
körlemesine devralınmaz — çekilen tam metin künyeyle ya da karşı tarafın
alıntısıyla ÖRTÜŞMÜYORSA (yanlış künye, çarpıtılmış pasaj, bağlamından
koparılmış cümle) bu, dilekçede AÇIKÇA ileri sürülür: karşı atfın çürümesi
başlı başına savunma kozudur. Karşı tarafın dayandığı karar salt-ALEYHE
çıkarsa m.6 aynen uygulanır: karar zaten karşı tarafça İLERİ SÜRÜLMÜŞ
olduğundan cephanelik istisnası devrededir — ayırt etme/çürütme dilekçede
yapılır, kaçınılmaz.

## İçtihat kullanımı — 5 adım (İçtihat Muhakeme Zinciri'nin düzyazı izdüşümü)
Uyuşmazlığa uygun içtihat bulunduğunda (her zaman `oa-ictihat` üzerinden teyitli **ve yukarıdaki çıplak künye yasağı uyarınca muhakeme edilmiş**), dilekçede beş adım sırayla yürür (tam mimari — örüntüler + a fortiori/sınırlama tekniği: `references/kanun-yolu-mimari-playbook.md` B4):
1. **Tam künye + KAYNAK BAĞLANTISI:** merci + daire + esas no + karar no + tarih
   eksiksiz yazılır; hemen ardından **parantez içinde kararın resmî kaynak
   bağlantısı** verilir — ör. *Yargıtay 17. HD, 17.01.2013, 2012/2516 E.,
   2013/224 K. (https://…)*. Bağlantı **yalnız** muhakeme kaydındaki
   `**KAYNAK-URL:**` alanından gelir (teyit anında `oa_hafiza.py teyit
   --kaynak-url …` ile kaydedilmiştir). **Kayıtlı URL yoksa parantez HİÇ
   AÇILMAZ** — yazım aşamasında bağlantı üretilmez, tahmin edilmez,
   hatırlanmaz. Uydurma bağlantı çıplak künyeden DAHA KÖTÜDÜR: çıplak künye
   "teyit edilmedi" der, sahte bağlantı "teyit edildi" der. **[G4] mekanik
   kapı (v0.5.7):** bu kural artık `ictihat_muhakeme_denetim.py`'de denetlenir
   — künye yanında kütükte izi olmayan bağlantı TESLİM ENGELİDİR; kayıtlı
   bağlantının dilekçeye işlenmemesi görünür UYARIDIR (kullanıcı kuralı:
   karardan bahsedilince linki de dilekçede olmalı).
2. **İlgili kısmın aynen (birebir blok-)alıntısı:** kararın yalnızca uyuşmazlıkla **ilgili pasajı** (gerekçenin ilgili yeri) **birebir** alıntılanır — tüm karar değil, davayla bağlantılı kısım. Alıntı, MCP'den çekilen **karar metninden** (muhakeme kaydının İLGİLİ-KISIM alanı) gelir; **hafızadan/yeniden kurarak alıntı yapılmaz** (atıf denetimi → `oa-kontrol` A). **OCR kontrolü:** metin OCR/markdown dönüşümünden geldiği için bozuk olabilir; alıntıda kusur sezilirse **çalışmada "OCR şüphesi" diye bildir** ve kanonik kaynakla teyit et (`oa-ictihat`) — OCR hatasını "birebir" diye dilekçeye taşıma.
3. **Damıtma cümlesi:** alıntıdan hemen sonra, kararın koyduğu kuralı **soyutlayan** tek/birkaç cümle yazılır ("Bu karar ... hâllerde ... ortaya koymaktadır") — alıntıyı tekrar etmez, kuralı çıkarır.
4. **Somut tatbik:** damıtılan kural dosyanın olgu desenine **eşlenir** — olgular arasındaki benzerlik açıkça kurulur, mümkünse **a fortiori** ("emsaldeki olguda dahi kabul edilmişken, dosyamızdaki daha güçlü olguda evleviyetle kabul edilmelidir").
5. **Gerekirse sınırlama/ayırt şerhi:** **yalnız kendi lehe dayanağının** zayıf yönü, karşı taraf söylemeden önce dar biçimde sınırlanır (ALEYHE-AYIRT damgasının dilekçe-yüzü). **Sunum disiplini sınırı:** yalnız DUYULMUŞ (karşı tarafın fiilen dayandığı/kararda fiilen değerlendirilmiş) aleyhe içtihat ayırt edilir; duyulmamış aleyhe içtihat preemptive çürütülmez, `oa-antitez` cephaneliğinde dahili kalır (aşağıdaki "Sunum disiplini" ile aynı kök).

Çıplak alıntı (damıtma/tatbik açıklaması olmadan bırakılan alıntı) kabul edilmez; içtihat ancak davaya **uygulanarak** değer üretir.

## GÖRÜNMEZ İSKELET — paragrafın iç mantığı (P1-11 ek kural)
İDDİA→NORM→İÇTİHAT→ÖRTÜŞME→SONUÇ zinciri paragrafın **İÇ MANTIĞI**dır, yüzey
metnine **ETİKET olarak sızmaz** (saha dersi: canlı testte model iskeleti
görünür kalıba çevirdi — paragraf başlarına "İddiamız:", "Norm:", "Somut
örtüşme:" yazdı — akıcılık bozuldu, kullanıcı düzeltme istedi). Paragraflar
**geçiş cümleleriyle** anlam bütünlüğünde örülür; iskelet okurun
**hissettiği ama görmediği** bir mimaridir — tıpkı bir binanın taşıyıcı
kolonlarının sıvanın altında kalması gibi. `dilekce_denetim.py`'nin **[H]
GÖRÜNMEZ İSKELET TARAMASI** kapısı (advisory — ASLA bloklamaz) bu kalıp-
açılışları satır başında arar ve bulursa bir akıcılık uyarısı basar; bu
hukuki içerik denetimi DEĞİLDİR, yalnız biçim sinyalidir.

## ÖMERALP ÜSLUP BAĞLAMASI — yazım disiplini playbook'a zorunlu bağlı
Bu parçanın yazım disiplini `references/kanun-yolu-mimari-playbook.md`
(B1-B7, ömeralp temyizinden damıtık) üslubuna **ZORUNLU referansla bağlıdır:**
dilekçe o playbook'un yazım konseptiyle — **tez-omurgalı, akıcı, bütünsel
bağlantılı** — yazılır; yukarıdaki GÖRÜNMEZ İSKELET kuralı bunun ayrılmaz
parçasıdır (etiketli-parça değil, örülü-bütün). Teslim öncesi kontrol
listesine ek madde: **"üslup playbook'a uygun mu?"** — bkz. aşağıdaki
"Teslim öncesi MEKANİK KAPILAR" listesi ve `oa-kontrol/SKILL.md` B listesi
("Teslim öncesi kontrol (pre-filing)").

## KUSUR→SONUÇ→TALEP ASİMETRİSİ (P1-11 ek kural — taraf-bilinçli)
Karşı tarafın kusuru **TESPİT** edilir, doğurduğu **SONUÇ** yazılır, ama
**GİDERİLMESİNE yönelik ara karar talebi KURULMAZ.** (Ör. davalıysak: dava
şartı eksikliği tespit edilir + ret talebi KURULUR; "tamamlanması için süre
verilsin" talebi KURULMAZ — rakibin davasını onarmasına yardım etmek
müvekkil-aleyhi talep inşasıdır.) Bu, Anayasa m.6'nın (müvekkil-aleyhi dış
çıktı yasağı) **taktik yüzüdür** ve **taraf-bilinçlidir** — davacıysak ve
karşı taraf (davalı) kusurluysa aynı asimetri simetrik biçimde işler.
`dilekce_denetim.py`'nin **[I] KUSUR→SONUÇ→TALEP ASİMETRİSİ TARAMASI** kapısı
(advisory — ASLA bloklamaz) karşı-taraf-kusuru bağlamında "süre verilsin/
tamamlan-/gideril-" kalıplarını arar ve bulursa bir uyarı basar.

## AVUKAT REVİZESİNDEN DAMITILAN YEDİ KURAL (2026/307 saha vakası — v0.5.5.2)
Modelin ürettiği taslak ile avukatın imzaladığı nüsha karşılaştırıldı (147↔147
paragraf, 52.086→51.618 karakter). Avukat metni **kısaltırken iki esaslı vakıa
EKLEDİ** — yani çıkarılanlar hacim, eklenenler isabetti. Damıtılan kurallar:

1. **TESPİT ≠ İTİRAZ — dilekçe usulî işlemdir.** Taslak ihtiyati haczi
   *anlatıyordu*; avukat "**Bu ihtiyati haciz kararına da itiraz ediyoruz**"
   cümlesini ekledi. Aleyhe bir işlemi betimlemek ona itiraz etmek DEĞİLDİR:
   korunmak istenen her hak için AÇIK BEYAN kurulur.
2. **Terditli SAVUNMA kurulur, terditli TALEP kurulmaz.** Avukat bir yandan
   "davayı kabul etmemekle birlikte" kaydını EKLEDİ, öte yandan netice-i
   talepteki "aksi kanaatte sorumluluğun … sınırlı tutulmasına" fıkrasını
   SİLDİ. Sınır nettir: esasa ilişkin savunma ihtiyaten kurulabilir, ama
   mahkemeden **kendi yenilgini varsayan bir ara çözüm İSTENMEZ** — bu, hâkime
   hazır bir orta yol sunmaktır. (Kusur→Sonuç→Talep asimetrisinin kendi-taraf
   yüzü.)
3. **Savunulmayan usulî noktayı savunma.** Avukat, cevabın süresinde olduğunu
   ispatlayan koca bir "SÜRE" bölümünü tümüyle SİLDİ. Kimsenin itiraz etmediği
   bir usulî durumu savunmak, olmayan bir tartışmayı açar.
4. **"Sunacağız" değil, VAKIA kur ve sicile bağla.** Taslak "banka kayıtlarını
   delil listemizde bildirmiş olup süresi içinde sunacaktır" diyordu; avukat
   bunu karşılıklı devrin kendisiyle (aynı günler, ardışık yevmiye numaraları,
   TTSG tarih/sayı) değiştirdi. Vaat savunmayı erteler; **sicile bağlı olgu
   derhâl hüküm doğurur.**
5. **Künye gövdede tekrarlanmaz.** Gövdede OLGU, delil listesinde KÜNYE:
   avukat metne serpilmiş noter yevmiye künyelerini toplayıp gövdeden çıkardı,
   delil listesini "celbi: ilgili noterliklerden" biçiminde sadeleştirdi.
6. **İspat yükü AÇIKÇA tahsis edilir.** "Ticaret siciline işlenen resmi
   belgenin aksine olan **ispat yükü davacıdadır. Bu ispat yükü
   sağlanamamıştır.**" — taslak bunu ima ediyordu; hukukî sonuç ima edilmez,
   kurulur.
7. **Bölüm tek cümlelik net sonuçla kapanır.** "Özetle davalı müvekkilimizin
   tasarrufun iptaline konu olacak hiçbir işlemi yoktur." Uzun tahlilin
   sonucunu okurun çıkarmasına bırakma. (Bu, M8 SONUÇ ANATOMİSİ modülünün
   saha kanıtıdır.)

## İÇTİHAT PORTFÖYÜ — gövde vs kütük ayrımı (M6, Paket D — v0.5.5)
Muhakeme edilmiş (LEHE/ALEYHE-AYIRT) kararların SAYISI arttıkça hepsini gövdeye
5 adımla işlemek dilekçeyi ŞİŞİRİR ve en güçlü argümanı gürültüye gömer.
**v0.3.20 FINAL-MAX deseni:** gövdeye yalnız **en güçlü 3-5 karar** girer;
kalan tüm muhakeme edilmiş kararlar `_oa/cikti/03-ictihat-muhakeme.md`
kütüğünde **yedek** olarak durur (dış çıktıya İŞLENMEZ ama kaybolmaz —
gerekirse cevaba-cevap/istinaf aşamasında oradan çekilir). Güç sıralaması
(en güçlüden başlanır, gövdeye bu sırayla 3-5 tanesi girer):
1. **HGK/İBK > Daire kararı** — Hukuk/Ceza Genel Kurulu veya İçtihadı Birleştirme Kararı, tek daire kararından her zaman daha bağlayıcı/ağırlıklıdır.
2. **Yeni > Eski** — aynı ağırlıktaki kararlar arasında güncel tarihli olan (içtihat değişikliği/güncellenme riskine karşı) tercih edilir.
3. **İhtisas dairesi** — uyuşmazlığın gerçek ihtisas dairesinden gelen karar (bkz. `oa-alan` HSK iş bölümü tespiti), dolaylı/genel bir daireden gelene tercih edilir.
Bu sıralama bir hukuki isabet hükmü DEĞİLDİR (avukat muhakemesi son sözdür) —
yalnız "hangi 3-5'i gövdeye, kalanı kütüğe" seçimini disipline eden bir
heuristiktir; `oa-kontrol`'ün G1-G3 kapıları hâlâ HER karara (gövdedeki
VEYA kütükteki) aynen uygulanır.

## Playbook'lar

**Dava dilekçesi** — Zorunlu (HMK m.119): mahkeme; taraflar+TCKN; vekil; konu ve **değer/miktar** (harç/görev/kesinlik); vakıalar (sıra no); deliller (vakıayla eşli); hukuki sebepler; talep; imza. Sık atlanan: dava değeri, delil-vakıa eşlemesi, yetki/görev.

**Cevap dilekçesi** — Zorunlu (HMK m.129): savunma; karşı vakıalar; deliller; **ilk itirazlar** (süresinde sürülmezse düşer); talep. Süre kural olarak iki hafta. İstihkak (İİK m.97/a): **mülkiyet karinesi** ekseni (istihkak savunmasının taşıyıcı eksenlerinden). Sık atlanan: ilk itirazların süresinde sürülmesi; inkâr edilmeyen vakıanın ikrar sayılması.

**İstinaf dilekçesi** — Zorunlu (HMK m.342 vd.): ilk derece künyesi; **somut, gerekçeli istinaf sebepleri**; talep. Süre iki hafta (m.345); harç/gider tam (m.344). Sık atlanan: her sebebin ilk derece dosyasındaki **somut dayanağa** bağlanması; katılma/cevap süreleri (m.347-348). (örüntü: işçilik istinafında hukuka aykırı delil m.189/2 + toplu iş sözleşmesinin dosyaya celbedilmemesi — çok gerekçeli istinafta her sebep ayrı sütun.)

**Temyiz dilekçesi** — Zorunlu: BAM künyesi; **hukuka aykırılık** sebepleri; talep. Süre iki hafta (m.361); temyiz edilebilirlik (parasal sınır/kategori) önce kontrol. Maddi vakıa değil, hukuka aykırılık ekseninde yaz.

**AYM bireysel başvuru** — Zorunlu (6216 m.47/3): kimlik-adres; ihlal edilen hak; **dayanılan Anayasa hükümleri**; ihlal gerekçeleri; **başvuru yolları tüketme aşamaları**; tüketme/öğrenme tarihi; zarar; deliller + karar aslı/örneği + harç belgesi; vekilse **vekâletname** (m.47/4). Süre 30 gün (m.47/5 → `oa-sure`). İhlal eksenleri: gerekçeli karar hakkı, silahların eşitliği/sürpriz karar yasağı, mülkiyet, özel hayat/meslek hayatı; her eksen AYM-teyitli kararla. Sık atlanan: tam tüketme; kişisel/güncel/doğrudan etkilenme (m.46); süre başlangıcı (en sık açık uç: tebliğ/öğrenme tarihi).

**Tasarrufun iptali — davalı cevabı (takas/ivaz kalıbı)** — Davalı borçludan
mal/pay devralmış ve karşılığında kendi malvarlığından bir şey vermişse:
karşı-yönlü devri **sicilden** kur (TTSG tarih/sayı/sayfa/ilan no) → aleniyeti
**TTK m.36/3** ile karşı tarafa bağla → iptale tabi tasarrufun **aktifi azaltan**
işlem olduğu ve bunun **dava şartı** sayıldığı ilkesini kur → karşılığın nakit
değil **sicile tescilli, hacze açık** malvarlığı olduğunu vurgula → bölümü tek
cümleyle kapat. Ayrıntı, güvenli künye formülü, TTSG'nin noter-künyesi olarak
okunması ve **kalıbın dürüst sınırı** (birebir emsal bulunamadı; kalıp norm
üzerinde durur): `references/ticaret-sicili-desenleri.md`. **Kritik niteleme:**
TTSG'deki yevmiye, genel kurul kararının TASDİK yevmiyesidir — pay devir
sözleşmesinin yevmiyesi DEĞİLDİR.

**Yemin teklif dilekçesi + metni** — Dayanak HMK m.225 vd.; iade m.228. Vakıa **kesin, tek tek, net** formüle edilir. Yalnızca kesin delil bulunmayan, çekişmeli, yeminle ispatı caiz vakıada; yeminin iadesi ihtimali müvekkile anlatılır. (bono uyuşmazlığı örüntüsü: teklif dilekçesi + yemin metni + m.228 birlikte hazırlanır.)

**İdari kanal başvuru (çocuk teslimi/kişisel ilişki)** — Dayanak 5395 ÇKK + 7343 + Yönetmelik; **Adli Destek ve Mağdur Hizmetleri Müdürlüğü** kanalı (eski İİK m.25 vd. mülga). Asil bizzat ise birinci tekil şahıs; mahkeme kararı onaylı sureti; varsa 6284 kararı; iletişim bilgisi zorunlu. Sık atlanan: asil/vekil diline göre imza bloğu; adres/telefon; teslim süresi/yeri.

**Sözleşme tahriri** — *(NOT: kapsamlı sözleşme işi artık ayrı parça `oa-sozlesme`'dedir — tahrir/inceleme/revize/müzakere, kloz kapsam denetimi scriptiyle; bu playbook basit/hızlı protokoller ve aile-hukuku protokolleri için kalır.)* Boşanma protokolü: velayet + **kişisel ilişki takvimi** (tatil/bayram/yaz), nafaka, mal rejimi/**katılma alacağı**, adres bildirimi, uluslararası seyahat izni. Adi ortaklık/ticari: edim dengesi, fesih/tasfiye, paylı mülkiyet, mahsuplaşma, defter/kasa, yetki. Sık atlanan: ifa yeri/zamanı, temerrüt/cezai şart, ihtirazi kayıt, fesih usulü.

**Hukuki mütalaa** — Yapı: sorun → maddi vakıa → norm (teyitli) → içtihat (teyitli) → **karşı tez + zaaflar** → sonuç/strateji + açık uçlar. Sık atlanan: müvekkil-aleyhi zaafın açıkça raporlanması; sulh/uzlaşma alternatifi; kesin tavsiye dayatması değil karar-malzemesi.

## Aktif çıkarım refleksi
Şablonu edilgen doldurma. **En güçlü müvekkil-lehi çerçeveyi sen kur**: olguların desteklediği ama anılmamış bir talebi/savunmayı ekle; argümanları en yüksek etki için sırala; zayıf görüneni lehte konumlandır (gizleyerek değil, yöneterek). Dilekçe bir form değil, lehe inşa edilen bir stratejidir.

## ANTİTEZ PASI — zorunlu girdi (M3, Paket D — v0.5.5)
Yazımdan ÖNCE `oa-antitez`'in çıktısı (`_oa/cikti/*antitez*.json` matrisi) **zorunlu bir pas girdisidir** — antitez koşulmadan yazılan bir dilekçe, karşı tarafın en güçlü kozları görülmeden kurulmuş demektir (durum farkındalığı eksik). `dilekce_denetim.py`'nin **[G] ANTİTEZ-CEVAP-ÇAPASI** kapısı (advisory — ASLA bloklamaz) matristeki her **DUYULMUŞ** (karşı taraf fiilen ileri sürmüş) + çürütülmüş cephe için dilekçede bir anahtar-kelime çapası arar; bulamazsa görünür bir uyarı basar ("çürütme dış çıktıya işlenmemiş olabilir"). Aleyhe tarama İÇ dosyaya (matris, `duyulmus:false` kayıtlar) **AKTİF** kalır — dış dilekçeye yalnız **DUYULMUŞ** olan girer (aşağıdaki "Sunum disiplini" ile aynı kök).

## Sunum disiplini — sunulmamış antiteze değinme
Sunulan dilekçede, karşı tarafın **henüz ileri sürmediği** bir savunmaya/iddiaya karşı preemptive çürütme **yazma** — kendi zayıf noktanı işaret etmek ve karşı tarafı silahlandırmaktır. Dilekçeyi dosyada/karar gerekçesinde fiilen **var olana** göre kur (dava dilekçesi kendi tezini; cevap karşı tarafın ileri sürdüğünü; istinaf/temyiz kararın gerekçesini karşılar). Hipotetik antiteze hazırlık `oa-antitez` cephaneliğinde **dahili** durur; karşı taraf ileri sürünce devreye girer. (Not: olguların desteklediği kendi olumlu talebini eklemek bundan farklıdır ve teşvik edilir.)

## Kompozisyon ve çıktı
Süre satırı için `oa-sure`; her atıf `oa-ictihat`'tan teyitli; alan tespiti `oa-alan`.

**Çıktı formatı — UDF VARSAYILAN (kurucu kural):** Kullanıcı/Fable kararı: **aksi açıkça talep edilmedikçe (ör. "md olarak ver", "docx istiyorum") dilekçe çıktısı UDF formatında üretilir.** md taslak her hâlde ARA ÜRÜNdür (UDF ondan türetilir), teslim edilen NİHAİ çıktı UDF'dir.

**ALTIN KURAL — UDF ELLE YAZILMAZ (GÖREV D, B5 — bağlayıcı):** UDF, yalnız `udf-cli`'nin üretebildiği/okuyabildiği opak bir UYAP biçimidir; içyapısı hakkında varsayımda bulunulmaz, zip/`content.xml` elle kurulmaz, `.udf` elle düzenlenmez, ve **`md2udf` ASLA kullanılmaz — daima `html2udf`**. Ayrıntılı operasyonel referans: `references/uyap-belge-formatlari.md` (Yargı Pro `udf_tiff_pdf_guide` rehberinin ailedeki klonu — güncel sürüm için daima o dosyaya/rehbere bakılır). Saha kanıtı (v0.5.5, KRİTİK): eski hand-rolled zip motorunun ürettiği `.udf` **UYAP editöründe açılmadı** — bu yüzden o motor (`--yerel-motor`) `udf_yaz.py`'den TAMAMEN KALDIRILDI; script'in artık TEK yazma yolu gerçek `npx -y udf-cli@latest html2udf` çağrısıdır.

Akış: taslak metin (md) → `python scripts/udf_yaz.py --girdi taslak.md --cikti dilekce.udf` — bu komut md'yi UDF-HTML'e çevirir (`md_udf_html.py`) ve rehberin ZORUNLU kıldığı gerçek yazıcıyı (`npx -y udf-cli@latest html2udf`, ağ+oturum ister) çağırır; opsiyonel `--pdf dilekce.pdf` ile aynı ara HTML'den A4 PDF de üretir (`udf_html2pdf.py`, ağsız — UDF üretimi başarısız olsa BİLE denenir). **npx/udf-cli bulunamazsa veya oturum gerekiyorsa script FAIL-CLOSED çıkar: hiçbir `.udf` yazılmaz, exit != 0, stderr'de net talimat** (`npx -y udf-cli@latest login` insan varsa; başsız ortamda `issue_cli_login_code` MCP aracı) — eski elle-zip yoluna SESSİZCE düşülmez. Ardından aşağıdaki **UDF GEÇERLİLİK KAPISI**. Yalnız kullanıcı açıkça md/docx istediğinde bu akış atlanır; hazır bir `.docx`/`.pdf` varsa `docx2udf` (login-gated) kullanılabilir (bkz. referans §5).

**TESLİM tanımı tekildir (P1-11 — bağlayıcı doktrin):** bir taslak ancak
`oa-kontrol/scripts/teslim_paketi.py` **exit 0 + `_oa/defter/teslim-makbuz.json`**
üretiminden geçtiyse TESLİM EDİLMİŞ sayılır — başka hiçbir işaret (dosya adı,
sözel beyan, "hazır" demek) TESLİM'i belgelemez. **`TESLİM`/`FINAL` adı**
(ör. `08-dilekce-TESLIM.md`) makbuz kapısını tetikleyen hızlı ad-deseni
sinyalidir (`pipeline_kayit.py`'nin ad-bağımsız uyarısı da her hâlükârda
çalışır) — **FINAL adını yalnız gerçekten son sürüme sakla**; ara taslaklara
bu adı erken vermek makbuz kapısını yanlış zamanda tetikler.

**Teslim öncesi MEKANİK KAPILAR (R2 — tek ölçüt `teslim_paketi.py` exit 0; aşağıdaki alt kapılar bu tek script'in içinde sabit sırada koşar, elle sayılmaz):**
1. **UDF GEÇERLİLİK KAPISI** (UDF çıktısı üretildiyse zorunlu) — `python scripts/udf_yaz.py --dogrula dilekce.udf` (yazmadan var olan dosyayı denetler) **veya** `python scripts/dilekce_denetim.py <taslak.md> --tip ... --taraf ... --udf dilekce.udf` (aşağıdaki [A]-[D] ile birlikte tek çağrıda [E] olarak çalışır). Denetlenen: zip açılır mı, `content.xml` var mı, XML iyi biçimli mi, **offset taşıyan TÜM elemanlar** (yalnız `<content>` değil — gerçek çıktıda `<tab/>` de offset taşır) CDATA metnini UTF-16 code-unit biriminde **boşluksuz ve örtüşmesiz döşüyor** mu, ve **5. bacak: RESMİ OKUYUCU TANIĞI** — dosya, onu ÜRETEN aracın kendi okuyucusuyla (`npx -y udf-cli@latest udf2md`) geri okunabiliyor mu. Beşinci bacağın gerekçesi: ilk dördü dosyayı BİZİM ayrıştırıcımızın varsayımına göre sınar; sahada bizi yakan hata sınıfı ise tam olarak "bizim round-trip'imizi geçen ama UYAP'ın açmadığı dosya"ydı — kendi varsayımıyla kendini doğrulamak kanıt değildir. Ağ/oturum yoksa bu bacak **YAPILAMADI** der (görünür; "doğrulandı" SAYILMAZ) ve bloklamaz — ortam koşuludur, dosyanın kusuru değil. Script yalnız **"geçerli/geçersiz UDF"** der — **"iyi dilekçe" demez** (sahte kesinlik yok); GEÇERSİZ ise exit 1.
2. `python scripts/dilekce_denetim.py <taslak.md> --tip <dava|cevap|istinaf|temyiz|aym_bireysel|yemin|idari-kanal> --taraf <davaci|davali|sanik>` — tip başına zorunlu unsur + "avukata yakışan tertip-düzen" + OCR-teyit şerhi + **MÜVEKKİL-ALEYHİ İFADE TARAMASI** (anayasal tek katı sınır: davalıda kabul/ikrar, davacıda kendi iddiasını çökerten ifade → exit 1 ile durdurur). **`--tip istinaf|temyiz` iken (M3-2):** [B] TERTİP-DÜZEN kapısı, `kanun-yolu-mimari-playbook.md`'nin B1/B2/B4/B6 mekanik izdüşümünü de denetler — künye blok alan seti (kanun yoluna konu kararın kimliği/sonucu + dayanak norm), TEBLİĞ TARİHİ'nin AYRI SATIRDA olması, GİRİŞ bölümünün varlığı, SONUÇ/İSTEM'in numaralı olması, her içtihat blok-alıntısının ardından açıklama paragrafı bulunması — yalnız VAR/YOK (uyarı, bloklamaz). `--ictihat-muhakeme` ile birlikte `--tip` değeri [F] kapısına da geçer: G1 "emsal içtihat yok" uyarısı yalnız "esaslı" tiplerde (dava/cevap/istinaf/temyiz/aym_bireysel) basılır, `yemin`/`idari-kanal` gibi hafif tiplerde [BİLGİ]'ye düşer (R6).
3. `python ../oa-kontrol/scripts/kunye_teyit.py <taslak.md>` — her içtihat/mevzuat atfının teyit kütüğünde izi var mı (teyitsiz atıf → exit 1).
4. `oa-kontrol` A (atıf) + B (usul+esas) listeleri — B listesine eklenen **"üslup playbook'a uygun mu?"** maddesi dahil (aşağıya bkz.).

Aynı `dilekce_denetim.py` çağrısı (madde 2) iki ADVISORY kapıyı da (ASLA
bloklamaz, exit koduna dokunmaz) tek raporda basar: **[H] GÖRÜNMEZ İSKELET
TARAMASI** (yukarıdaki "GÖRÜNMEZ İSKELET" kuralı) ve **[I] KUSUR→SONUÇ→TALEP
ASİMETRİSİ TARAMASI** (yukarıdaki "KUSUR→SONUÇ→TALEP ASİMETRİSİ" kuralı).
Teslim öncesi son avukat gözünde bu iki uyarı da — **üslup playbook'a uygun
mu?** sorusuyla birlikte — okunur; bloklamadıkları için elle görülmezlerse
sessizce geçilebilirler.

## Öğrenme günlüğü
Yeni bir tip/zorunlu unsur/sık-atlanan alan öğrenildiğinde ilgili playbook'a ekle, aşağıya işle, yeniden paketle.
## Anayasal düstur — usul esasa üstündür
Usulün esasa takaddümü ailenin anayasal düsturudur: usulden düşen dosya esasa hiç giremez; süre, usul hukukunun parçası ve telafisiz tek hatadır. Dilekçede **usul katmanı esastan önce kurulur ve denetlenir**: doğru merci (görev/yetki), süre satırı, harç, zorunlu unsurlar (m.119/129/342...), taraf/temsil — usulden dönen dilekçe esası hiç anlatamaz. Karşı tarafın süre kaçırması tespitliyse (`oa-sure --islem`, belgeli tebliğle) **süre/usul itirazı paragrafı dilekçenin EN BAŞINA** yazılır ve netice-i talep 'ÖNCELİKLE usulden (süre yönünden) reddi' ile açılır; esas savunma 'kabul anlamına gelmemek kaydıyla' onu izler.

## Anayasal bloklar — tek kaynak (anayasa.md)
Bu parça, ailenin ortak anayasal ilkelerine tabidir — **Çaba/token standardı** (model/efor kullanıcının tercihi; muhakemede/doğrulamada/çıktı kalitesinde tasarruf YOK, yalnız mekanik katmanda kayıpsız verimlilik), **Örnekleme ilkesi** (konu sınırlaması yok — kapsam TÜM Türk hukuku), **Doğaçlama meşruiyeti** (yöntem serbest, olgu MCP-teyitli), ayrıca Doğrulama mimarisi, Anonimleştirme ve Layer 0 gizlilik. **Tek ve yetkili kaynak: `ortak-avukat/references/anayasa.md`.** (Bu parça alt-ajan olarak koşarken bu ilkeler `oa-pipeline/scripts/oa_hafiza.py ajan-brif` ile taşınır.)

## Başbakan denetimi (anayasal)
Bu parça, ailenin Başbakanı `oa-pipeline`'ın icra+denetimine tabidir: çağrıldığında disiplini İSTİSNASIZ ve tam işletilir (ama/fakat/token-tasarrufu gerekçesiyle kestirme YASAK). Görev savsaklanmaz; gerçekten yapılamayan bir şey varsa dürüstçe belirtilir ("yaptım" denmez) ve alternatif yöntem üretilir. Önemli olan proses ve çıktı kalitesidir.

## Müvekkil-aleyhi dış çıktı yasağı (anayasal)
Teslim edilen dilekçe/sözleşme DIŞ çıktıdır: müvekkili zayıflatan, gereksiz ikrar içeren, karşı tarafa koz veren ifade ÜRETİLMEZ; metin daima müvekkil lehine kurgulanır. Zaaf varsa iç analizde (avukata) dürüstçe bildirilir ama dış belgeye yazılmaz — saklamak değil, karşı tarafın eline vermemek. (Zorunlu usul unsurları ve mahkemeye karşı dürüstlük hariç tutulamaz.)

## Fiziksel aktivasyon — simülasyon yasağı (anayasal)
Bu parça yalnızca ÜÇ kanıttan en az biriyle "çalıştı" sayılır: (1) Skill aracıyla FİİLEN çağrıldı ve bu gövde bağlama yüklendi (kullanıcının `/oa-dilekce` komutuyla eşdeğer); (2) scripti gerçekten koştu ve çıktısı görünür; (3) gerektirdiği MCP çağrısı fiilen yapıldı (araç + sorgu + sonuç kaydıyla). Kısa description her zaman bağlamda durur — o VİTRİNDİR, disiplin değildir; gerçek disiplin bu gövdededir. Bu yüzden hiçbir parça bu parçayı description'ından TAKLİT EDEMEZ; bu parça da başka bir parçanın işine ihtiyaç duyduğunda onu Skill aracıyla fiilen çağırır (olmuyorsa SKILL.md'sini Read ile yükler; o da olmuyorsa "FİZİKEN YÜKLENEMEDİ" diye açıkça yazar). Yapılmamış çağrı 'yapılmış', koşmamış script 'koşmuş' gösterilemez — bu, halüsinasyonun ta kendisidir. Devir alırken/verirken kısa DEVİR PAKETİ (ne yapıldı → ne bekleniyor → hangi kanıt) kullanılır ve pipeline defterine (`oa-pipeline/scripts/pipeline_kayit.py`) işlenir. Bu parçanın ürettiği her kalıcı çıktı (JSON/rapor/devir paketi) çalışılan klasörün `_oa/` yerel hafıza kökünde yaşar (yapı: `oa-pipeline` → Çalışma Kökü).

## Değişiklik Günlüğü
Tam günlük `references/degisiklik-gunlugu.md`'dedir (bağlam ekonomisi için ayrıldı — içerik aynen korunur; yeni kayıtlar oraya işlenir). Güncel sürüm: **v3.26**.

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

## v0.5.8.1 — KOMPAKT-KAPANIŞ KURALI (447 provası dersleri; pipeline ŞART DEĞİL)

Bu parça bir teslim ürünü (dilekçe/mütalaa — md/html/pdf/udf) ürettiği AN,
pipeline hattı kurulu olmasa bile şu beşli ZORUNLUDUR:

1. **Link:** her künyenin YANINA kütükteki `KAYNAK-URL` erişim linki yazılır —
   linksiz künye EKSİK atıftır ([G4]; kural v0.5.7.5'ten beri yürürlükte).
2. **m.6 CEPHANELİK:** karşı tarafın MUHTEMEL savunmalarının analizi ve
   cevapları DİLEKÇEYE YAZILMAZ — yalnız `_oa/cikti/07-antitez-cephanelik.md`
   iç dosyasına yazılır (farkındalık içindir; dilekçede kurulması savunma
   hattını karşı tarafa HEDİYE etmek ve zayıf noktayı İFŞA etmektir).
   Bilinçli ön-karşılama (praeoccupatio) yalnız avukat onayıyla kalır.
   Mekanik gözü: `dilekce_denetim.py` [K] taraması (advisory).
3. **KAYNAK-BLOĞU:** ürünün İLK satırları `<!-- kaynaklar: yol@sha8 · ... -->`
   `<!-- besledigi: ... -->` `<!-- uretim: <zaman> · <parça> -->` (graft
   deseni; `tazelik_denetim.py` bunu okur — bayatlama görünür olur).
4. **MÜHÜR:** üretimden hemen sonra
   `oa-kontrol/scripts/muhur_yaz.py --kok . --urun <yol> --girdi <girdiler>`
   koşulur (ürün başına `.prov.json` doğum belgesi; UYAP öncesi `--dogrula`).
5. **DENETİM:** `oa-dilekce/scripts/dilekce_denetim.py <taslak> --kok .`
   (içinde [F] içtihat-muhakeme + [G4]/[G5] + [K] m.6 taraması birleşiktir)
   koşulmadan hiçbir ürün avukata "hazır" diye sunulamaz.

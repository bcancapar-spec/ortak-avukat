# İcra dilekçe ailesi — OA yöntemiyle tip cetveli (v0.5.18 aday)

> **Neden var.** v0.5.17'ye kadar dilekçe kapısı (`scripts/dilekce_denetim.py`)
> dava, cevap, istinaf, temyiz, AYM ve genel tipleri tanıyordu; **icra tipi
> yoktu.** Takip talebi, ödeme emrine itiraz ya da ihalenin feshi gibi bir metin
> `--tip genel` ile denetleniyor, İİK'nın kendine özgü zorunlu içeriği (yurt içi
> adres, kısmi itirazda cihet ve miktar, süre başlangıcının tarihi, satışta
> gider avansı …) hiç aranmıyordu. Bu cetvel o boşluğu kapatır.
>
> **Karşı-tez incelemesi.** Cetvelin ilk sürümü Fable 5.1'e salt okunur
> incelemeye verildi (2026-10-05); benimsenen düzeltmeler: süre İFADESİ yerine
> süre başlangıcının TARİHİ (olayın yanında) aranır; kanunun "talep üzerine" ya
> da "karar verebilir" dediği istemler (inkâr tazminatı, kambiyoda geçici
> durdurma) zorunlu unsur değil istişari uyarıdır; "varsa" denen TCKN/VKN ve
> vadesiz bonoda vade zorunlu parça değildir; ticari dava şartı sinyali
> daraltıldı. Her düzeltme resmî metinle yeniden doğrulandı; Fable görüşü
> kaynak sayılmadı.
>
> **Kaynak ve otorite.** Ailenin ayrıştırma fikri (takip açma / takibe itiraz /
> haciz-satış / icra mahkemesi / bağlı davalar / icra ceza / usul işlemleri)
> Yargı PRO'nun 3-1…3-9 skill'lerinden **fikir olarak** alındı; metin, kod ve
> script alınmadı. Otorite OA yöntemidir: model metni kurar, script yalnız
> mekanik VAR/YOK der; hukuki ölçüt resmî metindir. Aşağıdaki her madde ve süre
> **Yargı PRO MCP `mevzuat_getir` ile mevzuat.gov.tr metninden 2026-10-05'te
> okundu** (künye tablosu en sonda). Okunmayan iddia yazılmadı; teyit
> edilemeyen yerde `TEYİT BEKLİYOR` yazar.

## 0. Yazımdan önce — icra dosyasını beş katmanda oku

Dilekçeyi yazmadan önce dosya şu sırayla okunur; her katman bir sonrakinin
ön şartıdır. Okuma çıktısı iç analizdir (`_oa/cikti/`), dilekçeye girmez.

1. **Takip yolu.** Yol, senedin türünden değil **takip talebinden ve ödeme/icra
   emri örneğinden** okunur. Bonoya dayanan ama genel haciz yoluyla açılmış bir
   takip ilamsız rejime tabidir; kambiyo rejimi ancak kambiyoya özgü yolla
   açılmış takipte işler. Yol yanlış okunursa merci, süre ve durdurma etkisi
   birlikte yanlış olur.
2. **Tebliğ.** Ödeme emri, icra emri, itiraz ya da kıymet takdiri raporunun
   tebliğ tarihi mazbatadan okunur (şüphede `oa-usul` tebligat denetimi).
   Tarih belgeyle bağlanamıyorsa süre hesaplanmaz, avukata tek soru sorulur.
3. **Kesinleşme.** İtiraz var mı, hangi mercie, hangi kapsamda (kısmi mi),
   imza ayrıca reddedilmiş mi? Kısmi itirazda kabul edilen kısım için takip
   sürer (İİK m.66/1).
4. **Aşama.** Haciz, haciz ihbarnamesi (m.89 zinciri), istihkak, kıymet
   takdiri, satış, ihale, sıra cetveli — hangisi açık, hangisi kapalı.
5. **Süre haritası.** Her açık pencere `oa-sure` ile hesaplanır, elle
   hesaplanmaz (aşağıda §3).

## 1. Yol ve merci ayrımı — müvekkil kaybını önleyen asıl ayrım

- **İlamsız takip (genel haciz).** Ödeme emrine itiraz **icra dairesine**,
  ödeme emrinin tebliğinden **yedi gün** içinde, dilekçe ya da sözlü beyanla
  yapılır (İİK m.62/1). Süresinde itiraz **takibi durdurur** (m.66/1). Borcun
  bir kısmına itiraz eden, o kısmın **cihetini ve miktarını açıkça** gösterir;
  göstermezse itiraz edilmemiş sayılır (m.62, kısmi itiraz fıkrası). Senetteki
  imza reddedilecekse bu **ayrıca ve açıkça** yazılır; yazılmazsa icra takibi
  yönünden imza kabul edilmiş sayılır (m.62, imza fıkrası). Borçlu ya da
  vekili itirazla birlikte borçlunun **yurt içindeki adresini** bildirmek
  zorundadır (m.62, adres fıkrası). m.62'nin fıkraları konusuyla anılır:
  metindeki mülga fıkra notu yüzünden fıkra sırası belirsizdir.
- **Kambiyo senetlerine mahsus haciz yolu.** Senedin kambiyo vasfına şikâyet,
  imzaya itiraz ve borca itiraz (borçlu olmama, itfa, mehil, zamanaşımı, yetki)
  **icra mahkemesine**, dilekçeyle ve **beş gün** içinde yapılır (m.168/1-3, 4,
  5). Borca da imzaya da itiraz **satıştan başka takip işlemlerini
  durdurmaz** (m.169, m.170/1); mahkeme takibin geçici olarak durdurulmasına
  karar **verebilir** (m.169/a-2, m.170/2). Durdurma istemi bir **risk
  kararıdır**: takip durdurulur ve itiraz reddedilirse borçlu, karşı tarafın
  isteği üzerine yüzde yirmiden az olmamak üzere tazminata (m.169/a-6), imza
  itirazında ayrıca yüzde on para cezasına (m.170/3) mahkûm edilir. İmza
  itirazı geri alınırsa ya da borç kısmen veya tamamen kabul edilirse
  mahkemenin vasfı re'sen gözetmesi (m.170/a-2) artık uygulanmaz (m.170/a-3) —
  kambiyo itirazında "kısmen kabul" cümlesi bu yüzden müvekkil aleyhidir.
- **Kira ve hasılat kirası (ihtarlı ödeme emri).** Borçlu itiraz sebeplerini
  yedi gün içinde icra dairesine bildirir; kira akdini ve varsa sözleşmedeki
  imzasını **açık ve kesin** reddetmezse akdi kabul etmiş sayılır (m.269/2).
  Eski Borçlar Kanunu m.260'taki altı günlük mühlet hâlinde itiraz süresi üç
  gündür (m.269 son fıkra; TBK karşılığı bu turda okunmadı — `TEYİT BEKLİYOR`).
- **İlamlı takip.** İcra emrinin tebliğinden itibaren yedi gün içinde
  zamanaşımı, itfa ya da imhal itirazı icra mahkemesine yapılır (m.33/1);
  tehir-i icra için kanun yolu başvurusu ile depo ya da teminat gerekir (m.36).

**Kesin kaldırma ile itirazın iptali ayrıdır.** Takip, imzası ikrar edilmiş ya
da noterce onaylı borç ikrarı içeren bir senede veya resmî bir belgeye
dayanıyorsa alacaklı itirazın tebliğinden **altı ay** içinde icra
mahkemesinden itirazın kaldırılmasını isteyebilir; bu süre geçerse aynı alacak
için yeniden ilamsız takip yapılamaz (m.68/1). Senet hususi ve imza
reddedilmişse yol geçici kaldırmadır (m.68/a, yine altı ay). Belge yoksa ya da
altı ay geçmişse yol, genel mahkemede **bir yıl** içinde açılan itirazın iptali
davasıdır (m.67/1). İtirazın iptali icra mahkemesinde değil genel mahkemede
görülür; dilekçe kapısı başlıkta icra mahkemesi görürse uyarır.

## 2. Tip cetveli — `dilekce_denetim.py --tip`

Her tip için: ne zaman · kapının [A] zorunlu unsurları · süre bağlantısı ·
müvekkil-aleyhi ekseni · sık atlanan (kapının [A] altındaki istişari uyarısı).
Unsur adlarının tam metni ve desenleri scriptteki `TIPLER` sözlüğündedir; bu
liste onun insan-okur özetidir.

### takip-talebi (İİK m.58; kambiyoda m.167)
- **Ne zaman:** takip başlatılırken, icra dairesine.
- **Zorunlu unsurlar:** icra dairesi; alacaklının adı/unvanı ve yerleşim yeri
  (adresi); ödemenin yapılacağı banka ve hesap bilgisi (m.58/2-1); borçlunun
  adı/unvanı ve adresi (m.58/2-2); alacağın Türk parasıyla tutarı, faiz
  isteniyorsa faizin miktarı/oranı ve işlemeye başladığı gün (m.58/2-3); senet
  ya da borcun sebebi (m.58/2-4); seçilen takip yolu (m.58/2-5); alacak bir
  belgeye dayanıyorsa belgenin aslı ya da onaylı örnekleri (m.58/3); kambiyoda
  senedin aslı ve borçlu adedince onaylı örneği (m.167/2); kira tahliyesinde
  ihtar ve tahliye istemi (m.269/1); tarih ve imza. **Vade aranmaz:**
  vadesi gösterilmemiş bono görüldüğünde ödenecek sayılır (TTK m.777/2);
  vadenin denetimi icra dairesinindir (İİK m.168/1).
- **Süre bağlantısı:** takip talebinin kendi süresi yoktur. Alacağın
  zamanaşımı maddi süredir (`oa-sure --tur maddi`). Karşı tarafın itiraz
  penceresi (m.62/1 ya da m.168) ve haciz isteme süresi (m.78/2) izlenir.
- **Müvekkil-aleyhi eksen:** alacaklı (`--taraf alacakli`).
- **Sık atlanan:** faiz istemi hiç yoksa uyarı — faizsiz takip çoğu zaman
  müvekkil kaybıdır, karar avukatındır. TCKN/VKN görünmüyorsa uyarı: kanun
  alacaklınınkini "varsa" (m.58/2-1), borçlununkini "alacaklı tarafından
  biliniyorsa" (m.58/2-2) ister — zorunlu parça değildir.

### odeme-emrine-itiraz (İİK m.62; kira tahliyesinde m.269)
- **Zorunlu unsurlar:** takibi yapan icra dairesi; takip dosyası; borçlu ve
  **borçlunun yurt içi adresi** (m.62, adres fıkrası); ödeme emrinin **tebliğ
  (ya da usulsüz tebliğde öğrenme) tarihi** — tebliğ olayının yanında; açık
  itiraz beyanı (borca, faize, ferilerine); itiraz kısmiyse **cihet ve
  miktar** (m.62, kısmi itiraz fıkrası); takibin durdurulması istemi; tarih ve
  imza.
- **Süre bağlantısı:** m.62/1 — ödeme emrinin tebliğinden yedi gün (kira
  tahliyesinde m.269/2).
- **Müvekkil-aleyhi eksen:** borçlu (`--taraf borclu`). İlamsız takipte kısmi
  kabul + kısmi itiraz meşru bir stratejidir; kambiyoya özgü "kısmen kabul"
  kalıbı burada taranmaz (birinci ağızdan "kabul ediyoruz/etmekteyiz" ise
  davalı ekseniyle her tipte taranır).
- **Sık atlanan:** senede ya da sözleşmeye dayanan takipte imza beyanı yoksa
  uyarı (m.62, imza fıkrası); kira tahliyesinde akdin açık ve kesin reddi yoksa
  uyarı (m.269/2). İkisi de avukat kararıdır: imza bilinçli olarak kabul
  edilebilir.

### kambiyo-itiraz (İİK m.168/1-3, 4, 5; m.169, 169/a, 170, 170/a)
- **Zorunlu unsurlar:** icra mahkemesi; takip dosyası (icra dairesi + esas
  no); borçlu ve alacaklı; ödeme emrinin tebliğ (ya da öğrenme) tarihi;
  itirazın türü açıkça (borca / imzaya / vasıf şikâyeti / yetki); itiraz
  sebebi; **borçlu olmama, itfa ya da imhal ileri sürülüyorsa** resmî veya
  imzası ikrar edilmiş dayanak belge (m.169/a-1 — zamanaşımı ve yetki
  itirazında belge koşulu yoktur; "Deliller" başlığı belge sayılmaz);
  itirazın kabulü/takibin iptali talebi; tarih ve imza.
- **Süre bağlantısı:** m.168/1-3, 4, 5 — ödeme emrinin tebliğinden beş gün.
- **Müvekkil-aleyhi eksen:** borçlu; bu tipte ayrıca borcun kısmen kabulü
  taranır (m.170/a-3). İmza itirazının geri alınması her borçlu tipinde
  taranır.
- **Sık atlanan:** kötü niyet tazminatı istemi (m.169/a-6, m.170/4) yoksa
  uyarı. Takibin geçici olarak durdurulması istemi yoksa **risk notlu** uyarı
  (m.169/a-2, m.170/2 takdiri; reddedilen itirazda tazminat m.169/a-6, imzada
  para cezası m.170/3) — istem zorunlu unsur değil, avukatın risk kararıdır.

### gecikmis-itiraz (İİK m.65)
- **Zorunlu unsurlar:** icra mahkemesi (itirazı icra mahkemesi inceler —
  m.65/3); takip dosyası; mani (mazeret) ve borçlunun kusursuzluğu (m.65/1);
  **maninin kalktığı günün tarihi** (üç günlük sürenin başlangıcı — m.65/2);
  mazereti gösteren deliller; itiraz ve sebepleri; harç ve masraf (m.65/2 —
  aynı dilekçede ödenir); takibin tatili/durdurulması istemi; tarih ve imza.
- **Süre bağlantısı:** m.65/2 — maninin kalktığı günden üç gün; m.65/1 —
  paraya çevirme bitinceye kadar.
- **Müvekkil-aleyhi eksen:** borçlu.

### itirazin-kaldirilmasi (İİK m.68, m.68/a)
- **Zorunlu unsurlar:** icra mahkemesi; takip dosyası; alacaklı ve borçlu;
  itirazın tebliğ tarihi; dayanak belgenin niteliği (m.68/1 belgesi ya da
  m.68/a imza incelemesi); kesin ya da geçici kaldırma talebi; deliller; tarih
  ve imza.
- **Süre bağlantısı:** m.68/1 ve m.68/a-1 — itirazın tebliğinden altı ay;
  geçerse aynı alacak için yeniden ilamsız takip yapılamaz.
- **Müvekkil-aleyhi eksen:** alacaklı.
- **Sık atlanan:** **icra inkâr tazminatı istemi** yoksa uyarı — m.68 son
  fıkra ve m.68/a son fıkra tazminatı "diğer tarafın talebi üzerine" bağlar:
  istenmezse hükmedilmez. Kanun istemi dilekçenin zorunlu içeriği yapmadığı
  için kapı bloklamaz; istemeyi unutmak müvekkil kaybı olduğu için uyarır.

### itirazin-iptali (İİK m.67; dava — HMK m.119)
- **Zorunlu unsurlar:** HMK m.119 dava dilekçesi unsurları (mahkeme, davacı
  ve davalı, adres ve davacının TCKN/VKN'si, **dava değeri**, sıra numaralı
  vakıalar ve deliller, hukuki sebepler, talep sonucu, imza); takip dosyası;
  itirazın tebliğ tarihi; itirazın iptali ve takibin devamı talebi; uyuşmazlık
  ticariyse **dava şartı arabuluculuk** son tutanağı (TTK m.5/A-1 itirazın
  iptalini açıkça sayar). Ticari sinyal bilinçli olarak **dardır**: "ticari
  dava/iş/ilişki/defter", tacir, cari hesap ve kambiyo senedi (bono, çek,
  poliçe — TTK'da düzenlendiği için ticari davadır, TTK m.4/1-a); tek bir
  "A.Ş." unvanı ya da "fatura" kelimesi yetmez. "Ticari dava değildir",
  "tüketici" ya da "dava şartı kapsamında değildir" beyanı koşulu kaldırır.
- **Süre bağlantısı:** m.67/1 — itirazın tebliğinden bir yıl. Süre geçerse
  genel hükümlere göre alacak davası hakkı saklıdır (m.67/5).
- **Müvekkil-aleyhi eksen:** alacaklı (davacı konumu).
- **Sık atlanan:** başlıkta icra mahkemesi yazılmışsa uyarı — itirazın
  iptali genel mahkemede açılır. **İcra inkâr tazminatı istemi** yoksa uyarı
  (m.67/2: diğer tarafın talebi üzerine, hükmolunan meblağın yüzde
  yirmisinden az olmamak üzere — istenmezse hükmedilmez).

### menfi-tespit (İİK m.72; istirdat dahil)
- **Zorunlu unsurlar:** HMK m.119 unsurları (dava değeri dahil); takiple
  bağlantı (dosya ya da "takipten önce" beyanı); borçlu olunmadığına ilişkin
  vakıa ve deliller; borçlu olunmadığının tespiti (istirdatta iade) talebi;
  istirdatta **ödeme tarihi** — ödeme olayının yanında ("ödeme emri" tarihi bu
  unsuru karşılamaz); ticari uyuşmazlıkta dava şartı arabuluculuk (TTK
  m.5/A-1 menfi tespit ve istirdatı sayar; dar sinyal ve istisna yukarıdaki
  gibi).
- **Süre bağlantısı:** menfi tespitin kendine özgü dava süresi yok; istirdat
  ödeme tarihinden bir yıl (m.72/7).
- **Müvekkil-aleyhi eksen:** borçlu — **bu tipte borçlu DAVACI konumundadır**;
  kapı tarama eksenini buna göre çevirir (davalı kalıbı "davanın kabulüne"
  burada borçlunun kendi talebidir, sinyal sayılmaz).
- **Sık atlanan:** ihtiyati tedbir istemi (takipten önce açılan davada yüzde
  on beşten az olmayan teminatla takibin durdurulması — m.72/2; takipten sonra
  takip durdurulamaz, aynı teminatla paranın alacaklıya ödenmemesi istenir —
  m.72/3) ve kötü niyet tazminatı istemi (m.72/5, talep üzerine, yüzde
  yirmiden az olamaz) yoksa uyarı.

### haciz-talebi (İİK m.78)
- **Zorunlu unsurlar:** icra dairesi; takip dosyası; haczi istenen mal, hak
  ya da alacak; takibin kesinleştiği (ödeme emri süresi geçti ya da itiraz
  kaldırıldı — m.78/1); haciz istemi; tarih ve imza.
- **Süre bağlantısı:** m.78/2 — haciz isteme hakkı ödeme emrinin tebliğinden
  bir yıl geçmekle düşer (itiraz/dava ve taksit sözleşmesi süresi sayılmaz).

### satis-talebi (İİK m.106, m.110)
- **Zorunlu unsurlar:** icra dairesi; takip dosyası; haczedilen mal ve haciz
  tarihi; **kıymet takdiri ve satış giderlerinin peşin yatırılması** (m.106/3;
  yatırılmazsa satış talebi vaki olmamış sayılır — m.106/5); sicile kayıtlı
  motorlu araçta muhafaza, kıymet takdiri ve satışın birlikte istenmesi
  (m.106/4); satış istemi; tarih ve imza.
- **Süre bağlantısı:** m.106/1 — hacizden itibaren bir yıl (7343 sayılı
  Kanunla taşınır/taşınmaz ayrımı kalktı); süresinde istenmezse haciz kalkar
  (m.110/1).

### haciz-ihbarnamesi-itiraz (İİK m.89 — üçüncü kişi)
- **Zorunlu unsurlar:** icra dairesi (itiraz yazılı ya da sözlü icra
  dairesine yapılır — m.89/2); takip dosyası; ihbarname (birinci/ikinci/
  üçüncü) ve **tebliğ tarihi**; itiraz sebebi (borcun olmadığı, malın yedinde
  bulunmadığı, ödendiği …); talep; tarih ve imza.
- **Süre bağlantısı:** m.89/2-3 — ihbarnamenin tebliğinden yedi gün; ikinci
  ihbarname yedi gün; üçüncü bildirimde on beş gün içinde ödeme ya da menfi
  tespit davası ve dava belgesinin yirmi gün içinde icra dairesine teslimi.
  Süresinde itiraz edilmezse mal yedinde ya da borç zimmetinde sayılır.
- **Müvekkil-aleyhi eksen:** üçüncü kişi (`--taraf ucuncu-kisi`) — bu tipte
  itirazdan vazgeçme/geri alma taranır (borcu zimmetinde saydırır, m.89/3).
- **Dürüstlük kuralı (kapıya işlendi):** itiraz gerçeğe aykırı olamaz —
  alacaklı cevabın aksini ispatlarsa üçüncü kişi İİK m.338/1'e göre (üç aydan
  bir yıla kadar hapis) cezalandırılır ve tazminata mahkûm edilebilir
  (m.89/4). Bu yüzden üçüncü kişinin borçluya borcu olduğunu ya da yedindeki
  malın borçluya ait olduğunu söyleyen **dürüst beyan bu tipte BLOK değil
  istişari uyarıdır** (kabul edilen kısmın kapsamı müvekkille yazılı teyit
  edilir). Aynı cümle istihkak davasında müvekkili bitirir ve orada BLOK
  kalır.

### kiymet-takdiri-sikayet (İİK m.128/a)
- **Zorunlu unsurlar:** raporu düzenleten icra dairesinin bulunduğu yer icra
  mahkemesi; takip dosyası; rapor ve **tebliğ tarihi**; somut değer itirazı
  (gerekçe, emsal); yeniden bilirkişi incelemesi ve **masraf ile ücretin
  şikâyetten itibaren yedi gün içinde yatırılması** (yatırılmazsa şikâyet
  kesin olarak reddedilir — m.128/a-1); talep; tarih ve imza.
- **Süre bağlantısı:** m.128/a-1 — raporun tebliğinden yedi gün; ayrıca
  masraf için şikâyetten yedi gün. Kararlar kesindir.

### ihalenin-feshi (İİK m.134/2)
- **Zorunlu unsurlar:** icra mahkemesi (şikâyet yolu); takip dosyası ve
  ihale tarihi; talep edenin m.134/2'de sayılan sıfatı (satış isteyen
  alacaklı, borçlu, mahcuzun resmî sicilinde kayıtlı ilgili, sınırlı ayni hak
  sahibi, pey süren); **yurt içinde adres**; yolsuzluk sebepleri; **menfaat
  ihlali** (m.134'e göre ihalenin feshini
  isteyen, yolsuzluk sonucu kendi menfaatinin zarar gördüğünü ispatla
  yükümlüdür); ihalenin feshi talebi; tarih ve imza.
- **Süre bağlantısı:** m.134/2 — ihale tarihinden yedi gün; satış ilanı tebliğ
  edilmemişse ya da esaslı hata/fesada sonradan vakıf olunmuşsa ıttıladan,
  her hâlde ihalenin elektronik satış portalında ilanından bir yıl.
- **Sık atlanan:** pey süren gibi listede adı geçmeyen ilgili için ihale
  bedelinin yüzde beşi teminat ve nispi harcın yarısı peşin (m.134/3-4;
  eksikse iki haftalık kesin süre, sonra ret — 7571 sayılı Kanun eki) yoksa
  uyarı. Talep esastan reddedilirse ihale bedelinin yüzde onuna kadar para
  cezası riski vardır (m.134/5) — strateji kararı (`oa-strateji`).

### icra-sikayet (İİK m.16)
- **Zorunlu unsurlar:** icra mahkemesi; takip dosyası; şikâyet olunan icra
  dairesi işlemi; **öğrenme ya da tebliğ tarihi** (yalnız m.16/2'deki süresiz
  hâllerde aranmaz; süre öğrenmeden işlediği için "tebliğ edilmemiştir"
  beyanı burada unsuru kaldırmaz); kanuna aykırılık ya da olaya uygunsuzluk
  gerekçesi; işlemin iptali ya da düzeltilmesi talebi; tarih ve imza.
- **Süre bağlantısı:** m.16/1 — işlemin öğrenildiği tarihten yedi gün; bir
  hakkın yerine getirilmemesi ya da sebepsiz sürüncemede bırakılması hâlinde
  her zaman (m.16/2). Mevcut `oa-sure` kuralı: `iik_sikayet`.

### istihkak-davasi (İİK m.96-97, 97/a — üçüncü kişi)
- **Zorunlu unsurlar:** icra mahkemesi; davacı (üçüncü kişi) ve davalılar;
  adres ve TCKN/VKN; dava değeri; takip dosyası ve haciz (tarih/tutanak);
  **başlangıç olayının tarihi** (mahkeme kararının tefhim/tebliği ya da hacze
  ıttıla); **mülkiyet karinesine karşı** malın nasıl iktisap edildiği ve
  borçlunun yanında neden bulunduğu (m.97/a: istihkak davacısı bunları
  göstermek ve ispat etmekle yükümlüdür); deliller; istihkakın kabulü ve
  haczin kaldırılması talebi; tarih ve imza.
- **Süre bağlantısı:** m.97/6 — takibin devamı kararının tefhim ya da
  tebliğinden yedi gün (aksi hâlde iddiadan vazgeçilmiş sayılır); m.97/9 —
  iddia imkânı verilmemiş üçüncü kişi için hacze ıttıladan yedi gün; m.96/3 —
  istihkak iddiası ıttıladan yedi gün.
- **Müvekkil-aleyhi eksen:** üçüncü kişi.
- **Sık atlanan:** takibin talikı (tedbir) istemi yoksa uyarı (m.97/1, 97/9).
- **Karşı yön:** alacaklı vekili, istihkak iddiasına icra dairesinin verdiği
  **üç günlük** mühlette itiraz eder; susarsa iddiayı kabul etmiş sayılır
  (m.96/2) — bu kısa dilekçe `icra-usul` tipiyle denetlenir.

### icra-ceza-sikayet (İİK m.76, 337/a, 338, 340, 344; usul m.347-351)
- **Zorunlu unsurlar:** icra (ceza) mahkemesi; şikâyetçi alacaklı, borçlu ve
  adres; takip dosyası; fiil ve dayanak madde (mal beyanında bulunmama için
  tazyik m.76, ticareti terk ve m.44 beyanı m.337/a, gerçeğe aykırı beyan
  m.338, ödeme şartını ihlal m.340, nafaka kararına uymama m.344); öğrenme
  tarihi (öğrenme olayının yanında) ve fiil tarihi; **deliller** (şikâyetçi
  dilekçesinde gösterdiği delillerle bağlıdır — m.351/1); tazyik hapsi ya da
  cezalandırma talebi; tarih ve imza.
- **Süre bağlantısı:** m.347 — fiilin öğrenildiği tarihten üç ay, her hâlde
  fiilden bir yıl (hak düşürücü).
- **Müvekkil-aleyhi eksen:** alacaklı (şikâyetten vazgeçme dahil).
- **Usul notu:** şikâyetçi duruşmaya gelmez ve vekil de göndermezse şikâyet
  hakkı düşer (m.349) — celse takvimi `oa-sure`/defterde izlenir.

### icra-usul (İİK m.33, 36, 71, 78, 96/2, 111 …)
- **Zorunlu unsurlar:** icra dairesi ya da icra mahkemesi; takip dosyası;
  talep konusu ve dayanak madde; talep; tarih ve imza. Koşullu olarak: tehir-i
  icrada kanun yolu başvurusu ile depo/teminat (m.36/1); icranın geri
  bırakılmasında icra emrinin tebliğ tarihi, itfa/imhal/zamanaşımı ve —
  yalnız itfa/imhalde — resmî ya da onaylı belge (m.33/1; zamanaşımında belge
  koşulu yoktur); istihkak iddiasına itirazda icra dairesi bildiriminin tarihi
  (m.96/2 — üç günlük mühlet, susma kabul sayılır).
- **Süre bağlantısı:** koşula göre m.33/1 (yedi gün), m.96/2 (üç gün), m.78/2
  (bir yıl); icra mahkemesi kararına istinaf m.363 (mevcut `oa-sure` kuralı:
  `iik_istinaf`).
- **Sık atlanan:** taahhüt/taksit metninde, makbul sebep olmadan ödeme şartını
  ihlal eden borçlu için üç aya kadar tazyik hapsi (m.340) uyarısı — borçlu
  vekili müvekkili yazılı bilgilendirir.

## 3. Süre bağlantısı ilkesi (süre HESABI `oa-sure`'ündür)

- Kapının **[S] SÜRE BAĞLANTISI** bölümü, tipin bağlı olduğu maddeyi yazar ve
  `oa-sure/scripts/sure_kurallari.json` içinde o maddeyi taşıyan kuralı
  **çalışma anında** arar. Bulursa kural kimliğini basar; bulamazsa
  "TEYİT BEKLİYOR — `oa-sure`'de bu madde için kural yok" der. Bu bölüm
  **asla bloklamaz**; süreyi hesaplamaz, yalnız hangi kurala bağlanacağını
  gösterir.
- Kural yoksa süre **elle hesaplanmaz**; avukat teyidi alınır ve belirsizlikte
  en erken son gün esas alınır (ailenin temkin kuralı).
- **[A]'da süre İFADESİ değil süre başlangıcının TARİHİ aranır.** "Yedi gün
  içinde" cümlesi dilekçenin yasal içeriği değildir; süresinde başvurunun
  dilekçedeki belgesi başlangıç olayının (tebliğ, öğrenme, maninin kalkması,
  ödeme, tefhim) tarihidir. Tarih olayın **yanında** aranır (olaydan sonra 80,
  önce 100 karakter — Türkçede tarih çoğu kez fiilden önce gelir); belgenin
  başka yerindeki imza tarihi bu unsuru karşılamaz. Usulsüz tebliğde muhatabın
  tebliğe muttali olduğunu beyan ettiği tarih tebliğ tarihi sayılır (Tebligat
  K. m.32) — öğrenme tarihi unsuru karşılar. Tebliğ henüz yapılmamışsa
  ("tebliğ edilmemiştir/edilmeden") tarih yazılamaz; bu açık beyan tarih
  unsurunu kaldırır (tebliğden önce başvurmak müvekkilin hakkıdır). İstisna
  yalnız olumsuz çekimdir: "tebliğ edilmesi" ad-fiili istisna değildir.
- İcra mahkemesine arz edilen işler ivedidir (İİK m.18/1); adli tatilde
  süreler uzamaz (HMK m.103/1-h — 5 Ekim 2026 Yargı PRO analizi doğrulama
  kaydı; Yargıtay 12. HD içtihadıyla teyitli, yetenek denetimi bulgusu Y-01).
  Süre motorundaki bu düzeltme `oa-sure` tarafındadır.

## 4. Taraf sıfatları ve müvekkil-aleyhi tarama (`--taraf`)

- `alacakli`: davacı ekseni + işçi-yanı iş hukuku kalıpları + icra alacaklısı
  kalıpları (alacağın tahsil edildiğinin/ödendiğinin kabulü, takipten feragat,
  haczin kaldırılmasına muvafakat, alacağın zamanaşımına uğradığının kabulü,
  istihkak iddiasının kabulü, şikâyetten vazgeçme).
- `borclu`: davalı ekseni + işveren-yanı iş hukuku kalıpları + icra borçlusu
  kalıpları (ödeme emrine itiraz etmeme, itirazdan vazgeçme ya da geri alma,
  takibin kesinleştiğinin kabulü, borçlu olunduğunun kabulü, borcun tamamen
  kabulü, imza itirazından vazgeçme, birinci ağızdan "kabul ettik/
  etmekteyiz"). Kanunun kendi terimi olan "imzası ikrar edilmiş belge" (m.68/1,
  m.169/a-1) ikrar sayılmaz.
- `ucuncu-kisi`: davacı ekseni + üçüncü kişi kalıpları (borçluya borcun
  bulunduğunun ya da malın borçluya ait olduğunun kabulü, istihkak
  iddiasından vazgeçme).
- **Tipe göre eksen çevrimi:** `menfi-tespit` tipinde borçlu davacı, alacaklı
  davalı konumundadır (davalı ekseninin "davanın kabul" kalıbı borçlunun kendi
  talebidir; esasa ilişkin ikrar kalıpları korunur). `kambiyo-itiraz` tipinde
  borçlu ekseni borcun **kısmen** kabulünü de tarar (m.170/a-3); ilamsız
  takipte kısmi kabul meşru strateji olduğundan orada taranmaz.
  `haciz-ihbarnamesi-itiraz` tipinde üçüncü kişinin borç/mal beyanı BLOK değil
  uyarıdır (yukarıda dürüstlük kuralı); itirazdan vazgeçme ise BLOK'tur.
- **İki katmanlı kalıp:** geniş kalıp ±70 karakterlik olumsuzlama
  korumasıyla çalışır ("kabul anlamına gelmemek kaydıyla" sinyal üretmez).
  Çekimli olumlu yüklemle biten ikrarlar ("itirazımızdan vazgeçiyoruz",
  "borcun tamamını kabul ediyoruz") ayrıca `(?#kesin)` kalıbıyla aranır ve bu
  pencereden muaftır: komşu "aksi/değil/redd" sözcüğü gerçek bir ikrarı
  BİLGİ'ye düşüremez. Ortaç ("kabul ettiğimiz anlamına gelmez") ve olumsuz
  çekim ("vazgeçmiyoruz", "vazgeçmeyeceğiz") kesin kalıba girmez; olumlu
  "-mek/-mekte" biçimleri ("vazgeçmek istiyoruz", "vazgeçmekteyiz") yakalanır.
  Yanlış pozitifi avukat gözü eler; yanlış negatif müvekkili batırır.
- **Entegrasyon notu:** `oa-kontrol/scripts/teslim_paketi.py` `--taraf`
  seçenekleri bu üç sıfatı henüz tanımıyor (o dosya bu paketin alanı dışında;
  ana ajana raporlandı). O güne kadar teslim zincirinde alacaklı için
  `--taraf davaci`, borçlu için `--taraf davali` verilir; icra kalıplarının
  tamamı için `dilekce_denetim.py` doğrudan `--taraf alacakli|borclu|ucuncu-kisi`
  ile koşulur.

## 5. Okunan resmî metinler (Yargı PRO MCP, 2026-10-05)

`mevzuat_getir` (mevzuatgov:kanun:3:2004 — İİK): m.16, m.18, m.32, m.33,
m.33/a, m.36, m.58, m.62, m.65, m.66, m.67, m.68, m.68/a, m.71, m.72, m.76,
m.78, m.89, m.96, m.97, m.97/a, m.106, m.110, m.111, m.111/a, m.128/a, m.134,
m.142, m.167, m.168, m.169, m.169/a, m.170, m.170/a, m.269-269/d, m.337/a,
m.338, m.340, m.344, m.347, m.349, m.350, m.351. (mevzuatgov:kanun:5:6102 —
TTK) m.4, m.5/A, m.776, m.777. (mevzuatgov:kanun:3:7201 — Tebligat K.) m.32.
(mevzuatgov:kanun:5:6100 — HMK) m.119, m.127, m.317, m.342. m.69
(borçtan kurtulma, yedi gün ve yüzde on beş depo) ve HMK m.103/1-h için
kaynak: 5 Ekim 2026 Yargı PRO analizinin resmî metin doğrulama kaydı (aynı
MCP araçlarıyla).

## 6. Bilinçli olarak bu turda yapılmayanlar

- Tasarrufun iptali davasının davacı yanı (İİK m.277-284), sıra cetveline
  itiraz davası (m.142), iflas yolu, rehnin paraya çevrilmesinin ayrıntısı ve
  borçtan kurtulma davası (m.69) için ayrı tip açılmadı; bunlar `dava`
  tipiyle ve bu cetvelin genel ilkeleriyle yazılır.
- Harç, gider avansı, inkâr tazminatı ve depo tutarları hesaplanmaz (oran ve
  tarife bu parçada teyit edilmez — anayasa m.4).
- Kapı içtihat atfı üretmez; icra içtihadı `oa-ictihat` zincirinden gelir.

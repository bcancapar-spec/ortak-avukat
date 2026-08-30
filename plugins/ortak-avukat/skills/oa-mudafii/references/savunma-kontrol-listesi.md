# Ceza Savunması Kontrol Listeleri (oa-mudafii)

Bu dosya, evreye göre savunma kontrol listelerini, unsur-denetim şablonunu ve müvekkil-lehine
argüman bankasını taşır. Madde numaraları **başlangıç çıpasıdır**; kullanım anında Mevzuat/Yargı
MCP'den teyit edilir (`oa-ictihat`). Sayımlar **örneklemdir**, kapsamı daraltmaz.

## İçindekiler
1. Soruşturma evresi kontrol listesi
2. Kovuşturma evresi kontrol listesi
3. Kanun yolu kontrol listesi
4. Unsur-denetim şablonu (maddi + manevi)
5. Müvekkil-lehine argüman bankası

---

## 1. Soruşturma evresi (şüpheli müdafiliği)

- **İfade/sorgu hakları (CMK m.147):** susma hakkı; müdafi yardımı; isnadın bildirilmesi;
  lehe delil toplanmasını isteme; yakınına haber verme. Müdafi yokken alınan ifade hükme
  esas alınamaz (m.148/4).
- **İfade alma yasağı (m.148):** işkence, ilaç, yorma, aldatma, cebir/tehdit, vaat ile
  alınan beyan rızaya dayalı olsa da delil sayılmaz.
- **Gözaltı (m.91):** süre, sebep, ölçülülük; gözaltına itiraz (m.91/5) Sulh Ceza Hâkimliği.
- **Tutukluluk (m.100-101):** kuvvetli suç şüphesi + tutuklama nedeni (kaçma/karartma) +
  ölçülülük; adli kontrol (m.109) öncelikli; tutuklamaya/temadiye **itiraz** (m.101/5, m.267).
- **Arama/elkoyma (m.116 vd.):** karar/onay var mı; sınırları aşıldı mı; hukuka aykırı arama
  → delil yasağı.
- **Müdafiin dosya inceleme yetkisi (m.153):** kısıtlama kararı var mı, kapsamı.
- **Soruşturmanın gizliliği (m.157).**
- **Lehe delil talebi (m.160/2):** Cumhuriyet savcısı şüphe lehine delili de toplamakla
  yükümlü; toplanmayan belirleyici lehe delil eksik soruşturmadır.
- **KYOK'a itiraz (m.173):** kovuşturmaya yer olmadığı kararı müvekkil aleyhineyse — değil;
  müşteki/katılan tarafıysak — tebliğden **iki hafta**, Sulh Ceza Hâkimliği.
- **Uzlaştırma (m.253) / önödeme (TCK m.75) / etkin pişmanlık:** uygulanabilir mi (lehe çıkış).

## 2. Kovuşturma evresi (sanık müdafiliği)

- **İddianamenin iadesi sebepleri (CMK m.174):** unsur/delil eksikliği, suç vasfı,
  ön ödeme/uzlaştırma yapılmaması.
- **Tensip ve davetiye:** meşruhatlı davetiye usulüne uygun mu; tebligat sağlıklı mı.
- **Sorgu (m.191):** isnat, haklar, susma; ek savunma hakkı (m.226 — vasıf değişiminde).
- **Doğrudan doğruyalık (m.217/1):** mağdur/tanık huzurda dinlendi mi; dinlenmeyen beyana
  dayanıldı mı; ulaşılamayan tanıkta SEGBİS/istinabe tüketildi mi, m.211 okuması yapıldı mı.
- **Tanık/mağdur (m.43 vd., m.236):** mağdur beyanı menfaat/atfı cürüm yönünden tartıldı mı.
- **Bilirkişi (m.63 vd.):** dijital/ses/imza aidiyeti incelendi mi; rapora itiraz.
- **Tevsi tahkikat:** toplanmayan lehe delil için talep; reddi savunma hakkı kısıtlaması
  (m.289/1-h) olabilir — tutanağa geçir.
- **Esas hakkında mütalaaya karşı beyan; son söz sanığındır (m.216/3)** — vareste değilse
  bizzat sanığa sorulmalı.
- **Hüküm türü (m.223):** beraat (2-a unsur yok / 2-c sübut yok), CYO (m.223/3-4), düşme,
  HAGB (m.231), erteleme (TCK m.51), seçenek yaptırım (TCK m.50).

## 3. Kanun yolu (sanık lehine)

> **SÜRE DEĞERİ İKİ YERDE TUTULMAZ (A-2, v0.5.14).** Aşağıdaki süreler
> **başlangıç çıpasıdır**; bağlayıcı tek kaynak `oa-sure/scripts/sure_kurallari.json`
> tablosu ve `hesapla_sure.py` hesabıdır (`--kural cmk_istinaf|cmk_temyiz|cmk_itiraz`).
> Bu listedeki bir değer JSON tablosuyla çelişirse **JSON esastır** ve çelişki
> `oa-usta`'ya bildirilir — ikiz liste kayması bu dosyanın geçmişteki tek P0'ıdır
> (m.268'in mülga süre değeri SKILL.md'de düzeltilirken burada altı hafta yaşadı).

- **İstinaf (CMK m.272-281):** süre **iki hafta** (m.273/1 — "hükmün gerekçesiyle
  birlikte tebliğ edildiği tarihten itibaren"); tutuklu sanıkta m.263 saklıdır.
  m.273/2 (eski "yedi günlük" beyan rejimi) **7499 s.K. ile mülgadır.** Somut/gerekçeli
  sebep şart değildir (m.273/4 — sanık ve katılan için sebep göstermemek incelemeye
  engel değil); BAM usul **ve** esas inceler; m.289 kesin hukuka aykırılık re'sen gözetilir.
  **Kapalı yol denetimi (m.272/3):** hapisten çevrilme hâriç belirli adlî para cezası
  mahkûmiyetleri, üst sınırı belirli günü geçmeyen adlî para cezası suçlarından beraat
  hükümleri ve **kanunda kesin olduğu yazılı** hükümler istinafa kapalıdır — parasal
  sınır rakamı hafızadan yazılmaz, kullanım anında MCP'den çekilir.
- **HAGB → kanun yolu (m.231/12 — Değişik: 16/7/2026-7589/15 md.):** hüküm birebir
  *"**272 nci maddenin üçüncü fıkrası hükümleri saklı kalmak üzere**, hükmün
  açıklanmasının geri bırakılması kararına karşı istinaf yoluna başvurulabilir"*.
  Yani istinaf **koşulsuz açık değildir**: önce m.272/3 kapalılık denetimi yapılır.
  BAM'ın kararları hakkında m.286 uygulanır; HAGB'yi ilk derece sıfatıyla BAM veya
  Yargıtay vermişse (yine m.272/3 saklı) temyiz yolu açılır. İnceleme **usul ve
  esasa ilişkin hukuka aykırılıklar** yönündendir. **7499 s.K. metni artık yürürlükte
  değildir** — 7589 öncesi kaleme dayanan her çıkarım yeniden kurulur.
- **Temyiz (m.286-307):** süre **iki hafta** — m.291/1, gerekçeli kararın tebliğinden.
  Temyiz edilebilirlik (m.286/2-3 katalogları) **önce** denetlenir. (Tutukluda m.263 saklı;
  m.291/2 7499 s.K. ile **mülga**); maddi vakıa değil hukuka aykırılık ekseni.
- **İtiraz (m.267-271):** kural **iki hafta**; başlangıç, ilgililerin kararı **öğrendiği** gündür (m.268/1).
  Kapsam: tutukluluk, adli kontrol ve kanunun itiraza tabi tuttuğu kararlar; m.263 saklıdır.
  **Başlangıç rejimi istinaf/temyizden FARKLIDIR:** itirazda başlangıç *öğrenme
  günüdür* (m.35), istinaf/temyizde *gerekçeli kararın tebliği*. Aynı dosyada iki
  süre tek formülle hesaplanmaz.
- **⚠ ADLİ TATİL — CEZA REJİMİ AYRIDIR (CMK m.331/4):** *"Adlî tatile rastlayan
  süreler işlemez. Bu süreler tatilin bittiği günden itibaren **üç gün** uzatılmış
  sayılır."* Ceza sürelerine hukuk yargısının **HMK m.104** rejimi (bir hafta)
  UYGULANMAZ — aradaki fark bir kanun yolunu süreden reddettirir. Tatil dönemi
  m.331/1'dedir; m.331/2-3 uyarınca **soruşturma, tutuklu işler ve ivedi hususlar**
  tatilde de yürür. Hesabı `hesapla_sure.py` ile yaptır ve çıktının hangi yargı
  koluna göre uzatma uyguladığını **gözle doğrula**.
- **AYM bireysel başvuru (6216 m.45 vd.):** m.47/5 — başvuru yollarının tüketildiği
  (yol öngörülmemişse ihlalin öğrenildiği) tarihten itibaren **otuz gün**; haklı
  mazerette mazeretin kalktığı tarihten **onbeş gün**. İhlal eksenleri: adil
  yargılanma/gerekçeli karar/silahların eşitliği, masumiyet karinesi, kişi hürriyeti.
- **Kanun yararına bozma (m.309) / yargılamanın yenilenmesi (m.311).**
- **⛓ TUTUKLU MÜVEKKİL — SÜREYİ KESEN KANAL (CMK m.263):** tutuklu şüpheli/sanık,
  **zabıt kâtibine beyanla veya bulunduğu ceza infaz kurumu ve tutukevi müdürüne
  beyanda bulunarak yahut dilekçe vererek** kanun yollarına başvurabilir; m.263/2'ye
  göre işlem yapıldığında *"kanun yolları için bu Kanunda belirlenen süreler
  **kesilmiş sayılır**"* (m.263/4). m.268/1, m.273/1 ve m.291/1'in üçü de
  "263 üncü madde hükmü saklıdır" der. İki yönlü kullan: (a) müvekkile bu kanal
  **ilk görüşmede** anlatılır; (b) "süre doldu" sonucuna varmadan önce kurum
  kaydı/tutanağı **celbedilir** — müvekkil süresinde başvurmuş olabilir.
- **Süre/tebliğ:** e-tebligat — 7201 m.7/a: elektronik yolla tebligat, muhatabın
  elektronik adresine **ulaştığı tarihi izleyen beşinci günün sonunda** yapılmış
  sayılır; UETS "okundu sayıldı" tarihi esas (erken açılma süreyi öne almaz).
- **KYOK'a itiraz (müşteki tarafındaysak — m.173/1):** kararın tebliğinden **iki hafta**,
  ağır ceza mahkemesinin bulunduğu yerdeki Sulh Ceza Hâkimliği.

## 4. Unsur-denetim şablonu

İsnat edilen her suç için doldur (eşleşmeyen satır = savunma ekseni):

| Unsur | Kanuni gereklilik | Dosyadaki vakıa | Eşleşme | İspat aracı | Boşluk/eksen |
|---|---|---|---|---|---|
| Fiil (hareket) | | | var/yok/şüpheli | belgeli/tanık/bilirkişi/yok | |
| Netice (varsa) | | | | | |
| İlliyet / objektif isnadiyet | | | | | (kesme: 3. kişi/mağdur kusuru) |
| Fail (bizzat mı?) | | | | | (fiili başkası mı işledi?) |
| Maddi konu / mağdur | | | | | |
| Manevi unsur (kast/taksir) | | | | | (bilme/özel kast ispatı?) |
| Nitelikli hâl | | | | | |
| Hukuka uygunluk / kusur | | | | | (m.24-34, hata m.30) |

Kural: **bir tek unsur bile "yok/şüpheli" ise** beraat (CMK m.223/2-a/c) önceliklidir;
"şüpheli" satırlar in dubio pro reo ile lehe doldurulur.

## 5. Müvekkil-lehine argüman bankası (örneklem)

- "İsnadın dayandığı beyan **huzurda dinlenmemiştir** (CMK m.217); doğrudan doğruyalık ihlali."
- "Belirleyici **lehe delil toplanmadan** (HTS/kamera/bilirkişi) hüküm kurulmuştur — eksik inceleme."
- "Suçun **maddi unsuru** (fiil/illiyet) müvekkil yönünden oluşmamıştır; fiili gerçekleştiren başkasıdır."
- "**Manevi unsur** (bilme/özel kast) somut delille kurulmamış, çıkarımla varsayılmıştır."
- "Dayanak beyan **menfaat sahibi/atfı cürüm** niteliğindedir; bağımsız, sınanmış delille desteklenmemiştir."
- "Dijital/ses delili **aidiyet yönünden doğrulanmamıştır** (adli bilişim yok)."
- "Olayla **eş zamanlı ilk beyan** ile sonraki beyan çelişmektedir; çağdaş beyan esas alınmalıdır."
- "Aynı olayda verilmiş **lehe karar** (takipsizlik/beraat) gerekçede değerlendirilmemiştir."
- "Hüküm gerekçesi iddianame/mütalaa **kopyasıdır** (CMK m.230, m.289/1-g — kesin hukuka aykırılık)."
- "Hukuka aykırı yöntemle elde edilen delil **dışlanmalıdır** (m.206/2-a, m.217/2, m.289/1-i)."
- "Sonradan/lehe kanun değişikliği veya AYM iptali **lehe** uygulanmalıdır (TCK m.7)."
- "Kademeli talep: öncelikle **beraat**; olmazsa eksik incelemenin giderilmesi için **bozma/yeniden yargılama**."

Her argüman, kullanımdan önce dosyanın somut vakıasına bağlanır ve dayandığı içtihat
`oa-ictihat` üzerinden resmî kaynaktan teyit edilir (tam künye + ilgili kısmın aynen alıntısı
+ davaya bağlayan açıklama — `oa-dilekce`).

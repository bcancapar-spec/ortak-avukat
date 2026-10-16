# Saha Karnesi — 307 sahası (v0.5.9.1)

**İş:** derdest bir tasarrufun iptali davasında ikinci cevap (beyan) dilekçesi.
**Tarih:** 22.08.2026 · **Süre:** 161 dakika · **Sürüm:** v0.5.9.1
**Yöntem:** üç kollu adli analiz (transkript + artefakt + mekanizma), her kol
ana analizciyi *çürütmekle* görevlendirildi; ardından bulgular tek tek elle
doğrulandı.

---

## 0. Baş cümle

Koşu yeşil teslim makbuzuyla kapandı, atıf zinciri fiziken kapalıdır ve
sistemin kendi kapıları gerçek kusurları yakaladı. **Ama koşu "temiz deney"
değildi ve makbuzdan sonra en kritik artefakt makbuzun dışında değişti.**
Karnenin en ağır bulgusu budur; en değerli bulgusu ise bu kusurun sistemin
kendi bıraktığı izlerden çıkmış olmasıdır.

## 1. Deney sınıfı: MÜDAHALELİ

Protokol "tek doğal prompt + sıfır müdahale" şartı koyuyordu. Ölçüm: **11
gerçek kullanıcı turu.** Sınıflandırma:

| Sınıf | Adet | Örnek |
|---|---|---|
| Görev promptu | 1 | işin tarifi |
| **Mekanik yönlendirme** | **2** | parçaların adıyla, slash komutuyla çağrılması |
| **Teslim sürtünmesi** | **5** | üretilen dosyanın yerinin tekrar tekrar sorulması |
| İçerik yönlendirmesi | 3 | usul tespiti sorusu, tonun sertleştirilmesi |

Mekanik-hijyen promptu hedefi **0** idi; ölçülen **7** (mekanik yönlendirme +
teslim sürtünmesi). İçerik yönlendirmeleri başarısızlık sayılmaz — o avukatın
işidir — ama ayrı sayılır.

## 2. Ölçülen tablo

| Ölçüm | Değer |
|---|---|
| Üretim | ~822 bin çıktı token · 271 araç çağrısı (161 kabuk, 69 hukuk MCP) |
| Bağlam | 154. dakikada sıkışma (özetleme) — koşu sonuna 7 dakika kala |
| Hook kanalı | 6 ayrı olay türü ateşledi; defterde 47 hook olayı |
| İçtihat triyajı | **45 damga: 44 LEHE + 1 ALEYHE-AYIRT**, 45'i tam-metin sınıfı |
| Döküm | 30 dosya (ham tam metinler) · muhakeme kaydı 27 ilgili-kısım |
| Makbuz zinciri | RED 05:46:09 → **YEŞİL 05:46:48** (exit 0, 8 kapı) |
| Dış çıktı | 40-UYAP dizini yeşil makbuzla birlikte doğdu |
| Alt-ajan dağıtımı | **0** (kural dosyası bunu "varsayılan" ilan etmesine rağmen) |

## 3. Çalışan taraf

**Atıf zinciri fiziken kapalı.** Teslim metnindeki içtihat künyelerinin tamamı
damgalı satır + tam-metin dökümü + ilgili-kısım muhakemesi olarak mevcut.
Uydurma künye yok. Kararlar listeden künyeyle değil, tam metinleri çekilerek
okundu ve damgalandı.

**Aleyhe farkındalığı stratejiyi şekillendirdi.** Müvekkil aleyhine olan karar
dilekçeye alınmadı, yalnız ayırt/çürütme bağlamında kullanıldı; ayrıca
cephanelikte tutulan bir başka aleyhe karar yüzünden **ana savunma ekseni
kaydırıldı**. Bu, kuralın kâğıtta değil sahada işlediğini gösterir.

**Fail-closed gerçek pozitif verdi.** Ayırt edemediği bir ibareyi kendi lehine
yorumlamak yerine kapı durdu ve 5 kalemlik avukat kararı listesi üretti. Defter
kapısı teslimi ayrıca iki kez durdurdu; kırmızı makbuz gerçekten exit 1 verdi.

**Bayat araç nöbetçisi çalıştı.** Üç açılışta bayat araç kuşağı adıyla bildirildi
ve altı dakika içinde onarıldı; sonraki koşularda uyarı düşmedi.

**Kayıpsızlık tuttu.** Bu karnenin en ağır bulguları, sistemin kendi tuttuğu
kayıtlardan çıktı. Kusurunu görünür bırakan bir sistem, gizleyenden ölçülemez
biçimde iyidir.

## 4. Kusurlar — ağırlık sırasıyla

### K1 (AĞIR) — Teslim ürünü makbuzun dışında değişti, mühür kırık

Avukatın UYAP'a yükleyeceği resmî adlı UDF, mühürlendiği andan **68 dakika
sonra** yeniden üretildi; mühür tazelenmedi ve bu pencerede deftere hiçbir olay
düşmedi. Mühür dosyasındaki özet ile dosyanın gerçek özeti **birbirini
tutmuyor**. Pratik anlamı: *sistemin belgelediği dosya ile yüklenecek dosya
aynı değil.*

### K2 (AĞIR) — Makbuz, teslim edilen ürünü kapsamıyor

Yeşil makbuzun ürün listesi yalnız dahilî çalışma adlı nüshayı sayıyor; resmî
adlı ürün kapsamın **hiç içine girmemiş**. Yani makbuz yeşil, ama yeşil olduğu
şey avukatın yükleyeceği dosya değil.

### K3 (AĞIR) — Parçalar kendiliğinden çağrılmadı; kök sebep bulundu

Yazım ve kontrol parçaları koşu boyunca modelce kendiliğinden çağrılmadı;
avukat ikisini de adıyla çağırmak zorunda kaldı. Kök sebep koddadır:
prompt kanalında **defter açıksa devir hatırlatması bilerek susturuluyor**
("gürültü disiplini"). Bu satırın altında yalnız uyarı blokları kalıyor;
"parça taklit edilmez, çağrılır" buyruğu ilk turdan sonra modele bir daha hiç
ulaşmıyor. Gürültüyü azaltmak için yapılan bir iyileştirme, tetiği sessizce
kaldırmış.

### K4 (ORTA) — Teslim sürtünmesi

Avukat üretilen dosyanın yerini **beş kez** sordu. Mutlak yol hiçbir kalıcı
artefakta yazılmıyor; makbuzdaki alan köke göreli. v0.5.9'un ilan ettiği
"sürtünmesizlik" ilkesi bu koşuda tutmadı.

### K5 (ORTA) — İçerik denetçisi alıntıyı kendi cümlemizden ayıramıyor

Müvekkil-aleyhi tarayıcısı, birebir Yargıtay alıntısının *içinde* geçen bir
ibareyi kendi beyanımız sanıp bloke etti. Model bunu aşmaya çalışmadı, kararı
gerekçesiyle avukata taşıdı — davranış doğru, kapı yanlış.

### K6 (HAFİF) — Ateşlemeyen kural

Kural dosyası alt-ajan dağıtımını "varsayılan, opsiyonel değil" ilan ediyor;
koşuda **sıfır kez** ateşledi. Ateşlemeyen kapı silinir kuralı gereği bu satır
ya dar kapsamla yeniden yazılmalı ya kaldırılmalıdır.

### K7 (HAFİF) — Kütük iki sayıcıya iki farklı sayı veriyor

Aynı künye kütüğü, farklı sayma yöntemleriyle farklı toplamlar verdi. Ölçüm
aracının kendisi belirsizse karne rakamları tartışmalı hâle gelir.

## 5. Doğrulanamayan iddia (dürüstlük kaydı)

Adli kollardan biri, yeşil makbuzun "zorlama" ile alındığını öne sürdü.
**Doğrulanamadı:** defterde ve kütükte böyle bir şerh bulunamadı. Doğrulanan
kısım şudur: kırmızı ve yeşil makbuz **aynı kaynak metnin özetini** taşıyor ve
aralarında 39 saniye var — yani belge değişmedi, açılan kapı defter bütünlüğü
kapısıydı. Bu meşru bir geçiştir, ama makbuzun yeşilliğinin bir bölümünün
belgeyi değil kayıt düzenini ölçtüğünü gösterir.

## 6. Ana analizcinin düzeltmesi

Koşu sırasında canlı olarak "tek doğal prompt, sıfır mekanik-hijyen promptu"
raporlandı. **Bu yanlıştı.** Gözlem dosya sistemi üzerinden yapılmış, transkript
sayılmamıştı; yokluk kanıtı, kanıtın yokluğuyla karıştırıldı. Doğrusu §1'dedir.
Vitrindeki ilgili bölüm bu karneyle birlikte düzeltilmiştir.

## 7. v0.5.10 onarım listesi

Her madde ölçülmüş bir kusura bağlıdır; kanıtsız madde yoktur.

| # | Kanıt | Onarım |
|---|---|---|
| 1 | K1 — mühür/dosya özeti uyuşmazlığı | Teslim ürünü değiştiğinde mühür zorunlu tazelensin; tazelenmemiş mühür sunumda "ask" doğursun |
| 2 | K2 — makbuz kapsamı eksik | Makbuzun ürün listesi dış-çıktı dizinindeki **tüm** teslim-sınıfı ürünleri kapsasın |
| 3 | K3 — devir buyruğu susuyor | Prompt kanalında "parça çağrılır, taklit edilmez" buyruğu defter açıkken de akmaya devam etsin (kısa biçimde) |
| 4 | K4 — konum beş kez soruldu | Yeşil makbuzda ve teslim notunda ürünün **mutlak yolu** yazılsın |
| 5 | K5 — alıntı-içi yanlış pozitif | Denetçi alıntı bloklarını kendi beyandan ayırsın |
| 6 | K6 — ateşlemeyen kural | Alt-ajan maddesi dar kapsamla yeniden yazılsın veya kaldırılsın |

## 8. Alınmayan hüküm

**İçerik kabulü kaydedilmedi.** Dilekçenin hukuken tatmin edici olup olmadığı
avukatın hükmüdür ve bu karne yazılırken henüz verilmemiştir. Bu boşluk bilerek
boş bırakılmıştır — doldurulmuş gibi gösterilmesi karneyi değersiz kılardı.

---

*Yöntem notu: n=1. Tek koşu kanıt değil gözlemdir. Bu karnenin amacı övünmek
değil, bir sonraki sürümün neyi onaracağını ölçüye bağlamaktır.*

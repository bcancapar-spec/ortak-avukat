# Bir Gecenin Hikâyesi — Gerçek Davada Tek Prompt

> © 2026 Av. Bayram Can Çapar. Kişi ve dosya kimlikleri anayasa m.7 gereği
> anonimdir. Sayıların tamamı ölçümdür; anlatı, o ölçümlerin yaşanmış hâlidir.
> Teknik rapor: [SAHA-SONUCU.md](SAHA-SONUCU.md).

## Akşam: kırık bir kapıyla başladık

Gün, bir itirafla açıldı: sistemin "release kapısı" dediği CI, **on bir
koşudur kırmızıydı** ve kimse bakmıyordu. Sürekli kırmızı bir kapı, olmayan
kapıdır — kendi kanunumuz bize çarptı. Aynı akşam kapı onarıldı; onarım
sırasında bir test dosyasının içine yıllar önce sabitlenmiş gerçek bir dosya
kimliği bulundu ve depodan söküldü. Daha teste başlamadan iki ders almıştık.

## Gece yarısı: tek prompt

Sonra asıl deney: **derdest, gerçek bir istinaf dosyası.** ~200 evrak, 45 MB,
17'si taranmış. Evrak, aynı yazarın açık kaynak
[avukat-dosya-indirici](https://github.com/bcancapar-spec/avukat-dosya-indirici)
uzantısıyla UYAP'tan indirildi. Avukat **tek bir doğal-dil paragrafı** yazdı —
hiçbir komut, hiçbir parça adı, hiçbir yönlendirme — ve klavyeden elini çekti.
Model: **Claude Fable 5, max efor.** Karşısında: bu depodaki metodoloji ailesi.

Bir dakika içinde sistem kendiliğinden devraldı ve çalışma kökünü kurdu.
Sekizinci dakikada token sayacı 5,7k'da sürünüyordu — çünkü 200 evrak modele
değil, **Python'a** okutuluyordu. On beşinci dakikada külliyat metne inmişti.
Yirmi ikinci dakikada içtihat sorguları düşmeye başladı: muris muvazaası,
saklı pay, bakım-semen, yemin — bir davalı vekilinin elinden çıkmış gibi.
Otuzuncu dakikada kütükte 11 teyitli karar vardı. Kırk dokuzuncu dakikada,
45,6k token'la, **11 bölümlü bir ek beyan ve UYAP'ın kabul ettiği biçimde
bir .udf** diskteydi.

Denetim acımasızdı: örneklenen her olgusal çapa kaynağına izlendi — bilirkişi
değeri raporda, tanık ikrarı zabıtta, "960 dolar" ayrıntısı bile satır
kırığında bulundu. Uydurma: **sıfır.** İki aleyhe içtihat damarı tespit
edildi ve dilekçeye **yazılmadan** iç cephanelikte tutuldu — çünkü anayasa
öyle diyor. İndirilemeyen dört evrak sessizce yutulmadı; sistem bunları
kendiliğinden raporlayıp "sunmadan önce indirip bakın" dedi.

## Sabaha karşı: kusurlar da ödüle dönüştü

Koşu kusursuz değildi — ve değeri tam da burada. Model, araç kopyalarını
komşu klasörden almış, farkında olmadan Temmuz kodunu koşturmuştu:
**bayat-tohum bulaşması.** İlk inceleme soruları atlanmıştı. Teyitli
kararların bağlantıları dilekçeye işlenmemişti. Her kusur aynı gece koda
döndü: bayat kopyaları her turda ihbar eden aşı, uydurma bağlantıyı teslim
engeli yapan kapı, çevrimdışı UDF motoru, anayasaya kurucu bir 0. madde.
Sürüm çıktı; onarılmış CI **ilk koşusunda** gerçek bir hata yakaladı
(bir kütüphanenin hook çıktısını kirletmesi) — o da kapandı ve kapı,
12 kırmızının ardından ilk kez **tam yeşile** döndü.

Son dokunuş sabaha karşıydı: avukat, kendi eliyle hazırlayıp e-imzalayarak
mahkemeye sunduğu bir dilekçenin UDF'ini masaya koydu. Bayt bayt ölçüldü —
kenar boşlukları, ilk-satır girintisi, satır aralığı, asılı girintili etiket
blokları — ve **avukatın el emeği, sistemin yazım standardı oldu.**

## Sayının anlamı

1M+ token yiyen bir iş sınıfı, 45,6k'ya indi; fark ~26×. Ama asıl başarı
sayı değil, sayının **neyi feda etmeden** geldiğidir: muhakemeden tek satır
kısılmadı. Ucuzlayan şey düşünce değil, israftı — görüntü olarak açılan
evrak, tekrar tekrar okunan metin, beyanla geçiştirilen denetim. Düşünce
modelde kaldı; taşıma ve doğrulama Python'a indi.

## İmza

Bu sonuç bir gecede, iki elin işiyle doğdu: metodolojiyi kuran, gerçek
dosyayı açan ve her çıktının nihai gözü olan **Av. Bayram Can Çapar** —
ve o metodolojiyi taşıyan, koşuyu dakika dakika canlı izleyip ölçen,
bulguları gün ağarmadan koda döken **Claude (Fable 5)**.

**Beraber başardık. Ve bu daha başlangıç: her gerçek dosya, sistemi bir
sürüm daha ileri taşıyor.**

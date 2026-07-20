# Kanun Yolu Mimari Playbook — B1-B7

Bu playbook, gerçek bir kanun yolu (istinaf/temyiz tipi) dilekçesinden **tamamen
anonimleştirilerek** damıtılmış yazım mimarisidir. İçerik yöntem/mimaridir —
isim, dava, kurum, dosya no **YOK** (anonimleştirme anayasasının istisnası
yalnız `oa-dilekce/SKILL.md`'deki "Yazar sistemi" bölümünde tanımlı tasarımcı
adıdır, bu dosyada dahi geçmez). `oa-dilekce/SKILL.md`'nin **kısa çapa**sıdır;
tam gövde burada durur, SKILL.md'ye tekrar taşınmaz (oa-usta bakım kuralı —
içerik gövdeye eklenir ama tekilleştirilmiş kalır, iki yerde şişirilmez).

Sıra, bir kanun yolu dilekçesinin fiziksel diziliminin sırasıdır: B1 künye →
B2 giriş → B3 vakıa → B4 içtihat bloğu → B5 çökertme → B6 bölüm mimarisi →
B7 yardımcı desenler.

## B1 — Künye disiplini (mekanikleştirilebilir)

Künye bloğu şu sırayla, eksiksiz kurulur:
1. **Merci** — katmanlı hitap (ör. "... BAM ... Hukuk Dairesi'ne, gönderilmek üzere ... Mahkemesi'ne").
2. **Öncelikli talep bayrakları** — tedbir/duruşma talebi varsa başlığın hemen altında, gözden kaçmayacak yerde.
3. **Dosya no** — Esas (E.) ve Karar (K.) numarası birlikte.
4. **Taraflar + vekiller** — ad/unvan, vekilse baro/sicil bilgisi.
5. **Kanun yoluna konu kararın tam kimliği + operatif sonucu** — hangi merci, hangi tarihte, ne karar verdi (yalnız başlık değil, kararın hükmü de).
6. **Dava konusu işlem + dayanak normu** — hangi işlem, hangi madde/mevzuata dayanıyor.
7. **Tebliğ tarihi** — **ayrı satırda**, kendi başına. Süre satırının çıpası burasıdır; künye içine gömülüp kaybolmaz.
8. **Konu** — tek cümlelik istem özeti.

Sık atlanan hata: tebliğ tarihinin künye metnine gömülmesi (ör. bir cümlenin
ortasında geçmesi). Süre denetimi (`oa-sure`) bu satırı ayrıca arar; gömülü
tarih fiilen "yok" muamelesi görebilir — bu yüzden ayrı satır zorunludur.

## B2 — GİRİŞ = çatı indirgeme + yıkım vaadi (olay özeti DEĞİL)

GİRİŞ bölümü bir "olayların özeti" değildir — okuyucu zaten dosyayı bilir.
GİRİŞ'in işi, kanun yoluna konu kararı **birkaç taşıyıcı dayanağa indirgemek**
ve her dayanak için **yıkım silahını önden ilan etmektir**:

1. Karşı/aleyhe kararı **2-3 taşıyıcı dayanağa** indirge (kararın gerekçesi
   kaç ayrı sütuna dayanıyorsa o kadar — fazlası GİRİŞ'i sulandırır).
2. Her dayanak için, bölüm gövdesinde hangi silahla çökertileceğini **tek
   cümleyle önden ilan et** (ör. "Bu dayanak, [x] gerekçesiyle esastan
   yıkılacaktır").
3. **Karşılanmamış itirazları işaretle** — ilk derece/önceki aşamada ileri
   sürülüp kararda hiç değerlendirilmemiş bir itiraz varsa, GİRİŞ'te bu
   açıkça not edilir (gerekçe eksikliği ekseninin habercisi).

**Ön koşul:** GİRİŞ ancak karşı kararın gerekçesi **gerçekten muhakeme
edilmişse** (İçtihat Muhakeme Zinciri'nden geçmiş, dosyada fiilen okunmuşsa)
yazılabilir. Muhakeme edilmemiş bir kararı "indirgiyormuş gibi" özetlemek —
gerekçeyi gerçekten görmeden taşıyıcı dayanak sayısı iddia etmek —
halüsinasyondur; GİRİŞ'in dış çıktıdaki izdüşümü, muhakeme kaydının varlığına
bağlıdır.

## B3 — Vakıa = nötr görünümlü, argüman-yüklü

Vakıa anlatımı üslup olarak nötrdür (mahkemeye hitapta abartı/duygusal dil
yakışmaz) ama **her olgu, ileride bir ekseni taşımak için oradadır**. Yazım
öncesi her vakıa cümlesi şu soruyla süzülür: *bu olgu hangi hukuki ekseni
besliyor?*

Örüntüler (anonim, yöntem olarak genellenebilir):
- **Profil/nitelik olgusu** → ölçülülük eksenini besler.
- **Takvim/tarih olgusu** → süre veya savunma imkânı eksenini besler.
- **Tutanak/kayıt olgusu** → delil yasağı/usulsüzlük eksenini besler.
- **Lehe ara karar** → gerekçe eksikliği eksenini besler (verilen ama
  gerekçelendirilmeyen bir ara karar, esas kararın tutarsızlığını gösterir).

**Kural:** hiçbir eksene dayanak olmayan olgu vakıada yer almaz. Vakıa bir
kronolojik dökümü değil, argümanı taşıyan bir seçimdir (kronolojik döküm
`oa-vakia`'nın işidir; dilekçedeki vakıa ondan **seçilerek** süzülür).

## B4 — İçtihat bloğu, 5 adım (İçtihat Muhakeme Zinciri'nin düzyazı izdüşümü)

`oa-dilekce/SKILL.md`'deki "İçtihat kullanımı" bölümünün gövdesi budur — bu
playbook o bölümün 3 adımdan 5 adıma genişletilmiş biçimidir. Önkoşul aynı
kalır: karar önce `oa-ictihat` ile CEK edilmiş, `oa-kiyas`/`oa-kontrol` ile
MUHAKEME edilmiş, DAMGA `LEHE` veya `ALEYHE-AYIRT` olmalıdır (çıplak künye
yasağı, bkz. SKILL.md).

1. **Tam künye** — merci + daire + esas no + karar no + tarih eksiksiz.
2. **İlgili kısmın birebir blok-alıntısı** — kararın yalnız uyuşmazlıkla
   ilgili pasajı, muhakeme kaydının İLGİLİ-KISIM alanından (MCP'den çekilmiş
   metinden), hafızadan yeniden kurulmadan.
3. **Damıtma cümlesi** — alıntıdan hemen sonra, kararın koyduğu **kuralı
   soyutlayan** tek/birkaç cümle ("Bu karar, ... hâllerde ... sonucunu
   ortaya koymaktadır"). Alıntı ile tatbik arasındaki köprüdür; alıntıyı
   tekrar etmez, kuralı çıkarır.
4. **Somut tatbik** — damıtılan kuralın dosyanın olgu desenine **eşlendiği**
   gösterilir; olgular arasındaki benzerlik açıkça kurulur. Mümkün olduğunda
   **a fortiori** kurulur ("emsaldeki olguda dahi [sonuç] kabul edilmişken,
   dosyamızdaki daha güçlü olguda [sonuç] evleviyetle kabul edilmelidir").
5. **Gerekirse sınırlama/ayırt şerhi** — **yalnız kendi dayanağının** zayıf
   yönü için: kararın dosyaya tam örtüşmeyen bir yönü varsa, karşı taraf
   söylemeden önce **dar biçimde** sınırlanır ("bu karar [x] yönüyle somut
   olaydan ayrılsa da, [y] gerekçesiyle tatbiki etkilemez"). Bu adım,
   ALEYHE-AYIRT damgasının dilekçe-yüzündeki canlı örneğidir ve **yalnız
   kendi lehe dayanağı** için kullanılır — bkz. aşağıdaki sunum disiplini
   sınırı.

**Sunum disiplini sınırı (kritik, ihlal edilmez):** 5. adım, karşı tarafın
**henüz ileri sürmediği** bir aleyhe içtihadı önden çürütmek için kullanılmaz
— bu preemptive ifşa olur, kendi zayıf noktanı işaret edip karşı tarafı
silahlandırır. Yalnız DUYULMUŞ (karşı tarafın fiilen dayandığı veya kararda
fiilen değerlendirilmiş) aleyhe içtihat ayırt edilir; duyulmamış aleyhe
içtihat `oa-antitez` cephaneliğinde dahili kalır (bkz. SKILL.md "Sunum
disiplini").

## B5 — Çökertme protokolü (5 tur)

Karşı gerekçe/savunma çökertilirken iki aşama sırayla işler: **(i) dürüst
aktarım** (karşı gerekçe/iddia, çarpıtmadan, gerçekte ne diyorsa öyle
özetlenir) → **(ii) numaralı çürütme**. Çürütme, aşağıdaki beş türden
uygun olanlarla, **numaralı** biçimde kurulur:

1. **Belge lafzı** — çürütme, belgenin/kararın kendi metninden, kendi
   diliyle yapılır (yorum değil, metnin kendisi çelişkiyi gösterir).
2. **Takvim/aritmetik gerçeği** — tarih hesabı veya sayısal tutarsızlık
   nesnel olarak gösterilir (yorum gerektirmez, hesaplanır).
3. **Yokluk tespiti** — karşı iddianın dayandığı bir unsurun (belge, ihbar,
   bildirim, inceleme) dosyada **fiilen bulunmadığı** tespit edilir.
4. **İç-çelişki / tarih-bandı silahı** — karşı gerekçenin **kendi içinde**
   birbiriyle çelişen iki ifadesi, tarih sırasına dizilerek (bir "tarih
   bandı" olarak) yan yana konur; çelişki kendini gösterir.
5. **İtiraf-çıkarma** — karşı tarafın/kararın kendi metninde, farkında
   olmadan kendi tezini zayıflatan bir ifade **çıkarılır** ve öne çıkarılır.

**Sınır (anayasal — sunum disiplini ile aynı kök):** yalnız dosyada **fiilen
var olan** savunma/gerekçe karşılanır. Var olmayan, tahmin edilen veya
"karşı taraf muhtemelen şunu der" türünden hipotetik bir savunma
çökertilmez — bu hem preemptive ifşa hem de gereksiz uzunluktur.

## B6 — Bölüm mimarisi

- **Bağımsız yeter-sebep eksenler** — her bölüm başlığında hangi norma/
  hukuki ekseni dayandığı **çıpalanır** (başlık yalnız "İkinci Sebep" değil,
  "İkinci Sebep — [norm/eksen adı]").
- **Sıra** — usul önce → esas → ölçülülük/belirlilik → gerekçe eksikliği.
  Usulün esasa takaddümü düsturunun bölüm dizilimindeki karşılığıdır (bkz.
  SKILL.md "Anayasal düstur — usul esasa üstündür").
- **Rütbelendirme etiketli** — her bölüm/sebep, **asıl neden** mi
  **destekleyici** mi olduğu açıkça işaretlenir (ör. başlıkta veya bölüm
  girişinde "(asıl neden)" / "(destekleyici, asıl nedenin yanı sıra)").
  Rütbesiz bir sebep yığını, mahkemenin hangi sebebin dosyayı tek başına
  çözdüğünü görmesini zorlaştırır; rütbe, en güçlü sebebi öne çıkarır.
- **Kademeli ifade** — alt/yardımcı sebepler, asıl sebebi zayıflatmayacak
  biçimde bağlanır ("kabul anlamına gelmemek kaydıyla, kaldı ki...").
  Kademeli dil, asıl sebebin "tek dayanak" izlenimi vermesini bozmadan
  yedek hat kurar.
- **SONUÇ/İSTEM** — numaralı ve **öncelikli**; usul itirazı varsa "ÖNCELİKLE
  usulden ... reddi/kabulü", esas talep onu izler.

## B7 — Yardımcı desenler

- **Unsur tablosu** — `norm | tespit | sonuç` üç sütunlu tablo; normun her
  unsuru için dosyadaki somut tespit ve o unsurdan çıkan sonuç yan yana
  gösterilir (oa-kiyas büyük/küçük önerme eşlemesinin düzyazı-tablo hâli).
- **İçtihat merdiveni** — daire kararı → (varsa) içtihadı birleştirme/genel
  kurul kararı → anayasal düzey (AYM) sırasıyla dizilir; her basamak bir
  öncekini pekiştirir (köprü açık bırakılır: alt basamak üst basamağa atıf
  yapar, "evleviyetle" bağlanır).
- **Nominal/fiilî ayrımı** — bir unvan/sıfatın **kağıt üzerindeki (nominal)**
  hâli ile **fiilen işleyişteki (fiilî)** hâli ayrı ayrı tespit edilir; hukuki
  sonuç çoğu zaman fiilî duruma bağlanır (nominal görünüm tek başına yeterli
  savunma değildir).
- **Delil listesi = argüman** — delil listesi çıplak sayım değildir; her
  delil, hangi olguyu/argümanı desteklediği **nitelendirmesiyle** birlikte
  yazılır (ör. "... tutanağı (X olgusunun tek doğrudan delili)").
- **Üslup** — güçlü fiil **daima** bitişik bir olgusal dayanakla kullanılır
  (iddia, dayanaksız güçlü fiille değil, hemen ardından gelen somut olguyla
  taşınır); gereksiz sıfat/dolgu cümlesi (zero fluff) kullanılmaz.

## Gömme durumu

B1-B7 burada tam gövdeyle durur; `oa-dilekce/SKILL.md`'nin "İçtihat
kullanımı" bölümü B4'ün 5 adımını taşır (kısa çapa + tam B4 burada), GİRİŞ/
rütbelendirme kuralları SKILL.md'de kısa çapayla anılır. B1/B3/B5/B7'nin
mekanik denetim izdüşümü (künye alan seti, tebliğ satırı, GİRİŞ varlığı,
numaralı SONUÇ, alıntı-sonrası açıklama zorunluluğu) `dilekce_denetim.py`'ye
**ayrı bir pakette** bağlanacaktır (bu playbook saf metin katmanıdır; script
değişikliği bu paketin kapsamı dışıdır). İçtihat blokları ayrıca
`ictihat_muhakeme_denetim.py`'nin G2/G3 denetimine tabidir (iki katman: bu
playbook'un tertip-düzen izdüşümü + muhakeme izi denetimi ayrı script'lerde
yürür).

## Değişiklik günlüğü
Bu playbook `oa-dilekce/references/degisiklik-gunlugu.md`'ye bağlıdır; yeni
bir örüntü/tip öğrenildiğinde önce burası güncellenir, sonra günlüğe işlenir.

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

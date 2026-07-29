# Ticaret Sicili Desenleri — TTSG'yi delil olarak kullanmak

> Kaynak: 2026/307 (tasarrufun iptali, davalı cevabı) saha vakası. Burada
> anlatılan **desendir**, o dosyaya özgü olgular değil. Her yeni dosyada
> olgular yeniden okunur, künyeler yeniden teyit edilir.

## 1. TTSG bir NOTER KÜNYESİ MADENİDİR

Türkiye Ticaret Sicili Gazetesi ilanlarının **"Tescile Delil Olan Belgeler"**
satırları, tescile esas işlemin **noterliğini + tarihini + yevmiye numarasını**
verir. OCR nüshalarında bile bu satır genelde okunur kalır.

Bu, bir dilekçe yazarı için üç şey demektir:

- **Belgeyi görmeden künyesini kurabilirsin.** Elinde noter tasdikli suret
  olmasa da, hangi noterlikten hangi yevmiye ile celp isteneceğini TTSG'den
  öğrenirsin (delil listesinde "celbi: … Noterliği'nden" olarak yazılır).
- **Zamanlama ilişkisi sicilden okunur.** Farklı şirketlere ait işlemlerin
  **aynı noterlikte ardışık yevmiye numaralarıyla** tasdik edilmiş olması,
  bunların bağımsız işlemler değil **tek bir karşılıklı anlaşmanın parçaları**
  olduğunun sicilden okunan göstergesidir. (2026/307'de üç devrin genel kurul
  kararları 4576 → 4591 → 4698 ardışık yevmiyelerle tasdikliydi; bu, "takas"
  tezinin omurgası oldu.) Muvazaa/ivazsızlık tartışmalarında yeniden
  kullanılabilir desendir.
- **Aleniyet karşı tarafa bağlanır.** TTK m.36/3 uyarınca tescil ve ilan
  olunan hususları bilmediklerine ilişkin iddialar dinlenmez — sicilde
  yayımlanmış bir olguyu "bilmiyorduk" savunması, hele profesyonel bir kredi
  kuruluşu için, dinlenmez.

## 2. KRİTİK NİTELEME KURALI — yevmiye neyin yevmiyesidir?

**TTSG'de görünen yevmiye, GENEL KURUL / ORTAKLAR KURULU KARARININ TASDİK
yevmiyesidir; pay devir SÖZLEŞMESİNİN yevmiyesi DEĞİLDİR.** İkisini eşitlemek
belgeyi yanlış nitelemektir ve karşı taraf bunu tek cümleyle çürütür.

Güvenli formül:

> "… tarih ve … yevmiye sayılı tasdikli genel kurul kararına konu devir
> sözleşmesi (celbi: … Noterliği'nden)"

Bu formül üç şeyi aynı anda yapar: künyeyi doğru nitelendirir, devrin kendisine
işaret eder, ve belgenin nereden geleceğini söyler.

## 3. TAKAS / İVAZ SAVUNMA KALIBI (tasarrufun iptali — davalı cevabı)

Davalı, borçludan pay/mal devralmış ve **karşılığında** kendi malvarlığından
bir şey vermişse, savunma şu beş adımda kurulur:

**(a) Karşı-yönlü devri SİCİLDEN kur.** Davacının kendi kullandığı delil
türüyle: TTSG tarih/sayı/sayfa/ilan no. Karşılığın *iddia edilmesi* değil,
*sicilde görünmesi* esastır.

**(b) Aleniyeti TTK m.36/3 ile karşı tarafa bağla.** İvaz sicilde ilan
edilmişse, davacının "bilmiyorduk / gizlendi" hattı kapanır.

**(c) Doktriner çapayı kur:** iptale tabi tasarruf, borçlunun malvarlığının
**AKTİFİNİ AZALTAN** işlemdir; bu bir **DAVA ŞARTIdır**. Aktifi azaltmayan —
hatta artıran — bir işlemde dava, esasa girilmeden **dava şartı yokluğundan**
reddedilir.
> ⚠ **ÇIPLAK KÜNYE YASAĞI BURADA DA GEÇERLİDİR.** 2026/307'de bu ilke
> Yargıtay 17. HD'nin bir kararıyla teyit edilip tam metni döküme alınmıştı.
> Kalıbı yeni bir dosyada kullanırken **künyeyi yeniden çek, tam metni oku,
> davaya bağını kur ve damgala** (`oa_hafiza.py teyit --damga …`). Buradaki
> not bir künye kaynağı değil, **aranacak ilkenin tarifidir**.

**(d) Karşılığın NİTELİĞİNİ vurgula.** Verilen karşılık nakit değil, **sicile
tescilli ve hacze açık** bir malvarlığı ise, "nakit gizlenir / para izlenemez"
eksenli içtihat hattı bu dosyada etkisizleşir: alacaklının el atabileceği bir
değer borçlunun malvarlığında durmaktadır.

**(e) Kapanış cümlesi.** Bölümü tek cümlelik net sonuçla kapat:
> "Tasarrufun iptali davasının esas araştırma konusu olan ivaz, bu dosyada
> gizli-saklı bir olgu değil, aleni sicilde yayımlanmış bir kayıttır."

### DÜRÜST SINIR (kalıbın zayıf noktası)
"Karşı devir TTSG'de ilan edilmiş → ret" sonucunu **birebir** kuran bir emsal,
üç ayrı taramada (trampa / ticaret sicili + aleniyet / Türkiye Ticaret Sicili
Gazetesi) **bulunamamıştır**. Kalıp bu yüzden emsal üzerine değil, **norm
(TTK m.36/3) + aktifi-azaltma ilkesi** üzerine durur. TTSG'yi yalnız ortaklık
sıfatının ispatına kullanan kararlar bu tez bakımından **nötrdür** — lehe
gösterilemez. Bu sınırı bilerek yaz: kalıbın gücü sicilden okunan olgudadır,
var olmayan bir emsalde değil.

## 4. TESLİM SONRASI HIZLI MOD

Dilekçe UYAP'a gittikten sonra avukat tipik olarak hızlı bir düzeltme
döngüsüne girer (soru → iki cümlelik kalıp → kendi md düzenlemesi → yeniden
basım). Bu döngüde **tek gerçek kaynak taslak md dosyasıdır** — UDF ondan
türetilir, tersi değil. Her düzeltmeden sonra zincir baştan koşar:

```
md → md_udf_html.py → npx -y udf-cli@latest html2udf → udf2md ile geri okuma + anahtar token grep
```

UDF üzerinde doğrudan düzenleme yapıldıysa (UYAP editöründe), **md artık bayat
demektir**: bir sonraki basımdan önce md, UDF'teki son hâle göre güncellenir;
aksi hâlde avukatın editörde yaptığı düzeltmeler sessizce geri alınır.

> **E-imzalı nüshaya dokunma.** Arşivinde `sign.sgn` bulunan bir UDF teslim
> nüshasıdır, taslak değil: içeriği değişirse imza geçersiz kalır. Değişiklik
> gerekiyorsa önce düzelt, **sonra yeniden imzala**.

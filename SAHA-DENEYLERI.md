# SAHA DENEYLERİ DEFTERİ — dokuz belgeli koşunun tam kaydı

> Sistem 149 gerçek davada test edilerek v0.0.1'den v0.5.11'e geldi. Bu
> defter, **v0.5.x döngüsünde sensörlü izleme + karne + adli analizle uçtan
> uca belgelenen dokuz koşunun** ayrıntılı kaydıdır. Dosya kimlikleri anayasa
> m.7 gereği yalnız saha etiketiyle anılır; hiçbir gerçek kişi, mahkeme veya
> dosya numarası bu belgeye giremez.

---

## Deney yöntemi — bir koşu nasıl belgelenir

**Döngü tektir:** gerçek derdest dava koşusu → karne → karnede ölçülen
kusurun onarımı → yeni sürüm. Kanıtsız iyileştirme yapılmaz; "şu mimariyi
kuralım" değil "şu koşuda şu kırıldı" konuşulur.

1. **Dosya gerçektir.** UYAP'tan indirilen ham evrak klasörü (34-214 evrak
   arası ölçüldü), yürüyen bir davanın güncel hali.
2. **Prompt doğaldır.** Avukat işi kendi diliyle tarif eder; mekanik talimat
   verilmez. Deneyin sınıfı promptla belirlenir ve karneye damgalanır:
   - **organik** — tek doğal prompt, sıfır müdahale, sıfır mekanik-hijyen
     promptu;
   - **müdahalesiz** — izlenir ama dokunulmaz;
   - **müdahaleli** — içerik/mekanik yönlendirme yapıldı (sayısı yazılır);
   - **müdahaleli-yetkili** — gözcüye koşu içi onarım yetkisi verildi
     (her müdahale defterde/transkriptte izlidir).
3. **Gözcü üç kaynaktan izler:** dosya-sistemi deltası (defter, kütük,
   makbuz, mühür, 40-UYAP), oturum transkripti (tur sayısı, araç karışımı,
   token eğrisi, skill çağrıları) ve eşik nöbetçileri (RED/yeşil makbuz,
   damga başlangıcı, mühür kırılması, bayat-araç uyarısı, avukat-kararı
   kavşağı). Gözlem salt-okunurdur; bulgular koşuya geri beslenmez.
4. **Karne üç kollu adli analizle çıkar:** transkript + artefakt + mekanizma
   kolları ayrı ayrı, birbirini ve gözcüyü ÇÜRÜTMEKLE görevli koşturulur;
   çelişkiler "çözülmedi" diye dürüstçe yazılır. Tek koşu = gözlemdir (n=1
   damgası), kanıt değil.
5. **İki hüküm asla karıştırılmaz:** mekanik tamlık (zincir fiziksel koştu
   mu) ile içerik kabulü (dilekçe avukatı tatmin etti mi) ayrı satırlardır.

---

## Koşu 1 — İlk tam koşu: ~200 evraklık istinaf dosyası

- **İş:** istinaf aşamasında ek beyan dilekçesi. **Sonuç:** 49 dakikada,
  45,6k token ile teslim edilebilir dilekçe + geçerli UDF.
- **Kıyas ölçümü:** aynı sınıf iş, evrakı modele görüntü olarak yükleyen eski
  usulde 1,2M+ token tüketiyordu — fark ~26×, muhakemeden kısılmadan
  (dakika dakika çizelge: [SAHA-SONUCU.md](SAHA-SONUCU.md)).
- **Dersler:** bayat araç kopyası tehlikesi ilk kez görüldü; atıfların
  kaynak-link zinciri kuralı doğdu → **v0.5.7** (bayat-tohum aşısı, G4
  bağlantı kapısı).

## Koşu 2 — Müdahalesiz test: 214 evraklık bakir klasör

- **Düzen:** tek doğal prompt, sıfır müdahale; sistemin kendi başına ne
  yaptığı ölçüldü.
- **Ana bulgu (kurucu ders):** "Kapının gücü kodunda değil TETİĞİNDEDİR" —
  mekanizmalar sağlamdı ama çağrılmıyorlardı. Beş somut eksik ölçüldü
  (çalışma hafızası elle yazılmış, muhakeme kaydı üretilmemiş, okuma
  ekonomisi kapısı ölü, tez iskelette yok, bekçi kapsamı dar).
- **İkinci ders:** uyum maliyeti = uyum — sertlik eklemek değil, tetik
  bağlamak gerekir. → **v0.5.5.1–v0.5.5.3** onarımları.

## Koşu 3 — 447 sahası: vergi davası

- **Ana bulgu:** hook katmanının **sessiz ölümü** — masaüstü uygulaması
  hook'u kabuksuz koşturuyordu; katman "tanımlı" görünüyor ama hiç
  ateşlemiyordu. "Tanımlı ≠ çalışıyor" dersi buradan çıktı; duman testi
  (`hook_doktor --kurulu`) zorunlu hale geldi.
- → **v0.5.8.1 / v0.5.8.2** (hook kayıt kanalının onarımı).

## Koşu 4 — 372 sahası: aile / mal rejimi

- **İlk kez:** hook katmanı uçtan uca canlı ateşledi. Koşu, **beş kollu adli
  analizle** (transkript + artefakt + kod yolu + şekil zinciri + desen
  karnesi) incelendi.
- **Elle-UDF krizi:** model UDF'i elle kurmaya yeltendi; elle kurulan dosya
  UYAP editöründe **açılmadı** (7 dosya karantina). Çözüm A/B testiyle
  bulundu: açılan ve açılmayan dosyaların iç imzaları karşılaştırıldı —
  editörün aradığı stil iskeleti tespit edildi.
- → **v0.5.8.4:** elle-UDF engeli, makbuz garantisi (RED bile damgalı
  makbuz keser), mühür otomasyonu, şekil kapısı (4×42,52 pt).

## Koşu 5 — 346 sahası: bilirkişi ek raporuna itiraz

- **Parlayan an:** künye kapısı **gerçek bir açığı** yakaladı ve model dürüst
  davrandı — uydurmak yerine eksikliği bildirdi.
- **Kırılma:** tek bir ayrıştırıcı yanlış-pozitifi (belgenin kendi "DOSYA NO"
  satırını atıf sanması) yeşil makbuzu matematiksel olarak imkânsız kıldı;
  ayrıca prompt kanalı klon-klasörde ölü bulundu.
- **Avukat kuralının doğuşu:** "Bulunan içtihatların TAMAMI okunmadan
  dilekçeye giremez; lehe ise girer, aleyhe olan cephaneliğe ayrılır" —
  → **v0.5.8.5:** mutlak triyaj **[G6]** (tam-metin döküm + muhakeme kaydı +
  LEHE damgası şartı), hook dirilişi, e-imza halkası.

## Koşu 6 — 777 sahası: banka/kefalet ikinci cevabı + 24 kök çapraz taraması

- **İçerik dersi:** ilk sunum avukat tarafından REDDEDİLDİ; yeniden inşa
  sonrası kabul edildi. "Kapılar yeşil ama içerik ret" ayrımı ilk kez burada
  keskinleşti — mekanik tamlık ≠ içerik kabulü.
- **Kök neden kazısı:** koşuda görülen tüm "model kusurları" (elle UDF, elle
  kütük, makbuzsuz beyan) transkript kazısıyla ÇÜRÜDÜ — model resmî araçları
  koşmuştu; kusur, uygulama paketinden servis edilen **bayat araç
  neslindeydi**. Kusuru modele atfetmeden dağıtım zincirine bakma dersi.
- **İlk gerçek LEHE/ALEYHE triyajı:** 23 LEHE / 11 ALEYHE — aleyhe olanlar
  dilekçeye değil iç cephaneliğe gitti.
- **İlk tam-standart UDF:** dört kenarı yönetmelik ölçüsünde (42,52 pt),
  UYAP editöründe açıldı. Ayrıca 24 dava kökünde çapraz tarama yapıldı.
- → **v0.5.8.6** (sürüm kilidi/parmak izi, VERSION.json) + **v0.5.9**
  (sunum kilidi, inline denetim, zincir-durumu enjeksiyonu, 40-UYAP şeması).

## Koşu 7 — 307 sahası: tasarrufun iptalinde ikinci cevap (devralmalı)

- **Zor koşullar bilerek seçildi:** dosya baştan yeniden indirilmişti — eski
  çalışma alanının önbelleği yeni evrak adlarıyla SIFIR kesişiyordu (209
  dosyada 0 ad eşleşmesi); sistem eski kütüğün damgalarını koruyup üstüne
  yeni triyajı ekledi, çökmedi.
- **Ölçümler:** 161 dakika · ~822k üretim tokeni · 271 araç çağrısı ·
  45 içtihat damgası (45'i tam-metin sınıfı) · teslim zinciri kendiliğinden
  koştu, ilk kapıda RED yedi, düzeltilip yeşile bağlandı.
- **Deney sınıfı dürüstlüğü:** koşu sırasında "tek doğal prompt" sanılıyordu;
  transkript sayımı 11 kullanıcı turu ve 7 mekanik-hijyen promptu gösterdi —
  karne kendini düzeltti, sınıf **müdahaleli** olarak yazıldı.
- **Ağır bulgular:** teslim ürünü makbuzdan ~68 dk sonra mührün dışında
  değişti (K1) ve makbuz resmî adlı ürünü kapsamıyordu (K2).
- → **v0.5.10:** atomik mühür + filo-tazelik kapısı + çift-uzantının
  kaynağında ölümü. Tam karne: [KARNE-307.md](KARNE-307.md).

## Koşu 8 — 923 sahası: vergi/gümrük — ödeme emri + ek tahakkuk

- **İLK ORGANİK YEŞİL MAKBUZ:** tek cümlelik tek prompt, sıfır müdahale,
  sıfır mekanik-hijyen promptu — RED'den kendi düzeltmesiyle yeşile döndü.
- **[G6] kapısının canlı sınavı:** dilekçelerde atıflar vardı ama tam-metin
  döküm yoktu; teslim zinciri RED verdi; model 7 kararın tam metnini döküp
  damgaladıktan sonra yeşil alabildi — kural kâğıtta değil kapıda yaşıyor.
- **Çift ürün:** iki ayrı dilekçe + iki UDF (ödeme emrine ve ek tahakkuka
  karşı); künye teyidi 15/15 + 18/18, teyitsiz sıfır.
- **Dürüst altyapı notu:** canlı içtihat ucuna erişilemeyince model yedek
  arşivle çalıştığını ve arşiv-sonrası kararların eksik olabileceğini
  kütüğün başına KENDİSİ yazdı ("AŞAN-KAYNAK" riski).
- **v0.5.10'a çift kanıt:** çift-uzantılı kopya adı ve mühürsüz kopya
  kusurları bu koşuda bağımsız olarak tekrarlandı.

## Koşu 9 — 1865 sahası: idari yüksek yargıda soruşturma-izni itirazı

- **En zorlu düzen:** 34 evrakın TAMAMI taranmış TIFF (OCR hattının sınavı);
  **iki müvekkil**, iki ayrı itiraz dilekçesi + çelişki raporu; aynı dava
  klasöründe **5-6 paralel oturum** (çok-oturumlu çalışmanın ilk ölçümü);
  sınıf: **müdahaleli-yetkili** (gözcüye onarım yetkisi verildi).
- **Kök düşman adlandırıldı:** onarılan araç kiti, uygulamanın eski paket
  anlık-görüntüsünden 9 dakika sonra ESKİ nesille geri ezildi — 777'den beri
  üçüncü nüks. Söz-müdahalesi (oturuma mesaj) ezildi; **dosya-düzeyi onarım +
  salt-okunur koruma** tuttu. Uyarıya itaat ölçüldü: 12 uyarı hiçbir şey
  değiştirmedi, teslim duvarının RED'i her şeyi değiştirdi.
- **v0.5.10 ilk gerçek sınavını burada verdi:** filo-tazelik kapısı yeşilin
  içinde koştu; kopyalar mühürleriyle gitti; mühür-kırık ürün (307'de 68 dk
  görünmez kalan sınıf) dakikasında yakalandı ve teslimden önce kapatıldı.
- **Kapanış ritüeli tam işledi:** kimliksiz ders damıtması (7+6+4 örüntü),
  devir paketleri, türetilmiş durum; tamamlanamayan tek iş (merci kararı
  dönünce ders güncelleme) deftere dürüstçe "asenkron" yazıldı.
- → **v0.5.11:** rpm karantinası, kilitli çekirdek, yönlü tazelik, oturum
  damgası. Tam karne: [KARNE-1865.md](KARNE-1865.md).

---

## Deneylerden damıtılan kurucu dersler

1. **Kapının gücü tetiğindedir** (Koşu 2) — mekanizma değil, çağrılma anı
   tasarlanır.
2. **Tanımlı ≠ çalışıyor** (Koşu 3) — her katman fiilen ateşlediği kanıtıyla
   yaşar; duman testi zorunludur.
3. **Üretildi ≠ geçerli** (Koşu 4) — ürün, resmî okuyucuda açılana kadar
   iddiadır.
4. **Kural kapıya bağlanmadıkça temennidir** (Koşu 5→8) — [G6] önce avukat
   kuralıydı, sonra kapı oldu; 923'te kapı olarak çalıştı.
5. **Kusuru modele atfetmeden dağıtım zincirine bak** (Koşu 6, 9) — üç
   koşunun "model hatası", bayat araç nesli çıktı.
6. **Mekanik tamlık ≠ içerik kabulü** (Koşu 6, 7) — iki hüküm ayrı yazılır;
   nihai hüküm avukatındır.
7. **Uyarı ikna etmez, kapı ikna eder** (Koşu 9) — davranış kusuru daha sert
   uyarıyla değil, itaate muhtaç olmayan korumayla çözülür.
8. **Gözcü de yanılır** (Koşu 7, 9) — canlı raporlar iki kez adli analizle
   düzeltildi; karneler gözcünün hükümlerini de çürütmekle görevlidir.

---
*Bu defter, koşular eklendikçe büyür. Sürüm eşlemesi:
[CHANGELOG.md](CHANGELOG.md) · özet tablo ve ölçülen örnekler:
[README → Saha deneyleri](README.md#saha-deneyleri--testler-nasıl-yapıldı).*

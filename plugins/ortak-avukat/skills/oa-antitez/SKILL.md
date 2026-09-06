---
name: oa-antitez
description: >-
  Ortak Avukat sisteminin ANTİTEZ/KRİTİK parçası. Bir dava, dosya, dilekçe veya
  tezin analiz edildiği her durumda — karşı tarafın bizi kapatacak savunma ve
  iddialarını DURUM FARKINDALIĞI için işin ilk etabında ortaya çıkar, sonra her
  birini ÇÖKERT. "Karşı taraf ne der", "zayıf yanlar neler", "bu argüman nereden
  çatlar", risk değerlendirmesi, şeytanın avukatı, teslimden önce sağlamlık kontrolü
  → kullanıcı açıkça istemese bile esaslı bir tez kurulduğunda tetikle. Deterministik
  motor (bundled script) cephe eksiksizliğini ve çürütme bütünlüğünü garanti eder.
  Bağımsız çalışır; `oa-interview` (ön teori), `oa-ictihat` (çürütme dayanağı) ve
  `oa-kontrol` (teslim denetimi) ile takım oynar.
---

# oa-antitez — Antitez ve Çürütme Motoru

Sök-tak parça. Amacı tek ve nettir: **antitez, durum farkındalığı içindir.** Karşı tarafın bizi kapatacak savunma/iddialarını **işin ilk etabında** görürüz; sonra her birini **çökertiriz.** Çıktı bir endişe listesi değil — **çürütülmüş, güçlenmiş konumumuz** ve dürüstçe işaretlenmiş artık risklerdir.

## Yönetici ilke
Tezini en güçlü karşı-teze karşı test etmeden tamam sayma. Hâkimin ve karşı vekilin gözünden bak: bu nereden çatlar? Çatlağı **önce sen bul** (farkındalık), sonra çürütmesini **hazırla** (cephanelik). Çürütemediğin yeri gizleme — **artık risk** olarak işaretle ve müvekkile/Can'a sun. Aktif çıkarımın denetleyici ikizidir: lehe tez üretirsin, burada onu kırmaya çalışırsın.

## Çıktının kullanımı — GİZLİ CEPHANELİK (en kritik kural)
Bu parçanın çıktısı — antitez matrisi ve zayıf noktalar — **yalnızca bize özeldir (dahili istihbarat).** Müvekkil-içi durum farkındalığı ve hazırlık içindir; karşı tarafa veya mahkemeye **proaktif sunulmaz.**

- **Sunulmamış antiteze karşı savunma geliştirme.** Karşı taraf bir savunmayı/iddiayı fiilen ileri sürmeden (yani "duyulmadan") ona karşı sunulan dilekçeye preemptive çürütme **koyma.** Bunu yapmak: (a) karşı tarafa argümanın en güçlü hâlini öğretir, (b) kendi zayıf noktamıza dikkat çeker, (c) kredibilite harcar — kendi ayağına kurşun.
- **Hazırlanan çürütme cephaneliktir, mühimmat değil ateş değil.** Karşı taraf o antitezi fiilen ileri sürünce / dosyaya girince (cevap, istinaf gerekçesi, bilirkişi) devreye alınır — hazır ve keskin.
- **İstisna — zaten "duyulmuş" olan:** argüman karşı dilekçede, mahkeme/karar gerekçesinde veya dosyadaki bir belgede zaten varsa, o artık ortadadır; ona karşı çürütmeyi sunarsın. Ayrım: *hipotetik (dahili) antitez* ↔ *fiilen ileri sürülmüş (cevaplanır) antitez*.
- **Müvekkilin kendi zaafı** da bu mantıkla yönetilir: dahili bilinir, sunulan belgede ifşa edilmez; karşı taraf değinirse hazır cevapla karşılanır.

## Deterministik motor
Script hukuki içeriği üretmez; **eksiksizliği ve bütünlüğü** garanti eder (protokol her seferinde aynı sırada çalışır):

```bash
# 1) Sabit saldırı cephelerini ve doldurulacak matris şablonunu al:
python scripts/antitez_matris.py --iskelet

# 2) Matrisi muhakemeyle doldur (her cephe için antitez + çürütme + dayanak + artık risk),
#    sonra bütünlüğünü denetle:
python scripts/antitez_matris.py --dogrula _oa/cikti/07-antitez-matris.json
```

Dokuz sabit **cephe** (kör nokta bırakmamak için eksiksiz değerlendirilir): usul · maddi vakıa · ispat/delil · hukuki niteleme · içtihat · zamanaşımı · def'i/karşı talep · müvekkil zaafı · **bilirkişi/teknik** (v0.5.16). Denetim deterministik olarak şunları yakalar: **açık cepheler** (değerlendirilmemiş = kör nokta), **çürütülmemiş antitezler** (ne çürütme ne risk işareti), **teyitsiz dayanak** (atıf denetimi → `oa-kontrol` A / `oa-ictihat`), güçlü antiteze dayanaksız çürütme, ve dürüst **artık riskler**.

**9. cephe — bilirkişi/teknik (v0.5.16, P1-5/A-20 — saha dersi):** çoğu dosyada fiilî karar mercii bilirkişi raporudur; sekiz cephe raporu hiçbir yerde ZORUNLU taramıyordu. Cephe şunları sorar — (a) **raporun kırılma noktaları:** HMK m.279/2'nin zorunlu içeriği (görevlendirme konusu, incelenen maddi vakıalar, gerekçe ve sonuç, görüş ayrılığı varsa sebebi, düzenlenme tarihi, imzalar) eksik mi; **tek imza/heyet:** kurul görevlendirmesinde müzakere ve tüm imzalar var mı (m.279/3), azınlık görüşü ayrı rapor mu; (b) **hukuki nitelendirme yasağı (HMK m.279/4):** bilirkişi uzmanlık/teknik bilgi dışına çıkıp hâkime ait hukuki nitelendirme/değerlendirme yapmış mı — yapmışsa o kısım rapordan düşer; (c) **itiraz stratejisi (HMK m.281):** raporun tebliğinden itibaren **iki hafta** içinde eksik tamamlatma / açıklama / yeni bilirkişi talebi; teknik çalışma gerektiren hâlde süre içinde başvurarak bir defalık, iki haftayı geçmeyen ek süre; mahkemenin ek rapor / sözlü açıklama / yeniden inceleme yetkisi — **süre ayağı `oa-sure --tur usul` ile hesaplanır** (usul esasa üstündür); (d) **uzman görüşü (HMK m.293):** tarafın kendi bilimsel mütalaası; bu nedenle ek süre istenemez; uzman duruşmaya çağrılıp geçerli özürsüz gelmezse raporu değerlendirilmez; (e) **keşif dayanağı:** rapor keşfe dayanıyorsa keşfin usulü ve tutanağı, dayanmıyorsa yerinde inceleme yapılmadan varılan sonuç. Karşı yön simetriktir: karşı tarafın dayandığı rapor/uzman görüşü de aynı beş sorudan geçirilir. *(HMK m.279, m.281, m.293 metinleri Mevzuat MCP teyit 2026-09-06 — `mevzuatgov:kanun:5:6100`.)* Eski sekiz cepheli matrisler `--dogrula`da **AÇIK CEPHE: bilirkisi_teknik** alır — istenen etki: kör nokta görünür, sessiz uyum yok.

## Protokol
1. **Tezi netleştir** (müvekkilin ana iddiası — bir cümle).
2. **İskeleti al;** dokuz cepheyi tek tek dolaş — karşı taraf buradan nasıl saldırır? Gücünü (yüksek/orta/düşük/yok) işaretle.
3. **Her saldırıyı çökert:** çürütmeyi yaz; dayanağı `oa-ictihat`'tan **teyitli** çek. Çürütemiyorsan **artık risk** olarak dürüstçe yaz — boş bırakma. **Aleyhe içtihat buraya akar:** `oa-ictihat` müvekkil aleyhine bulduğu kararları bu parçaya devreder; her birini ayırt etme (somut olayla farklılık), aşılmışlık/içtihat değişikliği, dar yorum veya lehe karşı-içtihatla çökert — ve gizli cephanelikte tut (karşı taraf ileri sürmeden sunma). **R3 (İçtihat Muhakeme Zinciri ile köprü):** DAMGA=`ALEYHE` (ayırt edilmemiş) kararlar burada dahili kalır; DAMGA `ALEYHE-AYIRT`'a yalnız karşı tarafın FİİLEN dayandığı/kararda fiilen değerlendirilmiş — yani **DUYULMUŞ** — aleyhe içtihat yükseltilir ve dilekçede ayırt edilerek karşılanır (bkz. `oa-kiyas/references/ictihat-muhakeme-sablonu.md`). Henüz duyulmamış (yalnız hipotetik) aleyhe içtihadı önden ayırt edip sunulan metne yazmak, bu parçanın "sunulmamış antiteze preemptive çürütme yazma" yasağının içtihat-özel görünümüdür.
4. **Denetle** (`--dogrula`): kör nokta, çürütülmemiş antitez, teyitsiz dayanak kalmasın.
5. **HÂKİM LENSİ — ikinci pas (v0.5.16, A-21; cephe DEĞİL, lens):** matris tamamlanıp çürütme brifi yazıldıktan sonra brifin üstünden ikinci kez geç ve şunu sor: **hâkim bu dosyayı nasıl kapatmak ister: iş yükü, gerekçe alışkanlığı, daire eğilimi; on dakikada okuyan hâkim tezi anlıyor mu.** Bu bir onuncu cephe değildir (script denetlemez, `--dogrula` bakmaz); model-denetimli bir bakış açısıdır: cephelerde "çürütüldü" görünen bir konum, hâkimin en kısa yoldan varacağı gerekçeyle hâlâ kapanabiliyorsa brif o gerekçeye göre yeniden sıralanır (ilk sayfada ne olmalı, hangi çürütme iki cümleye iner). Daire eğilimi iddiası olgudur — `oa-ictihat`/`oa-alan` teyidi olmadan yazılmaz; teyitsizse "izlenim — teyit edilmedi" etiketiyle kalır. `oa-kontrol` C2 brifi aynı cümleyle aynı lensi teslim öncesi uygular; ikisi aynı soruyu iki ayrı anda sorar, biri diğerinin yerine geçmez.
6. **Dahili sun:** güçlenmiş konum + cephanelikte hazır çürütmeler + yönetilecek artık riskler — yalnızca müvekkile/Can'a, karar-malzemesi olarak. Çürütmeler, karşı taraf ilgili antitezi ileri sürene dek **sunulan belgeye girmez.**
7. **CELSE KARTI (duruşma varsa — v0.5.13, pratikçi heyeti):** dosya tutanakta
   kazanılır; diskteki kusursuz analiz duruşma anında işe yaramaz. Duruşma
   öncesi cephanelikten **tek sayfalık** kart türetilir:
   `_oa/cikti/NN-celse-karti.md` (ayrı bir skill/parça DEĞİL — bu parçanın
   çıktısı). İçerik: (a) bu celsedeki 1-3 somut hedef, (b) karşı taraftan
   beklenen üç antiteze **sözlü** karşılık cümleleri, (c) tutanağa geçirilmesi
   şart olan beyanlar, (d) talep edilecek ara kararlar.
   **GİZLİLİK — mutlak:** kart iç analizdir; başına
   `⚠ DAHİLİ — DOSYAYA EKLENMEZ / UYAP'A YÜKLENMEZ` filigranı konur, teslim
   paketine ve 40-UYAP dizinine **asla** girmez.
   **Celse sonrası:** tutanak, kartla karşılaştırılır — bu bir *model-denetimli
   checklist*tir, mekanik denetim değildir ve yalnız **öneri** üretir
   ("şu beyan tutanağa geçmemiş görünüyor"). Düzeltme talebi verilip
   verilmeyeceği **avukatın takdiridir**; sistem otomatik gündem oluşturmaz.

## Kompozisyon (iki konum — v0.5.16 P0-3 hizalaması: `oa-pipeline` sabit hattıyla aynı sıra)
- **Erken (durum farkındalığı) = SABİT HAT ADIM 6:** KIYAS (adım 5) bitince ve **STRATEJİ (adım 7) başlamadan ÖNCE** çalışır — `oa-interview`'ın ön dava teorisi ve `oa-kiyas`'ın tatbik zinciri hazırken antitezi o teoriye karşı koştur; matris `_oa/cikti/07-antitez-matris.json`'a yazılır (evrak adı `[G]` kapısı ve pipeline önkoşul tablosuyla sözleşmelidir — ADIM numarası değişse de dosya öneki DEĞİŞMEZ). **`oa-strateji` antitez çıktısını girdi alır:** yol seçimi, başarı olasılığı ve artık-risk kararı, karşı tarafın kozları görülmeden verilmez — antitez stratejiden sonra koşarsa strateji kör kurulmuş olur (P0-3'ün kapattığı hata).
- **Geç (sağlamlık) = YAZIM (adım 8) sonrası / KONTROL (adım 9) öncesi:** dilekçe taslağı çıkınca matris yeniden dolaşılır — taslaktaki her argüman çökertilmeye karşı test edilmiş, DUYULMUŞ cephelerin çürütmesi metne çapalanmış olsun; `oa-kontrol` C2/[G] bu geç pasın mekanik aynasıdır.
Çürütme dayanakları daima `oa-ictihat` üzerinden teyitli; bu parça `oa-kontrol`'ün protokol temelinin üstüne kurulu deterministik motordur.

## Öğrenme günlüğü
Yeni bir saldırı cephesi/kalıbı veya çökertme tekniği öğrenildiğinde `STANDART_CEPHELER`'e ve protokole ekle, aşağıya işle, yeniden paketle.
## Anayasal düstur — usul esasa üstündür
Usulün esasa takaddümü ailenin anayasal düsturudur: usulden düşen dosya esasa hiç giremez; süre, usul hukukunun parçası ve telafisiz tek hatadır. Matriste **usul cephesi 1. cephedir** ve İLK taranır: bizim usul zaafımız (süre, görev/yetki, harç, ehliyet, temsil) karşı tarafın en ölümcül ve en ucuz kozudur — esas tezler ne kadar güçlü olursa olsun önce burası kapatılır. Simetrik taarruz: karşı tarafın usul hatası `oa-sure --islem` ile denetlenir; **cephanelik istisnası** — tespit edilen süre kaçırması saklanmaz, aktif usul itirazı olarak derhâl ileri sürülür.

## Anayasal bloklar — tek kaynak (anayasa.md)
Bu parça, ailenin ortak anayasal ilkelerine tabidir — **Çaba/token standardı** (model/efor kullanıcının tercihi; muhakemede/doğrulamada/çıktı kalitesinde tasarruf YOK, yalnız mekanik katmanda kayıpsız verimlilik), **Örnekleme ilkesi** (konu sınırlaması yok — kapsam TÜM Türk hukuku), **Doğaçlama meşruiyeti** (yöntem serbest, olgu MCP-teyitli), ayrıca Doğrulama mimarisi, Anonimleştirme ve Layer 0 gizlilik. **Tek ve yetkili kaynak: `ortak-avukat/references/anayasa.md`.** (Bu parça alt-ajan olarak koşarken bu ilkeler `oa-pipeline/scripts/oa_hafiza.py ajan-brif` ile taşınır.)

## Başbakan denetimi (anayasal)
Bu parça, ailenin Başbakanı `oa-pipeline`'ın icra+denetimine tabidir: çağrıldığında disiplini İSTİSNASIZ ve tam işletilir (ama/fakat/token-tasarrufu gerekçesiyle kestirme YASAK). Görev savsaklanmaz; gerçekten yapılamayan bir şey varsa dürüstçe belirtilir ("yaptım" denmez) ve alternatif yöntem üretilir. Önemli olan proses ve çıktı kalitesidir.

## Müvekkil-aleyhi: iç/dış ayrımı (anayasal)
Karşı tezleri ve müvekkil zaaflarını bulmak İÇ analizdir ve dürüstçe yapılır (durum farkındalığı için şart). Bu bulgular dış dilekçeye müvekkil aleyhine ifade olarak GEÇMEZ; içeride çökertilir, dışarıda yalnız çökertilmiş/lehe hali görünür.

## Fiziksel aktivasyon — simülasyon yasağı (anayasal)
Bu parça yalnızca ÜÇ kanıttan en az biriyle "çalıştı" sayılır: (1) Skill aracıyla FİİLEN çağrıldı ve bu gövde bağlama yüklendi (kullanıcının `/oa-antitez` komutuyla eşdeğer); (2) scripti gerçekten koştu ve çıktısı görünür; (3) gerektirdiği MCP çağrısı fiilen yapıldı (araç + sorgu + sonuç kaydıyla). Kısa description her zaman bağlamda durur — o VİTRİNDİR, disiplin değildir; gerçek disiplin bu gövdededir. Bu yüzden hiçbir parça bu parçayı description'ından TAKLİT EDEMEZ; bu parça da başka bir parçanın işine ihtiyaç duyduğunda onu Skill aracıyla fiilen çağırır (olmuyorsa SKILL.md'sini Read ile yükler; o da olmuyorsa "FİZİKEN YÜKLENEMEDİ" diye açıkça yazar). Yapılmamış çağrı 'yapılmış', koşmamış script 'koşmuş' gösterilemez — bu, halüsinasyonun ta kendisidir. Devir alırken/verirken kısa DEVİR PAKETİ (ne yapıldı → ne bekleniyor → hangi kanıt) kullanılır ve pipeline defterine (`oa-pipeline/scripts/pipeline_kayit.py`) işlenir. Bu parçanın ürettiği her kalıcı çıktı (JSON/rapor/devir paketi) çalışılan klasörün `_oa/` yerel hafıza kökünde yaşar (yapı: `oa-pipeline` → Çalışma Kökü).

## Değişiklik Günlüğü
Tam günlük `references/degisiklik-gunlugu.md`'dedir (bağlam ekonomisi için ayrıldı — içerik aynen korunur; yeni kayıtlar oraya işlenir). Güncel sürüm: **v3.26**.

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

## v0.5.8.5 — A1 TRİYAJ: ALEYHE'nin adresi CEPHANELİKTİR

> **ÇEKİRDEK (kullanıcı direktifi — aynen):** "Müvekkil aleyhine HİÇBİR yargı
> kararı dilekçeye giremez. MCP'den çekilen TÜM kararlar İSTİSNASIZ baştan
> sona (TAM METİN) okunur. LEHE ise dilekçeye; ALEYHE ise CEPHANELİĞE
> (strateji/farkındalık); NÖTR kütükte kalır."

- **ALEYHE damgalı her kararı cephanelik ürününe FİİLEN İŞLE** (matris /
  `_oa/cikti/07-antitez-cephanelik.md`) — kütükte damgalı durması yetmez;
  işlenmemiş aleyhe karar farkındalık kaybıdır. Mekanik ayna: [G6] TERS
  DENETİMİ, kütükte son damgası ALEYHE olup cephanelik ürünlerinde
  (`07-antitez*`) hiç anılmayan kararı **"FARKINDALIK KAYBI"** uyarısıyla
  görünür kılar (advisory — bloklamaz; giderilmesi bu parçanın işidir).
- **Duyulma anı kütüğe işlenir:** karşı taraf cephanelikteki aleyhe kararı
  FİİLEN ileri sürünce `oa_hafiza.py teyit --duyulmus` ile `DUYULMUS=EVET`
  işaretle; ancak o zaman ALEYHE-AYIRT yükseltmesi dilekçeye çıkabilir —
  yalnız ayırt/çürütme bağlamında, destek atfı olarak asla ([G6] dar
  istisnası). Duyulmamış aleyhe karar cephanelikte dahili kalır (m.6
  preemptive ifşa yasağı).
- **Çürütme de tam metinden kurulur:** arama sonucu parçasından alıntı
  YASAKTIR — ayırt/çürütme gerekçesi kararın GETİR dökümüne dayanır.

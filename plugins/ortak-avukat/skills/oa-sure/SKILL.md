---
name: oa-sure
description: >-
  Ortak Avukat sisteminin SÜRE parçası. Türk hukukunda her süreye bağlı işlemde —
  yalnızca usul (istinaf, temyiz, AYM başvuru, itiraz, cevap, dava açma; HMK/CMK/İYUK)
  değil, MADDİ HUKUK süreleri de (zamanaşımı/hak düşürücü: TBK, TMK, TTK, 6183 ve diğer
  kanun/yönetmelikler — ör. TTK m.23/c, m.749, m.814; TBK m.39, m.82; TMK m.571; 6183
  m.58) dahil — "süre ne kadar / ne zaman doluyor / kaçırdım mı / zamanaşımı" türü her
  işte DEVREYE GİR. Süre kuralını Mevzuat MCP'den teyit et, sonra başlangıç tarihinden
  son günü deterministik hesaplamak için bundled scripti `--tur usul|maddi` ile kullan
  (maddi sürelerde adli tatil uygulanmaz). Kullanıcı açıkça "süre hesapla" demese bile,
  dosyada bir süre/zamanaşımı söz konusuysa tetikle.
---

# oa-sure — Süre ve Usul (Ortak Avukat Lego Parçası)

Bu, **sök-tak (composable)** bir parçadır. Tek başına da çalışır, `ortak-avukat` çekirdek kimliğiyle birlikte de. Görevi tek ve nettir: **süre, dosyadaki telafisi olmayan tek hatadır** — onu deterministik hesaplar, usul tuzaklarını işaretler.

## Ne zaman tetiklenir
Kanun yolu/başvuru/süre içeren her durumda: istinaf, temyiz, AYM bireysel başvuru, itiraz, şikâyet, cevap, dava açma, eski hâle getirme; "süre ne kadar", "ne zaman doluyor", "kaçırdım mı".

## Yönetici ilke
Süreyi **karar tipini ve tebliğ/öğrenme tarihini teyit etmeden** beyan etme. Süre miktarı (kaç gün/hafta) ve parasal kesinlik sınırı **resmî kaynaktan (Mevzuat MCP)** doğrulanır; script yalnızca **deterministik aritmetiği** yapar. Otomasyon muhakemeyi besler, yerine geçmez.

## Normatif zemin — hesap HMK bilinciyle yapılır
Script mekaniği şu normlara dayanır ve çıktıda bunları **gerekçelendirir** (kara kutu değil):
- **HMK m.92:** süre, tebliğ/öğrenme gününü izleyen günden işler — tebliğ günü hesaba katılmaz.
- **HMK m.93 (kritik incelik):** resmî tatil günleri **süreye DAHİLDİR** — aradaki bayram/tatil süreyi uzatmaz; yalnızca **SON GÜN** tatile rastlarsa süre, tatili izleyen ilk iş günü mesai bitiminde dolar. ("Araya bayram girdi, süre uzar" yanılgısına düşme/düşürtme.)
- **Tatil günlerinin kaynağı 2429 s.K.:** ulusal bayram, genel tatiller, dini bayramlar (Ramazan 3,5 / Kurban 4,5 — arefeler yarım gün) ve **Pazar**. **Cumartesi** 2429'da sayılmaz; adliyelerin kapalı olması nedeniyle son günün cumartesiye rastlamasında pazartesiye uzama **yerleşik kabul/içtihatla** benimsenir — script bunu uygular ama ihtiyat ilkesi geçerlidir: işlemi son güne, hele cumartesi-kaymasına bırakma; UYAP elektronik kanal 23:59'a kadar açıktır.
- **HMK m.104 / İYUK m.8-3:** adli tatil / çalışmaya ara uzatmaları (yalnız usul sürelerinde; rejim farkı script'te ayrı işlenir).
- **Arefe yarım günleri** süreyi kaydırmaz (tabloya girilmez) — yalnız fiilî erişim riski olarak notlanır.

## E-tebligat başlangıç protokolü (7201 m.7/a · VUK m.107/A — saha dersi)
E-tebligatta süre başlangıcı iki FARKLI tarihe karışabilir: (a) belgenin muhatabın UETS adresine ULAŞTIĞI tarih, (b) TEBLİĞ SAYILMA tarihi — ulaşmayı İZLEYEN BEŞİNCİ GÜNÜN SONU (erken açılıp okuma süreyi öne almaz). Dosya/kullanıcı "e-tebliğ edildi" dediğinde hangi tarih olduğu SORULUR veya UETS kaydından teyit edilir; belirsiz kalıyorsa `--uets` ile İKİ SENARYOLU hesap yapılır.

**DAYANAK KOLA GÖRE DEĞİŞİR (v0.5.14; MCP teyitli 2026-08-31 — aritmetik aynı, NORM farklı):**
- **Adli/idari tebligat (UYAP-UETS): 7201 s.K. m.7/a** — *elektronik adrese ULAŞTIĞI tarihi izleyen beşinci günün sonunda* yapılmış sayılır.
- **Vergi idaresinin elektronik tebliği: VUK m.107/A** (7201 m.7/a DEĞİL) — *sistemle muhatabına İLETİLDİĞİ tarihi izleyen beşinci günün sonunda*. Madde **24/6/2026 tarihli 7587 s.K. ile yeniden düzenlenmiştir**: zorunlu mükellef kapsamı ve sistemden çıkış hâlleri kullanım anında teyit edilir. Script `--uets` çıktısında dayanağı seçilen kurala göre gösterir; dosyada fiilen hangi rejimin uygulandığını **teyit et** (yanlış norm dilekçeye girer, aritmetik doğru olduğu için hata sessiz kalır).

**GÜVENLİ TARAF — TEK TANIM, AMACA GÖRE AYRILIR (v0.5.14'te script ile hizalandı; denetim A-4):**
- **BİZİM süremizde** (kanun yolu/başvuru): güvenli taraf **ERKEN son gündür** — verilen tarih tebliğ-sayılma kabul edilerek çıkan senaryo. Karine (ulaşma+5) senaryosu tanım gereği **5 gün daha geçtir**; ona güvenip beklemek, girilen tarih zaten tebliğ-sayılma tarihiyse süreyi 5 gün AŞMAK demektir. Geç senaryo yalnız **not** düşülür.
- **KARŞI TARAFA kesin dil kurarken** (`--islem`): "süre kaçırılmıştır" hükmü ancak **her iki senaryo da aşılmışsa** yazılır — karine hukuken geçerli tebliğ tarihidir. Yalnız biri aşılmışsa ara tespit + teyit şerhi.

## Çift yönlü süre bilinci — karşı tarafın kaçırdığı süre SİLAHTIR
Süre yalnızca bizim riskimiz değildir. **Bir dava/dosya/ihtilaf incelenirken karşı tarafın süreye bağlı her işlemi de aynı deterministik hesapla denetlenir** — kullanıcı istemese bile, dosyada karşı tarafın tarihli bir işlemi görünür görünmez:
1. **Tara:** karşı tarafın süreli işlemlerini belirle — cevap dilekçesi (HMK m.127), ilk itirazlar (m.116-117), istinaf/temyiz (m.345/361), bilirkişi raporuna itiraz (m.281/2 hafta), ıslah sınırları, icra itirazı (İİK m.62 — 7 gün), ödeme emrine itiraz (6183 m.58 — 15 gün), idari dava süreleri (İYUK m.7) vb.
2. **Hesapla:** `--islem` ile fiilî işlem tarihini son güne karşı dene: `python scripts/hesapla_sure.py --teblig 2026-04-01 --kural hmk_istinaf --islem 2026-04-20`
3. **Kaçırma varsa ÇALIŞMAYA EKLE — net ve kesin dille:** "süresinden sonra yapılmıştır", "süreden reddi gerekir", "HMK m.128 uyarınca davacının vakıalarını inkâr etmiş sayılır", "m.117/2 uyarınca dinlenemez" — tereddütlü ("olabilir", "değerlendirilebilir") dil KULLANILMAZ. **Kesinliğin tek şartı:** karşı tarafa yapılan tebliğin tarihi **belgeli** (tebliğ şerhi / mazbata / UYAP kaydı) olmalıdır; teyitsizse tespit "tebliğ şerhinin teyidi kaydıyla" formülüyle yazılır ve teyit açık uç olarak işaretlenir.
4. **Cephanelik İSTİSNASI:** karşı tarafın süre kaçırması gizli cephaneliğe GİRMEZ. Bu bir savunma hazırlığı değil, **aktif usul itirazıdır** — bekletmek hak kaybettirir (cevaba cevapta, istinafa cevapta, ilk oturumda derhâl ileri sürülür). Script çıktısındaki hesap satırları (m.92/93/104 gerekçeli) dilekçedeki süre paragrafının iskeletidir → `oa-dilekce`.
5. **Sonucu doğru bağla:** her kaçırmanın usuli sonucu farklıdır (ret / inkâr sayılma / dinlenmeme / kesinleşme) — sonucu ilgili normdan `oa-ictihat` üzerinden teyit ederek yaz, ezberden genelleme yapma.

## İş akışı
1. **Yargı kolu + karar tipini** belirle → uygulanacak süre kuralını **Mevzuat MCP'den teyit et** (çıpalar için `references/sure-cizelgesi.md`).
2. **Süre yalnızca HMK/CMK/İYUK'tan ibaret DEĞİLDİR.** Süre/hak düşürücü/zamanaşımı kuralı **maddi hukuk mevzuatında** da olabilir: TBK (ör. m.39 iptal, m.82 sebepsiz zenginleşme, m.72 haksız fiil, m.146 genel zamanaşımı), TMK (ör. m.571 mirasçılıktan çıkarma), TTK (ör. m.23/c fatura itirazı, m.749/m.814 kambiyo), 6183 (ör. m.58 ödeme emrine itiraz), ve diğer kanun/yönetmelikler. **Hangi mevzuatın hangi maddesi süreyi koyuyor — Mevzuat MCP'den bul ve teyit et;** ezberden süre beyan etme.
3. **Tebliğ/öğrenme/başlangıç tarihini** netleştir. **Maddi hukuk sürelerinde başlangıç çoğu kez tebliğ değildir** (muacceliyet, öğrenme, fiil/zarar tarihi); doğru başlangıç anını teyit et. Yoksa **açık uç** işaretle.
4. **Deterministik hesap** için scripti çalıştır — **usul mu maddi mi olduğunu `--tur` ile belirt:**
   ```bash
   # USUL süresi (kanun yolu/başvuru — adli tatil uygulanır):
   python scripts/hesapla_sure.py --teblig 2026-05-20 --kural hmk_istinaf
   python scripts/hesapla_sure.py --teblig 2026-07-15 --kural iyuk_istinaf --yargi idari
   # MADDİ HUKUK süresi (zamanaşımı/hak düşürücü — adli tatil UYGULANMAZ):
   python scripts/hesapla_sure.py --teblig 2020-05-01 --sure 10 --birim yil --tur maddi   # TBK m.146
   python scripts/hesapla_sure.py --teblig 2025-03-10 --sure 6 --birim ay --tur maddi     # ör. 6 ay
   ```
   Birimler: `gun · hafta · ay · yil`. Script tebliğ+1 (HMK m.92 / CMK m.39/1), süre ekleme, hafta sonu + resmî tatil (HMK m.93 · İYUK m.8/2 · CMK m.39/4), ve **usul sürelerinde** adli tatil/çalışmaya arayı yargı koluna göre AYRI işler. **Maddi hukuk sürelerinde (`--tur maddi`) adli tatil uygulanmaz** (usul süresi değildir); yalnız son gün tatile rastlarsa kayar.

4b. **`--yargi` ZORUNLU BİLİNÇTİR — üç kol, ÜÇ FARKLI ADLİ TATİL UZATMASI (v0.5.14; MCP teyitli):**
   ```bash
   # CEZA — CMK m.331/4: tatilin bittiği günden ÜÇ GÜN (hukuktan 4 gün KISA)
   python scripts/hesapla_sure.py --teblig 2026-07-14 --kural cmk_istinaf --yargi ceza   # → 2026-09-03
   # CMK m.268 itiraz ÖĞRENME gününden işler (m.273/291 ise gerekçeli karar tebliğinden):
   python scripts/hesapla_sure.py --teblig 2026-07-14 --kural cmk_itiraz --yargi ceza --baslangic-turu ogrenme
   ```
   - **hukuk:** HMK m.102/104 → 31 Ağu + **bir hafta**. **idari:** İYUK m.61 / m.8/3 → ara bitimini izleyen tarihten **yedi gün**. **ceza:** CMK m.331/4 → tatilin bittiği günden **ÜÇ GÜN**.
   - `cmk_*` kuralı ceza kolu dışında (veya ceza kolu ceza-dışı kuralla) seçilirse script **HESABI DURDURUR** — sessiz yanlış varsayılan yasağı: uyarı basıp devam etmek, yanlış son günü hem ekrana hem `_oa/sureler.json` defterine yazardı.
   - **CMK m.331/2-3:** soruşturma, **tutuklu** işlere ilişkin kovuşturmalar ve ivedi işler tatilde de yürütülür (HSK belirler); BAM/Yargıtay tatilde yalnız tutuklu hükümleri inceler. Bu, hangi **İŞLERİN** görüleceğine dairdir — **süre uzaması her hâlde f.4'e tabidir.** Tutukluda ayrıca **CMK m.263** (kurum müdürüne başvuru süreyi KESER) kontrol edilir.

4c. **Yardımcı bayraklar — bayraksız hesap her zaman güvenli taraftır (v0.5.14; B-19):**
   ```bash
   # --baslangic-turu: aritmetiği DEĞİŞTİRMEZ; süreyi başlatan olayı görünür kılar,
   # kuralın izinli türleriyle çelişirse UYARIR ("belirsiz" → iki senaryo + ERKEN tarih)
   python scripts/hesapla_sure.py --teblig 2026-03-02 --kural hmk_istinaf --baslangic-turu tefhim
   # --adli-tatil-istisna: HMK m.103 (hukuk) / İYUK m.62 (idari) kapsamındaki işlerde
   # adli tatil UZATMASI UYGULANMAZ — ham bitiş korunur, yalnız tatil günü kayması yapılır
   python scripts/hesapla_sure.py --teblig 2026-07-15 --kural hmk_istinaf --adli-tatil-istisna
   # --uets: e-tebligatta iki senaryo (ulaşma günü esas / ulaşma+5. gün karinesi)
   python scripts/hesapla_sure.py --teblig 2026-08-10 --kural iyuk_dava_vergi --yargi idari --uets
   ```
   - **`--adli-tatil-istisna` KAPSAMI — HMK m.103/1 bentleri (hukuk kolu):** (a) ihtiyati tedbir/ihtiyati haciz/delil tespiti gibi geçici hukuki koruma, deniz raporu ve dispeçci atanması talepleri ile bunlara karşı itiraz ve başvurular; (b) her çeşit **nafaka** davaları ile **soybağı, velayet ve vesayete** ilişkin dava/işler; (c) nüfus kayıtlarının düzeltilmesi; (ç) hizmet akdi veya iş sözleşmesi sebebiyle **işçilerin açtıkları** davalar; (d) ticari defter kaybı/kıymetli evrak iptali; (e) iflas, konkordato, yeniden yapılandırma; (f) adli tatilde yapılmasına karar verilen keşifler; (g) tahkim; (ğ) çekişmesiz yargı işleri; (h) kanunen veya mahkeme kararıyla ivedi olan dava/işler.
     **DAVACI SIFATINI TEYİT ET:** (ç) bendi *"işçilerin açtıkları davalar"* lafzıyla davacı sıfatına bağlıdır — **işverenin** açtığı iş davası bu bende girmez. Kapsam dışı bir işte bayrağı kullanmak süreyi 7 gün **yanlış kısaltır**; tereddütte bayrağı KALDIR.
   - **İdari kolda aynı bayrak İYUK m.62'yi uygular** (HMK m.103 kataloğu idari yargıda geçerli DEĞİLDİR): nöbetçi mahkeme ara verme süresinde (a) yürütmenin durdurulmasına ve delillerin tespitine ait işleri, (b) kanunen belli süre içinde karara bağlanması gereken işleri görür.
   - **Ceza kolunda CMK m.331/4'ün lafzında istisna YOKTUR** — bayrağı ceza dosyasında kullanmak süreyi üç gün kısaltır ve dayanağı yoktur; script bunu açıkça uyarır.

4d. **İdari/vergi kanadında iki kör nokta — çizelgeden oku (v0.5.14):**
   - **Yürütmenin durdurulması (İYUK m.27):** dava açmak yürütmeyi **durdurmaz** (f.1); **ödeme emri bir TAHSİLAT işlemidir** ve açılan dava tahsili durdurmaz (f.4) → ayrıca YD istenir, yoksa dava sürerken haciz/satış yürür. YD reddine **itiraz 7 gün, bir defaya mahsus** (f.7 — `iyuk_yd_itiraz`); aynı sebeple ikinci istem yok (f.10). **İvedi yargılama (m.20/A-2/e) ve merkezî sınav (m.20/B-1/d) davalarında YD kararına itiraz EDİLEMEZ.**
   - **Özel yargılama usulleri:** dava m.20/A (ihale, **acele kamulaştırma**, ÖYK, turizm, ÇED, 6306) veya m.20/B (MEB-ÖSYM merkezî/ortak sınav) kapsamındaysa süre 60 gün DEĞİL, **30** (`iyuk_dava_ivedi`) veya **10** (`iyuk_dava_sinav`) gündür; ivedide **istinaf yolu kapalıdır (m.45/8)** ve her ikisinde **m.11 uygulanmaz**.
5. **Maddi hukuk uyarısı:** Script zamanaşımının **kesilmesini/durmasını** (TBK m.153-158) ve hak düşürücü sürenin durmazlığını **hesaplamaz** — bunları elle değerlendir. Zamanaşımı mı hak düşürücü mü olduğunu teyit et (sonuçları farklı: hak düşürücü süre def'i değil, re'sen dikkate alınır).
5b. **Süre pencere bindirme (M5, Paket D — v0.5.5):** dosyada AYNI ANDA işleyen birden fazla süre varsa (ör. cevap süresi + karşı tarafın istinaf süresi + bilirkişi rapor itiraz süresi aynı döneme denk geliyorsa), her birini kaydeden bir JSON (`[{"ad":..., "teblig":..., "kural":... | "sure"+"birim":...}, ...]`) hazırlanıp `python scripts/hesapla_sure.py --pencereler <json>` çalıştırılır — script HER kaydı `hesapla()` ile (aynı deterministik mantık) çözer ve `[teblig+1, son_gün]` pencerelerinin PAIRWISE çakışıp çakışmadığını raporlar; `oa-illiyet`'in zaman katmanındaki tetikleyici olaylar bu JSON'un girdisidir. Çakışma tespit edilirse ÖNCELİKLENDİRME avukat muhakemesidir — script yalnız çakışmayı gösterir.
6. **Tatil tablosu (`scripts/tatiller.json`) güncellenebilir:** sabit ulusal tatiller hazır; **kayan dini bayramları (Ramazan/Kurban)** resmî kaynaktan (Diyanet/Resmî Gazete) yıl bazında ekle — tabloya tahmin YAZMA. **Gelecek yıllar (ör. 2032) tablodan bağımsız çalışır:** script, tanımsız yıllarda aritmetik hicri hesapla (1-3 Şevval / 10-13 Zilhicce) TAHMİNİ bayram penceresi üretir ve son gün bu pencereye bitişikse uyarır — tahmine dayanarak kaydırma yapmaz; herhangi bir yılın tahminleri `--bayram YYYY` ile listelenir, Diyanet teyidi sonrası tabloya işlenir.
7. **İdari izin katmanı — iki kaynaklı tarama (kanun + CB tasarrufları):** Tatil rejimi yalnızca 2429 sayılı Kanun'dan ibaret değildir; her yıl Cumhurbaşkanlığı tasarrufuyla **idari izin** ilan edilebilir (köprü günleri, arife sabahları). **Terim ayrımı (karıştırma):** üç ayrı CB enstrümanı vardır ve hukuki nitelikleri farklıdır — **Cumhurbaşkanlığı Kararnamesi (CBK)** (AY m.104/17 düzenleyici işlem), **Cumhurbaşkanı Kararı** (idari tasarruf), **Cumhurbaşkanlığı Genelgesi** (iç düzen işlemi). İdari izin ilanının formu yıldan yıla değişebilir; bu yüzden taramada tek enstrümana kilitlenme — **üçünü birden tara:** Mevzuat MCP `search_cbk` + `search_cbbaskankarar` + `search_cbgenelge` (yıl + "idari izin"); ilan varsa `tatiller.json`'ın `idari_izin` bölümüne salt-ISO işle. **Hukuki kural:** idari izin, hangi enstrümanla ilan edilirse edilsin, 2429 anlamında resmî tatil DEĞİLDİR; **süreyi UZATMAZ, süreden sayılır.** Script bu günlerde son günü kaydırmaz, yalnızca uyarır: kurumlar fiilen kapalı olabilir (fiziki işlem/harç riski) → işlemi öne al veya UYAP elektronik kanalını (23:59) kullan; fiilî imkânsızlıkta eski hâle getirme (HMK m.95 vd.) ihtiyatla değerlendirilir — ona güvenerek beklenmez.
8. **Yerel deftere MEKANİK yaz (önemli):** Hesaplanan son gün `oa_hafiza.py sure-flag --tarih YYYY-AA-GG --aciklama "..." --kural <kural>` ile YEREL hafızaya (`_oa/sureler.json`) mekanik olarak işlenir — halüsinasyon çıpası (`_oa/dosya.md` süre özeti buna işaret eder ve her oturum açılışında taranır). **Dış takvim/hatırlatıcı eşgüdümü AVUKAT tarafından ELLE yapılır — `event_create`/`reminder_create` ÇAĞRILMAZ** (kurucu karar: YOL-HARİTASI §0). Takvim/hatırlatıcı aracı ortamda yoksa/kurulamıyorsa bu AÇIKÇA söylenir ve kullanıcıdan elle kurması istenir — disk pasiftir, kimseyi dürtmez. **Oturum açılışı refleksi:** her oturum başında `python scripts/sure_nobetci.py --kok .` çalıştırılır — `_oa/sureler.json` defterindeki TÜM süreleri bugüne göre tek komutla tarar ve sıralar; GEÇMİŞ/BUGÜN/YAKLAŞAN (D-7 içi) bir süre varsa exit 3 döner ve diğer her işin önüne geçer (sessiz kaçış yok).
9. Çıktıdaki **son günü ve uyarıları** müvekkile karar-malzemesi olarak sun.

## Çıktı kuralı
Her süreli işin başında net satır: *"[Karar tipi] — [yargı kolu] — süre: [X]; başlangıç: [tarih]; hesaplanan son gün: [tarih] (adli tatil/tatil günü kontrol edildi). Uyarılar: [...]"*

## Aktif çıkarım refleksi
Süreyi edilgen hesaplamakla bitirme. **Zamanlamanın kendisi bir kaldıraçtır:** bir mevzuat/parasal eşik değişikliği başvuruyu öne almayı mı geç bırakmayı mı gerektiriyor? Gerçekleşmiş örnek: 6183 m.48 tecil eşiğinin 1 milyon TL'ye / 72 aya çıkması (7579 sayılı Kanun, RG 22.05.2026) — değişiklik **beklenirken** bir kamu alacağı yapılandırma başvurusunu yürürlük sonrasına bırakmak somut kazanım sağlayabilir; **ertelenmiş yürürlük** de aynı kaldıracın tersidir (ör. Kamulaştırma m.10 AYM iptali, yürürlük 21.02.2027 — o tarihe kadar eski rejim geçerli). Erken başvurunun/feragatin lehe veya aleyhe etkisi var mı? Süre dolmadan atılabilecek lehe bir adım (ihtiyati tedbir, durdurma, eski hâle getirme) var mı? Bunları kendiliğinden müvekkile sun.

## Kompozisyon (takım oyunu)
- `ortak-avukat` (çekirdek kimlik) bir dosyada süre gündeme geldiğinde bu parçayı çağırır.
- `oa-dilekce` ile birlikte: dilekçe yazımında süre satırını bu parça üretir.
- Bağımsız: yalnızca "şu kararın istinaf süresi" sorusunda da tek başına çalışır.

## Öğrenme günlüğü — bu parça nasıl gelişir
Bu dosya **dosya tecrübesiyle büyür.** Yeni bir süre kuralı, daire kayması, mevzuat değişikliği veya tuzak öğrenildiğinde:
1. `references/sure-cizelgesi.md`'ye ekle (gerekirse `scripts/hesapla_sure.py`'deki `KURALLAR` tablosunu güncelle).
2. Aşağıdaki **Değişiklik Günlüğü**'ne tek satır işle.
3. Parçayı yeniden paketle.

Bu, "skill yönlendirmelerime ve yaptığımız işlere göre gelişsin" mekanizmasının somut hâlidir: değişiklikler burada kalıcılaşır, kaybolmaz.

## Anayasal düstur — usul esasa üstündür
Usulün esasa takaddümü ailenin anayasal düsturudur: usulden düşen dosya esasa hiç giremez; süre, usul hukukunun parçası ve telafisiz tek hatadır. Bu parça düsturun **nöbetçisidir**: hem bizim sürelerimizi (savunma) hem `--islem` ile karşı tarafınkini (taarruz) aynı deterministik disiplinle denetler. Süre gündeme geldiği an diğer her işin önüne geçer.

## Anayasal bloklar — tek kaynak (anayasa.md)
Bu parça, ailenin ortak anayasal ilkelerine tabidir — **Çaba/token standardı** (model/efor kullanıcının tercihi; muhakemede/doğrulamada/çıktı kalitesinde tasarruf YOK, yalnız mekanik katmanda kayıpsız verimlilik), **Örnekleme ilkesi** (konu sınırlaması yok — kapsam TÜM Türk hukuku), **Doğaçlama meşruiyeti** (yöntem serbest, olgu MCP-teyitli), ayrıca Doğrulama mimarisi, Anonimleştirme ve Layer 0 gizlilik. **Tek ve yetkili kaynak: `ortak-avukat/references/anayasa.md`.** (Bu parça alt-ajan olarak koşarken bu ilkeler `oa-pipeline/scripts/oa_hafiza.py ajan-brif` ile taşınır.)

## Başbakan denetimi (anayasal)
Bu parça, ailenin Başbakanı `oa-pipeline`'ın icra+denetimine tabidir: çağrıldığında disiplini İSTİSNASIZ ve tam işletilir (ama/fakat/token-tasarrufu gerekçesiyle kestirme YASAK). Görev savsaklanmaz; gerçekten yapılamayan bir şey varsa dürüstçe belirtilir ("yaptım" denmez) ve alternatif yöntem üretilir. Önemli olan proses ve çıktı kalitesidir.

## Fiziksel aktivasyon — simülasyon yasağı (anayasal)
Bu parça yalnızca ÜÇ kanıttan en az biriyle "çalıştı" sayılır: (1) Skill aracıyla FİİLEN çağrıldı ve bu gövde bağlama yüklendi (kullanıcının `/oa-sure` komutuyla eşdeğer); (2) scripti gerçekten koştu ve çıktısı görünür; (3) gerektirdiği MCP çağrısı fiilen yapıldı (araç + sorgu + sonuç kaydıyla). Kısa description her zaman bağlamda durur — o VİTRİNDİR, disiplin değildir; gerçek disiplin bu gövdededir. Bu yüzden hiçbir parça bu parçayı description'ından TAKLİT EDEMEZ; bu parça da başka bir parçanın işine ihtiyaç duyduğunda onu Skill aracıyla fiilen çağırır (olmuyorsa SKILL.md'sini Read ile yükler; o da olmuyorsa "FİZİKEN YÜKLENEMEDİ" diye açıkça yazar). Yapılmamış çağrı 'yapılmış', koşmamış script 'koşmuş' gösterilemez — bu, halüsinasyonun ta kendisidir. Devir alırken/verirken kısa DEVİR PAKETİ (ne yapıldı → ne bekleniyor → hangi kanıt) kullanılır ve pipeline defterine (`oa-pipeline/scripts/pipeline_kayit.py`) işlenir. Bu parçanın ürettiği her kalıcı çıktı (JSON/rapor/devir paketi) çalışılan klasörün `_oa/` yerel hafıza kökünde yaşar (yapı: `oa-pipeline` → Çalışma Kökü).

## Değişiklik Günlüğü
Tam günlük `references/degisiklik-gunlugu.md`'dedir (bağlam ekonomisi için ayrıldı — içerik aynen korunur; yeni kayıtlar oraya işlenir). Güncel sürüm: **v3.26**.

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

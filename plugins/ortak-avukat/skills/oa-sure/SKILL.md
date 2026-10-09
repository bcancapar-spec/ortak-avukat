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
Kanun yolu/başvuru/süre içeren her durumda: istinaf, temyiz, AYM bireysel başvuru, itiraz, şikâyet, cevap, dava açma, eski hâle getirme; "süre ne kadar", "ne zaman doluyor", "kaçırdım mı". **Ayrıca takvimsiz, AŞAMA TETİKLİ süreler** (ilk itiraz, delil bildirimi, ıslah, ön inceleme belge sunma, ceza katılma) — bkz. 4e: bunlarda tarih hesaplanmaz, aşama nöbete alınır.

## Yönetici ilke
Süreyi **karar tipini ve tebliğ/öğrenme tarihini teyit etmeden** beyan etme. Süre miktarı (kaç gün/hafta) ve parasal kesinlik sınırı **resmî kaynaktan (Mevzuat MCP)** doğrulanır; script yalnızca **deterministik aritmetiği** yapar. Otomasyon muhakemeyi besler, yerine geçmez.

## Normatif zemin — hesap HMK bilinciyle yapılır
Script mekaniği şu normlara dayanır ve çıktıda bunları **gerekçelendirir** (kara kutu değil):
- **HMK m.92:** süre, tebliğ/öğrenme gününü izleyen günden işler — tebliğ günü hesaba katılmaz.
- **HMK m.93 (kritik incelik):** resmî tatil günleri **süreye DAHİLDİR** — aradaki bayram/tatil süreyi uzatmaz; yalnızca **SON GÜN** tatile rastlarsa süre, tatili izleyen ilk iş günü mesai bitiminde dolar. ("Araya bayram girdi, süre uzar" yanılgısına düşme/düşürtme.)
- **Tatil günlerinin kaynağı 2429 s.K.:** ulusal bayram, genel tatiller, dini bayramlar (Ramazan 3,5 / Kurban 4,5 — arefeler yarım gün) ve **Pazar**. **Cumartesi** 2429'da sayılmaz; adliyelerin kapalı olması nedeniyle son günün cumartesiye rastlamasında pazartesiye uzama **yerleşik kabul/içtihatla** benimsenir — script bunu uygular ama ihtiyat ilkesi geçerlidir: işlemi son güne, hele cumartesi-kaymasına bırakma; UYAP elektronik kanal 23:59'a kadar açıktır.
- **HMK m.104 / İYUK m.8-3:** adli tatil / çalışmaya ara uzatmaları (yalnız usul sürelerinde; rejim farkı script'te ayrı işlenir).
- **Arefe yarım günleri** süreyi kaydırmaz (tabloya girilmez) — yalnız fiilî erişim riski olarak notlanır.
- **Adli tatil rejimini KURAL taşır (v0.5.18 / Y-01):** her tarih kuralında `adli_tatil` ∈ {`hmk104`, `iyuk8`, `cmk331`, `uygulanmaz`} + dayanak + teyit durumu vardır; `--kural` verildiğinde rejim kuraldan gelir, `--yargi` yalnız kol beyanıdır. Eski motor rejimi kuralın ön ekinden türetiyordu ve icra sürelerini HMK m.104 ile bir hafta **yanlış uzatıyordu** (10.08 tebliğ → 07.09; doğrusu istinaf 24.08, şikâyet 17.08). **İcra:** icra mahkemesine arz edilen hususlar ivedidir (İİK m.18/1, HMK m.103/1-h) — icra dairesi ve icra mahkemesi sürelerinde adli tatil uzatması YOKTUR (Y. 12. HD E.2025/7548 K.2025/7898; E.2024/7040 K.2024/10869); son gün kayması İİK m.19/3.
- **Kuralsız hesap TEMKİNLİDİR (v0.5.18, Fable denetimi S3):** `--kural` verilmeden `--sure/--birim` ile hukuk ya da idari usul süresi hesaplanırsa HMK m.104 / İYUK m.8/3 uzatması manşete KONMAZ — iki hüküm yalnız kendi kanunlarının tayin ettiği sürelere uygulanır; hâkimin verdiği kesin süre ya da başka kanunun (İİK, İş K., TBK, Av.K.) süresi uzamaz. Manşet uzamasız ERKEN tarihtir, uzamış okuma `alt_son`'da ve «KURALSIZ HESAP» uyarısında görünür (01.08 tebliğ, 15 gün → 17.08; okuma 07.09). Kural tablosunda karşılığı varsa her zaman `--kural` ile hesapla. Ceza kolu bilerek dışarıda: CMK m.331/4 sınırsız yazılmıştır ve tatil içi tebliğin ihtiyat planı zaten vardır.
- **Sınır hâli, arife, parasal kesinlik (v0.5.18, Fable denetimi S1/S2/S4):** ham bitiş tatilden önce olup son gün kaymasıyla 20 Temmuz'a düşerse uzatma okuması `alt_son`'da ve «SINIR HÂLİ» uyarısında görünür, manşet erken kalır. Son gün bayram arifesiyse (tablodaki bayram bloklarından türetilir, tahmin yapılmaz) «ARİFE» uyarısı basılır: fiziki işlem öğleden önce. «PARASAL KESİNLİK» uyarısı yalnız istinaf ve temyiz kurallarında basılır.
- **CMK m.331/4 — tatil İÇİNDE tebliğ (v0.5.18 / Y-02):** "adlî tatile rastlayan süreler işlemez" — tebliğ tatil içindeyse süre tatilde hiç işlemez, TAM süre 31 Ağustos'tan sonra işler (YCGK E.2013/2-272 K.2013/524; YCGK E.2021/319 K.2022/846 — tutuklu işlerde de; AYM Ramazan Seçen, B. No: 2021/37483). Eski daire okumasına göre (süre tatilde de işler; bitiş tatile rastlarsa 31 Ağu + üç gün, rastlamazsa ham bitiş — Y. 11. CD E.2017/14079 K.2018/2400) ERKEN tarih **İHTİYAT PLANI** olarak basılır, deftere ayrı kayıt olur ve `--json` çıktısında `plan_son_gun` olarak taşınır. Tebliğ tatilden önce, bitiş tatil içindeyse kural değişmedi: 31 Ağu + üç gün. **Sınır hâli:** tebliğ 19 Temmuz → süre tatilin ilk günü başlar; manşet ERKEN (31 Ağu + üç gün), YCGK okuması (tam süre) TEYİT BEKLİYOR olarak karşı taraf kapısına girer.

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
1. **Tara:** karşı tarafın süreli işlemlerini belirle — cevap dilekçesi (HMK m.127; basit yargılamada m.317/2), ilk itirazlar (m.116-117), istinaf/temyiz (m.345/361), bilirkişi raporuna itiraz (m.281/2 hafta), ıslah sınırları, icra itirazı (İİK m.62 — 7 gün, `iik_odeme_emrine_itiraz`), ödeme emrine itiraz (6183 m.58 — 15 gün), idari dava süreleri (İYUK m.7) vb.
2. **Hesapla:** `--islem` ile fiilî işlem tarihini son güne karşı dene: `python scripts/hesapla_sure.py --teblig 2026-04-01 --kural hmk_istinaf --islem 2026-04-20`
3. **Kaçırma varsa ÇALIŞMAYA EKLE — net ve kesin dille:** "süresinden sonra yapılmıştır", "süreden reddi gerekir", "HMK m.128 uyarınca davacının vakıalarını inkâr etmiş sayılır", "m.117/2 uyarınca dinlenemez" — tereddütlü ("olabilir", "değerlendirilebilir") dil KULLANILMAZ. **Kesinliğin tek şartı:** karşı tarafa yapılan tebliğin tarihi **belgeli** (tebliğ şerhi / mazbata / UYAP kaydı) olmalıdır; teyitsizse tespit "tebliğ şerhinin teyidi kaydıyla" formülüyle yazılır ve teyit açık uç olarak işaretlenir. **v0.5.18 — script kesin dili kendisi keser** ve "ARA TESPİT — KESİN DİL KULLANMA" basar: başlangıç kanıtı `beyan`/`yok`, tebliğ `supheli`, rejim TEYİT BEKLİYOR/türetilmiş ve işlem iki okumanın arasında, ya da tatil takvimi eksik yılda fark ≤ 10 gün (bkz. 4f ve `references/baslangic-kapisi.md` §3).
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
   Birimler: `gun · isgunu · hafta · ay · yil`. **`isgunu`** hafta sonu ve resmî tatilleri SAYMAZ (4857 m.21/5 "on işgünü" — takvim günüyle arası bir haftaya çıkabilir). Script tebliğ+1 (HMK m.92 / CMK m.39/1), süre ekleme, hafta sonu + resmî tatil (HMK m.93 · İYUK m.8/2 · CMK m.39/4), ve **usul sürelerinde** adli tatil/çalışmaya arayı kuralın kendi rejimine (kural yoksa yargı koluna) göre AYRI işler. **Maddi hukuk sürelerinde (`--tur maddi`) adli tatil uygulanmaz** (usul süresi değildir); yalnız son gün tatile rastlarsa kayar.

4b. **`--yargi` ZORUNLU BİLİNÇTİR — dört kol; `--kural` verildiğinde rejimi KURAL taşır (v0.5.14 → v0.5.18; MCP teyitli):**
   ```bash
   # CEZA — CMK m.331/4: tatilin bittiği günden ÜÇ GÜN (hukuktan 4 gün KISA)
   python scripts/hesapla_sure.py --teblig 2026-07-14 --kural cmk_istinaf --yargi ceza   # → 2026-09-03
   # CEZA — tebliğ tatil İÇİNDE: süre tatilde işlemez (YCGK 2022/846) + İHTİYAT PLANI
   python scripts/hesapla_sure.py --teblig 2026-08-25 --kural cmk_istinaf --yargi ceza   # → 2026-09-14 (ihtiyat/plan 2026-09-08)
   # CMK m.268 itiraz ÖĞRENME gününden işler (m.273/291 ise gerekçeli karar tebliğinden):
   python scripts/hesapla_sure.py --teblig 2026-07-14 --kural cmk_itiraz --yargi ceza --baslangic-turu ogrenme
   # İCRA — adli tatil uzatması YOK (İİK m.18/1); kayma İİK m.19/3
   python scripts/hesapla_sure.py --teblig 2026-08-10 --kural iik_istinaf --yargi icra   # → 2026-08-24 (eski motor YANLIŞ 2026-09-07)
   ```
   - **hukuk:** HMK m.102/104 → 31 Ağu + **bir hafta**. **idari:** İYUK m.61 / m.8/3 → ara bitimini izleyen tarihten **yedi gün**. **ceza:** CMK m.331/4 → tatilin bittiği günden **ÜÇ GÜN** (tebliğ tatil içindeyse tam süre 31 Ağu'dan sonra). **`--yargi icra`:** uzatma **YOK** (kuralsız serbest hesapta da).
   - **Kural düzeyinde rejim (v0.5.18):** `iik_*` ve tedbire itiraz (`hmk_tedbir_itiraz`, HMK m.103/1-a) **uygulanmaz**; 4857 süreleri (`is_*`) **uygulanmaz** (HMK'nın tayin ettiği süre değildir — Y. 9. HD E.2016/1261 K.2016/22196); AİHM (`aihm_basvuru`) uzatma YOK **ve son gün kayması YOK** (Sabri Güneş/Türkiye [BD] §§ 60-61). Rejimi resmî kaynakla **teyit edilemeyen** kurallar (`aym_bireysel`, `aym_bireysel_mazeret`, `iik_itirazin_iptali`, `iik_borctan_kurtulma`, `iik_89_menfi_tespit`, `hmk_tedbir_esas_dava`, `hmk_istifa_vekalet_devam`, `avk_istifa_vekalet_devam`, `iik_icra_ceza_sikayet*`) **TEMKİNLİ**: uzatma uygulanmaz (erken tarih), çıktı "TEMKİNLİ REJİM — TEYİT BEKLİYOR" uyarısı ve uzatmalı alternatif tarihi gösterir; karşı tarafın işlemi iki tarih arasındaysa kesin dil kurulmaz. Çıktıdaki "Adli tatil rejimi" satırı rejimin nereden geldiğini (kural kaydı / `--yargi`) yazar.
   - `cmk_*` kuralı ceza kolu dışında (veya ceza kolu ceza-dışı kuralla) seçilirse script **HESABI DURDURUR** — sessiz yanlış varsayılan yasağı: uyarı basıp devam etmek, yanlış son günü hem ekrana hem `_oa/sureler.json` defterine yazardı. AYM/AİHM kuralları kol-bağımsızdır (ceza dosyasında da hesaplanır); `iik_icra_ceza_sikayet*` ceza koluyla da çalışır.
   - **CMK m.331/2-3:** soruşturma, **tutuklu** işlere ilişkin kovuşturmalar ve ivedi işler tatilde de yürütülür (HSK belirler); BAM/Yargıtay tatilde yalnız tutuklu hükümleri inceler. Bu, hangi **İŞLERİN** görüleceğine dairdir — **süre uzaması her hâlde f.4'e tabidir.** Tutukluda ayrıca **CMK m.263** (kurum müdürüne başvuru süreyi KESER) kontrol edilir.

4c. **Yardımcı bayraklar — tereddütte İKİ hesap, plan ERKEN tarihe (v0.5.14; B-19 → v0.5.18 düzeltmesi):**
   Eski başlıktaki "bayraksız hesap her zaman güvenli taraftır" ifadesi **kendi süremiz için yanlıştı**: HMK m.103 işinde bayraksız hesap adli tatil uzatmasını uygular ve 7 gün **GEÇ** tarih verir. Doğru kural: kendi işlemini ERKEN (bayraklı) tarihe göre planla, ama erken tarih geçti diye hakkı terk etme (bayraksız tarihi de hesapla); karşı tarafa kesin dili ancak GEÇ tarih de aşılmışsa kur.
   ```bash
   # --baslangic-turu: aritmetiği DEĞİŞTİRMEZ; süreyi başlatan olayı görünür kılar,
   # kuralın izinli türleriyle çelişirse UYARIR ("belirsiz" → iki senaryo + ERKEN tarih).
   # Örnek ÇELİŞKİ: HMK m.345 istinaf süresi tefhimden değil YALNIZ TEBLİĞDEN işler (v0.5.18 / Y-03)
   python scripts/hesapla_sure.py --teblig 2026-03-02 --kural hmk_istinaf --baslangic-turu tefhim
   # --adli-tatil-istisna: HMK m.103 (hukuk) / İYUK m.62 (idari) kapsamındaki işlerde
   # adli tatil UZATMASI UYGULANMAZ — ham bitiş korunur, yalnız tatil günü kayması yapılır
   python scripts/hesapla_sure.py --teblig 2026-07-15 --kural hmk_istinaf --adli-tatil-istisna
   # --uets: e-tebligatta iki senaryo (ulaşma günü esas / ulaşma+5. gün karinesi)
   python scripts/hesapla_sure.py --teblig 2026-08-10 --kural iyuk_dava_vergi --yargi idari --uets
   ```
   - **`--adli-tatil-istisna` KAPSAMI — HMK m.103/1 bentleri (hukuk kolu):** (a) ihtiyati tedbir/ihtiyati haciz/delil tespiti gibi geçici hukuki koruma, deniz raporu ve dispeçci atanması talepleri ile bunlara karşı itiraz ve başvurular; (b) her çeşit **nafaka** davaları ile **soybağı, velayet ve vesayete** ilişkin dava/işler; (c) nüfus kayıtlarının düzeltilmesi; (ç) hizmet akdi veya iş sözleşmesi sebebiyle **işçilerin açtıkları** davalar; (d) ticari defter kaybı/kıymetli evrak iptali; (e) iflas, konkordato, yeniden yapılandırma; (f) adli tatilde yapılmasına karar verilen keşifler; (g) tahkim; (ğ) çekişmesiz yargı işleri; (h) kanunen veya mahkeme kararıyla ivedi olan dava/işler.
     **DAVACI SIFATINI TEYİT ET:** (ç) bendi *"işçilerin açtıkları davalar"* lafzıyla davacı sıfatına bağlıdır — **işverenin** açtığı iş davası bu bende girmez. Kapsam dışı bir işte bayrak süreyi 7 gün **kısa** gösterir (karşı tarafa kesin dil kurarken yanlış olur); kapsam içi bir işte bayraksız hesap 7 gün **GEÇ** tarih verir (kendi süren için tehlikeli). Tereddütte iki hesabı da yap: kendi işlemin ERKEN tarihe, karşı tarafa kesin dil GEÇ tarihe göre.
   - **İdari kolda aynı bayrak İYUK m.62'yi uygular** (HMK m.103 kataloğu idari yargıda geçerli DEĞİLDİR): nöbetçi mahkeme ara verme süresinde (a) yürütmenin durdurulmasına ve delillerin tespitine ait işleri, (b) kanunen belli süre içinde karara bağlanması gereken işleri görür.
   - **Ceza kolunda CMK m.331/4'ün lafzında istisna YOKTUR** — bayrağı ceza dosyasında kullanmak süreyi üç gün kısaltır ve dayanağı yoktur; script bunu açıkça uyarır.

4d. **İdari/vergi kanadında iki kör nokta — çizelgeden oku (v0.5.14):**
   - **Yürütmenin durdurulması (İYUK m.27):** dava açmak yürütmeyi **durdurmaz** (f.1); **ödeme emri bir TAHSİLAT işlemidir** ve açılan dava tahsili durdurmaz (f.4) → ayrıca YD istenir, yoksa dava sürerken haciz/satış yürür. YD reddine **itiraz 7 gün, bir defaya mahsus** (f.7 — `iyuk_yd_itiraz`); aynı sebeple ikinci istem yok (f.10). **İvedi yargılama (m.20/A-2/e) ve merkezî sınav (m.20/B-1/d) davalarında YD kararına itiraz EDİLEMEZ.**
   - **Özel yargılama usulleri:** dava m.20/A (ihale, **acele kamulaştırma**, ÖYK, turizm, ÇED, 6306) veya m.20/B (MEB-ÖSYM merkezî/ortak sınav) kapsamındaysa süre 60 gün DEĞİL, **30** (`iyuk_dava_ivedi`) veya **10** (`iyuk_dava_sinav`) gündür; ivedide **istinaf yolu kapalıdır (m.45/8)** ve her ikisinde **m.11 uygulanmaz**.
4f. **BAŞLANGIÇ KAPISI — hangi olay, hangi kanıt (v0.5.18; Yargı PRO 12-2/12-3 fikrinin OA uyarlaması):**
   Yanlış olaya bağlanan doğru hesap yanlış hesaptır. Hesaba girmeden önce dört soru sorulur — **hangi olay** (kuralın `izinli_baslangic_turleri`), **hangi kanıt**, **tebliğ geçerli mi**, **belirsizlik varsa iki senaryo** — ayrıntı ve normlar `references/baslangic-kapisi.md`'dedir (7201 s. TK m.7/a, 11, 21, 31, 32, 35, 36 — MCP teyitli 2026-10-05). Kapı aritmetiği DEĞİŞTİRMEZ; çelişkiyi görünür kılar ve karşı tarafa kesin dili keser.
   ```bash
   python scripts/hesapla_sure.py --teblig 2026-05-20 --kural hmk_istinaf --baslangic-kaniti uets-kaydi   # iki senaryo kendiliğinden
   python scripts/hesapla_sure.py --teblig 2026-03-02 --kural hmk_istinaf --baslangic-kaniti tefhim-tutanagi   # → KANIT ↔ KURAL ÇELİŞKİSİ
   python scripts/hesapla_sure.py --teblig 2026-03-02 --kural hmk_istinaf --teblig-durumu supheli   # → "İHTİYAT HEDEFİ", tek kesin tarih YOK
   ```
   - `--baslangic-kaniti`: `mazbata` · `uets-kaydi` · `kalem-tevdi` · `ilan` · `tefhim-tutanagi` · `uyap-erisim-kaydi` · `kesinlesme-serhi` · `beyan` · `yok`. Kanıtın işaret ettiği olay kuralın izinli türünde değilse **KANIT ↔ KURAL ÇELİŞKİSİ**; `beyan`/`yok` → **KANITSIZ BAŞLANGIÇ** (hesap ihtiyat amaçlı, karşı tarafa kesin dil kapalı).
   - `--teblig-durumu`: `gecerli` · `usulsuz` (TK m.32: muttali olunan tarih tebliğ tarihidir → `--baslangic-turu ogrenme`) · `supheli` (çıktı satırı ">>> İHTİYAT HEDEFİ"; defter kaydı `[İHTİYAT HEDEFİ — ŞÜPHELİ TEBLİĞ]` etiketli).
   - **AYM** (`aym_bireysel`): süre başvuru yollarının tüketilmesinden; AYM kararlarında nihai kararın UYAP'tan öğrenildiği tarih olay olarak kaydedilir (Ramazan Seçen § 9) — genel ilke **TEYİT BEKLİYOR**, erken öğrenme kanıtı varsa onu gir. **AİHM** (`aihm_basvuru`, 4 ay): iç hukukta yazılı tebliğ öngörülüyorsa **tebliğ** esastır (Sabri Güneş § 53); süre her dosyada **dört aydır** — 1.2.2022 öncesi altı ay geçişi kapsam dışıdır (avukat kararı 2026-10-06; `oa-usul` [G11] ile aynı).
4g. **Kural tablosu genişledi (v0.5.18 / Y-04, Y-05 — Mevzuat MCP teyitli 2026-10-05; K1 istifa kuralları 2026-10-07):**
   | Aile | Yeni kurallar |
   |---|---|
   | İcra (rejim: uygulanmaz) | `iik_temyiz` (m.364/2, 2 hafta) · `iik_odeme_emrine_itiraz` (m.62/1, 7 gün) · `iik_gecikmis_itiraz` (m.65/2, 3 gün) · `iik_itirazin_kaldirilmasi` (m.68/1, 6 ay) · `iik_89_ihbarname_itiraz` (m.89, 7 gün) · `iik_ihalenin_feshi` (m.134/2, 7 gün) + `_azami` (1 yıl) · `iik_kambiyo_itiraz` (m.168, 5 gün) · `iik_ihtiyati_haciz_itiraz` (m.265, 7 gün) |
   | İcra — rejim TEYİT BEKLİYOR (temkinli) | `iik_itirazin_iptali` (m.67/1, 1 yıl) · `iik_borctan_kurtulma` (m.69/2, 7 gün) · `iik_89_menfi_tespit` (m.89/3, 15 gün) · `iik_icra_ceza_sikayet` (m.347, 3 ay) + `_azami` (1 yıl) |
   | HMK | `hmk_dosya_gonderme` (m.20/1, 2 hafta) · `hmk_cevap_basit` (m.317/2, 2 hafta; ek süre en çok 2 hafta) · `hmk_on_inceleme_belge_sunma` (m.139/1-ç, 2 hafta KESİN — aşama çatalının tarih ayağı) · `hmk_tedbir_itiraz` (m.394, 1 hafta; uzamaz) · `hmk_tedbir_esas_dava` (m.397/1, 2 hafta; rejim TEYİT BEKLİYOR) |
   | AYM / AİHM | `aym_bireysel_mazeret` (6216 m.47/5, 15 gün) · `aihm_basvuru` (AİHS m.35/1, 4 ay; kayma YOK) |
   | Vekâletin sona ermesi — istifa (K1, 2026-10-07; rejim TEYİT BEKLİYOR) | `hmk_istifa_vekalet_devam` (HMK m.82/1, 2 hafta) · `avk_istifa_vekalet_devam` (Av.K. m.41/1, 15 gün) — ikisi de istifanın müvekkile TEBLİĞİNDEN, EŞİTLENMEZ; süre tatilde İŞLER (m.103/3), m.104 uzatması kararla teyit edilemedi → manşet ERKEN tarih (müvekkile "yeni vekil bu tarihten ÖNCE"), geç okuma (31 Ağu + 1 hafta) yalnız uyarıda (istifa eden avukatın takip sınırı). MK-2 çağrısı bu kurallarla yapılır; kuralsız `--sure` çağrısı yazın GEÇ tarih verir (25.07.2026 → 07.09; doğrusu 10.08) |
   `hmk_istinaf`, `hmk_temyiz`, `iik_istinaf`, `iik_temyiz` yalnız **TEBLİĞDEN** işler (Y-03: tefhim izinli başlangıç değildir).
4e. **AŞAMA TETİKLİ SÜRELER — takvim değil, aşama kapatır (v0.5.16 / I5; P1-3 / A-10; Mevzuat MCP teyit 2026-09-07):**
   Bazı usul "süreleri" için "tebliğ + N gün" sorusunun cevabı YOKTUR; işlem, yargılamanın bir **aşaması** kapanmadan yapılmalıdır. Bunlara tarih üretmek **yanlış tarih üretmektir** (nöbetçi o tarihi otorite sayar, defter kalıcılaştırır). Bu yüzden aşama kuralı `hesapla()`ya hiç girmez: script yalnız aşamayı, bağlı **pipeline adımını** (oa-pipeline ADIMLAR 0-10 — bu adım TAMAMLANMADAN işlem yapılmalı) ve dayanağı basar; `--teblig` gerekmez, verilirse "KULLANILMADI" diye görünür yazılır.
   ```bash
   python scripts/hesapla_sure.py --kural hmk_ilk_itiraz            # → "AŞAMA TETİKLİ: cevap dilekçesi … — pipeline adım 8'e bağlı; tarih yok"
   python scripts/hesapla_sure.py --kural hmk_islah --json          # → {"tur": "asama", "asama": "...", "pipeline_adimi": 6, "son_gun": null, ...}
   python scripts/hesapla_sure.py --kural hmk_delil_bildirimi --kok . # _oa varsa deftere tur=asama kaydı (son_gun YOK)
   ```
   | Kural | Aşama (kapatan olay) | Pipeline adımı | Dayanak (MCP teyit 2026-09-07) |
   |---|---|---|---|
   | `hmk_ilk_itiraz` | cevap dilekçesi | 8 (YAZIM) | HMK m.117/1 — ilk itirazların hepsi cevap dilekçesinde; aksi hâlde dinlenemez (katalog m.116/1; (c) mülga) |
   | `hmk_delil_bildirimi` | dilekçeler aşaması | 8 (YAZIM) — liste adım 4'te kurulur | HMK m.119/1-f · m.129/1-e; sonradan delil yasağı m.145/1 (istisna mahkeme takdirinde — güvenme) |
   | `hmk_on_inceleme_belge` | ön inceleme davetiyesi ihtarı | 4 (OLGU/DELİL) | HMK m.139/1-ç — tebliğden iki haftalık kesin süre; m.140/5 vazgeçmiş sayılma. **ÇATAL:** davetiye tebliğ edilince takvime bağlanır → `--kural hmk_on_inceleme_belge_sunma --teblig <tebliğ>` (v0.5.18) |
   | `hmk_islah` | tahkikat sona erene kadar | 6 (STRATEJİ) | HMK m.177/1 (m.177/2 bozma sonrası; m.176/2 tek hak) |
   | `cmk_katilma` | ilk derece kovuşturması, hüküm verilinceye kadar | 1 (ALIM) | CMK m.237/1-2 — kanun yolunda katılma istenemez |
   - **Ceza deseninin genellenmesi:** `cmk_katilma`, v0.5.13'te `oa-musteki-vekili`nin "katılma anı — olay tetikli kırmızı bayrak" olarak kurduğu kalemin (CMK m.237) ta kendisidir; bu sınıf aynı deseni hukuk koluna (ilk itiraz / delil / ıslah / ön inceleme) taşır. Ceza dosyasında `oa-musteki-vekili` katılma bayrağını bu kuralla deftere işler.
   - **Kol uyuşmazlığı kapısı (A-1) aşama kuralına UYGULANMAZ:** adli tatil aritmetiği olmadığı için `cmk_katilma` `--yargi` değerinden bağımsız çalışır.
   - **`--pencereler`:** aşama kaydı bindirme aritmetiğine katılmaz ama **görünür** atlanır ("≡ … tarih penceresi yok, bindirmeye katılmadı"); JSON çıktısında `asama` listesinde durur. Yalnız aşama kaydı varsa "DENETLENEMEDİ" (exit 1) — kanıt sayılmaz.
   - **Deftere yazım — `_oa/sureler.json` aşama kaydı şeması (`oa_hafiza.py sure-flag` ile AYNI defter/`flagler` listesi):** `son_gun`/`tarih` alanı **YOKTUR** — alanlar: `"tur": "asama"`, `"asama"` (kapatan aşama), `"pipeline_adimi"` (0-10), `"aciklama"`, `"kural"`, `"kayit"`. Örnek: `{"tur": "asama", "asama": "cevap dilekçesi (dilekçeler aşaması)", "pipeline_adimi": 8, "aciklama": "İlk itiraz … cevap dilekçesiyle (HMK m.117/1)", "kural": "hmk_ilk_itiraz"}`. Yazım yolu: `hesapla_sure.py --kural <asama_kurali> --kok <dava kökü>` (in-process, `_oa` yoksa defter icat edilmez; aynı kural+aşama ikinci kez eklenmez). **Not:** aşama kaydı kanonik yazıcıyla da yazılır (v0.5.16/H1): `oa_hafiza.py sure-flag --asama "<aşama>" --pipeline-adimi N --kural <asama_kurali> --aciklama "..."` — `--pipeline-adimi` ZORUNLU, `--tarih` YASAK (boş/uydurma tarih aşama kaydını takvim kaydına çevirir, yanlış alarm). JSON'a elle yazılmaz.
   - **Nöbetçi:** `sure_nobetci.py` aşama kayıtlarını `[≡] AŞAMA TETİKLİ — adım N tamamlanmadan bu işlem yapılmalı: …` ayrı bloğunda gösterir; **tarih sayımına ve acil sınıfına katmaz**, bozuk saymaz; yalnız aşama kaydı varsa exit 0 (exit sözleşmesi 0/3/1 değişmedi). Aşama kapandıysa (cevap verildi / tahkikat bitti / hüküm verildi) `--iptal <kimlik> --gerekce "..."` ile append-only düşürülür. Aşama sınıfı YALNIZ açık `"tur": "asama"` ile tanınır — tarihsiz ve tur'suz eski kayıt yine BOZUK'tur (fail-closed; eski defterler çökmez).
5. **Maddi hukuk uyarısı:** Script zamanaşımının **kesilmesini/durmasını** (TBK m.153-158) ve hak düşürücü sürenin durmazlığını **hesaplamaz** — bunları elle değerlendir. Zamanaşımı mı hak düşürücü mü olduğunu teyit et (sonuçları farklı: hak düşürücü süre def'i değil, re'sen dikkate alınır).
5b. **Süre pencere bindirme (M5, Paket D — v0.5.5):** dosyada AYNI ANDA işleyen birden fazla süre varsa (ör. cevap süresi + karşı tarafın istinaf süresi + bilirkişi rapor itiraz süresi aynı döneme denk geliyorsa), her birini kaydeden bir JSON (`[{"ad":..., "teblig":..., "kural":... | "sure"+"birim":...}, ...]`) hazırlanıp `python scripts/hesapla_sure.py --pencereler <json>` çalıştırılır — script HER kaydı `hesapla()` ile (aynı deterministik mantık) çözer ve `[teblig+1, son_gün]` pencerelerinin PAIRWISE çakışıp çakışmadığını raporlar; `oa-illiyet`'in zaman katmanındaki tetikleyici olaylar bu JSON'un girdisidir. Çakışma tespit edilirse ÖNCELİKLENDİRME avukat muhakemesidir — script yalnız çakışmayı gösterir.
6. **Tatil tablosu (`scripts/tatiller.json`) güncellenebilir:** sabit ulusal tatiller hazır; **kayan dini bayramları (Ramazan/Kurban)** resmî kaynaktan (Diyanet/Resmî Gazete) yıl bazında ekle — tabloya tahmin YAZMA. **Gelecek yıllar (ör. 2032) tablodan bağımsız çalışır:** script, tanımsız yıllarda aritmetik hicri hesapla (1-3 Şevval / 10-13 Zilhicce) TAHMİNİ bayram penceresi üretir ve son gün bu pencereye bitişikse uyarır — tahmine dayanarak kaydırma yapmaz; herhangi bir yılın tahminleri `--bayram YYYY` ile listelenir, Diyanet teyidi sonrası tabloya işlenir. **TATİL TAKVİMİ EKSİK (v0.5.18 / Y-08):** son gün (iş günü sayımında aradaki herhangi bir gün) tabloda resmî dini bayram kaydı olmayan bir yıla düşerse rapora "⚠ TATİL TAKVİMİ EKSİK" satırı ve uyarı basılır, deftere `"takvim_eksik": [yıl]` yazılır, nöbetçi kaydı işaretler ve `--islem` 10 günlük farkta kesin dili keser (bayram iş günü sanılmış olabilir → gerçek son gün daha geç olabilir). **2027 dini bayramları** resmî kaynakla teyit edilemediği için (Mevzuat MCP, 2026-10-05) tabloya GİRİLMEDİ — tarih tahmin edilip yazılmaz.
7. **İdari izin katmanı — iki kaynaklı tarama (kanun + CB tasarrufları):** Tatil rejimi yalnızca 2429 sayılı Kanun'dan ibaret değildir; her yıl Cumhurbaşkanlığı tasarrufuyla **idari izin** ilan edilebilir (köprü günleri, arife sabahları). **Terim ayrımı (karıştırma):** üç ayrı CB enstrümanı vardır ve hukuki nitelikleri farklıdır — **Cumhurbaşkanlığı Kararnamesi (CBK)** (AY m.104/17 düzenleyici işlem), **Cumhurbaşkanı Kararı** (idari tasarruf), **Cumhurbaşkanlığı Genelgesi** (iç düzen işlemi). İdari izin ilanının formu yıldan yıla değişebilir; bu yüzden taramada tek enstrümana kilitlenme — **üçünü birden tara:** Mevzuat MCP `mevzuat_ara` (`mevzuat_tur_list: CB_KARARNAME + CB_KARAR + CB_GENELGE`, `phrase: idari izin`, `resmi_gazete_tarihi_start/end` = o yıl); ilan varsa `tatiller.json`'ın `idari_izin` bölümüne salt-ISO işle. **Hukuki kural:** idari izin, hangi enstrümanla ilan edilirse edilsin, 2429 anlamında resmî tatil DEĞİLDİR; **süreyi UZATMAZ, süreden sayılır.** Script bu günlerde son günü kaydırmaz, yalnızca uyarır: kurumlar fiilen kapalı olabilir (fiziki işlem/harç riski) → işlemi öne al veya UYAP elektronik kanalını (23:59) kullan; fiilî imkânsızlıkta eski hâle getirme (HMK m.95 vd.) ihtiyatla değerlendirilir — ona güvenerek beklenmez.
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
1. `references/sure-cizelgesi.md`'ye ekle (gerekirse `scripts/sure_kurallari.json` + `scripts/hesapla_sure.py`'deki gömülü tabloyu **birlikte** güncelle — tarih kuralı `kurallar`/`_GOMULU_KURALLAR`, aşama kuralı `asama_kurallari`/`_GOMULU_ASAMA_KURALLAR`; ikiz kilit testleri yeşil kalmalı).
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


## İŞ MAHKEMESİ SÜRELERİ (4857 / 7036 / 6325 — MCP teyit 2026-09-10)

İş dosyasında tarih aritmetiği **tek başına yetmez**: üç mekanizma hesabın
dışındadır ve script bunları HESAPLAMAZ, yalnız GÖRÜNÜR kılar.

| Kural | Süre | Başlangıç | Dayanak |
|---|---|---|---|
| `is_ise_iade_arabulucu` | 1 ay | fesih bildiriminin **tebliği** | 4857 m.20/1 |
| `is_ise_iade_dava` | 2 hafta | arabuluculuk **son tutanağının düzenlenmesi** (olay) | 4857 m.20/1 |
| `is_ise_iade_arabulucu_ret` | 2 hafta | usulden ret kararının **kesinleşip resen tebliği** | 4857 m.20/1 |
| `is_ise_baslatma_basvuru` | **10 İŞ GÜNÜ** | kesinleşen kararın **tebliği** | 4857 m.21/5 |
| `is_ise_baslatma_isveren` | 1 ay | **işçinin başvurusu** (olay) | 4857 m.21/1 |
| `is_zamanasimi_5yil` | 5 yıl | fesih/muacceliyet (maddi hukuk) | 4857 Ek m.3 |

**Hesabın dışındaki üç mekanizma — hepsi çıktıda uyarı olarak basılır:**

1. **Dava şartı (7036 m.3):** işçi/işveren alacağı, tazminatı ve işe iade
   taleplerinde arabulucuya başvuru **dava şartıdır**; 7445 s.K. m.41 ile
   itirazın iptali, menfi tespit ve istirdat davaları da kapsamda. Son
   tutanağın aslı/onaylı örneği dilekçeye **eklenir**; eksikse dava usulden reddedilir.
2. **Süre durur (6325 m.18/A-15):** arabuluculuk bürosuna başvurudan son
   tutanağa kadar **zamanaşımı durur ve hak düşürücü süre işlemez**. Script bu
   günleri düşmez — arada geçen gün sayısını **elle ekle** ve deftere işle.
3. **Adli tatil:** tablodaki 4857 süreleri HMK'nın tayin ettiği süre değildir —
   kural rejimi **uygulanmaz** (v0.5.18; Y. 9. HD E.2016/1261 K.2016/22196: işe
   iade süresinde m.104 uzatması usul ve yasaya aykırı). Dava açıldıktan sonraki
   HMK süreleri için **HMK m.103/1-ç:** "hizmet akdi veya iş sözleşmesi sebebiyle
   **işçilerin AÇTIKLARI** davalar" tatilde görülür → süre uzamaz
   (`--adli-tatil-istisna`). Bent **davacı sıfatına** bağlıdır: **işverenin**
   açtığı iş davası bu bende girmez, orada uzatma işler.

**İşe iade davasında 2 haftanın başlangıcı TARTIŞMALIDIR.** İstanbul BAM 31. HD
(2020/2741 E., 2021/10 K.) düzenlenme tarihini esas alır; 29. HD (2024/502 E.,
2024/919 K.) imzalar tamamlanmamışsa tamamlanma tarihini sayar. Yargıtay 9. HD
(E.2024/10170, K.2024/14797, 18.11.2024) uyuşmazlığın giderilmesine **yer
olmadığına** karar verdiği için ayrılık **sürmektedir**. Plan **erken** tarihe
(düzenlenme) göre yapılır; geç senaryo yalnız ikincil savunmadır.

```bash
python scripts/hesapla_sure.py --teblig 2026-03-02 --kural is_ise_iade_arabulucu
python scripts/hesapla_sure.py --teblig 2026-04-10 --kural is_ise_iade_dava --baslangic-turu olay
python scripts/hesapla_sure.py --teblig 2026-03-06 --kural is_ise_baslatma_basvuru   # 10 İŞ GÜNÜ
```

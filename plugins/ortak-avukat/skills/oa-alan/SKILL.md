---
name: oa-alan
description: >-
  Ortak Avukat sisteminin ALAN/İHTİSAS DAİRESİ KONUMLANDIRMA parçası. Türk hukukunun
  HERHANGİ bir dalında — bir uyuşmazlığın hangi norma/maddeye bağlandığını ve
  Yargıtay/Danıştay/İstinaf (BAM/BİM) nezdinde hangi İHTİSAS dairesinin baktığını,
  HSK iş bölümü kararları ışığında konumlandırmak için DEVREYE GİR. "Hangi madde
  uygulanır", "hangi daire bakar", "nereden başlamalı" türü her işte tetikle. Alanı
  belirli dallarla SINIRLAMA; mesele çoğu zaman birden çok dalı birden ilgilendirir.
  Ayrıca geçmiş halüsinasyon/yanılma derslerinden çıkan YASAK BÖLGELERİ uygula (ör.
  Danıştay 8. Daire içtihadını hafızadan üretme; daire kaymaları). Kullanıcı alanı
  anmasa bile uyuşmazlık tipi belirginse tetikle. Bağımsız çalışır; `oa-ictihat`
  (sorgu) ve `oa-dilekce` (yazım) ile takım oynar.
---

# oa-alan — Alan ve İhtisas Dairesi Konumlandırma

**Bu bir konumlandırma yöntemidir, ezber alan listesi değil.** Görevi: bir uyuşmazlığı Türk hukukunun **bütünü** içinde konumlandırmak — hangi norm(lar), hangi yargı kolu, ve hangi **ihtisas dairesi**. Her madde/parasal sınır kullanım anında Mevzuat MCP'den, her künye Yargı/Danıştay/AYM MCP'den (`oa-ictihat`) teyit edilir.

## İlke — tüm Türk hukukunu düşün, dalla sınırlama
Meseleyi önceden seçilmiş birkaç dala (iş/ticaret/icra/idare...) **hapsetme.** Türk hukukunun **herhangi** bir dalı devrede olabilir (medeni, borçlar, ticaret, iş, icra-iflas, idare, vergi, ceza, anayasa, aile, miras, eşya, fikrî mülkiyet, gümrük, sosyal güvenlik, tüketici, rekabet, sağlık, çevre, enerji, vb. — bu sayım da tahdit değildir). 

**Çok-dallılık esastır:** bir uyuşmazlık çoğu zaman **birden fazla** dalı aynı anda ilgilendirir; biri çözülürken diğeri gözden kaçabilir. Örn. bir trafik kazası aynı anda haksız fiil (TBK), sigorta/ticaret (TTK), ceza ve sosyal güvenlik (5510 rücu) boyutu taşıyabilir; bir işçi alacağı iş + ticaret (işveren devri) + icra + ceza boyutlu olabilir. Bağlantılı **tüm** dalları aç, sonra her birini `oa-ictihat` ile derinleştir.

## İhtisas dairesi tespiti — HSK iş bölümü ışığında
İçtihat aramasını verimli kılan, baştan **doğru ihtisas dairesini** hedeflemektir. Uyuşmazlık konusuna göre **hangi özel/ihtisas dairesinin** baktığını belirle:
- **Yargıtay** (hukuk/ceza daireleri), **Danıştay** (idari/vergi daireleri), **İstinaf** (BAM hukuk/ceza; BİM idare/vergi) nezdinde uyuşmazlık için **ihtisaslaşmış** daireyi tespit et.
- Bunu **HSK'nın güncel iş bölümü (işbölümü) kararları** ışığında yap — daire görev dağılımı bu kararlarla belirlenir ve **dönemsel değişir** (daire kaymaları buradan doğar). Güncel iş bölümünü `oa-ictihat`/Mevzuat-Resmî Gazete üzerinden teyit et; **hafızadaki daire numarasına güvenme.**
- Doğru daireyi hedeflemek hem aramayı daraltır (gürültüyü azaltır) hem de emsalin gerçekten bağlayıcı/yerinde olmasını sağlar.
- **Daire değişmiş olabilir:** eski künyedeki daire bugün o işe bakmıyor olabilir; güncel iş bölümüyle çapraz doğrula (bilinen örnek: istihkakta görev 8. HD → 12. HD, BGK 18/01/2024).

## Yasak bölgeler — geçmiş halüsinasyon dersleri (bağlayıcı)
- **Danıştay 8. Daire içtihadı hafızadan ÜRETİLMEZ;** yalnızca AYM/Yargı Pro'den teyitliyse kullanılır, değilse dilekçeye girmez (yasak bölge — bilinçle dışlanır).
- **Hiçbir künye (esas/karar no, tarih, daire) hafızadan yazılmaz** — doğrulanana dek iddia.
- **Hiçbir süre/parasal sınır ezberden beyan edilmez** (icra istinafı "10 gün → 2 hafta" tuzağı).
- **Daire kaymalarına dikkat:** istihkak 8. HD → 12. HD (BGK 18/01/2024).
- **Bedesten kapsama boşlukları** (4. HD kısa onama, BAM Ceza yok) bir doktrinin "yok" sanılmasına yol açabilir; yokluğu kesinlemeden alternatif rota dene (`oa-ictihat`).

## FORUM SEÇİMİ — birden fazla yetkili mahkeme varsa (P2-2/A-7, v0.5.16)

Görev/yetki katmanı "hangi mahkeme **bakabilir**" sorusunu kapatır; forum seçimi "**hangisinde açmalıyız**" sorusudur ve ayrı bir adımdır. Yetki kuralları çoğu zaman **seçimlik** yetki verir — o zaman seçim **müvekkil menfaatine** göre yapılır, alışkanlığa göre değil.

**Norm haritası (Mevzuat MCP teyit 2026-09-06 — kullanım anında yeniden teyit):**
- **HMK m.6 genel yetki:** davalının dava tarihindeki yerleşim yeri mahkemesi (her davada açık).
- **m.7:** davalı birden fazlaysa **birinin** yerleşim yeri (m.7/2: sırf forum getirmek için davalı eklenmişse itiraz üzerine ayırma/yetkisizlik — tuzak).
- **m.9-16 özel yetki:** m.9 Türkiye'de yerleşim yeri yoksa mutad mesken / malvarlığı yeri; **m.10 sözleşme → ifa yeri de**; **m.11 miras → son yerleşim yeri KESİN**; **m.12 taşınmazın aynı → taşınmaz yeri KESİN**; m.13 karşı dava; **m.14/1 şube → şube yeri de**, m.14/2 ortaklık/üyelik → merkez KESİN; **m.15/1 zarar sigortası → mal/riziko yeri de**, m.15/2 can sigortası → yerleşim yeri KESİN; **m.16 haksız fiil → fiil yeri / zarar yeri / zarar görenin yerleşim yeri de**. Ayrıca özel kanunlardaki yetki hükümleri ve yetki sözleşmesi (m.17-18 — çıpa) taranır.
- **Kural:** "**de** açılabilir" yazan madde **seçimlik** yetkidir (m.6 + özel yetki birlikte açık) → forum seçimi vardır. "**kesin yetkilidir**" yazan madde (m.11, m.12, m.14/2, m.15/2 — örneklem) → **seçim yoktur**, tek forum; yanlış forum dava şartı eksikliğidir (HMK m.114/1-ç — çıpa) ve mahkemece re'sen gözetilir.

**Müvekkile uygun forum ölçütleri (NİTEL — sayı/olasılık yüzdesi uydurulmaz):** dört ana ölçüt — mesafe, iş yükü, bilirkişi havuzu, BAM/daire eğilimi — artı iki taktik ölçüt:
- **Mesafe / erişim:** müvekkilin, tanıkların ve vekilin duruşmaya/keşfe erişimi; SEGBİS imkânı; masraf.
- **İş yükü / hız:** mahkemenin ve bağlı BAM'ın bilinen tempo/dosya yoğunluğu (nitel gözlem, kütükten; sayı yok).
- **Bilirkişi havuzu:** uyuşmazlığın teknik alanında o yargı çevresinde bilirkişi/uzman bulunup bulunmadığı (ör. denizcilik, inşaat, tıp, yazılım).
- **BAM/daire eğilimi:** o yer BAM'ının ilgili dairesinin konu hakkındaki bilinen içtihat eğilimi — `oa-ictihat` ile **teyitli** kararlardan; hafızadan "şu BAM lehe" denmez.
- **Karşı tarafın avantajı:** karşı tarafın "ev sahası" (yerleşim yeri forumu) mu; m.7/2 itiraz riski var mı.
- **Usul kaldıracı:** tahkim/yetki sözleşmesi, zorunlu arabuluculuk merkezi, ihtiyati tedbir/haciz uygulanacak yer (m.390 ve İİK — çıpa) hangi forumda kolay.

**Soru listesi (avukata / müvekkile — her dosyada sorulur):**
1. Uyuşmazlıkta hangi yetki kuralları açık: yalnız m.6 mı, seçimlik özel yetki var mı, **kesin yetki** var mı?
2. Seçimlik ise aday forumlar hangileri (yerleşim yeri / ifa yeri / fiil-zarar yeri / şube / riziko yeri)?
3. Müvekkil, tanıklar ve deliller fiziken nerede; keşif gerekir mi?
4. Teknik bilirkişi gerektiren bir alan mı; hangi forumda havuz var?
5. Aday BAM dairelerinin konu hakkındaki eğilimi teyitli olarak nedir (`oa-ictihat`)?
6. Yetki sözleşmesi / tahkim şartı / özel kanun yetki hükmü var mı?
7. Karşı tarafın yetki itirazı (ilk itiraz — cevap dilekçesiyle, HMK m.116-117) ihtimali ve maliyeti nedir?

**Çıktı:** konumlama çıktısına (`_oa/cikti/` konumlama kaydı ve DEVİR PAKETİ) tek satırlık **«forum»** satırı eklenir: `forum: <seçilen mahkeme> — dayanak: <yetki maddesi, MCP teyit> — alternatifler: <...> — gerekçe: <nitel ölçüt(ler)>`; kesin yetki varsa `forum: <tek forum> — kesin yetki (<madde>) — seçim yok`. Seçim **karar materyalidir**; nihai forum kararı avukatındır. Yetki itirazı süresi ve dava şartı boyutu `oa-usul`/`oa-sure`'ye devredilir.

## Kompozisyon
Alan tespit edilir → forum seçilir → sorgu `oa-ictihat`, yazım `oa-dilekce`, süre `oa-sure`, usul/yetki denetimi `oa-usul`.

## UNSUR ŞABLONLARI — dava türü konumlandıktan sonra devreye giren kısayol (M4, Paket D — v0.5.5)
Dava türü konumlandıktan **hemen sonra** `references/unsur-sablonlari/` altındaki
asgari sette (`tasarrufun-iptali.md`, `ise-iade.md`, `itirazin-iptali.md`,
`kidem-ihbar.md` — **unsur | norm | delil-türü | yük** dört sütunlu) örtüşen bir
şablon var mı bak. Varsa **işaret et** ve unsur listesini `oa-vakia`'ya devret:
her **unsur** orada `vakia_matris.py`nin `iddialar[]` dizisine bir `id`
(`U1`, `U2`, …) olarak taşınır (unsur metni = iddia metni), delilsiz kalan unsur
`ispat_bosluklari`na düşüp `_oa/DURUM.md`de 🔴 kırmızı görünür. Şablondaki **norm**
çıpaları başlangıç noktasıdır — kesin hüküm gibi sunulmaz; kullanım anında güncel
metin/yürürlük Mevzuat MCP ile (bu parçanın kendi "Yasak bölgeler" ilkesi uyarınca)
**teyit edilir**.

## Aktif çıkarım refleksi
Alanı edilgen haritalamakla yetinme. Olgular ışığında **müvekkil için en verimli hukuki dayanağı kendiliğinden öne çıkar**: hangi karine (ör. İİK m.97/a mülkiyet karinesi), hangi ispat yükü kayması, hangi usul kaldıracı lehe işliyor? İstenmeyen ama dosyanın açtığı bir açıyı (ek talep, alternatif sebep) gör ve öner — sonra `oa-ictihat` ile doğrulat.

## Öğrenme günlüğü
Yeni bir çıpa, daire kayması veya yasak bölge öğrenildiğinde ekle, aşağıya işle, yeniden paketle.
## Anayasal düstur — usul esasa üstündür
Usulün esasa takaddümü ailenin anayasal düsturudur: usulden düşen dosya esasa hiç giremez; süre, usul hukukunun parçası ve telafisiz tek hatadır. Alan tespitinin **ilk çıktısı görev/yetki katmanıdır** (dava şartı): yanlış mercide açılan dosya esasa giremeden düşer. İhtisas dairesi tespiti bu katmanın devamıdır.

## Anayasal bloklar — tek kaynak (anayasa.md)
Bu parça, ailenin ortak anayasal ilkelerine tabidir — **Çaba/token standardı** (model/efor kullanıcının tercihi; muhakemede/doğrulamada/çıktı kalitesinde tasarruf YOK, yalnız mekanik katmanda kayıpsız verimlilik), **Örnekleme ilkesi** (konu sınırlaması yok — kapsam TÜM Türk hukuku), **Doğaçlama meşruiyeti** (yöntem serbest, olgu MCP-teyitli), ayrıca Doğrulama mimarisi, Anonimleştirme ve Layer 0 gizlilik. **Tek ve yetkili kaynak: `ortak-avukat/references/anayasa.md`.** (Bu parça alt-ajan olarak koşarken bu ilkeler `oa-pipeline/scripts/oa_hafiza.py ajan-brif` ile taşınır.)

## Başbakan denetimi (anayasal)
Bu parça, ailenin Başbakanı `oa-pipeline`'ın icra+denetimine tabidir: çağrıldığında disiplini İSTİSNASIZ ve tam işletilir (ama/fakat/token-tasarrufu gerekçesiyle kestirme YASAK). Görev savsaklanmaz; gerçekten yapılamayan bir şey varsa dürüstçe belirtilir ("yaptım" denmez) ve alternatif yöntem üretilir. Önemli olan proses ve çıktı kalitesidir.

## Fiziksel aktivasyon — simülasyon yasağı (anayasal)
Bu parça yalnızca ÜÇ kanıttan en az biriyle "çalıştı" sayılır: (1) Skill aracıyla FİİLEN çağrıldı ve bu gövde bağlama yüklendi (kullanıcının `/oa-alan` komutuyla eşdeğer); (2) scripti gerçekten koştu ve çıktısı görünür; (3) gerektirdiği MCP çağrısı fiilen yapıldı (araç + sorgu + sonuç kaydıyla). Kısa description her zaman bağlamda durur — o VİTRİNDİR, disiplin değildir; gerçek disiplin bu gövdededir. Bu yüzden hiçbir parça bu parçayı description'ından TAKLİT EDEMEZ; bu parça da başka bir parçanın işine ihtiyaç duyduğunda onu Skill aracıyla fiilen çağırır (olmuyorsa SKILL.md'sini Read ile yükler; o da olmuyorsa "FİZİKEN YÜKLENEMEDİ" diye açıkça yazar). Yapılmamış çağrı 'yapılmış', koşmamış script 'koşmuş' gösterilemez — bu, halüsinasyonun ta kendisidir. Devir alırken/verirken kısa DEVİR PAKETİ (ne yapıldı → ne bekleniyor → hangi kanıt) kullanılır ve pipeline defterine (`oa-pipeline/scripts/pipeline_kayit.py`) işlenir. Bu parçanın ürettiği her kalıcı çıktı (JSON/rapor/devir paketi) çalışılan klasörün `_oa/` yerel hafıza kökünde yaşar (yapı: `oa-pipeline` → Çalışma Kökü).

## Değişiklik Günlüğü
Tam günlük `references/degisiklik-gunlugu.md`'dedir (bağlam ekonomisi için ayrıldı — içerik aynen korunur; yeni kayıtlar oraya işlenir). Güncel sürüm: **v3.26**.

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

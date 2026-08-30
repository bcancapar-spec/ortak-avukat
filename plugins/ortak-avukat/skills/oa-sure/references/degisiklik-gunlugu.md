# oa-sure — Değişiklik Günlüğü

(SKILL.md gövdesinden bağlam ekonomisi için taşındı; içerik aynen korunmuştur.)

- **2026-06 (v1):** İlk sürüm. Mevzuat MCP'den teyitli çıpalar: HMK istinaf/temyiz 2 hafta (m.345/361), İYUK istinaf/temyiz 30 gün (m.45/46), AYM 30 gün (6216 m.47/5), İİK istinaf 2 hafta (m.363). **Düzeltilen tuzak:** icra istinafı eski "10 gün" değil, **2 hafta**. İdari yargıda karar düzeltme kaldırıldı (6545). Deterministik script eklendi (adli tatil + tatil günü + hareketli bayram uyarısı).
- **2026-06 (v1.1):** Aktif çıkarım refleksi eklendi (Can yönlendirmesi): zamanlamayı kaldıraç olarak gör — bekleyen eşik değişikliği, erken adım (tedbir/durdurma/eski hâle getirme) fırsatlarını kendiliğinden sun.
- **2026-06 (v1.2):** Script v2 (Can yönlendirmesi): (a) **İYUK çalışmaya ara** mekaniği doğru ve ayrı (1 Eylül + 7 gün, m.8/3 teyitli — HMK'nın 31 Ağu + 1 hafta'sından farklı; test edildi: HMK 07.09 / İYUK 08.09). (b) Resmî tatil tablosu **`tatiller.json`'a taşındı** — yıllık güncellenebilir; dini bayramlar tanımsızsa uyarı. (c) Hesaplanan son günün **takvime + hatırlatıcıya** yazılması iş akışına eklendi.
- **2026-06 (v1.3):** Maddi hukuk süreleri kapsama alındı (Can yönlendirmesi): süre yalnızca HMK/CMK/İYUK değil; TBK/TMK/TTK/6183 vb. zamanaşımı/hak düşürücü süreleri de dahil. Script v3: `--tur usul|maddi` (maddi sürede adli tatil uygulanmaz), `ay`/`yil` birimleri + ay-sonu taşması, zamanaşımı kesilme/durma ve hak düşürücü uyarıları. Başlangıç anının tebliğ olmayabileceği vurgulandı. Test edildi (maddi/usul ayrımı + regresyon temiz).
- **2026-06 (v1.4):** Denetim güncellemesi (Can yönlendirmesi): (1) `tatiller.json`'a **2026 dini bayramları** işlendi (Ramazan 20-22 Mart, Kurban 27-30 Mayıs — çoklu kaynaktan çapraz teyitli; salt-ISO format kuralı ve arife yarım-gün notu eklendi; 2027 boş — Diyanet/RG teyidi beklenmeden doldurulmayacak). Dört senaryoda regresyon temiz (bayram kayması ×2, adli tatil 07.09, maddi süre). (2) Aktif çıkarım örneği güncellendi: 6183 m.48 eşiği **yasalaştı** (7579, RG 22.05.2026 — 1M TL/72 ay); çizelgeye m.48 çıpası + **ertelenmiş yürürlük tuzağı** (Kamulaştırma m.10, yürürlük 21.02.2027) eklendi. (3) Çizelgedeki ölü `mcp-sorgu-kitabi.md` işareti `oa-ictihat`'a yönlendirildi.
- **2026-06 (v1.5):** **İdari izin katmanı** eklendi (Can yönlendirmesi — hukuki kural: *idari izin süreden sayılır*). (1) Tatil rejimi iki kaynaklı tarama oldu: 2429 s.K. (sabit/dini) + **CB genelgesi/kararı idari izinleri** (Mevzuat MCP `search_cbgenelge`/`search_cbbaskankarar`, yıl bazında). (2) Script v4 + `tatiller.json`'a `idari_izin` bölümü: idari izin günü son günü **ASLA kaydırmaz** (2429 anlamında resmî tatil değil — süre uzamaz), yalnızca uyarır (kurumlar fiilen kapalı → işlemi öne al / UYAP 23:59; fiilî imkânsızlıkta HMK m.95 ihtiyat notu). Tabloda kayıt yokken son gün bayrama bitişikse "CB genelgesini tara" uyarısı. (3) 2026 teyitli kayıt: **25 Mayıs** tam gün köprü izni (Kurban öncesi, CB Genel Sekreterliği genelgesi — çoklu kaynak çapraz teyit); yarım günler tabloya girilmez kuralı. Dört senaryoda test temiz: idari izinde son gün sabit + uyarı (25.05), resmî tatil kayması korunur (01.06), tarama dalı, regresyon (07.09 / 23.03).
- **2026-06 (v1.6):** İki güncelleme (Can yönlendirmesi). (1) **Terim ayrımı işlendi:** idari izin taraması tek enstrümana ("genelge") kilitlenmekten çıkarıldı; üç CB enstrümanı hukuki nitelikleriyle ayrıştırıldı — **Cumhurbaşkanlığı Kararnamesi (CBK, AY m.104/17 düzenleyici işlem) / Cumhurbaşkanı Kararı (idari tasarruf) / Cumhurbaşkanlığı Genelgesi (iç düzen işlemi)** — ve tarama üçünü birden kapsar oldu (`search_cbk` + `search_cbbaskankarar` + `search_cbgenelge`); ilan formu yıldan yıla değişebileceğinden etiket farkı ilan kaçırtmaz. (2) **Gelecek yıllar:** script v5 — tabloda tanımsız yıllar (ör. 2032) için **aritmetik hicri hesapla** (1-3 Şevval / 10-13 Zilhicce) tahmini bayram penceresi üretir; son gün pencereye bitişikse "TAHMİNİ DİNİ BAYRAM PENCERESİ" uyarısı verir (kaydırma ASLA yapılmaz — Diyanet/RG teyidi + tabloya işleme + yeniden hesap zorunlu); `--bayram YYYY` modu eklendi. Doğrulama: 2026 tahmini resmî tarihlerle **birebir** (20-22 Mart / 27-30 Mayıs); 2033'teki çift Ramazan Bayramı (Ocak+Aralık) vakası dahil test edildi.
- **2026-06 (v1.7):** İki katman (Can yönlendirmesi). (1) **HMK bilinci:** hesap mekaniği normatif zeminiyle açıklandı ve script çıktısı gerekçeli hâle getirildi — kayma satırları artık dayanağını söylüyor (HMK m.93 + "aradaki tatiller süreye DAHİLDİR" inceliği; 2429 s.K. kaynağı; cumartesi yerleşik-kabul notu + ihtiyat ilkesi; arefe yarım gün). (2) **Çift yönlü süre denetimi:** dava/ihtilaf incelenirken **karşı tarafın** süreli işlemleri de denetlenir; script v6'ya `--islem` modu eklendi — fiilî işlem tarihi son günle karşılaştırılır, kaçırma varsa **"SÜRE KAÇIRILMIŞTIR: X GÜN SONRA"** tespiti net/kesin dille üretilir ve ÇALIŞMAYA EKLENİR (tereddütlü dil yasak; kesinlik şartı = belgeli tebliğ tarihi, teyitsizse "tebliğ şerhinin teyidi kaydıyla"). **Cephanelik istisnası:** süre itirazı saklanmaz, derhâl ileri sürülür. Test: 5 gün geç istinaf tespiti, son günde işlem (m.93 kayması işlem lehine), 1 gün geçme, tüm regresyonlar temiz.
- **2026-06:** Anayasal düstur işlendi (Can yönlendirmesi): **usul esasa üstündür** — süre usul hukukunun parçasıdır; düstur bu parçanın işlevine operatif kuralla bağlandı (yukarıdaki bölüm). Müvekkil menfaati çift yönlü: kendi usul zaafını sıfırla, karşı tarafın usul hatasını (özellikle kaçırılmış süreyi) tespit et ve derhâl kullan.
- **2026-06:** Örnekleme ilkesi bağlandı (anayasal — Can yönlendirmesi): konu sayımları örneklemdir, kapsam tüm Türk hukukudur; işlemeyen örneklem güncellenir, metod sabittir.
- **2026-06:** Çaba/kalite standardı bağlandı (anayasal — Can yönlendirmesi): tasarruf hedef değil; derinlik karmaşıklığa göre yükselir; Opus+High taban.
- **2026-06:** Doğaçlama meşruiyeti bağlandı (anayasal — Can yönlendirmesi): yöntemde serbest doğaçlama (Çapar lafzı), olguda sıfır halüsinasyon/teyit.
- **2026-06:** Başbakan denetimine tabi olma bağlandı (anayasal — Can yönlendirmesi): istisnasız tam işletim, tembellik/kaçış yasağı, dürüst 'yapılamadı' + yeni yöntem.

- **2026-07 (v3.16):** Fiziksel aktivasyon — simülasyon yasağı bloğu eklendi (Can yönlendirmesi — komutla tetiklenen parçalar description'dan taklit edilmesin, fiilen çağrılsın): çalıştı = fiilî Skill çağrısı / gerçek script / gerçek MCP çağrısı + DEVİR PAKETİ + pipeline defteri kaydı. Değişiklik günlüğü bağlam ekonomisi için `references/degisiklik-gunlugu.md`'ye taşındı (içerik korunmuştur).
- **2026-07 (v3.17):** Yerel hafıza kuralı bağlandı (Can yönlendirmesi — hafıza ve devir çalışılan klasörde fiziksel yaşar): parçanın kalıcı çıktıları `_oa/` kökünde (defter/devir/teyit/cikti); fiziksel aktivasyon bloğuna işlendi.
- **2026-07 (v3.18):** Süre flag'leri yerel hafızaya bağlandı (rapor 5.4): hesaplanan son gün `oa_hafiza.py sure-flag` ile `_oa/sureler.json`'a işlenir (oturum açılışında taranır); hatırlatıcı aracı yoksa 'elle kur' açıkça söylenir — disk pasiftir, dürtmez.
- **2026-07 (v3.19):** E-TEBLİGAT BAŞLANGIÇ PROTOKOLÜ eklendi (ilk saha dosyası dersi): 7201 m.7/a ulaşma↔tebliğ-sayılma ayrımı; belirsizlikte iki-senaryolu hesap, erken son gün esas (güvenli yön), geç senaryo notta; tarih türü kullanıcıya/UETS kaydına sorulur.
- **2026-07:** Çaba/token düsturu GÜNCELLENDİ (Can yönlendirmesi): tasarruf artık HEDEF — ama yalnız mekanik/temsil katmanında ve VERİ-KAYIPSIZ; muhakemede tasarruf edilmez, derinlik/doğrulama/araştırma asla kısılmaz. Aile geneli anayasal güncelleme; deterministik motor: `oa-ingest`.
- **2026-07 (v3.22 — M2-3):** Sürüm işaretçisi ailenin ortak M2-3 entegrasyon sürümüne hizalandı (`aile_dogrula.py` sürüm tutarlılık uyarısını temizlemek için); bu satırın kendisi dışında bu parçada işlevsel bir değişiklik YOKTUR — gerçek içerik değişiklikleri (varsa) yukarıdaki ayrı kayıtlardadır.
- **2026-07 (v3.26 — M3-4 hizalama):** Sürüm işaretçisi ailenin M3 faz-sonu ortak hizalama sürümüne (v3.26) taşındı (`aile_dogrula.py` sürüm tutarlılık uyarısını kapatmak için); bu satırın kendisi dışında bu parçada işlevsel bir değişiklik YOKTUR — gerçek içerik değişiklikleri (varsa) yukarıdaki ayrı kayıtlardadır.
- **2026-07-28 (v0.5.5 — M5, Paket D):** `hesapla_sure.py`'ye yeni `--pencereler <json>` bayrağı — dosyada AYNI ANDA işleyen birden fazla süreyi (`hesapla()` ile aynı deterministik mantık) çözüp `[teblig+1, son_gün]` pencerelerinin PAIRWISE çakışıp çakışmadığını raporlar; `oa-illiyet`'in zaman katmanına girdi sağlar. Önceliklendirme avukat muhakemesidir, script yalnız çakışmayı gösterir.

## v0.5.13 — heyet infazı: başlangıç türü + MCP düzeltmeleri + kurtarma işaretçisi
- `--baslangic-turu` (teblig|tefhim|ogrenme|olay|belirsiz) — OPSİYONEL, imzanın
  SONUNDA, aritmetiği DEĞİŞTİRMEZ; "belirsiz"de iki-senaryo + ERKEN tarih uyarısı;
  tanınmayan değer sessizce yutulmaz. Gerekçe (MCP teyitli 2026-08-27): CMK m.268
  itiraz ÖĞRENME gününden, m.273/291 istinaf-temyiz GEREKÇELİ KARARIN TEBLİĞİNDEN.
- **Kural tablosu düzeltmesi (JSON + gömülü fallback birlikte):** cmk_itiraz
  7 gün → **iki hafta**; cmk_istinaf/temyiz kaynak metinleri 7499 sonrası
  gerçeğe göre yenilendi (hazır-bulunmayan fıkraları MÜLGA).
- Çizelge: İİK m.67 (1 yıl) / m.68-68a (6 ay) / m.72 (takip evresine göre teminat)
  çıpaları; İYUK m.10 (30 gün + 4 ay bekleme + 60 gün geç-cevap) ve m.11
  (durma + kalan süre) mekaniği; İYUK'ta eski hâle getirme YOK notu;
  VUK m.107/A (7587 s.K. ile değişik, beşinci gün kuralı).
- `sure_nobetci.py`: geçmiş süre çıktısına tek satırlık işaretçi — "GEÇMİŞ
  hukuken kesin değildir, kapı araştırmasını koştur". Katalog burada DEĞİL
  (ikiz-liste yasağı); `GEÇMİŞ` alt dizesi ve exit-3 sözleşmesi korundu.

## v0.5.8.5 — 2026-08-16

- **E4a — SÜRE BAĞI (hesap → defter otomatik):** `hesapla_sure.py` artık hesapladığı son günü `<kok>/_oa` varsa `_oa/sureler.json`'a OTOMATİK flag olarak işler (yeni `--kok` bayrağı; kayıt biçimi `oa_hafiza.py sure-flag` şemasıyla birebir — `sure_nobetci.py` aynı defteri okur; İN-PROCESS yazım, subprocess yok). Saha boşluğu buydu: hesap yapılıyor ama deftere elle işleme adımı atlanıyordu — nöbetçi hiç görmüyordu. `--uets` karine senaryosu AYRI kayıt olur (iki son gün de görünür — kayıpsızlık); aynı (son gün + açıklama) çifti tekrar eklenmez (tekrar koşu defteri şişirmez); `--aciklama` ile açıklama verilebilir, `--flagsiz` yalnız-hesap kipine döndürür. Yazım BLOKLAMAZ: defter hatası hesabı düşürmez, açıkça raporlanır; `_oa` yoksa defter İCAT EDİLMEZ (dava kökü değildir — görünür bilgi satırı). event_create/reminder_create yine ÇAĞRILMAZ; dış takvim eşgüdümü avukatta.

## v0.5.14 — DENETİM İNFAZI: ceza adli tatili + İYUK kör noktaları + girdi sağlamlaştırma

Kaynak: `DENETIM-CELISKI-KIRIK.md` (5 hukukçu + 4 mühendis avcı; her bulgu bağımsız
skeptikçe yeniden koşturuldu). Aşağıdaki her hukuki iddia bu turda **Mevzuat MCP'den
yeniden teyit edilmiştir (2026-08-31)**: CMK m.39, m.40, m.268, m.273, m.291, m.331 ·
İYUK m.8, m.20/A, m.20/B, m.27, m.45, m.48, m.61, m.62 · HMK m.103 · 6183 m.58 ·
VUK m.107/A · 7201 m.7/a · Danıştay 7.D. E.2000/5685 K.2002/3522 (tam metin).

### P0

- **[A-1] CEZA ADLİ TATİLİ — `--yargi ceza` + CMK m.331/4 (ÜÇ GÜN).** Motor, ceza kanun
  yolu sürelerine hukuk yargısının rejimini (HMK m.104, bir hafta) uyguluyor ve son günü
  **dört gün geç** veriyordu (`--teblig 2026-07-14 --kural cmk_istinaf` → 2026-09-07;
  doğrusu **2026-09-03**). `--yargi`ye `ceza` değeri, `hesapla()`ya m.331/4 dalı eklendi;
  tatil günü kayması gerekçesi de kola göre yazılıyor (hukuk HMK m.93 · idari İYUK m.8/2 ·
  ceza CMK m.39/4). m.331/2-3 (tatilde de yürütülen işler; tutuklu hükümler) ve m.263
  (süreyi kesen kanal) uyarı metnine ve çizelgeye işlendi.
  **KARAR — DURDURMA, uyarı değil:** `cmk_*` kuralı ceza kolu dışında (ya da ceza kolu
  ceza-dışı kuralla) seçilirse hesap **durur** (`p.error`, exit 2) ve son gün hiç basılmaz.
  Gerekçe: uyarı basıp devam etmek, ">>> HESAPLANAN SON GÜN" başlığını ve `--kok` verildiğinde
  `_oa/sureler.json`'a **otomatik yazılan flag'i** yerinde bırakırdı; `sure_nobetci.py` o
  kaydı otorite sayar ve B-17 uyarınca defterde düzeltme/silme yolu yoktur. Bedeli tek
  bayraktır ve hata mesajı bayrağı adıyla söyler. İYUK↔HMK uyuşmazlığı ise **bloklanmaz**
  (uzatma aritmetiği aynı sonucu verir) — mevcut bilgi notu korundu. Aynı kapı `--pencereler`
  yolunda da var: uyuşmazlık taşıyan kayıt mevcut "atlandı" disipliniyle düşer ve izi
  `atlanan` listesine yazılır.

### P1-P2 — hukuki

- **[A-3] Yürütmenin durdurulması (İYUK m.27) ailede hiç yoktu.** `iyuk_yd_itiraz` kuralı
  (7 gün, m.27/7, bir defaya mahsus) eklendi; çizelgeye m.27'nin tam bloğu işlendi:
  f.1 (dava açmak yürütmeyi durdurmaz), f.2 (iki şart birlikte + kamu görevlisi atama
  istisnası), f.3 (savunmasız ret), **f.4 (ödeme emri = TAHSİLAT işlemi → açılan dava
  tahsili durdurmaz; ihtirazi kayıtlı beyanname)**, f.6 (teminat), f.7 (7 gün itiraz +
  merciler + kesinlik), f.9, f.10 (aynı sebeple ikinci istem yok). **Şerh işlendi:**
  m.20/A-2/e ve m.20/B-1/d uyarınca ivedi ve merkezî sınav davalarında YD kararına
  **itiraz edilemez**.
- **[A-5] İYUK m.20/A ve m.20/B ailede hiç yoktu; script bu davalara sessizce 60 gün
  veriyordu.** Dört kural eklendi: `iyuk_dava_ivedi` (30 gün, m.20/A-2/a),
  `iyuk_temyiz_ivedi` (15 gün, /g), `iyuk_dava_sinav` (10 gün, m.20/B-1/a),
  `iyuk_temyiz_sinav` (5 gün, /f). Çizelgeye kataloglar + **m.45/8 "ivedide istinaf
  YOK"** + "m.11 uygulanmaz" işlendi. Avukatı yanlış yöne bakmaya sevk eden "özel kanun
  süreleri olabilir" uyarısı, bu sürelerin **İYUK'un kendisinde** olduğunu söyleyecek
  şekilde yeniden yazıldı.
- **[A-17] İYUK m.48 çizelgesi eksikti.** `iyuk_temyiz_cevap` (30 gün, m.48/3) ve
  `iyuk_temyiz_ozel_7gun` (7 gün — m.48/6 son cümle + m.45/2 ek cümle) eklendi; çizelgeye
  dört ayrı süreyi ayıran blok yazıldı (15 gün eksiklik · 30 gün cevap · 7 gün harç ·
  7 gün temyiz). m.48/3'ün taarruz yüzü (cevap verenin, kararı süresinde temyiz etmemiş
  olsa bile dilekçesinde temyiz isteminde bulunabilmesi) ayrıca not edildi.
- **[A-4] UETS "güvenli taraf" çelişkisi ve vergide yanlış dayanak.** Script "güvenli taraf
  KARİNE (Senaryo-2)" derken SKILL.md "ERKEN son gün esas alınır" diyordu; devamındaki cümle
  dilbilgisel olarak bozuktu. **Tek tanım, amaca göre ayrıldı:** bizim süremizde güvenli taraf
  ERKEN son gün; karşı tarafa kesin dil yalnız her iki senaryo da aşılmışsa. Dayanak artık
  kurala göre seçiliyor: vergi kanadında (`iyuk_dava_vergi`, `amme_6183_m58`) **VUK m.107/A**
  (Değişik: 24/6/2026-7587), diğerlerinde **7201 m.7/a** — aritmetik aynı olduğu için bu hata
  sessiz kalıyordu ama dilekçeye yanlış norm giriyordu.
- **[A-6] AYM'nin iptal ettiği 6183 m.58/5 yürürlükteymiş gibi hatırlatılıyordu.**
  "ayrıca m.58/5 haksız itiraz zammı yönü hatırlanır" ibaresi kaldırıldı; yerine iptal şerhi
  (**AYM 21/4/2022, E.2021/119, K.2022/48**; ikame hüküm konmamıştır) ve "müvekkil bu
  yaptırımla hak arama yolundan caydırılamaz" uyarısı yazıldı.
- **[A-7] Adli tatil istisnası gerekçesi yargı koluna göre dallandırıldı.** İdari yargı
  istinafında **HMK m.103** kataloğu basılıyordu; idari karşılık **İYUK m.62**'dir ve içeriği
  tamamen farklıdır (yalnız YD + delil tespiti + kanunen belli sürede karara bağlanacak
  işler). Üç dal yazıldı (hukuk m.103 bent bent · idari m.62 · ceza m.331/2-3 + "lafzında
  istisna yoktur" uyarısı). m.103/1-ç lafzı genişletilmişti: istisna **davacı sıfatına**
  bağlıdır (*"işçilerin AÇTIKLARI davalar"* — işverenin açtığı dava girmez); m.103/1-b'nin
  soybağı/velayet/vesayeti de saydığı eklendi. İYUK m.61/1 c.2 (tek mahkemeli yerler ara
  vermeden yararlanamaz) **ölçülmemiş açık uç** olarak kayda geçti.
- **[A-9] `_dikkat_cmk` notu yürürlükten kalkmış hukuku anlatıyor ve kendi teyitli
  kayıtlarını çürütüyordu** ("m.273 için 7 gün, m.291 için 15 gün diyebilir… teyit boş").
  Not MCP teyidiyle yeniden yazıldı: üçü de iki hafta, f.2'ler 7499 s.K. ile mülga, m.263
  saklı, adli tatil m.331/4. `cmk_*` teyit tarihleri 2026-08-31'e tazelendi.
- **[A-10] İdari yargıda var olmayan kurtarma kapısı (HMK m.95) öneriliyordu.** 2577 içinde
  "eski hale getirme"/"mazeret" **hiç geçmiyor** (MCP içinde-ara → 0 eşleşme). Uyarı üç kola
  ayrıldı: hukuk → HMK m.95/96; **idari → İYUK'ta bu kurum YOKTUR**, bakılacak yerler AY
  m.40/2, İYUK m.10 ve vergide düzeltme-şikâyet (yalnız vergi hatası varsa); **ceza → CMK
  m.40** (kusursuzluk; kanun yoluna başvuru hakkı bildirilmemişse kişi kusursuz sayılır) + m.263.
- **[A-20] 6183 m.58 süresinin çalışmaya ara ile uzaması TARTIŞMALI.** Danıştay 7.D.
  **E.2000/5685 K.2002/3522** (13.11.2002) tam metni çekildi: çoğunluk uzamadan yana (script
  doğru tarafta) ancak karar **oyçokluğu**; tetkik hâkimi, Danıştay savcısı ve ayrışık oy
  aksi yönde. Özel kanun sürelerine İYUK m.8/3 uzatması uygulandığında çıktıya "TARTIŞMALI
  UZATMA" şerhi düşüyor ve **güvenli plan olarak HAM BİTİŞ** gösteriliyor; çizelgeye de işlendi.

### Mühendislik

- **[B-16] Negatif/sıfır süre sessizce kabul ediliyordu.** `--sure -5` tebliğden ÖNCEKİ bir
  tarihi ">>> HESAPLANAN SON GÜN" diye basıp exit 0 dönüyordu. `miktar_dogrula()` eklendi
  (negatif · sıfır · tip · birim başına üst sınır) ve `hesapla()` girişinde çalışıyor;
  ayrıca dönüş öncesi `son < teblig` iç tutarsızlık kilidi kondu. `--sure 0` artık "alan
  eksik" **yalanını söylemiyor** (`a.sure is not None` düzeltmesi) — sıfır süre olarak reddediliyor.
- **[B-22] Bozuk/uç tarih ve miktarda ham traceback.** `--teblig` ve `--islem` için
  `p.error()` ile temiz mesaj (beklenen biçim + gg.aa.yyyy uyarısı); `hesapla()` çağrısı
  `ValueError`/`OverflowError` yakalanarak temiz mesaja çevriliyor; exit kodu argparse
  sözleşmesine uygun (2).
- **[B-21] İKİZ KURAL TABLOSU — ayrışma mekanik olarak kilitlendi.** `_GOMULU_KURALLAR` ile
  `sure_kurallari.json` artık tek kaynaktan üretiliyor ve **anahtar + miktar + birim + kaynak
  metni + teyit tarihi** beşi birden birebir aynı; `tests/test_v0514_sure.py` üç ayrı testle
  gelecekteki ayrışmayı yakalıyor. Teyit tarihi **metinden alana taşındı** (`_GOMULU_TEYIT`) —
  fallback yolu "teyit BOŞ" derken kaynak metninin "(MCP teyit 2026-08-27)" demesi, aynı
  ekranda iki zıt beyan üretiyordu. **Sessiz fallback kaldırıldı:** JSON yok/bozuk/boşsa
  düşme sebebi raporun ilk satırında görünür şekilde basılıyor.
- **[B-20] `--baslangic-turu` seçilen kuralla çelişse de sessizce kabul ediliyordu.** Kural
  tablosuna `izinli_baslangic_turleri` alanı eklendi (JSON + gömülü); uyuşmazlıkta görünür
  uyarı basılıyor. Script **nitelendirme yapmaz** — yalnız alanın kapalı kümede olup olmadığına
  bakar, hukuki hüküm avukata aittir. Alanı olmayan eski kayıtlarda kapı sessizdir (çökmez).
- **[B-19] `--adli-tatil-istisna`, `--uets`, `--baslangic-turu` hiçbir `.md`'de geçmiyordu.**
  Üçü de SKILL.md iş akışına örnek komutla girdi (§4b-4c-4d) ve çizelgeye "Motor bayrakları"
  tablosu eklendi; **HMK m.103 kapsamı artık talimat katmanında bent bent yazılı** (en tehlikeli
  boşluk buydu: kapsam bilinmediği için m.103 işlerinde varsayılan hesap bir hafta uzun çıkıyordu).

### Bilinçli kırılan mevcut test

- `tests/test_sure.py::test_kural_tablosu_json_okunuyor` — `cmk_itiraz` kuralını varsayılan
  `--yargi hukuk` ile koşuyordu; A-1 kapısı gereği bu artık exit 2'dir. Test `--yargi ceza`
  ile güncellendi ve gerekçesi docstring'ine yazıldı. Davranış değişikliği **kasıtlıdır**.

### Devir (başka pakete ait — bu turda UYGULANMADI)

- `PLAN-SEMA-PAKETI.md` §3 (T10) test #8, `"iyuk_yd_itiraz" not in ...` bekliyordu; bu turda
  A-3 talimatı gereği kural **eklendi**. `tests/test_tez10_amme_odeme_emri.py` yazan paket bu
  şartı kaldırmalıdır — "iki dosyada senkron gerekir" gerekçesi B-21 kilidiyle karşılanmıştır.

---
name: oa-kontrol
description: >-
  Ortak Avukat sisteminin DENETİM/KONTROL parçası. Bir dilekçe, dosya veya mütalaa
  teslim edilmeden önce; atıf/künye doğruluğu denetlenirken; müvekkil-aleyhi zaaflar
  taranırken DEVREYE GİR. Üç sabit kontrol listesini uygula: (1) atıf denetimi
  (her künye resmî kaynaktan teyitli mi), (2) teslim öncesi usul+esas kontrolü,
  (3) müvekkil-aleyhi zaaf protokolü. "Bunu kontrol et", "teslime hazır mı", "gözden
  geçir", "zayıf yanları neler" türü her işte — kullanıcı açıkça istemese bile esaslı
  bir çıktı teslim edilmeden önce — tetikle. Bağımsız çalışır; tüm oa- parçalarının
  çıktısını teslimden önce süzer. (İleride deterministik `oa-antitez` motoru bu
  listelerin üstüne kurulacaktır.)
---

# oa-kontrol — Teslim Öncesi Denetim ve Zaaf Protokolü

Sök-tak parça. Doğrulama mimarisinin **son kapısı**. Her kalem "evet/hayır"; "hayır" çıkan ya giderilir ya müvekkile **açık uç** olarak raporlanır — gömülmez.

## MEKANİK KAPILAR (checklist'i denetleyen scriptler — teslim engeli)
Aşağıdaki listeler artık iki deterministik script'le mekanik olarak desteklenir (model disiplini + script kapısı BİRLİKTE):
- `python scripts/kunye_teyit.py <taslak.md>` → **A listesinin atıf-izi kapısı:** taslaktaki her içtihat/mevzuat künyesini teyit edici kaynak evreniyle çaprazlar. **Kaynak evreni SADECE ikisidir:** `_oa/teyit/kunye-teyit.md` kütüğü + `_oa/teyit/dokum/` ham MCP dökümleri (bu ikinci dizin `oa-ictihat`'ın her MCP sonucunu diske yazma adımıyla beslenir). **`_oa/cikti/` teyit kaynağı DEĞİLDİR** — orası taslak/antitez/kıyas gibi MODELİN çalışma evrakıdır; oradaki bir iz en fazla "[BİLGİ] iz var ama TEYİT SAYILMAZ (model çıktısı)" şerhi alır, statüyü asla TEYİTLİ yapmaz. Teyitsiz atıf → **exit 1**. (Script künyenin KÜTÜK/DÖKÜM izini garantiler; hükmün iddiayı gerçekten karşıladığı A-2/A-5 muhakemesi yine aşağıdaki listenin işidir — mekanik iz ≠ içerik doğruluğu.)
- `python ../oa-dilekce/scripts/dilekce_denetim.py <taslak.md> --tip <tip> --taraf <taraf>` → **B (zorunlu unsur + tertip-düzen) + iç/dış (müvekkil-aleyhi ifade taraması) + OCR-teyit şerhi** kapısı; eksik/sinyal → **exit 1**.
- `python scripts/ictihat_muhakeme_denetim.py <taslak.md> --kok . [--tip <tip>]` → **İçtihat Muhakeme Zinciri mekanik kapısı** (MODÜL 2): dilekçedeki HER içtihat künyesi için `_oa/cikti/*ictihat-muhakeme*.md` kaydı var mı + künye eşleşiyor mu (`kunye_ortak.kunye_normalize` — esas/karar VE, biliniyorsa, **DAİRE**; esas/karar no'ları her dairede yılda sıfırdan başladığından tek başına esas/karar eşleşmesi YETERSİZDİR, daire de eşleşmelidir; dilekçe atfı daire belirtmiyorsa VE aynı esas/karar no'suna sahip birden fazla FARKLI daireye ait kayıt varsa **fail-closed exit 1** — "hangi kaydın geçerli olduğu belirlenemiyor") + KAYNAK-İZİ `_oa/teyit/dokum` içinde gerçekten var ve künye orada dize olarak geçiyor mu + İLGİLİ-KISIM/DAVAYA-BAĞ/DAMGA dolu mu (yoksa **çıplak atıf → exit 1**); ayrıca DAMGA=ALEYHE → **exit 1** (anayasa m.6 teslim engeli), DAMGA=ALEYHE-AYIRT ile AYIRT-ETME boşsa **exit 1** (fail-closed), DAMGA yok/geçersiz → **exit 1** ("muhakeme edilmemiş"), DAMGA=NOTR yalnız **uyarı** verir (bloklamaz). Script içeriğin isabetini MUHAKEME ETMEZ — yalnız varlık+bağ+alan bütünlüğünü denetler; doğrulanmış içtihat atfı hiç yoksa "emsal içtihat yok — muhakeme zayıf" **uyarısı** basar (bloklamaz). **`--tip` (M3-2/R6):** bu G1 uyarısı yalnız "esaslı" dilekçe tiplerinde (dava/cevap/istinaf/temyiz/aym_bireysel) basılır; `yemin`/`idari-kanal` gibi hafif tiplerde [BİLGİ]'ye düşer (G2/G3 engelleri tip'ten ETKİLENMEZ — `--tip` yalnız G1 gürültüsünü azaltır, tek kaynak liste `ESASLI_OLMAYAN_TIPLER`). **YENİ-2 (backlog):** aynı esas/karar/daireye ait birden çok kayıt varsa VE DAMGA değerleri birbirinden farklıysa (ör. biri LEHE biri ALEYHE), "ÇELİŞEN DAMGA" **uyarısı** basılır (bloklamaz) — script temiz adayı bulup kullanabilir ama tutarsızlığı sessizce gizlemez.
Teslim, bu üç script + `oa-antitez` çökertme matrisi + aşağıdaki A/B/C/D listeleri birlikte geçilince 'hazır' sayılır. **Tek ölçüt (R2 — sayım değil, tek script):** kapıları teker teker sayıp "kaçı yeşil" diye elle toplamak YASAKTIR — bu hem hataya açıktır (bir kapı unutulabilir) hem de sıralamayı (ilk engelde durma) görünmez kılar. Tek ve yetkili ölçüt aşağıdaki **`teslim_paketi.py` orkestra script'inin exit kodudur**: exit 0 = teslime hazır, exit ≠0 = değil. Alt kapılar (dilekce_denetim/kunye_teyit/ictihat_muhakeme_denetim/defter `--denetle`) bu tek script'in İÇİNDE sabit sırada zaten koşar; onları ayrı ayrı çalıştırıp sayıya dökmek gereksizdir ve yanlış-güven üretebilir.

**TEK KOMUT TESLİM ZİNCİRİ (orkestra script — fiilen ÇAĞRILIR, atlanmaz):** Yukarıdaki kapılar + Layer 0 + defter denetimini tek seferde, sabit sırada ve ilk engelde durarak koşan bir orkestra script'i vardır — teslim öncesi bu **tek komut** çalıştırılır:
```bash
python scripts/teslim_paketi.py <taslak.md> --tip <tip> --taraf <taraf> [--dis-arac] [--udf-yok] --kok .
```
(`--tip`: dava|cevap|istinaf|temyiz|aym_bireysel|genel; `--taraf`: davaci|davali|sanik|katilan|mudahil — boş bırakılabilir; `--dis-arac`: çıktı dış araca gidecekse Privacy Layer 0 kapısını zincire ekler; `--udf-yok`: kurucu kural "varsayılan çıktı UDF"yü BİLİNÇLİ atla (tercih makbuza yazılır); `--kok`: çalışma kökü.) Zincir dilekce_denetim → kunye_teyit → ictihat_muhakeme_denetim → [gizlilik_tara] → defter boşluğu (in-process) → tam_tur `--durum` sırasıyla koşar, ilk kapanan kapıda durur ve tek raporda hangi kapının kapandığını basar; hepsi geçerse UDF üretir ve "TESLİME HAZIR" der (exit 0). Bu script çalıştırılmadan/çıktısı görülmeden "teslime hazır" sözle beyan edilemez (R2: tek ölçüt bu script'in exit kodudur) — fiziksel aktivasyon kuralı burada da geçerlidir.

**TESLİM MAKBUZU + FAIL-CLOSED (P0-5, v0.5.5):** her koşu `_oa/defter/teslim-
makbuz.json` (başarı) ya da `teslim-makbuz-RED.json` (başarısız deneme —
İZLİDİR, kaybolmaz) ATOMİK yazar: {zaman, taslak_yol, taslak_sha256, tip,
taraf, kapilar:[{ad,durum,exit}], exit_kodu, udf_yolu, udf_atlandi_istekle,
ictihat_muhakeme_kanali, surum}. Kapı başına durum ENUM'u {OK,BLOK,ATLA,BILGI}
— "script bulunamadı/çalıştırılamadı" artık FAIL-CLOSED'dır: bir ENGELLEYİCİ
kapı için ATLA, BLOK ile EŞDEĞERDİR (zincir orada durur), yalnız BİLGİ kapıları
(`(e)` tam_tur `--durum`) bu kuraldan muaftır. Alt scriptler önce `__file__`-
göreli konumdan, bulunamazsa `OA_SKILLS_KOK` ortam değişkeni fallback'inden
aranır; hiçbiri yoksa hata TÜM denenen TAM YOLLARI gösterir. `pipeline_kayit.
py`'nin adım-9 önkoşul kapısı VE `--denetle`'nin makbuz bütünlük denetimi
(taslak sha256 eşleşmesi dahil) bu dosyayı okur.

## UDF TESLİM KAPILARI + MAKBUZ GARANTİSİ (v0.5.8.4 — 372 Torbalı devşirmesi)

`teslim_paketi.py` zincirinin UDF ucu 372 saha derslerinin mekanik karşılığıyla genişledi. Kapılar sabit sırada, elle sayılmaz (R2 — tek ölçüt yine exit kodu):

- **MEVCUT-UDF DEVRALMA:** üretimden ÖNCE aday `.udf` aranır (`<taslak>.udf` + `_oa/cikti` altında aynı kök-adlılar). Geçerli aday varsa YENİDEN ÜRETİLMEZ — `udf_devralindi` alanıyla makbuza geçer (çift-UDF tuzağı kapandı); geçersiz aday (elle-üretim imzalı) SİLİNMEZ, `_oa/arsiv-yerel/gecersiz-elle-udf/` karantinasına taşınır.
- **PROV-TAZELİK:** mühürdeki sha güncel dosyayla uyuşmuyorsa (bayat mühür) teslim RED — bayat mühürle teslim YOK.
- **YEREL-DAMGA:** mührün `was_generated_by` alanı yerel-motor gösteriyorsa teslim RED — yerel motor ürünü teslime giremez (372 A/B hükmü: suçlu yerel-motor content.xml).
- **ŞEKİL:** pageFormat 4 kenar 42.52 pt (Yönetmelik 2646 m.8) değilse `udf_yaz`'ın kenar yaması OTOMATİK uygulanır ve mühür sha'sı GÜNCELLENİR; düzeltilemezse RED. `LineSpacing="0.50"` (1,5 satır) yaygınlığı ve 11pt link imzası yalnız İSTİŞARİ satırdır (kapı kapatmaz).
- **OTOMATİK MÜHÜR:** teslime giren UDF mühürsüzse `teslim_paketi` onu KENDİSİ mühürler — mühürsüz teslim fiziksel olarak imkânsız (372: 23 uyarı / 0 uygulama dersi).
- **MAKBUZ GARANTİSİ:** zincir try/finally sarmalayıcıdadır — erken çıkışlar (taslak yok, argparse hatası, beklenmeyen çökme) dahil HER başarısız yol bir RED makbuzu düşürür (zaman + sebep + argv). Makbuzsuz ölüm yolu kalmadı.
- **TAZELİK BİLGİ KAPISI:** `tazelik_denetim.py` advisory koşulur; BAYAT/EKSİK satırları makbuza `tazelik_uyarilari` olarak geçer, kapı kapatmaz.

**ÇIKTI ŞEMASI — 40-UYAP dış-çıktı dizini (v0.5.9, advisory):** YEŞİL makbuz kesilen her koşuda `teslim_paketi.py` dava kökünde muhatap-nötr dış-çıktı dizini **`40-UYAP/`** kurar: nihai ürünün KOPYASI (UDF + varsa aynı kök-adlı PDF/DOCX — taşıma DEĞİL, tek-nüsha ilkesi: asıl `_oa/cikti`de mührünün yanında kalır) + `_damga` alanlı `teslim-makbuz-KOPYA.json`; makbuza `uyap_kopya` + `uyap_urun_kopyalari` alanları girer. **Avukat UYAP'a YÜKLERKEN — ya da karşı vekile/kuruma/müvekkile gönderirken — `40-UYAP/`taki kopyayı kullanır**; `00-TESLIM.md` teslim notuna da `40-UYAP/` yolu satırı yazılır. Kopya hatası teslimi KIRMAZ (görünür uyarı; exit değişmez); makbuz RED/yokken 40-UYAP üretilmez. Tek yetkili doktrin: `references/cikti-semasi.md` (kapıya terfi yolu + v0.5.10'a ertelenen A3/A4 bekçileri dahil).

**`muhur_yaz.py` ekleri:** ürün arşive taşınırken mührü AYIRMA — `python scripts/muhur_yaz.py --kok . --tasi ESKI YENI` mühür-dosya çiftini birlikte taşır (`artifact_file` güncellenir; sha DEĞİŞMİŞSE RET — taşıma içerik değiştirmez). `--llm` boş bırakılırsa kayda otomatik olarak 'mekanik üretim; içerik oturum LLM koşusundan' yazılır (dürüst varsayılan, boş beyan değil).

**`kaynak_blogu.py` (YENİ):** her `_oa/cikti` ürününün ilk satırına konacak `<!-- kaynaklar: yol@sha8 · ... -->` bloğunu `python scripts/kaynak_blogu.py --girdiler <yol...> [--besledigi X] [--uretim Y]` üretir — sha'yı model değil script hesaplar; `tazelik_denetim.py` bu blokla çalışır (@sha8'siz blok tazelik denetimini fiilen işlevsiz bırakır — 372 Torbalı bulgusu).

## A. Atıf denetimi (tavizsiz)
Dilekçeye giren **her** içtihat/mevzuat atfı için:
- [ ] Künye resmî kaynaktan teyitli mi? (esas/karar no, tarih, daire — Yargı/Mevzuat MCP, `oa-ictihat`). Hafıza/Gemini'den künye **iddia**dır.
- [ ] Kararın hükmü iddiayı **gerçekten** karşılıyor mu? Terim "savunma/temyiz sebebi" olarak mı geçiyor, mahkeme **esastan** mı uyguladı?
- [ ] Mevzuat maddesi yürürlükte mi (mülga/değişik değil mi)? Parasal sınır o yıl için mi?
- [ ] İçtihat güncel mi, içtihat değişikliği/tarih bandı kontrol edildi mi? (örüntü: aynı dairenin dönemsel içtihat ayrışması — tarih bandıyla doğrula.)
- [ ] **Yasak bölge** ihlali var mı? (Danıştay 8. Daire hafızadan üretilmez; daire kaymaları — `oa-alan`.)
- [ ] Teyit edilemeyen atıf **açıkça etiketlendi mi**? ("teyit edilmedi"/"MCP'de bulunamadı"/"tek kaynak").
- [ ] **İçtihat muhakeme edildi mi?** Dilekçedeki her içtihat atfının bir `_oa/cikti/NN-ictihat-muhakeme.md` kaydı var mı; DAMGA `LEHE` veya `ALEYHE-AYIRT` mi (`NOTR`/damgasız veya ayırt-etmesiz `ALEYHE-AYIRT` → çıkar, çıplak künye dilekçede kalamaz — `oa-kiyas/references/ictihat-muhakeme-sablonu.md`)?
- [ ] Esaslı sonuç **Yargıtay/BAM atfına** dayanıyor mu? Dayanmıyorsa muhakeme "zayıf" diye işaretlendi mi?

## MUHAKEME adımı (İçtihat Muhakeme Zinciri) — bu parçanın da işi
CEK (`oa-ictihat`) ve KULLAN (`oa-dilekce`) arasındaki MUHAKEME adımını
`oa-kiyas` ile birlikte bu parça da yürütür/denetler: her çekilmiş kararın
KUNYE + KAYNAK-IZI + İLGİLİ-KISIM + DAVAYA-BAĞ (R4 — eski adı "İLLİYET";
analoji/emsal-uygunluk bağı, `oa-illiyet`'in nedensellik grafıyla
karıştırılmasın) + **DAMGA** (kapalı enum:
`LEHE`/`ALEYHE`/`ALEYHE-AYIRT`/`NOTR`) alanları dolu mu, `ALEYHE-AYIRT`
ise AYIRT-ETME zorunlu alanı yazılmış mı (şema: `oa-kiyas/references/
ictihat-muhakeme-sablonu.md`). Kayıt `_oa/cikti/NN-ictihat-muhakeme.md`
olarak yazılır.

**Kritik doktrin (bağlayıcı, sapma yok):** dış çıktı (dilekçe) daima
müvekkil LEHİNEdir. `ALEYHE` (ayırt edilmemiş) içtihat dilekçeye **girmez**
ama iç analizde (muhakeme kaydı + `oa-antitez`) işlenmesi **ZORUNLUdur** —
saklanmaz. `ALEYHE-AYIRT` = aleyhe kararı ayırt ederek karşılamak (meşru
savunma tekniği, m.6 ihlali değil). Varsayılan-`NOTR`/damgasız kayıt
"muhakeme edilmemiş" sayılır (fail-closed) — hiçbir hâlde "nötr/geçerli"
varsayılmaz. Yargıtay/BAM atfı olmayan esaslı dilekçe muhakemesi ZAYIF
sayılır.

## B. Teslim öncesi kontrol (pre-filing)
**Usul/şekil:** [ ] Süre hesaplandı, net satır var mı (`oa-sure`)? [ ] Doğru merci + hitap? [ ] Taraf bilgileri tam (ad/unvan, TCKN/VKN, adres, vekil+baro)? [ ] Esas no doğru? [ ] Harç/gider atlanmadı mı (HMK m.344)? [ ] Vekâletname (AYM m.47/4)? [ ] İmza bloğu + sıfat tutarlı?
**Esas/içerik:** [ ] Vakıa→illiyet→norm/içtihat zinciri kopuksuz mu? [ ] Netice-i talep açık ve gerekçeyle birebir mi? [ ] Her iddia bir delile bağlı mı? [ ] Karşı tarafın en güçlü tezi **dahili** öngörülüp cephaneliğe hazırlandı mı (`oa-antitez`) — ama sunulan metne preemptive **konmadı** mı? [ ] **İfşa kontrolü:** sunulan metin, karşı tarafın henüz ileri sürmediği bir antitezi/zaafı ele veriyor mu? Veriyorsa **çıkar** — cephanelikte dahili kalsın. [ ] Zero fluff mu?
**Tip-spesifik:** [ ] İlgili dilekçe tipinin zorunlu unsurları + sık atlanan alanları kontrol edildi mi (`oa-dilekce`)?
**Üslup (P1-11 ek kural — ÖMERALP ÜSLUP BAĞLAMASI):** [ ] üslup playbook'a uygun mu? — `oa-dilekce/references/kanun-yolu-mimari-playbook.md` (B1-B7) üslubuyla (tez-omurgalı, akıcı, bütünsel bağlantılı) örülmüş mü; GÖRÜNMEZ İSKELET (İDDİA→NORM→İÇTİHAT→ÖRTÜŞME→SONUÇ) yüzeye ETİKET olarak sızmamış mı ([H] advisory), karşı-taraf-kusuru bağlamında GİDERİLMESİNE yönelik onarma-talebi kurulmamış mı ([I] advisory) — `dilekce_denetim.py`'nin [H]/[I] uyarıları gözden geçirildi mi?

## C. Müvekkil-aleyhi zaaf protokolü
Sadakat körü körüne onaya değil ilkelere yöneliktir. **Her** esaslı dosyada, yazımdan önce çalıştır:
- [ ] Müvekkilin **kendi belgelerindeki** çelişki/zaaf nerede? (örüntü: müvekkilin kendi ihtarnamesindeki olgu çelişkisi, ihtirazi kayıt yokluğu, desteksiz rakam.)
- [ ] Karşı tarafın en güçlü kozu ne; lehe nasıl konumlanır (gizleyerek değil, yöneterek)?
- [ ] Usul açığı var mı (süre, görev/yetki, derdestlik, kesin hüküm)?
- [ ] İspat yükü kimde; müvekkil karşılayabiliyor mu? Değilse strateji (yemin/isticvap/bilirkişi) buna göre mi?
- [ ] **En kötü senaryo** müvekkile açıkça söylendi mi? Sulh/uzlaşma daha rasyonel mi? (bu sorudan çoğu kez müzakere önerisi doğar.)

## C2. BAĞIMSIZ İÇERİK HAKEMİ — zorunlu adım (v0.5.5.2, saha kanıtlı)
**Mekanik kapıların hepsi yeşilken bile içerik yanlış olabilir.** 2026/307
dosyasında künye/şablon/defter kapılarının tümü yeşildi; ayrı bir denetçi
**dosya evrakına karşı "çürütmeye çalış" brifiyle** koşturulduğunda **1 KRİTİK**
hata çıktı: nakden tazmin savunmasındaki mükerrerlik kurgusu **aritmetik olarak
çelişikti** — karşı tarafın 836 rakamı zaten `1100 − 264` idi, yani 264 o
hesabın DIŞINDAYDI; taslak ise "836'nın içinde, düşülmeli" diyordu. Dilekçe
**kendi başka bölümüyle** çelişiyordu. Yanına 6 küçük bulgu: alıntı sadakati
(kip uyarlaması tırnak İÇİNDE yapılamaz), "baştan beri/hep" tarzı
genellemelerin sicil kronolojisiyle çapraz kontrolü, dosyada dayanağı olmayan
olgusal cümle, noter işlemi NİTELEME hatası, yer tutucu artığı.

Bu yüzden teslimden önce **ayrı bir denetçi** koşar (mekanik kapıların yerine
DEĞİL, onlara EK):
- Brif: *"Bu dilekçeyi çürütmeye çalış. Dosya evrakı tek gerçek kaynaktır."*
- [ ] **Aritmetik tutarlılık:** sayı/tarih içeren HER savunma, taslağın **kendi
      diğer bölümleriyle** aynı hesabı veriyor mu? (Bir rakamın nasıl
      türetildiği bir yerde açıklanıp başka yerde farklı türetilmişse KRİTİK.)
- [ ] **Alıntı sadakati:** tırnak içi metin kaynakla BİREBİR mi? Kip/çekim
      uyarlaması tırnağın DIŞINDA yapılır.
- [ ] **Dayanaksız olgu:** dosyada karşılığı olmayan olgusal cümle var mı?
- [ ] **Niteleme doğruluğu:** belge/işlem, gerçekte olduğu şey olarak mı
      adlandırılıyor? (bkz. `oa-dilekce/references/ticaret-sicili-desenleri.md`
      — TTSG yevmiyesi GK TASDİK yevmiyesidir, devir sözleşmesi yevmiyesi değil.)
- [ ] **Genelleme denetimi:** "baştan beri / hep / hiç" gibi mutlak ifadeler
      kronolojiyle sınandı mı?
`dilekce_denetim.py`'nin **[J] SAYI/TARİH HARİTASI** kapısı (advisory — ASLA
bloklamaz) aynı sayının birden çok yerde geçtiği noktaları bir arada listeler;
kapı çelişkiyi SÖYLEMEZ, **görünür kılar** — muhakeme hakemindir.

## D. Aktif fırsat taraması (zaafın ikizi)
Kontrol yalnızca zaaf avı değildir. Zaafı tararken **kullanılmamış lehe açıları** da ara: olguların desteklediği eksik bir talep, devreye sokulmamış bir karine/usul kaldıracı, güçlendirilebilecek bir argüman. Her "hayır" için bir **düzeltme + iyileştirme** öner — sadece sorunu işaretleme, müvekkilin konumunu yükselten çıkışı da göster.

## Çıktı kuralı
Teslimde **"Açık uçlar ve riskler"** başlığı: tamamlanacak alanlar (tebliğ tarihi, adres, harç), teyit bekleyen atıflar, müvekkil-aleyhi zaaflar **görünür** listelenir. Otomasyon muhakemeyi besler, yerine geçmez; nihai karar Can'ındır.

## Kompozisyon ve yol haritası
Tüm parçaların çıktısı teslimden önce buradan geçer. **`oa-antitez`** (deterministik kritik motoru) bu protokolün üstünde çalışır: sabit saldırı cephelerini eksiksiz dolaşır, her antiteze çürütme veya işaretli artık risk arar, dayanak teyidini denetler. Bu parça o motorun **protokol temelidir**; ikisi teslimden önce birlikte koşar (`oa-kontrol` denetim listesi + `oa-antitez` çökertme matrisi).

## Öğrenme günlüğü
Yeni bir kontrol kalemi veya zaaf kalıbı öğrenildiğinde ekle, aşağıya işle, yeniden paketle.
## Anayasal düstur — usul esasa üstündür
Usulün esasa takaddümü ailenin anayasal düsturudur: usulden düşen dosya esasa hiç giremez; süre, usul hukukunun parçası ve telafisiz tek hatadır. Teslim öncesi denetim **USUL-ÖNCE sırasıyla** yürür: (0) süre/süre satırı doğru ve takvimde mi; (1) görev/yetki/merci; (2) harç/gider; (3) zorunlu unsurlar; (4) taraf/temsil/vekâlet — bunlar temizlenmeden esas denetimine geçilmez. B listesine ek madde: **karşı tarafın süreli işlemleri tarandı mı** (`oa-sure --islem`), tespit edilen kaçırma çalışmaya net/kesin dille eklendi mi, tebliğ tarihi belgeli mi?

## Anayasal bloklar — tek kaynak (anayasa.md)
Bu parça, ailenin ortak anayasal ilkelerine tabidir — **Çaba/token standardı** (model/efor kullanıcının tercihi; muhakemede/doğrulamada/çıktı kalitesinde tasarruf YOK, yalnız mekanik katmanda kayıpsız verimlilik), **Örnekleme ilkesi** (konu sınırlaması yok — kapsam TÜM Türk hukuku), **Doğaçlama meşruiyeti** (yöntem serbest, olgu MCP-teyitli), ayrıca Doğrulama mimarisi, Anonimleştirme ve Layer 0 gizlilik. **Tek ve yetkili kaynak: `ortak-avukat/references/anayasa.md`.** (Bu parça alt-ajan olarak koşarken bu ilkeler `oa-pipeline/scripts/oa_hafiza.py ajan-brif` ile taşınır.)

## Başbakan denetimi (anayasal)
Bu parça, ailenin Başbakanı `oa-pipeline`'ın icra+denetimine tabidir: çağrıldığında disiplini İSTİSNASIZ ve tam işletilir (ama/fakat/token-tasarrufu gerekçesiyle kestirme YASAK). Görev savsaklanmaz; gerçekten yapılamayan bir şey varsa dürüstçe belirtilir ("yaptım" denmez) ve alternatif yöntem üretilir. Önemli olan proses ve çıktı kalitesidir.

## Müvekkil-aleyhi: iç/dış ayrımı (anayasal)
Zaaf taraması İÇ analizdir: müvekkilin zaafları/aleyhindeki deliller/riskler avukata DÜRÜSTÇE ve eksiksiz raporlanır (gizlenmez). Ama teslim öncesi denetimde, bu zaafların DIŞ dilekçeye sızıp sızmadığı da kontrol edilir — müvekkil aleyhine ifade dış metinde varsa çıkarılır. Kural: iç dürüstlük + dış koruma birlikte.

## Manifest kapatma (teslim öncesi — anayasal)
Teslim öncesi denetimde EVRAK MANİFESTOSU kapatılır: manifestteki her evrak fiilen işlendi mi, atlanan/okunamayan kaldı mı? Atlanan veya OCR'lanamamış evrak varsa açıkça raporlanır — "tüm dosya incelendi" denmeden önce bu sayım tutturulur. Eksik tarama, teslim engelidir.

## Fiziksel aktivasyon — simülasyon yasağı (anayasal)
Bu parça yalnızca ÜÇ kanıttan en az biriyle "çalıştı" sayılır: (1) Skill aracıyla FİİLEN çağrıldı ve bu gövde bağlama yüklendi (kullanıcının `/oa-kontrol` komutuyla eşdeğer); (2) scripti gerçekten koştu ve çıktısı görünür; (3) gerektirdiği MCP çağrısı fiilen yapıldı (araç + sorgu + sonuç kaydıyla). Kısa description her zaman bağlamda durur — o VİTRİNDİR, disiplin değildir; gerçek disiplin bu gövdededir. Bu yüzden hiçbir parça bu parçayı description'ından TAKLİT EDEMEZ; bu parça da başka bir parçanın işine ihtiyaç duyduğunda onu Skill aracıyla fiilen çağırır (olmuyorsa SKILL.md'sini Read ile yükler; o da olmuyorsa "FİZİKEN YÜKLENEMEDİ" diye açıkça yazar). Yapılmamış çağrı 'yapılmış', koşmamış script 'koşmuş' gösterilemez — bu, halüsinasyonun ta kendisidir. Devir alırken/verirken kısa DEVİR PAKETİ (ne yapıldı → ne bekleniyor → hangi kanıt) kullanılır ve pipeline defterine (`oa-pipeline/scripts/pipeline_kayit.py`) işlenir. Bu parçanın ürettiği her kalıcı çıktı (JSON/rapor/devir paketi) çalışılan klasörün `_oa/` yerel hafıza kökünde yaşar (yapı: `oa-pipeline` → Çalışma Kökü).

## Değişiklik Günlüğü
Tam günlük `references/degisiklik-gunlugu.md`'dedir (bağlam ekonomisi için ayrıldı — içerik aynen korunur; yeni kayıtlar oraya işlenir). Güncel sürüm: **v3.26**.

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

## v0.5.8.5 — teslim zinciri: advisory tamamlanma + e-imza halkası + istisna defteri

### B4 — RED makbuzda advisory rapor (zincirin görünür yarısı)

Engelleyici bir kapı kapandığında İLK-ENGELDE-DUR exit davranışı DEĞİŞMEZ;
ama engelleyici-OLMAYAN denetimler (devralma-aday raporu, şekil, prov-tazelik,
yerel-damga, tazelik advisory) yine de koşulur ve RED makbuzu
`advisory_denetimler` alanı kazanır (saha kanıtı: künye BLOK'u kenar ihlalini
görünmez bırakmıştı). Bu satırlar KAPI DEĞİLDİR: exit'i etkilemez, dosya
sistemine dokunmaz — RED raporunu okurken advisory bölümünü de OKU; engel
giderilince seni bekleyen ikinci sürprizi orada görürsün.

### B5 — E-İMZA MÜHÜR HALKASI (imzalı türev BAYAT değildir)

- UYAP editörü bir `.udf`'i e-imzalayınca zip'e `sign.sgn` girdisi ekler —
  dosyanın baytları DEĞİŞİR. Bu yüzden imzalı nüshanın sha'sı imza-öncesi
  mühürle eşleşmez; bu **BAYAT değil TÜREV'dir**. `muhur_yaz.py` sign.sgn
  tespit ederse tipi otomatik `e-imzali-nusha` yapar; `was_derived_from` =
  imza-öncesi nüshanın sha'sı (zincir kurulamıyorsa None + görünür uyarı).
- `teslim_paketi.py`: was_derived_from zinciri kurulmuş e-imzalı nüsha →
  YEŞİL; imzalı ama mühürsüz/zincirsiz → "imzalı türev mühürsüz" uyarısı +
  best-effort e-imzali-nusha mührü + istisna defterine `dogrulama-toleransi`
  satırı. İmzasız dosyada PROV-BAYAT RED'i AYNEN sürer.

### E-İMZA GUARD — imzalı nüshaya kenar yaması ASLA uygulanmaz

Kenar yaması zip'i yeniden yazar ve e-imzayı BOZAR. `sign.sgn`'li nüshada
kenarlar 42.52 pt değilse: yama YOK, RED de YOK (dosya zaten imzalı — karar
avukatındır); sapma görünür uyarı + makbuzda `sekil_imzali_sapma` alanı +
istisna defteri kaydı olur. Düzeltme imza ÖNCESİ sürümde yapılıp yeniden
imzalanır — imzalı dosyaya dokunulmaz.

### A4.8 — Teslim sunum disiplini

- **Durum sorusuna makbuz okunarak cevap ver.** "Teslime hazır mı / ne
  durumda" sorusunun cevabı bellekten değil `_oa/defter/teslim-makbuz.json`
  (ya da `teslim-makbuz-RED.json`) OKUNARAK verilir — makbuzda ne yazıyorsa
  durum odur.
- **RED makbuz kullanıcı mesajında GİZLENEMEZ.** Son deneme RED ise bu,
  kullanıcıya verilen özette açıkça ve ilk satırlarda söylenir (sebep +
  kapanan kapı); RED'i geçiştirip "taslak hazırlandı" demek makbuz
  garantisinin ihlalidir.
- **Teslimde tam yerel yol + mühür notu.** Teslim edilen ürünün TAM yerel
  yolu yazılır ve şu not eklenir: ürün taşınırken/kopyalanırken yanındaki
  `.prov.json` mührü BİRLİKTE taşınır (`muhur_yaz.py --tasi ESKI YENI`) —
  mühürsüz kopya, soy zinciri kopmuş kopyadır.

### İSTİSNA DEFTERİ — `_oa/defter/istisna-kayitlari.jsonl` (ortak şema)

Append-only JSONL; her satır: `{"zaman": ISO, "tur": ..., "ilgili": str,
"gerekce": str, "onay": "avukat"|"otomatik-kural", "imza": araç-imzası}`.
Yazan araçlar ve `tur` değerleri:

| Araç | tur | onay |
|---|---|---|
| `kunye_teyit.py` (B1 kendi-dosya-no muafiyeti) | `kunye-istisna` | otomatik-kural |
| `dilekce_denetim.py` (`--istisna-gerekce` ile [Y]/[T] düşürme) | `yanlis-pozitif-ilani` | avukat |
| `gizlilik_tara.py` (`--override-onay avukat`) | `gizlilik-deny-override` | avukat |
| `teslim_paketi.py` / `udf_yaz.py` / `pipeline_kayit.py` (e-imza toleransları) | `dogrulama-toleransi` | otomatik-kural |

Defter kayıt aracıdır, kapı değildir: yazılamaması akışı kırmaz ama görünür
uyarı bırakır. Hiçbir muafiyet/tolerans SESSİZ kalmaz — hepsi bu deftere iz
düşer; teslim öncesi gözden geçirmede defter de okunur.

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
python scripts/teslim_paketi.py <taslak.md> --tip <tip> --taraf <taraf> [--dis-arac] --kok .
```
(`--tip`: dava|cevap|istinaf|temyiz|aym_bireysel|genel; `--taraf`: davaci|davali|sanik|katilan|mudahil — boş bırakılabilir; `--dis-arac`: çıktı dış araca gidecekse Privacy Layer 0 kapısını zincire ekler; `--kok`: çalışma kökü.) Zincir dilekce_denetim → kunye_teyit → ictihat_muhakeme_denetim → [gizlilik_tara] → defter `--denetle` → tam_tur `--durum` sırasıyla koşar, ilk kapanan kapıda durur ve tek raporda hangi kapının kapandığını basar; hepsi geçerse UDF üretir ve "TESLİME HAZIR" der (exit 0). Bu script çalıştırılmadan/çıktısı görülmeden "teslime hazır" sözle beyan edilemez (R2: tek ölçüt bu script'in exit kodudur) — fiziksel aktivasyon kuralı burada da geçerlidir.

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

## C. Müvekkil-aleyhi zaaf protokolü
Sadakat körü körüne onaya değil ilkelere yöneliktir. **Her** esaslı dosyada, yazımdan önce çalıştır:
- [ ] Müvekkilin **kendi belgelerindeki** çelişki/zaaf nerede? (örüntü: müvekkilin kendi ihtarnamesindeki olgu çelişkisi, ihtirazi kayıt yokluğu, desteksiz rakam.)
- [ ] Karşı tarafın en güçlü kozu ne; lehe nasıl konumlanır (gizleyerek değil, yöneterek)?
- [ ] Usul açığı var mı (süre, görev/yetki, derdestlik, kesin hüküm)?
- [ ] İspat yükü kimde; müvekkil karşılayabiliyor mu? Değilse strateji (yemin/isticvap/bilirkişi) buna göre mi?
- [ ] **En kötü senaryo** müvekkile açıkça söylendi mi? Sulh/uzlaşma daha rasyonel mi? (bu sorudan çoğu kez müzakere önerisi doğar.)

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

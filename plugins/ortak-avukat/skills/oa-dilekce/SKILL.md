---
name: oa-dilekce
description: >-
  Ortak Avukat sisteminin DİLEKÇE/SÖZLEŞME YAZIM parçası. Türk hukukunda dava,
  cevap, istinaf, temyiz dilekçesi; AYM bireysel başvuru; yemin teklif dilekçesi;
  idari kanal başvuru dilekçesi; sözleşme tahriri (boşanma protokolü, adi ortaklık);
  hukuki mütalaa yazımında DEVREYE GİR. Her tip için zorunlu unsurları ve sık atlanan
  alanları (tebliğ tarihi, ihtirazi kayıt, harç, ihlal eksenleri) playbook olarak
  uygula. Kullanıcı bir dilekçe/sözleşme/mütalaa istediğinde — tip adını anmasa bile —
  tetikle. Bağımsız çalışır; `oa-sure` (süre satırı), `oa-ictihat` (teyitli atıf) ve
  `oa-kontrol` (teslim öncesi denetim) ile takım oynar.
---

# oa-dilekce — Dilekçe ve Sözleşme Playbook'ları

Sök-tak parça. Her tip için **zorunlu unsurlar** (eksikse usulden ret/iade) ve **sık atlanan alanlar** (en çok hata yapılan yer). Madde numaraları başlangıç çıpasıdır; usul kuralı kullanım anında `oa-ictihat` üzerinden teyit edilir. **Bu, zincirin son/çıktı aşamasıdır:** interview → alan → içtihat → antitez halkalarının ürünü burada belgeye dönüşür.

## Yazar sistemi ve lafzı — esas kural
Bu parça `ortak-avukat` ailesinin yazım çıktısıdır ve ailenin tasarımcısı **Av. Bayram Can Çapar**'ın dilekçe sistemine bağlıdır. **Çapar tarafından yazılan/yazılacak dilekçelerde onun kendi sistemine ve lafzına (üslup, dizilim, ifade tarzı, başlıklandırma, terim tercihi) uymak ESAS kuraldır** — jenerik bir şablon dayatılmaz, mevcut üslubu korunur ve sürdürülür. Eldeki bir Çapar dilekçesi örnek/şablon olarak verildiğinde: önce onun yapısal düzeni ve lafzı çıkarılır, sonra yeni dilekçe **o lafza sadık** üretilir. Aşağıdaki ortak omurga ve tip playbook'ları bu lafzın *üzerine oturduğu iskelettir* — onun yerini almaz; çatışma hâlinde Çapar'ın yerleşik üslubu önceliklidir (zorunlu usul unsurları hariç — onlar her hâlde bulunur). Bu kural anonimleştirme anayasasının istisnasıdır: Çapar sistemin tasarımcısıdır ve söz konusu olan müvekkil/dava izi değil, tasarımcının kendi yazım metodudur.

## Ortak omurga (her dilekçede)
Doğru merci + hitap → taraflar (ad/unvan, TCKN/VKN, adres, vekil + baro/sicil) → esas no → konu → açıklamalar (vakıa → illiyet → norm/içtihat) → hukuki sebepler → deliller → **netice-i talep** → tarih + imza + sıfat. Talep gerekçeyle birebir örtüşür; her iddia bir delile bağlanır.

## İçtihat kullanımı — tam künye + aynen alıntı + bağlamsal açıklama
Uyuşmazlığa uygun içtihat bulunduğunda (her zaman `oa-ictihat` üzerinden teyitli), dilekçede üç adım birlikte yürür:
1. **Tam künye:** daire + esas no + karar no + tarih eksiksiz yazılır.
2. **İlgili kısmın aynen alıntısı:** kararın yalnızca uyuşmazlıkla **ilgili pasajı** (gerekçenin ilgili yeri) **birebir** alıntılanır — tüm karar değil, davayla bağlantılı kısım. Alıntı, MCP'den çekilen **karar metninden** gelir; **hafızadan/yeniden kurarak alıntı yapılmaz** (atıf denetimi → `oa-kontrol` A). **OCR kontrolü:** metin OCR/markdown dönüşümünden geldiği için bozuk olabilir; alıntıda kusur sezilirse **çalışmada "OCR şüphesi" diye bildir** ve kanonik kaynakla teyit et (`oa-ictihat`) — OCR hatasını "birebir" diye dilekçeye taşıma.
3. **Bağlamsal-anlamsal açıklama (alıntıyı boşta bırakma):** alıntının hemen ardından, içtihadı **somut dosyaya bağlayan** yeterli açıklama yazılır — bu karar neden bu olguya uygulanır, olgular arasındaki benzerlik/illiyet nedir, müvekkil lehine hangi sonucu doğurur. Çıplak alıntı (açıklamasız) kabul edilmez; içtihat ancak davaya **uygulanarak** değer üretir.

## Playbook'lar

**Dava dilekçesi** — Zorunlu (HMK m.119): mahkeme; taraflar+TCKN; vekil; konu ve **değer/miktar** (harç/görev/kesinlik); vakıalar (sıra no); deliller (vakıayla eşli); hukuki sebepler; talep; imza. Sık atlanan: dava değeri, delil-vakıa eşlemesi, yetki/görev.

**Cevap dilekçesi** — Zorunlu (HMK m.129): savunma; karşı vakıalar; deliller; **ilk itirazlar** (süresinde sürülmezse düşer); talep. Süre kural olarak iki hafta. İstihkak (İİK m.97/a): **mülkiyet karinesi** ekseni (istihkak savunmasının taşıyıcı eksenlerinden). Sık atlanan: ilk itirazların süresinde sürülmesi; inkâr edilmeyen vakıanın ikrar sayılması.

**İstinaf dilekçesi** — Zorunlu (HMK m.342 vd.): ilk derece künyesi; **somut, gerekçeli istinaf sebepleri**; talep. Süre iki hafta (m.345); harç/gider tam (m.344). Sık atlanan: her sebebin ilk derece dosyasındaki **somut dayanağa** bağlanması; katılma/cevap süreleri (m.347-348). (örüntü: işçilik istinafında hukuka aykırı delil m.189/2 + toplu iş sözleşmesinin dosyaya celbedilmemesi — çok gerekçeli istinafta her sebep ayrı sütun.)

**Temyiz dilekçesi** — Zorunlu: BAM künyesi; **hukuka aykırılık** sebepleri; talep. Süre iki hafta (m.361); temyiz edilebilirlik (parasal sınır/kategori) önce kontrol. Maddi vakıa değil, hukuka aykırılık ekseninde yaz.

**AYM bireysel başvuru** — Zorunlu (6216 m.47/3): kimlik-adres; ihlal edilen hak; **dayanılan Anayasa hükümleri**; ihlal gerekçeleri; **başvuru yolları tüketme aşamaları**; tüketme/öğrenme tarihi; zarar; deliller + karar aslı/örneği + harç belgesi; vekilse **vekâletname** (m.47/4). Süre 30 gün (m.47/5 → `oa-sure`). İhlal eksenleri: gerekçeli karar hakkı, silahların eşitliği/sürpriz karar yasağı, mülkiyet, özel hayat/meslek hayatı; her eksen AYM-teyitli kararla. Sık atlanan: tam tüketme; kişisel/güncel/doğrudan etkilenme (m.46); süre başlangıcı (en sık açık uç: tebliğ/öğrenme tarihi).

**Yemin teklif dilekçesi + metni** — Dayanak HMK m.225 vd.; iade m.228. Vakıa **kesin, tek tek, net** formüle edilir. Yalnızca kesin delil bulunmayan, çekişmeli, yeminle ispatı caiz vakıada; yeminin iadesi ihtimali müvekkile anlatılır. (bono uyuşmazlığı örüntüsü: teklif dilekçesi + yemin metni + m.228 birlikte hazırlanır.)

**İdari kanal başvuru (çocuk teslimi/kişisel ilişki)** — Dayanak 5395 ÇKK + 7343 + Yönetmelik; **Adli Destek ve Mağdur Hizmetleri Müdürlüğü** kanalı (eski İİK m.25 vd. mülga). Asil bizzat ise birinci tekil şahıs; mahkeme kararı onaylı sureti; varsa 6284 kararı; iletişim bilgisi zorunlu. Sık atlanan: asil/vekil diline göre imza bloğu; adres/telefon; teslim süresi/yeri.

**Sözleşme tahriri** — *(NOT: kapsamlı sözleşme işi artık ayrı parça `oa-sozlesme`'dedir — tahrir/inceleme/revize/müzakere, kloz kapsam denetimi scriptiyle; bu playbook basit/hızlı protokoller ve aile-hukuku protokolleri için kalır.)* Boşanma protokolü: velayet + **kişisel ilişki takvimi** (tatil/bayram/yaz), nafaka, mal rejimi/**katılma alacağı**, adres bildirimi, uluslararası seyahat izni. Adi ortaklık/ticari: edim dengesi, fesih/tasfiye, paylı mülkiyet, mahsuplaşma, defter/kasa, yetki. Sık atlanan: ifa yeri/zamanı, temerrüt/cezai şart, ihtirazi kayıt, fesih usulü.

**Hukuki mütalaa** — Yapı: sorun → maddi vakıa → norm (teyitli) → içtihat (teyitli) → **karşı tez + zaaflar** → sonuç/strateji + açık uçlar. Sık atlanan: müvekkil-aleyhi zaafın açıkça raporlanması; sulh/uzlaşma alternatifi; kesin tavsiye dayatması değil karar-malzemesi.

## Aktif çıkarım refleksi
Şablonu edilgen doldurma. **En güçlü müvekkil-lehi çerçeveyi sen kur**: olguların desteklediği ama anılmamış bir talebi/savunmayı ekle; argümanları en yüksek etki için sırala; zayıf görüneni lehte konumlandır (gizleyerek değil, yöneterek). Dilekçe bir form değil, lehe inşa edilen bir stratejidir.

## Sunum disiplini — sunulmamış antiteze değinme
Sunulan dilekçede, karşı tarafın **henüz ileri sürmediği** bir savunmaya/iddiaya karşı preemptive çürütme **yazma** — kendi zayıf noktanı işaret etmek ve karşı tarafı silahlandırmaktır. Dilekçeyi dosyada/karar gerekçesinde fiilen **var olana** göre kur (dava dilekçesi kendi tezini; cevap karşı tarafın ileri sürdüğünü; istinaf/temyiz kararın gerekçesini karşılar). Hipotetik antiteze hazırlık `oa-antitez` cephaneliğinde **dahili** durur; karşı taraf ileri sürünce devreye girer. (Not: olguların desteklediği kendi olumlu talebini eklemek bundan farklıdır ve teşvik edilir.)

## Kompozisyon ve çıktı
Süre satırı için `oa-sure`; her atıf `oa-ictihat`'tan teyitli; alan tespiti `oa-alan`.

**Çıktı formatı — UDF VARSAYILAN (kurucu kural):** Kullanıcı/Fable kararı: **aksi açıkça talep edilmedikçe (ör. "md olarak ver", "docx istiyorum") dilekçe çıktısı UDF formatında üretilir.** md taslak her hâlde ARA ÜRÜNdür (UDF ondan türetilir), teslim edilen NİHAİ çıktı UDF'dir. Akış: taslak metin (md) → `python scripts/udf_yaz.py --girdi taslak.md --cikti dilekce.udf` (UYAP'a yüklenebilir; gerçek editörde `format_id` teyidi gerekir) → aşağıdaki **UDF GEÇERLİLİK KAPISI**. Yalnız kullanıcı açıkça md/docx istediğinde bu akış atlanır.

**Teslim öncesi MEKANİK KAPILAR (dört yeşil ışık — geçmeden 'teslime hazır' yok):**
1. **UDF GEÇERLİLİK KAPISI** (UDF çıktısı üretildiyse zorunlu) — `python scripts/udf_yaz.py --dogrula dilekce.udf` (yazmadan var olan dosyayı denetler) **veya** `python scripts/dilekce_denetim.py <taslak.md> --tip ... --taraf ... --udf dilekce.udf` (aşağıdaki [A]-[D] ile birlikte tek çağrıda [E] olarak çalışır). Denetlenen: zip açılır mı, `content.xml` var mı, XML iyi biçimli mi, paragraf `startOffset`/`length` UTF-16 code-unit biriminde ARDIŞIK ve CDATA metniyle toplamda tutarlı mı, metin round-trip ediyor mu. Script yalnız **"geçerli/geçersiz UDF"** der — **"iyi dilekçe" demez** (sahte kesinlik yok); GEÇERSİZ ise exit 1.
2. `python scripts/dilekce_denetim.py <taslak.md> --tip <dava|cevap|istinaf|temyiz|aym_bireysel> --taraf <davaci|davali|sanik>` — tip başına zorunlu unsur + "avukata yakışan tertip-düzen" + OCR-teyit şerhi + **MÜVEKKİL-ALEYHİ İFADE TARAMASI** (anayasal tek katı sınır: davalıda kabul/ikrar, davacıda kendi iddiasını çökerten ifade → exit 1 ile durdurur).
3. `python ../oa-kontrol/scripts/kunye_teyit.py <taslak.md>` — her içtihat/mevzuat atfının teyit kütüğünde izi var mı (teyitsiz atıf → exit 1).
4. `oa-kontrol` A (atıf) + B (usul+esas) listeleri.

## Öğrenme günlüğü
Yeni bir tip/zorunlu unsur/sık-atlanan alan öğrenildiğinde ilgili playbook'a ekle, aşağıya işle, yeniden paketle.
## Anayasal düstur — usul esasa üstündür
Usulün esasa takaddümü ailenin anayasal düsturudur: usulden düşen dosya esasa hiç giremez; süre, usul hukukunun parçası ve telafisiz tek hatadır. Dilekçede **usul katmanı esastan önce kurulur ve denetlenir**: doğru merci (görev/yetki), süre satırı, harç, zorunlu unsurlar (m.119/129/342...), taraf/temsil — usulden dönen dilekçe esası hiç anlatamaz. Karşı tarafın süre kaçırması tespitliyse (`oa-sure --islem`, belgeli tebliğle) **süre/usul itirazı paragrafı dilekçenin EN BAŞINA** yazılır ve netice-i talep 'ÖNCELİKLE usulden (süre yönünden) reddi' ile açılır; esas savunma 'kabul anlamına gelmemek kaydıyla' onu izler.

## Anayasal bloklar — tek kaynak (anayasa.md)
Bu parça, ailenin ortak anayasal ilkelerine tabidir — **Çaba/token standardı** (model/efor kullanıcının tercihi; muhakemede/doğrulamada/çıktı kalitesinde tasarruf YOK, yalnız mekanik katmanda kayıpsız verimlilik), **Örnekleme ilkesi** (konu sınırlaması yok — kapsam TÜM Türk hukuku), **Doğaçlama meşruiyeti** (yöntem serbest, olgu MCP-teyitli), ayrıca Doğrulama mimarisi, Anonimleştirme ve Layer 0 gizlilik. **Tek ve yetkili kaynak: `ortak-avukat/references/anayasa.md`.** (Bu parça alt-ajan olarak koşarken bu ilkeler `oa-pipeline/scripts/oa_hafiza.py ajan-brif` ile taşınır.)

## Başbakan denetimi (anayasal)
Bu parça, ailenin Başbakanı `oa-pipeline`'ın icra+denetimine tabidir: çağrıldığında disiplini İSTİSNASIZ ve tam işletilir (ama/fakat/token-tasarrufu gerekçesiyle kestirme YASAK). Görev savsaklanmaz; gerçekten yapılamayan bir şey varsa dürüstçe belirtilir ("yaptım" denmez) ve alternatif yöntem üretilir. Önemli olan proses ve çıktı kalitesidir.

## Müvekkil-aleyhi dış çıktı yasağı (anayasal)
Teslim edilen dilekçe/sözleşme DIŞ çıktıdır: müvekkili zayıflatan, gereksiz ikrar içeren, karşı tarafa koz veren ifade ÜRETİLMEZ; metin daima müvekkil lehine kurgulanır. Zaaf varsa iç analizde (avukata) dürüstçe bildirilir ama dış belgeye yazılmaz — saklamak değil, karşı tarafın eline vermemek. (Zorunlu usul unsurları ve mahkemeye karşı dürüstlük hariç tutulamaz.)

## Fiziksel aktivasyon — simülasyon yasağı (anayasal)
Bu parça yalnızca ÜÇ kanıttan en az biriyle "çalıştı" sayılır: (1) Skill aracıyla FİİLEN çağrıldı ve bu gövde bağlama yüklendi (kullanıcının `/oa-dilekce` komutuyla eşdeğer); (2) scripti gerçekten koştu ve çıktısı görünür; (3) gerektirdiği MCP çağrısı fiilen yapıldı (araç + sorgu + sonuç kaydıyla). Kısa description her zaman bağlamda durur — o VİTRİNDİR, disiplin değildir; gerçek disiplin bu gövdededir. Bu yüzden hiçbir parça bu parçayı description'ından TAKLİT EDEMEZ; bu parça da başka bir parçanın işine ihtiyaç duyduğunda onu Skill aracıyla fiilen çağırır (olmuyorsa SKILL.md'sini Read ile yükler; o da olmuyorsa "FİZİKEN YÜKLENEMEDİ" diye açıkça yazar). Yapılmamış çağrı 'yapılmış', koşmamış script 'koşmuş' gösterilemez — bu, halüsinasyonun ta kendisidir. Devir alırken/verirken kısa DEVİR PAKETİ (ne yapıldı → ne bekleniyor → hangi kanıt) kullanılır ve pipeline defterine (`oa-pipeline/scripts/pipeline_kayit.py`) işlenir. Bu parçanın ürettiği her kalıcı çıktı (JSON/rapor/devir paketi) çalışılan klasörün `_oa/` yerel hafıza kökünde yaşar (yapı: `oa-pipeline` → Çalışma Kökü).

## Değişiklik Günlüğü
Tam günlük `references/degisiklik-gunlugu.md`'dedir (bağlam ekonomisi için ayrıldı — içerik aynen korunur; yeni kayıtlar oraya işlenir). Güncel sürüm: **v3.21**.

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

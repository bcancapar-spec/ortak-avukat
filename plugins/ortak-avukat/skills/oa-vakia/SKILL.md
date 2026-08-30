---
name: oa-vakia
description: >-
  Ortak Avukat sisteminin VAKIA/DELİL YÖNETİM parçası. Bir dosyanın olgu ve delil
  tarafını disipline eder: olayların kronolojisini kurar, her iddiayı dayandığı
  delile eşler, ispat boşluklarını ve hiçbir iddiaya bağlanmamış (yetim) delilleri
  yakalar, dosyayı tasnif eder. "Olayları sıralayalım", "kronoloji çıkar", "hangi
  delil neyi ispatlıyor", "ispat yükü", "dosyayı düzenle/tasnif et", "elimizde ne var"
  → kullanıcı açıkça istemese bile bir dosya analiz edilirken veya dilekçe öncesi
  tetikle. Hukukta güçlü olan sistemin olgu/delil yarısını tamamlar. Deterministik
  motor (bundled script) kronoloji + iddia↔delil matrisini ve boşluk denetimini üretir.
  Bağımsız çalışır; `oa-interview` (olgu toplama), `oa-dilekce` (vakıa anlatımı/deliller),
  `oa-antitez` (ispat/delil cephesi) ile takım oynar.
---

# oa-vakia — Vakıa ve Delil Yönetimi

Sök-tak parça. Gerçek davada işin yarısı olgu ve delildir; sistem hukukta güçlü, burada bu yarıyı disipline eder. Görevi: **kronoloji kur · iddiayı delile eşle · ispat boşluğunu ve yetim delili yakala · dosyayı tasnif et.**

## Deterministik motor
Script hukuki değerlendirme yapmaz; **sıralar, eşler, boşluk/yetim tespit eder.** İspatın yeterliliğine ve delilin caizliğine muhakeme + `oa-antitez` (ispat/delil cephesi) karar verir.

```bash
python scripts/vakia_matris.py --iskelet > _oa/cikti/04-vakia.json  # iddia+olay şablonu (STDOUT = saf JSON)
python scripts/vakia_matris.py --dogrula _oa/cikti/04-vakia.json   # kronoloji + matris + boşluk
```
`--iskelet` **yalnız JSON'u stdout'a** basar; banner/açıklamalar stderr'e gider (v0.5.14 — yukarıdaki yönlendirme önceden ayrıştırılamaz bir dosya üretiyordu). Girdi JSON'unun kökü sözlük değilse script traceback yerine tek satırlık hata verip exit 1 döner.
Çıktı: **(1) Kronoloji** (tarihe göre sıralı; tarihsizler ayrı işaretli), **(2) İddia↔delil matrisi** (her iddiayı destekleyen olaylar), **(3) İspat boşlukları** (belgeli/somut delili olmayan iddialar — ispat yükü riski), **(4) Yetim deliller** (hiçbir iddiaya bağlanmamış olgular) ve geçersiz referans/ispat-durumu denetimi.

## İş akışı
1. **Olguları topla** (`oa-interview` çıktısından) ve iddiaları belirle.
2. Her olayı `{tarih, olgu, belge, destekler:[iddia], ispat_durumu}` olarak gir; `--dogrula` ile kronoloji + matrisi üret.
3. **İspat boşluklarını kapat:** delilsiz iddia için ya delil bul ya stratejiyi değiştir (yemin/isticvap/bilirkişi → `oa-dilekce`). Boşluk kapanmazsa **açık uç** olarak müvekkile raporla.
4. **Yetim delilleri** değerlendir: ya bir iddiaya bağla ya da neden tutulduğunu not et (gereksizse çıkar).
5. **Dosya tasnifi:** belgeleri kronoloji + iddia eşlemesine göre etiketle; UYAP arşivi/indirici çıktıları bu yapıya göre dizilebilir (Can'ın arşiv yol haritası ile birleşir).

## UNSUR ŞABLONLARI — dava-türü bağlantısı (M4, Paket D — v0.5.5)
`oa-alan` dava türünü tespit ettiğinde, `oa-alan/references/unsur-sablonlari/`
altındaki asgari sette (tasarrufun-iptali.md, ise-iade.md, itirazin-iptali.md,
kidem-ihbar.md — **unsur | norm | delil-türü | yük** dört sütunlu) örtüşen bir
şablon varsa açılır: her **unsur** doğrudan `vakia_matris.py`nin `iddialar[]`
dizisine bir `id` (U1, U2, …) olarak taşınır, unsur metni iddia metni olur.
Delilsiz kalan bir unsur `--dogrula ... --json <yol>` ile `ispat_bosluklari`na
düşer ve `_oa/DURUM.md`de **🔴 kırmızı** görünür (P0-8 renderer'ın ayrı alanı —
bkz. `pipeline_kayit.py::_vakia_delilsiz_unsur_uyarisi`). Şablondaki norm
atıfları başlangıç ÇIPASIDIR; kullanım anında Mevzuat MCP'den teyit edilir.

## ispat_durumu kategorileri
**TAM ispat araçları:** `belgeli · tanik · bilirkisi · karine · ikrar · yemin` — bunlar, olayın `belge` alanı da doluysa iddiayı **belgeli destekli** yapar.
**KISMİ ispat aracı:** `beyan` — kayda geçer, matriste `kismi_destek` olarak görünür, ama **tek başına iddiayı belgeli yapmaz**; iddia yine `ispat_bosluklari`na düşer.
**Boşluk sinyali:** `ispatsiz`.

Kategori listesi **kapalı beyaz listedir** (v0.5.14): listede olmayan bir etiket (ör. `"video"`) yazılırsa olay artık iddiayı belgeli SAYMAZ ve `GEÇERSİZ ispat_durumu` bloğunda görünür. Önceden hesap negatif listeye dayanıyordu (`!= "ispatsiz"`) ve geçersiz etiketli dolu bir belge iddiayı sessizce "belgeli" yapıyordu.

`beyan` **daima ifade/sorgu tutanağı `belge`si ile yazılır** — belgesiz `beyan` olayı, `oa-pipeline/scripts/capraz_denetim.py`'nin `BELGESIZ_MESRU` kümesinde (`karine · ikrar · yemin`) yer almadığı için `OLGU_EVRAKSIZ` kopukluğu sayılır ve o script exit 1 verir. Bu küme v0.5.14'te **bilinçli olarak değiştirilmemiştir** (kapı bir kütük/olgu disiplini kapısıdır; beyanın belgesiz kalması meşru değildir).

## ÖZNE EŞLEŞTİRME — yazım varyantı taraması (v0.5.8.4, advisory)
Matris girdisine tarafları `taraflar` listesine, her olayın failini opsiyonel
`ozne` alanına yaz — `vakia_matris.py --dogrula` bu adları Jaro-Winkler ile
skorlar ve çıktıya `ozne_eslestirme` bölümünü ekler: **skor ≥0.92 → BAGLA**
(aynı öznenin yazım varyantı sayılır), **0.80-0.92 → AVUKATA-SOR**. Amaç
kayıpsızlıktır: "öznenin tüm beyanları" sorgusu yazım varyantı yüzünden kayıt
kaçırmasın. **AVUKATA-SOR görüldüğünde model KENDİ KARAR VERMEZ — iki yazımın
aynı kişi olup olmadığını avukata sorar ve cevabı gelene dek kayıtları
birleştirmez.** Tarama `saglikli` hesabına girmez (advisory); varyant yoksa
sessizdir.

## Aktif çıkarım refleksi
Kronolojiyi edilgen dizme. Sıralama sırasında **müvekkil lehine örüntü** ara: bir illiyet zinciri, bir karşı tarafın temerrüt anı, bir hak düşürücü sürenin başlangıcı, lehe bir karine doğuran olgu. Boşluğu yalnız işaretleme — **nasıl kapatılacağını** da öner.

## Kompozisyon
`oa-interview` olguyu toplar → **oa-vakia** sıralar/eşler → `oa-antitez` ispat/delil cephesini bu matrisle test eder → `oa-dilekce` vakıa anlatımını ve delil listesini buradan kurar (her iddia bir delile bağlı). Not (İçtihat Muhakeme Zinciri çapası): bu parçanın kurduğu olgu örüntüsü, `oa-kiyas`'ın MUHAKEME adımında her içtihat için yazdığı DAVAYA-BAĞ alanının (bkz. `oa-kiyas/references/ictihat-muhakeme-sablonu.md`) somut malzemesidir — DAMGA/G1-G3 mekanik kapıları `oa-kontrol`'dedir, bu parça yalnız girdisini besler.

## Öğrenme günlüğü
Yeni bir ispat aracı, tasnif kalıbı veya tekrar eden boşluk tipi öğrenildiğinde script/şablona ekle, aşağıya işle, yeniden paketle.
## Anayasal düstur — usul esasa üstündür
Usulün esasa takaddümü ailenin anayasal düsturudur: usulden düşen dosya esasa hiç giremez; süre, usul hukukunun parçası ve telafisiz tek hatadır. Kronoloji çıkarılırken **tarihli her usul işlemi** (tebliğ, dilekçe, itiraz, başvuru, kararın yüze okunması) ayrı işaretlenir ve süre-denetim adayı olarak `oa-sure`'ye beslenir — **karşı tarafın işlem tarihleri özellikle** (`--islem` denetimi). Tebliğ tarihlerinin BELGELİ olup olmadığı (şerh/mazbata/UYAP) delil matrisinde ayrı sütundur.

## Anayasal bloklar — tek kaynak (anayasa.md)
Bu parça, ailenin ortak anayasal ilkelerine tabidir — **Çaba/token standardı** (model/efor kullanıcının tercihi; muhakemede/doğrulamada/çıktı kalitesinde tasarruf YOK, yalnız mekanik katmanda kayıpsız verimlilik), **Örnekleme ilkesi** (konu sınırlaması yok — kapsam TÜM Türk hukuku), **Doğaçlama meşruiyeti** (yöntem serbest, olgu MCP-teyitli), ayrıca Doğrulama mimarisi, Anonimleştirme ve Layer 0 gizlilik. **Tek ve yetkili kaynak: `ortak-avukat/references/anayasa.md`.** (Bu parça alt-ajan olarak koşarken bu ilkeler `oa-pipeline/scripts/oa_hafiza.py ajan-brif` ile taşınır.)

## Başbakan denetimi (anayasal)
Bu parça, ailenin Başbakanı `oa-pipeline`'ın icra+denetimine tabidir: çağrıldığında disiplini İSTİSNASIZ ve tam işletilir (ama/fakat/token-tasarrufu gerekçesiyle kestirme YASAK). Görev savsaklanmaz; gerçekten yapılamayan bir şey varsa dürüstçe belirtilir ("yaptım" denmez) ve alternatif yöntem üretilir. Önemli olan proses ve çıktı kalitesidir.

## Evrak bütünlük denetimi (manifest — anayasal)
Büyük dosyalarda (UYAP 300-500+ sf) kronolojiden ÖNCE EVRAK MANİFESTOSU çıkarılır: klasördeki her dosya numaralı listelenir (ad, tür, sayfa, metin mi görüntü/TIFF mi, OCR durumu, tek satır içerik). İndirilen evrak adedi ile manifest adedi karşılaştırılır — eşleşmezse eksik adıyla raporlanır, analiz beklemeye alınır. Her olgu/kronoloji kaydı manifest'teki evraka #no ile bağlanır; hiçbir iddiaya bağlanmamış evrak "işlenmedi" işaretiyle görünür kalır. Görüntü/taranmış/TIFF evrak "okudum" diye varsayılamaz: OCR'dan geçirilir veya "okunamadı, manuel gerekli" denir. Amaç: kullanıcının eksik evrakı elle yakalamak zorunda kalmaması.

## Fiziksel aktivasyon — simülasyon yasağı (anayasal)
Bu parça yalnızca ÜÇ kanıttan en az biriyle "çalıştı" sayılır: (1) Skill aracıyla FİİLEN çağrıldı ve bu gövde bağlama yüklendi (kullanıcının `/oa-vakia` komutuyla eşdeğer); (2) scripti gerçekten koştu ve çıktısı görünür; (3) gerektirdiği MCP çağrısı fiilen yapıldı (araç + sorgu + sonuç kaydıyla). Kısa description her zaman bağlamda durur — o VİTRİNDİR, disiplin değildir; gerçek disiplin bu gövdededir. Bu yüzden hiçbir parça bu parçayı description'ından TAKLİT EDEMEZ; bu parça da başka bir parçanın işine ihtiyaç duyduğunda onu Skill aracıyla fiilen çağırır (olmuyorsa SKILL.md'sini Read ile yükler; o da olmuyorsa "FİZİKEN YÜKLENEMEDİ" diye açıkça yazar). Yapılmamış çağrı 'yapılmış', koşmamış script 'koşmuş' gösterilemez — bu, halüsinasyonun ta kendisidir. Devir alırken/verirken kısa DEVİR PAKETİ (ne yapıldı → ne bekleniyor → hangi kanıt) kullanılır ve pipeline defterine (`oa-pipeline/scripts/pipeline_kayit.py`) işlenir. Bu parçanın ürettiği her kalıcı çıktı (JSON/rapor/devir paketi) çalışılan klasörün `_oa/` yerel hafıza kökünde yaşar (yapı: `oa-pipeline` → Çalışma Kökü).

## Değişiklik Günlüğü
Tam günlük `references/degisiklik-gunlugu.md`'dedir (bağlam ekonomisi için ayrıldı — içerik aynen korunur; yeni kayıtlar oraya işlenir). Güncel sürüm: **v3.26**.

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

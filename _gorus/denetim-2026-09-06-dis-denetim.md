> **Kaynak belge (2026-09-06).** v0.5.16 infazının dayandığı ikinci dış denetim raporu (A-1..A-28 · B-1..B-8 · P0/P1/P2 reçetesi); `_gorus/` kuralıyla aynen alınmıştır. Müvekkil/dosya kimliği içermez (anayasa m.7).

# ORTAK AVUKAT v0.5.15 — DIŞ DENETİM RAPORU

| | |
|---|---|
| **Tarih** | 2026-09-06 |
| **Denetlenen** | `bcancapar-spec/ortak-avukat` · commit `80ac847` (2026-09-02) · paket **0.5.15** |
| **Denetçi** | Claude (Fable 5.1) — bağımsız dış okuma; hiçbir depo dosyasına dokunulmadı |
| **Karar mercii** | Av. Bayram Can Çapar — bu rapor karar materyalidir, karar değildir |
| **Kapsam** | 20 parçanın hukuki uyuşmazlığa yaklaşımı (metodoloji) · müvekkil menfaati boşlukları · mühendislik ve yönetişim |
| **Kapsam dışı** | Norm güncelliği (Yargı Pro MCP ile canlı tutuluyor; kullanıcı direktifi) · saha davranışı (Claude Code oturumu yok, parçalar fiilen koşturulmadı) |
| **Anonimleştirme** | Rapor hiçbir müvekkil, dosya veya karşı taraf kimliği içermez (anayasa m.7) |

Bu rapor **beyan değil ölçüm** ilkesiyle yazıldı: her bulgu bir satır numarası, bir grep sayısı, bir test çıktısı ya da bir MCP teyidine bağlıdır. Bağlanamayan iddia rapora girmedi.

---

## 0. Yönetici özeti

Aile, tutarlı bir kimlik kuruyor: **çekişmeli modda duruşma avukatı.** Bu kimliğin güçlü olduğu yerde — usul, süre, içtihat disiplini, antitez, yazım — parçalar kıdemli düzeyde düşünüyor; "model kurar, script denetler" ayrımı ve teyit≠muhakeme mimarisi bilinen en disiplinli hukuk-AI tasarımıdır.

Zayıf olduğu yer, kıdemli avukatın ikinci kimliğidir — **danışman**: zaman ve para (strateji'de yargılama süresi/erime yok, dilekçede talep bloğu doktrini ince), üçüncü aktörler (hâkim ve bilirkişi modellenmiyor), müvekkilin kendi kararı (onay düğümü ve risk toleransı yok), çekişmesiz çıkışlar (cezada müzakereli yollar, ticarette forum ve senaryo). Bir de iki **ontolojik** hata var: delil matrisinde tanık/bilirkişi/karinenin koşulsuz ispat sayılması ve kıyasın tek normlu olması — ikisi de "yeşil rapor, kaybedilen dosya" üretebilir.

Mühendislik tarafında tek P0: taranmış evrakta **OCR dil paketi yokluğu evrak özelliği gibi raporlanıyor** (bu ortamda 2 kırmızı test bu yüzden).

| Sınıf | Adet | P0 | P1 | P2 |
|---|---|---|---|---|
| A — hukuki yaklaşım / müvekkil menfaati | 28 | 3 | 11 | 14 |
| B — mühendislik / yönetişim | 8 | 1 | 2 | 5 |

---

## 1. Yöntem

1. **Tam klon okuması.** 276 dosya; anayasa, 20 SKILL.md gövdesi, references, 30 script, 23 kök yönetişim belgesi (STATUS, CHANGELOG, karneler, saha, sıçrama notu).
2. **Test süiti bu ortamda koşuldu:** Python 3.12.3 / Linux / tesseract var, `tur` dil paketi yok / udf-cli oturumu yok. Sonuç: **1749 yeşil · 2 kırmızı · 12 atlama · 203 sn.** `aile_dogrula`: temiz, 20 parça.
3. **Hook gecikmesi ölçüldü:** boş dizinde `pipeline_kayit.py --hook-*` 390–475 ms/çağrı.
4. **Kapsam taraması:** metodolojik boşluk iddiaları aile genelinde `grep` ile sınandı; sayılar Ek-2'de. "0" = kavram hiç geçmiyor.
5. **MCP teyidi:** rapordaki kritik norm iddiaları Mevzuat MCP'den madde metniyle doğrulandı (Ek-3). Doğrulanmayan her atıf **çıpa** olarak işaretlidir — uygulama anında teyit edilir, bu rapor künye otoritesi değildir.
6. **İlk tur düzeltmesi:** denetçinin ilk değerlendirmesi web önbelleğindeki v0.5.5.3 README'ye dayanıyordu; klonla çürüyen bulgular (§3.2) rapora alınmadı.

---

## 2. Envanter ve ölçüm

| Kalem | Değer |
|---|---|
| Dosya | 276 |
| Parça | 20 (çekirdek + 19 `oa-*`) |
| Python (üretim + test) | ~60.100 satır; en büyük 7 üretim scripti 15.872 satır |
| `pipeline_kayit.py` | 5.562 satır · 159 fonksiyon · her hook çağrısında import |
| Test fonksiyonu / toplanan | 1.628 def / 1.763 toplanan (`OA-SUIT-SAYISI` işaretçisi) |
| Doktrin + yönetişim metni | 1,16 MB Markdown |
| Hook olayı | 6 (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, SessionEnd) |
| Süre kuralı | 21, tümü JSON tek kaynakta, MCP teyit tarihli |
| Deterministik motor | 8 (antitez, vakıa, kıyas, usul, süre, illiyet, sözleşme, teslim) |
| Belgeli saha koşusu | 9 (v0.5.x döngüsü); toplam 149 dava beyanı |

---

## 3. Doğrulanan güçlü yanlar

### 3.1 Sistemin gerçekten yaptığı (tekrar yapılmasın)

- **Teyit ≠ muhakeme.** Arama araçları damgasız; tam metin çeken araçlarda damga + davaya bağ + döküm zorunlu. Damga RATIO + ÖRTÜŞME + FARK'tan türetiliyor, beyan edilmiyor. Aşılmışlık sorusu her teyitte zorunlu; kaynak URL yalnız teyit anında kaydedilen.
- **Usul katmanı üç cepheli** (karşı taraf / müvekkil / kamu gücü); kesin dil tebliğ belgeliliğine kilitli; kurtarma kapıları yargı koluna göre ayrışıyor (İYUK'ta eski hâle getirme yok); AY m.40/2 standart soru; YD nöbeti (v0.5.14).
- **Süre motoru** usul/maddi ayrımı yapıyor, üç yargı kolunda üç farklı adli tatil uzatması, e-tebligat ikili senaryo, güvenli taraf amaca göre tanımlı, kural↔kol uyuşmazlığında hesap duruyor.
- **Antitez disiplini:** sunulmamış antiteze karşı önleyici çürütme yasağı, praeoccupatio yalnız avukat onayıyla, celse kartı dahili filigranlı.
- **Yazım doktrini** avukat revizesinden damıtılmış yedi kural (tespit≠itiraz, terditli talep kurulmaz, savunulmayan usulî noktayı savunma, vaat değil sicile bağlı olgu, künye gövdede tekrarlanmaz, ispat yükü açıkça tahsis edilir).
- **Denetim kültürü:** CMK m.331/4 (3 gün) vs HMK m.104 farkı yakalanmış; kaynakça üretecinin gerçeğe aykırı "tam metniyle okundu" beyanı kapatılmış; çürüyen hakem tezi (m.273/1) kayda geçirilmiş.
- **Sıçrama notu kararı doğru:** önceki davanın cephaneliğini yenisine taşımamak — desen eşleştirme muhakemenin yerine geçer.

### 3.2 İlk turda "eksik" sanılan, klonda mevcut bulunan

Müvekkil hedefi tipolojisi (`oa-strateji` §1) · İYUK m.27 YD ayrımı · zorunlu arabuluculuk dört adreste · süre başlangıç türü çatalı · kurtarma kapıları kataloğu · adli tatil istisnası (`--adli-tatil-istisna`, HMK m.103 bent bent) · Av.K. m.38 çatışma taraması · celse kartı · ispat yükü carve-out (üç şart, fail-closed) · yürütmenin durdurulması nöbeti.

---

## 4. Bulgular — A: hukuki yaklaşım ve müvekkil menfaati

Her bulgu: **Parça · Bulgu · Neden önemli · Kanıt.** Öncelik §6'da.

### Çekirdek ve orkestra

**A-1 · ortak-avukat — dosya ağırlığı triyajı yok.**
Kimlik "her mesele son derece karmaşık kabul edilir" diyor; kıdemli avukatın asıl yeteneği ise hangi dosyanın basit olduğunu bilmektir. Basit bir ihtarnameye tam hat açmak müvekkile fazla-avukatlık faturasıdır. Anayasa m.1 derinlikten kısmayı yasaklıyor; orantılılık kısma değil, mesleki karardır. *Kanıt:* `ortak-avukat/SKILL.md` §0 son madde; §0.5/2 "tek-iş istisnası (dar)" yalnız izole soruyu kapsıyor.

**A-2 · oa-pipeline — ANTİTEZ (7), STRATEJİ'den (6) sonra.**
Karşı tarafın en güçlü tezi görülmeden dava/sulh kararı verilmez. `oa-strateji` §2 antitez çıktısını girdi sayıyor; `oa-antitez` "erken konum" tanımlıyor; sabit hat ikisiyle çelişiyor. *Kanıt:* `oa-pipeline/SKILL.md` "Sabit hat" 6-7; `oa-strateji/SKILL.md` §2; `oa-antitez/SKILL.md` "Kompozisyon (iki konum)".

**A-3 · oa-pipeline — "müvekkil onayı bekleyen" düğümü yok.**
`DURUM.md`'de "avukat kararı bekleyen" var. Sulh teklifi, dava değeri, risk kabulü, tedbir teminatı avukatın değil müvekkilin kararıdır (Av.K. m.34 bilgilendirme — çıpa). Kapanış adımı ders kaydı üretiyor, müvekkile bilgilendirme çıktısı üretmiyor. *Kanıt:* `oa-pipeline/SKILL.md` M7; "10. KAPANIŞ" tanımı.

### Dosyayı ele alma

**A-4 · oa-ingest — kritik evrak sınıfı süre nöbetini otomatik tetiklemiyor.**
Kıdemli avukatın ilk okuduğu üç şey — tebliğ mazbatası, ara kararlar, bilirkişi raporu — süreyi ve dosyanın kaderini belirler. Manifest bunları türe göre sınıflıyor ama tebligat evrakından tarih çıkarıp `sure-flag` yazmıyor; nöbet modelin fark etmesine bağlı. *Kanıt:* `oa-ingest/SKILL.md` "İş akışı"; `okuma_kapisi.py` yalnız boyut/öncelik listesi üretir.

**A-5 · oa-interview — muhatap karışıklığı ve cevap statüsü.**
Metin müvekkille konuştuğunu varsayıyor ("müvekkile yansıt", "müvekkilin verdiği bilgiyi tekrar sorma"); gerçekte avukatla konuşuyor. Bu, cevapların statüsünü silikleştiriyor: kıdemli avukat müvekkil anlatısını belge gelene kadar **iddia** sayar. Alımda her cevabın "belgeli / beyan" etiketi alması `oa-vakia`'nın `beyan` kategorisini doğrudan beslerdi. *Kanıt:* `oa-interview/SKILL.md` "Yönetici ilke", protokol adım 4.

**A-6 · oa-interview — masraf gücü ve risk toleransı sorulmuyor.**
Harç, bilirkişi, teminat ve karşı vekâlet riskini kimin ne kadar taşıyabildiği ve müvekkilin riske toleransı, strateji girdisi olmadan strateji kurulamaz. *Kanıt:* `soru-bankasi.md` ortak çekirdek 6 soru — hiçbirinde yok; `oa-strateji` "risk tolerans" 0.

**A-7 · oa-alan — forum seçimi yok.**
Konumlama Yargıtay merkezli ("hangi daire bakar"). İlk derece stratejisinin asıl sorusu birden fazla yetkili mahkeme varsa (HMK m.6 vd. seçimlik yetki — çıpa) hangisinin müvekkile uygun olduğudur: mesafe, iş yükü, bilirkişi havuzu, daire eğilimi. *Kanıt:* `oa-alan/SKILL.md` "yetki" 2, "forum" 0, "birden fazla yetkili" 0.

### Her işi saran katmanlar

**A-8 · oa-usul — tamamlanabilir kusurda zamanlama kararı yok.**
A-cephesi her kusuru "derhâl ileri sürer." Kıdemli avukat **tamamlanabilir** kusuru (harç, vekâletname, dilekçe eksiği) bazen bilerek geç görür — erken söylersen karşı taraf tamamlar; **tamamlanamaz** olanı (süre) derhâl vurur. Kusur→Sonuç→Talep asimetrisi "giderme talep etme"yi yasaklıyor, "ne zaman ileri sür" sorusunu cevaplamıyor. *Kanıt:* `oa-usul/SKILL.md` A-1..A-5; anayasa m.2 "derhâl ileri sürülür".

**A-9 · oa-usul — usul yolu daima "en ucuz" varsayımı.**
Görevsizlik/yetkisizlik itirazı kazanılsa bile dosya yeni mahkemede sıfırdan başlar; hızı isteyen müvekkil için usul silahı pahalıdır. Usul kazanımı maliyet-fayda tablosunun "1. satırı" ilan edilmiş; müvekkil hedefiyle tartılmalı. *Kanıt:* `oa-usul/SKILL.md` "Anayasal düstur" bloğu; `oa-strateji` aynı blok.

**A-10 · oa-sure — aşama tetikli süreler sınıfı yok (hukuk kolu).**
Nöbet tarih tetikli. Usulün kritik sürelerinin bir sınıfı **aşama tetikli**dir: ilk itiraz cevapla birlikte, delil bildirimi dilekçeyle ve sonradan delil yasağı (HMK m.145 — çıpa), ıslah tahkikat sonuna kadar, belge sunma kesin süresi. Ceza kolunda katılma anı "olay tetikli kırmızı bayrak" olarak eklenmiş (v0.5.13); hukuk kolunda karşılığı yok. *Kanıt:* aile genelinde `m.145` 0; `sure_kurallari.json` 21 kuralın tümü gün/hafta birimli.

**A-11 · oa-gizlilik — senkron klasör riski modellenmemiş.**
Katman dış araç çağrısını koruyor. Pratikte meslek sırrının en sık sızdığı yol dış çağrı değil, **senkronize klasör**dür: avukatın "Belgeler" klasörü OneDrive/Google Drive/Dropbox'a bağlıysa `_oa/` ve cephanelik hiçbir süzgeçten geçmeden yurt dışı buluta gider. *Kanıt:* `oa-gizlilik` altında senkron/OneDrive/Dropbox 0; "bulut" 4 geçiş, tümü dış araç bağlamında.

**A-12 · oa-illiyet — menfaat akışı kenarı yok.**
Graf neden-sonuç kuruyor; muvazaa, perde, tasarrufun iptali, organik bağ argümanı ise "kim kimden ne aldı, kim kazandı" sorusundan çıkar. Ticaret sicili deseninde (ardışık yevmiye) bu elle yapılıyor. *Kanıt:* `oa-illiyet/SKILL.md` kenar tipleri: ilişki (ortaklik…istirak) + illiyet (fiil_netice…islem_sonuc) — para/mal akışı kenarı yok.

### Olgu ve hukuk

**A-13 · oa-vakia — ispat ontolojisi hatalı (üç kalem).** ⚠ P0
(i) `tanik` **koşulsuz tam ispat** sayılıyor; Türk usulünde tanık şartlı delildir (senetle ispat kuralı, delil başlangıcı, karşı tarafın muvafakati — HMK m.200-203 çıpa). (ii) `bilirkisi` her iddia için ispat aracı sayılıyor; hukuki nitelendirme iddiasında bilirkişi delil değildir (HMK m.266 sınırı — çıpa). Matris **vakıa iddiası** ile **hukuki iddia**yı ayırmıyor. (iii) `karine` tam ispat sayılıyor; karine ispat etmez, yükü kaydırır. Üçü de "yeşil matris, dinlenmeyen delil" üretir; `DURUM.md` yeşil kalır. Bu bir mevzuat güncelliği sorunu değil, kategori hatasıdır. *Kanıt:* `vakia_matris.py:39` `ISPAT_TAM = {"belgeli","tanik","bilirkisi","karine","ikrar","yemin"}`; aile genelinde "senetle ispat" 0.

**A-14 · oa-ictihat — içtihat haritası adımı yok.**
Protokol "kapsamlı tara → lehe/aleyhe ayır → lehe kullan". Kıdemli avukat önce **haritayı** çıkarır — yerleşik hat mı, ayrışma mı, HGK/İBK var mı — sonra konumlanır. "Birincil kriter: lehe" modeli üç lehe karar bulunca durdurur; yerleşik hattın aleyhe olduğunu öğrenmeden. Portföy hiyerarşisi (HGK/İBK > daire) yazım aşamasında (M6) var, araştırma aşamasında yok. *Kanıt:* `oa-ictihat/SKILL.md` "Birincil kriter" 1-5; `oa-dilekce/SKILL.md` M6.

**A-15 · oa-kiyas — tek normlu silojizm.**
Uyuşmazlıkta çoğu kez **yarışan normlar** vardır (sözleşme/haksız fiil talep yarışması, özel/genel kanun) ve avukat müvekkil lehine olanı seçer: zamanaşımı uzunluğu, kusur şartı, ispat kolaylığı, faiz. Şemada iddia başına tek büyük önerme var. *Kanıt:* `oa-kiyas` altında "yarışan", "alternatif norm", "talep yarışması" 0.

### Karar ve savunma

**A-16 · oa-strateji — zaman ekseni yok.**
İlk derece + istinaf + temyiz yıllar alır; "bugün %60 sulh vs dört yıl sonra %100 + faiz" kararı süre tahmini ve alacağın erimesi olmadan verilemez. Kesin sayı üretilmez (doktrin doğru), nitel bant üretilir. *Kanıt:* `oa-strateji` altında "yargılama süresi", "zaman değeri", "enflasyon", "ne kadar sürer" 0.

**A-17 · oa-strateji — müvekkil risk toleransı girdi değil.**
Aynı dosya riskten kaçan ve risk seven müvekkil için farklı yol demektir. A-6 ile birlikte kapanır. *Kanıt:* `oa-strateji/SKILL.md` §1 hedef tipolojisi (para/hız/ilişki/emsel/risk durdurma) tolerans içermiyor.

**A-18 · oa-strateji — maliyet cetveli deterministik değil.**
Harç, bilirkişi, karşı vekâlet ve kısmi red oranı maliyet kalemi olarak sayılıyor, hesaplanmıyor. Kesinlik eşiklerini sabit yazmama kararı (DENETİM v0.5.14) doğru; aynı yaklaşımla yıl damgalı tarife dosyası + bayatsa fail-closed mümkün. *Kanıt:* aile genelinde AAÜT/karşı vekâlet 2 geçiş, düzyazı; script yok.

**A-19 · oa-strateji — malvarlığı koruma refleksi yok.**
"Haklı olmak ≠ tahsil etmek" tespiti var, eylemi yok: dava öncesi ihtiyati haciz/tedbir (İİK m.257, HMK m.389 vd. — çıpa), teminat, bunların kendi süreleri (İİK m.264, HMK m.397 — çıpa). "0. adım: koruma tedbiri gerekli mi" sorusu maliyet-fayda tablosunun önüne konmalı. *Kanıt:* ihtiyati haciz/tedbir yalnız `tasarrufun-iptali.md` şablonu, bir saha anekdotu (`oa-dilekce`) ve adli tatil istisna listesinde; `oa-strateji` 0.

**A-20 · oa-antitez — bilirkişi cephesi yok.**
Sekiz cephe karşı vekili modelliyor. Türk hukuk yargısında hükmün taşıyıcısı çoğu kez bilirkişi raporudur — raporun kırılma noktaları, itiraz stratejisi, uzman görüşü (HMK m.293 — çıpa) ayrı cephe olmalı. *Kanıt:* `antitez_matris.py:47` STANDART_CEPHELER 8 kalem; "bilirkişi" SKILL'de 1 (tetik olarak), "uzman görüşü" 0.

**A-21 · oa-antitez / oa-kontrol — hâkim lensi yok.**
İçerik hakemi "çürütmeye çalış" brifiyle karşı vekil gibi okuyor. "Hâkim bu dosyayı nasıl kapatmak ister" — iş yükü, gerekçe alışkanlığı, dairenin eğilimi — sorusu yok. *Kanıt:* `oa-antitez` "hâkim" 1 (tek cümle), `oa-kontrol` C2 brif metni.

### Üretim ve teslim

**A-22 · oa-dilekce — netice-i talep doktrini ince.** ⚠ P0
Gövde için sert disiplin var (görünmez iskelet, yedi kural); talep bloğu için yok. Dosya talep bloğunda kazanılır ya da kaybedilir: asıl/fer'i talep dizilişi, meşru terdit (seçimlik haklar) ile kendini yenen terdit ayrımı, **faiz türü ve başlangıcı**, saklı tutulan haklar, yargılama gideri ve vekâlet ücreti, tedbir talebi. **MCP-teyitli etki:** HMK m.107 (belirsiz alacak) 7589 s.K. ile mülga, m.109/4 kısmi davada bir defaya mahsus talep artırımı + zamanaşımının dava tarihinden kesilmesi (Ek-3). Bu, kısmi dava + harç + zamanaşımı üçgenini değiştiren bir **talep mühendisliği** kuralıdır ve playbook'ta karşılığı yok. *Kanıt:* `oa-dilekce/SKILL.md` "netice-i talep" 2, "terditli" 1, "fazlaya ilişkin" 0, "yargılama gider" 0; aile genelinde faiz/temerrüt 1, kısmi dava/m.109 0.

**A-23 · oa-sozlesme — ifa senaryo testi yok.**
Sözleşme "bekleyen dava" gibi okunuyor — inceleme modunda doğru, tahrirde eksik. İşlem avukatı üç senaryoyu yazar: normal ifa, gecikme, fesih; her kloz üçünde çalışıyor mu? `delil_sozlesmesi` ve `bildirim_tebligat` kategorileri var; senaryo testi yok. *Kanıt:* `oa-sozlesme/SKILL.md` TAHRİR 1-6; `sozlesme_denetim.py:33` ZORUNLU_KATEGORILER.

**A-24 · oa-kontrol — uzunluk ve ilk sayfa testi yok.**
Türk hâkimi 36 KB'lık 11 bölümlü dilekçeyi okumaz. "Dilekçeyi on dakikada okuyan hâkim tezi anlıyor mu, talep bloğu tek başına yeterli mi" kontrol listesinde yok. *Kanıt:* `oa-kontrol/SKILL.md` B ve C2 listeleri; SAHA-SONUCU çıktı 36 KB / 11 bölüm.

### Ceza dalı

**A-25 · oa-mudafii — strateji beraat odaklı; müzakereli çıkışlar zayıf.**
Çoğu dosyada müvekkilin en avantajlı sonucu beraat değildir: uzlaştırma, etkin pişmanlık, seri muhakeme, basit yargılama, erteleme, HAGB. **Susma/beyan zamanlaması** — ifadeyi ne zaman, ne kadar vermek — savunma stratejisinin en kritik kararı olarak protokolsüz. *Kanıt:* `oa-mudafii` altında uzlaştırma 2, etkin pişmanlık 2, susma 3, erteleme 1, seri muhakeme 0, basit yargılama 0.

**A-26 · oa-musteki-vekili — ceza↔hukuk köprüsü yok.**
Müşteki vekilinin asıl stratejik sorusu "ceza yolu ne için?" Ceza dosyası çoğu kez hukuk davasının delil fabrikasıdır: bekletici mesele, kesinleşen ceza hükmünün hukuk hâkimini bağlaması (TBK m.74 — çıpa), tazminat zamanaşımına etkisi. Uzlaştırma masasında müştekinin pazarlık pozisyonu ve şikâyetten vazgeçmenin fiyatı da yok. *Kanıt:* `oa-musteki-vekili` altında m.74, bekletici, uzlaştırma, tazminat, şikâyetten vazgeçme — tümü 0.

### Öğrenme

**A-27 · oa-usta — hata tetikli damıtma yok.**
Damıtma iş tipi tetikli (üç tekrar). Kıdemli avukatın öğrenmesi hata tetiklidir: sistemin en değerli kural seti (yedi kural) tek bir avukat revizesinin diff'inden çıktı — bu tesadüf değil yöntem olmalı. *Kanıt:* `oa-usta/SKILL.md` "Ne zaman damıtmaya değer"; `oa-dilekce` yedi kuralın kaynağı (147↔147 paragraf karşılaştırması).

**A-28 · sistem geneli — avukat hükmü sensörü uygulanmamış.**
SICRAMA-NOTU (A) bileşeni: teslim sonrası KABUL / REVİZYONLA / RET + kapalı sebep listesi. Enjeksiyon yapmaz, ölçer; bugün ret gerekçeleri hiçbir artefakta yazılmıyor ve `oa-usta`'ya ulaşmıyor. Panelin kendi şartı geçerli: refleks "kabul" başlarsa alan silinmeyi hak eder. *Kanıt:* SICRAMA-NOTU §5; depo genelinde uygulama izi 0.

---

## 5. Bulgular — B: mühendislik ve yönetişim

**B-1 · oa-ingest — OCR dil paketi yokluğu evrak özelliği gibi raporlanıyor.** ⚠ P0
`oa_ingest.py:531-534` tesseract alt sürecinin `returncode` ve `stderr`'ini okumuyor; "Error opening data file …/tur.traineddata" hatası boş OCR sayılıyor → DPI/PSM yeniden denemeleri boşa dönüyor → her taranmış sayfa **"OCR-BOŞ → GÖRSEL İNCELEME GEREK"** damgası alıyor. Ortam hatası, evrak özelliği gibi raporlanır; avukat 34 TIFF'i elle inceler. "Sessiz atlama yok" ilkesinin ihlali. CI'ın `ocr` işi `tur` kurduğu için bunu yakalayamaz. Test skip koşulu yalnız ikili varlığını sınıyor (`TESSERACT_YOK = shutil.which(...)`), dil paketini değil. *Kanıt:* bu ortamda `tesseract --list-langs` = eng, osd; `test_saglikli_taranan_pdf_gorsel_uretilmez` ve `test_karisik_evrakta_yalniz_bos_sayfa_gorsele_girer_saglikli_sayfa_girmez` kırmızı; künye `ocr_bos_evrak: 1`.

**B-2 · oa-pipeline — monolit ve hook gecikmesi.**
`pipeline_kayit.py` 5.562 satır / 159 fonksiyon tek dosya; altı hook olayının her biri bu modülü import eder: boş dizinde 390–475 ms. 271 araç çağrılı bir koşuda ~2 dk; kabul edilebilir ama tek-yazar, AI-yazımı bir monolitte bakım riski yüksek. *Kanıt:* `wc -l`; ölçüm §1/3.

**B-3 · yönetişim belgeleri bayat.**
`STATUS.md` başlığı 0.5.11 (2026-08-26); `YOL-HARITASI.md` DURUM bloğu v0.5.8.4 ve ⬜ işaretli adli tatil istisnası kodda var; paket 0.5.15. "Beyan değil ölçüm" diyen sistemin durum dosyası kendi ilkesini ihlal ediyor. `OA-SUIT-SAYISI` işaretçisi modeli STATUS sürüm satırına da uygulanabilir. *Kanıt:* dosya başlıkları; `hesapla_sure.py:831 --adli-tatil-istisna`.

**B-4 · git geçmişinde dosya kimliği (public depo).**
STATUS §6c'nin kendi tespiti: tepe temizlendi, geçmiş commit'ler duruyor. Av.K. m.36 yönünden geçmiş commit de ifşadır. `filter-repo` maliyeti (SHA/etiket kırılması) sıfır fork/klon sayısında düşüktür. *Kanıt:* STATUS.md §6c "Açık kalan — kullanıcı kararı".

**B-5 · `_oa/` düz metin.**
OCR'lanmış TCKN/sağlık verisi dizüstünde şifresiz. Layer 0 dışa çıkışı korur, cihazı korumaz. YOL-HARITASI P2 ⬜ olarak duruyor; A-11 ile birleşince risk büyür. *Kanıt:* YOL-HARITASI §3 ilk madde.

**B-6 · teslim hattı tek tedarikçiye bağlı; iş sürekliliği planı yok.**
`udf-cli@latest` 33 yerde pinsiz (A5, ertelendi). Fail-closed doğru; servis düştüğünde avukatın ne yapacağı yazılı değil (`udf_html2pdf.py` mevcut, UYAP editörüne yapıştırma yolu belgelenmemiş). *Kanıt:* STATUS §3 A5; `oa-dilekce/scripts/udf_html2pdf.py`.

**B-7 · kök README vitrin tonu.**
"dünyadaki en güçlü modelde en ucuz token…" türü cümleler ölçüm diline aykırı; 149 dava / 9 belgeli koşu ayrımı doğru yapılmış, cümle kalitesi değil. *Kanıt:* `README.md` satır 29-32.

**B-8 · test skip koşulu ile üretim varsayımı ayrışıyor.**
B-1'in test tarafı: `TESSERACT_YOK` ikiliyi sınar, `--dil tur` varsayılanı dil paketini gerektirir. Aynı sınıf arıza (§6c "sabit yol → sessiz atlama") başka biçimde. *Kanıt:* `test_oa_ingest_ocr_nobetci.py:78`; `oa_ingest.py:1189`.

---

## 6. Öneriler — öncelikli

Anayasa uyumu: A-13 ve B-1 dışında hiçbir öneri yeni bloklayıcı kapı eklemez; eklenen her kalem ya **görünürlük** ya **tek satırlık soru** ya **model brifi**dir (HEYET-KARARLARI-v0513 "Değişmeyen ilkeler" ile aynı disiplin). Norm atıfları çıpadır; uygulama anında Mevzuat MCP'den teyit edilir.

### P0 — hak kaybı / yanlış yeşil

| # | Öneri | Parça | Ne değişir | Bitti ölçütü |
|---|---|---|---|---|
| P0-1 | **İspat ontolojisi düzeltmesi** (A-13) | `oa-vakia` + `vakia_matris.py` | `iddialar[].tur ∈ {vakia, hukuki}`; hukuki iddiada delil aranmaz, `bilirkisi` tam ispat sayılmaz. `tanik` için `caizlik ∈ {caiz, sinirli, caiz_degil, bilinmiyor}` alanı; `bilinmiyor` → `kismi_destek`. `karine` → `yuk_kaydirir` ayrı sınıf. Eski JSON'lar alan yoksa `bilinmiyor` sayılır (fail-closed, kırılma yok). | Kapalı beyaz liste testi + `ispat_bosluklari`'na düşen tanık-tek-delil vakası testi |
| P0-2 | **OCR dil paketi teşhisi** (B-1, B-8) | `oa_ingest.py`, `test_oa_ingest_ocr_nobetci.py` | `returncode≠0` veya "Error opening data file" → sayfa "OCR-BOŞ" değil, evrak **"OCR YAPILAMADI — dil paketi yok"** ayrı damga; künyeye `ocr_arac_hatasi` sayacı; retry zinciri çalışmaz. Test skip: `--list-langs` içinde `tur` yoksa gerekçeli atlama. | Bu ortamda 2 kırmızı → 2 gerekçeli atlama; `tur` kurulu ortamda yeşil |
| P0-3 | **Hat sırası: ANTİTEZ erken** (A-2) | `oa-pipeline` | Sabit hatta 6↔7 yer değiştirir ya da antitez ikiye bölünür: 5b "erken antitez (cephe gücü)" → 6 STRATEJİ → 8b "geç antitez (sağlamlık)". Önkoşul-artefakt kapısı buna göre güncellenir. | `pipeline_kayit` adım tablosu ve `DURUM.md` şablonu yeni sırayı yansıtır; testler yeşil |
| P0-4 | **Netice-i talep playbook'u** (A-22) | `oa-dilekce` (+ `dilekce_denetim.py` advisory [L]) | Talep bloğu unsur listesi: asıl/fer'i diziliş · meşru terdit vs kendini yenen terdit · faiz türü + başlangıç · saklı tutulan haklar · gider + vekâlet ücreti · tedbir talebi. Kısmi dava kalıbı m.109/4 rejimiyle (MCP-teyitli, Ek-3). [L]: talep bloğunda para varsa faiz türü ve tarihi var mı — bloklamaz, gösterir. | Playbook metni + [L] kapısı testi; harç/zamanaşımı etkisi `oa-strateji`'ye çapraz atıf |

### P1 — müvekkil parası ve kararı

| # | Öneri | Parça | Ne değişir |
|---|---|---|---|
| P1-1 | Koruma tedbiri 0. adımı (A-19) | `oa-strateji`, `oa-sure` | Karar protokolüne "dava öncesi ihtiyati haciz/tedbir gerekli mi" sorusu; teminat ve süre kalemleri süre nöbetine kural olarak girer |
| P1-2 | Zaman ekseni + risk toleransı (A-16, A-17, A-6) | `oa-interview`, `oa-strateji` | Alımda iki soru (masraf gücü, risk toleransı); stratejide her alternatif için nitel süre bandı ve "bugün X vs N yıl sonra Y" karşılaştırması; sayı üretilmez, bant üretilir |
| P1-3 | Aşama tetikli süre sınıfı (A-10) | `oa-sure`, `sure_nobetci.py` | `tur: asama` kural tipi ("cevapla birlikte", "tahkikat sonuna kadar"); pipeline adımına bağlı uyarı; ceza katılma anı deseni hukuk koluna genellenir |
| P1-4 | Yarışan norm (A-15) | `oa-kiyas` | İddia başına `buyuk_onerme[]` (birden çok); her biri için zamanaşımı/kusur/ispat/faiz sütunu; seçim gerekçesi zorunlu alan |
| P1-5 | Bilirkişi cephesi + hâkim lensi (A-20, A-21) | `oa-antitez`, `oa-kontrol` | STANDART_CEPHELER'e `bilirkisi_teknik` (9.); içerik hakemi brifine ikinci pas: "bu dosyayı on dakikada okuyan hâkim" |
| P1-6 | Müzakereli çıkışlar + beyan protokolü (A-25) | `oa-mudafii` | Savunma akışına "en avantajlı sonuç haritası" adımı (beraat / uzlaştırma / etkin pişmanlık / seri-basit yargılama / erteleme / HAGB — kapsam MCP teyitli); susma-beyan zamanlaması karar protokolü |
| P1-7 | Ceza↔hukuk köprüsü (A-26) | `oa-musteki-vekili` | "Ceza yolu ne için" sorusu; bekletici mesele/bağlayıcılık/tazminat zamanaşımı ekseni; uzlaştırma pozisyonu |
| P1-8 | Senkron klasör uyarısı (A-11, B-5) | `oa-gizlilik`, `oa_hafiza.py init` | Çalışma kökü yolu bulut senkron desenine uyuyorsa (OneDrive/Google Drive/Dropbox/iCloud) init anında görünür uyarı + `DURUM.md` satırı; `_oa/` için şifreli konteyner önerisi P2'den P1'e |
| P1-9 | Müvekkil onayı düğümü (A-3) | `oa-pipeline` | `DURUM.md`'de "müvekkil kararı bekleyen" bölümü (sulh, dava değeri, risk kabulü, teminat); KAPANIŞ'ta müvekkil bilgilendirme notu taslağı |
| P1-10 | Kritik evrak → süre tetiği (A-4) | `oa-ingest`, `okuma_kapisi.py` | Manifestte tebligat/ara karar/bilirkişi türü evrak için "süre adayı" işareti; tarih çıkarımı advisory, `sure-flag` yazımı avukat onayıyla |
| P1-11 | Deterministik maliyet cetveli (A-18) | `oa-strateji` (yeni script) | Yıl damgalı tarife JSON (harç + AAÜT), kısmi kabul/red senaryosu; bayat tarife → fail-closed |

### P2 — sistem sağlığı ve olgunlaşma

| # | Öneri | Bulgu |
|---|---|---|
| P2-1 | Dosya ağırlığı triyajı: "derinlik kısılmaz, kapsam orantılanır" — anayasa m.1'e tek cümle ek; basit/orta/ağır sınıfı ALIM'da avukat onayıyla | A-1 |
| P2-2 | Forum seçimi refleksi (`oa-alan` konumlama adımı) | A-7 |
| P2-3 | Usul zamanlama kararı: tamamlanabilir/tamamlanamaz kusur ayrımı + "şimdi mi, sonra mı" avukat kararı; usul kazanımının gecikme maliyeti strateji tablosunda | A-8, A-9 |
| P2-4 | `menfaat_akisi` kenar tipi (`oa-illiyet`) | A-12 |
| P2-5 | İçtihat haritası adımı (yerleşik/azınlık/ayrışma/HGK) triajdan önce | A-14 |
| P2-6 | İfa senaryo testi (normal/gecikme/fesih) tahrir modunda | A-23 |
| P2-7 | İlk sayfa + uzunluk testi (`oa-kontrol` B listesi) | A-24 |
| P2-8 | Avukat hükmü sensörü + revize-diff damıtma ritüeli | A-27, A-28 |
| P2-9 | `pipeline_kayit.py` bölme (hook kanalları / defter / DURUM renderer) | B-2 |
| P2-10 | STATUS/YOL-HARITASI sürüm işaretçisi testi | B-3 |
| P2-11 | `git filter-repo` kararı ve uygulaması | B-4 |
| P2-12 | udf-cli düşme senaryosu belgesi + pin kararı | B-6 |
| P2-13 | README vitrin cümlelerinin ölçüm diline çekilmesi | B-7 |

---

## 7. Uygulama notları

- **Anayasa m.1 ile A-1 gerilimi** bilinçli bırakıldı: triyaj derinlikten kesmek değildir; hangi parçanın koşacağını değil, kapsamın müvekkil hedefine orantılanmasını belirler. Metne tek cümle yeter; motorlara dokunmaz.
- **A-13 fail-closed yönü koruyor**: bilinmeyen caizlik → kısmi destek; hiçbir eski dosya kırılmaz, yalnız bugüne kadar yeşil görünen bazı matrisler kırmızıya döner — bu istenen etkidir.
- **Zamanlama kararları (A-8) modelin değil avukatın**: sistem tamamlanabilir kusuru işaretler ve "şimdi/sonra" sorusunu `DURUM.md`'ye koyar; kendi başına geciktirmez.
- **Sayı üretme yasağı korunur**: zaman ekseni ve maliyet cetveli bant ve tarife üretir, olasılık üretmez.
- **Yeni skill yok**: 20 parça manifest kapısı korunur; tüm öneriler mevcut parçaların gövdesine, şemasına veya scriptine ekleme.

---

## Ek-1 · Test koşusu

```
Ortam: Linux · Python 3.12.3 · pymupdf, pillow, pytest kurulu
tesseract 5 mevcut · diller: eng, osd (tur YOK) · npx/udf-cli oturumu YOK
Komut: python3 -m pytest tests -q -rs -p no:cacheprovider
Sonuç: 2 failed, 1749 passed, 12 skipped in 203.47s
Kırmızı:
  tests/test_oa_ingest_ocr_nobetci.py::test_saglikli_taranan_pdf_gorsel_uretilmez
    → assert kunye["ocr_bos_evrak"] == 0  (1 == 0)
  tests/test_oa_ingest_ocr_nobetci.py::test_karisik_evrakta_yalniz_bos_sayfa_gorsele_girer_saglikli_sayfa_girmez
    → assert kayit["ocr_bos_sayfalar"] == [1]  ([1, 2])
Atlama: udf-cli oturumu (gerekçeli), saha referansı tanımsız (gerekçeli)
aile_dogrula: "Denetlenen parça: 20 — AİLE YAPI DENETİMİ TEMİZ."
Hook gecikmesi (boş dizin, echo '{}' | pipeline_kayit.py --hook-*):
  acilis 449 ms · prompt 430 ms · pretool 391 ms · postwrite 391 ms · denetle 475 ms
```

## Ek-2 · Kapsam taraması (aile genelinde geçiş sayısı)

| Kavram | Sayı | Bulgu |
|---|---|---|
| senetle ispat / HMK m.200 | 0 | A-13 |
| HMK m.145 (sonradan delil) | 0 | A-10 |
| kısmi dava / m.109 / belirsiz alacak | 0 | A-22 |
| faiz / temerrüt (3095, avans, yasal) | 1 | A-22 |
| AAÜT / karşı vekâlet | 2 | A-18 |
| ihtiyati haciz / tedbir (strateji dışı) | 4 dosya, strateji 0 | A-19 |
| netice-i talep · terditli · fazlaya ilişkin · yargılama gideri (`oa-dilekce`) | 2 · 1 · 0 · 0 | A-22 |
| yargılama süresi · zaman değeri · enflasyon · risk tolerans (`oa-strateji`) | 0 · 0 · 0 · 0 | A-16, A-17 |
| bilirkişi · uzman görüşü · hâkim (`oa-antitez`) | 1 · 0 · 1 | A-20, A-21 |
| yarışan · alternatif norm (`oa-kiyas`) | 0 · 0 | A-15 |
| uzlaştırma · etkin pişmanlık · susma · seri muhakeme · basit yargılama (`oa-mudafii`) | 2 · 2 · 3 · 0 · 0 | A-25 |
| TBK m.74 · bekletici · uzlaştırma · tazminat · şikâyetten vazgeçme (`oa-musteki-vekili`) | 0 · 0 · 0 · 0 · 0 | A-26 |
| OneDrive · Dropbox · senkron (`oa-gizlilik`) | 0 · 0 · 0 | A-11 |
| forum · birden fazla yetkili (`oa-alan`) | 0 · 0 | A-7 |

## Ek-3 · MCP teyitleri (Mevzuat MCP, 2026-09-06)

**HMK m.107 — Belirsiz alacak davası:** `MADDE 107– (Mülga:16/7/2026-7589/19 md.)`

**HMK m.109 — Kısmi dava:** f.1 ve f.3 yürürlükte; f.2 (Mülga: 1/4/2015-6644/4); **f.4 (Ek:16/7/2026-7589/20 md.):** alacağın bir kısmının dava edildiği hâllerde talep konusu, aynı davada bir defaya mahsus olmak üzere iddianın genişletilmesi yasağına tabi olmaksızın tahkikatın sona ermesine kadar artırılabilir; zamanaşımı artırılan kısım bakımından da dava tarihinden itibaren kesilmiş sayılır.

Kaynak: `mevzuat.gov.tr` MevzuatNo=6100, MCP `mevzuat_getir(id_type=madde)`. Derdest davalar için geçici hüküm okunmadı — uygulama anında teyit gerekir.

## Ek-4 · Bu rapordaki norm atıflarının statüsü

| Statü | Atıflar |
|---|---|
| **MCP-teyitli (bu denetimde)** | HMK m.107, m.109 |
| **Çıpa — uygulama anında teyit** | Av.K. m.34, m.36; HMK m.6 vd., m.145, m.200-203, m.266, m.293, m.389 vd., m.397; İİK m.257, m.264; TBK m.74; CMK uzlaştırma/seri/basit yargılama hükümleri |
| **Depodan devralınan (deponun kendi teyidiyle)** | CMK m.331/4, m.268, m.273/1; İYUK m.27; 7201 m.7/a; VUK m.107/A |

---

*Bu rapor karar materyalidir. Nihai karar Av. Bayram Can Çapar'a aittir.*

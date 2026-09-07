# GELİŞİM DEFTERİ (CHANGELOG)

Bu depo "gerçek testlerle optimum" yöntemiyle gelişir: **gerçek derdest dava
koşusu → karne → karnede ölçülen kusurun onarımı → yeni sürüm.** Bu defter,
sürüm zincirinin kök özetidir. Üç kademe birbirini tamamlar:

- **Bu dosya** — sürüm başına tek kayıt (ne, neden, hangi saha kanıtıyla).
- **Parça günlükleri** — her skill'in kendi `references/degisiklik-gunlugu.md`
  dosyası (dosya/fonksiyon düzeyinde ayrıntı).
- **Karneler ve Release'ler** — saha koşularının adli analizi
  ([KARNE-307.md](KARNE-307.md), [KARNE-1865.md](KARNE-1865.md),
  [SAHA-SONUCU.md](SAHA-SONUCU.md)) ve GitHub Release notları.

Kural: **CI yeşermeden sürüm etiketi atılamaz**; sürüm damgaları (plugin,
marketplace, iki script) daima birlikte artar. Dosya kimlikleri anayasa m.7
gereği yalnız saha etiketiyle anılır.

---

## v0.5.16 — İki Denetimin İnfazı (2026-09-07)
**Kanıt türü:** iki bağımsız dış denetim raporu (6 Eylül 2026): (1) *bütünleşik
analiz* — döngü/graf/hook mimarisi + üç dalda saha sınaması + Yargıtay→BAM→ilk
derece dikey inişi; **22 bulgu** (K1–K5 kesişim, G1–G12 graf, H/P hook-pipeline,
D1–D4 kaynak) ve **12 hamle**; (2) *dış denetim* — 20 parçanın hukuki metodolojisi
ve müvekkil menfaati; **A-1..A-28 + B-1..B-8**, P0/P1/P2 reçetesi. Kaynak belgeler
`_gorus/denetim-2026-09-06-*.md`; her grubun Yargı Pro/Mevzuat teyit izleri
`_gorus/denetim-v0516-yargipro-teyit-<grup>.md` (49 MCP çağrısı, ~45 (kanun, madde)
çifti; kritik 0, küçük 10 — onarıldı). Saha "önce" ölçümü (11 gerçek dosya kopyası,
anonim kod) `oa-v0516-calisma/saha-once/`; **"sonra" ölçümü bu sürümde YAPILMADI**
(açık iş — STATUS §0).

**Yöntem:** reçete 15 sahiplik grubuna bölündü; her grup kendi git dalında
(`v0516/<grup>`) uygula → adversarial hakem → onarım → Yargı Pro hakem/onarım;
her norm Mevzuat/Yargı Pro MCP'den madde metniyle teyit (m.4), fikstürler
sentetik (m.7), önce-kırmızı TDD. Ana ajan hiçbir grubun dosyasına dokunmadı;
birleştirme tek entegratörde (`--no-ff`, sırayla A B C1 C2 D E F G H I1..I6;
çakışma yalnız `tests/README.md` OA-SUIT-SAYISI satırında — E/H/I3/I6, nihai
sayı `pytest --collect-only` ile tek seferde yazıldı; `tests/test_v0514_muhakeme.py`
F+I2 otomatik birleşti, iki beklenti de duruyor).

**Grup → parça:** **A** → oa-illiyet; **B** → oa-pipeline; **C1** → oa-dilekce; **C2** → oa-kontrol; **D** → oa-gizlilik, oa-pipeline; **E** → oa-ingest, oa-pipeline; **F** → oa-vakia; **G** → oa-usta; **H** → oa-ictihat; **I1** → oa-interview, oa-strateji; **I2** → oa-antitez; **I3** → oa-mudafii, oa-musteki-vekili; **I4** → oa-alan, oa-kiyas, oa-usul; **I5** → oa-sure; **I6** → oa-sozlesme.

**Kapanan bulgular (ölçüm: grup raporlarındaki `changelog_notu` metinlerinde anılan
kodlar):**

| Bulgu | Grup(lar) |
|---|---|
| A-1 | A, I5 |
| A-2 | B |
| A-3 | B |
| A-4 | E |
| A-5 | I1 |
| A-6 | I1 |
| A-7 | I4 |
| A-8 | I1, I4 |
| A-9 | I1 |
| A-10 | I5 |
| A-11 | D |
| A-13 | F |
| A-14 | H |
| A-15 | I4 |
| A-16 | I1 |
| A-17 | I1 |
| A-18 | I1 |
| A-19 | I1 |
| A-20 | I2 |
| A-21 | C2, I2 |
| A-22 | C1 |
| A-23 | I6 |
| A-24 | C2 |
| A-25 | I3 |
| A-26 | I3 |
| A-27 | G |
| A-28 | B, G |
| B-1 | B, E |
| B-2 | B, C2 |
| B-3 | G |
| B-5 | D |
| B-6 | C1 |
| B-8 | E |
| D1 | H |
| D2 | H |
| D3 | H |
| G1 | A |
| G2 | A, C2 |
| G3 | A |
| G4 | A |
| G5 | A, C2, D |
| G6 | A |
| G7 | A |
| G8 | A |
| G9 | A |
| G10 | A |
| G11 | C2 |
| G12 | A |
| H1 | B |
| H2 | C1 |
| K1 | B, G, I4 |
| K2 | A, B |
| K3 | C1 |
| K4 | C2 |
| K5 | C2, D |
| P0-1 | F |
| P0-2 | E |
| P0-3 | B, I2 |
| P0-4 | C1 |
| P0-9 | E |
| P1-1 | I1 |
| P1-2 | I1 |
| P1-3 | I5 |
| P1-4 | I4 |
| P1-5 | C2, I2 |
| P1-6 | I3 |
| P1-7 | I3 |
| P1-8 | D |
| P1-9 | B |
| P1-10 | E |
| P1-11 | I1 |
| P2-2 | I4 |
| P2-3 | I1, I4 |
| P2-5 | H |
| P2-6 | I6 |
| P2-7 | C2 |
| P2-8 | G |
| P2-10 | G |
| P2-12 | C1 |

Tabloda görünmeyen kodlar ya hazırlık commit'inde (fcae8d8: A-1/P2-1 anayasa m.1
triyaj, B-7/P2-13 README ölçüm dili) kapanmıştır ya da bir grubun notunda kod
adıyla anılmadan uygulanmıştır — parça günlükleri (`references/degisiklik-gunlugu.md`,
"v0.5.16" bölümü) ayrıntıyı taşır. Kapanan ana başlıklar: graf kapısı SERT + exit
sözleşmesi + bağlanmamış delil/köprü/güç sınıfları + dal-ayrımlı `kesme_flag` +
taraf yönü + karar/mahkeme tipi (A); bekçi DAMGAYA bağlandı (K1), graf kapısı (K2),
`--serh-kapi`, inline sayaç (M7), ANTİTEZ↔STRATEJİ sırası (P0-3), müvekkil kararı
düğümü (P1-9), avukat hükmü sensörü (A-28) (B); [F] hafif kip + [P] netice-i talep
+ [N] beyaz liste + udf-cli kesinti planı (C1); tarih-only/K-only atıf → EKSİK KÜNYE
BLOK, [G5-AKIBET], örtüşme sayacı, hâkim lensi (C2); `teyit --akibet` + senkron
klasör uyarısı (D); OCR araç-hatası teşhisi + süre adayı (E); ispat ontolojisi —
tanık caizliği, hukuki iddia, karine yük kaydırır (F); aile_dogrula yapısal kilitler
+ sürüm işaretçisi (G); `kanun_yolu_zinciri.py` + iniş ritüeli + içtihat haritası (H);
koruma tedbiri, zaman ekseni, risk toleransı, maliyet cetveli — fail-closed tarife (I1);
bilirkişi/teknik cephesi (dokuz cephe) + hâkim lensi (I2); müzakereli çıkışlar +
beyan protokolü, ceza↔hukuk köprüsü (I3); merci tayini, usul zamanlama, forum
seçimi, yarışan norm (I4); aşama tetikli süre sınıfı (I5); ifa senaryo testi (I6).

**Entegrasyon hizalamaları (birleşim sonrası, H1–H5 — `tests/test_v0516_entegrasyon.py`,
18 test):** H1 `oa_hafiza.py sure-flag --asama <ad> --pipeline-adimi N` (tarihsiz
`tur: asama` kaydı; `sure_nobetci` ile uçtan uca) · H2 eski «6 STRATEJİ / 7 ANTİTEZ»
sırası ortak-avukat/oa-mudafii/oa-musteki-vekili SKILL'lerinde düzeltildi; çalışma-
evrakı önekleri `06-antitez*`/`07-strateji*` (oa-antitez/oa-dilekce/oa-usul/oa-kiyas
şablonu, `oa_metrik.py`, `dilekce_denetim.py`, `ictihat_muhakeme_denetim.py`; eski
adlar geriye uyumla kabul) · H3 OA-SUIT-SAYISI tek seferde · H4 AKIBET yazar↔okur
uçtan uca (LEHE+bozuldu+atıf → BLOK) · H5 `*vakia*.json` bekçisi damgaya çekildi;
aile_dogrula KİLİT-A damga sözleşmesini (bekçi damgası ↔ üretici script) dört bekçide
denetler — gerçek depoda TEMİZ, kör kilit yok. «Sekiz cephe» kalıntıları «dokuz cephe».

**Sürüm damgaları:** plugin.json · marketplace.json · iki README · `pipeline_kayit.py`
ve `teslim_paketi.py` OA_SURUM → 0.5.16 (birlikte). `tests/README.md`
OA-SUIT-SAYISI = **2301** (`pytest --collect-only`). Tam süit sonucu STATUS §0'da.

**Yapılamayanlar / açık kalanlar (sessiz atlama yasağı):**
- Saha "SONRA" ölçümü (aynı 11 kopya, v0.5.16 araçları) ve önce/sonra tablosu — yapılmadı.
- `git push` — yapılmadı (kimlik engeli; `gh auth login -h github.com` sonrası kullanıcı).
- Avukat kararı bekleyen: B-4 `git filter-repo` (geçmişte dosya kimliği) · udf-cli pin
  (A5/B-6) · `maliyet_cetveli` tarife.json değerleri (AAÜT 2026 ek tabloları MCP'den
  alınamadı; nispi harç asgari haddi kaynak çelişkisi «çıpa» etiketli).
- MCP'den teyit edilemeyip «çıpa / teyit edilmedi» etiketiyle bırakılanlar: 7589 s.K. RG
  sayısı (C1); dava dilekçesi-temerrüt/faiz içtihadı ve HMK m.392 vd. (C1); HAGB «sanığın
  kabulü» AYM/7499 geçiş rejimi (I3); TBK m.74 içtihadı yalnız künye düzeyinde, TCK m.52 /
  CMK m.153 / TCK m.267 (I3); 492 s.K. m.30-32, HMK m.17-18/114/116-117/390 ve İİK tedbir
  çıpaları (I4); TBB Meslek Kuralları bilgilendirme hükmü (B-2); `ceza:hukuka_uygunluk`
  TCK m.24 vd. ve 12. CD künyesi (A-2).
- Devirler: `pipeline_kayit.py`'nin `senaryo_bosluklari` (I6 --json) okuması; `md_yaz`
  araç-hatası önerisinde dil adı sabiti (E); G11 parantez sayacının «m.353/(1)» sayması
  (C2, advisory); Linux'ta tur paketi yokken OCR yolu yalnız sahte ikiliyle sınandı (E).
- Belge bayatlık taraması (DEVAM-PLANI §9) bu sürümde H2 kalemi + sürüm/tarih damgaları
  ile SINIRLI yapıldı; satır satır tam tarama açık iş.
- **Belge bayatlık taraması — infaz (2026-09-07, ayrı commit):** 83 bulgu koda karşı
  doğrulandı, 82'si düzeltildi (1'i «bayatlık yok» bilgi notu). Sınıflar: script sayıları
  diskle eşitlendi (ingest 2 / kontrol 8 / ictihat 1 / strateji 1 / vakia 2); «sekiz cephe»
  → dokuz; 19 README damgası v3.20 → v3.26; «18 oa- parçası» → 19; eski MCP araç adları
  (`search_mevzuat*`, `search_cb*`, `search_anayasa_unified` birincil) → `mevzuat_ara` /
  `mevzuat_icinde_ara` / `mevzuat_getir` / `aym_ictihat_ara`; CLI enum/bayrak bayatlıkları
  (`--tip yemin|idari-kanal`, `--taraf` 6 değer, `--sebep` 7 değer, `--json` ZORUNLU
  kıyas, `sure-flag --asama`, `--muvekkil-karari`); DAMGA=NOTR G6'da BLOK; anayasa m.7
  kimlik soyutlamaları (yer adı + dosya no → «saha bulgusu»); Yönetmelik 2646 m.8 kenar
  notu (MCP teyit: üst/sol/sağ 1,5 cm — alt kenar maddede yok); 6 changelog'daki literal
  `
` yapıştırmaları gerçek satırlara açıldı ve yabancı parça blokları ayıklandı;
  KURULUM-SENKRON / TEST-KULLANIM «TARİHÎ» damgalandı; çekirdek günlüğündeki kesik satır
  (v3.14–v3.16 kayıp — git geçmişinde de yok) şerhlendi. Dokunulmayan: referans
  günlüklerindeki tarihî saha kimlikleri (ayrı karar), B-4 `git filter-repo`.

---

## v0.5.15 — UDF Yapılı Okuma (2026-08-31)
**Soru avukattan geldi:** *"ingest sistemimiz udf2md yapıyor muydu?"* Cevap:
yapıyordu ama **ham** — ZIP → CDATA → düz metin. Metin kaybolmuyordu, **yapı**
kayboluyordu. 798 gerçek evrakta ölçüldü: 739 tablo ızgarası · 424 iç içe tablo
· 548 görsel (20,8 MB mühür/imza — **delil**) · 32.593 alan etiketi · **7.316
veri düğümü** (düz metnin tamamen dışında; %100 kayıp) · 1.004 liste ögesi ·
1.487 altı çizili · 461 üst/alt bilgi. Bilirkişi hesap tablosunda tutar
kaleminden kopuyor, dilekçedeki "1., 2., 3." talep sırası düzleşiyordu.

**Çözüm — temiz oda.** Ticari bir üründe aynı işin çözümü olduğu görüldü;
avukat "yöntemlerinden faydalanalım" dedi. Sınır çizildi: **formatın kuralları
olgudur, öğrenilebilir; başkasının kodu ifadedir, kopyalanamaz.** Ajanın
referans olsun diye çıkardığı üçüncü taraf kaynakları karantinaya alındı;
üretim modülü yalnız avukatın kendi dosyalarındaki ölçümden ve kendi
sözlerimizle yazılmış şartnameden türedi. Açık kaynak taraması da kararı
destekledi: en yakın çözüm **lisanssız** bir depoda (= tüm hakları saklı).

**Ölçülen sonuç:** 796/798 dosya (eski hat 787) · görünür karakter kaybı
**0 / 6.403.940** — CDATA ham baytlardan **bağımsız** yeniden çıkarılarak
ölçüldü (modülün kendi beyanına güvenilmedi; ilk ölçümün **döngüsel** olduğu
sınavda yakalanmıştı) · tablo geometrisi **XML gerçeğine karşı 739/739** ·
regresyon 0 · salt-okuma ihlali 0/798 · ~4 ms/dosya · 75 yeni test.

**İki katmanlı invaryant (avukat kararı).** Önce "hiçbir karakter değişmeyecek"
dendi; ölçüm gösterdi ki katı okumada bu **796/796 dosyayı bloklar** ve yeni
hattı öldürür — çünkü hücre içi satır sonunun hücre ayracına dönüşmesi
tasarımın kendisidir. Avukat "kuralı esnet, önemli olan sonuca en yüksek
kesinlikle ulaşmak" dedi. Sonuç bir esneme değil, **doğru tanım** oldu:
**Katman 1 İÇERİK** katı, eşik 0 (bugün 0/6.403.940 ile tutuyor) ·
**Katman 2 KAP** tanımlı-esnek (belgeli, deterministik, sürüm damgalı).
*Katılık kaybolmadı, doğru katmana çekildi.*

**Kapıların huyu maliyet asimetrisinden:** üretim kapısı **işaretle-ve-taşı**
(bloklamak kayıplı hatta düşürür, değer kaybettirir; eksik karakterler
*kendileriyle* sapma kaydına yazılır — işaretlemek kaybetmek değildir);
bütünlük kapısı **blokla-ve-onar** (sha uyuşmazlığı güven iddiasını çökertir,
onarım ise 3,37 sn'de bedava).

**Künye artık makine-teyitli:** UYAP evrağın içinde mahkeme adını, dosya/karar
numarasını, tarafı **kendisi etiketliyor**; bugüne kadar bunları düz metinden
regex'le geri buluyorduk — hata payı bizimdi. Beyaz liste **dosya kapsamına**
göre seçildi (span sayısına göre değil: `makbuzBilgisi` 3.449 span taşır ama
yalnız 40 dosyada — o bir makbuz tablosudur). `kunye_kaynak: udf-alan`
provenansı, değerin tahmin değil kaynak beyanı olduğunu söyler.

**INDEX'e `Yapı` sütunu:** `T:n×m` · `V:n` · `G:n` · `İ` — yalnız ayırt edici
sinyal. İmzalayan personel sicili künyede kalır, **INDEX'e çıkmaz** (INDEX
dışa en çok sızan artefakttır).

**Determinizm:** aynı girdi + aynı sürüm → bayt-özdeş (hash-seed, ayrı süreç,
yol bağımsızlığı, CRLF testleriyle kilitli). `icerik_sha256` renderer'dan
**bağımsızdır** ve sürümler arası sabit kalmalıdır — değiştiği gün
"kayıpsızlık tanımımız değişti" demektir ve ayrıca gerekçe ister.

**Belge düzeltmesi:** `udf-ic-yapi.md` "ZIP içinde TEK content.xml" diyordu;
ölçüm 464 dosyada `documentproperties.xml` buldu (UYAP doğrulama kodu +
imzalayan sicili) — henüz okunmuyor, ayrı kalem olarak sırada.

**Sözleşme korundu:** `evrak_isle` 6'lı demeti bozulmadı; zenginlik 7. kanaldan
gider — PDF/OCR/DOCX hatlarına hiç dokunulmadı. Süit **1763** (1688'den).

## v0.5.14 — Denetimin İnfazı: 62 bulgu (2026-08-31)
**Kanıt türü:** iki bağımsız denetim turu. (1) Ertelenen dört tez kod üzerinde
planlandı ve planlar adversarial çürütmeden geçirildi; (2) eklentiyi **fiilen
çalıştıran** 5 hukukçu + scriptleri **fiilen koşturan** 4 mühendis avcı,
her biri ayrı bir şüpheci tarafından çürütülmeye tabi tutuldu. Toplam **62
bulgu** (A-1…A-22 hukuki, B-1…B-40 mühendislik). Hukuki iddiaların tamamı
Mevzuat MCP'den madde metniyle doğrulandı.

**Telafisiz üç hata düzeltildi:**
- **CMK m.331/4** — ceza kanun yolu sürelerine hukuk yargısının adli tatil
  rejimi (HMK m.104, bir hafta) uygulanıyordu; doğrusu **üç gündür**. Sistem
  dört gün geç tarih veriyordu; 4-7 Eylül'de verilen istinaf/temyiz süreden
  reddedilirdi. `--yargi ceza` kolu açıldı; kural↔kol uyuşmazlığı artık
  **hesabı durduruyor** (yanlış tarih deftere yazılamıyor).
- **CMK m.268** — referans dosyasında süre hâlâ "yedi gün"dü (v0.5.13'te
  SKILL.md düzeltilmiş, referans atlanmıştı: ikiz liste kayması).
- **IBAN deseni** — Layer 0'ın MUTLAK_DENY kuralı hane sayısı yanlış olduğu
  için **geçerli hiçbir Türk IBAN'ında ateşlemiyordu**.

**Halüsinasyon panzehirinin onarımı (P0):** künye kapısı yaygın künye
biçimlerini görmüyordu ve uydurma içtihatlı taslak uçtan uca "TESLİME HAZIR"
alabiliyordu; kaynakça üreteci ise kapının göremediği künye için dilekçeye
**gerçeğe aykırı "tam metniyle okundu" beyanı** yazıyordu. Kapı artık
ayrıştıramadığı atıfta **fail-closed**; teyitsiz künye varsa okundu beyanı
**hiç yazılmıyor**.

**Diğer P0'lar:** yürütmenin durdurulması (İYUK m.27) ailenin tamamında yoktu —
ödeme emrine karşı dava açmanın tahsilatı durdurmadığı hiçbir yerde yazılı
değildi; sunum kilidi dava klasörü dışında sessizce ölüydü; bayat-araç
nöbetçisi negatif parmak izine dayandığı için gerçekten bayat bir kiti
"kanaldan yeni" ilan ediyordu; mühürsüz-teslim taraması fail-open'dı;
`teslim_paketi` girdisini mutasyona uğratıyordu (aynı komut 1. koşuda yeşil,
2. koşuda kırmızı).

**Yapısal onarımlar:** kural tablosu artık **tek kaynak** (JSON) — gömülü
fallback ondan türetiliyor ve ayrışmayı bir test mekanik olarak yakalıyor
(bu tur entegratörün kendi kaymasını da yakaladı). Süit sayısı iddiası tek
işaretçiye indirildi. `unsur-sablonlari/` altına **amme ödeme emri** şablonu
eklendi (İİK ödeme emriyle karıştırma uyarısıyla). 21 süre kuralının
tamamı MCP teyit tarihli — teyitsiz kural **sıfır**.

**Entegratör hükmü (çatışma çözümü):** yeni sunum-kilidi uyarısı ile v0.5.9'un
"dava dışı klasörde sessiz kal" sözleşmesi çarpışıyordu. Ayrım: *diskte
olmayan bir yol için denetlenecek şey yoktur* (susmak gürültü disiplinidir);
uyarı yalnız **var olan** teslim ürününün kökü bulunamadığında çıkar.

Süit **1688** (v0.5.13'te 1406). Ayrıntı: [DENETIM-v0514.md](DENETIM-v0514.md).

## v0.5.13 — Heyet Kararlarının İnfazı (2026-08-27)
**Kanıt türü farklı:** bu sürüm bir saha karnesinden değil, **denetimden**
doğdu — 20 skill dört turdan geçti (7 mesleki denetçi + puanlama · 5 disiplinli
hukukçu hakem heyeti · 4 pratikçi avukatın tez/antitez düellosu · 3 yazılım
mühendisinin kod hükmü). Her hukuki iddia Mevzuat MCP'den madde metniyle
doğrulandı; ajan transkriptleri SHA-256 manifestli arşive mühürlendi.
**İki gerçek hata düzeltildi:** katılma anı (CMK m.237 — kanun yolunda
istenemez; ilk derecede hüküm verilinceye kadar) ve itiraz süresi (m.268:
"7 gün" → **iki hafta**, öğrenme gününden; JSON + gömülü fallback birlikte).
**Bir hakem tezi teyitte ÇÜRÜDÜ** ve bu da kayda geçti: "istinaf tefhimden
işler" iddiası m.273/1'in güncel metniyle yıkıldı (f.2, 7499 ile mülga) —
dosya doğruydu, değiştirilmedi. Ders: düzeltmenin kendisi de teyide tabidir.
**Yeni:** süre başlangıç türü çatalı (`--baslangic-turu`; belirsizde iki
senaryo + erken tarih) · "süre kaçtı" mutlak dilinin kırılması + kurtarma
kapıları kataloğu (yargı koluna göre; İYUK'ta eski hâle getirme YOK) ·
tutuklu dosya kipi · celse kartı + **dahili sızıntı kapısı** (iç analiz
belgesi dış çıktıya kopyalanamaz) · zorunlu arabuluculuk dava şartı dört
adreste · İİK m.67/68/72 + İYUK m.10/11 + VUK m.107/A çıpaları · mal kaçırma
kavşağı (iki tarih ekseni). Gerekçeli daraltmalar
[HEYET-KARARLARI-v0513.md](HEYET-KARARLARI-v0513.md)'de. Süit o gün **1406** toplandı (v0.5.14/B-35 düzeltmesi: kayıt 1405 yazıyordu, yeniden ölçüldü).

## v0.5.12 — İçtihat Kaynakçası (2026-08-27)
**Avukat kuralı:** dilekçeye giren her Yargıtay/Danıştay kararının **kaynak
linki** tüm çıktılarda görünsün. Taslağın sonuna idempotent kaynakça bloğu
üretildi; URL **yalnız** muhakeme kaydının teyitli satırından alınır —
uydurma yasak, linki olmayan künye görünür notla işaretlenir. UDF üretiminden
önce işlenir, makbuza kaydı düşer. Ayrıca 40-UYAP adının gerekçesi sözlüğe
(bant başı = giden evrak) ve tüm token ölçümleri repoya girdi. Süit 1394.

## v0.5.11 — Kit Güvenlik Katmanı (2026-08-26)
**Saha kanıtı:** 1865 (çok-oturumlu, müdahaleli-yetkili · [KARNE-1865.md](KARNE-1865.md)).
Kök düşman adlandırıldı: uygulamanın rpm anlık-görüntüsünden bulaşan bayat
araç nesli (777'den beri 3. nüks); tek seferlik onarımın yetmediği ölçüldü.
**Onarım:** rpm karantinası ('ask') · kilitli çekirdek (salt-okunur + 'ask') ·
yönlü tazelik (bayat / kanaldan-yeni / özdeş) · oturum damgası (defter+makbuz
`session_id`) · çok-oturum görünürlüğü · sözleşme-dışı dizin ve MANİFEST-önce
bekçileri. Süit 1385. Saha koşusu maliyeti: ~4,3M token (çok oturumlu).

## v0.5.10 — Kusursuz UDF Dönüşümü (2026-08-25)
**Saha kanıtı:** 307 (K1: ürün makbuzdan 68 dk sonra mühür dışında değişti;
K2: makbuz resmî ürünü kapsamıyordu · [KARNE-307.md](KARNE-307.md)) + 923
(çift-uzantı ve mühürsüz-kopya bağımsız tekrarı).
**Onarım:** atomik mühür (üretim=mühür, üç yolda) · filo-tazelik kapısı
(kök + 40-UYAP tüm teslim-sınıfı UDF'ler makbuza) · çift-uzantı kaynağında
öldü · kopyalar mühürleriyle gider · sunum kilidi makbuz-sonrası değişiklik
penceresini kapattı. Süit 1371. Saha maliyetleri: 307 ~822k · 923 ~360k token.

## v0.5.9 / v0.5.9.1 — Deterministik Tamamlayıcı Zincir (2026-08-22)
**Saha kanıtı:** 777 karnesi + 24-kök çapraz taraması + iki bağımsız hakem
turu (T1-T26 konsolide raporun yerli uygulaması). 777 koşusu ~1,50M token.
Sunum kilidi (makbuzsuz teslim-sınıfı gönderim → 'ask') · inline dilekçe
denetimi · zincir-durumu enjeksiyonu · 40-UYAP dış-çıktı şeması · vitrinin
avukat diliyle sıfırdan inşası. 0.5.9.1: kurulum damgası (sürüm-cache kuralı).

## v0.5.8.4 – v0.5.8.6 — Saha Karnelerinin İnfazı (2026-08-15 → 08-18)
**Saha kanıtı:** 372 (elle-UDF krizi; A/B testiyle hvl-default imzası bulundu),
346 (künye kapısı gerçek açık yakaladı; [G6] mutlak triyaj doğdu), 777 (bayat
kit kök nedeni).
0.5.8.4: elle-UDF engeli + makbuz garantisi (RED bile damgalı) + mühür
otomasyonu + şekil kapısı (4×42,52 pt). 0.5.8.5: [G6] mutlak triyaj (tam metin
okunmadan karar dilekçeye giremez; ALEYHE → iç cephanelik) + hook dirilişi +
e-imza halkası. 0.5.8.6: sürüm kilidi/parmak izi + VERSION.json + devralma
köprüleri. Koşu maliyetleri: 372 ~1,24M · 346 ~1,17M token.

## v0.5.7.x — Saha Donanımı (2026-08-07 → 08-08)
Bayat-tohum aşısı (komşu klasörden kopya yasağı — 754 bulgusu) · G4 bağlantı
kapısı · Yargı Pro birincil + otomatik yedek zincir · davadan gelen atıflar da
link zincirine tabi (kullanıcı kuralı) · CI stdout kirliliği onarımı.

## v0.5.6.1 — Hook Kaydı + Devir Zorlayıcı (2026-08-06)
Hook katmanının kayıt altyapısı; oturumlar arası devir disiplini; rehber
sadeleştirmesi ("ateşlemeyen kapı silinir" ilkesine ilk büyük uygulama).

## v0.5.5 – v0.5.5.5 — Aktivasyon Zinciri + Müdahalesiz Test Dersleri (2026-07-28 → 08-02)
**Saha kanıtı:** 214 evraklık bakir klasörde müdahalesiz test — "kapının gücü
kodunda değil tetiğindedir." Aktivasyon zinciri, OCR nöbetçisi, UDF hattının
resmî araca kilitlenmesi, geçerlilik kapısı, içerik hakemi; 0.5.5.5: cp1254
kodlama çökmesi onarımı (P0).

## v0.5.0 – v0.5.4 — Temel Atma (2026-07-19 → 07-20)
Temiz kurulum (tek kaynak: GitHub) · oa-ingest v1.5 paralel çıkarım · Okuma
Ekonomisi (Gate A-G) · İçtihat Muhakeme Zinciri (G1-G3) · working memory
(`dosya-analiz.md` doğum anı) · dilekçe playbook · anayasa dedup. İlk paket
57 testle çıktı; süitin GÜNCEL büyüklüğü tek kaynaktan okunur: [tests/README.md](tests/README.md) `OA-SUIT-SAYISI` işaretçisi.

---
*Daha eski tarih öncesi (v0.4.0 ve öncesi) tek-skill dönemidir; bugünkü
20-parça mimarisi v0.5.0 temiz kurulumuyla başlar.*

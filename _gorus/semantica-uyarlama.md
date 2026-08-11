# GÖRÜŞ — Semantica → Ortak-Avukat Uyarlama Analizi

**Tarih:** 2026-08-11 · **Mod:** salt-okuma + analiz (kod değişikliği YOK, push YOK)
**Karar verici:** Av. Bayram Can ÇAPAR — bu belge karar MATERYALİDİR, karar değildir. Uygulama ayrı oturumdur.
**Kaynak repo:** https://github.com/semantica-agi/semantica (klon: v0.6.0 etiketli, depth-50, salt-okuma)
**Hedef repo:** lokal çalışma kopyası `C:\Users\pc\.claude\plugins\marketplaces\ortak-avukat` (KANONİK)
**Lokal ↔ public sapma denetimi (doğrulandı):** `git fetch` sonrası iki yönde de fark yok, çalışma ağacı temiz → lokal = public (6e4ded6, v0.5.7.5). Analiz her iki snapshot için aynı anda geçerlidir.
**Bağımsızlık:** Claude.ai tarafındaki analiz bu oturuma verilmedi; görüş bağımsız kuruldu.

**Yöntem:** 8 paralel salt-okuma derin-eksen (semantica: genel/bağımlılık, graf+storage,
bi-temporal+provenance, conflict+reasoning, MCP+karar zekâsı; ortak-avukat: anayasa/doktrin,
hafıza+pipeline, deterministik motorlar; ~1,16M token okuma, 227 araç çağrısı) → sentez taslağı →
3 bağımsız çürütücü mercek (sahte-fayda/fırsat-maliyeti · KVKK/anayasa · ters-yön) → hakemlik → bu görüş.
Damgalar: **[doğrulandı]** = kaynakta bizzat görüldü (dosya/satır kanıtlı) · **[spekülasyon]** = çıkarım ·
**[yorum]** = yoruma dayalı okuma.

---

## ÖZET — tek paragraf

Semantica'dan **pip ile alınacak hiçbir şey yoktur; kopyalanacak kod da bugün itibarıyla yoktur.**
Bu bir başarısızlık değil, ölçülmüş bir **negatif sonuçtur**: semantica'nın vaat ettiği yeteneklerin
yapısal yarısı ortak-avukat'ta zaten mevcut (graf denetimi, kaynak izi, karar defteri), kalan yarısının
ihtiyacı ise gösterilemedi (bi-temporal, değer-çelişkisi kapısı, sqlite emsal kütüğü — üçü de antitez
turunda çöktü). Egzersizin kalıcı kazanımları: (1) kendi backlog'umuzun (P2 ortak kimlik uzayı, Fikir 8,
dört motorun test borcu) **bağımsız teyidi**, (2) karar uzayına **YOL-B′ (vendoring) seçeneğinin**
eklenmesi ve buna aile kuralı önerisi, (3) YOL-HARITASI'nın **bayat olduğunun** kanıtlanması (birçok ⬜
kutu kodda fiilen bitmiş), (4) üç küçük, ucuz, riski düşük iyileştirme adayı. Efor önceliği değişmez:
**K4 (gerçek dosyada uçtan uca prova + UDF gerçek UYAP testi).**

---

## 1. KAZANIM ENVANTERİ

### 1a. Sahte-fayda olarak AYIKLANANLAR (mevcut mekanizma zaten çözüyor)

| Aday | Neden sahte-fayda | Damga |
|---|---|---|
| **Kalıcı bağlam grafı** (ContextGraph) | `graf.json` zaten kalıcı JSON yönlü graf (dugumler/kenarlar/dayanak_delil). Semantica ContextGraph'ın kalıcılığı da yalnız JSON save/load — üstünlük yok. Kalıcı property-graph için semantica bile SUNUCU ister (varsayılan neo4j; gömülü backend yok). | doğrulandı |
| **Yapısal çelişki/kopukluk tespiti** | `grafik_denetim.py` yetim düğüm, desteksiz iddia kenarı, articulation-point (muvazaa/perde sinyali), yönlü çevrim (dairesel illiyet), bridge-edge (yük taşıyan kenar) denetimini ZATEN yapıyor. Semantica'nın yapısal katmanından alınacak yeni yetenek yok. | doğrulandı |
| **Kaynak izi (provenance)** | Atıf katmanında `kunye_teyit.py` + append-only kütük + ham MCP dökümü (`_oa/teyit/dokum/`) fiilî provenance eşdeğeri; evrak katmanında kaynak+sha+yöntem+⚠-OCR damgası. Semantica'nın PROV-O'su bile dahili olarak RDF değil (tek tablolu SQLite; PROV-O yalnız dışa aktarım). | doğrulandı |
| **Dava-içi karar kaydı** | Pipeline defteri (`avukat-karari` olayları, gerekçeli, append-only) zaten tutuyor. Boşluk yalnız davalar-ARASI katmanda (bkz. K7). | doğrulandı |
| **MCP üzerinden "semantik" emsal arama** | Semantica MCP'sinin find_precedents'ı embedding değil, Jaccard kelime kesişimi (context_graph.py 2594-2670). Vaat ile kod ayrışıyor — alınacak şey vaadin kendisi kadar bile yok. | doğrulandı |

### 1b. GERÇEK boşluklar (ortak-avukat'ta doğrulanmış; semantica'nın çözdüğü İDDİA edilen alanlar)

| # | Boşluk | Kanıt | Tek seferlik / bileşik |
|---|---|---|---|
| B1 | Aynı olgu için iki FARKLI DEĞER (çelişen tarih/tutar) girilince yakalayan denetçi yok — `capraz_denetim.py` yalnız referans bütünlüğü | capraz_denetim.py 178-237 tamamı okundu; değer karşılaştırma kodu yok | bileşik (ama bkz. §2-K3: ihtiyaç ölçülmedi) |
| B2 | vakıa↔delil↔graf bağı sabit ID değil, normalize ≥4 karakter alt-dize eşleşmesi | capraz_denetim.py `_norm/_eslesir` 62-81; YOL-HARITASI P2 satır 66 zaten planlamış | bileşik |
| B3 | Davalar-arası ders/emsal hafızası yalnız niyet düzeyinde (arsiv-yerel + oa-usta damıtma; Fikir 8 `ders_damit.py` yapılmamış; `dersler/` dizini SKILL.md'de var, kodda yok) | oa_hafiza.py DIZINLER satır 50 vs oa-pipeline/SKILL.md satır 97 | bileşik (kapanan her dosyanın dersi telafisiz kaybolur) |
| B4 | Defter satırı silinir/bozulursa sessizce düşer (dayanıklılık tercihi; tespit mekanizması yok) | oa_hafiza-pipeline eksen raporu | tek seferlik küçük sağlamlaştırma |
| B5 | DÖRT deterministik motor (grafik_denetim, vakia_matris, kiyas_denetim, usul_matris) tests/ altında SIFIR referanslı; kiyas_denetim kritik boşlukta bile exit 0 | grep boş; kiyas_denetim.py main() 133-153'te sys.exit yok | tek seferlik (bakım borcu — semantica'dan bağımsız) |
| B6 | YOL-HARITASI bayat: §6-C ve §6-F fiilen kodda BİTMİŞ (pipeline_kayit.py 6/14 append-only; kunye_teyit.py 38-47 _oa/cikti dışlama + MERCİ katmanı), Fikir 1/2/3 bitmiş (döküm diski, teslim_paketi.py, sure_nobetci.py mevcut) — kutular ⬜ duruyor | ters-yön merceği satır kanıtlarıyla; DURUM bloğu v0.5.0 döneminde kalmış | tek seferlik (mutabakat oturumu) |

### 1c. Semantica'ya özgü NET katkı — dürüst bilanço

Antitez turunun meta-tespiti **[doğrulandı]**: envanterdeki gerçek boşlukların hepsi ya kendi
backlog'umuzda zaten yazılıydı (B2 = P2 maddesi; B3 = Fikir 8) ya semantica'dan bağımsız bakım borcu
(B5, B6). Semantica'dan taşınabilir tek somut kod adayı (bi-temporal çekirdek, 174 satır stdlib)
ihtiyaç gösterilemediği için düştü. Kalan katkılar **fikir/ibret düzeyindedir**: uuid5 içerik-türevli
ID deseninin bizim ekosistemde NEDEN çalışmayacağının anlaşılması, "confidence 0-1" alanının sayı-uydurma
yasağıyla çatışması, FTS5-Türkçe sınırının erken görülmesi, vendoring yolunun keşfi.

---

## 2. KAZANIM × ÜÇ YOL KIYASI

### Ortak hüküm — YOL-B (pip: `semantica==0.6.0`): TÜM kazanımlar için RET **[doğrulandı]**

Üç bağımsız çürütücünün de yıkamadığı, tersine güçlendirdiği karar:

- **43 ZORUNLU bağımlılık** — torch, transformers, sentence-transformers, spacy, faiss-cpu,
  opencv-python, librosa, gensim, umap-learn çekirdekte (pyproject.toml 46-89, "SAFE DEFAULT" başlığı);
  GB mertebesi kurulum [spekülasyon: boyut ölçülmedi, paket adlarından çıkarım]. Etiket: **ÖLDÜRÜCÜ**.
- **CI kendi Python testlerini KOŞMUYOR** — 9 workflow, sıfır pytest adımı; ~4.270 test fonksiyonu
  repoda duruyor ama hiçbir otomasyonla doğrulanmıyor (ci.yml 20-63). Etiket: **YAPISAL**.
- **CHANGELOG'un kendi itirafıyla kırık modüller** — pipeline_provenance var olmayan modülü import
  ediyor; 18 provenance wrapper'ının arka sınıfları eksik; evals boş "Coming Soon". "Production/Stable"
  classifier'ı ile çelişiyor. Etiket: **YAPISAL**.
- **API kararsız** — 3 haftada 192 commit, dolu Unreleased; requires-python >=3.8 beyanı
  numpy>=2.0.2 ile çelişik [spekülasyon]; Windows CI yok. Etiket: **YAPISAL**.
- **KVKK m.12 açısı** — müvekkil verisi işleyen tek makinede ~177k satır denetlenmemiş üçüncü-parti
  kod + dev transitif yüzey, veri güvenliği yükümüyle ters. Etiket: **ÖLDÜRÜCÜ** (bu sistem için).
- Anayasa uyumu: fiilî bağımlılık felsefesi ("minimal + Windows-dostu + binary'siz + eksikte
  fail-closed" — yazılı ayrı madde DEĞİL, requirements.txt + oa-ingest pratiği [doğrulandı]) ile
  taban tabana zıt.

### Keşfedilen dördüncü yol — YOL-B′ (vendoring: seçilmiş dosya kopyası)

Ters-yön merceğinin haklı tespiti **[doğrulandı]**: taslak karar uzayı eksikti. MIT lisansı telif
satırı korunarak dosya kopyalamaya izin verir; kopyalanan dosya pin'lidir (API churn etkisiz),
kurulum yoktur, testleri yerel pytest'e bağlanır. **Bugün vendor edilecek somut hedef kalmadı**
(tek aday bi-temporal çekirdeğiydi; ihtiyaç düştü) — ama yol, GELECEK kararlar için kayda geçirilmeli.
Aile kuralı önerisi (Can'ın onayına): *vendor/ altındaki kod DONDURULMUŞTUR; her vendor dosyası kendi
test dosyasıyla gelir; aile_dogrula'ya "vendor dosyası testsiz olamaz" denetimi eklenir* (m.0 fiilî
donanım ilkesiyle uyum).

### K3 — Değer-düzeyi çelişki tespiti (B1 boşluğu)

- **YOL-A (seçilen — ama KÜÇÜLTÜLMÜŞ ve ŞARTLI):** Önce ÖLÇÜM: kapanmış gerçek bir dosyanın
  vakia.json'u elle taranır — "aynı olgu + farklı değer" deseni hiç çıkmıyorsa kalıcı gömülür.
  Çıkıyorsa: exit-1 kapısı DEĞİL, `vakia_matris.py`'ye ~20 satır **advisory rapor** + şemaya
  "çekişmeli/taraf-beyanı" işareti (işaretli kayıt = İHTİLAF [davanın konusu, meşru], işaretsiz =
  olası veri çelişkisi). Kapanış ancak avukat-karari olayıyla.
  Gerekçe: antitez turu iki öldürücü kusur buldu — (i) şemada olgu-anahtarı/tutar/taraf boyutu yok,
  vakia.json'u model TEK geçişte kurduğundan aynı anahtara iki değer hali fiilen doğmuyor (denetçi boş
  döner); (ii) hukukta çelişen iki değer çoğu zaman UYUŞMAZLIĞIN KENDİSİDİR — mekanik exit-1, modeli
  iki değerden birini silmeye zorlar = reddettiğimiz ConflictResolver'ı arka kapıdan kurmak.
- **YOL-B/B′:** Semantica ConflictDetector alınmaz — çekirdeği trivial (str-set karşılaştırma),
  kritik-alan/uyumsuz-tip tabloları İngilizce-gömülü ('name','revenue', Person↔Organization),
  Türk hukuku şemasında sessizce etkisiz; str() eşitliği sahte çelişki üretir ('1.0'≠'1') [doğrulandı].
- **Efor:** ölçüm 0,5 oturum; advisory ~20-50 satır. **Anayasa:** rapor-durma m.9 ("karar materyali
  üretir; nihai karar Çapar'ın") ile tam uyumlu; Türkçe değer normalizasyonu (tarih/tutar biçimleri)
  kapsam dışı tutulur, tutulmazsa efor patlar [doğrulandı — kvkk merceği].

### K4 — Bi-temporal olgu modeli + as-of sorgusu → **YOL-C (ALMAMA)** [doğrulandı]

Antitez turunda **öldürücü** ile düştü: (i) tek bir kullanım senaryosu gösterilemedi — dava dosyası
KAPALI tarihsel kayıttır; olay zaten nokta-zamanlı ('tarih' alanı); "T itibariyle görünüm" =
kronolojide tarih≤T satırları, vakia_matris bunu bugün üretiyor; (ii) bi-temporalliğin gerçekten
gerektiği tek yer olan sürelerde ZATEN var (`sureler.json {son_gun, kayit}`); (iii) "dosya geçmişte
nasıl görünüyordu" append-only defter + tez_gecmisi + GEÇERSİZ-KILINDI + arsiv-yerel nüshalarıyla tam
cevaplı; (iv) model-doldurmalı geçerlilik alanları dayanaksızsa m.4 ("OLGUDA doğaçlama asla") ihlali —
örnek alınan sistemde bile bu alanlar "always caller-supplied, never auto-computed". Mutable
`gecersiz(bool)` fikri ayrıca append-only idiyomla çatışıyordu (ikinci hükümsüzlük dili = yeni çelişki
yüzeyi). **Gelecek kaydı:** ihtiyaç bir gün ÖLÇÜLÜRSE doğru araç yerli yazım değil YOL-B′ vendor'dur
(temporal_model.py 174 satır stdlib + kapsamlı test dosyası birlikte taşınır) [doğrulandı — ters-yön].

### K5 — Defter bütünlüğü (B4) → hash zinciri DÜŞTÜ; yerine mini-nöbetçi **[doğrulandı]**

Taslaktaki onceki_imza hash zinciri **yapısal** kusurla çöktü: defter fan-out alt-ajanlarının PARALEL
append ettiği JSONL (bu yüzden append-only seçilmişti); satır-zinciri iki eşzamanlı append'te çatallanır
→ sahte bozulma alarmı; tek bozuk satır tüm devamı KALICI kırmızıya boyar (append-only onarımı yasaklar)
→ alarm körlüğü. Tehdit modelinin gerçek kısmı (bütün-dosya kaybı/kırpılma) için yeter çözüm:
**DURUM.md türetilirken defter satır sayısı + dosya sha'sı metrik.json'a yazılır; önceki koşuya göre
satır sayısı AZALMIŞSA uyarı** (~5-10 satır, yarışsız, onarım sorunsuz). YOL-A(mini).

### K6 — Ortak kimlik uzayı (B2) → **YOL-A** (kendi P2 maddemizin icrası) [doğrulandı]

Acı gerçek ve ölçülmüş (alt-dize eşleşmesi kısa/benzer adlarda yanlış pozitif/negatif üretir); madde
semantica'dan BAĞIMSIZ olarak P2'de zaten planlıydı. Tasarım düzeltmesi antitezden: **uuid5
içerik-türevli ID ALINMAZ** — içerikten türeyen kimlik, üç dosyayı ayrı model geçişlerinin yazdığı
ekosistemde ya kırılganlığı artırır ya gereksizleşir; ayrıca değer-türevli ID, değer-çelişki
gruplamasını imkânsızlaştırır (aynı olgunun iki değerli kaydı farklı ID alır). Doğru biçim: yetkili
kayıt dosyasının atadığı kısa el-ID (V1/D3/E7) + ingest evrak #no referansı + `capraz_denetim`'in
FK denetçisine dönüşmesi. Ön-koşul: B5 testleri (şemayı okuyan dört motor testsizken şema geçişi kör
refactor olur). Efor: şema tasarımı + geçiş ~2-3 oturum. Anayasa: temiz.

### K7 — Davalar-arası karar kaydı + emsal hafızası (B3) → sqlite/FTS5 biçimi **DÜŞTÜ**; çekirdek Fikir 8'e iner

Taslağın A4'ü antitez turunda en ağır hasarı aldı (iki mercekten dört öldürücü/yapısal):

- **m.7 garantisi boştu:** `gizlilik_tara.py` desen bekçisidir, İSİM TESPİTİ HİÇ YAPMAZ; m.7'nin
  çekirdek yasağı tam olarak isimdir. Reponun kendi planı bile arsiv terfisi için ayrı "isim/TCKN
  taraması" kapısı ister (YOL-HARITASI satır 65, ⬜) [doğrulandı].
- **Süzgeç ikilemi:** künye deseni strict'te ASK/DENY → künye işaretçili hiçbir kayıt yazılamaz
  (kütük işlevsiz); balanced'a inmek = müvekkil esas no'su ile Yargıtay künyesi aynı regex'te
  ayırt edilmeden geçer (süzgeç delik) [doğrulandı].
- **Damga davalar-arası taşınamaz:** m.5 "teyit ≠ muhakeme" — damga DAVAYA-BAĞ'ın çıktısıdır; dava
  X'te LEHE olan Y'de ALEYHE olabilir; kütükte damga = muhakemeyi önbelleğe almak = m.5 ikinci
  yarısının ihlali + Denizli-754 bayat-tohum deseninin kurumsallaşması [doğrulandı].
- **KVKK sırası ters:** imha/saklama ritüeli yazılmadan (P2 ⬜) kalıcı davalar-arası kütük kurulamaz;
  sqlite'ta DELETE imha değildir (secure_delete + VACUUM + WAL artıkları tasarlanmadan KVKK "yok etme"
  gerçekleşmez); konum disiplini yoksa OneDrive-senkron dizine düşen tek dosya, TÜM müvekkil
  örüntülerini Layer 0'a görünmeden buluta çıkarır (bu makinede OneDrive mevcut) [doğrulandı].
- **Ölü depo dinamiği + kurucu direktif:** oa-arsiv "pratik faydası düşük" gerekçesiyle Can kararıyla
  kaldırılmıştı; FTS5 unicode61 Türkçe gövdeleme yapmaz; tek avukat kapanış hızında arama gerektirecek
  kütle yıllar alır [doğrulandı].

**Ayakta kalan çekirdek** (semantica katkısı ≈ 0; kendi Fikir 8'imiz): `ders_damit.py` —
md-only, append-only, **insan-onaylı** (oa-usta "üretilen taslaktır" ilkesinin kütüğe izdüşümü),
kapalı-sözlük şema (olay-tipi + norm kimliği + sonuç; serbest metin YOK, damga YOK, confidence YOK —
sayı-uydurma yasağı üç SKILL.md'de yazılı), arama katmanı YOK (grep yeter). **Ön-koşullar:**
(1) isim-tarama kapısı (YOL-HARITASI satır 65) yazılmış olacak; (2) dersler/ vs arsiv-yerel doc/kod
tutarsızlığı kapatılmış olacak; (3) konum sabit + bulut-senkron yasağı mekanik denetlenecek;
(4) KVKK yaşam döngüsü (P2) tasarıma dahil. Ters-yön merceğinin haklı notu: kütük yokken kapanan her
dosyanın dersi TELAFİSİZ kaybolur — bu, ön-koşulları hızlandırma gerekçesidir, atlama gerekçesi değil.
**Künye önbelleği yasağı her durumda kalır** (m.5: her dosyada MCP teyidi).

### K8-K11 — ALMAMA (YOL-C) listesi [doğrulandı — üç mercek de yıkamadı]

| Kalem | Gerekçe |
|---|---|
| **MCP sunucusu** | Tek kullanıcılı lokal kurulumda dosya-tabanlı hafıza zaten köprü; semantica'da İKİ paralel MCP sunucusu var (17 vs 12 araç, kanonik belirsiz), kök 'mcp' paket adı resmî SDK ile çakışma riski, kalıcılık bile opsiyonel. Bakım+saldırı yüzeyi ekler, işlev eklemez. |
| **Datalog/kural muhakeme motoru** | Hukuki nitelemeyi mekanikleştirmek ailenin bilinçli felsefesine aykırı (grafik_denetim docstring: "illiyetin HUKUKİ niteliğine karar VERMEZ"). Semantica'nın en iddialı motoru Rete zaten iskelet (AlphaNode._matches koşulsuz True). |
| **ConflictResolver otomatik çözüm** | "most_recent kazanır" tarzı stratejiler çelişen tarih/tutar karşısında KARAR üretir — karar avukatındır (m.9). |
| **Embedding tabanlı semantik arama** | Statü düzeltmesi [ters-yön haklı]: "asla" değil "**şartlı yedek**" — arama katmanı hiç doğmadığı için bugün konusu yok; doğarsa önce FTS5 `tokenize=trigram` (bu makinede doğrulandı: SQLite 3.50.4, trigram OK) + ölçülebilir geri-çağırma eşiği; eşik tutmazsa lokal ONNX + ÇOK DİLLİ model (varsayılan bge-small-en-v1.5 İngilizce'dir, alınmaz). |
| **PROV-O/RDF ihracı** | Tüketicisi yok; semantica'da bile dahili depo RDF değil. |

### K12 — Görselleştirme → küçük YOL-A adayı (sıra disiplininden bağımsız) [doğrulandı — ters-yön]

`grafik_denetim.py --json` çıktısı köprü düğümleri (muvazaa sinyali), kesme adaylarını (mücbir sebep)
ve yük taşıyan kenarları (ispatlanmazsa zincir kopar) ZATEN üretiyor; tüketicisi yok. Tek dosyalık,
stdlib-only, CDN'siz gömülü-SVG HTML görselleştirici (~150-300 satır): şema değiştirmez, salt-okur,
Layer 0 temiz (dosya diskte kalır) — avukatın hâkime/müvekkile illiyet anlatımında doğrudan
kullanılabilir ürün. Semantica katkısı yalnız ilham (onların yığını plotly'dir, alınmaz).

---

## 3. DENGE TABLOSU

| Kazanım | YOL-A (devşirme) | YOL-B (pip) | YOL-B′ (vendor) | YOL-C (almama) | SEÇİM |
|---|---|---|---|---|---|
| Kalıcı graf | — | RET | — | zaten var | **C** (sahte-fayda) |
| Yapısal çelişki/graf denetimi | — | RET | — | zaten var | **C** (sahte-fayda) |
| Kaynak izi/provenance | — | RET | — | zaten var | **C** (sahte-fayda) |
| Değer-çelişki tespiti | ölçüm→advisory ~20-50 satır | tablolar TR'de etkisiz | çekirdek trivial, gerek yok | ölçüm boşsa göm | **A (şartlı-küçük)** |
| Bi-temporal + as-of | ihtiyaç yok | RET | 174 satır hazır ama ihtiyaç yok | ✓ | **C** (gelecekte gerekirse B′) |
| Defter bütünlüğü | mini-nöbetçi ~10 satır | RET | — | zincir biçimi düştü | **A (mini)** |
| Ortak kimlik uzayı | el-ID + FK denetçisi (P2 icrası) | RET | uuid5 alınmaz | — | **A** (ön-koşul: B5 testleri) |
| Davalar-arası emsal kütüğü | Fikir 8 md-only, ön-koşullu | RET | — | sqlite/FTS5 biçimi düştü | **A (şartlı, ertelenmiş; semantica-dışı)** |
| MCP sunucusu | — | RET | — | ✓ | **C** |
| Datalog/reasoning | — | RET | — | ✓ | **C** |
| Otomatik çelişki çözümü | — | RET | — | ✓ | **C** |
| Embedding arama | — | RET | — | şartlı yedek | **C (şartlı yedek)** |
| Görselleştirme | tek dosya HTML/SVG | RET (plotly) | — | — | **A (küçük, bağımsız)** |
| *Meta: vendoring protokolü* | aile kuralı önerisi | — | çerçeve kazanımı | — | **kabul önerilir** |

**Terazi (tek paragraf):** Toplam fayda tarafında büyük kalem YOKTUR — semantica'dan ne kurulum ne kopya
düzeyinde bugün taşınacak kod çıkmıştır; fayda hanesinde kalanlar üç küçük iyileştirme (advisory
değer-çelişki [ölçüme bağlı], defter mini-nöbetçisi, graf görselleştirici), bir orta kalem (P2 kimlik
uzayının — zaten bizim olan — teyitli önceliklendirilmesi) ve iki çerçeve kazanımıdır (vendoring yolu +
bayat yol haritasının kanıtı). Toplam bedel tarafında ise pip-yolunun bedeli ÖLDÜRÜCÜ (GB bağımlılık,
test edilmeyen CI, kırık modüller, KVKK yüzeyi), sqlite-emsal-kütüğünün bedeli YAPISAL (m.5/m.7/KVKK
çatışmaları) olarak ölçülmüştür. Net sonuç: **bedelli her şey reddedilir; bedelsiz küçükler alınır;
asıl efor K4'e gider.** Bu, "uyarlama programı" değil "seçici bağışıklık + üç ucuz vitamin"dir.

---

## 4. NET TAVSİYE

**İlk somut adım (ilk oturum, kod değişikliği önerisi olarak Can onayına):**
**YOL-HARITASI mutabakat oturumu** — §6-B/C/F ve Fikir 1-2-3 kutuları koda karşı tek tek işaretlenir
(kanıtlar bu görüşte hazır), DURUM bloğu v0.5.7.5'e taşınır, K1'in bugünkü durumu canlı ölçülür
(hook_doktor/kurulu-kopya + skill listesi). Gerekçe: tüm zamanlama kararları şu an bayat belgeye
çapalı; bu görüşün kendi taslağı bile bu tuzağa düştü (antitez yakaladı).

**Efor önceliği (değişmez):** **K4 — gerçek dosyada uçtan uca prova + UDF gerçek UYAP testi.**
"UYAP Asistan v1.0" ibaresi repoda geçmiyor **[doğrulandı — grep boş]**; bu adı, K4 + P1-UDF kümesinin
etiketi olarak okuyorum **[yorum]**. Deterministik filo tek bir gerçek UYAP teslimiyle uçtan uca
sınanmadıkça filoya katman eklemek, test edilmemiş uçağa koltuk eklemektir. Semantica'dan süzülen
hiçbir adım K4'ün önüne geçmez.

**Alınacaklar — sıra ve koşullarıyla:**

1. **[hemen, paralel, onay gerekmez-denecek kadar küçük ama yine de onaya sunulur]**
   a. **A1a:** Dört motora karakterizasyon testi (MEVCUT davranışı olduğu gibi kilitler; davranış
      değişikliği İÇERMEZ). Bakım borcudur, semantica'dan bağımsızdır.
   b. **DURUM.md advisory bağlantısı:** grafik_denetim/kiyas_denetim/usul_matris --json çıktıları
      pipeline_kayit'in mevcut vakia-deseni örnek alınarak DURUM.md advisory alanlarına bağlanır
      (~50 satır, sıfır şema değişikliği) → üç motora bir anda GERÇEK tüketici doğar.
   c. **Defter mini-nöbetçisi:** satır sayısı + sha, azalmada uyarı (~10 satır).
2. **[K4 sonrası / P2 penceresi]** **K6 kimlik uzayı:** şema tasarımı Can onayına; A1a ön-koşul;
   el-ID + FK denetçisi; uuid5 yok.
3. **[ölçüme bağlı]** **K3 değer-çelişki:** önce kapanmış gerçek dosyada desen taraması; boşsa göm;
   doluysa advisory + çekişmeli-işaret.
4. **[isteğe bağlı, sıra bağımsız]** **K12 görselleştirici** — Can isterse hızlı-kazanım.
5. **[ertelenmiş + ön-koşullu + semantica-dışı]** **Fikir 8 ders_damit (md-only):** isim-tarama
   kapısı + dersler/ tutarsızlığı + konum/senkron disiplini + KVKK yaşam döngüsü tasarımı
   tamamlanmadan AÇILMAZ; damga/confidence/künye-önbellek asla.

**Alınmayacaklar:** pip semantica (her biçimde), MCP sunucusu, Datalog, otomatik çelişki çözümü,
PROV-O/RDF, bi-temporal şema alanları, hash zinciri, sqlite/FTS5 emsal deposu, embedding araması
(şartlı yedek statüsünde uyur).

**Karar soruları (Can'a):**
1. kiyas_denetim kritik boşlukta **kapı mı olsun (exit 1), karar-malzemesi mi kalsın (exit 0)?**
   (Mevcut exit 0 bilinçli tasarım olabilir; terditli/alternatif savunma meşru avukat kararıdır.
   Antitez iki mercekte "kapı olmasın" yönünde; ters-yön "kapı olsun" dedi. Görüşüm: DURUM.md
   advisory'si varken kapıya gerek yok — ama bu sizin kararınız.)
2. **Vendoring aile kuralı** (vendor dondurulur + testli gelir + aile_dogrula denetler) kabul edilsin mi?
3. Anayasaya **m.0'a "dış desen devşirme protokolü" fıkrası** eklensin mi? (Bu analiz, uyumu m.4/m.7/
   m.0/m.8'den DOLAYLI türetmek zorunda kaldı — açık hüküm yorumu kapatır.)
4. Fikir 8'in ön-koşul zinciri onaylanıyor mu, yoksa tamamen mi gömülsün?

---

## 5. KARŞI GÖRÜŞ (oa-antitez ruhuyla — kendi tavsiyemin çürütme turu)

**m.8 dürüstlük beyanı:** `oa-antitez` parçası Skill aracıyla FİİLEN çağrıldı ve gövdesi yüklendi
(kanıt-1). Deterministik motoru (`antitez_matris.py`, 8 sabit HUKUKİ cephe: usul/vakıa/ispat/...)
dava-bağlamına özgü olduğundan bu mimari kararda KOŞULMADI; cephe-eksiksizliği işlevi, üç bağımsız
çürütücü ajan (sahte-fayda/fırsat-maliyeti · KVKK/anayasa · ters-yön) + şiddet etiketi
(öldürücü/yapısal/yönetilebilir/küçük) ile karşılandı. Toplam: 26 çürütme denemesi, 19 ayakta-kalan.

### Düşenler (ilk taslağımdan çökertilen parçalar — bu görüşe düzeltilmiş halleri girdi)

| Taslak iddiam | Çürüten | Şiddet | Sonuç |
|---|---|---|---|
| Bi-temporal alanlar + as-of görünümü | sahte-fayda + kvkk | öldürücü | YOL-C'ye indi |
| Değer-çelişki exit-1 kapısı | sahte-fayda + kvkk | öldürücü | ölçüm + advisory'ye indi |
| sqlite/FTS5 davalar-arası kütük | sahte-fayda + kvkk (4 ayrı vuruş) | öldürücü | Fikir 8 md-only + ön-koşullara indi |
| Defter hash zinciri | sahte-fayda | yapısal (yarış koşulu) | mini-nöbetçiye indi |
| "Bu bir semantica uyarlama programıdır" çerçevesi | sahte-fayda | yapısal | NEGATİF SONUÇ çerçevesine döndü |
| YOL-B'nin vendor'suz toptan reddi (karar uzayı eksik) | ters-yön | yapısal | YOL-B′ eklendi |
| Bayat YOL-HARITASI'na çapalı zamanlama | sahte-fayda + ters-yön | küçük/yapısal | mutabakat oturumu ilk adım oldu |
| uuid5 içerik-türevli ID | sahte-fayda + kvkk | yönetilebilir | el-ID + FK'ye döndü |
| kiyas exit-1'in A1'e gömülmesi | kvkk | küçük | ayrı karar sorusuna döndü |
| gecersiz(bool) alanı | kvkk | yapısal | append-only düzeltme-olayı idiyomuna döndü |
| Embedding "ALMAMA=asla" etiketi | ters-yön | yönetilebilir | "şartlı yedek"e döndü |
| Görselleştirmenin gerekçesiz ertelenmesi | ters-yön | küçük | bağımsız küçük adaya döndü |

### Ayakta kalanlar (yıkılamayanlar — güçlenerek çıktı)

- **YOL-B (pip) toptan RET** — üç mercek de saldırdı, üçünde de güçlendi (KVKK merceği ek gerekçe
  ekledi: tedarik-zinciri yüzeyi).
- **Sahte-fayda ayıklama listesi** (kalıcı graf / yapısal denetim / kaynak izi / dava-içi karar
  kaydı "zaten var") — dosya-satır kanıtlı, simetrik doğrulama (semantica tarafı da okundu).
- **Künye önbelleği yasağı** — m.5 + içtihat değişkenliği + Denizli-754; hız kazancı tek güvence
  noktasına değmez.
- **YOL-C çekirdeği** (MCP/Datalog/Resolver/PROV-O) — ters-yön merceği her kalemi geri kazanmayı
  denedi, hiçbirini kurtaramadı.
- **Dört motorun test borcu + K4 önceliği** — tersine keskinleşti.
- **6 gerçek boşluk envanteri** — tamamı dosya/satır kanıtlı çıktı.

### Artık riskler (çürütülemedi, dürüstçe işaretli)

1. **[spekülasyon]** Ters-yön merceğinin "telafisiz ders kaybı" argümanı: Fikir 8 ön-koşulları
   tamamlanana kadar kapanan dosyaların dersleri gerçekten kaybolmaya devam eder. Ön-koşulları
   hızlandırmak bu riski küçültür; ama ön-koşulsuz açmak m.7/KVKK riskini büyütür. Terazi Can'ındır.
2. **[spekülasyon]** K1'in (kurulu kopya senkronu) bugünkü durumu bu oturumda canlı ölçülmedi
   (salt-okuma sınırı); mutabakat oturumunda ölçülmeli — Denizli-754 dersi gereği bayat kurulu kopya
   tüm bu analizi masadaki araca yansıtmayabilir.
3. **[yorum]** "UYAP Asistan v1.0" okuması: bu adın başka bir planın (repo-dışı) etiketi olma
   ihtimali var; öyleyse zamanlama bölümü o planla çaprazlanmalı.
4. Değer-çelişki ölçümü hiç yapılmadan advisory yazılırsa boş-denetçi riski geri gelir — sıra bozulmamalı.

---

*Bu görüş salt-okuma oturumunda üretildi; repoda status.md ve bu dosya dışında hiçbir değişiklik
yapılmadı, hiçbir şey push edilmedi, hiçbir paket kurulmadı. Semantica klonu `%TEMP%\semantica`
altındadır (silinebilir). Uygulama, Av. Bayram Can Çapar'ın kabulüne bağlı ayrı oturumdur.*

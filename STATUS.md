# DURUM — Ortak Avukat

**Tarih:** 2026-08-26 · **Sürüm:** 0.5.11 · **Commit:** `26bd278`+
*(önceki kayıtlar: 2026-08-22 · 0.5.9 · `46bd1d3` — 2026-08-15 · 0.5.8.4 · `fc9cb31` — 2026-08-07 · 0.5.7 · `2804eef` — 2026-08-06 · 0.5.6.1 · `d69187f` — 2026-07-29 · 0.5.5.5 · `a1b9d18`)*

> **Saha sonucu (tek prompt, gerçek istinaf dosyası, Fable 5 max):**
> [SAHA-SONUCU.md](SAHA-SONUCU.md) — ~200 evrak · 49 dk · 45,6k token ·
> teslim edilebilir ek beyan + geçerli UDF. v0.5.7 o koşunun bulgularından
> doğdu (bayat-tohum aşısı · [G4] bağlantı kapısı · yerel motor v2 ·
> anayasa m.0 · hook doktoru).

Bu dosya deponun **o anki gerçek** durumunu tutar: neyin ölçüldüğü, neyin
açık kaldığı, sıradaki sürümün neden değiştiği. Beyan değil **ölçüm** yazılır;
bir satır ölçülmeden buraya girmez.

---

## 0. Durum özeti (2026-08-26 · v0.5.11)

- **v0.5.10 — Kusursuz UDF Dönüşümü** (`83969e4`, 307 karnesi K1/K2 + 923
  çift-kanıt): atomik mühür (üretim=mühür, üç yolda) · FİLO-TAZELİK kapısı
  (kök+40-UYAP tüm teslim-sınıfı UDF'ler makbuza) · çift-uzantı kaynağında
  öldü · kopyalar mühürleriyle gider · sunum kilidi makbuz-sonrası değişiklik
  penceresini kapattı. Süit o gün 1371 yeşil.
- **v0.5.11 — Kit Güvenlik Katmanı** (`c428aa4`, 1865 karnesi T1-T7): rpm
  karantinası ('ask') · kilitli çekirdek (salt-okunur + 'ask') · yönlü
  tazelik (bayat/kanaldan-yeni/özdeş) · oturum damgası (defter+makbuz
  session_id) · çok-oturum görünürlüğü · dizin + MANİFEST-önce bekçileri.
- **Tam süit: 1385 yeşil / 1 tasarımsal atlama** · aile denetimi temiz ·
  CI 4'lü matris yeşil · kurulu kanal 0.5.11.
- **Saha:** 149 gerçek dava toplam; v0.5.x döngüsünde 9 belgeli koşu
  ([SAHA-DENEYLERI.md](SAHA-DENEYLERI.md)); ilk ORGANİK yeşil makbuz 923
  sahasında; 1865 çok-oturumlu + müdahaleli-yetkili sınıf
  ([KARNE-1865.md](KARNE-1865.md)).
- **Açık işler:** v0.5.12 adayı P1-4b (çok-oturum kilit sahipliği) ·
  1865 içerik hükümleri avukatta · yeni saha koşusu v0.5.11 korumalarının
  canlı sınavı olacak.

## 0. Durum özeti (2026-08-22 · v0.5.9)

v0.5.8.4'ten bu yana **iki saha koşusu** daha yapıldı ve zincir dört sürüm
ilerledi:

- **346 sahası** (bilirkişi itirazı — v0.5.8.4'ün ilk saha provası): künye
  kapısı **gerçek bir açığı** yakaladı ve model dürüst davrandı; tek bir
  ayrıştırıcı yanlış-pozitifi (taslağın kendi DOSYA NO satırı) yeşil makbuzu
  imkânsız kıldı; hook katmanı klon-klasörde ölüydü → **v0.5.8.5** (`1ed49c4`):
  **A1 mutlak triyaj [G6]** (MCP'den çekilen her karar istisnasız tam metniyle
  okunur; LEHE → dilekçe, ALEYHE → cephanelik; NOTR artık BLOK) + [Y]/[M]/[N]/[T]
  denetimleri + kendi-dosya-no istisnası + hook dirilişi + e-imza halkası.
  160 yeni test; o günkü tam süit 1207 yeşil / 1 atlama.
- **777 sahası** (banka/kefalet ikinci cevap + 24 kök çapraz taraması): kök
  neden **bayat araç kiti**; ilk gerçek LEHE/ALEYHE triyajı (23/11) ölçüldü;
  resmî araç zinciriyle üretilen UDF dört kenarı 42,52 pt ile ilk
  **tam-standart ürün** olarak UYAP editöründe açıldı → **v0.5.8.6**
  (`ef018d2`): sürüm kilidi (bayat-nesil parmak izi) + kanonik makbuz kuralı +
  triyaj köprüsü. 45+ yeni test; tam süit 1256 yeşil / 1 atlama.
- **v0.5.9 Faz A** (`aee52cc`) — dört ilke (deterministik · tamamlayıcı ·
  kesintisiz · sürtünmesiz): **sunum kilidi** (yeşil kanonik makbuz yokken
  teslim-sınıfı dosya gönderimi "ask" kararına bağlı) + **inline zincir**
  (her dilekçe-taslak yazımında hızlı denetim in-process; bulgu modele geri
  akar) + **kesintisiz akış** (her prompt'a ≤3 satır ZİNCİR DURUMU). 50 yeni
  test; tam süit **1317 yeşil / 1 atlama**; 4 damga birlikte 0.5.9.
- **v0.5.9 borç-kapatma** (`4b861a2`) — iki bağımsız Fable 5 hakem denetiminin
  konsolide **T1–T26** raporu yerli uygulandı: hook_doktor onarımı + ilk kez
  testli · aile_dogrula **Kapı-A** (manifest "N skill" sayımı — "22 skill"
  hatasını canlı yakaladı → 20) ve **Kapı-B** (hook kapsamı) · çift-kanal
  dedup · oran araçları. 24 yeni test. Ardından `46bd1d3` ci-fix (ubuntu
  exec-bit).

**Bugünkü ölçüm (2026-08-22, bu makine):** toplanan test **1357**
(tam süit bugün koşulmadı; son tam ölçüm 1317 yeşil / 1 atlama, `aee52cc`) ·
vitrin alt-kümesi `-k "skill or sablon or anayasa or referans or readme"` →
**39 yeşil / 1 tasarımsal atlama** · `aile_dogrula` **TEMİZ (20 parça)** ·
plugin.json = marketplace.json = **0.5.9**.

- **CI:** `46bd1d3` ci-fix push'landı; bu kayıt anında koşu sonucu bu
  makineden doğrulanmadı — sürüm etiketlemeden önce `gh run list` (§6b kuralı).
- **Vitrin:** README kökten yeniden yazıldı (hedef okuyucu: Türk avukatı) —
  prompt şablonu, saha metodolojisi, 20 parça kataloğu, kolay kurulum,
  `_oa/` + 40-UYAP; telif blokları ana repodaki son hâlinden (68217f4/7692966)
  birebir taşındı.
- **Sırada:** v0.5.9'un kendi **saha provası** (organik yeşil makbuz hâlâ 0 —
  sınanmamış kapı beyandır) + 40-UYAP çıktı dizini entegrasyonunun saha teyidi.

---

## 1. Yeşil olanlar (2026-08-15 v0.5.8.4 ölçümü — güncel sayılar §0'da)

| Ne | Değer | Nasıl doğrulanır |
|---|---|---|
| Test — avukatın ortamı (yazıcı VAR, cp1254) | **1049 toplandı · 1048 yeşil · 1 tasarımsal atlama · 0 kırmızı** | `python -m pytest tests -q -rs` |
| Test — saha referansı verilince | atlanan test de koşar | `OA_SAHA_REFERANS=<dava>/_oa/metin python -m pytest tests/test_oa_ingest_ocr_nobetci.py -rs` |
| Test — CI ortamı (yazıcı YOK, taklit) | **0 kırmızı** (yazıcı gerektiren testler görünür gerekçeyle atlanır) | `OA_TEST_UDF_YAZICI=0 python -m pytest tests -q -rs` |
| CI — gerçek | `fc9cb31` **yeşil** (zincirin ilk yeşil koşusu) | `gh run list --limit 5` |
| Aile yapı denetimi | **temiz**, 20 parça | `python plugins/.../aile_dogrula.py plugins/ortak-avukat/skills` |
| Sürüm damgaları | dört damga eşzamanlı (`0.5.8.4`) | `test_hooks_wiring.py` |
| Hook katmanı — sahada | 372 sahasında **ilk kez uçtan uca canlı** ateşledi (v0.5.8.2 sonrası) | koşu artefaktları + defter `{"tip":"hook"}` satırları |

**Üç ortamda da koşuluyor artık:** avukatın makinesi (oturum açık) · CI
taklidi (yazıcısız) · gerçek CI. Yazıcısız ortam v0.5.5.1'den beri
ölçülmüyordu — §6b.

Onarım, çalışan ortamda **tek bir yeni atlama üretmedi** — kapsam aynen
duruyor. Kalan tek atlama, saha referansı verilmediğinde ortaya çıkan OCR
testidir; `OA_SAHA_REFERANS` tanımlanınca o da koşar (§6c).

---

## 2. Kapatılanlar (sürüm sürüm)

| Sürüm | Ne | Neden |
|---|---|---|
| `v0.5.5` | Aktivasyon: advisory kapı → atlanamaz zincir | v0.5.4 sahada kapıları ateşleyememişti |
| `v0.5.5.1` | Saha tetikleri + UDF hattı kilidi | mekanizmalar sağlamdı, **çağrılmıyorlardı** |
| `v0.5.5.2` | UDF geçerlilik kapısı: iki yanlış-BLOK + resmî okuyucu tanığı | kapı, koruduğu teslimi kesiyordu |
| `v0.5.5.3` | Bağımsız içerik hakemi + sicil desenleri + içtihat bağlantıları | dilekçe kendi bölümüyle aritmetik çelişiyordu |
| `v0.5.5.4` | GitHub açılış sayfası aile tanıtımı (yalnız anlatım) | 20 parçanın hiçbiri açılış sayfasında görünmüyordu |
| `v0.5.5.5` | **P0 — teslim hattı avukatın kendi ortamında çöküyordu** | §6 |
| `v0.5.6` | Yükleme hatası düzeltmesi + Yargı Pro MCP işlem rehberleri | 22→20 parça sayımı ve yükleme kırığı |
| `v0.5.6.1` | **P0 — `hooks` kaydı geri kondu** + devir zorlayıcı + iki rehber sadeleştirildi | v0.5.6 `plugin.json`'dan `hooks` satırını düşürmüştü: dört hook olayı da ölüydü |
| *(sürümsüz)* | **CI onarımı — release kapısı 11 koşudur ölüydü** | §6b |
| `v0.5.7`–`v0.5.7.5` | Bayat-tohum aşısı · [G4] link kapısı · yerel motor v2 · anayasa m.0 · araç-adı hizalaması · bağlantı katmanı (Pro birincil + `yargi-mcp` yedek) · davadan gelen atıflar da link zinciri | Denizli saha koşusunun bulguları + kullanıcı kuralları |
| `v0.5.8` | Semantica+Graft **desen** devşirmesi: [G5] · KAYNAK-BLOĞU · oa-mühür (PROV-O) · özne eşleştirici · `--zincir` · yasak-nöbetçisi | kod alınmadı, desen alındı (m.0 protokolü) |
| `v0.5.8.1` | Tetik paketi: kompakt-kapanış kuralı + [K] cephanelik bekçisi + Stop mühür nöbetçisi | 447 provası: 22 parçadan 1'i çağrılmıştı — desenler ateşleyemedi |
| `v0.5.8.2` | **Hook yapısal onarımı:** polyglot `run-hook.cmd`, `\|\|` zinciri yasak | masaüstü hook'u kabuksuz koşturuyor; üç sahada sıfır-ateşlemenin kökü |
| `v0.5.8.3` | Şekil standardı v2 (Yönetmelik No. 2646): 4 kenar 42.52pt · 1,5 satır · linkler 11pt parantezde | Can emri + mevzuat teyidi |
| `v0.5.8.4` | **372 karnesinin infazı:** elle-UDF engeli (3 katman) · makbuz garantisi · mühür otomasyonu · şekil kapısı · desen onarımları · Gate A dirilişi | 5 kollu adli analiz; 93 yeni test; CI ilk yeşil |

---

## 3. Açık bulgular (v0.5.6 hazırlık analizinden)

Sıra, **müvekkile dokunma** ihtimaline göre.

### A1 · `.xlsx` bilirkişi raporu sessizce kayboluyor — YÜKSEK
`manifest_olustur.py` `.doc/.xls/.xlsx/.odt/.heic` uzantılarını "ofis belgesi —
metin" diye sınıflar; `oa_ingest.py` bunları **işleyemez**. Sonuç: bir bilirkişi
hesap tablosu manifestte okunabilir görünüp ingest'te "desteklenmeyen tür"
oluyor. Uzantı kümesi üç dosyada yaşıyor ve **ikisi zaten ayrışmış**.
→ Tek kaynağa indir, fark `INGEST_OKUYAMAZ` diye **adlandırılsın** (sessiz değil).

### A2 · ~~Test dağılımı ters~~ → **KAPANDI (v0.5.14)** — DÜŞÜK
İlk kayıt (2026-08-06) altı motoru "hiçbir testte anılmıyor" diye saymıştı;
o gün doğruydu, ama **defter bayatladı**: dördünün test dosyası 2026-08-11'de
eklendiği hâlde bu satır aylarca eski hâliyle kaldı ve kapatılmış dört kalemin
gürültüsü, gerçekten açık olan tek kalemi gizledi (v0.5.14 denetim bulgusu
B-36).

**Bu satır artık elle tutulmuyor.** Motor kapsamı mekanik olarak denetlenir:
`tests/test_v0514_vitrin.py::test_b37_testte_hic_yuklenmeyen_motor_defterle_ortusuyor`
`skills/*/scripts/*.py` altındaki her motoru tarar; hiçbir testte yüklenmeyen
bir motor kaldığında kırmızı yanar ve borç ADIYLA kapsam defterine yazılır.
Aynı kapı ters yönde de çalışır: kapatılmış bir borç defterde kalırsa (yani
bu sayfanın 2026-08 hâli tekrarlanırsa) yine kırmızı yanar. Kapsam defterinin
son ölçümü **boş**tur.

### A3 · Resmî okuyucu bacağının kendisi testsiz — ORTA
`npx_ile_udf_oku` gerçek hâliyle hiçbir testte koşmuyor; tüm testler sahte
okuyucu enjekte ediyor. Yani UDF kapısının **tek dış tanığı** doğrulanmamış.

### A4 · ~~Delilsiz-unsur uyarısı testsiz~~ → **YANLIŞ TEŞHİS, DÜZELTİLDİ** — DÜŞÜK
İlk analiz "tek testi fonksiyonun adının kaynakta geçtiğini doğruluyor" demişti.
**Yanlış.** `tests/test_durum_md.py:319` gerçek bir `04-vakia.json` yazıp gerçek
CLI'yı koşturuyor ve `DURUM.md`'de uyarının 🔴 ile göründüğünü doğruluyor;
negatif vakası da var. Hata bendeydi: fonksiyon *adını* gremiştim, ürettiği
*çıktı dizesini* değil.

Geriye **daha dar** bir boşluk kalıyor: test, `04-vakia.json`'u **elle yazıyor**
— `vakia_matris.py` üretmiyor. Yani üretici şeması kayarsa tüketici testi yine
yeşil kalır. Kilitlenmesi gereken şey uyarı değil, **üretici-tüketici
sözleşmesi**.

### ÇALIŞAN SÜRÜM TABANI (2026-07-29 ölçümü — kod yok, yalnız kayıt)
Sistem bugün **bu sürümlerle** yeşil: `udf-cli` **0.4.3** · Python **3.14.6** ·
`pymupdf` **1.28.0** · `pillow` **12.3.0** · `pytest` **9.1.1** · Node **v26.4.0** ·
ortam kodlaması **cp1254** (PYTHONUTF8 ayarsız).

Bu satırın tek işi şu: yarın bir şey bozulduğunda "önceden ne çalışıyordu"
sorusunun cevabı olsun. **Sabitleme değildir** — sabitleme UYAP biçim
değiştirdiğinde bizi eski sürümde çakılı bırakır. Karar: pinleme **ertelendi**,
gerçek bir kırılma görülene kadar aksiyon alınmayacak (kullanıcı kararı,
2026-07-29). Bozulma olursa ilk bakılacak yer bu satırdır.

### A5 · `udf-cli@latest` 33 yerde pinsiz — ORTA (ERTELENDİ)
Teslim hattının tek yazıcısı ve tek doğrulayıcısı sürüm kilidi olmadan
çağrılıyor. Pinlemek de bedelli: UYAP biçim değişirse pinli sürüm sessizce
bayatlar. Karar gerektirir.

---

## 4. v0.5.6 — plan neden değişti

**Eski manda:** *"ateşlemeyen kapıyı sil, zırhı geri al; oran küçülmeli."*

Analiz bu mandayı **ampirik olarak çürüttü**:

- **Silinecek kütle yok.** 16.347 satır üretim kodunda ~8 satır ölü sembol var.
- **Zırh sandığımız şey dürüst kullanımda ateş ediyor.** 24 silme önerisinin
  24'ü çürütmede düştü; gerekçeler deneysel — ajanlar kodu silip koşturdu.
  `DAMGA=` normalizasyonu kaldırılınca sıradan bir avukat girdisiyle canlı
  fail-open üretti; `--dokum` satır-sonu kapısı "Windows'ta imkânsız" denen
  senaryoda bu makinede ateş etti; ZWSP katmanı `ictihat_getir` yanıtındaki
  **her markdown başlığında** ateşliyor.
- **Oran zaten sabit.** 5,26× → **5,41×**. Büyümedi, ama küçülmedi de.

**Yeni eksen: SADELEŞTİRME değil HİZALAMA.** Test ve denetim, işin *yapıldığı*
yere taşınır. Somut kapsam: A1 (evrak kaybı) · A2 (test dağılımı) · A3/A4
(sahte yeşil testler) · M8/M9 önkoşulları.

---

## 5. M8 / M9 önkoşulları — şu an **üretilmeyen** veri

Anatomi katmanı (kurgu kilitli) bu üç alan olmadan kurulamaz:

| Eksik | Nerede olmalı | Sonuç |
|---|---|---|
| **Karar tarihi** ayrıştırılmıyor | `kunye_ortak.py` (ESAS/KARAR/MERCİ/DAİRE var, TARİH yok) | M8'in zorunlu "örneklem beyanı → dönem" alanı kurulamaz |
| **Sayfa/satır izi** yok | `oa_ingest` UDF/DOCX/düz-metin hattı sayfa ayracı üretmiyor | M9 konkordansının `sayfa` sütunu boş kalır |
| **Taraf ve sonuç sınıfı** kalıcı değil | yalnız CLI argümanı + teslim makbuzu | M8'in taraf-bilinçli anatomisi dayanaksız kalır |

Ayrıca iki tasarım tuzağı ölçüldü: `_oa/arastirma/` dizini şu anda **sözleşme
dışıdır** (açılınca gölge-hat uyarısı üretir), ve `maruziyet.md` `_oa/cikti`
altına konursa `dosya-analiz.md`'ye **tam gömülür** — yani iç istihbarat
dilekçe yazıcısının bağlamına sızar.

---

### A6 · `maruziyet.md` gömülme tuzağı — plana bağlanmamıştı
`_oa/cikti` altındaki **her** dosya `dosya-analiz.md`'ye tam gömülür. `maruziyet.md`
(iç istihbarat: zayıf unsurlarımız) oraya konursa dilekçe yazıcısının bağlamına
**sızar** — anayasa m.6'nın anatomi düzlemindeki ihlali. §5'te ölçülmüştü ama
hiçbir iş kalemine bağlanmamıştı. Konum kararı M8'den **önce** verilmeli.

### A7 · Şema göçü riski — M8 örneklemini çarpıtır
Yeni alanlar (karar tarihi, paragraf izi, taraf/sonuç sınıfı) künye şemasını
değiştirir. Mevcut `_oa` klasörleri (441 ve 320 evraklık olanlar dâhil) eski
şemada kalır. M8 geldiğinde eski-yeni karışık külliyat **sessizce çarpık
örneklem** üretir. Şema sürümü + göç kararı, alan eklemeden önce verilmeli.

---

## 5b. Üç jüri hükmü (Fable 5, bağımsız, max efor)

**0 ONAY · 3 ŞARTLI-ONAY · 0 RET.** Üçü de eksen değişikliğini (sadeleştirme →
hizalama) ölçümle haklı buldu, üçü de **aynı itirazda** buluştu:

> Plan **içe dönük**. Elde dört bakir gerçek UYAP klasörü (idari, istinaf,
> aile, icra) dururken ağırlık sentetik test yazımına gidiyor. Oysa bu deponun
> **en ağır kusurlarının hiçbirini test bulmadı — hepsini saha buldu**:
> encoding çöküşü, elle yazılan defter, açılmayan UDF, geçerliyi kesen kapı.

Ortak şartlar: ölçüm ortamı sözleşmesi **mekanikleşsin** (CI'da `PYTHONUTF8`
unset ikinci koşu) · motor testleri **davranışsal** olsun ve en az bir **kırmızı
yol** içersin · her yeni teste "hangi saha arızasını yakalar" gerekçesi zorunlu,
gerekçesi yazılamayan test **yazılmaz** · motor başına en fazla ~150 satır bütçe
tavanı · `udf-cli`'nin gerçek sürümü teslim makbuzuna damgalansın.

**Jüri-3'ün açık uyarısı:** plan, şartlarla bile oranı ~5,41 → ~5,55'e
**büyütür**. "Oran küçülmeli" ölçütü ya açıkça yeniden onaylanmalı ya emekliye
ayrılmalı — **sessizce çiğnenmemeli**. (Bkz. §8/1.)

---

## 6. Bugünün asıl dersi

**Hata kodda değil, ölçüm ortamındaydı.**

Teslim hattı, avukatın kendi Windows ortamında (`PYTHONUTF8` ayarsız, cp1254)
çöküyordu: `subprocess.run(..., text=True)` çağrılarına `encoding=`
verilmediği için `udf-cli` çıktısı yerel kod sayfasıyla çözülüyor ve ilk
çok-baytlı karakterde `UnicodeDecodeError` fırlatıyordu. Sonuç sessiz bir hata
değil **teslim engeliydi**: geçerli bir dilekçe "GEÇERSİZ" ilan ediliyordu.

Görülmemesinin sebebi: geliştirme koşularının tamamı `PYTHONUTF8=1` ile
yapılmıştı ve o bayrak kusuru maskeliyordu. *"801 test yeşil"* beyanı **doğru
ama yanıltıcıydı** — sistemin fiilen çalıştığı ortam hiç sınanmamış, hep
düzeltilmiş bir ortam sınanmıştı.

Bu, günün tüm saha bulgularıyla aynı sınıftandır: **kapı yeşil görünüyordu,
değildi.** Defter elle yazılmıştı, UDF "üretildi" ama açılmıyordu, geçerlilik
kapısı geçerli dilekçeyi kesiyordu. Ortak kök: *doğru soruyu yanlış yerde
sormak.*

---

## 6b. Aynı ders, aynadan (2026-08-06) — CI

**Bu kez yerel yeşildi, CI kırmızıydı.** Aynı kanun, ters yön.

`v0.5.5.1`'de UDF hattı bilerek `npx udf-cli html2udf` tek yoluna kilitlendi
ve yerel motor kaldırıldı (B5: ürettiği `.udf` UYAP'ta açılmıyordu). `udf_yaz.py`
o günden beri **fail-closed**: oturum yoksa hiçbir `.udf` yazmaz. GitHub
koşucularında `npx` **var**, `udf-cli` **oturumu yok**. Zinciri sonuna kadar
koşturan **15 test** bu yüzden kırmızıya döndü — kod hatası değil, ortam.

Görülmemesinin sebebi: bildirimler okunmadı ve yerel koşu hep yeşildi.

**Bedeli, kırmızı testlerden büyüktü.** `ci.yml` şöyle diyordu: *"Release
kapısı: aile yapı denetimi + testler. İkisi de geçmeden yeşil olmaz."* Ama
`aile_dogrula` pytest'in **arkasında bir adımdı**; pytest patlayınca hiç
çalışmadı. Yani:

| | |
|---|---|
| Son yeşil koşu | `v0.5.5` — 28 Temmuz |
| Kırmızı koşu | **11** (v0.5.5.1 → v0.5.6.1) |
| Bu sürede çalışan yapı denetimi | **0 kez** |

Beş sürüm, var olmayan bir kapıdan geçti.

**Kanun:** *sürekli kırmızı bir kapı, olmayan kapıdır.* "Advisory kapı =
olmayan kapı" ile aynı hastalık — insan bakmayı bırakır. Ve: **bir kapı, başka
bir kapının arkasına saklanmamalı.**

**Onarım (yalnız `tests/` + `.github/`; `plugins/` altında tek satır değişmedi):**

1. `tests/oa_udf_ortam.py` — "gerçek yazıcı bu ortamda var mı" sorusunun **tek
   kaynağı**. Yoklamayı yeniden yazmaz; üretimdeki
   `udf_yaz.npx_kullanilabilir_mi()`yi çağırır ve **koşu başına bir kez**
   önbelleğe alır. (Aynı soru eskiden `test_udf_yaz.py`'de 5, `test_udf_metin.py`'de
   1 kez soruluyordu — her biri ayrı bir `npx … whoami` ağ turu. İkiz kaldırıldı;
   hem yerel hem CI koşusu hızlandı.)
2. **İki katman, "hepsini sustur" değil.** 15 testin 11'i aslında zincir
   *mantığını* sınıyordu, UDF'i tesadüfen istiyordu; bunlar `udf_arglari`
   fixture'ı ile koşar. Yazıcı **varsa fixture boştur** — avukatın makinesinde
   test bugünkünün aynısıdır, tam zinciri koşar. Yazıcı yoksa `--udf-yok`
   geçer; bu bayrak uydurma değildir, makbuza `udf_atlandi_istekle: true` diye
   yazılır. Gerçekten `.udf` artefaktı iddia eden 4 test görünür gerekçeyle
   atlanır; her birinin **ortamdan bağımsız ikizi** eklendi (818 → 821 test).
3. `aile_dogrula` **ayrı bir işe** alındı — bir daha testlerin arkasına
   saklanamaz. `pytest -rs`: atlanan her test gerekçesiyle listelenir.
4. Her koşunun başlık satırı durumu **basar**; sessiz atlama yok.

**Yeşil CI artık ne demek:** *"aile yapısı sağlam + teslim zincirinin mantığı
dört platformda ayakta."* **"UDF hattı çalışıyor" DEMEZ.** UDF hattı yalnız
avukatın kendi makinesinde (oturum açık) ve sahada doğrulanır. Bu ayrım
`ci.yml` başlığına da yazıldı — altı ay sonra rozet yanlış okunmasın.

**Reddedilen yol:** oturum jetonunu GitHub secret'a koymak. Dört iş × her
push ≈ 20 dönüşüm demekti; aylık kota tükenince **avukat gerçek dilekçesini
UDF'e çeviremezdi**. Test altyapısı müvekkil işini bloklayamaz. (Ayrıca jeton
kendini yalnız tutulduğu makinede tazeler; kopya bayatlar, CI yine kırmızıya
dönerdi.)

---

## 6c. Anonimleştirme sızıntısı (2026-08-06, aynı turda)

CI onarımının "2 atlanan test nedir" sorusundan çıktı.

`tests/test_oa_ingest_ocr_nobetci.py` v0.5.5'ten (`852fd3c`) beri depoda ve
depo **herkese açık**. İçinde bir müvekkil dosyasının **tam yolu sabit
yazılıydı**: kişisel Windows kullanıcı adı + `<yıl>_<esas>_<şehir>_<mahkeme>`
klasör adı; yanında iki gerçek evrak adı.

Anayasa m.7: *"hiçbir müvekkil, karşı taraf veya **dosya** ismen anılamaz"*
(Av.K. m.36 · KVKK). Esas numarası + mahkeme o dosyayı **tekilleştirir**.
`_saha/` klasörünü ve `SAHA-PB.md`'yi depo dışında tutmamızın gerekçesi tam
olarak buydu — ama bu, deponun **içindeydi** ve aylardır yayındaydı.

**İkinci bulgu, aynı satırda:** yol sabit yazılı olduğu için klasör yeniden
adlandırılınca test **sessizce atlanmaya** başladı. İki test bir süredir hiç
koşmuyordu ve kimse fark etmemişti — yine "ateşlemeyen kapı" sınıfı.

**Yapılan:** sabit yol kaldırıldı; referans `OA_SAHA_REFERANS` ortam
değişkeniyle verilir, beklenti listesi dava klasörünün kendi `_oa`'sında
(depo **dışında**) durur. Testlerdeki gerçek dosya kimlikleri kurgu ile
değiştirildi (`Örnek 1. İş Mahkemesi E. 2099/1` vb.); testlerin **amacı
korundu** — mahkeme deseni şehir adına değil `N. <tür> Mahkemesi` yapısına
bakar. Eklenti içindeki esas numarası 8 dosyada `saha dosyası A` ile
değiştirildi (yalnız açıklama satırları; **davranış değişmedi**).
Ve test **yeniden ateşler hâle geldi**.

**Dokunulmadı:** `Yargıtay 4. HD, E. 2023/1234` (uydurma test künyesi),
`E.2025/190` (Resmî Gazete'de yayımlanmış AYM kararı), sayı içermeyen şehir
anmaları (bir şehir bir dosyayı tekilleştirmez).

**Açık kalan — kullanıcı kararı:** bu içerik **geçmiş commit'lerde** duruyor.
Yalnız tepe temizlendi. Geçmişi silmek `git filter-repo` + force-push ister;
tüm SHA'lar değişir, etiketler ve mevcut klonlar kırılır.

---

## 7. Ölçüm

| Katman | Satır | 29 Tem (v0.5.5.5) |
|---|---|---|
| Doktrin (SKILL.md + references + README'ler) | 6.109 | 5.925 |
| Üretim kodu (`skills/*/scripts/*.py`) | 16.512 | 16.347 |
| Test | 16.142 | 15.736 |
| **Oran (kod+test)/doktrin** | **5,35×** | 5,41× (28 Tem tabanı: 5,26×) |

*(6 Ağu ölçümü; aradaki fark v0.5.6 + v0.5.6.1 + bu CI onarımının toplamıdır.
Oran **küçüldü** — doktrin, koddan ve testten hızlı büyüdü.)*

En büyük üç script tek başına 6.128 satır: `pipeline_kayit.py` (2.977),
`oa_hafiza.py` (1.581), `tam_tur.py` (1.570).

> **Ölçüm şerhi:** oran, paydanın tanımına duyarlıdır. Yalnız `SKILL.md` +
> `references` sayılırsa 7,16× çıkar. Yukarıdaki 5,41×, 28 Temmuz tabanıyla
> **karşılaştırılabilir** geniş tanımı kullanır (tüm `plugins/**/*.md`).
> İki sayıyı karıştırmak, oranın büyüdüğü yanılgısını üretir.

---

## 8. Karar bekleyen

1. **"Oran küçülmeli" ölçütü — geçerli mi?** Üç jüriden ikisi bunu doğrudan
   sordu. Plan, en dar hâliyle bile oranı büyütür. Üç seçenek: (a) ölçüt aynen
   geçerli → v0.5.6 yalnız A1+A5+önkoşullar olur, motor doğrulaması repo testi
   yerine **bakir klasörde saha koşusu** ile yapılır (net ~sıfır büyüme);
   (b) ölçüt "zırh/tören şişmesi" olarak yeniden tanımlanır; (c) emekliye ayrılır.
   **Sessizce çiğnenmeyecek** — karar buraya yazılacak.
2. **Ağırlık nereye?** Jürinin ortak itirazı: dört bakir klasör dururken
   sentetik test yazmak. v0.5.6 sahaya mı dönsün (playbook hazır), repoda mı
   kalsın?
3. **`udf-cli` pinlensin mi?** (A5 — iki yönlü bedel; hangi yönde olursa olsun
   gerçek sürüm teslim makbuzuna damgalanacak)
4. **`_oa/arastirma/` meşrulaştırılsın mı**, yoksa anatomi mevcut dizinlere mi
   yazsın? (gölge-hat bekçisini zayıflatmadan) — **ve `maruziyet.md` nereye?** (A6)

---

## 10. Saha test protokolü

`SAHA-PB v1.0` yazıldı: **depo dışında**, `uyap-evraklar/_saha/SAHA-PB.md`
(gerçek klasör adları taşıdığı için GitHub'a girmez). Özü: bir kapı ancak
avukatın **kendi ortamında**, gerçek dosyada, koşu penceresi içinde zaman
damgalı bir **eser** bırakmış ve o eser aşağı akışta **tüketilmişse**
ateşlemiştir; gerisi beyandır.

Bugünkü dersi yapısal olarak kapatan kural: koşu, ortam parmak izi almadan
başlamaz; `PYTHONUTF8` tanımlıysa koşu **başarısız değil HÜKÜMSÜZ** sayılır —
hiçbir çıktısı kanıt olamaz. Ayrıca koşu-içi onarım yasak (çökme bulgudur),
ölçümü avukat **ayrı terminalde** yapar (sistem kendi karnesini yazamaz), ve
başarı ölçütü koşu başlamadan yazılıp kilitlenir.

İlk adım **KOŞU-0**: kullanılmış bir klasörde ölçüm aygıtının provası — bakir
maliyeti sıfır. Gerekçe bugünün dersinin ta kendisi: doğrulanmamış ölçüm aygıtı
kıt bakir örneğe doğrultulmaz.

---

## 9. Nasıl doğrulanır

```bash
python -m pytest tests -q
```

```bash
python plugins/ortak-avukat/skills/oa-usta/scripts/aile_dogrula.py plugins/ortak-avukat/skills
```

**CI'ı YAZICISIZ ortamda taklit et** (avukatın gerçek oturumuna dokunmadan —
GitHub koşucusunun gördüğünü yerelde görmek için):

```bash
OA_TEST_UDF_YAZICI=0 python -m pytest tests -q -rs
```

**Sürüm etiketlemeden ÖNCE CI'a bak** (§6b dersi — sürekli kırmızı bir kapı,
olmayan kapıdır):

```bash
gh run list --limit 5
```

Avukatın gerçek ortamını sınamak için `PYTHONUTF8` **ayarlanmadan** koşulmalıdır
— aksi hâlde platforma özgü kusurlar maskelenir.

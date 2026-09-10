# DENETİM — Backend'de müvekkil lehine sonucu bozan sistemsel kırıklar

**Tarih:** 2026-09-10 · **Kapsam:** `plugins/ortak-avukat` tüm skill seti, backend (Python) katmanı
— 20 skill · 35 script · 32.278 satır · `tools/hook_doktor.py` · CI · kurulum belgesi
**Dal:** `claude/ortak-avukat-backend-check-qpjdbp` · **Karar verici:** Av. Bayram Can ÇAPAR

---

## 0. Soru ve muhakeme çerçevesi

Sorulan şuydu: *bir avukatın **müvekkili lehine** olan sonucu bozacak sistemsel kırık ve
bug var mı?* Bu soruyu verimli aramaya çevirmek için önce **hangi illiyet hatlarından**
zarar gelebileceği kuruldu — çünkü bu sistemde zarar "script çöktü" diye görünmez;
sessizce, yeşil bir makbuzun altından gelir:

| Hat | Mekanizma | Sonuç |
|---|---|---|
| **H1 — HAK KAYBI** | süre/usul hesabı yanlış | hak düşürücü süre kaçar; esasa girilmeden ret |
| **H2 — DAYANAK ÇÖKÜŞÜ** | künye/içtihat teyidi kör kalır; ALEYHE karar LEHE damgalanır; müvekkil-aleyhi ifade yakalanmaz | dilekçe kendi aleyhine delil taşır |
| **H3 — SIR** | gizlilik kapısı kaçırır/fail-open | müvekkil sırrı karşı tarafa/dış araca gider |
| **H0 — KAPI YANILSAMASI** | bir kapı hata alınca **geçirirse** ya da **hiç doğmazsa** | üç hat da sessizce açılır |

**H0 bu sistemde özel olarak ağırdır.** Deponun bütün vaadi tek cümledir: *"model kurar →
script denetler."* Bu vaat kırıldığında ortaya çıkan şey "denetim yok" değil, ondan
kötüsüdür: **denetim yapıldığı sanılan bir yokluk.** Aşağıdaki beş bulgunun dördü tam
olarak bu sınıftandır.

---

## 1. Bulgular

### B1 — `tam_tur.py` Python 3.12'den önce **import edilemiyor** (SyntaxError) · H0
**Kanıt.** Depodaki 35 script'in 34'ü Python 3.11'de temiz derleniyor; biri derlenmiyor:

```
plugins/ortak-avukat/skills/oa-pipeline/scripts/tam_tur.py:1407 ve :1479
SyntaxError: f-string expression part cannot include a backslash
```

f-string **ifadesi içinde** ters bölü, PEP 701 öncesinde (yani 3.12'den önce) sözdizimi
hatasıdır. Kırık olan tek dosyanın, rolü en ağır olan dosya olması tesadüf değil: bu
script `--durum` ("iş başında ilk soru"), `--baslat`/`--senkron`/`--kaydet` (DOĞUM-ANI
KALICILIK) ve **Gate G**'nin dayandığı `_analiz_kaydi_fiziksel_tamam` fonksiyonunu taşır.

**İlliyet — kapının kör noktası.** `pipeline_kayit._gate_g_kalicilik_denetle` fail-closed
yazılmış (P1-12) ve import başarısızlığında kapıyı KAPATIYOR. Ama o dala varmadan önce
şu satır var:

```python
analiz_json = os.path.join(kok, "_oa", "analiz", "dosya-analiz.json")
if not os.path.exists(analiz_json):
    return None, None          # ← tam_tur kullanılmamış sayılır: SESSİZ ATLAMA
```

`tam_tur.py` hiç çalışamadığı için `dosya-analiz.json` **hiç doğmaz** → kapı, korumak
istediği şeyin yokluğunu "bu akış tam_tur kullanmıyor" diye okur ve **kendini kapatmaz,
yok sayar.** Fail-closed tasarım, koruduğu aracın var olmasına bağlıysa, araç hiç
doğmadığında koruma da doğmaz.

**Kırığın avukata ulaşma yolu — belge çelişkisi.** Üç kaynak üç şey söylüyordu:

| Kaynak | Beyan |
|---|---|
| `README.md` (kurulum adımı, gereksinim tablosu, §2 başlığı) | **Python 3.10+** |
| `pyproject.toml` | `requires-python = ">=3.12"` |
| `.github/workflows/ci.yml` | yalnız **3.12 / 3.13** |

Avukat kurulum belgesine uyup 3.10/3.11 kurarsa, CI'nin hiç bakmadığı bir ortamda çalışır
ve Gate G sessizce düşer. Deponun kendi ilkesi — *"beyan değil ölçüm yazılır"* — burada
kurulum belgesinde çiğnenmişti: 3.10 desteği hiç ölçülmemiş bir beyandı.

**Onarıldı.** Sabit metinler f-string dışına alındı (uyumluluk çıpası notuyla); README'nin
üç yeri ölçülen gerçeğe (3.12+) çekildi ve alt sınırın *neden* bir tercih değil ölçüm
olduğu yazıldı. `tests/test_v0517_...::test_b1_tum_scriptler_calisan_python_ile_derlenebilir`
bu sınıfı süitin koştuğu her sürümde kilitler.

---

### B2 — Müvekkil-aleyhi taraması `--taraf` yokken kör, ama çıktı **"[OK] bulunamadı"** diyor · H2

Bu, denetimin en ağır tek bulgusudur; çünkü kapı çökmüyor, **yalan söylüyor.**

**Repro.** Dört ayrı ikrar taşıyan bir cevap dilekçesi taslağı (*"borcu kabul etmektedir"*,
*"davayı kabul ediyoruz"*, *"kusurlu olduğunu"*, *"iddia doğrudur"*):

```
$ dilekce_denetim.py taslak.md --tip cevap                 # --taraf YOK
   [OK] belirgin müvekkil-aleyhi ifade sinyali bulunamadı (heuristik)

$ dilekce_denetim.py taslak.md --tip cevap --taraf davali
   [UYARI] olası müvekkil-aleyhi ifade: "borcu kabul" ...
   [UYARI] olası müvekkil-aleyhi ifade: "doğrudur" ...
   [UYARI] olası müvekkil-aleyhi ifade: "iddia doğrudur" ...
```

**İlliyet.** `teslim_paketi.py`'nin `--taraf` yardımı **"boş bırakılabilir"** der; boşsa alt
çağrıya hiç geçirilmez (`+ (["--taraf", a.taraf] if a.taraf else [])`). `denetle()` içinde
`taraf in ALEYHE` False olur ve yalnız iki desenli `genel` seti taranır — yani taraf-özel
eksenlerin (kabul/ikrar · feragat · şikâyetten vazgeçme · suç ikrarı) hiçbiri taranmaz.
Hiçbir yerde "tarama kısmî" uyarısı yoktu.

**Neden bu bir *yanlış güvence*, "sessiz atlama" değil.** Sessiz atlama, yapılmayan işi
hiç anmamaktır. Burada script yapılmayan iş hakkında **olumlu hüküm** kuruyor: *bakmadım*
demesi gerekirken *bakıp bulamadım* diyor. Bu ayrımın hukuki bedeli somuttur — HMK m.188
uyarınca ikrar kesin delildir ve geri alınamaz; teslim zinciri yeşil makbuz kesmişken
dilekçeye giren bir ikrar, davanın kendisini bitirir.

**Onarıldı.** Kapsam artık çıktının **başında** ve iki hâlde de görünür:

```
[D] MÜVEKKİL-ALEYHİ İFADE TARAMASI (anayasal — tek katı sınır)
   [UYARI] TARAMA KISMİ — taraf sıfatı VERİLMEDİ. Yalnız 'genel' kalıp seti tarandı;
           taraf-özel eksenler (kabul/ikrar · feragat · şikayetten vazgeçme · suç
           ikrarı) TARANMADI.
           → --taraf ... VERİP YENİDEN KOŞ; aksi hâlde aşağıdaki sonuç bir TEMİZLİK
             BEYANI DEĞİLDİR.
   [—] taranan DAR kapsamda sinyal yok — bu 'temiz' DEMEK DEĞİLDİR.
```

Taraf verildiğinde ise `[KAPSAM] taranan kalıp setleri: davali, genel` yazılır — hangi
eksenlerin fiilen tarandığı artık okunabilir bir olgudur, varsayım değil.

---

### B3 — Olumsuzlama deseni Türkçe `-me` ekini ayırt etmiyor → **gerçek ikrar susturuluyor** · H2

**Kanıt (izole ölçüm).** `NEG` deseninde `\bkabul\s*etme` **kelime sınırı olmadan** yazılmıştı:

| girdi | eski sonuç |
|---|---|
| `Davayı kabul ediyoruz.` | BLOK (doğru) |
| `Müvekkil borcu kabul **etmektedir** ve davayı kabul ediyoruz.` | **BİLGİ — susar** |
| `Borcun tamamını kabul **etmekteyiz**; davayı kabul ediyoruz.` | **BİLGİ — susar** |
| `Müvekkilin borcu kabul **etmesi** sebebiyle davayı kabul ediyoruz.` | **BİLGİ — susar** |

**Kök neden — dil bilgisi düzeyinde.** Türkçede `-me` iki ayrı ektir: **olumsuzluk** eki
(`kabul etme-mek`) ve **mastar/ad** eki (`kabul etme-si`, `kabul et-mektedir`). Desen
ikisini aynı harf dizisi olarak görüyordu. Sonuç: en yaygın ikrar kalıbı ("… kabul
etmektedir"), bir aleyhe eşleşmenin ±70 karakterlik penceresine düştüğü anda o eşleşmeyi
**BLOK'tan BİLGİ'ye indiriyordu** — yani ikrarın kendisi, ikrarı gizleyen şey oluyordu.

Gerçek olumsuz çekimler zaten ayrı ayrı listelidir (`etmedi[ğg]`, `etmiyor`, `etmemek`,
`etmez`), dolayısıyla `\bkabul\s*etme\b` (kelime sınırlı) daraltması koruma kaybettirmez.

**Onarıldı + ölçüldü.** Aynı taslakta `--taraf davali` artık **3 değil 5** sinyal yakalıyor
("davayı kabul" ve "kabul ediyoruz" BLOK'a döndü). Gerçek olumsuzlama koruması korundu:
*"davanın kabulü anlamına gelmemek kaydıyla"* ve *"kabul etmiyoruz"* hâlâ sinyali düşürüyor
(mevcut dört regresyon testi yeşil kaldı).

---

### B4 — `mudahil` CLI'de var, kalıp sözlüğünde **yok** → doğru kullanımda bile kör tarama · H2

**Kanıt.**

```
ALEYHE anahtarları  : davaci, davali, genel, katilan, musteki, sanik
CLI --taraf choices : davaci, davali, katilan, mudahil, musteki, sanik
KAPSANMAYAN         : mudahil
```

`--taraf mudahil` verilen ikrarlı taslak → `[OK] belirgin müvekkil-aleyhi ifade sinyali
bulunamadı`. **B2'den daha sinsidir:** avukat taraf sıfatını *doğru* verdiği için taramanın
yapıldığını sanır; kör nokta, kullanıcının doğru davranışının arkasına saklanır.

**Onarıldı.** Fer'î müdahil, yanında katıldığı tarafın yardımcısıdır (HMK m.66-69); asli
müdahil kendi hakkını ileri sürer. Script müdahilin hangi tarafta olduğunu **bilemez** →
fail-closed tercih: **her iki eksen de** taranır (`davaci` + `davali` + `genel`). Yanlış
pozitifi avukat gözü eler; yanlış negatif müvekkili batırır. Ayrıca `test_b4_cli_taraf_
secenekleri_ile_kalip_kapsami_AYRISAMAZ` bundan böyle CLI ile kalıp kapsamının ayrışmasını
yapısal olarak yasaklar — aynı boşluk yeni bir sıfat eklendiğinde tekrar açılamaz.

---

### B5 — Hook katmanı: **teşhis aracı, avukatı sistemi kırmaya yönlendiriyordu** · H0

**Olgu.** `plugin.json`'da `"hooks": "./hooks/hooks.json"` satırı yok; onu commit `08441f5`
(2026-09-07, main HEAD) kaldırmış:

> *"…standart yol olduğu için zaten otomatik yüklenen hooks dosyasını ikinci kez
> bildiriyordu. Bu, kurulumda «Duplicate hooks file detected» hatasına ve eklentinin
> (20 skill dâhil) tamamen yüklenememesine yol açıyordu."*

**Çelişki.** Buna karşılık depodaki dört test ve `tools/hook_doktor.py` hâlâ eski sözleşmeyi
zorluyordu; doktor avukata şunu basıyordu:

```
plugin.json hooks: ✗ YOK — hook katmanı hiç kaydolmaz (v0.5.6 arızası)
```

**Dış teyit.** Resmî Claude Code plugin referansı (2026-09-10): *"Location: `hooks/hooks.json`
in plugin root, **or** inline in plugin.json"* — standart konum otomatik keşfedilir;
manifestteki `hooks` alanı **özel yol** ya da **inline tanım** içindir. Yani commit'in
gerekçesi doğrulanıyor: hook'lar ölmemiş, standart yoldan yükleniyor.

**Asıl kırık burada.** Tehlike hook'ların ölmesi değil, **teşhisin ters yönü göstermesiydi.**
Avukat "✗ ARIZA (v0.5.6)" uyarısına uyup satırı geri koysaydı → *Duplicate hooks file
detected* → **eklentinin tamamı, 20 skill dâhil, hiç yüklenmeyecekti.** Yani yanlış alarm,
gerçek arızadan daha yıkıcı bir "onarıma" çağırıyordu. Ayrıca bu dört kırmızı, deponun
kendi *"CI yeşermeden sürüm etiketi atılamaz"* kuralı gereği sürüm hattını kilitli tutuyordu.

**Karar (Av. Bayram Can ÇAPAR, 2026-09-10): sözleşme yeni gerçeğe çevrildi.** Kilitlenen şey
değişmedi — *kaydı düşen hook, olmayan hooktur* — yalnız mekanizması düzeltildi:

- **Eski sözleşme:** manifest `./hooks/hooks.json` bildirmek **zorunda**.
- **Yeni sözleşme:** `hooks/hooks.json` **standart konumda var ve tetik sözlüğü dolu**
  olmalı; manifest onu **yeniden bildirmemeli** (özel/standart-dışı yol bildirimi hâlâ meşru).

`hook_doktor.py` artık doğru yönü gösteriyor ve çift bildirimi *kendisi* arıza sayıyor:

```
plugin.json hooks: ✓ bildirim YOK — doğru; hooks/hooks.json standart konumdan
                   otomatik yüklenir (çift bildirim eklentiyi öldürür)
[2] hooks.json   : ✓ 6 olay kayıtlı (SessionStart, UserPromptSubmit, PreToolUse,
                     PostToolUse, Stop, SessionEnd)
```

---

### B6 — İŞ MAHKEMELERİ EKSENİ: müvekkili bitiren ikrarların HİÇBİRİ yakalanmıyordu · H2

**Nasıl test edildi.** Avukatın kendi dosyalarına (İndirilenler klasörü) bu oturumdan
erişim yoktur — oturum bulutta izole bir konteynerde koşuyor. Bu yüzden test, *gerçek
dosya* yerine **gerçek ve güncel kaynak** üzerinden kuruldu: Yargı Pro MCP'den çekilen
Yargıtay 9. Hukuk Dairesi kararları, iş mahkemesi vakalarının somut tarihleri ve iş
hukukunun kendi ikrar dili.

**Önce doğrulama — süre motoru gerçek Yargıtay vakalarında sınandı (GEÇTİ).**

| Vaka | Motor | Mahkeme kararındaki son gün |
|---|---|---|
| **Y. 9. HD E.2016/10425 K.2017/8620** — ikale 29.08.2015, 1 aylık hak düşürücü süre | `2015-09-29` | **29.09.2015** (Yargıtay); ilk derece "30 Eylül" demişti ve Yargıtay bunu *"yasanın düzenlemesine **açıkça aykırı**"* buldu |
| Arabuluculuk son tutanağı 27.11.2018 + 2 hafta | `2018-12-11` | 11.12.2018 |
| Avanos vakası: 09.01.2019 + 2 hafta | `2019-01-23` | 23.01.2019 |
| Adıyaman vakası: 07.03.2018 + 2 hafta | `2018-03-21` | 21.03.2018 |

Motor 4/4 doğru. Özellikle birincisi anlamlı: **HMK m.92'nin ay hesabında ilk derece
mahkemesinin düştüğü hatayı motor yapmıyor** (`_ay_ekle` tebliğ gününe denk gelen günü
verir, ertesi günü değil).

**Sonra kırık — teslim öncesi son kapı iş hukukunu hiç tanımıyordu.** İş davasında
müvekkili bitiren ikrar, genel medeni usul dilinde ("kabul ediyoruz", "feragat") değil,
**iş hukukunun kendi dilinde** gelir. Ölçüm:

```
İŞÇİ (davacı) yanı  : 0/7 yakalandı
İŞVEREN (davalı) yanı: 0/5 yakalandı
```

Kaçan yedi işçi-yanı ikrar ve her birinin bedeli:

| İfade | Sonuç |
|---|---|
| "istifa etmiştir" | fesih işçiye ait olur → **kıdem + ihbar düşer** (4857 m.17, m.120) |
| "kendi isteğiyle ayrılması" | işveren feshi yok → tazminat yok |
| "ibranameyi imzalamıştır" | alacakların ibrası (TBK m.420) |
| "ikale sözleşmesi imzalanarak" | **işe iade hakkı ve tazminatlar ortadan kalkar** |
| "alacağı kalmamıştır" | dava konusuz kalır |
| "devamsızlık yapmıştır" | işverenin haklı fesih sebebi (4857 m.25/II-g) |
| "feshin haklı sebebe dayandığı" | işe iade + tazminat talepleri çöker |

İşveren yanında da beş ikrar kaçıyordu: haksız fesih, kıdeme hak kazanma, ödenmemiş fazla
mesai, sigortasız çalıştırma, ihbar önelime uyulmaması.

**Bu boşluk sistemin kendi içinde bir asimetriydi.** `oa-alan` parçası iş hukukunu
**biliyor** — `references/unsur-sablonlari/ise-iade.md` (4857 m.18-21) ve `kidem-ihbar.md`
şablonları mevcut. Yani sistem davayı kurarken iş hukukunu tanıyor, ama **teslim öncesi
son kapı** onu tanımıyordu.

**Onarıldı.** İki yeni taraf-asimetrik eksen eklendi (`_ALEYHE_IS_ISCI_YANI`,
`_ALEYHE_IS_ISVEREN_YANI`). Asimetri kasıtlıdır: *"istifa etti"* bir **işveren** vekili
dilekçesinde müvekkil **lehinedir** ve orada taranmaz; *"haksız fesih"* bir **işçi**
vekili dilekçesinde lehedir ve orada taranmaz.

**Neden opsiyonel bir `--alan is` bayrağına bağlanmadı:** aynı denetimin **B2** bulgusu,
taramayı isteğe bağlı bir bayrağa bağlamanın onu sessizce kör bıraktığını gösterdi.
Kalıplar doğrudan taraf setlerine eklendi; yanlış-pozitifi avukat gözü eler ([UYARI]
sınıfı, BLOK değil), yanlış-negatif müvekkili batırır.

**Türkçe morfoloji çıpası — B3'ün akrabası.** İlk yazımda iki kalıp kaçıyordu ve sebebi
öğreticiydi: **ünlü düşmesi** (`fesih` → `fes**h**in`) ve **ünsüz yumuşaması** (`sebep` →
`sebe**b**e`). B3'te `-me` ekinin iki işlevi neyse, bu da odur: Türkçe çekim, kalıbı
sessizce ıskalatır. Ayrıca tüm kalıplar **OCR bozulmasına** karşı toleranslı yazıldı
(`[ıi]`, `[sş]`, `[gğ]`) — sistem OCR'dan geçmiş evrakla çalışıyor ve ailenin mevcut
konvansiyonu da budur.

**Onarım sonrası ölçüm:**

```
İŞÇİ    — Türkçe 7/7 · OCR bozulmuş 7/7
İŞVEREN — Türkçe 5/5 · OCR bozulmuş 5/5   → TOPLAM 24/24
Ters-taraf yanlış alarm: 0/4 (davali·davaci·musteki·sanik tümü temiz)
```

29 yeni kilit (`test_v0517_...` B6 bloğu). Kilitlerin tuttuğu doğrulandı: eksen geçici
geri alındığında **25 test kırmızı** yanıyor.

### B7 — İş hukuku süre kuralı kural tabanında YOK (bulgu — onarılmadı, kapsam kararı sizin)

`hesapla_sure.py` kural tabanında **21 kural** var ve **hiçbiri iş hukuku değil**
(HMK/CMK/İYUK/İİK/AYM). Yani avukat `--kural ise_iade` diyemez.

**İyi haber — fail-closed:** bilinmeyen kural `argparse choices` ile **reddediliyor**;
sistem sessizce yanlış hesap yapmıyor, hata verip duruyor. Kırık değil, **kapsam boşluğu**.

Eklenmeye aday, iş mahkemelerinde en sık ıskalanan üç süre:

1. **İşe iade — arabulucuya başvuru:** fesih bildiriminin tebliğinden **1 ay** (4857 m.20/1,
   7036 s.K. m.11 ile değişik).
2. **İşe iade — dava:** arabuluculuk **son tutanağından 2 hafta** içinde iş mahkemesinde
   dava (4857 m.20/1). ⚠️ **Başlangıcı TARTIŞMALIDIR** — aşağıya bakınız.
3. **İşe başlatma başvurusu:** kesinleşen kararın tebliğinden **10 İŞ GÜNÜ** (4857 m.21/5).
   ⚠️ Motor **"iş günü" birimini tanımıyor** (`gun|hafta|ay|yil`); `--birim gun` takvim
   günü sayar ve **erken** (dolayısıyla güvenli ama dar) bir tarih verir. Bu bir birim
   eksikliğidir; tatil tablosu zaten mevcut olduğundan eklenmesi teknik olarak küçüktür.

**Tartışmalı başlangıç — güncel içtihat durumu (Yargı Pro, 2026-09-10):**
Yargıtay 9. HD **E.2024/10170 K.2024/14797 (18.11.2024)** kararında, işe iade davasındaki
iki haftalık sürenin ne zaman başlayacağına dair BAM daireleri arasındaki uyuşmazlık
incelendi ve **"uyuşmazlığın giderilmesine YER OLMADIĞINA"** karar verildi (usulden: 29. HD
kararı nihai/kesin nitelikte değildi). Yani **ayrılık sürüyor**:

- **İstanbul BAM 31. HD** (2020/2741 E., 2021/10 K.): son tutanağın **düzenlendiği tarih**
  esastır; imza tarihi ya da telekonferansla katılım önemsizdir; süre hak düşürücüdür ve
  resen gözetilir.
- **İstanbul BAM 29. HD** (2024/502 E., 2024/919 K.): tutanakta imza/imza tarihi yoksa,
  **tüm imzaların tamamlandığı tarih** düzenlenme tarihi sayılır.

Aynı dosyada anılan çok sayıda BAM kararı ise *"hak düşürücü sürelerde tereddüt hâlinde,
aleyhine süre konulan kişi lehine yorum"* ilkesiyle **işçi lehine** geç tarihi kabul etmiştir.

**Avukat için operatif sonuç — motorun A-20 mantığıyla aynı:** güvenli plan **erken**
tarihtir (son tutanağın düzenlenme tarihi); imzaların tamamlanması ya da tebliğe dayalı
geç tarih yalnız **ikincil savunma** olarak tutulmalıdır. Bir kural eklenecekse uyarı
metninin bu ayrılığı taşıması gerekir — çünkü burada "doğru hesap" tek başına yetmez,
**hangi olaya bağlandığı** belirleyicidir.

### B8 — [F] kapısı dilekçenin KENDİ dosya numarasını çıplak künye sayıyordu · H0

**Nasıl bulundu.** Backend, Yargı Pro'nun **gerçek verisiyle** uçtan uca sınandı: gerçek
kararlar çekildi, teyit kütüğüne işlendi, dilekçeye kondu ve kapılar koşturuldu. Sentetik
test verisinin göremediği şey buydu.

**Önce — çalışan her şey (gerçek veriyle doğrulandı):**

| Test | Sonuç |
|---|---|
| Künye ayrıştırma — 10 farklı merci biçimi (HGK · daire · BAM · Danıştay · AYM BB · iyelik/sonek/sıkışık yazımlar) | **10/10**, ayrıştırılamayan 0 |
| AYM bireysel başvurusu (`B. No: 2021/58970`) | doğru: `kunye_turu=aym_bb`, karar no yok (6216 m.45-49) |
| **Halüsinasyon kapısı** — döküm metninde geçmeyen alıntı | **RET** (exit 1): *"özet/parafraz kabul edilmez"* |
| Damgasız GETİR kaydı | **RET** (exit 1) |
| DAVAYA-BAĞ < 40 karakter | **RET** (exit 1) |
| LEHE damgalı gerçek künye dilekçede | **[OK]**, kütük kaydına bağlandı |
| Gerçek çıplak künye (kütükte yok) | **BLOK** |
| **ALEYHE damgalı künye dilekçede** | **BLOK** — *"anayasa m.6 — müvekkil-aleyhi dış çıktı yasağı"* |

**Sonra — kırık.** Geçerli, tam kurallı bir dilekçe [F] kapısından **geçemedi**:

```
[BLOK] (satır 5) 2026/100 E.  (E. 2026/100 / K. — / Daire: belirtilmemiş)
       ✗ Bu künye için hiçbir _oa/cikti/*ictihat-muhakeme*.md kaydı yok
         (çıplak/muhakeme edilmemiş atıf) — dilekçede çıplak künye kalamaz
```

Satır 5, dilekçenin **kendi künye bloğu**: `DOSYA NO : 2026/100 E.`

**İlliyet — düzeltilmiş bir hatanın kardeş kapıda hayatta kalması.** Bu, CHANGELOG'da
anılan **346 sahasının tek ayrıştırıcı yanlış-pozitifi**dir ("taslağın kendi DOSYA NO
satırını karşı-atıf sanması") ve o gün *"tek bir ayrıştırıcı yanlış-pozitifi yeşil makbuzu
imkânsız kıldı"* diye kayda geçmişti. Muafiyet yazıldı — ama yalnız **iki** yere:

| Dosya | `KENDI_DOSYA_SATIR_RE` muafiyeti |
|---|---|
| `kunye_ortak.py` (`ayristirilamayan_atiflar`) | ✅ var |
| `kunye_teyit.py` (`kendi_dosya_no_ayikla`) | ✅ var |
| **`ictihat_muhakeme_denetim.py`** (`taslaktaki_atiflari_bul` → [G2]) | ❌ **yok** |

`kunye_ortak.py`'deki tanımın başında *"TEK KAYNAK burasıdır; `kunye_teyit.py` bu tanımı
kullanır"* yazıyordu — cümle, kardeş kapıyı hiç anmıyor. Tek kaynak ilan edilmiş ama
**tek tüketici** varsayılmıştı.

**Neden yanlış-pozitif bir kapı, kapalı bir kapıdan tehlikeli olabilir.** Bu kırık
müvekkile doğrudan zarar vermiyor: sahte bir engel üretiyor. Ama sistemin bütün mimarisi
"kapıya güven" üzerine kurulu ve `--serh` ile gerekçeli geçiş meşru bir yol. Geçerli
dilekçelerini düzenli olarak sahte engelle karşılayan bir avukat, kapıyı şerhle geçmeye
**alışır** — ve o alışkanlık, sıra **gerçek** bir çıplak künyeye geldiğinde de işler.
Yanlış-pozitif, kapıyı doğrudan değil, ona duyulan güveni aşındırarak açar.

**Onarıldı.** Muafiyet gerçekten tek kaynağa taşındı: `kunye_ortak.kendi_dosya_no_mu()`
(+ `satir_metni_no()`), ve [F] kapısının `taslaktaki_atiflari_bul()` fonksiyonuna bağlandı.
Muafiyet **dar** ve fail-closed — dört şart birden aranır: (1) özel künye türü değil
(AYM BB / AİHM gerçek atıftır), (2) E.+K. çifti tam değil, (3) daire/merci anılmıyor,
(4) satır `DOSYA NO` / `ESAS NO` / `MERCİ` etiketiyle başlıyor.

**Onarımın kapıyı gevşetmediği ayrıca ölçüldü:**

| Negatif test | Sonuç |
|---|---|
| Gerçek çıplak künye (22. HD, kütükte yok) | **BLOK** ✅ |
| `DOSYA NO` satırında **tam** künye + daire (`Yargıtay 4. HD E. 2019/1111 K. 2020/2222`) | **BLOK** ✅ (muafiyet kapsamadı) |
| ALEYHE damgalı künye | **BLOK** ✅ |
| Geçerli LEHE künye + kendi dosya no | **exit 0** ✅ |

6 yeni kilit; onarım geri alındığında **4 test kırmızı** yanıyor. `test_b8_muafiyet_KAPIYI_
GEVSETMEZ_tam_kunye_hala_yakalanir` bundan böyle muafiyetin genişlemesini yapısal olarak
yasaklar.

## 2. Kırık BULUNMAYAN hatlar (negatif bulgular — dürüst kayıt)

**H1 — SÜRE / HAK KAYBI: temiz.** `hesapla_sure.py` sınır senaryolarında fiilen koşturuldu:
adli tatilin ilk günü (20 Tem) ve son günü (31 Ağu), tatil öncesi/sonrası, ceza CMK m.331/4
üç günlük uzatma (3 Eyl), hukuk HMK m.104 bir hafta (7 Eyl), idari İYUK m.8/3 yedi gün
(7 Eyl), 31 Ocak → Şubat ay ekleme, artık yıl 29 Şubat → 28 Şubat, yıl geçişi. Hepsi doğru.

Dikkate değer bir davranış: ham bitişi 19 Temmuz (Pazar) olan bir süre, HMK m.93 kaymasıyla
**20 Temmuz'a** — adli tatilin ilk gününe — düşüyor ve uzatma uygulanmıyor. Bu, uzatmayı
*ham bitişe* bağlayan yorumdur ve **güvenli taraftır**: erken tarih hak kaybettirmez, geç
tarih kaybettirir. Motor bilinçli olarak doğru tarafta duruyor.

**H3 — GİZLİLİK: temiz.** `gizlilik_tara.py` fail-closed: checksum tutmayan TCKN/kart dizileri
düşürülmüyor, "olası" düzeyinde işaretleniyor (OCR ile bozulmuş gerçek kimlik kaçmasın diye).
IBAN deseni B-15'te 26 karaktere düzeltilmiş ve doğru.

**Latent not (aktif bug değil, dayanıklılık kalemi):** `_MASKE` listesi IBAN desenine
`MUTLAK_DENY[4]` diye **konum üzerinden** bağlı. Listeye eleman eklenir ya da sıra
değişirse maske yanlış deseni maskeler ve **IBAN maskesiz kalır**. Bugün indeks doğru;
ada göre aramak bu bağı kırılgan olmaktan çıkarır. Avukatın kararına bırakıldı.

---

## 3. Ölçüm

| Kalem | Önce | Sonra |
|---|---|---|
| Python 3.11'de derlenmeyen script | 1 (`tam_tur.py`) | 0 |
| Süit toplama | 2318 | **2329** (+11 yeni kilit) |
| Hook katmanı kırmızısı | 4 | 0 |
| İkrarlı taslakta yakalanan sinyal (`--taraf davali`) | 3 | **5** |
| İkrarlı taslakta `--taraf`sız çıktı | `[OK] bulunamadı` | `TARAMA KISMİ` + "temiz DEMEK DEĞİLDİR" |

**Nihai koşu — CI hedef sürümünde (Python 3.12, `requirements.txt` tam):**

```
2314 passed, 15 skipped in 306.34s        →  2314 + 15 = 2329  (işaretçi tam)
aile_dogrula.py  → Denetlenen parça: 20 · AİLE YAPI DENETİMİ TEMİZ.
hook_doktor.py   → exit 0 · altı olayın altısı da ✓
```

**Sıfır kırmızı.** (Python **3.11**'de koşulduğunda tek bir kırmızı kalıyor:
`test_cf_regexi_unicodedata_ile_birebir`, U+13439–U+1343F yedi kod noktasında ayrışıyor.
Bu bir depo kırığı DEĞİL, Unicode sürüm farkıdır: bu karakterler Unicode 15.0'da `Cf`
oldu; Python 3.11 Unicode **14.0** taşır, 3.12 **15.0**, 3.13 **15.1**. Testin kendi
docstring'i bu durumu zaten öngörmüştü. İlginç biçimde bu kırmızı, B1'de düzeltilen
`>=3.12` sınırının **bağımsız bir teyidi** oldu: depo gerçekten 3.12+ ister ve README'nin
"3.10+" beyanı ölçülmemiş bir beyandı.)

Not: `pymupdf`/`pillow` kurulu değilken süit 2314 **topluyordu** (2329 değil); 2318 beyanı
doğruydu, eksik olan bağımlılıklardı (`requirements.txt`). Bu, işaretçinin yanlış olduğu
izlenimini veren ikinci dereceden bir tuzaktı ve ölçümle elendi — beyan değil ölçüm.

---

## 4. Canlı doğrulama — avukatın kendi makinesinde (mekanik test bunu ikame edemez)

`hook_doktor.py`'nin kendi [4] notunun dediği gibi: hook katmanının sağlamlığı, süreç
tazeliğinden bağımsız kanıtlanamaz. B5 kararının canlı teyidi için, kendi makinenizde:

1. Eklentiyi güncelleyin ve **Claude Code'u tam kapatıp yeniden açın** (bayat süreç tuzağı).
2. Kurulum sırasında **"Duplicate hooks file detected"** uyarısının **çıkmadığını** görün.
3. Eklentinin **20 skill'inin de** listelendiğini doğrulayın (çift bildirim varsa hiçbiri gelmez).
4. Bir dava klasöründe `python tools/hook_doktor.py` koşun — `[1b]` satırı artık
   *"✓ bildirim YOK — doğru"* demeli, `[2]` altı olayı saymalı, `[3]` altı olayın altısı da
   `exit 0` vermeli.
5. Bir dosyaya Write/Edit yapıp **PostToolUse** tetiğinin fiilen ateşlediğini gözleyin
   (hook katmanının canlı olduğunun tek gerçek kanıtı budur).

Bu beş adım yeşilse B5 kararı sahada da kapanmış olur.

---

## 5. Açık kalan / avukat kararı bekleyen

- **`_MASKE` indeks bağı** (yukarıda): ada göre arama önerisi — uygulanmadı, karar sizin.
- **Sürüm damgası artırılmadı.** Bu dal bir denetim + onarım dalıdır; `plugin.json` /
  `marketplace.json` / `pipeline_kayit.py` / `teslim_paketi.py` OA_SURUM damgaları
  **birlikte** artar kuralı gereği, sürüm kararı ve CHANGELOG sürüm girişi size aittir.
- **Ceza adli tatilinde lafız tartışması:** CMK m.331/4 *"adlî tatile **rastlayan** süreler
  işlemez"* der; script uzatmayı (yerleşik uygulamayla uyumlu olarak) yalnız **bitişi**
  tatile rastlayan sürelere uyguluyor. Sürenin bir *kısmı* tatile rastladığında da işlemeyeceği
  yönündeki lafzî yorum daha geniş bir sonuç verirdi. Bu bir kod kırığı değil, hukuki
  yorum tercihidir ve bilinçli olduğu için değiştirilmedi — kayda geçirilmiştir.

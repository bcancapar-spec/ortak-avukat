# PERFORMANS-STATUS — Oturum Kaydı ve Ölçüm Defteri

**Oturum:** PC hızlandırma + Ortak Avukat sistem optimizasyonu
**Tarih:** 2026-09-10 · **Dal:** `claude/pc-optimization-performance-r2n435`
**Karar verici:** Av. Bayram Can ÇAPAR
**Kayıt kuralı:** Bu dosya oturum boyunca güncellenir. `STATUS.md`'ye
DOKUNULMAZ (o deponun kendi durum defteri — üzerine yazmak veri kaybı olurdu).

---

## 0. ÖNCE DÜRÜSTLÜK: NEYİ İNCELEYEBİLDİM, NEYİ İNCELEYEMEDİM

**Bu oturum uzak (remote) bir bulut konteynerinde koştu — sizin fiziki
bilgisayarınızda değil.** Verdiğiniz "pc use" yetkisi bu oturuma
bilgisayarınızın işletim sistemine erişim sağlamıyor; sağlayamaz, çünkü kod
başka bir makinede çalışıyor.

| | Bu oturumun gördüğü | Sizin PC'niz |
|---|---|---|
| Ortam | Ubuntu 24.04, KVM sanal makine | Windows (masaüstü Claude Code) |
| İşlemci | 4 vCPU Intel Xeon @2.10GHz | bilinmiyor — ölçülmedi |
| RAM | 15 GiB | bilinmiyor — ölçülmedi |

Bu yüzden iş iki parçaya ayrıldı:

1. **Ölçülmüş ve uygulanmış:** Ortak Avukat'ın kendi kod yolundaki gecikme.
   Burada ölçüldü, düzeltildi, testle kilitlendi. Sizin PC'nizde de aynen
   kazanca döner — çünkü yavaşlığın kaynağı donanım değil, kodun her hook'ta
   yaptığı gereksiz iş.
2. **Sizin PC'nizde koşmanız için hazırlanan:** `tools/pc_hizlandir.ps1`
   (teşhis → uygula → geri al) ve `tools/hook_olc.py` (ölçüm). Hiçbiri kör
   tavsiye değil; her adımın gerekçesi, riski ve geri alma yolu yazılı.

Windows olduğunuz depodan kanıtlı: `run-hook.cmd` polyglot sarmalayıcısı,
`STATUS.md:294` (cp1254 konsol), `STATUS.md:150` (masaüstü uygulaması hook'u
kabuksuz koşturuyor).

---

## 1. ÖLÇÜM METODOLOJİSİ — ve ilk ölçümümün NEDEN YANLIŞ olduğu

Bu bölüm kayda geçirilmiştir çünkü **ilk ölçümüm hatalıydı** ve hatanın
sebebi öğreticidir. Üç tuzağa düştüm; üçü de artık `tools/hook_olc.py`
içinde kapatılmıştır.

### Tuzak 1 — DEDUP KISA DEVRESİ (en yıkıcı)

`pipeline_kayit.py:_hook_dedup_kisa_devre` aynı olayı **aynı saniye içinde**
ikinci kez yan-etkisiz kısa devre yapar; `prompt` için ayırt edici `None`'dır
(anahtar yalnız olay adı). İlk ölçümlerimi 20 tekrarlı **sıkı bir döngüde**
yaptım — yani çağrıların çoğu NO-OP'tu.

Ölçüm (gerçek dava kökü, `--hook-prompt`):

| | süre |
|---|---|
| aralıksız 5 çağrı | 56, 57, 251, 56, 667 ms — kısa devre + gerçek iş karışık |
| 1.1 sn arayla 3 çağrı | 210, 221, 373 ms — **her seferinde gerçek iş** |

→ `hook_olc.py` artık her çağrı arasında `--bekle` (varsayılan 1.1 sn) bekler
ve boş çıktılı (kısa devre olası) çağrıları ayrı sayar.

### Tuzak 2 — BOŞ KLASÖR TABANI

İlk ölçümlerimi boş bir geçici kökte yaptım. Boş kökte hook neredeyse hiç iş
yapmaz: `_oa/` yoktur, kapılar erken çıkar. **Gerçek maliyeti belirleyen şey
modül yükleme değil, dava kökündeki dosya sistemi işidir.**

→ `hook_olc.py --gercekci` temsilî bir dava kökü kurar (40 evrak + defter +
`_oa/cikti` metin ürünleri + **ikili ürünler**: 3 MB PDF, 400 KB UDF).

### Tuzak 3 — YANLIŞ HEDEF

Aracım doğrudan `pipeline_kayit.py`'yi ölçüyordu; oysa `run-hook.cmd` artık
`hook_giris.py` çağırıyor. Yani **terk edilmiş yolu** ölçüyordum. Ayrıca
`main`'de `hook_giris.py` olmadığı için import dökümü sessizce boş dönüp
yanlışlıkla "ağır modül YOK" diyordu — bir dürüstlük kusuru, düzeltildi
(döküm alınamazsa artık AÇIKÇA "DÖKÜM ALINAMADI" der).

**Ders:** Bir ölçüm aracı, ölçtüğü sistemin kendi optimizasyonlarını
(dedup, erken çıkış) tanımıyorsa kendi kendini yalanlar.

---

## 2. ÖLÇÜLEN SONUÇ (düzeltilmiş, elmayla-elma)

Koşullar: `main` dalı vs bu dal · **aynı** ölçüm aracı · gerçekçi dava kökü ·
dedup yenilmiş (1.1 sn ara) · Python 3.12.3 · 4 vCPU Xeon 2.10GHz · sıcak
sayfa önbelleği. Ortanca değerler.

| Hook modu | ÖNCE (`main`) | SONRA | kazanç |
|---|---|---|---|
| `hook-prompt` (her kullanıcı turu) | 239.4 ms | **46.4 ms** | −80.6% |
| `hook-pretool` (her Write/Edit/Bash) | 232.7 ms | **40.4 ms** | −82.6% |
| `hook-postwrite` | 931.5 ms | **77.8 ms** | −91.6% |
| `hook-denetle` (Stop + SessionEnd) | 935.3 ms | **77.1 ms** | −91.8% |
| `hook-acilis` (SessionStart) | 248.3 ms | **42.4 ms** | −82.9% |
| **Bir `Write` (Pre+Post birlikte)** | **1164.2 ms** | **118.1 ms** | **−89.9% · 9.86×** |
| Sıcak yolda ağır modül | **11** (pymupdf dahil) | **0** | — |
| Test süiti (`-n auto`, 4 çekirdek) | 94.8 s | **43.0 s** | −54.6% |
| Test süiti (seri) | 259.1 s | — | `-n auto` ile 6.0× |

`hooks.json`'da **Stop ve SessionEnd aynı `hook-denetle` moduna bağlı** —
yani oturum kapanışında o bedel iki kez ödeniyordu: ~1.87 s → ~0.15 s.

### İlk raporumun düzeltmesi

PR #5'in ilk gövdesinde "189.7 ms → 26.9 ms" yazmıştım. O sayı **boş
klasörde, dedup'a yakalanmış sıkı bir döngüyle** alınmıştı; hem yöntemi
geçersizdi hem de gerçek kazancı **olduğundan küçük** gösteriyordu. Yukarıdaki
tablo geçerli olandır.

---

## 3. KÖK NEDENLER (illiyet zinciri)

### KN-1 — Tek bir string sabiti için PDF kütüphanesi yükleniyordu

`trace` + `-X importtime` ile doğrulanmış zincir:

```
hook_prompt / hook_denetle
  └─ _sozlesme_disi_uyarisi / _denetle_hesapla
      └─ _sozlesme_disi_dizinler()
          └─ _dizin_beyaz_liste()
              └─ _oa_ingest_modulu_beyaz_liste()
                  └─ oa_ingest.py'yi exec_module ile TAM YÜRÜTÜR (1716 satır)
                      └─ subprocess · zipfile · concurrent.futures
                         → multiprocessing, logging, enum
                      └─ pymupdf  ← 78-86 ms  ★ asıl bedel
                      └─ PIL.Image ← 7-8 ms
```

Zincirin **tek amacı** `ONBAKIS_DIZIN` sabitini okumaktı
(`oa_ingest.py:275` → `"metin-onbakis"`). Tasarım niyeti doğruydu (DRY /
tek kaynak, "ikiz liste" yasağı); bedeli ölçülmemişti.

**Yanlış çözümüm (v0.5.16.2):** hesabı tembelleştirdim. Bu maliyeti
**kaldırmadı, erteledi** — ve gerçek dava klasöründe o dal her zaman
koştuğu için hiçbir şey kazandırmadı. Çok-ajanlı denetim bunu yakaladı.

**Doğru çözüm (v0.5.16.3):** sabit, modül **hiç yürütülmeden**, dosyadan
satır okunarak alınır (`_oa_ingest_sabit_oku`). Tek-kaynak garantisi aynen
korunur: değer hâlâ çalışma anında `oa_ingest.py`'den gelir, koda gömülmez.
Sabit basit bir string literali değilse desen eşleşmez ve **tam import
yedeğine** düşülür — yanlış değer üretmek yapısal olarak imkânsız.

### KN-2 — Bytecode önbelleği hiç kullanılmıyordu

Python, `__main__` olarak koşan bir betiğin bytecode'unu **asla** önbelleğe
almaz; `__pycache__` yalnızca *import edilen* modüller için çalışır. Hook ağı
`pipeline_kayit.py`'yi doğrudan çağırdığı için **6300+ satır her ateşlemede
yeniden derleniyordu.**

Çözüm: `hook_giris.py` modülü importlib ile yükleyip `main()` çağırır.
Ölçüm (gerçekçi kök, mod ortalaması): giriş betiği doğrudan yoldan
**~38-46 ms** daha hızlı.

### KN-3 — 3 MB'lık PDF, utf-8'e çözülüp regex'e sokuluyordu

`_dilekce_sekilli_makbuzsuz_uyarisi` (özyinelemeli) ve `_kutuk_dilekce_sayaci`
(özyinelemesiz) `_oa/cikti`'daki **her dosyayı** uzantı süzgeci olmadan
`f.read()` ile tam okuyordu. Bir dava kökünde orada `ek-deliller.pdf` (3 MB)
ve `TASLAK.udf` (400 KB) gibi **ikili ürünler** durur.

Çözüm: `_ikili_urun_mu()` süzgeci. **Kapının kararı değişmedi** — zip/ikili
bir dosyanın utf-8-replace çözümü `DAVACI:` / `NETİCE-İ TALEP` gibi Türkçe
hukuk kalıplarını üretemez; bu dosyalar bugün de eşleşmiyordu, sadece
eşleşmedikleri pahalıya anlaşılıyordu. Metin dosyaları **aynen tam** okunur:
bilinçli olarak bayt eşiği/kırpma getirilmedi (uzun bir dilekçenin
`NETİCE-İ TALEP` bölümü 20 KB'ı aşabilir; kırpma kapıyı kör edebilirdi).

### KN-4 — Ölü import

`oa_ingest.py:243` `import xml.etree.ElementTree as ET` — bu dosyada `ET.`
kullanımı **sıfır**. (Benim ilk sayımım "43 kullanım" demişti; o naif bir
alt-dize sayımıydı, `ETİKETLERİ` gibi Türkçe kelimeleri sayıyordu. Ajan
doğruyu buldu.) Bedeli soğuk süreçte 8.7 ms.

---

## 4. ÇOK-AJANLI DENETİM SONUCU

7 boyutta paralel analiz + her boyut için çelişmeli doğrulama (14 ajan):

| | sayı |
|---|---|
| Toplam bulgu | 103 |
| Toplam hüküm | 101 |
| Güvenle uygulanabilir | 56 |
| Dikkat gerekli (veri/davranış riski) | 27 |
| **Çelişmeli doğrulamada REDDEDİLEN** | **18** |

Reddedilenler arasında **benim de düşebileceğim hurafeler** vardı ve
`pc_hizlandir.ps1`'in "REDDEDİLENLER" bölümüne gerekçesiyle yazıldı:
`-X frozen_modules` (3.11+ zaten donmuş modül kullanıyor), `fsutil
disablelastaccess` (Windows 10 1803+ zaten kapalı), NTFS 8.3 / klasör
sıkıştırma, çekirdek park etme, WSL2, `python -S`, VBS/HVCI kapatma.

Bu oturumda **uygulanan** ajan bulguları: KN-1'in gerçek çözümü, KN-3, KN-4,
ölçüm aracının üç tuzağı, `hook_giris.py` çift-yan-etki kapısı, taze kurulum
`.pyc` uçurumu (compileall), `PYTHONUTF8` eleştirisi, CFA veri kaybı riski.

---

## 5. VERİ BÜTÜNLÜĞÜ BULGUSU (hızdan önce gelir)

**Denetimli Klasör Erişimi (Controlled Folder Access)** açıkken, tanınmayan
bir sürecin Belgeler/Masaüstü altına yazması engellenir. Hook yolunda yazan
süreç `python.exe`'dir ve dava klasörleri tipik olarak Belgeler altındadır.
Engellenirse append-only deftere olay **hiç yazılmaz** ve üst katmanlardaki
"hatayı yut" desenleri yüzünden bu **sessiz** kalabilir.

`pc_hizlandir.ps1` artık CFA durumunu teşhis eder ve çözümü gösterir
(`-ControlledFolderAccessAllowedApplications` ile `python.exe`'yi izinli
yapmak — CFA'yı kapatmadan). Betik bunu **kendi başına yapmaz**: izinli
uygulama listesi bir güvenlik kararıdır, karar vericiye aittir.

---

## 6. DEĞİŞMEZ KISIT — SIFIR VERİ KAYBI (uygulandı)

Hiçbiri zayıflatılmadı, hepsi testle kilitlendi:

- `_oa/defter/pipeline-olaylar.jsonl` — append-only olay defteri, gerçeğin
  kaynağı. **Dokunulmadı.**
- Atomik `replace` ile türetilmiş görünüm tazeleme. **Dokunulmadı.**
- Dosya kilitleri (`fcntl` / `msvcrt`). **Dokunulmadı.**
- "Kanıtla yazılır" kapıları, GATE G. **Dokunulmadı.**
- Çıkış kodu aktarımı: `--denetle` → exit 1 testle doğrulandı (giriş betiği
  `SystemExit`'i yutmuyor — `BaseException`'dır).
- Kapı kararı eşitliği: ikili süzgecin kapı kararını değiştirmediği testle
  kilitli.
- Test atlanmadı / devre dışı bırakılmadı / karantinaya alınmadı.

---

## 7. DURUM

| Aşama | Durum |
|---|---|
| Depo keşfi + yığın tespiti | ✅ |
| Sıcak yol profillemesi (`trace`, `-X importtime`, cProfile) | ✅ |
| 7 boyutlu çok-ajanlı denetim + çelişmeli doğrulama | ✅ |
| KN-1 (sabit okuma) · KN-2 (bytecode) · KN-3 (ikili süzgeç) · KN-4 (ölü import) | ✅ uygulandı |
| Ölçüm aracının üç tuzağı | ✅ kapatıldı |
| Dürüst A/B (main vs dal, aynı araç, gerçekçi kök) | ✅ |
| Test süiti — sıfır regresyon | ✅ 4 başarısız (önceden var) / 2318 geçti |
| Yeni testler (19: hook_giris 10 + sıcak yol 9) | ✅ |
| Windows betiği — gerçek PowerShell ayrıştırıcısıyla doğrulandı | ✅ |
| `-Uygula` sizin makinenizde koşulması | ⏳ **size ait** |

---

## 8. KARAR BEKLEYEN İKİ KONU (değiştirilmedi)

1. **Önceden var olan 4 kırmızı test.** `main`'de de kırmızı: `08441f5`
   commit'i `plugin.json`'dan `hooks` alanını kaldırdı, testler hâlâ şart
   koşuyor. `hooks` geri mi konacak, testler mi güncellenecek?
2. **`run-hook.cmd` platform asimetrisi.** Windows kolu çıkış kodunu yutuyor
   (`exit /b 0`), bash kolu `exec` ile aktarıyor. `Stop` hook'undaki
   `--hook-denetle` exit 1'i Linux'ta bloklar, Windows'ta bloklamaz.
   Dosyanın kendi açıklaması "hook ASLA bloklamaz" dediği için Windows
   davranışı kasıtlı olabilir — ama o zaman iki platform farklı kapı
   semantiği taşıyor.

İkisi de davranış kararıdır; **Av. Bayram Can ÇAPAR**'a aittir.

---

## 9. İKİNCİ TUR (v0.5.16.4) — ajan iddialarının kendi denetimi

Birinci turun bıraktığı beş bulgu tek tek **kendim ölçüldü**. Üçü
doğrulanmadı; ikisi doğrulandı ve düzeltildi. Ajan çıktısı hüküm değil,
hipotezdir.

| Ajan iddiası | Kendi ölçümüm | Sonuç |
|---|---|---|
| "Defter tek Stop hook'unda **4 kez** taranıyor" | 11 olaylı gerçek defter: `olaylari_oku` **2 kez**, `derle` 1 kez | ❌ **doğrulanmadı** |
| "`_eklenti_script_indeksi()` önbelleksiz, çağrı başına 21 `os.listdir`" | `hook-denetle` yolunda **0 kez** çağrılıyor | ❌ **bu yolda alakasız** |
| "`oa_metrik` → `pipeline_kayit` ikinci exec: **126–152 ms**" | `_oa_metrik_ozet_al` toplam **9 ms** | ❌ **artık geçerli değil** — `_oa_ingest_sabit_oku` düzeltmem pymupdf zincirini zaten kurutmuş; ajan düzeltmeden ÖNCE ölçmüş |
| "`re` derlemesi 9 ms israf" | 34 derlemenin 25'i `oa_hafiza`'nın **tek seferlik** modül-seviyesi derlemesi, 9'u `fnmatch`'in kendi önbellekli desenleri | ❌ **zorunlu iş, israf değil** |
| "Aynı modüller birden çok kez yürütülüyor" | cProfile: `exec_module` **5 kez** — `oa_hafiza.py` × **3**, `oa_metrik.py` × 1, `pipeline_kayit.py` × 1 | ✅ **doğrulandı → düzeltildi** |

### Düzeltilen: süreç çapında paylaşımlı modül önbelleği

**Kök neden:** her in-process yükleyici kendi modül global'inde memoize
ediyor; iki ayrı yükleyici aynı dosyayı yüklediğinde iki ayrı örnek doğuyor
ve memoizasyon örnekler arasına geçmiyor.

**Çözüm:** `sys.modules` süreç çapında tek sözlüktür.
`_paylasimli_modul_al()` paylaşımlı bir anahtarla oradan okur;
`oa_metrik._yuklu_pipeline_kayit()` zaten yüklü örneği **dosya kimliğiyle**
(ada göre değil) bulur.

| | ÖNCE | SONRA |
|---|---|---|
| `exec_module` / hook | **5** | **2** |
| `oa_hafiza.py` yürütmesi | 3× | **1×** |
| `pipeline_kayit.py` fazladan yürütmesi | 1× | **0** |
| Soğuk `.pyc` (taze kurulum) uçtan uca | **397 ms** | **95–135 ms** |
| Sıcak `.pyc` uçtan uca | ~42 ms | ~42 ms |

**Dürüst not:** sıcak `.pyc` durumunda uçtan uca kazanç **ölçülemedi**
(117.9 vs 118.1 ms — gürültü içinde), çünkü bytecode önbelleği modül
yüklemeyi zaten ucuzlatmış. Kazanç **soğuk önbellekte** gerçekleşiyor:
eklentiyi her güncellediğinizde ve `.pyc` yazılamayan kurulumlarda. Yapılan
iş yine de ölçülebilir biçimde azaldı (5 → 2 modül yürütmesi, 8800 satır).

### Bu mimarinin tabanına ulaşıldı

Kalan 2 `exec_module` **zorunludur** (`oa_hafiza` bir kez, `oa_metrik` bir
kez). Kalan regex derlemeleri **tek seferlik ilklendirmedir**. Kalan uçtan
uca ~42 ms: yorumlayıcı başlığı (~12 ms) + `pipeline_kayit`'in kendi
yüklenmesi + zorunlu modül yüklemeleri + gerçek defter/dosya işi.

Daha ileri gitmek **mimari** değişiklik ister (kalıcı bir yardımcı süreç
veya hook'ları birleştirmek) — o, bloklamayan hook sözleşmesini ve
"kanıtla yazılır" kapılarını yeniden tasarlamak demektir. Karar vericiye
ait bir tercih; performans gerekçesiyle tek taraflı yapılmaz.

### Uygulanmayan tek kalem

CI pip önbelleği — **uygulandı** (`actions/setup-python cache: pip` +
`pytest-xdist -n auto`, süit 259 s → 43 s). Ayrı commit.

---

## 10. ZAMANLAMA EŞİĞİ NEDEN TUTMAZ — v0.5.17 KALİBRASYONU (Windows)

`test_giris_betigi_dogrudan_cagridan_HIZLI` oran eşiği (`giris < dogrudan *
0.75`) v0.5.17'de KALDIRILDI. Karar ölçümle alındı; tablo kalıcı kayıt olarak
buradadır (ortam: Windows 11 · Python 3.14.6 · 12 çekirdek · gerçekçi dava
kökü · çıplak yorumlayıcı başlığı **53.49 ms**).

**1) Oran yapısal olarak eşiğin bandına düşüyor.** Kazanç sabit bir DERLEME
maliyetidir (mutlak); oranın paydası platforma bağlıdır. Aynı ~40–80 ms kazanç
Linux'ta ~%45, Windows'ta ~%23 oran verir.

| koşul | giriş | doğrudan | oran |
|---|---|---|---|
| yalıtılmış (yüksüz) | 128.0 ms | 166.3 ms | %23 — eşiğin ALTINDA |
| tam süit (`-n auto`) yükü altında | 203.3 ms | 194.6 ms | ters dönüş (eski AAAAA-BBBBB blok düzeninin artefaktı) |

Yüksüz makinede 3 koşuda **1 kırmızı**; yani yük tek başına açıklamıyor.

**2) Kendinden kalibre mutlak ölçüt de çürütüldü.** `fark >= 0.5 × C`
(C = kaynağın derleme maliyeti) öngörüsü fark ≈ 0.85–0.95·C varsayıyordu.
Gerçek: **fark/C = 0.24–0.62.** Sebep: U (`.pyc` okuma + doğrulama +
unmarshal) 6300 satırlık modülde ihmal edilemez — bu makinede 0.3–0.4·C.

| tahminci | ölçülen aralık | kararlılık |
|---|---|---|
| `min(doğrudan) − min(giriş)` | 25.9 – 80.8 ms | KÖTÜ — iki farklı yayılımlı dağılımın tabanları çıkarılıyor; doğrudan yolun geniş sağ kuyruğu (127→233 ms) tabanını orantısız düşürür, kazancı sistematik küçültür |
| ortanca − ortanca | 74.5 – 101.9 ms | iyi |
| **eşleştirilmiş fark ortancası (ABBA)** | **61.5 – 100.2 ms · ortanca 78.8 ms** | EN İYİ — ortak-mod kayma çift içinde söner; bağımsız araç `hook_olc` hook-prompt için **+79.0 ms** demişti: birebir uyum |

C'nin kendisi de alt süreç gürültüsünü paylaşmaz: ısıtmasız 124–234 ms,
ısıtılmış (2 atılır + min-5) 113–160 ms. Gürültüyü ölçeklemeyen bir paydaya
bağlı eşik, gürültüyü yalnızca TAŞIR.

**3) Karar.** Kırılgan kapı, kırmızı kapıdan kötüdür: «tekrar koştur» refleksi
öğretir — ki bu, testin önlemek için yazıldığı şeyin (kazancın bir gün sessizce
kaybolması) tam mekanizmasıdır. Bu yüzden BÜYÜKLÜK artık assert EDİLMEZ:

- **KAPI (deterministik, kırmızı bütçesi sıfır):**
  `test_pipeline_kayit_KOD_NESNESI_PYC_DEN_YUKLENIR` — `python -v` import izinde
  `code object from …pipeline_kayit.cpython-3xx.pyc` aranır ve kaynaktan
  derleme satırının YOKLUĞU doğrulanır. Docstring'in iddia ettiği şeyi (derleme
  atlanır) her zamanlama eşiğinden daha DOĞRUDAN kanıtlar; `runpy` yedeğine
  sessiz düşüşü, bayat/yazılamayan önbelleği ve loader değişikliğini yakalar.
- **KANARYA (assert YOK, bloklamaz):** `test_giris_kazanci_KANARYA`
  (`@pytest.mark.perf`) — eşleştirilmiş ABBA fark ortancası 20 ms altına
  düşerse UYARI basar. Sağlıklı sayı özete düşmez; tekrarlayan uyarı sinyaldir.
- **DEFTER (insan-okur kapı):** sürüm öncesi `tools/hook_olc.py --gercekci
  --tekrar 5 --karsilastir` koşulur, tablo bu belgeye eklenir; hook-prompt
  farkı 30 ms altındaysa sürüm notunda gerekçelendirilir.

**CI:** ana koşu `pytest -rsfE -n auto -m "not perf"`, ayrı **seri** adım
`pytest -rsfE -m perf -p no:xdist` (paralel işçiler birbirinin ölçümünü
kirletir). Karantina değil YALITIM — kanarya her bacakta koşar.

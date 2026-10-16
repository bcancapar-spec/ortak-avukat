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

---

## 11. v0.5.18 SÜRÜM ÖNCESİ DEFTER ÖLÇÜMÜ (2026-10-06, yeni bilgisayar)

Komut: `python tools/hook_olc.py --gercekci --tekrar 5 --karsilastir --import-dokumu`
(makine boşta; kancaların yorumlayıcısı). Ortam: Windows 11 · Python 3.14.8 · 16 çekirdek ·
gerçekçi dava kökü · çıplak yorumlayıcı başlığı **19.67 ms** (§10'daki ölçümde 53.49 ms).

| olay | giriş (ortanca) | NET | doğrudan yol | giriş kazancı |
|---|---|---|---|---|
| hook-prompt | 101.3 ms | 81.6 ms | 129.0 ms | +27.7 ms |
| hook-pretool | 88.4 ms | 68.7 ms | 120.8 ms | +32.5 ms |
| hook-postwrite | 136.3 ms | 116.7 ms | 164.3 ms | +28.0 ms |
| hook-denetle | 134.3 ms | 114.6 ms | 179.4 ms | +45.1 ms |
| hook-acilis | 88.4 ms | 68.7 ms | 129.5 ms | +41.1 ms |

Bileşik: bir Write (Pre + Post) **224.7 ms** bloklama. Sıcak yol import dökümü: `hook-prompt`
ve `hook-denetle` yolunda ağır modül YOK (102 import izlendi).

**Gerekçe — hook-prompt kazancı 30 ms'nin altında (§10 defter kuralı):** kazanç sabit bir
derleme maliyetidir; bu makine çıplak başlıkta ~2,7 kat hızlı olduğundan mutlak kazanç da
küçüldü. Oran korunuyor: giriş/doğrudan farkı %21,5 (§10'daki yalıtılmış ölçümde %23).
Kapı (`test_pipeline_kayit_KOD_NESNESI_PYC_DEN_YUKLENIR`) ve kanarya (`-m perf`) Python 3.12 ve
3.14'te yeşil. v0.5.18'in yeni kanca işi (belge güvenlik bölümü DURUM.md'de) sıcak yola ağır
modül eklemedi.

## 12. v0.5.18 SÜRÜM DEFTERİ ÖLÇÜMÜ — v0.5.17.1 ↔ v0.5.18 adayı (2026-10-08)

Komut: `python tools/hook_olc.py --gercekci --tekrar 5 --karsilastir --import-dokumu`.

- **Taban:** `origin/main` 4b2f029 (v0.5.17.1, kullanıcıların elindeki sürüm); `git archive` ile ayrı dizine çıkarıldı.
- **Araç:** iki ağaçta aynı sürüm (`git diff origin/main HEAD -- tools/hook_olc.py` boş).
- **Koşul:** iki ağaç `compileall` ile eşit `.pyc` sıcaklığında; A/B/A/B dönüşümlü; her koşudan önce boşta denetimi (0 yabancı python süreci, CPU %2–14).
- **Ortam:** Windows 11 · 16 çekirdek · gerçekçi dava kökü. Python 3.14.8 (kancaların yorumlayıcısı; çıplak başlık 22,5–24,9 ms) ve 3.12.15.
- Ham çıktılar yerel ölçüm klasöründe (depo dışı).

### 12.1 Standart kök — Python 3.14.8 (ortanca ms, iki tur)

| olay | v0.5.17.1 | v0.5.18 | fark (ortalama) |
|---|---|---|---|
| hook-prompt | 83,4 / 85,8 | 88,8 / 85,1 | +2,4 |
| hook-pretool | 79,1 / 80,0 | 81,4 / 79,8 | +1,1 |
| hook-postwrite | 108,0 / 107,1 | 108,2 / 107,7 | +0,4 |
| hook-denetle | 112,6 / 108,0 | 111,5 / 113,8 | +2,4 |
| hook-acilis | 82,9 / 81,1 | 80,5 / 82,3 | −0,6 |

- Bileşik (bir Write, Pre+Post): 187,1 / 187,1 → 189,6 / 187,5 ms.
- Giriş betiği kazancı (hook-prompt, doğrudan − giriş): 37,0 / 33,9 → 37,5 / 40,3 ms. §10 kuralının 30 ms eşiğinin üstünde; gerekçe gerekmez.
- Import dökümü: dört koşuda da `hook-prompt` ve `hook-denetle` yolunda ağır modül YOK (102 import izlendi).

**Sonuç:** standart kökte v0.5.18 kanca yoluna ölçülebilir maliyet eklemedi. En büyük fark +2,4 ms; turlar arası oynamanın içinde.

### 12.2 Standart kök — Python 3.12.15 (aynı protokol)

| olay | v0.5.17.1 | v0.5.18 | fark (ortalama) |
|---|---|---|---|
| hook-prompt | 80,6 / 81,0 | 83,0 / 80,6 | +1,0 |
| hook-pretool | 74,8 / 77,1 | 77,8 / 75,8 | +0,9 |
| hook-postwrite | 106,0 / 119,9 | 105,1 / 108,2 | −6,3 |
| hook-denetle | 109,0 / 104,8 | 109,2 / 107,7 | +1,6 |
| hook-acilis | 77,9 / 76,8 | 78,4 / 80,6 | +2,2 |

- `hook-postwrite`'taki −6,3, ana dalın ikinci turundaki geniş dağılımdan gelir (104,6–146,2 ms); gerçek bir kazanç değildir.
- Çıplak başlık 34,5–37,0 ms. Bileşik: 180,8 / 197,0 → 182,8 / 184,0 ms.
- Giriş betiği kazancı (hook-prompt): 31,4 / 31,6 → 36,3 / 31,6 ms; eşiğin üstünde.
- Import dökümü: ağır modül YOK (78 import izlendi).

### 12.3 Ölçek kökü — v0.5.18'in yeni işinin gerçek bedeli (Python 3.14.8)

Standart kökte `_oa/cikti`'da denetim JSON'u yoktur. v0.5.18'in zincir işi (çapraz denetim, bayat zincir, S1 kaynak beyanı) orada boş koşar. Bu yüzden Görev 1'in ölçek senaryosu da aynı protokolle ölçüldü. Senaryo 3000 evraklık bir dosyayı temsil eder:
- 1,4 MB graf (6000 düğüm);
- 3000 olaylı vakıa;
- 300 kıyas vakıası;
- dört damgalı denetim JSON'u.

| olay | v0.5.17.1 | v0.5.18 | fark |
|---|---|---|---|
| hook-denetle | 389,9 / 393,8 | 470,7 / 468,1 | **+77,6 (~%20)** |
| hook-prompt | 87,0 / 90,4 | 84,1 / 87,1 | −3,1 |
| hook-pretool | 80,4 / 79,5 | 85,4 / 79,5 | +2,5 |
| hook-acilis | 80,8 / 82,0 | 81,8 / 80,5 | −0,3 |

- `hook-postwrite` bu protokolde güvenilir değildir. Tetik "son 60 sn içinde taslak yazıldı mı" koşuluna bağlıdır; kökün yaşına göre ya tam gövdeyi (395,7 → 459,2) ya erken çıkışı (80,0 → 82,5) ölçer.
- **Tam yol kontrolü:** her çağrıdan önce bir çalışma evrakı güncellenerek alınan ölçüm standartla aynıdır: 387,8 / 388,2 → 468,7 / 468,6, fark +80,7. İki ölçümün ortalaması **+79 ms**.
  - Gövde her çağrıda tam koşar. "Boş çıktı" yalnız değişmeyen çıktının BASIMININ susturulmasıdır (`_hook_cikti_degisti_mi`).
  - Dedup kısa devresi yalnız aynı saniyede devreye girer; `--bekle 1.1` onu yener.

**Kaynak (cProfile, tek çağrı, ısıtmadan sonra):** artışın neredeyse tamamı B-2 çapraz denetimidir.
- `_capraz_bosluk_uyarisi` → `capraz_denetim.caprazla_ayrintili`: graf, vakıa ve kıyas kimlikleri ortak uzayda eşleştirilir (25.799 `_norm` çağrısı).
- Bayat zincir ~17 ms.
- v0.5.18'in süreç-içi JSON ayrıştırma önbelleği maliyetin bir kısmını geri kazanır: `_denetim_jsonlari` 4 çağrı / 49,5 ms → 10 çağrı / 18,5 ms.
- Bunlar profilli sürelerdir; cProfile çok sayıda küçük çağrıyı şişirir. Profilsiz fark ~+79 ms'dir.

**Gerekçe:** bu maliyet zincirleme tepkinin kendisidir. Üç halkanın aynı kişiyi ve olayı aynı kimlikle anıp anmadığı her Stop'ta yeniden denetlenir. Maliyet yalnız zincir motorlarının çıktısı olan büyük dosyada görünür; standart kökte sıfırdır.

**v0.5.19 adayı (ölçüldü, uygulanmadı):** çapraz denetimin sonucu girdilerin içerik özetine (sha) bağlanıp kanca çağrıları arasında önbelleklenebilir; girdiler çoğu turda değişmez. Bu türetilmiş bir önbellektir; gerçeğin kaynağı (defter) değişmez. → **Uygulandı ve ölçüldü: §14.**

### 12.4 Görev 1'in "+27,5 ms" ölçümüyle uzlaşma

Görev 1'in raporu, `hook-denetle` için +27,5 ms ölçmüştü (Python 3.12.15, taban: zincir onarımının başlangıç commit'i). Son kodda, aynı araçla, iki yorumlayıcıda ve A/B/A/B koşulduğunda bu fark **yeniden üretilmedi**: 3.14'te +2,4, 3.12'de +1,6 ms.

- Görev 1'in karar ölçümü tek bir ÖNCE/SONRA çiftiydi. Aynı çiftte dokunulmayan `hook-acilis` +10,0 ms oynamıştı; gürültü tabanı ±10 ms mertebesindeydi.
- Ölçülen kod, birleştirme öncesi ara hâldi.
- Kalıcı bedel standart kökte değil, zincir ürünleri olan büyük dosyada görünür (§12.3).

### 12.5 Diğer sürüm kapıları (aynı gün)

- Zamanlama kanaryası (`-m perf -p no:xdist`): Python 3.14 ve 3.12'de geçti, uyarı yok.
- `hook_doktor --servis-atla`: TÜM MEKANİK KONTROLLER GEÇTİ.
  - Sürüm mutabakatı 0.5.18.
  - `plugin.json`'da çift hooks bildirimi yok.
  - 6 olay kayıtlı; altısı da exit 0.
  - [5] "servis edilen nesil" bu makinede BAYAT görünür, çünkü kurulu eklenti 0.5.17.1'dir. Bu, sürüm main'e birleşip `/plugin` ile güncellenene kadar beklenen ortam hâlidir; kod arızası değildir.
- `aile_dogrula`: AİLE YAPI DENETİMİ TEMİZ (20 parça).

## 13. v0.5.18 EKSİKLER TURU — 38a3859 ↔ çalışma ağacı (2026-10-12)

Komut: `python tools/hook_olc.py --gercekci --tekrar 5 --karsilastir --import-dokumu`.

- **Neden:** bu tur kanca yoluna dokundu: DURUM.md üretimi («Avukat Kararı Bekleyen» tek kaynağı, şerh sahibi etiketi), `run-hook.cmd` (yorumlayıcı seçimi).
- **Taban:** HEAD 38a3859 (`git archive` ile depo dışına çıkarıldı). Ölçüm aracı iki ağaçta aynı dosya.
- **Koşul:** iki ağaç `compileall` ile eşit `.pyc` sıcaklığında; A/B/A/B dönüşümlü.
- **Ortam:** Windows 11 · 16 çekirdek · gerçekçi dava kökü · Python 3.14.8 (kancaların yorumlayıcısı; çıplak başlık 22,5–22,9 ms).

| olay | 38a3859 | çalışma ağacı | fark (ortalama) |
|---|---|---|---|
| hook-prompt | 84,1 / 85,2 | 86,1 / 84,2 | +0,5 |
| hook-pretool | 81,7 / 80,8 | 79,7 / 79,1 | −1,9 |
| hook-postwrite | 109,4 / 107,2 | 108,8 / 107,9 | +0,1 |
| hook-denetle | 109,3 / 113,3 | 109,5 / 112,3 | −0,4 |
| hook-acilis | 82,0 / 81,9 | 81,7 / 82,7 | +0,3 |

- Bileşik (bir Write, Pre+Post): 191,0 / 188,0 → 188,6 / 187,0 ms.
- Giriş betiği kazancı (hook-prompt, doğrudan − giriş): 35,2 / 35,9 → 35,8 / 35,3 ms. §10 kuralının 30 ms eşiğinin üstünde; gerekçe gerekmez.
- Import dökümü: dört koşuda da `hook-prompt` ve `hook-denetle` yolunda ağır modül YOK (103 import izlendi).

**Sonuç:** bu tur kanca yoluna ölçülebilir maliyet eklemedi; farklar turlar arası oynamanın içinde. Sarmalayıcının kendi maliyeti bu araçla ölçülmez (araç `hook_giris.py`'yi doğrudan çağırır). Sarmalayıcı değişikliği yalnız `where` çıktısının süzülmesidir; ek süreç açmaz.

## 14. v0.5.19 ADAYI — ÇAPRAZ DENETİM SONUÇ ÖNBELLEĞİ (2026-10-09)

§12.3'ün açık kalemi uygulandı. Ölçek kökünde Stop kancasının v0.5.18'deki +79 ms'si B-2 çapraz denetimiydi (`_capraz_bosluk_uyarisi` → `_capraz_bosluk_hesapla` → `capraz_denetim.caprazla_ayrintili`). Kanca gövdesi her Stop'ta tam koşar; çapraz denetimin girdileri ise çoğu turda değişmez.

### 14.1 Ne değişti

- Sonuç `_oa/defter/.capraz-onbellek.json`'da tutulur. Dosya türetilmiştir: gerçeğin kaynağı değildir, silinmesi bir şey kaybettirmez (sonraki koşu yeniden hesaplar).
- Anahtar (sha256) sonucu belirleyen her şeyi kapsar:
  - üç model girdisinin (graf / vakıa / kıyas) rol başına içerik özeti;
  - S1 seçimini besleyen damgalı denetim JSON'ları (`grafik_denetim`, `vakia_matris`, `kiyas_denetim`);
  - `capraz_denetim.py` ve `pipeline_kayit.py` dosyalarının özeti (kod değişince önbellek geçersiz);
  - yorumlayıcının küçük sürümü (`cpython-3.14`; eşleştirmenin dayandığı Unicode veritabanı buna bağlıdır);
  - önbellek şeması (`_CAPRAZ_ONBELLEK_SEMA`).
- Girdi seçimi her koşuda yeniden yapılır. Her girdi BİR kez okunur; özet ve ayrıştırma aynı baytlardan yapılır. Böylece iki okuma arasındaki bir yarış eski özete yeni sonucu bağlayamaz. Ayrıştırma `capraz_denetim._yukle` ile eşdeğerdir (testli).
- Fail-closed:
  - okunamayan girdi, anahtar / okuma / yazma adımında istisna, gövde özeti tutmayan dosya (yarım yazım, elle düzenleme), yabancı anahtar ya da beklenmeyen yapı → önbellek kullanılmaz, sonuç hesaplanır;
  - hiçbir önbellek hatası `_capraz_bosluk_hesapla`'nın dış `except`ine (→ boş, "temiz" görünen sonuç) ulaşmaz;
  - JSON gidiş-dönüşü sonucu birebir geri vermiyorsa önbelleğe yazılmaz.
- Yan etki sınırları:
  - `denetle` dedup parmak izinden hariçtir (`.hook-son-iz.json` ile aynı gerekçe: ilk koşunun kendi yazımı dedup'u ölü koda çevirmesin);
  - `_oa/defter` yoksa yazılmaz, dizini yaratmaz;
  - append-only olay defterine dokunmaz;
  - yazım tmp + `os.replace` ile atomiktir.
- Standart kökte (JSON girdisi yok) önbellek yoluna hiç girilmez; ek iş yapı gereği sıfırdır.
- Kilitler: `tests/test_v0519_capraz_onbellek.py` (37 test). Her kilit için ürün kodu geçici bozuldu, testin kırmızıya döndüğü görüldü, dosya bayt-özdeş geri yüklendi (sha256 doğrulandı): **21 mutasyonun 21'i yakalandı.**

### 14.2 Ölçüm koşulları

- Tabanlar `git archive` ile ayrı dizine çıkarıldı:
  - v0.5.18: `guncelleme/0.5.18` ucu edb2b46 (PR #8);
  - v0.5.17.1: `origin/main` 4b2f029.
- Aday: bu dalın çalışma ağacının kopyası.
- Ağaçlar aynı üst dizinde ve aynı `.py` kümesinde. `compileall -f` (Python 3.14.8, kancaların yorumlayıcısı) ile eşit `.pyc` sıcaklığına getirildiler. `tools/hook_olc.py` üç ağaçta bayt-özdeş.
- Ortam: Windows 11 · 16 çekirdek · Python 3.14.8.
- **Makine bu ölçümde paylaşımlıydı.** Başka bir Claude oturumu aralıklarla tam ve parça süitler koşturuyordu (37'ye varan python süreci, anlık CPU %72'ye kadar). Bu yüzden:
  - her koşu "sakin pencere" kapısıyla başlatıldı (yabancı python süreci 0, ardışık 3 örnekte CPU ≤ %12) ve koşu sonrası durum kaydedildi;
  - karar ölçütü §10'un önerdiği **eşleştirilmiş ABBA fark ortancasıdır**: A ve B çağrıları yan yana dönüşümlü koşar, ortak yük kayması çift içinde söner;
  - mutlak sayılar oturuma göre oynar; karşılaştırma yalnız aynı oturumdaki ağaçlar arasında yapılır.
- Kapı kurulmadan, yük altında alınan iki koşu GEÇERSİZ sayıldı. Kodu iki ağaçta özdeş olan `hook-acilis` o koşularda 143 ↔ 102 ms oynamıştı.
- Ham çıktılar yerel ölçüm klasöründe (depo dışı).

### 14.3 Ölçek kökü — eşleştirilmiş ABBA (karar ölçütü)

Gerçek kanca yolu (`hook_giris.py --hook-denetle`). Senaryo §12.3'ün aynısıdır: 1,4 MB graf, 3000 olaylı vakıa, 300 kıyas vakıası, dört damgalı denetim JSON'u. Her senaryoda 12 çift koşuldu. Her çağrıdan önce ilgili kökte şu yapıldı:
- **TAM:** bir çalışma evrakı güncellenir. Gövde tam koşar, çapraz girdileri değişmez; v0.5.19'da önbellek isabet eder.
- **ISKA:** `04-vakia.json` sonuna boşluk eklenir. Sonuç aynı kalır ama özet değişir; v0.5.19'da önbellek ıskalar. Önbelleğin en kötü durum bedeli budur.
- **STANDART-TAM:** standart kök, TAM ile aynı tetik.

v0.5.18 ↔ v0.5.19 (ortanca ms):

| senaryo | v0.5.18 | v0.5.19 | eşleştirilmiş fark ortancası [Ç1 / Ç3] |
|---|---|---|---|
| TAM (isabet) | 527,9 | 437,5 | **−96,5** [−129,6 / −80,1] |
| ISKA | 511,6 | 531,3 | +22,2 [+4,4 / +42,0] |
| STANDART-TAM | 137,4 | 129,0 | −0,3 [−10,4 / +2,5] |

v0.5.17.1 ↔ v0.5.19 (ortanca ms; bu koşu sakin pencerede alındı, v0.5.17.1 §12.3'teki ~390 ms'yi yeniden verdi):

| senaryo | v0.5.17.1 | v0.5.19 | eşleştirilmiş fark ortancası [Ç1 / Ç3] |
|---|---|---|---|
| TAM (isabet) | 390,8 | 394,6 | **−3,6** [−19,7 / +11,5] |
| ISKA | 385,3 | 461,2 | +78,0 [+53,3 / +82,7] |
| STANDART-TAM | 106,7 | 112,1 | +4,7 [+1,4 / +7,1] |

- **İsabette** Stop kancası v0.5.17.1 düzeyine döner: v0.5.18'in +79 ms'lik gerilemesi geri alındı (fark gürültü bandında).
- **Iskada** (yalnız çapraz girdisi değiştiğinde, yani bir zincir motoru yeniden koştuğunda) bedel v0.5.18'inkiyle aynı mertebededir. Önbelleğin kendi ek bedeli süreç içinde +7,7 ms ölçüldü (14.5). Kanca düzeyindeki +22,2 ms, süreç düzeyindeki dosya maliyetlerini ve bu oturumun gürültüsünü de taşır.
- Standart kökteki +4,7 ms v0.5.18'in kendi zincir ekleridir (§12.1: +2,4 ms). v0.5.18 ↔ v0.5.19 arasında aynı senaryo −0,3 ms verdi.

### 14.4 Ölçek kökü — §12.3 protokolünün tekrarı (v0.5.18 ↔ v0.5.19, iki tur, ortanca ms)

| olay | v0.5.18 | v0.5.19 | fark (ortalama) |
|---|---|---|---|
| hook-denetle | 540,6 / 534,3 | 425,1 / 440,9 | **−104,5** |
| hook-denetle TAM | 502,0 / 529,7 | 449,7 / 442,9 | −69,6 |
| hook-denetle ISKA | 543,2 / 516,1 | 542,7 / 541,8 | +12,6 |
| hook-prompt | 122,7 / 124,7 | 105,8 / 129,1 | −6,3 |
| hook-pretool | 126,9 / 122,5 | 108,2 / 120,7 | −10,3 |
| hook-acilis | 123,6 / 127,4 | 100,8 / 130,8 | −9,7 |

- Çapraz yola yalnız `--hook-denetle` ve `--hook-postwrite` ulaşır. `hook-prompt`, `hook-pretool` ve `hook-acilis` değiştirilen koda hiç girmez; bu üçündeki −6…−10 ms bu oturumun gürültü bandıdır.
- `hook-postwrite` bu protokolde güvenilir değildir (§12.3); burada 5/5 erken çıkışı ölçtü: 117,8 / 106,6 → 122,2 / 118,3.
- Standart kök TAM yol: 154,1 / 139,8 → 158,2 / 152,5 (+8,4). Eşleştirilmiş ABBA aynı senaryoda −0,3 ms verdi (14.3); fark gürültüdür.
- **Çıktı eşitliği.** Aynı ölçek senaryosu, kök yolu ve türetim zamanı satırı normalleştirilerek karşılaştırıldı. v0.5.18 ile v0.5.19'un hem ıska hem isabet koşusunda `--denetle` çıkış kodu, stdout ve DURUM.md BİREBİR aynıdır; DURUM.md «Çapraz Denetim» bölümünü taşır. İsabet koşusu önbellek dosyasını yeniden yazmadı.

### 14.5 Süreç içi bileşenler (ölçek kökü, 9 tekrar, ortanca ms)

- `_capraz_bosluk_hesapla`: v0.5.18 81,1 · v0.5.19 ıska 88,8 (+7,7) · v0.5.19 isabet 5,6 (−75,5).
- İsabetin bileşenleri: girdi seçimi 0,9 · üç girdinin bayt okuması 1,5 · anahtar 1,4 · önbellek okuma 2,0.
- Iskanın ek bileşenleri: yabancı anahtarlı okuma 0,4 · yazma 5,7 (JSON 2,4 · gidiş-dönüş denetimi 1,6 · sha256 0,1 · disk 0,5).
- Sonuç 0 kopuk ve 3000 belirsiz öğedir; önbellek gövdesi 665 KB.
- İsabetin kazancı `caprazla_ayrintili`'den büyüktür, çünkü 1,4 MB grafın `_yukle` ile ikinci kez ayrıştırılmasını da atlar. `_denetim_jsonlari` onu zaten bir kez ayrıştırıyor.

### 14.6 Gerçek kanca yolunda doğrulama (cProfile, ölçek kökü, ikinci Stop)

- `caprazla_ayrintili`, `_norm`, `_capraz_girdi_coz` ve `_capraz_onbellek_yaz` çağrılmadı.
- `_capraz_bosluk_hesapla`, `_capraz_onbellek_anahtari` ve `_capraz_onbellek_oku` birer kez çağrıldı.
- Değişmez 5 korunuyor: eklenti modül gövdelerinin her biri BİR kez yürütüldü (`pipeline_kayit`, `capraz_denetim`, `oa_hafiza`, `oa_metrik`, `tazelik_denetim`, `hook_giris`).

### 14.7 Standart kök — sürüm defteri komutu (A/B × 3)

Komut: `hook_olc --gercekci --tekrar 5 --karsilastir --import-dokumu` (ortanca ms).

| olay | v0.5.18 (3 koşu) | v0.5.19 (3 koşu) | fark (ortancaların ortancası) |
|---|---|---|---|
| hook-prompt | 124,2 / 124,5 / 94,4 | 105,6 / 121,2 / 119,2 | −5,0 |
| hook-pretool | 106,1 / 98,3 / 100,0 | 96,9 / 100,8 / 119,9 | +0,8 |
| hook-postwrite | 131,4 / 126,0 / 130,5 | 142,2 / 143,8 / 152,7 | +13,3 |
| hook-denetle | 154,0 / 151,6 / 130,9 | 138,6 / 140,0 / 147,3 | −11,6 |
| hook-acilis | 122,0 / 102,2 / 125,5 | 102,3 / 102,4 / 118,6 | −19,6 |

- Bu koşular simetrik dizin düzeni kurulmadan alındı: v0.5.18 ağacı Temp altında, aday çalışma ağacındaydı. Koşu sonrası kayıtlara göre altı koşunun dördünde yabancı yük vardı; en kötüsü A1 (20 python süreci, CPU %72).
- Değiştirilen koda girmeyen `hook-acilis`'in −19,6 ms'si bu koşuların gürültü ölçüsüdür.
- `hook-postwrite` (+13,3) ile `hook-denetle` (−11,6) standart kökte aynı gövdeyi koşar ve zıt yönde oynadı. Standart kökte çapraz yol önbelleğe uğramaz; aynı gövdenin eşleştirilmiş ABBA ölçümü −0,3 ms verdi (14.3).
- Giriş betiği kazancı (hook-prompt, doğrudan − giriş): v0.5.18'de 21,1 / 39,1 / 50,9 (ortanca 39,1), v0.5.19'da 48,2 / 39,8 / 37,5 (ortanca 39,8). §10 kuralının 30 ms eşiğinin üstünde; gerekçe gerekmez.
- Import dökümü: altı koşunun altısında `hook-prompt` ve `hook-denetle` yolunda ağır modül YOK (102 import izlendi).

### 14.8 Sürüm kapıları (aynı gün)

- Tam süit (`-n auto -m "not perf"`), 0 kırmızı:
  - Python 3.14: 3640 geçti, 2 atlandı;
  - Python 3.12: 3640 geçti, 2 atlandı;
  - atlananlar ortam kaynaklıdır (saha referansı tanımsız; `python-docx` kurulu değil).
- Zamanlama kanaryası (`-m perf -p no:xdist`): iki yorumlayıcıda geçti, uyarı yok.
- `hook_doktor --servis-atla`: TÜM MEKANİK KONTROLLER GEÇTİ (6 olay, altısı da exit 0; sürüm damgası henüz 0.5.18).
- `aile_dogrula`: AİLE YAPI DENETİMİ TEMİZ (20 parça).

**Sonuç:** büyük dosyada (3000 evrak) Stop kancası, çapraz girdiler değişmediği her turda v0.5.17.1 düzeyine döner (eşleştirilmiş fark v0.5.17.1'e göre −3,6 ms, v0.5.18'e göre −96,5 ms). Girdi değiştiği turda ödenen bedel v0.5.18'inkiyle aynı mertebededir. Standart kökte değişiklik yoktur.

### 14.9 Yeniden ölçüm 2026-10-16 — 61b8e14 üzerine taşıma

- **Taşıma notu:** bu bölüm ilk commit'inde (`ad66357`) §13 numarasını taşıyordu. Denetim dalında §13 v0.5.18 eksikler turuna ait olduğundan `61b8e14` üzerine yeniden temellendirmede §14 oldu; taşınan commit'in (`d996f62`) mesajındaki «§13» bu bölümdür. 14.1–14.8'in sayıları 2026-10-09 ölçümüdür, değiştirilmedi.
- **Komut:** `py -3.14 tools/hook_olc.py --gercekci --tekrar 3 --karsilastir --import-dokumu` (sürüm defteri kuralı). Tek ağaç ölçüldü, A/B tabanı yoktur; bu satırlardan sürümler arası fark çıkarılmaz.
- **Koşul:** gerçekçi dava kökü (standart kök; ölçek kökü değil) · ölçümden önce `compileall` ile `.pyc` sıcak (ortamda `PYTHONDONTWRITEBYTECODE=1`) · tek koşu.
- **Ortam:** Windows 11 · 16 çekirdek · Python 3.14.8 (çıplak başlık 21,34 ms, ortanca).

| olay | ortanca | en hızlı | en yavaş | NET | boş çıktı | doğrudan `pipeline_kayit.py` |
|---|---|---|---|---|---|---|
| hook-prompt | 71,2 | 69,4 | 86,0 | 49,8 | 0/3 | 111,0 |
| hook-pretool | 64,0 | 63,0 | 64,5 | 42,6 | 3/3 | 106,5 |
| hook-postwrite | 94,6 | 92,6 | 97,4 | 73,3 | 2/3 | 136,2 |
| hook-denetle | 96,0 | 95,1 | 118,9 | 74,6 | 2/3 | 138,2 |
| hook-acilis | 67,4 | 64,9 | 68,8 | 46,1 | 0/3 | 106,2 |

- Bileşik (bir Write, Pre+Post): 158,6 ms.
- Giriş betiği kazancı (hook-prompt, doğrudan − giriş): 39,8 ms. §10 kuralının 30 ms eşiğinin üstünde; gerekçe gerekmez.
- Import dökümü: `hook-prompt` ve `hook-denetle` yolunda ağır modül YOK (102 import izlendi).
- Aynı gün kapılar (`d996f62`): tam süit (`-n auto -m "not perf"`) 3840 geçti · 12 atlandı · 0 kırmızı (atlananlar ortam kaynaklıdır: UDF yazıcısı `OA_TEST_UDF_YAZICI=0` ile kapalı, saha referansı tanımsız); zamanlama kanaryası (`-m perf -p no:xdist`) 1 geçti; `ruff` temiz; `aile_dogrula` AİLE YAPI DENETİMİ TEMİZ (20 parça). Toplanan test 3853, OA-SUIT-SAYISI ile birebir.

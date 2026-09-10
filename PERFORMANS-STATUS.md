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

## 9. SIRADAKİ EN BÜYÜK KAZANÇLAR (denetimde bulundu, bu oturumda uygulanmadı)

Kalan ~77 ms'lik `hook-denetle` bedelinin içinde:

- **Defterin tek Stop hook'unda 4 kez baştan sona taranması** — zamanla
  kötüleşen O(n) borç (20.001 olaylı defterde ölçüldü: 1437 ms).
- `_oa_metrik_ozet_al` → `oa_metrik.py` → `pipeline_kayit.py`'yi **aynı
  süreçte ikinci kez** exec ediyor (cProfile: 126-152 ms).
- `hook_prompt`'ta aynı dosyaların 5 kez okunması (~3.4 MB gereksiz okuma).
- `_eklenti_script_indeksi()` önbelleksiz: her çağrıda 21 `os.listdir`.
- CI'da pip önbelleği yok (koşu başına 5 iş × 35 MB).

Bunlar ölçüldü ve doğrulandı ama **uygulanmadı** — her biri defter okuma
semantiğine dokunduğu için ayrı bir tur ve ayrı bir test seti hak ediyor.

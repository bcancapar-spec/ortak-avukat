# CLAUDE.md — Ortak Avukat çalışma hafızası

Bu dosya Claude Code'un bu depoda çalışırken uyması gereken kuralları ve
öğrenilmiş dersleri tutar. Karar verici **Av. Bayram Can ÇAPAR**'dır.

---

## Proje nedir

Türk hukuku için **Claude Code eklentisi** (`plugins/ortak-avukat`): çekirdek +
19 `oa-*` beceri (skill) tek pakette. Python ≥ 3.12. Yargı Pro MCP ile
içtihat/mevzuat doğrulaması.

- Kod: `plugins/ortak-avukat/skills/*/scripts/*.py` (176 dosya)
- Beceri metinleri: `plugins/ortak-avukat/skills/*/SKILL.md`
- Hook ağı: `plugins/ortak-avukat/hooks/` (`hooks.json` + `run-hook.cmd`)
- Testler: `tests/` (2340 test — tek kaynak: `tests/README.md`'deki
  `OA-SUIT-SAYISI` işaretçisi; `test_b35` ikisini karşılaştırır)
- **Hedef ortam: Windows** (masaüstü Claude Code, cp1254 konsol)

---

## Testleri koşturma

```bash
python -m pytest tests/ -q -n auto      # 4 çekirdekte ~43 s
python -m pytest tests/ -q              # tek çekirdek ~259 s (v0.5.16.3 öncesi ölçüm)
```

`-n auto` (pytest-xdist) **kullanın**: süit paralel-güvenlidir (ölçüldü:
sonuçlar birebir aynı), 3.5× hızlanır. `pytest-xdist` yoksa:
`pip install pytest-xdist`.

### Bilinen, ÖNCEDEN VAR OLAN başarısızlıklar — RELEASE KAPISI ŞU AN KAPALI

`main` dalında da kırmızı yanan 4 test (dört CI bacağının hepsinde):

- `test_devir_zorlayici.py::test_plugin_json_hooks_KAYDINI_tasimak_ZORUNDA`
- `test_hooks_wiring.py::test_plugin_json_var_ve_gecerli_json`
- `test_hooks_wiring.py::test_plugin_json_hooks_alani_diskte_cozulebilir`
- `test_hook_doktor.py::test_uctan_uca_tum_olaylar_yesil`

**Kök neden saptandı (PR #5 yorumunda tam kanıtla):** deponun kendi
tarihinde belgelenmiş bir çelişki.

| Olay | Ne yapıldı | Sahada ne oldu |
|---|---|---|
| **v0.5.6** | `plugin.json`'dan `hooks` düştü | `STATUS.md:145`: "dört hook olayı da ölüydü" → v0.5.6.1'de **P0** olarak geri kondu, bu 4 test kilit olarak yazıldı |
| **`08441f5`** | Aynı satır tekrar kaldırıldı | "Duplicate hooks file detected" → **eklentinin tamamı (20 skill) yüklenemedi** |

Uzlaşma: **Claude Code'un davranışı bu iki olay arasında değişti.**
`hooks/hooks.json` eklenti kökünde artık **otomatik keşfediliyor**; alanı
tekrar bildirmek yinelenen kayıt sayılıp eklentiyi düşürüyor.

**Kanıt (resmî belge + deponun kendi CI çıktısı):** `plugins-reference`
hook konumunu *"`hooks/hooks.json` in plugin root, or inline in
plugin.json"* diye tanımlıyor ve alanı **opsiyonel** sayıyor. Daha
güçlüsü: `hook_doktor` aynı koşuda `plugin.json hooks: ✗ YOK` derken
**altı olayın altısını da** `✓ exit 0` olarak ölçüyor — yani "hook katmanı
hiç kaydolmaz" teşhisi kendi ölçümüyle çelişiyor.

**Sonuç:** bu 4 test şu an eklentiyi tamamen bozacak bir yapılandırmayı
şart koşuyor — önlemek için yazıldıkları arızadan daha büyüğünü. `08441f5`
doğru davranmış; kilitler bayat.

**Karar bekliyor** (önerilen yama PR #5 yorumunda): testler ters çevrilip
`hook_doktor`'un teşhisi düzeltilecek. Bu, deponun hook kaydı hakkındaki
garantisini değiştirdiği için **davranış kararıdır** — Bayram Can ÇAPAR'a
aittir. Kendi başına "düzeltilmemelidir".

---

## PERFORMANS DEĞİŞMEZLERİ — bunları geri almayın

v0.5.16.3'te bir `Write`'ın hook bloklaması **1164 ms → 118 ms** (%89.9
azalma, 9.86×) düşürüldü; sıcak yoldaki ağır modül sayısı **11 → 0**.
Ölçüm: `main` vs bu dal, aynı araç, **gerçekçi dava kökü**, dedup yenilmiş.
Ayrıntı ve kök neden zincirleri: `PERFORMANS-STATUS.md`.

Altı yapısal karar bunu sağlıyor; hepsi kolayca ve sessizce geri alınabilir,
o yüzden burada yazılıdır.

### 1. `ONBAKIS_DIZIN` sabiti oa_ingest'i YÜRÜTMEDEN okunmalı

**En büyük tek kazanç.** `_dizin_beyaz_liste_hesapla()` bu sabiti almak için
`oa_ingest.py`'yi (1716 satır) TAM YÜRÜTÜYORDU; o da dolaylı olarak
**pymupdf (78-86 ms) + PIL (7-8 ms)** çekiyordu. PDF okumakla ilgisi olmayan
bir kanca PDF kütüphanesi yüklüyordu — hem `hook_prompt` (her kullanıcı turu)
hem `hook_denetle` (her asistan turu + SessionEnd) yollarında.

Şimdi `_oa_ingest_sabit_oku("ONBAKIS_DIZIN")` dosyayı **satır olarak okur**.

- **Tek-kaynak garantisi (P1-9(a)) BOZULMADI**: değer hâlâ çalışma anında
  `oa_ingest.py`'den gelir, koda gömülmez. Fark: dosya yürütülmez, okunur.
- Sabit basit bir string literali değilse desen eşleşmez → **tam import
  yedeğine** düşülür. Yanlış değer üretmek yapısal olarak imkânsız.
- `_oa_ingest_modulu_beyaz_liste()` **kaldırılmadı** (yedek + testli).

> **UYARI — v0.5.16.2'nin dersi:** ilk denemem hesabı *tembelleştirmekti*.
> O maliyeti **kaldırmadı, erteledi** — ve gerçek dava klasöründe ilgili dal
> her zaman koştuğu için hiçbir şey kazandırmadı. Tembelleştirme, her zaman
> çalışan bir kod yolu için çözüm DEĞİLDİR.

### 2. `DIZIN_BEYAZ_LISTE` TEMBEL kalmalı (ikincil kazanç)

Modül seviyesinde hesaplanmamalıdır; `_dizin_beyaz_liste()` erişimcisi ilk
kullanımda hesaplar, modül dışı `mod.DIZIN_BEYAZ_LISTE` erişimi `__getattr__`
(PEP 562) ile aynı yere düşer.

- **Modül İÇİ kullanım `_dizin_beyaz_liste()` çağırmalı.** Modül
  `__getattr__`'ı modülün kendi içindeki çıplak global ad aramasında
  **ateşlenmez** — çıplak `DIZIN_BEYAZ_LISTE` yazarsanız `NameError` alırsınız.
- Yeni bir modül-seviyesi ağır hesap eklemeyin. Kontrol:
  `python tools/hook_olc.py --gercekci --import-dokumu`
  → "ağır modül YOK ✓" görmelisiniz.

### 3. `_oa/cikti` taramaları İKİLİ ÜRÜNLERİ okumamalı

`_dilekce_sekilli_makbuzsuz_uyarisi` ve `_kutuk_dilekce_sayaci` eskiden
`_oa/cikti`'daki **her dosyayı** uzantı süzgeci olmadan `f.read()` ile tam
okuyordu — 3 MB'lık `ek-deliller.pdf` utf-8'e çözülüp regex'e sokuluyordu
(tek fonksiyon çağrısı 271 ms). `_ikili_urun_mu()` süzgecini kaldırmayın.

- Süzgeç **kapının kararını değiştirmez**: zip/ikili bir dosyanın
  utf-8-replace çözümü Türkçe hukuk kalıplarını üretemez. Testle kilitli
  (`test_ikili_suzgec_kapi_kararini_DEGISTIRMIYOR`).
- **Metin dosyalarına bayt eşiği/kırpma EKLEMEYİN.** Uzun bir dilekçenin
  `NETİCE-İ TALEP` bölümü 20 KB'ı aşabilir; kırpma teslim kapısını kör eder.
  (Kod tabanındaki `f.read(20000)` deseni TETİKLEYİCİ arayan kardeş
  fonksiyona aittir — o kapı beslemez.)

### 4. `oa_ingest.py`'ye ölü import geri koymayın

`import xml.etree.ElementTree as ET` kaldırıldı: bu dosyada `ET.` kullanımı
**sıfırdı** (soğuk süreçte 8.7 ms bedelsiz maliyet). ET gerçekten
`udf_yaz.py`, `udf_md.py`, `pipeline_kayit.py`, `hesapla_sure.py` ve
`oa_hafiza.py`'de kullanılır ve orada import edilir.

### 5. Aynı modül tek hook çağrısında BİR KEZ yürütülmeli

Bu depoda kardeş scriptler birbirini `spec_from_file_location` ile in-process
yükler (paket yok). Her yükleyici **kendi modül global'inde** memoize
ediyordu; iki ayrı yükleyici (`pipeline_kayit` + `oa_metrik`) aynı dosyayı
yüklediğinde iki ayrı örnek doğuyor ve memoizasyon örnekler arasına
**geçmiyordu**.

Ölçüm (11 olaylı gerçek defter, tek `--hook-denetle`, cProfile):
`exec_module` **5 kez** koşuyordu — `oa_hafiza.py` (2500 satır) × **3**,
`oa_metrik.py` × 1, `pipeline_kayit.py` (6300 satır) × 1 fazladan.
Şimdi **2**. Soğuk `.pyc` senaryosunda (taze kurulum / güncelleme sonrası
ilk çağrı) uçtan uca: **397 ms → 95–135 ms**.

İki mekanizma:

- `_paylasimli_modul_al()` + `sys.modules["_oa_paylasimli_oa_hafiza"]` —
  **anahtar dize `pipeline_kayit.py` ve `oa_metrik.py`'de AYNI olmak
  zorunda.** Ayrışırsa hiçbir şey çökmez, paylaşım **sessizce ölür**;
  bu yüzden testle kilitli (`test_paylasimli_onbellek_anahtari_IKI_DOSYADA_AYNI`).
- `oa_metrik._yuklu_pipeline_kayit()` — zaten yüklü örneği bulur.
  **Arama ADA göre değil, DOSYA KİMLİĞİNE göre yapılır** (`__file__`
  realpath + gereken çağrı yüzeyi). Neden: bu modül bağlama göre farklı
  adlarla yüklenir — hook yolunda `pipeline_kayit`, CLI'da `__main__`,
  testlerde `_pk_test` gibi benzersiz adlar (tests/README.md §1). Ada
  bakmak optimizasyonu tesadüfi bir ada bağlardı.

Neden güvenli (üçü de denetlendi): bu modüller modül seviyesinde
**yan etkisizdir**; üretim kodu mutable global'lerini (`DIZINLER`,
`ARAMA_ARACLARI`…) **yerinde değiştirmez**, yalnız okur; aday adına
güvenilmez, kimlik denetiminden geçer. Tek-kaynak garantisi **güçlenir**:
iki ayrı örnek yerine tek örnek okunur.

> `hook_giris.py`'nin `sys.modules["pipeline_kayit"] = mod` satırı bu
> paylaşımın giriş kapısıdır — kaldırmayın.

### 6. Hook yolu `hook_giris.py` üzerinden geçmeli

Python, `__main__` olarak koşan bir betiğin bytecode'unu **ASLA** önbelleğe
almaz (`__pycache__` yalnızca IMPORT edilen modüller için). Hook ağı
`pipeline_kayit.py`'yi doğrudan çağırdığında 6300+ satır **her ateşlemede**
yeniden derleniyordu (~38-46 ms).

- `run-hook.cmd`'yi `pipeline_kayit.py`'ye geri yönlendirmeyin.
- `PYTHONDONTWRITEBYTECODE` **ayarlı olmamalı** — kazancı tümüyle yok eder.
- `hook_giris.py` `sys.path`'i kirletmez; bu deseni bozmayın.
- **Taze kurulumda `.pyc` YOKTUR** (`.gitignore` `__pycache__/` dışlıyor ve
  eklenti her güncellemede yeni bir sürümlü dizine açılır). İlk çağrı tam
  bedeli öder. Çözüm: güncellemeden sonra `python -m compileall <eklenti dizini>`
  — `tools/pc_hizlandir.ps1 -Uygula` bunu yapar.
- Modül gövdesi **YARIDA** çökerse betik `runpy` yedeğine DÜŞMEZ (çift yan
  etki riski); hatayı olduğu gibi bırakır. Bu bilinçlidir, "iyileştirmeyin".

### Ölçüm aracı — ve ÜÇ ÖLÇÜM TUZAĞI

```bash
python tools/hook_olc.py --gercekci --tekrar 5 --karsilastir --import-dokumu
```

`--gercekci` bayrağını **KULLANIN**. Bu oturumda üç tuzağa düşüldü; hepsi
araçta kapatıldı ama elle ölçerken yine düşülebilir:

1. **Dedup kısa devresi.** `_hook_dedup_kisa_devre` aynı olayı aynı saniye
   içinde kısa devre yapar (`prompt` için ayırt edici `None`). Sıkı bir
   döngüde ölçerseniz çağrıların çoğu NO-OP olur. Ölçüldü: aralıksız 56 ms
   vs 1.1 sn arayla 210-373 ms — **%70 yanlış ölçüm.** Araç varsayılan
   olarak `--bekle 1.1` bekler; `--bekle 0` vermeyin.
2. **Boş klasör tabanı.** Boş kökte hook neredeyse hiç iş yapmaz. Gerçek
   maliyeti dava kökündeki dosya sistemi işi belirler, modül yükleme değil.
3. **Yanlış hedef.** Gerçek yol `run-hook.cmd` → `hook_giris.py`. Doğrudan
   `pipeline_kayit.py` ölçmek terk edilmiş yolu ölçer.

Araç ortamını (Python sürümü, OS, çekirdek) basar — ortamsız sayı anlamsızdır.
Absolüt sayılar yorumlayıcı sürümüne ve `.pyc` sıcaklığına göre değişir;
karşılaştırma **aynı makinede, aynı yorumlayıcıyla, arka arkaya** yapılmalıdır.
İki dalı kıyaslarken ölçüm aracının **aynı sürümünü** her iki tarafa kopyalayın.

---

## VERİ KAYBI YASAK BÖLGESİ

Bu yapılar performans gerekçesiyle **dokunulmaz**:

| Yapı | Nerede | Neden dokunulmaz |
|---|---|---|
| Append-only olay defteri | `_oa/defter/pipeline-olaylar.jsonl` | Gerçeğin kaynağı. Oku-değiştir-yaz YAPILMAZ; yalnızca satır eklenir. Paralel alt-ajan güvenliği buna dayanır. |
| Atomik `replace` | türetilmiş `pipeline-durum.json` tazeleme | Yarım yazılmış görünüm okunmasın. |
| Dosya kilitleri | `pipeline_kayit.py` (`fcntl` / `msvcrt`) | Eşzamanlı yazımda satır karışmasın. |
| "Kanıtla yazılır" kapıları | `--isle`, `--denetle`, GATE G | Model beyanı değil, script çıktısı esas. |
| Çıkış kodu aktarımı | `--denetle` → exit 1 | Teslim kapısı. Yutulursa kapı SESSİZCE ölür. |
| Müvekkil evrakı | `_oa/` (`.gitignore`'da) | Depoya ASLA girmez. |

Ayrıca:

- **Test atlamak / devre dışı bırakmak / karantinaya almak YASAKTIR.**
  Kırmızı bir test ya düzeltilir ya gerekçesiyle raporlanır.
- `tests/README.md`'deki `OA-SUIT-SAYISI` işaretçisi test eklendiğinde
  güncellenmelidir (`test_b35` bunu denetler).
- `skills/*/scripts/*.py` altına yeni bir motor eklerseniz **en az bir testte
  anılmalıdır** (`test_b37` kapsam kapısı). `KAPSAM_DEFTERI` bugün BOŞ —
  borç eklemeyin, test yazın.
- `hooks/run-hook.cmd`'nin **yürütülebilir** satırlarında `||` zincir
  operatörü YASAK (447 yapısal-arıza dersi: masaüstü uygulaması hook'u
  kabuksuz koşturur, `||` python'a argüman gider, hook sessizce ölür).

---

## Bilinen asimetri (karar bekliyor)

`run-hook.cmd`'nin **Windows kolu çıkış kodunu yutuyor**
(`python "%OA_SCRIPT%" --%~1` ardından koşulsuz `exit /b 0`), **bash kolu
`exec` ile aktarıyor.** Sonuç: `Stop` hook'undaki `--hook-denetle`'nin
exit 1'i Linux'ta bloklar, Windows'ta bloklamaz.

Dosyanın kendi açıklaması "hook ASLA bloklamaz" diyor — yani Windows'taki
davranış **kasıtlı olabilir**. Ama o zaman iki platform farklı kapı
semantiği taşıyor. Bu bir davranış kararıdır; performans oturumunda
**değiştirilmedi**, rapor edildi.

---

## Windows tarafı

`tools/pc_hizlandir.ps1` — ölç → uygula → tekrar ölç. Varsayılan mod
teşhistir (hiçbir şey değiştirmez). `-Uygula` yönetici gerektirir,
`-GeriAl` her değişikliği geri alır. En büyük kazanç Defender dışlamalarında
(her `CreateProcess` ve her `.py` okuması taranıyor).

Betik bilinçli olarak **reddettiği** şeyleri de gerekçesiyle listeler
(pagefile kapatma → veri kaybı riski; kayıt defteri temizleyicileri, "RAM
optimize ediciler", SSD defrag → ölçülebilir kazanç yok).

---

## Üslup

- Belgeler ve kod açıklamaları **Türkçe**; hukuk terminolojisi korunur.
- Açıklamalar "ne yaptığını" değil **"neden var olduğunu"** anlatır (illiyet).
  Depoda yerleşik desen: `NEDEN VAR:` başlığı.
- Ölçüm olmadan performans iddiası yazılmaz. Tahmin ise `tahmin:` diye
  işaretlenir.

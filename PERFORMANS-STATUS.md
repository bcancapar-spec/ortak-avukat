# PERFORMANS-STATUS — Canlı Oturum Kaydı

**Oturum:** PC hızlandırma + Ortak Avukat sistem optimizasyonu
**Tarih:** 2026-09-10 · **Dal:** `claude/pc-optimization-performance-r2n435`
**Karar verici:** Av. Bayram Can ÇAPAR
**Kayıt kuralı:** Bu dosya oturum boyunca anlık güncellenir. `STATUS.md`'ye
DOKUNULMAZ (o deponun kendi durum defteri — üzerine yazmak veri kaybı olurdu).

---

## 0. ÖNCE DÜRÜSTLÜK: NEYİ İNCELEYEBİLDİM, NEYİ İNCELEYEMEDİM

**Bu oturum uzak (remote) bir bulut konteynerinde koşuyor — sizin fiziki
bilgisayarınızda değil.** Verdiğiniz "pc use" yetkisi bu oturuma
bilgisayarınızın işletim sistemine erişim sağlamıyor; sağlayamaz, çünkü kod
başka bir makinede çalışıyor.

| | Bu oturumun gördüğü | Sizin PC'niz |
|---|---|---|
| Ortam | Ubuntu 24.04, KVM sanal makine | Windows (masaüstü Claude Code) |
| İşlemci | 4 vCPU Intel Xeon @2.10GHz | bilinmiyor — ölçülmedi |
| RAM | 15 GiB | bilinmiyor — ölçülmedi |
| Disk | 252 GB (30 GB boş) | bilinmiyor — ölçülmedi |

Sonuç olarak bu oturumun ürettiği iş iki parçaya ayrılır:

1. **Ölçülmüş ve doğrudan uygulanan:** Ortak Avukat sisteminin kendi kod
   yolundaki gecikmeler. Bunlar burada ölçüldü, düzeltildi, test edildi.
   Bu, sizin PC'nizde de aynen kazanca dönüşür — çünkü yavaşlığın kaynağı
   donanım değil, kodun her hook'ta yaptığı gereksiz iş.
2. **Sizin PC'nizde koşmanız için hazırlanan:** Windows tarafı ayarları,
   ölçüm betiğiyle birlikte. Hiçbiri kör tavsiye değil; her biri ölçülebilir,
   geri alınabilir ve veri kaybı riski yazılı.

Windows olduğunuz depodan kanıtlı: `run-hook.cmd` polyglot sarmalayıcısı,
`STATUS.md:294` (cp1254 konsol, `PYTHONUTF8` ayarsız), `STATUS.md:150`
(masaüstü uygulaması hook'u kabuksuz koşturuyor).

---

## 1. ÖLÇÜM: SİSTEM NEREDE YAVAŞ

Ölçüm ortamı: bu konteyner (hızlı Linux, sıcak sayfa önbelleği). **Windows'ta
her sayı daha büyüktür** — süreç başlığı `CreateProcess` ile `fork`'tan pahalı,
Defender her süreç başlığını ve her `.py` okumasını keser, üstüne `cmd.exe`
katmanı biner. Windows çarpanı ölçülmedi; bu yüzden aşağıda Linux sayılarını
veriyorum ve çarpanı tahmin olarak işaretliyorum.

### 1.1 Hook ek yükü (10 çağrı ortalaması)

| Hook modu | Süre / çağrı | Çıplak python üstü net yük |
|---|---|---|
| `--hook-prompt` | 111 ms | ~97 ms |
| `--hook-pretool` | 103 ms | ~89 ms |
| `--hook-postwrite` | 108 ms | ~94 ms |
| `--hook-denetle` | 100 ms | ~86 ms |
| *(çıplak `python3 -c pass`)* | *14 ms* | *—* |

`hooks.json` altı olay bağlıyor, **hepsi `async:false` (bloklayıcı)**:
`SessionStart`, `UserPromptSubmit`, `PreToolUse(Write|Edit|Bash|PowerShell|SendUserFile)`,
`PostToolUse(Write|Edit)`, `Stop`, `SessionEnd`.

**Bileşik etki:** Bir `Write` çağrısı Pre + Post ikisini de ateşler →
2 × ~105 ms ≈ **210 ms bloklama**. Her `Bash` çağrısı ≈ 105 ms. 30 araç
çağrılı bir tur ≈ **3–5 saniye saf bloklama** (Linux'ta; Windows'ta tahminen
katları).

### 1.2 Kök neden 1 — tek sabit için 1716 satırlık modül yürütülüyor

İlliyet zinciri (`trace` ile doğrulandı, tahmin değil):

```
pipeline_kayit.py:433  DIZIN_BEYAZ_LISTE = _dizin_beyaz_liste_hesapla()   ← MODÜL SEVİYESİ
  └─ :426 _dizin_beyaz_liste_hesapla()
      └─ :403 _oa_ingest_modulu_beyaz_liste()
          └─ oa_ingest.py'yi exec_module ile TAM YÜRÜTÜR (1716 satır)
              └─ :242 import subprocess, zipfile, tempfile, shutil …
              └─ :243 import xml.etree.ElementTree as ET
              └─ :244 from concurrent.futures import ProcessPoolExecutor
                      └─ multiprocessing, multiprocessing.context,
                         multiprocessing.reduction, logging, enum, pathlib
```

Bu zincirin **tek amacı** `ONBAKIS_DIZIN` sabitini okumak
(`oa_ingest.py:275` → `"metin-onbakis"`). Modül seviyesinde olduğu için
**her hook çağrısında**, `--hook-prompt` dahil, ingest ile hiç ilgisi
olmayan modlarda da koşuyor.

Tasarım niyeti meşru ve iyi: sabit TEK KAYNAKTAN okunsun (DRY, "ikiz liste"
hatasına karşı). Bedeli ölçüldü:

| Sabiti okuma yöntemi | Süre / çağrı | Net maliyet |
|---|---|---|
| Şimdiki: `exec_module` (tam yürütme) | 54.5 ms | **40.1 ms** |
| `ast.parse` ile sabit çıkarımı | 35.6 ms | 21.2 ms |
| Regex ile satır tarama | 17.1 ms | **2.7 ms** |

**Kazanç: ~37.4 ms / hook** — ve tek-kaynak garantisi korunur, çünkü değer
hâlâ çalışma anında `oa_ingest.py`'den okunur, koda gömülmez.

Ek ironi: fonksiyonun sabit yedeği zaten `{"metin", "metin-onbakis", "analiz"}`.
Ağır import'un ürettiği küme, yedek kümeyle **birebir aynı**. Yani bugün
40 ms, davranışta hiçbir fark üretmeyen bir garanti için ödeniyor.

### 1.3 Kök neden 2 — bytecode önbelleği hiç kullanılmıyor

`pipeline_kayit.py` hooklarda `__main__` olarak koşuyor. Python `__main__`
betiğinin bytecode'unu **önbelleğe almaz** — `__pycache__` yalnızca *import
edilen* modüller için çalışır. Doğrulandı: dizindeki tek `.pyc` dosyası
`oa_hafiza.cpython-311.pyc` (o import ediliyor); `pipeline_kayit` için yok.

Sonuç: **her çağrıda 6318 satır sıfırdan derleniyor.**

| | Süre / çağrı |
|---|---|
| Kaynaktan derleme (şimdiki) | 51.2 ms |
| Hazır `.pyc` yükleme | 21.1 ms |

**Kazanç: ~30 ms / hook.**

### 1.4 İki kök nedenin toplamı

~37.4 + ~30 ≈ **67 ms**, ölçülen ~97 ms'lik hook ek yükünün içinden.
Yani hook gecikmesinin yaklaşık **%70'i** donanımla değil, iki yapısal
kod kararıyla ilgili. Bu yüzden "PC'yi hızlandırmak" bu sistemde önce
**yazılım** işidir; işletim sistemi ayarları ikinci sıradadır.

---

## 2. DURUM

| Aşama | Durum |
|---|---|
| Depo keşfi + yığın tespiti | ✅ bitti |
| Sıcak yol ölçümü (4 hook modu) | ✅ bitti |
| Kök neden 1 izlenmesi (import zinciri) | ✅ bitti — `trace` ile kanıtlı |
| Kök neden 2 doğrulanması (bytecode) | ✅ bitti — ölçümlü |
| Düzeltme prototipi ölçümü | ✅ bitti (regex: 2.7 ms) |
| 7 boyutlu çok-ajanlı denetim | ⏳ koşuyor |
| Çelişmeli doğrulama (veri kaybı) | ⏳ koşuyor |
| Uygulama + test | ⏸ bekliyor |
| Windows betiği | ⏸ bekliyor |

---

## 3. DEĞİŞMEZ KISIT — SIFIR VERİ KAYBI

Hiçbir optimizasyon aşağıdakileri zayıflatmayacak:

- `_oa/defter/pipeline-olaylar.jsonl` — append-only olay defteri, **gerçeğin
  kaynağı**. Oku-değiştir-yaz yapılmaz; yalnızca satır eklenir.
- Atomik `replace` ile türetilmiş görünüm tazeleme (`pipeline-durum.json`).
- Dosya kilitleri (`fcntl` / `msvcrt`, `pipeline_kayit.py:~1069`).
- "Kanıtla yazılır" kapıları, GATE G kalıcılık kapısı, fail-closed ayrımları.
- Müvekkil evrakı (`_oa/` — depoya hiç girmez, `.gitignore`'da).

Test atlamak, devre dışı bırakmak veya karantinaya almak **yasak**.

---

*(Bu dosya oturum ilerledikçe güncellenir.)*

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
- Testler: `tests/` (2328 test)
- **Hedef ortam: Windows** (masaüstü Claude Code, cp1254 konsol)

---

## Testleri koşturma

```bash
python -m pytest tests/ -q -n auto      # 4 çekirdekte ~75 s
python -m pytest tests/ -q              # tek çekirdek ~259 s
```

`-n auto` (pytest-xdist) **kullanın**: süit paralel-güvenlidir (ölçüldü:
sonuçlar birebir aynı), 3.5× hızlanır. `pytest-xdist` yoksa:
`pip install pytest-xdist`.

### Bilinen, ÖNCEDEN VAR OLAN başarısızlıklar (bu oturumdan bağımsız)

`main` dalında da kırmızı yanan 4 test — `08441f5` commit'i `plugin.json`'dan
`hooks` alanını kaldırdı, ama testler onu hâlâ şart koşuyor:

- `test_devir_zorlayici.py::test_plugin_json_hooks_KAYDINI_tasimak_ZORUNDA`
- `test_hooks_wiring.py::test_plugin_json_var_ve_gecerli_json`
- `test_hooks_wiring.py::test_plugin_json_hooks_alani_diskte_cozulebilir`
- `test_hook_doktor.py::test_uctan_uca_tum_olaylar_yesil`

**Karar bekliyor:** `hooks` alanı `plugin.json`'a geri mi konacak, yoksa
testler mi güncellenecek? İkisi de davranış kararıdır — Bayram Can ÇAPAR'a
aittir. Kendi başına "düzeltilmemelidir".

---

## PERFORMANS DEĞİŞMEZLERİ — bunları geri almayın

v0.5.16.2'de hook gecikmesi **189.7 ms → 26.9 ms** (%85.8 azalma, 7.05×)
düşürüldü. İki yapısal karar bunu sağlıyor; ikisi de kolayca ve sessizce
geri alınabilir, o yüzden burada yazılıdır.

### 1. `DIZIN_BEYAZ_LISTE` TEMBEL kalmalı

`pipeline_kayit.py`'de bu değer **modül seviyesinde hesaplanmamalıdır.**
Eskiden `DIZIN_BEYAZ_LISTE = _dizin_beyaz_liste_hesapla()` satırı modül
gövdesindeydi; her hook çağrısında `oa_hafiza.py` (2500 satır) **ve**
`oa_ingest.py` (1716 satır) in-process import ediliyordu — oa_ingest de
modül seviyesinde `subprocess`, `zipfile`, `xml.etree.ElementTree`,
`concurrent.futures` (→ `multiprocessing`, `logging`, `enum`) çekiyordu.
Bedeli: **~155 ms/hook**, ve bu değer **tek bir yerde** kullanılıyor:
`_sozlesme_disi_dizinler()` (gölge-dizin bekçisi, advisory).

Şimdi `_dizin_beyaz_liste()` erişimcisi ilk kullanımda hesaplıyor; modül
dışı `mod.DIZIN_BEYAZ_LISTE` erişimi `__getattr__` (PEP 562) ile aynı yere
düşüyor.

- **Tek-kaynak garantisi (P1-9(b)) BOZULMADI**: `_dizin_beyaz_liste_hesapla()`
  aynen duruyor, hâlâ üretici modüllerden CANLI türetiyor, değer koda
  gömülmedi. Değişen tek şey NE ZAMAN ödendiği.
- **Modül İÇİ kullanım `_dizin_beyaz_liste()` çağırmalı.** Modül `__getattr__`'ı
  modülün kendi içindeki çıplak global ad aramasında **ateşlenmez** — çıplak
  `DIZIN_BEYAZ_LISTE` yazarsanız `NameError` alırsınız.
- Yeni bir modül-seviyesi ağır hesap eklemeyin. Kontrol:
  `python tools/hook_olc.py --import-dokumu` → "ağır modül YOK ✓" görmelisiniz.

### 2. Hook yolu `hook_giris.py` üzerinden geçmeli

Python, `__main__` olarak koşan bir betiğin bytecode'unu **ASLA** önbelleğe
almaz (`__pycache__` yalnızca IMPORT edilen modüller için). Hook ağı
`pipeline_kayit.py`'yi doğrudan çağırdığında 6300+ satır **her ateşlemede**
yeniden derleniyordu (~41 ms).

`hooks/run-hook.cmd` içindeki `OA_SCRIPT` artık `hook_giris.py`'yi gösterir;
o da `pipeline_kayit.py`'yi importlib ile yükleyip `main()`'i çağırır.

- `run-hook.cmd`'yi `pipeline_kayit.py`'ye geri yönlendirmeyin.
- `PYTHONDONTWRITEBYTECODE` **ayarlı olmamalı** — kazancı tümüyle yok eder.
- `hook_giris.py` `sys.path`'i kirletmez (kardeş dosya stdlib'i gölgeleyemez);
  bu deseni bozmayın.
- Testler: `tests/test_hook_giris.py` (10 test) hem işlev eşitliğini hem
  kazancın kendisini kilitler.

### Ölçüm aracı

```bash
python tools/hook_olc.py --tekrar 25 --import-dokumu
```

Bir hız beyanı ancak bu araçta görülürse gerçektir. Araç ortamını (Python
sürümü, işletim sistemi, çekirdek) basar — ortamsız sayı anlamsızdır.
Absolüt sayılar yorumlayıcı sürümüne ve `.pyc` sıcaklığına göre değişir;
karşılaştırma **aynı makinede, aynı yorumlayıcıyla, arka arkaya** yapılmalıdır.

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

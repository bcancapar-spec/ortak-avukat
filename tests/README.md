# Test Mimarisi — mühendisler için

<!-- OA-SUIT-SAYISI: 1763 -->

> **Süit büyüklüğünün TEK kaynağı yukarıdaki `OA-SUIT-SAYISI` işaretçisidir.**
> `tests/test_v0514_vitrin.py` bu sayıyı her koşuda `pytest --collect-only`
> ile karşılaştırır; ayrıştığı an kırmızı yanar. Test ekleyen/silen, YALNIZ
> bu satırı günceller — başka hiçbir belgede süit sayısı yazmaz
> (v0.5.14/B-35: sayı üç ayrı yerde üç ayrı ve üçü de yanlıştı).

> Bu belge, süiti **geliştirici gözüyle** anlatır: desenler, sözleşmeler,
> koşum kuralları ve yeni test ekleme disiplini. Avukat-dili özet ana
> README'nin "Mekanik test altyapısı" bölümündedir.

## Şekil

- Saf `pytest`, harici test bağımlılığı yok; parametrize varyantlarıyla
  toplanan sınama sayısı yukarıdaki işaretçidedir.
- Tam süit ~7 dk (Windows, tek makine). CI: GitHub Actions matrisi —
  **Windows + Ubuntu × Python 3.12/3.13** + ayrı `aile_dogrula` yapısal
  denetimi. Kural: **CI yeşermeden sürüm etiketi atılamaz.**
- Adlandırma sözleşmesi: `test_vXYZ_*.py` = bir saha karnesinden doğan
  **sürüm-reçetesi paketi** (süitin en kalabalık sınıfı). Dosya docstring'i,
  paketi doğuran saha kanıtını atıflar — test, gerekçesiz yaşayamaz.

## Çekirdek desenler

### 1. Modül yükleme: paket yok, `importlib` var

Skill scriptleri Python paketi değildir (her skill kendi `scripts/` dizininde
bağımsız yaşar). Testler modülleri şu kalıpla yükler:

```python
spec = importlib.util.spec_from_file_location("benzersiz_ad", yol)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
```

Her test dosyası **benzersiz modül adı** kullanır (`v0511_pk` gibi) — aynı
scriptin iki testte iki kez yüklenmesi çakışma üretmez; modül-düzeyi global
durum (ör. payload önbelleği) testler arasına sızmaz.

### 2. Sentetik dava kökü: her test kendi dünyasını kurar

Standart kurulum `tmp_path` üzerinde `_oa/` iskeletinin gereken kadarını
elle inşa eder (defter dizini, sentetik künye, kurgu taslak). **Anayasa m.7
test koduna da uygulanır:** gerçek kişi adı, gerçek dosya numarası, gerçek
yerel yol test koduna GİREMEZ — kimlikler daima kurgudur ("2024/123 Esas").
Commit öncesi sızıntı taraması (`git grep`) disiplinin parçasıdır; bu kural
bir kez sabit-yol sızıntısıyla öğrenildi ve o günden beri mekaniktir.

### 3. Ağ kapısı: tek yoklama, görünür atlama

Bazı testler gerçek `npx udf-cli` yazıcısı ister (login-gated, ağ gerekir).
Politika `tests/oa_udf_ortam.py` + `conftest.py`'dedir:

- Ortam **koşu başına BİR KEZ** yoklanır (her testte ayrı ağ çağrısı yasak).
- Sonuç `pytest_report_header` ile her koşunun başına basılır — **sessiz
  atlama yasak**: yazıcı yoksa hangi testlerin neden atlandığı görünür.
- Gerçek-yazıcı isteyen testler `gercek_udf_yazici_gerekli` işaretiyle
  ayrılır; geri kalan her şey **tamamen ağsız ve deterministiktir**.
- Fail-closed testleri tersini de kilitler: araç YOKKEN üretim denemesi
  `exit != 0` vermeli ve **hiçbir çıktı dosyası bırakmamalıdır**.

### 4. Hook testleri: payload simülasyonu

Hook'lar stdin'den JSON payload okur (Claude Code hook sözleşmesi). İki
katmanda test edilir:

- **Süreç-dışı (CLI):** `subprocess` ile `pipeline_kayit.py --hook-pretool`
  koşulur, payload stdin'e verilir; çıktıdaki `permissionDecision` ("ask")
  ve deftere düşen olay doğrulanır.
- **Süreç-içi:** `monkeypatch.setattr(mod, "_hook_stdin_payload_oku",
  lambda: veri)` ile payload enjekte edilir — stdin'in tek-okunurluk
  sözleşmesi (modül önbelleği dahil) ayrıca test edilir.

### 5. Sözleşme sınıfları — neyin testi yazılır?

Süit, davranışları dört sözleşme sınıfına göre kilitler:

| Sözleşme | Örnek doğrulama |
|---|---|
| **Fail-closed kapı** | Eksik script/geçersiz girdi → `exit 1` + RED makbuzu; kapı atlanırsa teslim durur; "geçti" çıktısı ancak fiilî koşumla |
| **Asla-fırlatmaz yardımcı** | Bozuk JSON, yok dizin, kilitli dosya → istisna YOK, güvenli varsayılan döner (hook'lar ana akışı asla öldüremez) |
| **Append-only + idempotent** | Defter yalnız sona ekler (imza alanıyla); nabız/kilit fonksiyonları ikinci çağrıda durumu bozmaz; saniye-içi çift ateşleme dedup'lanır |
| **Atomik yazım** | Kalıcı dosyalar `tmp + os.replace` ile yazılır; yarıda kesilme yarım dosya bırakmaz; üretim+mühür tek işlem (mühürsüz ürün senaryosu kırmızı) |

Bayt-düzeyi UDF invaryantları ayrı bir ailedir: zip girdileri, stil imzası,
offset/uzunluk tutarlılığı, kenar ölçüleri — ve **imzalı-nüsha profili**
(zip'te imza girdisi varken editör-kaynaklı float/boşluk sapmalarına
tolerans; imzasız dosyada sıfır tolerans, iki yön de testli).

### 6. TDD + kanıt zinciri

- **Önce kırmızı:** her onarım, kusuru yeniden üreten testin BAŞARISIZ
  görülmesiyle başlar; commit'e ancak yeşile dönmüş hâli girer.
- **Kanıt zinciri:** bozuk teşhis aracı onarılmadan önce, bozukluğu fiilen
  gösteren koşum kayda geçirilir ("bozuk hali sahte ARIZA basıyordu" →
  onarım → aynı koşum temiz). Denetçiler de denetlenir: `aile_dogrula`,
  parmak-izi ve şema denetçilerinin kendileri test kapsamındadır.
- Davranış değişikliği bilinçli olduğunda eski testi güncellemek meşrudur —
  ama gerekçesi test docstring'ine ve değişiklik günlüğüne yazılır
  (ör. çift-uzantı ad şeması değişiminde eski adı kilitleyen testler,
  yeni sözleşmeye taşındı).

## Koşum tarifleri

```bash
# tam süit
python -m pytest tests -q

# tek paket / tek test / desenle
python -m pytest tests/test_v0511_kit_guvenlik.py -q
python -m pytest tests -q -k "muhur"

# ilk kırmızıda dur (hızlı teşhis)
python -m pytest tests -q -x

# yapısal aile denetimi (süitten ayrı ikinci kapı)
python plugins/ortak-avukat/skills/oa-usta/scripts/aile_dogrula.py plugins/ortak-avukat/skills
```

Windows notu: Türkçe çıktı için `PYTHONUTF8=1` önerilir. Ubuntu notu:
kabuk sarmalayıcıları exec-bit ister (`update-index --chmod=+x`) — CI'da
bir kez `exit 126` ile öğrenildi.

## Yeni test ekleme kontrol listesi

1. Kusur bir saha karnesine ya da ölçüme bağlanabiliyor mu? Bağlantıyı
   docstring'e yaz (kanıtsız test = gerekçesiz kural).
2. Senaryo tamamen sentetik mi (m.7)? Gerçek ad/yol/numara sıfır mı?
3. Ağsız mı? Değilse `gercek_udf_yazici_gerekli` ile işaretle ve atlama
   gerekçesinin görünür olduğunu doğrula.
4. Önce KIRMIZI koştur; onarım sonrası yeşili aynı komutla kanıtla.
5. Tam süit + `aile_dogrula` + (sürüm çıkacaksa) dört sürüm damgasının
   birlikte arttığını doğrula.

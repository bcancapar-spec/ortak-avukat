# Heyet raporu — USUL üyesi (depo sözleşmesi, kapılar, kayıt) · 2026-10-16

**Dal:** `denetim/fable-2026-10-15` · **HEAD:** `8be918f` · **Taban:** `origin/main` = `753e48c` (v0.6.0) ·
**Kapsam:** `origin/main..HEAD` · **Push:** yok.
**Ölçüm ortamı:** Windows · `py -3.14` (Python 3.14.8) · pytest 9.1.1 + pytest-xdist · ruff 0.17.0 ·
`PYTHONUTF8=1 OA_TEST_UDF_YAZICI=0` · her pytest çağrısı `-p no:cacheprovider`.
**Yöntem:** Paylaşılan çalışma ağacında başka oturumun commit'siz işi durduğu için süit ve dosya yazan
kapılar `git worktree add --detach … HEAD` ile açılan geçici, temiz bir worktree'de koşuldu
(HEAD `8be918f`; `git status --short` boş). İş bitince geçici worktree `git worktree remove --force`
ile kaldırıldı ve `git worktree list`'ten düştüğü doğrulandı. Bu rapor beyana değil ölçüme dayanır;
alt ajan raporları (`ajan-raporlari/`) ve depo dışı devir notları yalnız VERİ olarak okundu (anayasa
m.11). Rapora kişi adı, müvekkil, dosya numarası ve mutlak yerel yol yazılmadı (m.7).

## 1. Kapsam ve yöntem

### 1.1 Commit listesi (yeniden eskiye · `git log --oneline origin/main..HEAD`)

| # | Commit | Konu | İçerik sınıfı (`git diff-tree -M --name-status`) |
|---|---|---|---|
| 1 | `8be918f` | Heyet: güvenlik üyesi tanımındaki mutlak yol örneği kaldırıldı | belge (`docs/heyet/ajanlar/`, 1 satır) |
| 2 | `c5f739f` | Heyet: üç kıdemli avukat denetçi ajan tanımı ve push öncesi protokol | belge (`docs/heyet/`, 4 dosya) |
| 3 | `08aef92` | Kök katalog script sayıları ölçümle; iki vitrin tek kapıda; kayıtlar | vitrin + test + kayıt (5 dosya) |
| 4 | `934e212` | Excel'de gizli katman ölçülür (v0.5.19 kalemi) | motor (oa-ingest) + 28 test + kayıt (14 dosya) |
| 5 | `8a1c882` | Vitrin: eklenti README'si katmanlı düzende; parça tablosu ölçümle kilitli | vitrin + 4 test (4 dosya) |
| 6 | `99ef95f` | Kayıtlar: DENETIM belgesi, CHANGELOG, STATUS/YOL-HARITASI, sözlük, parça günlükleri | kayıt (11 dosya) |
| 7 | `200dda5` | Depo hijyeni: güvenlik bildirimi ve PR şablonu | `.github` (2 dosya) |
| 8 | `cf425d9` | Vitrin: hukukçu, hâkim-savcı ve geliştirici için katmanlı README | vitrin (1 dosya) |
| 9 | `45a6d2e` | Kök dizin sadeleşti: tarihî kayıtlar docs/arsiv/; bağlantı kapısı | bağlantı yeniden yazımı + test (12 dosya; taşıma YOK — bkz. U-1) |
| 10 | `47bba4d` | Metin hijyeni kapısı istisnasız | 2 test dosyası + 13 dosya taşıma `R100` (bkz. U-1) |
| 11 | `30495ab` | Sürüm damgası: pyproject.toml da denetlenir (0.1.0 → 0.6.0) | motor (oa-usta) + 3 test + pyproject |
| 12 | `7fcbb22` | Kaynak hijyeni kapısı: ruff hata sınıfı + CI lint işi; ham karakterler kaçışa | `ruff.toml`, CI, 2 motor, test dosyaları (F401 temizliği) |
| 13 | `d9d358a` | Numaralı liste kaynak numarasını korur: `<ol start>` | motor (oa-dilekce) + 2 test |
| 14 | `52de60f` | Vitrin: avukatın bekleyen README düzeltmeleri dala alındı | vitrin (1 dosya) |

- `git rev-list --count origin/main..HEAD` → **14** (koşum notu "13" diyordu; bkz. N-1).
- `git diff --stat origin/main...HEAD` → `90 files changed, 3134 insertions(+), 675 deletions(-)` (koşum notuyla birebir).
- Ebeveyn zinciri (`git log --topo-order --format='%h %p'`) tarih sırasıyla aynı; sapma yok.

### 1.2 Koşulan kapılar (geçici worktree, HEAD `8be918f`)

| Kapı | Komut | Son satır |
|---|---|---|
| Tam süit (paralel, CI kipi) | `PYTHONUTF8=1 OA_TEST_UDF_YAZICI=0 py -3.14 -m pytest tests -q -n auto -m "not perf" -p no:cacheprovider -rsfE` | `3800 passed, 12 skipped in 93.99s (0:01:33)` |
| Zamanlama (seri) | `… -m pytest tests -q -m perf -p no:xdist -p no:cacheprovider` | `1 passed, 3812 deselected in 7.45s` |
| Toplanan test | `… -m pytest tests --collect-only -q -p no:cacheprovider` | `3813 tests collected in 5.78s` = `tests/README.md` `OA-SUIT-SAYISI: 3813` |
| Aile yapı denetimi | `py -3.14 plugins/ortak-avukat/skills/oa-usta/scripts/aile_dogrula.py plugins/ortak-avukat/skills` | `Denetlenen parça: 20` · `AİLE YAPI DENETİMİ TEMİZ.` (exit 0) |
| Kaynak hijyeni | `py -3.14 -m ruff check .` | `All checks passed!` (ruff 0.17.0) |
| Vitrin künyesi | `py -3.14 tools/satir_sayaci.py --yaz` | `güncel: README.md` · `güncel: plugins/ortak-avukat/README.md`; ardından `git status --short` boş (hiçbir dosya değişmedi) |
| Kurulu eklenti | `py -3.14 tools/hook_doktor.py --kurulu` | `SONUÇ: TÜM MEKANİK KONTROLLER GEÇTİ ✓` (servis edilen nesil `0.6.0 → 0.6.0`; bkz. N-4) |

12 atlama ortam gerekçeli ve görünür (`-rs`): 11'i udf-cli oturumu yok (`test_teslim_paketi` ×2,
`test_teslim_makbuz` ×2, `test_udf_yaz` ×6, `test_udf_metin` ×1), 1'i `OA_SAHA_REFERANS` tanımsız
(`test_oa_ingest_ocr_nobetci`). Kırmızı: 0.

### 1.3 Kayıt disiplini ölçümü (commit'li ağaç)

- **OA-SUIT-SAYISI ilerlemesi** (her commit'te `git show <h>:tests/README.md`): 3769 (taban) → 3771
  `d9d358a` → 3776 `7fcbb22` → 3779 `30495ab` → 3779 `47bba4d` → 3781 `45a6d2e` → 3781 (`cf425d9`,
  `200dda5`, `99ef95f`) → 3785 `8a1c882` → 3813 `934e212` → 3813 (`08aef92`, `c5f739f`, `8be918f`).
  Commit mesajlarındaki sayılarla birebir; HEAD'de gerçek toplama (3813) ile birebir.
- **Sürüm damgaları (HEAD):** `plugin.json` 0.6.0 · `marketplace.json` 0.6.0 · `pyproject.toml` 0.6.0 ·
  `STATUS.md` 0.6.0 · `YOL-HARITASI.md` v0.6.0 · kök README `**Sürüm:** 0.6.0` · eklenti README
  `**Sürüm:** 0.6.0` · `OA_SURUM = "0.6.0"` (`teslim_paketi.py:1245`, `pipeline_kayit.py:172`).
  Sürüm değişmedi; damgalar tutarlı. Sürüm numarası avukat kararı (DENETIM §7/4).
- **CHANGELOG:** "Sürümsüz — BAĞIMSIZ KOD VE VİTRİN DENETİMİ (2026-10-15)" kaydı; B-1, B-2…B-5, B-6,
  B-7/B-11, Excel gizli katman, Vitrin (kök + eklenti README, `8a1c882`), Depo hijyeni, Ölçüm
  (`CHANGELOG.md:361`: 3800 · 12 · 0 · 3813) ve "Dokunulmayan" maddeleri var. Heyet commit'leri için
  madde YOK (bkz. U-2).
- **Parça günlükleri** (`git diff --stat origin/main...HEAD -- '*degisiklik-gunlugu.md'`): oa-dilekce +1
  (B-1 `md_udf_html.py`), oa-ingest +2 (B-3 `udf_md.py`; Excel gizli katman), oa-pipeline +1 (B-4
  `oa_hafiza.py`), oa-usta +1 (B-6 `surum_isaretcileri`). Değişen her motor kendi parçasının
  günlüğünde (`git ls-tree` ile konum doğrulandı: `md_udf_html.py` → oa-dilekce, `udf_md.py` → oa-ingest,
  `oa_hafiza.py` → oa-pipeline, `aile_dogrula.py` → oa-usta, `belge_guvenlik.py` → oa-ingest).
- **STATUS:** satır 6–14 tarihli 2026-10-15 notu ve ölçüm cümlesi (3800 · 12 · 0 · 3813); satır 38
  Excel kalemi üstü çizili. **YOL-HARITASI:** satır 28–29 Excel kalemi kapatıldı, satır 35–39 denetim
  dalı notu. **DENETIM §6:** ölçüm tablosu + Görev 1–8 kayıtları.
- **"Önce kırmızı" izi:** diff'te eklenen `NEDEN VAR` satırı 4 (`test_kaynak_hijyeni.py`,
  `test_belge_baglantilari.py`, `test_eklenti_vitrini.py`, `test_v0519_excel_gizli_katman.py`).
  Commit mesajında kırmızı → yeşil izi: `d9d358a`, `30495ab`, `45a6d2e`, `8a1c882`, `934e212`,
  `8be918f` var; `7fcbb22`, `47bba4d`, `08aef92` yok (bkz. N-2).
- **Belgeler Türkçe:** `docs/heyet/**`, `.github/SECURITY.md`, `.github/PULL_REQUEST_TEMPLATE.md`,
  `docs/DENETIM-2026-10-15.md` okundu; Türkçe.

### 1.4 Alt ajan raporlarının ağaçta doğrulanması (beyan → ölçüm)

| İddia | Ölçüm | Sonuç |
|---|---|---|
| `08aef92`: `test_eklenti_vitrini.py` 4 test; OA-SUIT-SAYISI 3813 değişmedi | `grep -c '^def test_'` → 4; işaretçi 3813 → 3813 | doğru |
| `08aef92`: kök README üç başlık (çekirdek · 1, oa-pipeline · 11, oa-ingest · 6) | `README.md:782/792/812`; disk (`git ls-tree HEAD … scripts/*.py`): ortak-avukat 1, oa-pipeline 11, oa-ingest 6; öbür 13 başlık da diskle birebir; scriptsiz 4 parçanın başlığı sayı taşımıyor, disk 0 | doğru |
| `08aef92`: CHANGELOG Vitrin + Ölçüm, DENETIM §6, STATUS cümlesi | §1.3 | doğru |
| `08aef92` ölçümü: 3800 · 12 · 0; toplanan 3813 | bu koşum: 3800 · 12 · 0 (93,99 s); 3813 | doğru (süre ayrı koşu) |
| `8a1c882`: eklenti README 615 → 690 satır, CRLF korundu, 4 test, 3781 → 3785 | `wc -l` 615 → 690; CRLF 690/690; 4; işaretçi 3781 → 3785 | doğru |
| `934e212`: 14 dosya; `belge_guvenlik.py` +553; 28 test; kapı `SURUM` 1.2; 128 MB / 64 MB sınırları | `git show --stat` 14 dosya, 553 satır; 28 `def test_` (parametrize 0); `belge_guvenlik.py:94` `SURUM = "1.2"`, `:157` ve `:161` sabitler | doğru |
| `8be918f`: mutlak yol örneği kaldırıldı; yerel kopya (`.claude/agents`) özdeş | diff tek satır (sürücü harfli profil yolu örneği → sözle anlatım); `diff -q` üç tanım dosyası özdeş | doğru |
| `c5f739f`/`8be918f` yalnız belge ekler; tam süit ayrıca koşulmadı (beyan) | dosya listesi yalnız `docs/heyet/**`; bu koşumun tam süiti HEAD'de yeşil | doğru |
| "8 kapı dosyası 82 yeşil" / "yedi kapı dosyası + yeni test 82 yeşil" | ölçülmedi (tam süit kapsıyor) | — |

Rapor ile diff ayrışan iddia bulunmadı. Ancak raporların dayandığı DENETIM §6 ve `45a6d2e` mesajının
commit atfı bir noktada ağaçla uyuşmuyor (U-1).

## 2. Bulgular

### U-1 · UYARI · `47bba4d` commit içeriği mesajından geniş: arşiv taşıması fiilen bu commit'te

- **Dosya/kanıt:** `git diff-tree -M --no-commit-id --name-status -r 47bba4d` → 13 `R100`
  (`PERFORMANS-STATUS.md` → `docs/`, `SICRAMA-NOTU.md` → `docs/`, 11 tarihî kayıt → `docs/arsiv/`) +
  `tests/test_kaynak_hijyeni.py`, `tests/test_v0518_metin_hijyeni.py`; `git show --stat 47bba4d` →
  `15 files changed, 19 insertions(+), 26 deletions(-)`. Mesaj yalnız metin hijyeni istisnasını
  anlatır; taşımadan söz etmez. `45a6d2e` ("Kök dizin sadeleşti…") `git diff-tree -M` ile 12 dosya:
  bağlantı yeniden yazımları, `docs/arsiv/README.md`, `tests/test_belge_baglantilari.py` — taşımanın
  kendisi yok. `45a6d2e` mesajı ("11 kayıt docs/arsiv/ altına … taşındı") ve DENETIM §6 "Görev 4 tamam
  (`45a6d2e`)" taşımayı `45a6d2e`'ye atfeder.
- **Ara durum kanıtı:** `git show 47bba4d:CHANGELOG.md` içinde köke işaret eden
  `KARNE-307 / KARNE-1865 / SAHA-SONUCU / BASARI / OLCUMLER` bağlantısı 13 (hedefler o commit'te kökte
  yok → kırık); `45a6d2e`'de 0. Bağlantı kapısı `45a6d2e`'de doğduğu için `47bba4d`'de kırmızı test yoktu.
- **Müvekkile etkisi:** üretim davranışı değişmez (HEAD yeşil). Kayıt zinciri yanıltıcı: `47bba4d` tek
  başına geri alınırsa arşiv de geri gider ve bağlantı kapısı kırılır; inceleyen avukat ya da `git bisect`
  taşımayı yanlış commit'te arar. Depo sözleşmesi "her commit kendi kanıtını taşır" (`tests/README.md`
  §6 kanıt zinciri) bu iki commit'te tutmuyor.
- **Onarım:** (a) asgari — DENETIM §6 "Görev 2" ve "Görev 4" satırlarına ve CHANGELOG "Kök dizin ve
  bağlantı kapısı" maddesine "taşıma fiilen `47bba4d` ile girdi, bağlantılar `45a6d2e`'de düzeltildi"
  notu; (b) tam — dal push edilmediği için mümkün: avukat kararıyla tarihçe düzeltmesi (taşımayı
  `45a6d2e`'ye almak; commit kimlikleri değişir, DENETIM ve heyet raporlarındaki atıflar güncellenir).

### U-2 · UYARI · Heyet commit'leri (`c5f739f`, `8be918f`) CHANGELOG ve STATUS'ta kayıtsız

- **Kanıt:** `git diff origin/main...HEAD -- CHANGELOG.md STATUS.md YOL-HARITASI.md docs/DENETIM-2026-10-15.md | grep -E '^\+' | grep -ciE 'oa-heyet|docs/heyet|kıdemli avukat|denetim kurulu'`
  → 0; `git show HEAD:CHANGELOG.md | grep -c docs/heyet` → 0. `docs/heyet/README.md` protokol m.4
  "CHANGELOG'a tek satır"ı KARAR aşamasına bırakıyor; ama `c5f739f` depo sözleşmesine yeni bir
  push-öncesi kapı ekliyor (ajan tanımları + protokol) ve bu değişiklik defterinde görünmüyor.
- **Müvekkile etkisi:** doğrudan yok. Sözleşme etkisi: "her commit için CHANGELOG + STATUS" kuralı
  iki commit'te boş; heyet kapısının ne zaman doğduğu CHANGELOG'dan okunamıyor.
- **Onarım:** KARAR.md commit'inde CHANGELOG "Sürümsüz" kaydına "Heyet" maddesi (`c5f739f`,
  `8be918f`, bu koşum ve karar) + STATUS'a 2026-10-16 tarihli not.

### U-3 · UYARI · `docs/heyet/README.md`: "`.claude/agents/` git'te yok sayılan dizin" iddiası depoda karşılıksız

- **Kanıt:** `git show HEAD:.gitignore | grep -c claude` → 0. `git check-ignore -v
  .claude/agents/oa-heyet-usul.md` → yok sayma bu makinenin yerel `info/exclude` dosyasından (satır 9
  `.claude/`), depodan değil. `git ls-files .claude` → 0 (altında izlenen dosya yok).
- **Müvekkile etkisi:** dolaylı. Taze klonda protokolün "`cp docs/heyet/ajanlar/*.md .claude/agents/`"
  adımı izlenmeyen dosya üretir; Claude Code `.claude/` altına yerel ayar dosyaları da yazar;
  yanlışlıkla commit riski (yerel yol / izin listesi sızıntısı — B-38'in koruduğu sınıf).
- **Onarım:** `.gitignore`'a `.claude/` satırı (izlenen dosya 0 olduğu için bedelsiz) ya da README
  cümlesinin "yerel exclude ile yok sayılır" diye düzeltilmesi; ilki tercih.

### N-1 · NOT · Koşum notu "13 commit" diyor; ölçüm 14

- `git rev-list --count origin/main..HEAD` → 14; notun kendi hash listesi de 14 hash sayıyor.
  Rapor/diff ayrışması değil, sayım hatası. KARAR.md'de 14 yazılmalı.

### N-2 · NOT · "Önce kırmızı" izi üç commit mesajında eksik; iki test dosyasında `NEDEN VAR` başlığı yok

- `7fcbb22`: kırmızı hâl mesajda değil, DENETIM §1 tablosunda (ruff 54 / 516 bulgu → temiz).
  `47bba4d`: kilit testi; zaten kaçışlı ifadeyi kilitler, kırmızı görülmesi yapısal olarak mümkün değil,
  mesaj bunu söylemiyor. `08aef92`: test kök kataloğa genişletildi; kök başlıklar bayat olduğu için
  kırmızı görülmüş olmalı, kayıt yok. `tests/test_md_udf_html.py` ve `tests/test_v0516_G.py` yeni
  testleri `NEDEN VAR` başlığı taşımıyor; gerekçe docstring'de (B-1 / B-6 atfı) var.
- Etki: yok; kanıt zincirinin okunabilirliği. Onarım: sonraki commit'lerde tek cümle ("kırmızı görüldü: …").

### N-3 · NOT · `STATUS.md` başlık damgası bayat

- `STATUS.md:3` `**Tarih:** 2026-10-12`; gövde 2026-10-15 notu ve ölçüm cümlesi taşıyor (satır 6–14).
  Onarım: KARAR commit'inde başlık tarihi tazelenir.

### N-4 · NOT · `hook_doktor --kurulu` dalın kodunu değil kurulu önbelleği ölçer

- Çıktı: servis edilen nesil `0.6.0 → 0.6.0`. Sürüm değişmediği için kurulu kopyanın bu dalın
  içeriğini taşıyıp taşımadığı araçla ayırt edilemez; "6/6 kanca sağlıklı" bulgusu kurulu kopyaya
  aittir. Dal içeriğiyle kurulum ölçülmedi (bkz. §4).

### N-5 · NOT · Paylaşılan ağaçta `test_b35` kırmızı — karar dışı işin etkisi

- Paylaşılan ağaçta salt okunur koşum (`PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`;
  `tests/test_belge_baglantilari.py tests/test_v0518_metin_hijyeni.py tests/test_v0514_vitrin.py`):
  `test_b35_suit_sayisi_isaretcisi_gercek_toplama_ile_ayni` → `beyan edilen: 3813 · gerçek toplanan:
  3850`; aynı koşumda bağlantı, metin hijyeni ve b38 kapıları 10 geçti. Kaynak: izlenmeyen
  `tests/test_teyit_kanali.py` + `tests/test_kanal_bagimsiz_metin.py` (bölüm 5). Commit'li ağaçta
  yeşil (§1.2).

## 3. Karar önerisi

**ŞARTLI PUSH.** BLOKLAYICI yok: HEAD'in temiz kopyasında altı kapının altısı yeşil (3800 · 12 · 0;
perf 1; aile TEMİZ; ruff temiz; künye güncel; kurulu eklenti ✓), sayaç ve damgalar tutarlı, kayıtlar
(U-2 dışında) yerinde, alt ajan beyanları ağaçla örtüşüyor. Şartlar (push öncesi, aynı dalda; 1–3 tek
kayıt commit'iyle karşılanabilir):

1. **U-2:** CHANGELOG "Sürümsüz" kaydına Heyet maddesi + STATUS'a 2026-10-16 notu (KARAR.md commit'iyle).
2. **U-1:** DENETIM §6 (Görev 2 / Görev 4) ve CHANGELOG'a "taşıma fiilen `47bba4d`'de" notu; tarihçe
   düzeltmesi istenirse avukat kararı (dal push edilmemiş, mümkün).
3. **U-3:** `.gitignore`'a `.claude/` (ya da README cümlesi düzeltilir).
4. Heyet dosyaları (`docs/heyet/2026-10-16/**`, KARAR.md) commit'lendikten sonra commit'li ağaçta
   `tests/test_belge_baglantilari.py`, `tests/test_v0518_metin_hijyeni.py`, `tests/test_v0514_vitrin.py`
   yeniden yeşil görülür (b38 yalnız `git ls-files` tarar; bu rapor ve dört ajan raporu yazıldığında
   izlenmeyen dosyaydı — aynı üç b38 deseni, Cf sınıfı ve göreli bağlantı hedefiyle elle tarandı: 0 bulgu).
5. Bölüm 5'teki commit'siz iş push kapsamına GİRMEZ; girecekse önce commit, `OA-SUIT-SAYISI`
   (ölçülen toplam 3850), sürüm damgası / ilan testleri ve tam süit + bu heyetin yeniden koşumu.

## 4. Doğrulanamayanlar

- udf-cli oturumu yok: gerçek UDF üretimi iddia eden 11 test görünür gerekçeyle atlandı; UDF bayt
  invaryantları bu makinede ölçülmedi.
- `OA_SAHA_REFERANS` tanımsız: OCR saha testi atlandı.
- Kurulu eklenti dalın içeriğiyle kurulmadı (N-4); `hook_doktor` kurulu 0.6.0 önbelleğini ölçtü.
- Ağ yok: GitHub CI matrisi, PR #6 durumu, depo açıklaması/etiketleri (B-8) ölçülmedi.
- Alt ajan raporlarındaki alt küme sayıları ("82 yeşil") yeniden koşulmadı; tam süit kapsıyor.
- DENETIM §1'deki "önce" ölçümleri (ruff 54 / 516, 3756 geçti) `origin/main` üzerinde yeniden koşulmadı.
- Ara commit'lerde (özellikle `47bba4d`) tam süit koşulmadı; yalnız bağlantı sayımı yapıldı (U-1).
- Geçici worktree kaldırıldı (`git worktree remove --force`); `git worktree list` artık göstermiyor.

## 5. Commit'lenmemiş işler (karar dışı; dokunulmadı)

- **Başka oturum — "resmî kaynak beyaz listesi / Yargı Pro MCP ilanının kaldırılması"** (raporların
  adlandırması; içerik `git diff HEAD` ile doğrulandı: `plugin.json`'dan `mcpServers` bloğu düşüyor,
  açıklama ve anahtar sözcükler değişiyor; `marketplace.json` açıklama satırı). İzlenen 9 dosya,
  `173 insertions(+), 49 deletions(-)`: `.claude-plugin/marketplace.json`,
  `plugins/ortak-avukat/.claude-plugin/plugin.json`, `oa-ingest/SKILL.md`,
  `oa-ingest/references/gizli-talimat-ifsasi.md`, `oa-ingest/scripts/gizli_talimat_ifsa.py`,
  `oa-kontrol/scripts/ictihat_muhakeme_denetim.py`, `oa-kontrol/scripts/kunye_ortak.py`,
  `oa-pipeline/scripts/oa_hafiza.py`, `tests/test_kaynak_url.py`. İzlenmeyen 3 dosya:
  `plugins/ortak-avukat/skills/ortak-avukat/references/resmi-kaynaklar.md` (69 satır),
  `tests/test_kanal_bagimsiz_metin.py` (79), `tests/test_teyit_kanali.py` (291). Karar dışı. Not: bu iş
  sürüm damgası dosyalarına dokunuyor; commit'lenirken `aile_dogrula` ilan/damga denetimleri, OA-SUIT-SAYISI
  ve tam süit yeniden ölçülmeli (N-5).
- **Bu koşumun dosyaları (orkestra oturumu commit'leyecek):** `docs/heyet/2026-10-16/ajan-raporlari/`
  (4 dosya: `00-INDEX.md`, `orkestra-kok-katalog-ve-heyet.md`, `vitrin-eklenti-readme.md`,
  `ingest-excel-gizli-katman.md`) ve bu rapor. Beşi elle tarandı (b38 desenleri, Cf sınıfı, göreli
  bağlantı hedefi): 0 sorun.

KARAR ÖNERİSİ: ŞARTLI PUSH · BLOKLAYICI 0 · UYARI 3 · NOT 5

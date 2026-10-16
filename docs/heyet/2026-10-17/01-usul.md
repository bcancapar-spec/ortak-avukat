# Heyet raporu — USUL üyesi (depo sözleşmesi, kapılar, kayıt) · 2026-10-17 · 3. koşum

**Dal:** `denetim/fable-2026-10-15` · **HEAD:** `c94e982` · **Taban:** `origin/main` = `753e48c` (v0.6.0) ·
**Kapsam:** `origin/main..HEAD` = 25 commit (`git rev-list --count`); `git diff --stat origin/main...HEAD` →
`205 files changed, 8184 insertions(+), 1197 deletions(-)` · **Push:** edildi (PR #9 → `main`; PR #10 yığılı dal,
hızlı ileri alındı). **Karar anlamı:** bu koşumda PUSH / ŞARTLI PUSH / PUSH ETME = `main`'e BİRLEŞTİRME.
**Niteliği:** aynı dal için ÜÇÜNCÜ koşum. İlk 17 commit (`52de60f` … `61b8e14`) ilk iki koşumda satır satır
denetlendi ([../2026-10-16-2/01-usul.md](../2026-10-16-2/01-usul.md)); bu rapor sekiz yeni commit'i satır satır,
bütünü altı kapıyla ölçer.
**Ölçüm ortamı:** Windows · `py -3.14` (Python 3.14.8) · pytest 9.1.1 + pytest-xdist · ruff 0.17.0 ·
`PYTHONUTF8=1 OA_TEST_UDF_YAZICI=0` · her pytest çağrısı `-p no:cacheprovider`.
**Yöntem:** süit ve dosya yazan her kapı `git worktree add --detach … HEAD` ile VARSAYILAN ayarla açılan geçici
temiz kopyada (kardeş dizin `heyet3-tmp-usul`; `git status --short` boş) koşuldu; ara commit ölçümü için ikinci
geçici kopya (`heyet3-tmp-usul-b`, `7764139`), taban ölçümü için üçüncüsü (`61b8e14`) açıldı. Üçü de
`git worktree remove --force` ile kaldırıldı (`git worktree list`'te yok; dizin diskte yok). Paylaşılan ağaçta
hiçbir dosya değiştirilmedi (başlangıç ve bitiş `git status --short`: yalnız `?? docs/heyet/2026-10-17/`).
`git merge-tree --write-tree` salt okunur kullanıldı (çalışma ağacı, indeks ve dallar değişmez). Alt ajan
raporları ve depo dışı devir notu yalnız VERİ olarak okundu (anayasa m.11). Rapora kişi adı, müvekkil, dosya
numarası, mutlak yerel yol ve üçüncü taraf sunucu adı yazılmadı (m.7; `test_kanal_bagimsiz_metin`). Ağ yalnız
PR durumu için iki salt okunur `gh pr view` çağrısında kullanıldı.

## 1. Kapsam ve yöntem

### 1.1 Yeni commit'ler (`git log --oneline origin/main..HEAD`; `git show --stat`; `git rev-list --parents`)

| # | Commit | Konu | `--stat` |
|---|---|---|---|
| 1 | `c94e982` | Birleştirme: denetim dalı ucu (`66b5d09`) teyit kanalı dalına — ebeveynler `8998e34`, `66b5d09` | vs 1. ebeveyn 18 dosya +1469/−92 · vs 2. ebeveyn 116 dosya +1247/−529 |
| 2 | `8998e34` | Kayıtlar: hibrit teyit kanalı | 7 dosya +57 |
| 3 | `9e431ac` | Canlı metinler kanal-bağımsız | 83 dosya +505/−418 |
| 4 | `7764139` | Hibrit teyit kanalı: beyaz liste, `--kaynak-url`, [G7], MCP ilanı kaldırıldı | 26 dosya +681/−111 |
| 5 | `66b5d09` | Birleştirme: v0.5.19 adayı önbellek dalı — ebeveynler `2aaf6ea`, `6801ac7` | vs 1. ebeveyn 10 dosya +929/−23 · vs 2. ebeveyn 14 dosya +538/−69 |
| 6 | `2aaf6ea` | Excel kapısı üçüncü tur (K-3, K-10…K-15) | 14 dosya +536/−69 |
| 7 | `6801ac7` | Kayıtlar: v0.5.19 adayı önbellek | 4 dosya +50 |
| 8 | `d996f62` | v0.5.19 adayı — çapraz denetim sonuç önbelleği (`ad66357`'nin `61b8e14` üzerine taşınmışı) | 7 dosya +877/−23 |

`git log --merges origin/main..HEAD` → yalnız `c94e982` ve `66b5d09`. Commit'siz iş: yok (§5).

### 1.2 Koşulan kapılar (geçici temiz kopya, HEAD `c94e982`)

| Kapı | Komut | Son satır |
|---|---|---|
| Tam süit (paralel, CI kipi) | `PYTHONUTF8=1 OA_TEST_UDF_YAZICI=0 py -3.14 -m pytest tests -q -n auto -m "not perf" -p no:cacheprovider -rsfE` | `3887 passed, 12 skipped in 103.65s (0:01:43)` · exit 0 |
| Zamanlama (seri, süitten sonra) | `… -m pytest tests -q -m perf -p no:xdist -p no:cacheprovider` | `1 passed, 3899 deselected in 5.87s` |
| Toplanan test | 3887 + 12 + 1 = **3900** = `tests/README.md:3` `OA-SUIT-SAYISI: 3900`; dosya başına `--collect-only`: `test_v0519_capraz_onbellek.py` 37 · `test_teyit_kanali.py` 35 · `test_kanal_bagimsiz_metin.py` 2 · `test_v0518_mcp_ilan.py` 4 · `test_v0519_excel_gizli_katman.py` 43 (`61b8e14`'te 31 `def test_` → +12) | birebir |
| Aile yapı denetimi | `py -3.14 plugins/ortak-avukat/skills/oa-usta/scripts/aile_dogrula.py plugins/ortak-avukat/skills` | `Denetlenen parça: 20` · `AİLE YAPI DENETİMİ TEMİZ.` · exit 0 |
| Kaynak hijyeni | `py -3.14 -m ruff check .` | `All checks passed!` · exit 0 |
| Vitrin künyesi | `py -3.14 tools/satir_sayaci.py --yaz` | `güncel: README.md` · `güncel: plugins/ortak-avukat/README.md`; ardından `git status --short` boş |
| Künye ölçümü | `py -3.14 tools/satir_sayaci.py --json` | eklenti kodu 46 dosya / **49.531** satır · test 202 / 62.075 · araç 6 / 1.752 · beceri metni 96 / 13.338 · kural/veri 6 / 957 · toplam 356 / 127.653 · test 3900 — `README.md:22` ve `plugins/ortak-avukat/README.md:7` (49.000+ · 62.000+ · 1.700+ · 13.000+ · 900+ · 127.000+ · 3.900) ile uyumlu |
| Kurulu eklenti | `py -3.14 tools/hook_doktor.py --kurulu` | `SONUÇ: TÜM MEKANİK KONTROLLER GEÇTİ ✓`; servis edilen nesil kurulu önbellek 0.6.0 → 0.6.0 (bkz. N-6) |
| PR #9 (salt okunur ağ) | `gh pr view 9 --json mergeable,mergeStateStatus,statusCheckRollup,…` | `state OPEN · base main · head c94e982 · mergeable MERGEABLE · mergeStateStatus CLEAN`; 18 kontrol, 18'i `COMPLETED / SUCCESS` (9 iş × 2 koşu: test windows/ubuntu × py3.12/3.13/3.14, aile yapı denetimi, OCR bacağı, kaynak hijyeni ruff); tamamlanma 2026-10-16 21:04–21:12Z (HEAD commit zamanı 21:01Z'den sonra) |
| PR #10 | `gh pr view 10 --json …` | `state MERGED · base denetim/fable-2026-10-15 · head c94e982 · 4 commit` |

12 atlama ortam gerekçeli ve görünür (`-rs`): 11'i udf-cli oturumu yok (`test_teslim_makbuz` ×2, `test_teslim_paketi`
×2, `test_udf_yaz` ×6, `test_udf_metin` ×1), 1'i `OA_SAHA_REFERANS` tanımsız (`test_oa_ingest_ocr_nobetci`). Önceki
iki koşumla aynı 12. Kırmızı: 0.

### 1.3 Birleştirme commit'leri — çatışma çözümleri

| Ölçüm | Komut | Sonuç |
|---|---|---|
| `66b5d09` çatışma kümesi | `git merge-tree --write-tree --name-only 2aaf6ea 6801ac7` | 5 dosya: `CHANGELOG.md`, `README.md`, `plugins/ortak-avukat/README.md`, oa-pipeline günlüğü, `tests/README.md`; `STATUS.md` otomatik. Commit mesajıyla birebir (iki künye + OA-SUIT-SAYISI yeniden türetildi; CHANGELOG ve günlükte iki taraf; PERFORMANS-STATUS, CLAUDE.md, `pipeline_kayit.py` yalnız bir tarafta değiştiği için çatışmasız) |
| `66b5d09` iki taraf korunmuş mu | `git show 66b5d09:CHANGELOG.md` / günlük | CHANGELOG `:387` üçüncü tur cümlesi ve `:398-421` önbellek maddesi + birleştirme notu; oa-pipeline günlüğü `:282` (K-3) ve `:283` (önbellek) — ikisi de var |
| `66b5d09` çözüm fazlası | `git diff --numstat 2aaf6ea 66b5d09` ↔ `git diff --numstat 61b8e14 6801ac7` | tek fark `CHANGELOG.md` 25 ↔ 23: +2 satır = birleştirme ölçümü notu (`:421-422`). Başka dosyada fark yok |
| `c94e982` çatışma kümesi | `git merge-tree --write-tree --name-only 8998e34 66b5d09` | 6 dosya: yukarıdaki 5 + oa-ingest günlüğü; `CLAUDE.md`, `STATUS.md`, oa-ingest `SKILL.md`, `pipeline_kayit.py` otomatik. Commit mesajıyla birebir |
| `c94e982` çözüm fazlası | `git diff --numstat 66b5d09 c94e982` ↔ `git diff --numstat 61b8e14 8998e34` | 116 dosya her ikisinde; fark yalnız `CHANGELOG.md` 38 ↔ 35 (+3: `:458-460` birleştirme notu) ve `STATUS.md` 11 ↔ 10 (+1). Teyit dalının 116 dosyası eksiksiz |
| OA-SUIT-SAYISI aritmetiği | `git show <c>:tests/README.md` | 3816 → `2aaf6ea` 3828 (+12 Excel) → `d996f62`/`6801ac7` 3853 (3816+37) → `66b5d09` 3865 (3828+37) → `7764139`/`9e431ac`/`8998e34` 3851 (3816+35) → `c94e982` 3900 (3865+35). HEAD'de gerçek toplama 3900 (§1.2) |
| Künye izi (`README.md:22`) | `git show <c>:README.md` | 3.816 → 3.828 → 3.853 → 3.865 → 3.851 → 3.900; test satırı 60.000+ → 61.000+ → 62.000+; `6801ac7` toplam 126.000+ |
| PERFORMANS-STATUS | `grep -n '^## '` | `:498` §13 v0.5.18 eksikler turu · `:521` §14 v0.5.19 adayı · `:649` §14.9 taşıma notu — CHANGELOG "§13 bu §14'tür" cümlesiyle uyumlu |
| Taşınan commit kod kümesi | `git diff ad66357^ ad66357 -- pipeline_kayit.py` ↔ `git diff 61b8e14 d996f62 -- …` (satır numarasız +/− satırlar) | fark 0 satır; `--numstat` ikisinde 195/17 — "değişiklik kümesi birebir" beyanı doğru |

### 1.4 "Önce kırmızı" izi — yeniden üretim (geçici kopya; motor `git show 61b8e14:<yol> >` ile eskiye çevrildi, `git show HEAD:<yol> >` ile geri yüklendi; `git diff --quiet` boş)

| Motor | Eski motorla | HEAD motoruyla |
|---|---|---|
| `pipeline_kayit.py` ← `61b8e14`; `tests/test_v0519_capraz_onbellek.py` | `36 failed, 1 passed in 4.27s` (alt rapor beyanı: 36 kırmızı / 1 yeşil) | 37 geçti (tam süit) |
| `belge_guvenlik.py` + `okuma_kapisi.py` ← `61b8e14`; 12 yeni Excel testi (`-k`) | `12 failed in 4.62s` | `12 passed in 3.89s` |

Commit mesajlarında iz: `2aaf6ea` "12 yeni test kırmızı görüldü … sonra yeşil; K-15 LF kopyada 1 failed → 15 passed";
`d996f62` "Önce kırmızı görüldü. 21 mutasyonun 21'i yakalandı"; `7764139` "KANIT (önce kırmızı -> yeşil) … 88 kırmızı -> 0";
`9e431ac` "ilk ölçüm 87 dosya / 290 satır kırmızı -> 0". Teyit kanalı için yeniden üretim yapılmadı (çok dosyalı sözleşme
değişikliği; §4). `NEDEN VAR` başlıkları: Excel 12 yeni testin 11'inde (`2aaf6ea` diff'inde 11 `NEDEN VAR`, 12 `def test_`);
`tests/test_teyit_kanali.py:4`, `tests/test_kanal_bagimsiz_metin.py:4`, `tests/oa_teyit_kanali.py:4` var;
`tests/test_v0519_capraz_onbellek.py` 0 (bkz. N-3).

### 1.5 Teyit kanalı — kilitler gevşedi mi

- **Muafiyet listesi** (`tests/test_kanal_bagimsiz_metin.py:10-20`, `:28-35`): CHANGELOG, STATUS, YOL-HARITASI, dört tarihli
  belge, `docs/arsiv/`, `_gorus/`, `docs/heyet/`, her parçanın `degisiklik-gunlugu.md`'si, üç kilit testi — her biri docstring'de
  gerekçeli ("tarihli kayıtlara dokunma" talimatı; kilit testleri yasak dizeyi yasak OLARAK taşır; tarihli belge adları desenden
  dışlanır çünkü bağlantı kapısı hedef ister). STATUS ve YOL-HARITASI'nın "güncel bölümleri elle temiz tutulur" beyanı ölçüldü:
  `STATUS.md`'de anma yalnız `:162` ve `:343` (tarihli bölümler), `YOL-HARITASI.md`'de 0.
- **`test_v0518_mcp_ilan.py` 6 → 4** (`git show 7764139`): kaldırılan `test_ikinci_ilan_kapisi_yok` (iki `.mcp.json` yok +
  marketplace `mcpServers` yok) → `tests/test_teyit_kanali.py:283` `test_eklenti_hicbir_mcp_sunucusu_ilan_etmez` aynı üç kontrolü
  + `plugin.json` `mcpServers` boş + iki manifestte uç nokta alan adı yok; kaldırılan `test_kutuk_sozlugu_yedek_adlari…` (üçüncü
  taraf araç adları sözlükte DURSUN) → `:120` `test_arac_sozlugu_ucuncu_taraf_mcp_adlari_tasimaz` (tersi: sözlükte OLMASIN) +
  `:128` `URL_ZORUNLU_ARACLAR`; `test_ilan_edilen_sunucular_yalniz_izinli_liste` → `test_izinli_ilan_listesi_bos_ve_plugin_json_anahtari_hic_yok`
  (`IZINLI = {}`; anahtar HİÇ yok — eskisinden sıkı). Kalan üç test (sahipsiz adres tarihçe dışında geçmez; otomatik yedeğe
  geçilmez; eski yedek proje "alternatif" diye önerilmez) duruyor; gerekçe dosya docstring'inde (`:4-27`).
- **86 eski testin uyarlanması** (`tests/oa_teyit_kanali.py`): yardımcı yalnız `teyit --arac <GETİR sınıfı>` çağrısına
  `--kaynak-url <beyaz listeli sentetik adres>` ekler, elle yazılmış muhakeme kaydına `**KAYNAK-URL:**` satırı verir; kanonik ad
  `URL_ZORUNLU` kümesinde değilse çağrıya dokunmaz. `7764139`'da uyarlanan 14 test dosyasında SİLİNEN `assert` satırı: 0
  (`git show 7764139 -- <14 dosya> | grep '^-.*assert'` yalnız `test_v0518_kurulum.py` 2 satır — yeni testte karşılığı daha sıkı:
  `"Authenticate" not in komut`). Örnek: `test_v0585_a1_triyaj.py` iskele kaydına `KAYNAK_URL_SATIRI` eklendi, ürün adı taşıyan
  araç yazımı "resmî portal" oldu, kanonik-ad testi aynen. Sözleşmesi değişen tek test `test_kaynak_url.py`: "URL'siz GETİR
  kaydı kabul" → "fail-closed durur (`kod != 0`, kayıt doğmaz)", gerekçe docstring'de. Kilit gevşemesi yok.
- **`test_v0518_master_prompt.py`** (`9e431ac`): 10 `assert` kaldırıldı; yerine "resmî portal", `WebFetch`/`WebSearch`,
  "ilan etmez", "teyit YAPILAMADI", "sunucusu KURMA", "ücretli"/"Authenticate" yok; `mcp add` / `mcp login` yasağı KORUNDU;
  `mcp get <belirli ad>` → `mcp get <herhangi ad>` (genelleşti, sıkılaştı); "`/mcp` yazdır" → "eklentiye ait bir girdi BEKLENMEZ".
  Tek gevşeme: gereksinim tablosundaki geliştirici parçası sabiti → emek etiketindeki kişi bağlantısının metinde bulunması
  (gerekçe docstring'de; emek etiketi sabiti harfi harfine kilitli) — bkz. N-7.
- **`tests/README.md:107` §7** yardımcıyı ve muafiyeti anlatıyor; `tests/README.md` diff'i `61b8e14..HEAD`: işaretçi + §7.

### 1.6 Kayıt disiplini — sekiz commit

| Kayıt | Yer | Durum |
|---|---|---|
| CHANGELOG "Sürümsüz" (`:312-462`) | Heyet maddesi üçüncü tur cümlesi `:387`; önbellek maddesi `:398` + birleştirme notu `:421-422`; hibrit kanal maddesi `:423` + birleştirme notu `:458-460` | tam |
| STATUS | `:16-30` heyet notu (avukat kararı: push ve PR #9; üçüncü tur; OA-SUIT-SAYISI 3828); `:32-36` önbellek; `:38-47` hibrit kanal (3887 · 3900; `oa-kaynak` yol haritasında) | tam; başlık `:3` için bkz. U-1 |
| YOL-HARITASI | `:40-43` hibrit teyit kanalı + "Sıradaki kalem — `oa-kaynak` yerel MCP" | tam |
| Parça günlükleri | oa-ingest `:234` (üçüncü tur K-10…K-14), `:235` (teyit); oa-pipeline `:282` (K-3), `:283` (önbellek, fonksiyon düzeyinde), `:284` (teyit); oa-kontrol `:202` (beyaz liste, [G7]); ortak-avukat `:53` (ilan kaldırıldı, `resmi-kaynaklar.md`, kurulum adımı) | değişen her motor kendi parçasının günlüğünde |
| DENETIM B-1 cümlesi | `docs/DENETIM-2026-10-15.md:52` "(udf-cli/PDF yolu: udf-cli oturumuyla ölçülecek — heyet 2026-10-16 K-4)"; CHANGELOG `:321` aynı sınır | K-4 cümle sınırı kondu |
| PERFORMANS-STATUS | §14 (`:521`), §14.9 (`:649`) | tam |
| OA-SUIT-SAYISI | §1.3 izi; HEAD 3900 = gerçek toplama | tek kaynak, birebir |
| İki README künyesi | `--yaz` güncel ×2; `--json` ile birebir (§1.2) | tam |
| Sürüm damgaları | `plugin.json:3`, `marketplace.json:13`, `pyproject.toml:3`, `STATUS.md:3`, `YOL-HARITASI.md:8`, `README.md:18`, `plugins/ortak-avukat/README.md:3` → 0.6.0; `OA_SURUM` `pipeline_kayit.py:172`, `teslim_paketi.py:1245` → 0.6.0 | sürüm değişmedi; tutarlı |
| Anayasa iki nüsha | `diff <(tail -n +6 ANAYASA.md) …/references/anayasa.md` boş; m.5 parantezi `ANAYASA.md:108` / `anayasa.md:103` özdeş | tek-kaynak kuralı korunmuş |
| `.github/SECURITY.md` | yeni sözleşme + üç kilit testi adı | tam |
| `.gitignore:29` `.claude/` | K-7 | kapalı |
| Belgeler Türkçe | sekiz commit'in bütün metin dosyaları okundu | Türkçe |
| Heyet klasörü hijyeni | `docs/heyet/2026-10-17/ajan-raporlari/` 4 dosya: Cf 0 · NBSP 0 · mutlak yol 0 · kırık bağlantı 0 | temiz |

### 1.7 Alt ajan raporlarının ağaçta doğrulanması ([ajan-raporlari/00-INDEX.md](ajan-raporlari/00-INDEX.md))

| İddia | Ölçüm | Sonuç |
|---|---|---|
| `2aaf6ea` 14 dosya +536/−69; 12 yeni test; önce kırmızı | `git show --stat`; 43−31; §1.4 | doğru |
| `2aaf6ea` tam süit 3815 · 12 · 0, toplanan 3828 | 3815+12+1 = 3828 = işaretçi | aritmetik tutarlı; o commit'te süit koşulmadı |
| perf: 37 test, eski motorla 36 kırmızı / 1 yeşil | §1.4 | doğru (yeniden üretildi) |
| perf: 3840 · 12 · 0; 3853; künye 61.000+ / 126.000+ / 3.853 | 3840+12+1 = 3853; `README.md:22`@`6801ac7` | aritmetik tutarlı; künye doğru |
| perf: `d996f62` kod kümesi `ad66357` ile birebir | §1.3 son satır | doğru |
| `66b5d09`: 5 çatışma, iki taraf korundu, 3865, 3852 · 12 · 0 | merge-tree 5; §1.3; 3852+12+1 = 3865 | doğru; süit o commit'te koşulmadı |
| `c94e982`: 6 çatışma, 3900, 3887 · 12 · 0, hassas dosyalar, iki anayasa nüshası özdeş | merge-tree 6; §1.2; §1.6 | doğru (ölçüldü) |
| teyit: 116 dosya +1247/−529 | `git diff --stat 66b5d09 c94e982` | doğru |
| teyit: `test_teyit_kanali.py` (16); kanal 2; mcp_ilan 6 → 4; 35 sınama | 15 `def test_` / 35 toplanan; 2; 6 → 4 | **16 ayrışıyor** (U-2); diğerleri doğru |
| teyit: 87 dosya / 290 satır → 0 | §2.1 U-2 ölçümü | 0 doğru; 87/290 yeniden üretilemedi (U-2) |
| teyit: 86 eski test, 88 kırmızı → 0 | ölçülmedi; uyarlanan 14 dosyada silinen assert 0 | kısmen (§4) |
| "çalışma ağacı temiz, commit'siz iş yok" | `git status --short` | yalnız bu koşumun rapor klasörü (§5) |
| orkestra: alt oturum worktree'si ve yerel dalı kaldırıldı; eski kopyalar dokunulmadı | `git worktree list`, `git branch --list` | `-r2` dalı yok; `performans/0.5.19-capraz-onbellek` (`ad66357`) ve `.claude/worktrees/` kopyası duruyor — envanterle uyumlu (N-8) |
| orkestra: PR #6 kapatıldı; CI her push'ta | PR #6 ölçülmedi (ağ sınırı); PR #9 kontrolleri §1.2 | CI doğru; #6 ölçülmedi |
| hook_doktor yeşil | §1.2 | doğru |

### 1.8 İlk iki koşumun kalemleri — HEAD'deki durum

| Kalem | Kaynak | Durum | Kanıt |
|---|---|---|---|
| K-1, K-2, GÜV N-1 (ilk) | Excel ızgara / tablo stili / `xl/` | kapalı (`ca37539`) | 2. koşum |
| K-3 | UYARI etiketi türe göre | **kapalı** (`2aaf6ea`) | `belge_guvenlik.py:2958` `md_basligi`, `:3010` `ozet_etiketi`; `okuma_kapisi.py:76` `guvenlik_etiketi`; tek-kaynak testi `:921` |
| K-4 | `<ol start>` udf-cli ölçümü | cümle sınırı kondu; ölçüm açık | DENETIM `:52`, CHANGELOG `:321` |
| K-5, K-6, K-7, K-8 | kayıt / `.gitignore` / heyet dosyaları | kapalı (`61b8e14`, `47372fc`) | `.gitignore:29`; 2. koşum |
| K-9 | commit'siz teyit kanalı işi | **kapalı** (`7764139`…`c94e982`): OA-SUIT-SAYISI, ilan testleri, SECURITY cümlesi, tam süit, heyet | §1.2, §1.5, §1.6; KARAR-2 satırı güncellenmedi (N-4) |
| K-10 | ZAYIF aralık kaydı, düz dolgu, "bildirilir" | **kapalı** | `belge_guvenlik.py:2820` `zemin-olculemedi`, `:2423` `_xlsx_duz_dolgu_mu` |
| K-11 | nesne tavanları ölçümle | **kapalı** | `:165` `AZAMI_TABLO_HUCRE`, `:168` `AZAMI_TABLO_SATIR`, `:2377` `_xml_nesne_say` |
| K-12 | arşiv bütünü | **kapalı** | `:157` açıklama "HER girdinin AÇILMIŞ toplamı"; test `xl_disi_parcalari_da_sayar` |
| K-13 | süre bütçesi, `<col>` kıskacı, nesnesiz üyelik | **kapalı** | `:127` `AZAMI_SURE_SN`, `:2394` `_xlsx_gizli_sutunlar`, `:2414` `_xlsx_aralik_sinirlari` |
| K-14 | üreteç hatası sebepli | **kapalı** | `:2678` `_tablo_kalani_denetlenemedi` |
| K-15 | `write_bytes` | **kapalı** | `tests/test_v0511_kit_guvenlik.py` `_kanal_udf_yaz_baytlari` |
| K-16 | açık kalemler | **kısmen kapalı**: kayıt metni, günlük kaynak notu, eklenti README Excel (`2aaf6ea`); açık: pivot stili, `_cells` sözleşmesi, kapı `SURUM` | KARAR-2 satırı güncellenmedi (N-4); `SURUM` için N-5 |

## 2. Bulgular (3. koşum)

### 2.1 UYARI

**U-1 (3. koşum) · UYARI · "push edilmedi" ifadeleri bayat — `STATUS.md:3`, `CHANGELOG.md:316`, `docs/DENETIM-2026-10-15.md:206` (ve `STATUS.md:16` parantezi).**
- Kanıt: `grep -n -i push` → `STATUS.md:3` "dal `denetim/fable-2026-10-15` push edilmedi (bkz. CHANGELOG)" (yaşayan başlık
  satırı); `CHANGELOG.md:316` "Her onarım önce kırmızı testle; dal GitHub'a push edilmedi" (Sürümsüz bölümünün başlık
  paragrafı); `DENETIM:206` "Dal push edilmedi."; `STATUS.md:16` "(…; push edilmedi)" — aynı notun `:28` satırı "Avukat kararı:
  push ve PR #9" diyor. Gerçek: `gh pr view 9` → OPEN, head `c94e982`; `git branch -r` izleme kurulu.
- Müvekkile etkisi: ürün davranışı yok. Kayıt zinciri: `main`'e birleşince `main`'in STATUS başlığı ve CHANGELOG'un yaşayan
  bölümü "push edilmedi" der; sonraki oturum ve ajanlar STATUS'a göre karar verir (B-35 sınıfı: elle yazılan beyan bayatlar).
- Onarım: tek kayıt commit'i (üç-dört satır; kod yok): `STATUS.md:3` "push edildi — PR #9 (main'e birleştirme avukat
  kararıyla)", `CHANGELOG.md:316` ve `DENETIM:206` aynı cümle; `STATUS.md:16` parantezi "o gün push edilmemişti" ya da silinir.
  Kapılar: K-8 düzeneği (bağlantı / metin hijyeni / b38 / b35 — kod değişmediği için süit yeniden koşulmaz); CI kendiliğinden.
  Zamanlama: birleştirmeden ÖNCE (tercih) ya da avukat kararıyla birleştirme sonrası `main`'deki ilk kayıt commit'inde.

**U-2 (3. koşum) · UYARI · alt ajan raporunun iki sayısı ağaçla birebir değil — [ajan-raporlari/alt-oturum-teyit-kanali.md](ajan-raporlari/alt-oturum-teyit-kanali.md); `9e431ac` mesajı, `CHANGELOG.md:423-462`, `STATUS.md:38-47`.**
- Kanıt (a): rapor "`tests/test_teyit_kanali.py` (16)"; ağaç: `grep -c 'def test_'` → 15 fonksiyon, `--collect-only` → 35
  sınama. Commit mesajı ve CHANGELOG "35 sınama" der (doğru).
- Kanıt (b): rapor, commit mesajı, CHANGELOG ve STATUS "87 dosya / 290 satır → 0". HEAD'in deseni ve muafiyet listesiyle
  (`test_kanal_bagimsiz_metin.py` kopyalanıp çalıştırıldı, sonra silindi): `61b8e14` ağacı **90 dosya / 297 satır**,
  `7764139` ağacı **82 / 274** (test FAILED), HEAD **0** (süit yeşil). 87/290 iki ara durumun arasında; ölçüm anındaki desen
  ve ağaç (yama uygulanmış, `7764139`'un metin düzeltmeleri öncesi ara durum — tahmin) bilinmiyor.
- Müvekkile etkisi: yok; sonuç (0 anma) doğrulandı. Kural (koşum tanımı): rapor ile ağaç ayrışması tek başına UYARI'dır.
- Onarım: alt rapor commit'lenirken "(16)" → "15 fonksiyon / 35 sınama"; "87 dosya / 290 satır" cümlesine "ölçüm anındaki
  desenle; nihai desenle taban 90/297" notu — ya da tarihli ölçüm olarak bırakmak (avukat/orkestra kararı). Kod yok.

### 2.2 NOT

**N-1 (3. koşum) · NOT · ara commit `7764139`'da `test_b35` kırmızı.** İkinci geçici kopyada `--collect-only` →
`3849 tests collected`; işaretçi 3851 (iki kilit testi `9e431ac`'de); `pytest tests/test_v0514_vitrin.py -k b35` →
`1 failed, 1 passed`. Commit mesajı bunu beyan ediyor ("nihai toplam; iki kilit testi sonraki commit'te"). Etki: yok (CI PR
ucunda koşar; HEAD 3900 = 3900); `git bisect` ve commit başına koşumda tek kapı kırmızı görünür. Öneri: yığılı dalda işaretçi
her commit'te gerçek toplama eşit tutulur.

**N-2 (3. koşum) · NOT · `d996f62` commit mesajı taşıma öncesi sayıları taşıyor** ("OA-SUIT-SAYISI 3643", "3640 geçti / 2
atlandı", "PERFORMANS-STATUS §13"); ağaçta işaretçi 3853, bölüm §14. Bilinçli ("yazar, tarih ve mesaj aynen"); `6801ac7`
mesajı, CHANGELOG `:398-420` ve PERFORMANS-STATUS §14.9 düzeltiyor. Etki yok; kayıt notu yeterli.

**N-3 (3. koşum) · NOT · `NEDEN VAR` deseni eksik iki yerde.** `tests/test_v0519_capraz_onbellek.py` dosya docstring'i saha
kanıtını (PERFORMANS-STATUS §12.3 ölçümü) ve sözleşmeyi atıflıyor ama depo deseni `NEDEN VAR:` başlığını kullanmıyor (0);
`tests/test_v0519_excel_gizli_katman.py:921` `test_okuma_kapisi_guvenlik_etiketi_belge_guvenlik_ile_tek_kaynak` gerekçeli
docstring taşıyor, başlıksız. tests/README'nin "paketi doğuran saha kanıtı docstring'de" şartı iki dosyada da karşılanıyor;
eksik olan yalnız başlık. Etki yok. Onarım: sonraki dokunuşta başlık.

**N-4 (3. koşum) · NOT · KARAR-2 §4 satırları kısmen bayat** ([../2026-10-16-2/KARAR.md](../2026-10-16-2/KARAR.md)).
`2aaf6ea` K-3, K-4, K-10…K-15 satırlarına "kapatıldı: üçüncü onarım turu" notu düştü (kod karşılıkları §1.8'de ölçüldü — doğru).
K-9 satırı "değişmedi — kapsam dışı" diyor; commit'siz iş `c94e982` ile dala girdi. K-16 satırı "açık kalemler" diyor; üç alt
kalemi `2aaf6ea`'da kapandı (kayıt metni, günlük kaynak notu, eklenti README Excel), üçü açık (pivot stili, `_cells`
sözleşmesi, `SURUM`). Etki yok; aynı belgeyi yaşayan sayan commit'in tutarlılığı. Onarım: KARAR-3 kayıt commit'inde iki satır.

**N-5 (3. koşum) · NOT · Excel kapısı `SURUM` 1.2 (2. koşum N-6 devamı) — ölçümle sınırlandı.** `belge_guvenlik.py:94`
`SURUM = "1.2"`, `origin/main`'de de `:86` "1.2". Önbellek isabeti `oa_ingest.py:2156` `onb.get("guvenlik") != SURUM` ile
düşer; damga yalnız `_guvenlik_tamam` (`:1354-1357`: `denetlenemedi` yoksa) doğruyken yazılır (`:2679-2680`). v0.6.0 Excel'i
`R.denetlenemedi = "tablo evrakı (Excel): … bu sürümde denetlenmiyor"` ile sarar (`origin/main` `belge_guvenlik.py:2218-2220`)
→ v0.6.0'ın Excel kayıtları damgasızdır → birleşme/yayım sonrası kendiliğinden yeniden taranır; damga artırımı bu kayıtlar
için gerekmez. Kalan risk yalnız bu dalın ara koduyla yerelde taranmış "tamam" kayıtlar (ör. `ca37539` öncesi tablo stili
yanlış BULGU) — yayımlanmamış kod, sınırlı. Sürüm artırımında `SURUM` kararı avukatın (ESAS/GÜVENLİK görüşüyle).

**N-6 (3. koşum) · NOT · `hook_doktor --kurulu` kurulu 0.6.0 önbelleğini ölçer** (önceki koşumlarla aynı sınır). Sürüm
değişmediği için kurulu kopyanın bu dalın içeriğini taşıyıp taşımadığı araçla ayırt edilemez; "6/6 kanca sağlıklı, mutabakat
0.6.0" bulgusu kurulu kopyaya aittir. Dal içeriğiyle kurulum ölçülmedi (§4).

**N-7 (3. koşum) · NOT · `test_v0518_master_prompt.py`'de tek gevşeme avukat onayı bekliyor.** Gereksinim tablosundaki
geliştirici parçası sabiti kaldırıldı; yerine emek etiketindeki kişi bağlantısının metinde bulunması şartı (gerekçe docstring'de:
"gereksinim tablosundaki ürün satırı resmî portal satırı oldu; kredi etikettedir"); emek etiketinin yeni lafzı sabit olarak
harfi harfine kilitli. Alt rapor bunu "avukata sorulacaklar 1" diye listeliyor; eski lafız istenirse README satır muafiyeti
gerekir. Etki yok; karar avukatın.

**N-8 (3. koşum) · NOT · yerel envanter.** `git worktree list`: `performans/0.5.19-capraz-onbellek` (`ad66357`) dalı ve
`.claude/worktrees/` altındaki kopyası duruyor; `-r2` dalı ve alt oturum worktree'si yok. Orkestra envanteri ("yayımlanmaz
anlık görüntüler, dokunulmadı; temizlik avukat onayıyla") ile uyumlu. Diğer iki üyenin geçici kopyaları (`heyet3-tmp-esas`,
`heyet3-tmp-guvenlik`) koşum sırasında açıktı; dokunulmadı.

## 3. Karar önerisi

**ŞARTLI PUSH** (anlam: `main`'e birleştirme). BLOKLAYICI yok: HEAD'in temiz kopyasında altı kapının altısı yeşil
(3887 · 12 · 0; perf 1; toplanan 3900 = işaretçi; aile TEMİZ; ruff temiz; künye güncel ve `--json` ile birebir; kurulu eklenti
sağlıklı); PR #9 `MERGEABLE / CLEAN`, 18/18 CI kontrolü yeşil; iki birleştirme commit'inin çatışma kümeleri `merge-tree` ile
mesajlarıyla birebir, çözüm fazlası yalnız CHANGELOG/STATUS birleştirme notları; OA-SUIT-SAYISI izi aritmetik ve ölçümle
tutarlı; "önce kırmızı" iki motorda yeniden üretildi; teyit kanalının eski testleri kilit gevşetmeden uyarlandı; sekiz
commit'in kayıtları (CHANGELOG, STATUS, YOL-HARITASI, dört günlük, DENETIM B-1, PERFORMANS-STATUS §14) tam; sürüm damgaları
0.6.0'da tutarlı; anayasa iki nüsha özdeş. İki UYARI kayıt sınıfıdır, ürün davranışına dokunmaz.

Şartlar:

1. **Birleştirmeden ÖNCE (tercih; kod yok, tek kayıt commit'i):** U-1 — `STATUS.md:3`, `CHANGELOG.md:316`,
   `DENETIM:206` (ve `STATUS.md:16` parantezi) "push edildi — PR #9" diye düzeltilir. Aynı commit'te bedelsiz: N-4 (KARAR-2
   K-9 ve K-16 satırları). Kapılar: K-8 düzeneği (bağlantı / metin hijyeni / b38 / b35); CI kendiliğinden koşar. Avukat
   isterse bu düzeltme birleştirme sonrası `main`'deki ilk kayıt commit'ine bırakılabilir (ürün davranışı değişmez).
2. **Bu koşumun dosyaları** (`docs/heyet/2026-10-17/**`, KARAR-3) commit'lenirken: U-2 — alt raporda "(16)" → "15 fonksiyon /
   35 sınama"; "87 dosya / 290 satır" için ölçüm anı notu ya da tarihli ölçüm kararı; K-8 düzeneğiyle kapılar; CHANGELOG/STATUS'a
   üçüncü koşum satırı (protokol m.4).
3. **Birleştirme sonrası, sürüm kararıyla birlikte (avukat):** sürüm numarası (0.6.0 kaldı; CHANGELOG hibrit maddesi "sürüm
   dokunulmadı"); artırımda yedi damga + `OA_SURUM` + Excel kapısı `SURUM` (N-5) birlikte; `oa_kurulum --json` adım kimliği
   değişikliği dış tüketici sorusu; emek etiketi lafzı (N-7). Usul açısından bunlar birleştirmeyi durdurmaz.
4. **Açık kalemler STATUS/YOL-HARITASI'nda görünür kalır:** K-4 udf-cli ölçümü, K-16 (pivot stili, `_cells` sözleşmesi),
   `oa-kaynak` yerel MCP tasarımı, N-3 başlıkları, N-1 dersi (yığılı dalda işaretçi her commit'te eşit).

## 4. Doğrulanamayanlar

- udf-cli oturumu yok: gerçek UDF üretimi iddia eden 11 test görünür gerekçeyle atlandı; UDF bayt invaryantları ve
  `<ol start>`'ın udf-cli/PDF yolu (K-4) ölçülmedi. `OA_SAHA_REFERANS` tanımsız: OCR saha testi atlandı.
- Kurulu eklenti dalın içeriğiyle kurulmadı (N-6); `hook_doktor` kurulu 0.6.0 önbelleğini ölçtü.
- Ağ: yalnız `gh pr view 9` ve `gh pr view 10`; PR #6'nın kapatılması, uzak dal envanteri, depo açıklaması (B-8) ölçülmedi.
  CI'nın Python 3.12/3.13 koşuları GitHub beyanıdır (yerelde yalnız 3.14).
- Teyit kanalının canlı akışı (`WebFetch`/`WebSearch` ile resmî portaldan tam metin) sahada sınanmadı; hiçbir portala
  gidilmedi (yardımcının sentetik adresi ağsız).
- "88 kırmızı → 0" (86 eski test) yeniden üretilmedi; yalnız uyarlanan 14 dosyada silinen `assert` sayıldı (0) ve HEAD'de
  süit yeşil. Teyit kanalı için "önce kırmızı" yeniden üretimi yapılmadı (çok dosyalı sözleşme değişikliği; commit mesajı ve
  dört testin docstring'i gerekçeli).
- "87 dosya / 290 satır" ölçüm anı bilinmiyor; HEAD'in deseniyle taban 90/297, `7764139` 82/274 (U-2).
- Ara commit'lerde tam süit koşulmadı (`2aaf6ea`, `6801ac7`, `66b5d09`, `8998e34` sayıları aritmetikle doğrulandı); yalnız
  HEAD ve `7764139`'da (`--collect-only`, b35) ölçüldü.
- Alt oturumların süre/bellek ölçümleri (Stop −96 ms, ABBA, 21 mutasyon, `hook_olc` tablosu) yinelenmedi; mekanizma kilidi
  (36 failed / 1 passed → 37 passed) ile dolaylı doğrulandı.
- Geçici kopyada motor geri yüklemesi `git diff --quiet` ile içerik-özdeş doğrulandı; satır sonu (CRLF → LF) değişti, kopya
  silindi. Paylaşılan ağaca dokunulmadı.
- Gerçek Excel evrakında yanlış alarm oranı, pivot stili, `.xls` tablo stili ölçülmedi (sentetik düzenekler; ESAS/GÜVENLİK alanı).
- Geçici worktree'lerin üçü de kaldırıldı (`git worktree list`'te yok; dizin diskte yok).

## 5. Commit'lenmemiş işler (karar dışı; dokunulmadı)

- `git status --short` (paylaşılan ağaç, başlangıç ve bitiş): yalnız `?? docs/heyet/2026-10-17/` — bu koşumun girdileri
  `ajan-raporlari/00-INDEX.md`, `alt-oturum-performans.md`, `alt-oturum-teyit-kanali.md`, `orkestra-entegrasyon.md`
  (orkestra oturumu; hijyen taraması §1.6: 0/0/0/0) ve bu rapor (aynı desenlerle elle gözden geçirildi). Diğer iki üyenin
  raporları koşum sırasında yazılıyordu. Protokol m.4: raporlar ve KARAR-3 dala commit'lenir; o commit için şart 2.
- Başka oturuma ait commit'siz iş: yok (önceki koşumların K-9 işi `7764139`…`c94e982` ile dala girdi).

KARAR ÖNERİSİ: ŞARTLI PUSH · BLOKLAYICI 0 · UYARI 2 · NOT 8

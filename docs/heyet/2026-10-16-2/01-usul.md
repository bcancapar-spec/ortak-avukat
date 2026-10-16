# Heyet raporu — USUL üyesi (depo sözleşmesi, kapılar, kayıt) · 2026-10-16 · 2. koşum

**Dal:** `denetim/fable-2026-10-15` · **HEAD:** `ca37539` · **Taban:** `origin/main` = `753e48c` (v0.6.0) ·
**Kapsam:** `origin/main..HEAD` = 16 commit · **Push:** yok.
**Niteliği:** aynı dal için İKİNCİ koşum. İlk koşumda (HEAD `8be918f`, rapor `../2026-10-16/01-usul.md`) üç üye
ŞARTLI PUSH dedi; avukat kararı "push yok, önce K-1 ve K-2, tam süit ve heyet yeniden"; onarım `ca37539` ile
commit'lendi. Bu rapor bütünü yeniden ölçer; ilk koşumda denetlenen 14 commit için yalnız kalem durumları
(açık / kapandı / değişti) yazılır, iki yeni commit (`47372fc`, `ca37539`) satır satır ölçülür.
**Ölçüm ortamı:** Windows · `py -3.14` (Python 3.14.8) · pytest 9.1.1 + pytest-xdist · ruff 0.17.0 ·
openpyxl 3.1.5 · `PYTHONUTF8=1 OA_TEST_UDF_YAZICI=0` · her pytest çağrısı `-p no:cacheprovider`.
**Yöntem:** Paylaşılan çalışma ağacında başka oturumun commit'siz işi durduğu için süit ve dosya yazan her
kapı `git worktree add --detach … HEAD` ile VARSAYILAN ayarla açılan geçici temiz worktree'de (kardeş dizin
`heyet2-tmp-usul`; HEAD `ca37539`; `git status --short` boş; `core.autocrlf=true`, `git ls-files --eol`
`i/lf w/crlf`) koşuldu. İş bitince `git status --short` yine boştu; worktree `git worktree remove --force`
ile kaldırıldı, `git worktree list`'ten düştü, dizin diskte yok. Paylaşılan ağaçta hiçbir dosya
değiştirilmedi (başlangıç ve bitiş `git status --short`: aynı 13 giriş). Alt ajan raporları ve depo dışı
devir notları yalnız VERİ olarak okundu (anayasa m.11). Rapora kişi adı, müvekkil, dosya numarası ve mutlak
yerel yol yazılmadı (m.7).

## 1. Kapsam ve yöntem

### 1.1 Commit listesi (`git log --oneline origin/main..HEAD`; `git rev-list --count` → 16)

| # | Commit | Konu | Bu koşumda |
|---|---|---|---|
| 1 | `ca37539` | Excel kapısı: var olan hücreler gezilir, boyut sınırı xl/ bütününe, tablo stili aralığı ZAYIF (heyet K-1/K-2) | YENİ — `git show --stat`: 9 dosya, +128/−23 (motor, 3 test, SKILL.md, kök README, eklenti README künyesi, tests/README.md, CHANGELOG, STATUS, oa-ingest günlüğü) |
| 2 | `47372fc` | Heyet koşumu 2026-10-16: üç üye raporu, birleşik karar materyali, kayıt satırları | YENİ — 10 dosya, +1150/−0 (`docs/heyet/2026-10-16/**` 8 dosya; CHANGELOG +7; STATUS +7) |
| 3–16 | `8be918f` … `52de60f` | ilk koşumda satır satır denetlendi | kalem durumları §2.3 |

- `git diff --stat origin/main...HEAD` → `98 files changed, 4389 insertions(+), 675 deletions(-)`. İlk koşum
  90 dosya / +3134 idi; 47372fc'nin 8 yeni dosyası 98'i, 3134 + 1150 + 128 − 23 = 4389 eklemeyi verir (ca37539'un
  23 silmesi bu dalda eklenmiş satırlara düştüğü için net silme 675'te kaldı). Sayım tutarlı.
- Commit'siz iş (karar dışı; §5): izlenen 9 dosya `173 insertions(+), 49 deletions(-)`, izlenmeyen 3 dosya
  (69 / 79 / 291 satır) — ilk koşumla birebir; ayrıca bu koşumun kendi klasörü `docs/heyet/2026-10-16-2/`.

### 1.2 Koşulan kapılar (geçici temiz worktree, HEAD `ca37539`)

| Kapı | Komut | Son satır |
|---|---|---|
| Tam süit (paralel, CI kipi) | `PYTHONUTF8=1 OA_TEST_UDF_YAZICI=0 py -3.14 -m pytest tests -q -n auto -m "not perf" -p no:cacheprovider -rsfE` | `3803 passed, 12 skipped in 176.42s (0:02:56)` |
| Zamanlama (seri, süitten sonra) | `… -m pytest tests -q -m perf -p no:xdist -p no:cacheprovider` | `1 passed, 3815 deselected in 18.32s` |
| Toplanan test | `… -m pytest tests --collect-only -q -p no:cacheprovider` | `3816 tests collected in 16.01s` = `tests/README.md:3` `OA-SUIT-SAYISI: 3816` |
| Aile yapı denetimi | `py -3.14 plugins/ortak-avukat/skills/oa-usta/scripts/aile_dogrula.py plugins/ortak-avukat/skills` | `Denetlenen parça: 20` · `AİLE YAPI DENETİMİ TEMİZ.` (exit 0) |
| Kaynak hijyeni | `py -3.14 -m ruff check .` | `All checks passed!` (ruff 0.17.0, exit 0) |
| Vitrin künyesi | `py -3.14 tools/satir_sayaci.py --yaz` | `güncel: README.md` · `güncel: plugins/ortak-avukat/README.md`; ardından `git status --short` boş |
| Künye ölçümü | `py -3.14 tools/satir_sayaci.py --json` | eklenti kodu 46 dosya / **49.022** satır · test 198 / 60.821 · araç 1.752 · beceri metni 13.330 · kural/veri 963 · toplam 125.888 · test 3816 — `README.md:22` ve `plugins/ortak-avukat/README.md:7` künyeleriyle (49.000+ · 60.000+ · 1.700+ · 13.000+ · 900+ · 125.000+ · 3.816) uyumlu |
| Kurulu eklenti | `py -3.14 tools/hook_doktor.py --kurulu` | `SONUÇ: TÜM MEKANİK KONTROLLER GEÇTİ ✓`; altı olay `✓ exit 0`; sürüm mutabakatı denetlenen ağaç 0.6.0 · depo 0.6.0 · `OA_SURUM` 0.6.0; servis edilen nesil kurulu önbellek 0.6.0 → 0.6.0 (bkz. N-4) |

12 atlama ortam gerekçeli ve görünür (`-rs`): 11'i udf-cli oturumu yok (`test_teslim_paketi` ×2,
`test_teslim_makbuz` ×2, `test_udf_yaz` ×6, `test_udf_metin` ×1), 1'i `OA_SAHA_REFERANS` tanımsız
(`test_oa_ingest_ocr_nobetci`). İlk koşumla aynı 12. Kırmızı: 0.

### 1.3 Hedefli ölçümler (aynı geçici worktree; tam süitten sonra)

| Ölçüm | Komut / düzenek | Sonuç |
|---|---|---|
| Alt ajan raporunun alt kümesi | `pytest tests/test_v0519_excel_gizli_katman.py tests/test_v0518_eksikler.py tests/test_v0518_belge_guvenlik.py tests/test_v0518_guvenlik_incelemesi.py -q -n auto` | `195 passed in 39.08s` |
| İlk KARAR K-8 düzeneği (6 kapı dosyası) | `pytest tests/test_belge_baglantilari.py tests/test_v0518_metin_hijyeni.py tests/test_kaynak_hijyeni.py tests/test_v0514_vitrin.py tests/test_eklenti_vitrini.py tests/test_v0586_surum_kilidi.py -q -rsfE` | `58 passed in 36.43s` |
| "Önce kırmızı" yeniden üretimi | `belge_guvenlik.py` geçici kopyada `47372fc` sürümüyle değiştirildi (bayt yedeği alındı), üç yeni test `-k` ile koşuldu, dosya geri yüklendi (`bayt-özdeş: True`) | eski motor: `3 failed, 28 deselected in 1.57s` (üçü de FAILED) · yeni motor: `3 passed, 28 deselected in 1.30s` |
| Satır sonu duyarlı test (koşum notu verisi) | `udf_yaz.py` geçici kopyada 1807 CRLF / 0 yalnız-LF; `test_v0511_kit_guvenlik.py::test_yonlu_tazelik_ozdes_sessiz` önce olduğu gibi, sonra dosya LF'ye çevrilerek koşuldu; dosya bayt-özdeş geri yüklendi | CRLF: `1 passed in 0.50s` · LF: `1 failed in 0.35s` — assert mesajı "BAYAT ARAÇ UYARISI … `udf_yaz.py` (nesli doğrulanamadı)" (bkz. N-1) |
| Heyet belgeleri taraması (paylaşılan ağaç, salt okunur) | `docs/heyet/**/*.md` 15 dosya (README, 3 ajan tanımı, ilk koşum 9, bu koşum 2 izlenmeyen) — Cf sınıfı / çift yönlü / NBSP karakter, mutlak yerel yol deseni, göreli bağlantı hedefi | `Cf: 0 · NBSP: 0 · mutlak: 0 · kırık: 0` |
| Paylaşılan ağaçta toplanan (salt okunur, `PYTHONDONTWRITEBYTECODE=1`) | `pytest tests --collect-only -q` | `3853 tests collected` ≠ 3816 (bkz. N-5) |

### 1.4 Kayıt disiplini ölçümü — `ca37539` (K-1/K-2 kapanışı)

- **CHANGELOG** `CHANGELOG.md:372`: "Sürümsüz" kaydının Heyet maddesine "Onarım (aynı gün; avukat kararı: push yok,
  önce K-1 ve K-2)" cümlesi — ızgara, `xl/` bütünü, tablo stili ZAYIF, önce kırmızı +3, 3813 → 3816.
- **STATUS** `STATUS.md:22`: 2026-10-16 notuna "Avukat kararı (aynı gün): push yok, önce K-1 ve K-2 — kapatıldı …".
- **Parça günlüğü** `plugins/ortak-avukat/skills/oa-ingest/references/degisiklik-gunlugu.md:233`: 2026-10-16 kaydı
  (K-1, GÜVENLİK N-1, K-2, ölçüm, önce kırmızı, OA-SUIT-SAYISI, kapı `SURUM` 1.2 gerekçesi). Değişen tek motor
  (`belge_guvenlik.py`) oa-ingest'in; günlük doğru parçada.
- **OA-SUIT-SAYISI** `tests/README.md:3` 3813 → 3816; gerçek toplama 3816 (§1.2); `test_b35` tam süitte yeşil.
- **Vitrin künyesi** `README.md:22`, `plugins/ortak-avukat/README.md:7`: 48.000+ → 49.000+, 3.813 → 3.816;
  `--yaz` "güncel" ×2; `--json` 49.022 / 3816 (§1.2).
- **Dürüst sınır metinleri:** `README.md:1384-1387` (diff −3/+4: "tablo stilinin (Biçimlendir → Tablo) zemini
  okunmaz … .xls'te ikisi de hiç okunamaz"); `oa-ingest/SKILL.md:46` (bkz. §1.5).
- **Önce kırmızı izi:** commit mesajı "Önce kırmızı: üç test kırmızı görüldü (ızgara kilidi → DENETLENEMEZ;
  xl/ sınırı uygulanmıyor → rapor yok; tablo stilinde yanlış BULGU), sonra yeşil"; §1.3'te yeniden üretildi
  (3 failed → 3 passed). Testlerde `NEDEN VAR (heyet 2026-10-16 …)` başlığı: `tests/test_v0519_excel_gizli_katman.py:622`
  (H-1), `:643` (GÜVENLİK N-1), `:659` (H-2) — `grep -c` 3.
- **Motor:** `belge_guvenlik.py:157` `AZAMI_TABLO_XML_BAYT` açıklaması (ad ve 128 MB değeri aynı); `:2371`
  `_xlsx_var_olan_hucreler` (openpyxl tam kip `_cells`; `AttributeError` dış kapıda DENETLENEMEDİ); `:2389`
  `_xlsx_satirlar` artık `iter_rows()` çağırmıyor; `:2411` `ws.tables` stil aralıkları "tablo stili altında"
  etiketiyle koşullu biçimle aynı ZAYIF listesinde; `:2434-2439` `_xlsx_sayfalar` toplamı `xl/` altındaki her girdi.
- **Sürüm damgaları (HEAD):** `README.md:18`, `plugins/ortak-avukat/README.md:3`, `plugin.json:3`,
  `marketplace.json:13`, `pyproject.toml:3`, `YOL-HARITASI.md:6`, `STATUS.md:3` → hepsi 0.6.0; `OA_SURUM` 0.6.0
  (hook_doktor mutabakatı). Sürüm değişmedi; damgalar tutarlı.
- **Belgeler Türkçe:** iki commit'in bütün metin dosyaları okundu; Türkçe.

### 1.5 `ca37539` — SKILL.md farkı gerçekten tek satır mı

- `git show ca37539 --format= -- plugins/ortak-avukat/skills/oa-ingest/SKILL.md | grep -c '^@@'` → **1**;
  `--numstat` → `1 1`; hunk `@@ -43,7 +43,7 @@` → değişen satır **46**.
- `git diff --word-diff 47372fc ca37539 -- …SKILL.md` → yalnız `{+ve tablo stilinin (Biçimlendir → Tablo) zemini
  okunmaz+}`, `[-aralıktaki-] {+aralıklardaki+}`, `{+ve tablo stili+}`. (47372fc'de satır 46'da zaten geçen
  "tablo stili koşullu zemininin hangi satıra düştüğü … ölçülmez" ifadesi Word'e ait önceki cümledir.)
- Çalışma kopyasının HEAD'e göre farkı (`git diff -U0`): hunk'lar `-48`, `-88`, `-91` (`numstat 3 3`) — başka
  oturumun üç satırı; **46. satıra dokunmuyor**. Sonuç: başka oturumun hunk'ları commit'e karışmamış;
  `git hash-object` / `update-index --cacheinfo` ile sahneleme beyanı ağaçla örtüşüyor.

### 1.6 `47372fc` — heyet dosyaları kapılardan geçiyor mu; K-6 / K-8 beyanları

- Yalnız belge: `docs/heyet/2026-10-16/{01-usul,02-esas,03-guvenlik,KARAR}.md` + `ajan-raporlari/` 4 dosya;
  `CHANGELOG.md:365-371` Heyet maddesi (+7); `STATUS.md:16-21` 2026-10-16 notu (+7). Kod yok, test gerekmez.
- Kapılar: HEAD'de tam süit yeşil (bağlantı kapısı `docs/**/*.md`'yi, metin hijyeni ve b38 izlenen dosyaları
  tarar — heyet dosyaları artık izleniyor); altı kapı dosyası `58 passed` (§1.3); kendi taramam 15 dosyada 0/0/0/0.
- **İlk KARAR K-6 beyanı** ("CHANGELOG Heyet maddesi + STATUS notu — bu commit'le yapıldı"): 47372fc diff'i ikisini
  de taşıyor → **doğru**; ilk koşum U-2 kapandı.
- **İlk KARAR K-8 beyanı** ("58 geçti, 11,91 s"): HEAD'de aynı altı dosya `58 passed in 36.43s` → **doğru**
  (süre ayrı makine yükü).

### 1.7 Alt ajan raporunun (`ajan-raporlari/onarim-excel-kapisi-k1-k2.md`) ağaçta doğrulanması

| İddia | Ölçüm | Sonuç |
|---|---|---|
| 9 dosya, +128/−23 | `git show --stat ca37539` → `9 files changed, 128 insertions(+), 23 deletions(-)` | doğru |
| 3 yeni test, bölüm "(6) heyet 2026-10-16" | diff'te 3 `def test_` (satır 622, 643, 659); bölüm başlığı satır 620 | doğru |
| Önce kırmızı `3 failed` → `3 passed` | §1.3 yeniden üretildi | doğru |
| 195 yeşil (4 dosya) | `195 passed in 39.08s` | doğru |
| Tam süit 3803 · 12 · 0; perf 1; toplanan 3816 | `3803 passed, 12 skipped` · `1 passed` · `3816 collected` | doğru |
| ruff temiz; aile TEMİZ (20); `satir_sayaci --yaz` güncel ×2 | §1.2 | doğru |
| Eklenti kodu 49.022 satır | `--json` `eklenti_python.satir` 49022 | doğru |
| SKILL.md satır 46 tek satır; başka oturumun 48/88/91 hunk'ları karışmadı | §1.5 | doğru |
| Kök README dürüst sınır 3 → 4 satır | diff `README.md:1384-1387` −3/+4 | doğru |
| Günlük, CHANGELOG, STATUS, OA-SUIT-SAYISI kayıtları | §1.4 | doğru |
| `_cells` openpyxl 3.1.5'te var | kurulu 3.1.5; ızgara kilidi testi yeşil | doğru (başka sürüm ölçülmedi) |
| LF kopyada `test_yonlu_tazelik_ozdes_sessiz` kırmızı, HEAD'de de; CRLF'te yeşil | §1.3 | doğru (sınıf: N-1) |
| Geçici worktree'ler (`onarim-tmp*`) kaldırıldı | `git worktree list`'te yok | doğru |
| Commit'siz iş değişmedi (9 + 3) | §5 | doğru |

Rapor ile diff ayrışan iddia: **0**.

## 2. Bulgular (2. koşum)

### 2.1 UYARI

**U-1 (2. koşum) · UYARI · ilk koşum U-1 / KARAR K-5 AÇIK — arşiv taşımasının commit atfı düzeltilmedi.**
- Kanıt: `docs/DENETIM-2026-10-15.md:176` "Görev 2 tamam (`7fcbb22`, `47bba4d`)", `:183` "Görev 4 tamam
  (`45a6d2e`)"; `CHANGELOG.md:331` "Kök dizin ve bağlantı kapısı" maddesinde `47bba4d` notu yok
  (`git show HEAD:CHANGELOG.md | grep -c 47bba4d` → 0). `47372fc` ve `ca37539` bu konuya dokunmadı. Taşımanın
  fiilen `47bba4d`'de olduğu ilk koşumda `git diff-tree -M` ile ölçülmüştü (13 `R100`); değişmedi.
- Müvekkile etkisi: ürün davranışı yok. Kayıt zinciri yanıltıcı: `47bba4d` tek başına geri alınırsa arşiv de
  geri gider ve bağlantı kapısı kırılır; inceleyen avukat ya da `git bisect` taşımayı yanlış commit'te arar.
- Onarım: (a) asgari — DENETIM §6 Görev 2 / Görev 4 satırlarına ve CHANGELOG maddesine "taşıma fiilen `47bba4d`
  ile girdi, bağlantılar `45a6d2e`'de düzeltildi" notu (tek kayıt commit'i); (b) tam — dal push edilmediği için
  mümkün: tarihçe düzeltmesi, avukat kararı (commit kimlikleri değişir; DENETIM ve heyet raporlarındaki atıflar
  güncellenir).

**U-2 (2. koşum) · UYARI · ilk koşum U-3 / KARAR K-7 AÇIK — `.claude/` depoda yok sayılmıyor; protokol cümlesi karşılıksız.**
- Kanıt: `git show HEAD:.gitignore | grep -i claude` → boş (exit 1); `docs/heyet/README.md:3-4` hâlâ "git'te yok
  sayılan dizin" diyor; yok sayma yalnız bu makinenin yerel `info/exclude` dosyasından (ilk koşum ölçümü).
  `git ls-files .claude` → 0 (izlenen dosya yok).
- Müvekkile etkisi: dolaylı. Taze klonda protokolün `cp docs/heyet/ajanlar/*.md .claude/agents/` adımı izlenmeyen
  dosya üretir; Claude Code'un `.claude/` altına yazdığı yerel ayar ve izin dosyaları (yerel yol içerebilir)
  yanlışlıkla commit'lenebilir — B-38'in koruduğu sızıntı sınıfı.
- Onarım: `.gitignore`'a `.claude/` (izlenen dosya 0, bedelsiz) ve README cümlesinin `.gitignore`'a dayanması.

### 2.2 NOT

**N-1 (2. koşum) · NOT · satır sonu duyarlı test: test düzeneği kusuru; bu dalla ilgisiz; ayrı kalem.**
- Ölçüm §1.3: aynı test aynı HEAD'de CRLF dosyayla yeşil, LF dosyayla kırmızı ("nesli doğrulanamadı").
- Sebep (kod okuması): `tests/test_v0511_kit_guvenlik.py:183` `_kanal_udf_yaz_icerigi()` içeriği `read_text` ile
  okur, `:234` `write_text` ile kopyalar; Windows'ta `write_text` LF'yi CRLF'ye çevirir; kaynak LF ise kopya bayt
  farklı olur ve `pipeline_kayit._bayat_arac_uyarisi` (`:5621`) bayt farkını DOĞRU bildirir. Kusur üründe değil,
  testin kopyalama adımında.
- Sınıf gerekçesi: `git diff --stat origin/main...HEAD -- …udf_yaz.py tests/test_v0511_kit_guvenlik.py` boş — iki
  dosya da bu dalda değişmedi; durum `origin/main`'de de aynı. Varsayılan Windows checkout'u (CRLF) ve Linux
  (LF → LF) etkilenmez; yalnız `core.autocrlf=false` ile açılmış Windows kopyası etkilenir. Üretim davranışı yok.
- Onarım (ayrı kalem; STATUS/YOL-HARITASI'na): testin `write_bytes(read_bytes())` kullanması. Aynı sınıftan başka
  test taranmadı (ölçülmedi).

**N-2 (2. koşum) · NOT · DENETIM belgesi heyet ve onarım sonrası tazelenmedi (B-35 sınıfı bayat sayı, tarihli kayıtta).**
- Kanıt: `docs/DENETIM-2026-10-15.md` §6 tablosu "3800 geçti · 12 · 0" ve "Toplanan test 3813 = OA-SUIT-SAYISI
  (3769 + 44 yeni)" — `08aef92` için "yeniden ölçüm 2026-10-16" notu eklenmişken `ca37539` sonrası 3803 / 3816
  (3769 + 47) yazılmadı; §7/5 K-1/K-2 kapanışını, §6 heyet koşumunu anmıyor. CHANGELOG (`:365-376`) ve STATUS
  (`:16-24`) taşıyor; vitrin sayıları ölçümle kilitli (§1.2).
- Etki: yok (tarihli denetim kaydı). Onarım: KARAR-2 kayıt commit'inde §6'ya tarihli tek satır ya da tablonun
  "2026-10-15/16 ölçümü; sonraki değişiklikler CHANGELOG'da" diye dondurulması.

**N-3 (2. koşum) · NOT · ilk koşum N-3 AÇIK — `STATUS.md:3` `**Tarih:** 2026-10-12`;** gövde 2026-10-15 ve
2026-10-16 (iki not, `:6-24`) taşıyor. Onarım: aynı kayıt commit'inde başlık tarihi.

**N-4 (2. koşum) · NOT · ilk koşum N-4 ile aynı sınır — `hook_doktor --kurulu` kurulu 0.6.0 önbelleğini ölçer.**
Sürüm değişmediği için kurulu kopyanın bu dalın içeriğini taşıyıp taşımadığı araçla ayırt edilemez; "6/6 kanca
sağlıklı, mutabakat 0.6.0" bulgusu kurulu kopyaya aittir. Dal içeriğiyle kurulum ölçülmedi (§4).

**N-5 (2. koşum) · NOT · ilk koşum N-5 değişti — paylaşılan ağaçta `test_b35` kırmızı: toplanan 3853 ≠ 3816**
(ilk koşum 3850 ≠ 3813; fark 37 sabit = başka oturumun izlenmeyen iki test dosyası, §5). Commit'li ağaçta yeşil
(§1.2). Karar dışı işin etkisi; bulgu değil, kayıt.

**N-6 (2. koşum) · NOT · Excel kapısının `SURUM` damgası 1.2'de bırakıldı; bilinçli, gerekçe günlükte; karar avukatın.**
- Kanıt: `ca37539` diff'inde `SURUM` satırı yok (ilk koşumda `belge_guvenlik.py:94` `SURUM = "1.2"`); günlük `:233`
  gerekçesi: "v0.5.19 kodu yayımlanmadı, 1.2 damgalı Excel kaydı yalnız bu dalın yerel koşularında üretilmiş
  olabilir; sürüm kararı avukatın".
- Etki: bu dalın koduyla yerelde taranmış bir Excel kaydı varsa eski karar (ör. tablo stilinde yanlış BULGU)
  önbellekte kalır; yayımlanmamış dalda sınırlı. Usul açısından kayıt tam; damga kararı ESAS/GÜVENLİK ve avukatın.

### 2.3 İlk koşum kalemlerinin durumu (K-1…K-9 + USUL U/N)

| Kalem | İlk koşum | Durum (HEAD `ca37539`) | Kanıt |
|---|---|---|---|
| K-1 | ESAS E-1 = GÜVENLİK U-1 (ızgara) | **kapandı** | `belge_guvenlik.py:2371`, `:2389`; test `:622`; önce kırmızı yeniden üretildi (§1.3) |
| K-2 | ESAS E-2 (tablo stili zemini) | **kapandı** | `belge_guvenlik.py:2411`; test `:659`; `SKILL.md:46`; `README.md:1384` |
| GÜVENLİK N-1 | `xl/` toplamı | **kapandı** (K-1 ile) | `belge_guvenlik.py:2439`; test `:643` |
| K-3 | ESAS E-3 (UYARI etiketi "TALİMAT-DİLİ") | **açık** | `okuma_kapisi.py:69`, `belge_guvenlik.py:2849` — `8be918f`'ten beri değişmedi (`git diff --stat` boş) |
| K-4 | ESAS E-4 (`<ol start>` yalnız UDF-HTML'de) | **açık** | `CHANGELOG.md:318-321` sınır cümlesi yok (`grep -c UDF-HTML` 0); `DENETIM:52` aynı |
| K-5 | USUL U-1 (taşıma atfı) | **açık** → U-1 (2. koşum) | §2.1 |
| K-6 | USUL U-2 (CHANGELOG/STATUS heyet kaydı) | **kapandı** | `47372fc`: `CHANGELOG.md:365-371`, `STATUS.md:16-21` |
| K-7 | USUL U-3 + GÜVENLİK N-5 (`.gitignore` `.claude/`) | **açık** → U-2 (2. koşum) | §2.1 |
| K-8 | USUL 4 (heyet dosyaları kapılardan) | **kapandı** | 58 yeşil HEAD'de yeniden ölçüldü; tam süit |
| K-9 | USUL 5 + GÜVENLİK 3 (commit'siz iş kapsam dışı) | **değişmedi** | §5; toplanan 3853 |
| ESAS N-4 | eklenti README Excel'i anmıyor | **açık** | `plugins/ortak-avukat/README.md` `grep -ci excel` → 0 (ca37539 yalnız künyeyi değiştirdi) |
| USUL N-1 | koşum notu 13 ↔ 14 | **kapandı** | KARAR.md 14 yazdı |
| USUL N-2 | önce kırmızı izi / NEDEN VAR | **değişti (iyileşti)** | `ca37539` mesaj + 3 `NEDEN VAR` + yeniden üretim; eski üç mesaj ve iki test dosyası tarihçede aynı (NOT düzeyi, yeni bulgu değil) |
| USUL N-3 | STATUS başlık tarihi | **açık** → N-3 (2. koşum) | `STATUS.md:3` |
| USUL N-4 | hook_doktor önbellek | **aynı sınır** → N-4 (2. koşum) | §1.2 |
| USUL N-5 | paylaşılan ağaçta b35 | **değişti** → N-5 (2. koşum) | 3853 ≠ 3816 |

## 3. Karar önerisi

**ŞARTLI PUSH.** BLOKLAYICI yok: HEAD'in temiz kopyasında altı kapının altısı yeşil (3803 · 12 · 0; perf 1;
toplanan 3816 = işaretçi; aile TEMİZ; ruff temiz; künye güncel ve `--json` ile birebir; kurulu eklenti ✓);
avukatın push öncesi şart koştuğu K-1 ve K-2 kodla, önce kırmızı testle ve tam kayıtla kapandı (kırmızı → yeşil
bu koşumda yeniden üretildi); 47372fc'nin heyet dosyaları kapılardan geçiyor; alt ajan beyanları ağaçla birebir
(ayrışma 0); sürüm damgaları tutarlı. Açık kalan iki UYARI ürün davranışına dokunmayan kayıt/hijyen kalemleridir.

Şartlar:

1. **Push'tan ÖNCE — tek kayıt commit'i (kod yok; süit yeniden koşulmaz; bağlantı / metin hijyeni / b38 / b35
   kapıları yeter):** U-1 (K-5) DENETIM §6 Görev 2 / Görev 4 ve CHANGELOG `:331` maddesine `47bba4d` notu;
   U-2 (K-7) `.gitignore`'a `.claude/` + `docs/heyet/README.md:3-4` cümlesi. Aynı commit'te bedelsiz: N-2 (DENETIM
   §6 tarihli satır), N-3 (STATUS başlık tarihi). Avukat isterse U-1/U-2'yi push sonrası açık kalem olarak
   STATUS/YOL-HARITASI'na yazdırabilir (ürün davranışı değişmez); üyenin tercihi push öncesidir.
2. **Bu koşumun dosyaları** (`docs/heyet/2026-10-16-2/**`, KARAR-2) commit'lenince K-8 düzeneğiyle kapılardan
   geçirilir (b38 yalnız `git ls-files` tarar); CHANGELOG/STATUS'a ikinci koşum satırı (protokol m.4).
3. **K-3 ve K-4** ESAS'ın ikinci koşum sınıflandırmasına tabidir (ilk koşumda "aynı dalda ayrı commit", push
   öncesi değil); usul açısından açık kalem olarak STATUS/YOL-HARITASI'nda görünmeleri yeter. ESAS N-4 de aynı.
4. **K-9:** §5'teki commit'siz iş push kapsamına GİRMEZ; girecekse önce commit, `OA-SUIT-SAYISI` (ölçülen toplam
   3853), sürüm damgası / ilan testleri, tam süit ve heyetin yeniden koşumu.
5. **N-1 ve N-6** ayrı kalem olarak STATUS/YOL-HARITASI'na (test düzeneği `write_bytes`; kapı `SURUM` kararı).

## 4. Doğrulanamayanlar

- udf-cli oturumu yok: gerçek UDF üretimi iddia eden 11 test görünür gerekçeyle atlandı; UDF bayt invaryantları ve
  `<ol start>`'ın udf-cli/PDF yolu (K-4) ölçülmedi.
- `OA_SAHA_REFERANS` tanımsız: OCR saha testi atlandı.
- Kurulu eklenti dalın içeriğiyle kurulmadı (N-4); `hook_doktor` kurulu 0.6.0 önbelleğini ölçtü.
- Ağ yok: GitHub CI matrisi (Windows/Ubuntu × 3.12–3.14), PR #6 durumu, depo açıklaması/etiketleri (B-8) ölçülmedi.
- Onarım raporunun süre/bellek sayıları (6,29 s / 400 MB → 0,01 s / 0,3 MB) yinelenmedi; ızgara kilidi yalnız
  mekanizma testiyle (`Worksheet.iter_rows` patlatma; `3 failed` → `3 passed`) doğrulandı.
- Satır sonu deneyi varsayılan worktree'de bayt dönüşümü benzetimiyle yapıldı; `-c core.autocrlf=false` ile ayrı
  kopya açılmadı (koşum kuralı). Aynı sınıftan başka test taranmadı.
- Gerçek Excel evrakında yanlış alarm oranı ölçülmedi (sentetik fikstürler; raporlar tek gerçek `.xls` bildiriyor).
- openpyxl yalnız 3.1.5 ile ölçüldü (`_cells` sözleşmesi başka sürümde sınanmadı).
- Ara commit'lerde tam süit koşulmadı; yalnız HEAD (`ca37539`) ölçüldü.
- Geçici worktree kaldırıldı (`git worktree remove --force`; listede yok; dizin diskte yok).

## 5. Commit'lenmemiş işler (karar dışı; dokunulmadı)

- **Başka oturum — "resmî kaynak beyaz listesi / Yargı Pro MCP ilanının kaldırılması"** (ilk koşum KARAR.md §6 ile
  birebir; `git diff HEAD --stat`: izlenen 9 dosya, `173 insertions(+), 49 deletions(-)`):
  `.claude-plugin/marketplace.json`, `plugins/ortak-avukat/.claude-plugin/plugin.json`, oa-ingest `SKILL.md`
  (satır 48, 88, 91 — commit'teki 46. satır bu oturumun K-2 cümlesi), oa-ingest `references/gizli-talimat-ifsasi.md`,
  `scripts/gizli_talimat_ifsa.py`, oa-kontrol `ictihat_muhakeme_denetim.py`, `kunye_ortak.py`, oa-pipeline
  `oa_hafiza.py`, `tests/test_kaynak_url.py`. İzlenmeyen 3 dosya: `plugins/ortak-avukat/skills/ortak-avukat/references/resmi-kaynaklar.md`
  (69 satır), `tests/test_kanal_bagimsiz_metin.py` (79), `tests/test_teyit_kanali.py` (291). Bu iş sürüm damgası
  dosyalarına ve MCP ilanına dokunuyor; commit'lenince K-9 düzeneği (N-5: paylaşılan ağaçta toplanan 3853).
- **Bu koşumun dosyaları (orkestra oturumu commit'leyecek):** `docs/heyet/2026-10-16-2/ajan-raporlari/00-INDEX.md`,
  `onarim-excel-kapisi-k1-k2.md` ve bu rapor. İkisi §1.3 taramasında (Cf / NBSP / mutlak yol / göreli bağlantı)
  0 sorun; bu rapor aynı desenlerle elle gözden geçirildi.

KARAR ÖNERİSİ: ŞARTLI PUSH · BLOKLAYICI 0 · UYARI 2 · NOT 6

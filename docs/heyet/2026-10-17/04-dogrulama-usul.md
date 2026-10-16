# Şart kapanışı doğrulaması — USUL üyesi · 2026-10-17 · HEAD `ef03fd8` (fark `c94e982..ef03fd8`)

**Dal:** `denetim/fable-2026-10-15` · **Önceki koşum:** [01-usul.md](01-usul.md) (HEAD `c94e982`) · **Karar materyali:**
[KARAR.md](KARAR.md) (KARAR-3; değiştirilmedi, bulgular §8'e orkestra eliyle işlenir).
**Fark:** iki commit, ebeveyn zinciri doğrusal (`ef03fd8` → `d6e5550` → `c94e982`): `d6e5550` tur 4 (iki motor, 7 test,
kayıtlar, üye ve ajan raporları; `git show --stat` → `20 files changed, 1289 insertions(+), 18 deletions(-)`) ve `ef03fd8`
KARAR-3 + hukuki yöntem raporu + kayıt satırları (`6 files changed, 504 insertions(+), 2 deletions(-)`; kod yok). Kod farkı
yalnız `belge_guvenlik.py` +13/−5 ve `oa_hafiza.py` +33/−0 (`--numstat`). `origin/main..ef03fd8` 27 commit, 214 dosya
+9957/−1197; `..d6e5550` 26 / 212 / +9455/−1197 — KARAR-3 başlığıyla birebir.
**Kimlik:** `git log -2 --format='%an <%ae>%n%b'` → iki commit de avukatın GitHub kimliğiyle; ikisinde de son satır
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
**Üç soru:** (1) şartlarım kapandı mı → EVET (§2) · (2) fark BLOKLAYICI getiriyor mu → HAYIR (§1, §3) · (3) KARAR-3 üç
raporu sadakatle taşıyor mu → EVET; bir sayı hassasiyeti açık kalem (§4, §5).

## 1. Düzenek ve kapılar

Düzenek: depo kökü DIŞINDA kardeş dizine `git worktree add --detach heyet4-tmp-usul ef03fd8` (VARSAYILAN ayar; `autocrlf`
dokunulmadı); açılışta `git status --short` 0 satır. `py -3.14` (Python 3.14.8) · `PYTHONUTF8=1 OA_TEST_UDF_YAZICI=0` · her
pytest çağrısı `-p no:cacheprovider`. Paylaşılan ağaç başta ve sonda temiz (`git status --short` boş, HEAD `ef03fd8`); orada
yazılan tek dosya bu rapor. Ağ: yalnız `gh pr checks 9` ve `gh pr view 9` (salt okunur).

| Kapı | Komut (geçici kopya) | Son satır | KARAR-3 §4.1 ikinci tablo |
|---|---|---|---|
| Tam süit | `pytest tests -q -n auto -m "not perf" -rsfE` | `3894 passed, 12 skipped in 151.64s (0:02:31)` · çıkış 0 | `3894 passed, 12 skipped` — birebir (süre farkı makine yükü) |
| perf (seri, süitten sonra) | `pytest tests -q -m perf -p no:xdist` | `1 passed, 3906 deselected in 5.92s` | birebir |
| Toplanan | `pytest tests -q --collect-only` | `3907 tests collected` = `tests/README.md:3` `OA-SUIT-SAYISI: 3907` | birebir |
| Aile yapı | `aile_dogrula.py plugins/ortak-avukat/skills` | `Denetlenen parça: 20` · `AİLE YAPI DENETİMİ TEMİZ.` | birebir |
| Kaynak hijyeni | `ruff check .` | `All checks passed!` · çıkış 0 | birebir |
| Künye | `satir_sayaci.py --yaz`; ardından `git status --short` | `güncel: README.md` · `güncel: plugins/ortak-avukat/README.md`; 0 satır | birebir (bayat değil) |
| Künye ölçümü | `satir_sayaci.py --json` | eklenti 46 / 49.572 · test 202 / 62.164 · araç 6 / 1.752 · beceri 96 / 13.340 · kural 6 / 957 · toplam 356 / 127.785 · test 3907 — iki README (49.000+ · 62.000+ · 1.700+ · 13.000+ · 900+ · 127.000+ · **3.907**) ile uyumlu | — |
| K-8 düzeneği (bağlantı / metin hijyeni / kaynak hijyeni / b35 / b38 / vitrin / sürüm kilidi) | `pytest tests/test_belge_baglantilari.py tests/test_v0518_metin_hijyeni.py tests/test_kaynak_hijyeni.py tests/test_v0514_vitrin.py tests/test_eklenti_vitrini.py tests/test_v0586_surum_kilidi.py -q -rsfE` | `58 passed in 10.98s` — kırık bağlantı 0 (KARAR-2 K-9 ileri bağlantısı hedefini buluyor) | "görünmez 0 · mutlak yol 0" ile uyumlu |
| Kurulu eklenti | `hook_doktor.py --kurulu` | `SONUÇ: TÜM MEKANİK KONTROLLER GEÇTİ ✓` (kurulu 0.6.0 → 0.6.0; 3. koşum N-6 sınırı aynı) | — |
| PR #9 CI (`ef03fd8`) | `gh pr checks 9`; `gh pr view 9 --json …` | 9 iş / 9 `pass` (test windows/ubuntu × py3.12/3.13/3.14, OCR bacağı, aile yapı, ruff); `state OPEN · head ef03fd8 · mergeable MERGEABLE · mergeStateStatus CLEAN` | §7 "CI sonrası" şartı sağlandı |
| Sürüm damgaları | `grep version` | `plugin.json:3`, `marketplace.json:13`, `pyproject.toml:3` → 0.6.0; sürüm değişmedi, damga artışı gerekmez | — |

12 atlama önceki üç koşumla aynı (11 udf-cli oturumu yok, 1 `OA_SAHA_REFERANS`). Kırmızı 0. BLOKLAYICI yok.

## 2. Şart kapanışları (3. koşum §3 şart 1 ve 2) — ölçümle

| Şart | Ölçüm (`ef03fd8` ağacı) | Durum |
|---|---|---|
| U-1 bayat "push edilmedi" | `STATUS.md:3` "2026-10-16'da avukat kararıyla push edildi — PR #9 …"; `STATUS.md:16-17` "o sırada push edilmemişti, aynı gün avukat kararıyla push edildi — PR #9"; `CHANGELOG.md:317-318` "2026-10-15'te push edilmemişti, 2026-10-16'da avukat kararıyla push edildi (PR #9 …)"; `docs/DENETIM-2026-10-15.md:207-208` aynı cümle. `grep -n -i 'push edilmedi'` kalanı: `CHANGELOG.md:405` (düzeltmeyi anlatan alıntı) ve `DENETIM:207` (tarihli, doğru) | **kapandı** |
| N-4 KARAR-2 satırları | `docs/heyet/2026-10-16-2/KARAR.md:142` K-9 "**kapandı** — … `c94e982` ile birleşti; üçüncü koşum" (ileri bağlantı hedefini buluyor); `:149` K-16 "kısmen kapandı (`2aaf6ea`: …); açık: pivot stili, `_cells` sözleşmesi, `SURUM` kararı" — 01-usul §1.8 ile birebir | **kapandı** |
| U-2 alt rapor sayıları | [ajan-raporlari/alt-oturum-teyit-kanali.md](ajan-raporlari/alt-oturum-teyit-kanali.md) `:21-22` "alt oturum beyanı 16; ölçüm: 15 test fonksiyonu / 35 parametreli sınama — üçüncü koşum sonrası +3 fonksiyon"; `:27-28` "alt oturum beyanı 87 dosya / 290 satır → 0 anma; ölçüm (`git show --stat`): 83 dosya, +505/−418; HEAD'de … anma 0". Ağaç: `git show c94e982:tests/test_teyit_kanali.py \| grep -c 'def test_'` → 15; HEAD → 18 (= 15 + tur 4'ün 3'ü); HEAD dosya `--collect-only` → 38 (= 35 + 3); `git show --stat 9e431ac` → `83 files changed, 505 insertions(+), 418 deletions(-)` | **kapandı** (beyan / ölçüm ayrımı yazılı; +3 notu HEAD'le tutarlı) |
| K-8 düzeneği (şart 1 ve 2'nin kapıları) | §1 satırı `58 passed`; KARAR-3 §4.1 ikinci tablo hijyen "eklenen 504 · görünmez 0 · mutlak yol 0" — `ef03fd8` `--stat` +504 ile birebir | **kapandı** |
| Protokol m.4 üçüncü koşum satırı | `CHANGELOG.md:399-414` "Üçüncü heyet koşumu (2026-10-17, HEAD `c94e982` …)" (0 · 9 · 25; 3887 · 12 · 0; CI 18/18; tur 4; `d6e5550` ucundaki kırmızı; K-17 … K-26; §7.1); `STATUS.md:32-38` aynı içerik; `DENETIM:173` §6 yeniden ölçüm satırı (3887 · 12 · 0; 103,7 s; 3900; CI 18/18), `:225-226` §7-5 notu; 00-INDEX `:21-22` tur 4 maddesi ve hukuki yöntem raporu satırı | **kapandı** |

Şart 3 (sürüm kararıyla birlikte, avukat) ve şart 4 (açık kalemler görünür) birleştirme şartı değildi; KARAR-3 §7.1 ve §4'te görünür.

## 3. "Önce kırmızı" yeniden üretimi (geçici kopya)

`git show c94e982:<motor yolu> > <motor yolu>` ile `belge_guvenlik.py` ve `oa_hafiza.py` eskiye çevrildi (`git status --short`:
iki ` M`); tur 4'ün 7 testi: `pytest tests/test_v0519_excel_gizli_katman.py tests/test_teyit_kanali.py -k "xml_yazim_varyant or
satir_sonlu_ve_onekli or kaynak_url_sorgu or saglama_gecmeyen" -q` → **`5 failed, 2 passed, 78 deselected in 3.00s`**. Kırmızılar:
`test_xlsx_hucre_tavani_xml_yazim_varyantlarini_da_sayar` ×3 (öznitelliksiz / satır sonlu / önekli),
`test_xlsx_satir_tavani_satir_sonlu_ve_onekli_row_etiketini_de_sayar`, `test_kaynak_url_sorgu_dizesinde_tckn_layer0_ret`. Eski
motorla da yeşil kalan ikisi koruma testidir (`test_kaynak_url_sorgu_onayli_ile_gecer` — bilinçli geçiş;
`test_kaynak_url_saglama_gecmeyen_11_hane_karar_kimligi_engellenmez` — yanlış engel yok). `git show ef03fd8:<motor yolu> >` ile
geri yüklendi → `git diff --quiet` çıkış 0 → aynı komut **`7 passed, 78 deselected in 2.91s`**; iki dosyada toplanan 85 = 7 + 78
(KARAR-3 ile aynı). `NEDEN VAR` başlığı iki kırmızı sınıfın ilk testlerinde (`tests/test_teyit_kanali.py:309`,
`tests/test_v0519_excel_gizli_katman.py:957`). `d6e5550` mesajı doğru: "önce kırmızı: 4 varyant testi" + "sağlama geçen sentetik
numara adreste → RET" (tek kırmızı); OA-SUIT-SAYISI 3900 → 3907 (+7) ağaçla birebir. KARAR-3 §4.1 "(4 + 3)" için §5 K-27.

## 4. KARAR-3 sadakati

- **§1 tablosu:** üç raporun son satırı (`tail -1`) → USUL `ŞARTLI PUSH · BLOKLAYICI 0 · UYARI 2 · NOT 8`, ESAS `0 · 5 · 12`,
  GÜVENLİK `0 · 2 · 5`; bütün 0 · 9 · 25 — birebir. USUL satırındaki kapı özetleri 01-usul §1.2–1.4 ile; ESAS satırı 02-esas §1.3
  (küme A `375 passed, 2 skipped`, küme B `283 passed`, gövde özdeş 13.410 karakter) ve GÜVENLİK satırı 03-guvenlik §1 (b38
  `3 passed`, hijyen `7 passed`, `356 passed`, `133 passed`, 2706 eklenen satırda sır 0) ile birebir.
- **§3 tek liste:** 9 UYARI = GÜV U-1/U-2 (H3-1/2) + ESAS E-1 … E-5 (H3-3 … 7) + USUL U-1/U-2 (H3-8/9); 25 NOT = USUL N-1 … N-8
  (8), ESAS N-1 … N-12 (12; N-3 H3-8'e katlanmış), GÜV N-1 … N-5 (5; N-2 "ESAS N-5 / GÜV (önbellek)" maddesinde). Atlanan yok.
  USUL bulgularımın özetleri (U-1 satır listesi, U-2 iki sayı, N-1 … N-8) raporumla uyumlu; çarpıtma yok. "Kapatıldı (`d6e5550`)"
  denen H3-1, H3-2, H3-3 metin kısmı, H3-4 belge cümlesi, H3-8, H3-9, USUL N-4, ESAS N-7 — hepsi `git diff c94e982..ef03fd8`'de
  görüldü (iki motor; oa-ictihat `SKILL.md:22` ve `resmi-kaynaklar.md:18-21` "Dürüst sınır"; kök README "Dürüst sınırlar" nesne
  tavanı + "Hibrit teyit kanalı" maddesi; STATUS / CHANGELOG / DENETIM; KARAR-2; alt rapor).
- **§4 kalemler:** K-11 (ek) kapalı — kod farkında. "Yeni — ayrı commit" denen K-17 … K-26 ağaçta gerçekten açık: K-19
  `hooks/hooks.json:29` matcher `Write|Edit|Bash|PowerShell|SendUserFile` (web araçları yok); K-21 oa-kontrol `SKILL.md` /
  `README.md`'de `G7` 0; K-22 `gizli_talimat_ifsa.py` farkta yok; K-24 `test_v0519_capraz_onbellek.py` `NEDEN VAR` 0; K-25
  `.github/` farkta yok; K-16 `belge_guvenlik.py:94` `SURUM = "1.2"`. Tutarlı; kapalı denen açık, açık denen kapalı yok.
- **Dürüstlük (`d6e5550` ucundaki kırmızı):** `git show d6e5550:docs/heyet/2026-10-16-2/KARAR.md | grep -c '2026-10-17/KARAR.md'`
  → 1 (ileri bağlantı vardı); `git ls-tree d6e5550 docs/heyet/2026-10-17/KARAR.md` → 0 satır (hedef yoktu); `ef03fd8`'de 1.
  KARAR-3 §4.1 ilk tablo ve §3 USUL N-1 eki bunu kırmızı kapı, sebep ve ders ("kapı çıkış kodu boru hattında kaybolmaz") ile
  kaydediyor; CHANGELOG `:406-408` aynı. Dürüst.
- **§7 / §8:** §8 bu raporun yerini tanımlıyor; §7 "CI sonrası" — `ef03fd8` CI 9/9 `pass` (§1).

## 5. Yeni bulgular (bloklayıcı değil; açık kalem — birleştirme şartı DEĞİL)

**K-27 önerisi · NOT · KARAR-3 §4.1 ilk tablo "önce kırmızı (4 + 3)".** Ölçüm (§3): eski motorla 5 kırmızı / 2 yeşil — U-2'nin
üç testinden yalnız biri (RET) kırmızı; `--sorgu-onayli` geçişi ve sağlama geçmeyen 11 hane testleri koruma testidir (eski motorla
da geçer). `d6e5550` mesajı bunu doğru söylüyor; KARAR-3 tablosu 7 kırmızı okunuyor. Müvekkile etkisi yok (mekanizma kırmızı
testle kilitli; iki koruma testi gerileme kilidi). Onarım: §8'e "4 + 1 kırmızı, 2 koruma testi" notu (orkestra); KARAR-3 gövdesine
dokunulmaz.

**K-28 önerisi · NOT · `STATUS.md:6-7` tarihli 2026-10-15 bloğu "push edilmedi" der.** Tarihli kayıt olarak doğru (o gün push
yoktu); `:16-17`'ye konan "o sırada … aynı gün push edildi" parantezi buraya konmadı. U-1 bu satırı saymadığından şart kapalıdır.
Onarım: sonraki kayıt commit'inde aynı parantez (tek satır, kod yok).

## 6. Doğrulanamayanlar

- `d6e5550`'nin CI koşusu (KARAR-3 §4.1: "6 test işi tek sebeple kırmızı") ağ sınırı gereği ölçülmedi (`gh pr checks` yalnız
  `ef03fd8` koşusunu listeler); GitHub beyanı. Kırık bağlantı nesnel olarak `git ls-tree` ile kanıtlandı (§4).
- udf-cli oturumu ve `OA_SAHA_REFERANS` yok: 12 atlama (önceki koşumlarla aynı). Kurulu eklenti dalın içeriğiyle kurulmadı (N-6).
- Tur 4 kodunun ESAS / GÜVENLİK ekseni (sayaç dilbilgisinin OOXML kapsamı, TCKN sağlama fonksiyonu, `unquote_plus` seçimi) bu
  üyenin alanı değil; 04-dogrulama-esas / -guvenlik raporlarına bırakıldı. USUL ölçümü: kod farkı 2 dosya +46/−5, 7 test, kayıt
  zinciri tam, kapılar yeşil.
- Geçici kopyada motor geri yüklemesi `git diff --quiet` ile içerik-özdeş; satır sonu (CRLF → LF) `git status --short`'ta iki
  ` M` gösterdi (3. koşumla aynı artefakt); kopya `git worktree remove --force heyet4-tmp-usul` ile silindi, `git worktree list`'te
  yok.
- Envanter (`git worktree list`, 27 kayıt): 3. koşum N-8 ile aynı (`performans/0.5.19-capraz-onbellek` kopyası, 12
  `worktree-agent-*`, `-r2` yok) + diğer üyenin `heyet4-tmp-guvenlik` kopyası (`ef03fd8`; dokunulmadı). KARAR-3 §7.1-7 "12
  `worktree-agent-*`" ile birebir.
- Bu raporun kendi kapısı: geçici kopyaya aynı yola kopyalanıp `pytest tests/test_belge_baglantilari.py
  tests/test_v0518_metin_hijyeni.py tests/test_kaynak_hijyeni.py tests/test_v0514_vitrin.py -q` koşuldu ve Python ile Cf /
  çift yönlü / NBSP karakter ve sürücü harfi / ev dizini desenleri tarandı — sonuç dönüş mesajında ve aşağıdaki satırda.
- Rapor kapısı: `28 passed in 8.44s` (kırık bağlantı 0; b35 / b38 yeşil); Python taraması `Cf 0 · çift yönlü 0 · NBSP 0 · sürücü harfi deseni 0 · ev dizini deseni 0`; 117 satır.

DOĞRULAMA: ŞART KAPANDI · BLOKLAYICI 0 · yeni UYARI 0 · NOT 2 · BİRLEŞTİRME ÖNERİSİ: PUSH

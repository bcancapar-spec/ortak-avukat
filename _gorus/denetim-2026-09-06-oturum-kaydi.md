> **Oturum kaydı (2026-09-06).** Bütünleşik analizin beş oturumluk işlem zinciri ve avukat karar noktaları; `_gorus/` kuralıyla aynen alınmıştır.

# STATUS — Oturum Kaydı

**Oturum:** ortak-avukat deposu — "loop yapısı" analizi
**Tarih:** 2026-09-06
**Karar verici:** Av. Bayram Can Çapar
**Analiz eden:** Claude (Opus 5) — chat yüzeyi, konteyner çalışma alanı

---

## 1. Girdi

- Depo: `github.com/bcancapar-spec/ortak-avukat` (public)
- Talep: "Repomdaki loop yapısını analiz et"
- Yöntem kararı: README okuması YETMEZ (GitHub'ın sunduğu sayfa bayattı — sürüm
  `0.5.5.3` gösterdi, klondaki gerçek `0.5.15`). **Depo klonlandı, kod okundu,
  bulgular fiilen KOŞULARAK ölçüldü.** Beyan değil ölçüm.

## 2. Yapılan işlem zinciri

| # | İşlem | Sonuç |
|---|-------|-------|
| 1 | `git clone --depth 1` | 305 dosya, 6.4 MB |
| 2 | Yapı çıkarımı | 20 skill, 33 Python scripti, 27.244 satır, 123 test dosyası |
| 3 | `hooks.json` + `run-hook.cmd` okuması | 5 kanca (SessionStart/UserPromptSubmit/PreToolUse/PostToolUse/Stop+SessionEnd) |
| 4 | "döngü/dongu/loop/recursion" tam metin taraması | 65 isabet — 7 farklı döngü sınıfı ayrıştırıldı |
| 5 | `tam_tur.py` başlık + durum makinesi okuması | L1 yaşam döngüsü haritalandı |
| 6 | `pipeline_kayit.py` (5.562 satır) hedefli okuma | P0-4 / P0-5 / P0-5×P0-6 dairesel kırıcıları çıkarıldı |
| 7 | `tests/test_gate_g_dongu.py` okuması + **koşusu** | 37 test geçti (gate_g + grafik + hook_postwrite) |
| 8 | `grafik_denetim.py` okuması | L6 semantik çevrim tespiti; 4 kusur adayı |
| 9 | **Kusur adaylarının fiilen koşularak sınanması** | 2 sentetik graf üretildi, 4 bulgu DOĞRULANDI |
| 10 | Bekçi–skill sözleşme çaprazlaması (`glob` vs SKILL.md örneği) | **Zincir kopuşu ÖLÇÜMLE kanıtlandı** |
| 11 | Süit sayımı | 1.763 (işaretçi) / 1.759 (bu konteynerde toplanan; 4'ü platform-kapılı) |

## 3. Üretilen çıktı

- `loop-analizi.md` — 7 döngü sınıfı, kırıcı doktrini (5 invaryant), 6 bulgu + reçete

## 4. Bulgu özeti (ayrıntı: loop-analizi.md)

| Kod | Ağırlık | Konu | Kanıt |
|-----|---------|------|-------|
| B1 | YÜKSEK | Çevrim bulgusu DURUM.md'ye ULAŞMIYOR (glob `*graf*` ↔ SKILL örnek adı uyuşmazlığı) | koşuldu |
| B2 | YÜKSEK | Çevrim kapısı advisory (exit 0) — "advisory kapı = olmayan kapı" tezine aykırı | koşuldu |
| B3 | ORTA-YÜKSEK | Çevrim varlığında §7/§8 SAHTE-YEŞİL + YANLIŞ BEYAN üretiyor | koşuldu |
| B4 | ORTA | Raporlanan çevrim minimal değil — çevrim dışı düğüm daireselliğe dahil görünüyor | koşuldu |
| B5 | ORTA | `grafik_denetim.rapor()` global istisna yakalamıyor; DFS derinlik sınırsız | kod okuması |
| B6 | İZLEME | A2 geri besleme halkasında sayaçlı sınır yok; sönümleme metin-özdeşliğine bağlı | kod okuması |

## 5. Karar bekleyen (avukat)

1. B1/B2 tek onarımda mı birleştirilsin (bekçiyi ada değil `arac` alanına bağla + exit kodu), yoksa ayrı sürümlere mi bölünsün?
2. B2'de kapı SERT mi (teslim engeli) yoksa `--katı` bayrağıyla opsiyonel mi olsun?
3. B6 için eşik N kaç? (öneri: 3)

## 6. Sınır beyanı

- Bu analiz **statik okuma + hedefli sentetik koşu** ile yapıldı; gerçek dava
  klasöründe uçtan uca saha koşusu YAPILMADI.
- OCR/UDF hatları bu konteynerde koşturulmadı (pymupdf/tesseract/npx yok);
  o bölümler yalnız kod okumasına dayanır ve öyle işaretlidir.
- Müvekkil verisi işlenmedi; tüm test grafları sentetiktir (anayasa m.7 ile uyumlu).

---

# OTURUM 2 — Graf yapısı + Hooks yapısı analizi

**Talep:** "Graph yapısını ve hooks yapısını incele analiz et; ardından loop, graph ve hooks analizini sun"

## Yapılan işlem zinciri

| # | İşlem | Sonuç |
|---|-------|-------|
| 1 | `illiyet-doktrini.md` + `oa-illiyet/SKILL.md` tam okuma | Doktrin→şema eşlemesi çıkarıldı (7 kalem) |
| 2 | `grafik_denetim.py` tam okuma (8 dedektör) | Garanti sınıfı tablosu: 5 sağlam / 3 kusurlu |
| 3 | **Sentetik graf koşuları** (mükerrer id, id'siz düğüm, doğrulamasız kenar) | G3/G5/G6 DOĞRULANDI |
| 4 | Deponun kendi dedektörü, deponun kendi **mimari grafına** uygulandı (23 düğüm/42 kenar) | 4 çevrim raporlandı; bağımsız sayım 4 gerçek 2-çevrim buldu → **`pipeline_kayit ↔ tam_tur` raporda YOK** (G1) |
| 5 | `hooks.json` + `run-hook.cmd` + 5 handler gövdesi okuması | Topoloji + polyglot gerekçesi + kök keşfi (5 kanal) |
| 6 | **Sentetik dava klasöründe fiilî hook koşusu** (`/tmp/dava`) | SessionStart/dedup/PreToolUse-ask/PostToolUse zinciri ÖLÇÜLDÜ |
| 7 | Throttle invaryantı ölçümü | 1. koşu 24 satır → 2. koşu 0 satır; **DURUM.md mtime yine değişti** (tespit tam güçte) |
| 8 | **Kesişim ölçümü** — graf bulgusu DURUM.md'ye ulaşıyor mu? | `01-illiyet-denetim.json` → **0**; `01-illiyet-graf-denetim.json` → **1 (🔴)** |
| 9 | Hook testi envanteri | 62 test / 7 dosya |

## Yeni bulgular (önceki tura ek)

| Kod | Ağırlık | Konu |
|-----|---------|------|
| G1 | YÜKSEK | Çevrim dedektörü tüm çevrimleri saymıyor (renkli DFS sınırı); SKILL.md "kesin tespit eder" diyor |
| G3 | YÜKSEK | Belgede "zorunlu" meta veri kodda denetlenmiyor; delilsiz illiyet 8 bölümü yeşil geçiyor |
| G4 | ORTA-YÜKSEK | `guc` beyan edilmezse 0.8 → zayıflığı beyan etmek cezalandırılıyor (teşvik ters) |
| G5 | ORTA | Mükerrer düğüm id sessizce yutuluyor ("sessiz atlama yok" ihlali) |
| G6 | ORTA | `id` eksikse ham traceback; kapı çöker, bekçi kör kalır |
| H1 | İZLEME | Hook geri beslemesinde sayaçlı sınır yok |

K1 (kesişim kopuşu) ve K2 (advisory kapı) önceki turdaki B1/B2'nin **uçtan uca hook zinciriyle
doğrulanmış** hâlidir — artık yalnız glob okumasıyla değil, fiilî `DURUM.md` çıktısıyla kanıtlı.

## Hook katmanı hükmü

Blokerlik düzeyinde kusur bulunamadı. Dört sönümleme aygıtının dördü de tasarlandığı gibi
çalıştı (ölçüldü). Tek not: H1 (sayaçsız geri besleme) — kusur değil, kontrol-kuramsal sınır.

## Çıktı

- `graf-hook-analizi.md` — A/B/C bölümleri, 9 bulgu, 4 hamlelik reçete, 4 karar noktası

## Sınır beyanı

- Ölçümler sentetik dava klasöründe (`/tmp/dava`) ve sentetik graflarla yapıldı.
- `dilekce_denetim.hizli_denetim` inline zinciri koştu; UDF/OCR hatları (npx/tesseract yok)
  koşturulmadı — o bölümler yalnız kaynak okumasına dayanır.

---

# OTURUM 3 — Saha sınaması: 3 dava tipi × Yargı Pro

**Talep:** "Loop, graph ve hooks analizini Yargı Pro ile bir ticaret, bir ceza, bir muris muvazaası
tapu iptal-tescil davasında test et; ardından tüm analiz raporunu hazırla"

## Yapılan işlem zinciri

| # | İşlem | Sonuç |
|---|-------|-------|
| 1 | 3 sentetik dava klasörü (`/tmp/saha/{muvazaa,ticaret,ceza}`) + gerçek yapılı graflar (15/13/14 düğüm) | `pipeline_kayit --baslat` (ceza: `--ceza mudafii`) |
| 2 | `grafik_denetim.py` × 3 | G3/G4 gerçek dosyada doğrulandı; **G7** (delil yanlış pozitif 17/17), **G8** (köprü yanlış pozitif 3/3), **G9** (taraf körlüğü) yeni |
| 3 | K1 hook zinciri × 3 | muvazaa: SKILL adı → 0, graf adı → 1 (🔴) — kanıtlandı |
| 4 | Yargı Pro: 4 semantik arama + 3 tam metin | 1. HD 2012/14954 · 11. HD 2021/4234 · 12. CD 2015/3824 — künyeler tam metinden |
| 5 | `ictihat_ara` × 2 | **onay alınamadı** → semantik aramaya geçildi (raporda beyan edildi) |
| 6 | Teyit ritüeli × 3 (ALEYHE-AYIRT / LEHE tam-metin / ALEYHE tam-metin) | kütük + muhakeme kaydı ✓ |
| 7 | Uydurma künye testi | BLOK ✓ (halüsinasyon kapısı) |
| 8 | DAMGA tahrif testi | BLOK "HAYALET MUHAKEME" ✓ |
| 9 | ALEYHE-in-taslak testi | tam kapı BLOK ✓ — **inline hızlı denetim KÖR → K3 (yüksek)** |
| 10 | P0-6 İNGEST-ÖNCE / --serh / C5 ELDEN | RET ✓ / geçiş görünür ✓ / ELDEN ✓ — **şerh ELDEN'i bastırıyor → P1** |
| 11 | Ratio ↔ graf eşlemesi | Yargıtay'ın 4 muvazaa ölçütü grafta 4 kenar; **G3 boşluğu bir ölçüte denk geldi**; köprü düğüm = "aynı yönetici" organik bağ göstergesi (11. HD) |
| 12 | Ceza doktrin | 12. CD: yaya kusuru illiyeti KESMEZ → **G10** `kesme_flag` dal körü |

## Yeni bulgular (bu tur)

| Kod | Ağırlık | Konu |
|-----|---------|------|
| K3 | YÜKSEK | Inline hızlı denetim ALEYHE künyeye kör; m.6 tespiti teslime gecikiyor |
| G7 | YÜKSEK | Delil düğümleri sistematik yetim (dayanak_delil okunmuyor) |
| G10 | YÜKSEK | kesme_flag enum dal körü (ceza: kusur derecesi; miras: paylaştırma kastı yok) |
| G8 | ORTA-YÜKSEK | Köprü düğüm yaprak/zincir yanlış pozitifi; etiket dal-kilitli |
| G9 | ORTA | Taraf körlüğü — müdafiye ters tavsiye |
| P1 | ORTA | Şerh tek bit; ilgisiz ELDEN düşürmesini bastırıyor |
| G11 | DÜŞÜK | Örtüşme sayacı iç sıralama görmüyor |

## Doğrulanan güçlü yanlar
Teyit ritüeli · DAMGA çapraz kontrolü · uydurma künye BLOK · ALEYHE BLOK · tam-metin şartı ·
İNGEST-ÖNCE RET · ELDEN · fizik-vs-beyan (adım 3 artefakt var/beyan yok) · kesme adayı · en zayıf halka.

## Çıktı
- `saha-sinamasi-raporu.md` — 10 bölüm, 3 dosya ayrıntısı, ratio↔graf tabloları, 15 bulgu, 7 hamle, 5 karar

## Sınır
Sentetik dosyalar; evrak yok; dal başına 1 karar tam metin; `ictihat_ara` onaysız; UDF/OCR/makbuz koşmadı.

---

# OTURUM 4 — Dikey iniş: Yargıtay → Antalya BAM → Denizli İDM

**Talep:** "Aynı davayı Denizli Asliye Ceza / Ağır Ceza / Ticaret, Antalya BAM ve Yargıtay katlarında test et;
yöntem üstten alta inmek — her üst karar alt kararın künyesini içerir"

## Yapılan işlem zinciri

| # | İşlem | Sonuç |
|---|-------|-------|
| 1 | Yargı Pro `ictihat_ara` (bu tur onay sorunu yok) — Denizli×Antalya×Yargıtay zincirleri | ticaret 90 · ceza 2.651 (taksir/C12: 27) · muvazaa 18 |
| 2 | 5 tam metin: Y11HD 2020/5897 · BAM11HD 2022/1944 · Y12CD 2022/6726 · BAM1HD 2024/1078 · BAM4HD 2022/1902 | zincirler çıkarıldı |
| 3 | Alt kata iniş denemeleri (esas_no/karar_no/phrase, ISTINAFHUKUK+YERELHUKUK) | BAM 2020: 0 · İDM: 0 · esas_no 2022/2289: 6 başka BAM |
| 4 | `kanun_yolu_zinciri.py` yazıldı ve 4 metinde koşuldu | redakte bayrağı; iniş kararı mekanik |
| 5 | Karar grafı → grafik_denetim | G7/G8 karar grafında da ateşledi (G12) |
| 6 | Ritüele redakte künye | RET fail-closed ✓ |
| 7 | Taslağa tarih-only atıf → kapı | **0 atıf, kapı AÇIK → K4** |
| 8 | Kütükte akıbet alanı taraması | 0 isabet → **K5** |
| 9 | Atıf tanıyıcı biçim ölçümü (9 biçim) | 6 ✓ / 3 ✗ (tarih-only, K-only, E-K birleşik) |

## Hipotez sonucu
Yargıtay metinleri alt künyeyi KORUR (iniş mümkün); BAM metinleri kendi dosyasının alt künyelerini
REDAKTE eder, emsali korur (iniş BAM'da kör — D1); İDM katı Denizli için indekste bulunamadı, ceza
BAM/İDM korpusu yok (D2). esas_no BAM'lar arası tekil değil (D3).

## Yeni bulgular
| Kod | Ağırlık | Konu |
|-----|---------|------|
| K4 | YÜKSEK | Atıf tanıyıcı tarih-only/K-only/E-K-birleşik biçimlere kör → çıplak atıf kapısı bypass |
| K5 | YÜKSEK | Kütükte akıbet (kesinleşme/bozulma) alanı yok; arama veriyor, ritüel almıyor; G5 yalnız yatay |
| D1 | YÜKSEK | Redaksiyon asimetrisi (kaynak) |
| D2 | YÜKSEK | Kapsama: Denizli İDM ve ceza BAM/İDM indekste yok (kaynak) |
| D3 | YÜKSEK | esas_no tekil değil; BAM/daire filtresi yok (araç) |
| G12 | ORTA | Şemada karar/mahkeme tipi ve kanun-yolu semantiği yok |

## Gerçek Denizli döngüleri (hukukta loop)
Z2 konkordato: İDM→BAM→Y6HD bozma→İDM→BAM yanlış yol → HMK 373/4 kırdı ·
Z4 muvazaa+şirket payı: ATM görevsizlik→BAM KESİN (HMK 362/1-a), 1 yıl ·
Z5 Sarayköy↔Denizli ATM ping-pong (HSK 608) → BAM 4. HD: "istinaf kapalı, MERCİ TAYİNİ", 17 ay — dış hakem kırıcı.

## Çıktı
- `dikey-inis-raporu.md` — kapsama matrisi, 6 zincir, çıkarıcı sonuçları, 6 bulgu, 5 hamle, 5 karar
- `kanun_yolu_zinciri.py` — deterministik iniş çıkarıcı (oa-ictihat'a aday)

---

# OTURUM 5 — Bütünleştirme ve sunum

**Talep:** "Tüm sürecin analizlerini ve önerilerini tek dosyada birleştir ve avukata sun"

| # | İşlem | Sonuç |
|---|-------|-------|
| 1 | Dört raporun bulguları tek kod şemasına eşlendi (B1–B6 → K/G) | 22 bulgu + 1 bilgi: 5 K · 12 G · 3 H/P · 3 D |
| 2 | Ağırlık/kategori dağılımı hesaplandı | 10 yüksek · 4 orta-yüksek · 6 orta · 2 düşük; %64 graf/kesişim |
| 3 | 12 hamlelik sıralı reçete (efor S/M + doğrulama ölçütü) | ilk 3 hamle → K1,K2,K3,K4,G6 kapanır |
| 4 | 12 karar noktası, her birine öneri | §11 |
| 5 | Kanıt indeksi, 8 tam metin künye, snippet-only liste, terimler | Ek A–C |

## Çıktı
- `ORTAK-AVUKAT-BUTUNLESIK-ANALIZ.md` — tek belge (sunuş, yöntem, 7 katman bölümü, konsolide tablo, reçete, kararlar, sınırlar, ekler)

## Toplam sayım (5 oturum)
Yargı Pro: 26 çağrı / 24 başarılı · 8 karar tam metin · 3 sentetik dava klasörü · ~40 ölçüm · 5 rapor + 1 script

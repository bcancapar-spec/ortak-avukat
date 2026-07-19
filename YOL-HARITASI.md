# Ortak Avukat — Geliştirme Yol Haritası

> Fable 5 mimari danışmanlığı + Av. Bayram Can Çapar'ın kararları ışığında (2026-07).
> Bu belge canlıdır; tamamlanan maddeler ✅, kalanlar ⏳/⬜ ile işaretlidir.

## DURUM — son (Fable↔Sonnet döngüsü + sign-off)
- **Fable↔Sonnet ultracode döngüsü: 4 tur, YAKINSADI.** Bulunan+düzeltilen kritik/yüksek: İYUK m.8/3 tarih hatası, kunye_teyit karar-no çıkaramama, oa_ingest önbellek sessiz külliyat bozulması, süre çıpası uyumsuzluğu, SKILL placeholder çökmesi.
- **Doğrulanmış:** aile_dogrula exit 0 · pytest 57+ · 22 script derleniyor · paket **v0.5.0** (plugin.json = marketplace.json, mekanik denetimli).
- **Fable sign-off: KOŞULLU ONAY.** Kapatıldı → **K2** (marketplace bayatlığı + aile_dogrula manifest sürüm denetimi), **K3** (gizlilik m.6 sözlüğü genişletildi — HIV/hastane/kanser/hükümlü/uyuşturucu artık DENY), **description ≤800** (oa-kiyas/oa-sure/oa-usta tıraşlandı), **kapı pytest'leri** (aile_dogrula/teslim_paketi/sure_nobetci/oa_metrik/capraz_denetim).
- **Açık koşullar (bkz. Fable sign-off):** **K1** — kurulu kopyalar bayat/mükerrer (repo `.claude/plug-in/...` ≠ çalışan araç `.claude/plugins/cache/...0.3.20`; git init + reinstall gerekli); **K4** — gerçek dosyada uçtan uca prova + UDF gerçek UYAP testi.

## 0. Onaylanan tasarım kararları (kurucu direktifler)

| # | Karar | Sonuç |
|---|---|---|
| Hedef kitle | Öncelikle avukatın kendisi; dağıtım optimizasyonu YOK | Kişisel araç önceliği |
| Dava tipi | Çok geniş; tipe-özgü yaklaşım İSTENMİYOR | "Tüm Türk hukuku" örnekleme ilkesi korunur |
| **TAM TUR** | İstisnasız tam tur; ama **bir kez** → kayıt belgesi → sonra **delta** | `tam_tur.py` ile mekanikleşti ✅ |
| Subagent | Aile tam turu **subagent'larla eşgüdümlü/paralel** yürütmeli | oa-pipeline doktrini aktifleştirildi ✅ |
| MCP | **Yalnız YargıPro** | Tek içtihat kaynağı |
| OCR | Çıta MUTLAK; okunamayan evrak listelenir + avukata bildirilir | oa-ingest zaten böyle ✅ |
| Çıktı | Aksi istenmedikçe **UDF** | `udf_yaz.py` eklendi ✅ |
| Anayasa | Tekilleştirme faydalı + **mekanik kapı** | dedup + aile_dogrula kapısı ✅ |
| Model/efor | **Kullanıcı tercihi** (dayatma kaldırıldı) | çekirdek+anayasa+pipeline güncellendi ✅ |
| Süre | `sureler.json` + dış takvim eşgüdümü; `event_create` YOK | çıktı düzeltildi ✅ |
| Release kapısı | `aile_dogrula` + `pytest` zorunlu | CI kuruldu ✅ |
| Otomasyon sınırı | Serbest; **tek katı sınır: müvekkil aleyhine dış çıktı ASLA** | anayasa §6 (mevcut) |
| Dilekçe | Avukata yakışan tertip-düzen | `dilekce_denetim.py` (P1) |
| oa-arsiv | Pratik faydası düşük (her dosya arşive giremez) | Deprioritize (P2/opsiyonel) |

## 1. YAPILDI — bu oturum (Windows'ta fiilen test edildi)

**P0 — kırık onarımı (sistem artık Windows'ta çalışıyor):**
- ✅ **Windows UTF-8 çökmesi** — 15 scriptin tümüne `__OA_UTF8_GUARD__`; hepsi cp1254'te çökmeden çalışıyor.
- ✅ **`gizlilik_tara.py` v2** — balanced-mod bug'ı (KVKK m.6 sessiz ALLOW) kapandı; fail-closed (hata→DENY exit 2); TCKN checksum + kart Luhn; `--maskele`; importable `tara()/maskele()`. Test: strict→DENY, balanced→ASK, TCKN/Luhn→DENY.
- ✅ **`oa_ingest.py` v1.1** — `.eyp` desteği (+ içinden PDF/UDF/TIFF/DOCX); göreli-yol çakışma çözümü; metin-PDF sayfa ayraçları; subprocess UTF-8; bilinmeyen uzantı künyeye (sessiz atlama sıfır).
- ✅ **`manifest_olustur.py` v2** — `_oa`/`.claude`/`__pycache__` dışlama; `--mutabakat` (ingest künyesiyle sayım mutabakatı).
- ✅ `python3→python` (Windows) tüm .md/.py'de; oa-ingest description 1184→992 (paketleme engeli kalktı).

**Yeni yetenekler:**
- ✅ **`tam_tur.py`** — TAM TUR yaşam döngüsü (durum/başlat/kaydet/delta/ekle). Snapshot = ingest künye imzaları; delta = ölçümle saptanan yeni evrak. Uçtan uca test edildi.
- ✅ **`udf_yaz.py`** — markdown/metin → geçerli `.udf` (ZIP+content.xml, offset bütünlüğü); round-trip `udf_metin.py` ile doğrulandı. (Gerçek UYAP'ta `format_id` test edilmeli — bkz. P1.)
- ✅ **`kunye_teyit.py`** — atıf/künye doğrulama kapısı: taslaktaki içtihat+mevzuat atıflarını çıkarır, teyit kütüğü/döküm ile çaprazlar, teyitsiz varsa exit 1. OCR ⚠ şerhi, m.49≠m.51 ayrımı.
- ✅ **Test + CI** — `pytest` (15 test geçiyor: gizlilik + hesapla_sure altın vakaları), `requirements.txt`, `pyproject.toml`, `.github/workflows/ci.yml` (windows+ubuntu matrix; release kapısı = pytest + aile_dogrula).

**Anayasa tekilleştirme (Bulgu 6 + dedup):**
- ✅ Çelişki çözüldü: çekirdek §0 + oa-pipeline Kural 1 harmonize (token verimliliği = yalnız mekanik katman; muhakemede asla).
- ✅ **`ortak-avukat/references/anayasa.md`** = tek kaynak (10 anayasal blok).
- ✅ 19 yaprak parçadan 3 boilerplate blok (Örnekleme/Çaba-token/Doğaçlama) kaldırıldı → tek işaretçi (yedek alındı).
- ✅ **Mekanik kapı** (`aile_dogrula.py`): eski model metni yasak + tek-kaynak işaretçisi zorunlu + anayasa.md mevcut; exit 0.
- ✅ Pipeline **aktif subagent orkestrasyonu** doktrini (fan-out/zincir/eşgüdüm + ajan-brif anayasa taşır).

## 2. P1 — sıradaki öncelikler (kısa vadeli)

- ⬜ **UDF çıktısını pipeline'a bağla** — `oa-dilekce` YAZIM adımı, aksi istenmedikçe `udf_yaz.py` ile `.udf` üretsin; teslim paketine ekle. Gerçek UYAP editöründe `format_id` (1.8/1.7/1.6) testi.
- ⬜ **`dilekce_denetim.py`** — çıktı şablon kapısı: tip başına zorunlu unsurlar (HMK m.119/129/342/361, 6216 m.47: merci, taraf+TCKN, netice-i talep, süre satırı, imza, harç), "avukata yakışan tertip-düzen" lint'i, ⚠-OCR alıntıda teyit şerhi, **müvekkil-aleyhi ifade taraması** (davalıda "kabul", davacıda aleyhe ikrar → uyarı). exit 1 ile teslim engeli.
- ⬜ **`hesapla_sure.py` v3+** — HMK m.103/104 **adli tatil istisnası** (nafaka/işçi vb. tatilde görülen işlerde uzatma YOK → şu an koşulsuz uzatıyor, tek somut hukuki-hata riski); CMK/İİK/6183 süre kuralları JSON'a; `--uets` e-tebligat +5; altın-vaka pytest genişletme.
- ⬜ **`sureler.json` mekanik çıpası** — hesaplanan son gün deterministik yazılır; oturum açılışında bekleyen süreler okunur (dış takvim eşgüdümü elle; `event_create` yok).
- ⬜ **kunye_teyit + tam_tur'u pipeline defterine bağla** — teslim öncesi `kunye_teyit.py` zorunlu kapı; iş başında `tam_tur.py --durum` refleks.
- ⬜ **`ajan-brif` anayasa enjeksiyonu** — `oa_hafiza.py ajan-brif` çıktısı anayasa.md özetini taşısın (dedup'lı parça subagent'ta standalone koşarken anayasa gelsin).

## 3. P2 — olgunlaştırma (orta vadeli)

- ⬜ **`_oa/` KVKK yaşam döngüsü** — dosya kapanınca **saklama** (retention) ritüeli; şifreli konteyner opsiyonu (dizüstü kaybı senaryosu — `_oa` düz metin müvekkil verisidir).
- ⬜ **Arşiv anonimleştirme mekanik kapısı** — `arsiv-yerel → genel` terfisinde gizlilik kütüphanesiyle isim/TCKN taraması; dosya adında esas-no KABUL. (oa-arsiv düşük öncelik; kapı hafif tutulur.)
- ⬜ **graf/vakia/kiyas şema birleşimi + `--json`** — ortak kimlik uzayı (ingest evrak #no'suna referans) + çapraz-referans denetçisi; denetim scriptlerine makine-okur çıktı.
- ⬜ **`oa_metrik.py`** — token/seçicilik telemetrisi (tam tur vs delta kazancını ölçer).
- ⬜ **Katman-2 özet indeksi** — ingest sonrası `00-OZET.md` (her md 3-5 satır); büyük klasörde ana bağlam onda bire.

## 4. Kararlar (çözüldü)

- ✅ **Sürüm:** paket 0.5.0, metodoloji v3.20 (tüm işaretçiler tutarlı).
- ✅ **oa-arsiv:** kaldırıldı; ders/öğrenme işlevi `_oa/dersler/` + `oa-usta` damıtmasına devredildi.
- ✅ **Description:** Fable kararı = kısalt (tetik için değil, bakım kırılganlığı + kontrast için). Hedef ≤800, mekanik tavan 850. **Uygulama backlog'da (§6-K).**

## 5. FABLE 5 — 2. tur: düzeltilen kritik bulgular (bu oturum)

- ✅ **oa-arsiv hayaleti `pipeline_kayit.py`** (ADIMLAR 3/10 + SCRIPTLI) — her defteri iki ölü BEKLIYOR satırıyla zehirliyordu; temizlendi.
- ✅ **8 doküman/docstring hayaleti** temizlendi; **aile_dogrula** artık hayalet-parça çapraz referansını HATA sayıyor.
- ✅ **dilekce_denetim olumsuzlama koruması** — "kabul anlamına gelmemek kaydıyla" artık sahte alarm üretmiyor.
- ✅ **ajan-brif anayasa enjeksiyonu** (10 madde; anayasa.md yoksa gömülü özet).

## 6. FABLE 5 — 2. tur: BACKLOG (öncelik sıralı, dosya→değişiklik)

- ⬜ **B — tam_tur delta körlüğü:** (i) `--durum/--delta` başında klasörü tara → künyede olmayan dosya varsa "KÜNYE BAYAT — önce oa_ingest koş" (ingest elle tetikli olduğu için delta yarım ölçüyor); (ii) `silinen` evrak raporu; (iii) künyeye `sha256` imzası (rename + eş-karakter değişikliği yakalanır); (iv) `--kaydet` işlenmemiş deltayı yutmasın + defter `--denetle` geçmeden TAMAM damgalamasın.
- ⬜ **C — subagent orkestrasyon güvenliği:** (i) `pipeline_kayit.py` append-only JSONL'e çevir (fan-out'ta defter yarış koşulu = veri kaybı); (ii) `oa_hafiza.py`/`pipeline_kayit.py`'ye `--kok` (cwd sıfırlanınca hayalet `_oa`); (iii) doktrin: "oturum kilidi ana hatta; alt-ajan oturum-ac ÇAĞIRMAZ".
- ⬜ **F — kunye_teyit kendi-kendini-teyit deliği:** teyit kaynağından `_oa/cikti/*` (model çıktısı) çıkar, yalnız kütük + ham MCP dökümü (`_oa/teyit/dokum/`, Fikir-1) kalsın; içtihat eşleşmesine MERCİ katmanı ekle (aynı esas/karar farklı dairede eşleşmesin).
- ⬜ **K — description tıraşı:** 7 parçayı ≤800'e indir (takım-oynar/anayasa-özeti/script-adı çıkar; ayırt edici tetik + olumsuz kapsam + oto-tetik kalsın); `aile_dogrula` eşiğini >850 HATA'ya çek; `tetik-vakalari.md` regresyon listesi.
- ⬜ **G/H/I — küçük sağlamlaştırmalar:** gizlilik balanced "raporla-engelleme" + "varsayılan strict" politika notu; udf_yaz UTF-16 offset (non-BMP karakter); oa_ingest EYP dalını önbelleğe bağla (delta döngüsünde her koşuda yeniden OCR).

## 7. FABLE 5 — geliştirme fikirleri (öncelik önerisiyle)

1. **MCP döküm diski** (`_oa/teyit/dokum/`) — oa-ictihat her MCP sonucunu ham diske yazar; kunye_teyit deliğini kapatır + delta'da araştırma tekrarlanmaz.
2. **Teslim paketi kapısı** (`teslim_paketi.py`) — dilekce_denetim→kunye_teyit→gizlilik→defter --denetle→udf_yaz tek komut zinciri.
3. **Süre nöbetçisi** (`sure_nobetci.py`) — oturum açılışında sureler.json'dan D-7/D-3/D-1/GEÇMİŞ uyarısı ("disk pasiftir" zaafını kapatır).
4. **Gelişme→refleks eşleyici** — tam_tur --delta yeni evrağın türünü tahmin edip refleks (ör. "bilirkişi → itiraz süresi") önerir.
5. **Karşı-iddia kapatma denetçisi** — cevap/istinaf taslağı karşı dilekçedeki her iddiaya cevap vermiş mi.
6. **EK eşleyici** — taslaktaki EK-N atıfları manifest evrakıyla eşleşiyor mu.
7. **Dilekçe şablon tek-kaynağı** (`dilekce_sablon.json`) — dilekce_denetim + udf_yaz aynı tertip tanımından okur.
8. **Kapanış dersi damıtıcısı** (`ders_damit.py`) — _oa/dersler kaydını gizlilik kütüphanesiyle anonimlik kapısından geçirir (oa-usta'ya).

**Fable öncelik sırası:** §6-C (defter yarışı + --kok) → §6-B (delta körlüğü) → §6-F (kendi-kendini-teyit) → §6-K (description) → §7-Fikir 2 (teslim paketi) → §7-Fikir 1/3.

---
© 2026 Av. Bayram Can Çapar — FSEK. İzinsiz çoğaltma/dağıtma/türev yasaktır.

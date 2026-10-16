# KARAR MATERYALİ — heyet ikinci koşumu 2026-10-16

**Dal:** `denetim/fable-2026-10-15` · **HEAD:** `ca37539` · **Taban:** `origin/main` = `753e48c` (v0.6.0) ·
**Kapsam:** `origin/main..HEAD` — 16 commit (`52de60f` … `ca37539`), 98 dosya, +4389/−675 · **Push:** yapılmadı.
Heyet karar vermez, karar materyali üretir (anayasa m.9); push yalnız avukatın kararıyla, avukatın elinden yapılır.

**Niteliği.** Aynı dal için ikinci koşum. İlk koşum ([../2026-10-16/KARAR.md](../2026-10-16/KARAR.md), HEAD
`8be918f`): üç üye ŞARTLI PUSH, push öncesi şart K-1 (Excel kapısında ızgara gezintisi) ve K-2 (tablo stili
zemini). Avukat kararı (aynı gün): "push etme; önce K-1 ve K-2'yi önce kırmızı testle kapatalım, tam süit ve
heyet yeniden koşsun; sonra push kararını tekrar sor." Onarım `ca37539` ile commit'lendi
([ajan-raporlari/00-INDEX.md](ajan-raporlari/00-INDEX.md)); üç üye aynı anda yeniden çağrıldı, her biri
kapılarını varsayılan ayarla açılmış temiz geçici worktree'de kendisi koşturdu, üç geçici worktree de kaldırıldı.
Alt ajan raporları beyan sayıldı, ağaçta ölçüldü; rapor ile diff ayrışan iddia bulunmadı (USUL §1.7: 14/14).

**Karar kuralı** (protokol m.3, [../README.md](../README.md)): tek BLOKLAYICI bile varsa PUSH ETME; üçü de PUSH
diyorsa PUSH; ŞARTLI PUSH şartları birleştirilir, her şart bir onarım kalemi olur.

## 1. Üç öneri yan yana

| Üye | Rapor | Öneri | BLOKLAYICI | UYARI | NOT | Kendi koşturduğu ana kapılar (son satır) |
|---|---|---|---|---|---|---|
| USUL | [01-usul.md](01-usul.md) | ŞARTLI PUSH | 0 | 2 | 6 | tam süit `3803 passed, 12 skipped in 176.42s`; perf `1 passed`; toplanan 3816 = OA-SUIT-SAYISI 3816; aile `TEMİZ` (20); ruff `All checks passed!`; `satir_sayaci --yaz` güncel ×2, `--json` 49.022 / 3816; `hook_doktor --kurulu` ✓; "önce kırmızı" yeniden üretildi (eski motor `3 failed` → yeni `3 passed`); K-8 düzeneği `58 passed`; SKILL.md farkı 1 satır |
| ESAS | [02-esas.md](02-esas.md) | ŞARTLI PUSH | 0 | 2 | 11 | hedefli 6 dosya `200 passed in 21.64s`; aile `TEMİZ`; K-1 eşdeğerlik 10 kenar durumunda birebir, önce/sonra 400 MB → 0,3 MB; K-2 10 düzenek; hukuki dayanak değişikliği yok, TEYİT BEKLİYOR yok |
| GÜVENLİK | [03-guvenlik.md](03-guvenlik.md) | PUSH | 0 | 0 | 5 | eklenen 1278 satırda sır deseni 0; b38 `3 passed`; hijyen `7 passed`; ruff temiz; güvenlik seti `263 passed`; teslim zinciri / sürüm kilidi / bağlantı / vitrin `133 passed`; hassas dosyalar (`plugin.json`, `marketplace.json`, `hooks/`, `requirements.txt`, `udf_yaz.py`, `gizlilik_tara.py`, `.github/`) değişmedi; U-1/K-1, `xl/` ve K-2 kapanışı bağımsız düzenekle doğrulandı |
| **Bütün** | | **ŞARTLI PUSH** | **0** | **4** | **22** | |

## 2. Bütünleşik sonuç

**Heyet önerisi: ŞARTLI PUSH** (kural: iki ŞARTLI PUSH + bir PUSH → şartlar birleşir). BLOKLAYICI yok. Avukatın
push öncesi şart koştuğu K-1 ve K-2 üç üyenin ayrı ölçümüyle kapandı: ızgara gezintisi yok (5 KB kitap + uzak
stilli hücre: 6,29 s / 400 MB → 0,01 s / 0,3 MB; okuyucu eşlemesi on kenar durumunda bozulmadı), tablo stilindeki
beyaz başlık artık yanlış BULGU üretmiyor, boyut sınırı `xl/` bütününe uygulanıyor; "önce kırmızı" izi commit
mesajında ve testlerde, usul tarafından yeniden üretildi. HEAD'in temiz kopyasında tam süit yeşil; sır sızıntısı,
Layer 0 gevşemesi, uç nokta değişikliği yok; hukuki dayanak dokunulmamış.

Birleşik şartların zamanlaması:

- **Push'tan önce (USUL 1):** K-5 (taşıma atfı notu) ve K-7 (`.gitignore` `.claude/`) + bedelsiz N-2 (DENETIM
  §6 tarihli ölçüm satırı) ve N-3 (STATUS başlık tarihi) — hepsi kayıt sınıfı, kod yok. **Bu KARAR commit'iyle
  kapatıldı** (§4; GÜVENLİK §5'in sonunda "başka oturumun 5 izlenen dosyada commit'siz değişikliği" diye gördüğü
  değişiklikler bu kalemlerin ta kendisidir — orkestra oturumunun kayıt işi, bu commit'te).
- **Push'tan önce (USUL 2):** bu koşumun dosyaları commit'lenince K-8 düzeneğiyle kapılar + CHANGELOG/STATUS
  satırı — **bu commit'te yapıldı** (§4.1).
- **Aynı dalda ayrı commit, push öncesi değil (ESAS Ş-1, Ş-2; ESAS/USUL sınıflandırmasıyla K-3, K-4):** ZAYIF
  aralık kaydı (E-5), 128 MB tavanının bellek karşılığı (E-7), UYARI etiketi (K-3), `<ol start>` UDF ölçümü (K-4).
- **Açık kalem (GÜVENLİK beklentisi; STATUS/YOL-HARITASI):** süre denetimi ve sütun açıklığı (G N-1, N-2; ESAS
  N-2), `docProps` toplamı (G N-3), üreteç hatalarının sarmalanması (G N-4), satır sonu duyarlı test (USUL N-1),
  kapı `SURUM` kararı (USUL N-6), eklenti README'de Excel (ilk koşum ESAS N-4).

**Sonuç:** bu commit'ten sonra üç üyenin "push'tan önce" dediği hiçbir şart açık kalmaz; kalanların tümü üyelerce
"aynı dalda ayrı commit" ya da "açık kalem" sınıfındadır ve hepsi fail-closed'dur. Push kararı avukatın (§7).

## 3. Bulgular — tek liste (2. koşum)

Kanıt, satır numaraları ve düzenekler üye raporlarındadır; burada özetlenir. Birleşik numaralar H2-n.

**H2-1 · UYARI · USUL U-1 (= ilk koşum K-5) · `docs/DENETIM-2026-10-15.md` §6 Görev 2 / Görev 4; CHANGELOG
"Kök dizin ve bağlantı kapısı".** Arşiv taşıması (13 `R100`) fiilen `47bba4d`'de; kayıt `45a6d2e`'ye atfediyordu.
Ürün etkisi yok; kayıt zinciri yanıltıcı. **Kapatıldı (bu commit):** DENETIM Görev 2 ve Görev 4 satırlarına ve
CHANGELOG maddesine kayıt notu. Tarihçe düzeltmesi (commit kimliklerini değiştirir) istenirse avukat kararı.

**H2-2 · UYARI · USUL U-2 (= ilk koşum K-7; GÜVENLİK ilk N-5) · `.gitignore`; `docs/heyet/README.md:3-4`.**
`.claude/` yalnız yerel `info/exclude`'da yok sayılıyordu; taze klonda ajan kopyaları ve yerel ayar/izin dosyaları
(yerel yol içerebilir, B-38 sınıfı) yanlışlıkla commit'lenebilirdi. **Kapatıldı (bu commit):** `.gitignore`'a
`.claude/` (izlenen dosya 0; `git check-ignore` artık `.gitignore:29`), protokol cümlesi `.gitignore`'a dayanıyor.

**H2-3 · UYARI · ESAS E-5 · `belge_guvenlik.py:2410-2412` (ZAYIF listesi), `:2656`; `README.md:1384-1387`,
`SKILL.md:46`.** Tablo stili ve koşullu biçim aralığındaki düşük kontrastlı hücre için gizlilik hesaplanıyor
ama talimat dili yoksa ne kayıt ne damga düşüyor (rapor `None`): Medium2 gövde şeridinde beyaz yazı/beyaz tarih
görünür ve damgasız (tarih süre adayı olabilir, m.2; sınırlayıcılar sürüyor), Light1 başlığında beyaz yazı Excel'de
de görünmezken kapı susuyor, hücrenin KENDİ düz dolgusu varken bile ZAYIF sayılıyor (oysa zemin kesin). m.11'in
çekirdeği (talimat dili yakalama) korunuyor; m.6 kazancı bu kayıptan ağır; eksik olan evrak düzeyinde bildirim.
Onarım (aynı dalda ayrı commit, önce kırmızı test): AGIR olmayan `zemin-olculemedi` kaydı (sayfa, aralık, hücre
sayısı, ilk örnek) → UYARI, damga yok; tablo stili aralığında hücrenin kendi düz dolgusu varsa ölçüm; README/SKILL
"bildirilir". `.xls` tarafı ölçülemedi (xlrd tablo stilini okumaz).

**H2-4 · UYARI · ESAS E-7 · `belge_guvenlik.py:157-163` (`AZAMI_TABLO_XML_BAYT` 128 MB; yorum "tahmin: ≤ 0,5 GB"),
`:2439`.** Tavanın bellek karşılığı: 300.000 hücre / 14,6 MB sayfa XML'i → kapı tepe 116 MB; 200.000 hücresiz gizli
`<row>` tanımı / 6,2 MB XML (sıkıştırılmış 508 KB) → 121 MB. `tahmin:` doğrusal ölçekle tavanda ~1 GB (hücre yoğun)
… ~2,4 GB (gizli satır başlığı yoğun; ~10 MB dosya yeter); koddaki "≤ 0,5 GB" yorumu ölçümle çelişiyor (2–5×).
Fail-closed (`MemoryError` → DENETLENEMEZ), ama 8 GB makinede takas ve dakikalarca kilit; K-1 sınıfı, daha büyük
dosya ister. Onarım (ayrı commit): tavanı ölçümle yeniden belirlemek (ör. 32 MB) ya da sayfa XML'inde ucuz `<row`
/ `<c ` nesne sayımı; yorumu düzeltmek; önce kırmızı test.

NOT'lar (bloklamaz; kayıt ve izleme):

- **USUL N-1** — `tests/test_v0511_kit_guvenlik.py::test_yonlu_tazelik_ozdes_sessiz` LF checkout'ta kırmızı
  (`read_text`/`write_text` CRLF dönüşümü; HEAD'de ve `origin/main`'de aynı; `udf_yaz.py` ve test bu dalda
  değişmedi), CRLF checkout ve CI'da yeşil. Test düzeneği kusuru, ürün değil; ayrı kalem: `write_bytes`.
- **USUL N-2** — DENETIM §6 heyet/onarım sonrası bayattı → **kapatıldı (bu commit):** tarihli ölçüm satırı, §7/5 notu.
- **USUL N-3** — STATUS başlık tarihi 2026-10-12 → **kapatıldı (bu commit):** 2026-10-16.
- **USUL N-4** — `hook_doktor --kurulu` kurulu 0.6.0 önbelleğini ölçer, dal içeriğini değil (aynı sınır).
- **USUL N-5** — paylaşılan ağaçta `test_b35` kırmızı (toplanan 3853 ≠ 3816; fark 37 = başka oturumun izlenmeyen
  iki test dosyası); commit'li ağaçta yeşil. Karar dışı işin etkisi.
- **USUL N-6** — Excel kapısı `SURUM` 1.2'de bırakıldı (gerekçe oa-ingest günlüğünde: kod yayımlanmadı); dalın
  koduyla yerelde taranmış Excel kaydı varsa eski karar önbellekte kalır. Damga kararı avukatın.
- **ESAS N-1** — K-1 kapanışı ölçüldü: 10 kenar durumunda yeni gezinti `iter_rows` ile birebir (sütun uzayı 1'den,
  ara `None`, kuyruk, sıra, `MergedCell`, stilli boş, formül, yorum, hücresiz gizli satır, uzak değerli); bellek
  400,1 / 401,0 MB → 0,3 MB.
- **ESAS N-2** — `belge_guvenlik.py:2398-2404` gizli `<col>` yığını (16.384 tanım, 50 KB) → `set.update` 1,7 s/sayfa;
  belleksiz; öneri: `d.max`'ı `ws.max_column` ile kıskaçlamak (tek satır).
- **ESAS N-3** — ZAYIF aralıkta talimat dili kaydı "gizlenmiş hücre" der; görünür beyaz yazıda da aynı kayıt düşer
  (m.4/m.6, dar artık). Öneri: yöntem metni "zemini ölçülemeyen aralıkta açık renkli yazı — gizli olduğu kesin değil".
- **ESAS N-4** — pivot tablo stili ZAYIF listesinde değil (kod okuması; `tahmin:` koyu pivot stilinde yanlış BULGU).
- **ESAS N-5** — `ws._cells` özel API; `requirements.txt` `openpyxl>=3.1` üst sınırsız; kalkarsa her `.xlsx`
  DENETLENEMEZ ve `test_v0519…:622` kırmızı (sessiz değil). Öneri: üst sınır ya da kurulum denetimi.
- **ESAS N-6** — `xl/` toplamı meşru kitapta yanlış DENETLENEMEZ'e yol açmaz (`tahmin:` eşik ~2,0 M hücre; HTS
  dökümü etkilenmez).
- **ESAS N-7** — vitrin sayıları ölçümle birebir (49.022 / 3816 / 31 test); günlükte "önce" sayılarının heyet
  ölçümü olduğu belirtilmeli (kaynak izi).
- **ESAS N-8** — hukuki dayanak değişikliği yok; TEYİT BEKLİYOR yok.
- **ESAS N-9** — bitişik damgalar tek `⟦GİZLİ KATMAN⟧` bloğunda birleşir; kayıp değil, bilgi.
- **ESAS N-10** — alt ajan raporları ağaçla örtüşüyor (`excel-oturumu-ozeti.md` dahil).
- **ESAS N-11** — `47372fc` yalnız belge, m.9 uyumlu.
- **GÜVENLİK N-1** — sütun açıklığı maliyeti: her satırda 1. ve 16.384. sütun dolu, 1000 satır (17 KB) → kapı
  25,8 s / 95 MB, okuyucu 1,7 s (okuyucu metni 46,9 MB — `origin/main` davranışı); bellek sınırlı; satır döngüsünde
  süre denetimi yok. Onarım: `_tablo_sayfa_isle`'de `AZAMI_SURE_SN` denetimi ya da satır başına açıklık tavanı.
- **GÜVENLİK N-2** — düşük kontrastlı hücre × ZAYIF aralık: `CellRange.__contains__` 3,2 µs/çağrı, 300 tablo × 500
  hücre 0,60 s; aralık sayısına tavan yok (ilk koşum N-3'ün genişlemiş hâli). Onarım: süre denetimi; aralıkları
  dörtlüye çözüp nesne kurmadan karşılaştırmak.
- **GÜVENLİK N-3** — boyut toplamı `xl/` ile sınırlı; openpyxl `docProps/core.xml`, `custom.xml`,
  `[Content_Types].xml`'i de bütünüyle açar: 45,8 KB kitapta 40 MB dolgu → okuyucu 96 MB, kapı 86 MB. Onarım tek
  satır (toplam bütün girdiler) + test.
- **GÜVENLİK N-4** — üreteç içi hatalar (`_cells` yok, bozuk `ref`: `CellRange("A1:B")` `ValueError`, `"A:C"`
  `TypeError`) `tara()` dış `except`'ine düşer: metin bütünüyle VERİ (fail-closed, ölçüldü) ama sebep "tarama hatası",
  gizli sayfa/talimat sınıflaması o yolda yok. Onarım: `_tablo_tara` sayfa döngüsünü aynı üç `except` ile sarmak.
- **GÜVENLİK N-5** — ilk koşum kalemlerinin HEAD'deki durumu (§4 ile aynı).

## 4. Kalemler — durum ve yeni onarım kalemleri

| Kalem | Kaynak | Durum (bu commit sonrası) | Ne / kanıt |
|---|---|---|---|
| K-1 | ESAS E-1 = GÜV U-1 | **kapandı** (`ca37539`) | üç üye ölçtü: 400 MB → 0,3 MB; eşleme bozulmadı; ızgara kilidi testi |
| K-2 | ESAS E-2 | **kapandı** (`ca37539`; bedeli H2-3) | tablo stili başlığı → rapor yok; talimat dili → BULGU |
| GÜV N-1 (ilk) | `xl/` toplamı | **kapandı** (`ca37539`); `xl/` dışı → K-12 | test `:643` |
| K-3 | ESAS E-3 | açık — aynı dalda ayrı commit | UYARI etiketi `TALİMAT-DİLİ`; `okuma_kapisi.py:69` |
| K-4 | ESAS E-4 | açık — aynı dalda ayrı commit | `<ol start>` udf-cli ölçümü ya da "UDF-HTML'de" sınırı |
| K-5 | USUL U-1 | **kapandı (bu commit)** | DENETIM §6 Görev 2/4 notu, CHANGELOG notu; tarihçe düzeltmesi avukat kararı |
| K-6 | USUL U-2 (ilk) | kapandı (`47372fc`) | üç üye doğruladı |
| K-7 | USUL U-3 + GÜV N-5 (ilk) | **kapandı (bu commit)** | `.gitignore` `.claude/`; protokol cümlesi |
| K-8 | USUL 4 | kapandı (`47372fc`); bu commit için yinelendi | §4.1 |
| K-9 | USUL 5 + GÜV 3 | değişmedi — kapsam dışı | commit'siz iş (§6); commit'lenince OA-SUIT-SAYISI (ölçülen 3853), ilan testleri, SECURITY.md cümlesi, tam süit, heyet |
| K-10 | ESAS E-5 (H2-3) | yeni — aynı dalda ayrı commit | ZAYIF aralık kaydı; düz dolgulu hücrede ölçüm; "bildirilir" |
| K-11 | ESAS E-7 (H2-4) | yeni — aynı dalda ayrı commit | tavan/nesne sayımı ölçümle; yorum düzeltmesi |
| K-12 | GÜV N-3 | yeni — ayrı commit (tek satır + test) | boyut toplamı bütün girdiler |
| K-13 | GÜV N-1, N-2; ESAS N-2 | yeni — ayrı commit | satır döngüsünde `AZAMI_SURE_SN`; `<col>` kıskacı; aralık üyeliği nesnesiz |
| K-14 | GÜV N-4 | yeni — ayrı commit | üreteç hatalarını `_tablo_denetlenemedi`'ye düşürmek |
| K-15 | USUL N-1 | yeni — ayrı kalem | testte `write_bytes(read_bytes())` |
| K-16 | ESAS N-3, N-4, N-5, N-7; ilk ESAS N-4; USUL N-6 | açık kalemler | kayıt metni, pivot stili, `_cells` sözleşmesi, günlük kaynak notu, eklenti README Excel, `SURUM` kararı |

### 4.1 K-8 ölçümü (bu commit'in dosyaları)

Düzenek: `git worktree add --detach <geçici> HEAD` (`ca37539`, varsayılan ayar) → bu commit'in 13 dosyası geçici
ağaca kopyalanıp indeksine alındı (`git add -A`; b38 `git ls-files` taradığı için) → kapılar koşuldu → geçici
worktree `git worktree remove --force` ile kaldırıldı (`git worktree list`'te yok).

| Kapı (geçici temiz worktree · `py -3.14` · `PYTHONUTF8=1 OA_TEST_UDF_YAZICI=0` · `-p no:cacheprovider`) | Son satır |
|---|---|
| `pytest tests/test_belge_baglantilari.py tests/test_v0518_metin_hijyeni.py tests/test_kaynak_hijyeni.py tests/test_v0514_vitrin.py tests/test_eklenti_vitrini.py tests/test_v0586_surum_kilidi.py -q -rsfE` | `58 passed in 10.73s` — bağlantı 0 kırık; b35 toplanan = OA-SUIT-SAYISI 3816; b38 mutlak yol 0 |
| `aile_dogrula.py plugins/ortak-avukat/skills` | `AİLE YAPI DENETİMİ TEMİZ.` (20 parça) |
| `satir_sayaci.py --yaz` | `güncel` ×2 |
| `ruff check .` | `All checks passed!` |
| Python taraması — sahnelenen 1180 eklenen satır: Cf / çift yönlü / NBSP karakter · mutlak yerel yol | 0 · 0 |

Kod değişmediği için tam süit yeniden koşulmadı (USUL 2. koşum §3 şart 1: "süit yeniden koşulmaz; bağlantı /
metin hijyeni / b38 / b35 kapıları yeter"); HEAD `ca37539` için tam süit usul raporunda (3803 · 12 · 0).

## 5. Doğrulanamayanlar (üç raporun birleşimi)

- Tam süit yalnız usul üyesinde (3803 · 12 · 0); esas ve güvenlik hedefli kümeler (200; 263 + 133).
- udf-cli oturumu yok: 11 test atlandı; `<ol start>` UDF/PDF yolu (K-4) ölçülmedi. `OA_SAHA_REFERANS` yok (1).
- Kurulu eklenti dalın içeriğiyle kurulmadı; `hook_doktor` kurulu 0.6.0 önbelleğini ölçtü.
- Ağ yok: CI koşusu, PR #6, B-8, Yargı Pro uç noktası sağlık denetimi.
- Gerçek Excel evrakında yanlış alarm ve tablo stili / sütun açıklığı sıklığı ölçülmedi (sentetik düzenekler).
- `.xls`'te tablo stili davranışı (Excel yok); pivot stili (openpyxl üretmez) — kod okuması ve tahmin.
- E-7 tavan tahmini 6,2 ve 14,6 MB'da ölçüldü, 128 MB'da değil; süreler usul süitiyle eş zamanlı yük altında.
- openpyxl yalnız 3.1.5 ile ölçüldü (`_cells` sözleşmesi).
- Onarımın süre/bellek sayıları usul tarafından yinelenmedi (mekanizma testiyle dolaylı); esas ve güvenlik yineledi.
- Ara commit'lerde tam süit yok; yalnız HEAD.

## 6. Commit'lenmemiş iş — karar dışı

Başka oturumun açık işi değişmedi: izlenen 9 dosya (`173 insertions(+), 49 deletions(-)` — `plugin.json`
`mcpServers` kaldırma, `marketplace.json`, oa-ingest `SKILL.md` 48/88/91. satır hunk'ları,
`gizli-talimat-ifsasi.md`, `gizli_talimat_ifsa.py`, `ictihat_muhakeme_denetim.py`, `kunye_ortak.py`,
`oa_hafiza.py`, `tests/test_kaynak_url.py`) + izlenmeyen 3 dosya (`resmi-kaynaklar.md`,
`tests/test_kanal_bagimsiz_metin.py`, `tests/test_teyit_kanali.py`). Üç üye dokunmadı; bu karar yalnız commit'li
fark üzerinedir. Commit'lenince K-9 düzeneği ve heyetin yeniden koşumu (B-23). GÜVENLİK §5'in gördüğü "5 izlenen
dosyada başka oturumun commit'siz değişikliği" (`.gitignore`, CHANGELOG, STATUS, DENETIM, `docs/heyet/README.md`)
bu oturumun K-5/K-7/N-2/N-3 kayıt işidir ve bu commit'tedir.

## 7. Avukata sunulan karar

Heyet karar vermez. Soru: **`denetim/fable-2026-10-15` dalı push edilsin mi?**

- **Heyet önerisi:** ŞARTLI PUSH; bu kayıt commit'iyle birlikte "push'tan önce" sınıfında açık şart kalmadı
  (K-1, K-2, K-5, K-7 kapandı; K-6, K-8 önceden). Kalan kalemler (K-3, K-4, K-10 … K-16) üyelerce aynı dalda ayrı
  commit ya da açık kalem sınıfındadır; hepsi fail-closed, hiçbiri sır ya da sessiz geçiş değildir. Güvenlik
  üyesi koşulsuz PUSH dedi.
- **Seçenekler:** (a) dal bu hâliyle push edilir, kalan kalemler STATUS/YOL-HARITASI'nda açık kalem olarak sonraki
  commit'lerde kapanır; (b) önce K-10 ve K-11 (ESAS'ın iki uyarısı; önce kırmızı test, tam süit, heyet yeniden),
  sonra push; (c) push edilmez, dal bekler.
- **Dalın hiçbir parçası** commit'siz işi kapsamaz; o iş için push kararı ayrıca verilir (K-9).

Bu belge, üç üye raporu, ajan raporları ve kayıt kalemleri dala commit'lendi; push yapılmadı.

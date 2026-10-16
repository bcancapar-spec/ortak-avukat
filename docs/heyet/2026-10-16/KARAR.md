# KARAR MATERYALİ — heyet koşumu 2026-10-16

**Dal:** `denetim/fable-2026-10-15` · **HEAD:** `8be918f` · **Taban:** `origin/main` = `753e48c` (v0.6.0) ·
**Kapsam:** `origin/main..HEAD` — 14 commit (`52de60f` … `8be918f`), 90 dosya, +3134/−675 ·
**Push:** yapılmadı. Heyet karar vermez, karar materyali üretir (anayasa m.9); push yalnız avukatın
kararıyla, avukatın elinden yapılır.

**Koşum.** Üç üye aynı anda, Fable modeliyle çağrıldı (protokol: [../README.md](../README.md)). Her
üye kapılarını temiz geçici worktree'de (HEAD `8be918f`, `git status` boş) kendisi koşturdu;
paylaşılan ağaçta başka oturumun commit'siz işi durduğu için süit orada koşulmadı. Üç geçici
worktree de kaldırıldı (`git worktree list`'te yok). Alt ajan raporları
([ajan-raporlari/00-INDEX.md](ajan-raporlari/00-INDEX.md)) beyan sayıldı, her iddia ağaçta ölçüldü;
rapor ile diff ayrışan iddia bulunmadı. Koşum notu 13 commit demişti, ölçüm 14 (USUL N-1); bu
belge 14 yazar.

**Karar kuralı** (protokol m.3): tek BLOKLAYICI bile varsa PUSH ETME; üçü de PUSH diyorsa PUSH;
ŞARTLI PUSH şartları birleştirilir, her şart bir onarım kalemi olur.

## 1. Üç öneri yan yana

| Üye | Rapor | Öneri | BLOKLAYICI | UYARI | NOT | Kendi koşturduğu ana kapılar (son satır) |
|---|---|---|---|---|---|---|
| USUL | [01-usul.md](01-usul.md) | ŞARTLI PUSH | 0 | 3 | 5 | tam süit `3800 passed, 12 skipped in 93.99s`; perf `1 passed`; toplanan 3813 = OA-SUIT-SAYISI 3813; aile `TEMİZ` (20 parça); ruff `All checks passed!`; `satir_sayaci --yaz` "güncel" ×2; `hook_doktor --kurulu` `TÜM MEKANİK KONTROLLER GEÇTİ`; sürüm damgaları 7 yerde 0.6.0 |
| ESAS | [02-esas.md](02-esas.md) | ŞARTLI PUSH | 0 | 4 | 7 | hedefli 11 test dosyası `326 passed in 9.55s`; aile `TEMİZ`; `satir_sayaci --json` künyeyle birebir; hukuki dayanak değişikliği yok, TEYİT BEKLİYOR yok; koruma gevşemesi altı eksende bulunmadı |
| GÜVENLİK | [03-guvenlik.md](03-guvenlik.md) | ŞARTLI PUSH | 0 | 1 | 6 | eklenen 3134 satırda sır deseni 0; b38 `3 passed`; metin + kaynak hijyeni `7 passed`; ruff temiz; güvenlik seti (10 dosya) `260 passed`; teslim zinciri / sürüm kilidi / bağlantı / vitrin (7 dosya) `133 passed`; `plugin.json`, `marketplace.json`, `hooks/`, `run-hook.cmd`, Layer 0 ve teslim zinciri dosyaları değişmedi |
| **Bütün** | | **ŞARTLI PUSH** | **0** | **8** | **18** | |

## 2. Bütünleşik sonuç

**Heyet önerisi: ŞARTLI PUSH.** BLOKLAYICI yok. HEAD'in temiz kopyasında altı kapının altısı
yeşil; sayaç ve damgalar tutarlı; sır sızıntısı, Layer 0 gevşemesi, sahipsiz uç nokta yok; hiçbir
kapı fail-open'a dönmemiş, teyit zinciri kısalmamış, avukat kararı modele kaymamış, süre kuralı
değişmemiş, olgu üretilmemiş. Dal müvekkili dört eksende daha iyi korur: Excel gizli katmanı artık
ölçülüyor, talep bendi numarası korunuyor, kaynak hijyeni ve bağlantı kapıları var, vitrin ölçümle
kilitli.

Sekiz UYARI'nın ikisi iki üyenin ayrı ayrı bulduğu aynı bulgudur (H-1: ESAS E-1 = GÜVENLİK U-1;
H-7: USUL U-3 = GÜVENLİK N-5); birleşik liste 7 UYARI taşır. Üyelerin "push'tan önce" dediği
şartlar yalnız ikidir ve ikisi de yeni Excel kapısındadır (H-1, H-2); kalanı aynı dalda ayrı commit
ya da kayıt düzeltmesidir (§4).

## 3. Bulgular — tek liste

Sıra: önce UYARI'lar, sonra NOT'lar. Kanıt, satır numaraları ve ölçüm düzenekleri üye
raporlarındadır; burada özetlenir.

**H-1 · UYARI · ESAS E-1 + GÜVENLİK U-1 · `belge_guvenlik.py:2368-2403` (`_xlsx_satirlar`,
`ws.iter_rows()` tam kip).** Excel kapısı sayfayı sınırsız gezer; maliyet dosya boyutuna değil
ızgaraya (`max_row × max_column`) bağlı; `AZAMI_TABLO_XML_BAYT` (128 MB) bunu bağlamaz. İki üyenin
bağımsız sentetik ölçümü örtüşüyor: 5 KB kitap + değersiz tek uzak stilli hücre (satır 3000 × sütun
600 / satır 20.000 × sütun 100) → kapı 6,29 s ve yaklaşık 400 MB; okuyucu (`tablo_isle`, salt-okur)
0,00 s. Bellek tükenince `MemoryError` → DENETLENEMEDİ (fail-closed; sessiz geçiş yok, sır sızmaz).
Müvekkile etkisi: evrak ekseni (alım kilitlenir) ve gizli tuzak ekseni (karşı tarafın 5 KB'lık
hazırlanmış tablosu avukatın makinesini dakikalarca kilitler; hizmet engelleme). Onarım: sayfa
başına koordinat tavanı → `_TabloOlculemedi` → sebepli DENETLENEMEDİ, ya da yalnız var olan
hücreleri gezmek; önce kırmızı test (tek uzak hücreli fikstür: karar DENETLENEMEZ, süre 1 saniyenin
altında, bellek sabit).

**H-2 · UYARI · ESAS E-2 · `belge_guvenlik.py:2332-2345` (`_xlsx_zemin`), `:2275`
(`_kontrast_bulgusu`); `oa-ingest/SKILL.md:38`, `:46`; `README.md:1379`.** "Biçimlendir → Tablo"
(`ws.tables`, tablo stili) zemini okunmuyor; hücrenin kendi dolgusu yoksa zemin beyaz varsayılıyor.
Ölçüm: stil zeminli koyu başlık satırı + beyaz kalın yazı → kapı kararı **BULGU**, 3 `gizli-metin`,
örnekler başlık metinleri (Excel bunları koyu zeminde görünür çizer). DOCX'te 2026-10-05 ölçümünde
3.343 yanlış alarm üreten "koyu hücredeki beyaz başlık" sınıfının Excel eşleniği. Müvekkile etkisi:
m.6 — BULGU ifşa bölümüne adaydır; yersiz ifşa müvekkilin güvenilirliğini zedeler; tablo stili
dürüst sınırda da anılmıyor. Onarım: `ws.tables` aralıklarındaki açık yazıyı koşullu biçim kuralıyla
aynı ZAYIF sınıfa almak (yalnız talimat diliyle bulgu) ya da zemini "ölçülmez" saymak; SKILL.md ve
README dürüst sınırına "tablo stili"; `.xls`'te xlrd okumaz → "ölçülmez"; önce kırmızı test.

**H-3 · UYARI · ESAS E-3 · `belge_guvenlik.py:2811-2820` (`ozet_etiketi`), `:2784-2796`
(`md_basligi`); `oa-pipeline/scripts/okuma_kapisi.py:69`; `gizli_talimat_ifsa.py:570`.** Excel
gizli satır/sütun/sayfa/biçim UYARI'sı (v0.5.19 ile ilk kez oluşuyor) okuma listesinde ve INDEX'te
`TALİMAT-DİLİ` etiketiyle, md başlığında "talimat dili ya da görünmez karakter" cümlesiyle
gösteriliyor. Bildirim var, adı yanlış (m.11); avukat gizli satırı biçimsel bir uyarı sanabilir.
Onarım: UYARI etiketi ve başlık türe göre (ör. GİZLİ-KATMAN), `okuma_kapisi` eşlemesi tek kaynaktan;
test: gizli satırlı Excel'in etiketi "TALİMAT-DİLİ" olmamalı.

**H-4 · UYARI · ESAS E-4 · `CHANGELOG.md:320`, `docs/DENETIM-2026-10-15.md:52` ↔
`tests/test_md_udf_html.py:88`, `:96`.** "9. bent artık '1.' basılmıyor" iddiası yalnız UDF-HTML
dizgesinde (`<ol start="9">`) testli; udf-cli ve PDF yolunda ölçüm kaydı yok (CI kipinde 12
atlama). Kod yönünde gerileme yok (1'den başlayan liste bayt-özdeş). Müvekkile etkisi: doğrulanmamış
bilgi ekseni (vitrin) — mahkeme bent numarasına atıf yapar. Onarım: udf-cli oturumu açık makinede
bir kez ölçüm ve kayıt; o zamana kadar CHANGELOG/DENETIM cümlesine "UDF-HTML'de; UDF/PDF çıktısı
udf-cli ile ölçülecek" sınırı.

**H-5 · UYARI · USUL U-1 · `47bba4d` ↔ `45a6d2e`; `docs/DENETIM-2026-10-15.md` §6 Görev 2 /
Görev 4; CHANGELOG "Kök dizin ve bağlantı kapısı" maddesi.** 13 dosyalık arşiv taşıması (`R100`)
fiilen `47bba4d` ("metin hijyeni") commit'indedir; `45a6d2e` yalnız bağlantı yeniden yazımını
taşır. `45a6d2e` mesajı ve DENETIM §6 taşımayı `45a6d2e`'ye atfeder; `47bba4d` ara durumunda
CHANGELOG'da köke işaret eden 13 kırık bağlantı var (bağlantı kapısı henüz doğmamıştı). Üretim
davranışı değişmez (HEAD yeşil); kayıt zinciri yanıltıcı: `47bba4d` tek başına geri alınırsa arşiv
de geri gider; `git bisect` taşımayı yanlış commit'te arar. Onarım: (a) asgari — DENETIM §6 ve
CHANGELOG'a "taşıma fiilen `47bba4d` ile girdi, bağlantılar `45a6d2e`'de düzeltildi" notu; (b) tam —
dal push edilmediği için mümkün: tarihçe düzeltmesi (commit kimlikleri değişir, DENETIM ve heyet
raporlarındaki atıflar güncellenir) — avukat kararı.

**H-6 · UYARI · USUL U-2 · CHANGELOG, STATUS.** Heyet commit'leri (`c5f739f`, `8be918f`) sürüm
defterinde ve STATUS'ta kayıtsızdı (grep 0); `c5f739f` depo sözleşmesine yeni bir push-öncesi kapı
ekliyor. Onarım: CHANGELOG "Sürümsüz" kaydına Heyet maddesi + STATUS'a 2026-10-16 notu. **Bu
KARAR commit'iyle kapatıldı** (§4 K-6).

**H-7 · UYARI · USUL U-3 + GÜVENLİK N-5 · `.gitignore`; `docs/heyet/README.md` ve
`ajan-raporlari/orkestra-kok-katalog-ve-heyet.md` "git'te yok sayılır" cümleleri.** `.claude/`
yalnız bu makinenin yerel `info/exclude` dosyasında yok sayılır; HEAD `.gitignore`'da `.claude`
geçmiyor (`git ls-files .claude` → 0). Taze klonda protokolün `cp` adımı izlenmeyen dosya üretir;
Claude Code'un `.claude/` altına yazdığı yerel ayar ve izin dosyaları yanlışlıkla commit'lenebilir
(B-38'in koruduğu sınıf). Onarım: `.gitignore`'a `.claude/` (izlenen dosya 0, bedelsiz; `ruff.toml`
zaten dışlıyor) ve README cümlesinin yerel exclude'a değil `.gitignore`'a dayanması.

NOT'lar (bloklamaz; kayıt ve izleme):

- **USUL N-1** — koşum notu 13 commit dedi, ölçüm 14; bu belge 14 yazar.
- **USUL N-2** — "önce kırmızı" izi `7fcbb22`, `47bba4d`, `08aef92` mesajlarında yok; iki test
  dosyasında `NEDEN VAR` başlığı yok (gerekçe docstring'de). Sonraki commit'lerde tek cümle.
- **USUL N-3** — `STATUS.md:3` başlık tarihi 2026-10-12; gövde 2026-10-15 ve 2026-10-16 notları taşıyor.
- **USUL N-4** — `hook_doktor --kurulu` kurulu 0.6.0 önbelleğini ölçer, dal içeriğini değil; "6/6
  kanca sağlıklı" bulgusu kurulu kopyaya aittir.
- **USUL N-5** — paylaşılan ağaçta `test_b35` kırmızı (beyan 3813, toplanan 3850): kaynak başka
  oturumun izlenmeyen iki test dosyası (§6); commit'li ağaçta yeşil.
- **ESAS N-1** — hukuki dayanak değişikliği yok (`*.json`, playbook, references'ta madde/süre/tarife
  farkı 0); dalda yeni tek hukuki cümle `52de60f` e-tebligat açıklaması, teyit izi oa-dilekce
  günlüğü 2026-10-12 (Yargı PRO `mevzuat_getir`). TEYİT BEKLİYOR yok.
- **ESAS N-2** — `belge_guvenlik.py:2529` alım kipinde `gizli-talimat` konumu sabit "gizli katman";
  ifşa bölümünde tespit yeri kesin değil (m.4, m.6). Öneri: aralık → konum haritası.
- **ESAS N-3** — görünür hücre tarihleri artık süre adayı olabilir (v0.5.18'de tüm tablo sarılıydı);
  m.11 ile uyumlu, saha kalibrasyonuyla izlenecek; sınırlayıcılar var (süre adayı kesinlik iddia
  etmez, başlangıç kapısı kanıt ister).
- **ESAS N-4** — `plugins/ortak-avukat/README.md` Excel'i hiç anmıyor (yetenek de sınır da); iki
  vitrinin tutarlılığı için satır eklenmeli (tablo stili dahil).
- **ESAS N-5** — sayılar ölçümle birebir (`satir_sayaci --json` ↔ iki README künyesi ↔
  OA-SUIT-SAYISI 3813).
- **ESAS N-6** — heyet protokolü m.9 ile uyumlu: heyet karar vermez, onay bayrağı üretmez.
- **ESAS N-7** — alt ajan raporlarının iddiaları (14 dosya, +523/−30 = 553, 28 test, 615 → 690
  satır, `SURUM` 1.2) ağaçta doğrulandı; "saha kalibrasyonu açık" uyarısının ilk somut örneği H-2.
- **GÜVENLİK N-1** — `belge_guvenlik.py:2405-2411` boyut ön denetimi yalnız `xl/worksheets/`
  toplar; tam kipe özgü parçalar (yorum, çizim, tablo, pivot önbelleği) sınırsız; hata yolu
  fail-closed. Onarım tek satır: toplamı tüm `xl/` girdileri üzerinden almak (K-1 ile birlikte).
- **GÜVENLİK N-2** — koşullu biçim ZAYIF bölgesinde damgasız gizli tarih süre adayı olabilir
  (belgelenmiş sınır); öneri: AGIR olmayan `kosullu-bicim-araligi` kaydı.
- **GÜVENLİK N-3** — `belge_guvenlik.py:2396` hücre × koşullu-biçim-kuralı maliyeti; kural sayısına
  tavan yok; yalnız süre.
- **GÜVENLİK N-4** — `.github/workflows/ci.yml` eylemleri SHA'ya sabit değil, `permissions:` yok
  (önceden var olan desen; `ruff==0.17.0` ve `udf-cli@${SURUM}` sabit, `secrets.*` yok). Ayrı kalem.
- **GÜVENLİK N-6** — `oa_hafiza.py:772` yinelenen `"bölge"` öğesi silindi; davranış değişmedi.

## 4. Şartlar → onarım kalemleri (birleşik)

Üç üyenin şartları birleştirildi; her şart bir kalemdir. "Zamanlama" sütunu üyelerin kendi
sınıflandırmasıdır.

| Kalem | Bulgu | Üye şartı | Zamanlama | Ne yapılacak |
|---|---|---|---|---|
| K-1 | H-1 | ESAS Ş-1, GÜVENLİK 1 | **push'tan önce** | `_xlsx_sayfalar` / `_xlsx_satirlar`'a sayfa başına koordinat tavanı → sebepli DENETLENEMEDİ (GÜVENLİK N-1'deki `xl/` toplamı aynı kalemde); önce kırmızı test; OA-SUIT-SAYISI ve oa-ingest günlüğü. GÜVENLİK alternatifi: avukat bunu açık kalem olarak STATUS/YOL-HARITASI'na yazmayı seçerse push edilebilir; üyenin tercihi kapatmaktır |
| K-2 | H-2 | ESAS Ş-2 | **push'tan önce** | `ws.tables` aralığında açık yazı ZAYIF ya da zemin "ölçülmez"; SKILL.md ve README dürüst sınırına "tablo stili"; önce kırmızı test (stil başlıklı kurgu tablo → rapor yok) |
| K-3 | H-3 | ESAS Ş-3 | aynı dalda ayrı commit | Excel gizli-katman UYARI'sı için etiket ve md başlığı türe uygun; `okuma_kapisi` tek kaynak; test |
| K-4 | H-4 | ESAS Ş-4 | aynı dalda ayrı commit | udf-cli oturumuyla `<ol start>` UDF düzeyinde bir kez ölçülüp kaydedilir; ölçülene kadar CHANGELOG/DENETIM cümlesi "UDF-HTML'de" diye sınırlanır |
| K-5 | H-5 | USUL 2 | kayıt; tarihçe düzeltmesi avukat kararı | DENETIM §6 (Görev 2 / Görev 4) ve CHANGELOG'a "taşıma fiilen `47bba4d`'de" notu; istenirse tarihçe düzeltmesi |
| K-6 | H-6 | USUL 1 | **bu commit** | CHANGELOG "Sürümsüz" kaydına Heyet maddesi + STATUS'a 2026-10-16 notu — yapıldı |
| K-7 | H-7 | USUL 3 | kayıt | `.gitignore`'a `.claude/`; README cümlesi |
| K-8 | — | USUL 4 | **bu commit** | heyet dosyaları (`docs/heyet/2026-10-16/**`, CHANGELOG, STATUS) commit'li içerikle bağlantı / metin hijyeni / kaynak hijyeni / b38 / b35 kapılarından geçirilir — ölçüm §4.1 |
| K-9 | §6 | USUL 5, GÜVENLİK 3 | kapsam | commit'siz iş push kapsamına girmez; commit'lenince OA-SUIT-SAYISI (ölçülen toplam 3850), sürüm damgası ve ilan testleri (`test_v0518_mcp_ilan`), `.github/SECURITY.md` cümlesi, tam süit ve heyetin yeniden koşumu (B-23 dersi) |

GÜVENLİK 2 ("tam süit usul ölçümüyle yeşil") USUL §1.2 ile karşılandı: `3800 passed, 12 skipped`.

### 4.1 K-8 ölçümü (bu commit'in dosyaları)

Düzenek: `git worktree add --detach <geçici> HEAD` (`8be918f`, `git status` boş) → bu commit'in dosyaları
(`docs/heyet/2026-10-16/**`, CHANGELOG.md, STATUS.md) geçici ağaca kopyalanıp indeksine alındı (`git add -A`;
b38 `git ls-files` taradığı için) → kapılar koşuldu → geçici worktree `git worktree remove --force` ile
kaldırıldı (`git worktree list`'te yok).

| Kapı (geçici temiz worktree · `py -3.14` · `PYTHONUTF8=1 OA_TEST_UDF_YAZICI=0` · `-p no:cacheprovider`) | Son satır |
|---|---|
| `pytest tests/test_belge_baglantilari.py tests/test_v0518_metin_hijyeni.py tests/test_kaynak_hijyeni.py tests/test_v0514_vitrin.py tests/test_eklenti_vitrini.py tests/test_v0586_surum_kilidi.py -q -rsfE` | `58 passed in 11.91s` — bağlantı kapısı, metin ve kaynak hijyeni, vitrin (b35: toplanan = OA-SUIT-SAYISI 3813; b38: mutlak yol 0), eklenti vitrini, sürüm kilidi |
| Python taraması — `docs/heyet/2026-10-16/**/*.md` (9 dosya) + CHANGELOG/STATUS'un eklenen satırları: Cf / çift yönlü / NBSP karakter · mutlak yerel yol | 0 · 0 |

Not: çalışma kopyasında satır sonu dönüşümü etkin olduğundan git "LF → CRLF" uyarısı verdi; dosyalar indekse LF
olarak girer, depodaki öbür belgelerle aynı (`git ls-files --eol`: i/lf).

## 5. Doğrulanamayanlar (üç raporun birleşimi)

- udf-cli oturumu yok: 11 test görünür gerekçeyle atlandı; UDF bayt invaryantları ve `<ol start>`'ın
  udf-cli/PDF yolu ölçülmedi (H-4).
- `OA_SAHA_REFERANS` tanımsız: OCR saha testi atlandı.
- Kurulu eklenti dalın içeriğiyle kurulmadı; `hook_doktor` kurulu 0.6.0 önbelleğini ölçtü (USUL N-4).
- Ağ yok (yasak): GitHub CI koşusu, PR #6 durumu, depo açıklaması ve etiketleri (B-8), Yargı Pro uç
  noktası sağlık denetimi; "sahipsiz değil" yargısı yalnız "ilan değişmedi" ölçümüne dayanır.
- Excel kapısının gerçek evrakta yanlış alarm oranı: alt ajan raporu tek gerçek `.xls` (temiz)
  bildiriyor; heyet yalnız sentetik düzenek ölçtü (H-2 düzeneği yanlış alarm verdi).
- Ara commit'lerde (özellikle `47bba4d`) tam süit koşulmadı; yalnız bağlantı sayımı yapıldı.
- Alt ajan raporlarındaki alt küme sayıları ("82 yeşil") yeniden koşulmadı; tam süit kapsıyor.
- DENETIM §1'deki "önce" ölçümleri (ruff 54 / 516, 3756 geçti) `origin/main` üzerinde yinelenmedi.
- GÜVENLİK N-1 kod okumasıyla saptandı, deneyle ölçülmedi.
- e-tebligat cümlesinin dayandığı Yargı PRO teyidi yinelenmedi (ağ yok); günlük kaydı tarih taşıyor.

## 6. Commit'lenmemiş iş — karar dışı

Paylaşılan çalışma ağacında BAŞKA oturumun açık işi ("resmî kaynak beyaz listesi / Yargı Pro MCP
ilanının kaldırılması"): izlenen 9 dosya, `173 insertions(+), 49 deletions(-)` —
`.claude-plugin/marketplace.json`, `plugins/ortak-avukat/.claude-plugin/plugin.json` (`mcpServers`
bloğu düşüyor, açıklama ve anahtar sözcükler değişiyor), oa-ingest `SKILL.md`,
`references/gizli-talimat-ifsasi.md`, `scripts/gizli_talimat_ifsa.py`, oa-kontrol
`ictihat_muhakeme_denetim.py`, `kunye_ortak.py`, oa-pipeline `oa_hafiza.py`,
`tests/test_kaynak_url.py`; izlenmeyen 3 dosya: `references/resmi-kaynaklar.md` (69 satır),
`tests/test_kanal_bagimsiz_metin.py` (79), `tests/test_teyit_kanali.py` (291). Üç üye de dokunmadı,
değerlendirmedi; bu karar yalnız commit'li fark üzerinedir. O iş teyit zincirine (m.5), sürüm
damgası dosyalarına ve MCP ilanına (B-23) dokunduğu için commit'lendikten sonra ayrı heyet koşumu
ister (K-9).

## 7. Avukata sunulan karar

Heyet karar vermez. Soru: **`denetim/fable-2026-10-15` dalı push edilsin mi?**

- **Heyet önerisi:** ŞARTLI PUSH. Push'tan önce K-1 ve K-2 (Excel kapısı: ızgara tavanı, tablo
  stili zemini; her ikisi önce kırmızı test, ardından tam süit ve heyetin yeniden koşumu); K-3…K-7
  aynı dalda ayrı commit ya da kayıt düzeltmesi.
- **Asgari yol (GÜVENLİK üyesinin alternatifi):** K-1 açık kalem olarak STATUS/YOL-HARITASI'na
  yazılırsa güvenlik şartı karşılanır; ESAS üyesinin K-1 ve K-2 "push'tan önce" şartı ise yalnız
  kodla kapanır.
- **Dalın hiçbir parçası** commit'siz işi kapsamaz; o iş için push kararı ayrıca verilir (K-9).

Bu belge ve üç üye raporu dala commit'lendi; push yapılmadı.

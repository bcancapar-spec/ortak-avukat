# Şart kapanışı doğrulaması — GÜVENLİK ve GİZLİLİK · 2026-10-17 · 3. koşum sonrası (kısa koşum)

**Üye:** oa-heyet-guvenlik · **Dal:** `denetim/fable-2026-10-15` · **Doğrulanan fark:** `c94e982..ef03fd8` (iki commit:
`d6e5550` tur 4 — kod + 7 test + kayıtlar; `ef03fd8` KARAR-3 + öneri raporu + kayıt satırları, kod yok) · **Dayanak:**
[3. koşum raporum](03-guvenlik.md) (ŞARTLI PUSH 0·2·5) ve [KARAR-3](KARAR.md) §2, §4.1, §7, §8. Üç soru: U-1/U-2 tarif
edildiği gibi ve önce kırmızı testle kapandı mı; fark BLOKLAYICI getiriyor mu; KARAR-3 raporumu sadakatle taşıyor mu.

## 1. Düzenek ve komutlar

Geçici worktree depo kökü dışında, varsayılan ayarla: `git worktree add --detach <yol> ef03fd8` → HEAD `ef03fd8`,
`git status --short` 0 satır. `py -3.14` (3.14.8), `PYTHONUTF8=1 OA_TEST_UDF_YAZICI=0`, `-p no:cacheprovider`; deney
betikleri ve sentetik veri depo dışı geçici dizinde (`-I -X utf8`); openpyxl 3.1.5. Ağ yok. Paylaşılan ağaca yazılan tek
dosya bu rapor. Mutasyon deneyleri yalnız geçici kopyada, her adımdan sonra geri alındı (kirli dosya 0).

| # | Komut / düzenek | Son satır |
|---|---|---|
| 1 | `git diff --stat c94e982..ef03fd8` · `..d6e5550` · `d6e5550..ef03fd8` | 22 dosya +1792/−19 · 20 dosya +1289/−18 · 6 dosya +504/−2, `.py` yok |
| 2 | aynı fark: `hooks/`, `.github/`, `requirements.txt`, `pyproject.toml`, iki `.claude-plugin/` | boş (değişmedi) |
| 3 | eklenen `.py` satırlarında `import / requests / urllib.request / socket / http.client / subprocess / eval / exec / pickle / os.system / @latest / npx / open(` | tek eşleşme: fonksiyon içi `import urllib.parse` (ayrıştırıcı, ağ çağrısı değil) |
| 4 | `pytest tests/test_v0514_vitrin.py -q -k b38` · hijyen iki dosya · `ruff check .` | `3 passed, 16 deselected` · `7 passed` · `All checks passed!` |
| 5 | `pytest test_teyit_kanali test_v0519_excel_gizli_katman test_kaynak_url test_gizlilik` · 7 yeni test (`-k`) · `test_belge_baglantilari` | `101 passed in 5.47s` · `7 passed, 78 deselected` · `2 passed` |
| 6 | Sır taraması: `-U0` eklenen 1792 satır (KARAR-3, öneri raporu, üye/ajan raporları dahil) | §4 |
| 7 | U-1 deneyi: 7 XML yazımı × 5.000 hücre; parça sınırı 19 boyut; dilbilgisi; gerçek tavan 1.000.001 hücre | §2 |
| 8 | U-2 deneyi: 22 adres vakası fonksiyon düzeyinde + 10 vaka CLI uçtan uca (`init` ile sentetik kök) | §3 |
| 9 | Mutasyon: (A) iki modül `c94e982` hâli + yeni testler · (B1) desen eski `rb"<c "` · (B2) `_kaynak_url_layer0_tara` → `return None` | `5 failed, 2 passed` · `4 failed` · `1 failed, 2 passed` |
| 10 | Bu rapor temiz kopyada: bağlantı kapısı + hijyen + b38 + sır deseni sayımı | dönüş mesajında |

## 2. U-1 kapanışı — nesne sayacı (ölçüm)

`belge_guvenlik.py:2380-2381` `_XML_HUCRE_RE` = `rb"<(?:[A-Za-z_][\w.-]*:)?c(?=[\s/>])"`, `_XML_SATIR_RE` aynı yapıyla `row`;
`_xml_nesne_say` (`:2384-2399`) kuyruk 128 bayt — 3. koşumda önerdiğim desen birebir. Sentetik kitap 100 × 50 = 5.000 hücre:

| Yazım | Sayaç (hücre, satır) | openpyxl | `AZAMI_TABLO_HUCRE`=1000 |
|---|---|---|---|
| düzgün `<c r=…>` · öznitelliksiz `<c>` · satır sonlu `<c\nr=…>` · sekmeli `<c\tr=…>` · önekli `<x:c …>` · uzun önek `<abc.d-e_1:c …>` | altısında (5000, 100) | 5000 / 100 | altısında `_TabloOlculemedi` |
| ASCII dışı önek `<ş:c …>` (`xmlns:ş=` ana ad alanı) | (0, 0) | 5000 / 100 | **KAPI GEÇTİ, kitap yüklendi** → K-27 |

Parça sınırı: aynı XML 19 parça boyutunda (1 … 65536, 127/128/129 dahil) referansla birebir, sapma 0 — bölünen etiket
doğru sayılıyor. Dilbilgisi: `<cols>`, `<col …>`, `<cellXfs …>`, `<cx/>`, `<rows/>`, `<rowBreaks …>`, `<colBreaks/>`,
`<cfRule/>`, `<color …>`, `<controls/>`, `<cellWatches/>` sayılmıyor; `<c r>`, `<c/>`, `<c>`, `<c:c/>`, `<x14:c/>`, `<c\n/>`,
`<c\r\n r>` ve `<row r>`, `<row/>` sayılıyor → (7, 2) beklenen (7, 2), dört parça boyutunda aynı. Yanlış pozitifle meşru
dosyanın erken DENETLENEMEZ olması yok. Gerçek tavan: 1.000.001 öznitelliksiz hücre (28 KB dosya, 14 MB XML) → `_TabloOlculemedi`
0,78 s / tepe 5 MB, kitap yüklenmedi. Kilit: (A) eski kodda dört Excel testi kırmızı; (B1) yalnız desen eskiye çevrilince
`4 failed` (bölüm (8) kilit). Sonuç: U-1 tarif edildiği gibi, önce kırmızı testle kapandı; artık kalan ASCII dışı önek K-27.

## 3. U-2 kapanışı — `--kaynak-url` Layer 0 (ölçüm)

`oa_hafiza.py:832-853` `_tckn_saglama_gecer_mi` (algoritma doğru: tek/çift hane toplamları, 10. ve 11. hane; ilk hane 0
değil) ve `_kaynak_url_layer0_tara` (yol + sorgu + parça, `unquote_plus`, sağlama geçmeyen 11 hane `#` ile örtülür, sonra
`_layer0_sorgu_tara`); çağrı `cmd_teyit` `:1287-1292`, biçim denetiminden hemen sonra, döküm yazımından ve beyaz liste
kapısından ÖNCE, araç sınıfından bağımsız; `sys.exit` → çıkış 1. CLI uçtan uca (sentetik kök, kurgu künye, sentetik sağlama
geçen numara = `tests/test_gizlilik.py` sabiti, origin/main'de 3 kez var):

| Vaka | Çıkış | `RET (Layer 0)` | muhakeme kaydı | numara `_oa` altında |
|---|---|---|---|---|
| B GETİR, sorgu dizesinde numara + kurgu ad · C `WebSearch`, aynı adres · yüzde-kodlu rakamlar · parça `#…` · yalnız kurgu ad | 1 | evet | yok | hayır |
| D B + `--sorgu-onayli` (bilinçli geçiş) · E sağlama geçmeyen 11 hane (karar kimliği) · temiz adres | 0 | — | var | (bilinçli / meşru) |
| F 0 ile başlayan 11 haneli yerli cep biçimi · G userinfo'da sağlama geçen numara | **0** | **hayır** | **var** | **evet** → K-28 |

Fonksiyon düzeyi (22 vaka): `+` ayraçlı sözcükler + numara, yol segmentinde numara, IBAN, e-posta, plaka, 10 haneli / `+90`'lı /
boşluklu telefon, kurgu mahkeme adı + esas no, 2 sözcüklü ve büyük harfli kurgu ad → bulgu; iki temiz adres → None. Kilit:
(A) eski kodda `test_kaynak_url_sorgu_dizesinde_tckn_layer0_ret` kırmızı; (B2) fonksiyon `None` dönünce `1 failed, 2 passed`
(bölüm (f) kilit; eşlik eden iki test regresyon bekçisidir, eski kodda da yeşildir). İkinci kilit açık: `ictihat_muhakeme_denetim.py`
[G7] `resmi_kaynak_denetimi` (`:929-943`) yalnız beyaz liste, dosyada Layer 0 anması 0 — KARAR-3 K-17 dürüst. Sonuç: U-2 tarif
edildiği gibi (yol + sorgu + parça → Layer 0, bilinçli geçiş aynı bayrak), önce kırmızı testle kapandı; sağlama süzgecinin yan
etkisi ve `netloc` K-28.

## 4. Fark taraması (sır, tedarik zinciri, kanca)

Eklenen 1792 satırda: ham görünmez / çift yönlü 0 · IBAN 0 · telefon 0 · mutlak yerel yol 0 · esas-karar deseni 0 · kişi adı 0
(`Av.` 0; ad-soyad deseninin 24 eşleşmesi "Birleştirmeden ÖNCE", "İki UYARI" gibi büyük harfli sözcük çiftleri) · 11 hane 3
(CI koşu kimliği; iki sentetik test sabiti — sağlama geçeni origin/main'de zaten var) · e-posta 1 (`@pytest.mark` yanlış
pozitif) · token/parola 7 (hepsi raporlardaki tür adları). Kanca, CI, bağımlılık, sürüm ve manifest dosyaları değişmedi; yeni
uç nokta / alan adı 0 (adresler beyaz listedeki portallar ve sentetik yollar); `subprocess` / ağ 0. Fail-open 0: iki yeni kapı da
reddederek durur. `ef03fd8` kod içermez. **BLOKLAYICI 0.**

## 5. KARAR-3 sadakati

§1 satırım: ŞARTLI PUSH · 0 · 2 · 5 ve kapı son satırları (2706 satır sır 0, b38 3, hijyen 7, ruff, 356, 133, 41 vaka, 4 yazım ×
5.000 + 100 k / 300 k, Layer 0 deneyi, kanca/CI/bağımlılık değişmedi) raporumla birebir. §2: U-1 ve U-2 "birleştirmeden önce
— kapatıldı, önce kırmızı" doğru (ölçüm §2, §3); U-1 için sunduğum "ya da STATUS açık kalemi" seçeneğinde kapatma tercih
edilmiş (benim tercihim de buydu); şart 3 (tam süit) §4.1'de USUL ölçümü. N-1 → K-20, N-2 → K-26, N-3 → K-22, N-4 → §7.1/8,
N-5 → K-25; U-2 ikinci kilit K-17 — hepsi doğru ve eksiksiz. Tek sapma NOT-2.

## 6. Yeni bulgular — açık kalem (birleştirme şartı değil)

**K-27 · UYARI · `belge_guvenlik.py:2380-2381` — önek sınıfı ASCII (`[A-Za-z_][\w.-]*`); XML 1.0 ad başlangıcı ASCII dışı harf
olabilir.** `<ş:c …>` sayaçta 0 (satır da 0), openpyxl 5.000 hücre okur, tavan 1000'de kapı geçti; 100.000 hücre 585 KB dosyada
1,24 s / tepe 37 MB (3. koşum ölçeğiyle aynı sınıf; sessiz geçiş yok, sır sızmaz — U-1 ile aynı etki). 3. koşumdaki önerim de bu
sınıfı kapsamıyordu. Onarım (ölçüldü): `rb"<(?:[A-Za-z_\x80-\xff][\w.\-\x80-\xff]*:)?c(?=[\s/>])"` 100.000 sayar; `row` aynı.
Önce kırmızı: bölüm (8) parametrelerine ASCII dışı önek vakası.

**K-28 · UYARI · `oa_hafiza.py:843-853` — (a) sağlama maskesi 0 ile başlayan 11 haneli yerli cep biçimini (0 + 10 hane; sağlama
hiç geçmez) `#` ile örtüyor, `_TELEFON_RE` ham metinde eşleşirken maskeli metinde eşleşmiyor (ölçüldü): adreste bu biçim →
çıkış 0, muhakeme kaydına ve `_oa` altına yazıldı (deney F); aynı değer `--sorgu`'da RET. Kod yorumu `:1284-1285` "telefon …
aynen taranır" diyor — bu biçim için doğru değil. (b) `netloc` taranmıyor: userinfo'daki sağlama geçen numara → çıkış 0,
`**KAYNAK-URL:**` satırına yazıldı (deney G); `resmi_kaynak_mi` `hostname` ile userinfo'yu ayıklar, beyaz liste geçer.**
Gevşeme değil (`c94e982`'de adres hiç taranmıyordu; `--sorgu` yolu değişmedi) — yeni yüzeyin iki dar boşluğu. Onarım (ölçüldü,
dört satır): telefon desenini maskeden ÖNCE ham çözülmüş metinde ara; `p.netloc`'u taranan metne ekle — beş vakada beklenen
sonuç (telefon → RET, userinfo → RET, karar kimliği ve iki temiz adres → geçer). Önce kırmızı: bölüm (f)'ye iki vaka. K-17 ile
aynı commit.

**NOT-1 · parite sınırları (önceden var, bu onarıma özgü değil).** `+`/boşlukla bölünmüş numara, `ad=…&soyad=…` ayrı alanlar,
küçük harfli ad, `/` ayraçlı yol segmentleri hem adreste hem `--sorgu`'da None (ölçüldü) — `_layer0_sorgu_tara` tasarım sınırı
(`:700-705` yorumu). Öneri: adres çözümünde `/`, `=`, `&` → boşluk (K-28 ile).

**NOT-2 · KARAR-3 §4.1 "önce kırmızı (4 + 3)".** Ölçüm: eski kodda 4 + 1 kırmızı (`5 failed, 2 passed`); `--sorgu-onayli` ve karar
kimliği testleri eski kodda da yeşil (regresyon bekçisi). §2'deki cümle doğru; §4.1'deki sayı fazla. Kayıt.

## 7. Doğrulanamayanlar

Tam süit koşulmadı (USUL; KARAR-3 §4.1 `3894 passed, 12 skipped` beyan). Canlı `WebFetch`/`WebSearch` akışı ve CI koşusu
görülmedi (ağ yok). ASCII dışı önek deneyi bu makinedeki openpyxl 3.1.5 ile; ayrıştırıcı arka ucu (lxml / expat) ölçülmedi —
XML 1.0 adlandırma kuralı gereği her uyumlu ayrıştırıcı kabul eder. K-27 ölçeği 100.000 hücreye kadar; üstü 3. koşumdan
çıkarım. KARAR-3'ün USUL/ESAS satırları doğrulanmadı — yalnız kendi satırım. Geçici worktree iş bitiminde
`git worktree remove --force` ile kaldırıldı; `git worktree list`'te yokluğu dönüş mesajında.

DOĞRULAMA: ŞART KAPANDI · BLOKLAYICI 0 · yeni UYARI 2 · NOT 2 · BİRLEŞTİRME ÖNERİSİ: PUSH

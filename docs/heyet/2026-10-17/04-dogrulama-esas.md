# Şart kapanışı doğrulaması — ESAS üyesi — 2026-10-17 (fark `c94e982..ef03fd8`)

**Dal** `denetim/fable-2026-10-15` · **HEAD** `ef03fd8` · **Fark** iki commit: `d6e5550` (tur 4 — iki motor, 7 test, dürüst sınır cümleleri,
kayıtlar) ve `ef03fd8` (KARAR-3, öneri raporu, kayıt satırları; kod yok) — 22 dosya, +1792/−19. Üçüncü koşum raporum: [02-esas.md](02-esas.md)
(HEAD `c94e982`). Yalnız üç soru: Ş-1/Ş-2 kapandı mı; fark koruma gevşetiyor mu; KARAR-3 sadık mı. Ölçü tek: müvekkil hangi kayıptan korunur.
m.7: kişi, müvekkil, dosya numarası, mutlak yol yok; sentetik sayılar ve kurgu adlar metne alınmadı. Ağ yok. KARAR-3 değiştirilmedi (§8 orkestranın).

## 1. Düzenek

- Geçici worktree `heyet4-tmp-esas` (depo kökü dışında, `--detach ef03fd8`, varsayılan ayar): `git status --short` 0 satır;
  `py -3.14` (3.14.8); `PYTHONUTF8=1 OA_TEST_UDF_YAZICI=0`; `-p no:cacheprovider`; bitince `git worktree remove --force`.
- Küme A — teyit kanalı (`test_teyit_kanali`, `test_kaynak_url`, `test_oa_hafiza_teyit_damga`, `test_oa_hafiza_arac_guvenlik`,
  `test_ictihat_muhakeme_denetim`, `test_v0518_mcp_ilan`, `test_gizlilik`; `-n auto -m "not perf"`): `182 passed in 5.34s`.
- Küme B — Excel / vitrin / bağlantı / hijyen (`test_v0519_excel_gizli_katman`, `test_v0518_belge_guvenlik`, `test_v0514_vitrin`
  b35/b37/b38, `test_eklenti_vitrini`, `test_belge_baglantilari`, `test_v0518_metin_hijyeni`, `test_kaynak_hijyeni`,
  `test_kanal_bagimsiz_metin`): `198 passed in 12.75s` → OA-SUIT-SAYISI 3907 = toplanan (b35); yeni motorlar testli (b37 borcu yok).
- İki deney depo dışında, oturum çalışma alanında, `-I` ile, yalnız kurgu veriyle; kurgu kökler silindi. Hukuki dayanak: farkta `*.json` ve
  playbook yok; `references/` altında yalnız `resmi-kaynaklar.md` (kanal belgesi — madde, süre, tarife kalemi yok) → yeni "TEYİT BEKLİYOR" yok.

## 2. Ş-1 / Ş-2 kapanışı — cümle cümle

| Yer | Cümle (öz) | Eksiği kapatıyor mu | Fazla / yanlış iddia |
|---|---|---|---|
| `oa-ictihat/SKILL.md:22` sonu "*Dürüst sınır:*" | `WebFetch` İŞLENMİŞ metin döndürür; tamlık araca ve portala bağlı; `--dokum-sinifi tam-metin` avukat beyanı, kapı ölçmez; canlı akış sahada sınanmadı (E-1) | E-1 ✓ — dört unsur: işlenmiş, verbatim garantisi yok, beyan, saha ölçümü yok | Paragraf başındaki "`WebFetch` tam metin (GETİR sınıfı)" sınıf adıdır; dürüst sınır aynı paragrafta → kabul |
| `references/resmi-kaynaklar.md:18-21` | aynı E-1 cümlesi + "(`teyit` `--sorgu` ve `--kaynak-url` için mekanik; web araçlarının kendi çağrıları için kural, mekanik kapı değil — E-2, açık kalem)" | E-1 ✓; E-2'nin özü ✓ (web çağrısında mekanik kapı yok) | **Kalan ima:** cümle "sorgu çıkmadan önce Layer 0 süzgeci … çalışır" diye başlıyor ve "mekanik" `teyit`'e bağlanıyor; `teyit` kayıt anında, çağrıdan SONRA koşar — çıkışı geri almaz, kaydı ve dilekçeye geçecek bağlantıyı engeller → NOT-2 |
| `README.md:1403-1407` Excel maddesi | 128 MB açılmış arşiv; 1 M hücre / 500 k satır tanımı; "(tahmin: ~0,4 GB / ~0,3 GB)"; "meşru dev dökümler de takılabilir" | N-7 ✓ | Sayılar "tahmin" etiketli; dayanak GÜV ölçümü 0,41 KB/hücre (`03-guvenlik.md:140`) ve `belge_guvenlik.py:168` ~0,6 KB/satır → dürüst |
| `README.md:1408-1412` yeni "Hibrit teyit kanalı" maddesi | adres + diske inen metin kanıt, kelimesi kelimesine tamlık ölçülmez; E-1 cümlesi; Layer 0 web araçları için kural, mekanik kapı `teyit` taraması; açık kalem: kanca | E-1 ✓, E-2 ✓ | `:1409` parantezi "(sayfa düzeni, kesilmiş uzun metin, portalın bot sınırı)" ölçülmemiş olguları liste gibi okutuyor → "olabilir" kipi (NOT-2) |
| Ş-2: `STATUS.md:3`, `:16-17`; `CHANGELOG.md:316-318`; `docs/DENETIM-2026-10-15.md:207-208` | "2026-10-16'da avukat kararıyla push edildi (PR #9)"; birleştirme avukatın talimatıyla, doğrulama + CI sonrası | N-3 ✓ | `STATUS.md:6-7` 2026-10-15 bloğu hâlâ "push edilmedi" — tarihli kayıt, `:16`'daki "o sırada" niteleyicisi yok → NOT-3 |

**Sonuç: Ş-1 ve Ş-2 kapandı.** Kalanlar kelime düzeyindedir (NOT-2, NOT-3); birleştirme şartı değildir.

## 3. Yeni kodun koruma etkisi

### 3.1 `oa_hafiza.py` — `_tckn_saglama_gecer_mi` (`:832`), `_kaynak_url_layer0_tara` (`:843-853`), kapı (`:1287-1292`)

Deney: fonksiyon düzeyi (18 adres) + CLI (`teyit --arac ictihat_getir` + damga + döküm, kurgu kök). Sonuçlar:
- Sağlamalı sentetik TCKN sorgu dizesinde ve `#` parçasında → `RET (Layer 0)`, çıkış ≠ 0, muhakeme kaydı yok, sayı `_oa` altında
  yok ✓. Sağlama geçmeyen 11 hane (karar kimliği) → kabul ✓ (yanlış engel yok).
- `_layer0_sorgu_tara`'ya ulaşanlar (hepsi RET ✓): IBAN (yolda) · e-posta · telefon 10 hane / ayraçlı kodlu / +90 kodlu · kurgu iki
  sözcüklü ad-soyad (`+` ve `%C4%B1` kodlu; bağlamlı ve bağlamsız) · ilk derece mahkeme adı + esas no · plaka. Salt esas no kabul —
  bilinen sınır, `--sorgu` ile aynı (değişmedi).
- **Delik 1 — 0 ile başlayan bitişik 11 haneli telefon:** `_TCKN_RE` eşleşmesi sağlama geçmeyince `#`×11 ile maskeleniyor (`:852`),
  sonra `_TELEFON_RE` maskeyi göremiyor → adres KABUL, CLI çıkış 0, `**KAYNAK-URL:**` satırı muhakemeye yazıldı; aynı sayı
  `--sorgu`'da RET (TCKN kuralı). Sağlama inceltmesinin yan etkisi; kod yorumu `:1286` "telefon … aynen taranır" bu biçim için yanlış.
- **Delik 2 — kullanıcı-bilgisi:** yalnız yol + sorgu + parça taranıyor (`:851`); `kullanıcı@alan` biçiminde sentetik TCKN ya da ad
  `netloc`'ta → tarama None, `resmi_kaynak_mi` True (`hostname` resmî), CLI çıkış 0, adres muhakemeye yazıldı. Resmî portal
  adresinde kullanıcı-bilgisi meşru değildir → RET olmalı.
- `--sorgu-onayli`: geçiş çalışıyor; `_oa` altında "onayl" izi 0 dosya; tek bayrak iki yüzeyi (`:1251` sorgu, `:1287` adres) birden
  açıyor. m.9/m.10: bilinçli geçiş kütükte görünmüyor, [G7] dayanak yaparken ayırt edemez. `--sorgu` için önceden de böyleydi;
  yeni yüzey aynı eksiği devraldı.
- Fail-open yol yok: `urlsplit` ValueError → RET (`:849-850`); bulgu → `sys.exit`, kayıt ve döküm yazımından önce; GETİR / mevzuat
  sınıfında adres zorunlu (`:1298-1300`); kapı araç sınıfından bağımsız (ARAMA + adres de taranır). Çift kodlanmış (`%25xx`) desen
  çözülmez — model-tarafı kaçış, `--sorgu`'daki sınırla eşdeğer.
- Müvekkile etkisi: iki delik dar (portal arama adresinde telefon ya da kullanıcı-bilgisi olağan değil); kapı çağrıdan sonra çalışır — dış
  çıkışı değil, kaydı ve dilekçeye geçen bağlantıyı engeller. `main`'de adres taraması hiç yok → gerileme yok, yeni kayıp ekseni yok → **UYARI (K-27)**.

### 3.2 `belge_guvenlik.py` — `_XML_HUCRE_RE` / `_XML_SATIR_RE` (`:2380-2381`), `_xml_nesne_say` (`:2384-2399`)

- Desen `<` + isteğe bağlı önek + `c`/`row` + (boşluk | `/` | `>`). Kurgu XML: standart (2,1), öznitelliksiz / `<c/>` / satır sonlu
  (3,1), önekli `x:` ve `ns-1.a:` (3,1) — hepsi doğru. Yanıltıcı etiketler `<cols>`, `<col>`, `<cfRule>`, `<conditionalFormatting>`,
  `<c:chart>`, `<c:v>`, `<cellWatch>`, `<customSheetView>`, `<rowBreaks>`, `<r>`, `<rPr>`, kapanış etiketleri → (0,0): `<c` ile
  başlayan başka etiket sayılmıyor. Yorum / CDATA içindeki `<c>` sayılır → fazla sayım, ihtiyatlı yön.
- Parça sınırı: 1.800 hücre / 3 satırlık gövde 14 parça boyunda (1 … 4096) aynı sonuç; 128 baytlık kuyruk çift sayım üretmedi.
- Meşru dev döküm: standart yazımda sayım eskisiyle aynı, egzotik yazımda daha çok → DENETLENEMEZ daha geç değil, en az eskisi
  kadar erken; tavanlar `:165`/`:168` değişmedi; aşım `_TabloOlculemedi` sebepli (`:2524-2529`), kitap yüklenmez; README tavanı
  yazıyor (N-7 kapandı). Fail-closed korunuyor (m.1, m.11); 4 yeni test (`test_v0519_excel_gizli_katman.py:929-977`) yeşil.

## 4. KARAR-3 sadakati

- H3-3 … H3-7 ↔ E-1 … E-5: kanıt yerleri, etki ve onarım cümleleri raporumla örtüşüyor; H3-5 GÜV N-1'i, H3-7 GÜV N-3 ve K-16'yı
  doğru ekliyor. K-18 … K-23 ↔ Ş-3 … Ş-8 birebir (K-21 N-12'yi, K-22 GÜV N-3'ü içerir). NOT'lar: N-1, N-2, N-4 … N-12 §3'te;
  N-3 = H3-8 (Ş-2) → 12/12 taşınmış. §7.1: anayasa MCP ifadeleri (1), `hudoc.exec.coe.int` / ABAD (2), `SURUM` (3), emek etiketi
  (4), `oa-kaynak` (5), sürüm numarası (6) — listem eksiksiz. Sayılar: UYARI 2+5+2 = 9, NOT 8+12+5 = 25, test +7 (3+4) → 3907 ✓.
- "Kapandı" denip tam kapanmayan: **H3-2 (GÜV U-2) "Kapatıldı"** → ölçümümde kısmen: §3.1 iki delik + izsiz geçiş (K-27, K-28). GÜV'ün
  istediği yol/sorgu/parça taraması ve kırmızı test var; GÜV vaka C (ARAMA sınıfı + aynı adres) kodda kapsanıyor, testi yok. H3-1, H3-3
  (metin), H3-8 ve N-7 kapanışları ölçümle doğru. H3-4 "belge cümlesi düzeltildi" → özü doğru, zamanlama iması kaldı (NOT-2).
- N-12 orkestra ölçümü doğru: `motor_koprusu.py:83` "model araç çantasını `_oa/araclar/`a DÜZ kopyalar"; üç pipeline scriptinde
  `shutil.copy*` 0; bayt-özdeşlik `pipeline_kayit.py:5799` `_bayat_arac_uyarisi` (atıf `:5800` docstring içi — doğru);
  `oa_hafiza.py:1076-1080` üç konum, `:1308-1311` yoksa RET (fail-closed).

## 5. Öneri raporunun sınırları ve m.7 — [hukuki-yontem-onerisi.md](ajan-raporlari/hukuki-yontem-onerisi.md)

- Orkestra notu: madde numaraları hafızadan ve teyitsiz (m.4, m.5); ürüne, playbook'a, kurala girmez; karar avukatın (m.9); her
  kalemde "Karar" ve "Teyit" etiketi; §Sınırlar teyit kaydı taşımayan hükümleri sayıyor → üç madde için yeterli. Hukuki içerik
  yargılanmadı (ağ yok; teyit avukat / oa-ictihat).
- m.7 taraması: kişi adı 0 (yalnız "Av.K." kanun kısaltması), 11 haneli sayı 0, esas-no kalıbı 0, mutlak yol 0, büyük harfli ad
  çifti 0; hijyen kapısı yeşil (küme B).
- Depoda durma riski: dosya `docs/heyet/` altında, Skill aracı yüklemez. Ancak raporun kendi yöntemi depo taramasıdır ("Ölçüm: …
  için 0 eşleşme", "Repoda … diye geçer"): gelecekte bir model `HMK m.61` gibi bir taramada bu dosyadan isabet alıp "repoda geçer"
  sayabilir. Başlığa tek cümle (NOT-4): "> Depo taramasında bu dosyadan çıkan isabet dayanak değildir: buradaki madde numaraları
  ve hüküm özetleri teyitsiz adaydır; dayanak yalnız SKILL / references / kural dosyalarındaki teyit kayıtlarıdır (anayasa m.4, m.5)."

## 6. Yeni bulgular (açık kalem; birleştirme şartı değil)

- **K-27 · UYARI · `oa_hafiza.py:843-853`, `:1287-1292`** — §3.1 delik 1 ve 2; sır ekseni (dar). Onarım, önce kırmızı test:
  (a) desenler maskesiz metinde koşar — TCKN dalı sağlamalı (`any(_tckn_saglama_gecer_mi(m) …)`), diğer desenler ham `acik`
  üzerinde; (b) `p.username` ya da `p.password` doluysa RET; (c) kod yorumu `:1286` ve KARAR-3 H3-2 "kısmen" diye düzeltilir.
  Testler: 0 ile başlayan 11 haneli bitişik telefon adreste RET; kullanıcı-bilgili adres RET; ARAMA sınıfı + kirli adres RET.
- **K-28 · NOT · `oa_hafiza.py:1251`, `:1287`, `:2512`** — `--sorgu-onayli` geçişi kütükte ve muhakeme kaydında izsiz; tek bayrak iki
  yüzeyi açıyor. Onarım: kayıt satırına `[LAYER0-ONAYLI GEÇİŞ: <desen>; yüzey: sorgu|adres]`; [G7] bu kaydı dayanak yaparken
  görünür UYARI; isteğe bağlı ayrı bayrak `--kaynak-url-onayli`.
- **NOT-2 · `resmi-kaynaklar.md:18-21`, `README.md:1409`** — zamanlama: "model sorguyu göndermeden önce Layer 0 süzgecini uygular
  (kural); mekanik tarama `teyit`'te kayıt anındadır — çıkışı geri almaz, kaydı ve dilekçeye geçecek bağlantıyı engeller; araç
  çağrısını saran kanca K-19". README parantezi → "(… olabilir)".
- **NOT-3 · `STATUS.md:6-7`** — 2026-10-15 bloğunda "push edilmedi" → "o sırada push edilmemişti (2026-10-16 PR #9)".
- **NOT-4 · öneri raporu başlığı** — §5 cümlesi. **NOT-5 · KARAR-3 §2 ve §3 H3-2** — "Kapatıldı" → "kısmen; K-27, K-28"; §8'e bu rapor.

## 7. Doğrulanamayanlar

- `WebFetch`'in resmî portallardan fiilen ne döndürdüğü; Layer 0'ın web araçlarına uygulanması (ağ yok). GÜV U-1 300 k hücre ölçümü
  ve bellek tahminleri (0,4 / 0,3 GB) yinelenmedi; gerçek dev döküm yok. Tam süit, CI 18/18, zamanlama kanaryası — usul üyesi.
- Önceden var olan yedi "TEYİT BEKLİYOR" kalemi değişmedi (02-esas §4). Öneri raporundaki hukuki içerik ve madde atıfları — resmî
  teyit avukat / oa-ictihat.

Raporun kendi kapıları: geçici kopyada `test_belge_baglantilari` + `test_v0518_metin_hijyeni`; yol, 11 hane, esas-no, Cf / NBSP / çift yönlü
karakter desenleri elle — sonuç dönüş mesajında. Paylaşılan ağaçta yalnız bu dosya yazıldı; git yazma komutu yok; ağ yok. Birleştirmeden
önce şart kalmadı; K-27 aynı dalda ayrı commit (birleştirme sonrası ilk iş yeter).

DOĞRULAMA: ŞART KAPANDI · BLOKLAYICI 0 · yeni UYARI 1 · NOT 5 · BİRLEŞTİRME ÖNERİSİ: ŞARTLI PUSH

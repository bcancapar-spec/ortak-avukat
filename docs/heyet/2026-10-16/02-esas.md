# Heyet raporu — ESAS üyesi (hukuki yöntem, müvekkil menfaati) — 2026-10-16

**Dal:** `denetim/fable-2026-10-15` · **HEAD:** `8be918f` · **Kapsam:** `origin/main..HEAD`
(14 commit, 90 dosya, +3134/−675) · **Ölçüm ortamı:** geçici worktree `heyet-tmp-esas`
(detached, HEAD `8be918f`; iş bitince kaldırıldı) · yorumlayıcı `py -3.14` (Python 3.14.8),
`PYTHONUTF8=1 OA_TEST_UDF_YAZICI=0`, pytest `-p no:cacheprovider`.

Ölçü tektir: bu dal sahaya çıkarsa müvekkil hangi kayıptan korunur, hangi kayba açılır
(evrak · süre · doğrulanmamış bilgi · sır · karşı tarafın gizli tuzağı). Alt ajan raporları
BEYAN sayıldı; her iddia diff'te ve ağaçta ölçüldü. Anayasa m.7 gereği kişi, müvekkil, dosya
numarası ve mutlak yerel yol yazılmamıştır. Başarı olasılığı sayıyla verilmez.

---

## 1. Kapsam — commit başına: parça · korunan kayıp ekseni · anayasa maddesi

| Commit | Parça | Müvekkili hangi kayıptan korur | Madde |
|---|---|---|---|
| `52de60f` | kök README (avukatın bekleyen düzeltmeleri: Excel okuyucuları, Mağaza kısayolu, prompt satırları) | Doğrulanmamış bilgi: e-tebligatta iki tarihin birlikte hesaplandığı prompt açıklaması; kod yok | m.2, m.6 (anlatım) |
| `d9d358a` | oa-dilekce `md_udf_html.py` (`<ol start>`) | Mahkemeye yanlış bilgi: talep bendinin kaynak numarası korunur (9. bent "1." basılmaz); 1'den başlayan liste bayt-özdeş | m.4 (olgu korunur), m.6 |
| `7fcbb22` | depo: `ruff.toml`, CI `lint`, `udf_md.py` `_CF_RE` kaçışa, `oa_hafiza.py` yinelenen küme öğesi, test temizliği | Gizli tuzak: eklentinin kendi kaynağında ham çift-yönlü/görünmez karakter (gözle okunandan farklı kod) yasağı; `_CF_RE` deseni özdeş (`test_cf_regexi_unicodedata_ile_birebir`) | m.11'in kaynak koda yansıması |
| `30495ab` | oa-usta `aile_dogrula.py` + `pyproject.toml` 0.1.0 → 0.6.0 | Doğrulanmamış bilgi: sürüm damgası bayatlığı görünür (UYARI sınıfı) | m.0 (bayat araç), m.8 |
| `47bba4d` | `test_v0518_metin_hijyeni` istisnasız | Aynı eksen; istisna kalktı | m.11 |
| `45a6d2e` | kök dizin → `docs/arsiv/`, `tests/test_belge_baglantilari.py` | "Her iddia kanıtlı": kırık bağlantı kapısı; kod yok | m.5 (ruhu) |
| `cf425d9` | kök README katmanlı düzen; "Hâkim ve savcı gözüyle" | Vitrin dürüstlüğü; m.4/m.5/m.9/m.10/m.11 anlatımı; kod yok | m.8 |
| `200dda5` | `.github/SECURITY.md`, PR şablonu | Sır: müvekkil verisi içeren bulgu herkese açık issue'ya yazılmaz | m.7, m.10 |
| `99ef95f` | CHANGELOG sürümsüz kayıt, STATUS, YOL-HARITASI, SOZLUK, DENETIM belgesi | Kayıt; kod yok | m.8 |
| `8a1c882` | eklenti README katmanlı + `tests/test_eklenti_vitrini.py` | Vitrin sayıları ölçümle (B-35 dersi) | m.8 |
| `934e212` | oa-ingest `belge_guvenlik.py` (+553): Excel gizli katmanı ölçülür | Gizli tuzak: gizli satır/sütun/sayfa, zeminle aynı renk, `;;;`, minik punto yerinde damgalanır; süre: damgalı tarih süreye girmez | m.11, m.2, m.6 |
| `08aef92` | kök README katalog sayıları, CHANGELOG/DENETIM/STATUS | Vitrin dürüstlüğü | m.8 |
| `c5f739f` | `docs/heyet/` tanımlar + protokol | Süreç: heyet karar vermez, karar materyali üretir; push avukatın | m.9 |
| `8be918f` | güvenlik üyesi tanımındaki mutlak yol örneği kaldırıldı | Sır/anonimlik (`test_b38`) | m.7 |

Değişen kod parçaları yalnız dört dosyadır: `md_udf_html.py` (9 satır), `belge_guvenlik.py`
(+553), `udf_md.py` (4 satır, desen özdeş), `oa_hafiza.py` (2 satır), `aile_dogrula.py` (17
satır). Yeni script yok (`git diff --diff-filter=A` boş) → `test_b37` kapsam borcu doğmaz.

### 1.1 Koruma gevşemesi taraması — altı eksen

- **Fail-closed → fail-open:** bulunmadı. Excel kapısında okuyucu yok / boyut sınırı /
  eşleşmeme / parça sınırı → `TABLO_AC` ya da `DENETLENEMEDI_AC` ile VERİ sarması ve
  `R.denetlenemedi` dolu (`belge_guvenlik.py:2512-2553`, `:2674-2700`); testle kilitli
  (`tests/test_v0519_excel_gizli_katman.py:441`, `:452`, `:464`, `:497`). Dış sarmalayıcı
  `oa_ingest._guvenlik_tara` (`oa_ingest.py:1287-1297`) her istisnada DENETLENEMEZ döner.
  `R.sonuc()` DENETLENEMEZ'i "temiz" saymaz (`belge_guvenlik.py:440-456`).
- **Teyit zinciri kısalması (m.5):** değişiklik yok; künye/teyit/akıbet kodu bu dalda
  dokunulmamış (çalışma ağacındaki `kunye_ortak.py` / `ictihat_muhakeme_denetim.py` farkı
  commit'siz, karar dışı — §5).
- **Müvekkil-aleyhi dış çıktı (m.6):** tek yol Excel yanlış alarmının ifşa bölümüne aday
  olmasıdır — bkz. **E-2** (ölçüldü).
- **Avukat kararının modele kayması (m.9):** değişiklik yok; `--onay/--serh-onay/--hukum-onay/
  --karar-onay` kapılarına dokunulmamış. Heyet protokolü "karar vermez" der
  (`docs/heyet/README.md`).
- **Süre hesabında geç tarih (m.2):** `hesapla_sure`, başlangıç kapısı, adli tatil kodu
  değişmedi. Excel'de damgalı bölgedeki tarih süre adayı olmaz (önceki kural sürer); görünür
  hücre tarihleri artık aday olabilir — bkz. **N-3**.
- **Olguda doğaçlama (m.4):** `<ol start>` kaynak numarasını değiştirmez, korur
  (`md_udf_html.py:329`); Excel kapısı değer silmez/düzeltmez — her senaryoda
  `_damgasiz(yeni) == metin` kilidi (`test_v0519…:239`, `:295`, `:441`, `:464`).

### 1.2 Koşulan kapılar (geçici worktree, komut → son satır)

| Komut | Son satır |
|---|---|
| `git worktree add --detach heyet-tmp-esas HEAD` | `HEAD is now at 8be918f …` |
| `py -3.14 -m pytest tests/test_md_udf_html.py tests/test_v0519_excel_gizli_katman.py tests/test_v0518_eksikler.py tests/test_v0518_belge_guvenlik.py tests/test_udf_md.py tests/test_eklenti_vitrini.py tests/test_belge_baglantilari.py tests/test_v0516_G.py tests/test_kaynak_hijyeni.py tests/test_v0518_metin_hijyeni.py tests/test_v0585_dilekce_kurallari.py -q -n auto -m "not perf" -p no:cacheprovider` | `326 passed in 9.55s` |
| `py -3.14 plugins/ortak-avukat/skills/oa-usta/scripts/aile_dogrula.py plugins/ortak-avukat/skills` | `AİLE YAPI DENETİMİ TEMİZ.` (Denetlenen parça: 20) |
| `py -3.14 tools/satir_sayaci.py --json` (salt okur) | `test_sayisi: 3813`, toplam satır `125792` |
| Bu raporun kendi kapıları (rapor geçici worktree'ye kopyalanıp): `py -3.14 -m pytest tests/test_v0514_vitrin.py -k b38 tests/test_belge_baglantilari.py tests/test_v0518_metin_hijyeni.py -q -p no:cacheprovider` | bkz. §6 |

Tam süit ve perf kanaryası usul üyesinin görevidir; burada koşulmadı. İki sentetik ölçüm
depo dışında, oturum çalışma alanında, yalnız üretilmiş kurgu tablolarla yapıldı (m.7);
düzenekleri E-1 ve E-2'de yazılıdır.

---

## 2. Bulgular

### E-1 · UYARI · `belge_guvenlik.py:2368-2403` (`_xlsx_satirlar`), `:2387` (`ws.iter_rows()`), `:157` (`AZAMI_TABLO_XML_BAYT`)

**Kanıt.** Kapı `.xlsx`'i openpyxl TAM kipte açar (`:2414`) ve `ws.iter_rows()`'u sınırsız
gezer. Tam kipte `iter_rows`, `max_row × max_column` ızgarasındaki HER koordinat için bir
`Cell` nesnesi kurup saklar; maliyet dosya boyutuna değil ızgaraya bağlıdır. Tek sınır olan
`AZAMI_TABLO_XML_BAYT` (açılmış sayfa XML'i 128 MB) bunu bağlamaz. Sentetik ölçüm (A1:C2
değerli, artı **değersiz, yalnız stilli tek uzak hücre**; dosya birkaç KB):

| Uzak hücre | Izgara | Okuyucu `tablo_isle` | Kapı `tara` | Tepe bellek | Karar |
|---|---|---|---|---|---|
| satır 2.000 · sütun 100 | 200.000 | 0,00 s | 0,48 s | 43 MB | temiz |
| satır 20.000 · sütun 100 | 2.000.000 | 0,00 s | 6,29 s | 401 MB | temiz |

`tahmin:` satır 200.000 · sütun 100 → ~60 s ve ~4 GB; `MemoryError` `tara()` içinde yakalanır
→ DENETLENEMEZ (fail-closed, `:2766`), ama o ana kadar alım işçisi kilitli kalır ve makine
takas belleğine düşer. Okuyucu (`oa_ingest.tablo_isle`, salt-okur kip + `reset_dimensions`)
aynı dosyada 0,00 s: sorun yalnız yeni kapı yolundadır — origin/main'de bu yol yoktu.

**Müvekkile etkisi.** Evrak ekseni (alım kilitlenir; "kesilen evrak alımı baştan başlar" —
README dürüst sınırlar) ve gizli tuzak ekseni (karşı taraf bir hücreyi uzağa biçimlendirerek
alımı durdurabilir). Fail-open değildir; kayıp bütünlük değil erişilebilirliktir.

**Önerilen onarım.** `_xlsx_sayfalar`'da sayfa başına `ws.max_row * ws.max_column` (ya da
`len(ws._cells)`) için bir `AZAMI_TABLO_HUCRE` tavanı → `_TabloOlculemedi` (sebepli
DENETLENEMEDİ, mevcut `AZAMI_*` deseniyle); ya da yalnız var olan hücreleri (`ws._cells`
anahtarları, satır sırasıyla) gezmek. Önce kırmızı test: uzak stilli hücre fikstürü.

### E-2 · UYARI · `belge_guvenlik.py:2332-2345` (`_xlsx_zemin`), `:2275` (`_kontrast_bulgusu`); dürüst sınır metinleri `oa-ingest/SKILL.md:38`, `:46`; `README.md:1379`

**Kanıt.** Hücrenin kendi dolgusu yoksa zemin BEYAZ varsayılır (`:2335`, `:2340`). Excel'in
"Biçimlendir → Tablo" özelliği (`ws.tables` / `tableStyleInfo`) hiç okunmaz (kaynakta
`tables`/`tableStyle` geçmiyor). Sentetik ölçüm: A1:C3 aralığına `TableStyleMedium2` (koyu
başlık satırı, stil zeminli) uygulanmış, başlık hücreleri açıkça **beyaz kalın** yazılı kurgu
tablo → kapı kararı **BULGU**, üç `gizli-metin`, örnekler başlık metinleri ("Tarih",
"Aciklama", "Tutar"). Oysa Excel bu başlıkları koyu zeminde beyaz, görünür çizer. Bu, DOCX'te
2026-10-05 ölçümünde 29 evrakta 3.343 yanlış alarm üreten "koyu hücredeki beyaz başlık"
sınıfının Excel eşleniğidir (SKILL.md belge güvenlik paragrafı); kapının kendi ölçütü de
budur: iki renkten biri çözülemiyorsa alarm yok, çünkü "yanlış alarm ifşa dilekçesine
girerdi" (`_kontrast_bulgusu` docstring, `:2276-2278`). Tablo stili dürüst sınır listelerinde
anılmıyor (koşullu biçim, degrade/desen, şekil anılıyor).

**Müvekkile etkisi.** m.6: BULGU kararı ifşa bölümüne adaydır (`gizli_talimat_ifsa.py`
yalnız BULGU'yu alır); yersiz ifşa mahkeme önünde müvekkilin güvenilirliğini zedeler. İç
analizde de md başlığı "bu evrakta insan gözünün görmediği bir katman var" der ve başlık
satırı GİZLİ KATMAN diye modele gider. Sınırlayıcılar var (bölümü koyma kararı avukatın;
alıntı görünür; "teknik bulgu kötü niyet kanıtı değildir"), ama kapının kendi standardı
(sentetik yanlış alarm 0) burada karşılanmıyor.

**Önerilen onarım.** `ws.tables` aralıklarını (`ref`) toplayıp o aralıktaki açık renkli
yazıyı koşullu biçim kuralıyla aynı ZAYIF sınıfa almak (yalnız talimat diliyle bulgu;
`:2388-2398` deseni) ya da zemini `None` (ölçülmez) saymak; SKILL.md ve README dürüst sınırına
"tablo stili" eklemek. Önce kırmızı test: yukarıdaki düzenek. `.xls`'te xlrd tablo stilini
okumaz → "ölçülmez" diye yazılır.

### E-3 · UYARI · `belge_guvenlik.py:2811-2820` (`ozet_etiketi`), `:2784-2796` (`md_basligi`); `oa-pipeline/scripts/okuma_kapisi.py:69`; `gizli_talimat_ifsa.py:570` (HEAD)

**Kanıt.** UYARI kararının kısa etiketi `🛡TALİMAT-DİLİ`'dir (`:2819`; `okuma_kapisi.py:69`
aynı eşleme) ve md başlığı "metinde yapay zekâya hitap eden dil ya da görünmez karakter var"
der (`:2793-2795`); ifşa iç notu da UYARI'yı "görünür metinde yapay zekâya hitap eden dil ya
da görünmez karakter" diye açıklar. v0.5.18'de Excel için UYARI kararı hiç oluşmuyordu
(tablo her zaman DENETLENEMEZ ya da BULGU idi). v0.5.19 kalemiyle `gizli-satir` /
`gizli-sutun` / `gizli-sayfa` / `gizli-bicim` tek başına UYARI'dır (`test_v0519…:239`
`karar == "UYARI"`; `test_v0518_eksikler` yeni sözleşme). Sonuç: gizli satır taşıyan bir
hesap/HTS dökümü okuma listesinde ve INDEX tablosunda "TALİMAT-DİLİ" etiketiyle, md
başlığında "talimat dili ya da görünmez karakter" cümlesiyle görünür. Alt satırlar (ilk 8
bulgu) doğru türü yazar; yanlış olan özet etiket ve başlık cümlesidir.

**Müvekkile etkisi.** Gizli tuzak ekseni; m.11 "avukata açıkça bildirilir" — bildirim var,
adı yanlış. Avukat "talimat dili" etiketini biçimsel bir uyarı sanıp gizli satırı
küçümseyebilir.

**Önerilen onarım.** UYARI etiketini türe göre ayırmak (gizli-* türü varsa ör.
`🛡GİZLİ-KATMAN (UYARI)`), `md_basligi` cümlesini genelleştirmek, `okuma_kapisi` eşlemesini
tek kaynaktan okumak; test: gizli satırlı Excel'in etiketi "TALİMAT-DİLİ" olmamalı.

### E-4 · UYARI · `CHANGELOG.md:320`, `docs/DENETIM-2026-10-15.md:52` ↔ `tests/test_md_udf_html.py:88`, `:96`; `tests/test_v0584_udf_hatti.py:305`

**Kanıt.** Vitrin "9. bent artık '1.' basılmıyor" (CHANGELOG) ve "UDF/PDF'e çevrilirken"
(DENETIM B-1) der. Kilitleyen testler yalnız UDF-HTML dizgesini (`<ol start="9">`) sınar;
gerçek `udf-cli html2udf` çıktısı CI kipinde atlanır (12 ortam atlaması; `.github/workflows/
ci.yml` başlığı). udf-cli'nin `start` özniteliğini numaralandırmaya taşıyıp taşımadığına dair
depoda hiçbir ölçüm kaydı yok; PDF yolu da ölçülmedi. Kod yönünde gerileme yoktur: 1'den
başlayan liste bayt-özdeştir (`test_md_udf_html.py:88`).

**Müvekkile etkisi.** Doğrulanmamış bilgi ekseni (vitrin): mahkeme hükmü bent numarasına
atıf yapar; düzeltme UDF'te işlemiyorsa kusur sürer ama kayıt "kapandı" der.

**Önerilen onarım.** udf-cli oturumu açık makinede bir kez ölçüm (`OA_TEST_UDF_YAZICI=1`;
`start` taşıyan liste → UDF → `udf2md`/XML'den numaralandırma okunur) ve kaydı; o zamana kadar
CHANGELOG/DENETIM cümlesine "UDF-HTML'de; UDF/PDF çıktısı udf-cli ile ölçülecek" sınırı.

### N-1 · NOT · Hukuki dayanak — değişiklik yok; e-tebligat cümlesi teyit izli

Playbook, kural `*.json` ve references dosyalarında kanun maddesi / süre / tarife değişikliği
yok (`git diff --stat` ile sınandı: references altında yalnız dört `degisiklik-gunlugu.md`,
+5 satır; `*.json` değişmedi). SKILL.md farklarında anılan tek norm HMK m.29'dur ve önceden
vardı. README'deki atıflar (HMK m.82/1, Av.K. m.41/1, Av.K. m.168/2, HMK m.344/1,
HMK m.94/2-3, Teb.K. m.7/a, icra sürelerinde adli tatil) `origin/main` README'sinde birebir
mevcuttur (taşındı, değişmedi). Dalda yeni olan tek hukuki cümle `52de60f` (avukatın README
düzeltmeleri) ile gelen prompt açıklamasıdır: e-tebligatta "ulaşma günü" ve "ulaşmayı izleyen
beşinci günün sonu" iki senaryo birlikte, güvenli taraf erken son gün. Teyit izi depoda
vardır: oa-dilekce günlüğü 2026-10-12 ("Teb.K. m.7/a 4. fıkra — Yargı PRO `mevzuat_getir`
teyidi"; `origin/main`'de mevcut) ve oa-sure SKILL.md m.7/a satırları. **TEYİT BEKLİYOR yok.**

### N-2 · NOT · `belge_guvenlik.py:2519-2535` — gizli katmandaki talimatın konumu "gizli katman"

Alım kipinde `gizli-talimat` kaydının konumu sabit "gizli katman" dizgesidir (`:2529`); CLI
kipinde "satır N (sayfa X)" / "hücre … (sayfa …)" yazılır. İfşa bölümünde tespit yeri
«gizli katman» diye çıkar; satır/sütun bilgisi ayrı `gizli-satir`/`gizli-sutun` kaydındadır
(UYARI türü → iç not). m.6/m.4: dış metinde tespit yeri kesin olmalı. Öneri: `_tablo_talimat`'a
aralık → konum haritası vermek. Gerileme değil (v0.5.18'de "gizli sayfa" idi).

### N-3 · NOT · Görünür hücre tarihleri artık süre adayı olabilir — tasarım gereği, izlenecek

v0.5.18'de tüm tablo `TABLO_AC` sarmasında olduğu için Excel'den hiçbir tarih süre adayı
olmuyordu; şimdi yalnız damgalı bölge dışlanır. Bu m.11 ile uyumludur (dayanak görünür
metindir). Ölçülmeyen kalan katmanlar (koşullu biçim, degrade/desen, şekil, **tablo stili** —
E-2) bir tarihi görünür bırakabilir. Sınırlayıcı: süre adayı kesinlik iddia etmez, sure-flag
yazmaz (`okuma_kapisi.py:72-77`); başlangıç kapısı kanıt ister. Saha kalibrasyonuyla birlikte
izlenmeli.

### N-4 · NOT · `plugins/ortak-avukat/README.md:575` — ikinci vitrin Excel'i hiç anmıyor

Eklenti README'sinde "Excel" sözcüğü geçmiyor: ne `oa-ingest` satırında yetenek, ne
"Sistemin yapmadıkları"nda sınır. Kök README dürüst sınırlar bölümü (`README.md:1379`) Excel
sınırlarını yazıyor. İki vitrinin tutarlılığı için eklenti README'sine Excel satırı
(yetenek + ölçülmeyenler, tablo stili dahil).

### N-5 · NOT · Sayılar ölçümle doğrulandı

`satir_sayaci.py --json`: eklenti 48.992 / test 60.756 / araç 1.752 / beceri 13.329 / kural
963 / toplam 125.792 / test 3.813 — iki README künyesiyle (48.000+ · 60.000+ · 1.700+ ·
13.000+ · 900+ · 125.000+ · 3.813) ve `tests/README.md` OA-SUIT-SAYISI 3813 ile birebir.
Eklenti tablosundaki script sayıları `test_eklenti_vitrini` ile disk sayımına kilitli
(koşuldu, yeşil). "Tam süit 3800 geçti" ve "69 bağlantı / 29 kırık" sayıları bu koşumda
yeniden ölçülmedi (usul üyesi).

### N-6 · NOT · Heyet protokolü m.9 ile uyumlu

`docs/heyet/README.md`: "Heyet karar vermez, karar materyali üretir"; push yalnız avukatın
elinden. Tanımlarda model/ajan hiçbir onay bayrağı üretmez. Tutarlı.

### N-7 · NOT · Alt ajan raporları — iddialar ağaçta doğrulandı

`ingest-excel-gizli-katman.md`: 14 dosya, `belge_guvenlik.py` +553 (stat ✓), 28 test
(`grep -c "^def test_"` = 28 ✓), kapı `SURUM` 1.2 kaldı (`:94` ✓), karar seviyeleri kodla
aynı (✓), fail-closed yolları testli (✓). `vitrin-eklenti-readme.md`: 615 → 690 satır (✓),
üç bayat sayı 10→11, 5→6, —→1 (diff ✓). `orkestra-kok-katalog-ve-heyet.md`: `8be918f`
yalnız tanım dosyası (✓). Raporların "saha kalibrasyonu açık" uyarısı yerindedir; E-2 bu
uyarının ilk somut örneğidir.

---

## 3. Karar önerisi

**ŞARTLI PUSH.** BLOKLAYICI yok: hiçbir kapı fail-open'a dönmemiş, teyit zinciri
kısalmamış, avukat kararı modele kaymamış, süre kuralı değişmemiş, olgu üretilmemiş.
Dal, müvekkili dört eksende daha iyi korur (Excel gizli katmanı artık ölçülüyor, talep
bendi numarası korunuyor, kaynak hijyeni ve bağlantı kapıları var, vitrin ölçümle kilitli).
Şartlar, Excel kapısının iki ölçülmüş açığı ile iki dürüstlük kalemidir:

- **Ş-1 (E-1):** `_xlsx_sayfalar`'a ızgara tavanı (`max_row × max_column` ya da var olan
  hücre sayısı) → sebepli DENETLENEMEDİ; önce kırmızı test (uzak stilli hücre).
- **Ş-2 (E-2):** `ws.tables` aralıklarındaki açık yazı ZAYIF (yalnız talimat diliyle) ya da
  zemin "ölçülmez"; dürüst sınıra "tablo stili"; önce kırmızı test (stil başlıklı kurgu
  tablo → `rapor is None`).
- **Ş-3 (E-3):** Excel gizli-katman UYARI'sı için etiket ve md başlığı türe uygun;
  `okuma_kapisi` ile tek kaynak; test.
- **Ş-4 (E-4):** udf-cli oturumuyla `<ol start>` UDF düzeyinde bir kez ölçülüp kaydedilir;
  ölçülene kadar CHANGELOG/DENETIM cümlesi "UDF-HTML'de" diye sınırlanır.

Ş-1 ve Ş-2 push'tan önce; Ş-3 ve Ş-4 aynı dalda ayrı commit olarak yeterlidir. Her şart
`tests/README.md` OA-SUIT-SAYISI ve ilgili parça günlüğünü günceller.

---

## 4. Doğrulanamayanlar (resmî kaynak ya da ortam teyidi gerektirir)

- `<ol start>` özniteliğinin `udf-cli html2udf` ve PDF yolunda numaralandırmaya işlenmesi —
  udf-cli oturumu bu koşumda yok (E-4).
- Excel kapısının gerçek evrakta yanlış alarm oranı — alt ajan raporu tek gerçek `.xls`
  (temiz) bildiriyor; bu koşum yalnız sentetik düzenek ölçtü (E-2 düzeneği yanlış alarm verdi).
- Tam süit (3800 geçti) ve perf kanaryası — usul üyesinde; burada yalnız hedefli 326 test.
- Hukuki norm teyidi gereken yeni kalem yok (N-1); e-tebligat cümlesinin dayandığı günlük
  kaydı Yargı PRO teyit tarihi taşır, teyidin kendisi bu koşumda yinelenmedi (ağ yok).

---

## 5. Commit'lenmemiş işler — karar dışı

Paylaşılan çalışma ağacında BAŞKA oturumun açık işi durur ("resmî kaynak beyaz listesi /
Yargı Pro MCP ilanının kaldırılması"): izlenen `.claude-plugin/marketplace.json`,
`plugins/ortak-avukat/.claude-plugin/plugin.json`, oa-ingest `SKILL.md`,
`references/gizli-talimat-ifsasi.md`, `scripts/gizli_talimat_ifsa.py`, oa-kontrol
`ictihat_muhakeme_denetim.py`, `kunye_ortak.py`, oa-pipeline `oa_hafiza.py`,
`tests/test_kaynak_url.py`; izlenmeyen `references/resmi-kaynaklar.md`,
`tests/test_kanal_bagimsiz_metin.py`, `tests/test_teyit_kanali.py`. Dokunulmadı, okunmadı,
değerlendirilmedi; bu rapor yalnız commit'li fark (`origin/main...HEAD`) üzerinedir. O iş
teyit zincirine (m.5) dokunduğu için commit'lendikten sonra ayrı heyet koşumu ister.

---

## 6. Bu raporun kendi kapıları ve temizlik

Rapor paylaşılan ağaca yazıldı, geçici worktree'ye kopyalanıp `test_b38` (mutlak yol),
`test_belge_baglantilari` (bağlantı) ve `test_v0518_metin_hijyeni` (ham görünmez karakter)
kapılarından geçirildi; sonuç orkestra oturumuna dönüşte yazılmıştır. Geçici worktree
`heyet-tmp-esas` `git worktree remove --force` ile kaldırıldı; sentetik ölçüm dosyaları
depo dışındaydı ve silindi. Paylaşılan ağaçta bu rapor dışında hiçbir dosya değiştirilmedi;
git yazma komutu kullanılmadı.

KARAR ÖNERİSİ: ŞARTLI PUSH · BLOKLAYICI 0 · UYARI 4 · NOT 7

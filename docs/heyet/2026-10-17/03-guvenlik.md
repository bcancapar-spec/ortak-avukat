# Heyet raporu — GÜVENLİK ve GİZLİLİK · 2026-10-17 · 3. koşum (main'e birleştirme kapısı)

**Üye:** oa-heyet-guvenlik · **Dal:** `denetim/fable-2026-10-15` · **HEAD:** `c94e982` (push edilmiş; PR #9) ·
**Kapsam:** `origin/main..HEAD` 25 commit; ikinci koşumdan (`61b8e14`) sonra 8 yeni commit, 124 dosya, +2706/−615.
Karar önerisi "main'e birleştirme" anlamındadır. Önceki koşumlar: [1. koşum](../2026-10-16/03-guvenlik.md)
(ŞARTLI PUSH 0·1·6), [2. koşum](../2026-10-16-2/03-guvenlik.md) (PUSH 0·0·5). Ölçü: müvekkilin sırrı ve
güvenliği (anayasa m.7, m.10, m.11; `.github/SECURITY.md` — bu dalda yeniden yazıldı; `CLAUDE.md` yasak bölgesi).

## 1. Kapsam ve yöntem

Yeni commit'ler: `2aaf6ea` (Excel üçüncü tur), `d996f62` + `6801ac7` (v0.5.19 çapraz denetim sonuç önbelleği),
`66b5d09` (birleştirme), `7764139` + `9e431ac` + `8998e34` + `c94e982` (hibrit teyit kanalı: `mcpServers` kaldırıldı,
beyaz liste, `--kaynak-url`, [G7], 87 dosya canlı metin, kayıtlar). İlk 17 commit önceki iki koşumda tarandı; bu
koşumda yalnız sabit dosyalar ve sayılar yeniden ölçüldü.

Yöntem. Commit'li fark `git diff 61b8e14..HEAD` (kod) ve `-U0` (sır taraması) ile alındı; çalışma ağacı temizdi
(yalnız bu koşumun `docs/heyet/2026-10-17/` dosyaları izlenmiyor). Test koşan her kapı ve her deney temiz geçici
worktree'de koşuldu: `git worktree add --detach heyet3-tmp-guvenlik HEAD` (varsayılan ayar; `git status --short`
0 satır, HEAD `c94e982`). Yorumlayıcı `py -3.14` (3.14.8); `PYTHONUTF8=1`, `OA_TEST_UDF_YAZICI=0`;
`-p no:cacheprovider`. Deney betikleri ve sentetik veri depo dışı geçici dizinde (`-I` ile koşuldu); openpyxl 3.1.5.
Ağ kullanılmadı; hiçbir portala ya da uç noktaya gidilmedi. Depo dosyası düzenlenmedi; tek yazılan dosya bu rapordur.

| # | Komut / düzenek | Son satır |
|---|---|---|
| 1 | `git diff --stat 61b8e14..HEAD -- hooks/ .github/workflows/ requirements.txt pyproject.toml .claude-plugin/ plugin.json` | yalnız `marketplace.json` (+1/−1) ve `plugin.json` (+3/−9); kanca, CI, bağımlılık, sürüm dosyaları boş |
| 2 | `pytest tests/test_v0514_vitrin.py -q -k b38` | `3 passed, 16 deselected in 0.27s` |
| 3 | `pytest tests/test_v0518_metin_hijyeni.py tests/test_kaynak_hijyeni.py -q` | `7 passed in 0.73s` |
| 4 | `ruff check .` | `All checks passed!` |
| 5 | güvenlik seti: ilk koşumun 10 dosyası + `test_teyit_kanali`, `test_kanal_bagimsiz_metin`, `test_kaynak_url`, `test_v0519_capraz_onbellek` | `356 passed in 25.42s` (2. koşum 10 dosya: 263) |
| 6 | teslim zinciri / sürüm kilidi / bağlantı / vitrin, aynı 7 dosya | `133 passed in 20.06s` (önceki koşumlar 133) |
| 7 | Sır taraması: `-U0` eklenen 2706 satır — TCKN, IBAN, telefon, e-posta, mutlak yerel yol, token/anahtar/parola, esas-karar no, `_oa/` içerik yolu, Ad SOYAD, Cf/çift yönlü, dava kimliği, eski uç nokta | §2.1 |
| 8 | Aynı desenler `docs/heyet/2026-10-17/ajan-raporlari/*.md` (4 dosya, izlenmeyen) | tümü 0 |
| 9 | `resmi_kaynak_mi` düşmanca adres deneyi (41 vaka: userinfo/fragment/sorgu taklidi, yüzde-kodlu nokta, punycode, U+2024, ters bölü, NUL, sondan ekleme, IP, ftp/file, büyük harf, port, sondaki nokta, alt alan, görünmez karakter) | beklenen dışı 0 (§2.1, N-1) |
| 10 | Excel nesne sayacı deneyi: dört XML yazımı × 5.000 hücre; ölçek 100.000 / 300.000 hücre (`tracemalloc`) | §2.2 U-1 |
| 11 | `oa_hafiza.py teyit` Layer 0 deneyi: aynı sentetik 11 haneli sayı `--sorgu`'da ve `--kaynak-url` sorgu dizesinde | §2.2 U-2 |
| 12 | Bu raporun taslağı temiz kopyada b38 + metin/kaynak hijyeni + bağlantı kapısı + Cf/yol/e-posta sayımı | dönüş mesajında |

Tam süit bilinçli olarak koşulmadı (usul üyesinin görevi); alt ajan beyanı "3887 geçti · 12 atlandı" beyan sayılır.

## 2. Bulgular

### 2.1 Sıfır bulgu alanları (kanıtıyla)

- **Sır sızıntısı (herkese açık, push edilmiş dal).** 2706 eklenen satırda: TCKN 0 · IBAN 0 · telefon 0 · e-posta 0 ·
  mutlak yerel yol 0 · token/anahtar/parola 0 · ham görünmez/çift yönlü karakter 0. Esas/karar deseni 30 eşleşmenin
  tümü yayımlanmış içtihat künyesi ya da sentetik fikstür: `sure_kurallari.json:632,645` ve `oa-usul/SKILL.md:173`
  (yalnız kanal cümlesi değişen satırlar; künyeler `origin/main`'de de var — ölçüldü), `bireysel-basvuru-yolu.md:177`
  (AYM norm denetimi), `tests/test_teyit_kanali.py` (kurgu daire + kurgu numara). "Dava kimliği" tek eşleşmesi
  `oa-pipeline/SKILL.md:313`'teki genel "dosya no" sözcüğü. `_oa/` 33 eşleşmesi ürün yolu adıdır (içerik değil).
  Eski uç nokta anması 6: `CHANGELOG.md:425` (tarihli kayıt) ve üç kilit testin yasak dizeleri. Dört ajan raporunda
  bütün desenler 0 (ölçüm 8). `tests/oa_teyit_kanali.py` adresi sentetiktir (`/karar/sentetik-1`), hiçbir adrese
  gidilmez.
- **Tedarik zinciri / ilan (B-23).** HEAD'de `plugin.json` ve `marketplace.json`'da `mcpServers` yok; `.mcp.json`
  depoda yok (`find` 0); `hooks.json`'da yalnız altı kanca olayı; README/SKILL/`oa_kurulum.py`'de kurulum kalıntısı
  (`/mcp`, `Authenticate`, `plugin:ortak-avukat:`) 0. `test_v0518_mcp_ilan` 6 → 4 eşlemesi ölçüldü:
  `test_ilan_edilen_sunucular_yalniz_izinli_liste` → `test_izinli_ilan_listesi_bos_ve_plugin_json_anahtari_hic_yok`
  (`IZINLI = {}` + anahtar hiç yok); `test_ikinci_ilan_kapisi_yok` (iki `.mcp.json` + marketplace) →
  `test_teyit_kanali::test_eklenti_hicbir_mcp_sunucusu_ilan_etmez` aynı üç denetim + manifestlerde eski sağlayıcı
  adı yok; `test_kutuk_sozlugu_yedek_adlari_damga_disiplininde_tutar` silindi, karşılığı
  `test_arac_sozlugu_ucuncu_taraf_mcp_adlari_tasimaz` + [G7]. B-23 dersinin üç kilidi duruyor (sahipsiz adres
  tarihçe dışında geçmez; otomatik yedeğe geçilmez; yedek proje önerilmez). Canlı metinde eski sağlayıcı/uç nokta
  anması: muafiyet dışı `git grep` 0; `STATUS.md:162,343` tarihli bölüm (muaf, test docstring'inde gerekçeli).
  `hooks/`, `run-hook.cmd`, `requirements.txt`, `ci.yml`, `pyproject.toml` 61b8e14..HEAD değişmedi (ölçüm 1).
  Yeni import yalnız `urllib.parse` (`kunye_ortak.py:1227`, ayrıştırıcı — ağ çağrısı değil) ve `hashlib`
  (`pipeline_kayit.py`); eklenen `.py` satırlarında (tests hariç) `requests|urllib.request|socket|http.client|
  subprocess|eval|exec|pickle|os.system|@latest|npx` 0. `udf_yaz.py` farkı 2 docstring satırı (sürüm sabiti ve
  katı engel değişmedi; ölçüm 6).
- **Layer 0 (m.10) — korunanlar.** `oa_hafiza.py:832-872` `_layer0_sorgu_tara` TCKN / IBAN / e-posta / telefon /
  plaka / mahkeme+esas no / ad-soyad; `:1227-1232` her `--sorgu` için araç sınıfından bağımsız (deney 11-A:
  sentetik sayı `--sorgu`'da → `RET (Layer 0)`, çıkış 1, muhakeme kaydı doğmadı). Beyaz liste fail-closed:
  kardeş modül yüklenemezse RET (`:1275-1279`), liste dışı adres RET (`:1280-1285`), liste dışı kabul bayrağı yok;
  [G7] dayanak kaydında adres yok/liste dışı → TESLİM ENGELİ (`ictihat_muhakeme_denetim.py:929-943`). `resmi_kaynak_mi`
  (`kunye_ortak.py:1255-1275`) 41 vakada beklenen davranış: alan adı küçük harfe çevrilir, sondaki nokta atılır,
  `hostname` (userinfo/port ayrışır), yalnız eşitlik ya da `.` + alan adı soneki, `.gov.tr` genel kuralı; yol ve
  sorgu dizesine bakılmaz (tasarım). UYAP giriş / e-imza / PIN / parola için eklenen satır 0; bulut OCR 0.
- **Gizli talimat savunması (m.11).** Excel üçüncü tur yalnız damgalar ve kaydeder: `_tablo_kalani_denetlenemedi`
  (`belge_guvenlik.py:2678-2693`) üreteç hatasında kalan metni VERİ sarar, kalan gizli sayfaları başlıktan damgalar,
  talimat dilini sınıflar; ilk sebep korunur (`R.denetlenemedi or sebep`). `zemin-olculemedi` (`:2816-2823`) kayıt
  düşer, damga vurmaz. Süre bütçesi satır döngüsünde (`:2726-2733`), aşım sebepli `DENETLENEMEDI_AC`. İfşa motoru
  yalnız `karar == "BULGU"` alır (`gizli_talimat_ifsa.py:567-580` → `continue`); UYARI dilekçe bölümüne girmez.
  DENETLENEMEZ sessizce temiz sayılmaz. `_tablo_hata_sebebi` (`:2673-2675`) `_kirp(str(e), 100)` — openpyxl
  iletileri tablo tanımı / sütun adı / renk dizesi taşır, hücre metni değil; sebep yalnız yerel künye ve md
  başlığına gider.
- **Çapraz denetim önbelleği (`_oa/defter/.capraz-onbellek.json`).** İçerik: `{"kopuk": [...], "belirsiz": [...]}`,
  öğeler `{tip, mesaj}` (`capraz_denetim.py:343-347`) — evraktan türetilmiş eşleşme mesajları (kimlik/ad dizeleri),
  metin bütünü değil. `.gitignore:8-9` (`_oa/`, `**/_oa/`; `git check-ignore` doğruladı); teslim paketi `defter`
  dizinini paketlemez (`teslim_paketi.py` grep 0). Anahtar sha256: üç girdinin baytları, damgalı denetim JSON'ları,
  `capraz_denetim.py` + `pipeline_kayit.py` özeti, yorumlayıcı, şema (`pipeline_kayit.py:3636-3663`). Başlık
  `{"anahtar", "govde": sha256}` + gövde; anahtar ya da gövde özeti tutmazsa None (`:3670-3697`); okuma/anahtar/yazma
  istisnaları kendi `except`inde, dış `except`e ([], []) düşmez (`:3757-3812`). `_oa/defter` yoksa yazılmaz
  (`:3706`); tmp + `os.replace` (`:3717-3723`); dedup parmak izi dışı (`:4995`). 37 test yeşil (ölçüm 5): çöp /
  kesik / boş / temizlenmiş gövde / yabancı anahtar / JSON değil / tip yanlış / dizin → yeniden hesap; append-only
  deftere dokunulmaz; çıktı önbellekli/önbelleksiz birebir. `CLAUDE.md` yasak bölgesiyle uyumlu.
- **Kanca ağı.** Değişmedi; `run-hook.cmd` yürütülebilir satırlarında `||` yok; hedef `hook_giris.py`; kanca
  testleri yeşil (ölçüm 5).
- **Girdi seli.** Arşiv bütünü toplamı `ZipInfo.file_size` beyanıyla (`belge_guvenlik.py:2500-2505`; CPython beyandan
  fazlasını okutmaz), gizli sütun kıskacı (`:2394-2411`), aralık üyeliği nesnesiz (`:2414-2420`), sayfa başına
  `AZAMI_HUCRE_BULGU`. Nesne tavanının açığı U-1.
- **Metin hijyeni.** Ölçüm 3, 4, 7, 8: 0 / yeşil.
- **Alt ajan beyanlarından ağaçta doğrulananlar.** "`mcpServers` kaldırıldı" ✓; "`.mcp.json` yok" ✓; "6 → 4" ✓;
  "`oa_kurulum` adımı `teyit_kanali`, BİLGİ, ağdan yoklamaz" ✓ (`oa_kurulum.py:316-326`); "`oa_hafiza` sözlüğünden
  üçüncü taraf adları çıktı" ✓ (`:570-598`); "önbellek fail-closed, 37 test" ✓; "Excel +12 test" — güvenlik seti
  263 → 356 artışının içinde (ayrı sayılmadı); `9e431ac` 83 dosya +505/−418, `2aaf6ea` 14 dosya +536/−69, `7764139`
  26 dosya +681/−111 (ölçüldü); "87 dosya / 290 satır" anma sayısı ölçülmedi (usul).

### 2.2 İlk iki koşumun kalemleri (durum, ölçümle)

| Kalem | Durum | Kanıt |
|---|---|---|
| 1. koşum U-1 / K-1 | kapalı (2. koşumda) | `_xlsx_var_olan_hucreler` |
| 2. koşum N-1 (satır döngüsü süre bütçesi) / K-13 | kapalı | `belge_guvenlik.py:2726-2733` |
| 2. koşum N-2 (ZAYIF aralık üyeliği maliyeti) / K-13 | kapalı | `_xlsx_aralik_sinirlari` `:2414-2420`, karşılaştırma `:2482-2486` |
| 2. koşum N-3 (`xl/` dışı parçalar) / K-12 | kapalı | toplam bütün girdiler `:2503` |
| 2. koşum N-4 (üreteç hatası genel yola düşüyor) / K-14 | kapalı | `_tablo_kalani_denetlenemedi`, `_tablo_tara` `:2866-2880` |
| 1. koşum N-2 (koşullu biçim aralığı kaydı) / K-10 | kapalı | `zemin-olculemedi` kaydı `:2816-2823` |
| K-3 (UYARI etiketi türe göre) | kapalı | `ozet_etiketi` `:3016-3018`, `okuma_kapisi.guvenlik_etiketi` |
| K-4 (CHANGELOG "UDF-HTML" sınırı) | kapalı | `CHANGELOG.md:321` |
| K-7 / 1. koşum N-5 (`.gitignore` `.claude/`) | kapalı | `.gitignore:29`; `git ls-files .claude` boş |
| 1. koşum N-4 (CI `permissions:` / SHA sabitleme) | açık, değişmedi | N-4 (3. koşum) |
| K-11 (nesne tavanı) | kapalı sayılmıştı; atlatılıyor | U-1 (3. koşum) |
| K-9 (commit'siz iş) | kapandı: iş commit'lendi ve bu koşumda tarandı | §1 |

### 2.3 Bulgu listesi (3. koşum)

**U-1 · UYARI · `plugins/ortak-avukat/skills/oa-ingest/scripts/belge_guvenlik.py:2377-2391` (`_xml_nesne_say`) ve
`:2506-2521` (`_xlsx_sayfalar` nesne tavanı) — K-11 hücre/satır tavanı yalnız `<c ` ve `<row ` bayt dizilerini sayar;
geçerli üç XML yazımıyla atlatılıyor.**
Kanıt: OOXML'de `r` özniteliği isteğe bağlıdır (`<c>` — openpyxl sayaçla konum verir), etiket adı ile öznitelik
arasında satır sonu/sekme geçerli boşluktur (`<c\nr="A1">`), ad alanı öneki geçerlidir (`<x:c r="A1">`; openpyxl
etiketi ad alanıyla eşler). Deney (temiz kopyanın modülü, sentetik kitaplar, 5.000 hücre):

| Yazım | Sayaç (hücre, satır) | openpyxl hücre | `AZAMI_TABLO_HUCRE`=1000 ile kapı |
|---|---|---|---|
| düzgün `<c r=…>` | (5000, 5000) | 5000 | `_TabloOlculemedi` (doğru) |
| öznitelliksiz `<c>` | (0, 0) | 5000 | KAPI GEÇTİ, kitap yüklendi |
| satır sonlu `<c\nr=…>` | (0, 0) | 5000 | KAPI GEÇTİ |
| önekli `<x:c r=…>` | (0, 0) | 5000 | KAPI GEÇTİ |

Ölçek (öznitelliksiz, sayaç 0): 100.000 hücre — dosya 11,0 KB, XML 2,6 MB → 2,19 s / tepe 43 MB; 300.000 hücre —
23,6 KB, XML 7,8 MB → 8,18 s / tepe 123 MB (0,41 KB/hücre). Öznitelliksiz hücre 26 bayt: 128 MB bayt tavanı ≈ 5 M
hücre → tahmin ~2 GB / dakikalar — tam da K-11'in kapatmaya çalıştığı sınıf (ESAS E-7 tahmini 1–2,4 GB). Gizli satır
tavanı (`<row\nhidden="1">`) aynı yolla atlatılır. Testte üç yazım yok (`test_v0519_excel_gizli_katman.py:878,891`
yalnız düzgün yazım).
Müvekkile etkisi: karşı tarafın 25 KB'lık hazırlanmış tablosu avukatın makinesinde alımı dakikalarca kilitler ve
belleği doldurur (hizmet engelleme). Sessiz geçiş yok: bellek tükenirse `MemoryError` → `tara()` dış `except` →
DENETLENEMEDİ; tamamlanırsa karar doğru. Sır sızmaz. İlk koşum U-1 ile aynı sınıf.
Onarım: sayacı etiket dilbilgisine bağlamak — `rb"<(?:[A-Za-z_][\w.-]*:)?c(?=[\s/>])"` ve `row` için aynı desen;
parça kuyruğunu önek + boşluk payıyla 64 bayta çıkarmak; ya da openpyxl'in kendi yoluyla (`iterparse`, `{ns}c` /
`{ns}row`, öğe temizleyerek) saymak — bellek sabit, hız yüklemenin altında. Önce kırmızı test: üç yazımda sentetik
kitap + `AZAMI_TABLO_HUCRE` / `AZAMI_TABLO_SATIR` monkeypatch → `_TabloOlculemedi`.

**U-2 · UYARI · `plugins/ortak-avukat/skills/oa-pipeline/scripts/oa_hafiza.py:1250-1258` (`--kaynak-url` biçim
denetimi) ve `:1261-1285` (teyit kanalı kapısı) — yeni kanalda ZORUNLU olan adres Layer 0 taramasından geçmiyor.**
Kanıt: `_layer0_sorgu_tara` yalnız `args.sorgu` üzerinde çağrılır (`:1228`); adres için yalnız `^https?://[^\s<>"]+$`
biçimi ve beyaz liste denetlenir. Hibrit kanalda model tam metni `WebFetch`'e verdiği adresten çeker; portalın arama
sayfası adresi sorgu dizesinde müvekkil tanımlayıcı veri taşıyabilir. Deney 11 (temiz kopya, `init` ile sentetik kök,
sentetik 11 haneli sayı + kurgu ad): (A) sayı `--sorgu`'da → `RET (Layer 0)`, çıkış 1, kayıt yok; (B) aynı sayı ve
ad `--kaynak-url` sorgu dizesinde (`…/arama?tc=<sayı>&ad=<ad>`), `--sorgu` anonim → çıkış 0, "Teyit kütüğüne
işlendi", `03-ictihat-muhakeme.md`'ye `**KAYNAK-URL:**` satırıyla yazıldı; (C) ARAMA sınıfı `WebSearch` + aynı adres
→ çıkış 0. Kayıt yazılınca adres [G4]/[G7]'den izinli bağlantı olarak dilekçeye geçebilir (`:1666-1677` KAYNAK-URL
dilekçede künye yanına yazılabilen tek bağlantıdır).
Müvekkile etkisi: m.10'un dört deseni (TCKN / ad-soyad / esas no / IBAN) sorgu yerine adresle dış portala gider;
kayıt bunu meşrulaştırır ve dış çıktıya bağlantı olarak taşıyabilir. Tasarım MCP kanalında da post-hoc'tu (araç
çağrısından sonra kayıt); fark: o kanalda tek taşıyıcı `--sorgu` idi ve taranıyordu, şimdi ikinci taşıyıcı zorunlu
ve taranmıyor. Model tarafı `oa-gizlilik` SKILL.md:5 web'i kapsar; `resmi-kaynaklar.md:18` "sorgu çıkmadan önce
Layer 0" der, adres için sessizdir. Mevcut bir denetim gevşetilmedi; yeni yüzey kapsanmadı — bu yüzden UYARI.
Onarım (küçük): `urlsplit(u)` yol + sorgu + parça `unquote_plus` ile çözülüp `_layer0_sorgu_tara`'dan geçirilsin;
bulgu → `RET (Layer 0)` (bilinçli geçiş `--sorgu-onayli` ile aynı bayrak); [G7]'de dayanak kaydının adresi aynı
taramadan geçsin (ikinci kilit); `resmi-kaynaklar.md` ve `oa-ictihat/SKILL.md:118`'e "adres de anonimdir —
portalın arama sayfası adresine müvekkil verisi yazılmaz" cümlesi. Önce kırmızı test: `test_teyit_kanali`'ye deney
B ve C vakaları.

**N-1 · NOT · `plugins/ortak-avukat/skills/oa-kontrol/scripts/kunye_ortak.py:1267` — düz `http://` şema kabul;
yol ve sorgu dizesine bakılmaz.**
Kanıt: `p.scheme not in ("http", "https")`; deney 9'da `http://` resmî alan True, `…/yonlendir?to=<dış adres>`
True (açık yönlendirme yolu). Beyaz listedeki portallar https'e yönlendirir; düz http ile çekilen tam metin yolda
değiştirilebilir, sorgu düz metin gider. Etki düşük (model fiilen https kullanır). Öneri: yalnız `https`, ya da
http'de görünür UYARI; yol/sorgu için U-2.

**N-2 · NOT · `pipeline_kayit.py:3678-3679` (`_capraz_onbellek_oku`) — dosya bütünüyle okunur, boyut tavanı yok.**
Kanıt: `f.read()`; güven sınırı dava klasörü (docstring `:3675-3676`; defter `.jsonl` de aynı). Etki yok (kendi
dizininde kendi yazdığı dosya). Kayıt.

**N-3 · NOT · `plugins/ortak-avukat/skills/oa-ingest/scripts/gizli_talimat_ifsa.py:569-574` — UYARI iç notu artık
`zemin-olculemedi` kaydının `ornek` alanını (hücre metni) taşıyabilir; cümle Excel türleri için yanlış.**
Kanıt: `ilk["ornek"]` `_alinti_metni` ile iç nota girer; iç not yalnız JSON `ic_not` ve konsola gider (`:664`,
`:895-897`), dilekçe bölümüne girmez (`:567` → `continue`) — m.6 korunur. Cümle "görünür metinde yapay zekâya hitap
eden dil ya da görünmez karakter" Excel gizli katman / zemin UYARI'ları için yanlış (orkestra raporunda açık kalem;
ESAS alanı). Kayıt.

**N-4 · NOT · `.github/workflows/ci.yml` — `permissions:` yok, eylemler etiketle sabit (ilk koşum N-4; 61b8e14..HEAD
0 satır).** `ruff==0.17.0`, `udf-cli@${SURUM}` sabit; `secrets.*` yok. Ayrı kalem.

**N-5 · NOT · `.github/SECURITY.md:28-37` ve ilan kilitleri — tarihli kayıtlar eski kanalı adıyla ve uç nokta adresiyle
anmaya devam eder (`CHANGELOG.md:425`, parça günlükleri, `STATUS.md` tarihli bölümler); belge bunu söylemiyor.**
Kanıt: `test_kanal_bagimsiz_metin.py:9-20` muafiyeti docstring'de gerekçeli; SECURITY.md yalnız "canlı metinlerde"
der. Ayrıca `test_eklenti_hicbir_mcp_sunucusu_ilan_etmez:291` manifestlerde yalnız eski sağlayıcı adını yasaklar
(dize denetimi). Öneri: SECURITY.md'ye tek cümle ("tarihli kayıtlar eski kanalı anar; kilit canlı metin içindir") ve
manifest kilidini sağlayıcıdan bağımsız kılmak (`plugin.json` / `marketplace.json` içinde `http(s)://` dizesi yok).

## 3. Karar önerisi — ŞARTLI PUSH (main'e birleştirme)

Sır sızıntısı yok (2706 satır + 4 ajan raporu: 0), Layer 0'da mevcut bir denetim gevşetilmedi, sahipsiz uç nokta
yok (hiç ilan yok; üç kilit duruyor), kanca ağı değişmedi: PUSH ETME eşiği aşılmadı. İki UYARI var; ikisi de ucuz
kapanır ve ikisi de kırmızı testle kilitlenmelidir:

1. **U-2 birleştirmeden ÖNCE kapatılır.** Teyit kanalı bu birleştirmenin ana değişikliğidir; m.10'un mekanik
   tripwire'ı yeni zorunlu alanı kapsamadan kanal main'e girmemeli (yaklaşık on satır + iki test).
2. **U-1 birleştirmeden önce kapatılır** ya da avukat tercih ederse `STATUS.md` / `YOL-HARITASI.md`'ye tarihli açık
   kalem olarak yazılır; tercihim kapatmaktır (ilk koşum U-1 aynı sınıfta kapatılmıştı; K-11 "kapandı" kaydı bu
   hâliyle eksik).
3. Tam süit usul üyesinin ölçümüyle yeşil olmalı (ben 21 dosyalık iki kümeyi koştum: 356 + 133).

N-1 … N-5 kayıt kalemidir; hiçbiri sessiz geçiş ya da sır kaybı değildir.

## 4. Doğrulanamayanlar

- Tam süit ("3887 geçti · 12 atlandı") ve `OA-SUIT-SAYISI` 3900 koşulmadı/toplanmadı — usul üyesinin görevi.
- "87 dosya / 290 satır" anma sayısı ölçülmedi (commit 83 dosya); kalıntı taraması (0) ölçüldü.
- `WebFetch`/`WebSearch` canlı akışı sahada sınanmadı; hiçbir portala gidilmedi (yasak). `resmi_kaynak_mi` yalnız
  dize olarak denetlendi; IDNA eşlemesinin (tam genişlik harf, ideografik nokta) tarayıcı tarafı ölçülmedi — kapı
  bu vakalarda ya aynı resmî alanı kabul ediyor ya da reddediyor (fail-closed), kabul ettiği liste dışı vaka yok.
- U-1 ölçeği 300.000 hücreye kadar ölçüldü; tavan (~5 M hücre, ~2 GB) doğrusal büyümeden çıkarıldı.
- GitHub CI koşusu (PR #9) görülmedi; yalnız yapılandırma okundu.
- Depo dışı devir notu salt okundu; beyanları yalnız ağaçta ölçülebilenler kadar doğrulandı (§2.1 son madde).
- Bu raporun kendisi yazıldıktan sonra temiz kopyada b38, metin/kaynak hijyeni ve bağlantı kapısından geçirildi;
  sonuç dönüş mesajında.

## 5. Commit'lenmemiş işler (karar dışı)

Çalışma ağacı temiz; izlenmeyen tek klasör bu koşumun `docs/heyet/2026-10-17/` dosyalarıdır (dört ajan raporu —
tarandı, sır 0 — ve üye raporları). Önceki koşumların commit'siz işi (teyit kanalı) `7764139`…`c94e982` ile
commit'lendi ve bu koşumda tarandı; §5'te başka iş yok.

Geçici worktree `heyet3-tmp-guvenlik`: iş bitiminde `git worktree remove --force` ile kaldırıldı; `git worktree list`
çıktısında yer almıyor (dönüş mesajında teyit edildi).

KARAR ÖNERİSİ: ŞARTLI PUSH · BLOKLAYICI 0 · UYARI 2 · NOT 5

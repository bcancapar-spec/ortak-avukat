# Heyet raporu — ESAS üyesi (hukuki yöntem, müvekkil menfaati) — 2026-10-16 · 2. koşum

**Dal:** `denetim/fable-2026-10-15` · **HEAD:** `ca37539` · **Kapsam:** `origin/main..HEAD` (16 commit; 14'ü
ilk koşumda denetlendi ve değişmedi — commit kimlikleri aynı; yeni olan `47372fc` ve `ca37539`) ·
**Ölçüm ortamı:** geçici worktree `heyet2-tmp-esas` (detached, HEAD `ca37539`, varsayılan ayar,
`git status --short` 0 satır; iş bitince kaldırıldı) · `py -3.14` (Python 3.14.8, openpyxl 3.1.5) ·
`PYTHONUTF8=1 OA_TEST_UDF_YAZICI=0` · pytest `-p no:cacheprovider`.

Ölçü tektir: bu dal sahaya çıkarsa müvekkil hangi kayıptan korunur, hangi kayba açılır (evrak · süre ·
doğrulanmamış bilgi · sır · karşı tarafın gizli tuzağı). İlk koşumda ŞARTLI PUSH demiştim (E-1 ızgara, E-2
tablo stili push'tan önce); avukat "push yok, önce K-1 ve K-2" dedi; onarım `ca37539` ile geldi. Bu koşum
onarımı ve bütünü yeniden ölçer. Alt ajan raporları BEYAN sayıldı; her iddia diff'te ve geçici kopyada
ölçüldü. Anayasa m.7 gereği kişi, müvekkil, dosya numarası ve mutlak yerel yol yazılmadı. Başarı olasılığı
sayıyla verilmez. Süre ölçümleri **yük altında** alındı (usul üyesi aynı anda komşu geçici kopyada tam
süiti koşturuyordu); bellek ölçümleri (`tracemalloc` tepe) yükten etkilenmez.

---

## 1. Kapsam

### 1.1 Yeni commit'ler — parça · korunan kayıp ekseni · anayasa maddesi

| Commit | Parça | Müvekkili hangi kayıptan korur | Madde |
|---|---|---|---|
| `47372fc` | yalnız belge: `docs/heyet/2026-10-16/**` (3 üye raporu, KARAR, 4 ajan raporu), CHANGELOG "Heyet" maddesi, STATUS notu (`git show --stat`: 10 dosya, +1150, kod 0) | Kayıt: push kararının avukatta kaldığı ve şartların yazılı olduğu belgelenir; "heyet karar vermez" | m.8, m.9 |
| `ca37539` | oa-ingest `belge_guvenlik.py` (+62/−16: `_xlsx_var_olan_hucreler`, `xl/` toplamı, tablo stili ZAYIF), `tests/test_v0519_excel_gizli_katman.py` +3 test (28 → 31, `grep -c "^def test_"`), oa-ingest `SKILL.md` 1 satır, kök README dürüst sınır, oa-ingest günlüğü, CHANGELOG "Onarım" cümlesi, STATUS, `tests/README.md` 3813 → 3816, eklenti README künyesi | **Evrak ekseni:** karşı tarafın 5 KB'lık hazırlanmış tablosu alımı kilitleyemez (K-1). **m.6:** koyu tablo başlığındaki beyaz yazı artık yanlış BULGU (ifşa adayı) üretmez (K-2). **Gizli tuzak:** boyut ön denetimi `xl/` bütününü sayar (N-1) | m.1 (tasarruf mekanik katmanda, kayıpsız), m.6, m.11 |

İki commit'te hukuki dayanak değişikliği yok: `git diff --stat 8be918f..HEAD -- '*.json' 'skills/*/references/'
'skills/*/SKILL.md'` → yalnız oa-ingest `SKILL.md` dürüst sınır cümlesi (1 satır); `*.json` 0; references altında
yalnız günlük kaydı. Yeni script yok (`git diff --diff-filter=A --name-only 8be918f..HEAD` → yalnız `docs/heyet/**`)
→ `test_b37` kapsam borcu doğmaz. `ca37539`'daki `SKILL.md` farkı tek satırdır (`git show ca37539 -- SKILL.md`);
onarım raporunun "HEAD tabanlı blob ile sahnelendi" beyanı doğrulandı — başka oturumun açık hunk'ları commit'e
girmemiş.

### 1.2 Koşulan kapılar (geçici worktree; komut → son satır)

| Komut | Son satır |
|---|---|
| `git worktree add --detach heyet2-tmp-esas HEAD` | `HEAD is now at ca37539 …` · `git status --short` 0 satır |
| `py -3.14 -m pytest tests/test_v0519_excel_gizli_katman.py tests/test_v0518_eksikler.py tests/test_v0518_belge_guvenlik.py tests/test_eklenti_vitrini.py tests/test_belge_baglantilari.py tests/test_v0514_vitrin.py -q -n auto -m "not perf" -p no:cacheprovider -rs` | `200 passed in 21.64s` (atlama 0; b35: toplanan = OA-SUIT-SAYISI 3816) |
| `py -3.14 plugins/ortak-avukat/skills/oa-usta/scripts/aile_dogrula.py plugins/ortak-avukat/skills` | `Denetlenen parça: 20` · `AİLE YAPI DENETİMİ TEMİZ.` |
| `py -3.14 tools/satir_sayaci.py --json` | `test_sayisi: 3816` · eklenti 49.022 · test 60.821 · araç 1.752 · beceri 13.330 · kural 963 · toplam 125.888 |
| Sentetik düzenek (depo dışı geçici dizin, yalnız kurgu kitaplar; modüller geçici kopyadan yüklendi) | §2 tabloları (K-1 eşdeğerlik 10 kenar durumu, önce/sonra ölçüm, K-2 10 düzenek, N-1 oranı, iki ek vektör, profil) |

Tam süit ve perf kanaryası usul üyesinindir; burada koşulmadı.

### 1.3 Koruma gevşemesi taraması — altı eksen (`ca37539`, `47372fc`)

- **Fail-closed → fail-open:** bulunmadı. `_cells` yoksa `AttributeError` → `tara()` dış `except` → DENETLENEMEZ
  (`belge_guvenlik.py:2379-2380` docstring'i, `:2795-2799`); `xl/` toplamı eşiği aşınca `_TabloOlculemedi` →
  `_tablo_denetlenemedi` (`:2439-2442`, `:2722`); testle kilitli (`test_v0519…:643-656`). Tablo stili
  aralığı ZAYIF kuralı kapıyı "temiz" demeye itmez ama evrak düzeyinde kayıt da düşürmez — bu bir belgelenmiş
  ölçüm sınırıdır, fail-open değildir; bedeli **E-5**'te ölçüldü.
- **Teyit zinciri (m.5):** değişiklik yok; künye/teyit/akıbet kodu iki commit'te dokunulmamış.
- **Müvekkil-aleyhi dış çıktı (m.6):** ilk koşum E-2 yolu kapandı (ölçüm: `TableStyleMedium2` beyaz kalın
  başlık → `rapor is None`, §2 t3). Artık: ZAYIF aralıkta talimat dili taşıyan hücre "gizlenmiş hücre" diye
  kaydediliyor (**N-3**).
- **Avukat kararının modele kayması (m.9):** değişiklik yok; onay bayrakları dokunulmamış; KARAR.md "heyet karar
  vermez, karar materyali üretir" der; `47372fc` hiçbir onay üretmez.
- **Süre hesabında geç tarih (m.2):** `hesapla_sure`, başlangıç kapısı, adli tatil kodu değişmedi. Yeni etki:
  tablo stili aralığındaki açık renkli tarih onarımdan önce BULGU/damgalıydı (süreye girmezdi), şimdi görünür ve
  damgasız (§2 t5) → süre adayı olabilir; sınırlayıcılar sürüyor (süre adayı kesinlik iddia etmez, başlangıç kapısı
  kanıt ister) — **E-5** kapsamında.
- **Olguda doğaçlama (m.4):** değer silinmez/düzeltilmez — 20 düzeneğin hepsinde `_damgasiz(yeni) == metin`
  (§2); künye/madde/tarih üretimi yok; vitrin sayıları ölçümle (**N-7**).

---

## 2. Bulgular

Sayım yalnız bu koşumda yeni bulunanları kapsar; ilk koşumdan açık kalanlar §2.3'te (sayıma dahil değil).

### 2.1 K-1 / K-2 / GÜVENLİK N-1 kapanışının ölçümü

**K-1 eşdeğerlik (okuyucu eşlemesi bozulmadı).** `_xlsx_var_olan_hucreler` (`belge_guvenlik.py:2371-2386`)
çıktısı, aynı kitabın taze yüklemesinde `iter_rows()` ile kurulan eski gezintiyle (`satir[0].row`,
`[(h.column, h) …]`) `_xlsx_satirlar` düzeyinde karşılaştırıldı; ayrıca okuyucu (`oa_ingest.tablo_isle`,
salt-okur) metniyle eşleme ve damga-sonrası bayt özdeşliği ölçüldü:

| Kenar durumu | yeni == eski | eşleme / karar | not |
|---|---|---|---|
| A ve B sütunu her satırda boş (veri C'den) + boş gizli sütun A | evet | temiz, DENETLENEMEZ yok | sütun uzayı 1'den: kapı `[(1,''),(2,''),(3,'Tarih'),(4,'Tutar')]`, okuyucu `' \| \| Tarih \| Tutar'` |
| satır içi boş koordinat + C'de beyaz yazı | evet | BULGU, damga `a \|  \| ⟦…ZX beyaz⟧` tam yerinde | |
| kuyrukta ve ortada yalnız stilli değersiz hücre | evet | temiz | kuyruk düşer, orta `''` kalır: `[(1,'x'),(2,''),(3,'y')]` ↔ okuyucu `x \|  \| y` |
| sıra dışı ekleme (satır 10 önce 2; sütun C önce A) | evet | temiz | satır sırası `[2, 10]`, sütun sırası doğru |
| birleştirilmiş hücreler (`A1:C1`, `B2:B3`) + gizli satır 3 | evet | UYARI gizli-satir, satır 3 damgalı | `_cells[(1,2)]` tipi `MergedCell`; değeri None → `''` |
| boş dize değeri ve önbelleksiz formül (`data_only`) | evet | temiz | iki yol da `''` |
| yalnız yorumlu hücre (D1) | evet | temiz | satır `[(1,'a')]` |
| hücresiz gizli satır (`row_dimensions[5].hidden`) | evet | temiz, kayıt yok | iki yolda da atlanır |
| uzak DEĞERLİ hücre (satır 20.000 × sütun 100) | — | temiz | kapı satır 20000 / 100 hücre; okuyucu son satırı `' \| '×99 + 'uzak'` |
| gizli satır 3 + beyaz E2 + boş D2 (ofset) | evet | BULGU + gizli-satir | E2 damgası ile satır 3 damgası tek damgada birleşir (**N-9**) |

**K-1 önce/sonra (bu makine, yük altında; `tracemalloc` tepe; "önce" = aynı koşumda `iter_rows` gezintisine
geri döndürülmüş kapı):**

| Kitap | Dosya | Okuyucu | Kapı SONRA | Kapı ÖNCE |
|---|---|---|---|---|
| taban (3 satır) | 4.924 B | 0,00 s | 0,01 s / 0,3 MB | 0,01 s / 0,3 MB |
| + stilli uzak hücre 3000 × 600 | 4.957 B | 0,00 s | **0,01 s / 0,3 MB** | 10,88 s / 400,1 MB |
| + stilli uzak hücre 20.000 × 100 | 4.957 B | 0,01 s | **0,01 s / 0,3 MB** | 12,50 s / 401,0 MB |

Onarım raporunun "6,29 s / 400 MB → 0,01 s / 0,3 MB" iddiası: bellek birebir (400,1 / 401,0 → 0,3 MB), "sonra"
birebir; "önce" süresi yük altında 10,9–12,5 s (ilk koşumda iki üye 6,29 s ölçmüştü) — süre makine yüküne bağlı,
büyüklük sınıfı aynı. Izgara kilidi testi (`test_v0519…:622-640`) zamanlamasız mekanizma kilididir:
`Worksheet.iter_rows` patlatılır, kapı dokunursa DENETLENEMEZ ve test kırmızı; `ReadOnlyWorksheet` ayrı sınıf
olduğu için okuyucu etkilenmez. Kilit sağlam.

**K-2 tablo stili (10 düzenek; `ref="A1:C3"`, başlık `A1:C1`):**

| Düzenek | Karar | Yorum |
|---|---|---|
| t1 `tableStyleInfo` YOK + gövdede beyaz yazı | BULGU gizli-metin B2 | stil adı yoksa ölçüm sürüyor (doğru) |
| t2 `TableStyleInfo(name=None)` + gövdede beyaz yazı | BULGU gizli-metin B2 | ad None → ölçüm sürüyor (doğru) |
| t3 `TableStyleMedium2`, beyaz kalın başlık | temiz (`rapor is None`) | ilk koşum E-2 yanlış alarmı kapandı (m.6) |
| t4 `Medium2`, gövde şerit satırında beyaz yazı | temiz | gizlilik `('gizli-metin', '…; tablo stili altında', True)` hesaplanıyor ama kayıt/damga yok → **E-5** |
| t5 `Medium2`, gövdede beyaz **tarih** | temiz | tarih görünür ve damgasız → süre adayı olabilir → **E-5** |
| t6 `Medium2`, hücrenin KENDİ beyaz düz dolgusu + beyaz yazı | temiz | hücre dolgusu stilden üstün olduğu için ölçülebilirdi → **E-5** (öneri) |
| t7 `Medium2`, koyu düz dolgu + beyaz yazı | temiz | doğru |
| t8 `Medium2`, tablo DIŞINDA beyaz yazı | BULGU gizli-metin A5 | aralık dışı ölçüm sürüyor (doğru) |
| t9 `Medium2`, gövdede beyaz yazı + talimat dili | BULGU gizli-talimat ×2 | ZAYIF yolu çalışıyor; kayıt metni "gizlenmiş hücre" der → **N-3** |
| t10 `TableStyleLight1`, beyaz kalın başlık | temiz | Light1 başlığa zemin çizmez: beyaz yazı Excel'de de görünmez — gerçek gizli yazı artık ölçülmüyor → **E-5** |

**GÜVENLİK N-1 (`xl/` toplamı):** kod `:2439` her `xl/` girdisini sayar; test `:643-656` sayfa XML'ini tam
sınıra koyup bütünün aşmasını DENETLENEMEZ diye kilitler. Davranış değişikliğinin meşru kitaplara etkisi **N-6**.

### 2.2 Bulgu listesi

### E-5 · UYARI · 2. koşum · `belge_guvenlik.py:2410-2412` (ZAYIF listesi), `:2656` (`len(gizlilik) > 2` → yalnız talimat diliyle damga); dürüst sınır `README.md:1384-1387`, oa-ingest `SKILL.md:46`

**Kanıt.** Tablo stili (ve koşullu biçim) aralığındaki düşük kontrastlı hücre için gizlilik hesaplanıyor
(t4: `('gizli-metin', 'kontrast=1.00 …; tablo stili altında', True)`) ama talimat dili yoksa ne kayıt ne damga
düşüyor; rapor `None` (= "denetlenen katmanlarda gizleme bulunmadı"). t5'te beyaz tarih görünür ve damgasız
kalıyor; t10'da `TableStyleLight1` başlığı zemin çizmediği için beyaz yazı Excel'de de görünmezken kapı susuyor;
t6'da hücrenin KENDİ düz dolgusu varken (Excel'de doğrudan hücre biçimi tablo stilinden üstündür — zemin
kesin) yine ZAYIF sayılıyor. Onarımdan önce bu hücreler BULGU/damgalıydı (yanlış alarmla birlikte); onarım
yanlış alarmı kaldırırken gerçek gizlemeyi de sessizleştirdi. İlk koşumda bu kuralı ben önermiştim
(E-2: "ZAYIF ya da zemin ölçülmez"); ölçüm bedelini şimdi gösteriyor.

**Müvekkile etkisi.** Gizli tuzak ekseni (karşı tarafın "Biçimlendir → Tablo" ile hazırladığı dökümde beyaz
yazıyla gizlenmiş tutar/tarih kayıtsız geçer) ve m.2 (t5: damgasız tarih süre adayı olabilir; sınırlayıcılar:
süre adayı kesinlik iddia etmez, başlangıç kapısı tebliğ kanıtı ister). Talimat dili saldırısı yakalanmaya
devam ediyor (t9) — m.11'in çekirdeği korunuyor. m.6 kazancı (yanlış ifşa yok) bu kayıptan ağırdır; karar doğru
yöndedir, eksik olan **evrak düzeyinde bildirim**: README/SKILL "yalnız talimat diliyle bulgudur" diyor ama
"o aralıkta açık renkli yazı var" bilgisi avukata gitmiyor. "Zemin None (ölçülmez)" daha iyi olmazdı: talimat
yakalama da giderdi.

**Önerilen onarım (aynı dalda ayrı commit; önce kırmızı test).** (a) ZAYIF aralıkta talimat dili olmayan
düşük kontrastlı hücreler için AGIR olmayan tek kayıt (`zemin-olculemedi`: sayfa, aralık, hücre sayısı, ilk
örnek) → karar UYARI; damga yok (yanlış damga da ifşa adayı değil ama metni kirletir); GÜVENLİK N-2'nin koşullu
biçim önerisiyle aynı mekanizma. (b) Tablo stili aralığında hücrenin kendi **düz** dolgusu varsa zemin kesindir:
ZAYIF değil, ölçülür (koşullu biçimde bu geçerli değil — CF hücre dolgusunu ezer). (c) README/SKILL cümlesine
"bildirilir" eki. `.xls` tarafı: xlrd tablo stilini okumadığı için t3 sınıfı yanlış alarm `.xls`'te sürebilir
(ölçülemedi, §4).

### E-7 · UYARI · 2. koşum · `belge_guvenlik.py:157-163` (`AZAMI_TABLO_XML_BAYT` 128 MB ve "tahmin: ≤ 0,5 GB" yorumu), `:2439` (ön denetim)

**Kanıt.** Tavanın bellek karşılığı iki noktada ölçüldü (yük altında süre; `tracemalloc` tepe): (1) 300.000
hücre, sayfa XML'i 14,6 MB → kapı tepe 116 MB; (2) 200.000 hücresiz gizli `<row>` tanımı (`row_dimensions`),
sayfa XML'i 6,2 MB, **sıkıştırılmış dosya 508 KB** → kapı tepe 121 MB (openpyxl her gizli satır için
`RowDimension` kurar). `tahmin:` doğrusal ölçekle 128 MB tavanında ~1 GB (hücre yoğun) ile ~2,4 GB (gizli satır
başlığı yoğun; ~10 MB sıkıştırılmış dosya yeter). Kaynak yorumu "sınır ~2,5 M hücre (tahmin: ≤ 0,5 GB)" ölçümle
çelişiyor (2–5×). Okuyucu aynı dosyada 0,66 s / salt-okur.

**Müvekkile etkisi.** Evrak ekseni — K-1 ile aynı sınıf, daha büyük dosya gerektirir: 8 GB'lık avukat
makinesinde takas, sonra `MemoryError` → DENETLENEMEZ (fail-closed, sessiz geçiş yok) ama dakikalarca kilit;
"kesilen alım baştan başlar" sınırıyla birleşince aynı dosya her koşuda yeniden kilitler.

**Önerilen onarım (aynı dalda ayrı commit).** Tavanı ölçümle yeniden belirlemek (ör. 32 MB ≈ `tahmin:`
0,25–0,6 GB) ya da ön denetime sayfa XML'indeki `<row` / `<c ` sayımı gibi ucuz bir nesne tavanı eklemek; yorumu
ölçümle düzeltmek; önce kırmızı test (sentetik gizli satır yığını → sebepli DENETLENEMEZ, bellek sabit).

### N-1 · NOT · 2. koşum · K-1 kapanışı ölçüldü — eşdeğer ve etkili

§2.1: 10 kenar durumunda yeni gezinti eski `iter_rows` gezintisiyle birebir; eşleme hiçbirinde bozulmadı;
önce/sonra bellek 400 MB → 0,3 MB. Kapanış şartı karşılandı.

### N-2 · NOT · 2. koşum · `belge_guvenlik.py:2398-2404` — gizli `<col>` yığınında `set.update` döngüsü

16.384 gizli sütun tanımı (`min=k max=16384`, 50 KB dosya, açılmış `xl/` 1,1 MB) → kapı yük altında 26,6 s,
profil (yüksüz) 2,04 s/sayfa, bunun 1,70 s'si `gizli_sutun.update(range(min, max+1))` (16.384 çağrı); bellek
12 MB; sonuç UYARI gizli-sutun (doğru). Sınırlı ve belleksiz (K-1'in aksine); 128 MB tavanında ~200 sayfa ×
2 s. Öneri: `d.max`'ı `ws.max_column` ile kıskaçlamak (hücresiz sütunun gizliliği veri taşımaz) — tek satır.

### N-3 · NOT · 2. koşum · `belge_guvenlik.py:2558` (`_tablo_talimat`) — ZAYIF aralıkta talimat kaydı "gizlenmiş hücre" der

t9'da kayıt: yöntem "Excel'de GİZLİ KATMANDA (gizli sayfa/satır/sütun ya da gizlenmiş hücre) … talimat dili",
konum "gizli katman". ZAYIF yolunda gizlilik ölçülmemiştir; koyu tablo başlığında **görünür** beyaz yazı talimat
dili taşısaydı aynı kayıt düşer ve ifşa bölümü (`gizli_talimat_ifsa.py:396` `gizli-talimat`'ı alır) mahkemeye
"gizlenmiş" derdi (m.4/m.6, dar artık: talimat dili gerektirir; bölümü koyma kararı avukatın). Öneri: ZAYIF
kaynaklı kayıtta yöntem "zemini ölçülemeyen aralıkta (tablo stili / koşullu biçim) açık renkli yazı — gizli
olduğu KESİN DEĞİL"; konum için ilk koşum N-2 haritası.

### N-4 · NOT · 2. koşum · Pivot tablo stili ZAYIF listesinde değil (kod okuması)

`belge_guvenlik.py`'de `_pivots` / `pivotTableStyleInfo` geçmiyor; ZAYIF listesi yalnız `ws.conditional_formatting`
ve `ws.tables` (`:2410-2412`). `tahmin:` koyu pivot stilinde (PivotStyleMedium/Dark) beyaz başlık t3 sınıfı
yanlış BULGU üretir; Excel'in varsayılan pivot stili açık zeminlidir, yaygın değil. Düzenek kurulmadı (openpyxl
pivot üretmez). Öneri: `ws._pivots[*].location.ref` aralıkları aynı listeye.

### N-5 · NOT · 2. koşum · `belge_guvenlik.py:2380` — `ws._cells` özel API

`requirements.txt` `openpyxl>=3.1` üst sınırsız; `_cells` kalkarsa her `.xlsx` DENETLENEMEZ olur. Sessiz kör
nokta değil: evrak başlığında "tarama hatası: AttributeError" görünür ve `test_v0519…:622` kırmızı olur (rapor
`None` bekler). Öneri: üst sınır (`<4`) ya da kurulumda `hasattr(Worksheet, "_cells")` denetimi.

### N-6 · NOT · 2. koşum · GÜVENLİK N-1 kapanışı — meşru kitapta yanlış DENETLENEMEZ beklenmez

Ölçüm: openpyxl'in yazdığı 300.000 hücrelik kitapta `sharedStrings.xml` 0 MB (3.1 dizeleri satır içi yazar),
`styles` 0,00 MB → oran Excel üretimi dosyayı temsil etmez. `tahmin:` Excel dosyasında dize başına ~15–30 B
sharedStrings payıyla eşik ~2,6 M hücreden ~2,0 M hücreye iner; HTS/hesap dökümü (1 M hücre, ~50 MB) etkilenmez.
Etkilenen kitap görünür ve sebepli DENETLENEMEZ olur (fail-closed); okuyucu metni yine gelir.

### N-7 · NOT · 2. koşum · Vitrin sayıları ölçümle — bir kaynak notu eksik

`satir_sayaci --json` ↔ iki README künyesi birebir (49.022 → 49.000+, 60.821, 1.752, 13.330, 963, 125.888,
3.816); OA-SUIT-SAYISI 3816 = toplanan (b35 yeşil); test dosyasında 31 `def test_` (28 + 3). CHANGELOG "Onarım"
cümlesi ve STATUS notu koddaki üç değişiklikle örtüşüyor. "3803 geçti · 12 atlandı · 0 kırmızı" usul üyesinde.
Eksik: günlük ve CHANGELOG "6,29 s / 400 MB" sayısını tek ölçüm gibi yazıyor; onarım raporunun tablosu "Kapı ÖNCE
(heyet ölçümü)" diyerek kaynağı belirtiyor — günlüğe de "önce: heyet ölçümü" notu (kaynak izi, m.8).

### N-8 · NOT · 2. koşum · Hukuki dayanak — değişiklik yok, TEYİT BEKLİYOR yok

§1.1: `8be918f..HEAD` aralığında kanun maddesi, süre kuralı, tarife kalemi değişikliği 0; anılan tek norm HMK m.29
(önceden var, SKILL.md).

### N-9 · NOT · 2. koşum · `belge_guvenlik.py:604-631` — bitişik damgalar birleşir

C10 düzeneğinde E2 damgası ile gizli satır 3 damgası arasında yalnız `\n` olduğu için `_uygula` ikisini tek
`⟦GİZLİ KATMAN⟧` bloğunda birleştirir (`:622`: aynı tür + aralık boşluk). Gizli satır metni damga içinde,
`_damgasiz == metin`, kayıt tam. Kayıp değil; ifşa alıntısında iki ayrı parça tek blok görünür — bilgi.

### N-10 · NOT · 2. koşum · Alt ajan raporları — iddialar ağaçla örtüşüyor

`onarim-excel-kapisi-k1-k2.md`: 9 dosya +128/−23 (stat ✓), 3 yeni test ✓, `SKILL.md` tek satır ✓, 3816 ✓,
49.022 ✓, "önce kırmızı" beyanı (üç testin eski kodda kırmızı olacağı kod okumasıyla doğrulandı: ızgara →
DENETLENEMEZ, `xl/` → rapor yok, stil → BULGU). `excel-oturumu-ozeti.md` (`934e212` kapsamı; ilk koşumda
denetlendi): 28 test, 3800/12 ilk koşum ölçümüyle aynı; yeni iddia yok. LF kopyadaki `test_yonlu_tazelik_ozdes_sessiz`
kırmızısı bu koşumda yinelenmedi (varsayılan ayarla açıldı; usul üyesinin sınıflandırması).

### N-11 · NOT · 2. koşum · `47372fc` — yalnız belge, m.9 ile uyumlu

Kod 0; KARAR.md "Heyet karar vermez" ve "push yalnız avukatın elinden"; CHANGELOG/STATUS cümleleri ilk koşum
ölçümleriyle (3800 · 12 · 0 · 93,99 s · 3813) birebir. Bağlantıları `test_belge_baglantilari` kapsıyor (200 geçti).

### 2.3 Kalan kalemlerin durumu (sayıma dahil değil)

| Kalem | Durum (HEAD `ca37539`) | Kanıt |
|---|---|---|
| K-1 (E-1 / U-1) | **KAPANDI** | §2.1 eşdeğerlik + önce/sonra; `test_v0519…:622` |
| K-2 (E-2) | **KAPANDI** (bedeli E-5) | §2.1 t3; `test_v0519…:659` |
| K-3 (E-3 etiket) | AÇIK | `belge_guvenlik.py:2849` `🛡TALİMAT-DİLİ`; `okuma_kapisi.py:69` aynı eşleme; `md_basligi` `:2823-2824` |
| K-4 (E-4 `<ol start>` UDF) | AÇIK | `CHANGELOG.md:320` "9. bent artık '1.' basılmıyor" sınırsız; udf-cli ölçümü yok |
| K-5 (U-1 taşıma atfı) | AÇIK | `docs/DENETIM-2026-10-15.md:183` "Görev 4 tamam (`45a6d2e`)", `47bba4d` notu yok |
| K-6 (U-2 kayıt) | KAPANDI | `47372fc` CHANGELOG/STATUS |
| K-7 (U-3 `.gitignore`) | AÇIK | `.gitignore`'da `claude` 0 |
| K-8 (kapılar) | YAPILDI | KARAR §4.1; bu koşum 200 geçti |
| K-9 (commit'siz iş) | BEKLİYOR | §5 |
| 1. koşum N-4 (eklenti README Excel) | AÇIK | `plugins/ortak-avukat/README.md`'de "Excel" 0 |
| USUL N-3 (STATUS başlık tarihi) | AÇIK | `STATUS.md:3` 2026-10-12 |

Yeni şart gerekir mi: **push'tan önce yeni şart yok.** E-5 ve E-7 aynı dalda ayrı commit'tir.

---

## 3. Karar önerisi

**ŞARTLI PUSH.** BLOKLAYICI yok: iki push-öncesi şart ölçümle kapandı (K-1: 400 MB → 0,3 MB, eşleme on kenar
durumunda bozulmadı; K-2: yanlış ifşa adayı yok), hiçbir kapı fail-open'a dönmedi, teyit zinciri kısalmadı,
avukat kararı modele kaymadı, süre kuralı değişmedi, olgu üretilmedi, hukuki dayanak dokunulmadı. Dal
`origin/main`'e göre müvekkili her eksende daha iyi korur. Kalan iki UYARI aynı kapının ölçülmüş sınırlarıdır
ve fail-closed'dur. Şartlar (hepsi aynı dalda ayrı commit; push'tan önce olması gereken yok):

- **Ş-1 (E-5):** ZAYIF aralıkta açık renkli yazı için AGIR olmayan evrak düzeyinde kayıt; hücrenin kendi düz
  dolgusu varsa tablo stili aralığında ölçüm; README/SKILL "bildirilir"; önce kırmızı test.
- **Ş-2 (E-7):** `AZAMI_TABLO_XML_BAYT` bellek karşılığı ölçülüp tavan ya da nesne sayımı buna göre; yorum
  düzeltilir; önce kırmızı test.
- **İlk koşumdan süren şartlar:** K-3, K-4 (aynı dalda ayrı commit), K-5, K-7 (kayıt); K-9 commit'lenince ayrı
  heyet koşumu.

Her şart `tests/README.md` OA-SUIT-SAYISI ve oa-ingest günlüğünü günceller.

---

## 4. Doğrulanamayanlar

- `.xls`'te tablo stili: xlrd okumaz; Excel'in "Biçimlendir → Tablo"yu BIFF8'e nasıl yazdığı (stil zemini hücre
  XF'ine işlenir mi) bu makinede ölçülemedi (Excel yok; ham BIFF8 fikstürü tablo kaydı taşımıyor). t3 sınıfı
  yanlış alarmın `.xls`'te sürüp sürmediği açık.
- Pivot tablo stili (N-4): düzenek kurulamadı; iddia kod okuması + tahmin.
- E-7 tavan tahmini: 6,2 ve 14,6 MB'da ölçüldü, 128 MB'da ölçülmedi (doğrusal ölçek); süre sayıları yük altında.
- N-6: Excel üretimi dosyada `sharedStrings` payı ölçülmedi (openpyxl satır içi yazıyor); eşik tahmini.
- Tam süit (3803 / 12 / 0) ve perf kanaryası — usul üyesinde; burada 200 hedefli test.
- Gerçek evrak ölçümü: alt ajan raporu tek gerçek `.xls` (temiz); bu koşum yalnız sentetik düzenek.
- `<ol start>`'ın udf-cli/PDF yolu (K-4) — udf-cli oturumu yok.
- Hukuki norm teyidi gereken yeni kalem yok (N-8).

---

## 5. Commit'lenmemiş işler — karar dışı

Paylaşılan çalışma ağacında BAŞKA oturumun açık işi aynen duruyor (`git status --short`): izlenen
`.claude-plugin/marketplace.json`, `plugins/ortak-avukat/.claude-plugin/plugin.json`, oa-ingest `SKILL.md`
(48/88/91. satır hunk'ları), `references/gizli-talimat-ifsasi.md`, `scripts/gizli_talimat_ifsa.py`, oa-kontrol
`ictihat_muhakeme_denetim.py`, `kunye_ortak.py`, oa-pipeline `oa_hafiza.py`, `tests/test_kaynak_url.py`;
izlenmeyen `references/resmi-kaynaklar.md`, `tests/test_kanal_bagimsiz_metin.py`, `tests/test_teyit_kanali.py`.
Dokunulmadı, değerlendirilmedi; bu rapor yalnız commit'li fark üzerinedir. İfşa scripti incelemesi (N-3) HEAD
nüshasıyla (`git show HEAD:…`) yapıldı, çalışma kopyasıyla değil. `docs/heyet/2026-10-16-2/` bu koşumun
dosyalarıdır (izlenmiyor; orkestra commit'ler).

## 6. Bu raporun kendi kapıları ve temizlik

Rapor geçici worktree'ye kopyalanıp `tests/test_belge_baglantilari.py` ve `tests/test_v0518_metin_hijyeni.py`
ile tarandı; b38 yol desenleri (`test_v0514_vitrin.py:322-329`) izlenmeyen dosyaya uygulanmadığı için aynı üç
desen ve Cf/NBSP sınıfı elle koşuldu; sonuç dönüş mesajında. Geçici worktree `heyet2-tmp-esas`
`git worktree remove --force` ile kaldırıldı; sentetik kitaplar ve düzenek scriptleri depo dışındaydı, silindi.
Paylaşılan ağaçta bu rapor dışında dosya değiştirilmedi; git yazma komutu kullanılmadı.

KARAR ÖNERİSİ: ŞARTLI PUSH · BLOKLAYICI 0 · UYARI 2 · NOT 11

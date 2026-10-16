# Heyet raporu — ESAS üyesi (hukuki yöntem, müvekkil menfaati) — 2026-10-17 · 3. koşum

**Dal:** `denetim/fable-2026-10-15` · **HEAD:** `c94e982` · **Kapsam:** `origin/main..HEAD` (25 commit; 205 dosya,
+8184/−1197). İlk 17 commit ilk iki koşumda denetlendi, kimlikleri değişmedi; yeni olan sekiz commit: `2aaf6ea`,
`d996f62`, `6801ac7`, `66b5d09`, `7764139`, `9e431ac`, `8998e34`, `c94e982`. **Kararın anlamı:** `main`'e
birleştirme (avukat "birleştir ve push et" dedi). **Ölçüm ortamı:** geçici worktree `heyet3-tmp-esas` (detached,
HEAD `c94e982`, varsayılan ayar, `git status --short` 0 satır; iş bitince kaldırıldı) · `py -3.14` (Python 3.14.8) ·
`PYTHONUTF8=1 OA_TEST_UDF_YAZICI=0` · pytest `-p no:cacheprovider`. Sentetik düzenek depo dışında, oturum çalışma
alanında, yalnız kurgu veriyle kuruldu; hiçbir adrese gidilmedi (ağ yok).

Ölçü tektir: bu dal sahaya çıkarsa müvekkil hangi kayıptan korunur, hangi kayba açılır (evrak · süre · doğrulanmamış
bilgi · sır · karşı tarafın gizli tuzağı). Alt ajan raporları BEYAN sayıldı; her iddia diff'te, ağaçta ve geçici
kopyada ölçüldü. Anayasa m.7 gereği kişi, müvekkil, dosya numarası ve mutlak yerel yol yazılmadı. Başarı olasılığı
sayıyla verilmez. Tam süit ve zamanlama kanaryası usul üyesinindir; burada hedefli kapılar koşuldu.

---

## 1. Kapsam

### 1.1 İlk 17 commit — önceki koşumlarda denetlendi (özet; ayrıntı `docs/heyet/2026-10-16/02-esas.md` §1 ve
`docs/heyet/2026-10-16-2/02-esas.md` §1)

| Commit | Parça | Korunan kayıp ekseni | Madde |
|---|---|---|---|
| `52de60f` | kök README (avukatın bekleyen düzeltmeleri) | doğrulanmamış bilgi (anlatım) | m.2, m.6 |
| `d9d358a` | oa-dilekce `md_udf_html.py` `<ol start>` | mahkemeye yanlış bent numarası gitmez | m.4, m.6 |
| `7fcbb22` | ruff/CI lint, `_CF_RE` kaçışla | gizli tuzak (kaynakta görünmez karakter) | m.11 |
| `30495ab` | `aile_dogrula` + `pyproject` sürüm damgası | bayat araç görünür | m.0, m.8 |
| `47bba4d` | metin hijyeni kapısı istisnasız | aynı | m.11 |
| `45a6d2e` | `docs/arsiv/` + bağlantı kapısı | kayıt bütünlüğü | m.5 (ruhu) |
| `cf425d9` | katmanlı README | vitrin dürüstlüğü | m.8 |
| `200dda5` | `.github/SECURITY.md`, PR şablonu | sır (bulgu herkese açık issue'ya yazılmaz) | m.7, m.10 |
| `99ef95f` | kayıtlar | — | m.8 |
| `8a1c882` | eklenti README + `test_eklenti_vitrini` | vitrin sayıları ölçümle | m.8 |
| `934e212` | oa-ingest `belge_guvenlik.py` Excel gizli katmanı | gizli tuzak; damgalı tarih süreye girmez | m.11, m.2, m.6 |
| `08aef92` | kök katalog sayıları ölçümle | vitrin | m.8 |
| `c5f739f` | heyet tanımları + protokol | karar avukatta kalır | m.9 |
| `8be918f` | güvenlik üyesi tanımındaki mutlak yol kaldırıldı | sır/anonimlik | m.7 |
| `47372fc` | 1. koşum kayıtları (yalnız belge) | kayıt | m.8, m.9 |
| `ca37539` | Excel K-1/K-2 (ızgara gezintisi, `xl/` toplamı, tablo stili ZAYIF) | evrak (alım kilitlenmez); m.6 (yanlış ifşa adayı yok) | m.1, m.6, m.11 |
| `61b8e14` | 2. koşum kayıtları; `.gitignore` `.claude/`; taşıma atfı; STATUS tarihi | kayıt; sır (`.claude/` yerel yol taşır) | m.7, m.8 |

### 1.2 Yeni sekiz commit — parça · korunan kayıp ekseni · anayasa maddesi

| Commit | Parça (kanıt) | Müvekkili hangi kayıptan korur | Madde |
|---|---|---|---|
| `2aaf6ea` | oa-ingest `belge_guvenlik.py` +245: nesne tavanları `:165`/`:168`, `_xml_nesne_say` `:2377`, `_xlsx_gizli_sutunlar` `:2394`, `_xlsx_duz_dolgu_mu` `:2423`, arşiv bütünü `:2503`, süre bütçesi `:2727`, `zemin-olculemedi` `:2820`, `_tablo_kalani_denetlenemedi` `:2678`, etiket sınıfı `:2997-3001`; oa-pipeline `okuma_kapisi.py` `guvenlik_etiketi` `:76`; +12 test (3816 → 3828) | gizli tuzak: ZAYIF aralıktaki açık renkli yazı artık sessiz değil, etiket doğru adla; evrak: tavanlar ve süre bütçesi alımı kilitlemez, hata sebepli DENETLENEMEZ; m.2: ZAYIF aralıktaki görünür tarih süre adayı satırında etiketli | m.1, m.6, m.11 |
| `d996f62` | oa-pipeline `pipeline_kayit.py` +212: `_capraz_bosluk_hesapla` önbelleği `:3731-3800`, `_capraz_onbellek_oku` `:3670`, `_capraz_onbellek_yaz` `:3699`; `tests/test_v0519_capraz_onbellek.py` (37); CLAUDE.md değişmez #7; PERFORMANS-STATUS §14 | evrak: çapraz denetim (kopuk/belirsiz) sonucu değişmeden hızlanır; önbellek hatası "temiz" üretemez (fail-closed) | m.1 (mekanik katman, kayıpsız) |
| `6801ac7` | kayıtlar (CHANGELOG, STATUS, oa-pipeline günlüğü, §14.9) | kayıt | m.8 |
| `66b5d09` | birleştirme; künye/OA-SUIT-SAYISI ölçümle | — | m.8 |
| `7764139` | oa-kontrol `kunye_ortak.py` `RESMI_KAYNAKLAR` `:1229-1251`, `resmi_kaynak_mi` `:1255-1275`; `ictihat_muhakeme_denetim.py` [G7] `:929-941`, `:1343-1356`; oa-pipeline `oa_hafiza.py` `GETIR_ARACLARI` `:572`, `URL_ZORUNLU_ARACLAR` `:597`, kapılar `:1267-1284`; `plugin.json` `mcpServers` kaldırıldı; `oa_kurulum.py` adım; `references/resmi-kaynaklar.md`; `tests/test_teyit_kanali.py` (35 sınama); 86 eski test `tests/oa_teyit_kanali.py` yardımcısıyla | doğrulanmamış bilgi: teyit kanıtı sunucu beyanından resmî adres + döküme geçer; adressiz / liste dışı dayanak teslim engeli; sır: eklenti üçüncü taraf uç nokta ilan etmez | m.4, m.5, m.9, m.10 |
| `9e431ac` | 83 dosya (+505/−418) canlı metin — "87 dosya / 290 satır → 0" anma ölçümüdür (test deseni; beyan), commit dosya sayısı değil; ANAYASA m.5 parantezi (iki nüsha); README 5. adım, master prompt 7-8; SECURITY; SOZLUK; `tests/test_kanal_bagimsiz_metin.py` | anlatım kanalla tutarlı; hukuki içerik değişmedi (§2.2 N-4) | m.5, m.8 |
| `8998e34` | kayıtlar (CHANGELOG, STATUS, YOL-HARITASI `oa-kaynak`, dört günlük) | kayıt | m.8 |
| `c94e982` | birleştirme; OA-SUIT-SAYISI 3900 ölçümle | — | m.8 |

Yeni script yok: `git diff --diff-filter=A --name-only origin/main...HEAD` yalnız `tests/` altında 8 dosya →
`test_b37` kapsam borcu doğmaz. Hukuki dayanak dosyalarındaki (`*.json`, playbook, references) tek değişiklik teyit
notlarının kanal adıdır (§2.2 N-4).

### 1.3 Koşulan kapılar (geçici worktree; komut → son satır)

| Komut | Son satır |
|---|---|
| `git worktree add --detach heyet3-tmp-esas HEAD` | `HEAD is now at c94e982 …` · `git status --short` 0 satır |
| pytest küme A — teyit kanalı: `test_teyit_kanali`, `test_kaynak_url`, `test_v0518_mcp_ilan`, `test_ictihat_muhakeme_denetim`, `test_ictihat_muhakeme_coklu_bolum`, `test_v0518_kurulum`, `test_v0518_master_prompt`, `test_oa_hafiza_teyit_damga`, `test_oa_hafiza_arac_guvenlik`, `test_v0585_a1_triyaj`, `test_dilekce_denetim`, `test_teslim_paketi`, `test_v0516_entegrasyon`, `test_kunye_teyit*` (`-q -n auto -m "not perf" -p no:cacheprovider -rs`) | `375 passed, 2 skipped in 18.91s` (2 atlama: udf-cli oturumu yok) |
| pytest küme B — Excel/önbellek/vitrin/hijyen: `test_v0519_capraz_onbellek`, `test_v0519_excel_gizli_katman`, `test_v0518_belge_guvenlik`, `test_v0518_eksikler`, `test_v0511_kit_guvenlik`, `test_v0514_vitrin` (b35/b37/b38), `test_eklenti_vitrini`, `test_belge_baglantilari`, `test_v0518_metin_hijyeni`, `test_kaynak_hijyeni`, `test_kanal_bagimsiz_metin`, `test_okuma_kapisi*` | `283 passed in 20.67s` |
| `aile_dogrula.py plugins/ortak-avukat/skills` | `Denetlenen parça: 20` · `AİLE YAPI DENETİMİ TEMİZ.` |
| `satir_sayaci.py --json` | eklenti 49.531 · test 62.075 · araç 1.752 · beceri 13.338 · kural 957 · toplam 127.653 · `test_sayisi: 3900` |
| anayasa iki nüsha (satır sonu normalize; vitrin başlığı 5 satır hariç; Python karşılaştırması) | `govde ozdes: True` (13.410 karakter) |
| sentetik düzenek A/B (depo dışı; kurgu veri; ağ yok) | §2.1 |

### 1.4 Koruma gevşemesi taraması — altı eksen (bütün üzerinde)

- **Fail-closed → fail-open:** bulunmadı. Teyit: adres yoksa RET (`oa_hafiza.py:1267`), liste yüklenemezse RET
  (`:1277`), liste dışı RET (`:1281`), damgasız GETİR RET, döküm yoksa damga yok (`:1382`), verbatim denetimi
  (`:1476`); [G7] dayanakta TESLİM ENGELİ (`ictihat_muhakeme_denetim.py:932-941`, `:1355`). Önbellek: her adım kendi
  `try`ında, bozuk/yabancı dosya ıska, okunamayan girdide önbellek yok (`pipeline_kayit.py:3770`). Excel: tavan,
  süre bütçesi ve üreteç hatası sebepli DENETLENEMEZ (`belge_guvenlik.py:2503-2522`, `:2727`, `:2678`). Yeni kayıt
  sınıfı `zemin-olculemedi` AGIR dışı (`:173`) → karar UYARI, "temiz" değil.
- **Teyit zinciri (m.5):** içtihat için GÜÇLENDİ (adres zorunlu + [G7]); mevzuat için yarım güçlendi (adres zorunlu,
  döküm zorunlu değil — **E-3**); kanıtın cinsi değişti (sunucu belge metni → `WebFetch` işlenmiş içerik — **E-1**).
  Eski adressiz kayıtlar dayanak olamaz (fail-closed, **N-2**).
- **Müvekkil-aleyhi dış çıktı (m.6):** tek yol ifşa bölümüdür: ZAYIF-kaynaklı talimat tespitinin "KESİN DEĞİL"
  niteleyicisi dış metne geçmiyor (**E-5**). `zemin-olculemedi` kaydı ifşaya girmez (`gizli_talimat_ifsa.py:396`
  yalnız `gizli-talimat` alır).
- **Avukat kararının modele kayması (m.9):** onay bayrakları dokunulmamış; heyet/KARAR metinleri "karar avukatın"
  der; anayasa metnine dokunuş yalnız parantez (**N-1**) ve avukata açıkça sunulmuş (ajan raporu, CHANGELOG).
- **Süre hesabında geç tarih (m.2):** `hesapla_sure.py`, `sure_kurallari.json`, başlangıç kapısı: yalnız yorum/not
  kanal adı değişti; kural, tarih, madde aynen (**N-4**). ZAYIF aralıktaki görünür tarih artık etiketli (**N-6**).
- **Olguda doğaçlama (m.4):** künye/madde/tarih/tutar üretimi yok; Excel değer silmez; vitrin sayıları ölçümle
  (**N-8**). Açık: `WebFetch` dökümünün "tam metin" sayılması (**E-1**) ve `.gov.tr` genel kuralı (**E-3**).

---

## 2. Bulgular

Sayım bu koşumda yeni bulunanları kapsar; önceki koşumlardan açık kalemlerin durumu §2.3'te (sayıma dahil değil).

### 2.1 Teyit kanalı — düzenek ölçümü (depo dışı, kurgu veri)

**A — `resmi_kaynak_mi` (`kunye_ortak.py:1255-1275`):**

| Girdi sınıfı | Sonuç | Yorum |
|---|---|---|
| kullanıcı-bilgisi hilesi (`…gov.tr@evil…`), parça/sorgu içinde alan adı, sondan ekleme (`…gov.tr.sahte…`), Kiril homograf, `file:`/`ftp:`, IPv6, özel içtihat siteleri | False | fail-closed doğru |
| sondaki nokta, büyük harf, `:443`, `http://` (TLS'siz) | True | `http` kabul — **E-3** |
| salt `gov.tr`, e-Devlet, TBMM, bakanlık duyuru sayfası | True | her `.gov.tr` her araç için — **E-3** |
| `hudoc.exec.coe.int` (AİHM kararlarının infazı), ABAD `curia.europa.eu` | False | listede yok; ekleme avukat kararı — **N-10** |
| adres içinde boşluk / satır sonu | True | `teyit` komutu bunları adres alanında önce reddeder; [G7] ayrıştırıcısı `\S+` ister (`ictihat_muhakeme_denetim.py:164`) → sızma yok |

**B — `oa_hafiza.py teyit` ve [G7]:**

| Senaryo | Sonuç |
|---|---|
| S1 `mevzuat_getir` + resmî adres, döküm yok | KABUL; `_oa/teyit/dokum` boş — **E-3** |
| S1b `mevzuat_getir` + bakanlık duyurusu (`.gov.tr`) | KABUL — **E-3** |
| S2 `WebSearch` sorguda TCKN benzeri 11 hane | RET (Layer 0) |
| S2b `WebSearch` sorguda salt esas-no deseni · S2c ad-soyad benzeri | KABUL (bilinen sınır `oa_hafiza.py:698-705`) — **E-2** |
| S3 `WebFetch` mevzuat sayfası, damgasız | RET ("--damga ZORUNLU") — **E-4** |
| S3b `WebFetch` mevzuat sayfası, NOTR damga, künyesiz | RET ("ayrıştırılabilir künye yok") — **E-4** |
| S4 `ictihat_getir` + adres, `--dokum-sinifi` yok | KABUL + UYARI "geriye uyum: ilgili-kisim" (döküm sınıfı beyan) — **E-1** |
| S5 `ictihat_getir` + `http://` resmî adres | KABUL — **E-3** |
| S6 `ictihat_getir` + e-Devlet adresi | KABUL — **E-3** |
| S7 eski (adressiz) muhakeme kaydı dilekçeye dayanak | çıkış 1 · `[G7] … KAYNAK-URL yok … --kaynak-url ile yenileyin` — **N-2** |

### 2.2 Bulgu listesi

### E-1 · UYARI · 3. koşum · `references/resmi-kaynaklar.md:17-18` ("`WebFetch` tam metin"), `oa-ictihat/SKILL.md:22` ("`WebFetch` tam metin (GETİR sınıfı — damga + döküm + `--kaynak-url` zorunlu)"), `README.md:62`, `:136`, `:615-616`; `oa_hafiza.py:572`, `:1382`, `:1476`

**Kanıt.** Eski kanalda GETİR aracı portalın belge metnini araç çıktısı olarak döndürüyordu (sözlükten çıkarılan
`get_bedesten_document_markdown` adı, `7764139` diff'i `oa_hafiza.py:572`). Claude Code'un `WebFetch` aracı, araç
tanımına göre sayfayı çeker, HTML'i markdown'a çevirir ve içeriği verilen istemle küçük bir modelden geçirip o
modelin yanıtını döndürür; ham belge metni değil, işlenmiş yanıt gelir; uzun kararda kısaltma/özetleme olabilir.
Script zinciri dökümün cinsini ayırt edemez: `--ilgili-kisim` verbatim denetimi (`:1476`) döküme karşı yapılır,
döküm ise `WebFetch`'in işlenmiş yanıtıdır; `--dokum-sinifi tam-metin` beyandır (S4). Portalların sayfa davranışı
(betikle çizilen arama, oturum) ağsız ölçülemedi (§4). Vitrin bunu söylemiyor: `README.md:1367` "Dürüst sınırlar —
bu sürümde ölçülmeyenler" hibrit kanalı saymıyor; orkestra raporu "canlı akış sahada sınanmadı" diyor, README
demiyor.

**Müvekkile etkisi.** Doğrulanmamış bilgi ekseni: dilekçeye "birebir alıntı" diye giren cümle, portal metninin
işlenmiş bir yeniden yazımı olabilir; [G6] "karar baştan sona okundu" beyanı işlenmiş metne dayanır. Fail-closed
yollar duruyor (döküm yoksa damga, damga yoksa dilekçe yok; adres liste dışıysa teyit yok) — kapı açılmadı, kanıtın
cinsi değişti ve bu değişim vitrinde yazılı değil.

**Önerilen onarım.** (a) Birleştirmeden ÖNCE metin: `README.md` dürüst sınırlar, `resmi-kaynaklar.md:17` ve
`oa-ictihat/SKILL.md:22`'ye tek cümle — "`WebFetch` işlenmiş içerik döndürür, verbatim garanti etmez; hibrit kanalın
canlı akışı sahada ölçülmedi". (b) Aynı dalda ayrı commit, önce kırmızı test: `WebFetch` kaynaklı kayıtta
`--dokum-sinifi tam-metin` için ek şart (döküm uzunluğu/yapı ölçütü ya da avukat onay bayrağı); kütük satırına araç
izi; [G6] triyajında `WebFetch` dökümü için görünür uyarı. (c) `oa-kaynak` yerel katmanı (yol haritası) ham metni
araç çıktısı olarak geri getirir — tasarım kararı avukatın.

### E-2 · UYARI · 3. koşum · `hooks/hooks.json:29` (PreToolUse matcher `Write|Edit|Bash|PowerShell|SendUserFile`), `references/resmi-kaynaklar.md:18-19` ("sorgu çıkmadan önce Layer 0 süzgeci (`oa-gizlilik`) çalışır"), `oa_hafiza.py:832` (`_layer0_sorgu_tara`), `:1228`, `:706-708`

**Kanıt.** Hook ağı `WebFetch`/`WebSearch` çağrılarını sarmıyor (matcher'da yok; `origin/main` ile aynı satır —
eski MCP araçları da sarılmıyordu). Mekanik Layer 0 yalnız `oa_hafiza.py teyit --sorgu` üzerinde ve çağrıdan SONRA
(kütük kaydı anında) çalışır: S2 TCKN yakalandı; S2b salt esas no ve S2c ad-soyad yakalanmadı (bilinen sınır,
`:698-705`). Fark: eski kanalda sorgu sözleşmeli bir hukuk servisine gidiyordu; şimdi `WebSearch` ile genel bir
arama motoruna gider. `README.md:1163-1166` "dış araca (bulut MCP/web) veri çıkışı Layer 0'a tabidir" diyor —
talimat düzeyinde doğru, mekanik düzeyde değil; `resmi-kaynaklar.md:18` "çalışır" diyerek mekanik ima ediyor.

**Müvekkile etkisi.** Sır ekseni: model disiplini bozulursa (uzun oturum, alt-ajan) müvekkil tanımlayıcı sorgu
arama motoruna gider; sonradan kütük RET'i çıkışı geri almaz. Talimat düzeyinde koruma (Av.K. m.36, m.10) duruyor;
mekanik güvence yok ve belge mekanik güvence varmış gibi okunuyor.

**Önerilen onarım.** Aynı dalda ayrı commit, önce kırmızı test: `hooks.json` PreToolUse matcher'a
`WebFetch|WebSearch`; `hook_pretool` bu araçlarda `tool_input` alanlarını (`url`, `query`, `prompt`)
`gizlilik_tara.py` strict kipinden geçirir (deny/ask). Onarıma kadar `resmi-kaynaklar.md:18` cümlesi "model,
sorguyu göndermeden önce `oa-gizlilik` süzgecinden geçirir (talimat; mekanik kapı yol haritasında)" diye düzeltilir.

### E-3 · UYARI · 3. koşum · `kunye_ortak.py:1270` (`.gov.tr` soneki her alan adı), `:1229-1251` (`tur` alanı var, kullanılmıyor), `oa_hafiza.py:597`, `:1267-1284` (yalnız varlık + liste), `:1382` (döküm yalnız `--damga` ile zorunlu); `resmi-kaynaklar.md:10-11` ("iki şeyle kanıtlanır: resmî portalın adresi ve diske inmiş tam metin")

**Kanıt.** S1: `mevzuat_getir` adresle, dökümsüz KABUL (döküm dosyası 0) — madde için "tam metin diske iner" kuralı
kodda yok. S1b: bakanlık duyuru sayfası (`.gov.tr`) `mevzuat_getir` için kabul. S6: e-Devlet adresi `ictihat_getir`
için kabul. S5: `http://` kabul. Listedeki `tur` (mevzuat / içtihat / kurum / tarife / aihm) araç sınıfıyla
eşlenmiyor.

**Müvekkile etkisi.** Doğrulanmamış bilgi: "resmî metin" diye kütüğe giren madde bir kurumun özet/duyuru
sayfasından okunmuş olabilir; madde metni diske inmediği için sonradan karşılaştırma yok. Eski kanala göre gerileme
yok (adres hiç yoktu); belge kodun önündedir (vitrin).

**Önerilen onarım.** Ayrı commit, önce kırmızı test: `mevzuat_getir`/`resmi_gazete_getir` için adres
`tur ∈ {mevzuat, resmi-gazete}` ya da avukat onayı; içtihat GETİR için `tur ∈ {ictihat, aihm, kurum}`; genel
`.gov.tr` kuralı `kurum` sınıfına; mevzuat kayıtlarında `--dokum-icerik` zorunlu (madde metni diske) — ya da
`resmi-kaynaklar.md:10` "madde için adres yeter" diye dürüstleştirilir; `https` şartı.

### E-4 · UYARI · 3. koşum · parça bütünlüğü (SKILL ↔ script): `oa-kontrol/SKILL.md` ve `oa-kontrol/README.md`'de "[G7]" ve "kaynak-url" 0 geçiş (grep) — kapı `ictihat_muhakeme_denetim.py:929-1356`'da; `oa-ictihat/SKILL.md:155-156`; `ictihat-muhakeme-sablonu.md:252`; `oa-ictihat/SKILL.md:142`; düzenek S3/S3b

**Kanıt.** (i) [G7] kapısının sahibi oa-kontrol'dür; SKILL.md ve README'si kapıyı anmıyor. (ii) `oa-ictihat/SKILL.md:155`
GETİR ritüeli "`ictihat_getir`/`kurum_karari_getir`" sayıyor, `WebFetch` yok; `:156` tek-komut örneğinde
`--kaynak-url` yok (aynı dosya `:22` ve `:173` doğru) — örneği izleyen model RET alır. (iii) Şablon `:252`
"KAYNAK-URL varsa onun altında" der; [G7] "yoksa engel" der. (iv) `:142` "Sağlık: Pro'da ayrı sağlık aracı yok —
`legal_research_guide`": eski kanal artığı; araç adı `oa_hafiza.py` sözlüğünden çıkarıldı (`7764139` diff
`MEVZUAT_KURUM_ARACLARI`). (v) S3/S3b: `WebFetch` ile çekilen mevzuat sayfası kütüğe işlenemiyor (damgasız RET;
damgalı künyesiz RET) → model ya `--arac mevzuat_getir` yazar (fiilen `WebFetch` kullandı — m.8 araç+sorgu+sonuç
sadakati) ya da kayıt düşmez.

**Müvekkile etkisi.** İş durur (fail-closed RET), kayıt sadakati zayıflar; dış çıktıya yanlış bilgi gitmez.

**Önerilen onarım.** Metinler: oa-kontrol SKILL/README'ye [G7]; `:155-156` ritüele `WebFetch` ve `--kaynak-url`;
şablon `:252` "zorunlu"; `:142` artığı. Kod: `WebFetch` için mevzuat/RG sınıfı (adresin `tur`üne göre sınıflama —
E-3 ile aynı commit).

### E-5 · UYARI · 3. koşum · `gizli_talimat_ifsa.py:313-399` (`_yontem_aciklama`), `:414` (`_konum_aciklama`); kaynakta "KESİN DEĞİL" ve "zemini ölçülemeyen" 0 geçiş; `belge_guvenlik.py:2641`, `:2798`

**Kanıt (ölçüm).** ZAYIF-kaynaklı `gizli-talimat` kaydının yöntem metni ("…açık renkli yazıda … talimat dili — gizli
olduğu KESİN DEĞİL; Excel'de açıp bakın") ifşa çevirisinde "açık renkli yazı; metin, belgeyi otomatik işleyen
yazılımlara yönelik yönerge kalıbı içermektedir" olur; konum "«zemini ölçülemeyen aralık»". Niteleyici düşer; tespit
ifşa bölümünün "gizli katman" çerçevesinde sunulur.

**Müvekkile etkisi.** m.4/m.6, dış çıktı: tablo stili aralığında açık renkli ve talimat benzeri dil taşıyan GÖRÜNÜR
bir hücre mahkemeye gizlenmiş gibi anlatılabilir; karşı taraf hücrenin görünür olduğunu gösterir, HMK m.29 iddiası
boşa çıkar ve müvekkilin dürüstlüğü sorgulanır. Dar: talimat dili + açık renk + tablo stili / koşullu biçim aralığı;
ifşa bölümünü koyma kararı avukatın; iç not niteleyiciyi taşır. Orkestra raporu kalemi "açık" diye kaydetmiş.

**Önerilen onarım.** Ayrı commit, önce kırmızı test: `_yontem_aciklama`'da "KESİN DEĞİL"/"zemini ölçülemeyen"
kalıbı → "zemini ölçülemeyen tablo stili / koşullu biçim aralığında açık renkli yazı — gizli olduğu kesin değildir,
orijinalde denetlenmelidir"; bu sınıf varsayılan olarak ifşa gövdesine değil iç nota düşer. Onarıma kadar
ZAYIF-kaynaklı tespitler ifşa taslağında avukat eliyle süzülür.

### N-1 · NOT · 3. koşum · Anayasa m.5 parantezi — içerik kaybı yok; iki nüsha özdeş; kalan MCP atıfları avukat kararı

`ANAYASA.md:108` ↔ `references/anayasa.md` gövdesi özdeş (ölçüm §1.3; `aile_dogrula` TEMİZ). Değişen yalnız
parantez (eski: üçüncü taraf sunucu adı / Mevzuat MCP; yeni: "resmî kaynak beyaz listesi: içtihat portalları /
mevzuat.gov.tr"); cümle, kural ve madde numarası aynen. Kalan MCP atıfları: `:104` m.4 "daima MCP/resmî kaynaktan",
`:111` "MCP'de bulunamadı", `:114` "norm (Mevzuat MCP) → içtihat (Yargı/AYM MCP)", `:166` m.9 "MCP aktifliği
ön-koşulu", `:172` m.10 "bulut MCP". Kodda "MCP aktif" ön-koşulu yok (grep 0); eklenti MCP ilan etmezken anayasanın
MCP katmanını anması çelişki değil (bağlamda araç varsa aynı disiplinle kullanılır — `oa-ictihat/SKILL.md:22`), ama
m.9 ön-koşulu artık tanımsız. Anayasa avukatın belgesidir; öneri: "MCP aktifliği" → "teyit kanalına erişim" — karar
avukatın.

### N-2 · NOT · 3. koşum · Eski kütük kayıtları — [G7] engeli fail-closed; avukata yönelik geçiş notu eksik

S7: adressiz eski kayıt dayanaksa çıkış 1 ve mesaj onarım yolunu söyler. Bedel: devam eden dosyalarda dilekçe öncesi
her dayanak kararın resmî portaldan yeniden çekilmesi (m.5 ile uyumlu, kayıp değil). `oa-ictihat/SKILL.md:29` modele
söylüyor; `README.md` "Güncelleyenin yapacakları" (`:1333-1366`) avukata söylemiyor. Öneri: tek madde.

### N-3 · NOT · 3. koşum · `STATUS.md:3` — "dal `denetim/fable-2026-10-15` push edilmedi" bayat

Dal push edildi ve PR #9 açık (orkestra raporu, devir notu; yerel `origin/denetim/fable-2026-10-15` izleme dalı `c94e982`). Tek satırlık vitrin
düzeltmesi; birleştirmeden önce (§3 Ş-2).

### N-4 · NOT · 3. koşum · Hukuki dayanak — değişen yalnız teyit notlarının kanal adı; madde, tarih, etiket aynen

`git show 9e431ac`: `sure_kurallari.json:632`, `:645` (`adli_tatil_dayanak`: "üçüncü taraf `ictihat_ara`" →
"resmî içtihat portalı `ictihat_ara`"; madde, künye, tarih 2026-10-07 ve "TEYİT BEKLİYOR" etiketi aynen);
`tarife.json` `_aciklama` (fikir kaynağı adı); `hesapla_sure.py` yorumları; `dilekce_denetim.py` yorumları (İİK
m.16/1, TTK m.4/1-a, m.776, İİK m.170/a-3, HMK m.127, m.317/2 — "resmî metin (mevzuat.gov.tr), 2026-10-05");
`kunye_teyit.py` yorumları; references (icra ailesi, idari-ceza, bireysel başvuru, meslek kuralları, illiyet
doktrini, gizli-talimat ifşası §6). Hiçbir madde numarası, süre, oran ya da tarife kalemi değişmedi. Teyit izi:
kaynak (mevzuat.gov.tr) + tarih + araç adı korunmuş; kanalın üçüncü taraf aracı olduğu bilgisi düştü — tarihçe
CHANGELOG'da. Yeni "TEYİT BEKLİYOR" yok; önceden var olanlar (`sure_kurallari.json:286`, `:538`, `:551`, `:619`,
`:632`, `:645`, `:658`) aynen ve TEMKİNLİ (erken tarih) kuralıyla işleniyor → BLOKLAYICI doğmaz; §4'te listeli.
`uyap-belge-formatlari.md` kaynak atfı ürün adından "udf-cli geliştiricisinin rehberi"ne — aynı geliştirici
(README emek etiketi); olgu değişmedi.

### N-5 · NOT · 3. koşum · Çapraz önbellek — fail-closed yapı kodda ve testte doğrulandı; gizlilik sınırı aynı

`pipeline_kayit.py:3731-3800`: girdi bir kez bayt olarak okunur, okunamayan → `okunamayan=True` → anahtar yok
(`:3770`); anahtar/okuma/yazma ayrı `try`; `_capraz_onbellek_oku:3670` başlık anahtarı + gövde sha256 + yapı
denetimi → aksi None; `_capraz_onbellek_yaz:3699` `_oa/defter` yoksa yazmaz (`:3706`), JSON gidiş-dönüşü
(`:3713`), tmp + `os.replace`; dedup bağışıklığı `:4995`. 37 test yeşil (küme B);
`test_DURUM_md_ve_denetle_ciktisi_onbellekli_onbelleksiz_BIREBIR` "v0.5.18 ile birebir" iddiasını,
`test_onbellek_kodu_cokerse_sonuc_yine_dogru` fail-closed'ı kilitler. `CLAUDE.md:238-256` değişmez #7 metni kodla
örtüşür. Gizlilik: `.capraz-onbellek.json` kopuk/belirsiz kayıtları (evrak ve vakıa kimlikleri — müvekkil verisi)
taşır; `_oa/defter` altında, `.gitignore` `_oa/` ve `**/_oa/` kapsar; güven sınırı defterle aynı (docstring).
Mutasyon kanıtı (21/21) alt oturum beyanıdır, yinelenmedi.

### N-6 · NOT · 3. koşum · Excel — 2. koşum E-5 ve N-3 kapandı; K-3 etiketleri avukata doğru adla görünür

`belge_guvenlik.py:2820` `zemin-olculemedi` (AGIR dışı `:173` → UYARI; damga yok); `:2798` ve `:2641` "KESİN
DEĞİL" metni (iç kayıt); `_xlsx_duz_dolgu_mu:2423` — 2. koşum t6 sınıfı (hücrenin kendi düz dolgusu) artık
ölçülür; ifşa yalnız `gizli-talimat` alır (`gizli_talimat_ifsa.py:396`) → `zemin-olculemedi` ifşa bölümüne girmez
(m.6). K-3: `UYARI_ETIKETLERI:2998`, `_uyari_sinifi:3001`, `okuma_kapisi.guvenlik_etiketi:76`; süre adayı satırına
etiket (`:364`) → ZAYIF aralıktaki görünür tarih (2. koşum t5) okuma listesinde ve süre adayı satırında
`🛡ZEMİN-ÖLÇÜLEMEDİ` ile görünür (m.2 bildirimi). Öncelik gizli > zemin > talimat: aynı sayfada gizli satır ve
görünür talimat dili varsa etiket yalnız gizli katmanı söyler; bulgular listesinde ikisi de var — bilgi.
K-14 (`:2678`): sebep `R.denetlenemedi`ye yazılır → karar DENETLENEMEZ, "temiz" değil; işlenmiş sayfa damgaları
durur.

### N-7 · NOT · 3. koşum · 2. koşum E-7 kapanışı (nesne tavanları) — büyük meşru döküm sebepli DENETLENEMEZ olabilir (tahmin)

`:165` 1.000.000 `<c `, `:168` 500.000 `<row `; `_xml_nesne_say:2377` kitabı yüklemeden akışla sayar; tüm
sayfaların toplamı; aşımda sebepli `_TabloOlculemedi` (kitap belleğe alınmaz). `tahmin:` (gerçek döküm yok) 10-15
sütunlu HTS/banka dökümü 70-100 bin satırı aşınca ~1 M hücreye ulaşır ve DENETLENEMEZ olur; yıllık yoğun hat HTS'si
bu sınıfa girebilir. Sonuç fail-closed ve görünür: okuyucu metni yine gelir, avukat "DENETLENEMEZ — temiz sayılmaz"
uyarısını görür; sessiz geçiş yok. `README.md:1380-1395` dürüst sınır nesne tavanını saymıyor (CHANGELOG sayıyor) —
tek cümle önerisi. Bayt tavanı (`:157`) ayrıca duruyor.

### N-8 · NOT · 3. koşum · Vitrin sayıları ve iddiaları ölçümle birebir; `test_b37` borcu yok

`satir_sayaci --json` ↔ `README.md:22` ve eklenti README `:7`: 49.531 → "49.000+", 62.075 → "62.000+", 1.752 →
"1.700+", 13.338 → "13.000+", 957 → "900+", 127.653 → "127.000+", 3.900 test; `tests/README.md:3` 3900 = toplanan
(b35 yeşil). "beyaz liste; üçüncü taraf sunucu yok" (`marketplace.json`) ↔ `plugin.json` `mcpServers` yok
(`test_teyit_kanali.py:283`). YOL-HARITASI `oa-kaynak` kalemi "kurulmadı; karar avukatın" — dürüst. SOZLUK yeni
terim kodla uyumlu. Yeni motor yok → `test_b37` kapsam borcu yok.

### N-9 · NOT · 3. koşum · Test uyarlamaları koruma gevşetmedi

`tests/oa_teyit_kanali.py:23-36`: yardımcı yalnız `teyit` çağrısında, `--kaynak-url` yokken ve araç URL_ZORUNLU
sınıfındayken sentetik adres ekler; başka RET sebepleri etkilenmez; kapının kendisi `test_teyit_kanali.py`'de ayrı.
`test_kaynak_url.py:69-80` tersine çevrildi (eski: URL'siz GETİR kabul; yeni: RET ve kayıt yok) — gerekçe docstring'de,
yeni sözleşme daha sıkı. `test_v0518_mcp_ilan.py` 6 → 4: "tek izinli sunucu" → `IZINLI = {}` (`:34`, `:44`);
"sözlükte yedek adlar" → `test_arac_sozlugu_ucuncu_taraf_mcp_adlari_tasimaz`; B-23'ün üç testi duruyor (`:52`,
`:69`, `:77`). `test_v0518_master_prompt`: "geliştirici parçası" kilidi düştü, emek etiketi kilidi sürüyor (kişi adı
ve bağlantı README 5. adımda korunmuş; ürün adı anılmıyor — alt oturumun avukata sorusu 1).

### N-10 · NOT · 3. koşum · Beyaz liste kenar durumları (§2.1 A) — hile desenleri reddediliyor; iki meşru kaynak listede değil

Reddedilenler doğru. `hudoc.exec.coe.int` (AİHM kararlarının infazı) ve ABAD listede değil — nadir, ekleme
`resmi-kaynaklar.md` "Listeyi değiştirmek" kuralıyla avukat kararı. Boşluklu/satır sonlu adres `resmi_kaynak_mi`
düzeyinde kabul; `teyit` komutu adres alanında önce reddeder, [G7] ayrıştırıcısı `\S+` ister → sızma yok.

### N-11 · NOT · 3. koşum · Alt ajan raporları ↔ ağaç

`2aaf6ea` 14 dosya +536/−69 ✓ (stat); `d996f62` `pipeline_kayit.py` +212 ✓; `7764139` 26 dosya ✓; `9e431ac` 83 dosya
(+505/−418) — "87 dosya / 290 satır" anma ölçümüdür, commit dosya sayısı değil (iki sayı farklı şeyi sayar); OA-SUIT-SAYISI 3900 ✓; anayasa iki nüsha özdeş ✓ (ölçüm); `plugin.json` `mcpServers`
yok ✓; `oa_kurulum.py` `teyit_kanali` adımı BİLGİ ✓. "290 satır" ilk ölçüm beyanıdır (eski ağaçta yinelenmedi);
"3887 geçti · 12 atlandı" tam süit usul üyesinde.

### N-12 · NOT · 3. koşum · Araç çantası kopyasında beyaz liste

`oa_hafiza.py:1056` çanta kopyasında kardeş `kunye_ortak.py` aranır; yoksa `:1277` RET "beyaz listesi yüklenemedi —
FAIL-CLOSED" → kapı kapanır, açılmaz. Çanta kurucusunun `kunye_ortak.py`'yi kopyaladığı bu koşumda doğrulanmadı (§4).

### 2.3 Önceki koşumlardan kalan kalemler (sayıma dahil değil)

| Kalem | Durum (HEAD `c94e982`) | Kanıt |
|---|---|---|
| K-3 (1. koşum E-3 etiket) | **KAPANDI** | `2aaf6ea`; N-6 |
| K-4 (1. koşum E-4 `<ol start>`) | cümle sınırı kondu; udf-cli ölçümü AÇIK | CHANGELOG, DENETIM B-1 satırı |
| K-5 (taşıma atfı) · K-7 (`.gitignore`) | **KAPANDI** | `61b8e14`; `.gitignore` son blok |
| K-10 … K-15 (2. koşum E-5, E-7, N-2, N-3; GÜV N-1 … N-4; USUL N-1) | **KAPANDI** | `2aaf6ea`; N-6, N-7 |
| K-16 (ifşa iç notu cümlesi) | AÇIK → bu koşum **E-5** | `gizli_talimat_ifsa.py:313-399` |
| 2. koşum N-4 (pivot stili) · `.xls` tablo stili · kapı `SURUM` 1.2 | AÇIK (orkestra kaydı; avukat kararı) | CHANGELOG üçüncü tur maddesi |
| 1. koşum N-4 (eklenti README Excel) | **KAPANDI** | eklenti README oa-ingest satırı |
| USUL N-3 (STATUS tarihi) | tarih güncel; "push edilmedi" bayat → **N-3** | `STATUS.md:3` |

---

## 3. Karar önerisi

**ŞARTLI PUSH** (`main`'e birleştirme). BLOKLAYICI yok: hiçbir kapı fail-open'a dönmedi; içtihat teyit zinciri
`origin/main`'e göre güçlendi (adres zorunlu, [G7], ilan yok); avukat kararı modele kaymadı; süre kuralı ve hukuki
dayanak değişmedi; olgu üretilmedi; Excel ve önbellek kapıları fail-closed ve testli. Beş UYARI'nın ortak noktası
şudur: yeni kanalın kanıtı eskisinden farklı cinstendir (işlenmiş web içeriği, genel arama motoru, her `.gov.tr`) ve
vitrin bu farkı henüz söylemiyor; mekanik kapılar talimatın gerisinde. Müvekkil bu dalla her eksende `main`'den daha
iyi korunur; eksik olan dürüst sınır ve iki küçük mekanik kapıdır.

**Birleştirmeden ÖNCE (dakikalık metin işleri):**
- **Ş-1 (E-1):** `README.md` dürüst sınırlar + `resmi-kaynaklar.md:17` + `oa-ictihat/SKILL.md:22`'ye "`WebFetch`
  işlenmiş içerik döndürür, verbatim garanti etmez; hibrit kanalın canlı akışı sahada ölçülmedi" cümlesi; `README.md`
  dürüst sınırlara nesne tavanı (N-7) tek cümle.
- **Ş-2 (N-3):** `STATUS.md:3` "push edilmedi" → push ve PR #9 kaydı.

**Aynı dalda ayrı commit (birleştirmeden sonra ilk iş olabilir; her biri önce kırmızı test, OA-SUIT-SAYISI ve
günlük):**
- **Ş-3 (E-1):** `WebFetch` kaynaklı kayıtta `tam-metin` sınıfı için ek şart; kütükte araç izi; [G6] uyarısı.
- **Ş-4 (E-2):** PreToolUse matcher'a `WebFetch|WebSearch` + `gizlilik_tara` strict; `resmi-kaynaklar.md:18`
  cümlesi.
- **Ş-5 (E-3 + E-4 kod):** araç sınıfı ↔ `tur` eşlemesi; mevzuat kayıtlarında döküm; `https`; `WebFetch` için
  mevzuat/RG sınıfı.
- **Ş-6 (E-4 metin):** oa-kontrol SKILL/README [G7]; oa-ictihat `:155-156`, `:142`; şablon `:252`.
- **Ş-7 (E-5):** ifşa çevirisinde "kesin değil" niteleyicisi; ZAYIF sınıfı varsayılan iç not.
- **Ş-8 (N-2):** README güncelleme notlarına "eski teyit kayıtları dilekçe öncesi yenilenir" maddesi.

**Avukat kararı gerektirenler (heyet karar vermez):** N-1 (anayasa m.4/m.5/m.9/m.10'daki MCP ifadeleri), N-10
(listeye `hudoc.exec.coe.int` / ABAD), `oa-kaynak` yerel katmanının önceliği, kapı `SURUM` 1.2, emek etiketi
lafzı, sürüm numarası.

---

## 4. Doğrulanamayanlar (resmî kaynak teyidi ya da saha ölçümü gerektirir)

- Hibrit kanalın canlı akışı: `WebFetch`'in resmî portallardan (betikle çizilen arama sayfaları, oturum, uzun karar
  metni) ne döndürdüğü; dökümün verbatim payı; `WebSearch` keşfinin resmî alan adlarıyla sınırlanabilirliği —
  bu koşumda ağ yok, hiçbir portala gidilmedi.
- Layer 0'ın `WebSearch`/`WebFetch` çağrılarına fiilen uygulanıp uygulanmadığı (talimat düzeyi; mekanik kapı yok).
- "87 dosya / 290 satır" ilk ölçümü (eski ağaçta yinelenmedi); tam süit (3887 / 12 / 0), zamanlama kanaryası ve CI
  (PR #9) — usul üyesi / ağ.
- N-7 tavan tahmini (1 M hücre) gerçek HTS/banka dökümüyle ölçülmedi.
- Araç çantası kurucusunun `kunye_ortak.py`'yi kopyaladığı (N-12).
- Önceden var olan "TEYİT BEKLİYOR" kalemleri — bu dalda değişmedi, resmî teyit avukat ya da oa-ictihat işidir:
  `sure_kurallari.json:632` (HMK m.82/1 süresine HMK m.104 uygulanırlığı), `:645` (Av.K. m.41 süresi), `:619`
  (HMK m.397/1), `:538`/`:551` (İİK m.347 şikâyet süresi), `:286`/`:658` (6216 s.K. ve AYM İçtüzüğünde adli tatil);
  hepsi TEMKİNLİ (erken tarih) kuralıyla işleniyor.
- `.xls` tablo stili ve pivot stili (2. koşum; düzenek kurulamadı).
- Mutasyon kanıtları (önbellek 21/21; Excel "önce kırmızı") alt oturum beyanıdır.

---

## 5. Commit'lenmemiş işler — karar dışı

Koşum başında `git status --short` yalnız `?? docs/heyet/2026-10-17/` (bu koşumun dosyaları) gösteriyordu; rapor yazılırken
paylaşılan ağaçta BAŞKA oturumun açık işi belirdi: ` M tests/test_teyit_kanali.py` (+40) ve ` M tests/test_v0519_excel_gizli_katman.py`
(+49; yalnız ekleme). Dokunulmadı, okunmadı, değerlendirilmedi; bu rapor yalnız commit'li fark (`c94e982`) üzerinedir ve
ölçümler bu değişiklikten önce, geçici kopyada alındı. Orkestra commit'lerse ayrı koşum gerekir (`test_b35` OA-SUIT-SAYISI,
kapsam). `docs/heyet/2026-10-17/` bu koşumun dosyalarıdır (izlenmiyor; orkestra commit'ler).

## 6. Bu raporun kendi kapıları ve temizlik

Rapor geçici worktree'ye kopyalanıp `tests/test_belge_baglantilari.py` ve `tests/test_v0518_metin_hijyeni.py` ile
tarandı; b38 yol desenleri (`tests/test_v0514_vitrin.py:322-329`) izlenmeyen dosyaya uygulanmadığı için üç desen,
Cf/NBSP sınıfı ve `test_kanal_bagimsiz_metin` deseni elle koşuldu; sonuç dönüş mesajında. Geçici worktree
`heyet3-tmp-esas` `git worktree remove --force` ile kaldırıldı; sentetik düzenek depo dışındaydı, kurgu kökleri
silindi. Paylaşılan ağaçta bu rapor dışında dosya değiştirilmedi; git yazma komutu kullanılmadı; ağa çıkılmadı.

KARAR ÖNERİSİ: ŞARTLI PUSH · BLOKLAYICI 0 · UYARI 5 · NOT 12

# KARAR MATERYALİ — heyet üçüncü koşumu 2026-10-17 (main'e birleştirme öncesi bütün)

**Dal:** `denetim/fable-2026-10-15` · **Denetlenen HEAD:** `c94e982` (üçüncü koşum) · **Onarım turu (tur 4):** `d6e5550` ·
**Taban:** `origin/main` = `753e48c` (v0.6.0) · **Kapsam:** `origin/main..c94e982` — 25 commit; ilk 17'si ilk iki koşumda
denetlendi, bu koşumun yeni sekiz commit'i `d996f62`, `6801ac7`, `2aaf6ea`, `66b5d09`, `7764139`, `9e431ac`, `8998e34`,
`c94e982` (iki birleştirme dahil); `origin/main...d6e5550`: 26 commit, 212 dosya, +9455/−1197 · **Push:** dal 2026-10-16'da
avukat kararıyla push edildi; PR #9 (main'e) açık. Heyet karar vermez, karar materyali üretir (anayasa m.9); birleştirme
avukatın kararıyla.

**Niteliği.** Aynı dal için üçüncü koşum; konusu `main`'e birleştirilecek bütündür. İlk koşum
([../2026-10-16/KARAR.md](../2026-10-16/KARAR.md), HEAD `8be918f`) ve ikinci koşum
([../2026-10-16-2/KARAR.md](../2026-10-16-2/KARAR.md), HEAD `ca37539`) sonrası avukat kararları: dal push edildi, PR #9
açıldı; "0.6'yı geliştir"; "bekleyen PR dallarını ve bekleyen commit'leri incele, geliştir, push et; sistem bir ahenk
içinde çalışsın". Bu kararlarla dala giren iş: Excel kapısı üçüncü onarım turu (`2aaf6ea`: K-3, K-10 … K-15), v0.5.19
adayı çapraz denetim sonuç önbelleği (`d996f62`, `6801ac7`; `66b5d09` ile birleşti), hibrit teyit kanalı (`7764139`,
`9e431ac`, `8998e34`; PR #10 denetim dalına hızlı ileri alındı, `c94e982`). Üç üye aynı anda çağrıldı; her biri kapılarını
varsayılan ayarla açılmış kendi geçici worktree'sinde koşturdu ve kopyasını kaldırdı. Alt ajan raporları
([ajan-raporlari/00-INDEX.md](ajan-raporlari/00-INDEX.md)) beyan sayıldı, ağaçta ölçüldü (USUL §1.7: 15 iddiada 1
ayrışma — U-2; 2'si yalnız kısmen yinelenebildi). Üç üyenin "birleştirmeden önce" dediği şartlar orkestra tarafından tur 4'te
(`d6e5550`) kapatıldı; bu kayıt commit'i KARAR-3'ü, hukuki yöntem öneri raporunu ve kayıt satırlarını ekler; tur 4'ün kodu
heyetin görmediği kod olduğundan birleştirmeden önce üç üye yalnız fark üzerinde şart kapanışını doğrular (§7, §8).

**Karar kuralı** (protokol m.3, [../README.md](../README.md)): tek BLOKLAYICI bile varsa PUSH ETME; üçü de PUSH diyorsa
PUSH; ŞARTLI PUSH şartları birleştirilir, her şart bir onarım kalemi olur.

## 1. Üç öneri yan yana

| Üye | Rapor | Öneri | BLOKLAYICI | UYARI | NOT | Kendi koşturduğu ana kapılar (son satır) |
|---|---|---|---|---|---|---|
| USUL | [01-usul.md](01-usul.md) | ŞARTLI PUSH | 0 | 2 | 8 | tam süit `3887 passed, 12 skipped in 103.65s` · perf `1 passed` · toplanan 3900 = OA-SUIT-SAYISI · aile `TEMİZ` (20) · ruff `All checks passed!` · künye `--yaz` güncel ×2, `--json` 49.531 / 62.075 / 3900 birebir · `hook_doktor --kurulu` ✓ · PR #9 `MERGEABLE / CLEAN`, 18/18 CI · PR #10 `MERGED` · iki birleştirmenin çatışma kümeleri `merge-tree` ile mesajlarla birebir · "önce kırmızı" iki motorda yeniden üretildi (önbellek `36 failed, 1 passed` → 37; Excel `12 failed` → `12 passed`) · 8 commit'in kayıtları tam · anayasa iki nüsha özdeş |
| ESAS | [02-esas.md](02-esas.md) | ŞARTLI PUSH | 0 | 5 | 12 | küme A (teyit kanalı, 14 dosya) `375 passed, 2 skipped` · küme B (Excel / önbellek / vitrin / hijyen) `283 passed` · aile `TEMİZ` · anayasa gövdesi özdeş (13.410 karakter) · depo dışı kurgu düzenek: `resmi_kaynak_mi` 5 girdi sınıfı, `teyit` + [G7] 7 senaryo · altı eksende koruma gevşemesi taraması: fail-open 0 · hukuki dayanak değişmedi, yeni TEYİT BEKLİYOR yok |
| GÜVENLİK | [03-guvenlik.md](03-guvenlik.md) | ŞARTLI PUSH | 0 | 2 | 5 | `-U0` eklenen 2706 satırda sır deseni 0 (TCKN / IBAN / telefon / e-posta / yol / token / Cf) · b38 `3 passed` · hijyen `7 passed` · ruff temiz · güvenlik seti `356 passed` · teslim zinciri / sürüm kilidi / bağlantı / vitrin `133 passed` · 41 düşmanca adres vakası beklenen dışı 0 · nesne sayacı deneyi 4 XML yazımı × 5.000 hücre + 100 k / 300 k ölçek · Layer 0 deneyi (`--sorgu` ↔ `--kaynak-url`) · `hooks/`, CI, bağımlılık, sürüm dosyaları değişmedi; `plugin.json` yalnız `mcpServers` kaldırma |
| **Bütün** | | **ŞARTLI PUSH** | **0** | **9** | **25** | |

## 2. Bütünleşik sonuç

**Heyet önerisi: ŞARTLI PUSH** (anlam: `main`'e birleştirme). BLOKLAYICI yok: HEAD'in temiz kopyasında altı kapının altısı
yeşil; PR #9 CI 18/18; hiçbir kapı fail-open'a dönmedi; içtihat teyit zinciri `origin/main`'e göre güçlendi (adres zorunlu,
[G7], üçüncü taraf ilanı yok); Layer 0'da mevcut bir denetim gevşetilmedi; süre kuralı ve hukuki dayanak değişmedi; olgu
üretilmedi; Excel ve önbellek kapıları fail-closed ve testli; sır sızıntısı 0. Dokuz UYARI'nın ortak noktası: yeni kanalın
kanıtı eskisinden farklı cinstendir (işlenmiş web içeriği, genel arama motoru, her `.gov.tr`) ve vitrin bu farkı
söylemiyordu; iki mekanik kapı talimatın gerisindeydi (nesne sayacı atlatılabiliyor, zorunlu adres Layer 0'dan geçmiyor);
üç kayıt bayattı. Müvekkil bu dalla her eksende `main`'den daha iyi korunur; eksik olan dürüst sınır ve küçük mekanik
kapılardır.

Birleşik şartların zamanlaması ve durumu:

- **Birleştirmeden ÖNCE — kapatıldı: tur 4 (`d6e5550`), önce kırmızı testle.**
  - GÜVENLİK U-1 (H3-1): nesne sayacı etiket dilbilgisine bağlandı (`belge_guvenlik.py` `_XML_HUCRE_RE` /
    `_XML_SATIR_RE`: `<` + isteğe bağlı ad alanı öneki + `c`/`row` + boşluk, `/` ya da `>`; parça kuyruğu 128 bayt).
    Önce kırmızı: `test_xlsx_hucre_tavani_xml_yazim_varyantlarini_da_sayar` (öznitelliksiz / satır sonlu / önekli) +
    `test_xlsx_satir_tavani_satir_sonlu_ve_onekli_row_etiketini_de_sayar` — öznitelliksiz varyant ilk yazımda kırmızı
    olmadı (openpyxl sayı hücresine `t="n"` yazıyor, dönüşüm `<c` üretmiyordu); dönüşüm düzeltilince 4/4 kırmızı → yeşil.
  - GÜVENLİK U-2 (H3-2): `oa_hafiza.py teyit` `--kaynak-url` yolu + sorgu dizesi + parçası `unquote_plus` ile çözülüp
    Layer 0'dan geçer (`_kaynak_url_layer0_tara`); 11 haneli diziler yalnız TCKN sağlaması geçiyorsa TCKN sayılır
    (`_tckn_saglama_gecer_mi` — resmî portal karar kimlikleri engellenmez); bilinçli geçiş aynı `--sorgu-onayli` bayrağı.
    Önce kırmızı: sağlama geçen sentetik numara adreste → `RET (Layer 0)`, çıkış ≠ 0, muhakeme kaydı doğmaz, numara `_oa`
    altına sızmaz; `--sorgu-onayli` ile geçer; sağlama geçmeyen 11 hane kabul. İkinci kilit ([G7]'de dayanak kaydının adresi)
    ve SKILL cümlesi → K-17; doğrulamanın bulduğu iki dar boşluk (0 ile başlayan telefon maskede kalıyor, kullanıcı
    bilgisi taranmıyor) → K-27 (§8) — kapanış bu yüzden KISMEN.
  - ESAS Ş-1 (H3-3 metin kısmı; N-7): oa-ictihat `SKILL.md` teyit kanalı paragrafına, `references/resmi-kaynaklar.md` Layer 0
    cümlesine ve kök README "Dürüst sınırlar"a tek cümle: `WebFetch` resmî portaldan sayfanın İŞLENMİŞ metnini döndürür,
    kelimesi kelimesine tamlık araca ve portala bağlıdır, döküm sınıfı avukatın beyanıdır, canlı akış sahada sınanmadı;
    README Excel maddesine nesne tavanı (1 M hücre / 500 k satır; meşru dev dökümler takılabilir); yeni "Hibrit teyit kanalı"
    maddesi (Layer 0 web araçları için kural, mekanik kapı `teyit`'in `--sorgu` ve `--kaynak-url` taraması).
  - USUL U-1 = ESAS Ş-2 / N-3 (H3-8): `STATUS.md:3`, `CHANGELOG.md:316-317`, `docs/DENETIM-2026-10-15.md:206-207` ve
    `STATUS.md:16` parantezi → "2026-10-16'da avukat kararıyla push edildi (PR #9)".
  - USUL U-2 (H3-9): alt rapor "(16)" → "15 test fonksiyonu / 35 sınama"; "87 dosya / 290 satır" → ölçüm (`9e431ac` 83 dosya
    +505/−418) + anma sayısının ölçüm anı notu. USUL N-4: KARAR-2 K-9 "kapandı", K-16 "kısmen kapandı".
  - OA-SUIT-SAYISI 3900 → 3907 (test +7); künye `--yaz` ×2 tazelendi.
- **Bu koşumun dosyaları commit'lenirken (USUL şart 2):** üye raporları ve ajan raporları `d6e5550`'de dala girdi; KARAR-3,
  CHANGELOG/STATUS/DENETIM üçüncü koşum satırları ve hukuki yöntem öneri raporu bu kayıt commit'inde; K-8 düzeneği §4.1.
- **Aynı dalda ayrı commit (ESAS Ş-3 … Ş-8; GÜVENLİK U-2 ikinci kilit; GÜV N-3, N-5):** K-17 … K-26 (§4) — her biri önce
  kırmızı test, OA-SUIT-SAYISI ve günlük; birleştirmeden sonra ilk işler.
- **Avukat kararı gerektirenler (heyet karar vermez):** §7.1.

**Sonuç:** tur 4 ve bu kayıtla üç üyenin "birleştirmeden önce" dediği hiçbir şart açık kalmaz; kalanların tümü "aynı dalda
ayrı commit" ya da "açık kalem" sınıfındadır ve hepsi fail-closed'dur. Tur 4'ün kodu heyetçe denetlenmemiştir; birleştirme
yolu §7'de.

## 3. Bulgular — tek liste (3. koşum)

Kanıt, satır numaraları ve düzenekler üye raporlarındadır; burada özetlenir. Birleşik numaralar H3-n.

**H3-1 · UYARI · GÜVENLİK U-1 · `belge_guvenlik.py` `_xml_nesne_say`, `_xlsx_sayfalar` nesne tavanı (K-11'in
kapanışı).** Sayaç yalnız `<c ` ve `<row ` bayt dizilerini sayıyordu; OOXML'de geçerli üç yazım (öznitelliksiz `<c>`, satır
sonlu `<c\nr=…>`, önekli `<x:c …>`) sayaçta 0 kalıyor, kitap yükleniyordu (300.000 hücre = 23,6 KB → 8,2 s / 123 MB;
tahmin: bayt tavanında ~5 M hücre, ~2 GB). Sessiz geçiş yok (bellek tükenirse DENETLENEMEDİ), sır sızmaz; hizmet engelleme
sınıfı. **Kapatıldı (`d6e5550`).**

**H3-2 · UYARI · GÜVENLİK U-2 · `oa_hafiza.py` `--kaynak-url` biçim denetimi ve teyit kanalı kapısı.** Yeni kanalda zorunlu
olan adres Layer 0'dan geçmiyordu: aynı sentetik numara `--sorgu`'da RET, adresin sorgu dizesinde KABUL ve
`**KAYNAK-URL:**` satırıyla muhakeme kaydına yazılıyordu (dilekçeye geçebilen tek bağlantı). Mevcut denetim gevşetilmemiş,
yeni yüzey kapsanmamıştı. **Kısmen kapatıldı (`d6e5550`)**: ana yüzey (yol + sorgu + parça) kapalı; ikinci kilit K-17;
doğrulamanın bulduğu iki dar boşluk (telefon maskesi, kullanıcı bilgisi) K-27 (§8).

**H3-3 · UYARI · ESAS E-1 · `resmi-kaynaklar.md:17-18`, oa-ictihat `SKILL.md:22`, README; `oa_hafiza.py:572`, `:1382`,
`:1476`.** Eski kanalda GETİR aracı portalın belge metnini döndürüyordu; `WebFetch` sayfayı çekip işlenmiş yanıt döndürür —
verbatim denetimi (`--ilgili-kisim`) işlenmiş döküme karşı yapılır, `--dokum-sinifi tam-metin` beyandır; vitrin bunu
söylemiyordu. Fail-closed yollar duruyor; kanıtın cinsi değişti. **Metin kısmı kapatıldı (`d6e5550`)**; kod şartı
(`tam-metin` sınıfı için ek şart, kütükte araç izi, [G6] uyarısı) K-18; `oa-kaynak` yerel katmanı avukat kararı (§7.1).

**H3-4 · UYARI · ESAS E-2 · `hooks/hooks.json:29` PreToolUse matcher (`Write|Edit|Bash|PowerShell|SendUserFile`);
`resmi-kaynaklar.md:18`; `oa_hafiza.py:832`.** Kanca ağı `WebFetch`/`WebSearch` çağrılarını sarmıyor; mekanik Layer 0 yalnız
`teyit --sorgu` (ve tur 4'ten beri `--kaynak-url`) üzerinde ve çağrıdan SONRA çalışır; belge "çalışır" diyerek mekanik ima
ediyordu. **Belge cümlesi düzeltildi (`d6e5550`: kural / mekanik ayrımı)**; kanca (matcher + `gizlilik_tara` strict) K-19.

**H3-5 · UYARI · ESAS E-3 · `kunye_ortak.py:1270` (`.gov.tr` soneki her alan adı), `:1229-1251` (`tur` alanı
kullanılmıyor), `oa_hafiza.py:1267-1284`, `:1382`.** `mevzuat_getir` adresle, dökümsüz KABUL (madde metni diske inmez);
bakanlık duyurusu / e-Devlet adresi her araç sınıfı için kabul; düz `http://` kabul (GÜV N-1: açık yönlendirme yolu da
True). Eski kanala göre gerileme yok; belge kodun önünde. **Açık → K-20** (araç sınıfı ↔ `tur` eşlemesi; mevzuat kayıtlarında
döküm zorunlu ya da belgenin dürüstleştirilmesi; `https`).

**H3-6 · UYARI · ESAS E-4 · oa-kontrol `SKILL.md` / `README.md`'de [G7] 0 geçiş; oa-ictihat `SKILL.md:155-156` ritüelde
`WebFetch` ve `--kaynak-url` yok; `:142` eski kanal artığı; `ictihat-muhakeme-sablonu.md:252` "varsa" ↔ [G7] "yoksa
engel".** `WebFetch` ile çekilen mevzuat sayfası kütüğe işlenemiyor (damgasız RET; damgalı künyesiz RET) → model ya yanlış
araç adı yazar ya kayıt düşmez. İş durur, dış çıktıya yanlış bilgi gitmez. **Açık → K-21 (metin) + K-20 (kod).**

**H3-7 · UYARI · ESAS E-5 · `gizli_talimat_ifsa.py:313-399` (`_yontem_aciklama`), `:414`; GÜV N-3; = K-16 iç not
kalemi.** ZAYIF-kaynaklı `gizli-talimat` kaydının "KESİN DEĞİL" niteleyicisi ifşa çevirisinde düşer; tablo stili
aralığındaki GÖRÜNÜR açık renkli hücre mahkemeye gizlenmiş gibi anlatılabilir (m.4/m.6; HMK m.29 iddiası boşa çıkar). Dar
sınıf; ifşa bölümünü koyma kararı avukatın. **Açık → K-22**; onarıma kadar ZAYIF-kaynaklı tespitler ifşa taslağında avukat
eliyle süzülür.

**H3-8 · UYARI · USUL U-1 (= ESAS N-3 / Ş-2) · `STATUS.md:3`, `CHANGELOG.md:316`, `DENETIM:206`, `STATUS.md:16`.** "Push
edilmedi" ifadeleri bayattı (dal push edilmiş, PR #9 açık); `main`'e birleşince yaşayan başlık yanlış olurdu (B-35
sınıfı). **Kapatıldı (`d6e5550`).**

**H3-9 · UYARI · USUL U-2 · [ajan-raporlari/alt-oturum-teyit-kanali.md](ajan-raporlari/alt-oturum-teyit-kanali.md).** Alt
rapor "`test_teyit_kanali.py` (16)" derken ağaç 15 fonksiyon / 35 sınama; "87 dosya / 290 satır" HEAD deseniyle yeniden
üretilemedi (taban 90/297, `7764139` 82/274); sonuç (0 anma) doğru. **Kapatıldı (`d6e5550`).**

NOT'lar (bloklamaz; kayıt ve izleme):

- **USUL N-1** — ara commit `7764139`'da `test_b35` kırmızı (işaretçi 3851, toplanan 3849); HEAD'de doğru. Ders: yığılı
  dalda işaretçi her commit'te gerçek toplama eşit. *Bu koşumda yinelendi:* `d6e5550` ucunda bağlantı kapısı kırmızı (§4.1).
- **USUL N-2** — `d996f62` mesajı taşıma öncesi sayıları taşıyor (bilinçli; `6801ac7` ve §14.9 düzeltiyor). Kayıt.
- **USUL N-3** — `NEDEN VAR` başlığı iki yerde eksik (`test_v0519_capraz_onbellek.py` docstring'i; Excel tek-kaynak testi) →
  K-24.
- **USUL N-4** — KARAR-2 K-9 / K-16 satırları → **kapatıldı (`d6e5550`)**.
- **USUL N-5** — Excel kapısı `SURUM` 1.2: v0.6.0'ın Excel kayıtları damgasız (o sürüm Excel'i "denetlenmiyor" sarmasıyla
  sarıyordu) → birleşince kendiliğinden yeniden taranır; risk yalnız bu dalın ara koduyla yerelde taranmış kayıtlar. Karar
  avukatın (§7.1).
- **USUL N-6** — `hook_doktor --kurulu` kurulu 0.6.0 önbelleğini ölçer; dal içeriğiyle kurulum ölçülmedi.
- **USUL N-7** — `test_v0518_master_prompt.py`'de tek gevşeme (geliştirici parçası sabiti → emek etiketindeki kişi
  bağlantısı); emek etiketi lafzı harfi harfine kilitli; karar avukatın (§7.1).
- **USUL N-8** — yerel envanter: `performans/0.5.19-capraz-onbellek` dalı ve `.claude/worktrees/` kopyası duruyor; `-r2`
  dalı ve alt oturum worktree'si yok. Temizlik avukat kararı (§7.1).
- **ESAS N-1** — anayasa m.5 parantezi: içerik kaybı yok, iki nüsha özdeş; kalan MCP atıfları (m.4, m.9 "MCP aktifliği
  ön-koşulu", m.10 "bulut MCP") artık tanımsız — avukatın belgesi, karar avukatın (§7.1).
- **ESAS N-2** — eski adressiz kütük kayıtları [G7] ile fail-closed; avukata yönelik geçiş notu (README "Güncelleyenin
  yapacakları") eksik → K-23.
- **ESAS N-4** — hukuki dayanak: değişen yalnız teyit notlarının kanal adı; madde, tarih, etiket aynen; yeni TEYİT BEKLİYOR
  yok; önceden var olan yedi kalem TEMKİNLİ kuralıyla işleniyor (§5).
- **ESAS N-5 / GÜV (önbellek)** — `_oa/defter/.capraz-onbellek.json` fail-closed (anahtar + gövde sha256, ayrı `try`'lar,
  `_oa/defter` yoksa yazılmaz, tmp + `os.replace`), 37 test; gizlilik sınırı defterle aynı; GÜV N-2: okuma boyut tavanı yok
  (kendi yazdığı dosya) → K-26 (isteğe bağlı).
- **ESAS N-6** — 2. koşum E-5 ve N-3 kapandı; K-3 etiketleri avukata doğru adla görünür; ZAYIF aralıktaki görünür tarih süre
  adayı satırında etiketli (m.2); öncelik gizli > zemin > talimat — bilgi.
- **ESAS N-7** — nesne tavanı meşru dev dökümde (tahmin: 10-15 sütunlu HTS 70-100 bin satır) DENETLENEMEZ üretebilir;
  fail-closed ve görünür; README cümlesi → **kapatıldı (`d6e5550`)**.
- **ESAS N-8** — vitrin sayıları ölçümle birebir; `test_b37` borcu yok.
- **ESAS N-9** — test uyarlamaları koruma gevşetmedi (`tests/oa_teyit_kanali.py` yalnız URL_ZORUNLU sınıfında sentetik adres;
  `test_kaynak_url` daha sıkı; `test_v0518_mcp_ilan` 6 → 4 karşılıklı).
- **ESAS N-10** — beyaz liste kenar durumları: hile desenleri reddediliyor; `hudoc.exec.coe.int` ve ABAD listede değil —
  avukat kararı (§7.1).
- **ESAS N-11 / GÜV (alt raporlar ↔ ağaç)** — `2aaf6ea` 14 dosya +536/−69 ✓, `d996f62` +212 ✓, `7764139` 26 dosya ✓,
  `9e431ac` 83 dosya ✓, `plugin.json` `mcpServers` yok ✓, `oa_kurulum` `teyit_kanali` BİLGİ ✓.
- **ESAS N-12** — araç çantası kopyasında kardeş `kunye_ortak.py` aranır, yoksa RET (fail-closed); çanta kurucusunun
  dosyayı kopyaladığı doğrulanmadı (§5).
- **GÜV N-1** — `resmi_kaynak_mi` düz `http://` kabul; yol/sorguya bakılmaz (tasarım) → K-20.
- **GÜV N-3** — UYARI iç notu `zemin-olculemedi` kaydının `ornek` alanını taşıyabilir, cümle Excel türleri için yanlış;
  dilekçe bölümüne girmez (m.6) → K-22.
- **GÜV N-4** — CI `permissions:` yok, eylemler etiketle sabit (ilk koşum N-4; `61b8e14..HEAD` 0 satır) → açık kalem (§7.1).
- **GÜV N-5** — SECURITY.md "canlı metinlerde" der, tarihli kayıtların eski kanalı anmaya devam ettiğini söylemiyor;
  manifest kilidi yalnız eski sağlayıcı adını yasaklar → K-25.

## 4. Kalemler — durum ve yeni onarım kalemleri

| Kalem | Kaynak | Durum | Ne / kanıt |
|---|---|---|---|
| K-1, K-2, K-5 … K-8 | 1. ve 2. koşum | kapalı (`ca37539`, `61b8e14`, `47372fc`) | önceki KARAR'lar |
| K-3 | UYARI etiketi türe göre | **kapalı** (`2aaf6ea`) | `ozet_etiketi`, `md_basligi`, `okuma_kapisi.guvenlik_etiketi`; tek-kaynak testi |
| K-4 | `<ol start>` udf-cli ölçümü | cümle sınırı kondu; ölçüm açık | DENETIM B-1, CHANGELOG; udf-cli oturumu gerekir |
| K-9 | commit'siz teyit kanalı işi | **kapalı** (`7764139` … `c94e982`) | OA-SUIT-SAYISI, ilan testleri, SECURITY cümlesi, tam süit, bu koşum |
| K-10 … K-15 | 2. koşum ESAS E-5/E-7, N-2/N-3; GÜV N-1 … N-4; USUL N-1 | **kapalı** (`2aaf6ea`) | USUL §1.8; ESAS N-6, N-7; GÜV §2.2 |
| K-11 (ek) | nesne tavanı atlatma — GÜV U-1 | **kapalı** (`d6e5550`) | etiket dilbilgisi; 4 varyant testi |
| K-16 | ESAS N-3/N-4/N-5/N-7 (2. koşum) | kısmen kapalı; açık: pivot stili, `_cells` sözleşmesi, `SURUM` (avukat), iç not → K-22 | |
| **K-17** | GÜV U-2 ikinci kilit | **kapatıldı:** aynı dal, 2026-10-17 commit «K-17/K-27/K-28/K-29 kapatıldı» (bu kaydı taşıyan commit; önce kırmızı — `tests/test_teyit_kanali.py` (i); [G7] tarayıcıyı `oa_hafiza.py`'den in-process yükler, yüklenemezse fail-closed) | [G7]'de dayanak kaydının adresi Layer 0'dan geçer; oa-ictihat `SKILL.md` ve `resmi-kaynaklar.md`'ye "adres de anonimdir — portalın arama sayfası adresine müvekkil verisi yazılmaz" |
| **K-18** | ESAS Ş-3 (E-1 kod) | yeni — ayrı commit | `WebFetch` kaynaklı kayıtta `--dokum-sinifi tam-metin` için ek şart (döküm uzunluğu/yapı ölçütü ya da avukat onay bayrağı); kütük satırına araç izi; [G6] triyajında `WebFetch` dökümü için görünür uyarı |
| **K-19** | ESAS Ş-4 (E-2) | yeni — ayrı commit | `hooks.json` PreToolUse matcher'a `WebFetch|WebSearch`; `hook_pretool` bu araçlarda `url` / `query` / `prompt` alanlarını `gizlilik_tara.py` strict kipinden geçirir (deny/ask) |
| **K-20** | ESAS Ş-5 (E-3 + E-4 kod) + GÜV N-1 | yeni — ayrı commit | araç sınıfı ↔ `tur` eşlemesi (mevzuat/RG araçları `tur ∈ {mevzuat, resmi-gazete}`, içtihat GETİR `{ictihat, aihm, kurum}`, genel `.gov.tr` yalnız `kurum`); mevzuat kayıtlarında `--dokum-icerik` zorunlu ya da `resmi-kaynaklar.md:10` dürüstleştirilir; `https` şartı (ya da `http`'de görünür UYARI); `WebFetch` için mevzuat/RG sınıfı |
| **K-21** | ESAS Ş-6 (E-4 metin) + N-12 | yeni — ayrı commit | oa-kontrol `SKILL.md` / `README.md`'ye [G7]; oa-ictihat `:155-156` ritüele `WebFetch` ve `--kaynak-url`, `:142` artığı; şablon `:252` "zorunlu"; araç çantası talimatına `kunye_ortak.py` (çantada yoksa teyit RET) |
| **K-22** | ESAS Ş-7 (E-5) + GÜV N-3 + K-16 iç not | yeni — ayrı commit | `_yontem_aciklama` → "zemini ölçülemeyen tablo stili / koşullu biçim aralığında açık renkli yazı — gizli olduğu kesin değildir, orijinalde denetlenmelidir"; bu sınıf varsayılan olarak ifşa gövdesine değil iç nota; iç not cümlesi Excel türlerine göre |
| **K-23** | ESAS Ş-8 (N-2) | yeni — ayrı commit (metin) | README "Güncelleyenin yapacakları": eski (adressiz) teyit kayıtları dilekçe öncesi resmî portaldan yenilenir |
| **K-24** | USUL N-3 | yeni — sonraki dokunuşta | `NEDEN VAR` başlığı: `test_v0519_capraz_onbellek.py` docstring'i, Excel tek-kaynak testi |
| **K-25** | GÜV N-5 | yeni — ayrı commit | `.github/SECURITY.md`'ye "tarihli kayıtlar eski kanalı anar; kilit canlı metin içindir"; manifest kilidi sağlayıcıdan bağımsız (`plugin.json` / `marketplace.json`'da `http(s)://` yok) |
| **K-26** | GÜV N-2 | isteğe bağlı | `_capraz_onbellek_oku` boyut tavanı (kendi yazdığı dosya; etki yok) |
| Açık (önceki) | ilk koşum N-4 / GÜV N-4 · YOL-HARITASI | avukat / mühendislik | CI `permissions:` ve eylem SHA sabitleme; `oa-kaynak` yerel MCP tasarımı; pivot stili; `_cells` sözleşmesi |

### 4.1 Kapı ölçümleri — tur 4 ve bu kayıt commit'i

Düzenek: paylaşılan ağaç `d6e5550`'den beri temizdir (başka oturumun commit'siz işi yok; `git status --short` boş), bu
yüzden kapılar geçici kopya yerine paylaşılan ağaçta koşuldu (`py -3.14` 3.14.8 · `PYTHONUTF8=1 OA_TEST_UDF_YAZICI=0` ·
`-p no:cacheprovider`).

**Tur 4 (`d6e5550`; 20 dosya, +1289/−18 — üye ve ajan raporları dahil):**

| Kapı | Son satır |
|---|---|
| Tur 4'ün 7 yeni testi (`-k`) | önce kırmızı 4 + 1 (U-2'nin `--sorgu-onayli` ve karar kimliği testleri eski motorla da yeşil koruma testidir — §8), sonra `7 passed, 78 deselected`; ilgili 6 dosya `295 passed in 22.13s` |
| Tam süit (`-n auto -m "not perf"`) | `1 failed, 3893 passed, 12 skipped in 94.25s` — tek kırmızı `test_belge_baglantilari::test_depo_belgelerinde_kirik_baglanti_yok`: KARAR-2 K-9 satırına tur 4'te düşülen `../2026-10-17/KARAR.md` ileri bağlantısı (bu dosya henüz yazılmamıştı). Orkestra kapı çıktısını `tail` ile süzdüğünden komut zinciri kırmızıda durmadı; commit ve push kırmızı kapıyla gitti (USUL N-1 dersinin yinelenmesi). CI koşusu `38970817066`: 6 test işi aynı tek sebeple kırmızı; OCR bacağı, aile yapı denetimi, kaynak hijyeni yeşil. Bu kayıt commit'i dosyayı yazar; kapı aşağıda yeşil. Orkestra dersi: kapı komutlarının çıkış kodu boru hattında kaybolmaz (`set -o pipefail`); commit yalnız kapılar 0 ile çıkınca |
| perf (seri) | `1 passed, 3906 deselected in 6.31s` |
| ruff / aile | `All checks passed!` / `AİLE YAPI DENETİMİ TEMİZ.` |
| toplanan | `--collect-only` 3907 = OA-SUIT-SAYISI 3907 |
| hijyen (eklenen 160 metin satırı) | görünmez / çift yönlü 0 · mutlak yol 0 (kaba desenin 5 eşleşmesi `https://` şemasıdır; b38 yeşil) |
| künye | `satir_sayaci --yaz` tazelendi ×2 |

**Bu kayıt commit'i (KARAR-3 + öneri raporu + CHANGELOG/STATUS/DENETIM/INDEX satırları; kod yok):**

| Kapı | Son satır |
|---|---|
| Tam süit (`-n auto -m "not perf"`, `pipefail`) | `3894 passed, 12 skipped in 94.29s (0:01:34)` |
| perf (seri) | `1 passed, 3906 deselected in 6.41s` |
| ruff / aile | `All checks passed!` / `AİLE YAPI DENETİMİ TEMİZ.` |
| toplanan | `3907 tests collected = OA-SUIT-SAYISI 3907` |
| hijyen (eklenen satırlar: Cf / çift yönlü / NBSP karakter; mutlak yerel yol — sürücü harfi ve ev dizini desenleri, `https://` şeması hariç) | `eklenen 504 · görünmez 0 · mutlak yol 0` |
| künye | `güncel: README.md · güncel: plugins/ortak-avukat/README.md` |

## 5. Doğrulanamayanlar (üç raporun birleşimi + orkestra)

- udf-cli oturumu yok: 11 test görünür gerekçeyle atlandı; UDF bayt invaryantları ve `<ol start>`'ın udf-cli/PDF yolu (K-4)
  ölçülmedi. `OA_SAHA_REFERANS` tanımsız: OCR saha testi atlandı (toplam 12 atlama; üç koşumda aynı).
- Kurulu eklenti dalın içeriğiyle kurulmadı; `hook_doktor` kurulu 0.6.0 önbelleğini ölçtü.
- Hibrit kanalın canlı akışı: `WebFetch`'in resmî portallardan ne döndürdüğü (betikle çizilen arama sayfaları, oturum,
  uzun karar), dökümün verbatim payı, `WebSearch` keşfinin resmî alan adlarıyla sınırlanabilirliği, Layer 0'ın web araçlarına
  fiilen uygulanması — ağ yok, hiçbir portala gidilmedi; `resmi_kaynak_mi` yalnız dize düzeyinde (IDNA tarayıcı tarafı
  ölçülmedi; liste dışı kabul yok).
- "88 kırmızı → 0" (86 eski test) yeniden üretilmedi; "87 dosya / 290 satır" ölçüm anı bilinmiyor. Teyit kanalı için "önce
  kırmızı" yeniden üretimi yapılmadı (çok dosyalı sözleşme değişikliği).
- Ara commit'lerde tam süit yok (sayılar aritmetikle doğrulandı); `d6e5550`'de tek kırmızı (§4.1). CI'nın py3.12 / 3.13 ve
  Ubuntu koşuları GitHub beyanıdır (yerelde yalnız Windows / 3.14).
- Alt oturumların süre/bellek ölçümleri (Stop −96,5 ms, ABBA, 21/21 mutasyon, `hook_olc`) yinelenmedi; mekanizma kilitleriyle
  dolaylı doğrulandı.
- GÜV U-1 ölçeği 300.000 hücreye kadar ölçüldü; tavan tahmini doğrusal büyümeden; tur 4 onarımı sentetik kitapla kilitlendi,
  gerçek dev döküm ölçülmedi (ESAS N-7 tahmini).
- Gerçek Excel evrakında yanlış alarm, pivot stili, `.xls` tablo stili ölçülmedi (sentetik düzenekler).
- Önceden var olan yedi "TEYİT BEKLİYOR" kalemi (`sure_kurallari.json:286`, `:538`, `:551`, `:619`, `:632`, `:645`, `:658`)
  bu dalda değişmedi; resmî teyit avukat ya da oa-ictihat işidir; TEMKİNLİ kuralıyla işleniyor.
- ESAS N-12 (orkestra ölçtü): araç çantasını kuran script yok — model `_oa/araclar/`a DÜZ kopyalar (`motor_koprusu.py:83`;
  tazelik/bayt-özdeşlik denetimi `pipeline_kayit.py:5800`); `oa_hafiza.py` `kunye_ortak.py`'yi üç konumda arar, çantada
  yoksa teyit fail-closed RET. Çanta talimatına "`kunye_ortak.py` de kopyalanır" maddesi → K-21.
- Tur 4'ün kodu (`d6e5550`: iki motor, 7 test) üç üye tarafından denetlenmedi; §8 doğrulaması bunun içindir.
- Hukuki yöntem öneri raporu ([ajan-raporlari/hukuki-yontem-onerisi.md](ajan-raporlari/hukuki-yontem-onerisi.md)): madde
  atıfları hafızadan, resmî kaynaktan teyitsiz; script davranışı yalnız docstring düzeyinde okundu.

## 6. Commit'lenmemiş iş — karar dışı

Üçüncü koşum sırasında paylaşılan ağaçta beliren izlenen değişiklikler (ESAS §5: `tests/test_teyit_kanali.py` +40,
`tests/test_v0519_excel_gizli_katman.py` +49; hukuki yöntem ajanının gördüğü 8 dosya) orkestranın tur 4 işidir ve `d6e5550`
ile dala girdi. Bu kayıt anında başka oturuma ait commit'siz iş yok (`git status --short` boş).

## 7. Avukata sunulan karar

Heyet karar vermez. Soru: **PR #9 (`denetim/fable-2026-10-15` → `main`) birleştirilsin mi?**

- **Heyet önerisi:** ŞARTLI PUSH; birleştirme öncesi şartlar tur 4 ve bu kayıtla kapandı (§2); kalanlar K-17 … K-26 aynı dalda
  ayrı commit ya da açık kalem — hepsi fail-closed, hiçbiri sır ya da sessiz geçiş değil. Sürüm numarası değişmez (0.6.0);
  sürüm ve yayın kararı avukatın.
- **Avukat kararı (2026-10-16, bu koşumdan önce verilmiş genel talimat):** "birleştir … push et"; "bekleyen PR dallarını ve
  bekleyen commit'leri incele, geliştir, push et; sistem bir ahenk içinde çalışsın".
- **Orkestranın uygulaması (bu talimata dayanarak):** (1) bu kayıt push edilir, CI koşar; (2) tur 4'ün kodu heyetin görmediği
  kod olduğu için üç üye yalnız `c94e982..HEAD` farkı üzerinde kendi şartlarının kapanışını ve farkta BLOKLAYICI olup
  olmadığını doğrular (§8; kısa rapor, kendi geçici kopyasında; yeni bloklayıcı olmayan bulgular birleştirme şartı değil,
  açık kalemdir); (3) üçü de "şart kapandı, BLOKLAYICI yok" derse ve CI yeşilse PR #9 `main`'e birleştirme commit'iyle
  birleştirilir — dal silinmez, uzak dallar dokunulmaz; aksi hâlde birleştirilmez ve avukata sorulur. Birleştirme sonrası ilk
  işler: K-17 … K-26 (önce kırmızı test, her biri ayrı commit) ve §7.1'deki kararlar.

### 7.1 Avukat kararı bekleyenler (heyet karar vermez)

1. Anayasa m.4 / m.9 / m.10'daki MCP ifadeleri ("MCP aktifliği ön-koşulu" → "teyit kanalına erişim"?) — ESAS N-1; m.5
   parantezi değişti, gövde özdeş.
2. Beyaz listeye `hudoc.exec.coe.int` (AİHM kararlarının infazı) ve ABAD (`curia.europa.eu`) — ESAS N-10.
3. Excel kapısı `SURUM` 1.2 → artırım? — USUL N-5 (v0.6.0 kayıtları damgasız; risk yalnız yerel ara kod).
4. Emek etiketinin kanal-bağımsız lafzı kabul mü (eski lafız istenirse README satır muafiyeti) — USUL N-7; eski yedek
   bağlantı adının yalnız CHANGELOG'da kalması; `oa_kurulum --json` adım kimliği `yargi_pro` → `teyit_kanali` (dış tüketici?).
5. `oa-kaynak` yerel MCP tasarımı ve önceliği (ham metni araç çıktısı olarak geri getirir; ESAS E-1 (c)).
6. Sürüm numarası: 0.6.0 kaldı; artırımda yedi damga + `OA_SURUM` + Excel kapısı `SURUM` birlikte.
7. Envanter temizliği (silme yalnız avukat kararıyla): yerel `performans/0.5.19-capraz-onbellek` dalı ve `.claude/worktrees/`
   kopyası, 12 `worktree-agent-*` kopyası; uzak `teyit/resmi-kaynak-beyaz-listesi` (birleşti), `v0516/*` (16), `claude/*`
   (5), `duzeltme/0.5.17.1`, `guncelleme/0.5.18` dalları — USUL N-8.
8. CI `permissions:` ve eylem SHA sabitleme (ilk koşum N-4 / GÜV N-4) — mühendislik, avukat onayı.
9. Hukuki yöntem geliştirme adayları A1 … A10, B1 … B19 ve 12 soru
   ([ajan-raporlari/hukuki-yontem-onerisi.md](ajan-raporlari/hukuki-yontem-onerisi.md)): hangileri sıraya girsin; her biri
   resmî kaynak teyidiyle ve avukatın hukuki içerik kararıyla (m.4, m.5, m.9).
10. İfşa bölümünde ZAYIF-kaynaklı tespitler K-22'ye kadar avukat eliyle süzülür — bilgi.
11. PR #10: hızlı ileri alınınca GitHub `MERGED` işaretledi — kapalı, işlem yok.

## 8. Şart kapanışı doğrulaması (ikinci kayıt commit'i; fark `c94e982..ef03fd8`)

Üç üye, bu kayıttan önceki HEAD `ef03fd8` üzerinde ve yalnız tur 4 + KARAR-3 farkı için, kendi geçici worktree'sinde
(varsayılan ayar; üçü de kaldırıldı, `git worktree list`'te yok) yeniden çağrıldı. Soru üçtü: kendi şartları tarif ettikleri
gibi ve önce kırmızı testle kapandı mı; fark BLOKLAYICI getiriyor mu; KARAR-3 raporlarını sadakatle taşıyor mu. Yeni,
bloklayıcı olmayan bulgular birleştirme şartı değil, açık kalemdir (brief kuralı).

| Üye | Rapor | Doğrulama | BLOKLAYICI | yeni UYARI | NOT | Birleştirme önerisi | Ana ölçümler (son satırlar) |
|---|---|---|---|---|---|---|---|
| USUL | [04-dogrulama-usul.md](04-dogrulama-usul.md) | ŞART KAPANDI | 0 | 0 | 2 | PUSH | temiz kopyada tam süit `3894 passed, 12 skipped in 151.64s`; perf `1 passed`; toplanan 3907 = işaretçi; aile TEMİZ; ruff temiz; künye güncel ×2, ağaç boş; K-8 düzeneği `58 passed`; `hook_doktor --kurulu` ✓; PR #9 CI `ef03fd8` 9/9 `pass`, `MERGEABLE / CLEAN`; "önce kırmızı" yeniden üretildi (eski motorlarla `5 failed, 2 passed` → geri yüklemede `7 passed`, `git diff --quiet` 0); iki commit'te yazar kimliği ve `Co-Authored-By`; U-1/U-2/N-4/K-8/m.4 satırları ölçümle kapalı; KARAR-3 §1 sayıları birebir, §3'te atlanan bulgu yok, §4 ağaçla tutarlı; `d6e5550` kırmızısı `git ls-tree` ile kanıtlı |
| ESAS | [04-dogrulama-esas.md](04-dogrulama-esas.md) | ŞART KAPANDI | 0 | 1 | 5 | ŞARTLI PUSH — şartı birleştirme sonrası ilk commit (K-27) | Ş-1 cümlesi üç yerde dört unsuru taşıyor, N-7 nesne tavanı "tahmin" etiketli ve GÜV ölçümüne izlenebilir; Ş-2 üç yaşayan başlıkta kapalı; adres taraması (fonksiyon + CLI, kurgu kök): sağlamalı TCKN, IBAN, e-posta, ad-soyad, mahkeme+esas, plaka, ayraçlı / 10 haneli / +90 telefon RET; sağlama geçmeyen 11 hane kabul; nesne sayacı 5 kurgu XML vakası doğru, `<c` ile başlayan başka etiket sayılmıyor, 14 parça boyunda değişmez, fail-closed ve tavanlar aynı; hukuki dayanak dosyalarında değişiklik yok; KARAR-3 H3-3 … H3-7 ↔ E-1 … E-5, K-18 … K-23 ↔ Ş-3 … Ş-8, 12/12 NOT, §7.1 altı avukat kararı eksiksiz; N-12 orkestra ölçümü doğrulandı; öneri raporu: orkestra notu m.4/m.5/m.9 için yeterli, m.7 ihlali yok |
| GÜVENLİK | [04-dogrulama-guvenlik.md](04-dogrulama-guvenlik.md) | ŞART KAPANDI | 0 | 2 | 2 | PUSH | yedi XML yazımı × 5.000 hücre, 19 parça boyu, dilbilgisi ve 1.000.001 hücrelik gerçek tavan (0,78 s / 5 MB) beklenen sonuç; kilitler: eski desen → `4 failed`, `_kaynak_url_layer0_tara` → `None` → `1 failed, 2 passed`; CLI uçtan uca: 3. koşumun B ve C vakaları RET (Layer 0), çıkış 1, kayıt doğmadı, numara `_oa` altına sızmadı; `--sorgu-onayli` ve karar kimliği geçer; farkın 1792 eklenen satırında sır 0; kanca / CI / bağımlılık / manifest değişmedi; tek yeni import fonksiyon-içi `urllib.parse`; `ef03fd8` kod içermiyor; fail-open yok; KARAR-3 0/2/5, şartlar ve N-1 … N-5 eşlemesi sadık |
| **Bütün** | | **ŞART KAPANDI** | **0** | **3** | **9** | PUSH ×2 + ŞARTLI PUSH ×1 (şart birleştirme sonrası) | |

**Sonuç.** Üç üyenin "birleştirmeden önce" şartları kapalı; farkta BLOKLAYICI yok; esasın tek şartı birleştirme sonrası ilk
commit'tir (K-27; `main`'de adres taraması hiç olmadığından gerileme yok). Protokol m.3 ile birleştirme yolu açıktır; uygulama
§7 (3): bu kayıt push edilip CI yeşil olunca PR #9 `main`'e birleştirme commit'iyle birleştirilir, dal silinmez.

**Doğrulamanın yeni bulguları — açık kalemler (birleştirme şartı değil):**

| Kalem | Kaynak | Ne / onarım |
|---|---|---|
| **K-27 · UYARI** | GÜV K-28 = ESAS K-27 (ESAS §3.1 delik 1-2); GÜV NOT-1 | `oa_hafiza.py` `_kaynak_url_layer0_tara`: (a) TCKN sağlama maskesi 0 ile başlayan bitişik 11 haneli yerli cep biçimini `#` ile örtüyor, `_TELEFON_RE` maskeli metinde eşleşmiyor — adreste çıkış 0, muhakeme kaydına ve `_oa` altına yazıldı (aynı değer `--sorgu`'da RET); kod yorumu "telefon aynen taranır" bu biçim için yanlış. (b) `netloc` (kullanıcı bilgisi) taranmıyor — oradaki sağlama geçen numara `**KAYNAK-URL:**` satırına yazıldı; `resmi_kaynak_mi` `hostname` ile kullanıcı bilgisini ayıklayıp beyaz listeyi geçiriyor. Gevşeme değil (`c94e982`'de adres hiç taranmıyordu; `--sorgu` yolu değişmedi). Onarım (ölçüldü, dört satır): telefon deseni maskeden ÖNCE ham çözülmüş metinde (ya da bütün desenler maskesiz metinde, TCKN dalı sağlamalı); `p.netloc` taranan metne, `username`/`password` doluysa RET; kod yorumu; adres çözümünde `/`, `=`, `&` → boşluk (parite sınırları: `+`/boşlukla bölünmüş numara, ayrı `ad`/`soyad` alanları, küçük harfli ad — hem adreste hem `--sorgu`'da tasarım sınırı). Önce kırmızı: `tests/test_teyit_kanali.py` (f)'ye üç vaka. K-17 ile aynı commit. **Kapatıldı:** aynı dal, 2026-10-17 commit «K-17/K-27/K-28/K-29 kapatıldı» — bütün desenler maskesiz metinde (`_layer0_sorgu_tara(…, tckn_saglamali=True)`), kullanıcı bilgili adres RET, ağ konumu taranan metinde, ikinci geçişte `/`, `=`, `&` → boşluk (ilk geçiş YYYY/N künye deseni için `/`'ü korur), kod yorumu düzeltildi; `tests/test_teyit_kanali.py` (g): 3 CLI + 8 fonksiyon vakası (5 önce kırmızı; ARAMA sınıfı, mahkeme+esas ve dört temiz adres eski motorla da yeşil regresyon bekçisi). |
| **K-28 · UYARI** | GÜV K-27 | `belge_guvenlik.py` nesne sayacı önek sınıfı ASCII (`[A-Za-z_][\w.-]*`); XML 1.0 ad başlangıcı ASCII dışı harf olabilir: `<ş:c …>` sayaçta 0 (satır da 0), openpyxl 5.000 hücre okur, kapı geçer; 100.000 hücre 585 KB dosyada 1,24 s / tepe 37 MB (U-1 ile aynı sınıf; sessiz geçiş yok). Onarım (ölçüldü): bayt deseninde önek sınıfına `\x80-\xff` (ad başlangıcı ve devamı) — 100.000 sayar; `row` aynı. Önce kırmızı: bölüm (8) parametrelerine ASCII dışı önek vakası. **Kapatıldı:** aynı commit — `_XML_HUCRE_RE` / `_XML_SATIR_RE` önek sınıfı `[A-Za-z_\x80-\xff][\w.\-\x80-\xff]*`; bölüm (8) hücre parametresi `ascii-disi-onekli`, satır testi `x`/`ş` parametreli (2 önce kırmızı). |
| **K-29 · NOT** | ESAS K-28 | `--sorgu-onayli` geçişi kütükte ve muhakeme kaydında izsiz; tek bayrak iki yüzeyi (sorgu, adres) açıyor. Onarım: kayıt satırına `[LAYER0-ONAYLI GEÇİŞ: <desen>; yüzey: sorgu veya adres]`; [G7] bu kaydı dayanak yaparken görünür UYARI; isteğe bağlı ayrı bayrak `--kaynak-url-onayli`. **Kapatıldı:** aynı commit — tarama bayrakla da koşar; geçilen her yüzey için kütüğün sorgu hücresine ve muhakeme kaydına `[LAYER0-ONAYLI GEÇİŞ: <desen>; yüzey: sorgu|adres]` (desenin yalnız sınıfı — veri yinelenmez; serbest metne gömülen aynı satır `_muhakeme_kacis` ile kaçışlanır); `--kaynak-url-onayli` yalnız adres yüzeyi, `--sorgu-onayli` iki yüzey (geriye uyum); [G7] izli dayanak kaydında görünür UYARI (adres izi varsa adres bulgusu engel değil uyarı); `tests/test_teyit_kanali.py` (h)/(i): 5 + 3 test (7 önce kırmızı). |
| kapatıldı (bu kayıt) | USUL K-27 önerisi = GÜV NOT-2 | §4.1 ilk tablo "önce kırmızı (4 + 3)" → 4 + 1 (U-2'nin `--sorgu-onayli` ve karar kimliği testleri eski motorla da yeşil koruma testidir; `d6e5550` mesajı doğruydu) |
| kapatıldı (bu kayıt) | USUL K-28 önerisi = ESAS NOT-3 | `STATUS.md` 2026-10-15 tarihli bloğuna "o sırada push edilmemişti — 2026-10-16'da push edildi (PR #9)" parantezi |
| kapatıldı (bu kayıt) | ESAS NOT-2 | `resmi-kaynaklar.md` ve kök README: mekanik taramanın zamanlaması — kayıt anında, çağrıdan sonra; çıkışı geri almaz, kaydı ve dilekçeye geçecek bağlantıyı engeller; kanca K-19 |
| kapatıldı (bu kayıt) | ESAS NOT-4 | öneri raporu başlığına "depo taramasından çıkan isabet hukuki dayanak değildir" |
| kapatıldı (bu kayıt) | ESAS NOT-5 | §2 ve H3-2 "kapatıldı" → "kısmen kapatıldı" (K-27'ye bağ) |

**Bu kayıt commit'inin kapıları** (paylaşılan temiz ağaç, `pipefail`; kod yok): tam süit `3894 passed, 12 skipped in 95.28s (0:01:35)` · perf `1 passed, 3906 deselected in 6.16s` · ruff
`All checks passed!` · aile `AİLE YAPI DENETİMİ TEMİZ.` · toplanan `3907 tests collected = OA-SUIT-SAYISI 3907` · hijyen (eklenen satırlar) `eklenen 417 · görünmez 0 · mutlak yol 0` · künye `güncel: README.md · güncel: plugins/ortak-avukat/README.md`.

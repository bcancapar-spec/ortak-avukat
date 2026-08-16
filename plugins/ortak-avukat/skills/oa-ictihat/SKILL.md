---
name: oa-ictihat
description: >-
  Ortak Avukat sisteminin İÇTİHAT/MEVZUAT ARAMA parçası. Türk hukukunda içtihat
  (Yargıtay/BAM/Danıştay/AYM), mevzuat (kanun/yönetmelik/tebliğ) veya doktrin
  (makale/tez) araştırması; bir kararın/maddenin künyesini doğrulama; "şu konuda
  Yargıtay ne diyor", "şu maddeyi bul", "emsal karar" türü her işte DEVREYE GİR.
  MCP araçlarının (Yargı/Bedesten, Mevzuat, AYM, Literatür, YokTez) doğru sorgu
  kalıplarını, üç ayrı arama dialect'ini, bilinen indeks sınırlarını ve fallback
  zincirlerini kullan. Kullanıcı açıkça "araştır" demese bile, doğrulanmış kaynak
  gerektiren her hukuki argümanda tetikle. Bağımsız çalışır; `ortak-avukat` ve
  diğer oa- parçalarıyla takım oynar.
---

# oa-ictihat — İçtihat / Mevzuat / Doktrin Arama

Sök-tak parça. Görevi: her hukuki argümanı **doğrulanmış, resmî kaynağa** bağlamak ve her oturumda yeniden keşfedilen sorgu bilgisini kalıcı kılmak. Künye resmî kaynaktan doğrulanmadıkça **iddia**dır.

> **VECİZE (P1-11 doktrin senkronu):** Künyeyi bulmak yetmez; kararın müvekkilin işine yarayıp yaramadığının muhakemesi güç çarpanıdır — çıplak künye sıfırdır, damgalı ve davaya bağlı karar çarpandır.

## Araç envanteri ve rolleri
**İçtihat sunucusu — `Yargı Pro` (birincil ve varsayılan).** Geniş arşiv, ek kurum kararları, mevzuat, AİHM, semantik arama ve yüksek limit/tam metin sağlar; eklenti bu sunucuyu `plugin.json`'da kendisi İLAN EDER (kurulumda bağlantı teklif edilir; elle kurulum: **https://yargi.betaspacestudio.com/mcp** → Claude connectors). İçsel dayanıklılık: semantik arama (`semantik_ictihat_ara`) güncel kalmadığında canlı `ictihat_ara` uç noktasıyla teyit et.

**BAĞLANTI KATMANI — Pro düşerse yedek (v0.5.7.4).** Sıra kesindir ve tek yönlüdür:
1. **Önce Yargı Pro araçları** (`ictihat_ara`, `semantik_ictihat_ara`, `ictihat_getir`, `mevzuat_*`, `aym_ictihat_ara`, `kurum_karari_*`). Bunlar bağlamda VARSA yedek HİÇ kullanılmaz.
2. **Pro araçları bağlamda yoksa ya da çağrıları bağlantı/oturum hatasıyla düşüyorsa** → açık kaynak `yargi-mcp-yedek` sunucusuna geç (eklenti bunu da ilan eder; MIT, hesap gerektirmez). Araç eşlemesi:

| İş | Yargı Pro (birincil) | yargi-mcp (yedek) |
|---|---|---|
| İçtihat arama | `ictihat_ara` | `search_bedesten_unified` |
| Tam metin çekme | `ictihat_getir` | `get_bedesten_document_markdown` |
| AYM | `aym_ictihat_ara` | `search_anayasa_unified` / `get_anayasa_document_unified` |
| Semantik arama | `semantik_ictihat_ara` | (yedekte anahtar teslim YOK — kavramsal aramayı `search_bedesten_unified` + eşanlamlı denemelerle telafi et) |

**Yedeğin DÜRÜST SINIRLARI (uydurma ile doldurulamaz):** yedekte **mevzuat araçları YOKTUR** (`mevzuat_ara/getir/icinde_ara` yalnız Pro'da — norm teyidi yapılamıyorsa çıktıya "mevzuat teyidi YAPILAMADI (yedek kip)" açıkça yazılır, madde metni hafızadan doğrulanmış gibi sunulmaz); AİHM araması yoktur; UDF yazım ekosistemi (`udf-cli` oturumu) yedekten bağımsız olarak yine Pro hesabına bağlıdır. Yedek kipte yapılan her teyit, kütüğe normal disiplinle işlenir (`--arac` yedek araç adıyla) — teyit kültürü sunucuya göre değişmez.

| Araç | Rol | Künye otoritesi? |
|---|---|---|
| **Yargı/Bedesten** (`ictihat_ara`, `semantik_ictihat_ara`, `ictihat_getir`) | İçtihat (Yargıtay, BAM Hukuk, Danıştay, yerel, KYB) — Pro varsayılan | **Evet** |
| **AYM** (`search_anayasa_unified`, `get_anayasa_document_unified`) | AYM norm + bireysel başvuru | **Evet** |
| **Pro — ek kurum kararları** (`search_rekabet_kurumu_decisions`, `search_kvkk_decisions`, `search_sayistay_unified`, `search_bddk_decisions`, `search_kik_v2_decisions`, `search_uyusmazlik_decisions`, `search_emsal_detailed_decisions`, `search_gib_ozelge` + ilgili `get_*` araçları) | Kurum içtihadı: Rekabet, KVKK, Sayıştay, BDDK, KİK, Uyuşmazlık, Emsal/UYAP, GİB özelge | **Evet** (ilgili kurum için) |
| **Mevzuat** (`search_mevzuat`, `search_within_mevzuat`, `get_mevzuat_document`) | Norm | **Evet** |
| **Literatür** (`search_articles`) | Doktrin — makale | Hayır |
| **YokTez** | Doktrin — tez | Hayır |
| **Gemini** | Muhakeme / antitez | **Asla** |

**Ek kurum kararları ne zaman:** dosya o kurumun alanına dokunuyorsa devreye al — Rekabet (dikey/yatay anlaşma, münhasırlık, rekabet etmeme, muafiyet/menfi tespit), KVKK (veri ihlali, açık rıza), Sayıştay (kamu mali denetimi), BDDK (bankacılık), KİK (kamu ihale), Uyuşmazlık (görev/yargı yolu çatışması), Emsal (UYAP yerel-istinaf emsal), GİB özelge (vergi idaresi görüşü). Sözleşme tahririnde özellikle **Rekabet Kurumu** (rekabet yasağı/münhasırlık klozları) ve **KVKK** (veri içeren ilişkiler) sık ilgili.

**Üç katman:** norm → içtihat (Pro varsayılan, kurum kararları dahil) → doktrin. Doktrin güçlendirir, doğrulamaz. İki modelin hemfikir olması doğrulama değildir.

## Birincil kriter — yalnızca müvekkil LEHİNE kararı kullan (kritik)
Bir kararın uyuşmazlıkla **ilgili** olması yetmez; dilekçeye girecek içtihadın **müvekkil lehine** olması esastır. Süreç:
1. **Kapsamlı tara:** İstinaf (BAM/BİM), Yargıtay ve Danıştay içtihatlarını uyuşmazlık konusuna göre bul (doğru ihtisas dairesi için `oa-alan`).
2. **Lehe/aleyhe ayır:** bulunan her kararı müvekkil pozisyonu açısından sınıfla.
3. **Lehe olanı kullan:** dilekçede ve lehe argümanda yalnızca **müvekkil lehine** kararlara dayan (`oa-dilekce`).
4. **Aleyhe olanı `oa-antitez`'e devret:** müvekkil aleyhine kararlar **atılmaz** — gizli cephanelikte dahili tutulur; karşı taraf ileri sürerse ayırt etme (distinguishing), aşılmışlık, somut olayla farklılık veya lehe yorumla çürütmek için `oa-antitez`'e taşınır. Aleyhe içtihadı sunulan belgeye proaktif yazma.
5. **Dürüstlük sınırı:** "lehe seçmek" ≠ aleyhe/bağlayıcı otoriteyi mahkemeden gizlemek. Doğrudan uygulanabilir bağlayıcı bir içtihat aleyhe ise, stratejiyi (ayırt etme/uzlaşma) buna göre kur; yok sayıp riski müvekkile bildirmemek olmaz (HMK dürüstlük + `oa-kontrol`).

Bu 2-3 adımdaki lehe/aleyhe ayrımı, İçtihat Muhakeme Zinciri'nde biçimsel bir
karşılık bulur: her karar `oa-kiyas`/`oa-kontrol`'de **DAMGA** alanıyla
(`LEHE`/`ALEYHE`/`ALEYHE-AYIRT`/`NOTR`) resmen damgalanır ve
`_oa/cikti/NN-ictihat-muhakeme.md` kaydına yazılır (şema:
`oa-kiyas/references/ictihat-muhakeme-sablonu.md`). Bu parça künyeyi CEK
eder; damgayı **atamaz**.
**ZORUNLU SON SORU (v0.5.8.1 — şablon kullanılsın kullanılmasın, HER teyitte):**
"Bu karar sonradan AŞILMIŞ olabilir mi?" (İBK, içtihat/kanun değişikliği,
daire kayması). Şüphe varsa kararın tarihinden SONRAKİ aynı-konu kararlarına
kısa bakış; aşılmışsa kayda/kütüğe `**AŞAN-KAYNAK:**` + `**AŞILMA-TARİHİ:**`
işlenir — [G5]: aşılmış karar LEHE dayanak olarak dilekçeye giremez. Kütük
hangi biçimde tutulursa tutulsun bu iki alan atlanamaz.

## Kapsam — İstinaf + Yargıtay + Danıştay
Türk hukukundaki uyuşmazlığa dönük içtihadı üç düzeyde ara: **İstinaf (BAM hukuk/ceza, BİM idare/vergi)**, **Yargıtay**, **Danıştay**. İstinaf içtihadı özellikle güncel eğilim ve henüz Yargıtay/Danıştay'a taşınmamış meselelerde değerlidir; üçünü birden tara, ihtisas dairesini `oa-alan` ile hedefle.

## Üç arama dialect'i — operatör kuralları farklı (en sık hata)
- **`search_mevzuat.phrase` (Mevzuat Solr):** `+zorunlu`, `-hariç`, `"tam ifade"`, `kelime*`, `kelime~`. ⚠️ AND/OR/NOT yazıları parser'ı **bozar**; bitişik iki kelime zaten AND.
- **`ictihat_ara.phrase` (Bedesten Solr):** AND/OR/NOT **çalışır** (BÜYÜK HARF), `"tam ifade"` çalışır. ⚠️ Wildcard/fuzzy **yok**; en çok iki terimli AND en isabetli.
- **`search_within_mevzuat.query` (tek kanun, yerel boolean):** AND/OR/NOT (BÜYÜK HARF) **gerçekten** çalışır, `( )` gruplama, `"tam ifade"`.
Tüm dialect'lerde Türkçe diakritikleri koru (ç ş ğ ı İ ö ü).

## Kurum kararları ve TEK BELGE İÇİNDE arama (v0.5.6.1 — rehber sadeleştirmesi)
Bu bölüm, ayrı bir "işlem rehberi" skill'i olarak taşınan operasyonel özün
aileye alınmış hâlidir. Ayrı skill SİLİNDİ: araştırma disiplini iki yerde
yaşayamaz (ikiz-liste yasağı) — rehberi okuyup "araştırmayı öğrendim" sanmak,
bu ailenin bilinen halüsinasyon kapısıdır.

- **`kurum_karari_ara`** — `kurum` parametresiyle **11 kurumda** birleşik arama:
  `gib` (özelge) · `btk` · `rekabet` · `uyusmazlik` · `kik` · `sayistay` ·
  `bddk` · `kvkk` · `sigorta` (Sigorta Tahkim) · `reklam` (Reklam Kurulu) ·
  `kdk` (Kamu Denetçiliği). Filtreler kuruma özeldir; yabancı filtre
  `invalid_params` döndürür. `btk`/`rekabet`/`uyusmazlik` sonuçları belge
  içeriği TAŞIMAZ (PDF) — tam metni yalnız gerçekten gereken karar için
  `kurum_karari_getir` ile al (OCR maliyetli). Sayfalama: `page` +
  `results_per_page` (1–50).
- **⚠️ LAYER 0 — BU SATIR ANAYASALDIR (m.10):** `bddk` · `kvkk` · `sigorta` ·
  `reklam` sorguları **ÜÇÜNCÜ TARAF bir web servisine** (Tavily) gider; Yargı
  Pro'nun kendi indeksinde değildir. Bu dört kuruma yapılan aramalara
  **müvekkil adı, TCKN, esas no veya herhangi bir kişi-tanımlayıcı ayrıntı
  ASLA yazılmaz** — yalnız hukuki kavram yazılır. (`not_configured` dönebilir;
  sonuçlar tek sayfadır.)
- **`mevzuat_icinde_ara`** — tek bir mevzuat belgesi *İÇİNDE* yerel Boole
  araması. 50.000 kelimelik kanunu getirip sayfalamak yerine üç maddeyi anında
  yalıtır: anayasa m.1'in ("israftan kes, muhakemeden kesme") saf uygulaması.
  Operatörler **BÜYÜK HARF** ZORUNLU: `"açık rıza" AND sağlık` ·
  `(ihracat OR ithalat) AND NOT istisna`.
- **Kimlik kökeni:** resmî kanun numarası (`6698`) = `mevzuat_no`; ama
  `mevzuat_getir`/`mevzuat_icinde_ara` `mevzuat_ara`'nın döndürdüğü
  `mevzuat_id`'yi ister (`mevzuatgov:kanun:5:6698`). `unsupported_legacy_id`
  alırsan `mevzuat_ara` ile yeniden ara.
- **Sayfalama asimetrisi (sessiz hata kaynağı):** `ictihat_ara` **`pageNumber`**
  (camelCase) ister; mevzuat araçları **`page`**. `ictihat_ara`'ya `page`
  göndermek **sessizce yok sayılır** — ikinci sayfayı aldığını sanırsın, birinci
  sayfayı alırsın.
- **Maddesiz türler:** `TEBLIGLER` · `CB_KARAR` · `CB_GENELGE` maddeye
  bölünmez; `id_type: "outline"|"madde"` bunlarda `outline_desteklenmiyor`
  döner — tam metni getir ya da `mevzuat_icinde_ara` kullan.
- Tek bir Sigorta Tahkim dergisi sayısı içinde: `sigorta_dergi_icinde_ara`;
  tek bir Reklam Kurulu bülteni içinde: `reklam_bulten_icinde_ara`.

## Sunucu çağrı sırası (varsayılan — kolay akış)
Norm önce, içtihat sonra:
1. **Mevzuat** taraması (Mevzuat MCP / `search_mevzuat`) — norm katmanı.
2. **İçtihat:** **Yargı Pro**'yu çağır — **semantik arama** (`semantik_ictihat_ara`) burada açıktır. Semantik korpus güncel değilse **canlı `ictihat_ara`** uç noktasıyla teyit et.
- **Semantik ne zaman:** kelime tutmayan, kavramsal/anlam bazlı emsal ararken kullan. **Güncel karar veya tam künye** gerekiyorsa canlı `ictihat_ara` kullan — semantik korpus ~1 yıl eski (son ~12 ayın kararı yok).

## Yerleşik kalıplar
- **Bedesten:** `birimAdi` + `court_types` + tırnaklı `phrase`; çoğu iş `ictihat_ara` ile. HGK için `birimAdi="HGK"`. Tarih bandı (`kararTarihiStart/End`) ile içtihat değişikliğini izole et. Künyeyi alıp gerekçeyi `ictihat_getir` ile çek — snippet yetmez.
- **Mevzuat:** numara → `mevzuat_no` (6100 HMK, 2577 İYUK, 2004 İİK, 6216 AYM, 6098 TBK); `mevzuat_id` → `outline`/`search_within_mevzuat`/`get_mevzuat_document`. Büyük metinler `chunk` ile.
- **Mevzuat — yönetmelik araması:** yönetmelikler **birden çok alt tipe** dağılır (YONETMELIK / CB_YONETMELIK / KKY / UY); tek tiple arayıp "yok" deme. Önce **tipsiz başlık araması**, bulunamazsa alt tipleri sırayla tara. (Çocuk Teslimi Yönetmeliği dosyasında öğrenildi.)
- **Mevzuat — torba/değişiklik kanunu bulma:** `mevzuat_adi` ile jenerik torba başlığı araması **güvenilmezdir** (başlıklar uzun ve standart dışı). Güvenilir kalıp: **tarih-aralıklı kanun araması** (RG tarihi biliniyorsa banda daralt) → listeden numarayla seç. (7579 sayılı Kanun böyle bulundu — RG 22.05.2026, mevzuatId 352551; başlık araması başarısızdı.)
- **AYM:** `search_anayasa_unified` + `get_anayasa_document_unified`; bireysel başvuruda yalnızca AYM-teyitli kararlar.

## Bilinen sınırlar — baştan hazırlıklı gir
- **Bedesten gerçek phrase-search yapmaz:** uzun/çok terimli ifadede kelime bazında eşleştirir, şişkin sayı döndürür (TBK m.71'de 1.082.645 "kayıt"). Kısa 1-2 ayırt edici terim + daire/tarih filtresi kullan.
- **4. HD kısa ONAMA kararları uzun gerekçeyle indekslenmemiş;** bazı doktrinler beklenmedik rotadan gelir (TBK m.71 → TMK m.1007 / KTK m.85).
- **BAM Ceza Daireleri Bedesten indeksinde yok.**
- **Danıştay tam metni bazen `null` döner:** PDF kaynaklı, OCR'ı henüz tamamlanmamış kararlar metinsiz gelebilir. Bu "karar yok" demek değildir — künye geçerlidir; metni kanonik kaynaktan (UYAP / Kazancı-Lexpera / kararlar.danistay) ayrıca çek ve çalışmada durumu bildir.
- **Semantik arama** (`semantik_ictihat_ara`, Yargı Pro — API key ile açık): kavramsal emsal için güçlü, ama **korpus ~1 yıl eski (son ~12 ay yok)**, **`birimAdi` (daire) filtresi YOK** ve iki aşamalı boru hattında timeout verebilir. Daire-hedefli arama gerekiyorsa canlı `ictihat_ara` (`birimAdi` + `court_types` + tırnaklı `phrase`) kullan; güncel için de canlı unified; HGK için `birimAdi="HGK"`.
- **Rate limit:** çağrıları `sleep` ile arala.
- **OCR şüphesi — çalışmada BİLDİR:** Karar/mevzuat metni (`ictihat_getir`, mevzuat PDF/OCR) dönüşümden gelir; bozuk karakter, kopuk kelime, anlamsız sayı/harf dizisi olabilir. Aynen alıntı taşıyacak bir pasajda OCR kusuru sezilirse **sessizce düzeltme veya taşıma** — çalışmada açıkça "OCR şüphesi" diye işaretle ve kanonik kaynakla (Resmî Gazete / UYAP / Kazancı-Lexpera) bir kez teyit et. OCR hatasını dilekçeye taşımak, hatalı "birebir" alıntı demektir.

## Fallback zincirleri (gerçek kullanımdan)
- **İçtihat sunucusu:** **Yargı Pro** (semantik açık); güncel karar için **canlı `ictihat_ara`** ile teyit. Norm taraması (Mevzuat) bundan önce gelir.
- **Mevzuat MCP timeout →** `mevzuat.gov.tr` `web_fetch` (PDF: `web_fetch_pdf_extract_text=True`); birden çok kaynaktan teyit. (5510 m.21/4'te kullanıldı.)
- **Literatür MCP timeout →** kısa bekle + retry; ısrarlıysa web_search ile DergiPark, künyeyi ayrı doğrula.
- **Bedesten şişmesi →** terimi kısalt + daire/tarih; gerekirse Lexpera/Kazancı/UYAP Emsal (Can'ın erişimi).
- **Genel:** resmî kaynağa erişilemiyorsa **açıkça raporla**, sessizce hafızadan doldurma. Sağlık: `check_government_servers_health`.

## Araç keşfi ve sahte-teyit yasağı (kritik)
Bu dosyadaki araç adları kurulumdan kuruluma DEĞİŞEBİLİR (ör. aynı işlevin Türkçe adlı araçları: `ictihat_ara`, `semantik_ictihat_ara`, `mevzuat_ara`, `mevzuat_getir`). Sorgudan önce oturumda MEVCUT araç listesine bak ve gerçekte var olan aracı kullan; adı tutmuyor diye işlevi atlamak da, var olmayan bir araca çağrı yapılmış gibi sonuç yazmak da yasaktır. **"Teyitli" etiketi yalnızca fiilen yapılmış bir çağrıya konur** ve üçlü kayıtla yazılır: araç + sorgu + dönen künye/metin. Araç gerçekten yoksa veya erişilemiyorsa: fallback zinciri + açık beyan ("şu araç kapalı; bu künye teyit edilemedi").

## Ham MCP dökümü diske yazılır — kunye_teyit'in ikinci kaynağı (kritik)
`oa-kontrol/scripts/kunye_teyit.py` teyit edici kaynak evrenini SADECE ikisinden okur: `_oa/teyit/kunye-teyit.md` kütüğü + `_oa/teyit/dokum/` ham MCP dökümleri. `_oa/cikti/` (taslak/antitez/kıyas gibi model çıktıları) teyit kaynağı DEĞİLDİR — oraya yazılan bir izi kunye_teyit "teyitli" saymaz, yalnız [BİLGİ] şerhi verir. Bu ikinci kaynağı (döküm dizini) besleyen adım BURADADIR — atlanırsa teyit evreninin yarısı kalıcı boş kalır ve kunye_teyit sistematik olarak yanlış-pozitif TEYİTSİZ üretir.

`oa_hafiza.py teyit` **iki araç sınıfı** ayırır (P0-2, v0.5.5) — hangi komutu yazacağın `--arac` değerine göre değişir:

- **ARAMA sınıfı** (`ictihat_ara`/`semantik_ictihat_ara`/`aym_ictihat_ara`/`aihm_ictihat_ara` — tam metin DÖNMEZ, yalnız aday künye/snippet): `--damga` YASAKTIR (metinsiz damga vurulamaz). Tek-komut:
  `python oa-pipeline/scripts/oa_hafiza.py teyit --arac ictihat_ara --sorgu "<sorgu>" --sonuc "<aday künyeler/özet>" [--dokum-icerik "<ham snippet>"]`
  — `--dokum-icerik` verilirse script kendi döküm dosyasını `_oa/teyit/dokum/`'a YAZAR (ayrıca dosyayı elle oluşturup `--dokum <yol>` ile bağlaman GEREKMEZ).
- **GETİR sınıfı** (`ictihat_getir`/`kurum_karari_getir` — tam metin DÖNER): `--damga LEHE|ALEYHE|ALEYHE-AYIRT|NOTR` ZORUNLUDUR (damgasız içtihat kütüğe, kütüksüz künye çıktıya GİREMEZ) — bu, İçtihat Muhakeme Zinciri'nin (MODÜL 2) tek-komut ritüelidir, MUHAKEME adımını (`oa-kiyas`/`oa-kontrol`) de aynı çağrıda tetikler:
  `python oa-pipeline/scripts/oa_hafiza.py teyit --arac ictihat_getir --sorgu "<sorgu>" --sonuc "<Yargıtay 4. HD, E. 2023/1234, K. 2023/5678>" --damga LEHE --dokum-sinifi tam-metin --bag "<DAVAYA-BAĞ, ≥40 karakter>" --ilgili-kisim "<döküm içinde VERBATİM geçen alıntı>" --dokum-icerik "<ham tam metin>"`
  `--sonuc` içinde ayrıştırılabilir bir `E./K. YYYY/NNNN` künyesi bulunmalıdır (yoksa RET — çıplak künye üretmez). Aynı künye için ikinci bir `teyit --damga` çağrısıyla FARKLI bir damga vermek (ör. ALEYHE→LEHE) sessizce kabul edilmez; bilinçli değişim `--damga-degistir "<gerekçe, ≥40 karakter>"` ister.

Her iki sınıfta da dökümü **elle** yazıp yalnızca `--dokum <mevcut-dosya>` ile bağlamak da geçerlidir (ör. daha önce başka bir araçla üretilmiş bir ham metni yeniden kullanmak için); ama normal akışta `--dokum-icerik` tek adımda hem dosyayı yazar hem bağlar.

## Karar çekme (CEK) — ictihat_getir → ham md → muhakeme girdisi
İçtihat Muhakeme Zinciri'nde bu parçanın rolü **yalnızca CEK**tir; MUHAKEME
(illiyet + LEHE/ALEYHE/ALEYHE-AYIRT/NOTR damgası) `oa-kiyas`/`oa-kontrol`'e
aittir — bu iki adım **karıştırılmaz**. CEK adımı:
1. Künyeyi bul ve teyit et (yukarıdaki akış).
2. Kararın **tam metnini** `ictihat_getir`/`ictihat_getir`
   (veya kurulumdaki eşdeğer araç) ile çek — snippet yetmez.
3. Ham metni "Ham MCP dökümü diske yazılır" bölümündeki kuralla
   `_oa/teyit/dokum/<tarih>-<arac>-<slug>.md` yoluna yaz.
4. Bu dosya adını `oa-kiyas`/`oa-kontrol`'e **KAYNAK-IZI** olarak devret —
   MUHAKEME adımı bu izi kullanarak `_oa/cikti/NN-ictihat-muhakeme.md`
   kaydını üretir (alan şeması: `oa-kiyas/references/ictihat-muhakeme-sablonu.md`).
5. **KAYNAK BAĞLANTISINI AYNI ANDA YAKALA (v0.5.5.3 — avukat talimatı).**
   Aracın döndürdüğü resmî karar bağlantısı (URL) **o anda** kütüğe geçirilir:
   `oa_hafiza.py teyit … --kaynak-url "https://…"`. Bu bağlantı, dilekçede
   künyenin hemen ardından **parantez içinde** yayımlanır.
   **Neden tam bu anda:** bağlantıyı yakalayabileceğin tek an, kararı fiilen
   çektiğin andır. Yazım aşamasında model bir URL *hatırlayamaz*, ancak
   *uydurabilir* — ve uydurma bağlantı çıplak künyeden DAHA KÖTÜDÜR: çıplak
   künye "teyit edilmedi" der, sahte bağlantı "teyit edildi" der. Bu yüzden
   kural tek yönlüdür: **URL teyit anında kaydedilmediyse, dilekçede parantez
   hiç açılmaz.** Araç bir bağlantı döndürmüyorsa bu bir eksiklik değildir —
   künye bağlantısız yazılır, uydurulmaz.
Bir karar **çekilmiş olması** onun **muhakeme edilmiş** sayılması için
yeterli değildir — damga atanmadan (NOTR = "muhakeme edilmemiş",
fail-closed) hiçbir içtihat dilekçeye giremez.

**İÇTİHAT PORTFÖYÜ (M6, Paket D — v0.5.5):** birden fazla LEHE/ALEYHE-AYIRT
karar biriktiğinde HEPSİ gövdeye YAZILMAZ — v0.3.20 FINAL-MAX deseni gereği
gövdeye en güçlü 3-5'i (HGK/İBK > daire, yeni > eski, ihtisas dairesi)
girer, kalanı kütükte (`_oa/cikti/03-ictihat-muhakeme.md`) yedek durur (bkz.
`oa-dilekce/SKILL.md` "İÇTİHAT PORTFÖYÜ"). CEK adımında bu sıralamayı
kolaylaştırmak için her künyenin merci+daire+tarihi (HGK/İBK ayrımı dahil)
KAYNAK-IZI'yla birlikte açıkça not edilir.

## Aktif çıkarım refleksi
Edilgen "getir-koy" yapma. Bulduğun her teyitli kararı **müvekkil lehine bir argümana bağla**; aleyhe bir içtihat çıkarsa onu **ayırt etmenin (distinguishing)** yolunu ara; ve nötr aramanın yanı sıra müvekkilin konumunu **güçlendirecek** aramayı da kendiliğinden kur. İçtihat bir liste değil, lehe inşa edilecek malzemedir.

## Yol haritası (gelecek hook — henüz aktif değil)
İleride bu parça, resmî MCP kaynaklarının **yanına** Can'ın yerel RAG'ini de bir kaynak olarak sorgulayabilir: vektörlenmiş alan kitapları (ör. Uyar İcra ve İflas Hukuku ciltleri), `bge-m3`/ChromaDB, FastMCP köprüsü. **Disiplin değişmez:** yerel RAG ve doktrin **doğrulamaz, yönlendirir**; künye otoritesi yine yalnızca Yargı/Mevzuat/AYM'dir. Telif uyumu (alıntı sınırı) yerel korpusta da geçerli. KVKK + meslek sırrı için Privacy Layer 0 (yerel DB) önce gelir.

## Kompozisyon
`ortak-avukat` çekirdeği bir argüman doğrulanması gerektiğinde bu parçayı çağırır. `oa-dilekce` ile: dilekçedeki her atıf buradan teyitli gelir. `oa-alan` ile: alan tespit edilir, sorgu burada kurulur.

## Öğrenme günlüğü
Yeni bir sorgu kalıbı, indeks boşluğu veya fallback öğrenildiğinde bu dosyaya işle, aşağıya tek satır ekle, yeniden paketle.
## Anayasal düstur — usul esasa üstündür
Usulün esasa takaddümü ailenin anayasal düsturudur: usulden düşen dosya esasa hiç giremez; süre, usul hukukunun parçası ve telafisiz tek hatadır. Dosyada usul meselesi (süre, görev, yetki, dava şartı) tespit edildiğinde **usul içtihadı esas içtihadından ÖNCE aranır** — usulden kazanılan dosyada esas araştırması maliyeti düşer; karşı tarafın süre kaçırmasının usuli sonucu (ret/inkâr/dinlenmeme) içtihatla teyit edilerek yazılır.

## Anayasal bloklar — tek kaynak (anayasa.md)
Bu parça, ailenin ortak anayasal ilkelerine tabidir — **Çaba/token standardı** (model/efor kullanıcının tercihi; muhakemede/doğrulamada/çıktı kalitesinde tasarruf YOK, yalnız mekanik katmanda kayıpsız verimlilik), **Örnekleme ilkesi** (konu sınırlaması yok — kapsam TÜM Türk hukuku), **Doğaçlama meşruiyeti** (yöntem serbest, olgu MCP-teyitli), ayrıca Doğrulama mimarisi, Anonimleştirme ve Layer 0 gizlilik. **Tek ve yetkili kaynak: `ortak-avukat/references/anayasa.md`.** (Bu parça alt-ajan olarak koşarken bu ilkeler `oa-pipeline/scripts/oa_hafiza.py ajan-brif` ile taşınır.)

## Başbakan denetimi (anayasal)
Bu parça, ailenin Başbakanı `oa-pipeline`'ın icra+denetimine tabidir: çağrıldığında disiplini İSTİSNASIZ ve tam işletilir (ama/fakat/token-tasarrufu gerekçesiyle kestirme YASAK). Görev savsaklanmaz; gerçekten yapılamayan bir şey varsa dürüstçe belirtilir ("yaptım" denmez) ve alternatif yöntem üretilir. Önemli olan proses ve çıktı kalitesidir.

## Halüsinasyon teftişine tabi (anayasal)
Bu parçanın getirdiği HER künye (mahkeme/daire, esas-karar no, tarih) Başbakan'ın (oa-pipeline) olgu-teftişine tabidir: çıktıya girmeden Yargı Pro/Mevzuat MCP'den teyitli olduğu ayrıca doğrulanır. Teyit edilemeyen künye/madde DOĞRUDAN DIŞLANIR — 'doğrulanamadı' işaretlenir, asla teyitliymiş gibi bırakılmaz. Aşama-aşama kontrol: bir adımda teyitli künye sonraki adımda sapmamalı (esas/karar no, daire sabit).

## Fiziksel aktivasyon — simülasyon yasağı (anayasal)
Bu parça yalnızca ÜÇ kanıttan en az biriyle "çalıştı" sayılır: (1) Skill aracıyla FİİLEN çağrıldı ve bu gövde bağlama yüklendi (kullanıcının `/oa-ictihat` komutuyla eşdeğer); (2) scripti gerçekten koştu ve çıktısı görünür; (3) gerektirdiği MCP çağrısı fiilen yapıldı (araç + sorgu + sonuç kaydıyla). Kısa description her zaman bağlamda durur — o VİTRİNDİR, disiplin değildir; gerçek disiplin bu gövdededir. Bu yüzden hiçbir parça bu parçayı description'ından TAKLİT EDEMEZ; bu parça da başka bir parçanın işine ihtiyaç duyduğunda onu Skill aracıyla fiilen çağırır (olmuyorsa SKILL.md'sini Read ile yükler; o da olmuyorsa "FİZİKEN YÜKLENEMEDİ" diye açıkça yazar). Yapılmamış çağrı 'yapılmış', koşmamış script 'koşmuş' gösterilemez — bu, halüsinasyonun ta kendisidir. Devir alırken/verirken kısa DEVİR PAKETİ (ne yapıldı → ne bekleniyor → hangi kanıt) kullanılır ve pipeline defterine (`oa-pipeline/scripts/pipeline_kayit.py`) işlenir. Bu parçanın ürettiği her kalıcı çıktı (JSON/rapor/devir paketi) çalışılan klasörün `_oa/` yerel hafıza kökünde yaşar (yapı: `oa-pipeline` → Çalışma Kökü).

## Değişiklik Günlüğü
Tam günlük `references/degisiklik-gunlugu.md`'dedir (bağlam ekonomisi için ayrıldı — içerik aynen korunur; yeni kayıtlar oraya işlenir). Güncel sürüm: **v3.26**.

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

## v0.5.8 — AŞILMIŞLIK SORUSU (zorunlu teyit adımı)

Her künye teyidi + DAMGA yazımında tek soru daha sorulur: **"Bu karar sonradan
aşılmış olabilir mi?"** (İBK, içtihat değişikliği, kanun değişikliği, daire
kayması). Şüphe varsa Yargı Pro'da kararın tarihinden SONRAKİ aynı-konu
kararlarına kısa bakış atılır; aşılmışlık tespit edilirse muhakeme kaydına
`**AŞAN-KAYNAK:**` / `**AŞILMA-TARİHİ:**` işlenir (şablon: oa-kiyas
ictihat-muhakeme-sablonu.md). [G5] kapısı DAMGA=LEHE + aşılmış + dilekçede
atıf birleşimini TESLİM ENGELİ sayar — aşılmış karar lehte dayanak olamaz.

**Üretici uç (v0.5.8.4):** alanları elle yazma — aşılmışlık, teyit komutunun
kendi bayraklarıyla işlenir: `oa_hafiza.py teyit … --damga <DAMGA>
--asan-kaynak "<künye/norm>" --asilma-tarihi GG.AA.YYYY --gecerlilik-bitis
GG.AA.YYYY` (üç bayrak YALNIZ `--damga` ile geçerlidir; damgasız çağrı RET —
üç alan tek komutla yazılır, lehe-denetimde AŞILMIŞ çıkan karar böyle işlenir;
kullanım örneği şablondadır).

## v0.5.8.5 — A1 TRİYAJ (tam-okuma + LEHE şartı)

> **ÇEKİRDEK (kullanıcı direktifi — aynen):** "Müvekkil aleyhine HİÇBİR yargı
> kararı dilekçeye giremez. MCP'den çekilen TÜM kararlar İSTİSNASIZ baştan
> sona (TAM METİN) okunur. LEHE ise dilekçeye; ALEYHE ise CEPHANELİĞE
> (strateji/farkındalık); NÖTR kütükte kalır."

CEK adımının triyaj yükümlülükleri:

- **Tam metni oku, sonra damgala.** `ictihat_getir` ile çekilen HER karar
  baştan sona okunur. **Arama sonucu parçasından alıntı YASAKTIR** — ARAMA
  sınıfı tam metin döndürmez; snippet'ten alıntı "birebir" iddiasıyla
  yapısal yalandır. Alıntı daima GETİR dökümünden gelir.
- **Okuma sınıfını beyan et:** karar baştan sona okunduysa teyit komutuna
  `--dokum-sinifi tam-metin` ekle (yalnız GETİR sınıfında geçerlidir; ARAMA
  ve mevzuat/kurum çağrısında RET). Sınıf beyan edilmezse script görünür
  UYARI basar ve dürüst `ilgili-kisim` işler; sınıfsız ESKİ kütük satırı da
  okur tarafında `ilgili-kisim` sayılır — tam-okuma İDDİA EDİLMEZ.
- **Duyulmuş işareti:** karşı tarafın FİİLEN ileri sürdüğü kararı
  `--duyulmus` ile işaretle (kütüğe `DUYULMUS=EVET` yazılır) — [G6] ayırt
  istisnasının kütük ayağı budur; işaretsiz aleyhe karara preemptive ifşa
  yasağı (m.6) uygulanır.
- **[G6] kapısını baştan besle:** `ictihat_muhakeme_denetim.py` dilekçedeki
  her künye için kütükte TAM-METİN sınıfı döküm arar; yoksa TESLİM ENGELİ.
  Tam-metinsiz künyeyi zincire hiç sokma — kapıda değil, kaynağında çöz.

Örnek (GETİR + tam-okuma + damga; alan örnekleri:
`oa-kiyas/references/ictihat-muhakeme-sablonu.md`):

```bash
python oa-pipeline/scripts/oa_hafiza.py teyit --arac ictihat_getir --sorgu "<sorgu>" --sonuc "<künye>" --damga LEHE --dokum-sinifi tam-metin --bag "..." --ilgili-kisim "..." --dokum-icerik @ham.md
```

Aleyhe + karşı tarafça fiilen ileri sürülmüş karar: aynı komuta
`--damga ALEYHE-AYIRT --duyulmus --ayirt "<somut fark>"` verilir.

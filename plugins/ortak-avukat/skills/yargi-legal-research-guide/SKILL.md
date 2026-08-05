---
name: yargi-legal-research-guide
description: Türk hukuku veya mahkeme kararlarını Yargı MCP araçlarıyla araştırırken kullan (sürüm 2026-07-08b)
---

# Türk Hukuku Araştırma Kılavuzu (Yargı MCP)

Kılavuz sürümü: 2026-07-08b

Bu kılavuz, otonom bir yapay zekâ ajanı olan seni, Yargı MCP (Model Context Protocol) sunucusuyla Türk hukuku araştırma iş akışlarında akıcı kılar. Aşağıdaki 8 çekirdek araç (artı isteğe bağlı bir beta araç — Bölüm 6) mevzuatı, mahkeme içtihatlarını ve kurum kararlarını (özelge, BTK/Rekabet/KİK, Sayıştay, Uyuşmazlık, BDDK/KVKK/Sigorta Tahkim, Reklam Kurulu, KDK/Ombudsmanlık) çapraz sorgulayarak soruları doğru yanıtlamanı sağlar.

## 1. Türk Hukuk Normlar Hiyerarşisi

Alt seviye bir norm, üst seviye bir normla çelişemez. **Sorun için en yüksek *işlevsel* kaynaktan başla.** Sıradan özel hukuk, vergi, iş, ceza ve idare hukuku sorularında önce ilgili Kanun'u veya düzenlemeyi belirle. Anayasa'yı; sorun temel haklar, normlar hiyerarşisi, iptal, anayasal yorum veya alt normların geçerliliği ile ilgili olduğunda kullan.

1. **Anayasa**: En üstün norm.
2. **Kanun**: TBMM tarafından çıkarılır. Çoğu sorgu için birincil başlangıç noktası.
3. **Kanun Hükmünde Kararname (KHK)**: Tarihsel olarak Bakanlar Kurulu'nca çıkarılmıştır; genellikle Kanun'a eşdeğerdir ama temel hakları düzenlemede sıkı sınırları vardır.
4. **Cumhurbaşkanlığı Kararnamesi (CBK)**: Cumhurbaşkanı'nca çıkarılır; Parlamento'nun yasama yaptığı alanlarda kesinlikle Kanun'a tabidir. Bir Kanun ile CBK çatışırsa, Kanun üstün gelir.
5. **Tüzük**: Daha eski araçlar (çoğunlukla kaldırılıyor veya değiştiriliyor).
6. **Yönetmelik**: Kanunların uygulanmasını düzenlemek için bakanlıklar, Cumhurbaşkanı veya kamu tüzel kişilerince çıkarılır.
7. **Tebliğ**: Ayrıntılı idari yönergeler ve teknik kurallar (vergi ve idare hukukunda çok yaygın).

**Milletlerarası Antlaşmalar (Anayasa m.90/5)** bu merdivende tek bir basamağa değil, merdivenin yanında konumlanır. Usulüne göre onaylanmış antlaşmalar Kanun hükmündedir ve anayasaya aykırılıkları ileri sürülemez; kritik olarak, **temel hak ve özgürlüklere** ilişkin bir antlaşma ile aynı konudaki bir Kanun çatışırsa, **antlaşma üstün gelir** (ör. AİHS). Bunlar bu 5 araçla ARANAMAZ — bir temel-hak çatışması söz konusuysa ilgisini bildir ve kullanıcıyı antlaşma metnine ve Anayasa Mahkemesi (AYM) içtihadına yönlendir.

Mahkeme İçtihatları normlar hiyerarşisinde bir basamak DEĞİLDİR. *Yargıtay* (özel hukuk/ceza) ve *Danıştay* (idari) kararları, birincil mevzuat değil, ikna edici yorumdur. İstisnalar: bağlayıcı *İçtihadı Birleştirme Kararları* ve *Anayasa Mahkemesi* iptal/bireysel-başvuru kararları norm-seviyesinde etki taşır. **Araç uyarısı**: AYM ve İçtihadı Birleştirme kararları `ictihat_ara`'nın `court_types` değerleri arasında DEĞİLDİR — bunları bu 5 araçla getiremezsin. Önem taşıdıklarında bunu açıkça söyle ve kullanıcıyı Resmî Gazete'ye veya AYM veritabanına yönlendir.

## 2. Araştırma Araçlarına Genel Bakış

Sunucu dört alanda 8 çekirdek araç sunar: **Mevzuat**, **Mahkeme Kararları (İçtihat)**, **Anayasa Mahkemesi** ve **Kurum Kararları**.

**Mevzuat Araçları:**
*   `mevzuat_ara`: Tüm mevzuat veritabanında (~27 bin belge) global arama. Kanunların, yönetmeliklerin ve tebliğlerin metadata'sını ve iç kimliklerini bulur.
*   `mevzuat_getir`: Çok-amaçlı getirme aracı. Bir belgenin tam metnini, belirli bir *Madde*'sini, *Gerekçe*'sini veya yapısal içindekiler tablosunu (outline) getirir.
*   `mevzuat_icinde_ara`: Tek bir mevzuat belgesi *içinde* odaklı, yerel Boole araması yapar. Medeni Kanun gibi devasa kodlarda gezinmek için son derece güçlüdür.

**Mahkeme Kararları Araçları:**
*   `ictihat_ara`: 5 mahkeme türünde (Yargıtay, Danıştay, yerel, istinaf, KYB) milyonlarca kararda global Solr araması.
*   `aym_ictihat_ara`: Anayasa Mahkemesi kararlarında arama — varsayılan tüm türler ya da filtreli: `norm_denetimi`, `bireysel_basvuru`, `siyasi_parti`, `yuce_divan`.
*   `aihm_ictihat_ara`: AİHM (Avrupa İnsan Hakları Mahkemesi) kararlarında HUDOC üzerinden arama — kararlar + kabul edilebilirlik kararları. Varsayılan davalı Türkiye'dir (`ulke`); `HEPSI` tüm devletleri arar.
*   `ictihat_getir`: HERHANGİ bir mahkeme kararının tam metnini getirir — Bedesten `documentId`'leri, AYM `document_id`'leri (`anayasa:<guid>`) ve AİHM `document_id`'leri (`aihm:<itemid>`) dâhil. 40.000 karakteri aşan belgeler sayfalanır; `page_number` ile gez.

**Kurum Kararları Araçları:**
*   `kurum_karari_ara`: `kurum` parametresi ile 11 kurum üzerinde birleşik arama — `gib` (GİB özelgeleri), `btk` (BTK kurul kararları), `rekabet` (Rekabet Kurumu), `uyusmazlik` (Uyuşmazlık Mahkemesi), `kik` (Kamu İhale Kurumu), `sayistay`, `bddk`, `kvkk`, `sigorta` (Sigorta Tahkim), `reklam` (Reklam Kurulu bültenleri), `kdk` (Kamu Denetçiliği Kurumu). Filtreler kuruma özeldir; seçtiğin `kurum`'a ait olmayan bir filtre geçmek `invalid_params` döner. ⚠️ `btk`/`rekabet`/`uyusmazlik` sonuçları belge içeriği taşımaz (PDF): alakayı filtrelerle daralt, belge metnini yalnız gerçekten gerekli kararlar için `kurum_karari_getir` ile al (OCR maliyetli). `include_snippets: true` yalnız `gib` ve `kdk`'da ek belge getirir. Sayfalama için `page` + `results_per_page` (1–50). ⚠️ `bddk`/`kvkk`/`sigorta`/`reklam` HARİCİ web araması (Tavily) ile keşfedilir: `not_configured` dönebilir, sonuçlar tek sayfadır ve **arama kelimeleri üçüncü-taraf bir servise gider — bu sorgulara ASLA müvekkil adı veya kişi-tanımlayıcı ayrıntı yazma.** Tek bir Sigorta Tahkim dergisi sayısı İÇİNDE arama için `sigorta_dergi_icinde_ara`; tek bir Reklam Kurulu bülteni İÇİNDE için `reklam_bulten_icinde_ara`.
*   `kurum_karari_getir`: `document_id` ile tam karar metnini Markdown olarak getirir. `ictihat_getir` ile aynı 40.000 karakterlik sayfalama.

## 3. Kritik Tuzaklar ve Sözdizimsel Kapanlar

Bu bölümü dikkatle oku. Ajan hatalarının çoğu bu kuralları çiğnemekten doğar.

*   **Sorgu Hijyeni — Anahtar Kelime Çıkar, Soruyu Asla Yapıştırma**: Kullanıcının tam cümlesini bir `phrase`/`query`/`mevzuat_adi` parametresine BOŞALTMA. Uzun sorgu HER ZAMAN yanlıştır ama motora göre zıt nedenlerle: mevzuat araçları her boşlukla ayrılmış kelimeyi AND'ler (40 kelimelik soru → neredeyse sıfır sonuç), `ictihat_ara` ise OR'lar (→ yüz binlerce alâkasız isabet). Hukuki sorunu 2–5 terime damıt. Tek dev arama yerine birkaç dar arama çalıştır.
*   **AYM Araması Üçüncü, Operatörsüz Bir Lehçedir**: `aym_ictihat_ara.query` DÜZ Türkçe kelime alır — `+` yok, operatör-tırnak yok, AND/OR/NOT yok, joker yok. Her ek kelime sonucu DARALTIR. Tarihler ISO `YYYY-MM-DD`. Norm-denetimi davalarını `esas_no`/`karar_no`, bireysel başvuruları `basvuru_no` ile işaretle.
*   **AİHM (`aihm_ictihat_ara`) HUDOC lehçesi kullanır**: boşluk=AND, `"tam söz öbeği"`, OR/NOT ve parantez çalışır; alan sözdizimi (`:`/`=`) reddedilir. Varsayılan davalı Türkiye; `dil: "TUR"` satırını tercih et. AİHS maddesiyle hedefle: `madde`/`ihlal`/`ihlal_yok`. `metin_var: false` ise aynı davanın İngilizce/Fransızca satırını getir.
*   **Türkçe Diakritikleri Koru**: Her zaman tam Türkçe karakterlerle yaz (ç, ş, ğ, ı, İ, ö, ü) — `karari` değil `kararı`. Asla ASCII'ye çevirme.
*   **Solr ile Boole Sözdizimi Ayrımı**:
    *   `mevzuat_ara` (`phrase`) **hiçbir operatör kabul etmez**: tırnak, `+`, `-`, joker ve AND/OR/NOT birebir metin olarak aranır. Önce tam öbek denenir, sonuç yoksa kelimeler AND'lenir.
    *   `mevzuat_icinde_ara` (`query`) yerel değerlendirilir. Büyük harf `AND`, `OR`, `NOT` kullanmak ZORUNDASIN.
*   **Sorgu Kitapçığı (motora göre operatörler)**:
    *   `ictihat_ara.phrase` (Bedesten Solr — **boşluk OR'lar**): tam hedef → `"imar planı"` · iki kavram birlikte → `+kamulaştırma +"bedel tespiti"` · dışla → `mülkiyet -kira` · iki sebepten biri → `"haksız fiil" OR "sebepsiz zenginleşme"`. Joker/fuzzy/yakınlık yok.
    *   `mevzuat_ara.phrase` (operatör YOK): 2-5 anahtar kelime. Sıralama Resmî Gazete tarihine göredir, alâka sıralaması yoktur → `mevzuat_adi` veya `mevzuat_no` ile daralt.
    *   `mevzuat_icinde_ara.query` (BÜYÜK harf operatörler): `"açık rıza" AND sağlık` · `(ihracat OR ithalat) AND NOT istisna`.
    *   Sonda doğrulandı: tek başına `"etkin pişmanlık"` → 129K, `"nitelikli dolandırıcılık"` → 100K, yan yana → 228K ≈ birleşim; `+"etkin pişmanlık" +"nitelikli dolandırıcılık"` → 1.184, gerçek kesişim.
*   **Tarih Anlamları (aynı format, farklı anlam)**: İkisi de **ISO 8601 `YYYY-MM-DD`** alır. Fark *hangi* tarihe göre filtrelediğidir. `mevzuat_ara` (`resmi_gazete_tarihi_start/end`) **Resmî Gazete yayım tarihini** hedefler, **yürürlük tarihini DEĞİL** — her zaman kanunun `Yürürlük` maddesini ve değişiklik notlarını oku. `ictihat_ara` (`kararTarihiStart/End`) **karar tarihine** göre filtreler.
*   **Kimlik Kökeni (`mevzuat_no` vs `mevzuat_id`)**: Resmî kanun numarası (KVKK için "6698") `mevzuat_no`'dur. `mevzuat_getir`/`mevzuat_icinde_ara` ise `mevzuat_ara`'nın döndürdüğü `mevzuat_id`'yi ister (`mevzuatgov:kanun:5:6698` biçiminde). `unsupported_legacy_id` alırsan `mevzuat_ara` ile yeniden ara.
*   **`mevzuat_no`'yu Asla Uydurma**: Emin değilsen önce `mevzuat_adi` ile ara, sonra numarayı yanıttan çıkar. Uydurulan numaralar sessizce sıfır-sonuç verir.
*   **Sayfalama Parametresi Asimetrisi**: `ictihat_ara` **`pageNumber`** (camelCase); mevzuat araçları **`page`**. `ictihat_ara`'ya `page` göndermek sessizce yok sayılır. Sayfa boyutları: bedesten `page_size` ≤100, `mevzuat_ara` 20, `mevzuat_icinde_ara` 50, `kurum_karari_ara` `results_per_page` ≤50.
*   **Varsayılan Mahkeme Türleri**: `ictihat_ara` varsayılanı `['YARGITAYKARARI', 'DANISTAYKARAR']` — yalnız yüksek mahkemeler. 2016 sonrası özel hukuk istinaf eğilimleri için `court_types`'a `ISTINAFHUKUK`'u açıkça GEÇMELİSİN. İstinaf kararları bağlayıcı doktrin değildir.
*   **Alâka vs Tarih Sıralaması (`sort_by`)**: `ictihat_ara` `phrase` varsa ALÂKA-sıralıdır. Kronoloji önemliyse açıkça `sort_by: "date"` geç. `sort_direction` YALNIZCA tarih sıralamasına uygulanır. `mevzuat_ara`'da alâka sıralaması YOKTUR.
*   **İki Kademeli Snippet**: cache'teki sonuçlar her zaman ücretsiz `snippet` taşır. `include_snippets: true` ile 5 taneye kadar cache-siz üst isabet getirilir — bu getirmeler KOTASIZDIR ve cache'i herkes için ısıtır. PDF kararları atlanır. Geniş taramalarda kapalı bırak; triyajda aç.
*   **`date_suspect` Bayrağı**: karar yılı bariz upstream yazım hatası olan girdiler (`21.09.6006`) bunu taşır. İşaretli tarihe asla güvenme — belgeyi getir ve gerçek tarihi metinden oku.
*   **Docket-Numarası Hedefleme (`esas_no` / `karar_no`)**: `YIL/SIRA` formatı (ör. `YYYY/NNNNN`). Kullanıcı zaten numara verdiyse phrase-araması yerine bunlarla filtrele.
*   **Maddesiz Türler**: `TEBLIGLER`, `CB_KARAR`, `CB_GENELGE` maddeye bölünmüyor — `id_type: "outline"|"madde"` bunlarda `outline_desteklenmiyor` döner. Tam metni getir ya da `mevzuat_icinde_ara` kullan.
*   **Talep Üzerine PDF OCR**: Cumhurbaşkanlığı genelge/kararları çoğu zaman PDF'tir; ilk getirme yavaş olur (2-3 sn).
*   **Gerekçe Yok**: Kaynak mevzuat.gov.tr gerekçe yayımlamıyor. Yasama gerekçesi gerekiyorsa TBMM kaynaklarına bak. (Bazı kanunlarda `gerekce_id` döner — varsa `id_type: "gerekce"` ile getirilebilir; yoksa uydurma.)
*   **Mülga Kanunlar**: Varsayılan aramalar yürürlükteki kanunları hedefler. Tarihsel senaryolar için `mevzuat_tur_list`'e açıkça `["MULGA"]` geç. **Yürürlükten kaldırma önceki içtihatları otomatik geçersiz kılmaz** — geçici maddeler çoğu zaman eski kanunu yaşatır.

## 4. Görüş İçeren Strateji Sezgileri

*   **Bilindiğinde `mevzuat_no`'yu Tercih Et**: "TTK" veya "KVKK" soruluyorsa resmî numarayı (6102, 6698) bul ve `mevzuat_ara(mevzuat_no=...)` kullan. Başlıkla aramaktan sonsuz kat kesindir.
*   **Genişten Başla, Sonra Daralt**: Önce temel Kanun'u güvenceye al, ilgili *Madde*'yi oku, sonra usulü belirleyen *Yönetmelik*/*Tebliğ*'i ara.
*   **Bağlam İçin Outline'ları Kullan**: Devasa kanunlarda (TBK 6098) körlemesine arama kaotik sonuç verir. Önce outline, sonra ilgili Bölüm, sonra o Madde'ler.
*   **`mevzuat_icinde_ara`'yı Acımasızca Kullan**: 50.000 kelimelik kanunu getirip sayfalamak yerine 3 maddeyi anında yalıt.
*   **Daireyi Oku, Otoriteyi Tart (`birimAdi`)**: Genel Kurul kararları tek-daire kararlarını geçer: **HGK** ve **CGK** bir Daire'den (`H1`–`H23`, `C1`–`C23`, Danıştay `D1`–`D17`) çok daha fazla otorite taşır; **İçtihadı Birleştirme (İBK)** doğrudan bağlayıcıdır. Çatışmada üst kurulu tercih et.
*   **Güncelliği Doğrula**: İçtihat bulduktan sonra, modern olaylara uygulamadan önce maddenin güncel metnini, değişiklik notlarını, yürürlük tarihlerini ve *geçici maddeleri* kontrol et. *Lex mitior* bir **ceza hukuku** ilkesidir (TCK 5237 m.7); özel/idari işlerde varsayılan **geriye yürümezlik** ve *kazanılmış hakların* korunmasıdır — ceza kuralını ceza-dışı alanlara taşıma.

## 5. Uçtan Uca Örnek Senaryolar

### Örnek 1: Yazılım İhracatı için KDV İstisnası
İki kanun birlikte çalışır — KDV Kanunu 3065 ve Teknoloji Geliştirme Bölgeleri Kanunu 4691.

1. `mevzuat_ara {"mevzuat_no": "3065", "mevzuat_tur_list": ["KANUN"]}`
2. `mevzuat_ara {"mevzuat_no": "4691", "mevzuat_tur_list": ["KANUN"]}`
3. `mevzuat_icinde_ara {"mevzuat_id": "<4691_ID>", "query": "yazılım AND (ihracat OR \"hizmet ihracı\") AND istisna"}`
4. `mevzuat_getir {"id": "<3065_ID>", "id_type": "outline"}` → Madde 11 "İhracat istisnası"
5. `mevzuat_getir {"id": "<MADDE_ID>", "id_type": "madde"}`
   *Kısayol: madde numarasını biliyorsan outline'ı atla — `{"id":"<ID>","id_type":"madde","madde_no":11}`*
6. `mevzuat_ara {"phrase": "+\"teknoloji geliştirme bölgesi\" +yazılım +istisna", "mevzuat_tur_list": ["TEBLIGLER"]}`

### Örnek 2: Kiracı Hakları ve İhtiyaç Nedeniyle Tahliye (TBK)
1. `mevzuat_ara {"mevzuat_no": "6098"}`
2. `mevzuat_getir {"id": "<TBK_ID>", "id_type": "outline"}` → Kira Sözleşmesi m.299-356; ihtiyaç tahliyesi m.350
3. `mevzuat_getir {"id": "<M350_ID>", "id_type": "madde"}`
4. `ictihat_ara {"phrase": "(\"ihtiyaç sebebiyle tahliye\" OR \"ihtiyaç nedeniyle tahliye\" OR gereksinim) AND samimi AND zorunlu", "court_types": ["YARGITAYKARARI"], "birimAdi": "ALL"}`
   **Kritik**: Türk hukuki üslubu *nedeniyle* / *sebebiyle* / *gereksinim* arasında değişir — hepsini OR'la.
5. `ictihat_getir {"documentId": "<ID>"}`

### Örnek 3: PDF Belgeler (Cumhurbaşkanlığı Genelgeleri)
`CB_GENELGE` PDF'tir, maddeye bölünmez; `mevzuat_icinde_ara` `pdf_full` katmanına yönlenir (tek tam-metin eşleşmesi).
1. `mevzuat_ara {"phrase": "aile", "mevzuat_tur_list": ["CB_GENELGE"]}`
2. `mevzuat_icinde_ara {"mevzuat_id": "<ID>", "query": "aile AND nüfus"}` → `{source: "pdf_full", total_matches: 1}`
3. Gerekirse `mevzuat_getir {"id": "<ID>", "id_type": "mevzuat"}`

### Örnek 4: Mülga Kanun ile Güncel Kanunu İzleme
1. `mevzuat_ara {"mevzuat_no": "1412", "mevzuat_tur_list": ["MULGA"]}`
2. `mevzuat_icinde_ara {"mevzuat_id": "<1412_ID>", "query": "temyiz AND ceza"}`
3. `mevzuat_ara {"mevzuat_no": "5271"}` → `mevzuat_icinde_ara {"query": "(istinaf OR temyiz) AND ceza"}`
   *Eski metinler Osmanlıca yazım kullanabilir (`müruru zaman` iki kelime) — OR alternatifi ekle.*

### Örnek 5: Gerekçe Üzerinden Yasama İradesi
**Her kanunun gerekçesi yoktur.** Getirmeden önce `gerekce_id`'nin boş olmadığını doğrula.
1. `mevzuat_ara {"mevzuat_no": "7512"}` → `gerekce_id` alanını kontrol et
2. `mevzuat_getir {"id": "<GEREKCE_ID>", "id_type": "gerekce"}`
   *Karşı-örnek: KVKK 6698 hiç `gerekce_id` döndürmez — ID uydurma, erişilemez olduğunu bildir.*

### Örnek 6: Bir Değişiklikten Sonra İçtihat Hâlâ Geçerli mi?
1. `ictihat_ara {"phrase": "\"765 sayılı\"", "court_types": ["YARGITAYKARARI"], "kararTarihiStart": "2004-01-01", "kararTarihiEnd": "2004-12-31"}`
2. `mevzuat_ara {"mevzuat_no": "765", "mevzuat_tur_list": ["MULGA"]}`
3. TCK 5237 m.7 (lex mitior) + geçici maddeleri kontrol et.
   *1 Haziran 2005 öncesi suçlar sanık lehineyse hâlâ TCK 765'e tabidir — "geçersiz" ilan etmeden önce doğrula.*

### Örnek 7: Mahkemeler-Arası Karşılaştırma (Yargıtay vs İstinaf)
1. `ictihat_ara {"phrase": "mobbing AND ispat", "court_types": ["YARGITAYKARARI"]}`
2. `ictihat_ara {"phrase": "mobbing AND ispat", "court_types": ["ISTINAFHUKUK"]}` — **açıkça geçmelisin**
3. Her iki kümeden seçilenler için `ictihat_getir` (arama sonuçlarında `markdown_content` YOKTUR).
   *AND yığılması geri çağırımı sıfıra düşürebilir — genişten başla.*

### Örnek 8: İdari İşlemin İptali (Danıştay Zinciri)
Hat: *Kanun* → *Yönetmelik/Tebliğ* → *Danıştay* (iptal davası).
1. `mevzuat_ara {"mevzuat_no": "4733", "mevzuat_tur_list": ["KANUN"]}`
2. `mevzuat_ara {"mevzuat_adi": "tütün mamulleri ve alkollü içkiler", "mevzuat_tur_list": ["YONETMELIK", "KKY"]}`
3. `mevzuat_icinde_ara {"mevzuat_id": "<YON_ID>", "query": "ruhsat AND (satış OR perakende) AND başvuru"}`
4. `ictihat_ara {"phrase": "tütün AND ruhsat AND (iptal OR \"yetki aşımı\" OR \"hukuka aykırılık\")", "court_types": ["DANISTAYKARAR"]}`
5. `ictihat_getir`
   **Yetki uyarısı**: yalnız **ülke çapında** düzenlemeler ilk derecede doğrudan Danıştay'da dava edilir (Danıştay K. m.24); bölgesel/yerel düzenlemenin iptali İdare Mahkemesi'nde başlar — Danıştay isabetinin yokluğu dava olmadığı anlamına gelmez.

### Örnek 9: Snippet Odaklı Triyaj (Kota-Tasarrufu)
1. `ictihat_ara {"phrase": "+\"kamulaştırmasız el atma\" +tazminat", "court_types": ["YARGITAYKARARI"], "include_snippets": true, "page_size": 10}`
2. `snippet` alanlarını oku, terimleri yalnızca geçerken anan sonuçları ele.
3. Yalnız 1–2 kazanan için `ictihat_getir`.
   *Belge kotasını 10 yerine 2 kararda harcadın — üst isabetleri sıralamak önemliyse varsayılan desenin bu olsun.*

### Örnek 10: AYM Bireysel Başvuru
1. `aym_ictihat_ara {"decision_type": "bireysel_basvuru", "query": "mülkiyet hakkı kamulaştırma", "decision_date_start": "2023-01-01", "results_per_page": 10}`
2. `ictihat_getir {"documentId": "anayasa:<guid>"}`
   *Uzun kararlarda `is_paginated: true` ise `current_page == total_pages` olana kadar `page_number` ile gez. Eski-stil referanslar (`/ND/<yil>/<sira>`, `/BB/<yil>/<sira>`) da `documentId` olarak çalışır. Norm denetimi için `decision_type: "norm_denetimi"` + `esas_no`.*

### Örnek 11: Kurum Kararları (özelge · dış-arama · iki-kademeli bülten)
**Doğrudan-API kurumları** (gib·btk·rekabet·uyusmazlik·kik·sayistay·kdk) yapılandırılmış filtre kabul eder; **dış-arama kurumları** (bddk·kvkk·sigorta·reklam) yalnız `keywords`, tek sayfa, ve kelimeler üçüncü-tarafa gider.
1. `kurum_karari_ara {"kurum": "gib", "keywords": "gayrimenkul değer artışı kazancı istisna", "tarih_baslangic": "2023-01-01"}`
2. `kurum_karari_getir {"document_id": "gib:<id>"}`
3. `kurum_karari_ara {"kurum": "kvkk", "keywords": "açık rıza olmadan veri işleme idari para cezası"}` — ⚠️ kişi-tanımlayıcı ayrıntı YAZMA
4. `kurum_karari_ara {"kurum": "reklam", "keywords": "yanıltıcı fiyat indirimi"}` → `reklam:336`
5. `reklam_bulten_icinde_ara {"bulten_no": 336, "keywords": "indirim"}`
   *Aynı desen Sigorta Tahkim için `sigorta_dergi_icinde_ara({"dergi_no": <n>, ...})`.*

## 6. Kavram Araması — YALNIZCA `semantik_ictihat_ara` Araç Listende Varsa

*   **Ne yapar**: doğal-dil sorguyu gömer ve kavramsal olarak en benzer kararları döner — hukuki bir FİKİR için içtihat gerektiğinde ve tam ifade bilinmiyorsa faydalı.
*   **Ne alırsın**: `documentId` + `related_quotes` (alâka sıralı pasajlar) + daire/dosya metadata'sı.
*   ⚠️ **Külliyat yaklaşık bir yıl eskidir ve GÜNCELLENMEZ** — son ~12 ayın kararlarını içermez. Güncel içtihat için ASLA ona güvenme; keşif aracı say ve `ictihat_ara` (canlı indeks) ile çapraz-kontrol et.
*   **Soğuk başlangıç**: ilk sorgu ~20 sn sürebilir.
*   **İş akışı**: semantik sorgu → `related_quotes` terminolojisini topla → o terimlerle `ictihat_ara`'yı yeniden çalıştır.

## Son Öğütler

1. **`mevzuat_icinde_ara` kullanabiliyorken 100 sayfalık bir PDF'i asla okuma**.
2. **Kanun numaralarını asla uydurma**. Emin değilsen `mevzuat_adi` ile ara.
3. **Türk hukuku ağır kodifiyedir**. Yanıt genellikle geniş bir *Kanun* ile özel bir *Tebliğ*'in, bir *Yargıtay* kararıyla yorumlanan kesişimindedir.
4. **Kapsamlı çok-kollu araştırma için paralelleştir**. Soru birden çok kaynak veya mahkeme kapsıyorsa orkestrasyon planı için `agentic_legal_deep_research` çağır.

---

## Ortak Avukat ailesiyle ilişki

Bu kılavuz `oa-ictihat` parçasının **araç katmanıdır**: `oa-ictihat` hangi araştırmanın
yapılacağına karar verir, bu kılavuz o aramanın **hangi lehçeyle** yazılacağını söyler.
`oa-ictihat` tetiklendiğinde buradaki sorgu kitapçığı (Bölüm 3) ve tuzaklar geçerlidir.

Diğer bağlantılar:
- **`oa-kontrol`** atıf denetiminde her künyenin resmî kaynaktan teyidini ister — teyit bu
  araçlarla yapılır; `ictihat_getir` / `mevzuat_getir` çağrılmadan bir künye "doğrulandı"
  sayılmaz.
- **`oa-alan`** bir uyuşmazlığı daireye konumlandırırken Bölüm 4'teki otorite sıralaması
  (İBK bağlayıcı > HGK/CGK > tek Daire) ve `birimAdi` filtresi kullanılır.
- **`oa-sure`** mevzuat süresini teyit ederken `mevzuat_icinde_ara` ile ilgili maddeyi
  yalıtır; Bölüm 3'teki **Resmî Gazete tarihi ≠ yürürlük tarihi** uyarısı burada kritiktir.

**Gizlilik sınırı — `oa-gizlilik` Layer 0 ile birleşir:** Bölüm 2'de işaretlenen dış-arama
kurumları (`bddk`, `kvkk`, `sigorta`, `reklam`) sorgu kelimelerini üçüncü taraf bir arama
servisine (Tavily) gönderir. Bu sorgulara **müvekkil adı, dosya/esas numarası, TCKN veya
herhangi bir kişi-tanımlayıcı ayrıntı yazılmaz.** Aynı disiplin diğer araçlar için de
geçerlidir: arama terimleri **hukuki kavramlardan** oluşmalı, dosya verisinden değil.
Bölüm 3'ün ilk kuralı (sorguyu 2–5 terime damıt) bunu doğal olarak sağlar — uzun sorgu
hem gizlilik hem isabet açısından yanlıştır.

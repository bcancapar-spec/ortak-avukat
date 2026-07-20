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

## Araç envanteri ve rolleri
**İçtihat sunucusu — `Yargı Pro` (tek ve varsayılan içtihat sunucusu).** Geniş arşiv, ek kurum kararları, semantik arama ve yüksek limit/tam metin sağlar; kurulum için **https://yargi.betaspacestudio.com/mcp** adresinden Claude Code connectors bölümünden bağlanır. İçsel dayanıklılık: semantik arama (`search_bedesten_semantic`) güncel kalmadığında canlı `search_bedesten_unified` uç noktasıyla teyit et.

| Araç | Rol | Künye otoritesi? |
|---|---|---|
| **Yargı/Bedesten** (`search_bedesten_unified`, `search_bedesten_semantic`, `get_bedesten_document_markdown`) | İçtihat (Yargıtay, BAM Hukuk, Danıştay, yerel, KYB) — Pro varsayılan | **Evet** |
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

## Kapsam — İstinaf + Yargıtay + Danıştay
Türk hukukundaki uyuşmazlığa dönük içtihadı üç düzeyde ara: **İstinaf (BAM hukuk/ceza, BİM idare/vergi)**, **Yargıtay**, **Danıştay**. İstinaf içtihadı özellikle güncel eğilim ve henüz Yargıtay/Danıştay'a taşınmamış meselelerde değerlidir; üçünü birden tara, ihtisas dairesini `oa-alan` ile hedefle.

## Üç arama dialect'i — operatör kuralları farklı (en sık hata)
- **`search_mevzuat.phrase` (Mevzuat Solr):** `+zorunlu`, `-hariç`, `"tam ifade"`, `kelime*`, `kelime~`. ⚠️ AND/OR/NOT yazıları parser'ı **bozar**; bitişik iki kelime zaten AND.
- **`search_bedesten_unified.phrase` (Bedesten Solr):** AND/OR/NOT **çalışır** (BÜYÜK HARF), `"tam ifade"` çalışır. ⚠️ Wildcard/fuzzy **yok**; en çok iki terimli AND en isabetli.
- **`search_within_mevzuat.query` (tek kanun, yerel boolean):** AND/OR/NOT (BÜYÜK HARF) **gerçekten** çalışır, `( )` gruplama, `"tam ifade"`.
Tüm dialect'lerde Türkçe diakritikleri koru (ç ş ğ ı İ ö ü).

## Sunucu çağrı sırası (varsayılan — kolay akış)
Norm önce, içtihat sonra:
1. **Mevzuat** taraması (Mevzuat MCP / `search_mevzuat`) — norm katmanı.
2. **İçtihat:** **Yargı Pro**'yu çağır — **semantik arama** (`search_bedesten_semantic`) burada açıktır. Semantik korpus güncel değilse **canlı `search_bedesten_unified`** uç noktasıyla teyit et.
- **Semantik ne zaman:** kelime tutmayan, kavramsal/anlam bazlı emsal ararken kullan. **Güncel karar veya tam künye** gerekiyorsa canlı `search_bedesten_unified` kullan — semantik korpus ~1 yıl eski (son ~12 ayın kararı yok).

## Yerleşik kalıplar
- **Bedesten:** `birimAdi` + `court_types` + tırnaklı `phrase`; çoğu iş `search_bedesten_unified` ile. HGK için `birimAdi="HGK"`. Tarih bandı (`kararTarihiStart/End`) ile içtihat değişikliğini izole et. Künyeyi alıp gerekçeyi `get_bedesten_document_markdown` ile çek — snippet yetmez.
- **Mevzuat:** numara → `mevzuat_no` (6100 HMK, 2577 İYUK, 2004 İİK, 6216 AYM, 6098 TBK); `mevzuat_id` → `outline`/`search_within_mevzuat`/`get_mevzuat_document`. Büyük metinler `chunk` ile.
- **Mevzuat — yönetmelik araması:** yönetmelikler **birden çok alt tipe** dağılır (YONETMELIK / CB_YONETMELIK / KKY / UY); tek tiple arayıp "yok" deme. Önce **tipsiz başlık araması**, bulunamazsa alt tipleri sırayla tara. (Çocuk Teslimi Yönetmeliği dosyasında öğrenildi.)
- **Mevzuat — torba/değişiklik kanunu bulma:** `mevzuat_adi` ile jenerik torba başlığı araması **güvenilmezdir** (başlıklar uzun ve standart dışı). Güvenilir kalıp: **tarih-aralıklı kanun araması** (RG tarihi biliniyorsa banda daralt) → listeden numarayla seç. (7579 sayılı Kanun böyle bulundu — RG 22.05.2026, mevzuatId 352551; başlık araması başarısızdı.)
- **AYM:** `search_anayasa_unified` + `get_anayasa_document_unified`; bireysel başvuruda yalnızca AYM-teyitli kararlar.

## Bilinen sınırlar — baştan hazırlıklı gir
- **Bedesten gerçek phrase-search yapmaz:** uzun/çok terimli ifadede kelime bazında eşleştirir, şişkin sayı döndürür (TBK m.71'de 1.082.645 "kayıt"). Kısa 1-2 ayırt edici terim + daire/tarih filtresi kullan.
- **4. HD kısa ONAMA kararları uzun gerekçeyle indekslenmemiş;** bazı doktrinler beklenmedik rotadan gelir (TBK m.71 → TMK m.1007 / KTK m.85).
- **BAM Ceza Daireleri Bedesten indeksinde yok.**
- **Danıştay tam metni bazen `null` döner:** PDF kaynaklı, OCR'ı henüz tamamlanmamış kararlar metinsiz gelebilir. Bu "karar yok" demek değildir — künye geçerlidir; metni kanonik kaynaktan (UYAP / Kazancı-Lexpera / kararlar.danistay) ayrıca çek ve çalışmada durumu bildir.
- **Semantik arama** (`search_bedesten_semantic`, Yargı Pro — API key ile açık): kavramsal emsal için güçlü, ama **korpus ~1 yıl eski (son ~12 ay yok)**, **`birimAdi` (daire) filtresi YOK** ve iki aşamalı boru hattında timeout verebilir. Daire-hedefli arama gerekiyorsa canlı `search_bedesten_unified` (`birimAdi` + `court_types` + tırnaklı `phrase`) kullan; güncel için de canlı unified; HGK için `birimAdi="HGK"`.
- **Rate limit:** çağrıları `sleep` ile arala.
- **OCR şüphesi — çalışmada BİLDİR:** Karar/mevzuat metni (`get_bedesten_document_markdown`, mevzuat PDF/OCR) dönüşümden gelir; bozuk karakter, kopuk kelime, anlamsız sayı/harf dizisi olabilir. Aynen alıntı taşıyacak bir pasajda OCR kusuru sezilirse **sessizce düzeltme veya taşıma** — çalışmada açıkça "OCR şüphesi" diye işaretle ve kanonik kaynakla (Resmî Gazete / UYAP / Kazancı-Lexpera) bir kez teyit et. OCR hatasını dilekçeye taşımak, hatalı "birebir" alıntı demektir.

## Fallback zincirleri (gerçek kullanımdan)
- **İçtihat sunucusu:** **Yargı Pro** (semantik açık); güncel karar için **canlı `search_bedesten_unified`** ile teyit. Norm taraması (Mevzuat) bundan önce gelir.
- **Mevzuat MCP timeout →** `mevzuat.gov.tr` `web_fetch` (PDF: `web_fetch_pdf_extract_text=True`); birden çok kaynaktan teyit. (5510 m.21/4'te kullanıldı.)
- **Literatür MCP timeout →** kısa bekle + retry; ısrarlıysa web_search ile DergiPark, künyeyi ayrı doğrula.
- **Bedesten şişmesi →** terimi kısalt + daire/tarih; gerekirse Lexpera/Kazancı/UYAP Emsal (Can'ın erişimi).
- **Genel:** resmî kaynağa erişilemiyorsa **açıkça raporla**, sessizce hafızadan doldurma. Sağlık: `check_government_servers_health`.

## Araç keşfi ve sahte-teyit yasağı (kritik)
Bu dosyadaki araç adları kurulumdan kuruluma DEĞİŞEBİLİR (ör. aynı işlevin Türkçe adlı araçları: `ictihat_ara`, `semantik_ictihat_ara`, `mevzuat_ara`, `mevzuat_getir`). Sorgudan önce oturumda MEVCUT araç listesine bak ve gerçekte var olan aracı kullan; adı tutmuyor diye işlevi atlamak da, var olmayan bir araca çağrı yapılmış gibi sonuç yazmak da yasaktır. **"Teyitli" etiketi yalnızca fiilen yapılmış bir çağrıya konur** ve üçlü kayıtla yazılır: araç + sorgu + dönen künye/metin. Araç gerçekten yoksa veya erişilemiyorsa: fallback zinciri + açık beyan ("şu araç kapalı; bu künye teyit edilemedi").

## Ham MCP dökümü diske yazılır — kunye_teyit'in ikinci kaynağı (kritik)
`oa-kontrol/scripts/kunye_teyit.py` teyit edici kaynak evrenini SADECE ikisinden okur: `_oa/teyit/kunye-teyit.md` kütüğü + `_oa/teyit/dokum/` ham MCP dökümleri. `_oa/cikti/` (taslak/antitez/kıyas gibi model çıktıları) teyit kaynağı DEĞİLDİR — oraya yazılan bir izi kunye_teyit "teyitli" saymaz, yalnız [BİLGİ] şerhi verir. Bu ikinci kaynağı (döküm dizini) besleyen adım BURADADIR — atlanırsa teyit evreninin yarısı kalıcı boş kalır ve kunye_teyit sistematik olarak yanlış-pozitif TEYİTSİZ üretir. Bu yüzden **her MCP araştırma sonucunda**:
1. Dönen ham çıktıyı (künye/metin/snippet) **`_oa/teyit/dokum/<tarih>-<arac>-<slug>.md`** olarak diske yaz (ör. `2026-07-19-search_bedesten_unified-tbk-m49.md`); dizin yoksa oluştur.
2. Kütük satırını o dosyaya bağla: `python oa-pipeline/scripts/oa_hafiza.py teyit --arac <arac> --sorgu "<sorgu>" --sonuc "<künye/özet>" --dokum _oa/teyit/dokum/<dosya>`.
3. Yalnızca kütüğe satır yazıp dökümü atlamak da olur (kütük tek başına yeterli teyit kaynağıdır), ama uzun/parçalı metinlerde (gerekçe, madde tam metni) ham dökümü de diske yazmak ileride merci/daire ayrıştırmasını ve içerik çaprazını güçlendirir — özellikle şüpheli/OCR'lı veya çok terimli künyelerde döküm atlanmaz.

## Karar çekme (CEK) — ictihat_getir → ham md → muhakeme girdisi
İçtihat Muhakeme Zinciri'nde bu parçanın rolü **yalnızca CEK**tir; MUHAKEME
(illiyet + LEHE/ALEYHE/ALEYHE-AYIRT/NOTR damgası) `oa-kiyas`/`oa-kontrol`'e
aittir — bu iki adım **karıştırılmaz**. CEK adımı:
1. Künyeyi bul ve teyit et (yukarıdaki akış).
2. Kararın **tam metnini** `ictihat_getir`/`get_bedesten_document_markdown`
   (veya kurulumdaki eşdeğer araç) ile çek — snippet yetmez.
3. Ham metni "Ham MCP dökümü diske yazılır" bölümündeki kuralla
   `_oa/teyit/dokum/<tarih>-<arac>-<slug>.md` yoluna yaz.
4. Bu dosya adını `oa-kiyas`/`oa-kontrol`'e **KAYNAK-IZI** olarak devret —
   MUHAKEME adımı bu izi kullanarak `_oa/cikti/NN-ictihat-muhakeme.md`
   kaydını üretir (alan şeması: `oa-kiyas/references/ictihat-muhakeme-sablonu.md`).
Bir karar **çekilmiş olması** onun **muhakeme edilmiş** sayılması için
yeterli değildir — damga atanmadan (NOTR = "muhakeme edilmemiş",
fail-closed) hiçbir içtihat dilekçeye giremez.

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
Tam günlük `references/degisiklik-gunlugu.md`'dedir (bağlam ekonomisi için ayrıldı — içerik aynen korunur; yeni kayıtlar oraya işlenir). Güncel sürüm: **v3.22**.

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

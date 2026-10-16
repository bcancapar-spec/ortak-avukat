# Ajan raporu — hukuki yöntem geliştirme adayları (salt okunur inceleme, 2026-10-17)

> **Niteliği ve sınırı (orkestra notu).** Avukatın "sistemi en iyi avukatlık muhakemesine eriştir" talimatı üzerine tek bir
> inceleme ajanı (Fable 5.1) anayasayı, çekirdek ve 15 parça SKILL metnini ve 27 referans dosyasını okudu; hiçbir dosya
> değiştirilmedi, script koşulmadı, ağ kullanılmadı. Rapor DEĞİŞİKLİK DEĞİL, avukatın karar vereceği aday listesidir: her
> kalem "Karar: avukat / mühendislik" ve "Teyit: gerekir / gerekmez" etiketi taşır. Rapordaki madde numaraları hafızadan
> anılmıştır ve resmî kaynaktan TEYİT EDİLMEMİŞTİR (anayasa m.4, m.5) — hiçbiri teyitsiz ürüne, playbook'a ya da kurala
> girmez; §"Sınırlar" hangi hükümlerin repoda teyit kaydı taşımadığını sayar. Heyet üçüncü koşumunun kapsamı dışındadır
> (koşum `c94e982`'nin kod ve kayıt denetimidir); KARAR-3 §7.1'de avukata soru olarak sunulur. Ajan paylaşılan ağaçta
> orkestranın tur-4 değişikliklerini (`d6e5550`) izlenmemiş hâlde gördü; raporda o dosyalara satır atfı yoktur. Depo
> taramasından çıkan bir isabet (grep) hukuki dayanak değildir; "Teyit: gerekir" taşıyan hiçbir kalem resmî kaynaktan
> okunmadan ürüne, playbook'a ya da kurala girmez (heyet doğrulaması 2026-10-17, ESAS NOT-4).


Kapsam: dal `denetim/fable-2026-10-15`, HEAD `c94e982`. Yollar `plugins/ortak-avukat/skills/` köküne göredir; kök dosyalar ayrıca yazılır.
Hiçbir depo dosyası değiştirilmedi; git yazma komutu, ağ ve test yok. Bu rapor değişiklik değil, avukatın karar vereceği aday listesidir.
Madde numaraları bu raporda yalnız iz sürmek içindir: hiçbiri resmî kaynaktan teyit edilmeden metne girmez (m.4, m.5). "Ölçüm" = repoda grep/okuma sonucu. "tahmin:" = ölçülmemiş etki.
Okunan: ANAYASA.md + çekirdek SKILL.md + 15 parça SKILL.md; 27 references dosyası (19 tam, 8 kısmi); 5 script/JSON yalnız başlık/şema düzeyinde.
Ölçüt: (a) muhakeme derinliği · (b) kör nokta · (c) tutarlılık · (d) karar materyali. Tür: metin / playbook / script / test.

## Genel tablo

- Güçlü taraf: süre başlangıç kapısı ve e-tebligat iki senaryosu, kola göre adli tatil, icra dilekçe ailesi, ispat ontolojisi, DAMGA zinciri, strateji karar materyali (nitel bant + maliyet cetveli + müvekkil kararı kapısı).
- Desen 1: yöntem "karşı taraf ne der" sorusunda çok güçlü. "Bizim zamanında kayda geçirmemiz gereken" tarafta zayıf: def'i, karşı dava, ihbar, karşı delil, katılma yoluyla istinaf.
- Desen 2: köprüler tek parçada kalıyor. Ceza–hukuk köprüsü yalnız müşteki vekilinde; praeoccupatio istisnası yalnız usul ve dilekçede.
- Desen 3: çapa var, motor kuralı yok. Çizelgedeki bazı telafisiz süreler `sure_kurallari.json`'da yok.

## Parça karnesi (kısa)

| Parça | Güçlü yan | Ana kör nokta (aday) |
|---|---|---|
| ortak-avukat | iç/dış ayrımı, usul önceliği, doğrulama | yönlendirme tablosu, "çift-model" iddiası (B3, B15) |
| oa-antitez | 9 cephe, hâkim lensi, celse kartı, akıbet dersi | istisnasız preemptive yasağı (A2); cephe çift sayımı (B8) |
| oa-kiyas | ispat yükü carve-out fail-closed, yarışan normlar | usul sütunu yok (B9); TBK m.72 çapası eksik (A4) |
| oa-strateji | koruma tedbiri §0, masraf/risk kapısı, zaman ekseni | kanun yolu protokolü yok (A7); geri dönüşsüzlük (B7) |
| oa-dilekce | netice-i talep, terdit ayrımı, yedi kural, icra ailesi | cevapta def'i/karşı dava (A1); istinafta sınırlı inceleme (A7) |
| oa-usul | asimetrik protokol, tamamlanabilir kusur, kamu gücü | ihbar (A8), bekletici mesele (B11), iflas (B10) |
| oa-sure | başlangıç kapısı, aşama tetikli süreler | eksik kurallar (A3); kesilme/durma elle (B13) |
| oa-vakia | tanık şartlı delil, karine yük kaydırır, tedarik planı | karşı delil (A6); akıbet elle (A9) |
| oa-illiyet | iki kenar tipi, dal önekli kesme, kanun yolu zinciri | rücu → ihbar köprüsü yok (A8); ondalık "güven" (B6) |
| oa-ictihat | içtihat haritası, iniş ritüeli, aşılmışlık sorusu | yukarı yön akıbet (A9); bağlayıcı aleyhe (A5); bayat kanal (B2) |
| oa-kontrol | tek ölçüt makbuz, bağımsız hakem, hâkim lensi | ifşa kontrolünde kayıt koruma sorusu yok (A2) |
| oa-interview | belgeli/beyan statüsü, çatışma taraması | paralel dosya (A4), karşı taraf malvarlığı (B14) |
| oa-alan | forum seçimi, yasak bölgeler, unsur şablonları | şablonda süre niteliği karışık (A10) |
| oa-mudafii | en avantajlı sonuç haritası, susma protokolü | dava zamanaşımı kesilme protokolü yok (B13) |
| oa-musteki-vekili | "ceza yolu ne için" beş eksen, katılma anı | köprü yalnız bu parçada (A4) |
| oa-pipeline | kavşak, müvekkil kararı, avukat şerhi ayrımı | "MCP aktifliği" bayat (B2); ALIM'da paralel dosya yok (A4) |

## A listesi — en çok müvekkil koruyan 10 aday

**A1. Davalı cevap penceresi: def'i ve karşı dava nöbeti yok** — oa-dilekce, oa-sure
- Yer: `oa-dilekce/SKILL.md:288`; `oa-sure/SKILL.md:134-140`; `ANAYASA.md:204-205`; `oa-alan/references/unsur-sablonlari/kidem-ihbar.md:17`.
- Gözlem: Cevap playbook'u: "Sık atlanan: ilk itirazların süresinde sürülmesi; inkâr edilmeyen vakıanın ikrar sayılması." Zamanaşımı/takas def'i ve karşı dava yok. Aşama tablosu yalnız ilk itiraz, delil, ön inceleme, ıslah, katılma taşır. Anayasa gerekçesi bu kaybı "ör. zamanaşımı def'i" diye örnekler; işletimdeki tek karşılık bir unsur şablonu. Ölçüm: HMK m.132/m.133 için 0 eşleşme.
- Neden: hâkimin kendiliğinden gözetmediği def'i süresinde sürülmezse davalı müvekkil kazanılabilir davayı kaybeder. tahmin: karşı dava kaçarsa ayrı dava, harç ve süre maliyeti.
- Öneri: playbook — cevap tipine "def'i / karşı talep" satırı. script — oa-sure aşama kuralları: zamanaşımı def'i, karşı dava, iddia/savunma genişletme penceresi. script — `dilekce_denetim.py` cevap+davalı için advisory def'i taraması. test — kilit.
- Karar: avukat (def'i kataloğu, pencere) + mühendislik (kural, kapı).
- Teyit: gerekir — TBK m.161; HMK m.132-133, m.141; def'inin ıslahla ileri sürülmesi içtihadı (`oa-usul/references/usul-cetveli.md:42` "tartışmalı" diyor).

**A2. Sunulmamış antitez yasağı ile kayıt koruma arasında köprü yok** — oa-antitez, oa-kontrol, oa-dilekce, oa-usul
- Yer: `oa-antitez/SKILL.md:25,52`; `oa-kontrol/SKILL.md:117`; `oa-dilekce/SKILL.md:334,410`; `oa-usul/SKILL.md:98-99`; `oa-musteki-vekili/SKILL.md:204`.
- Gözlem: Antitez istisnasız: "Sunulmamış antiteze karşı savunma geliştirme." Kontrol B: "Veriyorsa çıkar." Usul ise "İSTİSNA (tek)" olarak avukat onaylı praeoccupatio ve "kurucu unsur" sınırını, müşteki akışı "ama ispat boşluğunu önden kapat" ilkesini tanır. Ölçüm: HMK m.355/m.357 için 0; m.141 yalnız bilirkişi itirazında (`oa-dilekce/SKILL.md:525`).
- Neden: model "cephanelik" gerekçesiyle çürütmede gerekecek vakıayı ve delili de dilekçeden çıkarabilir. Dilekçeler aşaması kapanınca genişletme yasağı, süresinden sonra delil yasağı, istinafta yeni vakıa/delil engeli işler. tahmin: en sık dava ve cevap dilekçesinde.
- Öneri: metin — anayasa m.6'ya ya da antitez gövdesine tek "sınırlar" paragrafı: argüman saklanır, vakıa ve delil kaydı saklanmaz; praeoccupatio avukat onayıyla. playbook — kontrol B'ye "kayıt koruma" sorusu. script — antitez cephesine `kayit_gerekli: vakia|delil|yok` alanı + [G] advisory.
- Karar: avukat (anayasal ilke metni).
- Teyit: gerekir — HMK m.141, m.145, m.357 güncel metni.

**A3. Çapası olup motor kuralı olmayan telafisiz süreler** — oa-sure, oa-strateji, oa-antitez, oa-usul
- Yer: `oa-sure/references/sure-cizelgesi.md:24,28,445`; `oa-sure/scripts/sure_kurallari.json`; `oa-strateji/SKILL.md:45-57`; `oa-antitez/SKILL.md:47`; `oa-usul/SKILL.md:69-70,113`; `oa-dilekce/references/icra-dilekce-ailesi.md:259,297-300`.
- Gözlem: Çizelge istinafa cevap ve eski hâle getirme sürelerini çıpalar. Strateji ihtiyati haciz sonrası yedi günü yazar ama "kural eklenmesi oa-sure (I5) alanıdır, burada eklenmez" der. Ölçüm: JSON ve gömülü tabloda HMK m.96, m.281, m.347-348; İİK m.264, m.97/6, m.128/a; CMK m.41 için kural kimliği 0.
- Neden: kuralsız hesapta izinli başlangıç türü denetlenemez; manşet uzamasız erken tarihe düşer (`oa-sure/SKILL.md:33`). Kaçarsa ihtiyati haciz kendiliğinden kalkar, rapor tartışmasızlaşır, eski hâle kapısı kapanır. tahmin: kendi süremizde risk düşük, karşı tarafa kesin dil kurarken yüksek.
- Öneri: script — sekiz kural (başlangıç türü, adli tatil rejimi, teyit tarihi). test — ikiz kilit.
- Karar: mühendislik; adli tatil rejimi için avukat teyidi.
- Teyit: gerekir — her maddenin resmî metni ve tatil rejimi.

**A4. Ceza–hukuk köprüsü yalnız müşteki parçasında; hukuk dosyasında uzamış zamanaşımı görünmüyor** — oa-sure, oa-kiyas, oa-interview, oa-pipeline
- Yer: `oa-musteki-vekili/SKILL.md:44-46`; `oa-sure/references/sure-cizelgesi.md:347`; `oa-kiyas/references/kiyas-rehberi.md:111,118`; `oa-interview/references/soru-bankasi.md:7-17`.
- Gözlem: TBK m.72/1'in "daha uzun ceza zamanaşımı" kaydı yalnız müşteki §0(c)'de. Süre çizelgesi "m.72 (haksız fiil — 2/10 yıl)" der; kıyas örneği norm seçimini "daha uzun zamanaşımı"na dayandırır. Alım çekirdeğinde bağlantılı ceza/icra/idari dosya sorusu yok.
- Neden: suç da oluşturan haksız fiilde model "zamanaşımı doldu" deyip geçerli talebi terk ettirebilir. Yarışan norm seçimi ters dönebilir. tahmin: bekletici mesele, ceza hükmünün bağlayıcılığı ve derdestlik sinyalleri de kaçar.
- Öneri: playbook — iki çapaya kayıt + `oa-sure --tur maddi` için "suç teşkili varsa iki senaryo" uyarısı. playbook — soru bankası çekirdeğine "paralel/bağlantılı dosyalar". metin — pipeline ALIM'da §0 tablosu hukuk dosyasında da çağrılır.
- Karar: avukat.
- Teyit: gerekir — TBK m.72/1, m.74; TCK m.66; HMK m.165 (müşteki §0'da teyit kaydı var; kullanım anında yeniden).

**A5. Bağlayıcı aleyhe içtihat için ayırt etme yolu kapıda kapalı; şablon ile kapı çelişiyor** — oa-kiyas, oa-dilekce, oa-antitez, oa-ictihat
- Yer: `oa-kiyas/references/ictihat-muhakeme-sablonu.md:81-83`; `oa-dilekce/SKILL.md:465-467`; `oa-antitez/SKILL.md:52`; `oa-ictihat/SKILL.md:51,211-213`.
- Gözlem: Şablon ALEYHE-AYIRT için "karşı tarafın ileri sürmesi beklenen/sürdüğü bağlayıcı otorite" der. [G6] yalnız `DUYULMUS=EVET` ile geçirir; antitez "yalnız ... DUYULMUŞ" der. oa-ictihat bağlayıcı aleyhe içtihatta stratejiyi kurmayı söyler, dilekçe yolunu tanımlamaz.
- Neden: hâkim bağlayıcı içtihadı kendiliğinden uygular. Karşı taraf anmadı diye ayırt edilmezse hüküm o içtihatla, bizim farkımız hiç yazılmadan kurulur. tahmin: "silahlandırma" gerekçesi otorite zaten mahkemedeyken işlemez.
- Öneri: script — kütüğe `BAGLAYICI=EVET`; [G6]'ya "duyulmuş VEYA bağlayıcı + avukat onayı" istisnası. metin — şablon cümlesi kapıyla hizalanır. test.
- Karar: avukat (m.6 yorumu) + mühendislik.
- Teyit: gerekir — 2797 s.K. m.45 (oa-ictihat'ta teyit kaydı var); AY m.153.

**A6. Karşı delil: "yük karşıdaysa planlanmaz" kuralı süre engeline açık** — oa-vakia, oa-kiyas
- Yer: `oa-vakia/SKILL.md:112-117`; `oa-kiyas/SKILL.md:105,117-118`; `oa-sure/references/sure-cizelgesi.md:37-40`.
- Gözlem: Delil planı "İspat yükü karşı taraftaysa tedarik planlanmaz" der. Kıyastaki `curutme_hazirligi` dahilidir, "dilekçeye kopyalanmaz". Çizelge sonradan delil yasağını ve istisnaya "güvenme"yi yazar.
- Neden: karşı taraf yükünü karşılarsa çürütme delilimiz dilekçeler aşamasında gösterilmediği için sonradan getirilemeyebilir. tahmin: "yük karşıdaydı" avantajı tam bu anda kaybolur.
- Öneri: script — `delil_plani.py`ye `karsi_delil` satır tipi. playbook — `curutme_hazirligi`ndaki delil kalemleri (argüman değil) delil listesine akar. test.
- Karar: avukat.
- Teyit: gerekir — HMK m.140/5, m.145; karşı delil uygulaması.

**A7. Kanun yolu karar protokolü yok (strateji açıklaması vaat ediyor)** — oa-strateji, oa-dilekce, oa-sure
- Yer: `oa-strateji/SKILL.md:5,94,162-172`; `oa-dilekce/SKILL.md:225-241,290,292`; `oa-sure/references/sure-cizelgesi.md:15`; `oa-sure/SKILL.md:34`; `oa-dilekce/references/kanun-yolu-mimari-playbook.md:136`.
- Gözlem: Açıklama "hangi kanun yolu, hangi sıra" der; seçenek yelpazesi "dava / sulh-müzakere / icra takibi / idari başvuru / tedbir-durdurma / bekle". Ölçüm: HMK m.355, m.357 için 0; m.348 yalnız "katılma/cevap süreleri (m.347-348)". Kesinlik yalnız uyarı; eşik maddeleri anılmaz. Kısmi dava kalıbı kesinlik etkisini anmaz. Sebep sırası sonuç türünü (kaldırma-geri gönderme / esastan karar) tartmaz.
- Neden: başvurmak karşı tarafa katılma yolunu açabilir. Sınırlı inceleme ve yeni vakıa/delil engeli istinaf dilekçesini tek atış yapar. tahmin: düşük "şimdilik" değer kararı kesin kılabilir; usul sebebi hız hedefli müvekkilde dosyayı başa döndürür.
- Öneri: playbook — strateji'ye "KANUN YOLU KARARI" bölümü: başvur / başvurma / karşı başvuruyu bekle; kesinlik, katılma riski, sonuç türü, maliyet, süre sütunları. playbook — istinaf tipine sınırlı inceleme ve yeni vakıa/delil satırı; kısmi dava kalıbına kesinlik notu.
- Karar: avukat.
- Teyit: gerekir — HMK m.341, m.347, m.348, m.353, m.355, m.357, m.362 ve yeniden değerleme hükmü.

**A8. Davanın ihbarı ve fer'i müdahale hiç yok; illiyet grafı rücu sinyalini usule bağlamıyor** — oa-usul, oa-dilekce, oa-illiyet
- Yer: `oa-illiyet/references/illiyet-doktrini.md:36-37`; `oa-illiyet/SKILL.md:72-77`; `oa-dilekce/SKILL.md:288`.
- Gözlem: Ölçüm: "davanın ihbar", "ihbar olunan", "fer'i müdahale" için 0; HMK m.61 hiçbir playbook'ta yok. Doktrin "iç ilişkide rücu (TBK m.61-62)" ve `medeni:ucuncu_kisi_kusuru` bayrağını taşır; usul aracına köprü yok.
- Neden: davalı müvekkil rücu edebileceği kişiye (alt işveren, sigortacı, kefil, üretici) davayı ihbar etmezse rücu davasında aynı tartışma sıfırdan açılır. tahmin: ihbarın bağlayıcılık etkisi kaybedilir (etkisi teyit gerekir).
- Öneri: script — `grafik_denetim.py` advisory "ihbar adayı" (müvekkil davalı + rücu/kefalet/asıl-alt işveren/sigorta kenarı). playbook — cevap tipine ihbar ve fer'i müdahale satırı; oa-sure aşama kuralı.
- Karar: avukat (taktik) + mühendislik (sinyal).
- Teyit: gerekir — HMK m.61 vd., m.66 vd.; ihbarın etkisine ilişkin içtihat.

**A9. Lehe dayanağın akıbeti (yukarı yön) mekanik değil** — oa-ictihat, oa-vakia, oa-kontrol
- Yer: `oa-vakia/SKILL.md:138`; `oa-kontrol/SKILL.md:120`; `oa-ictihat/SKILL.md:60-65,221-257`; `oa-kiyas/references/ictihat-muhakeme-sablonu.md:198-201`; `oa-antitez/SKILL.md:87`.
- Gözlem: Saha dersi: "lehe gösterilen bir kararın üst mahkemece kaldırıldığı yazılmamıştı." Mekanik bayrak "v0.5.19 adayı"; tarama elle. Zorunlu son soru aşılmışlığı sorar; iniş ritüeli aşağı yönlü. Atfedilen BAM/ilk derece kararının kendi kanun yolu sonucu için alan yok; "Otomatik aşan-kaynak taraması v2'ye ertelendi."
- Neden: kaldırılmış ya da bozulmuş karara dayanan dilekçe tek karşı atıfla çöker; güven kaybı bütün metne yayılır.
- Öneri: playbook+script — muhakeme kaydına `AKIBET` alanı (kesin / onandı / bozuldu-kaldırıldı / bilinmiyor); LEHE BAM/ilk derece atfında boşsa [G6] uyarısı; "çıkış ritüeli" metni. test.
- Karar: mühendislik + avukat (uyarı mı kapı mı).
- Teyit: yöntem için gerekmez; somut aramada resmî portal.

**A10. Unsur şablonlarında süre niteliği karışık; A-15 onarımı yayılmamış** — oa-alan
- Yer: `oa-alan/references/unsur-sablonlari/kidem-ihbar.md:20-27`; `.../ise-iade.md:17`; `.../itirazin-iptali.md:24`; `.../tasarrufun-iptali.md:16`; `oa-vakia/SKILL.md:37-46`.
- Gözlem: Kıdem-ihbar notu ayrımın "aynı yapıştırma dizgiyle yazılmıştı" ve şablon başına yeniden yazılacağını söyler. İşe iade U6 ve itirazın iptali U4 hâlâ "Mahkemece resen + davalı def'i". Tasarrufun iptali U6 doğru ayrımı yapar.
- Neden: re'sen gözetilen sürede "def'i" ibaresi davacı tarafta "ileri sürülmezse sorun yok" yanılgısı doğurabilir. tahmin: unsur U-id olarak vakıa matrisine ve DURUM.md'ye bu nitelemeyle taşınır.
- Öneri: playbook — iki hücre teyitten sonra yeniden yazılır. test — şablonda "resen + def'i" birlikteliği yasak.
- Karar: avukat (niteleme).
- Teyit: gerekir — İş K. m.20/1 ve İİK m.67/1 sürelerinin niteliği (içtihat).

## B listesi

| # | Yer | Gözlem | Neden | Öneri (tür) | Karar | Teyit |
|---|---|---|---|---|---|---|
| B1 | `oa-antitez/SKILL.md:47`; `oa-dilekce/SKILL.md:517-535` | Bilirkişi itirazı iki ayrı listede: antitez beş soru, dilekçe dört eksen; birbirini anmıyor | itirazda bir eksen düşer | tek liste + `bilirkisi-itiraz` tipi (playbook+script) | mühendislik+avukat | antitezde teyit kaydı var |
| B2 | `oa-ictihat/SKILL.md:33,35,43,142`; `oa-pipeline/SKILL.md:30`; `ortak-avukat/SKILL.md:79,82`; `oa-alan/SKILL.md:33` | Hibrit kanal kararından kalan ifadeler: "Pro varsayılan", eski `search_*` adları (aynı dosyada :82 `kurum_karari_ara`), "MCP AKTİFLİĞİ ZORUNLUDUR"; Danıştay 8. D teyidi AYM bilgi bankasına eşlenmiş | model kanal varken durabilir ya da yanlış portalda arar | metin | mühendislik | gerekmez |
| B3 | `ortak-avukat/SKILL.md:24`; `oa-pipeline/SKILL.md:277`; `plugins/ortak-avukat/.claude-plugin/plugin.json` | "çift-model antitez kontrolü" ve Gemini'ye giden metin anılıyor; eklenti sunucu ilan etmiyor | mekanizmasız süreç iddiası | "varsa" kaydı ya da kaldırma (metin) | avukat | gerekmez |
| B4 | `oa-antitez:70`, `oa-dilekce:316,318`, `oa-interview:72`, `oa-pipeline:313`, `oa-strateji:207,263`, `oa-vakia:98` (+4 reference başlığı); `oa-vakia:138`, `oa-usul:161` | "(v0.5.18 aday)" etiketleri; CHANGELOG'da v0.5.18 ve v0.6.0 yayımlanmış; "v0.5.19 adayı" 0.6.0 sonrası bayat | tahmin: model yürürlükteki kuralı "aday" sayar | metin | mühendislik | gerekmez |
| B5 | `oa-kiyas/references/ictihat-muhakeme-sablonu.md:118,141,194,220,246,249,255`; `oa-dilekce/SKILL.md:79-80`; `oa-ictihat/SKILL.md:156` | Örneklerde gerçek görünümlü tam künyeler; gerçek mi kurgu mu metinden anlaşılmıyor | tahmin: teslim zinciri dışındaki çıktıda künye tohumu | maske ya da "BİÇİM ÖRNEĞİ — ATIF DEĞİL" damgası (metin+test) | mühendislik | gerekmez |
| B6 | `oa-antitez/scripts/antitez_matris.py:210`; `oa-illiyet/references/illiyet-doktrini.md:157`; `oa-strateji/SKILL.md:20,100`; `oa-kiyas/SKILL.md:36`; `oa-illiyet/scripts/grafik_denetim.py:1390` | Üç ayrı güç sözlüğü; kıyas "olasılık" serbest metin; "beklenen kazanım × olasılık bandı"; zincir "güven" ondalıkla basılıyor | karar materyalinde ölçek karışır; ondalık olasılık sanılabilir | eşleme tablosu + "sıralama puanı, olasılık değil" etiketi (metin+script) | avukat+mühendislik | gerekmez |
| B7 | `oa-mudafii/SKILL.md:95-97`; `oa-strateji/SKILL.md:94-117` | Ceza haritası "geri dönüşsüz mü" sorar; hukuk strateji tablosunda feragat/kabul/sulh geri dönüşsüzlüğü, "bekle"nin süre bedeli, erken bitişin harç-vekâlet etkisi yok | müvekkil geri dönüşsüz seçimi bedelini görmeden yapar | iki sütun (playbook) + cetvelde erken bitiş satırı (script) | avukat | gerekir: HMK m.311, m.315; 492 s.K.; AAÜT |
| B8 | `oa-antitez/scripts/antitez_matris.py:185,190` | "usul" ve "zamanasimi" cepheleri hak düşürücüyü birlikte taşıyor; tahsil edilebilirlik ve kanun yolu/kesinlik cephesi yok | aynı risk iki satırda, iki risk hiç | tekilleştir + 10. cephe adayı (script+test; [G] kilitleri etkilenir) | avukat | gerekmez |
| B9 | `oa-kiyas/SKILL.md:131-132`; `oa-kiyas/references/kiyas-rehberi.md:94-96`; `oa-alan/SKILL.md:46` | Yarışan norm kıyası dört ölçütle; usul sonucu (yetki maddesi, dava şartı arabuluculuk, senetle ispat) ve yedek normun vakıalarının dilekçede bildirilmesi denetlenmiyor | tahmin: seçilen norm usulde düşer ya da yedek norm vakıasız kalır | `usul_sonucu`, `vakia_bildirildi` alanları (şema+playbook) | avukat | gerekir: HMK m.10, m.16, m.33, m.111 |
| B10 | `oa-dilekce/references/icra-dilekce-ailesi.md:414-417`; `oa-sure/SKILL.md:100` | İflas yolu "bu turda yapılmadı"; konkordato yalnız adli tatil istisnasında; derdest dava ve takiplere etkisi hiçbir yerde yok | tahmin: dava/takip yanlış merci ve sürede yürür | usul cetveline "iflas/konkordato etkisi" satırı (playbook) | avukat | gerekir: İİK iflas ve konkordato hükümleri (madde no teyit edilecek) |
| B11 | `oa-musteki-vekili/SKILL.md:44`; `oa-usul/references/usul-cetveli.md` | Bekletici mesele ve bağlı sorun süresi yalnız ceza parçalarında; usul cetvelinde ve oa-sure'de yok | süresinde başvurulmazsa iddiadan vazgeçilmiş sayılma riski (müşteki §0 okuması) | cetvel satırı + oa-sure kuralı | avukat+mühendislik | gerekir: HMK m.165 |
| B12 | `oa-dilekce/references/idari-ceza-tipleri.md:44-45,136-137` | Ceza temyizi için ayrı tip yok; `temyiz` tipi HMK m.364/2 unsurlarını arıyor | ceza temyizinde yanlış unsur seti | `ceza-temyiz` tipi (script+test) | mühendislik | gerekir: CMK m.291-295 |
| B13 | `oa-sure/SKILL.md:146`; `oa-mudafii/SKILL.md:204`; `oa-musteki-vekili/SKILL.md:141-143` | Zamanaşımının kesilmesi/durması "elle değerlendir"; ceza dava zamanaşımı "taranır" ama protokol yok | tahmin: kesen işlem atlanır, sonuç ters çıkar | kesen/durduran olay listesi + maddi hesapta "kesilme tarihi" girdisi (playbook+script) | avukat+mühendislik | gerekir: TBK m.153-158; TCK m.66-67 |
| B14 | `oa-strateji/SKILL.md:23-27,109`; `oa-interview/references/soru-bankasi.md:7-17` | Strateji §0 ve §5 karşı tarafın malvarlığını girdi sayar; alım çekirdeği yalnız müvekkilin masraf gücünü sorar | tedbir kararı girdisiz verilir | çekirdeğe bir soru (playbook) | avukat | gerekmez |
| B15 | `ortak-avukat/SKILL.md:106-125` | Çekirdek yönlendirme tablosunda oa-ingest yok | tahmin: tekil işte ingest atlanır | tablo satırı (metin) | mühendislik | gerekmez |
| B16 | `oa-vakia/SKILL.md:74-91`; `oa-illiyet/references/cikti-blogu.md:78`; `oa-ictihat/SKILL.md:291` | Örneklerde gerçek kişi adı görünümlü ad çiftleri; diyagram örneğinde kişi adı; bir doktrin yazarının adı | m.7 uyum tartışması | "kurgusal" etiketi ya da harf kalıbı (metin) | avukat | gerekmez |
| B17 | `oa-dilekce/SKILL.md:183-266`; `oa-kontrol/SKILL.md:174-177` | [P] faiz, fazlaya ilişkin hak, gider arar; çok davalılı davada sorumluluk biçimi ve tescil/teslim talebinde konu kimliği aranmaz | taleple bağlılık: eksik kalem hükme girmez | [P]'ye iki advisory kalem (script+test) | avukat+mühendislik | gerekir: TBK m.61-62; HMK m.297/2 |
| B18 | `ANAYASA.md:167-168`; `oa-strateji/SKILL.md:17`; `oa-pipeline/SKILL.md:485` | Anayasa m.9 nihai kararı avukata verir; strateji "karar müvekkilindir", pipeline "farklı egemenlik alanları" der | model karar sahibini karıştırabilir | m.9'a müvekkil kararı alanını tanıyan cümle (metin) | avukat | gerekir: Av.K. m.34 |
| B19 | `oa-alan/SKILL.md:30,36` | Daire kayması örneği tarihli bir iş bölümü kararına dayanıyor; teyit tarihi yok | yıllık iş bölümü değişince örnek bayatlar | teyit tarihi damgası (metin) | mühendislik | gerekir: güncel iş bölümü |

## Avukata sorular (hukuki içerik kararı)

1. m.6 preemptive yasağının istisnaları — kayıt koruma, bağlayıcı otorite, kendi dayanağın sınırlanması, praeoccupatio — hangisi varsayılan, hangisi onaylı olsun? (A2, A5)
2. Zamanaşımı def'i için sistemin "son güvenli an"ı cevap dilekçesi mi sayılsın? (A1)
3. Davalı tarafta karşı delil bildirimi varsayılan mı olsun; delil listesine "karşı delil" etiketiyle mi girsin? (A6)
4. Katılma yoluyla istinaf riski "müvekkil kararı bekleyen" kalemi mi olsun? Kısmi dava değerinin kesinlik etkisi uyarı mı, kapı mı? (A7)
5. Bağlayıcı sayılacak otorite listesi: İBK ve AYM norm denetimi dışında genel kurul kararları da girsin mi? (A5)
6. Davanın ihbarı önerisi hangi graf sinyaliyle tetiklensin: rücu, kefalet, sigorta, alt işveren? (A8)
7. Ceza–hukuk köprüsü (müşteki §0 tablosu) hukuk dosyalarında da zorunlu adım mı olsun? (A4)
8. Akıbet alanı boşken LEHE BAM atfı uyarı mı alsın, BLOK mu? (A9)
9. İş K. m.20/1 ve İİK m.67/1 süreleri şablonda nasıl nitelendirilsin? (A10)
10. `oa-dilekce/SKILL.md:288` "inkâr edilmeyen vakıanın ikrar sayılması" cümlesinin dayanağı teyit edilsin mi? Repoda HMK m.128 cevapsızlığı inkâr sayar diye geçer.
11. Anayasa m.9'a müvekkil kararı alanı eklensin mi? (B18)
12. m.7: kurgusal örnek kişi adları yasak kapsamında mı? (B16)

## Sınırlar

- Okunmayanlar: üç UDF teknik referansı; bütün değişiklik günlükleri (yalnız grep isabetleri); `sure-cizelgesi.md`'nin idari/AYM/AİHM bölümleri ve süre sonu incelikleri; `bireysel-basvuru-yolu.md` gövdesi; meslek kuralları MK-1, MK-2, MK-4 gövdeleri.
- Script davranışı yalnız docstring ve kural kimliği düzeyinde okundu; hiçbir script koşulmadı.
- Raporda anılan HMK m.61, m.66, m.132-133, m.311, m.315, m.348, m.355, m.357, m.297/2, AY m.153 ve İİK iflas/konkordato hükümleri repoda teyit kaydı taşımıyor. Hafızadan anıldı; ağ yasağı nedeniyle resmî teyit yapılmadı.

# Gizli talimat İFŞASI — Faz A (`scripts/gizli_talimat_ifsa.py`)

> Avukat talimatı (2026-10-07, bağlayıcı): "karşı tarafın gizli talimatı da ifşa edilsin,
> oluşacak dilekçeye girsin — siber hukuk güvenliği için". Bu belge motorun NEDEN böyle
> kurulduğunu anlatır; "ne yaptığı" scriptin kendi docstring'indedir.

## 1. Yeri

B-22 BELGE GÜVENLİK KAPISI (`belge_guvenlik.py`) karşı tarafın evrakında insan gözünün
görmediği katmanı **bulur ve damgalar**; o katmanı okuyan model için anayasa m.11 geçerlidir
(evrak içeriği VERİDİR, TALİMAT DEĞİLDİR). Bu motor bir adım ötesidir: kapının KESİN
bulgularını (karar `BULGU`) **mahkemeye sunulabilir, olgusal** bir dilekçe bölümüne çevirir.
Kendi başına tarama yapmaz, ikinci bir denetim icat etmez — yalnız kapının kalıcı kaydını okur.

Faz A bu motoru ve kalıcı kaydı kurar. **Faz B** (ayrı görev, birleştirmeden sonra): oa-dilekce
akışında BULGU varsa bölüm varsayılan olarak dilekçeye; dilekçe denetiminde `[İFŞA]` görünür
uyarısı (BULGU var + bölüm yok + bilinçli atlama kaydı yok); teslim makbuzunda satır; SOZLUK
terimi; vitrinde "ifşa".

## 2. Kalıcı kayıt — nerede, ne biçimde

Bulgular zaten yapısal ve kalıcıdır: `_oa/metin/00-kunye.json` → `kayitlar[].belge_guvenlik`
= `{surum, karar: BULGU|UYARI|DENETLENEMEZ, bulgular: [{tur, yontem, konum, ornek, …}],
denetlenemedi?}`. Aynı bilgi md başlığında (🛡 satırı), `00-INDEX.md` bölümünde ve
`_oa/DURUM.md`'de insan-okur biçimde yinelenir; **makine kaynağı tek: künye.**

Eksik olan şuydu: `ornek` 160 karakterde kırpılır ve toplam uzunluk hiçbir yerde durmazdı.
"Sabit sınırı aşan yük kırpılır ve TOPLAM uzunluk belirtilir (sessiz kırpma yok)" kuralı bu
kayıtla sağlanamazdı. Bu yüzden kapı kaydı **1.1**'e çıktı (`belge_guvenlik.SURUM`):

- `uzunluk` — metinli her bulguda, kırpılmamış normalleştirilmiş metnin karakter sayısı;
- `alinti` — yalnız `ornek` kırpıldıysa, `AZAMI_ALINTI_KAR` (2.000) karaktere kadar metin;
- `ornek` BAYT BAYT eskisi gibidir; metinsiz bulguda (bidi, nüsha sayısı…) alan eklenmez →
  md başlığı, INDEX ve DURUM.md değişmez.

Sürüm ilerlediği için 1.0 işaretli önbellek kaydı bir sonraki ingest'te **yeniden taranır**
(OCR'lı evrakta hafif yol: md metni; şüphe varsa tam yeniden çıkarım). Bu tek seferlik bir
bedeldir ve bilinçlidir: eski kayıtta toplam uzunluk yoktur, motor bunu dilekçede açıkça söyler
("toplam uzunluğu inceleme kaydında bulunmamaktadır") ve iç notta `--yeniden` önerir.

## 3. Arayüz

```
python scripts/gizli_talimat_ifsa.py --kok <dava kökü> [--md <yol>] [--json <yol>]
```

- Çıkış **0** = ifşa edilecek BULGU yok (bölüm üretilmez; `--md` yazılmaz) · **1** = BULGU var,
  bölüm üretildi · **3** = bulgular okunamadı/denetlenemedi (`_oa` ya da künye yok, bozuk JSON,
  şema dışı, kapı modülü yüklenemedi — fail-closed; "temiz" DENMEZ).
- `--json` her kararda yazılır (Faz B kapısı için); `--md` yalnız karar `IFSA_VAR` iken. Bayat bir
  md varsa görünür UYARI basılır, dosya silinmez.
- JSON (`sort_keys`, atomik `tmp + os.replace`): `arac`, `surum`, `karar`
  (`IFSA_VAR | IFSA_YOK | DENETLENEMEDI`), `kaynaklar` (`[{rol: "kunye", yol:
  "metin/00-kunye.json", sha8}]`), `bulgular` (BULGU kayıtlarının AGIR bulguları; her biri
  `evrak, no, sunan_taraf, tur, yontem, konum, yontem_aciklama, konum_aciklama, alinti,
  uzunluk, gosterilen, kirpildi, uzunluk_kayitli, dilekceye_girdi, tutulma_nedeni`),
  `dilekce_bolumu_md`, `ic_not`, `yer_tutucular`, `dayanak`.
- Python: `ifsa_uret(kok) -> dict` (JSON ile aynı içerik). `_oa`'ya YAZMAZ.
- Determinizm: zaman damgası/rastgelelik yok; kayıtlar `(no, kaynak)` ile dizilir; aynı `_oa`
  → bayt-özdeş md ve JSON (testli).

## 4. Dilekçe bölümünün kuralları ve gerekçeleri

| Kural | Uygulama | Neden |
|---|---|---|
| Yalnız `BULGU` kayıtları | `UYARI`/`DENETLENEMEZ` yalnız `ic_not`'ta | Mahkemeye giden metinde yanlış suçlama müvekkile zarar verir (anayasa m.6) |
| Kayıt içinde yalnız AGIR türler | görünür `talimat-dili`, `gorunmez-karakter`, `kahin-devre-disi` dilekçeye girmez | Görünür metin "gizli" değildir; ikincil işaret ifşa konusu değildir |
| Görünür ya da içeriksiz YAPISAL tespit girmez (düzeltme turu 1, Ö-1) | `damga-taklidi` (görünür özel parantez), `isaret-taklidi` (görünür sayfa ayracı satırı), örneği boş `arsiv-nushasi` (özdeş nüsha / beklenen yerde değil) → `dilekceye_girdi: false, tutulma_nedeni: "gorunur-yapisal"`, iç notta; `bidi` (görünmez denetim karakteri) ve metinli FARKLI nüsha kalır | Mahkemeye "insan gözüyle görünmeyen metin" denip hiçbir gizli metin gösterilemez; bir bilirkişi raporundaki matematiksel ayraç ya da yapıştırılmış sayfa ayracı satırı "gizleme" ile anılamaz (anayasa m.6) |
| Şema dışı bulgu girmez (K-1) | `_bulgu_normalize`: tür dizge değil / metin alanı dizge değil → iç notta "şema dışı", dilekçeye girmez; beklenmedik iç hata → `DENETLENEMEDI`, çıkış 3 | Çıkış 1 "BULGU var" demektir; istisna onunla çakışamaz |
| Olgusal, nötr dil | "tespit edilmiştir", "takdirindedir"; niyet/suç/hile sözcükleri testle yasak | Script hukuki karar vermez; nitelendirme avukatın ve Mahkemenin |
| Anılan madde = okunan madde | HMK m.29, m.199 — `DAYANAK` sabiti resmî metni ve künyeyi taşır; test, md'de anılan her maddenin dayanakta olduğunu kilitler | Okunmamış madde anılmaz |
| Her tespit için ad / yer / biçim / alıntı | `_evrak_adi_goster`, `_konum_aciklama`, `_yontem_aciklama`, etiketli `> «…»` bloğu | Mahkemenin doğrulayabileceği somutluk |
| Zararsızlaştırma | görünmez → `[U+XXXX]`; `* _ ~ + < > [ ] & @ \` iki yana boşluk; ters tırnak → `[U+0060]`; bağlantı şeması sonrası `:` → `[U+003A]`, `www.` → `www[U+002E]` (GFM önizlemede tıklanabilir saldırgan bağlantısı kalmaz — K-3); tek satır, «» içinde; 1.500 karakter sınırı + TOPLAM; «»→`"` ve özel parantez→`[]` ikameleri ile sayının normalleştirilmiş kayda ait olduğu gösterim kuralında yazılı (K-2) | Dilekçeyi okuyacak başka yapay zekâ aracı yükü talimat gibi işlemesin; dönüştürücü karakter silmesin; mahkeme hiçbir sessiz dönüşümle karşılaşmasın |
| Evrak adı (K-4) | `*<>[]&\` aralanır; alt çizgi yalnız sözcük sınırında, tilde yalnız koşuda aralanır (`__ad__` kalın, `~~ad~~` üstü çizili olmaz; `cevap_dilekcesi` dokunulmaz) | "Dosyadaki adıyla" iddiası görüntüleyicide bozulmasın |
| İç iz yok | bölümde ⟦⟧, `_oa/`, araç/script adı, `<!--`, üretilmiş md adı geçmez (testli) | Teslim evrakına araç izi sızması B-18/B-19 dersi |
| Sunan taraf | kalıcı kayıtta `sunan_taraf: "karsi-taraf"` ise "karşı tarafça sunulan evrak"; yoksa `[SUNAN TARAF — avukat teyidi]` | Tahminle "karşı taraf" yazılmaz (fail-closed) |
| `ic_not` | doğrulama adımları (Ctrl+A, zemin değiştir, Word gizli metin, izli değişiklik, PDF seçim, Unicode görüntüleyici, zip aç), yer tutucu uyarısı, tutulan tespitler, eski kayıt notu, "karar avukatındır" | Avukat tespiti ASIL evrakta kendi gözüyle doğrular |

### Alıntı nötrleme — iki dönüştürücüye karşı neden "boşluk"?

Hedef iki okuyucu var: CommonMark uyumlu her görüntüleyici ve projenin kendi
`oa-dilekce/scripts/md_udf_html.py` dönüştürücüsü (md → UDF-HTML → `html2udf`). İkincisi
ters eğik çizgi kaçışını TANIMAZ (`\*\*x\*\*` içinde `*\*` çiftini italik yapar) ve ters tırnak
çiftini SİLER (delil kaybı). Her iki okuyucuda da "iki yanı boşluklu işaret" vurgu/etiket/
bağlantı sayılmaz; `<` ardından boşluk etiket açmaz; `](` bitişikliği bozulduğu için bağlantı
oluşmaz. Karakterler silinmez, yalnız aralanır — gösterim kuralı bölümün sonunda mahkemeye
açıkça yazılır. Alıntı tek satır ve `«` ile başladığı için satır başı yapıları (başlık, liste,
tablo, alıntı) tetiklenemez. Test, gerçek dönüştürücüde alıntı paragrafında `<strong>/<em>/<u>/
<a>/<script>` oluşmadığını kilitler.

## 5. Ruling satırları (belirsizlikte verilen kararlar)

- **Ruling: `kahin-devre-disi` evrakta yalnız SEZGİSEL gerekçeli tespitler (yöntemde kontrast /
  alfa / örtü / zemin) dilekçeye alınmaz, iç notta tam metniyle tutulur; deterministik gerekçeli
  tespitler (görünmez kip Tr 3, punto, sayfa dışı, TAG, vanish, silinmiş metin, nüsha, üst veri)
  normal girer** — Neden: kâhin tam da bu dört gerekçenin yanlış alarmını kesmek için eklendi
  (2026-10-05 ölçümü: 41 PDF işaretinin 38'i yanlış alarmdı; DOCX'te 3.343); kâhin çalışmadığında
  görünür bir başlık "gizli" sayılabilir ve ifşa bir suçlama etkisi doğurur — fail-closed yön
  "suçlama yapma"dır; TAG karakteri ya da Tr 3 kipi ise kâhinden bağımsız, dosyadan okunan
  kesinliktir, onu tutmak gerçek bir bulguyu saklamak olurdu — Yanılırsa bedeli: gerçek bir
  beyaz-yazı yükü kâhinsiz makinede dilekçeye kendiliğinden girmez; avukat iç nottaki tam metni
  görür, orijinalde doğrular ya da PyMuPDF ≥ 1.24.2 ile `--yeniden` tarar ve bölüm o zaman
  üretilir (gecikme, kayıp değil).
- **Ruling: sunan taraf için yeni bir `_oa` dosyası/şeması İCAT EDİLMEDİ; motor künye
  kaydındaki isteğe bağlı `sunan_taraf` alanına bakar, bugün hiçbir adım bunu yazmadığı için
  çıktı her zaman yer tutuculudur** — Neden: depoda evrakı hangi tarafın sunduğunu kaydeden
  kalıcı bir yapı yok (`delil_plani.kim` delili KİMİN tedarik edeceğidir, evrakın sunanı değil;
  `teslim_paketi --taraf` bizim dilekçemizin tarafıdır); Faz A'da yeni şema açmak Faz B'nin
  (oa-interview/oa-vakia) tasarımını önceden bağlardı — Yanılırsa bedeli: her evrakta bir yer
  tutucu; Faz B dilekçe denetimi yer tutucuyu zaten kapı yapar (JSON `yer_tutucular`), dilekçe
  doldurulmadan çıkamaz.
- **Ruling: kayıt içindeki AGIR olmayan türler (`talimat-dili` görünür metin, `gorunmez-karakter`)
  BULGU kaydında da dilekçeye alınmaz** — Neden: ifşanın konusu insan gözünün GÖRMEDİĞİ katmandır;
  görünür talimat dili karşı tarafın da gördüğü metindir, "gizleme" iddiası taşımaz — Yanılırsa
  bedeli: iç notta örnekle gösterilir, avukat isterse dilekçeye kendisi yazar.
- **Ruling: alıntı bloğu kod çiti (```) DEĞİL, `> «…»` alıntı satırı** — Neden: `md_udf_html`
  kod çitini tanımaz (satır metin olarak UDF'e girerdi) ve çit içinde `# başlık` yine
  yorumlanırdı; alıntı bloğu hem CommonMark'ta hem dönüştürücüde (QUOTE stili) desteklenir —
  Yanılırsa bedeli: görsel olarak kod bloğu kadar "ayrı" durmaz; etiket satırları ve «» bunu
  telafi eder.
- **Ruling: kapı kaydı 1.0 → 1.1 ve önbellek yeniden taraması kabul edildi** — Neden: eski
  kayıtta TOPLAM uzunluk yoktur; kayıt kendini onarmazsa her eski BULGU dilekçeye "toplam
  uzunluk kayıtta yok" notuyla girerdi; önbellek işareti tam da bunun için var — Yanılırsa
  bedeli: ilk ingest'te tek seferlik yeniden tarama (OCR'lı evrakta md metni hafif yolu).
- **Ruling (düzeltme turu 1, Ö-2 — önceki "varlıklar çözülmez" kararı GERİ ALINDI): kapı, DOCX
  gizli parçasını kaydederken XML'in beş ön tanımlı varlığını (`&amp; &lt; &gt; &quot; &apos;`) ve
  sayısal karakter başvurularını (`&#123;`, `&#x7B;`) TEK GEÇİŞTE çözer (`belge_guvenlik._xml_varlik_coz`);
  HTML'e özgü adlar (`&nbsp;`) ve XML'de geçersiz başvurular (sıfır, vekil, aralık dışı) olduğu gibi
  kalır; çift çözme yok (`&amp;lt;` → "&lt;" dizgesi)** — Neden: iyi biçimli XML'de bu çözüm yorum
  değil kayıpsız ve belirlenimci ters serileştirmedir — belgede harfiyen `&lt;` yazılıysa
  `document.xml`'de `&amp;lt;` durur ve tek geçiş onu doğru ("&lt;") çözer; çözmemek, Word'ün
  gösterdiği `<system>` yerine mahkemeye `& lt;system & gt;` sunmak demekti ("alıntı belgeyle uyuşmuyor"
  itirazı). Kural `oa_ingest.docx_isle` (evrak gövdesi, Görev 6) ile BİREBİR aynı tutulur; kapı,
  parçayı gövdede İKİ yazımla arar (çözülmüş, sonra dosyadaki) ki Görev 6 birleşmeden önce de sonra da
  yerinde damgalama çalışsın — Yanılırsa bedeli: HTML adlı bir varlık (`&nbsp;`) alıntıda ad olarak
  görünür (Word da göstermez — tutarlı). **Birleşme notu:** `belge_guvenlik._docx_duz` docstring'i
  "docx_isle ile AYNI" der; Görev 6 `docx_isle`'ye çözümü eklediğinde `_docx_duz`'a da aynı
  `_xml_varlik_coz` satırı eklenmeli (nüsha farkı satırları gövdede aynı yazımla bulunsun).
- **Ruling (düzeltme turu 1, Ö-1): `damga-taklidi`, `isaret-taklidi` ve örneği boş `arsiv-nushasi`
  dilekçeye GİRMEZ (`tutulma_nedeni: "gorunur-yapisal"`), `bidi` girer** — Neden: üçü görünür ya da
  içeriksiz tespittir (tek bir görünür `⟦` karakteri, görünür "--- sayfa N ---" satırı, içeriği birebir
  aynı ikinci zip girdisi); dilekçe "insan gözüyle görünmeyen metin" deyip hiçbir gizli metin
  gösteremezdi — kural 1'in önlemek istediği yanlış suçlama; `bidi` ise görünmez denetim karakteridir,
  tespit gerçekten görünmez bir katmandır — Yanılırsa bedeli: gerçekten kötü niyetli bir damga taklidi
  ya da özdeş-nüsha hilesi dilekçeye kendiliğinden girmez; iç notta avukata tam gerekçesiyle gösterilir,
  avukat gerekli görürse kendisi yazar.

## 6. Resmî metinler (Yargı PRO `mevzuat_getir`, 2026-10-07; mevzuat.gov.tr)

- **6100 sayılı HMK m.29** (`mevzuatgov:kanun:5:6100:m29`) — Dürüst davranma ve doğruyu söyleme
  yükümlülüğü: "(1) Taraflar, dürüstlük kuralına uygun davranmak zorundadırlar. (2) Taraflar,
  davanın dayanağı olan vakıalara ilişkin açıklamalarını gerçeğe uygun bir biçimde yapmakla
  yükümlüdürler." → Bölümde değerlendirme "Mahkemenin takdirindedir" çizgisinde anılır; aykırılık
  İDDİA EDİLMEZ.
- **6100 sayılı HMK m.199** (`mevzuatgov:kanun:5:6100:m199`) — Belge: "… elektronik ortamdaki
  veriler ve bunlara benzer bilgi taşıyıcıları bu Kanuna göre belgedir." → Gizli katman, evrakın
  (belgenin) içeriğinin parçasıdır; bölüm onu "belge içeriği" olarak sunar.

Suç nitelendirmesi (TCK) bilerek okunmadı ve anılmadı: motor ceza hukuku değerlendirmesi yapmaz.

## 7. Dürüst sınırlar

- Alıntı, kapının kaydettiği normalleştirilmiş metindir: satır sonları ve ardışık boşluklar tek
  boşluk, TAG/RLO/sıfır genişlik karakterleri ayıklanmış (TAG yükü çözülmüş). Birebir bayt
  sadakati evrakın elektronik aslındadır; bölüm bunu söyler.
- DOCX gizli parça KAYDI XML varlıkları çözülmüş (belgenin gösterdiği) metindir (Ö-2); evrak
  GÖVDESİ (`oa_ingest.docx_isle` md'si) Görev 6 birleşene dek dosyadaki yazımdadır — kapı her iki
  yazımı da gövdede arar, damga yerinde kalır. HTML'e özgü varlık adları (`&nbsp;`) çözülmez.
- Görünmez karakter yoğun bir yükte 1.500 kaynak karakteri `[U+XXXX]` kaçışlarıyla ~13 KB'lık tek
  satıra şişebilir: sınır KAYNAK metnindedir, çıktıda değil — bilinçli (kaçış sayısı delilin kendisidir).
- Çıplak URL ve e-posta alıntıda tıklanabilir bağlantı oluşturmaz (`[U+003A]`, `[U+002E]`, ` @ `);
  bu, adresin OKUNMASINI engellemez — yalnız tıklanmasını.
- `yontem_aciklama` tanınan kalıplarla kurulur; tanınmayan gerekçe "biçimsel gizleme (teknik
  ayrıntı inceleme kaydında)" olur — ham gerekçe hiçbir koşulda dilekçeye geçmez.
- Motor evrakın kim tarafından sunulduğunu bilmez (bkz. Ruling); "karşı taraf" ancak kalıcı
  kayıtla yazılır.
- `IFSA_YOK` bir güvenlik beyanı DEĞİLDİR: UYARI/DENETLENEMEZ kayıtları iç notta durur; künye
  yoksa karar `DENETLENEMEDI`'dir (ingest koşmamış dosyada "bulgu yok" denmez).

## 8. Faz B bağlama noktaları (dosya / fonksiyon)

- **oa-dilekce akışı:** `gizli_talimat_ifsa.ifsa_uret(kok)` → `dilekce_bolumu_md` (karar
  `IFSA_VAR` iken) dilekçe taslağının sonuna (EKLER'den önce) eklenir; `yer_tutucular` boş
  değilse taslak "avukat teyidi bekliyor" sayılır.
- **Dilekçe denetimi (`oa-dilekce/scripts/dilekce_denetim.py`):** künyede `belge_guvenlik.bulgu > 0`
  (pipeline_kayit `_belge_guvenlik_ozeti` ile aynı ucuz okuma) ve taslakta `BOLUM_BASLIGI` yoksa ve
  bilinçli atlama kaydı yoksa `[İFŞA]` görünür uyarısı; taslakta `YER_TUTUCU_SUNAN` kalmışsa RET.
- **Teslim makbuzu (`oa-kontrol/scripts/teslim_paketi.py`):** JSON `karar` + `bulgular` sayısı +
  `kaynaklar[0].sha8` satırı (hangi künyeden üretildiği izlenebilir olsun).
- **Sunan taraf:** künye kaydına `sunan_taraf: "karsi-taraf"` yazan tek yer (oa-interview evrak
  rolü sorusu ya da oa-vakia) — `gizli_talimat_ifsa._sunan_taraf` yalnız bu değeri tanır
  (`SUNAN_KARSI`).
- **pipeline_kayit DURUM.md:** `_belge_guvenlik_uyarisi` yanına "ifşa bölümü üretildi/üretilmedi"
  satırı (JSON `karar`).
- **SOZLUK / vitrin:** "İfşa (gizli talimat)" terimi; vitrin cümlesi bu belgeden türetilir.

## 9. Testler

`tests/test_v0518_gizli_talimat_ifsa.py` (26) — bölüm + determinizm, JSON/atomik/sha8,
UYARI-DENETLENEMEZ dışlama, kayıt içi tür dışlama, iç iz/damga sızmazlığı, görünmez karakter
kaçışı, Markdown/HTML etkisizliği (gerçek `md_udf_html` ile), uzun yük kırpma + TOPLAM, eski
kayıt, sunan taraf, nitelendirme yasağı + dayanak eşleşmesi, çıkış 3 / çıkış 0, çoklu evrak sırası,
kâhin devre dışı, uçtan uca (sentetik saldırı evrakı → `oa_ingest` → ifşa), yapısal sözleşme;
düzeltme turu 1: görünür yapısal türler, tür-duyarlı konum, DOCX alıntısı belgenin gösterdiği metin,
beklenmedik istisna → 3, şema dışı bulgu, gösterim kuralı, URL/e-posta, evrak adı vurgu koşusu,
sayısal `no` sırası.
`tests/test_v0518_belge_guvenlik.py` (2) — kapı kaydı 1.1; DOCX gizli parçada XML varlıklarının tek
geçiş çözümü ve iki yazımlı gövde eşlemesi. Gerçek evrak YOK; tüm fikstür sentetik (anayasa m.7).

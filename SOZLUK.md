# HUKUKÇULAR İÇİN SÖZLÜK

> Bu repoda geçen teknik terimlerin, avukatın/hâkimin/savcının diliyle
> karşılıkları. Benzetmeler kolaylık içindir; teknik ayrıntı için ilgili
> belgeye bağlantı verilmiştir.

## Temel kavramlar

**Yapay zekâ / Büyük dil modeli (LLM):** Metin okuyup metin üreten yazılım.
Çok okumuş ama **yemin etmemiş** bir stajyer gibidir: parlak akıl yürütür,
fakat kaynak göstermeye zorlanmazsa uydurabilir. Bu sistemin varlık sebebi
onu kaynağa ve kayda zorlamaktır.

**Prompt:** Modele yazdığınız talimat/istek metni. Bu sistemde tek doğal
cümle yeter; metodolojiyi promptla öğretmezsiniz, sistem kendi disiplinini
işletir.

**Token:** Modelin okuma-yazma ölçü birimi (kabaca hece/kelime parçası).
"Dosya masrafı"nın buradaki karşılığıdır: aynı işi daha az tokenle yapmak,
aynı dilekçeyi daha az fotokopi parasıyla çıkarmak gibidir — sistem bunu
evrakı görüntü yerine metin olarak okuyarak başarır.

**Halüsinasyon:** Modelin olmayan şeyi (tipik olarak olmayan içtihadı)
gerçekmiş gibi yazması. Bu sistemde yapısal panzehiri vardır: künyesi resmî
kaynaktan teyit edilmemiş ve tam metni okunmamış karar dilekçeye giremez.

**Deterministik:** Aynı girdiye her zaman aynı sonucu veren, keyfiyeti
olmayan işleyiş. Harç hesabı gibi: kim hesaplarsa hesaplasın sonuç aynıdır.
Sistemin denetim katmanı bilerek böyle kurulmuştur — "model kurar, script
denetler, model muhakeme eder."

**Script (betik):** Belirli bir işi her seferinde aynı şekilde yapan küçük
program (burada Python dilinde). Duygusu, yorumu, "bugün üşendim"i yoktur;
bu yüzden denetim ona emanettir. Script yalan söyleyemez.

## Sistemin çalışma düzeni

**Skill / parça:** Sistemin bir yeteneği (ör. süre hesabı, antitez, teslim
denetimi). Yirmi parça, tek bir kıdemli meslektaşın yetenekleri gibi birlikte
çalışır; ayrı programlar değildir.

**Eklenti (plugin) / Marketplace:** Skill setinin Claude Code'a kurulan
paket hâli ve o paketin dağıtıldığı kanal. Baro levhası benzetmesi yanlış
olmaz: eklenti oradan "kaydolur", güncellemeler oradan gelir.

**Hook (kanca):** Belirli anlarda **kendiliğinden** devreye giren tetik:
oturum açılınca, siz her mesaj yazınca, model dosya yazınca, oturum
kapanınca. Kalemdeki nöbetçi kâtip gibidir — kimse çağırmasa da damgasını
basar, uyarısını düşer.

**MCP:** Modelin dış kaynaklara (içtihat/mevzuat veri tabanları gibi)
bağlandığı standart köprü. **Yargı Pro MCP** bu sistemin varsayılan içtihat
kanalıdır; açık kaynak alternatif **yargi-mcp**'dir (semantik arama için
ayrıca bir AI API anahtarı ister).

**API anahtarı:** Bir çevrimiçi hizmeti kullanma yetkinizi kanıtlayan gizli
kod — vekâletnamenin dijital karşılığı gibi düşünün. Kimseyle paylaşılmaz;
bu sistemin gizlilik katmanı onu dışarı da sızdırmaz.

**Oturum (session):** Claude Code penceresinde tek bir çalışma celsesi.
Sistem celseler arası hafızayı diskte (`_oa/`) tutar; yeni celse dosyayı
"duruşmaya kaldığı yerden" devralır. v0.5.11'den beri her kayıt hangi
celsenin ürünü olduğunu da söyler (**oturum damgası**).

**Semantik arama:** Kelimeyle değil ANLAMLA arama. "Menfi tespit" yazmadan,
olayı cümleyle anlatıp o olaya benzeyen kararları bulmak — kelime eşleşmesi
tıkandığında devreye giren yedek kanaldır.

**İlliyet grafı:** Dosyadaki kişi–kurum–delil–olay bağlarının çizge hâli:
kim kime ne yapmış, hangi fiil hangi neticeyi doğurmuş, her bağın dayandığı
delil ne. Sistem bu haritada **kesme noktası** (illiyeti kesen savunma
adayları) ve **ispat boşluğu** arar.

## Kayıt ve güvence katmanı

**`_oa/` kökü:** Dava klasörünüzün içinde sistemin açtığı çalışma dosyası —
büronuzdaki dosya gömleği gibi. Defter, kütük, taslaklar, makbuzlar hep
burada; müvekkil evrakının aslına dokunulmaz (salt-okunur).

**Defter (append-only):** Sistemin olay defteri. "Append-only" = yalnız
sona eklenir; geçmiş kayıt silinemez, değiştirilemez — esas defterinin
dijital ahlâkı. Karneler bu defterden çıkar.

**Künye teyidi:** Bir kararın esas/karar numarasının ve dairesinin resmî
kaynaktan doğrulanması — UYAP'tan aslını celbetmeden fotokopiye itibar
etmemek gibi. Teyitsiz künye "iddia"dır, atıf değildir.

**Damga (LEHE/ALEYHE) ve mutlak triyaj [G6]:** Tam metni okunan her karar
kütüğe damgalanır: LEHE ise dilekçeye girebilir; ALEYHE ise **giremez** —
**cephaneliğe** (yalnız sizin gördüğünüz iç dosyaya) kalkar ki duruşmada
sürprizle karşılaşmayın.

**Makbuz (yeşil/RED):** Teslim zincirinin sonunda kesilen resmî sonuç
belgesi. **Yeşil makbuz** = dokuz denetim kapısının fiilen koşup geçtiğinin
kanıtı; **RED makbuzu** = hangi kapının neden kapandığının belgesi.
Harç makbuzu neyse bu da odur: makbuz yoksa işlem yok sayılır.

**Mühür (provenance):** Ürünün yanına basılan kimlik kaydı: hangi kaynaktan,
hangi araçla, hangi içerik parmak iziyle üretildi. Noter mührünün dosya
karşılığı. Ürün mühürden sonra değişmişse sistem bunu fark eder ve teslimi
durdurur.

**Kapı / fail-closed:** Denetim noktası. "Fail-closed" = tereddütte
KAPANIR: denetim scripti bulunamazsa "geçmiş sayalım" denmez, teslim durur.
Şüpheden sanık yararlanır ama şüpheden **teslim** yararlanamaz.

**Sunum kilidi:** Makbuzsuz (veya mührü bayat) bir teslim-sınıfı dosya size
gönderilmek istenirse sistemin durup "emin misiniz?" diye sorması. Karar
devri sizdedir; ama artık görmeden olmaz.

**40-UYAP dizini:** Yeşil makbuz kesilince dava klasörünüzde doğan çıktı
klasörü — UYAP'a yüklenecek her şey (UDF, PDF, mühürler, makbuz kopyası)
tek yerde. E-imza ve yükleme yalnız avukata aittir.

**Kit / araç çantası · bayat araç:** Denetim scriptlerinin dava klasörüne
alınan çalışma kopyaları. "Bayat" = eski nesil kopya — eski matbu dilekçeyle
yeni usulde iş yapmak gibi tehlikelidir; v0.5.11 bu çantayı kilitler ve
kaynağını denetler.

## Dosya biçimleri ve yardımcı araçlar

**UDF:** UYAP'ın belge biçimi. Kritik saha dersi: elle/başka yolla kurulan
UDF, UYAP editöründe **açılmayabilir** — bu yüzden üretim yalnız resmî
araçla yapılır ve dosya açılabilirlik kapısından geçirilir.

**OCR / Tesseract:** Taranmış evraktaki görüntüyü metne çeviren teknoloji
ve bu iş için kullanılan ücretsiz program. Islak imzalı, faks kokulu
mazbatalar ancak böyle okunur; OCR çıktısı her zaman "⚠ teyit gerek"
damgası taşır — makine okuması, aslın yerine geçmez.

**Python / pip · Node.js / npx:** İki yazılım ortamı ve paket araçları.
Python = denetim scriptlerinin dili; Node.js = UDF üretim araçlarının
koştuğu ortam. "pip install" ve "npx" komutları, ilgili aracı kurup
çalıştırmanın standart yoludur — kurulum bölümünde adım adım verilir.

**Terminal / komut satırı:** Programlara yazıyla talimat verilen pencere.
Korkulacak bir şey değildir; kurulumdaki komutlar kopyala-yapıştırdır.

## Geliştirme ve kanıt düzeni

**Depo (repo) / GitHub · commit · sürüm etiketi:** Sistemin kaynak
dosyalarının tutulduğu yer, her değişikliğin tarihli-imzalı kaydı ve
yayımlanan sürümün damgası. Değişiklik günlüğü gibi: kim, ne zaman, neyi,
neden değiştirdi — hepsi geriye doğru izlenebilir
([CHANGELOG.md](CHANGELOG.md)).

**Test / regresyon testi / TDD:** Sistemin her güvencesini otomatik sınayan
1.385 senaryo. "Regresyon" = bir kez düzeltilen kusurun sessizce geri
gelmesi; her kusurun testi süitte nöbette kaldığı için gelemez. TDD = önce
kusuru yeniden üreten test yazılır (KIRMIZI görülür), sonra onarım
(YEŞİL). Ayrıntı: [tests/README.md](tests/README.md).

**CI:** Her değişiklikte tüm testleri dört ayrı ortamda kendiliğinden
koşturan hakem. Kural: **CI yeşermeden sürüm yayınlanamaz** — onaysız
karar tebliğe çıkmaz.

**Karne:** Bir saha koşusunun dürüst sonuç belgesi — neyin çalıştığı,
neyin kırıldığı, hangi onarımın doğduğu. Başarısızlıklar da yazılır;
sürümler karneden doğar ([SAHA-DENEYLERI.md](SAHA-DENEYLERI.md)).

---
*Eksik terim mi var? Repoda karşılaştığınız ve burada bulamadığınız her
terim bir eksikliktir — bildirin, eklensin.*

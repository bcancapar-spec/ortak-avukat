---
name: oa-illiyet
description: >
  Ortak Avukat sisteminin NEDENSELLİK / İLİŞKİ / İLLİYET parçası ve tüm aileyi kuşatan
  kesişen katman. Bir uyuşmazlıkta kişilerin, şirketlerin, kamu kurumlarının,
  nesnelerin ve delillerin birbirleriyle bağını ve neden-sonuç (illiyet) zincirini
  yönlü graf olarak modellemek için DEVREYE GİR: müşteki↔şüpheli, katılan↔sanık↔hükümlü,
  davacı↔davalı, alacaklı↔borçlu↔üçüncü kişi, asıl-alt işveren, ortak-müdür-şirket,
  fiil→netice→zarar ilişkilerini kur; kesme noktalarını (mücbir sebep, mağdur/üçüncü
  kişi kusuru), köprü düğümlerini (muvazaa/perde sinyali) ve ispat boşluklarını tespit
  et. "kim kime nasıl bağlı", "neden-sonuç", "illiyet bağı", "ilişki haritası",
  "kesilme savunması" türü her işte — kullanıcı açıkça istemese bile bir
  dosya/dilekçe/tez analiz edilirken — tetikle.
---

# oa-illiyet — Nedensellik / İlişki / İlliyet Kiti

Bu parça, Türk hukukunda her uyuşmazlığın altında yatan **bağ ve neden-sonuç
yapısını** açık, denetlenebilir bir **yönlü grafa** çevirir. Anayasadaki "illiyet
bağı odaklı muhakeme" prensibini bir beyandan **operasyonel araca** dönüştürür.

Temel ayrım — kit bunun üstüne kuruludur: **iki tip kenar var.** Statik *ilişki*
kenarları (kim kime nasıl bağlı) ile dinamik *illiyet* kenarları (ne neye yol
açtı) farklı şeylerdir ve ayrı modellenir. Bu ayrım yapılmazsa "ortaklık bağı"
ile "fiilin zarara yol açması" karışır ve muhakeme bozulur.

## İş bölümü: model kurar, script denetler, model yorumlar

- **Modelin işi (muhakeme):** grafı kurmak (düğüm/kenar çıkarmak), illiyet tipini
  değerlendirmek (uygun illiyet mi, objektif isnadiyet mi), kesme savunmasının
  gerçekten illiyeti kesip kesmediğine karar vermek. Bunlar yargıdır,
  deterministikleştirilemez.
- **Scriptin işi (garantör):** kurulan grafta gözün kaçıracağı boşlukları kesin
  yakalamak — yetim düğüm, kırık zincir, desteksiz kenar, köprü düğüm, çevrim,
  kesme adayları, yük taşıyan kenar. `scripts/grafik_denetim.py`.
- **Yine modelin işi (yorum):** script raporunu hukuki sonuca bağlamak.

Sahte kesinlikten kaçın: script "uygun illiyet vardır" demez; sadece yapısal
boşluğu işaretler. İlliyetin hukuki niteliği daima muhakeme konusudur.

## Akış

### 1. Grafı kur (düğüm + iki tip kenar)

Dosyadaki her aktör ve unsuru düğüm yap. Düğüm tipleri:
`gercek_kisi` (usul rolü ZORUNLU: şüpheli/sanık/hükümlü · müşteki/katılan/mağdur ·
davacı/davalı/müdahil · alacaklı/borçlu/üçüncü kişi · tanık/bilirkişi),
`tuzel_kisi` (şirket/ticari işletme/adi ortaklık), `kamu` (idare/SGK/icra/mahkeme/
kolluk), `nesne` (taşınmaz/taşınır/araç/ziynet/senet/para), `delil`
(belge/tanık/bilirkişi/keşif/dijital), `olay` (fiil/işlem/sözleşme/haciz/tebligat),
`hak` (mülkiyet/alacak/talep).

Kenarları İKİ kategoride çıkar:

**(A) İlişki kenarı (statik bağ):** `ortaklik`, `temsil`, `vekalet`, `akrabalik`,
`isci_isveren`, `asil_alt_isveren`, `alacakli_borclu`, `mulkiyet`, `zilyetlik`,
`muvazaa`, `organik_bag`, `hakimiyet`, `kefalet`, `sozlesme_tarafi`,
`istirak` (TCK m.37-39: faillik/azmettirme/yardım).

**(B) İlliyet kenarı (neden-sonuç):** `fiil_netice`, `sebep_zarar`, `ihlal_sonuc`,
`kusur_zarar`, `islem_sonuc`. Her illiyet kenarı şu nitelikleri taşır:
- `illiyet_tipi`: `dogal` (conditio sine qua non) / `uygun` (medeni, hakim teori) /
  `objektif_isnadiyet` (ceza)
- `guc`: `dispozitif` / `guclu` / `zayif` / `tartismali`
- `kesme_flag`: yoksa boş; varsa `mucbir_sebep` / `magdur_kusuru` / `ucuncu_kisi_kusuru`

**Her kenarın zorunlu meta verisi** (eksikse script yakalar):
- `dayanak_delil`: hangi delil düğümü kanıtlıyor (liste; boş olabilir ama o zaman boşluk)
- `dogrulama`: `teyitli` (delil/MCP) / `iddia` (delilsiz) / `karine`
- `norm`: kenarı hukuken anlamlı kılan madde (örn. zilyetlik→İİK m.97; temsil→TTK m.370)

İlliyet doktrinini uygularken `references/illiyet-doktrini.md`'yi oku. Hangi normun
illiyeti düzenlediğinden emin değilsen **oa-ictihat ile Mevzuat/Yargı Pro'den teyit
et** — hafızadan norm/künye üretme.

### 2. Grafı JSON yaz ve denetle

Grafı `_oa/cikti/01-illiyet-graf.json` olarak yaz (şema `references/illiyet-doktrini.md` sonunda; çalışma evrakı kuralı).
Sonra deterministik denetimi çalıştır:

```bash
python scripts/grafik_denetim.py _oa/cikti/01-illiyet-graf.json
```

Script şunları kesin tespit eder ve raporlar:
- **Yetim düğüm** — hiçbir kenara bağlı değil (dosyada neden var?)
- **Desteksiz kenar** — `dogrulama: iddia` ve `dayanak_delil` boş (ispat boşluğu → oa-vakia)
- **Kırık illiyet zinciri** — illiyet kenarları uçtan uca bağlanmıyor (eksik ara halka)
- **Köprü düğüm** — iki ayrı kümeyi bağlayan tek düğüm (örn. iki şirketi bağlayan
  müdür → MUVAZAA / tüzel kişilik perdesinin aralanması sinyali)
- **Çevrim** — dairesel illiyet (mantık hatası)
- **Kesme adayları** — `kesme_flag` dolu illiyet kenarları (→ oa-antitez beslemesi)
- **Yük taşıyan kenar** — çıkarılırsa illiyet zincirini koparan kritik bağ (→ oa-strateji)

### 3. Raporu hukuki sonuca bağla (model)

Script çıktısını yorumla: hangi boşluk müvekkil-aleyhine, hangi köprü düğüm karşı
tarafın vuracağı yer, hangi kesme savunması ciddi. Boşlukları açıkça müvekkile
bildir (anayasa: zaafları rahatsız edici olsa da söyle).

### 4. "İlliyet / Bağ Haritası" bloğunu üret

Her esaslı çıktıya `references/cikti-blogu.md`'deki standart bloğu ekle (taraflar+rol,
ilişki kenarları, illiyet kenarları, boşluk denetimi, oa-antitez beslemesi).

## Diğer parçalara entegrasyon

Bu kit tek başına da çalışır ama asıl gücü kuşatıcılığındadır. Çağrı haritası:

- **oa-interview** → ilk alımda düğüm ve bağları topla; graf burada doğar.
- **oa-vakia** → iddia↔delil matrisi grafın alt kümesidir; yetim delil = yetim düğüm.
- **oa-kiyas** → küçük önerme = doğrulanmış illiyet grafı (düz olgu listesi değil).
- **oa-antitez** → kesme adaylarını ve zayıf/desteksiz kenarları otomatik karşı-cephe yap.
- **oa-strateji** → yük taşıyan düğüm/kenar = stratejik hedef.
- **oa-dilekce** → vakıa anlatımı = anlatılan illiyet zinciri; her halka delile bağlı.
- **oa-sure** → sürenin başlangıcı bir illiyet düğümüdür (tetikleyici fiil/öğrenme/tebliğ).
- **oa-kontrol** → teslimden önce: kopuk halka var mı, kesme savunması ihmal edilmiş mi,
  yük taşıyan bağ yeterince ispatlı mı.

## Anayasal süzgeç

Üretilen graf **karar materyalidir, karar değildir**. İlliyetin hukuki niteliği ve
nihai sorumluluk Av. Bayram Can Çapar'a aittir. Her kenar teyitli/iddia/karine
etiketlidir; doğrulanmamış illiyet null kabul edilir. Norm ve künye yalnızca resmî
kaynaktan (Yargı/Mevzuat MCP) teyitlidir — hafızadan üretilmez.

## Anayasal düstur — usul esasa üstündür
Usulün esasa takaddümü ailenin anayasal düsturudur: usulden düşen dosya esasa hiç giremez; süre, usul hukukunun parçası ve telafisiz tek hatadır. Grafta **tarihli usul olayları** (tebliğ → süre → işlem) ayrı düğüm tipiyle işaretlenir ve usul zinciri esas zincirinden önce denetlenir; kopuk usul halkası (süresinde yapılmamış işlem) `oa-sure --islem`e raporlanır. **`oa-usul` ile EŞGÜDÜM (çift yönlü):** usul düğümleri oa-usul taramasının girdisidir; oa-usul tespitleri grafı topolojik günceller — sakat tebliğ 'tebliğ→süre' kenarını keser, yok hükmünde kamu işlemi düğümü ve türev kenarlarını düşürür, delil yasağı ispat kenarını koparır. Kesme analizi iki parçanın ortak motorudur; pipeline'da aynı graf birlikte güncellenir.

## Anayasal bloklar — tek kaynak (anayasa.md)
Bu parça, ailenin ortak anayasal ilkelerine tabidir — **Çaba/token standardı** (model/efor kullanıcının tercihi; muhakemede/doğrulamada/çıktı kalitesinde tasarruf YOK, yalnız mekanik katmanda kayıpsız verimlilik), **Örnekleme ilkesi** (konu sınırlaması yok — kapsam TÜM Türk hukuku), **Doğaçlama meşruiyeti** (yöntem serbest, olgu MCP-teyitli), ayrıca Doğrulama mimarisi, Anonimleştirme ve Layer 0 gizlilik. **Tek ve yetkili kaynak: `ortak-avukat/references/anayasa.md`.** (Bu parça alt-ajan olarak koşarken bu ilkeler `oa-pipeline/scripts/oa_hafiza.py ajan-brif` ile taşınır.)

## Başbakan denetimi (anayasal)
Bu parça, ailenin Başbakanı `oa-pipeline`'ın icra+denetimine tabidir: çağrıldığında disiplini İSTİSNASIZ ve tam işletilir (ama/fakat/token-tasarrufu gerekçesiyle kestirme YASAK). Görev savsaklanmaz; gerçekten yapılamayan bir şey varsa dürüstçe belirtilir ("yaptım" denmez) ve alternatif yöntem üretilir. Önemli olan proses ve çıktı kalitesidir.

## Halüsinasyon teftişine tabi (anayasal)
Grafa yazılan her karar/olgu düğümü Başbakan'ın olgu-teftişine tabidir: künyeye dayanan düğümler Yargı Pro'dan, norma dayananlar Mevzuat MCP'den teyitlidir. Teyit edilemeyen düğüm grafa teyitli olarak girmez — 'doğrulanamadı' işaretlenir veya dışlanır. Uydurma karar/madde üzerine illiyet zinciri kurulamaz.

## Fiziksel aktivasyon — simülasyon yasağı (anayasal)
Bu parça yalnızca ÜÇ kanıttan en az biriyle "çalıştı" sayılır: (1) Skill aracıyla FİİLEN çağrıldı ve bu gövde bağlama yüklendi (kullanıcının `/oa-illiyet` komutuyla eşdeğer); (2) scripti gerçekten koştu ve çıktısı görünür; (3) gerektirdiği MCP çağrısı fiilen yapıldı (araç + sorgu + sonuç kaydıyla). Kısa description her zaman bağlamda durur — o VİTRİNDİR, disiplin değildir; gerçek disiplin bu gövdededir. Bu yüzden hiçbir parça bu parçayı description'ından TAKLİT EDEMEZ; bu parça da başka bir parçanın işine ihtiyaç duyduğunda onu Skill aracıyla fiilen çağırır (olmuyorsa SKILL.md'sini Read ile yükler; o da olmuyorsa "FİZİKEN YÜKLENEMEDİ" diye açıkça yazar). Yapılmamış çağrı 'yapılmış', koşmamış script 'koşmuş' gösterilemez — bu, halüsinasyonun ta kendisidir. Devir alırken/verirken kısa DEVİR PAKETİ (ne yapıldı → ne bekleniyor → hangi kanıt) kullanılır ve pipeline defterine (`oa-pipeline/scripts/pipeline_kayit.py`) işlenir. Bu parçanın ürettiği her kalıcı çıktı (JSON/rapor/devir paketi) çalışılan klasörün `_oa/` yerel hafıza kökünde yaşar (yapı: `oa-pipeline` → Çalışma Kökü).

## Değişiklik Günlüğü
Tam günlük `references/degisiklik-gunlugu.md`'dedir (bağlam ekonomisi için ayrıldı — içerik aynen korunur; yeni kayıtlar oraya işlenir). Güncel sürüm: **v3.20**.

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

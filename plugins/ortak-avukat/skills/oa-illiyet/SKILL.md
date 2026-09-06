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
`hak` (mülkiyet/alacak/talep), `karar` (ilk derece/BAM/Yargıtay kararı) ve `mahkeme`
(v0.5.16 — kanun yolu katı; köprü/perde hesabından muaf, çünkü mahkeme yapısı gereği
her tarafı bağlar). Ticaret dosyasında organik bağ ve tüzel kişilik perdesi için AYRI
`hak` düğümleri kur (şablon: `references/cikti-blogu.md`, doktrin §4).

Kenarları İKİ kategoride çıkar:

**(A) İlişki kenarı (statik bağ):** `ortaklik`, `temsil`, `vekalet`, `akrabalik`,
`isci_isveren`, `asil_alt_isveren`, `alacakli_borclu`, `mulkiyet`, `zilyetlik`,
`muvazaa`, `organik_bag`, `hakimiyet`, `kefalet`, `sozlesme_tarafi`,
`istirak` (TCK m.37-39: faillik/azmettirme/yardım), `kanun_yolu` (v0.5.16 — YALNIZ
`karar | mahkeme` düğümleri arasında, kat sırasıyla alt derece → üst derece; `sonuc`
ZORUNLU: `onadi | bozdu | kaldirdi | geri_cevirdi | esastan_ret | kesin`; illiyet
zincirine/çevrime/yük hesabına GİRMEZ — §9 "KANUN YOLU ZİNCİRİ" + JSON
`kanun_yolu_zinciri`).

**(B) İlliyet kenarı (neden-sonuç):** `fiil_netice`, `sebep_zarar`, `ihlal_sonuc`,
`kusur_zarar`, `islem_sonuc`. Her illiyet kenarı şu nitelikleri taşır:
- `illiyet_tipi`: `dogal` (conditio sine qua non) / `uygun` (medeni, hakim teori) /
  `objektif_isnadiyet` (ceza)
- `guc`: `dispozitif` / `guclu` / `zayif` / `tartismali`
- `kesme_flag`: yoksa boş; varsa **DAL ÖNEKLİ** (v0.5.16 — şema kırıldı, avukat
  kararı #7): medeni → `medeni:mucbir_sebep` / `medeni:magdur_kusuru` /
  `medeni:ucuncu_kisi_kusuru`; miras → `miras:paylastirma_kasti` / `miras:ivaz`;
  ceza → `ceza:izin_verilen_risk` / `ceza:kendi_tehlikesine_girme` /
  `ceza:hukuka_uygunluk` / `ceza:magdur_kusuru`. Aynı etiket üç dalda üç ayrı
  hukuki sonuç doğurur; eski çıplak değer (`magdur_kusuru` vb.) `[ŞEMA UYARISI]`
  alır ve `--goc` ile dal etiketlenir (exit değişmez — geriye uyum).
  **Doktrin hatırlatması (hukuki HÜKÜM değil):** `ceza:magdur_kusuru` için script §6'da
  sabit not basar — "illiyeti KESMEZ, kusur derecesine/ceza miktarına etki eder
  (Yargıtay 12. CD yerleşik hattı; künye KÜTÜKTEN, hafızadan yazılmaz; TCK m.22/4-5 —
  Mevzuat MCP teyit 2026-09-07)"; `miras:paylastirma_kasti` için "muris muvazaasında
  bozma gerekçesi — ispat ölçütü". Bu satırlar doktrin hatırlatmasıdır, hukuki hüküm
  değil: kesip kesmediğine script DEĞİL avukat karar verir (model kurar, script
  denetler; script hukuki yorum yapmaz, sadece hatırlatır).

**Her kenarın zorunlu meta verisi** (eksikse script yakalar):
- `dayanak_delil`: hangi delil düğümü kanıtlıyor (liste; boş olabilir ama o zaman boşluk)
- `dogrulama`: `teyitli` (delil/MCP) / `iddia` (delilsiz) / `karine`
- `norm`: kenarı hukuken anlamlı kılan madde (örn. zilyetlik→İİK m.97; temsil→TTK m.370)

İlliyet doktrinini uygularken `references/illiyet-doktrini.md`'yi oku. Hangi normun
illiyeti düzenlediğinden emin değilsen **oa-ictihat ile Mevzuat/Yargı Pro'den teyit
et** — hafızadan norm/künye üretme.

### 2. Grafı JSON yaz ve denetle

Grafı `_oa/cikti/01-illiyet-graf.json` olarak yaz (şema `references/illiyet-doktrini.md` sonunda; çalışma evrakı kuralı).
Sonra deterministik denetimi çalıştır (`--json` ZORUNLU — bekçi/B grubu bu
dosyayı okur; v0.5.16 dersi: köşeli parantezli "opsiyonel" kapı sahada 0 kez
ateşlenmişti — opsiyonel kapı = ateşlemeyen kapı):

```bash
python scripts/grafik_denetim.py _oa/cikti/01-illiyet-graf.json --json _oa/cikti/01-illiyet-denetim.json
```

**Taraf → tavsiye yönü (v0.5.16 G9, avukat kararı #8 — defterden, CLI override):**
`--taraf sanik|mudafii|katilan|musteki|davaci|davali|alacakli|borclu` VEYA `--kok <dava kökü>`
ver; `--kok` verilirse `<kök>/_oa/defter/pipeline-durum.json` `ceza_dali` alanı okunur
(`mudafii` → sanık tarafı, `musteki` → müşteki tarafı; hukuk dosyasında alan boştur).
Taraf savunma/borçlu/davalı kanadındaysa §6/§7/§8 tavsiye yönü TERSİNE döner:
"bu bağı sağlamlaştır" → "karşı tarafın bu bağını ÇÜRÜT / kesme savunmasını KUR"
(JSON `taraf`, `yon: "kur" | "curut"`). Taraf bilinmiyorsa mevcut "kur" metni +
"taraf bilinmiyor — --taraf ver" notu; `--taraf` defteri ezer.

```bash
python scripts/grafik_denetim.py _oa/cikti/01-illiyet-graf.json --json _oa/cikti/01-illiyet-denetim.json --kok .
python scripts/grafik_denetim.py _oa/cikti/01-illiyet-graf.json --json _oa/cikti/01-illiyet-denetim.json --taraf sanik
```

**Göç (v0.5.16 G10):** eski (dal öneksiz) grafı yeniden etiketle — kaynağa dokunmaz,
değişen kenar sayısını basar; hedef dalda kanonik olmayan değer göçmez ("elle düzelt"):

```bash
python scripts/grafik_denetim.py --goc _oa/cikti/01-illiyet-graf.json --dal medeni --cikti _oa/cikti/01-illiyet-graf.v2.json
```

**Çıkış kodu sözleşmesi (v0.5.16 — SERT KAPI, avukat kararı #1):**

| exit | anlam | JSON |
|---|---|---|
| exit 0 | temiz — şema hatası yok, çevrim yok | `cikis_kodu: 0`, `blok_sinifi: []` |
| exit 1 | kullanım hatası (argüman yok) | — |
| exit 2 | **DENETİM ÇÖKTÜ** (dosya yok / bozuk JSON / beklenmeyen istisna) — stdout `DENETİM ÇÖKTÜ: <sınıf>: <mesaj>` | `denetim_coktu: true`, `hata`, `cikis_kodu: 2` |
| exit 3 | **çevrim VEYA şema hatası** var — temizlenmeden pipeline ilerlemez (şema: eksik id/tip/usul_rolu, mükerrer id, illiyet kenarında `illiyet_tipi`/`dogrulama`, `kanun_yolu` kenarında `sonuc`) | `cikis_kodu: 3`, `blok_sinifi: ["sema" \| "cevrim"]` |

`--goc` alt komutu: 0 tamam · 1 eksik argüman · 2 `GÖÇ ÇÖKTÜ` (çıktı yazılmaz).
Exit 2/3 durdurur; 0 dışındaki her kod avukata görünür (sessiz yeşil yok).
`[ŞEMA UYARISI]` satırları (eski çıplak `kesme_flag`, karar-dışı uçlu `kanun_yolu`,
kanonik-dışı `sonuc`) advisory'dir — exit'i değiştirmez.
`--json` alanları (bekçi sözleşmesi, adlar birebir): `arac="grafik_denetim"`,
`sema_hatalari`, `cevrimler`, `denetim_coktu`, `cikis_kodu`, `blok_sinifi`,
`yetim_dugumler`, `baglanmamis_deliller`, `desteksiz_kenarlar`,
`guc_beyansiz_kenarlar`, `kopru_dugumler[].etiket`,
`kesme_adaylari[].{kesme_flag, dal, not}`, `yuk_tasiyan_kenarlar`, `zincirler`,
`zincir_uyarisi`, `taraf`, `yon`, `kanun_yolu_zinciri[].{yol, sonuclar}`.

Script şunları kesin tespit eder ve raporlar:
- **Şema hatası (exit 3)** — eksik `id`/`tip`/`usul_rolu`, **mükerrer düğüm id**
  (ilk kayıt korunur, hata basılır), tanımsız kaynak/hedef, illiyet kenarında
  eksik `illiyet_tipi` **ve eksik `dogrulama`** (v0.5.16: doğrulanmamış
  illiyet sessizce teyitli sayılamaz). `norm` eksikliği `[ŞEMA UYARISI]`
  (advisory) — saha grafları kırılmaz ama Mevzuat MCP teyitli norm istenir.
- **Yetim düğüm** — hiçbir kenara bağlı değil (dosyada neden var?). `tip: delil`
  düğümleri bu sınıfa girmez (aşağıdaki ayrı sınıf).
- **BAĞLANMAMIŞ DELİL (§2b, ayrı sınıf — v0.5.16)** — hiçbir kenarın
  `dayanak_delil`inde anılmayan `tip: delil` düğümü: oa-vakia'nın *yetim delil*
  semantiği — hangi iddiayı/kenarı ispatlıyor? Referans düğüm id'si olabilir;
  serbest metinse delil `ad`ıyla ≥0.6 yazım benzerliği (tr küçük harf) bağlı
  sayar. JSON `baglanmamis_deliller: [{id, ad}]`. (ispat yükü çerçevesi:
  HMK m.190 — Mevzuat MCP teyit 2026-09-06)
- **Desteksiz kenar** — `dogrulama` beyan edilmemiş VEYA (`dogrulama: iddia` ve
  `dayanak_delil` boş) (ispat boşluğu → oa-vakia)
- **GÜÇ BEYAN EDİLMEMİŞ (§3, ayrı sınıf — v0.5.16)** — `guc` verilmemiş illiyet
  kenarı; zincir analizinde ağırlığı `beyan-yok = 0.4 ≤ tartışmalı` (eski 0.8
  "beyan etmeyeni zayıf beyan edenden güçlü sayıyordu" — dürüstlük ödülü
  tersine dönmüştü). JSON `guc_beyansiz_kenarlar`.
- **Kırık illiyet zinciri** — illiyet kenarları uçtan uca bağlanmıyor (eksik ara halka)
- **Köprü düğüm (tip-duyarlı etiket — v0.5.16)** — kaldırılınca grafı en az iki
  ≥2 düğümlü parçaya bölen tek düğüm (yaprak komşusu ve A-B-C zincirinin orta
  düğümü ELENİR). Etiket: **`perde`** = köprü `gercek_kisi` ve ayırdığı en az
  iki parçanın her birinde `tuzel_kisi` var (iki şirketi bağlayan tek müdür →
  MUVAZAA / tüzel kişilik perdesinin aralanması sinyali; muvazaa çerçevesi
  TBK m.19 — Mevzuat MCP teyit 2026-09-06); **`yapisal`** = aksi hâlde nötr
  yapısal köprü (perde etiketi DEĞİL — sahte muvazaa sinyali üretilmez).
  `tip: karar | mahkeme` düğümleri hesaptan muaf. JSON
  `kopru_dugumler: [{id, ad, etiket}]`.
- **Çevrim (exit 3)** — dairesel illiyet (mantık hatası). v0.5.16: çevrimler
  MİNİMAL (çevrim-dışı düğüm içermez: A→B→C→B → `[B, C, B]`) ve mükerrersiz;
  ≤200 düğümde tam basit çevrim sayımı, üstünde örneklem (rapor bunu söyler).
  Çevrim varken §7 yük taşıyan kenar "çevrimde anlamsız", §8 köksüz graf
  "GÜVENİLMEZ" damgası taşır (sahte-yeşil kapanışı).
- **Kesme adayları** — `kesme_flag` dolu illiyet kenarları (→ oa-antitez beslemesi);
  dal önekli flag + `ceza:magdur_kusuru` / `miras:paylastirma_kasti` için sabit doktrin
  hatırlatması (hüküm değil); yön `curut` ise "kesme savunmasını KUR"
- **Yük taşıyan kenar** — çıkarılırsa illiyet zincirini koparan kritik bağ (→ oa-strateji);
  yön `kur` → "bu bağı sağlamlaştır", yön `curut` → "karşı tarafın bu bağını ÇÜRÜT"
- **Kanun yolu zinciri (§9 — v0.5.16)** — `kanun_yolu` kenarlarının kat sırası + sonuçları
  (JSON `kanun_yolu_zinciri`); illiyet hesaplarına girmez, çevrim sayılmaz
- **Zincir güven analizi** — VARSAYILAN (v0.5.8.4): uçtan uca her illiyet
  zinciri için `confidence_decay` + **en zayıf halka** (advisory —
  oa-antitez/oa-strateji beslemesi). 372 sahasında `--zincir` bayrağı 0 kez
  verildiği için analiz hiç üretilmemişti (opsiyonel kapı = ateşlemeyen kapı);
  artık bayraksız koşar. Bilinçli kapatmak için `--zincirsiz`; eski `--zincir`
  geriye-uyum no-op'tur.

### 3. Raporu hukuki sonuca bağla (model)

Script çıktısını yorumla: hangi boşluk müvekkil-aleyhine, hangi köprü düğüm karşı
tarafın vuracağı yer, hangi kesme savunması ciddi. Boşlukları açıkça müvekkile
bildir (anayasa: zaafları rahatsız edici olsa da söyle).

### 4. "İlliyet / Bağ Haritası" bloğunu üret

Her esaslı çıktıya `references/cikti-blogu.md`'deki standart bloğu ekle (taraflar+rol,
ilişki kenarları, illiyet kenarları, boşluk denetimi, oa-antitez beslemesi).

## ZAMAN KATMANI — kronoloji + süre pencere bindirme (M5, Paket D — v0.5.5)

İlliyet grafının her düğümü/kenarı zaman içinde bir yere oturur; bu **ZAMAN
KATMANI** grafa `references/cikti-blogu.md`'deki **tarih | olay | kaynak-evrak |
sha** dört sütunlu bir tabloyla eklenir — her satır bir düğüm/kenarın hangi
evraktan (`_oa/metin/<evrak>`) ve hangi sha16 imzayla geldiğini gösterir
(kayıpsızlık: iddia hafızadan değil, izlenebilir bir evraktan gelir). Bu tablo
`oa-vakia`'nın kronolojisiyle (`vakia_matris.py`) AYNI olguları taşır — ikinci
bir kronoloji İCAT EDİLMEZ, yalnız illiyet açısından etiketlenir (sebep/sonuç/
tetikleyici).

**Süre pencere bindirme:** zaman katmanındaki tetikleyici olaylardan (tebliğ,
öğrenme, muacceliyet) birden fazla süre doğuyorsa (ör. cevap süresi + karşı
tarafın istinaf süresi aynı dönemde işliyor), her biri `oa-sure/scripts/
hesapla_sure.py` ile AYRI hesaplanır; birden fazla süre varsa hepsi tek bir
JSON'a (`{ad, teblig, kural|sure+birim}` listesi) toplanıp `hesapla_sure.py
--pencereler <json>` ile **PENCERE BİNDİRME** (üst üste binen süre aralıkları)
deterministik olarak taranır — script yalnız tarih aritmetiğiyle çakışmayı
gösterir, hangi sürenin önceliklendirileceği avukat muhakemesidir.

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
Tam günlük `references/degisiklik-gunlugu.md`'dedir (bağlam ekonomisi için ayrıldı — içerik aynen korunur; yeni kayıtlar oraya işlenir). Güncel sürüm: **v3.26**.

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

---
name: oa-kiyas
description: >
  Ortak Avukat sisteminin AÇIK KIYAS / HUKUKİ SİLOJİZM parçası. Türk hukukunda her
  hukuki sonucu örtük sezgiyle değil, denetlenebilir üçlü yapıyla üret: BÜYÜK ÖNERME
  (uygulanacak norm + onu somutlaştıran içtihat) → KÜÇÜK ÖNERME (somut maddi vakıa /
  illiyet grafı) → SONUÇ (tatbik + olasılık). Bu, Türk hukukundaki subsumtion/tatbik
  mantığının ta kendisidir. Norm unsurları ile vakıa arasında eşleşme denetimi yap;
  eşleşmeyen unsuru ispat/hukuk boşluğu olarak işaretle. "Bu olaya hangi madde nasıl
  uygulanır", "hukuki dayanak nedir", "neden bu sonuç", "tatbik et", "unsurlar oluşmuş
  mu", "subsumtion" türü her işte — kullanıcı açıkça istemese bile bir argüman ya da
  dilekçe gerekçesi kurulurken — tetikle.
---

# oa-kiyas — Açık Kıyas / Hukuki Silojizm

Hukuki muhakemeyi örtük ve yapısız olmaktan çıkarıp **denetlenebilir üçlü yapıya**
oturtur. Türk hukukunun subsumtion (tatbik) mantığı zaten budur: norm → maddi vakıa
→ hukuki sonuç. Bu parça o yapıyı zorunlu kılar; böylece her sonuç hâkim ve karşı
taraf tarafından adım adım denetlenebilir, gizli sıçramalar görünür olur.

> **VECİZE (P1-11 doktrin senkronu):** Künyeyi bulmak yetmez; kararın müvekkilin işine yarayıp yaramadığının muhakemesi güç çarpanıdır — çıplak künye sıfırdır, damgalı ve davaya bağlı karar çarpandır.

## Neden zorunlu üçlü yapı

Bir hukuki sonuç "şu sebeple şöyle olur" diye tek hamlede verilirse, hangi normun
hangi vakıaya nasıl bağlandığı görünmez; halüsinasyon ve mantık sıçraması burada
saklanır. Üçlü yapı her halkayı açığa çıkarır:

1. **Büyük önerme (norm + içtihat):** Uygulanacak kural. Madde metni + onu
   somutlaştıran Yargıtay/Danıştay/AYM içtihadı. **Yalnızca resmî kaynaktan teyitli**
   (oa-ictihat → Mevzuat/Yargı Pro). Hafızadan norm/künye üretme.
2. **Küçük önerme (vakıa):** Somut maddi olay. Düz olgu listesi değil; varsa
   **oa-illiyet grafı** (fiil→netice illiyet zinciri, taraf bağları). Her olgu delile
   bağlı (oa-vakia).
3. **Sonuç (tatbik):** Norm küçük önermeye uygulanınca çıkan hukuki sonuç + olasılık.

## İş bölümü: model kurar, script denetler, model yorumlar

- **Modelin işi (muhakeme):** üç önermeyi kurmak; normun anlamını yorumlamak;
  hangi içtihadın somutlaştırdığına karar vermek.
- **Scriptin işi (garantör):** yapısal eksiklik — üç bileşen dolu mu, normun her
  unsuru bir vakıaya eşlenmiş mi, eşleşmeyen unsur var mı. `scripts/kiyas_denetim.py`.
- **Yine modelin işi (yorum):** boşlukları hukuki sonuca bağlamak (eksik unsur =
  ispat boşluğu mu, hukuki dayanak yetersizliği mi).

Sahte kesinlikten kaçın: script "unsur oluşmuştur" demez; sadece "bu unsura karşılık
vakıa eşlenmemiş" der. Unsurun gerçekten oluşup oluşmadığı muhakemedir.

## Akış

### 1. Büyük önermeyi kur (norm + içtihat)
Uygulanacak normu belirle. Normu **unsurlarına ayır** (örn. haksız fiil TBK m.49:
fiil + hukuka aykırılık + kusur + zarar + illiyet bağı). Her unsuru ayrı yaz. Normu
somutlaştıran içtihadı oa-ictihat ile teyitli ekle. Emin değilsen MCP'den doğrula.

### 2. Küçük önermeyi kur (vakıa / illiyet grafı)
Somut olayı, normun unsurlarıyla eşleşecek biçimde yaz. Varsa oa-illiyet grafından
besle (illiyet bağı unsuru zaten orada modellenmiştir). Her olguyu delile bağla.

### 3. Eşleştir ve denetle
Kıyası JSON yaz (`_oa/cikti/05-kiyas.json`, şema `references/kiyas-rehberi.md`) ve çalıştır:
```bash
python scripts/kiyas_denetim.py _oa/cikti/05-kiyas.json
```
Script raporlar: eksik bileşen, vakıaya eşlenmemiş norm unsuru (= boşluk),
delile bağlanmamış küçük önerme, içtihatsız büyük önerme.

### 4. Sonucu kur ve yorumla
Tatbiki yaz: her unsur karşılandı mı, karşılanmayan varsa sonuç ne (talep reddine mi
yol açar, ek ispat mı gerekir). Boşlukları açıkça bildir (anayasa: zaafı söyle).

## İçtihat muhakemesi (MUHAKEME adımı) — DAMGA + illiyet + ilgili kısım
Büyük önermenin içtihat bileşeni (`buyuk_onerme.ictihat`) tek başına yeterli
değildir: her içtihat için ayrı bir **muhakeme kaydı** üretilmeden o karar
"muhakeme edilmiş" sayılmaz (İçtihat Muhakeme Zinciri, şema:
`references/ictihat-muhakeme-sablonu.md`). **Doktrin (P1-11 — bağlayıcı):
ölçüt dosya sayısı DEĞİL, kaydın varlığıdır — "bir karar = bir MUHAKEME KAYDI"**
— kayıt iki eşdeğer FORM'da var olabilir:

- **STANDART YOL (çoğunluk hâli — tek komut):** `oa_hafiza.py teyit --damga
  ... --bag ... --ilgili-kisim ... --dokum-icerik ...` — bu TEK çağrı hem
  döküm dosyasını hem `_oa/cikti/03-ictihat-muhakeme.md`'ye bölüm-append
  muhakeme kaydını KENDİSİ yazar (bkz. aşağıdaki tek-blok örnek). 1-5
  içtihat/rutin atıf için budur; ayrı bir dosya AÇILMAZ.
- **DERİN YOL (kilit kararlar):** uzun kıyas/ayırt-etme gerektiren, birden
  fazla unsuru birden karşılaştıran kilit bir karar için AYRI bir
  `_oa/cikti/NN-ictihat-muhakeme.md` dosyası açılır — alan şeması AYNIDIR
  (KUNYE/KAYNAK-IZI/İLGİLİ-KISIM/DAVAYA-BAĞ/DAMGA/AYIRT-ETME), yalnız
  gerekçe/ayırt-etme metni tek-komutun `--bag`/`--ayirt` alanlarına
  sığmayacak kadar uzundur.

**Hangi durumda dosya açılır:** derin yol yalnız (a) birden fazla emsalin
ÇAPRAZ kıyaslandığı, (b) ayırt-etmenin çok-paragraflı gerekçe gerektirdiği,
veya (c) aynı künyeye ait çelişen damga adaylarının tartışıldığı durumlarda
tercih edilir; aksi hâlde standart (tek-komut) yol RESMÎ ve yeterli yoldur.

**Standart yol — tek-blok örnek (anonim sorgu):**
```bash
# 1) MCP: ictihat_getir ile tam metni çek — 2) tek komut kütük+döküm+muhakeme yazar:
python oa-pipeline/scripts/oa_hafiza.py teyit --arac ictihat_getir --sorgu "4. HD haksız fiil zamanaşımı" --sonuc "Yargıtay 4. HD, E. .../K. ..." --damga LEHE --dokum-sinifi tam-metin --bag "...(≥40 kr, hangi unsuru somutlaştırıyor)..." --ilgili-kisim "...(döküm içinde VERBATİM geçen alıntı)..." --dokum-icerik @ham.md
```
Bu tek komut kütük satırını, döküm dosyasını (provenans notlu) VE
`03-ictihat-muhakeme.md`'ye bölüm-append muhakeme kaydını AYNI ANDA üretir —
alan eşleme sözlüğü: kütük `DAMGA=`↔bölüm `**DAMGA:**`, `--bag`↔`##
DAVAYA-BAĞ`, `--ilgili-kisim`↔`## İLGİLİ-KISIM`, döküm yolu↔`**KAYNAK-IZI:**`.

Adım adım (her iki YOL için de geçerli alanlar):
1. **KUNYE** ve **KAYNAK-IZI**'nı `oa-ictihat`'tan devral.
2. **İLGİLİ-KISIM**'ı KAYNAK-IZI dosyasından aynen çıkar (davayla ilgili
   gerekçe pasajı — tüm karar değil).
3. **DAVAYA-BAĞ**'ı yaz (R4 — eski adı "İLLİYET"; `oa-illiyet`'in nedensellik
   grafıyla karışmasın diye analoji/emsal-uygunluk bağı bu adı taşır): bu
   karar büyük önermenin hangi unsurunu somutlaştırıyor, küçük önermenin
   (vakıa) hangi olgusuyla eşleşiyor.
4. **DAMGA**'yı ata — kapalı enum, dört değer: `LEHE` \| `ALEYHE` \|
   `ALEYHE-AYIRT` \| `NOTR`. `ALEYHE-AYIRT` ise **AYIRT-ETME** alanı zorunlu
   (kararın somut olaya neden uymadığı — bu meşru bir savunma tekniğidir,
   m.6 ihlali değildir). Damga atanmazsa kayıt `NOTR` sayılır (fail-closed:
   "muhakeme edilmemiş", kullanılamaz).
5. Kaydı standart yolda `teyit --damga` KENDİSİ, derin yolda avukat/model
   `_oa/cikti/NN-ictihat-muhakeme.md` olarak yazar (bir karar = bir MUHAKEME
   KAYDI — dosya sayısı değil kaydın varlığı ölçüttür).

**Kritik doktrin (bağlayıcı):** dış çıktı (dilekçe) daima müvekkil LEHİNEdir
— yalnız `LEHE`/`ALEYHE-AYIRT` damgalı kayıtlar dilekçeye girer. `ALEYHE`
(ayırt edilmemiş) içtihat dilekçeye **girmez**, ama iç analizde (bu kayıt +
`oa-antitez` cephaneliği) işlenmesi **ZORUNLUdur** — saklanmaz, dahili
tutulur. Yargıtay/BAM atfı olmayan esaslı bir dilekçe muhakemesi **zayıf**
sayılır.

**TESLİM tanımı tekildir (P1-11):** bu parçanın ürettiği muhakeme kayıtları
(standart veya derin yol) `oa-kontrol/scripts/ictihat_muhakeme_denetim.py`
tarafından TESLİM aşamasında (`teslim_paketi.py` → `_oa/defter/teslim-makbuz.json`)
yeniden denetlenir; kayıt eksik/çıplak kalırsa makbuz kapısı kapanmaz —
muhakeme burada kurulur, geçerliliği orada mühürlenir.

## Diğer parçalara entegrasyon
- **oa-ictihat** → büyük önermenin teyitli norm+künyesini sağlar.
- **oa-illiyet** → küçük önerme = illiyet grafı (illiyet bağı unsuru oradan gelir).
- **oa-vakia** → küçük önermenin delil bağını sağlar.
- **oa-antitez** → karşı taraf hangi unsurun oluşmadığını iddia eder; kıyas zaafı.
- **oa-dilekce** → dilekçe gerekçesi = açık kıyas (norm→vakıa→sonuç dizilimi).

## Anayasal süzgeç
Üretilen kıyas **karar materyalidir, karar değildir**. Normun yorumu ve nihai sonuç
Av. Bayram Can Çapar'a aittir. Büyük önermenin norm/künyesi yalnız resmî kaynaktan
teyitlidir. Script yapısal boşluğu gösterir; unsurun hukuken oluşup oluşmadığı yargıdır.

## Anayasal düstur — usul esasa üstündür
Usulün esasa takaddümü ailenin anayasal düsturudur: usulden düşen dosya esasa hiç giremez; süre, usul hukukunun parçası ve telafisiz tek hatadır. Usul normları da kıyasa konu olur: dosyada usul meselesi varsa **usule ilişkin kıyas** (büyük önerme = süre/görev normu + usul içtihadı; küçük önerme = tarihli işlem vakıası) **esasa ilişkin kıyastan önce** kurulur — sonuç 'usulden' ise esas kıyası maliyeti düşer.

## Anayasal bloklar — tek kaynak (anayasa.md)
Bu parça, ailenin ortak anayasal ilkelerine tabidir — **Çaba/token standardı** (model/efor kullanıcının tercihi; muhakemede/doğrulamada/çıktı kalitesinde tasarruf YOK, yalnız mekanik katmanda kayıpsız verimlilik), **Örnekleme ilkesi** (konu sınırlaması yok — kapsam TÜM Türk hukuku), **Doğaçlama meşruiyeti** (yöntem serbest, olgu MCP-teyitli), ayrıca Doğrulama mimarisi, Anonimleştirme ve Layer 0 gizlilik. **Tek ve yetkili kaynak: `ortak-avukat/references/anayasa.md`.** (Bu parça alt-ajan olarak koşarken bu ilkeler `oa-pipeline/scripts/oa_hafiza.py ajan-brif` ile taşınır.)

## Başbakan denetimi (anayasal)
Bu parça, ailenin Başbakanı `oa-pipeline`'ın icra+denetimine tabidir: çağrıldığında disiplini İSTİSNASIZ ve tam işletilir (ama/fakat/token-tasarrufu gerekçesiyle kestirme YASAK). Görev savsaklanmaz; gerçekten yapılamayan bir şey varsa dürüstçe belirtilir ("yaptım" denmez) ve alternatif yöntem üretilir. Önemli olan proses ve çıktı kalitesidir.

## Fiziksel aktivasyon — simülasyon yasağı (anayasal)
Bu parça yalnızca ÜÇ kanıttan en az biriyle "çalıştı" sayılır: (1) Skill aracıyla FİİLEN çağrıldı ve bu gövde bağlama yüklendi (kullanıcının `/oa-kiyas` komutuyla eşdeğer); (2) scripti gerçekten koştu ve çıktısı görünür; (3) gerektirdiği MCP çağrısı fiilen yapıldı (araç + sorgu + sonuç kaydıyla). Kısa description her zaman bağlamda durur — o VİTRİNDİR, disiplin değildir; gerçek disiplin bu gövdededir. Bu yüzden hiçbir parça bu parçayı description'ından TAKLİT EDEMEZ; bu parça da başka bir parçanın işine ihtiyaç duyduğunda onu Skill aracıyla fiilen çağırır (olmuyorsa SKILL.md'sini Read ile yükler; o da olmuyorsa "FİZİKEN YÜKLENEMEDİ" diye açıkça yazar). Yapılmamış çağrı 'yapılmış', koşmamış script 'koşmuş' gösterilemez — bu, halüsinasyonun ta kendisidir. Devir alırken/verirken kısa DEVİR PAKETİ (ne yapıldı → ne bekleniyor → hangi kanıt) kullanılır ve pipeline defterine (`oa-pipeline/scripts/pipeline_kayit.py`) işlenir. Bu parçanın ürettiği her kalıcı çıktı (JSON/rapor/devir paketi) çalışılan klasörün `_oa/` yerel hafıza kökünde yaşar (yapı: `oa-pipeline` → Çalışma Kökü).

## Değişiklik Günlüğü
Tam günlük `references/degisiklik-gunlugu.md`'dedir (bağlam ekonomisi için ayrıldı — içerik aynen korunur; yeni kayıtlar oraya işlenir). Güncel sürüm: **v3.26**.

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

## v0.5.8.5 — A1 TRİYAJ (MUHAKEME adımının tam-okuma şartı)

> **ÇEKİRDEK (kullanıcı direktifi — aynen):** "Müvekkil aleyhine HİÇBİR yargı
> kararı dilekçeye giremez. MCP'den çekilen TÜM kararlar İSTİSNASIZ baştan
> sona (TAM METİN) okunur. LEHE ise dilekçeye; ALEYHE ise CEPHANELİĞE
> (strateji/farkındalık); NÖTR kütükte kalır."

- **DAMGA, tam metin okunmadan VURULMAZ.** RATIO çıkarımı yalnız KAYNAK-IZI
  dökümündeki TAM METİNDEN yapılır; **arama sonucu parçasından alıntı
  YASAKTIR** — snippet'ten RATIO kurmak muhakeme değil iddiadır.
- **Tek-komut ritüeli okuma sınıfını taşır:** karar baştan sona okunduysa
  `--dokum-sinifi tam-metin` ver; verilmezse döküm dürüst `ilgili-kisim`
  sınıfıyla işlenir ve [G6] triyaj kapısı o künyeyi dilekçede BLOKLAR.
  Karşı tarafın fiilen ileri sürdüğü aleyhe karar `--duyulmus` ile
  işaretlenir (ALEYHE-AYIRT'ın dilekçeye çıkabilmesinin kütük şartı).
- **Triyaj sonucu üç adrese dağılır:** LEHE → dilekçe adayı (`oa-dilekce`);
  ALEYHE → cephanelik (`oa-antitez` — strateji/farkındalık; kütükte bırakmak
  yetmez); NOTR → kütükte kalır, hiçbir çıktıya girmez. [G6] bunu mekanik
  denetler: NOTR artık BLOK'tur (eskiden uyarıydı); ALEYHE-AYIRT yalnız
  duyulmuş + ayırt bağlamı dar istisnasıyla geçer.
- Alan biçimleri ve örnek kayıt: `references/ictihat-muhakeme-sablonu.md`
  → "DÖKÜM-SINIFI ve DUYULMUŞ" bölümü.

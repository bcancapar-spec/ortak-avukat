# İdari dava, YD talebi, ceza istinafı ve Y-06 kapı sıkılaştırması (v0.5.18 aday)

> **Neden var.** 3 Ekim 2026 yetenek denetiminin Y-06 bulgusu dilekçe
> kapısında (`scripts/dilekce_denetim.py`) dört açık saydı: dava değeri ayrı
> unsur değildi; bileşik unsurlarda (ör. "taraf + kimlik", "ihlal edilen hak +
> Anayasa maddesi") tek bir desen unsuru "var" saydırıyordu; idari dava ve ceza
> istinafı için tip yoktu. Bu not, kapattığımız açıkları ve dürüst sınırlarını
> anlatır. Yürütmenin durdurulması talebinin fikri Yargı PRO 4-4'ten, hukuk
> kanun yolu sıkılaştırmasının fikri 2-6'dan alındı (yalnız fikir; metin ve kod
> alınmadı). Bütün madde metinleri **Yargı PRO MCP `mevzuat_getir` ile
> 2026-10-05'te mevzuat.gov.tr'den okundu.**

## 1. Bileşik unsur — "her parça ayrı ayrı" (Y-06)

Kapı artık iki tür unsur tanır:

- **Tekil unsur:** desenlerden biri geçerse unsur vardır (eski davranış).
- **Bileşik unsur:** unsur birden çok parçadan oluşur; **her parça ayrı ayrı**
  karşılanmalıdır. Bir parça eksikse rapor yalnız o parçayı adıyla söyler
  (ör. "… — eksik parça: Anayasa maddesi").
- **Yakınlık parçası:** adres gibi taraf başına aranan bilgiler, taraf
  etiketinin ardından belirli bir pencerede aranır; alacaklının adresi borçlunun
  adres eksiğini örtmez. Tebliğ/bildirim/öğrenme tarihi de olayın **yanında**
  aranır (olaydan sonra 80, önce 100 karakter): belgenin sonundaki imza
  tarihi tebliğ tarihini örtmez (Fable 5.1 salt okunur incelemesi,
  2026-10-05). "Tebliğ edilmemiştir/edilmeden" beyanı tarih unsurunu kaldırır —
  tebliğden önce başvurmak müvekkilin hakkıdır; yalnız olumsuz çekim istisna
  sayılır ("tebliğ edilmesi" sayılmaz).
- **Koşullu unsur:** yalnız belirli bir koşul metinde varsa zorunludur (ör.
  kısmi itiraz varsa cihet ve miktar; ticari uyuşmazlıkta arabuluculuk).

Sıkılaştırılan mevcut tipler (yeni test yazılmadan önce mevcut testlerin hiçbiri
bu tiplerde ilgili alanı kilitlemiyordu; ayrıntı değişiklik günlüğünde):

- **istinaf** — "Kararın başvurana tebliğ edildiği tarih" artık ayrı aranır
  ve tarih tebliğ olayının yanında olmalıdır (HMK m.342/2-ç); eskiden "süre"
  ya da "iki hafta" kelimesi tek başına bu unsuru karşılıyordu. Kararın
  mahkemesi ile sayısı birlikte aranır (m.342/2-c); tarih ve imza birlikte
  aranır (m.342/2-g). m.342/2-c kararın **tarihini** de ister; eski tipte kilit
  testleri bozmamak için karar tarihi yokluğu [A] altında istişari uyarıdır.
  Not: m.342/3'e göre dilekçe, başvuranın kimliği ve imzasıyla kararı yeteri
  kadar belli ediyorsa diğer hususlar bulunmasa bile reddolunmaz — kapının
  sıkılığı OA kalite standardıdır, ret ölçütü değildir.
- **temyiz** — "İlamın tebliğ edildiği tarih" ayrı aranır (HMK m.364/2-d);
  tarih ve imza birlikte (m.364/2-ğ).
- **aym_bireysel** — "ihlal edilen hak" ile "dayanılan Anayasa hükümleri"
  ayrı parçalardır (6216 m.47/3); başvurucunun kimlik **ve adres** bilgisi
  birlikte aranır; ekler (işlem/karar örneği + harç belgesi ya da adli yardım)
  eklendi (m.47/3 son cümle); avukatla temsilde vekâletname (m.47/4).

**Dürüst sınır — eski `dava` tipi:** HMK m.119/1-d dava değerini malvarlığı
davalarında zorunlu içerik sayar; m.119/2 ise (d) bendini bir haftalık kesin
süre yaptırımının dışında tutar (eksikliği "dava açılmamış sayılır" sonucuna
bağlanmaz). Eski `dava` tipinde dava değeri **bloklayıcı yapılmadı**: mevcut
test süitinde değer satırı olmayan, para talepli taslağın temiz geçmesini
bekleyen bir kilit var (`tests/test_v0516_C1.py`, [P] CLI testi) ve o dosya bu
paketin alanı dışında. Bunun yerine `dava` tipinde değer yoksa [A] altında
**görünür bir uyarı** basılır; yeni malvarlığı tiplerinde (itirazın iptali,
menfi tespit, istihkak davası) dava değeri baştan **zorunlu unsurdur**.
Aynı gerekçeyle eski `dava`/`genel` tipindeki "Taraf + kimlik (TC/adres)"
unsuru bloklayıcı biçimde sıkılaştırılmadı (adressiz sentetik taslaklarla temiz
geçiş bekleyen mevcut testler var); taraf var ama adres ya da TCKN yoksa
`dava` tipinde uyarı basılır (HMK m.119/1-b, c; eksiklikte bir haftalık kesin
süre, tamamlanmazsa dava açılmamış sayılır — m.119/2). Bu iki kalemin
bloklayıcıya çevrilmesi avukat ve ana ajan kararıdır (fixture güncellemesiyle
birlikte).

## 2. idari-dava (İYUK m.3)

- **Merci:** Danıştay, idare mahkemesi ya da vergi mahkemesi başkanlığına
  hitaben yazılmış **imzalı** dilekçe (m.3/1).
- **Zorunlu unsurlar (m.3/2):** tarafların ve varsa vekil/temsilcilerin ad,
  soyad/unvan ve adresleri ile gerçek kişilerin TCKN'si (a); davanın konusu,
  sebepleri ve dayanılan deliller (b); dava konusu idari işlemin **yazılı
  bildirim tarihi** (c — kapı tarihi bildirim/tebliğ/öğrenme olayının yanında
  arar; zımni retde yazılı bildirim olmadığından başvuru tarihi de bu unsuru
  karşılar: otuz gün içinde cevap verilmezse istek reddedilmiş sayılır,
  İYUK m.10/2); mali yükümlerde ve tam yargı davalarında
  **uyuşmazlık konusu miktar** (d); vergi davalarında verginin ya da cezanın
  nevi ve yılı, ihbarnamenin tarihi ve numarası (e). Dava konusu kararın ve
  belgelerin asılları ya da örnekleri eklenir (m.3/3).
- **YD istenmişse:** iki koşul ayrı ayrı kurulmalıdır (aşağıda §3); kapı
  idari dava dilekçesinde "yürütmenin durdurulması" görürse iki koşulu da
  arar.
- **Süre bağlantısı:** dava açma süresi İYUK m.7 (`oa-sure` kuralları
  `iyuk_dava_idare` — 60 gün, `iyuk_dava_vergi` — 30 gün; ivedi ve sınav
  davalarının özel süreleri ayrıca tanımlı). Başvuru/zımni ret yolları (m.10,
  m.11) `oa-sure` ve `oa-usul` kapsamındadır.

## 3. yd-talebi (İYUK m.27)

- **İki koşul birlikte:** idari işlemin uygulanması hâlinde **telafisi güç
  veya imkânsız zarar** doğması ve işlemin **açıkça hukuka aykırı** olması
  (m.27/2). Kapı iki koşulu ayrı unsur olarak arar; soyut "zarar doğar" cümlesi
  ispat değildir, zarar somut belgeye bağlanır (bu bir yazım ilkesidir; kapı
  yalnız varlığı söyler).
- **Uygulanmakla etkisi tükenecek işlem:** savunma alınmadan da YD verilebilir;
  ancak kamu görevlilerinin atama, naklen atama, görev ve unvan değişikliği ile
  görevlendirme işlemleri bu sayılmaz (m.27/2).
- **Teminat:** YD teminat karşılığı verilir; durumun gereklerine göre teminat
  aranmayabilir, idareden ve adli yardımdan yararlanandan alınmaz (m.27/6) —
  kapı "teminat" konusunu görmezse teminatsız YD istemini hatırlatır.
- **İkinci istem yasağı:** aynı sebeplere dayanılarak ikinci kez YD istenemez
  (m.27/10) — önceki istem anılıyorsa kapı farklı sebebin açıkça yazılmasını
  hatırlatır.
- **YD kararına itiraz:** kararın tebliğini izleyen günden yedi gün, bir
  defaya mahsus; itiraz üzerine verilen karar kesindir (m.27/7). İtiraz
  dilekçesinde kapı kararın **tebliğ tarihini** arar (süre ifadesini değil).
  Mevcut `oa-sure` kuralı: `iyuk_yd_itiraz` (ivedi ve sınav davalarındaki
  itiraz kapalılığı o kuralın notundadır).
- Vergi davalarında dava, dava konusu kısmın tahsilini kendiliğinden durdurur;
  istisnalar m.27/4'tedir — gereksiz YD talebi yazılmaz.

## 4. ceza-istinaf (CMK m.273)

- **Merci:** istinaf istemi **hükmü veren mahkemeye** dilekçe verilerek ya da
  zabıt kâtibine beyanla yapılır (m.273/1); dilekçe başlığı hükmü veren ceza
  mahkemesine hitap eder ve bölge adliye mahkemesine gönderilmesini ister.
- **Süre:** hükmün **gerekçesiyle birlikte tebliğinden** itibaren iki hafta
  (m.273/1; 7499 sayılı Kanunla eski "hazır bulunmayanlar" fıkrası mülga).
  Mevcut `oa-sure` kuralı: `cmk_istinaf`. Tefhim tarihi süre başlangıcı
  değildir.
- **Zorunlu unsurlar (kapı):** hükmü veren mahkeme ve bölge adliye
  mahkemesi; hükmün künyesi (esas/karar no ve hüküm); başvuranın sıfatı
  (sanık/müdafi, katılan/vekili, suçtan zarar gören); gerekçeli hükmün tebliğ
  tarihi (tebliğ olayının yanında; gerekçeli hüküm henüz tebliğ edilmeden
  verilen süre tutum dilekçesinde "tebliğ edilmemiştir" beyanı tarih parçasını
  kaldırır); istinaf sebepleri; talep (hükmün kaldırılması, beraat, yeniden
  hüküm); tarih ve imza. Kanun yolu tipi olduğu için `kanun-yolu-mimari-playbook`
  yapısal kalemleri (GİRİŞ, numaralı SONUÇ, tebliğ tarihinin ayrı satırı …)
  de istişari olarak denetlenir.
- **Hukuki not:** sanık ve katılanın başvuru nedenlerini göstermemesi
  incelemeye engel değildir (m.273/4) — kapının "istinaf sebepleri" unsuru bu
  yüzden **yasal değil OA standardıdır**: sebepli istinaf, bölge adliye
  incelemesini müvekkilin lehine yönlendirir. Temyizde ise bozma nedenini
  göstermek zorunludur ve temyiz sebebi yalnız hukukî yöne ilişkin olabilir
  (CMK m.294/1-2) — ceza temyizi için mevcut `temyiz` tipi kullanılır.
- **Müvekkil-aleyhi eksen:** `--taraf sanik` (suç ikrarı), `--taraf katilan`
  ya da `musteki` (şikâyetten vazgeçme/uzlaşma).

## 5. Okunan resmî metinler (Yargı PRO MCP, 2026-10-05)

HMK (mevzuatgov:kanun:5:6100) m.119, m.342, m.364 · İYUK
(mevzuatgov:kanun:5:2577) m.3, m.10, m.27 · CMK (mevzuatgov:kanun:5:5271) m.273,
m.291, m.294 · 6216 (mevzuatgov:kanun:5:6216) m.47 · Tebligat K.
(mevzuatgov:kanun:3:7201) m.32.

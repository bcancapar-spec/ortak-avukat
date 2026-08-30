# Unsur Şablonu — İtirazın İptali Davası (İİK m.67-68)

Norm çıpası: 2004 sayılı İcra ve İflas Kanunu m.67 (itirazın iptali/genel
mahkemede dava), m.68-68/a (belgeye dayalı takiplerde imzaya itiraz/itirazın
kesin kaldırılması ile ayrımı). **Kullanım anında** güncel metin + ilamsız
takip usulü + kötüniyet tazminatı oranı (m.67/2) `oa-ictihat`/Mevzuat MCP'den
teyit edilir; itirazın iptali mi yoksa itirazın kaldırılması (İİK m.68/68a,
icra mahkemesi) mi işletileceği ayrımı `oa-alan`da (görev/yetki) yapılır.

**İKİ TAZMİNAT AYRIDIR (A-16, v0.5.14).** m.67/2 tek cümlede **iki ayrı**
yaptırım kurar ve ikisi de **"diğer tarafın talebi üzerine"** hükmolunur:
(1) **icra inkâr tazminatı** — borçlunun *itirazının* haksızlığı hâlinde
**borçlu** aleyhine; (2) **kötüniyet tazminatı** — *takibin* haksız ve kötü
niyetli görülmesi hâlinde **alacaklı** aleyhine. m.67 son fıkrası ikisini adıyla
ayrı ayrı sayar. Oran **asgaridir**, sabit değil; rakamı buraya yazma —
kullanım anında Mevzuat MCP'den çek. İtiraz eden veli/vasi/mirasçı ise
borçlu aleyhine tazminat **kötü niyetin sübutuna bağlıdır** (m.67/3).

| Unsur (id önerisi) | Norm çıpası | Delil türü | İspat yükü |
|---|---|---|---|
| U1 — Geçerli bir ilamsız icra takibinin varlığı ve ödeme emrinin tebliği | İİK m.58-60 | İcra takip dosyası, tebligat evrakı | Davacı (alacaklı) |
| U2 — Borçlunun süresinde (7 gün) itiraz etmiş ve takibin durmuş olması | İİK m.62 | İtiraz dilekçesi, icra dosyası durdurma şerhi | Davacı (itirazın süresinde/usulüne uygun yapıldığını çürütmek isterse davacı, aksi hâlde bu davanın ön koşulu) |
| U3 — Alacağın maddi hukuk bakımından varlığı ve muaccel olması (asıl borç ilişkisinin ispatı) | Genel borçlar hukuku (TBK) + somut ilişkinin dayanağı norm (kullanım anında teyitli) | Sözleşme, fatura, ihtarname, cari hesap ekstresi, tanık/bilirkişi | Davacı (alacaklı) |
| U4 — Davanın itirazın tebliğinden itibaren 1 yıllık süre içinde açılması (aksi hâlde genel mahkemede alacak davası açma hakkı saklı kalır) | İİK m.67/1 | İtiraz tebliğ/öğrenme tarihi ile dava tarihi karşılaştırması | Mahkemece resen + davalı def'i |
| U5 — Borçlunun itirazının HAKSIZ olduğu (itiraz sebeplerinin çürütülmesi — zamanaşımı, ödeme, takas def'i gibi) | Somut itiraz sebebine göre değişir (TBK zamanaşımı/ifa/takas hükümleri — kullanım anında teyitli) | İtiraz dilekçesindeki sebepler + bunları çürüten delil | Davacı (itirazı çürütme yükü davacıdadır) |
| U6 (sonuç aşaması — MÜVEKKİL ALACAKLIYSA LEHE TALEP) — Borçlunun **itirazının haksızlığına** karar verilirse **borçlu** aleyhine **icra inkâr tazminatı**; hükmolunması **bizim açık talebimize** bağlıdır ve oran **asgaridir** (kanunda yazılı asgari oranın altına inilemez) | İİK m.67/2 | Takip talebi/dava talebi (m.67 son fıkra: tazminat tespitinde **talep** esas alınır) + mahkeme kararıyla birlikte hesap | Talebi eden: alacaklı (müvekkil). Talep edilmezse mahkeme **kendiliğinden hükmetmez** → asgari oran masada kalır |
| U7 (sonuç aşaması — MÜVEKKİL ALACAKLIYSA ALEYHE RİSK) — **Takibin** haksız ve kötü niyetli görülmesi hâlinde **alacaklı** aleyhine **kötüniyet tazminatı** (m.67/2'nin ikinci yaptırımı — icra inkâr tazminatıyla AYNI KURUM DEĞİLDİR; m.67 son fıkrası ikisini ayrı ayrı sayar) | İİK m.67/2 | Takibin dayanağı belge, ihtar/muacceliyet zinciri, karşı tarafın talebi | Talebi eden: borçlu (karşı taraf). Bizim işimiz bu riski **önden ölçmek** (`oa-antitez`) |

**Antitez çapası (M3 köprüsü):** karşı tarafın (borçlu) en olası savunması
U3'ün (alacağın esası) veya U5'teki karşı def'ilerin (zamanaşımı, ifa, takas)
öne sürülmesidir — `oa-antitez` matrisinde "defi_karsi_talep" ve "zamanasimi"
cepheleri bu unsurlarla doğrudan eşlenir.

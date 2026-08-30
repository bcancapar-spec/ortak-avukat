# Unsur Şablonu — Tasarrufun İptali Davası (İİK m.277 vd.)

Norm çıpası: 2004 sayılı İcra ve İflas Kanunu m.277-284 (alacaklının tasarrufun
iptali davası). **Kullanım anında** güncel metin/yürürlük Mevzuat MCP'den,
ilgili içtihat (özellikle muvazaa/bağış-benzeri tasarruf/üçüncü kişi kötüniyeti
konularında yerleşik Yargıtay içtihadı) `oa-ictihat`'tan teyit edilir — aşağıdaki
madde numaraları başlangıç ÇIPASIDIR, hafızadan kesinlenmez.

| Unsur (id önerisi) | Norm çıpası | Delil türü | İspat yükü |
|---|---|---|---|
| U1 — Alacaklının kesinleşmiş/kesinleşmemiş alacağı ve borçlu aleyhine icra takibi (aciz vesikası veya haciz/iflas hâli) | İİK m.277, m.278/1 | İcra dosyası, aciz vesikası, haciz tutanağı | Davacı (alacaklı) |
| U2 — Borçlu tarafından yapılan tasarruf işlemi (satış, bağış, ivazsız/düşük bedelli devir, teminat verme vb.) ve tasarrufun tarihi | İİK m.278-280 | Tapu kaydı/resmi senet, banka dekontu, sözleşme, ticaret sicili kaydı | Davacı |
| U3 — Tasarrufun İİK'nın öngördüğü şüpheli dönem/süre içinde yapılmış olması (haciz/iflasa yakın tarih) | İİK m.279, m.281 | Tasarruf tarihi ile takip/haciz/iflas tarihinin karşılaştırılması (tarih zinciri — bkz. oa-illiyet zaman katmanı) | Davacı |
| U4 — Borçlunun mameleğinin alacağı karşılamaya yetmez hâle gelmesi / borç ödemeden aciz | İİK m.277 | Bilirkişi/mal varlığı tespiti, icra dosyası haciz sonuçları | Davacı |
| U5 — İvazsızlık veya bariz oransızlık (bedelsiz/düşük bedelli devir) YA DA üçüncü kişinin (lehtarın) kötüniyeti/alacaklıyı zarara sokma kastından haberdarlığı | İİK m.278/2-3, m.280 | Emsal bedel/ekspertiz, tanık, taraflar arası akrabalık/ticari ilişki karinesi | Davacı; bazı hâllerde karine ile yer değiştirebilir (kullanım anında teyit) |
| U6 — Davanın süresinde açılması (hak düşürücü süre) | İİK m.284 | Tasarruf/takip tarihleri ile dava açma tarihinin karşılaştırılması | Mahkemece resen + davalı def'i |

**Antitez çapası (M3 köprüsü):** karşı tarafın en olası savunması genellikle
U5'in (ivazsızlık/kötüniyet) çürütülmesi veya U6 (süre) def'idir — `oa-antitez`
matrisinde "usul" (süre) ve "ispat_delil" cepheleri bu unsurlarla eşlenir.

---

## MAL KAÇIRMA KAVŞAĞI — yol seçimi ve İKİ AYRI TARİH EKSENİ (v0.5.13)

Saha dersi: bu davanın kader anı **tarih aritmetiğidir** ve iki eksen
birbirine karıştırılırsa dosya ilk celsede düşer.

**A. Yol seçimi — tasarrufun iptali mi, muvazaa (TBK m.19) mı?** İkisi ayrı
davadır; birinin şartları diğerininkini karşılamaz. Kavşak sorusu üç
kalemdir ve **her üçü de** cevaplanmadan yol seçilmez:
1. Elde **aciz belgesi / kesinleşmiş takip** var mı? (İİK yolunun kapısı)
2. Tasarruf, İİK'nın şüpheli dönem pencerelerine giriyor mu?
3. İşlem gerçekte hiç yapılmamış (görünüşte) mi — yoksa gerçek ama alacaklıyı
   zarara sokan bir işlem mi? Birincisi muvazaa, ikincisi iptal davasıdır.
Yol kapalıysa **kapalı olduğu yazılır**; "her ikisini de açalım" refleksi
harç/vekâlet riski üretir, tercih gerekçeli yapılır (`oa-strateji`).

**B. İki tarih ekseni — ASLA tek tabloya sıkıştırılmaz.**

| Eksen | Yön | Ne ölçer | Norm çıpası |
|---|---|---|---|
| **Şüpheli dönem** | Haciz / aciz / iflastan **GERİYE** | Tasarruf, kritik ana ne kadar yakın yapılmış | İİK m.278, m.279, m.280 |
| **Hak düşürücü süre** | Tasarruftan dava tarihine **İLERİ** | Dava süresinde mi açılmış | İİK m.284 (beş yıl) |

Geri eksen bir **niteleme** işidir (hangi pencere, hangi karine); ileri eksen
takvim hesabıdır. **Geri eksen `hesapla_sure`'a sokulmaz** — o motor süre
aritmetiği içindir; şüpheli dönem değerlendirmesi unsur analizinde kalır.
İleri eksen (m.284) `oa-sure`'a hak düşürücü süre olarak verilir.

**C. "Karine YOK" damgası üç tip taranmadan basılamaz.** İİK m.278 (ivazsızlık
/ bariz oransızlık karineleri), m.279 (aciz hâline yakın dönemde yapılan
belirli işlemler), m.280 (alacaklıyı zarara sokma kastı — özellikle yakınlar
arası ve bilme unsuru). Üçü tek tek taranıp sonucu yazılmadan olumsuz hüküm
verilirse, m.280 hattı açıkken müvekkil davadan vazgeçirilmiş olur. Tarama
sonucu olumsuzsa **kesin dille kapatılır** ("üç karine tipi de taranmıştır;
şu sebeple uygulanamaz") — belirsiz bırakmak yasaktır.

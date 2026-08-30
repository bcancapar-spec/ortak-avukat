# Kloz Cetveli — oa-sozlesme referansı

Cetveldeki her sayım ÖRNEKLEMDİR (anayasal örnekleme ilkesi): kapsamı daraltmaz,
metodu gösterir. Madde numaraları çıpadır; kullanım anında Mevzuat MCP'den teyit
edilir — ezberden şekil şartı/eşik beyan edilmez.

## Tip-bazlı ek kloz örneklemi

- **NDA:** tanım kapsamı (neyin sır olduğu — aşırı geniş tanım aleyhe de işler),
  süre (sözleşme sonrası kaç yıl), istisnalar (kamuya mal olmuş / bağımsız geliştirme /
  yasal zorunluluk), iade/imha, cezai şart, gömülü non-compete/non-solicit TARAMASI.
- **Hizmet/eser:** kabul/muayene prosedürü ve süresi, hakediş, ayıp ihbarı, gecikme
  cezası ile fesih ilişkisi, alt yüklenici, IP/eserin devri (kapsam: yalnız iş ürünü mü),
  SLA/servis seviyeleri.
- **Kira (işyeri):** TBK emredici rejimi, kira tespiti, tahliye taahhüdü (tarih/şekil),
  devir yasağı, ortak gider, depozito rejimi.
- **Ortaklık/hissedarlar:** oy/veto eşikleri, ön alım/birlikte satış (ROFR/tag-drag),
  kilitlenme çözümü, kâr dağıtım politikası, rekabet yasağı, çıkış mekanizması.
- **İş sözleşmesi:** rekabet yasağının süre/coğrafya/iş-türü sınırı (TBK m.444-447
  çıpası — teyitle), cezai şartın tek taraflılığı sorunu, fazla mesai muvafakati,
  eğitim gideri karşılığı asgari süre.
- **Bayilik/franchise/tek satıcılık:** münhasırlık ve rekabet etmeme → 4054 m.4 +
  dikey anlaşmalar muafiyet rejimi (Rekabet Kurumu kararları — oa-ictihat), asgari
  alım taahhüdü, marka kullanımı, stok iade, fesih sonrası müşteri/portföy tazminatı.
- **Lisans:** kapsam (ülke/süre/münhasırlık), alt lisans, denetim hakkı, kaynak kod
  emaneti (escrow), telif/royalty raporlaması.
- **Sulh/ibra protokolü:** ibranın kapsamı (hangi talepler), feragat sınırı, gizlilik,
  vergi yükü paylaşımı, ifa şartına bağlı ibra.

## Karşı taslak TUZAK listesi (İNCELEME modunda ilk tur — örneklem)
Tek taraflı fesih/değişiklik · asimetrik cezai şart ve sorumluluk tavanı ·
muafiyet/sorumluluk sınırlama klozu · zamanaşımı kısaltması · aleyhe delil sözleşmesi ·
uzak forum/tahkim (maliyetle hak arama fiilen kapanır) · otomatik uzama + dar fesih
penceresi · devir serbestisi asimetrisi · IP devrinin iş ürünü dışına taşması ·
NDA içine gömülü rekabet yasağı · referans/logo/veri kullanım izni (KVKK) ·
merger klozunun yuttuğu e-posta taahhütleri · "uygun görülen" gibi tek taraflı
takdir ifadeleri · bildirimin yalnız karşı tarafça seçilen kanala bağlanması.

## Şekil şartı çıpaları (kullanımda MUTLAKA Mevzuat MCP teyidi)
Kefalet: el yazılı azami miktar + tarih, eş rızası (TBK m.583-584) · taşınmaz satış
vaadi: noter düzenleme şekli · araç satışı: noter · işyeri devri/marka devri: sicil ·
tahkim şartı: yazılılık · tüketici işlemlerinde TKHK'nın emredici içerik şartları ·
elektronik ortamda kurulan sözleşmede güvenli e-imza/KEP delil rejimi.

## Geçerlilik denetim merdiveni
0. **Ehliyet / temsil** — fiil ehliyeti ve ayırt etme gücü (TMK m.9: "Fiil
   ehliyetine sahip olan kimse, kendi fiilleriyle hak edinebilir ve borç altına
   girebilir."; m.15: ayırt etme gücü bulunmayan kimsenin fiilleri hukukî sonuç
   doğurmaz) + tüzel kişide temsil yetkisinin kapsamı (sicil/imza sirküleri,
   vekâletname). "Ehliyet klozu" YAZILAMAZ — bu bir kloz değil, metnin altındaki
   katmandır; `sozlesme.json`'da `gecerlilik_katmani.ehliyet_temsil` alanına işlenir.
1. Emredici hükme aykırılık → kesin hükümsüzlük (kloz veya sözleşme).
2. Şekil şartı ihlali → geçersizlik (tipe göre tamamı/kısmı).
3. Genel işlem koşulu (TBK m.20-25) → yazılmamış sayılma + aleyhe yorum.
   Çıpalar (Mevzuat MCP teyitli): m.21 — karşı tarafa koşulların varlığı hakkında
   açıkça bilgi verilip içeriğini öğrenme imkânı sağlanmadıkça ve karşı taraf kabul
   etmedikçe genel işlem koşulları **yazılmamış sayılır**; "sözleşmenin niteliğine ve
   işin özelliğine yabancı olan" koşullar da yazılmamış sayılır. m.25 — genel işlem
   koşullarına dürüstlük kurallarına aykırı olarak karşı tarafın aleyhine veya
   durumunu ağırlaştırıcı nitelikte hükümler **konulamaz**.
   `gecerlilik_katmani.genel_islem_kosullari` alanına işlenir.
4. Cezai şartta indirim (TBK m.182/son; tacirler arası istisna bilinci — m.22 TTK
   çıpası, teyitle).
5. Ahlaka/kişilik haklarına aykırı aşırı bağlayıcılık (kelepçeleme) → kısmi butlan.
6. **İptal edilebilirlik (hükümsüzlük DEĞİL — bozulabilirlik) ve onun SÜRESİ.**
   İmzalanmış bir metinde çoğu zaman tek gerçek çıkış yolu budur ve süreye bağlıdır;
   süre geçerse kloz tartışması anlamsızlaşır. Çıpalar (Mevzuat MCP teyitli):
   - **İrade sakatlıkları (TBK m.30-39):** esaslı yanılma (m.30 — "Sözleşme kurulurken
     esaslı yanılmaya düşen taraf, sözleşme ile bağlı olmaz."), aldatma (m.36 — aldatma
     sonucu sözleşme yapan taraf, yanılması esaslı olmasa bile bağlı değildir; üçüncü
     kişinin aldatmasında karşı tarafın bilmesi/bilecek durumda olması aranır),
     korkutma (m.37 — diğerinin veya üçüncü kişinin korkutması sonucu sözleşme yapan
     taraf bağlı değildir).
   - **SÜRE (m.39):** yanılma/aldatmayı öğrendiği ya da korkutmanın etkisinin ortadan
     kalktığı andan başlayarak **bir yıl** içinde sözleşme ile bağlı olmadığını
     bildirmez veya verdiği şeyi geri istemezse, **sözleşmeyi onamış sayılır**.
     Onanmış sayılma, aldatma/korkutmada tazminat hakkını ortadan kaldırmaz (m.39/2).
   - **Aşırı yararlanma (m.28):** edimler arasında açık oransızlık, zarar görenin zor
     durumda kalmasından veya düşüncesizliğinden ya da deneyimsizliğinden yararlanılarak
     gerçekleştirilmişse zarar gören, ya sözleşmeyle bağlı olmadığını bildirip edimin
     geri verilmesini ya da sözleşmeye bağlı kalarak oransızlığın giderilmesini
     isteyebilir. **SÜRE:** düşüncesizlik/deneyimsizliği öğrendiği; zor durumda kalmada
     bu durumun ortadan kalktığı tarihten başlayarak **bir yıl** ve her hâlde
     sözleşmenin kurulduğu tarihten başlayarak **beş yıl**.
   → Bu basamak tetiklendiği anda süre hesabı `oa-sure` ile (`--tur maddi`) yapılır;
   başlangıç anı olgu meselesidir ve `oa-vakia` kronolojisinden çıkarılır.

Her basamak `oa-ictihat` ile güncel içtihattan teyit edilerek uygulanır; yukarıdaki
madde metinleri kullanım anında Mevzuat MCP'den YENİDEN teyit edilir (ezber yasağı).

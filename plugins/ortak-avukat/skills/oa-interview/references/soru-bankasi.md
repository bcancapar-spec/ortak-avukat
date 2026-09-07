# Soru Bankası — Alan Bazlı İlk İnceleme

> Bu banka, ilk inceleme mülakatında **alan belirlendikten sonra** kullanılır. Hepsini sormak zorunda değilsin; karar-kritik olanları seç, avukatın zaten verdiğini tekrar sorma. Amaç sorgu değil, **illiyet zincirini kurabilecek asgari maddi gerçeği** toplamak.
>
> **Muhatap avukattır; her cevap `belgeli|beyan` statüsü alır (A-5, v0.5.16).** Cevabın dayanağı dosyadaki bir evraksa `belgeli` (evrak adı/tarihi yazılır); müvekkil anlatısıysa `beyan` — belge gelene kadar İDDİA'dır ve `oa-vakia` `beyan` kategorisine (kısmi destek, ispat boşluğu açık) düşer. Statü söylenmemişse `beyan` sayılır.

## Her alanda ortak çekirdek (önce bunlar)
1. **Talep:** Müvekkilin somut, ölçülebilir hedefi ne? (tahsil / iptal / men / boşanma / borç yapılandırma…)
2. **Roller:** Müvekkil davacı/davalı/başvuran/şikâyetçi mi? Karşı taraf kim, vekili var mı?
3. **Aşama + merci:** Henüz açılmadı / derdest / karar çıktı / kanun yolu? Hangi mahkeme-daire, esas no?
4. **SÜRE (en kritik):** İşleyen bir süre var mı? Tebliğ/öğrenme tarihi nedir? (→ `oa-sure`)
5. **Belgeler:** Hangi belgeler elde (sözleşme, ihtarname, kararlar, bilirkişi, tebligat)? Hangileri eksik?
6. **Zaaf (dürüst, erken):** Karşı tarafın en güçlü kozu ne? Müvekkilin kendi belgelerinde zayıf nokta var mı?
7. **Masraf gücü (A-6/A-17, v0.5.16):** Harç (başvuru + peşin karar harcı), bilirkişi ücreti, ihtiyati haciz/tedbir **teminatı** ve **karşı vekâlet riskini** fiilen KİM taşıyacak — müvekkil mi, sigorta/üçüncü kişi mi, adli yardım mı? Nakit akışı yol seçimini belirler (→ `oa-strateji` §1; rakamlar `oa-strateji/scripts/maliyet_cetveli.py`).
8. **Risk toleransı (müvekkil beyanı):** `kaçınan | nötr | alan` — "bugün kesin az" ile "yıllar sonra belki çok" arasında müvekkil hangisini seçer? Avukatın tahmini değil, müvekkilden alınmış beyan; alınmadıysa "bilinmiyor" yazılır (`oa-strateji` bu iki girdi olmadan yol kararı vermez → «Müvekkil Kararı Bekleyen»).

## İş hukuku
Hizmet süresi, son ücret (brüt/net, ekler), fesih tarihi ve şekli (yazılı bildirim var mı), fesih sebebi, SGK kayıtları, TİS kapsamı var mı, savunma alınmış mı, bordro/puantaj, fazla mesai-AGİ kayıtları, ihbar/kıdem ödendi mi.

## Ticaret / borçlar
Sözleşme tipi ve tarihi, taraf sıfatları (şirket/şahıs, temsil yetkisi), ifa/temerrüt durumu, ihtarname teatisi, fatura/cari hesap, kambiyo senedi varsa tanzim/vade/teminat niteliği, ticari defterler, (varsa) ortaklık yapısı ve yetki sınırlandırması.

## İcra-iflas
Takip türü ve tarihi, taraf sıfatı (alacaklı/borçlu/üçüncü kişi), itiraz/şikâyet durumu ve tarihi, haczedilen mal kimde-kimin adına (istihkak ise mülkiyet karinesi), icra dosya no, ödeme emri tebliğ tarihi.

## İdare / vergi
İdari işlem ne, tebliğ tarihi (dava süresi için kritik), üst makama başvuru yapıldı mı (İYUK m.11), işlemin dayanağı ve gerekçesi, ilk derece/istinaf/temyiz aşaması, (vergi ise) tarhiyat türü ve tutarı.

## Anayasa / AYM bireysel başvuru
Tüm olağan başvuru yolları tüketildi mi (hangi aşamalar), nihai kararın tebliğ tarihi (30 gün için kritik), ihlal edildiği ileri sürülen hak(lar), dayanılacak Anayasa hükümleri, güncel/kişisel/doğrudan etkilenme var mı, vekâletname.

## Gümrük
Eşyanın tanımı ve beyan edilen GTİP, idarenin önerdiği GTİP, yeniden sınıflandırma gerekçesi (format/şekil mi esas mı), ceza tutarı, tebliğ tarihi, numune/teknik rapor var mı.

## Aile
Evlilik tarihi, çocuk(lar) ve yaş, anlaşmalı mı çekişmeli mi, velayet/kişisel ilişki talebi, mal rejimi ve edinilmiş mal (katılma alacağı), 6284 koruma kararı var mı, (çocuk teslimi ise) mevcut mahkeme kararı ve teslim sorunu.

## Sosyal güvenlik
Borç türü (prim/idari para cezası), tutar bandı ve dönem aralığı, sigortalılık statüsü (Bağ-Kur/4a/4b), takip kesinleşti mi, tahsil zamanaşımı durumu (6183 m.102), hizmet ihtiyacı var mı (durdurma alternatifi için), daha önce yapılandırma başvurusu yapıldı mı.

> Alan belirsizse, ortak çekirdeği sor; cevaplar alanı netleştirince ilgili bloğa geç. Alan tespiti için `oa-alan` ile birlikte çalış.

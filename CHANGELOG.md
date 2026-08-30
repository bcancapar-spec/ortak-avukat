# GELİŞİM DEFTERİ (CHANGELOG)

Bu depo "gerçek testlerle optimum" yöntemiyle gelişir: **gerçek derdest dava
koşusu → karne → karnede ölçülen kusurun onarımı → yeni sürüm.** Bu defter,
sürüm zincirinin kök özetidir. Üç kademe birbirini tamamlar:

- **Bu dosya** — sürüm başına tek kayıt (ne, neden, hangi saha kanıtıyla).
- **Parça günlükleri** — her skill'in kendi `references/degisiklik-gunlugu.md`
  dosyası (dosya/fonksiyon düzeyinde ayrıntı).
- **Karneler ve Release'ler** — saha koşularının adli analizi
  ([KARNE-307.md](KARNE-307.md), [KARNE-1865.md](KARNE-1865.md),
  [SAHA-SONUCU.md](SAHA-SONUCU.md)) ve GitHub Release notları.

Kural: **CI yeşermeden sürüm etiketi atılamaz**; sürüm damgaları (plugin,
marketplace, iki script) daima birlikte artar. Dosya kimlikleri anayasa m.7
gereği yalnız saha etiketiyle anılır.

---

## v0.5.13 — Heyet Kararlarının İnfazı (2026-08-27)
**Kanıt türü farklı:** bu sürüm bir saha karnesinden değil, **denetimden**
doğdu — 20 skill dört turdan geçti (7 mesleki denetçi + puanlama · 5 disiplinli
hukukçu hakem heyeti · 4 pratikçi avukatın tez/antitez düellosu · 3 yazılım
mühendisinin kod hükmü). Her hukuki iddia Mevzuat MCP'den madde metniyle
doğrulandı; ajan transkriptleri SHA-256 manifestli arşive mühürlendi.
**İki gerçek hata düzeltildi:** katılma anı (CMK m.237 — kanun yolunda
istenemez; ilk derecede hüküm verilinceye kadar) ve itiraz süresi (m.268:
"7 gün" → **iki hafta**, öğrenme gününden; JSON + gömülü fallback birlikte).
**Bir hakem tezi teyitte ÇÜRÜDÜ** ve bu da kayda geçti: "istinaf tefhimden
işler" iddiası m.273/1'in güncel metniyle yıkıldı (f.2, 7499 ile mülga) —
dosya doğruydu, değiştirilmedi. Ders: düzeltmenin kendisi de teyide tabidir.
**Yeni:** süre başlangıç türü çatalı (`--baslangic-turu`; belirsizde iki
senaryo + erken tarih) · "süre kaçtı" mutlak dilinin kırılması + kurtarma
kapıları kataloğu (yargı koluna göre; İYUK'ta eski hâle getirme YOK) ·
tutuklu dosya kipi · celse kartı + **dahili sızıntı kapısı** (iç analiz
belgesi dış çıktıya kopyalanamaz) · zorunlu arabuluculuk dava şartı dört
adreste · İİK m.67/68/72 + İYUK m.10/11 + VUK m.107/A çıpaları · mal kaçırma
kavşağı (iki tarih ekseni). Gerekçeli daraltmalar
[HEYET-KARARLARI-v0513.md](HEYET-KARARLARI-v0513.md)'de. Süit **1405**.

## v0.5.12 — İçtihat Kaynakçası (2026-08-27)
**Avukat kuralı:** dilekçeye giren her Yargıtay/Danıştay kararının **kaynak
linki** tüm çıktılarda görünsün. Taslağın sonuna idempotent kaynakça bloğu
üretildi; URL **yalnız** muhakeme kaydının teyitli satırından alınır —
uydurma yasak, linki olmayan künye görünür notla işaretlenir. UDF üretiminden
önce işlenir, makbuza kaydı düşer. Ayrıca 40-UYAP adının gerekçesi sözlüğe
(bant başı = giden evrak) ve tüm token ölçümleri repoya girdi. Süit 1394.

## v0.5.11 — Kit Güvenlik Katmanı (2026-08-26)
**Saha kanıtı:** 1865 (çok-oturumlu, müdahaleli-yetkili · [KARNE-1865.md](KARNE-1865.md)).
Kök düşman adlandırıldı: uygulamanın rpm anlık-görüntüsünden bulaşan bayat
araç nesli (777'den beri 3. nüks); tek seferlik onarımın yetmediği ölçüldü.
**Onarım:** rpm karantinası ('ask') · kilitli çekirdek (salt-okunur + 'ask') ·
yönlü tazelik (bayat / kanaldan-yeni / özdeş) · oturum damgası (defter+makbuz
`session_id`) · çok-oturum görünürlüğü · sözleşme-dışı dizin ve MANİFEST-önce
bekçileri. Süit 1385. Saha koşusu maliyeti: ~4,3M token (çok oturumlu).

## v0.5.10 — Kusursuz UDF Dönüşümü (2026-08-25)
**Saha kanıtı:** 307 (K1: ürün makbuzdan 68 dk sonra mühür dışında değişti;
K2: makbuz resmî ürünü kapsamıyordu · [KARNE-307.md](KARNE-307.md)) + 923
(çift-uzantı ve mühürsüz-kopya bağımsız tekrarı).
**Onarım:** atomik mühür (üretim=mühür, üç yolda) · filo-tazelik kapısı
(kök + 40-UYAP tüm teslim-sınıfı UDF'ler makbuza) · çift-uzantı kaynağında
öldü · kopyalar mühürleriyle gider · sunum kilidi makbuz-sonrası değişiklik
penceresini kapattı. Süit 1371. Saha maliyetleri: 307 ~822k · 923 ~360k token.

## v0.5.9 / v0.5.9.1 — Deterministik Tamamlayıcı Zincir (2026-08-22)
**Saha kanıtı:** 777 karnesi + 24-kök çapraz taraması + iki bağımsız hakem
turu (T1-T26 konsolide raporun yerli uygulaması). 777 koşusu ~1,50M token.
Sunum kilidi (makbuzsuz teslim-sınıfı gönderim → 'ask') · inline dilekçe
denetimi · zincir-durumu enjeksiyonu · 40-UYAP dış-çıktı şeması · vitrinin
avukat diliyle sıfırdan inşası. 0.5.9.1: kurulum damgası (sürüm-cache kuralı).

## v0.5.8.4 – v0.5.8.6 — Saha Karnelerinin İnfazı (2026-08-15 → 08-18)
**Saha kanıtı:** 372 (elle-UDF krizi; A/B testiyle hvl-default imzası bulundu),
346 (künye kapısı gerçek açık yakaladı; [G6] mutlak triyaj doğdu), 777 (bayat
kit kök nedeni).
0.5.8.4: elle-UDF engeli + makbuz garantisi (RED bile damgalı) + mühür
otomasyonu + şekil kapısı (4×42,52 pt). 0.5.8.5: [G6] mutlak triyaj (tam metin
okunmadan karar dilekçeye giremez; ALEYHE → iç cephanelik) + hook dirilişi +
e-imza halkası. 0.5.8.6: sürüm kilidi/parmak izi + VERSION.json + devralma
köprüleri. Koşu maliyetleri: 372 ~1,24M · 346 ~1,17M token.

## v0.5.7.x — Saha Donanımı (2026-08-07 → 08-08)
Bayat-tohum aşısı (komşu klasörden kopya yasağı — 754 bulgusu) · G4 bağlantı
kapısı · Yargı Pro birincil + otomatik yedek zincir · davadan gelen atıflar da
link zincirine tabi (kullanıcı kuralı) · CI stdout kirliliği onarımı.

## v0.5.6.1 — Hook Kaydı + Devir Zorlayıcı (2026-08-06)
Hook katmanının kayıt altyapısı; oturumlar arası devir disiplini; rehber
sadeleştirmesi ("ateşlemeyen kapı silinir" ilkesine ilk büyük uygulama).

## v0.5.5 – v0.5.5.5 — Aktivasyon Zinciri + Müdahalesiz Test Dersleri (2026-07-28 → 08-02)
**Saha kanıtı:** 214 evraklık bakir klasörde müdahalesiz test — "kapının gücü
kodunda değil tetiğindedir." Aktivasyon zinciri, OCR nöbetçisi, UDF hattının
resmî araca kilitlenmesi, geçerlilik kapısı, içerik hakemi; 0.5.5.5: cp1254
kodlama çökmesi onarımı (P0).

## v0.5.0 – v0.5.4 — Temel Atma (2026-07-19 → 07-20)
Temiz kurulum (tek kaynak: GitHub) · oa-ingest v1.5 paralel çıkarım · Okuma
Ekonomisi (Gate A-G) · İçtihat Muhakeme Zinciri (G1-G3) · working memory
(`dosya-analiz.md` doğum anı) · dilekçe playbook · anayasa dedup. İlk paket
57 testle çıktı; bugün 1405.

---
*Daha eski tarih öncesi (v0.4.0 ve öncesi) tek-skill dönemidir; bugünkü
20-parça mimarisi v0.5.0 temiz kurulumuyla başlar.*

# Unsur Şablonu — Kıdem Tazminatı + İhbar Tazminatı

Norm çıpası: Kıdem tazminatı — 1475 sayılı (mülga) İş Kanunu m.14 (yürürlükte
tutulan tek madde); ihbar tazminatı — 4857 sayılı İş Kanunu m.17. **Kullanım
anında** güncel tavan/taban tutarlar, faiz türü (bankalarca mevduata
uygulanan en yüksek faiz — kıdemde; yasal faiz — ihbarda, güncel içtihatla
teyitli) ve haklı/geçerli sebep içtihadı `oa-ictihat`/Mevzuat MCP'den teyit
edilir.

| Unsur (id önerisi) | Norm çıpası | Delil türü | İspat yükü |
|---|---|---|---|
| U1 — İşçinin en az 1 yıllık kıdeminin bulunması (kıdem tazminatı için) | 1475 sk. m.14/1 | SGK hizmet dökümü, işe giriş bildirgesi, iş sözleşmesi | Davacı (işçi) |
| U2 — İş sözleşmesinin kıdem tazminatına hak kazandıran bir sebeple sona ermesi (işveren feshi haklı sebep DIŞI, işçinin haklı feshi, emeklilik/askerlik/evlilik gibi kanuni sebepler) | 1475 sk. m.14/1 | Fesih bildirimi, istifa dilekçesi + haklı sebep delili, emeklilik belgesi | Davacı |
| U3 — İşverenin feshinin HAKLI SEBEBE dayanmadığı (haklı sebep varsa kıdem/ihbar hakkı doğmaz) | İş K. m.25 (işverenin haklı fesih hâlleri — teyitli) | Fesih bildirimi/gerekçesi, tutanaklar, tanık | Kıdem/ihbar isteyen tarafta haklı-sebep YOKLUĞUNU değil, işveren TARAFI haklı sebebin VARLIĞINI ispatla yükümlü (ispat yükü yer değiştirir — kullanım anında teyitli) |
| U4 — Kıdem tazminatı tavanına göre son ücret + giydirilmiş ücret (ikramiye, yol, yemek, prim gibi süreklilik arz eden yan haklar) tespiti | 1475 sk. m.14 + kullanım anında teyitli tavan | Ücret bordroları, banka hesap dökümü, bilirkişi hesap raporu | Davacı (miktar) — işveren karşı delil sunabilir |
| U5 — İhbar süresine uyulmadan (bildirimsiz) fesih yapılması VEYA ihbar süresi ücretinin ödenmemiş olması | İş K. m.17 (kıdeme göre kademeli ihbar süreleri — teyitli) | Fesih tarihi + kıdem süresi hesabı, ödeme dekontu (varsa) | Davalı (işveren) — ödediğini ispatla yükümlü |
| U6 — Zamanaşımı (kıdem/ihbar alacakları için 7036 sy. K. sonrası özel süre — değeri kullanım anında teyitli) | İş K. m.32/son atfıyla ilgili hükümler + **TBK m.161** | Fesih/muacceliyet tarihi ile dava/arabuluculuk başvuru tarihi | **DEF'İDİR — davalı (işveren) ileri sürmedikçe hâkim resen gözetemez.** TBK m.161 birebir: *"Zamanaşımı ileri sürülmedikçe, hâkim bunu kendiliğinden göz önüne alamaz."* İşçi vekiliyken bu satır bir FIRSAT (def'i gelmezse alacak ayakta), işveren vekiliyken bir GÖREV (def'i cevap dilekçesinde açıkça ileri sürülür) |
| U7 — Arabuluculuğa başvuru zorunluluğu ve son tutanak tarihi | 7036 sy. İş Mahkemeleri Kanunu (teyitli) | Arabuluculuk son tutanağı | Mahkemece resen (dava şartı) |

**Süre rejimi ayrımı (A-15, v0.5.14 — dizgi hatası onarımı):** bu şablonun
"İspat yükü" sütununda **zamanaşımı** ile **hak düşürücü süre / dava şartı**
aynı yapıştırma dizgiyle yazılmıştı. Ayrım kaldırılamaz:
- **Zamanaşımı (U6):** borcu sona erdirmez, dava edilebilirliğini zayıflatır →
  **def'i**, ileri sürülmedikçe hâkim gözetemez (TBK m.161).
- **Hak düşürücü süre / dava şartı (U7 ve işe iade penceresi):** hakkın kendisini
  düşürür veya davanın görülebilirliğini engeller → **mahkemece resen** gözetilir.
Şablonlar arası kopyalarken bu sütun **şablon başına** yeniden yazılır.

**Antitez çapası (M3 köprüsü):** işveren tarafının en olası savunması U3'ün
(işçinin/işverenin haklı feshi) veya U6 (zamanaşımı) def'idir — `oa-antitez`
matrisinde "maddi_vakia"/"usul" ve "zamanasimi" cepheleri bu unsurlarla
eşlenir; işçi vekili için U3'ün çürütülmesi ve U4 (giydirilmiş ücret) miktar
tartışması ana cephelerdir.

# Yargı Pro teyit izi — v0.5.16 / GRUP C1 (oa-dilekce: [F] hafif kip, [P] netice-i talep playbook'u, [N] beyaz liste, UDF kesinti planı)

Hakem: Yargı Pro hakemi (yalnız okuma + MCP). Tarih: 2026-09-07. Taban: 80ac847.
Kapsam: `git diff 80ac847` içindeki .md/.py (tests hariç) dosyalarına giren hukuki norm atıfları.
Müvekkil/dosya verisi yok; sorgular yalnız kanun no + madde no.

## Araç + sorgu + sonuç

| # | Araç | Sorgu | Diffteki iddia | Sonuç |
|---|---|---|---|---|
| 1 | `mevzuat_getir` | 6100 m.111 | terditli dava: aslilik-ferîlik; hukuki/ekonomik bağlantı şart; asli talep esastan reddedilmedikçe ferî talep incelenemez (m.111/1-2) | (1) ve (2) aynen. UYUŞUYOR |
| 2 | `mevzuat_getir` | 6100 m.109 | m.109/1 bölünebilir talep; m.109/3 feragat karinesi yok; m.109/4 (Ek 16/7/2026-7589/20) bir defaya mahsus artırım + zamanaşımı dava tarihinden kesilmiş sayılır | (1),(3),(4) aynen; (4) «Ek:16/7/2026-7589/20». UYUŞUYOR |
| 3 | `mevzuat_getir` | 6100 m.107 | «belirsiz alacak davası MÜLGA (16/7/2026-7589/19)» | «MADDE 107– (Mülga:16/7/2026-7589/19 md.)». UYUŞUYOR |
| 4 | `mevzuat_ara` | mevzuat_no 7589 | «RG 31.07.2026 — sayı bu turda teyit edilmedi» | 7589 s.K. RG 31.07.2026, kabul 16.07.2026; RG sayısı outline'da 33326. UYUŞUYOR (sayı artık teyitli: 33326) |
| 5 | `mevzuat_getir` | 7589 m.26 | «yürürlük m.26/1-c: bu maddeler yayımı tarihinde» | (1)-c «Diğer maddeleri yayımı tarihinde» — m.10/19/20 bu sınıfta (a: m.3; b: m.11,12,22 üç ay sonra). UYUŞUYOR |
| 6 | `mevzuat_getir` | 7589 geçici m.1 (outline → gecici1) | «geçici m.1/10: mülga m.107, kaldırılma tarihinden önce açılan davalar bakımından uygulanmaya devam olunur» | f.(10) aynen. UYUŞUYOR |
| 7 | `mevzuat_getir` | 3095 m.1 | «kanuni faiz (Değişik 16/7/2026-7589/10): reeskont oranının %80'i; 30 Haziran beş puan farkı» | Aynen. UYUŞUYOR |
| 8 | `mevzuat_getir` | 3095 m.2 | temerrüt faizi m.1 oranı; ticari işlerde avans faizi sözleşme olmasa bile; akdi faiz üstündeyse temerrüt faizi akdi faizden az olamaz | Üç fıkra aynen. UYUŞUYOR |
| 9 | `mevzuat_getir` | 6098 m.117 | temerrüt: ihtar; belirli gün; haksız fiilde fiil tarihi; sebepsiz zenginleşmede zenginleşme tarihi, iyiniyetlide bildirim şart | Aynen. UYUŞUYOR |
| 10 | `mevzuat_getir` | 6100 m.323 | «m.323/1-ğ vekille takip edilen davalarda takdir olunacak vekâlet ücreti yargılama giderindendir» | (1)-ğ aynen. UYUŞUYOR |
| 11 | `mevzuat_getir` | 6100 m.326 | «/1 aleyhine hüküm verilen taraftan; /2 haklılık oranına göre» | (1),(2) aynen. UYUŞUYOR |
| 12 | `mevzuat_getir` | 6100 m.389 | «m.389/1 ihtiyati tedbir şartları» | (1) aynen. UYUŞUYOR |
| 13 | `mevzuat_getir` | 6100 m.332 | (hakem kontrolü — diffte anılmıyor) | (1) «Yargılama giderlerine, mahkemece resen hükmedilir.» → aşağıdaki KRİTİK'in dayanağı |

«Yön. 2646 m.8» (udf-hatti-kesinti-plani.md) tabanda zaten mevcut bir atfın tekrarıdır; bu turda yeniden teyit edilmedi. Belgede «bu turda teyit edilmedi» etiketli iddialar (dava dilekçesinin temerrüt hükmü doğurması; tedbirde teminat/itiraz maddeleri; AAÜT sayıları) anayasa m.4'e uygun biçimde çıpalanmış — teyitsiz iddia olarak sunulmamış.

## Hukuki mantık (netice-i talep / faiz)
- Faiz türü ve başlangıcı yazılmazsa faize hükmedilemez (taleple bağlılık) — doğru.
- Kısmi dava + m.109/4 bir defalık artırım; yeni davada «belirsiz alacak» kalıbı kurulmaz — m.107 mülga + geçici m.1/10 ile uyumlu, doğru.
- Meşru terdit / kendini yenen terdit ayrımı m.111 ile çelişmiyor (m.111 meşru terdite izin verir; playbook yalnız taktik sınır koyuyor).
- **YANLIŞ ÖNERME (KRİTİK):** `dilekce_denetim.py` `netice_talep_uyarilari` [P] uyarı metni: «talep bloğunda 'yargılama gideri' / 'vekâlet ücreti' istemi görünmüyor — HMK m.323/ğ + m.326 gereği istenmeyen kalem hükme girmeyebilir». HMK m.332/1 yargılama giderlerine (m.323 kapsamı, vekâlet ücreti dahil) mahkemece RE'SEN hükmedilmesini emreder; «istenmeyen kalem hükme girmeyebilir» önermesi bu maddeye aykırıdır ve m.323/m.326 bu sonucu taşımaz. Doğru ifade: «yargılama giderine re'sen hükmedilir (HMK m.332/1); açık istem sahada standarttır / hükmün eksik yazılmasına karşı sigortadır». SKILL.md 5. kalem bu yanlış sonucu yazmıyor; yalnız script metni yanlış.

## İçtihat künyesi / «yerleşik hat» iddiası
Diff'te hafızadan yazılmış içtihat künyesi yok; test fikstürü «E. 2098/7, K. 2098/8» sentetik.

## m.7
TCKN / gerçek kişi / gerçek dosya adı taraması: bulgu yok. Yeni referans belgesi telif satırında avukatın kendi adı (repo standardı) — müvekkil verisi değil.

## Hüküm
KRİTİK: 1 (yukarıdaki [P] uyarı metni — HMK m.332/1'e aykırı önerme; düzeltme tek satır). KÜÇÜK: RG sayısı 33326 artık teyitli, SKILL.md «sayı bu turda teyit edilmedi» notu güncellenebilir. → ONAY YOK (kritik giderilince onay).
MCP çağrı sayısı (bu grup için): 13.

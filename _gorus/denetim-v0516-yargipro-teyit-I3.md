# v0.5.16 / I3 — Yargı Pro teyit izi (hakem: Yargı Pro; tarih 2026-09-07)

Kapsam: `git diff 80ac847` — oa-mudafii/SKILL.md (§2/A sonuç haritası, §2/B beyan protokolü), oa-musteki-vekili/SKILL.md (§0 ceza↔hukuk köprüsü), tests/README.md, tests/test_v0516_I3.py. Kod düzeltme yapılmadı; testler koşulmadı (uygulayıcı koştu). Müvekkil/kişi verisi yok.

## Araç çağrıları (27)

| # | Araç | Sorgu | Sonuç / hüküm |
|---|---|---|---|
| 0 | kullanici_profili_getir | — | profil alındı (bağlayıcı kural) |
| 1 | mevzuat_getir | CMK 5271 m.231 | 7589/15 (16/7/2026) ile f.5-14 değişik; 2 yıl/adlî para; f.6 a-b-c (zararın giderilmesi); f.7 erteleme/seçenek yasağı; f.8 beş yıl denetim + zamanaşımı durur; f.9 taksit; f.10 düşme; f.11 itiraz; f.12 istinaf (m.272/3 saklı) / BAM-Yargıtay ilk derece → temyiz; f.13 kayıt; f.14 işkence-eziyet istisnası. Sanığın kabulü şartı f.6'da yok → SKILL "uygulama anında teyit" notu doğru. UYUMLU |
| 2 | mevzuat_getir | CMK m.250 | f.1 suç listesi, f.3 müdafi huzurunda kabul, f.4 yarı indirim, f.5-6 m.50/51/231 kıyasen, f.9 talepten ağır hüküm yok + mazeretsiz gelmeme = vazgeçme, f.10 delil yasağı, f.11 iştirak/birlikte suç, f.12 yaş/akıl, f.14 itiraz. UYUMLU |
| 3 | mevzuat_getir | CMK m.251 | f.1 asliye ceza, iddianame kabulü sonrası, duruşma günü belirlenmeden; f.2 iki hafta; f.3 dörtte bir; f.4 HAGB yazılı karşı çıkmama; f.5 itiraz; f.6 duruşma açma; f.7-8 izin/talep + birlikte suç. UYUMLU |
| 4 | mevzuat_getir | CMK m.253 | f.1-b listesi (m.106/1, 141, 155, 157 vb.), f.3 cinsel/123A/125 dışlama + birlikte suç kuralı, f.4 yedi gün ret, f.7 tüm mağdurlar, f.8 delil toplamaya engel değil, f.18 tekrar yok, f.19 KYOK/erteleme/tazminat davası yasağı/ilam niteliği, f.20 delil yasağı, f.21 zamanaşımı durur. UYUMLU. Küçük: f.3'e 7571/24 (24/12/2025) önödeme istisnası eklenmiş, SKILL'de yok |
| 5 | mevzuat_getir | CMK m.147 | f.1-e susma hakkı, f.1-f lehe delil. UYUMLU |
| 6 | mevzuat_getir | CMK m.172 | KYOK — soruşturmada beraat karşılığı. UYUMLU |
| 7 | mevzuat_getir | CMK m.254 | f.2 (7531/17, 2024) def'aten → düşme; taksit → durma. UYUMLU |
| 8 | mevzuat_getir | CMK m.255 | yalnız uzlaşan yararlanır. UYUMLU |
| 9 | mevzuat_getir | CMK m.141 | f.1-e KYOK/beraat sonrası tazminat. UYUMLU |
| 10 | mevzuat_getir | CMK m.223 | f.2 beraat halleri (a-e). UYUMLU |
| 11 | mevzuat_getir | CMK m.234 | f.1-a-1 delil toplanmasını isteme. UYUMLU |
| 12 | mevzuat_getir | CMK m.272 | f.3 istinaf edilemeyen hükümler (adlî para sınırı, 500 gün beraat, kesin hükümler). SKILL'deki "kapalı hükümlerde süre/harç kaybı" parantezi belirsiz — küçük |
| 13 | mevzuat_getir | TCK 5237 m.168 | f.1 üçte iki (kovuşturma öncesi), f.2 yarı (hüküm öncesi), f.4 kısmi iade rıza. UYUMLU |
| 14 | mevzuat_getir | TCK m.51 | 2 yıl / 18 yaş altı-65 üstü 3 yıl; a) 3 aydan fazla kasıtlı mahkûmiyet yok; b) pişmanlık; f.2 zarar koşulu; f.3 denetim 1-3 yıl, ceza süresinden az olamaz; f.7 infaz; f.8 infaz edilmiş sayılır. UYUMLU |
| 15 | mevzuat_getir | TCK m.49 | f.2 kısa süreli = bir yıl veya daha az. UYUMLU |
| 16 | mevzuat_getir | TCK m.50 | f.1 a-f seçenekler; f.2 seçimlik suçta paraya çevrilmez; f.3 zorunlu çevirme; f.4 taksir/bilinçli taksir; f.5 asıl mahkûmiyet; f.6 infaz hâkimliği. UYUMLU. Küçük: f.3'teki "daha önce hapis cezasına mahkûm edilmemiş olmak" ön koşulu SKILL'de atlanmış |
| 17 | mevzuat_getir | TCK m.73 | f.1 altı ay; f.2 öğrenme + hakarette 2 yıl tavanı (7531/14); f.4 vazgeçme düşürür / kesinleşme sonrası infaza engel değil; f.5 iştirakte kapsar; f.6 kabul etmeyeni etkilemez; f.7 şahsi haklardan vazgeçme. UYUMLU |
| 18 | mevzuat_getir | TCK m.66 | üst sınıra göre kademeli dava zamanaşımı. UYUMLU |
| 19 | mevzuat_getir | HMK 6100 m.165 | f.1 "bekletilebilir" (takdirî); f.2 süre / vazgeçmiş sayılma. UYUMLU |
| 20 | mevzuat_getir | TBK 6098 m.74 | hukuk hâkimi kusur/ayırt etme gücünde ceza sorumluluk hükümleriyle ve beraatla bağlı değil; kusur değerlendirmesi ve zarar belirlemesi bağlamaz. SKILL yönü DOĞRU |
| 21 | mevzuat_getir | TBK m.72 | 2 yıl / 10 yıl; ceza kanunu daha uzun zamanaşımı → o uygulanır. UYUMLU |
| 22 | ictihat_ara | Y3HD E.2018/3527 K.2018/6337 | 1 hit, 05.06.2018 — VAR |
| 23 | ictihat_ara | Y4HD E.2015/11693 K.2015/13705 | 1 hit, 26.11.2015 — VAR |
| 24 | ictihat_ara | Y1HD E.2019/128 K.2021/664 | 1 hit, 09.02.2021 — VAR (tam metin bu turda okunmadı; SKILL zaten "snippet düzeyi, kullanım anında DAMGA" diyor) |
| 25 | ictihat_getir | 131846700 (Y4HD) | "beraat bağlayıcı değilse de ceza mahkemesince belirlenecek maddi olgular hukuk hakimi yönünden bağlayıcıdır" — SKILL (b) ekseni ile UYUMLU |
| 26 | ictihat_getir | 427818600 (Y3HD) | "mahkumiyet kararı ve belirlenen maddi olgular hukuk hakimi yönünden bağlayıcıdır" — UYUMLU |

"— teyit" etiketli çıpalar (CMK m.153, TCK m.52, TCK m.267) bu turda da okunmadı; belgede etiket mevcut → m.4 uyumlu.

## Hukuki mantık
- Sonuç haritası: beraat ≠ en olası; HAGB "beraat değildir" ve 7589 rejimi doğru; uzlaştırma/etkin pişmanlık ile beraat tezi çelişkisinin iç analizde tutulması doğru; kademeli netice-i talep tutarlı.
- Beyan protokolü: sistem karar vermez, "Avukat Kararı Bekleyen" — anayasal ayrıma uygun; susma aleyhe yorumlanamaz ilkesi doğru.
- Köprü: TBK m.74 yönü doğru, "mutlak yazılmaz" uyarısı yerinde; m.72/1 uzun zamanaşımı doğru; m.73/7 ve m.253/19 fiyatı doğru.
- m.7: gerçek kişi/dosya adı yok (test dosyası dahil). description uzunluğu değişmemiş (YAML `>-` gövdesi; test kapsamı uygulayıcıda).

## HÜKÜM: ONAY (kritik 0; küçük 3 — m.253/3 önödeme istisnası, m.50/3 ön koşul, m.272/3 parantezi).

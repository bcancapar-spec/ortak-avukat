# v0.5.16/I4 — Yargı Pro teyit izi (hakem; 2026-09-07)

Taban: 80ac847. Yöntem: diff'e giren her BENZERSİZ (kanun, madde) çifti için tek `mevzuat_getir`; içtihat künyeleri için `ictihat_ara` (esas+karar, ISTINAFHUKUK) + `ictihat_getir` tam metin. Müvekkil/kişi/dosya verisi yok (m.7). Kod düzeltilmedi, test koşulmadı.

## Sorgular — mevzuat_getir
HMK (mevzuatgov:kanun:5:6100): m.6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 21, 22, 23, 77, 114, 115, 116, 117, 119, 341, 346 — 21 çağrı.
TBK (mevzuatgov:kanun:5:6098): m.49, 60, 72, 112, 146 — 5 çağrı.

| İddia | Sonuç |
|---|---|
| m.6 genel yetki; m.7/1-2 birden fazla davalı / tuzak; m.9 mutad mesken + malvarlığı; m.10 ifa yeri "de"; m.11 miras KESİN; m.12 taşınmaz aynı KESİN; m.13 karşı dava; m.14/1 şube "de", /2 merkez KESİN; m.15/1 mal/riziko "de", /2 can sigortası KESİN; m.16 fiil/zarar/zarar gören yerleşim "de" | HEPSİ UYUMLU |
| m.114/1-ç kesin yetki dava şartı; m.116-117 yetki itirazı ilk itiraz, cevap dilekçesiyle | UYUMLU |
| m.21/1-c, m.22/2, m.23/1-2 alıntıları | BİREBİR UYUMLU |
| m.77 vekâletname kesin süre; m.115/2 giderilebilir dava şartı kesin süre; m.119/2 (a,d,e,f,g) dışı — bir hafta — dava açılmamış sayılır | UYUMLU |
| m.341/346 (BAM kararının dayanağı olarak anılmış) | m.341 istinafa açık kararlar, m.346 dilekçe reddi — BAM metnindeki atıfla aynı |
| TBK m.60 alıntısı; m.49; m.112 kusur karinesi; m.146 on yıl; m.72 iki/on yıl | UYUMLU |
| 492 m.30-32, HMK m.17-18, m.390 | belgede «çıpa / teyit edilmedi» etiketli — kural gereği kritik değil |

## Sorgular — içtihat
| Künye | Sonuç |
|---|---|
| Antalya BAM 4. HD E.2023/126 K.2023/67, 24.01.2023 | VAR, KESİN. Metin: HSK 07/07/2021-608; "gerçekte görevsizlik kararı değil, teknik anlamda bir gönderme kararı"; nihai hüküm değil; yasa yolu kapalı; istinaf HMK 341-346 gereğince USULDEN RET; merci tayini için iade — diff alıntıları birebir |
| Antalya BAM 4. HD E.2023/128 K.2023/76, 24.01.2023 | VAR, KESİN, aynı yönde (HSK 608 + 01/09/2021 uygulama tarihi metinde) |
| Gaziantep BAM 4. HD E.2023/632 K.2023/795, 15.06.2023 | VAR, KESİN. İkinci mahkemenin kararı gerçek görevsizlik (bono vasfı yok → ticari dava değil → asliye hukuk); karşılıklı görevsizlik şartı oluşmadığından GERİ ÇEVİRME — diff özeti doğru |

HSK 608 sayılı karar: Mevzuat MCP (kanun/KHK/yönetmelik kapsamı) ile doğrudan çekilemedi; tarih (07/07/2021), sayı (608) ve uygulama başlangıcı (01/09/2021) üç BAM kararının metninde geçiyor — kamu bilgisi olarak dolaylı teyitli sayıldı.

## Hukuki mantık
- Merci tayini yolu m.21/1-c + m.22/2 ile doğru kurulmuş; "gönderme kararına istinaf kapalı → kesinleşme kendiliğinden" tespiti BAM metniyle uyumlu.
- Küçük: "Talep reddedilirse m.22/1 engel hâli" — m.22/1 YETKİLİ mahkemenin engeli içindir; görev engeli m.21/1-a. Yön yanlış değil, madde eşlemesi gevşek (advisory).
- Tamamlanabilir / tamamlanamaz kusur ayrımı ve "derhâl" yorumu norm metinleriyle tutarlı; script advisory, exit sözleşmesi korunmuş.
- TBK m.60 "en iyi giderim" seçim ölçütleri (zamanaşımı / kusur / ispat / faiz) ve örnek şema (m.112 karine, m.49 davacı ispatlar, m.146 ↔ m.72) doğru yönde.

## m.7
SKILL metinlerinde mahkeme/daire adı ve künye (kamu bilgisi) var; kişi/dosya/müvekkil verisi yok. Testte sentetik künye (E. 2099/1).

## Hüküm
KRİTİK: yok. KÜÇÜK: (1) m.22/1 ↔ m.21/1-a eşlemesi gevşek; (2) HSK 608 yalnız içtihat metninden dolaylı teyit; (3) tests/README OA-SUIT-SAYISI F(1784) / I4(1791) — entegrasyonda çakışır (hukuki değil). → ONAY.
MCP çağrısı (bu grup): 26 mevzuat_getir + 3 ictihat_ara + 3 ictihat_getir.

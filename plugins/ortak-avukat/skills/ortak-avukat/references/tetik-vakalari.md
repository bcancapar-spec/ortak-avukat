# Tetik Vakaları — Kırpma Sonrası Tetik-İsabet Regresyon Kontrol Listesi

Fable kuralı gereği 7 parçanın `description` bloğu ≤800 karaktere tıraşlandı (kardeş-parça
listeleri, anayasal ilke özetleri, playbook detayı ve script adları kesildi; ayırt edici
anahtar kelimeler, olumsuz kapsam sınırı ve oto-tetik cümlesi korundu). Bu tablo, kırpmanın
tetik yüzeyini **daraltmadığını** doğrular: aşağıdaki örnek kullanıcı cümleleri hâlâ beklenen
parçaya isabet etmelidir. Yeni bir tıraş/düzenleme sonrası bu liste elden geçirilir.

| # | Örnek kullanıcı cümlesi | Beklenen parça | Tetikleyen ayırt edici terim |
|---|--------------------------|----------------|-------------------------------|
| 1 | "Bu dosyayı baştan sona ele al, uçtan uca ilerleyelim." | oa-pipeline | uçtan uca / baştan sona |
| 2 | "Tam analiz yap; nereden başlayalım ve nasıl ilerleyelim?" | oa-pipeline | tam analiz / nereden başlayalım |
| 3 | "Evrakları oku, metne çevir; taranmış PDF neden bu kadar token yiyor?" | oa-ingest | metne çevir / taranmış / token |
| 4 | "Klasördeki UYAP evraklarını OCR'la, indeks çıkar." | oa-ingest | UYAP evrak / OCR / indeks |
| 5 | "Tebligat usulsüz görünüyor, dava şartı eksik mi?" | oa-usul | tebligat usulsüz / dava şartı |
| 6 | "Mahkeme görevsiz, harç eksik; ıslah edelim mi?" | oa-usul | görevsiz / harç eksik / ıslah |
| 7 | "İlk itirazları verelim, süresi geçmeden usulden ret isteyelim." | oa-usul | ilk itiraz / usulden ret |
| 8 | "Kim kime nasıl bağlı? İlliyet bağı bir yerde kesiliyor mu?" | oa-illiyet | kim kime bağlı / illiyet bağı |
| 9 | "Neden-sonuç zincirini ve ilişki haritasını çıkar." | oa-illiyet | neden-sonuç / ilişki haritası |
| 10 | "Karşı taraf kesilme savunması yapacak, mağdur kusuru var." | oa-illiyet | kesilme savunması |
| 11 | "Sanık müdafiiyiz; iddianameye karşı savunma dilekçesi yazalım." | oa-mudafii | sanık müdafii / savunma dilekçesi / iddianameye karşı |
| 12 | "Suçun unsurları oluşmadı; beraat, olmazsa HAGB isteyelim." | oa-mudafii | unsurları oluşmadı / beraat / HAGB |
| 13 | "Gözaltı ve tutukluluk var; ifade/sorgu öncesi hazırlık." | oa-mudafii | gözaltı/tutukluluk / ifade-sorgu |
| 14 | "Müşteki vekiliyiz; suç duyurusu ve şikâyet dilekçesi hazırlayalım." | oa-musteki-vekili | müşteki vekili / suç duyurusu / şikâyet dilekçesi |
| 15 | "KYOK'a itiraz edelim; kamu davası açılsın, delil getirtilsin." | oa-musteki-vekili | KYOK itirazı / kamu davası / delil getirtilsin |
| 16 | "Katılma talebi verelim; unsurlar oluştu, delili güvenceye alalım." | oa-musteki-vekili | katılma talebi / unsurlar oluştu |
| 17 | "NDA geldi, klozları incele; bize redline çıkar." | oa-sozlesme | NDA / kloz / redline |
| 18 | "Şu sözleşme taslağını revize et, müzakere pozisyonu kur." | oa-sozlesme | sözleşme / revize / müzakere |
| 19 | "Rekabet yasağı ve münhasırlık klozu geçerlilik sınırında mı?" | oa-sozlesme | rekabet yasağı / münhasırlık |

## Sınır ve ayrım notları (sahte-tetik / kayma önleme)

- **oa-pipeline ↔ oa-ingest:** Yalın "dosyayı işle" → oa-pipeline (genel akış). Bağlamda ham
  evrak, taranmış/görüntü PDF, OCR veya "metne çevir/token" geçiyorsa 0. adımın metin motoru
  **oa-ingest** öne çıkar. İkisi 0. MANİFEST adımını paylaşır; çakışma değil sıralamadır.
- **oa-mudafii ↔ oa-musteki-vekili (ceza dalı aynası):** Ayrım temsil edilen tarafadır.
  **Sanık/şüpheli** temsil ediliyorsa → oa-mudafii (savunma merceği). **Müşteki/mağdur/katılan**
  temsil ediliyorsa → oa-musteki-vekili (iddia merceği). Kullanıcı "müdafii/vekil" demese bile
  taraf belliyse ilgili parça tetiklenir; yanlış tarafın parçası tetiklenmemelidir.
- **oa-usul ↔ oa-sure:** Süre/zamanaşımı/hak düşürücü hesabı → oa-sure. Dava şartı, ilk itiraz,
  görev/yetki, tebligat, harç, ıslah gibi usul denetimi → oa-usul. Kanun yolu süresi ikisini de
  ilgilendirir; süre satırı oa-sure'de, şart denetimi oa-usul'de.
- **oa-illiyet:** "ilişki/bağ/neden-sonuç/illiyet/kesilme" bir dosya, dilekçe veya tez analiz
  edilirken kesişen katman olarak tetiklenir; tek başına sohbet sorusu değil, uyuşmazlık bağlamı
  gerekir.

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır
(5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

# v0.5.16/B — Yargı Pro teyit izi (hakem)

## Ortak teyit izi (Yargı Pro MCP, 2026-09-07)
Önce `kullanici_profili_getir` çağrıldı (1 çağrı). Müvekkil verisi gönderilmedi; sorgular yalnız madde numarası / soyut hukuki terim.

| # | araç | sorgu | sonuç | hüküm |
|---|---|---|---|---|
| 1 | mevzuat_getir | 5237 m.22 | (4) "ceza failin kusuruna göre belirlenir"; (5) "herkes kendi kusurundan dolayı sorumlu olur" — alıntı BİREBİR | UYUŞUYOR |
| 2 | mevzuat_getir | 5237 m.37 | faillik (m.37-39 faillik/azmettirme/yardım başlığı; m.37 metni faillik) | UYUŞUYOR |
| 3 | mevzuat_getir | 6100 m.190 | ispat yükü (1) lehine hak çıkaran taraf; (2) karine | UYUŞUYOR |
| 4 | mevzuat_getir | 6100 m.353 | (1)a esası incelemeden kaldırma+gönderme; (1)b esastan ret / düzelterek yeniden esas | UYUŞUYOR (enumda "yeniden esas hakkında karar" yok — küçük) |
| 5 | mevzuat_getir | 6100 m.370 | onama kararları (+ düzelterek onama) | UYUŞUYOR |
| 6 | mevzuat_getir | 6098 m.19 | muvazaalı işlemler — gerçek ve ortak irade | UYUŞUYOR |
| 7 | mevzuat_getir | 6098 m.52 | zarar görenin kusuru → hâkim tazminatı indirebilir / tamamen kaldırabilir | UYUŞUYOR |
| 8 | mevzuat_getir | 5271 m.280 | (1)a esastan ret, (1)e-f bozma, (2) kaldırarak yeniden hüküm | UYUŞUYOR |
| 9 | mevzuat_getir | 5271 m.302 | temyiz isteminin esastan reddi / bozma | UYUŞUYOR |
| 10 | mevzuat_getir | 1136 m.34 | (Değişik 4667/21) özen, doğruluk ve onur — metin BİREBİR; "bilgilendirme" lafzen yok (belge bunu dürüstçe yazıyor) | UYUŞUYOR |
| 11 | ictihat_ara | C12 +"mağdurun kusuru" +"illiyet bağı" +taksir +"kusur oranı" | 0 sonuç (dar filtre) | — |
| 12 | ictihat_ara | +"taksirle" +"mağdurun kusuru" +"illiyet bağını" | 4 sonuç, tümü 12. CD (2015-2025, taksirle yaralama/öldürme) | "12. CD yerleşik hattı" iddiası künyesiz + "künye KÜTÜKTEN" etiketli → çıpa kuralı sağlanmış; hafızadan künye YOK |
| 13 | ictihat_ara | +"organik bağ" +"tüzel kişilik perdesi" | 39 sonuç; 11. HD 2024 kararı organik bağı perdenin aralanması ölçütü sayıyor | belge künye yazmıyor ("kütükten teyitli karar ile") → uygun |

TCK m.24 vd. belgede "çıpa, bu turda teyit edilmedi" etiketli → teyit istenmedi, kural sağlanmış.
m.7 taraması: diff'lerde yalnız sentetik ("Sentetik A.Ş.", "E. 2099/1") değer; gerçek kişi/dosya adı YOK.

## B'ye özgü hüküm
- Tek hukuki norm: 1136 s. Av.K. m.34 — metin birebir, "bilgilendirme lafzen yok" dürüst okuması doğru; TBB Meslek Kuralları "çıpa — teyit edilmedi" etiketli → kural sağlanmış.
- Hat sırası ANTİTEZ→STRATEJİ mantığı (karşı tez görülmeden yol kararı yok) tutarlı; müvekkil kararı UYARI/bloklamaz ayrımı egemenlik alanıyla uyumlu; m.6 dış çıktı sınıfı doğru işlenmiş.
- Küçük: `HUKUM_SEBEPLERI` = usul|olgu|hukuk|uslup|talep|ictihat|diger — G grubu SKILL.md'de farklı liste yazıyor (bkz. G izi); B tarafında hata yok, G'de düzeltilmeli.

HÜKÜM: ONAY (kritik 0).

# Kıyas Rehberi ve JSON Şeması — oa-kiyas referansı

## Subsumtion (tatbik) mantığı

Türk hukukunda hukuki sonuç, normun somut olaya uygulanmasıyla (subsumtion) doğar.
Açık kıyas bunu üç önermeye böler:

- **Büyük önerme:** Soyut kural. Norm + onu somutlaştıran içtihat. Norm
  **unsurlarına** ayrılır (Tatbestandsmerkmale). Örnekler:
  - Haksız fiil (TBK m.49): fiil · hukuka aykırılık · kusur · zarar · illiyet bağı
  - Sözleşmeye aykırılık (TBK m.112): borç · ihlal · kusur (karine) · zarar · illiyet
  - İstihkak (İİK m.96 vd.): üçüncü kişinin mülkiyet/sınırlı ayni hak iddiası ·
    haczin varlığı · zilyetlik durumu (m.97/a karinesi)
- **Küçük önerme:** Somut maddi vakıa. Her vakıa, büyük önermenin bir veya birden
  çok unsurunu **karşılar** (`karsilar` alanı). Her vakıa delile bağlıdır.
- **Sonuç:** Tüm unsurlar karşılanırsa hukuki sonuç doğar. Karşılanmayan unsur =
  ispat boşluğu veya hukuki dayanak yetersizliği → sonuç o ölçüde zayıflar.

## Norm unsurlarına ayırma — neden kritik

Karşı taraf bütün normu değil, **tek bir unsuru** çökerterek davayı kazanır
(örn. "kusur yok" veya "illiyet bağı kesildi"). Unsurları ayrı yazmak, her birinin
ayrı ayrı ispatlanması gerektiğini ve karşı tarafın nereye vuracağını görünür kılar.
İlliyet bağı unsuru için oa-illiyet grafını kullan.

## JSON şeması

```json
{
  "buyuk_onerme": {
    "norm": "TBK m.49 (Mevzuat MCP'den teyitli)",
    "unsurlar": [
      {"id": "fiil", "ad": "Fiil"},
      {"id": "h_aykiri", "ad": "Hukuka aykırılık"},
      {"id": "kusur", "ad": "Kusur"},
      {"id": "zarar", "ad": "Zarar"},
      {"id": "illiyet", "ad": "İlliyet bağı"}
    ],
    "ictihat": [
      {"kunye": "Y.4.HD E.... K....", "dogrulama": "teyitli"}
    ]
  },
  "kucuk_onerme": {
    "vakialar": [
      {"metin": "Davalı aracıyla kırmızıda geçti", "karsilar": ["fiil","h_aykiri"], "dayanak_delil": ["trafik_tutanagi"]},
      {"metin": "Müvekkil yaralandı", "karsilar": ["zarar"], "dayanak_delil": ["rapor"]}
    ]
  },
  "sonuc": "Fiil/hukuka aykırılık/zarar karşılandı; kusur ve illiyet için ek ispat gerekli."
}
```

## Kullanım
`kiyas.json` yaz, `python scripts/kiyas_denetim.py kiyas.json` çalıştır. Script
karşılanmamış unsuru, delilsiz vakıayı, teyitsiz içtihadı ve yetim vakıayı yakalar.
Yorum ve nihai sonuç avukata aittir.

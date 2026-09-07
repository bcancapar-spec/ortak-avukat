# v0.5.16/F — Yargı Pro teyit izi (hakem; 2026-09-07)

Taban: 80ac847. Yöntem: diff'e giren her BENZERSİZ (kanun, madde) çifti için tek `mevzuat_getir`. Müvekkil/kişi/dosya verisi yok (m.7). Kod düzeltilmedi, test koşulmadı.

## Sorgular (mevzuat_getir, mevzuatgov:kanun:5:6100 — HMK)
| Madde | Diff iddiası | Sonuç |
|---|---|---|
| m.190/1-2 | ispat yükü lehine hak çıkaranda; karineye dayanan yalnız temel vakıayı ispatlar, karşı taraf aksini ispat edebilir | UYUMLU |
| m.200 | parasal sınırı aşan işlemler senetle ispat; karşı tarafın açık muvafakatiyle tanık | UYUMLU (sınır 2.500 TL nominal; belgede sayı yazılmamış — doğru çıpa) |
| m.201 | senede karşı tanıkla ispat yasağı | UYUMLU |
| m.202 | delil başlangıcı varsa tanık dinlenebilir | UYUMLU |
| m.203 | istisnalar: yakın akraba, teamül, imkânsızlık, irade bozukluğu/aşırı yararlanma, üçüncü kişi muvazaası, senet kaybı | UYUMLU (a-e bentleri birebir) |
| m.266 | hâkimlik mesleğinin gerektirdiği hukuki bilgiyle çözülecek konularda bilirkişiye başvurulamaz (6754/49) | UYUMLU |

## Hukuki mantık
- Vakıa iddiası ≠ hukuki iddia; tanık şartlı delil (caizlik fail-closed); karine yük kaydırır (m.190/2); bilirkişi hukuki iddiada delil değil — hepsi madde metinleriyle örtüşür.
- Tanık-tek-delil vakıa iddiasının boşluğa düşmesi ve "yeşil matris"in kırmızıya dönmesi istenen etki; SKILL/script/test docstring tutarlı.

## Hüküm
KRİTİK: yok. KÜÇÜK: yok. → ONAY.
MCP çağrısı (bu grup): 6 mevzuat_getir.

# Yargı Pro teyit izi — v0.5.16 / GRUP H (oa-ictihat: kanun yolu zinciri, iniş ritüeli D1-D3, içtihat haritası)

Hakem: Yargı Pro hakemi (yalnız okuma + MCP). Tarih: 2026-09-07. Taban: 80ac847.
Kapsam: `git diff 80ac847` içindeki .md/.py (tests hariç) dosyalarına giren hukuki norm atıfları.
Müvekkil/dosya verisi yok; sorgular yalnız kanun no + madde no.

## Araç + sorgu + sonuç

| # | Araç | Sorgu | Diffteki iddia | Sonuç |
|---|---|---|---|---|
| 1 | `mevzuat_getir` | 2797 m.45 | «İBK kararları benzer hukuki konularda Yargıtay Genel Kurullarını, dairelerini ve adliye mahkemelerini bağlar» | f.5 aynen bu cümle. UYUŞUYOR |
| 2 | `mevzuat_getir` | 6100 m.341 | «ilk derece nihai kararına karşı istinaf (HMK m.341)» | (1)-a «Nihai kararlar». UYUŞUYOR |
| 3 | `mevzuat_getir` | 6100 m.361 | «BAM dairesi kararına karşı temyiz (HMK m.361)» | (1) BAM hukuk dairelerinden verilen temyizi kabil nihai kararlar. UYUŞUYOR |
| 4 | `mevzuat_getir` | 5271 m.272 | «ceza: istinaf CMK m.272» | (1) ilk derece hükümlerine karşı istinaf. UYUŞUYOR |
| 5 | `mevzuat_getir` | 5271 m.286 | «CMK m.286 — bozma dışı hükümler» | (1) «BAM ceza dairelerinin bozma dışında kalan hükümleri temyiz edilebilir». UYUŞUYOR |

## Hukuki mantık
- Hiyerarşi «İBK > HGK > daire»: İBK bağlayıcılığı m.45'ten; «HGK kararı daire kararının üstünde fiilî ağırlık taşır» ifadesi bağlayıcılık iddiası değil, ağırlık tespiti — doğru ölçülü.
- D1 (BAM'ın kendi dosyasının ilk derece künyesini redakte etmesi), D2 (indeks kapsamı), D3 (esas_no BAM'lar arası tekil değil) olgusal/indeks tespitleridir; hukuki norm iddiası taşımaz. Script hukuki yorum yapmıyor; künyeyi yalnız metinde var olandan çıkarıyor.
- «BAM Ceza Daireleri indekste yok» ifadesi mevcut «Bilinen sınırlar» bölümüne atıf; yeni iddia değil.

## İçtihat künyesi / «yerleşik hat» iddiası
Yok (test fikstürleri «2099/…», «2090/…» sentetik sınıfı; şartname gereği).

## m.7
TCKN / gerçek kişi / gerçek dosya adı taraması: bulgu yok. Mahkeme adları «Örnek …» sentetik.

## Hüküm
KRİTİK: yok. KÜÇÜK: yok. → ONAY (Yargı Pro teyit yönünden).
MCP çağrı sayısı (bu grup için): 5.

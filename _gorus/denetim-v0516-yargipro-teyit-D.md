# Yargı Pro teyit izi — v0.5.16 / GRUP D (oa_hafiza.py akıbet üreticisi + senkron klasör uyarısı, oa-gizlilik)

Hakem: Yargı Pro hakemi (yalnız okuma + MCP). Tarih: 2026-09-07. Taban: 80ac847.
Kapsam: `git diff 80ac847` içindeki .md/.py (tests hariç) dosyalarına giren hukuki norm atıfları.
Müvekkil/dosya verisi yok; sorgular yalnız kanun no + madde no.

## Araç + sorgu + sonuç

| # | Araç | Sorgu | Diffteki iddia | Sonuç |
|---|---|---|---|---|
| 1 | `mevzuat_getir` | 1136 m.36 | «Av.K. m.36 — avukatın görevi dolayısıyla öğrendiği hususları açığa vurması yasaktır (sır saklama)» | Başlık «Sır saklama»; f.1 aynen bu yönde. UYUŞUYOR |
| 2 | `mevzuat_getir` | 6698 m.6 | «KVKK m.6 — sağlık/ceza mahkûmiyeti gibi özel nitelikli veriler ancak sayılı şartlarla işlenebilir (7499/33)» | f.1 sağlık, ceza mahkûmiyeti sayılmış; f.2 mülga 7499/33; f.3 değişik 7499/33 — «işlenmesi yasaktır. Ancak … halinde mümkündür». UYUŞUYOR |
| 3 | `mevzuat_getir` | 6698 m.9 | «KVKK m.9 — yurt dışına aktarım yeterlilik kararı / uygun güvence şartına bağlıdır (7499/34 ile değişik)» | Başlık «Kişisel verilerin yurt dışına aktarılması», (Değişik 2/3/2024-7499/34); f.1 yeterlilik kararı, f.4 uygun güvenceler. UYUŞUYOR |

`references/gizlilik-desenleri.md` içindeki «TCK m.239» satırı önceden mevcuttur (v0.5.16 eklemesi değil); bu turda yeniden teyit edilmedi.

## Hukuki mantık
- «Senkron istemcisinin sunucusu çoğu zaman yurt dışındadır; ‘yalnız yedekliyorum’ beyanı aktarım şartını kaldırmaz» — m.9 aktarımı amaçtan bağımsız düzenler; önerme m.9 metniyle uyumlu (olgusal «çoğu zaman» beyanı hukuki iddia değil).
- Akıbet üreticisi: --akibet yalnız GETİR + --damga ile; kaynak zorunlu; «araç» / «avukat beyanı» sınıfı görünür — m.4/m.5 (uydurma yasağı) ile uyumlu; script akıbetin doğruluğunu iddia etmiyor.

## İçtihat künyesi / «yerleşik hat» iddiası
Yok.

## m.7
TCKN / gerçek kişi / gerçek dosya adı taraması: bulgu yok.

## Hüküm
KRİTİK: yok. KÜÇÜK: yok. → ONAY (Yargı Pro teyit yönünden).
MCP çağrı sayısı (bu grup için): 3.

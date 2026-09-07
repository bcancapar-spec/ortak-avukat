# v0.5.16 / I5 — Yargı Pro (Mevzuat MCP) teyit izi

Hakem: Yargı Pro hakemi (alt-ajan) · Tarih: 2026-09-07 · Taban: 80ac847 · Dal: v0516/I5
Kapsam: `git diff 80ac847` içindeki .md/.py/.json (oa-sure: SKILL.md, sure-cizelgesi.md, hesapla_sure.py, sure_kurallari.json, sure_nobetci.py). Testler koşulmadı. Kod düzeltmesi yok. Müvekkil/dosya verisi yok (m.7).
Araç: `mevzuat_getir` (madde). İçtihat künyesi iddiası diff'te YOK → `ictihat_ara` çağrılmadı.

## Norm teyitleri

| Norm (diff iddiası) | Sorgu | Sonuç |
|---|---|---|
| HMK m.116/1 — katalog: (a) kesin yetki yoksa yetki itirazı, (b) tahkim; (c) 7251 ile mülga | mevzuatgov:kanun:5:6100 m.116 | UYUŞUYOR ((c) Mülga: 22/7/2020-7251/8) |
| HMK m.117/1 — ilk itirazların hepsi cevap dilekçesinde; aksi hâlde dinlenemez; m.117/2-3 | m.117 | UYUŞUYOR |
| HMK m.119/1-f — her vakıanın hangi delille ispat edileceği | m.119 | UYUŞUYOR |
| HMK m.129/1-e — cevap dilekçesinde aynı | m.129 | UYUŞUYOR |
| HMK m.145/1 — süreden sonra delil gösterilemez; istisna (geciktirme amacı yok VEYA kusur yok) → izin verebilir | m.145 | UYUŞUYOR |
| HMK m.139/1-ç — davetiye tebliğinden iki haftalık kesin süre; vazgeçmiş sayılma ihtarı | m.139 | UYUŞUYOR (7251/13 değişik cümle) |
| HMK m.140/5 — ihtara rağmen sunmayan taraf vazgeçmiş sayılır | m.140 | UYUŞUYOR (7251/14 değişik) |
| HMK m.177/1-3 — tahkikat sona erene kadar; bozma/kaldırma sonrası (7251/18); sözlü/yazılı | m.177 | UYUŞUYOR |
| HMK m.176/2 — aynı davada bir kez | m.176 | UYUŞUYOR |
| HMK m.127 — cevap süresi iki hafta (hmk_cevap atfı) | m.127 | UYUŞUYOR |
| CMK m.237/1-2 — hüküm verilinceye kadar katılma; kanun yolunda istenemez | mevzuatgov:kanun:5:5271 m.237 | UYUŞUYOR |

## Hukuki mantık denetimi (aşama tetikli süreler)
- "Tarih üretmek yanlış tarih üretmektir" önermesi ve `hesapla()`ya girmeme kararı doğru; ilk itiraz/delil bildirimi/ıslah/katılma gerçekten takvimsiz, aşama kapatmalı işlemlerdir.
- `hmk_on_inceleme_belge` ÇATAL tasarımı doğru: davetiye tebliğine kadar tarih yok; tebliğle m.139/1-ç iki haftalık kesin süre başlar (`--teblig … --sure 2 --birim hafta`).
- Kol uyuşmazlığı kapısının (A-1) aşama kuralına uygulanmaması tutarlı (adli tatil aritmetiği yok).
- Nöbetçi: aşama kaydını sayıma/acil sınıfına katmama ve `tur: asama` dışı tarihsiz kaydı BOZUK sayma (fail-closed) doğru.
- Ceza deseni (CMK m.237) → hukuk koluna genelleme: madde metinleriyle uyumlu.

## Bulgular
KRİTİK: yok.
KÜÇÜK:
1. `pipeline_adimi` değerleri mevcut ADIMLAR (STRATEJİ 6, ANTİTEZ 7, YAZIM 8) ile yazılmış; SPEC.I2/B grubu antitezi adım 6'ya, stratejiyi 7'ye taşıyor. Entegrasyonda `hmk_islah` (6 = STRATEJİ) etiketi ANTİTEZ'e kayar — sayı değil ad üzerinden eşleme ya da entegratör notu gerekir (hukuki değil, entegrasyon).
2. `hmk_delil_bildirimi` açıklaması "dilekçeler aşaması" diyor; uygulamada ikinci cevap/cevaba cevap (m.136-137) dilekçeleri de bu aşamaya dâhildir — çizelgede tek cümle not faydalı olur.

## Hüküm
I5: ONAY (kritik sıfır).
MCP çağrı sayısı (bu grup için): HMK ×10, CMK ×1.

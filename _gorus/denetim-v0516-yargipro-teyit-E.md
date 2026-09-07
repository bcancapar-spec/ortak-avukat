# v0.5.16 / E — Yargı Pro (Mevzuat MCP) teyit izi

Hakem: Yargı Pro hakemi (alt-ajan) · Tarih: 2026-09-07 · Taban: 80ac847 · Dal: v0516/E
Kapsam: `git diff 80ac847` içindeki .md/.py (oa-ingest README/SKILL/oa_ingest.py; oa-pipeline/scripts/okuma_kapisi.py). Testler koşulmadı. Kod düzeltmesi yok. Müvekkil/dosya verisi yok (m.7).
Araç: `mevzuat_ara` (İİK/6183/İYUK ID çözümü) + `mevzuat_getir` (madde). İçtihat künyesi iddiası diff'te YOK → `ictihat_ara` çağrılmadı. OCR araç hatası kısmı (P0-2) hukuki norm içermez — yalnız mekanik/okundu.

## Norm teyitleri (okuma_kapisi.py SURE_ADAYI_ONERI + SKILL.md 6. adım)

| Norm (diff iddiası) | Sorgu | Sonuç |
|---|---|---|
| HMK m.345/1 — istinaf iki hafta, ilamın tebliğinden | mevzuatgov:kanun:5:6100 m.345 | UYUŞUYOR |
| HMK m.281/1 — bilirkişi raporuna tebliğden iki hafta | m.281 | UYUŞUYOR (7251/24 ek cümle: iki haftayı geçmeyen ek süre — belgede yok, aday notu için yeterli) |
| CMK m.273/1 — istinaf, hükmün gerekçesiyle tebliğinden iki hafta | mevzuatgov:kanun:5:5271 m.273 | UYUŞUYOR (m.273/2 7499 ile mülga — mevcut _dikkat_cmk notuyla tutarlı) |
| İYUK m.7/1 — Danıştay/idare 60, vergi 30 gün | mevzuatgov:kanun:5:2577 m.7 | UYUŞUYOR |
| İYUK m.45/1 — BİM istinaf tebliğden 30 gün | m.45 | UYUŞUYOR (7524 ile kesinlik sınırı 31.000 TL; 7589 (2026) değişiklikleri süreye dokunmuyor) |
| İİK m.62/1 — ödeme emrine itiraz tebliğden 7 gün | mevzuatgov:kanun:3:2004 m.62 | UYUŞUYOR |
| 6183 m.58/1 — amme ödeme emrine itiraz tebliğden 15 gün | mevzuatgov:kanun:3:6183 m.58 | UYUŞUYOR |

## Hukuki mantık denetimi
- "Tebliğ mazbatası süreyi başlatır; hangi sürenin işlediği tebliğ edilen belgeye bağlı" doğru.
- Script `sure-flag` yazmıyor; `--flagsiz` ile hesapla_sure otomatik flag kapısı aşılmıyor — onay disiplini korunmuş.
- OCR'lı evrakta tarih orijinalden teyit şartı doğru.
- `ihbarname` önerisinde kısa süre (vergi 30) önce → güvenli yön.

## Bulgular
KRİTİK: yok.
KÜÇÜK:
1. `SURE_ADAYI_ONERI["odeme_emri"]["kural"] = ["amme_6183_m58"]`: ÖNERİLEN ADIMLAR satırı ilk kuralı komuta gömdüğü için genel haciz (İİK m.62, 7 gün) ödeme emrinde de 15 günlük kural komut olarak basılır — kısa süre yerine UZUN süreyi varsayan (fail-open) yön. Advisory + `--flagsiz` + not sayesinde kritik değil, ama süre telafisizdir: liste boş bırakılıp placeholder'a düşürülmesi ya da notun komuta taşınması önerilir.
2. `gerekceli_karar`/`karar` önerisi hmk_istinaf'ı önce basıyor; ceza/idari dosyada kural ayrımı avukata bırakılmış — İYUK 30 gün > HMK iki hafta olduğundan yön güvenli; not yeterli.
3. HMK m.281/1 ek süre imkânı (7251) aday notunda yok — bilgi amaçlı.

## Hüküm
E: ONAY (kritik sıfır).
MCP çağrı sayısı (bu grup için): HMK ×2, CMK ×1, İYUK ×2, İİK ×1, 6183 ×1, mevzuat_ara ×3.

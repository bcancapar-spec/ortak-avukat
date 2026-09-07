# v0.5.16 / I6 — Yargı Pro (Mevzuat MCP) teyit izi

Hakem: Yargı Pro hakemi (alt-ajan) · Tarih: 2026-09-07 · Taban: 80ac847 · Dal: v0516/I6
Kapsam: `git diff 80ac847` içindeki .md/.py (oa-sozlesme: SKILL.md, kloz-cetveli.md, sozlesme_denetim.py). Testler koşulmadı. Kod düzeltmesi yok. Müvekkil/dosya verisi yok (m.7).
Araç: `mevzuat_getir` (madde, TBK 6098). İçtihat künyesi iddiası diff'te YOK → `ictihat_ara` çağrılmadı. TMK m.9 diff'e girmedi (bağlam satırı) → teyit dışı.

## Norm teyitleri

| Norm (diff iddiası) | Sorgu | Sonuç |
|---|---|---|
| TBK m.117 — muaccel borç, ihtarla temerrüt; birlikte belirlenen/usulüne uygun bildirimle belirlenen günün geçmesiyle | mevzuatgov:kanun:5:6098 m.117 | UYUŞUYOR (metin ayrıca haksız fiil/sebepsiz zenginleşme başlangıçlarını sayar — sözleşme bağlamında atlanması sorun değil) |
| TBK m.118 — kusursuzluğu ispat etmedikçe gecikme zararı | m.118 | UYUŞUYOR |
| TBK m.123 — karşılıklı borçta uygun süre / hâkimden süre | m.123 | UYUŞUYOR |
| TBK m.124 — süre gerektirmeyen üç hâl (durum/tutum; ifa yararsız; kesin vade sözleşmeden anlaşılıyor) | m.124 | UYUŞUYOR |
| TBK m.125 — ifa+gecikme tazminatı / hemen bildirerek müspet zarar / dönme + karşılıklı iade | m.125 | UYUŞUYOR (m.125/3 son cümle: kusursuzluk ispat edilemezse hükümsüzlük zararı da — belgede yok, eksik değil) |
| TBK m.126 — ifasına başlanmış sürekli edimli sözleşmede fesih + erken sona erme zararı | m.126 | UYUŞUYOR |

## Hukuki mantık denetimi (ifa senaryo testi)
- Gecikme senaryosu → m.117/118/123/124; fesih senaryosu → m.125 (ani edimli: dönme) / m.126 (sürekli edimli: fesih) ayrımı doğru kurulmuş.
- "Kesin vade klozu gecikme senaryosunu süre vermeden fesih senaryosuna bağlar" (m.124/3) doğru.
- `bildirim_tebligat` ve `delil_sozlesmesi` kategorilerinin üç senaryonun omurgası sayılması (ihtar/bildirim kanalı; ispat rejimi) m.117 ihtar ve m.125 "hemen bildirerek" ile tutarlı.
- Script nitelendirme yapmıyor; `belirsiz` varsayılanı ve bloklamama (exit sözleşmesi) belgede açıkça yazılı; İNCELEME modunda "calismaz = müvekkil aleyhine tetik" okuma yönü tutarlı.

## Bulgular
KRİTİK: yok.
KÜÇÜK:
1. kloz-cetveli / SKILL: sürekli edimli sözleşmede "fesih" ile ani edimli sözleşmede "dönme" ayrımı doğru; ancak TBK m.126'nın "ifasına BAŞLANMIŞ" şartı SKILL 7. adımda var, cetvelde de var — tamam. Kira/hizmet gibi özel hükümlerin (TBK kira m.315-316, hizmet m.435) genel temerrüt rejimini kısmen dışladığı bir cümleyle çıpalanabilir (özel norm önceliği); yanlış önerme yok.

## Hüküm
I6: ONAY (kritik sıfır).
MCP çağrı sayısı (bu grup için): TBK ×6.

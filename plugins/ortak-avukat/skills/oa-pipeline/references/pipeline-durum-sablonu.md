# Pipeline Durum Şablonu — oa-pipeline referansı

Uzun/çok oturumlu bir dosyada akışın nerede olduğunu izlemek için `pipeline-durum.md`
olarak tutulur. Hangi adımların bittiğini, hangi çıktının üretildiğini ve hangi
kavşakta avukat onayı beklendiğini gösterir.

## Şablon

```markdown
# Pipeline Durumu — [Dosya / taraflar]
Güncelleme: [tarih]

## Adım durumu
| # | Adım | Parça | Durum | Çıktı |
|---|------|-------|-------|-------|
| 1 | ALIM | oa-interview/illiyet/sure | ✓ bitti | illiyet grafı + süre: istinaf 2 hafta |
| 2 | KONUMLAMA | oa-alan | ✓ bitti | İİK m.97; İcra Hukuk Mah. |
| 3 | ARAŞTIRMA | oa-ictihat/arsiv | ⏳ sürüyor | 3 emsal teyitli, 1 bekliyor |
| 4 | OLGU/DELİL | oa-vakia | ⬜ başlamadı | — |
| 5 | KIYAS | oa-kiyas | ⬜ | — |
| 6 | ANTİTEZ | oa-antitez | ⬜ | — |
| 7 | STRATEJİ | oa-strateji | ⬜ | — |
| 8 | YAZIM | oa-dilekce | ⬜ | — |
| 9 | KONTROL | oa-kontrol | ⬜ | — |

## Bekleyen avukat kararı (kritik kavşak)
- [ ] [Kavşak açıklaması — ör. "zilyetlik delili zayıf, dava mı sulh mu?"]

## Bekleyen müvekkil kararı (P1-9, v0.5.16 — karar müvekkilindir)
- [ ] [Konu — seçenekler: a | b | c] (`pipeline_kayit.py --muvekkil-karari "<konu>" --secenekler "a|b|c"`;
      kapatma `--muvekkil-karari-kapat "<konu>" --karar "<seçim>" --gerekce "…"`; bilgilendirme notu:
      `muvekkil-bilgilendirme-sablonu.md`)

## Avukat hükümleri (A-28 sensörü — teslim sonrası, ölçer; kapı değildir)
- KABUL n / REVİZYONLA n / RET n — kaynak `_oa/defter/avukat-hukmu.jsonl`

## Açık riskler / süre uyarıları
- ⏰ İstinaf süresi: [son gün]
- ⚠ [yük taşıyan eksik delil / dispozitif risk]

## Toplanan teyitli künyeler (araştırma çıktısı — sonraki adımlar bununla sınırlı)
- [künye 1 — kaynak: Yargı Pro]
- [künye 2 — kaynak: Mevzuat MCP]
```

## Kurallar
- **Künye tutarlılığı:** 8. adımda (yazım) kullanılan her künye bu listede olmalı.
  Listede olmayan künye belirirse = uydurma şüphesi, dur ve teyit et.
- **Süre üstünlüğü:** süre uyarısı varsa diğer adımların önüne geçer.
- **Kavşak onayı:** "bekleyen avukat kararı" kutusu doluyken pipeline kendiliğinden
  ilerlemez; avukat işaretler.
- **Hat sırası (v0.5.16/P0-3):** 6 = ANTİTEZ, 7 = STRATEJİ — karşı tarafın en güçlü tezi
  görülmeden yol kararı verilmez. ≤v0.5.15 defterlerindeki eski sıra `pipeline_kayit.py`
  tarafından yeni hücreye eşlenir («eski hat sırası ≤v0.5.15 — adım eşlendi» notu).
- **Müvekkil kararı:** avukat kararından ayrı egemenlik alanıdır; kapanmamış müvekkil
  kararı varken KAPANIŞ görünür UYARI üretir (bloklamaz).

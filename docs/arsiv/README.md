# Arşiv — tarihî saha karneleri, denetim ve ölçüm kayıtları

Bu dizin, deponun **geçmişine** ait kayıtları tutar: her dosya kendi tarihini ve
sürümünü taşır ve geriye dönük olarak yeniden yazılmaz. Güncel durum için
[STATUS.md](../../STATUS.md), sürüm zinciri için [CHANGELOG.md](../../CHANGELOG.md),
ilkeler için [ANAYASA.md](../../ANAYASA.md) okunur. Dosya kimlikleri anayasa m.7
gereği anonimdir; saha kayıtları yalnız saha etiketiyle (307, 1865, 923…) anılır.

2026-10-15 denetiminde kök dizinden buraya taşındı (gerekçe: kök dizinde 23 Markdown
dosyası vardı, 13'ü tarihî kayıttı; vitrine ilk bakan hukukçu güncel ile geçmişi
ayırt edemiyordu). Bağlantılar `tests/test_belge_baglantilari.py` ile denetlenir.

| Dosya | Ne anlatır | Dönem |
|---|---|---|
| [KARNE-307.md](KARNE-307.md) | Derdest bir dosyada ikinci cevap dilekçesinin üç kollu adli analizi (transkript + artefakt + mekanizma) | 2026-08, v0.5.9.1 |
| [KARNE-1865.md](KARNE-1865.md) | İdari yüksek yargıda soruşturma-izni itirazı; çok oturumlu çalışma karnesi | 2026-08, v0.5.10 → 0.5.11 |
| [SAHA-SONUCU.md](SAHA-SONUCU.md) | Tek promptla gerçek istinaf dosyası: ölçülmüş saha sonucu | 2026-08-07 |
| [BASARI.md](BASARI.md) | Aynı koşunun anlatı hâli ("bir gecenin hikâyesi") | 2026-08 |
| [SAHA-DENEYLERI.md](SAHA-DENEYLERI.md) | Dokuz belgeli saha koşusunun tam kaydı | v0.5.x |
| [OLCUMLER.md](OLCUMLER.md) | Token, süre ve verim ölçümleri | v0.5.x |
| [HEYET-KARARLARI-v0513.md](HEYET-KARARLARI-v0513.md) | Üç bağımsız denetim heyetinin kararlarının infazı | v0.5.13 |
| [DENETIM-v0514.md](DENETIM-v0514.md) | 62 bulgulu denetimin infazı | v0.5.14 |
| [DENETIM-v0516.md](DENETIM-v0516.md) | İki bağımsız dış denetimin infazı | v0.5.16 |
| [KURULUM-SENKRON.md](KURULUM-SENKRON.md) | Depo ile çalışan araç arasındaki sürüm senkronu (tarihî belge, v0.5.0 dönemi) | 2026-07 |
| [TEST-KULLANIM.md](TEST-KULLANIM.md) | Prova döneminde fork'un ayrı kullanımı (kapandı) | 2026-09 |

Yaşayan iki defter arşivde değil, bir üst dizindedir:
[docs/PERFORMANS-STATUS.md](../PERFORMANS-STATUS.md) (kanca gecikmesi ölçüm defteri — her
sürümden önce tazelenir) ve [docs/SICRAMA-NOTU.md](../SICRAMA-NOTU.md) (uygulanmamış mimari
fikrin ve neden uygulanmadığının kaydı; avukat hükmü sensörünün dayanağı).

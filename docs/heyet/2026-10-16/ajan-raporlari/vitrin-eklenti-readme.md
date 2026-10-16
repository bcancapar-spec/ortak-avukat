# Ajan raporu — vitrin: eklenti README'si katmanlı düzende

**Tarih:** 2026-10-15 · **Commit:** `8a1c882` · **Dal:** `denetim/fable-2026-10-15` · **Push:** yok.
**Kaynak:** vitrin alt oturumunun devir notu. Bu dosya beyandır; heyet ağaçta doğrular.

## Ne değişti

- `plugins/ortak-avukat/README.md` 615 → 690 satır; başlık bazında dilimlenip yeniden kuruldu
  (korunan bloklar kaynaktan kesildi, elle yeniden yazılmadı; CRLF korundu). Yeni sıra: künye →
  kısa giriş + okuyucu yönlendirme tablosu → "Bir bakışta — ne yapar, ne yapmaz" → "Bir dosya
  önünüze geldiğinde ne oluyor" (hat özeti + yedi adım katlanır) → DÜSTUR → Kurulum → Parça dizini
  (özet tablo: Rol · Hatta yeri · Script) + katlanır tam katalog → Sistemin yapmadıkları →
  Güncelleme notları (v0.6.0 ve 2026-10-15 denetim bağlantıları; v0.5.18 notları katlanır).
- Düşen metin: "Bu nedir"in ilk iki paragrafı (kök README ile aynıydı; özü girişe sıkıştırıldı).
  Üçüncü paragraf (Lego mimarisi) Parça dizininin önsözü oldu.
- **Ölçüm bulgusu:** eski "Parça dizini" tablosunda üç script sayısı bayattı: oa-pipeline 10 →
  diskte 11, oa-ingest 5 → 6, çekirdek "—" → 1 (`oa_kurulum.py`).
- Yeni test `tests/test_eklenti_vitrini.py` (4 test): tabloyu `skills/<parça>/scripts/*.py`
  sayımına, katmanlı düzene ve iki belge bağlantısına kilitler. OA-SUIT-SAYISI 3781 → 3785;
  `satir_sayaci --yaz` iki README'nin künye satırını tazeledi (yalnız test sayısı değişti).

## Koşulan kapılar (beyan)

| Kapı | Sonuç |
|---|---|
| Tam süit `-n auto`, CI kipi | 3772 geçti · 12 ortam gerekçesiyle atlandı · 0 kırmızı (82,7 s) |
| perf kanaryası | 1 geçti |
| ruff | temiz |
| aile yapı denetimi | TEMİZ (20 parça) |
| bağlantı kapısı | 0 kırık |
| yedi kapı dosyası + yeni test | 82 yeşil |

## Üst oturuma bırakılanlar (sonradan `08aef92` ile kapatıldı; heyet doğrular)

1. Kök README'de aynı bayatlık: katlanır katalogda "oa-pipeline · 10 script" ve
   "oa-ingest · 5 script" başlıkları (ölçüm 11 ve 6); sayım kök kataloğa genişletilecekti.
2. Kayıtlar: CHANGELOG "Sürümsüz" kaydının "Vitrin" maddesine bir cümle; DENETIM §6'ya Görev 5
   devamı satırı. Bu oturum kayıt dosyalarına dokunmadı.

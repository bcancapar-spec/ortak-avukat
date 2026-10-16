# Ajan raporu — oa-ingest: Excel'de gizli satır/sütun ve yazı rengi (v0.5.19 kalemi)

**Tarih:** 2026-10-15 · **Commit:** `934e212` · **Dal:** `denetim/fable-2026-10-15` · **Push:** yok;
sürüm numarası ve birleştirme avukat kararı.
**Kaynak:** Excel gizli katman oturumunun devir notu. Bu dosya beyandır; heyet ağaçta doğrular.

## Ne değişti

14 dosya: `belge_guvenlik.py` (+553), yeni `tests/test_v0519_excel_gizli_katman.py` (28 test),
`tests/test_v0518_eksikler.py` (Excel uçtan uca testi yeni sözleşmeye), README, oa-ingest SKILL.md
ve parça günlüğü, SURUM-0.6.0, SOZLUK, CHANGELOG (sürümsüz 2026-10-15 kaydına madde), YOL-HARITASI
ve STATUS (kalem kapatıldı), DENETIM-2026-10-15 kapsam notu, `tests/README.md` OA-SUIT-SAYISI 3813,
satır sayacı tazelendi. Commit yalnız bu 14 dosyayı içerir (pathspec ile; paylaşılan ağaçta başka
oturumun açık işi vardı).

## Tasarım kararları

1. `.xlsx`: openpyxl tam kip (`read_only=False`). Ölçülen: `row_dimensions.hidden` ve
   `height == 0`; `column_dimensions.hidden` ve `width == 0`; yazı rengi ↔ dolgu kontrastı < 1,5
   (tema eşlemesi, dizinli renk, tint yaklaşımı); `;;;` ve `;;` biçimi; punto ≤ 2. Koşullu biçim
   aralığındaki açık renkli yazı ZAYIF (yalnız talimat diliyle) — DOCX koyu şekil kuralı.
2. `.xls`: xlrd `formatting_info=True` — satır/sütun gizliliği, palet rengi, düz dolgu, biçim,
   punto. xlrd koşullu biçimi okumaz → ZAYIF ayrımı yok (günlükte). Biçim bilgisi açılamazsa /
   xlrd yoksa → eskisi gibi DENETLENEMEZ (sebepli).
3. Değer silinmez/düzeltilmez: gizli parça okuyucunun yazdığı satırla sırayla eşlenip kesin
   konumda damgalanır; `_damgasiz(yeni) == metin` her senaryoda kilitli.
   `_tablo_hucre_metni` = `oa_ingest._tablo_hucre` (testle kilitli; oa_ingest import edilmez,
   kapı hafif kalır).
4. Önce kırmızı: 27 test kırmızı görüldü, sonra uygulama; bir ek kırmızı (sayfa başlığı taklidi)
   → bölümler regex'le kesilmiyor, sırayla eşleniyor; taklit satır görünür kalır ve
   `isaret-taklidi` alır.
5. Karar seviyeleri: `gizli-sayfa` / `gizli-satir` / `gizli-sutun` / `gizli-bicim` UYARI (AGIR
   değil: resmî dökümde gizli yardımcı satır olağan); `gizli-metin` (kontrast/punto) BULGU;
   gizli katmandaki talimat `gizli-talimat` BULGU; `gizli-hucre-ozeti` sayfa başına 8'den
   fazlasının özeti (İFŞA dilekçesine boş alıntı girmesin).
6. Fail-closed: okuyucu yok / boyut sınırı (`AZAMI_TABLO_XML_BAYT` 128 MB, `AZAMI_XLS_BAYT`
   64 MB) / parça sınırı / eşleşmeme → kalan metin `⟦DENETLENEMEDİ (tablo: … ölçülemedi)⟧`.
   Kapı `SURUM` 1.2 kaldı: Excel kayıtları önbellekte işaretsizdi, yeni kodla kendiliğinden
   yeniden taranır; öbür biçimler yeniden taranmaz.

## Koşulan kapılar (beyan; izole: HEAD + yalnız bu dosyalar, geçici worktree)

| Kapı | Sonuç |
|---|---|
| Tam süit | 3800 geçti · 12 atlandı · 0 kırmızı (3 dk 13 s) |
| perf kanaryası | 1 geçti |
| `aile_dogrula` | TEMİZ |
| `ruff check .` | temiz |

## Ölçüm

- Sentetik 100.000 × 6 hücre (30,7 MB sayfa XML'i): tam kip yükleme 4,1 sn + hücre geçişi 0,4 sn.
- Gerçek evrak: eldeki evrak klasörlerinde yalnız tek gerçek `.xls` vardı (3,7 bin hücre) →
  temiz, 36 ms. Saha kalibrasyonu AÇIK (YOL-HARITASI/STATUS'a yazıldı).

## Açık / dürüst sınır

- Gerçek Excel evrakıyla kalibrasyon (yanlış alarm oranı, özellikle beyaz yazı BULGU seviyesi).
- Ölçülmeyenler (belgelerde yazılı): koşullu biçimin koşulu, degrade/desenli dolgu, hücre
  üstüne çizilmiş şekil/grafik, `General;;;` gibi kısmi gizleyen biçim.

## Paylaşılan çalışma kopyası uyarısı (2026-10-15 itibarıyla)

Aynı worktree'de başka oturumun açık işi vardı; paylaşılan kopyada tam süit o sırada KIRMIZI idi
(89 başarısız: hepsi o dosyaların kapsamında + `test_b35` işaretçi uyuşmazlığı — izlenmeyen test
dosyaları toplamı 3848'e çıkarıyor, işaretçi 3813). Bu değişiklik izole kopyada yeşil.

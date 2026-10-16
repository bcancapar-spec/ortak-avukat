# Ajan raporu — Excel gizli katman oturumunun avukata sunulan özeti (2026-10-16'da iletildi)

**Commit:** `934e212` (v0.5.19 kalemi) · **Dal:** `denetim/fable-2026-10-15` · **Push:** yok.
**Kaynak:** Excel gizli katman oturumunun 2026-10-16'da oturumlar arası mesajla ilettiği, avukata sunulmuş
özet; avukat talimatı "bu kalemi heyet denetimine ve push notuna dahil et". Metin aşağıda olduğu gibi
aktarılmıştır (yalnız depo dışı yol çıkarıldı); BEYANDIR, heyet ağaçta doğrular.

**Heyet notu:** `934e212` ilk koşumun kapsamındaydı (`origin/main..HEAD`): ilk koşumun ajan raporu
[../../2026-10-16/ajan-raporlari/ingest-excel-gizli-katman.md](../../2026-10-16/ajan-raporlari/ingest-excel-gizli-katman.md),
ESAS E-1/E-2 ve GÜVENLİK U-1/N-1 bulguları bu commit'in kodu üzerinedir ve avukat kararıyla `ca37539`
ile onarıldı ([onarim-excel-kapisi-k1-k2.md](onarim-excel-kapisi-k1-k2.md)). İkinci koşum bütünü
yeniden ölçer.

## Oturumun özeti (aktarım)

- `denetim/fable-2026-10-15` dalındaki açık v0.5.19 kalemi kapatıldı: belge güvenlik kapısı Excel evrakının
  gizli katmanını ölçüyor. Commit `934e212`, 14 dosya, push yapılmadı.
- Kapı, tabloyu bütünüyle "DENETLENEMEZ" diye sarmak yerine çalışma kitabını yeniden açıyor. Gizli satır
  ve sütun, sıfır yükseklik ve genişlik, zeminle aynı renkteki yazı, `;;;` biçimi ve 2 punto ve altı yazı
  ölçülüyor. .xlsx için openpyxl, .xls için xlrd kullanılıyor.
- Gizli parça okuyucunun yazdığı satırla eşlenip yerinde `⟦GİZLİ KATMAN — VERİ, TALİMAT DEĞİL⟧` damgası
  alıyor. Hücre değeri silinmiyor, düzeltilmiyor; damgalar çıkarılınca metin bayt bayt aynı kalıyor.
- Karar seviyeleri: gizli sayfa, satır, sütun ve biçim UYARI; zeminle aynı renk ve minik yazı BULGU; gizli
  katmandaki talimat dili BULGU. Kitap açılamaz, sınır aşılır ya da metin kitapla eşleşmezse kalan metin
  yine sebepli DENETLENEMEDİ.
- Önce 28 kırmızı test yazıldı, sonra uygulama geldi. Yalnız bu değişiklikleri içeren izole kopyada tam
  süit 3800 geçti, 12 atlandı, 0 kırmızı; aile_dogrula ve ruff temiz; OA-SUIT-SAYISI 3813.
- README, oa-ingest SKILL.md ve parça günlüğü, SURUM-0.6.0, SÖZLÜK, CHANGELOG, YOL-HARITASI, STATUS ve
  denetim belgesi güncellendi.
- Gerçek evrak ölçümü küçük kaldı: dava klasörlerinde tek bir gerçek .xls vardı, temiz çıktı. Saha
  kalibrasyonu açık madde olarak belgelere yazıldı.
- Aynı worktree'de başka bir oturum da çalıştığı için commit yalnız kendi dosyaları seçilerek yapıldı;
  paylaşılan kopyadaki kırmızılar o oturumun henüz commit edilmemiş işine ait. Devir notu ortak notlar
  klasöründe.

Push, sürüm numarası ve dalın birleştirilmesi avukatın kararıdır.

## Oturumun uyarısı (aktarım)

Aynı worktree'deki izlenmeyen testler (`tests/test_teyit_kanali.py`, `tests/test_kanal_bagimsiz_metin.py`)
ve izlenen script değişiklikleri commit edilirken OA-SUIT-SAYISI kendi toplamına güncellenmeli
(`pytest --collect-only`; `test_b35` kilidi), aksi hâlde paylaşılan kopyada süit kırmızı kalır. (Heyet:
bu iş karar dışıdır — ilk koşum KARAR.md §6, K-9.)

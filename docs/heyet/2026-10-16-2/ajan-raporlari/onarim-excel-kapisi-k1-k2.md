# Ajan raporu — onarım oturumu: Excel kapısı K-1 / K-2 (heyetin push öncesi şartları)

**Tarih:** 2026-10-16 · **Commit:** `ca37539` · **Dal:** `denetim/fable-2026-10-15` · **Push:** yok.
**Kaynak:** onarım oturumunun (ilk koşumun orkestrası) kendi kaydı; avukat kararı "push etme, önce K-1 ve
K-2, tam süit ve heyet yeniden". Bu dosya beyandır; heyet ağaçta doğrular.

## Ne değişti (9 dosya, +128 / −23)

- `plugins/ortak-avukat/skills/oa-ingest/scripts/belge_guvenlik.py`:
  - **K-1** — yeni `_xlsx_var_olan_hucreler(ws)`: openpyxl tam kip hücre sözlüğü `ws._cells` üzerinden
    satırları artan sırada, `iter_rows()` ile aynı sütun uzayında (1. sütundan satırın son var olan
    hücresine; boş koordinat `None`) verir. `_xlsx_satirlar` artık `ws.iter_rows()` çağırmaz; kuyruk boş
    hücre kuralı, gizli satır/sütun kümeleri ve okuyucu eşlemesi değişmedi. `_cells` yoksa
    `AttributeError` dış kapıda DENETLENEMEDİ olur (fail-closed; openpyxl 3.1.5'te var).
  - **GÜVENLİK N-1** — `_xlsx_sayfalar` boyut ön denetimi `xl/worksheets/*.xml` yerine `xl/` altındaki her
    girdinin açılmış toplamını sayar; sabit `AZAMI_TABLO_XML_BAYT` adı ve 128 MB değeri aynı, açıklaması
    güncellendi; hata iletisi "açılmış xl/ içeriği".
  - **K-2** — `ws.tables` içinde stil adı taşıyan her tablonun `ref` aralığı, koşullu biçim aralıklarıyla
    aynı ZAYIF listesine girer (`(CellRange, "tablo stili altında")`); o aralıktaki düşük kontrastlı yazı
    yalnız talimat diliyle bulgudur. Başka karar seviyesi değişmedi.
- `tests/test_v0519_excel_gizli_katman.py` +3 (bölüm "(6) heyet 2026-10-16"): ızgara kilidi
  (`Worksheet.iter_rows` monkeypatch ile patlatılır; zamanlama assert'i yok — depo kuralı), `xl/` toplamı
  (sayfa XML'i tam sınırda, bütün aşıyor → DENETLENEMEZ), tablo stili (temiz beyaz başlık → rapor yok;
  başlıkta talimat dili → BULGU `gizli-talimat`). Önce kırmızı görüldü: DENETLENEMEZ / `rapor is None`
  başarısız / BULGU; sonra yeşil.
- Dürüst sınır metinleri: `oa-ingest/SKILL.md` satır 46 (tek satır) ve kök `README.md` dürüst sınırlar
  (3 → 4 satır): tablo stili zemini okunmaz, .xls'te ikisi de okunamaz.
- Kayıt: oa-ingest `references/degisiklik-gunlugu.md` 2026-10-16 kaydı; CHANGELOG "Sürümsüz" Heyet maddesine
  "Onarım" cümlesi; STATUS 2026-10-16 notuna avukat kararı; `tests/README.md` OA-SUIT-SAYISI 3813 → 3816;
  iki README künyesi `satir_sayaci --yaz` ile (eklenti kodu 48.000+ → 49.000+: temiz kopyada 49.022 satır).

**SKILL.md sahneleme notu:** paylaşılan ağaçta `SKILL.md` başka oturumun açık hunk'larını (satır 48, 88,
91) taşıyor. Bu oturum yalnız 46. satırı değiştirdi ve commit'e HEAD tabanlı bir kopya (HEAD + yalnız bu
cümle) `git hash-object` / `git update-index --cacheinfo` ile sahnelendi; `git show ca37539 -- …SKILL.md`
tek satır fark gösterir. Çalışma kopyasında diğer oturumun hunk'ları aynen duruyor.

## Ölçüm (bu makine, Python 3.14.8; kapı tepe belleği tracemalloc)

| Senaryo | Dosya | Okuyucu | Kapı ÖNCE (heyet ölçümü) | Kapı SONRA | Karar |
|---|---|---|---|---|---|
| taban (3 satır) | 4,9 KB | 0,00 s | 0,01 s / 0,3 MB | 0,01 s / 0,3 MB | temiz |
| + stilli uzak hücre satır 3000 × sütun 600 | 5,0 KB | 0,00 s | 6,29 s / 400 MB | 0,01 s / 0,3 MB | temiz |
| + stilli uzak hücre satır 20.000 × sütun 100 | 5,0 KB | 0,01 s | 6,29 s / 401 MB | 0,01 s / 0,3 MB | temiz |

Tablo stili (TableStyleMedium2, beyaz kalın başlık satırı): önce karar BULGU (3 `gizli-metin`, örnekler
başlık metinleri) → sonra rapor yok; başlıkta talimat dili → BULGU `gizli-talimat` (ZAYIF yolu).

## Koşulan kapılar

| Kapı | Ortam | Son satır |
|---|---|---|
| Üç yeni test (önce) | paylaşılan ağaç, yalnız bu dosya | `3 failed, 28 deselected` |
| Üç yeni test (sonra) | aynı | `3 passed, 28 deselected` |
| Excel + eksikler + belge_guvenlik + guvenlik_incelemesi | paylaşılan ağaç, `-n auto` | `195 passed in 13.05s` |
| Tam süit `-n auto -m "not perf"` | varsayılan checkout'lu geçici temiz worktree (HEAD `47372fc` + bu dosyalar) | `3803 passed, 12 skipped in 174.18s` |
| perf | aynı | `1 passed` |
| toplanan | aynı | `3816 tests collected` = OA-SUIT-SAYISI 3816 |
| `ruff check .` | aynı | `All checks passed!` |
| `aile_dogrula.py` | aynı | `AİLE YAPI DENETİMİ TEMİZ.` (20 parça) |
| `satir_sayaci.py --yaz` | aynı | `güncel` ×2 |

Geçici worktree'ler (`onarim-tmp`, `onarim-tmp2`, `onarim-tmp3`) kaldırıldı; `git worktree list`'te yok.

## Not — satır sonuna duyarlı test (bu değişiklikle ilgisiz; heyete veri)

`-c core.autocrlf=false` ile açılan (LF) geçici kopyada tam süit `1 failed, 3802 passed`: kırmızı
`tests/test_v0511_kit_guvenlik.py::test_yonlu_tazelik_ozdes_sessiz`; aynı test yamasız HEAD `47372fc`'de
de kırmızı (3 deneme + yamasız 1), varsayılan (CRLF) checkout'ta HEAD'de ve onarımla yeşil. Sebep: test
`_kanal_udf_yaz_icerigi()` içeriğini `read_text` / `write_text` ile kopyalıyor; Windows'ta `write_text`
LF'yi CRLF'ye çevirir, kaynak dosya LF ise bayt-özdeşlik bozulur ve `_bayat_arac_uyarisi` "nesli
doğrulanamadı" der. CI (Linux; LF → LF) ve CRLF checkout etkilenmez. Öneri (ayrı kalem): testin
`write_bytes(read_bytes())` kullanması.

## Commit'lenmemiş iş (karar dışı) — değişmedi

Başka oturumun 9 izlenen + 3 izlenmeyen dosyası (ilk koşum KARAR.md §6) çalışma ağacında aynen duruyor;
dokunulmadı. Paylaşılan ağaçta `test_b35` bu yüzden kırmızıdır (toplanan ≠ 3816); commit'li ağaçta yeşil.

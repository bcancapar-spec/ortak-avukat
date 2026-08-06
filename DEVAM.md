# DEVAM NOTU — v0.5.6.1 (yarım kaldı)

**Durduruldu:** internet kesintisi öncesi, tam test koşusu sırasında.
**Taban:** `1ddd614` (v0.5.6, sizin commit'iniz) — üstüne çalışıldı, HENÜZ COMMIT YOK.

## Yapılan (dosyalar diske yazıldı, kayıp yok)

| Dosya | Ne yapıldı |
|---|---|
| `plugins/ortak-avukat/.claude-plugin/plugin.json` | `"hooks": "./hooks/hooks.json"` GERİ KONDU (v0.5.6'da silinmişti → 4 tetik ölüydü) · sürüm 0.5.6.1 |
| `plugins/ortak-avukat/hooks/hooks.json` | `UserPromptSubmit` eklendi → `--hook-prompt` |
| `.../oa-pipeline/scripts/pipeline_kayit.py` | `hook_prompt()` (devir zorlayıcı) · `_hat_atlandi_uyarisi()` + `_calisma_urunu_var_mi()` (atlanmış hat nöbetçisi) · `--hook-prompt` bayrağı · `hook_denetle`'ye nöbetçi bağlandı · `OA_SURUM=0.5.6.1` |
| `.../oa-kontrol/scripts/teslim_paketi.py` | `OA_SURUM=0.5.6.1` |
| `.claude-plugin/marketplace.json` | sürüm 0.5.6.1 |
| `.../yargi-legal-research-guide/` | anayasa çapası + simülasyon yasağı bloğu + `references/degisiklik-gunlugu.md` |
| `.../yargi-udf-tiff-pdf-guide/` | aynısı |
| `tests/test_devir_zorlayici.py` | YENİ, 10 test |
| `STATUS.md` | YENİ (izlenmiyor, push edilmedi) |

## Doğrulanmış olanlar

- `test_devir_zorlayici.py` → **10/10 yeşil** (tek başına koşuldu)
- `aile_dogrula` → **TEMİZ, 22 parça**
- `--hook-prompt` canlı sınandı: bakir dava klasöründe enjekte ediyor · hat açıksa sessiz · dava klasörü değilse sessiz
- Atlanmış hat nöbetçisi, saha vakasının birebir taklidinde yakaladı

## KALAN TEK İŞ

Tam test koşusu — **bitmedi, sonucu bilinmiyor**. Önceki koşuda 6 kırmızı vardı;
hepsinin sebebi giderildi (4 sürüm damgası ayrışması + 8 `aile_dogrula` hatası),
ama bu **doğrulanmadı**.

```bash
cd "C:/Users/pc/.claude/plug-in/ortak-avukat-main"
unset PYTHONUTF8          # ZORUNLU — avukatın gerçek ortamı cp1254; UTF8 kusuru maskeler
python -m pytest tests -q
```

Beklenen: ~816 geçti / 2 atlandı, 0 kırmızı. Yeşilse:

```bash
git add -A
git commit -F <mesaj-dosyasi>     # PowerShell here-string kırılıyor, -F kullan
git tag -a v0.5.6.1 -m "..."
git push origin main && git push origin v0.5.6.1
```

## Açık karar (kullanıcıya soruldu, cevap alınmadı)

`STATUS.md` bu sürümle GitHub'a gitsin mi, yoksa yerelde mi kalsın?

## Not

İnternet kesintisi testleri etkilemez (yerel koşu) — ama `udf-cli` çağıran
birkaç test ağ ister; bağlantı yokken onlar yanlış-kırmızı verebilir. Bu yüzden
tam koşu bağlantı geldikten SONRA yapılmalı.

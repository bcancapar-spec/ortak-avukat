# Ajan raporu — teyit kanalı alt oturumu: resmî kaynak beyaz listesi, MCP ilanı kaldırıldı

**Commit'ler:** `7764139` (kod + testler), `9e431ac` (canlı metinler kanal-bağımsız), `8998e34` (kayıtlar),
`c94e982` (denetim dalı ucu `66b5d09` kendi içine alındı; 6 çatışma çözüldü) · **PR #10** (taban denetim dalı;
orkestra dalı hızlı ileri aldı — #10 "#9 ile birleşti" notuyla kapatılacak) · **Model:** Fable 5.1. Bu dosya alt
oturumun dönüş raporundan çıkarılmış beyandır; kararın kaynağı dosyalardaki "2026-10-15 avukat kararı" kayıtlarıdır.

## Ne

- **Sözleşme:** eklenti hiçbir MCP sunucusu ilan etmez (`plugin.json` `mcpServers` kaldırıldı, `marketplace.json`
  açıklaması); içtihat/mevzuat teyidinin kanıtı RESMÎ PORTALIN ADRESİ + diske inmiş tam metindir. Beyaz liste tek
  kaynak `oa-kontrol/scripts/kunye_ortak.py` (`RESMI_KAYNAKLAR`, `resmi_kaynak_mi`: listedeki alan adı ya da alt
  alanı, ya da `.gov.tr` soneki; şema http(s); sondan ekleme taklidi reddedilir); avukat nüshası
  `skills/ortak-avukat/references/resmi-kaynaklar.md` (testle özdeş). Kanal hibrittir: model resmî portallara
  Claude Code'un `WebFetch` (GETİR — damga zorunlu) / `WebSearch` (ARAMA) araçlarıyla ulaşır; `oa_hafiza.py teyit`
  tam metin çeken araçlarda `--kaynak-url` ZORUNLU ve beyaz listeli (liste yüklenemezse fail-closed);
  `ictihat_muhakeme_denetim.py` [G7]: dilekçeye dayanak kaydın adresi yoksa ya da liste dışıysa TESLİM ENGELİ,
  dayanak olmayanda UYARI. Araç sözlüğünden üçüncü taraf MCP adları çıkarıldı (kanonik adlar `ictihat_getir`,
  `mevzuat_getir` … kaldı — "ne yaptığını söyler, kimin yaptığını değil"). `oa_kurulum.py` `yargi_pro` adımı →
  `teyit_kanali` (BİLGİ; kurulum gerektirmez). Yerel `oa-kaynak` MCP sunucusu YOL-HARITASI kalemi.
- **Testler:** `tests/test_teyit_kanali.py` (alt oturum beyanı 16; ölçüm: 15 test fonksiyonu / 35 parametreli sınama —
  üçüncü koşum sonrası +3 fonksiyon), `tests/test_kanal_bagimsiz_metin.py` (2; tarihli kayıtlar ve
  `docs/heyet/` muaf), `test_kaynak_url` yeni sözleşme (URL'siz GETİR teyidi fail-closed durur), `test_v0518_mcp_ilan`
  6 → 4 (B-23 dersi korunur; çift kilit yok, biri diğerine atıf), `test_v0518_kurulum`. Kanal değişiminin kırdığı 86
  eski test `tests/oa_teyit_kanali.py` yardımcısıyla (beyaz listeli sentetik adres) yeşil. Baz ölçüm: tam süit 88
  kırmızı → 0.
- **Canlı metinler (`9e431ac`):** alt oturum beyanı "87 dosya / 290 satır → 0 anma"; ölçüm (`git show --stat`):
  83 dosya, +505/−418; HEAD'de muafiyet dışı anma 0 (USUL 3. koşum ölçtü). Görevdeki "~28 / ~70" tahmini bayt
  kipli grep'ten geliyordu. Örnekler: 19 README'de "## Yargı Pro bağlantısı …" → "## Teyit kanalı
  (resmî kaynak beyaz listesi)"; master prompt 7) "YARGI PRO DURUMU" → "TEYİT KANALI … /mcp listesinde eklentiye ait
  girdi beklenmez", 8) eski yedek bağlantı adı verilmez; `ANAYASA.md` ve `references/anayasa.md` m.5 parantezi
  "(Yargı Pro/Mevzuat MCP)" → "(resmî kaynak beyaz listesi: içtihat portalları / mevzuat.gov.tr)" (iki nüsha özdeş);
  dayanak notları "(Yargı PRO MCP mevzuat_getir, teyit 2026-10-05)" → "(resmî metin — mevzuat.gov.tr, mevzuat_getir;
  teyit 2026-10-05)" (madde/tarih aynen); emek etiketi "Fikir kaynağı: … 16-4" ürün adsız, kişi adı ve bağlantı korundu.
- **Kayıtlar (`8998e34`):** CHANGELOG "Sürümsüz" maddesi, STATUS, YOL-HARITASI (`oa-kaynak`), dört parça günlüğü,
  SOZLUK terimi, tests/README §7.

## Kapılar (birleşik ağaç `c94e982`, Python 3.14.8, Windows)

| Kapı | Sonuç |
|---|---|
| Tam süit | 3887 geçti · 12 atlandı (udf-cli oturumu, saha referansı) · 0 kırmızı (91,8 s) |
| perf | 1 geçti, 3899 seçim dışı |
| ruff | All checks passed! |
| aile_dogrula | TEMİZ (20 parça) |
| hook_doktor --kurulu | TÜM MEKANİK KONTROLLER GEÇTİ ✓ |
| OA-SUIT-SAYISI | 3816 → 3851 (dal) → 3900 (birleşik), collect-only ile doğrulandı |

## Doğrulanamayan (alt oturum)

Hiçbir portala / MCP uç noktasına ağ erişimi yapılmadı; `WebFetch`/`WebSearch` canlı teyit akışı sahada sınanmadı; CI
koşmadı; kurulu eklenti 0.6.0 önbelleği (bu dalın kodu kurulu değil).

## Avukata sorulacaklar (alt oturumun listesi)

1. Emek etiketinin kanal-bağımsız lafzı kabul mü (eski lafız istenirse README satır muafiyeti gerekir).
2. Eski yedek bağlantı adının yalnız CHANGELOG'da kalması yeterli mi.
3. `oa_kurulum --json` adım kimliği `yargi_pro` → `teyit_kanali`: dış tüketici var mı.
4. Yerel `oa-kaynak` MCP tasarımı ve önceliği.
5. PR #9 birleşince #10'un akıbeti (orkestra: hızlı ileri alındı, #10 kapatılır).

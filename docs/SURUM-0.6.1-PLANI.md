# 0.6.1 — koordinasyon planı (komser avukat; 2026-10-17)

> Avukat kararı (2026-10-17): hedef 0.6.1. Bu belge canlı koordinasyon panosudur: kim ne yapıyor,
> hangi dosyalara dokunuyor, neyin kapısı ne, birleştirme hangi sırayla. Sürüm ve birleştirme
> kararı avukatındır (anayasa m.9); push yalnız avukat kararıyla. Ölçü tektir: müvekkilin menfaati
> (m.6) — sistem davayı kazanmaya hizmet eder, vitrin ikincildir. Metin kuralı: zero fluff.

## 1. Durum (ölçüm)

| Ne | Durum |
|---|---|
| `main` | `2db90ab` (PR #9, 2026-10-17 01:39) — 0.6.0 damgalı, 0.6.0 sonrası iş taşıyor |
| `denetim/fable-2026-10-15` | `d2c5fbe`; PR #11 → main AÇIK, CI 9/9 yeşil, birleştirilebilir; birleştirme kararı avukatın |
| `avukat-karari/udf-layer0-istisnasi` | `86a8ff9` (tabanı `d72feda`, denetim ucunun gerisinde); kendi heyet koşumu 2026-10-17-2 nihai öneri PUSH; push edilmedi |
| `onarim/ictihat-atif-baglanti` | `d2c5fbe` tabanlı, iş sürüyor (sahipsiz Yargıtay atıfı kapısı) |
| Paylaşılan worktree `denetim-fable-1015` | iki oturum aynı dalda commit atıyor (boşluk a/b, skill turu) — dosya sahipliği §3 |

## 2. 0.6.1 kapsamı

Girer: A K-17…K-29 kapanışı (yapıldı) · B saha metinleri anonim + testler belgesi (yapıldı) · C boşluk
analizi belgesi (yapıldı) + §0 (a)(b) uygulaması (sürüyor) · D skill ailesi turu (sürüyor) · E UDF
üretimi Layer 0 istisnası (dal hazır, entegrasyon bekliyor) · F sahipsiz atıf kapısı (sürüyor) ·
G avukat kararı bekleyenlerden karara bağlananlar (§5) · H sürüm damgası + heyet + release.

Girmez (0.6.2'ye): boşluk analizi §0 (c)-(f); YOL-HARITASI v0.5.19 açık kalemleri (kaldığı yerden
süren alım, avukat onayı kanıtı, döküm kaynak sınıfı, usul satırları kapısı, dosya-içi akıbet
bayrağı, avukat kavşağı kapısı, makbuzun nihai UDF özeti); `oa-kaynak` yerel MCP; hukuki yöntem
adayları A1…A10 / B1…B19 (avukat seçimi sonrası).

## 3. Dosya sahipliği (çakışma yasağı)

| Oturum | Sahip olduğu dosyalar | Dokunmaz |
|---|---|---|
| Boşluk (a)(b) | `oa-sure/**`, `oa-musteki-vekili/SKILL.md` + günlüğü, `oa-mudafii/SKILL.md` (yalnız :158 cümlesi), `oa-pipeline/SKILL.md` (yalnız :295 cümlesi), `tests/test_sure_*`, kural teyit notu | diğer her şey |
| Skill turu | diğer parçaların SKILL.md / references / docstring'leri, parça başına kilit testi | boşluk oturumunun dosyaları; `oa-gizlilik/**` ve UDF-Layer 0 metinleri (E); `kunye_teyit.py`, `dilekce_denetim.py` atıf bölümü (F); `oa_hafiza.py`, `belge_guvenlik.py`, `ictihat_muhakeme_denetim.py` kodu |
| Layer 0 UDF (E) | kendi dalı; entegrasyonda çatışma çözümü | paylaşılan worktree |
| Sahipsiz atıf (F) | kendi dalı: `oa-kontrol/scripts/kunye_teyit.py`, `oa-dilekce/scripts/dilekce_denetim.py` atıf bölümü, testleri | `ictihat_muhakeme_denetim.py` (önce komsere) |
| Komser (bu oturum) | CHANGELOG, STATUS, YOL-HARITASI, bu belge, sürüm damgaları, heyet koşumu, release notu, PR #11 | parça kodu |

Ortak kural: CHANGELOG / STATUS / YOL-HARITASI'na oturumlar DOKUNMAZ — kayıtları komser, raporlardan
işler. `tests/README.md` OA-SUIT-SAYISI: her oturum yalnız kendi toplamıyla, commit'ten hemen önce
`pytest --collect-only -q` ile ölçerek. Commit yalnız açık pathspec ile; `git add -A` yasak; push yok.

## 4. Rapor şablonu (zero fluff; her tur sonunda komsere SendMessage)

```
RAPOR — <oturum> — <tarih saat>
Dal / worktree: … | HEAD: … | push: hayır
Yapılan: <sha> — tek satır (dosyalar)
Kapılar: tam süit G·A·K | ruff | aile | perf | ilgili testler (önce kırmızı: evet/hayır)
Doğrulanamayan / açık: …
Avukata soru (varsa): …
Sonraki adım: …
```

## 5. Avukat kararı bekleyenler (KARAR-3 §7.1 — 0.6.1 için karar gerekenler)

| No | Karar | Komser önerisi |
|---|---|---|
| 1 | Anayasa m.4 / m.9 / m.10 "MCP aktifliği" ifadeleri → "teyit kanalına erişim" | evet, 0.6.1'de; anayasa metni avukatın — onayla girer |
| 2 | Beyaz listeye `hudoc.exec.coe.int`, `curia.europa.eu` | evet (AİHM infaz, ABAD) |
| 3 | Excel kapısı `SURUM` 1.2 → 1.3 | evet, sürüm damgasıyla birlikte |
| 4 | Emek etiketi lafzı; `oa_kurulum --json` adım kimliği `teyit_kanali` | mevcut lafız kalsın; kimlik kalsın |
| 7 | Envanter temizliği (yerel/uzak eski dallar, worktree kopyaları) | 0.6.1 sonrası, liste ile ayrı karar |
| 8 | CI `permissions:` + eylem SHA sabitleme | evet, komser yapar (mühendislik) |
| 9 | Hukuki yöntem adayları A1…A10 / B1…B19 | 0.6.2; avukat seçer |

## 6. Birleştirme ve çıkış sırası

1. Sürmekte olan oturumlar tur sonunda rapor verir (§4); komser kayıtları işler.
2. E dalı: denetim ucu E'ye birleştirilir (merge; tarih korunur), çatışmalar çözülür, tam süit; sonra
   E → denetim dalına birleştirme (avukat kararı: PR #11'e yığılı mı, ayrı PR mı).
3. F dalı aynı yol.
4. Sürüm damgası tek commit: `plugin.json`, `marketplace.json`, `pyproject.toml`, STATUS, YOL-HARITASI,
   iki README künyesi, `OA_SURUM` (`pipeline_kayit.py`, `teslim_paketi.py`), Excel `SURUM`; CHANGELOG
   "Sürümsüz" kaydı → "v0.6.1" başlığı; `aile_dogrula` sürüm işaretçisi uyarısı sıfır.
5. Heyet koşumu (usul / esas / güvenlik; `origin/main..HEAD`) → KARAR; BLOKLAYICI 0 şartı.
6. CI yeşil → PR #11 birleştirme (avukat) → etiket `v0.6.1` + GitHub Release notu (avukat eliyle;
   notu komser hazırlar).

## 7. Bitti sayılma ölçütü

Tam süit 0 kırmızı (altı ortam + yapı + OCR + lint); heyet BLOKLAYICI 0; her hukuki kural teyit
damgalı ya da TEYİT BEKLİYOR; canlı metinde üçüncü taraf sunucu anması 0; anayasa m.7 taraması
temiz; kayıtlar (CHANGELOG / STATUS / YOL-HARITASI / parça günlükleri) ölçümle; sürüm damgaları
eşit. Beyan yok, ölçüm var.

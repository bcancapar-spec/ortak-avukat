# v0.5.16 / I1 — Yargı Pro (Mevzuat MCP) teyit izi

Hakem: Yargı Pro hakemi (alt-ajan) · Tarih: 2026-09-07 · Taban: 80ac847 · Dal: v0516/I1
Kapsam: `git diff 80ac847` içindeki .md/.py/.json (oa-strateji, oa-interview). Testler koşulmadı (uygulayıcı koştu). Kod düzeltmesi yapılmadı.
Müvekkil/dosya verisi yok (m.7). Araç: `mevzuat_ara` (ID çözümü) + `mevzuat_getir` (madde) + `mevzuat_getir` (tam metin, 492 tarife/tebliğ). İçtihat künyesi iddiası diff'te YOK → `ictihat_ara` çağrılmadı.

## Norm teyitleri (her satır = bir MCP madde çağrısı; sorgu → sonuç)

| Norm (diff iddiası) | Sorgu | Sonuç |
|---|---|---|
| İİK m.257 — rehinsiz + vadesi gelmiş; m.257/2 hâller | mevzuatgov:kanun:3:2004 m.257 | UYUŞUYOR (yerleşim yeri yok; mal gizleme/kaçırma/kaçma/hileli işlem) |
| İİK m.258 — delil; ret ve yüze karşı karar istinaf; BAM kesin (m.258/3) | m.258 | UYUŞUYOR (7251/50 değişik 3. fıkra) |
| İİK m.259 — teminat kural; ilam: aranmaz; ilam mahiyetinde: takdir | m.259 | UYUŞUYOR |
| İİK m.264/1 — 7 gün takip/dava (gıyapta: tutanak tebliğinden); m.264/2-3 (7 gün; 1 ay) | m.264 | UYUŞUYOR |
| HMK m.389/1 — tedbir şartları | mevzuatgov:kanun:5:6100 m.389 | UYUŞUYOR |
| HMK m.392 — teminat zorunlu; resmî belge/kesin delil/durum → gerekçeli teminatsız; adli yardım | m.392 | UYUŞUYOR |
| HMK m.397/1 — uygulama talebinden iki hafta; aksi hâlde kendiliğinden kalkar | m.397 | UYUŞUYOR |
| 492 s.K. m.28/a — karar ve ilam harcı dörtte biri peşin; bakiye tebliğden bir ay | mevzuatgov:kanun:5:492 m.28 | UYUŞUYOR — EKSİK NÜANS: ölüm/cismani zarar tazminatında peşin oran YİRMİDE BİR (aşağıda küçük) |
| 492 s.K. m.30 — noksan harç tamamlanmadan devam yok | m.30 | UYUŞUYOR |
| 492 s.K. m.15, m.16 — nispi/maktu ölçü, değer esası | m.15, m.16 | UYUŞUYOR |
| HMK m.119/2 — bir haftalık kesin süre | m.119 | UYUŞUYOR (kapsam: (a),(d),(e),(f),(g) DIŞI bentler) |
| HMK m.77/1 — kesin süre içinde vekâletname; aksi hâlde açılmamış sayılır | m.77 | UYUŞUYOR |
| HMK m.115/2-3 — giderilebilir dava şartı kesin süre; hüküm anında giderilmişse ret yok | m.115 | UYUŞUYOR |
| HMK m.20 — iki hafta içinde gönderme talebi; aksi hâlde açılmamış sayılır; yeni mahkeme davetiye | m.20 | UYUŞUYOR (özet; başlangıç üç ihtimalli: kesin karar tebliği / kesinleşme / kanun yolu reddi tebliği) |
| HMK m.323 — yargılama gideri kalemleri | m.323 | UYUŞUYOR |
| HMK m.326/2 — haklılık oranına göre paylaştırma | m.326 | UYUŞUYOR |
| AAÜT m.3/1 (az/üç kat), m.7 (yarım/tam), m.13/1-4 | mevzuatgov:teblig:5:42687 tam metin (RG 04.11.2025/33067; değ. 08.01.2026/33131, 28.03.2026/33207) | UYUŞUYOR — m.13/3 ve m.13/4 YALNIZ maddi tazminat istemli davalar için (aşağıda küçük); m.10/2 mülga 08.01.2026 doğru |
| (1) sayılı tarife: başvurma asliye 732,00; III-1-a binde 68,31; III-2-a maktu karar 732,00; III-2-d ihtiyati haciz/tedbir 1.206,00; IV-a/c temyiz 3.608,50; IV-d/e istinaf 2.002,00; V keşif 5.188,00 | mevzuatgov:kanun:5:492 tam metin chunk 3 ("Uygulanan Miktar" sütunu) | BİREBİR UYUŞUYOR |
| Nispi asgari had (tarife.json: 732) | aynı chunk: "Nispi harçlar ... (427,60 TL) liradan aşağı olamaz" | KAYNAK ÇELİŞKİSİ — tarife.json bunu zaten çıpa olarak yazmış. Hakem notu: mevzuat.gov satırı güncellenmemiş görünüyor (2024 değeri); (g) bendinde 615,40 (2025) ve %18,95 artışla 732,02 → 732 tutarlı. Avukat teyidi şartı belgede var; KRİTİK değil |
| Harçlar Kanunu Genel Tebliği Seri No: 98 | mevzuat_ara TEBLIGLER → mevzuatgov:teblig:5:42887; tam metin | Metin yalnız gövde (%18,95 artış; RG 31.12.2025/33124); tarife EKİ xlsx → MCP'den okunamadı; rakamlar 492 konsolide metniyle teyit edildi (üstteki satır) |

## Hukuki mantık denetimi
- Koruma tedbiri 0. adım: kanuni çerçeve doğru; "usul esasa üstündür / tamamlayıcı süre telafisiz" önermesi İİK m.264 ve HMK m.397 metniyle uyumlu. sure_kurallari.json'a kural eklenmemiş (I5 alanı) — sözleşmeye uygun.
- Zaman ekseni: sayı/yıl üretilmiyor; şablon uydurma yasağıyla uyumlu.
- Usul zamanlama: tamamlanabilir/tamamlanamaz ayrımı HMK m.115/119/77 metinleriyle uyumlu; "derhâl" kuralının tamamlanamaz kusur için olduğu notu makul.
- maliyet_cetveli.py: fail-closed (exit 2) ve olasılık üretmeme ilkesi doğru. Aritmetik m.28/a (1/4) ve AAÜT m.13 kurallarını uyguluyor; aşağıdaki küçük kayıtlar dışında yanlış önerme yok.

## Bulgular
KRİTİK: yok.
KÜÇÜK:
1. `maliyet_cetveli.py` / SKILL.md: 492 m.28/a'daki istisna (ölüm ve cismani zarar tazminat davalarında peşin harç 1/20) yazılmamış; `pesin_oran` 0,25 sabit. Cismani zarar dosyasında açılış maliyeti 5 kat fazla hesaplanır — bir bayrak/parametre eklenmeli.
2. `hesapla()` AAÜT m.13/3 (kısmi rette davacı vekili ücreti tavanı) ve m.13/4 (tam rette maktu) kurallarını TÜM para davalarına uyguluyor; tebliğ metninde ikisi de yalnız "maddi tazminat istemli" davalar için. Alacak davasında tam ret → nispi ücret (m.13/1-2) olmalı. Bugün `aaut.*` null olduğu için kalem hesaplanmıyor (etkisiz), ama doldurulunca yanlış yön verir — dava tipi girdisi gerekir.
3. SKILL.md HMK m.20 özeti "kararın kesinleşmesinden itibaren iki hafta" diyor; madde üç başlangıç ihtimali sayıyor (kesin kararda tebliğ; kanun yoluna gidilmemişse kesinleşme; gidilmişse ret kararının tebliği). Süre satırı oa-sure'ye devrettiği için tehlike düşük.
4. `tarife.json` nispi asgari had kaynak çelişkisi belgede çıpa olarak duruyor (yukarıda) — avukat teyidi gerektiği notu korunmalı.

## Hüküm
I1: ONAY (kritik sıfır). Küçükler entegratöre.
MCP çağrı sayısı (bu grup için kullanılan): İİK ×5, HMK ×11, 492 ×4 madde + 2 tam metin chunk, AAÜT ×1, Seri No 98 ×1, mevzuat_ara ×4.

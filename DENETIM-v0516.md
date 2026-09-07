# DENETİMİN İNFAZI — v0.5.16

> Bu belge, 6 Eylül 2026 tarihli **iki bağımsız dış denetimin** (bütünleşik
> analiz: 22 bulgu + 12 hamle; dış denetim: 28 A + 8 B bulgusu, P0/P1/P2
> öneri listesi) nasıl kapatıldığını kayda geçirir. Denetim, infaz, hakemlik, norm
> teyidi, birleştirme ve saha ölçümü **ayrı ellerde** yürüdü. Hiçbir uygulayıcı
> `main`'e commit atmadı; birleştirme tek entegratörde toplandı. Kaynak
> belgeler `_gorus/denetim-2026-09-06-*.md`; her grubun MCP teyit izi
> `_gorus/denetim-v0516-yargipro-teyit-<grup>.md` (15 dosya).

## Yöntem

**15 dal.** Öneri listesi, parça sahipliğine göre 15 gruba bölündü (A oa-illiyet ·
B oa-pipeline · C1 oa-dilekce · C2 oa-kontrol · D oa-gizlilik+hafıza ·
E oa-ingest · F oa-vakia · G oa-usta · H oa-ictihat · I1 oa-interview/strateji ·
I2 oa-antitez · I3 ceza ikizleri · I4 oa-alan/kiyas/usul · I5 oa-sure ·
I6 oa-sozlesme). Her grup kendi `git worktree`'sinde, kendi `v0516/<grup>`
dalında çalıştı; sahiplik dışı dosyaya dokunmak yasaktı. A ve B iki alt
görevle (A-1/A-2, B-1/B-2) yürüdü. Önce-kırmızı TDD zorunluydu; fikstürler
sentetik (anayasa m.7).

**Adversarial hakem.** Her grubun çıktısı, varsayılanı *"bu iş eksik/yanlış"*
olan bir hakeme verildi; hakem dosyayı kendisi açıp komutu kendisi koşturdu.
14 hakem kararının 13'ü ONAY; **1 RET** (C2): K4 onarımı, etiketsiz birleşik
künyede kelime sınırı geri izlemesiyle **regresyon** üretmişti — tam künye
kısmi eşleşiyordu. Onarıldı, iki kilit testi eklendi, yeniden ONAY.

**Yargı Pro teyit turu.** Kod ve belgeye giren her norm, gruplar bittikten
sonra ayrı bir hakem turunda Mevzuat/Yargı Pro MCP'den **madde metniyle**
yeniden okundu (5 küme, 157 teyit). Kritik **1**: `dilekce_denetim.py`
netice-i talep uyarısı *"istenmeyen kalem hükme girmeyebilir"* diyordu;
oysa **HMK m.332/1** yargılama giderine **re'sen** hükmedilir der — script
metni yanlış hukuki önermeydi (SKILL.md doğruydu). Düzeltildi (`8e8b844`).
Küçükler (10) grup dallarında onarıldı.

**Entegratör.** 15 dal `--no-ff` ile sırayla birleştirildi (A B C1 C2 D E F G
H I1…I6; birleşim ucu `10aa5c1`, sürüm commit'i `7389fc4`). Birleşim sonrası
beş hizalama (H1–H5) ve `tests/test_v0516_entegrasyon.py` (18 test) eklendi.
Ardından ayrı bir belge bayatlık taraması (`714aa59`, 82 düzeltme) ve bu
belge.

**Saha ölçümü.** 11 gerçek dosya kopyası üzerinde v0.5.15 ile "önce" (118
ham çıktı), ardından v0.5.16 ile üç partide "sonra" (D01–D15, U01–U27 —
tamamı anonim kod; `_oa` artefaktı olmayan klasörler ölçülmedi). Ölçümcüler
yalnız ham stdout/stderr okudu, MCP çağırmadı, orijinal klasörlere dokunmadı;
çevrim kapısı gerçek graflarda çevrim bulunmadığından **sentetik** grafla sınandı.

## Telafisiz ikili

| # | Kusur | Neden telafisiz |
|---|---|---|
| **K4** | Atıf tanıyıcı *"dd.mm.yyyy tarihli karar"*, *"YYYY/N sayılı"* ve birleşik `YYYY/N-N` biçimlerine kördü; künyesiz atıf `[G1] 0 atıf → AÇIK` ile kapıyı geçiyordu | Kapının **görmediği** atıf, halüsinasyon panzehirinin tam deliğidir: uydurma bir karar tarih-only yazılırsa teslim yeşil kalıyordu. Şimdi **EKSİK KÜNYE → BLOK** (fail-closed); saha: önce 0, sonra 106 atıf yakalandı (U partisi) |
| **B-1** | OCR dil paketi yokluğu *"görsel inceleme gerek"* diye evrak özelliği gibi raporlanıyordu | Taranmış evrağın metni **sessizce** boş kalıyordu; süre taşıyan bir tebligat okunmamış sayılırdı. Şimdi *"OCR YAPILAMADI — dil paketi/araç hatası"* ayrı damga, sayaç, 00-INDEX'te 🔴 bölüm; saha: `--dil xyz` 66 sn → 2 sn, 11/11 evrak doğru sınıf |

## Halüsinasyon panzehirinin üçüncü onarımı

- **K3 —** PostToolUse hızlı denetimi ALEYHE künyeli taslağı görmüyordu
  (yalnız [N]/[L]). Artık **[F] hafif kip** in-process: künye → kütükte DAMGA →
  ALEYHE ise inline bulgu, 8 kalem tavanı, 2 sn sınırı; listede **en başta**.
  Saha: 0/21 → 8/9 ve 26/33 taslakta.
- **K5 —** kütükte **akıbet** (kesinleşti / bozuldu / kaldırıldı) alanı yoktu.
  `teyit --akibet … --akibet-kaynak` (kaynak zorunlu; araç ↔ avukat beyanı
  sınıfı görünür), bozulmuş+LEHE atıf → **[G5-AKIBET] TESLİM ENGELİ**; yazar
  (oa_hafiza) ↔ okur (ictihat_muhakeme) uçtan uca (H4). Saha: hiçbir gerçek
  kütükte akıbet verisi yok → kapı henüz ateşlenmedi (veri gelince ateşler).
- **K1/K2 —** graf bulgusu `DURUM.md`'ye ulaşmıyordu (bekçi dosya adına
  bağlıydı) ve çevrim kapısı `exit 0` ile "olmayan kapı"ydı. Bekçi **damgaya**
  (`arac == grafik_denetim`) bağlandı; `grafik_denetim` şema/çevrimde **exit 3**;
  pipeline adım-1 UYGULANDI kaydı çevrimli/şema-hatalı grafta **RET**, çıkış
  yalnız adlandırılmış `--serh-kapi graf`. `aile_dogrula` KİLİT-A bekçi damgası
  ↔ üretici script literalini dört bekçide denetler (K1 sınıfının tekrarı
  mekanik olarak kırmızı).

## Bulgu → hamle → dosya → test

Durum: **K** kapandı · **Kı** kısmen · **E** ertelendi. Dosya yolları
`plugins/ortak-avukat/skills/` altındadır; testler `tests/`.

### Bütünleşik analiz (K, G, H/P, D)

| Bulgu | Hamle | Dosya | Test | Durum |
|---|---|---|---|---|
| K1 | bekçi damgaya; KİLİT-A | oa-pipeline/scripts/pipeline_kayit.py · oa-usta/scripts/aile_dogrula.py | test_v0516_B · test_v0516_G · test_v0516_entegrasyon (H5) | K — saha: D03/D05/D09 + 9/9 U klasöründe satır var |
| K2 | exit 3 + GRAF KAPISI + `--serh-kapi` | oa-illiyet/scripts/grafik_denetim.py · pipeline_kayit.py | test_v0516_A · test_v0516_B | K — sentetik çevrim 3 partide RET; gerçek şema-hatalı D05/U11 RET |
| K3 | [F] hafif kip | oa-dilekce/scripts/dilekce_denetim.py | test_v0516_C1 · test_v059_hizli_kip | K — yan bulgu S-1 (kütük ayrıştırıcı) |
| K4 | EKSİK KÜNYE sınıfı → BLOK | oa-kontrol/scripts/kunye_ortak.py · kunye_teyit.py · ictihat_muhakeme_denetim.py | test_v0516_C2 · test_kunye_teyit | K — hakem RET'i sonrası regresyon onarıldı; yan bulgu S-3 |
| K5 | `--akibet` + [G5-AKIBET] | oa-pipeline/scripts/oa_hafiza.py · ictihat_muhakeme_denetim.py | test_v0516_D · test_v0516_C2 · entegrasyon (H4) | K — sahada veri yok, kapı beklemede |
| G1 | çevrim minimal kırpma + tam sayım | grafik_denetim.py | test_v0516_A | K |
| G2 | çevrimde §7/§8 sahte güven/yanlış beyan kaldırıldı | grafik_denetim.py | test_v0516_A | K |
| G3 | illiyet kenarında `dogrulama` zorunlu | grafik_denetim.py + oa-illiyet SKILL/şema | test_v0516_A | K — saha: desteksiz kenar D05 0→8, D09 0→10 |
| G4 | beyan-yok ağırlığı 0.4 + `guc_beyansiz_kenarlar` ayrı alan | grafik_denetim.py | test_v0516_A · test_zincir_analizi | K — D03 en düşük güven 0.64→0.16 |
| G5 | mükerrer `id` → hata | grafik_denetim.py | test_v0516_A | K |
| G6 | `rapor()` try/except, DFS derinlik sınırı, DENETİM ÇÖKTÜ damgası | grafik_denetim.py | test_v0516_A | K |
| G7 | `dayanak_delil` katıldı; **bağlanmamış delil** ayrı sınıf | grafik_denetim.py | test_v0516_A | K — D11 yetim 8/11/16→0; U 80→0 (+20 bağlanmamış) |
| G8 | köprü tip-duyarlı (perde yalnız tüzel-kişi kümelerini bağlayan gerçek kişi) | grafik_denetim.py | test_v0516_A | K — yan bulgu S-5 (sinyal kaybı mı?) |
| G9 | `--taraf` + defterden `--ceza mudafii` okuma → sağlamlaştır/çürüt yönü | grafik_denetim.py | test_v0516_A | K — sahada ayrı ölçüm yok |
| G10 | `kesme_flag` dal-ayrımlı enum (medeni/miras/ceza) + `--goc` scripti | grafik_denetim.py · oa-illiyet/references doktrin | test_v0516_A | K — gerçek grafların göçü avukat kararı (bkz. §Avukat) |
| G11 | örtüşme sayacına `(n)` ve `;` | ictihat_muhakeme_denetim.py | test_v0516_C2 | K — «m.353/(1)» parantezi sayılıyor (advisory, devir) |
| G12 | `tip: karar\|mahkeme`, `tur: kanun_yolu` + `sonuc` enum'u | grafik_denetim.py + şema | test_v0516_A | K |
| P1 | `--serh-kapi <ad>`; ELDEN düşürmesi bağımsız | pipeline_kayit.py | test_v0516_B | K — yan bulgu S-2 (ingest-once şerhi erken dönüyor) |
| H1 | (dosya, kapı-sınıfı) sayacı, N≥3 → M7 | pipeline_kayit.py | test_v0516_B | K — sahada tetiklenmedi |
| H2 | [N] taraf etiketi + KONU/TL beyaz liste | dilekce_denetim.py | test_v0516_C1 | Kı — taraf etiketi 0→0 (sıfır taban); özel ad/il adı gürültüsü sürüyor |
| D1 | iniş ritüeli: kat başına kütük satırı `SEVİYE/KÜNYE/METİN` | oa-ictihat/scripts/kanun_yolu_zinciri.py · SKILL | test_v0516_H | K |
| D2 | kapsama sınırları belgelendi (BAM/İDM korpusu) | oa-ictihat SKILL/references | test_v0516_H | K — araç dışı sınır; belge |
| D3 | `ictihat_ara` sarmalayıcısında (BAM, daire) istemci-tarafı süzgeç | oa-ictihat SKILL | test_v0516_H | K |
| D4 | künye daima tam metinden (mevcut m.4 ilkesi) | — | — | E — bilgi notu; değişiklik gerekmedi |
| Hamle 12 | merci tayini notu (HSK 2021 iş bölümü sonrası ilçe dosyası) | oa-usul SKILL «GÖREV DÖNGÜSÜ — MERCİ TAYİNİ» | test_v0516_I4 | K — kişi/dosya verisi yok |

### Dış denetim (A, B)

| Bulgu | Hamle | Dosya | Test | Durum |
|---|---|---|---|---|
| A-1 | anayasa m.1'e triyaj cümlesi (derinlik kısılmaz, kapsam orantılanır) | ortak-avukat/references/anayasa.md | test_skill_doktrin · test_v0585_a1_triyaj | K — hazırlık commit'i `fcae8d8` |
| A-2 | hat sırası 6 ANTİTEZ ↔ 7 STRATEJİ; eski defter «adım eşlendi» notu | pipeline_kayit.py · ortak-avukat/oa-mudafii/oa-musteki-vekili SKILL · oa_metrik.py | test_v0516_B · entegrasyon (H2) | K — saha: 15/15 + 5/5 DURUM'da not |
| A-3 | «Müvekkil Kararı Bekleyen» DURUM bölümü + bilgilendirme şablonu | pipeline_kayit.py · muvekkil-bilgilendirme-sablonu.md | test_v0516_B · test_durum_md | K — 15/15 U, 5/5 D |
| A-4 | manifestte süre adayı işareti (`okuma_kapisi --sure-adaylari`, advisory) | oa-ingest/scripts/okuma_kapisi.py | test_v0516_E · test_okuma_kapisi | K — D11 9 / D13 7 / U 3 klasör |
| A-5 | muhatap ayrımı + cevap statüsü soruları | oa-interview SKILL | test_v0516_I1 | K |
| A-6 | masraf gücü + risk toleransı alımda | oa-interview SKILL | test_v0516_I1 | K |
| A-7 | forum seçimi refleksi | oa-alan SKILL | test_v0516_I4 | K — HMK m.17-18/114/116-117/390 çıpaları teyitsiz etiketli |
| A-8 | tamamlanabilir kusurda «şimdi/sonra» avukat kararı | oa-usul SKILL · oa-strateji SKILL | test_v0516_I4 · test_v0516_I1 | K |
| A-9 | «en ucuz usul» varsayımı kaldırıldı; gecikme maliyeti strateji tablosunda | oa-usul/oa-strateji SKILL | test_v0516_I4 | K |
| A-10 | `tur: asama` süre sınıfı (5 kural, tarihsiz) + `sure-flag --asama` | oa-sure sure_kurallari.json · hesapla_sure.py · sure_nobetci.py · oa_hafiza.py (H1) | test_v0516_I5 · entegrasyon (H1) | K — sahada `tur: asama` kaydı yok, blok gözlenemedi |
| A-11 | senkron klasör uyarısı (`init` anında, JSON izi) | oa_hafiza.py · oa-gizlilik SKILL + gizlilik-desenleri.md | test_v0516_D | K — Av.K. m.36, KVKK m.6/m.9 MCP teyitli |
| A-12 | `menfaat_akisi` kenar tipi | — | — | **E** — hiçbir grup uygulamadı (depoda sıfır geçiş); v0.5.17 |
| A-13 | ispat ontolojisi: `tur ∈ {vakia, hukuki}`, tanık `caizlik`, karine yük kaydırır, bilirkişi tam ispat değil | oa-vakia/scripts/vakia_matris.py · SKILL | test_v0516_F · test_vakia_matris | K — U 4 klasör 31 «caizlik belirsiz» satırı; eski JSON'lar alan yoksa fail-closed |
| A-14 | içtihat haritası adımı (yerleşik/azınlık/ayrışma/HGK) | oa-ictihat SKILL | test_v0516_H | K |
| A-15 | `buyuk_onermeler[]` + YARIŞAN NORMLAR tablosu; gerekçesiz seçim KRİTİK | oa-kiyas/scripts/kiyas_denetim.py | test_v0516_I4 · test_kiyas_denetim | K — exit 0 korundu (2026-08-12 kararı); saha JSON'ları eski şema |
| A-16 | zaman ekseni (nitel süre bandı; sayı üretilmez) | oa-strateji SKILL | test_v0516_I1 | K |
| A-17 | risk toleransı strateji girdisi | oa-strateji SKILL | test_v0516_I1 | K |
| A-18 | `maliyet_cetveli.py` — yıl damgalı tarife, bayat → fail-closed | oa-strateji/scripts/maliyet_cetveli.py · tarife.json | test_v0516_I1 | **Kı** — AAÜT ek tabloları MCP'den alınamadı; boş kalemler avukat kararı |
| A-19 | koruma tedbiri 0. adımı | oa-strateji SKILL · oa-sure | test_v0516_I1 | K — İİK tedbir çıpaları teyitsiz etiketli |
| A-20 | 9. cephe `bilirkisi_teknik` | oa-antitez/scripts/antitez_matris.py | test_v0516_I2 | K — saha 20 matris 8/9 «EKSİK»; exit 0 |
| A-21 | hâkim lensi (on dakikada okuyan hâkim) ikinci pas | oa-antitez SKILL · oa-kontrol SKILL | test_v0516_I2 · test_v0516_C2 | K |
| A-22 | netice-i talep playbook + [P] advisory | oa-dilekce SKILL · dilekce_denetim.py | test_v0516_C1 | K — Yargı Pro hakemi script metnini düzeltti (HMK m.332/1); saha 53/54 taslakta [P] |
| A-23 | ifa senaryo testi (normal/gecikme/fesih) | oa-sozlesme/scripts/sozlesme_denetim.py | test_v0516_I6 | K — D09 3/3 «45 senaryo boşluğu»; pipeline okuması devir |
| A-24 | ilk sayfa + uzunluk testi (B listesi) | oa-kontrol SKILL · dilekce_denetim | test_v0516_C2 | K |
| A-25 | en avantajlı sonuç haritası + susma/beyan protokolü | oa-mudafii SKILL | test_v0516_I3 | K — HAGB «sanığın kabulü» geçiş rejimi teyitsiz şerhli |
| A-26 | ceza↔hukuk köprüsü («ceza yolu ne için») | oa-musteki-vekili SKILL | test_v0516_I3 | K — TBK m.74 içtihadı yalnız künye düzeyi |
| A-27 | hata tetikli damıtma + revize-diff ritüeli | oa-usta SKILL · aile_dogrula | test_v0516_G | K |
| A-28 | avukat hükmü sensörü (DURUM «Avukat Hükümleri» bölümü) | pipeline_kayit.py · oa-usta | test_v0516_B · test_v0516_G | K — sahada bölüm var, hüküm kaydı yok |
| B-1 | OCR araç hatası tespiti (rc≠0 / dil verisi yok → ayrı damga) | oa-ingest/scripts/oa_ingest.py | test_v0516_E · test_oa_ingest_ocr_nobetci | K — bkz. Telafisiz ikili |
| B-2 | `pipeline_kayit.py` bölme (P2-9) | — | — | **E** — dosya 6.284 satır; bölme yapılmadı. Hook gecikmesi [F] hafif kipin 2 sn sınırıyla dolaylı ele alındı |
| B-3 | STATUS/YOL-HARITASI sürüm işaretçisi testi + bayatlık taraması | aile_dogrula.py · kök belgeler | test_v0516_G · test_v0514_vitrin | K — `714aa59`: 82 düzeltme |
| B-4 | `git filter-repo` | — | — | **E** — avukat kararı (geçmiş yeniden yazımı) |
| B-5 | `_oa/` düz metin | oa-gizlilik SKILL «Senkron klasör riski» + init uyarısı | test_v0516_D | **Kı** — uyarı + şifreli konteyner önerisi; şifreleme cihaz kararı |
| B-6 | udf-cli kesinti planı belgesi; pin kararı | oa-dilekce references | test_v0516_C1 | **Kı** — belge var; pin avukat kararı |
| B-7 | README ölçüm dili | README.md | test_v0514_vitrin | K — hazırlık `fcae8d8` + `714aa59` |
| B-8 | test skip koşulu ↔ üretim varsayımı (dil paketi yoksa gerekçeli atlama) | test_oa_ingest_ocr_nobetci.py | aynı | K — Linux gerçek koşusu CI'da görülecek |

## Saha: önce (v0.5.15) → sonra (v0.5.16)

Kodlar anonimdir (D = ilk ölçüm kümesi, U = ikinci küme); sayılar ham
çıktıdan okunmuştur. «Ö=S» değişmedi demektir.

| Bulgu | Ölçü | Önce | Sonra |
|---|---|---|---|
| K1 | graf denetim satırı DURUM.md'de | doğrulanamadı (ham yok); v0.5.15 DURUM'da yalnız ad-uyumlu JSON'un 2 satırı (D03) | D03 3 JSON → 19 satır · D05 20 + «+36 uyarı daha» · D09 40 şema satırı · U 9/9 klasörde «Graf Yapısal Boşluk» bölümü (temiz JSON'da doğru olarak yok) |
| K2 | çevrimli graf → adım-1 UYGULANDI | exit 0; kayıt geçer | sentetik çevrim: exit 3 · pipeline RET (GRAF KAPISI) · yanlış kapı şerhi RET · `--serh-kapi graf` ŞERHLİ (3 partide aynı) · gerçek şema-hatalı D05/U11 RET |
| K3 | hızlı kipte [F] | 0/21 taslak | D 8/9 · U 26/33, hepsinde en başta · D06 «kütük bulunamadı — 14 künye» in-process görünür · «kütük fiilen kullanılmıyor» 9/9 Ö=S |
| K4 | tarih-only / K-only atıf | AYRIŞTIRILAMAYAN 49 (sınıfsız); [G2] BLOK 0 | [EKSİK KÜNYE] D04 11 · D06 3 · D10 2 · D11 32+32 · U 106; [G2] EKSİK KÜNYE BLOK D04 1 · U 32; 3 taslak exit 0→1 |
| K5 | [P] netice-i talep · [G5-AKIBET] | 0/21 (bölüm yok); para geçen 15 blokta faiz 0/15 | [P] D 9/9 · D10 12/12 · U 32/33 (advisory; exit değişmez) · [G5-AKIBET] 0/33 — kütüklerde akıbet verisi yok |
| G3 | desteksiz kenar (`dogrulama` yok) | D05 0 · D09 0 («her kenar delil-teyitli») | D05 8 · D09 10 · U11 13 ✗ → exit 3 |
| G4 | beyan-yok ağırlığı / en düşük zincir güveni | 0.8 / D03 0.64 | 0.4 / D03 0.16; `guc_beyansiz_kenarlar` D03 8/8 |
| G7 | yetim delil → bağlanmamış delil | D11 8/11/16 yetim (tümü delil) · U 80 yetim | D11 yetim 0 + bağlanmamış 0/1/1 · U yetim 0 + 20 bağlanmamış · D03 5 |
| G8 | köprü etiketi | D03 4 (3'ü kanonik-dışı tip) «muvazaa/perde» · U 114 «muvazaa» | tip-duyarlı: D03/D05 0 · D11 5/4/6 «yapısal köprü» · U 1 perde / 56 yapısal |
| G8 | şema hatasında exit | D05 16 ✗ exit 0 · D09 20 ✗ exit 0 | exit 3 + `blok_sinifi ["sema"]` (D05, D09, U11) |
| G10 | `--goc` gerçek graflarda | araç yok | D03 0/16 kenar · D09 0 · D11 2 «göçmedi, elle düzelt» · U 12/12 exit 0, 22 «elle düzelt»; kaynağa dokunmadı |
| H2 | [N] toplam / taraf etiketi | D 62 · U 257 / 0 | D 54 · U 232 (KONU/TL elendi) / 0 → 0; özel ad/il adı gürültüsü sürüyor |
| P0-1 | ingest normal | D11 40 evrak · 188 sn · OCR-BOŞ 0 | D11 101 sn · OCR-BOŞ 0 · D13 14 evrak 140 sn · U24/U25/U27 exit 0, YÜKLENEMEDİ 0 |
| P0-2 | `--dil xyz` | exit 0; 11 evrak OCR-BOŞ (yanlış sınıf); «dil paketi/xyz» stdout'ta yok; 66 sn | «OCR YAPILAMADI — dil paketi/araç hatası» D11 11 · D13 5 · U14 3; `ocr_arac_hatasi` sayacı; 00-INDEX 🔴 bölümü; 2 sn; exit hâlâ 0 |
| P0-3 | hat sırası | adım 7 = antitez («script izi yok» yalnız adım 7'de) | DURUM «eski hat sırası ≤v0.5.15 — adım eşlendi» D 5/5 · D09/D10 · U 15/15; `--goster` 6=ANTİTEZ 7=STRATEJİ |
| P0-4 | pipeline `--denetle` | 8/8 exit 1 (makbuz yok, Gate G) | Ö=S: 8/8 · D09/D10 · U 18/18 exit 1; eski şema defter D07 + 3 U «defter bulunamadı» |
| A-3 | «Müvekkil Kararı Bekleyen» | 0 (ham yok) | D 5/5 · U 15/15 (içerik «(yok)»); «Avukat Hükümleri (A-28)» bölümü yeni |
| A-4 | `okuma_kapisi --sure-adaylari` | — | D11 9 · D13 7 · U 3/3 klasör; advisory, `sure-flag` yazmadı |
| A-10 | aşama tetikli blok | — | 0/16 defterde `tur: asama` kaydı → gözlenemedi; süre nöbetçisi Ö=S (D05 exit 3: 1 BUGÜN; D10 2 GEÇMİŞ) |
| A-13 | vakıa ontolojisi | D05 15/15 «belgeli», saglikli=true | «tanık caizliği belirsiz (HMK m.200-203)» U 4 klasör 31 satır · hukuki iddia/karine sayaçları 10/10 (0 — eski şema) · D05 hâlâ 15/15 belgeli · 6/10 «EKSİK», exit 0 |
| A-15 | kıyas yarışan norm | tek `str` norm; D05 7/7 DELİLSİZ «Yapı bütün» exit 0 | Ö=S; `buyuk_onermeler` 22/22 JSON'da yok (eski veri); «KRİTİK BOŞLUK var» U05/U10/U11 exit 0 |
| A-20 | antitez cephe kapsamı | 8/8 (%100) TAMAM | 8/9 (%89) «EKSİK — KÖR NOKTA: bilirkisi_teknik» D 4/4 · D11 2/2 · U 14/14; exit 0 |
| A-23 | sözleşme senaryo denetimi | özellik yok; exit 0 | D09 3/3 «SENARYO DENETİMİ AÇIK — 45 boşluk»; exit 0 |

**Sahanın yeni yan bulguları (v0.5.17 adayı, sırayla):**

- **S-1 —** `kunye_ortak.kutukten_son_damga` kütük satırlarını *"17 hücre / 7
  beklenirdi — BOZUK fail-CLOSED"* diye atlıyor: 26/33 U taslağında her künye
  «damgasız» görünüyor (hızlı kip 8.411, tam CLI 6.127 uyarı satırı). Kütük
  sütun sözleşmesi ile ayrıştırıcı uyuşmuyor — fail-closed olduğu için yanlış
  yeşil yok, ama gerçek DAMGA'lar kör; K3'ün sahadaki gerçek getirisi buna bağlı.
- **S-2 —** `00-kunye.json` yokken `--serh-kapi ingest-once` şerhi erken
  dönüyor; GRAF KAPISI hiç değerlendirilmiyor (çevrimli graf şerhsiz geçti).
  Kapı zinciri sırası düzeltilmeli.
- **S-3 —** `kunye_teyit` ÖZET satırı EKSİK KÜNYE sınıfını saymıyor (D04
  «TEYİTSİZ 0» ama 11 EKSİK KÜNYE); BLOK doğru, özet yanıltıcı.
- **S-4 —** DURUM.md 20 satır tavanı dosya sırasına göre kesiyor; D05'te
  yeni JSON'un satırları «+36 uyarı daha» arkasında.
- **S-5 —** köprü sinyali D03 4 / D05 2 → 0: tip-duyarlı etiket doğru çalışıyor
  olabilir, ama muvazaa/perde uyarısının sahada tamamen susması strateji sinyali
  kaybı mı — kaynak okunmadan karar verilemez.
- **S-6 —** `--goc` çıktısı klasöre yazılınca pipeline bekçisi onu «makbuzsuz
  dilekçe adayı» saydı (dosya dizin dışına taşındı).
- **S-7 —** U01 graf sayıları D11 ile birebir aynı — olası kopya klasör; iki
  kümenin bağımsızlığı bu satırda şüpheli.
- **S-8 —** A-20 «Matris bütünlüğü EKSİK», A-15 «KRİTİK BOŞLUK», A-13 «EKSİK»
  hepsi exit 0 (tasarım: motor bloklamaz, DURUM gösterir). Ölçüm notu, kusur değil;
  ama üç motorun aynı anda «eksik + yeşil» demesi avukatın gözünden kaçabilir.

## Entegratör hükümleri (çatışma çözümleri)

**Süit sayısı tek elden.** 15 dalın her biri `tests/README.md` OA-SUIT-SAYISI
satırına kendi sayısını yazmıştı (E/H/I3/I6 çakıştı). Karar: gruplar bu satıra
dokunmaz, B-35 kırmızısı bilinçli bırakılır, entegratör `pytest --collect-only`
ile **tek seferde** yazar. D grubu kendi değişikliğini bu gerekçeyle geri aldı.

**Kapılar sert, motorlar advisory.** K2'de kapı sert (adım-1 RET, çıkış yalnız
adlandırılmış şerh) — "advisory kapı = olmayan kapı" tezi. Buna karşılık
kıyas/antitez/vakıa motorları (A-15/A-20/A-13) *exit 0* korudu: 2026-08-12
kararı gereği yorum avukatındır, motor bloklamaz, DURUM gösterir. İki ilke
çelişmez: **kayıt kapısı** bloklar, **analiz motoru** gösterir.

**G4: 0.4 mi, ayrı sınıf mı?** İkisi de: beyan-yok ağırlığı 0.4'e indi *ve*
`guc_beyansiz_kenarlar` ayrı alan oldu; §3'e boşluk düşer. Denetimin önerdiği
"ayrı sınıf" dürüstlük ölçütüne daha uygun; 0.4 ise eski grafların zincir
güvenini hemen düşürür (D03 0.64→0.16 — istenen etki).

**G10: şema kırıldı.** `kesme_flag` dal-ayrımlı enum'a geçti (geriye uyumsuz);
eski graflar için `--goc` scripti verildi, ama serbest-metin flag'ler göçmüyor
(«elle düzelt»). Gerçek graflarda 0 kenar otomatik göçtü — bkz. §Avukat.

**Hat sırası: eski defterler kırılmadı.** ANTİTEZ 6 ↔ STRATEJİ 7 değişince
eski defterler yeniden yazılmadı; DURUM'a «eski hat sırası — adım eşlendi» notu
düşer, eski evrak önekleri geriye uyumla kabul edilir.

**Teyit izi dosyaları.** 11 dalın teyit dosyası kök dizine düşmüştü (yol
ayracı eksik); `git mv` ile `_gorus/` altına taşındı — 15/15.

## Yapılamayanlar (sessiz atlama yasağı)

- **A-12** `menfaat_akisi` kenar tipi ve **B-2/P2-9** `pipeline_kayit.py` bölme
  — hiçbir grup uygulamadı; v0.5.17 adayı.
- **Tam süit** sürüm commit'inden (`7389fc4`) **önce** alınamadı (arka planda
  sürüyordu); bayatlık commit'i (`714aa59`) sonrası tam koşu: **2300 yeşil /
  1 atlama / 0 kırmızı** (491 sn). Bu belgenin commit'inden önce bağımsız bir
  tam koşu daha alındı — sonuç §Sayılar.
- **Saha yan bulguları S-1…S-8** bu sürümde onarılmadı (ölçüm sürüm commit'inden
  sonra alındı); koda dokunulmadı.
- `git push` yapılmadı: GitHub kimliği geçersiz (`gh auth status`: keyring
  token invalid); push denemesi zaman aşımı. Avukat `gh auth login -h github.com`
  sonrası `git push origin main`.
- Kurulu kanal **0.5.9.1 BAYAT** (`tools/hook_doktor.py`: «bayat nesil servis
  ediliyor»); yerel eklenti güncellemesi interaktif `/plugin` gerektirir —
  avukat adımı.
- MCP'den teyit edilemeyip **«çıpa — teyit edilmedi»** etiketiyle bırakılan
  normlar: 7589 s.K. RG sayısı; dava dilekçesi-temerrüt/faiz içtihadı ve HMK
  m.392 vd. (C1); HAGB «sanığın kabulü» geçiş rejimi, TBK m.74 tam metin, TCK
  m.52 / CMK m.153 / TCK m.267 (I3); 492 s.K. m.30-32, HMK m.17-18/114/116-117/390,
  İİK tedbir çıpaları (I4); TBB Meslek Kuralları bilgilendirme hükmü (B);
  TCK m.24 vd. ve 12. CD hattı künyesi (A). Kullanım anında teyit şartı.
- AAÜT 2026 ek tabloları (maktu/nispi) MCP'den çekilemedi (RG eki PDF id'si
  reddedildi); nispi harç asgari haddi iki kaynakta farklı — tarife.json'da
  «çıpa — kaynak çelişkisi».
- Devirler: `pipeline_kayit.py`'nin `senaryo_bosluklari` okuması (I6);
  `md_yaz` dil adı sabiti (E); G11 «m.353/(1)» parantez sayacı (C2); Linux'ta
  tur paketi yokken OCR yolu yalnız sahte ikiliyle sınandı (E); oa-usta SKILL.md
  aile denetimi paragrafı hâlâ «üç bekçi / glob deseni» anlatıyor (4. bekçi +
  damga sözleşmesi metne işlenmedi).
- Bayatlık taramasında bilinçli dokunulmayanlar: referans günlüklerindeki
  tarihî saha kimlikleri ve test docstring'leri (ayrı avukat kararı).
- Saha kapsamı: `_oa` artefaktı olmayan 8 klasör ölçülmedi; G9 taraf yönü,
  H1 sayacı, A-10 aşama bloğu ve K5 akıbet kapısı sahada **tetiklenecek veri
  bulunamadığı** için gözlenemedi.

## Avukat kararı bekleyen

| # | Karar | Öneri / bedel |
|---|---|---|
| 1 | **B-4** `git filter-repo` — public depo geçmişinde dosya kimliği | Geçmiş yeniden yazımı kalıcı ve zorlayıcıdır; yalnız avukat kararıyla. Push öncesi karar verilmeli |
| 2 | **udf-cli pin** (A-5/B-6) | Pin: tedarikçi kesintisinde stabil; bedel: güvenlik/format güncellemesi elle. Kesinti planı belgesi hazır |
| 3 | **tarife değerleri** (`maliyet_cetveli` tarife.json) | AAÜT ek tabloları RG'den elle girilmeli; boş kalemler fail-closed (cetvel üretmez). Nispi asgari had: RG mi konsolide metin mi? |
| 4 | **`kesme_flag` göçü gerçek graflarda** (G10) | 22 serbest-metin flag otomatik göçmedi; her biri dalına (medeni/miras/ceza) göre elle sınıflanmalı. Göçülmezse eski graflarda `dal: null` kalır, ceza dalı notu üretilmez |
| 5 | Kurulu kanal güncellemesi (0.5.9.1 → 0.5.16) | `/plugin` ile güncelle, Claude Code'u tam kapat-aç, `hook_doktor.py --kurulu` yeşil olana kadar saha koşusu yapma |
| 6 | S-5 köprü sinyali | Perde etiketi sahada sıfıra düştü; «yapısal köprü» satırı yeterli mi, yoksa ticaret dosyasında ayrı perde uyarısı geri mi gelsin? |

## Sayılar

58 bulgu (22 + 28 A + 8 B) + 12 hamle + 28 öneri kalemi · 15 dal / 17
uygulayıcı görevi · 14 adversarial hakem (1 RET → onarıldı) · 5 Yargı Pro
hakem kümesi, 157 norm teyidi (1 kritik → onarıldı) · 42 ajan, ~80 dk ·
saha 11 + 27 anonim klasör, 3 ölçüm partisi · süit **1763 → 2301** ·
tam süit **2300 yeşil / 1 atlama / 0 kırmızı** — iki bağımsız tam koşu (bayatlık sonrası 491 sn; bu belge öncesi 497 sn) · `aile_dogrula` TEMİZ (20
parça) · beş sürüm damgası birlikte 0.5.16 · push YOK (kimlik).

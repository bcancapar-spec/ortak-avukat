# oa-usta — Değişiklik Günlüğü

(SKILL.md gövdesinden bağlam ekonomisi için taşındı; içerik aynen korunmuştur.)

- **2026-06:** Anayasal düstur işlendi (Can yönlendirmesi): **usul esasa üstündür** — süre usul hukukunun parçasıdır; düstur bu parçanın işlevine operatif kuralla bağlandı (yukarıdaki bölüm). Müvekkil menfaati çift yönlü: kendi usul zaafını sıfırla, karşı tarafın usul hatasını (özellikle kaçırılmış süreyi) tespit et ve derhâl kullan.
- **2026-06:** Anonimleştirme süzgeci bağlandı (anayasal kural — Can yönlendirmesi): skill metinlerine tasarımcı dışında isim/dava/dosya atfı giremez; içerik soyut örüntü olarak taşınır.
- **2026-06:** Örnekleme ilkesi bağlandı (anayasal — Can yönlendirmesi): konu sayımları örneklemdir, kapsam tüm Türk hukukudur; işlemeyen örneklem güncellenir, metod sabittir.
- **2026-06:** Çaba/kalite standardı bağlandı (anayasal — Can yönlendirmesi): tasarruf hedef değil; derinlik karmaşıklığa göre yükselir; Opus+High taban.
- **2026-06:** Doğaçlama meşruiyeti bağlandı (anayasal — Can yönlendirmesi): yöntemde serbest doğaçlama (Çapar lafzı), olguda sıfır halüsinasyon/teyit.
- **2026-06:** Başbakan denetimine tabi olma bağlandı (anayasal — Can yönlendirmesi): istisnasız tam işletim, tembellik/kaçış yasağı, dürüst 'yapılamadı' + yeni yöntem.
- **2026-06:** ÇIRAK kimliği + sürekli birikim döngüsü eklendi (Can yönlendirmesi — "hukuk gelişen sosyal bilim; oa-usta tüm çalışmalardan öğrenip kendini geliştirsin; usta=Başbakan-pipeline, çırak=oa-usta"): Çırak, Başbakan pipeline'ı (özellikle KAPANIŞ adımını) gözlemleyerek öğrenir, dersi oa-arsiv Örüntü Kütüphanesi'ne/skill-adayına damıtır, olgunlaşınca yapıya döker, mevzuat/içtihat gelişimini örnekleme güncellemesiyle izler. Dürüst tanım: gerçek ML değil, kalıcı metin birikimi (fonksiyonel öğrenme).

- **2026-07 (v3.16):** Fiziksel aktivasyon — simülasyon yasağı bloğu eklendi (Can yönlendirmesi — komutla tetiklenen parçalar description'dan taklit edilmesin, fiilen çağrılsın): çalıştı = fiilî Skill çağrısı / gerçek script / gerçek MCP çağrısı + DEVİR PAKETİ + pipeline defteri kaydı. Değişiklik günlüğü bağlam ekonomisi için `references/degisiklik-gunlugu.md`'ye taşındı (içerik korunmuştur).
- **2026-07 (v3.17):** Aile yapı denetimi eklendi (Can yönlendirmesi — rapor 5.5): `scripts/aile_dogrula.py` — frontmatter/name eşleşmesi, description 1024 sınırı (>900 uyarı), fiziksel blok, günlük işaretçisi, script referans bütünlüğü, sürüm tutarlılığı. Bakım kuralı: YENİ İÇERİK GÖVDEYE, description'a DEĞİL; her paketlemeden önce denetim koşulur.
- **2026-07:** Çaba/token düsturu GÜNCELLENDİ (Can yönlendirmesi): tasarruf artık HEDEF — ama yalnız mekanik/temsil katmanında ve VERİ-KAYIPSIZ; muhakemede tasarruf edilmez, derinlik/doğrulama/araştırma asla kısılmaz. Aile geneli anayasal güncelleme; deterministik motor: `oa-ingest`.
- **2026-07 (v3.22 — M2-3):** Sürüm işaretçisi ailenin ortak M2-3 entegrasyon sürümüne hizalandı (`aile_dogrula.py` sürüm tutarlılık uyarısını temizlemek için); bu satırın kendisi dışında bu parçada işlevsel bir değişiklik YOKTUR — gerçek içerik değişiklikleri (varsa) yukarıdaki ayrı kayıtlardadır.
- **2026-07 (v3.23 — M3-3, hafif çapa):** "Başbakan'dan öğren" maddesine İçtihat Muhakeme Zinciri çapası eklendi: `_oa/cikti/NN-ictihat-muhakeme.md` kayıtları (özellikle ALEYHE-AYIRT'ın AYIRT-ETME gerekçeleri) Çırak için zengin bir ders kaynağı olarak işaretlendi.
- **2026-07 (v3.26 — M3-4 hizalama):** Sürüm işaretçisi ailenin M3 faz-sonu ortak hizalama sürümüne (v3.26) taşındı (`aile_dogrula.py` sürüm tutarlılık uyarısını kapatmak için); bu satırın kendisi dışında bu parçada işlevsel bir değişiklik YOKTUR — gerçek içerik değişiklikleri (varsa) yukarıdaki ayrı kayıtlardadır.
- **2026-08-12 — v0.5.8 fork-prova:** aile_dogrula: YASAK-NÖBETÇİSİ (ağ-import taraması, m.0 icra aracı) + VENDOR testsiz-olamaz denetimi.
- **2026-08-31 (v0.5.14 — denetim raporu B-27):** `aile_dogrula.py --help` / `-h` artık
  KULLANIM HATASI değildir: kullanım metni stdout'a basılır ve **exit 0** dönülür.
  Neden: 32 script taranmış, `rc=0 → 31`, `rc=1 → 1` çıkmış; tek istisna bu scriptti
  (kullanım metni `sys.exit(str)` ile stderr'e gidip exit 1 üretiyordu) ve otomatik
  keşif yapan bir üst katman aracı bunu "bozuk/yok" sayabiliyordu. Argümansız çağrının
  hâlâ kullanım hatası (exit != 0) olması AYNEN korundu.
  Test: `tests/test_v0514_pipeline.py::test_b27_aile_dogrula_help_exit0`.

## v0.5.16 — 2026-09-07 · İki Denetimin İnfazı (birleşim + entegrasyon)

> Kaynak: iki dış denetim raporu (2026-09-06, `_gorus/denetim-2026-09-06-*.md`), 15 sahiplik grubu (`v0516/<grup>` dalları), Yargı Pro hakem teyitleri (`_gorus/denetim-v0516-yargipro-teyit-<grup>.md`). Aşağıdaki blok(lar) ilgili grubun ajan raporundaki `changelog_notu` metninin aynıdır; entegratör notu birleşim sonrası hizalamayı (H1–H5) kaydeder.

### Grup G — kaynak rapor `04-G-uygula.json`

## v0.5.16 — YAPISAL KİLİTLER (Hamle 10) · SÜRÜM İŞARETÇİSİ (P2-10/B-3) · HATA TETİKLİ DAMITMA (P2-8/A-27/A-28)
- **2026-09-06 (v0.5.16 — Hamle 10, K1):** `scripts/aile_dogrula.py` KİLİT-A `bekci_skill_sozlesmesi()`: `oa-pipeline/scripts/pipeline_kayit.py` boşluk bekçilerinin (`_graf_yapisal_bosluk_uyarisi` / `_kiyas_bosluk_uyarisi` / `_usul_bosluk_uyarisi`) `glob.glob(os.path.join(cdiz, "…"))` desenleri, ilgili parçanın (oa-illiyet / oa-kiyas / oa-usul) SKILL.md örnek komutundaki `--json _oa/cikti/<ad>.json` çıktı adıyla fnmatch ile eşleşmezse HATA («bekçi–skill sözleşme kopuşu (K1)»). Saha dersi: oa-illiyet örneği `01-illiyet-denetim.json` yazdırırken bekçi `*graf*.json` okuyordu → üretilen JSON bekçiye hiç girmedi, DURUM.md sahte yeşil gösterdi (B-28 `05-kiyas*` ↔ `*kiyas*.json` aynı sınıf). Depo-dışı kopyada sessiz (VENDOR deseni); bekçi/desen bulunamazsa UYARI (kilit kör kaldı, gizlenmez). Kapatılan bulgu: K1 / Hamle 10(a) — bekçi tarafı B grubu (`*.json` + damga).
- **2026-09-06 (v0.5.16 — Hamle 10(b)):** KİLİT-B `kanonik_doktrin_uyum()`: `oa-illiyet/scripts/grafik_denetim.py` `KANONIK` enum değerlerinin her biri `oa-illiyet/references/illiyet-doktrini.md`'de LİTERAL geçmezse HATA («enum↔doktrin ayrışması: <alan> '<değer>' doktrinde yok»); script yüklenemezse UYARI, doktrin dosyası yoksa HATA. Ölçüm (main 80ac847): 23/23 değer doktrinde, 0 ayrışma — A grubu yeni enum eklerken doktrini güncellemezse kapı kırmızı.
- **2026-09-06 (v0.5.16 — P2-10 / B-3):** `surum_isaretcileri()`: `STATUS.md` «**Sürüm:** X» ve `YOL-HARITASI.md` «## DURUM — son (… · vX)» sürümü `plugin.json` «version» ile eşit değilse UYARI (hata değil — vitrin bayatlığı paketlemeyi durdurmaz, görünür kalır); satır bulunamazsa da UYARI; depo-dışı kopyada sessiz. Test: `tests/test_v0516_G.py::test_surum_isaretcileri` (entegratör bump'ına kadar bilinçli kırmızı).
- **2026-09-06 (v0.5.16 — P2-8 / A-27 / A-28):** SKILL.md «HATA TETİKLİ DAMITMA» bölümü: damıtma yalnız iş-tipi tekrarıyla (≥3) değil avukat revize diff'iyle tetiklenir (A-27: tek revizeden yedi kural çıktı — tekrar eden iş tipi değil hata tipiydi). Kaynak `_oa/defter/avukat-hukmu.jsonl` (B grubu `pipeline_kayit.py --avukat-hukmu KABUL|REVIZYONLA|RET --sebep …`, append-only, kapı değil); tetik: RET/REVİZYONLA kaydı + ürün↔revize diff → aday kural `[sebep] → [ürün] → [avukat] → [kural] → [parça]`, `_oa/dersler/`'e anonim (m.7). Eşik/oran YOK, KAPANIŞ'ta sayım görünür (kaç teslim → kaçına hüküm → KABUL/REVİZYONLA/RET). SICRAMA-NOTU §5 şartı aynen: refleks KABUL başlarsa alan silinmeyi hak eder; oran düşükse üstüne katman kurulmaz. Model/script ayrımı: diff+sayım mekanik, kural çıkarma yargı. «Aile yapı denetimi» paragrafına üç yeni kilit işlendi.
- Testler: `tests/test_v0516_G.py` (22 test — sentetik fikstür, iki yön; gerçek ağaç kopyasında `*.json` ile exit 0 kanıtı; KANONİK gerçek depo ölçümü; SKILL.md belge testleri).

### Entegratör notu (2026-09-07)

- **Entegrasyon (H5/G):** `aile_dogrula.py` KİLİT-A B grubunun DAMGA biçimini (`_denetim_jsonlari(kok, "<arac>")`) tanır: desen ortak süzgeçten (`*.json`) alınır + üretici script `"arac": "<arac>"` damgasını yazmıyorsa HATA (damga kopuşu); `_vakia_delilsiz_unsur_uyarisi` → oa-vakia dördüncü bekçi olarak kapsama alındı. Gerçek depoda kilit kör değil, denetim TEMİZ.

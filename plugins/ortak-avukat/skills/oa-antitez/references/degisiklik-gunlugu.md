# oa-antitez — Değişiklik Günlüğü

(SKILL.md gövdesinden bağlam ekonomisi için taşındı; içerik aynen korunmuştur.)

- **2026-06 (v1):** İlk sürüm (Can yönlendirmesi: antitez = durum farkındalığı + çökertme). Sekiz sabit cepheli deterministik matris motoru; eksiksizlik + bütünlük + teyit denetimi; artık risklerin dürüst raporlanması. İskeleti/denetimi gerçek istihkak senaryosuyla test edildi (kör nokta + teyitsiz dayanak yakalandı).
- **2026-06 (v1.1):** **Gizli cephanelik** kuralı eklendi (Can yönlendirmesi): antitez/zaaf yalnızca dahilidir; sunulmamış (duyulmamış) antiteze karşı sunulan belgede preemptive savunma geliştirilmez; hazır çürütme karşı taraf ileri sürünce devreye alınır. Hipotetik antitez ↔ fiilen ileri sürülmüş antitez ayrımı.
- **2026-06:** Anayasal düstur işlendi (Can yönlendirmesi): **usul esasa üstündür** — süre usul hukukunun parçasıdır; düstur bu parçanın işlevine operatif kuralla bağlandı (yukarıdaki bölüm). Müvekkil menfaati çift yönlü: kendi usul zaafını sıfırla, karşı tarafın usul hatasını (özellikle kaçırılmış süreyi) tespit et ve derhâl kullan.
- **2026-06:** Örnekleme ilkesi bağlandı (anayasal — Can yönlendirmesi): konu sayımları örneklemdir, kapsam tüm Türk hukukudur; işlemeyen örneklem güncellenir, metod sabittir.
- **2026-06:** Çaba/kalite standardı bağlandı (anayasal — Can yönlendirmesi): tasarruf hedef değil; derinlik karmaşıklığa göre yükselir; Opus+High taban.
- **2026-06:** Doğaçlama meşruiyeti bağlandı (anayasal — Can yönlendirmesi): yöntemde serbest doğaçlama (Çapar lafzı), olguda sıfır halüsinasyon/teyit.
- **2026-06:** Başbakan denetimine tabi olma bağlandı (anayasal — Can yönlendirmesi): istisnasız tam işletim, tembellik/kaçış yasağı, dürüst 'yapılamadı' + yeni yöntem.
- **2026-06:** Müvekkil-aleyhi dış çıktı yasağı bağlandı (anayasal — Can): iç analizde dürüst zaaf, dış belgede müvekkil lehine kurgu.

- **2026-07 (v3.16):** Fiziksel aktivasyon — simülasyon yasağı bloğu eklendi (Can yönlendirmesi — komutla tetiklenen parçalar description'dan taklit edilmesin, fiilen çağrılsın): çalıştı = fiilî Skill çağrısı / gerçek script / gerçek MCP çağrısı + DEVİR PAKETİ + pipeline defteri kaydı. Değişiklik günlüğü bağlam ekonomisi için `references/degisiklik-gunlugu.md`'ye taşındı (içerik korunmuştur).
- **2026-07 (v3.17):** Yerel hafıza kuralı bağlandı (Can yönlendirmesi — hafıza ve devir çalışılan klasörde fiziksel yaşar): parçanın kalıcı çıktıları `_oa/` kökünde (defter/devir/teyit/cikti); fiziksel aktivasyon bloğuna işlendi.
- **2026-07 (v3.18):** Çalışma evrakı kuralı: matris `_oa/cikti/07-antitez-matris.json` standart yoluna bağlandı.
- **2026-07:** Çaba/token düsturu GÜNCELLENDİ (Can yönlendirmesi): tasarruf artık HEDEF — ama yalnız mekanik/temsil katmanında ve VERİ-KAYIPSIZ; muhakemede tasarruf edilmez, derinlik/doğrulama/araştırma asla kısılmaz. Aile geneli anayasal güncelleme; deterministik motor: `oa-ingest`.
- **2026-07 (v3.22 — M2-3):** Sürüm işaretçisi ailenin ortak M2-3 entegrasyon sürümüne hizalandı (`aile_dogrula.py` sürüm tutarlılık uyarısını temizlemek için); bu satırın kendisi dışında bu parçada işlevsel bir değişiklik YOKTUR — gerçek içerik değişiklikleri (varsa) yukarıdaki ayrı kayıtlardadır.
- **2026-07 (v3.23 — M3-3, R3):** Protokol adım 3'e köprü cümlesi eklendi — DAMGA=`ALEYHE-AYIRT`'a yalnız karşı tarafın FİİLEN dayandığı/kararda fiilen değerlendirilmiş (yani **DUYULMUŞ**) aleyhe içtihat yükseltilir; henüz duyulmamış aleyhe içtihadı önden ayırt edip sunulan metne yazmak "sunulmamış antiteze preemptive çürütme" yasağının içtihat-özel görünümü olarak açıkça bağlandı (`oa-kiyas/references/ictihat-muhakeme-sablonu.md`).
- **2026-07 (v3.26 — M3-4 hizalama):** Sürüm işaretçisi ailenin M3 faz-sonu ortak hizalama sürümüne (v3.26) taşındı (`aile_dogrula.py` sürüm tutarlılık uyarısını kapatmak için); bu satırın kendisi dışında bu parçada işlevsel bir değişiklik YOKTUR — gerçek içerik değişiklikleri (varsa) yukarıdaki ayrı kayıtlardadır.
- **2026-07-28 (v0.5.5 — M3, Paket D):** `antitez_matris.py`'ye her cephe kaydında `duyulmus` (bool) alanı eklendi — karşı taraf antitezi FİİLEN ileri sürdü mü; yeni `duyulmus_curutmeler()` yardımcı fonksiyonu yalnız DUYULMUŞ+çürütülmüş cepheleri döndürür, `oa-dilekce/scripts/dilekce_denetim.py`'nin [G] ANTİTEZ-CEVAP-ÇAPASI advisory kapısı bunu tüketir (dış/iç ayrımı: hipotetik antitez cephanelikte kalır).

## v0.5.13 — CELSE KARTI (duruşma ürünü; yeni parça DEĞİL)
- Cephanelikten türetilen tek sayfalık `_oa/cikti/NN-celse-karti.md`: celse
  hedefleri, beklenen antiteze sözlü karşılıklar, tutanağa geçirilecek beyanlar,
  istenecek ara kararlar. DAHİLİ filigranı zorunlu (teslim kapısı bunu mekanik
  dışlar — oa-kontrol v0.5.13). Celse sonrası tutanak karşılaştırması
  MODEL-DENETİMLİ CHECKLİST'tir, öneri üretir; düzeltme talebi avukatın takdiri.

## v0.5.8.5 — 2026-08-16

- **A1 TRİYAJ — ALEYHE'nin adresi CEPHANELİKTİR:** SKILL'e yeni bölüm. ALEYHE damgalı her karar cephanelik ürününe (matris / `07-antitez-cephanelik.md`) FİİLEN İŞLENİR — kütükte damgalı durması yetmez. Mekanik ayna: [G6] TERS DENETİMİ (`ictihat_muhakeme_denetim.py`) kütükte son damgası ALEYHE olup cephanelik ürünlerinde (`07-antitez*`) hiç anılmayan kararı "FARKINDALIK KAYBI" uyarısıyla görünür kılar (advisory — bloklamaz).
- **Duyulma anının kütük kaydı:** karşı taraf cephanelikteki aleyhe kararı fiilen ileri sürünce `oa_hafiza.py teyit --duyulmus` ile `DUYULMUS=EVET` işlenir; ALEYHE-AYIRT yükseltmesi ancak bu işaret + dilekçede ayırt/çürütme bağlamıyla dilekçeye çıkabilir ([G6] dar istisnası — destek atfı olarak asla). Duyulmamış aleyhe karar cephanelikte dahili kalır (m.6) — mevcut R3 köprüsünün mekanik ayağı tamamlandı.
- **Tam-metin şartı çürütmede de geçerli:** arama sonucu parçasından alıntı YASAKTIR; ayırt/çürütme gerekçesi kararın GETİR dökümüne dayanır.

## v0.5.14 — 2026-08-31

- **[B-26] `--iskelet` artık geçerli JSON üretir.** Kanıt (denetim, koşturuldu): `antitez_matris.py --iskelet > dosya.json` sonrası `json.load` **JSONDecodeError** veriyordu (başta insan raporu, sonda "Doldurduktan sonra: …" düz metni). Bu, `dilekce_denetim.py`'nin [G] ANTİTEZ-CEVAP-ÇAPASI kapısının okuduğu `_oa/cikti/*antitez*.json` dosyasının doğal üretim yoluydu — en doğal kullanım sessizce kullanılamaz dosya üretiyor, hata bir sonraki adımda çıkıyordu. Matris şablonu STDOUT'a, cephe listesi ve açıklamalar STDERR'e taşındı. Sekiz cephe kümesi, alan adları ve `duyulmus` varsayılanı DEĞİŞMEDİ.
- **[B-23] Girdi sağlamlaştırması.** `--dogrula` ile verilen JSON'un kökü sözlük değilse (null / `[]` / dize) eski kod ham `AttributeError` traceback'i veriyordu; artık tek satırlık hata + exit 1. `cepheler` liste değilse boş sayılır; sözlük olmayan cephe kayıtları düşürülür ama SESSİZ DEĞİL — `ŞEMA HATASI` bloğunda "N kayıt sözlük değil — denetime alınmadı" satırıyla görünür ve `saglikli` hükmünü bozar.
- **DEĞİŞMEYEN:** `duyulmus_curutmeler()` sözleşmesi (fail-safe, asla çökmez) · `STANDART_CEPHELER` sekizlisi · `GUC_DEGERLERI`/`DAYANAK_DURUMLARI` enum'ları · `dogrula()` sonunda exit kodu bulunmaması (B-12'nin exit-sözleşmesi ayağı bu pakette UYGULANMADI — bugün tek programatik tüketici exit koduna bakmıyor; sözleşme değişikliği ayrı bir avukat kararıdır).
- **Kırılan mevcut test:** yok.

## v0.5.16 — 2026-09-07 · İki Denetimin İnfazı (birleşim + entegrasyon)

> Kaynak: iki dış denetim raporu (2026-09-06, `_gorus/denetim-2026-09-06-*.md`), 15 sahiplik grubu (`v0516/<grup>` dalları), Yargı Pro hakem teyitleri (`_gorus/denetim-v0516-yargipro-teyit-<grup>.md`). Aşağıdaki blok(lar) ilgili grubun ajan raporundaki `changelog_notu` metninin aynıdır; entegratör notu birleşim sonrası hizalamayı (H1–H5) kaydeder.

### Grup I2 — kaynak rapor `09-I2-uygula.json`

## v0.5.16 — BİLİRKİŞİ/TEKNİK CEPHESİ + HÂKİM LENSİ + HAT SIRASI HİZALAMASI (Grup I2)\n\n- **P1-5 / A-20 — 9. cephe `bilirkisi_teknik`** (`scripts/antitez_matris.py` → `STANDART_CEPHELER`): raporun kırılma noktaları (HMK m.279/2 zorunlu içerik), tek imza/heyet (m.279/3), hukuki nitelendirme yasağı (m.279/4), itiraz stratejisi (m.281 — tebliğden iki hafta; 7251/24 ek süre; süre ayağı `oa-sure --tur usul`), uzman görüşü (m.293), keşif dayanağı. Norm metinleri Mevzuat MCP'den okundu (`mevzuat_getir` mevzuatgov:kanun:5:6100 m.279/281/293, teyit 2026-09-06). Saha dersi: çoğu dosyada fiilî karar mercii bilirkişi raporudur; sekiz cephe raporu hiçbir yerde ZORUNLU taramıyordu. **Bilinçli etki:** eski sekiz cepheli matrisler `--dogrula`da «AÇIK CEPHE: bilirkisi_teknik» alır — sessiz uyum yok, kör nokta görünür. `--iskelet` 9 cephe; `duyulmus_curutmeler()` ve `oa-dilekce` [G] kapısının okuduğu `_oa/cikti/*antitez*.json` sözleşmesi değişmedi (kanıt: `tests/test_v0516_I2.py`).\n- **A-21 — HÂKİM LENSİ** (`SKILL.md` Protokol 5): çürütme brifine ikinci pas — «hâkim bu dosyayı nasıl kapatmak ister: iş yükü, gerekçe alışkanlığı, daire eğilimi; on dakikada okuyan hâkim tezi anlıyor mu». Cephe değil lens: script denetlemez; daire eğilimi iddiası `oa-ictihat`/`oa-alan` teyidi olmadan yazılmaz. `oa-kontrol` C2 brifiyle aynı cümle, iki ayrı an.\n- **P0-3 — Kompozisyon hizalaması** (`SKILL.md` «Kompozisyon (iki konum)»): erken konum = SABİT HAT ADIM 6 (KIYAS sonrası, STRATEJİ adım 7'den ÖNCE); **`oa-strateji` antitez çıktısını girdi alır** — antitez stratejiden sonra koşarsa strateji kör kurulur. Geç konum = YAZIM (8) sonrası / KONTROL (9) öncesi; `07-antitez*` evrak öneki [G]/pipeline önkoşul tablosuyla sözleşmeli, ADIM numarası değişse de değişmez.\n- Testler: `tests/test_v0516_I2.py` (11 yeni); `tests/test_v0514_muhakeme.py` iskelet cephe sayısı 8→9 (docstring'de gerekçeli karakterizasyon değişikliği).

### Entegratör notu (2026-09-07)

- **Entegrasyon (H2/P0-3):** çalışma-evrakı öneki `06-antitez-*` (matris/cephanelik) — sabit hat adım 6; ≤v0.5.15 adı `07-antitez-*` pipeline bekçisi ve [G] kapısı (`*antitez*.json`) tarafından geriye uyumla kabul edilir.

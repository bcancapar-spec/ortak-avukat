# oa-gizlilik — Değişiklik Günlüğü

(SKILL.md gövdesinden bağlam ekonomisi için taşındı; içerik aynen korunmuştur.)

- **2026-06:** Anayasal düstur işlendi (Can yönlendirmesi): **usul esasa üstündür** — süre usul hukukunun parçasıdır; düstur bu parçanın işlevine operatif kuralla bağlandı (yukarıdaki bölüm). Müvekkil menfaati çift yönlü: kendi usul zaafını sıfırla, karşı tarafın usul hatasını (özellikle kaçırılmış süreyi) tespit et ve derhâl kullan.
- **2026-06:** Anonimleştirme süzgeci bağlandı (anayasal kural — Can yönlendirmesi): skill metinlerine tasarımcı dışında isim/dava/dosya atfı giremez; içerik soyut örüntü olarak taşınır.
- **2026-06:** Örnekleme ilkesi bağlandı (anayasal — Can yönlendirmesi): konu sayımları örneklemdir, kapsam tüm Türk hukukudur; işlemeyen örneklem güncellenir, metod sabittir.
- **2026-06:** Çaba/kalite standardı bağlandı (anayasal — Can yönlendirmesi): tasarruf hedef değil; derinlik karmaşıklığa göre yükselir; Opus+High taban.
- **2026-06:** Doğaçlama meşruiyeti bağlandı (anayasal — Can yönlendirmesi): yöntemde serbest doğaçlama (Çapar lafzı), olguda sıfır halüsinasyon/teyit.
- **2026-06:** Başbakan denetimine tabi olma bağlandı (anayasal — Can yönlendirmesi): istisnasız tam işletim, tembellik/kaçış yasağı, dürüst 'yapılamadı' + yeni yöntem.

- **2026-07 (v3.16):** Fiziksel aktivasyon — simülasyon yasağı bloğu eklendi (Can yönlendirmesi — komutla tetiklenen parçalar description'dan taklit edilmesin, fiilen çağrılsın): çalıştı = fiilî Skill çağrısı / gerçek script / gerçek MCP çağrısı + DEVİR PAKETİ + pipeline defteri kaydı. Değişiklik günlüğü bağlam ekonomisi için `references/degisiklik-gunlugu.md`'ye taşındı (içerik korunmuştur).
- **2026-07 (v3.17):** Yerel hafıza kuralı bağlandı (Can yönlendirmesi — hafıza ve devir çalışılan klasörde fiziksel yaşar): parçanın kalıcı çıktıları `_oa/` kökünde (defter/devir/teyit/cikti); fiziksel aktivasyon bloğuna işlendi.
- **2026-07 (v3.18):** Çalışma evrakı kuralı: tarama girdisi `_oa/cikti/gizlilik-tara.txt` standart yoluna bağlandı.
- **2026-07:** Çaba/token düsturu GÜNCELLENDİ (Can yönlendirmesi): tasarruf artık HEDEF — ama yalnız mekanik/temsil katmanında ve VERİ-KAYIPSIZ; muhakemede tasarruf edilmez, derinlik/doğrulama/araştırma asla kısılmaz. Aile geneli anayasal güncelleme; deterministik motor: `oa-ingest`.
- **2026-07 (v3.22 — M2-3):** Sürüm işaretçisi ailenin ortak M2-3 entegrasyon sürümüne hizalandı (`aile_dogrula.py` sürüm tutarlılık uyarısını temizlemek için); bu satırın kendisi dışında bu parçada işlevsel bir değişiklik YOKTUR — gerçek içerik değişiklikleri (varsa) yukarıdaki ayrı kayıtlardadır.
- **2026-07 (v3.26 — M3-4 hizalama):** Sürüm işaretçisi ailenin M3 faz-sonu ortak hizalama sürümüne (v3.26) taşındı (`aile_dogrula.py` sürüm tutarlılık uyarısını kapatmak için); bu satırın kendisi dışında bu parçada işlevsel bir değişiklik YOKTUR — gerçek içerik değişiklikleri (varsa) yukarıdaki ayrı kayıtlardadır.

## v0.5.8.5 — 2026-08-16

- **E2 bağlam istisnaları (`gizlilik_tara.py` — saha yanlış-pozitif onarımı):** (a) "rapor" TEK BAŞINA sağlık verisi tetiklemez (bilirkişi/ek/kök rapor hukuk metninin gündelik kelimesi) — yalnız ±60 karakter pencerede sağlık-bağlam komşusu (çekirdek kelime ya da doktor/hekim/heyet) varsa sinyal; çekirdek sağlık kelimeleri bağımsız tetiklenmeye devam eder (yanlış negatif üretmez). (b) Mersis biçim kuralı: 16 hane + 0 başlangıcı kart DEĞİL (IIN 0 ile başlamaz); Luhn tutsa bile kart sayılmaz, [BİLGİ] kanalına düşer. (c) Telefon zayıf-şiddet HASSAS deseni eklendi (05XX/+90); ±40 karakterde belge/doküman-id etiketi (documentId/evrak no/belge no/doğrulama kodu/barkod) taşıyan diziler ayrışır — etiketi olmayan her telefon-biçimli dizi yine yakalanır (fail-closed yön).
- **DENY-OVERRIDE protokolü:** DENY yalnız `--override-onay avukat` + `--override-gerekce` (≥30 karakter) ile aşılır; gerekçesiz override hiç taramadan fail-closed DENY (exit 2). Aşım `_oa/defter/istisna-kayitlari.jsonl`'a (`tur=gizlilik-deny-override`, `onay=avukat`, ortak şema) kaydedilir; rapor AYNEN basılır (görünürlük kaybolmaz). SKILL'e açık kural: model bu parametreyi kendi inisiyatifiyle EKLEYEMEZ — avukattan açık talimat + gerekçe olmadan DENY nihaidir; önce alternatif önerilir.
- **[BİLGİ] satırı genelleşti:** bilgi kanalı artık yalnız esas/karar no değil, engellemeyen tüm desenleri (Mersis dahil) taşır — metin buna göre güncellendi.

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

## v0.5.16 — 2026-09-07 · İki Denetimin İnfazı (birleşim + entegrasyon)

> Kaynak: iki dış denetim raporu (2026-09-06, `_gorus/denetim-2026-09-06-*.md`), 15 sahiplik grubu (`v0516/<grup>` dalları), Yargı Pro hakem teyitleri (`_gorus/denetim-v0516-yargipro-teyit-<grup>.md`). Aşağıdaki blok(lar) ilgili grubun ajan raporundaki `changelog_notu` metninin aynıdır; entegratör notu birleşim sonrası hizalamayı (H1–H5) kaydeder.

### Grup D — kaynak rapor `32-hakem-uygula.json`

### oa-pipeline (oa_hafiza.py) — v0.5.16/D
- **K5 [Hamle 4] AKIBET üreticisi:** `teyit --akibet kesinlesti|kesinlesmedi|bozuldu|kaldirildi|geri_cevrildi --akibet-kaynak "<künye|arac:<ad>>"`. Kaynak zorunlu (RET); `arac:<ad>` → «araç», aksi «avukat beyanı» sınıfı — kütükte (`AKIBET=<enum> AKIBET-KAYNAK=<sınıf>: …`, DAMGA= ile aynı sütun) ve muhakeme kaydında (`**AKIBET:**` / `**AKIBET-KAYNAK:**`, KUNYE/DAMGA bloğunda tek satır) görünür. Yalnız GETİR + `--damga`; ARAMA/mevzuat kaydında RET, tek başına `--akibet-kaynak` RET (sessiz düşme yok). Otomatik akış: `--sonuc` metnindeki KESİNLEŞTİ/KESİNLEŞMEDİ (harf/İ-I katlamalı) → akıbet + `arac:<arac>` kaynağı, `[BİLGİ]` ile görünür. `bozuldu|kaldirildi` + LEHE → `[BİLGİ] … [G5-AKIBET] kapısı dilekçede BLOKLAR` (kayıt yazılır; kapı oa-kontrol'de). Enjeksiyon katmanı `AKIBET=`/`AKIBET-KAYNAK=` tokenlarını ve `**AKIBET:**` satır belirteçlerini de kaçışlar. C2 okuyucusuyla (`AKIBET_LINE_RE`, `kutukten_son_akibet`) birebir round-trip.
- **P1-8 / A-11 / B-5 senkron klasör uyarısı:** `init`, çalışma kökünün mutlak yolunu bulut senkron desenlerine (OneDrive, «OneDrive - …», Google Drive/GoogleDrive/My Drive, Dropbox, iCloudDrive/iCloud Drive, Box Sync, Nextcloud, Syncthing; parça düzeyi, harf duyarsız) karşı tarar; eşleşmede görünür UYARI (Av.K. m.36, KVKK m.6/m.9 — Mevzuat MCP teyit 2026-09-06/07) + `_oa/defter/senkron-uyari.json` `{yol, desen, zaman}`; bayat JSON `[BİLGİ]` ile kaldırılır. Bloklamaz; DURUM.md türetimi pipeline_kayit.py'de.

### oa-gizlilik — v0.5.16/D
- SKILL.md «Senkron klasör riski» bölümü: meslek sırrının en sık sızma yolu dış çağrı değil senkron klasördür; Layer 0 dış çağrıyı süzer, cihazı/klasörü korumaz; `_oa/` + cephanelik yurt dışı buluta süzgeçsiz gider; hukuki temel 1136 s. Av.K. m.36, KVKK m.6 ve m.9 (Mevzuat MCP teyit 2026-09-06, yeniden 2026-09-07); öneri P2→P1 şifreli konteyner (VeraCrypt / BitLocker); modelin işi uyarıyı bir kez açıkça söylemek, karar avukatın.
- references/gizlilik-desenleri.md: KVKK m.9 normu; «Senkron klasör desenleri» tablosu (örneklem — anayasa m.3), parça-düzeyi eşleşme kuralı, `oa_hafiza.py init` uyarı işaretçisi ve JSON izi.

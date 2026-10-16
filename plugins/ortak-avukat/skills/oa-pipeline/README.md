# oa-pipeline

*Ortak Avukat ailesi · v3.26 · bir `oa-*` parçası*

Ortak Avukat sisteminin ORKESTRASYON / UÇTAN UCA AKIŞ parçası. Bir dosyayı baştan sona işlerken oa- parçalarını doğru sırada zincirler: MANİFEST → ALIM → KONUMLAMA → ARAŞTIRMA → OLGU/DELİL → KIYAS → ANTİTEZ → STRATEJİ → YAZIM → KONTROL → KAPANIŞ, her adımın çıktısını bir sonrakine taşıyarak; usul/illiyet/gizlilik katmanları ve ceza dalı (oa-mudafii / oa-musteki-vekili) her aşamayı sarar. Basit dosyada sabit hat; karmaşık/atipik dosyada dinamik mod (her adımda "yeterli bilgi var mı, hangi parça gerekli" değerlendirmesi). Kritik kavşakta (düşük başarı olasılığı, eksik delil, yüksek risk) durur ve avukata sorar. "Bu dosyayı baştan sona ele al", "tam analiz yap", "dosyayı işle", "uçtan uca", "nereden başlayalım ve nasıl ilerleyelim" türü her işte — ve kapsamlı bir dosya/dava ilk kez ele alınırken, kullanıcı açıkça istemese bile — tetikle. Tüm oa- parçalarını (interview, illiyet, vakia, alan, ictihat, kiyas, strateji, antitez, sure, dilekce, kontrol) bir omurgaya bağlar.

## Deterministik scriptler

- `scripts/manifest_olustur.py`
- `scripts/oa_hafiza.py`
- `scripts/pipeline_kayit.py`
- `scripts/udf_metin.py`
- `scripts/tam_tur.py`
- `scripts/capraz_denetim.py`
- `scripts/okuma_kapisi.py`
- `scripts/oa_metrik.py`

> Scriptler modelin muhakemesini **denetler** (eksiksizlik/tutarlılık); model kurar, script sağlamasını yapar.

## Referanslar

- `references/degisiklik-gunlugu.md`
- `references/pipeline-durum-sablonu.md`
- `references/muvekkil-bilgilendirme-sablonu.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-pipeline` ile de çağrılabilir.

## Teyit kanalı (resmî kaynak beyaz listesi)

Ailenin içtihat/mevzuat doğrulaması **resmî portallardan** yapılır; model bu portallara Claude Code'un web araçlarıyla (**WebFetch** tam metin / **WebSearch** keşif) ulaşır. Kurulacak ya da bağlanacak bir sunucu yoktur — eklenti üçüncü taraf MCP sunucusu ilan etmez (2026-10-15 avukat kararı). Teyidin kanıtı resmî portalın adresi ve diske inmiş tam metindir; beyaz liste: [resmî kaynaklar](../ortak-avukat/references/resmi-kaynaklar.md).

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

# oa-mudafii

*Ortak Avukat ailesi · v3.26 · bir `oa-*` parçası*

Ortak Avukat sisteminin CEZA MÜDAFİLİĞİ (sanık/şüpheli savunması) kimlik ve orkestra parçası. Bir ceza soruşturması, kovuşturması veya kanun yolunda sanık/şüpheli müdafiliği üstlenildiğinde DEVREYE GİR: savunma duruşunu (masumiyet karinesi, şüpheden sanık yararlanır, ispat yükü iddia makamında) kur; suçun MADDİ ve MANEVİ unsurlarını tek tek denetle; delil cephesini (doğrudan doğruyalık/CMK m.217, hukuka aykırı delil, eksik inceleme, atfı cürüm beyanı, dijital/ses aidiyeti) tara; kanun yolu süresini nöbette tut. "Sanık/şüpheli müdafiiyiz", "savunma dilekçesi", "iddianameye karşı", "istinaf/temyiz/itiraz", "ifade/sorgu", "gözaltı/tutukluluk", "beraat", "HAGB", "unsurları oluşmadı", "ceza dosyası" türü her işte — kullanıcı açıkça "müdafii" demese bile bir ceza dosyasında sanık/şüpheli temsil edildiği belli olduğunda — tetikle. ortak-avukat ve oa-pipeline ile takım oynar; oa- parçalarını savunma merceğiyle çağırır.

## Yapı

Bu parça saf metin-disiplinidir (deterministik script içermez); protokolleri `SKILL.md` gövdesindedir.

## Referanslar

- `references/degisiklik-gunlugu.md`
- `references/savunma-kontrol-listesi.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-mudafii` ile de çağrılabilir.

## Teyit kanalı (resmî kaynak beyaz listesi)

Ailenin içtihat/mevzuat doğrulaması **resmî portallardan** yapılır; model bu portallara Claude Code'un web araçlarıyla (**WebFetch** tam metin / **WebSearch** keşif) ulaşır. Kurulacak ya da bağlanacak bir sunucu yoktur — eklenti üçüncü taraf MCP sunucusu ilan etmez (2026-10-15 avukat kararı). Teyidin kanıtı resmî portalın adresi ve diske inmiş tam metindir; beyaz liste: [resmî kaynaklar](../ortak-avukat/references/resmi-kaynaklar.md).

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

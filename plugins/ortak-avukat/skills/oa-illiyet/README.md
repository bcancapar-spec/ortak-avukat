# oa-illiyet

*Ortak Avukat ailesi · v3.26 · bir `oa-*` parçası*

Ortak Avukat sisteminin NEDENSELLİK / İLİŞKİ / İLLİYET parçası ve tüm aileyi kuşatan kesişen katmanı. Bir uyuşmazlıkta kişilerin, şirketlerin, kamu kurumlarının, nesnelerin ve delillerin birbirleriyle BAĞINI, İLİŞKİSİNİ ve neden-sonuç (illiyet) zincirini yönlü graf olarak modellemek için DEVREYE GİR. Müşteki↔şüpheli, katılan↔sanık↔hükümlü, davacı↔davalı, alacaklı↔borçlu↔üçüncü kişi, asıl-alt işveren, ortak-müdür-şirket, fiil→netice→zarar ilişkilerini kur; kesme noktalarını (mücbir sebep, mağdur/üçüncü kişi kusuru), köprü düğümleri (muvazaa/perde sinyali), yük taşıyan bağı ve ispat boşluklarını deterministik tespit et. "kim kime nasıl bağlı", "neden-sonuç", "illiyet bağı", "ilişki haritası", "kesilme savunması" türü her işte — kullanıcı açıkça istemese bile bir dosya/dilekçe/tez analiz edilirken — tetikle. Bağımsız çalışır; ortak-avukat ve diğer oa- parçalarıyla (oa-vakia, oa-kiyas, oa-antitez, oa-dilekce, oa-kontrol) takım oynar.

## Deterministik scriptler

- `scripts/grafik_denetim.py`

> Scriptler modelin muhakemesini **denetler** (eksiksizlik/tutarlılık); model kurar, script sağlamasını yapar.

## Referanslar

- `references/cikti-blogu.md`
- `references/degisiklik-gunlugu.md`
- `references/illiyet-doktrini.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-illiyet` ile de çağrılabilir.

## Teyit kanalı (resmî kaynak beyaz listesi)

Ailenin içtihat/mevzuat doğrulaması **resmî portallardan** yapılır; model bu portallara Claude Code'un web araçlarıyla (**WebFetch** tam metin / **WebSearch** keşif) ulaşır. Kurulacak ya da bağlanacak bir sunucu yoktur — eklenti üçüncü taraf MCP sunucusu ilan etmez (2026-10-15 avukat kararı). Teyidin kanıtı resmî portalın adresi ve diske inmiş tam metindir; beyaz liste: [resmî kaynaklar](../ortak-avukat/references/resmi-kaynaklar.md).

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

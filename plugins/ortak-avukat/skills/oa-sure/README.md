# oa-sure

*Ortak Avukat ailesi · v3.26 · bir `oa-*` parçası*

Ortak Avukat sisteminin SÜRE parçası. Türk hukukunda her süreye bağlı işlemde — yalnızca usul (istinaf, temyiz, AYM başvuru, itiraz, cevap, dava açma; HMK/CMK/İYUK) değil, MADDİ HUKUK süreleri de (zamanaşımı/hak düşürücü: TBK, TMK, TTK, 6183 ve diğer kanun/yönetmelikler — ör. TTK m.23/c, m.749, m.814; TBK m.39, m.82; TMK m.571; 6183 m.58) dahil — "süre ne kadar / ne zaman doluyor / kaçırdım mı / zamanaşımı" türü her işte DEVREYE GİR. Süre kuralını Mevzuat MCP'den teyit et, sonra başlangıç tarihinden son günü deterministik hesaplamak için bundled scripti `--tur usul|maddi` ile kullan (maddi sürelerde adli tatil uygulanmaz). Kullanıcı açıkça "süre hesapla" demese bile, dosyada bir süre/zamanaşımı söz konusuysa tetikle. Bağımsız kullanılabilir; `ortak-avukat` kimliğiyle birlikte takım hâlinde çalışır.

## Deterministik scriptler

- `scripts/hesapla_sure.py`
- `scripts/sure_nobetci.py` (nöbetçi; her oturum açılışında `--kok .`; exit 0/3/1; `--iptal/--gerekce` append-only)
- veri: `scripts/sure_kurallari.json`, `scripts/tatiller.json`

> Scriptler modelin muhakemesini **denetler** (eksiksizlik/tutarlılık); model kurar, script sağlamasını yapar.

## Referanslar

- `references/degisiklik-gunlugu.md`
- `references/sure-cizelgesi.md`
- `references/baslangic-kapisi.md` (v0.5.18 — hangi olay, hangi kanıt: tebliğ/tefhim/öğrenme kapısı)

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-sure` ile de çağrılabilir.

## Teyit kanalı (resmî kaynak beyaz listesi)

Ailenin içtihat/mevzuat doğrulaması **resmî portallardan** yapılır; model bu portallara Claude Code'un web araçlarıyla (**WebFetch** tam metin / **WebSearch** keşif) ulaşır. Kurulacak ya da bağlanacak bir sunucu yoktur — eklenti üçüncü taraf MCP sunucusu ilan etmez (2026-10-15 avukat kararı). Teyidin kanıtı resmî portalın adresi ve diske inmiş tam metindir; beyaz liste: [resmî kaynaklar](../ortak-avukat/references/resmi-kaynaklar.md).

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

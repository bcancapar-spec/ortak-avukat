# oa-usta

*Ortak Avukat ailesi · v3.26 · bir `oa-*` parçası*

Ortak Avukat sisteminin META / SKILL-DAMITMA parçası. Avukat bir iş tipini elle birkaç kez çözdüğünde (belirli bir ihtarname, başvuru, dilekçe kalıbı, tekrarlayan analiz), o oturumların ortak desenini çıkarıp yeniden kullanılabilir bir oa- skill TASLAĞINA damıt. Tekrarlayan işi kurumsallaştırır. "Bunu her seferinde yapıyorum, skill yapalım", "bu işi kalıba dök", "şunu otomatikleştir", "tekrar eden bu süreci yetenek haline getir", "yeni bir oa- parçası tasarla" türü her işte — ve aynı tip iş üçüncü kez tekrarlandığında, kullanıcı açıkça istemese bile — tetikle. Üretilen taslak daima oa- aile konvansiyonlarına (anayasal süzgeç, MCP doğrulama, model kurar/script denetler ayrımı, karar materyali) uyar. Bağımsız çalışır; skill-creator formatını izler, oa-kontrol (güvenlik denetimi) ile takım oynar.

## Deterministik scriptler

- `scripts/aile_dogrula.py`

> Scriptler modelin muhakemesini **denetler** (eksiksizlik/tutarlılık); model kurar, script sağlamasını yapar.

## Referanslar

- `references/degisiklik-gunlugu.md`
- `references/oa-skill-iskeleti.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-usta` ile de çağrılabilir.

## Teyit kanalı (resmî kaynak beyaz listesi)

Ailenin içtihat/mevzuat doğrulaması **resmî portallardan** yapılır; model bu portallara Claude Code'un web araçlarıyla (**WebFetch** tam metin / **WebSearch** keşif) ulaşır. Kurulacak ya da bağlanacak bir sunucu yoktur — eklenti üçüncü taraf MCP sunucusu ilan etmez (2026-10-15 avukat kararı). Teyidin kanıtı resmî portalın adresi ve diske inmiş tam metindir; beyaz liste: [resmî kaynaklar](../ortak-avukat/references/resmi-kaynaklar.md).

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

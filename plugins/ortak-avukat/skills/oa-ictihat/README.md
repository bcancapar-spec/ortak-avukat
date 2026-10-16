# oa-ictihat

*Ortak Avukat ailesi · v3.26 · bir `oa-*` parçası*

Ortak Avukat sisteminin İÇTİHAT/MEVZUAT ARAMA parçası. Türk hukukunda içtihat (Yargıtay/BAM/Danıştay/AYM), mevzuat (kanun/yönetmelik/tebliğ) veya doktrin (makale/tez) araştırması; bir kararın/maddenin künyesini doğrulama; "şu konuda Yargıtay ne diyor", "şu maddeyi bul", "emsal karar" türü her işte DEVREYE GİR. MCP araçlarının (Yargı/Bedesten, Mevzuat, AYM, Literatür, YokTez) doğru sorgu kalıplarını, üç ayrı arama dialect'ini, bilinen indeks sınırlarını ve fallback zincirlerini kullan. Kullanıcı açıkça "araştır" demese bile, doğrulanmış kaynak gerektiren her hukuki argümanda tetikle. Bağımsız çalışır; `ortak-avukat` ve diğer oa- parçalarıyla takım oynar.

## Deterministik scriptler

- `scripts/kanun_yolu_zinciri.py` — üst mahkeme kararı metninden kanun yolu zincirini (BAM → ilk derece künyeleri) çıkarır, iniş kararını MEKANİK verir (`redakte` görünür), `--suzgec` ile `ictihat_ara` sonuçlarını BAM/daire/yıl ile istemci tarafında süzer (v0.5.16).

> Scriptler modelin muhakemesini **denetler** (yapısal/mekanik); model kurar, script sağlamasını yapar. Arama disiplini ve protokoller `SKILL.md` gövdesindedir.

## Referanslar

- `references/degisiklik-gunlugu.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-ictihat` ile de çağrılabilir.

## Teyit kanalı (resmî kaynak beyaz listesi)

Ailenin içtihat/mevzuat doğrulaması **resmî portallardan** yapılır; model bu portallara Claude Code'un web araçlarıyla (**WebFetch** tam metin / **WebSearch** keşif) ulaşır. Kurulacak ya da bağlanacak bir sunucu yoktur — eklenti üçüncü taraf MCP sunucusu ilan etmez (2026-10-15 avukat kararı). Teyidin kanıtı resmî portalın adresi ve diske inmiş tam metindir; beyaz liste: [resmî kaynaklar](../ortak-avukat/references/resmi-kaynaklar.md).

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

# oa-sozlesme

*Ortak Avukat ailesi · v3.26 · bir `oa-*` parçası*

Ortak Avukat sisteminin SÖZLEŞME parçası. Her tür sözleşmenin HAZIRLANMASI (tahrir), İNCELENMESİ (karşı taraf taslağı), REVİZESİ ve MÜZAKERESİNDE devreye gir: NDA, hizmet/eser, kira, satış/devir, ortaklık/hissedarlar, iş, vekâlet, bayilik/franchise, lisans, protokol/sulh, atipik-karma sözleşmeler. Kloz kapsam denetimi (deterministik script), risk matrisi, tuzak taraması, redline + fallback pozisyonları, genel işlem koşulları (TBK m.20-25) + Rekabet (rekabet yasağı / münhasırlık) + KVKK kloz denetimi, şekil şartı ve imza yetkisi taraması. "Sözleşme hazırla", "şu taslağı incele", "NDA geldi", "kloz", "revize", "redline", "müzakere" türü her işte — kullanıcı sözleşme tipini anmasa bile ortada akdî bir metin varsa — tetikle. Bağımsız çalışır; oa-ictihat (teyitli norm/emsal), oa-antitez (karşı taraf okuması), oa-sure (süre/temerrüt), oa-strateji (müzakere planı) ve oa-kontrol (teslim denetimi) ile takım oynar.

## Deterministik scriptler

- `scripts/sozlesme_denetim.py`

> Scriptler modelin muhakemesini **denetler** (eksiksizlik/tutarlılık); model kurar, script sağlamasını yapar.

## Referanslar

- `references/degisiklik-gunlugu.md`
- `references/kloz-cetveli.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-sozlesme` ile de çağrılabilir.

## Teyit kanalı (resmî kaynak beyaz listesi)

Ailenin içtihat/mevzuat doğrulaması **resmî portallardan** yapılır; model bu portallara Claude Code'un web araçlarıyla (**WebFetch** tam metin / **WebSearch** keşif) ulaşır. Kurulacak ya da bağlanacak bir sunucu yoktur — eklenti üçüncü taraf MCP sunucusu ilan etmez (2026-10-15 avukat kararı). Teyidin kanıtı resmî portalın adresi ve diske inmiş tam metindir; beyaz liste: [resmî kaynaklar](../ortak-avukat/references/resmi-kaynaklar.md).

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

# oa-interview

*Ortak Avukat ailesi · v3.20 · bir `oa-*` parçası*

Ortak Avukat sisteminin İLK İNCELEME / MÜLAKAT parçası. Yeni bir dosya, dava, uyuşmazlık veya hukuki mesele ilk kez önüne geldiğinde — DERİNLEMESİNE ANALİZE GİRMEDEN ÖNCE — durup yapılandırılmış sorular sorarak maddi gerçeği, belgeleri, süreyi, müvekkil hedefini ve zaafları topla. Özellikle Claude Cowork'te uzun analiz/belge üretimine başlamadan önce bu alım aşamasını çalıştır. "Şu dosyaya bakalım", "yeni bir dava", "bu konuda ne yapabiliriz", bir olay anlatımı veya Cowork'te yeni bir iş başlangıcı → kullanıcı açıkça "soru sor" demese bile tetikle. Bağımsız çalışır; akışın EN BAŞINDADIR, sonra `oa-alan`/`oa-ictihat`/`oa-dilekce` parçalarına devreder.

## Yapı

Bu parça saf metin-disiplinidir (deterministik script içermez); protokolleri `SKILL.md` gövdesindedir.

## Referanslar

- `references/degisiklik-gunlugu.md`
- `references/soru-bankasi.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-interview` ile de çağrılabilir.

## Yargı Pro bağlantısı (verimli kullanım için gerekli)

Ailenin içtihat/mevzuat doğrulaması **Yargı Pro** MCP'sine dayanır. Claude Code'da **connectors** bölümünden şu adresi ekleyip bağlanın:

```
https://yargi.betaspacestudio.com/mcp
```

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

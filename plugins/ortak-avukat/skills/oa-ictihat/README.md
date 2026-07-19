# oa-ictihat

*Ortak Avukat ailesi · v3.20 · bir `oa-*` parçası*

Ortak Avukat sisteminin İÇTİHAT/MEVZUAT ARAMA parçası. Türk hukukunda içtihat (Yargıtay/BAM/Danıştay/AYM), mevzuat (kanun/yönetmelik/tebliğ) veya doktrin (makale/tez) araştırması; bir kararın/maddenin künyesini doğrulama; "şu konuda Yargıtay ne diyor", "şu maddeyi bul", "emsal karar" türü her işte DEVREYE GİR. MCP araçlarının (Yargı/Bedesten, Mevzuat, AYM, Literatür, YokTez) doğru sorgu kalıplarını, üç ayrı arama dialect'ini, bilinen indeks sınırlarını ve fallback zincirlerini kullan. Kullanıcı açıkça "araştır" demese bile, doğrulanmış kaynak gerektiren her hukuki argümanda tetikle. Bağımsız çalışır; `ortak-avukat` ve diğer oa- parçalarıyla takım oynar.

## Yapı

Bu parça saf metin-disiplinidir (deterministik script içermez); protokolleri `SKILL.md` gövdesindedir.

## Referanslar

- `references/degisiklik-gunlugu.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-ictihat` ile de çağrılabilir.

## Yargı Pro bağlantısı (verimli kullanım için gerekli)

Ailenin içtihat/mevzuat doğrulaması **Yargı Pro** MCP'sine dayanır. Claude Code'da **connectors** bölümünden şu adresi ekleyip bağlanın:

```
https://yargi.betaspacestudio.com/mcp
```

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

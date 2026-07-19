# oa-musteki-vekili

*Ortak Avukat ailesi · v3.20 · bir `oa-*` parçası*

Ortak Avukat sisteminin MÜŞTEKİ/MAĞDUR VEKİLLİĞİ (iddia/şikâyet) kimlik ve orkestra parçası — oa-mudafii'nin AYNASI. Bir suç duyurusu, şikâyet, katılma (müdahillik), KYOK'a itiraz veya suçtan zarar gören temsili üstlenildiğinde DEVREYE GİR: iddia duruşunu kur (etkili soruşturma hakkı, suçtan zarar görenin hakları); suçun MADDİ ve MANEVİ unsurlarını tek tek KUR ve delile eşle (unsur inşası — savunma denetiminin aynası); manevi unsuru (kast/özel kast) objektif göstergelerden kur; ispat boşluğunu somut delille KAPAT, eksik soruşturmayı tamamlat, delili karartma/kaçış riskine karşı güvenceye al (celp/tedbir/elkoyma); şikâyet süresi ve zamanaşımını nöbette tut. "Müşteki/mağdur vekiliyiz", "suç duyurusu", "şikâyet dilekçesi", "katılma talebi", "KYOK itirazı", "kamu davası açılsın", "unsurlar oluştu", "delil getirtilsin" türü her işte — kullanıcı açıkça "müşteki vekili" demese bile bir ceza dosyasında müşteki/mağdur temsil edildiği belli olduğunda — tetikle. ortak-avukat ve oa-pipeline ile takım oynar.

## Yapı

Bu parça saf metin-disiplinidir (deterministik script içermez); protokolleri `SKILL.md` gövdesindedir.

## Referanslar

- `references/degisiklik-gunlugu.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-musteki-vekili` ile de çağrılabilir.

## Yargı Pro bağlantısı (verimli kullanım için gerekli)

Ailenin içtihat/mevzuat doğrulaması **Yargı Pro** MCP'sine dayanır. Claude Code'da **connectors** bölümünden şu adresi ekleyip bağlanın:

```
https://yargi.betaspacestudio.com/mcp
```

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

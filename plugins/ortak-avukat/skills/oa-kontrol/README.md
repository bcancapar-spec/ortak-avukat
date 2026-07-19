# oa-kontrol

*Ortak Avukat ailesi · v3.20 · bir `oa-*` parçası*

Ortak Avukat sisteminin DENETİM/KONTROL parçası. Bir dilekçe, dosya veya mütalaa teslim edilmeden önce; atıf/künye doğruluğu denetlenirken; müvekkil-aleyhi zaaflar taranırken DEVREYE GİR. Üç sabit kontrol listesini uygula: (1) atıf denetimi (her künye resmî kaynaktan teyitli mi), (2) teslim öncesi usul+esas kontrolü, (3) müvekkil-aleyhi zaaf protokolü. "Bunu kontrol et", "teslime hazır mı", "gözden geçir", "zayıf yanları neler" türü her işte — kullanıcı açıkça istemese bile esaslı bir çıktı teslim edilmeden önce — tetikle. Bağımsız çalışır; tüm oa- parçalarının çıktısını teslimden önce süzer. (İleride deterministik `oa-antitez` motoru bu listelerin üstüne kurulacaktır.)

## Yapı

Bu parça saf metin-disiplinidir (deterministik script içermez); protokolleri `SKILL.md` gövdesindedir.

## Referanslar

- `references/degisiklik-gunlugu.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-kontrol` ile de çağrılabilir.

## Yargı Pro bağlantısı (verimli kullanım için gerekli)

Ailenin içtihat/mevzuat doğrulaması **Yargı Pro** MCP'sine dayanır. Claude Code'da **connectors** bölümünden şu adresi ekleyip bağlanın:

```
https://yargi.betaspacestudio.com/mcp
```

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

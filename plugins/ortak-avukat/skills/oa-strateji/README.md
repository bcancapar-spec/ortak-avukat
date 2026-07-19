# oa-strateji

*Ortak Avukat ailesi · v3.20 · bir `oa-*` parçası*

Ortak Avukat sisteminin STRATEJİ/KARAR parçası. Bir uyuşmazlıkta yol seçimini yapılandırır: dava mı sulh mu, hangi kanun yolu, hangi sıra; maliyet-fayda analizi; başarı olasılığının dürüst (sayı uydurmayan) değerlendirmesi; alternatif yollar (ör. icrada durdurma vs yapılandırma, ihtarname-sulh vs dava). "Dava açalım mı", "sulh mu olsa", "ne yapmalı", "stratejimiz ne", "değer mi", "kazanma şansı", "maliyet-fayda", "hangi yol" → kullanıcı açıkça "strateji" demese bile bir yol kararı gerektiğinde tetikle. Mütalaaya gömülü kalan strateji muhakemesini formalize eder. `oa-vakia` (delil gücü), `oa-antitez` (zaaf/risk), `oa-sure` (zamanlama), `oa-ictihat` (içtihat eğilimi) çıktılarını bir karara bağlar.

## Yapı

Bu parça saf metin-disiplinidir (deterministik script içermez); protokolleri `SKILL.md` gövdesindedir.

## Referanslar

- `references/degisiklik-gunlugu.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-strateji` ile de çağrılabilir.

## Yargı Pro bağlantısı (verimli kullanım için gerekli)

Ailenin içtihat/mevzuat doğrulaması **Yargı Pro** MCP'sine dayanır. Claude Code'da **connectors** bölümünden şu adresi ekleyip bağlanın:

```
https://yargi.betaspacestudio.com/mcp
```

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

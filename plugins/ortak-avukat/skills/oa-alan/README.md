# oa-alan

*Ortak Avukat ailesi · v3.20 · bir `oa-*` parçası*

Ortak Avukat sisteminin ALAN/İHTİSAS DAİRESİ KONUMLANDIRMA parçası. Türk hukukunun HERHANGİ bir dalında — bir uyuşmazlığın hangi norma/maddeye bağlandığını ve Yargıtay/Danıştay/İstinaf (BAM/BİM) nezdinde hangi İHTİSAS dairesinin baktığını, HSK iş bölümü kararları ışığında konumlandırmak için DEVREYE GİR. "Hangi madde uygulanır", "hangi daire bakar", "nereden başlamalı" türü her işte tetikle. Alanı belirli dallarla SINIRLAMA; mesele çoğu zaman birden çok dalı birden ilgilendirir. Ayrıca geçmiş halüsinasyon/yanılma derslerinden çıkan YASAK BÖLGELERİ uygula (ör. Danıştay 8. Daire içtihadını hafızadan üretme; daire kaymaları). Kullanıcı alanı anmasa bile uyuşmazlık tipi belirginse tetikle. Bağımsız çalışır; `oa-ictihat` (sorgu) ve `oa-dilekce` (yazım) ile takım oynar.

## Yapı

Bu parça saf metin-disiplinidir (deterministik script içermez); protokolleri `SKILL.md` gövdesindedir.

## Referanslar

- `references/degisiklik-gunlugu.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-alan` ile de çağrılabilir.

## Yargı Pro bağlantısı (verimli kullanım için gerekli)

Ailenin içtihat/mevzuat doğrulaması **Yargı Pro** MCP'sine dayanır. Claude Code'da **connectors** bölümünden şu adresi ekleyip bağlanın:

```
https://yargi.betaspacestudio.com/mcp
```

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

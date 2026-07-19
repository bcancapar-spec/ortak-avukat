# oa-dilekce

*Ortak Avukat ailesi · v3.20 · bir `oa-*` parçası*

Ortak Avukat sisteminin DİLEKÇE/SÖZLEŞME YAZIM parçası. Türk hukukunda dava, cevap, istinaf, temyiz dilekçesi; AYM bireysel başvuru; yemin teklif dilekçesi; idari kanal başvuru dilekçesi; sözleşme tahriri (boşanma protokolü, adi ortaklık); hukuki mütalaa yazımında DEVREYE GİR. Her tip için zorunlu unsurları ve sık atlanan alanları (tebliğ tarihi, ihtirazi kayıt, harç, ihlal eksenleri) playbook olarak uygula. Kullanıcı bir dilekçe/sözleşme/mütalaa istediğinde — tip adını anmasa bile — tetikle. Bağımsız çalışır; `oa-sure` (süre satırı), `oa-ictihat` (teyitli atıf) ve `oa-kontrol` (teslim öncesi denetim) ile takım oynar.

## Yapı

Bu parça saf metin-disiplinidir (deterministik script içermez); protokolleri `SKILL.md` gövdesindedir.

## Referanslar

- `references/degisiklik-gunlugu.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-dilekce` ile de çağrılabilir.

## Yargı Pro bağlantısı (verimli kullanım için gerekli)

Ailenin içtihat/mevzuat doğrulaması **Yargı Pro** MCP'sine dayanır. Claude Code'da **connectors** bölümünden şu adresi ekleyip bağlanın:

```
https://yargi.betaspacestudio.com/mcp
```

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

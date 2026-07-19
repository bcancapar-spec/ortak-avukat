# oa-antitez

*Ortak Avukat ailesi · v3.20 · bir `oa-*` parçası*

Ortak Avukat sisteminin ANTİTEZ/KRİTİK parçası. Bir dava, dosya, dilekçe veya tezin analiz edildiği her durumda — karşı tarafın bizi kapatacak savunma ve iddialarını DURUM FARKINDALIĞI için işin ilk etabında ortaya çıkar, sonra her birini ÇÖKERT. "Karşı taraf ne der", "zayıf yanlar neler", "bu argüman nereden çatlar", risk değerlendirmesi, şeytanın avukatı, teslimden önce sağlamlık kontrolü → kullanıcı açıkça istemese bile esaslı bir tez kurulduğunda tetikle. Deterministik motor (bundled script) cephe eksiksizliğini ve çürütme bütünlüğünü garanti eder. Bağımsız çalışır; `oa-interview` (ön teori), `oa-ictihat` (çürütme dayanağı) ve `oa-kontrol` (teslim denetimi) ile takım oynar.

## Deterministik scriptler

- `scripts/antitez_matris.py`

> Scriptler modelin muhakemesini **denetler** (eksiksizlik/tutarlılık); model kurar, script sağlamasını yapar.

## Referanslar

- `references/degisiklik-gunlugu.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-antitez` ile de çağrılabilir.

## Yargı Pro bağlantısı (verimli kullanım için gerekli)

Ailenin içtihat/mevzuat doğrulaması **Yargı Pro** MCP'sine dayanır. Claude Code'da **connectors** bölümünden şu adresi ekleyip bağlanın:

```
https://yargi.betaspacestudio.com/mcp
```

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

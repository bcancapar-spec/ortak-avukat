# oa-sure

*Ortak Avukat ailesi · v3.20 · bir `oa-*` parçası*

Ortak Avukat sisteminin SÜRE parçası. Türk hukukunda her süreye bağlı işlemde — yalnızca usul (istinaf, temyiz, AYM başvuru, itiraz, cevap, dava açma; HMK/CMK/İYUK) değil, MADDİ HUKUK süreleri de (zamanaşımı/hak düşürücü: TBK, TMK, TTK, 6183 ve diğer kanun/yönetmelikler — ör. TTK m.23/c, m.749, m.814; TBK m.39, m.82; TMK m.571; 6183 m.58) dahil — "süre ne kadar / ne zaman doluyor / kaçırdım mı / zamanaşımı" türü her işte DEVREYE GİR. Süre kuralını Mevzuat MCP'den teyit et, sonra başlangıç tarihinden son günü deterministik hesaplamak için bundled scripti `--tur usul|maddi` ile kullan (maddi sürelerde adli tatil uygulanmaz). Kullanıcı açıkça "süre hesapla" demese bile, dosyada bir süre/zamanaşımı söz konusuysa tetikle. Bağımsız kullanılabilir; `ortak-avukat` kimliğiyle birlikte takım hâlinde çalışır.

## Deterministik scriptler

- `scripts/hesapla_sure.py`

> Scriptler modelin muhakemesini **denetler** (eksiksizlik/tutarlılık); model kurar, script sağlamasını yapar.

## Referanslar

- `references/degisiklik-gunlugu.md`
- `references/sure-cizelgesi.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-sure` ile de çağrılabilir.

## Yargı Pro bağlantısı (verimli kullanım için gerekli)

Ailenin içtihat/mevzuat doğrulaması **Yargı Pro** MCP'sine dayanır. Claude Code'da **connectors** bölümünden şu adresi ekleyip bağlanın:

```
https://yargi.betaspacestudio.com/mcp
```

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

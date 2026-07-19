# oa-vakia

*Ortak Avukat ailesi · v3.20 · bir `oa-*` parçası*

Ortak Avukat sisteminin VAKIA/DELİL YÖNETİM parçası. Bir dosyanın olgu ve delil tarafını disipline eder: olayların kronolojisini kurar, her iddiayı dayandığı delile eşler, ispat boşluklarını ve hiçbir iddiaya bağlanmamış (yetim) delilleri yakalar, dosyayı tasnif eder. "Olayları sıralayalım", "kronoloji çıkar", "hangi delil neyi ispatlıyor", "ispat yükü", "dosyayı düzenle/tasnif et", "elimizde ne var" → kullanıcı açıkça istemese bile bir dosya analiz edilirken veya dilekçe öncesi tetikle. Hukukta güçlü olan sistemin olgu/delil yarısını tamamlar. Deterministik motor (bundled script) kronoloji + iddia↔delil matrisini ve boşluk denetimini üretir. Bağımsız çalışır; `oa-interview` (olgu toplama), `oa-dilekce` (vakıa anlatımı/deliller), `oa-antitez` (ispat/delil cephesi) ile takım oynar.

## Deterministik scriptler

- `scripts/vakia_matris.py`

> Scriptler modelin muhakemesini **denetler** (eksiksizlik/tutarlılık); model kurar, script sağlamasını yapar.

## Referanslar

- `references/degisiklik-gunlugu.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-vakia` ile de çağrılabilir.

## Yargı Pro bağlantısı (verimli kullanım için gerekli)

Ailenin içtihat/mevzuat doğrulaması **Yargı Pro** MCP'sine dayanır. Claude Code'da **connectors** bölümünden şu adresi ekleyip bağlanın:

```
https://yargi.betaspacestudio.com/mcp
```

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

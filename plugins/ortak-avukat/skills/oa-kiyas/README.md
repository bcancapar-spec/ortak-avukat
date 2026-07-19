# oa-kiyas

*Ortak Avukat ailesi · v3.20 · bir `oa-*` parçası*

Ortak Avukat sisteminin AÇIK KIYAS / HUKUKİ SİLOJİZM parçası. Türk hukukunda her hukuki sonucu örtük sezgiyle değil, denetlenebilir üçlü yapıyla üret: BÜYÜK ÖNERME (uygulanacak norm + onu somutlaştıran içtihat) → KÜÇÜK ÖNERME (somut maddi vakıa / illiyet grafı) → SONUÇ (tatbik + olasılık). Bu, Türk hukukundaki subsumtion/tatbik mantığının ta kendisidir. Norm unsurları ile vakıa arasında eşleşme denetimi yap; eşleşmeyen unsuru ispat/hukuk boşluğu olarak işaretle. "Bu olaya hangi madde nasıl uygulanır", "hukuki dayanak nedir", "neden bu sonuç", "tatbik et", "unsurlar oluşmuş mu", "subsumtion" türü her işte — kullanıcı açıkça istemese bile bir argüman ya da dilekçe gerekçesi kurulurken — tetikle. Bağımsız çalışır; oa-illiyet (küçük önerme), oa-ictihat (teyitli büyük önerme), oa-antitez (kıyas zaafı) ve oa-dilekce (gerekçe) ile takım oynar.

## Deterministik scriptler

- `scripts/kiyas_denetim.py`

> Scriptler modelin muhakemesini **denetler** (eksiksizlik/tutarlılık); model kurar, script sağlamasını yapar.

## Referanslar

- `references/degisiklik-gunlugu.md`
- `references/kiyas-rehberi.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-kiyas` ile de çağrılabilir.

## Yargı Pro bağlantısı (verimli kullanım için gerekli)

Ailenin içtihat/mevzuat doğrulaması **Yargı Pro** MCP'sine dayanır. Claude Code'da **connectors** bölümünden şu adresi ekleyip bağlanın:

```
https://yargi.betaspacestudio.com/mcp
```

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

# oa-usul

*Ortak Avukat ailesi · v3.20 · bir `oa-*` parçası*

Ortak Avukat sisteminin USUL HUKUKU parçası ve "usul esasa üstündür" düsturunun uygulayıcısı; pipeline'ın her aşamasında çalışan kesişen katman. Türk usul mevzuatının TAMAMINDA (HMK/İYUK/İİK/CMK/6216/7201/492 ve tüm özel usul hükümleri — sınırlı sayım değil) dava şartı, ilk itiraz, görev/yetki, tebligat, harç, taraf/temsil ehliyeti, ıslah, eski hâle getirme ve kanun yolu şartlarını denetlemek için DEVREYE GİR. Üç cephelidir: karşı tarafın usul eksiğini tespit edip kurtuluş kapılarını kapatır; müvekkilin hatasında çıkış kapılarını üç kanaldan (içtihat/doktrin/web) araştırır; kamu gücünün (idare/yargı/icra) usul hatalarını ayrı denetler. "Dava şartı", "ilk itiraz", "tebligat usulsüz", "görevsiz/yetkisiz", "harç eksik", "ıslah", "eski hâle getirme", "usulden ret" türü her işte — ve herhangi bir dava/dosya/ihtilaf analiz edilirken, kullanıcı açıkça istemese bile — tetikle. oa-sure (süre ikizi), oa-illiyet (eşgüdüm), oa-ictihat, oa-antitez, oa-dilekce ve oa-kontrol ile takım oynar.

## Deterministik scriptler

- `scripts/usul_matris.py`

> Scriptler modelin muhakemesini **denetler** (eksiksizlik/tutarlılık); model kurar, script sağlamasını yapar.

## Referanslar

- `references/degisiklik-gunlugu.md`
- `references/usul-cetveli.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-usul` ile de çağrılabilir.

## Yargı Pro bağlantısı (verimli kullanım için gerekli)

Ailenin içtihat/mevzuat doğrulaması **Yargı Pro** MCP'sine dayanır. Claude Code'da **connectors** bölümünden şu adresi ekleyip bağlanın:

```
https://yargi.betaspacestudio.com/mcp
```

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

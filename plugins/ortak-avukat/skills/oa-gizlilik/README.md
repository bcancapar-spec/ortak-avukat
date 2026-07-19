# oa-gizlilik

*Ortak Avukat ailesi · v3.20 · bir `oa-*` parçası*

Ortak Avukat sisteminin GİZLİLİK / MESLEK SIRRI / UYAP KORUMA parçası ve Privacy Layer 0 garantörü. Bir içerik dış araca (web, bulut MCP, e-posta, üçüncü parti bağlayıcı) gönderilmeden ÖNCE; müvekkil verisi, TC kimlik, dosya/esas no, sağlık veya ceza verisi, hesap/kart bilgisi gibi hassas unsurları ve UYAP login / e-imza / PIN desenlerini tara. Avukatlık Kanunu m.36 (sır saklama), TCK m.239 (ticari sır), KVKK m.6 (özel nitelikli veri) temelinde çalışır. "Bu güvenli mi", "dışarı gitsin mi", "gizli veri var mı", "UYAP", "e-imza", "paylaşmadan önce kontrol et", "KVKK" türü her işte — ve bir çıktı/araç çağrısı hassas veri taşıyor olabileceğinde, kullanıcı açıkça istemese bile — tetikle. UYAP login ve e-imza/PIN adımları yalnızca avukata aittir; bu parça onlar için ASLA kod yazmaz, yalnızca engeller. Bağımsız çalışır; tüm oa- parçalarının dış-araç çağrısını süzer.

## Deterministik scriptler

- `scripts/gizlilik_tara.py`

> Scriptler modelin muhakemesini **denetler** (eksiksizlik/tutarlılık); model kurar, script sağlamasını yapar.

## Referanslar

- `references/degisiklik-gunlugu.md`
- `references/gizlilik-desenleri.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-gizlilik` ile de çağrılabilir.

## Yargı Pro bağlantısı (verimli kullanım için gerekli)

Ailenin içtihat/mevzuat doğrulaması **Yargı Pro** MCP'sine dayanır. Claude Code'da **connectors** bölümünden şu adresi ekleyip bağlanın:

```
https://yargi.betaspacestudio.com/mcp
```

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

# oa-gizlilik

*Ortak Avukat ailesi · v3.26 · bir `oa-*` parçası*

Ortak Avukat sisteminin GİZLİLİK / MESLEK SIRRI / UYAP KORUMA parçası ve Privacy Layer 0 garantörü. Bir içerik dış araca (web, bulut MCP, e-posta, üçüncü parti bağlayıcı) gönderilmeden ÖNCE; müvekkil verisi, TC kimlik, dosya/esas no, sağlık veya ceza verisi, hesap/kart bilgisi gibi hassas unsurları ve UYAP login / e-imza / PIN desenlerini tara. Avukatlık Kanunu m.36 (sır saklama), TCK m.239 (ticari sır), KVKK m.6 (özel nitelikli veri) temelinde çalışır. "Bu güvenli mi", "dışarı gitsin mi", "gizli veri var mı", "UYAP", "e-imza", "paylaşmadan önce kontrol et", "KVKK" türü her işte — ve bir çıktı/araç çağrısı hassas veri taşıyor olabileceğinde, kullanıcı açıkça istemese bile — tetikle. UYAP login ve e-imza/PIN adımları yalnızca avukata aittir; bu parça onlar için ASLA kod yazmaz, yalnızca engeller. Bağımsız çalışır; tüm oa- parçalarının dış-araç çağrısını süzer.

## Deterministik scriptler

- `scripts/gizlilik_tara.py`

> Scriptler modelin muhakemesini **denetler** (eksiksizlik/tutarlılık); model kurar, script sağlamasını yapar.

## Referanslar

- `references/degisiklik-gunlugu.md`
- `references/gizlilik-desenleri.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-gizlilik` ile de çağrılabilir.

## Teyit kanalı (resmî kaynak beyaz listesi)

Ailenin içtihat/mevzuat doğrulaması **resmî portallardan** yapılır; model bu portallara Claude Code'un web araçlarıyla (**WebFetch** tam metin / **WebSearch** keşif) ulaşır. Kurulacak ya da bağlanacak bir sunucu yoktur — eklenti üçüncü taraf MCP sunucusu ilan etmez (2026-10-15 avukat kararı). Teyidin kanıtı resmî portalın adresi ve diske inmiş tam metindir; beyaz liste: [resmî kaynaklar](../ortak-avukat/references/resmi-kaynaklar.md).

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

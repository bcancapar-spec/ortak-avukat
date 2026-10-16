# oa-dilekce

*Ortak Avukat ailesi · v3.26 · bir `oa-*` parçası*

Ortak Avukat sisteminin DİLEKÇE/SÖZLEŞME YAZIM parçası. Türk hukukunda dava, cevap, istinaf, temyiz dilekçesi; AYM bireysel başvuru; yemin teklif dilekçesi; idari kanal başvuru dilekçesi; sözleşme tahriri (boşanma protokolü, adi ortaklık); hukuki mütalaa yazımında DEVREYE GİR. Her tip için zorunlu unsurları ve sık atlanan alanları (tebliğ tarihi, ihtirazi kayıt, harç, ihlal eksenleri) playbook olarak uygula. Kullanıcı bir dilekçe/sözleşme/mütalaa istediğinde — tip adını anmasa bile — tetikle. Bağımsız çalışır; `oa-sure` (süre satırı), `oa-ictihat` (teyitli atıf) ve `oa-kontrol` (teslim öncesi denetim) ile takım oynar.

## Deterministik scriptler

- `scripts/dilekce_denetim.py` (tip başına zorunlu unsur + tertip-düzen + müvekkil-aleyhi ifade taraması)
- `scripts/udf_yaz.py`
- `scripts/md_udf_html.py`
- `scripts/udf_html2pdf.py`

> Scriptler modelin muhakemesini **denetler** (eksiksizlik/tutarlılık); model kurar, script sağlamasını yapar. Protokoller `SKILL.md` gövdesindedir.

## Referanslar

- `references/degisiklik-gunlugu.md`
- `references/kanun-yolu-mimari-playbook.md`
- `references/ticaret-sicili-desenleri.md`
- `references/udf-hatti-kesinti-plani.md`
- `references/udf-ic-yapi.md`
- `references/uyap-belge-formatlari.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-dilekce` ile de çağrılabilir.

## Teyit kanalı (resmî kaynak beyaz listesi)

Ailenin içtihat/mevzuat doğrulaması **resmî portallardan** yapılır; model bu portallara Claude Code'un web araçlarıyla (**WebFetch** tam metin / **WebSearch** keşif) ulaşır. Kurulacak ya da bağlanacak bir sunucu yoktur — eklenti üçüncü taraf MCP sunucusu ilan etmez (2026-10-15 avukat kararı). Teyidin kanıtı resmî portalın adresi ve diske inmiş tam metindir; beyaz liste: [resmî kaynaklar](../ortak-avukat/references/resmi-kaynaklar.md).

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

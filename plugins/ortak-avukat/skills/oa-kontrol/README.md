# oa-kontrol

*Ortak Avukat ailesi · v3.26 · bir `oa-*` parçası*

Ortak Avukat sisteminin DENETİM/KONTROL parçası. Bir dilekçe, dosya veya mütalaa teslim edilmeden önce; atıf/künye doğruluğu denetlenirken; müvekkil-aleyhi zaaflar taranırken DEVREYE GİR. Üç sabit kontrol listesini uygula: (1) atıf denetimi (her künye resmî kaynaktan teyitli mi), (2) teslim öncesi usul+esas kontrolü, (3) müvekkil-aleyhi zaaf protokolü. "Bunu kontrol et", "teslime hazır mı", "gözden geçir", "zayıf yanları neler" türü her işte — kullanıcı açıkça istemese bile esaslı bir çıktı teslim edilmeden önce — tetikle. Bağımsız çalışır; tüm oa- parçalarının çıktısını teslimden önce süzer. Deterministik `oa-antitez` motoru bu listelerin üstünde çalışır.

## Deterministik scriptler

- `scripts/ictihat_muhakeme_denetim.py` (içtihat muhakeme zinciri kapısı G1-G11)
- `scripts/kaynakca_uret.py`
- `scripts/kaynak_blogu.py`
- `scripts/kunye_ortak.py`
- `scripts/kunye_teyit.py`
- `scripts/muhur_yaz.py`
- `scripts/tazelik_denetim.py`
- `scripts/teslim_paketi.py` (teslim zinciri + makbuz)

> Scriptler modelin muhakemesini **denetler** (eksiksizlik/tutarlılık); model kurar, script sağlamasını yapar. Protokoller `SKILL.md` gövdesindedir.

## Referanslar

- `references/degisiklik-gunlugu.md`
- `references/cikti-semasi.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-kontrol` ile de çağrılabilir.

## Teyit kanalı (resmî kaynak beyaz listesi)

Ailenin içtihat/mevzuat doğrulaması **resmî portallardan** yapılır; model bu portallara Claude Code'un web araçlarıyla (**WebFetch** tam metin / **WebSearch** keşif) ulaşır. Kurulacak ya da bağlanacak bir sunucu yoktur — eklenti üçüncü taraf MCP sunucusu ilan etmez (2026-10-15 avukat kararı). Teyidin kanıtı resmî portalın adresi ve diske inmiş tam metindir; beyaz liste: [resmî kaynaklar](../ortak-avukat/references/resmi-kaynaklar.md).

Kurulum ayrıntısı ve ailenin tamamı için: [plugin README](../../README.md).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

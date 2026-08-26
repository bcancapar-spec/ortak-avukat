# TEST-KULLANIM — bu fork'u ana ortak-avukat'tan AYRI nasıl kullanırsınız

> **GÜNCEL DURUM (2026-08-26):** prova dönemi kapandı — ana depo
> (`bcancapar-spec/ortak-avukat`) v0.5.11'dedir ve KANONİKTİR; fork artık
> yalnız AYNA olarak eşit tutulur. Aşağıdaki anahtarlamalı-kullanım tarifi,
> ileride yeniden bir aday-paket prova dönemi açılırsa geçerli olacak
> TARİHÎ prosedürdür.

## Altın kural: İKİ AİLE AYNI ANDA KURULU OLMAZ

Fork'taki eklentinin adı bilinçli olarak aynıdır (`ortak-avukat`) — skill
tetik metinleri ve `oa-*` aile adları değişmesin diye. Bedeli: ana eklentiyle
YAN YANA kurulursa iki aile aynı prompta birden tetiklenir (KURULUM-SENKRON
"mükerrer aile" dersi). Bu yüzden kullanım ANAHTARLAMALIDIR: ya ana, ya test.

## Teste geçiş (3 komut + restart)

```
claude plugin marketplace add bcancapar-spec/test-ortak-avukat
claude plugin uninstall ortak-avukat@ortak-avukat
claude plugin install ortak-avukat@ortak-avukat
```

> DİKKAT (2026-08-13 saha dersi): marketplace ADI fork'ta da `ortak-avukat`tır
> (marketplace.json'dan gelir, repo adından DEĞİL) — `add` komutu yeni kayıt
> açmaz, MEVCUT `ortak-avukat` marketplace'inin kaynağını fork'a çevirir.
> Install bu yüzden `@ortak-avukat` ile yazılır. Hangi repoya baktığınızın
> kanıtı: `git -C ~/.claude/plugins/marketplaces/ortak-avukat remote -v`

Sonra Claude Code'u **TAM kapat-aç** (hook'lar yalnız süreç başında yüklenir —
754 koşusunun kanıtladığı ders; "Restart to apply" yetmez, süreç ölmeli).

## Ana sürüme dönüş

```
claude plugin uninstall ortak-avukat@ortak-avukat
claude plugin marketplace add bcancapar-spec/ortak-avukat
claude plugin install ortak-avukat@ortak-avukat
```
(`marketplace add` mevcut kaydın kaynağını ana depoya GERİ çevirir.)
+ yine TAM kapat-aç.

## "Şu an hangisi kurulu?" — mekanik teyit

```
ls ~/.claude/plugins/cache
```
Test sürümünün kanıtı: `cache/ortak-avukat/ortak-avukat/0.5.8/` klasörü
(sürüm damgası 0.5.8 = fork-prova; ana en çok 0.5.7.5'tir). İkinci kanıt:
test sürümünde şu dosya vardır, ana sürümde YOKTUR:
`.../skills/oa-kontrol/scripts/muhur_yaz.py`

## Test koşusunda neye bakılır (v0.5.8 karne kalemleri)

1. **[G5]** — teyit sırasında model "bu karar aşılmış olabilir mi?" soruyor mu;
   AŞAN-KAYNAK işlenmiş LEHE karar dilekçeye girmeye çalışınca BLOK yiyor mu.
2. **KAYNAK-BLOĞU** — `_oa/cikti` ürünleri ilk 3 satırında `kaynaklar@sha8`
   taşıyor mu; ingest büyüyünce `tazelik_denetim.py --kok .` BAYAT ilan ediyor mu.
3. **Mühür** — kapanışta ürün başına `.prov.json` doğuyor mu;
   `muhur_yaz.py --dogrula <urun.udf>` UYAP öncesi ✓ veriyor mu.
4. **Nöbetçi** — `aile_dogrula` yeşil mi (ağ-import sıfır taban ölçüldü).
5. **Özne eşleştirici** — OCR varyantlı adlarda BAGLA/AVUKATA-SOR damgaları
   isabetli mi (yanlış-BAGLA = karneye eksi).
6. **--zincir** — graf üretiminden sonra en-zayıf-halka çıktısı antitez
   bölümünü besliyor mu.

Prova GEÇERSE: paket ana depoya v0.5.8 olarak taşınır (4 damga birlikte) —
o taşıma ayrı bir Can onayıdır.

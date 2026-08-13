# TEST-KULLANIM — bu fork'u ana ortak-avukat'tan AYRI nasıl kullanırsınız

> Bu depo v0.5.8 aday paketinin (semantica+graft desen devşirmesi) PROVA
> sahasıdır. Ana depo (`bcancapar-spec/ortak-avukat`, v0.5.7.5) DONUKTUR.

## Altın kural: İKİ AİLE AYNI ANDA KURULU OLMAZ

Fork'taki eklentinin adı bilinçli olarak aynıdır (`ortak-avukat`) — skill
tetik metinleri ve `oa-*` aile adları değişmesin diye. Bedeli: ana eklentiyle
YAN YANA kurulursa iki aile aynı prompta birden tetiklenir (KURULUM-SENKRON
"mükerrer aile" dersi). Bu yüzden kullanım ANAHTARLAMALIDIR: ya ana, ya test.

## Teste geçiş (3 komut + restart)

```
claude plugin marketplace add bcancapar-spec/test-ortak-avukat
claude plugin uninstall ortak-avukat@ortak-avukat
claude plugin install ortak-avukat@test-ortak-avukat
```

Sonra Claude Code'u **TAM kapat-aç** (hook'lar yalnız süreç başında yüklenir —
754 koşusunun kanıtladığı ders; "Restart to apply" yetmez, süreç ölmeli).

## Ana sürüme dönüş

```
claude plugin uninstall ortak-avukat@test-ortak-avukat
claude plugin install ortak-avukat@ortak-avukat
```
+ yine TAM kapat-aç.

## "Şu an hangisi kurulu?" — mekanik teyit

```
ls ~/.claude/plugins/cache
```
`test-ortak-avukat/` klasörü görünüyorsa test sürümündesiniz. İkinci kanıt:
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

# Unsur Şablonları — asgari set (M4, Paket D — v0.5.5)

Bu klasör, sık görülen dava türleri için **unsur | norm | delil-türü | yük**
dört-sütunlu tablolar tutar. Amaç: `oa-vakia`'nın iddia↔delil matrisini
(`vakia_matris.py`) **kör noktasız** kurmak — dava türü tespit edildikten
(`oa-alan`) sonra ilgili şablon açılır, her **unsur** bir `iddialar[].id`
(`U1`, `U2`, …) olarak vakıa matrisine taşınır; unsuru destekleyen somut
delil(ler) `olaylar[].destekler`e bağlanır. Bir unsur delilsiz kalırsa
`vakia_matris.py --dogrula ... --json <yol>` bunu `ispat_bosluklari`na yazar
ve `pipeline_kayit.py`nin ürettiği `_oa/DURUM.md`de **🔴 kırmızı** olarak
görünür (bkz. `oa-pipeline/scripts/pipeline_kayit.py::_vakia_delilsiz_unsur_uyarisi`).

## Kullanım

1. `oa-alan` dava türünü konumlar (bu şablonlardan biriyle örtüşüyorsa işaret eder).
2. İlgili şablonun unsur listesi `vakia_matris.py --iskelet` çıktısındaki
   `iddialar` dizisine **U1, U2, …** id'leriyle işlenir (unsur metni = iddia metni).
3. Her unsur için somut delil `olaylar[]`e eklenir, `destekler: ["U_"]` ile bağlanır.
4. `--dogrula` ile denetlenir; delilsiz unsur `ispat_bosluklari`na düşer → DURUM.md kırmızı.
5. Buradaki **norm** atıfları başlangıç ÇIPASIDIR — kullanım anında güncel
   metin/yürürlük/değişiklik `oa-alan`/`oa-ictihat` üzerinden Mevzuat MCP'den
   **teyit edilir** (hafızadan madde numarası/parasal sınır beyan edilmez —
   anayasa m.4, oa-alan "Yasak bölgeler").

## Asgari set (bu sürümde)
- `tasarrufun-iptali.md` — İİK m.277 vd. alacaklının tasarrufun iptali davası
- `ise-iade.md` — 4857 sayılı İş Kanunu m.18-21 işe iade davası
- `itirazin-iptali.md` — İİK m.67-68 itirazın iptali davası
- `kidem-ihbar.md` — kıdem tazminatı (1475 sayılı Kanun m.14) + ihbar tazminatı (İş K. m.17)
- `amme-odeme-emri.md` — **amme (kamu) alacağı** ödeme emrine karşı dava
  (6183 m.55, m.58; usul rejimi 2577 İYUK). **Karıştırma:** `itirazin-iptali.md`
  şablonundaki "ödeme emri" İİK m.58-60 anlamındadır — özel hukuk takibi;
  bu şablon idari yargıdaki amme alacağı davasıdır.

Yeni bir dava türü şablonu eklenirken bu dört sütun (**unsur | norm | delil-türü | yük**)
korunur; norm hücresi kullanım anında MCP-teyitli hâle getirilecek bir **başlangıç
noktası** olarak işaretlenir, kesin hüküm gibi sunulmaz.

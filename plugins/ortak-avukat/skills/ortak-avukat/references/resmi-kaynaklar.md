# Resmî kaynak beyaz listesi — teyit kanalı (2026-10-15, avukat kararı)

> Anayasa m.5: içtihat ve mevzuat, resmî kaynaktan doğrulanmadıkça yoktur.
> Bu belge "resmî kaynak"ın ne olduğunu sayar. Tek kaynak koddadır
> (`oa-kontrol/scripts/kunye_ortak.py` → `RESMI_KAYNAKLAR`, `resmi_kaynak_mi`);
> bu nüsha onunla testle özdeş tutulur (`tests/test_teyit_kanali.py`).

## Kural

Bir künyenin ya da maddenin teyidi iki şeyle kanıtlanır: **resmî portalın adresi**
ve **diske inmiş tam metin** (`_oa/teyit/dokum/`). Adres bu listedeki bir alan
adından ya da herhangi bir `.gov.tr` alan adından değilse teyit yoktur; künye
"teyit YAPILAMADI" damgasıyla kalır ve dış çıktıya "teyitli" giremez. Üçüncü
taraf sunucular, özel içtihat siteleri ve arama motoru özetleri teyit kaynağı
değildir; eklenti hiçbir MCP sunucusu ilan etmez.

Kanal **hibrittir**: model resmî portallara Claude Code'un kendi web araçlarıyla
(`WebFetch` tam metin, `WebSearch` keşif) ulaşır; sorgu çıkmadan önce Layer 0
süzgeci (`oa-gizlilik`) çalışır — müvekkil tanımlayıcı veri sorguya girmez.
Yerel, açık kodlu bir `oa-kaynak` MCP sunucusu (bu portalları saran keşif katmanı)
yol haritasındadır; kurulana kadar keşif, resmî alan adlarıyla sınırlı web aramasıdır.

## Liste

| Kaynak | Alan adı | Tür | Ne verir |
|---|---|---|---|
| Mevzuat Bilgi Sistemi | `mevzuat.gov.tr` | mevzuat | Kanun, CBK, tüzük, yönetmelik, tebliğ — yürürlükteki metin ve değişiklik geçmişi |
| Resmî Gazete | `resmigazete.gov.tr` | resmî gazete | Yayım günü ve metni; yürürlük tarihi teyidi |
| Bedesten — Adalet Bakanlığı içtihat portalı | `mevzuat.adalet.gov.tr` | içtihat | Yargıtay, BAM, Danıştay, BİM ve yerel mahkeme kararları (karar sayfası: `/ictihat/<kimlik>`) |
| Yargıtay Karar Arama | `karararama.yargitay.gov.tr` | içtihat | Yargıtay daire ve kurul kararları, tam metin |
| Yargıtay (kurul kararları, İBK) | `yargitay.gov.tr` | içtihat | İçtihadı Birleştirme ve Genel Kurul kararları |
| UYAP Emsal Karar | `emsal.uyap.gov.tr` | içtihat | İlk derece ve BAM/BİM emsal kararları |
| Danıştay Karar Arama | `karararama.danistay.gov.tr` | içtihat | Danıştay daire ve kurul kararları |
| Danıştay | `danistay.gov.tr` | içtihat | Kurul kararları, duyurular |
| AYM Kararlar Bilgi Bankası (bireysel başvuru) | `kararlarbilgibankasi.anayasa.gov.tr` | içtihat | Bireysel başvuru kararları (`B. No`) |
| AYM Norm Denetimi Kararlar Bilgi Bankası | `normkararlarbilgibankasi.anayasa.gov.tr` | içtihat | İptal ve itiraz kararları (`E./K.`) |
| Anayasa Mahkemesi | `anayasa.gov.tr` | içtihat | Resmî duyurular, İçtüzük |
| Uyuşmazlık Mahkemesi | `uyusmazlik.gov.tr` | içtihat | Görev ve hüküm uyuşmazlığı kararları |
| AİHM HUDOC | `hudoc.echr.coe.int` | AİHM | Strazburg kararları ve kabul edilebilirlik kararları |
| Türkiye Barolar Birliği (AAÜT) | `barobirlik.org.tr` | tarife | Avukatlık Asgari Ücret Tarifesi, meslek kuralları |
| Rekabet Kurumu | `rekabet.gov.tr` | kurum | Kurul kararları |
| KVKK | `kvkk.gov.tr` | kurum | Kurul karar özetleri, rehberler |
| Kamu İhale Kurumu | `kik.gov.tr` | kurum | Uyuşmazlık kararları |
| Sayıştay | `sayistay.gov.tr` | kurum | Daire ve Genel Kurul kararları |
| Gelir İdaresi Başkanlığı (özelge) | `gib.gov.tr` | kurum | Özelgeler, sirkülerler |
| SPK | `spk.gov.tr` | kurum | Kurul kararları, bültenler |
| BDDK | `bddk.org.tr` | kurum | Kurul kararları, düzenlemeler |

Genel kural: alan adı `.gov.tr` ile bitiyorsa (yukarıda sayılmasa da) resmîdir.
`www.` gibi alt alanlar kabul edilir; `mevzuat.gov.tr.sahte.net` gibi sondan
eklemeler reddedilir.

## Kütüğe nasıl girer

```
python oa_hafiza.py teyit --kok . --arac ictihat_getir --sorgu "<anonim sorgu>" --sonuc "<künye>" --kaynak-url https://mevzuat.adalet.gov.tr/ictihat/<kimlik> --dokum-icerik @ham.md --dokum-sinifi tam-metin --damga LEHE --ilgili-kisim "<verbatim alıntı>" --bag "<davaya bağ, en az kırk karakter>"
```

- Tam metin çeken araçlarda (`ictihat_getir`, `kurum_karari_getir`, `WebFetch`,
  `mevzuat_getir`, `resmi_gazete_getir`) `--kaynak-url` zorunludur ve listeden olmalıdır.
- Arama araçlarında (`ictihat_ara`, `WebSearch` …) adres isteğe bağlıdır; verilirse
  listeden olmalıdır.
- `ictihat_muhakeme_denetim.py` [G7]: dilekçeye dayanak olan muhakeme kaydının adresi
  yoksa ya da liste dışıysa teslim engelidir.

## Listeyi değiştirmek

Yeni bir resmî kaynak gerekiyorsa önce `kunye_ortak.RESMI_KAYNAKLAR` tuple'ına, sonra
bu tabloya eklenir; test ikisini karşılaştırır. Ekleme kararı avukatındır (anayasa m.9).

# İçtihat Muhakeme Şablonu — NN-ictihat-muhakeme.md alan şeması

Bu şema, **MODUL 2 — İçtihat Muhakeme Zinciri**'nin ortak veri modelidir. Her
tetkik edilen karar (`oa-ictihat`'ın çektiği her içtihat) için **bir** kayıt
üretilir; kayıt kararın "muhakeme edilmiş" sayılabilmesinin TEK kanıtıdır.
Çıplak künye (yalnız daire+esas+karar, muhakeme kaydı olmadan) hiçbir zaman
dilekçeye giremez — bkz. `oa-dilekce` "Çıplak künye yasağı".

## Akıştaki yeri

```
oa-ictihat  → CEK   → karar_getir/ictihat_getir ile ham md, _oa/teyit/dokum/'a yazılır
oa-kiyas /
oa-kontrol  → MUHAKEME → illiyet + DAMGA (LEHE/ALEYHE/ALEYHE-AYIRT/NOTR) + ilgili kısım
                          → NN-ictihat-muhakeme.md, _oa/cikti/'ya yazılır
oa-dilekce  → KULLAN → yalnız DAMGA=LEHE veya DAMGA=ALEYHE-AYIRT olan kayıtlar
                        dilekçeye girer; ALEYHE (ayırt edilmemiş) ve NOTR asla girmez
```

CEK ve MUHAKEME ayrı adımlardır: bir kararın **çekilmiş olması** onun
**muhakeme edilmiş** sayılması için yeterli değildir. Muhakeme edilmemiş
(damgasız/eksik alanlı) kayıt fail-closed kuralı gereği **NOTR** sayılır ve
kullanılamaz (aşağıya bkz.).

## Dosya adı ve konum

`_oa/cikti/NN-ictihat-muhakeme.md` — `NN` dosyanın işlendiği sırayı gösteren
iki haneli sıra no'dur (`01`, `02`, ...). Bir dosyada **bir** karar
muhakeme edilir; birden çok karar birden çok dosyaya ayrılır (kimlik
karışıklığını önler, `oa-pipeline/scripts/capraz_denetim.py` benzeri ileri
çapraz denetime uygun tekil kimlik alanı sağlar).

## Alanlar

| Alan | Zorunlu mu | Kaynağı | Açıklama |
|---|---|---|---|
| **KUNYE** | Her zaman | `oa-ictihat` (Yargı/Bedesten/AYM/Mevzuat MCP, teyitli) | Merci + daire + esas no + karar no + tarih. Yalnız MCP'den fiilen teyitli künye — hafızadan **yazılmaz**. `oa-kontrol/kunye_teyit.py`'nin denetlediği atıf budur. |
| **KAYNAK-IZI** | Her zaman | `oa-ictihat`'ın CEK adımı | Kararın tam metninin ham hâlinin diske yazıldığı dosya adı: `_oa/teyit/dokum/<dosya>.md`. Bu, `kunye_teyit.py`'nin ikinci teyit kaynağıdır (kütük + döküm). İz yoksa (dosya gerçekten diskte yoksa) kayıt eksik sayılır. |
| **İLGİLİ-KISIM** | Her zaman | KAYNAK-IZI dosyasından **aynen** | Kararın **somut davayla ilgili** gerekçe pasajı — tüm karar değil, ilgili kısım. Birebir alıntı; hafızadan yeniden kurulmaz. OCR şüphesi varsa açıkça işaretlenir (kanonik kaynakla teyit edilene kadar). |
| **DAMGA** | Her zaman | Model muhakemesi (`oa-kiyas`/`oa-kontrol`) | **Kapalı enum — yalnız dört değer:** `LEHE` \| `ALEYHE` \| `ALEYHE-AYIRT` \| `NOTR`. Aşağıdaki "DAMGA enumu" bölümüne bkz. |
| **DAVAYA-BAĞ** | Her zaman | Model muhakemesi | Bu karar **neden** somut olaya uygulanır — kararın hükmü ile davanın vakıası arasındaki bağ (norm-unsuru/vakıa eşleşmesi; `oa-kiyas` büyük önermesiyle ilişkilendirilir). **Alan adı bilinçli seçildi (R4):** bu bir **analoji/emsal-uygunluk** bağıdır, `oa-illiyet`'in modellediği fiil→netice **nedensellik** zinciriyle KARIŞTIRILMASIN diye eskiden "İLLİYET" olan bu alan **DAVAYA-BAĞ** olarak adlandırılmıştır (terim değişikliği; muhakeme içeriği aynıdır). Boş/yüzeysel DAVAYA-BAĞ = kayıt eksik sayılır. |
| **AYIRT-ETME** | **Yalnız** `DAMGA: ALEYHE-AYIRT` olduğunda ZORUNLU; diğer üç damgada bu alan yazılmaz/boş kalır | Model muhakemesi | Kararın somut olaya **neden uymadığı** — ayırt etme (distinguishing) gerekçesi. Bu alan olmadan `ALEYHE-AYIRT` damgası geçersizdir (fail-closed: alan boşsa kayıt `ALEYHE` gibi işlem görür, dilekçeye giremez). |

## DAMGA enumu — kapalı, dört değer

- **LEHE** — Karar müvekkil pozisyonunu destekler; dilekçede tam künye +
  ilgili kısım aynen alıntı + bağlamsal açıklama ile kullanılabilir
  (`oa-dilekce` "İçtihat kullanımı" adımı).
- **ALEYHE** — Karar müvekkil aleyhinedir ve **ayırt edilmemiştir**. Dış
  çıktıya (dilekçe) **asla girmez**; yalnız iç analizde (muhakeme kaydı +
  `oa-antitez` cephaneliği) dahili tutulur — bkz. aşağıdaki "Kritik doktrin".
- **ALEYHE-AYIRT** — Karar müvekkil aleyhine görünür AMA somut olayla
  **ayırt edilmiştir** (distinguishing): AYIRT-ETME alanı bu farkı somut
  gerekçeyle anlatır. Ayırt edilmiş aleyhe karar dilekçede **karşılamak**
  amacıyla kullanılabilir — bu, meşru bir savunma tekniğidir, adil
  yargılanma hakkının (m.6) ihlali anlamına **gelmez**; karşı tarafın
  ileri sürmesi beklenen/sürdüğü bağlayıcı otoriteyi görmezden gelmek
  yerine açıkça karşılamaktır.
- **NOTR** — **Varsayılan.** Karar henüz muhakeme edilmemiştir (damga
  atanmamış, DAMGA alanı boş, veya kayıt hiç üretilmemiş). Fail-closed:
  NOTR/damgasız kayıt **hiçbir şart altında** dilekçeye giremez ve
  "muhakeme edilmiş" sayılmaz.

## Kritik doktrin — dış/iç ayrımı ve fail-closed (bağlayıcı, sapma yok)

1. **Dış çıktı (dilekçe) daima müvekkil LEHİNEdir.** Dilekçeye yalnız
   `LEHE` veya `ALEYHE-AYIRT` damgalı, muhakeme kaydı tamam olan kararlar
   girer. `oa-dilekce`'nin "Çıplak künye yasağı" kuralı budur.
2. **ALEYHE (ayırt edilmemiş) içtihat dilekçeye GİRMEZ** — ama iç analizde
   (muhakeme kaydı + `oa-antitez` çökertme matrisi) işlenmesi **ZORUNLUdur**.
   Aleyhe kararı görmezden gelip yalnız lehe kararları yazmak, dürüstlük
   sınırının (HMK dürüstlük + `oa-kontrol` A listesi) ihlalidir — aleyhe
   karar **saklanmaz**, dahili cephanelikte tutulur ve gerekirse strateji
   ona göre kurulur.
3. **Varsayılan-NOTR / damgasız = "muhakeme edilmemiş" (fail-closed).**
   Hiçbir script veya model "damga yoksa nötr/geçerli say" varsayımına
   girmez; damgasız kayıt kullanılamaz durumdadır, kullanılabilir hâle
   gelmesi için açıkça muhakeme edilmesi (DAMGA atanması) gerekir.
   **(YENİ-1, backlog)** NOTR'un mekanik karşılığı `ictihat_muhakeme_denetim.py`
   düzeyinde yalnız bir **UYARIDIR** (bloklamaz — bkz. yukarıdaki "Denetim"
   bölümü); giriş yasağının (NOTR'un dilekçeye girmemesi gerektiği hükmünün)
   nihai uygulayıcısı script değil, **model + avukat gözüdür** — mekanik kapı
   burada da sahte kesinlik üretmez, yalnız işaret verir.
4. **Yargıtay/BAM atfı OLMAYAN esaslı dilekçe muhakemesi ZAYIF sayılır.**
   Esaslı bir hukuki sonuç (özellikle içtihadın yerleşik olduğu konularda)
   hiç Yargıtay/BAM içtihadına dayanmıyorsa, bu açıkça "zayıf/teyitsiz
   muhakeme" olarak işaretlenir — `oa-kontrol` A listesi bunu denetler.

## Örnek kayıt (`_oa/cikti/01-ictihat-muhakeme.md`)

```markdown
# 01 — İçtihat Muhakeme Kaydı

**KUNYE:** Yargıtay 4. HD, E. 2023/1234, K. 2023/5678, T. 12.09.2023
**KAYNAK-IZI:** _oa/teyit/dokum/2026-07-19-search_bedesten_unified-tbk-m49.md
**DAMGA:** LEHE

## İLGİLİ-KISIM
> "...davalının trafik kurallarına aykırı hareketi ile davacının zararı
> arasında illiyet bağı kurulmuş olup, TBK m.49 uyarınca tazminat
> sorumluluğu doğduğu..." (KAYNAK-IZI dosyasından aynen alıntı)

## DAVAYA-BAĞ
Bu karar, dosyamızdaki trafik kazası olgusuyla (kırmızı ışıkta geçme +
yaralanma) aynı unsur setini (fiil, hukuka aykırılık, illiyet, zarar)
içeriyor; TBK m.49'un büyük önermesini somutlaştıran doğrudan emsaldir.

## AYIRT-ETME
(DAMGA=LEHE olduğundan bu alan uygulanmaz — boş bırakılır.)
```

İkinci bir örnek — aleyhe kararın ayırt edilmesi:

```markdown
# 02 — İçtihat Muhakeme Kaydı

**KUNYE:** Yargıtay 4. HD, E. 2022/900, K. 2022/4400, T. 03.05.2022
**KAYNAK-IZI:** _oa/teyit/dokum/2026-07-19-search_bedesten_unified-tbk-m49-aleyhe.md
**DAMGA:** ALEYHE-AYIRT

## İLGİLİ-KISIM
> "...somut olayda davacının kendi kusuru ağır basmakta olup, illiyet
> bağının kesildiği..." (KAYNAK-IZI dosyasından aynen alıntı)

## DAVAYA-BAĞ
Karar, illiyet bağının davacı kusuruyla kesildiği hâllere ilişkindir;
bizim dosyamızda ise davacı kusuru yoktur (delil: trafik tutanağı, tam
kusur davalıda).

## AYIRT-ETME
Emsal kararda davacının %70 kusurlu olduğu tespit edilmiştir; dosyamızda
ise trafik tutanağına göre davacının hiçbir kusuru bulunmamaktadır —
olgusal zemin farklı olduğundan emsal karar somut olaya uygulanmaz.
```

## Denetim (aktif — `oa-kontrol/scripts/ictihat_muhakeme_denetim.py`)

Kayıtların mekanik denetimi MODÜL 2'de (`oa-kontrol/scripts/
ictihat_muhakeme_denetim.py`) deterministik bir script'e bağlandı — bu,
`kiyas_denetim.py`'nin yapısal denetim felsefesiyle aynıdır: script "DAMGA
doğru mu" demez, yalnız "DAMGA alanı kapalı enumdan biri mi, AYIRT-ETME
gerekliyken dolu mu, KAYNAK-IZI dosyası `_oa/teyit/dokum` içinde fiilen var
mı ve künye orada dize olarak geçiyor mu, İLGİLİ-KISIM/DAVAYA-BAĞ dolu mu"
der. Damganın hukuken isabetli olup olmadığı (İLGİLİ-KISIM'ın GERÇEKTEN
ilgili olup olmadığı dahil) avukat muhakemesidir — script bu muhakemeye
girmez, yalnız varlık+bağ+alan bütünlüğünü denetler. Çıplak/eksik/ALEYHE
(ayırt edilmemiş) atıf tespit edilirse **teslim engeli** (exit 1); DAMGA=NOTR
veya hiç doğrulanmış içtihat atfı olmaması yalnız **uyarı** üretir (bloklamaz).

## Kompozisyon
- **`oa-ictihat`** → CEK adımını yürütür (künye + ham metin, `_oa/teyit/dokum/`).
- **`oa-kiyas`** → MUHAKEME adımını yürütür (DAVAYA-BAĞ, büyük önerme bağı);
  kayıt `oa-kiyas`'ın kendi kıyas JSON'una da (`buyuk_onerme.ictihat`) beslenir.
- **`oa-kontrol`** → MUHAKEME'nin DAMGA/AYIRT-ETME disiplinini + A listesi
  atıf denetimini birlikte yürütür; teslim öncesi son kapıdır.
- **`oa-dilekce`** → yalnız KULLAN adımı: `LEHE`/`ALEYHE-AYIRT` damgalı,
  muhakeme kaydı tamam kararları dilekçeye işler.
- **`oa-antitez`** → `ALEYHE` (ayırt edilmemiş) kayıtların dahili
  cephaneliğidir.

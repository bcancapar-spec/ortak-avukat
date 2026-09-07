# İlliyet Doktrini ve Graf Şeması — oa-illiyet referansı

Bu dosya iki şey içerir: (1) Türk hukukunda illiyet/bağ doktrininin özeti — kitin
hukuki çekirdeği; (2) graf JSON şeması. Norm ve künyeler buradan "ezbere" alınmaz;
somut dosyada **Mevzuat/Yargı Pro ile teyit** edilir. Bu özet yön gösterir, kaynak değildir.

## İçindekiler
1. Medeni hukukta illiyet (haksız fiil / sözleşme)
2. Ceza hukukunda nedensellik
3. İspat bağı (usul)
4. Kurumsal / kişilik bağı
5. Usul rolleri ve geçişleri
6. Graf JSON şeması

---

## 1. Medeni hukukta illiyet

- **Doğal (fiili) illiyet:** conditio sine qua non — "o fiil olmasaydı netice doğmaz mıydı?"
  Olmazsa olmaz şart testi. Graf: `illiyet_tipi: dogal`.
- **Hukuki (uygun) illiyet bağı:** Türk-İsviçre Borçlar Hukukunda **hakim teori**.
  Fiilin, hayatın olağan akışına ve genel hayat tecrübelerine göre o tür sonucu
  doğurmaya elverişli olması. Sadece doğal illiyet yetmez; uygunluk aranır.
  Graf: `illiyet_tipi: uygun`.
- **İlliyet bağının kesilmesi (3 hal):** (1) mücbir sebep, (2) zarar görenin/mağdurun
  ağır kusuru, (3) üçüncü kişinin ağır kusuru. Bunlar nedensellik bağını koparabilir.
  Graf (v0.5.16 — dal önekli): `kesme_flag: medeni:mucbir_sebep | medeni:magdur_kusuru |
  medeni:ucuncu_kisi_kusuru`. Kesmeye varmayan zarar gören kusuru tazminatı indirir /
  kaldırır (TBK m.52 — Mevzuat MCP teyit 2026-09-07); kesme ile indirim ayrı sorulardır.
- **Miras dalı (muris muvazaası / tenkis ekseni):** `kesme_flag: miras:paylastirma_kasti |
  miras:ivaz`. `miras:paylastirma_kasti` = muris muvazaasında bozma gerekçesi — ispat
  ölçütü (mirasçıdan mal kaçırma kastı ispatlanmadan görünürdeki işlem muvazaalı
  sayılmaz; muvazaa çerçevesi TBK m.19 — Mevzuat MCP teyit 2026-09-06; künye KÜTÜKTEN).
  `miras:ivaz` = gerçek bir karşılık (ivaz) varsa görünürdeki işlemin muvazaa iddiası
  zayıflar — ispat konusu.
- **Çoklu illiyet:** müteselsil sorumluluk (birlikte/müşterek illiyet) ve iç ilişkide
  rücu (TBK m.61-62). Yarışan illiyet, farazi illiyet, kısmî illiyet ayrımlarına dikkat.
- Dayanak normlar (teyit et): TBK m.49 vd. (haksız fiil), m.112 vd. (sözleşmeye aykırılık).

## 2. Ceza hukukunda nedensellik

- **Şart teorisi (conditio sine qua non / eşdeğerlik):** her şart neticeye eşit katkı.
  Tek başına yetersiz bulunarak eleştirilir (sınırsız genişleme).
- **Objektif isnadiyet (objektif yükleme) teorisi:** modern doktrin. İki aşama:
  (a) fiil ile netice arasında nedensellik, (b) neticenin faile objektif olarak
  yüklenebilmesi — failin hukuken önemli bir tehlike yaratması ve bu tehlikenin
  neticede gerçekleşmesi. Graf: `illiyet_tipi: objektif_isnadiyet`.
- **Ceza dalında "kesme" (objektif isnadiyet düzeltmeleri — v0.5.16 dal önekli):**
  `kesme_flag: ceza:izin_verilen_risk | ceza:kendi_tehlikesine_girme |
  ceza:hukuka_uygunluk | ceza:magdur_kusuru`. İzin verilen risk ve mağdurun kendi
  tehlikesine girmesi objektif isnadiyeti düşürebilir; hukuka uygunluk nedeni fiilin
  hukuka aykırılığını kaldırır (TCK m.24 vd. — çıpa, bu turda teyit edilmedi).
  **`ceza:magdur_kusuru` — DOKTRİN HATIRLATMASI (hüküm değil):** mağdur kusuru
  ceza dalında illiyeti KESMEZ — kusur derecesine/ceza miktarına etki eder
  (Yargıtay 12. CD yerleşik hattı; künye KÜTÜKTEN, hafızadan yazılmaz). Norm
  çerçevesi: TCK m.22/4 "taksirle işlenen suçtan dolayı verilecek olan ceza failin
  kusuruna göre belirlenir", m.22/5 "herkes kendi kusurundan dolayı sorumlu olur"
  (Mevzuat MCP teyit 2026-09-07). Script §6'da bu notu SABİT basar; kesip kesmediğine
  karar vermez — o karar avukatındır (model kurar, script denetler).
- **Netice sebebiyle ağırlaşmış suç (TCK m.23):** ağır netice için en azından taksir
  bağı aranır (objektif sorumluluk yasağı).
- **İştirak (TCK m.37-39):** faillik/müşterek faillik, azmettirme, yardım etme — kişiler
  arası illiyet-katkı bağları. Graf: ilişki kenarı `tur: istirak`.

## 3. İspat bağı (usul)

- Delil ↔ vakıa ispat bağı (HMK m.187 vd.); ispat yükü (HMK m.190; TMK m.6: iddia eden ispatla).
- **Karineler:** ispat yükünü kaydırır. İlliyet karinesi, fiili karine, kanuni karine.
  Graf: `dogrulama: karine` (delilsiz ama karineye dayalı kenar geçerli sayılır).
- Dijital delil bütünlüğü / zincir (chain of custody) — delil düğümleri arası bütünlük.

## 4. Kurumsal / kişilik bağı

- **TTK temsil:** m.370-371 (temsil yetkisi), ticari mümessil/ticari vekil, m.373 iyiniyetli
  üçüncü kişinin korunması. LTD'de m.629/1 → m.370-378 atfı (müdürün yetki sınırı).
- **Şirketler topluluğu / hakimiyet:** TTK m.195 vd.; bağlı/hakim şirket, kontrol.
- **Tüzel kişilik perdesinin aralanması (perdeyi kaldırma):** organik/ekonomik bağ varsa
  tüzel kişilik ayrılığı göz ardı edilir. Köprü düğüm (iki şirketi bağlayan ortak/müdür)
  bunun tipik sinyali.
- **Muvazaa (TBK m.19):** görünürdeki işlem ile gerçek irade ayrışması; nam-ı müstear.
  İstihkak davalarında sık (mal görünüşte üçüncü kişinin, gerçekte borçlunun).
- **Ticaret modelleme şablonu (v0.5.16, avukat kararı #11 — M4):** organik bağ ve
  tüzel kişilik perdesinin aralanması için grafta **AYRI `hak`/talep düğümleri** kur:
  `hak:organik_bag_talebi` (şirketler arası organik bağ → müteselsil/ortak sorumluluk
  talebi) ve `hak:perde_talebi` (tüzel kişilik perdesinin aralanması → ortağın/diğer
  şirketin sorumluluğu talebi); her ikisini aynı `tuzel_kisi` düğümlerine `iliski`
  kenarlarıyla (`organik_bag`, `hakimiyet`, `muvazaa`) bağla, illiyet kenarını her
  talep için ayrı ispat zinciriyle kur. Gerekçe: Yargıtay iki yolu
  **"alternatif değil, birlikte"** sayar — organik bağ, perdenin aralanmasının
  sinyal/ölçütlerinden biridir
  (künye burada yazılmaz; dilekçeye **kütükten teyitli karar ile** girer — Yargı MCP'de
  2026-09-07'de "organik bağ + tüzel kişilik perdesi" araması sonuç verdi, kararlar
  kütüğe işlenmeden atıf yapılmaz). Köprü düğümün `perde` etiketi (§4 script) bu iki
  düğümün kurulması için TETİKTİR, hükmü değildir.
- **İş hukuku:** İş K. m.2 asıl işveren-alt işveren + muvazaa; organik bağ. Müteselsil
  sorumluluk. SGK rücu (5510 m.21/4) — illiyet zinciri: iş kazası→kusur→SGK ödemesi→rücu.

## 5. Usul rolleri ve geçişleri

İllyet grafında gerçek kişi düğümünün usul rolü zorunludur ve evre boyunca DEĞİŞİR:

- **Soruşturma:** şüpheli · müşteki · mağdur · suçtan zarar gören · ihbar eden
- **Kovuşturma:** sanık · katılan (müdahil, CMK m.237 vd.) · mağdur
- **İnfaz:** hükümlü
- **Hukuk yargısı:** davacı · davalı · asli/fer'i müdahil
- **İcra:** alacaklı · borçlu · üçüncü kişi (istihkak, İİK m.96-99)
- Geçişler: müşteki→katılan; şüpheli→sanık→hükümlü. Aynı kişi farklı dosyada farklı rol.
- **Taraf → tavsiye yönü (v0.5.16 G9):** script `--taraf sanik|mudafii|katilan|musteki|
  davaci|davali|alacakli|borclu` (veya `--kok` ile pipeline defterinin `ceza_dali`
  alanı: mudafii → sanık tarafı, musteki → müşteki tarafı) alır; savunma/borçlu/davalı
  kanadında §6/§7/§8 tavsiyeleri "bu bağı sağlamlaştır" yerine "karşı tarafın bu
  bağını ÇÜRÜT / kesme savunmasını KUR" yönünde yazılır (JSON `yon: kur | curut`).

---

## 6. Graf JSON şeması

```json
{
  "dugumler": [
    {
      "id": "kisa_benzersiz_kimlik",
      "tip": "gercek_kisi | tuzel_kisi | kamu | nesne | delil | olay | hak | karar | mahkeme",
      "usul_rolu": "(gercek_kisi için ZORUNLU: borclu/sanik/katilan/davaci/...)",
      "ad": "Görünen ad"
    }
  ],
  "kenarlar": [
    {
      "kaynak": "dugum_id",
      "hedef": "dugum_id",
      "kategori": "iliski | illiyet",
      "tur": "(iliski: ortaklik/temsil/zilyetlik/muvazaa/asil_alt_isveren/istirak/kanun_yolu/... | illiyet: fiil_netice/sebep_zarar/kusur_zarar/...)",
      "illiyet_tipi": "(illiyet kenarı için: dogal | uygun | objektif_isnadiyet)",
      "guc": "dispozitif | guclu | zayif | tartismali",
      "kesme_flag": "(varsa, DAL ÖNEKLİ: medeni:mucbir_sebep | medeni:magdur_kusuru | medeni:ucuncu_kisi_kusuru | miras:paylastirma_kasti | miras:ivaz | ceza:izin_verilen_risk | ceza:kendi_tehlikesine_girme | ceza:hukuka_uygunluk | ceza:magdur_kusuru)",
      "dayanak_delil": ["delil_dugum_id", "..."],
      "dogrulama": "teyitli | iddia | karine",
      "norm": "İİK m.97 (Mevzuat MCP'den teyitli)",
      "sonuc": "(YALNIZ tur: kanun_yolu kenarında, ZORUNLU: onadi | bozdu | kaldirdi | geri_cevirdi | esastan_ret | kesin)"
    }
  ]
}
```

### Enum tablosu — DOKTRİN ↔ KOD KİLİDİ (v0.5.16)

`grafik_denetim.py` `KANONIK` sözlüğündeki HER değer aşağıda **literal** geçer;
`aile_dogrula.py` bu kilidi mekanik denetler (kodda olup burada olmayan değer = aile
yapı hatası). Yeni değer önce buraya, sonra koda yazılır.

| alan | kanonik değerler | not |
|---|---|---|
| `tip` | `gercek_kisi` · `tuzel_kisi` · `kamu` · `nesne` · `delil` · `olay` · `hak` · `karar` · `mahkeme` | `karar`/`mahkeme` (v0.5.16 G12): kanun yolu katı; köprü hesabından muaf |
| `kategori` | `iliski` · `illiyet` | statik bağ / neden-sonuç |
| `illiyet_tipi` | `dogal` · `uygun` · `objektif_isnadiyet` | §1-2 |
| `guc` | `dispozitif` · `guclu` · `zayif` · `tartismali` | beyansız = 0.4 ≤ tartışmalı |
| `kesme_flag` | `medeni:mucbir_sebep` · `medeni:magdur_kusuru` · `medeni:ucuncu_kisi_kusuru` · `miras:paylastirma_kasti` · `miras:ivaz` · `ceza:izin_verilen_risk` · `ceza:kendi_tehlikesine_girme` · `ceza:hukuka_uygunluk` · `ceza:magdur_kusuru` | dal önekli (v0.5.16 G10); eski çıplak `mucbir_sebep` / `magdur_kusuru` / `ucuncu_kisi_kusuru` → `[ŞEMA UYARISI]` + `--goc` |
| `dogrulama` | `teyitli` · `iddia` · `karine` · `delil` | `delil` = sahada yerleşik `teyitli` eşanlamı |
| `sonuc` | `onadi` · `bozdu` · `kaldirdi` · `geri_cevirdi` · `esastan_ret` · `kesin` | yalnız `tur: kanun_yolu`; HMK m.353 (kaldırma / esastan ret), m.370 (onama); CMK m.280 (esastan ret / bozma / kaldırma), m.302 (esastan ret / bozma) — Mevzuat MCP teyit 2026-09-07 |

**Kanun yolu kenarı (G12):** `tur: kanun_yolu` yalnız `karar | mahkeme` düğümleri
arasında geçerlidir (başka uçta `[ŞEMA UYARISI]`); `sonuc` zorunludur (eksik → exit 3);
kategori `iliski` yazılır (`illiyet` yazılırsa uyarılır). Kanun yolu kenarları illiyet
zincirine, çevrim ve yük hesabına GİRMEZ — yargı kademesi neden-sonuç değildir. Kat
sırası (`kaynak` alt derece kararı → `hedef` üst derece kararı) ve sonuçlar §9 "KANUN
YOLU ZİNCİRİ" bölümünde ve JSON `kanun_yolu_zinciri: [{yol, sonuclar}]` alanında verilir.

**Göç (G10):** eski grafı yeniden etiketlemek için
`python scripts/grafik_denetim.py --goc eski.json --dal medeni|miras|ceza --cikti yeni.json`
— kaynağa dokunmaz, değişen kenar sayısını basar; hedef dalda kanonik olmayan değer
(ör. `--dal ceza` ile `ivaz`) göçmez, "elle düzelt" uyarısı alır.

**Kullanım:** Grafı bu şemaya göre `graf.json` yaz, sonra
`python scripts/grafik_denetim.py graf.json --json denetim.json` ile deterministik
boşluk denetimi yap (`--json` zorunlu — bekçi okur; `--taraf`/`--kok` ile tavsiye yönü).

**Şema sertliği (v0.5.16 — grafik_denetim.py kapısı):**
- Her düğümde `id` zorunlu ve **benzersiz** — mükerrer id şema hatasıdır (ilk kayıt
  korunur, hata basılır, exit 3).
- İlliyet kenarında `illiyet_tipi` VE `dogrulama` zorunlu (eksik → exit 3); doğrulanmamış
  illiyet null kabul edilir, sessizce teyitli sayılmaz.
- `guc` beyan edilmezse kenar **güç beyansız** sınıfına düşer; zincir analizinde ağırlığı
  `beyan-yok = 0.4 ≤ tartışmalı` (beyan etmemek ödüllendirilmez).
- `norm` eksikliği advisory `[ŞEMA UYARISI]`dır (saha grafları kırılmaz); norm yalnız
  Mevzuat MCP teyitli yazılır.
- `dayanak_delil` listesi delil düğümünün **id**'sini taşır; serbest metin yazılırsa delil
  `ad`ıyla ≥0.6 yazım benzerliği bağlı sayar. Hiçbir kenarın dayanağında anılmayan
  `tip: delil` düğümü **bağlanmamış delil** (§2b) olarak ayrı raporlanır — oa-vakia'nın
  yetim delil semantiği; ispat yükü çerçevesi HMK m.190 (Mevzuat MCP teyit 2026-09-06).
- Çevrim (dairesel illiyet) exit 3'tür; çevrimler minimal ve mükerrersiz raporlanır.
- Köprü düğüm etiketi tip-duyarlıdır: `perde` (gerçek kişi + ayırdığı en az iki parçada
  tüzel kişi — muvazaa çerçevesi TBK m.19, Mevzuat MCP teyit 2026-09-06) / `yapisal`
  (nötr). `tip: karar | mahkeme` düğümleri köprü hesabından muaftır.

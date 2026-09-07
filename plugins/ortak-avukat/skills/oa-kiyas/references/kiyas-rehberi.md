# Kıyas Rehberi ve JSON Şeması — oa-kiyas referansı

## Subsumtion (tatbik) mantığı

Türk hukukunda hukuki sonuç, normun somut olaya uygulanmasıyla (subsumtion) doğar.
Açık kıyas bunu üç önermeye böler:

- **Büyük önerme:** Soyut kural. Norm + onu somutlaştıran içtihat. Norm
  **unsurlarına** ayrılır (Tatbestandsmerkmale). Örnekler:
  - Haksız fiil (TBK m.49): fiil · hukuka aykırılık · kusur · zarar · illiyet bağı
  - Sözleşmeye aykırılık (TBK m.112): borç · ihlal · kusur (karine) · zarar · illiyet
  - İstihkak (İİK m.96 vd.): üçüncü kişinin mülkiyet/sınırlı ayni hak iddiası ·
    haczin varlığı · zilyetlik durumu (m.97/a karinesi)
- **Küçük önerme:** Somut maddi vakıa. Her vakıa, büyük önermenin bir veya birden
  çok unsurunu **karşılar** (`karsilar` alanı). Her vakıa delile bağlıdır.
- **Sonuç:** Tüm unsurlar karşılanırsa hukuki sonuç doğar. Karşılanmayan unsur =
  ispat boşluğu veya hukuki dayanak yetersizliği → sonuç o ölçüde zayıflar.

## Norm unsurlarına ayırma — neden kritik

Karşı taraf bütün normu değil, **tek bir unsuru** çökerterek davayı kazanır
(örn. "kusur yok" veya "illiyet bağı kesildi"). Unsurları ayrı yazmak, her birinin
ayrı ayrı ispatlanması gerektiğini ve karşı tarafın nereye vuracağını görünür kılar.
İlliyet bağı unsuru için oa-illiyet grafını kullan.

## JSON şeması

```json
{
  "buyuk_onerme": {
    "norm": "TBK m.49 (Mevzuat MCP'den teyitli)",
    "unsurlar": [
      {"id": "fiil", "ad": "Fiil"},
      {"id": "h_aykiri", "ad": "Hukuka aykırılık"},
      {"id": "kusur", "ad": "Kusur"},
      {"id": "zarar", "ad": "Zarar"},
      {"id": "illiyet", "ad": "İlliyet bağı"}
    ],
    "ictihat": [
      {"kunye": "Y.4.HD E.... K....", "dogrulama": "teyitli"}
    ]
  },
  "kucuk_onerme": {
    "vakialar": [
      {"metin": "Davalı aracıyla kırmızıda geçti", "karsilar": ["fiil","h_aykiri"], "dayanak_delil": ["trafik_tutanagi"]},
      {"metin": "Müvekkil yaralandı", "karsilar": ["zarar"], "dayanak_delil": ["rapor"]}
    ]
  },
  "sonuc": "Fiil/hukuka aykırılık/zarar karşılandı; kusur ve illiyet için ek ispat gerekli."
}
```

## İspat yükü alanları (opsiyonel — v0.5.14)

Karşılanmamış her unsur otomatik olarak bizim boşluğumuz değildir: ispat yükü,
kanunda özel bir düzenleme bulunmadıkça, iddia edilen vakıaya bağlanan hukuki
sonuçtan **kendi lehine hak çıkaran** tarafa aittir (HMK m.190/1 — *"İspat yükü,
kanunda özel bir düzenleme bulunmadıkça, iddia edilen vakıaya bağlanan hukuki
sonuçtan kendi lehine hak çıkaran tarafa aittir."*; aynı yönde TMK m.6). Her
unsura şu **opsiyonel** alanlar yazılabilir — eski dosyalarda yoksa script
çökmez, `bilinmiyor` sayar:

```json
{
  "id": "kusur",
  "ad": "Kusur",
  "ispat_yuku": "bizde | karsi_taraf | resen | bilinmiyor",
  "ispat_yuku_kaynak": "Yükü kaydıran norm/karine çıpası (kullanım anında MCP'den teyit)",
  "curutme_hazirligi": ["Karşı taraf yükünü kaldırırsa ne yapacağız — dahili"]
}
```

`ispat_yuku` **kapalı enum**dur; dışında bir değer script tarafından
YORUMLANMAZ (görünür uyarı + `bilinmiyor`). `unsur_vakia_eslesme[].durum`
alanı dört değerlidir: `karsilanan_delilli · karsilanan_delilsiz ·
karsilanmamis · ispat_yuku_karsida`.

**Carve-out üç şartlıdır (fail-CLOSED):** `ispat_yuku == "karsi_taraf"` **+**
dolu `ispat_yuku_kaynak` **+** boş olmayan `curutme_hazirligi`. Üçü birlikte
yoksa unsur eskisi gibi karşılanmamış ve **kritik** sayılır; rapor "carve-out
VERİLMEDİ" der. `curutme_hazirligi` DAHİLİdir — raporun 5. bölümü filigranlıdır,
dilekçeye kopyalanmaz.

## Yarışan normlar — `buyuk_onermeler` listesi (opsiyonel — v0.5.16, P1-4/A-15)

Aynı vakıa birden çok norma bağlanabiliyorsa (sözleşme ↔ haksız fiil talep
yarışması; özel ↔ genel kanun) büyük önerme **tekil sözlük yerine liste**
yazılır. Ölçüt **TBK m.60** (Mevzuat MCP teyit 2026-09-06): *"Bir kişinin
sorumluluğu, birden çok sebebe dayandırılabiliyorsa hâkim, zarar gören aksini
istemiş olmadıkça veya kanunda aksi öngörülmedikçe, zarar görene en iyi giderim
imkânı sağlayan sorumluluk sebebine göre karar verir."* "En iyi giderim"
karşılaştırması dört sütunda yapılır: **zamanaşımı uzunluğu · kusur şartı ·
ispat kolaylığı · faiz** (başlangıcı/türü).

```json
{
  "buyuk_onermeler": [
    {
      "norm": "TBK m.112 (sözleşmeye aykırılık — Mevzuat MCP teyitli)",
      "secili": true,
      "unsurlar": [{"id": "borc", "ad": "Borç"}, {"id": "ihlal", "ad": "İhlal"},
                   {"id": "kusur", "ad": "Kusur (karine)"}, {"id": "zarar", "ad": "Zarar"}],
      "ictihat": [{"kunye": "…", "dogrulama": "teyitli"}],
      "zamanasimi": "TBK m.146 — 10 yıl (kullanımda teyit)",
      "kusur_sarti": "kusur karinesi — borçlu kusursuzluğunu ispatlar",
      "ispat_kolayligi": "borç ilişkisi ve ihlal belgeli",
      "faiz": "temerrüt tarihinden",
      "secim_gerekcesi": "daha uzun zamanaşımı + kusur karinesi; en iyi giderim (TBK m.60)"
    },
    {
      "norm": "TBK m.49 (haksız fiil — Mevzuat MCP teyitli)",
      "unsurlar": [{"id": "fiil", "ad": "Fiil"}, {"id": "kusur", "ad": "Kusur"},
                   {"id": "zarar", "ad": "Zarar"}, {"id": "illiyet", "ad": "İlliyet"}],
      "ictihat": [],
      "zamanasimi": "TBK m.72 — 2 / 10 yıl (kullanımda teyit)",
      "kusur_sarti": "davacı ispatlar",
      "ispat_kolayligi": "kusur ve illiyet ispatı bizde",
      "faiz": "zarar (olay) tarihinden"
    }
  ],
  "kucuk_onerme": { "vakialar": [ "…" ] },
  "sonuc": "…"
}
```

Kurallar:
- Her öğe **{norm, unsurlar, ictihat, zamanasimi, kusur_sarti, ispat_kolayligi,
  faiz, secim_gerekcesi}** alanlarını taşır; `secili: true` işaretli öğe
  (yoksa listenin **ilki**) subsumtion denetimine (§3) esas alınır.
- **≥2 aday varsa** rapor §2.a'da **YARIŞAN NORMLAR** karşılaştırma tablosu
  basılır ve seçilen önermede `secim_gerekcesi` **zorunludur**; boşsa
  «✗ yarışan norm seçimi gerekçesiz» satırı + kritik boşluk (exit yine 0 —
  2026-08-12 Can kararı: kapı değil karar-malzemesi).
- Karşılaştırma alanı boş kalırsa tabloda `—` + görünür uyarı (kritik DEĞİL —
  yorum avukatındır). Sözlük olmayan öğe görünür uyarıyla atlanır.
- Tek öğeli liste yarışma sayılmaz (tablo ve gerekçe aranmaz). Hem
  `buyuk_onerme` hem `buyuk_onermeler` yazılmışsa liste esas alınır, görünür
  uyarı basılır.
- JSON çıktısında **`buyuk_onerme.yarisan_normlar`** listesi (her öğe: norm ·
  zamanasimi · kusur_sarti · ispat_kolayligi · faiz · secim_gerekcesi ·
  secili); tekil şemada boş liste — eski dosyalar değişmeden çalışır.
  ÜST-DÜZEY anahtar kümesi değişmez (K1 ileri koruması, v0.5.14).
- Zamanaşımı/faiz madde çıpaları bu tabloda **iddia**dır; kullanım anında
  Mevzuat MCP'den teyit edilir, hafızadan yazılmaz.

## Kullanım
`kiyas.json` yaz, `python scripts/kiyas_denetim.py kiyas.json --json _oa/cikti/05-kiyas-denetim.json` çalıştır (`--json` ZORUNLU — pipeline K1 bekçisi bu damgayı okur). Script
karşılanmamış unsuru, delilsiz vakıayı, teyitsiz içtihadı ve yetim vakıayı yakalar.
Norm hiç unsurlara ayrılmamışsa denetim YAPILAMAMIŞ sayılır ve kritik boşluk
basılır ("yapı bütün" DEĞİL). Girdi okunamaz/bozuk ya da kökü sözlük değilse
traceback yerine tek satırlık hata + exit 1 döner.
Yorum ve nihai sonuç avukata aittir.

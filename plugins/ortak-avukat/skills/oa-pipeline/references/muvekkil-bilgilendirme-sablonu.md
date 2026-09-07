# Müvekkil Bilgilendirme Notu İskeleti — oa-pipeline referansı (P1-9, v0.5.16)

KAPANIŞ (adım 10) adımında, dosyada **müvekkil kararı gerektiren bir kavşak** varsa
(`pipeline_kayit.py --muvekkil-karari …` ile açılmış — sulh teklifi, dava değeri, risk
kabulü, tedbir teminatı ve kıyasen benzerleri) müvekkile yazılacak bilgilendirme notu
bu iskeletle kurulur. Konu sayımı örneklemdir (anayasa m.3); listede olmayan kavşak aynı
iskeletle işlenir.

## Hukuki dayanak (Mevzuat MCP teyit 2026-09-06)

**1136 sayılı Avukatlık Kanunu m.34** (Değişik: 2/5/2001 - 4667/21 md.) — Mevzuat MCP'den
çekilen madde metni: *"Avukatlar, yüklendikleri görevleri bu görevin kutsallığına yakışır
bir şekilde özen, doğruluk ve onur içinde yerine getirmek ve avukatlık unvanının
gerektirdiği saygı ve güvene uygun biçimde davranmak ve Türkiye Barolar Birliğince
belirlenen meslek kurallarına uymakla yükümlüdürler."* (kaynak: mevzuat.gov.tr,
MevzuatNo=1136, Tertip 5 — `mevzuat_getir` id `mevzuatgov:kanun:5:1136`, madde 34).

Dürüst okuma: m.34 metni "bilgilendirme" sözcüğünü **lafzen içermez**; müvekkilin
kararı gerektiren kavşakta bilgilendirilmesi, maddedeki **özen ve doğruluk** yükümünün
somut görünümüdür. TBB Meslek Kuralları'nın ilgili hükmü bu belgede **teyit edilmedi**
(çıpa — teyit edilmedi); notta ayrıca anılacaksa oa-ictihat/Mevzuat MCP ile önce teyit edilir.

## Sınıf: DIŞ ÇIKTI — m.6 ve Layer 0

Bu not müvekkile gider; müvekkilin elinden üçüncü kişiye/karşı tarafa geçebilir.
- **Anayasa m.6 (müvekkil-aleyhi dış çıktı yasağı):** notta müvekkilin pozisyonunu
  zayıflatan ikrar, karşı tarafa koz veren ifade, "haksızız" sınıfı cümle YAZILMAZ.
  Riskler **karar için gerekli ölçüde ve nesnel dille** anlatılır; zaaf analizi ve
  antitez cephaneliği (`_oa/cikti/06-antitez-*`) İÇ dosyada kalır, nota kopyalanmaz.
- **Layer 0 (`oa-gizlilik`):** not e-posta/bulut/dış araca çıkmadan önce taranır (TC,
  esas no, sağlık/ceza verisi, üçüncü kişi verileri). Şablondaki köşeli parantezler
  gerçek veriyle yalnız avukatın kendi ortamında doldurulur.
- **Anonimlik (m.7):** bu şablon ve `_oa/dersler` kaydı gerçek isim taşımaz; deftere
  düşen konu metni de ("Sulh teklifi" gibi) kimlik taşımamalıdır.

## İskelet

```markdown
Sayın [müvekkil hitabı],

[Dosya kısa tanımı — konu düzeyinde, esas/karar no yalnız müvekkilin kendi bilgisi ise]

1. KARAR GEREKTİREN KONU
   [Konu — DURUM.md > Müvekkil Kararı Bekleyen satırıyla aynı]

2. SEÇENEKLER (defterde açılan seçeneklerle birebir)
   a) [seçenek a] — [öngörülen sonuç / maliyet / süre]
   b) [seçenek b] — [öngörülen sonuç / maliyet / süre]
   c) [seçenek c] — [...]

3. HER SEÇENEĞİN RİSKİ (nesnel, karar için gerekli ölçüde; m.6 — aleyhe ikrar yok)
   [Olasılık sayı uydurulmaz — oa-strateji dürüst değerlendirme disiplini; süre sınırı
    varsa oa-sure hesabıyla son gün yazılır]

4. AVUKATIN MESLEKİ GÖRÜŞÜ (öneri, karar değil)
   [Gerekçeli öneri — karar müvekkilindir]

5. KARAR VE SÜRE
   Kararınızı [son tarih — oa-sure hesabına dayalı] tarihine kadar bildirmenizi rica ederim.
   [Karar alınınca: pipeline_kayit.py --muvekkil-karari-kapat "<konu>" --karar "<seçim>"
    --gerekce "<müvekkilin gerekçesi / bildirim yolu ve tarihi>"]

Saygılarımla,
[Av. — imza bloğu]
```

## Kapanış ritüeliyle bağ

- Kapanmamış müvekkil kararı varken adım-10 UYGULANDI yazılırsa `pipeline_kayit.py`
  görünür UYARI basar (bloklamaz). Uyarı, bu notun yazılıp gönderildiğinin değil,
  **kararın deftere işlendiğinin** yokluğunu söyler; not gönderildiyse de karar gelene
  kadar kavşak AÇIK kalır.
- Müvekkilin kararı ve gerekçesi deftere (`muvekkil_karari_kapat`) işlenince
  DURUM.md «Müvekkil Kararları (Kayıtlı)» bölümüne düşer; append-only — eski BEKLEYEN
  izi kaybolmaz.

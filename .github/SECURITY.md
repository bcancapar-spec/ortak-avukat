# Güvenlik bildirimi

Bu depo bir hukuk bürosunun çalışma aracıdır. Müvekkil verisi depoya hiçbir zaman
girmez: çalışma kökü `_oa/` `.gitignore`'dadır ve anayasa m.7 (anonimlik) ile m.10
(Layer 0 gizlilik) bunu mekanik olarak denetler. Yine de bir güvenlik açığı
bulursanız şu yolu izleyin.

## Nasıl bildirilir

- Müvekkil verisi, dosya veya esas numarası, UYAP oturumu, e-imza ya da PIN deseni
  içeren **hiçbir** bulguyu herkese açık bir issue'ya yazmayın.
- Bulguyu e-posta ile bildirin: **b.cancapar@gmail.com**, konu satırı
  `ortak-avukat güvenlik`. Yeniden üretim adımlarını sentetik veriyle yazın
  (kurgu dosya numarası, kurgu ad).
- Hangi sürümde gördüğünüzü yazın (`claude plugin list` çıktısındaki Version
  satırı ya da `plugins/ortak-avukat/.claude-plugin/plugin.json`).

## Kapsam

- Eklenti scriptleri: `plugins/ortak-avukat/skills/*/scripts/`
- Kanca katmanı: `plugins/ortak-avukat/hooks/` (her oturumda kendiliğinden koşar)
- Teslim zinciri: `udf_yaz.py`, `teslim_paketi.py`, `muhur_yaz.py`
- Belge güvenlik kapısı: `belge_guvenlik.py`, `gizli_talimat_ifsa.py`
  (gizli talimat savunması, anayasa m.11)
- Layer 0 gizlilik süzgeci: `gizlilik_tara.py`

Üçüncü taraf bileşenler (Yargı Pro MCP, `udf-cli`, Tesseract, PyMuPDF) bu deponun
parçası değildir; onlara ilişkin bulgular kendi sağlayıcılarına bildirilir. Depo
yalnız Yargı Pro'yu ilan eder; başka bir MCP sunucusu ilan edilmez ve bu testle
kilitlidir (`tests/test_v0518_mcp_ilan.py`).

## Desteklenen sürüm

Yalnız en son yayımlanan sürüm (GitHub Releases) desteklenir; eski sürümler için
yama yayımlanmaz, güncelleme yolu kök README'dedir.

## Ne olur

Bildirim yanıtlanır. Düzeltme, kusuru yeniden üreten kırmızı testle birlikte
yapılır ve sürüm defterine (`CHANGELOG.md`) işlenir; bildiren, isterse, orada
anılır. Müvekkil verisi içeren bir bulgu alınırsa veri saklanmaz ve bildirene
silmesi söylenir.

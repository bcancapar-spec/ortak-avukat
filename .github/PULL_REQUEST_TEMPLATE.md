## Ne değişti, neden

<!-- Tek paragraf: ne değişti, NEDEN VAR (hangi saha kanıtı, hangi denetim bulgusu). -->

## Kontrol listesi (depo sözleşmesi)

- [ ] Önce kırmızı test: kusuru yeniden üreten test eklendi, düşerken görüldü, onarımla yeşile döndü.
- [ ] `python -m pytest tests -q -n auto -m "not perf"` ve `python -m pytest tests -q -m perf -p no:xdist` yeşil.
- [ ] `python plugins/ortak-avukat/skills/oa-usta/scripts/aile_dogrula.py plugins/ortak-avukat/skills` TEMİZ ve `python -m ruff check .` temiz.
- [ ] Test sayısı değiştiyse `tests/README.md` OA-SUIT-SAYISI güncellendi (tek kaynak); vitrin künyesi `python tools/satir_sayaci.py --yaz` ile tazelendi.
- [ ] Sürüm değiştiyse damgalar birlikte arttı: `plugin.json`, `marketplace.json`, `STATUS.md`, `YOL-HARITASI.md`, `pyproject.toml`.
- [ ] Anayasa m.7: hiçbir kişi, müvekkil, dosya adı veya numarası, mutlak yerel yol kod ve belgeye girmedi.
- [ ] Kaynakta ham görünmez karakter yok (gerekiyorsa kaçışla yazıldı); belge bağlantıları çözülüyor (`tests/test_belge_baglantilari.py`).
- [ ] `CHANGELOG.md` ve ilgili parçanın `references/degisiklik-gunlugu.md` dosyasına kayıt düşüldü.
- [ ] Hukuki içerik değiştiyse norm ve içtihat resmî kaynaktan teyitli; karar avukatın (anayasa m.4, m.9).

## Bu ortamda doğrulanamayan

<!-- Dürüst sınır: sınanamayan ne var (ör. udf-cli oturumu yok, Tesseract yok)? Açıkça yazın. -->

# oa-ingest

*Ortak Avukat ailesi · v1.0 · bir `oa-*` parçası*

Ortak Avukat sisteminin ÇIKARIM / AI KATMANI parçası ve 0. MANİFEST adımının metin motoru. UYAP evrak indiricisinin "insan gözü" için ürettiği klasörü (PDF/TIFF/JPG/EYP/UDF/DOCX) yapay zekânın ucuza ve kesintisiz okuyabileceği metne çevirir: her evrağın metnini deterministik script ile en ucuz doğru yoldan bir kez çıkarır, belge-başına Markdown + tek `kunye.json` + `00-INDEX.md` üretir. Böylece sonraki tüm parçalar külliyatı görüntü değil ucuz metin ve indeks üzerinden seçici okur. Bağlam kopmaz: her metin kaynağına (evrak no+dosya+sayfa+yöntem) bağlıdır, OCR çıktısı "⚠ teyit" damgalıdır, orijinal salt-okunur arşivde durur.

## Deterministik scriptler

- `scripts/oa_ingest.py`

> Script modelin muhakemesini **denetlemez, besler**: ham evrağı ucuz metne çevirir; neyin esaslı olduğu muhakemeye ve `oa-vakia`/`oa-ictihat`'e kalır. Model kurar, script çıkarır.

## Bağımlılıklar

- `pip install pymupdf pillow` (PDF + görüntü; Windows'ta binary gerektirmez)
- OCR için (yalnız taranmış evrakta): **Tesseract** + `tur` dil paketi
  - Windows: UB-Mannheim kurucusu (kurulumda "Turkish" + "Add to PATH")
  - Linux: `apt-get install tesseract-ocr tesseract-ocr-tur`
- Tesseract yoksa metin PDF/UDF/DOCX yine işlenir; taranmışlar "YÜKLENEMEDİ ⚠" damgalanır.

## Referanslar

- `references/degisiklik-gunlugu.md`

## Nasıl çalışır

`ortak-avukat` çekirdeği tetiklendiğinde `oa-pipeline` bu parçayı 0. adımda (MANİFEST) otomatik zincire sokar (elle seçmeye gerek yok). Tek başına `/ortak-avukat:oa-ingest` ile de çağrılabilir; manuel CLI için `python scripts/oa_ingest.py "<dava_klasoru>"`.

## Çıktı

`<dava_klasoru>/_oa/metin/` → `00-INDEX.md` (seçilebilir evrak tablosu), `00-kunye.json` (makine-okur künye), `NNN-<slug>.md` (belge-başına metin).

---
© 2026 Av. Bayram Can Çapar — Bu eserin tüm fikri mülkiyet, mali ve manevi hakları saklıdır (5846 sayılı FSEK). İzinsiz çoğaltma, dağıtma veya türev çalışma yasaktır.

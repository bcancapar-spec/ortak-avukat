# ÇIKTI ŞEMASI — 40-UYAP dış-çıktı dizini (v0.5.9, A1 doktrin)

© 2026 Av. Bayram Can Çapar — 'Ortak Avukat' metodoloji sistemi.

Bu belge, dava kökündeki **muhatap-nötr dış-çıktı dizini `40-UYAP/`** şemasının
tek yetkili tanımıdır. Mekanik kurucusu: `oa-kontrol/scripts/teslim_paketi.py`
(A2 — yalnız YEŞİL makbuz yolunda çalışır).

## 1. 40-UYAP nedir? (muhatap-nötr / yön-belirli)

`40-UYAP/`, dava kökünde **dışa giden HER şeyin** tek durağıdır: UYAP'a
yüklenecek dilekçe, karşı vekile ihtarname, kuruma başvuru, müvekkile rapor —
hepsi. Ad "UYAP" dese de dizin **muhatap-nötrdür**: sınıflandırma muhataba
göre değil, YÖNE göredir (içeride kalan çalışma evrakı `_oa/` altında yaşar;
dışa çıkan ürün `40-UYAP/`ta durur). Avukat UYAP'a YÜKLERKEN — ya da herhangi
bir dış muhataba gönderirken — `40-UYAP/`taki kopyayı kullanır; `_oa/` içinde
dosya aramaz.

İçerik (YEŞİL makbuz kesildiğinde `teslim_paketi.py` tarafından kurulur):
- nihai teslim ürünlerinin KOPYALARI (UDF + varsa aynı kök-adlı PDF/DOCX),
- `teslim-makbuz-KOPYA.json` — yeşil makbuzun damgalı kopyası (bkz. §3).

## 2. Tek-nüsha ilkesi (KOPYA, taşıma DEĞİL)

`40-UYAP/`taki her dosya bir **kopyadır**; asıl tektir ve yerinden OYNAMAZ:
- ürünün aslı `_oa/cikti` (ya da üretildiği yer) — mührünün (`.prov.json`)
  YANINDA kalır; mühür↔dosya çifti asla ayrılmaz,
- makbuzun aslı `_oa/defter/teslim-makbuz.json` — teslim tanımının tek
  ölçütü ODUR (P1-11); `40-UYAP/`taki kopya teslim beyanına dayanak OLAMAZ.

**SEMBOLİK LİNK YASAKTIR:** Windows'ta symlink güvenilmez (yetki/junction
tuzakları); kopya ise zip'lenip taşınabilir — dış muhataba giden klasörün
taşınabilirliği şemanın var oluş nedenidir.

**Tarayıcı-dışlama sözleşmesi:** `40-UYAP/` dışa giden KOPYA dizinidir, gelen
evrak DEĞİLDİR — ham-evrak tarayıcıları (`oa_ingest.py` / `tam_tur.py` /
`manifest_olustur.py`, ortak `ATLA_DIZIN` kümesi) onu `_oa` gibi ATLAR. Aksi
hâlde kurucu, yeşil teslimin hemen ardından kendi kopyasıyla KUNYE BAYAT /
delta yanlış-pozitifi üretirdi (öz-bulaşma).

## 3. KOPYA damgası kuralı

`teslim-makbuz-KOPYA.json` içine mekanik olarak şu alan eklenir:

```json
"_damga": "KOPYA — asil: _oa/defter/teslim-makbuz.json"
```

Bu damga, kopyanın kendi içinden asla "asıl makbuz" sanılmamasını sağlar
(777 sahası dersi: makbuz-şekilli yan dosyalar yeşil makbuz BEYANINA dayanak
yapılmıştı). Damgasız bir makbuz-kopyası şema-dışıdır. Asıl makbuzda da izi
vardır: `uyap_kopya` alanı kopyanın köke-göreli yolunu
(`40-UYAP/teslim-makbuz-KOPYA.json`), `uyap_urun_kopyalari` alanı ürün
kopyalarını taşır.

## 4. Advisory doğuş + veriyle kapıya terfi yolu

Bu şema **advisory doğar** (v0.5.5 dersi: yanlış katmanı sertleştirme;
tetiklenme kanıtı olmadan kapı kurulmaz):
- 40-UYAP kurulumu/kopyalaması HATASI teslimi KIRMAZ — görünür uyarı basılır,
  exit kodu DEĞİŞMEZ (yeşil yeşil kalır),
- makbuz RED iken ya da hiç yokken 40-UYAP ÜRETİLMEZ (dışa çıkacak ürün yok).

**Kapıya terfi yolu (veriyle):** 2-3 saha koşusundan sonra uyarı tetiklenme
sayısına bakılır — kopya hatası/40-UYAP-dışı yükleme fiilen yaşanıyorsa şema
engelleyici kapıya terfi ettirilebilir; yaşanmıyorsa advisory kalır (ateşlemeyen
kapı kurulmaz — AMAÇ ÇİZGİSİ). **Terfi kararı avukatındır**, sayaç yalnız
kanıtı hazırlar.

## 5. Ertelenen bekçiler (v0.5.10 notu)

**A3/A4 bekçileri bu sürümde YOKTUR — bilinçli olarak v0.5.10'a ertelendi:**
40-UYAP içeriğini denetleyen kapılar (ör. bayat-kopya nöbetçisi: asıl ürün
değişti ama 40-UYAP kopyası eski kaldı; 40-UYAP-dışından yükleme uyarısı).
v0.5.9'da yalnız KURUCU (A2) vardır; bekçiler §4'teki saha verisi toplandıktan
sonra tasarlanır (deterministik · tamamlayıcı · kesintisiz · sürtünmesiz
dört-ilke süzgecinden geçerek).

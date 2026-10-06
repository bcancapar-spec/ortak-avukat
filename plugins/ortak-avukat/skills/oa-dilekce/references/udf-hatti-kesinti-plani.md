# UDF HATTI KESİNTİ PLANI — udf-cli servisi düştüğünde iş sürekliliği (v0.5.16 — B-6 / P2-12)

> © 2026 Av. Bayram Can Çapar — FSEK. Bu belge KOD DEĞİŞTİRMEZ; mevcut
> araçların kesinti anındaki kullanım sırasını ve avukatın karar noktalarını
> yazar. Bağlayıcı çerçeve: SKILL.md "ALTIN KURAL — UDF ELLE YAZILMAZ"
> (UDF yalnız `udf-cli html2udf` ile üretilir; elle zip/`content.xml`
> YASAK; `--yerel-motor` EMEKLİ, HATA verir) ve "TESLİM tanımı tekildir"
> (yalnız `teslim_paketi.py` exit 0 + `_oa/defter/teslim-makbuz.json`).

## 0. Neyi çözer, neyi çözmez

`udf_yaz.py` tek gerçek yazıcı olarak `npx -y udf-cli@0.5.6 html2udf`
çağırır; bu adım **ağ + oturum** (`udf-cli login`) ister. Servis düştüğünde
(npm kaydı erişilemez, udf-cli sunucusu yanıt vermiyor, oturum açılamıyor,
paket yeni sürümde kırık) script **FAIL-CLOSED** çıkar: hiçbir `.udf`
yazılmaz, exit != 0, stderr'de talimat. Bu plan, o anda **teslimin
durmaması** için hangi yolların meşru olduğunu sıralar. Çözmediği şey:
UYAP'a **UDF** olarak yükleme — bu yalnız servis dönünce ya da UYAP
editörüyle olur; plan bunu **gizlemez**, makbuza yazdırır.

Kesinti teşhisi (bir dakika): `npx -y udf-cli@0.5.6 whoami` → (a) komut
bulunamadı / ağ hatası = SERVİS/AĞ kesintisi, (b) "giriş gerekli" = OTURUM
kesintisi (login yenilenir, plan gerekmez), (c) html2udf hata veriyor ama
whoami OK = PAKET kırığı (§4 pin kararı).

## 1. Yol A — PDF nüsha: `udf_html2pdf.py` (ağsız)

- `udf_yaz.py --girdi taslak.md --cikti dilekce.udf --pdf dilekce.pdf`
  zaten **UDF üretimi başarısız olsa BİLE** PDF bacağını dener: aynı
  UDF-HTML (`md_udf_html.py`) A4 PDF'e dökülür (PyMuPDF; Times New Roman
  TTF gömülür — font yoksa PDF yine çıkar, UYARI basılır). Tek başına:
  `python scripts/udf_html2pdf.py --girdi taslak.udf.html --cikti dilekce.pdf
  --baslik "…"`.
- PDF, **UYAP dışı** teslim kanalları için tam nüshadır: müvekkile
  gönderim, karşı vekile e-posta, fiziki dosya, noter, kurum başvurusu, arşiv.
  Şekil standardı (1,5 satır, 42.52 pt kenar, 11 pt linkler) aynı HTML'den
  geldiği için PDF de bunu taşır.
- PDF **UDF değildir**: UYAP "Doküman" alanına UDF ister; PDF ancak "ek"
  olarak yüklenebilir (avukat kararı — dilekçenin kendisi ek olarak
  yüklenemez, aşağıdaki §2 gerekir).
- Sınır: PyMuPDF kurulu değilse script açık HATA ile çıkar (sessiz atlama
  yok); o durumda md/HTML nüsha kalır — bkz. §2.

## 2. Yol B — UYAP Doküman Editörüne yapıştırma (avukat yapar; aile kod yazmaz)

Layer 0 (anayasa m.10): UYAP login / e-imza / PIN adımları **münhasıran
avukata aittir**; aile bu adımlar için hiçbir otomasyon üretmez, yalnız
metni hazırlar.

1. Kaynak metin: `_oa/cikti/…-dilekce.md` (asıl) — ya da `md_udf_html.py`
   ile üretilmiş `.udf.html` tarayıcıda açılıp seçilir (biçim korunur).
2. UYAP Avukat Portal → ilgili dosya → "Dilekçe/Evrak Hazırla" → UYAP
   Doküman Editörü (Java) açılır; metin **yapıştırılır**, başlık/hiza/
   numaralı liste editörde gözle kontrol edilir (yapıştırma sonrası girinti
   ve satır aralığı kaybolabilir — 1,5 satır ve kenar boşlukları editörde
   yeniden verilir; Yön. 2646 m.8 — SKILL.md şekil standardı).
3. Editörden **UDF olarak kaydet** → bu dosya udf-cli çıktısıyla aynı sınıf
   gerçek üretici çıktısıdır (`hvl-default` stil tanımı taşır);
   `python scripts/udf_yaz.py --dogrula <indirilen>.udf` ile mekanik kapı
   yine koşulur (resmî okuyucu bacağı servis yokken "YAPILAMADI" der —
   görünür, engel değil).
4. E-imza + gönderim: avukat. Bu yolla üretilen UDF'in **kaynak-bloğu ve
   mühürü** (`muhur_yaz.py --urun <udf>`) elle yeniden koşulur — yoksa
   tazelik denetimi bu ürünü göremez.

Bu yol servis kesintisinde **UDF üretiminin tek meşru yoludur**; elle
`content.xml` kurmak (372 dersi 10-D) bu yolun alternatifi DEĞİLDİR.

## 3. Yol C — `teslim_paketi.py --udf-yok` (bilinçli atlama, makbuza yazılır)

- `python ../oa-kontrol/scripts/teslim_paketi.py <taslak.md> --tip … --taraf …
  --kok . --udf-yok` → tüm engelleyici kapılar ([A]-[F], künye teyit,
  gizlilik, defter) AYNEN koşar; yalnız UDF üretim adımı **"ATLANDI
  (--udf-yok BİLİNÇLİ istekle)"** olarak raporlanır ve makbuza
  `udf_atlandi_istekle: true` yazılır. `40-UYAP/` dizinine kopyalanacak ürün
  yoksa bu da görünür bildirilir.
- Bu, "UDF yok ama dilekçe HUKUKEN teslime hazır" beyanının **tek dürüst
  kaydıdır**: kapılar geçilmiş, biçim borcu açıkça ertelenmiştir. Servis
  dönünce `udf_yaz.py` ile UDF üretilir ve `teslim_paketi.py` **--udf-yok'suz
  yeniden** koşulur (yeni makbuz; eski makbuz defterde tarihçe olarak kalır).
- Yasak: `--udf-yok` makbuzuyla "UDF teslim edildi" DEMEK. Makbuzdaki alan
  tam da bunu ayırt etmek için vardır (sessiz atlama yasağı).
- Bayrak `udf_yaz.py`'ye değil `teslim_paketi.py`'ye aittir; `udf_yaz.py`
  servis yokken her hâlde fail-closed'dur.

## 4. Pin kararı — VERİLDİ: (b) bilinen-iyi sürüme pin (kullanıcı kararı, 2026-10-05)

Hat v0.5.18'den itibaren **`udf-cli@0.5.6`** sürümüne sabitlidir. Sürüm
`scripts/udf_yaz.py` içindeki TEK sabittedir (`UDF_CLI_SURUM`); `whoami`,
`html2udf`, `udf2md` çağrıları ve kullanıcıya basılan giriş talimatı bu
sabiti kullanır; üretim makbuzu (`_oa/defter/udf-uretim-makbuz.jsonl`)
kullanılan paketi `uretici_paket` alanına yazar. Gerekçe: sabitlenmemiş en son
sürüm her koşuda kayıttaki en yeni yayını çeker — kırık ya da değişmiş bir
yayın denetimsiz biçimde teslim zincirine girer, dün çalışan komut bugün
çalışmayabilir (yeniden üretilebilirlik yok); npm kaydına göre paketin
geliştirme bağımlılıklarında kod karartıcı bulunduğundan yayımlanan kodun
denetimi de zordur. Sürüm bilgisi (en son yayın 0.5.6 — 2026-09-28; bir
önceki 0.5.5 — 2026-09-22; kaynak deposu github.com/saidsurucu/udf-cli; MIT)
ana ajanın 2026-10-05 tarihli npm kaydı okumasına dayanır.

Karar kaydı (seçenekler):

| Seçenek | Ne yapar | Bedel | Durum |
|---|---|---|---|
| (a) sabitsiz en son sürüm | v0.5.17'ye kadarki davranış | kırık/değişmiş yayın = denetimsiz değişiklik ya da kesinti | BIRAKILDI |
| (b) bilinen-iyi sürüme pin | `udf-cli@<UDF_CLI_SURUM>`; her koşu aynı üretici | UYAP tarafı değişince eski sürüm uyumsuz kalabilir; yükseltme bilinçli iş olur | **SEÇİLDİ (v0.5.18)** |
| (c) pin + en son sürüm yedeği | önce pinli sürüm, hata verirse en son sürüm denenir | iki sürüm evreni — denetimsiz yayın kapısı yeniden açılır | uygulanmadı |
| (d) yerel önbellek | `npx` yerine önceden kurulu global `udf-cli` (`--npx` ile komut yolu) — npm kaydı erişilemese de paket eldedir; **sunucu/oturum** kesintisini ÇÖZMEZ | önbellek bayatlar; sürüm yine bilinçli yönetilmeli | ayrıca değerlendirilebilir |

**Yükseltme yöntemi:** sürüm yalnız AVUKAT ONAYIYLA değişir; yeni sürümün
yayım notları okunur, sahte-npx testleri ve (oturumlu ortamda) gerçek yazıcı
altın vakası geçer; `UDF_CLI_SURUM` ile birlikte oa-dilekce belgelerindeki
komut örnekleri aynı değişiklikte güncellenir (test, belgelerdeki sürümün
sabitle aynı olmasını kilitler) ve değişiklik günlüğüne eski → yeni sürüm ile
gerekçe yazılır. "html2udf hata veriyor ama whoami OK" (paket/UYAP uyumsuzluğu)
hâlinde önce §1-§3 yolları, sonra yükseltme değerlendirmesi.

**Aynı risk sınıfı — aynı karar kapsamında sabitlendi (2026-10-05):**
`docx2udf` (`udf_yaz.py` → `DOCX2UDF_SURUM = "1.0.6"`; npm kaydında lisans ve
kaynak depo alanı YOKTUR — denetlenebilirlik düşük, yükseltmede ayrıca temkin),
belgede önerilen `uyap-tiff-cli@0.4.4` ve `uyap-pdf-cli@0.3.4` (ikisi de
UNLICENSED; geliştirme bağımlılıklarında kod karartıcı var — OA bu ikisini
ÇAĞIRMAZ; yerel `oa-ingest` hattı tercih edilir). Sürüm bilgileri ana ajanın
npm kaydı okumasına dayanır (2026-10-05).

## 5. Kesinti anı kontrol listesi (sıra)

1. Teşhis: `whoami` (§0) — oturum ise login, plan gerekmez.
2. Servis/paket kesintisi ise: **teslim aciliyeti var mı?** Yoksa bekle;
   `oa-sure` son günü yakınsa devam.
3. `udf_yaz.py … --pdf` koş → PDF nüsha + `.udf.html` ara ürün elde (Yol A).
4. UYAP'a bugün girmesi ŞARTSA: Yol B (editöre yapıştır, UDF'i editörden
   kaydet, `--dogrula`, mühür).
5. Teslim zincirini kapat: `teslim_paketi.py --udf-yok` (Yol C) → makbuz +
   `00-TESLIM.md`'ye "UDF: servis kesintisi — Yol B/C" notu.
6. Servis dönünce: `udf_yaz.py` ile UDF, `teslim_paketi.py` bayraksız
   yeniden; sürüm yükseltme değerlendirmesi (§4) için gözlemi
   `_oa/dersler`'e yaz.

## 6. Yapılmayanlar (dürüst sınır)

- Elle UDF üretimi HİÇBİR koşulda önerilmez (ALTIN KURAL).
- Bu belgenin kendisi kod değiştirmez (B-6 kapsamı: plan). (b) pin kararı
  v0.5.18'de ayrı pakette `udf_yaz.py`'ye işlendi (§4); (c) yedek sürüm
  uygulanmadı.
- UYAP editör adımları avukatın deneyimine bırakılmıştır; menü adları UYAP
  sürümüne göre değişebilir — burada yazılanlar yol tarifi, ekran kaydı
  değildir.

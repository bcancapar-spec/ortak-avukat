# UDF HATTI KESİNTİ PLANI — udf-cli servisi düştüğünde iş sürekliliği (v0.5.16 — B-6 / P2-12)

> © 2026 Av. Bayram Can Çapar — FSEK. Bu belge KOD DEĞİŞTİRMEZ; mevcut
> araçların kesinti anındaki kullanım sırasını ve avukatın karar noktalarını
> yazar. Bağlayıcı çerçeve: SKILL.md "ALTIN KURAL — UDF ELLE YAZILMAZ"
> (UDF yalnız `udf-cli html2udf` ile üretilir; elle zip/`content.xml`
> YASAK; `--yerel-motor` EMEKLİ, HATA verir) ve "TESLİM tanımı tekildir"
> (yalnız `teslim_paketi.py` exit 0 + `_oa/defter/teslim-makbuz.json`).

## 0. Neyi çözer, neyi çözmez

`udf_yaz.py` tek gerçek yazıcı olarak `npx -y udf-cli@latest html2udf`
çağırır; bu adım **ağ + oturum** (`udf-cli login`) ister. Servis düştüğünde
(npm kaydı erişilemez, udf-cli sunucusu yanıt vermiyor, oturum açılamıyor,
paket yeni sürümde kırık) script **FAIL-CLOSED** çıkar: hiçbir `.udf`
yazılmaz, exit != 0, stderr'de talimat. Bu plan, o anda **teslimin
durmaması** için hangi yolların meşru olduğunu sıralar. Çözmediği şey:
UYAP'a **UDF** olarak yükleme — bu yalnız servis dönünce ya da UYAP
editörüyle olur; plan bunu **gizlemez**, makbuza yazdırır.

Kesinti teşhisi (bir dakika): `npx -y udf-cli@latest whoami` → (a) komut
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

## 4. Pin kararı — seçenekler (AVUKAT KARARI; bu belge karar VERMEZ)

Hat bugün **`udf-cli@latest`** sabitine bağlıdır (`udf_yaz.py` — `whoami`,
`html2udf`, `udf2md` çağrılarında). "latest" her koşuda kayıttaki en yeni
sürümü çeker: **artı** — UYAP biçim değişikliklerini üretici tarafında
otomatik alır; **eksi** — kırık bir yayın hattı aynı gün durdurur, dün
çalışan komut bugün çalışmaz (yeniden üretilebilirlik yok). Seçenekler:

| Seçenek | Ne yapar | Bedel | Gerektirdiği |
|---|---|---|---|
| (a) `@latest` sürsün | mevcut davranış | kırık yayın = kesinti (bu plan) | hiçbir şey |
| (b) bilinen-iyi sürüme pin | `udf-cli@<sürüm>` sabiti; her koşu aynı üretici | UYAP tarafı değişince eski sürüm sessizce uyumsuz kalabilir; sürüm yükseltme bilinçli iş olur | `udf_yaz.py`'de sürüm sabiti + günlükte kayıt (kod değişikliği — ayrı paket) |
| (c) pin + `@latest` yedek | önce pinli sürüm, hata verirse latest denenir (ya da tersi) | iki sürüm evreni; hangi sürümle üretildiği makbuza yazılmalı | kod değişikliği + `udf-uretim-makbuz.jsonl`'a sürüm alanı |
| (d) yerel önbellek | `npx` yerine önceden kurulu global `udf-cli` (`--npx` ile komut yolu verilir) — npm kaydı erişilemese de paket eldedir; **sunucu/oturum** kesintisini ÇÖZMEZ | önbellek bayatlar; sürüm yine bilinçli yönetilmeli | kurulum adımı, kod değişikliği yok |

Karar ölçütleri (avukat): kesinti sıklığı ve süresi, UYAP biçim değişim
hızı, her üretimin aynı sürümle tekrarlanabilir olmasının ne kadar
istendiği. Hangi sürümün "bilinen-iyi" olduğu **bu belgede yazılmaz** —
sayı, o günkü gerçek üretim makbuzundan (`_oa/defter/udf-uretim-makbuz.jsonl`)
okunur; uydurma sürüm numarası yazılmaz (m.4).

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
   yeniden; pin kararı (§4) için gözlemi `_oa/dersler`'e yaz.

## 6. Yapılmayanlar (dürüst sınır)

- Elle UDF üretimi HİÇBİR koşulda önerilmez (ALTIN KURAL).
- Bu belge `udf_yaz.py`'ye pin/yedek sürüm eklemez — kod değişikliği yok
  (B-6 kapsamı: plan); (b)/(c) seçilirse ayrı paket.
- UYAP editör adımları avukatın deneyimine bırakılmıştır; menü adları UYAP
  sürümüne göre değişebilir — burada yazılanlar yol tarifi, ekran kaydı
  değildir.

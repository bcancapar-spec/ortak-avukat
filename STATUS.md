# DURUM — Ortak Avukat

**Tarih:** 2026-07-29 · **Sürüm:** 0.5.5.5 · **Commit:** `a1b9d18` · **Etiket:** `v0.5.5.5`

Bu dosya deponun **o anki gerçek** durumunu tutar: neyin ölçüldüğü, neyin
açık kaldığı, sıradaki sürümün neden değiştiği. Beyan değil **ölçüm** yazılır;
bir satır ölçülmeden buraya girmez.

---

## 1. Yeşil olanlar (ölçüldü)

| Ne | Değer | Nasıl doğrulanır |
|---|---|---|
| Test | **808 toplandı · 806 yeşil · 2 atlandı** | `python -m pytest tests -q` |
| Test — avukatın ortamı | aynı sonuç (**cp1254**, `PYTHONUTF8` ayarsız) | `unset PYTHONUTF8` ile aynı komut |
| Aile yapı denetimi | **temiz**, 20 parça | `python plugins/ortak-avukat/skills/oa-usta/scripts/aile_dogrula.py plugins/ortak-avukat/skills` |
| Sürüm damgaları | dört damga eşzamanlı (`0.5.5.5`) | `test_hooks_wiring.py` |
| Yerel ↔ uzak | eşit, bekleyen commit 0 | `git status -sb` |

**İki ortamda da koşuluyor artık.** Bu satır v0.5.5.5'in tek sebebidir —
aşağıya bakınız.

---

## 2. Bugün kapatılanlar

| Sürüm | Ne | Neden |
|---|---|---|
| `v0.5.5` | Aktivasyon: advisory kapı → atlanamaz zincir | v0.5.4 sahada kapıları ateşleyememişti |
| `v0.5.5.1` | Saha tetikleri + UDF hattı kilidi | mekanizmalar sağlamdı, **çağrılmıyorlardı** |
| `v0.5.5.2` | UDF geçerlilik kapısı: iki yanlış-BLOK + resmî okuyucu tanığı | kapı, koruduğu teslimi kesiyordu |
| `v0.5.5.3` | Bağımsız içerik hakemi + sicil desenleri + içtihat bağlantıları | dilekçe kendi bölümüyle aritmetik çelişiyordu |
| `v0.5.5.4` | GitHub açılış sayfası aile tanıtımı (yalnız anlatım) | 20 parçanın hiçbiri açılış sayfasında görünmüyordu |
| `v0.5.5.5` | **P0 — teslim hattı avukatın kendi ortamında çöküyordu** | aşağıda |

---

## 3. Açık bulgular (v0.5.6 hazırlık analizinden)

Sıra, **müvekkile dokunma** ihtimaline göre.

### A1 · `.xlsx` bilirkişi raporu sessizce kayboluyor — YÜKSEK
`manifest_olustur.py` `.doc/.xls/.xlsx/.odt/.heic` uzantılarını "ofis belgesi —
metin" diye sınıflar; `oa_ingest.py` bunları **işleyemez**. Sonuç: bir bilirkişi
hesap tablosu manifestte okunabilir görünüp ingest'te "desteklenmeyen tür"
oluyor. Uzantı kümesi üç dosyada yaşıyor ve **ikisi zaten ayrışmış**.
→ Tek kaynağa indir, fark `INGEST_OKUYAMAZ` diye **adlandırılsın** (sessiz değil).

### A2 · Test dağılımı ters — YÜKSEK
Sahada fiilen koşan altı motorun **kendi mantığı sınanmıyor**: `usul_matris`,
`vakia_matris`, `kiyas_denetim`, `sozlesme_denetim`, `grafik_denetim` hiçbir
testte anılmıyor; `antitez_matris` yalnız **bir** testte geçiyor, o da motoru
değil `teslim_paketi`'nin elle yazılmış matris dosyasını *tüketmesini* sınıyor.
Yani `--iskelet`/`--dogrula` yolları, sekiz cephe kümesi ve kapalı enum'lar
doğrulanmamış. Buna karşılık sahada hiç koşmayan defter **24 test dosyalı**.
Test yazdık ama işin yapıldığı yere değil, kodun yazıldığı yere yazdık.

### A3 · Resmî okuyucu bacağının kendisi testsiz — ORTA
`npx_ile_udf_oku` gerçek hâliyle hiçbir testte koşmuyor; tüm testler sahte
okuyucu enjekte ediyor. Yani UDF kapısının **tek dış tanığı** doğrulanmamış.

### A4 · ~~Delilsiz-unsur uyarısı testsiz~~ → **YANLIŞ TEŞHİS, DÜZELTİLDİ** — DÜŞÜK
İlk analiz "tek testi fonksiyonun adının kaynakta geçtiğini doğruluyor" demişti.
**Yanlış.** `tests/test_durum_md.py:319` gerçek bir `04-vakia.json` yazıp gerçek
CLI'yı koşturuyor ve `DURUM.md`'de uyarının 🔴 ile göründüğünü doğruluyor;
negatif vakası da var. Hata bendeydi: fonksiyon *adını* gremiştim, ürettiği
*çıktı dizesini* değil.

Geriye **daha dar** bir boşluk kalıyor: test, `04-vakia.json`'u **elle yazıyor**
— `vakia_matris.py` üretmiyor. Yani üretici şeması kayarsa tüketici testi yine
yeşil kalır. Kilitlenmesi gereken şey uyarı değil, **üretici-tüketici
sözleşmesi**.

### ÇALIŞAN SÜRÜM TABANI (2026-07-29 ölçümü — kod yok, yalnız kayıt)
Sistem bugün **bu sürümlerle** yeşil: `udf-cli` **0.4.3** · Python **3.14.6** ·
`pymupdf` **1.28.0** · `pillow` **12.3.0** · `pytest` **9.1.1** · Node **v26.4.0** ·
ortam kodlaması **cp1254** (PYTHONUTF8 ayarsız).

Bu satırın tek işi şu: yarın bir şey bozulduğunda "önceden ne çalışıyordu"
sorusunun cevabı olsun. **Sabitleme değildir** — sabitleme UYAP biçim
değiştirdiğinde bizi eski sürümde çakılı bırakır. Karar: pinleme **ertelendi**,
gerçek bir kırılma görülene kadar aksiyon alınmayacak (kullanıcı kararı,
2026-07-29). Bozulma olursa ilk bakılacak yer bu satırdır.

### A5 · `udf-cli@latest` 33 yerde pinsiz — ORTA (ERTELENDİ)
Teslim hattının tek yazıcısı ve tek doğrulayıcısı sürüm kilidi olmadan
çağrılıyor. Pinlemek de bedelli: UYAP biçim değişirse pinli sürüm sessizce
bayatlar. Karar gerektirir.

---

## 4. v0.5.6 — plan neden değişti

**Eski manda:** *"ateşlemeyen kapıyı sil, zırhı geri al; oran küçülmeli."*

Analiz bu mandayı **ampirik olarak çürüttü**:

- **Silinecek kütle yok.** 16.347 satır üretim kodunda ~8 satır ölü sembol var.
- **Zırh sandığımız şey dürüst kullanımda ateş ediyor.** 24 silme önerisinin
  24'ü çürütmede düştü; gerekçeler deneysel — ajanlar kodu silip koşturdu.
  `DAMGA=` normalizasyonu kaldırılınca sıradan bir avukat girdisiyle canlı
  fail-open üretti; `--dokum` satır-sonu kapısı "Windows'ta imkânsız" denen
  senaryoda bu makinede ateş etti; ZWSP katmanı `ictihat_getir` yanıtındaki
  **her markdown başlığında** ateşliyor.
- **Oran zaten sabit.** 5,26× → **5,41×**. Büyümedi, ama küçülmedi de.

**Yeni eksen: SADELEŞTİRME değil HİZALAMA.** Test ve denetim, işin *yapıldığı*
yere taşınır. Somut kapsam: A1 (evrak kaybı) · A2 (test dağılımı) · A3/A4
(sahte yeşil testler) · M8/M9 önkoşulları.

---

## 5. M8 / M9 önkoşulları — şu an **üretilmeyen** veri

Anatomi katmanı (kurgu kilitli) bu üç alan olmadan kurulamaz:

| Eksik | Nerede olmalı | Sonuç |
|---|---|---|
| **Karar tarihi** ayrıştırılmıyor | `kunye_ortak.py` (ESAS/KARAR/MERCİ/DAİRE var, TARİH yok) | M8'in zorunlu "örneklem beyanı → dönem" alanı kurulamaz |
| **Sayfa/satır izi** yok | `oa_ingest` UDF/DOCX/düz-metin hattı sayfa ayracı üretmiyor | M9 konkordansının `sayfa` sütunu boş kalır |
| **Taraf ve sonuç sınıfı** kalıcı değil | yalnız CLI argümanı + teslim makbuzu | M8'in taraf-bilinçli anatomisi dayanaksız kalır |

Ayrıca iki tasarım tuzağı ölçüldü: `_oa/arastirma/` dizini şu anda **sözleşme
dışıdır** (açılınca gölge-hat uyarısı üretir), ve `maruziyet.md` `_oa/cikti`
altına konursa `dosya-analiz.md`'ye **tam gömülür** — yani iç istihbarat
dilekçe yazıcısının bağlamına sızar.

---

### A6 · `maruziyet.md` gömülme tuzağı — plana bağlanmamıştı
`_oa/cikti` altındaki **her** dosya `dosya-analiz.md`'ye tam gömülür. `maruziyet.md`
(iç istihbarat: zayıf unsurlarımız) oraya konursa dilekçe yazıcısının bağlamına
**sızar** — anayasa m.6'nın anatomi düzlemindeki ihlali. §5'te ölçülmüştü ama
hiçbir iş kalemine bağlanmamıştı. Konum kararı M8'den **önce** verilmeli.

### A7 · Şema göçü riski — M8 örneklemini çarpıtır
Yeni alanlar (karar tarihi, paragraf izi, taraf/sonuç sınıfı) künye şemasını
değiştirir. Mevcut `_oa` klasörleri (441 ve 320 evraklık olanlar dâhil) eski
şemada kalır. M8 geldiğinde eski-yeni karışık külliyat **sessizce çarpık
örneklem** üretir. Şema sürümü + göç kararı, alan eklemeden önce verilmeli.

---

## 5b. Üç jüri hükmü (Fable 5, bağımsız, max efor)

**0 ONAY · 3 ŞARTLI-ONAY · 0 RET.** Üçü de eksen değişikliğini (sadeleştirme →
hizalama) ölçümle haklı buldu, üçü de **aynı itirazda** buluştu:

> Plan **içe dönük**. Elde dört bakir gerçek UYAP klasörü (idari, istinaf,
> aile, icra) dururken ağırlık sentetik test yazımına gidiyor. Oysa bu deponun
> **en ağır kusurlarının hiçbirini test bulmadı — hepsini saha buldu**:
> encoding çöküşü, elle yazılan defter, açılmayan UDF, geçerliyi kesen kapı.

Ortak şartlar: ölçüm ortamı sözleşmesi **mekanikleşsin** (CI'da `PYTHONUTF8`
unset ikinci koşu) · motor testleri **davranışsal** olsun ve en az bir **kırmızı
yol** içersin · her yeni teste "hangi saha arızasını yakalar" gerekçesi zorunlu,
gerekçesi yazılamayan test **yazılmaz** · motor başına en fazla ~150 satır bütçe
tavanı · `udf-cli`'nin gerçek sürümü teslim makbuzuna damgalansın.

**Jüri-3'ün açık uyarısı:** plan, şartlarla bile oranı ~5,41 → ~5,55'e
**büyütür**. "Oran küçülmeli" ölçütü ya açıkça yeniden onaylanmalı ya emekliye
ayrılmalı — **sessizce çiğnenmemeli**. (Bkz. §8/1.)

---

## 6. Bugünün asıl dersi

**Hata kodda değil, ölçüm ortamındaydı.**

Teslim hattı, avukatın kendi Windows ortamında (`PYTHONUTF8` ayarsız, cp1254)
çöküyordu: `subprocess.run(..., text=True)` çağrılarına `encoding=`
verilmediği için `udf-cli` çıktısı yerel kod sayfasıyla çözülüyor ve ilk
çok-baytlı karakterde `UnicodeDecodeError` fırlatıyordu. Sonuç sessiz bir hata
değil **teslim engeliydi**: geçerli bir dilekçe "GEÇERSİZ" ilan ediliyordu.

Görülmemesinin sebebi: geliştirme koşularının tamamı `PYTHONUTF8=1` ile
yapılmıştı ve o bayrak kusuru maskeliyordu. *"801 test yeşil"* beyanı **doğru
ama yanıltıcıydı** — sistemin fiilen çalıştığı ortam hiç sınanmamış, hep
düzeltilmiş bir ortam sınanmıştı.

Bu, günün tüm saha bulgularıyla aynı sınıftandır: **kapı yeşil görünüyordu,
değildi.** Defter elle yazılmıştı, UDF "üretildi" ama açılmıyordu, geçerlilik
kapısı geçerli dilekçeyi kesiyordu. Ortak kök: *doğru soruyu yanlış yerde
sormak.*

---

## 7. Ölçüm

| Katman | Satır |
|---|---|
| Doktrin (SKILL.md + references + README'ler) | 5.925 |
| Üretim kodu (`skills/*/scripts/*.py`) | 16.347 |
| Test | 15.736 |
| **Oran (kod+test)/doktrin** | **5,41×** (28 Tem tabanı: 5,26×) |

En büyük üç script tek başına 6.128 satır: `pipeline_kayit.py` (2.977),
`oa_hafiza.py` (1.581), `tam_tur.py` (1.570).

> **Ölçüm şerhi:** oran, paydanın tanımına duyarlıdır. Yalnız `SKILL.md` +
> `references` sayılırsa 7,16× çıkar. Yukarıdaki 5,41×, 28 Temmuz tabanıyla
> **karşılaştırılabilir** geniş tanımı kullanır (tüm `plugins/**/*.md`).
> İki sayıyı karıştırmak, oranın büyüdüğü yanılgısını üretir.

---

## 8. Karar bekleyen

1. **"Oran küçülmeli" ölçütü — geçerli mi?** Üç jüriden ikisi bunu doğrudan
   sordu. Plan, en dar hâliyle bile oranı büyütür. Üç seçenek: (a) ölçüt aynen
   geçerli → v0.5.6 yalnız A1+A5+önkoşullar olur, motor doğrulaması repo testi
   yerine **bakir klasörde saha koşusu** ile yapılır (net ~sıfır büyüme);
   (b) ölçüt "zırh/tören şişmesi" olarak yeniden tanımlanır; (c) emekliye ayrılır.
   **Sessizce çiğnenmeyecek** — karar buraya yazılacak.
2. **Ağırlık nereye?** Jürinin ortak itirazı: dört bakir klasör dururken
   sentetik test yazmak. v0.5.6 sahaya mı dönsün (playbook hazır), repoda mı
   kalsın?
3. **`udf-cli` pinlensin mi?** (A5 — iki yönlü bedel; hangi yönde olursa olsun
   gerçek sürüm teslim makbuzuna damgalanacak)
4. **`_oa/arastirma/` meşrulaştırılsın mı**, yoksa anatomi mevcut dizinlere mi
   yazsın? (gölge-hat bekçisini zayıflatmadan) — **ve `maruziyet.md` nereye?** (A6)

---

## 10. Saha test protokolü

`SAHA-PB v1.0` yazıldı: **depo dışında**, `uyap-evraklar/_saha/SAHA-PB.md`
(gerçek klasör adları taşıdığı için GitHub'a girmez). Özü: bir kapı ancak
avukatın **kendi ortamında**, gerçek dosyada, koşu penceresi içinde zaman
damgalı bir **eser** bırakmış ve o eser aşağı akışta **tüketilmişse**
ateşlemiştir; gerisi beyandır.

Bugünkü dersi yapısal olarak kapatan kural: koşu, ortam parmak izi almadan
başlamaz; `PYTHONUTF8` tanımlıysa koşu **başarısız değil HÜKÜMSÜZ** sayılır —
hiçbir çıktısı kanıt olamaz. Ayrıca koşu-içi onarım yasak (çökme bulgudur),
ölçümü avukat **ayrı terminalde** yapar (sistem kendi karnesini yazamaz), ve
başarı ölçütü koşu başlamadan yazılıp kilitlenir.

İlk adım **KOŞU-0**: kullanılmış bir klasörde ölçüm aygıtının provası — bakir
maliyeti sıfır. Gerekçe bugünün dersinin ta kendisi: doğrulanmamış ölçüm aygıtı
kıt bakir örneğe doğrultulmaz.

---

## 9. Nasıl doğrulanır

```bash
python -m pytest tests -q
```

```bash
python plugins/ortak-avukat/skills/oa-usta/scripts/aile_dogrula.py plugins/ortak-avukat/skills
```

Avukatın gerçek ortamını sınamak için `PYTHONUTF8` **ayarlanmadan** koşulmalıdır
— aksi hâlde platforma özgü kusurlar maskelenir.

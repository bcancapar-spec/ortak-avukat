# STATUS — Oturum Kaydı · TTK · Müdürün Ortaklara Karşı Yetkileri / Baskı Araçları

**Oturum:** 2026-09-07 · **Dal:** `claude/ticaret-kanunu-mudur-hakları-0wy547`
**Karar verici:** Av. Bayram Can Çapar (Denizli Barosu · Sicil 1807)
**Kayıt disiplini:** anlık + atomik · her faz sonunda bu dosya güncellenir.

---

## 0. Soru (ham hâliyle)

> "Şirket müdürünün şirket ortaklarına karşı ticaret kanunu gereğince
> yapabileceği zorlamalar, baskı unsurları ve yönetsel haklar neler olabilir?"

## 1. Sorunun hukuken yeniden çerçevelenmesi (ön muhakeme)

Soru üç ayrı hukuki kategoriyi tek torbada topluyor. Muhakemenin ilk işi bu
torbayı ayırmaktır; ayrılmazsa çıktı "müdür şunları yapabilir" listesine döner
ve **yetki ile fiilî güç** birbirine karışır. Ayrım:

| # | Kategori | Hukuki niteliği | Denetim ölçütü |
|---|---|---|---|
| A | **Yönetsel haklar** | TTK'nın müdüre TANIDIĞI yetki | Yetki var mı? (m. 623 vd.) |
| B | **Meşru zorlama araçları** | Kanunun/şirket sözleşmesinin ortağa YÜKLEDİĞİ borcu müdürün icra etmesi | Borç kaynağı ve usul doğru mu? |
| C | **Baskı unsurları** | Yetkinin AMACI DIŞINDA kullanılması | Eşit işlem (m. 627), dürüstlük (TMK 2), hakkın kötüye kullanılması |

**Kritik illiyet tespiti (hipotez — normla teyide tabi):** Müdürün ortağa karşı
kullandığı "gücün" büyük kısmı müdürlük sıfatından değil, **genel kurul
çoğunluğundan** doğar. Müdür sıfatı tek başına ince bir yetkidir; asıl kaldıraç
müdürün aynı zamanda hâkim ortak olmasıdır. Bu ayrım yapılmazsa hem teşhis hem
savunma yanlış kurulur.

## 2. Yöntem

1. Norm teyidi: TTK (6102) madde madde `mevzuat_getir` ile resmî metin.
2. İçtihat: Yargıtay 11. HD + HGK; `ictihat_ara` / `semantik_ictihat_ara`;
   künye + `source_url` zorunlu; teyit edilmeyen künye yazılmaz.
3. Muhakeme: her araç için **yetki kaynağı → sınır → karşı hak (panzehir)**
   üçlüsü; ortağın kalkanı ayrı bölümde.
4. Çıktı: `MUTALAA-TTK-MUDUR-ORTAK.md` (ana mütalaa) + `kaynak-kutugu.md`.

## 3. İlerleme kütüğü

- [x] Depo ve metodoloji incelendi (oa-ictihat künye disiplini benimsendi).
- [x] Kullanıcı profili alındı (Yargı PRO).
- [x] TTK mevzuat kimliği doğrulandı: `mevzuatgov:kanun:5:6102` (RG 14.02.2011).
- [x] Faz-1: Norm teyidi (limited şirket ekseni) — TAMAM. Teyit edilen maddeler:
      573, 591, 592, 594, 595, 596, 601, 602, 603-607, 608, 610, 611, 613, 614,
      615(mülga), 616, 617, 618, 619, 620, 621, 622, 623, 625, 626, 627, 629,
      630, 631, 633, 635, 636, 638, 640, 641, 642, 644.
- [x] Faz-2: AŞ atıfları — TAMAM: 128, 129, 358, 371, 376, 391, 392, 395, 410,
      411, 412, 437, 438, 439, 445, 446, 447, 481, 482, 483, 493, 519, 531,
      553, 555 + TMK m.2, TCK m.155, m.239.
- [x] Faz-3: İçtihat taraması TAMAM (6 tam metin + 15 snippet teyidi; kütük ayrı dosyada).
- [x] Faz-4: Mütalaanın yazımı TAMAM (`MUTALAA-TTK-MUDUR-ORTAK.md` + `kaynak-kutugu.md`).
- [x] Faz-5: Commit + push + taslak PR.

## 4. Açık riskler / dürüst sınırlar

- Soru "şirket müdürü" diyor: **limited şirket** (ortak + müdür terminolojisi)
  esas alınacak; anonim şirkette "müdür" unvanı taşıyan kişi yönetim kurulu
  üyesi/atanmış müdür olabilir → AŞ karşılığı ayrı bölümde işlenecek.
- Somut dosya verisi yok; çıktı **soyut mütalaa** olacaktır, dosyaya uyarlama
  avukatın kararına bırakılır.

---

## 5. Faz-1 muhakeme çıktısı — norm teyidinden doğan KRİTİK bulgular

**B-1 (yapısal):** TTK m. 623/3 ve m. 625/1 müdüre *yönetim* yetkisi verir;
ortağın **kişisel/ortaklık haklarına** doğrudan müdahale yetkisi vermez. Ortağın
statüsüne dokunan her karar (çıkarma, pay devrine onay, kâr payı, ek ödeme
öngörme, sözleşme değişikliği) **genel kurulun devredilemez yetkisindedir**
(m. 616/1). ⇒ *Müdürün "zorlama gücü" hukuken değil, çoğunluk hâkimiyeti
üzerinden fiilen kurulur.* Mütalaanın omurgası budur.

**B-2 (ek ödeme):** m. 603/5 — "Şartlar gerçekleşmişse, ek ödemeler **müdürler
tarafından** istenir." Bu, kanunun müdüre verdiği **doğrudan ve gerçek** para
talep etme yetkisidir; ama üç kilidi vardır: (i) şirket sözleşmesinde
öngörülmüş olmalı, (ii) m. 603/1'deki üç şarttan biri gerçekleşmeli,
(iii) tavan = itibarî değerin **iki katı** (m. 603/3). Sözleşmede yoksa
sonradan getirilmesi **ilgili tüm ortakların onayına** bağlıdır (m. 607).
⇒ En sık görülen baskı senaryosu: şartlar yokken "zarar var, ek ödeme yatır"
çağrısı. Bu çağrı **yok hükmünde değil ama dayanaksızdır**; ortak ödemez,
müdürün icrası m. 603/1'i ispata bağlıdır.

**B-3 (ıskat yok):** `mevzuat_icinde_ara("ıskat")` → 6102'de "ıskat" yalnız
**m. 483 (AŞ)** ve m. 519'da geçiyor. m. 644'ün atıf listesinde 481-483 **YOK**.
⇒ **Limited şirkette ortağın payının ıskatı (paydan yoksun bırakma) yoktur.**
Sermaye borcunu ödemeyen ortağa karşı müdürün elindeki araç: m. 128/7 (eda
davası + tazminat) ve m. 129 (temerrüt faizi) — pay iptali değil. "Sermayeni
yatırmazsan payını iptal ederim" tehdidi **hukuken boştur**. (AŞ'de tersi:
m. 481-483 ile yönetim kuruluna gerçek ıskat yetkisi verilmiştir — iki tip
arasındaki en keskin fark.)

**B-4 (bilgi kesme):** m. 614/2 müdüre bilgi/incelemeyi **engelleme** yetkisi
verir — fakat yalnız "ortağın bilgiyi şirket zararına kullanma **tehlikesi**"
varsa ve **gerekli ölçüde**. Karar mercii müdür değil, itiraz üzerine **genel
kurul**; genel kurul da haksız engellerse **mahkeme** (m. 614/3, karar kesin).
⇒ Pratikte en çok kötüye kullanılan kaldıraç; ama üç kademeli kilit var ve
ortağın m. 594/2 pay defteri inceleme hakkı **koşulsuzdur**.

**B-5 (pay devri kilidi):** m. 595/2-3 — devre onay **genel kurulun**, üstelik
sözleşmede aksi yoksa **sebep göstermeksizin** reddedilebilir; sözleşme devri
tamamen **yasaklayabilir** (m. 595/4). ⇒ Ortağı şirkette "kilitleme" gücü
buradadır ve bu güç müdürün değil çoğunluğundur. Panzehir: m. 595/5 haklı
sebeple çıkma + 3 aylık **zımnî onay** süresi (m. 595/7).

**B-6 (çıkarma):** m. 640 — çıkarma ya *sözleşmede yazılı sebeple genel kurul
kararıyla* (ortağa 3 ay iptal davası hakkı) ya da *haklı sebeple mahkeme
kararıyla* olur; her ikisinde de karar/dava mercii müdür değildir (m. 616/1-h,
621/1-h; nisap: 2/3 + salt çoğunluk). ⇒ "Seni ortaklıktan atarım" tehdidi tek
başına müdürün elinde olan bir yetki değildir.

**B-7 (asimetri):** m. 630/1 genel kurul müdürü **her zaman** görevden alabilir;
m. 630/2 **her ortak** haklı sebeple mahkemeden müdürün yetkisinin
kaldırılmasını isteyebilir (azınlık ortağın en güçlü tek silahı — çoğunluk
gerekmez). Buna karşılık müdürün ortağı "azletme" yetkisi yoktur.
⇒ Yetki asimetrisi **ortak lehinedir**; fiilî güç asimetrisi ise müdür lehine
işler. Muhakemede bu ikisi ayrılmazsa teşhis yanlış olur.

---

## 6. Faz-3 muhakeme çıktısı — içtihattan doğan KRİTİK bulgular

**İ-1 — EN GÜÇLÜ PANZEHİR (yokluk).** Yargıtay 11. HD, E.2024/6094 K.2025/4433
(23.06.2025): şirket sözleşmesinde ek ödeme yükümlülüğü yoksa ya da mevcut
yükümlülük artırılıyorsa, ek ödeme öngören genel kurul kararı **oybirliği**
şartını (TTK m. 607) taşımadığı için **YOK HÜKMÜNDEDİR** — butlan değil,
yokluk. Sonuçları: süreye tabi değil, muhalefet şerhi dava şartı değil,
mahkemece **resen** gözetilir, hakkın kötüye kullanılması sınırına dahi tabi
değildir. ⇒ "Ek ödeme yatır" baskısının en sert kırılma noktası.
Destek: Y11HD E.2018/4878 K.2019/6438 (zararın ortaklarca karşılanması kararı
→ **butlan**, 3 aylık süreye tabi değil).

**İ-2 — Kâr payı müdüre karşı dava edilemez.** Y11HD E.2022/4059 K.2024/152
(10.01.2024, onama): kâr dağıtımında münhasır yetkili organ genel kuruldur;
karar yoksa mahkeme kâr payına hükmedemez; **müdüre karşı kâr payı davası
açılamaz.** ⇒ Ortağın hattı: 617/3→411/412 ile gündeme "kâr dağıtımı"
koydurmak, sonra 622→445 iptal davası. Doğrudan tahsil davası hattı ölüdür.

**İ-3 — Çıkarma müdürün elinde değil; %51 de yetmez.** Aynı karar + Y11HD
E.2021/3956 K.2022/7571: ortağın çıkarılması davasını **şirket** açar
(aktif husumet), üstelik TTK m. 616/1-h + 621/1-h **çifte nisap** (temsil
edilen oyların 2/3'ü + oy hakkı bulunan sermayenin tamamının salt çoğunluğu)
gerekir. İst. BAM 43. HD E.2021/1491 K.2024/259: %51 ile alınan çıkarma kararı
nisabı sağlamaz → dava şartı yokluğu. ⇒ "Seni ortaklıktan atarım" tehdidi,
çoğunluk ortak-müdürün elinde bile çoğu zaman **blöftür**.

**İ-4 — Ortağın sorumluluk davası için genel kurul kararı GEREKMEZ.** Y11HD
E.2021/3956 K.2022/7571 açıkça: "ortağın açtığı sorumluluk davasında genel
kurul kararı alınması yönündeki ilk derece mahkemesi kararı doğru değildir."
(TTK m. 644/1-a → 553, 555: tazminat **şirkete** ödenir.) ⇒ Azınlık ortağın
çoğunluğa ihtiyaç duymadan işletebileceği ikinci silah (birincisi m. 630/2).

**İ-5 — Bilgi hattında usul kilidi çift yönlü.** Y11HD E.2016/8554 K.2018/1956:
m. 614 davasından önce **genel kurula başvuru özel dava şartıdır** (müdürün
lehine gecikme kaldıracı). Ama Y11HD E.2018/833 K.2018/1722 (kanun yararına
bozma): m. 437 limited şirkete uygulanmaz (m. 644'te atıf yok) ve m. 614 davası
için **süre öngörülmemiştir** (437/5'teki 10 gün geçerli değil). ⇒ Müdür
zaman kazanır ama hakkı süreyle öldüremez.

**İ-6 — Rekabet ihlali tek başına azil sebebi.** Y11HD E.2021/3956 K.2022/7571:
müdürün aynı konuda rakip şirket kurup orada da müdürlük yapması **tek başına**
m. 630/2 haklı sebebidir. ⇒ Baskı kuran müdürün en sık düştüğü tuzak.

**İ-7 — ANTİTEZ (aleyhe damga).** (a) Y11HD E.2024/4040 K.2025/2386
(14.04.2025): huzur hakkı ödemesinin örtülü kâr dağıtımı sayılması **otomatik
değildir**; ciro, iş hacmi, emek/mesai ölçütleriyle bilirkişi incelemesine
bağlıdır — orantılıysa iptal istemi reddedilir. (b) İst. 6. ATM E.2017/491
K.2021/427: ortak m. 617/3→411/412 yolunu **kullanmamışsa**, genel kurulun
toplanmamış olması tek başına azil için haklı sebep sayılmayabilir.
⇒ Ortağın "önce kendi usulî adımını atma" yükü vardır; atmadan dava açmak
davayı öldürür.

**İ-8 — Çoğunluk ortağın azlık yolu yoktur.** Ankara BAM 21. HD E.2022/409
K.2023/231: genel kurulu çağırma yetkisi münhasıran müdürdedir; %90 ortak
TTK m. 411 azlık çağrı hakkından **yararlanamaz** (Ankara 8. ATM 2020/180 E.).
Yol: m. 617/3 → 410/2 (müdürler kurulu toplanamıyorsa mahkeme izniyle tek
ortak çağırır). ⇒ Müdür, kendisini azledecek çoğunluğu bile bir süre genel
kurulsuz bırakabilir; fakat BAM bunu müdürün **ağır kusuru** saymıştır.

**İ-9 — Dürüstlük hattı.** İst. 14. ATM E.2023/835 K.2025/818: kâr
dağıtmazken hâkim ortağın müdür sıfatıyla huzur hakkı + prim alması ve
kârın tamamının yedeğe ayrılmasıyla çıkma payının fiilen çıkan ortağa
ödettirilmesi dürüstlük kuralına aykırı bulunmuştur; ayrıca gerekçe
**karar anındaki** gerekçeyle sınırlıdır, sonradan üretilen gerekçe
kararı haklı kılmaz.

## 7. Dürüstlük notu (kayıt disiplini)

- `1114669300` (İst. Anadolu 5. ATM E.2025/90 K.2025/81) tam metni çekildi:
  **esas hakkında hüküm değil, tefrik/gönderme kararıdır.** İçindeki zengin
  "baskı unsuru" listesi **dava dilekçesi iddiasıdır**, mahkeme tespiti
  değildir. Mütalaada yalnız "saha kalıbı örneği" olarak, bu kayıtla
  kullanılacaktır. Hüküm gibi sunulmayacaktır.
- Snippet ile teyit edilen kararlar kütükte ayrıca işaretlenmiştir.

---

## 8. ÖLÇÜM (beyan değil)

**Yargı PRO çağrı sayımı:** 1 profil + 1 mevzuat arama + 1 mevzuat-içi arama
(`ıskat` → 2 isabet) + **50 madde çekimi** + 6 içtihat arama + 5 semantik arama
+ 9 tam metin içtihat çekimi. Bir çağrı bağlantı hatasıyla düştü (m. 622),
**yeniden denendi ve alındı** — teyitsiz madde bırakılmadı.

**Depo süiti (bu konteynerde):**
`python3 -m pytest tests -q --ignore=tests/test_tam_tur*.py`
→ **20 fail / 2229 pass / 24 skip / 2 error** (171 sn).
Aynı komut **bu oturumun dosyaları geçici olarak dizinden çıkarılarak**
tekrar koşuldu → **birebir aynı sayı** (20/2229/24/2, 168 sn).
⇒ **Bu oturumun katkısı regresyon üretmiyor.**

**Dürüst sınır — süit neden tam yeşil değil:** Konteynerde **Python 3.11.15**
var; depo CI matrisi **3.12 / 3.13** koşuyor (`.github/workflows/ci.yml`).
`plugins/.../oa-pipeline/scripts/tam_tur.py:1407` PEP 701 (f-string içinde
ters bölü) kullanıyor; 3.11'de **SyntaxError** verdiği için 3 test dosyası
toplanamıyor, bunları dışlamak da süit-sayısı işaretçisi testini düşürüyor.
Kalan düşükler de aynı sürüm farkının türevidir ve **bu oturumdan önce de
aynen mevcuttur** (yukarıdaki kontrollü karşılaştırma). Depo kodu bu oturumda
**hiç değiştirilmemiştir**; katkı yalnız `_gorus/` altında üç `.md` dosyasıdır.

## 9. Teslim

| Dosya | İçerik |
|---|---|
| `MUTALAA-TTK-MUDUR-ORTAK.md` | Ana mütalaa (10 bölüm: kategori ayrımı, yönetsel haklar, meşru zorlama matrisi, blöf listesi, 13 saha kalıbı, ortağın savunma protokolü, AŞ karşılaştırması, müdürün risk haritası, illiyet şeması, sonuç) |
| `kaynak-kutugu.md` | 50 madde + 43 içtihat künyesi, `source_url`'li; teyit dereceleri (TAM/SNIPPET/KÜNYE/ATIF); aşılmışlık taraması; teyit edilemeyenler |
| `status.md` | Bu oturum kaydı (anlık + atomik) |

---

## 10. Faz-6 (plan dışı) — CI teşhisi ve ayrı düzeltme dalı

PR #2 açıldıktan sonra CI'nın `test (ubuntu-latest / py3.12)` ve `py3.13`
ayakları düştü. Teşhis zinciri:

1. **Düşük bu PR'ın mı?** `git diff --stat origin/main...HEAD` → yalnız 3
   markdown dosyası; `plugin.json` dahil hiçbir koda dokunulmamış.
2. **`main`'de de var mı?** `origin/main` ayrı ve temiz bir worktree'ye
   çıkarıldı, bu oturumun hiçbir dosyası ortada yokken aynı testler koşuldu
   → **3 failed, 17 passed**. Aynı düşükler. ⇒ Düşük `main`'in kendi ucunda.
3. **Kök neden:** `main` ucu `08441f5` ("manifestteki yinelenen hooks
   bildirimini kaldir") `plugin.json`'dan `"hooks": "./hooks/hooks.json"`
   satırını **haklı gerekçeyle** sildi (standart yol zaten otomatik
   yükleniyor; ikinci bildirim `Duplicate hooks file detected` verip 20
   skill'in tamamını düşürüyordu) — ama o satırı **zorunlu** sayan 4 iddiayı
   güncellemedi.
4. **Çarpışan iki saha dersi:** (a) v0.5.6 — kayıt hiç yoksa tetikler ölür;
   (b) 08441f5 — iki kez bildirilirse eklenti hiç yüklenmez. **(a)'nın
   çaresi (b)'nin arızasıdır**; ikisi eski iddia biçimiyle aynı anda
   sağlanamaz.
5. **Mevcut yama var mı?** Depoda başka açık PR yok (PR #1 Temmuz'da
   kapanmış) ⇒ taşınabilecek bir düzeltme yok.

**Yapılanlar:**
- PR #2'ye **tek** gerekçe yorumu bırakıldı (düşen kontroller, neden bu PR'ın
  olmadığı, temiz `main` üzerindeki birebir üretim, önerilen yama).
  Deterministik bir `assert` hatası olduğu için CI dakikası harcayan tekrar
  koşum yapılmadı; gerekçesi yorumda yazılı.
- **Doktrin değişikliği olduğu için karar avukata soruldu** (karar verici:
  Bayram Can ÇAPAR). Onay üzerine ayrı dal açıldı:
  `claude/hook-manifest-tek-kez-degismezi` → **PR #3**.
- Yeni değişmez: **hook katmanı TAM BİR KEZ yüklenebilir olmalıdır** —
  dosya standart yolda durmalı, manifest onu tekrar bildirmemeli.
  Dokunulan: `tools/hook_doktor.py` (üç dallı kontrol),
  `tests/test_hooks_wiring.py`, `tests/test_devir_zorlayici.py`.
- **Sürüm damgalarına dokunulmadı** (0.5.16.1 aynen); kodda uydurma sürüm
  etiketi yazılmadı, yorumlar commit sha'sına atıf yapıyor.

**Ölçüm (yerel, py3.11; py3.12+ isteyen 3 `tam_tur` dosyası hariç):**

| | fail | pass | skip | error |
|---|---|---|---|---|
| önce (`origin/main`) | 20 | 2229 | 24 | 2 |
| sonra (PR #3 dalı) | **16** | **2233** | 24 | 2 |

Tam 4 düzelme, yeni düşük yok. `python tools/hook_doktor.py --servis-atla`
→ exit 0, `SONUÇ: TÜM MEKANİK KONTROLLER GEÇTİ ✓`.

**Muhakeme notu (salt-belge PR neden genişletilmedi):** Düzeltme, deponun
kodlanmış doktrinine dokunuyor; salt-belge bir mütalaa PR'ına iliştirilirse
hem inceleme birimi bulanır hem de doktrin değişikliği bir mütalaa commit'inin
içinde görünmez hâle gelir. Ayrı dal, ayrı PR — inceleme birimi temiz kalır.

**Açık:** PR #2, PR #3 birleşene kadar kırmızı kalacaktır; kırmızının sebebi
bu PR değildir ve PR'da yazılıdır. İki PR de izlemede.

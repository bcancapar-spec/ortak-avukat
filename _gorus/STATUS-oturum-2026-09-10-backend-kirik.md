# OTURUM KAYDI — Backend Sistemsel Kırık/Bug Taraması
**Tarih:** 2026-09-10 · **Dal:** `claude/ortak-avukat-backend-check-qpjdbp` · **Karar verici:** Av. Bayram Can ÇAPAR

## Görev
`ortak-avukat` plugin'inin TÜM skill setinde **backend (Python) katmanında**,
bir avukatın **müvekkili lehine** olan sonucu bozacak **sistemsel kırık ve bug**
var mı? — Tarama + kanıtlı bulgu + onarım.

## Muhakeme çerçevesi (neden-sonuç / illiyet)
Bu sistemde "müvekkil lehine" sonucu bozan kırık, üç illiyet hattından birinden gelir:

- **H1 — HAK KAYBI HATTI:** süre/usul hesabı yanlış → dilekçe geç → hak düşürücü
  süre kaçar → esasa girilmeden ret. (En ağır; geri dönüşü yok.)
- **H2 — DAYANAK ÇÖKÜŞÜ HATTI:** içtihat/künye teyidi kör kalır veya ALEYHE karar
  LEHE damgalanır → dilekçe kendi aleyhine delil taşır / uydurma atıf → itibar +
  esas kaybı.
- **H3 — SIR/GİZLİLİK HATTI:** müvekkil sırrı, karşı taraf lehine sızar veya
  gizlilik kapısı fail-open davranır → CMK/Avukatlık K. ihlali.
- **H0 — KAPI YANILSAMASI (kesişen):** Bir kapı hata alınca **geçirirse**
  (fail-open), yukarıdaki üç hat da sessizce açılır. Sistemin tüm vaadi
  "model beyan etmez, script denetler" olduğu için fail-open kapı = sistemin
  çekirdek vaadinin kırılması.

## İlerleme defteri
- [x] Depo yapısı çıkarıldı (317 dosya · 35 script · 32.278 satır backend · 20 skill)
- [ ] Baseline süit ölçümü
- [ ] H1 süre hattı taraması
- [ ] H2 künye/içtihat hattı taraması
- [ ] H3 gizlilik hattı taraması
- [ ] H0 fail-open kapı taraması
- [ ] Bulguların kanıtlanması (repro)
- [ ] Onarım + test

---
## BULGULAR (kanıtlı)

### B1 — `tam_tur.py` Python <3.12'de İMPORT EDİLEMEZ (SyntaxError) · H0/KAPI YANILSAMASI
**Kanıt:** `python3.11 -m py_compile tam_tur.py` → `SyntaxError: f-string expression part
cannot include a backslash` (iki yerde: satır 1407 ve 1479). Depodaki 35 script içinde
kırık olan TEK dosya bu — ve rolü en ağır olanı.
**İlliyet:** `README.md:120,157,172` avukata **"Python 3.10+"** diyor; `pyproject.toml:5`
`requires-python=">=3.12"`; CI matrisi yalnız **3.12/3.13** koşuyor. Avukat README'ye uyup
3.10/3.11 kurarsa → `tam_tur.py` HİÇ çalışmaz → `dosya-analiz.json` hiç doğmaz →
`_gate_g_kalicilik_denetle` ilk satırında `if not os.path.exists(analiz_json): return None, None`
→ **Gate G (kalıcılık kapısı) sessizce ATLANIR.** Kapı fail-closed yazılmış (P1-12) ama
koruduğu aracın VAR OLMASINA bağlı: araç hiç doğmazsa kapı kendini kapatmaz, yok sayar.
**Durum:** ONARILDI (sabit metin f-string dışına alındı; 3.11'de tüm depo temiz derleniyor).

### B2 — `--taraf` boşken müvekkil-aleyhi taraması KÖR, ama çıktı "[OK] bulunamadı" diyor · H2
**Kanıt (repro):** İçinde *"borcu kabul etmektedir"*, *"davayı kabul ediyoruz"*,
*"kusurlu olduğunu"*, *"iddia doğrudur"* geçen cevap dilekçesi taslağı:
- `--taraf` YOK  → `[OK] belirgin müvekkil-aleyhi ifade sinyali bulunamadı`
- `--taraf davali` → 3 adet `[UYARI] olası müvekkil-aleyhi ifade`
**İlliyet:** `teslim_paketi.py --taraf` dokümanında **"boş bırakılabilir"**; boşsa alt çağrıya
hiç geçirilmiyor (`+ (["--taraf", a.taraf] if a.taraf else [])`). `denetle()` içinde
`taraf in ALEYHE` False → yalnız 2 desenli `genel` seti taranır. Hiçbir yerde "taraf
verilmedi → tarama KISMİ" uyarısı YOK.
**Ağırlık:** Bu bir *sessiz atlama* değil, **YANLIŞ GÜVENCE**: script "bakmadım" demesi
gerekirken "bulamadım" diyor. HMK m.188: ikrar kesin delildir — geri alınamaz.

### B3 — NEG (olumsuzlama) deseni Türkçe `-me` ekini ayırt etmiyor → GERÇEK İKRAR susturuluyor · H2
**Kanıt (izole):** NEG = `...|\bkabul\s*etme|...`
| girdi | sonuç |
|---|---|
| `Davayı kabul ediyoruz.` | BLOK (doğru) |
| `Müvekkil borcu kabul **etmektedir** ve davayı kabul ediyoruz.` | **BİLGİ — susar** |
| `Borcun tamamını kabul **etmekteyiz**; davayı kabul ediyoruz.` | **BİLGİ — susar** |
| `Müvekkilin borcu kabul **etmesi** sebebiyle davayı kabul ediyoruz.` | **BİLGİ — susar** |
**İlliyet:** Türkçede `-me` hem OLUMSUZLUK eki (`kabul etmemek`) hem MASTAR/çekim ekidir
(`kabul etmektedir` = olumlu ikrar). Desen ikisini ayırmıyor → en yaygın ikrar kalıbı
bir aleyhe eşleşmenin ±70 karakter penceresine düştüğü anda o eşleşme BLOK'tan BİLGİ'ye düşer.

### B4 — `mudahil` CLI'de var, ALEYHE sözlüğünde YOK → doğru kullanımda bile "[OK]" · H2
**Kanıt:** `ALEYHE` anahtarları `{davaci, davali, genel, katilan, musteki, sanik}`;
CLI `--taraf` choices `{davaci, davali, katilan, mudahil, musteki, sanik}` → **kapsanmayan: `mudahil`**.
`--taraf mudahil` ile aynı ikrarlı taslak → `[OK] belirgin müvekkil-aleyhi ifade sinyali bulunamadı`.
**Ağırlık:** B2'den daha sinsi — avukat taraf sıfatını DOĞRU verdiği için "tarandı" sanır.

### B5 — HOOK KATMANI: kod ile teşhis aracı ÇELİŞİYOR (karar gerektirir) · H0
**Olgu:** `plugin.json`'da `"hooks": "./hooks/hooks.json"` satırı YOK. Bunu kaldıran
commit `08441f5` (2026-09-07, main'in HEAD'i):
> *"standart yol olduğu için zaten otomatik yüklenen hooks dosyasını ikinci kez
> bildiriyordu. Bu, kurulumda «Duplicate hooks file detected» hatasına ve eklentinin
> (20 skill dahil) tamamen yüklenememesine yol açıyordu."*

**Çelişki:** Depodaki 4 test + `tools/hook_doktor.py` hâlâ ESKİ sözleşmeyi zorluyor:
- `test_hooks_wiring.py::test_plugin_json_var_ve_gecerli_json`
- `test_hooks_wiring.py::test_plugin_json_hooks_alani_diskte_cozulebilir`
- `test_devir_zorlayici.py::test_plugin_json_hooks_KAYDINI_tasimak_ZORUNDA`
- `test_hook_doktor.py::test_uctan_uca_tum_olaylar_yesil`
- `hook_doktor.py` çıktısı: `plugin.json hooks: ✗ YOK — hook katmanı hiç kaydolmaz (v0.5.6 arızası)`

**Dış teyit (resmi Claude Code plugin referansı, WebFetch 2026-09-10):**
> *"Location: `hooks/hooks.json` in plugin root, or inline in plugin.json"* — standart
> konum OTOMATİK keşfedilir; `plugin.json`'daki `hooks` alanı ÖZEL yol veya INLINE
> tanım içindir. Yani commit'in gerekçesi doğrulanıyor.

**Neden bu bir KIRIK:** Tehlike artık hook'ların ölmesi değil, **teşhis aracının
avukatı sistemi kırmaya yönlendirmesi**. `hook_doktor.py` "✗ ARIZA (v0.5.6)" basıyor;
avukat bunu görüp satırı geri koyarsa → *Duplicate hooks file detected* → **eklentinin
tamamı (20 skill) yüklenmez** → hiçbir kapı korumaz. Yani yanlış alarm, gerçek arızadan
daha yıkıcı bir onarıma çağırıyor. Ayrıca bu 4 kırmızı, CI'yi "yeşermeden sürüm yok"
kuralı gereği kilitli tutar.

**Karar Av. Bayram Can ÇAPAR'a aittir** — iki yol zıt yönde:
(A) Testleri + `hook_doktor.py`'yi yeni sözleşmeye çevir (hooks/hooks.json diskte VE
    geçerli olmalı; `plugin.json` onu YENİDEN bildirmemeli). Kanıtların işaret ettiği yol.
(B) `hooks` satırını geri koy, testler eski hâliyle kalsın — commit'in çözdüğü kurulum
    arızası geri gelir.

## H1 (SÜRE) — TARAMA SONUCU: KIRIK BULUNMADI
`hesapla_sure.py` sınır senaryolarında ölçüldü (adli tatil ilk/son günü, tatil öncesi/
sonrası, ceza CMK m.331/4 üç gün, idari İYUK m.8/3 yedi gün, 31 Ocak→Şubat ay ekleme,
artık yıl 29 Şubat, yıl geçişi). Hepsi doğru. **Kritik gözlem:** ham bitiş 19 Temmuz
(Pazar) → HMK m.93 kayması son günü 20 Temmuz'a (adli tatilin İLK günü) taşıyor ve
uzatma UYGULANMIYOR. Bu, uzatmayı ham bitişe bağlayan (a) yorumudur ve **güvenli
taraftır** (erken tarih hak kaybettirmez, geç tarih kaybettirir). Motor doğru tarafta.

## H3 (GİZLİLİK) — TARAMA SONUCU: KIRIK BULUNMADI
`gizlilik_tara.py` fail-closed: checksum tutmayan TCKN/kart da düşürülmüyor, 'olası'
olarak işaretleniyor. IBAN deseni B-15'te 26 karaktere düzeltilmiş (doğru).
*Latent not (aktif bug değil):* `_MASKE` listesi `MUTLAK_DENY[4]` ile **konuma bağlı**;
listeye eleman eklenir/sırası değişirse maske yanlış deseni maskeler ve IBAN maskesiz
kalır. Ada göre aramak daha dayanıklı olur.

---
## OTURUM KAPANIŞI (2026-09-10)

- **Onarıldı:** B1 (tam_tur.py + README) · B2/B3/B4 (dilekce_denetim.py) · B5 (hook sözleşmesi,
  avukat kararıyla)
- **Kilitlendi:** `tests/test_v0517_muvekkil_lehine_kiriklar.py` (10 sınama) + `test_hooks_wiring.py`
  ve `test_devir_zorlayici.py` yeni sözleşmeye çevrildi. Kilitlerin TUTTUĞU doğrulandı: onarımlar
  geçici geri alındığında testler kırmızı yandı (B3→1, B4→2), geri yüklendiğinde 10/10 yeşil.
- **Nihai ölçüm (Python 3.12 = CI hedef sürümü):** `2314 passed, 15 skipped` → 2329 = işaretçi ·
  `aile_dogrula` 20 parça TEMİZ · `hook_doktor` exit 0, altı olay yeşil.
- **Commit:** `fe4f3ab` · **PR:** https://github.com/bcancapar-spec/ortak-avukat/pull/4 (draft, izleniyor)
- **Avukata bırakılan:** sürüm damgası + CHANGELOG sürüm girişi · `_MASKE` indeks bağı ·
  raporun §4 canlı doğrulama adımları.

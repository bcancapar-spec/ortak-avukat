# AYM ve AİHM Bireysel Başvuru Yolu — Kabul Edilebilirlik Kontrol Listesi (v0.5.18 aday)

> **Model kurar, script denetler.** Bu belge, `scripts/usul_matris.py`'nin `[G10]` (AYM) ve
> `[G11]` (AİHM) denetimlerinin hukuki haritasıdır. Script hiçbir başvuru için «gidilir /
> gidilmez» demez; yalnız her ölçütün **değerlendirildiğini, kanıta bağlandığını** ve
> şüpheli/karşılanmayan ölçütün **gerekçeyle avukata taşındığını** denetler. Süre HESABI
> `oa-sure`'nindir; burada yalnız bağı kurulur. Her dayanak satırı kullanım anında yeniden
> resmî kaynaktan okunur (aşağıdaki teyit tarihleri ilk kurulumun izidir, ezber değildir).

## 0. Neden var — müvekkil lehine gerekçe

AYM bireysel başvurusu ve AİHM başvurusu çoğu dosyanın **son çıkış kapısıdır** ve hatası
telafisizdir: süresi kaçmış, yolu tüketilmemiş, formu eksik ya da «dördüncü derece»
(delil takdirine itiraz) şikâyetine dönüşmüş başvuru esasa hiç girmeden reddedilir. İkinci
büyük kayıp, AYM'nin kabul edilemezlik ya da ihlal-yok kararının «dosya bitti» sanılması ve
AİHM penceresinin sessizce kapanmasıdır. Kontrol listesi bu iki kaybı mekanik olarak
görünür kılar. Fikir kaynağı: Yargı PRO 5-1, 5-3, 5-4, 5-5 (AYM) ve 6-1…6-5 (AİHM) skill
tasarımı — metin alınmadı; ölçütler OA'nın kendi yöntemiyle ve resmî metinden kuruldu.

## 1. Kullanım ve durum sözleşmesi

```bash
python scripts/usul_matris.py --ornek-bb > _oa/cikti/usul-matris.json   # kurgu şablon
python scripts/usul_matris.py --girdi _oa/cikti/usul-matris.json        # [G1]…[G11]
```

Üst düzey `bireysel_basvuru` listesindeki her kayıt bir yoldur (`yol: aym|aihm`). Her ölçüt
`{"durum": ..., "kanit": ..., "not": ...}` taşır. Durum kapalı kümedir:

| Durum | Script davranışı |
|---|---|
| ölçüt hiç yok / geçersiz | **BOŞLUK** — değerlendirilmemiş ölçütle başvuru planlanamaz |
| `tamam` | `kanit` doluysa bulgu satırı; **kanıtsızsa BOŞLUK** (kanıtsız beyan kesin dil sayılmaz) |
| `eksik` | **BOŞLUK** — eksik bilgi/belge tamamlanmadan başvuru hazır sayılmaz |
| `supheli` | **⚠ ŞÜPHELİ** bulgu → avukat kararı; `not` (gerekçe) yoksa BOŞLUK |
| `karsilanmiyor` | **✗ KABUL EDİLEMEZLİK RİSKİ** bulgu → avukat kararı; `not` yoksa BOŞLUK; `avukat_karari` (`devam` \| `vazgec`) yazılmamışsa BOŞLUK (risk bilinçli üstlenilir ya da yoldan vazgeçilir — ikisi de kayda geçer). Script başvuruyu YASAKLAMAZ |
| `uygulanmaz` | yalnız koşullu kalemlerde (aşağıda «koşullu» işaretli); temel ölçütte BOŞLUK |

Alan hiç yoksa (eski dosya) `[G10]`/`[G11]` satırı basılmaz — mevcut exit sözleşmesi korunur.

## 2. AYM — kabul edilebilirlik ölçütleri `[G10]`

Teyit: Yargı PRO `mevzuat_getir` (mevzuat.gov.tr), `mevzuatgov:kanun:5:6216`, 2026-10-05.

| Anahtar | Ölçüt (OA özeti) | Dayanak |
|---|---|---|
| `konu_bakimindan` | Hak hem Anayasa'da hem AİHS ve Türkiye'nin taraf olduğu ek protokollerde korunuyor; ihlal kamu gücünden; yasama işlemi ve düzenleyici idari işlem aleyhine doğrudan başvuru yok; AYM kararları ve yargı denetimi dışındaki işlemler konu olamaz | 6216 m.45/1, m.45/3 |
| `kisi_bakimindan` | **Mağdur sıfatı:** güncel ve kişisel hak DOĞRUDAN etkilenmiş; kamu tüzel kişisi başvuramaz; özel hukuk tüzel kişisi yalnız tüzel kişiliğe ait hakları için; yabancı, yalnız Türk vatandaşlarına tanınan haklarda başvuramaz | 6216 m.46 |
| `zaman_bakimindan` | Nihai işlem/karar 23.09.2012'den sonra kesinleşmiş | 6216 geçici m.1/8 |
| `yollarin_tuketilmesi` | Kanunda öngörülen idari ve yargısal yolların TAMAMI tüketilmiş; şikâyetin özü derece yargısında ileri sürülmüş (dilekçelerle gösterilir) | 6216 m.45/2 |
| `anayasal_onem_onemli_zarar` | Başvuru Anayasa'nın uygulanması/yorumlanması ya da temel hakların kapsamı ve sınırları bakımından önem taşıyor **ya da** başvurucu önemli bir zarara uğradı (ikisi BİRDEN yoksa kabul edilemezlik kararı verilebilir) | 6216 m.48/2 (ilk eşik) |
| `acik_dayanaktan_yoksunluk` | Açıkça dayanaktan yoksun değil; şikâyet kanun yolunda gözetilecek bir husus değil («dördüncü derece» yasağı — mahkeme kararına karşı başvuruda inceleme ihlalin varlığı ve giderimiyle sınırlıdır) | 6216 m.48/2 (ikinci eşik), m.49/6 |
| `kotuye_kullanmama` | Bireysel başvuru hakkı açıkça kötüye kullanılmıyor; aksi hâlde yargılama giderleri dışında **iki bin TL'yi geçmeyen disiplin para cezası** | 6216 m.51 |

Ek usul notları (resmî metin): kabul edilebilirlik incelemesi komisyonlarca yapılır;
kabul edilemezlik kararları **kesindir ve ilgililere tebliğ edilir** (m.48/3-4). Başvuru
harca tabidir (m.47/2); avukatla temsil hâlinde vekâletname sunulur (m.47/4).

## 3. AYM başvuru formu ve zorunlu ekler (`form` alt listesi)

Teyit: AYM İçtüzüğü `mevzuatgov:ic_tuzuk:5:1` — m.59 (Değişik: RG 6/11/2018-30587), m.60,
m.63, m.66; 6216 m.47/3, m.47/6 (2026-10-05).

- Başvuru, İçtüzük ekindeki (EK-1) ve Mahkemenin internet sitesindeki **form** kullanılarak
  resmî dilde yapılır (m.59/1). Serbest dilekçe formun yerine geçmez.
- Form içeriği m.59/2 (a)–(l); zorunlu ekler m.59/3 (a)–(h). Koşullu kalemler (`uygulanmaz`
  verilebilir): 59/2-b, c, ğ, ı, i, l · 59/3-a, c, ç, f, ğ, h · 60/2. **Koşula bağlı**
  kalemler: 59/3-b harç belgesi yalnız **adli yardım** talebinde (59/3-h `tamam`; talep
  Bölüm/Komisyonca karara bağlanır — m.62/2); 59/2-f tüketme aşamaları ve 59/3-g kanun
  yolu dilekçeleri yalnız **başvuru yolu öngörülmemişse** (kayıtta
  `"basvuru_yolu_ongorulmemis": true` — 6216 m.47/3 ve 47/5 bu hâli ayrıca düzenler).
- Belge sunulamıyorsa gerekçesi ve varsa bilgisi forma eklenir (m.59/4); bilgilerde
  değişiklik Mahkemeye bildirilir (m.59/5).
- Form (ekler hariç) **on sayfayı geçerse** olayların özeti ayrıca eklenir (m.60/2).
- **Başvuru tarihi:** usulünce hazırlanan form harç tahsil makbuzuyla birlikte teslim
  edildiğinde verilen alındı belgesinin tarihi (m.63/2) — doğrudan, mahkemeler ya da yurt
  dışı temsilcilikler aracılığıyla (6216 m.47/1; İçtüzük m.63/1).
- **Eksiklik:** Bireysel Başvuru Bürosu şekil incelemesi yapar; eksiklik için **on beş günü
  geçmeyen KESİN süre** verilir; geçerli mazeret olmadan tamamlanmazsa ret (6216 m.47/6;
  İçtüzük m.66/1-2). Süresinde yapılmayan, şekle aykırı ya da eksiği tamamlanmayan başvuru
  Komisyonlar Başraportörünce reddedilir; tebliğden itibaren **yedi gün** içinde Komisyona
  itiraz edilebilir, Komisyon kararı kesindir (m.66/3). → Bu iki süre de `oa-sure`'ye gider;
  yazıda fiilen verilen süre esastır.

## 4. Süre — `oa-sure` bağı (hesap burada YAPILMAZ)

- **AYM:** başvuru yollarının tüketildiği tarihten; yol öngörülmemişse ihlalin öğrenildiği
  tarihten itibaren **otuz gün**; haklı mazerette mazeretin kalktığı tarihten **on beş gün**
  + belgeler (6216 m.47/5). `oa-sure` kuralları: `aym_bireysel`; mazeret süresi
  `aym_bireysel_mazeret` (oa-sure v0.5.18 kataloğu).
- **AİHM:** iç hukuk yollarının tüketilmesinden sonra ve kesinleşmiş iç hukuk kararından
  itibaren **dört ay** (AİHS m.35/1, 15 No.lu Protokol m.4 ile değişik metin — Orhan/Türkiye
  (k.k.), no. 38358/22, 6 Aralık 2022, § 25). 1.2.2022 öncesi kararlara ilişkin altı ay
  geçişi OA kapsamı dışındadır (avukat kararı 2026-10-06): motor her dosyada dört ay esas
  alır (`oa-sure` ile aynı). Süre, uygulamada kararın tebliğinden (ya da içeriğinin
  öğrenilme imkânından) işler (aynı karar §§ 31, 35, 46);
  süre kuralı kamu düzenindendir ve resen gözetilir (aynı karar § 23; Aybek ve
  Diğerleri/Türkiye (k.k.), no. 32365/20, 2 Haziran 2026, §§ 6, 9-10). Kaynak: HUDOC,
  Yargı PRO `aihm_ictihat_ara` + `ictihat_getir` (Türkçe çeviri — Adalet Bakanlığı).
  `[G11]` nihai karar tarihini ister ve süreyi dört ay olarak basar; son günü `oa-sure`
  hesaplar; oa-sure v0.5.18 kataloğundaki kural `aihm_basvuru`dur.
  Kural adı katalogda (`oa-sure/scripts/sure_kurallari.json` — adların TEK kaynağı)
  yoksa `[G10]`/`[G11]` görünür bulgu basar; önek yolla tutarsızsa BOŞLUK.
- Script iki alanı ZORUNLU tutar: `sure.son_gun` (oa-sure çıktısı) ve
  `sure.baslangic_kaniti` (tebliğ şerhi, UYAP kaydı, tefhim tutanağı…). Belgesiz başlangıçla
  kesin son gün yazılmaz (aile kuralı G4/G9 ile aynı ihtiyat).
- `sure.basvuru_tarihi` son günü aşıyorsa **SÜRE GEÇMİŞ** bulgusu basılır ve
  `sure.avukat_karari` (`devam` | `vazgec`) yazılmadan boşluk kapanmaz. AYM'de `devam`
  kararı `sure.mazeret_kaniti` ister: mazeret, onu **belgeleyen delillerle** birlikte ileri
  sürülür (6216 m.47/5; form 59/2-ğ, ek 59/3-ğ).

## 5. AİHM — kabul edilebilirlik ölçütleri `[G11]`

Sözleşme metni Yargı PRO mevzuat aracında yok; ölçütler AİHM'in kendi kararlarından
(HUDOC, Türkçe çeviri) teyit edildi.

| Anahtar | Ölçüt (OA özeti) | Dayanak · teyit |
|---|---|---|
| `magdur_sifati` | Başvurucu iddia edilen ihlalden kişisel olarak etkilenen «mağdur» | AİHS m.34 · Aksu/Türkiye [BD] (2012) «Article 34 - Victim» |
| `yollarin_tuketilmesi` | İç hukuk yolları tüketildi; Türkiye yönünden **AYM bireysel başvurusu** etkili iç hukuk yoludur; şikâyetin özü AYM'de ileri sürüldü | AİHS m.35/1 · Aybek ve Diğerleri § 3 (Uzun/Türkiye (k.k.), no. 10755/13 atfı) |
| `konu_bakimindan_bagdasma` | Şikâyet edilen hak Sözleşme/Protokol kapsamında (konu bakımından bağdaşma) | AİHS m.35/3-a · Orhan § 54 |
| `acik_dayanaktan_yoksunluk` | Açıkça dayanaktan yoksun değil; delil takdirine itiraz («dördüncü derece») değil | AİHS m.35/3-a · Orhan § 56 |
| `onemli_zarar` | Başvurucu önemli bir zarar görmüş **ya da** insan haklarına saygı esas incelemeyi gerektiriyor | AİHS m.35/3-b (15 No.lu Protokol m.5) · Ağcakaya/Türkiye (k.k.), no. 39365/18, 13 Eylül 2022, § 10-11 |
| `ayni_konu_baska_merci` | Esasen aynı başvuru AİHM'ce daha önce incelenmemiş ve başka bir uluslararası soruşturma/çözüm merciine sunulmamış (sunulduysa ilgili yeni bilgi var) | AİHS m.35/2-b · Varnava ve Diğerleri/Türkiye [BD], no. 16064/90 ve diğerleri, 18 Eylül 2009 — HUDOC künye özeti: ilgili madde «35-2-b», sonuç «Preliminary objections dismissed (substantially the same …)» |
| `kotuye_kullanmama` | Bireysel başvuru hakkı kötüye kullanılmıyor (değerlendirme avukatın) | AİHS m.35/3-a · Akdivar ve Diğerleri/Türkiye [BD], no. 21893/93, 16 Eylül 1996 — HUDOC künye özeti «(Art. 35-3-a) Abuse of the right of application» |
| `eksiksiz_basvuru` | Resmî formun bütün alanları ve zorunlu ekler eksiksiz | AİHM İçtüzüğü m.47 — **TEYİT BEKLİYOR** (metin MCP'de yok) |

## 6. AİHM emsal araştırma protokolü (Yargı PRO MCP)

Künye otoritesi HUDOC'tur; ikincil kaynaktaki (makale, kitap) künye iddiadır.

1. **Bağlam önce:** madde + şikâyet + ispatlanacak vakıa tek satırda yazılmadan sorgu yok.
2. **Arama — `aihm_ictihat_ara`:** varsayılan davalı devlet Türkiye (`ulke: TUR`; tümü için
   `HEPSI`). Hedefleme alan sözdizimiyle değil **parametreyle** yapılır: `madde` (ör. `6`,
   `35-1`, `P1-1`), `ihlal` / `ihlal_yok`, `karar_tipi` (`karar` | `kabul_edilebilirlik`),
   `onem_duzeyi: 1` (ilke kararları), `basvuru_no`, `dava_adi`, tarih sınırları, `dil: TUR`
   (Türkçe çeviri satırı varsa onu tercih et). `keywords`'te boşluk = VE, `"tam öbek"`,
   büyük harf `OR`/`NOT`. Aynı karar her dil için ayrı satır döner.
3. **En az bir aleyhe tur:** `ihlal_yok` ve `karar_tipi: kabul_edilebilirlik` ayrı aramalar
   (Hükümetin savunma hattı oradadır) — sonuç `oa-antitez` cephaneliğine gider.
4. **Tam metin — `ictihat_getir`** (`document_id: aihm:<itemid>`): kısa liste tam metinle
   okunur; `metin_var: false` ise aynı kararın başka dil satırı denenir; daire/Büyük Daire/
   komite ve hüküm fıkrası metinden doğrulanır.
5. **Kütük:** arama `oa_hafiza.py teyit --arac aihm_ictihat_ara` (ARAMA sınıfı — damga
   vurulmaz); tam metin `--arac ictihat_getir --damga … --dokum-sinifi tam-metin`.
6. **Dilekçede künye biçimi:** «Örnek/Türkiye, no. 12345/18, 10.12.2019, § 45» ya da «(Başvuru
   no. 12345/18)». Atıf kapısı (`oa-kontrol/kunye_teyit.py`) bu Türkçe yazımı v0.5.18'den beri
   künye olarak tanır (AİHM bağlamı + «no.»/«B. No»/«Başvuru no» öneki); eskiden EKSİK KÜNYE
   sayılıyordu.
7. **AYM emsali** için `aym_ictihat_ara` (`decision_type: bireysel_basvuru`, `basvuru_no`) +
   `ictihat_getir` (`anayasa:<guid>`); ayrıntı `oa-ictihat`.

## 7. Karar sonrası yollar

**AYM** (6216 m.50; teyit 2026-10-05):
- İhlal kararında ihlalin ve sonuçlarının giderilmesi için yapılması gerekenlere hükmedilir;
  yerindelik denetimi yapılamaz, idari işlem/eylem niteliğinde karar verilemez (m.50/1).
  `ihlal` / `kismi` kararında `ihlal_kaynagi` ZORUNLUDUR (`mahkeme_karari` → m.50/2
  yeniden yargılama; `diger` → m.50/1 giderim); yazılmamışsa `[G10]` BOŞLUK üretir —
  giderim yolu ihlalin kaynağına göre ayrılır.
- İhlal **mahkeme kararından** kaynaklanıyorsa dosya yeniden yargılama için ilgili mahkemeye
  gönderilir; yeniden yargılamada hukuki yarar yoksa tazminata hükmedilebilir ya da genel
  mahkemelerde dava yolu gösterilebilir; mahkeme mümkünse dosya üzerinden karar verir (m.50/2).
  **Dayanak 6216 m.50/2'dir:** HMK m.375/1-i, CMK m.311/1-f ve İYUK m.53/1-ı yalnız **AİHM**
  kararını (ve AİHM'de dostane çözüm / tek taraflı deklarasyonla düşmeyi) sayar — AYM
  kararına dayanak gösterilmez (`[G10]` yanlış dayanağı BOŞLUK sayar).
- Bölüm kararları ilgililere ve Adalet Bakanlığına tebliğ edilir (m.50/3); feragatte düşme
  (m.50/5).
- **Kabul edilemezlik / ihlal yok / kısmi** → AİHM yolu ayrıca değerlendirilir; `[G10]`
  `aihm_degerlendirmesi` boşsa BOŞLUK üretir. «Gidilmeyecek» de bir avukat kararıdır ve
  yazılır.

**AİHM** (iç hukukta yeniden yargılama — mevzuat.gov.tr metinleri, 2026-10-05):

| İniş kolu | Dayanak | Süre (hesap `oa-sure`) |
|---|---|---|
| Hukuk | HMK m.375/1-i + m.377/1-e | Kesinleşmiş AİHM kararının **tebliğinden üç ay**; «her hâlde on yıl» azami süresi (e) bendi yönünden AYM E.2022/7, K.2022/79 (21.06.2022, RG 01.07.2022/31883) ile iptal (kaynak: v0.5.18 doğrulama turu kaydı, 2026-10-05; karar Yargı PRO `aym_ictihat_ara` ile görüldü) |
| Ceza | CMK m.311/1-f | AİHM kararının **kesinleştiği tarihten bir yıl**; bent 4.2.2003'te kesinleşmiş kararlar ve bu tarihten sonraki başvurular için (m.311/2) |
| İdari | İYUK m.53/1-ı + m.53/3 | AİHM kararının **kesinleştiği tarihten bir yıl** |

- Üç bent de ihlal tespitinin yanında AİHM'deki **dostane çözüm ya da tek taraflı deklarasyon
  sonucu düşme** kararını sayar (`karar_turu: dostane_cozum | tek_tarafli_deklarasyon`).
- **Adil tazmin:** AİHS m.41 (HUDOC künye özetlerinde «Article 41 — Just satisfaction»).
  Talebin süresi ve biçimi (AİHM İçtüzüğü m.60) — **TEYİT BEKLİYOR**.
- AİHM kararının kesinleşme anı (AİHS m.44), Büyük Daire'ye gönderme (m.43) ve infaz
  denetimi (m.46) — **TEYİT BEKLİYOR**; kesinleşmeye bağlı sayaçlar kesinleşme belgesi
  gelmeden «kesin» yazılmaz.

## 8. `usul_matris.py` girdi şeması (`bireysel_basvuru`)

```json
{"bireysel_basvuru": [
  {"id": "BB1", "yol": "aym",
   "kriterler": {"konu_bakimindan": {"durum": "tamam", "kanit": "…"},
                 "kisi_bakimindan": {…}, "zaman_bakimindan": {…},
                 "yollarin_tuketilmesi": {…}, "anayasal_onem_onemli_zarar": {…},
                 "acik_dayanaktan_yoksunluk": {…}, "kotuye_kullanmama": {…}},
   "basvuru_yolu_ongorulmemis": false,
   "form": {"59/2-a": "tamam", "…": "…", "60/2": "uygulanmaz"},
   "sure": {"kural": "aym_bireysel", "baslangic": "YYYY-AA-GG",
            "baslangic_kaniti": "…", "son_gun": "YYYY-AA-GG", "basvuru_tarihi": null,
            "avukat_karari": "devam|vazgec (yalnız SÜRE GEÇMİŞ)", "mazeret_kaniti": "…"},
   "karar_sonrasi": {"karar_turu": "ihlal|ihlal_yok|kabul_edilemezlik|kismi|dusme",
                     "ihlal_kaynagi": "mahkeme_karari|diger", "dayanak": "6216 m.50/2",
                     "aihm_degerlendirmesi": "…"}},
  {"id": "BB2", "yol": "aihm",
   "kriterler": {"magdur_sifati": {…}, "yollarin_tuketilmesi": {…},
                 "konu_bakimindan_bagdasma": {…}, "acik_dayanaktan_yoksunluk": {…},
                 "onemli_zarar": {…}, "ayni_konu_baska_merci": {…},
                 "kotuye_kullanmama": {…}, "eksiksiz_basvuru": {…}},
   "sure": {"kural": "aihm_…", "nihai_karar_tarihi": "YYYY-AA-GG", "baslangic": "…",
            "baslangic_kaniti": "…", "son_gun": "…"},
   "karar_sonrasi": {"karar_turu": "ihlal|ihlal_yok|kabul_edilemezlik|dostane_cozum|tek_tarafli_deklarasyon|dusme",
                     "inis_kolu": "hmk|cmk|iyuk", "sure_kurali": "…", "son_gun": "…",
                     "adil_tazmin": "…"}}]}
```

`karar_sonrasi` opsiyoneldir (karar yoksa yazılmaz). Ölçüt kaydında `durum:
karsilanmiyor` ise `"avukat_karari": "devam|vazgec"` da yazılır. Kurgu tam şablon:
`--ornek-bb`.

## 9. Ceza karar sonrası — koruma tedbiri tazminatı (CMK m.141-142) — yöntem notu

Fikir kaynağı Yargı PRO 1-7 (yalnız tazminat kolu; infaz hesabı bilinçli olarak alınmadı —
oranlar geçici maddelerle sık değişir, hesap aracı yokken kesin infaz tarihi verilmez).
Teyit: `mevzuatgov:kanun:5:5271` m.141-142 (7499 değişiklikleriyle), 2026-10-05.

- **Kimler:** m.141/1 (a)–(l) bentleri — örnekler: kanuni koşullar dışında yakalama/
  tutuklama (a); kanuni gözaltı süresinde hâkim önüne çıkarılmama (b); makul sürede yargılama
  mercii huzuruna çıkarılmama (d); kanuna uygun yakalama/tutuklamadan sonra kovuşturmaya yer
  olmadığı ya da beraat kararı (e); gözaltı ve tutuklulukta geçen sürenin hükümlülük
  süresini aşması ya da yalnız para cezası (f); ölçüsüz arama (i); koşulları oluşmadan
  elkoyma (j); konutu terk etmeme / tedavi gibi adli kontrol sonrası kovuşturmaya yer
  olmadığı ya da beraat (l — 7499 ile eklendi). (e), (f), (l) kararlarını veren merci
  tazminat hakkını ilgiliye bildirir ve bu karara geçirilir (m.141/2).
- **Süre (hak düşürücü nitelikte izlenir):** kesinleşmenin ilgilisine **tebliğinden üç ay ve
  her hâlde kesinleşmeyi izleyen bir yıl** (m.142/1) — iki sınırdan önce dolan esas alınır;
  hesap `oa-sure` (kural yoksa elle hesap + `sureler.json` flag'i + «TEYİT BEKLİYOR» şerhi).
- **Merci:** zarara uğrayanın oturduğu yer ağır ceza mahkemesi; **ancak (e), (f), (l)
  bentleri 6384 sayılı Kanun (Tazminat Komisyonu) kapsamındadır** — ağır cezaya yapılan bu
  istemler Komisyona gönderilir; karma istemde ayrılır ve **ağır cezaya istem tarihi esas
  alınır** (m.142/2, 7499 ek cümleleri).
- **Dilekçe:** açık kimlik ve adres, zarara yol açan işlem, zararın nitelik ve niceliği +
  belgeler (m.142/3); eksiklik **bir ay** içinde giderilmezse istem itiraz yolu açık olarak
  reddedilir (m.142/4).
- **Kanun yolu:** istinaf (istemde bulunan, Cumhuriyet savcısı, Hazine temsilcisi); karar
  yerinde görülmezse BAM işin esası hakkında karar verir ve BAM'ın bu fıkra uyarınca
  verdiği kararlar **kesindir** (m.142/8, 7499) — temyiz beklentisi verilmez.
- `usul_matris.py`'de ayrı kontrol listesi YOKTUR (yalnız yöntem notu); süre satırı
  `oa-sure`/`sure_nobetci` disipliniyle izlenir.

## 10. TEYİT BEKLİYOR ve avukat kararı gereken noktalar

- **TEYİT BEKLİYOR:** AİHM İçtüzüğü m.47 (eksiksiz başvuru ve sürenin kesilmesi), m.60 (adil
  tazmin talebinin süresi/biçimi); AİHS m.43 (Büyük Daire), m.44 (kesinleşme), m.46 (infaz
  denetimi), m.35/2-a (anonim başvuru — HUDOC aramasında künye özeti bulunamadı; listeye
  alınmadı). AİHM kuralının oa-sure'deki adı artık `aihm_basvuru`dur (oa-sure v0.5.18
  kataloğu). m.35/2-b ve m.35/3-a «kötüye kullanma» HUDOC künye özetleriyle teyit
  edilip listeye girdi. AYM'de «yer bakımından yetki»
  ölçütü 6216'da adıyla yer almıyor ve AYM kararlarında teyit edilemedi — listeye alınmadı.
- **Avukat kararı:** her `supheli`/`karsilanmiyor` ölçüt (karşılanmıyorsa `avukat_karari`
  kayda geçer); süresi geçmiş başvuruda mazeret yolu (6216 m.47/5 — `sure.avukat_karari`);
  AYM kabul edilemezlik/ihlal-yok kararından sonra AİHM'e gidilip gidilmeyeceği; AİHM'de
  dostane çözüm / tek taraflı deklarasyon tercihi (müvekkilin yazılı iradesi); yeniden
  yargılama mı tazminat mı.

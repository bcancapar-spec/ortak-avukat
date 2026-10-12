# Başlangıç Kapısı — tebliğ, tefhim, öğrenme (v0.5.18)

> **Neden var:** süre motoru tarih aritmetiğini doğru yapar; ama **yanlış olaya bağlanan
> doğru hesap, yanlış hesaptır.** Saha derslerinde süre kayıpları hesap hatasından çok
> başlangıç tarihinin belgesiz ya da yanlış olaydan alınmasından doğdu (kesinleşme şerhini
> tek tarih sanmak, e-tebligatta ulaşma günü ile tebliğ sayılma gününü karıştırmak, AYM'de
> öğrenmeyi atlamak). Bu kapı, hesaba girmeden önce **hangi olay** ve **hangi kanıt**
> sorusunu mekanik olarak sorar. Script hukuki nitelendirme yapmaz; yalnız kayıt ile
> kuralın izinli başlangıç türlerini karşılaştırır ve çelişkiyi görünür kılar.
>
> Fikir kaynağı: Yargı PRO 12-2 (tebligat denetimi) ve 12-3 (öğrenme tarihi denetimi).
> Metin onlardan kopyalanmadı; OA yöntemiyle (model kurar, script denetler) yeniden yazıldı.
> Aşağıdaki her norm Mevzuat MCP'den teyitlidir (2026-10-05); teyit edilemeyen yer
> **TEYİT BEKLİYOR** diye işaretlidir.

## 1. Dört soru — sırayla

1. **Hangi olay süreyi başlatıyor?** Kuralın `izinli_baslangic_turleri` alanına bak
   (`sure_kurallari.json`). Ör. HMK m.345 istinaf ve m.361 temyiz, İİK m.363 istinaf ve
   m.364/2 temyiz **yalnız tebliğden** işler — tefhim ya da öğrenme süreyi başlatmaz.
   CMK m.268 itiraz ve İİK m.16 şikâyet ise **öğrenmeden** işler.
2. **Hangi kanıt?** `--baslangic-kaniti` ile beyan et:
   - `mazbata` — tebliğ mazbatası/şerhi. TK m.21: muhatap bulunamaz veya tebellüğden
     kaçınırsa ihbarnamenin kapıya yapıştırıldığı tarih tebliğ tarihidir; adres kayıt
     sistemindeki adreste de aynı (m.21/2). TK m.35: adresini değiştirip bildirmeyene,
     evrakın eski adrese asıldığı tarih tebliğ tarihidir.
   - `uets-kaydi` — e-tebligat. TK m.7/a: tebligat, muhatabın elektronik adresine
     **ulaştığı tarihi izleyen beşinci günün sonunda** yapılmış sayılır. Motor bu kanıtta
     iki senaryoyu (ulaşma günü / ulaşma+5) **kendiliğinden** hesaplar; BİZİM süremizde
     plan erken tarihtir.
   - `kalem-tevdi` — celsede veya kalemde imza karşılığı tevdi; TK m.36: tebliğ
     hükmündedir.
   - `ilan` — ilanen tebligat; TK m.31: son ilan tarihinden itibaren **yedi gün sonra**
     tebliğ sayılır (merci 15 güne kadar uzun süre tayin edebilir). `--teblig`'e tebliğ
     sayılma tarihini gir.
   - `tefhim-tutanagi` — yüze karşı açıklama.
   - `uyap-erisim-kaydi` — öğrenme kaydı.
   - `kesinlesme-serhi` — kesinleşme tarihi (ör. HMK m.20/1'de kanun yoluna
     başvurulmadan kesinleşen görevsizlik/yetkisizlik kararı).
   - `beyan` / `yok` — belge yok. Hesap yapılır ama **ihtiyat** amaçlıdır; karşı tarafa
     kesin dil kurulamaz.
3. **Tebliğ geçerli mi?** `--teblig-durumu gecerli|usulsuz|supheli`:
   - **Vekile tebliğ** (TK m.11/1): vekil vasıtasıyla takip edilen işte tebligat vekile
     yapılır; birden çok vekile yapılmışsa **ilkine** yapılan tebliğ asıl tebliğ tarihidir.
     Asile yapılan tebliğ ayrıca incelenir (CMK'nın sanığa tebliğ hükümleri saklıdır).
   - **Usulsüz tebliğ** (TK m.32): tebliğ usulüne aykırı olsa bile muhatap tebliğe muttali
     olmuşsa muteberdir; **muhatabın beyan ettiği tarih** tebliğ tarihi sayılır. Usulsüzlük
     süreyi kendiliğinden sınırsız bırakmaz → `--teblig` öğrenme tarihi olmalı ve
     `--baslangic-turu ogrenme` verilmeli; motor eksikse uyarır.
   - **Şüpheli** (tarih okunamıyor, mazbata eksik, çelişkili kayıt): motor **tek kesin
     tarih üretmez**; çıktı "İHTİYAT HEDEFİ" diye etiketlenir ve deftere öyle yazılır.
     Okunamayan tarih tahmin edilmez — silik bir tarihten hesaplanan süre, hiç
     hesaplanmamış süreden daha tehlikelidir.
4. **Belirsizlik varsa?** İki senaryo hesapla (`--baslangic-turu belirsiz`, `--uets`), plan
   **erken** tarihe göre; ham tarihlerin küçüğünü otomatik seçme — hangi olayın hangi
   kanıtla bağlandığını dosyaya yaz.

## 2. Rejime göre başlangıç (öğrenme üçgeni)

| Rejim | Başlangıç | Not |
|---|---|---|
| HMK istinaf/temyiz | ilamın **tebliği** (m.345/1, m.361/1) | Tefhim ve öğrenme başlatmaz. İş mahkemesinde de aynı (7036 m.7/4). |
| İİK icra mahkemesi istinaf/temyiz | **tebliğ** (m.363, m.364/2) | 7499 s.K. "tefhim veya" ibaresini kaldırdı. Adli tatilde uzamaz (İİK m.18/1). |
| İİK şikâyet | işlemin **öğrenilmesi** (m.16/1) | Öğrenmeyi belgeye bağla. |
| CMK itiraz | kararın **öğrenilmesi** (m.268/1) | İstinaf/temyiz ise gerekçeli kararın tebliğinden (m.273/1, m.291/1). |
| AYM bireysel başvuru | başvuru yollarının **tüketilmesi**; yol yoksa ihlalin **öğrenilmesi** (6216 m.47/5) | Nihai kararın UYAP'tan öğrenildiği tarih AYM kararlarında olay olarak kaydedilmektedir (ör. Ramazan Seçen, B. No: 2021/37483, 6/1/2026, § 9) — tebliğden önce öğrenme süreyi başlatabilir; genel ilke **TEYİT BEKLİYOR**. Erken öğrenme kanıtı varsa erken tarihi esas al. |
| AİHM | nihai iç hukuk kararı; iç hukukta yazılı tebliğ öngörülüyorsa **tebliğ** (Sabri Güneş/Türkiye [BD], no. 27396/06, § 53 — Worm/Avusturya) | AYM'nin öğrenme yaklaşımını AİHM'e otomatik taşıma. Son gün tatile rastlasa da **uzamaz** (§§ 60-61). |

## 3. Karşı tarafın süresi (taarruz)

Karşı tarafa "süre kaçırılmıştır" kesin dili ancak şu üçü birlikteyken kurulur:
(a) başlangıç **belgeli** (mazbata/UETS/kalem tevdi/tefhim tutanağı), (b) bütün senaryolar
aşılmış (UETS, CMK tatil-içi tebliğ), (c) adli tatil rejimi ve tatil takvimi **teyitli**.
Motor `--islem` ile bunlardan biri eksikse kesin dil yerine **ARA TESPİT** basar.

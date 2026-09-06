> **Kaynak belge (2026-09-06).** Bu dosya, v0.5.16 infazının dayandığı iki dış denetim raporundan biridir; deponun `_gorus/` kuralıyla (dış görüş = değişmeden saklanır, infaz kararları CHANGELOG/DENETIM-v0516.md'de) aynen alınmıştır. Taraflar/olgular sentetik, içtihatlar Yargı Pro'dan tam metinle teyitli (anayasa m.6-7).

# ORTAK AVUKAT v0.5.15 — BÜTÜNLEŞİK ANALİZ VE ÖNERİ RAPORU

**Sunulan:** Av. Bayram Can Çapar (karar verici)
**Tarih:** 6 Eylül 2026
**Kapsam:** Dört oturum — döngü mimarisi · graf ve hook yapısı · üç dalda saha sınaması (Yargı Pro) ·
Yargıtay→Antalya BAM→Denizli dikey iniş
**Kanıt standardı:** Her bulgu ya kaynak satırıyla ya fiilî koşu çıktısıyla dayanaklıdır. Beyan yok, ölçüm var.
Tüm taraflar/olgular sentetik; içtihatlar gerçek ve Yargı Pro'dan tam metinle teyitli (anayasa m.6–7).

---

## SUNUŞ — bir sayfada

**Ne yapıldı.** Depo klonlandı (305 dosya, 27.244 satır Python, 1.763 test, 20 skill). Kaynak okundu;
önermeler sentetik mikro-testlerle sınandı; sonra **üç gerçek dava yapısında** (muris muvazaası,
tüzel kişilik perdesi, taksirle öldürme) hook zinciri fiilen koşturuldu ve **26 Yargı Pro çağrısıyla 8
karar tam metniyle** teyit ritüelinden geçirildi; son olarak aynı dalların **Denizli–Antalya–Yargıtay**
zincirleri üstten alta inilerek izlendi. Yaklaşık 40 ayrı ölçüm yapıldı.

**Hüküm — üç cümle.**
1. **Zorlama omurgası sağlam.** Teyit ritüeli, DAMGA çapraz kontrolü, uydurma künye kapısı, ALEYHE
   yasağı, tam-metin şartı, İNGEST-ÖNCE kapısı, hook throttle/dedup/ask — hepsi ölçüldü, hepsi
   tasarlandığı gibi çalıştı. Halüsinasyon ve aleyhe sızması mekanik olarak kapalı.
2. **Graf katmanı doğru modelliyor, ama zorlamadan pay almamış.** Yargı Pro teyidi, şemanın Yargıtay'ın
   gerçek ölçütleriyle birebir örtüştüğünü gösterdi (muvazaada dört ölçüt = dört kenar; perdede "aynı
   yönetici" = köprü düğüm). Buna karşın grafın bulduğu boşluk avukata ulaşmıyor, delilsiz kenar yeşil
   geçiyor, dedektörlerin bir kısmı sistematik yanlış alarm veriyor.
3. **Kopuşlar katmanların kesiştiği yerde.** Graf→hook (K1), hızlı denetim→anayasa m.6 (K3),
   taslak→künye tanıma (K4), kütük→akıbet (K5). Kod doğru; tetik ve sözleşme kopuk — deponun kendi
   v0.5.5.1 dersi: *"kapının gücü kodunda değil tetiğindedir."*

**En yüksek getirili üç hamle (toplam birkaç oturum):**
- **[F] içtihat kapısını hızlı kipe al** → anayasa m.6 ihlali bir sonraki turda görünür (K3).
- **Graf bekçisini dosya adına değil `arac` damgasına bağla + çevrimde exit 3** → K1, K2, G6 tek onarımda.
- **Atıf tanıyıcıya tarih-only / K-only / birleşik biçim ekle, "EKSİK KÜNYE" sınıfı BLOK** → K4.

Kalan 19 bulgu ve 12 hamlelik sıralı reçete §9–§10'da; avukatın vereceği 12 karar §11'de.

---

## 1. YÖNTEM

| Oturum | Soru | Yöntem | Çıktı |
|---|---|---|---|
| 1 | Döngü yapısı | Klon → tam metin tarama → kaynak okuma → 37 test koşusu → sentetik graf | `loop-analizi.md` |
| 2 | Graf + hook yapısı | 8 dedektör okuması → sentetik dava klasöründe fiilî hook koşusu → mimari graf üzerinde deponun kendi dedektörü | `graf-hook-analizi.md` |
| 3 | Üç dalda saha | 3 sentetik klasör, gerçek yapılı graflar → Yargı Pro (4 arama, 3 tam metin) → teyit ritüeli → kapılar | `saha-sinamasi-raporu.md` |
| 4 | Dikey iniş | Denizli×Antalya×Yargıtay zincirleri (12 arama, 5 tam metin) → deterministik çıkarıcı → kata kata iniş | `dikey-inis-raporu.md` + `kanun_yolu_zinciri.py` |

Deponun kendi doktrini analize uygulandı: *önce kırmızı* (kusur fiilen üretildi), *beyan değil ölçüm*
(GitHub'ın sunduğu README bayattı — klon esas alındı), *sessiz atlama yok* (yapılamayan her şey §12'de).

---

## 2. MİMARİ — DÖNGÜ YAPISI

Depoda tek bir "loop" yok, **yedi ayrı döngü sınıfı** var; farklı ölçeklerde çalışır, farklı garantilerle korunur.

| # | Sınıf | Ölçek | Sonlanma garantisi | Durum |
|---|---|---|---|---|
| L1 | Yaşam döngüsü — `tam_tur` (bir kez tam, sonra delta) | dosya ömrü | Gate G+ dört fiziksel koşul; bayat-künye kapısı | ✅ en sağlam kurgu |
| L2 | Orkestrasyon — 0→10 adım + 3 kalıcı katman | oturum(lar) | Sıralı hat; dinamik modda **insan kapısı** | ✅ |
| L3 | Dairesel bağımlılık (deadlock) | çağrı içi | 3 adlandırılmış kırıcı: P0-4 / P0-5 / P0-5×P0-6 | ✅ testle kilitli |
| L4 | Hook geri beslemesi — `Stop` her turda | her asistan turu | 4 sönümleme aygıtı; asla bloklamaz | ✅ (H1 izleme) |
| L5 | Retry — OCR merdiveni, ZIP kurtarma, ad çakışması | ms–sn | Sabit merdiven / monoton ilerleme | ✅ kusur yok |
| L6 | Semantik — illiyette dairesellik | analiz | Renkli DFS — **advisory** | ⚠ bulguların odağı |
| L7 | Epistemik — dairesel doğrulama | doktrin | **Dış tanık** zorunluluğu (resmî okuyucu, bağımsız ölçüm) | ✅ |

**Kırıcı doktrininin beş invaryantı (koddan çıkarıldı):**
1. İstisna dardır, dışa açılmaz — kırıcı bayraklar yalnız in-process kwarg; CLI yüzeyi yok.
2. Atlama daima görünür — *sessiz atlama yasağı*.
3. Çöken kapı = atlanan kapı → FAIL-CLOSED; ama yalnız araç fiilen kullanılıyorsa (polarite doğru).
4. Throttle yalnız **basıma** uygulanır, **tespite** asla.
5. Deadlock yerine insan — PreToolUse `deny` değil `ask`.

P0-4'ün `gate_g_atla=True` bayrağı aynı zamanda karşılıklı in-process import'un **özyineleme sonlandırıcısı**dır;
`test_gate_g_dongu` kaynak taramasıyla (`"import subprocess" not in kaynak`) kilitler — refaktörle geri alınamaz.

---

## 3. GRAF KATMANI

### 3.1 Doktrinin şemaya çevrilmesi — kitin en özgün fikri

| Doktrin | Şema alanı | Yargı Pro ile doğrulanan karşılık |
|---|---|---|
| Conditio sine qua non / uygun illiyet / objektif isnadiyet | `illiyet_tipi` | — |
| İlliyetin kesilmesi (3 hâl, TBK) | `kesme_flag` | ⚠ cezada farklı işler (G10) |
| İspat yükü / karine | `dogrulama: teyitli\|iddia\|karine` | — |
| Perdeyi kaldırma / muvazaa | **köprü düğüm** (articulation point) | ✅ 11. HD: "yöneticilerinin veya kurucularının aynı olması" = organik bağ göstergesi |
| Usul rolü geçişleri | `usul_rolu` zorunlu | — |
| İlişki ↔ illiyet ayrımı | iki kenar kategorisi | ✅ Yargıtay'ın iki katlı testi (organik bağ + kötüniyetin somut ispatı) |

**Muris muvazaası ratio ↔ graf** (1. HD E.2012/14954): Yargıtay'ın dört ölçütü — bedel-değer farkı,
murisin makul nedeni, davalının alış gücü, beşeri ilişki — grafta **dört ayrı kenar**. Model doğru.

### 3.2 Sekiz dedektör — garanti sınıfı

| § | Dedektör | Garanti | Durum |
|---|---|---|---|
| 1 | Şema | Kısmî — zorunlu alanların bir kısmı | ⚠ G3 |
| 2 | Yetim düğüm | Tam — **ama delilde yanlış pozitif** | ⚠ G7 |
| 3 | Desteksiz kenar | Dar — beyan edilmemişi kaçırır | ⚠ G3 |
| 4 | Köprü düğüm | Tam — yaprak-komşusunu da işaretler, etiket dal-kilitli | ⚠ G8 |
| 5 | Çevrim | Varlık sağlam, **sayım eksik**, advisory | ⚠ G1, K2 |
| 6 | Kesme adayı | Tam | ✅ |
| 7 | Yük taşıyan kenar | Tam — çevrimde anlamsız | ⚠ G2 |
| 8 | Zincir güven | Advisory — köksüz grafta sessiz/yanlış beyan; beyan-yok ödüllü | ⚠ G2, G4 |

§6/§7/§8'in **hukuki isabeti** üç dalda da yüksekti: en zayıf halka olarak "tanık beyanına dayalı gizli
irade" (muvazaa), "tartışmalı doğrudan zarar bağı" (ticaret), "mağdur kusuru kesme adayı" (ceza) — tam da
Yargıtay'ın vurduğu yerler.

---

## 4. HOOK KATMANI

**Topoloji:** 5 kanca (`SessionStart` · `UserPromptSubmit` · `PreToolUse` · `PostToolUse` · `Stop`+`SessionEnd`)
→ tek sarmalayıcı `run-hook.cmd` (polyglot .cmd/bash; gerekçe: masaüstü hook'u kabuksuz koşturuyor, `||`
python'a argüman gidiyor → üç sahada sıfır ateşleme) → tek gövde `pipeline_kayit.py`.

**Kök keşfi** — beş kanallı aday listesi (`--kok` › payload `cwd` › `tool_input.file_path/files` → yukarı
yürüyüş › `CLAUDE_PROJECT_DIR` › CWD), **tümü** denenir. B-4 dersi: `SendUserFile` yolu `files` alanında;
okunmadığı için SUNUM KİLİDİ sessizce ölüydü.

**Dört sönümleme aygıtı — ölçüldü:**

| Aygıt | Ölçüm |
|---|---|
| `_hook_dedup_kisa_devre` | ikinci `SessionStart` aynı saniyede → çıktı yok ✓ |
| `_hook_postwrite_tetikle_mi` | dilekçe-şekilli dosya yoksa ağır gövde hiç çağrılmıyor ✓ |
| `_hook_cikti_degisti_mi` | 1. koşu 24 satır → 2. koşu 0 satır; **DURUM.md mtime yine değişti** ✓ |
| `INLINE_DENETIM_ZAMAN_SINIRI_SN = 2.0` | kaynak |

**Gürültü kısılıyor, körlük kısılmıyor** — mimarinin en olgun kararı. Hook nabzı (`.hook-son-iz.json`)
sessizlik ile ölümü ayırt ediyor. `ask` doktrini halkayı kilitlemiyor, avukatı halkaya sokuyor.
**Hook katmanında blokerlik düzeyinde kusur bulunmadı.**

---

## 5. KESİŞİM — kopuşların yeri

```
model grafı kurar → grafik_denetim --json <ad> → { arac, cevrimler, sema_hatalari, desteksiz_kenarlar }
        │                                                      │
        │                              pipeline_kayit._graf_yapisal_bosluk_uyarisi
        │                                  ① glob  *graf*.json        ← AD sözleşmesi (kırılgan)
        │                                  ② damga arac == grafik_denetim
        ▼                                                      ▼
   oa-illiyet/SKILL.md örneği:                            _oa/DURUM.md → hook_prompt → model
   --json _oa/cikti/01-illiyet-denetim.json   ← ①'e uymaz → HİÇ ULAŞMAZ
```

| Ölçüm (aynı graf, aynı bulgu) | DURUM.md'de |
|---|---|
| `01-illiyet-denetim.json` (SKILL.md'nin kendi örneği) | **0** |
| `01-illiyet-graf-denetim.json` | **1 — 🔴** |

Üç gerçek dosyada tekrar etti. Girdi dosyası ①'den geçip ②'de, çıktı ②'den geçecekken ①'de eleniyor →
**kapsama sıfır.** Üstüne `--json` köşeli parantezle opsiyonel — v0.5.8.4'ün "opsiyonel kapı = ateşlemeyen
kapı" dersi bir alt katmanda tekrar ediyor.

**Kök neden (dört oturumda değişmedi):** Pipeline/teslim katmanı fiziksel kanıta, exit koduna ve kilitli
teste bağlı. Graf katmanı **basılı metin** düzeyinde. Sistemin muhakeme çekirdeğine en yakın kapı, en zayıf
zorlamaya sahip olan — ve Yargı Pro teyidi modelin doğru olduğunu gösterdiği için, eksik zorlama **yanlış
değil doğru bir modeli** değersizleştiriyor.

---

## 6. SAHA SINAMASI — üç dal, özet

| | Muris muvazaası | Ticaret / perde | Ceza / taksir (müdafi) |
|---|---|---|---|
| Graf | 15 düğüm / 14 kenar | 13 / 10 | 14 / 7 |
| Teyit | 1. HD E.2012/14954 K.2013/3103 — **ALEYHE-AYIRT** | 11. HD E.2021/4234 K.2022/8380 — **LEHE, tam-metin** | 12. CD E.2015/3824 K.2016/2339 — **ALEYHE, tam-metin** |
| Ratio↔graf | 4 ölçüt = 4 kenar; **G3 boşluğu "beşeri ilişki" ölçütüne denk geldi** | köprü düğüm K = "aynı yönetici"; iki katlı test yapısal | **mağdur kusuru illiyeti kesmez**, kusur derecesini etkiler → G10 |
| Kapı testi | uydurma künye BLOK ✓ · DAMGA tahrifi BLOK ✓ · tam-metin şartı ✓ | kapı AÇIK (exit 0) ✓ · örtüşme sayacı yanlış "yüzeysel" (G11) | ALEYHE taslakta **BLOK** ✓ · **inline hızlı denetim kör → K3** |
| Graf kusuru | G3, G7 (6/6 delil yetim) | G4 (0.36 vs 0.80), G7, G8 (alacaklı "perde sinyali") | G7, G8 (ölen yaya "perde sinyali"), G9 (müdafiye "sağlamlaştır") |

**Ceza doktrin bulgusu:** Yargıtay 12. CD (2016, 2019, 2021, 2025, 2026 — tutarlı): yayanın kural ihlali
sürücüyü kusursuz kılmaz; **kusur derecesini ve cezayı** etkiler. Şemanın `kesme_flag: magdur_kusuru`
alanı medeni hukuktan (TBK haksız fiil) ödünç; ceza grafında müdafiyi on yıldır reddedilen bir savunmaya
yönlendirebilir. Muvazaada da "paylaştırma kastı" (1. HD'nin bozma gerekçesi) şemaya sığmıyor.

---

## 7. DİKEY İNİŞ — Denizli × Antalya × Yargıtay, özet

**Hipotez:** "Her üst karar, incelediği alt kararın künyesini içerir." **Sonuç: kata bağlı.**

| Kat | Metin indekste | Alt künye metinde | İniş |
|---|---|---|---|
| Yargıtay (hukuk, yeni format) | ✅ | ✅ başlıkta `MAHKEMESİ/SAYISI + İLK DERECE/SAYISI` | **en kolay** |
| Yargıtay (hukuk, eski) | ✅ | ✅ gövdede tarih+E+K | mümkün |
| Yargıtay (ceza, yeni) | ✅ | BAM ✅ · İDM **ilçe redakte, E/K yok** | BAM'a kadar |
| Antalya BAM (hukuk) | ⚠ ~2021+, kısmi | ✗ kendi dosyası `... Esas, ... Karar`; **emsal künye korunur** | kör |
| Antalya BAM (ceza) · Denizli İDM (tümü) | ✗ | — | yok |

**Denizli'nin kendi döngüleri** (gerçek, tam metin):
- **Konkordato (BAM 11. HD E.2022/1944):** İDM tasdik → BAM ret → Yargıtay 6. HD bozma → İDM uyma →
  davacı yine istinaf → BAM: "HMK m.373/4, kanun yolu temyizdir" → geri. Kırıcı: norm.
- **Görev ping-pong (BAM 4. HD E.2022/1902):** Sarayköy AHM (ATM sıfatıyla) ↔ Denizli ATM, ikisi de
  HSK 608'e dayanıyor. 17 ay sonra BAM: "gönderme kararı, istinaf kapalı, **merci tayini**." Kırıcı: dış
  hakem. ISTINAFHUKUK'ta en az 6 kopya (Çivril, Acıpayam, Sarayköy).
- **Muvazaa + şirket payı (BAM 1. HD E.2024/1078):** ATM görevsizlik → BAM KESİN (HMK m.362/1-a) →
  AHM'de yeniden; bir yılda sıfır esas.

Bunlar P0-4/5/6'nın hukuktaki ikizi: **iki kapı birbirini beklerse çözüm daha büyük halka değil,
halkanın dışından bir merci.** Sistem bunu kodda yapıyor; grafında ve kütüğünde modelleyemiyor (G12, K5).

`kanun_yolu_zinciri.py` (teslim edildi): dört üst metinde koştu, künyeyi ve **redakte bayrağını**
deterministik çıkardı, "ilk dereceye iniş mümkün mü" kararını mekanik verdi (1 EVET / 3 HAYIR).

---

## 8. NE ÇALIŞTI — ölçülmüş güçlü yanlar

| Mekanizma | Test | Sonuç |
|---|---|---|
| Teyit ritüeli (`teyit --damga`) | 3 gerçek karar, 3 damga sınıfı | tek komut → kütük + muhakeme kaydı + URL ✓ |
| **DAMGA çapraz kontrolü** | muhakeme kaydı elle LEHE yapıldı | BLOK — "HAYALET MUHAKEME, fail-closed" ✓ |
| **Uydurma künye kapısı** | sentetik `E.2099/1` | BLOK — çıplak atıf, TESLİM ENGELİ ✓ |
| **ALEYHE yasağı (m.6)** | ALEYHE karar savunmaya yazıldı | ritüelde uyarı + kapıda BLOK ✓ |
| Tam-metin okuma şartı (G6) | ilgili-kısım sınıfıyla teyit | "baştan sona okunduğu kanıtlanmadı" ✓ |
| Kapı AÇIK yolu | tam-metin + LEHE + URL + bağ | exit 0 ✓ |
| Redakte künye | E/K'sız `--sonuc` | RET, hiçbir şey yazılmadı ✓ |
| İNGEST-ÖNCE (P0-6) | 00-kunye.json yok | RET; `--serh` ile görünür geçiş ✓ |
| ELDEN (C5) | script izi yok | ELDEN; DURUM.md ayrı sayaç ✓ |
| **Fizik-vs-beyan** | teyit artefaktı var, adım 3 defterde yok | `[FİZİKSEL: artefakt VAR / beyan YOK ⚠]` ✓ |
| Gate G kırıcı | 37 test | geçti; subprocess yasağı kaynak taramasıyla kilitli ✓ |
| Hook dedup / ön-denetim / throttle / ask | sentetik dava klasörü | dördü de tasarlandığı gibi ✓ |
| Kesme adayı §6 · yük taşıyan §7 · en zayıf halka §8 | 3 dal | hukuken isabetli ✓ |

**Zorlama omurgası — teyit → damga → kapı — üç dalda ve iki kanun yolu katında fail-closed çalıştı.**

---

## 9. KONSOLİDE BULGU TABLOSU

*Önceki oturum kodları eşlemesi: B1→K1, B2→K2, B3→G2, B4→G1, B5→G6, B6→H1.*

### Kesişim (K) — katmanlar arası kopuş

| Kod | Ağırlık | Bulgu | Kanıt |
|---|---|---|---|
| **K1** | YÜKSEK | Graf bulgusu `DURUM.md`'ye ulaşmıyor: bekçi globu `*graf*.json` ↔ SKILL.md'nin belgelediği çıktı adı; girdi `arac` damgasında eleniyor → kapsama sıfır | 3/3 dosya, uçtan uca |
| **K2** | YÜKSEK | Çevrim/graf kapısı advisory (`exit 0`), hiçbir adımı bloklamıyor — "advisory kapı = olmayan kapı" tezine aykırı | koşu |
| **K3** | YÜKSEK | PostToolUse hızlı denetimi ALEYHE künyeli taslağı görmüyor (yalnız [N]/[L]); m.6 tespiti teslime gecikiyor | ceza, koşu |
| **K4** | YÜKSEK | Atıf tanıyıcı tarih-only / K-only / `YYYY/N-N sayılı` biçimlere kör → künyesiz atıf kapıyı geçiyor (`[G1] 0 atıf → AÇIK`); Yargıtay kendisi birleşik biçimi kullanıyor | ölçüm, 9 biçim |
| **K5** | YÜKSEK | Kütükte akıbet (kesinleşme/bozulma) alanı yok; arama `KESİNLEŞTİ/KESİNLEŞMEDİ` veriyor, ritüel almıyor; G5 yalnız yatay aşmayı bilir | grep 0, saha |

### Graf (G)

| Kod | Ağırlık | Bulgu | Kanıt |
|---|---|---|---|
| **G3** | YÜKSEK | Belgede "zorunlu" `dogrulama/dayanak_delil/norm` kodda denetlenmiyor; delilsiz illiyet 8 bölümü yeşil geçiyor; §3 yanlış beyan — **Yargıtay ölçütü** olan kenarda | muvazaa |
| **G7** | YÜKSEK | Delil düğümleri sistematik yetim (17/17): `yetim_dugumler` `dayanak_delil` okumuyor; gerçek boşluk (banka kaydı yok, EDR yok) gürültüde kayboluyor | 3/3 |
| **G10** | YÜKSEK | `kesme_flag` enum dal körü: cezada mağdur kusuru illiyeti kesmez (12. CD); miras'ta paylaştırma kastı, ceza'da izin verilen risk/kendi tehlikesine girme şemada yok | Yargı Pro |
| **G2** | ORTA-YÜKSEK | Çevrimde §7 sahte güven, §8 yanlış beyan ("illiyet kenarı yok" — oysa var; köksüz graf) | koşu |
| **G4** | ORTA-YÜKSEK | `guc` beyan-yok 0.8 > tartışmalı 0.4 → dürüstlük yarı puana düşüyor; aynı avukatın iki iddiasında ölçüldü | ticaret |
| **G8** | ORTA-YÜKSEK | Köprü dedektörü yaprak-komşusu/doğrusal düğümleri işaretliyor; etiket ticarete kilitli (alacaklı A, ölen yaya, BAM kararı "perde sinyali") | 3/3 + karar grafı |
| **G1** | ORTA | Renkli DFS çevrimleri eksiksiz saymıyor (`pipeline_kayit↔tam_tur` raporda yok); rapor minimal çevrim değil (A→B→C→B) | mimari graf |
| **G5** | ORTA | Mükerrer düğüm id sessizce yutuluyor; davacı buharlaştı, şema "bütün" dedi | koşu |
| **G6** | ORTA | `id` eksikse ham traceback; `rapor()` try/except yok; DFS derinlik sınırsız → çöken kapı = atlanan kapı (P1-12 sınıfı) | koşu |
| **G9** | ORTA | Taraf körlüğü — defter `--ceza mudafii` biliyor, dedektör bilmiyor; müdafiye "sağlamlaştır" | ceza |
| **G12** | ORTA | Şemada karar/mahkeme düğüm tipi ve kanun-yolu kenar semantiği (onadı/bozdu/kaldırdı/kesin) yok | iniş |
| **G11** | DÜŞÜK | Örtüşme sayacı `(1)…;(2)…;(3)…` biçimini görmüyor → yanlış "yüzeysel" uyarısı | ticaret |

### Hook / pipeline (H, P)

| Kod | Ağırlık | Bulgu | Kanıt |
|---|---|---|---|
| **P1** | ORTA | `--serh` tek bit; İNGEST-ÖNCE için verilen şerh ilgisiz C5 ELDEN düşürmesini de bastırıyor (`:1394 … and not serh_bayrak`) | koşu |
| **H1** | İZLEME | Hook geri beslemesinde sayaçlı sınır yok; sönümleme metin özdeşliğine bağlı → salınım olası | kaynak |
| H2 | DÜŞÜK | `[N] çıplak kısaltma 'SANIK'` — taraf etiketi kısaltma sanıldı | ceza |

### Kaynak / indeks (D) — araç dışı ama iş akışını belirleyen

| Kod | Ağırlık | Bulgu |
|---|---|---|
| **D1** | YÜKSEK | Redaksiyon asimetrisi: Yargıtay alt künyeyi korur; BAM kendi dosyasının alt/geçmiş künyelerini (ilçe dahil) redakte eder, emsal künyeyi korur → iniş BAM'da kör |
| **D2** | YÜKSEK | Kapsama: Denizli İDM (ATM/AHM/ACM) kararı Bedesten'de bulunamadı; ceza BAM/İDM korpusu yok; ISTINAFHUKUK Antalya ~2021+ |
| **D3** | YÜKSEK | `esas_no` BAM'lar arası tekil değil (6 BAM aynı E); `ictihat_ara`'da BAM/daire filtresi yok |
| D4 | BİLGİ | Arama indeksi karar tarihini 1 yıl yanlış gösterdi (01.03.2012 vs 2013); künye daima tam metinden |

**Toplam: 22 bulgu** (5 K · 12 G · 3 H/P · 3 D) + 1 bilgi.
**Ağırlık dağılımı:** 10 yüksek · 4 orta-yüksek · 6 orta · 2 düşük/izleme.
**Kategori dağılımı:** kusurların **%64'ü graf katmanında veya graf'ın diğer katmanlarla kesişiminde** — kök neden tezi sayısal olarak da tutuyor.

---

## 10. ÖNCELİKLİ REÇETE — 12 hamle, sıralı

*Efor: S = tek oturum · M = birkaç oturum (TDD, önce kırmızı). Her hamlede "nasıl doğrulanır" verilmiştir.*

| # | Hamle | Kapattığı | Efor | Doğrulama |
|---|---|---|---|---|
| **1** | `dilekce_denetim.hizli_denetim`'e **[F] hafif sürümü**: künye regex → kütükte DAMGA → ALEYHE ise inline bulgu (kütük yerel, 2 sn'ye sığar) | K3 | S | ALEYHE künyeli taslak PostToolUse'ta `[F]` bulgusu üretsin |
| **2** | Bekçiyi **ada değil damgaya** bağla: `glob("*.json")` + `arac == grafik_denetim`; `grafik_denetim` çevrim/şema hatasında **exit 3**; `rapor()` try/except + `DENETİM ÇÖKTÜ` damgası; SKILL.md'de `--json` **zorunlu** | K1, K2, G6 | S | SKILL örnek komutu birebir → DURUM.md'de 🔴 satır |
| **3** | `taslaktaki_atiflari_bul`'a üç desen: `<merci> … dd.mm.yyyy tarihli` · `<merci>'nin YYYY/N sayılı` · `YYYY/N-N sayılı` (→ E/K'ya ayır). İlk ikisi **"EKSİK KÜNYE" BLOK** | K4 | S | 9 biçimin 9'u tanınsın; tarih-only → BLOK |
| **4** | `teyit --akibet kesinlesti\|kesinlesmedi\|bozuldu\|kaldirildi\|geri-cevrildi --akibet-kaynak <künye>`; `bozuldu/kaldirildi`+LEHE → G5 mantığıyla BLOK; arama sonucundaki `kesinleşme` alanı otomatik aksın | K5 | M | bozulmuş BAM kararı LEHE ile dilekçeye giremesin |
| **5** | `yetim_dugumler`'e `dayanak_delil` referanslarını kat; anılmayan delili **ayrı sınıf** ("bağlanmamış delil"). Köprü testinde yaprak-komşusu/doğrusal iç düğümleri ele; etiketi tip-duyarlı yap (iki `tuzel_kisi` kümesini bağlayan `gercek_kisi` → perde; diğerleri nötr) | G7, G8 | S | 3 saha grafında delil yetim sayısı 17→2; alacaklı/yaya işaretlenmesin |
| **6** | İlliyet kenarında `dogrulama` **zorunlu**; §3 `dogrulama` yoksa **veya** iddia+delilsizse yakalasın; `GUC_VARSAYILAN = 0.4` | G3, G4 | S | meta verisiz kenar §1'de hata, §3'te boşluk; beyan-yok ≤ tartışmalı |
| **7** | `kesme_flag` **dal-ayrımlı**: `medeni:` mücbir/mağdur/üçüncü kişi · `miras:` paylaştırma_kasti/ivaz · `ceza:` izin_verilen_risk/kendi_tehlikesine_girme/hukuka_uygunluk; ceza dalında `magdur_kusuru` için "illiyeti kesmez — kusur oranı" notu. `grafik_denetim --taraf` (veya defterden `--ceza mudafii` oku) → "sağlamlaştır/çürüt" yönü | G10, G9 | M | ceza grafında mağdur_kusuru → uyarı metni; müdafi grafında yön tersine |
| **8** | Şemaya `tip: karar\|mahkeme`; kenar `tur: kanun_yolu` + `sonuc: onadi\|bozdu\|kaldirdi\|geri_cevirdi\|esastan_ret\|kesin`; `kanun_yolu_zinciri.py` → `oa-ictihat/scripts/` **iniş ritüeli**: kat başına kütük satırı `SEVİYE=BAM KÜNYE=redakte METİN=indekste-yok`; `ictihat_ara` sarmalayıcısında (BAM, daire) istemci-tarafı süzgeç | G12, D1, D2, D3 | M | 4 üst metinde çıkarıcı aynı sonucu versin; kütükte kat satırları |
| **9** | `--serh-kapi <ad>`: şerh yalnız adlandırılan kapıyı geçsin; ELDEN düşürmesi bağımsız kalsın | P1 | S | İNGEST-ÖNCE şerhli + script izi yok → ELDEN |
| **10** | `aile_dogrula.py`'ye iki yapısal kilit: (a) her SKILL.md örnek komutunun çıktı adı ↔ onu tüketen bekçi deseni; (b) `KANONIK` enum'ları ↔ doktrin dosyası dal başlıkları | K1 sınıfı tekrar | S | mevcut uyumsuzluk kırmızı; düzeltme sonrası yeşil |
| **11** | Küçükler: çevrimi minimal kırp + Johnson sayımı (G1); mükerrer `id` hata (G5); örtüşme sayacına `\(\d+\)` ve `;` (G11); `[N]`'de taraf etiketleri beyaz liste (H2); H1 için (dosya, kapı-sınıfı) sayacı, N≥3'te M7'ye yükselt | G1, G5, G11, H2, H1 | S | ilgili mikro-testler |
| **12** | `oa-usul`'a **Denizli notu**: HSK 608 (07/07/2021) — 01/09/2021 öncesi açılmış ilçe ATM-sıfatlı dosyada devir/görevsizlik değil doğrudan **merci tayini** talebi (17 ay kazandırır) | pratik | S | not eklendi; kişi/dosya verisi yok (m.7 uyumlu) |

**Önerilen sıra:** 1 → 2 → 3 (aynı hafta, her biri tek oturum, en yüksek getiri) → 5 → 6 → 9 → 10 → 4 → 7 → 8 → 11 → 12.
Hamle 1–3 tamamlandığında beş K bulgusunun üçü ve iki G bulgusu kapanır; anayasa m.6 ve halüsinasyon
kapısı **tam** hâle gelir.

---

## 11. AVUKAT KARARI BEKLEYEN

| # | Karar | Öneri |
|---|---|---|
| 1 | K2 — çevrim tespitinde kapı **sert** (adım-1 UYGULANDI bloklanır, `--serh` çıkışı var) mı, `--katı` bayrağıyla opsiyonel mi? | Sert — "advisory kapı = olmayan kapı" senin tezin |
| 2 | K3 — [F] hızlı kipe alınırsa bulgu modele geri akar ve "düzelt" döngüsü doğar; H1 sayacıyla birlikte mi gelsin? | Birlikte (N=3) |
| 3 | K4 — tarih-only atıf BLOK mu, "künyeyi tamamla" uyarısı mı? | BLOK — kapının görmediği atıf en tehlikelisi |
| 4 | K5 — akıbet kaynağı yalnız araç sonucu mu, avukat beyanı da kabul mü? | Araç birincil; beyan `--akibet-kaynak` ile ve görünür |
| 5 | G4 — beyan-yok ağırlığı 0.4 mı, ayrı "beyan-yok" sınıfı (§3'e boşluk düşer, JSON genişler) mi? | Ayrı sınıf — dürüstlük ölçütüne daha uygun |
| 6 | G7 — `dayanak_delil`'de anılmayan delil "yetim" (bloklamaz) mı, "bağlanmamış delil" ayrı sınıf mı? | Ayrı sınıf — oa-vakia yetim delil semantiğiyle hizalı |
| 7 | G10 — `kesme_flag` şeması **kırılsın** mı (dal-ayrımlı, geriye uyumsuz) yoksa enum korunup dal notu mu? | Kırılsın; eski graflar için göç scripti |
| 8 | G9 — taraf bilgisi CLI ile mi, defterden okumayla mı? | Defterden (tek kaynak), CLI override |
| 9 | G12 — şemaya karar/mahkeme tipi mi, `olay` + `tur` konvansiyonu mu? | Tip — karar grafı köprü/perde etiketinden muaf tutulabilir |
| 10 | İniş ritüeli oa-ictihat'a mı, oa-pipeline ARAŞTIRMA alt adımına mı? | oa-ictihat scripti; pipeline adım 3 kanıtı olarak tüketir |
| 11 | Ticaret modelleme — organik bağ ve perde için ayrı talep düğümleri şablona (M4) girsin mi? | Evet — Yargıtay iki yolu "alternatif değil, birlikte" sayıyor |
| 12 | Hamle 12 — Denizli-özel usul notunda mahkeme/HSK kararı adı geçmesi m.7 ile uyumlu mu? | Uyumlu — kamu kaynağı, kişi verisi değil |

---

## 12. SINIRLAR — dürüst beyan

- **Sentetik dosyalar:** üç dava klasörü sentetiktir; evrak külliyatı yok, `oa_ingest` koşmadı
  (İNGEST-ÖNCE kapısı şerhle geçildi — DURUM.md'de görünür).
- **Kapsam:** dal başına 1–2 karar tam metinle teyit (toplam 8); arama listesindeki diğer kararlar snippet
  düzeyinde okundu ve **hiçbiri teyitli sayılmadı**. Ceza doktrin sonucu 12. CD'ye dayanır; CGK düzeyinde
  ayrıca teyit edilmedi.
- **MCP:** 26 çağrı, 24 başarılı; 3. oturumda `ictihat_ara` iki kez onay alamadı (semantik aramayla
  ikame); 4. oturumda sorun yok.
- **Koşturulmayan hatlar:** UDF üretimi, OCR, `teslim_paketi`/makbuz (npx/tesseract yok) — o bölümler
  yalnız kaynak okumasına dayanır.
- **Kapsama iddiaları** (Denizli İDM yok, ceza BAM yok) bu oturumun sorgularına dayanır; "bulunamadı ≠ yok".
- **Çıkarıcı** regex tabanlı, 4 metinde doğrulandı; genelleme için daha geniş örneklem gerekir.
- **İniş UYAP'ta sürdürülmedi** — UYAP erişimi münhasıran avukata aittir (Layer 0).

---

## EK A — Kanıt indeksi

| Oturum | Artefakt | İçerik |
|---|---|---|
| 1 | `loop-analizi.md` | 7 döngü sınıfı, 5 invaryant, B1–B6 (→ K/G kodlarına eşlendi) |
| 2 | `graf-hook-analizi.md` | 8 dedektör tablosu, hook topolojisi, throttle/dedup/ask ölçümleri, K1/K2, G1–G6, H1 |
| 3 | `saha-sinamasi-raporu.md` | 3 dal, ratio↔graf tabloları, kapı testleri, K3, G7–G11, P1 |
| 4 | `dikey-inis-raporu.md` + `kanun_yolu_zinciri.py` | kapsama matrisi, 6 zincir, K4/K5, D1–D3, G12 |
| — | `status.md` | oturum kaydı (işlem zincirleri, karar noktaları) |

Sentetik test kökleri: `/tmp/saha/{muvazaa,ticaret,ceza}` (defter, kütük, muhakeme kaydı, DURUM.md),
`/tmp/dava` (hook ölçümleri), `/tmp/zincir` (iniş çıkarıcı ve karar grafları), `/tmp/gtest` (graf mikro-testleri).

## EK B — Yargı Pro'dan tam metniyle çekilen kararlar (8)

| Karar | Konu | Kullanım |
|---|---|---|
| Yargıtay 1. HD E.2012/14954 K.2013/3103 T.01.03.2013 | Muris muvazaası ispat ölçütleri; paylaştırma kastı | saha — ALEYHE-AYIRT |
| Yargıtay 11. HD E.2021/4234 K.2022/8380 T.28.11.2022 | Organik bağ ↔ perdenin çapraz aralanması | saha — LEHE, tam-metin |
| Yargıtay 12. CD E.2015/3824 K.2016/2339 T.17.02.2016 | Yayanın ani çıkışı — sürücü tali kusurlu, beraat bozuldu | saha — ALEYHE, tam-metin |
| Yargıtay 11. HD E.2020/5897 K.2021/6938 T.08.12.2021 | Denizli ATM → Antalya BAM 11. HD zinciri; geri çevirme | iniş Z1 |
| Antalya BAM 11. HD E.2022/1944 K.2022/1038 T.08.09.2022 (KESİNLEŞTİ) | Konkordato kanun yolu döngüsü; HMK m.373/4 | iniş Z2 |
| Yargıtay 12. CD E.2022/6726 K.2026/2388 T.09.03.2026 | Denizli ACM taksir zinciri; CMK m.286/2-c | iniş Z3 |
| Antalya BAM 1. HD E.2024/1078 K.2024/871 T.07.05.2024 (KESİNLEŞTİ) | Muvazaa + şirket payı; görev; HMK m.362/1-a | iniş Z4 |
| Antalya BAM 4. HD E.2022/1902 K.2023/130 T.02.02.2023 (KESİNLEŞTİ) | Sarayköy↔Denizli görev döngüsü; merci tayini | iniş Z5 |

*Yalnız arama başlığı/snippet düzeyinde görülen (teyitli SAYILMAYAN) kararlar:* HGK E.2023/1138 K.2025/287 ·
HGK E.2022/454 K.2023/1221 · 12. CD E.2018/528, E.2025/7568, E.2022/258, E.2021/10241, E.2019/11406 ·
1. HD E.2024/3160 K.2025/3027 (Z6 üç-kat başlığı), E.2023/2889, E.2022/7579, E.2018/5136, E.2026/800 ·
10. CD (Denizli AĞCM uyuşturucu zincirleri, çeşitli).

## EK C — Kısa terimler

**Damga:** LEHE / ALEYHE / ALEYHE-AYIRT / NÖTR — teyit ritüelinde kararın müvekkil yönünden nitelendirilmesi.
**Kütük:** `_oa/teyit/kunye-teyit.md` — append-only teyit satırları. **Muhakeme kaydı:** `_oa/cikti/*ictihat-muhakeme*.md`.
**Bekçi:** `pipeline_kayit` içinde `_oa/cikti/*.json` çıktılarını DURUM.md'ye taşıyan fonksiyonlar.
**Köprü düğüm / yük taşıyan kenar:** articulation point / bridge — kaldırılınca grafı bölen düğüm/kenar.
**İniş:** üst mahkeme metninden alt karar künyesini çıkarıp alt kata geçme. **Redakte:** metinde `...` ile silinmiş künye.

---

*Bu belge karar materyalidir, karar değildir. Nihai karar Av. Bayram Can Çapar'a aittir.*
*Müvekkil verisi işlenmemiştir; taraflar/olgular sentetiktir; içtihatlar gerçek ve resmî kaynaktan tam
metinle teyitlidir; mahkeme ve HSK kararı adları kamu bilgisidir (anayasa m.6–7).*

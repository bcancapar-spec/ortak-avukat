# Ortak Avukat — Türk Hukuku Co-Counsel Sistemi

**Sürüm:** 0.3.20 (metodoloji v3.20) · **Yazar:** Av. Bayram Can Çapar · **Kapsam:** Türk hukukunun tamamı

> **© 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).** Fikri mülkiyet ile mali/manevi haklar münhasıran hak sahibine aittir; izinsiz çoğaltma/dağıtma/türev yasaktır. Bkz. depo kökündeki [LICENSE](../../LICENSE) ve [NOTICE](../../NOTICE).

Türk hukukunda kıdemli bir **Ortak Avukat (Co-Counsel)** kimliğiyle çalışan, İlk İlkeler (First Principles) ve **illiyet bağı** odaklı derin muhakeme yürüten bir **metodoloji sistemidir**. Sistem kişilere değil yönteme bağlıdır: gerçek pratikten doğan düşünce metodunu, doğrulanmış içtihada ve deterministik denetim scriptlerine oturtur.

Bu eklenti, **çekirdek `ortak-avukat` + 19 `oa-*` parça = 20 skill**'i tek pakette toplar. Mimari kasıtlı olarak **"Lego"** — her parça bağımsız yüklüdür ve tek başına çalışır; `oa-pipeline` bunları uçtan uca orkestrasyona bağlar.

## Yargı Pro bağlantısı — ÖNCE bunu yapın

Ailenin içtihat, mevzuat ve kurum kararı doğrulaması **Yargı Pro** adlı MCP sunucusuna dayanır. Yeteneklerin verimli çalışması için bu bağlantı **zorunludur**. Claude Code'da bağlayın:

1. Claude Code → **connectors** (bağlayıcılar) bölümünü açın.
2. Yeni bir MCP sunucusu ekleyin; adını **Yargı Pro** koyun.
3. Adres olarak şunu girin:

   ```
   https://yargi.betaspacestudio.com/mcp
   ```

4. Kimlik doğrulama (OAuth) akışını tamamlayın.

Komut satırını tercih ederseniz:

```bash
claude mcp add --transport http "yargipro" https://yargi.betaspacestudio.com/mcp
```

Yargı Pro; geniş içtihat arşivi, semantik arama, yüksek limit/tam metin ve ek kurum kararlarını (Rekabet, KVKK, Sayıştay, BDDK, KİK, Uyuşmazlık, Emsal/UYAP, GİB özelge) sağlar. Bağlantı olmadan aile "elden-MCP-teyitli" moda düşer ve künye doğrulaması yapamaz — bu, sistemin **halüsinasyonsuz** çalışma güvencesini zayıflatır.

> Ayrıca **Mevzuat MCP** (norm), **Literatür/DergiPark** ve **YÖK Tez** (doktrin) bağlıysa doğrulama zinciri tamdır. Bu paket hiçbir MCP kimlik bilgisi içermez; sunucular kendi ortamınızda bağlanır (gizlilik ilkesi).

## Kurulum

**GitHub marketplace üzerinden (önerilen):**

```
/plugin marketplace add <github-kullanıcı>/ortak-avukat
/plugin install ortak-avukat@ortak-avukat
```

**`.plugin` dosyasıyla:** paketi sohbete bırakın; önizlemeden inceleyip onay düğmesiyle kurun. 20 skill birlikte yüklenir.

## Mimari

- **Çekirdek (`ortak-avukat`):** Varsayılan çalışma kimliği ve orkestra şefi. Çağrıldığında aileyi devreye alır.
- **Fonksiyonel parçalar:** Akışın adımları (alım → konumlama → araştırma → olgu/delil → kıyas → strateji → antitez → yazım → kontrol → kapanış).
- **Kesişen katmanlar:** `oa-usul` (usulün esasa takaddümü), `oa-illiyet` (nedensellik grafı) ve `oa-gizlilik` (Layer 0 — her dış-araç çağrısını süzer) her aşamayı sarar.
- **Ceza dalı:** `oa-mudafii` (sanık/şüpheli savunması) ve `oa-musteki-vekili` (iddia/şikâyet) aynanın iki yüzü.
- **Determinizm:** Kritik parçalar, model muhakemesini denetleyen Python scriptleri taşır (süre hesabı, illiyet grafı, antitez matrisi, usul matrisi, kıyas denetimi, sözleşme kloz denetimi vb.).

## Parçalar (20)

| Skill | Rol |
|---|---|
| [`ortak-avukat`](skills/ortak-avukat/) | Çekirdek kimlik + orkestra şefi (varsayılan çalışma modu) |
| [`oa-pipeline`](skills/oa-pipeline/) | Uçtan uca orkestrasyon (MANİFEST→…→KAPANIŞ); "Başbakan" icra+denetim |
| [`oa-interview`](skills/oa-interview/) | İlk inceleme / mülakat — maddi gerçek, belge, süre, hedef, zaaf toplama |
| [`oa-alan`](skills/oa-alan/) | İhtisas dairesi konumlama (Yargıtay/Danıştay/İstinaf) + HSK iş bölümü |
| [`oa-illiyet`](skills/oa-illiyet/) | Nedensellik / ilişki / illiyet grafı (kesişen katman) |
| [`oa-vakia`](skills/oa-vakia/) | Vakıa/delil yönetimi — kronoloji + iddia↔delil matrisi + ispat boşluğu |
| [`oa-ictihat`](skills/oa-ictihat/) | İçtihat/mevzuat/doktrin araması (Yargı Pro, AYM, Mevzuat, Literatür, YÖK Tez) |
| [`oa-kiyas`](skills/oa-kiyas/) | Açık kıyas / hukuki silojizm (büyük önerme → küçük önerme → sonuç) |
| [`oa-strateji`](skills/oa-strateji/) | Yol seçimi — dava/sulh, kanun yolu, maliyet-fayda, dürüst olasılık |
| [`oa-antitez`](skills/oa-antitez/) | Antitez / kritik / çökertme motoru (durum farkındalığı + sağlamlık) |
| [`oa-usul`](skills/oa-usul/) | Usul hukuku (HMK/İYUK/İİK/CMK/6216/7201/492 + özel usuller); kesişen katman |
| [`oa-sure`](skills/oa-sure/) | Süre / zamanaşımı / hak düşürücü süreler (usul + maddi hukuk); nöbetçi |
| [`oa-dilekce`](skills/oa-dilekce/) | Dilekçe & mütalaa yazımı (dava/cevap/istinaf/temyiz/AYM başvuru) |
| [`oa-sozlesme`](skills/oa-sozlesme/) | Sözleşme tahriri, inceleme/redline, kloz kapsam denetimi |
| [`oa-kontrol`](skills/oa-kontrol/) | Teslim öncesi denetim — atıf/künye doğruluğu + usul/esas + zaaf protokolü |
| [`oa-mudafii`](skills/oa-mudafii/) | Ceza müdafiliği (sanık/şüpheli savunması) |
| [`oa-musteki-vekili`](skills/oa-musteki-vekili/) | Müşteki/mağdur vekilliği (iddia/şikâyet) — savunmanın aynası |
| [`oa-gizlilik`](skills/oa-gizlilik/) | Gizlilik / meslek sırrı / UYAP koruma (Privacy Layer 0) |
| [`oa-usta`](skills/oa-usta/) | Meta / skill-damıtma (Çırak öğrenme döngüsü) |

## Anayasal ilkeler (özet)

Aile, tüm parçalara işlenmiş ortak bir "anayasa" ile çalışır: aktif çıkarım (edilgen olmama), usulün esasa takaddümü, olguda sıfır üretim / yöntemde serbest doğaçlama, zorunlu tam-tur orkestrasyon, çaba ve kalite standardı (maliyet tasarrufu asla hedef değil), müvekkil-aleyhi dış çıktı yasağı (iç analizde dürüst raporlama), evrak bütünlük protokolü ve yerel hafıza (`_oa/` çalışma evrakı).

## Sürüm notu

Tam değişiklik günlüğü [`skills/ortak-avukat/references/degisiklik-gunlugu.md`](skills/ortak-avukat/references/degisiklik-gunlugu.md) dosyasındadır. v3.20'de dağıtım/dokümantasyon katmanı ve "Yargı Pro" isim tutarlılığı eklendi; metod ve script determinizmi değişmedi.

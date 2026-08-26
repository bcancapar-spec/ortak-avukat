# TOKEN VE VERİM ÖLÇÜMLERİ

> Belgeli saha koşularının ölçülmüş token/süre/verim kayıtları. Sayılar
> beyan değil ölçümdür; ölçüm yöntemi en başta açıklanır. Dosya kimlikleri
> anayasa m.7 gereği yalnız saha etiketiyle anılır.

## Ölçüm yöntemi — iki sayaç, iki ayrı gerçek

- **Üretim tokeni (bu belgedeki esas ölçü):** oturum transkriptindeki her
  model çağrısının çıktı-token alanlarının toplamı — düşünme blokları ve
  araç çağrıları dahil, modelin fiilen ürettiği her şey.
- **Uygulama sayacı:** Claude Code arayüzünün gösterdiği sayı; bağlam/özet
  ekonomisini yansıtır ve üretimden KÜÇÜKTÜR. Sahada ölçülen oran: arayüz
  sayacı, gerçek üretimin kabaca 1/6 – 1/8'i (307: arayüz 60k iken üretim
  ~489k; 923: arayüz 56k iken üretim ~359k). İki sayacı karıştırmamak
  karne disiplininin parçasıdır.
- Süreler transkript zaman damgalarından; dilim eğrileri 5 dakikalık
  pencerelerle hesaplanır.

## Koşu tablosu (belgeli koşular)

Süre sütunu iki türdür: **iş süresi** (kesintisiz koşularda, dakika dakika
ölçülü) ve *duvar saati* (♦ işaretli — oturumun ilk-son kaydı arası; molalar
dahil olduğundan iş süresinden büyüktür).

| Koşu | Süre | Üretim tokeni | Not |
|---|---|---|---|
| İlk tam koşu (istinaf, ~200 evrak) | 49 dk | **45,6k** | Kıyas: aynı iş, evrakı görüntü olarak yükleyen eski usulde **1,2M+** token — fark **~26×** ([SAHA-SONUCU.md](SAHA-SONUCU.md)) |
| 447 (vergi) | ♦ | **~604k** | Hook katmanının sessiz ölümünün teşhis koşusu |
| 372 (aile/mal rejimi) | ♦ | **~1,24M** | Elle-UDF krizi + 5 kollu adli analiz bu koşudan çıktı |
| 346 (bilirkişi itirazı) | ♦ ~8,5 saat | **~1,17M** | [G6] kuralının doğduğu koşu |
| 777 (banka/kefalet, ikinci cevap) | ♦ | **~1,50M** | İçerik reddi + yeniden inşa dahil; ilk 23/11 LEHE/ALEYHE triyajı |
| 307 (tasarrufun iptali, ikinci cevap) | 161 dk | **~822k** | 271 araç çağrısı (161 kabuk + 69 hukuk MCP); 45 karar tam metin; 154. dk'da bağlam sıkışması |
| 923 (vergi/gümrük, çift dilekçe) | 57 dk (yeşile kadar) | **~360k**; kapanış oturumuyla **~930k** | Tek cümlelik prompt, sıfır müdahale; ilk ORGANİK yeşil makbuz |
| 1865 (soruşturma-izni itirazı, 2 müvekkil) | çok oturumlu, ~2 gün ♦ | oturum başına 0,4M–1,14M; **toplam ~4,3M** | 5-6 paralel oturum; 34 TIFF'in tamamı OCR'dan geçti |

*447/372/777 ölçümleri koşu sonrasında hayatta kalan transkriptlerden geriye
dönük sayılmıştır (2026-08-27); o koşular canlı token-izlemesiz yapılmıştı —
izleme disiplini 307 ile başladı.*

## 307 dilim eğrisi — bir koşunun anatomisi

161 dakikalık koşunun 5'er dakikalık üretim dilimleri iki fazı ayırt
ettirir (örnek kesit):

| Dilim | Üretim | Yorum |
|---|---|---|
| 0-5 dk | 26k | açılış + devralma |
| 5-10 dk | 69k | keşif zirvesi (yüksek önbellek okumalı) |
| 20-25 dk | 71k | yazım fazı başlangıcı (önbellek okuma 7M→0,8M düştü) |
| 25-30 dk | 70k | saf yazım |
| 40-45 dk | 39k | düzeltme turları |

Ortalama tempo ~8,1k token/dk; koşu boyunca boşta dilim yok denecek kadar
az. Ders: uzun koşuda asıl risk token değil **bağlam sıkışması** — 307'de
sıkışma bitişe 7 dakika kala geldi ve zarar vermedi; daha büyük dosyada
muhakemenin ortasına denk gelebilir (okuma işinin destelenmesi bu yüzden
bir "hafıza yatırımı"dır).

## Diğer ölçülmüş kalemler

### Geliştirme tarafı ölçümleri (saha değil, sürüm üretimi)

Yöntemin kendisi de token yer; şeffaflık gereği kaydı:

- **Karne adli analizi (307):** 3 kol + sentez = 4 ajan, **~566k** token.
- **v0.5.10 tasarım paneli:** 5 lens + 5 çürütücü + sentez = 11 ajan,
  **~1,43M** token (yapısal sıçrama tartışması dahil).
- Bir sürümün tam laboratuvar döngüsü (testler + süit koşuları + CI) bunlara
  ek; süit tek koşusu makine-yerelde ~7-10 dakikadır, model tokeni yemez.

- **Alt-ajan sabit maliyeti:** iki işlem yapan minik bir alt-ajan **~63k**
  token yedi (her ajan doğuşta tüm kurulumu yükleniyor). Sonuç: karar-başına
  ajan ekonomik değil; ajan kullanılacaksa deste (batch) gerekir.
- **Ekonominin kaynağı:** kazanç, evrakı görüntü yerine **bir kez metne
  indirip** her adımda o metni seçici okumaktan gelir (Gate A-G okuma
  ekonomisi). Muhakemeden hiçbir koşuda kısılmamıştır — 1,68M karakterlik
  bir külliyat (~561k token eşdeğeri metin) tek sefer çıkarılıp defalarca
  kullanılmıştır (307 eski korpus ölçümü).
- **Yeniden-indirme koşulu:** dosya UYAP'tan baştan indirildiğinde eski
  önbellek adlarla örtüşmeyebilir (307: 209 dosyada 0 ad kesişimi) —
  o koşuda ekonomi kalemi "ölçüm dışı" damgalanır; sistemin çalışması
  ölçülür, tokeni değil.

---
*Yeni koşuların ölçümleri bu dosyaya eklenir. Karne bağlantıları:
[SAHA-DENEYLERI.md](SAHA-DENEYLERI.md) · [KARNE-307.md](KARNE-307.md) ·
[KARNE-1865.md](KARNE-1865.md).*

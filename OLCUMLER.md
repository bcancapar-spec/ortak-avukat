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

| Koşu | Süre | Üretim tokeni | Araç çağrısı | Not |
|---|---|---|---|---|
| İlk tam koşu (istinaf, ~200 evrak) | 49 dk | **45,6k** | — | Kıyas ölçümü: aynı iş, evrakı görüntü olarak yükleyen eski usulde **1,2M+** token — fark **~26×** ([SAHA-SONUCU.md](SAHA-SONUCU.md)) |
| 307 (tasarrufun iptali, ikinci cevap) | 161 dk | **~822k** | 271 (161 kabuk + 69 hukuk MCP) | 45 karar tam metin okundu; 154. dakikada bağlam sıkışması (bitişe 7 dk kala) |
| 923 (vergi/gümrük, çift dilekçe) | ~70 dk | **~400k** | 100+ | Tek cümlelik prompt, sıfır müdahale; ilk ORGANİK yeşil makbuz |
| 1865 (soruşturma-izni itirazı, 2 müvekkil) | çok oturumlu, ~2 gün | oturum başına 0,4M–1,13M; **toplam ~4M** | 500+ | 5-6 paralel oturum; 34 TIFF'in tamamı OCR'dan geçti |

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

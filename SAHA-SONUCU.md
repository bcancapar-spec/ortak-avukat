# SAHA SONUCU — Tek Prompt, Gerçek İstinaf Dosyası (2026-08-07)

> © 2026 Av. Bayram Can Çapar. Dosya kimliği anayasa m.7 (Av.K. m.36 · KVKK)
> gereği anonimdir: gerçek, derdest bir hukuk istinaf dosyası — burada
> yalnız ölçüm yaşar. Ölçüm ortamı: **Claude Fable 5 (max efor)**, Claude
> Code masaüstü, Windows 11, eklenti v0.5.6.1, **müdahalesiz koşu** —
> avukat tek bir doğal-dil prompt yazdı, akışa bir daha dokunmadı; sistem
> soru da sormadı (tek prompt → teslim edilebilir çıktı).

## Ölçülen sayılar

| Metrik | Değer |
|---|---|
| Külliyat | **~200 evrak** (193 dosya + EYP içleri = 202 işlem birimi) · 45 MB · 17'si OCR |
| Prompt | **1** (doğal avukat dili; hiçbir parça/komut adı anılmadı) |
| Uçtan uca süre | **49 dk 17 sn** (ingest → araştırma → taslak → UDF) |
| Toplam token | **45,6k** |
| Evrak başına | ≈ **226 token/evrak** |
| Ara verim | 15. dk'da 12,5k — ingest script işi, model beklemede |
| Çıktı | 36 KB / 11 bölümlü istinaf ek beyanı + **geçerli .udf** + iç risk cephaneliği |
| İçtihat | 11 karar + 3 norm — tümü MCP'den teyitli, kütük + ham döküm izli |
| Olgu sadakati | Örneklem 5/5 kaynağa izlendi (bilirkişi değeri, tanık ikrarı, tedavül bedeli, pay oranı, el yazılı belge alıntıları) — **uydurma: 0** |
| Aleyhe sızıntı | 0 — iki aleyhe içtihat damarı tespit edildi ve **dilekçeye yazılmadan** iç cephanelikte tutuldu (m.6) |
| Eksik-evrak dürüstlüğü | İndirilemeyen 4 evrak (tebligat + banka ekstresi dâhil) kullanıcıya **kendiliğinden** raporlandı |

**Bağlam:** ailenin eski koşullarında yalnız analiz aşaması için 1,2M+ token
gözlemlenmişti; bu koşu uçtan uca 45,6k ile kapandı — **~26× mertebesinde
tasarruf** (şerh: farklı dosyalar, bire bir kıyas değil; mertebe bilgisidir).
Tasarrufun kaynağı okuma ekonomisi: evrak görüntü olarak modele hiç girmedi,
deterministik çıkarım scripti metne indirdi, model ucuz metinden seçici okudu.

## Dürüst karne

**Verim ve muhakeme kaybı çok azdı; çıktı profesyonel sayılır düzeydeydi** —
istinaf ek beyanı, karşı tarafın kendi dilekçesindeki ikrarları yakalayan,
mülga saklı-pay hükmünü işleyen, bilirkişi değerleme yöntemindeki çıplak
mülkiyet/tam mülkiyet hatasını Harçlar K. m.64 ölçüsüyle çökerten, yemin
usulünü iki yönlü işleyen bir kurgu taşıyordu ve avukat incelemesinden geçti.

Kayıplar da ölçüldü ve v0.5.7'ye dönüştü:

1. **Bayat-tohum bulaşması (ana bulgu):** model, araç kopyalarını yüklü
   eklentiden değil komşu dava klasöründen aldı — 20/20 kopya eski nesildi;
   güncel kapılar (makbuz/sha, OCR nöbetçisi, DAMGA, KAYNAK-URL) o koşuda
   fiilen kapalıydı. → v0.5.7: bayt-karşılaştırmalı **bayat-araç aşısı** +
   taze-kaynak şartı.
2. İlk-inceleme soruları atlandı (tek-prompt akışın bedeli); kayıt geriye
   dönük ve törensel atıldı. → izlemede; zorlama katmanı taze araçla döner.
3. Teyitli kararların bağlantıları dilekçeye işlenmedi (bayat araç
   `--kaynak-url`'i bilmiyordu). → v0.5.7: **[G4] bağlantı tutarlılık kapısı**
   (uydurma link = teslim engeli; kayıtlı-ama-işlenmemiş link = görünür uyarı).

## Çözülmemiş kalan: UDF çevriminin oturum bağımlılığı

md → HTML → UDF akışının kanonik yazıcısı (`html2udf`) barındırılan hesaba
bağlıdır; bu koşuda model önce yerel motorla üretti, sonra kendini düzeltip
resmî yazıcıyla yeniden üretti — iki çıktı da mekanik kapıdan ve resmî
okuyucu round-trip'inden (13/13 çapa) geçti. v0.5.7 bu gerçeği ikili yapıya
bağladı: kanonik yol değişmedi; `--yerel-motor` yalnız açık bayrakla,
zorunlu mekanik kapı ve "UYAP editöründe görsel teyit ZORUNLU" şerhiyle
çevrimdışı yedek oldu (`oa-dilekce/references/udf-ic-yapi.md`). UYAP
editöründe uçtan uca canlı teyit, sıradaki saha adımıdır.

## Tek cümlelik sonuç

**Tek prompt + metodoloji ailesi + Fable 5 max:** ~200 evraklık gerçek bir
istinaf dosyası, 49 dakikada ve 45,6k token'la, kaynak-izli ve teslim
edilebilir bir ek beyana dönüştü — muazzam token tasarrufu, ölçülebilir
düzeyde küçük muhakeme kaybıyla; kalan tek yapısal bağımlılık UDF yazıcısının
oturumudur.

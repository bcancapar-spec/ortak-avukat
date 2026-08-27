# Saha Karnesi — 1865 sahası (v0.5.10 → v0.5.11)

**İş:** idari yüksek yargı nezdinde soruşturma-izni itirazı; iki müvekkil,
iki ayrı itiraz dilekçesi + çelişki/tutarsızlık raporu.
**Tarih:** 25-26.08.2026 · **Biçim:** ÇOK OTURUMLU (aynı dava klasöründe 5-6
paralel oturum) · **Deney sınıfı: MÜDAHALELİ-YETKİLİ** (avukat, gözcüye koşu
içi onarım yetkisi verdi; iki müdahale yapıldı ve ikisi de kayıtlı).

## 0. Baş cümle

Koşu taze yeşil makbuzla ve eksiksiz kapanış ritüeliyle bitti; v0.5.10'un üç
onarımı ilk gerçek sınavında doğrulandı. Ama karnenin asıl değeri kusur
tarafında: **777'den beri üçüncü kez nükseden gerçek düşman adlandırıldı**
(uygulamanın rpm anlık-görüntüsünden bulaşan bayat araç nesli) ve tek
seferlik onarımın ona YETMEDİĞİ ölçüldü.

## 0.5 Token ölçümü

Toplam üretim **~4,3M token** (5-6 paralel oturum; oturum başına 0,4M–1,14M;
duvar saati ~2 gün). Yöntem ve tüm koşuların tablosu: [OLCUMLER.md](OLCUMLER.md).

## 1. Çalışan taraf

- **v0.5.10 canlı doğrulama:** FİLO-TAZELİK kapısı yeşil makbuzun içinde
  koştu; 40-UYAP kopyaları mühürleriyle gitti; çift-uzantı üretimden
  kayboldu; makbuz 6 teslim-sınıfı ürünü mühür durumlarıyla kapsadı.
- **Mühür-kırık penceresi dakikasında yakalandı** (307'de 68 dk görünmezdi)
  ve teslimden önce sistemce kapatıldı — taze yeşil, gerçek zincirle kesildi.
- **Denetçi-denetlenen ayrımı hayat kurtardı:** hook'lar kurulu kanaldan
  koştuğu için kit bulaşması denetçiyi körleştiremedi; bulaşma bu sayede
  görüldü.
- **Kapanış ritüeli gerçek iş üretti:** kimliksiz ders damıtması (7+6+4
  örüntü), devir paketleri, türetilmiş DURUM.md; eksik kalan tek iş
  (merci kararı dönünce ders tamamlama) deftere DÜRÜSTÇE "asenkron" yazıldı.
- **[G6] disiplini çok-oturumda korundu:** kararlar tam metinle okunup
  damgalandı; araştırma oturumu kütüğe toplu damga bastı.

## 2. Kusurlar — ağırlık sırasıyla (v0.5.11'in hammadesi)

| # | Kusur | Ölçüm |
|---|---|---|
| T1 | **rpm bulaşması nüksediyor** — onarılan kit, uygulamanın rpm anlık-görüntü yolundan 9 dk sonra ESKİ nesille geri ezildi (777'den beri 3. nüks) | çekirdek üç script 14-20KB erken-nesil kopyayla ezildi; kaynak yolu transkriptte |
| T2 | **Uyarıya itaat yok** — bayat uyarısı turlarca görmezden gelindi; hizaya getiren hep teslim duvarının RED'i oldu | 12 uyarı ↔ tek onarım anı |
| T3 | **Söz-müdahalesi zayıf, dosya-müdahalesi güçlü** — oturuma mesaj kuyrukta ezildi; doğrudan dosya onarımı + salt-okunur koruma tuttu | onarım→9 dk'da ezilme; koruma→sıfır ezilme |
| T4 | **Çok-oturum sözleşmesi yok** — kit ezme yarışı, sahipsiz makbuz, fiilen devre dışı tek-oturum kilidi | 5-6 paralel oturum, ortak `_oa` |
| T5 | **Bayat karşılaştırıcı yön bilmiyor** — kit kanaldan YENİYKEN de "bayat" bağırdı; gürültü gerçek uyarının itibarını yedi | uyarıların ~⅓'ü yanlış yönlü |
| T6 | Sözleşme-dışı typo dizini (`metin-sororn` sınıfı) sessizce doğdu; künye bir süre yanlış dizinde yaşadı | dizin + içinde künye/INDEX |
| T7 | Künye kurulmadan araştırma derinleşti (MANİFEST sırası) | ilk 30 dk: künye yok, 11+ içtihat çağrısı |
| T8 | Gözcü, makbuz TAZELENMESİNİ ayırt edemedi (varlık-bazlı sensör) | 21:11 taze yeşili kaçırdı (gözcü tarafı; plugin dışı) |

## 3. Müdahale kaydı (yetkili, ikisi de defterde/transkriptte izli)

1. **Söz-müdahalesi:** taklit/bayat çekirdeğin kaynaktan kopyalanması talimatı
   → işlendi ama 9 dk sonra rpm kopyasıyla geri ezildi (T3'ün ölçümü).
2. **Dosya-müdahalesi:** gözcü üç çekirdeği v0.5.10 deposundan doğrudan
   onardı + salt-okunur yaptı + üç oturuma yasak bildirimi → kalıcı tuttu;
   sistem sonrasında kendi başına taze yeşile ulaştı.

Ders: müdahalenin de "model kurar, script denetler" simetrisi var — gözcü
sözle değil dosya sistemiyle müdahale etmeli.

## 4. Dürüstlük kayıtları

- Gözcünün ilk teşhisi ("model elle taklit yazdı") YARI YANLIŞTI — kazı,
  dosyaların rpm anlık-görüntüsünden kopyalanmış gerçek-ama-eski nesil
  olduğunu gösterdi. Gözcü hükümleri de çürütülebilirdir.
- İçerik hükmü (dilekçelerin ve çelişki raporunun avukat kabulü) bu karne
  yazılırken kaydedilmemişti — boşluk bilerek boş.
- n=1: tek dosya, tek koşu; sayılar gözlemdir, kanıt değil.

## 5. v0.5.11'e giden onarımlar

T1→P0-1 rpm karantinası ('ask') · T3→P0-2 kilitli çekirdek (salt-okunur +
'ask') · T5→P1-3 yönlü tazelik (bayat/kanaldan-yeni/özdeş) · T4→P1-4a oturum
damgası + taze-oturum uyarısı (kilit sahipliği bilinçli olarak v0.5.12'ye) ·
T6→P2-5 · T7→P2-6 · T8→gözcü v7 (depo dışı). T2'nin tedavisi daha sert uyarı
değil: uyarıyı azalt-doğrula (P1-3) + itaate muhtaç olmayan koruma (P0'lar).

---
*Yöntem: üç kaynaklı canlı gözlem (dosya sistemi + transkript + defter) +
yetkili müdahale kaydı. Dosya kimliği m.7 gereği yalnız saha etiketiyle.*

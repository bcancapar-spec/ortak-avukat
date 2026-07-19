# "İlliyet / Bağ Haritası" Çıktı Bloğu — oa-illiyet referansı

Bu blok, illiyet analizini içeren her esaslı çıktıya (dilekçe analizi, dosya
değerlendirmesi, mütalaa) eklenir. `oa-vakia`, `oa-dilekce`, `oa-antitez` bu bloğu
üretir. Amacı: bağ ve neden-sonuç yapısını avukatın tek bakışta görebileceği
standart bir görünüme indirgemek.

## Şablon

```
## İlliyet / Bağ Haritası

### Taraflar ve roller
- [tip] Ad — usul rolü (ilgili kanun/evre)
  (her gerçek kişi için rol zorunlu: borçlu/sanık/katılan/davacı/...)

### İlişki kenarları (statik bağ — kim kime nasıl bağlı)
- Ad —[ilişki türü]→ Ad   [doğrulama: teyitli/iddia/karine]  (norm)
  ⚠ desteksiz ise işaretle → oa-vakia ile delil tespiti

### İlliyet kenarları (neden-sonuç)
- Olay/fiil —[sebep_zarar/fiil_netice]→ sonuç
  tip: uygun illiyet / objektif isnadiyet · güç: ...
  ⚠ KESME ADAYI varsa: mücbir sebep / mağdur kusuru / üçüncü kişi kusuru

### Boşluk / risk denetimi (grafik_denetim.py çıktısından)
- Yetim düğüm: ...
- Köprü düğüm: ... → muvazaa / perdeyi kaldırma sinyali (karşı tarafın hedefi)
- Yük taşıyan kenar: ... → ispatlanmazsa zincir kopar (oa-strateji önceliği)
- Desteksiz kenar: ... adet → oa-vakia

### oa-antitez beslemesi
- Karşı tarafın kuracağı kesme/savunma: ...
- Çürütme dayanağı: [oa-ictihat ile aranacak — somut içtihat]
```

## Görsel (opsiyonel)

Karmaşık graflar için Mermaid diyagramı üret; kesme noktalarını ve köprü düğümleri
ayırt edilir biçimde göster:

```
graph LR
  ahmet[Ahmet Y. - borçlu] -->|ortaklık TTK m.195| xltd[X Ltd.]
  xltd -.->|zilyetlik İİK m.97 - DELİLSİZ| mal[Haczedilen mal]
  haciz[Haciz işlemi] ==>|sebep-zarar / KESME: 3. kişi kusuru| mal
```

Kesik çizgi (`-.->`) = desteksiz/zayıf bağ; kalın ok (`==>`) = kesme adayı taşıyan
illiyet. Köprü düğümü not düş.

## Kural

Bu blok **karar materyalidir**. İlliyetin hukuki niteliği ve nihai sorumluluk
Av. Bayram Can Çapar'a aittir. Boşluklar müvekkil-aleyhine olsa da açıkça yazılır
(anayasa: zaafları rahatsız edici olsa da bildir).

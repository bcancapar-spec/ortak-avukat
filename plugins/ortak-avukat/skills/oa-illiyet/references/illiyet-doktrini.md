# İlliyet Doktrini ve Graf Şeması — oa-illiyet referansı

Bu dosya iki şey içerir: (1) Türk hukukunda illiyet/bağ doktrininin özeti — kitin
hukuki çekirdeği; (2) graf JSON şeması. Norm ve künyeler buradan "ezbere" alınmaz;
somut dosyada **Mevzuat/Yargı Pro ile teyit** edilir. Bu özet yön gösterir, kaynak değildir.

## İçindekiler
1. Medeni hukukta illiyet (haksız fiil / sözleşme)
2. Ceza hukukunda nedensellik
3. İspat bağı (usul)
4. Kurumsal / kişilik bağı
5. Usul rolleri ve geçişleri
6. Graf JSON şeması

---

## 1. Medeni hukukta illiyet

- **Doğal (fiili) illiyet:** conditio sine qua non — "o fiil olmasaydı netice doğmaz mıydı?"
  Olmazsa olmaz şart testi. Graf: `illiyet_tipi: dogal`.
- **Hukuki (uygun) illiyet bağı:** Türk-İsviçre Borçlar Hukukunda **hakim teori**.
  Fiilin, hayatın olağan akışına ve genel hayat tecrübelerine göre o tür sonucu
  doğurmaya elverişli olması. Sadece doğal illiyet yetmez; uygunluk aranır.
  Graf: `illiyet_tipi: uygun`.
- **İlliyet bağının kesilmesi (3 hal):** (1) mücbir sebep, (2) zarar görenin/mağdurun
  ağır kusuru, (3) üçüncü kişinin ağır kusuru. Bunlar nedensellik bağını koparabilir.
  Graf: `kesme_flag: mucbir_sebep | magdur_kusuru | ucuncu_kisi_kusuru`.
- **Çoklu illiyet:** müteselsil sorumluluk (birlikte/müşterek illiyet) ve iç ilişkide
  rücu (TBK m.61-62). Yarışan illiyet, farazi illiyet, kısmî illiyet ayrımlarına dikkat.
- Dayanak normlar (teyit et): TBK m.49 vd. (haksız fiil), m.112 vd. (sözleşmeye aykırılık).

## 2. Ceza hukukunda nedensellik

- **Şart teorisi (conditio sine qua non / eşdeğerlik):** her şart neticeye eşit katkı.
  Tek başına yetersiz bulunarak eleştirilir (sınırsız genişleme).
- **Objektif isnadiyet (objektif yükleme) teorisi:** modern doktrin. İki aşama:
  (a) fiil ile netice arasında nedensellik, (b) neticenin faile objektif olarak
  yüklenebilmesi — failin hukuken önemli bir tehlike yaratması ve bu tehlikenin
  neticede gerçekleşmesi. Graf: `illiyet_tipi: objektif_isnadiyet`.
- **Netice sebebiyle ağırlaşmış suç (TCK m.23):** ağır netice için en azından taksir
  bağı aranır (objektif sorumluluk yasağı).
- **İştirak (TCK m.37-39):** faillik/müşterek faillik, azmettirme, yardım etme — kişiler
  arası illiyet-katkı bağları. Graf: ilişki kenarı `tur: istirak`.

## 3. İspat bağı (usul)

- Delil ↔ vakıa ispat bağı (HMK m.187 vd.); ispat yükü (HMK m.190; TMK m.6: iddia eden ispatla).
- **Karineler:** ispat yükünü kaydırır. İlliyet karinesi, fiili karine, kanuni karine.
  Graf: `dogrulama: karine` (delilsiz ama karineye dayalı kenar geçerli sayılır).
- Dijital delil bütünlüğü / zincir (chain of custody) — delil düğümleri arası bütünlük.

## 4. Kurumsal / kişilik bağı

- **TTK temsil:** m.370-371 (temsil yetkisi), ticari mümessil/ticari vekil, m.373 iyiniyetli
  üçüncü kişinin korunması. LTD'de m.629/1 → m.370-378 atfı (müdürün yetki sınırı).
- **Şirketler topluluğu / hakimiyet:** TTK m.195 vd.; bağlı/hakim şirket, kontrol.
- **Tüzel kişilik perdesinin aralanması (perdeyi kaldırma):** organik/ekonomik bağ varsa
  tüzel kişilik ayrılığı göz ardı edilir. Köprü düğüm (iki şirketi bağlayan ortak/müdür)
  bunun tipik sinyali.
- **Muvazaa (TBK m.19):** görünürdeki işlem ile gerçek irade ayrışması; nam-ı müstear.
  İstihkak davalarında sık (mal görünüşte üçüncü kişinin, gerçekte borçlunun).
- **İş hukuku:** İş K. m.2 asıl işveren-alt işveren + muvazaa; organik bağ. Müteselsil
  sorumluluk. SGK rücu (5510 m.21/4) — illiyet zinciri: iş kazası→kusur→SGK ödemesi→rücu.

## 5. Usul rolleri ve geçişleri

İllyet grafında gerçek kişi düğümünün usul rolü zorunludur ve evre boyunca DEĞİŞİR:

- **Soruşturma:** şüpheli · müşteki · mağdur · suçtan zarar gören · ihbar eden
- **Kovuşturma:** sanık · katılan (müdahil, CMK m.237 vd.) · mağdur
- **İnfaz:** hükümlü
- **Hukuk yargısı:** davacı · davalı · asli/fer'i müdahil
- **İcra:** alacaklı · borçlu · üçüncü kişi (istihkak, İİK m.96-99)
- Geçişler: müşteki→katılan; şüpheli→sanık→hükümlü. Aynı kişi farklı dosyada farklı rol.

---

## 6. Graf JSON şeması

```json
{
  "dugumler": [
    {
      "id": "kisa_benzersiz_kimlik",
      "tip": "gercek_kisi | tuzel_kisi | kamu | nesne | delil | olay | hak",
      "usul_rolu": "(gercek_kisi için ZORUNLU: borclu/sanik/katilan/davaci/...)",
      "ad": "Görünen ad"
    }
  ],
  "kenarlar": [
    {
      "kaynak": "dugum_id",
      "hedef": "dugum_id",
      "kategori": "iliski | illiyet",
      "tur": "(iliski: ortaklik/temsil/zilyetlik/muvazaa/asil_alt_isveren/istirak/... | illiyet: fiil_netice/sebep_zarar/kusur_zarar/...)",
      "illiyet_tipi": "(illiyet kenarı için: dogal | uygun | objektif_isnadiyet)",
      "guc": "dispozitif | guclu | zayif | tartismali",
      "kesme_flag": "(varsa: mucbir_sebep | magdur_kusuru | ucuncu_kisi_kusuru)",
      "dayanak_delil": ["delil_dugum_id", "..."],
      "dogrulama": "teyitli | iddia | karine",
      "norm": "İİK m.97 (Mevzuat MCP'den teyitli)"
    }
  ]
}
```

**Kullanım:** Grafı bu şemaya göre `graf.json` yaz, sonra
`python scripts/grafik_denetim.py graf.json` ile deterministik boşluk denetimi yap.

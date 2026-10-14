# HEYET KARARLARININ İNFAZI — v0.5.13

> Bu belge, üç bağımsız denetim turunun (akademik hukukçu heyeti · pratikçi
> avukat hakem düellosu · yazılım mühendisi heyeti) sonuçlarından **hangisinin
> uygulandığını, hangisinin daraltıldığını ve hangisinin ÇÜRÜDÜĞÜNÜ** kayda
> geçirir. Denetim malzemesinin tamamı ve ajan transkriptleri SHA-256
> manifestli yerel arşivdedir.

## Yöntem

- **Tur 1 — mesleki denetim:** 7 denetçi 20 SKILL.md'yi tek süzgeçten geçirdi:
  *"esaslı amaç ne olursa olsun müvekkilin menfaatine olsun."* Ayrıca 20 skill
  "avukat gibi düşünüp SONUCA varma" ölçütüyle puanlandı (ortalama 7,8/10).
- **Tur 2 — Türk hukukçusu hakem heyeti:** 5 disiplin (medeni usul, ceza,
  idare-vergi, özel hukuk, meslek kuralları) + başkan kararı.
- **Tur 3 — pratikçi düello:** kürsüde pişmiş 4 avukat hakem tez yazdı,
  birbirlerinin tezlerini **çapraz sorguyla yıkmaya** çalıştı (AYAKTA/YARALI/
  DÜŞTÜ), moderatör 20 tezi 12 maddeye indirdi.
- **Tur 4 — mühendis heyeti:** 3 denetçi (mimari bütünlük · test/CI etkisi ·
  geriye uyumluluk) her tezi **kod üzerinde** inceledi; UYGULANABİLİR / RİSKLİ
  / KIRAR hükmü verdi.
- **Norm teyidi:** hiçbir hukuki düzeltme hafızadan yazılmadı; her biri
  Mevzuat MCP'den güncel madde metniyle doğrulandı (2026-08-27).

## En önemli sonuç: bir tez ÇÜRÜDÜ

Pratikçi heyetin 1 numaralı tezi, `oa-mudafii`'deki "istinaf süresi gerekçeli
kararın tebliğinden işler" ifadesini **hata** sayıyordu ("tefhim tuzağı").
MCP teyidi bunun tersini gösterdi: **CMK m.273/1** metni *"hükmün gerekçesiyle
birlikte tebliğ edildiği tarihten itibaren iki hafta"* diyor ve hazır
bulunmayanlara ilişkin eski f.2 **7499 sayılı Kanunla mülga** edilmiş. Yani
dosyadaki ifade doğruydu; hakemin iddiası **eski hukuka** dayanıyordu.
**Dosya değiştirilmedi.** Ders: heyet de yanılır — düzeltmenin kendisi de
teyide tabidir.

## Uygulananlar

| # | Karar | Nerede |
|---|---|---|
| P0-1 | **Katılma anı** (CMK m.237): yalnız ilk derece kovuşturmasında, hüküm verilinceye kadar; kanun yolunda istenemez + tek istisna | `oa-musteki-vekili` |
| P0-2 | **CMK m.268 itiraz: 7 gün → iki hafta**, başlangıç öğrenme günü; itiraz ↔ istinaf/temyiz başlangıç rejimi ayrımı | `oa-mudafii` + kural tablosu (JSON **ve** gömülü fallback) |
| 1 | `--baslangic-turu` (teblig/tefhim/ogrenme/olay/belirsiz) — opsiyonel, imzanın sonunda, aritmetiği değiştirmez; belirsizde iki senaryo + ERKEN tarih | `hesapla_sure.py` |
| 2 | "Süre kaçtı" mutlak dilinin kırılması: nöbetçide tek satır işaretçi; **kurtarma kapıları kataloğu tek kaynakta** (kola göre ayrışır; İYUK'ta eski hâle getirme yok) | `sure_nobetci.py` + `oa-usul` |
| 3 | **Tutuklu dosya kipi:** ALIM'da zorunlu soru + defter/açılış damgası; azami süre iki senaryolu ve nitelendirme-teyitli (banner enflasyonu yok) | `oa-mudafii` |
| 4 | **Celse kartı** (yeni parça değil, cephanelik çıktısı) + DAHİLİ filigran + **mekanik sızıntı kapısı** | `oa-antitez` + `teslim_paketi.py` |
| 6 | **Zorunlu arabuluculuk dava şartı** — dört adreste birden (ilk-tur sorusu, usul taraması, dilekçe ön-kontrolü, tutanak→süre penceresi) | `oa-interview`, `oa-usul`, `oa-dilekce` |
| 8 | **İİK takip gövdesi çıpaları:** m.67 (1 yıl), m.68/68-a (6 ay), m.72 (takip evresine göre teminatın işlevi) | süre çizelgesi |
| 9 | **Mal kaçırma kavşağı:** yol seçimi + iki ayrı tarih ekseni + "karine YOK" üç tip taranmadan basılamaz | `oa-alan` şablonu |
| 11 | **İYUK m.10/11 mekaniği** (30 gün, 4 ay bekleme, 60 gün geç-cevap; durma + kalan süre) + VUK m.107/A (7587 ile değişik) | süre çizelgesi |

## Bilinçli olarak UYGULANMAYANLAR (gerekçeli)

- **Yeni 21. skill / ayrı celse parçası:** mühendis M2 "KIRAR" dedi — manifestteki
  "20 skill" iddiası CI'ın yapı işini düşürürdü. Kart, mevcut parçanın çıktısı
  olarak girdi.
- **m.108 periyodik inceleme "tekrar alanı":** şema işi; `tam_tur` iskeletine
  yeni numaralı bölüm eklemek sahadaki eski `dosya-analiz.md`'leri "bozuk"
  gösterip **kapanmış dosyaların TAMAM damgasını düşürürdü** (M3 bulgusu).
- **Tez 5, 7, 10, 12** (delil-niteliği motoru, kıyasa ispat yükü sütunu, ödeme
  emri unsur şablonu, tahsilat radarı): şema değişikliği gerektiriyor ve
  mühendis heyetinde KIRAR/ayrışma var — ayrı sürüme bırakıldı.
- **Otomatik tutanak düzeltme gündemi:** pratikçi antitez reddetti — "her celse
  tutanak kavgası açan vekil hâkimin kulağını kaybeder"; karar avukatındır.

## Değişmeyen ilkeler

Hiçbir kapı sertleştirilerek muhakeme engellenmedi; eklenen her kalem ya
**görünürlük** ya **tek satırlık ön-soru**dur. Fail-closed sözleşmeleri
(`GEÇMİŞ` alt dizesi, exit-3, 20-skill manifest kapısı, dört-damga sürüm
kuralı) korundu. Dahili belge sızıntı kapısı hariç yeni bloklayıcı kapı
eklenmedi.

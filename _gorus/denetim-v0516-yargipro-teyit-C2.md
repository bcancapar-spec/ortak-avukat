# Yargı Pro teyit izi — v0.5.16 / GRUP C2 (oa-kontrol: K4 atıf tanıyıcı, K5 akıbet tüketicisi, G11, hâkim lensi)

Hakem: Yargı Pro hakemi (yalnız okuma + MCP). Tarih: 2026-09-07. Taban: 80ac847.
Kapsam: `git diff 80ac847` içindeki .md/.py (tests hariç) dosyalarına giren hukuki norm atıfları.
Müvekkil/dosya verisi yok; sorgular yalnız kanun no + madde no.

## Araç + sorgu + sonuç

| # | Araç | Sorgu | Diffteki iddia | Sonuç |
|---|---|---|---|---|
| 1 | `mevzuat_getir` | 6100 m.371 | «HMK m.371 bozma sebepleri» ([G5-AKIBET] gerekçesi) | Madde başlığı «Bozma sebepleri»; (1) a-ç bentleri. UYUŞUYOR |
| 2 | `mevzuat_getir` | 6100 m.353 | «m.353/1-a kaldırma» | (1)-a: BAM «esası incelemeden kararın kaldırılmasına … gönderilmesine … kesin olarak karar verir». UYUŞUYOR |
| 3 | `mevzuat_getir` | 6100 m.119 | «HMK m.119/1-ğ anlamında ‘açık’ talep sonucu» (hâkim lensi) | (1)-ğ «Açık bir şekilde talep sonucu». UYUŞUYOR |
| 4 | `ictihat_ara` | esas 2023/1234 karar 2023/5678, H4, Yargıtay | test fikstürü künyesi (`tests/test_v0516_C2.py` — «SENTETİKTİR» beyanlı) | 0 sonuç; fikstür gerçek bir karara işaret etmiyor gibi görünüyor (0 sonuç ≠ yokluk kanıtı; m.7 sızıntısı YOK) |

Diff'te önceden var olan (değişmeyen) satırdaki «6216 s.K. m.45-49» atfı v0.5.16 eklemesi değildir; bu turda yeniden teyit edilmedi.

## Hukuki mantık (akıbet rejimi)
- LEHE + {bozuldu, kaldirildi} + dilekçede atıf → BLOK: bozulan/kaldırılan hüküm ortadan kalktığından lehe dayanak olamaz — doğru önerme.
- LEHE + kesinlesmedi → yalnız UYARI (kanun yolu açık): doğru; kesinleşmemiş karar dayanak olabilir, izlenmelidir.
- geri_cevrildi → «esasa ilişkin hüküm değil»: geri çevirme usulî bir iade kararıdır; önerme doğru.
- K4 tarih-only/K-only → EKSİK KÜNYE BLOK: aynı gün aynı daire birden çok karar verebileceğinden tek tarih/tek sayı ile mekanik teyit yapılamaz — doğru; «yerel mahkemenin … tarihli kararı» istisnası yapısal, hukuki yorum içermiyor.

## İçtihat künyesi / «yerleşik hat» iddiası
Diff'te hafızadan yazılmış içtihat künyesi ya da «Yargıtay … der» iddiası yok (test fikstürleri hariç).

## m.7
TCKN / gerçek kişi / gerçek dosya adı taraması: bulgu yok.

## Hüküm
KRİTİK: yok. KÜÇÜK: yok. → ONAY (Yargı Pro teyit yönünden).
MCP çağrı sayısı (bu grup için): 4 (toplam oturum sayısı ana raporda).

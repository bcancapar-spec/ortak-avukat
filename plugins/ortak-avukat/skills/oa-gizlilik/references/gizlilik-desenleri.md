# Gizlilik Desenleri ve İzin Gridi — oa-gizlilik referansı

## Hukuki temel
- **Avukatlık Kanunu m.36** — sır saklama yükümlülüğü; meslek sırrı.
- **TCK m.239** — ticari sır / müşteri sırrının açıklanması (ceza).
- **KVKK m.6** — özel nitelikli kişisel veri (sağlık, ceza mahkûmiyeti, biyometrik,
  din, etnik köken, sendika) — işlenmesi/aktarımı katı koşullara bağlı.
- **KVKK m.9** — kişisel verinin yurt dışına aktarımı: yeterlilik kararı ya da uygun
  güvence şartı (Mevzuat MCP teyit 2026-09-06, yeniden 2026-09-07 — 7499/34 ile değişik; senkron klasör riskinin normu).
- **KVKK genel** — kişisel verinin yurt dışına/üçüncü tarafa aktarımı.

## Desen sınıfları

### Mutlak DENY (her mod — Claude dokunmaz)
| Desen | Neden |
|---|---|
| UYAP login/oturum akışı | KATI KURAL: münhasıran avukat, manuel |
| e-imza / e-mühür / mobil imza | KATI KURAL: münhasıran avukat |
| PIN / parola / şifre | kimlik doğrulama sırrı |
| API anahtarı / token / secret | sistem kimliği |
| IBAN / kart numarası | finansal kimlik |

Bu desenlerde Claude: kod yazmaz, alanı doldurmaz, göndermez. "Bu adım size aittir,
manuel yapın" der ve durur.

### Hassas (mod'a göre deny/ask)
| Desen | Şiddet | strict | balanced |
|---|---|---|---|
| TC Kimlik No | güçlü | DENY | ASK |
| Sağlık/ceza/biyometrik (KVKK m.6) | güçlü | DENY | ASK |
| Esas/Karar no + taraf bağlamı | zayıf | ASK | geçer |
| Müvekkil ad + dosya bağlamı | zayıf | ASK | geçer |

**Künye beyaz listesi (A-22, v0.5.14).** Yukarıdaki satırın ölçütü **taraf
bağlamıdır**, künyenin kendisi değil. Bir esas/karar numarası, penceresinde
**yerleşik içtihat mercii** adı (Yargıtay, Danıştay, AYM, AİHM, BAM/BİM, HGK,
CGK, İçtihadı Birleştirme) taşıyor **ve** taraf bağlamı (davacı/davalı/müvekkil/
sanık/müşteki/borçlu/vekil …) taşımıyorsa **kamuya açık atıftır**: hassas veri
sayılmaz, ASK üretmez, `[BİLGİ]` kanalında görünür ve exit kodunu etkilemez.

Beyaz listeye **girmeyen** iki hâl (fail-closed):
- **Mercisiz çıplak künye** (`E. 2020/1111`) — müvekkilin kendi esas numarası olabilir.
- **İlk derece mahkemesi künyesi** (`… 3. İş Mahkemesi 2025/354 E.`) — dava
  dosyası kimliğidir; "Mahkemesi" ibaresi yerleşik içtihat mercii yerine geçmez.

Gerekçe: yanlış-pozitif üreten bir gizlilik kapısı uzun vadede **gerçek
pozitifi de** geçirtir; desen doktrinden sapmamalıdır.

## Modlar
- **strict** — dış buluta, web aramasına, üçüncü parti MCP'ye giderken. Varsayılan.
- **balanced** — yerel DB / çevrimdışı model (Ollama) gibi düşük riskli hedef.
- Yerel/çevrimdışı işleme muaf; risk **dış aktarımdadır**.

## Dış-araç izin gridi (MCP hardening)
MCP bağlayıcılar kalıcı erişim verir; tek-seferlik çekme değildir. Bu yüzden:

| Aksiyon tipi | Karar |
|---|---|
| Okuma (read/search/list/get) | geçer (always allow) |
| Durum değiştiren (send/write/update/move/share) | onay iste (needs approval) |
| UYAP'ta sil / dışa-paylaş | **bloklu** |
| Kalıcı kural (forwarding/filtre/webhook) | onay iste |

"Forward"u send say; yanlış yorumlanan bir talimat onaysız aktarıma yol açabilir.

## Senkron klasör desenleri (v0.5.16 — P1-8 / A-11 / B-5)

Çalışma kökünün mutlak yolunda, **yol parçası (klasör adı) düzeyinde, büyük/küçük harf
duyarsız** eşleşen desenler. Parça desene eşitse ya da desenin ardından boşluk / `-` /
`_` / `(` geliyorsa eşleşir ("OneDrive - Şirket", "Dropbox (Personal)"); bitişik türev
("onedrivelike") eşleşmez — yanlış-pozitif uyarı gerçek uyarının değerini düşürür.

| Desen | Tipik konum |
|---|---|
| `OneDrive`, `OneDrive - <kuruluş>` | Windows kullanıcı kökü (kişisel / iş hesabı) |
| `Google Drive`, `GoogleDrive`, `My Drive` | Drive for Desktop |
| `Dropbox`, `Dropbox (Personal)` | kullanıcı kökü |
| `iCloudDrive`, `iCloud Drive` | Windows iCloud istemcisi / macOS |
| `Box Sync` | Box istemcisi |
| `Nextcloud` | öz-barındırılan bulut (sunucu yeri bilinmeli) |
| `Syncthing` | eşler arası senkron (uzak cihaz sayısı bilinmeli) |

Liste **örneklemdir** (anayasa m.3): listede olmayan bir senkron istemcisi aynı riski taşır;
avukat kökü tanımıyorsa senkron dışı sayılmaz, sorulur.

**İnit uyarısı işaretçisi:** üretici uç `oa-pipeline/scripts/oa_hafiza.py init`'tir —
eşleşmede stdout'a görünür UYARI (Av.K. m.36 / KVKK m.6, m.9) + `_oa/defter/senkron-uyari.json`
`{yol, desen, zaman}`; kök artık desende değilse bayat JSON `[BİLGİ]` ile kaldırılır.
Bloklamaz. Öneri: senkron dışına taşı, taşınamıyorsa VeraCrypt / BitLocker şifreli
konteyner (bkz. SKILL.md "Senkron klasör riski").

## Sınır
Tarama desenlere dayanır; her hassas veriyi yakalamayı garanti etmez. ALLOW çıktısı
"kesin güvenli" demek değildir — emin olunmayan her aktarımda avukata danışılır.
Şüphede daima daha kısıtlayıcı karar seçilir.

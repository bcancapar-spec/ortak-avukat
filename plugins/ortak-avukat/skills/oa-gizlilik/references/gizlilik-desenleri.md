# Gizlilik Desenleri ve İzin Gridi — oa-gizlilik referansı

## Hukuki temel
- **Avukatlık Kanunu m.36** — sır saklama yükümlülüğü; meslek sırrı.
- **TCK m.239** — ticari sır / müşteri sırrının açıklanması (ceza).
- **KVKK m.6** — özel nitelikli kişisel veri (sağlık, ceza mahkûmiyeti, biyometrik,
  din, etnik köken, sendika) — işlenmesi/aktarımı katı koşullara bağlı.
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

## Sınır
Tarama desenlere dayanır; her hassas veriyi yakalamayı garanti etmez. ALLOW çıktısı
"kesin güvenli" demek değildir — emin olunmayan her aktarımda avukata danışılır.
Şüphede daima daha kısıtlayıcı karar seçilir.

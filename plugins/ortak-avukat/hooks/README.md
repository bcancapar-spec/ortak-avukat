# hooks.json — P0-7 (v0.5.5) MODEL-BAĞIMSIZ TETİK

`hooks.json` şu satırı taşır: oturum kapanışında (`Stop`/`SessionEnd`)
`pipeline_kayit.py --hook-denetle` otomatik koşar.

- `_oa/defter` bu çalışma kökünde YOKSA: sessizce `exit 0` (bu dizin
  pipeline defteri kullanmıyor).
- VARSA: denetim + `oa_metrik` özetini basar ve `_oa/DURUM.md`'yi tazeler.
- ASLA bloklamaz, ASLA oturum kapanışını engellemez — tek amacı zincirin
  ucunu modelin gönüllü çağrısından bağımsızlaştırmaktır.
- `Stop` harness tarafından HER asistan turu bitiminde tetiklenir (yalnız
  oturum sonunda değil). Denetim (`denetle_calistir`, dolayısıyla
  `_oa/DURUM.md` türetimi) HER hook çağrısında TAM güçte koşar — bu asla
  kısa devre yapılmaz, çünkü uyarıların çoğu (makbuzsuz dilekçe/UDF adayı,
  Gate G) deftere değil diske bakar ve defter değişmeden de değişebilir.
  Yalnız STDOUT BASIMI kısa devre olabilir: bir önceki koşunun denetim
  çıktı METNİ ile bu koşununki bit-bit AYNIYSA (`_hook_cikti_degisti_mi` —
  `_oa/defter/.hook-son-iz.json`) basım bastırılır (gürültü azaltma); metnin
  EN UFAK farkı (yeni bir uyarı/sorun satırı dahil) basımı yeniden tetikler.

(Bu açıklama BİLİNÇLİ olarak `hooks.json`'ın DIŞINDA tutulur — üst düzey
`description` anahtarı Claude Code hook şemasının bir parçası değildir;
şema-dışı ek alan taşımak yerine bu bilgi ayrı bir README'de tutulur.)

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

## Yorumlayıcı seçimi — Windows Mağaza kısayolu (v0.5.18)

`run-hook.cmd` PATH'teki ilk `python`'u körlemesine çağırmaz. Windows'ta
`%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe` Microsoft Store'un yer
tutucusudur: Python yüklü değilmiş gibi davranıp 49 koduyla çıkar. 2026-10-11'de
yeni bilgisayarda PATH'te ilk sırada bu kısayol vardı ve kurulu eklentinin altı
hook olayının altısı da sessizce ölüydü (`tools/hook_doktor.py`: altısı exit 49).
Sarmalayıcı artık hem cmd hem bash kolunda WindowsApps adaylarını atlar, gerçek
yorumlayıcıyı seçer; başka yorumlayıcı yoksa kısayolu son çare olarak dener.
`py` başlatıcısı seçilirse `-3` ile çağrılır. Yürütülebilir satırlarda `||`
yoktur (447 dersi). Eski sürümü kullanan makinede geçici çare kullanıcıdadır:
Ayarlar > Uygulamalar > Gelişmiş uygulama ayarları > Uygulama yürütme diğer
adları > "python.exe" ve "python3.exe" kapalı. Eklenti sistem ayarına dokunmaz.

**Dosya saf ASCII kalır (v0.5.18, 2026-10-12 ölçümü).** Depo bu dosyayı LF satır
sonuyla saklar, çünkü bash kolu CRLF'yi kaldıramaz. Konsol kod sayfası UTF-8 (65001)
iken cmd, LF'li batch dosyasındaki çok baytlı bir karakterin ofsetini yanlış sayıyor,
satırın ortasından okumaya başlıyor ve REM yorumunun parçalarını komut diye
çalıştırıyordu. Sistem genelinde UTF-8 kullanan Windows'ta kanca böyle ölür. Bu
dosyaya Türkçe karakter ya da uzun tire YAZMAYIN; `tests/test_hook_sarmalayici.py`
hem bayt düzeyinde hem `chcp 65001` altında koşarak bunu kilitler.

(Bu açıklama BİLİNÇLİ olarak `hooks.json`'ın DIŞINDA tutulur — üst düzey
`description` anahtarı Claude Code hook şemasının bir parçası değildir;
şema-dışı ek alan taşımak yerine bu bilgi ayrı bir README'de tutulur.)

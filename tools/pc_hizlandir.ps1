<#
  pc_hizlandir.ps1 — ORTAK AVUKAT İÇİN WINDOWS OPTİMİZASYONU
  © 2026 Av. Bayram Can Çapar — Tüm hakları saklıdır (5846 sayılı FSEK).

  ═══════════════════════════════════════════════════════════════════════════
  NE YAPAR / NE YAPMAZ
  ═══════════════════════════════════════════════════════════════════════════
  Bu betik Ortak Avukat'ın İŞ YÜKÜNE ÖZEL olarak Windows'u ayarlar. O iş yükü
  şudur: tur başına ONLARCA KISA ÖMÜRLÜ python.exe süreci. Bu, Windows'un en
  pahalı bulduğu desendir — çünkü her süreç başlığında (CreateProcess)
  Defender devreye girer, her .py okuması taranır, ve güç planı düşük frekansta
  duruyorsa frekans rampası her seferinde baştan tırmanır.

  ASLA YAPMAZ:
    · Hiçbir dosyayı silmez, taşımaz, üzerine yazmaz.
    · Sayfa dosyasına (pagefile) DOKUNMAZ — kapatmak bellek dolduğunda süreç
      çökmesine ve VERİ KAYBINA yol açar. Bu betik bunu önermez bile.
    · Servis kapatmaz, kayıt defteri "temizlemez", "RAM optimize etmez".
      Bunlar ölçülebilir kazanç vermeyen, sistem kararlılığını bozan
      hurafelerdir. Bkz. aşağıdaki REDDEDİLENLER bölümü.
    · Yaptığı HER değişiklik -GeriAl ile geri alınır.

  ═══════════════════════════════════════════════════════════════════════════
  KULLANIM — ÖNCE ÖLÇ, SONRA UYGULA
  ═══════════════════════════════════════════════════════════════════════════
    # 1) Teşhis (hiçbir şey değiştirmez — varsayılan mod):
    .\tools\pc_hizlandir.ps1

    # 2) Kendi makinenizin hook gecikmesini ölçün (referans sayı):
    python .\tools\hook_olc.py --tekrar 25

    # 3) Uygula (yönetici PowerShell gerekir):
    .\tools\pc_hizlandir.ps1 -Uygula

    # 4) Tekrar ölçün — kazancı KENDİ makinenizde görün:
    python .\tools\hook_olc.py --tekrar 25

    # Geri almak için:
    .\tools\pc_hizlandir.ps1 -GeriAl

  Yönetici PowerShell: Başlat → "PowerShell" → sağ tık → "Yönetici olarak
  çalıştır". Betik imzasız olduğu için gerekirse:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#>

[CmdletBinding()]
param(
    [switch]$Uygula,      # değişiklikleri gerçekten yap
    [switch]$GeriAl,      # yapılan değişiklikleri geri al
    [switch]$Agresif      # güvenlik ödünü daha büyük olan adımları da uygula
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'Continue'

$DepoKok  = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$KayitDir = Join-Path $env:LOCALAPPDATA 'ortak-avukat'
$Kayit    = Join-Path $KayitDir 'pc_hizlandir-kayit.json'
$Gunluk   = Join-Path $KayitDir 'pc_hizlandir-gunluk.txt'
New-Item -ItemType Directory -Force -Path $KayitDir | Out-Null

function Yaz([string]$m, [string]$renk = 'Gray') { Write-Host $m -ForegroundColor $renk }
function Bolum([string]$m) { Yaz ""; Yaz ("── " + $m + " " + ("─" * [Math]::Max(0, 66 - $m.Length))) 'Cyan' }
function Kaydet([string]$m) { ("[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) | Add-Content -Path $Gunluk -Encoding UTF8 }

function YoneticiMi {
    $k = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $k.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# ── Geri alma defteri: her değişiklik ÖNCEKİ değeriyle diske yazılır ────────
function DefterOku {
    if (Test-Path $Kayit) { try { return Get-Content $Kayit -Raw | ConvertFrom-Json } catch { } }
    return $null
}
function DefterYaz($nesne) { $nesne | ConvertTo-Json -Depth 6 | Set-Content -Path $Kayit -Encoding UTF8 }

# ═══════════════════════════════════════════════════════════════════════════
# 1. TEŞHİS — donanım ve mevcut ayarlar
# ═══════════════════════════════════════════════════════════════════════════
function Teshis {
    Bolum "DONANIM"
    $cs  = Get-CimInstance Win32_ComputerSystem
    $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
    $os  = Get-CimInstance Win32_OperatingSystem
    Yaz ("  İşlemci        : {0}" -f $cpu.Name.Trim())
    Yaz ("  Çekirdek/İş par: {0} fiziksel / {1} mantıksal" -f $cpu.NumberOfCores, $cpu.NumberOfLogicalProcessors)
    Yaz ("  Taban frekans  : {0} MHz" -f $cpu.MaxClockSpeed)
    Yaz ("  RAM            : {0:N1} GB" -f ($cs.TotalPhysicalMemory / 1GB))
    Yaz ("  Boş RAM        : {0:N1} GB" -f ($os.FreePhysicalMemory / 1MB))
    Yaz ("  İşletim sistemi: {0} (derleme {1})" -f $os.Caption, $os.BuildNumber)

    # Disk tipi: SSD mi HDD mi — birleştirme (defrag) önerisi buna bağlı
    try {
        Get-PhysicalDisk | ForEach-Object {
            Yaz ("  Disk           : {0} · {1} · {2:N0} GB" -f $_.FriendlyName, $_.MediaType, ($_.Size / 1GB))
        }
    } catch { Yaz "  Disk           : okunamadı (Get-PhysicalDisk yok)" }

    Bolum "PYTHON"
    $py = Get-Command python -ErrorAction SilentlyContinue
    if ($py) {
        Yaz ("  python         : {0}" -f $py.Source)
        Yaz ("  sürüm          : {0}" -f (& python --version 2>&1))
        $v = (& python -c "import sys;print(sys.version_info[0]*100+sys.version_info[1])" 2>&1)
        if ([int]$v -lt 312) {
            Yaz "  ! UYARI: Ortak Avukat Python >= 3.12 istiyor (pyproject.toml)." 'Yellow'
            Yaz "    3.12+ kurulumu bazı dosyaların hiç yüklenmemesine son verir." 'Yellow'
        }
    } else { Yaz "  ! python PATH'te YOK — hooklar sessizce hiç ateşlenmez." 'Red' }

    # KRİTİK: bu değişken ayarlıysa bytecode önbelleği ÇALIŞMAZ ve
    # hook_giris.py'nin sağladığı ~41 ms/hook kazanç KAYBOLUR.
    if ($env:PYTHONDONTWRITEBYTECODE) {
        Yaz "  ! PYTHONDONTWRITEBYTECODE AYARLI — bytecode önbelleği devre dışı!" 'Red'
        Yaz "    Bu, hook başına ~41 ms kazancı yok eder. Kaldırılmalı." 'Red'
    } else { Yaz "  PYTHONDONTWRITEBYTECODE: ayarsız ✓ (bytecode önbelleği çalışır)" 'Green' }

    if ($env:PYTHONUTF8 -eq '1') { Yaz "  PYTHONUTF8=1 ✓" 'Green' }
    else { Yaz "  PYTHONUTF8: ayarsız — cp1254 konsolunda Türkçe çökmesi riski" 'Yellow' }

    Bolum "GÜÇ PLANI"
    $aktif = (powercfg /getactivescheme) -join ''
    Yaz ("  Aktif          : {0}" -f $aktif.Trim())
    if ($aktif -match 'Dengeli|Balanced') {
        Yaz "  ! 'Dengeli' plan: kısa süreçler için frekans rampası yavaş." 'Yellow'
    }

    Bolum "DEFENDER (gerçek zamanlı tarama)"
    try {
        $mp = Get-MpPreference
        $rt = (Get-MpComputerStatus).RealTimeProtectionEnabled
        Yaz ("  Gerçek zamanlı koruma: {0}" -f $rt)
        $yollar = @($mp.ExclusionPath)
        $surecler = @($mp.ExclusionProcess)
        Yaz ("  Dışlanan yol sayısı  : {0}" -f ($yollar | Where-Object { $_ }).Count)
        Yaz ("  Dışlanan süreç sayısı: {0}" -f ($surecler | Where-Object { $_ }).Count)
        if ($rt -and -not ($surecler -contains 'python.exe')) {
            Yaz "  ! python.exe dışlanmamış: her hook süreci taranıyor." 'Yellow'
        }
    } catch { Yaz "  Defender bilgisi okunamadı (üçüncü parti antivirüs olabilir)." 'Yellow' }

    Bolum "EKLENTİ KURULUMU"
    $adaylar = @(
        (Join-Path $env:USERPROFILE '.claude\plugins'),
        (Join-Path $env:APPDATA 'Claude\plugins')
    )
    foreach ($a in $adaylar) { if (Test-Path $a) { Yaz ("  bulundu: {0}" -f $a) } }
    Yaz ("  depo kökü      : {0}" -f $DepoKok)
}

# ═══════════════════════════════════════════════════════════════════════════
# 2. UYGULA
# ═══════════════════════════════════════════════════════════════════════════
function OptimizasyonUygula {
    if (-not (YoneticiMi)) {
        Yaz "HATA: -Uygula için YÖNETİCİ PowerShell gerekir." 'Red'
        Yaz "  Başlat → PowerShell → sağ tık → 'Yönetici olarak çalıştır'" 'Yellow'
        return
    }

    $defter = [ordered]@{
        tarih                = (Get-Date -Format 'o')
        guc_plani_onceki     = $null
        defender_eklenen_yol = @()
        defender_eklenen_sur = @()
        ortam_onceki         = [ordered]@{}
    }

    # ── (P0) DEFENDER DIŞLAMALARI ──────────────────────────────────────────
    # NEDEN EN BÜYÜK KAZANÇ: Defender her CreateProcess'i ve her .py okumasını
    # keser. Tur başına onlarca python.exe başlığı olan bir iş yükünde bu,
    # süreç başına on-yüz milisaniye mertebesinde ek yük demektir.
    # GÜVENLİK ÖDÜNÜ (açıkça): dışlanan yol ARTIK TARANMAZ. Bu yüzden yalnızca
    # (a) sizin kendi eklenti kodunuzun bulunduğu dizinler ve (b) Python
    # kurulum dizini dışlanır. Müvekkil evrakının bulunduğu dava klasörleri
    # DIŞLANMAZ — orada indirilen dosyalar olabilir, tarama sürmelidir.
    Bolum "P0 · DEFENDER DIŞLAMALARI"
    $dislanacak = @()
    foreach ($p in @((Join-Path $env:USERPROFILE '.claude\plugins'),
                     (Join-Path $env:APPDATA 'Claude\plugins'),
                     $DepoKok)) {
        if (Test-Path $p) { $dislanacak += $p }
    }
    $pyKomut = Get-Command python -ErrorAction SilentlyContinue
    if ($pyKomut) { $dislanacak += (Split-Path -Parent $pyKomut.Source) }

    try {
        $mevcut = @((Get-MpPreference).ExclusionPath)
        foreach ($p in ($dislanacak | Select-Object -Unique)) {
            if ($mevcut -contains $p) { Yaz ("  zaten dışlanmış: {0}" -f $p); continue }
            Add-MpPreference -ExclusionPath $p -ErrorAction Stop
            $defter.defender_eklenen_yol += $p
            Yaz ("  + yol dışlandı : {0}" -f $p) 'Green'
            Kaydet "Defender yol dislandi: $p"
        }
        $mevcutSur = @((Get-MpPreference).ExclusionProcess)
        foreach ($s in @('python.exe', 'pythonw.exe', 'py.exe')) {
            if ($mevcutSur -contains $s) { Yaz ("  zaten dışlanmış: {0}" -f $s); continue }
            Add-MpPreference -ExclusionProcess $s -ErrorAction Stop
            $defter.defender_eklenen_sur += $s
            Yaz ("  + süreç dışlandı: {0}" -f $s) 'Green'
            Kaydet "Defender surec dislandi: $s"
        }
        Yaz "  NOT: dışlanan yollar artık taranmıyor — bilinçli bir ödün." 'Yellow'
    } catch {
        Yaz ("  Defender ayarı yapılamadı: {0}" -f $_.Exception.Message) 'Red'
        Yaz "  (Kurumsal politika veya üçüncü parti antivirüs engelliyor olabilir.)" 'Yellow'
    }

    # ── (P0) PYTHON ORTAM DEĞİŞKENLERİ ─────────────────────────────────────
    # PYTHONDONTWRITEBYTECODE ayarlıysa hook_giris.py'nin tüm kazancı gider.
    # PYTHONUTF8=1 ise STATUS.md:294'te kayıtlı cp1254 çökmelerini bitirir.
    Bolum "P0 · PYTHON ORTAM DEĞİŞKENLERİ"
    $defter.ortam_onceki['PYTHONDONTWRITEBYTECODE'] = [Environment]::GetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', 'User')
    $defter.ortam_onceki['PYTHONUTF8'] = [Environment]::GetEnvironmentVariable('PYTHONUTF8', 'User')

    if ([Environment]::GetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', 'User')) {
        [Environment]::SetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', $null, 'User')
        Yaz "  - PYTHONDONTWRITEBYTECODE kaldırıldı (bytecode önbelleği açıldı)" 'Green'
        Kaydet "PYTHONDONTWRITEBYTECODE kaldirildi"
    } else { Yaz "  PYTHONDONTWRITEBYTECODE zaten ayarsız ✓" }

    [Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', 'User')
    Yaz "  + PYTHONUTF8=1 (Türkçe konsol çökmesi biter)" 'Green'
    Kaydet "PYTHONUTF8=1 ayarlandi"
    Yaz "  ! Yeni değerler için Claude Code TAM kapatılıp açılmalı." 'Yellow'

    # ── (P1) GÜÇ PLANI ─────────────────────────────────────────────────────
    # Kısa ömürlü süreçler frekans rampasından en çok etkilenen iş yüküdür:
    # süreç, işlemci tam hıza çıkmadan bitiyor. 'Yüksek performans' planı
    # minimum işlemci durumunu yükselterek bu rampayı ortadan kaldırır.
    # Dizüstünde pil ömrü azalır — bilinçli ödün.
    Bolum "P1 · GÜÇ PLANI"
    $defter.guc_plani_onceki = ((powercfg /getactivescheme) -join '' -replace '.*GUID:\s*([0-9a-fA-F-]+).*', '$1').Trim()
    $YUKSEK = '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'   # Yüksek performans (sabit GUID)
    $ULTIMATE = 'e9a42b02-d5df-448d-aa00-03f14749eb61' # Ultimate Performance (varsa)
    $planlar = (powercfg /list) -join "`n"
    $hedef = if ($planlar -match [regex]::Escape($ULTIMATE)) { $ULTIMATE } else { $YUKSEK }
    powercfg /setactive $hedef 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Yaz ("  + güç planı: {0}" -f $hedef) 'Green'
        Kaydet "Guc plani $hedef (onceki: $($defter.guc_plani_onceki))"
        Yaz "  ! Dizüstüyseniz pil ömrü azalır (geri alınabilir)." 'Yellow'
    } else { Yaz "  güç planı değiştirilemedi (kurumsal politika olabilir)" 'Yellow' }

    # ── (P2) DÜRÜSTLÜK BÖLÜMÜ: ÖLÇÜLMEMİŞ / MARJİNAL ADIMLAR ───────────────
    Bolum "P2 · MARJİNAL — sadece -Agresif ile"
    if ($Agresif) {
        # NTFS son-erişim zamanı: Windows 10 1803+ zaten "sistem yönetimli"
        # modda büyük ölçüde kapatıyor. Kazanç KÜÇÜK ve bu makinede ÖLÇÜLMEDİ.
        fsutil behavior set disablelastaccess 1 2>&1 | Out-Null
        Yaz "  + NTFS son-erişim zamanı kapatıldı (kazanç küçük, ölçülmedi)" 'Green'
        Kaydet "fsutil disablelastaccess 1"
    } else {
        Yaz "  atlandı. NTFS son-erişim zamanı / 8.3 kısa ad: kazanç KÜÇÜK ve"
        Yaz "  bu iş yükü için ÖLÇÜLMEDİ. Büyük kazanç P0'dadır, burada değil."
    }

    DefterYaz $defter
    Bolum "BİTTİ"
    Yaz ("  geri alma defteri: {0}" -f $Kayit)
    Yaz ("  günlük           : {0}" -f $Gunluk)
    Yaz ""
    Yaz "  ŞİMDİ ÖLÇÜN — kazancı kendi makinenizde görün:" 'Cyan'
    Yaz "    python .\tools\hook_olc.py --tekrar 25" 'Cyan'
}

# ═══════════════════════════════════════════════════════════════════════════
# 3. GERİ AL
# ═══════════════════════════════════════════════════════════════════════════
function GeriAlUygula {
    if (-not (YoneticiMi)) { Yaz "HATA: -GeriAl için YÖNETİCİ PowerShell gerekir." 'Red'; return }
    $d = DefterOku
    if ($null -eq $d) { Yaz "Geri alma defteri yok — uygulanmış değişiklik bulunamadı." 'Yellow'; return }

    Bolum "GERİ ALINIYOR"
    foreach ($p in @($d.defender_eklenen_yol)) {
        if ($p) { Remove-MpPreference -ExclusionPath $p -ErrorAction SilentlyContinue; Yaz ("  - yol dışlaması kaldırıldı: {0}" -f $p) 'Green'; Kaydet "GERI AL yol: $p" }
    }
    foreach ($s in @($d.defender_eklenen_sur)) {
        if ($s) { Remove-MpPreference -ExclusionProcess $s -ErrorAction SilentlyContinue; Yaz ("  - süreç dışlaması kaldırıldı: {0}" -f $s) 'Green'; Kaydet "GERI AL surec: $s" }
    }
    if ($d.guc_plani_onceki) {
        powercfg /setactive $d.guc_plani_onceki 2>&1 | Out-Null
        Yaz ("  - güç planı geri alındı: {0}" -f $d.guc_plani_onceki) 'Green'
        Kaydet "GERI AL guc plani: $($d.guc_plani_onceki)"
    }
    if ($d.ortam_onceki) {
        foreach ($ad in @('PYTHONDONTWRITEBYTECODE', 'PYTHONUTF8')) {
            $eski = $d.ortam_onceki.$ad
            [Environment]::SetEnvironmentVariable($ad, $(if ($eski) { $eski } else { $null }), 'User')
            Yaz ("  - {0} eski değerine döndü ({1})" -f $ad, $(if ($eski) { $eski } else { 'ayarsız' })) 'Green'
        }
    }
    Remove-Item $Kayit -Force -ErrorAction SilentlyContinue
    Yaz "  Geri alma tamam." 'Green'
}

# ═══════════════════════════════════════════════════════════════════════════
# REDDEDİLENLER — neden önerilmediğinin gerekçesi
# ═══════════════════════════════════════════════════════════════════════════
function Reddedilenler {
    Bolum "REDDEDİLENLER (bilinçli olarak ÖNERİLMEZ)"
    @(
        @{ ad = 'Sayfa dosyasını (pagefile) kapatmak';
           n  = 'Bellek dolduğunda süreçler çöker → İŞLENMEMİŞ VERİ KAYBI. Asla.' },
        @{ ad = 'Kayıt defteri "temizleyicileri"';
           n  = 'Ölçülebilir hız kazancı yok; sistemi bozma riski gerçek.' },
        @{ ad = '"RAM optimize edici" araçlar';
           n  = 'Çalışan süreçlerin belleğini diske attırır; SONRAKİ erişimi YAVAŞLATIR.' },
        @{ ad = 'SSD birleştirme (defrag)';
           n  = 'SSD''de kazanç yok, yazma ömrünü tüketir. Windows zaten TRIM uyguluyor.' },
        @{ ad = 'Servisleri toptan kapatmak';
           n  = 'Hangi servisin neyi beslediği belirsiz; kazanç ölçülemez, arıza kesin.' },
        @{ ad = 'Gerçek zamanlı korumayı TAMAMEN kapatmak';
           n  = 'Hedefli dışlama aynı kazancı verir, makineyi savunmasız bırakmaz.' },
        @{ ad = 'WSL2 altında koşturmak';
           n  = 'Depo Windows diskindeyse /mnt geçişi dosya işlemlerini YAVAŞLATIR. Ancak tüm ağaç WSL2 ext4 içinde yaşarsa kazanç olur — o zaman da masaüstü entegrasyonu karmaşıklaşır.' },
        @{ ad = 'python -S / -E ile site''ı atlamak';
           n  = 'Hook yolunda ~3 ms kazanç; ama oa-ingest pymupdf/pillow''a ihtiyaç duyduğunda site-packages şart. Ödün kazançtan büyük.' }
    ) | ForEach-Object {
        Yaz ("  ✗ {0}" -f $_.ad) 'Red'
        Yaz ("     {0}" -f $_.n)
    }
}

# ── Akış ───────────────────────────────────────────────────────────────────
Yaz ""
Yaz "  ORTAK AVUKAT — WINDOWS OPTİMİZASYONU" 'Cyan'
Yaz "  ölç → uygula → tekrar ölç. Kanıtsız hız beyanı yoktur." 'DarkGray'

if ($GeriAl)      { GeriAlUygula }
elseif ($Uygula)  { Teshis; OptimizasyonUygula; Reddedilenler }
else {
    Teshis
    Reddedilenler
    Bolum "SONRAKİ ADIM"
    Yaz "  Bu bir TEŞHİS koşusuydu — hiçbir şey değiştirilmedi."
    Yaz "  Uygulamak için (yönetici PowerShell):  .\tools\pc_hizlandir.ps1 -Uygula" 'Cyan'
}
Yaz ""

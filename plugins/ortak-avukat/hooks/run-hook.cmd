: << 'CMDBLOCK'
@echo off
REM Ortak Avukat hook sarmalayicisi (v0.5.8.2 - 447 yapisal-ariza dersi).
REM NEDEN VAR: masaustu uygulamasi hook komutunu KABUKSUZ calistirabiliyor;
REM "python X || py -3 X" zincirindeki || kabuk operatoru olarak degil
REM python'a arguman olarak gidiyor -> sessiz olum (uc sahada sifir atesleme).
REM Cozum (superpowers run-hook.cmd deseni): fallback mantigi BU dosyanin
REM icinde; hooks.json tek tirnakli TEK komut cagirir.
REM Kullanim: run-hook.cmd <mod>
REM   (hook-prompt | hook-postwrite | hook-denetle | hook-pretool | hook-acilis)
REM Mod gecisi JENERIKTIR (--%1): yeni hook modlari bu dosyada degisiklik
REM gerektirmez - v0.5.8.5 hook-acilis (SessionStart) bu yoldan gecer.
REM CWD'ye DOKUNMAZ: pipeline_kayit.py dava kokunu CWD'den okur.
REM STDIN python'a AKTARILIR (cocuk surec miras alir) - hook-pretool payload'i
REM (tool_input) bu kanaldan okur; asla tuketilmez/kesilmez.

REM PERFORMANS (v0.5.16.2): hedef artik hook_giris.py - o, pipeline_kayit.py'yi
REM IMPORT ederek cagirir, boylece Python bytecode'u __pycache__'ten okur.
REM `__main__` olarak kosulan bir betigin bytecode'u ASLA onbellege alinmaz;
REM 6300+ satir her hook ateslemesinde sifirdan derleniyordu.
REM OLCUM (Py3.12, net yuk): dogrudan 67.6 ms -> giris betigi 26.3 ms.
REM hook_giris.py yoksa (yarim/eski kurulum) ESKI hedefe dusulur - islev
REM kaybi YOK, sadece eski hiz. Yedek mantigi "if not exist" ile kurulur;
REM zincir operatoru KULLANILMAZ (447 dersi: kabuksuz yurutmede sessiz olum).

REM YORUMLAYICI SECIMI (v0.5.18, 2026-10-11 bu makinede olculdu): PATH'te
REM Microsoft Store'un sahte python kisayolu (WindowsApps; "Python was not
REM found", cikis 49) gercek yorumlayicidan ONCE gelince eski kod onu kosturuyor,
REM kanca katmaninin alti olayi da SESSIZCE oluyordu. Adaylar (python, python3,
REM py) PATH sirasiyla taranir; WindowsApps altindakiler EN SONA birakilir
REM (orada gercek bir MSIX takma adi da olabilir - baska aday yoksa denenir).
REM Etiket/alt rutin KULLANILMAZ (cmd'nin LF satir sonunda etiket arama kusuru);
REM ek surec acilmaz (kanca hizi): tek `where`, dize karsilastirmasi.

if "%~1"=="" exit /b 0
setlocal EnableDelayedExpansion
set "HOOK_DIR=%~dp0"
set "OA_SCRIPT=%HOOK_DIR%..\skills\oa-pipeline\scripts\hook_giris.py"
if not exist "%OA_SCRIPT%" set "OA_SCRIPT=%HOOK_DIR%..\skills\oa-pipeline\scripts\pipeline_kayit.py"

set "OA_PY="
set "OA_PY_YEDEK="
for /f "delims=" %%P in ('where python python3 py 2^>nul') do (
    set "OA_ADAY=%%P"
    if "!OA_ADAY:WindowsApps=!"=="!OA_ADAY!" (
        if not defined OA_PY set "OA_PY=%%P"
    ) else (
        if not defined OA_PY_YEDEK set "OA_PY_YEDEK=%%P"
    )
)
if not defined OA_PY set "OA_PY=!OA_PY_YEDEK!"
REM Python yok - sessizce cik (hook ASLA bloklamaz)
if not defined OA_PY exit /b 0
set "OA_PY_ARG="
for %%N in ("!OA_PY!") do if /i "%%~nN"=="py" set "OA_PY_ARG=-3"
call "!OA_PY!" !OA_PY_ARG! "%OA_SCRIPT%" --%~1
exit /b 0
CMDBLOCK

# Unix/bash tarafi (polyglot; shebang'siz - Linux'ta /bin/sh ile kosar, POSIX sh).
# PERFORMANS (v0.5.16.2): hedef hook_giris.py (bkz. yukaridaki CMD blogu).
# Yoksa eski hedefe dusulur - islev kaybi YOK, sadece eski hiz.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OA_SCRIPT="${SCRIPT_DIR}/../skills/oa-pipeline/scripts/hook_giris.py"
if [ ! -f "$OA_SCRIPT" ]; then
    OA_SCRIPT="${SCRIPT_DIR}/../skills/oa-pipeline/scripts/pipeline_kayit.py"
fi
# YORUMLAYICI SECIMI (v0.5.18; bkz. CMD blogu): once PATH genelinde python3, sonra
# python (eski dagitimlarda PATH'te once gelen bir dizindeki 'python' Python 2 olabilir;
# dizin basina arama onu python3'ten once seciyordu). Calistirilabilir olmayan dosya
# atlanir; WindowsApps altindakiler (Store kisayolu olabilir) en sona. Ek surec acilmaz.
oa_py=""
oa_yedek=""
oa_ara() {
    for d in $PATH; do
        for ad in "$@"; do
            if [ -f "$d/$ad" ]; then
                if [ -x "$d/$ad" ]; then
                    case "$d" in
                        *[Ww]indows[Aa]pps*)
                            if [ -z "$oa_yedek" ]; then oa_yedek="$d/$ad"; fi
                            ;;
                        *)
                            oa_py="$d/$ad"
                            return 0
                            ;;
                    esac
                fi
            fi
        done
    done
    return 1
}
oa_ifs="$IFS"
set -f
IFS=":"
oa_ara python3 python3.exe
if [ -z "$oa_py" ]; then
    oa_ara python python.exe
fi
IFS="$oa_ifs"
set +f
if [ -z "$oa_py" ]; then
    oa_py="$oa_yedek"
fi
if [ -n "$oa_py" ]; then
    exec "$oa_py" "$OA_SCRIPT" "--$1"
fi
exit 0

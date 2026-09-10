: << 'CMDBLOCK'
@echo off
REM Ortak Avukat hook sarmalayicisi (v0.5.8.2 — 447 yapisal-ariza dersi).
REM NEDEN VAR: masaustu uygulamasi hook komutunu KABUKSUZ calistirabiliyor;
REM "python X || py -3 X" zincirindeki || kabuk operatoru olarak degil
REM python'a arguman olarak gidiyor -> sessiz olum (uc sahada sifir atesleme).
REM Cozum (superpowers run-hook.cmd deseni): fallback mantigi BU dosyanin
REM icinde; hooks.json tek tirnakli TEK komut cagirir.
REM Kullanim: run-hook.cmd <mod>
REM   (hook-prompt | hook-postwrite | hook-denetle | hook-pretool | hook-acilis)
REM Mod gecisi JENERIKTIR (--%1): yeni hook modlari bu dosyada degisiklik
REM gerektirmez — v0.5.8.5 hook-acilis (SessionStart) bu yoldan gecer.
REM CWD'ye DOKUNMAZ: pipeline_kayit.py dava kokunu CWD'den okur.
REM STDIN python'a AKTARILIR (cocuk surec miras alir) — hook-pretool payload'i
REM (tool_input) bu kanaldan okur; asla tuketilmez/kesilmez.

REM PERFORMANS (v0.5.16.2): hedef artik hook_giris.py — o, pipeline_kayit.py'yi
REM IMPORT ederek cagirir, boylece Python bytecode'u __pycache__'ten okur.
REM `__main__` olarak kosulan bir betigin bytecode'u ASLA onbellege alinmaz;
REM 6300+ satir her hook ateslemesinde sifirdan derleniyordu.
REM OLCUM (Py3.12, net yuk): dogrudan 67.6 ms -> giris betigi 26.3 ms.
REM hook_giris.py yoksa (yarim/eski kurulum) ESKI hedefe dusulur — islev
REM kaybi YOK, sadece eski hiz. Yedek mantigi "if not exist" ile kurulur;
REM zincir operatoru KULLANILMAZ (447 dersi: kabuksuz yurutmede sessiz olum).

if "%~1"=="" exit /b 0
set "HOOK_DIR=%~dp0"
set "OA_SCRIPT=%HOOK_DIR%..\skills\oa-pipeline\scripts\hook_giris.py"
if not exist "%OA_SCRIPT%" set "OA_SCRIPT=%HOOK_DIR%..\skills\oa-pipeline\scripts\pipeline_kayit.py"

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python "%OA_SCRIPT%" --%~1
    exit /b 0
)
where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    py -3 "%OA_SCRIPT%" --%~1
    exit /b 0
)
where python3 >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python3 "%OA_SCRIPT%" --%~1
    exit /b 0
)
REM Python yok — sessizce cik (hook ASLA bloklamaz)
exit /b 0
CMDBLOCK

# Unix/bash tarafi (polyglot): ayni scripti python3/python ile kos.
# PERFORMANS (v0.5.16.2): hedef hook_giris.py (bkz. yukaridaki CMD blogu).
# Yoksa eski hedefe dusulur — islev kaybi YOK, sadece eski hiz.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OA_SCRIPT="${SCRIPT_DIR}/../skills/oa-pipeline/scripts/hook_giris.py"
if [ ! -f "$OA_SCRIPT" ]; then
    OA_SCRIPT="${SCRIPT_DIR}/../skills/oa-pipeline/scripts/pipeline_kayit.py"
fi
if command -v python3 >/dev/null 2>&1; then
    exec python3 "$OA_SCRIPT" "--$1"
elif command -v python >/dev/null 2>&1; then
    exec python "$OA_SCRIPT" "--$1"
fi
exit 0

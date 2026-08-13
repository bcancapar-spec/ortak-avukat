: << 'CMDBLOCK'
@echo off
REM Ortak Avukat hook sarmalayicisi (v0.5.8.2 — 447 yapisal-ariza dersi).
REM NEDEN VAR: masaustu uygulamasi hook komutunu KABUKSUZ calistirabiliyor;
REM "python X || py -3 X" zincirindeki || kabuk operatoru olarak degil
REM python'a arguman olarak gidiyor -> sessiz olum (uc sahada sifir atesleme).
REM Cozum (superpowers run-hook.cmd deseni): fallback mantigi BU dosyanin
REM icinde; hooks.json tek tirnakli TEK komut cagirir.
REM Kullanim: run-hook.cmd <mod>   (hook-prompt | hook-postwrite | hook-denetle)
REM CWD'ye DOKUNMAZ: pipeline_kayit.py dava kokunu CWD'den okur.

if "%~1"=="" exit /b 0
set "HOOK_DIR=%~dp0"
set "OA_SCRIPT=%HOOK_DIR%..\skills\oa-pipeline\scripts\pipeline_kayit.py"

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
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OA_SCRIPT="${SCRIPT_DIR}/../skills/oa-pipeline/scripts/pipeline_kayit.py"
if command -v python3 >/dev/null 2>&1; then
    exec python3 "$OA_SCRIPT" "--$1"
elif command -v python >/dev/null 2>&1; then
    exec python "$OA_SCRIPT" "--$1"
fi
exit 0

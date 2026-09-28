@echo off
rem ============================================
rem  Buka folder ini di VS Code (tinggal klik 2x)
rem ============================================

rem Pindah ke folder tempat file .bat ini berada
cd /d "%~dp0"

rem 1) Coba pakai perintah "code" yang ada di PATH
where code >nul 2>nul
if %errorlevel%==0 (
    code .
    goto :eof
)

rem 2) Kalau tidak ada di PATH, coba lokasi install umum
set "VSCODE_USER=%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"
set "VSCODE_SYS=%ProgramFiles%\Microsoft VS Code\Code.exe"

if exist "%VSCODE_USER%" (
    start "" "%VSCODE_USER%" "%~dp0"
    goto :eof
)

if exist "%VSCODE_SYS%" (
    start "" "%VSCODE_SYS%" "%~dp0"
    goto :eof
)

echo.
echo VS Code tidak ditemukan.
echo Pastikan VS Code sudah terinstall, atau saat install centang
echo opsi "Add to PATH".
echo.
pause

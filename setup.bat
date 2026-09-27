@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title LinguaForge - First Time Setup

set "PYVER=3.11.9"
set "PYURL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
set "PYINSTALLER=%TEMP%\chatterbox_python311.exe"
set "VENV_PY=%~dp0.venv\Scripts\python.exe"
set "FFMPEG_DIR=%~dp0tools\ffmpeg"
set "FFMPEG_EXE=%FFMPEG_DIR%\bin\ffmpeg.exe"
set "FFURL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
set "FFZIP=%TEMP%\chatterbox_ffmpeg.zip"
set "FFTMP=%TEMP%\chatterbox_ffmpeg_extract"
set "MARKER=%~dp0.setup_complete"

call :banner
call :find_python
if errorlevel 1 call :install_python
if errorlevel 1 goto :failed

call :find_python
if errorlevel 1 goto :failed

call :ensure_venv
if errorlevel 1 goto :failed

call :install_pytorch
if errorlevel 1 goto :failed

call :install_deps
if errorlevel 1 goto :failed

call :install_ffmpeg
if errorlevel 1 goto :failed

call :verify
if errorlevel 1 goto :failed

>"%MARKER%" echo LinguaForge setup completed successfully on %date% %time%

echo.
echo ============================================================
echo                    SETUP COMPLETE
echo ============================================================
echo.
echo Everything required by LinguaForge is installed.
echo.
echo Next step: double-click run.bat
 echo.
pause
exit /b 0

:banner
echo.
echo ============================================================
echo                 LinguaForge SETUP
echo ============================================================
echo.
echo This setup will install Python 3.11, create the project
echo virtual environment, install the exact Chatterbox runtime,
echo install bundled FFmpeg, and verify CUDA / Perth / Chatterbox.
echo.
exit /b 0

:find_python
set "PYTHON_CMD="
py -3.11 -c "import sys; assert sys.version_info[:2]==(3,11); print(sys.version)" >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.11"
    echo [OK] Python 3.11 found.
    exit /b 0
)
python -c "import sys; assert sys.version_info[:2]==(3,11); print(sys.version)" >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    echo [OK] Python 3.11 found.
    exit /b 0
)
exit /b 1

:install_python
echo.
echo [1/6] Python 3.11 was not found. Downloading it now...
echo.
where curl.exe >nul 2>&1
if not errorlevel 1 (
    curl.exe -L --fail --retry 3 -o "%PYINSTALLER%" "%PYURL%"
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -UseBasicParsing -Uri '%PYURL%' -OutFile '%PYINSTALLER%'"
)
if not exist "%PYINSTALLER%" (
    echo [ERROR] Could not download Python.
    exit /b 1
)

echo Installing Python 3.11 for the current Windows user...
"%PYINSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_launcher=1
if errorlevel 1 (
    echo [ERROR] Python installation failed. Error code: %errorlevel%
    exit /b 1
)

del /q "%PYINSTALLER%" >nul 2>&1
call :find_python
if errorlevel 1 (
    echo [ERROR] Python was installed but cannot be found.
    exit /b 1
)
exit /b 0

:ensure_venv
echo.
echo [2/6] Preparing the project virtual environment...
if exist "%VENV_PY%" (
    echo [OK] .venv already exists.
) else (
    "%PYTHON_CMD%" -m venv ".venv"
    if errorlevel 1 (
        echo [ERROR] Could not create .venv.
        exit /b 1
    )
    echo [OK] .venv created.
)

"%VENV_PY%" -m pip install --upgrade pip >nul
if errorlevel 1 echo [WARNING] pip upgrade failed; continuing.
exit /b 0

:install_pytorch
echo.
echo [3/6] Installing the exact PyTorch CUDA 12.4 runtime...
echo This may take several minutes.
echo.
"%VENV_PY%" -m pip install --disable-pip-version-check --upgrade ^
 torch==2.6.0+cu124 ^
 torchvision==0.21.0+cu124 ^
 torchaudio==2.6.0+cu124 ^
 --index-url https://download.pytorch.org/whl/cu124
if errorlevel 1 (
    echo [ERROR] PyTorch installation failed.
    exit /b 1
)
exit /b 0

:install_deps
echo.
echo [4/6] Installing Chatterbox and supporting packages...
echo.
"%VENV_PY%" -m pip install --disable-pip-version-check --upgrade ^
 chatterbox-tts==0.1.7 ^
 resemble-perth==1.0.1 ^
 setuptools==80.10.2 ^
 soundfile==0.14.0 ^
 numpy ^
 PySide6==6.11.2 ^
 PySide6-Fluent-Widgets==1.11.3
if errorlevel 1 (
    echo [ERROR] Chatterbox dependencies installation failed.
    exit /b 1
)
exit /b 0

:install_ffmpeg
echo.
echo [5/6] Preparing bundled FFmpeg...
if exist "%FFMPEG_EXE%" (
    echo [OK] Bundled FFmpeg already exists.
    exit /b 0
)

where ffmpeg.exe >nul 2>&1
if not errorlevel 1 (
    echo [OK] FFmpeg already exists in Windows PATH.
    exit /b 0
)

echo Downloading FFmpeg...
if exist "%FFTMP%" rmdir /s /q "%FFTMP%" >nul 2>&1
where curl.exe >nul 2>&1
if not errorlevel 1 (
    curl.exe -L --fail --retry 3 -o "%FFZIP%" "%FFURL%"
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -UseBasicParsing -Uri '%FFURL%' -OutFile '%FFZIP%'"
)
if not exist "%FFZIP%" (
    echo [ERROR] Could not download FFmpeg.
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '%FFZIP%' -DestinationPath '%FFTMP%' -Force"
if errorlevel 1 (
    echo [ERROR] Could not extract FFmpeg.
    exit /b 1
)

if not exist "%FFTMP%" (
    echo [ERROR] FFmpeg extraction folder was not created.
    exit /b 1
)

for /d %%D in ("%FFTMP%\ffmpeg-*") do (
    if exist "%%D\bin\ffmpeg.exe" (
        mkdir "%~dp0tools" >nul 2>&1
        if exist "%FFMPEG_DIR%" rmdir /s /q "%FFMPEG_DIR%" >nul 2>&1
        move "%%D" "%FFMPEG_DIR%" >nul
        goto :ffmpeg_moved
    )
)

echo [ERROR] FFmpeg executable was not found after extraction.
exit /b 1

:ffmpeg_moved
del /q "%FFZIP%" >nul 2>&1
rmdir /s /q "%FFTMP%" >nul 2>&1
if not exist "%FFMPEG_EXE%" (
    echo [ERROR] FFmpeg installation failed.
    exit /b 1
)
echo [OK] Bundled FFmpeg installed.
exit /b 0

:verify
echo.
echo [6/6] Verifying the complete runtime...
echo.

"%VENV_PY%" -c "import sys, torch, torchvision, torchaudio, soundfile, numpy, perth, PySide6, qfluentwidgets; from chatterbox.tts_turbo import ChatterboxTurboTTS; assert sys.version_info[:2]==(3,11); assert torch.__version__=='2.6.0+cu124'; assert torchvision.__version__=='0.21.0+cu124'; assert torchaudio.__version__=='2.6.0+cu124'; assert callable(perth.PerthImplicitWatermarker); print('Python:', sys.version.split()[0]); print('Torch:', torch.__version__); print('Torchvision:', torchvision.__version__); print('Torchaudio:', torchaudio.__version__); print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NOT AVAILABLE'); print('Perth watermarker: OK'); print('Chatterbox import: OK'); print('PySide6: OK'); print('QFluentWidgets: OK')"
if errorlevel 1 (
    echo.
    echo [ERROR] Runtime verification failed.
    echo The installation is incomplete. No setup marker was created.
    exit /b 1
)

if exist "%FFMPEG_EXE%" (
    "%FFMPEG_EXE%" -version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Bundled FFmpeg failed its test.
        exit /b 1
    )
    echo FFmpeg: bundled and working.
) else (
    ffmpeg.exe -version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] FFmpeg is not available.
        exit /b 1
    )
    echo FFmpeg: PATH and working.
)

"%VENV_PY%" -m pip check
if errorlevel 1 (
    echo [ERROR] pip check found broken requirements.
    exit /b 1
)

echo.
echo [OK] All runtime checks passed.
exit /b 0

:failed
echo.
echo ============================================================
echo                      SETUP FAILED
echo ============================================================
echo.
echo Do not run the application yet.
echo Fix the error shown above and run setup.bat again.
echo.
pause
exit /b 1

@echo off

rem Base Path Setting
path C:\Windows
path C:\Windows\System32;%path%
path C:\Windows\System32\Wbem;%path%
path C:\Windows\System32\WindowsPowerShell\v1.0;%path%

cd %~dp0

set MINICONDA_DIR=%cd%\tools\miniconda3
path %MINICONDA_DIR%;%path%
path %cd%;%path%
set PYTHONPATH=%path%

if exist "%MINICONDA_DIR%" (
    echo Miniconda is already installed in %MINICONDA_DIR%
) else (
    echo Miniconda is not installed. Installing Miniconda...
    set MINICONDA_INSTALLER_SCRIPT=Miniconda3-py312_24.3.0-0-Windows-x86_64.exe
    curl -o %MINICONDA_INSTALLER_SCRIPT% https://repo.anaconda.com/miniconda/%MINICONDA_INSTALLER_SCRIPT%
    start /wait "" %MINICONDA_INSTALLER_SCRIPT% /InstallationType=JustMe /S /D=%MINICONDA_DIR%
    del %MINICONDA_INSTALLER_SCRIPT%
    echo Miniconda has been installed to %MINICONDA_DIR%
    
    echo Installing Python library...
    python -m pip install -r requirements.txt --no-warn-script-location
    echo Setup completed.
)

python -V

python .\jhdsfinder\gui\main.py
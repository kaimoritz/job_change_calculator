REM This will create a new virtual environment and installing libs listed in requirements.txt

@Echo Off



Set "VIRTUAL_ENV=venv_job_change_calculator"

If Not Exist "%VIRTUAL_ENV%\Scripts\activate.bat" (
    echo Creating a new virtual environment....
    python.exe -m pip install --upgrade pip
    echo Checking pip --version....
    pip --version
    pip.exe install virtualenv
    python.exe -m venv --clear %VIRTUAL_ENV%
) else (
    echo Using existing virtual environment....
)

If Not Exist "%VIRTUAL_ENV%\Scripts\activate.bat" Exit /B 1

Call "%VIRTUAL_ENV%\Scripts\activate.bat"
python.exe -m pip install --upgrade pip
echo Checking: pip --version....
pip --version

pip.exe install -r requirements.txt

echo Yeah! Your virtual environment is now ready to use.
python --version
echo Path to your virtual environment: %VIRTUAL_ENV%
pause
Exit /B 0
Set-Location -LiteralPath $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot "venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Error "Project virtual environment not found at venv\Scripts\python.exe"
    exit 1
}

& $venvPython -m streamlit run app.py

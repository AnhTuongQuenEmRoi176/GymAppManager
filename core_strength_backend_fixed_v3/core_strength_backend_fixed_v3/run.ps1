Set-Location $PSScriptRoot

if (-not (Test-Path '.venv\Scripts\python.exe')) {
  Write-Error "Chưa có .venv của backend tại $PSScriptRoot\.venv. Hãy chạy .\setup.ps1 trước."
  exit 1
}

& .\.venv\Scripts\python.exe -c 'import uvicorn'
if ($LASTEXITCODE -ne 0) {
  & .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

& .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

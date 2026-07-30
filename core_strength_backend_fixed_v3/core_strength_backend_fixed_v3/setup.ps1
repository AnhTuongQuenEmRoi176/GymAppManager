Set-Location $PSScriptRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue) -and -not (Get-Command py -ErrorAction SilentlyContinue)) {
  Write-Error 'Không tìm thấy Python trong PATH.'
  exit 1
}

if (-not (Test-Path '.venv\Scripts\python.exe')) {
  if (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 -m venv .venv
  } else {
    python -m venv .venv
  }
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not (Test-Path '.env')) { Copy-Item '.env.example' '.env' }
Write-Host "Đã cài đặt xong vào $PSScriptRoot\.venv"

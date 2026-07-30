$ErrorActionPreference = 'Stop'
$projectRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location $projectRoot

if (-not (Get-Command flutter -ErrorAction SilentlyContinue)) {
  throw 'Chưa cài Flutter hoặc Flutter chưa có trong PATH.'
}

$backup = Join-Path ([System.IO.Path]::GetTempPath()) ("core_strength_" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $backup | Out-Null
Copy-Item -Recurse -Force (Join-Path $projectRoot 'lib') $backup
Copy-Item -Force (Join-Path $projectRoot 'pubspec.yaml') $backup
Copy-Item -Force (Join-Path $projectRoot 'analysis_options.yaml') $backup

try {
  flutter create --project-name core_strength_mobile --org com.corestrength --platforms android,ios,web .

  Remove-Item -Recurse -Force (Join-Path $projectRoot 'lib')
  Copy-Item -Recurse -Force (Join-Path $backup 'lib') $projectRoot
  Copy-Item -Force (Join-Path $backup 'pubspec.yaml') $projectRoot
  Copy-Item -Force (Join-Path $backup 'analysis_options.yaml') $projectRoot

  flutter pub get
  Write-Host ''
  Write-Host 'Đã tạo platform Android/iOS/Web và cài package.' -ForegroundColor Green
  Write-Host 'Chạy demo: flutter run'
} finally {
  Remove-Item -Recurse -Force $backup -ErrorAction SilentlyContinue
}

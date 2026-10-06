$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectDir ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Create the project virtual environment and install requirements.txt first."
}

$tesseractCommand = Get-Command tesseract.exe -ErrorAction SilentlyContinue
$tesseractCandidates = @(
    $(if ($tesseractCommand) { Split-Path -Parent $tesseractCommand.Source }),
    "C:\Program Files\Tesseract-OCR",
    "C:\Program Files (x86)\Tesseract-OCR"
) | Where-Object { $_ }

$tesseractDir = $tesseractCandidates | Where-Object {
    Test-Path (Join-Path $_ "tesseract.exe")
} | Select-Object -First 1

if (-not $tesseractDir) {
    throw "Tesseract OCR was not found. Install it with eng, vie, and osd language data."
}

$payloadDir = Join-Path $projectDir "build\installer_payload\tesseract"
$payloadTessdata = Join-Path $payloadDir "tessdata"
New-Item -ItemType Directory -Force -Path $payloadTessdata | Out-Null

Copy-Item (Join-Path $tesseractDir "tesseract.exe") $payloadDir -Force
Copy-Item (Join-Path $tesseractDir "*.dll") $payloadDir -Force
Copy-Item (Join-Path $tesseractDir "tessdata\*") $payloadTessdata -Recurse -Force

$license = Join-Path $tesseractDir "doc\LICENSE"
if (-not (Test-Path $license)) {
    throw "Tesseract license file was not found at $license"
}
Copy-Item $license (Join-Path $payloadDir "LICENSE") -Force

foreach ($language in @("eng", "vie", "osd")) {
    if (-not (Test-Path (Join-Path $payloadTessdata "$language.traineddata"))) {
        throw "Missing Tesseract language data: $language"
    }
}

Push-Location $projectDir
try {
    & $python -m PyInstaller --noconfirm .\markitdown_gui.spec
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }
} finally {
    Pop-Location
}

$makensisCandidates = @(
    (Get-Command makensis.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1),
    (Join-Path $env:LOCALAPPDATA "Programs\NSIS\makensis.exe"),
    (Join-Path $env:ProgramFiles "NSIS\makensis.exe"),
    (Join-Path ${env:ProgramFiles(x86)} "NSIS\makensis.exe")
) | Where-Object { $_ -and (Test-Path $_) }

$makensis = $makensisCandidates | Select-Object -First 1
if (-not $makensis) {
    throw "NSIS 3 was not found. Install NSIS and rerun this script."
}

& $makensis (Join-Path $PSScriptRoot "MarkitdownTool.nsi")
if ($LASTEXITCODE -ne 0) {
    throw "NSIS compilation failed with exit code $LASTEXITCODE"
}

Write-Host "Installer created: $(Join-Path $projectDir 'dist\MarkitdownTool-Setup.exe')"

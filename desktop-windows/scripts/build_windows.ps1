$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if ($env:PROCESSOR_ARCHITECTURE -notmatch "64") {
    throw "O build deve ser executado em Windows x64."
}

if (!(Test-Path ".venv/Scripts/python.exe")) {
    py -3.12 -m venv .venv
}
$Python = Join-Path $Root ".venv/Scripts/python.exe"
& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements-build.txt
& $Python scripts/download_model.py
& $Python -m py_compile main.py analysis_runtime.py
& $Python -m PyInstaller --noconfirm --clean app.spec

$Out = Join-Path $Root "dist/PMAC-Analise-Formacao"
New-Item -ItemType Directory -Force "$Out/notebook", "$Out/assets", "$Out/models" | Out-Null
Copy-Item "notebook/ferramenta_preditiva_pmac.ipynb" "$Out/notebook/" -Force
Copy-Item "assets/pmac-assinatura-horizontal.png", "assets/pmac-brasao.webp", "assets/pmac-icon.png" "$Out/assets/" -Force
Copy-Item "licenses/Apache-2.0.txt" "$Out/" -Force
Copy-Item "licenses/NOTICE.txt" "$Out/AVISOS-TERCEIROS.txt" -Force
Copy-Item "LICENSES.md" "$Out/" -Force
New-Item -ItemType Directory -Force "$Out/models/paraphrase-multilingual-MiniLM-L12-v2" | Out-Null
Copy-Item "models/paraphrase-multilingual-MiniLM-L12-v2/*" "$Out/models/paraphrase-multilingual-MiniLM-L12-v2/" -Recurse -Force
Copy-Item "README.md" "$Out/LEIA-ME.txt" -Force

$SmokeOut = Join-Path $env:TEMP "pmac-smoke-output"
$SmokeEvents = Join-Path $env:TEMP "pmac-smoke-events.jsonl"
if (Test-Path $SmokeOut) { Remove-Item $SmokeOut -Recurse -Force }
& "$Out/PMAC-Analise-Formacao.exe" --worker "tests/fixtures/mini_pmac.csv" $SmokeOut --event-file $SmokeEvents
if ($null -ne $LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "O worker empacotado encerrou com código $LASTEXITCODE" }
if (!(Test-Path $SmokeEvents)) { throw "O worker empacotado não criou o arquivo de eventos." }
$SmokeEventText = Get-Content $SmokeEvents -Raw
if ($SmokeEventText -notmatch '"event": "run_completed"') { throw "O worker empacotado não concluiu a análise." }
if (!(Test-Path (Join-Path $SmokeOut "resultado_analise_pmac_completo.csv"))) { throw "O executável empacotado não gerou os CSVs esperados." }

$Release = Join-Path $Root "release"
New-Item -ItemType Directory -Force $Release | Out-Null
$Zip = Join-Path $Release "PMAC-Analise-Formacao-Windows-x64.zip"
if (Test-Path $Zip) { Remove-Item $Zip -Force }
Compress-Archive -Path "$Out/*" -DestinationPath $Zip -CompressionLevel Optimal
Get-FileHash $Zip -Algorithm SHA256 | Format-List
Write-Host "Pacote criado: $Zip"

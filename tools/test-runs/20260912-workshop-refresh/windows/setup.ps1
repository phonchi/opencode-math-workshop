$ErrorActionPreference = 'Stop'
$root = 'C:\Users\User\Documents\ai-math-refresh-20260912'
Set-Location $root
$uv = 'C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe'
$oc = 'C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\SST.opencode_Microsoft.Winget.Source_8wekyb3d8bbwe\opencode.exe'
$env:PATH = (Split-Path $uv) + ';' + (Split-Path $oc) + ';' + $env:PATH
$env:XDG_CONFIG_HOME = "$root\isolated\config"
$env:XDG_DATA_HOME = "$root\isolated\data"
$env:XDG_CACHE_HOME = "$root\isolated\cache"
$env:OPENCODE_CONFIG_DIR = "$root\isolated\config\opencode"
$env:OPENCODE_DISABLE_CLAUDE_CODE = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:MPLBACKEND = 'Agg'
New-Item -ItemType Directory -Force "$root\evidence" | Out-Null
Start-Transcript -Path "$root\evidence\setup-transcript.log" -Force
& $uv --version
& $oc --version
& $uv sync
if ($LASTEXITCODE -ne 0) { throw 'uv sync failed' }
& $uv run python -c 'import platform,numpy,sklearn,matplotlib,networkx,scipy; print(platform.platform()); print(numpy.__version__,sklearn.__version__,scipy.__version__)'
if ($LASTEXITCODE -ne 0) { throw 'imports failed' }
& $uv run python tools/verify_math.py --out evidence/reference
if ($LASTEXITCODE -ne 0) { throw 'math verification failed' }
Stop-Transcript

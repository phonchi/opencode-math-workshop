param([string]$Task='hello',[string]$Mode='auto',[string]$ProjectName='',[string]$SessionId='')
$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding
$OutputEncoding = [Console]::OutputEncoding
$root='C:\Users\User\Documents\ai-math-refresh-20260912'
$uv='C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe'
$oc='C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\SST.opencode_Microsoft.Winget.Source_8wekyb3d8bbwe\opencode.exe'
$env:PATH=(Split-Path $uv)+';'+(Split-Path $oc)+';'+$env:PATH
$env:XDG_CONFIG_HOME="$root\isolated\config"
$env:XDG_DATA_HOME="$root\isolated\data"
$env:XDG_CACHE_HOME="$root\isolated\cache"
$env:OPENCODE_CONFIG_DIR="$root\isolated\config\opencode"
$env:OPENCODE_DISABLE_CLAUDE_CODE='1'
$env:PYTHONIOENCODING='utf-8'
$env:MPLBACKEND='Agg'
Get-ChildItem Env: | Where-Object { $_.Name -match 'API_KEY|AUTH_TOKEN' } | ForEach-Object { Remove-Item ('Env:'+$_.Name) }
$project="$root\agent-$Task-$Mode"
if ($ProjectName) { $project="$root\$ProjectName" }
New-Item -ItemType Directory -Force $project,"$project\figs","$project\notes" | Out-Null
foreach($file in @('AGENTS.md','opencode.json','pyproject.toml','uv.lock')) { Copy-Item "$root\$file" "$project\$file" }
Set-Location $project
$prompt=[IO.File]::ReadAllText("$root\prompts\$Task.txt",[Text.Encoding]::UTF8)
& $uv sync 2>&1 | Out-File "$root\evidence\$Task-$Mode-setup.log" -Encoding utf8
$args=@('run','--model','opencode/big-pickle','--format','json')
if($Mode -eq 'auto') {$args+='--auto'}
if ($SessionId) { $args+=@('--session',$SessionId) }
$args+=$prompt
& $oc @args 2>&1 | Tee-Object -FilePath "$root\evidence\$Task-$Mode-agent.log"
$code=$LASTEXITCODE
@{task=$Task;mode=$Mode;exit_code=$code;project=$project;time=(Get-Date -Format o)} | ConvertTo-Json | Out-File "$root\evidence\$Task-$Mode-result.json" -Encoding utf8
exit $code

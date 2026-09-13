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

Set-Location "$root\agent-workflow-auto"
& $oc debug skill 2>&1 | Out-File "$root\evidence\debug-skill.log" -Encoding utf8
& $oc debug agent math-reviewer 2>&1 | Out-File "$root\evidence\debug-math-reviewer.log" -Encoding utf8

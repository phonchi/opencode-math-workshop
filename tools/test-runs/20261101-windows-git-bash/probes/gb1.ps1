[Console]::OutputEncoding=[Text.UTF8Encoding]::new()
$gb='C:\Program Files\Git'
'git version: ' + (& "$gb\cmd\git.exe" --version)
'pcon setting: ' + (Get-Content "$gb\etc\git-bash.config" -ErrorAction SilentlyContinue)
Get-ItemProperty 'HKLM:\SOFTWARE\GitForWindows' -ErrorAction SilentlyContinue | Select-Object CurrentVersion,InstallPath | Format-List
'wt: ' + (Get-Command wt.exe -ErrorAction SilentlyContinue).Source
'env PYTHONUTF8 user: ' + [Environment]::GetEnvironmentVariable('PYTHONUTF8','User')
$out=Join-Path $env:TEMP 'gb-tty.txt'; Remove-Item $out -ErrorAction SilentlyContinue
$u=$out -replace '\\','/'
$inner="cd /c/ai-math-lab; { echo SHELL=`$SHELL MSYS=`$MSYS TERM=`$TERM; command -v opencode uv git; opencode --version; uv run python -c 'import sys;print(`"py stdin tty`",sys.stdin.isatty())' ; test -t 0 && echo bash-stdin-tty; } >'$u' 2>&1 </dev/tty"
$p=Start-Process "$gb\usr\bin\mintty.exe" -ArgumentList '-e','/usr/bin/bash','-lc',"`"$inner`"" -PassThru
$p.WaitForExit(30000)|Out-Null; if(-not $p.HasExited){Stop-Process -Id $p.Id -Force}
'--- inside mintty'; if(Test-Path $out){[IO.File]::ReadAllText($out)}else{'(no output)'}
# auto shell detection when launched from Git Bash, no shell config
$port=49530;$base="http://127.0.0.1:$port"
function Call($m,$path,$body){ $wc=New-Object Net.WebClient; $wc.Encoding=[Text.Encoding]::UTF8; $wc.Headers['Content-Type']='application/json'; if($m -eq 'GET'){return $wc.DownloadString("$base$path")}; return $wc.UploadString("$base$path",$m,$body) }
$sv=Start-Process "$gb\bin\bash.exe" -ArgumentList '-lc',"`"cd /c/ai-math-lab; exec opencode serve --port $port --hostname 127.0.0.1`"" -PassThru -WindowStyle Hidden
try{
 $up=$false;1..40|%{if(-not $up){try{Call GET '/config' $null|Out-Null;$up=$true}catch{Start-Sleep -Milliseconds 500}}}
 "server from git bash up: $up"
 $sid=(Call POST '/session?directory=C:%5Cai-math-lab' '{"title":"encoding-probe"}'|ConvertFrom-Json).id
 $b=@{agent='build';command='echo BASH=$BASH_VERSION; [Environment]::CommandLine; ls -la | head -2'}|ConvertTo-Json -Compress
 $r=Call POST "/session/$sid/shell?directory=C:%5Cai-math-lab" $b|ConvertFrom-Json; $r.parts|%{if($_.type -eq 'tool'){$_.state.output}}
 Call DELETE "/session/$sid`?directory=C:%5Cai-math-lab" ''|Out-Null
}finally{ & taskkill /PID $sv.Id /T /F 2>&1|Out-Null; Get-CimInstance Win32_Process -Filter "name='opencode.exe'"|?{$_.CommandLine -match "--port $port"}|%{Stop-Process -Id $_.ProcessId -Force} }

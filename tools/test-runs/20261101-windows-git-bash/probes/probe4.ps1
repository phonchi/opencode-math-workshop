[Console]::OutputEncoding=[Text.UTF8Encoding]::new()
$exe=(Get-Command opencode).Source; $port=49526; $base="http://127.0.0.1:$port"
$env:PYTHONUTF8='1'
function Call($m,$path,$body){ $wc=New-Object Net.WebClient; $wc.Encoding=[Text.Encoding]::UTF8; $wc.Headers['Content-Type']='application/json'; if($m -eq 'GET'){return $wc.DownloadString("$base$path")}; return $wc.UploadString("$base$path",$m,$body) }
$zh=[string]::Join('',[char]0x4E2D,[char]0x6587)
foreach($cfg in @($null,'{"shell":"C:\\Program Files\\Git\\bin\\bash.exe"}')){
 if($cfg){$env:OPENCODE_CONFIG_CONTENT=$cfg;'##### git-bash + PYTHONUTF8=1'}else{Remove-Item Env:OPENCODE_CONFIG_CONTENT -ErrorAction SilentlyContinue;'##### powershell + PYTHONUTF8=1'}
 $p=Start-Process $exe -ArgumentList 'serve','--port',$port,'--hostname','127.0.0.1' -WorkingDirectory 'C:\ai-math-lab' -PassThru -WindowStyle Hidden
 try{
  $up=$false; 1..40|%{ if(-not $up){ try{ Call GET '/config' $null|Out-Null; $up=$true }catch{ Start-Sleep -Milliseconds 500 } } }
  $sid=(Call POST '/session?directory=C:%5Cai-math-lab' '{"title":"encoding-probe"}'|ConvertFrom-Json).id
  $py='uv run python -c "print(chr(0x4e2d)+chr(0x6587))"'
  $b=@{agent='build';command=$py}|ConvertTo-Json -Compress
  $r=Call POST "/session/$sid/shell?directory=C:%5Cai-math-lab" $b|ConvertFrom-Json; $r.parts|%{ if($_.type -eq 'tool'){ $_.state.output } }
  try{ Call DELETE "/session/$sid`?directory=C:%5Cai-math-lab" ''|Out-Null }catch{}
 }finally{ Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue; Start-Sleep 1 }
}

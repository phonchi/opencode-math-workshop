[Console]::OutputEncoding=[Text.UTF8Encoding]::new()
$exe=(Get-Command opencode).Source; $port=49525; $base="http://127.0.0.1:$port"
$env:OPENCODE_CONFIG_CONTENT='{"shell":"C:\\Program Files\\Git\\bin\\bash.exe"}'
function Call($m,$path,$body){ $wc=New-Object Net.WebClient; $wc.Encoding=[Text.Encoding]::UTF8; $wc.Headers['Content-Type']='application/json'; if($m -eq 'GET'){return $wc.DownloadString("$base$path")}; return $wc.UploadString("$base$path",$m,$body) }
$p=Start-Process $exe -ArgumentList 'serve','--port',$port,'--hostname','127.0.0.1' -WorkingDirectory 'C:\ai-math-lab' -PassThru -WindowStyle Hidden
try{
 $up=$false; 1..40|%{ if(-not $up){ try{ Call GET '/config' $null|Out-Null; $up=$true }catch{ Start-Sleep -Milliseconds 500 } } }
 $sid=(Call POST '/session?directory=C:%5Cai-math-lab' '{"title":"encoding-probe"}'|ConvertFrom-Json).id
 $zh=[string]::Join('',[char]0x4E2D,[char]0x6587)
 foreach($c in @('ls -la | head -4',"echo $zh","mkdir -p /tmp/zhprobe; touch /tmp/zhprobe/$zh.txt; ls /tmp/zhprobe; rm -r /tmp/zhprobe","uv run python -c `"print('$zh')`"","uv run python -c `"import sys; print(sys.stdout.encoding)`"")){
  "=== $c"; $b=@{agent='build';command=$c}|ConvertTo-Json -Compress
  try{ $r=Call POST "/session/$sid/shell?directory=C:%5Cai-math-lab" $b|ConvertFrom-Json; $r.parts|%{ if($_.type -eq 'tool'){ $_.state.output } } }catch{ "ERR: $_" }
 }
 try{ Call DELETE "/session/$sid`?directory=C:%5Cai-math-lab" ''|Out-Null; 'session deleted' }catch{}
}finally{ Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }

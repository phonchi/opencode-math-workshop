[Console]::OutputEncoding=[Text.UTF8Encoding]::new()
$port=49517; $base="http://127.0.0.1:$port"
$env:OPENCODE_UTF8_DEBUG='1'
$dbg=Join-Path $env:TEMP 'utf8-plugin.log'
if(Test-Path $dbg){"debug log pre-exists: $((Get-Item $dbg).Length) bytes"; $start=(Get-Item $dbg).Length}else{$start=0}
$exe=(Get-Command opencode).Source
$p=Start-Process $exe -ArgumentList 'serve','--port',$port,'--hostname','127.0.0.1' -WorkingDirectory 'C:\ai-math-lab' -PassThru -WindowStyle Hidden
function Call($m,$path,$body){
  $wc=New-Object Net.WebClient; $wc.Encoding=[Text.Encoding]::UTF8; $wc.Headers['Content-Type']='application/json'
  $u="$base$path"
  if($m -eq 'GET'){return $wc.DownloadString($u)}
  return $wc.UploadString($u,$m,$body)
}
try{
  $up=$false; 1..40|%{ if(-not $up){ try{ Call GET '/config' $null|Out-Null; $up=$true }catch{ Start-Sleep -Milliseconds 500 } } }
  "server up: $up"
  $sid=(Call POST '/session?directory=C:%5Cai-math-lab' '{"title":"encoding-probe"}'|ConvertFrom-Json).id
  "session: $sid"
  foreach($c in @('[Console]::OutputEncoding.WebName; [Environment]::CommandLine','!ls')){
    "=== CMD: $c"
    $b=@{agent='build';command=$c}|ConvertTo-Json -Compress
    try{
      $r=Call POST "/session/$sid/shell?directory=C:%5Cai-math-lab" $b|ConvertFrom-Json
      $r.parts|%{ if($_.type -eq 'tool'){ "--- input: " + $_.state.input.command; "--- output:"; $_.state.output } }
    }catch{ "ERR: $_" }
  }
  try{ Call DELETE "/session/$sid`?directory=C:%5Cai-math-lab" ''|Out-Null; 'session deleted' }catch{ "delete err: $_" }
}finally{ Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue; 'server stopped' }
'=== plugin debug log (new lines)'
if(Test-Path $dbg){ $t=[IO.File]::ReadAllText($dbg); $t.Substring([Math]::Min($start,$t.Length)) }else{'(none)'}

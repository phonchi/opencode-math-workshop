[Console]::OutputEncoding=[Text.UTF8Encoding]::new()
$exe=(Get-Command opencode).Source
'pwsh: ' + ((Get-Command pwsh -ErrorAction SilentlyContinue).Source)
'git-bash: ' + (Test-Path 'C:\Program Files\Git\bin\bash.exe')
function Call($m,$base,$path,$body){
  $wc=New-Object Net.WebClient; $wc.Encoding=[Text.Encoding]::UTF8; $wc.Headers['Content-Type']='application/json'
  if($m -eq 'GET'){return $wc.DownloadString("$base$path")}
  return $wc.UploadString("$base$path",$m,$body)
}
function Probe($name,$port,$launcher,$cfg){
  "##### $name"
  $base="http://127.0.0.1:$port"
  if($cfg){$env:OPENCODE_CONFIG_CONTENT=$cfg}else{Remove-Item Env:OPENCODE_CONFIG_CONTENT -ErrorAction SilentlyContinue}
  $bat=Join-Path $env:TEMP "oc-probe-$port.cmd"
  [IO.File]::WriteAllText($bat,"@echo off`r`n$launcher`"$exe`" serve --port $port --hostname 127.0.0.1`r`n",[Text.Encoding]::ASCII)
  $p=Start-Process cmd.exe -ArgumentList '/c',$bat -WorkingDirectory 'C:\ai-math-lab' -PassThru -WindowStyle Hidden
  try{
    $up=$false; 1..40|%{ if(-not $up){ try{ Call GET $base '/config' $null|Out-Null; $up=$true }catch{ Start-Sleep -Milliseconds 500 } } }
    if(-not $up){'server failed';return}
    $sid=(Call POST $base '/session?directory=C:%5Cai-math-lab' '{"title":"encoding-probe"}'|ConvertFrom-Json).id
    foreach($c in @('[Console]::OutputEncoding.WebName','!ls')){
      $b=@{agent='build';command=$c}|ConvertTo-Json -Compress
      try{ $r=Call POST $base "/session/$sid/shell?directory=C:%5Cai-math-lab" $b|ConvertFrom-Json
        $r.parts|%{ if($_.type -eq 'tool'){ ($_.state.output -split "`n")[0] } }
      }catch{ "ERR: $_" }
    }
    try{ Call DELETE $base "/session/$sid`?directory=C:%5Cai-math-lab" ''|Out-Null }catch{}
  }finally{
    & taskkill /PID $p.Id /T /F 2>&1 | Out-Null
    Remove-Item $bat -ErrorAction SilentlyContinue
  }
}
Probe 'A chcp 65001 before launching' 49521 "chcp 65001 >nul`r`n" $null
if(Get-Command pwsh -ErrorAction SilentlyContinue){ Probe 'B shell=pwsh' 49522 '' '{"shell":"pwsh"}' }
Probe 'C shell=cmd' 49523 '' '{"shell":"cmd"}'
if(Test-Path 'C:\Program Files\Git\bin\bash.exe'){ Probe 'D shell=git-bash' 49524 '' '{"shell":"C:\\Program Files\\Git\\bin\\bash.exe"}' }

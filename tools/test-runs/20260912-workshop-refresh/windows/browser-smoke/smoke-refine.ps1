$ErrorActionPreference='Stop'
[Console]::OutputEncoding=New-Object Text.UTF8Encoding
$OutputEncoding=[Console]::OutputEncoding
$root='C:\Users\User\Documents\ai-math-refresh-20260912\browser-smoke'
New-Item -ItemType Directory -Force $root | Out-Null
$edge='C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$port=9337
$process=Start-Process -FilePath $edge -ArgumentList @('--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',"--remote-debugging-port=$port",("--user-data-dir="+$root+'\profile'),'about:blank') -PassThru
$socket=$null
try {
  $ready=$false
  for($i=0;$i -lt 40;$i++){try{$version=Invoke-RestMethod "http://127.0.0.1:$port/json/version";$ready=$true;break}catch{Start-Sleep -Milliseconds 250}}
  if(-not $ready){throw 'Native Edge CDP did not start'}
  $tab=Invoke-RestMethod "http://127.0.0.1:$port/json/new?about:blank" -Method Put
  $socket=New-Object Net.WebSockets.ClientWebSocket
  $socket.ConnectAsync([uri]$tab.webSocketDebuggerUrl,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
  $script:cid=0
  function Cdp($method,$parameters=@{}) {
    $script:cid++
    $id=$script:cid
    $payload=@{id=$id;method=$method;params=$parameters}|ConvertTo-Json -Compress -Depth 60
    $bytes=[Text.Encoding]::UTF8.GetBytes($payload)
    $segment=New-Object 'ArraySegment[byte]' -ArgumentList @(,$bytes)
    $socket.SendAsync($segment,[Net.WebSockets.WebSocketMessageType]::Text,$true,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
    while($true){
      $memory=New-Object IO.MemoryStream
      do {
        $buffer=New-Object byte[] 65536
        $part=New-Object 'ArraySegment[byte]' -ArgumentList @(,$buffer)
        $received=$socket.ReceiveAsync($part,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
        $memory.Write($buffer,0,$received.Count)
      }while(-not $received.EndOfMessage)
      $response=[Text.Encoding]::UTF8.GetString($memory.ToArray())|ConvertFrom-Json
      $memory.Dispose()
      if($response.id -eq $id){if($response.error){throw ($response.error|ConvertTo-Json)};return $response.result}
    }
  }
  function Eval($expression){$value=Cdp 'Runtime.evaluate' @{expression=$expression;returnByValue=$true;awaitPromise=$true;userGesture=$true};if($value.exceptionDetails){throw ($value.exceptionDetails|ConvertTo-Json -Depth 10)};return $value.result.value}
  Cdp 'Page.enable' | Out-Null
  Cdp 'Browser.grantPermissions' @{permissions=@('clipboardReadWrite','clipboardSanitizedWrite')} | Out-Null
  $results=@()
  $base='file://wsl.localhost/Ubuntu/home/phonchi/opencode-math-workshop/'
  foreach($page in @('lab2-pca.html')){
    foreach($width in @(1440)){
      Cdp 'Emulation.setDeviceMetricsOverride' @{width=$width;height=1000;deviceScaleFactor=1;mobile=$false}|Out-Null
      Cdp 'Page.navigate' @{url=($base+$page)}|Out-Null
      Start-Sleep -Seconds 2
      Cdp 'Page.bringToFront' | Out-Null
      $state=Eval '(async()=>{await document.fonts.ready;return {url:location.href,title:document.title,width:innerWidth,scrollWidth:document.documentElement.scrollWidth,heading:document.querySelector("h1")?.textContent,sidebars:document.querySelectorAll("nav").length}})()'
      if(-not $state.heading -or $state.scrollWidth -gt $width){throw ('Bad containment/page: '+($state|ConvertTo-Json))}
      $record=@{page=$page;viewport=$width;state=$state}
      if($page -eq 'lab2-pca.html'){
        $interaction=Eval '(()=>{const v=()=>[document.querySelector("#projection-variance").textContent,document.querySelector("#projection-error").textContent];const initial=v();const slider=document.querySelector("#projection-angle");slider.value=90;slider.dispatchEvent(new Event("input",{bubbles:true}));const changed=v();document.querySelector("#projection-principal").click();const principal=v();document.querySelector("#projection-reset").click();return {initial,changed,principal,reset:v(),angle:slider.value}})()'
        if(($interaction.initial -join '|') -eq ($interaction.changed -join '|')){throw 'PCA slider did not update'}
        if(($interaction.initial -join '|') -ne ($interaction.reset -join '|')){throw 'PCA reset mismatch'}
        $record.interaction=$interaction
        $copy=Eval '(async()=>{const b=document.querySelector("pre.cmd button.copy");if(!b)return {present:false};const c=b.parentElement.querySelector("code");const expected=(c?c.textContent:Array.from(b.parentElement.childNodes).filter(x=>x!==b).map(x=>x.textContent).join("")).trim();b.click();await new Promise(r=>setTimeout(r,400));let matches=null;try{matches=(await navigator.clipboard.readText())===expected}catch(e){}return {present:true,label:b.textContent,matches,commandLength:expected.length}})()'
        $record.copy=$copy
        Eval 'document.querySelector(".pca-explorer").scrollIntoView({block:"start"})' | Out-Null
      }
      $clip=Eval '(()=>{const r=document.querySelector(".pca-explorer").getBoundingClientRect();return {x:r.x+scrollX,y:r.y+scrollY,width:r.width,height:r.height,scale:1}})()'
      $shot=Cdp 'Page.captureScreenshot' @{format='png';captureBeyondViewport=$true;clip=$clip}
      [IO.File]::WriteAllBytes("$root\$($page.Replace('.html',''))-$width-panel.png",[Convert]::FromBase64String($shot.data))
      $results+=$record
    }
  }
  @{browser=$version.Browser;userAgent=$version.'User-Agent';results=$results;status='PASS'}|ConvertTo-Json -Depth 30|Out-File "$root\clipboard-panel-result.json" -Encoding utf8
} finally {
 if($socket){$socket.Dispose()}
 if($process -and -not $process.HasExited){Stop-Process -Id $process.Id -Force}
}

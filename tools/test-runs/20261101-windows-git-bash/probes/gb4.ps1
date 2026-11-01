[Console]::OutputEncoding=[Text.UTF8Encoding]::new()
Add-Type -AssemblyName System.Drawing,System.Windows.Forms
Add-Type @"
using System;using System.Runtime.InteropServices;
public class W{[DllImport("user32.dll")]public static extern bool GetWindowRect(IntPtr h,out R r);[DllImport("user32.dll")]public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint f);[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
public struct R{public int L,T,Ri,B;}}
"@
$gb='C:\Program Files\Git'; $tmp=$env:TEMP; $u=($tmp -replace '\\','/')
function Snap($h,$path){ $r=New-Object W+R; [W]::GetWindowRect($h,[ref]$r)|Out-Null; $b=New-Object Drawing.Bitmap ($r.Ri-$r.L),($r.B-$r.T); $g=[Drawing.Graphics]::FromImage($b); $dc=$g.GetHdc(); [W]::PrintWindow($h,$dc,2)|Out-Null; $g.ReleaseHdc($dc); $b.Save($path); $g.Dispose(); $b.Dispose() }
function Key($k){ [W]::SetForegroundWindow($h)|Out-Null; Start-Sleep -Milliseconds 400; [Windows.Forms.SendKeys]::SendWait($k); Start-Sleep -Milliseconds 800 }
function Paste($t,$k){ Set-Clipboard -Value $t; Key $k }
$zh=[string]::Join('',[char]0x8cbc,[char]0x4e0a,[char]0x6e2c,[char]0x8a66)
$py='uv run python -c "print(chr(0x4e2d)+chr(0x6587))"'
$before=@(Get-Process opencode -ErrorAction SilentlyContinue).Id
$clipOld=$null; try{$clipOld=Get-Clipboard -Raw -ErrorAction Stop}catch{}
try{
[IO.File]::WriteAllText("$tmp\gb-t3.sh","#!/usr/bin/bash`nexport PYTHONUTF8=1`ncd /c/ai-math-lab`nexec opencode`n",[Text.UTF8Encoding]::new($false))
Start-Process "$gb\usr\bin\mintty.exe" -ArgumentList '-t','probe3','-s','110,32','-e','/usr/bin/bash','-l',"$u/gb-t3.sh"
Start-Sleep 10
$w=Get-Process mintty|?{$_.MainWindowTitle -match 'probe3|OpenCode'}|Select -First 1; $h=$w.MainWindowHandle
Key '!'; Paste 'ls -la | head -3' '^v'; Key '{ENTER}'; Start-Sleep 5; Snap $h "$tmp\q1.png"
Key '!'; Paste $py '^v'; Key '{ENTER}'; Start-Sleep 8; Snap $h "$tmp\q2.png"
Get-Process opencode -ErrorAction SilentlyContinue|?{$before -notcontains $_.Id}|%{Stop-Process -Id $_.Id -Force}
Stop-Process -Id $w.Id -Force -ErrorAction SilentlyContinue
Start-Sleep 1
[IO.File]::WriteAllText("$tmp\gb-t4.sh","#!/usr/bin/bash`nexport PYTHONUTF8=1`ncd /c/ai-math-lab`nexec bash -i`n",[Text.UTF8Encoding]::new($false))
Start-Process "$gb\usr\bin\mintty.exe" -ArgumentList '-t','probe4','-s','100,24','-e','/usr/bin/bash','-l',"$u/gb-t4.sh"
Start-Sleep 5
$w=Get-Process mintty|?{$_.MainWindowTitle}|Select -First 1; "bash window: "+$w.MainWindowTitle; $h=$w.MainWindowHandle
Paste ('echo ctrlv-'+$zh) '^v'; Start-Sleep 1; Snap $h "$tmp\q3.png"; Key '^c'
Paste ('echo shiftins-'+$zh) '+{INSERT}'; Key '{ENTER}'; Start-Sleep 1
Paste $py '+{INSERT}'; Key '{ENTER}'; Start-Sleep 6; Snap $h "$tmp\q4.png"
Stop-Process -Id $w.Id -Force
}finally{ if($clipOld){Set-Clipboard -Value $clipOld}else{Set-Clipboard -Value ' '} }
'done'

[Console]::OutputEncoding=[Text.UTF8Encoding]::new()
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;using System.Runtime.InteropServices;
public class W{[DllImport("user32.dll")]public static extern bool GetWindowRect(IntPtr h,out R r);[DllImport("user32.dll")]public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint f);[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
public struct R{public int L,T,Ri,B;}}
"@
$gb='C:\Program Files\Git'; $tmp=$env:TEMP; $u=($tmp -replace '\\','/')
$sh1=@"
#!/usr/bin/bash
cd /c/ai-math-lab
{ echo "SHELL=`$SHELL MSYS=`$MSYS TERM=`$TERM"; command -v opencode uv git; opencode --version; test -t 0 && echo bash-stdin-tty; uv run python -c "import sys;print('py stdin tty',sys.stdin.isatty())"; } > "$u/gb-tty.txt" 2>&1
"@
[IO.File]::WriteAllText("$tmp\gb-t1.sh",($sh1 -replace "`r",""),[Text.UTF8Encoding]::new($false))
Remove-Item "$tmp\gb-tty.txt" -ErrorAction SilentlyContinue
Start-Process "$gb\usr\bin\mintty.exe" -ArgumentList '-t','probe-a','-e','/usr/bin/bash','-l',"$u/gb-t1.sh"
Start-Sleep 15
'--- inside mintty'; if(Test-Path "$tmp\gb-tty.txt"){[IO.File]::ReadAllText("$tmp\gb-tty.txt")}else{'(no output)'}
function Snap($hwnd,$path){ $r=New-Object W+R; [W]::GetWindowRect($hwnd,[ref]$r)|Out-Null; $bmp=New-Object Drawing.Bitmap ($r.Ri-$r.L),($r.B-$r.T); $g=[Drawing.Graphics]::FromImage($bmp); $dc=$g.GetHdc(); [W]::PrintWindow($hwnd,$dc,2)|Out-Null; $g.ReleaseHdc($dc); $bmp.Save($path); "snap $($bmp.Width)x$($bmp.Height) $path" }
# TUI inside mintty
$sh2="#!/usr/bin/bash`ncd /c/ai-math-lab`nopencode`necho exit=`$? > $u/gb-tui-exit.txt`nsleep 20`n"
[IO.File]::WriteAllText("$tmp\gb-t2.sh",$sh2,[Text.UTF8Encoding]::new($false))
Remove-Item "$tmp\gb-tui-exit.txt" -ErrorAction SilentlyContinue
$before=@(Get-Process opencode -ErrorAction SilentlyContinue).Id
Start-Process "$gb\usr\bin\mintty.exe" -ArgumentList '-t','probe-tui','-s','110,32','-e','/usr/bin/bash','-l',"$u/gb-t2.sh"
Start-Sleep 12
$w=Get-Process mintty -ErrorAction SilentlyContinue|?{$_.MainWindowTitle}
"mintty windows: " + (($w|%{"$($_.Id):$($_.MainWindowTitle)"}) -join ' | ')
$w2=$w|?{$_.MainWindowTitle -match 'probe-tui|opencode|OC'}|Select-Object -First 1
if($w2){ Snap $w2.MainWindowHandle "$tmp\gb-tui-mintty.png" }
'exit file: ' + (Get-Content "$tmp\gb-tui-exit.txt" -ErrorAction SilentlyContinue)
Get-Process opencode -ErrorAction SilentlyContinue|?{$before -notcontains $_.Id}|%{"cleanup opencode "+$_.Id;Stop-Process -Id $_.Id -Force}
Get-Process mintty -ErrorAction SilentlyContinue|?{$_.MainWindowTitle -match 'probe|opencode|OC'}|%{Stop-Process -Id $_.Id -Force}

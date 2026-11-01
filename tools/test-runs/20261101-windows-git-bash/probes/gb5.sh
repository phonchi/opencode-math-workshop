echo MSYSTEM=$MSYSTEM
command -v winget setx notepad
winget --version
setx OC_PROBE_TMP 1
reg query 'HKCU\Environment' //v OC_PROBE_TMP
reg delete 'HKCU\Environment' //v OC_PROBE_TMP //f
cd ~/Documents && pwd

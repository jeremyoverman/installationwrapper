set ELEVATE_APP=D:\Python27\pythonw.exe
set ELEVATE_PARMS=E:\workspace\bfusatool\gui.py
echo Set objShell = CreateObject("Shell.Application") >elevatedapp.vbs
echo Set objWshShell = WScript.CreateObject("WScript.Shell") >>elevatedapp.vbs
echo Set objWshProcessEnv = objWshShell.Environment("PROCESS") >>elevatedapp.vbs
echo objShell.ShellExecute "%ELEVATE_APP%", "%ELEVATE_PARMS%", "", "runas" >>elevatedapp.vbs
cscript elevatedapp.vbs
DEL elevatedapp.vbs
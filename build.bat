@echo off
py -3.6 -m pyinstaller owl-watcher.spec
bash -c "pyinstaller owl-watcher.spec"
pause
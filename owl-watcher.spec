# -*- mode: python -*-

import os
from sys import platform

if platform == 'linux' or platform == 'linux2':
    datas=[('chromedriver', '.')]
elif platform == 'darwin':
    datas=[('chromedriver_osx', '.')]
elif platform == 'win32':
    datas=[('chromedriver.exe', '.')]


a = Analysis(['owl-watcher.py'],
             pathex=['.'],
             binaries=[],
             datas=datas,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=None)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='owl-watcher',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True , icon='owl-watcher.ico')

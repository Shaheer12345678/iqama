# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build spec for Iqama.

Build a single-file Windows .exe (no Python installation required to
run it) with:

    pyinstaller packaging/iqama.spec --distpath dist --workpath build

Run from the project root. Output lands in dist/Iqama.exe.

To swap in real artwork: replace resources/icon.ico (used both here,
for the exe's own icon, and at runtime for the tray icon) -- nothing
else needs to change.
"""
from pathlib import Path

project_root = Path(SPECPATH).parent
src_path = project_root / "src"
resources_path = project_root / "resources"

a = Analysis(
    [str(project_root / "packaging" / "entry_point.py")],
    pathex=[str(src_path)],
    binaries=[],
    datas=[(str(resources_path), "resources")],
    hiddenimports=[
        "plyer.platforms.win.notification",
        "win32timezone",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Iqama",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(resources_path / "icon.ico"),
    version=str(project_root / "packaging" / "version_info.txt"),
)

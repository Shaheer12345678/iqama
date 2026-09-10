"""Registers/unregisters Iqama in the current user's Windows startup.

A prayer reminder app is only useful if it's actually running, so this
writes a value under HKCU\\...\\Run rather than relying on the user to
remember to launch it -- no admin rights needed, no scheduled task.
"""
from __future__ import annotations

import sys
import winreg

from ..config import APP_NAME

RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _launch_command() -> str:
    """Command line that relaunches the app the same way it's running now."""
    if getattr(sys, "frozen", False):
        # Packaged .exe: sys.executable *is* Iqama.exe.
        return f'"{sys.executable}"'
    # Running from source: relaunch via the same interpreter and entry module.
    return f'"{sys.executable}" -m iqama.main'


def is_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_NAME)
        return True
    except FileNotFoundError:
        return False


def set_enabled(enabled: bool) -> None:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_WRITE) as key:
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _launch_command())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass

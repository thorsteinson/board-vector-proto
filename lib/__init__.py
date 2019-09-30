from . import asset_manager
from . import window

_mgr = None
_win = None

def get_asset_mgr():
    global _mgr
    if not _mgr:
        _mgr = asset_manager.AssetManager()
    return _mgr

def get_window():
    global _win
    if not _win:
        _win = window.Window()
    return _win

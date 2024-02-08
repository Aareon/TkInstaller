import ctypes
import getpass
import os
import sys
from pathlib import Path
from tkinter import font

from loguru import logger
from PIL import Image

ROOT_DIR = Path(__file__).parent.parent
ASSETS_DIR = ROOT_DIR / "assets"

UAC_ICON_PATH = ASSETS_DIR / "UAC.png"


def get_default_font():
    # Check if Segoe UI font is available on the system
    if "Segoe UI" in font.families():
        # Configure the font for all widgets
        default_font = font.Font(family="Segoe UI")
        # root
        return default_font


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    if is_admin():
        logger.debug("Already running with administrator privileges.")
    else:
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        if ret >= 33:
            logger.debug("Acquired admin")
        else:
            logger.debug(f"Could not elevate: {ret}")
        sys.exit(0)


def resize_image(image, width, height):
    return image.resize((width, height), Image.BICUBIC)


def get_windows_username():
    try:
        username = os.getenv("USERNAME") or getpass.getuser()
        return username
    except Exception as e:
        logger.exception("Unable to retrieve Windows username:", str(e))
        raise

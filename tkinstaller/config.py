import configparser
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
CONFIG_PATH = ROOT_DIR / "installer_config.ini"

CONFIG = configparser.ConfigParser()
CONFIG.read(CONFIG_PATH)
INSTALLER_CONFIG = CONFIG["Installer"]

GLOBAL_INSTALL_PATH = INSTALLER_CONFIG["global_install_path"]
if "@ProgramFiles@" in GLOBAL_INSTALL_PATH:
    GLOBAL_INSTALL_PATH = Path(
        INSTALLER_CONFIG["global_install_path"].replace(
            "@ProgramFiles@", os.environ.get("ProgramFiles")
        )
    )
elif "@ProgramFiles86@" in GLOBAL_INSTALL_PATH:
    GLOBAL_INSTALL_PATH = Path(
        INSTALLER_CONFIG["global_install_path"].replace(
            "@ProgramFiles86@", os.environ.get("ProgramFiles(x86)")
        )
    )
GLOBAL_INSTALL_EXISTS = GLOBAL_INSTALL_PATH.exists() and GLOBAL_INSTALL_PATH.is_dir()

USER_INSTALL_PATH = Path(
    INSTALLER_CONFIG["user_install_path"].replace(
        "@LocalPrograms@", str(Path.home() / "AppData\\Local\\Programs")
    )
)
USER_INSTALL_EXISTS = USER_INSTALL_PATH.exists() and USER_INSTALL_PATH.is_dir()

APP_EXE_NAME = INSTALLER_CONFIG.get("app_exe_name")

import configparser
from pathlib import Path
import PyInstaller.__main__ as pyinstaller

if __name__ == "__main__":
    ROOT_PATH = Path(__file__).parent
    CONFIG_PATH = ROOT_PATH / "installer_config.ini"
    DIST_PATH = ROOT_PATH / "dist"

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    config = config["Installer"]
    EXE_NAME = config["app_exe_name"]

    pyinstaller.run([
        "__main__.py",
        "--onefile",
        "--noconsole",
        "--icon=.\\assets\\logo.png",
        "--add-data=.\\installer_config.ini:.",
        "--add-data=.\\assets:assets"
    ])

    BUILT_EXE = DIST_PATH / "__main__.exe"
    BUILT_EXE.rename(DIST_PATH / config["app_exe_name"])

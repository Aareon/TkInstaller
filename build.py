import configparser
import shutil
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
    COMP_APP_PATH = config["compressed_app_path"].replace("@HERE@", str(ROOT_PATH))

    pyinstaller.run(
        [
            "__main__.py",
            "--onefile",
            "--noconsole",
            "--icon=.\\assets\\logo.png",
            "--add-data=.\\installer_config.ini:.",
            "--add-data=.\\assets:assets",
            f"--add-data={COMP_APP_PATH}:.",
        ]
    )

    BUILT_EXE = DIST_PATH / "__main__.exe"
    TARGET_EXE = DIST_PATH / config["app_exe_name"]

    if TARGET_EXE.exists():
        TARGET_EXE.unlink()

    BUILT_EXE.rename(TARGET_EXE)

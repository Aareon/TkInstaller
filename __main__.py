import sys
from loguru import logger
from tkinstaller.ui import installer, uninstaller

if __name__ == "__main__":
    logger.debug(sys.argv)
    if "--uninstall" not in sys.argv:
        logger.debug("Running installer")
        installer = installer.InstallerApp()
        sys.exit(installer.run())
    
    uninstaller = uninstaller.UninstallerApp()
    sys.exit(uninstaller.run())


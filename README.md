# TkInstaller
Create an installer for your application using TkInstaller!

## How to use TkInstaller
Firsr you'll need to create a `zip` or `7z` archive containing your application, as well as any data files you need to include.
Then you'll modify the `installer_config.ini` to point to your archive, and change any settings necessary.
Next you can test the installer by executing it with your Python environment.
If it succeeds in installing your app to the location of your choosing, run the included `build.py` to package it all up.
You can then distribute the resulting installer `EXE` however you desire.

## Configuration
You can change the `title`, `version`, and logo of your application by modifying the `installer_config.ini`.
The installer uses placeholders for `Local Programs` and `Program Files`, it is suggested that you don't change the `@variable@` parts unless you know what you're doing.
Make sure to set `compressed_app_path` to the name of your compressed archive containing your application.
Ensure `app_exe_name` matches the EXE you're trying to install, or the "Run after install" option will fail.
You can change the color of the installer "Finished" screen by changing `finished_logo_background` to any RGB value.
> Note:
> `finished_logo_background` does not accept Alpha transparency values, and only accepts RGB.

## Credits
- [Example logo.png](https://www.clipartmax.com/middle/m2H7d3d3N4m2K9G6_music-tambourine-icon-pandereta-en-silueta/)

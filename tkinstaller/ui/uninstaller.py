import shutil
import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import font, ttk

from loguru import logger
from PIL import Image, ImageTk

from tkinstaller import config
from tkinstaller.ui.extractor import DecompressFrame
from tkinstaller.utils import (
    ROOT_DIR,
    UAC_ICON_PATH,
    get_windows_username,
    is_admin,
    resize_image,
    run_as_admin,
)


def delete_folder_with_progress(progress_bar, folder_path):
    def delete_files_in_folder(folder):
        total_files = sum(1 for item in folder.glob("**/*"))
        if total_files == 0:
            return
        progress_per_file = 100 / total_files
        completed_files = 0
        for item in folder.glob("**/*"):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(
                    item
                )  # Use shutil.rmtree() to remove non-empty directories
            completed_files += 1
            progress_bar["value"] = completed_files * progress_per_file
            progress_bar.update_idletasks()  # Update the progress bar

    def delete_folder(folder):
        logger.debug(f"delete folder: {folder}")
        shutil.rmtree(folder)

    def delete_and_update_progress():
        delete_files_in_folder(folder_path)
        delete_folder(folder_path)
        progress_bar.configure(value=100)
        progress_bar.master.event_generate("<<ProgressFinished>>")


    delete_and_update_progress()


class UninstallerApp(tk.Tk):
    __built: bool

    def __init__(self):
        super().__init__()

        logger.debug(f"IsAdmin: {is_admin()}")
        run_as_admin()  # run-run this script if not elevated

        self.UAC_ICON = ImageTk.PhotoImage(
            resize_image(Image.open(UAC_ICON_PATH), 12, 12)
        )

        self.BOLD_FONT = font.Font(weight="bold", size=8)
        self.MED_BOLD_FONT = font.Font(weight="bold", size=12)
        self.BIG_BOLD_FONT = font.Font(weight="bold", size=16)
        self.MIN_FONT = font.Font(size=8)

        self.finished_left_background = config.INSTALLER_CONFIG.get(
            "finished_logo_background", "blue"
        )
        if "," in self.finished_left_background:
            # Convert the RGB components to integers
            red, green, blue = map(int, self.finished_left_background.split(", "))
            self.finished_left_background = f"#{red:02x}{green:02x}{blue:02x}"

        # load image
        image_fp = Path(
            config.INSTALLER_CONFIG["logo_path"].replace("@HERE@", str(ROOT_DIR))
        )
        self.orig_image = Image.open(image_fp)
        small_image = resize_image(self.orig_image, 32, 32)
        self.tk_image = ImageTk.PhotoImage(small_image)

        # Tk variables
        self.selected_option = tk.IntVar(value=0 if not is_admin() else 1)
        self.selected_option_text_default = (
            f"Fresh install for this user ({get_windows_username()})"
        )
        self.selected_option_text = tk.StringVar(
            value=self.selected_option_text_default
        )

        if config.USER_INSTALL_EXISTS:
            self.selected_option_text.set(
                f"There is already a per-user installation. ({config.USER_INSTALL_PATH}) Will reinstall/upgrade."
            )

        self.run_after_install = tk.IntVar(value=1)

        self.__built = False
    
    def forget_all_children(self):
        # Iterate over all children of the master widget
        for child in self.winfo_children():
            for c in child.winfo_children():
                c.pack_forget()
        # Forget (remove) the child widget from the layout
        child.pack_forget()

    def finished_button_pressed(self):
        sys.exit(0)

    def cancel_pressed(self):
        sys.exit(0)

    def back_pressed(self):
        pass

    def uninstall_finished(self, *args):
        self.uninstall_frame.destroy()
        self.progress_bar.destroy()
        self.next_button.destroy()
        title = config.INSTALLER_CONFIG["title"]
        if config.INSTALLER_CONFIG.getboolean("show_version_in_title"):
            title = f"{title} {config.INSTALLER_CONFIG['version']}"
        self.title(f"{title} Uninstall")

        self.finished_frame = tk.Frame(self, height=495, background="white")

        self.finished_left_frame = tk.Frame(
            self.finished_frame, background=self.finished_left_background
        )
        self.finished_image = resize_image(self.orig_image, 80, 80)
        self.finished_tk_image = ImageTk.PhotoImage(self.finished_image)

        finished_image_label = tk.Label(
            self.finished_left_frame,
            image=self.finished_tk_image,
            background=self.finished_left_background,
        )
        finished_image_label.pack(side="top", anchor="center", pady=20)
        finished_text_label = tk.Label(
            self.finished_left_frame,
            text=config.INSTALLER_CONFIG["title"],
            background=self.finished_left_background,
            foreground="white",
            font=self.BIG_BOLD_FONT,
        )

        finished_text_label.pack(side="top", anchor="center")

        self.finished_right_frame = tk.Frame(self.finished_frame, background="white")
        complete_label = tk.Label(
            self.finished_right_frame,
            text=f"Completing {config.INSTALLER_CONFIG['title']} Uninstall",
            font=self.MED_BOLD_FONT,
            background="white",
        )
        complete_label.pack(side="top", anchor="nw", pady=10, padx=6)
        description_label = tk.Label(
            self.finished_right_frame,
            text=(
                f"{config.INSTALLER_CONFIG['title']} has been uninstalled from your computer."
                "\n\nClick Finish to close Setup."
            ),
            font=self.MIN_FONT,
            justify="left",
            background="white",
            wraplength=340,
        )
        description_label.pack(side="top", anchor="nw", pady=10, padx=4)

        style = ttk.Style()
        style.configure("White.TCheckbutton", background="white")

        self.finished_left_frame.pack(
            side="left", anchor="nw", fill="both", expand=True
        )
        self.finished_right_frame.pack(
            side="right", anchor="nw", fill="both", expand=True
        )

        self.buttons_frame = tk.Frame(self, relief="sunken", borderwidth=1)

        self.finish_button = ttk.Button(
            self.buttons_frame,
            text="Finish",
            command=lambda: sys.exit(0),
        )

        self.finished_button = ttk.Button(
            self.buttons_frame, text="Finish", command=self.finished_button_pressed
        )

        self.finished_frame.pack(side="top", anchor="nw", fill="both", expand=True)

        self.cancel_button = ttk.Button(
            self.buttons_frame, text="Cancel", command=self.cancel_pressed
        )
        self.cancel_button.pack(side="right", anchor="nw", padx=8)
        self.finish_button.pack(side="right", anchor="nw")

        self.buttons_frame.pack(side="right", fill="x", expand=True)

    def next_pressed(self):
        self.finished_frame.pack_forget()
        self.next_button.pack_forget()
        self.buttons_frame.pack_forget()

        logger.debug("Uninstalling...")
        self.uninstall_frame = tk.Frame(self, height=495)
        self.progress_bar = ttk.Progressbar(
            master=self.uninstall_frame, orient=tk.HORIZONTAL, length=300, mode="determinate"
        )
        self.progress_bar.pack(side="top", anchor="center", padx=10, pady=30)

        self.bind("<<ProgressFinished>>", self.uninstall_finished)

        if config.GLOBAL_INSTALL_EXISTS:
            logger.debug(f"Uninstalling {config.GLOBAL_INSTALL_PATH}")
            delete_folder_with_progress(self.progress_bar, config.GLOBAL_INSTALL_PATH)

        if config.USER_INSTALL_EXISTS:
            logger.debug(f"Uninstalling {config.USER_INSTALL_PATH}")
            self.progress_bar.configure(value=0)
            delete_folder_with_progress(self.progress_bar, config.USER_INSTALL_PATH)

        if not config.GLOBAL_INSTALL_EXISTS and not config.USER_INSTALL_EXISTS:
            self.uninstall_finished()
        
        self.uninstall_frame.pack(side="top", fill="both", expand=True)
        self.buttons_frame.pack(side="bottom", fill="x", padx=10, pady=10)

    def build(self):
        self.geometry("495x360")

        self.tk.call("wm", "iconphoto", self._w, self.tk_image)

        # Disable resizing in both directions
        self.resizable(width=False, height=False)

        title = config.INSTALLER_CONFIG["title"]
        if config.INSTALLER_CONFIG.getboolean("show_version_in_title"):
            title = f"{title} {config.INSTALLER_CONFIG['version']}"
        self.title(f"{title} Uninstall")

        self.finished_frame = tk.Frame(self, height=495, background="white")

        self.finished_left_frame = tk.Frame(
            self.finished_frame, background=self.finished_left_background
        )
        self.finished_image = resize_image(self.orig_image, 80, 80)
        self.finished_tk_image = ImageTk.PhotoImage(self.finished_image)

        finished_image_label = tk.Label(
            self.finished_left_frame,
            image=self.finished_tk_image,
            background=self.finished_left_background,
        )
        finished_image_label.pack(side="top", anchor="center", pady=20)
        finished_text_label = tk.Label(
            self.finished_left_frame,
            text=config.INSTALLER_CONFIG["title"],
            background=self.finished_left_background,
            foreground="white",
            font=self.BIG_BOLD_FONT,
        )

        finished_text_label.pack(side="top", anchor="center")

        self.finished_right_frame = tk.Frame(self.finished_frame, background="white")
        complete_label = tk.Label(
            self.finished_right_frame,
            text=f"Welcome to {config.INSTALLER_CONFIG['title']} Uninstall",
            font=self.MED_BOLD_FONT,
            background="white",
        )
        complete_label.pack(side="top", anchor="nw", pady=10, padx=6)
        description_label = tk.Label(
            self.finished_right_frame,
            text=(
                f"Setup will guide you through the uninstallation of {config.INSTALLER_CONFIG['title']}."
                f"\n\nBefore starting the uninstallation, make sure {config.INSTALLER_CONFIG['title']} is not running."
                "\n\nClick Next to continue."
            ),
            font=self.MIN_FONT,
            justify="left",
            background="white",
            wraplength=340,
        )
        description_label.pack(side="top", anchor="nw", pady=10, padx=4)

        style = ttk.Style()
        style.configure("White.TCheckbutton", background="white")

        self.finished_left_frame.pack(
            side="left", anchor="nw", fill="both", expand=True
        )
        self.finished_right_frame.pack(
            side="right", anchor="nw", fill="both", expand=True
        )

        self.buttons_frame = tk.Frame(self, relief="sunken", borderwidth=1)

        self.next_button = ttk.Button(
            self.buttons_frame,
            text="Next >",
            command=self.next_pressed,
        )

        self.finished_button = ttk.Button(
            self.buttons_frame, text="Finish", command=self.finished_button_pressed
        )

        self.finished_frame.pack(side="top", anchor="nw", fill="both", expand=True)

        self.cancel_button = ttk.Button(
            self.buttons_frame, text="Cancel", command=self.cancel_pressed
        )
        self.cancel_button.pack(side="right", anchor="nw", padx=8)
        self.next_button.pack(side="right")

        self.buttons_frame.pack(side="right", fill="x", expand=True)

        self.__built = True
        return self

    def run(self):
        if not self.__built:
            self.build()
            time.sleep(0.1)

        self.mainloop()

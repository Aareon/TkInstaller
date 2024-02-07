import os
import platform
import subprocess
import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import font, ttk

from loguru import logger
from PIL import Image, ImageTk

from tkinstaller.ui.extractor import DecompressFrame
from tkinstaller.utils import (
    ROOT_DIR,
    UAC_ICON_PATH,
    get_windows_username,
    is_admin,
    resize_image,
    run_as_admin,
)
from tkinstaller import config


class InstallerApp(tk.Tk):
    __built: bool

    def __init__(self):
        super().__init__()

        logger.debug(f"IsAdmin: {is_admin()}")

        UAC_ICON = ImageTk.PhotoImage(
            resize_image(Image.open(UAC_ICON_PATH), 12, 12)
        )

        self.BOLD_FONT = font.Font(weight="bold", size=8)
        self.MED_BOLD_FONT = font.Font(weight="bold", size=12)
        self.BIG_BOLD_FONT = font.Font(weight="bold", size=16)
        self.MIN_FONT = font.Font(size=8)

        # load image
        image_fp = Path(config.INSTALLER_CONFIG["logo_path"].replace("@HERE@", str(ROOT_DIR)))
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

    def finished_button_pressed(self):
        if self.run_after_install.get():
            installation_kind = self.selected_option.get()
            if platform.system() == "Windows":
                creation_flags = subprocess.CREATE_NEW_CONSOLE
            else:
                creation_flags = subprocess.START_NEW_SESSION
            subprocess.Popen(
                Path(
                    f"{self.global_install_path if installation_kind else config.USER_INSTALL_PATH}"
                )
                / config.APP_EXE_NAME,
                creationflags=creation_flags,
            )
        sys.exit(0)

    def install_complete(self):
        self.geometry("495x360")
        self.top_frame.pack_forget()
        self.sep_frame.pack_forget()
        self.decompress_frame.pack_forget()
        self.program_sep_frame.pack_forget()
        self.next_button.pack_forget()
        self.buttons_frame.pack_forget()

        self.finished_frame = tk.Frame(self, height=495, background="white")

        finished_left_background = config.INSTALLER_CONFIG.get("finished_logo_background", "blue")
        if "," in finished_left_background:
            # Convert the RGB components to integers
            red, green, blue = map(int, finished_left_background.split(", "))
            finished_left_background = f"#{red:02x}{green:02x}{blue:02x}"

        self.finished_left_frame = tk.Frame(
            self.finished_frame, background=finished_left_background
        )
        self.finished_image = resize_image(self.orig_image, 80, 80)
        self.finished_tk_image = ImageTk.PhotoImage(self.finished_image)

        finished_image_label = tk.Label(
            self.finished_left_frame,
            image=self.finished_tk_image,
            background=finished_left_background,
        )
        finished_image_label.pack(side="top", anchor="center", pady=20)
        finished_text_label = tk.Label(
            self.finished_left_frame,
            text=config.INSTALLER_CONFIG["title"],
            background=finished_left_background,
            foreground="white",
            font=self.BIG_BOLD_FONT,
        )

        finished_text_label.pack(side="top", anchor="center")

        self.finished_right_frame = tk.Frame(self.finished_frame, background="white")
        complete_label = tk.Label(
            self.finished_right_frame,
            text=f"Completing {config.INSTALLER_CONFIG['title']} Setup",
            font=self.MED_BOLD_FONT,
            background="white",
        )
        complete_label.pack(side="top", anchor="nw", pady=10, padx=6)
        description_label = tk.Label(
            self.finished_right_frame,
            text=f"{config.INSTALLER_CONFIG['title']} has been installed on your computer.\nClick Finish to close Setup.",
            font=self.MIN_FONT,
            justify="left",
            background="white",
        )
        description_label.pack(side="top", anchor="nw", pady=10, padx=4)

        style = ttk.Style()
        style.configure("White.TCheckbutton", background="white")
        run_checkbox = ttk.Checkbutton(
            self.finished_right_frame,
            text=f"Run {config.INSTALLER_CONFIG['title']}",
            onvalue=1,
            offvalue=0,
            variable=self.run_after_install,
            style="White.TCheckbutton",
        )
        run_checkbox.pack(side="top", anchor="nw", padx=4, pady=30)

        self.finished_left_frame.pack(
            side="left", anchor="nw", fill="both", expand=True
        )
        self.finished_right_frame.pack(
            side="right", anchor="nw", fill="both", expand=True
        )

        self.finished_button = ttk.Button(
            self.buttons_frame,
            text="Finish",
            command=self.finished_button_pressed
        )
        self.finished_button.pack(side="right")
        self.back_button.pack_forget()
        self.back_button.pack(side="right")

        self.finished_frame.pack(side="top", anchor="nw", fill="both", expand=True)

        self.buttons_frame.configure(relief="sunken", borderwidth=1)
        self.buttons_frame.pack(side="right", fill="x", expand=True)

    def cancel_pressed(self):
        sys.exit(0)

    def back_pressed(self):
        self.decompress_frame.pack_forget()
        self.program_sep_frame.pack_forget()
        self.next_button.pack_forget()
        self.back_button.pack_forget()
        self.buttons_frame.pack_forget()

        self.middle_frame.pack(side="top", anchor="nw", fill="both", expand=True)
        self.bottom_label.pack(side="top", anchor="nw", padx=20)
        self.program_sep_frame.pack(
            side="top", anchor="nw", padx=4, fill="x", expand=True, pady=16
        )
        self.install_button.pack(side="right", anchor="nw")
        self.buttons_frame.pack(side="right", anchor="nw", pady=6)

    def install_pressed(self):
        if self.selected_option.get():
            run_as_admin()
            install_path = self.global_install_path
        else:
            install_path = config.USER_INSTALL_PATH

        install_path = Path(install_path)
        archive_path = Path(
            config.INSTALLER_CONFIG["compressed_app_path"].replace("@HERE@", str(ROOT_DIR))
        )

        self.middle_frame.pack_forget()
        self.bottom_label.pack_forget()
        self.program_sep_frame.pack_forget()
        self.buttons_frame.pack_forget()

        self.install_button.pack_forget()

        self.label_1.configure(text="Installing")
        self.label_2.configure(
            text=f"Please wait while {config.INSTALLER_CONFIG['title']} is being installed."
        )

        self.decompress_frame = DecompressFrame(self)
        self.decompress_frame.pack(
            side="top",
            anchor="nw",
            padx=20,
            pady=20,
            ipady=41,
            ipadx=86,
            fill="x",
            expand=True,
        )

        self.program_sep_frame.pack(
            side="top", anchor="nw", padx=4, fill="x", expand=True, pady=16
        )

        self.next_button = ttk.Button(
            self.buttons_frame, text="Next >", state="disabled"
        )
        self.next_button.pack(side="right", anchor="nw")

        self.back_button = ttk.Button(
            self.buttons_frame,
            text="< Back",
            command=self.back_pressed,
            state="disabled",
        )
        self.back_button.pack(side="right", anchor="nw")

        self.cancel_button.configure(state="disabled")

        self.buttons_frame.pack(side="right", anchor="nw", pady=6)

        self.decompress_frame.start_decompression(
            archive_path, install_path, self.install_complete
        )

    def remove_install_button_image(self):
        self.install_button.destroy()
        self.install_button = ttk.Button(
            self.buttons_frame, text="Install", width=11, command=self.install_pressed
        )
        self.install_button.pack(side="right", anchor="nw")

    def set_bottom_label(self):
        if self.selected_option.get():
            self.selected_option_text.set(
                "Fresh install for all users. (will prompt for admin credentials)"
            )
            self.install_button.configure(
                image=self.UAC_ICON,
                text="Install",
                compound=tk.LEFT,
                width=9,
                command=self.install_pressed,
            )
        else:
            self.remove_install_button_image()
            if self.user_install_exists:
                self.selected_option_text.set(
                    f"There is already a per-user installation. ({config.USER_INSTALL_PATH}) Will reinstall/upgrade."
                )
            else:
                self.selected_option_text.set(self.selected_option_text_default)

    def build(self):
        # Disable resizing in both directions
        self.resizable(width=False, height=False)

        title = config.INSTALLER_CONFIG["title"]
        if config.INSTALLER_CONFIG.getboolean("show_version_in_title"):
            title = f"{title} {config.INSTALLER_CONFIG['version']}"
        self.title(f"{title} Setup")

        self.top_frame = tk.Frame(self, background="white")
        self.label_frame = tk.Frame(self.top_frame, width=200, background="white")

        self.label_1 = tk.Label(
            self.label_frame,
            text="Choose Installation Options",
            font=self.BOLD_FONT,
            background="white",
        )
        self.label_1.pack(side="top", anchor="nw", padx=6)

        self.label_2 = tk.Label(
            self.label_frame,
            text="Who should this application be installed for?",
            background="white",
        )
        self.label_2.pack(side="top", anchor="nw", padx=10)

        self.tk.call("wm", "iconphoto", self._w, self.tk_image)

        image_label = tk.Label(self.top_frame, image=self.tk_image, background="white")
        image_label.pack(side="right", anchor="ne", pady=8, padx=10)

        self.label_frame.pack(side="left", fill="x", expand=True, ipadx=50)
        self.top_frame.pack(side="top", anchor="nw", fill="x", expand=True)

        # Create a separate frame for the separator and image
        self.sep_frame = tk.Frame(self)

        sep = ttk.Separator(self.sep_frame, orient=tk.HORIZONTAL)
        sep.pack(side="top", fill="x")

        self.sep_frame.pack(side="top", anchor="nw", fill="x", expand=True)

        self.middle_frame = tk.Frame(self)
        please_label = tk.Label(
            self.middle_frame,
            text="Please select whether you wish to make this software available to all users or just yourself",
        )
        please_label.pack(side="top", anchor="nw", padx=20)

        combo_frame = tk.Frame(self.middle_frame)

        selection_combo_opt_1 = ttk.Radiobutton(
            combo_frame,
            text="Anyone who uses this computer (all users)",
            variable=self.selected_option,
            value=1,
            command=self.set_bottom_label,
        )
        selection_combo_opt_2 = ttk.Radiobutton(
            combo_frame,
            text=f"Only for me ({get_windows_username()})",
            variable=self.selected_option,
            value=0,
            command=self.set_bottom_label,
        )

        selection_combo_opt_1.pack(side="top", anchor="nw", padx=40)
        selection_combo_opt_2.pack(side="top", anchor="nw", padx=40)

        combo_frame.pack(side="top", anchor="nw", fill="both", expand=True, pady=30)
        self.middle_frame.pack(side="top", anchor="nw", fill="both", expand=True)

        self.bottom_label = tk.Label(
            self, textvariable=self.selected_option_text, wraplength=360, justify="left"
        )
        self.bottom_label.pack(side="top", anchor="w", padx=20)

        # program name/version + separator
        self.program_sep_frame = tk.Frame(self)

        program_label = tk.Label(
            self.program_sep_frame,
            text=f"{config.INSTALLER_CONFIG['title']} {config.INSTALLER_CONFIG['version']}",
            foreground="gray",
            font=self.MIN_FONT,
        )
        program_label.pack(side="left", anchor="nw")

        program_sep = ttk.Separator(self.program_sep_frame, orient=tk.HORIZONTAL)
        program_sep.pack(side="right", anchor="nw", fill="x", expand=True, pady=10)

        self.program_sep_frame.pack(
            side="top", anchor="nw", padx=4, fill="x", expand=True, pady=16
        )

        self.buttons_frame = tk.Frame(self)
        self.cancel_button = ttk.Button(
            self.buttons_frame, text="Cancel", command=self.cancel_pressed
        )
        self.cancel_button.pack(side="right", anchor="nw", padx=8)
        self.install_button = ttk.Button(
            self.buttons_frame, text="Install", width=11, command=self.install_pressed
        )
        self.install_button.pack(side="right", anchor="nw")
        self.buttons_frame.pack(side="top", anchor="nw", fill="x", expand=True, pady=6)

        self.__built = True
        return self

    def run(self):
        if not self.__built:
            self.build()
            time.sleep(0.1)

        self.mainloop()

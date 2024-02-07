import threading
import tkinter as tk
import zipfile
from pathlib import Path
from tkinter import ttk

import py7zr
from loguru import logger


class DecompressFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self, variable=self.progress_var, length=300, mode="determinate"
        )
        self.progress_bar.pack(side="top", anchor="nw", fill="x", expand=True)

        # Variable to store the completion status
        self.decompression_complete = tk.BooleanVar(value=False)

    def start_decompression(
        self, archive_path: Path, output_directory: Path, callback=None
    ):
        # Run decompression in a separate thread to avoid freezing the GUI
        threading.Thread(
            target=self.decompress,
            args=(archive_path, output_directory, callback),
            daemon=True,
        ).start()

    def decompress(self, archive_path, output_directory, callback=None):
        try:
            if archive_path.suffix == ".7z":
                self.decompress_7z(archive_path, output_directory)
            elif archive_path.suffix == ".zip":
                self.decompress_zip(archive_path, output_directory)
            else:
                logger.error(f"Unsupported archive format: {archive_path}")

            # Set the completion status to True
            self.decompression_complete.set(True)

            logger.debug(f"Extracted {archive_path} to {output_directory}")

            # Call the callback function if provided
            if callback:
                callback()
        except Exception as e:
            logger.exception(
                "Error during decompression:", e, archive_path, output_directory
            )
            raise

    def decompress_7z(self, archive_path, output_directory):
        with py7zr.SevenZipFile(archive_path, mode="r") as archive:
            total_files = sum(1 for _ in archive.list())
            self.progress_var.set(0)
            for index, file_info in enumerate(archive.list(), start=1):
                file_name = file_info.filename
                self.update_progress(index, total_files)
                archive.extract(file_name, path=output_directory)

    def decompress_zip(self, archive_path, output_directory):
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            total_files = len(zip_ref.infolist())
            self.progress_var.set(0)
            for index, file_info in enumerate(zip_ref.infolist(), start=1):
                file_name = file_info.filename
                self.update_progress(index, total_files)
                zip_ref.extract(file_name, path=output_directory)

    def update_progress(self, current_value, total_value):
        progress_percentage = (current_value / total_value) * 100
        self.progress_var.set(progress_percentage)
        self.master.update_idletasks()
        progress_percentage = (current_value / total_value) * 100
        self.progress_var.set(progress_percentage)
        self.master.update_idletasks()

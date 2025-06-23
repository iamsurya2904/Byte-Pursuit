import gi
import os
import platform
import re
import threading
import subprocess
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from gi.repository import Gtk, Gdk, GLib

def list_disks():
    try:
        result = subprocess.run(["lsblk", "-o", "NAME,SIZE,TYPE,MOUNTPOINT"], capture_output=True, text=True, check=True)
        disks = []
        for line in result.stdout.splitlines()[1:]:
            parts = line.split()
            if "disk" in parts or "part" in parts:
                disks.append(" ".join(parts))
        return disks
    except Exception as e:
        return [f"Error retrieving disks: {e}"]

def check_sudo_permissions():
    try:
        result = subprocess.run(["sudo", "-v"], capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        return False

def decrypt_log_data(encrypted_data, key, iv):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_data) + decryptor.finalize()

def extract_logs(drive_path, output_folder, log_callback):
    os.makedirs(output_folder, exist_ok=True)
    buffer_size = 4096
    LOG_PATTERN = re.compile(rb'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')

    log_count = 0
    leftover_data = b""

    decryption_key = b"1234567890abcdef"  # Example key (16 bytes for AES-128)
    iv = b"abcdef1234567890"  # Example IV (16 bytes for AES-128)

    try:
        with open(drive_path, "rb") as drive:
            while chunk := drive.read(buffer_size):
                chunk = leftover_data + chunk
                leftover_data = b""
                matches = list(LOG_PATTERN.finditer(chunk))
                for i, match in enumerate(matches):
                    start = match.start()
                    if i < len(matches) - 1:
                        end = matches[i + 1].start()
                        log_data = chunk[start:end]
                    else:
                        log_data = chunk[start:]
                        leftover_data = log_data
                        continue

                    decrypted_log = decrypt_log_data(log_data, decryption_key, iv)

                    log_file_path = os.path.join(output_folder, f"log_{log_count}.txt")
                    with open(log_file_path, "wb") as log_file:
                        log_file.write(log_data)

                    log_callback(f"Extracted encrypted log file: {log_file_path}")
                    log_callback(f"Decrypted log data: {decrypted_log.decode('utf-8', errors='ignore')}")
                    log_count += 1

        log_callback(f"Extraction completed. Total log files extracted: {log_count}")
    except FileNotFoundError:
        log_callback(f"Error: File {drive_path} not found.")
    except PermissionError:
        log_callback(f"Error: Permission denied for {drive_path}.")
    except Exception as e:
        log_callback(f"Unexpected error while processing {drive_path}: {e}")

class FileRecoveryApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Enhanced File Recovery Tool")
        self.set_border_width(10)
        self.set_default_size(600, 400)

        self.drive_path = None
        self.output_folder = None

        self.load_css()

        os_info = f"Detected OS: {platform.system()} {platform.release()}"
        self.label = Gtk.Label(label=os_info)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.pack_start(self.label, False, False, 0)

        self.input_button = Gtk.Button(label="Select Drive/File")
        self.input_button.set_image(Gtk.Image.new_from_icon_name("drive-harddisk", Gtk.IconSize.LARGE_TOOLBAR))
        self.input_button.set_tooltip_text("Select a disk or file to scan")
        self.input_button.connect("clicked", self.on_input_clicked)

        self.output_button = Gtk.Button(label="Select Output Folder")
        self.output_button.set_image(Gtk.Image.new_from_icon_name("folder", Gtk.IconSize.LARGE_TOOLBAR))
        self.output_button.set_tooltip_text("Select the folder to save recovered files")
        self.output_button.connect("clicked", self.on_output_clicked)

        self.recover_button = Gtk.Button(label="Recover Files")
        self.recover_button.set_image(Gtk.Image.new_from_icon_name("document-open", Gtk.IconSize.LARGE_TOOLBAR))
        self.recover_button.set_tooltip_text("Start recovering files")
        self.recover_button.connect("clicked", self.on_recover_clicked)

        self.reset_button = Gtk.Button(label="Reset")
        self.reset_button.set_image(Gtk.Image.new_from_icon_name("edit-clear", Gtk.IconSize.LARGE_TOOLBAR))
        self.reset_button.set_tooltip_text("Reset all selections")
        self.reset_button.connect("clicked", self.on_reset_clicked)

        self.file_type_combo = Gtk.ComboBoxText()
        self.file_type_combo.append_text("Select File Type")
        self.file_type_combo.append_text("JPG")
        self.file_type_combo.append_text("PNG")
        self.file_type_combo.append_text("PDF")
        self.file_type_combo.append_text("LOG FILES")
        self.file_type_combo.set_tooltip_text("Choose the file type to recover")
        self.file_type_combo.set_active(0)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)

        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_buffer = self.log_view.get_buffer()

        vbox.pack_start(self.input_button, False, False, 0)
        vbox.pack_start(self.output_button, False, False, 0)
        vbox.pack_start(self.file_type_combo, False, False, 0)
        vbox.pack_start(self.recover_button, False, False, 0)
        vbox.pack_start(self.reset_button, False, False, 0)
        vbox.pack_start(self.progress_bar, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.log_view)
        scroll.set_vexpand(True)
        vbox.pack_start(scroll, True, True, 0)

        self.add(vbox)

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            button {
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
                background-color: #4CAF50;
                color: white;
            }
            button:hover {
                background-color: #45a049;
            }
            label {
                font-size: 18px;
                color: white;
                font-weight: bold;
            }
            window {
                background-color: #333;
            }
        """)
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def on_input_clicked(self, widget):
        if not check_sudo_permissions():
            self.show_error("Sudo permissions are required to access disk devices.")
            return

        choice_dialog = Gtk.Dialog(title="Select Input Method", parent=self, flags=0)
        choice_dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        choice_dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        dialog_box = choice_dialog.get_content_area()

        label = Gtk.Label(label="Choose input method for recovery:")
        dialog_box.pack_start(label, False, False, 10)

        self.input_method_combo = Gtk.ComboBoxText()
        self.input_method_combo.append_text("Manual Input Path")
        self.input_method_combo.append_text("Select from lsblk (Disk/Partition)")
        self.input_method_combo.set_active(0)
        dialog_box.pack_start(self.input_method_combo, False, False, 10)

        choice_dialog.show_all()
        response = choice_dialog.run()

        if response == Gtk.ResponseType.OK:
            selected_method = self.input_method_combo.get_active_text()
            if selected_method == "Manual Input Path":
                manual_dialog = Gtk.FileChooserDialog("Select Drive/File", self, Gtk.FileChooserAction.OPEN,
                                                      ("Cancel", Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK))
                manual_response = manual_dialog.run()
                if manual_response == Gtk.ResponseType.OK:
                    self.drive_path = manual_dialog.get_filename()
                    self.log_message(f"Manual path selected: {self.drive_path}")
                manual_dialog.destroy()
            elif selected_method == "Select from lsblk (Disk/Partition)":
                disks = list_disks()
                disk_dialog = Gtk.Dialog(title="Select Disk", parent=self, flags=0)
                disk_dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
                disk_dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
                disk_dialog_box = disk_dialog.get_content_area()
                disk_combo = Gtk.ComboBoxText()

                for disk in disks:
                    disk_combo.append_text(disk)

                disk_combo.set_active(0)
                disk_dialog_box.add(disk_combo)
                disk_dialog.show_all()

                disk_response = disk_dialog.run()
                if disk_response == Gtk.ResponseType.OK:
                    selected_disk = disk_combo.get_active_text()
                    if selected_disk:
                        self.drive_path = f"/dev/{selected_disk.split()[0]}"
                        self.log_message(f"Drive selected: {self.drive_path}")
                disk_dialog.destroy()

        choice_dialog.destroy()

    def on_output_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Select Output Folder", self,
                                       Gtk.FileChooserAction.SELECT_FOLDER,
                                       ("Cancel", Gtk.ResponseType.CANCEL,
                                        "Select", Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.output_folder = dialog.get_filename()
            self.log_message(f"Output folder selected: {self.output_folder}")
        dialog.destroy()

    def on_recover_clicked(self, widget):
        choice = self.file_type_combo.get_active_text()
        if not self.drive_path or not self.output_folder:
            self.show_error("Please select both a drive and an output folder.")
            return
        if choice == "Select File Type" or not choice:
            self.show_error("Please select a valid file type.")
            return

        self.progress_bar.set_fraction(0)
        threading.Thread(target=self.start_recovery, args=(choice,)).start()

    def on_reset_clicked(self, widget):
        self.drive_path = None
        self.output_folder = None
        self.file_type_combo.set_active(0)
        self.progress_bar.set_fraction(0)
        self.log_buffer.set_text("")
        self.log_message("Selections reset.")

    def start_recovery(self, file_type):
        def update_progress(amount):
            GLib.idle_add(self.progress_bar.set_fraction, min(amount / 1000000000, 1))

        def log_callback(message):
            GLib.idle_add(self.log_message, message)

        if file_type == "JPG":
            recover_file(self.drive_path, b'\xff\xd8\xff\xe0', b'\xff\xd9', 'jpg', self.output_folder, update_progress, log_callback)
        elif file_type == "PNG":
            recover_file(self.drive_path, b'\x89PNG\r\n\x1a\n', b'IEND\xaeB`\x82', 'png', self.output_folder, update_progress, log_callback)
        elif file_type == "PDF":
            recover_file(self.drive_path, b'%PDF', b'%%EOF', 'pdf', self.output_folder, update_progress, log_callback)
        elif file_type == "LOG FILES":
            extract_logs(self.drive_path, self.output_folder, log_callback)

        GLib.idle_add(self.progress_bar.set_fraction, 1)

    def log_message(self, message):
        end_iter = self.log_buffer.get_end_iter()
        self.log_buffer.insert(end_iter, message + "\n")

    def show_error(self, message):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, "Error")
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

def main():
    app = FileRecoveryApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()

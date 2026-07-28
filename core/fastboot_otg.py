import sys
import os
import time
import subprocess
import shutil

from core.py_fastboot import PyFastboot

class FastbootOTG:
    """Fastboot USB-OTG Controller for Termux with PyUSB Engine"""
    
    def __init__(self):
        self.py_fb = PyFastboot()
        self.fastboot_bin = shutil.which("fastboot") or "/data/data/com.termux/files/usr/bin/fastboot"
        self.connected_serial = None
        self.is_pyusb_active = False

    def scan_devices(self):
        """Scans devices connected via USB OTG in Fastboot mode"""
        ok, serial = self.py_fb.connect()
        if ok:
            self.connected_serial = serial
            self.is_pyusb_active = True
            
            product = self.py_fb.getvar("product")
            anti = self.py_fb.getvar("anti")
            unlocked = self.py_fb.getvar("unlocked")
            battery = self.py_fb.getvar("battery-voltage")

            name_map = {
                "ginkgo": "Redmi Note 8",
                "sweet": "Redmi Note 10 Pro",
                "surya": "POCO X3 NFC",
                "renoir": "Mi 11 Lite 5G",
                "mondrian": "POCO F5 Pro",
                "marble": "POCO F5",
                "chopin": "POCO X3 GT",
                "ruby": "Redmi Note 12 Pro 5G",
                "toco": "Mi Note 10 Lite",
                "peridot": "POCO F6"
            }
            dev_name = name_map.get(product.lower(), f"Xiaomi ({product})")

            return {
                "serial": serial,
                "mode": "Fastboot OTG (PyUSB Engine)",
                "product": product,
                "name": dev_name,
                "chipset": "Qualcomm / MediaTek",
                "anti": int(anti) if anti.isdigit() else 1,
                "unlocked": unlocked,
                "battery": f"{battery} mV",
                "is_simulated": False
            }, f"OTG Device detected: {serial} ({dev_name})"

        return {
            "serial": "XM_OTG_984A09",
            "mode": "Fastboot OTG",
            "product": "ginkgo",
            "name": "Redmi Note 8",
            "chipset": "Qualcomm Snapdragon 665",
            "anti": 1,
            "unlocked": "yes",
            "battery": "4222 mV",
            "is_simulated": True
        }, "Hardware OTG not detected. Simulation mode active."

    def getvar(self, serial, var_name):
        if self.is_pyusb_active:
            return self.py_fb.getvar(var_name)
        return "N/A"

    def flash_partition(self, serial, partition, img_path, is_simulated=False, callback=None):
        """Flashes a partition via PyUSB Fastboot OTG"""
        if callback:
            callback(f"Flashing '{partition}' ({os.path.basename(img_path)})...", "process")

        if is_simulated:
            time.sleep(1.0)
            if callback:
                callback(f"Flashing '{partition}' OKAY", "success")
            return True, "OKAY"

        if self.is_pyusb_active:
            try:
                if not os.path.exists(img_path):
                    if callback:
                        callback(f"Image file '{img_path}' not found.", "error")
                    return False, "File missing"

                filesize = os.path.getsize(img_path)
                hex_size = f"{filesize:08x}"

                # 1. Download command
                ok, resp = self.py_fb.send_cmd(f"download:{hex_size}")
                if not ok:
                    if callback:
                        callback(f"Download init failed '{partition}': {resp}", "error")
                    return False, resp

                # 2. Transfer binary image data
                with open(img_path, "rb") as f:
                    chunk_size = 65536
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        self.py_fb.ep_out.write(chunk)

                # Read response
                resp_data = self.py_fb.ep_in.read(512, timeout=10000)
                resp_str = bytes(resp_data).decode('ascii', errors='ignore')

                if not resp_str.startswith("OKAY"):
                    if callback:
                        callback(f"Data download '{partition}' failed: {resp_str}", "error")
                    return False, resp_str

                # 3. Flash command
                ok_flash, resp_flash = self.py_fb.send_cmd(f"flash:{partition}")
                if ok_flash:
                    if callback:
                        callback(f"Flashing '{partition}' OKAY", "success")
                    return True, resp_flash
                else:
                    if callback:
                        callback(f"Flash '{partition}' failed: {resp_flash}", "error")
                    return False, resp_flash

            except Exception as e:
                if callback:
                    callback(f"Error PyUSB Flashing '{partition}': {str(e)}", "error")
                return False, str(e)

        return False, "OTG driver not active"

    def reboot(self, serial, target="system", is_simulated=False):
        if is_simulated:
            return True, f"Simulated reboot to {target}"
            
        if self.is_pyusb_active:
            ok, msg = self.py_fb.reboot(target)
            return ok, msg or "Reboot OKAY"

        return False, "Not connected"

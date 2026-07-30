import sys
import os
import time
import subprocess
import shutil

from core.py_fastboot import PyFastboot
from core.sparse_splitter import SparseSplitter
from core.adb_controller import ADBController

class FastbootOTG:
    """Fastboot & ADB USB-OTG Controller with Dual-Engine (C++ Fastboot/ADB + PyUSB Fallback)"""
    
    def __init__(self):
        self.py_fb = PyFastboot()
        self.adb_ctrl = ADBController()
        self.fastboot_bin = shutil.which("fastboot") or "/data/data/com.termux/files/usr/bin/fastboot"
        self.connected_serial = None
        self.is_pyusb_active = False
        self.connection_mode = "fastboot" # 'fastboot' or 'adb'

    def scan_devices(self):
        """Scans devices connected via USB OTG in Fastboot or ADB mode"""
        self.py_fb.dispose()
        self.connection_mode = "fastboot"

        # 1. Check Fastboot mode via C++ binary under su
        if os.path.exists(self.fastboot_bin):
            try:
                env = dict(os.environ)
                env["PATH"] = f"/data/data/com.termux/files/usr/bin:{env.get('PATH', '')}"
                env["LD_LIBRARY_PATH"] = "/data/data/com.termux/files/usr/lib"
                
                res = subprocess.check_output([self.fastboot_bin, "devices"], text=True, env=env, stderr=subprocess.STDOUT).strip()
                if res:
                    lines = res.splitlines()
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 2 and parts[1] == "fastboot":
                            self.connected_serial = parts[0]
                            break
            except:
                pass

        # 2. Check Fastboot mode via PyUSB
        ok, serial = self.py_fb.connect()
        if ok or self.connected_serial:
            serial = self.connected_serial or serial
            self.connected_serial = serial
            self.is_pyusb_active = True
            self.connection_mode = "fastboot"
            
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
                "mode": "Fastboot OTG Engine",
                "conn_type": "fastboot",
                "product": product if product != "N/A" else "ginkgo",
                "name": dev_name,
                "chipset": "Qualcomm / MediaTek",
                "anti": int(anti) if anti.isdigit() else 1,
                "unlocked": unlocked if unlocked != "N/A" else "yes",
                "battery": f"{battery} mV" if battery != "N/A" else "4380 mV",
                "is_simulated": False
            }, f"OTG Device detected (Fastboot): {serial} ({dev_name})"

        # 3. Check ADB mode via ADBController
        adb_dev, adb_msg = self.adb_ctrl.scan_adb_devices()
        if adb_dev:
            self.connected_serial = adb_dev["serial"]
            self.connection_mode = "adb"

            props = self.adb_ctrl.get_device_props(adb_dev["serial"])
            dev_name = props.get("marketname") or props.get("model") or props.get("device") or "Xiaomi Device"
            product_code = props.get("device") or "xiaomi"
            locked_val = props.get("locked", "0")
            unlocked_str = "no" if locked_val == "1" else "yes"

            return {
                "serial": adb_dev["serial"],
                "mode": f"ADB OTG Engine ({adb_dev['state'].upper()})",
                "conn_type": "adb",
                "adb_state": adb_dev["state"],
                "product": product_code,
                "name": dev_name,
                "chipset": "Qualcomm / MediaTek",
                "anti": 1,
                "unlocked": unlocked_str,
                "battery": "4000 mV",
                "android_ver": props.get("android_ver", "Android"),
                "miui_ver": props.get("miui_ver", "MIUI"),
                "is_simulated": False
            }, f"OTG Device detected (ADB): {adb_dev['serial']} ({dev_name})"

        # 4. Simulation mode
        return {
            "serial": "XM_OTG_984A09",
            "mode": "Fastboot OTG",
            "conn_type": "fastboot",
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

    def erase_partition(self, serial, partition, is_simulated=False):
        """Erases a partition via Fastboot OTG"""
        if is_simulated:
            return True, "OKAY"

        self.py_fb.dispose()

        if os.path.exists(self.fastboot_bin):
            try:
                cmd = [self.fastboot_bin, "-s", serial, "erase", partition]
                env = dict(os.environ)
                env["PATH"] = f"/data/data/com.termux/files/usr/bin:{env.get('PATH', '')}"
                env["LD_LIBRARY_PATH"] = "/data/data/com.termux/files/usr/lib"
                
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
                stdout, stderr = proc.communicate()
                out_combined = (stdout + "\n" + stderr).strip()
                if proc.returncode == 0 or "OKAY" in out_combined:
                    return True, "OKAY"
            except Exception:
                pass

        return self.py_fb.send_command(f"erase:{partition}")

    def flash_partition(self, serial, partition, img_path, is_simulated=False, callback=None):
        """Flashes a partition via OTG with high-speed C++ Fastboot Engine and PyUSB Fallback"""
        if not os.path.exists(img_path):
            if callback:
                callback(f"Image file '{img_path}' not found.", "error")
            return False, "File missing"

        if is_simulated:
            time.sleep(0.3)
            if callback:
                callback(f"Flashing '{partition}' OKAY", "success")
            return True, "OKAY"

        self.py_fb.dispose()

        # Priority 1: High-Speed Android C++ Fastboot Binary under su
        if os.path.exists(self.fastboot_bin):
            try:
                cmd = [self.fastboot_bin, "-s", serial, "flash", partition, img_path]
                env = dict(os.environ)
                env["PATH"] = f"/data/data/com.termux/files/usr/bin:{env.get('PATH', '')}"
                env["LD_LIBRARY_PATH"] = "/data/data/com.termux/files/usr/lib"
                
                if callback:
                    callback(f"Flashing '{partition}' via C++ Fastboot Engine...", "process")

                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
                stdout, stderr = proc.communicate()
                out_combined = (stdout + "\n" + stderr).strip()

                if proc.returncode == 0 or "OKAY" in out_combined:
                    if callback:
                        callback(f"Flashing '{partition}' OKAY", "success")
                    return True, "OKAY"
            except Exception as e:
                pass

        # Priority 2: PyUSB Fastboot Driver Fallback
        ok, _ = self.py_fb.connect()
        if ok:
            try:
                max_dl_str = self.py_fb.getvar("max-download-size")
                max_dl = 300 * 1024 * 1024
                if max_dl_str and max_dl_str != "N/A":
                    try:
                        val = int(max_dl_str, 16) if max_dl_str.startswith("0x") else int(max_dl_str)
                        if val > 10 * 1024 * 1024:
                            max_dl = min(val - 1048576, 300 * 1024 * 1024)
                    except:
                        pass

                file_size = os.path.getsize(img_path)

                sub_files = [img_path]
                if file_size > max_dl:
                    sub_files = SparseSplitter.split_sparse_file(img_path, max_size=max_dl)

                total_subs = len(sub_files)

                for s_idx, s_file in enumerate(sub_files, start=1):
                    def progress_cb(sent, total):
                        pct = int((sent / total) * 100) if total > 0 else 0
                        if total_subs > 1:
                            if callback:
                                callback(f"[{s_idx}/{total_subs}] {pct}% '{partition}' payload...", "process")
                        else:
                            if callback:
                                callback(f"[{pct}%] Sending '{partition}' payload...", "process")

                    ok_data, resp_data = self.py_fb.send_data(s_file, callback=progress_cb)
                    
                    if s_file != img_path and os.path.exists(s_file):
                        os.remove(s_file)

                    if not ok_data:
                        if callback:
                            callback(f"Download stream '{partition}' failed: {resp_data}", "error")
                        return False, resp_data

                    ok_flash, resp_flash = self.py_fb.send_command(f"flash:{partition}", timeout=300000)
                    if not ok_flash:
                        if callback:
                            callback(f"Flash '{partition}' failed: {resp_flash}", "error")
                        return False, resp_flash

                if callback:
                    callback(f"Flashing '{partition}' OKAY", "success")
                return True, "OKAY"

            except Exception as e:
                if callback:
                    callback(f"Error PyUSB Flashing '{partition}': {str(e)}", "error")
                return False, str(e)

        return False, "OTG driver not active"

    def reboot(self, serial, target="system", is_simulated=False):
        if is_simulated:
            return True, f"Simulated reboot to {target}"
            
        self.py_fb.dispose()

        # If in ADB mode, reboot via ADB
        if self.connection_mode == "adb":
            return self.adb_ctrl.reboot(serial, target)

        # Fastboot reboot
        if os.path.exists(self.fastboot_bin):
            try:
                target_cmd = "reboot-bootloader" if target == "bootloader" else ("reboot-recovery" if target == "recovery" else "reboot")
                cmd = [self.fastboot_bin, "-s", serial, target_cmd]
                env = dict(os.environ)
                env["PATH"] = f"/data/data/com.termux/files/usr/bin:{env.get('PATH', '')}"
                env["LD_LIBRARY_PATH"] = "/data/data/com.termux/files/usr/lib"
                subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
                return True, "Reboot OKAY"
            except:
                pass

        if self.is_pyusb_active:
            ok, msg = self.py_fb.reboot(target)
            return ok, msg or "Reboot OKAY"

        return False, "Not connected"

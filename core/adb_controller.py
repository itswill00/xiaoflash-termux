import os
import sys
import shutil
import subprocess

class ADBController:
    """ADB-OTG Controller with Root Environment Exports"""

    def __init__(self):
        self.adb_bin = shutil.which("adb") or "/data/data/com.termux/files/usr/bin/adb"

    def _get_env(self):
        env = dict(os.environ)
        env["PATH"] = f"/data/data/com.termux/files/usr/bin:{env.get('PATH', '')}"
        env["LD_LIBRARY_PATH"] = "/data/data/com.termux/files/usr/lib"
        env["HOME"] = "/data/data/com.termux/files/home"
        env["ANDROID_USER_HOME"] = "/data/data/com.termux/files/home/.android"
        return env

    def scan_adb_devices(self):
        """Scans for connected ADB OTG devices"""
        if not os.path.exists(self.adb_bin):
            return None, "ADB binary not found."

        try:
            env = self._get_env()
            res = subprocess.check_output([self.adb_bin, "devices"], text=True, env=env, stderr=subprocess.STDOUT).strip()
            lines = res.splitlines()

            for line in lines:
                parts = line.split()
                if len(parts) >= 2 and parts[0] != "List":
                    serial = parts[0]
                    state = parts[1] # 'device', 'recovery', 'sideload', 'unauthorized'
                    return {
                        "serial": serial,
                        "state": state,
                        "is_simulated": False
                    }, f"ADB Device detected: {serial} ({state})"

        except Exception as e:
            return None, str(e)

        return None, "No ADB device detected."

    def get_device_props(self, serial):
        """Reads system properties via ADB shell"""
        if not os.path.exists(self.adb_bin):
            return {}

        env = self._get_env()
        props = {}

        prop_keys = {
            "model": "ro.product.model",
            "device": "ro.product.device",
            "marketname": "ro.product.marketname",
            "android_ver": "ro.build.version.release",
            "miui_ver": "ro.build.version.incremental",
            "locked": "ro.boot.flash.locked"
        }

        for label, prop_name in prop_keys.items():
            try:
                cmd = [self.adb_bin]
                if serial and not serial.startswith("XM_OTG"):
                    cmd.extend(["-s", serial])
                cmd.extend(["shell", "getprop", prop_name])

                val = subprocess.check_output(cmd, text=True, env=env, stderr=subprocess.DEVNULL).strip()
                if val:
                    props[label] = val
            except:
                pass

        return props

    def reboot(self, serial, target="bootloader"):
        """Reboots target device via ADB with stdout/stderr capture"""
        if not os.path.exists(self.adb_bin):
            return False, "ADB binary missing"

        env = self._get_env()
        target_cmd = "bootloader" if target == "bootloader" else ("recovery" if target == "recovery" else "")
        
        cmd = [self.adb_bin]
        if serial and not serial.startswith("XM_OTG"):
            cmd.extend(["-s", serial])
        cmd.append("reboot")
        if target_cmd:
            cmd.append(target_cmd)

        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
            stdout, stderr = proc.communicate()
            out_combined = (stdout + "\n" + stderr).strip()

            if proc.returncode == 0 or "reboot" in out_combined.lower() or not out_combined:
                return True, f"Reboot command sent ({target})"
            else:
                return False, out_combined or f"Exit code {proc.returncode}"
        except Exception as e:
            return False, str(e)

    def sideload(self, serial, zip_path, callback=None):
        """Sideloads an OTA/Recovery ZIP file via ADB"""
        if not os.path.exists(zip_path):
            return False, f"File missing: {zip_path}"

        env = self._get_env()
        cmd = [self.adb_bin]
        if serial and not serial.startswith("XM_OTG"):
            cmd.extend(["-s", serial])
        cmd.extend(["sideload", zip_path])

        try:
            if callback:
                callback("Initiating ADB sideload transfer...", "process")

            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
            stdout, stderr = proc.communicate()
            out_combined = (stdout + "\n" + stderr).strip()

            if proc.returncode == 0 or "Total xfer" in out_combined or "100%" in out_combined:
                if callback:
                    callback("Sideload completed OKAY", "success")
                return True, "Sideload OKAY"
            else:
                err_msg = stderr.strip() or stdout.strip() or "Sideload failed"
                if callback:
                    callback(f"Sideload failed: {err_msg}", "error")
                return False, err_msg
        except Exception as e:
            if callback:
                callback(f"Sideload error: {str(e)}", "error")
            return False, str(e)

    def shell(self, serial, cmd_str):
        """Executes a custom shell command via ADB"""
        if not os.path.exists(self.adb_bin):
            return False, "ADB binary missing"

        env = self._get_env()
        cmd = [self.adb_bin]
        if serial and not serial.startswith("XM_OTG"):
            cmd.extend(["-s", serial])
        cmd.extend(["shell", cmd_str])

        try:
            res = subprocess.check_output(cmd, text=True, env=env, stderr=subprocess.STDOUT).strip()
            return True, res
        except subprocess.CalledProcessError as e:
            return False, e.output.strip() or str(e)
        except Exception as e:
            return False, str(e)

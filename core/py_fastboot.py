import usb.core
import usb.util
import usb.backend.libusb1
import ctypes
import sys
import os
import time

class PyFastboot:
    """Enterprise-Grade Pure Python Fastboot USB Protocol Engine"""

    def __init__(self, vendor_id=0x18d1, product_id=0xd00d):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.dev = None
        self.ep_in = None
        self.ep_out = None
        self.backend = self._init_backend()

    def _init_backend(self):
        """Initializes libusb-1.0 backend with robust Termux path fallback"""
        lib_paths = [
            "/data/data/com.termux/files/usr/lib/libusb-1.0.so",
            "/usr/lib/libusb-1.0.so",
            "/usr/lib/aarch64-linux-gnu/libusb-1.0.so"
        ]
        for lib_path in lib_paths:
            if os.path.exists(lib_path):
                try:
                    usb.backend.libusb1._lib_object = None
                    backend = usb.backend.libusb1.get_backend(find_library=lambda x, p=lib_path: p)
                    if backend is not None:
                        return backend
                except:
                    pass
        return None

    def connect(self):
        """Discovers and initializes Fastboot USB device endpoints"""
        try:
            find_kwargs = {"backend": self.backend} if self.backend else {}
            
            # 1. Vendor search (Google 0x18d1, Xiaomi 0x2717, or Product 0xd00d)
            self.dev = usb.core.find(idVendor=self.vendor_id, **find_kwargs)
            if self.dev is None:
                self.dev = usb.core.find(idVendor=0x2717, **find_kwargs)
            
            if self.dev is None:
                # 2. Iterate connected devices
                for d in usb.core.find(find_all=True, **find_kwargs):
                    if d.idProduct == 0xd00d or d.idVendor in (0x18d1, 0x2717):
                        self.dev = d
                        break

            if self.dev is None:
                return False, "Fastboot device not found on USB OTG bus."

            # Set active configuration
            try:
                self.dev.set_configuration()
            except usb.core.USBError:
                pass  # Already configured

            cfg = self.dev.get_active_configuration()
            intf = cfg[(0, 0)]

            # Claim interface if kernel driver attached
            try:
                if self.dev.is_kernel_driver_active(0):
                    self.dev.detach_kernel_driver(0)
            except (NotImplementedError, usb.core.USBError):
                pass

            for ep in intf:
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                    self.ep_out = ep
                elif usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                    self.ep_in = ep

            if not self.ep_out or not self.ep_in:
                return False, "Failed to locate Fastboot USB bulk IN/OUT endpoints."

            serial = usb.util.get_string(self.dev, self.dev.iSerialNumber) if self.dev.iSerialNumber else "11bb599a"
            return True, serial

        except Exception as e:
            return False, f"USB Fastboot initialization error: {str(e)}"

    def read_response(self, timeout=10000):
        """Reads responses from Fastboot IN endpoint until OKAY or FAIL"""
        info_msgs = []
        start_time = time.time()

        while True:
            try:
                resp_data = self.ep_in.read(512, timeout=timeout)
                resp_str = bytes(resp_data).decode('ascii', errors='ignore').strip()

                if resp_str.startswith("OKAY"):
                    return True, resp_str[4:].strip()
                elif resp_str.startswith("FAIL"):
                    return False, resp_str[4:].strip()
                elif resp_str.startswith("INFO"):
                    info_msgs.append(resp_str[4:].strip())
                elif resp_str.startswith("DATA"):
                    return True, resp_str
                else:
                    if resp_str:
                        return True, resp_str

            except usb.core.USBTimeoutError:
                if time.time() - start_time > (timeout / 1000.0):
                    return False, "USB Timeout waiting for Fastboot response"
            except Exception as e:
                return False, str(e)

    def send_cmd(self, cmd_str, timeout=10000):
        """Sends a fastboot ASCII command string and waits for status"""
        if not self.dev or not self.ep_out or not self.ep_in:
            return False, "Not connected"

        try:
            self.ep_out.write(cmd_str.encode('ascii'), timeout=timeout)
            return self.read_response(timeout=timeout)
        except Exception as e:
            return False, str(e)

    def send_data(self, file_path, callback=None):
        """Sends binary payload data in bulk chunks with zero data loss"""
        if not os.path.exists(file_path):
            return False, "File missing"

        filesize = os.path.getsize(file_path)
        hex_size = f"{filesize:08x}"

        # 1. Download command
        ok, resp = self.send_cmd(f"download:{hex_size}")
        if not ok:
            return False, f"Download command failed: {resp}"

        # 2. Transfer binary stream
        try:
            chunk_size = 1048576  # 1MB buffer chunk for maximum USB throughput
            written_total = 0

            with open(file_path, "rb") as f:
                while written_total < filesize:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Ensure full chunk is written
                    offset = 0
                    while offset < len(chunk):
                        written = self.ep_out.write(chunk[offset:], timeout=30000)
                        offset += written

                    written_total += len(chunk)
                    if callback:
                        callback(written_total, filesize)

            # Read response after data transfer completes
            return self.read_response(timeout=30000)

        except Exception as e:
            return False, f"USB stream write failed: {str(e)}"

    def getvar(self, var_name):
        ok, res = self.send_cmd(f"getvar:{var_name}", timeout=3000)
        if ok:
            return res.strip()
        return "N/A"

    def reboot(self, target="system"):
        cmd_map = {
            "bootloader": "reboot-bootloader",
            "recovery": "reboot-recovery",
            "system": "reboot"
        }
        cmd = cmd_map.get(target, "reboot")
        res = self.send_cmd(cmd)
        self.dispose()
        return res

    def dispose(self):
        """Safely disposes USB resources and releases interface"""
        if self.dev:
            try:
                usb.util.dispose_resources(self.dev)
            except:
                pass
            self.dev = None
            self.ep_in = None
            self.ep_out = None

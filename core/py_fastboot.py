import usb.core
import usb.util
import usb.backend.libusb1
import ctypes
import sys
import os
import time

class PyFastboot:
    """Pure Python Fastboot USB Protocol Engine with USB Reset Recovery"""

    def __init__(self, vendor_id=0x18d1, product_id=0xd00d):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.dev = None
        self.ep_in = None
        self.ep_out = None
        self.backend = self._init_backend()

    def _init_backend(self):
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
        try:
            find_kwargs = {"backend": self.backend} if self.backend else {}
            
            known_vids = [0x18d1, 0x2717, 0x0e8d, 0x05c6, 0x0b05, 0x2a45, 0x22d9, 0x2a70]
            for vid in known_vids:
                self.dev = usb.core.find(idVendor=vid, **find_kwargs)
                if self.dev is not None:
                    break
            
            if self.dev is None:
                try:
                    for d in usb.core.find(find_all=True, **find_kwargs):
                        if d.idProduct in (0xd00d, 0x4ee0, 0x0fff, 0x900e) or d.idVendor in known_vids:
                            self.dev = d
                            break
                        try:
                            for cfg in d:
                                for intf in cfg:
                                    if intf.bInterfaceClass == 0xff and intf.bInterfaceSubClass == 0x42:
                                        self.dev = d
                                        break
                        except:
                            pass
                        if self.dev is not None:
                            break
                except:
                    pass

            if self.dev is None:
                return False, "Fastboot device not found on USB OTG bus."

            # Reset USB bus state to resolve [Errno 16] Resource busy locks
            try:
                self.dev.reset()
            except:
                pass

            try:
                if self.dev.is_kernel_driver_active(0):
                    self.dev.detach_kernel_driver(0)
            except:
                pass

            try:
                cfg = self.dev.get_active_configuration()
            except:
                try:
                    self.dev.set_configuration()
                    cfg = self.dev.get_active_configuration()
                except:
                    pass

            intf = cfg[(0, 0)]
            for ep in intf:
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                    self.ep_out = ep
                elif usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                    self.ep_in = ep

            if not self.ep_out or not self.ep_in:
                return False, "Failed to locate Fastboot USB bulk IN/OUT endpoints."

            serial = "11bb599a"
            try:
                if self.dev.iSerialNumber:
                    serial = usb.util.get_string(self.dev, self.dev.iSerialNumber)
            except:
                pass

            return True, serial

        except Exception as e:
            return False, f"USB Fastboot initialization error: {str(e)}"

    def read_response(self, timeout=10000):
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

            except usb.core.USBTimeoutError:
                if (time.time() - start_time) * 1000 > timeout:
                    return False, "Timeout waiting for Fastboot response."
            except Exception as e:
                return False, str(e)

    def send_command(self, cmd_str, timeout=10000):
        try:
            self.ep_out.write(cmd_str.encode('ascii'), timeout=timeout)
            return self.read_response(timeout=timeout)
        except Exception as e:
            return False, str(e)

    def getvar(self, var_name):
        ok, res = self.send_command(f"getvar:{var_name}")
        if ok:
            return res
        return "N/A"

    def send_data(self, file_path, callback=None):
        if not os.path.exists(file_path):
            return False, f"File missing: {file_path}"

        file_size = os.path.getsize(file_path)
        hex_size = f"{file_size:08x}"
        
        ok, res = self.send_command(f"download:{hex_size}")
        if not ok or not res.startswith("DATA"):
            return False, f"Download handshake failed: {res}"

        chunk_size = 1048576  # 1MB throughput
        sent_bytes = 0

        with open(file_path, "rb") as f:
            while sent_bytes < file_size:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                self.ep_out.write(chunk, timeout=30000)
                sent_bytes += len(chunk)
                if callback:
                    callback(sent_bytes, file_size)

        return self.read_response(timeout=30000)

    def flash_partition(self, partition, file_path, callback=None):
        ok_dl, res_dl = self.send_data(file_path, callback=callback)
        if not ok_dl:
            return False, res_dl

        return self.send_command(f"flash:{partition}", timeout=300000)

    def reboot(self, target="system"):
        if target == "bootloader":
            return self.send_command("reboot-bootloader")
        elif target == "recovery":
            return self.send_command("reboot-recovery")
        return self.send_command("reboot")

    def dispose(self):
        if self.dev:
            try:
                usb.util.dispose_resources(self.dev)
            except:
                pass
            self.dev = None

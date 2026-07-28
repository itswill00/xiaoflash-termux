import usb.core
import usb.util
import usb.backend.libusb1
import ctypes
import sys
import os

class PyFastboot:
    """Pure Python Fastboot USB Protocol Client via PyUSB"""

    def __init__(self, vendor_id=0x18d1, product_id=0xd00d):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.dev = None
        self.ep_in = None
        self.ep_out = None
        self.backend = self._init_backend()

    def _init_backend(self):
        """Initializes libusb-1.0 backend for PyUSB in Termux environment"""
        lib_path = "/data/data/com.termux/files/usr/lib/libusb-1.0.so"
        if os.path.exists(lib_path):
            try:
                usb.backend.libusb1._lib_object = None
                return usb.backend.libusb1.get_backend(find_library=lambda x: lib_path)
            except:
                pass
        return None

    def connect(self):
        try:
            # Search for Google Vendor 0x18d1, Xiaomi 0x2717 or Fastboot product ID 0xd00d
            if self.backend:
                self.dev = usb.core.find(backend=self.backend, idVendor=self.vendor_id)
                if self.dev is None:
                    self.dev = usb.core.find(backend=self.backend, idVendor=0x2717)
            else:
                self.dev = usb.core.find(idVendor=self.vendor_id)
                if self.dev is None:
                    self.dev = usb.core.find(idVendor=0x2717)

            if self.dev is None:
                # Scan all connected USB devices
                find_kwargs = {"backend": self.backend} if self.backend else {}
                for d in usb.core.find(find_all=True, **find_kwargs):
                    if d.idProduct == 0xd00d or d.idVendor in (0x18d1, 0x2717):
                        self.dev = d
                        break

            if self.dev is None:
                return False, "USB Fastboot device not found on OTG bus."

            self.dev.set_configuration()
            cfg = self.dev.get_active_configuration()
            intf = cfg[(0, 0)]

            for ep in intf:
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                    self.ep_out = ep
                elif usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                    self.ep_in = ep

            if not self.ep_out or not self.ep_in:
                return False, "Failed to locate Fastboot USB IN/OUT endpoints."

            serial = usb.util.get_string(self.dev, self.dev.iSerialNumber) if self.dev.iSerialNumber else "11bb599a"
            return True, serial

        except Exception as e:
            return False, f"USB Fastboot initialization error: {str(e)}"

    def send_cmd(self, cmd_str):
        if not self.dev or not self.ep_out or not self.ep_in:
            return False, "Not connected"

        try:
            self.ep_out.write(cmd_str.encode('ascii'))
            resp_data = self.ep_in.read(512, timeout=5000)
            resp_str = bytes(resp_data).decode('ascii', errors='ignore')

            if resp_str.startswith("OKAY"):
                return True, resp_str[4:]
            elif resp_str.startswith("FAIL"):
                return False, resp_str[4:]
            elif resp_str.startswith("INFO"):
                return True, resp_str[4:]
            else:
                return True, resp_str
        except Exception as e:
            return False, str(e)

    def getvar(self, var_name):
        ok, res = self.send_cmd(f"getvar:{var_name}")
        if ok:
            return res.strip()
        return "N/A"

    def reboot(self, target="system"):
        if target == "bootloader":
            return self.send_cmd("reboot-bootloader")
        elif target == "recovery":
            return self.send_cmd("reboot-recovery")
        else:
            return self.send_cmd("reboot")

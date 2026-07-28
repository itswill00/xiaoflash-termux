#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.fastboot_otg import FastbootOTG

def main():
    print("====================================================")
    print("🔍 XiaoFlash OTG Real-time Monitor & Debugger")
    print("====================================================")
    
    otg = FastbootOTG()
    device, msg = otg.scan_devices()

    if not device.get("is_simulated"):
        print("\n✅ PHYSICAL FASTBOOT DEVICE DETECTED VIA USB OTG!")
        print("----------------------------------------------------")
        print(f"📱 Serial Number    : {device['serial']}")
        print(f"🏷️  Codename Product : {device['product']} ({device['name']})")
        print(f"🛡️  Anti-Rollback    : v{device['anti']}")
        print(f"🔓 Bootloader Status: {device['unlocked'].upper()}")
        print(f"🔋 Battery Voltage  : {device['battery']}")
        print(f"⚡ Driver Engine     : {device['mode']}")
        print("----------------------------------------------------")
        print("✨ Target Xiaomi device ready for OTG flashing!")
    else:
        print("\n⚠️ Device not detected via OTG.")

if __name__ == "__main__":
    main()

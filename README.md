# XiaoFlash Termux OTG ⚡

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Platform Termux](https://img.shields.io/badge/platform-Termux-green.svg)](https://termux.dev/)
[![License MIT](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Xiaomi Fastboot](https://img.shields.io/badge/Xiaomi-HyperOS%20%7C%20MIUI-red.svg)](https://miui.com)

**XiaoFlash** is a lightweight, efficient, and robust CLI tool designed to flash official Xiaomi, Redmi, and POCO Fastboot ROMs directly from **Termux on Android via USB OTG cable**.

Built with a custom **PyUSB Fastboot Engine**, it bypasses standard Termux `android-tools` segfault issues and offers a clean, human-crafted terminal user experience with built-in **Anti-Rollback (ARB) Protection Guard**.

---

## ✨ Features

- 🔌 **Native USB OTG Fastboot Engine**: Direct PyUSB communication with Xiaomi fastboot bootloaders via OTG.
- 🛡️ **Anti-Rollback (ARB) Protection**: Automatic ARB index comparison to prevent hard bricks (deadboot).
- ⚡ **3 Official Flashing Modes**:
  - `Clean All (flash_all)` - Full wipe & fresh ROM install (Recommended).
  - `Save User Data (flash_all_except_storage)` - Update system without wiping internal storage & photos.
  - `Clean All & Lock` - Clean install + Re-lock Xiaomi OEM Bootloader.
- 🛠️ **Single Partition Flashing**: Flash individual `.img` partitions (`boot.img`, `init_boot.img`, `recovery.img`, `super.img`, `vbmeta.img`, etc.).
- 🔄 **Rescue Toolkit**: One-click reboot commands (`System`, `Fastboot`, `Recovery`).
- 🎨 **Compact & Efficient UI**: Clean, clutter-free terminal interface inspired by modern Unix CLI utilities.

---

## 🚀 Quick Installation

Run the following 1-line command in **Termux**:

```bash
git clone https://github.com/your-username/xiaoflash-termux.git && cd xiaoflash-termux && bash setup.sh
```

---

## 📖 Usage Guide

Once installed, simply launch the tool from anywhere in Termux by typing:

```bash
xiaoflash
```

### 🔌 Connecting target phone via OTG:

1. Connect the **USB OTG Adapter** to the **Host Phone** (the device running Termux).
2. Connect a standard USB cable from the OTG adapter to the **Target Phone** (Xiaomi device to be flashed).
3. Put the **Target Phone** into **Fastboot Mode**:
   - Power off the target device.
   - Press & hold `Power Button + Volume Down` until the **FASTBOOT** logo appears.
4. Launch `xiaoflash` in Termux. The device model, serial, ARB index, and battery voltage will be detected automatically!

---

## 🛠️ Project Structure

```
xiaoflash-termux/
├── core/
│   ├── arb_checker.py      # Anti-Rollback safety guard
│   ├── fastboot_otg.py     # Fastboot OTG controller
│   ├── py_fastboot.py      # Pure Python PyUSB Fastboot driver
│   ├── rom_extractor.py    # .tgz / .zip ROM extractor & script parser
│   └── ui_menu.py          # Clean CLI interface renderer
├── xiaoflash               # Executable main CLI script
├── setup.sh                # Automatic Termux installer
├── requirements.txt        # Python dependencies (rich, pyusb)
└── README.md
```

---

## ⚠️ Safety Disclaimer

- **Root Access**: Host phone running Termux requires root access (`su`) to open raw USB OTG device handles under Android SELinux policies.
- **Battery Level**: Always ensure the target phone's battery level is above **50%** before flashing.
- **Cable Integrity**: Do not disconnect the USB OTG cable while flashing partitions.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

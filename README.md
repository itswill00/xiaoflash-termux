# XiaoFlash Termux OTG

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Platform Termux](https://img.shields.io/badge/platform-Termux-green.svg)](https://termux.dev/)
[![License MIT](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Xiaomi Fastboot](https://img.shields.io/badge/Xiaomi-HyperOS%20%7C%20MIUI-red.svg)](https://miui.com)

**XiaoFlash** is a lightweight, efficient CLI utility designed to flash official Xiaomi, Redmi, and POCO Fastboot ROMs directly from **Termux on Android via USB OTG cable**.

Built with a custom **PyUSB Fastboot Engine** and **Android Sparse Image Sub-Chunking**, it provides a clean, minimal terminal user experience with built-in Anti-Rollback (ARB) safety checks.

---

## Features

- **Native USB OTG Fastboot Driver**: Direct PyUSB communication with Xiaomi fastboot bootloaders via OTG.
- **Android Sparse Sub-Chunking Engine**: Auto-splits large partitions (`system.img`, `super.img`, `userdata.img`) into valid sub-chunks (`<= 300MB`) to comply with hardware `max-download-size` limits.
- **Anti-Rollback (ARB) Guard**: Automatic ARB index comparison to prevent hard bricks (deadboot).
- **Interactive Fastboot CLI Shell**: Custom fastboot command shell (`getvar`, `flash`, `erase`, `reboot`, `oem`, `flashing`, `devices`).
- **3 Flashing Modes**:
  - `Clean All (flash_all)` - Full wipe & fresh ROM install.
  - `Save User Data (flash_all_except_storage)` - System update preserving internal storage.
  - `Clean All & Lock` - Clean install + Re-lock Xiaomi OEM Bootloader.
- **Single Partition Flashing**: Flash individual `.img` partitions (`boot.img`, `recovery.img`, `super.img`, etc.).
- **Live MiFirm Scraper**: Auto-detect device model codename and resolve verified fastboot `.tgz` CDN links.

---

## Installation

Run the following 1-line command in **Termux**:

```bash
git clone https://github.com/itswill00/xiaoflash-termux.git && cd xiaoflash-termux && bash setup.sh
```

---

## Usage Guide

Once installed, launch the utility from anywhere in Termux by typing:

```bash
xiaoflash
```

### Connecting target phone via OTG:

1. Connect the **USB OTG Adapter** to the **Host Phone** (device running Termux).
2. Connect a USB cable from the OTG adapter to the **Target Phone** (Xiaomi device to be flashed).
3. Put the **Target Phone** into **Fastboot Mode**:
   - Power off target device.
   - Press & hold `Power + Volume Down` until the **FASTBOOT** logo appears.
4. Launch `xiaoflash` in Termux. Device model, serial, ARB index, and battery voltage will be detected automatically.

---

## Project Structure

```
xiaoflash-termux/
├── core/
│   ├── arb_checker.py      # Anti-Rollback safety guard
│   ├── fastboot_otg.py     # Fastboot OTG controller
│   ├── fastboot_shell.py    # Interactive Fastboot CLI Shell
│   ├── mifirm_scraper.py   # Live MiFirm.net ROM scraper
│   ├── py_fastboot.py      # Pure Python PyUSB Fastboot driver
│   ├── rom_downloader.py   # Resumable HTTP Range ROM downloader
│   ├── rom_extractor.py    # .tgz / .zip ROM extractor & script parser
│   ├── sparse_splitter.py  # Android Sparse & RAW Image Sub-Chunking Engine
│   └── ui_menu.py          # Clean CLI interface renderer
├── xiaoflash               # Executable main CLI launcher
├── setup.sh                # Automatic Termux installer
├── requirements.txt        # Python dependencies (rich, pyusb)
└── README.md
```

---

## Requirements & Notes

- **Root Access**: Host phone running Termux requires root access (`su`) to open raw USB OTG device handles under Android SELinux policies.
- **Battery Level**: Ensure target phone battery level is above 30% before flashing.
- **Cable Integrity**: Do not disconnect the USB OTG cable while flashing partitions.

---

## License

This project is licensed under the [MIT License](LICENSE).

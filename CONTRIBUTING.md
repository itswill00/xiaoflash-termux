# Contributing to XiaoFlash Termux OTG ⚡

Thank you for considering contributing to **XiaoFlash**! Contributions are welcome and appreciated.

## How Can I Contribute?

### 1. Adding New Device Codenames
You can add support for new Xiaomi / Redmi / POCO devices in `core/fastboot_otg.py` and `core/rom_downloader.py`:
```python
name_map = {
    "ginkgo": "Redmi Note 8",
    "sweet": "Redmi Note 10 Pro",
    "your_codename": "Device Name"
}
```

### 2. Reporting Bugs
- Use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md).
- Provide device details, Termux logs, and steps to reproduce.

### 3. Pull Request Guidelines
- Follow clean Python coding style (PEP 8).
- Ensure existing features work without breaking OTG communication.
- Make commits with clean messages and signoff (`git commit -s`).

Thank you for making XiaoFlash better for everyone!

#!/data/data/com.termux/files/usr/bin/bash
# XiaoFlash Termux OTG Installer Script

set -e

echo "-----------------------------------------------------------------"
echo "XiaoFlash - Xiaomi Fastboot OTG Utility Installer"
echo "-----------------------------------------------------------------"

# 1. Update package lists and install required dependencies
echo "Installing required Termux packages (python, libusb, android-tools)..."
pkg update -y || true
pkg install python libusb android-tools -y

# 2. Install Python requirements
echo "Installing Python dependencies (rich, pyusb)..."
pip install --break-system-packages -r "$(dirname "$0")/requirements.txt" || pip install -r "$(dirname "$0")/requirements.txt"

# 3. Setup launcher link
LAUNCHER_PATH="/data/data/com.termux/files/usr/bin/xiaoflash"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/xiaoflash"

chmod +x "$SCRIPT_PATH"

cat << 'EOF' > "$LAUNCHER_PATH"
#!/data/data/com.termux/files/usr/bin/bash
TARGET_SCRIPT="/data/data/com.termux/files/home/xiaoflash-termux/xiaoflash"

if [ ! -f "$TARGET_SCRIPT" ]; then
    TARGET_SCRIPT="$(find /data/data/com.termux/files/home -name "xiaoflash" -type f | head -n 1)"
fi

if [ "$(id -u)" -ne 0 ]; then
    su -c "export PATH=/data/data/com.termux/files/usr/bin:\$PATH; export LD_LIBRARY_PATH=/data/data/com.termux/files/usr/lib; python3 $TARGET_SCRIPT \"\$@\""
else
    export PATH=/data/data/com.termux/files/usr/bin:$PATH
    export LD_LIBRARY_PATH=/data/data/com.termux/files/usr/lib
    python3 "$TARGET_SCRIPT" "$@"
fi
EOF

chmod +x "$LAUNCHER_PATH"

echo "-----------------------------------------------------------------"
echo "XiaoFlash installation completed successfully."
echo "Usage: Simply type 'xiaoflash' anywhere in Termux."
echo "-----------------------------------------------------------------"

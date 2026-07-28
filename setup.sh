#!/data/data/com.termux/files/usr/bin/bash
# XiaoFlash Termux OTG Installer Script

set -e

echo "===================================================="
echo "⚡ Installing XiaoFlash - Xiaomi Fastboot OTG Tool"
echo "===================================================="

# 1. Update package lists and install required dependencies
echo "📦 Installing required Termux packages (python, libusb, android-tools)..."
pkg update -y
pkg install python libusb android-tools -y

# 2. Install Python requirements
echo "🐍 Installing Python dependencies (rich, pyusb)..."
pip install -r "$(dirname "$0")/requirements.txt"

# 3. Setup launcher link
LAUNCHER_PATH="/data/data/com.termux/files/usr/bin/xiaoflash"
SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/xiaoflash"

chmod +x "$SCRIPT_PATH"

cat << 'EOF' > "$LAUNCHER_PATH"
#!/data/data/com.termux/files/usr/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_SCRIPT="/data/data/com.termux/files/home/xiaoflash-termux/xiaoflash"

if [ ! -f "$TARGET_SCRIPT" ]; then
    TARGET_SCRIPT="$(find /data/data/com.termux/files/home -name "xiaoflash" -type f | head -n 1)"
fi

if [ "$(id -u)" -ne 0 ]; then
    su -c "PATH=$PATH:/data/data/com.termux/files/usr/bin LD_LIBRARY_PATH=/data/data/com.termux/files/usr/lib python3 $TARGET_SCRIPT $*"
else
    PATH=$PATH:/data/data/com.termux/files/usr/bin LD_LIBRARY_PATH=/data/data/com.termux/files/usr/lib python3 "$TARGET_SCRIPT" "$@"
fi
EOF

chmod +x "$LAUNCHER_PATH"

echo "===================================================="
echo "✅ XiaoFlash installation completed successfully!"
echo "===================================================="
echo "Usage: Simply type 'xiaoflash' anywhere in Termux."
echo "===================================================="

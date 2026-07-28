import os
import tarfile
import zipfile
import shutil

class ROMExtractor:
    """Manages Xiaomi Fastboot ROM Extraction and Shell Script Parsing in Termux"""

    @staticmethod
    def extract_rom(file_path, output_dir, progress_callback=None):
        """Extracts .tgz / .tar.gz / .zip Fastboot package"""
        if not os.path.exists(file_path):
            return False, f"File tidak ditemukan: {file_path}"

        os.makedirs(output_dir, exist_ok=True)
        
        try:
            if progress_callback:
                progress_callback(f"Mengekstrak package: {os.path.basename(file_path)}...", "info")

            if file_path.endswith(".tgz") or file_path.endswith(".tar.gz") or file_path.endswith(".tar"):
                with tarfile.open(file_path, "r:*") as tar:
                    tar.extractall(path=output_dir)
            elif file_path.endswith(".zip"):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(output_dir)
            else:
                return False, "Format file tidak didukung. Wajib .tgz / .tar.gz / .zip"

            if progress_callback:
                progress_callback("Ekstraksi ROM selesai!", "success")

            return True, output_dir

        except Exception as e:
            return False, f"Gagal mengekstrak ROM: {str(e)}"

    @staticmethod
    def parse_flash_script(images_dir, mode="flash_all"):
        """
        Parses image directory or flash_all.sh script to obtain list of partitions to flash
        """
        script_name = f"{mode}.sh"
        script_path = os.path.join(images_dir, script_name)

        partitions = []

        if os.path.exists(script_path):
            # Parse commands from flash_all.sh
            with open(script_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith("fastboot") and "flash" in line:
                        parts = line.split()
                        try:
                            flash_idx = parts.index("flash")
                            part_name = parts[flash_idx + 1]
                            img_file = parts[flash_idx + 2]
                            partitions.append((part_name, img_file))
                        except:
                            pass

        if not partitions:
            # Fallback scan images folder directly for .img files
            img_dir = os.path.join(images_dir, "images") if os.path.exists(os.path.join(images_dir, "images")) else images_dir
            if os.path.exists(img_dir):
                standard_parts = ["gpt.bin", "boot.img", "init_boot.img", "dtbo.img", "recovery.img", "super.img", "vbmeta.img", "vendor_boot.img", "cust.img"]
                for item in standard_parts:
                    full_p = os.path.join(img_dir, item)
                    if os.path.exists(full_p):
                        part_name = item.replace(".img", "").replace(".bin", "")
                        partitions.append((part_name, full_p))

        return partitions

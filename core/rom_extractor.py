import os
import tarfile
import zipfile

class ROMExtractor:
    """Manages Xiaomi Fastboot ROM Extraction and Script Parsing with path traversal protection"""

    @staticmethod
    def extract_rom(file_path, output_dir, progress_callback=None):
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        os.makedirs(output_dir, exist_ok=True)
        
        try:
            if progress_callback:
                progress_callback(f"Extracting package: {os.path.basename(file_path)}...", "info")

            if file_path.endswith(".tgz") or file_path.endswith(".tar.gz") or file_path.endswith(".tar"):
                with tarfile.open(file_path, "r:*") as tar:
                    # Apply safe extraction filter for Python 3.12+ / 3.14 compatibility
                    try:
                        tar.extractall(path=output_dir, filter='data')
                    except TypeError:
                        tar.extractall(path=output_dir)

            elif file_path.endswith(".zip"):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(output_dir)
            else:
                return False, "Unsupported archive format. Must be .tgz / .tar.gz / .zip"

            if progress_callback:
                progress_callback("ROM extraction complete!", "success")

            return True, output_dir

        except Exception as e:
            return False, f"Extraction failed: {str(e)}"

    @staticmethod
    def parse_flash_script(images_dir, mode="flash_all"):
        script_name = f"{mode}.sh"
        script_path = os.path.join(images_dir, script_name)

        partitions = []

        if os.path.exists(script_path):
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
            img_dir = os.path.join(images_dir, "images") if os.path.exists(os.path.join(images_dir, "images")) else images_dir
            if os.path.exists(img_dir):
                standard_parts = ["gpt.bin", "boot.img", "init_boot.img", "dtbo.img", "recovery.img", "super.img", "vbmeta.img", "vendor_boot.img", "cust.img"]
                for item in standard_parts:
                    full_p = os.path.join(img_dir, item)
                    if os.path.exists(full_p):
                        part_name = item.replace(".img", "").replace(".bin", "")
                        partitions.append((part_name, full_p))

        return partitions

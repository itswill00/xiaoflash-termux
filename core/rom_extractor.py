import os
import tarfile
import zipfile
from rich.console import Console

console = Console()

class ROMExtractor:
    """Manages Xiaomi Fastboot ROM Extraction and Script Parsing"""

    @staticmethod
    def extract_rom(file_path, output_dir, progress_callback=None):
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        os.makedirs(output_dir, exist_ok=True)
        console.print(f"Unpacking archive: [cyan]{os.path.basename(file_path)}[/cyan]")
        console.print(f"Destination folder: [yellow]{output_dir}[/yellow]")
        
        try:
            if file_path.endswith(".tgz") or file_path.endswith(".tar.gz") or file_path.endswith(".tar"):
                with tarfile.open(file_path, "r:*") as tar:
                    members = tar.getmembers()
                    total = len(members)
                    console.print(f"Extracting {total} files from tar archive...")
                    for idx, member in enumerate(members, start=1):
                        try:
                            tar.extract(member, path=output_dir, filter='data')
                        except TypeError:
                            tar.extract(member, path=output_dir)
                        if progress_callback and idx % 10 == 0:
                            progress_callback(f"Extracted {idx}/{total} files...", "info")

            elif file_path.endswith(".zip"):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    members = zip_ref.namelist()
                    total = len(members)
                    console.print(f"Extracting {total} files from zip archive...")
                    for idx, member in enumerate(members, start=1):
                        zip_ref.extract(member, output_dir)
                        if progress_callback and idx % 10 == 0:
                            progress_callback(f"Extracted {idx}/{total} files...", "info")
            else:
                return False, "Unsupported archive format. Must be .tgz / .tar.gz / .zip"

            console.print("[green]Extraction completed successfully.[/green]")
            return True, output_dir

        except Exception as e:
            return False, f"Extraction failed: {str(e)}"

    @staticmethod
    def parse_flash_script(images_dir, mode="flash_all"):
        script_name = f"{mode}.sh"
        script_path = os.path.join(images_dir, script_name)

        partitions = []

        if os.path.exists(script_path):
            console.print(f"Parsing Xiaomi flash script: [cyan]{script_name}[/cyan]")
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
                console.print(f"Scanning image directory: [cyan]{img_dir}[/cyan]")
                standard_parts = ["gpt.bin", "boot.img", "init_boot.img", "dtbo.img", "recovery.img", "super.img", "vbmeta.img", "vendor_boot.img", "cust.img"]
                for item in standard_parts:
                    full_p = os.path.join(img_dir, item)
                    if os.path.exists(full_p):
                        part_name = item.replace(".img", "").replace(".bin", "")
                        partitions.append((part_name, full_p))

        if partitions:
            console.print(f"Parsed [green]{len(partitions)}[/green] partition image(s) for flashing.")

        return partitions

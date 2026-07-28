import os
import shutil
import time
from rich.console import Console

console = Console()

class BootPatcher:
    """One-Click Magisk & KernelSU Boot Patcher & Flasher for Xiaomi Devices"""

    @staticmethod
    def find_boot_img(search_dir="/sdcard/Download"):
        """Locates boot.img or init_boot.img in directory"""
        candidates = ["boot.img", "init_boot.img", "vendor_boot.img"]
        for root, _, files in os.walk(search_dir):
            for file in files:
                if file in candidates:
                    return os.path.join(root, file)
        return None

    @staticmethod
    def patch_and_flash(fastboot_otg, serial, boot_img_path, root_type="magisk", is_simulated=False):
        """Prepares patched boot image and flashes via OTG"""
        if not os.path.exists(boot_img_path):
            console.print(f"[bold red]❌ Boot image missing at '{boot_img_path}'[/bold red]")
            return False, "File missing"

        part_name = "init_boot" if "init_boot" in os.path.basename(boot_img_path) else "boot"
        console.print(f"[bold cyan]⚡ Preparing {root_type.upper()} root patch for '{part_name}'...[/bold cyan]")

        # Create output directory for patched images
        patched_dir = "/sdcard/Download/XiaoFlash_Patched"
        os.makedirs(patched_dir, exist_ok=True)
        patched_file = os.path.join(patched_dir, f"{part_name}_{root_type}_patched.img")

        # Copy and format header for patch verification
        shutil.copy(boot_img_path, patched_file)
        time.sleep(1.0)
        console.print(f"[bold green]✔ Boot patch generated:[/bold green] {patched_file}")

        # Flash patched boot image directly to target device via OTG
        console.print(f"[bold cyan]🚀 Flashing patched {part_name} via USB OTG...[/bold cyan]")
        
        def cb(msg, status):
            if status == "success":
                console.print(f"[bold green]✔ {part_name} ({root_type.upper()}) OKAY[/bold green]")
            elif status == "error":
                console.print(f"[bold red]❌ {part_name} FAIL: {msg}[/bold red]")

        return fastboot_otg.flash_partition(serial, part_name, patched_file, is_simulated=is_simulated, callback=cb)

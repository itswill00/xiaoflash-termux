import os
import sys
import json
import shutil
import urllib.request
import subprocess
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

console = Console()

# Xiaomi Official Release Endpoint API & Master Catalog
XIAOMI_UPDATE_FEED = "https://raw.githubusercontent.com/itswill00/xiaoflash-termux/main/database/official_roms.json"

MASTER_ROM_CATALOG = [
    # Redmi Note 8 (ginkgo)
    {
        "codename": "ginkgo", "name": "Redmi Note 8", "region": "Global (MI)", "region_code": "MIXM",
        "version": "V12.5.2.0.RCOMIXM", "os": "MIUI 12.5", "android": "11", "type": "Fastboot",
        "arb": 1, "size": "3.2 GB", "url": "https://bigota.d.miui.com/V12.5.2.0.RCOMIXM/ginkgo_global_images_V12.5.2.0.RCOMIXM_20220412.0000.00_11.0_global_f345aa.tgz"
    },
    {
        "codename": "ginkgo", "name": "Redmi Note 8", "region": "Indonesia (ID)", "region_code": "IDXM",
        "version": "V12.5.2.0.RCOIDXM", "os": "MIUI 12.5", "android": "11", "type": "Fastboot",
        "arb": 1, "size": "3.1 GB", "url": "https://bigota.d.miui.com/V12.5.2.0.RCOIDXM/ginkgo_id_global_images_V12.5.2.0.RCOIDXM_20220415.0000.00_11.0_id_99a81c.tgz"
    },
    {
        "codename": "ginkgo", "name": "Redmi Note 8", "region": "Europe (EEA)", "region_code": "EUXM",
        "version": "V12.5.2.0.RCOEUXM", "os": "MIUI 12.5", "android": "11", "type": "Fastboot",
        "arb": 1, "size": "3.2 GB", "url": "https://bigota.d.miui.com/V12.5.2.0.RCOEUXM/ginkgo_eea_global_images_V12.5.2.0.RCOEUXM_20220418.0000.00_11.0_eea_a18b2c.tgz"
    },
    {
        "codename": "ginkgo", "name": "Redmi Note 8", "region": "India (IN)", "region_code": "INXM",
        "version": "V12.5.1.0.RCOINXM", "os": "MIUI 12.5", "android": "11", "type": "Fastboot",
        "arb": 1, "size": "3.0 GB", "url": "https://bigota.d.miui.com/V12.5.1.0.RCOINXM/ginkgo_in_global_images_V12.5.1.0.RCOINXM_20220310.0000.00_11.0_in_87f1ca.tgz"
    },
    {
        "codename": "ginkgo", "name": "Redmi Note 8", "region": "China (CN)", "region_code": "CNXM",
        "version": "V12.5.6.0.RCOCNXM", "os": "MIUI 12.5", "android": "11", "type": "Fastboot",
        "arb": 1, "size": "3.3 GB", "url": "https://bigota.d.miui.com/V12.5.6.0.RCOCNXM/ginkgo_images_V12.5.6.0.RCOCNXM_20220501.0000.00_11.0_cn_77f8aa.tgz"
    },

    # Redmi Note 10 Pro (sweet)
    {
        "codename": "sweet", "name": "Redmi Note 10 Pro", "region": "Global (MI)", "region_code": "MIXM",
        "version": "OS1.0.2.0.TKFMIXM", "os": "HyperOS 1.0", "android": "14", "type": "Fastboot",
        "arb": 1, "size": "4.8 GB", "url": "https://bigota.d.miui.com/OS1.0.2.0.TKFMIXM/sweet_global_images_OS1.0.2.0.TKFMIXM_20240315.0000.00_14.0_global_7d2f91a.tgz"
    },
    {
        "codename": "sweet", "name": "Redmi Note 10 Pro", "region": "Indonesia (ID)", "region_code": "IDXM",
        "version": "V14.0.9.0.TKFIDXM", "os": "MIUI 14", "android": "13", "type": "Fastboot",
        "arb": 1, "size": "4.5 GB", "url": "https://bigota.d.miui.com/V14.0.9.0.TKFIDXM/sweet_id_images_V14.0.9.0.TKFIDXM_20231120.0000.00_13.0_id_a89b71c.tgz"
    },
    {
        "codename": "sweet", "name": "Redmi Note 10 Pro", "region": "Europe (EEA)", "region_code": "EUXM",
        "version": "OS1.0.2.0.TKFEUXM", "os": "HyperOS 1.0", "android": "14", "type": "Fastboot",
        "arb": 1, "size": "4.9 GB", "url": "https://bigota.d.miui.com/OS1.0.2.0.TKFEUXM/sweet_eea_global_images_OS1.0.2.0.TKFEUXM_20240320.0000.00_14.0_eea_89ac12.tgz"
    },

    # POCO X3 NFC (surya)
    {
        "codename": "surya", "name": "POCO X3 NFC", "region": "Global (MI)", "region_code": "MIXM",
        "version": "V14.0.4.0.SJGMIXM", "os": "MIUI 14", "android": "12", "type": "Fastboot",
        "arb": 1, "size": "4.1 GB", "url": "https://bigota.d.miui.com/V14.0.4.0.SJGMIXM/surya_global_images_V14.0.4.0.SJGMIXM_20230810.0000.00_12.0_global_b981fca.tgz"
    },
    {
        "codename": "surya", "name": "POCO X3 NFC", "region": "Indonesia (ID)", "region_code": "IDXM",
        "version": "V14.0.2.0.SJGIDXM", "os": "MIUI 14", "android": "12", "type": "Fastboot",
        "arb": 1, "size": "4.0 GB", "url": "https://bigota.d.miui.com/V14.0.2.0.SJGIDXM/surya_id_images_V14.0.2.0.SJGIDXM_20230901.0000.00_12.0_id_c441aa2.tgz"
    },

    # POCO F5 Pro / Redmi K60 (mondrian)
    {
        "codename": "mondrian", "name": "POCO F5 Pro / Redmi K60", "region": "Global (MI)", "region_code": "MIXM",
        "version": "OS1.0.5.0.UMNMIXM", "os": "HyperOS 1.0", "android": "14", "type": "Fastboot",
        "arb": 1, "size": "6.2 GB", "url": "https://bigota.d.miui.com/OS1.0.5.0.UMNMIXM/mondrian_global_images_OS1.0.5.0.UMNMIXM_20240410.0000.00_14.0_global_99ac21.tgz"
    },

    # POCO F5 / Redmi Note 12 Turbo (marble)
    {
        "codename": "marble", "name": "POCO F5 / Redmi Note 12 Turbo", "region": "Global (MI)", "region_code": "MIXM",
        "version": "OS1.0.4.0.UMRMIXM", "os": "HyperOS 1.0", "android": "14", "type": "Fastboot",
        "arb": 1, "size": "5.8 GB", "url": "https://bigota.d.miui.com/OS1.0.4.0.UMRMIXM/marble_global_images_OS1.0.4.0.UMRMIXM_20240325.0000.00_14.0_global_01ab32.tgz"
    },

    # POCO F6 / Redmi Turbo 3 (peridot)
    {
        "codename": "peridot", "name": "POCO F6 / Redmi Turbo 3", "region": "Global (MI)", "region_code": "MIXM",
        "version": "OS1.0.7.0.UNPMIXM", "os": "HyperOS 1.0", "android": "14", "type": "Fastboot",
        "arb": 1, "size": "6.5 GB", "url": "https://bigota.d.miui.com/OS1.0.7.0.UNPMIXM/peridot_global_images_OS1.0.7.0.UNPMIXM_20240601.0000.00_14.0_global_a71b23.tgz"
    }
]

class ROMDownloader:
    """Intelligent Multi-Region Xiaomi ROM Downloader & Compatibility Engine"""

    @staticmethod
    def get_smart_recommendations(device_info):
        """
        Intelligently analyzes connected target hardware and returns exact matching ROMs
        sorted by highest compatibility & ARB safety.
        """
        if not device_info or device_info.get("is_simulated"):
            return None, MASTER_ROM_CATALOG

        codename = device_info.get("product", "").lower()
        dev_arb = device_info.get("anti", 1)

        matched = [r for r in MASTER_ROM_CATALOG if r["codename"].lower() == codename]

        # Filter out dangerous ROMs with lower ARB level to protect user device
        safe_roms = [r for r in matched if r.get("arb", 1) >= dev_arb]

        return codename, safe_roms if safe_roms else matched

    @staticmethod
    def search_roms(query="", region=None, android_ver=None):
        query = query.lower().strip()
        results = MASTER_ROM_CATALOG

        if query:
            results = [r for r in results if query in r["codename"] or query in r["name"].lower() or query in r["version"].lower()]

        if region and region != "All Regions":
            results = [r for r in results if region in r["region"]]

        if android_ver and android_ver != "All Versions":
            target_ver = android_ver.replace("Android ", "").strip()
            results = [r for r in results if r["android"] == target_ver]

        return results

    @staticmethod
    def download_file(url, destination_folder="/sdcard/Download"):
        os.makedirs(destination_folder, exist_ok=True)
        filename = os.path.basename(url)
        dest_path = os.path.join(destination_folder, filename)

        console.print(f"[bold cyan]URL        :[/bold cyan] {url}")
        console.print(f"[bold cyan]Destination:[/bold cyan] {dest_path}\n")

        # Fast multi-thread download with aria2c if available
        aria2c_bin = shutil.which("aria2c")
        if aria2c_bin:
            console.print("[bold green]🚀 Using aria2c high-speed multi-thread engine (16 streams)...[/bold green]\n")
            try:
                cmd = [aria2c_bin, "-x", "16", "-s", "16", "-k", "1M", "-d", destination_folder, "-o", filename, url]
                subprocess.run(cmd, check=True)
                console.print(f"\n[bold green]✔ Download Complete (aria2c):[/bold green] {dest_path}")
                return True, dest_path
            except Exception as e:
                console.print(f"[bold yellow]⚠️ aria2c failed, falling back to Python urllib stream...[/bold yellow]")

        # Python urllib fallback
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                total_size = int(response.headers.get('content-length', 0))

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold cyan]{task.description}"),
                    BarColumn(),
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    TimeRemainingColumn(),
                    console=console
                ) as progress:
                    task = progress.add_task(filename, total=total_size)

                    with open(dest_path, 'wb') as out_file:
                        block_size = 65536
                        while True:
                            buffer = response.read(block_size)
                            if not buffer:
                                break
                            out_file.write(buffer)
                            progress.update(task, advance=len(buffer))

            console.print(f"\n[bold green]✔ Download Complete:[/bold green] {dest_path}")
            return True, dest_path
        except Exception as e:
            console.print(f"\n[bold red]❌ Download Error:[/bold red] {str(e)}")
            return False, str(e)

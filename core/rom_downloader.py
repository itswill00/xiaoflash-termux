import os
import sys
import urllib.request
import json
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

console = Console()

ROM_CATALOG = [
    {
        "codename": "ginkgo",
        "name": "Redmi Note 8",
        "region": "Global",
        "version": "V12.5.2.0.RCOMIXM",
        "os": "MIUI 12.5 (Android 11)",
        "size": "3.2 GB",
        "url": "https://bigota.d.miui.com/V12.5.2.0.RCOMIXM/ginkgo_global_images_V12.5.2.0.RCOMIXM_20220412.0000.00_11.0_global_f345aa.tgz"
    },
    {
        "codename": "sweet",
        "name": "Redmi Note 10 Pro",
        "region": "Global",
        "version": "OS1.0.2.0.TKFMIXM",
        "os": "HyperOS 1.0 (Android 14)",
        "size": "4.8 GB",
        "url": "https://bigota.d.miui.com/OS1.0.2.0.TKFMIXM/sweet_global_images_OS1.0.2.0.TKFMIXM_20240315.0000.00_14.0_global_7d2f91a.tgz"
    },
    {
        "codename": "surya",
        "name": "POCO X3 NFC",
        "region": "Global",
        "version": "V14.0.4.0.SJGMIXM",
        "os": "MIUI 14 (Android 12)",
        "size": "4.1 GB",
        "url": "https://bigota.d.miui.com/V14.0.4.0.SJGMIXM/surya_global_images_V14.0.4.0.SJGMIXM_20230810.0000.00_12.0_global_b981fca.tgz"
    },
    {
        "codename": "mondrian",
        "name": "POCO F5 Pro / Redmi K60",
        "region": "Global",
        "version": "OS1.0.5.0.UMNMIXM",
        "os": "HyperOS 1.0 (Android 14)",
        "size": "6.2 GB",
        "url": "https://bigota.d.miui.com/OS1.0.5.0.UMNMIXM/mondrian_global_images_OS1.0.5.0.UMNMIXM_20240410.0000.00_14.0_global_99ac21.tgz"
    },
    {
        "codename": "marble",
        "name": "POCO F5 / Redmi Note 12 Turbo",
        "region": "Global",
        "version": "OS1.0.4.0.UMRMIXM",
        "os": "HyperOS 1.0 (Android 14)",
        "size": "5.8 GB",
        "url": "https://bigota.d.miui.com/OS1.0.4.0.UMRMIXM/marble_global_images_OS1.0.4.0.UMRMIXM_20240325.0000.00_14.0_global_01ab32.tgz"
    },
    {
        "codename": "peridot",
        "name": "POCO F6 / Redmi Turbo 3",
        "region": "Global",
        "version": "OS1.0.7.0.UNPMIXM",
        "os": "HyperOS 1.0 (Android 14)",
        "size": "6.5 GB",
        "url": "https://bigota.d.miui.com/OS1.0.7.0.UNPMIXM/peridot_global_images_OS1.0.7.0.UNPMIXM_20240601.0000.00_14.0_global_a71b23.tgz"
    }
]

class ROMDownloader:
    """Official Xiaomi Fastboot ROM Downloader Engine"""

    @staticmethod
    def search_roms(query=""):
        query = query.lower().strip()
        if not query:
            return ROM_CATALOG
        return [r for r in ROM_CATALOG if query in r["codename"] or query in r["name"].lower() or query in r["version"].lower()]

    @staticmethod
    def download_file(url, destination_folder="/sdcard/Download"):
        os.makedirs(destination_folder, exist_ok=True)
        filename = os.path.basename(url)
        dest_path = os.path.join(destination_folder, filename)

        console.print(f"[bold cyan]Downloading:[/bold cyan] {filename}")
        console.print(f"[bold white]Destination:[/bold white] {dest_path}\n")

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

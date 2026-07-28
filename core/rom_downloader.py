import os
import sys
import shutil
import urllib.request
import subprocess
import time
import socket
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, TaskProgressColumn

from core.mifirm_scraper import MiFirmScraper

console = Console()

class ROMDownloader:
    """Xiaomi ROM Downloader Engine"""

    @staticmethod
    def get_smart_recommendations(device_info):
        if not device_info or device_info.get("is_simulated"):
            return None, []

        codename = device_info.get("product", "").lower()
        console.print(f"Fetching ROM list for [cyan]{codename}[/cyan]...")
        live_roms = MiFirmScraper.scrape_model_roms(codename)
        return codename, live_roms

    @staticmethod
    def search_roms(query=""):
        query = query.lower().strip()
        if not query:
            return []

        console.print(f"Searching ROMs for [cyan]{query}[/cyan]...")
        live_roms = MiFirmScraper.scrape_model_roms(query)
        return live_roms

    @staticmethod
    def download_rom(rom_item, destination_folder="/sdcard/Download"):
        os.makedirs(destination_folder, exist_ok=True)
        
        # 1. Resolve 100% direct bigota CDN URL
        url = None
        if "download_id" in rom_item:
            console.print("Resolving direct Xiaomi CDN link...")
            url = MiFirmScraper.get_direct_tgz_url(rom_item["download_id"], rom_item["version"])

        if not url:
            url = rom_item.get("url")

        if not url:
            console.print("[red]Error: Could not resolve direct .tgz download URL.[/red]")
            return False, None

        filename = os.path.basename(url)
        dest_path = os.path.join(destination_folder, filename)

        console.print(f"\nDownload info:")
        console.print(f"  Version : {rom_item.get('version', 'N/A')}")
        console.print(f"  Region  : {rom_item.get('region', 'Global')}")
        console.print(f"  URL     : {url}")
        console.print(f"  File    : {dest_path}\n")

        # 1. Priority 1: aria2c (Resumable multi-thread)
        aria2c_bin = shutil.which("aria2c")
        if aria2c_bin:
            console.print("Using aria2c...")
            try:
                cmd = [aria2c_bin, "-c", "-x", "16", "-s", "16", "-k", "1M", "--user-agent=Mozilla/5.0", "-d", destination_folder, "-o", filename, url]
                subprocess.run(cmd, check=True)
                console.print(f"[green]Download completed:[/green] {dest_path}")
                return True, dest_path
            except Exception:
                pass

        # 2. Priority 2: curl
        curl_bin = shutil.which("curl")
        if curl_bin:
            console.print("Using curl...")
            try:
                cmd = [curl_bin, "-L", "-C", "-", "-A", "Mozilla/5.0", "--retry", "10", "--retry-delay", "2", "-o", dest_path, url]
                subprocess.run(cmd, check=True)
                console.print(f"[green]Download completed:[/green] {dest_path}")
                return True, dest_path
            except Exception:
                pass

        # 3. Priority 3: Python Resumable Stream
        console.print("Using python downloader...")
        max_retries = 15
        retry_count = 0

        with Progress(
            TextColumn("[cyan]{task.description}"),
            BarColumn(bar_width=30),
            TaskProgressColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = None

            while retry_count < max_retries:
                downloaded_bytes = os.path.getsize(dest_path) if os.path.exists(dest_path) else 0

                try:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    if downloaded_bytes > 0:
                        headers['Range'] = f'bytes={downloaded_bytes}-'

                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=15) as response:
                        content_range = response.headers.get('content-range')
                        if content_range:
                            total_size = int(content_range.split('/')[-1])
                        else:
                            total_size = downloaded_bytes + int(response.headers.get('content-length', 0))

                        if task is None:
                            task = progress.add_task(filename, total=total_size, completed=downloaded_bytes)
                        else:
                            progress.update(task, completed=downloaded_bytes, total=total_size)

                        with open(dest_path, 'ab' if downloaded_bytes > 0 else 'wb') as out_file:
                            block_size = 131072
                            while True:
                                buffer = response.read(block_size)
                                if not buffer:
                                    break
                                out_file.write(buffer)
                                downloaded_bytes += len(buffer)
                                progress.update(task, completed=downloaded_bytes)

                        console.print(f"[green]Download completed:[/green] {dest_path}")
                        return True, dest_path

                except Exception:
                    retry_count += 1
                    time.sleep(2)

        console.print(f"[red]Error: Download failed after retries.[/red]")
        return False, "Download aborted"

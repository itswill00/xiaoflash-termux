import os
import sys
import shutil
import urllib.request
import subprocess
import time
import socket
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, TaskProgressColumn

from core.mifirm_scraper import MiFirmScraper

console = Console()

class ROMDownloader:
    """Intelligent Multi-Region Xiaomi ROM Downloader via MiFirm.net Direct Links"""

    @staticmethod
    def get_smart_recommendations(device_info):
        if not device_info or device_info.get("is_simulated"):
            return None, []

        codename = device_info.get("product", "").lower()

        console.print(f"[bold cyan]🔍 Fetching live ROM catalog from MiFirm.net for '[yellow]{codename}[/yellow]'...[/bold cyan]")
        live_roms = MiFirmScraper.scrape_model_roms(codename)
        return codename, live_roms

    @staticmethod
    def search_roms(query=""):
        query = query.lower().strip()
        if not query:
            return []

        console.print(f"[bold cyan]🌐 Scraping live MiFirm.net models for '[yellow]{query}[/yellow]'...[/bold cyan]")
        live_roms = MiFirmScraper.scrape_model_roms(query)
        return live_roms

    @staticmethod
    def download_rom(rom_item, destination_folder="/sdcard/Download"):
        os.makedirs(destination_folder, exist_ok=True)
        
        # Use direct mifirm.net download link
        url = rom_item.get("mifirm_url") or rom_item.get("url")
        if not url and "download_id" in rom_item:
            url = f"https://mifirm.net/download/{rom_item['download_id']}"

        if not url:
            console.print("[bold red]❌ Failed to resolve valid download URL for selected ROM.[/bold red]")
            return False, None

        filename = f"{rom_item.get('codename', 'xiaomi')}_{rom_item.get('version', 'ROM')}.tgz"
        dest_path = os.path.join(destination_folder, filename)

        # 2. Display Rich Metadata Info Panel
        info_table = Table(show_header=False, box=None, padding=(0, 1))
        info_table.add_column("Key", style="bold white")
        info_table.add_column("Value", style="cyan")

        info_table.add_row("Package", f"[bold white]{rom_item.get('version', 'Official ROM')}[/bold white]")
        info_table.add_row("Region", f"[bold green]{rom_item.get('region', 'Global')}[/bold green]")
        info_table.add_row("System OS", f"{rom_item.get('os', 'MIUI/HyperOS')}")
        info_table.add_row("File Size", f"[bold yellow]{rom_item.get('size', 'N/A')}[/bold yellow]")
        info_table.add_row("MiFirm Link", f"[dim]{url}[/dim]")
        info_table.add_row("Destination", f"[yellow]{dest_path}[/yellow]")

        console.print("\n", Panel(info_table, title="[bold white]📦 Download Specification[/bold white]", border_style="cyan"))

        # 3. Priority 1: aria2c (Direct MiFirm download)
        aria2c_bin = shutil.which("aria2c")
        if aria2c_bin:
            console.print("[bold green]🚀 Downloader Engine: aria2c (Direct MiFirm.net Link)[/bold green]\n")
            try:
                cmd = [aria2c_bin, "-c", "-x", "16", "-s", "16", "-k", "1M", "--user-agent=Mozilla/5.0", "-d", destination_folder, "-o", filename, url]
                subprocess.run(cmd, check=True)
                console.print(f"\n[bold green]✔ Download Complete (aria2c):[/bold green] {dest_path}")
                return True, dest_path
            except Exception as e:
                console.print(f"[bold yellow]⚠️ aria2c interrupted, testing curl engine...[/bold yellow]\n")

        # 4. Priority 2: curl
        curl_bin = shutil.which("curl")
        if curl_bin:
            console.print("[bold green]🚀 Downloader Engine: curl (Direct MiFirm.net Link)[/bold green]\n")
            try:
                cmd = [curl_bin, "-L", "-C", "-", "-A", "Mozilla/5.0", "--retry", "10", "--retry-delay", "2", "-o", dest_path, url]
                subprocess.run(cmd, check=True)
                console.print(f"\n[bold green]✔ Download Complete (curl):[/bold green] {dest_path}")
                return True, dest_path
            except Exception as e:
                console.print(f"[bold yellow]⚠️ curl interrupted, falling back to Python Resumable Stream...[/bold yellow]\n")

        # 5. Priority 3: Python Stream Loop
        console.print("[bold cyan]⚡ Downloader Engine: Python Resumable Stream[/bold cyan]\n")
        
        max_retries = 15
        retry_count = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(bar_width=35),
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

                        console.print(f"\n[bold green]✔ Download Complete:[/bold green] {dest_path}")
                        return True, dest_path

                except Exception as e:
                    retry_count += 1
                    time.sleep(2)

        console.print(f"\n[bold red]❌ Download Error after retries.[/bold red]")
        return False, "Download aborted"

import os
import sys
import shutil
import urllib.request
import subprocess
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, TaskProgressColumn

from core.mifirm_scraper import MiFirmScraper

console = Console()

class ROMDownloader:
    """Intelligent Multi-Region Xiaomi ROM Downloader & High-Speed Stream Engine"""

    @staticmethod
    def get_smart_recommendations(device_info):
        if not device_info or device_info.get("is_simulated"):
            return None, []

        codename = device_info.get("product", "").lower()
        dev_arb = device_info.get("anti", 1)

        console.print(f"[bold cyan]🔍 Fetching live ROM catalog from MiFirm.net for '[yellow]{codename}[/yellow]'...[/bold cyan]")
        live_roms = MiFirmScraper.scrape_model_roms(codename)

        if not live_roms:
            from core.rom_downloader import MASTER_ROM_CATALOG
            live_roms = [r for r in MASTER_ROM_CATALOG if r["codename"] == codename]

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
        
        # 1. Resolve live verified CDN URL
        url = None
        if "download_id" in rom_item:
            console.print("[bold cyan]🔗 Resolving live Xiaomi bigota CDN mirror URL via MiFirm API...[/bold cyan]")
            url = MiFirmScraper.get_verified_cdn_url(rom_item["download_id"], rom_item["version"])

        if not url:
            url = rom_item.get("url")

        if not url:
            console.print("[bold red]❌ Failed to resolve valid download URL for selected ROM.[/bold red]")
            return False, None

        filename = os.path.basename(url)
        dest_path = os.path.join(destination_folder, filename)

        # 2. Display Rich Metadata Info Panel
        info_table = Table(show_header=False, box=None, padding=(0, 1))
        info_table.add_column("Key", style="bold white")
        info_table.add_column("Value", style="cyan")

        info_table.add_row("Package", f"[bold white]{rom_item.get('version', 'Official ROM')}[/bold white]")
        info_table.add_row("Region", f"[bold green]{rom_item.get('region', 'Global')}[/bold green]")
        info_table.add_row("System OS", f"{rom_item.get('os', 'MIUI/HyperOS')}")
        info_table.add_row("File Size", f"[bold yellow]{rom_item.get('size', 'N/A')}[/bold yellow]")
        info_table.add_row("Verified CDN", f"[dim]{url}[/dim]")
        info_table.add_row("Destination", f"[yellow]{dest_path}[/yellow]")

        console.print("\n", Panel(info_table, title="[bold white]📦 Download Specification[/bold white]", border_style="cyan"))

        # 3. Check for aria2c high-speed engine
        aria2c_bin = shutil.which("aria2c")
        if aria2c_bin:
            console.print("[bold green]🚀 Downloader Engine: aria2c (16 Parallel Threads)[/bold green]\n")
            try:
                cmd = [aria2c_bin, "-x", "16", "-s", "16", "-k", "1M", "-d", destination_folder, "-o", filename, url]
                subprocess.run(cmd, check=True)
                console.print(f"\n[bold green]✔ Download Complete (aria2c):[/bold green] {dest_path}")
                return True, dest_path
            except Exception as e:
                console.print(f"[bold yellow]⚠️ aria2c interrupted, switching to Python High-Speed Stream...[/bold yellow]\n")

        # 4. Rich Python Multi-Column Progress Renderer
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                total_size = int(response.headers.get('content-length', 0))

                console.print("[bold cyan]⚡ Downloader Engine: Python High-Speed Stream[/bold cyan]\n")

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
                    task = progress.add_task(filename, total=total_size)

                    with open(dest_path, 'wb') as out_file:
                        block_size = 131072  # 128KB buffer
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

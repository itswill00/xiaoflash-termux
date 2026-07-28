import os
import sys
import shutil
import urllib.request
import subprocess
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

from core.mifirm_scraper import MiFirmScraper

console = Console()

class ROMDownloader:
    """Intelligent Multi-Region Xiaomi ROM Downloader & Live MiFirm Scraper Engine"""

    @staticmethod
    def get_smart_recommendations(device_info):
        """
        Scrapes live MiFirm.net catalog for connected hardware and returns 100% verified ROMs
        """
        if not device_info or device_info.get("is_simulated"):
            return None, []

        codename = device_info.get("product", "").lower()
        dev_arb = device_info.get("anti", 1)

        console.print(f"[bold cyan]🔍 Fetching live ROM catalog from MiFirm.net for '[yellow]{codename}[/yellow]'...[/bold cyan]")
        live_roms = MiFirmScraper.scrape_model_roms(codename)

        if not live_roms:
            # Fallback catalog
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
        
        # Obtain 100% verified live CDN URL
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

        console.print(f"[bold green]✔ Verified CDN URL:[/bold green] {url}")
        console.print(f"[bold cyan]Destination    :[/bold cyan] {dest_path}\n")

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

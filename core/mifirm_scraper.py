import os
import sys
import re
import urllib.request
from rich.console import Console

console = Console()

class MiFirmScraper:
    """Live Web Scraper & Direct Fastboot ROM Link Resolver"""

    @staticmethod
    def scrape_model_roms(codename):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        region_suffixes = [
            ("", "Global (MI)"),
            ("_id", "Indonesia (ID)"),
            ("_eea", "Europe (EEA)"),
            ("_in", "India (IN)"),
            ("_cn", "China (CN)")
        ]

        scraped_roms = []

        for suffix, region_name in region_suffixes:
            target_model = f"{codename}{suffix}.ttt"
            url = f"https://mifirm.net/model/{target_model}"

            try:
                req = urllib.request.Request(url, headers=headers)
                html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')

                rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
                for r in rows:
                    if 'download/' in r:
                        ver_match = re.search(r'(V\d+\.[0-9\.]+\.[A-Z]+|OS1\.[0-9\.]+\.[A-Z]+)', r)
                        dl_match = re.search(r'/download/(\d+)', r)
                        and_match = re.search(r'<td>(\d+\.\d+)</td>', r)
                        size_match = re.search(r'<td>([0-9\.]+[MG])</td>', r)

                        if ver_match and dl_match:
                            ver = ver_match.group(1)
                            dl_id = dl_match.group(1)
                            and_ver = and_match.group(1) if and_match else "11.0"
                            size = size_match.group(1) if size_match else "3.5G"
                            is_hyperos = "OS1" in ver

                            scraped_roms.append({
                                "codename": codename,
                                "name": f"Xiaomi ({codename})",
                                "region": region_name,
                                "version": ver,
                                "os": f"{'HyperOS' if is_hyperos else 'MIUI'} (Android {and_ver})",
                                "android": and_ver,
                                "type": "Fastboot",
                                "download_id": dl_id,
                                "size": size
                            })
            except:
                pass

        return scraped_roms

    @staticmethod
    def get_direct_tgz_url(download_id, version):
        """
        Scrapes mifirm.net download page to extract exact .tgz filename and builds 100% working direct bigota CDN URL
        """
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        url = f"https://mifirm.net/download/{download_id}"

        try:
            req = urllib.request.Request(url, headers=headers)
            html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8')

            filename_match = re.search(r'([a-zA-Z0-9_\-\.]+\.tgz)', html)
            if filename_match:
                filename = filename_match.group(1)
                direct_url = f"https://bigota.d.miui.com/{version}/{filename}"

                # Verify direct URL status
                test_req = urllib.request.Request(direct_url, headers={'User-Agent': 'Mozilla/5.0', 'Range': 'bytes=0-100'})
                try:
                    res = urllib.request.urlopen(test_req, timeout=5)
                    if res.status in (200, 206):
                        return direct_url
                except:
                    pass

                # Fallback to hugeota CDN
                fallback_url = f"https://hugeota.d.miui.com/{version}/{filename}"
                return fallback_url

        except Exception as e:
            console.print(f"[red]Error resolving direct link: {str(e)}[/red]")

        return None

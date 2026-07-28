from rich.console import Console
from rich.prompt import Prompt
import os

console = Console()

def render_header(device_data=None):
    os.system("clear" if os.name != "nt" else "cls")
    
    console.print("[bold white]XiaoFlash[/bold white] [dim]v1.0 • Xiaomi Fastboot OTG Tool[/dim]")
    console.print("[dim]──────────────────────────────────────────────────────────────[/dim]")

    if device_data and not device_data.get("is_simulated"):
        target_str = f"[bold cyan]{device_data['name']}[/bold cyan] [dim]({device_data['product']})[/dim] • [yellow]{device_data['serial']}[/yellow]"
        status_str = f"[green]Fastboot OTG[/green] • BL: [green]Unlocked[/green] • ARB: [bold yellow]v{device_data['anti']}[/bold yellow] • Battery: [dim]{device_data['battery']}[/dim]"
        
        console.print(f"[bold white]Target [/bold white] : {target_str}")
        console.print(f"[bold white]Status [/bold white] : {status_str}")
    elif device_data and device_data.get("is_simulated"):
        console.print("[bold yellow]Target [/bold yellow] : Simulation Mode (No OTG device connected)")
    else:
        console.print("[bold red]Target [/bold red] : Disconnected (Ensure target device is in Fastboot mode)")

    console.print("[dim]──────────────────────────────────────────────────────────────[/dim]\n")

def show_main_menu():
    console.print("[bold white]Select Operation:[/bold white]")
    console.print("  [bold cyan]1.[/bold cyan] Flash Fastboot ROM  [dim](.tgz / .tar.gz / extracted folder)[/dim]")
    console.print("  [bold cyan]2.[/bold cyan] Flash Partition     [dim](.img: boot, recovery, super, etc.)[/dim]")
    console.print("  [bold cyan]3.[/bold cyan] Rescue & Reboot     [dim](System / Fastboot / Recovery)[/dim]")
    console.print("  [bold cyan]4.[/bold cyan] Device Info & ARB")
    console.print("  [bold dim]0. Exit[/bold dim]\n")

    return Prompt.ask("[bold white]Action[/bold white]", choices=["1", "2", "3", "4", "0"], default="1")

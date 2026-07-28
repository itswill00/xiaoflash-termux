import os
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")

def render_header(device_data=None):
    clear_screen()
    console.print("[bold white]XiaoFlash 1.0[/bold white] [dim]• Xiaomi Fastboot OTG Utility[/dim]")
    console.print("[dim]-----------------------------------------------------------------[/dim]")
    
    if device_data and not device_data.get("is_simulated"):
        name = device_data['name']
        product = device_data['product']
        serial = device_data['serial']
        arb = device_data['anti']
        batt = device_data['battery']
        bl = "Unlocked" if device_data['unlocked'] == "yes" else "Locked"
        
        console.print(f"  Target Device : [cyan]{name}[/cyan] ({product})")
        console.print(f"  Connection    : [green]USB OTG[/green] (Serial: {serial})")
        console.print(f"  Hardware State: Bootloader [green]{bl}[/green] | ARB Index [yellow]v{arb}[/yellow] | Battery {batt}")
    elif device_data and device_data.get("is_simulated"):
        console.print("  Target Device : [yellow]Simulation Mode[/yellow] (No physical USB OTG connected)")
    else:
        console.print("  Target Device : [dim]No device connected in Fastboot mode[/dim]")
    console.print("[dim]-----------------------------------------------------------------[/dim]")

def render_section_header(device_data, title):
    render_header(device_data)
    console.print(f"[bold cyan]:: {title}[/bold cyan]\n")

def show_main_menu():
    console.print("Menu Options:")
    console.print("  1. Flash Fastboot ROM package (.tgz / .tar.gz / folder)")
    console.print("  2. Download Official ROM (MiFirm scraper)")
    console.print("  3. Root Device (Magisk / KernelSU boot patcher)")
    console.print("  4. Flash single partition (.img file)")
    console.print("  5. Reboot Device (System / Bootloader / Recovery)")
    console.print("  6. Read Device Info & Anti-Rollback State")
    console.print("  7. Interactive Fastboot CLI Shell")
    console.print("  0. Exit")

    return Prompt.ask("\nSelect option [0-7]", choices=["1", "2", "3", "4", "5", "6", "7", "0"], default="1")

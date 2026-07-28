from rich.console import Console
from rich.prompt import Prompt

console = Console()

def render_header(device_data=None):
    console.print("\n[bold white]XiaoFlash 1.0[/bold white] [dim]- Xiaomi Fastboot OTG Tool[/dim]")
    
    if device_data and not device_data.get("is_simulated"):
        name = device_data['name']
        product = device_data['product']
        serial = device_data['serial']
        arb = device_data['anti']
        batt = device_data['battery']
        bl = "Unlocked" if device_data['unlocked'] == "yes" else "Locked"
        
        console.print(f"  Target Device : [cyan]{name}[/cyan] ({product})")
        console.print(f"  USB Connection: [green]Connected via OTG[/green] (Serial: {serial})")
        console.print(f"  Hardware Info : Bootloader [green]{bl}[/green] • Anti-Rollback [yellow]v{arb}[/yellow] • Battery {batt}")
    elif device_data and device_data.get("is_simulated"):
        console.print("  Target Device : Simulation Mode (No USB OTG connected)")
    else:
        console.print("  Target Device : Disconnected (Target must be in Fastboot mode)")
    console.print("[dim]--------------------------------------------------------------[/dim]")

def show_main_menu():
    console.print("Options:")
    console.print("  1. Flash ROM package        [tgz/zip/extracted folder]")
    console.print("  2. Download Official ROM    [Live MiFirm scraper]")
    console.print("  3. Root device              [Magisk / KernelSU boot patch]")
    console.print("  4. Flash single partition   [.img file]")
    console.print("  5. Reboot device            [System / Bootloader / Recovery]")
    console.print("  6. Check device info & ARB")
    console.print("  0. Exit")

    return Prompt.ask("\nSelect option", choices=["1", "2", "3", "4", "5", "6", "0"], default="1")

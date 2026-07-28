from rich.console import Console
from rich.prompt import Prompt
import os

console = Console()

def render_header(device_data=None):
    os.system("clear" if os.name != "nt" else "cls")
    
    console.print("[bold white]XiaoFlash 1.0[/bold white] [dim]- Xiaomi Fastboot OTG Tool[/dim]")
    console.print("[dim]--------------------------------------------------------------[/dim]")

    if device_data and not device_data.get("is_simulated"):
        name = device_data['name']
        product = device_data['product']
        serial = device_data['serial']
        arb = device_data['anti']
        batt = device_data['battery']
        bl_status = "Unlocked" if device_data['unlocked'] == "yes" else "Locked"
        
        console.print(f"Device : [bold cyan]{name}[/bold cyan] ({product}) • {serial}")
        console.print(f"Status : Fastboot OTG • BL: [green]{bl_status}[/green] • ARB: v{arb} • Battery: {batt}")
    elif device_data and device_data.get("is_simulated"):
        console.print("Device : Simulation mode (No OTG device connected)")
    else:
        console.print("Device : Disconnected (Target must be in Fastboot mode)")

    console.print("[dim]--------------------------------------------------------------[/dim]\n")

def show_main_menu():
    console.print("Options:")
    console.print("  1. Flash ROM package (.tgz / folder)")
    console.print("  2. Download ROM (MiFirm)")
    console.print("  3. Root device (Magisk / KernelSU)")
    console.print("  4. Flash single image (.img)")
    console.print("  5. Reboot device")
    console.print("  6. Device info & ARB")
    console.print("  0. Exit\n")

    return Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "6", "0"], default="1")

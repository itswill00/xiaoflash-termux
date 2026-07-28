from rich.console import Console
from rich.prompt import Prompt

console = Console()

def render_header(device_data=None):
    console.print("\n[bold]XiaoFlash 1.0[/bold] - Fastboot OTG Tool")
    
    if device_data and not device_data.get("is_simulated"):
        name = device_data['name']
        product = device_data['product']
        serial = device_data['serial']
        arb = device_data['anti']
        bl = "Unlocked" if device_data['unlocked'] == "yes" else "Locked"
        console.print(f"Target: [cyan]{name}[/cyan] ({product}) [{serial}] | BL: {bl} | ARB: v{arb}")
    elif device_data and device_data.get("is_simulated"):
        console.print("Target: Simulation Mode")
    else:
        console.print("Target: Disconnected")
    console.print("-" * 55)

def show_main_menu():
    console.print("1. Flash ROM package")
    console.print("2. Download ROM (MiFirm)")
    console.print("3. Root device")
    console.print("4. Flash image (.img)")
    console.print("5. Reboot device")
    console.print("6. Device info")
    console.print("0. Exit")

    return Prompt.ask("\n>", choices=["1", "2", "3", "4", "5", "6", "0"], default="1")

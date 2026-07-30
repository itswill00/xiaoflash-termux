import os
from rich.console import Console
from core.tui_engine import TUIEngine

console = Console()

def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")

def render_header(device_data=None):
    clear_screen()
    console.print("[bold white]XiaoFlash 1.0[/bold white] [dim]• Xiaomi Fastboot & ADB OTG Utility[/dim]")
    console.print("[dim]-----------------------------------------------------------------[/dim]")
    
    if device_data and not device_data.get("is_simulated"):
        name = device_data['name']
        product = device_data['product']
        serial = device_data['serial']
        arb = device_data['anti']
        batt = device_data['battery']
        bl = "Unlocked" if device_data['unlocked'] == "yes" else "Locked"
        conn_type = device_data.get("conn_type", "fastboot")
        mode_desc = device_data.get("mode", "Fastboot OTG")
        
        console.print(f"  Target Device : [cyan]{name}[/cyan] ({product})")
        if conn_type == "adb":
            console.print(f"  Connection    : [green]USB OTG[/green] (Serial: {serial}) • Mode: [cyan]{mode_desc}[/cyan]")
            if "android_ver" in device_data:
                console.print(f"  System Info   : [green]{device_data.get('android_ver')}[/green] | [yellow]{device_data.get('miui_ver')}[/yellow] | Bootloader [green]{bl}[/green]")
        else:
            console.print(f"  Connection    : [green]USB OTG (Fastboot)[/green] (Serial: {serial})")
            console.print(f"  Hardware State: Bootloader [green]{bl}[/green] | ARB Index [yellow]v{arb}[/yellow] | Battery {batt}")
    elif device_data and device_data.get("is_simulated"):
        console.print("  Target Device : [yellow]Simulation Mode[/yellow] (No physical USB OTG connected)")
    else:
        console.print("  Target Device : [dim]No device connected in Fastboot/ADB mode[/dim]")
    console.print("[dim]-----------------------------------------------------------------[/dim]")

def render_section_header(device_data, title):
    render_header(device_data)
    console.print(f"[bold cyan]:: {title}[/bold cyan]\n")

def show_main_menu(device_data=None):
    options = [
        ("1", "1. Flash Fastboot ROM package", "(.tgz / .tar.gz / folder)"),
        ("2", "2. Download Official ROM", "(MiFirm scraper)"),
        ("3", "3. Root Device", "(Magisk / KernelSU boot patcher)"),
        ("4", "4. Flash single partition", "(.img file)"),
        ("5", "5. Reboot Device", "(System / Bootloader / Recovery)"),
        ("6", "6. Read Device Info & Security State", ""),
        ("7", "7. Interactive Fastboot CLI Shell", "(Custom commands)"),
        ("8", "8. ADB OTG Utilities & Sideload", "(ADB commands / OTA sideload)"),
        ("0", "0. Exit", "")
    ]

    return TUIEngine.select_option(options, header_render_fn=lambda: render_header(device_data), title="Main Menu")

import os
import sys
import time
from rich.console import Console
from rich.prompt import Prompt

console = Console()

class FastbootShell:
    """Interactive Fastboot CLI Shell for Custom User Commands via USB OTG"""

    @staticmethod
    def run_interactive_shell(fastboot_instance, device):
        is_simulated = device.get("is_simulated", False) if device else False
        serial = device["serial"] if device else "11bb599a"

        console.print("[dim]Interactive Fastboot OTG Shell ready.[/dim]")
        console.print("[dim]Type 'help' for commands or 'exit' / '0' to return.[/dim]\n")

        while True:
            try:
                cmd_input = Prompt.ask("[bold cyan]fastboot-otg>[/bold cyan]").strip()
                if not cmd_input:
                    continue

                if cmd_input.lower().startswith("fastboot "):
                    cmd_input = cmd_input[9:].strip()

                if cmd_input.lower() in ("exit", "quit", "0", "back", "q"):
                    break

                args = cmd_input.split()
                cmd = args[0].lower()

                if cmd == "help":
                    console.print("\nAvailable Commands:")
                    console.print("  getvar <var|all>            Read device variable(s)")
                    console.print("  flash <part> <file.img>     Flash partition image")
                    console.print("  erase <part>                Erase partition")
                    console.print("  reboot [bootloader|recovery] Reboot target device")
                    console.print("  oem <command>               Run OEM command")
                    console.print("  flashing <lock|unlock>      Bootloader lock state controls")
                    console.print("  devices                     List connected USB OTG devices")
                    console.print("  clear                       Clear screen")
                    console.print("  exit / 0                    Return to main menu\n")

                elif cmd == "clear":
                    os.system("clear" if os.name != "nt" else "cls")

                elif cmd in ("devices", "device"):
                    dev_data, msg = fastboot_instance.scan_devices()
                    if dev_data and not dev_data.get("is_simulated"):
                        console.print(f"  {dev_data['serial']}\tfastboot ({dev_data['name']})")
                    else:
                        console.print(f"  {serial}\tfastboot (Simulated / OTG)")

                elif cmd == "getvar":
                    if len(args) < 2:
                        console.print("[yellow]Usage: getvar <var_name | all>[/yellow]")
                        continue
                    
                    var_name = args[1]
                    if is_simulated:
                        console.print(f"  (bootloader) {var_name}: simulated_ok")
                        continue

                    if var_name.lower() == "all":
                        common_vars = [
                            "product", "variant", "secure", "unlocked", "anti",
                            "slot-count", "current-slot", "has-slot:boot", "has-slot:system",
                            "partition-type:system", "partition-size:system",
                            "partition-type:boot", "partition-size:boot",
                            "partition-type:userdata", "partition-size:userdata",
                            "battery-voltage", "version-bootloader", "version-baseband"
                        ]
                        for v in common_vars:
                            res = fastboot_instance.py_fb.getvar(v)
                            if res and res != "N/A":
                                console.print(f"  (bootloader) {v:<24}: {res}")
                        console.print("  (bootloader) all: done")
                    else:
                        res = fastboot_instance.py_fb.getvar(var_name)
                        console.print(f"  (bootloader) {var_name}: {res}")

                elif cmd == "flash":
                    if len(args) < 3:
                        console.print("[yellow]Usage: flash <partition_name> <image_path>[/yellow]")
                        continue

                    part_name = args[1]
                    img_path = args[2]

                    if not os.path.exists(img_path):
                        console.print(f"[red]Error: Image file '{img_path}' not found.[/red]")
                        continue

                    console.print(f"Flashing '{img_path}' -> {part_name}...")
                    start_t = time.time()
                    
                    def cb(msg, status):
                        pass

                    ok, res = fastboot_instance.flash_partition(serial, part_name, img_path, is_simulated=is_simulated, callback=cb)
                    elapsed = time.time() - start_t
                    if ok:
                        console.print(f"[bold green]OKAY[/bold green] [{elapsed:.2f}s]")
                    else:
                        console.print(f"[bold red]FAIL ({res})[/bold red]")

                elif cmd == "erase":
                    if len(args) < 2:
                        console.print("[yellow]Usage: erase <partition_name>[/yellow]")
                        continue

                    part_name = args[1]
                    if is_simulated:
                        console.print(f"Erasing '{part_name}'... [bold green]OKAY[/bold green]")
                        continue

                    console.print(f"Erasing '{part_name}'...")
                    ok, res = fastboot_instance.py_fb.send_command(f"erase:{part_name}")
                    if ok:
                        console.print("[bold green]OKAY[/bold green]")
                    else:
                        console.print(f"[bold red]FAIL ({res})[/bold red]")

                elif cmd == "reboot":
                    target = args[1] if len(args) > 1 else "system"
                    ok, res = fastboot_instance.reboot(serial, target, is_simulated=is_simulated)
                    if ok:
                        console.print(f"Rebooting to {target}... [bold green]OKAY[/bold green]")
                    else:
                        console.print(f"[bold red]Reboot failed: {res}[/bold red]")

                elif cmd in ("oem", "flashing"):
                    sub_cmd = " ".join(args[1:])
                    if is_simulated:
                        console.print(f"Executing {cmd} {sub_cmd}... [bold green]OKAY[/bold green]")
                        continue

                    raw_c = f"{cmd} {sub_cmd}"
                    ok, res = fastboot_instance.py_fb.send_command(raw_c)
                    if ok:
                        console.print(f"{res}\n[bold green]OKAY[/bold green]")
                    else:
                        console.print(f"[bold red]FAIL ({res})[/bold red]")

                else:
                    if is_simulated:
                        console.print(f"Executing '{cmd_input}'... [bold green]OKAY[/bold green]")
                        continue

                    ok, res = fastboot_instance.py_fb.send_command(cmd_input)
                    if ok:
                        console.print(f"{res}\n[bold green]OKAY[/bold green]")
                    else:
                        console.print(f"[bold red]FAIL ({res})[/bold red]")

            except (KeyboardInterrupt, EOFError):
                break

        console.print("[dim]Exiting Fastboot Shell...[/dim]")

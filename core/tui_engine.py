import os
import sys
import tty
import termios
from rich.console import Console

console = Console()

class TUIEngine:
    """Interactive Key-Driven Terminal UI Engine (Arrow Keys & File Picker)"""

    @staticmethod
    def get_key():
        """Reads a single keypress from raw terminal input"""
        fd = sys.stdin.fileno()
        try:
            old_settings = termios.tcgetattr(fd)
        except Exception:
            # Non-tty fallback
            ch = sys.stdin.read(1)
            return ch

        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                # Read escape sequence
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A':
                        return 'UP'
                    elif ch3 == 'B':
                        return 'DOWN'
                    elif ch3 == 'C':
                        return 'RIGHT'
                    elif ch3 == 'D':
                        return 'LEFT'
                return 'ESC'
            elif ch in ('\r', '\n'):
                return 'ENTER'
            elif ch == ' ':
                return 'SPACE'
            elif ch in ('\x7f', '\x08'):
                return 'BACKSPACE'
            elif ch.lower() == 'q':
                return 'Q'
            elif ch == '0':
                return '0'
            return ch
        finally:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except Exception:
                pass

    @staticmethod
    def select_option(options, header_render_fn=None, title="Select Option"):
        """Interactive arrow key menu selector"""
        current_idx = 0
        total_items = len(options)

        while True:
            if header_render_fn:
                header_render_fn()
            else:
                os.system("clear" if os.name != "nt" else "cls")
                console.print(f"[bold cyan]:: {title}[/bold cyan]\n")

            console.print("[dim]Use UP/DOWN (↑/↓) arrow keys to navigate • ENTER to select • '0'/ESC to back[/dim]\n")

            for idx, item in enumerate(options):
                # item can be tuple (key, label, desc) or str
                if isinstance(item, tuple):
                    key, label, desc = item[0], item[1], item[2] if len(item) > 2 else ""
                    display_text = f"{label:<36} [dim]{desc}[/dim]" if desc else label
                else:
                    display_text = str(item)

                if idx == current_idx:
                    console.print(f" [bold white on blue] > {display_text} [/bold white on blue]")
                else:
                    console.print(f"   {display_text}")

            key = TUIEngine.get_key()

            if key == 'UP':
                current_idx = (current_idx - 1) % total_items
            elif key == 'DOWN':
                current_idx = (current_idx + 1) % total_items
            elif key in ('ENTER', 'RIGHT'):
                selected = options[current_idx]
                return selected[0] if isinstance(selected, tuple) else selected
            elif key in ('ESC', 'Q', 'LEFT', '0'):
                return "0"

    @staticmethod
    def file_browser(start_dir="/sdcard/Download", allowed_exts=None, select_dir_mode=False, header_render_fn=None, title="Select File"):
        """Interactive Arrow-Key File & Folder Picker"""
        current_dir = start_dir
        if not os.path.exists(current_dir):
            current_dir = "/storage/emulated/0"
        if not os.path.exists(current_dir):
            current_dir = os.path.expanduser("~")

        cursor_idx = 0

        while True:
            try:
                entries = sorted(os.listdir(current_dir))
            except Exception:
                entries = []

            # Filter folders and files
            folders = []
            files = []

            for entry in entries:
                if entry.startswith('.'):
                    continue
                full_p = os.path.join(current_dir, entry)
                if os.path.isdir(full_p):
                    folders.append(entry)
                elif os.path.isfile(full_p):
                    if allowed_exts is None or any(entry.endswith(ext) for ext in allowed_exts):
                        files.append(entry)

            items = []
            if current_dir != "/" and current_dir != "/storage/emulated/0":
                items.append(("..", "[Parent Directory]", True))

            if select_dir_mode:
                items.append((".", "[SELECT THIS CURRENT FOLDER]", True))

            for f in folders:
                items.append((f, f"📁 {f}/", True))

            for fi in files:
                full_fi = os.path.join(current_dir, fi)
                try:
                    sz_bytes = os.path.getsize(full_fi)
                    if sz_bytes < 1024 * 1024:
                        sz_str = f"{sz_bytes / 1024:.1f} KB"
                    elif sz_bytes < 1024 * 1024 * 1024:
                        sz_str = f"{sz_bytes / (1024*1024):.1f} MB"
                    else:
                        sz_str = f"{sz_bytes / (1024*1024*1024):.2f} GB"
                except:
                    sz_str = ""

                items.append((fi, f"📄 {fi:<32} [dim]({sz_str})[/dim]", False))

            if not items:
                items.append(("..", "[Empty Directory - Go Back]", True))

            if cursor_idx >= len(items):
                cursor_idx = max(0, len(items) - 1)

            if header_render_fn:
                header_render_fn()
            else:
                os.system("clear" if os.name != "nt" else "cls")
                console.print(f"[bold cyan]:: {title}[/bold cyan]\n")

            console.print(f"  Current Path: [yellow]{current_dir}[/yellow]")
            console.print("[dim]Use ↑/↓ to move • RIGHT/ENTER to open/select • LEFT to go up • '0'/ESC to cancel[/dim]\n")

            # Window scrolling for long file lists
            window_size = 12
            start_win = max(0, cursor_idx - window_size // 2)
            end_win = min(len(items), start_win + window_size)
            if end_win - start_win < window_size and start_win > 0:
                start_win = max(0, end_win - window_size)

            for idx in range(start_win, end_win):
                raw_name, display_label, is_dir = items[idx]

                if idx == cursor_idx:
                    console.print(f" [bold white on blue] > {display_label} [/bold white on blue]")
                else:
                    console.print(f"   {display_label}")

            if len(items) > window_size:
                console.print(f"\n[dim]-- Showing items {start_win+1}-{end_win} of {len(items)} --[/dim]")

            key = TUIEngine.get_key()

            if key == 'UP':
                cursor_idx = (cursor_idx - 1) % len(items)
            elif key == 'DOWN':
                cursor_idx = (cursor_idx + 1) % len(items)
            elif key in ('RIGHT', 'ENTER', 'SPACE'):
                raw_name, display_label, is_dir = items[cursor_idx]

                if raw_name == "..":
                    current_dir = os.path.dirname(current_dir)
                    cursor_idx = 0
                elif raw_name == ".":
                    return current_dir
                elif is_dir:
                    current_dir = os.path.join(current_dir, raw_name)
                    cursor_idx = 0
                else:
                    return os.path.join(current_dir, raw_name)

            elif key in ('LEFT', 'BACKSPACE'):
                if current_dir != "/" and current_dir != "/storage/emulated/0":
                    current_dir = os.path.dirname(current_dir)
                    cursor_idx = 0
                else:
                    return None

            elif key in ('ESC', 'Q', '0'):
                return None

class ARBChecker:
    """Anti-Rollback (ARB) Protection Safeguard for Xiaomi Devices"""

    @staticmethod
    def verify_safety(device_arb, rom_arb):
        device_arb = int(device_arb) if str(device_arb).isdigit() else 1
        rom_arb = int(rom_arb) if str(rom_arb).isdigit() else 1

        if rom_arb < device_arb:
            return False, (
                f"🚨 ARB CRITICAL MISMATCH!\n"
                f"Device ARB Level: v{device_arb}\n"
                f"Target ROM ARB  : v{rom_arb}\n"
                f"Flashing a lower ARB index ROM will permanently HARD BRICK (Deadboot) the device!"
            ), "CRITICAL"

        return True, f"✅ ARB Safe (Device: v{device_arb} | Target ROM: v{rom_arb})", "SAFE"

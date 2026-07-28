class ARBChecker:
    """Anti-Rollback (ARB) Guard"""

    @staticmethod
    def verify_safety(device_arb, rom_arb):
        device_arb = int(device_arb) if str(device_arb).isdigit() else 1
        rom_arb = int(rom_arb) if str(rom_arb).isdigit() else 1

        if rom_arb < device_arb:
            return False, (
                f"Warning: Anti-Rollback mismatch.\n"
                f"Device ARB level is v{device_arb}, but target ROM ARB is v{rom_arb}.\n"
                f"Flashing a lower ARB version will brick the device."
            ), "CRITICAL"

        return True, f"ARB check passed (Device: v{device_arb}, ROM: v{rom_arb})", "SAFE"

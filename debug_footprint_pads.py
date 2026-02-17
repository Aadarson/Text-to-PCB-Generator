import sys
import os
import pcbnew

def list_pads():
    KICAD_SHARE = r"C:\Program Files\KiCad\9.0\share\kicad"
    FP_LIB_PATH = os.path.join(KICAD_SHARE, "footprints")

    footprints_to_check = {
        "Arduino": ("Module", "Arduino_UNO_R3"),
    }

    print(f"Checking footprints in {FP_LIB_PATH}...")

    for name, (lib, fp_name) in footprints_to_check.items():
        lib_path = os.path.join(FP_LIB_PATH, f"{lib}.pretty")
        try:
            footprint = pcbnew.FootprintLoad(lib_path, fp_name)
            if footprint:
                print(f"\n--- {name} ({fp_name}) ---")
                for pad in footprint.Pads():
                    print(f"  Pad Name/Num: '{pad.GetName()}'")
            else:
                print(f"\nFAILED to load {name}")
        except Exception as e:
            print(f"\nERROR loading {name}: {e}")

if __name__ == "__main__":
    list_pads()

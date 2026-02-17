import sys
import os
import pcbnew

def test_load_footprint():
    # KiCad 9.0 default library path
    KICAD_SHARE = r"C:\Program Files\KiCad\9.0\share\kicad"
    FP_LIB_PATH = os.path.join(KICAD_SHARE, "footprints")

    # Put a specific library in the table? 
    # Usually pcbnew relies on fp-lib-table.
    # If the user has run KiCad, it might be setup. If not, we might need to load from file directly.

    print(f"KiCad version: {pcbnew.GetBuildVersion()}")
    
    # Try to load a footprint directly from a .pretty folder
    # We'll test loading Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal
    lib_path = os.path.join(FP_LIB_PATH, "Resistor_THT.pretty")
    fp_name = "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"
    
    print(f"Attempting to load {fp_name} from {lib_path}")
    
    try:
        # Load directly from library path
        # Note: FootprintLoad takes (library_path, footprint_name)
        footprint = pcbnew.FootprintLoad(lib_path, fp_name)
        if footprint:
            print(f"SUCCESS: Loaded footprint {footprint.GetReference()}")
        else:
            print("FAILURE: FootprintLoad returned None")
            
    except Exception as e:
        print(f"ERROR loading footprint: {e}")

if __name__ == "__main__":
    test_load_footprint()

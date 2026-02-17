import pcbnew
import sys

def inspect_api():
    b = pcbnew.BOARD()
    ds = b.GetDesignSettings()
    print("Attributes of BOARD_DESIGN_SETTINGS:")
    for d in dir(ds):
        if "NetClass" in d:
            print(f" - {d}")
    
    print("\nAttributes of m_NetSettings:")
    if hasattr(ds, 'm_NetSettings'):
        ns = ds.m_NetSettings
        for d in dir(ns):
            if "Net" in d or "Class" in d:
                print(f" - {d}")
        
        # Try finding Default
        print("Classes in NetSettings?")
        if hasattr(ns, 'm_NetClasses'):
            print("Found m_NetClasses in NetSettings")

inspect_api()

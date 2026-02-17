import sys
try:
    import pcbnew
    print("SUCCESS: pcbnew module imported.")
    print(f"KiCad Version: {pcbnew.GetBuildVersion()}")
except ImportError as e:
    print(f"FAILURE: {e}")
except Exception as e:
    print(f"ERROR: {e}")

import pcbnew
import sys
import os

def check_board(filename="design.kicad_pcb"):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return

    try:
        board = pcbnew.LoadBoard(filename)
    except Exception as e:
        print(f"Error loading board: {e}")
        return
    
    print(f"--- BOARD INSPECTION: {filename} ---")
    
    # 1. Nets
    try:
        # Just get the count, avoid iteration hell
        nets = board.GetNetsByName()
        print(f"Total Nets (Raw Count): {nets.size()}")
    except:
        print("Could not count nets.")

    # 2. Tracks & Widths
    tracks = board.GetTracks()
    width_counts = {}
    total_len = 0
    track_count = 0
    
    for track in tracks:
        if isinstance(track, pcbnew.PCB_TRACK):
            track_count += 1
            w = track.GetWidth()
            w_mm = round(pcbnew.ToMM(w), 2) # Round for comparison
            width_counts[w_mm] = width_counts.get(w_mm, 0) + 1
            total_len += track.GetLength()
            
    print("\n--- TRACK STATISTICS ---")
    print(f"Total Track Segments: {track_count}")
    print("Track Width Distribution:")
    for w, count in sorted(width_counts.items()):
        print(f"  - {w:.2f} mm: {count} segments")
        
    expected_widths = [0.25, 0.8, 1.2]
    found_widths = list(width_counts.keys())
    
    missing_widths = []
    for ew in expected_widths:
         if not any(abs(fw - ew) < 0.05 for fw in found_widths):
             missing_widths.append(ew)

    if not missing_widths:
         print("SUCCESS: All advanced track widths (0.25mm, 0.8mm, 1.2mm) found.")
    else:
         print(f"WARNING: The following track widths were NOT found: {missing_widths}")

    # 3. Zones
    zones = board.Zones()
    print("\n--- ZONES ---")
    print(f"Total Zones: {len(zones)}")
    for z in zones:
        try:
            layer = z.GetLayerName()
            print(f"  - Zone on {layer}")
        except:
            print("  - Zone found")

    # 4. Mounting Holes
    footprints = board.GetFootprints()
    holes = 0
    for fp in footprints:
        try:
            val = fp.GetValue()
            # Try getting LibID safely
            try:
                fpid = fp.GetFPID().GetLibItemName()
            except:
                fpid = ""
                
            if "MountingHole" in val or "MountingHole" in fpid:
                holes += 1
        except:
            pass
            
    print("\n--- MOUNTING HOLES ---")
    if holes >= 4:
        print(f"SUCCESS: Found {holes} Mounting Holes.")
    else:
        print(f"WARNING: Found {holes} Mounting Holes (Expected 4+).")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_board(sys.argv[1])
    else:
        check_board()

import sys
import json
import os
import pcbnew
from pcbnew import *

def create_board(netlist_file, output_file):
    print(f"Loading netlist from {netlist_file}...")
    with open(netlist_file, 'r') as f:
        data = json.load(f)
    
    components_data = data.get('components', [])
    nets_data = data.get('nets', [])

    # Create a new board
    board = pcbnew.BOARD()
    
    # Define Library Path
    # Define Library Path based on OS/ENV
    default_share = r"C:\Program Files\KiCad\9.0\share\kicad"
    if os.name != 'nt':
        default_share = "/usr/share/kicad"
        
    KICAD_SHARE = os.getenv("KICAD_SHARE", default_share)
    FP_LIB_PATH = os.path.join(KICAD_SHARE, "footprints")

    def load_footprint(fp_id):
        try:
            if ":" in fp_id:
                lib, name = fp_id.split(":", 1)
                lib_path = os.path.join(FP_LIB_PATH, f"{lib}.pretty")
                return pcbnew.FootprintLoad(lib_path, name)
            return None
        except Exception as e:
            print(f"Error loading {fp_id}: {e}")
            return None

    # 1. Add Components & Grid Placement
    comp_map = {} 
    grid_x = 50.0
    grid_y = 50.0
    row_count = 0
    
    for comp in components_data:
        ref = comp['ref']
        val = comp['value']
        fp_id = comp['footprint']
        
        footprint = load_footprint(fp_id)
        if not footprint:
            print(f"WARNING: Skipping {ref} ({fp_id})")
            continue
            
        footprint.SetReference(ref)
        footprint.SetValue(val)
        
        # Position
        pos = pcbnew.VECTOR2I(int(pcbnew.FromMM(grid_x)), int(pcbnew.FromMM(grid_y)))
        footprint.SetPosition(pos)
        
        board.Add(footprint)
        comp_map[ref] = footprint
        
        grid_x += 25.0
        row_count += 1
        if row_count > 3:
            grid_x = 50.0
            grid_y += 25.0
            row_count = 0

    # 2. PROPER NET CREATION
    net_map = {} 
    
    # Setup Design Rules (Professional Tweak)
    # Wrap in try-except to be safe across API versions
    try:
        dsettings = board.GetDesignSettings()
        if hasattr(dsettings, 'm_TrackMinWidth'):
            dsettings.m_TrackMinWidth = int(pcbnew.FromMM(0.2))
        if hasattr(dsettings, 'm_ViasMinSize'):
            dsettings.m_ViasMinSize = int(pcbnew.FromMM(0.6))
        if hasattr(dsettings, 'm_ViasMinDrill'):
            dsettings.m_ViasMinDrill = int(pcbnew.FromMM(0.3))
    except Exception as e:
        print(f"Warning: Could not set Design Rules: {e}")
    
    def get_or_create_net(name):
        # Check if already exists in board
        existing = board.FindNet(name)
        if existing:
            return existing
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        return net

    # 3. Process Connections
    print("Routing Connections...")
    for net_info in nets_data:
        net_name = net_info['name']
        net_nodes = net_info['nodes']
        
        net = get_or_create_net(net_name)
        # Net Class assignment skipped to avoid API incompatibility
        net_map[net_name] = net
        
        pads_to_connect = [] 

        # Assign Pads to Net
        for node in net_nodes:
            ref = node['ref']
            pin = node['pin']
            if ref in comp_map:
                pad = comp_map[ref].FindPadByNumber(pin)
                if pad:
                    pad.SetNet(net)
                    pads_to_connect.append(pad)

        # 4. Create Tracks (Direct Routing with Variable Width)
        if len(pads_to_connect) > 1:
            for i in range(len(pads_to_connect) - 1):
                p1 = pads_to_connect[i]
                p2 = pads_to_connect[i+1]
                
                # Determine Width based on Class
                net_cls = net_info.get('class', 'signal')
                width_mm = 0.25
                if net_cls == 'power': width_mm = 0.8 # GND/VCC
                if net_cls == 'motor': width_mm = 1.2 # High Current
                
                # Create Track
                track = pcbnew.PCB_TRACK(board)
                track.SetStart(p1.GetPosition())
                track.SetEnd(p2.GetPosition())
                track.SetWidth(int(pcbnew.FromMM(width_mm)))
                track.SetLayer(pcbnew.F_Cu)
                track.SetNet(net)
                board.Add(track)

    # 5. Add GND Zone
    # Try to find a GND net
    gnd_net = None
    for name in net_map:
        if "GND" in name.upper() or "GROUND" in name.upper():
            gnd_net = net_map[name]
            break
            
    if gnd_net:
        print(f"Adding GND Zone for {gnd_net.GetNetname()}...")
        # Get Board Bounding Box
        b_bbox = board.GetBoardEdgesBoundingBox()
        
        # Inflate slightly for zone coverage
        inflate = int(pcbnew.FromMM(2.0))
        b_bbox.Inflate(inflate) # Keep logic simple
        
        # Create Zone
        zone = pcbnew.ZONE(board)
        zone.SetLayer(pcbnew.B_Cu) # Bottom copper for ground plane logic
        zone.SetNet(gnd_net)
        
        # Add basic rectangle outline
        # Using NewOutline mechanism
        poly = zone.Outline()
        outline = poly.NewOutline()
        
        # Define rectangle points
        p1 = pcbnew.VECTOR2I(b_bbox.GetLeft(), b_bbox.GetTop())
        p2 = pcbnew.VECTOR2I(b_bbox.GetRight(), b_bbox.GetTop())
        p3 = pcbnew.VECTOR2I(b_bbox.GetRight(), b_bbox.GetBottom())
        p4 = pcbnew.VECTOR2I(b_bbox.GetLeft(), b_bbox.GetBottom())
        
        # Append logic (KiCad API varies, attempting standard poly set)
        # Note: In KiCad 7+, Append may take x, y integers
        try:
             poly.Append(b_bbox.GetLeft(), b_bbox.GetTop())
             poly.Append(b_bbox.GetRight(), b_bbox.GetTop())
             poly.Append(b_bbox.GetRight(), b_bbox.GetBottom())
             poly.Append(b_bbox.GetLeft(), b_bbox.GetBottom())
        except:
             # Fallback if API differs
             print("Warning: Could not create zone geometry (API mismatch)")
        
        board.Add(zone)
        # zone.Fill() # Usually requires valid connectivity context, might fail in script

    # 6. Edge Cuts & Mounting Holes
    listing = [m.GetBoundingBox() for m in board.GetFootprints()]
    if listing:
        rect = listing[0]
        for r in listing[1:]:
            rect.Merge(r)
        
        # Margin for routing and holes
        margin_mm = 5
        margin = int(pcbnew.FromMM(margin_mm))
        rect.Inflate(margin)
        
        pts = [
            (rect.GetLeft(), rect.GetTop()),
            (rect.GetRight(), rect.GetTop()),
            (rect.GetRight(), rect.GetBottom()),
            (rect.GetLeft(), rect.GetBottom())
        ]
        
        # Add Edge Cuts
        for i in range(4):
            seg = pcbnew.PCB_SHAPE(board)
            seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
            start = pcbnew.VECTOR2I(pts[i][0], pts[i][1])
            end = pcbnew.VECTOR2I(pts[(i+1)%4][0], pts[(i+1)%4][1])
            seg.SetStart(start)
            seg.SetEnd(end)
            seg.SetLayer(pcbnew.Edge_Cuts)
            seg.SetWidth(int(pcbnew.FromMM(0.1)))
            board.Add(seg)

        # Add Mounting Holes (M3)
        hole_offset = int(pcbnew.FromMM(3)) # 3mm from edge
        hole_size = int(pcbnew.FromMM(3.2)) # M3 clearance
        
        hole_positions = [
            (rect.GetLeft() + hole_offset, rect.GetTop() + hole_offset),
            (rect.GetRight() - hole_offset, rect.GetTop() + hole_offset),
            (rect.GetRight() - hole_offset, rect.GetBottom() - hole_offset),
            (rect.GetLeft() + hole_offset, rect.GetBottom() - hole_offset)
        ]
        
        for h_pos in hole_positions:
            try:
                # Load generic Mounting Hole footprint
                # "MountingHole:MountingHole_3.2mm_M3"
                mh = pcbnew.FootprintLoad(os.path.join(KICAD_SHARE, "footprints", "MountingHole.pretty"), "MountingHole_3.2mm_M3")
                mh.SetPosition(pcbnew.VECTOR2I(h_pos[0], h_pos[1]))
                board.Add(mh)
            except:
                print("Warning: Could not add mounting hole (footprint not found)")

    # 7. Add Zone (Moved to after Edge Cuts for better filling logic)
    if gnd_net:
        print(f"Adding GND Zone for {gnd_net.GetNetname()}...")
        
        zone = pcbnew.ZONE(board)
        zone.SetLayer(pcbnew.B_Cu) 
        zone.SetNet(gnd_net)
        zone.SetMinThickness(int(pcbnew.FromMM(0.25)))
        
        poly = zone.Outline()
        outline = poly.NewOutline()
        
        # Use simple inflated rect
        zone_rect = rect
        # zone_rect.Inflate(int(pcbnew.FromMM(-0.5))) # Pull back slightly from edge
        
        poly.Append(zone_rect.GetLeft(), zone_rect.GetTop())
        poly.Append(zone_rect.GetRight(), zone_rect.GetTop())
        poly.Append(zone_rect.GetRight(), zone_rect.GetBottom())
        poly.Append(zone_rect.GetLeft(), zone_rect.GetBottom())
        
        board.Add(zone)
        # Try to fill if possible (requires zones to be closed)
        # zone.Fill(board.GetConnectivity()) # KiCad 7+ logic is complex here
        # board.BuildConnectivity()

    pcbnew.SaveBoard(output_file, board)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python kicad_script.py <netlist> <output>")
    else:
        create_board(sys.argv[1], sys.argv[2])

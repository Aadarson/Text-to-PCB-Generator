import datetime
import subprocess
import os
import shutil

def generate_gerbers(pcb_path: str, output_dir: str) -> bool:
    """
    Generates Gerber and Drill files from a .kicad_pcb file using kicad-cli.
    Returns True if successful, False otherwise.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Path to kicad-cli (Assuming recognized in PATH or hardcoded for this env)
    # We found it in C:\Program Files\KiCad\9.0\bin\kicad-cli.exe
    kicad_cli = r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
    
    if not os.path.exists(kicad_cli):
        print(f"Error: kicad-cli not found at {kicad_cli}")
        return False

    try:
        # 1. Export Gerbers
        # Layers: F.Cu, B.Cu, F.SilkS, B.SilkS, F.Mask, B.Mask, Edge.Cuts
        cmd_gerber = [
            kicad_cli, "pcb", "export", "gerbers",
            "--output", output_dir,
            "--layers", "F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts",
            pcb_path
        ]
        
        subprocess.run(cmd_gerber, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 2. Export Drill files
        cmd_drill = [
            kicad_cli, "pcb", "export", "drill",
            "--output", output_dir,
            pcb_path
        ]
        
        subprocess.run(cmd_drill, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Gerber generation failed: {e}")
        # print(e.stderr.decode())
        return False


# Minimal footprint templates (simplified for demo purposes)
# In a real tool, these would be read from key-value pairs or .kicad_mod files
FOOTPRINT_TEMPLATES = {
    "Package_TO_SOT_THT:TO-220-3_Vertical": """
  (footprint "Package_TO_SOT_THT:TO-220-3_Vertical" (layer "F.Cu")
    (at {x} {y})
    (attr through_hole)
    (fp_text reference "{ref}" (at 0 -5.5) (layer "F.SilkS")
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (fp_text value "{val}" (at 0 3) (layer "F.Fab")
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (fp_line (start -5 -2) (end 5 -2) (layer "F.SilkS") (width 0.12))
    (fp_line (start 5 -2) (end 5 2) (layer "F.SilkS") (width 0.12))
    (fp_line (start 5 2) (end -5 2) (layer "F.SilkS") (width 0.12))
    (fp_line (start -5 2) (end -5 -2) (layer "F.SilkS") (width 0.12))
    (pad "1" thru_hole rect (at -2.54 0) (size 2 2) (drill 1) (layers "*.Cu" "*.Mask"))
    (pad "2" thru_hole circle (at 0 0) (size 2 2) (drill 1) (layers "*.Cu" "*.Mask"))
    (pad "3" thru_hole circle (at 2.54 0) (size 2 2) (drill 1) (layers "*.Cu" "*.Mask"))
  )""",
    "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm": """
  (footprint "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" (layer "F.Cu")
    (at {x} {y})
    (attr through_hole)
    (fp_text reference "{ref}" (at 0 -3.5) (layer "F.SilkS")
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (fp_text value "{val}" (at 0 3.5) (layer "F.Fab")
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (fp_circle (center 0 0) (end 2.5 0) (layer "F.SilkS") (width 0.12))
    (pad "1" thru_hole circle (at -2.5 0) (size 1.6 1.6) (drill 0.8) (layers "*.Cu" "*.Mask"))
    (pad "2" thru_hole circle (at 2.5 0) (size 1.6 1.6) (drill 0.8) (layers "*.Cu" "*.Mask"))
  )""",
     "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal": """
  (footprint "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" (layer "F.Cu")
    (at {x} {y})
    (attr through_hole)
    (fp_text reference "{ref}" (at 0 -2) (layer "F.SilkS")
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (fp_text value "{val}" (at 0 2) (layer "F.Fab")
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (fp_line (start -3.81 0) (end 3.81 0) (layer "F.SilkS") (width 0.12))
    (pad "1" thru_hole circle (at -3.81 0) (size 1.6 1.6) (drill 0.8) (layers "*.Cu" "*.Mask"))
    (pad "2" thru_hole circle (at 3.81 0) (size 1.6 1.6) (drill 0.8) (layers "*.Cu" "*.Mask"))
  )""",
    "Unknown_Footprint": """
  (footprint "Unknown_Footprint" (layer "F.Cu")
    (at {x} {y})
    (fp_text reference "{ref}" (at 0 -3) (layer "F.SilkS"))
    (fp_text value "{val}" (at 0 3) (layer "F.Fab"))
    (fp_circle (center 0 0) (end 2 0) (layer "F.SilkS") (width 0.12))
  )""",
    "Button_Switch_THT:SW_PUSH_6mm": """
  (footprint "Button_Switch_THT:SW_PUSH_6mm" (layer "F.Cu")
    (at {x} {y})
    (fp_text reference "{ref}" (at 0 -4) (layer "F.SilkS"))
    (fp_text value "{val}" (at 0 4) (layer "F.Fab"))
    (fp_rect (start -3 -3) (end 3 3) (layer "F.SilkS") (width 0.12))
    (pad "1" thru_hole circle (at -2.25 1.5) (size 1.5 1.5) (drill 0.8) (layers "*.Cu" "*.Mask"))
    (pad "2" thru_hole circle (at 2.25 1.5) (size 1.5 1.5) (drill 0.8) (layers "*.Cu" "*.Mask"))
  )""",
    "Potentiometer_THT:Potentiometer_Bourns_3386P_Vertical": """
  (footprint "Potentiometer_THT:Potentiometer_Bourns_3386P_Vertical" (layer "F.Cu")
    (at {x} {y})
    (fp_text reference "{ref}" (at 0 -3) (layer "F.SilkS"))
    (fp_text value "{val}" (at 0 3) (layer "F.Fab"))
    (fp_rect (start -4.7 -4.7) (end 4.7 4.7) (layer "F.SilkS") (width 0.12))
    (pad "1" thru_hole circle (at -2.54 -2.54) (size 1.5 1.5) (drill 0.8) (layers "*.Cu" "*.Mask"))
    (pad "2" thru_hole circle (at 0 -2.54) (size 1.5 1.5) (drill 0.8) (layers "*.Cu" "*.Mask"))
    (pad "3" thru_hole circle (at 2.54 -2.54) (size 1.5 1.5) (drill 0.8) (layers "*.Cu" "*.Mask"))
  )""",
    "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical": """
  (footprint "PinHeader_1x02" (layer "F.Cu")
    (at {x} {y})
    (fp_text reference "{ref}" (at 0 -2) (layer "F.SilkS"))
    (fp_text value "{val}" (at 0 2) (layer "F.Fab"))
    (fp_rect (start -1.27 -2.54) (end 1.27 2.54) (layer "F.SilkS") (width 0.12))
    (pad "1" thru_hole rect (at 0 -1.27) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask"))
    (pad "2" thru_hole circle (at 0 1.27) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask"))
  )""",
    "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical": """
  (footprint "PinHeader_1x03" (layer "F.Cu")
    (at {x} {y})
    (fp_text reference "{ref}" (at 0 -2) (layer "F.SilkS"))
    (fp_rect (start -1.27 -3.81) (end 1.27 3.81) (layer "F.SilkS") (width 0.12))
    (pad "1" thru_hole rect (at 0 -2.54) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask"))
    (pad "2" thru_hole circle (at 0 0) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask"))
    (pad "3" thru_hole circle (at 0 2.54) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask"))
  )""",
     "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical": """
  (footprint "PinHeader_1x04" (layer "F.Cu")
    (at {x} {y})
    (fp_text reference "{ref}" (at 0 -2) (layer "F.SilkS"))
    (fp_rect (start -1.27 -5.08) (end 1.27 5.08) (layer "F.SilkS") (width 0.12))
    (pad "1" thru_hole rect (at 0 -3.81) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask"))
    (pad "4" thru_hole circle (at 0 3.81) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask"))
  )""",
    "Module:Arduino_UNO_R3": """
  (footprint "Module:Arduino_UNO_R3" (layer "F.Cu")
    (at {x} {y})
    (fp_text reference "{ref}" (at 0 -27) (layer "F.SilkS"))
    (fp_text value "{val}" (at 0 27) (layer "F.Fab"))
    (fp_rect (start -34.8 -26.1) (end 34.8 26.1) (layer "F.SilkS") (width 0.12))
    (pad "1" thru_hole circle (at -32 -24) (size 3 3) (drill 3) (layers "*.Mask"))
    (pad "2" thru_hole circle (at 33 24) (size 3 3) (drill 3) (layers "*.Mask"))
  )""",
    "Display:LCD-016N002L": """
  (footprint "Display:LCD-016N002L" (layer "F.Cu")
    (at {x} {y})
    (fp_text reference "{ref}" (at 0 -19) (layer "F.SilkS"))
    (fp_rect (start -40 -18) (end 40 18) (layer "F.SilkS") (width 0.12))
    (pad "1" thru_hole rect (at -35 -16) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask"))
  )""",
    "Display:OLED-0.96-128x64_I2C": """
  (footprint "Display:OLED" (layer "F.Cu")
    (at {x} {y})
    (fp_text reference "{ref}" (at 0 -14) (layer "F.SilkS"))
    (fp_rect (start -13 -13) (end 13 13) (layer "F.SilkS") (width 0.12))
    (pad "1" thru_hole rect (at -3.81 -11) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask"))
  )""",
    "Relay_THT:Relay_SPDT_SANYOU_SRD_Series_Form_C": """
  (footprint "Relay_SPDT" (layer "F.Cu")
    (at {x} {y})
    (fp_rect (start -9.5 -7.5) (end 9.5 7.5) (layer "F.SilkS") (width 0.12))
    (pad "1" thru_hole circle (at -7 0) (size 2 2) (drill 1.2) (layers "*.Cu" "*.Mask"))
  )""",
    "Package_TO_SOT_THT:TO-92_Inline": """
  (footprint "TO-92" (layer "F.Cu")
    (at {x} {y})
    (fp_text reference "{ref}" (at 0 -3) (layer "F.SilkS"))
    (fp_circle (center 0 0) (end 2.5 0) (layer "F.SilkS") (width 0.12))
    (pad "1" thru_hole rect (at -1.27 0) (size 1.3 1.3) (drill 0.7) (layers "*.Cu" "*.Mask"))
    (pad "2" thru_hole circle (at 0 0) (size 1.3 1.3) (drill 0.7) (layers "*.Cu" "*.Mask"))
    (pad "3" thru_hole circle (at 1.27 0) (size 1.3 1.3) (drill 0.7) (layers "*.Cu" "*.Mask"))
  )""",
    "Sensor:Ultrasonic_HC-SR04": """
  (footprint "HC-SR04" (layer "F.Cu")
    (at {x} {y})
    (fp_rect (start -22.5 -10) (end 22.5 10) (layer "F.SilkS") (width 0.12))
    (fp_circle (center -13 0) (end -5 0) (layer "F.SilkS") (width 0.12))
    (fp_circle (center 13 0) (end 21 0) (layer "F.SilkS") (width 0.12))
    (pad "1" thru_hole rect (at -3.81 -8) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask"))
  )"""
}

def generate_kicad_pcb(netlist: dict) -> str:
    """
    Generates a .kicad_pcb file content from the netlist.
    """
    
    header = f"""(kicad_pcb (version 20211014) (generator "Text-to-PCB AI")
  (general
    (thickness 1.6)
  )
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (32 "B.Adhes" user)
    (33 "F.Adhes" user)
    (34 "B.Paste" user)
    (35 "F.Paste" user)
    (36 "B.SilkS" user)
    (37 "F.SilkS" user)
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (40 "Dwgs.User" user)
    (41 "Cmts.User" user)
    (42 "Eco1.User" user)
    (43 "Eco2.User" user)
    (44 "Edge.Cuts" user)
    (45 "Margin" user)
    (46 "B.CrtYd" user)
    (47 "F.CrtYd" user)
    (48 "B.Fab" user)
    (49 "F.Fab" user)
  )
  (setup
    (stackup
      (layer "F.SilkS" (type "Top Silk Screen"))
      (layer "F.Paste" (type "Top Solder Paste"))
      (layer "F.Mask" (type "Top Solder Mask") (color "Green") (thickness 0.01))
      (layer "F.Cu" (type "copper") (thickness 0.035))
      (layer "B.Cu" (type "copper") (thickness 0.035))
      (layer "B.Mask" (type "Bottom Solder Mask") (color "Green") (thickness 0.01))
      (layer "B.Paste" (type "Bottom Solder Paste"))
      (layer "B.SilkS" (type "Bottom Silk Screen"))
      (copper_finish "None")
      (dielectric_constraints no)
    )
    (pcbplotparams
      (layerselection 0x00010fc_ffffffff)
      (disableapertmacros no)
      (usegerberextensions yes)
      (usegerberattributes yes)
      (usegerberadvancedattributes yes)
      (creategerberjobfile yes)
      (svguseinch no)
      (svgprecision 6)
      (excludeedgelayer yes)
      (plotframeref no)
      (viasonmask no)
      (mode 1)
      (useauxorigin no)
      (hpglpennumber 1)
      (hpglpenspeed 20)
      (hpglpendiameter 15.000000)
      (dxfpolygonmode yes)
      (dxfimperialunits yes)
      (dxfusepcbnewfont yes)
      (psnegative no)
      (psa4output no)
      (plotreference yes)
      (plotvalue yes)
      (plotinvisibletext no)
      (sketchpadsonfab no)
      (subtractmaskfromsilk no)
      (outputformat 1)
      (mirror no)
      (drillshape 1)
      (scaleselection 1)
      (outputdirectory "")
    )
  )
"""

    # Grid placement logic
    grid_spacing = 15.0 # mm
    components_per_row = 4
    
    footprints_str = ""
    
    # Component placement logic with coordinate tracking
    comp_coords = {} # Map ref -> (x, y)
    
    components = netlist.get("components", [])
    for idx, comp in enumerate(components):
        row = idx // components_per_row
        col = idx % components_per_row
        x = 50.0 + (col * grid_spacing)
        y = 50.0 + (row * grid_spacing)
        
        ref = comp.get("ref", f"U{idx}")
        comp_coords[ref] = (x, y)
        
        fp_name = comp.get("footprint", "Unknown_Footprint")
        template = FOOTPRINT_TEMPLATES.get(fp_name, FOOTPRINT_TEMPLATES["Unknown_Footprint"])
        
        fp_str = template.format(
            x=x, 
            y=y, 
            ref=ref, 
            val=comp.get("value", "Val")
        )
        footprints_str += fp_str

    # Routing logic (Simple graphical lines)
    routing_str = ""
    connections = netlist.get("nets", [])
    for conn in connections:
        source_ref = None
        target_ref = None
        
        # Find refs for source and target names
        # This is a bit loose because connections use "name" (e.g. "LM7805") but we placed "U1", "C1"
        # We need to map back.
        # Simple heuristic: find first component with matching value/name and use its ref.
        # This fails if multiple same components exist. 
        # Ideally, connections should use REFs.
        # But our current NLP parser returns "names".
        # Let's try to match by name.
        
        for ref, coords in comp_coords.items():
            # Find the component with this ref
            comp = next((c for c in components if c.get("ref") == ref), None)
            if comp:
                if conn.get("from").lower() in comp.get("value").lower() and not source_ref:
                     source_ref = ref
                elif conn.get("to").lower() in comp.get("value").lower() and not target_ref:
                     target_ref = ref
        
        if source_ref and target_ref:
            x1, y1 = comp_coords[source_ref]
            x2, y2 = comp_coords[target_ref]
            routing_str += f"""
  (gr_line (start {x1} {y1}) (end {x2} {y2}) (layer "Eco1.User") (width 0.5))"""

    footer = "\n)"
    
    # Calculate board bounds
    min_x, min_y = 50.0, 50.0
    max_x, max_y = 50.0, 50.0
    
    if comp_coords:
        xs = [c[0] for c in comp_coords.values()]
        ys = [c[1] for c in comp_coords.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
    
    # Add margin
    margin = 10.0
    min_x -= margin
    min_y -= margin
    max_x += margin
    max_y += margin
    
    # Draw Edge.Cuts (Board Outline)
    edge_cuts_str = f"""
  (gr_line (start {min_x} {min_y}) (end {max_x} {min_y}) (layer "Edge.Cuts") (width 0.1))
  (gr_line (start {max_x} {min_y}) (end {max_x} {max_y}) (layer "Edge.Cuts") (width 0.1))
  (gr_line (start {max_x} {max_y}) (end {min_x} {max_y}) (layer "Edge.Cuts") (width 0.1))
  (gr_line (start {min_x} {max_y}) (end {min_x} {min_y}) (layer "Edge.Cuts") (width 0.1))
"""

    return header + footprints_str + routing_str + edge_cuts_str + footer

if __name__ == "__main__":
    test_netlist = {
        "components": [
            {"ref": "U1", "value": "LM7805", "footprint": "Package_TO_SOT_THT:TO-220-3_Vertical"},
            {"ref": "C1", "value": "Capacitor", "footprint": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"},
            {"ref": "R1", "value": "Resistor", "footprint": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"}
        ]
    }
    pcb_content = generate_kicad_pcb(test_netlist)
    print(pcb_content)

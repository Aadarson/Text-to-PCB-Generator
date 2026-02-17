import pytest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pcb_layout_generator import generate_kicad_pcb

def test_generate_pcb_content():
    netlist = {
        "components": [
            {"ref": "U1", "value": "LM7805", "footprint": "Package_TO_SOT_THT:TO-220-3_Vertical"},
            {"ref": "C1", "value": "Capacitor", "footprint": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"}
        ]
    }
    
    pcb_content = generate_kicad_pcb(netlist)
    
    assert "(kicad_pcb" in pcb_content
    assert "(version" in pcb_content
    assert "(footprint \"Package_TO_SOT_THT:TO-220-3_Vertical\"" in pcb_content
    assert "(footprint \"Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm\"" in pcb_content
    assert "(layer \"F.Cu\")" in pcb_content
    
    # Check if placement coordinates are different (at least basic check)
    # This is tricky with simple string check, but we can look for "at 50.0 50.0" and "at 65.0 50.0" 
    # based on our grid logic (50 start + 15 spacing)
    assert "(at 50.0 50.0)" in pcb_content
    assert "(at 65.0 50.0)" in pcb_content

def test_generate_simple_routing():
    netlist = {
        "components": [
            {"ref": "U1", "value": "LM7805", "footprint": "Package_TO_SOT_THT:TO-220-3_Vertical"},
            {"ref": "C1", "value": "Capacitor", "footprint": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"}
        ],
        "nets": [
            {"from": "LM7805", "to": "Capacitor"}
        ]
    }
    
    pcb_content = generate_kicad_pcb(netlist)
    assert "(gr_line" in pcb_content
    assert "(layer \"Eco1.User\")" in pcb_content

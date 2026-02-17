import pytest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.schematic_generator import generate_schematic, map_component_to_footprint

def test_map_component():
    assert map_component_to_footprint("LM7805") == "Package_TO_SOT_THT:TO-220-3_Vertical"
    assert "Capacitor" in map_component_to_footprint("capacitor")
    assert "Resistor" in map_component_to_footprint("Resistor")
    assert map_component_to_footprint("UnknownThing") == "Unknown_Footprint"

def test_generate_schematic():
    components = [
        {"name": "LM7805", "quantity": 1, "type": "NOUN"},
        {"name": "capacitor", "quantity": 2, "type": "NOUN"}
    ]
    connections = [
        {"from": "LM7805", "to": "capacitor", "type": "electrical"}
    ]
    
    netlist = generate_schematic(components, connections)
    
    assert "components" in netlist
    assert len(netlist["components"]) == 2
    assert "nets" in netlist
    assert len(netlist["nets"]) == 1
    
    # Check if footprints are assigned
    for comp in netlist["components"]:
        assert comp["footprint"] != "Unknown_Footprint"

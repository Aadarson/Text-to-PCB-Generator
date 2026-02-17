import sys
import os
import json
import subprocess

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.schematic_generator import generate_schematic

def test_pipeline():
    print("Testing Functional PCB Pipeline...")
    
    # 1. Mock parsed data (Advanced RC Car)
    components = [
        {"name": "Arduino", "quantity": 1},
        {"name": "L293D", "quantity": 1},
        {"name": "Motor", "quantity": 2},
        {"name": "Battery", "quantity": 1},
        {"name": "LED", "quantity": 2}
    ]
    # NO EXPLICIT CONNECTIONS provided
    connections = []
    
    # 2. Generate Netlist
    netlist = generate_schematic(components, connections)
    print("Netlist generated with nets:", len(netlist['nets']))
    
    # Verify Heuristics
    has_gnd = any(n['name'] == 'GND' for n in netlist['nets'])
    has_led_res = any('Net-(' in n['name'] for n in netlist['nets'] if 'GND' not in n['name'])
    
    if has_gnd: print("SUCCESS: Auto-GND Net created.")
    else: print("FAILURE: No Auto-GND Net.")
        
    if has_led_res: print("SUCCESS: Auto-LED-Resistor Pair created.")
    else: print("FAILURE: No Auto-Chain.")
    
    # 3. Save Netlist
    netlist_file = "test_netlist.json"
    with open(netlist_file, "w") as f:
        json.dump(netlist, f, indent=2)
        
    # 4. Run KiCad Script
    output_file = "test_functional.kicad_pcb"
    if os.path.exists(output_file):
        os.remove(output_file)
        
    kicad_python = r"C:\Program Files\KiCad\9.0\bin\python.exe"
    script_path = "src/kicad_script.py"
    
    cmd = [kicad_python, script_path, netlist_file, output_file]
    
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("STDOUT:", result.stdout)
    if result.returncode != 0:
        print("STDERR:", result.stderr)
        print("FAILURE: Script execution failed.")
        exit(1)
        
    if os.path.exists(output_file):
        print(f"SUCCESS: {output_file} created.")
        size = os.path.getsize(output_file)
        print(f"File size: {size} bytes")
        if size > 100:
            print("Pipeline Verification PASSED")
        else:
             print("FAILURE: File too small")
    else:
        print("FAILURE: Output file not found.")

if __name__ == "__main__":
    test_pipeline()

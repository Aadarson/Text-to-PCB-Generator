import sys
import os
import shutil

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pcb_layout_generator import generate_gerbers, generate_kicad_pcb

def test_gerber_generation():
    # 1. Create a minimal valid dummy PCB file using the REAL generator
    test_netlist = {
        "components": [
            {"ref": "U1", "value": "LM7805", "footprint": "Package_TO_SOT_THT:TO-220-3_Vertical"},
            {"ref": "C1", "value": "Capacitor", "footprint": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"}
        ],
        "nets": []
    }
    
    # Generate content with Edge.Cuts
    dummy_pcb_content = generate_kicad_pcb(test_netlist)
    
    test_pcb_file = "test_design.kicad_pcb"
    output_dir = "test_gerbers"
    
    with open(test_pcb_file, "w") as f:
        f.write(dummy_pcb_content)
        
    # Clean output dir if exists
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        
    print(f"Generating Gerbers for {test_pcb_file}...")
    success = generate_gerbers(test_pcb_file, output_dir)
    
    if success:
        print("SUCCESS: process returned True.")
        # Verify files exist
        expected_files = ["test_design-F_Cu.gbr", "test_design-B_Cu.gbr", "test_design-drl.drl"] # Partial list check
        files = os.listdir(output_dir)
        print(f"Generated files: {files}")
        if len(files) > 0:
            print("Verification PASSED: Files created.")
        else:
            print("Verification FAILED: Output directory is empty.")
            exit(1)
    else:
        print("FAILURE: generate_gerbers returned False.")
        exit(1)

    # Cleanup
    # os.remove(test_pcb_file)
    # shutil.rmtree(output_dir)

if __name__ == "__main__":
    test_gerber_generation()

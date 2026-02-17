from fastapi.testclient import TestClient
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app

client = TestClient(app)

def test_generate_endpoint_integration():
    response = client.post("/generate", json={"prompt": "Design a circuit with LM7805 and 2 capacitors. Connect LM7805 to capacitor."})
    if response.status_code != 200:
        print(f"API Error: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    
    # Check NLP part
    parsed = data["parsed_data"]
    assert len(parsed["components"]) >= 2
    assert len(parsed["connections"]) >= 1
    
    # Check Schematic part
    netlist = data["netlist"]
    assert len(netlist["components"]) == len(parsed["components"])
    assert len(netlist["nets"]) == len(parsed["connections"])
    
    # Verify footprint mapping in netlist
    for comp in netlist["components"]:
        assert comp["footprint"] != "Unknown_Footprint"
        assert comp["ref"] is not None

    # Check PCB generation
    assert "pcb_file" in data
    assert os.path.exists(data["pcb_file"])
    
    # Verify download endpoint
    download_url = data["download_url"]
    response = client.get(download_url)
    assert response.status_code == 200
    
    # Cleanup
    if os.path.exists(data["pcb_file"]):
        os.remove(data["pcb_file"])

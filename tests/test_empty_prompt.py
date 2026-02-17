from fastapi.testclient import TestClient
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app

client = TestClient(app)

def test_empty_components_warning():
    response = client.post("/generate", json={"prompt": "create an remote control base pcb board"})
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "warning"
    assert "No components detected" in data["message"]
    assert data["pcb_file"] is None

if __name__ == "__main__":
    try:
        test_empty_components_warning()
        print("Test PASSED: Warning received correctly.")
    except Exception as e:
        print(f"Test FAILED: {e}")
        import traceback
        traceback.print_exc()

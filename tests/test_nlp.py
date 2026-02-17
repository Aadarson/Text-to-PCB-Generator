import pytest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.nlp_parser import parse_requirements

def test_parse_components_basic():
    text = "Design a power supply with LM7805 and 2 capacitors"
    result = parse_requirements(text)
    
    assert "error" not in result
    components = result["components"]
    
    # Check for LM7805
    lm7805 = next((c for c in components if "LM7805" in c["name"]), None)
    assert lm7805 is not None
    assert lm7805["quantity"] == 1
    
    # Check for capacitors
    caps = next((c for c in components if "capacitor" in c["name"].lower()), None)
    assert caps is not None
    assert caps["quantity"] == 2

def test_parse_single_component():
    text = "Add a resistor"
    result = parse_requirements(text)
    resistor = next((c for c in result["components"] if "resistor" in c["name"].lower()), None)
    assert resistor is not None
    assert resistor["quantity"] == 1

def test_parse_connection():
    text = "Connect LM7805 to capacitor"
    result = parse_requirements(text)
    
    connections = result["connections"]
    assert len(connections) > 0
    conn = connections[0]
    # Note: precise extraction depends on parser accuracy, so we check for presence
    assert "LM7805" in conn["from"] or "LM7805" in conn["to"]
    assert "capacitor" in conn["to"] or "capacitor" in conn["from"]

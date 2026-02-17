import spacy
from typing import List, Dict, Any

# Load the spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback if model is not found, though it should be installed via command
    print("Warning: en_core_web_sm not found. Run 'python -m spacy download en_core_web_sm'")
    nlp = None

def parse_requirements(text: str) -> Dict[str, Any]:
    """
    Parses natural language requirements to extract components and connections.
    """
    if not nlp:
        return {"error": "NLP model not loaded"}

    doc = nlp(text)
    components = []
    
    # Expanded component keywords based on user prompts
    potential_components = [
        "lm7805", "capacitor", "resistor", "led", "diode", "battery", "switch",
        "button", "potentiometer", "sensor", "display", "screen", "oled", "lcd",
        "buzzer", "motor", "relay", "transistor", "breadboard", "wire", "jumper",
        "regulator", "module", "bluetooth", "wifi", "gsm", "rf", "esp8266", "arduino",
        "dht11", "dht22", "lm35", "hc-sr04", "pir", "ldr", "photodiode", "mq", "mpu6050",
        "segment", "header", "connector"
    ]

    # 1. Parsing Line-by-Line for Markdown Lists
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        # Check for bullet points
        if line.startswith(('-', '*', '+')):
            # Remove bullet and process the content
            content = line.lstrip('-*+ ').strip()
            # simple quantity extraction (heuristic)
            quantity = 1
            
            # Check for component match in the line content
            # strict check: any known keyword present?
            found_keyword = None
            for keyword in potential_components:
                if keyword in content.lower():
                    found_keyword = keyword
                    break
            
            if found_keyword:
                # Try to extract full name from the line (e.g., "**Push Buttons**" -> "Push Buttons")
                # Remove markdown bold/italic
                clean_name = content.replace('*', '').replace('_', '').split('-')[0].strip() # Take part before dash if description exists
                
                # Validation: ensure clean_name isn't just empty or super long description
                if len(clean_name) > 50 or len(clean_name) < 2:
                    clean_name = found_keyword.title()

                components.append({
                    "name": clean_name,
                    "quantity": quantity,
                    "type": "MarkdownList" 
                })

    # 2. SpaCy Fallback for Narrative Text (if no list items found, or to supplement)
    # Only run if line-parsing didn't yield much, or run anyway to catch things in sentences.
    # To avoid duplicates, we'll check names.
    
    existing_names = [c["name"].lower() for c in components]
    
    for token in doc:
        # Check if text matches known components (case-insensitive partial match)
        if any(comp in token.text.lower() for comp in potential_components) and token.text.lower() not in existing_names:
             # Basic check to avoid grabbing verbs or common words unless they are strictly in our list
             # (Our list is now quite broad, so we rely on POS tags for context if possible, but keep it simple for now)
             
             if token.pos_ in ["NOUN", "PROPN"] or token.text.lower() in potential_components:
                components.append({
                    "name": token.text,
                    "quantity": 1,
                    "type": token.pos_
                })
                existing_names.append(token.text.lower())

    # Connection extraction logic (unchanged for now, focusing on components)
    connections = []
    
    # Simple dependency parsing for connections
    connection_verbs = ["connect", "attach", "wire", "link", "add"]
    
    for token in doc:
        if token.lemma_.lower() in connection_verbs:
            subj = None
            obj = None
            ind_obj = None
            
            # Helper to check if token is a potential component
            def is_component(t):
                return any(comp in t.text.lower() for comp in potential_components)

            # Check children
            for child in token.children:
                if is_component(child):
                    if child.dep_ in ["nsubj", "nsubjpass"]:
                        subj = child.text
                    elif child.dep_ in ["dobj"]:
                        obj = child.text
                    elif child.dep_ in ["xcomp", "dative"]:
                        ind_obj = child.text
                
                if child.dep_ == "prep" and child.text in ["to", "with"]:
                    for grandchild in child.children:
                        if is_component(grandchild):
                            ind_obj = grandchild.text
            
            # Form connection
            source = None
            target = None
            
            if subj and ind_obj:
                source = subj
                target = ind_obj
            elif obj and ind_obj:
                source = obj
                target = ind_obj
            elif subj and obj:
                 source = subj
                 target = obj

            if source and target:
                connections.append({
                    "from": source,
                    "to": target,
                    "type": "electrical"
                })

    return {
        "original_text": text,
        "components": components,
        "connections": connections
    }

if __name__ == "__main__":
    # Quick test
    print(parse_requirements("Design a power supply with LM7805 and 2 capacitors"))

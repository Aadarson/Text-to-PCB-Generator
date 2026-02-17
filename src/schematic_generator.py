from typing import List, Dict, Any

# Simplified footprint mapping
FOOTPRINT_MAP = {
    # Specifics first
    "dht11": "Sensor:Aosong_DHT11_5.5x12.0_P2.54mm",
    "dht22": "Sensor:Aosong_DHT11_5.5x12.0_P2.54mm", 
    "mq": "Sensor:Gas_Sensor_MQ-series",
    "hc-sr04": "Sensor:Ultrasonic_HC-SR04",
    "pir": "Sensor:PIR_Motion_HC-SR501",
    "mpu6050": "Sensor_Motion:InvenSense_MPU-6050_QFN-24_4x4mm_P0.5mm",
    "ldr": "OptoDevice:Resistor_LDR_5.0x4.1mm_P3mm_Vertical",
    "oled": "Display:OLED-0.96-128x64_I2C",
    "lcd": "Display:LCD-016N002L",
    "segment": "Display_7Segment:7SegmentLED_LTS-6960HR",
    "arduino": "Module:Arduino_UNO_R3",
    "atmega328": "Package_DIP:DIP-28_W7.62mm", # Standard DIP
    "esp8266": "RF_Module:ESP-12E",
    "bluetooth": "RF_Module:HC-05", # Proxy
    "cal": "RF_Module:NRF24L01_Breakout", # Proxy catch-all if needed
    "nrf24": "RF_Module:NRF24L01_Breakout",
    "rf": "RF_Module:NRF24L01_Breakout",
    "wifi": "RF_Module:ESP-12E",
    "gsm": "RF_Module:SIM800L",
    "l293": "Package_DIP:DIP-16_W7.62mm",
    "l298": "Package_TO_SOT_THT:TO-220-15_P2.54x2.54mm_Staggered_LeadDown",
    "motor driver": "Package_DIP:DIP-16_W7.62mm",
    "regulator": "Package_TO_SOT_THT:TO-220-3_Vertical",
    "7805": "Package_TO_SOT_THT:TO-220-3_Vertical",
    "lm7805": "Package_TO_SOT_THT:TO-220-3_Vertical",
    "led": "LED_THT:LED_D5.0mm",
    "photodiode": "LED_THT:LED_D5.0mm",
    "terminal": "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
    "screw": "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
    "jack": "Connector_BarrelJack:BarrelJack_Horizontal",
    "switch": "Button_Switch_THT:SW_Slide_1P2T_SS12D06_Volz", # Slide switch for power

    # Generics last
    "display": "Display:LCD-016N002L",
    "screen": "Display:LCD-016N002L",
    "sensor": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
    "module": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
    "batery": "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal", 
    "battery": "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal", # Better for high current
    "motor": "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal", # Motors use terminals
    "capacitor": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
    "resistor": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
    "diode": "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",
    "breadboard": "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical", 
    "wire": "Connector_PinHeader_2.54mm:PinHeader_1x01_P2.54mm_Vertical",
    "jumper": "Connector_PinHeader_2.54mm:PinHeader_1x01_P2.54mm_Vertical",
    "regulator": "Package_TO_SOT_THT:TO-220-3_Vertical", 
    "header": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
    "connector": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"
}

def map_component_to_footprint(component_name: str) -> str:
    """
    Maps a component name to a KiCad footprint.
    """
    # Check for exact match first
    if component_name in FOOTPRINT_MAP:
        return FOOTPRINT_MAP[component_name]
    
    # Check for partial match (case-insensitive)
    name_lower = component_name.lower()
    for key, footprint in FOOTPRINT_MAP.items():
        if key in name_lower:
            return footprint
            
    return "Unknown_Footprint"

def generate_schematic(components: List[Dict[str, Any]], connections: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generates a schematic representation (netlist) from components and connections.
    """
    schematic_components = []
    
    for idx, comp in enumerate(components):
        ref_designator = f"U{idx+1}" # Simple auto-incrementing reference
        if "resistor" in comp["name"].lower() or "potentiometer" in comp["name"].lower():
            ref_designator = f"R{idx+1}"
        elif "capacitor" in comp["name"].lower():
            ref_designator = f"C{idx+1}"
        elif "led" in comp["name"].lower() or "diode" in comp["name"].lower():
            ref_designator = f"D{idx+1}"
        elif "switch" in comp["name"].lower() or "button" in comp["name"].lower():
            ref_designator = f"SW{idx+1}"
        elif "connector" in comp["name"].lower() or "header" in comp["name"].lower() or "jumper" in comp["name"].lower():
            ref_designator = f"J{idx+1}" 
        elif "motor" in comp["name"].lower():
            ref_designator = f"M{idx+1}"
        elif "battery" in comp["name"].lower():
            ref_designator = f"BT{idx+1}"
        elif "crystal" in comp["name"].lower():
            ref_designator = f"Y{idx+1}"
            
        footprint = map_component_to_footprint(comp["name"])
        
        schematic_components.append({
            "ref": ref_designator,
            "value": comp["name"],
            "footprint": footprint,
            "quantity": comp["quantity"]
        })

    # Component Pin Configurations (Standard KiCad Footprints)
    PIN_CONFIG = {
        "led": {"pins": ["2", "1"], "cathode": "1", "anode": "2"}, # 1=K, 2=A
        "diode": {"pins": ["2", "1"], "cathode": "1", "anode": "2"},
        "resistor": {"pins": ["1", "2"]}, 
        "capacitor": {"pins": ["1", "2"]},
        "switch": {"pins": ["1", "2"]},
        "button": {"pins": ["1", "2"]},
        "header": {"pins": ["1", "2", "3", "4", "5"]}, # Generic
        "arduino": {"pins": [str(i) for i in range(1, 33)]} # Use all valid pads
    }

    # Tracking used pins: {ref: {pin: usage_count}}
    used_pins = {c["ref"]: {} for c in schematic_components}
    
    def get_next_pin(comp, target_name=""):
        ref = comp['ref']
        ctype = "generic"
        
        # Determine type
        for k in PIN_CONFIG:
            if k in comp['value'].lower():
                ctype = k
                break
                
        config = PIN_CONFIG.get(ctype, {"pins": ["1", "2", "3"]}) # Default fallback
        available = config["pins"]
        
        # Smart Selection for Polarized Components
        if ctype in ["led", "diode"]:
            # If connecting to GND, prefer Cathode (1)
            is_gnd_target = "gnd" in target_name.lower() or "ground" in target_name.lower()
            if is_gnd_target:
                candidate = config["cathode"]
                if used_pins[ref].get(candidate, 0) == 0:
                    used_pins[ref][candidate] = 1
                    return candidate
            else:
                 # Prefer Anode (2) for signal
                 candidate = config["anode"]
                 if used_pins[ref].get(candidate, 0) == 0:
                    used_pins[ref][candidate] = 1
                    return candidate

        # Greedy Selection for others
        for p in available:
            if used_pins[ref].get(p, 0) == 0:
                used_pins[ref][p] = 1
                return p
        
        # If all used (or shared bus like GND), reuse if allowed?
        # For now, return last one or "1" to avoid crash, but log it?
        return available[0]

    # Create Nets
    net_list = []
    
    # 1. Process explicit connections from NLP
    processed_pairs = set()
    
    for conn in connections:
        src_name = conn.get("from", "").lower()
        dst_name = conn.get("to", "").lower()
        
        # Find components by loose matching name/value
        src_comp = None
        dst_comp = None
        
        for c in schematic_components:
            val = c["value"].lower()
            if src_name in val:
                src_comp = c
            if dst_name in val:
                dst_comp = c
        
        if src_comp and dst_comp:
            # Create a Net Name
            net_name = f"Net-({src_comp['ref']}-{dst_comp['ref']})"
            
            # Get Pins
            p1 = get_next_pin(src_comp, dst_comp['value'])
            p2 = get_next_pin(dst_comp, src_comp['value'])
            
            # Identify pads
            net_list.append({
                "name": net_name,
                "nodes": [
                    {"ref": src_comp['ref'], "pin": p1}, 
                    {"ref": dst_comp['ref'], "pin": p2}
                ]
            })
            processed_pairs.add((src_comp['ref'], dst_comp['ref']))

    # 2. Heuristic / Auto-Connections (The "Make it Workable" Fix)
    # If no explicit connections exist, try to chain components intelligently
    
    unconnected_leds = [c for c in schematic_components if "led" in c['value'].lower()]
    unconnected_resistors = [c for c in schematic_components if "resistor" in c['value'].lower()]
    power_sources = [c for c in schematic_components if "battery" in c['value'].lower() or "regulator" in c['value'].lower() or "arduino" in c['value'].lower()]
    
    # Heuristic A: Connect typical LED-Resistor pairs if valid
    # Logic: Pair 1 LED with 1 Resistor until we run out
    min_pairs = min(len(unconnected_leds), len(unconnected_resistors))
    for i in range(min_pairs):
        led = unconnected_leds[i]
        res = unconnected_resistors[i]
        
        if (led['ref'], res['ref']) not in processed_pairs and (res['ref'], led['ref']) not in processed_pairs:
            # Connect LED Anode -> Resistor
            # (Assuming we want Series)
            p_led = get_next_pin(led, "resistor") # Likely Anode (2)
            p_res = get_next_pin(res, "led")      # Pin 1
            
            net_name = f"Net-({led['ref']}-{res['ref']})"
            net_list.append({
                "name": net_name,
                "nodes": [
                    {"ref": led['ref'], "pin": p_led},
                    {"ref": res['ref'], "pin": p_res}
                ]
            })
            
            # Connect LED Cathode -> GND (if we have a GND concept later)
            # Connect Resistor -> Signal/Power (Placeholder)
            
            processed_pairs.add((led['ref'], res['ref']))

    # Heuristic B: Power Rails (GND, VCC)
    gnd_net_nodes = []
    
    for c in schematic_components:
        val = c['value'].lower()
        ref = c['ref']
        ctypes_with_gnd = ["arduino", "sensor", "module", "battery", "regulator", "led", "capacitor", "motor", "l293", "l298", "driver"]
        if any(t in val for t in ctypes_with_gnd):
            target = "GND"
            pin = get_next_pin(c, target)
            if pin:
               gnd_net_nodes.append({"ref": ref, "pin": pin})

    if gnd_net_nodes:
        net_list.append({
            "name": "GND",
            "nodes": gnd_net_nodes
        })

    # Heuristic C: Motor Driver <-> Motors
    motor_drivers = [c for c in schematic_components if "l293" in c['value'].lower() or "l298" in c['value'].lower() or "driver" in c['value'].lower()]
    motors = [c for c in schematic_components if "motor" in c['value'].lower() and "driver" not in c['value'].lower()]
    
    if motor_drivers and motors:
        driver = motor_drivers[0]
        pass_count = 0
        for m in motors:
            if (m['ref'], driver['ref']) in processed_pairs: continue
            net_name_1 = f"Net-(Motor_Out_{pass_count}A)"
            net_name_2 = f"Net-(Motor_Out_{pass_count}B)"
            d_pin_1 = "3" if pass_count == 0 else "11"
            d_pin_2 = "6" if pass_count == 0 else "14"
            net_list.append({"name": net_name_1, "nodes": [{"ref": driver['ref'], "pin": d_pin_1}, {"ref": m['ref'], "pin": "1"}]})
            net_list.append({"name": net_name_2, "nodes": [{"ref": driver['ref'], "pin": d_pin_2}, {"ref": m['ref'], "pin": "2"}]})
            pass_count += 1
            if pass_count >= 2: break

    # Heuristic D: Battery -> Power Input
    batteries = [c for c in schematic_components if "battery" in c['value'].lower()]
    if batteries and motor_drivers:
        bat = batteries[0]
        drv = motor_drivers[0]
        net_name = "Net-(Batt_Pos-Driver_Power)"
        net_list.append({"name": net_name, "nodes": [{"ref": bat['ref'], "pin": "2"}, {"ref": drv['ref'], "pin": "8"}]})

    # Helper: Net Classification
    def classify_net(name):
        n = name.lower()
        # High Current / Motor
        if "motor" in n or "m+" in n or "m-" in n or "net-(m" in n:
             return "motor"
        # Power
        if "gnd" in n or "vcc" in n or "5v" in n or "3v3" in n or "vin" in n or "batt" in n:
             return "power"
        # Default Signal
        return "signal"

    # Finalize Nets with Classes
    final_nets = []
    for net in net_list:
        n_cls = classify_net(net['name'])
        net['class'] = n_cls
        final_nets.append(net)

    # Basic netlist structure
    netlist = {
        "design": {
            "source": "Text-to-PCB Generator",
            "date": "2026-02-13",
            "tool": "Custom AI Generator"
        },
        "components": schematic_components,
        "nets": final_nets
    }
    
    return netlist

if __name__ == "__main__":
    # Test
    comps = [{"name": "LM7805", "quantity": 1}, {"name": "Capacitor", "quantity": 2}]
    conns = [{"from": "LM7805", "to": "Capacitor", "type": "electrical"}]
    print(generate_schematic(comps, conns))

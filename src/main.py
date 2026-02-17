from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import subprocess

app = FastAPI()

class DesignRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_design(request: DesignRequest):
    try:
        # Call NLP Parser
        from src.nlp_parser import parse_requirements
        parsed_data = parse_requirements(request.prompt)
        parsed_data = parse_requirements(request.prompt)
        print(f"Parsed Data: {parsed_data}")
        
        # Debug Log
        try:
            with open("server_debug.log", "a", encoding="utf-8") as logutils:
                logutils.write(f"--- Request ---\n")
                logutils.write(f"Prompt: {request.prompt}\n")
                logutils.write(f"Parsed: {parsed_data}\n")
        except Exception as e:
            print(f"Logging failed: {e}")
        
        if not parsed_data.get("components"):
            return {
                "status": "warning",
                "message": "No components detected in your prompt. Please be more specific (e.g., 'Add a resistor and LED').",
                "parsed_data": parsed_data,
                "netlist": {"components": [], "nets": []},
                "pcb_file": None,
                "logs": [
                    "Parsing requirement...",
                    "WARNING: No components found in the text.",
                    "Try referencing specific parts like 'LM7805', 'Resistor', 'Capacitor'."
                ],
                "download_url": None
            }

        # Generate Schematic (Netlist)
        from src.schematic_generator import generate_schematic
        netlist = generate_schematic(
            parsed_data.get("components", []), 
            parsed_data.get("connections", [])
        )
        
        # Save Netlist to JSON for KiCad Script
        import json
        netlist_file = "netlist.json"
        with open(netlist_file, "w") as f:
            json.dump(netlist, f, indent=2)

        # Generate PCB Layout using KiCad Script
        output_file = "design.kicad_pcb"
        # Determine KiCad Python Executable based on OS/ENV
        default_kicad_py = r"C:\Program Files\KiCad\9.0\bin\python.exe"
        if os.name != 'nt':
            default_kicad_py = "/usr/bin/python3" # Typical linux path
            
        kicad_python = os.getenv("KICAD_PYTHON_EXE", default_kicad_py)
        script_path = "src/kicad_script.py"
        
        print(f"Running KiCad script: {kicad_python} {script_path}")
        cmd = [kicad_python, script_path, netlist_file, output_file]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        
        if result.returncode != 0:
             raise Exception(f"KiCad script failed: {result.stderr}")
            
        # Verify output exists
        if not os.path.exists(output_file):
             raise Exception("KiCad script finished but no PCB file created.")

        # Logs update
        logs = [
            "Parsing requirements...",
            f"Identified components: {len(parsed_data.get('components', []))}",
            "Generating netlist...",
            "Executing KiCad Automation Script...",
            "Placing footprints...",
            "Routing tracks...",
            f"Generated {output_file}"
        ]
            
        # Generate Gerbers
        from src.pcb_layout_generator import generate_gerbers
        import shutil
        
        gerber_dir = "gerbers"
        gerber_zip = "design_gerbers" # shutil adds .zip automatically
        gerber_generated = generate_gerbers(output_file, gerber_dir)
        
        gerber_url = None
        if gerber_generated:
            shutil.make_archive(gerber_zip, 'zip', gerber_dir)
            gerber_url = f"/download/{gerber_zip}.zip"
            
        return {
            "status": "success", 
            "message": "Design generated successfully", 
            "parsed_data": parsed_data,
            "netlist": netlist,
            "pcb_file": output_file,
            "logs": logs + [f"Gerber generation: {'Success' if gerber_generated else 'Failed'}"],
            "download_url": f"/download/{output_file}",
            "gerber_url": gerber_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse('static/index.html')

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = filename # Simple implementation for now, ideally restrict directory
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename, media_type='application/octet-stream')
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

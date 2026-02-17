# Use an image with KiCad installed
# KiCad 8.0 is a stable choice for Docker/Linux automation
FROM kicad/kicad:8.0

# Install Python dependencies
# The base image is Ubuntu-based
USER root
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
# Use system pip or create venv (system pip is fine in container)
RUN pip3 install --no-cache-dir -r requirements.txt
RUN python3 -m spacy download en_core_web_sm



# Copy source code
COPY src/ src/
COPY static/ static/

# Environment Variables for KiCad
# The base image usually sets these, but we ensure defaults
ENV KICAD_PYTHON_EXE=/usr/bin/python3
ENV KICAD_SHARE=/usr/share/kicad
ENV HEADLESS=1
ENV PYTHONUNBUFFERED=1


# Expose Port
EXPOSE 8080

# Run FastAPI
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]

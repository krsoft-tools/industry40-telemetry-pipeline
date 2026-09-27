# Industry 4.0 Real-Time Telemetry & Analytics Engine

A production-ready Python backend simulating and analyzing real-time IoT/PLC telemetry from industrial machinery (RBG cranes, lift tables, safety light barriers) using FastAPI and Pandas.

## Features
- **Data Ingestion**: High-performance FastAPI endpoint validating complex nested telemetry payloads with Pydantic v2.
- **Hardware Simulator**: Asynchronous event generator mimicking actual warehouse and factory equipment states.
- **Real-Time Analytics**: In-memory Pandas engine executing streaming anomaly detection and critical safety violations:
  - Critical Safety Breaches (Un-muted light barrier interruption)
  - Hardware Motor Overloads (Current peaks > 75A)
  - Mechanical Timeout Errors
- **Interactive OpenAPI/Swagger**: Automatically generated interactive API documentation.

## Tech Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI / Uvicorn
- **Data Processing**: Pandas / Pydantic v2
- **Networking**: Requests / HTTP

## Quick Start

1. **Clone the repository & set up environment**:
   ```bash
   git clone <https://github.com/krsoft-tools/industry40-telemetry-pipeline>
   cd industry40-telemetry-pipeline
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the FastAPI Server**:
   ```bash
   python main.py
   ```

3. **Run the Hardware Simulator** (in a second terminal):
   ```bash
   python simulator.py
   ```

4. **View Real-Time Alerts**:
   Open `http://127.0.0.1:8000/docs` in your browser and execute `/api/analytics/alerts`.

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from typing import Dict, Any

app = FastAPI(title="Industry 4.0 Data Pipeline Engine")

# Lokálna vyrovnávacia pamäť na simuláciu toku dát
data_buffer = []

class TelemetryPayload(BaseModel):
    timestamp: float
    device_id: str
    components: Dict[str, Any]

@app.post("/api/telemetry")
async def receive_telemetry(payload: TelemetryPayload):
    # Uložíme prichádzajúce dáta do pamäte
    flat_data = {
        "timestamp": payload.timestamp,
        "rbg_status": payload.components["rbg_crane_01"]["status"],
        "rbg_current": payload.components["rbg_crane_01"]["motor_current_A"],
        "table_status": payload.components["aushubtisch_01"]["status"],
        "muting": payload.components["safety_zone_c"]["muting_sensors_active"],
        "barrier": payload.components["safety_zone_c"]["light_barrier_interrupted"],
    }
    data_buffer.append(flat_data)
    
    # Udržiavame buffer na rozumnej veľkosti (posledných 100 správ)
    if len(data_buffer) > 100:
        data_buffer.pop(0)
        
    return {"status": "processed", "stored_records": len(data_buffer)}

@app.get("/api/analytics/alerts")
async def get_alerts():
    """Pandas engine, ktorý v reálnom čase filtruje a analyzuje incidenty na linke"""
    if not data_buffer:
        return {"alerts": [], "message": "Žiadne dáta v systéme."}
        
    # Preklopenie dát z pamäte do Pandas DataFrame
    df = pd.DataFrame(data_buffer)
    alerts = []
    
    # 1. Kritérium: Detekcia neoprávneného vstupu človeka do zóny (Light barrier prerušená bez Mutingov)
    critical_safety = df[(df["barrier"] == True) & (df["muting"] == False)]
    if not critical_safety.empty:
        alerts.append({
            "type": "CRITICAL_SAFETY_VIOLATION",
            "message": f"Detekovaný človek v zóne! Závora narušená {len(critical_safety)}x bez mutingu.",
            "count": len(critical_safety)
        })
        
    # 2. Kritérium: Analýza preťaženia motorov na RBG zakladači (Prúd nad 75A)
    motor_overload = df[(df["rbg_current"] > 75.0)]
    if not motor_overload.empty:
        # Použijeme native python float(), aby bol JSON serializer v pohode
        max_val = float(motor_overload["rbg_current"].max())
        alerts.append({
            "type": "HARDWARE_MOTOR_OVERLOAD",
            "message": "RBG Zakladač hlási vysoký odber na motore (nad 75A). Hrozí prehriatie.",
            "max_current_detected": round(max_val, 2)
        })
        
    # 3. Kritérium: Chyba stola (Timeout)
    table_errors = df[df["table_status"] == "TIMEOUT_ERROR"]
    if not table_errors.empty:
        alerts.append({
            "type": "MECHANICAL_TIMEOUT",
            "message": "Zdvíhací stôl (Aushubtisch) nedosiahol koncový spínač v limite.",
            "count": len(table_errors)
        })

    return {
        "total_records_analyzed": len(df),
        "active_alerts": alerts
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

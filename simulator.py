import time
import random
import requests

# Konfigurácia - kam posielame dáta (naše FastAPI)
API_URL = "http://127.0.0.1:8000/api/telemetry"

def generate_hardware_data():
    """Simuluje reálne stavy z hardvéru na základe tvojej praxe"""
    
    # 1. RBG Zakladač (Regalbediengerät - 30m výškový robot)
    rbg_states = ["IDLE", "TRAVELING", "LIFTING", "RETRIEVING", "ERROR"]
    rbg_status = random.choices(rbg_states, weights=[20, 50, 20, 8, 2])[0]
    
    # 2. Aushubtisch 1 (Zdvíhací stôl)
    table_states = ["DOWN", "LIFTING", "UP", "LOWERING", "TIMEOUT_ERROR"]
    table_status = random.choices(table_states, weights=[40, 10, 40, 9, 1])[0]
    
    # 3. Svetelná závora a Muting (Bezpečnosť)
    # Ak je muting aktívny (True), závora môže byť prerušená (True) bez alarmu
    muting_active = random.choice([True, False])
    light_barrier_broken = random.choice([True, False]) if muting_active else random.choices([True, False], weights=[1, 99])[0]

    payload = {
        "timestamp": time.time(),
        "device_id": "SECTION_LOGISTICS_01",
        "components": {
            "rbg_crane_01": {
                "status": rbg_status,
                "current_height_m": round(random.uniform(0.0, 30.0), 2) if rbg_status != "IDLE" else 0.0,
                "motor_current_A": round(random.uniform(15.0, 85.0), 1) if rbg_status in ["TRAVELING", "LIFTING"] else 0.0
            },
            "aushubtisch_01": {
                "status": table_status,
                "limit_switch_down": True if table_status == "DOWN" else False,
                "limit_switch_up": True if table_status == "UP" else False
            },
            "safety_zone_c": {
                "muting_sensors_active": muting_active,
                "light_barrier_interrupted": light_barrier_broken
            }
        }
    }
    return payload

if __name__ == "__main__":
    print("Spúšťam hardvérový simulátor linky... (Ukončíš cez Ctrl+C)")
    while True:
        data = generate_hardware_data()
        try:
            # Posielame surové dáta na náš FastAPI backend
            response = requests.post(API_URL, json=data)
            print(f"[HARDWARE] Dáta odoslané. Server odpovedal: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("[WARN] Backend zatiaľ nebeží, čakám...")
        
        time.sleep(1.0) # Každú sekundu nový balík dát z linky

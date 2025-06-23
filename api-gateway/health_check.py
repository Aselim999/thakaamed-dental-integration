from fastapi import FastAPI, HTTPException
from typing import Dict, List
import psycopg2
import requests
import socket
from datetime import datetime

app = FastAPI()

def check_database() -> Dict:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="thakaamed_dental",
            user="postgres",
            password="postgres"
        )
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return {"status": "healthy", "response_time_ms": 10}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_mirth_connect() -> Dict:
    try:
        # Check if Mirth Connect web interface is accessible
        response = requests.get("http://localhost:8080", timeout=5)
        return {
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "response_time_ms": response.elapsed.total_seconds() * 1000
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_hl7_ports() -> List[Dict]:
    ports = [
        {"name": "HIS-RIS", "port": 6661},
        {"name": "RIS-Modality", "port": 6662},
        {"name": "Report-HIS", "port": 6663}
    ]
    
    results = []
    for port_info in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port_info['port']))
        sock.close()
        
        results.append({
            "name": port_info['name'],
            "port": port_info['port'],
            "status": "open" if result == 0 else "closed"
        })
    
    return results

def check_ai_api() -> Dict:
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        return {
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "response_time_ms": response.elapsed.total_seconds() * 1000
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/health/complete")
async def complete_health_check():
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "healthy",
        "components": {
            "database": check_database(),
            "mirth_connect": check_mirth_connect(),
            "hl7_ports": check_hl7_ports(),
            "ai_api": check_ai_api()
        }
    }
    
    # Determine overall status
    for component, status in health_status["components"].items():
        if isinstance(status, dict) and status.get("status") == "unhealthy":
            health_status["overall_status"] = "unhealthy"
            break
        elif isinstance(status, list):
            for item in status:
                if item.get("status") == "closed":
                    health_status["overall_status"] = "degraded"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
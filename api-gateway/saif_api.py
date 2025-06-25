from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import random
import asyncio
from datetime import datetime
import uvicorn
import psycopg2
from psycopg2.extras import RealDictCursor
import json

app = FastAPI(title="ThakaaMed SAIF API", version="1.0.0")

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="thakaamed_dental",
        user="abdallaselim",
        password="admin",
        cursor_factory=RealDictCursor
    )

class AnalysisRequest(BaseModel):
    patient_id: str
    order_id: str
    modality: str
    analysis_type: str
    priority: str = "normal"

class Finding(BaseModel):
    type: str
    description: str
    location: str
    confidence: float
    severity: str

class AnalysisResponse(BaseModel):
    order_id: str
    analysis_id: str
    status: str
    findings: List[Finding]
    confidence_score: float
    processing_time: float

# Mock AI analysis function
async def perform_ai_analysis(request: AnalysisRequest) -> Dict:
    # Simulate processing time
    processing_time = random.uniform(2.0, 5.0)
    await asyncio.sleep(processing_time)
    
    # Generate mock findings
    possible_findings = [
        {
            "type": "caries",
            "descriptions": [
                "Caries detected in tooth #14",
                "Deep caries in tooth #26",
                "Initial caries in tooth #37"
            ],
            "severity": ["mild", "moderate", "severe"]
        },
        {
            "type": "bone_loss",
            "descriptions": [
                "Bone loss indicated in mandibular region",
                "Periodontal bone loss around tooth #46",
                "Generalized horizontal bone loss"
            ],
            "severity": ["mild", "moderate", "severe"]
        },
        {
            "type": "periapical_lesion",
            "descriptions": [
                "Periapical radiolucency at tooth #22",
                "Possible periapical pathology at tooth #15"
            ],
            "severity": ["moderate", "severe"]
        }
    ]
    
    findings = []
    num_findings = random.randint(1, 3)
    
    for _ in range(num_findings):
        finding_type = random.choice(possible_findings)
        findings.append(Finding(
            type=finding_type["type"],
            description=random.choice(finding_type["descriptions"]),
            location=f"Quadrant {random.randint(1, 4)}",
            confidence=round(random.uniform(0.85, 0.99), 2),
            severity=random.choice(finding_type["severity"])
        ))
    
    overall_confidence = round(sum(f.confidence for f in findings) / len(findings), 2)
    
    return {
        "findings": findings,
        "confidence_score": overall_confidence,
        "processing_time": processing_time
    }

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_image(request: AnalysisRequest):
    try:
        # Save analysis request to database
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO ai_analysis_results (order_id, analysis_status)
            VALUES (%s, 'PROCESSING')
            RETURNING analysis_id
        """, (request.order_id,))
        
        analysis_id = cur.fetchone()['analysis_id']
        conn.commit()
        
        # Perform AI analysis
        result = await perform_ai_analysis(request)
        
        # Update database with results
        cur.execute("""
            UPDATE ai_analysis_results
            SET findings = %s,
                confidence_score = %s,
                analysis_status = 'COMPLETED',
                analysis_datetime = NOW()
            WHERE analysis_id = %s
        """, (
            json.dumps([f.dict() for f in result['findings']]),
            result['confidence_score'],
            analysis_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Send results to Mirth Connect
        import requests
        response_data = {
            "order_id": request.order_id,
            "analysis_id": str(analysis_id),
            "status": "completed",
            "findings": result['findings'],
            "confidence_score": result['confidence_score'],
            "processing_time": result['processing_time']
        }
        
        # Post to Mirth's HTTP listener
        requests.post("http://localhost:8080/ai-results", json=response_data)
        
        return AnalysisResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
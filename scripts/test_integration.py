import socket
import time
from datetime import datetime

def send_hl7_message(host, port, message):
    """Send HL7 message to Mirth Connect"""
    # HL7 messages need MLLP wrapping
    mllp_start = b'\x0b'
    mllp_end = b'\x1c\x0d'
    
    wrapped_message = mllp_start + message.encode('utf-8') + mllp_end
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.send(wrapped_message)
        response = sock.recv(4096)
        return response
    finally:
        sock.close()

def create_test_order():
    """Create a test ORM^O01 message"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    message = f"""MSH|^~\\&|HIS|HOSPITAL|RIS|RADIOLOGY|{timestamp}||ORM^O01|MSG{timestamp}|P|2.5
PID|1||TEST{timestamp}^^^HOSPITAL^MR||TESTPATIENT^JOHN^A||19850312|M|||123 TEST ST^RIYADH^RIYADH^12345^SA||(011)555-0123
ORC|NW|ORD{timestamp}|REQ{timestamp}|GRP{timestamp}|SC||||{timestamp}|||DR.SMITH^JOHN^A
OBR|1|ORD{timestamp}|REQ{timestamp}|PANO^Panoramic X-Ray^L|||{timestamp}|||||||||DR.JONES^MARY^B||||||||||1"""
    
    return message, f"ORD{timestamp}"

def main():
    print("Starting HL7 Integration Test...")
    
    # Step 1: Send test order
    print("\n1. Sending test order to HIS->RIS channel...")
    test_message, order_id = create_test_order()
    response = send_hl7_message('localhost', 6661, test_message)
    print(f"Response: {response}")
    print(f"Order ID: {order_id}")
    
    # Step 2: Simulate order completion
    print("\n2. Updating order status to COMPLETED...")
    import psycopg2
    conn = psycopg2.connect(
        host="localhost",
        database="thakaamed_dental",
        user="postgres",
        password="postgres"
    )
    cur = conn.cursor()
    cur.execute("UPDATE imaging_orders SET order_status = 'COMPLETED' WHERE order_id = %s", (order_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    # Step 3: Wait for AI processing
    print("\n3. Waiting for AI analysis (10 seconds)...")
    time.sleep(10)
    
    # Step 4: Check results
    print("\n4. Checking AI analysis results...")
    conn = psycopg2.connect(
        host="localhost",
        database="thakaamed_dental",
        user="postgres",
        password="postgres"
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT analysis_status, confidence_score, findings 
        FROM ai_analysis_results 
        WHERE order_id = %s
    """, (order_id,))
    
    result = cur.fetchone()
    if result:
        print(f"Analysis Status: {result[0]}")
        print(f"Confidence Score: {result[1]}")
        print(f"Findings: {result[2]}")
    else:
        print("No AI analysis results found")
    
    cur.close()
    conn.close()
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
import psycopg2
import time
import os
from datetime import datetime, timedelta

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def get_stats():
    conn = psycopg2.connect(
        host="localhost",
        database="thakaamed_dental",
        user="postgres",
        password="postgres"
    )
    cur = conn.cursor()
    
    # Get order statistics
    cur.execute("""
        SELECT order_status, COUNT(*) 
        FROM imaging_orders 
        WHERE created_at > NOW() - INTERVAL '24 hours'
        GROUP BY order_status
    """)
    order_stats = dict(cur.fetchall())
    
    # Get AI analysis statistics
    cur.execute("""
        SELECT analysis_status, COUNT(*), AVG(confidence_score)
        FROM ai_analysis_results
        WHERE created_at > NOW() - INTERVAL '24 hours'
        GROUP BY analysis_status
    """)
    ai_stats = cur.fetchall()
    
    # Get recent errors
    cur.execute("""
        SELECT COUNT(*) 
        FROM hl7_message_log
        WHERE status = 'ERROR' 
        AND created_at > NOW() - INTERVAL '1 hour'
    """)
    error_count = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return order_stats, ai_stats, error_count

def main():
    while True:
        clear_screen()
        print("=== ThakaaMed Dental Integration Monitor ===")
        print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        order_stats, ai_stats, error_count = get_stats()
        
        print("Order Statistics (Last 24 hours):")
        for status, count in order_stats.items():
            print(f"  {status}: {count}")
        
        print("\nAI Analysis Statistics (Last 24 hours):")
        for status, count, avg_confidence in ai_stats:
            print(f"  {status}: {count} (Avg Confidence: {avg_confidence:.2f}%)")
        
        print(f"\nErrors (Last hour): {error_count}")
        
        print("\nPress Ctrl+C to exit")
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
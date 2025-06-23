import psycopg2
import time
from datetime import datetime, timedelta
import statistics

class PerformanceMonitor:
    def __init__(self, db_config):
        self.db_config = db_config
        
    def get_metrics(self):
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        
        metrics = {}
        
        # Message processing times
        cur.execute("""
            SELECT 
                message_type,
                AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_processing_time,
                MAX(EXTRACT(EPOCH FROM (updated_at - created_at))) as max_processing_time,
                COUNT(*) as message_count
            FROM hl7_message_log
            WHERE created_at > NOW() - INTERVAL '1 hour'
            AND status = 'PROCESSED'
            GROUP BY message_type
        """)
        
        metrics['message_processing'] = cur.fetchall()
        
        # AI analysis performance
        cur.execute("""
            SELECT 
                AVG(EXTRACT(EPOCH FROM (analysis_datetime - created_at))) as avg_ai_time,
                AVG(confidence_score) as avg_confidence,
                COUNT(*) as analysis_count
            FROM ai_analysis_results
            WHERE created_at > NOW() - INTERVAL '1 hour'
            AND analysis_status = 'COMPLETED'
        """)
        
        metrics['ai_performance'] = cur.fetchone()
        
        # Error rates
        cur.execute("""
            SELECT 
                message_type,
                COUNT(*) as error_count
            FROM hl7_message_log
            WHERE created_at > NOW() - INTERVAL '1 hour'
            AND status = 'ERROR'
            GROUP BY message_type
        """)
        
        metrics['error_rates'] = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return metrics
    
    def generate_report(self):
        metrics = self.get_metrics()
        
        report = f"""
Performance Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 60}

Message Processing Performance (Last Hour):
{'-' * 40}
"""
        
        for msg_type, avg_time, max_time, count in metrics['message_processing']:
            report += f"{msg_type:15} | Avg: {avg_time:6.2f}s | Max: {max_time:6.2f}s | Count: {count:5}\n"
        
        ai_perf = metrics['ai_performance']
        if ai_perf and ai_perf[0]:
            report += f"""
AI Analysis Performance (Last Hour):
{'-' * 40}
Average Processing Time: {ai_perf[0]:.2f} seconds
Average Confidence Score: {ai_perf[1]:.2f}%
Total Analyses: {ai_perf[2]}
"""
        
        if metrics['error_rates']:
            report += f"""
Error Rates (Last Hour):
{'-' * 40}
"""
            for msg_type, error_count in metrics['error_rates']:
                report += f"{msg_type:15} | Errors: {error_count:5}\n"
        
        return report

# Usage
if __name__ == "__main__":
    monitor = PerformanceMonitor({
        'host': 'localhost',
        'database': 'thakaamed_dental',
        'user': 'postgres',
        'password': 'postgres'
    })
    
    print(monitor.generate_report())
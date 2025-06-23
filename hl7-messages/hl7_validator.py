import re
from typing import Dict, List, Tuple

class HL7Validator:
    def __init__(self):
        self.required_segments = {
            'ORM^O01': ['MSH', 'PID', 'ORC', 'OBR'],
            'ORU^R01': ['MSH', 'PID', 'OBR', 'OBX'],
            'MDM^T02': ['MSH', 'EVN', 'PID', 'PV1', 'TXA']
        }
    
    def validate_message(self, message: str) -> Tuple[bool, List[str]]:
        """Validate HL7 message structure"""
        errors = []
        segments = message.strip().split('\r\n')
        
        if not segments:
            errors.append("Empty message")
            return False, errors
        
        # Check MSH segment
        if not segments[0].startswith('MSH'):
            errors.append("Message must start with MSH segment")
            return False, errors
        
        # Parse MSH
        msh_fields = segments[0].split('|')
        if len(msh_fields) < 12:
            errors.append("Invalid MSH segment")
            return False, errors
        
        message_type = msh_fields[8]
        
        # Check required segments
        if message_type in self.required_segments:
            segment_types = [seg[:3] for seg in segments]
            for required in self.required_segments[message_type]:
                if required not in segment_types:
                    errors.append(f"Missing required segment: {required}")
        
        return len(errors) == 0, errors
    
    def parse_message(self, message: str) -> Dict:
        """Parse HL7 message into dictionary"""
        segments = message.strip().split('\r\n')
        parsed = {}
        
        for segment in segments:
            parts = segment.split('|')
            segment_type = parts[0]
            
            if segment_type not in parsed:
                parsed[segment_type] = []
            
            parsed[segment_type].append(parts)
        
        return parsed

# Example usage
if __name__ == "__main__":
    validator = HL7Validator()
    
    # Test message
    test_msg = """MSH|^~\\&|HIS|HOSPITAL|RIS|RADIOLOGY|20241215143000||ORM^O01|MSG001|P|2.5
PID|1||12345^^^HOSPITAL^MR||ALBADR^AHMED^MOHAMMAD||19850312|M|||123 MAIN ST^RIYADH^RIYADH^12345^SA||(011)555-0123
ORC|NW|ORD001|REQ001|GRP001|SC||||20241215143000|||DR.SMITH^JOHN^A
OBR|1|ORD001|REQ001|PANO^Panoramic X-Ray^L|||20241215150000|||||||||DR.JONES^MARY^B||||||||||1"""
    
    is_valid, errors = validator.validate_message(test_msg)
    print(f"Valid: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    
    parsed = validator.parse_message(test_msg)
    print(f"Parsed segments: {list(parsed.keys())}")
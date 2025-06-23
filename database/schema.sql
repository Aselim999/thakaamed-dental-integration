-- Patient Information
CREATE TABLE patients (
    patient_id VARCHAR(50) PRIMARY KEY,
    mrn VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    gender CHAR(1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders Table
CREATE TABLE imaging_orders (
    order_id VARCHAR(50) PRIMARY KEY,
    patient_id VARCHAR(50) REFERENCES patients(patient_id),
    order_status VARCHAR(20) DEFAULT 'NEW',
    procedure_code VARCHAR(20),
    procedure_name VARCHAR(100),
    ordering_physician VARCHAR(100),
    order_datetime TIMESTAMP,
    scheduled_datetime TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Analysis Results
CREATE TABLE ai_analysis_results (
    analysis_id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES imaging_orders(order_id),
    analysis_status VARCHAR(20) DEFAULT 'PENDING',
    findings JSONB,
    confidence_score DECIMAL(5,2),
    analysis_datetime TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- HL7 Message Log
CREATE TABLE hl7_message_log (
    log_id SERIAL PRIMARY KEY,
    message_type VARCHAR(20),
    message_control_id VARCHAR(50),
    message_content TEXT,
    direction VARCHAR(10), -- 'INBOUND' or 'OUTBOUND'
    status VARCHAR(20),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_orders_patient ON imaging_orders(patient_id);
CREATE INDEX idx_orders_status ON imaging_orders(order_status);
CREATE INDEX idx_ai_results_order ON ai_analysis_results(order_id);
CREATE INDEX idx_hl7_log_type ON hl7_message_log(message_type);
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


// =====================================
// Additional Database Schema Required:
// =====================================


-- Add these columns to existing imaging_orders table:
ALTER TABLE imaging_orders 
ADD COLUMN IF NOT EXISTS actual_start_time TIMESTAMP,
ADD COLUMN IF NOT EXISTS completion_time TIMESTAMP,
ADD COLUMN IF NOT EXISTS performing_physician VARCHAR(100),
ADD COLUMN IF NOT EXISTS performed_station VARCHAR(20),
ADD COLUMN IF NOT EXISTS operator_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Create MPPS tracking table:
CREATE TABLE mpps_tracking (
    id SERIAL PRIMARY KEY,
    mpps_instance_uid VARCHAR(64) UNIQUE NOT NULL,
    order_id VARCHAR(20) NOT NULL,
    patient_id VARCHAR(20) NOT NULL,
    mpps_status VARCHAR(20),
    performed_station_ae_title VARCHAR(20),
    performing_physician VARCHAR(100),
    operator_name VARCHAR(100),
    start_datetime TIMESTAMP,
    end_datetime TIMESTAMP,
    created_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create order status log table:
CREATE TABLE order_status_log (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    patient_id VARCHAR(20),
    mpps_instance_uid VARCHAR(64),
    previous_status VARCHAR(20),
    new_status VARCHAR(20),
    status_change_reason VARCHAR(50),
    changed_by VARCHAR(100),
    station_ae_title VARCHAR(20),
    change_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes:
CREATE INDEX idx_mpps_tracking_order_id ON mpps_tracking(order_id);
CREATE INDEX idx_mpps_tracking_patient_id ON mpps_tracking(patient_id);
CREATE INDEX idx_order_status_log_order_id ON order_status_log(order_id);
CREATE INDEX idx_imaging_orders_status ON imaging_orders(order_status);

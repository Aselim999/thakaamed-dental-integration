#!/bin/bash

# Backup script for ThakaaMed Dental Integration

BACKUP_DIR="/backup/thakaamed"
DB_NAME="thakaamed_dental"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Function to backup database
backup_database() {
    echo "Backing up database..."
    pg_dump -h localhost -U postgres -d $DB_NAME > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
    
    # Compress the backup
    gzip "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
    echo "Database backup completed: db_backup_$TIMESTAMP.sql.gz"
}

# Function to backup Mirth channels
backup_mirth_channels() {
    echo "Backing up Mirth channels..."
    
    # Export channels using Mirth CLI
    # Note: Adjust path to your Mirth installation
    /opt/mirth-connect/mccommand -s https://localhost:8443 \
        -u admin -p admin \
        -c "channel list" > "$BACKUP_DIR/channels_$TIMESTAMP.xml"
    
    echo "Mirth channels backup completed"
}

# Function to backup configuration files
backup_configs() {
    echo "Backing up configuration files..."
    
    tar -czf "$BACKUP_DIR/configs_$TIMESTAMP.tar.gz" \
        ../config/ \
        ../api-gateway/config.yaml \
        ../scripts/*.py
    
    echo "Configuration backup completed"
}

# Function to restore database
restore_database() {
    if [ -z "$1" ]; then
        echo "Usage: restore_database <backup_file>"
        return 1
    fi
    
    echo "Restoring database from $1..."
    gunzip -c "$1" | psql -h localhost -U postgres -d $DB_NAME
    echo "Database restore completed"
}

# Main execution
case "$1" in
    backup)
        mkdir -p $BACKUP_DIR
        backup_database
        backup_mirth_channels
        backup_configs
        
        # Clean old backups (keep last 7 days)
        find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
        find $BACKUP_DIR -name "*.xml" -mtime +7 -delete
        ;;
    
    restore)
        restore_database "$2"
        ;;
    
    *)
        echo "Usage: $0 {backup|restore <backup_file>}"
        exit 1
        ;;
esac
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../logs/soc_incidents.db"))

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Incidents Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            src_ip TEXT,
            severity TEXT,
            description TEXT,
            classification TEXT,
            confidence REAL,
            reason TEXT,
            full_log TEXT,
            report_path TEXT
        )
    ''')

    # 2. Active Rules Table (Persistent Registry)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            decision_id TEXT,
            rule_hash TEXT,
            src_ip TEXT,
            attack_stage TEXT,
            status TEXT,
            created_at TEXT,
            expire_at TEXT
        )
    ''')
    
    # 3. Performance Indexing
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_rule_hash ON active_rules(rule_hash)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_expire_at ON active_rules(expire_at)')
    
    conn.commit()
    conn.close()

def cleanup_expired_rules():
    """Removes all expired rules from the registry."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("DELETE FROM active_rules WHERE expire_at < ?", (now,))
    conn.commit()
    conn.close()

def is_rule_active(rule_hash):
    """Checks if a specific rule hash is currently active and unexpired."""
    cleanup_expired_rules() # Self-cleaning on check
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM active_rules WHERE rule_hash = ? AND status = 'generated'", (rule_hash,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def register_rule(rule_data):
    """Registers a new SOAR decision into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO active_rules (
            decision_id, rule_hash, src_ip, attack_stage, 
            status, created_at, expire_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        rule_data.get("decision_id"),
        rule_data.get("rule_hash"),
        rule_data.get("src_ip"),
        rule_data.get("attack_stage"),
        rule_data.get("status", "generated"),
        rule_data.get("created_at"),
        rule_data.get("expire_at")
    ))
    conn.commit()
    conn.close()

def log_incident(incident_data):

    """
    Saves an enriched and triaged incident into the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    triage = incident_data.get("triage_decision", {})
    
    cursor.execute('''
        INSERT INTO incidents (
            timestamp, src_ip, severity, description, 
            classification, confidence, reason, full_log, report_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        incident_data.get("timestamp", datetime.now().isoformat()),
        incident_data.get("src_ip", "Unknown"),
        incident_data.get("severity", "Medium"),
        incident_data.get("description", "Security Alert"),
        triage.get("classification", "Unclassified"),
        triage.get("confidence", 0.0),
        triage.get("reason", ""),
        incident_data.get("full_log", ""),
        incident_data.get("report_path", "")
    ))
    
    conn.commit()
    conn.close()

def get_recent_incidents(limit=50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM incidents ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at: {DB_PATH}")

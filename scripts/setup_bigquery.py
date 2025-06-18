# scripts/setup_bigquery.py
"""
🐙 Inktrace BigQuery Setup Script
scripts/setup_bigquery.py

Set up BigQuery dataset, tables, and sample policies for the Policy Agent.
Run this once to initialize your BigQuery environment for inktrace-463306.
"""

import asyncio
from datetime import datetime
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import json


class InktraceBigQuerySetup:
    """Setup BigQuery for Inktrace policy management"""
    
    def __init__(self, project_id: str = "inktrace-463306"):
        self.project_id = project_id
        self.dataset_id = "inktrace_policies"
        self.client = bigquery.Client(project=project_id)
        
    def setup_complete_environment(self):
        """Set up the complete BigQuery environment"""
        print("🐙 INKTRACE BIGQUERY SETUP")
        print("=" * 50)
        print(f"Project: {self.project_id}")
        print(f"Dataset: {self.dataset_id}")
        print("=" * 50)
        
        # Step 1: Create dataset
        self.create_dataset()
        
        # Step 2: Create tables
        self.create_policies_table()
        self.create_violations_table()
        self.create_agents_table()
        
        # Step 3: Load sample data
        self.load_sample_policies()
        self.load_sample_violations()
        
        print("\n✅ BigQuery setup complete!")
        print(f"📊 Dataset: {self.project_id}.{self.dataset_id}")
        print("🔗 Console: https://console.cloud.google.com/bigquery")
        
    def create_dataset(self):
        """Create the main dataset"""
        dataset_id = f"{self.project_id}.{self.dataset_id}"
        
        try:
            self.client.get_dataset(dataset_id)
            print(f"✅ Dataset already exists: {dataset_id}")
        except NotFound:
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = "US"
            dataset.description = "Inktrace security policies and compliance data for octopus intelligence"
            
            dataset = self.client.create_dataset(dataset, timeout=30)
            print(f"✅ Created dataset: {dataset_id}")
    
    def create_policies_table(self):
        """Create the security policies table"""
        table_id = f"{self.project_id}.{self.dataset_id}.security_policies"
        
        schema = [
            bigquery.SchemaField("policy_id", "STRING", mode="REQUIRED", description="Unique policy identifier"),
            bigquery.SchemaField("policy_name", "STRING", mode="REQUIRED", description="Human-readable policy name"),
            bigquery.SchemaField("category", "STRING", mode="REQUIRED", description="Policy category (Authentication, Data Protection, etc.)"),
            bigquery.SchemaField("severity", "STRING", mode="REQUIRED", description="Violation severity (CRITICAL, HIGH, MEDIUM, LOW)"),
            bigquery.SchemaField("description", "STRING", description="Detailed policy description"),
            bigquery.SchemaField("rule_expression", "STRING", mode="REQUIRED", description="Policy rule logic expression"),
            bigquery.SchemaField("remediation", "STRING", description="Recommended remediation actions"),
            bigquery.SchemaField("enabled", "BOOLEAN", mode="REQUIRED", description="Whether policy is active"),
            bigquery.SchemaField("tentacle", "STRING", description="Associated Inktrace tentacle (T1-T8)"),
            bigquery.SchemaField("regulatory_framework", "STRING", description="Related regulatory framework (GDPR, SOC2, etc.)"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        
        self._create_table_if_not_exists("security_policies", table_id, schema)
    
    def create_violations_table(self):
        """Create the policy violations table"""
        table_id = f"{self.project_id}.{self.dataset_id}.policy_violations"
        
        schema = [
            bigquery.SchemaField("violation_id", "STRING", mode="REQUIRED", description="Unique violation identifier"),
            bigquery.SchemaField("policy_id", "STRING", mode="REQUIRED", description="Associated policy ID"),
            bigquery.SchemaField("agent_id", "STRING", description="Agent that violated the policy"),
            bigquery.SchemaField("severity", "STRING", mode="REQUIRED", description="Violation severity"),
            bigquery.SchemaField("description", "STRING", description="Violation description"),
            bigquery.SchemaField("details", "JSON", description="Additional violation details"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED", description="Violation status (ACTIVE, RESOLVED, INVESTIGATING)"),
            bigquery.SchemaField("tentacle", "STRING", description="Detecting tentacle"),
            bigquery.SchemaField("threat_score", "INTEGER", description="Associated threat score (0-100)"),
            bigquery.SchemaField("detected_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("resolved_at", "TIMESTAMP"),
            bigquery.SchemaField("resolution_notes", "STRING"),
        ]
        
        self._create_table_if_not_exists("policy_violations", table_id, schema)
    
    def create_agents_table(self):
        """Create the agents monitoring table"""
        table_id = f"{self.project_id}.{self.dataset_id}.agents_monitoring"
        
        schema = [
            bigquery.SchemaField("agent_id", "STRING", mode="REQUIRED", description="Unique agent identifier"),
            bigquery.SchemaField("agent_name", "STRING", description="Agent display name"),
            bigquery.SchemaField("port", "INTEGER", description="Agent port number"),
            bigquery.SchemaField("status", "STRING", description="Agent status (ACTIVE, INACTIVE, SUSPICIOUS)"),
            bigquery.SchemaField("threat_score", "INTEGER", description="Current threat score (0-100)"),
            bigquery.SchemaField("is_malicious", "BOOLEAN", description="Whether agent is identified as malicious"),
            bigquery.SchemaField("capabilities", "JSON", description="Agent capabilities and skills"),
            bigquery.SchemaField("last_seen", "TIMESTAMP", description="Last activity timestamp"),
            bigquery.SchemaField("communication_count", "INTEGER", description="Number of A2A communications"),
            bigquery.SchemaField("metadata", "JSON", description="Additional agent metadata"),
        ]
        
        self._create_table_if_not_exists("agents_monitoring", table_id, schema)
    
    def _create_table_if_not_exists(self, table_name: str, table_id: str, schema):
        """Create table with given schema if it doesn't exist"""
        try:
            self.client.get_table(table_id)
            print(f"✅ Table already exists: {table_name}")
        except NotFound:
            table = bigquery.Table(table_id, schema=schema)
            table = self.client.create_table(table, timeout=30)
            print(f"✅ Created table: {table_name}")
    
    def load_sample_policies(self):
        """Load comprehensive sample security policies"""
        table_id = f"{self.project_id}.{self.dataset_id}.security_policies"
        
        # Get current timestamp as string for BigQuery
        current_time = datetime.now().isoformat()
        
        sample_policies = [
            # T1 - Identity & Access Management
            {
                "policy_id": "POL-T1-001",
                "policy_name": "Agent Authentication Required",
                "category": "Authentication",
                "severity": "HIGH",
                "description": "All agents must implement proper authentication mechanisms before joining the ecosystem",
                "rule_expression": "agent.has_authentication == true",
                "remediation": "Implement OAuth 2.0, API key authentication, or mutual TLS",
                "enabled": True,
                "tentacle": "T1",
                "regulatory_framework": "SOC2",
                "created_at": current_time,
                "updated_at": current_time,
            },
            {
                "policy_id": "POL-T1-002",
                "policy_name": "Multi-Factor Authentication",
                "category": "Authentication",
                "severity": "MEDIUM",
                "description": "Agents handling sensitive data must support multi-factor authentication",
                "rule_expression": "agent.supports_mfa == true AND data.sensitivity == 'high'",
                "remediation": "Enable MFA for high-sensitivity data processing agents",
                "enabled": True,
                "tentacle": "T1",
                "regulatory_framework": "NIST",
                "created_at": current_time,
                "updated_at": current_time,
            },
            
            # T2 - Data Protection
            {
                "policy_id": "POL-T2-001",
                "policy_name": "Data Encryption in Transit",
                "category": "Data Protection",
                "severity": "CRITICAL",
                "description": "All inter-agent communications must use TLS 1.3 encryption",
                "rule_expression": "communication.encryption == 'TLS' AND tls.version >= '1.3'",
                "remediation": "Enable TLS 1.3 for all agent communications and disable legacy protocols",
                "enabled": True,
                "tentacle": "T2",
                "regulatory_framework": "GDPR",
                "created_at": current_time,
                "updated_at": current_time,
            },
            {
                "policy_id": "POL-T2-002",
                "policy_name": "Data Encryption at Rest",
                "category": "Data Protection",
                "severity": "HIGH",
                "description": "Agent data storage must use AES-256 encryption",
                "rule_expression": "storage.encryption == 'AES-256'",
                "remediation": "Configure AES-256 encryption for all agent data stores",
                "enabled": True,
                "tentacle": "T2",
                "regulatory_framework": "HIPAA",
                "created_at": current_time,
                "updated_at": current_time,
            },
            
            # T3 - Behavioral Intelligence
            {
                "policy_id": "POL-T3-001",
                "policy_name": "Resource Consumption Limits",
                "category": "Behavioral",
                "severity": "MEDIUM",
                "description": "Agents must not exceed 80% CPU or memory utilization",
                "rule_expression": "resources.cpu_usage <= 80 AND resources.memory_usage <= 80",
                "remediation": "Implement resource quotas and monitoring for agent processes",
                "enabled": True,
                "tentacle": "T3",
                "regulatory_framework": "Internal",
                "created_at": current_time,
                "updated_at": current_time,
            },
            
            # T4 - Operational Resilience
            {
                "policy_id": "POL-T4-001",
                "policy_name": "Agent Health Monitoring",
                "category": "Resilience",
                "severity": "HIGH",
                "description": "All agents must respond to health checks within 5 seconds",
                "rule_expression": "health_check.response_time <= 5000",
                "remediation": "Implement proper health check endpoints and monitoring",
                "enabled": True,
                "tentacle": "T4",
                "regulatory_framework": "Internal",
                "created_at": current_time,
                "updated_at": current_time,
            },
            
            # T5 - Supply Chain Security
            {
                "policy_id": "POL-T5-001",
                "policy_name": "Dependency Security Scanning",
                "category": "Supply Chain",
                "severity": "HIGH",
                "description": "Agent dependencies must be scanned for known vulnerabilities",
                "rule_expression": "dependencies.vulnerability_scan == 'passed'",
                "remediation": "Run dependency security scans and update vulnerable packages",
                "enabled": True,
                "tentacle": "T5",
                "regulatory_framework": "NIST",
                "created_at": current_time,
                "updated_at": current_time,
            },
            
            # T6 - Compliance & Governance
            {
                "policy_id": "POL-T6-001",
                "policy_name": "GDPR Data Retention Limit",
                "category": "Privacy",
                "severity": "HIGH",
                "description": "Personal data must not be retained longer than 2 years",
                "rule_expression": "data.retention_days <= 730 AND data.type == 'personal'",
                "remediation": "Implement automated data purging after 24 months for personal data",
                "enabled": True,
                "tentacle": "T6",
                "regulatory_framework": "GDPR",
                "created_at": current_time,
                "updated_at": current_time,
            },
            {
                "policy_id": "POL-T6-002",
                "policy_name": "Audit Log Retention",
                "category": "Compliance",
                "severity": "MEDIUM",
                "description": "Security audit logs must be retained for 7 years",
                "rule_expression": "logs.type == 'security' AND logs.retention_years >= 7",
                "remediation": "Configure log retention policy for security events per regulatory requirements",
                "enabled": True,
                "tentacle": "T6",
                "regulatory_framework": "SOX",
                "created_at": current_time,
                "updated_at": current_time,
            },
            
            # T7 - Advanced Threats
            {
                "policy_id": "POL-T7-001",
                "policy_name": "Malicious Agent Detection",
                "category": "Threat Detection",
                "severity": "CRITICAL",
                "description": "Agents with threat scores >70 must be quarantined immediately",
                "rule_expression": "agent.threat_score > 70",
                "remediation": "Quarantine agent, initiate security investigation, and notify security team",
                "enabled": True,
                "tentacle": "T7",
                "regulatory_framework": "Internal",
                "created_at": current_time,
                "updated_at": current_time,
            },
            {
                "policy_id": "POL-T7-002",
                "policy_name": "Prompt Injection Protection",
                "category": "Threat Detection",
                "severity": "HIGH",
                "description": "Agents must validate and sanitize all input prompts",
                "rule_expression": "input.validation == 'enabled' AND prompt.sanitization == 'active'",
                "remediation": "Implement prompt injection detection and input sanitization",
                "enabled": True,
                "tentacle": "T7",
                "regulatory_framework": "Internal",
                "created_at": current_time,
                "updated_at": current_time,
            },
            
            # T8 - Network Security
            {
                "policy_id": "POL-T8-001",
                "policy_name": "Network Segmentation",
                "category": "Network Security",
                "severity": "HIGH",
                "description": "Agents must operate within designated network segments",
                "rule_expression": "network.segment == 'authorized' AND firewall.rules == 'enforced'",
                "remediation": "Configure network segmentation and firewall rules for agent isolation",
                "enabled": True,
                "tentacle": "T8",
                "regulatory_framework": "NIST",
                "created_at": current_time,
                "updated_at": current_time,
            }
        ]
        
        try:
            # Check if policies already exist
            query = f"SELECT COUNT(*) as count FROM `{table_id}`"
            results = list(self.client.query(query))
            
            if results[0].count == 0:
                errors = self.client.insert_rows_json(
                    self.client.get_table(table_id), 
                    sample_policies
                )
                
                if errors:
                    print(f"❌ Error inserting sample policies: {errors}")
                else:
                    print(f"✅ Loaded {len(sample_policies)} sample policies across all 8 tentacles")
            else:
                print(f"✅ Policies already exist: {results[0].count} policies")
                
        except Exception as e:
            print(f"❌ Error loading sample policies: {e}")
    
    def load_sample_violations(self):
        """Load sample policy violations for demo purposes"""
        table_id = f"{self.project_id}.{self.dataset_id}.policy_violations"
        
        # Get current timestamp as string for BigQuery
        current_time = datetime.now().isoformat()
        
        sample_violations = [
            {
                "violation_id": "VIO-001",
                "policy_id": "POL-T6-001",
                "agent_id": "data_processor",
                "severity": "HIGH",
                "description": "Customer data retention exceeds 2-year GDPR limit",
                "details": {
                    "data_age_days": 850,
                    "data_type": "personal",
                    "estimated_records": 15000
                },
                "status": "ACTIVE",
                "tentacle": "T6",
                "threat_score": 65,
                "detected_at": current_time,
                "resolved_at": None,
                "resolution_notes": None,
            },
            {
                "violation_id": "VIO-002",
                "policy_id": "POL-T2-001",
                "agent_id": "legacy_agent",
                "severity": "CRITICAL",
                "description": "Agent using deprecated TLS 1.2 instead of required TLS 1.3",
                "details": {
                    "current_tls_version": "1.2",
                    "required_tls_version": "1.3",
                    "encryption_strength": "medium"
                },
                "status": "INVESTIGATING",
                "tentacle": "T2",
                "threat_score": 45,
                "detected_at": current_time,
                "resolved_at": None,
                "resolution_notes": "Coordinating with DevOps team for TLS upgrade",
            }
        ]
        
        try:
            query = f"SELECT COUNT(*) as count FROM `{table_id}`"
            results = list(self.client.query(query))
            
            if results[0].count == 0:
                errors = self.client.insert_rows_json(
                    self.client.get_table(table_id), 
                    sample_violations
                )
                
                if errors:
                    print(f"❌ Error inserting sample violations: {errors}")
                else:
                    print(f"✅ Loaded {len(sample_violations)} sample violations for demo")
            else:
                print(f"✅ Violations already exist: {results[0].count} violations")
                
        except Exception as e:
            print(f"❌ Error loading sample violations: {e}")


def main():
    """Main setup function"""
    print("🚀 Setting up BigQuery for Inktrace Policy Agent...")
    
    try:
        setup = InktraceBigQuerySetup()
        setup.setup_complete_environment()
        
        print("\n📋 NEXT STEPS:")
        print("1. Run: python agents/policy_agent.py --port 8006")
        print("2. Test with: curl -X POST http://localhost:8006/tasks/send")
        print("3. View data: https://console.cloud.google.com/bigquery")
        print("4. Deploy to Cloud Run with the deployment scripts")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("\n💡 Make sure you have:")
        print("   - Google Cloud SDK installed and authenticated")
        print("   - BigQuery API enabled for inktrace-463306")
        print("   - Appropriate IAM permissions")


if __name__ == "__main__":
    main()
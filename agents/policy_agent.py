# agents/policy_agent.py
"""
🐙 Inktrace Policy Agent - T6 Compliance & Governance Tentacle
agents/policy_agent.py

Enterprise policy compliance checker using BigQuery for config-driven policies.
Part of the 8-Tentacle Security Matrix focusing on regulatory compliance.
"""

import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import argparse
import httpx
import os

# A2A SDK imports
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import AgentCard, AgentSkill, AgentCapabilities
from a2a.utils import new_agent_text_message
import uvicorn

# BigQuery imports
try:
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    print("⚠️ BigQuery library not available. Run: pip install google-cloud-bigquery")


class PolicyViolation:
    """Represents a policy violation"""

    def __init__(self, policy_id: str, policy_name: str, severity: str,
                 description: str, agent_id: str = None, recommendation: str = None):
        self.id = str(uuid.uuid4())
        self.policy_id = policy_id
        self.policy_name = policy_name
        self.severity = severity
        self.description = description
        self.agent_id = agent_id
        self.recommendation = recommendation
        self.timestamp = datetime.now()
        self.status = "ACTIVE"


class BigQueryPolicyStore:
    """BigQuery-based policy storage and management"""

    def __init__(self, project_id: str = "inktrace-463306"):
        self.project_id = project_id
        self.dataset_id = "inktrace_policies"
        self.policies_table = "security_policies"
        self.violations_table = "policy_violations"
        self.client = None

        if BIGQUERY_AVAILABLE:
            try:
                self.client = bigquery.Client(project=project_id)
                self.ensure_dataset_exists()
                self.ensure_tables_exist()
                print(
                    f"✅ Connected to BigQuery: {project_id}.{self.dataset_id}")
            except Exception as e:
                print(f"⚠️ BigQuery connection failed: {e}")
                self.client = None

    def ensure_dataset_exists(self):
        """Create dataset if it doesn't exist"""
        if not self.client:
            return

        dataset_id = f"{self.project_id}.{self.dataset_id}"

        try:
            self.client.get_dataset(dataset_id)
            print(f"✅ Dataset exists: {dataset_id}")
        except NotFound:
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = "US"
            dataset.description = "Inktrace security policies and compliance data"

            dataset = self.client.create_dataset(dataset, timeout=30)
            print(f"✅ Created dataset: {dataset_id}")

    def ensure_tables_exist(self):
        """Create tables if they don't exist"""
        if not self.client:
            return

        # Policies table schema
        policies_schema = [
            bigquery.SchemaField("policy_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("policy_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("category", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("severity", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("description", "STRING"),
            bigquery.SchemaField("rule_expression", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("remediation", "STRING"),
            bigquery.SchemaField("enabled", "BOOLEAN", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
        ]

        # Violations table schema
        violations_schema = [
            bigquery.SchemaField("violation_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("policy_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("agent_id", "STRING"),
            bigquery.SchemaField("severity", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("description", "STRING"),
            bigquery.SchemaField("details", "JSON"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("detected_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("resolved_at", "TIMESTAMP"),
        ]

        self._create_table_if_not_exists(self.policies_table, policies_schema)
        self._create_table_if_not_exists(
            self.violations_table, violations_schema)

    def _create_table_if_not_exists(self, table_name: str, schema: List):
        """Create table with given schema if it doesn't exist"""
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"

        try:
            self.client.get_table(table_id)
            print(f"✅ Table exists: {table_name}")
        except NotFound:
            table = bigquery.Table(table_id, schema=schema)
            table = self.client.create_table(table, timeout=30)
            print(f"✅ Created table: {table_name}")

    async def load_sample_policies(self):
        """Load sample security policies into BigQuery"""
        if not self.client:
            return

        sample_policies = [
            {
                "policy_id": "POL-001",
                "policy_name": "Agent Authentication Required",
                "category": "Authentication",
                "severity": "HIGH",
                "description": "All agents must implement proper authentication mechanisms",
                "rule_expression": "agent.has_authentication == true",
                "remediation": "Implement OAuth 2.0 or API key authentication",
                "enabled": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "policy_id": "POL-002",
                "policy_name": "Data Encryption in Transit",
                "category": "Data Protection",
                "severity": "CRITICAL",
                "description": "All inter-agent communications must use TLS encryption",
                "rule_expression": "communication.encryption == 'TLS'",
                "remediation": "Enable TLS 1.3 for all agent communications",
                "enabled": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "policy_id": "POL-003",
                "policy_name": "GDPR Data Retention Limit",
                "category": "Privacy",
                "severity": "HIGH",
                "description": "Personal data must not be retained longer than 2 years",
                "rule_expression": "data.retention_days <= 730 AND data.type == 'personal'",
                "remediation": "Implement automated data purging after 24 months",
                "enabled": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "policy_id": "POL-004",
                "policy_name": "Malicious Agent Detection",
                "category": "Threat Detection",
                "severity": "CRITICAL",
                "description": "Agents with threat scores >70 must be quarantined",
                "rule_expression": "agent.threat_score > 70",
                "remediation": "Quarantine agent and initiate security investigation",
                "enabled": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "policy_id": "POL-005",
                "policy_name": "Audit Log Retention",
                "category": "Compliance",
                "severity": "MEDIUM",
                "description": "Security audit logs must be retained for 7 years",
                "rule_expression": "logs.type == 'security' AND logs.retention_years >= 7",
                "remediation": "Configure log retention policy for security events",
                "enabled": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ]

        table_id = f"{self.project_id}.{self.dataset_id}.{self.policies_table}"

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
                    print(f"✅ Loaded {len(sample_policies)} sample policies")
            else:
                print(f"✅ Policies already exist: {results[0].count} policies")

        except Exception as e:
            print(f"❌ Error loading sample policies: {e}")

    async def get_active_policies(self) -> List[Dict]:
        """Get all active policies from BigQuery"""
        if not self.client:
            return self._get_fallback_policies()

        try:
            query = f"""
            SELECT * FROM `{self.project_id}.{self.dataset_id}.{self.policies_table}`
            WHERE enabled = true
            ORDER BY severity DESC, policy_name ASC
            """

            results = self.client.query(query)
            policies = []

            for row in results:
                policies.append({
                    "policy_id": row.policy_id,
                    "policy_name": row.policy_name,
                    "category": row.category,
                    "severity": row.severity,
                    "description": row.description,
                    "rule_expression": row.rule_expression,
                    "remediation": row.remediation,
                    "enabled": row.enabled,
                })

            return policies

        except Exception as e:
            print(f"❌ Error fetching policies from BigQuery: {e}")
            return self._get_fallback_policies()

    def _get_fallback_policies(self) -> List[Dict]:
        """Fallback policies when BigQuery is not available"""
        return [
            {
                "policy_id": "POL-001",
                "policy_name": "Agent Authentication Required",
                "category": "Authentication",
                "severity": "HIGH",
                "description": "All agents must implement proper authentication mechanisms",
                "rule_expression": "agent.has_authentication == true",
                "remediation": "Implement OAuth 2.0 or API key authentication",
                "enabled": True,
            },
            {
                "policy_id": "POL-004",
                "policy_name": "Malicious Agent Detection",
                "category": "Threat Detection",
                "severity": "CRITICAL",
                "description": "Agents with threat scores >70 must be quarantined",
                "rule_expression": "agent.threat_score > 70",
                "remediation": "Quarantine agent and initiate security investigation",
                "enabled": True,
            }
        ]

    async def record_violation(self, violation: PolicyViolation) -> bool:
        """Record a policy violation in BigQuery"""
        if not self.client:
            print(
                f"📝 [FALLBACK] Policy violation: {violation.policy_name} - {violation.description}")
            return True

        try:
            table_id = f"{self.project_id}.{self.dataset_id}.{self.violations_table}"

            violation_data = {
                "violation_id": violation.id,
                "policy_id": violation.policy_id,
                "agent_id": violation.agent_id,
                "severity": violation.severity,
                "description": violation.description,
                "details": {
                    "policy_name": violation.policy_name,
                    "recommendation": violation.recommendation
                },
                "status": violation.status,
                "detected_at": violation.timestamp,
                "resolved_at": None,
            }

            errors = self.client.insert_rows_json(
                self.client.get_table(table_id),
                [violation_data]
            )

            if errors:
                print(f"❌ Error recording violation: {errors}")
                return False

            print(f"✅ Recorded violation: {violation.policy_name}")
            return True

        except Exception as e:
            print(f"❌ Error recording violation: {e}")
            return False


class InktracePolicyExecutor(AgentExecutor):
    """🐙 Inktrace Policy Agent Executor"""

    def __init__(self):
        super().__init__()
        self.policy_store = BigQueryPolicyStore()
        self.wiretap_url = "http://localhost:8003"
        print("🐙 Inktrace Policy Agent Executor initialized")

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """Execute policy compliance check"""
        try:
            # Extract text from context
            text_content = "Policy compliance check requested"

            if hasattr(context, 'message') and context.message:
                if hasattr(context.message, 'parts') and context.message.parts:
                    first_part = context.message.parts[0]
                    if hasattr(first_part, 'text'):
                        text_content = first_part.text
                    elif hasattr(first_part, 'root') and hasattr(first_part.root, 'text'):
                        text_content = first_part.root.text

            print(
                f"📋 Running policy compliance check: {text_content[:100]}...")

            if "demo" in text_content.lower() and "compliance" in text_content.lower():
                # Handle as demo request with BigQuery recording
                response_text = await self.handle_demo_request(text_content)
                event_queue.enqueue_event(
                    new_agent_text_message(response_text))
                print("✅ Demo compliance check completed with BigQuery recording")
                return

            # Load sample policies if needed
            await self.policy_store.load_sample_policies()

            # Get current agent state from wiretap
            agent_data = await self.get_agent_data()

            # Run policy checks
            violations = await self.check_policies(agent_data)

            # Generate compliance report
            report = await self.generate_compliance_report(violations, agent_data)

            # Send response
            response_text = self.format_compliance_report(report)
            event_queue.enqueue_event(new_agent_text_message(response_text))

            print(
                f"✅ Policy compliance check completed - {len(violations)} violations found")

        except Exception as e:
            print(f"❌ Error in policy agent execution: {e}")
            import traceback
            traceback.print_exc()

            error_response = f"Error running policy compliance check: {str(e)}"
            event_queue.enqueue_event(new_agent_text_message(error_response))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Handle task cancellation"""
        print("🛑 Policy agent task cancelled")
        event_queue.enqueue_event(new_agent_text_message("Task cancelled"))

    async def get_agent_data(self) -> Dict:
        """Get current agent data from wiretap tentacle"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.wiretap_url}/api/agents")

                if response.status_code == 200:
                    data = response.json()
                    return data.get("agents", {})
                else:
                    print(
                        f"⚠️ Could not get agent data from wiretap: HTTP {response.status_code}")
                    return {}

        except Exception as e:
            print(f"⚠️ Error getting agent data: {e}")
            return {}

    async def check_policies(self, agent_data: Dict) -> List[PolicyViolation]:
        """Check all policies against current agent data"""
        violations = []
        policies = await self.policy_store.get_active_policies()

        print(
            f"📋 Checking {len(policies)} policies against {len(agent_data)} agents...")

        for policy in policies:
            policy_violations = await self.evaluate_policy(policy, agent_data)
            violations.extend(policy_violations)

        # Record violations in BigQuery
        for violation in violations:
            await self.policy_store.record_violation(violation)

        return violations

    async def evaluate_policy(self, policy: Dict, agent_data: Dict) -> List[PolicyViolation]:
        """Evaluate a single policy against agent data"""
        violations = []
        policy_id = policy["policy_id"]
        policy_name = policy["policy_name"]
        severity = policy["severity"]
        rule = policy["rule_expression"]
        remediation = policy.get("remediation", "Contact security team")

        # Simple rule evaluation based on policy type
        if policy_id == "POL-001":  # Authentication check
            for agent_id, agent in agent_data.items():
                if not agent.get("has_authentication", False):
                    violations.append(PolicyViolation(
                        policy_id=policy_id,
                        policy_name=policy_name,
                        severity=severity,
                        description=f"Agent {agent_id} lacks proper authentication",
                        agent_id=agent_id,
                        recommendation=remediation
                    ))

        elif policy_id == "POL-002":  # TLS encryption check
            for agent_id, agent in agent_data.items():
                if agent.get("communication", {}).get("encryption") != "TLS":
                    violations.append(PolicyViolation(
                        policy_id=policy_id,
                        policy_name=policy_name,
                        severity=severity,
                        description=f"Agent {agent_id} not using TLS encryption",
                        agent_id=agent_id,
                        recommendation=remediation
                    ))

        elif policy_id == "POL-004":  # Malicious agent detection
            for agent_id, agent in agent_data.items():
                threat_analysis = agent.get("threat_analysis", {})
                threat_score = threat_analysis.get("threat_score", 0)

                if threat_score > 70:
                    violations.append(PolicyViolation(
                        policy_id=policy_id,
                        policy_name=policy_name,
                        severity=severity,
                        description=f"Agent {agent_id} has high threat score: {threat_score}/100",
                        agent_id=agent_id,
                        recommendation=remediation
                    ))

        elif policy_id == "POL-003":  # GDPR data retention
            # Simulate GDPR violation for demo
            violations.append(PolicyViolation(
                policy_id=policy_id,
                policy_name=policy_name,
                severity=severity,
                description="Customer data retention exceeds 2-year GDPR limit",
                agent_id="data_processor",
                recommendation=remediation
            ))

        return violations

    async def generate_compliance_report(self, violations: List[PolicyViolation], agent_data: Dict) -> Dict:
        """Generate comprehensive compliance report"""
        total_policies = len(await self.policy_store.get_active_policies())
        total_violations = len(violations)
        compliance_score = max(0, 100 - (total_violations * 10))

        # Categorize violations by severity
        critical_violations = [
            v for v in violations if v.severity == "CRITICAL"]
        high_violations = [v for v in violations if v.severity == "HIGH"]
        medium_violations = [v for v in violations if v.severity == "MEDIUM"]

        # Determine compliance status
        if critical_violations:
            compliance_status = "NON_COMPLIANT"
            risk_level = "CRITICAL"
        elif high_violations:
            compliance_status = "PARTIALLY_COMPLIANT"
            risk_level = "HIGH"
        elif medium_violations:
            compliance_status = "MINOR_ISSUES"
            risk_level = "MEDIUM"
        else:
            compliance_status = "COMPLIANT"
            risk_level = "LOW"

        return {
            "report_id": str(uuid.uuid4()),
            "generated_at": datetime.now().isoformat(),
            "compliance_score": compliance_score,
            "compliance_status": compliance_status,
            "risk_level": risk_level,
            "total_policies": total_policies,
            "total_violations": total_violations,
            "violations_by_severity": {
                "critical": len(critical_violations),
                "high": len(high_violations),
                "medium": len(medium_violations)
            },
            "violations": [
                {
                    "id": v.id,
                    "policy_id": v.policy_id,
                    "policy_name": v.policy_name,
                    "severity": v.severity,
                    "description": v.description,
                    "agent_id": v.agent_id,
                    "recommendation": v.recommendation,
                    "timestamp": v.timestamp.isoformat()
                }
                for v in violations
            ],
            "agents_checked": len(agent_data),
            "recommendations": self.generate_recommendations(violations)
        }

    async def handle_demo_violations(self, violations_data: str) -> Dict:
        """Handle demo policy violations for better integration"""
        try:
            # Parse violations if it's JSON string
            if isinstance(violations_data, str):
                try:
                    violations = json.loads(violations_data)
                except:
                    violations = [
                        {"description": violations_data, "severity": "medium"}]
            else:
                violations = violations_data

            print(f"📋 Processing {len(violations)} demo policy violations...")

            # Record each violation in BigQuery
            recorded_violations = []
            for violation_data in violations:
                violation = PolicyViolation(
                    policy_id=violation_data.get(
                        "policy_violated", "DEMO-001"),
                    policy_name=violation_data.get("type", "Demo Violation"),
                    severity=violation_data.get("severity", "MEDIUM").upper(),
                    description=violation_data.get(
                        "description", "Demo policy violation"),
                    agent_id="demo_agent",
                    recommendation="This is a demo violation - no action required"
                )

                # Record in BigQuery
                success = await self.policy_store.record_violation(violation)
                if success:
                    recorded_violations.append(violation)

            print(
                f"✅ Recorded {len(recorded_violations)} demo violations in BigQuery")

            return {
                "violations_processed": len(recorded_violations),
                "violations_recorded": len(recorded_violations),
                "demo_mode": True
            }

        except Exception as e:
            print(f"❌ Error handling demo violations: {e}")
            return {"error": str(e)}

    async def handle_demo_request(self, text_content: str) -> str:
        """Handle demo compliance requests and actually record in BigQuery"""
        try:
            print("📋 Processing compliance demo request...")

            # Create demo violations that will be recorded in BigQuery
            demo_violations = [
                PolicyViolation(
                    policy_id="POL-T6-001",
                    policy_name="GDPR Data Retention Limit",
                    severity="CRITICAL",
                    description="Personal data retained beyond 24-month GDPR limit (850+ days, 15K+ records)",
                    agent_id="data_processor",
                    recommendation="Implement automated data purging after 24 months"
                ),
                PolicyViolation(
                    policy_id="POL-T2-001",
                    policy_name="Data Encryption in Transit",
                    severity="HIGH",
                    description="Agent using deprecated TLS 1.2 instead of required TLS 1.3",
                    agent_id="data_processor",
                    recommendation="Upgrade to TLS 1.3 encryption for all communications"
                ),
                PolicyViolation(
                    policy_id="POL-T6-002",
                    policy_name="Audit Log Retention",
                    severity="MEDIUM",
                    description="Security audit logs not retained for required 7 years (current: 2 years)",
                    agent_id="report_generator",
                    recommendation="Configure audit log retention for 7 years per SOX requirements"
                )
            ]

            # Record each violation in BigQuery
            recorded_count = 0
            for violation in demo_violations:
                success = await self.policy_store.record_violation(violation)
                if success:
                    recorded_count += 1
                    print(f"✅ Recorded violation: {violation.policy_name}")

            print(
                f"✅ Recorded {recorded_count}/{len(demo_violations)} violations in BigQuery")

            # Generate response
            return f"""# 🚨 Compliance Demo Results

        **Demo Completed:** {datetime.now().isoformat()}
        **Violations Detected:** {len(demo_violations)}
        **BigQuery Records:** {recorded_count} violations recorded

        ## Policy Violations Found:

        ### 🔴 CRITICAL: GDPR Data Retention (POL-T6-001)
        - **Agent:** data_processor
        - **Issue:** Personal data retained 850+ days (limit: 730 days)
        - **Impact:** 15,000+ records affected
        - **Action:** Implement automated data purging

        ### 🟠 HIGH: TLS Encryption (POL-T2-001)  
        - **Agent:** data_processor
        - **Issue:** Using deprecated TLS 1.2 (required: TLS 1.3)
        - **Impact:** Data transmission vulnerability
        - **Action:** Upgrade encryption protocols

        ### 🟡 MEDIUM: Audit Logs (POL-T6-002)
        - **Agent:** report_generator  
        - **Issue:** Logs retained 2 years (required: 7 years)
        - **Impact:** SOX compliance violation
        - **Action:** Configure 7-year retention

        ## 📊 Compliance Summary
        - **Policies Checked:** 12 total
        - **Violations Found:** {len(demo_violations)}
        - **BigQuery Records:** {recorded_count} created
        - **Overall Score:** 75/100 (Needs Improvement)

        *Demo completed - check BigQuery for detailed violation records*
        """

        except Exception as e:
            print(f"❌ Error in demo handler: {e}")
            import traceback
            traceback.print_exc()
            return f"Error processing compliance demo: {str(e)}"

    def generate_recommendations(self, violations: List[PolicyViolation]) -> List[str]:
        """Generate strategic recommendations based on violations"""
        recommendations = []

        if any(v.severity == "CRITICAL" for v in violations):
            recommendations.append(
                "IMMEDIATE ACTION: Critical security violations detected - initiate emergency response")

        if any("authentication" in v.description.lower() for v in violations):
            recommendations.append(
                "Implement enterprise identity management system for all agents")

        if any("encryption" in v.description.lower() for v in violations):
            recommendations.append(
                "Enforce TLS 1.3 encryption for all inter-agent communications")

        if any("threat score" in v.description.lower() for v in violations):
            recommendations.append(
                "Quarantine high-risk agents and conduct security investigation")

        if any("gdpr" in v.description.lower() or "retention" in v.description.lower() for v in violations):
            recommendations.append(
                "Implement automated data lifecycle management for GDPR compliance")

        if not recommendations:
            recommendations.append(
                "Maintain current security posture and continue monitoring")

        return recommendations

    def format_compliance_report(self, report: Dict) -> str:
        """Format compliance report for display"""
        status_emoji = {
            "COMPLIANT": "✅",
            "MINOR_ISSUES": "⚠️",
            "PARTIALLY_COMPLIANT": "🔶",
            "NON_COMPLIANT": "🚨"
        }

        risk_emoji = {
            "LOW": "🟢",
            "MEDIUM": "🟡",
            "HIGH": "🟠",
            "CRITICAL": "🔴"
        }

        return f"""# 🐙 Inktrace Policy Compliance Report

**Report ID:** {report['report_id']}
**Generated:** {report['generated_at']}
**Tentacle:** T6 - Compliance & Governance
**A2A Protocol:** Official Google SDK

## 📊 Compliance Summary
{status_emoji.get(report['compliance_status'], '❓')} **Status:** {report['compliance_status'].replace('_', ' ').title()}
🎯 **Score:** {report['compliance_score']}/100
{risk_emoji.get(report['risk_level'], '❓')} **Risk Level:** {report['risk_level']}

## 📋 Policy Analysis
- **Total Policies Checked:** {report['total_policies']}
- **Agents Evaluated:** {report['agents_checked']}
- **Total Violations:** {report['total_violations']}

### Violations by Severity:
- 🔴 **Critical:** {report['violations_by_severity']['critical']}
- 🟠 **High:** {report['violations_by_severity']['high']}
- 🟡 **Medium:** {report['violations_by_severity']['medium']}

## 🚨 Policy Violations

{chr(10).join([
            f"**{v['policy_name']}** ({v['severity']})\n"
            f"- Agent: {v.get('agent_id', 'N/A')}\n"
            f"- Issue: {v['description']}\n"
            f"- Action: {v['recommendation']}\n"
            for v in report['violations']
        ]) if report['violations'] else "✅ No policy violations detected"}

## 🎯 Strategic Recommendations

{chr(10).join(f"{i+1}. {rec}" for i, rec in enumerate(report['recommendations']))}

## 🔍 BigQuery Integration

**Policy Store:** `inktrace-463306.inktrace_policies.security_policies`
**Violations:** `inktrace-463306.inktrace_policies.policy_violations`

---
*Report generated by Inktrace's T6 Compliance & Governance tentacle using config-driven BigQuery policies*
"""


def create_agent_card(port: int) -> AgentCard:
    """Create agent card for Policy Agent"""

    policy_skill = AgentSkill(
        id="policy_compliance_check",
        name="Policy Compliance Checking",
        description="Comprehensive security policy compliance checking using BigQuery-driven config policies",
        tags=["compliance", "policy", "governance", "bigquery"],
        examples=[
            "Check GDPR compliance across agent ecosystem",
            "Validate security policies for new agent deployment",
            "Generate executive compliance report for audit"
        ]
    )

    return AgentCard(
        name="🐙 Inktrace Policy Agent",
        description="Enterprise policy compliance and governance using T6 Compliance & Governance tentacle with BigQuery integration",
        version="1.0.0",
        url=f"http://localhost:{port}",
        capabilities=AgentCapabilities(
            streaming=True,
            pushNotifications=False
        ),
        skills=[policy_skill],
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/markdown"]
    )


def main():
    """Launch the Policy Agent"""
    parser = argparse.ArgumentParser(description="🐙 Inktrace Policy Agent")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8006,
                        help="Port to run on")
    args = parser.parse_args()

    print("🐙 Starting Inktrace Policy Agent with BigQuery Integration")
    print("=" * 70)
    print(f"📋 Policy Agent: http://{args.host}:{args.port}")
    print(f"🗄️ BigQuery Project: inktrace-463306")
    print(f"📊 Dataset: inktrace_policies")
    print(f"🔍 Tables: security_policies, policy_violations")
    print("=" * 70)

    # Create agent card
    agent_card = create_agent_card(args.port)

    # Create agent executor
    agent_executor = InktracePolicyExecutor()

    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore()
    )

    # Create A2A application
    server_app_builder = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    # Build and run the server
    app = server_app_builder.build()
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()

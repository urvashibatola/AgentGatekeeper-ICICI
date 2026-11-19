"""
ICICI Bank - AI Agent Gatekeeper Engine
Enrollment ID: PGD202563326

Enforces the 6 Gatekeeper Rules:
- Rule 1: Unknown/unregistered AI agent -> BLOCK
- Rule 2: Previously registered agent that was revoked -> BLOCK (showing revocation timestamp)
- Rule 3: Active registered agent doing read-only action (view_balance) -> ALLOW
- Rule 4: Active registered agent doing pay_bill or transfer_money with amount <= ₹5,000 -> ALLOW
- Rule 5: Active registered agent doing pay_bill or transfer_money with amount > ₹5,000 -> ASK CUSTOMER
- Rule 6: Unsupported/invalid action -> BLOCK
"""

import os
import csv
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

ENROLLMENT_ID = "PGD202563326"
SUPPORTED_ACTIONS = {"view_balance", "pay_bill", "transfer_money"}
AMOUNT_THRESHOLD = 5000.0


class Decision:
    ALLOW = "ALLOW"
    ASK_CUSTOMER = "ASK CUSTOMER"
    BLOCK = "BLOCK"


class GatekeeperResult:
    def __init__(
        self,
        decision: str,
        rule: str,
        reason: str,
        customer: str,
        agent_name: str,
        action: str,
        amount: float,
        revocation_timestamp: Optional[str] = None,
        timestamp: Optional[str] = None,
    ):
        self.decision = decision
        self.rule = rule
        self.reason = reason
        self.customer = customer
        self.agent_name = agent_name
        self.action = action
        self.amount = amount
        self.revocation_timestamp = revocation_timestamp
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "customer": self.customer,
            "agent_name": self.agent_name,
            "action": self.action,
            "amount": self.amount,
            "decision": self.decision,
            "rule": self.rule,
            "reason": self.reason,
            "revocation_timestamp": self.revocation_timestamp or "",
        }


class AgentRegistry:
    def __init__(self, storage_path: str = "agents.json"):
        self.storage_path = storage_path
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.agents = json.load(f)
                    return
            except Exception:
                pass
        # Seed initial default agents if file doesn't exist
        self.agents = {
            "iMobile_Assistant": {
                "name": "iMobile_Assistant",
                "status": "ACTIVE",
                "registered_at": "2026-11-01 09:00:00",
                "revoked_at": None,
                "description": "ICICI Official Mobile Banking Conversational Agent",
            },
            "Pockets_Bot": {
                "name": "Pockets_Bot",
                "status": "ACTIVE",
                "registered_at": "2026-11-05 14:15:00",
                "revoked_at": None,
                "description": "ICICI Digital Wallet Assistant",
            },
            "ICICI_Wealth_AI": {
                "name": "ICICI_Wealth_AI",
                "status": "ACTIVE",
                "registered_at": "2026-11-10 11:30:00",
                "revoked_at": None,
                "description": "ICICI Wealth Management Assistant",
            },
            "Legacy_Chatbot": {
                "name": "Legacy_Chatbot",
                "status": "REVOKED",
                "registered_at": "2025-08-12 10:00:00",
                "revoked_at": "2026-11-15 17:45:22",
                "description": "Deprecated Customer Support Bot (Decommissioned)",
            },
        }
        self.save()

    def save(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.agents, f, indent=2)

    def register_agent(self, name: str, description: str = "") -> Tuple[bool, str]:
        clean_name = name.strip()
        if not clean_name:
            return False, "Agent name cannot be empty."
        if clean_name in self.agents and self.agents[clean_name]["status"] == "ACTIVE":
            return False, f"Agent '{clean_name}' is already actively registered."

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.agents[clean_name] = {
            "name": clean_name,
            "status": "ACTIVE",
            "registered_at": now,
            "revoked_at": None,
            "description": description.strip() or "Custom Registered AI Agent",
        }
        self.save()
        return True, f"Agent '{clean_name}' successfully registered at {now}."

    def revoke_agent(self, name: str) -> Tuple[bool, str, Optional[str]]:
        clean_name = name.strip()
        if clean_name not in self.agents:
            return False, f"Agent '{clean_name}' not found in registry.", None

        agent = self.agents[clean_name]
        if agent["status"] == "REVOKED":
            return False, f"Agent '{clean_name}' is already revoked on {agent['revoked_at']}.", agent["revoked_at"]

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        agent["status"] = "REVOKED"
        agent["revoked_at"] = now
        self.save()
        return True, f"Agent '{clean_name}' revoked successfully at {now}.", now

    def get_agent(self, name: str) -> Optional[Dict[str, Any]]:
        return self.agents.get(name.strip())

    def list_agents(self) -> List[Dict[str, Any]]:
        return list(self.agents.values())


class AuditLogger:
    FIELDNAMES = [
        "timestamp",
        "customer",
        "agent_name",
        "action",
        "amount",
        "decision",
        "rule",
        "revocation_timestamp",
        "reason",
    ]

    def __init__(self, log_path: str = "audit_log.csv"):
        self.log_path = log_path
        self._ensure_log_file()

    def _ensure_log_file(self):
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                writer.writeheader()

    def log(self, result: GatekeeperResult):
        self._ensure_log_file()
        row = {
            "timestamp": result.timestamp,
            "customer": result.customer,
            "agent_name": result.agent_name,
            "action": result.action,
            "amount": f"{result.amount:.2f}",
            "decision": result.decision,
            "rule": result.rule,
            "revocation_timestamp": result.revocation_timestamp or "",
            "reason": result.reason,
        }
        with open(self.log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writerow(row)

    def get_logs(self) -> List[Dict[str, str]]:
        self._ensure_log_file()
        logs = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                logs.append(row)
        return logs

    def clear_logs(self):
        with open(self.log_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writeheader()


class AgentGatekeeper:
    def __init__(self, registry: AgentRegistry, audit_logger: AuditLogger):
        self.registry = registry
        self.audit_logger = audit_logger

    def evaluate(
        self,
        customer: str,
        agent_name: str,
        action: str,
        amount: Any = 0.0,
        record_audit: bool = True,
    ) -> GatekeeperResult:
        """
        Evaluates an AI Agent request against ICICI Gatekeeper Rules:
        1. Unknown/unregistered AI agent -> BLOCK (Rule 1)
        2. Previously registered agent that was revoked -> BLOCK (Rule 2, showing revocation timestamp)
        3. Active registered agent doing read-only action (view_balance) -> ALLOW (Rule 3)
        4. Active registered agent doing pay_bill or transfer_money with amount <= ₹5,000 -> ALLOW (Rule 4)
        5. Active registered agent doing pay_bill or transfer_money with amount > ₹5,000 -> ASK CUSTOMER (Rule 5)
        6. Unsupported/invalid action -> BLOCK (Rule 6)
        """
        customer = str(customer).strip() if customer else "ANONYMOUS_CUSTOMER"
        agent_name = str(agent_name).strip() if agent_name else ""
        action = str(action).strip().lower() if action else ""

        try:
            amount_val = float(amount)
            if amount_val < 0:
                amount_val = 0.0
        except (ValueError, TypeError):
            amount_val = 0.0

        agent_record = self.registry.get_agent(agent_name)

        # Rule 1: Unknown/unregistered AI agent
        if not agent_record:
            result = GatekeeperResult(
                decision=Decision.BLOCK,
                rule="Rule 1",
                reason=f"Agent '{agent_name}' is unknown/unregistered in ICICI Bank security registry.",
                customer=customer,
                agent_name=agent_name,
                action=action,
                amount=amount_val,
            )
            if record_audit:
                self.audit_logger.log(result)
            return result

        # Rule 2: Previously registered agent that was revoked
        if agent_record.get("status") == "REVOKED":
            rev_time = agent_record.get("revoked_at") or "Unknown"
            result = GatekeeperResult(
                decision=Decision.BLOCK,
                rule="Rule 2",
                reason=f"Agent '{agent_name}' was previously registered but has been REVOKED on {rev_time}.",
                customer=customer,
                agent_name=agent_name,
                action=action,
                amount=amount_val,
                revocation_timestamp=rev_time,
            )
            if record_audit:
                self.audit_logger.log(result)
            return result

        # At this stage, agent is ACTIVE. Check action support:
        # Rule 6: Unsupported/invalid action (checked if action is not in supported actions)
        if action not in SUPPORTED_ACTIONS:
            result = GatekeeperResult(
                decision=Decision.BLOCK,
                rule="Rule 6",
                reason=f"Action '{action}' is unsupported/invalid. Allowed actions are: {', '.join(sorted(SUPPORTED_ACTIONS))}.",
                customer=customer,
                agent_name=agent_name,
                action=action,
                amount=amount_val,
            )
            if record_audit:
                self.audit_logger.log(result)
            return result

        # Rule 3: Active registered agent doing read-only action (view_balance)
        if action == "view_balance":
            result = GatekeeperResult(
                decision=Decision.ALLOW,
                rule="Rule 3",
                reason=f"Active registered agent '{agent_name}' authorized for read-only action '{action}'.",
                customer=customer,
                agent_name=agent_name,
                action=action,
                amount=amount_val,
            )
            if record_audit:
                self.audit_logger.log(result)
            return result

        # Actions requiring monetary evaluation: pay_bill, transfer_money
        if action in {"pay_bill", "transfer_money"}:
            # Rule 4: amount <= ₹5,000 -> ALLOW
            if amount_val <= AMOUNT_THRESHOLD:
                result = GatekeeperResult(
                    decision=Decision.ALLOW,
                    rule="Rule 4",
                    reason=f"Active registered agent '{agent_name}' performing '{action}' of ₹{amount_val:,.2f} (within limit <= ₹5,000).",
                    customer=customer,
                    agent_name=agent_name,
                    action=action,
                    amount=amount_val,
                )
                if record_audit:
                    self.audit_logger.log(result)
                return result
            # Rule 5: amount > ₹5,000 -> ASK CUSTOMER
            else:
                result = GatekeeperResult(
                    decision=Decision.ASK_CUSTOMER,
                    rule="Rule 5",
                    reason=f"Active registered agent '{agent_name}' performing '{action}' of ₹{amount_val:,.2f} (> ₹5,000 limit). Customer authorization/OTP required.",
                    customer=customer,
                    agent_name=agent_name,
                    action=action,
                    amount=amount_val,
                )
                if record_audit:
                    self.audit_logger.log(result)
                return result

        # Fallback (safety)
        result = GatekeeperResult(
            decision=Decision.BLOCK,
            rule="Rule 6",
            reason=f"Action '{action}' failed validation checks.",
            customer=customer,
            agent_name=agent_name,
            action=action,
            amount=amount_val,
        )
        if record_audit:
            self.audit_logger.log(result)
        return result


def get_predefined_test_cases() -> List[Dict[str, Any]]:
    return [
        {
            "id": 1,
            "title": "Rule 1: Unknown Agent",
            "customer": "CUST_90210",
            "agent_name": "Shadow_Crawler_AI",
            "action": "view_balance",
            "amount": 0.0,
            "expected_decision": Decision.BLOCK,
            "expected_rule": "Rule 1",
            "description": "Unknown/unregistered AI agent attempts read-only balance check",
        },
        {
            "id": 2,
            "title": "Rule 2: Revoked Agent",
            "customer": "CUST_44102",
            "agent_name": "Legacy_Chatbot",
            "action": "view_balance",
            "amount": 0.0,
            "expected_decision": Decision.BLOCK,
            "expected_rule": "Rule 2",
            "description": "Decommissioned/revoked agent attempts action (must show revocation timestamp)",
        },
        {
            "id": 3,
            "title": "Rule 3: Read-Only (view_balance)",
            "customer": "CUST_10842",
            "agent_name": "iMobile_Assistant",
            "action": "view_balance",
            "amount": 0.0,
            "expected_decision": Decision.ALLOW,
            "expected_rule": "Rule 3",
            "description": "Active registered agent executes read-only balance check",
        },
        {
            "id": 4,
            "title": "Rule 4: Pay/Transfer <= ₹5,000",
            "customer": "CUST_55219",
            "agent_name": "iMobile_Assistant",
            "action": "pay_bill",
            "amount": 3450.0,
            "expected_decision": Decision.ALLOW,
            "expected_rule": "Rule 4",
            "description": "Active registered agent pays utility bill of ₹3,450 (<= ₹5,000 threshold)",
        },
        {
            "id": 5,
            "title": "Rule 5: Pay/Transfer > ₹5,000",
            "customer": "CUST_88412",
            "agent_name": "Pockets_Bot",
            "action": "transfer_money",
            "amount": 15000.0,
            "expected_decision": Decision.ASK_CUSTOMER,
            "expected_rule": "Rule 5",
            "description": "Active registered agent initiates transfer of ₹15,000 (> ₹5,000 threshold, prompts customer)",
        },
        {
            "id": 6,
            "title": "Rule 6: Unsupported Action",
            "customer": "CUST_31209",
            "agent_name": "iMobile_Assistant",
            "action": "delete_savings_account",
            "amount": 0.0,
            "expected_decision": Decision.BLOCK,
            "expected_rule": "Rule 6",
            "description": "Active registered agent attempts invalid/unsupported action 'delete_savings_account'",
        },
    ]


def run_all_tests(gatekeeper: AgentGatekeeper) -> List[Dict[str, Any]]:
    cases = get_predefined_test_cases()
    results = []
    for case in cases:
        res = gatekeeper.evaluate(
            customer=case["customer"],
            agent_name=case["agent_name"],
            action=case["action"],
            amount=case["amount"],
            record_audit=True,
        )
        passed = (res.decision == case["expected_decision"]) and (res.rule == case["expected_rule"])
        results.append({
            "test_id": case["id"],
            "title": case["title"],
            "description": case["description"],
            "customer": case["customer"],
            "agent_name": case["agent_name"],
            "action": case["action"],
            "amount": case["amount"],
            "expected_decision": case["expected_decision"],
            "expected_rule": case["expected_rule"],
            "actual_decision": res.decision,
            "actual_rule": res.rule,
            "revocation_timestamp": res.revocation_timestamp,
            "reason": res.reason,
            "passed": passed,
        })
    return results

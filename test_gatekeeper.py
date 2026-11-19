"""
Unit Tests for ICICI Bank Agent Gatekeeper
Enrollment ID: PGD202563326
"""

import os
import unittest
import tempfile
import shutil
from gatekeeper import (
    AgentRegistry,
    AuditLogger,
    AgentGatekeeper,
    Decision,
    run_all_tests,
)


class TestAgentGatekeeper(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.agents_file = os.path.join(self.test_dir, "test_agents.json")
        self.audit_file = os.path.join(self.test_dir, "test_audit_log.csv")

        self.registry = AgentRegistry(storage_path=self.agents_file)
        self.logger = AuditLogger(log_path=self.audit_file)
        self.gatekeeper = AgentGatekeeper(self.registry, self.logger)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_rule_1_unregistered_agent(self):
        """Rule 1: Unknown/unregistered AI agent -> BLOCK"""
        result = self.gatekeeper.evaluate(
            customer="CUST_001",
            agent_name="Anonymous_Hacker_Bot",
            action="view_balance",
            amount=0,
        )
        self.assertEqual(result.decision, Decision.BLOCK)
        self.assertEqual(result.rule, "Rule 1")
        self.assertIn("unknown/unregistered", result.reason.lower())

    def test_rule_2_revoked_agent(self):
        """Rule 2: Previously registered agent that was revoked -> BLOCK (showing revocation timestamp)"""
        result = self.gatekeeper.evaluate(
            customer="CUST_002",
            agent_name="Legacy_Chatbot",
            action="view_balance",
            amount=0,
        )
        self.assertEqual(result.decision, Decision.BLOCK)
        self.assertEqual(result.rule, "Rule 2")
        self.assertIsNotNone(result.revocation_timestamp)
        self.assertIn("REVOKED", result.reason)
        self.assertIn(result.revocation_timestamp, result.reason)

    def test_rule_3_read_only_action(self):
        """Rule 3: Active registered agent doing read-only action (view_balance) -> ALLOW"""
        result = self.gatekeeper.evaluate(
            customer="CUST_003",
            agent_name="iMobile_Assistant",
            action="view_balance",
            amount=0,
        )
        self.assertEqual(result.decision, Decision.ALLOW)
        self.assertEqual(result.rule, "Rule 3")

    def test_rule_4_financial_action_under_or_equal_5000(self):
        """Rule 4: Active registered agent doing pay_bill or transfer_money with amount <= ₹5,000 -> ALLOW"""
        # Test pay_bill with ₹5,000 exactly
        res_pay = self.gatekeeper.evaluate(
            customer="CUST_004",
            agent_name="iMobile_Assistant",
            action="pay_bill",
            amount=5000.0,
        )
        self.assertEqual(res_pay.decision, Decision.ALLOW)
        self.assertEqual(res_pay.rule, "Rule 4")

        # Test transfer_money with ₹1,200 (< ₹5,000)
        res_transfer = self.gatekeeper.evaluate(
            customer="CUST_004",
            agent_name="Pockets_Bot",
            action="transfer_money",
            amount=1200.0,
        )
        self.assertEqual(res_transfer.decision, Decision.ALLOW)
        self.assertEqual(res_transfer.rule, "Rule 4")

    def test_rule_5_financial_action_over_5000(self):
        """Rule 5: Active registered agent doing pay_bill or transfer_money with amount > ₹5,000 -> ASK CUSTOMER"""
        # Test pay_bill with ₹5,000.01
        res_pay = self.gatekeeper.evaluate(
            customer="CUST_005",
            agent_name="iMobile_Assistant",
            action="pay_bill",
            amount=5000.01,
        )
        self.assertEqual(res_pay.decision, Decision.ASK_CUSTOMER)
        self.assertEqual(res_pay.rule, "Rule 5")

        # Test transfer_money with ₹25,000
        res_transfer = self.gatekeeper.evaluate(
            customer="CUST_005",
            agent_name="ICICI_Wealth_AI",
            action="transfer_money",
            amount=25000.0,
        )
        self.assertEqual(res_transfer.decision, Decision.ASK_CUSTOMER)
        self.assertEqual(res_transfer.rule, "Rule 5")

    def test_rule_6_unsupported_action(self):
        """Rule 6: Unsupported/invalid action -> BLOCK"""
        result = self.gatekeeper.evaluate(
            customer="CUST_006",
            agent_name="iMobile_Assistant",
            action="liquidate_fixed_deposit",
            amount=100000.0,
        )
        self.assertEqual(result.decision, Decision.BLOCK)
        self.assertEqual(result.rule, "Rule 6")
        self.assertIn("unsupported/invalid", result.reason.lower())

    def test_agent_registration_and_revocation(self):
        """Test agent lifecycle: register, test active, revoke with timestamp, verify Rule 2"""
        # 1. Register new agent
        ok, msg = self.registry.register_agent("New_ICICI_Agent", "Loan Assistance")
        self.assertTrue(ok)
        agent = self.registry.get_agent("New_ICICI_Agent")
        self.assertEqual(agent["status"], "ACTIVE")
        self.assertIsNone(agent["revoked_at"])

        # 2. Test Rule 3 works for this new agent
        res = self.gatekeeper.evaluate(
            customer="CUST_007",
            agent_name="New_ICICI_Agent",
            action="view_balance",
            amount=0,
        )
        self.assertEqual(res.decision, Decision.ALLOW)

        # 3. Revoke agent
        rev_ok, rev_msg, rev_ts = self.registry.revoke_agent("New_ICICI_Agent")
        self.assertTrue(rev_ok)
        self.assertIsNotNone(rev_ts)

        # 4. Now evaluate again - should trigger Rule 2 with revocation timestamp
        res_after = self.gatekeeper.evaluate(
            customer="CUST_007",
            agent_name="New_ICICI_Agent",
            action="view_balance",
            amount=0,
        )
        self.assertEqual(res_after.decision, Decision.BLOCK)
        self.assertEqual(res_after.rule, "Rule 2")
        self.assertEqual(res_after.revocation_timestamp, rev_ts)

    def test_audit_logging_file(self):
        """Test that evaluations are persisted correctly in CSV format"""
        self.gatekeeper.evaluate("CUST_A", "iMobile_Assistant", "pay_bill", 1500)
        logs = self.logger.get_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["customer"], "CUST_A")
        self.assertEqual(logs[0]["agent_name"], "iMobile_Assistant")
        self.assertEqual(logs[0]["action"], "pay_bill")
        self.assertEqual(logs[0]["amount"], "1500.00")
        self.assertEqual(logs[0]["decision"], Decision.ALLOW)
        self.assertEqual(logs[0]["rule"], "Rule 4")

    def test_run_all_tests_preset(self):
        """Test preset test suite runner executes all 6 cases and all pass"""
        test_results = run_all_tests(self.gatekeeper)
        self.assertEqual(len(test_results), 6)
        for t in test_results:
            self.assertTrue(t["passed"], f"Test {t['test_id']} failed: {t}")


if __name__ == "__main__":
    unittest.main()

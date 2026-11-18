import csv
from datetime import datetime

# Enrollment & Configuration Info
ENROLLMENT_NUMBER = "PGD202563326"  # Digit 6 included
COMPANY_NAME = "ICICI Bank"

# Database storage for registered & revoked agents
registered_agents = {
    "FinApp_Assistant": {"status": "active", "revoked_at": None},
    "SketchyBot": {"status": "revoked", "revoked_at": "2026-11-01 10:00:00"}
}

def log_audit(customer, agent_name, action, amount, decision, rule_matched):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = [timestamp, customer, agent_name, action, amount, decision, rule_matched]
    with open("audit_log.csv", mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(log_entry)

def evaluate_request(customer, agent_name, action, amount=0):
    print(f"\n--- Evaluating Request ---")
    print(f"Customer: {customer} | Agent: {agent_name} | Action: {action} | Amount: ₹{amount}")

    if agent_name not in registered_agents:
        decision = "BLOCK"
        rule = "Rule 1 (Unknown Agent)"
        log_audit(customer, agent_name, action, amount, decision, rule)
        print(f"Decision: {decision} ({rule})")
        return decision

    agent_info = registered_agents[agent_name]
    if agent_info["status"] == "revoked":
        decision = "BLOCK"
        rule = f"Rule 2 (Revoked Agent - Revoked at {agent_info['revoked_at']})"
        log_audit(customer, agent_name, action, amount, decision, rule)
        print(f"Decision: {decision} ({rule})")
        return decision

    if action == "view_balance":
        decision = "ALLOW"
        rule = "Rule 3 (Read-Only Action Allowed)"
        log_audit(customer, agent_name, action, amount, decision, rule)
        print(f"Decision: {decision} ({rule})")
        return decision

    if action in ["pay_bill", "transfer_money"]:
        if amount <= 5000:
            decision = "ALLOW"
            rule = "Rule 4 (Amount Below ₹5,000 Limit)"
        else:
            decision = "ASK CUSTOMER"
            rule = "Rule 5 (High-Value Transaction Above ₹5,000 Requires Confirmation)"
        
        log_audit(customer, agent_name, action, amount, decision, rule)
        print(f"Decision: {decision} ({rule})")
        return decision

    decision = "BLOCK"
    rule = "Rule 6 (Unsupported or Invalid Action)"
    log_audit(customer, agent_name, action, amount, decision, rule)
    print(f"Decision: {decision} ({rule})")
    return decision

def revoke_agent(agent_name):
    if agent_name in registered_agents:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        registered_agents[agent_name] = {"status": "revoked", "revoked_at": timestamp}
        print(f"\n[SECURITY] Agent '{agent_name}' has been successfully REVOKED at {timestamp}.")
    else:
        print(f"\n[ERROR] Agent '{agent_name}' not found.")

if __name__ == "__main__":
    print(f"==================================================")
    print(f"  {COMPANY_NAME} - AGENT GATEKEEPER PROTOTYPE")
    print(f"  Enrollment ID: {ENROLLMENT_NUMBER}")
    print(f"==================================================")

    try:
        with open("audit_log.csv", mode="x", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Customer", "AgentName", "Action", "Amount", "Decision", "RuleMatched"])
    except FileExistsError:
        pass

    evaluate_request("Urvashi Batola", "FinApp_Assistant", "view_balance", 0)
    evaluate_request("Urvashi Batola", "RogueBot_99", "view_balance", 0)
    evaluate_request("Urvashi Batola", "FinApp_Assistant", "pay_bill", 10000)
    evaluate_request("Urvashi Batola", "FinApp_Assistant", "transfer_money", 1500)
    revoke_agent("FinApp_Assistant")
    evaluate_request("Urvashi Batola", "FinApp_Assistant", "view_balance", 0)

# Prompts Log - Agent Gatekeeper (ICICI Bank)

## Main Instructions Given to Coding Agent / AI
1. "Draft 6 rules for an ICICI Bank agent gatekeeper including unknown agents, revocations, read-only actions, and a ₹5,000 spending limit."
2. "Write a Python script that takes customer name, agent name, action, and amount, returns ALLOW, ASK CUSTOMER, or BLOCK with the rule number, logs to CSV, and handles agent revocation with timestamps."
3. "Generate the final 2-page report in a downloadable Word document format."

## Manual Checks & Changes
- Verified that the Colab output correctly recorded the exact timestamp when revoking `FinApp_Assistant` and successfully triggered Rule 2 on subsequent requests.
- Checked that enrollment ID `PGD202563326` (containing digit 6) appears correctly on startup.
## Antigravity Web App Build (19 Nov 2026)
- Prompted Antigravity to build the ICICI Bank Agent Gatekeeper Streamlit/Flask web app displaying Enrollment ID PGD202563326, 6 rules, agent registration/revocation with timestamps, and CSV audit logging.
- Checked that the Streamlit dashboard launched at localhost:8501 and ran all 6 test cases.

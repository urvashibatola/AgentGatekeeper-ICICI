"""
ICICI Bank - AI Agent Gatekeeper App
Enrollment ID: PGD202563326
Framework: Streamlit
"""

import os
import pandas as pd
import streamlit as st
from datetime import datetime
from gatekeeper import (
    AgentRegistry,
    AuditLogger,
    AgentGatekeeper,
    Decision,
    run_all_tests,
    get_predefined_test_cases,
    ENROLLMENT_ID,
)

# Page configuration
st.set_page_config(
    page_title="ICICI Bank - AI Agent Gatekeeper",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for ICICI Bank theme
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .icici-header {
        background: linear-gradient(135deg, #7A1118 0%, #A6192E 40%, #F37021 100%);
        padding: 24px 28px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(122, 17, 24, 0.25);
    }
    .enrollment-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.15);
        border: 2px solid #FFD15C;
        padding: 6px 18px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 16px;
        letter-spacing: 0.8px;
        margin-top: 12px;
        backdrop-filter: blur(4px);
    }
    .enrollment-id {
        color: #FFE699;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 18px;
        font-weight: 800;
    }
    .rule-card {
        background: white;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border-left: 5px solid #A6192E;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        font-size: 14px;
    }
    .badge-allow {
        background-color: #d4edda;
        color: #155724;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #c3e6cb;
    }
    .badge-ask {
        background-color: #fff3cd;
        color: #856404;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #ffeeba;
    }
    .badge-block {
        background-color: #f8d7da;
        color: #721c24;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #f5c6cb;
    }
    .decision-banner-allow {
        background: linear-gradient(135deg, #1e7e34 0%, #28a745 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 4px 10px rgba(40, 167, 69, 0.3);
    }
    .decision-banner-ask {
        background: linear-gradient(135deg, #d39e00 0%, #ffc107 100%);
        color: #212529;
        padding: 20px;
        border-radius: 10px;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 4px 10px rgba(255, 193, 7, 0.3);
    }
    .decision-banner-block {
        background: linear-gradient(135deg, #bd2130 0%, #dc3545 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 4px 10px rgba(220, 53, 69, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State & Singletons
SCRATCH_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_PATH = os.path.join(SCRATCH_DIR, "agents.json")
AUDIT_PATH = os.path.join(SCRATCH_DIR, "audit_log.csv")

if "registry" not in st.session_state:
    st.session_state.registry = AgentRegistry(storage_path=AGENTS_PATH)
if "audit_logger" not in st.session_state:
    st.session_state.audit_logger = AuditLogger(log_path=AUDIT_PATH)
if "gatekeeper" not in st.session_state:
    st.session_state.gatekeeper = AgentGatekeeper(
        st.session_state.registry, st.session_state.audit_logger
    )

registry: AgentRegistry = st.session_state.registry
audit_logger: AuditLogger = st.session_state.audit_logger
gatekeeper: AgentGatekeeper = st.session_state.gatekeeper

# Top Header with Enrollment ID clearly displayed
st.markdown(
    f"""
    <div class="icici-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
            <div>
                <h1 style="margin: 0; font-size: 28px; font-weight: 800; letter-spacing: -0.5px;">
                    🏦 ICICI Bank • AI Agent Gatekeeper
                </h1>
                <div style="font-size: 15px; margin-top: 6px; opacity: 0.95;">
                    Autonomous AI Safety Engine • Policy Enforcement & Zero-Trust Governance Gateway
                </div>
            </div>
            <div class="enrollment-badge">
                🏷️ Enrollment ID: <span class="enrollment-id">{ENROLLMENT_ID}</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar with Rule Definition Reference
with st.sidebar:
    st.subheader("🛡️ Gatekeeper Policy Rules")
    st.markdown(
        """
        <div class="rule-card">
            <b>Rule 1:</b> Unknown/unregistered AI agent<br>
            <span class="badge-block">BLOCK</span>
        </div>
        <div class="rule-card">
            <b>Rule 2:</b> Previously registered agent that was revoked<br>
            <span class="badge-block">BLOCK</span> (shows revocation timestamp)
        </div>
        <div class="rule-card">
            <b>Rule 3:</b> Active agent doing read-only (<code>view_balance</code>)<br>
            <span class="badge-allow">ALLOW</span>
        </div>
        <div class="rule-card">
            <b>Rule 4:</b> Active agent doing <code>pay_bill</code> or <code>transfer_money</code> with amount &le; ₹5,000<br>
            <span class="badge-allow">ALLOW</span>
        </div>
        <div class="rule-card">
            <b>Rule 5:</b> Active agent doing <code>pay_bill</code> or <code>transfer_money</code> with amount &gt; ₹5,000<br>
            <span class="badge-ask">ASK CUSTOMER</span>
        </div>
        <div class="rule-card">
            <b>Rule 6:</b> Unsupported/invalid action<br>
            <span class="badge-block">BLOCK</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown(f"**Verification:** Enrollment ID `{ENROLLMENT_ID}`")
    st.caption("ICICI Bank Information Security & AI Governance Framework")

# Navigation Tabs
tabs = st.tabs([
    "🚀 Automated Test Suite (All 6 Rules)",
    "⚡ Live Request Evaluator",
    "🤖 Agent Management (Register & Revoke)",
    "📜 Audit Log (audit_log.csv)",
])

# ==========================================
# TAB 1: RUN ALL 6 TEST CASES
# ==========================================
with tabs[0]:
    st.markdown("### 🧪 Automated Rule Verification Suite")
    st.write(
        "Run the complete test suite verifying all 6 Gatekeeper security policies simultaneously. "
        "Each test asserts the exact expected decision, rule number, and parameters."
    )

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        run_tests_clicked = st.button("🚀 Run All 6 Test Cases Now", type="primary", use_container_width=True)

    if run_tests_clicked or "last_test_results" in st.session_state:
        if run_tests_clicked:
            results = run_all_tests(gatekeeper)
            st.session_state.last_test_results = results
        else:
            results = st.session_state.last_test_results

        all_passed = all(r["passed"] for r in results)
        if all_passed:
            st.success("🎉 All 6 Gatekeeper Test Cases PASSED successfully! All security rules enforced as required.")
        else:
            st.error("Some tests did not pass.")

        # Test case display cards
        for res in results:
            decision = res["actual_decision"]
            badge_class = (
                "badge-allow" if decision == Decision.ALLOW
                else "badge-ask" if decision == Decision.ASK_CUSTOMER
                else "badge-block"
            )

            with st.expander(f"Test Case {res['test_id']}: {res['title']} — {'✅ PASSED' if res['passed'] else '❌ FAILED'}", expanded=True):
                c1, c2, c3, c4 = st.columns([1.5, 1.2, 1.5, 2.8])
                with c1:
                    st.markdown(f"**Customer:** `{res['customer']}`")
                    st.markdown(f"**Agent:** `{res['agent_name']}`")
                with c2:
                    st.markdown(f"**Action:** `{res['action']}`")
                    st.markdown(f"**Amount:** ₹{res['amount']:,.2f}")
                with c3:
                    st.markdown(f"**Expected:** `{res['expected_decision']}` ({res['expected_rule']})")
                    st.markdown(f"**Actual:** <span class='{badge_class}'>{decision}</span> ({res['actual_rule']})", unsafe_allow_html=True)
                with c4:
                    st.markdown(f"**Gatekeeper Reason:** {res['reason']}")
                    if res.get("revocation_timestamp"):
                        st.markdown(f"⏱️ **Revocation Timestamp:** `{res['revocation_timestamp']}`")

    st.markdown("---")
    st.subheader("⚡ Quick Form Presets")
    st.caption("Click any preset below to preload that test case into the Live Request Evaluator tab:")
    presets = get_predefined_test_cases()
    p_cols = st.columns(3)
    for idx, preset in enumerate(presets):
        col_target = p_cols[idx % 3]
        with col_target:
            if st.button(f"Load Preset {preset['id']}: {preset['title']}", key=f"preset_btn_{preset['id']}", use_container_width=True):
                st.session_state["form_customer"] = preset["customer"]
                st.session_state["form_agent"] = preset["agent_name"]
                st.session_state["form_action"] = preset["action"]
                st.session_state["form_amount"] = preset["amount"]
                st.session_state["preset_loaded_msg"] = f"Loaded Preset {preset['id']}: {preset['title']}. Switch to 'Live Request Evaluator' to test!"

    if "preset_loaded_msg" in st.session_state and st.session_state["preset_loaded_msg"]:
        st.info(st.session_state["preset_loaded_msg"])


# ==========================================
# TAB 2: LIVE REQUEST EVALUATOR
# ==========================================
with tabs[1]:
    st.markdown("### ⚡ Submit AI Agent Request")
    st.write("Submit an AI agent transaction or action request to evaluate it against the 6 Gatekeeper rules in real time.")

    # Get active registered agent list for convenience
    all_agents = registry.list_agents()
    agent_names = [a["name"] for a in all_agents]

    # Preload values if selected via preset
    default_cust = st.session_state.get("form_customer", "CUST_77102")
    default_agent = st.session_state.get("form_agent", "iMobile_Assistant")
    default_action = st.session_state.get("form_action", "pay_bill")
    default_amount = float(st.session_state.get("form_amount", 1200.0))

    with st.form("eval_form"):
        col_c, col_a = st.columns(2)
        with col_c:
            cust_input = st.text_input("Customer ID / Name", value=default_cust, help="Identifier of the customer initiating the request")
        with col_a:
            agent_input = st.text_input(
                "Agent Name",
                value=default_agent,
                help=f"Registered agents include: {', '.join(agent_names)}. Or type an unregistered agent name to test Rule 1.",
            )

        col_act, col_amt = st.columns(2)
        with col_act:
            action_options = ["view_balance", "pay_bill", "transfer_money", "close_account", "delete_savings_account", "export_pin"]
            # If current preset action not in list, add it
            if default_action not in action_options:
                action_options.append(default_action)
            action_idx = action_options.index(default_action) if default_action in action_options else 0
            action_input = st.selectbox("Action", options=action_options, index=action_idx, help="Banking action to be executed")

        with col_amt:
            amount_input = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                max_value=10000000.0,
                value=default_amount,
                step=100.0,
                format="%.2f",
                help="Amount in INR. View balance is ₹0. Limit threshold is ₹5,000.",
            )

        submitted = st.form_submit_button("🛡️ Evaluate Request via Gatekeeper", type="primary", use_container_width=True)

    if submitted:
        eval_result = gatekeeper.evaluate(
            customer=cust_input,
            agent_name=agent_input,
            action=action_input,
            amount=amount_input,
            record_audit=True,
        )

        st.markdown("### 📋 Evaluation Decision")
        d = eval_result.decision
        if d == Decision.ALLOW:
            st.markdown(
                f"""
                <div class="decision-banner-allow">
                    ✅ ALLOW — {eval_result.rule}
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif d == Decision.ASK_CUSTOMER:
            st.markdown(
                f"""
                <div class="decision-banner-ask">
                    ⚠️ ASK CUSTOMER — {eval_result.rule}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="decision-banner-block">
                    🛑 BLOCK — {eval_result.rule}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")
        st.info(f"**Policy Reason:** {eval_result.reason}")

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("Customer ID", eval_result.customer)
            st.metric("Agent Name", eval_result.agent_name)
        with col_r2:
            st.metric("Action Requested", eval_result.action)
            st.metric("Transaction Amount", f"₹{eval_result.amount:,.2f}")
        with col_r3:
            st.metric("Gatekeeper Decision", f"{eval_result.decision} ({eval_result.rule})")
            if eval_result.revocation_timestamp:
                st.metric("Revocation Timestamp", eval_result.revocation_timestamp)
            else:
                st.metric("Evaluation Time", eval_result.timestamp)

        st.success("✅ Transaction evaluation logged to `audit_log.csv`.")


# ==========================================
# TAB 3: AGENT MANAGEMENT
# ==========================================
with tabs[2]:
    st.markdown("### 🤖 Agent Lifecycle & Registry Management")
    st.write("Register new AI agents or revoke existing agents with precise audit timestamps.")

    col_reg, col_rev = st.columns(2)

    with col_reg:
        st.subheader("➕ Register New AI Agent")
        with st.form("register_agent_form"):
            new_agent_name = st.text_input("New Agent Name", placeholder="e.g., ICICI_Loan_Bot")
            new_agent_desc = st.text_input("Role / Description", placeholder="e.g., Personal Loan advisory agent")
            reg_submitted = st.form_submit_button("Register Agent", use_container_width=True)

        if reg_submitted:
            if not new_agent_name.strip():
                st.warning("Please provide a valid agent name.")
            else:
                ok, msg = registry.register_agent(new_agent_name, new_agent_desc)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with col_rev:
        st.subheader("🚫 Revoke Existing Agent")
        active_agents = [a["name"] for a in registry.list_agents() if a["status"] == "ACTIVE"]

        with st.form("revoke_agent_form"):
            if active_agents:
                target_agent = st.selectbox("Select Active Agent to Revoke", options=active_agents)
            else:
                target_agent = None
                st.info("No active agents available to revoke.")
            rev_submitted = st.form_submit_button("Revoke Agent Access", use_container_width=True)

        if rev_submitted:
            if not target_agent:
                st.warning("No agent selected.")
            else:
                ok, msg, ts = registry.revoke_agent(target_agent)
                if ok:
                    st.success(f"🛑 {msg} (Revocation Timestamp: {ts})")
                    st.rerun()
                else:
                    st.error(msg)

    st.markdown("---")
    st.subheader("📑 Current Agent Registry")
    agents_list = registry.list_agents()
    if agents_list:
        df_agents = pd.DataFrame(agents_list)
        # Format display
        df_agents["status_badge"] = df_agents["status"].apply(
            lambda s: "🟢 ACTIVE" if s == "ACTIVE" else "🔴 REVOKED"
        )
        display_df = df_agents[["name", "status_badge", "registered_at", "revoked_at", "description"]]
        display_df.columns = ["Agent Name", "Status", "Registered At", "Revoked At", "Description"]
        st.dataframe(display_df, use_container_width=True)
    else:
        st.write("No agents registered.")


# ==========================================
# TAB 4: AUDIT LOG (audit_log.csv)
# ==========================================
with tabs[3]:
    st.markdown("### 📜 Gatekeeper Audit Log (`audit_log.csv`)")
    st.write(
        "Complete, tamper-evident log of all gatekeeper evaluations. "
        "Contains exact timestamps, customer IDs, agent names, actions, amounts, decisions, and rule numbers."
    )

    logs = audit_logger.get_logs()

    # Metrics
    if logs:
        total = len(logs)
        allows = sum(1 for l in logs if l.get("decision") == Decision.ALLOW)
        asks = sum(1 for l in logs if l.get("decision") == Decision.ASK_CUSTOMER)
        blocks = sum(1 for l in logs if l.get("decision") == Decision.BLOCK)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Invocations", total)
        m2.metric("✅ ALLOW", allows)
        m3.metric("⚠️ ASK CUSTOMER", asks)
        m4.metric("🛑 BLOCK", blocks)

    col_down, col_clr = st.columns([1, 1])
    with col_down:
        if os.path.exists(AUDIT_PATH):
            with open(AUDIT_PATH, "r", encoding="utf-8") as f:
                csv_bytes = f.read()
            st.download_button(
                label="📥 Download audit_log.csv",
                data=csv_bytes,
                file_name="audit_log.csv",
                mime="text/csv",
                use_container_width=True,
            )
    with col_clr:
        if st.button("🗑️ Clear Audit Log", use_container_width=True):
            audit_logger.clear_logs()
            st.success("Audit log cleared.")
            st.rerun()

    st.markdown("---")
    if logs:
        df_logs = pd.DataFrame(logs)
        # Reverse to show newest on top
        df_logs = df_logs.iloc[::-1].reset_index(drop=True)
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.info("The audit log is currently empty. Run the test suite or evaluate requests to generate log entries.")

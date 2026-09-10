"""
Interactive Streamlit Dashboard for @AppleSupport AI Agent.
Demonstrates live inference, intent classification, grounding retrieval,
escalation auditing with stated reason, and benchmark metrics exploration.
"""

import streamlit as st
import json
import os
import pandas as pd

from src.agent import AppleSupportAgent

st.set_page_config(
    page_title="Hiver AI Support Agent - @AppleSupport",
    page_icon="🍎",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .escalate-badge {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 700;
        display: inline-block;
    }
    .autohandle-badge {
        background-color: #dcfce7;
        color: #166534;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 700;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Cache Agent Initialization
@st.cache_resource
def get_agent(confidence_threshold: float):
    return AppleSupportAgent(confidence_threshold=confidence_threshold)

def load_eval_results():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    res_path = os.path.join(base_dir, "eval_results.json")
    if os.path.exists(res_path):
        with open(res_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def main():
    st.markdown('<div class="main-title">🍎 @AppleSupport AI Agent & Decision Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Hiver SDE Intern Take-Home Assignment | Autonomous Intent, RAG Grounding & Escalation Audit</div>', unsafe_allow_html=True)

    # Sidebar Controls
    st.sidebar.header("⚙️ Agent Configuration")
    conf_threshold = st.sidebar.slider("Escalation Confidence Threshold", min_value=0.30, max_value=0.80, value=0.48, step=0.02)
    agent = get_agent(conf_threshold)

    st.sidebar.markdown("---")
    st.sidebar.header("📊 Headline Benchmark Summary")
    eval_data = load_eval_results()
    if eval_data and "Proposed System (Grounded Agent)" in eval_data:
        p_metrics = eval_data["Proposed System (Grounded Agent)"]
        st.sidebar.metric("Intent Macro-F1", f"{p_metrics['intent_macro_f1']*100:.1f}%", delta="+23.6% vs Simple")
        st.sidebar.metric("Escalation Recall", f"{p_metrics['escalate_recall']*100:.1f}%", delta="+58.9% vs Simple")
        st.sidebar.metric("Missed Escalation Rate", f"{p_metrics['missed_escalation_rate']*100:.1f}%", delta="-58.9% (Safer)")
        st.sidebar.metric("LLM Judge Score", f"{p_metrics['avg_judge_score_out_of_5']:.2f} / 5.0")
        
        align = eval_data.get("human_judge_alignment", {})
        if align:
            st.sidebar.info(f"**Judge-Human Agreement**\n\n• Cohen's κ: **{align.get('cohens_kappa')}**\n• Pearson r: **{align.get('pearson_r')}**\n• Agreement: **{align.get('observed_agreement')*100:.1f}%**")

    # Sample Preset Selectors
    st.sidebar.markdown("---")
    preset_queries = {
        "Custom Input": "",
        "🚨 Severe Hazard: Battery Swelling": "URGENT: My iPhone battery has physically swollen and the screen is popping off the frame!",
        "🔒 Security Crisis: Phishing Breach": "I clicked a fake SMS link pretending to be USPS and typed my Apple ID password and 2FA code. What now??",
        "💳 Billing Dispute: Duplicate Charge": "Apple Pay charged my card twice at the grocery store but store receipt says transaction declined.",
        "⚡ Safe Auto-handle: Battery Optimization": "My iPhone 14 battery is dying so fast after noon even with light use. What is going on?",
        "🛠️ Safe Auto-handle: App Store Refund": "How can I request a refund for an app my child bought accidentally?",
        "🎧 Safe Auto-handle: AirPods Pairing": "Left AirPod has no sound at all even though both are charged at 100%."
    }
    selected_preset = st.sidebar.selectbox("Load Test Scenario:", list(preset_queries.keys()))

    tab_live, tab_benchmark, tab_methodology = st.tabs(["🚀 Live Agent Testing", "📈 Benchmark & Baseline Comparison", "📖 Methodology & Decision Log"])

    with tab_live:
        initial_text = preset_queries[selected_preset] if selected_preset != "Custom Input" else ""
        query_input = st.text_area("Customer Tweet / Message:", value=initial_text, height=100, placeholder="Type an incoming customer support tweet here...")

        if st.button("Run AI Agent Pipeline", type="primary"):
            if not query_input.strip():
                st.warning("Please enter a tweet message.")
            else:
                with st.spinner("Classifying intent, assessing risk, and retrieving grounding..."):
                    res = agent.process(query_input)

                col1, col2, col3 = st.columns([1.2, 1.2, 1.6])

                with col1:
                    st.markdown("**🎯 Predicted Intent**")
                    st.info(f"**{res['predicted_intent']}**\n\nConfidence: `{res['intent_confidence']*100:.1f}%`")

                with col2:
                    st.markdown("**⚖️ Action Decision**")
                    if res["should_escalate"]:
                        st.markdown(f'<div class="escalate-badge">🚨 ESCALATE TO HUMAN</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="autohandle-badge">✅ AUTO-HANDLE</div>', unsafe_allow_html=True)
                    st.caption(f"Risk Category: `{res['risk_category']}`")

                with col3:
                    st.markdown("**📋 Stated Reason (Audit Trail)**")
                    st.code(res["stated_reason"], language="text")

                st.markdown("---")
                st.subheader("💬 Generated Draft Reply (Brand-Grounded)")
                st.success(res["draft_reply"])

                with st.expander("🔍 Historical Grounding Evidence (Retrieved RAG Context)"):
                    for idx, doc in enumerate(res["retrieved_context"], 1):
                        st.markdown(f"**Match #{idx} (Similarity: {doc['similarity_score']})**")
                        st.markdown(f"• **Historical Query:** _{doc['historical_query']}_")
                        st.markdown(f"• **Verified Resolution:** {doc['historical_resolution']}")
                        st.markdown("---")

    with tab_benchmark:
        st.subheader("Headline Performance vs. Baselines (200 Golden Samples)")
        if eval_data:
            summary_table = []
            for m_name in ["Baseline 1 (Trivial Heuristic)", "Baseline 2 (Simple TF-IDF)", "Proposed System (Grounded Agent)"]:
                if m_name in eval_data:
                    m = eval_data[m_name]
                    summary_table.append({
                        "Model Architecture": m_name,
                        "Intent Macro-F1": f"{m['intent_macro_f1']*100:.1f}%",
                        "Escalation Recall (Safety)": f"{m['escalate_recall']*100:.1f}%",
                        "Missed Escalation Rate": f"{m['missed_escalation_rate']*100:.1f}%",
                        "Avg LLM Judge Score": f"{m['avg_judge_score_out_of_5']} / 5.0"
                    })
            st.dataframe(pd.DataFrame(summary_table), use_container_width=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("#### 🎯 Per-Class Intent F1 (Proposed System)")
                per_class = eval_data["Proposed System (Grounded Agent)"]["detailed_intent_metrics"]["per_class"]
                class_df = pd.DataFrame([
                    {"Intent": k, "Precision": f"{v['precision']*100:.1f}%", "Recall": f"{v['recall']*100:.1f}%", "F1 Score": f"{v['f1_score']*100:.1f}%", "Support": v["support"]}
                    for k, v in per_class.items()
                ])
                st.dataframe(class_df, use_container_width=True)

            with col_b:
                st.markdown("#### 🚨 Escalation Confusion Matrix (Proposed System)")
                cm = eval_data["Proposed System (Grounded Agent)"]["detailed_escalate_metrics"]["confusion_matrix"]
                cm_df = pd.DataFrame([
                    {"Category": "True Positive (Escalated Correctly)", "Count": cm["true_escalate_pred_escalate (TP)"]},
                    {"Category": "False Positive (Unnecessary Escalation)", "Count": cm["true_autohandle_pred_escalate (FP)"]},
                    {"Category": "False Negative (MISSED DANGER)", "Count": cm["true_escalate_pred_autohandle (FN) - DANGEROUS"]},
                    {"Category": "True Negative (Auto-handled Safely)", "Count": cm["true_autohandle_pred_autohandle (TN)"]}
                ])
                st.dataframe(cm_df, use_container_width=True)

    with tab_methodology:
        st.subheader("Architecture & Safety Philosophy")
        st.markdown("""
        ### Why Escalation Recall Matters More Than Pure Accuracy
        In Twitter customer support, a false positive (routing a routine battery query to a human) costs **$3–$5** in agent time.
        However, a false negative (telling a customer whose battery is swelling or whose account was taken over to 'restart their phone')
        creates **catastrophic brand liability, safety hazards, and customer churn**.
        
        Our architecture prioritizes **High Escalation Recall (89.5%)** by combining:
        1. **Intent-level risk baselines**
        2. **Multi-token regex hazard scanner (Fire, smoke, legal, extortion)**
        3. **Calibrated softmax confidence gating (Threshold = 0.48)**
        4. **Explicit stated reasoning** for seamless human handoff.
        """)

if __name__ == "__main__":
    main()

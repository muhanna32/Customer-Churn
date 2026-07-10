"""
app.py — Customer Churn Prediction Dashboard (Streamlit).

Clean, readable UI built entirely with native Streamlit components.
No raw HTML/CSS injections. Easy to read and maintain.
"""

import streamlit as st
import plotly.graph_objects as go

import config as cfg
from model import predict_customer_churn, load_ml_assets

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title=cfg.APP_TITLE,
    page_icon=cfg.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.title("🔮 Churn Predictor")
    st.divider()

    st.subheader("🤖 Model Selector")
    selected_model = st.selectbox(
        "Choose a model",
        options=list(cfg.MODEL_OPTIONS.keys()),
        index=list(cfg.MODEL_OPTIONS.keys()).index(cfg.DEFAULT_MODEL),
        help="Select the ML model to use for prediction.",
    )

    st.divider()

    st.subheader("ℹ️ About")
    st.caption(cfg.APP_DESCRIPTION)
    st.caption("**Built with:** Streamlit · scikit-learn · XGBoost · Plotly")

    # Pre-load all models on startup so the first prediction is instant
    load_ml_assets()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("🔮 Customer Churn Prediction Dashboard")
st.write("Fill in the customer details below, then click **Predict Churn Risk**.")
st.divider()

# ─────────────────────────────────────────────
# INPUT FORM  —  3 columns
# ─────────────────────────────────────────────
st.subheader("📋 Customer Information")

col1, col2, col3 = st.columns(3)

# ── Column 1 — Demographics ──────────────────
with col1:
    st.markdown("**🧑 Demographics**")

    credit_score = st.number_input(
        "Credit Score", min_value=300, max_value=900, value=650, step=1
    )
    geography = st.selectbox("Geography", options=cfg.GEOGRAPHY_OPTIONS)
    gender = st.selectbox("Gender", options=cfg.GENDER_OPTIONS)
    age = st.slider("Age", min_value=18, max_value=100, value=38)

# ── Column 2 — Financials ────────────────────
with col2:
    st.markdown("**💰 Financials**")

    balance = st.number_input(
        "Balance ($)", min_value=0.0, max_value=300_000.0, value=76_000.0, step=500.0
    )
    estimated_salary = st.number_input(
        "Estimated Salary ($)", min_value=0.0, max_value=250_000.0, value=50_000.0, step=500.0
    )
    num_products = st.selectbox("Number of Products", options=[1, 2, 3, 4], index=1)
    card_type = st.selectbox("Card Type", options=cfg.CARD_TYPE_OPTIONS)

# ── Column 3 — Activity & Engagement ─────────
with col3:
    st.markdown("**📊 Activity & Engagement**")

    tenure = st.slider("Tenure (years)", min_value=0, max_value=10, value=5)
    has_credit_card = st.selectbox("Has Credit Card?", options=list(cfg.BINARY_OPTIONS.keys()))
    is_active = st.selectbox("Is Active Member?", options=list(cfg.BINARY_OPTIONS.keys()))
    has_complained = st.selectbox("Has Complained?", options=list(cfg.BINARY_OPTIONS.keys()), index=1)
    satisfaction_score = st.selectbox("Satisfaction Score", options=cfg.SATISFACTION_SCORE_OPTIONS, index=2)
    point_earned = st.number_input("Points Earned", min_value=0, max_value=1200, value=500, step=10)

st.divider()

# ─────────────────────────────────────────────
# PREDICT BUTTON
# ─────────────────────────────────────────────
predict_btn = st.button("🚀 Predict Churn Risk", type="primary", use_container_width=True)

# ─────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────
if predict_btn:

    # Build the input dict from widget values
    user_input = {
        "CreditScore":      credit_score,
        "Geography":        geography,
        "Gender":           gender,
        "Age":              age,
        "Tenure":           tenure,
        "Balance":          balance,
        "NumOfProducts":    num_products,
        "HasCrCard":        cfg.BINARY_OPTIONS[has_credit_card],
        "IsActiveMember":   cfg.BINARY_OPTIONS[is_active],
        "Complain":         cfg.BINARY_OPTIONS[has_complained],
        "EstimatedSalary":  estimated_salary,
        "Card Type":        card_type,
        "Satisfaction Score": satisfaction_score,
        "Point Earned":     point_earned,
    }

    # Run prediction
    with st.spinner("Running prediction…"):
        try:
            prediction, probability = predict_customer_churn(
                model_name=selected_model,
                input_data=user_input,
            )
        except Exception as exc:
            st.error(f"Prediction error: {exc}")
            st.stop()

    st.subheader("📊 Prediction Results")

    # ── Result message (native Streamlit) ────
    pct = probability * 100
    if prediction == 1:
        st.error(
            f"**⚠️ High Churn Risk — {pct:.1f}% probability**\n\n"
            "Recommended action: Initiate a proactive retention campaign — "
            "personalised offers, loyalty rewards, or a relationship manager call."
        )
    else:
        st.success(
            f"**✅ Low Churn Risk — {pct:.1f}% probability**\n\n"
            "The customer appears satisfied and is likely to remain. "
            "Continue monitoring engagement and maintain relationship quality."
        )

    # ── KPI metrics + Gauge side by side ─────
    metrics_col, gauge_col = st.columns([1, 2])

    with metrics_col:
        st.metric(label="Model Used", value=selected_model)
        st.metric(label="Risk Level", value="HIGH ⚠️" if prediction == 1 else "LOW ✅")
        st.metric(label="Churn Probability", value=f"{pct:.2f}%")

    with gauge_col:
        # Plotly Gauge Chart (speedometer)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pct,
            number={"suffix": "%", "font": {"size": 48}},
            title={"text": "Churn Probability", "font": {"size": 18}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#5c6bc0", "thickness": 0.25},
                "steps": [
                    {"range": [0,  30], "color": "#c8e6c9"},   # green
                    {"range": [30, 60], "color": "#fff9c4"},   # yellow
                    {"range": [60, 100], "color": "#ffcdd2"},  # red
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.8,
                    "value": pct,
                },
            },
        ))
        fig.update_layout(height=300, margin={"t": 60, "b": 10, "l": 20, "r": 20})
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()
st.caption("Customer Churn Predictor  •  Powered by Machine Learning  •  Built with Streamlit")

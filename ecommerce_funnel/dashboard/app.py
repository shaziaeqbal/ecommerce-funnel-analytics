"""
Streamlit E-Commerce Funnel Dashboard
Run:  streamlit run dashboard/app.py
"""
import streamlit as st
import duckdb, pandas as pd, numpy as np, plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

DB = "data/ecommerce.duckdb"

st.set_page_config(
    page_title="E-Commerce Funnel Analytics",
    page_icon="🛒", layout="wide"
)

@st.cache_data(ttl=300)
def q(sql):
    con = duckdb.connect(DB, read_only=True)
    df  = con.execute(sql).df()
    con.close()
    return df

# ── Sidebar ──────────────────────────────────
st.sidebar.image("https://www.gstatic.com/images/branding/googlelogo/svg/googlelogo_clr_74x24px.svg", width=120)
st.sidebar.title("Filters")
channels = ["All"] + q("SELECT DISTINCT channel FROM sessions ORDER BY 1")["channel"].tolist()
sel_ch   = st.sidebar.selectbox("Channel", channels)
devices  = ["All"] + q("SELECT DISTINCT device  FROM sessions ORDER BY 1")["device"].tolist()
sel_dv   = st.sidebar.selectbox("Device",  devices)

where_parts = []
if sel_ch != "All": where_parts.append(f"channel='{sel_ch}'")
if sel_dv != "All": where_parts.append(f"device='{sel_dv}'")
where = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""

# ── KPIs ─────────────────────────────────────
kpi = q(f"""
SELECT
    COUNT(*)                                AS total_sessions,
    ROUND(AVG(purchased)*100,2)             AS conversion_rate,
    ROUND(AVG(CASE WHEN added_to_cart=1 AND purchased=0
                   THEN 1.0 ELSE 0 END)*100,2) AS abandonment_rate,
    (SELECT ROUND(SUM(revenue),0) FROM transactions) AS total_revenue
FROM sessions {where}
""")

st.title("🛒 E-Commerce Funnel Analytics — Google Merchandise Store")
st.caption("Synthetic dataset modelled after Google Analytics public data")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Total Sessions",    f"{int(kpi.total_sessions[0]):,}")
c2.metric("Conversion Rate",   f"{kpi.conversion_rate[0]}%")
c3.metric("Cart Abandonment",  f"{kpi.abandonment_rate[0]}%")
c4.metric("Total Revenue",     f"${int(kpi.total_revenue[0]):,}")

st.divider()

# ── Funnel ────────────────────────────────────
st.subheader("📊 Multi-Step Conversion Funnel")
funnel_df = q(f"""
SELECT
    SUM(viewed_product)   AS product_views,
    SUM(added_to_cart)    AS add_to_cart,
    SUM(reached_checkout) AS checkout,
    SUM(purchased)        AS purchase
FROM sessions {where}
""")
steps  = ["Product Views","Add to Cart","Checkout","Purchase"]
values = [int(funnel_df[c][0]) for c in
          ["product_views","add_to_cart","checkout","purchase"]]
fig_funnel = go.Figure(go.Funnel(
    y=steps, x=values,
    textinfo="value+percent previous",
    marker_color=["#4285F4","#FBBC05","#34A853","#EA4335"]
))
fig_funnel.update_layout(margin=dict(l=0,r=0,t=10,b=0), height=320)
st.plotly_chart(fig_funnel, use_container_width=True)

st.divider()

# ── Channel Performance ───────────────────────
left, right = st.columns(2)

with left:
    st.subheader("📡 Revenue by Channel")
    rev = q("""
        SELECT s.channel,
               ROUND(SUM(t.revenue),0) AS revenue,
               COUNT(DISTINCT t.transaction_id) AS orders
        FROM sessions s
        LEFT JOIN transactions t USING(session_id)
        GROUP BY 1 ORDER BY 2 DESC
    """)
    fig_rev = px.bar(rev, x="channel", y="revenue",
                     color="channel", text="revenue",
                     color_discrete_sequence=px.colors.qualitative.G10)
    fig_rev.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig_rev.update_layout(showlegend=False, height=340,
                          margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig_rev, use_container_width=True)

with right:
    st.subheader("📱 Conversion Rate by Device")
    dev = q(f"""
        SELECT device,
               ROUND(SUM(purchased)*100.0/COUNT(*),2) AS conv_rate
        FROM sessions {where}
        GROUP BY 1
    """)
    fig_dev = px.pie(dev, names="device", values="conv_rate",
                     color_discrete_sequence=["#4285F4","#34A853","#FBBC05"])
    fig_dev.update_layout(height=340, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig_dev, use_container_width=True)

st.divider()

# ── Cart Abandonment Prediction ───────────────
st.subheader("🤖 Cart Abandonment — ML Risk Scores")
model_path = Path("ml/abandonment_model.joblib")
if model_path.exists():
    import joblib
    from ml.predict import score_sessions
    sample = q("""
        SELECT session_id, channel, device, country,
               page_views, session_duration, bounce, reached_checkout
        FROM mart_cart_abandonment
        WHERE added_to_cart=1
        LIMIT 2000
    """)
    scored = score_sessions(sample)
    scored["risk"] = pd.cut(
        scored["abandonment_probability"],
        bins=[0,.4,.7,1.0],
        labels=["Low","Medium","High"]
    )
    risk_counts = scored["risk"].value_counts().reset_index()
    risk_counts.columns = ["Risk Level","Count"]
    fig_risk = px.bar(risk_counts, x="Risk Level", y="Count",
                      color="Risk Level",
                      color_discrete_map={"Low":"#34A853","Medium":"#FBBC05","High":"#EA4335"})
    fig_risk.update_layout(showlegend=False, height=300,
                           margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig_risk, use_container_width=True)
    with st.expander("View scored sessions (top 50)"):
        st.dataframe(
            scored[["session_id","channel","device",
                    "abandonment_probability","risk"]].head(50),
            use_container_width=True
        )
else:
    st.info("Run `python setup.py` to train the ML model, then refresh.")

st.divider()

# ── Revenue Impact (Business Case) ───────────
st.subheader("💰 Revenue Recovery — Business Case")
impact = q("SELECT * FROM mart_revenue_impact ORDER BY lost_revenue DESC")
st.dataframe(
    impact.rename(columns={
        "channel":"Channel",
        "abandoned_carts":"Abandoned Carts",
        "avg_order_value":"Avg Order Value ($)",
        "lost_revenue":"Lost Revenue ($)",
        "recovery_10pct":"10% Recovery ($)",
        "recovery_20pct":"20% Recovery ($)",
    }),
    use_container_width=True
)
total_lost = impact["lost_revenue"].sum()
rec10 = impact["recovery_10pct"].sum()
rec20 = impact["recovery_20pct"].sum()

r1,r2,r3 = st.columns(3)
r1.metric("💸 Total Lost Revenue",        f"${total_lost:,.0f}")
r2.metric("📈 10% Recovery Potential",    f"${rec10:,.0f}")
r3.metric("🚀 20% Recovery Potential",    f"${rec20:,.0f}")

st.caption("""
**Business Case:** Targeting high-risk abandoned carts (ML score > 0.7) with
personalised email / push campaigns typically recovers 10–20% of lost revenue
at <5% incremental cost, yielding 15–30× ROI on campaign spend.
""")

# ── Revenue Trend ─────────────────────────────
st.subheader("📅 Daily Revenue Trend")
trend = q("""
    SELECT transaction_date AS date,
           ROUND(SUM(revenue),2) AS revenue
    FROM transactions
    GROUP BY 1 ORDER BY 1
""")
fig_trend = px.area(trend, x="date", y="revenue",
                    color_discrete_sequence=["#4285F4"])
fig_trend.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0))
st.plotly_chart(fig_trend, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("Built with DuckDB · dbt · scikit-learn · Streamlit\nData: Google Merchandise Store (synthetic)")

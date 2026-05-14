"""
PapAiEra CCTS — No-Code Sustainability Dashboard
===================================================

Built-in Streamlit web application for carbon calculation,
factor editing, credit estimation, and ESG dashboard.

Launch:
    python -m pap_ai_era.ccts.ui.app
"""

import streamlit as st
import pandas as pd
import json
import os
import sys

# Add parent to path for local dev
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from pap_ai_era.ccts import (
    CarbonCalculator, FactorEngine, ProductMaster,
    CreditEstimator, FormulaEngine, ExcelHandler, DatabaseHandler,
)

# ─── Page Config ─────────────────────────────────────────────
st.set_page_config(
    page_title="PapAiEra CCTS — Carbon Credit Platform",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)}
    .main .block-container {padding-top: 1rem}
    h1 {color: #00d4aa !important; font-family: 'Segoe UI', sans-serif}
    h2, h3 {color: #7ec8e3 !important}
    .stMetric {background: rgba(0,212,170,0.08); border-radius: 12px; padding: 10px;
               border: 1px solid rgba(0,212,170,0.2)}
    .stDataFrame {border-radius: 8px}
    div[data-testid="stSidebar"] {background: linear-gradient(180deg, #1a1a2e 0%, #0f0f23 100%)}
    .factor-card {background: rgba(126,200,227,0.1); border-radius: 10px;
                  padding: 15px; margin: 5px 0; border: 1px solid rgba(126,200,227,0.2)}
</style>
""", unsafe_allow_html=True)

# ─── Initialize Engines ─────────────────────────────────────
@st.cache_resource
def get_engines():
    return {
        'factors': FactorEngine(),
        'products': ProductMaster(),
        'calculator': CarbonCalculator(),
        'credits': CreditEstimator(),
        'formulas': FormulaEngine(),
        'excel': ExcelHandler(),
    }

engines = get_engines()

# ─── Sidebar Navigation ─────────────────────────────────────
st.sidebar.markdown("## 🌿 PapAiEra CCTS")
st.sidebar.markdown("*Carbon Credit & Trading System*")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "🧮 Carbon Calculator", "📊 Credit Estimator",
     "⚙️ Factor Editor", "📁 Data Import", "📈 ESG KPIs"],
    index=0
)

st.sidebar.divider()
st.sidebar.markdown("**v0.6.1** | Built on PapAiEra")


# ═══════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.title("🌿 Carbon Credit & Trading System")
    st.markdown("**No-code sustainability platform for Pulp, Paper, Board & Packaging**")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Product Grades", len(engines['products'].grades))
    col2.metric("⛽ Fuel Factors", len(engines['factors'].list_fuel_factors()))
    col3.metric("⚡ Grid Regions", len(engines['factors'].list_electricity_factors()))
    col4.metric("📐 Formulas", len(engines['formulas'].list_formulas()))

    st.divider()

    # Quick Estimate Section
    st.subheader("⚡ Quick Carbon Estimate")
    c1, c2, c3 = st.columns(3)

    grades = list(engines['products'].grades.keys())
    with c1:
        sel_product = st.selectbox("Product Grade", grades, index=0)
    with c2:
        sel_tons = st.number_input("Production (tons)", value=1000.0, step=100.0, min_value=1.0)
    with c3:
        regions = list(engines['factors'].list_electricity_factors().keys())
        sel_region = st.selectbox("Grid Region", regions, index=regions.index('india_national'))

    if st.button("🔄 Calculate Quick Estimate", type="primary", use_container_width=True):
        result = engines['calculator'].quick_estimate(sel_product, sel_tons, sel_region)
        st.success(f"✅ Calculated for {sel_tons:.0f} tons of {sel_product}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Scope 1", f"{result.scope1_total:.1f} tCO₂e")
        m2.metric("Scope 2", f"{result.scope2_total:.1f} tCO₂e")
        m3.metric("Scope 3", f"{result.scope3_total:.1f} tCO₂e")
        m4.metric("Total", f"{result.total_tco2e:.1f} tCO₂e", f"{result.co2e_per_ton:.3f} t/ton")

        # Scope pie chart
        import plotly.graph_objects as go
        fig = go.Figure(data=[go.Pie(
            labels=['Scope 1 (Direct)', 'Scope 2 (Energy)', 'Scope 3 (Value Chain)'],
            values=[result.scope1_total, result.scope2_total, result.scope3_total],
            hole=0.5,
            marker_colors=['#ff6b6b', '#ffd93d', '#6bcb77'],
        )])
        fig.update_layout(
            title="Emission Breakdown by Scope",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='white', height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Product Catalog
    st.divider()
    st.subheader("📦 Product Catalog")
    catalog_data = engines['products'].list_grades()
    st.dataframe(pd.DataFrame(catalog_data), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: CARBON CALCULATOR
# ═══════════════════════════════════════════════════════════════
elif page == "🧮 Carbon Calculator":
    st.title("🧮 Carbon Calculator")
    st.markdown("**Full Scope 1 + 2 + 3 carbon footprint calculation**")

    with st.expander("📦 Product & Production", expanded=True):
        c1, c2 = st.columns(2)
        product = c1.selectbox("Product Grade", list(engines['products'].grades.keys()))
        production = c2.number_input("Production (tons)", value=1000.0, step=100.0)

    with st.expander("⛽ Scope 1 — Fuel Consumption (GJ)", expanded=True):
        fuel_types = list(engines['factors'].list_fuel_factors().keys())
        fuel_data = {}
        cols = st.columns(3)
        for i, ft in enumerate(fuel_types[:9]):
            val = cols[i % 3].number_input(ft.replace('_', ' ').title(), value=0.0, key=f"fuel_{ft}")
            if val > 0:
                fuel_data[ft] = val

    with st.expander("⚡ Scope 2 — Electricity & Steam"):
        c1, c2 = st.columns(2)
        elec_mwh = c1.number_input("Electricity (MWh)", value=0.0)
        elec_region = c2.selectbox("Grid Region",
                                   list(engines['factors'].list_electricity_factors().keys()),
                                   key="calc_region")
        c3, c4 = st.columns(2)
        steam_gj = c3.number_input("Purchased Steam (GJ)", value=0.0)
        steam_src = c4.selectbox("Steam Source",
                                 list(engines['factors'].list_steam_factors().keys()))

    with st.expander("🧪 Scope 3 — Chemicals (tons)"):
        chem_data = {}
        chem_cols = st.columns(3)
        for i, chem in enumerate(['naoh', 'clo2', 'starch', 'alum', 'latex', 'akd']):
            val = chem_cols[i % 3].number_input(chem.upper(), value=0.0, key=f"chem_{chem}")
            if val > 0:
                chem_data[chem] = val

    if st.button("🔥 Calculate Full Footprint", type="primary", use_container_width=True):
        result = engines['calculator'].calculate(
            product=product,
            production_tons=production,
            fuel=fuel_data or None,
            electricity_mwh=elec_mwh,
            electricity_region=elec_region,
            steam_purchased_gj=steam_gj,
            steam_source=steam_src,
            chemicals_tons=chem_data or None,
        )

        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Scope 1", f"{result.scope1_total:.2f} tCO₂e")
        m2.metric("Scope 2", f"{result.scope2_total:.2f} tCO₂e")
        m3.metric("Scope 3", f"{result.scope3_total:.2f} tCO₂e")
        m4.metric("🎯 Total", f"{result.total_tco2e:.2f} tCO₂e")

        st.code(result.summary(), language='text')

        if result.fuel_breakdown:
            st.subheader("Fuel Breakdown")
            st.dataframe(pd.DataFrame([
                {'Fuel': k.replace('_', ' ').title(), 'tCO₂e': v}
                for k, v in result.fuel_breakdown.items()
            ]), hide_index=True, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: CREDIT ESTIMATOR
# ═══════════════════════════════════════════════════════════════
elif page == "📊 Credit Estimator":
    st.title("📊 Carbon Credit Estimator")

    method = st.radio("Estimation Method",
                      ["Baseline vs Actual", "Fuel Switch", "Efficiency Gain"],
                      horizontal=True)

    if method == "Baseline vs Actual":
        c1, c2 = st.columns(2)
        proj_name = c1.text_input("Project Name", "Emission Reduction Project")
        price = c2.number_input("Credit Price ($/ton)", value=15.0)
        c3, c4 = st.columns(2)
        baseline = c3.number_input("Baseline Emissions (tCO₂e/year)", value=10000.0)
        current = c4.number_input("Current/Proposed Emissions (tCO₂e/year)", value=7500.0)

        if st.button("💰 Estimate Credits", type="primary"):
            ce = CreditEstimator(price_per_ton=price)
            result = ce.from_custom(proj_name, baseline, current)
            st.success("✅ Credit estimate calculated!")
            m1, m2, m3 = st.columns(3)
            m1.metric("CO₂ Saved", f"{result.savings_tco2e:,.1f} tons")
            m2.metric("Credits", f"{result.credit_tons:,.1f} tons")
            m3.metric("💰 Value", f"${result.credit_value_usd:,.2f}")
            st.code(result.summary(), language='text')

    elif method == "Fuel Switch":
        proj_name = st.text_input("Project Name", "Coal to Gas Conversion")
        price = st.number_input("Credit Price ($/ton)", value=15.0, key="fs_price")
        st.subheader("Baseline Fuel (GJ)")
        bc1, bc2 = st.columns(2)
        base_coal = bc1.number_input("Coal (GJ)", value=100000.0)
        base_gas = bc2.number_input("Natural Gas (GJ)", value=20000.0)
        st.subheader("Proposed Fuel (GJ)")
        pc1, pc2, pc3 = st.columns(3)
        prop_gas = pc1.number_input("Natural Gas (GJ)", value=80000.0, key="prop_gas")
        prop_bio = pc2.number_input("Biomass (GJ)", value=40000.0)
        prop_coal = pc3.number_input("Coal (GJ)", value=0.0, key="prop_coal")

        if st.button("💰 Estimate Credits", type="primary", key="fs_btn"):
            ce = CreditEstimator(price_per_ton=price)
            result = ce.from_fuel_switch(
                proj_name, 50000,
                {'coal_bituminous': base_coal, 'natural_gas': base_gas},
                {'natural_gas': prop_gas, 'biomass_wood': prop_bio, 'coal_bituminous': prop_coal}
            )
            m1, m2, m3 = st.columns(3)
            m1.metric("CO₂ Saved", f"{result.savings_tco2e:,.1f} tons")
            m2.metric("Credits", f"{result.credit_tons:,.1f} tons")
            m3.metric("💰 Value", f"${result.credit_value_usd:,.2f}")
            st.code(result.summary(), language='text')

    elif method == "Efficiency Gain":
        proj_name = st.text_input("Project Name", "Steam Optimization")
        c1, c2, c3 = st.columns(3)
        base_co2 = c1.number_input("Current Emissions (tCO₂e)", value=8000.0)
        eff_pct = c2.number_input("Efficiency Gain (%)", value=15.0)
        price = c3.number_input("Credit Price ($/ton)", value=15.0, key="eff_price")

        if st.button("💰 Estimate Credits", type="primary", key="eff_btn"):
            ce = CreditEstimator(price_per_ton=price)
            result = ce.from_efficiency(proj_name, base_co2, eff_pct)
            m1, m2, m3 = st.columns(3)
            m1.metric("CO₂ Saved", f"{result.savings_tco2e:,.1f} tons")
            m2.metric("Credits", f"{result.credit_tons:,.1f} tons")
            m3.metric("💰 Value", f"${result.credit_value_usd:,.2f}")
            st.code(result.summary(), language='text')


# ═══════════════════════════════════════════════════════════════
# PAGE: FACTOR EDITOR
# ═══════════════════════════════════════════════════════════════
elif page == "⚙️ Factor Editor":
    st.title("⚙️ Emission Factor Editor")
    st.markdown("**Edit any factor — changes apply immediately to all calculations**")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["⛽ Fuel", "⚡ Electricity", "♨️ Steam", "🏭 Process", "🌲 Fiber"])

    with tab1:
        st.subheader("Fuel Emission Factors (kg CO₂/GJ)")
        fuel_factors = engines['factors'].list_fuel_factors()
        edited_fuel = st.data_editor(
            pd.DataFrame([{'Factor': k, 'Value (kg CO₂/GJ)': v} for k, v in fuel_factors.items()]),
            use_container_width=True, hide_index=True, num_rows="dynamic",
        )
        if st.button("💾 Save Fuel Factors"):
            for _, row in edited_fuel.iterrows():
                engines['factors'].set_fuel_factor(row['Factor'], row['Value (kg CO₂/GJ)'])
            st.success("✅ Fuel factors updated!")

    with tab2:
        st.subheader("Grid Electricity Factors (kg CO₂/MWh)")
        elec_factors = engines['factors'].list_electricity_factors()
        edited_elec = st.data_editor(
            pd.DataFrame([{'Region': k, 'Value (kg CO₂/MWh)': v} for k, v in elec_factors.items()]),
            use_container_width=True, hide_index=True, num_rows="dynamic",
        )
        if st.button("💾 Save Electricity Factors"):
            for _, row in edited_elec.iterrows():
                engines['factors'].set_electricity_factor(row['Region'], row['Value (kg CO₂/MWh)'])
            st.success("✅ Electricity factors updated!")

    with tab3:
        st.subheader("Steam Factors (kg CO₂/GJ)")
        steam_factors = engines['factors'].list_steam_factors()
        edited_steam = st.data_editor(
            pd.DataFrame([{'Source': k, 'Value (kg CO₂/GJ)': v} for k, v in steam_factors.items()]),
            use_container_width=True, hide_index=True, num_rows="dynamic",
        )
        if st.button("💾 Save Steam Factors"):
            for _, row in edited_steam.iterrows():
                engines['factors'].set_steam_factor(row['Source'], row['Value (kg CO₂/GJ)'])
            st.success("✅ Steam factors updated!")

    with tab4:
        st.subheader("Process Factors (kg CO₂/ton)")
        proc_factors = engines['factors'].list_process_factors()
        edited_proc = st.data_editor(
            pd.DataFrame([{'Process': k, 'Value': v} for k, v in proc_factors.items()]),
            use_container_width=True, hide_index=True, num_rows="dynamic",
        )

    with tab5:
        st.subheader("Fiber Factors (kg CO₂/ADT)")
        fiber_factors = engines['factors'].list_fiber_factors()
        edited_fiber = st.data_editor(
            pd.DataFrame([{'Fiber Type': k, 'Value (kg CO₂/ADT)': v} for k, v in fiber_factors.items()]),
            use_container_width=True, hide_index=True, num_rows="dynamic",
        )

    st.divider()
    if st.button("📥 Export All Factors to JSON"):
        export_path = os.path.join(os.path.expanduser('~'), 'ccts_factors_export.json')
        engines['factors'].save_to_json(export_path)
        st.success(f"✅ Exported to {export_path}")


# ═══════════════════════════════════════════════════════════════
# PAGE: DATA IMPORT
# ═══════════════════════════════════════════════════════════════
elif page == "📁 Data Import":
    st.title("📁 Data Import / Export")

    tab1, tab2, tab3 = st.tabs(["📤 Upload Data", "📥 Download Templates", "🗄️ Database"])

    with tab1:
        st.subheader("Upload Production Data")
        uploaded = st.file_uploader("Upload Excel or CSV", type=['xlsx', 'xls', 'csv'])
        if uploaded:
            if uploaded.name.endswith('.csv'):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
            df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.success(f"✅ Loaded {len(df)} rows from {uploaded.name}")

            if 'product' in df.columns and 'production_tons' in df.columns:
                if st.button("🔥 Calculate All Rows", type="primary"):
                    results = []
                    for _, row in df.iterrows():
                        try:
                            fuel = {}
                            for col in df.columns:
                                if col.endswith('_gj') and row[col] > 0:
                                    fuel_name = col.replace('_gj', '')
                                    fuel[fuel_name] = row[col]

                            r = engines['calculator'].calculate(
                                product=row['product'],
                                production_tons=row['production_tons'],
                                fuel=fuel or None,
                                electricity_mwh=row.get('electricity_mwh', 0),
                                electricity_region=row.get('electricity_region', 'india_national'),
                            )
                            results.append(r.to_dict())
                        except Exception as e:
                            results.append({'product_grade': row.get('product', '?'), 'error': str(e)})

                    st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Download Templates")
        if st.button("📥 Generate Production Template"):
            template_path = os.path.join(os.path.expanduser('~'), 'ccts_production_template.xlsx')
            engines['excel'].generate_template(template_path, 'production')
            st.success(f"✅ Template saved to {template_path}")

        if st.button("📥 Generate Factors Template"):
            template_path = os.path.join(os.path.expanduser('~'), 'ccts_factors_template.xlsx')
            engines['excel'].generate_template(template_path, 'factors')
            st.success(f"✅ Template saved to {template_path}")

    with tab3:
        st.subheader("Database Connection")
        db_path = st.text_input("SQLite Database Path",
                                os.path.join(os.path.expanduser('~'), '.papaiera_ccts.db'))
        if st.button("🔗 Connect & View History"):
            try:
                db = DatabaseHandler(db_path)
                history = db.get_results_history(limit=50)
                if history:
                    st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
                else:
                    st.info("No calculation history found yet.")
                db.close()
            except Exception as e:
                st.error(f"Database error: {e}")


# ═══════════════════════════════════════════════════════════════
# PAGE: ESG KPIs
# ═══════════════════════════════════════════════════════════════
elif page == "📈 ESG KPIs":
    st.title("📈 ESG KPI Dashboard Builder")
    st.markdown("**Build custom sustainability dashboards**")

    fe = engines['formulas']
    categories = fe.get_categories()

    sel_cat = st.selectbox("KPI Category", ['all'] + categories)
    formulas = fe.list_formulas(category=sel_cat if sel_cat != 'all' else None)
    st.dataframe(pd.DataFrame(formulas), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("🧮 KPI Calculator")

    sel_formula = st.selectbox("Select Formula", [f['name'] for f in formulas])
    formula_info = next((f for f in formulas if f['name'] == sel_formula), None)

    if formula_info:
        st.info(f"**{formula_info['description']}** | Unit: {formula_info['unit']}")

        params = {}
        cols = st.columns(min(3, len(formula_info['parameters'])))
        for i, param in enumerate(formula_info['parameters']):
            params[param] = cols[i % len(cols)].number_input(
                param.replace('_', ' ').title(), value=100.0, key=f"kpi_{param}")

        if st.button("📊 Calculate KPI", type="primary"):
            try:
                value = fe.execute(sel_formula, **params)
                st.metric(formula_info['description'], f"{value:.4f} {formula_info['unit']}")
            except Exception as e:
                st.error(f"Calculation error: {e}")

    # Benchmark comparison
    st.divider()
    st.subheader("🎯 Product Benchmark Comparison")
    grades = engines['products'].list_grades()
    bench_df = pd.DataFrame(grades)
    if not bench_df.empty:
        import plotly.express as px
        fig = px.bar(bench_df, x='name', y='typical_co2_per_ton',
                     color='category', title='Typical CO₂ per Ton by Product Grade',
                     labels={'typical_co2_per_ton': 'kg CO₂/ton', 'name': 'Grade'})
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='white', height=400,
        )
        st.plotly_chart(fig, use_container_width=True)


# ─── Footer ─────────────────────────────────────────────────
st.sidebar.divider()
st.sidebar.caption("🌿 PapAiEra CCTS v0.6.1")
st.sidebar.caption("Carbon Credit & Trading System")
st.sidebar.caption("© 2026 PapAiEra")

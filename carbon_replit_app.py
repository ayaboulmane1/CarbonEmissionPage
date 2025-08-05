import streamlit as st
st.markdown(
    """
    <style>
        body {
            background-color: #e6f4ea;
        }
        .stApp {
            background-color: #e6f4ea;
        }
    </style>
    """,
    unsafe_allow_html=True
)

import pandas as pd
import plotly.graph_objects as go
from utils.emission_calculator import EmissionCalculator
from local_data_handler import LocalDataManager
import uuid

st.set_page_config(
    page_title="Carbon Emission Calculator - EV vs Diesel",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

lang = st.sidebar.selectbox("Select Language", ["German", "English", "Spanish"])

TEXTS = {
    "German": {
        "title": "Deutscher Kohlenstoff-Emissionsrechner",
        "subtitle": "Elektroauto vs. Diesel - Umfassende Lebenszyklus-Analyse",
        "banner": "Deutschlands Weg zur Klimaneutralität 2045 - Jedes Fahrzeug zählt!",
        "sidebar_title": "Navigation",
        "analysis_prompt": "Vollständige Analyse erkunden:",
        "vehicle_input": "Fahrzeug-Eingabe - Detaillierte Spezifikationen",
        "emission_dashboard": "Emissions-Dashboard - Echtzeitberechnungen",
        "comparison_analysis": "Vergleichsanalyse - Multi-Szenario-Vergleich",
        "impact_analysis": "Umweltauswirkungen - Umfassende Folgenabschätzung",
        "lifecycle_analysis": "Lebenszyklus-Analyse - Cradle-to-Grave Bewertung",
        "vehicle_type": "Fahrzeugtyp",
        "select_type": ["Elektrofahrzeug", "Dieselfahrzeug"],
        "efficiency_label": "Energieeffizienz (kWh/100km)",
        "mileage": "Jährliche Kilometerleistung",
        "calculate": "Berechnen",
        "result_title": "Ergebnisse",
        "annual": "Jährliche CO2 Emissionen",
        "lifetime": "Lebenszeit Emissionen",
        "total": "Gesamter Lebenszyklus"
    },
    "English": {
        "title": "German Carbon Emission Calculator",
        "subtitle": "Electric vs. Diesel Vehicles - Full Lifecycle Analysis",
        "banner": "Germany's Path to Climate Neutrality 2045 - Every Vehicle Counts!",
        "sidebar_title": "Navigation",
        "analysis_prompt": "Explore Full Analysis:",
        "vehicle_input": "Vehicle Input - Detailed Specifications",
        "emission_dashboard": "Emissions Dashboard - Real-Time Calculations",
        "comparison_analysis": "Comparison Analysis - Multi-Scenario View",
        "impact_analysis": "Environmental Impact - Full Consequence Estimation",
        "lifecycle_analysis": "Lifecycle Analysis - Cradle-to-Grave Assessment",
        "vehicle_type": "Vehicle Type",
        "select_type": ["Electric Vehicle", "Diesel Vehicle"],
        "efficiency_label": "Energy Efficiency (kWh/100km)",
        "mileage": "Annual Mileage (km)",
        "calculate": "Calculate",
        "result_title": "Results",
        "annual": "Annual CO2 Emissions",
        "lifetime": "Lifetime Emissions",
        "total": "Total Lifecycle"
    },
    "Spanish": {
        "title": "Calculadora de Emisiones de Carbono en Alemania",
        "subtitle": "Vehículo Eléctrico vs. Diésel - Análisis Completo del Ciclo de Vida",
        "banner": "Camino de Alemania hacia la Neutralidad Climática 2045 - ¡Cada Vehículo Cuenta!",
        "sidebar_title": "Navegación",
        "analysis_prompt": "Explorar Análisis Completo:",
        "vehicle_input": "Entrada de Vehículo - Especificaciones Detalladas",
        "emission_dashboard": "Panel de Emisiones - Cálculos en Tiempo Real",
        "comparison_analysis": "Análisis Comparativo - Vista de Múltiples Escenarios",
        "impact_analysis": "Impacto Ambiental - Evaluación Completa de Consecuencias",
        "lifecycle_analysis": "Análisis del Ciclo de Vida - Evaluación Total",
        "vehicle_type": "Tipo de Vehículo",
        "select_type": ["Vehículo Eléctrico", "Vehículo Diésel"],
        "efficiency_label": "Eficiencia Energética (kWh/100km)",
        "mileage": "Kilometraje Anual (km)",
        "calculate": "Calcular",
        "result_title": "Resultados",
        "annual": "Emisiones Anuales de CO2",
        "lifetime": "Emisiones de por Vida",
        "total": "Ciclo de Vida Total"
    }
}

T = TEXTS[lang]

st.markdown(f"""
    <div style="background: linear-gradient(135deg, #000000 0%, #DD0000 25%, #FFCE00 75%, #000000 100%); 
                padding: 30px; border-radius: 18px; margin-bottom: 30px; text-align: center; box-shadow: 0 8px 24px rgba(0,0,0,0.3);">
        <h1 style="color: white; font-size: 3em; margin: 0; font-weight: 800; text-shadow: 2px 2px 6px rgba(0,0,0,0.6);">
            {T['title']}</h1>
        <h3 style="color: #FFCE00; margin: 15px 0 0 0; font-weight: 400; font-size: 1.4em;">
            {T['subtitle']}</h3>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div style="background: linear-gradient(90deg, #2E8B57 0%, #32CD32 100%); 
                padding: 18px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 16px rgba(0,0,0,0.2);">
        <h4 style="color: white; margin: 0; text-align: center; font-size: 1.2em;">
            {T['banner']}</h4>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
    <div style="background: linear-gradient(45deg, #1E7F4F 0%, #2E8B57 100%); 
                padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.15);">
        <h2 style="color: white; margin: 0; text-align: center; font-weight: 600;">
            {T['sidebar_title']}</h2>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"### {T['analysis_prompt']}")
st.sidebar.markdown(T['vehicle_input'])
st.sidebar.markdown(T['emission_dashboard'])
st.sidebar.markdown(T['comparison_analysis'])
st.sidebar.markdown(T['lifecycle_analysis'])

# === Logic Starts Here ===
if 'calculator' not in st.session_state:
    st.session_state.calculator = EmissionCalculator()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(T['vehicle_type'])
    vehicle = st.selectbox("", T['select_type'])
    efficiency = st.number_input(T['efficiency_label'], min_value=10.0, max_value=50.0, value=18.0, step=0.5)
    mileage = st.number_input(T['mileage'], min_value=1000, max_value=100000, value=15000, step=1000)

    if st.button(T['calculate']):
        if vehicle == T['select_type'][0]:
            data = st.session_state.calculator.calculate_ev_emissions(mileage * 0.621371, efficiency, "Germany 2025")
        else:
            mpg = 235.2 / efficiency
            data = st.session_state.calculator.calculate_diesel_emissions(mileage * 0.621371, mpg)

        st.session_state.result = data

with col2:
    if 'result' in st.session_state:
        r = st.session_state.result
        st.subheader(T['result_title'])
        st.metric(T['annual'], f"{r['co2_annual']:.1f} kg")
        st.metric(T['lifetime'], f"{r['co2_lifetime']:.1f} kg")
        st.metric(T['total'], f"{r['total_lifecycle']:.1f} kg")

        df = pd.DataFrame({
            "Metric": [T['annual'], T['lifetime'], T['total']],
            "CO2 (kg)": [r['co2_annual'], r['co2_lifetime'], r['total_lifecycle']]
        })

        fig = go.Figure(data=[
            go.Bar(x=df['Metric'], y=df['CO2 (kg)'], marker_color=['#1E7F4F', '#2E8B57', '#FFCE00'])
        ])

        fig.update_layout(
            title=T['result_title'],
            xaxis_title="",
            yaxis_title="CO2 (kg)",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig, use_container_width=True)

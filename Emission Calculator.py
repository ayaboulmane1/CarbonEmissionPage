import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.emission_calculator import EmissionCalculator
from local_data_handler import LocalDataManager
import uuid
import plotly.express as px
from utils.data_handler import DataHandler

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
    <div style="background: #1e7f4f; padding: 32px; border-radius: 16px; margin-bottom: 24px; text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
        <h1 style="color: #ffffff; font-size: 2.5rem; margin: 0; font-weight: 700;">
            {T['title']}
        </h1>
        <h3 style="color: #c8facc; margin-top: 12px; font-weight: 400; font-size: 1.25rem;">
            {T['subtitle']}
        </h3>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="banner">{T['banner']}</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
    <div style="background: linear-gradient(45deg, #1E7F4F 0%, #2E8B57 100%); padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.15);">
        <h2 style="color: white; margin: 0; text-align: center; font-weight: 600;">
            {T['sidebar_title']}</h2>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"### {T['analysis_prompt']}")
st.sidebar.markdown(T['vehicle_input'])
st.sidebar.markdown(T['emission_dashboard'])
st.sidebar.markdown(T['comparison_analysis'])
st.sidebar.markdown(T['lifecycle_analysis'])

# Initialize components
if 'calculator' not in st.session_state:
    st.session_state.calculator = EmissionCalculator()
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = DataHandler()

# Main input section
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Vehicle Configuration")
    
    # Vehicle type selection
    vehicle_type = st.selectbox(
        "Select Vehicle Type",
        ["Electric Vehicle", "Diesel Vehicle"],
        help="Choose the type of vehicle for emission calculation"
    )
    
    # Basic parameters
    st.subheader("Basic Parameters")
    
    col_a, col_b = st.columns(2)
    with col_a:
        annual_mileage = st.number_input(
            "Annual Mileage (miles)",
            min_value=1000,
            max_value=100000,
            value=12000,
            step=1000,
            help="Average miles driven per year"
        )
        
        vehicle_age = st.number_input(
            "Expected Vehicle Lifetime (years)",
            min_value=5,
            max_value=25,
            value=15,
            help="Expected operational lifetime of the vehicle"
        )
    
    with col_b:
        if vehicle_type == "Electric Vehicle":
            efficiency = st.number_input(
                "Energy Efficiency (kWh/100 miles)",
                min_value=10.0,
                max_value=60.0,
                value=34.0,
                step=1.0,
                help="Energy consumption per 100 miles"
            )
        else:
            efficiency = st.number_input(
                "Fuel Efficiency (MPG)",
                min_value=15.0,
                max_value=60.0,
                value=30.0,
                step=1.0,
                help="Miles per gallon fuel efficiency"
            )
        
        driving_pattern = st.selectbox(
            "Driving Pattern",
            ["Mixed (City/Highway)", "Mostly City", "Mostly Highway"],
            help="Primary driving conditions"
        )
    
    # Vehicle-specific parameters
    if vehicle_type == "Electric Vehicle":
        st.subheader("Electric Vehicle Specific")
        
        col_c, col_d = st.columns(2)
        with col_c:
            grid_mix_label = st.selectbox(
                "Electricity Grid Mix",
                  list(st.session_state.calculator.grid_factors.keys()) ,
                help="Regional electricity generation source"
            )
            
            grid_mix_factor = st.session_state.calculator.grid_factors[grid_mix_label]
        
            
            charging_type = st.selectbox(
                "Primary Charging Type",
                ["Home (Level 2)", "Public Fast Charging", "Workplace Charging"],
                help="Most common charging method"
            )
        
        with col_d:
            battery_size = st.number_input(
                "Battery Capacity (kWh)",
                min_value=20.0,
                max_value=150.0,
                value=75.0,
                help="Total battery capacity"
            )
            
            cold_weather = st.checkbox(
                "Cold Weather Region",
                help="Check if vehicle operates in cold climate (affects efficiency)"
            )
    
    else:  # Diesel Vehicle
        st.subheader("Diesel Vehicle Specific")
        
        col_c, col_d = st.columns(2)
        with col_c:
            engine_size = st.number_input(
                "Engine Size (Liters)",
                min_value=1.0,
                max_value=8.0,
                value=2.0,
                step=0.1,
                help="Engine displacement in liters"
            )
            
            fuel_type = st.selectbox(
                "Diesel Type",
                ["Regular Diesel", "Bio-Diesel (B20)", "Renewable Diesel"],
                help="Type of diesel fuel used"
            )
        
        with col_d:
            emission_standard = st.selectbox(
                "Emission Standard",
                ["Euro 6", "Euro 5", "EPA Tier 3"],
                help="Vehicle emission compliance standard"
            )
            
            turbo = st.checkbox(
                "Turbocharged Engine",
                help="Check if engine is turbocharged"
            )

with col2:
    st.header("Quick Calculation")
    
    if st.button("Calculate Emissions", type="primary", use_container_width=True):
        # Prepare parameters
        parameters = {
            "annual_mileage": annual_mileage,
            "efficiency": efficiency,
            "vehicle_age": vehicle_age,
            "driving_pattern": driving_pattern
        }
        
        # Calculate emissions
        if vehicle_type == "Electric Vehicle":
            parameters.update({
                "grid_mix_label": grid_mix_label,
                "grid_mix_factor": grid_mix_factor,
                "charging_type": charging_type,
                "battery_size": battery_size,
                "cold_weather": cold_weather
            })
            
            results = st.session_state.calculator.calculate_ev_emissions(
                annual_mileage, efficiency, grid_mix_factor, vehicle_age
            )
        else:
            parameters.update({
                "engine_size": engine_size,
                "fuel_type": fuel_type,
                "emission_standard": emission_standard,
                "turbo": turbo
            })
            
            results = st.session_state.calculator.calculate_diesel_emissions(
                annual_mileage=annual_mileage,          # miles/year
                mpg=efficiency,                         # MPG from UI
                years=vehicle_age,
                fuel_type=fuel_type,
                engine_size_l=engine_size,
                emission_standard=emission_standard,
                turbo=turbo
            )

        
        # Save calculation
        st.session_state.data_handler.save_calculation(results, vehicle_type, parameters)
        
        # Display results
        st.success("Calculation Complete!")
        
        st.metric("Annual CO2 Emissions", f"{results['co2_annual']:.1f} kg")
        st.metric("Lifetime CO2 Emissions", f"{results['co2_lifetime']:.1f} kg")
        st.metric("Total w/ Manufacturing", f"{results['total_lifecycle']:.1f} kg")
        
        # Environmental impact score
        impact_score = st.session_state.calculator.get_environmental_impact_score(results)
        
        if impact_score < 30:
            st.success(f"Environmental Impact Score: {impact_score}/100 (Excellent)")
        elif impact_score < 60:
            st.warning(f"Environmental Impact Score: {impact_score}/100 (Good)")
        else:
            st.error(f"Environmental Impact Score: {impact_score}/100 (Poor)")

# Advanced settings
with st.expander("Advanced Settings & Assumptions"):
    st.subheader("Calculation Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Emission Factors Used:**")
        if vehicle_type == "Electric Vehicle":
            st.markdown(f"- Electricity Grid: **{grid_mix_factor:.3f} kg CO₂/kWh** "
                        f"({grid_mix_label})")
        st.markdown("- Diesel: 2.68 kg CO₂/liter")
    
    with col2:
        st.markdown("**Manufacturing Emissions:**")
        st.markdown("- Electric Vehicle: 8,500 kg CO2")
        st.markdown("- Diesel Vehicle: 6,200 kg CO2")
        st.markdown("- Includes battery production for EVs")

# Display calculation history
if st.session_state.data_handler.calculations_history:
    st.header("Calculation History")
    
    history_df = st.session_state.data_handler.get_calculations_df()
    st.dataframe(history_df, use_container_width=True, hide_index=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Clear History"):
            st.session_state.data_handler.clear_history()
            st.rerun()
    
    with col2:
        csv_data = st.session_state.data_handler.export_to_csv()
        if csv_data:
            st.download_button(
                "Download CSV",
                csv_data,
                "emission_calculations.csv",
                "text/csv"
            )
    
    with col3:
        json_data = st.session_state.data_handler.export_to_json()
        if json_data:
            st.download_button(
                "Download JSON",
                json_data,
                "emission_calculations.json",
                "application/json"
            )

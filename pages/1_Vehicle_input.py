import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.emission_calculator import EmissionCalculator
from utils.data_handler import DataHandler

st.set_page_config(page_title="Vehicle Input", page_icon="🚗", layout="wide")

st.title("🚗 Vehicle Specifications Input")
st.markdown("Enter detailed vehicle specifications and usage patterns for accurate emission calculations.")

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
                min_value=20.0,
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
            grid_mix = st.selectbox(
                "Electricity Grid Mix",
                ["US Average", "Coal Heavy", "Natural Gas", "Renewable Heavy"],
                help="Regional electricity generation source"
            )
            
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
                "grid_mix": grid_mix,
                "charging_type": charging_type,
                "battery_size": battery_size,
                "cold_weather": cold_weather
            })
            
            results = st.session_state.calculator.calculate_ev_emissions(
                annual_mileage, efficiency, grid_mix, vehicle_age
            )
        else:
            parameters.update({
                "engine_size": engine_size,
                "fuel_type": fuel_type,
                "emission_standard": emission_standard,
                "turbo": turbo
            })
            
            results = st.session_state.calculator.calculate_diesel_emissions(
                annual_mileage, efficiency, vehicle_age
            )
        
        # Save calculation
        st.session_state.data_handler.save_calculation(results, vehicle_type, parameters)
        
        # Display results
        st.success("Calculation Complete!")
        
        st.metric("Annual CO2 Emissions", f"{results['co2_annual']:.1f} kg")
        st.metric("Lifetime CO2 Emissions", f"{results['co2_lifetime']:.1f} kg")
        st.metric("Total w/ Manufacturing", f"{results['total_lifetime']:.1f} kg")
        
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
        st.markdown("- Diesel: 2.68 kg CO2/liter")
        st.markdown("- US Avg Grid: 0.386 kg CO2/kWh")
        st.markdown("- Coal Heavy Grid: 0.820 kg CO2/kWh")
        st.markdown("- Renewable Grid: 0.050 kg CO2/kWh")
    
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

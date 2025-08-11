import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.emission_calculator import EmissionCalculator
from utils.data_handler import DataHandler

st.set_page_config(page_title="Comparison Analysis", page_icon="⚖️", layout="wide")

st.title(" Multi-Scenario Comparison Analysis")
st.markdown("Compare multiple vehicle scenarios and analyze different driving patterns, efficiency levels, and grid mixes.")

# Initialize components
if 'calculator' not in st.session_state:
    st.session_state.calculator = EmissionCalculator()
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = DataHandler()

# Scenario builder
st.header("Scenario Builder")

# Initialize scenarios in session state
if 'scenarios' not in st.session_state:
    st.session_state.scenarios = []

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Create New Scenario")
    
    with st.form("scenario_form"):
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            scenario_name = st.text_input("Scenario Name", placeholder="e.g., Urban Commuter")
            vehicle_type = st.selectbox("Vehicle Type", ["Electric Vehicle", "Diesel Vehicle"])
            annual_mileage = st.number_input("Annual Mileage", min_value=1000, max_value=100000, value=12000)
        
        with col_b:
            if vehicle_type == "Electric Vehicle":
                efficiency = st.number_input("Efficiency (kWh/100mi)", min_value=20.0, max_value=60.0, value=34.0)
                grid_mix_factor= st.selectbox("Grid Mix", list(st.session_state.calculator.grid_factors.keys()))
                additional_param = grid_mix_factor
            else:
                efficiency = st.number_input("Efficiency (MPG)", min_value=15.0, max_value=60.0, value=30.0)
                fuel_type = st.selectbox("Fuel Type", ["Regular Diesel", "Bio-Diesel (B20)", "Renewable Diesel"])
                additional_param = fuel_type
        
        with col_c:
            years = st.number_input("Vehicle Lifetime", min_value=5, max_value=25, value=15)
            driving_pattern = st.selectbox("Driving Pattern", ["Mixed", "City", "Highway"])
        
        submitted = st.form_submit_button("Add Scenario", type="primary")
        
        if submitted and scenario_name:
            # Calculate emissions for scenario
            if vehicle_type == "Electric Vehicle":
                results = st.session_state.calculator.calculate_ev_emissions(
                    annual_mileage, efficiency, grid_mix_factor, years
                )
            else:
                results = st.session_state.calculator.calculate_diesel_emissions(
                    annual_mileage, efficiency, years
                )
            
            # Add to scenarios
            scenario = {
                "name": scenario_name,
                "vehicle_type": vehicle_type,
                "annual_mileage": annual_mileage,
                "efficiency": efficiency,
                "additional_param": additional_param,
                "years": years,
                "driving_pattern": driving_pattern,
                "results": results
            }
            
            st.session_state.scenarios.append(scenario)
            st.success(f"Added scenario: {scenario_name}")
            st.rerun()

with col2:
    st.subheader("Scenario Management")
    
    if st.session_state.scenarios:
        st.write(f"**Total Scenarios:** {len(st.session_state.scenarios)}")
        
        # List scenarios with remove option
        for i, scenario in enumerate(st.session_state.scenarios):
            col_name, col_remove = st.columns([3, 1])
            with col_name:
                st.write(f" {scenario['name']} ({scenario['vehicle_type']})")
            with col_remove:
                if st.button("❌", key=f"remove_{i}"):
                    st.session_state.scenarios.pop(i)
                    st.rerun()
        
        if st.button("Clear All Scenarios", type="secondary", key="clear_scenarios_btn1"):
            st.session_state.scenarios = []
            st.rerun()
    else:
        st.info("No scenarios created yet. Add scenarios using the form above.")

# Comparison analysis
if st.session_state.scenarios:
    st.header("Scenario Comparison Analysis")
    
    # Prepare data for comparison
    scenario_data = []
    for scenario in st.session_state.scenarios:
        scenario_data.append({
            "Scenario": scenario["name"],
            "Vehicle Type": scenario["vehicle_type"],
            "Annual CO2 (kg)": scenario["results"]["co2_annual"],
            "Lifetime CO2 (kg)": scenario["results"]["co2_lifetime"],
            "Total w/ Manufacturing (kg)": scenario["results"]["total_lifecycle"],
            "Annual Mileage": scenario["annual_mileage"],
            "Efficiency": scenario["efficiency"],
            "NOx (kg)": scenario["results"]["nox_annual"],
            "PM2.5 (kg)": scenario["results"]["pm25_annual"]
        })
    
    df_scenarios = pd.DataFrame(scenario_data)
    
    # Comparison charts
    tab1, tab2, tab3, tab4 = st.tabs(["CO2 Comparison", "All Pollutants", "Efficiency Analysis", "Cost Analysis"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Annual CO2 comparison
            fig_annual = px.bar(
                df_scenarios,
                x="Scenario",
                y="Annual CO2 (kg)",
                color="Vehicle Type",
                title="Annual CO2 Emissions by Scenario",
                color_discrete_map={"Electric Vehicle": "#2E8B57", "Diesel Vehicle": "#8B4513"}
            )
            fig_annual.update_xaxes(tickangle=45)
            st.plotly_chart(fig_annual, use_container_width=True)
        
        with col2:
            # Lifetime CO2 comparison
            fig_lifetime = px.bar(
                df_scenarios,
                x="Scenario",
                y="Lifetime CO2 (kg)",
                color="Vehicle Type",
                title="Lifetime CO2 Emissions by Scenario",
                color_discrete_map={"Electric Vehicle": "#2E8B57", "Diesel Vehicle": "#8B4513"}
            )
            fig_lifetime.update_xaxes(tickangle=45)
            st.plotly_chart(fig_lifetime, use_container_width=True)
        
        # Detailed comparison table
        st.subheader("Detailed Comparison Table")
        st.dataframe(df_scenarios, use_container_width=True, hide_index=True)
    
    with tab2:
        # Multi-pollutant radar chart
        if len(st.session_state.scenarios) >= 2:
            fig_radar = go.Figure()
            
            # Normalize pollutants for radar chart
            max_co2 = df_scenarios["Annual CO2 (kg)"].max()
            max_nox = df_scenarios["NOx (kg)"].max()
            max_pm25 = df_scenarios["PM2.5 (kg)"].max()
            
            for i, scenario in enumerate(st.session_state.scenarios[:5]):  # Limit to 5 scenarios
                normalized_values = [
                    scenario["results"]["co2_annual"] / max_co2 * 100,
                    scenario["results"]["nox_annual"] / max_nox * 100 if max_nox > 0 else 0,
                    scenario["results"]["pm25_annual"] / max_pm25 * 100 if max_pm25 > 0 else 0,
                    scenario["results"]["so2_annual"] / max(s["results"]["so2_annual"] for s in st.session_state.scenarios) * 100
                ]
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=normalized_values,
                    theta=['CO2', 'NOx', 'PM2.5', 'SO2'],
                    fill='toself',
                    name=scenario["name"]
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                title="Multi-Pollutant Comparison (Normalized %)",
                showlegend=True
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Pollutant breakdown chart
        pollutant_comparison = []
        for scenario in st.session_state.scenarios:
            pollutant_comparison.extend([
                {"Scenario": scenario["name"], "Pollutant": "CO2", "Emissions": scenario["results"]["co2_annual"]},
                {"Scenario": scenario["name"], "Pollutant": "NOx", "Emissions": scenario["results"]["nox_annual"]},
                {"Scenario": scenario["name"], "Pollutant": "PM2.5", "Emissions": scenario["results"]["pm25_annual"]},
                {"Scenario": scenario["name"], "Pollutant": "SO2", "Emissions": scenario["results"]["so2_annual"]}
            ])
        
        df_pollutants = pd.DataFrame(pollutant_comparison)
        
        fig_pollutants_grouped = px.bar(
            df_pollutants,
            x="Scenario",
            y="Emissions",
            color="Pollutant",
            title="Pollutant Emissions by Scenario",
            facet_row="Pollutant",
            log_y=True
        )
        fig_pollutants_grouped.update_xaxes(tickangle=45)
        st.plotly_chart(fig_pollutants_grouped, use_container_width=True)
    
    with tab3:
        # Efficiency vs Emissions analysis
        fig_efficiency = px.scatter(
            df_scenarios,
            x="Efficiency",
            y="Annual CO2 (kg)",
            color="Vehicle Type",
            size="Annual Mileage",
            hover_name="Scenario",
            title="Efficiency vs Annual CO2 Emissions",
            color_discrete_map={"Electric Vehicle": "#2E8B57", "Diesel Vehicle": "#8B4513"}
        )
        
        fig_efficiency.update_layout(
            xaxis_title="Efficiency (kWh/100mi for EV, MPG for Diesel)",
            yaxis_title="Annual CO2 Emissions (kg)"
        )
        
        st.plotly_chart(fig_efficiency, use_container_width=True)
        
        # Mileage impact analysis
        fig_mileage = px.scatter(
            df_scenarios,
            x="Annual Mileage",
            y="Annual CO2 (kg)",
            color="Vehicle Type",
            hover_name="Scenario",
            title="Annual Mileage vs CO2 Emissions",
            color_discrete_map={"Electric Vehicle": "#2E8B57", "Diesel Vehicle": "#8B4513"},
            trendline="ols"
        )
        
        st.plotly_chart(fig_mileage, use_container_width=True)
    
    with tab4:
        # Cost comparison analysis
        st.subheader("Cost Comparison Analysis")
        
        cost_data = []
        for scenario in st.session_state.scenarios:
            if scenario["vehicle_type"] == "Electric Vehicle":
                ev_dummy = {"electricity_annual_kwh": scenario["annual_mileage"] * scenario["efficiency"] / 100}
                diesel_dummy = {"fuel_annual_gallons": scenario["annual_mileage"] / 30}  # Assume 30 MPG for comparison
                costs = st.session_state.calculator.calculate_cost_comparison(diesel_dummy, ev_dummy)
                annual_cost = costs["ev_total_annual"]
            else:
                ev_dummy = {"electricity_annual_kwh": scenario["annual_mileage"] * 34 / 100}  # Assume 34 kWh/100mi
                diesel_dummy = {"fuel_annual_gallons": scenario["annual_mileage"] / scenario["efficiency"]}
                costs = st.session_state.calculator.calculate_cost_comparison(diesel_dummy, ev_dummy)
                annual_cost = costs["diesel_total_annual"]
            
            cost_data.append({
                "Scenario": scenario["name"],
                "Vehicle Type": scenario["vehicle_type"],
                "Annual Cost ($)": annual_cost,
                "Annual CO2 (kg)": scenario["results"]["co2_annual"],
                "Cost per kg CO2": annual_cost / scenario["results"]["co2_annual"] if scenario["results"]["co2_annual"] > 0 else 0
            })
        
        df_costs = pd.DataFrame(cost_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_cost_emissions = px.scatter(
                df_costs,
                x="Annual Cost ($)",
                y="Annual CO2 (kg)",
                color="Vehicle Type",
                hover_name="Scenario",
                title="Annual Cost vs CO2 Emissions",
                color_discrete_map={"Electric Vehicle": "#2E8B57", "Diesel Vehicle": "#8B4513"}
            )
            st.plotly_chart(fig_cost_emissions, use_container_width=True)
        
        with col2:
            fig_cost_efficiency = px.bar(
                df_costs,
                x="Scenario",
                y="Cost per kg CO2",
                color="Vehicle Type",
                title="Cost Efficiency ($/kg CO2)",
                color_discrete_map={"Electric Vehicle": "#2E8B57", "Diesel Vehicle": "#8B4513"}
            )
            fig_cost_efficiency.update_xaxes(tickangle=45)
            st.plotly_chart(fig_cost_efficiency, use_container_width=True)
        
        st.dataframe(df_costs, use_container_width=True, hide_index=True)

# Sensitivity analysis
st.header("Sensitivity Analysis")
GRID_COLORS = ["#1E7F4F", "#2B8757", "#339160", "#3D9C69", "#47A772",
               "#51B27B", "#5DBE85", "#69C98F", "#76D399", "#84DDA3"]
    


col1, col2 = st.columns(2)

with col1:
    st.subheader("Grid Mix Sensitivity (EVs)")
    
    base_mileage = 12000
    base_efficiency = 34.0
    
    grid_types = [list(st.session_state.calculator.grid_factors.keys())]
    grid_emissions = []
    
    for grid in grid_types:
        ev_calc = st.session_state.calculator.calculate_ev_emissions(base_mileage, base_efficiency, grid_mix_factor)
        grid_emissions.append(ev_calc["co2_annual"])
    # build a stable color map (scenario -> color)
        color_map = {name: GRID_COLORS[i % len(GRID_COLORS)]
                     for i, name in enumerate(grid_types)}
    fig_grid_sensitivity = go.Figure()
    fig_grid_sensitivity.add_trace(go.Bar(
        x=grid_types,
        y=grid_emissions,
        marker_color=[color_map[g] for g in grid_types] 
    ))
    
    fig_grid_sensitivity.update_layout(
        title="EV Emissions Sensitivity to Grid Mix",
        xaxis_title="Grid Type",
        yaxis_title="Annual CO2 (kg)"
    )
    
    st.plotly_chart(fig_grid_sensitivity, use_container_width=True)

with col2:
    st.subheader("Efficiency Sensitivity")
    
    efficiency_range = np.arange(20, 61, 5)  # 20-60 kWh/100mi for EVs
    mpg_range = np.arange(15, 61, 5)  # 15-60 MPG for diesel
    
    ev_emissions_eff = []
    diesel_emissions_eff = []
    
    for eff in efficiency_range:
        ev_calc = st.session_state.calculator.calculate_ev_emissions(base_mileage, eff, "US Average")
        ev_emissions_eff.append(ev_calc["co2_annual"])
    
    for mpg in mpg_range:
        diesel_calc = st.session_state.calculator.calculate_diesel_emissions(base_mileage, mpg)
        diesel_emissions_eff.append(diesel_calc["co2_annual"])
    
    fig_efficiency_sensitivity = go.Figure()
    fig_efficiency_sensitivity.add_trace(go.Scatter(
        x=efficiency_range, y=ev_emissions_eff,
        mode='lines+markers', name='Electric Vehicle',
        line=dict(color='#2E8B57', width=3)
    ))
    fig_efficiency_sensitivity.add_trace(go.Scatter(
        x=mpg_range, y=diesel_emissions_eff,
        mode='lines+markers', name='Diesel Vehicle',
        line=dict(color='#8B4513', width=3)
    ))
    
    fig_efficiency_sensitivity.update_layout(
        title="Emissions Sensitivity to Efficiency",
        xaxis_title="Efficiency (kWh/100mi for EV, MPG for Diesel)",
        yaxis_title="Annual CO2 (kg)"
    )
    
    st.plotly_chart(fig_efficiency_sensitivity, use_container_width=True)

# Export functionality
if st.session_state.scenarios:
    st.header("Export Scenario Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export to CSV", type="secondary"):
            csv_data = df_scenarios.to_csv(index=False)
            st.download_button(
                "Download Scenarios CSV",
                csv_data,
                "scenario_comparison.csv",
                "text/csv"
            )
    
    with col2:
        if st.button("Export Summary Report", type="secondary"):
            # Create summary report
            summary = f"""
# Scenario Comparison Summary Report

## Overview
- Total scenarios analyzed: {len(st.session_state.scenarios)}
- Electric vehicle scenarios: {len([s for s in st.session_state.scenarios if s['vehicle_type'] == 'Electric Vehicle'])}
- Diesel vehicle scenarios: {len([s for s in st.session_state.scenarios if s['vehicle_type'] == 'Diesel Vehicle'])}

## Key Findings
- Lowest annual emissions: {df_scenarios.loc[df_scenarios['Annual CO2 (kg)'].idxmin(), 'Scenario']} ({df_scenarios['Annual CO2 (kg)'].min():.1f} kg CO2)
- Highest annual emissions: {df_scenarios.loc[df_scenarios['Annual CO2 (kg)'].idxmax(), 'Scenario']} ({df_scenarios['Annual CO2 (kg)'].max():.1f} kg CO2)
- Average EV emissions: {df_scenarios[df_scenarios['Vehicle Type'] == 'Electric Vehicle']['Annual CO2 (kg)'].mean():.1f} kg CO2
- Average Diesel emissions: {df_scenarios[df_scenarios['Vehicle Type'] == 'Diesel Vehicle']['Annual CO2 (kg)'].mean():.1f} kg CO2

## Detailed Results
{df_scenarios.to_string(index=False)}
            """
            
            st.download_button(
                "Download Summary Report",
                summary,
                "scenario_summary.txt",
                "text/plain"
            )
    
    with col3:
        if st.button("Clear All Scenarios", type="secondary", key="clear_scenarios_btn"):
            st.session_state.scenarios = []
            st.rerun()

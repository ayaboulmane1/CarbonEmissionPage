import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.emission_calculator import EmissionCalculator
from utils.data_handler import DataHandler

st.set_page_config(page_title="Emissions Dashboard", page_icon="📊", layout="wide")

st.title("📊 Real-time Emissions Dashboard")
st.markdown("Interactive dashboard showing detailed emission calculations and comparisons.")

# Initialize components
if 'calculator' not in st.session_state:
    st.session_state.calculator = EmissionCalculator()
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = DataHandler()

# Top metrics row
st.header("Key Metrics Overview")

# Sample calculations for dashboard display
ev_sample = st.session_state.calculator.calculate_ev_emissions(12000, 34.0, "Deutschland 2025", 15)
diesel_sample = st.session_state.calculator.calculate_diesel_emissions(12000, 30.0, 15)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "EV Annual Emissions", 
        f"{ev_sample['co2_annual']:.0f} kg CO2",
        delta=f"-{diesel_sample['co2_annual'] - ev_sample['co2_annual']:.0f} kg vs Diesel"
    )

with col2:
    st.metric(
        "Diesel Annual Emissions", 
        f"{diesel_sample['co2_annual']:.0f} kg CO2",
        delta=f"+{diesel_sample['co2_annual'] - ev_sample['co2_annual']:.0f} kg vs EV"
    )

with col3:
    reduction_percent = ((diesel_sample['co2_annual'] - ev_sample['co2_annual']) / diesel_sample['co2_annual']) * 100
    st.metric(
        "Emission Reduction", 
        f"{reduction_percent:.1f}%",
        delta="EV advantage"
    )

with col4:
    lifetime_savings = diesel_sample['co2_lifetime'] - ev_sample['co2_lifetime']
    st.metric(
        "Lifetime CO2 Savings", 
        f"{lifetime_savings:.0f} kg",
        delta="15-year projection"
    )

# Interactive calculator section
st.header("Interactive Emission Calculator")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Input Parameters")
    
    # Real-time inputs
    rt_mileage = st.slider("Annual Mileage", 5000, 50000, 12000, 1000)
    rt_years = st.slider("Vehicle Lifetime (years)", 5, 25, 15)
    
    # EV parameters
    st.markdown("**Electric Vehicle:**")
    ev_efficiency = st.slider("EV Efficiency (kWh/100mi)", 20.0, 60.0, 34.0, 1.0)
    ev_grid = st.selectbox("Grid Mix", list(st.session_state.calculator.grid_factors.keys()))
    
    # Diesel parameters
    st.markdown("**Diesel Vehicle:**")
    diesel_efficiency = st.slider("Diesel Efficiency (MPG)", 15.0, 60.0, 30.0, 1.0)

with col2:
    st.subheader("Real-time Comparison")
    
    # Calculate real-time emissions
    ev_rt = st.session_state.calculator.calculate_ev_emissions(rt_mileage, ev_efficiency, ev_grid, rt_years)
    diesel_rt = st.session_state.calculator.calculate_diesel_emissions(rt_mileage, diesel_efficiency, rt_years)
    
    # Create comparison chart
    comparison_data = {
        "Vehicle Type": ["Electric Vehicle", "Diesel Vehicle"],
        "Annual CO2 (kg)": [ev_rt['co2_annual'], diesel_rt['co2_annual']],
        "Lifetime CO2 (kg)": [ev_rt['co2_lifetime'], diesel_rt['co2_lifetime']],
        "Total w/ Manufacturing (kg)": [ev_rt['total_lifecycle'], diesel_rt['total_lifecycle']]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    
    # Create grouped bar chart
    fig_comparison = go.Figure()
    
    fig_comparison.add_trace(go.Bar(
        name='Annual CO2',
        x=df_comparison['Vehicle Type'],
        y=df_comparison['Annual CO2 (kg)'],
        marker_color=['#2E8B57', '#8B4513']
    ))
    
    fig_comparison.update_layout(
        title="Annual CO2 Emissions Comparison",
        xaxis_title="Vehicle Type",
        yaxis_title="CO2 Emissions (kg)",
        showlegend=False
    )
    
    st.plotly_chart(fig_comparison, use_container_width=True)

# Detailed breakdown section
st.header("Detailed Emissions Breakdown")

tab1, tab2, tab3 = st.tabs(["CO2 Analysis", "All Pollutants", "Manufacturing Impact"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # CO2 over time
        years_range = list(range(1, rt_years + 1))
        ev_cumulative = [ev_rt['co2_annual'] * year for year in years_range]
        diesel_cumulative = [diesel_rt['co2_annual'] * year for year in years_range]
        
        fig_cumulative = go.Figure()
        fig_cumulative.add_trace(go.Scatter(
            x=years_range, y=ev_cumulative, mode='lines+markers',
            name='Electric Vehicle', line=dict(color='#2E8B57', width=3)
        ))
        fig_cumulative.add_trace(go.Scatter(
            x=years_range, y=diesel_cumulative, mode='lines+markers',
            name='Diesel Vehicle', line=dict(color='#8B4513', width=3)
        ))
        
        fig_cumulative.update_layout(
            title="Cumulative CO2 Emissions Over Time",
            xaxis_title="Years",
            yaxis_title="Cumulative CO2 (kg)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_cumulative, use_container_width=True)
    
    with col2:
        # Monthly breakdown
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        monthly_ev = [ev_rt['co2_annual'] / 12] * 12
        monthly_diesel = [diesel_rt['co2_annual'] / 12] * 12
        
        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Bar(
            x=months, y=monthly_ev, name='Electric Vehicle',
            marker_color='#2E8B57'
        ))
        fig_monthly.add_trace(go.Bar(
            x=months, y=monthly_diesel, name='Diesel Vehicle',
            marker_color='#8B4513'
        ))
        
        fig_monthly.update_layout(
            title="Monthly CO2 Emissions",
            xaxis_title="Month",
            yaxis_title="CO2 Emissions (kg)",
            barmode='group'
        )
        
        st.plotly_chart(fig_monthly, use_container_width=True)

with tab2:
    # All pollutants comparison
    pollutants_data = {
        "Pollutant": ["CO2", "NOx", "PM2.5", "SO2"],
        "Electric Vehicle": [
            ev_rt['co2_annual'],
            ev_rt['nox_annual'],
            ev_rt['pm25_annual'],
            ev_rt['so2_annual']
        ],
        "Diesel Vehicle": [
            diesel_rt['co2_annual'],
            diesel_rt['nox_annual'],
            diesel_rt['pm25_annual'],
            diesel_rt['so2_annual']
        ]
    }
    
    df_pollutants = pd.DataFrame(pollutants_data)
    
    # Normalize for better visualization (log scale)
    fig_pollutants = go.Figure()
    
    for vehicle in ["Electric Vehicle", "Diesel Vehicle"]:
        fig_pollutants.add_trace(go.Bar(
            name=vehicle,
            x=df_pollutants['Pollutant'],
            y=df_pollutants[vehicle],
            marker_color='#2E8B57' if vehicle == "Electric Vehicle" else '#8B4513'
        ))
    
    fig_pollutants.update_layout(
        title="Annual Pollutant Emissions Comparison",
        xaxis_title="Pollutant Type",
        yaxis_title="Emissions (kg)",
        yaxis_type="log",
        barmode='group'
    )
    
    st.plotly_chart(fig_pollutants, use_container_width=True)
    
    # Display data table
    st.subheader("Pollutant Emissions Data")
    st.dataframe(df_pollutants, use_container_width=True, hide_index=True)

with tab3:
    # Manufacturing impact analysis
    manufacturing_data = {
        "Component": ["Manufacturing", "15-Year Operation", "Total Lifetime"],
        "Electric Vehicle": [
            st.session_state.calculator.lifecycle_emissions["electric"]["total_manufacturing"],
            ev_rt['co2_lifetime'],
            ev_rt['total_lifecycle']
        ],
        "Diesel Vehicle": [
            st.session_state.calculator.lifecycle_emissions["diesel"]["total_manufacturing"],
            diesel_rt['co2_lifetime'],
            diesel_rt['total_lifecycle']
        ]
    }
    
    df_manufacturing = pd.DataFrame(manufacturing_data)
    
    # Stacked bar chart
    fig_manufacturing = go.Figure()
    
    fig_manufacturing.add_trace(go.Bar(
        name='Manufacturing',
        x=['Electric Vehicle', 'Diesel Vehicle'],
        y=[manufacturing_data["Electric Vehicle"][0], manufacturing_data["Diesel Vehicle"][0]],
        marker_color='lightblue'
    ))
    
    fig_manufacturing.add_trace(go.Bar(
        name='15-Year Operation',
        x=['Electric Vehicle', 'Diesel Vehicle'],
        y=[manufacturing_data["Electric Vehicle"][1], manufacturing_data["Diesel Vehicle"][1]],
        marker_color=['#2E8B57', '#8B4513']
    ))
    
    fig_manufacturing.update_layout(
        title="Lifecycle CO2 Emissions Breakdown",
        xaxis_title="Vehicle Type",
        yaxis_title="CO2 Emissions (kg)",
        barmode='stack'
    )
    
    st.plotly_chart(fig_manufacturing, use_container_width=True)

# Grid mix impact analysis
st.header("Electricity Grid Mix Impact Analysis")

grid_scenarios = list(st.session_state.calculator.grid_factors.keys())
grid_emissions = []

for grid in grid_scenarios:
    ev_grid_test = st.session_state.calculator.calculate_ev_emissions(rt_mileage, ev_efficiency, grid, rt_years)
    grid_emissions.append(ev_grid_test['co2_annual'])

fig_grid = go.Figure()
fig_grid.add_trace(go.Bar(
    x=grid_scenarios,
    y=grid_emissions,
    marker_color=[]
))

# Add diesel baseline
fig_grid.add_hline(
    y=diesel_rt['co2_annual'],
    line_dash="dash",
    line_color="red",
    annotation_text="Diesel Baseline"
)

fig_grid.update_layout(
    title="EV Emissions by Electricity Grid Mix",
    xaxis_title="Grid Mix Type",
    yaxis_title="Annual CO2 Emissions (kg)"
)

st.plotly_chart(fig_grid, use_container_width=True)

st.markdown("""
**Key Insights:**
- Electric vehicles show significant emission reductions even with coal-heavy grids
- Renewable energy grids can achieve up to 95% emission reduction compared to diesel
- Grid decarbonization directly improves EV environmental performance
""")

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.emission_calculator import EmissionCalculator
from utils.data_handler import DataHandler

st.set_page_config(page_title="Lifecycle Analysis", page_icon="🔄", layout="wide")

def create_waterfall_chart(lifecycle_data, vehicle_type):
    """Create a waterfall chart for lifecycle emissions"""
    phases = lifecycle_data["phases"]
    if vehicle_type == "Electric Vehicle":
        values = lifecycle_data["ev_emissions"]
        color = "#1E7F4F"
    else:
        values = lifecycle_data["diesel_emissions"]
        color = "#8B4513"
    
    # Create waterfall chart
    fig = go.Figure(go.Waterfall(
        name=vehicle_type,
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "total"],
        x=phases,
        y=values,
        connector={"line": {"color": "rgba(63, 63, 63, 0.2)"}},
        increasing={"marker": {"color": color}},
        decreasing={"marker": {"color": "#32CD32"}},
        totals={"marker": {"color": "#2F4F4F"}}
    ))
    
    fig.update_layout(
        title=f"{vehicle_type} - Lifecycle Emissions Breakdown",
        xaxis_title="Lifecycle Phase",
        yaxis_title="CO2 Emissions (kg)",
        showlegend=False
    )
    
    return fig

def create_sankey_diagram(ev_breakdown, diesel_breakdown):
    """Create Sankey diagram showing emission flows"""
    # Define nodes
    labels = [
        "Raw Materials", "Manufacturing", "Operation", "End of Life",
        "EV Total", "Diesel Total", "Battery Production", "Engine Production",
        "EV Operation", "Diesel Operation (Direct)", "Diesel Operation (Upstream)"
    ]
    
    # Define flows
    source = [0, 0, 1, 1, 2, 2, 2, 3, 3, 6, 7, 8, 9, 10]
    target = [4, 5, 4, 5, 4, 8, 9, 4, 5, 4, 5, 4, 5, 5]
    value = [
        ev_breakdown['raw_material_extraction'],
        diesel_breakdown['raw_material_extraction'],
        ev_breakdown['battery_production'] + ev_breakdown['vehicle_assembly'],
        diesel_breakdown['engine_production'] + diesel_breakdown['vehicle_assembly'],
        ev_breakdown['operation_direct'],
        ev_breakdown['operation_direct'],
        diesel_breakdown['operation_direct'],
        abs(ev_breakdown['end_of_life']),
        abs(diesel_breakdown['end_of_life']),
        ev_breakdown['battery_production'],
        diesel_breakdown['engine_production'],
        ev_breakdown['operation_direct'],
        diesel_breakdown['operation_direct'],
        diesel_breakdown['operation_upstream']
    ]
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=["#E8F5E8", "#E8F5E8", "#E8F5E8", "#32CD32", "#1E7F4F", "#8B4513", 
                   "#FFB6C1", "#DEB887", "#87CEEB", "#F4A460", "#F4A460"]
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=["rgba(30, 127, 79, 0.4)" if i % 2 == 0 else "rgba(139, 69, 19, 0.4)" for i in range(len(source))]
        ))])
    
    fig.update_layout(
        title_text="Lifecycle Emissions Flow Diagram",
        font_size=12,
        height=600
    )
    
    return fig

st.title("🔄 Comprehensive Lifecycle Analysis")
st.markdown("Deep dive into complete vehicle lifecycle emissions including manufacturing, operation, and end-of-life impacts.")

# Initialize components
if 'calculator' not in st.session_state:
    st.session_state.calculator = EmissionCalculator()
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = DataHandler()

# Input parameters
st.header("Lifecycle Analysis Parameters")

col1, col2, col3, col4 = st.columns(4)

with col1:
    lca_mileage = st.number_input("Annual Mileage", min_value=5000, max_value=50000, value=12000, step=1000)
    lca_years = st.number_input("Analysis Period (years)", min_value=5, max_value=30, value=15)

with col2:
    ev_efficiency = st.number_input("EV Efficiency (kWh/100mi)", min_value=20.0, max_value=60.0, value=34.0)
    diesel_efficiency = st.number_input("Diesel Efficiency (MPG)", min_value=15.0, max_value=60.0, value=30.0)

with col3:
    grid_mix = st.selectbox("Electricity Grid Mix", list(st.session_state.calculator.grid_factors.keys()))

with col4:
    analysis_type = st.selectbox("Analysis Scope", 
                                ["Standard Lifecycle", "Cradle-to-Grave", "Well-to-Wheel", "Tank-to-Wheel"])

# Calculate lifecycle analysis
if st.button("🔄 Run Comprehensive Lifecycle Analysis", type="primary", use_container_width=True):
    with st.spinner("Calculating comprehensive lifecycle emissions..."):
        lca_results = st.session_state.calculator.calculate_lifecycle_analysis(
            lca_mileage, ev_efficiency, diesel_efficiency, grid_mix, lca_years
        )
        
        st.session_state.lca_results = lca_results

# Display results if available
if 'lca_results' in st.session_state:
    lca_results = st.session_state.lca_results
    
    # Key metrics dashboard
    st.header("🎯 Key Lifecycle Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        payback_years = lca_results['carbon_payback_years']
        if payback_years != float('inf'):
            st.metric("Carbon Payback Period", f"{payback_years:.1f} years", 
                     "Time to offset manufacturing")
        else:
            st.metric("Carbon Payback Period", "Never", "EV worse than diesel")
    
    with col2:
        annual_savings = lca_results['annual_savings']
        st.metric("Annual CO2 Savings", f"{annual_savings:.0f} kg", 
                 f"{(annual_savings/lca_results['diesel_results']['co2_annual']*100):.1f}% reduction")
    
    with col3:
        total_savings = lca_results['total_savings_15_years']
        st.metric(,f"{years:.0f} Year Total Savings", f"{total_savings:.0f} kg", 
                 "EV advantage over lifetime")
    
    with col4:
        ev_total = lca_results['ev_results']['total_lifecycle']
        diesel_total = lca_results['diesel_results']['total_lifecycle']
        lifecycle_reduction = (diesel_total - ev_total) / diesel_total * 100
        st.metric("Lifecycle Reduction", f"{lifecycle_reduction:.1f}%", 
                 "Total environmental benefit")
    
    with col5:
        trees_equivalent = total_savings / 22  # kg CO2 per tree per year
        st.metric("Trees Equivalent", f"{trees_equivalent:.0f} trees", 
                 "CO2 offset equivalent")
    
    # Detailed analysis tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏭 Manufacturing Analysis", "⚡ Operation Analysis", "📊 Complete Lifecycle", 
        "🌱 Future Projections", "📈 Sensitivity Analysis"
    ])
    
    with tab1:
        st.subheader("Manufacturing Emissions Breakdown")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # EV manufacturing breakdown
            ev_manufacturing = {
                "Component": ["Raw Material Extraction", "Battery Production", "Vehicle Assembly", "Transportation", "Total"],
                "Emissions (kg CO2)": [
                    lca_results['ev_results']['lifecycle_breakdown']['raw_material_extraction'],
                    lca_results['ev_results']['lifecycle_breakdown']['battery_production'],
                    lca_results['ev_results']['lifecycle_breakdown']['vehicle_assembly'],
                    lca_results['ev_results']['lifecycle_breakdown']['transportation'],
                    lca_results['ev_results']['manufacturing_emissions']
                ]
            }
            
            fig_ev_mfg = px.pie(
                values=ev_manufacturing["Emissions (kg CO2)"][:-1],  # Exclude total
                names=ev_manufacturing["Component"][:-1],
                title="EV Manufacturing Emissions",
                color_discrete_sequence=px.colors.sequential.Greens_r
            )
            st.plotly_chart(fig_ev_mfg, use_container_width=True)
        
        with col2:
            # Diesel manufacturing breakdown
            diesel_manufacturing = {
                "Component": ["Raw Material Extraction", "Engine Production", "Vehicle Assembly", "Transportation", "Total"],
                "Emissions (kg CO2)": [
                    lca_results['diesel_results']['lifecycle_breakdown']['raw_material_extraction'],
                    lca_results['diesel_results']['lifecycle_breakdown']['engine_production'],
                    lca_results['diesel_results']['lifecycle_breakdown']['vehicle_assembly'],
                    lca_results['diesel_results']['lifecycle_breakdown']['transportation'],
                    lca_results['diesel_results']['manufacturing_emissions']
                ]
            }
            
            fig_diesel_mfg = px.pie(
                values=diesel_manufacturing["Emissions (kg CO2)"][:-1],  # Exclude total
                names=diesel_manufacturing["Component"][:-1],
                title="Diesel Manufacturing Emissions",
                color_discrete_sequence=px.colors.sequential.Oranges_r
            )
            st.plotly_chart(fig_diesel_mfg, use_container_width=True)
        
        # Manufacturing comparison table
        st.subheader("Manufacturing Comparison")
        manufacturing_comparison = pd.DataFrame({
            "Manufacturing Phase": ["Raw Materials", "Primary Component", "Vehicle Assembly", "Transportation", "Total"],
            "Electric Vehicle (kg CO2)": [
                ev_manufacturing["Emissions (kg CO2)"][0],
                ev_manufacturing["Emissions (kg CO2)"][1],
                ev_manufacturing["Emissions (kg CO2)"][2],
                ev_manufacturing["Emissions (kg CO2)"][3],
                ev_manufacturing["Emissions (kg CO2)"][4]
            ],
            "Diesel Vehicle (kg CO2)": [
                diesel_manufacturing["Emissions (kg CO2)"][0],
                diesel_manufacturing["Emissions (kg CO2)"][1],
                diesel_manufacturing["Emissions (kg CO2)"][2],
                diesel_manufacturing["Emissions (kg CO2)"][3],
                diesel_manufacturing["Emissions (kg CO2)"][4]
            ],
            "Difference (kg CO2)": [
                ev_manufacturing["Emissions (kg CO2)"][i] - diesel_manufacturing["Emissions (kg CO2)"][i]
                for i in range(5)
            ]
        })
        
        st.dataframe(manufacturing_comparison, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("Operational Emissions Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Operation breakdown for both vehicles
            operation_data = {
                "Vehicle Type": ["Electric Vehicle", "Electric Vehicle", "Diesel Vehicle", "Diesel Vehicle"],
                "Emission Source": ["Direct (Grid)", "Upstream (Infrastructure)", 
                                  "Direct (Tailpipe)", "Upstream (Fuel Cycle)"],
                "Annual Emissions (kg CO2)": [
                    lca_results['ev_results']['co2_annual_direct'],
                    lca_results['ev_results']['co2_annual_upstream'],
                    lca_results['diesel_results']['co2_annual_direct'],
                    lca_results['diesel_results']['co2_annual_upstream']
                ]
            }
            
            fig_operation = px.bar(
                operation_data,
                x="Vehicle Type",
                y="Annual Emissions (kg CO2)",
                color="Emission Source",
                title="Annual Operational Emissions Breakdown",
                color_discrete_map={
                    "Direct (Grid)": "#1E7F4F",
                    "Upstream (Infrastructure)": "#90EE90",
                    "Direct (Tailpipe)": "#8B4513",
                    "Upstream (Fuel Cycle)": "#D2B48C"
                }
            )
            st.plotly_chart(fig_operation, use_container_width=True)
        
        with col2:
            # Cumulative operational emissions over time
            years_range = list(range(1, lca_years + 1))
            ev_cumulative = [lca_results['ev_results']['co2_annual'] * year for year in years_range]
            diesel_cumulative = [lca_results['diesel_results']['co2_annual'] * year for year in years_range]
            
            fig_cumulative = go.Figure()
            fig_cumulative.add_trace(go.Scatter(
                x=years_range, y=ev_cumulative,
                mode='lines+markers', name='Electric Vehicle',
                line=dict(color='#1E7F4F', width=3),
                fill='tonexty' if years_range[0] != 1 else 'tozeroy'
            ))
            fig_cumulative.add_trace(go.Scatter(
                x=years_range, y=diesel_cumulative,
                mode='lines+markers', name='Diesel Vehicle',
                line=dict(color='#8B4513', width=3),
                fill='tonexty'
            ))
            
            # Add carbon payback point
            if lca_results['carbon_payback_years'] != float('inf') and lca_results['carbon_payback_years'] <= lca_years:
                payback_year = lca_results['carbon_payback_years']
                payback_emissions = lca_results['ev_results']['co2_annual'] * payback_year + lca_results['manufacturing_difference']
                
                fig_cumulative.add_vline(
                    x=payback_year,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Carbon Payback: {payback_year:.1f} years"
                )
            
            fig_cumulative.update_layout(
                title="Cumulative Operational Emissions",
                xaxis_title="Years",
                yaxis_title="Cumulative CO2 Emissions (kg)"
            )
            
            st.plotly_chart(fig_cumulative, use_container_width=True)
    
    with tab3:
        st.subheader("Complete Lifecycle Emissions")
        
        # Waterfall charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig_ev_waterfall = create_waterfall_chart(lca_results['lifecycle_comparison'], "Electric Vehicle")
            st.plotly_chart(fig_ev_waterfall, use_container_width=True)
        
        with col2:
            fig_diesel_waterfall = create_waterfall_chart(lca_results['lifecycle_comparison'], "Diesel Vehicle")
            st.plotly_chart(fig_diesel_waterfall, use_container_width=True)
        
        # Sankey diagram
        st.subheader("Emissions Flow Analysis")
        fig_sankey = create_sankey_diagram(
            lca_results['ev_results']['lifecycle_breakdown'],
            lca_results['diesel_results']['lifecycle_breakdown']
        )
        st.plotly_chart(fig_sankey, use_container_width=True)
        
        # Complete lifecycle table
        st.subheader("Complete Lifecycle Emissions Table")
        lifecycle_df = pd.DataFrame({
            "Lifecycle Phase": lca_results['lifecycle_comparison']['phases'],
            "Electric Vehicle (kg CO2)": lca_results['lifecycle_comparison']['ev_emissions'],
            "Diesel Vehicle (kg CO2)": lca_results['lifecycle_comparison']['diesel_emissions'],
            "Difference (kg CO2)": [
                diesel - ev for diesel, ev in zip(
                    lca_results['lifecycle_comparison']['diesel_emissions'],
                    lca_results['lifecycle_comparison']['ev_emissions']
                )
            ],
            "EV Advantage (%)": [
                ((diesel - ev) / diesel * 100) if diesel != 0 else 0
                for diesel, ev in zip(
                    lca_results['lifecycle_comparison']['diesel_emissions'],
                    lca_results['lifecycle_comparison']['ev_emissions']
                )
            ]
        })
        
        st.dataframe(lifecycle_df, use_container_width=True, hide_index=True)
    
    with tab4:
        st.subheader("Future Grid Decarbonization Projections")
        
        # Grid decarbonization projections
        projections = st.session_state.calculator.get_grid_decarbonization_projection(
            lca_mileage, ev_efficiency, lca_years
        )
        
        # Create projection chart
        fig_projection = go.Figure()
        
        years_range = list(range(1, lca_years + 1))
        colors = {"US Average": "#4682B4", "Coal Heavy": "#8B4513", 
                 "Natural Gas": "#FFA500", "Renewable Heavy": "#228B22"}
        
        for grid_type, emissions in projections.items():
            fig_projection.add_trace(go.Scatter(
                x=years_range, y=emissions,
                mode='lines+markers', name=grid_type,
                line=dict(color=colors.get(grid_type, "#666666"), width=3)
            ))
        
        # Add diesel baseline
        diesel_baseline = [lca_results['diesel_results']['co2_annual']] * lca_years
        fig_projection.add_trace(go.Scatter(
            x=years_range, y=diesel_baseline,
            mode='lines', name='Diesel Baseline',
            line=dict(color='red', dash='dash', width=2)
        ))
        
        fig_projection.update_layout(
            title="EV Emissions with Grid Decarbonization (3% annual improvement)",
            xaxis_title="Years",
            yaxis_title="Annual CO2 Emissions (kg)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_projection, use_container_width=True)
        
        # Future savings calculation
        future_savings = {}
        for grid_type, emissions in projections.items():
            total_emissions = sum(emissions)
            baseline_emissions = st.session_state.calculator.grid_factors[grid_type] * (lca_mileage / 100) * ev_efficiency * lca_years
            savings = baseline_emissions - total_emissions
            future_savings[grid_type] = {
                "current_total": baseline_emissions,
                "future_total": total_emissions,
                "additional_savings": savings
            }
        
        st.subheader("Additional Savings from Grid Decarbonization")
        savings_data = []
        for grid_type, data in future_savings.items():
            savings_data.append({
                "Grid Type": grid_type,
                "Current Projection (kg CO2)": f"{data['current_total']:.0f}",
                "With Decarbonization (kg CO2)": f"{data['future_total']:.0f}",
                "Additional Savings (kg CO2)": f"{data['additional_savings']:.0f}",
                "Improvement (%)": f"{(data['additional_savings'] / data['current_total'] * 100):.1f}%"
            })
        
        st.dataframe(pd.DataFrame(savings_data), use_container_width=True, hide_index=True)
    
    with tab5:
        st.subheader("Sensitivity Analysis")
        
        # Parameter ranges for sensitivity analysis
        mileage_range = np.arange(8000, 25000, 2000)
        efficiency_range_ev = np.arange(25, 55, 5)
        efficiency_range_diesel = np.arange(20, 50, 5)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Mileage sensitivity
            payback_sensitivity_mileage = []
            savings_sensitivity_mileage = []
            
            for mileage in mileage_range:
                temp_lca = st.session_state.calculator.calculate_lifecycle_analysis(
                    mileage, ev_efficiency, diesel_efficiency, grid_mix, lca_years
                )
                payback_sensitivity_mileage.append(temp_lca['carbon_payback_years'])
                savings_sensitivity_mileage.append(temp_lca['annual_savings'])
            
            fig_mileage_sensitivity = go.Figure()
            fig_mileage_sensitivity.add_trace(go.Scatter(
                x=mileage_range, y=payback_sensitivity_mileage,
                mode='lines+markers', name='Carbon Payback Period',
                line=dict(color='#1E7F4F', width=3)
            ))
            
            fig_mileage_sensitivity.update_layout(
                title="Carbon Payback Sensitivity to Annual Mileage",
                xaxis_title="Annual Mileage",
                yaxis_title="Payback Period (years)"
            )
            
            st.plotly_chart(fig_mileage_sensitivity, use_container_width=True)
        
        with col2:
            # Efficiency sensitivity heatmap
            payback_matrix = []
            for ev_eff in efficiency_range_ev:
                row = []
                for diesel_eff in efficiency_range_diesel:
                    temp_lca = st.session_state.calculator.calculate_lifecycle_analysis(
                        lca_mileage, ev_eff, diesel_eff, grid_mix, lca_years
                    )
                    payback = temp_lca['carbon_payback_years']
                    row.append(min(payback, 20))  # Cap at 20 years for visualization
                payback_matrix.append(row)
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=payback_matrix,
                x=efficiency_range_diesel,
                y=efficiency_range_ev,
                colorscale='RdYlGn_r',
                colorbar=dict(title="Payback Period (years)")
            ))
            
            fig_heatmap.update_layout(
                title="Carbon Payback Period Sensitivity",
                xaxis_title="Diesel Efficiency (MPG)",
                yaxis_title="EV Efficiency (kWh/100mi)"
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)

else:
    st.info("👆 Configure your analysis parameters and click 'Run Comprehensive Lifecycle Analysis' to see detailed results.")
    
    # Show sample lifecycle comparison
    st.header("Sample Lifecycle Comparison")
    
    sample_lca = st.session_state.calculator.calculate_lifecycle_analysis(
        12000, 34.0, 30.0, "US Average", 15
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Carbon Payback Period", f"{sample_lca['carbon_payback_years']:.1f} years")
    
    with col2:
        st.metric("Annual CO2 Savings", f"{sample_lca['annual_savings']:.0f} kg")
    
    with col3:
        st.metric("15-Year Total Savings", f"{sample_lca['total_savings_15_years']:.0f} kg")
    
    # Sample waterfall charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_sample_ev = create_waterfall_chart(sample_lca['lifecycle_comparison'], "Electric Vehicle")
        st.plotly_chart(fig_sample_ev, use_container_width=True)
    
    with col2:
        fig_sample_diesel = create_waterfall_chart(sample_lca['lifecycle_comparison'], "Diesel Vehicle")
        st.plotly_chart(fig_sample_diesel, use_container_width=True)

# Information section
st.header("📚 Lifecycle Analysis Methodology")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🏭 Manufacturing Phase")
    st.markdown("""
    **Includes:**
    - Raw material extraction and processing
    - Component manufacturing (battery/engine)
    - Vehicle assembly and testing
    - Transportation to dealership
    
    **Key Differences:**
    - EV: Higher due to battery production
    - Diesel: Lower manufacturing footprint
    """)

with col2:
    st.subheader("⚡ Operation Phase")
    st.markdown("""
    **Includes:**
    - Direct emissions (tailpipe/grid)
    - Upstream emissions (fuel cycle/transmission)
    - Maintenance and repairs
    - Infrastructure impact
    
    **Key Factors:**
    - Grid electricity mix for EVs
    - Fuel efficiency for both
    """)

with col3:
    st.subheader("♻️ End-of-Life Phase")
    st.markdown("""
    **Includes:**
    - Vehicle dismantling
    - Material recycling benefits
    - Waste disposal impacts
    - Component reuse potential
    
    **Benefits:**
    - Battery recycling (EVs)
    - Metal recovery (both)
    """)

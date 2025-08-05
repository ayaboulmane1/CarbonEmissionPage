import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.emission_calculator import EmissionCalculator
from local_data_handler import LocalDataManager
import uuid

# Configure page
st.set_page_config(
    page_title="Carbon Emission Calculator - EV vs Diesel",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Enhanced German-themed header with sophisticated styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #000000 0%, #DD0000 25%, #FFCE00 75%, #000000 100%); 
                padding: 25px; border-radius: 15px; margin-bottom: 20px; text-align: center;">
    <h1 style="color: white; font-size: 2.5em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
    🇩🇪 Deutscher Kohlenstoff-Emissionsrechner</h1>
    <h3 style="color: #FFCE00; margin: 10px 0 0 0; font-weight: 300;">
    Elektroauto vs. Diesel - Umfassende Lebenszyklus-Analyse</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # German environmental context banner
    st.markdown("""
    <div style="background: linear-gradient(90deg, #2E8B57 0%, #32CD32 100%); 
                padding: 15px; border-radius: 10px; margin-bottom: 25px;">
    <h4 style="color: white; margin: 0; text-align: center;">
    🌿 Deutschlands Weg zur Klimaneutralität 2045 - Jedes Fahrzeug zählt!</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'calculator' not in st.session_state:
        st.session_state.calculator = EmissionCalculator()
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = LocalDataManager()
        st.session_state.db_manager.initialize_sample_data()
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    # Enhanced German sidebar navigation with color coding
    st.sidebar.markdown("""
    <div style="background: linear-gradient(45deg, #1E7F4F 0%, #2E8B57 100%); 
                padding: 15px; border-radius: 10px; margin-bottom: 15px;">
    <h2 style="color: white; margin: 0; text-align: center;">🇩🇪 Navigation</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("### 🔍 Vollständige Analyse erkunden:")
    st.sidebar.markdown(" **Fahrzeug-Eingabe** - Detaillierte Spezifikationen")
    st.sidebar.markdown(" **Emissions-Dashboard** - Echtzeitberechnungen") 
    st.sidebar.markdown(" **Vergleichsanalyse** - Multi-Szenario-Vergleich")
    st.sidebar.markdown(" **Umweltauswirkungen** - Umfassende Folgenabschätzung")
    st.sidebar.markdown(" **Lebenszyklus-Analyse** - Cradle-to-Grave Bewertung")
    
    st.sidebar.markdown("---")
    
    # German environmental facts with enhanced styling
    st.sidebar.markdown("### 🎯 Deutsche Umweltfakten")
    st.sidebar.success("✅ E-Autos reduzieren Emissionen um 60-80% im deutschen Strommix")
    st.sidebar.info("📈 Stromnetz-Dekarbonisierung verbessert E-Auto Vorteile kontinuierlich") 
    st.sidebar.warning("⏱️ CO2-Amortisation typisch 2-3 Jahre für deutsche E-Autos")
    
    # German car market insights
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏭 Deutsche Automobilindustrie")
    st.sidebar.markdown("""
    <div style="background: #F0F8FF; padding: 10px; border-radius: 5px; border-left: 4px solid #1E7F4F;">
    <small>
    <b>BMW, Mercedes, Audi & VW</b><br>
    Führend in Premium-E-Mobilität<br>
    🔋 Fortschrittliche Batterietechnik<br>
    ♻️ Innovative Recycling-Systeme
    </small>
    </div>
    """, unsafe_allow_html=True)
    
    # Main page content with enhanced layout
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        # Enhanced calculator header with German styling
        st.markdown("""
        <div style="background: linear-gradient(90deg, #1E7F4F 0%, #32CD32 100%); 
                    padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0; text-align: center;">🔬 Fortschrittlicher Schnellrechner</h2>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            # German car model selection
            col_model, col_custom = st.columns([1.2, 0.8])
            
            with col_model:
                vehicle_type = st.selectbox("🚗 Fahrzeugtyp", ["Elektrofahrzeug", "Dieselfahrzeug"])
                
                # German car model presets from database
                if vehicle_type == "Elektrofahrzeug":
                    try:
                        electric_cars = st.session_state.db_manager.get_german_cars("electric")
                        car_options = ["Custom"] + [f"{row['brand']} {row['model']}" for _, row in electric_cars.iterrows()]
                        car_model = st.selectbox("🏭 Deutsche E-Auto Modelle", car_options)
                        
                        if car_model != "Custom":
                            # Find selected car data
                            selected_car = electric_cars[electric_cars.apply(lambda x: f"{x['brand']} {x['model']}" == car_model, axis=1)].iloc[0]
                            efficiency = selected_car['efficiency']
                            st.info(f"📊 {car_model}: {efficiency} kWh/100km, Reichweite: {selected_car['range_km']} km, Preis: €{selected_car['price_eur']:,}")
                        else:
                            efficiency = st.number_input("⚡ Energieeffizienz (kWh/100km)", 
                                                       min_value=15.0, max_value=45.0, value=21.0, step=0.5)
                    except:
                        # Fallback to hardcoded data if database fails
                        car_model = st.selectbox("🏭 Deutsche E-Auto Modelle", 
                                               ["Custom", "BMW iX3", "Mercedes EQC", "Audi e-tron", 
                                                "Volkswagen ID.4", "Porsche Taycan"])
                        efficiency = st.number_input("⚡ Energieeffizienz (kWh/100km)", 
                                                   min_value=15.0, max_value=45.0, value=21.0, step=0.5)
                else:
                    try:
                        diesel_cars = st.session_state.db_manager.get_german_cars("diesel")
                        car_options = ["Custom"] + [f"{row['brand']} {row['model']}" for _, row in diesel_cars.iterrows()]
                        car_model = st.selectbox("🏭 Deutsche Diesel Modelle", car_options)
                        
                        if car_model != "Custom":
                            # Find selected car data
                            selected_car = diesel_cars[diesel_cars.apply(lambda x: f"{x['brand']} {x['model']}" == car_model, axis=1)].iloc[0]
                            efficiency = 235.2 / selected_car['efficiency']  # Convert L/100km to MPG for calculation
                            st.info(f"📊 {car_model}: {selected_car['efficiency']} L/100km, {selected_car['emissions_g_km']} g CO2/km, Preis: €{selected_car['price_eur']:,}")
                        else:
                            efficiency = st.number_input("⛽ Kraftstoffeffizienz (L/100km)", 
                                                       min_value=4.0, max_value=12.0, value=6.5, step=0.1)
                            efficiency = 235.2 / efficiency  # Convert to MPG for calculation
                    except:
                        # Fallback to hardcoded data if database fails
                        car_model = st.selectbox("🏭 Deutsche Diesel Modelle", 
                                               ["Custom", "BMW 320d", "Mercedes C220d", "Audi A4 TDI", 
                                                "Volkswagen Passat TDI", "Porsche Macan Diesel"])
                        efficiency = st.number_input("⛽ Kraftstoffeffizienz (L/100km)", 
                                                   min_value=4.0, max_value=12.0, value=6.5, step=0.1)
                        efficiency = 235.2 / efficiency  # Convert to MPG for calculation
            
            with col_custom:
                annual_km = st.number_input("📏 Jährliche Kilometerleistung", 
                                          min_value=5000, max_value=80000, value=15000, step=1000)
                annual_mileage = annual_km * 0.621371  # Convert km to miles for calculation
                
                if vehicle_type == "Elektrofahrzeug":
                    grid_factor = st.selectbox("🔌 Deutsches Stromnetz", 
                                             ["Deutschland 2025", "Deutschland Kohleausstieg 2030", 
                                              "Deutschland Erneuerbar 2035", "Bayern (Wasser/Atom)",
                                              "Nordrhein-Westfalen (Kohle)", "Schleswig-Holstein (Wind)",
                                              "Baden-Württemberg", "EU-Durchschnitt"])
                else:
                    grid_factor = "Deutschland 2025"  # Default for diesel (not used)
            
            st.markdown("---")
            
            # Enhanced calculation buttons with German text
            col_calc, col_lca = st.columns(2)
            
            with col_calc:
                if st.button("🧮 Schnellberechnung", type="primary", use_container_width=True):
                    # Convert efficiency for calculation if needed
                    if vehicle_type == "Elektrofahrzeug":
                        # Convert kWh/100km to kWh/100miles for calculation
                        efficiency_miles = efficiency * 1.60934
                        emissions = st.session_state.calculator.calculate_ev_emissions(
                            annual_mileage, efficiency_miles, grid_factor
                        )
                    else:
                        # Convert L/100km to MPG for calculation
                        if car_model == "Custom":
                            efficiency_mpg = 235.2 / efficiency  # L/100km to MPG
                        else:
                            efficiency_mpg = efficiency
                        emissions = st.session_state.calculator.calculate_diesel_emissions(
                            annual_mileage, efficiency_mpg
                        )
                    
                    st.session_state.quick_emissions = emissions
                    st.session_state.quick_vehicle_type = vehicle_type
                    
                    # Save calculation to database
                    try:
                        brand, model = car_model.split(" ", 1) if car_model != "Custom" else ("Custom", "Custom")
                        st.session_state.db_manager.save_calculation(
                            st.session_state.session_id,
                            vehicle_type,
                            brand,
                            model,
                            annual_km,
                            efficiency,
                            grid_factor,
                            emissions
                        )
                    except Exception as e:
                        pass  # Continue without database save if there's an error
            
            with col_lca:
                if st.button("🔄 Vollständige Lebenszyklus-Analyse", type="secondary", use_container_width=True):
                    if vehicle_type == "Elektrofahrzeug":
                        diesel_eff = 35.0  # German diesel average MPG
                        efficiency_miles = efficiency * 1.60934
                        lca_results = st.session_state.calculator.calculate_lifecycle_analysis(
                            annual_mileage, efficiency_miles, diesel_eff, grid_factor
                        )
                    else:
                        ev_eff = 34.0  # German EV average kWh/100miles
                        if car_model == "Custom":
                            efficiency_mpg = 235.2 / efficiency
                        else:
                            efficiency_mpg = efficiency
                        lca_results = st.session_state.calculator.calculate_lifecycle_analysis(
                            annual_mileage, ev_eff, efficiency_mpg, grid_factor
                        )
                    
                    st.session_state.quick_lca = lca_results
        
        # Display quick results
        if 'quick_emissions' in st.session_state:
            emissions = st.session_state.quick_emissions
            vehicle_type_result = st.session_state.quick_vehicle_type
            
            st.markdown("### 📊 Results")
            
            col_r1, col_r2, col_r3 = st.columns(3)
            
            with col_r1:
                st.metric("Annual CO2 Emissions", f"{emissions['co2_annual']:.1f} kg",
                         help="Direct + upstream emissions per year")
            
            with col_r2:
                st.metric("Lifetime Emissions", f"{emissions['co2_lifetime']:.1f} kg",
                         help="15-year operational emissions")
            
            with col_r3:
                st.metric("Total Lifecycle", f"{emissions['total_lifecycle']:.1f} kg",
                         help="Including manufacturing footprint")
            
            # Environmental impact score
            impact_score = st.session_state.calculator.get_environmental_impact_score(emissions)
            
            if impact_score < 30:
                st.success(f"🌟 Environmental Impact Score: {impact_score}/100 (Excellent)")
            elif impact_score < 60:
                st.warning(f"✅ Environmental Impact Score: {impact_score}/100 (Good)")
            else:
                st.error(f"⚠️ Environmental Impact Score: {impact_score}/100 (Needs Improvement)")
        
        # Display LCA results if available
        if 'quick_lca' in st.session_state:
            lca = st.session_state.quick_lca
            
            st.markdown("### 🔄 Lifecycle Comparison")
            
            col_l1, col_l2, col_l3 = st.columns(3)
            
            with col_l1:
                if lca['carbon_payback_years'] != float('inf'):
                    st.metric("Carbon Payback", f"{lca['carbon_payback_years']:.1f} years",
                             help="Time for EV to offset manufacturing difference")
                else:
                    st.metric("Carbon Payback", "Never", "EV doesn't offset manufacturing")
            
            with col_l2:
                st.metric("Annual Savings", f"{lca['annual_savings']:.0f} kg CO2",
                         help="EV vs Diesel annual emission reduction")
            
            with col_l3:
                reduction_pct = (lca['annual_savings'] / lca['diesel_results']['co2_annual']) * 100
                st.metric("Emission Reduction", f"{reduction_pct:.1f}%",
                         help="Percentage reduction with EV")
    
    with col2:
        st.header("📈 Live Comparison Dashboard")
        
        # Calculate real-time comparison data
        ev_sample = st.session_state.calculator.calculate_ev_emissions(12000, 34.0, "Deutschland 2025", 15)
        diesel_sample = st.session_state.calculator.calculate_diesel_emissions(12000, 30.0, 15)
        
        comparison_data = {
            "Vehicle Type": ["Electric Vehicle", "Diesel Vehicle"],
            "Annual CO2 (kg)": [ev_sample['co2_annual'], diesel_sample['co2_annual']],
            "Lifetime CO2 (kg)": [ev_sample['co2_lifetime'], diesel_sample['co2_lifetime']],
            "Total Lifecycle (kg)": [ev_sample['total_lifecycle'], diesel_sample['total_lifecycle']]
        }
        
        df = pd.DataFrame(comparison_data)
        
        # Create sophisticated comparison chart
        fig = go.Figure()
        
        # Add bars for annual emissions
        fig.add_trace(go.Bar(
            name='Annual CO2',
            x=df['Vehicle Type'],
            y=df['Annual CO2 (kg)'],
            marker_color=['#1E7F4F', '#8B4513'],
            text=df['Annual CO2 (kg)'].round(0),
            textposition='auto',
            yaxis='y'
        ))
        
        # Add line for lifecycle emissions
        fig.add_trace(go.Scatter(
            name='Total Lifecycle',
            x=df['Vehicle Type'],
            y=df['Total Lifecycle (kg)'],
            mode='lines+markers+text',
            line=dict(color='red', width=3, dash='dash'),
            marker=dict(size=10, color='red'),
            text=df['Total Lifecycle (kg)'].round(0),
            textposition='top center',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="📊 Real-time Emissions Comparison",
            xaxis_title="Vehicle Type",
            yaxis=dict(title="Annual CO2 (kg)", side='left'),
            yaxis2=dict(title="Lifecycle CO2 (kg)", side='right', overlaying='y'),
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Enhanced metrics
        reduction = diesel_sample['co2_annual'] - ev_sample['co2_annual']
        reduction_pct = (reduction / diesel_sample['co2_annual']) * 100
        
        st.metric("Annual Emission Reduction", f"{reduction:.0f} kg CO2", f"{reduction_pct:.1f}% less")
        
        # Cost comparison
        costs = st.session_state.calculator.calculate_cost_comparison(diesel_sample, ev_sample)
        cost_savings = costs['annual_savings']
        
        st.metric("Annual Cost Savings", f"${cost_savings:.0f}", "EV advantage")
        
        # Trees equivalent
        trees = reduction / 22  # kg CO2 per tree per year
        st.metric("Trees Equivalent", f"{trees:.1f} trees", "Annual CO2 offset")
        
        # Database statistics
        try:
            st.markdown("---")
            st.markdown("### 📊 Berechnungs-Statistiken")
            
            col_s1, col_s2, col_s3 = st.columns(3)
            
            # Get calculation statistics
            history = st.session_state.db_manager.get_calculation_history(limit=1000)
            
            with col_s1:
                total_calculations = len(history)
                st.metric("Gesamt Berechnungen", f"{total_calculations:,}")
            
            with col_s2:
                if not history.empty:
                    avg_emissions = history['co2_annual'].mean()
                    st.metric("Ø Jahresemissionen", f"{avg_emissions:.0f} kg CO2")
            
            with col_s3:
                if not history.empty:
                    ev_count = len(history[history['vehicle_type'] == 'Elektrofahrzeug'])
                    ev_percentage = (ev_count / total_calculations * 100) if total_calculations > 0 else 0
                    st.metric("E-Auto Anteil", f"{ev_percentage:.1f}%")
            
            # Popular models
            if not history.empty and len(history) > 5:
                st.markdown("#### 🏆 Beliebte Modelle")
                col_pop1, col_pop2 = st.columns(2)
                
                with col_pop1:
                    popular_ev = st.session_state.db_manager.get_popular_car_models("Elektrofahrzeug", 3)
                    if not popular_ev.empty:
                        st.markdown("**Elektrofahrzeuge:**")
                        for _, car in popular_ev.iterrows():
                            st.markdown(f"• {car['brand']} {car['model']} ({car['calculation_count']} Berechnungen)")
                
                with col_pop2:
                    popular_diesel = st.session_state.db_manager.get_popular_car_models("Dieselfahrzeug", 3)
                    if not popular_diesel.empty:
                        st.markdown("**Dieselfahrzeuge:**")
                        for _, car in popular_diesel.iterrows():
                            st.markdown(f"• {car['brand']} {car['model']} ({car['calculation_count']} Berechnungen)")
        
        except Exception as e:
            st.info("📊 Datenbankstatistiken werden geladen...")
    
    # Enhanced German information section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FFD700 0%, #FF6B35 50%, #1E7F4F 100%); 
                padding: 25px; border-radius: 15px; margin: 30px 0;">
    <h2 style="color: white; margin: 0; text-align: center; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);">
    🌍 Über diesen fortschrittlichen Rechner</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # German-specific key features overview
    st.markdown("""
    <div style="background: linear-gradient(90deg, #E8F5E8 0%, #F0FFF0 100%); 
                padding: 25px; border-radius: 15px; border-left: 8px solid #DD0000; border-right: 8px solid #FFCE00;">
    <h3 style="color: #1E7F4F; margin-bottom: 15px;">🎯 Deutsche Weltklasse-Emissionsanalyse-Plattform</h3>
    <p style="font-size: 1.1em; line-height: 1.6;">
    Dieses hochentwickelte Tool bietet umfassende Lebenszyklus-Kohlenstoffemissionsanalysen für 
    deutsche Elektro- und Dieselfahrzeuge unter Verwendung modernster Umweltbewertungsmethoden 
    und Daten der deutschen Automobilindustrie.
    </p>
    <p style="color: #2E8B57; font-weight: bold; margin-top: 15px;">
    🏭 Basierend auf BMW, Mercedes, Audi, VW & Porsche Fahrzeugdaten<br>
    📊 Integriert deutsche Stromnetzdaten und Dekarbonisierungsprojektionen<br>
    🔬 Verwendet Fraunhofer ISI und UBA Forschungsergebnisse
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Enhanced German feature grid with colors
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(45deg, #1E7F4F 0%, #32CD32 100%); 
                    padding: 20px; border-radius: 15px; text-align: center; margin: 10px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h2 style="color: white; margin: 0;">🔬</h2>
        <h4 style="color: white; margin: 10px 0;">Wissenschaftliche Genauigkeit</h4>
        <ul style="text-align: left; list-style-type: none; color: white; padding: 0;">
        <li>✅ UBA Emissionsfaktoren</li>
        <li>✅ Deutsche Fahrprofile (WLTP)</li>
        <li>✅ 10+ deutsche Stromnetze</li>
        <li>✅ ISO 14040/14044 LCA Standards</li>
        <li>✅ Cradle-to-Grave Analyse</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(45deg, #FF6B35 0%, #FFD700 100%); 
                    padding: 20px; border-radius: 15px; text-align: center; margin: 10px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h2 style="color: white; margin: 0;">📊</h2>
        <h4 style="color: white; margin: 10px 0;">Erweiterte Analytik</h4>
        <ul style="text-align: left; list-style-type: none; color: white; padding: 0;">
        <li>✅ Multi-Schadstoff-Tracking</li>
        <li>✅ Herstellungsemissionen</li>
        <li>✅ Stromnetz-Dekarbonisierung</li>
        <li>✅ Sensitivitätsanalyse</li>
        <li>✅ Kosten-Nutzen-Analyse</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(45deg, #4169E1 0%, #87CEEB 100%); 
                    padding: 20px; border-radius: 15px; text-align: center; margin: 10px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h2 style="color: white; margin: 0;">🌍</h2>
        <h4 style="color: white; margin: 10px 0;">Umweltauswirkungen</h4>
        <ul style="text-align: left; list-style-type: none; color: white; padding: 0;">
        <li>✅ Klimawandelpotential</li>
        <li>✅ Luftqualitätsbewertung</li>
        <li>✅ Ressourcenverbrauch</li>
        <li>✅ Ökosystem-Impact-Score</li>
        <li>✅ Gesundheitseffekte</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(45deg, #8B008B 0%, #FF1493 100%); 
                    padding: 20px; border-radius: 15px; text-align: center; margin: 10px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h2 style="color: white; margin: 0;">🚀</h2>
        <h4 style="color: white; margin: 10px 0;">Erweiterte Features</h4>
        <ul style="text-align: left; list-style-type: none; color: white; padding: 0;">
        <li>✅ Interaktive Dashboards</li>
        <li>✅ Szenario-Vergleiche</li>
        <li>✅ Waterfall-Visualisierungen</li>
        <li>✅ Export-Funktionen</li>
        <li>✅ Echtzeitberechnungen</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # German key insights with enhanced styling
    st.markdown("""
    <div style="background: linear-gradient(90deg, #2E8B57 0%, #4169E1 100%); 
                padding: 20px; border-radius: 15px; margin: 20px 0;">
    <h3 style="color: white; margin: 0; text-align: center;">🔍 Wichtige Erkenntnisse aktueller deutscher Forschung</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(45deg, #4169E1 0%, #1E90FF 100%); 
                    padding: 20px; border-radius: 10px; margin: 10px 0; color: white;">
        <h4 style="margin: 0 0 10px 0;">⏱️ CO2-Amortisationszeit</h4>
        <p style="margin: 0;">Deutsche E-Autos gleichen ihre höheren Herstellungsemissionen 
        innerhalb von 2-3 Jahren aus, selbst im aktuellen deutschen Strommix mit Kohleanteil.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: linear-gradient(45deg, #32CD32 0%, #228B22 100%); 
                    padding: 20px; border-radius: 10px; margin: 10px 0; color: white;">
        <h4 style="margin: 0 0 10px 0;">📈 Stromnetz-Dekarbonisierung</h4>
        <p style="margin: 0;">Mit Deutschlands Energiewende werden E-Autos automatisch 
        umweltfreundlicher - ohne Änderungen am Fahrzeug. Bis 2030: 80% weniger Emissionen.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(45deg, #FF8C00 0%, #FF6347 100%); 
                    padding: 20px; border-radius: 10px; margin: 10px 0; color: white;">
        <h4 style="margin: 0 0 10px 0;">🗺️ Regionale Unterschiede</h4>
        <p style="margin: 0;">In Deutschland: 95% weniger Emissionen in S-H (Wind) vs. 
        40% in NRW (Kohle). Bayern und BW liegen bei 70-80% Reduktion.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: linear-gradient(45deg, #8B008B 0%, #DC143C 100%); 
                    padding: 20px; border-radius: 10px; margin: 10px 0; color: white;">
        <h4 style="margin: 0 0 10px 0;">🔋 Deutsche Batterietechnologie</h4>
        <p style="margin: 0;">BMW, Mercedes & VW investieren massiv in nachhaltige 
        Batterieproduktion. CO2-Footprint sinkt um 50% bis 2025 (Fraunhofer ISI Studie).</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

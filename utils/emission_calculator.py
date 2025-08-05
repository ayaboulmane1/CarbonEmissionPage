import numpy as np
import pandas as pd

class EmissionCalculator:
    def __init__(self):
        # Emission factors (kg CO2 per unit)
        self.diesel_factor = 2.68  # kg CO2 per liter
        self.diesel_density = 0.832  # kg/liter
        self.gallon_to_liter = 3.78541
        
        # German electricity grid emission factors (kg CO2 per kWh)
        # Based on German Federal Environment Agency (UBA) and Agora Energiewende data
        self.grid_factors = {
            "Deutschland 2025": 0.366,  # Current German grid mix
            "Deutschland Kohleausstieg 2030": 0.280,  # Projected with coal phase-out
            "Deutschland Erneuerbar 2035": 0.150,  # With 80% renewables target
            "Bayern (Wasser/Atom)": 0.220,  # Bavaria - hydro/nuclear heavy
            "Nordrhein-Westfalen (Kohle)": 0.450,  # NRW - industrial/coal region
            "Schleswig-Holstein (Wind)": 0.180,  # Northern Germany - wind heavy
            "Baden-Württemberg": 0.250,  # Southwest mixed energy
            "Österreich": 0.140,  # Austria comparison
            "Polen": 0.690,   # Poland high-coal comparison
            "EU-Durchschnitt": 0.295  # EU average for reference
        }
        
        # Additional pollutants (relative to CO2)
        self.pollutant_ratios = {
            "NOx": {"diesel": 0.015, "electric": 0.002},
            "PM2.5": {"diesel": 0.0008, "electric": 0.0001},
            "SO2": {"diesel": 0.0003, "electric": 0.001}
        }
        
        # German automotive lifecycle emissions (kg CO2)
        # Based on studies from Fraunhofer ISI, VDE, and German automotive manufacturers
        self.lifecycle_emissions = {
            "electric": {
                "raw_material_extraction": 2300,  # Higher for German premium EVs
                "battery_production": 3800,  # Improved German battery tech
                "vehicle_assembly": 2200,  # German manufacturing efficiency
                "transportation": 350,  # Shorter European transport
                "end_of_life": -600,  # Advanced German recycling
                "total_manufacturing": 8050  # Total German EV manufacturing
            },
            "diesel": {
                "raw_material_extraction": 1400,
                "engine_production": 2800,  # German precision engineering
                "vehicle_assembly": 2300,  # German automotive quality
                "transportation": 350,  # Shorter European transport
                "end_of_life": -250,  # German recycling systems
                "total_manufacturing": 6600  # Total German diesel manufacturing
            }
        }
        
        # German car efficiency standards (based on popular German models)
        self.german_car_models = {
            "electric": {
                "BMW iX3": {"efficiency": 29.0, "range_km": 460, "price_eur": 68300},
                "Mercedes EQC": {"efficiency": 32.5, "range_km": 417, "price_eur": 71281},
                "Audi e-tron": {"efficiency": 35.7, "range_km": 436, "price_eur": 81250},
                "Volkswagen ID.4": {"efficiency": 28.0, "range_km": 520, "price_eur": 47515},
                "Porsche Taycan": {"efficiency": 38.2, "range_km": 484, "price_eur": 105607}
            },
            "diesel": {
                "BMW 320d": {"efficiency": 19.6, "emissions_g_km": 126, "price_eur": 46850},
                "Mercedes C220d": {"efficiency": 19.2, "emissions_g_km": 131, "price_eur": 48561},
                "Audi A4 TDI": {"efficiency": 18.8, "emissions_g_km": 134, "price_eur": 49400},
                "Volkswagen Passat TDI": {"efficiency": 20.1, "emissions_g_km": 124, "price_eur": 42995},
                "Porsche Macan Diesel": {"efficiency": 14.2, "emissions_g_km": 189, "price_eur": 78481}
            }
        }
        
        # Fuel cycle emissions (upstream)
        self.fuel_cycle_factors = {
            "diesel": {
                "extraction": 0.65,  # kg CO2 per liter
                "refining": 0.52,
                "transportation": 0.18,
                "total_upstream": 1.35
            },
            "electricity": {
                "transmission_losses": 0.05,  # 5% loss factor
                "grid_infrastructure": 0.02   # kg CO2 per kWh
            }
        }
    
    def calculate_diesel_emissions(self, annual_mileage, mpg, years=15):
        """Calculate comprehensive lifecycle emissions for diesel vehicle"""
        # Annual fuel consumption
        annual_gallons = annual_mileage / mpg
        annual_liters = annual_gallons * self.gallon_to_liter
        
        # Direct CO2 emissions (tailpipe)
        co2_annual_direct = annual_liters * self.diesel_factor
        
        # Upstream emissions (fuel cycle)
        co2_annual_upstream = annual_liters * self.fuel_cycle_factors["diesel"]["total_upstream"]
        
        # Total annual emissions
        co2_annual = co2_annual_direct + co2_annual_upstream
        co2_lifetime = co2_annual * years
        
        # Lifecycle breakdown
        lifecycle_breakdown = self.lifecycle_emissions["diesel"].copy()
        lifecycle_breakdown["operation_direct"] = co2_annual_direct * years
        lifecycle_breakdown["operation_upstream"] = co2_annual_upstream * years
        lifecycle_breakdown["total_operation"] = co2_lifetime
        
        # Additional pollutants
        nox_annual = co2_annual * self.pollutant_ratios["NOx"]["diesel"]
        pm25_annual = co2_annual * self.pollutant_ratios["PM2.5"]["diesel"]
        so2_annual = co2_annual * self.pollutant_ratios["SO2"]["diesel"]
        
        # Total with manufacturing
        total_lifecycle = co2_lifetime + lifecycle_breakdown["total_manufacturing"]
        
        return {
            "co2_annual": co2_annual,
            "co2_annual_direct": co2_annual_direct,
            "co2_annual_upstream": co2_annual_upstream,
            "co2_lifetime": co2_lifetime,
            "total_lifecycle": total_lifecycle,
            "nox_annual": nox_annual,
            "pm25_annual": pm25_annual,
            "so2_annual": so2_annual,
            "fuel_annual_gallons": annual_gallons,
            "fuel_annual_liters": annual_liters,
            "lifecycle_breakdown": lifecycle_breakdown,
            "manufacturing_emissions": lifecycle_breakdown["total_manufacturing"]
        }
    
    def calculate_ev_emissions(self, annual_mileage, kwh_per_100_miles, grid_mix, years=15):
        """Calculate comprehensive lifecycle emissions for electric vehicle"""
        # Annual electricity consumption
        annual_kwh = (annual_mileage / 100) * kwh_per_100_miles
        
        # Grid emission factor
        grid_factor = self.grid_factors.get(grid_mix, self.grid_factors["Deutschland 2025"])
        
        # Direct emissions (grid electricity)
        co2_annual_direct = annual_kwh * grid_factor
        
        # Upstream emissions (transmission losses, grid infrastructure)
        transmission_factor = 1 + self.fuel_cycle_factors["electricity"]["transmission_losses"]
        co2_annual_upstream = annual_kwh * self.fuel_cycle_factors["electricity"]["grid_infrastructure"]
        
        # Total annual emissions (accounting for transmission losses)
        co2_annual = (co2_annual_direct * transmission_factor) + co2_annual_upstream
        co2_lifetime = co2_annual * years
        
        # Lifecycle breakdown
        lifecycle_breakdown = self.lifecycle_emissions["electric"].copy()
        lifecycle_breakdown["operation_direct"] = co2_annual_direct * transmission_factor * years
        lifecycle_breakdown["operation_upstream"] = co2_annual_upstream * years
        lifecycle_breakdown["total_operation"] = co2_lifetime
        
        # Additional pollutants (from electricity generation)
        nox_annual = co2_annual * self.pollutant_ratios["NOx"]["electric"]
        pm25_annual = co2_annual * self.pollutant_ratios["PM2.5"]["electric"]
        so2_annual = co2_annual * self.pollutant_ratios["SO2"]["electric"]
        
        # Total with manufacturing
        total_lifecycle = co2_lifetime + lifecycle_breakdown["total_manufacturing"]
        
        return {
            "co2_annual": co2_annual,
            "co2_annual_direct": co2_annual_direct * transmission_factor,
            "co2_annual_upstream": co2_annual_upstream,
            "co2_lifetime": co2_lifetime,
            "total_lifecycle": total_lifecycle,
            "nox_annual": nox_annual,
            "pm25_annual": pm25_annual,
            "so2_annual": so2_annual,
            "electricity_annual_kwh": annual_kwh,
            "grid_factor": grid_factor,
            "transmission_factor": transmission_factor,
            "lifecycle_breakdown": lifecycle_breakdown,
            "manufacturing_emissions": lifecycle_breakdown["total_manufacturing"]
        }
    
    def calculate_cost_comparison(self, diesel_data, ev_data, electricity_price=0.13, gas_price=3.50):
        """Calculate cost comparison between vehicles"""
        # Annual fuel/electricity costs
        diesel_annual_cost = diesel_data["fuel_annual_gallons"] * gas_price
        ev_annual_cost = ev_data["electricity_annual_kwh"] * electricity_price
        
        # Maintenance costs (approximate annual)
        diesel_maintenance = 1200  # Higher maintenance for ICE
        ev_maintenance = 400       # Lower maintenance for EV
        
        return {
            "diesel_fuel_cost": diesel_annual_cost,
            "ev_electricity_cost": ev_annual_cost,
            "diesel_maintenance": diesel_maintenance,
            "ev_maintenance": ev_maintenance,
            "diesel_total_annual": diesel_annual_cost + diesel_maintenance,
            "ev_total_annual": ev_annual_cost + ev_maintenance,
            "annual_savings": (diesel_annual_cost + diesel_maintenance) - (ev_annual_cost + ev_maintenance)
        }
    
    def get_environmental_impact_score(self, emissions_data):
        """Calculate environmental impact score (0-100, lower is better)"""
        # Normalize based on typical vehicle emissions
        max_co2 = 8000  # kg CO2 per year for high-emission vehicle
        co2_score = min(100, (emissions_data["co2_annual"] / max_co2) * 100)
        
        # Factor in other pollutants
        nox_weight = 0.2
        pm25_weight = 0.3
        so2_weight = 0.1
        
        # Normalize other pollutants (simplified)
        nox_score = min(100, (emissions_data["nox_annual"] / 120) * 100)
        pm25_score = min(100, (emissions_data["pm25_annual"] / 6) * 100)
        so2_score = min(100, (emissions_data["so2_annual"] / 2.4) * 100)
        
        # Weighted average
        impact_score = (
            co2_score * 0.4 +
            nox_score * nox_weight +
            pm25_score * pm25_weight +
            so2_score * so2_weight
        )
        
        return round(impact_score, 1)
    
    def calculate_lifecycle_analysis(self, annual_mileage, ev_efficiency, diesel_efficiency, grid_mix, years=15):
        """Calculate comprehensive lifecycle analysis comparing EV and diesel"""
        ev_results = self.calculate_ev_emissions(annual_mileage, ev_efficiency, grid_mix, years)
        diesel_results = self.calculate_diesel_emissions(annual_mileage, diesel_efficiency, years)
        
        # Calculate payback period (when EV becomes carbon neutral vs diesel)
        annual_savings = diesel_results['co2_annual'] - ev_results['co2_annual']
        manufacturing_difference = ev_results['manufacturing_emissions'] - diesel_results['manufacturing_emissions']
        
        if annual_savings > 0:
            carbon_payback_years = manufacturing_difference / annual_savings
        else:
            carbon_payback_years = float('inf')
        
        # Lifecycle comparison data
        lifecycle_comparison = {
            "phases": [
                "Raw Material Extraction",
                "Manufacturing",
                "Operation (15 years)",
                "End of Life",
                "Total Lifecycle"
            ],
            "ev_emissions": [
                ev_results['lifecycle_breakdown']['raw_material_extraction'],
                ev_results['lifecycle_breakdown']['battery_production'] + 
                ev_results['lifecycle_breakdown']['vehicle_assembly'] + 
                ev_results['lifecycle_breakdown']['transportation'],
                ev_results['co2_lifetime'],
                ev_results['lifecycle_breakdown']['end_of_life'],
                ev_results['total_lifecycle']
            ],
            "diesel_emissions": [
                diesel_results['lifecycle_breakdown']['raw_material_extraction'],
                diesel_results['lifecycle_breakdown']['engine_production'] + 
                diesel_results['lifecycle_breakdown']['vehicle_assembly'] + 
                diesel_results['lifecycle_breakdown']['transportation'],
                diesel_results['co2_lifetime'],
                diesel_results['lifecycle_breakdown']['end_of_life'],
                diesel_results['total_lifecycle']
            ]
        }
        
        return {
            "ev_results": ev_results,
            "diesel_results": diesel_results,
            "carbon_payback_years": carbon_payback_years,
            "annual_savings": annual_savings,
            "lifecycle_comparison": lifecycle_comparison,
            "total_savings_15_years": annual_savings * years,
            "manufacturing_difference": manufacturing_difference
        }
    
    def get_grid_decarbonization_projection(self, annual_mileage, ev_efficiency, years=15):
        """Project EV emissions with grid decarbonization over time"""
        # Assume 3% annual grid decarbonization
        decarbonization_rate = 0.03
        
        projections = {}
        for grid_type in ["US Average", "Coal Heavy", "Natural Gas", "Renewable Heavy"]:
            base_factor = self.grid_factors[grid_type]
            yearly_emissions = []
            
            for year in range(1, years + 1):
                # Grid gets cleaner each year
                adjusted_factor = base_factor * (1 - decarbonization_rate) ** year
                annual_kwh = (annual_mileage / 100) * ev_efficiency
                annual_co2 = annual_kwh * adjusted_factor
                yearly_emissions.append(annual_co2)
            
            projections[grid_type] = yearly_emissions
        
        return projections

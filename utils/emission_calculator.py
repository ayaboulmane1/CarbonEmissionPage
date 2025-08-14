import numpy as np
import pandas as pd

class EmissionCalculator:
    def __init__(self):
        # --------- Constants ---------
        self.diesel_factor = 2.68         # kg CO2 per liter
        self.diesel_density = 0.832       # kg/liter
        self.gallon_to_liter = 3.78541

        # --------- Germany-only grid factors (kg CO2 per kWh) ---------
        self.grid_factors = {
            "Deutschland 2025": 0.366,
            "Deutschland Kohleausstieg 2030": 0.280,
            "Deutschland Erneuerbar 2035": 0.150,
            "Bayern (Wasser/Atom)": 0.220,
            "Nordrhein-Westfalen (Kohle)": 0.450,
            "Schleswig-Holstein (Wind)": 0.180,
            "Baden-Württemberg": 0.250,
            "Österreich": 0.140,
            "Polen": 0.690,
            "EU-Durchschnitt": 0.295,
        }
        # case/whitespace-insensitive map for robust lookup
        self._grid_factors_lc = {k.strip().lower(): v for k, v in self.grid_factors.items()}

        # --------- Pollutants ---------
        self.pollutant_ratios = {
            "NOx": {"diesel": 0.015, "electric": 0.002},
            "PM2.5": {"diesel": 0.0008, "electric": 0.0001},
            "SO2": {"diesel": 0.0003, "electric": 0.001},
        }

        # --------- Lifecycle building blocks (Germany context) ---------
        self.lifecycle_emissions = {
            "electric": {
                "raw_material_extraction": 2300,
                "battery_production": 3800,
                "vehicle_assembly": 2200,
                "transportation": 350,
                "end_of_life": -600,
                "total_manufacturing": 8050,
            },
            "diesel": {
                "raw_material_extraction": 1400,
                "engine_production": 2800,
                "vehicle_assembly": 2300,
                "transportation": 350,
                "end_of_life": -250,
                "total_manufacturing": 6600,
            },
        }

        self.fuel_cycle_factors = {
            "diesel": {
                "extraction": 0.65,
                "refining": 0.52,
                "transportation": 0.18,
                "total_upstream": 1.35,
            },
            "electricity": {
                "transmission_losses": 0.05,   # 5% losses
                "grid_infrastructure": 0.02,   # kg CO2 per kWh
            },
        }

    # <<< FIXED: make this a real method (not nested in __init__) >>>
    def _grid_factor(self, grid_name: str):
        if isinstance(grid_name, (int, float)):
            return float(grid_name)
            
        key = (grid_name or "").strip().lower()
        return self._grid_factors_lc.get(key)

    # ---------------- Diesel ----------------
    def calculate_diesel_emissions(self, annual_mileage, mpg, years=15):
        annual_gallons = annual_mileage / mpg
        annual_liters = annual_gallons * self.gallon_to_liter

        co2_annual_direct = annual_liters * self.diesel_factor
        co2_annual_upstream = annual_liters * self.fuel_cycle_factors["diesel"]["total_upstream"]

        co2_annual = co2_annual_direct + co2_annual_upstream
        co2_lifetime = co2_annual * years

        lifecycle_breakdown = self.lifecycle_emissions["diesel"].copy()
        lifecycle_breakdown["operation_direct"] = co2_annual_direct * years
        lifecycle_breakdown["operation_upstream"] = co2_annual_upstream * years
        lifecycle_breakdown["total_operation"] = co2_lifetime

        total_lifecycle = co2_lifetime + lifecycle_breakdown["total_manufacturing"]

        return {
            "co2_annual": co2_annual,
            "co2_annual_direct": co2_annual_direct,
            "co2_annual_upstream": co2_annual_upstream,
            "co2_lifetime": co2_lifetime,
            "total_lifecycle": total_lifecycle,
            "nox_annual": co2_annual * self.pollutant_ratios["NOx"]["diesel"],
            "pm25_annual": co2_annual * self.pollutant_ratios["PM2.5"]["diesel"],
            "so2_annual": co2_annual * self.pollutant_ratios["SO2"]["diesel"],
            "fuel_annual_gallons": annual_gallons,
            "fuel_annual_liters": annual_liters,
            "lifecycle_breakdown": lifecycle_breakdown,
            "manufacturing_emissions": lifecycle_breakdown["total_manufacturing"],
        }

    # ---------------- EV ----------------
    def calculate_ev_emissions(self, annual_mileage, kwh_per_100_miles, grid_mix, years=15):
        annual_kwh = (annual_mileage / 100.0) * kwh_per_100_miles

        # robust lookup; default to Deutschland 2025 if not found
        grid_factor = self._grid_factor(grid_mix)
        if grid_factor is None:
            grid_factor = self.grid_factors["Deutschland 2025"]

        co2_annual_direct = annual_kwh * grid_factor
        transmission_factor = 1 + self.fuel_cycle_factors["electricity"]["transmission_losses"]
        co2_annual_upstream = annual_kwh * self.fuel_cycle_factors["electricity"]["grid_infrastructure"]

        co2_annual = (co2_annual_direct * transmission_factor) + co2_annual_upstream
        co2_lifetime = co2_annual * years

        lifecycle_breakdown = self.lifecycle_emissions["electric"].copy()
        lifecycle_breakdown["operation_direct"] = co2_annual_direct * transmission_factor * years
        lifecycle_breakdown["operation_upstream"] = co2_annual_upstream * years
        lifecycle_breakdown["total_operation"] = co2_lifetime

        total_lifecycle = co2_lifetime + lifecycle_breakdown["total_manufacturing"]

        return {
            "co2_annual": co2_annual,
            "co2_annual_direct": co2_annual_direct * transmission_factor,
            "co2_annual_upstream": co2_annual_upstream,
            "co2_lifetime": co2_lifetime,
            "total_lifecycle": total_lifecycle,
            "nox_annual": co2_annual * self.pollutant_ratios["NOx"]["electric"],
            "pm25_annual": co2_annual * self.pollutant_ratios["PM2.5"]["electric"],
            "so2_annual": co2_annual * self.pollutant_ratios["SO2"]["electric"],
            "electricity_annual_kwh": annual_kwh,
            "grid_factor": grid_factor,
            "transmission_factor": transmission_factor,
            "lifecycle_breakdown": lifecycle_breakdown,
            "manufacturing_emissions": lifecycle_breakdown["total_manufacturing"],
        }

    # ---------------- Comparison & LCA ----------------
    def calculate_cost_comparison(self, diesel_data, ev_data, electricity_price=0.13, gas_price=3.50):
        diesel_annual_cost = diesel_data["fuel_annual_gallons"] * gas_price
        ev_annual_cost = ev_data["electricity_annual_kwh"] * electricity_price
        diesel_maintenance, ev_maintenance = 1200, 400
        return {
            "diesel_fuel_cost": diesel_annual_cost,
            "ev_electricity_cost": ev_annual_cost,
            "diesel_maintenance": diesel_maintenance,
            "ev_maintenance": ev_maintenance,
            "diesel_total_annual": diesel_annual_cost + diesel_maintenance,
            "ev_total_annual": ev_annual_cost + ev_maintenance,
            "annual_savings": (diesel_annual_cost + diesel_maintenance) - (ev_annual_cost + ev_maintenance),
        }

    def get_environmental_impact_score(self, emissions_data):
        max_co2 = 8000
        co2_score = min(100, (emissions_data["co2_annual"] / max_co2) * 100)
        nox_score = min(100, (emissions_data["nox_annual"] / 120) * 100)
        pm25_score = min(100, (emissions_data["pm25_annual"] / 6) * 100)
        so2_score = min(100, (emissions_data["so2_annual"] / 2.4) * 100)
        return round(co2_score * 0.4 + nox_score * 0.2 + pm25_score * 0.3 + so2_score * 0.1, 1)

    def calculate_lifecycle_analysis(self, annual_mileage, ev_efficiency, diesel_efficiency, grid_mix_factor, years=15):
        ev_results = self.calculate_ev_emissions(annual_mileage, ev_efficiency, grid_mix_factor, years)
        diesel_results = self.calculate_diesel_emissions(annual_mileage, diesel_efficiency, years)

        annual_savings = diesel_results["co2_annual"] - ev_results["co2_annual"]
        manufacturing_difference = ev_results["manufacturing_emissions"] - diesel_results["manufacturing_emissions"]
        carbon_payback_years = manufacturing_difference / annual_savings if annual_savings > 0 else float("inf")

        lifecycle_comparison = {
            "phases": [
                "Raw Material Extraction",
                "Manufacturing",
                "Operation (15 years)",
                "End of Life",
                "Total Lifecycle",
            ],
            "ev_emissions": [
                ev_results["lifecycle_breakdown"]["raw_material_extraction"],
                ev_results["lifecycle_breakdown"]["battery_production"]
                + ev_results["lifecycle_breakdown"]["vehicle_assembly"]
                + ev_results["lifecycle_breakdown"]["transportation"],
                ev_results["co2_lifetime"],
                ev_results["lifecycle_breakdown"]["end_of_life"],
                ev_results["total_lifecycle"],
            ],
            "diesel_emissions": [
                diesel_results["lifecycle_breakdown"]["raw_material_extraction"],
                diesel_results["lifecycle_breakdown"]["engine_production"]
                + diesel_results["lifecycle_breakdown"]["vehicle_assembly"]
                + diesel_results["lifecycle_breakdown"]["transportation"],
                diesel_results["co2_lifetime"],
                diesel_results["lifecycle_breakdown"]["end_of_life"],
                diesel_results["total_lifecycle"],
            ],
        }

        return {
            "ev_results": ev_results,
            "diesel_results": diesel_results,
            "carbon_payback_years": carbon_payback_years,
            "annual_savings": annual_savings,
            "lifecycle_comparison": lifecycle_comparison,
            "total_savings_15_years": annual_savings * years,
            "manufacturing_difference": manufacturing_difference,
        }

    # --------- Germany‑only decarbonization projection ---------
    def get_grid_decarbonization_projection(self, annual_mileage, ev_efficiency, years=15):
        """
        Return {grid_type: [annual_emissions_year1, ..., yearN]} for EV,
        assuming linear improvement to 40% of current factor by year N.
        """
        projections = {}
        kwh_per_mile = ev_efficiency / 100.0

        for grid_type, base_factor in self.grid_factors.items():
            yearly = []
            for year in range(1, max(1, years) + 1):
                decarb = 1.0 - 0.6 * (year - 1) / max(1, years - 1)   # 60% lower by final year
                factor = max(0.0, base_factor * decarb)
                annual_kwh = annual_mileage * kwh_per_mile
                annual_co2 = annual_kwh * factor
                yearly.append(annual_co2)
            projections[grid_type] = yearly

        return projections

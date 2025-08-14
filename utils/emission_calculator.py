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
#<<< Diesel with fuel type and more parameters (for the first page) >>>
    def calculate_diesel_emissions_full(
        self,
        annual_mileage,                  # miles/year
        mpg,                              # miles per gallon
        years=15,
        fuel_type="Regular Diesel",       # "Regular Diesel" | "Bio-Diesel (B20)" | "Renewable Diesel"
        engine_size_l=2.0,
        emission_standard="Euro 6",       # "Euro 6" | "Euro 5" | "EPA Tier 3"
        turbo=True
    ):
        
    
        # ---- Assumptions / Modifiers ----
        # Fuel pathway impact on WTW CO2 per litre (tune as needed, or replace with literature values)
        fuel_type_mult = {
            "Regular Diesel": 1.00,
            "Bio-Diesel (B20)": 0.90,     # ~10% lower WTW as a conservative default
            "Renewable Diesel": 0.40      # strong reduction
        }.get(fuel_type, 1.00)

        # Real-world consumption modifier (small effect sizes; documented assumptions)
        consumption_mod = 1.0
        if engine_size_l and engine_size_l > 2.5:
            consumption_mod *= 1.05      # larger engines tend to use a bit more fuel
        if turbo:
            consumption_mod *= 0.97      # mild efficiency gain on downsized turbo engines
        if emission_standard == "Euro 5":
            consumption_mod *= 1.02      # legacy calibration / on-road gap
        # Euro 6 (baseline) and EPA Tier 3 left as 1.00
    
        # ---- Activity data (fuel use) ----
        annual_gallons = (annual_mileage / mpg) * consumption_mod
        annual_liters = annual_gallons * self.gallon_to_liter
    
        # ---- Emission factors (kg CO2 / litre) ----
        tailpipe_per_l = self.diesel_factor  # e.g., 2.68 kg CO2/L
        upstream_per_l = self.fuel_cycle_factors["diesel"]["total_upstream"]  # e.g., ~1.35 kg CO2/L
    
        # Apply fuel pathway multiplier to BOTH components so the breakdown remains consistent
        tailpipe_per_l *= fuel_type_mult
        upstream_per_l *= fuel_type_mult
    
        # ---- Annual emissions ----
        co2_annual_direct = annual_liters * tailpipe_per_l
        co2_annual_upstream = annual_liters * upstream_per_l
        co2_annual = co2_annual_direct + co2_annual_upstream
    
        # ---- Lifetime totals ----
        co2_lifetime = co2_annual * years
    
        # ---- Lifecycle breakdown (preserves your structure) ----
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
    
            # helpful echoes for UI/debug
            "assumptions": {
                "fuel_type": fuel_type,
                "fuel_type_multiplier": fuel_type_mult,
                "engine_size_l": engine_size_l,
                "turbo": turbo,
                "emission_standard": emission_standard,
                "consumption_modifier": consumption_mod,
                "tailpipe_per_litre": tailpipe_per_l,
                "upstream_per_litre": upstream_per_l
            }
    }

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
    def calculate_ev_emissions_full(
        self,
        annual_mileage,                  # miles/year
        kwh_per_100_miles,               # kWh per 100 miles
        grid_mix,                        # label or factor; robust lookup below
        years=15,
        battery_kwh=75.0,
        driving_pattern="Mixed (City/Highway)",  # "Mixed (City/Highway)" | "Mostly City" | "Mostly Highway"
        charging_type="Home (Level 2)",          # "Home (Level 2)" | "Public Fast Charging" | "Workplace Charging"
        cold_weather=False
    ):
        
        driving_pattern_factor = {
            "Mostly City": 1.05,
            "Mixed (City/Highway)": 1.00,
            "Mostly Highway": 0.95
        }.get(driving_pattern, 1.00)
    
        cold_weather_factor = 1.15 if cold_weather else 1.00
    
        # Charging losses modelled as extra energy drawn from grid
        charging_loss_frac = {
            "Home (Level 2)": 0.08,
            "Workplace Charging": 0.08,
            "Public Fast Charging": 0.10
        }.get(charging_type, 0.08)
    
        # Effective consumption per 100 miles
        eff_kwh_per_100_miles = kwh_per_100_miles * driving_pattern_factor * cold_weather_factor
    
        # Base annual kWh at the plug (before adding charging losses)
        annual_kwh_base = (annual_mileage / 100.0) * eff_kwh_per_100_miles
    
        # Add charging losses as additional kWh required from the grid
        annual_kwh = annual_kwh_base * (1.0 + charging_loss_frac)
    
        # -----------------------------
        # 2) Grid factor + upstream adders
        # -----------------------------
        # Robust grid factor resolution
        if isinstance(grid_mix, (int, float)):
            grid_factor = float(grid_mix)
        else:
            grid_factor = self._grid_factor(grid_mix)
            if grid_factor is None:
                grid_factor = self.grid_factors.get("Deutschland 2025", 0.366)  # safe fallback
    
        # Your existing upstream structure:
        # - T&D handled as a multiplicative factor on direct
        transmission_factor = 1.0 + self.fuel_cycle_factors["electricity"]["transmission_losses"]  # e.g., 0.05 → 1.05
        # - Infrastructure as an additive kg/kWh applied to kWh
        infra_ef = self.fuel_cycle_factors["electricity"]["grid_infrastructure"]  # kg CO2/kWh
    
        # -----------------------------
        # 3) Annual operational emissions
        # -----------------------------
        co2_annual_direct = annual_kwh * grid_factor
        co2_annual_upstream = annual_kwh * infra_ef
        co2_annual = (co2_annual_direct * transmission_factor) + co2_annual_upstream
        co2_lifetime = co2_annual * years
    
        # -----------------------------
        # 4) Manufacturing emissions (battery-scaled)
        # -----------------------------
        # Try to compute body+pack manufacturing from available attributes; otherwise fall back gracefully.
        # Preferred: explicit base-without-battery + EF per kWh
        battery_ef = getattr(self, "battery_emission_factor_kg_per_kwh", 82.5)  # kg CO2/kWh
        base_ev_body_only = getattr(self, "base_vehicle_manufacturing_ev_body_only", None)
    
        # Fallbacks if your class only has a single total manufacturing value:
        default_batt_kwh = getattr(self, "default_battery_kwh", None)
        manu_default_total = self.lifecycle_emissions["electric"].get("total_manufacturing", 8500.0)
    
        if base_ev_body_only is not None:
            manu = base_ev_body_only + battery_kwh * battery_ef
        elif default_batt_kwh is not None:
            # Replace assumed default battery with actual battery_kwh
            manu = manu_default_total - (default_batt_kwh * battery_ef) + (battery_kwh * battery_ef)
        else:
            # Last resort: keep existing total (can’t separate battery share without a default)
            manu = manu_default_total
    
        # Keep your lifecycle breakdown semantics
        lifecycle_breakdown = self.lifecycle_emissions["electric"].copy()
        lifecycle_breakdown["operation_direct"] = co2_annual_direct * transmission_factor * years
        lifecycle_breakdown["operation_upstream"] = co2_annual_upstream * years
        lifecycle_breakdown["total_operation"] = co2_lifetime
        lifecycle_breakdown["total_manufacturing"] = manu
    
        total_lifecycle = co2_lifetime + manu
    
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
            "manufacturing_emissions": manu,
    
            # Helpful echoes for UI / debugging / thesis transparency
            "assumptions": {
                "driving_pattern": driving_pattern,
                "driving_pattern_factor": driving_pattern_factor,
                "cold_weather": cold_weather,
                "cold_weather_factor": cold_weather_factor,
                "charging_type": charging_type,
                "charging_loss_fraction": charging_loss_frac,
                "battery_kwh": battery_kwh,
                "battery_ef_kg_per_kwh": battery_ef
            }
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

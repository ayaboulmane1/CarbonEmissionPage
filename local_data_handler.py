import json
import os
from datetime import datetime

class LocalDataManager:
    def __init__(self, base_dir='data'):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

        self.cars_file = os.path.join(self.base_dir, 'german_car_models.json')
        self.grid_file = os.path.join(self.base_dir, 'german_grid_data.json')
        self.history_file = os.path.join(self.base_dir, 'calculation_history.json')

        self._init_files()

    def _init_files(self):
        for file in [self.cars_file, self.grid_file, self.history_file]:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    json.dump([], f)

    def get_german_cars(self, vehicle_type=None):
        with open(self.cars_file, 'r') as f:
            cars = json.load(f)
        if vehicle_type:
            return [car for car in cars if car['vehicle_type'] == vehicle_type]
        return cars

    def get_grid_data(self):
        with open(self.grid_file, 'r') as f:
            return json.load(f)

    def get_calculation_history(self, session_id=None, limit=100):
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        if session_id:
            history = [h for h in history if h['user_session'] == session_id]
        return sorted(history, key=lambda x: x['created_at'], reverse=True)[:limit]

    def save_calculation(self, session_id, vehicle_type, brand, model, annual_km, efficiency, grid_region, calculation_results):
        entry = {
            "user_session": session_id,
            "vehicle_type": vehicle_type,
            "brand": brand,
            "model": model,
            "annual_km": annual_km,
            "efficiency": efficiency,
            "grid_region": grid_region,
            "co2_annual": calculation_results['co2_annual'],
            "co2_lifetime": calculation_results['co2_lifetime'],
            "manufacturing_emissions": calculation_results.get('manufacturing_emissions', 0),
            "total_lifecycle": calculation_results['total_lifecycle'],
            "calculation_data": calculation_results,
            "created_at": datetime.utcnow().isoformat()
        }

        with open(self.history_file, 'r+') as f:
            history = json.load(f)
            history.append(entry)
            f.seek(0)
            json.dump(history, f, indent=2)

    def initialize_sample_data(self):
        if os.path.exists(self.cars_file) and os.path.exists(self.grid_file):
            return

        electric_cars = [
            {"brand": "BMW", "model": "iX3", "vehicle_type": "electric", "efficiency": 29.0, "range_km": 460, "price_eur": 68300},
            {"brand": "Mercedes", "model": "EQC", "vehicle_type": "electric", "efficiency": 32.5, "range_km": 417, "price_eur": 71281},
            {"brand": "Volkswagen", "model": "ID.4", "vehicle_type": "electric", "efficiency": 28.0, "range_km": 520, "price_eur": 47515},
        ]
        diesel_cars = [
            {"brand": "BMW", "model": "320d", "vehicle_type": "diesel", "efficiency": 5.1, "emissions_g_km": 126, "price_eur": 46850},
            {"brand": "Mercedes", "model": "C220d", "vehicle_type": "diesel", "efficiency": 5.2, "emissions_g_km": 131, "price_eur": 48561},
            {"brand": "Volkswagen", "model": "Passat TDI", "vehicle_type": "diesel", "efficiency": 4.7, "emissions_g_km": 124, "price_eur": 42995},
        ]
        grid_data = [
            {"region": "Deutschland 2025", "emission_factor": 0.366, "renewable_percentage": 46.0, "coal_percentage": 24.0, "gas_percentage": 18.0, "nuclear_percentage": 12.0, "year": 2025},
            {"region": "Bayern (Wasser/Atom)", "emission_factor": 0.220, "renewable_percentage": 55.0, "coal_percentage": 8.0, "gas_percentage": 12.0, "nuclear_percentage": 25.0, "year": 2025},
        ]

        with open(self.cars_file, 'w') as f:
            json.dump(electric_cars + diesel_cars, f, indent=2)

        with open(self.grid_file, 'w') as f:
            json.dump(grid_data, f, indent=2)

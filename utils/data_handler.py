import pandas as pd
import json
from datetime import datetime

class DataHandler:
    def __init__(self):
        self.calculations_history = []
    
    def save_calculation(self, calculation_data, vehicle_type, parameters):
        """Save calculation to history"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "vehicle_type": vehicle_type,
            "parameters": parameters,
            "results": calculation_data
        }
        self.calculations_history.append(record)
        return record
    
    def get_calculations_df(self):
        """Convert calculations history to DataFrame"""
        if not self.calculations_history:
            return pd.DataFrame()
        
        data = []
        for calc in self.calculations_history:
            row = {
                "Timestamp": calc["timestamp"],
                "Vehicle Type": calc["vehicle_type"],
                "Annual Mileage": calc["parameters"].get("annual_mileage", "N/A"),
                "Efficiency": calc["parameters"].get("efficiency", "N/A"),
                "CO2 Annual (kg)": calc["results"]["co2_annual"],
                "CO2 Lifetime (kg)": calc["results"]["co2_lifetime"],
                "Total Lifetime (kg)": calc["results"]["total_lifetime"]
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def export_to_csv(self):
        """Export calculations to CSV format"""
        df = self.get_calculations_df()
        if not df.empty:
            return df.to_csv(index=False)
        return None
    
    def export_to_json(self):
        """Export calculations to JSON format"""
        return json.dumps(self.calculations_history, indent=2, default=str)
    
    def clear_history(self):
        """Clear all calculation history"""
        self.calculations_history = []
    
    def get_summary_statistics(self):
        """Get summary statistics from all calculations"""
        if not self.calculations_history:
            return None
        
        df = self.get_calculations_df()
        
        ev_data = df[df["Vehicle Type"] == "Electric Vehicle"]
        diesel_data = df[df["Vehicle Type"] == "Diesel Vehicle"]
        
        summary = {
            "total_calculations": len(df),
            "ev_calculations": len(ev_data),
            "diesel_calculations": len(diesel_data)
        }
        
        if not ev_data.empty:
            summary["ev_avg_annual_co2"] = ev_data["CO2 Annual (kg)"].mean()
            summary["ev_avg_lifetime_co2"] = ev_data["CO2 Lifetime (kg)"].mean()
        
        if not diesel_data.empty:
            summary["diesel_avg_annual_co2"] = diesel_data["CO2 Annual (kg)"].mean()
            summary["diesel_avg_lifetime_co2"] = diesel_data["CO2 Lifetime (kg)"].mean()
        
        if not ev_data.empty and not diesel_data.empty:
            summary["avg_annual_reduction"] = (
                diesel_data["CO2 Annual (kg)"].mean() - ev_data["CO2 Annual (kg)"].mean()
            )
            summary["avg_lifetime_reduction"] = (
                diesel_data["CO2 Lifetime (kg)"].mean() - ev_data["CO2 Lifetime (kg)"].mean()
            )
        
        return summary
    
    def get_vehicle_comparison_data(self):
        """Prepare data for vehicle comparison charts"""
        if not self.calculations_history:
            return None
        
        ev_results = []
        diesel_results = []
        
        for calc in self.calculations_history:
            if calc["vehicle_type"] == "Electric Vehicle":
                ev_results.append(calc["results"])
            else:
                diesel_results.append(calc["results"])
        
        return {
            "ev_results": ev_results,
            "diesel_results": diesel_results
        }

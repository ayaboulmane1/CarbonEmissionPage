import os
import psycopg2
from sqlalchemy import create_engine, text
import pandas as pd
from datetime import datetime
import json

class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.engine = create_engine(self.database_url)
        self.create_tables()
    
    def create_tables(self):
        """Create database tables for German car emission data"""
        create_tables_sql = """
        -- German car models table
        CREATE TABLE IF NOT EXISTS german_car_models (
            id SERIAL PRIMARY KEY,
            brand VARCHAR(50) NOT NULL,
            model VARCHAR(100) NOT NULL,
            vehicle_type VARCHAR(20) NOT NULL, -- 'electric' or 'diesel'
            efficiency FLOAT NOT NULL, -- kWh/100km for electric, L/100km for diesel
            range_km INTEGER, -- for electric vehicles
            emissions_g_km INTEGER, -- for diesel vehicles
            price_eur INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- German electricity grid data table
        CREATE TABLE IF NOT EXISTS german_grid_data (
            id SERIAL PRIMARY KEY,
            region VARCHAR(100) NOT NULL,
            emission_factor FLOAT NOT NULL, -- kg CO2 per kWh
            renewable_percentage FLOAT,
            coal_percentage FLOAT,
            gas_percentage FLOAT,
            nuclear_percentage FLOAT,
            year INTEGER DEFAULT 2025,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Calculation history table
        CREATE TABLE IF NOT EXISTS calculation_history (
            id SERIAL PRIMARY KEY,
            user_session VARCHAR(100),
            vehicle_type VARCHAR(20) NOT NULL,
            brand VARCHAR(50),
            model VARCHAR(100),
            annual_km INTEGER NOT NULL,
            efficiency FLOAT NOT NULL,
            grid_region VARCHAR(100),
            co2_annual FLOAT NOT NULL,
            co2_lifetime FLOAT NOT NULL,
            manufacturing_emissions FLOAT NOT NULL,
            total_lifecycle FLOAT NOT NULL,
            calculation_data JSONB, -- Store full calculation details
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- German environmental studies table
        CREATE TABLE IF NOT EXISTS german_studies (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            institution VARCHAR(100) NOT NULL, -- Fraunhofer ISI, UBA, etc.
            year INTEGER NOT NULL,
            summary TEXT,
            key_findings JSONB,
            url VARCHAR(300),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        with self.engine.connect() as conn:
            conn.execute(text(create_tables_sql))
            conn.commit()
    
    def populate_german_car_data(self):
        """Populate database with German car model data"""
        # German Electric Vehicles
        electric_cars = [
            ('BMW', 'iX3', 'electric', 29.0, 460, None, 68300),
            ('Mercedes', 'EQC', 'electric', 32.5, 417, None, 71281),
            ('Audi', 'e-tron', 'electric', 35.7, 436, None, 81250),
            ('Volkswagen', 'ID.4', 'electric', 28.0, 520, None, 47515),
            ('Porsche', 'Taycan', 'electric', 38.2, 484, None, 105607),
            ('BMW', 'i4', 'electric', 31.2, 590, None, 58300),
            ('Mercedes', 'EQS', 'electric', 29.8, 770, None, 106374),
            ('Audi', 'Q4 e-tron', 'electric', 33.1, 520, None, 52900)
        ]
        
        # German Diesel Vehicles
        diesel_cars = [
            ('BMW', '320d', 'diesel', 5.1, None, 126, 46850),
            ('Mercedes', 'C220d', 'diesel', 5.2, None, 131, 48561),
            ('Audi', 'A4 TDI', 'diesel', 5.3, None, 134, 49400),
            ('Volkswagen', 'Passat TDI', 'diesel', 4.7, None, 124, 42995),
            ('Porsche', 'Macan Diesel', 'diesel', 7.0, None, 189, 78481),
            ('BMW', 'X3 xDrive20d', 'diesel', 6.5, None, 155, 51050),
            ('Mercedes', 'GLC 220d', 'diesel', 6.2, None, 148, 53476),
            ('Audi', 'Q5 TDI', 'diesel', 6.8, None, 162, 56200)
        ]
        
        # Insert electric cars
        for car in electric_cars:
            insert_sql = """
            INSERT INTO german_car_models (brand, model, vehicle_type, efficiency, range_km, price_eur)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """
            with self.engine.connect() as conn:
                conn.execute(text(insert_sql), car)
                conn.commit()
        
        # Insert diesel cars
        for car in diesel_cars:
            insert_sql = """
            INSERT INTO german_car_models (brand, model, vehicle_type, efficiency, emissions_g_km, price_eur)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """
            with self.engine.connect() as conn:
                conn.execute(text(insert_sql), car)
                conn.commit()
    
    def populate_german_grid_data(self):
        """Populate database with German electricity grid data"""
        grid_data = [
            ('Deutschland 2025', 0.366, 46.0, 24.0, 18.0, 12.0, 2025),
            ('Deutschland Kohleausstieg 2030', 0.280, 65.0, 5.0, 15.0, 15.0, 2030),
            ('Deutschland Erneuerbar 2035', 0.150, 80.0, 0.0, 10.0, 10.0, 2035),
            ('Bayern (Wasser/Atom)', 0.220, 55.0, 8.0, 12.0, 25.0, 2025),
            ('Nordrhein-Westfalen (Kohle)', 0.450, 25.0, 45.0, 20.0, 10.0, 2025),
            ('Schleswig-Holstein (Wind)', 0.180, 75.0, 2.0, 13.0, 10.0, 2025),
            ('Baden-Württemberg', 0.250, 50.0, 15.0, 20.0, 15.0, 2025),
            ('EU-Durchschnitt', 0.295, 42.0, 18.0, 22.0, 18.0, 2025)
        ]
        
        for region_data in grid_data:
            insert_sql = """
            INSERT INTO german_grid_data (region, emission_factor, renewable_percentage, 
                                        coal_percentage, gas_percentage, nuclear_percentage, year)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """
            with self.engine.connect() as conn:
                conn.execute(text(insert_sql), region_data)
                conn.commit()
    
    def save_calculation(self, session_id, vehicle_type, brand, model, annual_km, 
                        efficiency, grid_region, calculation_results):
        """Save calculation to database"""
        insert_sql = """
        INSERT INTO calculation_history 
        (user_session, vehicle_type, brand, model, annual_km, efficiency, grid_region,
         co2_annual, co2_lifetime, manufacturing_emissions, total_lifecycle, calculation_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            session_id,
            vehicle_type,
            brand,
            model,
            annual_km,
            efficiency,
            grid_region,
            calculation_results['co2_annual'],
            calculation_results['co2_lifetime'],
            calculation_results.get('manufacturing_emissions', 0),
            calculation_results['total_lifecycle'],
            json.dumps(calculation_results)
        )
        
        with self.engine.connect() as conn:
            conn.execute(text(insert_sql), params)
            conn.commit()
    
    def get_german_cars(self, vehicle_type=None):
        """Get German car models from database"""
        if vehicle_type:
            sql = "SELECT * FROM german_car_models WHERE vehicle_type = %s ORDER BY brand, model"
            params = (vehicle_type,)
        else:
            sql = "SELECT * FROM german_car_models ORDER BY brand, model"
            params = ()
        
        return pd.read_sql(sql, self.engine, params=params)
    
    def get_grid_data(self):
        """Get German grid emission data"""
        sql = "SELECT * FROM german_grid_data ORDER BY region"
        return pd.read_sql(sql, self.engine)
    
    def get_calculation_history(self, session_id=None, limit=100):
        """Get calculation history"""
        if session_id:
            sql = """
            SELECT * FROM calculation_history 
            WHERE user_session = %s 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            params = (session_id, limit)
        else:
            sql = """
            SELECT * FROM calculation_history 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            params = (limit,)
        
        return pd.read_sql(sql, self.engine, params=params)
    
    def get_popular_car_models(self, vehicle_type, limit=5):
        """Get most popular car models from calculation history"""
        sql = """
        SELECT brand, model, COUNT(*) as calculation_count,
               AVG(co2_annual) as avg_annual_emissions,
               AVG(total_lifecycle) as avg_lifecycle_emissions
        FROM calculation_history 
        WHERE vehicle_type = %s
        GROUP BY brand, model
        ORDER BY calculation_count DESC
        LIMIT %s
        """
        
        return pd.read_sql(sql, self.engine, params=(vehicle_type, limit))
    
    def initialize_database(self):
        """Initialize database with German car and grid data"""
        try:
            self.populate_german_car_data()
            self.populate_german_grid_data()
            return True
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False
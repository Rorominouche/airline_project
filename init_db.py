import sqlite3

db_path = "aviation.db"

def init_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. FLEET Table (Avions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS FLEET (
            tail_number TEXT PRIMARY KEY,
            aircraft_model TEXT,
            economy_capacity INTEGER,
            business_capacity INTEGER
        )
    ''')
    
    # 2. ROUTES Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ROUTES (
            route_id TEXT PRIMARY KEY,
            departure_airport TEXT,
            arrival_airport TEXT,
            flight_duration_minutes INTEGER
        )
    ''')
    
    # 3. FLIGHTS Table (Schedule & Inventory)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS FLIGHTS (
            flight_id TEXT PRIMARY KEY,
            flight_number TEXT,
            route_id TEXT,
            tail_number TEXT,
            departure_datetime TEXT,
            base_price_economy REAL,
            seats_economy_available INTEGER,
            seats_business_available INTEGER,
            FOREIGN KEY(route_id) REFERENCES ROUTES(route_id),
            FOREIGN KEY(tail_number) REFERENCES FLEET(tail_number)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database successfully initialized with aviation standards!")

if __name__ == "__main__":
    init_database()
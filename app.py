import streamlit as st
import libsql_client
from datetime import datetime

# =====================================================================
# CONFIGURATION DE LA CONNEXION TURSO
# =====================================================================
# Remplis ici avec les informations fournies sur le site de Turso
TURSO_URL = "https://1adatabase-romain1a.aws-eu-west-1.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODE1MTcxMTYsImlkIjoiMDE5ZWNhYWUtMzMwMS03NjgzLTkyMzItMmFiNmIzYWYzNWJkIiwicmlkIjoiOTI2ZDdmYTUtNDhlOC00ZGMzLThhOTItOGI4MDdhOWFlNDdkIn0.iKl8zWoZMbFbctvatsMsXumi4tVwN0LPdnCn-InvE3z8-8Ctgs_S23HwlYaeETKiU3JfOwDk2XGSH5iobOmdCA"

# Fonction magique qui exécute les requêtes sur Turso (Cloud)
def execute_query(query, params=(), commit=False, fetch=False):
    # On ouvre la connexion avec le cloud
    client = libsql_client.create_client_sync(url=TURSO_URL, auth_token=TURSO_TOKEN)
    
    # Exécution de la requête
    result = client.execute(query, params)
    
    data = []
    if fetch:
        # Turso renvoie les données sous forme de lignes d'objets, 
        # on les convertit en listes/tuples classiques pour que Streamlit reste content
        data = [list(row) for row in result.rows]
        
    client.close()
    return data

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Amadeus Airline Manager", page_icon="✈️", layout="wide")
st.title("✈️ Amadeus Airline Operations Center (Cloud)")

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["📦 Resource Management", "📅 Flight Scheduling"])

# =====================================================================
# MODULE 1 : RESOURCE MANAGEMENT (Fleet & Network)
# =====================================================================
if menu == "📦 Resource Management":
    st.header("Fleet & Network Management")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("➕ Add Aircraft to Fleet")
        tail_num = st.text_input("Tail Number (e.g., F-JZNE)").upper()
        model = st.selectbox("Aircraft Model", ["Airbus A320", "Airbus A350", "Boeing 737", "Boeing 777"])
        capa_eco = st.number_input("Economy Seats", min_value=0, max_value=400, value=150)
        capa_bus = st.number_input("Business Seats", min_value=0, max_value=100, value=20)
        
        if st.button("Register Aircraft"):
            if tail_num:
                try:
                    execute_query("INSERT INTO FLEET VALUES (?, ?, ?, ?)", (tail_num, model, capa_eco, capa_bus), commit=True)
                    st.success(f"Aircraft {tail_num} successfully registered!")
                except Exception as e:
                    st.error(f"Error or duplicate entry: {e}")
            else:
                st.warning("Please enter a valid Tail Number.")

    with col2:
        st.subheader("➕ Create Route")
        dep = st.text_input("Departure Airport (IATA Code - e.g., NCE)").upper()
        arr = st.text_input("Arrival Airport (IATA Code - e.g., CDG)").upper()
        duration = st.number_input("Flight Duration (minutes)", min_value=10, max_value=1000, value=90)
        
        if st.button("Create Route"):
            if dep and arr:
                route_id = f"{dep}-{arr}"
                try:
                    execute_query("INSERT INTO ROUTES VALUES (?, ?, ?, ?)", (route_id, dep, arr, duration), commit=True)
                    st.success(f"Route {route_id} successfully created!")
                except Exception as e:
                    st.error(f"Error or duplicate entry: {e}")
            else:
                st.warning("Please fill in both airport codes.")

    # Display Data from Cloud
    st.write("---")
    st.subheader("📊 Active Fleet (Live Cloud)")
    try:
        fleet_data = execute_query("SELECT * FROM FLEET", fetch=True)
        st.dataframe(fleet_data, column_config={"0": "Tail Number", "1": "Aircraft Model", "2": "Eco Capacity", "3": "Business Capacity"})
    except Exception as e:
        #st.info("No aircraft registered yet or tables not initialized.")
        st.error(f"Erreur technique Fleet : {e}")

# =====================================================================
# MODULE 2 : FLIGHT SCHEDULING (Inventory & Planning)
# =====================================================================
elif menu == "📅 Flight Scheduling":
    st.header("Flight Scheduling & Inventory")
    
    # Dynamic fetching from Cloud for dropdowns
    try:
        fleet_list = [r[0] for r in execute_query("SELECT tail_number FROM FLEET", fetch=True)]
        routes_list = [r[0] for r in execute_query("SELECT route_id FROM ROUTES", fetch=True)]
    except Exception:
        fleet_list, routes_list = [], []
    
    if not fleet_list or not routes_list:
        st.warning("⚠️ Action Required: You must register at least one aircraft and one route in 'Resource Management' before scheduling a flight.")
    else:
        st.subheader("🗓️ Schedule a New Flight")
        c1, c2, c3 = st.columns(3)
        with c1:
            flight_num = st.text_input("Flight Number (e.g., AM102)").upper()
            selected_route = st.selectbox("Select Route", routes_list)
        with c2:
            selected_aircraft = st.selectbox("Assign Aircraft (Tail Num)", fleet_list)
            price_eco = st.number_input("Base Ticket Price Economy (€)", min_value=10.0, max_value=2000.0, value=99.0)
        with c3:
            date_flight = st.date_input("Departure Date")
            time_flight = st.time_input("Departure Time")
        
        if st.button("Schedule Flight"):
            if flight_num:
                # Fetch capacities from cloud to initialize available seats
                aircraft_info = execute_query("SELECT economy_capacity, business_capacity FROM FLEET WHERE tail_number = ?", (selected_aircraft,), fetch=True)[0]
                capa_eco, capa_bus = aircraft_info[0], aircraft_info[1]
                
                datetime_str = f"{date_flight} {time_flight}"
                flight_id = f"{flight_num}-{date_flight.strftime('%Y%m%d')}"
                
                try:
                    execute_query(
                        "INSERT INTO FLIGHTS VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (flight_id, flight_num, selected_route, selected_aircraft, datetime_str, price_eco, capa_eco, capa_bus),
                        commit=True
                    )
                    st.success(f"Flight {flight_num} successfully scheduled!")
                except Exception as e:
                    st.error(f"Error or duplicate flight: {e}")
            else:
                st.warning("Please enter a Flight Number.")
                
    # Display Schedule Table
    st.write("---")
    st.subheader("📋 Flight Schedule & Live Availability (Live Cloud)")
    try:
        flights_data = execute_query("SELECT flight_id, flight_number, route_id, tail_number, departure_datetime, base_price_economy, seats_economy_available FROM FLIGHTS", fetch=True)
        st.dataframe(flights_data)
    except Exception:
        st.info("No flights scheduled yet.")
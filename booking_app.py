import streamlit as st
import libsql_client
import random
import string
from datetime import datetime

# =====================================================================
# CONFIGURATION TURSO CLOUD
# =====================================================================
TURSO_URL = "https://1adatabase-romain1a.aws-eu-west-1.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODE1MTcxMTYsImlkIjoiMDE5ZWNhYWUtMzMwMS03NjgzLTkyMzItMmFiNmIzYWYzNWJkIiwicmlkIjoiOTI2ZDdmYTUtNDhlOC00ZGMzLThhOTItOGI4MDdhOWFlNDdkIn0.iKl8zWoZMbFbctvatsMsXumi4tVwN0LPdnCn-InvE3z8-8Ctgs_S23HwlYaeETKiU3JfOwDk2XGSH5iobOmdCA"

def execute_query(query, params=(), fetch=False):
    client = libsql_client.create_client_sync(url=TURSO_URL, auth_token=TURSO_TOKEN)
    result = client.execute(query, params)
    data = []
    if fetch:
        data = [list(row) for row in result.rows]
    client.close()
    return data

# Fonction utilitaire pour générer un code PNR à 6 caractères
def generate_pnr():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Amadeus Passenger Portal", page_icon="✈️", layout="wide")
st.title("✈️ Amadeus Passenger Booking & Check-in System")

# --- NAVIGATION ---
# AJOUT DE L'OPTION FLIGHT OCCUPANCY
menu = st.sidebar.radio("Navigation", [
    "🔍 Search & Book Flights", 
    "🎟️ Retrieve Boarding Pass", 
    "📋 View All Bookings",
    "📈 Flight Occupancy"
])

# =====================================================================
# MODULE 1 : SEARCH & BOOK FLIGHTS
# =====================================================================
if menu == "🔍 Search & Book Flights":
    st.header("Search and Book Your Next Flight")
    
    if "search_results" not in st.session_state:
        st.session_state.search_results = None

    try:
        routes = execute_query("SELECT departure_airport, arrival_airport FROM ROUTES", fetch=True)
        departures = sorted(list(set([r[0] for r in routes])))
        arrivals = sorted(list(set([r[1] for r in routes])))
    except Exception:
        departures, arrivals = [], []
        
    if not departures or not arrivals:
        st.warning("⚠️ No routes available in the system yet. Please ask the Operations Team to add routes first.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            from_airport = st.selectbox("From", departures)
        with c2:
            to_airport = st.selectbox("To", arrivals)
        with c3:
            travel_date = st.date_input("Travel Date")
            
        if st.button("Search Flights"):
            route_id = f"{from_airport}-{to_airport}"
            query = """
                SELECT flight_id, flight_number, departure_datetime, base_price_economy, seats_economy_available, seats_business_available 
                FROM FLIGHTS 
                WHERE route_id = ? AND departure_datetime LIKE ?
            """
            search_param = f"{travel_date}%"
            
            try:
                st.session_state.search_results = execute_query(query, (route_id, search_param), fetch=True)
                if not st.session_state.search_results:
                    st.info(f"No flights found for route {route_id} on {travel_date}.")
            except Exception as e:
                st.error(f"Erreur lors de la recherche : {e}")

        if st.session_state.search_results:
            st.write("---")
            st.subheader("Available Results")
            
            for fl in st.session_state.search_results:
                fl_id, fl_num, fl_time, price, seats_eco, seats_bus = fl
                
                with st.container():
                    st.markdown(f"### ✈️ Flight **{fl_num}** — {fl_time}")
                    col_info, col_book = st.columns([2, 1])
                    
                    with col_info:
                        st.write(f"💰 **Base Price:** {price} €")
                        st.write(f"💺 **Available Seats:** Economy: {seats_eco} | Business: {seats_bus}")
                    
                    with col_book:
                        passenger_name = st.text_input("Passenger Full Name", key=f"name_{fl_id}")
                        seat_class = st.selectbox("Class", ["Economy", "Business"], key=f"class_{fl_id}")
                        
                        if st.button(f"Confirm Booking for {fl_num}", key=f"btn_{fl_id}"):
                            if not passenger_name:
                                st.warning("Please enter the passenger's name.")
                            else:
                                if (seat_class == "Economy" and seats_eco <= 0) or (seat_class == "Business" and seats_bus <= 0):
                                    st.error("Sorry, this flight is fully booked in this class.")
                                else:
                                    pnr = generate_pnr()
                                    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    
                                    try:
                                        execute_query(
                                            "INSERT INTO BOOKINGS VALUES (?, ?, ?, ?, ?)",
                                            (pnr, passenger_name, fl_id, seat_class, current_date)
                                        )
                                        
                                        if seat_class == "Economy":
                                            execute_query("UPDATE FLIGHTS SET seats_economy_available = seats_economy_available - 1 WHERE flight_id = ?", (fl_id,))
                                        else:
                                            execute_query("UPDATE FLIGHTS SET seats_business_available = seats_business_available - 1 WHERE flight_id = ?", (fl_id,))
                                            
                                        st.success(f"🎉 Booking Confirmed! PNR: **{pnr}**")
                                        st.balloons()
                                        st.session_state.search_results = None
                                        
                                    except Exception as e:
                                        st.error(f"An error occurred during booking: {e}")

# =====================================================================
# MODULE 2 : RETRIEVE BOARDING PASS (PNR Check-in)
# =====================================================================
elif menu == "🎟️ Retrieve Boarding Pass":
    st.header("Digital Check-in & Boarding Pass")
    pnr_input = st.text_input("Enter your 6-character Booking Reference (PNR)").upper().strip()
    
    if st.button("Generate Boarding Pass"):
        if len(pnr_input) != 6:
            st.warning("A valid PNR must be exactly 6 characters long.")
        else:
            query = """
                SELECT b.passenger_name, b.seat_class, f.flight_number, f.departure_datetime, f.route_id, f.tail_number
                FROM BOOKINGS b
                JOIN FLIGHTS f ON b.flight_id = f.flight_id
                WHERE b.booking_reference = ?
            """
            booking_info = execute_query(query, (pnr_input,), fetch=True)
            
            if not booking_info:
                st.error("No booking found for this reference. Please check your PNR.")
            else:
                name, s_class, fl_num, fl_time, route, aircraft = booking_info[0]
                dep_apt, arr_apt = route.split("-")
                
                st.write("---")
                st.success("🎫 Boarding Pass Successfully Generated!")
                with st.expander("👉 CLICK TO OPEN YOUR DIGITAL BOARDING PASS", expanded=True):
                    st.markdown(f"""
                    ### ✈️ **BOARDING PASS — {s_class.upper()} CLASS**
                    **PASSENGER:** {name}  
                    **BOOKING REF (PNR):** `{pnr_input}`
                    ---
                    * **Flight:** {fl_num}  
                    * **Route:** {dep_apt} ➔ {arr_apt}  
                    * **Departure Time:** {fl_time}  
                    * **Aircraft Assigned:** {aircraft}
                    """)

# =====================================================================
# MODULE 3 : VIEW ALL BOOKINGS
# =====================================================================
elif menu == "📋 View All Bookings":
    st.header("📋 Master Booking List (Live Cloud Data)")
    query = """
        SELECT b.booking_reference, b.passenger_name, f.flight_number, f.route_id, b.seat_class, b.booking_date
        FROM BOOKINGS b
        JOIN FLIGHTS f ON b.flight_id = f.flight_id
        ORDER BY b.booking_date DESC
    """
    try:
        all_bookings = execute_query(query, fetch=True)
        if not all_bookings:
            st.info("No bookings have been made in the system yet.")
        else:
            st.dataframe(all_bookings, column_config={"0": "PNR", "1": "Passenger", "2": "Flight", "3": "Route", "4": "Class", "5": "Date"}, use_container_width=True)
            st.metric(label="Total Passengers Booked", value=len(all_bookings))
    except Exception as e:
        st.error(f"Error: {e}")

# =====================================================================
# NOUVEAU MODULE 4 : FLIGHT OCCUPANCY (Yield & Analytics)
# =====================================================================
elif menu == "📈 Flight Occupancy":
    st.header("📈 Flight Occupancy & Inventory Analytics")
    st.write("Live tracking of aircraft filling rates and business vs economy distribution.")
    
    # Requête pour croiser le plan de vol actuel avec les capacités maximales définies dans FLEET
    query = """
        SELECT f.flight_number, f.route_id, f.departure_datetime, 
               f.seats_economy_available, ac.economy_capacity,
               f.seats_business_available, ac.business_capacity
        FROM FLIGHTS f
        JOIN FLEET ac ON f.tail_number = ac.tail_number
        ORDER BY f.departure_datetime ASC
    """
    
    try:
        flights_stock = execute_query(query, fetch=True)
        
        if not flights_stock:
            st.info("No scheduled flights to analyze. Add flights in the Operations panel first.")
        else:
            for flight in flights_stock:
                fl_num, route, dt, eco_avail, eco_max, bus_avail, bus_max = flight
                
                # Calcul du nombre de sièges vendus (Maximum - Disponible)
                eco_sold = eco_max - eco_avail
                bus_sold = bus_max - bus_avail
                
                total_max = eco_max + bus_max
                total_sold = eco_sold + bus_sold
                
                # Calcul des pourcentages de remplissage
                pct_occupancy = int((total_sold / total_max) * 100) if total_max > 0 else 0
                
                # Interface visuelle par vol
                with st.expander(f"✈️ Flight {fl_num} ({route}) — {dt} — 📊 {pct_occupancy}% Full", expanded=True):
                    c1, c2, c3 = st.columns([1, 2, 2])
                    
                    with c1:
                        # Un indicateur global pour le vol
                        st.metric(label="Total Booked", value=f"{total_sold} / {total_max}", delta=f"{pct_occupancy}%")
                    
                    with c2:
                        st.write(f"**Economy Class:** {eco_sold} seats sold out of {eco_max}")
                        # Barre de progression Éco (Streamlit prend une valeur entre 0.0 et 1.0)
                        eco_pct = eco_sold / eco_max if eco_max > 0 else 0.0
                        st.progress(eco_pct)
                        st.caption(f"{eco_avail} seats left in Economy")
                        
                    with c3:
                        st.write(f"**Business Class:** {bus_sold} seats sold out of {bus_max}")
                        # Barre de progression Business
                        bus_pct = bus_sold / bus_max if bus_max > 0 else 0.0
                        st.progress(bus_pct)
                        st.caption(f"{bus_avail} seats left in Business")
                        
    except Exception as e:
        st.error(f"Error computing analytics: {e}")
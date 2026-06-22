import streamlit as st
import libsql_client
import webbrowser
import os
from datetime import datetime

# =====================================================================
# TURSO CONNECTION
# =====================================================================
TURSO_URL = "https://airline-faustine-ambrine.aws-eu-west-1.turso.io"

def execute_query(query, params=(), commit=False, fetch=False):
    client = libsql_client.create_client_sync(url=TURSO_URL, auth_token=TURSO_TOKEN)
    result = client.execute(query, params)
    data = []

    if fetch:

        data = [list(row) for row in result.rows]
    client.close()

    return data

# =====================================================================
# PAGE CONFIG
# =====================================================================
st.set_page_config(page_title="Amadeus Airline Manager", page_icon="✈️", layout="wide")
st.title("✈️ Amadeus Airline Operations Center (Cloud)")

# =====================================================================
# NAVIGATION — Réservation par défaut
# =====================================================================
menu = st.sidebar.radio(
    "Navigation",
    ["📦 Resource Management", "📅 Flight Scheduling", "🎫 Réservation"],
    index=2
)

# =====================================================================
# MODULE 1 : RESOURCE MANAGEMENT
# =====================================================================
if menu == "📦 Resource Management":
    st.header("Fleet & Network Management")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("➕ Add Aircraft to Fleet")
        tail_num = st.text_input("Tail Number (e.g., F-JZNE)").upper().strip()
        model = st.selectbox("Aircraft Model", ["Airbus A320", "Airbus A350", "Boeing 737", "Boeing 777"])
        capa_eco = st.number_input("Economy Seats", min_value=0, max_value=400, value=150)
        capa_bus = st.number_input("Business Seats", min_value=0, max_value=100, value=20)

        if st.button("Register Aircraft"):
            if tail_num:

                try:
                    execute_query("INSERT INTO Fleet VALUES (?, ?, ?, ?)", (tail_num, model, int(capa_eco), int(capa_bus)), commit=True)
                    st.success(f"Aircraft {tail_num} successfully registered!")
                    st.rerun()

                except Exception as e:

                    st.error(e)

    with col2:
        st.subheader("➕ Create Route")
        dep = st.text_input("Departure Airport (IATA Code - e.g., NCE)").upper().strip()
        arr = st.text_input("Arrival Airport (IATA Code - e.g., CDG)").upper().strip()
        duration_text = st.text_input("Flight Duration (e.g., 90 or 1h35)", value="90")

        if st.button("Create Route"):
            if dep and arr:

                route_id = f"{dep}-{arr}"

                try:
                    execute_query("INSERT INTO Route VALUES (?, ?, ?, ?)", (route_id, dep, arr, str(duration_text)), commit=True)
                    st.success(f"Route {route_id} successfully created!")
                    st.rerun()

                except Exception as e:

    st.write("---")
    st.subheader("📊 Active Fleet (Live Cloud)")
    try:
        fleet_data = execute_query("SELECT * FROM Fleet", fetch=True)
        st.dataframe(fleet_data, column_config={"0": "Tail Number", "1": "Aircraft Model", "2": "Eco Capacity", "3": "Business Capacity"}, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur technique Fleet : {e}")

# =====================================================================
# MODULE 2 : FLIGHT SCHEDULING
# =====================================================================
elif menu == "📅 Flight Scheduling":
    st.header("Flight Scheduling & Inventory")

    try:
        fleet_list = [r[0] for r in execute_query("SELECT tail_number FROM Fleet", fetch=True)]
        routes_list = [r[0] for r in execute_query("SELECT route_id FROM Route", fetch=True)]
    except Exception:
        fleet_list, routes_list = [], []

    if not fleet_list or not routes_list:

        st.warning(

        "⚠️ Add aircraft and routes first."

        )

    else:

        st.subheader(

        "🗓️ Schedule a New Flight"

        )

        # ⚠️ ON NE CHANGE PAS CES COLONNES

        c1,c2,c3 = st.columns(3)

        with c1:

            flight_num = st.text_input(

            "Flight Number"

            ).upper().strip()

            selected_route = st.selectbox(

            "Select Route",

            routes_list

            )

        with c2:

            selected_aircraft = st.selectbox(

            "Assign Aircraft",

            fleet_list

            )

            price_eco = st.number_input(

            "Price Economy",

            min_value=10.0,

            max_value=2000.0,

            value=99.0

            )

        with c3:
            date_flight = st.date_input("Departure Date")
            time_flight = st.time_input("Departure Time")
            price_bus = st.number_input("Base Price Business (€)", min_value=20.0, max_value=5000.0, value=299.0)

        if st.button("Schedule Flight"):
            if flight_num:
                try:
                    aircraft_info = execute_query("SELECT economy_capacity, business_capacity FROM Fleet WHERE tail_number = ?", (selected_aircraft,), fetch=True)[0]
                    capa_eco, capa_bus = aircraft_info[0], aircraft_info[1]
                    datetime_str = f"{date_flight} {time_flight}"
                    execute_query(
                        "INSERT INTO Flight VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (flight_num, selected_route, selected_aircraft, datetime_str, float(price_eco), float(price_bus), int(capa_eco), int(capa_bus)),
                        commit=True
                    )
                    st.success(f"Flight {flight_num} successfully scheduled!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error or duplicate flight: {e}")
            else:
                st.warning("Please enter a Flight Number.")

    st.write("---")
    st.subheader("📋 Flight Schedule & Live Availability (Live Cloud)")
    try:
        flights_data = execute_query("SELECT flight_number, route_id, tail_number, departure_datetime, price_economy, price_business, seats_economy, seats_business FROM Flight", fetch=True)
        st.dataframe(flights_data, use_container_width=True)
    except Exception as e:
        st.info("No flights scheduled yet or schema mismatch.")

# =====================================================================
# MODULE 3 : RÉSERVATION
# =====================================================================
elif menu == "🎫 Réservation":
    st.header("🎫 Réservation")

    try:
        execute_query("""
            CREATE TABLE IF NOT EXISTS Passenger (
                passenger_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
                phone TEXT
            )
        """, commit=True)
        execute_query("""
            CREATE TABLE IF NOT EXISTS Booking (
                booking_id TEXT PRIMARY KEY,
                passenger_id TEXT NOT NULL,
                flight_number TEXT NOT NULL,
                seat_number TEXT NOT NULL,
                travel_class TEXT NOT NULL,
                booking_date TEXT NOT NULL
            )
        """, commit=True)
    except Exception as e:
        st.warning(f"Table init warning: {e}")

    # ── CATÉGORIE 1 : PASSENGER ──────────────────────────────────────
    st.subheader("👤 Passenger")

    with st.expander("➕ Ajouter un passager", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            p_id = st.text_input("Passenger ID (ex: PAX001)").upper().strip()
            p_first = st.text_input("First Name").strip()
            p_last = st.text_input("Last Name").strip()
        with col2:
            p_email = st.text_input("Email").strip()
            p_phone = st.text_input("Phone").strip()

        if st.button("Register Passenger"):
            if p_id and p_first and p_last:
                try:
                    execute_query(
                        "INSERT INTO Passenger VALUES (?, ?, ?, ?, ?)",
                        (p_id, p_first, p_last, p_email, p_phone),
                        commit=True
                    )
                    st.success(f"Passager {p_first} {p_last} ({p_id}) enregistré !")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur ou doublon : {e}")
            else:
                st.warning("Veuillez remplir le Passenger ID, First Name et Last Name.")

    with st.expander("📊 Liste des passagers", expanded=True):
        try:
            passengers = execute_query("SELECT * FROM Passenger", fetch=True)
            if passengers:
                st.dataframe(
                    passengers,
                    column_config={
                        "0": "Passenger ID", "1": "First Name",
                        "2": "Last Name", "3": "Email", "4": "Phone"
                    },
                    use_container_width=True
                )
            else:
                st.info("Aucun passager enregistré.")
        except Exception as e:
            st.error(f"Erreur chargement passagers : {e}")

    st.write("---")

    # ── CATÉGORIE 2 : BOOKING ────────────────────────────────────────
    st.subheader("📋 Booking")

    try:
        passengers_list = execute_query("SELECT passenger_id, first_name, last_name FROM Passenger", fetch=True)
        flights_list = [r[0] for r in execute_query("SELECT flight_number FROM Flight", fetch=True)]
    except Exception:
        passengers_list, flights_list = [], []

    with st.expander("➕ Créer une réservation", expanded=True):
        if not passengers_list or not flights_list:
            st.warning("⚠️ Il faut au moins un passager et un vol pour créer une réservation.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                b_id = st.text_input("Booking ID (ex: BK001)").upper().strip()
                passenger_options = {f"{r[1]} {r[2]} ({r[0]})": r[0] for r in passengers_list}
                selected_pax_label = st.selectbox("Passager", list(passenger_options.keys()))
                selected_pax_id = passenger_options[selected_pax_label]
                selected_flight = st.selectbox("Vol", flights_list)

            with col2:
                travel_class = st.selectbox("Travel Class", ["Economy", "Business"])

                booked_seats = []
                try:
                    booked_seats = [r[0] for r in execute_query(
                        "SELECT seat_number FROM Booking WHERE flight_number = ?",
                        (selected_flight,), fetch=True
                    )]
                except Exception:
                    pass

                if travel_class == "Business":
                    all_seats = [f"{r}{c}" for r in range(1, 4) for c in ["A", "C", "D", "F"]]
                else:
                    all_seats = [
                        f"{r}{c}"
                        for r in range(4, 31)
                        if r != 13
                        for c in ["A", "B", "C", "D", "E", "F"]
                    ]

                available_seats = [s for s in all_seats if s not in booked_seats]
                seat_number = st.selectbox("Siège", available_seats if available_seats else ["Aucun siège disponible"])
                booking_date = st.date_input("Date de réservation", value=datetime.today())

            if st.button("Confirmer la réservation"):
                if b_id and seat_number and seat_number != "Aucun siège disponible":
                    try:
                        execute_query(
                            "INSERT INTO Booking VALUES (?, ?, ?, ?, ?, ?)",
                            (b_id, selected_pax_id, selected_flight, seat_number, travel_class, str(booking_date)),
                            commit=True
                        )
                        st.success(f"✅ Réservation {b_id} confirmée — Siège {seat_number} ({travel_class}) sur le vol {selected_flight} !")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur ou doublon : {e}")
                else:
                    st.warning("Veuillez remplir tous les champs et vérifier la disponibilité du siège.")

    with st.expander("📋 Toutes les réservations", expanded=True):
        try:
            bookings = execute_query(
                """
                SELECT b.booking_id, p.first_name || ' ' || p.last_name AS passenger,
                       b.flight_number, b.seat_number, b.travel_class, b.booking_date
                FROM Booking b
                LEFT JOIN Passenger p ON b.passenger_id = p.passenger_id
                ORDER BY b.booking_date DESC
                """,
                fetch=True
            )
            if bookings:
                st.dataframe(
                    bookings,
                    column_config={
                        "0": "Booking ID", "1": "Passager", "2": "Vol",
                        "3": "Siège", "4": "Classe", "5": "Date"
                    },
                    use_container_width=True
                )
            else:
                st.info("Aucune réservation pour le moment.")
        except Exception as e:
            st.error(f"Erreur chargement réservations : {e}")

    # ── SEAT MAP ─────────────────────────────────────────────────────
    st.write("---")
    st.subheader("🗺️ Plan de cabine A320")

    seatmap_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "a320_seatmap.html")

    try:
        flights_list_map = [r[0] for r in execute_query("SELECT flight_number FROM Flight", fetch=True)]
    except Exception:
        flights_list_map = []

    if flights_list_map:
        selected_map_flight = st.selectbox("Vol à visualiser", flights_list_map, key="map_flight_select")
        reserved_seats_raw = []
        try:
            reserved_seats_raw = [r[0] for r in execute_query(
                "SELECT seat_number FROM Booking WHERE flight_number = ?",
                (selected_map_flight,), fetch=True
            )]
        except Exception:
            pass

        if reserved_seats_raw:
            st.info(f"Sièges réservés sur le vol {selected_map_flight} : **{', '.join(reserved_seats_raw)}**")
        else:
            st.info(f"Aucun siège réservé sur le vol {selected_map_flight}.")

        if os.path.exists(seatmap_path):
            if st.button("🗺️ Ouvrir le plan de cabine A320"):
                with open(seatmap_path, "r", encoding="utf-8") as f:
                    seatmap_html = f.read()

                reserved_seats_json = str(reserved_seats_raw).replace("'", '"')
                injection = f"""
<script>
  (function() {{
    var reserved = {reserved_seats_json};
    function markReserved() {{
      document.querySelectorAll('.seat').forEach(function(seat) {{
        var row = seat.closest('.row');
        if (!row) return;
        var rowNum = row.querySelector('.row-number');
        if (!rowNum) return;
        var letter = seat.textContent.trim();
        var seatId = rowNum.textContent.trim() + letter;
        if (reserved.indexOf(seatId) !== -1) {{
          seat.dataset.occupied = 'true';
          seat.classList.add('occupied');
          seat.setAttribute('aria-label', (seat.getAttribute('aria-label') || '').replace('disponible', 'réservé'));
        }}
      }});
      var allSeats = document.querySelectorAll('.seat');
      var res = 0;
      allSeats.forEach(function(s) {{ if (s.dataset.occupied === 'true') res++; }});
      var countRes = document.getElementById('count-reserved');
      var countAvail = document.getElementById('count-available');
      if (countRes) countRes.textContent = res;
      if (countAvail) countAvail.textContent = allSeats.length - res;
    }}
    if (document.readyState === 'loading') {{
      document.addEventListener('DOMContentLoaded', markReserved);
    }} else {{
      setTimeout(markReserved, 50);
    }}
  }})();
</script>
"""
                seatmap_html = seatmap_html.replace("</body>", injection + "</body>")
                seatmap_html = seatmap_html.replace(
                    "Vol démo · A320 · Configuration 174 sièges",
                    f"Vol {selected_map_flight} · A320 · {len(reserved_seats_raw)} siège(s) réservé(s)"
                )

                tmp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_seatmap_tmp.html")
                with open(tmp_path, "w", encoding="utf-8") as f:
                    f.write(seatmap_html)

                webbrowser.open(f"file://{tmp_path}")
        else:
            st.warning("a320_seatmap.html introuvable. Placez-le dans le même dossier que app.py.")

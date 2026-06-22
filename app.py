import streamlit as st
import libsql_client

# =====================================================
# CONFIGURATION TURSO
# =====================================================

TURSO_URL = "https://airline-faustine-ambrine.aws-eu-west-1.turso.io"

TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODE3NzYxMjMsImlkIjoiMDE5ZWNmYmEtZWUwMS03YWNiLTk2YjQtOGIyYzcxZWI2YmM1IiwicmlkIjoiYmFiZDVlMWItOWNlOS00MDQ1LThjMWQtODQ3NjY3MThjOGY1In0.FPk6p_n0XVTNHA-mrUFKT3q6JdvvX9mONBGdb1svbC0K7FS4gJyKH5QijhD8FdQHqElaXy4OmMf5WRyucJqmDA"

# =====================================================
# CONNEXION TURSO
# =====================================================

def execute_query(query, params=(), fetch=False):

    client = libsql_client.create_client_sync(
        url=TURSO_URL,
        auth_token=TURSO_TOKEN
    )

    result = client.execute(query, params)

    data = []

    if fetch:

        data = [list(row) for row in result.rows]

    client.close()

    return data


# =====================================================
# PAGE
# =====================================================

st.set_page_config(
    page_title="Amadeus Airline Manager",
    page_icon="✈️",
    layout="wide"
)

# =====================================================
# CSS
# =====================================================

st.markdown("""

<style>

.main{

background:linear-gradient(
180deg,
#eef5ff,
#ffffff
);

}

h1{

color:#003366;

}

h2{

color:#004488;

}

div.stButton > button{

background:#0066cc;

color:white;

height:50px;

border-radius:12px;

border:none;

font-size:18px;

font-weight:bold;

}

div.stButton > button:hover{

background:#004a99;

}

[data-testid="stSidebar"]{

background:#10243d;

}

[data-testid="stSidebar"] *{

color:white;

}

</style>

""", unsafe_allow_html=True)

# =====================================================
# BANNIERE
# =====================================================

st.image(

"https://images.unsplash.com/photo-1436491865332-7a61a109cc05",

use_container_width=True

)

st.title(

"✈️ Amadeus Airline Operations Center"

)

st.caption(

"Cloud Management System"

)

# =====================================================
# MENU
# =====================================================

menu = st.sidebar.radio(

"Navigation",

[

"📦 Resource Management",

"📅 Flight Scheduling"

]

)

# =====================================================
# RESOURCE MANAGEMENT
# =====================================================

if menu == "📦 Resource Management":

    st.header(

    "📦 Fleet & Network Management"

    )

    try:

        nb_fleet = len(

            execute_query(

                "SELECT * FROM Fleet",

                fetch=True

            )

        )

    except:

        nb_fleet = 0

    try:

        nb_routes = len(

            execute_query(

                "SELECT * FROM Route",

                fetch=True

            )

        )

    except:

        nb_routes = 0

    a,b = st.columns(2)

    a.metric(

        "✈️ Aircraft",

        nb_fleet

    )

    b.metric(

        "🗺️ Routes",

        nb_routes

    )

    col1,col2 = st.columns(2)

    with col1:

        st.subheader(

        "🛫 Add Aircraft to Fleet"

        )

        tail_num = st.text_input(

        "Tail Number"

        ).upper().strip()

        model = st.selectbox(

        "Aircraft Model",

        [

        "Airbus A320",

        "Airbus A350",

        "Boeing 737",

        "Boeing 777"

        ]

        )

        capa_eco = st.number_input(

        "Economy Seats",

        min_value=0,

        max_value=400,

        value=150

        )

        capa_bus = st.number_input(

        "Business Seats",

        min_value=0,

        max_value=100,

        value=20

        )

        if st.button(

        "Register Aircraft"

        ):

            if tail_num:

                try:

                    execute_query(

                    "INSERT INTO Fleet VALUES (?, ?, ?, ?)",

                    (

                    tail_num,

                    model,

                    int(capa_eco),

                    int(capa_bus)

                    )

                    )

                    st.success(

                    f"{tail_num} added"

                    )

                    st.rerun()

                except Exception as e:

                    st.error(e)

    with col2:

        st.subheader(

        "🗺️ Create Route"

        )

        dep = st.text_input(

        "Departure Airport"

        ).upper().strip()

        arr = st.text_input(

        "Arrival Airport"

        ).upper().strip()

        duration = st.text_input(

        "Flight Duration",

        value="90"

        )

        if st.button(

        "Create Route"

        ):

            if dep and arr:

                route_id = f"{dep}-{arr}"

                try:

                    execute_query(

                    "INSERT INTO Route VALUES (?, ?, ?, ?)",

                    (

                    route_id,

                    dep,

                    arr,

                    duration

                    )

                    )

                    st.success(

                    f"{route_id} created"

                    )

                    st.rerun()

                except Exception as e:

                    st.error(e)

    st.divider()

    st.subheader(

    "📊 Active Fleet"

    )

    try:

        fleet_data = execute_query(

        "SELECT * FROM Fleet",

        fetch=True

        )

        st.dataframe(

        fleet_data,

        use_container_width=True,

        hide_index=True

        )

    except:

        st.info(

        "No aircraft"

        )

# =====================================================
# FLIGHT SCHEDULING
# =====================================================

elif menu == "📅 Flight Scheduling":

    st.header(

    "📅 Flight Scheduling & Inventory"

    )

    try:

        total_flights = len(

            execute_query(

            "SELECT * FROM Flight",

            fetch=True

            )

        )

    except:

        total_flights = 0

    st.metric(

    "✈️ Scheduled Flights",

    total_flights

    )

    try:

        fleet_list = [

        r[0]

        for r in execute_query(

        "SELECT tail_number FROM Fleet",

        fetch=True

        )

        ]

        routes_list = [

        r[0]

        for r in execute_query(

        "SELECT route_id FROM Route",

        fetch=True

        )

        ]

    except:

        fleet_list = []

        routes_list = []

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

            date_flight = st.date_input(

            "Departure Date"

            )

            time_flight = st.time_input(

            "Departure Time"

            )

            price_bus = st.number_input(

            "Price Business",

            min_value=20.0,

            max_value=5000.0,

            value=299.0

            )

        if st.button(

        "Schedule Flight"

        ):

            st.success(

            "Flight scheduled"

            )

    st.divider()

    st.subheader(

    "📋 Flight Schedule"

    )

    try:

        flights = execute_query(

        "SELECT * FROM Flight",

        fetch=True

        )

        st.dataframe(

        flights,

        use_container_width=True,

        hide_index=True

        )

    except:

        st.info(

        "No flights scheduled"

        )
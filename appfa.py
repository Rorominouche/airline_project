import streamlit as st
import httpx
import urllib3
import pandas as pd

# ⚠️ SSL bypass (dev / entreprise)
urllib3.disable_warnings()
 
# =====================
# CONFIG TURSO
# =====================
TURSO_DB_URL = "https://airline-faustine-ambrine.aws-eu-west-1.turso.io"
TURSO_AUTH_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODE2MTQyMTYsImlkIjoiMDE5ZWNhYmEtZWUwMS03YWNiLTk2YjQtOGIyYzcxZWI2YmM1IiwicmlkIjoiYmFiZDVlMWItOWNlOS00MDQ1LThjMWQtODQ3NjY3MThjOGY1In0.xUmk2p0anjZGi1t_txWGRxscu_grCUhA-QzSsMqUwYjSC0jRCWPZxykJMPsv8IFR2tbwaGD3JkVLthkDWUdQAw"
 
st.set_page_config(page_title="Airline Manager", page_icon="✈️", layout="wide")
 
st.title("✈️ Airline Manager")
 
# =====================
# MENU SIMPLE
# =====================
menu = st.sidebar.selectbox(
    "Navigation",
    ["Fleet ✈️", "Routes 🛫"]
)
 
# =========================================================
# ===================== FLEET ==============================
# =========================================================
if menu == "Fleet ✈️":
 
    st.header("✈️ Ajouter un avion")
 
    with st.form("fleet_form"):
        tail_number = st.text_input("Tail Number")
        aircraft_model = st.text_input("Aircraft Model")
 
        economy_capacity = st.number_input("Economy Capacity", min_value=0, step=1)
        business_capacity = st.number_input("Business Capacity", min_value=0, step=1)
 
        submit = st.form_submit_button("Ajouter l'avion")
 
    if submit:
 
        if not tail_number or not aircraft_model:
            st.error("Champs obligatoires manquants")
            st.stop()
 
        query = {
            "requests": [
                {
                    "type": "execute",
                    "stmt": {
                        "sql": """
                            INSERT INTO FLEET
                            (tail_number, aircraft_model, economy_capacity, business_capacity)
                            VALUES (?, ?, ?, ?)
                        """,
                        "args": [
                            {"type": "text", "value": str(tail_number)},
                            {"type": "text", "value": str(aircraft_model)},
                            {"type": "text", "value": str(economy_capacity)},
                            {"type": "text", "value": str(business_capacity)}
                        ]
                    }
                }
            ]
        }
 
        headers = {
            "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
            "Content-Type": "application/json"
        }
 
        try:
            r = httpx.post(
                f"{TURSO_DB_URL}/v2/pipeline",
                json=query,
                headers=headers,
                verify=False,
                follow_redirects=True,
                timeout=30
            )
 
            st.write("STATUS:", r.status_code)
 
            try:
                st.json(r.json())
            except:
                st.code(r.text)
 
            if r.status_code == 200:
                st.success("✈️ Avion ajouté avec succès")
            else:
                st.error("Erreur API Turso")
 
        except Exception as e:
            st.exception(e)

    # --- AJOUT TABLEAU FLEET ---
    st.write("---")
    st.subheader("📋 Liste des avions (FLEET)")
    
    select_query = {
        "requests": [
            {"type": "execute", "stmt": {"sql": "SELECT * FROM FLEET"}},
            {"type": "close"}
        ]
    }
    headers = {"Authorization": f"Bearer {TURSO_AUTH_TOKEN}", "Content-Type": "application/json"}
    
    try:
        res = httpx.post(f"{TURSO_DB_URL}/v2/pipeline", json=select_query, headers=headers, verify=False, timeout=10)
        if res.status_code == 200 and "result" in res.json()["results"][0]["response"]:
            result_data = res.json()["results"][0]["response"]["result"]
            columns = [col["name"] for col in result_data["cols"]]
            rows = [[cell["value"] if isinstance(cell, dict) and "value" in cell else cell for cell in row] for row in result_data["rows"]]
            df_fleet = pd.DataFrame(rows, columns=columns)
            st.dataframe(df_fleet, use_container_width=True)
        else:
            st.info("Aucun avion enregistré ou table introuvable.")
    except Exception as e:
        st.error(f"Erreur lors du chargement de la flotte : {e}")
 
# =========================================================
# ===================== ROUTES =============================
# =========================================================
elif menu == "Routes 🛫":
 
    st.header("🛫 Ajouter une route")
 
    with st.form("route_form"):
        route_id = st.text_input("Route ID")
        departure_airport = st.text_input("Departure Airport")
        arrival_airport = st.text_input("Arrival Airport")
        flight_duration = st.text_input("Flight Duration (ex: 2h30)")
 
        submit = st.form_submit_button("Ajouter la route")
 
    if submit:
 
        if not route_id or not departure_airport or not arrival_airport:
            st.error("Champs obligatoires manquants")
            st.stop()
 
        query = {
            "requests": [
                {
                    "type": "execute",
                    "stmt": {
                        "sql": """
                            INSERT INTO ROUTE
                            (route_id, departure_airport, arrival_airport, flight_duration)
                            VALUES (?, ?, ?, ?)
                        """,
                        "args": [
                            {"type": "text", "value": str(route_id)},
                            {"type": "text", "value": str(departure_airport)},
                            {"type": "text", "value": str(arrival_airport)},
                            {"type": "text", "value": str(flight_duration)}
                        ]
                    }
                }
            ]
        }
 
        headers = {
            "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
            "Content-Type": "application/json"
        }
 
        try:
            r = httpx.post(
                f"{TURSO_DB_URL}/v2/pipeline",
                json=query,
                headers=headers,
                verify=False,
                follow_redirects=True,
                timeout=30
            )
 
            st.write("STATUS:", r.status_code)
 
            try:
                st.json(r.json())
            except:
                st.code(r.text)
 
            if r.status_code == 200:
                st.success("🛫 Route ajoutée avec succès")
            else:
                st.error("Erreur API Turso")
 
        except Exception as e:
            st.exception(e)

    # --- AJOUT TABLEAU ROUTES ---
    st.write("---")
    st.subheader("📋 Liste des routes (ROUTE)")
    
    select_query = {
        "requests": [
            {"type": "execute", "stmt": {"sql": "SELECT * FROM ROUTE"}},
            {"type": "close"}
        ]
    }
    headers = {"Authorization": f"Bearer {TURSO_AUTH_TOKEN}", "Content-Type": "application/json"}
    
    try:
        res = httpx.post(f"{TURSO_DB_URL}/v2/pipeline", json=select_query, headers=headers, verify=False, timeout=10)
        res_json = res.json()
        
        # Fallback automatique sur ROUTES si la table au singulier renvoie une erreur
        if res.status_code == 200 and "error" in res_json["results"][0]["response"]:
            select_query["requests"][0]["stmt"]["sql"] = "SELECT * FROM ROUTES"
            res = httpx.post(f"{TURSO_DB_URL}/v2/pipeline", json=select_query, headers=headers, verify=False, timeout=10)
            res_json = res.json()

        if res.status_code == 200 and "result" in res_json["results"][0]["response"]:
            result_data = res_json["results"][0]["response"]["result"]
            columns = [col["name"] for col in result_data["cols"]]
            rows = [[cell["value"] if isinstance(cell, dict) and "value" in cell else cell for cell in row] for row in result_data["rows"]]
            df_routes = pd.DataFrame(rows, columns=columns)
            st.dataframe(df_routes, use_container_width=True)
        else:
            st.info("Aucune route enregistrée ou table introuvable.")
    except Exception as e:
        st.error(f"Erreur lors du chargement des routes : {e}")
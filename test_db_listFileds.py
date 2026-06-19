import httpx
import urllib3

# ⚠️ SSL bypass pour les environnements réseau entreprise/université
urllib3.disable_warnings()

# =====================================================================
# CONFIGURATION RECOLLÉE ET VÉRIFIÉE
# =====================================================================
TURSO_DB_URL = "https://airline-faustine-ambrine.aws-eu-west-1.turso.io"
TURSO_AUTH_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODE2MTQyMTYsImlkIjoiMDE5ZWNmYmEtZWUwMS03YWNiLTk2YjQtOGIyYzcxZWI2YmM1IiwicmlkIjoiYmFiZDVlMWItOWNlOS00MDQ1LThjMWQtODQ3NjY3MThjOGY1In0.xUmk2p0anjZGi1t_txWGRxscu_grCUhA-QzSsMqUwYjSC0jRCWPZxykJMPsv8IFR2tbwaGD3JkVLthkDWUdQAw"

headers = {
    "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
    "Content-Type": "application/json"
}

def execute_sql(sql_query):
    """Envoie une requête SQL à l'API v2 de Turso et renvoie les lignes brutes."""
    payload = {
        "requests": [
            {"type": "execute", "stmt": {"sql": sql_query}},
            {"type": "close"}
        ]
    }
    r = httpx.post(f"{TURSO_DB_URL}/v2/pipeline", json=payload, headers=headers, verify=False, timeout=10)
    
    if r.status_code != 200:
        raise Exception(f"Erreur API ({r.status_code}): {r.text}")
        
    res_json = r.json()
    
    if "error" in res_json:
        raise Exception(f"Erreur Turso Globale : {res_json['error']}")
        
    response_status = res_json["results"][0]["response"]
    if "error" in response_status:
        raise Exception(f"Erreur SQL : {response_status['error'].get('message')}")
        
    return response_status["result"]["rows"]

# =====================================================================
# SCRIPT PRINCIPAL
# =====================================================================
print("🔍 Inspection du schéma de la base de données Turso...\n")

try:
    # 1. Récupération de la liste de toutes les tables utilisateurs
    get_tables_sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    tables = execute_sql(get_tables_sql)
    
    if not tables:
        print("ℹ️ La base de données est connectée mais elle ne contient aucune table.")
    else:
        print(f"✅ Connexion réussie ! Écosystème trouvé : {len(tables)} table(s)\n")
        print("==================================================")
        
        # 2. Pour chaque table, on nettoie son nom et on inspecte ses colonnes
        for table_row in tables:
            raw_table_cell = table_row[0]
            table_name = raw_table_cell["value"] if isinstance(raw_table_cell, dict) and "value" in raw_table_cell else raw_table_cell
            
            print(f"\n📋 TABLE : {table_name}")
            print("-" * 40)
            
            # Requête SQLite pour inspecter les colonnes d'une table spécifique
            get_fields_sql = f"PRAGMA table_info({table_name});"
            fields = execute_sql(get_fields_sql)
            
            for field_row in fields:
                f_name_cell = field_row[1]
                f_type_cell = field_row[2]
                f_pk_cell = field_row[5]
                
                field_name = f_name_cell["value"] if isinstance(f_name_cell, dict) and "value" in f_name_cell else f_name_cell
                field_type = f_type_cell["value"] if isinstance(f_type_cell, dict) and "value" in f_type_cell else f_type_cell
                is_pk = f_pk_cell["value"] if isinstance(f_pk_cell, dict) and "value" in f_pk_cell else f_pk_cell
                
                pk_marker = " 🔑 [PK]" if str(is_pk) == "1" else ""
                
                print(f"  🔹 {field_name:<25} ({field_type}){pk_marker}")
        
        print("\n==================================================")

except Exception as e:
    print(f"❌ Impossible d'analyser la base de données.")
    print(f"Détail : {e}")
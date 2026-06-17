import libsql_client

# =====================================================================
# CONFIGURATION
# =====================================================================
TURSO_URL = "https://airline-faustine-ambrine.aws-eu-west-1.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODE2MTE3ODEsImlkIjoiMDE5ZWNhYmEtZWUwMS03YWNiLTk2YjQtOGIyYzcxZWI2YmM1IiwicmlkIjoiYmFiZDVlMWItOWNlOS00MDQ1LThjMWQtODQ3NjY3MThjOGY1In0.ChTY9CVEHt62O2K51NYw2VZpGHUV5vYxNXoB-i0n7CnoceZY_FgQKJsZymatE736A-lb_891DOElJRvazn4tDw"

# 1. Données de l'avion à insérer
tail_number = "F-GTAB"
aircraft_model = "Airbus A320"
economy_capacity = 150
business_capacity = 20

# 2. Requête SQL d'insertion
# (Adapte les noms des colonnes si elles sont différentes dans leur table)
query = """
    INSERT INTO FLEET (tail_number, aircraft_model, economy_capacity, business_capacity)
    VALUES (?, ?, ?, ?);
"""

print(f"⏳ Insertion de l'appareil {tail_number} dans le Cloud Turso...")

try:
    # Connexion au client
    client = libsql_client.create_client_sync(url=TURSO_URL, auth_token=TURSO_TOKEN)
    
    # Exécution de la requête avec les paramètres
    client.execute(query, (tail_number, aircraft_model, economy_capacity, business_capacity))
    
    print(f"✅ Ligne ajoutée avec succès ! L'avion {tail_number} est enregistré.")
    
    # Vérification : on re-sélectionne la table pour confirmer la présence de la ligne
    print("\n📊 Vérification du contenu actuel de la table FLEET :")
    check_query = "SELECT * FROM FLEET;"
    result = client.execute(check_query)
    
    for row in result.rows:
        print(f"  ✈️  {list(row)}")
        
    client.close()

except Exception as e:
    print("\n❌ Erreur lors de l'insertion.")
    print(f"Détail de l'erreur : {e}")
import time
import pyautogui

# Sécurité FailSafe active
pyautogui.FAILSAFE = True

# Liste des routes de test (Format: Route_ID, Départ, Arrivée, Durée)
TEST_ROUTES = [
    ("NCE-CDG", "NCE", "CDG", "95"),
    ("CDG-JFK", "CDG", "JFK", "650"),
    ("NCE-DXB", "NCE", "DXB", "380")
]

print("🚀 Lancement du robot de création de routes dans 5 secondes...")
print("👉 Ouvre ton navigateur sur l'appli (onglet Routes) et mets-le en PLEIN ÉCRAN !")
time.sleep(5)

for i, (route_id, dep, arr, duration) in enumerate(TEST_ROUTES):
    print(f"🤖 Ligne {i+1}/{len(TEST_ROUTES)} : Configuration du vol {route_id}")

    # --- ÉTAPE 1 : Remplir le "Route ID" ---
    # Coordonnées estimées du 1er champ (À ajuster selon ton écran)
    pyautogui.moveTo(x=-4000, y=730, duration=0.6)
    pyautogui.click()
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.write(route_id, interval=0.05)

    # --- ÉTAPE 2 : Aller sur "Departure Airport" (Touche TAB ou Clic) ---
    pyautogui.press('tab')
    time.sleep(0.2)
    pyautogui.write(dep, interval=0.05)

    # --- ÉTAPE 3 : Aller sur "Arrival Airport" ---
    pyautogui.press('tab')
    time.sleep(0.2)
    pyautogui.write(arr, interval=0.05)

    # --- ÉTAPE 4 : Aller sur "Flight Duration" ---
    pyautogui.press('tab')
    time.sleep(0.2)
    pyautogui.write(duration, interval=0.05)
    time.sleep(0.5)

    # --- ÉTAPE 5 : Clic sur le bouton "Ajouter la route" ---
    # Coordonnées estimées du bouton de soumission du formulaire
    pyautogui.moveTo(x=500, y=650, duration=0.5)
    pyautogui.click()

    print("⏳ Route envoyée ! Attente du rafraîchissement de la base Turso...")
    time.sleep(4.0) # Temps de latence pour voir le tableau se mettre à jour en direct
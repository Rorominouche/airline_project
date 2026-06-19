import time
import ctypes
import random
import string
import pyautogui

# Correction pour écrans avec mise à l'échelle Windows (125%, 150%, etc.)
# Sans ça, les coordonnées de pyautogui ne correspondent pas à l'écran réel
try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass  # ignore si pas sous Windows

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
    pyautogui.moveTo(x=1226, y=463, duration=0.6)
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
    pyautogui.moveTo(x=1259, y=778, duration=0.5)
    pyautogui.click()

    print("⏳ Route envoyée ! Attente du rafraîchissement de la base Turso...")
    time.sleep(4.0) # Temps de latence pour voir le tableau se mettre à jour en direct

    # ==========================
# ROBOT AIRCRAFT FLEET
# ==========================

MODELS = ["A319", "A320", "A321", "A330", "B737", "B738", "B772", "B788"]
USED_TAILS = set()

def random_tail_number():
    """Génère une immat. complètement aléatoire, du type F-XXXX, unique sur ce lancement."""
    while True:
        suffix = ''.join(random.choices(string.ascii_uppercase, k=4))
        tail = f"F-{suffix}"
        if tail not in USED_TAILS:
            USED_TAILS.add(tail)
            return tail

def random_aircraft():
    tail = random_tail_number()
    model = random.choice(MODELS)
    eco_seats = str(random.randint(90, 320))
    business_seats = str(random.randint(4, 48))
    return (tail, model, eco_seats, business_seats)

# Entre 2 et 3 appareils, générés aléatoirement à chaque lancement
NB_AIRCRAFTS = random.randint(2, 3)
AIRCRAFTS = [random_aircraft() for _ in range(NB_AIRCRAFTS)]

print(f"🎲 {NB_AIRCRAFTS} appareils générés aléatoirement : {AIRCRAFTS}")

print("✈️ Début création Aircraft Fleet dans 5 secondes...")
time.sleep(5)

for tail_number, model, eco_seats, business_seats in AIRCRAFTS:

    print(f"Création de l'appareil {tail_number}")

    # Tail Number
    pyautogui.moveTo(650, 470, duration=0.5)
    pyautogui.click()

    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")
    pyautogui.write(tail_number, interval=0.05)

    # Aircraft Model
    pyautogui.press("tab")
    pyautogui.write(model, interval=0.05)

    # Economy Seats
    pyautogui.press("tab")
    pyautogui.write(eco_seats, interval=0.05)

    # Business Seats
    pyautogui.press("tab")
    pyautogui.write(business_seats, interval=0.05)

    # Bouton Ajouter (Register Aircraft)
    pyautogui.moveTo(592, 915, duration=0.5)
    pyautogui.click()

    print(f"✅ {tail_number} ajouté")

    # Temps d'attente pour laisser la base se mettre à jour
    time.sleep(3)
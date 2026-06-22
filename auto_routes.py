import time
import random
import pyautogui

# ==================================
# CONFIGURATION
# ==================================

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

# Nombre de routes à créer
NB_ROUTES = 5

# Coordonnées du champ Departure Airport
DEPARTURE = (1000, 615)

# ==================================
# 50 ROUTES RÉELLES
# ==================================

ROUTES = [

("NCE","CDG",95),
("CDG","JFK",480),
("CDG","LHR",80),
("CDG","MAD",125),
("CDG","FCO",110),

("NCE","LHR",120),
("NCE","MAD",95),
("NCE","FCO",70),
("NCE","AMS",120),
("NCE","FRA",95),

("LHR","JFK",450),
("LHR","DXB",420),
("LHR","MAD",145),
("LHR","FCO",150),
("LHR","AMS",75),

("JFK","LAX",370),
("JFK","ORD",150),
("JFK","MIA",180),
("JFK","ATL",155),
("JFK","YYZ",95),

("LAX","SFO",90),
("LAX","SEA",165),
("LAX","LAS",75),
("LAX","ORD",245),
("LAX","MEX",240),

("FRA","AMS",65),
("FRA","VIE",85),
("FRA","IST",180),
("FRA","ATH",165),
("FRA","DXB",390),

("MAD","LIS",80),
("MAD","BCN",75),
("MAD","ATH",210),
("MAD","IST",240),
("MAD","CAI",270),

("FCO","ATH",125),
("FCO","IST",150),
("FCO","CAI",180),
("FCO","VIE",95),
("FCO","AMS",135),

("DXB","DEL",190),
("DXB","SIN",450),
("DXB","BKK",390),
("DXB","SYD",840),
("DXB","CAI",240),

("SIN","BKK",145),
("SIN","HKG",235),
("SIN","DEL",330),
("SIN","SYD",470),
("SIN","NRT",420)

]

# Éviter les doublons
random.shuffle(ROUTES)

routes_a_creer = ROUTES[:NB_ROUTES]

# ==================================
# DÉMARRAGE
# ==================================

print("Ouvre la page Routes.")

for i in range(5, 0, -1):

    print(i)

    time.sleep(1)

# ==================================
# CRÉATION DES ROUTES
# ==================================

for dep, arr, duration in routes_a_creer:

    print(f"{dep} -> {arr} ({duration} min)")

    # ------------------
    # Departure Airport
    # ------------------

    pyautogui.moveTo(
        DEPARTURE[0],
        DEPARTURE[1],
        duration=2
    )

    pyautogui.click()

    pyautogui.hotkey("ctrl", "a")

    pyautogui.write(
        dep,
        interval=0.05
    )

    # ------------------
    # Arrival Airport
    # ------------------

    pyautogui.press("tab")

    pyautogui.write(
        arr,
        interval=0.05
    )

    # ------------------
    # Duration
    # ------------------

    pyautogui.press("tab")

    pyautogui.hotkey("ctrl", "a")

    pyautogui.write(
        str(duration)
    )

    # ------------------
    # Create Route
    # ------------------

    pyautogui.press("tab")

    pyautogui.press("enter")

    time.sleep(1.5)

print("Terminé.")
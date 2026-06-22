import time
import random
import string
import pyautogui
from datetime import datetime, timedelta

# ==========================
# CONFIGURATION
# ==========================

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.8

NB_FLIGHTS = 2

# Coordonnées

FLIGHT_NUMBER = (131, 605)

SELECT_ROUTE = (120, 709)

ASSIGN_AIRCRAFT = (701, 603)

DEPARTURE_TIME = (1267, 703)

NB_ROUTES = 20

NB_AIRCRAFTS = 4

# ==========================
# ROUTES
# ==========================

ROUTES = [

("NCE-CDG",95),
("CDG-JFK",480),
("CDG-LHR",80),
("CDG-MAD",125),
("CDG-FCO",110),

("NCE-LHR",120),
("NCE-MAD",95),
("NCE-FCO",70),
("NCE-AMS",120),
("NCE-FRA",95),

("LHR-JFK",450),
("LHR-DXB",420),
("LHR-MAD",145),
("LHR-FCO",150),
("LHR-AMS",75),

("JFK-LAX",370),
("JFK-ORD",150),
("JFK-MIA",180),
("JFK-ATL",155),
("JFK-YYZ",95)

]

# ==========================
# FONCTIONS
# ==========================

def random_flight_number():

    lettres = ''.join(
        random.choices(
            string.ascii_uppercase,
            k=2
        )
    )

    chiffres = ''.join(
        random.choices(
            "0123456789",
            k=4
        )
    )

    return f"{lettres}{chiffres}"


def random_date():

    start = datetime(2026,6,20)

    end = datetime(2027,5,20)

    delta = end - start

    d = start + timedelta(
        days=random.randint(
            0,
            delta.days
        )
    )

    return d.strftime("%Y/%m/%d")


def random_time():

    return random.randint(0,95)


def generate_prices(duration):

    if duration <= 90:

        eco = random.randint(60,100)

    elif duration <= 180:

        eco = random.randint(100,180)

    elif duration <= 300:

        eco = random.randint(180,350)

    elif duration <= 500:

        eco = random.randint(350,700)

    else:

        eco = random.randint(700,1200)

    bus = random.randint(
        int(eco*1.4),
        int(eco*1.8)
    )

    return eco,bus

# ==========================
# DÉMARRAGE
# ==========================

print("Ouvre la page Flight Scheduling")

for i in range(5,0,-1):

    print(i)

    time.sleep(1)

# ==========================
# BOUCLE PRINCIPALE
# ==========================

for i in range(NB_FLIGHTS):

    flight = random_flight_number()

    route_index = random.randint(
        0,
        NB_ROUTES-1
    )

    aircraft_index = random.randint(
        0,
        NB_AIRCRAFTS-1
    )

    route,duration = ROUTES[route_index]

    dep_date = random_date()

    eco,bus = generate_prices(duration)

    print(f"Vol {i+1}")

    # ==========================
    # FLIGHT NUMBER
    # ==========================

    pyautogui.click(*FLIGHT_NUMBER)

    pyautogui.hotkey("ctrl","a")

    pyautogui.press("backspace")

    pyautogui.write(
        flight,
        interval=0.08
    )

    # ==========================
    # SELECT ROUTE
    # ==========================

    pyautogui.click(*SELECT_ROUTE)

    pyautogui.press("space")

    time.sleep(1)

    pyautogui.press(
        "up",
        presses=50
    )

    pyautogui.press(
        "down",
        presses=route_index
    )

    pyautogui.press("enter")

    # ==========================
    # ASSIGN AIRCRAFT
    # ==========================

    pyautogui.click(*ASSIGN_AIRCRAFT)

    pyautogui.press("space")

    time.sleep(1)

    pyautogui.press(
        "up",
        presses=20
    )

    pyautogui.press(
        "down",
        presses=aircraft_index
    )

    pyautogui.press("enter")

    # ==========================
    # PRICE ECONOMY
    # ==========================

    pyautogui.press("tab")

    pyautogui.hotkey(
        "ctrl",
        "a"
    )

    pyautogui.press("backspace")

    pyautogui.write(
        str(eco)
    )

    # ==========================
    # DEPARTURE DATE
    # ==========================

    pyautogui.press("tab")

    pyautogui.hotkey(
        "ctrl",
        "a"
    )

    pyautogui.press("backspace")

    pyautogui.write(
        dep_date,
        interval=0.08
    )

    pyautogui.press("enter")

    # ==========================
    # DEPARTURE TIME
    # ==========================

    pyautogui.click(*DEPARTURE_TIME)

    pyautogui.press("space")

    time.sleep(1)

    pyautogui.press(
        "up",
        presses=120
    )

    pyautogui.press(
        "down",
        presses=random_time()
    )

    pyautogui.press("enter")

    # ==========================
    # PRICE BUSINESS
    # ==========================

    pyautogui.press("tab")

    pyautogui.hotkey(
        "ctrl",
        "a"
    )

    pyautogui.press("backspace")

    pyautogui.write(
        str(bus)
    )

    # ==========================
    # SCHEDULE FLIGHT
    # ==========================

    pyautogui.press("tab")

    pyautogui.press("enter")

    time.sleep(3)

print("TERMINÉ ✈️")
import time
import pyautogui

# =====================================
# CONFIGURATION
# =====================================

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.4

# Nombre de fleets à créer
NB_FLEETS = 20

# Coordonnées du champ Tail Number
TAIL_NUMBER = (125, 550)

# Capacités associées
CAPACITY = {

    0: (180, 20),  # Airbus A320

    1: (320, 40),  # Airbus A350

    2: (189, 16),  # Boeing 737

    3: (350, 50)   # Boeing 777

}

# =====================================
# DÉMARRAGE
# =====================================

print("Mets la page Fleet au premier plan.")

for i in range(5, 0, -1):

    print(i)

    time.sleep(1)

# =====================================
# CRÉATION DES FLEETS
# =====================================

for i in range(NB_FLEETS):

    tail = f"F-{1000 + i}"

    model_position = i % 4

    eco, bus = CAPACITY[model_position]

    # --------------------
    # Retour sur Tail Number
    # --------------------

    pyautogui.moveTo(
        TAIL_NUMBER[0],
        TAIL_NUMBER[1],
        duration=2
    )

    pyautogui.click()

    # --------------------
    # Tail Number
    # --------------------

    pyautogui.hotkey("ctrl", "a")

    pyautogui.write(
        tail,
        interval=0.05
    )

    # --------------------
    # Aircraft Model
    # --------------------

    pyautogui.press("tab")

    time.sleep(0.5)

    # Ouvre la liste déroulante
    pyautogui.press("space")

    time.sleep(0.5)

    # Revenir au premier élément
    pyautogui.press("up", presses=5)

    time.sleep(0.3)

    # Descendre selon le fleet
    pyautogui.press(
        "down",
        presses=model_position
    )

    time.sleep(0.3)

    # Valider
    pyautogui.press("enter")

    # --------------------
    # Economy Seats
    # --------------------

    pyautogui.press("tab")

    pyautogui.hotkey("ctrl", "a")

    pyautogui.write(
        str(eco)
    )

    # --------------------
    # Business Seats
    # --------------------

    pyautogui.press("tab")

    pyautogui.hotkey("ctrl", "a")

    pyautogui.write(
        str(bus)
    )

    # --------------------
    # Register Aircraft
    # --------------------

    pyautogui.press("tab")

    time.sleep(0.5)

    pyautogui.press("enter")

    time.sleep(1.5)

print("Terminé.")

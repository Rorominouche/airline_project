import time
import pyautogui
import random

# =====================================
# CONFIGURATION
# =====================================

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.4

# Nombre de fleets à créer
NB_FLEETS = 20

# Coordonnées du champ Tail Number
TAIL_NUMBER = (2852, 166)



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

    randomA320a = random.randint(15, 30)
    randomA350a = random.randint(30, 50)
    randomB737a = random.randint(10, 25)
    randomB777a = random.randint(35, 60)

    randomA320b = 200 - randomA320a
    randomA350b = 360 - randomA350a
    randomB737b = 205 - randomB737a
    randomB777b = 400 - randomB777a

    # Capacités associées
    CAPACITY = {

        0: (randomA320b, randomA320a),  # Airbus A320

        1: (randomA350b, randomA350a),  # Airbus A350

        2: (randomB737b, randomB737a),  # Boeing 737

        3: (randomB777b, randomB777a)   # Boeing 777

    }

    tail = f"F-{1000 + random.randint(0, 8999)}"

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

    def write_tail_number(tail):
    # Écrit caractère par caractère en gérant les touches spéciales AZERTY
        for char in tail:
            if char == 'F':
                pyautogui.keyDown('shift')
                pyautogui.press('f')
                pyautogui.keyUp('shift')
            elif char == '-':
                pyautogui.press('6')  # Sur AZERTY, - est sur la touche 6 sans Maj
            elif char.isdigit():
                pyautogui.keyDown('shift')
                pyautogui.press(char)
                pyautogui.keyUp('shift')
            else:
                pyautogui.write(char, interval=0.05)
    write_tail_number(tail)

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

    pyautogui.keyDown('shift')
    pyautogui.write(
        str(eco)
    )
    pyautogui.keyUp('shift')

    # --------------------
    # Business Seats
    # --------------------

    pyautogui.press("tab")

    pyautogui.hotkey("ctrl", "a")

    pyautogui.keyDown('shift')
    pyautogui.write(
        str(bus)
    )
    pyautogui.keyUp('shift')
 
    # --------------------
    # Register Aircraft
    # --------------------

    pyautogui.press("tab")
 
    time.sleep(0.5)

    pyautogui.press("enter")

    time.sleep(1.5)

print("Terminé.")

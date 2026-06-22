import pyautogui
import time

print("📍 Déplace ta souris pour voir les coordonnées (Ctrl+C pour arrêter)\n")

try:
    while True:
        x, y = pyautogui.position()
        print(f"X = {x} | Y = {y}", end="\r")
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\n👋 Arrêt du script")
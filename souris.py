import pyautogui
import time

print("Tu as 5 secondes pour placer la souris sur Flight Number...")

time.sleep(5)

x, y = pyautogui.position()

print("Coordonnées :", x, y)
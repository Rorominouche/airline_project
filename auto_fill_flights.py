"""
==========================================================
 AUTO-REMPLISSAGE DEMO - Amadeus Airline Operations Center
==========================================================

Ce script pilote un VRAI navigateur (Chromium) avec Playwright pour
remplir automatiquement le formulaire "Flights" de ton app Streamlit,
en simulant des déplacements de souris visibles et la touche TAB
pour passer d'un champ à l'autre, comme le ferait un humain.

PRÉ-REQUIS
----------
1. Ton app Streamlit doit déjà tourner en local :
       streamlit run app.py
   (par défaut sur http://localhost:8501)

2. Installer Playwright (une seule fois) :
       pip install playwright
       playwright install chromium

UTILISATION
-----------
       python auto_fill_flights.py

Réglages rapides tout en bas du fichier (NB_VOLS, STREAMLIT_URL, etc.)
==========================================================
"""

import random
import string
import time
from datetime import date, timedelta

from playwright.sync_api import sync_playwright, Page


# ==========================================================
# CONFIGURATION
# ==========================================================

STREAMLIT_URL = "http://localhost:8501"

NB_VOLS = 5  # nombre de vols à créer pendant cette exécution

DATE_MIN = date(2026, 6, 20)
DATE_MAX = date(2027, 5, 20)

PRIX_MIN = 49.0
PRIX_MAX = 599.0

# Vitesse de la démo : plus haut = plus lent / plus visible
PAUSE_COURTE = 0.4
PAUSE_MOYENNE = 0.8
PAUSE_LONGUE = 1.3


# ==========================================================
# UTILITAIRES DE GENERATION
# ==========================================================

def generer_numero_vol() -> str:
    """Génère un numéro de vol style 'AF1234'."""
    compagnies = ["AF", "BA", "LH", "KL", "IB", "EK", "QR"]
    prefixe = random.choice(compagnies)
    chiffres = "".join(random.choices(string.digits, k=4))
    return f"{prefixe}{chiffres}"


def generer_date_aleatoire() -> date:
    """Date aléatoire entre DATE_MIN et DATE_MAX inclus."""
    delta_jours = (DATE_MAX - DATE_MIN).days
    offset = random.randint(0, delta_jours)
    return DATE_MIN + timedelta(days=offset)


def generer_heure_aleatoire() -> tuple[int, int]:
    """Heure aléatoire entre 00:00 et 23:59."""
    return random.randint(0, 23), random.randint(0, 59)


def generer_prix() -> float:
    return round(random.uniform(PRIX_MIN, PRIX_MAX), 2)


# ==========================================================
# AIDES PLAYWRIGHT : SOURIS VISIBLE + TAB
# ==========================================================

def deplacer_souris_vers(page: Page, locator, pause=PAUSE_MOYENNE):
    """
    Déplace la souris visuellement jusqu'à l'élément avant de cliquer,
    pour que le mouvement soit visible pendant la démo (au lieu d'un
    clic instantané invisible).
    """
    locator.scroll_into_view_if_needed()
    box = locator.bounding_box()
    if box is None:
        # Si l'élément n'est pas trouvable, on retente après un court délai
        time.sleep(pause)
        box = locator.bounding_box()
    if box:
        x = box["x"] + box["width"] / 2
        y = box["y"] + box["height"] / 2
        # déplacement en plusieurs étapes pour un mouvement fluide/visible
        page.mouse.move(x, y, steps=25)
    time.sleep(pause)


def cliquer_avec_souris(page: Page, locator, pause=PAUSE_MOYENNE):
    deplacer_souris_vers(page, locator, pause)
    locator.click()
    time.sleep(PAUSE_COURTE)


def appuyer_tab(page: Page, pause=PAUSE_COURTE):
    """Simule la touche TAB pour passer au champ suivant."""
    page.keyboard.press("Tab")
    time.sleep(pause)


# ==========================================================
# REMPLISSAGE D'UN VOL
# ==========================================================

def remplir_un_vol(page: Page, index: int):
    print(f"\n--- Création du vol {index + 1}/{NB_VOLS} ---")

    flight_number = generer_numero_vol()
    d = generer_date_aleatoire()
    heure, minute = generer_heure_aleatoire()
    prix = generer_prix()

    print(f"  Numéro de vol : {flight_number}")
    print(f"  Date          : {d.strftime('%Y/%m/%d')}")
    print(f"  Heure         : {heure:02d}:{minute:02d}")
    print(f"  Prix          : {prix} €")

    # ------------------------------------------------------
    # 1) Champ "Flight Number"
    # ------------------------------------------------------
    champ_flight_number = page.get_by_label("Flight Number")
    cliquer_avec_souris(page, champ_flight_number)
    champ_flight_number.fill("")
    page.keyboard.type(flight_number, delay=60)
    time.sleep(PAUSE_COURTE)

    # On passe au champ suivant (Route) avec TAB
    appuyer_tab(page)

    # ------------------------------------------------------
    # 2) Selectbox "Route" -> on le pilote au clavier après le TAB
    #    (les selectbox Streamlit s'ouvrent avec Entrée/flèche bas
    #     et se valident avec Entrée)
    # ------------------------------------------------------
    # Le focus est normalement déjà sur la selectbox Route grâce au TAB.
    # On choisit une option au hasard parmi celles disponibles.
    selectionner_option_aleatoire_selectbox(page, "Route")

    appuyer_tab(page)

    # ------------------------------------------------------
    # 3) Selectbox "Aircraft"
    # ------------------------------------------------------
    selectionner_option_aleatoire_selectbox(page, "Aircraft")

    appuyer_tab(page)

    # ------------------------------------------------------
    # 4) Date Input "Departure Date" -> format attendu par Streamlit: YYYY/MM/DD
    # ------------------------------------------------------
    champ_date = page.get_by_label("Departure Date")
    deplacer_souris_vers(page, champ_date, PAUSE_MOYENNE)
    champ_date.click()
    # On sélectionne tout le contenu existant puis on tape la nouvelle date
    page.keyboard.press("Control+A")
    page.keyboard.type(d.strftime("%Y/%m/%d"), delay=70)
    time.sleep(PAUSE_COURTE)
    page.keyboard.press("Escape")  # ferme le mini calendrier s'il s'est ouvert
    time.sleep(PAUSE_COURTE)

    appuyer_tab(page)

    # ------------------------------------------------------
    # 5) Time Input "Departure Time" -> menu déroulant Streamlit
    #    (liste d'horaires toutes les 15 min en général : on tape l'heure
    #     directement, c'est la méthode la plus fiable au clavier)
    # ------------------------------------------------------
    champ_heure = page.get_by_label("Departure Time")
    deplacer_souris_vers(page, champ_heure, PAUSE_MOYENNE)
    champ_heure.click()
    time.sleep(PAUSE_COURTE)

    heure_str = f"{heure:02d}:{minute:02d}"
    # Le widget time_input de Streamlit accepte la saisie clavier au format HH:MM
    page.keyboard.press("Control+A")
    page.keyboard.type(heure_str, delay=70)
    time.sleep(PAUSE_COURTE)
    page.keyboard.press("Enter")
    time.sleep(PAUSE_COURTE)

    appuyer_tab(page)

    # ------------------------------------------------------
    # 6) Number Input "Economy Ticket Price"
    # ------------------------------------------------------
    champ_prix = page.get_by_label("Economy Ticket Price")
    deplacer_souris_vers(page, champ_prix, PAUSE_MOYENNE)
    champ_prix.click()
    page.keyboard.press("Control+A")
    page.keyboard.type(str(prix), delay=60)
    time.sleep(PAUSE_COURTE)

    # ------------------------------------------------------
    # 7) Clic sur "Schedule Flight"
    # ------------------------------------------------------
    bouton = page.get_by_role("button", name="Schedule Flight")
    cliquer_avec_souris(page, bouton, PAUSE_LONGUE)

    time.sleep(PAUSE_LONGUE)
    print(f"  -> Vol {flight_number} enregistré.")


def selectionner_option_aleatoire_selectbox(page: Page, label: str):
    """
    Ouvre une selectbox Streamlit identifiée par son label, choisit une
    option au hasard parmi celles proposées, puis valide.
    Streamlit ouvre le menu avec Entrée ou flèche bas, puis on navigue
    avec les flèches et on valide avec Entrée.
    """
    page.keyboard.press("Enter")  # ouvre le menu déroulant
    time.sleep(PAUSE_COURTE)

    options = page.locator('li[role="option"]')
    options.first.wait_for(state="visible", timeout=5000)
    nb_options = options.count()

    if nb_options == 0:
        page.keyboard.press("Escape")
        return

    choix = random.randint(0, nb_options - 1)

    deplacer_souris_vers(page, options.nth(choix), PAUSE_MOYENNE)
    options.nth(choix).click()
    time.sleep(PAUSE_COURTE)


# ==========================================================
# SCRIPT PRINCIPAL
# ==========================================================

def main():
    with sync_playwright() as p:
        # headless=False : on VOIT le navigateur et les mouvements de souris
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        print(f"Ouverture de {STREAMLIT_URL} ...")
        page.goto(STREAMLIT_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(1.5)

        # On clique sur "Flights" dans le menu de navigation à gauche
        menu_flights = page.get_by_text("Flights", exact=True)
        cliquer_avec_souris(page, menu_flights, PAUSE_MOYENNE)
        time.sleep(1.0)

        for i in range(NB_VOLS):
            try:
                remplir_un_vol(page, i)
            except Exception as e:
                print(f"  /!\\ Erreur sur le vol {i + 1} : {e}")
                print("  On continue avec le vol suivant...")
            time.sleep(PAUSE_LONGUE)

        print("\nTerminé. Le navigateur reste ouvert 5 secondes pour vérification.")
        time.sleep(5)
        browser.close()


if __name__ == "__main__":
    main()

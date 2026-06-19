"""
Visualisation d'un plan de sièges (vue de dessus) d'un Airbus A380.
- Vert  = siège disponible
- Rouge = siège occupé

Le plan est simplifié (pas une carte officielle Airbus) : deux ponts
(pont principal et pont supérieur) avec une configuration de sièges
représentative d'un A380 en 3 classes.

Dépendances : matplotlib
    pip install matplotlib
"""

import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

random.seed(42)  # pour des résultats reproductibles, à retirer si besoin

# ----------------------------------------------------------------------
# 1. Définition de la configuration des sièges
# ----------------------------------------------------------------------
# Chaque pont est une liste de "rangées".
# Une rangée est définie par : (numéro de rangée, motif de sièges)
# Le motif est une chaîne où chaque caractère représente soit un siège
# ('S') soit une allée (' ' = espace).
#
# Pont supérieur (Upper deck) : Business (2-2-2) + Economy (2-4-2)
# Pont principal (Main deck)  : Première classe (1-2-1) + Economy (3-4-3)

upper_deck_layout = []
# Business class, rangées 1 à 15, motif 2-2-2
for row in range(1, 16):
    upper_deck_layout.append((row, "SS SS SS"))
# Economy (pont supérieur), rangées 16 à 45, motif 2-4-2
for row in range(16, 46):
    upper_deck_layout.append((row, "SS SSSS SS"))

main_deck_layout = []
# Première classe, rangées 1 à 6, motif 1-2-1
for row in range(1, 7):
    main_deck_layout.append((row, "S SS S"))
# Economy (pont principal), rangées 7 à 50, motif 3-4-3
for row in range(7, 51):
    main_deck_layout.append((row, "SSS SSSS SSS"))


def generer_occupation(layout, taux_occupation=0.7):
    """Associe à chaque siège un statut occupé/disponible aléatoire."""
    occupation = {}
    for row, pattern in layout:
        for col_idx, c in enumerate(pattern):
            if c == "S":
                occupation[(row, col_idx)] = random.random() < taux_occupation
    return occupation


upper_occupation = generer_occupation(upper_deck_layout)
main_occupation = generer_occupation(main_deck_layout)

# ----------------------------------------------------------------------
# 2. Fonction de dessin d'un pont
# ----------------------------------------------------------------------
SEAT_SIZE = 0.8
SEAT_GAP = 0.15
ROW_GAP = 0.15


def dessiner_pont(ax, layout, occupation, titre, y_offset=0):
    """Dessine un pont (liste de rangées) sur l'axe donné."""
    max_cols = max(len(pattern) for _, pattern in layout)

    for row, pattern in layout:
        y = y_offset - (row - 1) * (SEAT_SIZE + ROW_GAP)
        for col_idx, c in enumerate(pattern):
            if c != "S":
                continue
            x = col_idx * (SEAT_SIZE + SEAT_GAP)
            occupe = occupation[(row, col_idx)]
            couleur = "#e74c3c" if occupe else "#2ecc71"  # rouge / vert
            rect = patches.FancyBboxPatch(
                (x, y),
                SEAT_SIZE,
                SEAT_SIZE,
                boxstyle="round,pad=0.02,rounding_size=0.12",
                linewidth=0.6,
                edgecolor="#333333",
                facecolor=couleur,
            )
            ax.add_patch(rect)

        # Numéro de rangée à gauche
        ax.text(
            -0.9,
            y + SEAT_SIZE / 2,
            str(row),
            ha="right",
            va="center",
            fontsize=6,
            color="#555555",
        )

    nb_rows = len(layout)
    largeur = max_cols * (SEAT_SIZE + SEAT_GAP)
    hauteur = nb_rows * (SEAT_SIZE + ROW_GAP)

    ax.text(
        largeur / 2 - 1,
        y_offset + SEAT_SIZE,
        titre,
        ha="center",
        va="bottom",
        fontsize=13,
        fontweight="bold",
    )

    return largeur, hauteur


def dessiner_fuselage(ax, x_min, x_max, y_top, y_bottom):
    """Dessine un contour ovale simplifié représentant le fuselage."""
    largeur = x_max - x_min
    hauteur = y_top - y_bottom
    centre_x = (x_min + x_max) / 2
    centre_y = (y_top + y_bottom) / 2
    fuselage = patches.FancyBboxPatch(
        (x_min, y_bottom),
        largeur,
        hauteur,
        boxstyle="round,pad=0.6,rounding_size=2.5",
        linewidth=2,
        edgecolor="#2c3e50",
        facecolor="#ecf0f1",
        zorder=0,
    )
    ax.add_patch(fuselage)


# ----------------------------------------------------------------------
# 3. Construction de la figure
# ----------------------------------------------------------------------
fig, (ax_upper, ax_main) = plt.subplots(
    2, 1, figsize=(10, 26), gridspec_kw={"height_ratios": [45, 50]}
)

for ax, layout, occupation, titre in (
    (ax_upper, upper_deck_layout, upper_occupation, "Pont supérieur (Upper deck) — Business / Economy"),
    (ax_main, main_deck_layout, main_occupation, "Pont principal (Main deck) — Première / Economy"),
):
    largeur, hauteur = dessiner_pont(ax, layout, occupation, titre)
    dessiner_fuselage(ax, -1.4, largeur + 0.4, 1.6, -hauteur)

    ax.set_xlim(-2, largeur + 1)
    ax.set_ylim(-hauteur - 1, 2.5)
    ax.set_aspect("equal")
    ax.axis("off")

# Légende commune
legende_elements = [
    patches.Patch(facecolor="#2ecc71", edgecolor="#333333", label="Disponible"),
    patches.Patch(facecolor="#e74c3c", edgecolor="#333333", label="Occupé"),
]
fig.legend(
    handles=legende_elements,
    loc="upper center",
    ncol=2,
    fontsize=12,
    bbox_to_anchor=(0.5, 0.995),
)

fig.suptitle("Plan de sièges Airbus A380 — Vue de dessus", fontsize=18, fontweight="bold", y=1.01)

plt.tight_layout(rect=[0, 0, 1, 0.99])

# ----------------------------------------------------------------------
# 4. Export
# ----------------------------------------------------------------------
output_path = "a380_seatmap.png"
plt.savefig(output_path, dpi=150, bbox_inches="tight")
print(f"Image enregistrée : {output_path}")

plt.show()
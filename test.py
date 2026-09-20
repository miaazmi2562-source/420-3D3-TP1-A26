# fichier main de test pour le refactoring, NE PAS UTILISER app.py
import tkinter as tk
from modeles.portefeuille import Portefeuille
from observateurs.portfolio import Portfolio

INTERVALLE_MS = 30000

POLICE = ("Segoe UI", 10)
POLICE_TITRE = ("Segoe UI", 16, "bold")

TITRES = {
    "AAPL":  {"quantite": 10, "seuil_haut": 200.0, "seuil_bas": 150.0},
    "GOOGL": {"quantite": 5,  "seuil_haut": 160.0, "seuil_bas": 120.0},
    "MSFT":  {"quantite": 8,  "seuil_haut": 430.0, "seuil_bas": 380.0},
}

class App():
    def __init__(self):
        # initiation de la fenetre principal
        self.fenetre = tk.Tk()
        self.fenetre.title("Portfolio Tracker")
        self.fenetre.resizable(False, False)
        self.fenetre.option_add("*Font", POLICE)
        tk.Label(self.fenetre, text="Portfolio Tracker", font=POLICE_TITRE).pack(pady=10)

        # initialistion du portefeuille
        self.portefeuille = Portefeuille(TITRES)

        # initialisation de l'interface du portfolio
        self.portefolio_observateur = Portfolio(self.fenetre)
        self.portefeuille.abonner(self.portefolio_observateur)

        # Premier chargement des prix, puis boucle de rafraîchissement automatique
        self.rafraichir()
        self.fenetre.mainloop()

    # (rafraichir() se replanifie elle-même via fenetre.after)
    def rafraichir(self):
        self.portefeuille.rafraichir()
        # Replanifie le prochain cycle, que celui-ci ait réussi ou échoué
        self.fenetre.after(INTERVALLE_MS, self.rafraichir)


if __name__ == "__main__":
    App()

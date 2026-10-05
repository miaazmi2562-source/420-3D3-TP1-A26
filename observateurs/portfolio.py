import tkinter as tk
from observateurs.observateur import Observateur

POLICE_VALEUR = ("Segoe UI", 13, "bold")


class Portfolio(Observateur):
    # "Mon portfolio" : valeur totale et variation depuis l'ouverture,
    # mises à jour à chaque cycle de rafraîchir()
    def __init__(self, fenetre):
        self.fenetre = fenetre
        frame_portfolio = tk.LabelFrame(self.fenetre, text="Mon portfolio", padx=10, pady=10)
        frame_portfolio.pack(fill=tk.X, padx=10, pady=5)
        self.label_valeur = tk.Label(frame_portfolio, text="Valeur totale : calcul en cours...", font=POLICE_VALEUR)
        self.label_valeur.pack()
        self.label_variation = tk.Label(frame_portfolio, text="")
        self.label_variation.pack()

    # Actualise l'affichage du Portfolio 
    def actualiser(self, sujet):
        donnees = sujet.get_donnees()
        valeur_totale = donnees["valeur_totale"]
        variation_portfolio = donnees["variation_portfolio"]
        self.label_valeur.config(text=f"Valeur totale : {valeur_totale:.2f} $")
        symbole = "▲" if variation_portfolio >= 0 else "▼"
        self.label_variation.config(
            text=f"{symbole} {abs(variation_portfolio):.2f} $ depuis l'ouverture",
            fg="green" if variation_portfolio >= 0 else "red",
        )
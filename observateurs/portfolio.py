import tkinter as Tk 
from observateur import Observateur 
class Portfolio(Observateur):
    def __init__(self):
        frame_portfolio = tk.LabelFrame(self.fenetre, text="Mon portfolio", padx=10, pady=10)
        frame_portfolio.pack(fill=tk.X, padx=10, pady=5)
        self.label_valeur = tk.Label(frame_portfolio, text="Valeur totale : calcul en cours...", font=POLICE_VALEUR)
        self.label_valeur.pack()
        self.label_variation = tk.Label(frame_portfolio, text="")
        self.label_variation.pack()
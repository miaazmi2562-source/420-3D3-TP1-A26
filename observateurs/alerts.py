import tkinter as tk
from observateurs.observateur import Observateur

class Alerts(Observateur):
    def __init__(self, fenetre):
        self.fenetre = fenetre
        frame_alertes = tk.LabelFrame(self.fenetre, text="Alertes", padx=10, pady=10)
        frame_alertes.pack(fill=tk.X, padx=10, pady=5)
        self.label_alertes = tk.Label(
            frame_alertes, text="Aucune alerte", fg="gray", justify=tk.LEFT, wraplength=380
        )
        self.label_alertes.pack(anchor="w")

        self.label_maj = tk.Label(self.fenetre, text="", font=("Segoe UI", 9), fg="gray")
        self.label_maj.pack(pady=5)

    
    def actualiser(self, sujet):
        donnees = sujet.get_donnees()
        alerts_actuel = donnees["alertes"]
        self.label_alertes.config(text="\n".join(alerts_actuel) if alerts_actuel else "Aucune alerte", fg="red" if alerts_actuel else "gray")
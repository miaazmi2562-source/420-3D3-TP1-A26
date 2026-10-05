import tkinter as tk
from observateurs.observateur import Observateur
from datetime import datetime 

class Csv(Observateur):
    def __init__(self, fenetre):
        self.fenetre = fenetre 
        self.label_maj = tk.Label(self.fenetre, text="", font=("Segoe UI", 9), fg="gray")
        self.label_maj.pack(pady=5)
    
    def actualiser(self, sujet) -> None:

        donnees = sujet.get_donnees()
        prix_actuel = donnees["prix"]

        try: 

            horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("portfolio.csv", "a") as f:
                for ticker, (prix, ouverture) in prix_actuel.items():
                    f.write(f"{horodatage},{ticker},{prix:.2f},{ouverture:.2f}\n")
        
            self.label_maj.config(text=f"Dernière mise à jour : {horodatage}", fg="gray")
        
        except Exception as e:
             self.label_maj.config(text=f"Erreur : {e}", fg="red")
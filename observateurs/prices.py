import tkinter as tk
from observateurs.observateur import Observateur
from utils import formater_prix 

# creer la classe prices avec son constrcuteur: la fenetre et son titre 
class Prices(Observateur):
    def __init__(self,fenetre, titres):
        self.labels_prix = {}
        self.frames_prix = {}
        self.fenetre = fenetre 
        self.titres = titres 
        self.frame_prix = tk.LabelFrame(self.fenetre, text="Prix en temps réel", padx=10, pady=10)
        self.frame_prix.pack(fill=tk.X, padx=10, pady=5)
        for ticker in titres:
            self._creer_ligne_prix(ticker)
    
     
    def _creer_ligne_prix(self, ticker):
        """Ajoute la ligne d'affichage de prix pour un ticker (appelé au
        démarrage pour chaque titre, et à nouveau quand un titre est ajouté)."""
        frame = tk.Frame(self.frame_prix)
        frame.pack(fill=tk.X, pady=2)
        tk.Label(frame, text=f"{ticker}:", width=8, font=("Segoe UI", 10, "bold"), anchor="w").pack(side=tk.LEFT)
        label = tk.Label(frame, text="Chargement...")
        label.pack(side=tk.LEFT)
        self.labels_prix[ticker] = label
        self.frames_prix[ticker] = frame
    
    def actualiser(self, sujet):
        donnees = sujet.get_donnees()
        prix_actuel = donnees["prix"] # va chercher le prix actuel dans les donnees : prix  
        for ticker, (prix, ouverture) in prix_actuel.items(): #
            texte, couleur = formater_prix(prix, ouverture)
            self.labels_prix[ticker].config(text=texte, fg=couleur)
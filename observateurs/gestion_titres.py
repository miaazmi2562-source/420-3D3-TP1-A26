import tkinter as tk
from observateurs.observateur import Observateur
from utils import entier_positif, flottant_positif, recuperer_prix, formater_prix

class GestionTitres(Observateur):
    def __init__(self, fenetre, titres, prices):
        self.prices = prices
        self.fenetre = fenetre
        self.titres = titres
        self._construire_gestion()

    def actualiser(self, sujet):
        donnees = sujet.get_donnees()
        titres = donnees["titres"]

        self.listbox_titres.delete(0, tk.END)
        for ticker in titres:
            self.listbox_titres.insert(tk.END, self._texte_listbox(ticker))

    def _construire_gestion(self):
        """Construit la section "Gérer les titres" : formulaire d'ajout, liste
        des titres du portefeuille (avec retrait), et formulaire de modification
        de la sélection courante."""
        frame = tk.LabelFrame(self.fenetre, text="Gérer les titres", padx=10, pady=10)
        frame.pack(fill=tk.X, padx=10, pady=5)

        # Ligne 1 : formulaire d'ajout d'un nouveau titre
        ligne_ajout = tk.Frame(frame)
        ligne_ajout.pack(fill=tk.X)
        self.entry_ticker = self._champ(ligne_ajout, "Ticker", width=8)
        self.entry_quantite = self._champ(ligne_ajout, "Qté", width=5, valeur_defaut="1")
        self.entry_seuil_bas_ajout = self._champ(ligne_ajout, "Alerte basse", width=7)
        self.entry_seuil_haut_ajout = self._champ(ligne_ajout, "Alerte haute", width=7)
        tk.Button(ligne_ajout, text="Ajouter", command=self.ajouter_titre).pack(side=tk.LEFT)

        tk.Label(
            frame,
            text="(Alertes optionnelles : si vides, calculées à ±20% du prix actuel)",
            font=("Segoe UI", 8), fg="gray"
        ).pack(anchor="w", pady=(2, 5))

        # Ligne 2 : liste des titres actuellement dans le portefeuille + retrait
        # (la sélection dans cette liste sert aussi au formulaire de modification ci-dessous)
        ligne_liste = tk.Frame(frame)
        ligne_liste.pack(fill=tk.X)
        self.listbox_titres = tk.Listbox(ligne_liste, height=4, exportselection=False)
        self.listbox_titres.pack(side=tk.LEFT, fill=tk.X, expand=True)
        for ticker in self.titres:
            self.listbox_titres.insert(tk.END, self._texte_listbox(ticker))
        tk.Button(ligne_liste, text="Retirer", command=self.retirer_titre).pack(side=tk.LEFT, padx=(5, 0), anchor="n")

        # Ligne 3 : modification de la quantité et/ou des seuils du titre sélectionné
        ligne_modif = tk.Frame(frame)
        ligne_modif.pack(fill=tk.X, pady=(8, 0))
        tk.Label(ligne_modif, text="Sélection →").pack(side=tk.LEFT)
        self.entry_nouvelle_quantite = self._champ(ligne_modif, "Qté", width=5)
        self.entry_nouveau_seuil_bas = self._champ(ligne_modif, "Alerte basse", width=7)
        self.entry_nouveau_seuil_haut = self._champ(ligne_modif, "Alerte haute", width=7)
        tk.Button(ligne_modif, text="Modifier sélection", command=self.modifier_selection).pack(side=tk.LEFT)

        # Message de statut (succès / erreur) pour les actions de cette section
        self.label_statut_titres = tk.Label(frame, text="", font=("Segoe UI", 9), fg="gray")
        self.label_statut_titres.pack(anchor="w", pady=(5, 0))

    def _champ(self, parent, texte, width, valeur_defaut=""):
            """Ajoute un couple Label + Entry à `parent` et retourne l'Entry."""
            tk.Label(parent, text=f"{texte}:").pack(side=tk.LEFT)
            entry = tk.Entry(parent, width=width)
            if valeur_defaut:
                entry.insert(0, valeur_defaut)
            entry.pack(side=tk.LEFT, padx=(2, 8))
            return entry
    
    def ajouter_titre(self):
        """Valide le formulaire d'ajout, vérifie que le ticker existe via yfinance,
        puis l'insère dans TITRES et dans l'UI (ligne de prix + liste)."""
        ticker = self.entry_ticker.get().strip().upper()
        if not ticker:
            return
        if ticker in self.titres:
            self._statut(f"{ticker} est déjà dans le portfolio.", "orange")
            return

        try:
            quantite = entier_positif(self.entry_quantite.get().strip())
        except ValueError:
            self._statut("La quantité doit être un nombre entier positif.", "red")
            return

        # Les seuils sont optionnels à l'ajout : s'ils sont vides, on les
        # calcule plus bas à ±20% du prix actuel une fois celui-ci connu.
        texte_bas = self.entry_seuil_bas_ajout.get().strip()
        texte_haut = self.entry_seuil_haut_ajout.get().strip()
        try:
            seuil_bas = flottant_positif(texte_bas) if texte_bas else None
            seuil_haut = flottant_positif(texte_haut) if texte_haut else None
        except ValueError:
            self._statut("Les alertes doivent être des nombres positifs.", "red")
            return
        if seuil_bas is not None and seuil_haut is not None and seuil_bas >= seuil_haut:
            self._statut("L'alerte basse doit être inférieure à l'alerte haute.", "red")
            return
    
        # Le ticker n'existe vraiment que si yfinance renvoie un prix
        try:
            prix, ouverture = recuperer_prix(ticker)
        except Exception:
            self._statut(f"Le titre '{ticker}' n'existe pas.", "red")
            return

        self.titres[ticker] = {
            "quantite": quantite,
            "seuil_haut": round(seuil_haut if seuil_haut is not None else prix * 1.2, 2),
            "seuil_bas": round(seuil_bas if seuil_bas is not None else prix * 0.8, 2),
        }

        # Mise à jour de l'UI : nouvelle ligne de prix, nouvelle entrée dans la
        # liste, puis réinitialisation du formulaire d'ajout
        self.prices._creer_ligne_prix(ticker)
        self.listbox_titres.insert(tk.END, self._texte_listbox(ticker))
        for entry, valeur in (
            (self.entry_ticker, ""), (self.entry_quantite, "1"),
            (self.entry_seuil_bas_ajout, ""), (self.entry_seuil_haut_ajout, ""),
        ):
            entry.delete(0, tk.END)
            entry.insert(0, valeur)

        # Affiche le prix tout de suite plutôt que d'attendre le prochain
        # cycle de rafraîchir() (jusqu'à INTERVALLE_MS plus tard)
        texte, couleur = formater_prix(prix, ouverture)
        self.prices.labels_prix[ticker].config(text=texte, fg=couleur)
        self._statut(f"{ticker} ajouté au portfolio ({quantite} action(s)).", "green")
    
    def retirer_titre(self):
        """Retire le titre sélectionné dans la liste : du portefeuille (TITRES),
        de la liste, et détruit sa ligne de prix."""
        selectionne = self._ticker_selectionne()
        if selectionne is None:
            self._statut("Sélectionnez un titre à retirer.", "orange")
            return
        index, ticker = selectionne

        self.listbox_titres.delete(index)
        del self.titres[ticker]
        self.prices.labels_prix.pop(ticker, None)
        self.prices.frames_prix.pop(ticker).destroy()

        self._statut(f"{ticker} retiré du portfolio.", "gray")


    def modifier_selection(self):
        """Met à jour la quantité et/ou les seuils d'alerte du titre sélectionné.
        Chaque champ est optionnel : seuls ceux remplis sont modifiés, mais les
        deux seuils doivent être fournis ensemble pour rester cohérents."""
        selectionne = self._ticker_selectionne()
        if selectionne is None:
            self._statut("Sélectionnez un titre à modifier.", "orange")
            return
        index, ticker = selectionne

        texte_qte = self.entry_nouvelle_quantite.get().strip()
        texte_bas = self.entry_nouveau_seuil_bas.get().strip()
        texte_haut = self.entry_nouveau_seuil_haut.get().strip()
        if not texte_qte and not texte_bas and not texte_haut:
            self._statut("Entrez une nouvelle quantité et/ou de nouvelles alertes.", "orange")
            return

        changements = []
        try:
            if texte_qte:
                self.titres[ticker]["quantite"] = entier_positif(texte_qte)
                changements.append(f"{self.titres[ticker]['quantite']} action(s)")
            if texte_bas or texte_haut:
                if not (texte_bas and texte_haut):
                    self._statut("Les deux alertes doivent être fournies ensemble.", "red")
                    return
                seuil_bas, seuil_haut = flottant_positif(texte_bas), flottant_positif(texte_haut)
                if seuil_bas >= seuil_haut:
                    self._statut("L'alerte basse doit être inférieure à l'alerte haute.", "red")
                    return
                self.titres[ticker]["seuil_bas"] = round(seuil_bas, 2)
                self.titres[ticker]["seuil_haut"] = round(seuil_haut, 2)
                changements.append(f"alertes {seuil_bas:.2f} $ / {seuil_haut:.2f} $")
        except ValueError:
            self._statut("La quantité et les alertes doivent être des nombres positifs.", "red")
            return

        self._rafraichir_ligne_listbox(index, ticker)
        for entry in (self.entry_nouvelle_quantite, self.entry_nouveau_seuil_bas, self.entry_nouveau_seuil_haut):
            entry.delete(0, tk.END)
        self._statut(f"{ticker} mis à jour : {', '.join(changements)}.", "green")
        
    def _texte_listbox(self, ticker):
        """Construit la ligne texte affichée dans la liste pour un ticker."""
        infos = self.titres[ticker]
        return (
            f"{ticker} — {infos['quantite']} action(s) "
            f"(alerte : {infos['seuil_bas']:.2f} $ / {infos['seuil_haut']:.2f} $)"
        )
    def _rafraichir_ligne_listbox(self, index, ticker):
            """Remplace la ligne `index` par sa version à jour et la garde sélectionnée."""
            self.listbox_titres.delete(index)
            self.listbox_titres.insert(index, self._texte_listbox(ticker))
            self.listbox_titres.selection_set(index)
    
    def _ticker_selectionne(self):
        """Retourne (index, ticker) du titre sélectionné dans la liste, ou None.
        Le ticker est extrait du texte affiché (avant le tiret "—")."""
        selection = self.listbox_titres.curselection()
        if not selection:
            return None
        texte = self.listbox_titres.get(selection[0])
        return selection[0], texte.split(" — ")[0]
    
    def _statut(self, texte, couleur):
            """Affiche un message de statut (succès/erreur/info) sous le formulaire de gestion."""
            self.label_statut_titres.config(text=texte, fg=couleur)
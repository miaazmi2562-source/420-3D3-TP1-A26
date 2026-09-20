# Portfolio Tracker : suit en temps réel (toutes les INTERVALLE_MS) le prix
# de titres boursiers via yfinance, affiche la valeur du portefeuille, déclenche
# des alertes de seuil et journalise chaque cycle dans portfolio.csv.

import tkinter as tk
import yfinance as yf
from datetime import datetime


# Portefeuille initial : quantité détenue + seuils d'alerte par ticker.
# Modifié en place par l'UI (ajout/retrait/modification de titres).
TITRES = {
    "AAPL":  {"quantite": 10, "seuil_haut": 200.0, "seuil_bas": 150.0},
    "GOOGL": {"quantite": 5,  "seuil_haut": 160.0, "seuil_bas": 120.0},
    "MSFT":  {"quantite": 8,  "seuil_haut": 430.0, "seuil_bas": 380.0},
}

INTERVALLE_MS = 30000  # Fréquence de rafraîchissement des prix (30 secondes)

# Polices utilisées dans toute l'interface, centralisées ici pour rester cohérentes
POLICE = ("Segoe UI", 10)
POLICE_TITRE = ("Segoe UI", 16, "bold")
POLICE_VALEUR = ("Segoe UI", 13, "bold")

## --- Fonctions utilitaires --- ##
# Fonctions indépendantes de l'UI : accès réseau (yfinance), formatage et
# validation. Regroupées ici pour être réutilisées à la fois par l'ajout de
# titres et le cycle de rafraîchissement, sans dupliquer la logique.

def recuperer_prix(ticker):
    """Retourne (prix, ouverture) pour un ticker, ou lève une erreur s'il est introuvable."""
    info = yf.Ticker(ticker).fast_info
    prix = info["last_price"]
    if prix is None:
        raise ValueError(f"Le titre '{ticker}' n'existe pas.")
    return prix, info["open"]


def formater_prix(prix, ouverture):
    """Retourne le texte et la couleur à afficher pour un prix et sa variation
    par rapport à l'ouverture (vert si en hausse, rouge si en baisse)."""
    variation = (prix - ouverture) / ouverture * 100
    symbole = "▲" if variation >= 0 else "▼"
    couleur = "green" if variation >= 0 else "red"
    return f"{prix:.2f} $  {symbole} {abs(variation):.2f}%", couleur


def entier_positif(texte):
    """Convertit `texte` en entier strictement positif, ou lève ValueError."""
    valeur = int(texte)
    if valeur <= 0:
        raise ValueError
    return valeur


def flottant_positif(texte):
    """Convertit `texte` en nombre décimal strictement positif, ou lève ValueError."""
    valeur = float(texte)
    if valeur <= 0:
        raise ValueError
    return valeur


class App:
    def __init__(self):
        self.fenetre = tk.Tk()
        self.fenetre.title("Portfolio Tracker")
        self.fenetre.resizable(False, False)
        self.fenetre.option_add("*Font", POLICE)

        # labels_prix : ticker -> Label affichant "prix ▲/▼ variation%"
        # frames_prix : ticker -> Frame conteneur de cette ligne, pour pouvoir
        # la détruire proprement quand un titre est retiré
        self.labels_prix = {}
        self.frames_prix = {}

        tk.Label(self.fenetre, text="Portfolio Tracker", font=POLICE_TITRE).pack(pady=10)

        # Section "Prix en temps réel" : une ligne par titre du portefeuille
        self.frame_prix = tk.LabelFrame(self.fenetre, text="Prix en temps réel", padx=10, pady=10)
        self.frame_prix.pack(fill=tk.X, padx=10, pady=5)
        for ticker in TITRES:
            self._creer_ligne_prix(ticker)

        # Section "Gérer les titres" : ajout, retrait, modification (voir plus bas)
        self._construire_gestion()

        # Section "Mon portfolio" : valeur totale et variation depuis l'ouverture,
        # mises à jour à chaque cycle de rafraîchir()
        frame_portfolio = tk.LabelFrame(self.fenetre, text="Mon portfolio", padx=10, pady=10)
        frame_portfolio.pack(fill=tk.X, padx=10, pady=5)
        self.label_valeur = tk.Label(frame_portfolio, text="Valeur totale : calcul en cours...", font=POLICE_VALEUR)
        self.label_valeur.pack()
        self.label_variation = tk.Label(frame_portfolio, text="")
        self.label_variation.pack()

        # Section "Alertes" : liste des titres ayant franchi un seuil, ou message par défaut
        frame_alertes = tk.LabelFrame(self.fenetre, text="Alertes", padx=10, pady=10)
        frame_alertes.pack(fill=tk.X, padx=10, pady=5)
        self.label_alertes = tk.Label(
            frame_alertes, text="Aucune alerte", fg="gray", justify=tk.LEFT, wraplength=380
        )
        self.label_alertes.pack(anchor="w")

        self.label_maj = tk.Label(self.fenetre, text="", font=("Segoe UI", 9), fg="gray")
        self.label_maj.pack(pady=5)

        # Premier chargement des prix, puis boucle de rafraîchissement automatique
        # (rafraichir() se replanifie elle-même via fenetre.after)
        self.rafraichir()
        self.fenetre.mainloop()

    # ---------------------------------------------------------------- UI --

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
        for ticker in TITRES:
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

    def _texte_listbox(self, ticker):
        """Construit la ligne texte affichée dans la liste pour un ticker."""
        infos = TITRES[ticker]
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

    # ----------------------------------------------------------- actions --

    def ajouter_titre(self):
        """Valide le formulaire d'ajout, vérifie que le ticker existe via yfinance,
        puis l'insère dans TITRES et dans l'UI (ligne de prix + liste)."""
        ticker = self.entry_ticker.get().strip().upper()
        if not ticker:
            return
        if ticker in TITRES:
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

        TITRES[ticker] = {
            "quantite": quantite,
            "seuil_haut": round(seuil_haut if seuil_haut is not None else prix * 1.2, 2),
            "seuil_bas": round(seuil_bas if seuil_bas is not None else prix * 0.8, 2),
        }

        # Mise à jour de l'UI : nouvelle ligne de prix, nouvelle entrée dans la
        # liste, puis réinitialisation du formulaire d'ajout
        self._creer_ligne_prix(ticker)
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
        self.labels_prix[ticker].config(text=texte, fg=couleur)
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
        del TITRES[ticker]
        self.labels_prix.pop(ticker, None)
        self.frames_prix.pop(ticker).destroy()

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
                TITRES[ticker]["quantite"] = entier_positif(texte_qte)
                changements.append(f"{TITRES[ticker]['quantite']} action(s)")
            if texte_bas or texte_haut:
                if not (texte_bas and texte_haut):
                    self._statut("Les deux alertes doivent être fournies ensemble.", "red")
                    return
                seuil_bas, seuil_haut = flottant_positif(texte_bas), flottant_positif(texte_haut)
                if seuil_bas >= seuil_haut:
                    self._statut("L'alerte basse doit être inférieure à l'alerte haute.", "red")
                    return
                TITRES[ticker]["seuil_bas"] = round(seuil_bas, 2)
                TITRES[ticker]["seuil_haut"] = round(seuil_haut, 2)
                changements.append(f"alertes {seuil_bas:.2f} $ / {seuil_haut:.2f} $")
        except ValueError:
            self._statut("La quantité et les alertes doivent être des nombres positifs.", "red")
            return

        self._rafraichir_ligne_listbox(index, ticker)
        for entry in (self.entry_nouvelle_quantite, self.entry_nouveau_seuil_bas, self.entry_nouveau_seuil_haut):
            entry.delete(0, tk.END)
        self._statut(f"{ticker} mis à jour : {', '.join(changements)}.", "green")

    # ------------------------------------------------------------ cycle --

    def rafraichir(self):
        """Cycle principal : récupère les prix de tous les titres, met à jour
        l'affichage (prix, valeur totale, alertes), journalise dans le CSV,
        puis se replanifie elle-même dans INTERVALLE_MS millisecondes.
        Toute erreur (ex. réseau) est affichée sans interrompre le cycle."""
        try:
            # 1. Récupération des prix actuels pour tous les titres du portefeuille
            prix_actuels = {ticker: recuperer_prix(ticker) for ticker in TITRES}

            # 2. Mise à jour de l'affichage prix/variation de chaque titre
            for ticker, (prix, ouverture) in prix_actuels.items():
                texte, couleur = formater_prix(prix, ouverture)
                self.labels_prix[ticker].config(text=texte, fg=couleur)

            # 3. Valeur totale du portefeuille et variation depuis l'ouverture
            valeur_totale = sum(prix * TITRES[t]["quantite"] for t, (prix, _) in prix_actuels.items())
            valeur_ouverture = sum(ouv * TITRES[t]["quantite"] for t, (_, ouv) in prix_actuels.items())
            variation_portfolio = valeur_totale - valeur_ouverture

            self.label_valeur.config(text=f"Valeur totale : {valeur_totale:.2f} $")
            symbole = "▲" if variation_portfolio >= 0 else "▼"
            self.label_variation.config(
                text=f"{symbole} {abs(variation_portfolio):.2f} $ depuis l'ouverture",
                fg="green" if variation_portfolio >= 0 else "red",
            )

            # 4. Alertes : un titre est signalé s'il atteint ou dépasse son seuil haut,
            # ou atteint ou descend sous son seuil bas
            alertes = []
            for ticker, (prix, _) in prix_actuels.items():
                if prix >= TITRES[ticker]["seuil_haut"]:
                    alertes.append(f"⚠️ {ticker} dépasse le seuil haut ({prix:.2f} $ ≥ {TITRES[ticker]['seuil_haut']:.2f} $)")
                elif prix <= TITRES[ticker]["seuil_bas"]:
                    alertes.append(f"⚠️ {ticker} sous le seuil bas ({prix:.2f} $ ≤ {TITRES[ticker]['seuil_bas']:.2f} $)")
            self.label_alertes.config(text="\n".join(alertes) if alertes else "Aucune alerte", fg="red" if alertes else "gray")

            # 5. Journalisation : une ligne par titre est ajoutée au CSV à chaque cycle
            horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("portfolio.csv", "a") as f:
                for ticker, (prix, ouverture) in prix_actuels.items():
                    f.write(f"{horodatage},{ticker},{prix:.2f},{ouverture:.2f}\n")

            self.label_maj.config(text=f"Dernière mise à jour : {horodatage}", fg="gray")

        except Exception as e:
            self.label_maj.config(text=f"Erreur : {e}", fg="red")

        # Replanifie le prochain cycle, que celui-ci ait réussi ou échoué
        self.fenetre.after(INTERVALLE_MS, self.rafraichir)

if __name__ == "__main__":
    App()

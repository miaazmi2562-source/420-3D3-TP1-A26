# classe principal du portfolio, controle son état, d'actualiser les données
# et notifier. pas d'interface
import yfinance as yf
from modeles.sujet import Sujet

def recuperer_prix(ticker):
    """Retourne (prix, ouverture) pour un ticker, ou lève une erreur s'il est introuvable."""
    info = yf.Ticker(ticker).fast_info
    prix = info["last_price"]
    if prix is None:
        raise ValueError(f"Le titre '{ticker}' n'existe pas.")
    return prix, info["open"]

class Portefeuille(Sujet):
    def __init__(self, titres):
        super().__init__()
        self.titres = titres
        self.donnees = {
            "titres": self.titres,
            "prix": {},
            "valeur_totale": 0.0,
            "variation_portfolio": 0.0,
            "alertes": []
        }


    def get_donnees(self) -> dict:
        return self.donnees

    def rafraichir(self):
        """Cycle principal : récupère les prix de tous les titres, met à jour
        prix, valeur totale, alertes. Toute erreur (ex. réseau) est affichée sans interrompre le cycle."""
        # 1. Récupération des prix actuels pour tous les titres du portefeuille
        prix_actuels = {ticker: recuperer_prix(ticker) for ticker in self.titres}
        valeur_totale = 0.0
        valeur_ouverture = 0.0
        alertes = []

        # 2. Valeur totale du portefeuille et variation depuis l'ouverture
        for ticker, (prix, ouverture) in prix_actuels.items():
            quantite = self.titres[ticker]["quantite"]
            valeur_totale += prix * quantite
            valeur_ouverture += ouverture * quantite
            if prix >= self.titres[ticker]["seuil_haut"]:
                alertes.append(f"⚠️ {ticker} dépasse le seuil haut ({prix:.2f} $ ≥ {self.titres[ticker]['seuil_haut']:.2f} $)")
            elif prix <= self.titres[ticker]["seuil_bas"]:
                alertes.append(f"⚠️ {ticker} sous le seuil bas ({prix:.2f} $ ≤ {self.titres[ticker]['seuil_bas']:.2f} $)")

        variation_portfolio = valeur_totale - valeur_ouverture
        self.donnees = {
            "titres": self.titres,
            "prix": prix_actuels,
            "valeur_totale": valeur_totale,
            "variation_portfolio": variation_portfolio,
            "alertes": alertes
        }
        self.notifier()


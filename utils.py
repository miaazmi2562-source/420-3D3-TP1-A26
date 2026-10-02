# un ensemble de fonctions a utiliser dans les autres classes pour ne pas les reecrire a chaque fois.
import yfinance as yf

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
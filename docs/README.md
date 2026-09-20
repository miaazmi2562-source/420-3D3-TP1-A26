# TP1 — Suiveur de portefeuille boursier

## Présentation

Vous devez refactoriser une application de suivi de portefeuille boursier
en appliquant le **patron Observateur**.

L'application surveille en temps réel le prix de plusieurs titres boursiers
via l'API `yfinance` et notifie plusieurs composants à chaque mise à jour.

---

## Mise en place

```bash
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python app.py
```

---

## Fonctionnement de l'application existante

L'application surveille les titres boursiers ajoutés au portefeuille et toutes
les 30 secondes :

- Affichage du prix actuel et de la variation depuis l'ouverture pour chaque titre
- Affichage de la valeur totale du portefeuille et de sa variation
- Alertes visuelles quand un titre dépasse ou descend sous un seuil défini
- Ajout de nouveaux titres boursiers via l'interface
- Modification des quantités d'actions pour chaque titre
- Enregistrement des données dans un fichier CSV à chaque mise à jour


---

## Ce qui est fourni dans la branche `refactor`

```
portfolio/
├── main.py                  ← à compléter
├── requirements.txt
├── models/
│   └── subject.py           ← interface Sujet (complète — ne pas modifier)
└── observers/
    └── observer.py          ← interface Observateur (complète — ne pas modifier)
```

Tout le reste est à créer.

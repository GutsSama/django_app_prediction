## Présentation du projet

Application web développée avec Django permettant de prédire le montant d’une prime d’assurance
à partir des caractéristiques d’un utilisateur.

Le projet consiste à transformer un modèle de machine learning existant (régression linéaire)
en une application web complète et exploitable, intégrant un système d’authentification,
la gestion du profil utilisateur et une fonctionnalité de prédiction personnalisée.

Réalisé en équipe sur 10 jours, ce projet nous a permis de développer une application Django complète tout en appliquant de bonnes pratiques de structuration, de sécurité et de tests.

## Fonctionnalités

- Création de compte et authentification des utilisateurs (inscription, connexion, déconnexion)
- Gestion du profil utilisateur avec modification des informations liées à l’assurance
- Accès sécurisé aux pages réservées aux utilisateurs connectés
- Prédiction personnalisée de la prime d’assurance à partir des données utilisateur
- Système de prise de rendez-vous avec un conseiller
- Validation des formulaires et gestion des erreurs
- Mise en place de tests automatisés via le framework de tests Django (tests unitaires et fonctionnels)

## Technologies utilisées

### Back-end
- Python
- Django
- SQLite

### Front-end
- HTML / CSS
- Tailwind CSS
- JavaScript (interactions simples)

### Machine Learning
- Modèle de prédiction chargé via joblib

### Tests
- Framework de tests intégré à Django (tests unitaires et fonctionnels)

## Prérequis

- Python 3.10 ou supérieur
- pip
- virtualenv ou venv
- Node.js et npm (pour la gestion de Tailwind CSS)

## Cloner le dépôt
```bash
git clone git@github.com:GutsSama/django_app_prediction.git
cd django_app_prediction
```
## Créer et activer l'environnement virtuel
```bash
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
.venv\Scripts\activate     # Windows (PowerShell)
```

## Installer les dépendances
```bash
pip install -r requirements.txt
```

## Appliquer les migrations
```bash
python manage.py migrate
```

## Créer un superuser
```bash
python manage.py createsuperuser
```

## Lancer le serveur
```bash
python manage.py runserver
```

## Lancer les tests
```bash
python manage.py test
```

## Accès à l’application (en local)
http://127.0.0.1:8000/
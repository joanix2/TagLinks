# Utiliser une image Python officielle comme base
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt /app/requirements.txt

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tous les fichiers du répertoire courant dans le conteneur
COPY . /app

# Exposer le port utilisé par l'application Flask (5000 par défaut)
EXPOSE 5000

# Définir la commande pour lancer l'application
CMD ["python", "app.py"]

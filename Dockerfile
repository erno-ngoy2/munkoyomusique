FROM python:3.10-slim

# Installer les dépendances système, notamment ffmpeg pour l'audio
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier et installer les requirements Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Exposer le port de FastAPI
EXPOSE 7860FROM python:3.10-slim

# Installation de git et ffmpeg pour le traitement audio
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]

# Lancer l'application Uvicorn sur le port attendu par Hugging Face (7860)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
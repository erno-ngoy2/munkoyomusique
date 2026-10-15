# Site de téléchargement MUNKOYO MUSIQUE (MalakiLabs)

## Installer ces fichiers
Copie le contenu de ce dossier dans la racine de ton projet du site (à côté de `app-release.apk`),
en acceptant de remplacer `main.py` et `requirements.txt`. Ensuite :  git add . && git commit && git push

Fichiers :
- `main.py`                  le site (remplace l'ancien)
- `requirements.txt`         réduit à fastapi + uvicorn (l'ancien contenait mediapipe, opencv... inutiles ici)
- `templates/store.html`     la page de type « store »
- `versions.json`            l'historique des versions
- `static/`                  logo bleu, icônes, dossier `screens/` pour de vraies captures

## À chaque nouvelle version de l'application
1. Remplace `app-release.apk` par le nouvel APK signé.
2. Ouvre `versions.json` et ajoute EN PREMIER une entrée :
   {"version": "1.2", "code": 3, "date": "2026-11-02", "statut": "actuelle", "notes": ["...", "..."]}
3. Passe l'ancienne entrée « actuelle » en "statut": "precedente".
4. Déploie. La taille, la date et l'empreinte SHA-256 se mettent à jour toutes seules.

## Nouveau nom de domaine (munkoyomusique.online)
Définis la variable d'environnement SITE_URL = https://munkoyomusique.online
(elle sert aux liens de partage). Pense aussi à changer MiseAJour.URL_SITE dans l'application
pour que l'alerte de mise à jour renvoie vers la nouvelle adresse.

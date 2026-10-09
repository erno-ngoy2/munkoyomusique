import os
import tempfile
import yt_dlp


def obtenir_options_ytdl(dossier_destination: str = "downloads") -> dict:
    """
    Génère le dictionnaire d'options de yt-dlp optimisé pour éviter le blocage 'Sign in to confirm you're not a bot'.
    """
    options = {
        'format': 'ba/bestaudio/m4a/best',
        'outtmpl': os.path.join(dossier_destination, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': False,
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) '
                'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
            ),
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'android', 'ios'],
                'skip': ['webpage', 'configs'],
            }
        },
    }

    # Injection des cookies depuis la variable d'environnement Render (YOUTUBE_COOKIES)
    cookies_content = os.getenv('YOUTUBE_COOKIES')
    if cookies_content:
        # Nettoyage préalable des espaces superflus
        cookies_content = cookies_content.strip()
        temp_cookie_file = tempfile.NamedTemporaryFile(
            delete=False, mode='w', encoding='utf-8', suffix='.txt'
        )
        temp_cookie_file.write(cookies_content)
        temp_cookie_file.close()
        options['cookiefile'] = temp_cookie_file.name

    return options


def nettoyer_fichier_cookie(ydl_opts: dict):
    """
    Supprime le fichier temporaire de cookies après l'opération.
    """
    cookie_path = ydl_opts.get('cookiefile')
    if cookie_path and os.path.exists(cookie_path):
        try:
            os.remove(cookie_path)
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier cookie : {e}")


def rechercher_videos_youtube(recherche: str, max_resultats: int = 5) -> list:
    """
    Recherche des vidéos sur YouTube et retourne une liste de résultats.
    """
    query = recherche.strip()
    if not (query.startswith("http://") or query.startswith("https://")):
        query = f"ytsearch{max_resultats}:{query}"

    ydl_opts = obtenir_options_ytdl()
    ydl_opts.update({
        'extract_flat': 'in_playlist',
    })

    resultats = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)

            entries = info.get('entries', [info]) if 'entries' in info else [info]
            for entry in entries:
                if not entry:
                    continue

                duration_sec = entry.get('duration')
                if duration_sec:
                    minutes, secondes = divmod(int(duration_sec), 60)
                    duree_formatee = f"{minutes}:{secondes:02d}"
                else:
                    duree_formatee = "Inconnue"

                thumbnails = entry.get('thumbnails', [])
                thumbnail_url = thumbnails[0]['url'] if thumbnails else ""

                resultats.append({
                    "id": entry.get('id'),
                    "title": entry.get('title'),
                    "uploader": entry.get('uploader') or entry.get('channel', 'Artiste inconnu'),
                    "duration": duree_formatee,
                    "url": entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                    "thumbnail": thumbnail_url
                })
    finally:
        nettoyer_fichier_cookie(ydl_opts)

    return resultats


def telecharger_audio_par_url(url_video: str, dossier_destination: str = "downloads") -> dict:
    """
    Télécharge le flux audio de la vidéo sélectionnée.
    """
    if not os.path.exists(dossier_destination):
        os.makedirs(dossier_destination, exist_ok=True)

    ydl_opts = obtenir_options_ytdl(dossier_destination=dossier_destination)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_video, download=True)
            filename = ydl.prepare_filename(info)

        return {
            "status": "success",
            "title": info.get("title", "audio_youtube"),
            "duration": info.get("duration"),
            "file_path": os.path.abspath(filename),
            "filename": os.path.basename(filename)
        }
    finally:
        nettoyer_fichier_cookie(ydl_opts)


if __name__ == "__main__":
    saisie = input("Entrez un titre de chanson ou une URL YouTube : ").strip()
    if saisie:
        if saisie.startswith("http://") or saisie.startswith("https://"):
            res = telecharger_audio_par_url(saisie)
            print(res)
        else:
            resultats = rechercher_videos_youtube(saisie)
            print(f"Trouvé {len(resultats)} résultats :")
            for idx, r in enumerate(resultats, start=1):
                print(f"{idx}. {r['title']} ({r['duration']}) - {r['uploader']}")
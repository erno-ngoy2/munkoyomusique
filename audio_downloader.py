import os
import shutil
import tempfile

import yt_dlp


def obtenir_options_ytdl(dossier_destination: str = "downloads") -> dict:
    """
    Génère le dictionnaire d'options de yt-dlp.

    Variables d'environnement (toutes optionnelles) :
      - YOUTUBE_COOKIES : contenu d'un fichier cookies.txt (format Netscape)
      - PROXY_URL       : proxy à utiliser, ex. http://user:pass@host:port
      - DEBUG_YTDLP     : mettre 1 pour activer les logs détaillés
    """
    debug = bool(os.getenv("DEBUG_YTDLP"))

    options = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(dossier_destination, "%(title)s.%(ext)s"),
        "quiet": not debug,
        "no_warnings": not debug,
        "verbose": debug,
        "ignoreerrors": False,
        "noplaylist": True,
        # IMPORTANT : on ne force PAS 'player_client'.
        # Les clients android/ios ignorent les cookies, ce qui provoquait
        # "Failed to extract any player response" quand YOUTUBE_COOKIES était défini.
    }

    # Runtime JavaScript : yt-dlp utilise Deno par défaut, sinon on active Node.
    if not shutil.which("deno") and shutil.which("node"):
        options["js_runtimes"] = {"node": {}}

    # Proxy optionnel (utile si l'IP de Render est bloquée par YouTube).
    proxy = os.getenv("PROXY_URL")
    if proxy:
        options["proxy"] = proxy

    # Injection des cookies via un fichier temporaire.
    cookies_content = os.getenv("YOUTUBE_COOKIES")
    if cookies_content:
        temp_cookie_file = tempfile.NamedTemporaryFile(
            delete=False, mode="w", encoding="utf-8", suffix=".txt"
        )
        temp_cookie_file.write(cookies_content)
        temp_cookie_file.close()
        options["cookiefile"] = temp_cookie_file.name

    return options


def nettoyer_fichier_cookie(ydl_opts: dict):
    """Supprime le fichier temporaire de cookies s'il a été généré."""
    cookie_path = ydl_opts.get("cookiefile")
    if cookie_path and os.path.exists(cookie_path):
        try:
            os.remove(cookie_path)
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier cookie temporaire : {e}")


def rechercher_videos_youtube(recherche: str, max_resultats: int = 5) -> list:
    """Recherche des vidéos sur YouTube et retourne une liste de résultats."""
    query = recherche.strip()
    if not (query.startswith("http://") or query.startswith("https://")):
        query = f"ytsearch{max_resultats}:{query}"

    ydl_opts = obtenir_options_ytdl()
    ydl_opts.update({
        "extract_flat": "in_playlist",  # Extraction rapide des métadonnées
    })

    resultats = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)

            entries = info.get("entries", [info]) if "entries" in info else [info]
            for entry in entries:
                if not entry:
                    continue

                # Formatage de la durée (mm:ss)
                duration_sec = entry.get("duration")
                if duration_sec:
                    minutes, secondes = divmod(int(duration_sec), 60)
                    duree_formatee = f"{minutes}:{secondes:02d}"
                else:
                    duree_formatee = "Inconnue"

                # Miniature : dernière de la liste = généralement la meilleure qualité
                thumbnails = entry.get("thumbnails") or []
                thumbnail_url = thumbnails[-1]["url"] if thumbnails else ""

                resultats.append({
                    "id": entry.get("id"),
                    "title": entry.get("title"),
                    "uploader": entry.get("uploader") or entry.get("channel") or "Artiste inconnu",
                    "duration": duree_formatee,
                    "url": entry.get("webpage_url")
                    or f"https://www.youtube.com/watch?v={entry.get('id')}",
                    "thumbnail": thumbnail_url,
                })
    finally:
        nettoyer_fichier_cookie(ydl_opts)

    return resultats


def telecharger_audio_par_url(url_video: str, dossier_destination: str = "downloads") -> dict:
    """Télécharge le flux audio de la vidéo sélectionnée."""
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
            "filename": os.path.basename(filename),
        }
    finally:
        nettoyer_fichier_cookie(ydl_opts)


def diagnostic_environnement() -> dict:
    """
    Retourne l'état de l'environnement (version yt-dlp, Deno/Node, cookies, proxy).
    À exposer temporairement via une route /debug pour diagnostiquer Render.
    """
    return {
        "yt_dlp": yt_dlp.version.__version__,
        "deno": shutil.which("deno"),
        "node": shutil.which("node"),
        "ffmpeg": shutil.which("ffmpeg"),
        "has_cookies": bool(os.getenv("YOUTUBE_COOKIES")),
        "has_proxy": bool(os.getenv("PROXY_URL")),
    }


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
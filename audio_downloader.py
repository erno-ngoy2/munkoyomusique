import os
import yt_dlp


def rechercher_videos_youtube(recherche: str, max_resultats: int = 5) -> list:
    """
    Recherche des vidéos sur YouTube et retourne une liste de résultats détaillés.
    """
    query = recherche.strip()
    if not (query.startswith("http://") or query.startswith("https://")):
        query = f"ytsearch{max_resultats}:{query}"

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',  # Extraction rapide des métadonnées
    }

    resultats = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)

        entries = info.get('entries', [info]) if 'entries' in info else [info]
        for entry in entries:
            if not entry:
                continue

            # Formatage de la durée (mm:ss)
            duration_sec = entry.get('duration')
            if duration_sec:
                minutes, secondes = divmod(int(duration_sec), 60)
                duree_formatee = f"{minutes}:{secondes:02d}"
            else:
                duree_formatee = "Inconnue"

            # Récupération de la miniature
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

    return resultats


def telecharger_audio_par_url(url_video: str, dossier_destination: str = "downloads") -> dict:
    """
    Télécharge le flux audio de la vidéo sélectionnée par l'utilisateur.
    """
    if not os.path.exists(dossier_destination):
        os.makedirs(dossier_destination, exist_ok=True)

    ydl_opts = {
        'format': 'ba/bestaudio',
        'outtmpl': os.path.join(dossier_destination, '%(title)s.%(ext)s'),
        'js_runtimes': {
            'node': {},
            'deno': {},
            'quickjs': {}
        },
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': False,
    }

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
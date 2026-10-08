import os
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

from audio_downloader import rechercher_videos_youtube, telecharger_audio_par_url

app = FastAPI(
    title="YouTube Audio Search & Downloader",
    description="API FastAPI et interface web pour rechercher et télécharger de l'audio YouTube",
    version="2.0.0"
)

# Dossier où sont enregistrés les fichiers audio
DOSSIER_DOWNLOADS = "downloads"


@app.get("/", response_class=HTMLResponse)
def index():
    """
    Affiche la page Web responsive permettant la recherche et le choix de la chanson.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MUNKOYO MUSIQUE</title>
        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }
            body {
                background-color: #f4f6f9;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 20px;
            }
            .card {
                background: #ffffff;
                width: 100%;
                max-width: 580px;
                padding: 28px 20px;
                border-radius: 16px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            }
            h1 {
                font-size: 1.5rem;
                color: #1a1a1a;
                text-align: center;
                margin-bottom: 6px;
            }
            p.subtitle {
                font-size: 0.88rem;
                color: #666;
                text-align: center;
                margin-bottom: 20px;
            }
            .search-box {
                display: flex;
                gap: 8px;
                margin-bottom: 20px;
            }
            input[type="text"] {
                flex: 1;
                padding: 12px 14px;
                font-size: 0.95rem;
                border: 2px solid #e1e5ee;
                border-radius: 10px;
                outline: none;
                transition: border-color 0.2s;
            }
            input[type="text"]:focus {
                border-color: #ff0000;
            }
            button.btn-search {
                padding: 12px 18px;
                font-size: 0.95rem;
                font-weight: 600;
                color: #ffffff;
                background-color: #ff0000;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            button.btn-search:hover {
                background-color: #cc0000;
            }
            button:disabled {
                background-color: #cccccc !important;
                cursor: not-allowed;
            }
            #status {
                margin-bottom: 16px;
                padding: 12px;
                border-radius: 8px;
                font-size: 0.88rem;
                text-align: center;
                display: none;
            }
            .info { background-color: #e3f2fd; color: #0d47a1; }
            .success { background-color: #e8f5e9; color: #1b5e20; }
            .error { background-color: #ffebee; color: #b71c1c; }

            /* Liste des résultats */
            .results-list {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            .result-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 10px;
                border: 1px solid #eef0f5;
                border-radius: 10px;
                background: #fafbfc;
            }
            .result-item img {
                width: 70px;
                height: 52px;
                object-fit: cover;
                border-radius: 6px;
                background-color: #ccc;
            }
            .result-info {
                flex: 1;
                min-width: 0;
            }
            .result-title {
                font-size: 0.88rem;
                font-weight: 600;
                color: #222;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .result-meta {
                font-size: 0.78rem;
                color: #777;
                margin-top: 3px;
            }
            .btn-download {
                padding: 8px 12px;
                font-size: 0.8rem;
                font-weight: 600;
                color: #ff0000;
                background-color: #ffe5e5;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s;
                white-space: nowrap;
            }
            .btn-download:hover {
                background-color: #ff0000;
                color: #ffffff;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>MUNKOYO MUSIQUE</h1>
            <p class="subtitle">Recherchez un titre ou collez un lien YouTube</p>

            <form id="searchForm" class="search-box">
                <input type="text" id="query" placeholder="Nom de chanson, artiste ou URL..." required>
                <button type="submit" class="btn-search" id="btnSearch">Rechercher</button>
            </form>

            <div id="status"></div>
            <div id="results" class="results-list"></div>
        </div>

        <script>
            const searchForm = document.getElementById('searchForm');
            const queryInput = document.getElementById('query');
            const statusDiv = document.getElementById('status');
            const resultsDiv = document.getElementById('results');
            const btnSearch = document.getElementById('btnSearch');

            // 1. Recherche des morceaux
            searchForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const query = queryInput.value.trim();
                if (!query) return;

                statusDiv.style.display = 'block';
                statusDiv.className = 'info';
                statusDiv.innerText = "Recherche des vidéos en cours...";
                resultsDiv.innerHTML = '';
                btnSearch.disabled = true;

                try {
                    const formData = new FormData();
                    formData.append('query', query);

                    const response = await fetch('/api/search', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        const err = await response.json();
                        throw new Error(err.detail || 'Erreur de recherche');
                    }

                    const data = await response.json();
                    statusDiv.style.display = 'none';

                    if (data.results.length === 0) {
                        statusDiv.style.display = 'block';
                        statusDiv.className = 'error';
                        statusDiv.innerText = "Aucun résultat trouvé.";
                        return;
                    }

                    // Afficher les résultats sous forme de cartes
                    data.results.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'result-item';
                        div.innerHTML = `
                            <img src="${item.thumbnail}" alt="Vignette" onerror="this.style.display='none'">
                            <div class="result-info">
                                <div class="result-title" title="${item.title}">${item.title}</div>
                                <div class="result-meta">${item.uploader} •  ${item.duration}</div>
                            </div>
                            <button class="btn-download" onclick="downloadAudio('${item.url}', this)">
                                 Télécharger
                            </button>
                        `;
                        resultsDiv.appendChild(div);
                    });

                } catch (err) {
                    statusDiv.style.display = 'block';
                    statusDiv.className = 'error';
                    statusDiv.innerText = "Erreur : " + err.message;
                } finally {
                    btnSearch.disabled = false;
                }
            });

            // 2. Téléchargement du résultat spécifique sélectionné
            async function downloadAudio(url, buttonEl) {
                const originalText = buttonEl.innerText;
                buttonEl.innerText = " Extraction...";
                buttonEl.disabled = true;

                statusDiv.style.display = 'block';
                statusDiv.className = 'info';
                statusDiv.innerText = "Téléchargement et extraction de l'audio en cours...";

                try {
                    const formData = new FormData();
                    formData.append('url', url);

                    const response = await fetch('/api/download', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        const err = await response.json();
                        throw new Error(err.detail || 'Erreur lors du téléchargement');
                    }

                    const blob = await response.blob();
                    const downloadUrl = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');

                    const contentDisposition = response.headers.get('Content-Disposition');
                    let filename = 'audio.m4a';
                    if (contentDisposition && contentDisposition.includes('filename=')) {
                        filename = contentDisposition.split('filename=')[1].replace(/"/g, '');
                    }

                    a.href = downloadUrl;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();

                    statusDiv.className = 'success';
                    statusDiv.innerText = "Téléchargement réussi !";
                } catch (err) {
                    statusDiv.className = 'error';
                    statusDiv.innerText = "Erreur : " + err.message;
                } finally {
                    buttonEl.innerText = originalText;
                    buttonEl.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/api/search")
def search_endpoint(query: str = Form(...)):
    """
    Endpoint qui recherche les vidéos YouTube et retourne une liste de 5 choix.
    """
    try:
        results = rechercher_videos_youtube(recherche=query, max_resultats=5)
        return JSONResponse(content={"results": results})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/download")
def download_audio_endpoint(url: str = Form(...)):
    """
    Endpoint qui effectue le téléchargement direct de l'URL sélectionnée.
    """
    try:
        resultat = telecharger_audio_par_url(url_video=url, dossier_destination=DOSSIER_DOWNLOADS)
        fichier_chemin = resultat.get("file_path")
        fichier_nom = resultat.get("filename")

        if not fichier_chemin or not os.path.exists(fichier_chemin):
            raise HTTPException(status_code=500, detail="Fichier introuvable après traitement.")

        return FileResponse(
            path=fichier_chemin,
            media_type="audio/mp4",
            filename=fichier_nom
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
import os
from fastapi import FastAPI, HTTPException, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

from audio_downloader import rechercher_videos_youtube, telecharger_audio_par_url

app = FastAPI(
    title="MUNKOYO MUSIQUE",
    description="API FastAPI et interface web pour rechercher et télécharger de l'audio YouTube",
    version="2.3.0"
)

DOSSIER_DOWNLOADS = "downloads"


def supprimer_fichier_temporaire(chemin_fichier: str):
    """Supprime le fichier du serveur une fois qu'il a été envoyé au client."""
    try:
        if os.path.exists(chemin_fichier):
            os.remove(chemin_fichier)
    except Exception as e:
        print(f"Erreur lors de la suppression du fichier temporaire : {e}")


@app.get("/manifest.json")
def get_manifest():
    return FileResponse("manifest.json", media_type="application/manifest+json")


@app.get("/sw.js")
def get_sw():
    return FileResponse("sw.js", media_type="application/javascript")


@app.get("/", response_class=HTMLResponse)
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
        <title>MUNKOYO MUSIQUE</title>

        <!-- PWA Meta Tags -->
        <link rel="manifest" href="/manifest.json">
        <meta name="theme-color" content="#BD2D9C">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <link rel="apple-touch-icon" href="/192.png">
        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                -webkit-tap-highlight-color: transparent;
            }
            body {
                background-color: #8438E3;
                display: flex;
                justify-content: center;
                align-items: flex-start;
                min-height: 100vh;
                padding: 16px 12px;
                padding-top: max(16px, env(safe-area-inset-top));
                padding-bottom: max(16px, env(safe-area-inset-bottom));
            }
            .card {
                background: #ffffff;
                width: 100%;
                max-width: 580px;
                padding: 20px 16px;
                border-radius: 16px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            }
            h1 {
                font-size: 1.35rem;
                color: #1a1a1a;
                text-align: center;
                margin-bottom: 6px;
            }
            p.subtitle {
                font-size: 0.85rem;
                color: #666;
                text-align: center;
                margin-bottom: 18px;
            }
            .search-box {
                display: flex;
                flex-direction: column;
                gap: 10px;
                margin-bottom: 20px;
            }
            input[type="text"] {
                width: 100%;
                height: 46px;
                padding: 0 14px;
                font-size: 1rem;
                border: 2px solid #e1e5ee;
                border-radius: 10px;
                outline: none;
                transition: border-color 0.2s;
            }
            input[type="text"]:focus {
                border-color: #BD2D9C;
            }
            button.btn-search {
                width: 100%;
                height: 46px;
                font-size: 0.95rem;
                font-weight: 600;
                color: #ffffff;
                background-color: #BD2D9C;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                transition: background-color 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
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
                font-size: 0.85rem;
                text-align: center;
                display: none;
            }
            .info { background-color: #e3f2fd; color: #0d47a1; }
            .success { background-color: #e8f5e9; color: #1b5e20; }
            .error { background-color: #ffebee; color: #b71c1c; }

            .results-list {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .result-item {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px;
                border: 1px solid #eef0f5;
                border-radius: 10px;
                background: #fafbfc;
            }
            .result-item img {
                width: 60px;
                height: 45px;
                object-fit: cover;
                border-radius: 6px;
                background-color: #ccc;
                flex-shrink: 0;
            }
            .result-info {
                flex: 1;
                min-width: 0;
            }
            .result-title {
                font-size: 0.85rem;
                font-weight: 600;
                color: #222;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .result-meta {
                font-size: 0.75rem;
                color: #777;
                margin-top: 3px;
            }
            .btn-download {
                height: 38px;
                padding: 0 12px;
                font-size: 0.78rem;
                font-weight: 600;
                color: #BD2D9C;
                background-color: #ffe5e5;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s;
                white-space: nowrap;
                flex-shrink: 0;
            }
            .btn-download:hover {
                background-color: #BD2D9C;
                color: #ffffff;
            }

            /* --- STYLES DU POPUP D'INSTALLATION PWA --- */
            .pwa-modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(0, 0, 0, 0.55);
                backdrop-filter: blur(4px);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                padding: 16px;
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
            }
            .pwa-modal-overlay.active {
                opacity: 1;
                visibility: visible;
            }
            .pwa-modal {
                background: #ffffff;
                width: 100%;
                max-width: 400px;
                border-radius: 20px;
                padding: 24px 20px;
                text-align: center;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
                transform: translateY(20px);
                transition: transform 0.3s ease;
            }
            .pwa-modal-overlay.active .pwa-modal {
                transform: translateY(0);
            }
            .pwa-icon {
                width: 64px;
                height: 64px;
                border-radius: 16px;
                margin-bottom: 12px;
            }
            .pwa-title {
                font-size: 1.15rem;
                font-weight: 700;
                color: #1a1a1a;
                margin-bottom: 6px;
            }
            .pwa-desc {
                font-size: 0.85rem;
                color: #666;
                margin-bottom: 20px;
                line-height: 1.4;
            }
            .pwa-actions {
                display: flex;
                gap: 10px;
            }
            .btn-pwa-install {
                flex: 1;
                height: 44px;
                background: #BD2D9C;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 0.9rem;
                cursor: pointer;
            }
            .btn-pwa-close {
                flex: 1;
                height: 44px;
                background: #f1f3f7;
                color: #555;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 0.9rem;
                cursor: pointer;
            }

            @media (min-width: 480px) {
                body {
                    align-items: center;
                    padding: 20px;
                }
                .card {
                    padding: 28px 20px;
                }
                h1 {
                    font-size: 1.5rem;
                }
                p.subtitle {
                    font-size: 0.88rem;
                    margin-bottom: 20px;
                }
                .search-box {
                    flex-direction: row;
                    gap: 8px;
                }
                button.btn-search {
                    width: auto;
                    padding: 0 18px;
                }
                .result-item img {
                    width: 70px;
                    height: 52px;
                }
                .result-title {
                    font-size: 0.88rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>MUNKOYO MUSIQUE</h1>
            <p class="subtitle">Recherchez un titre ou collez un lien YouTube</p>

            <form id="searchForm" class="search-box">
                <input type="text" id="query" placeholder="Nom de chanson, artiste ou URL..." required autocomplete="off">
                <button type="submit" class="btn-search" id="btnSearch">Rechercher</button>
            </form>

            <div id="status"></div>
            <div id="results" class="results-list"></div>
        </div>

        <!-- POPUP D'INSTALLATION PWA -->
        <div class="pwa-modal-overlay" id="pwaOverlay">
            <div class="pwa-modal">
                <img src="/192.png" alt="Icone Munkoyo" class="pwa-icon">                <div class="pwa-title">Installer MUNKOYO MUSIQUE</div>
                <div class="pwa-desc">Installez l'application sur votre écran d'accueil pour un accès rapide et sans publicité.</div>
                <div class="pwa-actions">
                    <button class="btn-pwa-close" id="pwaCloseBtn">Plus tard</button>
                    <button class="btn-pwa-install" id="pwaInstallBtn">Installer</button>
                </div>
            </div>
        </div>

        <script>
            const searchForm = document.getElementById('searchForm');
            const queryInput = document.getElementById('query');
            const statusDiv = document.getElementById('status');
            const resultsDiv = document.getElementById('results');
            const btnSearch = document.getElementById('btnSearch');

            // --- GESTION DU POPUP PWA ---
            let deferredPrompt;
            const pwaOverlay = document.getElementById('pwaOverlay');
            const pwaInstallBtn = document.getElementById('pwaInstallBtn');
            const pwaCloseBtn = document.getElementById('pwaCloseBtn');

            window.addEventListener('beforeinstallprompt', (e) => {
                // Empêche la bannière par défaut du navigateur
                e.preventDefault();
                deferredPrompt = e;
                // Affiche notre popup personnalisé
                pwaOverlay.classList.add('active');
            });

            pwaInstallBtn.addEventListener('click', async () => {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    const { outcome } = await deferredPrompt.userChoice;
                    console.log(`Choix utilisateur : ${outcome}`);
                    deferredPrompt = null;
                }
                pwaOverlay.classList.remove('active');
            });

            pwaCloseBtn.addEventListener('click', () => {
                pwaOverlay.classList.remove('active');
            });

            // Enregistrement du Service Worker
            if ('serviceWorker' in navigator) {
                window.addEventListener('load', () => {
                    navigator.serviceWorker.register('/sw.js')
                        .then(reg => console.log('PWA Service Worker actif !', reg))
                        .catch(err => console.log('Erreur SW PWA:', err));
                });
            }

            // --- RECHERCHE ET TÉLÉCHARGEMENT ---
            searchForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const query = queryInput.value.trim();
                if (!query) return;

                queryInput.blur();

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

                    if (!data.results || data.results.length === 0) {
                        statusDiv.style.display = 'block';
                        statusDiv.className = 'error';
                        statusDiv.innerText = "Aucun résultat trouvé.";
                        return;
                    }

                    data.results.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'result-item';
                        div.innerHTML = `
                            <img src="${item.thumbnail}" alt="Vignette" onerror="this.style.display='none'">
                            <div class="result-info">
                                <div class="result-title" title="${item.title}">${item.title}</div>
                                <div class="result-meta">${item.uploader} • ${item.duration}</div>
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

                    if (contentDisposition) {
                        const filenameStarMatch = contentDisposition.match(/filename\*=utf-8''([^;]+)/i);
                        if (filenameStarMatch && filenameStarMatch[1]) {
                            filename = decodeURIComponent(filenameStarMatch[1]);
                        } else {
                            const filenameMatch = contentDisposition.match(/filename="?([^";]+)"?/i);
                            if (filenameMatch && filenameMatch[1]) {
                                filename = filenameMatch[1];
                            }
                        }
                    }

                    a.href = downloadUrl;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();

                    setTimeout(() => {
                        a.remove();
                        window.URL.revokeObjectURL(downloadUrl);
                    }, 100);

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
    try:
        results = rechercher_videos_youtube(recherche=query, max_resultats=5)
        return JSONResponse(content={"results": results})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/192.png")
def get_icon_192():
    return FileResponse("192.png", media_type="image/png")

@app.get("/512.png")
def get_icon_512():
    return FileResponse("512.png", media_type="image/png")

@app.post("/api/download")
def download_audio_endpoint(background_tasks: BackgroundTasks, url: str = Form(...)):
    try:
        os.makedirs(DOSSIER_DOWNLOADS, exist_ok=True)

        resultat = telecharger_audio_par_url(url_video=url, dossier_destination=DOSSIER_DOWNLOADS)
        fichier_chemin = resultat.get("file_path")
        fichier_nom = resultat.get("filename")

        if not fichier_chemin or not os.path.exists(fichier_chemin):
            raise HTTPException(status_code=500, detail="Fichier introuvable après traitement.")

        background_tasks.add_task(supprimer_fichier_temporaire, fichier_chemin)

        return FileResponse(
            path=fichier_chemin,
            filename=fichier_nom,
            media_type="audio/mp4",
            headers={
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
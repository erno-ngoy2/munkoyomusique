import os
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

app = FastAPI(
    title="MUNKOYO MUSIQUE",
    description="Téléchargement de musique gratuite & Application Android",
    version="3.0.0"
)

COUNTER_FILE = "downloads_count.json"
APK_PATH = "app-release.apk"  # Assurez-vous d'avoir votre APK à la racine


def get_count() -> int:
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, "r") as f:
                data = json.load(f)
                return data.get("count", 0)
        except Exception:
            return 0
    return 0


def increment_count() -> int:
    current = get_count() + 1
    with open(COUNTER_FILE, "w") as f:
        json.dump({"count": current}, f)
    return current


@app.get("/", response_class=HTMLResponse)
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MUNKOYO MUSIQUE — Free Music & APK Archive</title>
        <style>
            :root {
                --bg-color: #0b0b0b;
                --panel-color: #141414;
                --border-color: #262626;
                --text-primary: #ededed;
                --text-muted: #888888;
                --accent: #ff334b;
                --accent-hover: #ff1a35;
            }

            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: Courier, monospace, sans-serif;
            }

            body {
                background-color: var(--bg-color);
                color: var(--text-primary);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                padding: 24px;
            }

            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 16px;
                max-width: 900px;
                margin: 0 auto;
                width: 100%;
            }

            .logo {
                font-size: 1.1rem;
                font-weight: bold;
                letter-spacing: 2px;
                color: var(--text-primary);
                text-decoration: none;
            }

            .logo span {
                color: var(--accent);
            }

            .status-badge {
                font-size: 0.75rem;
                background: var(--border-color);
                padding: 4px 8px;
                color: var(--text-muted);
                border-radius: 2px;
            }

            main {
                max-width: 900px;
                margin: 40px auto;
                width: 100%;
                display: grid;
                grid-template-columns: 1fr 320px;
                gap: 40px;
                align-items: start;
            }

            @media (max-width: 768px) {
                main {
                    grid-template-columns: 1fr;
                    gap: 30px;
                }
            }

            .content-left h1 {
                font-size: 2.2rem;
                line-height: 1.1;
                margin-bottom: 16px;
                font-weight: 900;
                letter-spacing: -1px;
            }

            .content-left h1 span {
                color: var(--accent);
            }

            .content-left p {
                color: var(--text-muted);
                font-size: 0.95rem;
                line-height: 1.5;
                margin-bottom: 24px;
            }

            .terminal-box {
                background: var(--panel-color);
                border: 1px solid var(--border-color);
                padding: 16px;
                font-size: 0.85rem;
                color: var(--text-muted);
                margin-bottom: 24px;
            }

            .terminal-box b {
                color: var(--text-primary);
            }

            .download-panel {
                background: var(--panel-color);
                border: 1px solid var(--border-color);
                padding: 24px;
                position: relative;
            }

            .download-panel h3 {
                font-size: 1rem;
                margin-bottom: 12px;
                letter-spacing: 1px;
                text-transform: uppercase;
            }

            .btn-apk {
                display: block;
                width: 100%;
                background: var(--accent);
                color: #ffffff;
                text-align: center;
                padding: 14px;
                text-decoration: none;
                font-weight: bold;
                font-size: 0.9rem;
                letter-spacing: 1px;
                text-transform: uppercase;
                border: none;
                cursor: pointer;
                transition: background 0.15s ease;
                margin-bottom: 16px;
            }

            .btn-apk:hover {
                background: var(--accent-hover);
            }

            .meta-info {
                display: flex;
                justify-content: space-between;
                font-size: 0.8rem;
                color: var(--text-muted);
                border-top: 1px solid var(--border-color);
                padding-top: 12px;
            }

            .meta-info span#counter {
                color: var(--text-primary);
                font-weight: bold;
            }

            footer {
                max-width: 900px;
                margin: 0 auto;
                width: 100%;
                border-top: 1px solid var(--border-color);
                padding-top: 16px;
                font-size: 0.75rem;
                color: var(--text-muted);
                display: flex;
                justify-content: space-between;
            }
        </style>
    </head>
    <body>

        <header>
            <a href="#" class="logo">MUNKOYO<span>_MUSIQUE</span></a>
            <div class="status-badge">ARCHIVE // 2026.04</div>
        </header>

        <main>
            <div class="content-left">
                <h1>TÉLÉCHARGEZ VOTRE MUSIQUE <span>SANS LIMITES.</span></h1>
                <p>Munkoyo Musique est une plateforme libre d'accès dédiée au partage et au téléchargement de pistes audio gratuites. Sans inscription, sans publicité intrusive, et disponible partout.</p>

                <div class="terminal-box">
                    > init_stream: ok<br>
                    > codec: mp3 / flac direct source<br>
                    > status: <b>100% gratuit et ouvert</b>
                </div>
            </div>

            <div class="download-panel">
                <h3>Application Android</h3>
                <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 16px;">Installez le client natif directement sur votre smartphone.</p>

                <a href="/api/download" class="btn-apk" id="downloadBtn">Télécharger l'APK</a>

                <div class="meta-info">
                    <span>Total téléchargements</span>
                    <span id="counter">---</span>
                </div>
            </div>
        </main>

        <footer>
            <div>Munkoyo Musique Open Project</div>
            <div>Direct Direct Download Engine</div>
        </footer>

        <script>
            async function fetchStats() {
                try {
                    const response = await fetch('/api/stats');
                    const data = await response.json();
                    document.getElementById('counter').innerText = data.downloads;
                } catch (e) {
                    document.getElementById('counter').innerText = "N/A";
                }
            }

            fetchStats();

            document.getElementById('downloadBtn').addEventListener('click', () => {
                setTimeout(fetchStats, 1500);
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/download")
def download_apk():
    increment_count()
    if os.path.exists(APK_PATH):
        return FileResponse(
            path=APK_PATH,
            media_type="application/vnd.android.package-archive",
            filename="munkoyo_musique.apk"
        )
    else:
        return JSONResponse(status_code=404, content={"error": "APK introuvable sur le serveur."})


@app.get("/api/stats")
def get_stats():
    return {"downloads": get_count()}
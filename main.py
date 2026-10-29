"""
Site de téléchargement de MUNKOYO MUSIQUE (par MalakiLabs) — présentation de type « store ».

Fichiers utilisés :
  app-release.apk      l'APK à distribuer (à la racine, comme avant)
  versions.json        l'historique des versions (à modifier à chaque nouvelle version)
  templates/store.html la page
  static/              logo, icônes, et (facultatif) static/screens/*.png pour de vraies captures d'écran
Variable d'environnement facultative : SITE_URL (ex. https://munkoyomusique.online)
"""
import hashlib
import html
import json
import os
import threading
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

BASE = Path(__file__).resolve().parent
COUNTER_FILE = BASE / "downloads_count.json"
APK_PATH = BASE / "app-release.apk"
VERSIONS_FILE = BASE / "versions.json"
TEMPLATE = BASE / "templates" / "store.html"
SCREENS_DIR = BASE / "static" / "screens"

SITE_URL = os.environ.get("SITE_URL", "https://munkoyomusique.onrender.com").rstrip("/")
ANDROID_MIN = "7.1"
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]

app = FastAPI(
    title="MUNKOYO MUSIQUE",
    description="Application Android de MalakiLabs",
    version="4.0.0",
)
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")

_verrou = threading.Lock()


# ---------------------------------------------------------------------------
# Compteur de téléchargements
# ---------------------------------------------------------------------------
def get_count() -> int:
    try:
        with open(COUNTER_FILE, "r", encoding="utf-8") as f:
            return int(json.load(f).get("count", 0))
    except Exception:
        return 0


def increment_count() -> int:
    with _verrou:
        courant = get_count() + 1
        with open(COUNTER_FILE, "w", encoding="utf-8") as f:
            json.dump({"count": courant}, f)
        return courant


# ---------------------------------------------------------------------------
# Informations sur l'APK (taille, date, empreinte) — recalculées seulement si le fichier change
# ---------------------------------------------------------------------------
_apk = {}


def infos_apk():
    if not APK_PATH.exists():
        return None
    st = APK_PATH.stat()
    cle = (st.st_mtime_ns, st.st_size)
    with _verrou:
        if _apk.get("cle") != cle:
            h = hashlib.sha256()
            with open(APK_PATH, "rb") as f:
                for bloc in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(bloc)
            _apk.update(cle=cle, sha256=h.hexdigest(), taille=st.st_size,
                        date=datetime.fromtimestamp(st.st_mtime))
        return dict(_apk)


def lire_versions():
    try:
        with open(VERSIONS_FILE, "r", encoding="utf-8") as f:
            versions = json.load(f)
        return versions if isinstance(versions, list) else []
    except Exception:
        return []


def version_actuelle(versions):
    for v in versions:
        if v.get("statut") == "actuelle":
            return v
    return versions[0] if versions else {"version": "?", "code": 0, "notes": []}


def date_fr(texte_iso):
    try:
        d = datetime.strptime(texte_iso, "%Y-%m-%d")
        return f"{d.day} {MOIS[d.month - 1]} {d.year}"
    except Exception:
        return texte_iso or ""


def taille_fr(octets):
    return f"{octets / 1048576:.1f}".replace(".", ",") + " Mo"


esc = html.escape


# ---------------------------------------------------------------------------
# Morceaux de page générés
# ---------------------------------------------------------------------------
def html_historique(versions):
    badges = {"actuelle": ("Actuelle", "b-now"), "test": ("Version de test", "b-test")}
    blocs = []
    for v in versions:
        texte, classe = badges.get(v.get("statut"), ("Précédente", "b-old"))
        notes = "".join(f"<li>{esc(str(n))}</li>" for n in v.get("notes", []))
        blocs.append(
            '<article class="ver"><div class="ver-head">'
            f'<span class="ver-num">Version {esc(str(v.get("version", "")))}</span>'
            f'<span class="badge {classe}">{texte}</span>'
            f'<time>{esc(date_fr(v.get("date", "")))}</time></div>'
            f"<ul>{notes}</ul></article>"
        )
    return "\n".join(blocs)


def html_apercu():
    """Vraies captures si elles existent dans static/screens, sinon maquettes dessinées en CSS."""
    captures = []
    if SCREENS_DIR.exists():
        for p in sorted(SCREENS_DIR.iterdir()):
            if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
                captures.append(f'<img class="capture" src="/static/screens/{esc(p.name)}" alt="Capture d\'écran">')
    if captures:
        return "\n".join(captures)

    logo = '<img src="/static/logo.png" alt="">'
    return f"""
<div class="phone"><div class="ecran ciel">
  <div class="m-carte">{logo}
    <div class="m-champ">Nom de chanson, artiste…</div>
    <div class="m-bouton">Rechercher</div>
    <div class="m-ligne"><i></i><div><b>Suggestion pour toi</b>Artiste · 3:42</div><em>Télécharger</em></div>
    <div class="m-ligne"><i></i><div><b>Titre populaire</b>Artiste · 4:05</div><em>Télécharger</em></div>
    <div class="m-ligne"><i></i><div><b>Un autre titre</b>Artiste · 3:18</div><em>Télécharger</em></div>
  </div>
  <div class="m-nav"><span class="on"></span><span class="off"></span><span class="rond"></span></div>
</div></div>
<div class="phone"><div class="ecran nuit">
  <div class="cd"></div>
  <div class="m-titre">Ma chanson préférée</div><div class="m-sous">Artiste</div>
  <div class="m-barre"><b></b></div>
  <div class="m-ctrl"><span></span><span></span><span class="play"></span><span></span><span></span></div>
  <div class="m-nav"><span class="off"></span><span class="on"></span><span class="rond"></span></div>
</div></div>
<div class="phone"><div class="ecran nuit">
  <div class="m-notif"><div class="ligne">{logo}<b>MUNKOYO MUSIQUE</b></div><b>Ma chanson préférée</b>Artiste · lecture en cours</div>
  <div class="m-notif"><div class="ligne">{logo}<b>Téléchargement</b></div>Nouveau titre · 64 %</div>
  <div class="m-notif"><div class="ligne">{logo}<b>Annonce MalakiLabs</b></div>Une nouvelle version est disponible</div>
</div></div>"""


def rendre_page():
    versions = lire_versions()
    actuelle = version_actuelle(versions)
    infos = infos_apk()

    taille = taille_fr(infos["taille"]) if infos else "—"
    sha = infos["sha256"] if infos else "APK indisponible"
    if actuelle.get("date"):
        date_maj = date_fr(actuelle["date"])
    elif infos:
        date_maj = date_fr(infos["date"].strftime("%Y-%m-%d"))
    else:
        date_maj = "—"

    nouveautes = "".join(f"<li>{esc(str(n))}</li>" for n in actuelle.get("notes", []))
    remplacements = {
        "__SITE_URL__": SITE_URL,
        "__VERSION__": esc(str(actuelle.get("version", "?"))),
        "__CODE__": esc(str(actuelle.get("code", ""))),
        "__DATE__": esc(date_maj),
        "__TAILLE__": taille,
        "__SHA256__": sha,
        "__ANDROID_MIN__": ANDROID_MIN,
        "__TELECHARGEMENTS__": str(get_count()),
        "__NOUVEAUTES__": nouveautes,
        "__HISTORIQUE__": html_historique(versions),
        "__APERCU__": html_apercu(),
        "__ANNEE__": str(datetime.now().year),
    }
    page = TEMPLATE.read_text(encoding="utf-8")
    for cle, valeur in remplacements.items():
        page = page.replace(cle, valeur)
    # Fenêtre d'introduction (manuel + « Sauter ») affichée en popup sur le site central
    popup = POPUP.read_text(encoding="utf-8")
    popup = popup.replace("{{VERSION}}", ("v" + str(actuelle.get("version"))) if actuelle.get("version") else "-")
    popup = popup.replace("{{TAILLE}}", taille if infos else "-")
    popup = popup.replace("{{DATE}}", (infos["date"].strftime("%d/%m/%Y") if infos else "-"))
    page = page.replace("</body>", popup + "\n</body>", 1)
    return page


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
POPUP = BASE / "templates" / "popup.html"


@app.get("/", response_class=HTMLResponse)
def index():
    """Site central : la fenêtre d'introduction s'affiche en popup au premier accès."""
    return HTMLResponse(content=rendre_page())


@app.get("/store", response_class=HTMLResponse)
def store():
    return HTMLResponse(content=rendre_page())


@app.get("/api/download")
def download_apk():
    if not APK_PATH.exists():
        return JSONResponse(status_code=404, content={"error": "APK introuvable sur le serveur."})
    increment_count()
    return RedirectResponse(url="https://mmusique.onrender.com", status_code=303)


@app.get("/api/stats")
def get_stats():
    return {"downloads": get_count()}


@app.get("/api/version")
def api_version():
    """Version actuellement proposée (utile pour l'application)."""
    v = version_actuelle(lire_versions())
    infos = infos_apk()
    return {
        "version": v.get("version"),
        "code": v.get("code"),
        "sha256": infos["sha256"] if infos else None,
        "taille": infos["taille"] if infos else None,
    }


@app.get("/healthz")
def sante():
    return {"ok": True}

"""Apply the small prefix/SSO adapter to upstream webclient v3.0.0 before Vite build."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
def patch(name, old, new):
    path = root / name
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Unsupported webclient source: {name}")
    path.write_text(text.replace(old, new), encoding="utf-8")

patch("src/config.ts", "return ''", "return window.location.pathname.replace(/\\/$/, '')")
patch("src/router/index.ts", "createWebHashHistory(import.meta.env.BASE_URL)", "createWebHashHistory(window.location.pathname)")
for file in ["src/stores/events.ts", "src/stores/tracker.ts", "src/stores/player.ts"]:
    path = root / file
    text = path.read_text(encoding="utf-8")
    text = text.replace("new URL('/workers/sse-events.js', import.meta.url)", "new URL('./workers/sse-events.js', window.location.href)")
    text = text.replace('new Worker("/workers/logtrack.js")', 'new Worker(new URL("./workers/logtrack.js", window.location.href))')
    text = text.replace("new Worker('/workers/silence.js')", "new Worker(new URL('./workers/silence.js', window.location.href))")
    path.write_text(text, encoding="utf-8")
for file in (root / "public/workers").glob("*.js"):
    text = file.read_text(encoding="utf-8")
    text = text.replace(": location.origin", ": new URL('../', location.href).href.replace(/\\/$/, '')")
    file.write_text(text, encoding="utf-8")
patch("src/requests/useAxios.ts", "useModal().showLoginModal()", "if (error.response?.data?.login) window.location.assign(new URL('./auth/myaccounts/login', window.location.href).href); else useModal().showLoginModal()")
# Scope the installable app to its own directory in both standalone and suite mode.
patch("vite.config.ts", 'start_url: "/"', 'start_url: "./", scope: "./"')
patch("vite.config.ts", 'url: "/#/', 'url: "./#/')

# MyAccounts, standalone Music and Workspace

User requested swingmx/swingmusic fork, MyAccounts login, independent Music app
hosted with Workspace and ordinary shared Music folder available in FileBrowser.
Fork fahimc/swingmusic at I:/Projects/swingmusic, upstream89b9ddc7. Root upstream
preserved. WORKSPACE.md and scripts/build-workspace.ps1 describe reproducible
Windows package, standalone local auth and optional OIDC setup.

myaccounts.py adds Authlib1.6.5 state/nonce/PKCE/JWKS validation, exact configured
callback, stable issuer/sub-to-local-ID SQLite linkage, user default roles,
admin only exact Workspace owner sub. Scoped HttpOnly JWT cookie, Secure on HTTPS,
expiry bounded by provider token/max8h. Local/guest first-user bootstrap/pairing
blocked in OIDC mode, unsafe Origin mutations rejected. Auth guard precedes core
JWT hook including media; no unbounded refresh. Separate protected app state.

Music source fixed to WORKSPACE_MUSIC_DIR (Workspace files/Music), normalized
as_posix for upstream folder matching; settings can't expand root. Serial file
change scans every15s rescan original files, no second media copy. Added wraps
to existing background decorator for synchronous scan entry. Standalone without
OIDC keeps existing local auth. Waitress on Windows avoids frozen Granian spawn
recursion. Explicit __init__.py fixes Python3.12 importlib.resources namespace.
OSS LicenseManager None settings endpoint fixed; premium gates untouched.

Pinned webclientv3.0.0 adapter builds APIs/media/worker paths from current public
path; Vue hash history must use window.location.pathname instead of './' Vite
base or it drops /music after login. Webclient license is MIT; server AGPLv3.
Bundled FFmpeg7.1 from imageio-ffmpeg0.6.0 is GPLv3 (notices/source links included
in suite). PyInstaller6.22.3 workspace.spec includes metadata/client.zip,FFmpeg.
Build on fast C cache then copy final EXE to dist; I exFAT is slow. Build venv
C:/Projects/.cache/swingmusic-venv, source snapshot swingmusic-source. Stop own
native test EXEs before rebuilding or Windows blocks overwriting dist/Music.exe.

Verified real signed local OIDC fixture with wrong audience/state rejection,
PKCE verifier, ordinary/owner roles, stable subjects and media auth. Vite and
PyInstaller native build/health passed. Fresh Workspace owner/Drive login and
MP3 upload passed; Music native callback passed. Browser test found/fixed both
Windows root separator mismatch and Vue prefix bug. Final exact package playback
and final installer verification still in progress; current code unit test passes.
Live existing MyAccounts/FileBrowser untouched. Test secrets/private browser state
stay only in protected .cache preview data, never Git or source artifacts.

Final native package verified in fresh isolated suite: real MyAccounts owner callback,
normal Drive login/upload, original MP3 on shared Music path, automatic indexing,
byte-identical media response, browser audio playback and actual player double-click
streaming206 while retaining /music/. No browser errors; anonymous media/APIs denied.
Final Music SHA256 recorded in extended installer catalog. Final installer rebuild
and source publication finish in Workspace handoff. Windows root and Vue bugs fixed.


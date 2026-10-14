"""Optional MyAccounts relying party; ordinary standalone installs keep local auth."""
import hashlib
import html
import os
import secrets
import sqlite3
import threading
import time
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlsplit

from authlib.integrations.flask_client import OAuth
from flask import jsonify, redirect, request, session
from flask_jwt_extended import create_access_token, get_jwt, set_access_cookies, verify_jwt_in_request

_users_lock = threading.Lock()


def enabled():
    return bool(os.environ.get("WORKSPACE_OIDC_ISSUER"))


def prepare_workspace():
    from swingmusic.config import UserConfig
    if not enabled():
        return
    music = os.environ.get("WORKSPACE_MUSIC_DIR")
    if not music or not Path(music).is_absolute():
        raise ValueError("MyAccounts mode requires an absolute WORKSPACE_MUSIC_DIR")
    Path(music).mkdir(parents=True, exist_ok=True)
    config = UserConfig()
    config.rootDirs = [Path(music).resolve().as_posix()]
    config.enableWatchdog = True
    config.enablePeriodicScans = True
    config.usersOnLogin = False
    config.save()


def scan_music():
    """Serial scans pick up files uploaded or changed through FileBrowser."""
    from swingmusic.lib.index import index_everything
    root = Path(os.environ["WORKSPACE_MUSIC_DIR"])
    previous = None
    while True:
        try:
            current = sorted((str(p), p.stat().st_size, p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file())
            if current != previous:
                index_everything.__wrapped__()
                previous = current
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Shared music scan failed")
        time.sleep(15)


def resolve_user(issuer, subject):
    from swingmusic.db.userdata import UserTable
    from swingmusic.settings import Paths
    from swingmusic.utils.auth import hash_password
    if not isinstance(subject, str) or not subject or len(subject) > 1024:
        raise ValueError("Missing stable subject")
    with _users_lock, sqlite3.connect(Paths().config_dir / "workspace-identities.sqlite3") as db:
        db.execute("CREATE TABLE IF NOT EXISTS identities (issuer TEXT, subject TEXT, user_id INTEGER, PRIMARY KEY(issuer,subject))")
        row = db.execute("SELECT user_id FROM identities WHERE issuer=? AND subject=?", (issuer, subject)).fetchone()
        if row:
            user = UserTable.get_by_id(row[0])
            if user is None or user.extra.get("workspaceIssuer") != issuer or user.extra.get("workspaceSubject") != subject:
                raise ValueError("Linked account is unavailable")
            return user
        digest = hashlib.sha256((issuer + "\0" + subject).encode()).hexdigest()
        name = "myaccounts-" + digest[:32]
        if UserTable.get_by_username(name):
            raise ValueError("Account link conflict")
        # Only the installer's exact owner subject may administer this music server.
        owner = os.environ.get("WORKSPACE_OWNER_SUBJECT", "")
        roles = ["admin"] if owner and secrets.compare_digest(subject, owner) else ["user"]
        UserTable.insert_one({"username": name, "password": hash_password(secrets.token_urlsafe(48)), "roles": roles,
                              "extra": {"workspaceIssuer": issuer, "workspaceSubject": subject}})
        user = UserTable.get_by_username(name)
        db.execute("INSERT INTO identities VALUES (?,?,?)", (issuer, subject, user.id))
        return user


def install(app):
    if not enabled():
        return
    issuer = os.environ["WORKSPACE_OIDC_ISSUER"].rstrip("/")
    callback = os.environ["WORKSPACE_OIDC_REDIRECT_URI"]
    parsed = urlsplit(callback)
    if parsed.scheme != "https" and not (parsed.scheme == "http" and parsed.hostname in ("localhost", "127.0.0.1")):
        raise ValueError("OIDC callback requires HTTPS or loopback HTTP")
    issuer_url = urlsplit(issuer)
    if issuer_url.scheme != "https" and not (issuer_url.scheme == "http" and issuer_url.hostname in ("localhost", "127.0.0.1")):
        raise ValueError("OIDC issuer requires HTTPS or loopback HTTP")
    prefix = os.environ.get("WORKSPACE_BASE_PATH", "").rstrip("/")
    origin = parsed.scheme + "://" + parsed.netloc
    app.secret_key = app.config["JWT_SECRET_KEY"]
    app.config.update(SESSION_COOKIE_NAME="swingmusic_oidc", SESSION_COOKIE_PATH=prefix + "/",
                      SESSION_COOKIE_SECURE=parsed.scheme == "https", SESSION_COOKIE_HTTPONLY=True,
                      SESSION_COOKIE_SAMESITE="Lax", JWT_ACCESS_COOKIE_PATH=prefix + "/",
                      JWT_COOKIE_SECURE=parsed.scheme == "https", JWT_COOKIE_SAMESITE="Lax")
    oauth = OAuth(app)
    client = oauth.register("myaccounts", client_id=os.environ["WORKSPACE_OIDC_CLIENT_ID"],
                            client_secret=os.environ["WORKSPACE_OIDC_CLIENT_SECRET"],
                            server_metadata_url=issuer + "/.well-known/openid-configuration",
                            client_kwargs={"scope": "openid profile email", "code_challenge_method": "S256"})

    @app.get("/auth/myaccounts/login")
    def myaccounts_login():
        session.clear()
        return client.authorize_redirect(callback)

    @app.get("/auth/myaccounts/callback")
    def myaccounts_callback():
        try:
            # Authlib checks the browser-bound state, nonce, JWKS signature, audience and expiry.
            token = client.authorize_access_token()
            claims = token["userinfo"]
            if claims["iss"] != issuer:
                raise ValueError("Issuer mismatch")
            user = resolve_user(issuer, claims["sub"])
            expiry = min(int(claims["exp"]), int(time.time()) + 8 * 3600)
            response = redirect(prefix + "/")
            jwt = create_access_token(identity=user.todict(), expires_delta=timedelta(seconds=max(1, expiry-int(time.time()))),
                                      additional_claims={"workspace_exp": expiry})
            set_access_cookies(response, jwt, max_age=max(1, expiry-int(time.time())))
            session.clear()
            from swingmusic.store.general import GeneralStore
            GeneralStore.admin_exists = True  # MyAccounts manages account creation, including before owner login.
            GeneralStore.root_dirs_set = True
            return response
        except Exception:
            session.clear()
            return "MyAccounts sign-in could not be verified. Start sign-in again.", 401

    @app.get("/healthz")
    def workspace_health():
        return {"status": "ok"}

    @app.before_request
    def workspace_guard():
        if request.path in ("/healthz", "/auth/myaccounts/login", "/auth/myaccounts/callback"):
            return
        if request.method not in ("GET", "HEAD", "OPTIONS") and request.headers.get("Origin") != origin:
            return {"msg": "Origin rejected"}, 403
        # Provider-managed identities must not gain a local-password/guest/refresh route.
        if request.path in ("/auth/login", "/auth/refresh", "/auth/profile/create", "/auth/profile/update", "/auth/profile/guest/create", "/auth/pair", "/auth/getpaircode"):
            return {"msg": "Manage your account in MyAccounts"}, 403
        if request.path == "/notsettings/add-root-dirs" or (request.path == "/notsettings/update" and "rootDirs" in (request.get_json(silent=True) or {})):
            return {"msg": "The Music folder is managed by Workspace"}, 403
        try:
            verify_jwt_in_request()
            if get_jwt().get("workspace_exp", 0) <= time.time():
                raise ValueError("Session expired")
        except Exception:
            if request.path == "/":
                link = html.escape(prefix + "/auth/myaccounts/login", quote=True)
                return '<!doctype html><html lang="en"><meta name="viewport" content="width=device-width"><title>Swing Music</title><style>body{background:#12141a;color:#eee;font:18px system-ui;max-width:560px;margin:15vh auto;padding:24px}a{display:inline-block;background:#835cff;color:white;padding:16px 24px;border-radius:12px;text-decoration:none}p{color:#aaa}</style><h1>Swing Music</h1><p>Your music, hosted with Workspace.</p><a href="'+link+'">Sign in with MyAccounts</a></html>'
            return jsonify(msg="Sign in with MyAccounts", login=prefix + "/auth/myaccounts/login"), 401

    from swingmusic.store.general import GeneralStore
    GeneralStore.admin_exists = True
    GeneralStore.root_dirs_set = True
    # This guard must run before upstream's JWT check, including on public media routes.
    guards = app.before_request_funcs[None]
    guards.insert(0, guards.pop())

# <img src="src/swingmusic/assets/my_music.svg" alt="" width="40" height="40"> My Music

Your own music library, powered by Swing Music. Run a standalone player or connect it to One Workspace for MyAccounts sign-in and a shared Music folder visible in Drive.

[Download Windows preview](https://github.com/oneworkspacestudio/Music/releases) · [Standalone and suite setup](WORKSPACE.md) · [One Workspace](https://github.com/oneworkspacestudio/one-workspace) · [Upstream Swing Music](https://github.com/swingmx/swingmusic)

![Swing Music artist view showing an album library and playback controls](.github/images/artist.webp)

*Upstream Swing Music interface reference. This fork adds MyAccounts integration and the My Music identity.*

## Listen your way

- Browse a music library through the browser player, with albums, artists, folders and playlists.
- Run the portable Windows server independently with normal local-password sign-in.
- Use MyAccounts for the connected suite, with ordinary user roles and a specifically assigned owner.
- Upload music through Drive and play the original files; the library is not copied into a second media store.
- Keep listening data, indexes and player metadata in Music's separate private-data folder.

## Install with One Workspace

Use the [Git and Music installer](https://github.com/oneworkspacestudio/one-workspace/releases). The suite registers the Music OIDC client, creates the shared `Music` folder and opens the player at `/music/`.

Changes to the shared Music folder are rescanned about every 15 seconds. All permitted Music users share that library; Drive folder scopes do not become per-track Music permissions automatically. See the [storage and identity details](WORKSPACE.md).

## Run independently

Download `Music.exe` from this fork's [Windows preview](https://github.com/oneworkspacestudio/Music/releases), then start it with a private configuration folder:

```powershell
.\Music.exe --host 127.0.0.1 --port 1970 --config 'D:\Private\MyMusic'
```

Open `http://localhost:1970`, create your local account and choose your library. Standalone use does not require Workspace or FileBrowser.

For shared sign-in, register a dedicated MyAccounts OIDC client and configure the protected environment described in [WORKSPACE.md](WORKSPACE.md). MyAccounts mode disables local/guest account creation and device pairing; use the browser login for the integrated preview.

## Build locally

```powershell
./scripts/build-workspace.ps1 -Python 'python' -BuildRoot 'I:/Build/MyMusic'
```

The Windows package is built from the server, pinned webclient v3.0.0, the base-path/SSO adapter and matching My Music artwork. The script uses Python 3.12, uv, Node/npm and PyInstaller; it produces `dist/Music.exe`. Builds run locally without GitHub Actions.

The server uses Waitress on Windows. See [build/runtime notes](WORKSPACE.md) for dependency versions, FFmpeg provenance and standalone settings. Upstream deployment documentation and Docker examples are retained in the [earlier README](docs/README-archive.md).

## Preview status and licenses

The Windows integration is an unsigned preview. New source branding is separate from already published EXE assets. App sign-out is local to Music; immediate global session revocation is not implemented in this preview.

Swing Music retains the [AGPLv3 license](LICENSE), the pinned webclient retains its MIT license, and bundled FFmpeg has its own GPL terms and source requirements. Optional premium features remain subject to upstream licensing. Credits, contributors and upstream community links are preserved in the [archived README](docs/README-archive.md).

# Suite branding

New my_music SVG/transparent192/512 PNG and Windows ICO in src/swingmusic/assets.
Pinned v3 webclient adapter copies the artwork to upstream logo paths, favicon and
PWA sizes before Vite build. Primary Logo.vue uses a32px image URL to preserve artwork
layout/gradients; title is My Music. Existing SSO/base path patches retained.
workspace.spec now passes the matching ICO to PyInstaller. Native upstream image
assets are source inputs; no premium/licensing behavior changed.

Fresh pinned client production Vite build passed on H, using npm cache on I.
All desktop/mobile/onboarding logo components use bounded image sizes. Original
artwork is not optimized/recolored by the SVG component loader. Native PyInstaller
packaging passed; new EXE is sibling one-workspace/dist/branding/Music.exe. Existing standalone/suite Music processes and published EXE
not replaced. No new functional tests for artwork-only change and no commit/push/release.
Canonical artwork/generation scripts live in sibling one-workspace.

Final Music EXE started in fresh standalone fixture and rendered its new96px MM
logo on the real onboarding page. Embedded Windows icons for Workspace, setup,
Drive, Photos, Studio, Git and Music were extracted/reviewed and match artwork.
Initial standalone /healthz probe returned401: that anonymous health endpoint is
registered only in OIDC mode. UI availability confirmed directly; no health200
or new auth acceptance claim. Owned Music preview tree stopped; task-created
app ports19971/19972/19974 closed. Existing running apps/releases remain unchanged.

## Source publication follow-up

User requested pushing the affected repositories and adding logos to their main
READMEs. This supersedes the earlier local-only publication scope. All five main
READMEs now reference their local SVG assets. Drive publication includes the
previous Photos/Studio prerequisite source so the branded app imports build from
the pushed branch; unrelated preview files and concurrent Workspace Mail changes
remain excluded. Existing executable releases and live installations are unchanged.
GitHub Actions is disabled before publication; builds remain local.

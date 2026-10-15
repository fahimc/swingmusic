# Music profile and browser cache fixes

Signed OIDC displayName/name stored in user extra and exposed as firstname for
Home greeting; stable generated username and account ownership unchanged.
Python3.13 packaging includes conditional audioop-lts; import/runtime check passes.
Pinned upstream client adapter is rebuilt into the portable executable.

Final browser check exposed an old offline SPA shell intercepting authentication
navigation. PWA workbox disables offline navigation fallback: authentication and HTML gates
always reach the server; hashed static assets may still be cached. Packaged static
UI assets remain accessible while signed out so the service worker can update;
private API/media authentication is unchanged. Auth, index and worker registration
responses use no-store. The suite updates only an existing exact-scope Music
worker after upgrades. Client calls the canonical /nothome/ endpoint directly
to avoid old cached redirects. Proxy preserves mounted prefixes on native
redirects, leaving external OIDC destinations unchanged (regression tests pass).
Friendly greeting passed browser SSO; final homepage/logout checks recorded in
the local verification report.
Local changes/builds only, no publication. Synthetic one-second audio fixture was
indexed/played during preceding audit; no private music modified.

## Final local acceptance
Music final client passed normal SSO, friendly greeting, Recently added fixture
and full suite switcher. Server-authoritative navigation replaced offline HTML
fallback; static PWA assets remain cacheable. Browser logout closed Workspace
app access: authenticated Photos before, Photos/Music gates after; seven anonymous
private API/media routes401. Chrome blocked final Accounts /api/logout with
ERR_BLOCKED_BY_CLIENT; provider browser session termination is unverified.
No warning bypass. UI wording explains this separate step. Google Mail-related
classification review submitted successfully; no delisting decision/live Mail
acceptance. Source histories/output retained, named C build caches removed after
path/reparse/process checks; active installation/rollback retained. Nothing
committed, pushed or released. Detailed local report records limits/open features.

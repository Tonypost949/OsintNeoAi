# OAuth Credentials Inventory

## client_secret.json (KEEP — works for Drive, Photos)
- Client ID: `32555940559.apps.googleusercontent.com`
- Type: Google Cloud SDK built-in client
- Account: Google-owned (used by all gcloud users)
- Works with: Drive API, Photos API, Cloud Platform
- Does NOT work with: Tasks API
- Location: `agent/client_secret.json`
- Project: project-743aab84-f9a5-4ec7-954 (Owner: txtdjdrop)

## client_secret_tasks.json (NEW — for Tasks API ONLY)
- Client ID: `1717842843-37k6bdt8ed3k31adjntq2tgiojrn1l9i.apps.googleusercontent.com`
- Type: Desktop app (External, Testing mode)
- Account: Created by amd949609 for amd949609's own project
- Works with: Tasks API
- Does NOT work with: Drive, Photos (use client_secret.json for those)
- Location: `agent/client_secret_tasks.json`
- Project: starlit-respect-416516 (Owner: amd949609)
- Test users: amd949609@gmail.com (can be published to External for wider access)
- Token: `agent/tasks_token.json`

## GCP Accounts & Projects

| Account | Role in project-743aab84 | Owns separate projects |
|---------|--------------------------|----------------------|
| txtdjdrop@gmail.com | Owner | Various |
| osintneoai@gmail.com | Owner | Various |
| amd949609@gmail.com | projectMover only | starlit-respect-416516 (Owner) |

## How to Use
- **Drive/Photos scanners**: Use `client_secret.json` (via auth_helper default)
- **Tasks manager** (`google_tasks_manager.py`): Uses `client_secret_tasks.json` (hardcoded in script)
- **New OAuth clients**: Must be created via Cloud Console UI — no public API exists

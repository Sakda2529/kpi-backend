# Deploy Backend to Railway

## Files in this folder
- `app.py` — FastAPI app with JWT + role checks
- `auth.py` — JWT + bcrypt helpers
- `database.py` — SQLite connection (reads `DB_FILE` from env)
- `requirements.txt` — Python dependencies
- `railway.json` — Railway build/deploy configuration
- `Procfile` — fallback start command
- `nixpacks.toml` — optional Python version + install commands
- `.env.example` — variables to create in Railway

## Before Deploy
1. Make sure your SQLite database exists locally.
2. If you want SQLite data to persist on Railway, attach a **Volume** and set `DB_FILE` to a file on that mounted path, for example `/data/kpi.db`.
3. Set `SECRET_KEY` in Railway Variables.

## Railway Deploy Steps
1. Push the repo to GitHub.
2. In Railway: **New Project → Deploy from GitHub Repo**.
3. Set **Root Directory** = `backend`.
4. In the service, go to **Variables** and add:
   - `SECRET_KEY`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` (optional)
   - `DB_FILE=/data/kpi.db` (if using a volume mounted at `/data`)
5. In **Settings → Networking**, generate a public domain.
6. The service should start with:
   `uvicorn app:app --host 0.0.0.0 --port $PORT`

## Health Check
- Railway will hit `/health`

## Frontend
Update your frontend:
```js
const API_BASE = "https://your-backend.up.railway.app";
```

## Notes
- `allow_origins` is currently `*` for easier testing. Restrict it to your frontend domain for production.
- If your `jobs.status` values are not `done`, `pending`, `in_progress`, `new`, adjust the SQL in `app.py`.

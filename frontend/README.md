# MAVYN frontend

The React/Vite app talks to the FastAPI backend. During local development, Vite forwards `/api/*` requests to `http://127.0.0.1:8000`, so the browser does not need a separate CORS configuration.

## Run locally

1. Start the backend from the repository root in another terminal:

   ```sh
   cd backend
   python -m venv .venv
   source .venv/Scripts/activate
   pip install -e .
   python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. Start the frontend:

   ```sh
   cd frontend
   npm ci
   npm run dev
   ```

3. Open the local URL printed by Vite. Check the API at [http://localhost:8000/docs](http://localhost:8000/docs).

Run `pip install -e .` and `npm ci` on first setup (or after dependencies change).
Set `VITE_API_URL` if the frontend should call a deployed backend directly instead of using the local Vite proxy.

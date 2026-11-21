# MAVYN

Skincare market intelligence demo with a React/Vite frontend and FastAPI backend. The frontend reads the backend's sample category and product data and can request review analysis and generated marketing content.

## Run locally

Use two terminals from the repository root.

**Backend**

```sh
cd backend
python -m venv .venv
source .venv/Scripts/activate
pip install -e .
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend**

```sh
cd frontend
npm ci
npm run dev
```

Run the install commands the first time (or after dependencies change). Open the URL Vite prints. The API docs are at [http://localhost:8000/docs](http://localhost:8000/docs). The Vite development proxy forwards frontend `/api` requests to the backend.
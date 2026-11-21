# MAVYN

Skincare market intelligence demo with a React/Vite frontend and FastAPI backend. The frontend reads the backend's sample category and product data and can request review analysis and generated marketing content.

## Run locally

Set up the dependencies once, then start both servers from the repository root with one command.

**First-time setup (PowerShell)**

```sh
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -e .\backend
npm install
npm --prefix frontend ci
```

**Start the app**

```sh
npm run dev
```

Open the URL Vite prints. The API docs are at [http://localhost:8000/docs](http://localhost:8000/docs). The Vite development proxy forwards frontend `/api` requests to the backend. Stop both servers with `Ctrl+C`.
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

**Configure live research**

Copy `backend\.env.example` to `backend\.env` and set `NIM_API_KEY` and `TAVILY_API_KEY`
there. Keep both keys server-side; do not put them in a `VITE_` variable or share them in chat.
Restart the backend after editing the file. `/health` reports whether both providers are configured.

For a Vercel deployment, add `NIM_API_KEY`, `TAVILY_API_KEY`, `NIM_MODEL`,
`NIM_FALLBACK_MODELS`, and `NIM_BASE_URL` as environment variables for the backend project,
then redeploy.

**Start the app**

```sh
npm run dev
```

Open the URL Vite prints. The API docs are at [http://localhost:8000/docs](http://localhost:8000/docs). The Vite development proxy forwards frontend `/api` requests to the backend. Stop both servers with `Ctrl+C`.

For Lighthouse or production performance checks, build and preview the optimized frontend instead of auditing the Vite development server:

```sh
npm --prefix frontend run build
npm --prefix frontend run preview
```
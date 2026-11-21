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

**Configure Gemini**

Copy `backend\.env.example` to `backend\.env` and set `GEMINI_API_KEY` there. Keep the key
server-side; do not put it in a `VITE_` variable or share it in chat. The default model is
`gemini-3.5-flash-lite` and can be changed with `GEMINI_MODEL`. Restart the backend after editing
the file. Content generation returns a clear configuration error when the key is missing rather
than presenting template output as AI-generated. Gemini model selection is configurable with
`GEMINI_MODEL` and the comma-separated `GEMINI_FALLBACK_MODELS`; the backend tries at most three
models and does not retry credential errors.

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
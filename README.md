# Requirement Analysis Copilot

## Render deployment

### Backend

- Root directory: `backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health path: `/health`
- Required variables: `GEMINI_API_KEY`, `GEMINI_MODEL`, `FRONTEND_ORIGINS`, `PYTHON_VERSION`

### Frontend

- Root directory: `frontend`
- Build: `npm ci && npm run build`
- Publish directory: `dist`
- Required variable: `VITE_API_BASE_URL`

### Deployment order

1. Deploy backend.
2. Verify `/health` and `/docs`.
3. Set frontend `VITE_API_BASE_URL` to the backend URL.
4. Deploy frontend.
5. Set backend `FRONTEND_ORIGINS` to the frontend URL.
6. Redeploy backend.
7. Perform production smoke tests.

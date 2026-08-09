# CarBiz AI AutoMod V5.1

V5.1 changes the V5 demo into a real AI-ready architecture.

## What works

- Upload a real car photo
- `/api/identify` sends the photo to an OpenAI vision-capable model and returns make/model/generation/body/color/confidence
- Choose a modification package
- `/api/render` sends the original vehicle photo to the image edit model with preservation rules
- Before/After switching
- API key remains on the backend only

## Architecture

Browser / GitHub Pages
→ FastAPI backend on Render
→ OpenAI Responses API for vehicle identification
→ OpenAI Images Edit for modification preview

## A. Test locally

1. Install Python 3.11+.
2. Open this folder in Terminal.
3. Create a virtual environment:

   python -m venv .venv

4. Activate it.

   macOS/Linux:
   source .venv/bin/activate

   Windows:
   .venv\Scripts\activate

5. Install:

   pip install -r requirements.txt

6. Copy `.env.example` to `.env` and add your OpenAI API key.

7. Start backend:

   uvicorn server:app --reload

8. Keep `config.js` as:

   window.CARBIZ_API_BASE = "http://127.0.0.1:8000";

9. Open `index.html` through a simple local web server, for example:

   python -m http.server 5500

10. Open `http://127.0.0.1:5500`.

## B. Deploy backend to Render

1. Put ALL files in a GitHub repository.
2. In Render create a new **Blueprint** or Web Service from the repository.
3. `render.yaml` contains the build/start configuration.
4. Add secret environment variable:

   OPENAI_API_KEY = your real key

5. Deploy.
6. Copy the backend URL, e.g.:

   https://carbiz-v5-1-api.onrender.com

7. Test:

   https://carbiz-v5-1-api.onrender.com/health

## C. Connect frontend

Edit `config.js`:

window.CARBIZ_API_BASE = "https://YOUR-RENDER-BACKEND.onrender.com";

Commit the change.

## D. Deploy frontend with GitHub Pages

Repository → Settings → Pages → Deploy from branch → main → /(root)

Your frontend URL will look like:

https://YOUR-USERNAME.github.io/YOUR-REPO/

Then set the Render environment variable `ALLOWED_ORIGINS` to your exact GitHub Pages origin for production, such as:

https://YOUR-USERNAME.github.io

Restart/redeploy the backend after changing it.

## Security

- NEVER put `OPENAI_API_KEY` inside `index.html` or `config.js`.
- `.env` is excluded via `.gitignore`.
- For production, restrict CORS with `ALLOWED_ORIGINS`.
- Add authentication, rate limiting, request logging, quotas and image retention/deletion rules before public launch.

## V5.1 limitation

AI car identification from one image is probabilistic. Exact model year/trim may be uncertain when badges, lamps or body details are hidden. The UI therefore includes confidence and generation notes.

Generated modification images are visual previews, not engineering fitment guarantees. Real fitment must be checked against vehicle/chassis-specific parts data.

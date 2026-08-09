# CarBiz AutoMod V5.3

AI car identification + smart-fitment starter catalog + AI modification preview.

## Deploy
Frontend: GitHub Pages from `main` / `(root)`.
Backend: Render using `render.yaml`.

## Important
- `config.js` points the frontend to the Render API.
- Keep `OPENAI_API_KEY` only in Render Environment variables; never put it in GitHub/frontend code.
- `catalog.json` is a starter catalog. Prices are estimates. Items labelled CarBiz Select are not asserted to be live third-party products. Replace/add records with verified supplier SKU, product URL, vehicle years/chassis, stock and current price before enabling checkout.
- Smart Fitment is a recommendation score, not mechanical certification. Wheel PCD/offset, clearances and installation should be verified by a qualified installer.

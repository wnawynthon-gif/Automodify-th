# CarBiz AI AutoMod V5.2 Upgrade

V5.2 is designed to replace the files in your existing `Automodify-th` GitHub repo.

## V5.2 changes
- AI Identify remains the same working V5.1 backend.
- Vehicle-aware recommendations after make/model/body detection.
- `catalog.json` represents starter Layers 1–5 data.
- Compatibility score ranks kits by vehicle body type.
- Product cards include visual thumbnail icons.
- Mobile/tablet view puts the car preview before the controls.
- Detailed selected-product prompt is passed to `/api/render`.
- Includes the `from pathlib import Path` fix for the V5.1 render error.
- Existing Render service URL is retained. Do not create a second Render service.

## Upgrade
Upload all files in this ZIP to the root of GitHub repo `Automodify-th`, replace files with the same names, then Commit changes.

GitHub Pages updates the frontend after the commit. Your existing Render Blueprint can redeploy the backend from the same GitHub branch.

## Production note
Compatibility score in V5.2 is a recommendation score, not engineering certification. Later versions should add exact chassis, trim, PCD, offset, tyre size, sensor/ADAS clearance, part number and supplier stock.

# Poster build report — VERTICAL CHOREOGRAPHIES (2026-11-03)

Run id `poster-2026-11-03-seed20261103`. This is the report of the monochrome point-cloud poster (an appendix asset, not a slide).

## Executed actions

| File | Note |
|---|---|
| `src/data/aik_boundary_rep.json` | Mirror of `analysis/outputs/aik/aik_boundary_rep.csv` (cells `aik_e2_top1_g4_cont` = A, `aik_e2_low3_g4_cont` = B). Per boundary: mean, sd, p05/p95, anchor, mode shares, dominant mode, retention. Per run (n=100): U, elev_share, esc_share |
| `src/data/build_poster_dataset.py` | Rebuilds the JSON from the CSV and refreshes the inline data block of the HTML. No hand-typed numbers |
| `src/services/gstack_sync.js` | Google Sheets v4 loader, Drive v3 uploader, execution logger, exponential backoff, offline fallback |
| `src/visualizer/vertical_choreography_poster.html` | Canvas 2400x4200 + SVG HUD, control bar (Download 4K PNG / Download SVG HUD / Upload CSV), inline dataset |
| `src/visualizer/point_cloud_engine.js` | Mulberry32, 1D simplex, monotone cubic Hermite, ridge stippling, FNV-1a hash |
| `poster/vertical_choreographies_2400x4200.png` | Exported with the real "Download 4K PNG" button (control bar absent) |

- Canvas 2400x4200. Particles: B spire 352,565 + A massif 317,755 + zone-3 horizon 226,369 = 896,689. Render 947-1,392 ms (headless Chromium). Seed 20261103.
- Determinism: three consecutive renders gave the identical full-canvas+HUD hash `b7178252-c77b7cd2`. A CSV upload of a 1,600-row subset gave an identical canvas hash and identical HUD text.
- Data binding: 32/32 displayed flow and anchor values were found in the rendered HUD.
- Spec table vs dataset: 48 values compared, 1 mismatch: B 5→6F dominant mode (spec ELV, data ESC: esc 50.2 % vs elv 48.2 %). The data value is shown.
- Hero metrics: `-74.8 %` matches. Spec `+28.7 %` is `+28.76 %`, shown as `+28.8 %` (6→7F to 8→9F); the local step 7→8F to 8→9F (+26.4 %) is printed beneath it.
- Ridge nodes use each run's real values; noise has an envelope that is zero at every node; the nearest slice is the run closest to the 100-run mean. The 160 needle bars are 2 scenarios x 8 boundaries x 10 run-deciles.

## External services

- The Google Sheets / Drive integration (`src/services/gstack_sync.js`) was written but **never run against a live account** (no credentials were available).
- Verified offline: fallback to the local JSON (16 rows, no exception); backoff (429 twice then success with delays 1,500 / 2,500 ms; 503 forever = 4 calls with 1,000 / 2,000 / 4,000 ms then throws; 400 = no retry); sheet merge rejects sheets that do not yield 16 rows.
- Default sheet range `alk_boundary_rep!A1:I17` is the original author's tab name (override with `GSTACK_SHEET_RANGE`). Required environment variables: `GOOGLE_APPLICATION_CREDENTIALS`, `GSTACK_SHEET_ID`, `GSTACK_DRIVE_FOLDER_ID`. No secrets are stored in this repository.

## Open issues

1. Fonts (JetBrains Mono / Space Mono) are not embedded, so text metrics differ across machines.
2. SVG HUD export is implemented but not file-tested.
3. The shift of the dominant mode from escalator to elevator with anchor position is a new connection that is not in the paper text; confirm the model's mode-choice rule before presenting it.
4. The poster is a standalone portrait asset, not a 16:9 slide.
5. Tuning knobs in `render()`: `strip.count`, `face.count`, `face.tau`, `ampFrac`, fbm octaves, `zx` / `zy`.

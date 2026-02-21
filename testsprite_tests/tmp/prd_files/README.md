# UI Dataset Builder

Web UI scrape + auto-label dataset builder using Playwright. Crawls URLs, renders pages in Chromium, takes screenshots, extracts UI element bounding boxes from the DOM, and exports COCO (and optionally YOLO) annotations plus rich metadata for VLM grounding.

## Install

```bash
# From project root (ui_dataset_builder/)
uv sync
playwright install chromium
```

## Run

```bash
uv run ui-dataset build --urls-file data/urls.txt --out output/ --max-pages 10
```

(You can also run `uv run ui-dataset --max-pages 10` with options only.)

Main options:

- `--urls-file` – One URL per line (default: `data/urls.txt`)
- `--out` – Output directory (default: `output/`)
- `--max-pages` – Cap number of URLs to process (default: 500)
- `--concurrency` – Number of browser contexts in parallel (default: 4)
- `--viewport "1280x720"` – Desktop viewport; use `--mobile` for 390x844
- `--scroll-steps 0|1|2` – Extra screenshots after scrolling (~70% viewport per step)
- `--wait networkidle|domcontentloaded|load` – Page load strategy (default: networkidle)
- `--export coco|yolo|both` – Annotation format (default: coco)
- `--classes` – Comma-separated class list (default: button,link,input,...)
- `--min-size` – Min element width/height in px (default: 10)
- `--max-elements` – Max elements per screenshot (default: 200)
- `--respect-robots` – Respect robots.txt (default: false; see Legal below)

Output layout:

- `output/images/<site>/<page_id>.png` – Screenshots
- `output/annotations/coco.json` – Single COCO file; `per_image/<page_id>.json` for debugging
- `output/annotations/yolo/` – YOLO .txt per image (when `--export yolo` or `both`)
- `output/metadata/<site>/<page_id>.json` – Per-element metadata for VLM
- `output/logs/failures.csv` – Failed URLs and errors
- `output/manifest.jsonl` – One line per sample (url, image_path, metadata_path, page_id)

## Class taxonomy

- **button** – `<button>`, `[role="button"]`, or clickable div/span (pointer + handler)
- **link** – `<a href>`
- **input** – `<input>` (text, email, password, search, number, tel, url), `<textarea>`
- **checkbox** – `<input type="checkbox">`
- **radio** – `<input type="radio">`
- **dropdown** – `<select>`, role=combobox, aria-haspopup=listbox
- **image_icon** – `<img>`, `<svg>`, `<video>` (small SVGs ≤128px as icon)
- **text** – Visible text elements not in above classes (downsampled to 30 per image)

## Legal / ToS

Respect site terms of service and robots.txt. This tool is for building datasets from pages you are allowed to crawl. **By default `--respect-robots` is false**; the tool logs a warning. Ensure you have permission to crawl target sites and use responsibly at your own risk.

## Visualize annotations

- **Included script**: Draw bboxes on the first few images:
  ```bash
  uv sync --extra dev   # installs Pillow
  uv run python scripts/visualize_coco.py --max-images 5
  ```
  Output is written to `output/annotations/visualized/`. Options: `--coco`, `--output-dir`, `--out-dir`, `--max-images`.
- **COCO**: Use `output/annotations/coco.json` with `output/images/` in any COCO-capable viewer (e.g. [coco-viewer](https://github.com/trsvchn/coco-viewer)).
- **Per-image**: Open `output/annotations/per_image/<page_id>.json` next to `output/images/<site>/<page_id>.png` for quick debugging.

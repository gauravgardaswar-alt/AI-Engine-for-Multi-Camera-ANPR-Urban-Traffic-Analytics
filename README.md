# TrackSight — City-Wide ANPR Trajectory Tracking (SIH26127)

Working backend prototype for the problem statement: detects number
plates from multi-camera feeds, reads them with OCR, stores every
sighting with location + timestamp, and reconstructs a vehicle's
route across the city.

## What's here

```
tracksight/
├── requirements.txt
├── schema.sql              # PostgreSQL + PostGIS schema, run once
├── app/
│   ├── config.py            # settings (DB url, model paths, thresholds)
│   ├── database.py          # SQLAlchemy models
│   ├── detector.py          # YOLOv8 plate detection
│   ├── ocr_reader.py        # EasyOCR plate text reading
│   ├── pipeline.py          # detection -> OCR -> DB -> alert, per frame
│   └── main.py              # FastAPI app with all endpoints
```

## Setup

1. **Install PostgreSQL with PostGIS**, then create a database and run the schema:
   ```bash
   createdb tracksight
   psql tracksight -f schema.sql
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your database URL** (or edit the default in `app/config.py`):
   ```bash
   export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/tracksight"
   ```

4. **Get a real plate-detection model.** The default `yolov8n.pt` is the
   stock COCO model — it does NOT detect number plates out of the box.
   Either:
   - Fine-tune YOLOv8 on an Indian number-plate dataset (Roboflow has
     several public ones), or
   - Point `YOLO_MODEL_PATH` in `app/config.py` at a `.pt` file you've
     trained.

5. **Run the API**:
   ```bash
   uvicorn app.main:app --reload
   ```
   Visit `http://localhost:8000/docs` for interactive Swagger docs.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/detect/{camera_id}` | Upload a frame, run detection + OCR, store + alert |
| GET | `/trajectory/{plate_number}` | Full chronological route for a plate |
| GET | `/analytics/density` | Detection counts per camera (for heatmap) |
| POST | `/watchlist` | Add a plate to the blacklist/watchlist |
| GET | `/watchlist` | List watched plates |
| GET | `/alerts` | Recent alerts (watchlist matches) |
| POST | `/alerts/{id}/acknowledge` | Mark an alert as handled |

## Connecting the frontend

The `anpr_dashboard.html` and `anpr_feed_watchlist.html` prototypes
built earlier currently use hardcoded sample data (`cameras`,
`trajectories`, `alertsData` arrays in their `<script>` tags). To wire
them to this backend:

1. Replace the hardcoded `trajectories` object with a `fetch('/trajectory/' + plate)` call to this API.
2. Replace the hardcoded `alertsData` array with `fetch('/alerts')`.
3. Replace the watchlist form's local array with a `POST /watchlist` call.

## Testing without real cameras

You can test the full pipeline with any photo of a car:
```bash
curl -X POST "http://localhost:8000/detect/C1" \
     -F "file=@sample_car.jpg"
```

## Known limitations (be upfront about these in your demo)

- Stock YOLOv8 model needs fine-tuning on actual plates before accuracy claims hold
- No camera time-sync (NTP) implemented yet — timestamps assume server clock
- No authentication/authorization on the API yet — add before any real deployment
- OCR pre-processing is basic; heavy rain/motion blur will still need more work

-- TrackSight — City-Wide ANPR Trajectory Tracking
-- Run this once on a fresh PostgreSQL database with PostGIS enabled.

CREATE EXTENSION IF NOT EXISTS postgis;

-- Camera registry: every ANPR camera in the city network
CREATE TABLE IF NOT EXISTS cameras (
    camera_id     VARCHAR(20) PRIMARY KEY,
    name          VARCHAR(120) NOT NULL,
    location      GEOGRAPHY(POINT, 4326) NOT NULL,
    road_name     VARCHAR(120),
    is_active     BOOLEAN DEFAULT TRUE
);

-- Every plate detection event from any camera
CREATE TABLE IF NOT EXISTS detections (
    id              BIGSERIAL PRIMARY KEY,
    plate_number    VARCHAR(20) NOT NULL,
    camera_id       VARCHAR(20) REFERENCES cameras(camera_id),
    confidence      REAL NOT NULL,
    detected_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    frame_path      TEXT
);

CREATE INDEX IF NOT EXISTS idx_detections_plate ON detections (plate_number);
CREATE INDEX IF NOT EXISTS idx_detections_time  ON detections (detected_at);
CREATE INDEX IF NOT EXISTS idx_detections_camera ON detections (camera_id);

-- Blacklisted / flagged vehicles
CREATE TABLE IF NOT EXISTS watchlist (
    id            BIGSERIAL PRIMARY KEY,
    plate_number  VARCHAR(20) UNIQUE NOT NULL,
    owner_info    VARCHAR(200),
    reason        VARCHAR(120) NOT NULL,
    added_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Alerts fired when a watchlisted plate is seen
CREATE TABLE IF NOT EXISTS alerts (
    id            BIGSERIAL PRIMARY KEY,
    plate_number  VARCHAR(20) NOT NULL,
    camera_id     VARCHAR(20) REFERENCES cameras(camera_id),
    detected_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    reason        VARCHAR(120),
    acknowledged  BOOLEAN DEFAULT FALSE
);

-- Sample camera seed data (Nanded, Maharashtra)
INSERT INTO cameras (camera_id, name, location, road_name) VALUES
('C1', 'Vazirabad Chowk',  ST_GeogFromText('POINT(77.3120 19.1650)'), 'Main Road'),
('C2', 'Shivaji Putla',    ST_GeogFromText('POINT(77.3180 19.1590)'), 'Station Road'),
('C3', 'CIDCO Junction',   ST_GeogFromText('POINT(77.3260 19.1520)'), 'CIDCO Road'),
('C4', 'Bus Stand Road',   ST_GeogFromText('POINT(77.3260 19.1610)'), 'Bus Stand Road'),
('C5', 'Degloor Naka',     ST_GeogFromText('POINT(77.3140 19.1470)'), 'Degloor Road'),
('C6', 'Airport Road',     ST_GeogFromText('POINT(77.3230 19.1420)'), 'Airport Road')
ON CONFLICT (camera_id) DO NOTHING;

"""
Reads live frames from a phone running IP Webcam app,
sends each frame to the TrackSight backend for detection.
"""
import requests
import time

# ---- CONFIGURED FOR YOUR PHONE ----
PHONE_IP = "10.230.15.67"
PHONE_PORT = "8080"
CAMERA_ID = "C1"
BACKEND_URL = f"http://localhost:8000/detect/{CAMERA_ID}"
CAPTURE_INTERVAL = 3   # seconds between each detection attempt

PHONE_IP = ""   # ithe CAM 2 cha IP
PHONE_PORT =  "10.230.15.80.8080"
CAMERA_ID = "C2"             # ithe C1 chya jagi C2
# ------------------------------------

STREAM_URL = f"http://{PHONE_IP}:{PHONE_PORT}/shot.jpg"

print(f"Connecting to phone camera at {STREAM_URL}")
print(f"Sending frames to backend: {BACKEND_URL}")
print("Press Ctrl+C to stop.\n")

while True:
    try:
        response = requests.get(STREAM_URL, timeout=5)
        if response.status_code != 200:
            print("Failed to get frame from phone camera.")
            time.sleep(CAPTURE_INTERVAL)
            continue

        image_bytes = response.content

        files = {"file": ("frame.jpg", image_bytes, "image/jpeg")}
        result = requests.post(BACKEND_URL, files=files, timeout=30)

        print(f"[{time.strftime('%H:%M:%S')}] Sent frame -> Status: {result.status_code}")
        print(result.json())
        print("-" * 50)

    except Exception as e:
        print("Error:", e)

    time.sleep(CAPTURE_INTERVAL)
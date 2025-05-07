from flask import Flask, render_template, Response
import cv2
from deepface import DeepFace
from datetime import datetime
import mysql.connector
import threading
import time

app = Flask(__name__)

@app.route('/')
def index():
     return render_template("index.html")

@app.route('/services')
def services():
     return render_template("services.html")

@app.route('/web')
def web():
     return render_template("web.html")

@app.route('/contact_us')
def contact_us():
    return render_template("contact_us.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/collect')
def collect():
    return render_template("form.html")

# === Shared variables ===
frame_lock = threading.Lock()
current_frame = None
current_emotion = "Face not detected"
last_process_time = time.time()

# === MySQL connection ===
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="face_analysis"
)
cursor = conn.cursor()

# === Webcam setup ===
cap = cv2.VideoCapture(0)

# === Background thread to read frames ===
def capture_frames():
    global current_frame
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        with frame_lock:
            current_frame = frame.copy()

# === Background thread for emotion detection ===
def detect_emotion():
    global last_process_time, current_emotion
    while True:
        if time.time() - last_process_time >= 5:
            with frame_lock:
                frame = current_frame.copy() if current_frame is not None else None

            if frame is not None:
                try:
                    result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                    faces = result if isinstance(result, list) else [result]

                    if len(faces) != 1:
                        with frame_lock:
                            current_emotion = "Face not detected"
                    else:
                        face = faces[0]
                        emotion = face['dominant_emotion']
                        region = face['region']

                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute("INSERT INTO emotion_results (timestamp, emotion) VALUES (%s, %s)", (timestamp, emotion))
                        conn.commit()

                        with frame_lock:
                            current_emotion = emotion

                        print(f"[{timestamp}] Detected: {emotion}")
                except Exception as e:
                    print("[ERROR]", e)
                    with frame_lock:
                        current_emotion = "Face not detected"

                last_process_time = time.time()

# === Video stream route ===
def generate_frames():
    while True:
        with frame_lock:
            if current_frame is None:
                continue

            frame = current_frame.copy()
            try:
                result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                faces = result if isinstance(result, list) else [result]

                if len(faces) == 1:
                    face = faces[0]
                    x, y, w, h = face['region']['x'], face['region']['y'], face['region']['w'], face['region']['h']
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    label = f"Emotion: {current_emotion}"
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 255, 0), 2, cv2.LINE_AA)
                else:
                    label = "Face not detected"
                    cv2.putText(frame, label, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 0, 255), 2, cv2.LINE_AA)
            except:
                label = "Face not detected"
                cv2.putText(frame, label, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 0, 255), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# === Emotion API route ===
@app.route('/current_emotion')
def current_emotion_api():
    with frame_lock:
        return current_emotion

# === Web page route ===
@app.route('/web')
def web_page():
    return render_template('web.html')

# === Start background threads ===
frame_thread = threading.Thread(target=capture_frames, daemon=True)
emotion_thread = threading.Thread(target=detect_emotion, daemon=True)
frame_thread.start()
emotion_thread.start()

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# === Start Flask app ===
if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)

# Example content for emotion_checker_app.py (replace this with your actual code)
import time

print("Emotion Checker app is running...")
time.sleep(3)  # Simulate processing time
print("Emotion checked successfully!")

from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# Function to connect to the database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",       # Replace with your MySQL username
        password="12345",   # Replace with your MySQL password
        database="face_analysis"    # Replace with your correct database name
    )

@app.route("/")
def home():
    return render_template("home.html")

# Emotion question route
@app.route("/emotion-questions", methods=["GET", "POST"])
def emotion_questions():
    # Fetch last detected emotion from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT emotion FROM emotion_results ORDER BY id DESC LIMIT 1")
    last_emotion = cursor.fetchone()
    cursor.close()
    conn.close()

    if last_emotion:
        emotion = last_emotion[0]
    else:
        emotion = None  # Handle case when no emotion is detected

    options_by_emotion = {
        "sad": [
            "I feel lonely", "I miss someone", "I'm stressed about exams",
            "I feel hopeless", "I just feel low"
        ],
        "angry": [
            "Someone hurt me", "I'm frustrated", "I'm overwhelmed",
            "I feel ignored", "I was treated unfairly"
        ],
        "happy": [
            "I achieved something", "Someone made me smile", "It's a good day",
            "I feel loved", "Just feeling good"
        ],
        "surprise": [
            "Unexpected news", "A surprise event", "Someone surprised me",
            "I discovered something", "It just happened suddenly"
        ],
        "fear": [
            "I'm anxious", "I'm worried about future", "I saw something scary",
            "I fear failure", "I feel unsafe"
        ],
        "neutral": [
            "Just a regular day", "I’m not sure", "Feeling okay",
            "Balanced mood", "Neither happy nor sad"
        ]
    }

    if request.method == "POST":
        reason = request.form["reason"]
        suggestion_map = {
            "I feel lonely": "Try reaching out to a friend or family member.",
            "I miss someone": "Write down how you feel and what you'd tell them.",
            "I'm stressed about exams": "Take a break, organize your tasks, and talk to someone who understands.",
            "I feel hopeless": "You’re not alone. Consider talking to a counselor or trusted person.",
            "I just feel low": "Do something you enjoy, even a small walk or a favorite song can help.",
            "Someone hurt me": "Try journaling or expressing yourself in a healthy way.",
            "I'm frustrated": "Take a short walk and do some breathing exercises.",
            "I'm overwhelmed": "Break tasks into smaller parts and take it slow.",
            "I feel ignored": "Reach out to someone and let them know how you feel.",
            "I was treated unfairly": "Talk to someone you trust about it and seek advice."
            # Add more suggestions here as needed
        }
        return render_template("emotion_suggestion.html", reason=reason, suggestion=suggestion_map.get(reason, "We’re here for you."))

    return render_template("emotion_questions.html", emotion=emotion, options=options_by_emotion.get(emotion, []))


if __name__ == "__main__":
    app.run(debug=True, port=5000)

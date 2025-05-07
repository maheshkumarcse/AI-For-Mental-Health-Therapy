from flask import Flask, render_template
import mysql.connector
import requests

app = Flask(__name__)

def get_meme_with_joke(emotion):
    try:
        # Emotion → subreddit mapping
        emotion_subreddits = {
            "happy": "memes",
            "sad": "wholesomememes",
            "angry": "aww",                 # Calming and soothing GIFs
            "surprise": "Unexpected",       # Funny surprise reactions
            "neutral": "MildlyInteresting",
            "fear": "GetMotivated"
        }

        subreddit = emotion_subreddits.get(emotion.lower(), "memes")
        response = requests.get(f"https://meme-api.com/gimme/{subreddit}")

        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title"),
                "image_url": data.get("url")
            }

    except Exception as e:
        print(f"[✖] Error fetching meme: {e}")
    return None

@app.route("/")
def index():
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",      # ← replace with your DB username
            password="12345",  # ← replace with your DB password
            database="face_analysis"
        )
        cursor = conn.cursor()

        # Get the latest detected emotion
        cursor.execute("SELECT emotion, timestamp FROM emotion_results ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        emotion = "Unknown"
        timestamp = "--"
        meme_data = None

        if row:
            emotion, timestamp = row
            meme_data = get_meme_with_joke(emotion)

        return render_template("indexai.html", emotion=emotion, timestamp=timestamp, meme=meme_data)

    except Exception as e:
        return f"❌ Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)

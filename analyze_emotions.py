from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="face_analysis"
    )

@app.route("/", methods=["GET", "POST"])
def check_emotion():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        if "confirm" in request.form:
            if request.form["confirm"] == "yes":
                return redirect("/thankyou")
            else:
                return render_template("select_emotion.html")
        elif "corrected_emotion" in request.form:
            corrected = request.form["corrected_emotion"]
            cursor.execute("INSERT INTO emotion_results (emotion) VALUES (%s)", (corrected,))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect("/thankyou")

    cursor.execute("SELECT emotion FROM emotion_results ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    emotion = row[0] if row else "neutral"
    return render_template("confirm_emotion.html", emotion=emotion)
@app.route("/thankyou")
def thank_you():
    return "<h2>✅ Emotion confirmed and stored. Thank you!</h2>"

if __name__ == "__main__":
    app.run(debug=True)

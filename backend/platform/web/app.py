from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask_adam():
    data = request.json
    response = requests.post(
        "http://localhost:8000/v1/query",
        json={"message": data["text"]},
        headers={"X-Platform": "web"}
    )
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(port=5000)
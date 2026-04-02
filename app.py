from flask import Flask, jsonify
from bot import run_bot

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "Siddhi Pharma Bot is running! 🤖"})

@app.route("/run-bot")
def trigger_bot():
    """Cron job endpoint — called daily by Render"""
    try:
        run_bot()
        return jsonify({"status": "success", "message": "Bot run complete!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

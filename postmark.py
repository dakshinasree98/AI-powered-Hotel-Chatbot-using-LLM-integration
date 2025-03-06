from flask import Flask, request, jsonify
import os
import requests
import logging 
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()
POSTMARK_API_KEY = os.getenv("POSTMARK_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to send email using Postmark
def send_email(to_email, subject, body):
    postmark_url = "https://api.postmarkapp.com/email"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Postmark-Server-Token": POSTMARK_API_KEY
    }
    data = {
        "From": SENDER_EMAIL,
        "To": to_email,
        "Subject": subject,
        "TextBody": body
    }
    
    response = requests.post(postmark_url, json=data, headers=headers)
    if response.status_code == 200:
        return {"success": True, "message": "Email sent successfully"}
    else:
        return {"success": False, "error": response.text}

@app.route('/send_email', methods=['POST'])
def handle_send_email():
    data = request.get_json()
    email = data.get("email")
    subject = data.get("subject", "Room Availability at Thira Beach Home")
    body = data.get("body", "Here are the details of the available rooms.")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    result = send_email(email, subject, body)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)

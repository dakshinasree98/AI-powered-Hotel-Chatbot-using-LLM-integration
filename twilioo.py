import os
import sqlite3
from flask import Flask, request, jsonify
from groq import Groq
from dotenv import load_dotenv
import logging
from twilio.twiml.messaging_response import MessagingResponse

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")

# Initialize Groq client
groq_client = Groq(api_key=API_KEY)

# Hotel information constant
HOTEL_INFO = """Thira Beach Home is a luxurious seaside retreat that seamlessly blends Italian-Kerala heritage architecture with modern luxury..."""

# Connect to SQLite database
def connect_to_db():
    return sqlite3.connect('rooms.db')

# Fetch room details from the database
def fetch_room_details():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('SELECT title, description FROM room_data')
    results = cursor.fetchall()
    conn.close()
    if results:
        return "\n\n".join([f"Room: {title}\nDescription: {desc}" for title, desc in results])
    return "No room details available."

# Classify the query using Groq AI
def classify_query(query):
    prompt = f"""Classify the following query:
    1. Checking details - if it's about booking a hotel room
    2. Getting information - if it's about general hotel info.
    
    Query: {query}
    Respond with only the number (1 or 2)."""
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10
    )
    return response.choices[0].message.content.strip()

# Generate AI response
def generate_response(query, context):
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are Maya, a friendly hotel receptionist."},
            {"role": "user", "content": f"Query: {query}\nContext: {context}"}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content

# API Endpoint for Query Processing
@app.route('/query', methods=['POST'])
def handle_query():
    data = request.get_json()
    query = data.get('query', '')

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    query_type = classify_query(query)

    if query_type == "1":
        context = fetch_room_details()
    elif query_type == "2":
        context = HOTEL_INFO
    else:
        return jsonify({"error": "Invalid query classification"}), 500

    response = generate_response(query, context)
    return jsonify({"response": response})

# Twilio WhatsApp Webhook
@app.route('/twilio_webhook', methods=['POST'])
def twilio_webhook():
    phone_number = request.form.get('From')
    message_body = request.form.get('Body')

    if not phone_number or not message_body:
        return "<Response><Message>Error: Phone number and message are required.</Message></Response>", 400, {'Content-Type': 'application/xml'}

    query_type = classify_query(message_body)

    if query_type == "1":
        details = fetch_room_details()
        response_text = generate_response(message_body, details) if details else "No details found for that number."
    elif query_type == "2":
        response_text = generate_response(message_body, HOTEL_INFO)
    else:
        response_text = "Unable to classify your query."

    response = MessagingResponse()
    response.message(response_text)

    return str(response), 200, {'Content-Type': 'application/xml'}

# Run Flask App
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)

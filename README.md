## WhatsApp Chatbot using Flask, Twilio & Groq API:

This is a Flask-based chatbot that integrates with Twilio to handle WhatsApp messages in real-time.
The core functionality is powered by the Groq API, which classifies and generates responses to user queries. 
The app is deployed on Render for seamless hosting and uptime.


## Technologies Used:

- **Backend:** Python, Flask  
- **Messaging Platform:** Twilio (WhatsApp Sandbox)  
- **AI Integration:** Groq API (chat completions)  
- **Deployment:** Render  
- **Configuration:** python-dotenv for environment management  


##  How It Works:

1. A user sends a message to the WhatsApp number connected via Twilio.
2. Twilio forwards this message to the `/twilio_webhook` route on the Flask server.
3. The server sends the message to the Groq API to classify the query and generate a reply.
4. The response is sent back to the user on WhatsApp via Twilio.

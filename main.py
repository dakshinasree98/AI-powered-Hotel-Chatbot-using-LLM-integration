import os
import sqlite3
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Define hotel information constant
HOTEL_INFO = """
Thira Beach Home is a luxurious seaside retreat that seamlessly blends Italian-Kerala heritage architecture with modern luxury, creating an unforgettable experience. Nestled just 150 meters from the magnificent Arabian Sea, our beachfront property offers a secluded and serene escape with breathtaking 180-degree ocean views. 

The accommodations feature Kerala-styled heat-resistant tiled roofs, natural stone floors, and lime-plastered walls, ensuring a perfect harmony of comfort and elegance. Each of our Luxury Ocean View Rooms is designed to provide an exceptional stay, featuring a spacious 6x6.5 ft cot with a 10-inch branded mattress encased in a bamboo-knitted outer layer for supreme comfort.

Our facilities include:
- Personalized climate control with air conditioning and ceiling fans
- Wardrobe and wall mirror
- Table with attached drawer and two chairs
- Additional window bay bed for relaxation
- 43-inch 4K television
- Luxury bathroom with body jets, glass roof, and oval-shaped bathtub
- Total room area of 250 sq. ft.

Modern amenities:
- RO and UV-filtered drinking water
- 24/7 hot water
- Water processing unit with softened water
- Uninterrupted power backup
- High-speed internet with WiFi
- Security with CCTV surveillance
- Electric charging facility
- Accessible design for differently-abled persons

Additional services:
- Yoga classes
- Cycling opportunities
- On-site dining at Samudrakani Kitchen
- Stylish lounge and dining area
- Long veranda with ocean views

Location: Kothakulam Beach, Valappad, Thrissur, Kerala
Contact: +91-94470 44788
Email: thirabeachhomestay@gmail.com
"""

# Load environment variables and configure the app
def init_app():
    logger.info("Starting application initialization...")
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY not found in environment variables")
        raise ValueError("GROQ_API_KEY not found in environment variables. Please check your .env file.")
    
    logger.info("Successfully initialized Groq client")
    return Groq(api_key=api_key)

# Database initialization
def init_database():
    logger.info("Initializing database...")
    try:
        conn = sqlite3.connect('rooms.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS room_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE,
                description TEXT
            )
        ''')
        
        cursor.execute('SELECT COUNT(*) FROM room_data')
        count = cursor.fetchone()[0]
        logger.info(f"Current number of room descriptions in database: {count}")
        
        conn.commit()
        logger.info("Database initialization completed successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        conn.close()

# Connect to the SQLite database
def connect_to_db():
    logger.info("Attempting to connect to database...")
    try:
        conn = sqlite3.connect('rooms.db')
        logger.info("Successfully connected to database")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        st.error(f"Database connection error: {e}")
        return None

# Fetch room details from the database
def fetch_room_details():
    logger.info("Fetching room details...")
    conn = connect_to_db()
    if not conn:
        logger.error("Unable to fetch room details due to connection error")
        return "Unable to fetch room details due to database connection error."
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT title, description FROM room_data')
        results = cursor.fetchall()
        
        if results:
            logger.info(f"Successfully retrieved {len(results)} room descriptions")
            combined_description = "\n\n".join([
                f"Room: {title}\nDescription: {description}" 
                for title, description in results
            ])
            logger.debug(f"Combined descriptions: {combined_description[:100]}...")
            return combined_description
        else:
            logger.warning("No room details found in database")
            return "No room details available."
    except sqlite3.Error as e:
        logger.error(f"Error fetching room details: {e}")
        return f"Error fetching room details: {e}"
    finally:
        conn.close()
        logger.info("Database connection closed")

# Classify the query
def classify_query(client, query):
    logger.info(f"Classifying query: {query[:50]}...")
    try:
        prompt = f"""Classify the following query into one of two categories:
        1. Checking details - if the query is about wanting to book a hotel room
        2. Getting information - if the query is about wanting to know general information related to the hotel.

        Query: {query}
        
        Respond with only the category number (1 or 2)."""
        
        logger.info("Sending classification request to Groq API")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.5,
            top_p=1,
            stop=None,
            stream=False
        )
        result = response.choices[0].message.content.strip()
        logger.info(f"Query classified as type: {result}")
        return result
    except Exception as e:
        logger.error(f"Error classifying query: {e}")
        st.error(f"Error classifying query: {e}")
        return None

# Generate a response
def generate_response(client, query, context):
    logger.info(f"Generating response for query: {query[:50]}...")
    try:
        logger.info("Sending response generation request to Groq API")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are Maya, a friendly and professional hotel receptionist at Thira Beach Home. Your job is to assist guests by providing accurate and helpful information about the hotel, its amenities, and room availability.."},
                {"role": "user", "content": f"Query: {query}\nContext: {context}"}
            ],
            max_tokens=300,
            temperature=0.5,
            top_p=1,
            stop=None,
            stream=False
        )
        result = response.choices[0].message.content
        logger.info("Successfully generated response")
        logger.debug(f"Generated response: {result[:50]}...")
        return result
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return f"Error generating response: {e}"

def main():
    logger.info("Starting main application...")
    st.set_page_config(page_title="Thira Beach Home", page_icon="🏨")
    
    try:
        logger.info("Initializing application components...")
        groq_client = init_app()
        init_database()
        
        st.title("Thira Beach Home")
        st.markdown("---")
        
        st.write("Welcome! Ask any questions about our hotel or room bookings.")
        
       
        
        query = st.text_area("Enter your query:", height=100)
        
        if st.button("Submit Query", type="primary"):
            logger.info("Query submission button clicked")
            
            if not query:
                logger.warning("Empty query submitted")
                st.error("Please enter a query before submitting.")
                return
            
            with st.spinner("Processing your query..."):
                logger.info("Processing query...")
                query_type = classify_query(groq_client, query)
                
                if not query_type:
                    logger.error("Query classification failed")
                    st.error("Failed to classify your query. Please try again.")
                    return
                
                logger.info(f"Processing query type: {query_type}")
                if query_type == "1":
                    room_details = fetch_room_details()
                    logger.info("Generating response with room details")
                    response = generate_response(groq_client, query, room_details)
                elif query_type == "2":
                    logger.info("Generating response with hotel information")
                    response = generate_response(groq_client, query, HOTEL_INFO)
                else:
                    logger.error(f"Invalid query classification: {query_type}")
                    st.error("Invalid query classification. Please try again.")
                    return
                
                logger.info("Displaying response to user")
                st.success("Response:")
                st.write(response)
                
    except Exception as e:
        logger.error(f"Main application error: {e}")
        st.error(f"An error occurred: {e}")
        st.info("Please make sure you have set up your .env file with the GROQ_API_KEY")

if __name__ == "__main__":
    main()

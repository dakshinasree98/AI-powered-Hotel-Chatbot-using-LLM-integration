import sqlite3
import pandas as pd
import streamlit as st

# Streamlit app title
st.title("Room Database Viewer")

# Function to connect to SQLite database and fetch data
def get_data():
    try:
        conn = sqlite3.connect("rooms.db")
        df = pd.read_sql_query("SELECT * FROM room_data", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# Load data
data = get_data()

# Display data in Streamlit app
if not data.empty:
    st.write("### Edit Room Record")
    row = data.iloc[0]
    title = st.text_input("Title", row["title"], key="title")
    description = st.text_area("Description", row["description"], key="description")
    
    if st.button("Save Changes"):
        try:
            conn = sqlite3.connect("rooms.db")
            updated_df = pd.DataFrame([{"title": title, "description": description}])
            updated_df.to_sql("room_data", conn, if_exists="replace", index=False)
            conn.close()
            st.success("Database updated successfully!")
        except Exception as e:
            st.error(f"Error saving data: {e}")
else:
    st.write("No data found in the database.")

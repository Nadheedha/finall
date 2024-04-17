import streamlit as st
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["blooms"]
collection = db["users"]

def registration_page():
    st.title("Registration")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        # Check if the username already exists
        if collection.find_one({"username": username}):
            st.error("Username already exists. Please choose a different username.")
        else:
            # Insert new user into MongoDB
            user_data = {"username": username, "password": password}
            collection.insert_one(user_data)
            st.success("Registration successful. You can now login.")

if __name__ == "__main__":
    registration_page()

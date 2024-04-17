import streamlit as st
import pandas as pd
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["blooms"]
marks_collection = db["student_database"]

def calculate_performance(data):
    # Initialize dictionary to store total marks and scored marks for each K level
    performance = {}
    for row in data:
        _, scored_mark, total_mark, k_level = row
        if k_level not in performance:
            performance[k_level] = {"total_scored_mark": 0, "total_total_mark": 0}
        performance[k_level]["total_scored_mark"] += scored_mark
        performance[k_level]["total_total_mark"] += total_mark
    return performance

def enter_marks():
    st.title("Enter Marks")

    # Input fields
    student_name = st.text_input("Student Name")
    questionpaper_code = st.text_input("Question Paper Code")
    num_rows = st.number_input("Number of Rows", min_value=1, step=1)

    # Table to enter marks
    data = []
    input_table = pd.DataFrame(columns=["Question Number", "Scored Mark", "Total Mark", "K Level"], index=range(num_rows))
    for i in range(num_rows):
        input_table.loc[i, "Question Number"] = st.text_input(f"Question Number {i+1}", key=f"question_number_{i}")
        input_table.loc[i, "Scored Mark"] = st.number_input(f"Scored Mark {i+1}", min_value=0, step=1, key=f"scored_mark_{i}")
        input_table.loc[i, "Total Mark"] = st.number_input(f"Total Mark {i+1}", min_value=0, step=1, key=f"total_mark_{i}")
        input_table.loc[i, "K Level"] = st.selectbox(f"K Level {i+1}", ["K1", "K2", "K3","K4","K5","K6"], key=f"k_level_{i}")
    
    if st.button("Submit"):
        # Extract data from the input table
        data = input_table.values.tolist()

        # Calculate performance
        performance = calculate_performance(data)

        # Store data in MongoDB
        mark_data = {
            "student_name": student_name,
            "questionpaper_code": questionpaper_code,
            "data": data,
            "calculated_performance": performance
        }
        marks_collection.insert_one(mark_data)

        st.success("Marks submitted successfully!")
        st.write("Calculated Performance:", performance)

    # Display entered data in table format
    if data:
        df = pd.DataFrame(data, columns=["Question Number", "Scored Mark", "Total Mark", "K Level"])
        st.write("Entered Data:")
        st.write(df)

if __name__ == "__main__":
    enter_marks()

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["blooms"]
marks_collection = db["student_database"]

def plot_performance(student_name, questionpaper_code):
    # Retrieve data from MongoDB
    query = {
        "student_name": student_name,
        "questionpaper_code": questionpaper_code
    }
    mark_data = marks_collection.find_one(query)

    if mark_data:
        calculated_performance = mark_data["calculated_performance"]
        if calculated_performance:
            # Calculate percentage for each K level
            k_levels = []
            percentages = []
            for k_level, values in calculated_performance.items():
                total_scored_mark = values["total_scored_mark"]
                total_total_mark = values["total_total_mark"]
                percentage = (total_scored_mark / total_total_mark) * 100
                k_levels.append(k_level)
                percentages.append(percentage)

            # Plot bar graph
            plt.figure(figsize=(8, 6))
            plt.bar(k_levels, percentages, color='skyblue')
            plt.xlabel('K Level')
            plt.ylabel('Percentage')
            plt.title('Performance Analysis')
            plt.ylim(0, 100)
            st.pyplot(plt)
        else:
            st.warning("No performance data found for this student.")
    else:
        st.error("No data found for the specified student and question paper code.")

def student_analysis():
    st.title("Student Analysis")

    # Input fields
    student_name = st.text_input("Student Name")
    questionpaper_code = st.text_input("Question Paper Code")

    if st.button("Submit"):
        # Plot performance
        plot_performance(student_name, questionpaper_code)

if __name__ == "__main__":
    student_analysis()

import streamlit as st
from pymongo import MongoClient
import torch
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client.blooms
collection = db.qnpaper2

# Initialize Pinecone
Api_key = "a1a07892-456f-45b1-9694-e13027dc6a8a"
pc = Pinecone(api_key=Api_key)

# Initialize Retriever
device = 'cuda' if torch.cuda.is_available() else 'cpu'
retriever = SentenceTransformer("flax-sentence-embeddings/all_datasets_v3_mpnet-base", device=device)
index_name = "cognitive-levels-3"
index = pc.Index(index_name)

def query_pinecone(query, top_k):
    xq = retriever.encode([query]).tolist()
    xc = index.query(vector=xq, top_k=top_k, include_metadata=True)
    return xc

def classify_questions():
    results = []

    questions_cursor = collection.find({})
    for document in questions_cursor:
        for q in document.get("questions", []):
            question_number = q.get("question_number", "")
            question = q.get("question", "")
            options = q.get("options", "")
            mark = q.get("mark", "")

            if question:
                context = query_pinecone(question, top_k=1)
                if context and "matches" in context:
                    label = context['matches'][0]['metadata'].get("Label", "Not classified")
                else:
                    label = "Not classified"
            else:
                label = "Not classified"

            results.append((question_number, options, question, mark, label))

    return results

def analyze_marks(results):
    bt_level_marks = {}
    total_marks = sum([int(result[-2]) for result in results])  # Total marks
    for result in results:
        bt_level = result[-1]  # Last element is the BT_Level
        mark = int(result[-2])  # Second last element is the mark
        if bt_level in bt_level_marks:
            bt_level_marks[bt_level] += mark
        else:
            bt_level_marks[bt_level] = mark
    
    # Convert marks to percentages
    bt_level_percentages = {bt_level: (marks / total_marks) * 100 for bt_level, marks in bt_level_marks.items()}
    return bt_level_percentages

def bloom_page():
    st.header("Question Classification")

    results = classify_questions()

    if results:
        df = pd.DataFrame(results, columns=["Question Number", "Option", "Question", "Mark", "Label"])
        st.write("Question Data:")
        st.write(df)

        bt_level_percentages = analyze_marks(results)
        st.write("Marks Distribution by BT_Level:")
        st.write(bt_level_percentages)

        # Option to select chart type
        chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Pie Chart"])

        if chart_type == "Bar Chart":
            # Plotting single bar chart
            plt.figure(figsize=(10, 2))
            bt_levels = list(bt_level_percentages.keys())
            percentages = list(bt_level_percentages.values())
            cmap = plt.get_cmap('tab10')
            colors = cmap(np.linspace(0, 1, len(bt_levels)))
            left = 0
            for bt_level, percentage, color in zip(bt_levels, percentages, colors):
                plt.barh(0, percentage, left=left, color=color, label=bt_level)
                left += percentage

                # Add percentage label to the bar
                plt.text(left - percentage / 2, 0, f"{percentage:.1f}%", color='white', va='center', ha='center', fontsize=10)

            plt.xlabel('Percentage of Total Marks')
            plt.ylabel('Bloom\'s Taxonomy Level')
            plt.title('Marks Distribution by BT_Level (Bar Chart)')
            plt.legend(loc='upper right')
            plt.xlim(0, 100)
            plt.xticks([])
            plt.yticks([])

            st.write("Bar Chart:")
            st.pyplot(plt)

        elif chart_type == "Pie Chart":
            # Plotting pie chart
            plt.figure(figsize=(8, 8))
            bt_levels = list(bt_level_percentages.keys())
            percentages = list(bt_level_percentages.values())
            cmap = plt.get_cmap('tab10')
            colors = cmap(np.linspace(0, 1, len(bt_levels)))
            plt.pie(percentages, labels=bt_levels, autopct='%1.1f%%', colors=colors, startangle=140)
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.title('Marks Distribution by BT_Level (Pie Chart)')
            st.write("Pie Chart:")
            st.pyplot(plt)

    else:
        st.write("No questions found in the database.")

if __name__ == "__main__":
    bloom_page()

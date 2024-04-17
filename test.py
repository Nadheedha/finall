import streamlit as st
import pandas as pd

def editable_table(df):
    # Convert DataFrame to HTML table
    table = df.to_html(escape=False, index=False, header=True)

    # Display table as HTML
    st.components.v1.html(
        f"""
        <div contenteditable="true" class="editable-table">
            {table}
        </div>
        <style>
            .editable-table {{
                border-collapse: collapse;
                width: 100%;
            }}
            .editable-table th, .editable-table td {{
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }}
            .editable-table th {{
                background-color: #f2f2f2;
            }}
        </style>
        """,
        height=500
    )

def main():
    st.title("Editable Table Example")

    # Create an empty DataFrame with columns
    df = pd.DataFrame(columns=["Question Number", "Scored Mark", "Total Mark", "K Level"])

    # Add an empty row to start
    df.loc[0] = ["", "", "", ""]

    # Display editable table
    editable_table(df)

if __name__ == "__main__":
    main()

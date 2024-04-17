import streamlit as st
import dashboard
import bloom
import students_analysis

# Page names
pages = ["Welcome", "Identify Cognitive Level", "Enter Marks", "Analyze Performance"]

# Flag to control the execution of st.write
enable_write = True

def main():
    global enable_write

    st.title("Dashboard")

    # Add a style block to set the page background color

    # Sidebar
    st.sidebar.title("Navigation")

    # Selectbox to choose page
    selected_page = st.sidebar.selectbox("Select Page", pages)

    # Conditional rendering based on selected page
    if selected_page == "Welcome":
        enable_write = True
    elif selected_page == "Identify Cognitive Level":
        bloom.bloom_page()
        enable_write = False
    elif selected_page == "Enter Marks":
        dashboard.enter_marks()
        enable_write = False
    elif selected_page == "Analyze Performance":
        students_analysis.student_analysis()
        enable_write = False

    # Main content
    st.header("Welcome to the Dashboard")

    if selected_page == "Welcome" or enable_write:
        st.write("""
        This is a dashboard where you can perform various tasks related to student assessments.
        """)

        st.write("""
        ## About Identifying Cognitive Level
        In this section, you can analyze the cognitive level of questions to understand their complexity and depth.

        ## About Entering Marks
        In the Enter Marks section, you can input the marks obtained by students for various assessments.

        ## About Analyzing Performance
        The Analyze Performance section allows you to analyze the performance of students based on the entered marks and other metrics.
        """)

if __name__ == "__main__":
    main()

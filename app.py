import streamlit as st
import lab1
import lab2
import lab3
import lab4

# Title for the main page
st.title('Simple Streamlit App')

# Sidebar selection
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", ["Home", "Lab 1", "Lab 2", "Lab 3", "Lab 4"])

# Home Page
if selection == "Home":
    st.write("""
    ## Welcome to the Dhruv's Streamlit Labs App
    Use the sidebar to navigate to different labs.
    """)

# Lab 1 Page
elif selection == "Lab 1":
    lab1.run()

# Lab 2 Page
elif selection == "Lab 2":
    lab2.run()

# Lab 3 Page
elif selection == "Lab 3":
    lab3.run()

elif selection == "Lab 4":
    lab4.run()
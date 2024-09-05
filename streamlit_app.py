import streamlit as st
import lab1
import lab2

# Title of the app
st.title("Lab Navigator")

# Create a simple navigation using radio buttons or a selectbox
selected_lab = st.radio("Select a Lab", ['Lab 1', 'Lab 2'])

# Display the corresponding lab based on the selection
if selected_lab == 'Lab 1':
    lab1.show_lab()

elif selected_lab == 'Lab 2':
    lab2.show_lab()

import streamlit as st
import pandas as pd
import os
import hashlib

# File paths
user_file = 'users.csv'
data_file = 'truck_data.csv'

# Initialize user_data and truck_data as empty dictionaries
user_data = {}
truck_data = {}

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to create an empty users.csv file with headers
def create_user_file():
    pd.DataFrame(columns=["Username", "Password"]).to_csv(user_file, index=False)

# Function to create an empty truck_data.csv file with headers
def create_data_file():
    pd.DataFrame(columns=["Truck Number", "Driver's Name", "Driver's Id", "Contact Number", "Registration Date", "Weight", "Area", "Username"]).to_csv(data_file, index=False)

# Check if the user file exists
if not os.path.exists(user_file):
    create_user_file()

# Load existing user data
if os.path.exists(user_file):
    try:
        user_data = pd.read_csv(user_file).set_index('Username').to_dict(orient='index')
    except pd.errors.EmptyDataError:
        create_user_file()

# Check if the truck data file exists
if not os.path.exists(data_file):
    create_data_file()

# Load existing truck data
if os.path.exists(data_file):
    try:
        truck_data_df = pd.read_csv(data_file)
        if not truck_data_df.empty and "Truck Number" in truck_data_df.columns:
            truck_data = truck_data_df.to_dict(orient='index')
    except pd.errors.EmptyDataError:
        create_data_file()

# Streamlit app interface
st.title("🚚 Truck Registration and Login System")
st.write("Welcome to the **Truck Registration System**. You can create an account, log in, and manage trucks easily!")

# Session state management
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# Sign Up and Login tabs
tab1, tab2 = st.tabs(["📝 Sign Up", "🔑 Login"])

# Sign Up tab
with tab1:
    st.subheader("Create a New Account")
    new_username = st.text_input("👤 Username", key="register_username")
    new_password = st.text_input("🔒 Password", type="password", key="register_password")

    if st.button("Create Account", key="register_button"):
        if new_username in user_data:
            st.error("Username already exists.")
        elif new_username and new_password:
            user_data[new_username] = {"Password": hash_password(new_password)}
            pd.DataFrame.from_dict(user_data, orient='index').reset_index().rename(columns={"index": "Username"}).to_csv(user_file, index=False)
            st.session_state.logged_in = True
            st.session_state.current_user = new_username
            st.success("Account registered successfully!")
        else:
            st.error("Please fill out both fields.")

# Login tab
with tab2:
    st.subheader("Log in to Your Account")
    username = st.text_input("👤 Username", key="login_username")
    password = st.text_input("🔒 Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        if username in user_data and user_data[username]["Password"] == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.success(f"Welcome, {username}!")
        else:
            st.error("Invalid username or password.")

# If logged in, show truck registration form
if st.session_state.logged_in:
    st.subheader("🚛 Register a New Truck")
    truck_number = st.text_input("🚚 Truck Number")
    driver_name = st.text_input("👨‍✈️ Driver's Name")
    driver_id = st.text_input("👨‍✈️ Driver's ID")
    contact_number = st.text_input("📞 Contact Number")
    registration_date = st.date_input("📅 Registration Date")
    weight = st.number_input("Weight (tons)", min_value=0.0)
    area = st.text_input("Area where truck was weighed")

    if st.button("Register Truck"):
        if truck_number and driver_name and driver_id and contact_number:
            truck_data[truck_number] = {
                "Driver's Name": driver_name,
                "Driver's Id": driver_id,
                "Contact Number": contact_number,
                "Registration Date": registration_date,
                "Weight": weight,
                "Area": area,
                "Username": st.session_state.current_user,
            }
            truck_data_df = pd.DataFrame.from_dict(truck_data, orient='index').reset_index().rename(columns={"index": "Truck Number"})
            truck_data_df.to_csv(data_file, index=False)
            st.success(f"Truck {truck_number} registered successfully!")
        else:
            st.error("Please fill out all fields.")

    # Display registered trucks for the logged-in user
    st.subheader(f"🚛 Registered Trucks for {st.session_state.current_user}")
    user_trucks = {truck: details for truck, details in truck_data.items() if details.get("Username") == st.session_state.current_user}
    
    if user_trucks:
        for truck, details in user_trucks.items():
            st.write(f"**🚚 Truck Number:** {truck}")
            st.write(f"**👨‍✈️ Driver's Name:** {details['Driver\'s Name']}")
            st.write(f"**👨‍✈️ Driver's Id:** {details['Driver\'s Id']}")
            st.write(f"**📞 Contact Number:** {details['Contact Number']}")
            st.write(f"**📅 Registration Date:** {details['Registration Date']}")
            st.write(f"**Weight:** {details['Weight']} tons")
            st.write(f"**Area:** {details['Area']}")
            st.write("---")
    else:
        st.write("No trucks registered yet.")

# Logout button
if st.session_state.logged_in:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.success("Logged out successfully!")

from asyncio import sleep
import streamlit as st
from pymongo import MongoClient
import bcrypt
import uuid
import dashboard
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string

class MongoDBAuthenticator:
    def __init__(self, db_url, db_name):
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]
        self.users_collection = self.db['users']
        self.smtp_server = 'smtp.gmail.com'  # SMTP server address
        self.smtp_port = '587'  # SMTP server port
        self.smtp_username = 'nadheedha31@gmail.com' # SMTP server username
        self.smtp_password = 'ewdh vlcl yqrf qmht'  # SMTP server password

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password

    def generate_otp(self, length=6):
        """Generate a random OTP of the specified length."""
        return ''.join(random.choices(string.digits, k=length))

    def create_user(self, email, password, otp):

        hashed_password = self.hash_password(password)
        verification_token = str(uuid.uuid4())  # Generate a unique verification token
        user = {
            'email': email,
            'password': hashed_password,
            'verified': False,
            'verification_token': verification_token,
            'otp': otp  # Store OTP
        }
        self.users_collection.insert_one(user)
        self.send_verification_email(email, otp)

    def send_verification_email(self, email, otp):
        smtp_server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        smtp_server.starttls()
        smtp_server.login(self.smtp_username, self.smtp_password)

        message = MIMEMultipart()
        message['From'] = self.smtp_username
        message['To'] = email
        message['Subject'] = 'Email Verification'
        body = f'Your OTP for verification is: {otp}'
        message.attach(MIMEText(body, 'plain'))

        smtp_server.sendmail(self.smtp_username, email, message.as_string())
        smtp_server.quit()

    def handle_unverified_user(self, email):
        st.error("Your email is not verified. Please click the 'Verify Email' button below to verify your email.")
        if st.button("Verify Email"):
            otp = self.generate_otp()  # Generate OTP
            self.send_verification_email(email, otp)
            st.success("An OTP has been sent to your email. Please enter the OTP below to complete verification.")
            st.session_state['email'] = email
            st.session_state['otp'] = otp

    def authenticate_user(self, email, password):
        user = self.users_collection.find_one({"email": email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            if user['verified']:
                return True
            else:
                #self.handle_unverified_user(email)
                st.error("Ypur account hasnt been verified")
        return False

    def verify_otp(self, email, otp):
        user = self.users_collection.find_one({"email": email})
        print(f"User: {user}")
        print(f"OTP: {otp}")
        if user and user['otp'] == otp:
            self.users_collection.update_one({"email": email}, {"$set": {"verified": True}})
            return True
        return False


def login():
    st.header("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticator.authenticate_user(email, password):
            st.experimental_set_query_params(logged_in=True)
            st.success("Login successful!")
            sleep(0.5)
            dashboard.dashboard(email)
            return True  # Indicate successful login
        else:
            st.error("Invalid email or password.")
st.set_page_config(page_title="User Authentication App", page_icon=":guardsman:", layout="wide")

# Initialize session state variables
if 'email' not in st.session_state:
    st.session_state['email'] = None
if 'otp' not in st.session_state:
    st.session_state['otp'] = None

def register():
    st.header("Register")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register", key="register_btn"):
        if authenticator.users_collection.find_one({"email": email}):
            st.error("Email already registered.")
            return
        otp = authenticator.generate_otp()  # Generate OTP
        authenticator.create_user(email, password, otp)
        st.success("An OTP has been sent to your email. Please enter the OTP below to complete registration.")
        st.session_state['email'] = email
        st.session_state['otp'] = otp

def verify_otp():
    if st.session_state['email'] is not None and st.session_state['otp'] is not None:
        otp = st.text_input("Enter OTP", key="entered_otp")
        if otp:
            if authenticator.verify_otp(st.session_state['email'], otp):
                st.success("Registration successful! Your email has been verified.")
                st.session_state['email'] = None
                st.session_state['otp'] = None
            else:
                st.error("Invalid OTP. Please enter the correct OTP")

def main():
    st.title("User Authentication App")

    choice = st.sidebar.radio("Select Option", ("Login", "Register"))

    if choice == "Login":
        if login():
            st.empty()
    elif choice == "Register":
        register()
        verify_otp()

if __name__ == "__main__":
    # Initialize MongoDBAuthenticator
    authenticator = MongoDBAuthenticator("mongodb://localhost:27017", "blooms")
    main()
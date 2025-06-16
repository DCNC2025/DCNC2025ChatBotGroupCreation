import boto3
import os
from dotenv import load_dotenv
import json
import re
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import streamlit as st

# Load .env file values
load_dotenv()
print("SENDGRID_API_KEY:", os.getenv("SENDGRID_API_KEY"))
print("SENDER_EMAIL:", os.getenv("SENDER_EMAIL"))
# File to store user data
USERS_FILE = "data/users.json"
OTP_FILE = "data/otp.json"
# SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
# SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]
SENDER_EMAIL = st.secrets["SENDER_EMAIL"]
def get_aws_credentials_from_cognito():
    region = os.getenv("AWS_REGION")
    username = os.getenv("COGNITO_USERNAME")
    password = os.getenv("COGNITO_PASSWORD")
    client_id = os.getenv("AWS_APP_CLIENT_ID")
    user_pool_id = os.getenv("AWS_USER_POOL_ID")
    identity_pool_id = os.getenv("AWS_IDENTITY_POOL_ID")

    # Step 1: Authenticate with Cognito User Pool using USER_PASSWORD_AUTH
    idp_client = boto3.client("cognito-idp", region_name=region)
    try:
        response = idp_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
            },
            ClientId=client_id,
        )
    except idp_client.exceptions.NotAuthorizedException:
        raise Exception("❌ Cognito authentication failed. Check your username/password.")

    id_token = response["AuthenticationResult"]["IdToken"]

    # Step 2: Exchange token for temporary AWS credentials via Identity Pool
    identity_client = boto3.client("cognito-identity", region_name=region)
    identity_id = identity_client.get_id(
        IdentityPoolId=identity_pool_id,
        Logins={f"cognito-idp.{region}.amazonaws.com/{user_pool_id}": id_token}
    )["IdentityId"]

    credentials = identity_client.get_credentials_for_identity(
        IdentityId=identity_id,
        Logins={f"cognito-idp.{region}.amazonaws.com/{user_pool_id}": id_token}
    )["Credentials"]

    return credentials

def validate_email(email: str, role: str) -> Tuple[bool, str]:
    """
    Validate email based on role requirements
    Returns: (is_valid, error_message)
    """
    if role.lower() == "student":
        # Student email must start with 's' and end with @student.rmit.edu.au
        if not email.lower().startswith('s'):
            return False, "Student email must start with 's'"
        if not email.lower().endswith('@student.rmit.edu.au'):
            return False, "Student email must end with @student.rmit.edu.au"
    else:  # staff
        if not email.lower().endswith('@rmit.edu.au'):
            return False, "Staff email must end with @rmit.edu.au"
    
    return True, ""

def load_users() -> Dict:
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_users(users: Dict):
    """Save users to JSON file"""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def create_user(email: str, password: str, role: str) -> Tuple[bool, str]:
    """
    Create a new user
    Returns: (success, message)
    """
    # Validate email
    is_valid, error_msg = validate_email(email, role)
    if not is_valid:
        return False, error_msg

    # Load existing users
    users = load_users()
    
    # Check if user already exists
    if email in users:
        return False, "User already exists"
    
    # Create new user
    users[email] = {
        "password": password,  # In production, this should be hashed
        "role": role.lower(),
        "created_at": str(datetime.now())
    }
    
    # Save users
    save_users(users)
    return True, "User created successfully"

def authenticate_user(email: str, password: str) -> Tuple[bool, str, Optional[str]]:
    """
    Authenticate a user
    Returns: (success, message, role)
    """
    users = load_users()
    
    if email not in users:
        return False, "User not found", None
    
    user = users[email]
    if user["password"] != password:  # In production, this should compare hashed passwords
        return False, "Invalid password", None
    
    return True, "Login successful", user["role"]

def generate_otp(length: int = 6) -> str:
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def send_otp_email(email: str, otp: str) -> bool:
    try:
        import streamlit as st
        api_key = st.secrets.get("SENDGRID_API_KEY")
        sender_email = st.secrets.get("SENDER_EMAIL")
    except Exception as e:
        print(f"[ERROR] Failed to load Streamlit secrets: {e}")
        return False

    message = Mail(
        from_email=sender_email,
        to_emails=email,
        subject='Your RMIT Verification Code',
        html_content=f'<strong>Your verification code is: {otp}</strong>'
    )
    try:
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        return True
    except Exception as e:
        print(f"SendGrid error: {e}")
        return False


def store_otp(email: str, otp: str):
    otps = {}
    if os.path.exists(OTP_FILE):
        with open(OTP_FILE, 'r') as f:
            try:
                otps = json.load(f)
            except json.JSONDecodeError:
                otps = {}
    otps[email] = {"otp": otp, "expires": (datetime.now() + timedelta(minutes=5)).isoformat()}
    with open(OTP_FILE, 'w') as f:
        json.dump(otps, f)

def verify_otp(email: str, otp: str) -> bool:
    if not os.path.exists(OTP_FILE):
        return False
    with open(OTP_FILE, 'r') as f:
        try:
            otps = json.load(f)
        except json.JSONDecodeError:
            return False
    if email not in otps:
        return False
    otp_data = otps[email]
    if otp_data["otp"] != otp:
        return False
    if datetime.fromisoformat(otp_data["expires"]) < datetime.now():
        return False
    return True

def reset_password(email: str, new_password: str) -> Tuple[bool, str]:
    users = load_users()
    if email not in users:
        return False, "User not found"
    users[email]["password"] = new_password
    save_users(users)
    return True, "Password reset successful"

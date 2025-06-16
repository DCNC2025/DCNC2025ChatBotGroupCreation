import streamlit as st
import utils.auth as auth
from dotenv import load_dotenv
import os
import time
import base64
load_dotenv()

SENDGRID_API_KEY = st.secrets.get("SENDGRID_API_KEY") or os.getenv("SENDGRID_API_KEY")

# Function to get logo as base64
def get_logo_base64():
    try:
        with open("Rmit logo.png", "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        print("RMIT Logo image not found. Please ensure 'Rmit logo.png' is in the root directory.")
        return None

st.set_page_config(
    page_title="RMIT Group Formation Login 🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide sidebar and multipage nav during login
st.markdown("""
    <style>
    [data-testid="stSidebar"], .css-1lcbmhc.e1fqkh3o3 { display: none !important; }
    
    /* Remove top white bar */
    .stApp > header {
        display: none !important;
    }
    
    /* Remove default padding at the top */
    .main .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    /* Global styles */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stApp {
        background-color: #f0f2f5;
        background-image: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
    }
    .main {
        padding: 2rem;
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 1rem;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Card styling */
    .card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-out;
    }
    
    .card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transform: translateY(-3px);
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #e60028 0%, #d10024 100%);
        color: white;
        font-weight: 700;
        border-radius: 12px;
        border: none;
        padding: 0.7rem 1.4rem;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        box-shadow: 0 4px 10px rgba(230, 0, 40, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
        font-size: 1rem;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    .stButton button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: all 0.5s ease;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #ff0030 0%, #e60028 100%);
        box-shadow: 0 6px 15px rgba(230, 0, 40, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        transform: translateY(-3px) scale(1.02);
        color: white;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        font-weight: 800;
    }
    
    .stButton button:hover::before {
        left: 100%;
    }
    
    .stButton button:active {
        transform: translateY(1px) scale(0.98);
        box-shadow: 0 2px 5px rgba(230, 0, 40, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        background: linear-gradient(135deg, #d10024 0%, #b8001f 100%);
    }
    
    /* Role selection buttons */
    [data-testid="stHorizontalBlock"] .stButton button {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 80px;
        font-size: 1.2rem;
        font-weight: 700;
        border-radius: 15px;
        background: linear-gradient(135deg, #e60028 0%, #b8001f 100%);
        box-shadow: 0 8px 20px rgba(230, 0, 40, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
    }
    
    [data-testid="stHorizontalBlock"] .stButton button:hover {
        transform: translateY(-5px) scale(1.03);
        box-shadow: 0 12px 25px rgba(230, 0, 40, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        background: linear-gradient(135deg, #ff0030 0%, #e60028 100%);
        color: white;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        font-weight: 800;
    }
    
    /* Input field styling */
    input[type="text"] {
        border-radius: 8px !important;
        border: 2px solid #e1e4e8 !important;
        padding: 10px 15px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: none !important;
    }
    
    input[type="text"]:focus {
        border-color: #e60028 !important;
        box-shadow: 0 0 0 3px rgba(230, 0, 40, 0.1) !important;
    }
    
    /* Label styling */
    .stTextInput label, .stSelectbox label {
        font-weight: 500 !important;
        color: #333 !important;
        font-size: 14px !important;
        margin-bottom: 5px !important;
    }
    
    /* Success and error message styling */
    .stSuccess, .stError {
        border-radius: 10px !important;
        padding: 12px 20px !important;
        animation: slideIn 0.3s ease-out !important;
    }
    </style>
""", unsafe_allow_html=True)


if 'auth_stage' not in st.session_state:
    st.session_state.auth_stage = 'role_select'
if 'auth_role' not in st.session_state:
    st.session_state.auth_role = None
if 'auth_email' not in st.session_state:
    st.session_state.auth_email = ''
if 'otp_sent_time' not in st.session_state:
    st.session_state.otp_sent_time = 0


# Helper to reset auth navigation
def reset_auth():
    st.session_state.auth_stage = 'role_select'
    st.session_state.auth_role = None
    st.session_state.auth_email = ''
    st.session_state.otp_sent_time = 0

def show_logo_banner():
    logo_base64 = get_logo_base64()
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" width="120px" style="margin-bottom: 1rem; animation: pulse 2s infinite ease-in-out;">' if logo_base64 else ''
    
    st.markdown(f"""
        <div style='display: flex; flex-direction: column; justify-content: center; align-items: center; margin-bottom: 1.5rem; animation: fadeIn 0.8s ease-out;'>
            {logo_html}
            <div style='background: linear-gradient(135deg, #e60028 30%, #7b1fa2 100%); padding: 1.5rem 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); color: white; text-align: center; width: 100%; transition: all 0.3s ease;'>
                <h1 style='margin: 0; font-size: 1.8rem; text-shadow: 0 2px 4px rgba(0,0,0,0.1); line-height: 1.2;'>RMIT Group Formation Assistant</h1>
                <div style='font-size: 1rem; margin-top: 0.5rem; opacity: 0.9;'>Login Portal</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def show_role_select():
    show_logo_banner()
    st.write("")
    
    st.markdown("""
        <div style='text-align: center; margin-bottom: 1rem; animation: fadeIn 0.6s ease-out;'>
            <h2 style='font-size: 1.3rem; color: #333; font-weight: 600;'>Select your role to continue</h2>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("👨‍🎓 Student", use_container_width=True, key="student_btn"):
            st.session_state.auth_role = 'student'
            st.session_state.auth_stage = 'email_input'
            st.rerun()
    with col2:
        if st.button("👨‍🏫 Staff", use_container_width=True, key="staff_btn"):
            st.session_state.auth_role = 'staff'
            st.session_state.auth_stage = 'email_input'
            st.rerun()

def show_email_input():
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 1rem; animation: fadeIn 0.6s ease-out;'>
            <h2 style='font-size: 1.5rem; color: #333; font-weight: 600;'>{st.session_state.auth_role.capitalize()} Login</h2>
            <p style='color: #666; margin-top: 0.3rem;'>Enter your RMIT email address to receive a verification code</p>
        </div>
    """, unsafe_allow_html=True)
    
    
    
    email = st.text_input("Email Address", key="login_email", placeholder="Enter your RMIT email")
    send_code = st.button("SEND VERIFICATION CODE", use_container_width=True)
    if send_code:
        # Validate email format
        if st.session_state.auth_role == 'student':
            if not (email.lower().endswith('@student.rmit.edu.au') or email.lower().endswith('@rmit.edu.au')):
                st.error("Email must be a valid RMIT address")
                return

        else:
            if not email.lower().endswith('@rmit.edu.au'):
                st.error("Email must be a valid staff RMIT address")
                return
        # Send verification code
        otp = auth.generate_otp()
        auth.store_otp(email, otp)
        sent = auth.send_otp_email(email, otp)
        if sent:
            st.session_state.auth_email = email
            st.session_state.auth_stage = 'verify_code'
            st.session_state.otp_sent_time = int(time.time())
            st.rerun()
        else:
            st.error("Failed to send verification code. Please try again later.")
    
    st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
    st.button("← BACK", key="back_email", on_click=reset_auth)

def show_verify_code():
    st.markdown("""
        <div style='display: flex; flex-direction: column; align-items: center; margin-top: 1rem; animation: fadeIn 0.6s ease-out;'>
            <h2 style='font-size: 1.6rem; font-weight: 700; margin-bottom: 0.6rem; color: #222; text-align: center;'>Enter Verification Code</h2>
            <p style='color: #666; text-align: center; margin-bottom: 1rem;'>A verification code has been sent to your email</p>
        </div>
    """, unsafe_allow_html=True)
    
    
    # Display masked email for privacy
    email = st.session_state.auth_email
    masked_email = email[:3] + "*" * (email.find("@") - 3) + email[email.find("@"):]
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 0.8rem;'>
            <p style='color: #666;'>Code sent to: <strong>{masked_email}</strong></p>
        </div>
    """, unsafe_allow_html=True)
    
    code = st.text_input("Verification Code", key="otp_input", placeholder="Enter 6-digit code")
    now = int(time.time())
    seconds_left = max(0, 180 - (now - st.session_state.otp_sent_time))
    resend_disabled = seconds_left > 0
    minutes = seconds_left // 60
    seconds = seconds_left % 60
    
    if 'otp_error' not in st.session_state:
        st.session_state.otp_error = ''
    if st.session_state.otp_error:
        st.error(st.session_state.otp_error)
        
    verify = st.button("VERIFY AND LOGIN", key="verify_btn", use_container_width=True)
    
    # Timer display with better styling
    if resend_disabled:
        st.markdown(f"""
            <div style='text-align: center; margin: 0.8rem 0;'>
                <p style='color: #666; font-size: 0.9rem;'>Resend code in <span style='font-weight: bold; color: #e60028;'>{minutes:02d}:{seconds:02d}</span></p>
            </div>
        """, unsafe_allow_html=True)
    
    resend = st.button("RESEND CODE" if not resend_disabled else "RESEND CODE", key="resend_btn", disabled=resend_disabled)
    
    st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
    st.button("← BACK", key="back_verify", on_click=lambda: setattr(st.session_state, 'auth_stage', 'email_input'))
    if verify:
        if auth.verify_otp(st.session_state.auth_email, code):
            st.session_state.user_info = {"email": st.session_state.auth_email, "role": st.session_state.auth_role}
            st.session_state.auth_stage = None
            st.session_state.auth_role = None
            st.session_state.auth_email = None
            st.session_state.otp_sent_time = 0
            st.session_state.otp_error = None
            if st.session_state.user_info["role"] == 'student':
                st.success("Login successful! Redirecting to student portal...")
                st.switch_page('pages/app.py')
            else:
                st.success("Login successful! Redirecting to staff portal...")
                st.switch_page('pages/staff.py')
            st.stop()
        else:
            st.session_state.otp_error = "Invalid or expired verification code. Please try again."
            st.rerun()
    if resend and not resend_disabled:
        otp = auth.generate_otp()
        auth.store_otp(st.session_state.auth_email, otp)
        sent = auth.send_otp_email(st.session_state.auth_email, otp)
        if sent:
            st.session_state.otp_sent_time = int(time.time())
            st.success("Verification code resent to your email.")
            st.rerun()
        else:
            st.error("Failed to resend verification code. Please try again later.")
    
    
    # Auto-refresh the timer every second
    if resend_disabled:
        st.rerun()

def show_login_flow():
    if st.session_state.auth_stage == 'role_select':
        show_role_select()
        st.stop()
    elif st.session_state.auth_stage == 'email_input':
        show_logo_banner()
        show_email_input()
        st.stop()
    elif st.session_state.auth_stage == 'verify_code':
        show_logo_banner()
        show_verify_code()
        st.stop()

def main():
    show_login_flow()

if __name__ == "__main__":
    main()
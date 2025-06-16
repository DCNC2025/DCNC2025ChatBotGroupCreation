import streamlit as st
import os
import json
import utils.helpers as helpers
import streamlit.components.v1 as components
from features.group_management import (
    display_groups_for_assignment,
    create_group_for_user,
    join_group_for_user,
    delete_or_exit_group_for_user,
    get_group_list_as_text
)
from dotenv import load_dotenv
import base64
load_dotenv()

# Function to get logo as base64
def get_logo_base64():
    try:
        with open("Rmit logo.png", "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        # st.error("RMIT Logo image not found. Please ensure 'Rmit logo.png' is in the root directory.")
        print("RMIT Logo image not found. Please ensure 'Rmit logo.png' is in the root directory.") # Print to console instead of st.error before st is fully set up
        return None

# Initialize session state variables if not already present
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'page' not in st.session_state:
    st.session_state.page = 'Login'
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_selection' not in st.session_state:
    st.session_state.current_selection = None

st.set_page_config(
    page_title="RMIT Group Formation Assistant 🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme configuration
PRIMARY_COLOR = "#e60028"  # RMIT Red
SECONDARY_COLOR = "#000000" # RMIT Black
BACKGROUND_COLOR = "#f0f2f5" # Modern light grey background
TEXT_COLOR = "#333333" # Darker text for better contrast
SECONDARY_TEXT_COLOR = "#4A5568" # Modern grey text
ACCENT_COLOR = "#007bff" # Blue accent for highlights
TERTIARY_COLOR = "#f8f9fa" # Light grey for subtle elements
FONT_FAMILY = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"

# Custom CSS
st.markdown(f"""
<style>
/* Global styles */
body {{
    font-family: {FONT_FAMILY};
}}
.stApp {{
    background-color: {BACKGROUND_COLOR};
}}
.main {{
    padding: 2rem;
    background-color: #ffffff;
    border-radius: 15px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    margin: 1rem;
}}

/* Modern Sidebar Styling */
[data-testid="stSidebar"] {{
    background: linear-gradient(135deg, rgba(255, 255, 255, 1), rgba(245, 245, 245, 0.95)) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    border-right: 1px solid rgba(0, 0, 0, 0.1) !important;
    box-shadow: 5px 0 15px rgba(0, 0, 0, 0.05) !important;
}}

[data-testid="stSidebar"] > div {{
    padding: 1rem 1rem !important;
}}

/* Sidebar Heading Styling */
[data-testid="stSidebar"] h3 {{
    color: #000000 !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    margin-top: 1rem !important;
    margin-bottom: 0.7rem !important;
    padding-bottom: 0.3rem !important;
    border-bottom: 2px solid {PRIMARY_COLOR} !important;
    position: relative !important;
}}

[data-testid="stSidebar"] h3::after {{
    content: '' !important;
    position: absolute !important;
    bottom: -1px !important;
    left: 0 !important;
    width: 30px !important;
    height: 1px !important;
    background: linear-gradient(90deg, {PRIMARY_COLOR}, {ACCENT_COLOR}) !important;
}}

/* Sidebar Content Styling */
[data-testid="stSidebar"] ul {{
    list-style-type: none !important;
    padding-left: 0 !important;
}}

[data-testid="stSidebar"] li {{
    margin-bottom: 0.5rem !important;
}}

/* Sidebar Section Styling */
.sidebar-section {{
    margin-bottom: 1.2rem !important;
    padding-bottom: 0.7rem !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05) !important;
    display: block !important;
    width: 100% !important;
    clear: both !important;
}}

/* User Profile Card Styling */
.user-profile-card {{
    display: flex !important;
    align-items: center !important;
    background: linear-gradient(135deg, rgba(255, 255, 255, 1), rgba(245, 245, 245, 0.9)) !important;
    border-radius: 8px !important;
    padding: 0.6rem !important;
    margin: 0.7rem 0 !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08) !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    transition: all 0.3s ease !important;
}}

.user-profile-card:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.05) !important;
}}

.user-avatar {{
    font-size: 1.5rem !important;
    background: linear-gradient(135deg, {PRIMARY_COLOR}, {ACCENT_COLOR}) !important;
    color: white !important;
    width: 35px !important;
    height: 35px !important;
    border-radius: 50% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin-right: 0.7rem !important;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08) !important;
    text-align: center !important;
    line-height: 35px !important;
}}

.user-details {{
    flex: 1 !important;
}}

.user-name {{
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    color: #000000 !important;
    margin-bottom: 0.1rem !important;
}}

.user-role {{
    font-size: 0.75rem !important;
    color: #333333 !important;
    opacity: 1 !important;
}}

/* Session Info Styling */
.session-info {{
    background: rgba(255, 255, 255, 0.9) !important;
    border-radius: 6px !important;
    padding: 0.5rem !important;
    margin: 0.4rem 0 0.7rem 0 !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
}}

.info-item {{
    display: flex !important;
    # justify-content: space-between !important;
    align-items: center !important;
    margin-bottom: 0.3rem !important;
    font-size: 1.1rem !important;
}}

.info-label {{
    color: #000000 !important;
    font-weight: 500 !important;
}}

.info-value {{
    color: #000000 !important;
    font-weight: 600 !important;
    background: rgba(255, 255, 255, 0.9) !important;
    padding: 0.1rem 0.3rem !important;
    border-radius: 3px !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
}}

/* Sidebar Button Styling */
[data-testid="stSidebar"] .stButton > button {{
    width: 100% !important;
    text-align: left !important;
    background: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    border-radius: 6px !important;
    margin-bottom: 0.3rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    position: relative !important;
    overflow: hidden !important;
    padding: 0.4rem 0.7rem !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    color: #000000 !important;
}}

[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255, 255, 255, 0.9) !important;
    border-color: {PRIMARY_COLOR} !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05) !important;
}}

[data-testid="stSidebar"] .stButton > button:before {{
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 3px !important;
    height: 100% !important;
    background: linear-gradient(to bottom, {PRIMARY_COLOR}, {ACCENT_COLOR}) !important;
    opacity: 0 !important;
    transition: opacity 0.2s ease !important;
}}

[data-testid="stSidebar"] .stButton > button:hover:before {{
    opacity: 1 !important;
}}

/* Logo styling */
.logo-container {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-bottom: 2.5rem;
    padding-top: 1rem;
}}
.logo-container img {{
    height: 70px;
    max-width: 100%;
    background: transparent !important;
    margin-bottom: 0.5rem;
}}
.logo-text {{
    font-size: 1.2em;
    font-weight: bold;
    color: {TEXT_COLOR};
    text-align: center;
}}

/* Chat message styling */
.st-emotion-cache-1v0mbdj.e115fcil1,
[data-testid="chatAvatarIcon-assistant"] + div {{
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin: 0.8rem 0;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    border: 1px solid #e0e0e0;
}}
[data-testid="chatAvatarIcon-user"] + div {{
    background-color: #e7f3ff;
    border-left: 5px solid {ACCENT_COLOR};
}}
[data-testid="chatAvatarIcon-assistant"] + div {{
    background-color: {TERTIARY_COLOR};
    border-left: 5px solid {PRIMARY_COLOR};
}}

/* Button styling */
.stButton>button {{
    border: none;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    background-color: {PRIMARY_COLOR};
    color: white !important;
    transition: all 0.2s ease-in-out;
    font-weight: 600;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}
.stButton>button:hover {{
    background-color: #c00020;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}}
.stButton>button:active {{
    transform: translateY(0px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}

/* Sidebar styling */
[data-testid="stSidebar"] > div:first-child {{
    background-color: #ffffff;
    padding: 1.5rem;
    border-right: 1px solid #e0e0e0;
}}
.sidebar-section {{
    background-color: {TERTIARY_COLOR};
    padding: 1.2rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
    border: 1px solid #e0e0e0;
}}
.sidebar-section h3 {{
    color: {PRIMARY_COLOR};
    margin-bottom: 1rem;
    font-size: 1.3em;
    border-bottom: 2px solid {PRIMARY_COLOR};
    padding-bottom: 0.5rem;
}}

/* Chat input styling */
.stChatInputContainer {{
    padding: 1rem;
    background-color: #ffffff;
    border-top: 1px solid #e0e0e0;
    border-radius: 0 0 15px 15px;
}}
.stChatInput {{
    border-radius: 10px;
    border: 1px solid #ced4da;
    padding: 0.8rem 1rem;
}}
.stChatInput:focus-within {{
    border-color: {PRIMARY_COLOR};
    box-shadow: 0 0 0 0.2rem rgba(230, 0, 40, 0.25);
}}

/* Assignment card styling */
.assignment-card {{
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    background-color: {TERTIARY_COLOR};
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.2s ease-in-out;
}}
.assignment-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    border-color: {PRIMARY_COLOR};
}}
/* Assignment Cards Grid Layout */
.assignment-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    padding: 1rem;
    margin-top: 1rem;
}}

/* Assignment Card Container */
.assignment-container {{
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    position: relative;
    overflow: hidden;
}}

.assignment-container:hover {{
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}}

.assignment-container::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, {PRIMARY_COLOR}, {SECONDARY_COLOR});
}}

/* Assignment Title */
.assignment-title {{
    color: {TEXT_COLOR};
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}}

/* Assignment ID Badge */
.assignment-id {{
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: rgba(0, 0, 0, 0.05);
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.875rem;
    color: {SECONDARY_TEXT_COLOR};
}}

/* Assignment Details */
.assignment-details {{
    color: {SECONDARY_TEXT_COLOR};
    font-size: 0.95rem;
    line-height: 1.5;
}}

/* Max Members Badge */
.max-members {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(212, 0, 50, 0.1);
    color: {PRIMARY_COLOR};
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
    margin-top: 0.5rem;
}}

::-webkit-scrollbar {{width: 8px;}}
::-webkit-scrollbar-track {{background: {TERTIARY_COLOR};}}
::-webkit-scrollbar-thumb {{background: {SECONDARY_TEXT_COLOR}; border-radius: 4px;}}
::-webkit-scrollbar-thumb:hover {{background: {PRIMARY_COLOR};}}

body {{
        font-family: {FONT_FAMILY};
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
    }}
    /* Enhanced Custom Header Styling with Glass Effect */
    .custom-header {{
        background: linear-gradient(135deg, rgba(212,0,50,0.95) 0%, rgba(0,0,0,0.90) 100%);
        padding: 2.5rem 3rem;
        border-radius: 20px;
        margin: 1rem 0 3rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15), inset 0 1px 2px rgba(255,255,255,0.2);
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
    }}
    .custom-header::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    }}
    .custom-header .header-content {{
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }}
    .custom-header img {{
        height: 75px; /* Slightly larger logo */
        border-radius: 8px;
        transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
    }}
    .custom-header img:hover {{
        transform: scale(1.1) rotate(-3deg);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }}
    .custom-header .header-text h1 {{
        color: white;
        margin: 0;
        font-size: 2.4rem;
        font-weight: 700;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }}
    .custom-header .header-text p {{
        color: #E0E0E0; /* Light grey for subtitle */
        margin: 0.4rem 0 0 0;
        font-size: 1.1rem;
        font-weight: 300;
    }}

    /* Modern Assignment Card Styling with Glass Effect */
    .assignment-card {{
        background: rgba(255,255,255,0.9);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.2);
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    .assignment-card::before {{
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        width: 6px;
        height: 100%;
        background: {PRIMARY_COLOR};
        transition: all 0.4s ease;
    }}
    .assignment-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 16px 40px rgba(0,0,0,0.12);
        background: rgba(255,255,255,0.95);
    }}
    .assignment-card:hover::before {{
        width: 8px;
        background: linear-gradient({PRIMARY_COLOR}, {ACCENT_COLOR});
    }}
    .assignment-card h3 {{
        color: {SECONDARY_COLOR}; /* RMIT Black for titles */
        margin-top: 0;
        margin-bottom: 0.8rem;
        font-size: 1.5rem;
        font-weight: 600;
    }}
    .assignment-card p {{
        color: {SECONDARY_TEXT_COLOR};
        font-size: 0.95rem;
        line-height: 1.6;
    }}

    /* Modern Button Styling with Glass Effect */
    .stButton > button {{
        border-radius: 12px;
        border: 1px solid rgba(212,0,50,0.3);
        padding: 0.85rem 1.8rem;
        font-weight: 600;
        font-size: 1rem;
        background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, #FF1744 100%);
        color: white;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(212,0,50,0.2);
        position: relative;
        overflow: hidden;
    }}
    .stButton > button::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: all 0.6s ease;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, #FF1744 0%, {PRIMARY_COLOR} 100%);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(212,0,50,0.3);
    }}
    .stButton > button:hover::before {{
        left: 100%;
    }}
    /* Secondary button style (e.g., for 'Back to Menu') */
    .stButton[kind="secondary"] > button, .stButton button[title*="Back"], .stButton button[title*="Cancel"] {{
        background-color: {SECONDARY_TEXT_COLOR};
        border-color: {SECONDARY_TEXT_COLOR};
        color: white;
    }}
    .stButton[kind="secondary"] > button:hover, .stButton button[title*="Back"]:hover, .stButton button[title*="Cancel"]:hover {{
        background-color: white;
        color: {SECONDARY_TEXT_COLOR};
    }}

    /* Modern Input Field Styling */
    .stTextInput > div > div > input, .stTextArea > div > textarea {{
        border-radius: 12px;
        border: 1px solid rgba(206,212,218,0.5);
        padding: 1rem;
        font-size: 1rem;
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        transition: all 0.3s ease;
    }}
    .stTextInput > div > div > input:focus, .stTextArea > div > textarea:focus {{
        border-color: {PRIMARY_COLOR};
        box-shadow: 0 0 0 0.2rem rgba(212,0,50,0.25);
    }}
    .stRadio > div {{
        font-size: 1rem;
    }}
    /* Modern Alert Styling */
    .stAlert {{
        border-radius: 12px;
        padding: 1.5rem;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }}
    .stSuccess {{
        background-color: #D4EDDA;
        color: #155724;
        border-left: 5px solid #28A745;
    }}
    .stError {{
        background-color: #F8D7DA;
        color: #721C24;
        border-left: 5px solid #DC3545;
    }}
    .stWarning {{
        background-color: #FFF3CD;
        color: #856404;
        border-left: 5px solid {ACCENT_COLOR};
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {SECONDARY_COLOR};
    }}
    .stSpinner > div > svg {{
        stroke: {PRIMARY_COLOR};
    }}

    /* Modern Chat Interface Styling */
    .stChatMessage {{
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        padding: 1.2rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-out;
    }}

    .stChatMessage:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }}

    .stChatMessage [data-testid="StChatMessage"] {{
        background: transparent !important;
        border: none !important;
    }}
    
    /* Chat Avatar Styling */
    .stChatMessage [data-testid="stAvatar"] {{
        background: {PRIMARY_COLOR} !important;
        color: white !important;
        font-weight: 600 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 50% !important;
        width: 36px !important;
        height: 36px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1) !important;
    }}
    
    /* User Avatar Styling */
    .stChatMessage.user [data-testid="stAvatar"] {{
        background: linear-gradient(135deg, {PRIMARY_COLOR}, {ACCENT_COLOR}) !important;
    }}
    
    /* Assistant Avatar Styling */
    .stChatMessage.assistant [data-testid="stAvatar"] {{
        background: linear-gradient(135deg, {SECONDARY_COLOR}, #333) !important;
    }}

    /* User Message Styling - Right aligned */
    .stChatMessage.user {{
        background: linear-gradient(135deg, rgba({PRIMARY_COLOR}, 0.1) 0%, rgba({SECONDARY_COLOR}, 0.1) 100%);
        border-right: 4px solid {PRIMARY_COLOR};
        margin-left: 25% !important;
        margin-right: 0 !important;
        border-radius: 18px 4px 18px 18px;
    }}

    /* Assistant Message Styling - Left aligned */
    .stChatMessage.assistant {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(240, 240, 240, 0.9) 100%);
        border-left: 4px solid {SECONDARY_COLOR};
        margin-right: 25% !important;
        margin-left: 0 !important;
        border-radius: 4px 18px 18px 18px;
    }}

    /* Chat Container Styling */
    [data-testid="stChatContainer"] {{
        background: rgba(250, 250, 250, 0.6);
        padding: 1.5rem;
        border-radius: 20px;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        max-width: 900px;
        margin: 0 auto;
    }}
    
    /* Chat Messages Container */
    [data-testid="stChatMessageContainer"] {{
        gap: 1.5rem !important;
    }}

    /* Chat Input Styling */
    .stChatInputContainer {{
        padding: 0.8rem 1rem;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        border: 1px solid rgba(212, 0, 50, 0.1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        margin-top: 1rem;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }}
    
    /* Chat Input Field */
    .stChatInputContainer textarea {{
        border-radius: 10px !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        padding: 10px 15px !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }}
    
    .stChatInputContainer textarea:focus {{
        border-color: {PRIMARY_COLOR} !important;
        box-shadow: 0 0 0 2px rgba({PRIMARY_COLOR}, 0.2) !important;
    }}

    /* Assignment Cards Styling */
     .section-title {{
         font-size: 1.8rem;
         font-weight: 600;
         color: {SECONDARY_COLOR};
         margin-bottom: 1.5rem;
         position: relative;
         padding-bottom: 0.5rem;
     }}
     
     .section-title::after {{
         content: '';
         position: absolute;
         bottom: 0;
         left: 0;
         width: 80px;
         height: 4px;
         background: linear-gradient(90deg, {PRIMARY_COLOR}, {ACCENT_COLOR});
         border-radius: 2px;
     }}
     
     .assignment-card {{
         background: rgba(255, 255, 255, 0.85);
         backdrop-filter: blur(10px);
         -webkit-backdrop-filter: blur(10px);
         border-radius: 16px;
         border: 1px solid rgba(255, 255, 255, 0.3);
         box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
         padding: 1.5rem;
         margin-bottom: 1.5rem;
         transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
         position: relative;
         overflow: hidden;
         cursor: pointer;
         height: 100%;
         display: flex;
         flex-direction: column;
     }}
     
     .assignment-card::before {{
         content: '';
         position: absolute;
         top: 0;
         left: 0;
         width: 100%;
         height: 6px;
         background: linear-gradient(90deg, {PRIMARY_COLOR}, {ACCENT_COLOR});
         transform: scaleX(0);
         transform-origin: left;
         transition: transform 0.4s ease;
     }}
     
     .assignment-card:hover {{
         transform: translateY(-8px);
         box-shadow: 0 16px 40px rgba(0, 0, 0, 0.12);
     }}
     
     .assignment-card:hover::before {{
         transform: scaleX(1);
     }}
     
     .assignment-id {{
         display: inline-block;
         background: {PRIMARY_COLOR};
         color: white;
         font-weight: 600;
         font-size: 0.9rem;
         padding: 0.3rem 0.8rem;
         border-radius: 8px;
         margin-bottom: 0.8rem;
     }}
     
     .assignment-title {{
         font-size: 1.4rem;
         font-weight: 600;
         color: {SECONDARY_COLOR};
         margin-bottom: 1rem;
         line-height: 1.3;
     }}
     
     .assignment-details {{
         flex-grow: 1;
         display: flex;
         flex-direction: column;
     }}
     
     .assignment-details p {{
         font-size: 0.95rem;
         color: {SECONDARY_TEXT_COLOR};
         margin-bottom: 1rem;
         line-height: 1.5;
         flex-grow: 1;
     }}
     
     .max-members, .due-date {{
         font-size: 0.9rem;
         color: {SECONDARY_TEXT_COLOR};
         margin-top: 0.5rem;
         display: flex;
         align-items: center;
         gap: 0.5rem;
     }}
     
     /* Animation Keyframes */
     @keyframes fadeIn {{
         from {{ opacity: 0; transform: translateY(10px); }}
         to {{ opacity: 1; transform: translateY(0); }}
     }}
</style>
""", unsafe_allow_html=True)
#USERNAME = "testuser@student.rmit.edu.in"
USERNAME = st.session_state.get('user_info', {}).get('email', 'Unknown')

with open("data/assignments.json", "r") as f:
    assignments = json.load(f)
assignment_map = {a["assignment_id"]: a for a in assignments}
group_path = "data/groups.json"
if not os.path.exists(group_path):
    with open(group_path, "w") as f:
        json.dump({}, f)
with open(group_path, "r") as f:
    all_groups = json.load(f)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "content": "👋 Welcome! Below are the assignments available in **Data Communication and Net-Centric Computing (2502)**."}
    ]
if "selected_assignment" not in st.session_state:
    st.session_state.selected_assignment = None
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "anthropic.claude-3-haiku-20240307-v1:0"

# Remove multipage navigation links from sidebar
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    # User Profile Section
    st.markdown("### 👤 Profile")
    user_info = st.session_state.get('user_info', {})
    user_email = user_info.get('email', 'Unknown')
    user_role = user_info.get('role', 'Student').capitalize()
    user_info_html = f"""
    <div class='sidebar-card user-profile-card' style='width: 100%; min-height: 90px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: linear-gradient(135deg, rgba(255,255,255,1), rgba(245,245,245,0.95)); border-radius: 12px; padding: 1.2rem 0.5rem; margin: 0.7rem 0; box-shadow: 0 2px 6px rgba(0,0,0,0.08); border: 1px solid rgba(0,0,0,0.07);'>
        <div class='user-avatar' style='font-size: 2rem; background: linear-gradient(135deg, #e60028, #7b1fa2); color: white; width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 0.5rem; box-shadow: 0 2px 5px rgba(0,0,0,0.08);'>👨‍🎓</div>
        <div class='user-details' style='width: 100%; text-align: center;'>
            <div class='user-name' style='font-weight: 600; font-size: 1rem; color: #000; margin-bottom: 0.2rem; word-break: break-all; white-space: pre-wrap;'>{user_email}</div>
            <div class='user-role' style='font-size: 0.85rem; color: #333; opacity: 0.9;'>{user_role}</div>
        </div>
    </div>
    """
    st.markdown(user_info_html, unsafe_allow_html=True)
    # Current Session Info
    if st.session_state.selected_assignment:
        st.markdown(f"<div class='info-item'><span class='info-label'>📝</span> <span class='info-value'>{st.session_state.selected_assignment}</span></div>", unsafe_allow_html=True)
    
    # Extract model name for display
    current_model = "Claude 3 Haiku"
    if "sonnet" in st.session_state.selected_model.lower():
        current_model = "Claude 3.5 Sonnet"
        
    st.markdown(f"<div class='info-item'><span class='info-label'>🤖</span> <span class='info-value'>{current_model}</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
        # Model Selection Section
    st.markdown("### 🤖 AI Model")
    model_options = {
        "Claude 3 Haiku": "anthropic.claude-3-haiku-20240307-v1:0",
        "Claude 3.5 Sonnet": "anthropic.claude-3-5-sonnet-20240620-v1:0"
    }
    for name, model_id in model_options.items():
        is_selected = st.session_state.get('selected_model', '') == model_id
        button_prefix = "✓ " if is_selected else ""
        button_key = f"model_{model_id}"
        if is_selected:
            st.markdown(f"<div class='selected-model-indicator'></div>", unsafe_allow_html=True)
        if st.button(f"{button_prefix}{name}", key=button_key):
            st.session_state.selected_model = model_id
            st.rerun()
    # Logout button at the bottom
    st.markdown("---")
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page('login.py')

# Modern header with RMIT logo and gradient background
logo_base64 = get_logo_base64()
header_html_parts = [
    "<div class='custom-header'>",
    "    <div class='header-content'>"
]
if logo_base64:
    header_html_parts.append(f"""<img src='data:image/png;base64,{logo_base64}' alt='RMIT Logo' 
                                     onclick=\"window.open('https://www.rmit.edu.au', '_blank')\" 
                                     style='cursor:pointer;'>""")
header_html_parts.extend([
    "        <div class='header-text'>",
    "            <h1>RMIT Group Formation Assistant</h1>",
    "            <p>Intelligent group management for Data Communication and Net-Centric Computing</p>",
    "        </div>",
    "    </div>",
    "</div>"
])
st.markdown("\n".join(header_html_parts), unsafe_allow_html=True)

# Remove the default st.title as the custom header serves this purpose
# st.title("RMIT Group Formation Assistant 🤖")

chat_placeholder = st.container()

with st.container():
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

        # 👇 Add group buttons after last bot message only if not in UI flow
        if (
            msg["role"] == "bot"
            and i == len(st.session_state.messages) - 1
            and st.session_state.selected_assignment
            and not any([
                st.session_state.get("show_create_ui"),
                st.session_state.get("show_join_ui"),
                st.session_state.get("show_delete_ui")
            ])
        ):
            cols = st.columns(4, gap="small")
            with cols[0]:
                if st.button("➕ Create Group", key="chat_create"):
                    st.session_state.messages.append({"role": "user", "content": "create group"})
                    st.session_state.show_create_ui = True
                    st.rerun()
            with cols[1]:
                if st.button("👥 Join Group", key="chat_join"):
                    st.session_state.messages.append({"role": "user", "content": "join group"})
                    st.session_state.show_join_ui = True
                    st.rerun()
            with cols[2]:
                if st.button("📋 View Groups", key="chat_view"):
                    st.session_state.messages.append({"role": "user", "content": "view groups"})
                    response = get_group_list_as_text(
                        assignment_id=st.session_state.selected_assignment,
                        all_groups=all_groups,
                        user_email=USERNAME
                    )
                    st.session_state.messages.append({"role": "bot", "content": response})
                    st.rerun()
            with cols[3]:
                if st.button("❌ Delete/Exit Group", key="chat_delete"):
                    st.session_state.messages.append({"role": "user", "content": "delete or exit my group"})
                    st.session_state.show_delete_ui = True
                    st.rerun()

            # 🔙 Back to Menu
            st.markdown("")  # spacer
            if st.button("🔙 Back to Menu", key="chat_back"):
                st.session_state.messages.append({"role": "user", "content": "go back"})
                st.session_state.selected_assignment = None
                st.session_state.show_create_ui = False
                st.session_state.show_join_ui = False
                st.session_state.show_delete_ui = False
                st.session_state.messages.append({
                    "role": "bot",
                    "content": "🔙 You're back at the main menu. Please select an assignment."
                })
                st.rerun()


if st.session_state.get("show_create_ui", False):
    with st.chat_message("assistant"):
        if not st.session_state.selected_assignment:
            st.session_state.messages.append({
                "role": "bot",
                "content": "❗ You need to select an assignment before creating a group. Try 'Pick A3' or use the buttons below."
            })
            st.session_state.show_create_ui = False
            st.rerun()
            
        result = create_group_for_user(
            assignment_id=st.session_state.selected_assignment,
            all_groups=all_groups,
            user_email=USERNAME,
            assignment_map=assignment_map,
            return_group_name=True
        )     
        if isinstance(result, str):
            st.session_state.messages.append({"role": "bot", "content": result})
            st.session_state.show_create_ui = False
            st.rerun()
        elif result and isinstance(result, tuple):
            response, group_name = result
            if group_name:
                st.session_state.messages.append({"role": "user", "content": f"create group called {group_name}"})
            st.session_state.messages.append({"role": "bot", "content": response})
            st.session_state.show_create_ui = False
            with open(group_path, "w") as f:
                json.dump(all_groups, f, indent=2)
            st.rerun()
        # 👇 This stays *inside* the same block
        if st.button("🔙 Cancel and go back", key="cancel_create_group"):
            st.session_state.show_create_ui = False
            st.session_state.messages.append({
                "role": "bot",
                "content": "❌ Group creation cancelled. What would you like to do next?"
            })
            st.rerun()


if st.session_state.get("show_join_ui", False):
    result = join_group_for_user(
        assignment_id=st.session_state.selected_assignment,
        all_groups=all_groups,
        user_email=USERNAME,
        assignment_map=assignment_map,
        return_group_name=True
    )
    if result and isinstance(result, tuple):
        response, group_name = result
        st.session_state.messages.append({"role": "user", "content": f"join group {group_name}"})
        st.session_state.messages.append({"role": "bot", "content": response})
        st.session_state.show_join_ui = False
        with open(group_path, "w") as f:
            json.dump(all_groups, f, indent=2)
        st.rerun()

    if st.button("🔙 Cancel and go back", key="cancel_join_group"):
        st.session_state.show_join_ui = False
        st.session_state.messages.append({"role": "user", "content": "cancel join group"})
        st.session_state.messages.append({"role": "bot", "content": "❌ Group joining cancelled. You're back at the main menu."})
        st.rerun()

if st.session_state.get("show_delete_ui", False):
    result = delete_or_exit_group_for_user(
        assignment_id=st.session_state.selected_assignment,
        all_groups=all_groups,
        user_email=USERNAME
    )
    if result:
        user_msg = result.get("user_message")
        bot_msg = result.get("bot_response")
        st.session_state.messages.append({"role": "user", "content": user_msg})
        st.session_state.messages.append({"role": "bot", "content": bot_msg})
        st.session_state.show_delete_ui = False
        with open(group_path, "w") as f:
            json.dump(all_groups, f, indent=2)
        st.rerun()

    if st.button("🔙 Cancel and go back", key="cancel_delete_group"):
        st.session_state.show_delete_ui = False
        st.session_state.messages.append({"role": "user", "content": "cancel delete or exit"})
        st.session_state.messages.append({"role": "bot", "content": "❌ Delete/Exit action cancelled. You're back at the main menu."})
        st.rerun()

def show_assignments_inline():
    st.markdown("<h2 class='section-title'>📚 Available Assignments</h2>", unsafe_allow_html=True)
    
    # Create a responsive grid layout for assignment cards
    cols = st.columns(3)
    
    for i, a in enumerate(assignments):
        with cols[i % 3]:
            # Create a modern card with glass-morphism effect
            card_html = f"""
            <div class='assignment-card' onclick="window.parent.document.querySelector('[key="assign_{a['assignment_id']}"]').click();">                
                <div class='assignment-id'>{a['assignment_id']}</div>
                <h3 class='assignment-title'>{a['title']}</h3>
                <div class='assignment-details'>
                    <p>{a.get('description', 'No description provided.')}</p>
                    <div class='max-members'>👥 Max Group Size: {a.get('Maximum Group Members', 'N/A')}</div>
                    <div class='due-date'>📅 Due: {a.get('created_on', 'Not specified')}</div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # Hidden button that will be triggered by the card's onclick
            if st.button(f"Select {a['assignment_id']}", key=f"assign_{a['assignment_id']}", help=f"Select {a['title']}"):
                st.session_state.selected_assignment = a["assignment_id"]
                st.session_state.messages.append({"role": "user", "content": f"select assignment {a['assignment_id']}"})
                description = a.get("description", "No description provided.")
                max_members = a.get("Maximum Group Members", "N/A")
                st.session_state.messages.append({
                    "role": "bot",
                    "content": f"✅ Assignment selected: **{a['assignment_id']} - {a['title']}**\n\n📘 **Description:** {description}\n👥 **Group limit:** {max_members} members.\n\nWhat would you like to do next?"
                })
                st.rerun()

if st.session_state.selected_assignment is None:
    show_assignments_inline()

components.html("""
<script>
const textarea = window.parent.document.querySelector('textarea');
if (textarea) {
  textarea.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'Enter') {
      const sendBtn = window.parent.document.querySelector('button[kind="secondary"]');
      if (sendBtn) sendBtn.click();
    }
  });
}
</script>
""", height=0)

user_input = st.chat_input("Type a message about group formation...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    response = helpers.handle_user_input(
        message=user_input,
        assignments=assignments,
        all_groups=all_groups,
        selected_id=st.session_state.selected_assignment,
        user_email=USERNAME,
        model_id=st.session_state.selected_model
    )


    st.session_state.messages.append({"role": "bot", "content": response})

    with open(group_path, "w") as f:
        json.dump(all_groups, f, indent=2)

    # 🔁 Always rerun so UI updates IMMEDIATELY
    st.rerun()

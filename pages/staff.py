import streamlit as st
import os
import json
import base64
from datetime import datetime
from dotenv import load_dotenv
import streamlit.components.v1 as components
import sys

# Add parent directory to path so we can import features module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.admin_management import (
    create_assignment_for_admin,
    delete_assignment_for_admin,
    show_groups_for_assignment,
    export_groups_to_csv
)

load_dotenv(dotenv_path=".env.local")
USERNAME = os.getenv("USERNAME")

# Function to get logo as base64
def get_logo_base64():
    try:
        with open("Rmit logo.png", "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        print("RMIT Logo image not found. Please ensure 'Rmit logo.png' is in the root directory.")
        return None

# Theme configuration
PRIMARY_COLOR = "#e60028"  # RMIT Red
SECONDARY_COLOR = "#000000" # RMIT Black
BACKGROUND_COLOR = "#f0f2f5" # Modern light grey background
TEXT_COLOR = "#333333" # Darker text for better contrast
SECONDARY_TEXT_COLOR = "#4A5568" # Modern grey text
ACCENT_COLOR = "#007bff" # Blue accent for highlights
TERTIARY_COLOR = "#f8f9fa" # Light grey for subtle elements
FONT_FAMILY = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"

st.set_page_config(page_title="RMIT Assignment Admin Panel 🎓", layout="wide")

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
    margin-bottom: 1.5rem;
    padding: 20px;
    background-color: {PRIMARY_COLOR};
    border-radius: 10px;
}}
.logo-container img {{
    height: 70px;
    max-width: 100%;
    background: transparent !important;
    margin-bottom: 0.5rem;
}}
.logo-text {{
    font-size: 1.5em;
    font-weight: bold;
    color: white;
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
.stButton>button, .stDownloadButton>button {{  
    border: none;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    background-color: {PRIMARY_COLOR};
    color: white !important;
    transition: all 0.2s ease-in-out;
    font-weight: 600;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    width: 100% !important;
}}
.stButton>button:hover, .stDownloadButton>button:hover {{
    background-color: #c00020;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}}
.stButton>button:active, .stDownloadButton>button:active {{
    transform: translateY(0px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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

.info-item {{
    display: flex !important;
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
</style>
""", unsafe_allow_html=True)

# Hide default sidebar nav
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

ASSIGNMENTS_PATH = "data/assignments.json"
if not os.path.exists(ASSIGNMENTS_PATH):
    with open(ASSIGNMENTS_PATH, "w") as f:
        json.dump([], f)

with open(ASSIGNMENTS_PATH, "r") as f:
    assignments = json.load(f)

# Calculate next assignment_id like A4, A5...
existing_ids = [a["assignment_id"] for a in assignments if a["assignment_id"].startswith("A") and a["assignment_id"][1:].isdigit()]
existing_nums = sorted([int(a[1:]) for a in existing_ids])
next_id = f"A{existing_nums[-1] + 1}" if existing_nums else "A1"

assignment_map = {a["assignment_id"]: a for a in assignments}

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "content": "👋 Welcome to the Assignment Admin Panel. Select or create an assignment below."}
    ]
if "selected_assignment" not in st.session_state:
    st.session_state.selected_assignment = None
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "anthropic.claude-3-haiku-20240307-v1:0"
if "show_create_ui" not in st.session_state:
    st.session_state.show_create_ui = False
if "show_delete_ui" not in st.session_state:
    st.session_state.show_delete_ui = False
if "viewing_groups" not in st.session_state:
    st.session_state.viewing_groups = False

with st.sidebar:
    # Remove sidebar navigation and add compact profile card like in app.py (side by side)
    st.markdown("### 👤 Profile")
    user_info = st.session_state.get('user_info', {})
    user_email = user_info.get('email', USERNAME if USERNAME else 'Unknown')
    user_role = user_info.get('role', 'Staff').capitalize()
    user_info_html = f"""
    <div class='sidebar-card user-profile-card' style='width: 100%; min-height: 60px; max-width: 320px; display: flex; flex-direction: row; align-items: center; justify-content: flex-start; background: linear-gradient(135deg, rgba(255,255,255,1), rgba(245,245,245,0.95)); border-radius: 12px; padding: 0.7rem 1rem; margin: 0.7rem 0; box-shadow: 0 2px 6px rgba(0,0,0,0.08); border: 1px solid rgba(0,0,0,0.07);'>
        <div class='user-avatar' style='font-size: 2rem; background: linear-gradient(135deg, #7b1fa2, #e60028); color: white; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.08);'>👨‍💼</div>
        <div class='user-details' style='flex: 1; text-align: left;'>
            <div class='user-name' style='font-weight: 600; font-size: 1rem; color: #000; margin-bottom: 0.1rem; word-break: break-all; white-space: pre-wrap;'>{user_email}</div>
            <div class='user-role' style='font-size: 0.85rem; color: #333; opacity: 0.9;'>{user_role}</div>
        </div>
    </div>
    """
    st.markdown(user_info_html, unsafe_allow_html=True)
    if st.session_state.selected_assignment:
        st.markdown(f"<div class='info-item'><span class='info-label'>📝</span> <span class='info-value'>{st.session_state.selected_assignment}</span></div>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])  # Adjust the ratios if needed
    with col2:
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page('login.py')

# Display logo
logo_base64 = get_logo_base64()
if logo_base64:
    st.markdown(f"""
    <div class="logo-container" style="background-color: {PRIMARY_COLOR}; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <img src="data:image/png;base64,{logo_base64}" alt="RMIT Logo">
        <div class="logo-text" style="color: white; font-size: 1.5em; margin-top: 10px;">Assignment Admin Panel</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="logo-container" style="background-color: {PRIMARY_COLOR}; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <div class="logo-text" style="color: white; font-size: 1.5em;">Assignment Admin Panel</div>
    </div>
    """, unsafe_allow_html=True)

# Show chat messages
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

# Show assignments and actions only if not inside create/delete/view flow
if (
    not st.session_state.selected_assignment
    and not st.session_state.show_create_ui
    and not st.session_state.show_delete_ui
    and not st.session_state.viewing_groups
):
    # Display assignments in a grid layout
    st.markdown("<h3>Available Assignments</h3>", unsafe_allow_html=True)
    st.markdown("<div class='assignment-grid'>", unsafe_allow_html=True)
    
    # Create columns for the grid layout
    cols = st.columns(3)
    for i, a in enumerate(assignments):
        with cols[i % 3]:
            st.markdown(f"""
            <div class='assignment-card'>
                <h4>📘 {a['assignment_id']} - {a['title']}</h4>
                <p>{a['description'][:100]}...</p>
                <p>👥 Max Members: {a['Maximum Group Members']}</p>
                <p>📅 Due Date: {a['Due_date']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Select {a['assignment_id']}", key=f"assign_{a['assignment_id']}"):
                st.session_state.selected_assignment = a["assignment_id"]
                st.session_state.messages.append({"role": "user", "content": f"select assignment {a['assignment_id']}"})
                st.session_state.messages.append({"role": "bot", "content": f"✅ Assignment selected: **{a['title']}**\n\n📘 Description: {a['description']}\n👥 Max Members: {a['Maximum Group Members']}\n📅 Due Date: {a['Due_date']}"})
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Action buttons with improved styling
    cols = st.columns(2)
    with cols[0]:
        if st.button("➕ Create Assignment", key="create_btn", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "create assignment"})
            st.session_state.show_create_ui = True
            st.rerun()
    with cols[1]:
        if st.button("🗑️ Delete Assignment", key="delete_btn", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "delete assignment"})
            st.session_state.show_delete_ui = True
            st.rerun()

# Create assignment UI
if st.session_state.show_create_ui:
    with st.chat_message("assistant"):
        st.markdown("📝 Please fill out the assignment details below.")
        result = create_assignment_for_admin(next_id=next_id)
        if result:
            st.session_state.messages.append({"role": "bot", "content": f"✅ Assignment **{result['title']}** created successfully."})
            st.session_state.show_create_ui = False
            st.rerun()
        if st.button("🔙 Cancel", key="cancel_create_assignment", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "cancel create assignment"})
            st.session_state.messages.append({"role": "bot", "content": "❌ Assignment creation cancelled."})
            st.session_state.show_create_ui = False
            st.rerun()

# Delete assignment UI
if st.session_state.show_delete_ui:
    with st.chat_message("assistant"):
        st.markdown("🗑️ Select an assignment to delete.")
        result = delete_assignment_for_admin()
        if result:
            st.session_state.messages.append({"role": "bot", "content": f"🗑️ Deleted assignment **{result['title']}**."})
            st.session_state.show_delete_ui = False
            st.rerun()
        if st.button("🔙 Cancel", key="cancel_delete_assignment", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "cancel delete assignment"})
            st.session_state.messages.append({"role": "bot", "content": "❌ Assignment deletion cancelled."})
            st.session_state.show_delete_ui = False
            st.rerun()

# If assignment selected and not viewing groups
if st.session_state.selected_assignment and not st.session_state.viewing_groups:
    st.markdown("---")
    assignment_id = st.session_state.selected_assignment
    
    # Create a card for the selected assignment
    selected_assignment = assignment_map.get(assignment_id, {})
    if selected_assignment:
        st.markdown(f"""
        <div class='assignment-card' style='margin-bottom: 2rem;'>
            <h3>📘 {selected_assignment['assignment_id']} - {selected_assignment['title']}</h3>
            <p>{selected_assignment['description']}</p>
            <p>👥 Max Members: {selected_assignment['Maximum Group Members']}</p>
            <p>📅 Due Date: {selected_assignment['Due_date']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    cols = st.columns([1, 1, 1])
    with cols[0]:
        if st.button("📋 View Groups", key="view_groups_btn", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "view groups"})
            st.session_state.viewing_groups = True
            st.rerun()
    with cols[1]:
        export_groups_to_csv(assignment_id)
    with cols[2]:
        if st.button("🔙 Back to Menu", key="back_to_menu_btn", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "go back"})
            st.session_state.selected_assignment = None
            st.session_state.messages.append({"role": "bot", "content": "🔙 You're back at the assignment menu."})
            st.rerun()

# Viewing groups UI
if st.session_state.viewing_groups:
    st.markdown(f"""
    <div class='assignment-card' style='margin-bottom: 1.5rem;'>
        <h3>👥 Groups in this Assignment</h3>
    </div>
    """, unsafe_allow_html=True)
    
    with st.chat_message("assistant"):
        show_groups_for_assignment(st.session_state.selected_assignment)
    
    cols = st.columns([1, 1])
    with cols[0]:
        if st.button("🔙 Back", key="back_from_groups", use_container_width=True):
            st.session_state.viewing_groups = False
            st.session_state.messages.append({"role": "user", "content": "back from view groups"})
            st.session_state.messages.append({"role": "bot", "content": "📘 Assignment options available again."})
            st.rerun()
    with cols[1]:
        # Add download CSV button in the groups view
        assignment_id = st.session_state.selected_assignment
        export_groups_to_csv(assignment_id)

# Input box
user_input = st.chat_input("Ask me something about assignments...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({
        "role": "bot",
        "content": "🤖 I'm here to assist with assignment setup.\n\nPlease use the buttons above to create, delete, or view groups.\n\n💡 AI chat is only available for the *student assistant*, not the admin panel."
    })
    st.rerun()

# Keyboard shortcut handler
components.html("""
<script>
const textarea = window.parent.document.querySelector('textarea');
if (textarea) {
  textarea.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'Enter') {
      const sendBtn = window.parent.document.querySelector('button[kind=\"secondary\"]');
      if (sendBtn) sendBtn.click();
    }
  });
}
</script>
""", height=0)
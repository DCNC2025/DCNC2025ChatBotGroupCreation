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
        print("RMIT Logo image not found. Please ensure 'Rmit logo.png' is in the root directory.")
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

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

USERNAME = "testuser@student.rmit.edu.in"

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

with st.sidebar:
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("### 👤 Profile")

    user_info_html = f"""
    <div class='sidebar-card user-profile-card'>
        <div class='user-avatar'><span style='display:inline-block;'>👨‍🎓</span></div>
        <div class='user-details'>
            <div class='user-name'>{USERNAME}</div>
            <div class='user-role'>Student</div>
        </div>
    </div>
    """
    st.markdown(user_info_html, unsafe_allow_html=True)

    st.markdown("<div class='session-info'>", unsafe_allow_html=True)
    if st.session_state.selected_assignment:
        st.markdown(f"<div class='info-item'><span class='info-label'>📝</span> <span class='info-value'>{st.session_state.selected_assignment}</span></div>", unsafe_allow_html=True)

    current_model = "Claude 3 Haiku"
    if "sonnet" in st.session_state.selected_model.lower():
        current_model = "Claude 3.5 Sonnet"

    st.markdown(f"<div class='info-item'><span class='info-label'>🤖</span> <span class='info-value'>{current_model}</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("### 🤖 AI Model")

    model_options = {
        "Claude 3 Haiku": "anthropic.claude-3-haiku-20240307-v1:0",
        "Claude 3.5 Sonnet": "anthropic.claude-3-5-sonnet-20240620-v1:0"
    }

    for name, model_id in model_options.items():
        is_selected = st.session_state.selected_model == model_id
        button_prefix = "✓ " if is_selected else ""
        button_key = f"model_{model_id}"

        if is_selected:
            st.markdown(f"<div class='selected-model-indicator'></div>", unsafe_allow_html=True)

        if st.button(f"{button_prefix}{name}", key=button_key):
            st.session_state.selected_model = model_id
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

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

# ... rest of the app logic remains unchanged ...

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
                st.session_state.messages.append({"role": "user", "content": "stop this action and go back to assignment menu"})
                st.session_state.selected_assignment = None
                st.session_state.messages.append({
                    "role": "bot",
                    "content": "🔄 You can now choose a different assignment below."
                })
                st.rerun()


if st.session_state.get("show_create_ui", False):
    with st.chat_message("assistant"):
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

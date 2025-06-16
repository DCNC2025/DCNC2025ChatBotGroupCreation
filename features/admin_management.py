import streamlit as st
import json
import os
from datetime import datetime
import uuid
import pandas as pd

ASSIGNMENTS_PATH = "data/assignments.json"
GROUPS_PATH = "data/groups.json"


def load_assignments():
    if os.path.exists(ASSIGNMENTS_PATH):
        with open(ASSIGNMENTS_PATH, 'r') as f:
            return json.load(f)
    return []


def save_assignments(assignments):
    with open(ASSIGNMENTS_PATH, 'w') as f:
        json.dump(assignments, f, indent=2)


def create_assignment_for_admin(next_id):
    import streamlit as st
    from datetime import datetime
    import json
    import os

    st.markdown("""
    <style>
    .stTextInput > div > div > input,
    .stTextArea > div > textarea,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        background: #ffffff !important;  /* FULL WHITE */
        color: #000 !important;
        border: 1px solid #ccc !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }
    </style>
""", unsafe_allow_html=True)


    ASSIGNMENTS_PATH = "data/assignments.json"
    title = st.text_input("📘 Assignment Title", placeholder="Enter assignment title")
    description = st.text_area("📝 Assignment Description", placeholder="Enter a brief description")
    max_members = st.number_input("👥 Maximum Group Members", min_value=1, step=1, placeholder="Number of members")
    due_date = st.date_input("📅 Due Date")

    if st.button("✅ Submit"):
        new_assignment = {
            "assignment_id": next_id,
            "title": title.strip(),
            "description": description.strip(),
            "created_by": st.session_state.get("username", "instructor@rmit.edu.au"),
            "created_on": datetime.now().strftime("%Y-%m-%d"),
            "Due_date": due_date.strftime("%Y-%m-%d"),
            "Maximum Group Members": str(max_members)
        }

        # Load existing and append
        if os.path.exists(ASSIGNMENTS_PATH):
            with open(ASSIGNMENTS_PATH, "r") as f:
                assignments = json.load(f)
        else:
            assignments = []

        assignments.append(new_assignment)
        with open(ASSIGNMENTS_PATH, "w") as f:
            json.dump(assignments, f, indent=4)

        return new_assignment  # ✅ Return the new assignment object

    return None



def delete_assignment_for_admin():
    assignments = load_assignments()
    if not assignments:
        st.info("No assignments available to delete.")
        return None

    options = {f"{a['assignment_id']} - {a['title']}": a for a in assignments}
    choice = st.selectbox("🗑️ Select Assignment to Delete", list(options.keys()))
    selected = options.get(choice)

    if st.button("⚠️ Confirm Delete"):
        assignments = [a for a in assignments if a['assignment_id'] != selected['assignment_id']]
        save_assignments(assignments)
        st.success(f"🗑️ Deleted assignment: {selected['title']}")
        return selected
    return None


def show_groups_for_assignment(assignment_id):
    if os.path.exists(GROUPS_PATH):
        with open(GROUPS_PATH, 'r') as f:
            all_groups = json.load(f)
        groups = all_groups.get(assignment_id, [])
        if groups:
            st.subheader("👥 Groups in this Assignment")
            df = pd.DataFrame(groups)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No groups found for this assignment yet.")
    else:
        st.warning("No groups.json file found.")


def export_groups_to_csv(assignment_id):
    if os.path.exists(GROUPS_PATH):
        with open(GROUPS_PATH, 'r') as f:
            all_groups = json.load(f)
        groups = all_groups.get(assignment_id, [])
        if groups:
            df = pd.DataFrame(groups)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📤 Download CSV", data=csv,
                               file_name=f"groups_{assignment_id}.csv",
                               mime='text/csv')
        else:
            st.warning("No groups to export.")
    else:
        st.warning("No groups.json file found.")

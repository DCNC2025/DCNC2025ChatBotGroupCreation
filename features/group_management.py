import streamlit as st
import pandas as pd

def display_groups_for_assignment(assignment_id, all_groups, assignment_map):
    st.markdown("📋 **Showing group details above.**")

    groups = all_groups.get(assignment_id, [])
    if not groups:
        st.info("No groups found for this assignment.")
        return

    data = []
    for group in groups:
        data.append({
            "Group ID": group.get("group_id"),
            "Group Name": group.get("group_name"),
            "Created By": group.get("created_by"),
            "Members Count": len(group.get("members", [])),
            "Members": ", ".join(group.get("members", []))
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

def get_group_list_as_text(assignment_id, all_groups, user_email=None):
    """
    Returns a nicely formatted string of group information for a given assignment.
    Shows user's group first, followed by others.
    """
    if not assignment_id:
        return "⚠️ No assignment selected."

    user_group = None
    other_groups = []

    groups = all_groups.get(assignment_id, [])
    for group in groups:
        if not isinstance(group, dict):
            continue

        members = group.get("members", [])
        if user_email and user_email in members:
            user_group = group
        else:
            other_groups.append(group)

    message = ""

    # First: Show user’s group if found
    if user_group:
        message += f"🎯 **You are part of this group:** `{user_group['group_name']}`\n"
        message += f"👥 Members: {', '.join(user_group.get('members', []))}\n\n"
    else:
        message += f"❗ You are currently not part of any group in **{assignment_id}**.\n\n"

    # Now show other groups
    if other_groups:
        message += f"📋 **Other groups in {assignment_id}:**\n"
        for g in other_groups:
            members = g.get("members", [])
            group_line = f"- `{g['group_name']}` ({len(members)} members): {', '.join(members)}"
            message += group_line + "\n"
    else:
        message += "ℹ️ No other groups created yet."

    return message



def create_group_for_user(assignment_id, all_groups, user_email, assignment_map, return_group_name=False):
    groups = all_groups.setdefault(assignment_id, [])
    max_members = int(assignment_map[assignment_id].get("Maximum Group Members", 3))

    # Check if user is already in a group
    for group in groups:
        if user_email in group.get("members", []):
            already_in = f"⚠️ You are already part of **{group['group_name']}**. Please leave it before creating a new one."
            return (already_in, None) if return_group_name else already_in

    # UI to input group name
    group_name_input = st.text_input("Enter a name for your group:", key="custom_group_name")
    create_clicked = st.button("✅ Create Group", key="create_group_btn")

    if create_clicked and group_name_input.strip():
        new_group_name = group_name_input.strip()
        new_group_id = f"{assignment_id}-G{len(groups) + 1}"
        new_group = {
            "group_id": new_group_id,
            "group_name": new_group_name,
            "members": [user_email],
            "created_by": user_email
        }
        groups.append(new_group)
        response = f"✅ Group **{new_group_name}** created. You are now a member!"
        return (response, new_group_name) if return_group_name else response

    return None

def join_group_for_user(assignment_id, all_groups, user_email, assignment_map, return_group_name=False):
    groups = all_groups.get(assignment_id, [])
    max_members = int(assignment_map[assignment_id].get("Maximum Group Members", 3))

    # Check if already in a group
    for group in groups:
        if user_email in group.get("members", []):
            already_in = f"⚠️ You are already a member of **{group['group_name']}**. Please leave it before joining another group."
            return (already_in, None) if return_group_name else already_in

    available_groups = [g for g in groups if len(g.get("members", [])) < max_members]
    if not available_groups:
        msg = "🚫 All groups are currently full. You can create a new group instead."
        return (msg, None) if return_group_name else msg

    group_options = {
        f"{g['group_name']} ({len(g['members'])}/{max_members})": g for g in available_groups
    }

    selected_label = st.selectbox("👥 Select a group to join:", list(group_options.keys()), key="join_group_select")
    confirm = st.button("✅ Confirm Join", key="confirm_join_button")

    if confirm:
        selected_group = group_options[selected_label]
        if len(selected_group["members"]) >= max_members:
            msg = f"🚫 Sorry, **{selected_group['group_name']}** is now full."
            return (msg, None) if return_group_name else msg

        selected_group["members"].append(user_email)
        response = f"🎉 You have successfully joined **{selected_group['group_name']}**!"
        return (response, selected_group["group_name"]) if return_group_name else response

    return None

def delete_or_exit_group_for_user(assignment_id, all_groups, user_email):
    groups = all_groups.get(assignment_id, [])
    user_group = next((g for g in groups if user_email in g["members"]), None)

    if not user_group:
        return {
            "user_message": "Leave my group",
            "bot_response": "⚠️ You're not part of any group in this assignment."
        }

    st.markdown(f"🛠️ You are currently in **{user_group['group_name']}**.")
    action = st.radio("What would you like to do?", ["Exit Group", "Delete Group"], key="delete_exit_choice")
    proceed = st.button("✅ Confirm", key="confirm_delete_exit")

    if proceed:
        group_name = user_group['group_name']
        if action == "Exit Group":
            user_group["members"].remove(user_email)
            if user_email == user_group["created_by"]:
                if user_group["members"]:
                    new_leader = user_group["members"][0]
                    user_group["created_by"] = new_leader
                    return {
                        "user_message": f"exit group {group_name}",
                        "bot_response": f"✅ You’ve exited **{group_name}**. Leadership transferred to **{new_leader}**."
                    }
                else:
                    groups.remove(user_group)
                    return {
                        "user_message": f"exit group {group_name}",
                        "bot_response": f"✅ You were the last member of **{group_name}**. The group has been deleted."
                    }
            return {
                "user_message": f"exit group {group_name}",
                "bot_response": f"✅ You’ve exited **{group_name}**."
            }

        elif action == "Delete Group":
            if user_email == user_group["created_by"]:
                groups.remove(user_group)
                return {
                    "user_message": f"delete group {group_name}",
                    "bot_response": f"🗑️ Group **{group_name}** has been deleted."
                }
            else:
                return {
                    "user_message": f"try to delete group {group_name}",
                    "bot_response": "🚫 Only the group creator can delete the group."
                }

    return None

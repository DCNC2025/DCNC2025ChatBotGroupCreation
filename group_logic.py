import uuid

def create_group(assignment_id, group_name, user_email, assignments, all_groups):
    groups = all_groups.get(assignment_id, [])

    if any(g["group_name"].lower() == group_name.lower() for g in groups):
        return f"A group named '{group_name}' already exists for {assignment_id}."

    assignment = next((a for a in assignments if a["assignment_id"] == assignment_id), None)
    if not assignment:
        return "Assignment not found."

    group_id = f"{assignment_id}-G{str(uuid.uuid4())[:8]}"
    max_members = int(assignment["Maximum Group Members"])

    new_group = {
        "group_id": group_id,
        "group_name": group_name,
        "members": [user_email],
        "created_by": user_email,
        "max_members": max_members
    }

    groups.append(new_group)
    all_groups[assignment_id] = groups
    return f"✅ Group '{group_name}' created successfully with ID {group_id}."

def join_group(assignment_id, group_name, user_email, assignments, all_groups):
    groups = all_groups.get(assignment_id, [])

    for group in groups:
        if group["group_name"].lower() == group_name.lower():
            if user_email in group["members"]:
                return f"You're already a member of '{group_name}'."
            if len(group["members"]) >= group["max_members"]:
                return f"Sorry, '{group_name}' is full ({group['max_members']} members max)."
            group["members"].append(user_email)
            return f"✅ You've joined the group '{group_name}'!"

    return f"Group '{group_name}' not found in {assignment_id}."

def get_groups(assignment_id, all_groups):
    groups = all_groups.get(assignment_id, [])
    if not groups:
        return f"No groups found for {assignment_id} yet."

    msg = f"📋 Groups for {assignment_id}:\n"
    for g in groups:
        msg += f"- {g['group_name']} ({len(g['members'])}/{g['max_members']} members)\n"
    return msg

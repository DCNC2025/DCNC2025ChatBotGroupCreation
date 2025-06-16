import json
import streamlit as st
import logging
from dotenv import load_dotenv
from features.group_management import (
    create_group_for_user,
    join_group_for_user,
    delete_or_exit_group_for_user,
    get_group_list_as_text
)
from .bedrock_client import call_claude_model


load_dotenv()

def parse_intent_with_llm(message, model_id):
    try:
        raw_response = call_claude_model(message, model_id)
        logging.info("🧠 Claude raw response:\n%s", raw_response)

        try:
            parsed = json.loads(raw_response)

            if isinstance(parsed, list):
                return [p for p in parsed if p.get("type") == "intent"]

            elif parsed.get("type") == "intent":
                return [parsed]

            elif parsed.get("type") == "chat":
                return [{"type": "chat", "raw_response": raw_response.strip()}]

            else:
                return [{"type": "chat", "raw_response": raw_response.strip()}]

        except json.JSONDecodeError:
            return [{"type": "chat", "raw_response": raw_response.strip()}]

    except Exception as e:
        logging.warning(f"⚠️ LLM parsing failed: {e}")
        return [{"type": "error", "raw_response": str(e)}]

def handle_user_input(message, assignments, all_groups, selected_id, user_email, model_id):
    parsed_results = parse_intent_with_llm(message, model_id)

    if isinstance(parsed_results, dict):  # old fallback
        parsed_results = [parsed_results]

    all_responses = []

    for parsed_result in parsed_results:
        if parsed_result.get("type") == "chat":
            return parsed_result.get("raw_response", "🙂")

        if parsed_result.get("type") == "error":
            return f"⚠️ Claude could not process that: {parsed_result.get('raw_response')}"

        action = parsed_result.get("action", "unknown")
        assignment_id = parsed_result.get("assignment_id") or selected_id

        # ⚠️ Early check for assignment if needed
        if not assignment_id and action not in ["select_assignment", "go_back"]:
            return "❗ Please select an assignment first. Try 'Pick A1' or 'Show me A2'."

        # ✅ Handle actions
        if action == "select_assignment" and assignment_id:
            st.session_state.selected_assignment = assignment_id
            a = next((a for a in assignments if a["assignment_id"] == assignment_id), None)
            if a:
                desc = a.get("description", "No description.")
                max_members = a.get("Maximum Group Members", "N/A")
                all_responses.append(
                    f"✅ Assignment selected: **{a['assignment_id']} - {a['title']}**\n\n📘 **Description:** {desc}\n👥 **Group limit:** {max_members} members.\n\nWhat would you like to do next?"
                )
            else:
                all_responses.append("⚠️ Couldn't find that assignment. Try 'Pick A1'.")

        elif action == "create_group":
            st.session_state.show_create_ui = True
            all_responses.append("🛠️ Starting group creation flow...")

        elif action == "join_group":
            st.session_state.show_join_ui = True
            all_responses.append("➡️ Joining a group... let's go!")

        elif action == "delete_group":
            st.session_state.show_delete_ui = True
            all_responses.append("🚪 Preparing to delete or exit your group...")

        elif action == "view_groups":
            response = get_group_list_as_text(
                assignment_id=assignment_id,
                all_groups=all_groups,
                user_email=user_email
            )
            all_responses.append(response)

        elif action == "go_back":
            st.session_state.selected_assignment = None
            st.session_state.show_create_ui = False
            st.session_state.show_join_ui = False
            st.session_state.show_delete_ui = False
            all_responses.append("🔙 You're back at the main menu. Please select an assignment.")

        else:
            all_responses.append("🤖 I'm not sure what you meant. Try saying 'Create group for A1'.")

    return "\n\n".join(all_responses)

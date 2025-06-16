# RMIT Group Formation Assistant 🤖

This is a Streamlit-based chatbot interface that helps RMIT students form and manage assignment groups. It supports smart conversation-style flows for creating, joining, viewing, and exiting groups — all stored in local JSON files. AI model integration is supported to allow natural language interaction.

---

## 🚀 Features

- WhatsApp-style chat UI with avatars and conversation history
- Assignment selection and description display
- Create a new group with custom names
- Join existing groups (with limit checks)
- Exit or delete a group based on user roles
- View all groups for any assignment
- Keyboard shortcuts (Ctrl+Enter to send)
- Ready for AI integration (Claude, Llama, Nova, etc.)

---

## 🛠️ Prerequisites

Ensure you have **Python 3.9+** installed.

Install the following tools if not already:

- Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- pip (comes with Python)
- Git (optional, for cloning repo)

---

## 📦 Installation

1. **Clone the repo** (or copy the files):
   ```bash
   git clone https://github.com/your-username/group-formation-assistant.git
   cd group-formation-assistant

Create a virtual environment 
python -m venv .venv
source .venv/bin/activate   # On Windows use: .venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt

project-root/
│
├── app.py
├── data/
│   └── assignments.json
├── features/
│   └── group_management.py
├── utils/
│   ├── helpers.py
│   └── bedrock_client.py  ← ✅ Save it here
├── .env


Launch the Streamlit app using:
streamlit run app.py


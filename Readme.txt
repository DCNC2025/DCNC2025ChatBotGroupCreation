# RMIT Group Formation Assistant

This is a web application built using Streamlit to help students and staff at RMIT manage assignment group formation efficiently. The system supports role-based login and provides separate dashboards for students and staff.

It uses a simple file-based structure with no database dependencies, making it easy to run and test locally.

---

Note: 
1. Adjust your screen size for a better view. 
2. OTP might take 2-3 mins to receive in your Email.

## Overview

- **Students** can:
  - Log in and view assignment options
  - Create or join groups
  - See current group members

- **Staff** can:
  - Access a dashboard with group and assignment details
  - View and manage group memberships

The interface adapts based on the selected role during login.

---


## Setup
Register your account use your student email [here](https://us-
east-1kopki1lpu.auth.us-east-1.amazoncognito.com/login?
client_id=3h7m15971bnfah362dldub1u2p&response_type=code&scope=aws.cognito.signin.us
er.admin+email+openid&redirect_uri=https%3A%2F%2Fd84l1y8p4kdic.cloudfront.net)

----


## Login Process

Users start in `login.py`, where they choose their role (student or staff) and log in using a basic OTP flow. The login interface hides navigation and sidebars to keep the experience focused.

- After login, students are routed to `pages/app.py`, which provides the full group management experience.
- Staff are routed to `pages/staff.py`, where they can view all groups and take administrative actions.

Session state is used to track authentication, user roles, and email across pages.

---

## Project Structure

root/
├── data/ # Contains assignments.json, groups.json, otp.json
├── features/ # (Future use) Could store admin/student logic separately
├── pages/
│ ├── app.py # Main group chat interface for students
│ └── staff.py # Dashboard for staff/admins
├── utils/
│ ├── auth.py # Handles login, session, and role setup
│ ├── bedrock_client.py # Connects to AWS Bedrock for intent parsing
│ └── helpers.py # Utility functions and response handlers
├── .env # Stores test credentials for login (USERNAME/PASSWORD)
├── appsample.py # Alternate or older main chat UI version
├── login.py # Main Starting point for role selection and login
├── Readme.txt 
├── requirements.txt # Python dependencies
├── Rmit logo.png # RMIT branding used in UI
├── system.md # System prompt file for AI assistant

## Getting Started

### Install Dependencies

```bash
pip install -r requirements.txt


##Create a .env file in the root directory and include the following variables:
AWS_REGION=us-east-1
AWS_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
AWS_IDENTITY_POOL_ID=us-east-1:7771aae7-be2c-4496-a582-615af64292cf
AWS_USER_POOL_ID=us-east-1_koPKi1lPU
AWS_APP_CLIENT_ID=3h7m15971bnfah362dldub1u2p
COGNITO_USERNAME=USE YOUR LOGIN USERNAME
COGNITO_PASSWORD=USE YOUR PASSWORD
SENDGRID_API_KEY='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'
SENDER_EMAIL='rmit.bot@gmail.com'



#Running the App

streamlit run login.py

1. Select your role (student or staff)

2. Enter your email

3. OTP Received in Email. Paste it and log in

4. You'll be redirected to either the student or staff dashboard

#Data Files
Place these files in the data/ directory:

1. otp.json: Contains OTP details of each session 

2. assignments.json: list of assignments and max group sizes

3. groups.json: group names and member lists

Each file is plain JSON and can be created manually. Ask for templates if needed.





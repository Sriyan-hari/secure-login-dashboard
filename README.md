# Secure Login & Threat Monitoring Dashboard

## Overview
This project is a secure authentication system designed to prevent unauthorized access and monitor suspicious login activities.  
It focuses on implementing industry-level authentication using JWT and secure password handling.

---

## Problem Statement
Many applications suffer from weak authentication mechanisms and lack visibility into suspicious login attempts.  
This project addresses those issues by providing secure login and basic threat monitoring.

---

## Tech Stack
- Frontend: React.js
- Backend: Flask (Python)
- Authentication: JWT (JSON Web Token)
- Security: bcrypt (password hashing)
- Database: MySQL
- Version Control: Git & GitHub

---

## Features
- Secure user login using JWT authentication
- Password hashing using bcrypt (no plain-text passwords)
- Protected backend routes
- Login attempt monitoring (success / failure)
- Clean and secure Git practices using .gitignore

---

## Architecture Flow
1. User enters email and password on the React frontend
2. Login request is sent to the Flask backend
3. Backend validates credentials from the database
4. On success, a JWT token is generated
5. Token is sent back to frontend
6. Token is used to access protected APIs

---

## Security Implementation
- Passwords are hashed before storing in the database
- JWT is used to secure API endpoints
- Sensitive files like config and environment variables are excluded from GitHub

---

## How to Run the Project

### Backend
```bash
pip install -r requirements.txt
python app.py

--

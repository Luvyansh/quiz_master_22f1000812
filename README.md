# Quiz Master - Flask App

## Overview

Quiz Master is a Flask-based web application that enables users to take quizzes while providing an admin panel for quiz management. The application supports role-based access control, user authentication, quiz creation, and result tracking.

## Features

- **User Authentication**: Login and registration with role-based access (Admin/User).
- **Quiz Management**: CRUD operations for quizzes, subjects, and chapters.
- **User Management**: Admin control over user roles and data.
- **Quiz Attempt & Scoring**: Users can attempt quizzes, receive scores, and track attempts.
- **Search & Summary**: Efficient endpoints for searching quizzes and retrieving summaries.
- **Security**: API authentication using session-based authentication.

## Project Structure

```
quiz_master/
│── app/
│   ├── routes/            # Contains Flask route controllers
│   ├── models/            # Database models (SQLAlchemy)
│   ├── templates/         # HTML templates for the frontend
│   ├── static/            # CSS, JS, and images
│   ├── services/          # Utility functions (authentication, DB operations)
│   ├── config/            # Application configuration files
│   ├── __init__.py        # App initialization
│── main.py                # Entry point of the Flask application
│── requirements.txt       # Dependencies for the application
│── README.md              # Project documentation
```

## Installation

### Prerequisites

- Python 3.8+
- Flask
- SQLite/PostgreSQL (Database)

### Steps to Run the App

1. Clone the repository:
   ```sh
   git clone https://github.com/luvyansh/quiz_master_22f1000812.git
   cd quiz_master_22f1000812
   ```
2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the Flask application:
   ```sh
   python main.py
   ```
5. Open the application in your browser at `http://localhost:5000`

## API Endpoints

### Authentication

- `POST /login` - User login
- `POST /register` - User registration

### Quiz Management

- `GET /quiz` - Retrieve all quizzes
- `POST /quiz` - Create a new quiz (Admin)
- `GET /quiz/{quiz_id}` - Get quiz details
- `DELETE /quiz/{quiz_id}` - Delete a quiz (Admin)

### Chapters & Subjects

- `GET /subjects` - Get all subjects
- `POST /subjects` - Create a subject (Admin)
- `GET /chapters` - Get all chapters
- `POST /chapters` - Create a chapter (Admin)

### User Management

- `GET /users` - Retrieve all users (Admin)
- `DELETE /users/{user_id}` - Delete a user (Admin)

### Quiz Attempt

- `POST /quiz_master` - Attempt a quiz
- `GET /scores` - Retrieve user scores
- `GET /user_attempt` - Fetch user quiz attempts

### Search & Summary

- `GET /search` - Search quizzes
- `GET /summary` - Retrieve quiz summary

## Future Enhancements

- Leaderboards and user rankings
- AI-powered quiz recommendations
- Enhanced analytics and reporting

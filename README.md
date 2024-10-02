# AI Quizzer

AI Quizzer is a Flask-based web application that allows authenticated users to generate and submit quizzes with AI-generated questions. The application provides quiz history, allows retrying quizzes with new questions, and evaluates quiz submissions using Groq API integration.

## Features

- **User Authentication**: Users can register, log in, and obtain JWT tokens for authentication.
- **AI-Generated Quizzes**: Generate quizzes based on user-selected parameters such as grade, subject, difficulty, and total number of questions.
- **Quiz Submissions**: Submit completed quizzes and receive scores, with results sent via email.
- **Quiz History**: View past quiz submissions filtered by grade, subject, or date range.
- **Retry Quizzes**: Retake quizzes with fresh questions.
- **Email Notifications**: Users receive quiz results via email with suggestions for improvement.
- **Security**: JWT-based token authentication for all protected routes.

## Requirements

- Python 3.7+
- Flask 2.0+
- Groq API
- SQLAlchemy
- Flask-Mail for sending emails
- JWT for token-based authentication
- Postman or cURL for testing endpoints (optional)

## Installation

1. Clone the repository:(optional)After putting it on github
   ```bash
   git clone https://github.com/your-username/ai-quizzer.git
   cd ai-quizzer

2. Create a virtual environment and activate it:
    ```python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. pip install -r requirements.txt

4. Set up environment variables: Create a .env file in the root directory with the following variables:
    SECRET_KEY=your-secret-key
    DATABASE_URL=sqlite:///quizzer.db  # Or your production database URL
   
    GROQ_API_KEY=your-groq-api-key
   
    EMAIL_USER=your-email@gmail.com
   
    EMAIL_PASS=your-email-password

6. Runn the app locally(Flask Server)
    flask db upgrade  # For production with migration support
    python app_final.py  # For local testing

7. Run on your Browser or Postman to interact with the API's
    http://127.0.0.1:5000/

# API ENDPOINTS

API Endpoints

1. User Authentication
    Register: /register
    POST: Register a new user.
    Request body: { "username": "your_username", "password": "your_password" }
2. Login: /login
    POST: Log in to receive a JWT token.
    Request body: { "username": "your_username", "password": "your_password" }
3. Quiz Management
Generate Quiz: /generate-quiz

    POST (token required): Generate a quiz based on input parameters.
    Request body: {
    "grade": 5,
    "subject": "Math",
    "totalQuestions": 10,
    "maxScore": 100,
    "difficulty": "medium"
}


4. Submit Quiz: /submit-quiz

    POST (token required): Submit quiz answers for evaluation.
    Request body:{
    "quizId": "quiz-id",
    "responses": [
        {"questionId": "question-1", "userResponse": "A"},
        {"questionId": "question-2", "userResponse": "B"}
      ]
}


5. Quiz History: /quiz-history

    GET (token required): Get quiz submission history.

6. Retry Quiz: /retry-quiz/<quiz_id>

    POST (token required): Retry a quiz with new questions.

Other Routes

7. Get Hint: /get-hint/<quiz_id>/<question_id>
    GET (token required): Get a hint for a specific quiz question.

## Testing
Use tools like Postman or cURL to manually test the endpoints.

Example request using curl to register a new user:
curl -X POST http://127.0.0.1:5000/register \
-H "Content-Type: application/json" \
-d '{"username": "test_user", "password": "test_pass"}'



from flask_mail import Message
from app import mail
from app.models.user import User
from app.utils.helpers import generate_improvement_suggestions

def send_quiz_result_email(user_id, quiz, score, user_responses):
    user = User.query.get(user_id)
    if not user:
        return  # Handle error appropriately

    subject_line = f"Quiz Result: Grade {quiz.grade} {quiz.subject}"
    
    if score == quiz.max_score:
        body = f"""Congratulations on completing your Grade {quiz.grade} {quiz.subject} quiz!

Your score: {score} out of {quiz.max_score}

Subject: {quiz.subject}
Grade: {quiz.grade}
Difficulty: {quiz.difficulty}
Total Questions: {quiz.total_questions}

You've achieved a perfect score! Keep up the excellent work!"""
    else:
        suggestions = generate_improvement_suggestions(quiz.subject, user_responses)
        body = f"""Thank you for completing your Grade {quiz.grade} {quiz.subject} quiz.

Your score: {score} out of {quiz.max_score}

Quiz Details:
Subject: {quiz.subject}
Grade: {quiz.grade}
Difficulty: {quiz.difficulty}
Total Questions: {quiz.total_questions}

Here are some suggestions to improve your skills:

1. {suggestions[0]}
2. {suggestions[1]}

Keep practicing, and you'll see improvement!"""
    
    msg = Message(subject=subject_line,
                  recipients=[user.username],  # Assuming username is the email
                  body=body)
    
    mail.send(msg)
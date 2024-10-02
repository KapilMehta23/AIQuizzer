from flask import jsonify
from app import db
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.quiz_submission import QuizSubmission
from app.utils.helpers import generate_quiz_with_groq, evaluate_quiz, generate_hint
from app.services.email_service import send_quiz_result_email
import uuid
import datetime
from flask_caching import Cache


def generate_quiz(data):
    required_fields = ['grade', 'subject', 'totalQuestions', 'maxScore', 'difficulty']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    max_retries = 3
    for attempt in range(max_retries):
        try:
            quiz_data = generate_quiz_with_groq(data)
            quiz_id = quiz_data['id']

            # Store the quiz in cache
           # cache.set(f'quiz_{quiz_id}', quiz_data, timeout=60*60)
            
            with db.session.begin():
                new_quiz = Quiz(
                    id=quiz_data['id'],
                    grade=data['grade'],
                    subject=data['subject'],
                    total_questions=data['totalQuestions'],
                    max_score=data['maxScore'],
                    difficulty=data['difficulty']
                )
                db.session.add(new_quiz)
                
                for question in quiz_data['questions']:
                    new_question = Question(
                        id=question['id'],
                        quiz_id=new_quiz.id,
                        question_text=question['text'],
                        correct_answer=question['correct_answer']
                    )
                    db.session.add(new_question)
            
            return jsonify(quiz_data), 201
        except Exception as e:
            if attempt == max_retries - 1:
                return jsonify({'message': f'Error generating quiz after {max_retries} attempts: {str(e)}'}), 500
            continue

def submit_quiz(user_id, data):
    if 'quizId' not in data or 'responses' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    quiz = db.session.get(Quiz, data['quizId'])
    if not quiz:
        return jsonify({'message': 'Quiz not found'}), 404
    
    try:
        score, user_responses = evaluate_quiz(quiz, data['responses'])
        submission = QuizSubmission(user_id=user_id, quiz_id=quiz.id, score=score)
        db.session.add(submission)
        db.session.commit()
        
        send_quiz_result_email(user_id, quiz, score, user_responses)
        
        return jsonify({'score': score, 'maxScore': quiz.max_score}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error submitting quiz: {str(e)}'}), 500

def get_quiz_history(user_id, filters):
    cache_key = f'quiz_history_{user_id}_{filters.get("grade", "")}_{filters.get("subject", "")}'
    #cached_data = cache.get(cache_key)
    
   # if cached_data:
    #    return jsonify(cached_data), 200
    query = QuizSubmission.query.filter_by(user_id=user_id)
    
    if 'grade' in filters:
        query = query.join(Quiz).filter(Quiz.grade == filters['grade'])
    if 'subject' in filters:
        query = query.join(Quiz).filter(Quiz.subject == filters['subject'])
        
    if 'from_date' in filters:
        query = query.filter(QuizSubmission.completed_date >= datetime.datetime.strptime(filters['from_date'], '%d/%m/%Y'))
    if 'to_date' in filters:
        query = query.filter(QuizSubmission.completed_date <= datetime.datetime.strptime(filters['to_date'], '%d/%m/%Y'))
    
    submissions = query.all()
    results = [
        {
            'quizId': sub.quiz_id,
            'score': sub.score,
            'completedDate': sub.completed_date.strftime('%d/%m/%Y')
        } for sub in submissions
    ]
    #cache.set(cache_key, results, timeout=60*60)
    
    return jsonify(results), 200

def retry_quiz(quiz_id):
    quiz = db.session.get(Quiz, quiz_id)
    if not quiz:
        return jsonify({'message': 'Quiz not found'}), 404
    
    new_quiz_data = generate_quiz_with_groq({
        'grade': quiz.grade,
        'subject': quiz.subject,
        'totalQuestions': quiz.total_questions,
        'maxScore': quiz.max_score,
        'difficulty': quiz.difficulty
    })
    
    Question.query.filter_by(quiz_id=quiz.id).delete()
    
    new_questions = []
    for question in new_quiz_data['questions']:
        new_question = Question(
            id=question['id'],
            quiz_id=quiz.id,
            question_text=question['text'],
            correct_answer=question['correct_answer']
        )
        db.session.add(new_question)
        new_questions.append({
            'id': question['id'],
            'text': question['text'],
            'correct_answer': question['correct_answer'],
            'options': question['options']
        })
    
    db.session.commit()
    
    updated_quiz = {
        'id': quiz.id,
        'grade': quiz.grade,
        'subject': quiz.subject,
        'total_questions': quiz.total_questions,
        'max_score': quiz.max_score,
        'difficulty': quiz.difficulty,
        'questions': new_questions
    }
    
    return jsonify({
        'message': 'Quiz refreshed with new questions',
        'quiz': updated_quiz
    }), 200
    
def get_hint(quiz_id, question_id):
    quiz = db.session.get(Quiz, quiz_id)
    if not quiz:
        return jsonify({'message': 'Quiz not found'}), 404

    question = Question.query.filter_by(id=question_id, quiz_id=quiz_id).first()
    if not question:
        return jsonify({'message': 'Question not found'}), 404

    hint = generate_hint(question.question_text, quiz.grade, quiz.subject)
    return jsonify({'hint': hint}), 200
    

from flask import Blueprint, request, jsonify
from app.utils.decorators import token_required
from app.services.quiz_service import generate_quiz, submit_quiz, get_quiz_history, retry_quiz, get_hint
from app.utils.helpers import get_user_id_from_token

bp = Blueprint('quiz', __name__)

@bp.route('/generate-quiz', methods=['POST'])
@token_required
def generate_quiz_route():
    data = request.get_json()
    return generate_quiz(data)

@bp.route('/submit-quiz', methods=['POST'])
@token_required
def submit_quiz_route():
    data = request.get_json()
    user_id = get_user_id_from_token(request.headers.get('Authorization'))
    return submit_quiz(user_id, data)

@bp.route('/quiz-history', methods=['GET'])
@token_required
def get_quiz_history_route():
    filters = request.args
    user_id = get_user_id_from_token(request.headers.get('Authorization'))
    return get_quiz_history(user_id, filters)

@bp.route('/retry-quiz/<quiz_id>', methods=['POST'])
@token_required
def retry_quiz_route(quiz_id):
    return retry_quiz(quiz_id)

@bp.route('/get-hint/<quiz_id>/<question_id>', methods=['GET'])
@token_required
def get_hint_route(quiz_id, question_id):
    return get_hint(quiz_id, question_id)
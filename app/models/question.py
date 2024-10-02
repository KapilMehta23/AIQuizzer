from app import db

class Question(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    quiz_id = db.Column(db.String(36), db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.String(500), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
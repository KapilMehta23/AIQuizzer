from app import db

class Quiz(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    grade = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.String(10), nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True)
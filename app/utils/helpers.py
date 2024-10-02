import json,re
import uuid
import groq
import jwt
from app.models.user import User
from app.models.question import Question
from config import Config

client = groq.Groq(api_key=Config.GROQ_API_KEY)

def generate_quiz_with_groq(data):
    prompt = f"""Generate a quiz for grade {data['grade']} {data['subject']} with {data['totalQuestions']} questions.
    The difficulty level is {data['difficulty']}.
    Format the output as a JSON object with the following structure:
    {{
        "questions": [
            {{
                "text": "Question text",
                "correct_answer": "A|B|C|D",
                "options": {{
                    "A": "Option A text",
                    "B": "Option B text",
                    "C": "Option C text",
                    "D": "Option D text"
                }}
            }},
        ]
    }}
    Ensure that the questions are appropriate for the grade level and subject. Adhere to the given output format."""

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that generates educational quizzes."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="mixtral-8x7b-32768",
        max_tokens=2000,
        temperature=0.7,
    )

    quiz_data = json.loads(chat_completion.choices[0].message.content)
    
    quiz_data['id'] = str(uuid.uuid4())
    
    for question in quiz_data['questions']:
        question['id'] = str(uuid.uuid4())

    return quiz_data

def evaluate_quiz(quiz, responses):
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    
    question_mapping = {q.id: {'text': q.question_text, 'correct_answer': q.correct_answer} for q in questions}
    correct_answers = {q.question_text: q.correct_answer for q in questions}
    
    user_responses = {}
    for response in responses:
        question_id = response['questionId']
        if question_id in question_mapping:
            question_text = question_mapping[question_id]['text']
            user_responses[question_text] = response['userResponse']
   
    pair = f"""
    Correct answers:\n
    {json.dumps({q['text']: q['correct_answer'] for q in question_mapping.values()}, indent=4)},
    User responses:\n
    {user_responses} 
    """
      
    prompt = f"""
    Evaluate the quiz results for a user by comparing their responses to a list of correct answers. 
    Both the correct answers and user responses are provided as dictionaries, where the keys are the questions and the values are the corresponding answers. 
    The task is to calculate the total score by comparing each user's response to the correct answer for the same question. 
    Only the questions that appear in both the correct answers and the user's responses should be evaluated. The function should return the total number of correct answers.
    
    Here is an example:

    Correct answers:
    {{
    "What is the product of 5 and 7?": "C",
    "Which fraction is equivalent to 3/4?": "B",
    "If a rectangle has a length of 6 cm and a width of 4 cm, what is its area?": "D",
    "What is the result of subtracting 23 from 50?": "B",
    "Which number is the result of adding 125 and 175?": "D",
    "What is the value of 8 × (3 + 2)?": "D",
    "What is the result of dividing 72 by 9?": "B",
    "Which number is the smallest prime number larger than 10?": "A",
    "What is the perimeter of a square with a side length of 5 cm?": "B",
    "What is the result of 5³?": "C"
    }}
    User responses:
    {{
    "What is the product of 5 and 7?": "A",
    "If a rectangle has a length of 6 cm and a width of 4 cm, what is its area?": "D",
    "Which number is the smallest prime number larger than 10?": "A"
    }}
    You should compare the user's responses to the correct answers and return the number of correct responses. 
    For the example above, the output would be 2, since the user correctly answered the second and third questions.
    Evaluate the below pair of Correct answers and User responses please.
    {pair}
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that evaluates quiz responses."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama3-groq-70b-8192-tool-use-preview",
        max_tokens=100,
        temperature=0.1,
    )
    
    ai_response = chat_completion.choices[0].message.content.strip()
    score_match = re.search(r'\d+', ai_response)
    if score_match:
        score = int(score_match.group()) 
    else:
        raise ValueError("Unable to extract score from AI response")  # Extracting the score from the AI's response
    
    return score, user_responses

def generate_hint(question_text, grade, subject):
    prompt = f"""Given the following question for a grade {grade} {subject} quiz, provide a concise 1-2 line hint without giving away the answer:

Question: {question_text}

Your hint should:
1. Guide the student's thinking without revealing the solution
2. Highlight a key concept or approach relevant to solving the problem
3. Be appropriate for the grade level and subject
4. Encourage critical thinking

Provide only the hint, with no additional explanation or context."""

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an AI tutor providing helpful hints for quiz questions."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="mixtral-8x7b-32768",
        max_tokens=100,
        temperature=0.7,
    )

    hint = chat_completion.choices[0].message.content.strip()
    return hint

def generate_improvement_suggestions(subject, user_responses):
    prompt = f"""Based on the following quiz responses for a {subject} quiz, provide two concise suggestions for improvement:

{json.dumps(user_responses, indent=2)}

Your suggestions should:
1. Be specific to the subject and the user's performance
2. Offer actionable advice for improvement
3. Be encouraging and motivational

Provide only the two suggestions, separated by a newline character, with no additional explanation or context."""

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an AI tutor providing helpful suggestions for improvement based on quiz results."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="mixtral-8x7b-32768",
        max_tokens=200,
        temperature=0.7,
    )

    suggestions = chat_completion.choices[0].message.content.strip().split('\n')
    return suggestions[:2]  # Ensure we only return 2 suggestions

def get_user_id_from_token(token):
    data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    user = User.query.filter_by(username=data['user']).first()
    return user.id if user else None
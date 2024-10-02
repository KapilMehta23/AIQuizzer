from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from app import db
from app.models.user import User
from app.utils.decorators import token_required
from config import Config

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    
    new_user = User(username=data['username'], password=hashed_password)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'New user created!'}), 201
    except:
        db.session.rollback()
        return jsonify({'message': 'User already exists!'}), 409

@bp.route('/login', methods=['POST'])
def login():
    auth = request.get_json()

    if not auth or not auth['username'] or not auth['password']:
        return jsonify({'message': 'Could not verify'}), 401

    user = User.query.filter_by(username=auth['username']).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if check_password_hash(user.password, auth['password']):
        token = jwt.encode({
            'user': auth['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, Config.SECRET_KEY, algorithm="HS256")

        return jsonify({'token': token})

    return jsonify({'message': 'Could not verify'}), 401

@bp.route('/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({'message': 'This is a protected route!'})
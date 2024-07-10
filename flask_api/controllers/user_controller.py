
from flask import Blueprint, request, jsonify
from app import db,create_app
from models.user import User
import jwt
from passlib.hash import pbkdf2_sha256 as sha256


user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/all_users', methods=['GET'])
def get_users():
    db = current_app.db
    users = User.query.all()
    return jsonify([user.username for user in users])

@user_bp.route('/create_users', methods=['POST'])
def create_user():
    #db = create_app.db
    data = request.get_json()
    hashed_password = sha256.hash(data['password'])
    new_user = User(username=data['username'], email=data['email'], password=hashed_password, role = data['role'])
    try:
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        db.session.rollback()  # Rollback the transaction in case of an error
        return jsonify({'message': f'Failed to create user: {str(e)}'}), 500
    

@user_bp.route('/login', methods=['POST'])
def login():
    #db = create_app.db
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    

    user = User.query.filter_by(email=email).first()

    if user and sha256.verify(password, user.password):
        token = jwt.encode({
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, create_app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401
    

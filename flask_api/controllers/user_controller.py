from flask import Blueprint, request, jsonify,current_app
from models.user import User

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    db = current_app.db
    users = User.query.all()
    return jsonify([user.username for user in users])

@user_bp.route('/users', methods=['POST'])
def create_user():
    db = current_app.db
    data = request.get_json()
    new_user = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201
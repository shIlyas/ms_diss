import jwt
from functools import wraps
from flask import request, jsonify, current_app
from models.user import User

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            current_app.logger.error("Authorization header is missing")
            return jsonify({'message': 'Token is missing'}), 401

        try:
            # Check if the token is provided in the expected format
            if not auth_header.startswith('Bearer '):
                current_app.logger.error("Authorization header is malformed")
                return jsonify({'message': 'Token is missing'}), 401

            # Extract the token part from 'Bearer <token>'
            token = auth_header.split(" ")[1]
            current_app.logger.debug(f"Token received: {token}")

            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_app.logger.debug(f"Decoded JWT data: {data}")

            current_user = User.query.filter_by(email=data['email']).first()
            if not current_user:
                current_app.logger.error("User not found")
                return jsonify({'message': 'User not found'}), 404

        except jwt.ExpiredSignatureError:
            current_app.logger.error("Token has expired")
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            current_app.logger.error("Invalid token")
            return jsonify({'message': 'Token is invalid'}), 401
        except Exception as e:
            current_app.logger.error(f"Token decoding failed: {e}")
            return jsonify({'message': 'Token is invalid'}), 401

        return func(current_user, *args, **kwargs)

    return decorated
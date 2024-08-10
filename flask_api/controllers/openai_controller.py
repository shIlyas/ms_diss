from flask import Blueprint, request, jsonify, current_app
from app import db, logger
from models.user import RubricQuestion, AssistantScenario
import openai
import os
import requests
from utils import token_required  
# Initialize OpenAI with your API key
openai_assistant_bp = Blueprint('openai_assistant_bp', __name__)
openai.api_key = os.getenv("OPENAI_KEY")
openai.model = os.getenv("OPENAI_Model")

@openai_assistant_bp.route('/scenarios/<int:scenario_id>/create_assistant', methods=['POST'])
@token_required
def create_assistant(current_user,scenario_id):
    scenario = AssistantScenario.query.get(scenario_id)
    if not scenario:
        return jsonify({'message': 'Scenario not found'}), 404

    try:
        # Create the assistant on OpenAI using the scenario data
        headers = {
            'Authorization': f'Bearer {openai.api_key}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }
        
        assistant_payload = {
            "name": scenario.scenario_text,
            "instructions": scenario.additional_instructions,
            "model": openai.model 
        }

        response = requests.post(
            'https://api.openai.com/v1/assistants',
            headers=headers,
            json=assistant_payload
        )

        if response.status_code != 201:
            return jsonify({'message': 'Failed to create assistant with OpenAI', 'details': response.json()}), response.status_code

        assistant_data = response.json()

        return jsonify({'assistant_id': assistant_data['id']}), 200
    except Exception as e:
        logger.error(f"Failed to create assistant with OpenAI: {e}")
        return jsonify({'message': f'Failed to create assistant with OpenAI: {str(e)}'}), 500

@openai_assistant_bp.route('/create_thread', methods=['POST'])
@token_required
def create_thread(current_user):
    try:
        headers = {
            'Authorization': f'Bearer {openai.api_key}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }

        response = requests.post(
            'https://api.openai.com/v1/threads',
            headers=headers,
            json={}  # Sending an empty JSON payload
        )

        if response.status_code not in (200, 201):
            return jsonify({'message': 'Failed to create thread with OpenAI', 'details': response.json()}), response.status_code

        thread_data = response.json()

        return jsonify({'thread_id': thread_data['id']}), 200
    except Exception as e:
        logger.error(f"Failed to create thread with OpenAI: {e}")
        return jsonify({'message': f'Failed to create thread with OpenAI: {str(e)}'}), 500
    


@openai_assistant_bp.route('/threads/send_message', methods=['POST'])
@token_required
def send_message(current_user):
    
    data = request.get_json()
    assistant_id = data.get('assistant_id')
    thread_id = data.get('thread_id')
    role = data.get('role')
    content = data.get('content')
    if not thread_id:
        return jsonify({'message': 'Thread ID is required'}), 400
    if not role:
        return jsonify({'message': 'Role is required'}), 400
    if not content:
        return jsonify({'message': 'Content is required'}), 400

    try:
        headers = {
            'Authorization': f'Bearer {openai.api_key}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }

        payload = {
            'role': role,
            'content': content
        }

        response = requests.post(
            f'https://api.openai.com/v1/threads/{thread_id}/messages',
            headers=headers,
            json=payload
        )

        if response.status_code not in (200, 201):
            return jsonify({'message': 'Failed to send message to OpenAI', 'details': response.json()}), response.status_code

        message_data = response.json()

        return jsonify(message_data), 200
    except Exception as e:
        logger.error(f"Failed to Process Request: {e}")
        return jsonify({'message': f'Failed to process it with assistant: {str(e)}'}), 500


@openai_assistant_bp.route('/threads/run', methods=['POST'])
@token_required
def run_thread(current_user):
    data = request.get_json()
    thread_id = data.get('thread_id')
    assistant_id = data.get('assistant_id')

    if not thread_id:
        return jsonify({'message': 'Thread ID is required'}), 400
    if not assistant_id:
        return jsonify({'message': 'Assistant ID is required'}), 400

    try:
        headers = {
            'Authorization': f'Bearer {openai.api_key}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }

        payload = {
            'assistant_id': assistant_id
        }

        response = requests.post(
            f'https://api.openai.com/v1/threads/{thread_id}/runs',
            headers=headers,
            json=payload
        )

        if response.status_code not in (200, 201):
            return jsonify({'message': 'Failed to run thread with OpenAI', 'details': response.json()}), response.status_code

        run_data = response.json()
        return jsonify(run_data), 200
    except Exception as e:
        logger.error(f"Failed to run thread with OpenAI: {e}")
        return jsonify({'message': f'Failed to run thread with OpenAI: {str(e)}'}), 500



@openai_assistant_bp.route('/threads/last_assistant_message', methods=['POST'])
@token_required
def get_last_assistant_message(current_user):
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        headers = {
            'Authorization': f'Bearer {openai.api_key}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }

        response = requests.get(
            f'https://api.openai.com/v1/threads/{thread_id}/messages',
            headers=headers
        )

        if response.status_code not in (200, 201):
            return jsonify({'message': 'Failed to retrieve messages from OpenAI', 'details': response.json()}), response.status_code

        messages = response.json()['data']

        # Find the last message by the assistant
        assistant_message = next((msg for msg in messages if msg['role'] == 'assistant'), None)

        if not assistant_message:
            return jsonify({'message': 'No assistant message found in the thread'}), 404

        return jsonify(assistant_message), 200
    except Exception as e:
        logger.error(f"Failed to retrieve messages from OpenAI: {e}")
        return jsonify({'message': f'Failed to retrieve messages from OpenAI: {str(e)}'}), 500
from flask import Blueprint, request, jsonify, current_app
from app import db, logger
from models.user import RubricQuestion, AssistantScenario,Tags
import openai
import os
import requests
from utils import token_required  
# Initialize OpenAI with your API key
openai_assistant_bp = Blueprint('openai_assistant_bp', __name__)
openai.api_key = os.getenv("OPENAI_KEY")
openai.model = os.getenv("OPENAI_Model")
model_tuned = os.getenv("OPENAI_Model_Tuned")
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
    scenario_id = data.get('assistant_id')  # Assuming scenario_id is passed instead of assistant_id
    
    if not thread_id:
        return jsonify({'message': 'Thread ID is required'}), 400
    if not scenario_id:
        return jsonify({'message': 'Scenario ID is required'}), 400

    try:
        # Fetch the assistant_id (openid) from the database
        scenario = AssistantScenario.query.get(scenario_id)
        if not scenario or not scenario.openid:
            return jsonify({'message': 'Assistant not found or openid missing in the scenario'}), 404
        
        assistant_id = scenario.openid
        logger.error(f"{assistant_id}")
        headers = {
            'Authorization': f'Bearer {openai.api_key}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }

        payload = {
            'assistant_id': assistant_id,
            'model': model_tuned
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


@openai_assistant_bp.route('/threads/get_all_messages', methods=['POST'])
@token_required
def get_all_messages(current_user):
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        if not thread_id:
            return jsonify({'message': 'Thread ID is required'}), 400

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

        messages = response.json().get('data', [])

        # Extract role and message content from each message
        extracted_messages = []
        for message in messages:
            role = message.get('role')
            created_at = message.get('created_at')
            content_list = message.get('content', [])
            for content_item in content_list:
                if content_item.get('type') == 'text':
                    text_value = content_item.get('text', {}).get('value', '')
                    extracted_messages.append({'role': role, 'message': text_value, 'created_at': created_at})

        return jsonify(extracted_messages), 200
    except Exception as e:
        logger.error(f"Failed to retrieve messages from OpenAI: {e}")
        return jsonify({'message': f'Failed to retrieve messages from OpenAI: {str(e)}'}), 500




@openai_assistant_bp.route('/scenarios/<int:scenario_id>/rubric_responses', methods=['POST'])
@token_required
def handle_rubric_responses(current_user, scenario_id):
    data = request.get_json()

    # Retrieve scenario
    scenario = AssistantScenario.query.get(scenario_id)
    if not scenario:
        return jsonify({'message': 'Scenario not found'}), 404

    # Retrieve messages (both user and assistant) from the request data
    messages = data.get('messages')
    if not messages or not isinstance(messages, list):
        return jsonify({'message': 'A list of messages is required'}), 400

    # Transform 'message' to 'content'
    transformed_messages = [
        {
            "role": "system" if msg["role"] == "assistant" else msg["role"],
            "content": msg["message"]
        }
        for msg in reversed(messages) if msg.get("message") is not None
    ]

    # Manually add the additional instructions as a system message
    instructions = 'You are the assessor of the communication of doctor with patient persona. You will respond whether the given question has been fulfilled by the user (doctor) in the given chat or not.Take care of tone and slang of medical doctor like drug(medicine) and drug recreational drug. Provide a consise critical analysis For example no did not ask for social history at all or didnt ask because already being provided by patient. Focus should be more on response of doctor how he is communicating and gathering what is needed'
    transformed_messages.append({"role": "system", "content": instructions})

    test_messages = [
        {"role": "system", "content": "This is a test message."},
        {"role": "user", "content": "How can I help you?"}
    ]

    try:
        # Store the original model
        original_model = openai.model

        # Temporarily switch to the 'gpt-40-mini' model
        openai.model = 'gpt-4o-mini-2024-07-18'

        # Create a list to store the rubric responses
        rubric_responses = []

        # Retrieve the rubric questions associated with the scenario
        rubric_questions = RubricQuestion.query.filter_by(scenario_id=scenario_id).all()
       
        for question in rubric_questions:
            # Add the rubric question as a user message
            updated_transformed_messages = transformed_messages.copy()
            updated_transformed_messages.append({"role": "user", "content": question.question})
        
            # Send the updated messages to OpenAI to get the assistant's response for this rubric question
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {openai.api_key}',
                    'Content-Type': 'application/json'
                },
                json={"model": openai.model, "messages": updated_transformed_messages}
            )
        
            if response.status_code not in (200, 201):
                return jsonify({'message': f'Failed to get chat completion for rubric question: {question.question}', 'details': response.json()}), response.status_code
            
            # Get the assistant's response to the rubric question
            assistant_response = response.json()['choices'][0]['message']['content']
        
            rubric_responses.append({
                "question": question.question,
                "response": assistant_response
            })
        
        # Restore the original model after making the requests
        openai.model = original_model

        # Return all rubric responses
        return jsonify({"rubric_responses": rubric_responses}), 200

    except Exception as e:
        logger.error(f"Failed to process rubric responses with OpenAI: {e}")

        # Restore the original model in case of an error
        openai.model = original_model

        return jsonify({'message': f'Failed to process rubric responses: {str(e)}'}), 500


from transformers import pipeline

# Load the zero-shot classification pipeline with the BART model
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

@openai_assistant_bp.route('/scenarios/<int:scenario_id>/tag_evaluation', methods=['POST'])
@token_required
def handle_tag_evaluation(current_user, scenario_id):
    data = request.get_json()

    # Retrieve scenario
    scenario = AssistantScenario.query.get(scenario_id)
    if not scenario:
        return jsonify({'message': 'Scenario not found'}), 404

    # Retrieve messages (both user and assistant) from the request data
    messages = data.get('messages')

    if not messages or not isinstance(messages, list):
        return jsonify({'message': 'A list of messages is required'}), 400

    # Transform the messages and change "assistant" role to "patient" and "user" role to "doctor"
    transformed_messages = [
        {
            "role": "patient" if msg["role"] == "assistant" else 'doctor',
            "content": msg["message"]
        }
        for msg in reversed(messages) if msg.get("message") is not None
    ]

    # Initialize the chat string
    chat = ''

    # Iterating through transformed_messages to create the conversation
    for m in transformed_messages:
        if m["role"] == 'doctor':
            chat += f'Doctor: {m["content"]}. '
        else:
            chat += f'Patient: {m["content"]}. '                
    logger.info(chat)
    # Filter to only include user messages for evaluation
    user_messages = [
        {
            "role": msg["role"],
            "content": msg["message"]
        } for msg in reversed(messages) if msg.get("role") == "user" and msg.get("message") is not None
    ]

    # Retrieve the tags associated with the scenario
    tags = Tags.query.filter_by(scenario_id=scenario_id).all()  # Assume 'Tag' model holds tags for the scenario
    tag_names = [tag.tag for tag in tags]  # Extract tag names from Tags object
    logger.info(tag_names)
    # Create a list to store the evaluation results in the desired format
    tag_results = [{
            "message": "Messages",
            "results": tag_names
        }]
    
    try:
    
        for msg in reversed(messages):
            r = {
                "message": msg['message'],
                "results": []
            }
            if  msg['role'] == 'assistant':
                r["results"] = ['N/A'] * len(tag_names)
                tag_results.append(r)
                continue
           
            
            
            for tag in tag_names:
                hypothesis_start = f"{tag}"
                logger.info(hypothesis_start)
                #hypothesis_template = hypothesis_start + " {} in given conversation."
                # Perform zero-shot classification for the current message against the candidate tag
                result = classifier(msg['message'], candidate_labels=[tag], hypothesis_start = 'In this message doctor is {}')
                
                r['results'].append(result['scores'])
                


            # Append the result for the current message
            tag_results.append(r)

        # Return the results for each tag in the desired format
        return jsonify({
            "tag_evaluations": tag_results
        }), 200

    except Exception as e:
        logger.error(f"Failed to process tag evaluation: {e}")
        return jsonify({'message': f'Failed to process tag evaluation: {str(e)}'}), 500
"""
def handle_tag_evaluation(current_user, scenario_id):
    data = request.get_json()

    # Retrieve scenario
    scenario = AssistantScenario.query.get(scenario_id)
    if not scenario:
        return jsonify({'message': 'Scenario not found'}), 404

    # Retrieve messages (both user and assistant) from the request data
    messages = data.get('messages')
    # Transform 'message' to 'content'
   

    if not messages or not isinstance(messages, list):
        return jsonify({'message': 'A list of messages is required'}), 400

    transformed_messages = [
        {
            "role": "system" if msg["role"] == "patient" else 'doctor',
            "content": msg["message"]
        }
        for msg in reversed(messages) if msg.get("message") is not None
    ]
    chat = ''
    for m in transformed_messages:
        
        if m.role == 'doctor':
            chat.append(f' Doctor: {m.message}.')
        else:
            chat.append(f' Patient: {m.message}.')
                        

    # Filter to only include user messages for evaluation
    user_messages = [
        {
            "role": msg["role"],
            "content": msg["message"]
        }
        for msg in messages if msg.get("role") == "user" and msg.get("message") is not None
    ]

    # Retrieve the tags associated with the scenario
    tags = Tags.query.filter_by(scenario_id=scenario_id).all() # Assume 'Tag' model holds tags for the scenario

    # Create a list to store the evaluation results in the desired format
    tag_results = []

    try:
        for tag in tags:
            total_score_tag = 0  # To keep track of the total score for the current tag
            tag_name = tag.tag  # Assuming the tag model has a 'name' field
            
            hypothesis_template = "In the following chat this {message} is {}."
            # Classify each user message against the current tag
            for msg in user_messages:
                hypothesis_template = "In the following chat this message by user: {msg} is {}."
                # Perform zero-shot classification for the current message against the current tag
                classification_result = classifier(chat, candidate_labels=tags,hypothesis_template = hypothesis_template )
                   
                # Extract the score for the current tag
                tag_scores = classification_result['scores']  # First score corresponds to the current tag
                if tag_score > 0.50:
                    total_score_tag+=1
                     # Add to the total score for this tag

            # Calculate the average score for the current tag
            if len(user_messages) > 0:
                average_score_tag = total_score_tag / len(user_messages)
            else:
                average_score_tag = 0

            # Append the result for the current tag in the desired format
            tag_results.append({
                "name": tag_name,
                "score": f'{total_score_tag}/{len(user_messages)}'  # Round to 2 decimal places for better readability
            })

        # Return the results for each tag in the desired format
        return jsonify({
            "tag_evaluations": tag_results
        }), 200

    except Exception as e:
        logger.error(f"Failed to process tag evaluation: {e}")
        return jsonify({'message': f'Failed to process tag evaluation: {str(e)}'}), 500
"""